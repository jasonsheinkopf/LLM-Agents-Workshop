"""Lab 1: your first agent call. One model call with a system prompt, plus conversation history."""

from helpers import make_agent, system_message


def test_reply_comes_from_the_model(llm):
    llm.queue("Hi! Ridgeline here, how can I help?")
    call = make_agent(llm).start_call("dana")
    assert call.send("Hello?").reply == "Hi! Ridgeline here, how can I help?"


def test_system_prompt_goes_first(llm):
    call = make_agent(llm).start_call("dana")
    call.send("Hello?")
    req = llm.requests[0]
    assert req["messages"][0]["role"] == "system"
    assert "Ridgeline's phone assistant" in system_message(req)
    assert req["messages"][-1] == {"role": "user", "content": "Hello?"}


def test_uses_the_configured_model(llm):
    from gym_agent.config import SETTINGS

    make_agent(llm).start_call("dana").send("Hello?")
    assert llm.requests[0]["model"] == SETTINGS.model


def test_conversation_history_is_kept(llm):
    llm.queue("First answer.", "Second answer.")
    call = make_agent(llm).start_call("dana")
    call.send("First question")
    call.send("Second question")
    contents = [m.get("content") for m in llm.requests[1]["messages"]]
    assert contents[1:] == ["First question", "First answer.", "Second question"]


def test_caller_id_is_described_to_the_model(llm):
    make_agent(llm).start_call("dana").send("Hi")
    assert "Dana Ortiz" in system_message(llm.requests[0])
