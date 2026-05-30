"""Bus & payload command verbs: real deterministic effects, validation, telemetry, replay-safety.

Exercises the first batch wired through the order system as the ``command`` action
(``13-operator-command-catalog.md``): eps.shed_load / eps.restore_load (power), adcs.set_mode
(attitude), satcom.mitigate_interference (anti-jam). Each must produce an observable WorldState
change, re-validate at execution, and leave ``Simulation.replay()`` byte-identical.
"""

from __future__ import annotations

from spacesim.content.vignette import load_vignette
from spacesim.engine import telemetry as tel
from spacesim.engine.bus import BusState, PayloadState, advance_bus, enter_safe_mode
from spacesim.engine.buscommands import apply_command
from spacesim.engine.effects import ActiveEffect
from spacesim.engine.entities import Asset
from spacesim.engine.orders import Order
from spacesim.engine.simtime import minutes
from spacesim.engine.world import WorldState
from spacesim.session.manager import SessionManager

SEED = 42


def _mgr():
    mgr = SessionManager(load_vignette("training-basics"), seed=1)
    mgr.start()
    return mgr


def _cmd(actor, verb, **params):
    return Order(cell="blue", actor=actor, action="command", target=None,
                 params={"via": "GS-TRN", "verb": verb, **params})


# -- direct verb effects (unit) -----------------------------------------------
def test_shed_load_slows_battery_drain():
    """eps.shed_load cuts the eclipse drain, so SoC sits higher after the same eclipse span."""
    def soc_after_eclipse(shed: bool) -> float:
        bus = BusState()
        bus.power.battery_soc = 0.8
        bus.power.drain_rate_per_s = 1e-4
        if shed:
            apply_command(_one(bus), "SAT", "eps.shed_load", {}, 0)
        advance_bus(bus, None, minutes(30), sunlit=False)
        return bus.power.battery_soc
    assert soc_after_eclipse(shed=True) > soc_after_eclipse(shed=False)


def _one(bus):
    w = WorldState(now=0)
    w.assets["SAT"] = Asset(id="SAT", owner="blue", kind="satellite", bus_state=bus)
    return w


def test_restore_load_undoes_shed():
    w = _one(BusState())
    apply_command(w, "SAT", "eps.shed_load", {}, 0)
    assert w.assets["SAT"].bus_state.power.loads_shed is True
    apply_command(w, "SAT", "eps.restore_load", {}, 0)
    assert w.assets["SAT"].bus_state.power.loads_shed is False


def test_set_mode_changes_attitude():
    w = _one(BusState())
    ok, label = apply_command(w, "SAT", "adcs.set_mode", {"mode": "slew"}, 0)
    assert ok and label == "mode_slew" and w.assets["SAT"].bus_state.attitude.mode == "slew"


def test_mitigate_interference_shrinks_jam_signature():
    """The central troubleshooting loop: anti-jam shrinks the RX-power jam signature in telemetry."""
    w = WorldState(now=minutes(20))
    w.assets["SAT"] = Asset(id="SAT", owner="blue", kind="satellite",
                            bus_state=BusState(), payload_state=PayloadState(type="satcom"))
    w.active_effects.append(ActiveEffect(target="SAT", outcome="deny", start=0, end=minutes(60),
                                         category="electronic_warfare"))
    before = tel.sample(w, "SAT", "rx_power_dbm", w.now, SEED)["value"]
    apply_command(w, "SAT", "satcom.mitigate_interference", {}, w.now)
    after = tel.sample(w, "SAT", "rx_power_dbm", w.now, SEED)["value"]
    assert after < before - 5          # the receiver-power spike is measurably reduced
    nominal = tel.sample(w, "SAT", "rx_power_dbm", w.now, SEED, nominal=True)["value"]
    assert after > nominal             # ...but not fully gone (mitigation is capped)


def test_set_charge_mode_scales_charging():
    """eps.set_charge_mode 'fast' charges the battery faster while sunlit."""
    def soc_after_sun(mode: str) -> float:
        bus = BusState()
        bus.power.battery_soc = 0.5
        bus.power.charge_rate_per_s = 1e-4
        apply_command(_one(bus), "SAT", "eps.set_charge_mode", {"mode": mode}, 0)
        advance_bus(bus, None, minutes(30), sunlit=True)
        return bus.power.battery_soc
    assert soc_after_sun("fast") > soc_after_sun("nominal") > soc_after_sun("trickle")


def test_dump_storage_refreshes_ground_view():
    w = _one(BusState())
    ok, label = apply_command(w, "SAT", "cdh.dump_storage", {}, minutes(5))
    bus = w.assets["SAT"].bus_state
    assert ok and label == "telemetry_dumped"
    assert bus.ground_view is not None and bus.last_telemetry_time == minutes(5)


def test_collect_now_starts_filling_storage():
    bus = BusState()
    w = WorldState(now=0)
    w.assets["SAT"] = Asset(id="SAT", owner="blue", kind="satellite", bus_state=bus,
                            payload_state=PayloadState(type="isr_eo", collect_rate_per_s=1e-4))
    ok, label = apply_command(w, "SAT", "isr.collect_now", {}, 0)
    assert ok and label == "collecting" and w.assets["SAT"].payload_state.collecting
    advance_bus(bus, w.assets["SAT"].payload_state, minutes(10), sunlit=True)
    assert bus.cdh.storage_frac > 0.0          # storage actually fills once collecting


def test_collect_blocked_when_storage_full():
    bus = BusState()
    bus.cdh.storage_frac = 1.0
    w = WorldState(now=0)
    w.assets["SAT"] = Asset(id="SAT", owner="blue", kind="satellite", bus_state=bus,
                            payload_state=PayloadState(type="isr_eo"))
    ok, label = apply_command(w, "SAT", "isr.collect_now", {}, 0)
    assert not ok and label == "cannot_collect"


def test_isr_verb_rejected_on_satcom_payload():
    mgr = _mgr()
    mgr.world.assets["ISR-EO-1"].payload_state = PayloadState(type="satcom")
    assert mgr.validate_order("blue", _cmd("ISR-EO-1", "isr.collect_now")).reason == "no_payload_for_verb"


def test_batch3_verbs_mutate_observably():
    """Each batch-3 verb produces a real, observable mutation; clear_fault undoes a safe fsw_mode."""
    w = _one(BusState())
    apply_command(w, "SAT", "tcs.set_mode", {"mode": "survival"}, 0)
    assert w.assets["SAT"].bus_state.thermal.mode == "survival"
    apply_command(w, "SAT", "tcs.set_heater", {"on": True}, 0)
    assert w.assets["SAT"].bus_state.thermal.heater_on is True
    apply_command(w, "SAT", "comms.enable_isl", {"on": True}, 0)
    assert w.assets["SAT"].bus_state.comms.isl_enabled is True
    apply_command(w, "SAT", "comms.config_link", {"data_rate_kbps": 2048}, 0)
    assert w.assets["SAT"].bus_state.comms.data_rate_kbps == 2048
    apply_command(w, "SAT", "def.frequency_hop", {"on": True}, 0)
    assert w.assets["SAT"].bus_state.comms.freq_hopping is True
    apply_command(w, "SAT", "def.set_threat_warning", {"on": True}, 0)
    assert w.assets["SAT"].threat_warning is True
    # clear_fault returns fsw_mode to nominal when the bus isn't still safed (recompute would re-safe).
    w.assets["SAT"].bus_state.cdh.fsw_mode = "safe"
    apply_command(w, "SAT", "cdh.clear_fault", {}, 0)
    assert w.assets["SAT"].bus_state.cdh.fsw_mode == "nominal"


def test_frequency_hop_shrinks_jam_signature_in_telemetry():
    """def.frequency_hop on the bus reduces the jam term scaling like a payload mitigation does."""
    w = _one(BusState())                            # SAT with BusState (no payload)
    w.now = minutes(20)
    w.active_effects.append(ActiveEffect(target="SAT", outcome="deny", start=0, end=minutes(40),
                                         category="electronic_warfare"))
    before = tel.sample(w, "SAT", "rx_power_dbm", minutes(20), SEED)["value"]
    apply_command(w, "SAT", "def.frequency_hop", {"on": True}, minutes(20))
    after = tel.sample(w, "SAT", "rx_power_dbm", minutes(20), SEED)["value"]
    assert after < before - 8                        # signature shrinks (operator counters the jam)


def test_sigint_and_weather_payload_gates():
    """Sigint/weather verbs require a payload of the matching type, like ISR/SATCOM."""
    w = _one(BusState())
    w.assets["SAT"].payload_state = PayloadState(type="isr_eo")
    from spacesim.engine.buscommands import can_issue
    assert can_issue(w, "SAT", "sigint.task_collection") == (False, "no_payload_for_verb")
    assert can_issue(w, "SAT", "wx.schedule_collection") == (False, "no_payload_for_verb")
    w.assets["SAT"].payload_state = PayloadState(type="sigint")
    assert can_issue(w, "SAT", "sigint.task_collection")[0] is True
    w.assets["SAT"].payload_state = PayloadState(type="weather")
    assert can_issue(w, "SAT", "wx.schedule_collection")[0] is True


def test_patch_cyber_lets_recovery_stick():
    """def.patch_cyber removes a cyber root cause so the next recovery attempt actually sticks."""
    from spacesim.engine.bus import enter_safe_mode
    mgr = _mgr()
    sat = mgr.world.assets["ISR-EO-1"]
    sat.cyber_vulnerabilities = [{"vector": "ground_modem", "patchable": True, "patched": False}]
    enter_safe_mode(sat.bus_state, now=mgr.sim.clock.now, cause="cyber")
    mgr.sim._initial_state = mgr.world.model_dump()  # baseline AFTER safing so replay is consistent
    mgr.recovery.difficulty = "quick"
    # Without a patch, recovery re-safes.
    res = mgr.begin_recovery("blue", "ISR-EO-1")
    mgr.advance_to(res["finish_at"] + 1)
    assert mgr.world.assets["ISR-EO-1"].bus_state.safe_mode.blocked_reason  # re-safed
    # Patch the vector (defender's defensive verb), then recover again → sticks.
    ack = mgr.issue_order("blue", _cmd("ISR-EO-1", "def.patch_cyber", vector="ground_modem"))
    assert ack.ok
    mgr.advance_to(ack.earliest_window[1] + 1)
    assert mgr.world.assets["ISR-EO-1"].cyber_vulnerabilities[0]["patched"] is True
    res2 = mgr.begin_recovery("blue", "ISR-EO-1")
    mgr.advance_to(res2["finish_at"] + 1)
    assert mgr.world.assets["ISR-EO-1"].bus_state.mode == "nominal"
    assert mgr.sim.replay().model_dump_json() == mgr.world.model_dump_json()


def test_lost_asset_command_fails_gracefully():
    w = _one(BusState())
    w.assets["SAT"].health = "destroyed"
    ok, label = apply_command(w, "SAT", "eps.shed_load", {}, 0)
    assert not ok and label == "lost"


# -- order-system integration + validation ------------------------------------
def test_command_order_executes_and_is_replay_safe():
    mgr = _mgr()
    ack = mgr.issue_order("blue", _cmd("ISR-EO-1", "eps.shed_load"))
    assert ack.ok and ack.status == "queued" and ack.delivery_path == "ground_uplink"
    mgr.advance_to(ack.earliest_window[1] + 1)
    assert mgr.world.assets["ISR-EO-1"].bus_state.power.loads_shed is True
    assert any(e["template"] == "eps.shed_load" and e["success"] for e in mgr.world.effect_log)
    # The command fired as a logged event, so replay reproduces the world exactly.
    assert mgr.sim.replay().model_dump_json() == mgr.world.model_dump_json()


def test_command_validation_reasons():
    mgr = _mgr()
    # Unknown verb.
    assert mgr.validate_order("blue", _cmd("ISR-EO-1", "eps.no_such")).reason == "unknown_command"
    # No delivery path (no station / stored slot).
    bad = Order(cell="blue", actor="ISR-EO-1", action="command", params={"verb": "eps.shed_load"})
    assert mgr.validate_order("blue", bad).reason == "no_command_station"
    # Payload verb on an asset with no payload of that type.
    assert mgr.validate_order("blue", _cmd("ISR-EO-1", "satcom.shift_users")).reason == "no_payload_for_verb"
    # Fog: Red cannot command a Blue asset.
    assert mgr.validate_order("red", _cmd("ISR-EO-1", "eps.shed_load")).reason == "not_owner"


def test_payload_verb_blocked_in_safe_mode():
    mgr = _mgr()
    a = mgr.world.assets["ISR-EO-1"]
    a.payload_state = PayloadState(type="satcom")
    enter_safe_mode(a.bus_state, now=mgr.sim.clock.now, cause="cyber")
    assert mgr.validate_order("blue", _cmd("ISR-EO-1", "satcom.mitigate_interference")).reason == "payload_unavailable"


# -- Stage B: new catalog verbs -----------------------------------------------

def _sat_with_payload(payload_type: str = "isr_eo", dv: float = 50.0):
    from spacesim.engine.entities import AssetResources
    w = WorldState(now=0)
    w.assets["SAT"] = Asset(
        id="SAT", owner="blue", kind="satellite",
        bus_state=BusState(),
        payload_state=PayloadState(type=payload_type),
        resources=AssetResources(delta_v_ms=dv),
    )
    return w


def test_cdh_reset_subsystem_exits_fault_state():
    w = _sat_with_payload()
    bus = w.assets["SAT"].bus_state
    bus.cdh.fsw_mode = "safe"
    bus.attitude.mode = "safe"
    bus.attitude.pointing_ok = False
    ok, label = apply_command(w, "SAT", "cdh.reset_subsystem", {}, 0)
    assert ok and label == "subsystem_reset"
    assert bus.cdh.fsw_mode == "nominal"
    assert bus.attitude.mode == "nominal"
    assert bus.attitude.pointing_ok is True


def test_cdh_reset_subsystem_replay_safe():
    mgr = _mgr()
    ack = mgr.issue_order("blue", _cmd("ISR-EO-1", "cdh.reset_subsystem"))
    assert ack.ok
    mgr.advance_to(ack.earliest_window[1] + 1)
    assert any(e["template"] == "cdh.reset_subsystem" and e["success"] for e in mgr.world.effect_log)
    assert mgr.sim.replay().model_dump_json() == mgr.world.model_dump_json()


def test_adcs_desaturate_restores_pointing():
    w = _sat_with_payload()
    bus = w.assets["SAT"].bus_state
    bus.attitude.mode = "slew"
    bus.attitude.pointing_ok = False
    bus.attitude.status = "yellow"
    ok, label = apply_command(w, "SAT", "adcs.desaturate", {}, 0)
    assert ok and label == "desaturated"
    assert bus.attitude.mode == "nominal"
    assert bus.attitude.pointing_ok is True
    assert bus.attitude.status == "green"


def test_adcs_desaturate_replay_safe():
    mgr = _mgr()
    ack = mgr.issue_order("blue", _cmd("ISR-EO-1", "adcs.desaturate"))
    assert ack.ok
    mgr.advance_to(ack.earliest_window[1] + 1)
    assert mgr.sim.replay().model_dump_json() == mgr.world.model_dump_json()


def test_comms_point_antenna_sets_mode():
    w = _sat_with_payload()
    ok, label = apply_command(w, "SAT", "comms.point_antenna", {"mode": "tracking"}, 0)
    assert ok and label == "antenna_tracking"
    assert w.assets["SAT"].bus_state.comms.antenna_mode == "tracking"


def test_comms_point_antenna_unknown_mode_defaults_to_nominal():
    w = _sat_with_payload()
    ok, label = apply_command(w, "SAT", "comms.point_antenna", {"mode": "bogus"}, 0)
    assert ok and w.assets["SAT"].bus_state.comms.antenna_mode == "nominal"


def test_comms_point_antenna_replay_safe():
    mgr = _mgr()
    ack = mgr.issue_order("blue", _cmd("ISR-EO-1", "comms.point_antenna", mode="zenith"))
    assert ack.ok
    mgr.advance_to(ack.earliest_window[1] + 1)
    assert mgr.world.assets["ISR-EO-1"].bus_state.comms.antenna_mode == "zenith"
    assert mgr.sim.replay().model_dump_json() == mgr.world.model_dump_json()


def test_isr_set_mode_changes_payload_mode():
    w = _sat_with_payload("isr_eo")
    ok, label = apply_command(w, "SAT", "isr.set_mode", {"mode": "narrow"}, 0)
    assert ok and label == "isr_mode_narrow"
    assert w.assets["SAT"].payload_state.mode == "narrow"


def test_isr_set_mode_standby_stops_collecting():
    w = _sat_with_payload("isr_eo")
    w.assets["SAT"].payload_state.collecting = True
    ok, label = apply_command(w, "SAT", "isr.set_mode", {"mode": "standby"}, 0)
    assert ok and w.assets["SAT"].payload_state.collecting is False


def test_isr_set_mode_replay_safe():
    mgr = _mgr()
    ack = mgr.issue_order("blue", _cmd("ISR-EO-1", "isr.set_mode", mode="wide"))
    assert ack.ok
    mgr.advance_to(ack.earliest_window[1] + 1)
    assert mgr.world.assets["ISR-EO-1"].payload_state.mode == "wide"
    assert mgr.sim.replay().model_dump_json() == mgr.world.model_dump_json()


def test_pnt_set_integrity_changes_mode():
    w = _sat_with_payload("pnt")
    ok, label = apply_command(w, "SAT", "pnt.set_integrity", {"mode": "protected"}, 0)
    assert ok and label == "integrity_protected"
    assert w.assets["SAT"].payload_state.integrity_mode == "protected"


def test_pnt_set_integrity_wrong_payload_rejected():
    w = _sat_with_payload("isr_eo")
    # isr asset should fail can_issue for pnt.set_integrity
    from spacesim.engine.buscommands import can_issue
    ok, reason = can_issue(w, "SAT", "pnt.set_integrity")
    assert not ok and reason == "no_payload_for_verb"


def test_def_maneuver_evade_consumes_dv_and_sets_flag():
    w = _sat_with_payload(dv=50.0)
    ok, label = apply_command(w, "SAT", "def.maneuver_evade", {"dv_cost": 10.0}, 0)
    assert ok and label == "evasion_burn_executed"
    assert abs(w.assets["SAT"].resources.delta_v_ms - 40.0) < 1e-6
    assert w.assets["SAT"].payload_state.evasion_active is True


def test_def_maneuver_evade_rejected_when_dv_insufficient():
    w = _sat_with_payload(dv=0.5)
    ok, label = apply_command(w, "SAT", "def.maneuver_evade", {"dv_cost": 5.0}, 0)
    assert not ok and label == "insufficient_delta_v"


def test_def_maneuver_evade_can_issue_gate():
    from spacesim.engine.buscommands import can_issue
    w = _sat_with_payload(dv=0.0)
    ok, reason = can_issue(w, "SAT", "def.maneuver_evade")
    assert not ok and reason == "insufficient_delta_v"


def test_def_maneuver_evade_replay_safe():
    # ISR-EO-1 starts with 80.0 m/s Δv in training-basics; evasion costs 5.0 by default.
    mgr = _mgr()
    ack = mgr.issue_order("blue", _cmd("ISR-EO-1", "def.maneuver_evade", dv_cost=5.0))
    assert ack.ok
    mgr.advance_to(ack.earliest_window[1] + 1)
    assert mgr.world.assets["ISR-EO-1"].payload_state.evasion_active is True
    assert abs(mgr.world.assets["ISR-EO-1"].resources.delta_v_ms - 75.0) < 1e-6
    assert mgr.sim.replay().model_dump_json() == mgr.world.model_dump_json()
