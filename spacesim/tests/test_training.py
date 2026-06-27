"""The training vignette: every documented Blue and Red walkthrough step actually executes.

Driving the same orders the manual prescribes (through the SessionAPI) makes the guided
walkthrough a *verified* sequence even though the browser GUI is unverified headless.
"""

from __future__ import annotations

from spacesim.content.vignette import load_vignette
from spacesim.engine.orders import Order
from spacesim.session.manager import SessionManager


def _mgr():
    mgr = SessionManager(load_vignette("training-basics"), seed=1)
    mgr.start()
    return mgr


def test_vignette_has_at_least_five_steps_per_cell():
    vig = load_vignette("training-basics")
    assert len(vig.tutorial.get("blue", [])) >= 5
    assert len(vig.tutorial.get("red", [])) >= 5
    # Every step that issues an order names an actor (review/advance steps are exempt).
    for side in ("blue", "red"):
        for step in vig.tutorial[side]:
            if step["action"] not in ("review", "advance"):
                assert step.get("actor"), step


def test_blue_walkthrough_executes_and_wins():
    mgr = _mgr()

    # Step 2 — task RADAR-TRN to characterize RED-TGT → build custody.
    task = mgr.issue_order("blue", Order(cell="blue", actor="RADAR-TRN", action="observe",
                                         target="RED-TGT", params={"intent": "characterize", "classification": "hostile"}))
    assert task.status == "queued"
    mgr.advance_to(task.earliest_window[0] + 1)
    tr = mgr.world.track_for("blue", "RED-TGT")
    assert tr is not None and tr.characterized
    assert mgr.objectives()["blue"]["keep_custody"] is True

    # Step 3 — plan the downlink (queues to the next GS-TRN pass).
    dl = mgr.issue_order("blue", Order(cell="blue", actor="ISR-EO-1", action="downlink", params={"via": "GS-TRN"}))
    assert dl.status == "queued" and dl.delivery_path == "ground_uplink" and dl.earliest_window

    # Step 4 — advance past the downlink window → imagery delivered.
    mgr.advance_to(dl.earliest_window[1] + 1)
    assert mgr.world.mission.get("imagery_delivered") is True
    assert mgr.objectives()["blue"]["deliver_isr"] is True

    # Step 5 — maneuver to preserve the orbit (queues to the next command pass).
    mv = mgr.issue_order("blue", Order(cell="blue", actor="ISR-EO-1", action="maneuver",
                                       params={"dv": [0.0, 5.0, 0.0], "via": "GS-TRN"}))
    assert mv.status == "queued"


def test_red_walkthrough_executes_and_denies():
    mgr = _mgr()

    # Step 2 — find the Blue ISR satellite.
    obs = mgr.issue_order("red", Order(cell="red", actor="RED-RDR", action="observe",
                                       target="ISR-EO-1", params={"intent": "track"}))
    assert obs.status == "queued"
    mgr.advance_to(obs.earliest_window[0] + 1)
    assert mgr.world.track_for("red", "ISR-EO-1") is not None

    # Step 3 — jam the downlink (queues to the footprint window).
    jam = mgr.issue_order("red", Order(cell="red", actor="JAM-TRN", action="jam", target="ISR-EO-1",
                                       params={"modulation": "barrage", "power_w": 200.0}))
    assert jam.status == "queued"

    # Step 4 — cyber the modem off-pass → safe mode.
    cy = mgr.issue_order("red", Order(cell="red", actor="RED-CYBER", action="cyber", target="ISR-EO-1",
                                      params={"vector": "ground_modem", "payload": "seize_c2"}))
    assert cy.status == "queued" and cy.earliest_window is None  # cyber is not window-gated
    mgr.advance_to(mgr.world.now + 60 * 1_000_000)
    assert mgr.world.assets["ISR-EO-1"].bus_state.mode == "safe_mode"
    assert mgr.objectives()["red"]["disable_isr"] is True

    # Step 6 — a kinetic strike is rejected (ROE off by default).
    eng = mgr.issue_order("red", Order(cell="red", actor="RED-ASAT", action="engage", target="ISR-EO-1"))
    assert eng.status == "rejected" and eng.reason == "roe_kinetic_not_authorized"

    # Step 5 — past the delivery window with nothing delivered → Red denies.
    mgr.advance_to(mgr.ctx.landing_deadline + 1)
    assert mgr.objectives()["red"]["deny_isr"] is True


def test_scene_exposes_subsolar_point_for_globe_shading():
    mgr = _mgr()
    scene = mgr.get_scene("blue")
    assert -90.0 <= scene.sun_lat_deg <= 90.0
    assert -180.0 <= scene.sun_lon_deg <= 180.0
