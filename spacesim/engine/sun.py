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


# Sun's radius / Earth–Sun distance — used for the penumbral half-angle.
_SUN_RADIUS_M = 6.96340e8
_AU_M = 1.495978707e11

# Approximate angular radii (radians) as seen from a satellite near Earth.
_ALPHA_PEN = math.atan((_SUN_RADIUS_M + R_EARTH_EQ) / _AU_M)   # penumbra cone half-angle
_ALPHA_UMB = math.atan((_SUN_RADIUS_M - R_EARTH_EQ) / _AU_M)   # umbra cone half-angle


def eclipse_fraction(r_eci_sat: np.ndarray, micros: int) -> float:
    """Sunlit fraction in [0, 1].

    1.0 — fully sunlit (no Earth occultation)
    0.0 — full umbra (Earth completely blocks the Sun)
    intermediate — penumbral (partial occlusion), linearly interpolated between
                   the umbra and penumbra cone radii at the satellite's distance.

    Used by `engine/bus.py` to ramp battery drain smoothly through terminator
    crossings instead of binary-switching (FW §11.B.10).
    """
    sun = sun_unit_eci(micros)
    proj = float(np.dot(r_eci_sat, sun))
    if proj >= 0.0:
        return 1.0  # on the sunlit side of Earth
    # Distance from the anti-sun axis (cylindrical, scaled for cone widening)
    perp = r_eci_sat - proj * sun
    perp_dist = float(np.linalg.norm(perp))
    behind_dist = -proj  # how far behind Earth's center along anti-sun axis
    # Cone radii at this distance (penumbra widens, umbra narrows behind Earth)
    r_umb = R_EARTH_EQ - behind_dist * math.tan(_ALPHA_UMB)
    r_pen = R_EARTH_EQ + behind_dist * math.tan(_ALPHA_PEN)
    if perp_dist >= r_pen:
        return 1.0   # outside the penumbra
    if perp_dist <= max(0.0, r_umb):
        return 0.0   # inside the umbra
    if r_pen <= r_umb:
        return 0.0
    return float((perp_dist - r_umb) / (r_pen - r_umb))


def cats_phase_angle_deg(r_target_eci: np.ndarray, r_chaser_eci: np.ndarray, micros: int) -> float:
    """The CATS (Camera/Chase-Target-Sun) illumination phase angle, in degrees [0, 180]
    (IP-1300, FR-8220; grounded in R109 v1.3 §3.11): the angle *at the target* between the
    target->Sun vector and the target->chaser vector. 0 deg = fully lit as seen from the chaser,
    90 deg = side-lit, 180 deg = backlit / silhouetted.

    The Sun is treated as being at infinity (target->Sun == ``sun_unit_eci``), consistent with
    every other lighting primitive in this module; the parallax this neglects is below ~0.02 deg
    even at GEO. Pure and deterministic. This is the single shared phase-angle function for the
    engine (BL-0152): the display overlay (FR-8220) and any future access predicate (FR-1670)
    must both call it rather than re-deriving the geometry.
    """
    to_chaser = np.asarray(r_chaser_eci, dtype=float) - np.asarray(r_target_eci, dtype=float)
    dist = float(np.linalg.norm(to_chaser))
    if dist == 0.0:
        raise ValueError("chaser and target positions coincide; phase angle is undefined")
    cos_angle = float(np.dot(sun_unit_eci(micros), to_chaser / dist))
    return math.degrees(math.acos(max(-1.0, min(1.0, cos_angle))))
