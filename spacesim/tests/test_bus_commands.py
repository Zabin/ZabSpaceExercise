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
