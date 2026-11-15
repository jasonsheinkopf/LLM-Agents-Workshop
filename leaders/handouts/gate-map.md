# Approval-gate map

The handout for Block 5 of the [leaders' session](../README.md). The run of show is in the
[facilitator guide](../FACILITATOR.md#125-block-5-place-the-approval-gates-18-minutes).

Print the map once per table, with the Ridgeline example on the back. Draw the map large on the
wall as well: the wall copy is the one the room agrees.

---

## The map

**The pilot:** ____________________________________________  **Table:** ____________

**1. Copy the steps from the wall.** Five to eight, from what starts the workflow to what finishes
it. One line each: who or what does it, and what changes.

**2. Mark each step.** Tick every column that applies.

- **M: money.** The step spends, refunds, prices or commits money.
- **P: private information.** The step reads or sends information about a person, or anything
  that is yellow or red under the data rule.
- **C: a customer.** Something is sent to, promised to or changed for a customer or a member of
  the public.

**3. Decide who decides.** Write one letter for each step.

- **A: the agent, alone.** Only for a step with no tick.
- **H: the agent prepares, a person approves.** The person sees what will happen before it
  happens, and can say no.
- **X: a person only.** The agent does not do this step at all.

**The rule for a first pilot: a step with any tick is an H or an X.**

**4. For every H and X, name the role** of the person, and say where the rule lives. A rule can
live in the system (the step cannot happen without the approval), in a procedure (people are
expected to check), or only in the agent's instructions (the agent is told to ask). On a ticked
step, "only in the instructions" is not a gate.

| # | The step | M | P | C | A, H or X | Who approves (a role) | Where the rule lives |
|---|---|:---:|:---:|:---:|:---:|---|---|
| 1 | | | | | | | |
| 2 | | | | | | | |
| 3 | | | | | | | |
| 4 | | | | | | | |
| 5 | | | | | | | |
| 6 | | | | | | | |
| 7 | | | | | | | |
| 8 | | | | | | | |

**Check before you put your pen down:**

- Every ticked step is an H or an X.
- At least one step is an X. If none is, look harder.
- No gate depends on the agent being told to ask.

**The gate people will ask to remove first:** ______________________________

**The evidence you would need before agreeing:** ______________________________

<div style="page-break-after: always;"></div>

---

## An example: the Ridgeline phone agent

The steps of one call, as the agent in this repo handles them.

| # | The step | M | P | C | Who decides | Where the rule lives |
|---|---|:---:|:---:|:---:|---|---|
| 1 | Answer a question from the handbook | | | yes | The agent, alone | In the instructions (state only facts it was given, and name the policy), checked by the 19 test calls |
| 2 | Check the class schedule | | | | The agent, alone | Nothing to guard. The step only reads |
| 3 | Look up the caller's membership | | yes | | The agent, alone, within a limit | In code. The lookup takes no input, so it can only return the record of the person who is calling |
| 4 | Book a class | yes | | yes | **The agent prepares, the caller approves** | In code. See below |
| 5 | Text a confirmation | | yes | yes | The agent, alone, within a limit | In code. It can only text the number on file for the caller |
| 6 | Refund or cancel a booking | yes | | yes | **A person only** | No such tool exists. The agent can only transfer the call |
| 7 | Anything about an injury | | | yes | **A person only**: the duty manager | In the instructions only, checked by one test call |
| 8 | Book a birthday party | yes | | yes | **A person only**: the events coordinator | The booking tool only books classes. The agent transfers the call |

### The booking that stopped

This is step 4 in the engineers' own run of the phone call.

1. The model asked to book Sam, aged 8, into Youth Climbing on Saturday at 10:00.
2. The code did not book. It answered `needs_confirmation`, with a summary of the booking and a
   one-time code.
3. The agent read the details back to the caller and asked: shall I book that for you?
4. The caller replied: "Yes please, book it."
5. The model asked again, this time with the code. Now the booking went through, and a
   confirmation text went to the number on file.

The code accepts the one-time code only after the caller has spoken again, and only for exactly
the details that were read back. The model cannot propose and confirm in one breath, however it
is instructed and however a caller tries to trick it.

### What the code says when the model gets it wrong

Remember Card A: "Yes! I've booked your child into Intro to Belay on Saturday at 2 pm." Suppose
the finished agent's model tried to make that booking. These are the replies of the booking code
in this repo. They come from code, not from a model, so they are the same every time.

| The model asks to | The code answers |
|---|---|
| Book an 8-year-old into Intro to Belay | `Intro to Belay is for ages 12+; Sam is 8.` |
| Confirm a booking in the same turn as the summary | `Not confirmed yet. Read the summary to the caller and wait for their answer.` |
| Use a tool that does not exist, such as a refund | `Unknown tool`, followed by the list of tools that do exist |

The code stops the wrong booking. It cannot stop a wrong sentence: a model could still say
"you're booked" when nothing was. That is what the test calls are for. The first of them is the
phone call itself, and any reply to it that says a booking is done fails.

### What to notice

**The model proposes. Code and people decide.** An agent is like a capable new hire with a
checklist and a limited set of keys. Ridgeline's agent has six keys. None of them opens refunds.

**Look at where each rule lives.** Steps 3 to 6 and step 8 are held by code or by a missing key.
Step 7 is held by a sentence. When version 2 of the instructions dropped that sentence, the agent
gave advice about an injured ankle (Block 3). The test caught it. The sentence did not.

**Ridgeline lets the agent do two ticked steps alone**, steps 1 and 5. That was earned: each is
limited in code or covered by the test calls, and there is a scoreboard to show for it. Your pilot
has no scoreboard yet. Start with a person on every ticked step. Remove a gate later, at a review,
when the evidence supports it.

### Where this comes from

| What | Source in this repo |
|---|---|
| The steps and their limits | [Lab 5](../../labs/05-tools/README.md#the-idea-in-two-minutes), and the code in `solution/gym_agent/tools.py` and `solution/gym_agent/guardrails.py` |
| The booking that stopped | The run printed in [Lab 5](../../labs/05-tools/README.md#run-it-for-real), on `gpt-5-mini`. The trace of its last step is `docs/img/langfuse-trace-tools.png` |
| The code's replies | The first two are returned by `book_class` in `solution/gym_agent/tools.py`, and the third by `validate_call` in `solution/gym_agent/guardrails.py`. The offline tests in `tests/test_lab5_tools.py` check all three refusals |
| The test call that fails "you're booked" | `ep1-belay-8yo` in `data/evals/agent_cases.jsonl` |
