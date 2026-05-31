"""Conjunction screening (FUTURE-WORK §2).

Read-only / advisory: given the live `WorldState` and a propagator, find pairs of orbital
assets whose ranges drop below a threshold within a horizon. Operators use the output to
preload ``world.entities["conjunctions"]`` (or fire a ``conjunction_warning`` inject), which
then unlocks the ``prop.collision_avoid`` catalog verb on the at-risk asset.

This module never mutates `WorldState` — it's a pure predictor like the access provider.
"""

from __future__ import annotations

import numpy as np

from spacesim.engine.world import WorldState


def predict_conjunctions(world: WorldState, propagator, horizon_s: float = 3600.0,
                         step_s: float = 30.0, threshold_km: float = 25.0) -> list[dict]:
    """Return a list of `{a, b, t_close, range_km}` for asset pairs predicted within ``threshold_km``.

    Coarse: samples each orbital asset on a fixed step and reports the minimum-range slot
    per pair when the minimum is below the threshold. Good enough for v1 advisory; a
    high-fidelity drop-in (§2) replaces propagator + step strategy without touching callers.
    """
    sats = [(aid, a) for aid, a in world.assets.items()
            if a.orbit is not None and a.health != "destroyed"]
    if len(sats) < 2:
        return []
    t0 = world.now
    n_steps = max(1, int(horizon_s * 1_000_000 / int(step_s * 1_000_000)))
    times = [t0 + i * int(step_s * 1_000_000) for i in range(n_steps + 1)]

    # Pre-propagate positions: dict[aid] = list of (t, r_eci).
    pos: dict[str, list[tuple[int, np.ndarray]]] = {}
    for aid, a in sats:
        traj = []
        for t in times:
            r, _ = propagator.rv(a.orbit, t)
            traj.append((t, r))
        pos[aid] = traj

    out: list[dict] = []
    thresh_m = threshold_km * 1000.0
    ids = [aid for aid, _ in sats]
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            best_t = None
            best_rng = float("inf")
            for k, (t, ra) in enumerate(pos[ids[i]]):
                rb = pos[ids[j]][k][1]
                d = float(np.linalg.norm(ra - rb))
                if d < best_rng:
                    best_rng = d
                    best_t = t
            if best_rng < thresh_m:
                out.append({"a": ids[i], "b": ids[j], "t_close": best_t,
                            "range_km": best_rng / 1000.0})
    return out
