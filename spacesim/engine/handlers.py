"""Event handlers — the pure functions that mutate WorldState when an event fires.

A handler has the signature ``(world, payload, rng) -> None`` and must be a deterministic
function of its inputs (it may draw from ``rng`` but must never read the wall clock or any global
state). Phase 1 ships a tiny generic set so the determinism machinery is exercised end to end;
later phases register domain handlers (maneuver complete, window open, effect resolve, ...).
"""

from __future__ import annotations

from collections.abc import Callable

from spacesim.engine.rng import SeededRng
from spacesim.engine.world import WorldState

EventHandler = Callable[[WorldState, dict, SeededRng], None]


def _inc_counter(world: WorldState, payload: dict, rng: SeededRng) -> None:
    name = payload["name"]
    world.counters[name] = world.counters.get(name, 0) + int(payload.get("by", 1))


def _set_value(world: WorldState, payload: dict, rng: SeededRng) -> None:
    world.entities[payload["id"]] = payload["value"]


def _random_roll(world: WorldState, payload: dict, rng: SeededRng) -> None:
    """Add a d-sided die roll into a counter — exercises seeded randomness in replay."""
    sides = int(payload.get("sides", 6))
    into = payload["into"]
    world.counters[into] = world.counters.get(into, 0) + rng.randint(1, sides)


DEFAULT_HANDLERS: dict[str, EventHandler] = {
    "inc_counter": _inc_counter,
    "set_value": _set_value,
    "random_roll": _random_roll,
}
