"""Orbital perturbation models — drag, J3/J4, third-body, solar radiation pressure.

All pure functions: given the current state and a Δt, return a state delta in m/s²
(acceleration) or, where convenient, a small adjustment to apply to the orbit elements.
Wired in additively so callers (`HighFidelityPropagator` stub, ground-track previews,
multi-day decay estimates) can compose any subset without paying for what they don't use.

Reference: Vallado §8 (perturbations), Curtis §10 (drag and third-body).
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np

from spacesim.engine.orbit import MU_EARTH, R_EARTH_EQ


# Standard atmosphere parameters used by the exponential model.
# Each row: (altitude_km, base_density_kg/m³, scale_height_km).  From the U.S. Standard
# Atmosphere supplement; coarse but sufficient for "the LEO sat lost 0.5 km in 3 days" realism.
_ATMOS_TABLE: list[tuple[float, float, float]] = [
    (0.0,    1.225e+0,    7.249),
    (50.0,   1.0269e-3,   8.382),
    (100.0,  5.604e-7,    5.877),
    (150.0,  2.070e-9,    25.20),
    (200.0,  2.541e-10,   37.10),
    (300.0,  1.916e-11,   45.50),
    (400.0,  2.803e-12,   58.50),
    (500.0,  5.215e-13,   63.80),
    (600.0,  1.137e-13,   71.80),
    (700.0,  3.070e-14,   88.70),
    (800.0,  1.136e-14,   124.6),
    (900.0,  5.759e-15,   181.0),
    (1000.0, 3.561e-15,   268.0),
]

# Earth gravitational zonal harmonics (dimensionless).
J2 = 1.0826267e-3
J3 = -2.5327e-6
J4 = -1.6196e-6

# Sun/Moon gravitational parameters and rough mean distances from Earth (m³/s², m).
MU_SUN = 1.32712440018e20
MU_MOON = 4.9048695e12
_AU_M = 1.495978707e11
_MOON_DIST_M = 3.844e8

# Solar radiation pressure at 1 AU: 4.56e-6 N/m² (newtons per square metre exposed area).
_SRP_AT_1AU = 4.56e-6


def atmospheric_density(altitude_m: float) -> float:
    """Exponential atmosphere density (kg/m³).  Falls to ~0 above 1000 km."""
    alt_km = max(0.0, altitude_m / 1000.0)
    if alt_km >= _ATMOS_TABLE[-1][0]:
        return 0.0
    # Find the bracket and interpolate exponentially
    for i in range(len(_ATMOS_TABLE) - 1):
        h0, rho0, _H = _ATMOS_TABLE[i]
        h1, _rho1, _H1 = _ATMOS_TABLE[i + 1]
        if h0 <= alt_km < h1:
            return rho0 * math.exp(-(alt_km - h0) / _H)
    return 0.0


def drag_acceleration(r_eci: np.ndarray, v_eci: np.ndarray, ballistic_coeff: float,
                       earth_rotation_rate: float = 7.2921159e-5) -> np.ndarray:
    """Atmospheric drag acceleration vector (m/s²).

    Inputs:
        r_eci             position in ECI (m)
        v_eci             velocity in ECI (m/s)
        ballistic_coeff   Cd·A/m — the "ballistic coefficient" (m²/kg).  Larger = more drag.
        earth_rotation_rate  rotation rate of the atmosphere (rad/s)

    Uses a rotating-atmosphere assumption (v_rel = v_eci − ω × r) and the exponential model.
    """
    alt_m = float(np.linalg.norm(r_eci)) - R_EARTH_EQ
    rho = atmospheric_density(alt_m)
    if rho <= 0.0 or ballistic_coeff <= 0.0:
        return np.zeros(3)
    omega = np.array([0.0, 0.0, earth_rotation_rate])
    v_atm = np.cross(omega, r_eci)
    v_rel = v_eci - v_atm
    speed = float(np.linalg.norm(v_rel))
    if speed == 0:
        return np.zeros(3)
    return -0.5 * rho * ballistic_coeff * speed * v_rel


def j3_acceleration(r_eci: np.ndarray) -> np.ndarray:
    """J3 (pear-shaped) zonal perturbation acceleration (m/s²).

    Uses the standard axisymmetric form per Vallado Eq. 8-30: the inner
    polynomial is ``(7 sin³φ − 3 sin φ)`` (from the gradient of the J3 disturbing
    potential, **not** the potential's own P₃ inner polynomial ``(5 sin³φ −
    3 sin φ)``); the additional z-axis correction term has coefficient ``3/5``.

    Pinned by ``test_perturbations_j3_reference_state`` to a Vallado worked
    example (audit Jun 2026 corrected this from the prior ``5/3 sin³φ`` form
    inherited from the P₃ polynomial).
    """
    r_m = float(np.linalg.norm(r_eci))
    if r_m == 0:
        return np.zeros(3)
    x, y, z = float(r_eci[0]), float(r_eci[1]), float(r_eci[2])
    sin_phi = z / r_m
    inner = 7.0 * sin_phi ** 3 - 3.0 * sin_phi
    factor = -2.5 * J3 * MU_EARTH * (R_EARTH_EQ ** 3) / (r_m ** 5)
    ax = factor * inner * (x / r_m)
    ay = factor * inner * (y / r_m)
    az = factor * inner * (z / r_m) - \
         (J3 * MU_EARTH * (R_EARTH_EQ ** 3) / (r_m ** 4)) * (3.0 * sin_phi ** 2 - 0.6)
    return np.array([ax, ay, az])


def j4_acceleration(r_eci: np.ndarray) -> np.ndarray:
    """J4 zonal perturbation acceleration (m/s²)."""
    r_m = float(np.linalg.norm(r_eci))
    if r_m == 0:
        return np.zeros(3)
    sin_phi = float(r_eci[2]) / r_m
    common = (15.0 / 8.0) * J4 * MU_EARTH * (R_EARTH_EQ ** 4) / (r_m ** 6)
    # Magnitude only (radial); sufficient for the secular drift estimate the UI consumes.
    mag = common * (1 - 14.0 * sin_phi ** 2 + 21.0 * sin_phi ** 4)
    return -mag * (r_eci / r_m)


def third_body_acceleration(r_eci: np.ndarray, third_body_r: np.ndarray,
                              mu_third: float) -> np.ndarray:
    """Point-mass perturbation from a third body (Sun or Moon)."""
    rho = third_body_r - r_eci
    rho_n = float(np.linalg.norm(rho))
    r3_n = float(np.linalg.norm(third_body_r))
    if rho_n == 0 or r3_n == 0:
        return np.zeros(3)
    return mu_third * (rho / rho_n ** 3 - third_body_r / r3_n ** 3)


def srp_acceleration(r_eci: np.ndarray, sun_unit_vec: np.ndarray, srp_area_m2: float,
                      mass_kg: float, reflectivity: float = 1.3,
                      eclipse_fraction: float = 1.0) -> np.ndarray:
    """Solar radiation pressure acceleration (m/s²).

    eclipse_fraction: 1.0 = fully sunlit, 0.0 = in umbra, intermediate = penumbra (FW §10).
    """
    if srp_area_m2 <= 0.0 or mass_kg <= 0.0 or eclipse_fraction <= 0.0:
        return np.zeros(3)
    sun_norm = float(np.linalg.norm(sun_unit_vec))
    if sun_norm == 0:
        return np.zeros(3)
    sun_hat = sun_unit_vec / sun_norm
    # Approximate constant SRP at 1 AU (no inverse-square scaling — Earth's orbit eccentricity
    # is ~0.017; first-order this is invisible in PME-scale scenarios).
    force_per_area = _SRP_AT_1AU * reflectivity * eclipse_fraction
    return -(force_per_area * srp_area_m2 / mass_kg) * sun_hat


def secular_drag_decay(altitude_m: float, ballistic_coeff: float,
                         dt_s: float) -> float:
    """Estimate the secular altitude decay (m) over `dt_s` seconds at this altitude.

    Used by the UI's "projected ground track" preview so the operator sees the LEO sat
    actually losing altitude over multi-day scenarios.  Approximation: assumes constant
    circular orbit at the input altitude and uses dr/dt = -ρ·BC·v.
    """
    rho = atmospheric_density(altitude_m)
    if rho <= 0.0 or ballistic_coeff <= 0.0 or dt_s <= 0:
        return 0.0
    r = R_EARTH_EQ + altitude_m
    v = math.sqrt(MU_EARTH / r)
    # da/dt = -ρ·BC·v·a (Curtis Eq. 10.51, low-eccentricity form)
    da_dt = -rho * ballistic_coeff * v * r
    return float(da_dt * dt_s)


# ---------------------------------------------------------------------------------------------
# IP-1230 (FS-123 v1.1, ADR-0039; FR-1230/FR-4440) — space-weather index series → multipliers.
# Pure functions of declared data and sim time: no clock, no RNG. Anchors per ADR-0039 decisions
# 2-3, grounded in R131 v1.2 §3 (NOAA G-scale Kp 5-9; F10.7 ~50-300 sfu; ~10x solar-cycle density
# span at 400 km; 2-10x storm span). Linear interpolation between anchors.
# ---------------------------------------------------------------------------------------------

_F_SOLAR_ANCHORS: tuple[tuple[float, float], ...] = ((50.0, 0.3), (150.0, 1.0), (300.0, 3.0))
_F_GEO_ANCHORS: tuple[tuple[float, float], ...] = ((0.0, 1.0), (4.0, 1.0), (5.0, 2.0), (9.0, 10.0))


def _interp(anchors: tuple[tuple[float, float], ...], x: float) -> float:
    x = min(max(float(x), anchors[0][0]), anchors[-1][0])
    for (x0, y0), (x1, y1) in zip(anchors, anchors[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return anchors[-1][1]


def f_solar(f107: float) -> float:
    """Solar (F10.7) drag factor: 50/150/300 sfu → 0.3/1.0/3.0; positive values clamped to the
    [50, 300] anchor span (ADR-0039 decision 2). 150 sfu is the reference at which
    ``_ATMOS_TABLE`` applies unscaled — a declared convention, not a sourced claim."""
    return _interp(_F_SOLAR_ANCHORS, f107)


def f_geo(kp: float) -> float:
    """Geomagnetic (Kp) factor: flat 1.0 to Kp 4, then 2.0 at Kp 5 (G1) to 10.0 at Kp 9 (G5)
    (ADR-0039 decision 3)."""
    return _interp(_F_GEO_ANCHORS, kp)


def index_in_effect(series: Optional[list], t: int, key: str) -> Optional[float]:
    """The step-held value of index ``key`` at sim time ``t``: the latest entry at or before ``t``
    that carries ``key``, else ``None`` (ADR-0039 decision 1). ``series`` is the stored form
    ``[{"t": micros, "f107"?: float, "kp"?: float}, ...]`` sorted by ``t``."""
    value = None
    for entry in series or ():
        if entry["t"] > t:
            break
        if key in entry:
            value = entry[key]
    return value


def drag_multiplier(series: Optional[list], t: int) -> float:
    """``f_solar × f_geo`` at ``t``; an index not yet in effect contributes 1.0 (ADR-0039 d. 4)."""
    f107 = index_in_effect(series, t, "f107")
    kp = index_in_effect(series, t, "kp")
    return (1.0 if f107 is None else f_solar(f107)) * (1.0 if kp is None else f_geo(kp))


def anomaly_rate_multiplier(series: Optional[list], t: int) -> float:
    """``f_geo`` alone — F10.7 does not scale anomaly rate (ADR-0039 decision 5)."""
    kp = index_in_effect(series, t, "kp")
    return 1.0 if kp is None else f_geo(kp)


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def index_series_problems(entries, time_key: str, *, time_required: bool = True) -> list[str]:
    """Every problem in a declared index series (ADR-0039 decision 6), one string each; ``[]`` when
    valid. Shared by vignette load (``at_sim_s``/``t``) and the White inject boundary
    (``offset_s``, optional). Kp outside [0, 9], F10.7 ≤ 0, non-finite or non-numeric values
    (``bool`` included), an entry with neither index, and a bad time key are refused."""
    if not isinstance(entries, list):
        return ["index_series must be a list"]
    problems: list[str] = []
    for k, entry in enumerate(entries):
        where = f"entry {k}"
        if not isinstance(entry, dict):
            problems.append(f"{where} is not an object")
            continue
        if time_key in entry or time_required:
            tv = entry.get(time_key)
            if not _is_number(tv) or not math.isfinite(tv) or tv < 0:
                problems.append(f"{where}: {time_key} must be a finite number >= 0, got {tv!r}")
        if "kp" not in entry and "f107" not in entry:
            problems.append(f"{where} declares neither kp nor f107")
        if "kp" in entry:
            kp = entry["kp"]
            if not _is_number(kp) or not math.isfinite(kp) or not 0.0 <= kp <= 9.0:
                problems.append(f"{where}: kp must be a number in [0, 9], got {kp!r}")
        if "f107" in entry:
            f = entry["f107"]
            if not _is_number(f) or not math.isfinite(f) or f <= 0.0:
                problems.append(f"{where}: f107 must be a finite number > 0, got {f!r}")
    return problems
