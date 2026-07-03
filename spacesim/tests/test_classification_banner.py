"""IP-1120 — Classification Banner: one resolved value carried by SessionManager, read by the
UI-facing state, aar.export_csv, and save_state — never re-derived independently (FR-4510, NFR-3100).
"""

from __future__ import annotations

from spacesim.content.vignette import load_vignette
from spacesim.session import aar
from spacesim.session.inprocess import InProcessSession
from spacesim.session.manager import SessionManager


def test_classification_defaults_to_vignette_value():
    vig = load_vignette("leo-isr-denial")
    mgr = SessionManager(vig, seed=1)
    assert mgr.classification == vig.classification


def test_classification_override_flows_through_session():
    vig = load_vignette("leo-isr-denial")
    mgr = SessionManager(vig, seed=1, classification="UNCLASSIFIED//EXERCISE")
    assert mgr.classification == "UNCLASSIFIED//EXERCISE"
    assert mgr.classification != vig.classification


def test_aar_export_csv_embeds_active_classification():
    vig = load_vignette("leo-isr-denial")
    mgr = SessionManager(vig, seed=1, classification="UNCLASSIFIED//EXERCISE")
    rep = aar.report(mgr)
    assert rep.classification == "UNCLASSIFIED//EXERCISE"
    csv_text = aar.export_csv(rep)
    assert "UNCLASSIFIED//EXERCISE" in csv_text


def test_save_state_embeds_active_classification():
    vig = load_vignette("leo-isr-denial")
    mgr = SessionManager(vig, seed=1, classification="UNCLASSIFIED//EXERCISE")
    state = mgr.save_state()
    assert state["classification"] == "UNCLASSIFIED//EXERCISE"


def test_resume_from_state_preserves_classification_override():
    vig = load_vignette("leo-isr-denial")
    mgr = SessionManager(vig, seed=1, classification="UNCLASSIFIED//EXERCISE")
    state = mgr.save_state()
    resumed = SessionManager.from_state(state)
    assert resumed.classification == "UNCLASSIFIED//EXERCISE"


def test_resume_from_state_without_classification_key_falls_back_to_vignette_default():
    """Old save files (pre-IP-1120) lack the classification key — from_state must not error, and
    must fall back to the vignette's own default (Rollback Considerations)."""
    vig = load_vignette("leo-isr-denial")
    mgr = SessionManager(vig, seed=1)
    state = mgr.save_state()
    del state["classification"]
    resumed = SessionManager.from_state(state)
    assert resumed.classification == vig.classification


def test_set_parameter_preserves_classification_override():
    """Changing a tunable parameter before Start reconstructs the SessionManager (inprocess.py) —
    the classification override must survive that reconstruction, not silently revert to default
    (the two-sources-of-truth risk IP-1120's own Risks section names)."""
    api = InProcessSession()
    sid = api.load_vignette("leo-isr-denial", seed=1, classification="UNCLASSIFIED//EXERCISE")
    api.set_parameter(sid, "red_kinetic_authorized", True)
    assert api.classification(sid) == "UNCLASSIFIED//EXERCISE"


def test_list_sessions_surfaces_classification_for_joining_tabs():
    """joinSessionFromHash() (app.js) reads classification off list_sessions() — a second tab
    joining an existing session must see the same banner without re-deriving it."""
    api = InProcessSession()
    sid = api.load_vignette("leo-isr-denial", seed=1, classification="UNCLASSIFIED//EXERCISE")
    found = next(s for s in api.list_sessions() if s["sid"] == sid)
    assert found["classification"] == "UNCLASSIFIED//EXERCISE"
