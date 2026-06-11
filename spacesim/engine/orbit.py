"""Orbit representation and Keplerian element <-> state-vector conversion.

``OrbitState`` is the serializable contract from ``04-data-model.md`` §2. Fictional assets use
Keplerian elements (propagated two-body + J2 secular precession); real named satellites use a
TLE (propagated via sgp4 in ``propagator.py``). All angles are stored in degrees at this boundary
and converted to radians for the math.
"""

from __future__ import annotations

import math
from typing import Literal, Optional

import numpy as np
from pydantic import BaseModel

from spacesim.engine.geometry import J2, MU_EARTH, R_EARTH_EQ, MICROS_PER_SECOND

Regime = Literal["LEO", "LEO_SSO", "MEO", "GEO", "HEO", "CISLUNAR"]


class OrbitState(BaseModel):
    source: Literal["kepler", "tle"] = "kepler"
    epoch: int = 0  # sim time (micros) the elements are valid at

    # Keplerian (metres / degrees)
    a_m: Optional[float] = None
    e: Optional[float] = None
    i_deg: Optional[float] = None
    raan_deg: Optional[float] = None
    argp_deg: Optional[float] = None
    ta_deg: Optional[float] = None  # true anomaly at epoch

    # TLE
    tle_line1: Optional[str] = None
    tle_line2: Optional[str] = None

    regime: Optional[Regime] = None

    def model_post_init(self, _ctx) -> None:
        if self.regime is None and self.source == "kepler" and self.a_m is not None:
            self.regime = classify_regime(self.a_m, self.e or 0.0, self.i_deg or 0.0)


def classify_regime(a_m: float, e: float, i_deg: float) -> Regime:
    apogee = a_m * (1 + e) - R_EARTH_EQ
    perigee = a_m * (1 - e) - R_EARTH_EQ
    if e > 0.25 and apogee > 30_000e3:
        return "HEO"
    if apogee > 80_000e3:
        return "CISLUNAR"
    if perigee < 2_000e3:
        # Sun-synchronous orbits are retrograde, near-polar (~96-101 deg) at LEO altitudes.
        if 95.0 <= i_deg <= 104.0:
            return "LEO_SSO"
        return "LEO"
    # GEO: semi-major axis ≈ 42,164 km (altitude ≈ 35,786 km).
    # GEO inclined / GEO transfer orbits with apogee in the GEO band also classify here.
    if 41_000e3 <= a_m <= 43_000e3 or 35_000e3 <= apogee <= 37_000e3:
        return "GEO"
    return "MEO"


def period_s(a_m: float) -> float:
    if a_m <= 0:
        return float("nan")
    return 2.0 * math.pi * math.sqrt(a_m ** 3 / MU_EARTH)


def true_to_mean(nu: float, e: float) -> float:
    ecc_anom = math.atan2(math.sqrt(1 - e * e) * math.sin(nu), e + math.cos(nu))
    return ecc_anom - e * math.sin(ecc_anom)


def _solve_kepler(mean_anom: float, e: float) -> float:
    m = (mean_anom + math.pi) % (2 * math.pi) - math.pi
    ecc = m if e < 0.8 else math.pi
    for _ in range(50):
        f = ecc - e * math.sin(ecc) - m
        ecc -= f / (1 - e * math.cos(ecc))
        if abs(f) < 1e-12:
            break
    return ecc


def _j2_rates(a: float, e: float, i: float) -> tuple[float, float, float]:
    """Secular RAAN, argument-of-perigee, and mean-anomaly rates (rad/s)."""
    n = math.sqrt(MU_EARTH / a ** 3)
    p = a * (1 - e * e)
    k = 1.5 * J2 * (R_EARTH_EQ / p) ** 2
    cos_i = math.cos(i)
    raan_dot = -n * k * cos_i
    argp_dot = 0.5 * n * k * (5 * cos_i * cos_i - 1)
    m_dot = n + 0.5 * n * k * math.sqrt(1 - e * e) * (3 * cos_i * cos_i - 1)
    return raan_dot, argp_dot, m_dot


def elements_to_rv(orbit: OrbitState, t_micros: int) -> tuple[np.ndarray, np.ndarray]:
    """Propagate Keplerian elements (with J2 secular drift) to an ECI position/velocity."""
    a = orbit.a_m
    e = orbit.e or 0.0
    i = math.radians(orbit.i_deg or 0.0)
    raan0 = math.radians(orbit.raan_deg or 0.0)
    argp0 = math.radians(orbit.argp_deg or 0.0)
    nu0 = math.radians(orbit.ta_deg or 0.0)

    dt = (t_micros - orbit.epoch) / MICROS_PER_SECOND
    raan_dot, argp_dot, m_dot = _j2_rates(a, e, i)

    raan = raan0 + raan_dot * dt
    argp = argp0 + argp_dot * dt
    mean_anom = true_to_mean(nu0, e) + m_dot * dt

    ecc_anom = _solve_kepler(mean_anom, e)
    nu = math.atan2(math.sqrt(1 - e * e) * math.sin(ecc_anom), math.cos(ecc_anom) - e)

    p = a * (1 - e * e)
    r = p / (1 + e * math.cos(nu))
    r_pf = np.array([r * math.cos(nu), r * math.sin(nu), 0.0])
    v_scale = math.sqrt(MU_EARTH / p)
    v_pf = np.array([-v_scale * math.sin(nu), v_scale * (e + math.cos(nu)), 0.0])

    cos_o, sin_o = math.cos(raan), math.sin(raan)
    cos_w, sin_w = math.cos(argp), math.sin(argp)
    cos_i, sin_i = math.cos(i), math.sin(i)
    rot = np.array([
        [cos_o * cos_w - sin_o * sin_w * cos_i, -cos_o * sin_w - sin_o * cos_w * cos_i, sin_o * sin_i],
        [sin_o * cos_w + cos_o * sin_w * cos_i, -sin_o * sin_w + cos_o * cos_w * cos_i, -cos_o * sin_i],
        [sin_w * sin_i, cos_w * sin_i, cos_i],
    ])
    return rot @ r_pf, rot @ v_pf


def rv_to_elements(r: np.ndarray, v: np.ndarray, epoch: int) -> OrbitState:
    """Osculating Keplerian elements from an ECI state vector (used after an impulse)."""
    r_mag = float(np.linalg.norm(r))
    v_mag = float(np.linalg.norm(v))
    h = np.cross(r, v)
    h_mag = float(np.linalg.norm(h))
    n_vec = np.cross([0.0, 0.0, 1.0], h)
    n_mag = float(np.linalg.norm(n_vec))

    e_vec = ((v_mag ** 2 - MU_EARTH / r_mag) * r - float(np.dot(r, v)) * v) / MU_EARTH
    e = float(np.linalg.norm(e_vec))
    energy = v_mag ** 2 / 2 - MU_EARTH / r_mag
    a = -MU_EARTH / (2 * energy)
    i = math.acos(max(-1.0, min(1.0, h[2] / h_mag)))

    if n_mag > 1e-9:
        raan = math.acos(max(-1.0, min(1.0, n_vec[0] / n_mag)))
        if n_vec[1] < 0:
            raan = 2 * math.pi - raan
    else:
        raan = 0.0

    if n_mag > 1e-9 and e > 1e-9:
        argp = math.acos(max(-1.0, min(1.0, float(np.dot(n_vec, e_vec)) / (n_mag * e))))
        if e_vec[2] < 0:
            argp = 2 * math.pi - argp
    else:
        argp = 0.0

    if e > 1e-9:
        nu = math.acos(max(-1.0, min(1.0, float(np.dot(e_vec, r)) / (e * r_mag))))
        if float(np.dot(r, v)) < 0:
            nu = 2 * math.pi - nu
    else:
        # circular: use argument of latitude as the angle
        nu = math.acos(max(-1.0, min(1.0, float(np.dot(n_vec, r)) / (n_mag * r_mag)))) if n_mag > 1e-9 else 0.0
        if r[2] < 0:
            nu = 2 * math.pi - nu

    return OrbitState(
        source="kepler",
        epoch=epoch,
        a_m=a,
        e=e,
        i_deg=math.degrees(i),
        raan_deg=math.degrees(raan) % 360.0,
        argp_deg=math.degrees(argp) % 360.0,
        ta_deg=math.degrees(nu) % 360.0,
    )
