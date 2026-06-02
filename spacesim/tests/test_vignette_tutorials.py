"""Every numbered vignette ships a player tutorial whose winning moves actually work.

Two layers of protection:
  1. Structural — each vignette has blue+red tutorial blocks, ≥3 steps each, and every
     order-issuing step names an actor (review/advance are exempt). This is what the in-UI
     Tutorial panel renders and what docs/training/11-vignette-playbooks.md mirrors.
  2. Behavioural — the achievable objective-flipping sequences from those tutorials are driven
     through the SessionManager and asserted to flip the objective. Adversarial/geometry/ROE-
     gated objectives (proximity close-approach, kinetic neutralize/destroy without a track,
     evasion maneuvers that need a TT&C station) are documented in the tutorial with their gate
     and are not asserted here — only the moves a cell can complete on its own are.
"""

from __future__ import annotations

import pytest

from spacesim.content.vignette import load_vignette
from spacesim.engine.orders import Order
from spacesim.session.manager import SessionManager

NUMBERED = [
    "leo-isr-denial", "geo-rpo-shadowing", "gnss-ew-campaign", "co-orbital-threat-escort",
    "da-asat-crisis", "satcom-cyber-link", "sda-custody-hunt", "multi-domain-taiwan",
]


def _mgr(vid, **overrides):
    mgr = SessionManager(load_vignette(vid), seed=1, overrides=overrides or None)
    mgr.start()
    return mgr


def _issue(mgr, cell, **kw):
    return mgr.issue_order(cell, Order(cell=cell, **kw))


# -- layer 1: structure -------------------------------------------------------

@pytest.mark.parametrize("vid", NUMBERED)
def test_every_vignette_has_a_two_cell_tutorial(vid):
    vig = load_vignette(vid)
    blue = vig.tutorial.get("blue", [])
    red = vig.tutorial.get("red", [])
    assert len(blue) >= 3, f"{vid}: blue tutorial too short"
    assert len(red) >= 3, f"{vid}: red tutorial too short"
    for side, steps in (("blue", blue), ("red", red)):
        for step in steps:
            assert "title" in step and "action" in step, f"{vid}.{side}: malformed step {step}"
            if step["action"] not in ("review", "advance"):
                assert step.get("actor"), f"{vid}.{side} step {step.get('n')}: order step needs an actor"


# -- layer 2: the winning moves actually flip the objective -------------------

def test_01_blue_delivers_and_red_denies():
    mgr = _mgr("leo-isr-denial")
    dl = _issue(mgr, "blue", actor="ISR-EO-1", action="downlink", params={"via": "GS-NORTH"})
    assert dl.status == "queued" and dl.earliest_window
    mgr.advance_to(dl.earliest_window[1] + 1)
    assert mgr.objectives()["blue"]["deliver_isr"] is True

    mgr = _mgr("leo-isr-denial")
    jam = _issue(mgr, "red", actor="JAM-NORTH", action="jam", target="ISR-EO-1",
                 params={"success_prob": 1.0, "outcome": "deny"})
    assert jam.status == "queued"
    mgr.advance_to(mgr.ctx.landing_deadline + 1)
    assert mgr.objectives()["red"]["deny_isr"] is True
    # The ROE-teaching step really is rejected.
    eng = _issue(mgr, "red", actor="RED-ASAT", action="engage", target="ISR-EO-1")
    assert eng.status == "rejected" and eng.reason == "roe_kinetic_not_authorized"


def test_02_blue_holds_geo_custody():
    mgr = _mgr("geo-rpo-shadowing")
    ob = _issue(mgr, "blue", actor="BLUE-OPT", action="observe", target="RED-INSP",
                params={"intent": "characterize", "classification": "hostile"})
    assert ob.status == "queued" and ob.earliest_window
    mgr.advance_to(ob.earliest_window[0] + 1)
    assert mgr.objectives()["blue"]["maintain_custody"] is True


def test_03_blue_keeps_pnt_and_red_denies():
    mgr = _mgr("gnss-ew-campaign", red_ew_intensity="none")
    mgr.advance_to(mgr.ctx.landing_deadline + 1)
    assert mgr.objectives()["blue"]["maintain_service"] is True

    mgr = _mgr("gnss-ew-campaign")
    jam = _issue(mgr, "red", actor="RED-JAM", action="jam", target="BLUE-GNSS",
                 params={"success_prob": 1.0, "outcome": "deny"})
    assert jam.status == "queued"
    mgr.advance_to(jam.earliest_window[0] + 1)
    assert mgr.objectives()["red"]["deny_pnt"] is True


def test_04_blue_hva_survives_without_roe():
    mgr = _mgr("co-orbital-threat-escort")
    ob = _issue(mgr, "blue", actor="BLUE-RADAR", action="observe", target="RED-COORB",
                params={"intent": "characterize", "classification": "hostile"})
    assert ob.status == "queued"
    mgr.advance_to(mgr.ctx.landing_deadline + 1)
    # No kinetic ROE and no organic safing path → HVA survives by default; neutralize cannot complete.
    assert mgr.objectives()["blue"]["hva_survives"] is True
    assert mgr.objectives()["red"]["neutralize_hva"] is False


def test_05_red_destroys_with_weapons_quality_track():
    mgr = _mgr("da-asat-crisis")
    ob = _issue(mgr, "red", actor="RED-RADAR", action="observe", target="BLUE-SAT",
                params={"intent": "characterize", "classification": "hostile"})
    mgr.advance_to(ob.earliest_window[0] + 1)
    tr = mgr.world.track_for("red", "BLUE-SAT")
    assert tr is not None and tr.is_weapons_quality(mgr.world.now)  # the engage gate
    eng = _issue(mgr, "red", actor="RED-ASAT", action="engage", target="BLUE-SAT",
                 params={"success_prob": 1.0})
    assert eng.status == "queued" and eng.earliest_window
    mgr.advance_to(eng.earliest_window[1] + 1)
    assert mgr.objectives()["red"]["destroy_sat"] is True
    assert mgr.objectives()["blue"]["avoid_debris"] is False
    assert len(mgr.world.debris) > 0  # the irreversible cost the vignette teaches


def test_06_red_safes_satcom_off_pass():
    mgr = _mgr("satcom-cyber-link")
    cy = _issue(mgr, "red", actor="RED-CYBER", action="cyber", target="BLUE-SATCOM",
                params={"access_vector": "ground_modem", "outcome": "safe_mode",
                        "success_prob": 1.0, "sm_susceptibility": 1.0})
    assert cy.status == "queued" and cy.earliest_window is None  # cyber is not window-gated
    mgr.advance_to(mgr.world.now + 60_000_000)
    assert mgr.objectives()["red"]["disable_satcom"] is True


def test_07_blue_holds_custody_and_red_breaks_it_on_lapse():
    mgr = _mgr("sda-custody-hunt")
    ob = _issue(mgr, "blue", actor="BLUE-RADAR-1", action="observe", target="RED-OBJ",
                params={"intent": "characterize", "classification": "hostile"})
    assert ob.status == "queued" and ob.earliest_window
    mgr.advance_to(ob.earliest_window[0] + 1)
    assert mgr.objectives()["blue"]["maintain_custody"] is True

    # Red wins by default if Blue never re-tasks before the deadline.
    mgr = _mgr("sda-custody-hunt")
    mgr.advance_to(mgr.ctx.landing_deadline + 1)
    assert mgr.objectives()["red"]["break_custody"] is True


def test_08_capstone_blue_isr_and_red_cyber():
    mgr = _mgr("multi-domain-taiwan")
    dl = _issue(mgr, "blue", actor="ISR-EO-1", action="downlink", params={"via": "GS-NORTH"})
    assert dl.status == "queued" and dl.earliest_window
    ob = _issue(mgr, "blue", actor="BLUE-OPT", action="observe", target="RED-INSP",
                params={"intent": "characterize", "classification": "hostile"})
    assert ob.status == "queued"
    cy = _issue(mgr, "red", actor="RED-CYBER", action="cyber", target="SATCOM-1",
                params={"access_vector": "ground_modem", "outcome": "safe_mode",
                        "success_prob": 1.0, "sm_susceptibility": 1.0})
    assert cy.status == "queued" and cy.earliest_window is None
    mgr.advance_to(mgr.world.now + 60_000_000)
    assert mgr.objectives()["red"]["disable_satcom"] is True
