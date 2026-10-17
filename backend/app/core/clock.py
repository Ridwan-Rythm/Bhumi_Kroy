"""Single source of 'now'. The demo console can shift it (POST /demo/clock)."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

BDT = timezone(timedelta(hours=6))
_offset_days = 0


def now() -> datetime:
    return datetime.now(BDT) + timedelta(days=_offset_days)


def set_offset_days(days: int) -> None:
    global _offset_days
    _offset_days = int(days)


def get_offset_days() -> int:
    return _offset_days


def iso(dt: datetime) -> str:
    return dt.astimezone(BDT).isoformat(timespec="seconds")


def parse_iso(text: str) -> datetime:
    return datetime.fromisoformat(text)
