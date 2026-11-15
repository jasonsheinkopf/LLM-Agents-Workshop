# FAQ: "What if…?"

Short answers to the questions that come up. Errors with exact fixes are in
[TROUBLESHOOTING.md](TROUBLESHOOTING.md); this page is for everything else.

## Before you start

**What if I've never used Python?**
This workshop is not the place to learn Python from zero. If you can read a function and change a
few lines, you'll be fine: every lab is a handful of short functions, and the answer is always in
`solution/`. If `def` and `return` are new to you, do a one-day Python intro first, then come back.

**What if I don't want to pay for OpenAI?**
You need about $2 of credit for the whole workshop; there is no free tier. Set a $5 monthly limit so
there is no risk of a surprise. If you truly can't use OpenAI, the code works with any
OpenAI-compatible endpoint: set `OPENAI_BASE_URL` (for example to a local Ollama server) and
`AGENT_MODEL`, `JUDGE_MODEL`, `EMBEDDING_MODEL` and `EMBEDDING_DIM` to match. Expect lower scores
from small local models; the workshop was built and verified on `gpt-5-mini`.

**What if I use Google sign-in for Langfuse or Pinecone?**
That's fine. Sign-in method doesn't matter; you still create an API key inside the project
(Langfuse: Settings → API Keys; Pinecone: API Keys in the sidebar) and paste it into `.env`.

**What if my company blocks these services?**
Langfuse can be self-hosted with Docker (`docker compose up` from their repo; the code doesn't
change). For OpenAI and Pinecone there is no workaround except a personal machine and personal
accounts, with the synthetic data in this repo. Never put company data into a personal account.

**What if I'm on Windows?**
Everything runs on Windows with PowerShell. Use `Copy-Item .env.example .env` instead of `cp`, and
`.venv\Scripts\activate` if you ever activate the environment by hand (you don't need to with
`uv run`). WSL also works and is closer to the workshop's terminal output.

**What if I'd rather use pip, conda, or Poetry?**
See the "Prefer pip?" note in [Lab 0](00-setup.md). Then drop `uv run` from every command. `uv` is
recommended only because it pins the exact library versions the workshop was tested with.

**What if I want the ideas, not the labs?**
Watch the [recordings](../README.md#recordings): the first half of each episode teaches the idea
without code. If you lead a team rather than build, the
[90-minute briefing](FACILITATOR.md#variant-executive-briefing-90-minutes-no-laptops) and the
[five questions to ask any agent team](../handouts/questions-for-leaders.md) are written for you.

## While you work

**What if I'm stuck on a lab?**
In this order: (1) run that lab's tests and read the *first* failure's message, which names the
function and what it expected; (2) `grep -n "TODO(labN)" workshop/` to see what's left;
(3) `diff workshop/gym_agent/<file>.py solution/gym_agent/<file>.py` to compare with the answer.
Copying the answer is allowed. Understanding it is the point; the tests only check that it works.

**What if the tests pass but the real run looks wrong?**
The tests use a fake model, so they can't catch a bad prompt or a bad model answer. For the real
run, open the trace in Langfuse (Lab 2) and read what the model was actually sent. Nine times out
of ten the fix is there.

**What if my scores are different from the README's?**
They will be. Language models aren't deterministic, and your prompt wording, judge and test cases
may differ. Compare runs against *each other*, not against the README. The shape should match: v2
regresses on honesty and safety, memory lifts knowledge, tools lift booking.

**What if the judge disagrees with the human grades?**
That's the lesson of Lab 3, not a bug. Below ~90% agreement, read the disagreements, tighten
`JUDGE_PROMPT` in `evaluators.py`, and re-run `calibrate_judge`. If it's still low, try a stronger
`JUDGE_MODEL`. Never trust experiment scores from a judge you haven't calibrated.

**What if the agent says something is booked but it isn't?**
Check the trace: did `book_class` return `booked`? If not, the model claimed success without the
tool confirming it. That is exactly the failure the v3 prompt forbids and the eval set catches.
Add the case to `agent_cases.jsonl` so it's tested forever.

**What if I want to use my own documents instead of the gym handbook?**
Replace `data/handbook.md` (keep `## ` headings: that's the chunk boundary), re-run
`memory ingest`, then rewrite `data/evals/retrieval_cases.jsonl` for your sections. The rest of the
code doesn't change. To change the business entirely, also replace `schedule.json`,
`callers.json`, the prompts and the eval cases; see [labs/07-ship-it](../labs/07-ship-it/).

**What if I want to use a different vector database?**
Implement the four-method `VectorStore` protocol in `memory.py` (`upsert`, `query`, `delete_prefix`,
plus a `connect`). `InMemoryStore` in the same file is a complete example in thirty lines.

**What if I want to use Claude, Gemini or Llama instead?**
The agent loop and tools use the OpenAI chat-completions format. Any provider with an
OpenAI-compatible endpoint works by setting `OPENAI_BASE_URL`. For native SDKs you'd rewrite
`llm.py` and `_model_call` in `agent.py`; the rest of the workshop (traces, evals, memory, guardrails,
MCP) is provider-neutral.

**What if a lab's "real run" costs more than I expected?**
It shouldn't: the whole workshop is under $2 on `gpt-5-mini`. Experiments are the most expensive step
(19 cases × a few calls each). Use `--limit 5` while iterating, and check Usage on
platform.openai.com. If a loop ever ran away, `AGENT_MAX_STEPS` (default 6) is the brake.

**What if I accidentally commit my `.env`?**
Revoke the keys immediately (all three services let you delete a key in one click), create new
ones, then remove the file from history (`git rm --cached .env`, commit, and if it was pushed,
treat the old keys as public forever). The repo's `.gitignore` excludes `.env` to make this hard
to do by accident.

**What if I want to run this for my team?**
[FACILITATOR.md](FACILITATOR.md) has a 90-minute executive briefing and a one-day engineer
workshop, with timings, checkpoints and the things that go wrong.

## Concepts

**What's the difference between a workflow and an agent?**
In a workflow, your code decides the steps and the model fills them in. In an agent, the model
decides the next step (which tool, or whether to answer). Use the simplest one that solves the
task; this workshop's agent needs the loop because a booking takes a variable number of steps.

**Why both traces and evals?**
Traces tell you *what happened* on one call. Evals tell you *how often it goes right* across many.
You need the first to understand a failure and the second to know whether a change helped.

**Why a confirmation code instead of just telling the model to confirm?**
Because "always confirm before booking" in a prompt works *most* of the time, and a booking is
not a most-of-the-time action. The code only accepts a confirmation on a later caller turn than the
summary, so the model can't propose and confirm in one breath, however it is prompted or tricked.

**Why does the agent cite handbook sections?**
So a caller (and you, reading the trace) can tell a fact from a guess. Grounded answers are also
what the judge checks against: the rubric lists facts that must be conveyed.

**Why MCP, if the agent already has tools?**
MCP is for the day your tools are used by an agent you didn't write: a desktop assistant, an IDE,
another team's bot. One server, any client, same guardrails.

**Is Ridgeline a real gym?**
No. The gym, its policies, its prices and its callers are invented for this workshop, and the phone
numbers use the reserved 555-01xx range.
