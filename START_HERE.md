# Start here — your guided AI agents workshop

**Want to learn by doing? This is the course's front door.** Clone the repository, read one short concept lesson, build its corresponding lab, check your work, and follow the **Next** link. Repeat until you have a tested agent and a plan to apply it at work.

You **do not need the planned video series**: the written lessons adapt its teaching content and the existing labs contain runnable exercises, examples, tests, and debriefs.

**Prerequisites:** You can read and edit Python, use a terminal, and have seen an LLM API call. This is not a no-code workshop. **Time:** roughly 5–7 hours of hands-on learning, depending on experience, plus setup. Optional challenges take longer.

## Step 1 — Clone the repo onto your computer

You'll change files in `workshop/` as you learn, so **clone the project rather than just reading it on GitHub**:

```bash
git clone https://github.com/jasonsheinkopf/LLM-Agents-Workshop.git
cd LLM-Agents-Workshop
```

Where things live:

| Folder | Your job |
|---|---|
| `lessons/` | **Read first**: explanation, diagrams, examples, and questions (no video required) |
| `labs/` and `workshop/` | **Build next**: follow the numbered lab instructions and edit `TODO(labN)` functions |
| `tests/` | Check completion without live API costs |
| `solution/` | Look up a finished reference implementation **when stuck**, not before trying |

This is a fictional gym with a simulated telephone conversation in terminal chat. A booking writes a local file; text messages are simulated. The hands-on exercises use real OpenAI, Langfuse and Pinecone APIs when configured.

## Step 2 — Check off your progress

Your clone already includes [PROGRESS.md](PROGRESS.md). Open **that file directly** in any text editor. As you finish each lesson and lab, change `- [ ]` to `- [x]` and save. **That's all.** No copying, account, app, or progress service is required.

Because `PROGRESS.md` is tracked like any other file, Git will show your edits as a local modification. They stay on your computer unless **you decide** to commit and push them; no progress is transmitted automatically.

## Step 3 — Set up once

Follow [Lab 0: Setup](docs/00-setup.md). Install dependencies, configure the keys you need, and run the doctor. Lab 1 only needs OpenAI; later labs introduce Langfuse and Pinecone.

**Checkpoint:** the connection tests you configured report PASS. Never commit your `.env` file or real credentials.

## Step 4 — Follow the course in this order

Every module works the same way: **read the lesson → do the lab in your clone → run the checkpoint → answer the debrief → click Next**.

| # | Read the concept | Build and test it |
|---|---|---|
| 1 | [What makes an agent?](lessons/01-first-agent/README.md) | [Lab 1 — First agent](labs/01-first-agent/README.md) |
| 2 | [Traces: see what happened](lessons/02-traces/README.md) | [Lab 2 — Traces](labs/02-traces/README.md) |
| 3 | [Evals: measure a change](lessons/03-evals/README.md) | [Lab 3 — Evals](labs/03-evals/README.md) |
| 4 | [Memory, embeddings and RAG](lessons/04-memory/README.md) | [Lab 4 — Memory](labs/04-memory/README.md) |
| 5 | [Tool calling, loops and guardrails](lessons/05-tools/README.md) | [Lab 5 — Tools and red-team](labs/05-tools/README.md) |
| 6 | [MCP: share your guarded tools](lessons/06-mcp/README.md) | [Lab 6 — MCP](labs/06-mcp/README.md) |
| 7 | [Transfer it to your own work](lessons/07-transfer/README.md) | [Lab 7 — Make it yours](labs/07-ship-it/README.md) |

**Your next click:** [Lab 0 — Setup](docs/00-setup.md). At the end of Lab 0, continue to Lesson 1.

## What if I get stuck?

Try the lab's **Stuck?** section, [troubleshooting guide](docs/TROUBLESHOOTING.md), and offline tests. Compare the relevant `workshop/` function with `solution/`. For time-sensitive workshops, each lab gives a `scripts/catch_up.py` checkpoint that saves your current work and lets you rejoin the next block.

**Don't skip the debrief.** Passing tests demonstrates that code works; explaining a failure and adapting to a changed requirement helps establish that you understand it.

## Other routes

- **I'm teaching a class:** [Facilitator guide](docs/FACILITATOR.md)
- **I want to understand the instructional design:** [Design rationale](docs/DESIGN.md)

The six video companions are planned but not yet published. **The written lessons and labs are the complete path today.**
