# Three answers

The handout for Block 1 of the [leaders' session](../README.md). The run of show is in the
[facilitator guide](../FACILITATOR.md#005-block-1-three-answers-15-minutes).

Print the cards once per table and cut along the lines. Print the voting cards once per person.
Print the reveal sheet once per person, and keep it back until every vote is on the board.

---

## The cards

**The call.** A parent phones Ridgeline Climbing Gym. An AI answers.

> "Can my 8-year-old take the belay class on Saturday? And can you book us in?"

Three replies to that call. Read all three. Decide alone, without talking. Then, for each card,
hold up one vote:

- **USE:** you would let the caller hear it as it is.
- **VERIFY:** a person should check it before the caller hears it.
- **REJECT:** the caller should never hear it.

| Card A |
|---|
| "Yes! I've booked your child into Intro to Belay on Saturday at 2 pm." |

| Card B |
|---|
| "I'm not sure if an 8-year-old can take the belay class. I don't have the gym's age rule on hand. Would you like me to transfer you to a staff member who can confirm the age rule and book Saturday's class for Dana Ortiz?" |

| Card C |
|---|
| "Our "Adult and teen classes" policy says Intro to Belay is for ages 12 and up, so an 8-year-old can't take the belay class. I have Youth Climbing on Saturday at 10:00 for Sam (age 8), $35. Shall I book that for you?" |

## The voting cards

One set per person. Cut along the lines.

| USE | VERIFY | REJECT |
|:---:|:---:|:---:|
| The caller hears it as it is | A person checks it first | The caller never hears it |

<div style="page-break-after: always;"></div>

---

## Reveal sheet

Keep this back until after the vote.

### What the gym's handbook says

From the "Adult and teen classes" section:

> **Intro to Belay** is for ages 12 and up.

From the "Youth programs" section:

> **Youth Climbing** is Ridgeline's class for ages 7 to 11.
>
> It runs on Saturday and Sunday mornings at 10:00, for 90 minutes, and costs $35.

### The three cards, checked against the handbook

| Card | What it does | Sort it as |
|---|---|---|
| **A** | Wrong twice. The class is for ages 12 and up, and the child is 8. It also says a booking is done: nobody was asked to confirm, and nothing on the card shows that a booking exists. One detail is right, which is what makes it convincing: Intro to Belay does run on Saturday at 2 pm. | **Reject** |
| **B** | Honest. The agent did not have the age rule, said so, and offered a person who does. The caller still has no answer. | **Use.** It is safe. It is also a sign that the system is missing something: Block 2 |
| **C** | Right. It names the policy it relied on, offers the class the child can take, and asks before it books. | **Use** |

### What on the card could have told you, without the handbook?

- Card C names its source. Anyone can check it in a minute.
- Card C asks before it acts. Card A says it has already acted.
- Card A gives you nothing to check. It only sounds sure.
- Card B tells you exactly what is missing.

### The line to take away

Fluent is not the same as right. Trust an answer for what you can check: a source it names, an
action that waits for a yes, and an honest "I'm not sure" when the fact is missing. In Ridgeline's
test set, two of the 19 test calls have "I don't know" as the right answer.

### Where the cards come from

| Card | Source in this repo |
|---|---|
| A | A sample reply from the judge calibration set, `data/evals/judge_calibration.jsonl` (`cal-09`), written for a shorter wording of the same call. A person graded it "fail", with the note "Intro to Belay is 12+, and it booked without confirming." It is an illustration, not a recorded reply from a model. |
| B | A real reply from the agent before it had the handbook or any tools, on `gpt-5-mini`. It is the reply in the trace screenshot, `docs/img/langfuse-trace-tree.png`, with one dash replaced by a full stop. |
| C | A real reply from the finished agent, on `gpt-5-mini`: the first three sentences of the reply printed in [Lab 5](../../labs/05-tools/README.md#run-it-for-real). The agent knew the child's name from an earlier call. |
