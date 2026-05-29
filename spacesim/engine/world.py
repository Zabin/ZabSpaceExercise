"""WorldState — the authoritative, serializable simulation state.

This is the deterministic core's single source of truth. Phase 1 keeps it intentionally small
(a clock value plus generic entity/counter maps) so the determinism machinery can be proven end
to end; later phases extend it with assets, orbits, custody/tracks, fuel, and bus state per
``04-data-model.md``. Keep every field JSON-serializable so snapshots/saves round-trip exactly.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from spacesim.engine.custody import Track
from spacesim.engine.effects import ActiveEffect, DebrisField
from spacesim.engine.entities import Asset, Sensor


class WorldState(BaseModel):
    model_config = {"extra": "forbid"}

    now: int = 0  # simulated UTC, microseconds since the epoch (see simtime.py)

    # Domain state (grows by phase; all JSON-serializable for exact snapshots/replay).
    assets: dict[str, Asset] = Field(default_factory=dict)
    sensors: dict[str, Sensor] = Field(default_factory=dict)
    tracks: list[Track] = Field(default_factory=list)
    active_effects: list[ActiveEffect] = Field(default_factory=list)
    debris: list[DebrisField] = Field(default_factory=list)
    effect_log: list[dict] = Field(default_factory=list)     # resolved outcomes (for inspection/AAR)
    consequences: list[dict] = Field(default_factory=list)   # political consequences raised
    messages: list[dict] = Field(default_factory=list)       # injects/alerts addressed to cells
    mission: dict = Field(default_factory=dict)              # vignette-level objective flags
    ssn_staged: dict = Field(default_factory=dict)           # SSN: rid → staged measurement at collect; popped at deliver

    # Generic scratch state used by the Phase-1 determinism harness.
    entities: dict[str, dict] = Field(default_factory=dict)
    counters: dict[str, int] = Field(default_factory=dict)

    def copy_state(self) -> "WorldState":
        return self.model_copy(deep=True)

    def track_for(self, owner: str, obj: str) -> Track | None:
        for tr in self.tracks:
            if tr.owner == owner and tr.object == obj:
                return tr
        return None
