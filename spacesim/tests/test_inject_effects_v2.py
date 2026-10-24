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

@pytest.mark.verifies("FR-4430")
def test_sensor_health_defaults_to_nominal_when_absent_from_yaml():
    sensor = Sensor.model_validate({"id": "S-1", "owner": "blue"})
    assert sensor.health == "nominal"


@pytest.mark.verifies("FR-4430")
def test_scene_from_world_excludes_degraded_sensor():
    mgr = _bare_manager()
    mgr.world.sensors["S-1"] = Sensor(id="S-1", owner="blue", health="nominal")
    mgr.world.sensors["S-2"] = Sensor(id="S-2", owner="blue", health="degraded")
    scene = scene_from_world(mgr.world)
    assert "S-1" in scene.sensors
    assert "S-2" not in scene.sensors


# -- anomaly -----------------------------------------------------------------------------------

@pytest.mark.verifies("FR-4430")
def test_anomaly_bus_subsystem_sets_safe_mode_and_restore_clears_it():
    mgr = _bare_manager()
    mgr.world.assets["SAT-1"] = Asset(id="SAT-1", owner="blue", bus_state=BusState())
    mgr._apply_inject_effects(mgr.world, [
        {"type": "anomaly", "target": "SAT-1", "subsystem": "bus", "cause": "test cause"},
    ], mgr.sim.rng)
    bus = mgr.world.assets["SAT-1"].bus_state
    assert bus.mode == "safe_mode"
    # BL-0128 remediation: enter_safe_mode() must be used, not a bare `mode` assignment, so the
    # full safe-mode state is consistent — otherwise begin_recovery refuses with "not_safed" and
    # the asset is operator-unrecoverable.
    assert bus.safe_mode.active is True
    assert bus.safe_mode.cause == "test cause"
    assert bus.safe_mode.entered_at == mgr.world.now
    assert any("test cause" in m["text"] for m in mgr.world.messages)

    mgr._apply_inject_effects(mgr.world, [
        {"type": "anomaly", "target": "SAT-1", "subsystem": "bus", "restore": True},
    ], mgr.sim.rng)
    assert bus.mode == "nominal"
    assert bus.safe_mode.active is False


@pytest.mark.verifies("FR-4430")
def test_anomaly_safed_asset_is_accepted_by_begin_recovery():
    """BL-0128 remediation regression: an anomaly-safed asset must be recoverable through the
    existing RecoverySystem loop (Design Decision 4's actual intent), not refused with
    "not_safed"."""
    mgr = _bare_manager()
    mgr.world.assets["SAT-1"] = Asset(id="SAT-1", owner="blue", bus_state=BusState())
    mgr._apply_inject_effects(mgr.world, [
        {"type": "anomaly", "target": "SAT-1", "subsystem": "bus", "cause": "test cause"},
    ], mgr.sim.rng)
    result = mgr.begin_recovery("blue", "SAT-1", "")
    assert result["reason"] != "not_safed"


@pytest.mark.verifies("FR-4430")
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

@pytest.mark.verifies("FR-4430")
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

@pytest.mark.verifies("FR-4430")
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


@pytest.mark.verifies("FR-4430")
def test_forced_custody_loss_drop_removes_track():
    mgr = _bare_manager()
    mgr.world.tracks.append(Track(object="SAT-RED", owner="blue", confidence=1.0, last_observation=0))
    mgr._apply_inject_effects(mgr.world, [
        {"type": "forced_custody_loss", "cell": "blue", "target": "SAT-RED", "mode": "drop"},
    ], mgr.sim.rng)
    assert mgr.world.track_for("blue", "SAT-RED") is None


@pytest.mark.verifies("FR-4430")
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


@pytest.mark.verifies("FR-4430")
def test_forced_custody_loss_missing_target_is_a_no_op():
    mgr = _bare_manager()
    # No exception, no track created — Design Decision 2's posture.
    mgr._apply_inject_effects(mgr.world, [
        {"type": "forced_custody_loss", "cell": "blue", "target": "GHOST", "mode": "drop"},
    ], mgr.sim.rng)
    assert mgr.world.track_for("blue", "GHOST") is None


# -- scripted_manoeuvre -------------------------------------------------------------------------

@pytest.mark.verifies("FR-4430")
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


@pytest.mark.verifies("FR-4430")
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


@pytest.mark.verifies("FR-4430")
def test_scripted_manoeuvre_missing_asset_is_a_no_op():
    mgr = _bare_manager()
    mgr._apply_inject_effects(mgr.world, [
        {"type": "scripted_manoeuvre", "target": "GHOST", "mode": "eci", "params": {"dv": [1, 0, 0]}},
    ], mgr.sim.rng)  # must not raise


# -- IP-1063 (BL-0129 / BL-0188) — inject effect fire-time validation ---------------------------

def _validate(*args, **kwargs):
    # Imported lazily so the pre-implementation test run fails per test, not at collection.
    from spacesim.session.manager import validate_inject_effects
    return validate_inject_effects(*args, **kwargs)


def _bus_less_manager() -> SessionManager:
    """A started manager whose world has one bus-less satellite (BL-0188's shape — every shipped
    Red satellite) and one satellite with a bus."""
    orbit = {"a_m": _LEO_A, "e": 0.0, "i_deg": 51.6, "raan_deg": 0.0, "argp_deg": 0.0}
    raw = {
        "id": "test-ip1063", "title": "IP-1063",
        "start_epoch_utc": "2030-01-01T00:00:00Z",
        "blue_forces": [{"id": "SAT-BUS", "kind": "satellite", "orbit": {**orbit, "ta_deg": 0.0},
                         "bus_state": {"power": {"battery_soc": 0.9}}}],
        "red_forces": [{"id": "SAT-NOBUS", "kind": "satellite", "orbit": {**orbit, "ta_deg": 30.0}}],
        "neutral_forces": [], "sensors": [],
    }
    mgr = SessionManager(Vignette.model_validate(raw), seed=0)
    mgr.start()
    return mgr


@pytest.mark.verifies("FR-4430")
@pytest.mark.parametrize("effect", [
    {"type": "anomaly", "subsystem": "bus"},                                      # no target
    {"type": "anomaly", "target": "SAT-1", "subsystem": "power"},                 # bad subsystem
    {"type": "forced_custody_loss", "target": "SAT-1", "mode": "drop"},           # no cell
    {"type": "forced_custody_loss", "cell": "purple", "target": "SAT-1"},         # bad cell
    {"type": "scripted_manoeuvre", "target": "SAT-1", "mode": "warp"},            # bad mode
    {"target": "SAT-1"},                                                          # no type
    {"type": "anomoly", "target": "SAT-1"},                                       # unknown type
    {"type": "reveal_asset", "target": "SAT-1"},                                  # no `to`
])
def test_validator_flags_malformed_effects(effect):
    mgr = _bare_manager()
    problems = _validate(mgr.world, [effect], check_targets=False)
    assert len(problems) == 1


@pytest.mark.verifies("FR-4430")
def test_validator_accepts_well_formed_fr4430_effects():
    mgr = _bare_manager()
    mgr.world.assets["SAT-1"] = Asset(id="SAT-1", owner="blue", orbit=_orbit(), bus_state=BusState())
    mgr.world.sensors["S-1"] = Sensor(id="S-1", owner="blue")
    mgr.world.tracks.append(Track(object="SAT-1", owner="red", confidence=1.0, last_observation=0))
    effects = [
        {"type": "anomaly", "target": "SAT-1", "subsystem": "bus", "cause": "c"},
        {"type": "sensor_outage", "target": "S-1"},
        {"type": "forced_custody_loss", "cell": "red", "target": "SAT-1", "mode": "degrade", "degrade_to": 0.2},
        {"type": "scripted_manoeuvre", "target": "SAT-1", "mode": "eci", "params": {"dv": [1, 0, 0]}},
    ]
    assert _validate(mgr.world, effects, check_targets=True) == []


@pytest.mark.verifies("FR-4430")
def test_fire_inject_rejects_anomaly_on_bus_less_asset_and_changes_nothing():
    """BL-0188 — previously accepted with ok:true and silently a no-op."""
    mgr = _bus_less_manager()
    n_log, now = len(mgr.sim.eventlog.entries), mgr.sim.clock.now
    with pytest.raises(ValueError) as exc:
        mgr.fire_inject([{"type": "anomaly", "target": "SAT-NOBUS", "subsystem": "bus"}])
    assert "SAT-NOBUS" in str(exc.value) and "bus" in str(exc.value)
    assert len(mgr.sim.eventlog.entries) == n_log
    assert mgr.sim.clock.now == now
    # The same inject on an asset with a bus is accepted and lands.
    mgr.fire_inject([{"type": "anomaly", "target": "SAT-BUS", "subsystem": "bus", "cause": "x"}])
    assert mgr.world.assets["SAT-BUS"].bus_state.mode == "safe_mode"


@pytest.mark.verifies("FR-4430")
def test_fire_inject_is_atomic_on_a_partly_invalid_inject():
    mgr = _bus_less_manager()
    with pytest.raises(ValueError):
        mgr.fire_inject([{"type": "message", "to": ["white"], "text": "IP1063-atomic"},
                         {"type": "anomaly", "subsystem": "bus"}])
    assert not any(m.get("text") == "IP1063-atomic" for m in mgr.world.messages)


@pytest.mark.verifies("FR-4430")
def test_handler_skips_malformed_effect_without_raising():
    """BL-0129 — a malformed effect used to raise mid-handler after earlier effects mutated."""
    mgr = _bare_manager()
    mgr.world.sensors["S-1"] = Sensor(id="S-1", owner="blue")
    mgr._apply_inject_effects(mgr.world, [
        {"type": "message", "to": ["blue"], "text": "first"},
        {"type": "forced_custody_loss", "target": "SAT-X", "mode": "drop"},   # no cell
        {"type": "sensor_outage", "target": "S-1"},
    ], mgr.sim.rng)
    assert any(m.get("text") == "first" for m in mgr.world.messages)
    assert mgr.world.sensors["S-1"].health == "degraded"
    skipped = [m for m in mgr.world.messages
               if m.get("to") == ["white"] and str(m.get("text", "")).startswith("inject effect skipped")]
    assert len(skipped) == 1


@pytest.mark.verifies("FR-4430")
def test_skip_path_replays_identically():
    """BL-0129 — a vignette-style scheduled inject (bypassing fire_inject's boundary) with a
    malformed effect and a scripted manoeuvre whose params make compute_maneuver raise: live
    advances without an exception, and replay reproduces the live world exactly."""
    mgr = _bus_less_manager()
    t = mgr.sim.clock.now + 60 * 1_000_000
    mgr.sim.schedule(t, "inject", {"effects": [
        {"type": "message", "to": ["blue"], "text": "kept"},
        {"type": "anomaly", "subsystem": "bus"},                                           # malformed
        {"type": "scripted_manoeuvre", "target": "SAT-BUS", "mode": "eci", "params": {"dv": [1, 2]}},
    ]})
    mgr.sim.advance_to(t + 1)
    mgr.world = mgr.sim.world
    assert any(m.get("text") == "kept" for m in mgr.world.messages)
    skipped = [m for m in mgr.world.messages if str(m.get("text", "")).startswith("inject effect skipped")]
    assert len(skipped) == 2
    assert mgr.sim.replay().model_dump_json() == mgr.world.model_dump_json()


@pytest.mark.verifies("FR-4430")
def test_all_shipped_injects_and_library_templates_validate_clean():
    """Regression guard: the validator's known-type set and required keys match shipped content."""
    from pathlib import Path

    import yaml

    from spacesim.content.vignette import list_vignettes, load_vignette
    mgr = _bare_manager()
    problems = []
    for entry in list_vignettes():
        v = load_vignette(entry["id"])
        for inj in v.injects:
            problems += [f"{v.id}/{inj.id}: {p}"
                         for p in _validate(mgr.world, inj.effects, check_targets=False)]
    lib = Path(__file__).resolve().parent.parent / "content" / "inject_library.yaml"
    for inj in (yaml.safe_load(lib.read_text(encoding="utf-8")) or {}).get("injects") or []:
        problems += [f"library/{inj.get('id')}: {p}"
                     for p in _validate(mgr.world, inj.get("effects") or [], check_targets=False)]
    assert problems == []
