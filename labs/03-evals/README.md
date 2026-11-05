# Lab 3: Evals

📺 **Video:** [Agents Unpacked, Episode 3: Evals, how do you know it works?](https://youtube.com/@TODO)
⏱️ **Time:** 60 min · 💳 **Cost:** about $0.10 to $0.30 · 🔑 **Needs:** `OPENAI_API_KEY`, `LANGFUSE_*`

## Goal

Stop judging the agent on vibes. Move the prompt into Langfuse with versions and labels, build a
test set, grade answers with code checks and an LLM-as-a-judge (after checking the judge against
human labels), and run an **experiment** that compares two prompt versions on the same test set.

You'll also record a **baseline**: the agent's score before memory and tools. In Labs 4 and 5 you
re-run the same experiment and watch the numbers move. That's eval-driven development.

**By the end of this lab you can:**
- version prompts and deploy them by **label** (`production`, `staging`) with no code change;
- design test cases with *expected behaviour*, not exact expected strings;
- combine **deterministic checks** with an **LLM-as-a-judge**, and **calibrate** the judge;
- run, compare and promote with experiments.

## Concepts

```
 test set (dataset)        ×      prompt version      →    agent runs every case    →    graders     →   scores per run
 19 caller scenarios              v1 (production)          (traced)                     code + judge      compare v1, v2, v3
 with expected behaviour          v2, v3 (staging)                                                        promote the winner
```

- **Test case:** the caller's turns, plus what a good answer *must* convey (`facts`), *must not* do
  (`must_not`), which tool it should use, and whether it should end in a booking. See
  `data/evals/agent_cases.jsonl`.
- **Code checks** are free, fast and exact: did it book when it shouldn't have? Did it call the schedule tool?
- **LLM-as-a-judge** handles what code can't: "did the reply convey that the waiver must be signed
  by a guardian?" It's a second model call with a rubric.
- **Calibration:** a judge is a model too, and it can be wrong. Before you trust it, grade a few
  answers yourself and measure how often the judge agrees.

## Part A: Version the prompt in Langfuse

### Step 1: Push the first two prompt versions

This is the story from the video. Read the three files in `prompts/`:

| Version | What it is |
|---|---|
| `system_v1.md` | Careful rules, but **wordy**: "explain the relevant policies in full". Callers complain it takes forever. |
| `system_v2.md` | The quick fix: "be brief, one or two sentences". It's much shorter, and it quietly drops the rules. |
| `system_v3.md` | Brief **and** keeps the rules: grounding, the age policy, confirming bookings, safety. |

Push v1 as `production` and v2 as `staging`. (v3 comes in Step 9.)

```bash
workshop $ uv run python -m gym_agent.prompts push ../prompts/system_v1.md --label production
Pushed ../prompts/system_v1.md as front-desk v1 with label 'production'.
workshop $ uv run python -m gym_agent.prompts push ../prompts/system_v2.md --label staging
Pushed ../prompts/system_v2.md as front-desk v2 with label 'staging'.
```

In Langfuse, open **Prompts → front-desk**. There are two versions, and a label on each.

<img src="../../docs/img/langfuse-prompts.png" alt="Langfuse Prompts: front-desk with versions 1 to 3 and their labels" width="760">

*(This screenshot is from the end of the lab, after v3 is promoted.)* Try both
in chat, then ask the Episode 1 question. v2 *feels* better: it's snappier. Hold that thought.

### Step 2: Fetch by label: `workshop/gym_agent/prompts.py`

Complete `load_system_prompt`. When Langfuse is on, fetch the prompt that carries a label, with a
local **fallback** so the phone keeps working if Langfuse is down:

```python
from langfuse import get_client

prompt = get_client().get_prompt(
    SETTINGS.prompt_name,
    label=label or SETTINGS.prompt_label,           # "production" by default
    fallback=DEFAULT_PROMPT_FILE.read_text().strip(),
    cache_ttl_seconds=60,                           # cached in-process; refreshed in the background
)
version = "fallback" if prompt.is_fallback else f"langfuse:v{prompt.version}"
return SystemPrompt(text=prompt.compile(), version=version, langfuse_prompt=prompt)
```

### Step 3: Link traces to prompt versions: `workshop/gym_agent/agent.py`

In `_model_call`, complete the `TODO(lab3)`: pass `langfuse_prompt=self.agent.prompt.langfuse_prompt`
to the model call (only when Langfuse is enabled and the prompt came from Langfuse). Now every
generation shows which prompt version produced it, and Langfuse charts quality per version.

```bash
workshop $ uv run python -m gym_agent.chat                         # banner: prompt: langfuse:v1
workshop $ uv run python -m gym_agent.chat --prompt-label staging  # banner: prompt: langfuse:v2
```

## Part B: The test set and the graders

### Step 4: Upload the test set

Open `data/evals/agent_cases.jsonl`. There are 19 cases in six categories: `booking`, `knowledge`,
`honesty`, `safety`, `handoff` and `guardrail`. The first one is the call from the videos. Then upload:

```bash
workshop $ uv run python -m gym_agent.evals.upload_dataset
Uploaded 19 items to Langfuse dataset 'ridgeline-agent-cases'.
```

Find it under **Datasets**. Each item has an `input` (caller and turns) and an `expected_output`.

### Step 5: Write the graders: `workshop/gym_agent/evals/evaluators.py`

`booking_policy` is done for you as an example. Write:

1. **`tool_use`**, a code check. If the case expects a tool, pass only if the agent called it.
2. **`judge_reply`**, the LLM-as-a-judge. The rubric (`JUDGE_PROMPT`) is written for you. Make the
   call with `response_format={"type": "json_object"}`, parse the JSON, and make sure a garbled
   reply counts as a **fail**, not a crash.

```bash
repo $ uv run pytest tests/test_lab3_evals.py
```

### Step 6: Calibrate the judge before you trust it

`data/evals/judge_calibration.jsonl` has 12 replies a person has already graded. Some are
subtle, such as the right fact in different words, or a correct answer that also slips in medical advice.

```bash
workshop $ uv run python -m gym_agent.evals.calibrate_judge        # example output
agree     cal-01  human=pass judge=pass  (States the $24 adult price.)
...
Agreement with humans: 12/12 = 100%
```

Below about 90%, or any **too lenient** misses, means you fix the rubric before you go on. A lenient
judge lets bad prompts through. That's worse than a strict one.

## Part C: Experiments

### Step 7: Run the baseline (v1, production)

```bash
workshop $ uv run python -m gym_agent.evals.run_experiment --label production
```

Every case runs through your agent (traced), then gets graded. You'll get a table, plus a link:

```
  booking    0/4 passed
  handoff    0/1 passed
  knowledge  1/7 passed
  ...
  avg_judge_pass = 0.17     ← your numbers will differ
```

### Step 8: Run the candidate (v2, staging), then compare

```bash
workshop $ uv run python -m gym_agent.evals.run_experiment --label staging
```

In Langfuse: **Datasets → ridgeline-agent-cases → Runs**. Select both runs and **compare**. Open
the cases where they differ; each one links to its trace.

What you'll likely see: v2 is shorter, and it **regresses**. With the rules gone, it guesses: it
invents a wifi password, gives ankle advice, and forgets to say which age rule applies. This is the
regression from the video that vibe-testing missed, and the experiment catches it in one run.

### Step 9: Fix it with v3, then promote the winner

```bash
workshop $ uv run python -m gym_agent.prompts push ../prompts/system_v3.md --label staging
Pushed ../prompts/system_v3.md as front-desk v3 with label 'staging'.
workshop $ uv run python -m gym_agent.evals.run_experiment --label staging
```

Compare all three runs. v3 should match or beat v1 on **honesty** and **safety**, while staying
short. Then promote it:

```bash
workshop $ uv run python -m gym_agent.prompts promote 3
Label 'production' now points at front-desk v3.
```

Notice what **none** of them can fix: most **knowledge** and **booking** cases still fail, because
the agent has no handbook and no tools. The test set has just shown you, in numbers, that the next
problem isn't the prompt.

The running agent picks it up within the cache TTL, with no deploy. That's the loop from the video:
**trace → test set → experiment → promote**.

### Step 10: Write down your baseline

Fill in this scoreboard, because you'll come back to it:

| Run | avg_judge_pass | knowledge | booking | honesty + safety |
|---|---|---|---|---|
| Lab 3: v1 (no memory, no tools) | | | | |
| Lab 3: v2 (no memory, no tools) | | | | |
| Lab 3: v3 (no memory, no tools) | | | | |
| Lab 4: v3 + memory | | | | |
| Lab 5: v3 + memory + tools | | | | |

## What you should notice

- Two prompts that *feel* the same in chat can score very differently. Vibes don't scale to 19 cases, let alone 1,800.
- The judge is part of your system, so measure it like one.
- Good evals tell you **what kind** of problem you have. Here: knowledge and action, not wording.

## Stretch goals

- Write `prompts/system_v4.md` yourself, then push it with `--label staging`, run it and compare. Can you beat v3 without breaking anything?
- Add a case from your own `/bad` traces to `agent_cases.jsonl` and re-upload. (Same id = update, so it's safe to re-run.)
- Break the judge on purpose: delete "Grade strictly" from `JUDGE_PROMPT` and re-calibrate. What gets through?
- Try `--prompt-file ../prompts/system_v1.md --local` to test a prompt file before you push it.

## Stuck?

`diff workshop/gym_agent/evals/evaluators.py solution/gym_agent/evals/evaluators.py` ·
[TROUBLESHOOTING.md](../../docs/TROUBLESHOOTING.md#evals)

**Next:** [Lab 4: Memory →](../04-memory/)
