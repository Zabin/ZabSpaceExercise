"""Scheduler ordering / sub-stepping and exact sim-time conversion."""

from __future__ import annotations

from spacesim.engine import Simulation, WorldState
from spacesim.engine import simtime


def test_events_fire_in_time_order_then_insertion_order():
    sim = Simulation(WorldState(now=0), seed=0)
    # Schedule out of order; two events share t=10.
    sim.schedule(20, "inc_counter", {"name": "log_b"})
    sim.schedule(10, "set_value", {"id": "first", "value": 1})
    sim.schedule(10, "set_value", {"id": "second", "value": 2})
    sim.schedule(5, "set_value", {"id": "zeroth", "value": 0})
    sim.advance_to(100)

    fired = [(e.sim_time, e.kind, e.payload.get("id")) for e in sim.eventlog.entries]
    assert fired == [
        (5, "set_value", "zeroth"),
        (10, "set_value", "first"),   # inserted before "second" at the same time
        (10, "set_value", "second"),
        (20, "inc_counter", None),
    ]


def test_advance_in_two_steps_matches_single_step():
    def run(steps):
        sim = Simulation(WorldState(now=0), seed=3)
        sim.schedule(10, "random_roll", {"into": "r"})
        sim.schedule(40, "random_roll", {"into": "r"})
        sim.schedule(70, "inc_counter", {"name": "c", "by": 5})
        for s in steps:
            sim.advance_to(s)
        return sim.world.model_dump_json()

    assert run([100]) == run([25, 55, 100])


def test_simtime_iso_round_trip_is_exact():
    micros = simtime.from_iso("2026-05-24T12:34:56.123456+00:00")
    assert simtime.to_iso(micros) == "2026-05-24T12:34:56.123456+00:00"
    assert simtime.seconds(90) == 90 * simtime.MICROS_PER_SECOND
    assert simtime.minutes(1) == simtime.seconds(60)
