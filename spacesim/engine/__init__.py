"""Deterministic simulation core.

Hard invariants (enforced by ``spacesim/tests/test_import_guard.py``):
  * No imports of UI, session, or transport code.
  * No wall-clock reads (``datetime.now``/``utcnow``, ``time.time`` ...); only the sim clock.
  * No global RNG; all randomness flows through ``SeededRng`` (``rng.py``).
"""

from spacesim.engine.clock import Scheduler, SimClock
from spacesim.engine.eventlog import EventLog, EventLogEntry, Snapshot
from spacesim.engine.rng import SeededRng
from spacesim.engine.simulation import SavedSession, Simulation
from spacesim.engine.world import WorldState

__all__ = [
    "Scheduler",
    "SimClock",
    "EventLog",
    "EventLogEntry",
    "Snapshot",
    "SeededRng",
    "SavedSession",
    "Simulation",
    "WorldState",
]
