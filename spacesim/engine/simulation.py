"""Simulation — wires together the clock, scheduler, world, RNG, and event log.

This is the deterministic core's driver. During a live run, events are scheduled and fired by
``advance_to`` (sub-stepped so nothing is skipped) and appended to the event log. Because every
state change is a pure function of ``(WorldState, payload, rng)`` and the event log records the
exact ordered events, the same ``(initial_state, seed, eventlog)`` always reproduces the same
final state — that is the rewind/undo/branch guarantee, asserted by the determinism property test.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from spacesim.engine.clock import ScheduledEvent, Scheduler, SimClock
from spacesim.engine.eventlog import EventLog, Snapshot
from spacesim.engine.handlers import DEFAULT_HANDLERS, EventHandler
from spacesim.engine.rng import SeededRng
from spacesim.engine.world import WorldState


class SavedSession(BaseModel):
    """The on-disk save format: enough to load, rewind, replay, and branch exactly."""

    initial_state: dict
    seed: int
    final_time: int = 0  # clock value at save time (may be past the last event)
    snapshots: list[Snapshot] = Field(default_factory=list)
    eventlog: EventLog = Field(default_factory=EventLog)


class Simulation:
    def __init__(
        self,
        world: WorldState,
        seed: int,
        handlers: dict[str, EventHandler] | None = None,
    ) -> None:
        self._initial_state = world.model_dump()
        self._seed = seed
        self.world = world
        self.clock = SimClock(world.now)
        self.rng = SeededRng(seed)
        self.scheduler = Scheduler()
        self.eventlog = EventLog()
        self.snapshots: list[Snapshot] = []
        self._handlers: dict[str, EventHandler] = dict(DEFAULT_HANDLERS)
        if handlers:
            self._handlers.update(handlers)

    # -- live run --------------------------------------------------------------
    def register_handler(self, kind: str, fn: EventHandler) -> None:
        """Register a domain event handler ``(world, payload, rng) -> None``."""
        self._handlers[kind] = fn

    def handlers(self) -> dict[str, EventHandler]:
        return dict(self._handlers)

    def schedule(self, t: int, kind: str, payload: dict | None = None, actor: str = "system") -> None:
        self.scheduler.schedule(ScheduledEvent(t=t, kind=kind, actor=actor, payload=payload or {}))

    def _apply(self, kind: str, payload: dict) -> None:
        self._handlers[kind](self.world, payload, self.rng)

    def advance_to(self, target: int) -> None:
        """Advance the clock to ``target``, firing every due event in time order (sub-stepped)."""
        if target < self.clock.now:
            raise ValueError("advance_to cannot move time backwards; use rewind/replay")
        for event in self.scheduler.pop_due(target):
            self.clock.now = event.t
            self.world.now = event.t
            self._apply(event.kind, event.payload)
            self.eventlog.append(
                sim_time=event.t, kind=event.kind, actor=event.actor, payload=event.payload
            )
        self.clock.now = target
        self.world.now = target

    def rewind_to(self, t: int) -> None:
        """Exact rewind: keep event-log entries at or before ``t``, then re-derive state from
        the initial state + seed (replaying their RNG draws), and drop pending future events.
        This is the rewind/undo/branch primitive — only sound because the core is deterministic."""
        keep_seq = -1
        for e in self.eventlog.entries:
            if e.sim_time <= t:
                keep_seq = e.seq
        if keep_seq >= 0:
            self.eventlog.truncate_after(keep_seq)
        else:
            self.eventlog.entries = []
        self._rebuild(stop_time=t)

    def undo_last(self, n: int = 1) -> None:
        """Drop the last ``n`` event-log entries and re-derive state."""
        if n > 0:
            self.eventlog.entries = self.eventlog.entries[:-n] if n < len(self.eventlog.entries) else []
        stop = self.eventlog.entries[-1].sim_time if self.eventlog.entries else 0
        self._rebuild(stop_time=stop)

    def _rebuild(self, stop_time: int) -> None:
        world = WorldState.model_validate(self._initial_state)
        self.rng = SeededRng(self._seed)
        for entry in self.eventlog.entries:
            world.now = entry.sim_time
            self._handlers[entry.kind](world, entry.payload, self.rng)
        world.now = stop_time
        self.world = world
        self.clock.now = stop_time
        self.scheduler = Scheduler()  # pending future events do not survive a rewind/branch

    def snapshot(self) -> Snapshot:
        snap = Snapshot(
            seq=len(self.eventlog),
            sim_time=self.clock.now,
            world_state=self.world.model_dump(),
            rng_state=self.rng.export_state(),
        )
        self.snapshots.append(snap)
        return snap

    # -- save / load -----------------------------------------------------------
    def to_save(self) -> SavedSession:
        return SavedSession(
            initial_state=self._initial_state,
            seed=self._seed,
            final_time=self.clock.now,
            snapshots=list(self.snapshots),
            eventlog=self.eventlog,
        )

    # -- replay (the determinism guarantee) ------------------------------------
    def replay(self, up_to_seq: int | None = None) -> WorldState:
        """Re-derive current state from the initial state + seed + event log.

        Uses the latest in-range snapshot as a shortcut when available; pins the final clock to
        the live clock so trailing idle time (no events) reproduces exactly too.
        """
        final_time = self.clock.now if up_to_seq is None else None
        return replay(
            self._initial_state,
            self._seed,
            self.eventlog,
            handlers=self._handlers,
            snapshots=self.snapshots,
            up_to_seq=up_to_seq,
            final_time=final_time,
        )


def replay(
    initial_state: dict,
    seed: int,
    eventlog: EventLog,
    handlers: dict[str, EventHandler] | None = None,
    snapshots: list[Snapshot] | None = None,
    up_to_seq: int | None = None,
    final_time: int | None = None,
) -> WorldState:
    """Reproduce world state from ``(initial_state, seed, eventlog)``.

    If snapshots are supplied, start from the latest one whose ``seq`` is within range (and not
    past ``up_to_seq``) and apply only the remaining events — otherwise start from the beginning.
    ``final_time`` pins ``world.now`` after the last event (reproducing trailing idle time);
    if omitted, ``now`` is left at the last applied event's time.
    """
    h: dict[str, EventHandler] = dict(DEFAULT_HANDLERS)
    if handlers:
        h.update(handlers)

    last_seq = len(eventlog.entries) if up_to_seq is None else up_to_seq

    start_seq = 0
    if snapshots:
        candidates = [s for s in snapshots if s.seq <= last_seq]
        if candidates:
            snap = max(candidates, key=lambda s: s.seq)
            world = WorldState.model_validate(snap.world_state)
            rng = SeededRng(seed)
            rng.import_state(snap.rng_state)
            start_seq = snap.seq
        else:
            world = WorldState.model_validate(initial_state)
            rng = SeededRng(seed)
    else:
        world = WorldState.model_validate(initial_state)
        rng = SeededRng(seed)

    for entry in eventlog.entries:
        if entry.seq < start_seq or entry.seq >= last_seq:
            continue
        world.now = entry.sim_time
        h[entry.kind](world, entry.payload, rng)
    if final_time is not None:
        world.now = final_time
    return world
