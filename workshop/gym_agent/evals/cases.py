"""Load the eval files in data/evals/."""

from __future__ import annotations

import json

from ..config import DATA_DIR

EVALS_DIR = DATA_DIR / "evals"


def load_jsonl(name: str) -> list[dict]:
    with open(EVALS_DIR / name) as f:
        return [json.loads(line) for line in f if line.strip()]


def agent_cases() -> list[dict]:
    return load_jsonl("agent_cases.jsonl")
