# Contributing

Thanks for helping make the workshop better. Issues for confusing steps are as welcome as code.

## The one rule: keep `workshop/` and `solution/` in sync

`solution/gym_agent/` is the source of truth. `workshop/gym_agent/` is the same code with the
lab-specific parts replaced by `TODO(labN)` stubs that still let the app run.

When you change the agent:

1. Change `solution/` first, and add or adjust a test in `tests/test_labN_*.py`.
2. Mirror the change in `workshop/`: copy files that have no `TODO(lab` markers verbatim, and update the stubs and their hint comments in the files that do. Keep docstrings and section headings identical in both trees, so that `diff workshop/... solution/...`, which the labs suggest when someone is stuck, shows only the exercise.
3. If you changed `agent.py`, make the same change in `scripts/checkpoints/agent_start_of_labN.py`.
   Those are `agent.py` as it stands at the start of Labs 2 to 5, used by `scripts/catch_up.py`.
4. Update the lab README if a step, a command or an expected output changed.
5. Run the checks:

```bash
uv run ruff check .
uv run pytest --impl solution                      # all labs pass on the reference; workshop/ hasn't drifted;
                                                   # every catch-up checkpoint passes its earlier labs
grep -rn "TODO(lab" workshop/ | wc -l              # stubs are still there
```

If you change `prompts/`, `data/handbook.md`, the test cases or the scoreboard in `README.md`,
check the exhibits in `leaders/handouts/`. They quote the prompts, the handbook and the scores
word for word, so that they can be printed.

CI runs the same checks on every push. Tests are offline: they use the fake model in
`tests/fakes.py` and `memory.InMemoryStore`, so contributors never need API keys.

## The README figures

The figures at the top of `README.md` are drawn by `scripts/readme_figures.py`, in a light and a
dark version. If the scoreboard or the agenda changes, edit `SCORES`, `TIME` or `BLOCKS` in that
script and run it again. Don't edit the SVG files by hand.

## Style

- Python 3.11+, formatted for `ruff` (line length 100).
- Comments explain *why*: these files are read by learners.
- Keep the fictional gym fictional: no real businesses, people, or phone numbers outside `555-01xx`.
