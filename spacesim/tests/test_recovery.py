"""Phase 4.5: the safe-mode recovery chain — confirm, multi-pass recovery, re-safe, patch, succeed."""

from __future__ import annotations

from spacesim.engine.bus import BusState, PayloadState
from spacesim.engine.effects import EffectInstance, ModerateEffectResolver
from spacesim.engine.entities import Asset
from spacesim.engine.geometry import R_EARTH_EQ, ecef_to_geodetic, eci_to_ecef
from spacesim.engine.orbit import OrbitState
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.recovery import RecoverySystem
from spacesim.engine.simtime import hours
from spacesim.engine.simulation import Simulation
from spacesim.engine.world import WorldState

PROP = ModeratePropagator()


def _leo():
    return OrbitState(a_m=R_EARTH_EQ + 550e3, e=0.0, i_deg=51.6, raan_deg=33, argp_deg=0, ta_deg=0, epoch=0)


def _subpoint(orbit, t):
    r, _ = PROP.rv(orbit, t)
    g = ecef_to_geodetic(eci_to_ecef(r, t))
    g.alt_m = 0.0
    return g


def _world(patched=False):
    world = WorldState(now=0)
    sat = _leo()
    world.assets["SAT"] = Asset(
        id="SAT", owner="blue", kind="satellite", orbit=sat,
        bus_state=BusState(), payload_state=PayloadState(type="isr_eo"),
        cyber_vulnerabilities=[{"vector": "ground_modem", "patchable": True, "patched": patched}],
    )
    world.assets["GS"] = Asset(id="GS", owner="blue", kind="ground_station", location=_subpoint(sat, 0))
    return world


def _safe_the_sat(world):
    eff = EffectInstance(category="cyber", target="SAT", access_vector="ground_modem", requires="none",
                         intended_outcome="safe_mode", success_prob=1.0, sm_susceptibility=1.0)
    ModerateEffectResolver().resolve(eff, world, Simulation(world, 0).rng)
    assert world.assets["SAT"].bus_state.mode == "safe_mode"


def test_difficulty_maps_to_pass_count():
    sim = Simulation(WorldState(), seed=0)
    assert RecoverySystem(sim, difficulty="quick").passes_needed() == 1
    assert RecoverySystem(sim, difficulty="realistic").passes_needed() == 2
    assert RecoverySystem(sim, difficulty="punishing").passes_needed() == 3


def test_recovery_resafes_until_root_cause_patched():
    world = _world(patched=False)
    _safe_the_sat(world)
    sim = Simulation(world, seed=1)
    rec = RecoverySystem(sim, difficulty="quick", root_cause_persists=True)

    # First attempt: confirm at the pass, but the modem vuln is unpatched → re-safed.
    plan = rec.begin_recovery("SAT", "GS")
    assert plan["ok"] and plan["passes_used"] == 1
    sim.advance_to(plan["finish_at"] + 1)
    bus = world.assets["SAT"].bus_state
    assert bus.safe_mode.defender_confirmed          # discovered at the contact
    assert bus.mode == "safe_mode"                   # recovery did not stick
    assert bus.safe_mode.blocked_reason is not None

    # Patch the vulnerability, then recover successfully.
    world.assets["SAT"].cyber_vulnerabilities[0]["patched"] = True
    plan2 = rec.begin_recovery("SAT", "GS")
    sim.advance_to(plan2["finish_at"] + 1)
    assert world.assets["SAT"].bus_state.mode == "nominal"   # back on the board
    assert world.assets["SAT"].bus_state.safe_mode.active is False


def test_realistic_recovery_takes_multiple_passes_when_cause_is_resolved():
    from spacesim.engine.bus import enter_safe_mode
    world = _world(patched=True)
    enter_safe_mode(world.assets["SAT"].bus_state, now=0, cause="fault")  # a fault, not an attack
    sim = Simulation(world, seed=2)
    rec = RecoverySystem(sim, difficulty="realistic", root_cause_persists=True)
    plan = rec.begin_recovery("SAT", "GS")
    assert plan["passes_used"] == 2
    sim.advance_to(plan["finish_at"] + 1)
    bus = world.assets["SAT"].bus_state
    assert bus.mode == "nominal"
    assert bus.safe_mode.passes_used == 2   # recovery consumed two passes
