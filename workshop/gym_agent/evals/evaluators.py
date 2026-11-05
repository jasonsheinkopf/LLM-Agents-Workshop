"""Graders. Cheap deterministic checks first, then an LLM-as-a-judge for what code can't check.

Each evaluator follows Langfuse's experiment interface: it receives input, output, expected_output
and metadata as keyword arguments, and returns one or more `Evaluation`s.
"""

from __future__ import annotations

import json

from langfuse import Evaluation

from ..config import SETTINGS


# --------------------------------------------------------------------------- code checks
def booking_policy(*, output, expected_output, **_) -> Evaluation:
    """Did it book exactly when it should have? (Never without the caller's confirmation.)"""
    booked = bool(output["bookings"])
    want = bool(expected_output.get("should_book"))
    ok = booked == want
    why = "booked as expected" if ok and want else "correctly did not book" if ok else (
        "booked when it should not have" if booked else "did not complete the booking")
    return Evaluation(name="booking_policy", value=ok, data_type="BOOLEAN", comment=why)


def tool_use(*, output, expected_output, **_) -> Evaluation:
    """If the case expects a tool (e.g. check the schedule before answering), was it used?"""
    # TODO(lab3): expected_output["tool"] is a tool name or None. If None, pass. Otherwise pass
    #   only if that name appears in output["tool_calls"] (a list of {"name": ..., "status": ...}).
    #   Return Evaluation(name="tool_use", value=<bool>, data_type="BOOLEAN", comment=<why>).
    raise NotImplementedError("Lab 3: write tool_use (labs/03-evals/README.md)")


# --------------------------------------------------------------------------- LLM-as-a-judge
JUDGE_PROMPT = """You are grading a phone assistant for Ridgeline Climbing Gym (a fictional gym).

The caller said (in order):
{turns}

The assistant's final reply:
\"\"\"{reply}\"\"\"

A good reply MUST convey all of these points (meaning matters, not exact wording):
{facts}

A good reply must NOT do any of these:
{must_not}

Grade strictly. A reply that states a wrong price, age, time or policy fails, even if it is polite.
Reply with JSON only:
{{"facts_covered": <number of MUST points conveyed>, "violations": ["<any MUST NOT broken>"],
  "pass": <true only if every MUST point is conveyed and nothing is violated>, "reason": "<one sentence>"}}"""


def judge_reply(client, *, turns: list[str], reply: str, facts: list[str], must_not: list[str],
                model: str | None = None) -> dict:
    prompt = JUDGE_PROMPT.format(
        turns="\n".join(f"- {t}" for t in turns),
        reply=reply,
        facts="\n".join(f"- {f}" for f in facts) or "- (nothing specific)",
        must_not="\n".join(f"- {m}" for m in must_not) or "- (nothing specific)",
    )
    # TODO(lab3): ask the judge model for a verdict.
    #   1. client.chat.completions.create(model=model or SETTINGS.judge_model,
    #        messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})
    #   2. json.loads the message content (treat invalid JSON as {} so a bad reply counts as a fail)
    #   3. return {"pass": bool, "facts_covered": int, "violations": list, "reason": str}
    raise NotImplementedError(f"Lab 3: write judge_reply (labs/03-evals/README.md); prompt was {len(prompt)} chars")


def make_judge(client):
    def llm_judge(*, input, output, expected_output, **_) -> list[Evaluation]:
        v = judge_reply(client, turns=input["turns"], reply=output["reply"],
                        facts=expected_output.get("facts", []), must_not=expected_output.get("must_not", []))
        n = max(len(expected_output.get("facts", [])), 1)
        return [
            Evaluation(name="judge_pass", value=v["pass"], data_type="BOOLEAN", comment=v["reason"]),
            Evaluation(name="fact_recall", value=round(min(v["facts_covered"], n) / n, 2),
                       comment=f"violations: {v['violations']}" if v["violations"] else None),
        ]

    return llm_judge


# --------------------------------------------------------------------------- run-level summary
def pass_rates(*, item_results, **_) -> list[Evaluation]:
    """Average each boolean score across the whole run: the numbers you compare between prompts."""
    totals: dict[str, list[float]] = {}
    for r in item_results:
        for e in r.evaluations:
            if isinstance(e.value, bool | int | float):
                totals.setdefault(e.name, []).append(float(e.value))
    return [Evaluation(name=f"avg_{k}", value=round(sum(v) / len(v), 3)) for k, v in totals.items() if v]
