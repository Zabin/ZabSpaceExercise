"""Deterministic simulation core.

Hard invariants (enforced by ``spacesim/tests/test_import_guard.py``):
  * No imports of UI, session, or transport code.
  * No wall-clock reads (``datetime.now``/``utcnow``, ``time.time`` ...); only the sim clock.
  * No global RNG; all randomness flows through ``SeededRng`` (``rng.py``).
"""

from spacesim.engine.access import (
    AccessConfig,
    AccessProvider,
    AccessWindow,
    Scene,
    COMMAND_UPLINK,
    TELEMETRY_DOWNLINK,
    SENSOR_OBSERVATION,
    JAM_FOOTPRINT,
    WEAPON_ENGAGEMENT,
    RPO_PROXIMITY,
)
from spacesim.engine.clock import Scheduler, SimClock
from spacesim.engine.custody import Track, WEAPONS_QUALITY_THRESHOLD, observe
from spacesim.engine.effects import (
    ActiveEffect,
    DebrisField,
    EffectInstance,
    EffectOutcome,
    ModerateEffectResolver,
    is_link_denied,
)
from spacesim.engine.entities import Asset, AssetResources, GroundSite, Sensor
from spacesim.engine.eventlog import EventLog, EventLogEntry, Snapshot
from spacesim.engine.geometry import ECIState, GeoPoint
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import Order, OrderSystem, scene_from_world
from spacesim.engine.propagator import ModeratePropagator, Propagator
from spacesim.engine.rng import SeededRng
from spacesim.engine.simulation import SavedSession, Simulation
from spacesim.engine.world import WorldState

__all__ = [
    "AccessConfig",
    "AccessProvider",
    "AccessWindow",
    "Scene",
    "COMMAND_UPLINK",
    "TELEMETRY_DOWNLINK",
    "SENSOR_OBSERVATION",
    "JAM_FOOTPRINT",
    "WEAPON_ENGAGEMENT",
    "RPO_PROXIMITY",
    "Scheduler",
    "SimClock",
    "Track",
    "WEAPONS_QUALITY_THRESHOLD",
    "observe",
    "ActiveEffect",
    "DebrisField",
    "EffectInstance",
    "EffectOutcome",
    "ModerateEffectResolver",
    "is_link_denied",
    "Asset",
    "AssetResources",
    "Order",
    "OrderSystem",
    "scene_from_world",
    "GroundSite",
    "Sensor",
    "EventLog",
    "EventLogEntry",
    "Snapshot",
    "ECIState",
    "GeoPoint",
    "OrbitState",
    "ModeratePropagator",
    "Propagator",
    "SeededRng",
    "SavedSession",
    "Simulation",
    "WorldState",
]
