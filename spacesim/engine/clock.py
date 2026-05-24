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


class SimClock:
    def __init__(self, now: int = 0) -> None:
        self.now = now


class Scheduler:
    def __init__(self) -> None:
        self._heap: list[tuple[int, int, ScheduledEvent]] = []
        self._order = 0

    def schedule(self, event: ScheduledEvent) -> None:
        heapq.heappush(self._heap, (event.t, self._order, event))
        self._order += 1

    def next_time(self) -> int | None:
        return self._heap[0][0] if self._heap else None

    def pop_due(self, target: int):
        """Yield scheduled events with ``t <= target`` in (time, insertion) order."""
        while self._heap and self._heap[0][0] <= target:
            yield heapq.heappop(self._heap)[2]

    def __len__(self) -> int:
        return len(self._heap)
