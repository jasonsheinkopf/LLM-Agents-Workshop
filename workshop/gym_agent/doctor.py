"""Check your setup: every key in .env, tested against the real service.

    uv run python -m gym_agent.doctor
"""

from __future__ import annotations

import os
import sys

from rich.console import Console

from .config import REPO_ROOT, SETTINGS

console = Console()
OK, FAIL, SKIP = "[green]PASS[/]", "[red]FAIL[/]", "[yellow]SKIP[/]"


def check_openai() -> tuple[str, str]:
    if not os.getenv("OPENAI_API_KEY"):
        return FAIL, "OPENAI_API_KEY is not set (Lab 0, step 2)"
    from openai import OpenAI

    c = OpenAI()
    r = c.chat.completions.create(model=SETTINGS.model, messages=[{"role": "user", "content": "Reply with: ok"}])
    e = c.embeddings.create(model=SETTINGS.embedding_model, input=["ok"])
    dim = len(e.data[0].embedding)
    if dim != SETTINGS.embedding_dim:
        return FAIL, f"{SETTINGS.embedding_model} returns {dim} dims but EMBEDDING_DIM={SETTINGS.embedding_dim}"
    return OK, f"{SETTINGS.model} replied {r.choices[0].message.content!r}; {SETTINGS.embedding_model} -> {dim} dims"


def check_langfuse() -> tuple[str, str]:
    if not (os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")):
        return SKIP, "LANGFUSE_* keys not set yet (needed from Lab 2)"
    from langfuse import get_client

    url = os.getenv("LANGFUSE_BASE_URL") or os.getenv("LANGFUSE_HOST") or "https://cloud.langfuse.com"
    if not get_client().auth_check():
        return FAIL, f"keys rejected by {url}. Check the region (EU vs US) in LANGFUSE_BASE_URL"
    return OK, f"authenticated with {url}"


def check_pinecone() -> tuple[str, str]:
    if not os.getenv("PINECONE_API_KEY"):
        return SKIP, "PINECONE_API_KEY not set yet (needed from Lab 4)"
    from pinecone import Pinecone

    pc = Pinecone()
    pc.list_indexes()  # proves the key works
    if pc.has_index(SETTINGS.pinecone_index):
        stats = pc.Index(name=SETTINGS.pinecone_index).describe_index_stats()
        ns = {k: v.vector_count for k, v in (stats.namespaces or {}).items()}
        return OK, f"index '{SETTINGS.pinecone_index}' exists; vectors per namespace: {ns or 'none yet'}"
    return OK, f"key works; index '{SETTINGS.pinecone_index}' not created yet (Lab 4 creates it)"


def main() -> None:
    console.print(f"[bold]Workshop doctor[/]  (reading {REPO_ROOT / '.env'})\n")
    console.print(f"{OK if sys.version_info >= (3, 11) else FAIL}  Python {sys.version.split()[0]}")
    if not (REPO_ROOT / ".env").exists():
        console.print(f"{FAIL}  no .env file. Run:  cp .env.example .env")
    failed = False
    for name, check in [("OpenAI", check_openai), ("Langfuse", check_langfuse), ("Pinecone", check_pinecone)]:
        try:
            status, detail = check()
        except Exception as e:  # show the real error, it's usually self-explanatory
            status, detail = FAIL, f"{type(e).__name__}: {e}"
        failed |= status == FAIL
        console.print(f"{status}  {name}: {detail}")
    console.print("\n[bold green]All set.[/]" if not failed else "\n[bold red]Fix the FAIL lines, then re-run.[/] See docs/TROUBLESHOOTING.md")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
