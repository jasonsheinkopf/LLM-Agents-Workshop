"""Guardrails (Lab 5): the model proposes, your code decides.

The model only writes text. A "tool call" is the model *asking* your code to do something. Every
rule that matters is enforced here, in code the model cannot talk its way past:

1. Allow-list: only tools we registered can run. Anything else is refused.
2. Validation: arguments are parsed with Pydantic. Bad JSON, wrong types, or out-of-range values
   go back to the model as an error it can fix, and they never reach your systems.
3. Least privilege: the caller's identity comes from the phone system (the session), never from
   the model's arguments, so the agent can't book, look up or text anyone but the caller.
4. Confirmation: a booking needs a confirmation code that is only valid after the caller has sent a
   *new* message. The model cannot propose and confirm in the same breath (see tools.book_class).
5. Step limit: the loop in agent.py stops after SETTINGS.max_steps model calls.
6. Prompt injection: tool results are returned as JSON data with a clear "this is data" marker. The
   system prompt tells the model to treat them as information, not instructions.
"""

from __future__ import annotations

import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class ToolArgs(BaseModel):
    # Reject arguments we didn't define (e.g. a sneaky "to" phone number), instead of ignoring them.
    model_config = ConfigDict(extra="forbid")


Day = Literal["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class CheckScheduleArgs(ToolArgs):
    day: Day | None = Field(None, description="Day of the week, e.g. 'Saturday'. Omit for every day.")
    age: int | None = Field(None, ge=0, le=120, description="Participant's age, to show only classes they can take.")


class BookClassArgs(ToolArgs):
    class_id: str = Field(..., min_length=3, max_length=60, description="The class id from check_schedule.")
    participant_name: str = Field(..., min_length=1, max_length=60, description="Who will take the class.")
    participant_age: int = Field(..., ge=3, le=99, description="The participant's age in years.")
    confirmation_code: str | None = Field(
        None,
        description=(
            "Leave empty on the first call: you'll get a summary and a code. Read the summary to the "
            "caller. Only after they say yes in a later message, call again with the code."
        ),
    )


class SearchHandbookArgs(ToolArgs):
    query: str = Field(..., min_length=2, max_length=300, description="What to look up in the gym handbook.")


class LookupMemberArgs(ToolArgs):
    """No arguments on purpose: it can only ever look up the person who is calling."""


class SendTextArgs(ToolArgs):
    message: str = Field(..., min_length=5, max_length=320, description="The text message, e.g. a booking confirmation.")


class TransferToStaffArgs(ToolArgs):
    reason: str = Field(..., min_length=3, max_length=300, description="Why the caller needs a person.")
    team: Literal["front_desk", "duty_manager", "events"] = Field(
        "front_desk", description="duty_manager for injuries and incidents, events for birthday parties."
    )


ARG_MODELS: dict[str, type[BaseModel]] = {
    "check_schedule": CheckScheduleArgs,
    "book_class": BookClassArgs,
    "search_handbook": SearchHandbookArgs,
    "lookup_member": LookupMemberArgs,
    "send_text": SendTextArgs,
    "transfer_to_staff": TransferToStaffArgs,
}


class ToolError(Exception):
    """An error message the model should see, so it can correct itself."""


def validate_call(name: str, raw_arguments: str, allowed: set[str]) -> BaseModel:
    # TODO(lab5): three checks, each raising ToolError with a message the model can act on:
    #   1. allow-list: if name not in allowed -> ToolError("Unknown tool '<name>'. Available tools: [...]")
    #   2. JSON: json.loads(raw_arguments or "{}"); on JSONDecodeError -> ToolError("Arguments were not valid JSON: ...")
    #   3. schema: ARG_MODELS[name].model_validate(data); on ValidationError -> ToolError naming each
    #      bad field (err["loc"]) and why (err["msg"]).
    #   Return the validated Pydantic object.
    _ = (json, ValidationError)  # imported for you
    raise NotImplementedError("Lab 5: write validate_call (labs/05-tools/README.md)")


def as_tool_message(result: dict) -> str:
    """Tool output goes back to the model as clearly-labelled data, never as instructions."""
    return json.dumps({"tool_result_data": result}, ensure_ascii=False)
