"""Settings and paths. Everything configurable lives in your `.env` file (copy `.env.example`)."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# <repo>/solution/gym_agent/config.py -> parents[2] is the repo root (the same for workshop/).
REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
PROMPTS_DIR = REPO_ROOT / "prompts"
RUNTIME_DIR = REPO_ROOT / ".runtime"  # git-ignored: bookings made while you test

load_dotenv(REPO_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    model: str = os.getenv("AGENT_MODEL", "gpt-5-mini")
    judge_model: str = os.getenv("JUDGE_MODEL", "gpt-5-mini")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
    embedding_dim: int = int(os.getenv("EMBEDDING_DIM", "1536"))
    pinecone_index: str = os.getenv("PINECONE_INDEX", "ridgeline-agent")
    pinecone_cloud: str = os.getenv("PINECONE_CLOUD", "aws")
    pinecone_region: str = os.getenv("PINECONE_REGION", "us-east-1")
    prompt_name: str = os.getenv("LANGFUSE_PROMPT_NAME", "front-desk")
    prompt_label: str = os.getenv("LANGFUSE_PROMPT_LABEL", "production")
    dataset_name: str = os.getenv("LANGFUSE_DATASET", "ridgeline-agent-cases")
    max_steps: int = int(os.getenv("AGENT_MAX_STEPS", "6"))


SETTINGS = Settings()


def has(*names: str) -> bool:
    """True if every environment variable in `names` is set and non-empty."""
    return all(os.getenv(n) for n in names)


def langfuse_enabled() -> bool:
    return has("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY") and os.getenv(
        "LANGFUSE_TRACING_ENABLED", "true"
    ).lower() != "false"


def _quiet_langfuse_when_unconfigured() -> None:
    """Before Lab 2 you have no Langfuse keys. Tracing then turns itself off; hide its warnings."""
    if not langfuse_enabled():
        import logging

        import langfuse.logger  # noqa: F401  (importing it sets its own log level, so import first)

        logging.getLogger("langfuse").setLevel(logging.ERROR)


_quiet_langfuse_when_unconfigured()


def require(*names: str) -> None:
    """Exit with a friendly message if a required key is missing from `.env`."""
    missing = [n for n in names if not os.getenv(n)]
    if missing:
        sys.exit(
            f"Missing {', '.join(missing)} in {REPO_ROOT / '.env'}.\n"
            "Copy .env.example to .env and follow docs/00-setup.md to get the keys, "
            "then run:  uv run python -m gym_agent.doctor"
        )
