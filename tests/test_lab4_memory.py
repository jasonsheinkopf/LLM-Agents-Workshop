"""Lab 4: chunk -> embed -> store, retrieval, and per-caller memories (with an in-memory store)."""

import json

import pytest

from helpers import make_agent, system_message


@pytest.fixture
def store():
    from gym_agent.memory import InMemoryStore

    return InMemoryStore()


def test_handbook_is_chunked_by_section():
    from gym_agent.gym import load_handbook
    from gym_agent.memory import chunk_markdown

    chunks = chunk_markdown(load_handbook())
    sections = [c.section for c in chunks]
    assert len(chunks) == 13 and sections[0] == "Hours and location" and "Waivers" in sections
    waiver = next(c for c in chunks if c.section == "Waivers")
    assert waiver.text.startswith("Waivers:") and "legal guardian" in waiver.text
    assert len({c.id for c in chunks}) == 13, "stable, unique ids make re-ingesting safe"


def test_embed_returns_one_vector_per_text(llm):
    from gym_agent.memory import embed

    vecs = embed(llm, ["a waiver", "a birthday party"])
    assert len(vecs) == 2 and len(vecs[0]) > 0


def test_ingest_then_search_finds_the_right_section(llm, store):
    from gym_agent.memory import HANDBOOK_NS, Handbook

    hb = Handbook(llm, store)
    assert hb.ingest() == 13 and len(store.data[HANDBOOK_NS]) == 13
    hits = hb.search("can a babysitter or sibling sign the waiver for my kids", k=3)
    assert hits[0]["section"] == "Waivers"
    assert {"section", "text", "score"} <= set(hits[0])


def test_caller_memories_are_filtered_by_caller(llm, store):
    from gym_agent.memory import CallerMemory

    mem = CallerMemory(llm, store)
    mem.remember("dana", ["Dana's son Sam is 8 and wants to learn to belay."])
    mem.remember("priya", ["Priya's daughter Asha is 10."])
    assert mem.recall("dana", "son belay") == ["Dana's son Sam is 8 and wants to learn to belay."]
    assert all("Sam" not in m for m in mem.recall("priya", "son Sam belay")), "never leak another caller's memories"
    mem.forget("dana")
    assert mem.recall("dana", "son") == []


def test_extract_facts_reads_json(llm, store):
    from gym_agent.memory import CallerMemory

    llm.queue(json.dumps({"facts": ["Son Sam is 8."]}))
    facts = CallerMemory(llm, store).extract_facts([{"role": "user", "content": "My son Sam is 8"}])
    assert facts == ["Son Sam is 8."]


def test_agent_puts_handbook_and_memories_on_the_desk(llm, store):
    from gym_agent.memory import CallerMemory, Handbook

    hb, mem = Handbook(llm, store), CallerMemory(llm, store)
    hb.ingest()
    mem.remember("dana", ["Dana's son Sam is 8."])
    call = make_agent(llm, handbook=hb, caller_memory=mem).start_call("dana")
    call.send("Can my son's babysitter sign the waiver?")
    sys_msg = system_message(llm.requests[-1])
    assert "[Waivers]" in sys_msg, "retrieved handbook sections go into the prompt"
    assert "Sam is 8" in sys_msg, "this caller's memories go into the prompt"


def test_end_of_call_writes_memories(llm, store):
    from gym_agent.memory import MEMORY_NS, CallerMemory

    mem = CallerMemory(llm, store)
    llm.queue("Sure!", json.dumps({"facts": ["Sam is 8."]}))
    call = make_agent(llm, caller_memory=mem).start_call("dana")
    call.send("My son Sam is 8")
    assert call.end() == ["Sam is 8."]
    assert [r["metadata"]["caller_id"] for r in store.data[MEMORY_NS].values()] == ["dana"]
