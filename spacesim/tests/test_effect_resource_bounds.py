"""IP-1320 (FS-132; FR-1460, FR-1470, ADR-0037) — effect resource bounds.

FR-1460: an engagement never fires more rounds than its effector holds — refused at dry-run and
issue (`insufficient_ammo`), and re-checked at execution so queued engagements cannot overdraw.
FR-1470: a jam never changes the jammer's `power_w` rating (ADR-0037: a rating, not a consumable).
"""

from __future__ import annotations

import pytest

from spacesim.content.vignette import load_vignette
from spacesim.engine.custody import Track
from spacesim.engine.effects import EffectOutcome, ModerateEffectResolver
from spacesim.engine.entities import Asset, AssetResources
from spacesim.engine.geometry import R_EARTH_EQ, ecef_to_geodetic, eci_to_ecef
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import Order, OrderSystem
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.simtime import minutes
from spacesim.engine.simulation import Simulation
from spacesim.engine.world import WorldState
from spacesim.session.manager import SessionManager

PROP = ModeratePropagator()


def _leo(ta: float = 0.0) -> OrbitState:
    return OrbitState(a_m=R_EARTH_EQ + 550e3, e=0.0, i_deg=51.6, raan_deg=33, argp_deg=0, ta_deg=ta, epoch=0)


def _subpoint(orbit: OrbitState, t: int):
    r, _ = PROP.rv(orbit, t)
    g = ecef_to_geodetic(eci_to_ecef(r, t))
    g.alt_m = 0.0
    return g


class _ForcedResolver:
    """Deterministic test resolver: every resolution succeeds (or fails) as told, and every call
    is recorded so a test can see which effects were actually resolved."""

    def __init__(self, success: bool = True):
        self.success = success
        self.calls: list[str] = []
        self._real = ModerateEffectResolver()

    def resolve(self, effect, world, rng):
        self.calls.append(effect.target)
        if not self.success:
            return EffectOutcome(achieved_outcome="none", success=False)
        if effect.kinetic:
            target = world.assets.get(effect.target)
            if target is not None:
                target.health = "destroyed"
        return EffectOutcome(achieved_outcome=effect.intended_outcome, success=True)


def _kinetic_world(ammo: int, n_targets: int = 1) -> WorldState:
    sat = _leo()
    world = WorldState(now=0)
    for i in range(n_targets):
        tid = f"RSAT{i}"
        world.assets[tid] = Asset(id=tid, owner="red", kind="satellite", orbit=_leo(ta=0.01 * i))
        world.tracks.append(Track(object=tid, owner="blue", last_observation=0, confidence=1.0,
                                  characterized=True))
    world.assets["INT"] = Asset(id="INT", owner="blue", kind="interceptor",
                                location=_subpoint(sat, 0), resources=AssetResources(ammo=ammo))
    return world


def _osys(world: WorldState, resolver=None, seed: int = 7) -> tuple[Simulation, OrderSystem]:
    sim = Simulation(world, seed=seed)
    roe = {c: {"kinetic_authorized": True, "cyber_authorized": True} for c in ("blue", "red")}
    return sim, OrderSystem(sim, roe=roe, resolver=resolver)


def _engage(target: str = "RSAT0", **params) -> Order:
    return Order(cell="blue", actor="INT", action="engage", target=target,
                 params={"interceptor_class": "mrbm_kkv", **params})


# -- FR-1460: validation bound -------------------------------------------------------------------

def test_oversized_salvo_refused_by_dry_run_and_issue():
    world = _kinetic_world(ammo=2)
    sim, osys = _osys(world)
    log_before = len(sim.eventlog)
    preview = osys.dry_run(_engage(salvo_n=3))
    assert preview.status == "rejected" and preview.fail_reason == "insufficient_ammo"
    order = osys.issue(_engage(salvo_n=3))
    assert order.status == "rejected" and order.fail_reason == "insufficient_ammo"
    assert len(sim.eventlog) == log_before
    assert sim.scheduler.pending() == []  # nothing scheduled
    assert world.assets["INT"].resources.ammo == 2


def test_exact_salvo_accepted_and_charged_on_success():
    world = _kinetic_world(ammo=2)
    sim, osys = _osys(world, resolver=_ForcedResolver(success=True))
    order = osys.issue(_engage(salvo_n=2))
    assert order.status == "queued", order.fail_reason
    sim.advance_to(order.earliest_window[0] + 1)
    assert world.assets["INT"].resources.ammo == 0


@pytest.mark.parametrize("params", [{}, {"salvo_n": None}])
def test_absent_or_null_salvo_counts_as_one_round(params):
    world = _kinetic_world(ammo=1)
    _, osys = _osys(world)
    assert osys.dry_run(_engage(**params)).status == "queued"


def test_zero_rounds_still_no_ammo():
    world = _kinetic_world(ammo=0)
    _, osys = _osys(world)
    order = osys.issue(_engage(salvo_n=1))
    assert order.status == "rejected" and order.fail_reason == "no_ammo"


# -- FR-1460: execute-time re-check --------------------------------------------------------------

def _queued_overdraw():
    world = _kinetic_world(ammo=2, n_targets=2)
    resolver = _ForcedResolver(success=True)
    sim, osys = _osys(world, resolver=resolver)
    first = osys.issue(_engage("RSAT0", salvo_n=2))
    second = osys.issue(_engage("RSAT1", salvo_n=2))
    assert first.status == "queued" and second.status == "queued"
    last = max(first.earliest_window[0], second.earliest_window[0])
    sim.advance_to(last + 1)
    return world, sim, resolver


def test_queued_engagements_cannot_overdraw():
    world, _, resolver = _queued_overdraw()
    assert world.assets["INT"].resources.ammo == 0
    kinetic = [e for e in world.effect_log if e["template"].startswith("da_asat")]
    assert len(kinetic) == 2
    failed = [e for e in kinetic if e["achieved"] == "failed"]
    assert len(failed) == 1
    assert failed[0]["success"] is False and failed[0]["reason"] == "insufficient_ammo"
    # The failed engagement was never resolved and its target is untouched.
    assert len(resolver.calls) == 1
    assert world.assets[failed[0]["target"]].health != "destroyed"


def test_queued_overdraw_replays_identically():
    world, sim, _ = _queued_overdraw()
    replayed = sim.replay()
    assert replayed.model_dump() == world.model_dump()


# -- FR-1480 (IP-1321, FS-132 v1.1): a fired salvo is charged whether it hits or misses -----------
# Owner decision 2026-10-17 (`BL-0249`): misses consume interceptors too. Before IP-1321 the charge
# sat inside `if cons and outcome.success`, so a miss left the rounds untouched.

def _kinetic_log(world: WorldState) -> list[dict]:
    return [e for e in world.effect_log if e["template"].startswith("da_asat")]


def _missed_engagement():
    world = _kinetic_world(ammo=2)
    sim, osys = _osys(world, resolver=_ForcedResolver(success=False))
    order = osys.issue(_engage(salvo_n=1))
    assert order.status == "queued", order.fail_reason
    sim.advance_to(order.earliest_window[0] + 1)
    return world, sim, osys


def test_missed_salvo_is_charged():
    world, _, osys = _missed_engagement()
    (rec,) = _kinetic_log(world)
    assert rec["success"] is False
    assert world.assets["RSAT0"].health != "destroyed"
    assert world.assets["INT"].resources.ammo == 1          # the miss cost the round it fired
    # Only one round is left, so a 2-round salvo is now refused at both paths.
    assert osys.dry_run(_engage(salvo_n=2)).fail_reason == "insufficient_ammo"
    assert osys.issue(_engage(salvo_n=2)).fail_reason == "insufficient_ammo"


def test_salvo_at_already_destroyed_target_is_charged():
    world = _kinetic_world(ammo=2)
    sim, osys = _osys(world)                                 # the real resolver
    order = osys.issue(_engage(salvo_n=1))
    assert order.status == "queued", order.fail_reason
    world.assets["RSAT0"].health = "destroyed"               # destroyed before the window opens
    sim.advance_to(order.earliest_window[0] + 1)
    (rec,) = _kinetic_log(world)
    assert rec["achieved"] == "none" and rec["success"] is False
    assert world.assets["INT"].resources.ammo == 1


def test_exact_salvo_charged_on_a_miss():
    world = _kinetic_world(ammo=2)
    sim, osys = _osys(world, resolver=_ForcedResolver(success=False))
    order = osys.issue(_engage(salvo_n=2))
    assert order.status == "queued", order.fail_reason
    sim.advance_to(order.earliest_window[0] + 1)
    assert _kinetic_log(world)[-1]["success"] is False
    assert world.assets["INT"].resources.ammo == 0


# Recorded at `8b690d8` (before IP-1321) with the real resolver: seed 1 hits, seed 2 misses; the
# rounds left were 1 and 2. The outcomes must not change; only the miss's rounds now drop to 1.
@pytest.mark.parametrize("seed,achieved,success", [(1, "destroy", True), (2, "none", False)])
def test_engagement_outcome_unchanged_and_charged_for_seed(seed, achieved, success):
    world = _kinetic_world(ammo=2)
    sim, osys = _osys(world, seed=seed)
    order = osys.issue(_engage(salvo_n=1))
    sim.advance_to(order.earliest_window[0] + 1)
    (rec,) = _kinetic_log(world)
    assert (rec["achieved"], rec["success"]) == (achieved, success)
    assert world.assets["INT"].resources.ammo == 1


def test_missed_salvo_replays_identically():
    world, sim, _ = _missed_engagement()
    replayed = sim.replay()
    assert replayed.model_dump() == world.model_dump()
    assert replayed.assets["INT"].resources.ammo == 1


# -- FR-1470: jamming leaves the power rating alone ----------------------------------------------

@pytest.mark.parametrize("rating", [0.0, 250.0])
@pytest.mark.parametrize("success", [True, False])
def test_jam_leaves_power_rating_unchanged(rating, success):
    sat = _leo()
    world = WorldState(now=0)
    world.assets["SAT"] = Asset(id="SAT", owner="blue", kind="satellite", orbit=sat)
    world.assets["JAM"] = Asset(id="JAM", owner="red", kind="jammer", location=_subpoint(sat, minutes(40)),
                                resources=AssetResources(power_w=rating))
    sim, osys = _osys(world, resolver=_ForcedResolver(success=success))
    order = osys.issue(Order(cell="red", actor="JAM", action="jam", target="SAT",
                             params={"modulation": "barrage", "power_w": 200.0}))
    assert order.status == "queued", order.fail_reason
    sim.advance_to(order.earliest_window[0] + 1)
    assert world.effect_log and world.effect_log[-1]["template"] == "ew_jam"
    assert world.assets["JAM"].resources.power_w == rating


# Recorded at `a956951` (before IP-1320) with the real resolver: three jams from leo-isr-denial's
# JAM-NORTH. The outcomes must not change; only the jammer's power figure stops drifting (it was
# -380.0 after these three jams as built).
_RECORDED_JAM_OUTCOMES = [
    ("ew_jam", "electronic_warfare", "ISR-EO-1", "deny", True),
    ("ew_jam", "electronic_warfare", "ISR-EO-1", "deny", True),
    ("ew_jam", "electronic_warfare", "ISR-EO-1", "none", False),
]


@pytest.mark.parametrize("seed", [5, 11])
def test_jam_outcomes_unchanged_for_seed(seed):
    m = SessionManager(load_vignette("leo-isr-denial"), seed=seed)
    m.start()
    rating = m.world.assets["JAM-NORTH"].resources.power_w
    for mod in ("barrage", "spot", "sweep"):
        o = m.osys.issue(Order(cell="red", actor="JAM-NORTH", action="jam", target="ISR-EO-1",
                               params={"modulation": mod, "power_w": 200.0}))
        assert o.status == "queued", o.fail_reason
    m.sim.advance_to(m.sim.clock.now + 6 * 3600 * 1_000_000)
    rows = [(e["template"], e["category"], e["target"], e["achieved"], e["success"])
            for e in m.world.effect_log if e.get("template") == "ew_jam"]
    assert rows == _RECORDED_JAM_OUTCOMES
    assert m.world.assets["JAM-NORTH"].resources.power_w == rating
