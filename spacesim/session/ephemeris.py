"""Ephemeris export — truth and cell-observed state vectors over a time span, in ECI and RIC,
serialized as CSV or CCSDS OEM (IP-1210, FR-7410/FR-7420).

Both export variants share one time-span replay mechanism (`session.aar.state_at_time`, this
package's own additive sibling of `state_at`) and one serializer — per `ADS-1500`'s System
Architecture. Truth reads ground-truth `Asset.orbit`; cell-observed reads the requesting cell's
own `Track.state_estimate`, never ground truth and never another cell's belief (`ADR-0004`).
"""

from __future__ import annotations

import io
from datetime import datetime, timezone
from typing import Optional

import numpy as np

from spacesim.engine import simtime
from spacesim.engine.maneuver import lvlh_frame
from spacesim.engine.propagator import ModeratePropagator
from spacesim.session import aar
from spacesim.session.manager import BUS_TICK_PERIOD_S

_PROP = ModeratePropagator()


def _valid_range(mgr) -> tuple[int, int]:
    """The session's own recorded range: [initial epoch, last recorded/current time]."""
    return mgr.ctx.start_epoch, mgr.sim.clock.now


def _clamp_or_reject(mgr, t1: int, t2: int) -> tuple[int, int]:
    """Design Decision 1 (IP-1210, BL-0098) — a span wholly outside the session's recorded range
    is rejected outright, naming the actual valid range; a partially-overlapping span is
    silently clamped to the overlap."""
    lo, hi = _valid_range(mgr)
    if t2 < lo or t1 > hi:
        raise ValueError(
            f"requested time span [{t1}, {t2}] is wholly outside the session's recorded range "
            f"[{lo}, {hi}]"
        )
    return max(t1, lo), min(t2, hi)


def sample_times(t1: int, t2: int, interval_s: Optional[float] = None) -> list[int]:
    """Build the list of sampled instants in ``[t1, t2]``. Design Decision 2 (IP-1210, BL-0098):
    an explicit ``interval_s`` is used as given; omitted, defaults to a coarse interval derived
    from the span itself (``span / 100``), clamped to a minimum of one bus-tick period."""
    if t2 < t1:
        return []
    span_s = (t2 - t1) / 1_000_000.0
    if interval_s is None:
        interval_s = max(span_s / 100.0, BUS_TICK_PERIOD_S) if span_s > 0 else BUS_TICK_PERIOD_S
    step = max(int(interval_s * 1_000_000), 1)
    times = []
    t = t1
    while t <= t2:
        times.append(t)
        t += step
    return times


def to_ric(r_target: np.ndarray, v_target: np.ndarray,
           r_ref: np.ndarray, v_ref: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Project the target's ECI state, relative to the reference object, onto the reference
    object's own R/T/N (RIC) basis at the same instant — reuses `engine.maneuver.lvlh_frame`
    directly, the same physical frame under different letter names (R=Radial, I=In-track≡
    Transverse, C=Cross-track≡Normal).

    BL-0136/IP-1210 remediation (VR-1210 Finding H1): the RIC frame itself rotates with the
    reference object, so the *true* RIC-relative velocity is the inertial relative velocity
    minus the frame's own rotation term, ``omega x ric_r`` — projecting the raw inertial
    relative velocity onto the RIC basis (the prior implementation) omits this term and reports
    spurious relative motion for a co-orbital, RIC-stationary neighbour. The frame's angular
    velocity vector is ``h_ref / |r_ref|^2`` along the reference orbit's normal (``n_hat``,
    conserved specific angular momentum direction/rate for any two-body orbit); expressed in the
    RIC basis this is exactly ``[0, 0, omega]`` since ``n_hat`` is the basis's own third row."""
    r_hat, t_hat, n_hat = lvlh_frame(r_ref, v_ref)
    basis = np.array([r_hat, t_hat, n_hat])
    ric_r = basis @ (r_target - r_ref)
    ric_v_inertial = basis @ (v_target - v_ref)
    h_ref = np.cross(r_ref, v_ref)
    omega = np.linalg.norm(h_ref) / np.dot(r_ref, r_ref)
    omega_cross_ric_r = np.array([-omega * ric_r[1], omega * ric_r[0], 0.0])
    ric_v = ric_v_inertial - omega_cross_ric_r
    return ric_r, ric_v


def truth_ephemeris(mgr, object_id: str, reference_id: str, t1: int, t2: int,
                     interval_s: Optional[float] = None) -> list[dict]:
    """FR-7410 — ground-truth state vectors over a time span, ECI + RIC relative to
    ``reference_id``'s own ground-truth state. No-cell (White-Cell-only) per `FR-6220`."""
    t1, t2 = _clamp_or_reject(mgr, t1, t2)
    rows: list[dict] = []
    for t in sample_times(t1, t2, interval_s):
        world = aar.state_at_time(mgr, t)
        target = world.assets.get(object_id)
        reference = world.assets.get(reference_id)
        if target is None or target.orbit is None or reference is None or reference.orbit is None:
            continue
        r_t, v_t = _PROP.rv(target.orbit, t)
        r_r, v_r = _PROP.rv(reference.orbit, t)
        ric_r, ric_v = to_ric(r_t, v_t, r_r, v_r)
        rows.append({
            "t": t, "eci_r": r_t.tolist(), "eci_v": v_t.tolist(),
            "ric_r": ric_r.tolist(), "ric_v": ric_v.tolist(),
        })
    return rows


def cell_observed_ephemeris(mgr, cell: str, object_id: str, reference_id: str, t1: int, t2: int,
                             interval_s: Optional[float] = None) -> list[dict]:
    """FR-7420 — ``cell``'s own believed state vectors over a time span. A time T at which the
    cell holds no Track on ``object_id`` produces no row for that T (an empty result, never a
    fabricated one — FR-7420's own Postcondition). The reference object resolves to ground truth
    only if it is the requesting cell's own asset; otherwise the cell's own `state_estimate`,
    never ground truth for a merely-tracked reference (`ADS-1500` Decision 5)."""
    t1, t2 = _clamp_or_reject(mgr, t1, t2)
    rows: list[dict] = []
    for t in sample_times(t1, t2, interval_s):
        world = aar.state_at_time(mgr, t)
        tr = world.track_for(cell, object_id)
        if tr is None or tr.state_estimate is None:
            continue
        r_t, v_t = _PROP.rv(tr.state_estimate, t)

        ref_asset = world.assets.get(reference_id)
        if ref_asset is not None and ref_asset.owner == cell and ref_asset.orbit is not None:
            r_r, v_r = _PROP.rv(ref_asset.orbit, t)
        else:
            ref_tr = world.track_for(cell, reference_id)
            if ref_tr is None or ref_tr.state_estimate is None:
                continue  # no reference state available to this cell at T — no row, not fabricated
            r_r, v_r = _PROP.rv(ref_tr.state_estimate, t)

        ric_r, ric_v = to_ric(r_t, v_t, r_r, v_r)
        rows.append({
            "t": t, "eci_r": r_t.tolist(), "eci_v": v_t.tolist(),
            "ric_r": ric_r.tolist(), "ric_v": ric_v.tolist(),
            "confidence": tr.current_confidence(t),
            "uncertainty_km": tr.current_uncertainty_km(t),
        })
    return rows


def write_csv(rows: list[dict]) -> str:
    """The shared CSV serializer — one row per sampled time, ECI + RIC position/velocity,
    plus the cell-observed variant's optional confidence/uncertainty columns."""
    import csv

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow([
        "t_iso", "eci_r_x_m", "eci_r_y_m", "eci_r_z_m", "eci_v_x_ms", "eci_v_y_ms", "eci_v_z_ms",
        "ric_r_x_m", "ric_r_y_m", "ric_r_z_m", "ric_v_x_ms", "ric_v_y_ms", "ric_v_z_ms",
        "confidence", "uncertainty_km",
    ])
    for row in rows:
        w.writerow([
            simtime.to_iso(row["t"]), *row["eci_r"], *row["eci_v"], *row["ric_r"], *row["ric_v"],
            row.get("confidence", ""), row.get("uncertainty_km", ""),
        ])
    return buf.getvalue()


def _ccsds_epoch(micros: int) -> str:
    """CCSDS ASCII time format for an OEM epoch — no UTC-offset suffix (implicit, per
    ``TIME_SYSTEM = UTC``), unlike ``simtime.to_iso``'s ``+00:00``-suffixed output
    (VR-1210 Finding M1)."""
    return simtime.to_iso(micros).replace("+00:00", "")


def write_oem(rows: list[dict], object_id: str) -> str:
    """The shared CCSDS OEM (Orbit Ephemeris Message) serializer, KVN form — ECI position/
    velocity only (OEM has no native RIC-relative representation, per `FR-7430`'s companion
    file); position in km, velocity in km/s, per the CCSDS OEM convention.

    BL-0136/IP-1210 remediation (VR-1210 Finding M1) — the header now conforms to the CCSDS OEM
    KVN structure: ``CREATION_DATE``/``ORIGINATOR`` precede the metadata block; ``META_START``/
    ``META_STOP`` actually wrap ``OBJECT_NAME``/``OBJECT_ID``/``CENTER_NAME``/``REF_FRAME``/
    ``TIME_SYSTEM``/``START_TIME``/``STOP_TIME`` instead of bracketing nothing; state-vector and
    ``START_TIME``/``STOP_TIME`` epochs use the CCSDS ASCII time format (no ``+00:00`` suffix);
    ``REF_FRAME`` is ``TEME`` — the engine's own documented approximation
    (`engine/propagator.py`: "TEME treated as ECI at moderate fidelity"), not the more precise
    ``EME2000`` frame the prior label implied."""
    start = _ccsds_epoch(rows[0]["t"]) if rows else ""
    stop = _ccsds_epoch(rows[-1]["t"]) if rows else ""
    lines = [
        "CCSDS_OEM_VERS = 2.0",
        f"CREATION_DATE = {datetime.now(timezone.utc).isoformat().replace('+00:00', '')}",
        "ORIGINATOR = spacesim",
        "",
        "META_START",
        f"OBJECT_NAME = {object_id}",
        f"OBJECT_ID = {object_id}",
        "CENTER_NAME = EARTH",
        "REF_FRAME = TEME",
        "TIME_SYSTEM = UTC",
        f"START_TIME = {start}",
        f"STOP_TIME = {stop}",
        "META_STOP",
        "",
    ]
    for row in rows:
        r = [x / 1000.0 for x in row["eci_r"]]
        v = [x / 1000.0 for x in row["eci_v"]]
        lines.append(
            f"{_ccsds_epoch(row['t'])} {r[0]:.6f} {r[1]:.6f} {r[2]:.6f} "
            f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}"
        )
    return "\n".join(lines) + "\n"


def write_ric_csv(rows: list[dict]) -> str:
    """FR-7430 — the companion RIC-specific export file (CCSDS OEM has no native RIC/RSW-relative
    data-line representation, only for covariance blocks; a dedicated non-OEM companion file is
    the resolution the project owner selected for `BL-0136`'s FR-7410/OEM tension). A plain CSV,
    RIC position/velocity only — the ECI-carrying `write_oem`'s companion, not a replacement for
    it; `write_csv` above already carries both ECI and RIC for the CSV export path, so this
    function exists specifically to pair with `write_oem`, which cannot."""
    import csv

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow([
        "t_iso", "ric_r_x_m", "ric_r_y_m", "ric_r_z_m", "ric_v_x_ms", "ric_v_y_ms", "ric_v_z_ms",
    ])
    for row in rows:
        w.writerow([simtime.to_iso(row["t"]), *row["ric_r"], *row["ric_v"]])
    return buf.getvalue()
