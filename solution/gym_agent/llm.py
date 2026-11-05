"""The model client.

Lab 1 uses the plain OpenAI client. Lab 2 swaps in Langfuse's drop-in wrapper, which has the same
API but also records every call (prompt, response, tokens, cost, latency) as a trace.
"""

from __future__ import annotations

from .config import langfuse_enabled, require


def get_client():
    require("OPENAI_API_KEY")
    if langfuse_enabled():
        from langfuse.openai import OpenAI  # same interface, plus tracing
    else:
        from openai import OpenAI
    return OpenAI()
