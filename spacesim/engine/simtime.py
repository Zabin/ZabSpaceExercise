"""Simulated-UTC time.

Sim time is stored everywhere in the engine as an **integer count of microseconds since the
Unix epoch**. Integers keep arithmetic and ordering exact, which is what makes deterministic
rewind/replay byte-identical (floats would drift). ISO-8601 conversion happens only at the
serialization / display boundary.

Note: the conversion helpers below never read the wall clock — they only transform values they
are given, so they are safe inside the deterministic core.
"""

from __future__ import annotations

from datetime import datetime, timezone

MICROS_PER_SECOND = 1_000_000


def seconds(n: float) -> int:
    """Microseconds for ``n`` seconds (accepts int or float)."""
    return round(n * MICROS_PER_SECOND)


def minutes(n: float) -> int:
    return seconds(n * 60)


def hours(n: float) -> int:
    return seconds(n * 3600)


def from_iso(iso: str) -> int:
    """Parse an ISO-8601 instant into microseconds since the epoch (assumes UTC if naive)."""
    dt = datetime.fromisoformat(iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return round(dt.timestamp() * MICROS_PER_SECOND)


def to_iso(micros: int) -> str:
    """Render microseconds since the epoch as an ISO-8601 UTC string (exact, no float drift)."""
    secs, micro = divmod(micros, MICROS_PER_SECOND)
    dt = datetime.fromtimestamp(secs, tz=timezone.utc).replace(microsecond=micro)
    return dt.isoformat()
