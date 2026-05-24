"""Phase 1 gate: the deterministic-core property test.

This test *is* the rewind/undo/branch guarantee: replaying the same event log from the same seed
(from scratch, from a snapshot, or after a save round-trip) must reproduce byte-identical state.
If it ever fails, the cause is almost always a stray wall-clock read or un-seeded RNG. Per the
roadmap this test must stay green forever.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from spacesim.engine import SavedSession, Simulation, WorldState
from spacesim.engine.simulation import replay


def _build(events: list[tuple[int, str, dict]], seed: int) -> Simulation:
    sim = Simulation(WorldState(now=0), seed=seed)
    for t, kind, payload in events:
        sim.schedule(t, kind, payload)
    return sim


def _fixed_events() -> list[tuple[int, str, dict]]:
    return [
        (10, "inc_counter", {"name": "a", "by": 2}),
        (10, "random_roll", {"into": "rolls", "sides": 20}),  # same-time tie, deterministic order
        (5, "set_value", {"id": "x", "value": {"hp": 3}}),
        (30, "random_roll", {"into": "rolls", "sides": 6}),
        (20, "inc_counter", {"name": "a"}),
        (30, "set_value", {"id": "x", "value": {"hp": 1}}),
    ]


def test_replay_from_scratch_matches_live():
    end = 100
    sim = _build(_fixed_events(), seed=1234)
    sim.advance_to(end)
    live = sim.world.model_dump_json()

    replayed = replay(WorldState(now=0).model_dump(), 1234, sim.eventlog, final_time=end)
    assert replayed.model_dump_json() == live


def test_replay_from_midway_snapshot_matches_live():
    sim = _build(_fixed_events(), seed=99)
    sim.advance_to(15)  # fires the events at t=5 and t=10
    sim.snapshot()
    sim.advance_to(100)
    live = sim.world.model_dump_json()

    # Replay using the helper on the simulation (prefers the snapshot shortcut).
    assert sim.replay().model_dump_json() == live


def test_save_round_trip_reproduces_state():
    sim = _build(_fixed_events(), seed=7)
    sim.advance_to(50)
    sim.snapshot()
    sim.advance_to(100)
    live = sim.world.model_dump_json()

    save_json = sim.to_save().model_dump_json()
    loaded = SavedSession.model_validate_json(save_json)
    replayed = replay(
        loaded.initial_state,
        loaded.seed,
        loaded.eventlog,
        snapshots=loaded.snapshots,
        final_time=loaded.final_time,
    )
    assert replayed.model_dump_json() == live


def test_different_seed_changes_random_outcome():
    a = _build(_fixed_events(), seed=1)
    a.advance_to(100)
    b = _build(_fixed_events(), seed=2)
    b.advance_to(100)
    assert a.world.counters["rolls"] != b.world.counters["rolls"]


def test_cannot_advance_backwards():
    sim = _build([], seed=1)
    sim.advance_to(50)
    try:
        sim.advance_to(10)
    except ValueError:
        return
    raise AssertionError("advancing the clock backwards should raise")


_event_strategy = st.lists(
    st.tuples(
        st.integers(min_value=0, max_value=1000),  # time
        st.sampled_from(["inc_counter", "random_roll", "set_value"]),
        st.integers(min_value=0, max_value=5),  # disambiguator for payload building
    ),
    max_size=40,
)


@settings(max_examples=200, deadline=None)
@given(raw=_event_strategy, seed=st.integers(min_value=0, max_value=2**31 - 1))
def test_property_replay_is_byte_identical(raw, seed):
    events: list[tuple[int, str, dict]] = []
    for t, kind, k in raw:
        if kind == "inc_counter":
            payload = {"name": f"c{k}", "by": k}
        elif kind == "random_roll":
            payload = {"into": f"r{k}", "sides": k + 2}
        else:
            payload = {"id": f"e{k}", "value": {"v": k}}
        events.append((t, kind, payload))

    end = 1001
    sim = _build(events, seed=seed)
    sim.advance_to(end)
    live = sim.world.model_dump_json()

    replayed = replay(WorldState(now=0).model_dump(), seed, sim.eventlog, final_time=end)
    assert replayed.model_dump_json() == live
