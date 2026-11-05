"""The model client.

Lab 1 uses the plain OpenAI client. Lab 2 swaps in Langfuse's drop-in wrapper, which has the same
API but also records every call (prompt, response, tokens, cost, latency) as a trace.
"""

from __future__ import annotations

from .config import langfuse_enabled, require  # noqa: F401  (you'll use langfuse_enabled in Lab 2)


def get_client():
    require("OPENAI_API_KEY")
    # TODO(lab2): when langfuse_enabled(), import OpenAI from langfuse.openai instead.
    #   It's a drop-in replacement: same class, same methods, and every call becomes a trace.
    from openai import OpenAI

    return OpenAI()
