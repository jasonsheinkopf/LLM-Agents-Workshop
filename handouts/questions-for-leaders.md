# Five questions to ask any team building an agent

The handout for the [90-minute leaders' briefing](../docs/FACILITATOR.md#variant-executive-briefing-90-minutes-no-laptops).
A good answer to each one is evidence. A demo is not.

1. **Show me a trace of a wrong answer.** What went wrong, and how do you know?
2. **What is in your test set**, and where did it come from?
3. **Who grades the answers**, and how do you know the grader is right?
4. **What can the agent do without a human confirming**, and what stops it doing more?
5. **When you change the prompt, what tells you it got better?**

## What good and bad answers sound like

| Question | A good answer | A warning sign |
|---|---|---|
| 1 | They open a trace and point at the step that failed: the prompt, the retrieved pages, a tool result, or the model | "The model hallucinated" |
| 2 | Real cases, many of them from past failures, including ones where the right answer is "I don't know" | A handful of examples the team wrote in an afternoon |
| 3 | Code checks where possible, and a model judge that was checked against human grades first | "We look at the outputs" |
| 4 | A short list of allowed actions, validated in code, with confirmation on anything that matters | "We told it in the prompt not to" |
| 5 | An experiment: the same test set, before and after, compared | "It felt better when we tried it" |

## Before you approve a pilot

- Name one workflow, and what a good outcome looks like in a number.
- Name what you will **not** automate in it.
- Name the owner.
- Ask for the answers to the five questions in 30 days.
