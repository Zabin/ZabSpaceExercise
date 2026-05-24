"""WorldState — the authoritative, serializable simulation state.

This is the deterministic core's single source of truth. Phase 1 keeps it intentionally small
(a clock value plus generic entity/counter maps) so the determinism machinery can be proven end
to end; later phases extend it with assets, orbits, custody/tracks, fuel, and bus state per
``04-data-model.md``. Keep every field JSON-serializable so snapshots/saves round-trip exactly.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class WorldState(BaseModel):
    model_config = {"extra": "forbid"}

    now: int = 0  # simulated UTC, microseconds since the epoch (see simtime.py)
    entities: dict[str, dict] = Field(default_factory=dict)
    counters: dict[str, int] = Field(default_factory=dict)

    def copy_state(self) -> "WorldState":
        return self.model_copy(deep=True)
