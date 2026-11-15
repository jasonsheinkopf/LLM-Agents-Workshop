# Lab 1: Your first agent

**Self-paced reading:** [Read the concept lesson first](../../lessons/01-first-agent/README.md), then return here for the coding exercise. [Course map](../../START_HERE.md) · [Checklist](../../PROGRESS_TEMPLATE.md).

**Block 1** · In the room: 10 min explain and demo, 25 min build, 10 min debrief · On your own: about 30 min
**Cost:** a few cents · **Needs:** `OPENAI_API_KEY`

## Goal

Make one model call with a system prompt and keep the conversation going. Then call the gym and
watch the bare model fail in three ways. The rest of the day fixes them.

**The failure to look for:** ask it to book. It says it can't, or says it has when nothing happened.

**By the end of this lab you can:**
- explain what a chat completion call is: messages in, one message out;
- explain the roles in a conversation (`system`, `user`, `assistant`) and why history is resent every turn;
- name the three gaps between a model and an agent: **knowledge**, **action** and **quality**.

## Checkpoint

| | You're there when |
|---|---|
| **Floor** (every pair, before the debrief) | `uv run pytest tests/test_lab1_agent.py` is green, and you have asked your agent the phone-call question and asked it to book |
| **Target** (most pairs) | You have seen all three gaps for yourself, and can say which later block fixes each one |
| **Ceiling** (if you finish early) | The tasks under [Ceiling](#ceiling-if-you-finish-early), below |

## The idea in two minutes

A language model is a function: **text in → the next likely text out**. It has no memory between
calls. Every turn, you send the *whole* conversation:

```python
client.chat.completions.create(
    model="gpt-5-mini",
    messages=[
        {"role": "system",    "content": "You are the phone assistant for Ridgeline..."},  # instructions
        {"role": "user",      "content": "Hi, what time do you close?"},                    # caller
        {"role": "assistant", "content": "We close at 10 pm on weekdays."},                 # model (earlier turn)
        {"role": "user",      "content": "And on Sunday?"},                                 # caller (now)
    ],
)
```

The **system prompt** is the agent's job description. It goes first, every time. Our agent also
adds a little **context** after it: who is calling (from caller ID). In Lab 4, it will add memories
and handbook pages too.

## What you'll write

File: `workshop/gym_agent/agent.py`. Find the `TODO(lab1)` comments (`grep -n "TODO(lab1)" workshop/gym_agent/agent.py`).

### Step 1: `Call._model_call(messages)`: one model call

`kwargs` already holds the model name and the messages. Make the call, and return the model's
message (not the whole response):

```python
resp = self.agent.client.chat.completions.create(**kwargs)
return resp.choices[0].message
```

Leave the `TODO(lab3)` and `TODO(lab5)` comments where they are. You'll come back to them.

### Step 2: `Call.send(user_text)`: one turn of the call

1. Append the caller's message to `self.history` as `{"role": "user", "content": user_text}`.
2. Build the system message: the prompt text, a blank line, then `self._context(user_text)`.
3. Call `self._model_call([system, *self.history])`.
4. Append the reply to `self.history` as an `assistant` message.
5. Return `TurnResult(reply=msg.content, prompt_version=self.agent.prompt.version)`.

<details>
<summary>Show the answer</summary>

```python
def send(self, user_text: str) -> TurnResult:
    self.ctx.turn += 1
    self.history.append({"role": "user", "content": user_text})
    context = self._context(user_text)
    system = {"role": "system", "content": f"{self.agent.prompt.text}\n\n{context}"}
    msg = self._model_call([system, *self.history])
    self.history.append({"role": "assistant", "content": msg.content})
    return TurnResult(reply=msg.content, prompt_version=self.agent.prompt.version)
```

Why isn't the system message stored in `history`? Its context changes every turn. In Lab 4 it
will hold *this* turn's handbook pages, so it is rebuilt each time instead.
</details>

### Step 3: Check it offline

```bash
repo $ uv run pytest tests/test_lab1_agent.py
.....                                                     [100%]
5 passed
```

The tests use a fake model, so they're free and instant. They check the system prompt goes first,
the history is kept, and so on.

## Run it for real

```bash
workshop $ uv run python -m gym_agent.chat
```

You're calling as **Dana** (`--caller` picks someone else). The banner shows what's switched on:
`tools: none · memory: off · tracing: off`. That's right for now.

Try the phone call the day is built around, then a few more:

```
caller> Hi, can my 8-year-old take the belay class on Saturday? And can you book us in?
caller> How much is a day pass for a 12-year-old?
caller> Great, book it.
caller> /end
```

## What you should notice: the three gaps

| Gap | What happens | Why | Fixed in |
|---|---|---|---|
| **Knowledge** | It invents prices, ages and class times, or gives generic advice ("most gyms require..."). | The model has never seen Ridgeline's handbook. Its weights are frozen. | Lab 4 (memory) |
| **Action** | It says "You're booked!" but nothing was booked. Or it apologises that it can't book. | A model only writes text. It can't touch your systems. | Lab 5 (tools) |
| **Quality** | Every answer *sounds* fine. Is it right? Is v2 of the prompt better than v1? You can't tell. | You're judging on vibes, one chat at a time. | Labs 2 and 3 (traces, evals) |

> The system prompt it's using is `prompts/system_v3.md` (read it). Even with careful
> instructions such as "only state facts from your context", it has no facts to state yet. That's
> the point: **prompting can't fix missing knowledge or missing abilities.**

## Debrief

Answer these with your pair before you move on. In a room, the instructor asks pairs for their answers. On your own, write yours down.

1. What happened when you asked it to book?
2. Why can't a better system prompt fix that? Which of the three gaps is it?
3. The next time someone shows you an impressive agent demo, what will you ask to see?

## Make it yours

On your [workflow canvas](../../handouts/workflow-canvas.md), fill in the first row: **the workflow and its trigger**. What starts it, and what does a finished one look like?

## Ceiling: if you finish early

- Run `--caller priya` and ask about her membership. The model knows her name from `_context`, but nothing else.
- Swap the prompt: `uv run python -m gym_agent.chat --prompt-file ../prompts/system_v1.md` uses the wordy v1 prompt instead of `system_v3.md`. Ask the same questions and compare. Keep the comparison in mind for Lab 3.
- Read `gym.py`'s `describe_caller`. It's the simplest kind of context: a fact your *code* knows and injects.

## Stuck?

**Common failures in this lab:**
- `AttributeError: 'NoneType' object has no attribute 'content'`: `_model_call` returned the response, not `.choices[0].message`.
- `test_conversation_history_is_kept` fails: you're not appending the assistant reply to `self.history`, or you're appending the system message too (don't; it's rebuilt every turn).
- The chat replies but every answer ignores who is calling: the system message must include `self._context(user_text)`.

Compare with the answer: `diff workshop/gym_agent/agent.py solution/gym_agent/agent.py` (the
solution also has Labs 2 to 5 done, so focus on `_model_call` and `send`).
Common errors are in [TROUBLESHOOTING.md](../../docs/TROUBLESHOOTING.md).

**Out of time for this lab?** `repo $ uv run python scripts/catch_up.py 2` gives you working Lab 1 code, so you start the next block with the room. Your own files are backed up first.

**Next:** [Read the next lesson →](../../lessons/02-traces/README.md), then follow its link to the lab.
