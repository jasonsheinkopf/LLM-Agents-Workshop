# Lab 3: Evals

**Block 3** · In the room: 15 min explain and demo, 50 min build, 10 min debrief · On your own: about 60 min
**Cost:** about $0.10 to $0.30 · **Needs:** `OPENAI_API_KEY`, `LANGFUSE_*` · **Recording:** *Agents Unpacked*, Episode 3 ([where to find it](../../README.md#recordings))

## Goal

Stop judging the agent on vibes. Move the prompt into Langfuse with versions and labels, build a
test set, grade answers with code checks and an LLM-as-a-judge (after checking the judge against
human labels), and run an **experiment** that compares two prompt versions on the same test set.

You'll also record a **baseline**: the agent's score before memory and tools. In Labs 4 and 5 you
re-run the same experiment and watch the numbers move. That's eval-driven development.

**The failure to look for:** prompt v2 feels better in chat. Then run the experiment on it.

**By the end of this lab you can:**
- version prompts and deploy them by **label** (`production`, `staging`) with no code change;
- design test cases with *expected behaviour*, not exact expected strings;
- combine **deterministic checks** with an **LLM-as-a-judge**, and **calibrate** the judge;
- run, compare and promote with experiments.

## Checkpoint

| | You're there when |
|---|---|
| **Floor** (every pair, before the debrief) | v1 and v2 are pushed, the test set is uploaded, both experiments have run, and you can say which prompt you would ship and why |
| **Target** (most pairs) | The Lab 3 tests are green with your own graders, the judge is calibrated, v3 is run and promoted, and three rows of your scoreboard are filled in |
| **Ceiling** (if you finish early) | The tasks under [Ceiling](#ceiling-if-you-finish-early), below |

> **Short on time?** If your graders aren't passing 25 minutes into the build, copy `solution/gym_agent/evals/evaluators.py` over yours and run the experiments. Seeing the comparison matters more than finishing the grader code.

## The idea in two minutes

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

Read the three files in `prompts/`:

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
in chat, then ask the phone-call question. v2 *feels* better: it's snappier. Hold that thought.

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
`honesty`, `safety`, `handoff` and `guardrail`. The first one is the phone call from Block 1. Then upload:

```bash
workshop $ uv run python -m gym_agent.evals.upload_dataset
Uploaded 19 items to Langfuse dataset 'ridgeline-agent-cases'.
```

Find it under **Datasets**. Each item has an `input` (caller and turns) and an `expected_output`.

<img src="../../docs/img/langfuse-dataset.png" alt="The ridgeline-agent-cases dataset in Langfuse: items with input, expected output and category" width="760">

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
  booking    1/6 passed
  honesty    2/2 passed
  knowledge  0/8 passed
  safety     1/1 passed
  avg_judge_pass = 0.263     ← our run on gpt-5-mini; yours will be close, not identical
```

### Step 8: Run the candidate (v2, staging), then compare

```bash
workshop $ uv run python -m gym_agent.evals.run_experiment --label staging
```

In Langfuse: **Experiments** (or the dataset's **Experiments** tab). Tick the runs and press **Compare**.

<img src="../../docs/img/langfuse-experiment-compare.png" alt="Langfuse experiment comparison: summary scores per run with deltas against a baseline, then per-case scores" width="760">

*The comparison view: a summary row of scores per run, with the change against the baseline, then every
case side by side. This one is the end-of-day comparison from our `gpt-5-mini` run.* Open
the cases where they differ; each one links to its trace.

What you'll see: v2 is shorter, and it **regresses**. In our run, honesty went from 2/2 to 0/2 and
safety from 1/1 to 0/1: with the rules gone, it invents a wifi password and gives ankle advice.
Chatting with it missed this regression, and the experiment catches it in one run.

### Step 9: Fix it with v3, then promote the winner

```bash
workshop $ uv run python -m gym_agent.prompts push ../prompts/system_v3.md --label staging
Pushed ../prompts/system_v3.md as front-desk v3 with label 'staging'.
workshop $ uv run python -m gym_agent.evals.run_experiment --label staging
```

Compare all three runs. In our run, v3 matched v1 on every check (honesty 2/2, safety 1/1, judge
pass 0.26) at half the length. That is the win: the brevity callers asked for, without the
regression. Promote it:

```bash
workshop $ uv run python -m gym_agent.prompts promote 3
Label 'production' now points at front-desk v3.
```

Notice what **none** of them can fix: most **knowledge** and **booking** cases still fail, because
the agent has no handbook and no tools. The test set has just shown you, in numbers, that the next
problem isn't the prompt.

The running agent picks it up within the cache TTL, with no deploy. That's the loop:
**trace → test set → experiment → promote**.

### Step 10: Write down your baseline

Fill in this scoreboard, because you'll come back to it:

| Run | avg_judge_pass | knowledge | booking | honesty + safety | *(our run)* |
|---|---|---|---|---|---|
| Lab 3: v1 (no memory, no tools) | | | | | 0.26 · 0/8 · 1/6 · 3/3 |
| Lab 3: v2 (no memory, no tools) | | | | | 0.21 · 1/8 · 2/6 · 0/3 |
| Lab 3: v3 (no memory, no tools) | | | | | 0.26 · 0/8 · 1/6 · 3/3 |
| Lab 4: v3 + memory | | | | | 0.84 · 8/8 · 3/6 · 3/3 |
| Lab 5: v3 + memory + tools | | | | | 0.90 · 8/8 · 5/6 · 3/3 |

## What you should notice

- Two prompts that *feel* the same in chat can score very differently. Vibes don't scale to 19 cases, let alone 1,800.
- The judge is part of your system, so measure it like one.
- Good evals tell you **what kind** of problem you have. Here: knowledge and action, not wording.

## Debrief

Answer these with your pair before you move on. In a room, the instructor asks pairs for their answers. On your own, write yours down.

1. Which prompt did you prefer in chat, and which one won the experiment?
2. Why did v2 lose? What did "be brief" take out?
3. Before the next prompt change you ship anywhere, what will you run first?

## Make it yours

On your [workflow canvas](../../handouts/workflow-canvas.md), start **five test cases**. Write four now: three ordinary requests, and one where the right answer is "I don't know". For each, write what a good answer must do and must not do. You add the fifth, a hostile one, after the red-team round.

## Ceiling: if you finish early

- Write `prompts/system_v4.md` yourself, then push it with `--label staging`, run it and compare. Can you beat v3 without breaking anything?
- Add a case from your own `/bad` traces to `agent_cases.jsonl` and re-upload. (Same id = update, so it's safe to re-run.)
- Break the judge on purpose: delete "Grade strictly" from `JUDGE_PROMPT` and re-calibrate. What gets through?
- Try `--prompt-file ../prompts/system_v1.md --local` to test a prompt file before you push it.

## Stuck?

**Common failures in this lab:**
- `test_prompt_is_fetched_by_label_from_langfuse` fails: call `get_prompt` with `label=` and `fallback=`, and keep the returned object in `langfuse_prompt`.
- `test_judge_parses_verdict` fails: pass `response_format={"type": "json_object"}` and read `.choices[0].message.content`.
- `test_judge_survives_garbage` fails: wrap `json.loads` in `try/except json.JSONDecodeError` and treat failure as `{}`.
- The experiment runs but every item errors: open one trace; it's usually a missing key or a 429 rate limit (see Troubleshooting).

`diff workshop/gym_agent/evals/evaluators.py solution/gym_agent/evals/evaluators.py` ·
[TROUBLESHOOTING.md](../../docs/TROUBLESHOOTING.md#evals)

**Out of time for this lab?** `repo $ uv run python scripts/catch_up.py 4` gives you working Lab 3 code, so you start the next block with the room. Your own files are backed up first.

**Next:** [Lab 4: Memory →](../04-memory/)
