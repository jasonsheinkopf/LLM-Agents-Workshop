"""The agent: a model + instructions + memory + tools, running in a loop, observed by traces.

    agent = GymAgent.from_env()           # wires up OpenAI, Langfuse and Pinecone from .env
    call = agent.start_call("dana")       # one phone call = one Langfuse session
    print(call.send("Can my 8-year-old take the belay class on Saturday?").reply)
    call.end()                            # writes long-term memories about the caller

Lab by lab, this file grows:
  Lab 1  one model call with a system prompt           -> Call._model_call, Call.send
  Lab 2  every turn traced in Langfuse                 -> @observe + propagate_attributes
  Lab 3  the system prompt fetched from Langfuse       -> load_system_prompt(label)
  Lab 4  handbook RAG + per-caller memories            -> Call._context
  Lab 5  tools in a think -> act -> observe loop       -> Call.send's loop, tools.run_tool
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path

from langfuse import get_client, observe, propagate_attributes

from .config import SETTINGS, Settings, langfuse_enabled
from .guardrails import as_tool_message
from .gym import BookingStore, describe_caller
from .prompts import SystemPrompt, load_system_prompt
from .tools import CallContext, run_tool, tool_specs

ALL_TOOLS = ["check_schedule", "book_class", "lookup_member", "send_text", "search_handbook", "transfer_to_staff"]
GIVE_UP = "Sorry, I'm having trouble with that one. Let me transfer you to someone at the front desk."


@dataclass
class TurnResult:
    reply: str
    tool_calls: list[dict] = field(default_factory=list)  # [{"name", "arguments", "result"}]
    trace_id: str | None = None
    prompt_version: str = ""


class GymAgent:
    def __init__(
        self,
        client,
        *,
        tools: list[str] | None = None,
        handbook=None,
        caller_memory=None,
        prompt: SystemPrompt | None = None,
        prompt_label: str | None = None,
        bookings: BookingStore | None = None,
        settings: Settings = SETTINGS,
    ) -> None:
        self.client = client
        self.tools = list(ALL_TOOLS if tools is None else tools)
        if handbook is None and "search_handbook" in self.tools:
            self.tools.remove("search_handbook")  # no handbook, no handbook tool
        self.handbook = handbook
        self.caller_memory = caller_memory
        self.prompt = prompt or load_system_prompt(label=prompt_label)
        self.bookings = bookings if bookings is not None else BookingStore()
        self.settings = settings

    @classmethod
    def from_env(cls, *, prompt_label: str | None = None, prompt_file: Path | None = None,
                 bookings: BookingStore | None = None, tools: list[str] | None = None,
                 memory: bool = True) -> GymAgent:
        """Build the full agent from your .env.

        Memory switches on by itself once the Pinecone index exists (after Lab 4's `ingest`).
        """
        from .llm import get_client as get_llm
        from .memory import CallerMemory, Handbook, PineconeStore

        client = get_llm()
        handbook = caller_memory = None
        store = PineconeStore.try_connect() if memory else None
        if store is not None:
            handbook, caller_memory = Handbook(client, store), CallerMemory(client, store)
        prompt = load_system_prompt(label=prompt_label, prompt_file=prompt_file)
        return cls(client, tools=tools, handbook=handbook, caller_memory=caller_memory, prompt=prompt,
                   bookings=bookings)

    def start_call(self, caller_id: str) -> Call:
        return Call(self, caller_id)


class Call:
    """One phone call: the conversation history plus the tools' per-call state."""

    def __init__(self, agent: GymAgent, caller_id: str) -> None:
        self.agent = agent
        self.caller_id = caller_id
        self.call_id = f"call-{uuid.uuid4().hex[:12]}"
        self.history: list[dict] = []
        self.ctx = CallContext(caller_id=caller_id, bookings=agent.bookings, handbook=agent.handbook)

    # ----------------------------------------------------------------- context (Lab 4)
    def _context(self, user_text: str) -> str:
        """What goes on the model's desk this turn: who is calling, memories, handbook pages."""
        parts = [describe_caller(self.caller_id)]
        # TODO(lab4): if self.agent.caller_memory is set, recall this caller's memories for
        #   user_text and add them as a block that starts "What you remember about this caller".
        # TODO(lab4): if self.agent.handbook is set, search it for user_text (k=3) and add a
        #   "Handbook context" block with one "[<section>] <text>" line per hit.
        return "\n\n".join(parts)

    # ----------------------------------------------------------------- one model call (Lab 1)
    def _model_call(self, messages: list[dict]):
        kwargs = {"model": self.agent.settings.model, "messages": messages}
        # TODO(lab5): offer the tools:  specs = tool_specs(self.agent.tools); if specs: kwargs["tools"] = specs
        # TODO(lab3): link the trace to the prompt version: if langfuse_enabled() and
        #   self.agent.prompt.langfuse_prompt is not None, set kwargs["langfuse_prompt"] to it.
        return self.agent.client.chat.completions.create(**kwargs).choices[0].message

    # ----------------------------------------------------------------- the turn (Labs 1, 2, 5)
    @observe(name="phone-turn", as_type="agent")
    def send(self, user_text: str) -> TurnResult:
        with propagate_attributes(
            session_id=self.call_id,  # every turn of this call groups into one Langfuse session
            user_id=self.caller_id,
            tags=["ridgeline-agent"],
            metadata={"prompt_version": self.agent.prompt.version},
        ):
            self.ctx.turn += 1
            self.history.append({"role": "user", "content": user_text})
            system = {"role": "system", "content": f"{self.agent.prompt.text}\n\n{self._context(user_text)}"}
            # TODO(lab5): replace the single model call below with the agent loop. Up to
            #   self.agent.settings.max_steps times: call the model; if msg.tool_calls is empty, that's the
            #   reply. Otherwise append the assistant's tool_calls to history, run each one with
            #   run_tool(self.ctx, name, arguments, set(self.agent.tools)), record it in result.tool_calls,
            #   and append {"role": "tool", "tool_call_id": ..., "content": as_tool_message(output)}.
            #   If you run out of steps, reply with GIVE_UP.
            msg = self._model_call([system, *self.history])
            self.history.append({"role": "assistant", "content": msg.content})
            return TurnResult(reply=msg.content, prompt_version=self.agent.prompt.version,
                              trace_id=get_client().get_current_trace_id())

    def end(self) -> list[str]:
        """After the call: extract durable facts about the caller and store them (Lab 4)."""
        if self.agent.caller_memory is None:
            return []  # no memory, nothing to write (and no empty trace)
        return self._write_memories()

    @observe(name="end-call")
    def _write_memories(self) -> list[str]:
        with propagate_attributes(session_id=self.call_id, user_id=self.caller_id):
            facts = self.agent.caller_memory.extract_facts(self.history)
            self.agent.caller_memory.remember(self.caller_id, facts)
            return facts
