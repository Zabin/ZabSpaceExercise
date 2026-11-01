"""IP-1086 (Design Decision 7) — a TLE that is valid at the exercise start epoch.

Every shipped vignette starts in 2030, so the 2024 ISS TLE the older tests force-added is (correctly,
since IP-1086) refused: SGP4 cannot propagate it to the session's epoch. ``in_epoch_tle()`` returns an
ISS-like TLE fitted at a 2030 epoch with ``engine/tle_export.py::state_to_tle`` (round-trip-checked by
that module), so tests that need *a* valid TLE keep their assertions unchanged.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

from spacesim.engine import simtime
from spacesim.engine.orbit import OrbitState, elements_to_rv
from spacesim.engine.tle_export import state_to_tle

DEFAULT_EPOCH_ISO = "2030-03-15T06:00:00Z"


@lru_cache(maxsize=None)
def in_epoch_tle(epoch_iso: str = DEFAULT_EPOCH_ISO, satnum: int = 25544,
                 raan_deg: float = 247.4627, ta_deg: float = 325.0288) -> tuple[str, str]:
    """``(line1, line2)`` of an ISS-like (a=6 786 km, i=51.64 deg) TLE with epoch ``epoch_iso``."""
    t = simtime.from_iso(epoch_iso)
    orbit = OrbitState(source="kepler", epoch=t, a_m=6_786_000.0, e=0.0006703, i_deg=51.6416,
                       raan_deg=raan_deg, argp_deg=130.536, ta_deg=ta_deg)
    r, v = elements_to_rv(orbit, t)
    out = state_to_tle(np.asarray(r), np.asarray(v), t, satnum=satnum)
    return out["line1"], out["line2"]
