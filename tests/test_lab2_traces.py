"""Lab 2: traces. Every model call goes through Langfuse, and each turn is grouped by call."""

import sys

import pytest

from helpers import make_agent


def test_model_client_is_langfuse_wrapped_when_keys_exist(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-lf-test")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-lf-test")
    monkeypatch.setenv("LANGFUSE_TRACING_ENABLED", "true")
    from gym_agent import llm

    llm.get_client()
    assert "langfuse.openai" in sys.modules, "get_client() should import OpenAI from langfuse.openai"


def test_turn_is_an_observed_function():
    from gym_agent.agent import Call

    assert hasattr(Call.send, "__wrapped__"), "decorate Call.send with @observe(...)"


def test_turn_sets_session_and_user(llm, monkeypatch):
    import contextlib

    from gym_agent import agent as agent_mod

    seen = {}

    @contextlib.contextmanager
    def recorder(**kwargs):
        seen.update(kwargs)
        yield

    monkeypatch.setattr(agent_mod, "propagate_attributes", recorder)
    call = make_agent(llm).start_call("dana")
    call.send("Hi")
    assert seen.get("session_id") == call.call_id, "one phone call = one Langfuse session"
    assert seen.get("user_id") == "dana"


@pytest.mark.parametrize("caller", ["dana", "priya"])
def test_each_call_gets_its_own_id(llm, caller):
    a = make_agent(llm)
    assert a.start_call(caller).call_id != a.start_call(caller).call_id
