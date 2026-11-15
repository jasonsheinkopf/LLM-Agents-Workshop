# The leaders' track

**A two-hour working session for senior leaders. No laptops, no code. You arrive with two
workflows from your own organization. You leave with one pilot, a named owner, and a one-page plan
that says what the pilot must prove before anyone trusts it.**

| | |
|---|---|
| **Format** | Two hours, facilitated, at tables of three to five |
| **Room** | 8 to 20 senior leaders. One facilitator. The sponsor is in the room |
| **Before the session** | 15 minutes of [preparation](#before-the-session): send two workflows, answer two questions |
| **Equipment** | Paper, pens and a wall. No laptops, no accounts, no network |
| **Cost** | Printing |
| **The other track** | Engineers build the agent this session uses as its evidence: the [one-day workshop](../README.md) |

This is not the engineers' day with easier examples. Engineers decide how to build an agent, so
they leave with a repository. You decide where an agent belongs, who owns it and what it must
never do alone, so you leave with a decision.

The session starts from the same phone call as the engineers' day. Ridgeline Climbing Gym, a
fictional gym, wants an AI to answer the phone, and a parent calls:

> *"Can my 8-year-old take the belay class on Saturday? And can you book us in?"*

Engineers spend a day building the agent that answers that call. You spend forty minutes with what
it left behind: three answers to the call, the record of the one that failed the caller, and the
scores from a change that felt better and tested worse. Each exhibit comes from the engineers'
track in this repo, and each one says where. Then you put Ridgeline down and spend the rest of the
session on your own workflows.

---

## Who this is for

Leaders who decide where AI agents are used, who owns them and how much risk is acceptable: heads
of functions and business units, and the people who own operations, customer service, finance or
risk. You need no technical background. You do need the authority to name a pilot and an owner,
because that is what the session produces.

It is not for the people who will build the agent. They get the [engineers' day](../README.md).
It is not an introduction to AI, and it is not a product demonstration. It is also the wrong
session for a group that cannot make the decision: if a pilot needs the approval of someone who is
not in the room, invite that person.

## What you will be able to do

By the two-hour mark, the room can do these five things. Each one has evidence you can see in the
room.

| | By the end of the session you can | Shown by |
|---|---|---|
| 1 | **Judge** an AI answer by its evidence, not by how confident it sounds | Your vote on three answers to the same call, and what you say you would check |
| 2 | **Ask** for the evidence behind any claim about an agent: the record of a failure, the test set, the scores before and after a change | Your votes on the trace and on the scoreboard, and the question you write down to ask a team of your own |
| 3 | **Choose** a first pilot from your own workflows, by scoring value, data readiness, the cost of a mistake and how easy it is to undo | Your table's scorecard, and the one workflow the room picks |
| 4 | **Gate** it: find every step that touches money, private information or a customer, and put a person there | The gate map of the chosen workflow |
| 5 | **Commit** to it: an owner, a baseline number, first test cases, a reason to stop and a review date | The one-page pilot plan, with two names on it |

## What you leave with

**A one-page [pilot plan](handouts/pilot-plan.md)**, written by the room and read aloud before
anyone leaves:

| Row | What it says |
|---|---|
| The pilot | One workflow, what the agent does in it, and what it will not do |
| The owner | One person in the room, by name. The sponsor, by name. The date of the review |
| The baseline number | What is counted today, its value today, and the value that would count as working |
| The first test cases | Five, in plain words: three ordinary, one where the right answer is "I don't know", one that must never happen |
| Where a person approves | Every step that touches money, private information or a customer, and who approves it |
| What would make you stop | Decided now, while nobody has anything to defend |
| The evidence at the review | What the owner must show in 30 days before the pilot goes any wider |

**A shortlist.** The workflows that scored well and were not picked, each with a name next to it.

**[Five questions](../handouts/questions-for-leaders.md) to ask any team building an agent**, with
what a good answer and a warning sign sound like. A good answer to each one is evidence. A demo is
not.

**The three exhibits.** Take them back. They are the shortest way to show a team of your own what
evidence looks like.

---

## How the session runs

Every block runs the same loop as the engineers' day: a short **explanation**, something **shown**
that has a failure in it, **work** at the tables, and a **debrief**. For engineers the work is
code. Here it is a vote, a score, a map and a decision.

| Time | Block | Explain and show | You work | Debrief and decide | You're done when |
|---|---|---:|---:|---:|---|
| 0:00 | Open: the call, the outcome, the rules | 5 min | | | You know what leaves the room: one page |
| 0:05 | **1. Three answers** | 3 min | 7 min | 5 min | You have voted on all three answers, and said what you would check |
| 0:20 | **2. Whose fault was it?** | 4 min | 5 min | 4 min | You have looked for the missing fact in the trace, and voted again |
| 0:33 | **3. Would you have shipped it?** | 4 min | 5 min | 5 min | You voted before you saw the scores, and can say what they showed that the demo did not |
| 0:47 | Break | | | | |
| 0:52 | **4. Score your own workflows** | 4 min | 20 min | 9 min | Your table hands in a scorecard, and the room has one pilot with an owner |
| 1:25 | **5. Place the approval gates** | 4 min | 10 min | 4 min | Every step that touches money, private information or a customer has a person on it |
| 1:43 | **6. The pilot plan** | 2 min | 10 min | | Every row is filled in, with two names and a date |
| 1:55 | Close | | | 5 min | You hand in an exit card that names the question you will ask, and of whom |
| 2:00 | End | | | | |

Under a quarter of the session is explanation. Half is you voting, scoring, mapping and writing.
The rest is debrief and decisions. No explanation runs longer than five minutes.

**The help shrinks as the session goes on.** In Blocks 1 to 3 you get an exhibit and one question.
In Blocks 4 and 5 you get a form, and the material is your own. In the last block you get one
page with seven rows, and the room writes all of it.

**Everyone decides before anyone talks.** Votes go up together. Scores are written alone, in
silence, and compared afterward. The disagreements are where the session earns its two hours.

**Nothing can fail on the day.** Every exhibit is on paper. There is no live demonstration to
crash and no account to set up.

## Before the session

About 15 minutes, one week before. The sponsor sends [this email](handouts/pre-session-email.md).

1. **Send two workflows** from your part of the organization: work that happens every week, where
   someone has to look something up or decide something. Three sentences each: what starts it,
   what someone needs to know to do it, and what it produces. Add roughly how often it happens and
   how long it takes.
2. **Answer two questions**: how confident you are, from 1 to 5, that you could tell whether an AI
   agent is good enough to put in front of customers or staff, and what your biggest doubt is
   about using one here. The doubts go on the wall, without names.
3. **Bring nothing confidential.** The [data rule](../docs/FACILITATOR.md#the-data-rule) applies
   to the cards and the wall as much as to any system: describe a workflow, never a customer.

The sponsor does three things before the day: confirms that the people in the room can name a
pilot and an owner, says what happens to the plan afterward, and sets the date of the 30-day
review.

## After the session

- **The next morning:** the plan, the shortlist and the gate map, by email.
- **Week one:** the owner meets whoever will build the pilot, and measures the baseline.
- **Day 30:** the review. The owner answers the five questions with evidence, and the group
  decides: go on, change it, or stop. A decision to stop, made on evidence, is a good result.

The emails are written: [handouts/follow-up-emails.md](handouts/follow-up-emails.md).

## Running it

The [facilitator guide](FACILITATOR.md) is the run of show: what to say and show in each block,
the failure to show on purpose, the question to ask, the line to land, what to do when a skeptic
calls it hype or nobody brought a workflow, and how to measure whether the session worked. The
[handouts](handouts/) are ready to print: the answer cards, the trace, the scoreboard, the
workflow scorecard, the gate map, the pilot plan, the exit card and the emails.

## How the two tracks fit together

The pilot plan is the brief for whoever builds the pilot. Its rows are the leaders' half of the
engineers' [workflow canvas](../handouts/workflow-canvas.md): the test cases, the actions that
need a person, what will not be automated, the owner and the number. The engineers' half is the
knowledge the agent needs and the tools it gets. A team that has not yet built an agent with
traces, tests and guardrails can learn the pattern in the [engineers' day](../README.md), on the
same agent your exhibits came from.

## Why it is built this way

The design is written out in [docs/DESIGN.md](../docs/DESIGN.md#same-topic-two-workshops), side by
side with the engineers' day. In short:

1. **It starts from the decision.** Leaders do not build agents. They decide where one is used,
   who owns it and what it may do alone. The five outcomes above were fixed first, and every block
   exists to produce one of them.
2. **It teaches through decisions, not definitions.** Nobody is asked to define retrieval. You are
   asked whose fault a failed answer was, and you find out that the agent was sent to the phone
   without the handbook.
3. **Everyone is voting within ten minutes**, and working on their own workflows before the first
   hour is over.
4. **Failure is planned.** The confident answer is the wrong one. The answer that failed the
   caller was not the model's fault. The change that felt better scored worse. The most exciting
   workflow loses on the scorecard.
5. **The evidence is real.** The trace, the scoreboard and the booking that stopped come from the
   agent in this repo, not from a slide. You learn to ask for evidence by being shown some.
6. **It measures what the room produced.** Votes are counted before and after each reveal, the
   plan is the evidence at the end, and the session is checked again thirty days later.
7. **It ends with an owner.** Nobody leaves with only a discussion. The room leaves with one page
   that names who does what next, and when the group looks at the evidence.

## The scenario is fictional

Ridgeline Climbing Gym, its handbook, prices, classes and callers are invented. The exhibits are
real in a narrower sense: they are what the agent in this repo said and did when it was run
against that invented gym. Each handout says which file or lab its content comes from, and marks
anything that is a sample and not a recorded reply.
