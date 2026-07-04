"""Competency assessment: rubric-tier measurement of *how* a cell demonstrated tradecraft
(IP-2010, FS-201 / DOM-002).

Read-only analytics layer over existing engine/session state — no new gameplay mechanic, no
``WorldState`` mutation, no composite single score (ADR-0032 narrows ADR-0017's "no automated
assessment mechanism" prohibition to allow exactly this: multiple independent qualitative
dimensions, each on its own descriptive tier scale, never aggregated). First-iteration scope is
the three dimensions FS-201 §3 derives from data the engine already unambiguously produces:
**custody quality**, **window discipline**, and **belief-truth divergence**. The three deferred
dimensions (resource economy, escalation discipline, time-to-decision) are intentionally absent,
not substituted with a default (FS-201 Acceptance Criteria).

Per DOM-005 §7's validation-disclosure discipline, none of these three dimensions has undergone a
validity check beyond face validity — ``DISCLOSURE`` states that once, and every report carries it.
"""

from __future__ import annotations

from typing import Literal, Optional

import numpy as np

from spacesim.engine.custody import WEAPONS_QUALITY_THRESHOLD
from spacesim.engine.propagator import ModeratePropagator
from spacesim.session import aar

CustodyTier = Literal["speculative", "adequate", "disciplined"]
WindowTier = Literal["frequent-invalid-attempts", "occasional", "disciplined"]
DivergenceTier = Literal["high-divergence-unaware", "high-divergence-aware", "low-divergence"]

_PROP = ModeratePropagator()

# DOM-005 §7 face-validity disclosure — every reported dimension carries this verbatim (Definition
# of Done). None of the three dimensions below has been validated beyond face validity: the tier
# boundaries are first-cut, documented judgment calls (see each function's own docstring for the
# specific numbers), not empirically calibrated thresholds.
DISCLOSURE = (
    "Face validity only (DOM-005 §5) — tier boundaries below are documented first-cut design "
    "choices, not empirically validated thresholds. Not a leaderboard score; dimensions are not "
    "commensurable and are never aggregated (ADR-0032, DOM-002 §5)."
)


def _cell_decision_entries(mgr, cell: str):
    """DECISION_KINDS eventlog entries actually issued by ``cell`` (``entry.actor == cell``,
    per ``orders.py``'s ``actor=order.cell`` on every scheduled event — see ``orders.py:180`` etc.)."""
    return [e for e in mgr.sim.eventlog.entries if e.kind in aar.DECISION_KINDS and e.actor == cell]


def score_custody_quality(mgr, cell: str) -> CustodyTier:
    """Sample ``custody_confidence_at_decision`` (IP-2010 v1.1) at every moment ``cell`` actually
    acted on a tracked target — never at arbitrary intervals, and never recomputed via replay.

    Tier boundaries (first-cut, face-validity only — see ``DISCLOSURE``): the mean recorded
    confidence across all qualifying decisions is compared against ``WEAPONS_QUALITY_THRESHOLD``
    (0.8, the same number the engage gate and the operator's live track-confidence display already
    use) and a lower band of 0.5. A cell with no qualifying decisions (no order ever targeted a
    track it held) defaults to ``"speculative"`` — the most conservative reading of "no evidence of
    custody-based tradecraft," per the Definition of Done's requirement that this function always
    return a named tier, never a fourth "no data" value.
    """
    samples = [
        e.payload.get("custody_confidence_at_decision")
        for e in _cell_decision_entries(mgr, cell)
        if e.payload.get("custody_confidence_at_decision") is not None
    ]
    if not samples:
        return "speculative"
    mean_confidence = sum(samples) / len(samples)
    if mean_confidence >= WEAPONS_QUALITY_THRESHOLD:
        return "disciplined"
    if mean_confidence >= 0.5:
        return "adequate"
    return "speculative"


def score_window_discipline(mgr, cell: str) -> WindowTier:
    """Count ``issue()`` rejection attempts against successful issuances for ``cell`` across the
    exercise (``mgr.osys.orders`` — every ``issue()`` call, rejected or not, is registered there by
    ``OrderSystem.issue()``, unlike ``dry_run()`` which leaves no trace by design, so only real
    issue attempts are countable). Tier boundaries (first-cut, face-validity only — see
    ``DISCLOSURE``): 0% rejected is ``"disciplined"``, up to 20% is ``"occasional"``, above 20% is
    ``"frequent-invalid-attempts"``. A cell that issued no orders at all defaults to
    ``"disciplined"`` (no rejected attempts observed) rather than a fourth "no data" tier.
    """
    orders = [o for o in mgr.osys.orders.values() if o.cell == cell]
    if not orders:
        return "disciplined"
    rejected = sum(1 for o in orders if o.status == "rejected")
    rate = rejected / len(orders)
    if rate > 0.2:
        return "frequent-invalid-attempts"
    if rate > 0.0:
        return "occasional"
    return "disciplined"


def _position_km(orbit, t: int) -> Optional[np.ndarray]:
    if orbit is None:
        return None
    r, _ = _PROP.rv(orbit, t)
    return np.asarray(r, dtype=float) / 1000.0


def score_belief_truth_divergence(mgr, cell: str) -> DivergenceTier:
    """Classify divergence between ``cell``'s belief and ground truth at each targeted decision.

    For every ``DECISION_KINDS`` entry ``cell`` issued whose payload carries a non-``None``
    ``custody_confidence_at_decision`` (IP-2010 v1.1 — i.e. only decisions actually taken against a
    tracked target), replay to ``aar.state_at(mgr, seq=entry.seq)`` (the world exactly as it stood
    *before* this entry applied — the belief the cell acted on, and ground truth is always present
    in ``WorldState`` regardless of owner, since fog-of-war is a ``CellController``-boundary filter,
    never an engine-level state split, per ``CLAUDE.md``'s load-bearing invariants). Compare the
    believed position (the track's ``state_estimate`` propagated to ``entry.sim_time``, the same
    propagation ``scene.py``'s ``build_scene()`` already performs for the live belief map) against
    the true position (the target asset's real orbit, propagated the same way) at that instant.

    **Divergence threshold:** the track's own ``current_uncertainty_km()`` at that instant — i.e.
    "was the truth outside the uncertainty band the cell's own tool told it to expect," not an
    invented distance constant. Divergence beyond that band is "high"; within it is "low." High
    divergence then splits aware/unaware using the recorded ``custody_confidence_at_decision``
    against ``WEAPONS_QUALITY_THRESHOLD`` (the same "operator-visibly-marginal" band the engage gate
    already uses) — **the scorer reads this recorded field only; it never recomputes confidence via
    replay for this classification** (see IP-2010 v1.1's Risks for the residual disclosure this
    still carries, folded into ``DISCLOSURE`` above).

    A cell with no qualifying, geometrically-comparable decisions defaults to ``"low-divergence"``
    (no evidence of divergence observed) rather than a fourth "no data" tier. When multiple
    high-divergence decisions occur across the exercise with a mix of aware/unaware, this reports
    ``"high-divergence-aware"`` if *any* of them was aware — a facilitator debriefing a cell should
    see that a visible cue was ignored at least once, not have that fact averaged away.
    """
    high = 0
    aware = 0
    total = 0
    for e in _cell_decision_entries(mgr, cell):
        confidence = e.payload.get("custody_confidence_at_decision")
        if confidence is None:
            continue
        target = e.payload.get("object") or (e.payload.get("effect") or {}).get("target")
        if not target:
            continue
        world_then = aar.state_at(mgr, seq=e.seq)
        track = world_then.track_for(cell, target)
        true_asset = world_then.assets.get(target)
        if track is None or track.state_estimate is None or true_asset is None or true_asset.orbit is None:
            continue
        believed = _position_km(track.state_estimate, e.sim_time)
        truth = _position_km(true_asset.orbit, e.sim_time)
        if believed is None or truth is None:
            continue
        divergence_km = float(np.linalg.norm(truth - believed))
        uncertainty_km = track.current_uncertainty_km(e.sim_time)
        total += 1
        if divergence_km > uncertainty_km:
            high += 1
            if confidence < WEAPONS_QUALITY_THRESHOLD:
                aware += 1
    if total == 0 or high == 0:
        return "low-divergence"
    return "high-divergence-aware" if aware > 0 else "high-divergence-unaware"


def assessment_report(mgr) -> dict:
    """Per-cell/per-exercise rubric report: all three dimensions side-by-side, never a composite
    number (FS-201 §6's explicit non-goal). Deferred dimensions are absent, not defaulted."""
    return {
        cell: {
            "custody_quality": score_custody_quality(mgr, cell),
            "window_discipline": score_window_discipline(mgr, cell),
            "belief_truth_divergence": score_belief_truth_divergence(mgr, cell),
            "disclosure": DISCLOSURE,
        }
        for cell in ("blue", "red")
    }
