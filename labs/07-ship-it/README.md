# Lab 7: Make it yours

**Self-paced reading:** [Read the concept lesson first](../../lessons/07-transfer/README.md), then return here for the coding exercise. [Course map](../../START_HERE.md) · [Checklist](../../PROGRESS_TEMPLATE.md).

**Last block** · In the room: 25 min on your canvas, then 15 min of demos and the exit ticket · On your own: about 30 min, plus an hour in the following week
**Needs:** all keys

## Goal

You've built every piece on Ridgeline's phone call. This block is about your work, not
Ridgeline's. Take the workflow you brought this morning and leave with a plan for it that has a
name on it.

There are no steps in this lab. There is an outcome, and a page to put it on.

**By the end of this block you can:**
- map a workflow of your own onto the pattern you built today: knowledge, actions, confirmation, tests;
- say what you would not automate in it, and why;
- name who owns the next step, and what number will show it is working.

## Checkpoint

| | You're there when |
|---|---|
| **Floor** (every pair, before the demos) | Every row of your [workflow canvas](../../handouts/workflow-canvas.md) is filled in, and the last row has a person's name and a date |
| **Target** (most pairs) | Another pair has read your canvas and asked one question you couldn't answer. You wrote the question down |
| **Ceiling** (if you finish early) | [One improvement, the right way](#after-the-day-one-improvement-the-right-way), below, started on your Ridgeline agent |

## Part 1: Check what you built

```bash
repo $ uv run pytest                       # every lab passes on YOUR code now
workshop $ uv run python -m gym_agent.doctor
```

Then read your scoreboard from Lab 3 from top to bottom. It should tell a clear story:

| Run | What changed | What it fixed |
|---|---|---|
| v1, bare model | careful but wordy instructions | (baseline) |
| v2 prompt | "be brief" | nothing: a **regression** the experiment caught |
| v3 prompt | brief *and* keeps the rules | wordiness, without losing honesty or safety |
| + memory | handbook RAG, caller memories | **knowledge** |
| + tools | schedule, booking, transfer + guardrails | **action** |
| + evals and traces | throughout | **quality**: you can *prove* each step helped |

Those are the three gaps from Block 1, closed one at a time, with numbers.

## Part 2: Your workflow

Open your [workflow canvas](../../handouts/workflow-canvas.md). You filled in a row after each
block, so most of it is drafted. Finish it:

| Row | The question to settle now |
|---|---|
| The workflow and its trigger | Is it one workflow, or three? Pick the smallest one that would still be worth having |
| A good outcome | Could two people disagree about whether an answer was good? If so, tighten it |
| Five test cases | Is there one where the right answer is "I don't know", and one hostile one? |
| Knowledge it needs | Is that data green, yellow or red under [the data rule](../../handouts/workflow-canvas.md#the-data-rule)? |
| Actions it takes | Which action would you least want to see happen by mistake? That one needs confirmation in code |
| What we will not automate | If this row is empty, look harder |
| **Owner and next step** | A name, a first action, a date, and the number that tells you it is working |

The last row is the one that matters. A plan with no owner is a demo.

Then swap canvases with another pair. Read theirs, and ask the one question it doesn't answer.

## Part 3: Demos and the exit ticket

In a room, three pairs demo, two minutes each:

1. The phone call from Block 1, answered and booked.
2. Your scoreboard.
3. One failing case you would fix next, and **which layer it lives in**: the prompt, the
   knowledge, a tool, or the model. A layer, not a prompt tweak.

Then everyone fills in the [exit ticket](../../handouts/exit-ticket.md) and hands it in with the
pair's canvas.

On your own: record a 60-second version of that demo for a colleague, and answer the exit ticket's
four questions in writing.

## Debrief

1. Which of today's failures taught you the most?
2. Why did the numbers move when you added memory and tools, and not when you rewrote the prompt?
3. What is the first thing you will do differently on Monday?

## After the day: one improvement, the right way

This is the loop real teams run. Do it once on your Ridgeline agent in the week after the
workshop, while it is fresh. It takes about an hour.

Pick a failing case in your last run (there's usually one). Then:

1. **Read its trace.** Which step went wrong: retrieval, the prompt, a tool, or the model?
2. **Fix the right layer.** A retrieval miss isn't fixed by prompt wording. A missing rule isn't fixed by more context.
3. **If it's the prompt:** write `prompts/system_v4.md`, then `prompts push ... --label staging`.
4. **Run the experiment on staging**, then compare with production. Did your fix break anything else?
5. **Promote** only if it wins: `uv run python -m gym_agent.prompts promote <version>`.

```bash
workshop $ uv run python -m gym_agent.evals.upload_dataset          # if you added cases in the red-team round
workshop $ uv run python -m gym_agent.evals.run_experiment --label staging --name "v4 candidate"
```

Then do the first step on your canvas. To try the pattern on your own workflow, swap Ridgeline for
something you know: change `data/`, rewrite the test cases, and the rest of the code stays the same.

## The production checklist

What this workshop covered, and what you'd add before real customers call:

| Area | In this repo | Before production |
|---|---|---|
| Observability | Every turn, retrieval and tool call traced; sessions; user feedback scores | Alerts on error rate, latency and cost; PII masking in traces (Langfuse supports masking functions) |
| Evals | 19 cases, code checks, a calibrated judge, experiments | Hundreds of cases grown from production traces; run in CI on every prompt or code change; online evaluators scoring live traffic |
| Prompts | Versioned, labelled, fetched at runtime with a fallback | Review process for promotions; rollback runbook (it's one `promote` command) |
| Memory | Handbook RAG; per-caller memories with a filter | Re-ingest when the handbook changes; retention and deletion policy for memories; access logs |
| Tools | Allow-list, Pydantic validation, least privilege, two-step confirmation, step limit | Rate limits; idempotency keys on writes; audit log; human approval for high-risk actions |
| Security | Tool results as data; no high-risk tools exposed | Red-team test set for prompt injection; auth on the MCP server; secrets in a vault, not `.env` |

## What happens next

- **Tomorrow:** a recap, with a photo of your canvas.
- **Week one:** an office hour. Bring a trace of something that went wrong.
- **Day 30:** one email asking what happened to the plan on your canvas. An honest "it stalled,
  and here is where" is a useful answer.

You didn't just call an LLM today. You built an agent, measured it, tried to break it, and you
know what you would do next with your own.

**Finished?** Update your local [progress checklist](../../PROGRESS_TEMPLATE.md), revisit your workflow canvas in 30 days, or [return to Start here](../../START_HERE.md).
