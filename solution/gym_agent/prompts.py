"""System prompts, versioned in Langfuse (Lab 3).

The prompt text lives in Langfuse, not in your code. The agent fetches whichever version carries a
label (by default `production`), so you can roll a prompt forward or back without a deploy. The
files in `prompts/` are the starting versions, and the offline fallback if Langfuse isn't set up.

    uv run python -m gym_agent.prompts push ../prompts/system_v1.md --label production
    uv run python -m gym_agent.prompts push ../prompts/system_v2.md --label staging
    uv run python -m gym_agent.prompts promote 3          # move `production` to version 3
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import PROMPTS_DIR, SETTINGS, langfuse_enabled

DEFAULT_PROMPT_FILE = PROMPTS_DIR / "system_v3.md"


@dataclass
class SystemPrompt:
    text: str
    version: str  # "langfuse:v3", or "file:system_v2.md"
    langfuse_prompt: Any = None  # pass to the model call so the trace links to the prompt version


def load_system_prompt(label: str | None = None, prompt_file: Path | None = None) -> SystemPrompt:
    """Fetch the prompt with `label` from Langfuse, or fall back to a local file."""
    if prompt_file is not None or not langfuse_enabled():
        path = Path(prompt_file or DEFAULT_PROMPT_FILE)
        return SystemPrompt(text=path.read_text().strip(), version=f"file:{path.name}")

    from langfuse import get_client

    fallback = DEFAULT_PROMPT_FILE.read_text().strip()
    prompt = get_client().get_prompt(
        SETTINGS.prompt_name,
        label=label or SETTINGS.prompt_label,
        fallback=fallback,  # if Langfuse is unreachable, keep answering the phone
        cache_ttl_seconds=60,
    )
    version = "fallback" if prompt.is_fallback else f"langfuse:v{prompt.version}"
    return SystemPrompt(text=prompt.compile(), version=version, langfuse_prompt=prompt)


def _push(path: str, label: str | None, message: str | None) -> None:
    from langfuse import get_client

    lf = get_client()
    prompt = lf.create_prompt(
        name=SETTINGS.prompt_name,
        prompt=Path(path).read_text().strip(),
        type="text",
        labels=[label] if label else [],
        commit_message=message or f"from {Path(path).name}",
    )
    lf.flush()
    labels = f" with label '{label}'" if label else ""
    print(f"Pushed {path} as {SETTINGS.prompt_name} v{prompt.version}{labels}.")


def _promote(version: int, label: str) -> None:
    from langfuse import get_client

    lf = get_client()
    lf.update_prompt(name=SETTINGS.prompt_name, version=version, new_labels=[label])
    lf.flush()
    print(f"Label '{label}' now points at {SETTINGS.prompt_name} v{version}.")


def main() -> None:
    from .config import require

    require("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY")
    p = argparse.ArgumentParser(prog="python -m gym_agent.prompts")
    sub = p.add_subparsers(dest="cmd", required=True)
    push = sub.add_parser("push", help="create a new prompt version from a file")
    push.add_argument("file")
    push.add_argument("--label", default=None, help="e.g. production or staging")
    push.add_argument("--message", default=None, help="commit message shown in Langfuse")
    promote = sub.add_parser("promote", help="point a label at an existing version")
    promote.add_argument("version", type=int)
    promote.add_argument("--label", default="production")
    args = p.parse_args()
    if args.cmd == "push":
        _push(args.file, args.label, args.message)
    else:
        _promote(args.version, args.label)


if __name__ == "__main__":
    main()
