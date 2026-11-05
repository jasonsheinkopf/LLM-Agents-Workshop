"""Evaluate retrieval on its own: does the right handbook section come back in the top k?

    uv run python -m gym_agent.evals.retrieval -k 3

If retrieval misses, the model never sees the fact, and no prompt can fix that. Measure it separately.
"""

from __future__ import annotations

import argparse

from rich.console import Console

from ..config import require
from ..llm import get_client
from ..memory import Handbook, PineconeStore
from .cases import load_jsonl


def hit_rate(handbook: Handbook, cases: list[dict], k: int) -> tuple[float, list[dict]]:
    rows = []
    for c in cases:
        sections = [h["section"] for h in handbook.search(c["question"], k=k)]
        rows.append({**c, "got": sections, "hit": c["expected_section"] in sections})
    return sum(r["hit"] for r in rows) / len(rows), rows


def main() -> None:
    require("OPENAI_API_KEY", "PINECONE_API_KEY")
    p = argparse.ArgumentParser(prog="python -m gym_agent.evals.retrieval")
    p.add_argument("-k", type=int, default=3)
    args = p.parse_args()
    console = Console()
    score, rows = hit_rate(Handbook(get_client(), PineconeStore.connect()), load_jsonl("retrieval_cases.jsonl"), args.k)
    for r in rows:
        mark = "[green]hit [/]" if r["hit"] else "[red]miss[/]"
        console.print(f"{mark} {r['question']:<48} want [{r['expected_section']}]  got {r['got']}")
    console.print(f"\n[bold]hit@{args.k} = {score:.0%}[/] over {len(rows)} questions")

    from langfuse import get_client as lf

    lf().flush()


if __name__ == "__main__":
    main()
