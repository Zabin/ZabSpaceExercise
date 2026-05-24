"""Low-precision analytic Sun direction and eclipse/lighting tests.

Self-contained (no ephemeris download), deterministic, accurate to ~0.01 deg — ample for
lighting gates (optical sensors need the target sunlit and the site in darkness) and a
cylindrical eclipse model for satellite power. From the Astronomical Almanac low-precision series.
"""

from __future__ import annotations

import math

import numpy as np

from spacesim.engine.geometry import R_EARTH_EQ, micros_to_jd


def sun_unit_eci(micros: int) -> np.ndarray:
    """Unit vector toward the Sun in ECI (equatorial mean-of-date)."""
    d = micros_to_jd(micros) - 2451545.0
    mean_long = math.radians((280.460 + 0.9856474 * d) % 360.0)
    mean_anom = math.radians((357.528 + 0.9856003 * d) % 360.0)
    ecl_long = mean_long + math.radians(1.915) * math.sin(mean_anom) + math.radians(0.020) * math.sin(2 * mean_anom)
    obliquity = math.radians(23.439 - 0.0000004 * d)
    return np.array([
        math.cos(ecl_long),
        math.cos(obliquity) * math.sin(ecl_long),
        math.sin(obliquity) * math.sin(ecl_long),
    ])


def is_sunlit(r_eci_sat: np.ndarray, micros: int) -> bool:
    """Cylindrical shadow model: a satellite is sunlit unless behind Earth within its radius."""
    sun = sun_unit_eci(micros)
    proj = float(np.dot(r_eci_sat, sun))
    if proj >= 0.0:
        return True  # on the sunlit side of the terminator plane
    perp = r_eci_sat - proj * sun
    return float(np.linalg.norm(perp)) > R_EARTH_EQ
