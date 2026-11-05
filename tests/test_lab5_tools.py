"""Lab 5: tool schemas, guardrails, the two-step booking, and the agent loop."""

import json

import pytest

from fakes import tool_call
from helpers import make_agent

ALL = {"check_schedule", "book_class", "lookup_member", "send_text", "transfer_to_staff"}


@pytest.fixture
def ctx():
    from gym_agent.gym import BookingStore
    from gym_agent.tools import CallContext

    return CallContext(caller_id="dana", bookings=BookingStore.in_memory(), turn=1)


def run(ctx, name, **args):
    from gym_agent.tools import run_tool

    return run_tool(ctx, name, json.dumps(args), ALL)


def test_tool_specs_have_name_description_schema():
    from gym_agent.tools import tool_specs

    [spec] = tool_specs(["book_class"])
    fn = spec["function"]
    assert spec["type"] == "function" and fn["name"] == "book_class" and len(fn["description"]) > 40
    assert {"class_id", "participant_name", "participant_age"} <= set(fn["parameters"]["required"])


def test_unknown_tool_is_refused(ctx):
    from gym_agent.tools import run_tool

    assert "Unknown tool" in run_tool(ctx, "refund_everyone", "{}", ALL)["error"]


def test_bad_json_and_bad_values_become_errors(ctx):
    from gym_agent.tools import run_tool

    assert "not valid JSON" in run_tool(ctx, "book_class", "{oops", ALL)["error"]
    assert "participant_age" in run(ctx, "book_class", class_id="youth-sat-1000", participant_name="Sam", participant_age=400)["error"]


def test_schedule_filters_by_day_and_age(ctx):
    classes = run(ctx, "check_schedule", day="Saturday", age=8)["classes"]
    assert [c["class_id"] for c in classes] == ["youth-sat-1000"]
    assert classes[0]["seats_left"] == 3


def test_booking_needs_confirmation_on_a_later_turn(ctx):
    args = dict(class_id="youth-sat-1000", participant_name="Sam", participant_age=8)
    first = run(ctx, "book_class", **args)
    assert first["status"] == "needs_confirmation" and ctx.made_bookings == []
    code = first["confirmation_code"]
    same_turn = run(ctx, "book_class", **args, confirmation_code=code)
    assert "error" in same_turn and ctx.made_bookings == [], "the model can't confirm on the caller's behalf"
    ctx.turn += 1  # the caller replied "yes"
    done = run(ctx, "book_class", **args, confirmation_code=code)
    assert done["status"] == "booked" and ctx.made_bookings[0]["caller_id"] == "dana"


def test_changed_details_invalidate_the_code(ctx):
    args = dict(class_id="youth-sat-1000", participant_name="Sam", participant_age=8)
    code = run(ctx, "book_class", **args)["confirmation_code"]
    ctx.turn += 1
    assert "error" in run(ctx, "book_class", **{**args, "participant_name": "Max"}, confirmation_code=code)


def test_booking_rules_are_enforced_in_code(ctx):
    too_young = run(ctx, "book_class", class_id="intro-belay-sat-1400", participant_name="Sam", participant_age=8)
    assert "ages 12+" in too_young["error"], "the belay class is twelve and up"
    assert run(ctx, "book_class", class_id="youth-sun-1000", participant_name="Ana", participant_age=10)["status"] == "full"
    assert run(ctx, "book_class", class_id="lead-101-thu-1900", participant_name="Marcus", participant_age=30)["status"] == "needs_staff"


def test_lookup_and_text_only_reach_the_caller(ctx):
    assert run(ctx, "lookup_member")["name"] == "Dana Ortiz"
    sent = run(ctx, "send_text", message="You're booked: Youth Climbing, Sat 10:00.")
    assert sent == {"status": "sent", "to": "+1-555-0101"} and ctx.texts[0]["to"] == "+1-555-0101"
    sneaky = run(ctx, "send_text", message="hi there", to="+1-555-0102")
    assert "error" in sneaky and len(ctx.texts) == 1, "unknown arguments are rejected: the model can't choose who to text"


def test_agent_loop_runs_tools_and_feeds_results_back(llm):
    llm.queue([tool_call("check_schedule", {"day": "Saturday", "age": 8})],
              "Youth Climbing is Saturday at 10.")
    agent = make_agent(llm, tools=["check_schedule", "book_class", "transfer_to_staff"])
    result = agent.start_call("dana").send("Belay class for my 8 year old Saturday?")
    assert result.reply == "Youth Climbing is Saturday at 10."
    assert [t["name"] for t in result.tool_calls] == ["check_schedule"]
    second = llm.requests[1]["messages"]
    assert second[-2]["role"] == "assistant" and second[-2]["tool_calls"][0]["function"]["name"] == "check_schedule"
    assert second[-1]["role"] == "tool" and "youth-sat-1000" in second[-1]["content"]
    assert "tools" in llm.requests[0]


def test_loop_stops_after_max_steps(llm):
    from gym_agent.agent import GIVE_UP

    llm.queue(*[[tool_call("check_schedule", {})] for _ in range(20)])
    result = make_agent(llm, tools=["check_schedule"]).start_call("dana").send("loop forever")
    assert result.reply == GIVE_UP and len(llm.requests) == make_agent(llm).settings.max_steps


def test_full_booking_conversation(llm):
    args = {"class_id": "youth-sat-1000", "participant_name": "Sam", "participant_age": 8}

    def confirm_with_code(req):
        code = json.loads(req["messages"][-1]["content"])["tool_result_data"]["confirmation_code"]
        return f"That's Youth Climbing Saturday 10:00 for Sam, $35. Shall I book it? (code {code})"

    def book_with_code(req):
        code = next(m for m in req["messages"] if m["role"] == "tool")
        code = json.loads(code["content"])["tool_result_data"]["confirmation_code"]
        return [tool_call("book_class", {**args, "confirmation_code": code}, "c2")]

    llm.queue([tool_call("book_class", args, "c1")], confirm_with_code, book_with_code, "You're booked!")
    agent = make_agent(llm, tools=["check_schedule", "book_class"])
    call = agent.start_call("dana")
    call.send("Book Sam (8) into Saturday youth climbing")
    assert call.ctx.made_bookings == []
    call.send("Yes please")
    assert [b["class_id"] for b in call.ctx.made_bookings] == ["youth-sat-1000"]
