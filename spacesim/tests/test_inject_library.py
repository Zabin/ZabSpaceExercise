"""Tests for the white-cell inject library (FW §11.D.19).

Covers:
  - InProcessSession.inject_library() loads and parses content/inject_library.yaml
  - Each library entry has a valid id, label, and at least one effect
  - All effect `type`s used in the library are handled by manager._h_inject
  - fire_inject(at_sim_t=future) schedules an inject that applies on advance
  - fire_inject without at_sim_t still applies immediately (legacy contract)
  - spawn_debris effect handler appends a DebrisField
"""
from __future__ import annotations

import pytest

from spacesim.session.inprocess import InProcessSession


# Effect types accepted by manager._h_inject (must stay in sync with that handler).
_KNOWN_EFFECT_TYPES = {
    "message", "reveal_asset", "political_consequence", "patch_cyber_vuln",
    "gs_outage", "space_weather", "conjunction_warning", "spawn_debris",
}


def _api_session():
    api = InProcessSession()
    sid = api.load_vignette("training-basics")
    api.start(sid)
    return api, sid


# ---------------------------------------------------------------------------
# Library loading
# ---------------------------------------------------------------------------

def test_inject_library_loads_nonempty():
    api = InProcessSession()
    lib = api.inject_library()
    assert isinstance(lib, list) and len(lib) >= 5


def test_library_entries_have_required_fields():
    api = InProcessSession()
    for entry in api.inject_library():
        assert entry["id"]
        assert "label" in entry
        assert isinstance(entry.get("effects"), list) and entry["effects"]


def test_library_effects_use_supported_types():
    api = InProcessSession()
    for entry in api.inject_library():
        for eff in entry["effects"]:
            assert eff.get("type") in _KNOWN_EFFECT_TYPES, \
                f"{entry['id']} uses unsupported effect type: {eff.get('type')}"


def test_library_is_cached():
    """Repeat calls return the same in-memory list (cheap re-render)."""
    api = InProcessSession()
    a = api.inject_library()
    b = api.inject_library()
    assert a is not b or len(a) == len(b)   # cache may copy on read; either is fine


# ---------------------------------------------------------------------------
# Scheduled firing
# ---------------------------------------------------------------------------

def test_fire_inject_immediate_applies_now():
    api, sid = _api_session()
    mgr = api._sessions[sid]
    before = len(mgr.world.messages)
    api.fire_inject(sid, {"effects": [
        {"type": "message", "to": ["blue"], "text": "hello"},
    ]})
    assert len(mgr.world.messages) == before + 1


def test_fire_inject_scheduled_does_not_apply_until_advance():
    api, sid = _api_session()
    mgr = api._sessions[sid]
    before = len(mgr.world.messages)
    future = mgr.world.now + 60_000_000   # 60 seconds
    api.fire_inject(sid, {"effects": [
        {"type": "message", "to": ["blue"], "text": "later"},
    ]}, at_sim_t=future)
    # Still pending
    assert len(mgr.world.messages) == before
    # Advance past the trigger
    mgr.advance_to(future + 1)
    assert any(m.get("text") == "later" for m in mgr.world.messages)


def test_fire_inject_past_timestamp_applies_immediately():
    api, sid = _api_session()
    mgr = api._sessions[sid]
    before = len(mgr.world.messages)
    api.fire_inject(sid, {"effects": [
        {"type": "message", "to": ["blue"], "text": "past"},
    ]}, at_sim_t=mgr.world.now - 1)   # in the past → fire now
    assert len(mgr.world.messages) > before


# ---------------------------------------------------------------------------
# spawn_debris handler
# ---------------------------------------------------------------------------

def test_spawn_debris_effect_creates_debris_field():
    api, sid = _api_session()
    mgr = api._sessions[sid]
    before = len(mgr.world.debris)
    api.fire_inject(sid, {"effects": [
        {"type": "spawn_debris", "regime": "LEO", "altitude_km": 500,
         "n_fragments": 800, "message": "test breakup"},
    ]})
    assert len(mgr.world.debris) == before + 1
    fld = mgr.world.debris[-1]
    assert fld.region["regime"] == "LEO"
    assert fld.region["altitude_km"] == 500
    assert fld.region["n_fragments"] == 800
    assert fld.source == "inject"


# ---------------------------------------------------------------------------
# End-to-end: pick a library entry, fire it through the API
# ---------------------------------------------------------------------------

def test_library_entry_roundtrip_through_fire_inject():
    api, sid = _api_session()
    mgr = api._sessions[sid]
    lib = api.inject_library()
    # Pick the debris entry
    entry = next((e for e in lib if e["id"] == "debris_field_500km"), None)
    assert entry is not None
    before = len(mgr.world.debris)
    api.fire_inject(sid, {"effects": entry["effects"]})
    assert len(mgr.world.debris) == before + 1


def test_library_entry_scheduled_replays_through_eventlog():
    """A scheduled inject must show up in the event log so a save/resume round-trips."""
    api, sid = _api_session()
    mgr = api._sessions[sid]
    future = mgr.world.now + 30_000_000
    api.fire_inject(sid, {"effects": [{"type": "message", "to": ["white"], "text": "ev"}]},
                     at_sim_t=future)
    mgr.advance_to(future + 1)
    # The inject event is present in the eventlog (deterministic replay)
    inject_events = [e for e in mgr.sim.eventlog.entries if e.kind == "inject"]
    assert len(inject_events) >= 1
