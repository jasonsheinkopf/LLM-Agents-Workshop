"""Lab 3: prompts in Langfuse, a test set, graders and an experiment task."""

import json
from types import SimpleNamespace

from helpers import make_agent


def test_prompt_falls_back_to_a_file_offline(tmp_path):
    from gym_agent.prompts import load_system_prompt

    f = tmp_path / "p.md"
    f.write_text("Be brief.\n")
    p = load_system_prompt(prompt_file=f)
    assert p.text == "Be brief." and p.version == "file:p.md"


def test_prompt_is_fetched_by_label_from_langfuse(monkeypatch):
    import langfuse

    from gym_agent import prompts

    asked = {}

    class FakePrompt:
        version, is_fallback = 7, False

        def compile(self, **_):
            return "PROMPT FROM LANGFUSE"

    class FakeLangfuse:
        def get_prompt(self, name, **kw):
            asked.update(name=name, **kw)
            return FakePrompt()

    monkeypatch.setattr(prompts, "langfuse_enabled", lambda: True)
    monkeypatch.setattr(langfuse, "get_client", lambda: FakeLangfuse())
    p = prompts.load_system_prompt(label="staging")
    assert asked["label"] == "staging" and "fallback" in asked, "fetch by label, with a fallback"
    assert p.text == "PROMPT FROM LANGFUSE" and p.version == "langfuse:v7"
    assert p.langfuse_prompt is not None, "keep the prompt object so traces link to the version"


def test_dataset_files_are_well_formed():
    from gym_agent.evals.cases import agent_cases, load_jsonl

    cases = agent_cases()
    assert len(cases) >= 15 and len({c["id"] for c in cases}) == len(cases)
    for c in cases:
        assert c["input"]["turns"] and c["input"]["caller_id"]
        assert {"facts", "must_not", "tool", "should_book"} <= set(c["expected"])
    assert all("human_pass" in r for r in load_jsonl("judge_calibration.jsonl"))


def test_booking_policy_evaluator():
    from gym_agent.evals.evaluators import booking_policy

    assert booking_policy(output={"bookings": []}, expected_output={"should_book": False}).value is True
    assert booking_policy(output={"bookings": ["x"]}, expected_output={"should_book": False}).value is False
    assert booking_policy(output={"bookings": []}, expected_output={"should_book": True}).value is False


def test_tool_use_evaluator():
    from gym_agent.evals.evaluators import tool_use

    out = {"tool_calls": [{"name": "check_schedule", "status": "ok"}]}
    assert tool_use(output=out, expected_output={"tool": "check_schedule"}).value is True
    assert tool_use(output=out, expected_output={"tool": "transfer_to_staff"}).value is False
    assert tool_use(output=out, expected_output={"tool": None}).value is True


def test_judge_parses_verdict(llm):
    from gym_agent.evals.evaluators import judge_reply

    llm.queue(json.dumps({"facts_covered": 1, "violations": [], "pass": True, "reason": "fine"}))
    v = judge_reply(llm, turns=["How much is a day pass?"], reply="$24.", facts=["adult day pass is $24"], must_not=[])
    assert v["pass"] is True and v["facts_covered"] == 1
    prompt = llm.requests[0]["messages"][0]["content"]
    assert "$24." in prompt and "adult day pass is $24" in prompt
    assert llm.requests[0]["response_format"] == {"type": "json_object"}


def test_judge_survives_garbage(llm):
    from gym_agent.evals.evaluators import judge_reply

    llm.queue("not json")
    assert judge_reply(llm, turns=["q"], reply="r", facts=["f"], must_not=[])["pass"] is False


def test_run_case_plays_every_turn(llm):
    from gym_agent.evals.task import run_case

    llm.queue("one", "two")
    out = run_case(lambda: make_agent(llm), {"caller_id": "dana", "turns": ["a", "b"]})
    assert out["reply"] == "two" and len(out["transcript"]) == 4 and out["bookings"] == []


def test_pass_rates_run_evaluator():
    from langfuse import Evaluation

    from gym_agent.evals.evaluators import pass_rates

    items = [SimpleNamespace(evaluations=[Evaluation(name="judge_pass", value=v)]) for v in (True, False, True, True)]
    [avg] = pass_rates(item_results=items)
    assert avg.name == "avg_judge_pass" and avg.value == 0.75
