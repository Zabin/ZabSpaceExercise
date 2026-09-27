"""IP-1062 (FR-4430) — the four new inject effect types: anomaly, sensor_outage,
forced_custody_loss, scripted_manoeuvre. Plus Sensor.health's default/AccessProvider-filter
regression these effects depend on."""
from __future__ import annotations

import numpy as np
import pytest

from spacesim.content.vignette import Vignette
from spacesim.engine.bus import BusState
from spacesim.engine.custody import Track
from spacesim.engine.entities import Asset, Sensor
from spacesim.engine.geometry import R_EARTH_EQ
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import scene_from_world
from spacesim.session.manager import SessionManager

_LEO_A = R_EARTH_EQ + 550e3


def _bare_manager() -> SessionManager:
    """An unstarted SessionManager with no forces — used purely as a host for the effect
    dispatch helper (`_apply_inject_effects`) and its own `osys.prop`, populated by hand
    afterward so effect tests don't need to go through Vignette YAML orbit-key mapping."""
    raw = {
        "id": "test-inject-effects-v2", "title": "Effects v2",
        "start_epoch_utc": "2030-01-01T00:00:00Z",
        "blue_forces": [], "red_forces": [], "neutral_forces": [], "sensors": [],
    }
    return SessionManager(Vignette.model_validate(raw), seed=0)


def _orbit(ta_deg: float = 0.0) -> OrbitState:
    return OrbitState(a_m=_LEO_A, e=0.0, i_deg=51.6, raan_deg=0.0, argp_deg=0.0, ta_deg=ta_deg, epoch=0)


# -- Sensor.health default + AccessProvider filter regression --------------------------------

def test_sensor_health_defaults_to_nominal_when_absent_from_yaml():
    sensor = Sensor.model_validate({"id": "S-1", "owner": "blue"})
    assert sensor.health == "nominal"


def test_scene_from_world_excludes_degraded_sensor():
    mgr = _bare_manager()
    mgr.world.sensors["S-1"] = Sensor(id="S-1", owner="blue", health="nominal")
    mgr.world.sensors["S-2"] = Sensor(id="S-2", owner="blue", health="degraded")
    scene = scene_from_world(mgr.world)
    assert "S-1" in scene.sensors
    assert "S-2" not in scene.sensors


# -- anomaly -----------------------------------------------------------------------------------

def test_anomaly_bus_subsystem_sets_safe_mode_and_restore_clears_it():
    mgr = _bare_manager()
    mgr.world.assets["SAT-1"] = Asset(id="SAT-1", owner="blue", bus_state=BusState())
    mgr._apply_inject_effects(mgr.world, [
        {"type": "anomaly", "target": "SAT-1", "subsystem": "bus", "cause": "test cause"},
    ], mgr.sim.rng)
    assert mgr.world.assets["SAT-1"].bus_state.mode == "safe_mode"
    assert any("test cause" in m["text"] for m in mgr.world.messages)

    mgr._apply_inject_effects(mgr.world, [
        {"type": "anomaly", "target": "SAT-1", "subsystem": "bus", "restore": True},
    ], mgr.sim.rng)
    assert mgr.world.assets["SAT-1"].bus_state.mode == "nominal"


def test_anomaly_telemetry_subsystem_degrades_comms():
    mgr = _bare_manager()
    mgr.world.assets["SAT-1"] = Asset(id="SAT-1", owner="blue", bus_state=BusState())
    mgr._apply_inject_effects(mgr.world, [
        {"type": "anomaly", "target": "SAT-1", "subsystem": "telemetry", "cause": "jam-like"},
    ], mgr.sim.rng)
    assert mgr.world.assets["SAT-1"].bus_state.comms.status == "red"
    mgr._apply_inject_effects(mgr.world, [
        {"type": "anomaly", "target": "SAT-1", "subsystem": "telemetry", "restore": True},
    ], mgr.sim.rng)
    assert mgr.world.assets["SAT-1"].bus_state.comms.status == "green"


# -- sensor_outage -----------------------------------------------------------------------------

def test_sensor_outage_degrades_and_restore_clears():
    mgr = _bare_manager()
    mgr.world.sensors["S-1"] = Sensor(id="S-1", owner="blue")
    mgr._apply_inject_effects(mgr.world, [
        {"type": "sensor_outage", "target": "S-1", "cause": "antenna damage"},
    ], mgr.sim.rng)
    assert mgr.world.sensors["S-1"].health == "degraded"
    mgr._apply_inject_effects(mgr.world, [
        {"type": "sensor_outage", "target": "S-1", "restore": True},
    ], mgr.sim.rng)
    assert mgr.world.sensors["S-1"].health == "nominal"


# -- forced_custody_loss ------------------------------------------------------------------------

def test_forced_custody_loss_degrade_sets_confidence():
    mgr = _bare_manager()
    mgr.world.tracks.append(Track(object="SAT-RED", owner="blue", confidence=1.0, last_observation=0))
    mgr._apply_inject_effects(mgr.world, [
        {"type": "forced_custody_loss", "cell": "blue", "target": "SAT-RED",
         "mode": "degrade", "degrade_to": 0.1},
    ], mgr.sim.rng)
    tr = mgr.world.track_for("blue", "SAT-RED")
    assert tr is not None
    assert tr.confidence == pytest.approx(0.1)


def test_forced_custody_loss_drop_removes_track():
    mgr = _bare_manager()
    mgr.world.tracks.append(Track(object="SAT-RED", owner="blue", confidence=1.0, last_observation=0))
    mgr._apply_inject_effects(mgr.world, [
        {"type": "forced_custody_loss", "cell": "blue", "target": "SAT-RED", "mode": "drop"},
    ], mgr.sim.rng)
    assert mgr.world.track_for("blue", "SAT-RED") is None


def test_forced_custody_loss_never_touches_another_cells_track():
    """Negative assertion (FR-4430's Postcondition, ADR-0004) — a forced_custody_loss on blue's
    own track must never affect red's independent track on the same object."""
    mgr = _bare_manager()
    mgr.world.tracks.append(Track(object="SAT-X", owner="blue", confidence=1.0, last_observation=0))
    mgr.world.tracks.append(Track(object="SAT-X", owner="red", confidence=0.9, last_observation=0))
    mgr._apply_inject_effects(mgr.world, [
        {"type": "forced_custody_loss", "cell": "blue", "target": "SAT-X", "mode": "drop"},
    ], mgr.sim.rng)
    assert mgr.world.track_for("blue", "SAT-X") is None
    red_tr = mgr.world.track_for("red", "SAT-X")
    assert red_tr is not None
    assert red_tr.confidence == pytest.approx(0.9)


def test_forced_custody_loss_missing_target_is_a_no_op():
    mgr = _bare_manager()
    # No exception, no track created — Design Decision 2's posture.
    mgr._apply_inject_effects(mgr.world, [
        {"type": "forced_custody_loss", "cell": "blue", "target": "GHOST", "mode": "drop"},
    ], mgr.sim.rng)
    assert mgr.world.track_for("blue", "GHOST") is None


# -- scripted_manoeuvre -------------------------------------------------------------------------

def test_scripted_manoeuvre_changes_orbit_via_eci_mode_bypassing_delta_v_budget():
    mgr = _bare_manager()
    mgr.world.assets["SAT-1"] = Asset(id="SAT-1", owner="blue", orbit=_orbit())
    before_orbit = mgr.world.assets["SAT-1"].orbit
    assert mgr.world.assets["SAT-1"].resources.delta_v_ms == 0.0
    mgr._apply_inject_effects(mgr.world, [
        {"type": "scripted_manoeuvre", "target": "SAT-1", "mode": "eci",
         "params": {"dv": [10.0, 0.0, 0.0]}},
    ], mgr.sim.rng)
    after = mgr.world.assets["SAT-1"]
    assert after.orbit is not before_orbit  # a new osculating element set was computed
    # Never checked, never deducted — the whole point of Design Decision 3's bypass.
    assert after.resources.delta_v_ms == 0.0


def test_scripted_manoeuvre_changes_orbit_via_hohmann_mode():
    mgr = _bare_manager()
    mgr.world.assets["SAT-1"] = Asset(id="SAT-1", owner="blue", orbit=_orbit())
    r0, v0 = mgr.osys.prop.rv(mgr.world.assets["SAT-1"].orbit, mgr.world.now)
    mgr._apply_inject_effects(mgr.world, [
        {"type": "scripted_manoeuvre", "target": "SAT-1", "mode": "hohmann",
         "params": {"target_alt_km": (_LEO_A - R_EARTH_EQ) / 1000.0 + 50.0}},
    ], mgr.sim.rng)
    r1, v1 = mgr.osys.prop.rv(mgr.world.assets["SAT-1"].orbit, mgr.world.now)
    assert not np.allclose(v0, v1)
    assert mgr.world.assets["SAT-1"].resources.delta_v_ms == 0.0


def test_scripted_manoeuvre_missing_asset_is_a_no_op():
    mgr = _bare_manager()
    mgr._apply_inject_effects(mgr.world, [
        {"type": "scripted_manoeuvre", "target": "GHOST", "mode": "eci", "params": {"dv": [1, 0, 0]}},
    ], mgr.sim.rng)  # must not raise
