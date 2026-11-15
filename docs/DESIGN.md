# How this workshop was designed

A workshop is not a short course. Its job is not to cover material. Its job is to change what
someone does at work the following week. Everything in this repo follows from that, and this page
shows the reasoning so that anyone who runs or adapts the workshop knows what each part is for.

The design was done backward, in this order: who is in the room, what they should be able to do,
what would prove it, and only then the agenda. The agenda is the fourth decision, not the first.

## The design on one page

| | Decision | In this workshop |
|---|---|---|
| 1 | **Who** is in the room, and what do they decide? | Engineers who have called an LLM API and now have to build something reliable with one. Their question is "how do I make this trustworthy?" Their usual failure is a demo that works once. |
| 2 | **Outcome**: what can they do afterward that you could watch them do? | The [five outcomes](#the-outcomes-and-the-evidence-for-each): build, diagnose, measure, guard, transfer. |
| 3 | **Evidence**: what proves it? | Green tests on their own code, a scoreboard of experiments, a red-team record, and a filled-in workflow canvas. |
| 4 | **Arc**: how does a block run? | Explain one idea, demo it with a failure, build in pairs, debrief. Six times. |
| 5 | **Labs**: how is the help structured? | A starter repo where the boring parts are done. Floor, target and ceiling in every lab. Help that shrinks through the day. |
| 6 | **Room**: what has to be true on the day? | Pre-work done, synthetic data only, pairs chosen on purpose, a backup for everything live. |
| 7 | **Measure**: how do we know it worked? | Four moments: before, during, at the end, and thirty days later. |
| 8 | **Follow-through**: what happens next? | Every pair leaves with an owner and a next step. An office hour in week one, one email at day thirty. |

## Who it is for, and who it is not

Executives, product managers and engineers do not need the same workshop with different examples.
They make different decisions and fail in different ways. This workshop is for engineers, so its
artifact is a working repository with tests and traces.

Leaders who decide where to use agents need a different outcome (a decision, not a repository),
so they get a different session:
[the 90-minute briefing](FACILITATOR.md#variant-executive-briefing-90-minutes-no-laptops). It uses
the same agent as its evidence and asks nobody to write code.

## The outcomes, and the evidence for each

An outcome has to be something you can watch someone do. "Participants will understand agents"
fails that test: you cannot watch someone understand, so you cannot design for it or check it.
Each outcome here follows one template: *by when, who can do what, to what standard, shown by what.*

| | By 5:00, every pair can | Shown by | Where it is built |
|---|---|---|---|
| 1 | **Build** an agent that answers from a handbook and books a class only after the caller confirms | Lab tests green on their own code; one live booking | Blocks 1, 4, 5 |
| 2 | **Diagnose** a wrong answer from its trace and name the layer that failed | Each person opens one of their own bad traces and says what was missing | Block 2, then used in every later block |
| 3 | **Measure** a change before shipping it | Their scoreboard: a regression caught, a better prompt promoted, two re-runs that moved | Block 3, re-run in Blocks 4 and 5 |
| 4 | **Guard** the actions that matter in code | One guardrail that held under attack, one failure turned into a test case, and the same confirmation step holding for an outside client over MCP | Block 5, the red-team round, Block 6 |
| 5 | **Transfer** the pattern to their own work | A workflow canvas with five test cases, an owner and a next step | One row per block, finished in the last block |

**The test for every block** was: which outcome does this produce? A block with no answer was cut,
however interesting. That is why these are not in the day:

- **Fine-tuning, open models, quantization.** None of the five outcomes needs them.
- **Multi-agent orchestration.** The honest advice from the model labs is to start with the
  simplest thing that works and add autonomy only when the task needs it. One agent with tools is
  enough to teach every idea here.
- **An agent framework.** Participants write the loop themselves in about twenty lines. Once they
  have, any framework is easy to read. Taught the other way round, the framework hides the idea.
- **Deployment.** It is in the [production checklist](../labs/07-ship-it/README.md#the-production-checklist)
  as what comes next, with no lab.

## The arc of a block

Every block runs the same loop, six times in the day.

| Step | How long | What happens |
|---|---|---|
| **Explain** | 5 to 15 minutes | One new idea, and the problem it solves. Never more than one. |
| **Demo** | inside the same 5 to 15 minutes | The instructor does the first step live, thinking out loud, and shows a failure on purpose. |
| **Build** | 12 to 50 minutes | Pairs do the lab. The instructor circulates. |
| **Debrief** | 3 to 10 minutes | Three questions: what happened, why, and what will you do differently? |

Three decisions sit behind that loop.

**Explanations are short.** People can hold very little new material in working memory at once,
so one idea per block beats five. Over the working day, about a fifth is explanation and demo,
three fifths is building, and a fifth is checking and debriefing.

**The failures are planned.** A flawless demo teaches syntax. A demo that breaks, and is diagnosed
out loud, teaches engineering. With language models, failure is the normal case, so the day is
built around it:

| Block | The failure on purpose | What it teaches |
|---|---|---|
| 1 | The bare model cannot answer the caller, and cannot book | Prompting cannot fix missing knowledge or missing abilities |
| 2 | The trace of that answer has no class information in it | The model did not fail. It never had the fact |
| 3 | Prompt v2 feels better in chat and scores worse on honesty and safety | You cannot judge an agent one chat at a time |
| 4 | Retrieval with `-k 1` misses short, vague questions | If retrieval misses, no prompt can save the answer |
| 5 | The red-team round: five inputs written to break the agent | The rules that matter belong in code, not in a sentence the model may ignore |

**The help shrinks.** This is gradual release of responsibility: I do, we do, you do.

| Blocks | Mode | What is on the page |
|---|---|---|
| 1 and 2 | Code-along | Every line the pair writes |
| 3, 4 and 5 | Pairs build | The parts that carry the lesson (graders, retriever, guardrails) are described, not given. Tests say when they work |
| Red-team round, Make it yours | Challenge | An outcome and constraints. No steps |

## How the labs keep everyone moving

Once people are building, the instructor's attention is the scarce resource. The labs are built to
spend as little of it as possible on things that are not learning.

- **A starter repo with the boring parts done.** The app runs before any lab is written. Each lab
  asks for a few short functions: the decisions that matter, not the boilerplate.
- **Tests are the checkpoint.** They are offline, free and instant. The instructor never asks "is
  everyone done?" The question is "whose Lab 3 tests are green?"
- **Floor, target, ceiling.** Every lab names the minimum every pair must reach (the floor, which
  the instructor protects), what most pairs finish (the target), and a stretch for pairs who finish
  early (the ceiling). Fast pairs stay busy and nobody is left behind.
- **A way to catch up.** `scripts/catch_up.py N` puts a pair's code in the state it should be in
  at the start of Lab N, after backing up what they wrote. Falling behind in one block does not
  cost them the next.
- **Pairs chosen on purpose.** A stronger coder with someone who knows the business process, not
  strongest with strongest. Two people also halve the number of laptops that can fail.
- **One running example.** The same phone call from 9:15 to 5:00. Nobody spends attention learning
  a new scenario in each block.

## How we know it worked

Most training is judged by whether people liked it, because feedback forms are easy to collect.
That is the weakest of four kinds of evidence. This workshop plans for all four.

| Level | Question | How this workshop measures it |
|---|---|---|
| Reaction | Did they find it useful? | The [exit ticket](../handouts/exit-ticket.md): most valuable block, where they were stuck longest |
| Learning | Can they do it in the room? | Lab tests green, the scoreboard, the red-team record |
| Behavior | Did they use it afterward? | The [day-30 email](../handouts/follow-up-emails.md): did you build anything, and did it reach anyone? |
| Results | Did the work get better? | The sponsor's own measure for the workflow each pair chose |

It measures at four moments: before (the pre-work answers and the doctor check), during (the
checkpoint in every block), at the end (the artifacts and the exit ticket), and thirty to ninety
days later.

**The targets.** At 5:00, at least four pairs in five have green tests through Lab 5 and a
filled-in scoreboard, and every pair hands in a canvas with an owner. At day thirty, the number
that matters is how many of those canvases became something a real person used.

**The measurement feeds the labs.** If a third of the room is stuck at the same checkpoint, that
is one unclear instruction, not a third of the room failing. "Where were you stuck longest?" goes
into [TROUBLESHOOTING.md](TROUBLESHOOTING.md) and the lab README is fixed before the next room.

## What happens after the day

Prototypes die when nobody owns them. A great day with impressive demos and no change afterward
is workshop theater. So the last block is not a wrap-up: it is where each pair names a workflow
of their own, what they will not automate in it, who owns it and what happens next. Then there is
a light structure to keep it alive: a recap the next morning, an office hour in week one, one
email at day thirty, and a check with the sponsor at day sixty to ninety. The emails are written:
[handouts/follow-up-emails.md](../handouts/follow-up-emails.md).

## Running it more than once

A workshop that lives in one instructor's head cannot be run by a second instructor. This one is
written down so that it can: the [facilitator guide](FACILITATOR.md) has the timing, what to say,
the planned failure, the checkpoint and the known sticking points for every block; the
[handouts](../handouts/) are ready to send; the doctor command checks every laptop the same way;
and the starter repo behaves the same on every machine because the dependencies are pinned.

The core is fixed and the edge is meant to be changed. To run it for a particular team, keep the
six blocks and swap the scenario: replace the handbook, the schedule and the test cases in `data/`
with the team's own (synthetic or approved) data, and the code stays the same.

## The ideas this draws on

- **Backward design**: decide the result, then the evidence, then the activities. Grant Wiggins
  and Jay McTighe, *Understanding by Design* (1998).
- **The four levels of training evaluation**: reaction, learning, behavior, results. Donald
  Kirkpatrick (1959).
- **Gradual release of responsibility**: I do, we do, you do. P. David Pearson and Margaret
  Gallagher (1983).
- **Cognitive load**: working memory is small, so teach one idea at a time. John Sweller (1988).
- **The forgetting curve**: what is not practiced fades within days. Hermann Ebbinghaus (1885).
- **Start simple**: add agent complexity only when the task needs it. Anthropic, *Building
  effective agents* (2024).

Where this page gives numbers for time splits, room sizes and staffing, they are design guidance,
to be adjusted for the room in front of you.
