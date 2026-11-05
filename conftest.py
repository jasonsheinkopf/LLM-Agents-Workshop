"""Offline tests: no API keys, no network, no cost.

By default the tests check YOUR code in workshop/. To check the reference solution instead:

    uv run pytest                       # your code (workshop/)
    uv run pytest tests/test_lab1_agent.py
    uv run pytest --impl solution       # the finished version
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent

# Never send traces or read real prompts from tests, even if your .env has Langfuse keys.
os.environ["LANGFUSE_TRACING_ENABLED"] = "false"
os.environ["PINECONE_API_KEY"] = ""


def pytest_addoption(parser):
    parser.addoption("--impl", default=os.getenv("WORKSHOP_IMPL", "workshop"), choices=["workshop", "solution"],
                     help="which folder to test: workshop (your code, default) or solution")


def pytest_configure(config):
    impl = config.getoption("--impl")
    sys.path.insert(0, str(REPO / impl))
    sys.path.insert(0, str(REPO / "tests"))
    config._workshop_impl = impl


def pytest_report_header(config):
    return f"testing: {config._workshop_impl}/gym_agent"


@pytest.fixture
def llm():
    from fakes import FakeLLM

    return FakeLLM()
