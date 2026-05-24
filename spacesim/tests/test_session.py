"""Phase-4 end-to-end: Vignette 1 through the SessionAPI, fog-of-war, and rewind-to-a-branch."""

from __future__ import annotations

from spacesim.engine.orders import Order
from spacesim.session import InProcessSession


def _loaded(seed=1):
    api = InProcessSession()
    sid = api.load_vignette("leo-isr-denial", seed=seed)
    api.start(sid)
    return api, sid


def test_fog_of_war_hides_other_cells_assets():
    api, sid = _loaded()
    red = api.get_view(sid, "red")
    blue = api.get_view(sid, "blue")

    red_ids = {a["id"] for a in red.own_assets}
    blue_ids = {a["id"] for a in blue.own_assets}
    assert "ISR-EO-1" in blue_ids and "ISR-EO-1" not in red_ids   # Red can't see Blue's sat
    assert "JAM-NORTH" in red_ids and "JAM-NORTH" not in blue_ids
    # No Blue asset/hidden state leaks anywhere into the Red view.
    assert "ISR-EO-1" not in red.model_dump_json()
    # Red holds no tracks on Blue (no custody granted yet).
    assert red.known_tracks == []

    # White Cell sees ground truth (both sides) via god-view.
    god = api.get_godview(sid)
    assert {"ISR-EO-1", "JAM-NORTH"} <= set(god.assets.keys())


def test_reveal_asset_inject_grants_blue_a_track_on_red():
    api, sid = _loaded()
    assert api.get_view(sid, "blue").known_tracks == []
    api.fire_inject(sid, "commercial_imagery_leak")
    tracks = api.get_view(sid, "blue").known_tracks
    assert any(t["object"] == "RED-SURF" for t in tracks)


def test_blue_delivers_imagery_then_rewind_lets_red_deny_it():
    api, sid = _loaded()
    mgr = api._sessions[sid]
    start = mgr.world.now
    fork = start  # rewind back to the very start to try the other branch

    # --- Branch A: Blue downlinks at the next station pass, unopposed → Blue wins. ---
    ack = api.issue_order(sid, "blue", Order(cell="blue", actor="ISR-EO-1", action="downlink",
                                             params={"via": "GS-NORTH"}))
    assert ack.status == "queued" and ack.earliest_window is not None
    api.advance_to(sid, start + 800 * 1_000_000)   # past the ~51-673s downlink window
    assert mgr.world.mission.get("imagery_delivered") is True
    assert api.objectives(sid)["blue"]["deliver_isr"] is True

    # --- Rewind to the fork and take a different branch. ---
    api.rewind_to(sid, fork)
    assert mgr.world.mission.get("imagery_delivered") is None   # state truly rewound

    # --- Branch B: Red jams the downlink first; Blue's delivery is blocked → Red denies. ---
    api.issue_order(sid, "red", Order(cell="red", actor="JAM-NORTH", action="jam",
                                      target="ISR-EO-1", params={"success_prob": 1.0, "outcome": "deny"}))
    api.issue_order(sid, "blue", Order(cell="blue", actor="ISR-EO-1", action="downlink",
                                       params={"via": "GS-NORTH"}))
    api.advance_to(sid, start + 800 * 1_000_000)
    assert mgr.world.mission.get("imagery_delivered") is None   # jammed: nothing delivered
    api.advance_to(sid, mgr.ctx.landing_deadline + 1)
    objs = api.objectives(sid)
    assert objs["blue"]["deliver_isr"] is False
    assert objs["red"]["deny_isr"] is True

    # Blue perceives a symptom on its own sat, but the jammer's identity is withheld (fog).
    effects = api.get_view(sid, "blue").visible_effects
    assert any(e["target"] == "ISR-EO-1" and e["symptom"] == "deny" and e["attributed"] is False
               for e in effects)
