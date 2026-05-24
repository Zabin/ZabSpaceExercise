"""Safe-mode inducement (§6.1), hardening counterplay, and pass-gated discovery."""

from __future__ import annotations

from spacesim.engine.bus import BusState, PayloadState, refresh_ground_view
from spacesim.engine.busmodel import BusSystem
from spacesim.engine.effects import EffectInstance, ModerateEffectResolver
from spacesim.engine.entities import Asset
from spacesim.engine.geometry import R_EARTH_EQ
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import Order, OrderSystem
from spacesim.engine.rng import SeededRng
from spacesim.engine.simtime import hours, minutes
from spacesim.engine.simulation import Simulation
from spacesim.engine.world import WorldState


def _sat(**kw) -> Asset:
    return Asset(
        id="SAT", owner="blue", kind="satellite",
        orbit=OrbitState(a_m=R_EARTH_EQ + 550e3, e=0.0, i_deg=51.6, raan_deg=33, argp_deg=0, ta_deg=0, epoch=0),
        bus_state=BusState(), payload_state=PayloadState(type="isr_eo"),
        cyber_vulnerabilities=[{"vector": "ground_modem", "patchable": True, "patched": False}],
        **kw,
    )


def _cyber_safe_effect(**kw) -> EffectInstance:
    return EffectInstance(
        category="cyber", target="SAT", access_vector="ground_modem", requires="none",
        intended_outcome="safe_mode", success_prob=1.0, sm_susceptibility=1.0, **kw,
    )


def test_cyber_induces_safe_mode_and_disables_payload():
    w = WorldState(now=5000)
    w.assets["SAT"] = _sat()
    out = ModerateEffectResolver().resolve(_cyber_safe_effect(), w, SeededRng(1))
    assert out.success and out.achieved_outcome == "safe_mode"
    bus = w.assets["SAT"].bus_state
    assert bus.mode == "safe_mode" and bus.safe_mode.active
    assert bus.safe_mode.entered_at == 5000 and bus.safe_mode.cause == "cyber"


def test_hardening_and_patching_block_safe_mode():
    res = ModerateEffectResolver()
    # Fully hardened → susceptibility 0.
    hardened = WorldState(now=0)
    hardened.assets["SAT"] = _sat(hardening=1.0)
    assert not res.resolve(_cyber_safe_effect(), hardened, SeededRng(1)).success
    assert hardened.assets["SAT"].bus_state.mode == "nominal"
    # Patched vulnerability → no foothold.
    patched = WorldState(now=0)
    patched.assets["SAT"] = _sat()
    patched.assets["SAT"].cyber_vulnerabilities[0]["patched"] = True
    assert not res.resolve(_cyber_safe_effect(), patched, SeededRng(1)).success


def test_safe_mode_is_discovered_only_at_the_next_telemetry_contact():
    w = WorldState(now=0)
    sat = _sat()
    refresh_ground_view(sat.bus_state, now=0)  # last good contact: nominal
    w.assets["SAT"] = sat

    # Safe-mode is induced off-pass an hour later; the ground view is still the stale nominal one.
    w.now = hours(1)
    ModerateEffectResolver().resolve(_cyber_safe_effect(), w, SeededRng(1))
    assert sat.bus_state.mode == "safe_mode"
    assert sat.bus_state.ground_view["mode"] == "nominal"        # not discovered yet
    assert sat.bus_state.ground_view["safe_mode_active"] is False

    # Next contact dumps stored telemetry, revealing it entered safe mode an hour ago.
    contact = hours(2)
    w.now = contact
    refresh_ground_view(sat.bus_state, contact)
    assert sat.bus_state.ground_view["safe_mode_active"] is True
    assert sat.bus_state.ground_view["safe_mode_entered_at"] == hours(1) < contact


def test_bus_evolution_runs_through_event_loop_and_replays_identically():
    w = WorldState(now=0)
    sat = _sat()
    sat.bus_state.power.battery_soc = 0.6
    sat.bus_state.power.drain_rate_per_s = 0.4 / 3600
    sat.bus_state.power.charge_rate_per_s = 0.4 / 3600
    w.assets["SAT"] = sat
    w.assets["CYB"] = Asset(id="CYB", owner="blue", kind="cyber_unit")

    sim = Simulation(w, seed=11)
    bus_sys = BusSystem(sim)
    osys = OrderSystem(sim, roe={"cyber_authorized": True})

    bus_sys.schedule_ticks(period_s=300, until=hours(3))
    order = osys.issue(Order(cell="blue", actor="CYB", action="cyber", target="SAT",
                             params={"access_vector": "ground_modem", "outcome": "safe_mode",
                                     "success_prob": 1.0, "sm_susceptibility": 1.0}))
    assert order.status == "queued"

    sim.advance_to(hours(3))
    assert sat.bus_state.mode == "safe_mode"           # cyber safed it during the run
    assert isinstance(sat.bus_state.power.in_eclipse, bool)
    live = sim.world.model_dump_json()
    assert sim.replay().model_dump_json() == live      # bus ticks + effect replay byte-identically
