"""Propagator — the orbit-propagation fidelity seam (``03-simulation-engine.md`` §2).

The moderate v1 implementation propagates fictional Keplerian assets analytically (two-body + J2
secular) and real TLE assets via sgp4 (lazy-imported so the engine still imports without the
optional ``orbits`` extra). Callers depend only on the ``Propagator`` Protocol, so a numerical /
high-fidelity propagator can be dropped in later without touching gameplay code.
"""

from __future__ import annotations

import math
from typing import Protocol

import numpy as np

from spacesim.engine.geometry import (
    ECIState,
    GeoPoint,
    eci_to_ecef,
    ecef_to_geodetic,
    micros_to_jd,
    MICROS_PER_SECOND,
)
from spacesim.engine.orbit import OrbitState, elements_to_rv, rv_to_elements


class Propagator(Protocol):
    def state_at(self, orbit: OrbitState, t: int) -> ECIState: ...
    def apply_impulse(self, orbit: OrbitState, dv_eci: np.ndarray, t: int) -> OrbitState: ...
    def ground_track(self, orbit: OrbitState, t0: int, t1: int, step_s: float) -> list[GeoPoint]: ...


class ModeratePropagator:
    """Kepler+J2 for fictional assets; sgp4 for TLE-backed real satellites."""

    def rv(self, orbit: OrbitState, t: int) -> tuple[np.ndarray, np.ndarray]:
        if orbit.source == "tle":
            return _tle_rv(orbit, t)
        return elements_to_rv(orbit, t)

    def state_at(self, orbit: OrbitState, t: int) -> ECIState:
        r, v = self.rv(orbit, t)
        return ECIState(t=t, r_m=r.tolist(), v_ms=v.tolist())

    def apply_impulse(self, orbit: OrbitState, dv_eci: np.ndarray, t: int) -> OrbitState:
        r, v = self.rv(orbit, t)
        return rv_to_elements(r, v + np.asarray(dv_eci, dtype=float), t)

    def ground_track(self, orbit: OrbitState, t0: int, t1: int, step_s: float = 30.0) -> list[GeoPoint]:
        step = int(step_s * MICROS_PER_SECOND)
        pts: list[GeoPoint] = []
        t = t0
        while t <= t1:
            r, _ = self.rv(orbit, t)
            pts.append(ecef_to_geodetic(eci_to_ecef(r, t)))
            t += step
        return pts


class HighFidelityPropagator:
    """Stub for the P8 high-fidelity propagator seam (FUTURE-WORK §2 / build-spec/04 §10 M8).

    Drop-in replacement for ``ModeratePropagator`` — same ``Propagator`` Protocol, higher physics:
    - Numerical integration (RK4/RK78) with solar-radiation pressure, atmospheric drag, luni-solar.
    - Full SGP4/SDP4 via Orekit or poliastro for TLE assets, with precise TEME→ECI conversion.
    - Sub-metre orbit determination precision for conjunction screening.

    To activate: pass an instance to ``AccessProvider``, ``OrderSystem``, ``BusSystem``, and
    ``SceneBuilder`` instead of ``ModeratePropagator``.  The engine is otherwise unchanged.
    """

    def state_at(self, orbit: OrbitState, t: int) -> ECIState:  # noqa: D102
        raise NotImplementedError("HighFidelityPropagator is a seam stub — implement the body")

    def apply_impulse(self, orbit: OrbitState, dv_eci: np.ndarray, t: int) -> OrbitState:  # noqa: D102
        raise NotImplementedError("HighFidelityPropagator is a seam stub — implement the body")

    def ground_track(self, orbit: OrbitState, t0: int, t1: int, step_s: float) -> list[GeoPoint]:  # noqa: D102
        raise NotImplementedError("HighFidelityPropagator is a seam stub — implement the body")


def _tle_rv(orbit: OrbitState, t: int) -> tuple[np.ndarray, np.ndarray]:
    from sgp4.api import Satrec  # lazy: optional dependency

    sat = Satrec.twoline2rv(orbit.tle_line1, orbit.tle_line2)
    jd = micros_to_jd(t)
    jd_int = math.floor(jd - 0.5) + 0.5
    fr = jd - jd_int
    err, r_km, v_kms = sat.sgp4(jd_int, fr)
    if err != 0:
        raise ValueError(f"sgp4 propagation error code {err} for TLE asset")
    # TEME treated as ECI at moderate fidelity (GMST rotation to ECEF is consistent with TEME).
    return np.array(r_km) * 1000.0, np.array(v_kms) * 1000.0
