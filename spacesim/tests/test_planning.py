"""Phase 4.5: delivery paths (ISL/stored), the task->custody->unlock loop, and sensor contention."""

from __future__ import annotations

from spacesim.engine.entities import Asset, AssetResources, Sensor
from spacesim.engine.geometry import GeoPoint, R_EARTH_EQ, ecef_to_geodetic, eci_to_ecef
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import Order, OrderSystem
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.simtime import minutes
from spacesim.engine.simulation import Simulation
from spacesim.engine.world import WorldState

PROP = ModeratePropagator()


def _leo(ta=0.0):
    return OrbitState(a_m=R_EARTH_EQ + 550e3, e=0.0, i_deg=51.6, raan_deg=33, argp_deg=0, ta_deg=ta, epoch=0)


def _subpoint(orbit, t):
    r, _ = PROP.rv(orbit, t)
    g = ecef_to_geodetic(eci_to_ecef(r, t))
    g.alt_m = 0.0
    return g


def _sim(world, roe=None, seed=5):
    # IP-1172: OrderSystem.roe is now always cell-keyed; mirror a flat convenience dict to
    # both cells (matches content/vignette.py's own legacy-parameter fallback semantics).
    if roe is not None and "blue" not in roe and "red" not in roe:
        roe = {"blue": dict(roe), "red": dict(roe)}
    sim = Simulation(world, seed=seed)
    return sim, OrderSystem(sim, roe=roe)


def test_command_delivered_via_isl_when_sooner_than_a_distant_ground_pass():
    world = WorldState(now=0)
    world.assets["SAT"] = Asset(id="SAT", owner="blue", kind="satellite", orbit=_leo(),
                                resources=AssetResources(delta_v_ms=100.0))
    # Only ground station is far away (next pass ~17 h); a GEO relay has immediate crosslink LOS.
    world.assets["FAR-GS"] = Asset(id="FAR-GS", owner="blue", kind="ground_station",
                                   location=GeoPoint(lat_deg=-60.0, lon_deg=-90.0))
    world.assets["RELAY"] = Asset(id="RELAY", owner="blue", kind="satellite", isl_capable=True,
                                  orbit=OrbitState(a_m=42164e3, e=0.0, i_deg=0.0, raan_deg=0, argp_deg=0, ta_deg=0, epoch=0))

    sim, osys = _sim(world)
    order = osys.issue(Order(cell="blue", actor="SAT", action="maneuver",
                             params={"dv": [0.0, 5.0, 0.0], "via": "FAR-GS"}))
    assert order.status == "queued"
    assert order.delivery_path == "isl_relay"
    assert order.earliest_window[0] < minutes(60)   # sooner than the distant ground pass

    a_before = world.assets["SAT"].orbit.a_m
    sim.advance_to(order.earliest_window[0] + 1)
    assert world.assets["SAT"].orbit.a_m != a_before  # command actually executed


def test_stored_program_executes_at_its_preloaded_time_without_a_pass():
    world = WorldState(now=0)
    world.assets["SAT"] = Asset(id="SAT", owner="blue", kind="satellite", orbit=_leo(),
                                resources=AssetResources(delta_v_ms=100.0), stored_program=True)
    sim, osys = _sim(world)
    order = osys.issue(Order(cell="blue", actor="SAT", action="maneuver",
                             params={"dv": [0.0, 3.0, 0.0], "stored_at": minutes(5)}))
    assert order.delivery_path == "stored_program"
    assert order.earliest_window == (minutes(5), minutes(5))
    sim.advance_to(minutes(6))
    assert world.assets["SAT"].resources.delta_v_ms < 100.0  # burned onboard at the stored time


def test_task_then_custody_then_unlock_engagement():
    world = WorldState(now=0)
    sat = _leo()
    world.assets["RSAT"] = Asset(id="RSAT", owner="red", kind="satellite", orbit=sat)
    world.assets["INT"] = Asset(id="INT", owner="blue", kind="interceptor",
                                location=_subpoint(sat, 0), resources=AssetResources(ammo=1))
    world.sensors["RADAR"] = Sensor(id="RADAR", owner="blue", kind="ground_radar", location=_subpoint(sat, 0))

    sim, osys = _sim(world, roe={"kinetic_authorized": True})

    # Engagement blocked: no weapons-quality track yet.
    blocked = osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT"))
    assert blocked.status == "rejected" and blocked.fail_reason == "no_weapons_quality_track"

    # Task the sensor (auto-select) to characterize the object; report builds custody.
    task = osys.issue(Order(cell="blue", actor="auto", action="observe", target="RSAT",
                            params={"intent": "characterize", "gain": 0.9, "classification": "hostile"}))
    assert task.status == "queued" and task.actor == "RADAR"
    sim.advance_to(task.earliest_window[0] + 1)   # report fires at the window start
    tr = world.track_for("blue", "RSAT")
    assert tr.characterized and tr.current_confidence(world.now) > 0.8  # confidence rose, characterized
    assert tr.is_weapons_quality(world.now)

    # Now the same engagement validates and queues.
    ok = osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT", params={"interceptor_class": "mrbm_kkv"}))
    assert ok.status == "queued"


def test_sensor_contention_serializes_tasks_onto_later_windows():
    world = WorldState(now=0)
    sat = _leo()
    world.assets["RSAT"] = Asset(id="RSAT", owner="red", kind="satellite", orbit=sat)
    world.sensors["RADAR"] = Sensor(id="RADAR", owner="blue", kind="ground_radar", location=_subpoint(sat, 0))

    sim, osys = _sim(world)
    first = osys.issue(Order(cell="blue", actor="RADAR", action="observe", target="RSAT", params={"intent": "track"}))
    second = osys.issue(Order(cell="blue", actor="RADAR", action="observe", target="RSAT", params={"intent": "track"}))
    assert first.status == "queued" and second.status == "queued"
    # A sensor does one thing at a time: the second task is pushed to a later, non-overlapping pass.
    assert second.earliest_window[0] >= first.earliest_window[1]


def test_sensor_bookings_reconstructed_after_rewind():
    """Bookings for executed observe events are restored from the eventlog after a rewind.

    Without reconstruction, rewinding past an executed observe would clear the booking and
    allow a second observe to be booked in the same window, violating sensor contention.
    """
    from spacesim.session.manager import SessionManager
    from spacesim.content.vignette import load_vignette, build_world

    vig = load_vignette("leo-isr-denial")
    world, ctx = build_world(vig)
    mgr = SessionManager(vig, seed=42)
    mgr.start()

    # Find a sensor owned by blue and any orbital asset to observe.
    sid = next(s for s, sensor in mgr.world.sensors.items() if sensor.owner == "blue")
    target = next(a for a, asset in mgr.world.assets.items() if asset.orbit is not None)

    obs = Order(cell="blue", actor=sid, action="observe", target=target, params={"intent": "track"})
    ack = mgr.issue_order("blue", obs)
    assert ack.ok, f"observe rejected: {ack.reason}"
    win_start, win_end = ack.earliest_window

    # Advance past the observation window so the event fires and enters the eventlog.
    mgr.sim.advance_to(win_end + 1)
    assert any(e.kind == "execute_observe" for e in mgr.sim.eventlog.entries)

    # Rewind to just before the window ended (the event is still in the kept eventlog).
    mgr.rewind_to(win_start + 1)

    # The booking must be reconstructed: the sensor should be contended for that window.
    bookings = mgr.osys._sensor_bookings.get(sid, [])
    assert any(b0 <= win_start and b1 >= win_end for (b0, b1) in bookings), \
        f"booking for [{win_start}, {win_end}] not restored; got {bookings}"
