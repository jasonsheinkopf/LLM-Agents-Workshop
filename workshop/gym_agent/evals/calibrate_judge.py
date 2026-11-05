"""Can you trust the judge? Compare it with human labels before you rely on its scores.

    uv run python -m gym_agent.evals.calibrate_judge

data/evals/judge_calibration.jsonl holds replies a human already graded (pass/fail, and why).
If the judge disagrees with people too often, fix the judge prompt (evaluators.JUDGE_PROMPT)
before you use it to choose between agent prompts.
"""

from __future__ import annotations

from rich.console import Console

from ..config import SETTINGS, require
from ..llm import get_client
from .cases import load_jsonl
from .evaluators import judge_reply


def main() -> None:
    require("OPENAI_API_KEY")
    console = Console()
    client = get_client()
    rows = load_jsonl("judge_calibration.jsonl")
    agree, tp, fp, fn = 0, 0, 0, 0
    for row in rows:
        v = judge_reply(client, turns=[row["question"]], reply=row["reply"], facts=row["facts"], must_not=[])
        same = v["pass"] == row["human_pass"]
        agree += same
        tp += v["pass"] and row["human_pass"]
        fp += v["pass"] and not row["human_pass"]
        fn += (not v["pass"]) and row["human_pass"]
        mark = "[green]agree[/]" if same else "[red]DISAGREE[/]"
        console.print(f"{mark}  {row['id']}  human={'pass' if row['human_pass'] else 'fail'} "
                      f"judge={'pass' if v['pass'] else 'fail'}  ({v['reason']})")
    n = len(rows)
    console.print(f"\nJudge model: {SETTINGS.judge_model}")
    console.print(f"[bold]Agreement with humans: {agree}/{n} = {agree / n:.0%}[/]")
    console.print(f"Judge passed {fp} answer(s) a human failed (too lenient) and failed {fn} a human passed (too strict).")
    console.print("Aim for 90%+ agreement, and look hardest at the too-lenient ones: those let bad prompts through.")

    from langfuse import get_client as lf

    lf().flush()


if __name__ == "__main__":
    main()
