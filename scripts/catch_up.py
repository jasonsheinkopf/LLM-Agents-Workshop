"""Catch up: start a lab from working code.

Fell behind, or joined late? This puts your `workshop/` folder in the state it should be in at the
START of a lab: every earlier lab finished, this lab and the later ones still to write.

    repo $ uv run python scripts/catch_up.py 3      # Labs 1 and 2 done; Lab 3 is yours to write

Your current files are copied to `.runtime/catch-up-backup/` first, so nothing you wrote is lost.
"""

from __future__ import annotations

import argparse
import shutil
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SOLUTION = REPO / "solution" / "gym_agent"
CHECKPOINTS = Path(__file__).resolve().parent / "checkpoints"

# The files each lab finishes. agent.py grows in Labs 1 to 5, so it has a checkpoint per lab instead.
LAB_FILES = {
    2: ["llm.py"],
    3: ["prompts.py", "evals/evaluators.py"],
    4: ["memory.py"],
    5: ["tools.py", "guardrails.py"],
    6: ["mcp_server.py"],
}
LAB_NAMES = {1: "First agent", 2: "Traces", 3: "Evals", 4: "Memory", 5: "Tools", 6: "MCP",
             7: "Ship it and make it yours"}

# What the earlier labs left behind in Langfuse and Pinecone. The script doesn't run these for you:
# they need your keys and cost a few cents. Run the ones you haven't run yet, from workshop/.
SERVICE_STEPS = {
    3: ["uv run python -m gym_agent.prompts push ../prompts/system_v1.md --label production",
        "uv run python -m gym_agent.prompts push ../prompts/system_v2.md --label staging",
        "uv run python -m gym_agent.prompts push ../prompts/system_v3.md --label staging",
        "uv run python -m gym_agent.prompts promote 3",
        "uv run python -m gym_agent.evals.upload_dataset"],
    4: ["uv run python -m gym_agent.memory ingest"],
}


def plan(lab: int) -> dict[str, Path]:
    """Map each file in workshop/gym_agent to the file that replaces it at the start of `lab`."""
    files = {name: SOLUTION / name for done in range(2, lab) for name in LAB_FILES.get(done, [])}
    files["agent.py"] = (CHECKPOINTS / f"agent_start_of_lab{lab}.py") if lab <= 5 else SOLUTION / "agent.py"
    return files


def catch_up(lab: int, target: Path, backup: Path | None) -> list[str]:
    changed = []
    for name, source in plan(lab).items():
        dest = target / name
        if dest.exists() and dest.read_text() == source.read_text():
            continue
        if backup is not None and dest.exists():
            (backup / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dest, backup / name)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        changed.append(name)
    return changed


def main() -> None:
    p = argparse.ArgumentParser(description="Put workshop/ in the state it should be in at the start of a lab.")
    p.add_argument("lab", type=int, choices=range(2, 8), metavar="LAB", help="the lab you are about to start (2 to 7)")
    p.add_argument("--target", type=Path, default=REPO / "workshop" / "gym_agent", help=argparse.SUPPRESS)
    p.add_argument("--no-backup", action="store_true", help=argparse.SUPPRESS)
    args = p.parse_args()

    backup = None if args.no_backup else REPO / ".runtime" / "catch-up-backup" / time.strftime("%Y%m%d-%H%M%S")
    changed = catch_up(args.lab, args.target, backup)

    print(f"Ready for Lab {args.lab}: {LAB_NAMES[args.lab]}.")
    if changed:
        print(f"  Replaced: {', '.join(sorted(changed))}")
        if backup is not None:
            print(f"  Your versions are saved in {backup.relative_to(REPO)}/")
    else:
        print("  Nothing to change: your code is already there.")
    print(f"  Check it:  uv run pytest {' '.join(f'tests/test_lab{n}_*.py' for n in range(1, args.lab) if n <= 6)}")

    steps = [cmd for done in range(3, args.lab) for cmd in SERVICE_STEPS.get(done, [])]
    if steps:
        print("\nEarlier labs also set things up in Langfuse and Pinecone. From workshop/, run any of")
        print("these you haven't run yet:")
        for cmd in steps:
            print(f"  {cmd}")


if __name__ == "__main__":
    main()
