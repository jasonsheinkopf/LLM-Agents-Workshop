"""Maintainer check: workshop/ and solution/ may differ only in files that contain TODO(labN) stubs."""

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_workshop_and_solution_stay_in_sync():
    sol, ws = REPO / "solution" / "gym_agent", REPO / "workshop" / "gym_agent"
    sol_files = {p.relative_to(sol) for p in sol.rglob("*.py")}
    ws_files = {p.relative_to(ws) for p in ws.rglob("*.py")}
    assert sol_files == ws_files, f"file lists differ: {sorted(map(str, sol_files ^ ws_files))}"
    drifted = [str(f) for f in sorted(sol_files)
               if "TODO(lab" not in (ws / f).read_text() and (ws / f).read_text() != (sol / f).read_text()]
    assert not drifted, f"these files have no TODOs but differ from the solution: {drifted}"
