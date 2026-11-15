# Glossary

Every term the workshop uses, in a sentence or two, with the lab where you meet it.

| Term | Meaning | Lab |
|---|---|---|
| **LLM** | A model trained to predict the next token of text. Its weights are frozen after training. | 1 |
| **Token** | A chunk of text (roughly ¾ of a word) that models read and write. You pay per token. | 1 |
| **System prompt** | The instructions sent first on every call: the agent's job description. | 1 |
| **Context window** | Everything the model sees in one call: the prompt, the history, retrieved text and tool results. The "desk". | 1, 4 |
| **Agent** | A model plus instructions, memory and tools, running in a loop, measured by evals. | 1 |
| **Workflow vs agent** | In a workflow, your code decides the steps and the model fills them in. In an agent, the model decides the next step. Start with the simplest one that solves the task. | 1 |
| **Trace** | The record of one unit of work (one turn), as a tree of observations. | 2 |
| **Observation** | One step inside a trace: a generation (model call), retriever, tool, span, or evaluator. | 2 |
| **Session** | Traces grouped together: here, one phone call. | 2 |
| **Score** | A judgment attached to a trace: user feedback, a code check, or a judge's verdict. | 2, 3 |
| **Prompt management** | Prompts stored outside the code with versions and labels, and fetched at runtime. | 3 |
| **Label** | A movable pointer to a prompt version (`production`, `staging`). Promoting means moving the label. | 3 |
| **Dataset / test set** | Inputs, plus the expected *behaviour* for each. | 3 |
| **Evaluator / grader** | A function that scores an output: a code check, or an LLM-as-a-judge. | 3 |
| **LLM-as-a-judge** | A second model call that grades an answer against a rubric. | 3 |
| **Calibration** | Measuring how often the judge agrees with human labels, before trusting it. | 3 |
| **Experiment** | One run of a dataset through one version of the system, graded. You compare runs. | 3 |
| **Embedding** | A list of numbers representing a text's meaning. Similar meanings → nearby vectors. | 4 |
| **Vector database** | Stores embeddings and finds the nearest ones fast (Pinecone). The "filing cabinet". | 4 |
| **Chunking** | Splitting documents into pieces small enough to retrieve precisely. | 4 |
| **RAG** | Retrieval-augmented generation: retrieve relevant text, put it in the prompt, then answer. | 4 |
| **Namespace** | A partition inside a Pinecone index (`handbook`, `memories`). | 4 |
| **Metadata filter** | A condition on stored metadata (`caller_id = dana`) applied during search. Here, a privacy boundary. | 4 |
| **hit@k** | The share of questions whose right chunk shows up in the top *k* results. | 4 |
| **Tool** | A name, a description and a JSON schema that the model can ask your code to run. | 5 |
| **Tool call** | The model's structured request to run a tool, with arguments as a JSON string. | 5 |
| **Agent loop** | Think → act → observe, repeated until the model answers or a step limit is hit. | 5 |
| **Guardrail** | A rule enforced in code around the model: allow-list, validation, confirmation, limits. | 5 |
| **Least privilege** | Give the agent only the access it needs. Identity comes from the session, not from the model. | 5 |
| **Prompt injection** | Text (from a user, a document or a tool) that tries to override the agent's instructions. | 5 |
| **MCP** | Model Context Protocol: a standard way for any AI app to discover and call tools on a server. | 6 |
| **stdio / streamable HTTP** | MCP's transports: a local subprocess, or a URL. | 6 |
