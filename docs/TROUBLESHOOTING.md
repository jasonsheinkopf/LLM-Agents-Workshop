# Troubleshooting

Start with the doctor. It tests every key against the real service and prints the real error:

```bash
cd workshop && uv run python -m gym_agent.doctor
```

## Setup

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'gym_agent'` | You're in the wrong folder. App commands run **inside** `workshop/` (or `solution/`); tests run from the **repo root**. |
| `Missing OPENAI_API_KEY in …/.env` | Run `cp .env.example .env` in the repo root and fill it in. The `.env` file lives in the repo root, not in `workshop/`. |
| `uv: command not found` | Open a new terminal after installing uv, or follow the PATH hint the installer printed. |
| `uv sync` picks the wrong Python | `uv python install 3.12`, then `uv sync` again. The repo pins 3.12 in `.python-version`. |
| Tests say `NotImplementedError: Lab N: …` | That's expected: it's a `TODO(labN)` you haven't written yet. Run only the labs you've done: `uv run pytest tests/test_lab1_agent.py`. |

## OpenAI

| Symptom | Fix |
|---|---|
| `401 Incorrect API key` | The key was copied with a space or quote. Keys look like `sk-...`, with no quotes in `.env`. |
| `429 insufficient_quota` | Add billing at platform.openai.com → Settings → Billing. A ChatGPT subscription doesn't cover API usage. |
| `404 model not found` / `does not have access to model` | Set `AGENT_MODEL` and `JUDGE_MODEL` in `.env` to a model your account lists, then re-run the doctor. |
| `Unsupported parameter: 'temperature'` | Some reasoning models only allow the default temperature. This repo never sets it. If you added it, remove it, or use a model that supports it. |
| Embedding dimension mismatch | If you change `EMBEDDING_MODEL`, set `EMBEDDING_DIM` to match, and use a new `PINECONE_INDEX` name. An index's dimension can't change. |

## Langfuse

| Symptom | Fix |
|---|---|
| Doctor: `keys rejected` | Nine times out of ten it's the region. EU projects use `https://cloud.langfuse.com`, US projects use `https://us.cloud.langfuse.com`. Set `LANGFUSE_BASE_URL`. |
| Chat banner says `tracing: off` | One of `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` is empty, or `LANGFUSE_TRACING_ENABLED=false` is set. |
| No traces show up | They're sent in batches in the background. End the chat with `/end` (which flushes) rather than Ctrl-C, then refresh after a few seconds. |
| Each model call is a separate trace | `Call.send` isn't decorated with `@observe(...)` (Lab 2, step 2). |
| Traces aren't grouped into a session | `propagate_attributes(session_id=...)` must wrap the body of `send`, before the model call. |
| `get_prompt` returns the fallback | The prompt name or label doesn't exist yet. Run `prompts push … --label production` (Lab 3, step 1). The banner shows `prompt: fallback` when this happens. |
| Generations don't show the prompt version | Pass `langfuse_prompt=` in `_model_call` (Lab 3, step 3), and make sure the prompt came from Langfuse, not a file. |

## Evals

| Symptom | Fix |
|---|---|
| `Dataset not found` | Run `uv run python -m gym_agent.evals.upload_dataset` first, or use `--local`. |
| Every case fails on `judge_pass` | Run `calibrate_judge`. If it passes there, open a failing trace and read the judge's `comment`. It's usually right. |
| Scores change between identical runs | LLMs aren't deterministic. Compare averages over the whole set, re-run close calls, and grow the test set. That's normal, and part of the lesson. |
| Rate limit errors during experiments | Lower `max_concurrency` in `run_experiment.py` (it's 4), or try `--limit 5` first. |

## Pinecone

| Symptom | Fix |
|---|---|
| `Pinecone index 'ridgeline-agent' doesn't exist yet` | Run `uv run python -m gym_agent.memory ingest`. It creates the index. |
| Chat banner says `memory: off` | The index doesn't exist yet (run `ingest`), or `PINECONE_API_KEY` is empty. |
| Search returns nothing right after ingest | Serverless indexes are eventually consistent. Wait 10 to 30 seconds. |
| Region or plan error creating the index | The free Starter plan supports `aws` / `us-east-1` (the default). Check `PINECONE_CLOUD` and `PINECONE_REGION` in `.env`. |
| You remember the wrong thing about a caller | `uv run python -m gym_agent.memory forget dana`, then check `recall` still uses the `caller_id` filter. |

## Tools

| Symptom | Fix |
|---|---|
| The agent never calls tools | `tool_specs` still returns `[]`, or `_model_call` doesn't pass `tools=` (Lab 5, steps 1 and 4). The banner lists the tools. |
| `400 … 'tool' messages must be a response to a preceding message with 'tool_calls'` | Append the assistant message (with its `tool_calls`) to history **before** the tool results, and give each result the matching `tool_call_id`. |
| It says "booked!" but nothing is in `.runtime/bookings.json` | The model claimed success without a `booked` tool result. Check the trace. The v3 prompt forbids this. Add a case to the eval set if you see it. |
| `Not confirmed yet` on a booking you said yes to | The "yes" must be a *new* caller message, after the summary. That's the guardrail working. |
| Seats left look wrong | Delete `.runtime/bookings.json` to reset to the schedule's starting counts. |

## MCP

| Symptom | Fix |
|---|---|
| `No module named 'mcp.server.fastmcp'` | You're following an MCP SDK 1.x tutorial. In 2.x: `from mcp.server.mcpserver import MCPServer`. |
| Claude Desktop shows no tools | Use an **absolute** path in `--directory`, and the full path to `uv` if needed. Restart the app, and check its MCP logs. |
| The server prints garbage, or the client hangs | Nothing may `print()` to stdout in a stdio server, because stdout *is* the protocol. Log to stderr instead. |
| `search_handbook` says it isn't available | The server only enables it once the Pinecone index exists and both keys are set. |

Still stuck? [Open an issue](https://github.com/jasonsheinkopf/LLM-Agents-Workshop/issues) with the
command you ran, the full error, and the doctor's output (it never prints your keys).
