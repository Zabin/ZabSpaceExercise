"""IP-1089 (FR-7450) — the one parser for the span bounds of the time-span exports.

Pure: no clock, no RNG, no engine import. A bound is an integer number of microseconds of
simulated time (an ``int``, or a digits-only string with an optional leading ``-``) or an
extended-format ISO-8601 UTC timestamp ``YYYY-MM-DDThh:mm:ss[.f{1,6}]`` + ``Z`` | ``+00:00``.
Everything else raises ``ValueError("<name>: <reason>")`` (mapped to a 400 by the routes).
"""
from __future__ import annotations

import math
import re
from typing import Union

_INT = re.compile(r"-?[0-9]+")
_ISO = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})"
                  r"(?:\.([0-9]{1,6}))?(Z|\+00:00)")
_MICROS_PER_S = 1_000_000


def _days_from_civil(y: int, m: int, d: int) -> int:
    y -= m <= 2
    era = y // 400
    yoe = y - era * 400
    doy = (153 * (m + (-3 if m > 2 else 9)) + 2) // 5 + d - 1
    doe = yoe * 365 + yoe // 4 - yoe // 100 + doy
    return era * 146097 + doe - 719468


def _month_len(y: int, m: int) -> int:
    if m == 2:
        return 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28
    return 30 if m in (4, 6, 9, 11) else 31


def parse_span_bound(value: Union[int, str, None], name: str) -> int:
    """Return ``value`` as integer microseconds of sim UTC, or raise ``ValueError`` naming ``name``."""
    if isinstance(value, bool):
        raise ValueError(f"{name}: a boolean is not a timestamp or integer microseconds")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        why = "not finite" if not math.isfinite(value) else "a float is not accepted"
        raise ValueError(f"{name}: {why}; give an ISO-8601 UTC timestamp or integer microseconds")
    if not isinstance(value, str):
        raise ValueError(f"{name}: required; give an ISO-8601 UTC timestamp or integer microseconds")
    if _INT.fullmatch(value):  # digits-only is microseconds, never a date
        try:
            return int(value)
        except ValueError:  # CPython's int-string digit limit (4300): name the bound, not the limit
            raise ValueError(f"{name}: integer microseconds has too many digits "
                             f"({len(value.lstrip('-'))}); give an ISO-8601 UTC timestamp or a "
                             f"smaller integer") from None
    m = _ISO.fullmatch(value)
    if not m:
        raise ValueError(
            f"{name}: {value!r} is not an ISO-8601 UTC timestamp (YYYY-MM-DDThh:mm:ss[.ffffff]Z "
            f"or +00:00; a zone designator is required, no other offset) or integer microseconds")
    y, mo, d, hh, mi, ss = (int(g) for g in m.groups()[:6])
    frac = m.group(7) or ""
    if not 1 <= mo <= 12 or not 1 <= d <= _month_len(y, mo):
        raise ValueError(f"{name}: {value!r} has an out-of-range date field")
    if ss == 60:
        raise ValueError(f"{name}: {value!r} is a leap second, which is not accepted")
    if hh > 23 or mi > 59 or ss > 59:
        raise ValueError(f"{name}: {value!r} has an out-of-range time field")
    secs = _days_from_civil(y, mo, d) * 86_400 + hh * 3600 + mi * 60 + ss
    return secs * _MICROS_PER_S + int(frac.ljust(6, "0") or 0)
