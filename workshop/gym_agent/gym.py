"""The (fictional) gym's data: handbook, class schedule, callers, and a tiny booking store."""

from __future__ import annotations

import json
import secrets
from dataclasses import dataclass, field
from pathlib import Path

from .config import DATA_DIR, RUNTIME_DIR

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def load_handbook() -> str:
    return (DATA_DIR / "handbook.md").read_text()


def load_classes() -> list[dict]:
    return json.loads((DATA_DIR / "schedule.json").read_text())["classes"]


def load_callers() -> dict[str, dict]:
    callers = json.loads((DATA_DIR / "callers.json").read_text())["callers"]
    return {c["caller_id"]: c for c in callers}


def describe_caller(caller_id: str) -> str:
    """One line about the caller, as the phone system would know it (from caller ID)."""
    c = load_callers().get(caller_id)
    if not c or not c.get("name"):
        return "The caller's number is not on file."
    status = f"a {c['membership']} member" if c.get("member") else "not a member"
    return f"The caller is {c['name']} ({c['phone']}), {status}."


@dataclass
class BookingStore:
    """Seat bookings on top of the schedule's starting counts.

    `path=None` keeps everything in memory (used by tests and eval runs, so experiments never
    touch your real bookings file).
    """

    path: Path | None = RUNTIME_DIR / "bookings.json"
    bookings: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.path and self.path.exists():
            self.bookings = json.loads(self.path.read_text())

    @classmethod
    def in_memory(cls) -> BookingStore:
        return cls(path=None)

    def seats_left(self, cls_: dict) -> int:
        taken = cls_["booked"] + sum(1 for b in self.bookings if b["class_id"] == cls_["id"])
        return max(cls_["capacity"] - taken, 0)

    def add(self, *, class_id: str, caller_id: str, participant_name: str, participant_age: int) -> dict:
        booking = {
            "booking_id": "RG-" + secrets.token_hex(3).upper(),
            "class_id": class_id,
            "caller_id": caller_id,
            "participant_name": participant_name,
            "participant_age": participant_age,
        }
        self.bookings.append(booking)
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(json.dumps(self.bookings, indent=2))
        return booking
