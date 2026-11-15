"""The model client.

Lab 1 uses the plain OpenAI client. Lab 2 swaps in Langfuse's drop-in wrapper, which has the same
API but also records every call (prompt, response, tokens, cost, latency) as a trace.
"""

from __future__ import annotations

from .config import langfuse_enabled, require  # noqa: F401  (you'll use langfuse_enabled in Lab 2)


def get_client():
    """Return the OpenAI client the app uses for chat, embeddings and the judge.

    From Lab 2 it is Langfuse's drop-in wrapper, so every call through it is traced.
    """
    require("OPENAI_API_KEY")
    # TODO(lab2): when langfuse_enabled(), import OpenAI from langfuse.openai instead of openai.
    #   Replace the import below with an if/else that picks one of the two. The wrapper has the
    #   same class and methods, so nothing else in the app changes.
    from openai import OpenAI

    return OpenAI()
