"""A scripted stand-in for the OpenAI client, so tests run offline and deterministically."""

from __future__ import annotations

import hashlib
import json
import re
from types import SimpleNamespace


def tool_call(name: str, args: dict | str, call_id: str | None = None):
    raw = args if isinstance(args, str) else json.dumps(args)
    return SimpleNamespace(id=call_id or f"call_{name}", type="function",
                           function=SimpleNamespace(name=name, arguments=raw))


def bow_embedding(text: str, dim: int = 256) -> list[float]:
    """Bag-of-words hashed into a vector: crude, but texts sharing words end up close."""
    vec = [0.0] * dim
    for word in re.findall(r"[a-z]+", text.lower()):
        if len(word) > 2:
            vec[int(hashlib.md5(word.encode()).hexdigest(), 16) % dim] += 1.0
    return vec


class FakeLLM:
    """`replies` is a queue. Each entry is a string (a text answer), a list of tool_call(...)
    (the model asking for tools), or a callable taking the request kwargs and returning either."""

    def __init__(self, replies=None):
        self.replies = list(replies or [])
        self.requests: list[dict] = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))
        self.embeddings = SimpleNamespace(create=self._embed)

    def queue(self, *replies):
        self.replies.extend(replies)
        return self

    def _create(self, **kwargs):
        self.requests.append(kwargs)
        reply = self.replies.pop(0) if self.replies else "OK."
        if callable(reply):
            reply = reply(kwargs)
        if isinstance(reply, list):
            msg = SimpleNamespace(content=None, tool_calls=reply)
        else:
            msg = SimpleNamespace(content=reply, tool_calls=None)
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)])

    def _embed(self, *, model, input, **_):
        texts = [input] if isinstance(input, str) else input
        return SimpleNamespace(data=[SimpleNamespace(embedding=bow_embedding(t)) for t in texts])
