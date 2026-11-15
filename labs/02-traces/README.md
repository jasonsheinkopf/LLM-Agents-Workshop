# Lab 2: Traces

**Self-paced reading:** [Read the concept lesson first](../../lessons/02-traces/README.md), then return here for the coding exercise. [Course map](../../START_HERE.md) · [Checklist](../../PROGRESS.md).

**Block 2** · In the room: 10 min explain and demo, 25 min build, 10 min debrief · On your own: about 30 min
**Cost:** cents · **Needs:** `OPENAI_API_KEY`, `LANGFUSE_*`

## Goal

Record every turn of every call in **Langfuse**, so you can open any conversation and see exactly
what the model was sent, what it said back, how long it took and what it cost. Then grade turns
with `/good` and `/bad`. Those graded traces become your first test cases in Lab 3.

**The failure to look for:** open the trace of an answer that didn't help. Read the system message. The fact the caller needed was never in it.

**By the end of this lab you can:**
- explain **traces, observations and sessions**, and why you trace *before* you tune;
- instrument an LLM app with a drop-in client wrapper and one decorator;
- find a bad answer in production and see *why* it happened;
- attach **scores** (user feedback) to traces.

## Checkpoint

| | You're there when |
|---|---|
| **Floor** (every pair, before the debrief) | The Lab 2 tests are green, and one of your own traces is open in Langfuse. You can point at what is missing from its system message |
| **Target** (most pairs) | You have scored a turn with `/bad`, found it again with a filter, and replayed the whole call as a session |
| **Ceiling** (if you finish early) | The tasks under [Ceiling](#ceiling-if-you-finish-early), below |

## The idea in two minutes

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

<img src="../../docs/img/langfuse-trace-tree.png" alt="A phone-turn trace in Langfuse: the tree, the generation, and the exact system message" width="760">

*A real trace. Notice the `user_feedback: False` score and the `user: dana` / session links at the top. The
system message has instructions and the caller's name, but **nothing about classes**, and the model
still couldn't help the caller. (Captured from a self-hosted Langfuse with `gpt-5-mini`; Langfuse
Cloud looks the same.)*

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

<img src="../../docs/img/langfuse-sessions.png" alt="Langfuse session view: the call shown as a conversation" width="760">

### Turn a bad trace into a test case (preview of Lab 3)

<img src="../../docs/img/langfuse-add-to-dataset.png" alt="The Add to menu on a trace, with Dataset and Annotation queue" width="760">

On a trace you scored `/bad`, use **Add to dataset** (top right of the trace view). Create a
dataset called `from-production`, and add the input and what the answer *should* have been. This
is how real teams grow test sets: from real failures, not imagination.

## What you should notice

- A model call is cheap to trace and expensive to debug without one.
- Latency and cost are visible per turn, which matters when you add retrieval and tool loops.
- "The agent is wrong" becomes a precise question: *which step* was wrong?

## Debrief

Answer these with your pair before you move on. In a room, the instructor asks pairs for their answers. On your own, write yours down.

1. What did the trace of your worst answer show you that the chat window did not?
2. Was that answer wrong because of the prompt, the knowledge, a tool, or the model? How do you know?
3. In a system you work on today, what would you want traced that isn't?

## Make it yours

On your [workflow canvas](../../handouts/workflow-canvas.md), fill in **a good outcome**. How would you know an answer was good? How would a user tell you it was bad?

## Ceiling: if you finish early

- Do [turn a bad trace into a test case](#turn-a-bad-trace-into-a-test-case-preview-of-lab-3), above, if you skipped it.
- Add `metadata={"channel": "phone"}` to `propagate_attributes`, and filter by it in Langfuse.
- Call with `--caller priya` and `--caller marcus`, then look at the **Users** view.
- Read `tools.run_tool` in the solution. It uses `start_as_current_observation(as_type="tool")` to
  trace a block of code that isn't a function. You'll see those spans in Lab 5.

## Stuck?

**Common failures in this lab:**
- `test_model_client_is_langfuse_wrapped` fails: the import must be `from langfuse.openai import OpenAI` *inside* the `if langfuse_enabled():` branch.
- `test_turn_sets_session_and_user` fails: `propagate_attributes(...)` must wrap the body of `send`, with `session_id=self.call_id` and `user_id=self.caller_id`.
- Traces appear but not grouped: the `@observe` decorator is missing, or it decorates a different function.

`diff workshop/gym_agent/llm.py solution/gym_agent/llm.py` · [TROUBLESHOOTING.md](../../docs/TROUBLESHOOTING.md#langfuse)

**Out of time for this lab?** `repo $ uv run python scripts/catch_up.py 3` gives you working Lab 2 code, so you start the next block with the room. Your own files are backed up first.

**Next:** [Read the next lesson →](../../lessons/03-evals/README.md), then follow its link to the lab.
