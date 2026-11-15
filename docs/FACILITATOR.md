# Facilitator guide

The run of show for the instructor. Read it once end to end, then keep
[the day on one page](#the-day-on-one-page) open while you teach. The reasoning behind the design
is in [DESIGN.md](DESIGN.md).

**The spine, if you remember nothing else:** start with the learner and the outcome, teach only
enough to act, get them building early, make failure visible, measure what they built, and finish
with an owner and a next step.

## The outcomes you are teaching to

By 5:00, every pair can do these five things. If you have to cut something on the day, cut what
does not serve one of them.

| | Outcome | The evidence you look for |
|---|---|---|
| 1 | **Build** an agent that answers from a handbook and books only after the caller confirms | Lab tests green on their own code; one live booking |
| 2 | **Diagnose** a wrong answer from its trace, and name the layer that failed | Each person opens a bad trace of their own and says what was missing |
| 3 | **Measure** a change before shipping it | A scoreboard: a regression caught, a better prompt promoted |
| 4 | **Guard** the actions that matter in code | One guardrail that held under attack; one failure turned into a test case |
| 5 | **Transfer** the pattern to their own work | A workflow canvas with five test cases, an owner and a next step |

**Target for the room:** at 5:00, at least four pairs in five have green tests through Lab 5 and a
filled-in scoreboard, and every pair hands in a canvas with an owner.

## One week before

**The sponsor.** Find the person on the client side who owns the outcome. Ask two things: which
workflows matter to this team, and what happens to the best prototypes afterward. Without a
sponsor, the prototypes stay demos.

**Pre-work.** Send the [pre-work email](../handouts/pre-work-email.md). It asks each participant to
set up their laptop and send you the doctor output, to bring one workflow from their own job, and
to answer three questions you use for pairing. Chase the doctor output two days before. Every
laptop you fix in advance is ten minutes of the day you keep.

### The data rule

Agree it with the sponsor before the day, and say it out loud at 9:00.

- **Green:** public, synthetic, or made up for the workshop. Everything in `data/` is green.
- **Yellow:** internal, non-sensitive data the sponsor has approved for the workshop.
- **Red:** customer personal information, health data, credentials, legal or unreleased financial
  material. Never in the workshop unless the client's security team has signed off, and never
  into a third-party service without it.

**Pairs.** Use the pre-work answers. Pair a stronger coder with someone who knows the business
process, not strongest with strongest. Write the pairs on the board before people arrive.

**Staffing.** One instructor can circulate around about 16 builders. From 17 to 24, add a teaching
assistant whose job is to unblock single laptops so you never stop the room for one person. If the
client's laptops have single sign-on, proxies or blocked installs, bring someone who can fix
accounts and nothing else.

**Your own preparation.** The day before:

| Have ready | Why |
|---|---|
| The solution running on your laptop with real keys, and a Langfuse project from a full run | Your demos, and something to show if a participant's run is slow |
| Screenshots of each demo's end state, from that full run | The backup when a live demo will not recover |
| A spare OpenAI key with credit | Someone's key will fail or hit a limit |
| `uv run pytest --impl solution` green on the room's network | Proves the install works behind their firewall |
| The catch-up command tried once: `uv run python scripts/catch_up.py 3` | You will use it before 11:00 |
| Printed [canvases](../handouts/workflow-canvas.md) and [exit tickets](../handouts/exit-ticket.md), one per pair and per person | The network cannot break paper |

## The day on one page

| Time | Block | Explain and demo | Build | Debrief | Checkpoint: the floor every pair reaches |
|---|---|---:|---:|---:|---|
| 9:00 | Arrive and check | | | | Three PASS lines on every laptop; everyone knows their pair |
| 9:15 | 1. First agent | 10 | 25 | 10 | Lab 1 tests green; they have watched the bare model fail to book |
| 10:00 | 2. Traces | 10 | 25 | 10 | Each person has one of their own traces open and can say what is missing from it |
| 10:45 | Break | | | | |
| 11:00 | 3. Evals | 15 | 50 | 10 | Baseline and v2 experiments run; the room votes which to ship |
| 12:15 | Lunch | | | | |
| 1:15 | 4. Memory | 15 | 50 | 10 | The handbook is in Pinecone; the knowledge score moved in their re-run |
| 2:30 | Break | | | | |
| 2:45 | 5. Tools | 15 | 40 | | One live booking through the two-step confirmation |
| 3:40 | Red-team round | | 15 | 5 | Five hostile inputs tried; one guardrail that held, named by file |
| 4:00 | 6. MCP | 5 | 12 | 3 | The Python client lists their three tools |
| 4:20 | Make it yours | | 25 | | A finished canvas with an owner |
| 4:45 | Demos, exit ticket, close | | | 15 | Three demos; every exit ticket and canvas collected |

Minutes of working time: 70 explaining and demonstrating, 242 building, 78 checking and debriefing.

## How every block runs

**Explain (5 to 15 minutes).** One idea, and the problem it solves, starting from the phone call.
Each lab README has an "idea in two minutes" section with what to say and draw. If you catch
yourself past 15 minutes, stop and start the build.

**Demo (inside the same time).** Do the first step of the lab live on the projector, thinking out
loud, in the same repo the room has. Then show the planned failure for the block (listed below).
If a live demo breaks in a way you did not plan, narrate the diagnosis: read the error, open the
trace, form a guess, try a fix. If it is not fixed in two minutes, show the saved trace or screenshot from your own full run and
move on.

**Build.** Pairs work. You circulate. Three rules:

- Tests are the checkpoint. Don't ask "is everyone done?" Ask "whose Lab 3 tests are green?" and
  send the greens to help the reds.
- When a pair is stuck, open `solution/` with them and diff. The answer is always there, so being
  stuck never blocks them for long.
- Five minutes before the build ends, protect the floor. Any pair not there gets the shortcut
  listed for that block. Nobody starts the next block behind.

**Debrief.** Three questions, on the lab page: what happened, why, and what will you do
differently? Take answers from pairs, not volunteers. Then give two minutes for the row of the
canvas that goes with the block.

## Block by block

### 9:00 Arrive and check (15 minutes)

- Everyone runs `uv run python -m gym_agent.doctor` from `workshop/`. Pair reds with greens.
- Say the outcome for the day in one sentence, and play or read the phone call.
- Say the data rule.
- **If more than a few laptops are red at 9:15:** do not start teaching over it. Fix the most
  common error once on the projector, sit each red laptop's owner with a green pair, and let the
  assistant work through the rest during Block 1. Lab 1 needs only the OpenAI key.

### 9:15 Block 1: First agent ([Lab 1](../labs/01-first-agent/README.md))

- **Explain:** a model predicts the next text; it has no memory and cannot act. An agent is a
  model plus instructions, memory and tools, in a loop, measured by evals.
- **Demo:** write `_model_call` live. Run the chat and ask the phone-call question.
- **The failure on purpose:** ask it to book. It cannot. Ask the room why before you tell them.
- **Watch for:** `_model_call` returning the whole response instead of the message.
- **Shortcut to the floor:** the full answer is on the lab page; have them type it, not paste it.
- **Debrief line to land:** prompting cannot fix missing knowledge or missing abilities.

### 10:00 Block 2: Traces ([Lab 2](../labs/02-traces/README.md))

- **Explain:** a trace is the record of one turn; a session is one call; a score is a judgment
  attached to a trace. You trace before you tune.
- **Demo:** wrap the client, run one turn, open the trace.
- **The failure on purpose:** open the trace of the answer that could not help. The system
  message has no class information in it. "The model didn't fail. It never had the fact."
- **Watch for:** traces that never arrive because the chat was closed with Ctrl-C, not `/end`.
- **Shortcut to the floor:** `uv run python scripts/catch_up.py 3`, then run one chat turn.
- **Debrief line to land:** "the agent is wrong" becomes "which step was wrong?"

### 11:00 Block 3: Evals ([Lab 3](../labs/03-evals/README.md))

- **Explain:** vibes do not scale. A test set, graders (code checks and a model judge), and an
  experiment that runs every case against a prompt version.
- **Demo:** push v1 and v2. Chat with both. Ask the room which feels better. Most will say v2.
- **The failure on purpose:** the v2 experiment. Honesty and safety drop. Nobody saw it in chat.
- **Watch for:** rate limits on brand-new OpenAI accounts. Have them run with `--limit 5` first.
- **Watch for:** a pair whose v2 run scores higher overall than v1. It happens: with no rules the
  model guesses, and some guesses pass. Send them to the category rows. Safety and honesty are
  where v2 fails, and that is the point of reading a scoreboard by category.
- **Give judge calibration time.** A judge that disagrees with the human grades is the lesson,
  not a problem. This is where the room usually goes quiet and then loud.
- **Shortcut to the floor:** at minute 25 of the build, any pair still writing graders copies
  `solution/gym_agent/evals/evaluators.py` over their own. The experiment matters more.
- **Debrief line to land:** good evals tell you what kind of problem you have. Here it is
  knowledge and action, not wording.

### 1:15 Block 4: Memory ([Lab 4](../labs/04-memory/README.md))

- **Explain:** the context window is a desk, a vector store is a filing cabinet. Embeddings put
  similar meanings close together. Chunk, embed, store; then retrieve the right three pages.
- **Demo:** ingest the handbook live and search it with one odd phrasing ("can my nanny sign?").
- **The failure on purpose:** `evals.retrieval -k 1`. Some questions miss. If retrieval misses,
  the model never sees the fact.
- **Watch for:** a new Pinecone index returning nothing for the first 10 to 30 seconds.
- **Shortcut to the floor:** `uv run python scripts/catch_up.py 5`, then `memory ingest` and the
  experiment re-run.
- **Debrief line to land:** retrieval quality and answer quality are separate, and you can
  measure each. The caller filter is a privacy boundary.

### 2:45 Block 5: Tools ([Lab 5](../labs/05-tools/README.md))

- **Explain:** a tool is a name, a description and a schema. The model proposes a call; your code
  decides whether to run it. Risk rises when a system can act, not only answer.
- **Demo:** write `validate_call` live, then show a booking stopping at the confirmation step.
- **The failure on purpose:** saved for the red-team round, which is this block's debrief.
- **Watch for:** OpenAI `400 … tool_call_id`: the assistant message with its tool calls must go
  into history before the tool results.
- **Shortcut to the floor:** the loop is on the lab page in full. If the guardrails are not
  passing by minute 30, `uv run python scripts/catch_up.py 6`.

### 3:40 Red-team round ([Lab 5, part 2](../labs/05-tools/README.md#break-it-the-red-team-round))

- No explanation. Give the five inputs and fifteen minutes. Pairs try to break their own agent,
  then swap and try to break another pair's.
- **Debrief (5 minutes):** each pair names one guardrail that held and the file it lives in, and
  one answer that should become a test case. Ask every time: which layer?
- **Line to land:** for inputs 1 to 3 there is code behind the model, so the booking is refused
  even if the model goes along. For inputs 4 and 5 there is only a sentence in the prompt. Ask
  which they would bet on after ten prompt changes.

### 4:00 Block 6: MCP ([Lab 6](../labs/06-mcp/README.md))

- **Explain (5 minutes):** one server, many clients. The model on the other side is not yours.
- **Demo:** the MCP Inspector calling `check_schedule`, then `book_class` with an age of 400.
- **Shortcut to the floor:** both functions are on the lab page.
- **Line to land:** the confirmation step still holds, because it lives in the server.

### 4:20 Make it yours ([Lab 7](../labs/07-ship-it/README.md))

- No steps. Each pair finishes the canvas for the workflow one of them brought. Most rows are
  already drafted from the earlier blocks.
- Circulate and push on two rows: "what we will not automate" and "owner and next step." A canvas
  without a name on it is not finished.
- If the sponsor is in the room, this is where they walk around.

### 4:45 Demos, exit ticket, close

- Three pairs, two minutes each: the call, then the scoreboard, then one failure they would fix
  next and the layer it lives in. Choose pairs with different failures.
- Hand out the [exit ticket](../handouts/exit-ticket.md). Collect it with the canvas.
- Close with what happens next: the recap tomorrow, the office hour, the email at day thirty.

## When things go wrong

| What happens | What to do |
|---|---|
| **A third of the laptops fail at 9:15** | Stop. Fix the most common error once on the projector for everyone. Seat failed laptops with working pairs. Protect the floor for Block 1, and let the assistant handle individual cases while the room builds. |
| **Your live demo crashes** | Narrate it. Read the error aloud, open the trace, say your guess. This is the failure lesson arriving early. If it is not fixed in two minutes, switch to the saved trace from your own full run and keep the schedule. |
| **A fast pair is done in ten minutes** | Point them at the ceiling on the lab page. If they finish that, make them helpers for the pair next to them. |
| **Someone says "this is all hype"** | Thank them, and turn the doubt into a test: "What would it have to get right for you to trust it? Let's add that as a case." Skeptics often become the most engaged people in the room once their doubt is part of the exercise. |
| **The API or the network goes down** | The lab tests are offline and still run, so pairs keep writing code. Teach from your saved Langfuse project and the screenshots in `docs/img/`. Hand out the spare key if it is one account. |
| **More than a third of the room is red at a checkpoint** | That is one unclear instruction, not a third of the room failing. Stop the build, show that step on the projector, and write down which step it was. |
| **You are running 15 minutes late after lunch** | Shorten Block 6 to a demo, and keep the red-team round and Make it yours whole. They carry outcomes 4 and 5. |
| **The sponsor asks for slides instead of a hands-on day** | Ask what they want people to do differently afterward. If they want people to build, slides cannot produce that: offer one block inside their agenda as proof. If they want people to decide, the room is leaders, not builders: run the [leaders' session](../leaders/README.md), two hours with no laptops. |

## Measuring the day

| When | What you collect | What it tells you |
|---|---|---|
| Before | Doctor output, one workflow per person, the three pairing questions | Who needs help before the day; how to pair; a baseline for confidence |
| During | The checkpoint in every block | Where the room is stuck, while you can still do something about it |
| At 5:00 | Green tests, scoreboards, canvases, [exit tickets](../handouts/exit-ticket.md) | Whether the five outcomes happened |
| Week one | The questions people bring to the office hour | What the labs did not teach |
| Day 30 | One email: did you build it, and did it reach anyone? | The number that matters |
| Day 60 to 90 | The sponsor check | Whether a second cohort runs |

**The number to report:** what share of participants left with a working, measured agent and a
canvas with an owner, and what share of those canvases reached real use within thirty days.

**The funnel for the sponsor:** invited → attended → finished the labs → left with an owner →
built something → in use by someone else.

**After each room,** read the "stuck longest" answers on the exit tickets. Anything that appears
three times becomes a fix in the lab README and a line in [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
before the next room.

The emails for every step are in [handouts/follow-up-emails.md](../handouts/follow-up-emails.md).

## Variant: half day (3.5 hours, engineers)

Blocks 1, 2, 3 and 5 in full. Demo Block 4 from your own laptop and have everyone run
`uv run python scripts/catch_up.py 5` and `memory ingest`, so they have working memory for the tools lab. Set Block 6
as homework. Keep the red-team round and Make it yours, at ten minutes each. Memory is the easiest
lab to do alone afterward; tools are the hardest to debug alone, so tools stay in the room.

## Variant: on your own

The same labs, self-paced, in about five and a half hours. The "idea in two minutes" section of
each lab page stands in for the explanation, and `solution/` stands in for the demo. The debrief questions on each lab page are for the learner to answer in
writing, and the canvas is still the last step. Nothing else changes.

## Leaders get a different session

Leaders who decide where agents are used do not get a shorter version of this day. They make a
different decision, so they get a different session with a different outcome: two hours, no
laptops, ending in one pilot with a named owner and a one-page plan. It uses this agent's trace,
scoreboard and guardrails as its exhibits. It is in [leaders/](../leaders/README.md), with its
own [run of show](../leaders/FACILITATOR.md) and [handouts](../leaders/handouts/README.md).
