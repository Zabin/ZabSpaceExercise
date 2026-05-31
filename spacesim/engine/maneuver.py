"""Maneuver entry-mode computation — pure read-only functions.

All modes reduce to an ECI impulse vector ``dv``.  The engine's ``_h_maneuver``
always consumes a ``dv: [x, y, z]`` ECI vector; these helpers translate the
operator's chosen parameterisation into that form without touching any state.

Modes
-----
eci            Raw ECI impulse [x, y, z] m/s (current default, named for clarity).
lvlh           RTN frame: Radial / along-Track / Normal m/s.  Standard flight-ops.
finite_burn    LVLH direction unit-vector + magnitude (m/s) + duration (s, informational).
               Duration is stored in the result for AAR pulse-shape display only.
target_coe     Desired Classical Orbital Elements → single-burn velocity difference.
               Exact for coplanar changes; first-order approx for combined plane+altitude.
hohmann        Target circular altitude (km) → classic two-burn sequence.
               Returns the first burn; ``second_burn`` dict describes the deferred apoapsis
               circularisation the operator plans as a second maneuver order.
plane_change   Target inclination delta (deg) → pure normal-direction burn.
               Applies at the current position; optimal efficiency is at the node crossing.
"""
from __future__ import annotations

import math

import numpy as np

from spacesim.engine.geometry import MU_EARTH, R_EARTH_EQ
from spacesim.engine.orbit import OrbitState, rv_to_elements

__all__ = ["compute_maneuver", "lvlh_frame", "lvlh_to_eci"]


# ---------------------------------------------------------------------------
# LVLH / RTN helpers
# ---------------------------------------------------------------------------

def lvlh_frame(
    r_eci: np.ndarray,
    v_eci: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return unit vectors of the LVLH (RTN) frame.

    Convention:
      R = r̂         (radial outward from Earth centre)
      N = h / |h|   (normal to orbit plane; h = r × v)
      T = N × R     (along-track, completes the right-hand set)
    """
    r_hat = r_eci / np.linalg.norm(r_eci)
    h = np.cross(r_eci, v_eci)
    h_mag = float(np.linalg.norm(h))
    if h_mag < 1e-6:
        raise ValueError("degenerate orbit: angular momentum |h| ≈ 0")
    n_hat = h / h_mag
    t_hat = np.cross(n_hat, r_hat)
    return r_hat, t_hat, n_hat


def lvlh_to_eci(
    r_eci: np.ndarray,
    v_eci: np.ndarray,
    dv_r: float,
    dv_t: float,
    dv_n: float,
) -> np.ndarray:
    """Convert an LVLH (RTN) impulse to an ECI Δv vector."""
    r_hat, t_hat, n_hat = lvlh_frame(r_eci, v_eci)
    return dv_r * r_hat + dv_t * t_hat + dv_n * n_hat


# ---------------------------------------------------------------------------
# Orbit preview helper
# ---------------------------------------------------------------------------

def _orbit_summary(orbit: OrbitState) -> dict:
    if orbit.a_m is None:
        return {}
    r_earth_km = R_EARTH_EQ / 1000.0
    a_km = orbit.a_m / 1000.0
    e = orbit.e or 0.0
    return {
        "a_km": round(a_km, 2),
        "e": round(e, 6),
        "i_deg": round(orbit.i_deg or 0.0, 4),
        "raan_deg": round(orbit.raan_deg or 0.0, 4),
        "argp_deg": round(orbit.argp_deg or 0.0, 4),
        "alt_periapsis_km": round(a_km * (1.0 - e) - r_earth_km, 1),
        "alt_apoapsis_km": round(a_km * (1.0 + e) - r_earth_km, 1),
        "regime": orbit.regime,
    }


# ---------------------------------------------------------------------------
# Mode implementations
# ---------------------------------------------------------------------------

def _mode_eci(r: np.ndarray, v: np.ndarray, params: dict) -> np.ndarray:
    """Raw ECI impulse — existing behaviour, named for clarity."""
    dv = np.asarray(params.get("dv", [0.0, 0.0, 0.0]), dtype=float)
    if dv.shape != (3,):
        raise ValueError("eci mode: dv must be a 3-element list [x, y, z]")
    return dv


def _mode_lvlh(r: np.ndarray, v: np.ndarray, params: dict) -> np.ndarray:
    """RTN frame impulse: dv_r (radial), dv_t (along-track), dv_n (normal)."""
    return lvlh_to_eci(r, v,
                        float(params.get("dv_r", 0.0)),
                        float(params.get("dv_t", 0.0)),
                        float(params.get("dv_n", 0.0)))


def _mode_finite_burn(r: np.ndarray, v: np.ndarray, params: dict) -> np.ndarray:
    """Finite burn: LVLH thrust-direction unit-vector + scalar magnitude.

    params
    ------
    direction_r, direction_t, direction_n : float
        LVLH thrust direction (normalised internally; any non-zero vector works).
    magnitude_ms : float
        Total Δv magnitude (m/s).
    duration_s : float
        Burn duration in seconds (informational only — AAR pulse display).
    """
    d = np.array([
        float(params.get("direction_r", 0.0)),
        float(params.get("direction_t", 1.0)),
        float(params.get("direction_n", 0.0)),
    ], dtype=float)
    norm_d = float(np.linalg.norm(d))
    if norm_d < 1e-9:
        raise ValueError("finite_burn: thrust direction vector is zero")
    d_hat = d / norm_d
    magnitude = float(params.get("magnitude_ms", 0.0))
    return lvlh_to_eci(r, v, *(d_hat * magnitude))


def _mode_target_coe(
    r: np.ndarray,
    v: np.ndarray,
    orbit: OrbitState,
    params: dict,
    t: int,
    prop,
) -> np.ndarray:
    """Single-burn 'orbit surgery' to a target set of Classical Orbital Elements.

    Any element omitted from params defaults to the current orbit value.
    The burn is applied at the current position in time.  This is exact for
    coplanar manoeuvres; for combined plane + altitude changes it is a
    first-order single-burn approximation (suitable for moderate-fidelity PME).

    params
    ------
    a_km   : target semi-major axis in km  (omit to keep current)
    e      : target eccentricity            (omit to keep current)
    i_deg  : target inclination in degrees  (omit to keep current)
    raan_deg, argp_deg : RAAN / arg-of-perigee  (omit to keep current)
    """
    tgt = OrbitState(
        source="kepler",
        epoch=t,
        a_m=float(params.get("a_km", (orbit.a_m or 0.0) / 1000.0)) * 1000.0,
        e=float(params.get("e", orbit.e or 0.0)),
        i_deg=float(params.get("i_deg", orbit.i_deg or 0.0)),
        raan_deg=float(params.get("raan_deg", orbit.raan_deg or 0.0)),
        argp_deg=float(params.get("argp_deg", orbit.argp_deg or 0.0)),
        ta_deg=float(orbit.ta_deg or 0.0),   # same position in the new orbit
    )
    _, v_tgt = prop.rv(tgt, t)
    return v_tgt - v


def _mode_hohmann(r: np.ndarray, v: np.ndarray, params: dict) -> tuple[np.ndarray, dict]:
    """Hohmann transfer from the current circular-ish orbit to a target circular altitude.

    Returns ``(dv1_eci, second_burn_info)``.

    The first burn raises (or lowers) the apoapsis/periapsis.
    The second burn circularises at the target altitude; the operator issues it as a
    separate maneuver order ≈ half an orbital period later.

    params
    ------
    target_alt_km : float  — target circular altitude (km above Earth's surface)
    """
    r1 = float(np.linalg.norm(r))
    target_alt_km = float(params.get("target_alt_km", 500.0))
    r2 = target_alt_km * 1000.0 + R_EARTH_EQ

    if r2 <= R_EARTH_EQ * 0.5:
        raise ValueError("hohmann: target altitude is below Earth's surface")
    if abs(r2 - r1) < 1.0:
        raise ValueError("hohmann: current and target altitudes are the same")

    a_transfer = (r1 + r2) / 2.0
    v_t_at_r1 = math.sqrt(MU_EARTH * (2.0 / r1 - 1.0 / a_transfer))
    v_t_at_r2 = math.sqrt(MU_EARTH * (2.0 / r2 - 1.0 / a_transfer))
    v_c1 = math.sqrt(MU_EARTH / r1)
    v_c2 = math.sqrt(MU_EARTH / r2)

    dv1_mag = v_t_at_r1 - v_c1   # +ve = raise, -ve = lower
    dv2_mag = v_c2 - v_t_at_r2   # circularise at r2

    _, t_hat, _ = lvlh_frame(r, v)
    dv1_eci = dv1_mag * t_hat

    t_transfer_s = math.pi * math.sqrt(a_transfer ** 3 / MU_EARTH)

    second_burn: dict = {
        "dv_t_ms": round(dv2_mag, 4),
        "cost_ms": round(abs(dv2_mag), 4),
        "delay_s": round(t_transfer_s, 1),
        "direction": "along_track (LVLH T)",
        "note": (
            f"Issue second burn ≈{t_transfer_s / 60:.1f} min after the first, "
            f"using LVLH mode with dv_t = {dv2_mag:.3f} m/s to circularise at "
            f"{target_alt_km:.0f} km."
        ),
    }
    return dv1_eci, second_burn


def _mode_plane_change(r: np.ndarray, v: np.ndarray, params: dict) -> np.ndarray:
    """Pure inclination change via Rodrigues rotation of the velocity vector.

    Most efficient when applied at the ascending or descending node.  At an
    arbitrary position a small radial component appears; schedule at a node
    crossing for maximum propellant efficiency.

    Cost formula: |Δv| ≈ 2 v sin(Δi / 2), independent of altitude.

    params
    ------
    delta_i_deg : float  — signed inclination change in degrees (+ = increase)
    """
    delta_i = math.radians(float(params.get("delta_i_deg", 0.0)))
    r_hat = r / float(np.linalg.norm(r))
    cos_d = math.cos(delta_i)
    sin_d = math.sin(delta_i)
    # Rodrigues: rotate v by delta_i around r_hat (exact at node, approx elsewhere)
    v_rot = (v * cos_d
             + np.cross(r_hat, v) * sin_d
             + r_hat * float(np.dot(r_hat, v)) * (1.0 - cos_d))
    return v_rot - v


# ---------------------------------------------------------------------------
# Public dispatcher
# ---------------------------------------------------------------------------

def compute_maneuver(
    orbit: OrbitState,
    mode: str,
    params: dict,
    t: int,
    prop,
) -> dict:
    """Compute an ECI impulse from the operator's chosen entry mode.

    Returns a JSON-serialisable dict::

        {
          "dv":          [x, y, z],   # ECI impulse (m/s) — use as order params["dv"]
          "cost":        float,        # Δv magnitude (m/s)
          "new_orbit":   dict,         # preview of resulting orbital elements
          "second_burn": dict | None,  # Hohmann second-burn details; None for other modes
          "duration_s":  float | None, # finite_burn duration (informational)
        }
    """
    from spacesim.engine.propagator import ModeratePropagator  # avoids circular at module level
    if prop is None:
        prop = ModeratePropagator()

    r, v = prop.rv(orbit, t)
    second_burn = None
    duration_s = None

    if mode == "eci":
        dv = _mode_eci(r, v, params)
    elif mode == "lvlh":
        dv = _mode_lvlh(r, v, params)
    elif mode == "finite_burn":
        dv = _mode_finite_burn(r, v, params)
        duration_s = float(params.get("duration_s", 0.0))
    elif mode == "target_coe":
        dv = _mode_target_coe(r, v, orbit, params, t, prop)
    elif mode == "hohmann":
        dv, second_burn = _mode_hohmann(r, v, params)
    elif mode == "plane_change":
        dv = _mode_plane_change(r, v, params)
    else:
        raise ValueError(f"unknown maneuver mode: {mode!r}")

    cost = float(np.linalg.norm(dv))
    new_orbit = _orbit_summary(rv_to_elements(r, v + dv, t))

    return {
        "dv": [round(float(x), 6) for x in dv],
        "cost": round(cost, 4),
        "new_orbit": new_orbit,
        "second_burn": second_burn,
        "duration_s": duration_s,
    }
