"""Simulation clock and event scheduler.

The clock holds the single authoritative ``now`` (sim-UTC microseconds). The scheduler is a
time-ordered priority queue; its key invariant is **sub-stepping**: callers advance the clock by
firing every event with ``t <= target`` in time order and never jumping past one, so a 600x
fast-forward can't skip a short LEO pass (see ``03-simulation-engine.md`` §1).

Ordering is fully deterministic: events are keyed by ``(time, insertion_index)`` where the
insertion index is a monotonic counter, so ties break by insertion order and the event payloads
themselves are never compared.
"""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field


@dataclass
class ScheduledEvent:
    t: int
    kind: str
    actor: str = "system"
    payload: dict = field(default_factory=dict)
    tag: str = ""   # optional handle (e.g. an order id) used to cancel before it fires


class SimClock:
    def __init__(self, now: int = 0) -> None:
        self.now = now


class Scheduler:
    def __init__(self) -> None:
        self._heap: list[tuple[int, int, ScheduledEvent]] = []
        self._order = 0
        self._cancelled: set[str] = set()

    def schedule(self, event: ScheduledEvent) -> None:
        heapq.heappush(self._heap, (event.t, self._order, event))
        self._order += 1

    def cancel(self, tag: str) -> None:
        """Cancel a not-yet-fired event by tag; it is silently skipped when due (never logged)."""
        if tag:
            self._cancelled.add(tag)

    def is_cancelled(self, tag: str) -> bool:
        return bool(tag) and tag in self._cancelled

    def next_time(self) -> int | None:
        return self._heap[0][0] if self._heap else None

    def pending(self) -> list["ScheduledEvent"]:
        """All not-yet-fired, non-cancelled events (for save/resume), in time order."""
        return [ev for _, _, ev in sorted(self._heap) if not self.is_cancelled(ev.tag)]

    def pop_due(self, target: int):
        """Yield due events with ``t <= target`` in order, skipping cancelled ones."""
        while self._heap and self._heap[0][0] <= target:
            event = heapq.heappop(self._heap)[2]
            if not self.is_cancelled(event.tag):
                yield event

    def __len__(self) -> int:
        return len(self._heap)
