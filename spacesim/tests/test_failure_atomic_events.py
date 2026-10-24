"""IP-1021 (ADR-0038) — failure-atomic event application.

When a handler raises during a live advance, the engine restores the live world and RNG to exactly
what the event log reproduces, logs a no-op failure record in the event's place, and keeps
advancing. Before this package the event was lost, its partial mutation and RNG draws stayed in
live state but were never reproduced by replay (a live/replay divergence against invariant 1), and
``advance_to`` raised.

Known limit (IP-1021 Design Decision 4): state a handler mutates *outside* ``WorldState`` and the
RNG is not restored. Replay does not reproduce such state either, so this is not new divergence.
"""

from __future__ import annotations

import pytest
from spacesim.engine import SavedSession, Simulation, WorldState
from spacesim.engine.simulation import replay

FAILURE_KIND = "handler_error"


def _mutate_draw_then_raise(world: WorldState, payload: dict, rng) -> None:
    world.counters["poisoned"] = world.counters.get("poisoned", 0) + 100
    world.entities["half"] = {"written": True}
    rng.randint(1, 1_000_000)  # an RNG draw that replay will never reproduce
    raise ValueError("boom after mutating")


def _raise_only(world: WorldState, payload: dict, rng) -> None:
    raise ValueError(f"wrong-length dv: {payload.get('dv')}")


def _sim(seed: int = 77) -> Simulation:
    sim = Simulation(WorldState(now=0), seed=seed)
    sim.register_handler("bad", _mutate_draw_then_raise)
    sim.register_handler("bad_clean", _raise_only)
    sim.schedule(5, "inc_counter", {"name": "a"})
    sim.schedule(10, "random_roll", {"into": "rolls", "sides": 20})
    sim.schedule(20, "bad", {"x": 1}, actor="blue")
    sim.schedule(30, "random_roll", {"into": "rolls", "sides": 6})
    sim.schedule(40, "inc_counter", {"name": "a", "by": 3})
    sim.schedule(500, "inc_counter", {"name": "late"})
    return sim


def _replayed(sim: Simulation) -> tuple[str, dict]:
    """World JSON + RNG state that replaying the log reproduces (no snapshots)."""
    from spacesim.engine.rng import SeededRng
    w = WorldState.model_validate(sim._initial_state)
    rng = SeededRng(sim._seed)
    handlers = sim.handlers()
    for e in sim.eventlog.entries:
        w.now = e.sim_time
        handlers[e.kind](w, e.payload, rng)
    w.now = sim.clock.now
    return w.model_dump_json(), rng.export_state()


@pytest.mark.verifies("NFR-1610", "FR-1120")
def test_raising_handler_leaves_live_state_equal_to_replay():
    sim = _sim()
    sim.advance_to(100)
    world_json, rng_state = _replayed(sim)
    assert sim.world.model_dump_json() == world_json
    assert sim.rng.export_state() == rng_state
    assert "poisoned" not in sim.world.counters
    assert "half" not in sim.world.entities
    assert sim.replay().model_dump_json() == sim.world.model_dump_json()


@pytest.mark.verifies("NFR-1610")
def test_advance_continues_past_the_failure():
    sim = _sim()
    sim.advance_to(100)  # must not raise
    assert sim.clock.now == 100
    assert sim.world.counters["a"] == 4  # both inc_counter events (t=5, t=40) fired
    kinds = [e.kind for e in sim.eventlog.entries]
    assert kinds == ["inc_counter", "random_roll", FAILURE_KIND, "random_roll", "inc_counter"]


@pytest.mark.verifies("NFR-1610")
def test_pending_events_after_the_target_survive():
    sim = _sim()
    sim.advance_to(100)
    sim.advance_to(600)
    assert sim.world.counters.get("late") == 1


@pytest.mark.verifies("NFR-1610", "FR-1120")
def test_failure_record_carries_the_failed_event_and_replays_as_noop():
    sim = _sim()
    sim.advance_to(100)
    rec = next(e for e in sim.eventlog.entries if e.kind == FAILURE_KIND)
    assert rec.sim_time == 20
    assert rec.actor == "blue"
    assert rec.payload["failed_kind"] == "bad"
    assert rec.payload["failed_payload"] == {"x": 1}
    assert rec.payload["error_type"] == "ValueError"
    assert "boom" in rec.payload["error"]
    # Replaying the record alone changes nothing.
    before = WorldState(now=0)
    from spacesim.engine.handlers import DEFAULT_HANDLERS
    from spacesim.engine.rng import SeededRng
    rng = SeededRng(1)
    snapshot_rng = rng.export_state()
    DEFAULT_HANDLERS[FAILURE_KIND](before, rec.payload, rng)
    assert before.model_dump() == WorldState(now=0).model_dump()
    assert rng.export_state() == snapshot_rng


@pytest.mark.verifies("NFR-1610", "FR-1120")
def test_save_round_trip_with_a_failure_record_reproduces_state():
    sim = _sim()
    sim.advance_to(100)
    saved = SavedSession.model_validate_json(sim.to_save().model_dump_json())
    rebuilt = replay(saved.initial_state, saved.seed, saved.eventlog,
                     handlers=sim.handlers(), final_time=saved.final_time)
    assert rebuilt.model_dump_json() == sim.world.model_dump_json()


@pytest.mark.verifies("NFR-1610")
def test_raise_without_prior_mutation_behaves_the_same():
    sim = Simulation(WorldState(now=0), seed=3)
    sim.register_handler("bad_clean", _raise_only)
    sim.schedule(10, "bad_clean", {"dv": [1, 2]})
    sim.schedule(20, "inc_counter", {"name": "a"})
    sim.advance_to(50)
    assert sim.world.counters["a"] == 1
    assert [e.kind for e in sim.eventlog.entries] == [FAILURE_KIND, "inc_counter"]
    assert sim.replay().model_dump_json() == sim.world.model_dump_json()


@pytest.mark.verifies("NFR-1610")
def test_world_identity_is_kept_so_session_references_stay_valid():
    """Design Decision 2: rollback restores in place; SessionManager's references stay valid."""
    from spacesim.content.vignette import load_vignette
    from spacesim.session.manager import SessionManager
    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=5)
    mgr.start()
    mgr.set_clock(False)
    mgr.sim.register_handler("bad", _mutate_draw_then_raise)
    world_obj = mgr.sim.world
    t = mgr.sim.clock.now
    mgr.sim.schedule(t + 1_000_000, "bad", {"x": 2})
    mgr.sim.advance_to(t + 120_000_000)
    assert mgr.sim.world is world_obj
    assert mgr.world is mgr.sim.world
    assert mgr.osys.world is mgr.sim.world
    assert "poisoned" not in mgr.world.counters
    assert any(e.kind == FAILURE_KIND for e in mgr.sim.eventlog.entries)
    assert mgr.sim.replay().model_dump_json() == mgr.sim.world.model_dump_json()
