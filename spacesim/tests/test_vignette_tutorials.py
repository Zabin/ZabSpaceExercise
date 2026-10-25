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

from spacesim.content.vignette import list_vignettes, load_vignette
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

@pytest.mark.verifies("NFR-3400")
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

@pytest.mark.verifies("NFR-3400")
def test_01_blue_delivers_and_red_denies():
    mgr = _mgr("leo-isr-denial")
    dl = _issue(mgr, "blue", actor="ISR-EO-1", action="downlink", params={"via": "GS-NORTH"})
    assert dl.status == "queued" and dl.earliest_window
    mgr.advance_to(dl.earliest_window[1] + 1)
    assert mgr.objectives()["blue"]["deliver_isr"] is True

    mgr = _mgr("leo-isr-denial")
    jam = _issue(mgr, "red", actor="JAM-NORTH", action="jam", target="ISR-EO-1",
                 params={"modulation": "barrage", "power_w": 200.0})
    assert jam.status == "queued"
    mgr.advance_to(mgr.ctx.landing_deadline + 1)
    assert mgr.objectives()["red"]["deny_isr"] is True
    # The ROE-teaching step really is rejected.
    eng = _issue(mgr, "red", actor="RED-ASAT", action="engage", target="ISR-EO-1")
    assert eng.status == "rejected" and eng.reason == "roe_kinetic_not_authorized"


@pytest.mark.verifies("NFR-3400")
def test_02_blue_holds_geo_custody():
    mgr = _mgr("geo-rpo-shadowing")
    ob = _issue(mgr, "blue", actor="BLUE-OPT", action="observe", target="RED-INSP",
                params={"intent": "characterize", "classification": "hostile"})
    assert ob.status == "queued" and ob.earliest_window
    mgr.advance_to(ob.earliest_window[0] + 1)
    assert mgr.objectives()["blue"]["maintain_custody"] is True


@pytest.mark.verifies("NFR-3400")
def test_03_blue_keeps_pnt_and_red_denies():
    mgr = _mgr("gnss-ew-campaign", red_ew_intensity="none")
    mgr.advance_to(mgr.ctx.landing_deadline + 1)
    assert mgr.objectives()["blue"]["maintain_service"] is True

    mgr = _mgr("gnss-ew-campaign")
    jam = _issue(mgr, "red", actor="RED-JAM", action="jam", target="BLUE-GNSS",
                 params={"modulation": "barrage", "power_w": 200.0})
    assert jam.status == "queued"
    mgr.advance_to(jam.earliest_window[0] + 1)
    assert mgr.objectives()["red"]["deny_pnt"] is True


@pytest.mark.verifies("NFR-3400")
def test_04_blue_hva_survives_without_roe():
    mgr = _mgr("co-orbital-threat-escort")
    ob = _issue(mgr, "blue", actor="BLUE-RADAR", action="observe", target="RED-COORB",
                params={"intent": "characterize", "classification": "hostile"})
    assert ob.status == "queued"
    mgr.advance_to(mgr.ctx.landing_deadline + 1)
    # No kinetic ROE and no organic safing path → HVA survives by default; neutralize cannot complete.
    assert mgr.objectives()["blue"]["hva_survives"] is True
    assert mgr.objectives()["red"]["neutralize_hva"] is False


@pytest.mark.verifies("NFR-3400")
def test_05_red_destroys_with_weapons_quality_track():
    mgr = _mgr("da-asat-crisis")
    ob = _issue(mgr, "red", actor="RED-RADAR", action="observe", target="BLUE-SAT",
                params={"intent": "characterize", "classification": "hostile"})
    mgr.advance_to(ob.earliest_window[0] + 1)
    tr = mgr.world.track_for("red", "BLUE-SAT")
    assert tr is not None and tr.is_weapons_quality(mgr.world.now)  # the engage gate
    eng = _issue(mgr, "red", actor="RED-ASAT", action="engage", target="BLUE-SAT",
                 params={"interceptor_class": "mrbm_kkv"})
    assert eng.status == "queued" and eng.earliest_window
    mgr.advance_to(eng.earliest_window[1] + 1)
    assert mgr.objectives()["red"]["destroy_sat"] is True
    assert mgr.objectives()["blue"]["avoid_debris"] is False
    assert len(mgr.world.debris) > 0  # the irreversible cost the vignette teaches


@pytest.mark.verifies("NFR-3400")
def test_06_red_safes_satcom_off_pass():
    mgr = _mgr("satcom-cyber-link")
    cy = _issue(mgr, "red", actor="RED-CYBER", action="cyber", target="BLUE-SATCOM",
                params={"vector": "ground_modem", "payload": "seize_c2"})
    assert cy.status == "queued" and cy.earliest_window is None  # cyber is not window-gated
    mgr.advance_to(mgr.world.now + 60_000_000)
    assert mgr.objectives()["red"]["disable_satcom"] is True


@pytest.mark.verifies("NFR-3400")
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


@pytest.mark.verifies("NFR-3400")
def test_08_capstone_blue_isr_and_red_cyber():
    mgr = _mgr("multi-domain-taiwan")
    dl = _issue(mgr, "blue", actor="ISR-EO-1", action="downlink", params={"via": "GS-NORTH"})
    assert dl.status == "queued" and dl.earliest_window
    ob = _issue(mgr, "blue", actor="BLUE-OPT", action="observe", target="RED-INSP",
                params={"intent": "characterize", "classification": "hostile"})
    assert ob.status == "queued"
    cy = _issue(mgr, "red", actor="RED-CYBER", action="cyber", target="SATCOM-1",
                params={"vector": "ground_modem", "payload": "seize_c2"})
    assert cy.status == "queued" and cy.earliest_window is None
    mgr.advance_to(mgr.world.now + 60_000_000)
    assert mgr.objectives()["red"]["disable_satcom"] is True


# -- training-basics (Stage 0 onboarding): the script a learner follows, step by step ------------
#
# The numbered-vignette tests above stop at "the winning move flips the objective". The onboarding
# vignette is the one every learner follows *literally*, so these drive each cell's step script in
# order on a fixed seed and assert the timing and expectation each step states (owner decision
# 2026-10-25, release-candidate-1 assessment N2).

_TB = "training-basics"
_RADAR_OBS = dict(actor="RADAR-TRN", action="observe", target="RED-TGT",
                  params={"intent": "characterize", "classification": "hostile"})


def _tb_steps(side):
    return {s["n"]: s for s in load_vignette(_TB).tutorial[side]}


@pytest.mark.verifies("FR-11420")
def test_tb_blue_script_in_order_meets_both_objectives_by_the_deadline():
    mgr = _mgr(_TB)
    steps = _tb_steps("blue")
    deadline = mgr.ctx.landing_deadline

    ob = _issue(mgr, "blue", **_RADAR_OBS)                               # step 2
    assert ob.status == "queued" and ob.earliest_window
    mgr.advance_to(ob.earliest_window[0] + 1)
    assert mgr.objectives()["blue"]["keep_custody"] is True
    dl = _issue(mgr, "blue", actor="ISR-EO-1", action="downlink", params={"via": "GS-TRN"})  # step 3
    assert dl.status == "queued" and dl.delivery_path == "ground_uplink" and dl.earliest_window
    assert dl.earliest_window[1] < deadline          # the pass really is inside the T+1 h deadline
    mgr.advance_to(dl.earliest_window[1] + 1)                            # step 4
    assert mgr.objectives()["blue"]["deliver_isr"] is True

    # The "confirm the objective" step must be reachable *before* the deadline, and must precede
    # any step whose effect lands after it (the maneuver pass is hours out).
    review_ns = [n for n, s in steps.items() if s["action"] == "review" and n > 1]
    mv_ns = [n for n, s in steps.items() if s["action"] == "maneuver"]
    assert review_ns and mv_ns and max(review_ns) < min(mv_ns), \
        "confirm-the-objective must come before the post-deadline maneuver step"
    mgr.advance_to(deadline)
    assert mgr.objectives()["blue"] == {"deliver_isr": True, "keep_custody": True}

    mv = _issue(mgr, "blue", actor="ISR-EO-1", action="maneuver",
                params={"dv": [0.0, 5.0, 0.0], "via": "GS-TRN"})         # the maneuver step
    assert mv.status == "queued" and mv.earliest_window
    assert mv.earliest_window[0] > deadline, "maneuver pass is after the deadline; the step must say so"
    assert "deadline" in steps[min(mv_ns)]["expect"].lower()
    dv0 = mgr.world.assets["ISR-EO-1"].resources.delta_v_ms
    mgr.advance_to(mv.earliest_window[1] + 1)
    assert mgr.world.assets["ISR-EO-1"].resources.delta_v_ms == pytest.approx(dv0 - 5.0)


@pytest.mark.verifies("FR-11420")
@pytest.mark.parametrize("seed", [0, 1, 2, 3])
def test_tb_red_script_jam_always_denies_cyber_is_chance_based_and_retryable(seed):
    steps = _tb_steps("red")
    assert any(w in steps[4]["expect"].lower() for w in ("chance", "probab", "may fail")), \
        "Red step 4 must not promise safe mode: cyber resolves stochastically"
    mgr = SessionManager(load_vignette(_TB), seed=seed)
    mgr.start()
    obs = _issue(mgr, "red", actor="RED-RDR", action="observe", target="ISR-EO-1", params={"intent": "track"})
    assert obs.status == "queued"
    jam = _issue(mgr, "red", actor="JAM-TRN", action="jam", target="ISR-EO-1",
                 params={"modulation": "barrage", "power_w": 200.0})
    assert jam.status == "queued"
    cyber = dict(actor="RED-CYBER", action="cyber", target="ISR-EO-1",
                 params={"vector": "ground_modem", "payload": "seize_c2"})
    cy = _issue(mgr, "red", **cyber)
    assert cy.status == "queued" and cy.earliest_window is None
    for _ in range(8):        # the documented remedy for a failed attempt: re-issue
        mgr.advance_to(mgr.world.now + 60_000_000)
        if mgr.objectives()["red"]["disable_isr"]:
            break
        assert _issue(mgr, "red", **cyber).status == "queued"
    assert mgr.objectives()["red"]["disable_isr"] is True
    assert mgr.world.assets["ISR-EO-1"].bus_state.mode == "safe_mode"
    mgr.advance_to(mgr.ctx.landing_deadline + 1)                          # step 5
    assert mgr.objectives()["red"]["deny_isr"] is True                    # independent of the seed
    eng = _issue(mgr, "red", actor="RED-ASAT", action="engage", target="ISR-EO-1", params={})
    assert eng.status == "rejected" and eng.reason == "roe_kinetic_not_authorized"


@pytest.mark.verifies("FR-11420")
def test_tb_roe_note_matches_parameter_defaults():
    vig = load_vignette(_TB)
    default = {p.id: p.default for p in vig.parameters}
    assert default["cyber_authorized"] is True and default["red_kinetic_authorized"] is False
    mgr = _mgr(_TB)
    cy = _issue(mgr, "red", actor="RED-CYBER", action="cyber", target="ISR-EO-1",
                params={"vector": "ground_modem", "payload": "seize_c2"})
    assert cy.status == "queued"                      # cyber really is on by default
    for cell in ("blue", "red"):
        note = vig.intro_brief[cell]["roe_note"].lower()
        assert "cyber off" not in note and "cyber disabled" not in note, note
        assert "on" in note.split("cyber", 1)[1][:60], f"{cell} roe_note must say cyber is ON by default: {note}"


@pytest.mark.verifies("FR-11420")
@pytest.mark.parametrize("vid", [v["id"] for v in list_vignettes()])
def test_every_roe_note_agrees_with_the_cyber_default(vid):
    """Library-wide: a brief's ROE note must not say cyber is off when the default is on."""
    import re
    vig = load_vignette(vid)
    default = {p.id: p.default for p in vig.parameters}.get("cyber_authorized")
    if default is not True:
        return
    for cell, brief in (vig.intro_brief or {}).items():
        note = (brief or {}).get("roe_note", "")
        assert not re.search(r"cyber\s+(is\s+)?(off|disabled|not authori[sz]ed)", note, re.I), \
            f"{vid}.{cell}: roe_note says cyber off but cyber_authorized defaults true: {note!r}"


# Known, reported-not-fixed mismatches (release-candidate-1 N2 sweep): the brief's stated deadline
# differs from ``landing_window_start_s``. Which one is wrong needs an author decision per vignette.
# strict xfail: fixing a vignette makes its entry XPASS-fail, forcing its removal here (list only shrinks).
_DEADLINE_NOTE_KNOWN_WRONG = {
    "geo-rpo-shadowing", "co-orbital-threat-escort", "coa-china-md", "coa-china-ml",
    "mt-isr-sar", "mt-sigint-geolocate", "mt-weather-collect",
}


@pytest.mark.verifies("FR-11420")
@pytest.mark.parametrize("vid", [
    pytest.param(v["id"], marks=pytest.mark.xfail(strict=True, reason="brief deadline_note disagrees with landing_window_start_s"))
    if v["id"] in _DEADLINE_NOTE_KNOWN_WRONG else v["id"]
    for v in list_vignettes()])
def test_every_brief_deadline_note_states_the_real_deadline(vid):
    """A brief's ``T+N min|h (S s)`` deadline must equal the vignette's ``landing_window_start_s``."""
    import re
    vig = load_vignette(vid)
    secs = {p.id: p.default for p in vig.parameters}.get("landing_window_start_s")
    if secs is None:
        return
    for cell, brief in (vig.intro_brief or {}).items():
        note = (brief or {}).get("deadline_note", "")
        m = re.search(r"T\+\s*(\d+(?:\.\d+)?)\s*(min|h)\b", note)
        if not m:
            continue
        stated = float(m.group(1)) * (60 if m.group(2) == "min" else 3600)
        assert stated == secs, f"{vid}.{cell}: deadline_note says {m.group(0)!r} but landing_window_start_s={secs}"
