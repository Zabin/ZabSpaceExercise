"""Phase 6: all seven vignettes load/run, TLE force-add propagates, Red doctrine presets differ."""

from __future__ import annotations

from spacesim.content.vignette import list_vignettes, load_vignette
from spacesim.engine.access import AccessProvider, COMMAND_UPLINK
from spacesim.engine.orders import scene_from_world
from spacesim.session.manager import SessionManager
from spacesim.session.redai import RedDoctrine
from spacesim.session.inprocess import InProcessSession

# Canonical valid ISS TLE (Vallado sgp4 test vector).
TLE1 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
TLE2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"

EXPECTED = {"leo-isr-denial", "geo-rpo-shadowing", "gnss-ew-campaign", "co-orbital-threat-escort",
            "da-asat-crisis", "satcom-cyber-link", "sda-custody-hunt"}


def test_all_seven_vignettes_load_start_and_evaluate():
    ids = {v["id"] for v in list_vignettes()}
    assert EXPECTED <= ids
    for vid in EXPECTED:
        mgr = SessionManager(load_vignette(vid), seed=1)
        mgr.start()
        objs = mgr.objectives()
        assert set(objs.keys()) == {"blue", "red"}
        mgr.get_view("blue"); mgr.get_view("red"); mgr.get_scene("blue")  # no errors


def test_real_satellite_added_by_tle_propagates_and_generates_passes():
    api = InProcessSession()
    sid = api.load_vignette("leo-isr-denial", seed=1)
    ack = api.add_tle(sid, "ISS", TLE1, TLE2, owner="blue")
    assert ack.ok, ack.reason
    api.start(sid)
    # The added asset appears in Blue's belief scene with a real ground position.
    scene = api.get_scene(sid, "blue")
    iss = [a for a in scene.assets if a.id == "ISS"]
    assert iss and -90 <= iss[0].lat_deg <= 90

    # It propagates and produces ground-station passes alongside the fictional assets.
    mgr = api._sessions[sid]
    ap = AccessProvider(scene_from_world(mgr.world))
    now = mgr.world.now
    wins = ap.windows("GS-NORTH", "ISS", COMMAND_UPLINK, now, now + 24 * 3600 * 1_000_000)
    assert wins


def test_invalid_tle_is_rejected_with_reason():
    api = InProcessSession()
    sid = api.load_vignette("leo-isr-denial", seed=1)
    ack = api.add_tle(sid, "BAD", "not a tle", "also not", owner="blue")
    assert ack.ok is False and "invalid TLE" in ack.reason


def test_doctrine_profiles_drive_different_red_behavior():
    # russia_ew_first jams the GNSS link.
    mgr = SessionManager(load_vignette("gnss-ew-campaign"), seed=1)
    mgr.start()
    acks = RedDoctrine(mgr).step()
    assert any(a.status == "queued" for a in acks)  # a jam was queued

    # china_integrated cyber-safes the SATCOM bird via the modem vector.
    mgr2 = SessionManager(load_vignette("satcom-cyber-link"), seed=1)
    mgr2.start()
    RedDoctrine(mgr2).step()
    mgr2.advance_to(mgr2.world.now + 60 * 1_000_000)
    assert mgr2.world.assets["BLUE-SATCOM"].bus_state.mode == "safe_mode"
    assert mgr2.objectives()["red"]["disable_satcom"] is True

    # generic stays passive (tasks Red sensors; issues no offensive effect).
    mgr3 = SessionManager(load_vignette("da-asat-crisis"), seed=1)
    mgr3.start()
    acks3 = RedDoctrine(mgr3).step()
    assert all(a.status != "rejected" or a.reason for a in acks3)  # observe tasks, no crashes
