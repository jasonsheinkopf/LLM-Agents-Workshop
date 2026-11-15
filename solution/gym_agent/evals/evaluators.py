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
    want = expected_output.get("tool")
    if not want:
        return Evaluation(name="tool_use", value=True, data_type="BOOLEAN", comment="no tool required")
    used = [t["name"] for t in output["tool_calls"]]
    return Evaluation(name="tool_use", value=want in used, data_type="BOOLEAN", comment=f"expected {want}, used {used}")


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
    """Ask the judge model whether `reply` meets the case's expectations.

    Returns {"pass": bool, "facts_covered": int, "violations": list, "reason": str}. A judge reply
    that isn't valid JSON must come back as a fail, not an exception, so one garbled verdict can't
    crash a whole experiment.
    """
    prompt = JUDGE_PROMPT.format(
        turns="\n".join(f"- {t}" for t in turns),
        reply=reply,
        facts="\n".join(f"- {f}" for f in facts) or "- (nothing specific)",
        must_not="\n".join(f"- {m}" for m in must_not) or "- (nothing specific)",
    )
    resp = client.chat.completions.create(
        model=model or SETTINGS.judge_model,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    try:
        verdict = json.loads(resp.choices[0].message.content or "{}")
    except json.JSONDecodeError:
        verdict = {}
    return {"pass": bool(verdict.get("pass")), "facts_covered": int(verdict.get("facts_covered") or 0),
            "violations": verdict.get("violations") or [], "reason": verdict.get("reason", "unparseable judge output")}


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
