"""Append-only event log and state snapshots.

The event log is the authoritative ordered history of everything that happened: every applied
event in strict ``seq`` order with its sim timestamp. Together with the initial state and the
seed it is sufficient to reproduce any later state exactly (replay), and truncating it is how
undo/branch work. Snapshots are periodic full-state captures that let replay start from a recent
point instead of the beginning. See ``03-simulation-engine.md`` §7 and ``04-data-model.md`` §7.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class EventLogEntry(BaseModel):
    seq: int  # strict ordering, 0-based and contiguous
    sim_time: int
    kind: str
    actor: str = "system"
    payload: dict = Field(default_factory=dict)
    reversible_undo: bool = True


class Snapshot(BaseModel):
    seq: int  # number of event-log entries already applied at snapshot time
    sim_time: int
    world_state: dict  # serialized WorldState
    rng_state: dict


class EventLog(BaseModel):
    entries: list[EventLogEntry] = Field(default_factory=list)

    def append(
        self,
        sim_time: int,
        kind: str,
        actor: str = "system",
        payload: dict | None = None,
        reversible_undo: bool = True,
    ) -> EventLogEntry:
        entry = EventLogEntry(
            seq=len(self.entries),
            sim_time=sim_time,
            kind=kind,
            actor=actor,
            payload=payload or {},
            reversible_undo=reversible_undo,
        )
        self.entries.append(entry)
        return entry

    def truncate_after(self, seq: int) -> None:
        """Drop entries with ``seq`` greater than the given value (undo / branch)."""
        self.entries = [e for e in self.entries if e.seq <= seq]

    def __len__(self) -> int:
        return len(self.entries)
