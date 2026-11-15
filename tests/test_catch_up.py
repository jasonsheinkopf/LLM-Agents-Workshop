"""Maintainer check: `scripts/catch_up.py N` leaves working code for every lab before N.

Runs with `--impl solution` only, because it starts from the untouched starter code in workshop/.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRATCH = REPO / ".checkpoint_test"  # a sibling of workshop/, so the code finds data/ and prompts/
# Which labs still have work left in agent.py at the start of each lab.
AGENT_TODOS = {2: [2, 3, 4, 5], 3: [3, 4, 5], 4: [4, 5], 5: [5]}


@pytest.fixture
def scratch(request):
    if request.config._workshop_impl != "solution":
        pytest.skip("maintainer check: run with --impl solution")
    shutil.rmtree(SCRATCH, ignore_errors=True)
    shutil.copytree(REPO / "workshop", SCRATCH, ignore=shutil.ignore_patterns("__pycache__"))
    yield SCRATCH / "gym_agent"
    shutil.rmtree(SCRATCH, ignore_errors=True)


@pytest.mark.parametrize("lab", [2, 3, 4, 5, 6, 7])
def test_catch_up_passes_every_earlier_lab(scratch, lab):
    subprocess.run([sys.executable, "scripts/catch_up.py", str(lab), "--target", str(scratch), "--no-backup"],
                   cwd=REPO, check=True, capture_output=True)

    earlier = [str(p) for n in range(1, lab) for p in sorted((REPO / "tests").glob(f"test_lab{n}_*.py"))]
    run = subprocess.run([sys.executable, "-m", "pytest", *earlier, "--impl", SCRATCH.name,
                          "-p", "no:cacheprovider"], cwd=REPO, capture_output=True, text=True)
    assert run.returncode == 0, f"start of Lab {lab}: earlier labs fail\n{run.stdout[-2000:]}"

    agent = (scratch / "agent.py").read_text()
    for todo in AGENT_TODOS.get(lab, []):
        assert f"TODO(lab{todo})" in agent, f"start of Lab {lab}: agent.py should still leave Lab {todo} to write"
    if lab >= 6:
        assert agent == (REPO / "solution" / "gym_agent" / "agent.py").read_text()
