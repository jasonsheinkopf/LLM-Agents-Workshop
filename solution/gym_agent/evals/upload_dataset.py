"""Upload data/evals/agent_cases.jsonl to a Langfuse dataset. Safe to re-run (ids are stable).

    uv run python -m gym_agent.evals.upload_dataset
"""

from __future__ import annotations

from langfuse import get_client

from ..config import SETTINGS, require
from .cases import agent_cases


def main() -> None:
    require("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY")
    lf = get_client()
    lf.create_dataset(
        name=SETTINGS.dataset_name,
        description="Ridgeline phone agent: caller turns -> what a good answer must (and must not) do.",
    )
    cases = agent_cases()
    for case in cases:
        lf.create_dataset_item(
            dataset_name=SETTINGS.dataset_name,
            id=case["id"],  # same id = update in place, so re-running never duplicates items
            input=case["input"],
            expected_output=case["expected"],
            metadata={"category": case["category"]},
        )
    lf.flush()
    print(f"Uploaded {len(cases)} items to Langfuse dataset '{SETTINGS.dataset_name}'.")


if __name__ == "__main__":
    main()
