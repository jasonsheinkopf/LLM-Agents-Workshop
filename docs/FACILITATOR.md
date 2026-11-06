# Running this as a live workshop

This repo is built for self-paced learners, but it runs well as a live workshop. The principle is
the same one the course teaches: **build, inspect, improve**, not lecture, memorize, repeat. Design
backwards from what people should be able to build or change at work the next morning, teach only
enough theory to enable that, get them building early, make failure visible, measure what they
built, and finish with an owner and a next step.

## 1. Start from the outcomes

Decide which outcomes your room needs. Everything else follows from that choice.

| Outcome | Who needs it | Evidence it landed |
|---|---|---|
| **O1.** Explain what an agent is: a model plus instructions, memory and tools, in a loop, measured by evals; and tell a scripted workflow from an agent that directs its own steps | Everyone | They can draw the diagram and say what each piece fixes |
| **O2.** Diagnose a bad answer from its trace, not from guesswork | Everyone | Shown a trace, they name the layer that failed: prompt, data, tool or model |
| **O3.** Judge an agent with a test set and a calibrated judge, not vibes | Everyone | They can read an experiment comparison and say whether to ship |
| **O4.** Build the pieces: tracing, evals, retrieval, tools, guardrails | Engineers | Their `workshop/` code passes the lab tests |
| **O5.** Ask the right questions of a vendor or a team building agents | Leaders | They can list the five questions in the executive close |
| **O6.** Map one of their own workflows onto the agent pattern, with a named owner | Everyone | A filled-in workflow canvas with a next step and a success measure |

Executives need O1, O2, O3, O5 and O6. Engineers need O1 to O4 and O6. Don't give one room both.

**Four levels of success**, from weakest to strongest evidence. Plan to measure all four:

| Level | Question | How this course measures it |
|---|---|---|
| Knowledge | Did they understand it? | The checkpoint questions in each block below |
| Skill | Can they do it? | Lab tests green; a working agent in their own repo |
| Transfer | Did they use it afterwards? | The 30-day email: did you build anything? |
| Impact | Did work improve? | The sponsor's measure for the workflow they chose (hours, cycle time, error rate) |

The workshop KPI that matters is not "did they like it". It is: **what share of participants left
with a working, measured workflow, and what share of those reached real use within 30 days?**

## 2. Pre-work (one week before)

- **Environment:** send [Lab 0](00-setup.md). "You're ready" means the doctor command prints three PASS lines. Budget 15 minutes on the day for the ones who didn't.
- **Bring one workflow:** each participant names a repetitive or decision-heavy task from their own job, with its trigger, inputs, decisions and output. This becomes their challenge in the last block.
- **Data rule, agreed with the sponsor before the day:**
  - **Green:** public, synthetic or deliberately created workshop data. Everything in `data/` is green.
  - **Yellow:** internal, non-sensitive data the sponsor has approved for the workshop.
  - **Red:** customer PII, health data, credentials, legal or unreleased financial material. Never in a workshop unless explicitly approved, and never into a third-party service without it.
- **Sponsor:** a named person who can say which workflows matter and who will own the prototypes afterwards. Without one, the prototypes stay demos.

## 3. Format A: Executive briefing (90 minutes, no laptops)

**For:** leaders deciding whether and how to use agents.
**Promise:** they leave able to tell a real agent from a demo, and to ask for evidence instead of vibes.
**You need:** a projector; the solution running on your laptop with real keys; a Langfuse project
from a previous run (traces, an experiment comparison, a trace with a guardrail hit); and a cached
screen recording of the live parts, in case the network or an API fails.

| Time | Block | What happens | Checkpoint |
|---|---|---|---|
| 0:00 | **The call** | Play the phone call. Ask the room: what would the AI need to get this right? Collect answers on a board. | The board has knowledge, action and quality on it, in their words |
| 0:10 | **What makes an agent** (Ep 1) | Map their answers onto model, memory, tools, evals. One slide. Then: workflow vs agent, and why you start with the simplest thing that works. | Someone re-explains the diagram |
| 0:25 | **Live: fail, then work** | Run the bare model on the call (`chat --no-tools --no-memory`), then the full agent. Same question, two answers. | Someone says "the first one couldn't actually help" |
| 0:40 | **Live: the trace** (Ep 2) | Open a wrong or useless answer's trace. Show the system message has no class facts. "The model didn't fail. It never had the fact." | Ask: whose fault was it? (not the model's) |
| 0:55 | **Evals in one picture** (Ep 3) | The experiment comparison: v1, v2 (regressed), v3 (promoted). The regression nobody saw in the chat demo. | Ask: would you have shipped v2 from the demo? |
| 1:10 | **Guardrails** (Ep 5) | The trace where the model proposed a bad tool call and the code rejected it. "The model proposes. Your code decides." Risk rises when a system can *act*, not just answer. | Ask: what should never be left to the model? |
| 1:20 | **Your workflow + the five questions** | Each leader names one workflow and what they would not automate in it. Hand out the five questions. | They can repeat at least three |
| 1:30 | End | | |

**The five questions** (last slide and handout):
1. Show me a trace of a wrong answer. What went wrong, and how do you know?
2. What's in your test set, and where did it come from?
3. Who grades the answers, and how do you know the grader is right?
4. What can the agent do without a human confirming, and what stops it doing more?
5. When you change the prompt, what tells you it got better?

## 4. Format B: Engineer workshop (one day, laptops)

**For:** developers who have called an LLM API but haven't built an agent with evals and tools.
**Promise:** every participant leaves with a working, traced, tested agent in their own repo, and a
plan for one workflow of their own.
**Rhythm:** 10–15 minutes of teaching, then build. No block of talking longer than 15 minutes.
**Staffing:** one instructor up to 20 people; add a TA per 10 beyond that. For a room with cloud
or SSO complications, one person whose only job is unblocking laptops.

| Time | Block | Mode | Checkpoint |
|---|---|---|---|
| 9:00 | Setup triage | Everyone runs the doctor. Pair reds with greens. | All green by 9:15 |
| 9:15 | Ep 1 teach + **Lab 1** | Teach 10 min, build 25 | `pytest tests/test_lab1_agent.py` green; everyone has made the bare model fail |
| 10:00 | Ep 2 teach + **Lab 2** | Teach 10, build 20 | Each person opens one of their own traces and finds the missing fact |
| 10:45 | Break | | |
| 11:00 | Ep 3 teach + **Lab 3** | Teach 15, build 45 | Experiment comparison on screen; the room votes which prompt to promote |
| 12:15 | Lunch | | |
| 1:15 | Ep 4 teach + **Lab 4** | Teach 15, build 45 | `retrieval -k 3` hit rate on screen; the knowledge score moves in their re-run |
| 2:30 | Break | | |
| 2:45 | Ep 5 teach + **Lab 5** | Teach 15, build 40 | A live booking through the two-step confirmation |
| 3:40 | **Red-team round** | Everyone throws five adversarial inputs at their agent: the injection case, a wrong age, a changed detail after the summary, a question the handbook can't answer, an injury. | Each pair shows one guardrail that held and one answer that needs a test case |
| 4:00 | Ep 6 teach + **Lab 6** | Teach 10, build 15 | Their tools appear in the MCP Inspector |
| 4:25 | **Make it yours** | Pairs map the workflow they brought onto the pattern: what's the handbook, what are the tools, what needs confirmation, what are five test cases. Fill the canvas below. | A canvas per pair, with an owner |
| 4:50 | Demo round + close | Three pairs demo. Each names the failing case they'd fix next and which layer it's in. | They name a layer, not a prompt tweak |
| 5:00 | End | | |

**The workflow canvas** (one page per pair; also the executive handout):

| | |
|---|---|
| Workflow and trigger | |
| What a good outcome looks like (the success measure) | |
| Knowledge it needs (the "handbook") | |
| Actions it takes (the "tools"), and which need a human to confirm | |
| Five test cases, including one adversarial | |
| What we will *not* automate | |
| Owner and next step | |

**Facilitation notes**
- Tests are the checkpoint. Don't ask "is everyone done?"; ask "whose Lab 3 tests are green?" and send the greens to help the reds.
- When someone is stuck, open `solution/` with them and diff. The answer is always there, so being stuck never blocks the room.
- Show a failure on purpose in every live demo. A flawless demo teaches syntax; a failure teaches engineering.
- Judge calibration is where the "aha" usually happens. Give it time. A judge that disagrees with the humans is the lesson, not a problem.
- Rate limits: experiments run four cases at a time per person. Thirty people on a paid account is fine; on a brand-new account, run with `--limit 5` first.
- Mixed skill levels: pair a stronger coder with a domain expert, not strongest with strongest. Stretch goals in every lab README keep the fast ones busy.
- If the API or network fails mid-demo, switch to the cached recording and keep teaching. Carry a spare key.

## 5. Half-day variant (3.5 hours, engineers)

Labs 1, 2, 3 and 5 in full; demo Lab 4; set Lab 6 as homework. Keep the red-team round and "make
it yours", shortened to ten minutes each. Memory is the easiest lab to do alone; tools are the
hardest to debug alone, so keep tools in the room.

## 6. Assessment and follow-up

Measure the workshop the way the course measures agents.

| When | What | Looks like |
|---|---|---|
| Before | Confidence survey, environment check, one workflow per person | Doctor green; a filled workflow line |
| During | Lab checkpoints; the red-team round | If more than a third are red at a checkpoint, stop and teach |
| End of day | Three questions: most valuable lab, where you were stuck longest, what you'll build next week | "Stuck longest" answers go into [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| Week 1 | Office hour | The questions people bring tell you what the labs didn't teach |
| Day 30 | One email: did you build anything? Did it reach anyone? | This is the number that matters |
| Day 60–90 | Sponsor check: what shipped, what it changed, what's next | Decide whether the next cohort runs |

**Adoption funnel to report to the sponsor:** invited → attended → completed → built → piloted → adopted.

**Project rubric** for the "make it yours" demos, if you score them:

| Dimension | Weight |
|---|---:|
| Problem clarity and business value | 25% |
| Works on its five test cases | 25% |
| Evaluation: a test set exists, and the judge was checked | 20% |
| Safety: confirmation on actions, least privilege, nothing red in the data | 20% |
| Explanation: can they say which layer each failure lived in | 10% |

## 7. Things that go wrong, and what to do

| Risk | What it looks like | Mitigation built into this course |
|---|---|---|
| Confident wrong answers | Fluency mistaken for correctness | The Episode 1/2 "bare model" moment; the test set; the judge |
| Data leakage | Real customer data in a third-party service | The green/yellow/red rule; everything in `data/` is fictional |
| Prompt injection | Retrieved or tool text steers the agent | Tool results as data; the `g-injection` case; the red-team round |
| Excess autonomy | An action nobody confirmed | The two-step confirmation in code; no delete or refund tools exist |
| Cost runaway | Loops | `AGENT_MAX_STEPS`; experiments capped at four at a time |
| Demo fragility | API or network down on the day | Cached recording; spare key; offline tests still run |
| Skill gap | Some bored, some lost | Pre-work doctor; pairing; stretch goals; `solution/` to diff against |
| Workshop theater | Prototypes never reach work | The sponsor, the canvas, the owner, the 30-day email |
