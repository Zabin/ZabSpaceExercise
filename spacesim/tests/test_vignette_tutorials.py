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

import json

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


# Owner decision 2026-10-25: the engine's ``landing_window_start_s`` (== the objectives' own ``by_s``) is the
# deadline; every brief states it.


@pytest.mark.verifies("FR-11420")
@pytest.mark.parametrize("vid", [v["id"] for v in list_vignettes()])
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


# -- training-basics: the numbers and names the script states are the engine's, not keywords -----

def _doc(name):
    from pathlib import Path
    return (Path(__file__).resolve().parents[2] / "docs" / "training" / name).read_text(encoding="utf-8")


@pytest.mark.verifies("FR-11420")
def test_tb_stated_times_and_numbers_are_derived_from_the_engine():
    from spacesim.engine.cyber import effective_success
    mgr = _mgr(_TB)
    t0, deadline = mgr.world.now, mgr.ctx.landing_deadline
    ob = _issue(mgr, "blue", **_RADAR_OBS)
    mgr.advance_to(ob.earliest_window[0] + 1)
    dl = _issue(mgr, "blue", actor="ISR-EO-1", action="downlink", params={"via": "GS-TRN"})
    end_min = round((dl.earliest_window[1] - t0) / 60e6)
    mgr.advance_to(dl.earliest_window[1] + 1)
    mv = _issue(mgr, "blue", actor="ISR-EO-1", action="maneuver", params={"dv": [0.0, 5.0, 0.0], "via": "GS-TRN"})
    mv_h = round((mv.earliest_window[0] - t0) / 3600e6)
    assert end_min < (deadline - t0) / 60e6
    blue = _tb_steps("blue")
    assert f"T+{end_min} min" in blue[4]["when"], blue[4]["when"]
    assert f"T+{mv_h} h" in blue[6]["when"] and f"T+{mv_h} h" in blue[6]["expect"]
    assert "do not advance" in blue[5]["when"].lower()
    for doc in ("04-guided-vignette.md", "11-vignette-playbooks.md", "16-learning-path.md"):
        assert f"T+{mv_h} h" in _doc(doc), f"{doc} must state the engine's maneuver pass (about T+{mv_h} h)"
    assert f"T+{end_min} min" in _doc("11-vignette-playbooks.md")
    pct = f"{round(effective_success('ground_modem', 'low') * 100)}%"
    assert pct in _tb_steps("red")[4]["expect"] and pct in _doc("04-guided-vignette.md")


@pytest.mark.verifies("FR-11420")
def test_tb_red_brief_names_and_manual_recipe_match_the_yaml():
    import json
    vig = load_vignette(_TB)
    red = vig.intro_brief["red"]
    assert "ISR-EO-1" in red["success_criteria"] and "BLUE-SAT" not in str(vig.intro_brief)
    assert "Jam GS-TRN" not in red["threat_picture"] and "ISR-EO-1" in red["threat_picture"]
    jam = _tb_steps("red")[3]["params"]
    assert json.dumps(jam, separators=(",", ":")).replace(".0,", ".0,") .replace(" ", "") in _doc("04-guided-vignette.md").replace(" ", "")
    assert [o["id"] for o in vig.objectives["red"]] == ["deny_isr", "disable_isr"]   # each declared once


# -- step-by-step scripts: a learner follows each cell's tutorial in order (BL-owner priority 2026-10-25) -----
#
# ``_Learner`` executes a step exactly as the Tutorial panel states it (review = no-op; advance = the stated
# ``dt_s``; ``ssn_request`` = the SSN request chip; anything else = an order) on a fixed seed, and a
# per-vignette ``checks`` table asserts what the step's ``when``/``expect`` text claims. ``_script`` fails if
# any step of the cell has no check, so a new or re-ordered step cannot go unverified.

class _Learner:
    def __init__(self, vid, cell, seed=1, share=None, **overrides):
        self.vid, self.cell = vid, cell
        if share is not None:                      # the other cell's learner on the same live session
            self.mgr = share.mgr
        else:
            self.mgr = SessionManager(load_vignette(vid), seed=seed, overrides=overrides or None)
            self.mgr.start()
        self.t0 = share.t0 if share is not None else self.mgr.world.now
        self.steps = {s["n"]: s for s in load_vignette(vid).tutorial[cell]}

    def minutes(self, t):
        return round((t - self.t0) / 60e6)

    @property
    def clock_min(self):
        return self.minutes(self.mgr.world.now)

    def do(self, n):
        st = self.steps[n]
        act, p = st["action"], dict(st.get("params") or {})
        if act == "review":
            return None
        if act == "advance":
            assert "dt_s" in p, f"{self.vid}.{self.cell} step {n}: advance step must state dt_s"
            self.mgr.advance_to(self.mgr.world.now + int(p["dt_s"] * 1_000_000))
            return None
        if act == "recovery":
            return self.mgr.begin_recovery(self.cell, st["actor"], p["via"])
        if act == "ssn_request":
            return self.mgr.submit_ssn_request(self.cell, p["intent"], st["target"], p["regime"], p["priority"])
        if "." in act:             # a bus/payload verb is picked by name in the Action menu; the console posts it as
            p, act = {**p, "verb": act}, "command"      # action "command" + params.verb (app.js)
        return _issue(self.mgr, self.cell, actor=st["actor"], action=act, target=st.get("target"), params=p)

    def obj(self):
        return self.mgr.objectives()[self.cell]

    def other(self):
        return self.mgr.objectives()["red" if self.cell == "blue" else "blue"]


def _script(vid, cell, checks, seed=1, **overrides):
    run = _Learner(vid, cell, seed=seed, **overrides)
    assert set(checks) == set(run.steps), \
        f"{vid}.{cell}: every tutorial step needs a machine check (missing {set(run.steps) - set(checks)}, " \
        f"stale {set(checks) - set(run.steps)})"
    for n in sorted(run.steps):
        res = run.do(n)
        checks[n](run, res, run.steps[n])
    return run


def _noop(run, res, st):
    pass


def _said(st, *needles, keys=("when", "expect")):
    text = " ".join(str(st.get(k, "")) for k in keys).lower()
    for w in needles:
        assert w.lower() in text, f"step {st['n']} must say {w!r}: {text[:160]}"


def _starts_at(run, res, st, minute):
    assert res.status == "queued" and res.earliest_window
    assert run.minutes(res.earliest_window[0]) == minute
    _said(st, f"T+{minute} min")


@pytest.mark.verifies("FR-11420")
def test_script_gnss_blue():
    def s3(run, res, st):
        assert run.clock_min == 10 and run.mgr.world.track_for("blue", "BLUE-GNSS") is not None
    def s4(run, res, st):
        assert run.clock_min >= 60 and run.obj() == {"maintain_service": True}
    _script("gnss-ew-campaign", "blue", {
        1: _noop, 2: lambda r, res, st: _starts_at(r, res, st, 4), 3: s3, 4: s4, 5: _noop})


@pytest.mark.verifies("FR-11420")
def test_script_gnss_blue_holds_service_even_while_red_jams():
    mgr = _mgr("gnss-ew-campaign")
    assert _issue(mgr, "red", actor="RED-JAM", action="jam", target="BLUE-GNSS",
                  params={"modulation": "barrage", "power_w": 200.0}).status == "queued"
    mgr.advance_to(mgr.world.now + 3601 * 1_000_000)
    assert mgr.objectives()["blue"]["maintain_service"] is True      # step 4's "even if Red is jamming"
    assert mgr.objectives()["red"]["deny_pnt"] is True


@pytest.mark.verifies("FR-11420")
def test_script_gnss_red():
    def s2(run, res, st):
        assert res.status == "queued" and run.minutes(res.earliest_window[0]) <= 0     # "already open"
        _said(st, "already open")
        run.mgr.advance_to(run.mgr.world.now + 60_000_000)
        assert run.obj() == {"deny_pnt": True}                                          # "after you advance a minute"
    def s3(run, res, st):
        assert run.obj() == {"deny_pnt": True} and run.other() == {"maintain_service": True}
    _script("gnss-ew-campaign", "red", {1: _noop, 2: s2, 3: s3})


@pytest.mark.verifies("FR-11420")
def test_script_co_orbital_blue():
    def s3(run, res, st):
        assert run.clock_min == 20 and run.mgr.world.track_for("blue", "RED-COORB") is not None
    def s4(run, res, st):
        assert res.status == "rejected" and res.reason == "no_command_station"
        _said(st, "no_command_station", "refused")
    def s5(run, res, st):
        assert run.obj() == {"hva_survives": True} and run.other() == {"neutralize_hva": False}
    _script("co-orbital-threat-escort", "blue", {
        1: _noop, 2: lambda r, res, st: _starts_at(r, res, st, 17), 3: s3, 4: s4, 5: s5})


@pytest.mark.verifies("FR-11420")
def test_script_co_orbital_red():
    def s2(run, res, st):
        assert res.status == "rejected" and res.reason == "no_command_station"
        _said(st, "no_command_station", "refused")
    def s3(run, res, st):
        assert run.obj() == {"neutralize_hva": False}
    _script("co-orbital-threat-escort", "red", {1: _noop, 2: s2, 3: s3})


@pytest.mark.verifies("FR-11420")
def test_script_da_asat_blue():
    def s2(run, res, st):
        assert res.status == "rejected" and res.reason == "no_command_station"
        assert run.mgr.world.assets["BLUE-SAT"].resources.delta_v_ms == 20.0
        _said(st, "no_command_station", "20 m/s")
    def s3(run, res, st):
        assert run.obj() == {"avoid_debris": True}
    _script("da-asat-crisis", "blue", {1: _noop, 2: s2, 3: s3})


@pytest.mark.verifies("FR-11420")
def test_script_da_asat_red_strikes_inside_the_hour():
    deadline_min = 60
    def s3(run, res, st):
        tr = run.mgr.world.track_for("red", "BLUE-SAT")
        assert run.clock_min == 20 and tr is not None and tr.is_weapons_quality(run.mgr.world.now)
    def s4(run, res, st):
        assert res.status == "queued" and res.earliest_window
        lo, hi = (run.minutes(t) for t in res.earliest_window)
        assert hi < deadline_min and run.clock_min <= hi
        _said(st, f"T+{lo} to T+{hi} min", "T+20")
    def s5(run, res, st):
        assert run.clock_min == 30 < deadline_min
        assert run.obj() == {"destroy_sat": True} and run.other() == {"avoid_debris": False}
        assert len(run.mgr.world.debris) > 0
    _script("da-asat-crisis", "red", {
        1: _noop, 2: lambda r, res, st: _starts_at(r, res, st, 17), 3: s3, 4: s4, 5: s5})


@pytest.mark.verifies("FR-11420")
def test_script_da_asat_engage_before_the_track_is_refused():
    run = _Learner("da-asat-crisis", "red")
    eng = _issue(run.mgr, "red", actor="RED-ASAT", action="engage", target="BLUE-SAT", params={"interceptor_class": "mrbm_kkv"})
    assert eng.status == "rejected" and eng.reason == "no_weapons_quality_track"
    _said(run.steps[2], "no_weapons_quality_track")


@pytest.mark.verifies("FR-11420")
def test_script_sda_blue_requests_keep_custody_unbroken_to_the_deadline():
    mgr_run = _Learner("sda-custody-hunt", "blue")
    mgr = mgr_run.mgr
    gaps = []
    orig_do = mgr_run.do
    def watch_advance(n):
        # step through the clock a minute at a time so a lapse inside a long advance is caught
        st = mgr_run.steps[n]
        if st["action"] == "advance":
            end = mgr.world.now + int(st["params"]["dt_s"] * 1_000_000)
            while mgr.world.now < end:
                mgr.advance_to(min(end, mgr.world.now + 60_000_000))
                if mgr_run.clock_min >= 15 and not mgr.objectives()["blue"]["maintain_custody"]:
                    gaps.append(mgr_run.clock_min)
            return None
        return orig_do(n)
    steps = mgr_run.steps
    # step 1 review; 2 request at T+0 (product ~T+15); 3 +10m; 4 request; 5 repeat at T+30/50/70; 6 deadline
    r = watch_advance
    r(1)
    ack = r(2); assert ack.ok and mgr_run.minutes(ack.product_at) == 15; _said(steps[2], "T+15 min")
    r(3); assert mgr_run.clock_min == 10 and mgr.objectives()["blue"]["maintain_custody"] is False
    ack = r(4); assert ack.ok and mgr_run.minutes(ack.product_at) == 25; _said(steps[4], "T+25 min")
    for at in (30, 50, 70):                      # step 5: "file the same request again at T+30, T+50 and T+70"
        _said(steps[5], f"T+{at}")
        while mgr_run.clock_min < at:
            mgr.advance_to(mgr.world.now + 60_000_000)
            if mgr_run.clock_min >= 15 and not mgr.objectives()["blue"]["maintain_custody"]:
                gaps.append(mgr_run.clock_min)
        assert mgr_run.clock_min == at
        ack = r(5); assert ack.ok, (at, ack.reason)
    r(6)
    assert mgr_run.clock_min >= 90
    assert gaps == [], f"custody lapsed at minutes {gaps}"
    assert mgr_run.obj() == {"maintain_custody": True} and mgr_run.other() == {"break_custody": False}
    _said(steps[6], "T+134 min")
    # the claim that the organic radar cannot help in time
    ob = _issue(mgr_run.mgr, "blue", actor="BLUE-RADAR-1", action="observe", target="RED-OBJ", params={"intent": "track"})
    assert mgr_run.minutes(ob.earliest_window[0]) == 134
    _said(steps[1], "T+134 min")


@pytest.mark.verifies("FR-11420")
def test_script_sda_blue_skipping_requests_loses_custody():
    run = _Learner("sda-custody-hunt", "blue")
    run.do(2)
    run.mgr.advance_to(run.t0 + 5401 * 1_000_000)      # one request, then straight to the deadline
    assert run.obj() == {"maintain_custody": False} and run.other() == {"break_custody": True}
    _said(run.steps[5], "below 0.5")


@pytest.mark.verifies("FR-11420")
def test_script_sda_red():
    def s3(run, res, st):
        assert res.status == "rejected" and res.reason == "no_command_station"
        _said(st, "no_command_station")
    def s4(run, res, st):
        assert run.clock_min >= 90 and run.obj() == {"break_custody": True}      # Blue did nothing
    _script("sda-custody-hunt", "red", {1: _noop, 2: _noop, 3: s3, 4: s4})


# -- the library-wide tutorial contract ------------------------------------------------------------------

def _is_verb(a):
    return "." in a


_STEP_ACTIONS = {"review", "advance", "observe", "downlink", "jam", "engage", "maneuver", "cyber", "command",
                 "recovery", "ssn_request"}
_WITH_TUTORIAL = NUMBERED + ["training-basics", "mt-isr-sar", "mt-sigint-geolocate", "mt-weather-collect",
                             "nv-isl-relay-debris", "learn-intermediate-recovery"]


@pytest.mark.verifies("FR-11420")
@pytest.mark.parametrize("vid", _WITH_TUTORIAL)
def test_every_tutorial_step_is_executable_or_explicitly_explanatory(vid):
    """No free-text 'action' sentences: each step is a real action the driver can run, or a labelled review."""
    vig = load_vignette(vid)
    for side in ("blue", "red"):
        steps = vig.tutorial[side]
        assert len(steps) >= 3, f"{vid}.{side}: tutorial too short"
        assert [s["n"] for s in steps] == list(range(1, len(steps) + 1)), f"{vid}.{side}: steps must be numbered 1..N"
        for st in steps:
            assert st["action"] in _STEP_ACTIONS or _is_verb(st["action"]), f"{vid}.{side} step {st['n']}: action {st['action']!r} is not executable"
            assert st.get("title") and st.get("when") and st.get("expect"), f"{vid}.{side} step {st['n']}: needs title/when/expect"
            if st["action"] not in ("review", "advance"):
                assert st.get("actor") or st["action"] == "ssn_request", f"{vid}.{side} step {st['n']}: needs an actor"
            if st["action"] == "advance":
                assert "dt_s" in st["params"] or st["params"].get("to") == "order_window", \
                    f"{vid}.{side} step {st['n']}: advance must state dt_s (or to: order_window)"


@pytest.mark.verifies("FR-11420")
@pytest.mark.parametrize("vid", ["mt-isr-sar", "mt-sigint-geolocate", "mt-weather-collect", "nv-isl-relay-debris"])
def test_mission_trial_tutorials_end_by_advancing_past_the_stated_deadline(vid):
    """Each script's last advance carries the learner to (just past) the deadline its brief states."""
    vig = load_vignette(vid)
    deadline = {p.id: p.default for p in vig.parameters}["landing_window_start_s"]
    for side in ("blue", "red"):
        total = sum(s["params"]["dt_s"] for s in vig.tutorial[side] if s["action"] == "advance")
        assert deadline <= total <= deadline + 60, f"{vid}.{side}: script ends at {total}s, deadline is {deadline}s"


# -- mt-isr-sar -------------------------------------------------------------------------------------------

@pytest.mark.verifies("FR-11420")
def test_script_sar_blue():
    def s2(run, res, st):
        _starts_at(run, res, st, 19); assert res.delivery_path == "ground_uplink"
    def s3(run, res, st):
        _starts_at(run, res, st, 19)
    def s4(run, res, st):
        assert run.clock_min == 20 and run.obj()["collect_sar"] is True
        assert run.mgr.world.assets["SAR-1"].payload_state.collecting is True
    def s5(run, res, st):
        assert run.obj() == {"collect_sar": True, "survive": True} and run.other() == {"deny_downlink": False}
    _script("mt-isr-sar", "blue", {1: _noop, 2: s2, 3: s3, 4: s4, 5: s5})


@pytest.mark.verifies("FR-11420")
def test_script_sar_red_and_the_jam_really_denies_the_product():
    def s2(run, res, st):
        # the dazzler's menu offers only jam (browser test below); the refusal the text cites is real
        eng = _issue(run.mgr, "red", actor="RED-DAZZLE", action="engage", target="SAR-1", params={})
        assert eng.status == "rejected" and eng.reason == "roe_kinetic_not_authorized"
        _said(st, "only jam", "roe_kinetic_not_authorized")
    def s5(run, res, st):
        assert run.obj() == {"deny_downlink": True}
    red = _script("mt-isr-sar", "red", {
        1: _noop, 2: s2, 3: lambda r, res, st: _starts_at(r, res, st, 17), 4: _noop, 5: s5})
    # Together on one session: Red's jam from step 3 beats Blue's steps 2-3 downlink.
    red = _Learner("mt-isr-sar", "red"); blue = _Learner("mt-isr-sar", "blue", share=red)
    red.do(3); blue.do(2); blue.do(3); red.do(4)
    assert blue.obj()["collect_sar"] is False                                    # red step 4's claim
    red.do(5)
    assert red.obj() == {"deny_downlink": True} and blue.obj() == {"collect_sar": False, "survive": True}


# -- mt-weather-collect -----------------------------------------------------------------------------------

@pytest.mark.verifies("FR-11420")
def test_script_weather_blue():
    def s2(run, res, st):
        _starts_at(run, res, st, 34); assert res.delivery_path == "ground_uplink"
    def s3(run, res, st):
        assert run.clock_min == 40 and run.obj()["deliver_wx"] is True
    def s4(run, res, st):
        assert run.obj() == {"deliver_wx": True, "wx_op": True}
    def s5(run, res, st):
        assert res.status == "queued" and run.minutes(res.earliest_window[0]) == 230
        assert res.earliest_window[0] > run.mgr.ctx.landing_deadline         # "far past the deadline"
        _said(st, "T+230 min")
    _script("mt-weather-collect", "blue", {1: _noop, 2: s2, 3: s3, 4: s4, 5: s5})


@pytest.mark.verifies("FR-11420")
def test_script_weather_red():
    holder = {}
    def s3(run, res, st):
        assert run.clock_min == 20 and run.obj() == {"track_blue": True}
    def s4(run, res, st):
        assert run.clock_min >= 60 and run.obj() == {"track_blue": False}
        nxt = _issue(run.mgr, "red", actor="RED-SDA-SENSOR", action="observe", target="WX-1", params={"intent": "track"})
        assert run.minutes(nxt.earliest_window[0]) == 66
        _said(st, "T+66 min")
    _script("mt-weather-collect", "red", {
        1: _noop, 2: lambda r, res, st: _starts_at(r, res, st, 16), 3: s3, 4: s4})


# -- nv-isl-relay-debris ----------------------------------------------------------------------------------

@pytest.mark.verifies("FR-11420")
def test_script_isl_relay_blue():
    run0 = _Learner("nv-isl-relay-debris", "blue")
    ap, t0 = run0.mgr.osys._ap(), run0.t0
    a_view = ap.windows("GS-NORTH", "ISR-A", "command_uplink", t0, t0 + 3 * 3600 * 10**6)
    assert a_view and run0.minutes(a_view[0].start) == 0 and 7 <= run0.minutes(a_view[0].end) <= 9   # "first 8 minutes"
    assert not ap.windows("GS-NORTH", "ISR-B", "command_uplink", t0, t0 + 3 * 3600 * 10**6)           # B never in view
    def s2(run, res, st):
        assert run.clock_min == 10
        assert any("Conjunction advisory" in m["text"] for m in run.mgr.world.messages if "blue" in m["to"])
        _said(st, "T+5 min", "T+17 min")
    def s3(run, res, st):
        assert res.status == "queued" and res.delivery_path == "isl_relay"
        _said(st, "isl_relay", "95 m/s")
    def s4(run, res, st):
        assert run.mgr.world.assets["ISR-B"].resources.delta_v_ms == pytest.approx(95.0) and run.clock_min < 17
    def s5(run, res, st):
        assert run.obj() == {"isr_b_survives": True, "isr_b_op": True}
    _script("nv-isl-relay-debris", "blue", {1: _noop, 2: s2, 3: s3, 4: s4, 5: s5})


@pytest.mark.verifies("FR-11420")
def test_script_isl_relay_red():
    def s2(run, res, st):
        assert res.status == "queued" and run.minutes(res.earliest_window[0]) == 0
    def s3(run, res, st):
        assert run.clock_min == 10 and run.obj() == {"track_blue": True}
    def s4(run, res, st):
        assert run.clock_min >= 30 and run.obj() == {"track_blue": False}
    _script("nv-isl-relay-debris", "red", {1: _noop, 2: s2, 3: s3, 4: s4})


# -- mt-sigint-geolocate (engine limitation documented, not papered over) ---------------------------------

@pytest.mark.verifies("FR-11420")
def test_script_sigint_blue_and_red_state_the_known_limitation():
    def s2(run, res, st):
        assert res.status == "rejected" and res.reason == "no_window"; _said(st, "no_window")
    def s3(run, res, st):
        assert res.status == "rejected" and res.reason == "no_such_sensor"; _said(st, "no_such_sensor")
    def s4(run, res, st):
        assert run.clock_min >= 60
        assert run.obj() == {"characterize_emitter": False, "preserve_constellation": True}
        assert run.other() == {"deny_characterization": True}
    blue = _script("mt-sigint-geolocate", "blue", {1: _noop, 2: s2, 3: s3, 4: s4})
    _said(blue.steps[1], "KNOWN LIMITATION")
    inj = {i.id: i for i in load_vignette("mt-sigint-geolocate").injects}["emitter_silent"]
    assert inj.trigger["type"] == "manual"                                       # red step 2's claim
    _script("mt-sigint-geolocate", "red", {1: _noop, 2: _noop, 3: lambda r, res, st: _noop(r, res, st) or
            (r.obj() == {"deny_characterization": True} or pytest.fail("deny_characterization not MET"))})


# -- learn-intermediate-recovery --------------------------------------------------------------------------

def _learn_pair(seed=1, **ov):
    red = _Learner("learn-intermediate-recovery", "red", seed=seed, **ov)
    return red, _Learner("learn-intermediate-recovery", "blue", share=red)


@pytest.mark.verifies("FR-11420")
def test_script_recovery_blue_and_red_together_recover_by_the_deadline():
    from spacesim.engine.cyber import effective_success
    red, blue = _learn_pair()
    bus = lambda: red.mgr.world.assets["ISR-EO-LEARN"].bus_state.mode
    blue.do(1); assert bus() == "nominal"
    _said(blue.steps[1], "T+41 min"); red.do(1)
    cy = red.do(2); assert cy.status == "queued" and cy.earliest_window is None                # not window-gated
    assert f"{round(effective_success('ground_modem', 'low') * 100)}%" in red.steps[2]["expect"]
    red.do(3); assert bus() == "safe_mode" and red.obj() == {"keep_safed": True}
    blue.do(2); assert bus() == "safe_mode" and blue.obj() == {"recover_to_nominal": False}
    patch = blue.do(3); _starts_at(blue, patch, blue.steps[3], 41)
    rec = blue.do(4); assert rec["ok"] and rec["passes_used"] == 1; _said(blue.steps[4], "1 pass")
    blue.do(5)
    assert blue.clock_min >= 45 and bus() == "nominal"
    assert blue.obj() == {"recover_to_nominal": True} and red.obj() == {"keep_safed": False}
    # red step 5: once patched, further exploits do not safe the bird (and step 4's persistence while open is below)
    for _ in range(6):
        red.do(2); red.mgr.advance_to(red.mgr.world.now + 60_000_000)
        assert bus() == "nominal"
    red.do(4); red.do(5)


@pytest.mark.verifies("FR-11420")
def test_script_recovery_without_the_patch_does_not_stick():
    red, blue = _learn_pair()
    red.do(2); red.do(3)
    blue.do(2); blue.do(4)                                    # skip step 3, as step 6 warns
    blue.do(5)
    assert red.mgr.world.assets["ISR-EO-LEARN"].bus_state.mode == "safe_mode"
    assert blue.obj() == {"recover_to_nominal": False} and red.obj() == {"keep_safed": True}
    st = red.mgr.recovery_status("blue", "ISR-EO-LEARN")
    assert "root cause persists" in st["blocked_reason"]
    _said(blue.steps[6], "root cause persists (cyber)")
    # red step 4: while the hole is open, re-firing is how the bird is held in safe mode.
    assert red.steps[4]["action"] == "review"


@pytest.mark.verifies("FR-11420")
@pytest.mark.parametrize("seed", [2, 3])
def test_script_recovery_failed_exploit_is_retried(seed):
    """Red step 3/2: the exploit is chance-based - some seeds need a re-fire, as the text says."""
    red, blue = _learn_pair(seed=seed)
    for _ in range(8):
        red.do(2); red.do(3)
        if red.obj() == {"keep_safed": True}:
            break
    assert red.obj() == {"keep_safed": True}
    _said(red.steps[3], "fire again")


# -- the console really offers what the steps say (headless Chromium; skipped where absent) ----------------
from spacesim.tests.test_browser_console_rules import console, server, pw_browser, browser_path, content  # noqa: E402,F401


def _menu(c, actor):
    c.page.select_option("#o-actor", actor)
    c.settle()
    return c.page.eval_on_selector_all("#o-action option", "o => o.map(x => x.value)")


@pytest.mark.browser
@pytest.mark.verifies("FR-11420")
def test_console_offers_the_verbs_and_menus_the_tutorial_steps_name(console):
    c = console("mt-isr-sar")
    c.seat("blue")
    assert "isr.collect_now" in _menu(c, "SAR-1")
    c.page.select_option("#o-action", "isr.collect_now")
    c.settle()
    assert c.page.input_value("#o-params").replace(" ", "") == '{"via":"GS-POLAR"}'      # step 2's Params
    c.page.wait_for_function("document.getElementById('o-preview').textContent.includes('will queue')")
    c.seat("red")
    assert _menu(c, "RED-DAZZLE") == ["jam"]                                             # Red step 2
    c = console("learn-intermediate-recovery")
    c.seat("blue")
    assert "def.patch_cyber" in _menu(c, "ISR-EO-LEARN")
    c.page.select_option("#o-action", "def.patch_cyber")
    c.settle()
    assert json.loads(c.page.input_value("#o-params")) == {"via": "GS-LEARN", "vector": "ground_modem"}
