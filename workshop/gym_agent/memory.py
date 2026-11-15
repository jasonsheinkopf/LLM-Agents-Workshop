"""Long-term memory with a vector database (Lab 4).

Two "filing cabinet drawers" in one Pinecone index, kept apart by namespace:

* `handbook`: the gym's policies, chunked by section, embedded and stored once (`ingest`).
* `memories`: short facts about individual callers, written after each call and only ever read
  back with a `caller_id` filter, so one caller's memories never leak into another's call.

    uv run python -m gym_agent.memory ingest                      # chunk -> embed -> upsert
    uv run python -m gym_agent.memory search "can a babysitter sign the waiver?"
    uv run python -m gym_agent.memory recall dana "kids"          # what do we remember about Dana?
    uv run python -m gym_agent.memory forget dana                 # delete Dana's memories
"""

from __future__ import annotations

import argparse
import json
import math
import re
import time
import uuid
from dataclasses import dataclass
from typing import Any, Protocol

from langfuse import observe

from .config import SETTINGS, require
from .gym import load_handbook

HANDBOOK_NS = "handbook"
MEMORY_NS = "memories"


# --------------------------------------------------------------------------- chunking
@dataclass
class Chunk:
    id: str
    section: str
    text: str


def chunk_markdown(markdown: str) -> list[Chunk]:
    """Split the handbook on its `## ` headings: one chunk per policy section.

    Sections are short and self-contained, so a heading is a natural chunk boundary. Each chunk
    keeps its heading in the text, which helps both the embedding and the model's citation.
    """
    # TODO(lab4): return one Chunk per section, then delete the `raise` line below.
    #   Split on lines that start with "## ": re.split(r"^## ", markdown, flags=re.M)[1:].
    #   For each block: the heading is its first line; the body is the rest, with runs of
    #   whitespace collapsed to single spaces. Skip a section with an empty body.
    #   id = "handbook-" + a slug of the heading (e.g. "handbook-day-passes-and-prices"),
    #   section = the heading, text = f"{heading}: {body}".
    raise NotImplementedError("Lab 4: write chunk_markdown (labs/04-memory/README.md)")


# --------------------------------------------------------------------------- embeddings
def embed(client, texts: list[str]) -> list[list[float]]:
    """Turn texts into vectors, one per text, in the same order. Similar meanings land close together."""
    # TODO(lab4): make one request for all the texts, then delete the `raise` line below.
    #   Call client.embeddings.create(model=SETTINGS.embedding_model, input=texts), and return
    #   the .embedding of each item in the response's .data.
    raise NotImplementedError("Lab 4: write embed (labs/04-memory/README.md)")


# --------------------------------------------------------------------------- vector stores
class VectorStore(Protocol):
    def upsert(self, records: list[dict], namespace: str) -> None: ...
    def query(self, vector: list[float], top_k: int, namespace: str, filter: dict | None = None) -> list[dict]: ...
    def delete_prefix(self, namespace: str, prefix: str) -> None: ...


class PineconeStore:
    """The real thing: a serverless Pinecone index."""

    def __init__(self, index) -> None:
        self.index = index

    @classmethod
    def connect(cls, create: bool = False) -> PineconeStore:
        require("PINECONE_API_KEY")
        from pinecone import Pinecone, ServerlessSpec

        pc = Pinecone()  # reads PINECONE_API_KEY
        name = SETTINGS.pinecone_index
        if not pc.has_index(name):
            if not create:
                raise SystemExit(
                    f"Pinecone index '{name}' doesn't exist yet. Run: uv run python -m gym_agent.memory ingest"
                )
            print(f"Creating Pinecone index '{name}' ({SETTINGS.embedding_dim} dims, cosine)...")
            pc.create_index(
                name=name,
                dimension=SETTINGS.embedding_dim,
                metric="cosine",
                spec=ServerlessSpec(cloud=SETTINGS.pinecone_cloud, region=SETTINGS.pinecone_region),
            )
        return cls(pc.Index(name=name))

    @classmethod
    def try_connect(cls) -> PineconeStore | None:
        """Connect only if the key is set AND the index exists (i.e. you've run `ingest`)."""
        import os

        if not os.getenv("PINECONE_API_KEY"):
            return None
        from pinecone import Pinecone

        pc = Pinecone()
        return cls(pc.Index(name=SETTINGS.pinecone_index)) if pc.has_index(SETTINGS.pinecone_index) else None

    def upsert(self, records: list[dict], namespace: str) -> None:
        self.index.upsert(vectors=records, namespace=namespace, show_progress=False)

    def query(self, vector, top_k, namespace, filter=None) -> list[dict]:
        res = self.index.query(
            vector=vector, top_k=top_k, namespace=namespace, filter=filter, include_metadata=True
        )
        return [{"id": m.id, "score": m.score, "metadata": dict(m.metadata or {})} for m in res.matches]

    def delete_prefix(self, namespace: str, prefix: str) -> None:
        # Serverless indexes can't delete by metadata filter, so list the ids by prefix, then delete them.
        ids = [v.id for page in self.index.list(prefix=prefix, namespace=namespace) for v in page.vectors]
        if ids:
            self.index.delete(ids=ids, namespace=namespace)


class InMemoryStore:
    """A tiny stand-in with the same interface. Used by the offline tests, never by the agent."""

    def __init__(self) -> None:
        self.data: dict[str, dict[str, dict]] = {}

    def upsert(self, records, namespace):
        ns = self.data.setdefault(namespace, {})
        for r in records:
            ns[r["id"]] = r

    def query(self, vector, top_k, namespace, filter=None):
        def ok(meta: dict) -> bool:
            for key, cond in (filter or {}).items():
                want = cond.get("$eq") if isinstance(cond, dict) else cond
                if meta.get(key) != want:
                    return False
            return True

        def cos(a, b):
            dot = sum(x * y for x, y in zip(a, b, strict=True))
            return dot / ((math.sqrt(sum(x * x for x in a)) * math.sqrt(sum(y * y for y in b))) or 1)

        hits = [
            {"id": r["id"], "score": cos(vector, r["values"]), "metadata": r["metadata"]}
            for r in self.data.get(namespace, {}).values()
            if ok(r["metadata"])
        ]
        return sorted(hits, key=lambda h: -h["score"])[:top_k]

    def delete_prefix(self, namespace, prefix):
        ns = self.data.get(namespace, {})
        for rid in [rid for rid in ns if rid.startswith(prefix)]:
            del ns[rid]


# --------------------------------------------------------------------------- the handbook drawer
class Handbook:
    """The gym's handbook in the vector store: written once by `ingest`, read on every turn."""

    def __init__(self, client, store: VectorStore) -> None:
        self.client, self.store = client, store

    def ingest(self) -> int:
        """Chunk -> embed -> store (vector + text + metadata). Safe to re-run: ids are stable."""
        # TODO(lab4): chunk, embed and store the handbook, then delete the `raise` line below.
        #   1. chunk_markdown(load_handbook()).
        #   2. embed every chunk's text in one call.
        #   3. self.store.upsert([...], namespace=HANDBOOK_NS), with one record per chunk:
        #      {"id": chunk.id, "values": vector, "metadata": {"section": ..., "text": ...}}.
        #   Return the number of chunks.
        raise NotImplementedError("Lab 4: write Handbook.ingest (labs/04-memory/README.md)")

    @observe(name="search_handbook", as_type="retriever")
    def search(self, query: str, k: int = 3) -> list[dict]:
        """Return the k handbook sections nearest to `query`, best first."""
        # TODO(lab4): embed the query, look it up, then delete the `raise` line below.
        #   Query with self.store.query(vector, top_k=k, namespace=HANDBOOK_NS). Each hit has an
        #   "id", a "score" and the "metadata" you stored in ingest. Return one dict per hit:
        #   {"section": ..., "text": ..., "score": <the score rounded to 3 places>}.
        raise NotImplementedError("Lab 4: write Handbook.search (labs/04-memory/README.md)")


# --------------------------------------------------------------------------- the caller drawer
EXTRACT_PROMPT = """You maintain long-term memory for a climbing gym's phone assistant.
From the call transcript below, list durable facts about the CALLER that would help on a future
call: names and ages of people they book for, preferences, open issues. Skip small talk, anything
the gym's handbook already says, and anything sensitive (health details, payment details).
Reply with JSON only: {"facts": ["...", "..."]}. Use an empty list if there is nothing worth keeping.

Transcript:
"""


class CallerMemory:
    """Short facts about each caller, written at the end of a call and recalled on the next one."""

    def __init__(self, client, store: VectorStore) -> None:
        self.client, self.store = client, store

    def remember(self, caller_id: str, facts: list[str]) -> None:
        if not facts:
            return
        vectors = embed(self.client, facts)
        now = int(time.time())
        self.store.upsert(
            [
                {"id": f"mem-{caller_id}-{uuid.uuid4().hex[:8]}", "values": v,
                 "metadata": {"caller_id": caller_id, "text": f, "created_at": now}}
                for f, v in zip(facts, vectors, strict=True)
            ],
            namespace=MEMORY_NS,
        )

    @observe(name="recall_caller_memories", as_type="retriever")
    def recall(self, caller_id: str, query: str, k: int = 5) -> list[str]:
        """Return up to k of this caller's memories that best match `query`, as plain text."""
        # TODO(lab4): write this like Handbook.search, then delete the `raise` line below.
        #   Two differences: query namespace MEMORY_NS, and pass the metadata filter
        #   {"caller_id": {"$eq": caller_id}}. That filter is the privacy boundary: without it, one
        #   caller's memories could turn up in another caller's call. Return just the texts.
        raise NotImplementedError("Lab 4: write CallerMemory.recall (labs/04-memory/README.md)")

    def forget(self, caller_id: str) -> None:
        # Memory ids all start with "mem-<caller_id>-" (see remember), so delete by that prefix.
        self.store.delete_prefix(namespace=MEMORY_NS, prefix=f"mem-{caller_id}-")

    @observe(name="extract_memories")
    def extract_facts(self, transcript: list[dict[str, Any]]) -> list[str]:
        lines = [f"{m['role']}: {m['content']}" for m in transcript if m.get("content") and m["role"] in ("user", "assistant")]
        if not lines:
            return []
        resp = self.client.chat.completions.create(
            model=SETTINGS.model,
            messages=[{"role": "user", "content": EXTRACT_PROMPT + "\n".join(lines)}],
            response_format={"type": "json_object"},
        )
        try:
            facts = json.loads(resp.choices[0].message.content or "{}").get("facts", [])
        except json.JSONDecodeError:
            return []
        return [f for f in facts if isinstance(f, str) and f.strip()]


# --------------------------------------------------------------------------- CLI
def main() -> None:
    from .llm import get_client

    p = argparse.ArgumentParser(prog="python -m gym_agent.memory")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ingest", help="create the index if needed, then load the handbook")
    s = sub.add_parser("search", help="search the handbook")
    s.add_argument("query")
    s.add_argument("-k", type=int, default=3)
    r = sub.add_parser("recall", help="show what the agent remembers about a caller")
    r.add_argument("caller_id")
    r.add_argument("query", nargs="?", default="everything about this caller")
    f = sub.add_parser("forget", help="delete a caller's memories")
    f.add_argument("caller_id")
    args = p.parse_args()

    client = get_client()
    store = PineconeStore.connect(create=args.cmd == "ingest")
    if args.cmd == "ingest":
        n = Handbook(client, store).ingest()
        print(f"Upserted {n} handbook chunks into '{SETTINGS.pinecone_index}' / namespace '{HANDBOOK_NS}'.")
        print("New vectors can take a few seconds to become searchable.")
    elif args.cmd == "search":
        for hit in Handbook(client, store).search(args.query, k=args.k):
            print(f"{hit['score']:.3f}  [{hit['section']}]  {hit['text'][:110]}...")
    elif args.cmd == "recall":
        facts = CallerMemory(client, store).recall(args.caller_id, args.query)
        print("\n".join(f"- {x}" for x in facts) or f"(no memories for {args.caller_id})")
    else:
        CallerMemory(client, store).forget(args.caller_id)
        print(f"Deleted memories for {args.caller_id}.")

    from langfuse import get_client as lf

    lf().flush()


if __name__ == "__main__":
    main()
