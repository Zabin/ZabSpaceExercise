"""Current-epoch TLE generation from an ECI state (IP-1211, FR-7440 — `BL-0110` Design Decision 1).

A Two-Line Element set encodes SGP4 *mean* elements, while the engine's Kepler+J2 path carries
*osculating* elements — so a TLE cannot be produced by writing the engine's elements straight into
the fixed-width fields. Instead this module fits SGP4 mean elements to a single ECI state at a
single epoch:

1. Express the target state in non-singular **equinoctial** elements ``(a, h, k, p, q, λ)``,
   computed directly from ``(r, v)`` — not via ``orbit.rv_to_elements``, which collapses the true
   anomaly for circular-equatorial states — so ``e → 0`` and ``i → 0`` stay well-conditioned.
2. Iterative correction: build an SGP4 record from the current mean-element guess, evaluate it at
   ``tsince = 0``, convert its output to equinoctial elements the same way, and correct the guess
   from the residual ``target − current`` — a Newton step, falling back to the plain fixed-point
   step, each step-halved and accepted only if it reduces the state residual (see
   ``_fit_mean_elements``). Bounded iteration count; deterministic.
3. Format with the ``sgp4`` library's own ``export_tle`` (no hand-rolled fixed-width writer), parse
   the lines back, and measure the round-trip position residual at the TLE's own epoch; anything
   outside ``ROUND_TRIP_BOUND_M`` is rejected rather than emitted.

Limitation (stated to the operator verbatim via ``LIMITATION_NOTE``): the TLE matches the state *at
its epoch*; away from epoch, SGP4 and the engine's Kepler+J2 model diverge (ADR-0009 moderate
fidelity). Pure: no world access, no RNG, no wall clock; ``sgp4`` is lazy-imported (optional
dependency) exactly as ``propagator._tle_rv`` does.
"""

from __future__ import annotations

import math
from typing import Optional

import numpy as np

from spacesim.engine.geometry import MU_EARTH, R_EARTH_EQ, micros_to_jd
from spacesim.engine.orbit import OrbitState, true_to_mean

ROUND_TRIP_BOUND_M = 1000.0      # IP-1211 Design Decision 1 / FS-121 AC6
PLACEHOLDER_SATNUM = 99999       # Design Decision 2: analyst/unknown-object placeholder
MAX_ITERATIONS = 50
_MAX_HALVINGS = 12
_CONVERGED_M = 0.01
# Forward-difference steps for the Jacobian: a (m), then k, h, Q, P, λ (dimensionless / rad).
_FD_STEP = np.array([1.0, 1e-7, 1e-7, 1e-7, 1e-7, 1e-7])
_JD_1949_DEC_31 = 2433281.5      # SGP4's epoch origin (days since 1949-12-31 00:00 UT)
_TWO_PI = 2.0 * math.pi

LIMITATION_NOTE = (
    "Fitted SGP4 mean elements matching the state at the TLE epoch; propagated away from epoch, "
    "SGP4 and the simulator's Kepler+J2 model diverge (moderate fidelity)."
)


def _equinoctial_from_rv(r: np.ndarray, v: np.ndarray) -> np.ndarray:
    """``(a, k, h, Q, P, λ)``: k = e·cos(ω+Ω), h = e·sin(ω+Ω), Q = tan(i/2)·cos Ω,
    P = tan(i/2)·sin Ω, λ = mean longitude. Non-singular for e = 0 and i = 0."""
    hv = np.cross(r, v)
    hh = hv / np.linalg.norm(hv)
    denom_i = 1.0 + hh[2]
    if denom_i < 1e-12:
        raise ValueError("exactly retrograde-equatorial orbit (i = 180°) cannot be represented")
    p_eq = hh[0] / denom_i       # tan(i/2) sin Ω
    q_eq = -hh[1] / denom_i      # tan(i/2) cos Ω
    den = 1.0 + p_eq * p_eq + q_eq * q_eq
    f_hat = np.array([1.0 - p_eq * p_eq + q_eq * q_eq, 2.0 * p_eq * q_eq, -2.0 * p_eq]) / den
    g_hat = np.array([2.0 * p_eq * q_eq, 1.0 + p_eq * p_eq - q_eq * q_eq, 2.0 * q_eq]) / den
    r_mag = float(np.linalg.norm(r))
    e_vec = ((float(v @ v) - MU_EARTH / r_mag) * r - float(r @ v) * v) / MU_EARTH
    k = float(e_vec @ f_hat)
    h = float(e_vec @ g_hat)
    a = -MU_EARTH / (2.0 * (float(v @ v) / 2.0 - MU_EARTH / r_mag))
    e = math.hypot(h, k)
    lon_peri = math.atan2(h, k)
    true_lon = math.atan2(float(r @ g_hat), float(r @ f_hat))
    mean_lon = true_to_mean(true_lon - lon_peri, e) + lon_peri
    return np.array([a, k, h, q_eq, p_eq, mean_lon])


def _classical_from_equinoctial(q: np.ndarray) -> tuple[float, float, float, float, float, float]:
    """``(a, e, i, Ω, ω, M)`` in metres/radians, angles normalised to [0, 2π)."""
    a, k, h, q_eq, p_eq, mean_lon = (float(x) for x in q)
    e = math.hypot(h, k)
    raan = math.atan2(p_eq, q_eq) % _TWO_PI
    inc = 2.0 * math.atan(math.hypot(p_eq, q_eq))
    lon_peri = math.atan2(h, k)
    return a, e, inc, raan, (lon_peri - raan) % _TWO_PI, (mean_lon - lon_peri) % _TWO_PI


def _satrec(elements, epoch_sgp4: float, satnum: int, classification: str, intldesg: str,
            bstar: float):
    from sgp4.api import Satrec, WGS72  # lazy: optional dependency

    a, e, inc, raan, argp, mean_anom = elements
    if not (0.0 <= e < 1.0) or a <= 0.0:
        raise ValueError(f"fit left the elliptic domain (a={a:.0f} m, e={e:.4f})")
    n_rad_per_min = math.sqrt(MU_EARTH / a ** 3) * 60.0
    sat = Satrec()
    sat.sgp4init(WGS72, "i", int(satnum), epoch_sgp4, float(bstar), 0.0, 0.0,
                 e, argp, inc, mean_anom, n_rad_per_min, raan)
    sat.classification = classification or "U"
    sat.intldesg = intldesg or ""
    return sat


def _wrapped_residual(target: np.ndarray, current: np.ndarray) -> np.ndarray:
    d = target - current
    d[5] = (d[5] + math.pi) % _TWO_PI - math.pi
    return d


def _evaluate(guess: np.ndarray, epoch_sgp4: float, ident: tuple):
    """SGP4 state at ``tsince = 0`` for a mean-element guess → ``(equinoctial, r_m, v_ms)``.
    Raises ``ValueError`` if the guess is not a valid SGP4 element set."""
    sat = _satrec(_classical_from_equinoctial(guess), epoch_sgp4, *ident)
    err, r_km, v_kms = sat.sgp4_tsince(0.0)
    if err != 0:
        raise ValueError(f"SGP4 error code {err} while fitting mean elements")
    r_fit = np.array(r_km) * 1000.0
    v_fit = np.array(v_kms) * 1000.0
    return _equinoctial_from_rv(r_fit, v_fit), r_fit, v_fit


def _fit_mean_elements(r: np.ndarray, v: np.ndarray, target: np.ndarray, epoch_sgp4: float,
                       ident: tuple) -> np.ndarray:
    """Solve ``equinoctial(SGP4(guess, tsince=0)) = target`` for the mean-element ``guess``.

    Safeguarded iteration: each pass tries a Newton step (forward-difference Jacobian) and then
    the plain fixed-point step ``target − current``, each with step-halving, and accepts the first
    candidate that strictly reduces the state residual ``|Δr| + 1000 s·|Δv|``. The plain
    fixed-point iteration alone diverges for near-equatorial deep-space (GEO) states, where SDP4's
    lunisolar terms are ill-conditioned; the monotone acceptance makes the result never worse
    than the starting guess. Bounded (``MAX_ITERATIONS``) and fully deterministic."""
    guess = target.copy()
    current, r_fit, v_fit = _evaluate(guess, epoch_sgp4, ident)
    cost = float(np.linalg.norm(r_fit - r) + 1000.0 * np.linalg.norm(v_fit - v))
    for _ in range(MAX_ITERATIONS):
        if float(np.linalg.norm(r_fit - r)) < _CONVERGED_M:
            break
        fixed_point = _wrapped_residual(target, current)
        candidates = []
        try:
            jac = np.zeros((6, 6))
            for j in range(6):
                probe = guess.copy()
                probe[j] += _FD_STEP[j]
                jac[:, j] = _wrapped_residual(_evaluate(probe, epoch_sgp4, ident)[0], current) / _FD_STEP[j]
            candidates.append(np.linalg.solve(jac, fixed_point))
        except (np.linalg.LinAlgError, ValueError):
            pass
        candidates.append(fixed_point)
        improved = False
        for step in candidates:
            scale = 1.0
            for _ in range(_MAX_HALVINGS):
                trial = guess + scale * step
                scale *= 0.5
                try:
                    t_cur, t_r, t_v = _evaluate(trial, epoch_sgp4, ident)
                except ValueError:
                    continue
                t_cost = float(np.linalg.norm(t_r - r) + 1000.0 * np.linalg.norm(t_v - v))
                if t_cost < cost:
                    guess, current, r_fit, v_fit, cost = trial, t_cur, t_r, t_v, t_cost
                    improved = True
                    break
            if improved:
                break
        if not improved:
            break
    return guess


def tle_identity(orbit: OrbitState) -> dict:
    """Design Decision 2 — TLE line-1 identity + B* for an exported orbit.

    A TLE-sourced orbit carries its original catalog number, classification, international
    designator and B* forward; anything else (Kepler+J2 — fictional assets, or a TLE object after a
    manoeuvre re-expressed it as osculating elements) gets the ``99999`` placeholder, class ``U``,
    a blank designator and B* = 0 (the engine models no drag)."""
    if orbit.source == "tle" and orbit.tle_line1 and orbit.tle_line2:
        from sgp4.api import Satrec  # lazy: optional dependency

        src = Satrec.twoline2rv(orbit.tle_line1, orbit.tle_line2)
        return {"satnum": int(src.satnum), "classification": (src.classification or "U").strip() or "U",
                "intldesg": (src.intldesg or "").strip(), "bstar": float(src.bstar)}
    return {"satnum": PLACEHOLDER_SATNUM, "classification": "U", "intldesg": "", "bstar": 0.0}


def state_to_tle(r_m, v_ms, t_micros: int, *, satnum: int = PLACEHOLDER_SATNUM,
                 classification: str = "U", intldesg: str = "", bstar: float = 0.0) -> dict:
    """Fit a current-epoch TLE to the ECI (TEME-as-ECI, per ``propagator``) state ``(r_m, v_ms)``
    at sim time ``t_micros``. Returns ``{"line1", "line2", "fit_error_m"}``; raises ``ValueError``
    for a non-elliptic state, a sub-surface perigee, an SGP4 error, or a fit outside
    ``ROUND_TRIP_BOUND_M``."""
    from sgp4.api import Satrec  # lazy: optional dependency
    from sgp4.exporter import export_tle

    r = np.asarray(r_m, dtype=float)
    v = np.asarray(v_ms, dtype=float)
    energy = float(v @ v) / 2.0 - MU_EARTH / float(np.linalg.norm(r))
    if energy >= 0.0:
        raise ValueError("state is not a closed (elliptic) orbit — cannot be expressed as a TLE")
    target = _equinoctial_from_rv(r, v)
    a0, e0 = target[0], math.hypot(target[1], target[2])
    if a0 * (1.0 - e0) <= R_EARTH_EQ:
        raise ValueError("orbit perigee is below the Earth's surface — cannot be expressed as a TLE")

    epoch_sgp4 = micros_to_jd(t_micros) - _JD_1949_DEC_31
    ident = (satnum, classification, intldesg, bstar)
    guess = _fit_mean_elements(r, v, target, epoch_sgp4, ident)

    sat = _satrec(_classical_from_equinoctial(guess), epoch_sgp4, *ident)
    line1, line2 = export_tle(sat)
    check = Satrec.twoline2rv(line1, line2)
    err, r_km, _ = check.sgp4(check.jdsatepoch, check.jdsatepochF)
    if err != 0:
        raise ValueError(f"SGP4 error code {err} evaluating the exported TLE")
    fit_error_m = float(np.linalg.norm(np.array(r_km) * 1000.0 - r))
    if not fit_error_m <= ROUND_TRIP_BOUND_M:
        raise ValueError(f"TLE fit did not converge within {ROUND_TRIP_BOUND_M:.0f} m "
                         f"(residual {fit_error_m:.0f} m)")
    return {"line1": line1, "line2": line2, "fit_error_m": fit_error_m}


def orbit_to_tle(orbit: OrbitState, r_m, v_ms, t_micros: int,
                 identity: Optional[dict] = None) -> dict:
    """Convenience: ``state_to_tle`` with ``orbit``'s Design-Decision-2 identity."""
    return state_to_tle(r_m, v_ms, t_micros, **(identity or tle_identity(orbit)))
