"""IP-1066 (FS-106 v2.3, FR-4450) — White Cell edits or cancels a scheduled, not-yet-fired inject.

Cancel/edit are logged ``inject_admin`` actions; overrides fold from the event log strictly before
the instant they affect; a cancelled/superseded event is logged with ``skipped`` and applies
nothing; edits are rescheduled and re-armed after a rewind; everything replays byte-identically."""
from __future__ import annotations

import pytest

from spacesim.content.vignette import Vignette
from spacesim.session.manager import BUS_TICK_PERIOD_S, SessionManager

HOUR = 3600 * 1_000_000


def _vig() -> Vignette:
    return Vignette.model_validate({
        "id": "test-pending-injects", "title": "Pending inject queue",
        "start_epoch_utc": "2030-01-01T00:00:00Z",
        "blue_forces": [{"id": "SAT-BLUE", "kind": "satellite"}],
        "red_forces": [{"id": "SAT-RED", "kind": "satellite"}],
        "neutral_forces": [], "sensors": [],
        "injects": [
            {"id": "timed", "trigger": {"type": "time", "at_sim_s": 3600},
             "effects": [{"type": "message", "to": ["blue"], "text": "timed-original"}]},
            {"id": "reveal-2h", "trigger": {"type": "time", "at_sim_s": 7200},
             "effects": [{"type": "reveal_asset", "to": "blue", "target": "SAT-RED"}]},
            {"id": "cond", "trigger": {"type": "condition",
                                       "metric": {"kind": "custody", "side": "blue", "object": "SAT-RED", "min_conf": 0.5}},
             "effects": [{"type": "message", "to": ["blue"], "text": "cond-fired"}]},
        ],
    })


def _mgr() -> SessionManager:
    m = SessionManager(_vig(), seed=0)
    m.start()
    m.set_clock(False)
    return m


def _texts(m) -> list[str]:
    return [x["text"] for x in m.world.messages]


def _at(m, hours: float) -> int:
    return m.ctx.start_epoch + int(hours * HOUR)


def _handles(m) -> list[str]:
    return [p["handle"] for p in m.pending_injects()]


# 1 -------------------------------------------------------------------------------------------
@pytest.mark.verifies("FR-4450")
def test_pending_listing_shows_vignette_and_white_scheduled_injects():
    m = _mgr()
    m.fire_inject([{"type": "message", "to": ["blue"], "text": "white-later"}], at_sim_t=_at(m, 3))
    m.fire_inject([{"type": "message", "to": ["blue"], "text": "white-now"}])   # immediate: never pending
    pend = {p["handle"]: p for p in m.pending_injects()}
    assert set(pend) == {"timed", "reveal-2h", "cond", "white-1"}
    assert pend["timed"]["at"] == _at(m, 1) and pend["timed"]["trigger"] == "time"
    assert pend["timed"]["source"] == "vignette"
    assert pend["cond"]["at"] is None and pend["cond"]["trigger"] == "condition"
    assert pend["white-1"]["source"] == "white" and pend["white-1"]["at"] == _at(m, 3)
    assert pend["white-1"]["effects"][0]["text"] == "white-later"
    assert _handles(m) == ["timed", "reveal-2h", "white-1", "cond"]   # by fire time, conditions last


# 2-4 cancel ----------------------------------------------------------------------------------
@pytest.mark.verifies("FR-4450")
def test_cancelled_vignette_time_inject_never_fires_and_is_logged_skipped():
    m = _mgr()
    m.cancel_inject("timed")
    assert "timed" not in _handles(m)
    m.advance_to(_at(m, 1.5))
    assert "timed-original" not in _texts(m)
    (entry,) = [e for e in m.sim.eventlog.entries if e.kind == "inject" and e.payload.get("inject_id") == "timed"]
    assert entry.payload["skipped"] == "cancelled"


@pytest.mark.verifies("FR-4450")
def test_cancelled_condition_inject_never_fires():
    m = _mgr()
    m.cancel_inject("cond")
    m.advance_to(_at(m, 2.5))          # reveal at +2h makes the custody condition true
    assert "cond-fired" not in _texts(m)


@pytest.mark.verifies("FR-4450")
def test_condition_inject_still_fires_when_not_cancelled():
    m = _mgr()
    m.advance_to(_at(m, 2.5))
    assert _texts(m).count("cond-fired") == 1


@pytest.mark.verifies("FR-4450")
def test_cancelled_white_inject_never_fires():
    m = _mgr()
    m.fire_inject([{"type": "message", "to": ["blue"], "text": "white-later"}], at_sim_t=_at(m, 1))
    m.cancel_inject("white-1")
    m.advance_to(_at(m, 1.5))
    assert "white-later" not in _texts(m)


# 5-7 edit ------------------------------------------------------------------------------------
@pytest.mark.verifies("FR-4450")
def test_edited_effects_fire_once_with_the_edited_value():
    m = _mgr()
    m.edit_inject("timed", effects=[{"type": "message", "to": ["blue"], "text": "timed-edited"}])
    assert m.pending_injects()[0]["effects"][0]["text"] == "timed-edited"
    m.advance_to(_at(m, 1.5))
    assert _texts(m).count("timed-edited") == 1
    assert "timed-original" not in _texts(m)


@pytest.mark.verifies("FR-4450")
def test_edited_fire_time_moves_the_firing():
    m = _mgr()
    m.edit_inject("timed", at_sim_t=_at(m, 2.25))
    m.advance_to(_at(m, 1.5))
    assert "timed-original" not in _texts(m)
    m.advance_to(_at(m, 2.5))
    assert _texts(m).count("timed-original") == 1
    fired = [e for e in m.sim.eventlog.entries if e.kind == "inject" and e.payload.get("inject_id") == "timed"
             and "skipped" not in e.payload]
    assert [e.sim_time for e in fired] == [_at(m, 2.25)]


@pytest.mark.verifies("FR-4450")
def test_second_edit_supersedes_the_first():
    m = _mgr()
    m.edit_inject("timed", effects=[{"type": "message", "to": ["blue"], "text": "v1"}])
    m.edit_inject("timed", effects=[{"type": "message", "to": ["blue"], "text": "v2"}])
    m.advance_to(_at(m, 1.5))
    assert "v1" not in _texts(m) and _texts(m).count("v2") == 1


@pytest.mark.verifies("FR-4450")
def test_edited_white_inject_fires_edited():
    m = _mgr()
    m.fire_inject([{"type": "message", "to": ["blue"], "text": "w0"}], at_sim_t=_at(m, 1))
    m.edit_inject("white-1", effects=[{"type": "message", "to": ["blue"], "text": "w1"}])
    m.advance_to(_at(m, 1.5))
    assert "w0" not in _texts(m) and _texts(m).count("w1") == 1


@pytest.mark.verifies("FR-4450")
def test_edited_condition_inject_fires_with_edited_effects():
    m = _mgr()
    m.edit_inject("cond", effects=[{"type": "message", "to": ["blue"], "text": "cond-edited"}])
    m.advance_to(_at(m, 2.5))
    assert "cond-fired" not in _texts(m) and _texts(m).count("cond-edited") == 1


# 8 refusals ----------------------------------------------------------------------------------
def _snapshot(m):
    return m.world.model_dump(), len(m.sim.eventlog.entries), m.pending_injects()


@pytest.mark.verifies("FR-4450")
@pytest.mark.parametrize("call", [
    lambda m: m.cancel_inject("nope"),
    lambda m: m.edit_inject("nope", effects=[{"type": "message", "to": ["blue"], "text": "x"}]),
    lambda m: m.edit_inject("timed", at_sim_t=m.sim.clock.now),          # not in the future
    lambda m: m.edit_inject("cond", at_sim_t=_at(m, 5)),                 # condition: no fire time
    lambda m: m.edit_inject("timed"),                                     # empty edit
    lambda m: m.edit_inject("timed", effects=[{"type": "anomaly", "target": "SAT-BLUE", "subsystem": "bus"}]),
])
def test_refusals_change_nothing(call):
    m = _mgr()
    before = _snapshot(m)
    with pytest.raises(ValueError):
        call(m)
    assert _snapshot(m) == before


@pytest.mark.verifies("FR-4450")
def test_already_fired_and_already_cancelled_are_refused():
    m = _mgr()
    m.advance_to(_at(m, 1.5))
    with pytest.raises(ValueError, match="no pending inject"):
        m.cancel_inject("timed")
    m.cancel_inject("reveal-2h")
    with pytest.raises(ValueError, match="no pending inject"):
        m.cancel_inject("reveal-2h")


# 9-10 replay / rewind -------------------------------------------------------------------------
@pytest.mark.verifies("FR-4450", "FR-1120")
def test_session_with_cancel_and_edit_replays_byte_identically():
    m = _mgr()
    m.cancel_inject("reveal-2h")
    m.edit_inject("timed", effects=[{"type": "message", "to": ["blue"], "text": "e"}], at_sim_t=_at(m, 1.25))
    m.advance_to(_at(m, 3))
    assert m.sim.replay().model_dump() == m.world.model_dump()


@pytest.mark.verifies("FR-4450")
def test_rewind_to_before_the_edit_restores_the_original():
    m = _mgr()
    m.advance_to(_at(m, 0.25))
    t_before = m.sim.clock.now
    m.advance_to(_at(m, 0.5))
    m.edit_inject("timed", effects=[{"type": "message", "to": ["blue"], "text": "timed-edited"}])
    m.rewind_to(t_before)
    pend = {p["handle"]: p for p in m.pending_injects()}
    assert pend["timed"]["effects"][0]["text"] == "timed-original"
    m.advance_to(_at(m, 1.5))
    assert _texts(m).count("timed-original") == 1 and "timed-edited" not in _texts(m)


@pytest.mark.verifies("FR-4450")
def test_rewind_to_after_the_edit_keeps_it():
    m = _mgr()
    m.advance_to(_at(m, 0.25))
    m.edit_inject("timed", effects=[{"type": "message", "to": ["blue"], "text": "timed-edited"}],
                  at_sim_t=_at(m, 1.75))
    m.advance_to(_at(m, 0.75))
    m.rewind_to(_at(m, 0.5))
    m.advance_to(_at(m, 2))
    assert _texts(m).count("timed-edited") == 1 and "timed-original" not in _texts(m)
    fired = [e.sim_time for e in m.sim.eventlog.entries if e.kind == "inject"
             and e.payload.get("inject_id") == "timed" and "skipped" not in e.payload]
    assert fired == [_at(m, 1.75)]


# 11 HTTP --------------------------------------------------------------------------------------
@pytest.fixture()
def client_and_sid():
    from fastapi.testclient import TestClient
    from spacesim.session.inprocess import InProcessSession
    from spacesim.ui_web.server import create_app
    api = InProcessSession()
    sid = api.load_vignette("leo-isr-denial", seed=1)
    api.start(sid)
    api._sessions[sid].set_clock(False)
    c = TestClient(create_app(api))
    mgr = api._sessions[sid]
    t = mgr.sim.clock.now + HOUR
    r = c.post(f"/api/sessions/{sid}/inject?cell=white",
               json={"inject": {"effects": [{"type": "message", "to": ["blue"], "text": "h"}]}, "at_sim_t": t})
    assert r.status_code == 200
    return c, sid, mgr


@pytest.mark.verifies("FR-4450")
def test_http_pending_list_cancel_and_edit(client_and_sid):
    c, sid, mgr = client_and_sid
    r = c.get(f"/api/sessions/{sid}/injects/pending")
    assert r.status_code == 200 and "white-1" in [p["handle"] for p in r.json()]
    r = c.post(f"/api/sessions/{sid}/injects/white-1/edit?cell=white",
               json={"effects": [{"type": "message", "to": ["blue"], "text": "h2"}]})
    assert r.status_code == 200, r.text
    r = c.post(f"/api/sessions/{sid}/injects/white-1/cancel?cell=white")
    assert r.status_code == 200
    assert "white-1" not in [p["handle"] for p in c.get(f"/api/sessions/{sid}/injects/pending").json()]


@pytest.mark.verifies("FR-4450", "FR-4320")
@pytest.mark.parametrize("cell", ["blue", "red", "observer", None])
def test_http_non_white_is_403(client_and_sid, cell):
    c, sid, mgr = client_and_sid
    q = f"?cell={cell}" if cell else ""
    assert c.post(f"/api/sessions/{sid}/injects/white-1/cancel{q}").status_code == 403
    assert c.post(f"/api/sessions/{sid}/injects/white-1/edit{q}",
                  json={"effects": [{"type": "message", "to": ["blue"], "text": "x"}]}).status_code == 403
    assert "white-1" in [p["handle"] for p in mgr.pending_injects()]


@pytest.mark.verifies("FR-4450")
def test_http_refused_edit_is_400(client_and_sid):
    c, sid, mgr = client_and_sid
    r = c.post(f"/api/sessions/{sid}/injects/white-1/edit?cell=white", json={"effects": [{"type": "bogus"}]})
    assert r.status_code == 400 and "bogus" in r.json()["detail"]
    assert c.post(f"/api/sessions/{sid}/injects/nope/cancel?cell=white").status_code == 400


# 12 save / resume ------------------------------------------------------------------------------
@pytest.mark.verifies("FR-4450")
def test_save_resume_keeps_an_edited_pending_inject_and_the_white_counter(client_and_sid):
    c, sid, mgr = client_and_sid
    mgr.edit_inject("white-1", effects=[{"type": "message", "to": ["blue"], "text": "h-edited"}])
    resumed = SessionManager.from_state(mgr.save_state())
    resumed.set_clock(False)
    assert [p["effects"][0]["text"] for p in resumed.pending_injects() if p["handle"] == "white-1"] == ["h-edited"]
    resumed.fire_inject([{"type": "message", "to": ["blue"], "text": "next"}],
                        at_sim_t=resumed.sim.clock.now + 2 * HOUR)
    assert "white-2" in [p["handle"] for p in resumed.pending_injects()]
    resumed.advance_to(resumed.sim.clock.now + int(1.5 * HOUR))
    assert "h-edited" in [x["text"] for x in resumed.world.messages]
    assert BUS_TICK_PERIOD_S > 0
