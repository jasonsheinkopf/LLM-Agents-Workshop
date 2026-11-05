# Lab 2: Traces

📺 **Video:** [Agents Unpacked, Episode 2: Traces, see what your agent did](https://youtube.com/@TODO)
⏱️ **Time:** 30 min · 💳 **Cost:** cents · 🔑 **Needs:** `OPENAI_API_KEY`, `LANGFUSE_*`

## Goal

Record every turn of every call in **Langfuse**, so you can open any conversation and see exactly
what the model was sent, what it said back, how long it took and what it cost. Then grade turns
with `/good` and `/bad`. Those graded traces become your first test cases in Lab 3.

**By the end of this lab you can:**
- explain **traces, observations and sessions**, and why you trace *before* you tune;
- instrument an LLM app with a drop-in client wrapper and one decorator;
- find a bad answer in production and see *why* it happened;
- attach **scores** (user feedback) to traces.

## Concepts

A **trace** is the record of one unit of work: here, one turn of a phone call. Inside it,
**observations** form a tree:

```
phone-turn  (agent)                          1.9 s   $0.0004
├── OpenAI-generation  (generation)          1.7 s   model, prompt, reply, tokens, cost
├── search_handbook    (retriever)  ← Lab 4  what was searched, what came back
└── book_class         (tool)       ← Lab 5  arguments, result, errors
```

A **session** groups traces. One phone call = one session, so you can replay a whole call turn by
turn. A **user** id groups sessions by caller. A **score** is a judgment attached to a trace: a
thumbs-up from a user, a judge's verdict, or a code check.

Why trace first? Because you can't fix what you can't see. When the agent says something wrong,
the trace shows whether it was the prompt, the retrieval, a tool result or the model. In Lab 3
you'll turn real traces into test cases.

## What you'll write

### Step 1: Wrap the OpenAI client: `workshop/gym_agent/llm.py`

Langfuse ships a drop-in replacement for the OpenAI client. Same class, same methods, but every
call becomes a `generation` observation, with prompt, completion, model, token counts, cost and latency.

```python
def get_client():
    require("OPENAI_API_KEY")
    if langfuse_enabled():
        from langfuse.openai import OpenAI   # same interface, plus tracing
    else:
        from openai import OpenAI
    return OpenAI()
```

That one import change is all it takes to trace every model call in the app.

### Step 2: Make each turn a trace: `workshop/gym_agent/agent.py`

Without this step, each model call would be its own separate trace. To group a whole turn (and,
later, its retrievals and tool calls) under one parent:

1. Decorate `send` with `@observe(name="phone-turn", as_type="agent")`.
2. Put the body inside `with propagate_attributes(...)`. That sets the session, user, tags and
   metadata on this trace and everything inside it:

```python
@observe(name="phone-turn", as_type="agent")
def send(self, user_text: str) -> TurnResult:
    with propagate_attributes(
        session_id=self.call_id,          # one phone call = one session
        user_id=self.caller_id,           # who is calling
        tags=["ridgeline-agent"],
        metadata={"prompt_version": self.agent.prompt.version},
    ):
        ...  # your Lab 1 code, indented one level
        return TurnResult(reply=msg.content, prompt_version=self.agent.prompt.version,
                          trace_id=get_client().get_current_trace_id())
```

`trace_id` lets the chat CLI attach your `/good` and `/bad` scores to the right trace.

### Step 3: Check it offline

```bash
repo $ uv run pytest tests/test_lab1_agent.py tests/test_lab2_traces.py
```

## Run it for real

Make sure the three `LANGFUSE_*` values are in `.env`, and the doctor passes. Then:

```bash
workshop $ uv run python -m gym_agent.chat
```

The banner now says `tracing: on`. Have a short call, and use the commands:

```
caller> Can my 8-year-old take the belay class on Saturday?
caller> /trace                 ← prints a link to this turn's trace
caller> /bad made up the class time
caller> What time do you close on Sunday?
caller> /good
caller> /end
```

> Traces are sent in the background in small batches. `/end` flushes them. If you Ctrl-C out of
> the chat, the last turn may not arrive.

### Look around Langfuse

| Where | What to look at |
|---|---|
| **Tracing → Traces** | Your `phone-turn` traces. Open one: the tree, the exact system message (prompt + context), tokens, latency and cost. |
| **Tracing → Sessions** | Your whole call, turn by turn, as a conversation. |
| **Scores** (on the trace, or the Scores page) | `user_feedback` = 0 or 1, with your comment. |
| **Users** | Dana's calls, grouped. |
| **Filters** | Filter traces by `user_feedback = 0`: there's your list of things to fix. |

Now open the trace where it made up the class time, and look at the system message. There's
nothing in it about classes. **The trace just diagnosed the knowledge gap.** No prompt wording can
fix that. Lab 4 will.

### Turn a bad trace into a test case (preview of Lab 3)

On a trace you scored `/bad`, use **Add to dataset** (top right of the trace view). Create a
dataset called `from-production`, and add the input and what the answer *should* have been. This
is how real teams grow test sets: from real failures, not imagination.

## What you should notice

- A model call is cheap to trace and expensive to debug without one.
- Latency and cost are visible per turn, which matters when you add retrieval and tool loops.
- "The agent is wrong" becomes a precise question: *which step* was wrong?

## Stretch goals

- Add `metadata={"channel": "phone"}` to `propagate_attributes`, and filter by it in Langfuse.
- Call with `--caller priya` and `--caller marcus`, then look at the **Users** view.
- Read `tools.run_tool` in the solution. It uses `start_as_current_observation(as_type="tool")` to
  trace a block of code that isn't a function. You'll see those spans in Lab 5.

## Stuck?

`diff workshop/gym_agent/llm.py solution/gym_agent/llm.py` · [TROUBLESHOOTING.md](../../docs/TROUBLESHOOTING.md#langfuse)

**Next:** [Lab 3: Evals →](../03-evals/)
