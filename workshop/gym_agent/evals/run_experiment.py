"""Run the test set against one prompt version, grade every answer, and record it in Langfuse.

    uv run python -m gym_agent.evals.run_experiment --label production
    uv run python -m gym_agent.evals.run_experiment --label staging
    uv run python -m gym_agent.evals.run_experiment --prompt-file prompts/system_v1.md --local

Then open Langfuse -> Datasets -> ridgeline-agent-cases -> Runs, and compare the runs side by side.
`--local` runs the cases straight from data/evals/ (no dataset upload needed; still traced).
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from pathlib import Path

from langfuse import get_client
from rich.console import Console
from rich.table import Table

from ..config import SETTINGS, require
from ..llm import get_client as get_llm
from ..prompts import load_system_prompt
from .cases import agent_cases
from .evaluators import booking_policy, make_judge, pass_rates, tool_use
from .task import field, make_agent_factory, run_case


def main() -> None:
    p = argparse.ArgumentParser(prog="python -m gym_agent.evals.run_experiment")
    src = p.add_mutually_exclusive_group()
    src.add_argument("--label", default=None, help="Langfuse prompt label to test (default: production)")
    src.add_argument("--prompt-file", type=Path, default=None, help="test a local prompt file instead")
    p.add_argument("--local", action="store_true", help="use data/evals/agent_cases.jsonl, not the Langfuse dataset")
    p.add_argument("--no-memory", action="store_true", help="don't use the Pinecone handbook even if configured")
    p.add_argument("--no-tools", action="store_true", help="run the agent without tools")
    p.add_argument("--limit", type=int, default=None, help="only run the first N cases")
    p.add_argument("--name", default=None, help="run name (default: derived from the prompt version)")
    args = p.parse_args()
    require("OPENAI_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY")

    client = get_llm()
    handbook = None
    if not args.no_memory:
        from ..memory import Handbook, PineconeStore

        store = PineconeStore.try_connect()  # None until you've run Lab 4's ingest
        handbook = Handbook(client, store) if store else None
    prompt = load_system_prompt(label=args.label, prompt_file=args.prompt_file)
    factory = make_agent_factory(prompt=prompt, client=client, handbook=handbook,
                                 tools=[] if args.no_tools else None)
    features = f"{'rag' if handbook else 'no-rag'}+{'no-tools' if args.no_tools else 'tools'}"
    run_name = args.name or f"{prompt.version} {features}"

    def task(*, item, **_):
        return run_case(factory, field(item, "input"))

    lf = get_client()
    common = dict(name="ridgeline-agent", run_name=run_name, task=task,
                  evaluators=[booking_policy, tool_use, make_judge(client)], run_evaluators=[pass_rates],
                  max_concurrency=4, metadata={"prompt_version": prompt.version, "features": features})
    if args.local:
        cases = agent_cases()[: args.limit]
        data = [{"input": c["input"], "expected_output": c["expected"], "metadata": {"id": c["id"], "category": c["category"]}} for c in cases]
        result = lf.run_experiment(data=data, **common)
    else:
        dataset = lf.get_dataset(SETTINGS.dataset_name)
        if args.limit:
            dataset.items = dataset.items[: args.limit]
        result = dataset.run_experiment(**common)
    lf.flush()
    _print_summary(run_name, result)


def _print_summary(run_name: str, result) -> None:
    console = Console()
    table = Table(title=f"Experiment: {run_name}")
    for col in ("case", "category", "judge", "booking", "tool", "judge's reason"):
        table.add_column(col)
    by_cat: dict[str, list[bool]] = defaultdict(list)
    for r in result.item_results:
        meta = field(r.item, "metadata") or {}
        ev = {e.name: e for e in r.evaluations}
        passed = bool(ev.get("judge_pass") and ev["judge_pass"].value) and bool(
            ev.get("booking_policy") and ev["booking_policy"].value)
        by_cat[meta.get("category", "?")].append(passed)

        def mark(name, ev=ev):
            e = ev.get(name)
            return "-" if e is None else ("[green]pass[/]" if e.value else "[red]fail[/]")

        case_id = meta.get("id") or (getattr(r.item, "id", None) if not isinstance(r.item, dict) else None)
        table.add_row(case_id or "?",
                      meta.get("category", "?"), mark("judge_pass"), mark("booking_policy"), mark("tool_use"),
                      (ev["judge_pass"].comment or "")[:70] if "judge_pass" in ev else "")
    console.print(table)
    for cat, vals in sorted(by_cat.items()):
        console.print(f"  {cat:<10} {sum(vals)}/{len(vals)} passed")
    for e in result.run_evaluations:
        console.print(f"  [bold]{e.name}[/] = {e.value}")
    if result.experiment_url:
        console.print(f"\nOpen this run in Langfuse: {result.experiment_url}")


if __name__ == "__main__":
    main()
