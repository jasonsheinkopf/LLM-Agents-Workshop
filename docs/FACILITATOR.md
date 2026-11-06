# Running this as a live workshop

This repo is built for self-paced learners, but it runs well as a live workshop. Two formats are
below. Both start from the outcomes and work backwards: every block exists because it moves
people toward something they can do at the end, and every block ends with a checkpoint that shows
whether it worked.

## Before you plan anything: the outcomes

Decide which of these your room needs. Everything else follows from that choice.

| Outcome | Who needs it | Evidence it landed |
|---|---|---|
| **O1.** Explain what an agent is: a model plus instructions, memory and tools, in a loop, measured by evals | Everyone | They can draw the diagram and say what each piece fixes |
| **O2.** Diagnose a bad answer from its trace, not from guesswork | Everyone | Shown a trace, they say which layer failed (prompt, data, tool, model) |
| **O3.** Judge an agent with a test set and a calibrated judge, not vibes | Everyone | They can read an experiment comparison and say whether to ship |
| **O4.** Build the pieces: tracing, evals, retrieval, tools, guardrails | Engineers | Their `workshop/` code passes the lab tests |
| **O5.** Ask the right questions of a vendor or a team building agents | Executives | They can list the five questions in the exec close (below) |

Executives need O1, O2, O3 and O5. Engineers need O1 to O4. Don't try to give one room both.

## Format A: Executive briefing (90 minutes, no laptops)

**For:** CEOs, founders, product and business leaders deciding whether and how to use agents.
**Goal:** they leave able to tell a real agent from a demo, and to ask for evidence instead of vibes.
**You need:** a projector, the solution running on your laptop with real keys, and the Langfuse
project from a previous run (traces, an experiment comparison, a trace with a guardrail hit).

| Time | Block | What happens | Checkpoint |
|---|---|---|---|
| 0:00 | **The call** | Play or act the phone call. Ask the room: what would the AI need to get this right? Collect answers on a board. | The board has knowledge, action and quality on it, in their words |
| 0:10 | **What makes an agent** (Ep 1) | Map their answers onto model, memory, tools, evals. One slide. | Ask someone to re-explain the diagram |
| 0:25 | **Live: watch it fail, then work** | Run the bare model on the call (`chat --no-tools --no-memory`), then the full agent. Same question, two answers. | Someone says "the first one made that up" |
| 0:40 | **Live: the trace** (Ep 2) | Open the bad answer's trace. Show the system message has no class facts. "The model didn't fail. It never had the fact." | Ask: whose fault was it? (not the model's) |
| 0:55 | **Evals in one picture** (Ep 3) | The experiment comparison: v1, v2 (regressed), v3 (promoted). Explain the regression nobody noticed in testing. | Ask: would you have shipped v2 from the chat demo? |
| 1:10 | **Guardrails** (Ep 5) | The trace where the model invented a class ID and the code rejected it. "The model proposes. Your code decides." | Ask: what should never be left to the model? |
| 1:20 | **The exec close** | The five questions to ask any agent team or vendor (below). Hand out the one-pager. | They can repeat at least three |
| 1:30 | End | | |

**The five questions** (put them on the last slide and the handout):
1. Show me a trace of a wrong answer. What went wrong, and how do you know?
2. What's in your test set, and where did it come from?
3. Who grades the answers, and how do you know the grader is right?
4. What can the agent do without a human confirming, and what stops it doing more?
5. When you change the prompt, what tells you it got better?

## Format B: Engineer workshop (one day, laptops, keys set up in advance)

**For:** developers who have called an LLM API but haven't built an agent with evals and tools.
**Goal:** every participant leaves with a working, traced, tested agent in their own repo and
can explain each piece.
**You need:** participants to complete [Lab 0](00-setup.md) *before the day* (send it a week ahead,
with the doctor command as the "you're ready" check). Budget 15 minutes at the start for the ones
who didn't. Have one spare OpenAI key for emergencies.

| Time | Block | Mode | Checkpoint |
|---|---|---|---|
| 9:00 | Setup triage | Everyone runs the doctor. Pair anyone red with a neighbour who is green. | All green by 9:15 |
| 9:15 | Ep 1 teach + **Lab 1** | Teach 10 min, build 25 min | `pytest tests/test_lab1_agent.py` green; everyone has made the bare model fail |
| 10:00 | Ep 2 teach + **Lab 2** | Teach 10, build 20 | Each person opens one of their own traces and finds the missing fact |
| 10:45 | Break | | |
| 11:00 | Ep 3 teach + **Lab 3** | Teach 15, build 45 | Experiment comparison on screen; the room votes which prompt to promote |
| 12:15 | Lunch | | Tell them the afternoon labs are the fun ones |
| 1:15 | Ep 4 teach + **Lab 4** | Teach 15, build 45 | `retrieval -k 3` hit rate on screen; the knowledge score moves in their re-run |
| 2:30 | Break | | |
| 2:45 | Ep 5 teach + **Lab 5** | Teach 15, build 50 | A live booking through the two-step confirmation; someone tries the injection case |
| 4:00 | Ep 6 teach + **Lab 6** | Teach 10, build 20 | Their tools appear in the MCP Inspector |
| 4:30 | **Ship it** | Scoreboard review. Each pair names the failing case they'd fix next and which layer it's in. | Each pair states a layer, not a prompt tweak |
| 5:00 | End | | |

**Facilitation notes**
- Tests are the checkpoint. Don't walk the room asking "is everyone done?"; ask "whose Lab 3 tests are green?" and send the greens to help the reds.
- When someone is stuck, open `solution/` with them and diff. The answer is always there, so stuckness never blocks the room.
- The judge calibration step is where the "aha" usually happens. Give it time. If their judge disagrees with the humans, that is the lesson, not a problem.
- Rate limits: experiments run four cases at a time per person. Thirty people hitting OpenAI at once is fine on a paid account; on a brand-new account tell them to run with `--limit 5` first.
- Everything in `data/` is fictional. If someone asks whether it's a real gym, that's a good moment to talk about what you'd need to do with real customer data (PII in traces, retention of memories; see `labs/07-ship-it`).

## Half-day variant (3.5 hours, engineers)

Labs 1, 2, 3 and 5 in full; show Lab 4 as a demo and give Lab 6 as homework. Memory is the easiest
lab to do alone, and tools are the hardest to debug alone, so keep tools in the room.

## What to measure about the workshop itself

Do what the course teaches: measure, don't vibe-check.
- **During:** the test checkpoints tell you where the room is. If more than a third are red at a checkpoint, stop and teach, don't push on.
- **End of day:** three questions. Which lab was most valuable? Where did you get stuck longest? What would you build next week? The "stuck longest" answers go straight into [TROUBLESHOOTING.md](TROUBLESHOOTING.md).
- **Two weeks later:** one email. Did you build anything? That answer is the only one that matters.
