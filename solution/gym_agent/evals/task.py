"""The experiment *task*: run one test case through the agent and capture what happened."""

from __future__ import annotations

from ..agent import GymAgent
from ..gym import BookingStore


def field(item, name: str):
    """Experiment items are Langfuse DatasetItems (attributes) or local dicts (keys)."""
    return item[name] if isinstance(item, dict) else getattr(item, name)


def run_case(agent_factory, case_input: dict) -> dict:
    """Play each caller turn in order. Returns the transcript, tool calls and bookings made."""
    agent: GymAgent = agent_factory()
    call = agent.start_call(case_input["caller_id"])
    transcript, tool_calls, reply = [], [], ""
    for text in case_input["turns"]:
        result = call.send(text)
        reply = result.reply
        transcript += [{"role": "caller", "text": text}, {"role": "agent", "text": reply}]
        tool_calls += [{"name": t["name"], "status": t["result"].get("status") or ("error" if "error" in t["result"] else "ok")}
                       for t in result.tool_calls]
    return {"reply": reply, "transcript": transcript, "tool_calls": tool_calls,
            "bookings": [b["class_id"] for b in call.ctx.made_bookings],
            "transfers": [t["team"] for t in call.ctx.transfers]}


def make_agent_factory(*, prompt, client, handbook=None, tools=None):
    """Each case gets a fresh agent with an in-memory booking store: experiments never touch real
    bookings, and cases can't affect each other. Caller memories are off, so results don't depend on
    whatever you said in earlier chats."""

    def factory() -> GymAgent:
        return GymAgent(client, tools=tools, handbook=handbook, caller_memory=None, prompt=prompt,
                        bookings=BookingStore.in_memory())

    return factory
