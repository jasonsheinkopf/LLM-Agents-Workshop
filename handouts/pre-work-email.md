# Pre-work email

Send one week before. It asks for about 25 minutes. Send a one-line reminder two days before to
anyone whose doctor output you have not received.

---

**Subject:** Before [day, date]: 25 minutes of preparation for the agents workshop

Hi [name],

On [day, date] we spend the day building an AI agent, piece by piece: one that answers from a
handbook, takes actions safely, and that you can measure. You will work in pairs, and you will be
writing code within the first half hour.

To make that possible, three things before the day. Together they take about 25 minutes.

**1. Set up your laptop (20 minutes).** Follow Lab 0:
https://github.com/jasonsheinkopf/LLM-Agents-Workshop/blob/main/docs/00-setup.md
You are ready when this command prints three PASS lines:

```
cd workshop
uv run python -m gym_agent.doctor
```

Reply to this email with the output. If something fails, send what you see and we will fix it
before the day, not during it. [If your company laptop blocks installs or outside APIs, tell me now.]

**2. Bring one workflow from your own job.** Something repetitive or decision-heavy that you or
your team does every week. Reply with three sentences:

- What starts it? (a ticket arrives, a customer calls, a report is due)
- What does someone need to know or look up to do it?
- What is the result? (a reply, a booking, a decision, a document)

You will come back to this workflow all day, and leave with a plan for it.

**3. Answer three questions**, so I can pair people well:

- Have you called an LLM API from code? (never / once or twice / regularly)
- Which of these have you used: tracing, evals, a vector database, tool calling, MCP?
- From 1 to 5, how confident are you that you could tell whether an agent's answers are good
  enough to ship?

**Costs.** You need an OpenAI API key with about $2 of credit. [We will provide keys. / Please
expense it.] Langfuse and Pinecone are free at the size we use.

**Data.** Everything we use on the day is invented. Please don't bring customer data, credentials
or anything confidential to the workshop.

**The day.** 9:00 to 5:00, [room]. Lunch at 12:15. Bring your laptop and charger.

See you on [day],
[instructor]
