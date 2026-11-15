"""The agent: a model + instructions + memory + tools, running in a loop, observed by traces.

    agent = GymAgent.from_env()           # wires up OpenAI, Langfuse and Pinecone from .env
    call = agent.start_call("dana")       # one phone call = one Langfuse session
    print(call.send("Can my 8-year-old take the belay class on Saturday?").reply)
    call.end()                            # writes long-term memories about the caller

Lab by lab, this file grows:
  Lab 1  one model call with a system prompt           -> Call._model_call, Call.send
  Lab 2  every turn traced in Langfuse                 -> Call.send (@observe + propagate_attributes)
  Lab 3  each model call linked to its prompt version  -> Call._model_call (prompts.py fetches it)
  Lab 4  handbook RAG + per-caller memories            -> Call._context
  Lab 5  tools in a think -> act -> observe loop       -> Call._model_call, Call.send

How the TODOs work: each piece of work is tagged TODO(labN). Do only the current lab's TODOs and
leave the rest where they are: you'll come back to this file. A `raise NotImplementedError` marks
a function the app can't run without. Delete it once you've written the function.
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
    """What one turn of a call returns: the reply, and from Lab 5 the tools used to reach it."""

    reply: str
    tool_calls: list[dict] = field(default_factory=list)  # [{"name", "arguments", "result"}]
    trace_id: str | None = None
    prompt_version: str = ""


class GymAgent:
    """The agent: a model client, its instructions, and the memory and tools it may use.

    One agent serves many calls. Each call gets its own `Call`, with its own history.
    """

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
        """Answer the phone: a new call from `caller_id`, with an empty history."""
        return Call(self, caller_id)


class Call:
    """One phone call: the conversation history plus the tools' per-call state."""

    def __init__(self, agent: GymAgent, caller_id: str) -> None:
        self.agent = agent
        self.caller_id = caller_id
        self.call_id = f"call-{uuid.uuid4().hex[:12]}"
        self.history: list[dict] = []
        self.ctx = CallContext(caller_id=caller_id, bookings=agent.bookings, handbook=agent.handbook)

    # ----------------------------------------------------------------- context: Lab 4
    def _context(self, user_text: str) -> str:
        """Build what goes on the model's desk this turn, besides its instructions.

        Returns one string, which `send` adds to the system message. Until Lab 4 it only says who
        is calling. Lab 4 adds what the agent remembers about the caller and the handbook sections
        that best match what they just said.
        """
        parts = [describe_caller(self.caller_id)]
        # TODO(lab4): add up to two more blocks to `parts`. Keep the caller line above.
        #   1. Memories: if self.agent.caller_memory is set, recall this caller's memories for
        #      user_text. If any come back, add a block that starts "What you remember about this
        #      caller", with one line per memory.
        #   2. Handbook: if self.agent.handbook is set, search it for user_text (k=3). Add a block
        #      that starts "Handbook context", with one "[<section>] <text>" line per hit.
        #   Either one is None until you've run `memory ingest`: then skip that block.
        return "\n\n".join(parts)

    # ----------------------------------------------------------------- model call: Lab 1, extended in Labs 3 and 5
    def _model_call(self, messages: list[dict]):
        """Send the conversation to the model once, and return the model's reply.

        `messages` is the whole conversation, system message first. Returns the reply message
        (`response.choices[0].message`), not the whole response: `send` reads its `.content`, and
        from Lab 5 its `.tool_calls`.

        Lab 1 writes the call itself, the last step below. Labs 3 and 5 each add one option to
        `kwargs` before it.
        """
        kwargs = {"model": self.agent.settings.model, "messages": messages}
        # TODO(lab5): offer the tools. Build them with tool_specs(self.agent.tools), and add them as
        #   kwargs["tools"] only if the list isn't empty.
        # TODO(lab3): link the call to the prompt version that produced it. When langfuse_enabled()
        #   and self.agent.prompt.langfuse_prompt is not None, set kwargs["langfuse_prompt"] to it.
        return self.agent.client.chat.completions.create(**kwargs).choices[0].message

    # ----------------------------------------------------------------- one turn: Lab 1, extended in Labs 2 and 5
    # TODO(lab2): decorate send with @observe(name="phone-turn", as_type="agent"), so that each turn,
    #   and every model call, retrieval and tool call inside it, becomes one trace.
    def send(self, user_text: str) -> TurnResult:
        """Handle one turn of the call: the caller says `user_text`, and the agent replies.

        Adds the caller's message to `self.history`, builds this turn's system message, asks the
        model, adds its reply to the history and returns it.

        Lab 1 writes the turn with a single model call. Lab 2 wraps it in a trace. Lab 5 replaces
        the single call with a loop, so the model can use tools before it answers.
        """
        # TODO(lab2): put everything below inside
        #   with propagate_attributes(session_id=self.call_id, user_id=self.caller_id,
        #                             tags=["ridgeline-agent"],
        #                             metadata={"prompt_version": self.agent.prompt.version}):
        #   and pass trace_id=get_client().get_current_trace_id() to the TurnResult you return.
        #   (In this file, get_client is Langfuse's, imported at the top, not the OpenAI client.)
        self.ctx.turn += 1  # keep this line: Lab 5's booking guardrail counts the caller's turns
        self.history.append({"role": "user", "content": user_text})
        system = {"role": "system", "content": f"{self.agent.prompt.text}\n\n{self._context(user_text)}"}
        # TODO(lab5): replace the three lines below with the agent loop, at most
        #   self.agent.settings.max_steps model calls. Start from result = TurnResult(reply=GIVE_UP, ...).
        #   If a reply has no tool_calls, it is the answer: stop. Otherwise add the assistant's tool calls
        #   to the history, run each one with run_tool(...), and add each result as a "tool" message.
        #   Lab 5's README has the details.
        msg = self._model_call([system, *self.history])
        self.history.append({"role": "assistant", "content": msg.content})
        return TurnResult(reply=msg.content, prompt_version=self.agent.prompt.version)

    # ----------------------------------------------------------------- after the call: Lab 4 (written for you)
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
