"""Tools (Lab 5): what the agent can *do*.

A tool is three things the model reads (a name, a description and a JSON schema for its
arguments) plus a plain Python function that your code runs. The description is a prompt, so
write it like one: say when to use the tool, and when not to.

The schemas below are generated from the Pydantic models in guardrails.py, so the contract the
model sees and the validation your code runs can never drift apart.
"""

from __future__ import annotations

import secrets
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from langfuse import get_client

from .guardrails import (
    ARG_MODELS,
    BookClassArgs,
    CheckScheduleArgs,
    LookupMemberArgs,
    SearchHandbookArgs,
    SendTextArgs,
    ToolError,
    TransferToStaffArgs,
    validate_call,
)
from .gym import BookingStore, load_callers, load_classes

DESCRIPTIONS = {
    "check_schedule": (
        "List Ridgeline's weekly classes with day, time, ages, price and seats left. "
        "Use it before recommending or booking any class. Filter by day and/or the participant's age."
    ),
    "book_class": (
        "Book one participant into a class. Two steps: call it WITHOUT confirmation_code to get a "
        "summary and a code, read the summary to the caller and ask them to confirm, then, only "
        "after the caller says yes in a new message, call it again WITH the code."
    ),
    "search_handbook": (
        "Search the gym handbook (policies, prices, hours, waivers, parties, safety). Use it when "
        "the context you already have doesn't answer the caller's question."
    ),
    "lookup_member": (
        "Look up the caller's own membership on file (member or not, which plan). Takes no "
        "arguments: it can only look up the person who is calling."
    ),
    "send_text": (
        "Send a text message to the caller's phone number on file, e.g. a booking confirmation "
        "after book_class returns 'booked'. It can only text the caller."
    ),
    "transfer_to_staff": (
        "Hand the call to a person. Use it for injuries or incidents (duty_manager), birthday party "
        "bookings (events), membership cancellations, or anything you can't answer (front_desk)."
    ),
}


def tool_specs(names: list[str]) -> list[dict]:
    """The OpenAI `tools=[...]` list: name + description + JSON schema, for each tool."""
    return [
        {
            "type": "function",
            "function": {
                "name": n,
                "description": DESCRIPTIONS[n],
                "parameters": ARG_MODELS[n].model_json_schema(),
            },
        }
        for n in names
    ]


@dataclass
class PendingBooking:
    args: BookClassArgs
    issued_on_turn: int
    summary: str


@dataclass
class CallContext:
    """Everything a tool may touch during one phone call. Created by the agent, not the model."""

    caller_id: str
    bookings: BookingStore
    handbook: Any = None  # memory.Handbook, if long-term memory is set up
    turn: int = 0  # incremented by the agent on every new caller message
    pending: dict[str, PendingBooking] = field(default_factory=dict)
    transfers: list[dict] = field(default_factory=list)
    texts: list[dict] = field(default_factory=list)
    made_bookings: list[dict] = field(default_factory=list)


# --------------------------------------------------------------------------- implementations
def _class_view(c: dict, store: BookingStore) -> dict:
    ages = f"{c['min_age']}+" if c["max_age"] is None else f"{c['min_age']}-{c['max_age']}"
    view = {
        "class_id": c["id"], "name": c["name"], "day": c["day"], "start": c["start"],
        "minutes": c["minutes"], "ages": ages, "price_usd": c["price_usd"], "seats_left": store.seats_left(c),
    }
    if c.get("requires"):
        view["requires"] = c["requires"]
    return view


def _age_ok(c: dict, age: int) -> bool:
    return age >= c["min_age"] and (c["max_age"] is None or age <= c["max_age"])


def check_schedule(ctx: CallContext, args: CheckScheduleArgs) -> dict:
    classes = [
        _class_view(c, ctx.bookings)
        for c in load_classes()
        if (args.day is None or c["day"] == args.day) and (args.age is None or _age_ok(c, args.age))
    ]
    return {"classes": classes} if classes else {"classes": [], "note": "No classes match."}


def book_class(ctx: CallContext, args: BookClassArgs) -> dict:
    cls = next((c for c in load_classes() if c["id"] == args.class_id), None)
    if cls is None:
        raise ToolError(f"No class with id '{args.class_id}'. Call check_schedule for valid ids.")
    if not _age_ok(cls, args.participant_age):
        raise ToolError(f"{cls['name']} is for ages {_class_view(cls, ctx.bookings)['ages']}; "
                        f"{args.participant_name} is {args.participant_age}.")
    if cls.get("requires"):
        return {"status": "needs_staff", "message": f"{cls['name']} requires a {cls['requires']}, "
                "which staff must verify. Offer to transfer the caller to the front desk."}
    if ctx.bookings.seats_left(cls) <= 0:
        return {"status": "full", "message": f"{cls['name']} on {cls['day']} at {cls['start']} is full."}

    if args.confirmation_code is None:
        code = secrets.token_hex(2).upper()
        summary = (f"{cls['name']}, {cls['day']} at {cls['start']}, for {args.participant_name} "
                   f"(age {args.participant_age}), ${cls['price_usd']}.")
        ctx.pending[code] = PendingBooking(args=args, issued_on_turn=ctx.turn, summary=summary)
        return {"status": "needs_confirmation", "summary": summary, "confirmation_code": code,
                "next_step": "Read the summary to the caller and ask them to confirm. Do not say it is booked."}

    # Step two: the caller said yes, so the model calls again with the code.
    pending = ctx.pending.get(args.confirmation_code.upper())
    if pending is None:
        raise ToolError("That confirmation code is not valid. Call book_class without a code first.")
    if ctx.turn <= pending.issued_on_turn:
        # The guardrail that matters: confirmation must come from the CALLER, in a new message.
        raise ToolError("Not confirmed yet. Read the summary to the caller and wait for their answer.")
    if pending.args.model_dump(exclude={"confirmation_code"}) != args.model_dump(exclude={"confirmation_code"}):
        raise ToolError("The details changed since the summary. Start again without a code.")

    booking = ctx.bookings.add(class_id=cls["id"], caller_id=ctx.caller_id,
                               participant_name=args.participant_name, participant_age=args.participant_age)
    del ctx.pending[args.confirmation_code.upper()]
    ctx.made_bookings.append(booking)
    return {"status": "booked", "booking_id": booking["booking_id"], "summary": pending.summary,
            "reminder": "A parent or guardian must sign the waiver before the class."}


def search_handbook(ctx: CallContext, args: SearchHandbookArgs) -> dict:
    if ctx.handbook is None:
        return {"error": "The handbook isn't available. Offer to transfer the caller to staff."}
    return {"results": ctx.handbook.search(args.query, k=3)}


def lookup_member(ctx: CallContext, args: LookupMemberArgs) -> dict:
    caller = load_callers().get(ctx.caller_id) or {}
    if not caller.get("name"):
        return {"found": False, "note": "This number isn't on file. Ask the caller for their name if needed."}
    return {"found": True, "name": caller["name"], "member": caller.get("member", False),
            "membership": caller.get("membership")}


def send_text(ctx: CallContext, args: SendTextArgs) -> dict:
    phone = (load_callers().get(ctx.caller_id) or {}).get("phone")
    if not phone:
        raise ToolError("No phone number on file for this caller.")
    ctx.texts.append({"to": phone, "message": args.message})  # a real system would call an SMS API here
    return {"status": "sent", "to": phone}


def transfer_to_staff(ctx: CallContext, args: TransferToStaffArgs) -> dict:
    ctx.transfers.append(args.model_dump())
    return {"status": "transferring", "team": args.team,
            "next_step": "Tell the caller you're transferring them now, and why."}


IMPLEMENTATIONS: dict[str, Callable[[CallContext, Any], dict]] = {
    "check_schedule": check_schedule,
    "book_class": book_class,
    "search_handbook": search_handbook,
    "lookup_member": lookup_member,
    "send_text": send_text,
    "transfer_to_staff": transfer_to_staff,
}


def run_tool(ctx: CallContext, name: str, raw_arguments: str, allowed: set[str]) -> dict:
    """Validate, then execute, one tool call. Errors become results the model can react to.

    Each call is recorded as a `tool` observation in the Langfuse trace (input, output, errors).
    """
    with get_client().start_as_current_observation(name=name, as_type="tool", input=raw_arguments) as obs:
        try:
            args = validate_call(name, raw_arguments, allowed)
            result = IMPLEMENTATIONS[name](ctx, args)
        except ToolError as e:
            result = {"error": str(e)}
            obs.update(level="WARNING", status_message=str(e))
        obs.update(output=result)
    return result
