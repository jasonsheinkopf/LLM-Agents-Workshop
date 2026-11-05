# Ship it: the finale

📺 **Video:** [Agents Unpacked finale: The whole agent](https://youtube.com/@TODO)
⏱️ **Time:** 30 min · 🔑 **Needs:** all keys

You've built every piece. Now use them together, the way you would on a real team: one change,
measured end to end, and promoted only if it wins.

## 1. Check everything is green

```bash
repo $ uv run pytest                       # every lab passes on YOUR code now
workshop $ uv run python -m gym_agent.doctor
```

## 2. The full experiment

```bash
workshop $ uv run python -m gym_agent.evals.upload_dataset          # in case you added cases
workshop $ uv run python -m gym_agent.evals.run_experiment --label production --name "final: v3 + memory + tools"
```

In Langfuse, compare all your runs. Your scoreboard from Lab 3 should tell a clear story:

| Run | What changed | What it fixed |
|---|---|---|
| v1, bare model | careful but wordy instructions | (baseline) |
| v2 prompt | "be brief" | nothing: a **regression** the experiment caught |
| v3 prompt | brief *and* keeps the rules | wordiness, without losing honesty or safety |
| + memory | handbook RAG, caller memories | **knowledge** |
| + tools | schedule, booking, transfer + guardrails | **action** |
| + evals and traces | throughout | **quality**: you can *prove* each step helped |

That's Episode 1's three gaps, closed one by one, with numbers.

## 3. Make one improvement, the right way

Pick a failing case in your last run (there's usually one). Then:

1. **Read its trace.** Which step went wrong: retrieval, the prompt, a tool, or the model?
2. **Fix the right layer.** A retrieval miss isn't fixed by prompt wording. A missing rule isn't fixed by more context.
3. **If it's the prompt:** write `prompts/system_v4.md`, then `prompts push ... --label staging`.
4. **Run the experiment on staging**, then compare with production. Did your fix break anything else?
5. **Promote** only if it wins: `uv run python -m gym_agent.prompts promote <version>`.

## 4. The production checklist

What this workshop covered, and what you'd add before real customers call:

| Area | In this repo | Before production |
|---|---|---|
| Observability | Every turn, retrieval and tool call traced; sessions; user feedback scores | Alerts on error rate, latency and cost; PII masking in traces (Langfuse supports masking functions) |
| Evals | 19 cases, code checks, a calibrated judge, experiments | Hundreds of cases grown from production traces; run in CI on every prompt or code change; online evaluators scoring live traffic |
| Prompts | Versioned, labelled, fetched at runtime with a fallback | Review process for promotions; rollback runbook (it's one `promote` command) |
| Memory | Handbook RAG; per-caller memories with a filter | Re-ingest when the handbook changes; retention and deletion policy for memories; access logs |
| Tools | Allow-list, Pydantic validation, least privilege, two-step confirmation, step limit | Rate limits; idempotency keys on writes; audit log; human approval for high-risk actions |
| Security | Tool results as data; no high-risk tools exposed | Red-team test set for prompt injection; auth on the MCP server; secrets in a vault, not `.env` |

## 5. Share what you built

- Record a 60-second demo: the call from Episode 1, then the Langfuse trace, then the experiment comparison.
- Swap Ridgeline for something you know (a dentist's office, an IT help desk, your own product's docs). Change `data/`, rewrite the eval cases, and the rest of the code stays the same.
- Open a PR or an issue on this repo if something in the course could be clearer.

Congratulations. You didn't just call an LLM: you built, measured and shipped an agent. 🎉
