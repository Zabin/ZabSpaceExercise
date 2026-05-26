"""After-action review: replay, scrub, branch-compare, exportable summary (Phase 7).

Because the engine is deterministic, AAR is *read-only* replay: from ``(initial_state, seed,
event log)`` we reconstruct the exact world at any event-log sequence number without disturbing
the live session. That powers a scrubber (jump to any decision point), branch comparison (replay
two event logs and diff the outcomes), and an exportable campaign summary.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from spacesim.content.vignette import evaluate_objectives
from spacesim.engine.simulation import replay
from spacesim.engine.world import WorldState

DECISION_KINDS = {"execute_effect", "execute_maneuver", "execute_downlink", "execute_observe", "inject",
                  "recovery_finish", "recovery_confirm"}


class AAREvent(BaseModel):
    seq: int
    sim_time: int
    kind: str
    actor: str
    summary: str


class AARReport(BaseModel):
    vignette: str
    final_time: int
    n_events: int
    timeline: list[AAREvent] = Field(default_factory=list)
    consequences: list[dict] = Field(default_factory=list)
    final_objectives: dict = Field(default_factory=dict)


def state_at(mgr, seq: Optional[int] = None) -> WorldState:
    """Read-only: reconstruct the world after applying event-log entries with ``seq < seq``."""
    return replay(
        mgr.sim._initial_state,
        mgr.sim._seed,
        mgr.sim.eventlog,
        handlers=mgr.sim.handlers(),
        up_to_seq=seq,
    )


def objectives_at(mgr, seq: Optional[int] = None) -> dict:
    world = state_at(mgr, seq)
    return evaluate_objectives(world, mgr.ctx)


def snapshot_at(mgr, seq: Optional[int] = None) -> dict:
    """A light read-only snapshot for the AAR scrubber: clock, objectives, and per-asset state."""
    world = state_at(mgr, seq)
    n = len(mgr.sim.eventlog.entries)
    return {
        "seq": n if seq is None else seq,
        "n_events": n,
        "now": world.now,
        "objectives": evaluate_objectives(world, mgr.ctx),
        "assets": [{"id": a.id, "owner": a.owner, "health": a.health,
                    "bus_mode": a.bus_state.mode if a.bus_state else None}
                   for a in world.assets.values()],
        "debris": len(world.debris),
    }


def _summarize(entry) -> str:
    p = entry.payload
    if entry.kind == "execute_effect":
        eff = p.get("effect", {})
        return f"{eff.get('category')} → {eff.get('intended_outcome')} on {eff.get('target')}"
    if entry.kind == "execute_maneuver":
        return f"maneuver {p.get('actor')} (Δv {p.get('cost', 0):.1f} m/s)"
    if entry.kind == "execute_downlink":
        return f"downlink {p.get('actor')}"
    if entry.kind == "execute_observe":
        return f"observe {p.get('object')} ({p.get('intent')})"
    if entry.kind == "inject":
        return "inject: " + "; ".join(e.get("type", "") for e in p.get("effects", []))
    if entry.kind.startswith("recovery"):
        return f"{entry.kind} {p.get('sat', '')}"
    return entry.kind


def report(mgr) -> AARReport:
    timeline = [
        AAREvent(seq=e.seq, sim_time=e.sim_time, kind=e.kind, actor=e.actor, summary=_summarize(e))
        for e in mgr.sim.eventlog.entries if e.kind in DECISION_KINDS
    ]
    return AARReport(
        vignette=mgr.vignette.id,
        final_time=mgr.sim.clock.now,
        n_events=len(mgr.sim.eventlog.entries),
        timeline=timeline,
        consequences=list(mgr.sim.world.consequences),
        final_objectives=mgr.objectives(),
    )


def compare_branches(report_a: AARReport, report_b: AARReport) -> dict:
    """Diff two branch reports: event counts and which objectives flipped."""
    flips = {}
    for side in ("blue", "red"):
        a, b = report_a.final_objectives.get(side, {}), report_b.final_objectives.get(side, {})
        for oid in set(a) | set(b):
            if a.get(oid) != b.get(oid):
                flips[f"{side}.{oid}"] = {"a": a.get(oid), "b": b.get(oid)}
    return {
        "events_a": report_a.n_events,
        "events_b": report_b.n_events,
        "objective_flips": flips,
    }
