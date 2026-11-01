"""IP-1084 (H-1; FR-6210, FR-4430, FR-4440, FR-4420) — controller-set anomaly / sensor-outage
notices are addressed by ownership: White gets the controller's true cause, the owning cell the fact
only, the opposing cell nothing. A recipient matrix over every message-emitting inject effect plus
the environmental-anomaly tick; the other effects keep their (pinned) recipients."""
from __future__ import annotations

import json

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from spacesim.content.vignette import Vignette  # noqa: E402
from spacesim.session.inprocess import InProcessSession  # noqa: E402
from spacesim.session.manager import INJECT_EFFECT_TYPES, SessionManager  # noqa: E402
from spacesim.ui_web.server import create_app  # noqa: E402

CAUSE = "ZQCAUSE-secret-9"
_ORBIT = {"a_m": 6378137.0 + 500e3, "e": 0.0, "i_deg": 51.6, "raan_deg": 0.0, "argp_deg": 0.0, "ta_deg": 0.0}
B_SAT, R_SAT, N_SAT = "BLUESAT-ZQ1", "REDSAT-ZQ2", "NEUTSAT-ZQ3"
B_SENS, R_SENS = "BLUESENS-ZQ4", "REDSENS-ZQ5"
GS = "GS-ZQ6"
SENTINELS = (B_SAT, R_SAT, N_SAT, B_SENS, R_SENS, CAUSE)
SEC = 1_000_000


def _sat(i, **kw):
    return {"id": i, "kind": "satellite", "orbit": dict(_ORBIT), "bus_state": {}, **kw}


def _vig(extra=None, injects=None) -> Vignette:
    raw = {
        "id": "test-inject-notice-fog", "title": "Notice fog", "start_epoch_utc": "2030-01-01T00:00:00Z",
        "blue_forces": [_sat(B_SAT), {"id": GS, "kind": "ground_station",
                                       "location": {"lat_deg": 10.0, "lon_deg": 10.0, "alt_m": 0.0}}],
        "red_forces": [_sat(R_SAT)],
        "neutral_forces": [_sat(N_SAT)],
        "sensors": [
            {"id": B_SENS, "owner": "blue", "kind": "ground_radar",
             "location": {"lat_deg": 30.0, "lon_deg": -86.0, "alt_m": 0.0}},
            {"id": R_SENS, "owner": "red", "kind": "ground_radar",
             "location": {"lat_deg": 40.0, "lon_deg": 60.0, "alt_m": 0.0}},
        ],
        "injects": injects or [],
    }
    raw.update(extra or {})
    return Vignette.model_validate(raw)


def _session(vig=None, seed=3, start=True):
    api = InProcessSession()
    mgr = SessionManager(vig or _vig(), seed=seed)
    api._sessions["sess-zq"] = mgr
    if start:
        mgr.start()
        mgr.set_clock(False)
    return api, "sess-zq", mgr, TestClient(create_app(api))


@pytest.fixture()
def env():
    return _session()


def _fire(c, sid, effects, at=None):
    body = {"inject": effects}
    if at is not None:
        body["at_sim_t"] = at
    r = c.post(f"/api/sessions/{sid}/inject?cell=white", json=body)
    assert r.status_code == 200, r.text
    return r


def _texts(c, sid, cell):
    r = c.get(f"/api/sessions/{sid}/view/{cell}")
    assert r.status_code == 200
    return [m["text"] for m in r.json()["messages"]]


def _all(c, sid):
    return {cell: _texts(c, sid, cell) for cell in ("white", "blue", "red")}


def _anom(target, **kw):
    return {"type": "anomaly", "target": target, "subsystem": kw.pop("subsystem", "bus"), **kw}


# -- recipient matrix (FR-6210, FR-4430) ----------------------------------------------------------

@pytest.mark.verifies("FR-6210", "FR-4430")
@pytest.mark.parametrize("target,owner", [(B_SAT, "blue"), (R_SAT, "red")])
@pytest.mark.parametrize("subsystem", ["bus", "telemetry"])
def test_anomaly_white_cause_owner_fact_opponent_nothing(env, target, owner, subsystem):
    _, sid, _, c = env
    _fire(c, sid, [_anom(target, subsystem=subsystem, cause=CAUSE)])
    t = _all(c, sid)
    other = "red" if owner == "blue" else "blue"
    assert t["white"] == [f"{target}: anomaly declared ({CAUSE})"]
    assert t[owner] == [f"{target}: anomaly declared"]
    assert t[other] == []


@pytest.mark.verifies("FR-6210", "FR-4430")
@pytest.mark.parametrize("target,owner", [(B_SAT, "blue"), (R_SAT, "red")])
def test_anomaly_restore_follows_same_addressing(env, target, owner):
    _, sid, _, c = env
    _fire(c, sid, [_anom(target, cause=CAUSE)])
    _fire(c, sid, [_anom(target, restore=True)])
    t = _all(c, sid)
    other = "red" if owner == "blue" else "blue"
    assert t["white"][-1] == f"{target}: anomaly cleared"
    assert t[owner] == [f"{target}: anomaly declared", f"{target}: anomaly cleared"]
    assert t[other] == []


@pytest.mark.verifies("FR-6210", "FR-4430")
def test_anomaly_on_neutral_asset_is_white_only(env):
    _, sid, _, c = env
    _fire(c, sid, [_anom(N_SAT, cause=CAUSE)])
    t = _all(c, sid)
    assert t["white"] == [f"{N_SAT}: anomaly declared ({CAUSE})"]
    assert t["blue"] == t["red"] == []


@pytest.mark.verifies("FR-6210", "FR-4430")
@pytest.mark.parametrize("target,owner", [(B_SENS, "blue"), (R_SENS, "red")])
def test_sensor_outage_declared_and_cleared(env, target, owner):
    _, sid, _, c = env
    _fire(c, sid, [{"type": "sensor_outage", "target": target, "cause": CAUSE}])
    _fire(c, sid, [{"type": "sensor_outage", "target": target, "restore": True}])
    t = _all(c, sid)
    other = "red" if owner == "blue" else "blue"
    assert t["white"] == [f"{target}: sensor outage declared ({CAUSE})", f"{target}: sensor outage cleared"]
    assert t[owner] == [f"{target}: sensor outage declared", f"{target}: sensor outage cleared"]
    assert t[other] == []


@pytest.mark.verifies("FR-6210", "FR-4430")
def test_cause_appears_in_no_player_message_or_red_view_field(env):
    _, sid, _, c = env
    _fire(c, sid, [_anom(B_SAT, cause=CAUSE), {"type": "sensor_outage", "target": B_SENS, "cause": CAUSE}])
    assert not any(CAUSE in x for x in _texts(c, sid, "blue") + _texts(c, sid, "red"))
    assert CAUSE not in json.dumps(c.get(f"/api/sessions/{sid}/view/red").json())
    assert B_SAT not in json.dumps(c.get(f"/api/sessions/{sid}/view/red").json()["messages"])


# -- pinned-unchanged recipients (FR-6210) ---------------------------------------------------------

def _pinned_cases():
    return [
        ("gs_outage", {"type": "gs_outage", "target": GS, "cause": "cut"}, "GS-ZQ6: outage declared (cut)",
         {"white", "blue", "red"}),
        ("gs_outage_restore", {"type": "gs_outage", "target": GS, "restore": True}, "GS-ZQ6: outage cleared",
         {"white", "blue", "red"}),
        ("space_weather", {"type": "space_weather", "severity": "severe"}, "Space weather: severity=severe",
         {"white", "blue", "red"}),
        ("space_weather_series", {"type": "space_weather", "index_series": [{"offset_s": 0, "kp": 5}]},
         "Space weather: index series updated", {"white", "blue", "red"}),
        ("debris_msg", {"type": "spawn_debris", "regime": "LEO", "altitude_km": 500, "n_fragments": 3,
                        "message": "ZQ debris cloud"}, "ZQ debris cloud", {"white", "blue", "red"}),
        ("conjunction", {"type": "conjunction_warning", "a": B_SAT, "b": R_SAT, "range_km": 2.0},
         "Conjunction warning", {"white", "blue"}),
        ("msg_blue", {"type": "message", "to": ["blue"], "text": "ZQ-m-blue"}, "ZQ-m-blue", {"blue"}),
        ("msg_red", {"type": "message", "to": ["red"], "text": "ZQ-m-red"}, "ZQ-m-red", {"red"}),
        ("msg_all", {"type": "message", "to": ["white", "blue", "red"], "text": "ZQ-m-all"}, "ZQ-m-all",
         {"white", "blue", "red"}),
        ("scripted", {"type": "scripted_manoeuvre", "target": B_SAT, "mode": "eci",
                      "params": {"dv_eci_ms": [0.1, 0.0, 0.0]}}, "scripted manoeuvre", {"white"}),
    ]


@pytest.mark.verifies("FR-6210")
@pytest.mark.parametrize("name,eff,needle,who", _pinned_cases(), ids=[c[0] for c in _pinned_cases()])
def test_pinned_unchanged_effect_recipients(env, name, eff, needle, who):
    _, sid, _, c = env
    _fire(c, sid, [eff])
    t = _all(c, sid)
    for cell in ("white", "blue", "red"):
        has = any(needle in x for x in t[cell])
        assert has == (cell in who), (name, cell, t[cell])


@pytest.mark.verifies("FR-6210")
def test_spawn_debris_without_message_tells_nobody(env):
    _, sid, _, c = env
    _fire(c, sid, [{"type": "spawn_debris", "regime": "LEO", "altitude_km": 500, "n_fragments": 3}])
    assert _all(c, sid) == {"white": [], "blue": [], "red": []}


@pytest.mark.verifies("FR-6210")
def test_custody_effects_emit_no_message(env):
    _, sid, mgr, c = env
    _fire(c, sid, [{"type": "reveal_asset", "to": "blue", "target": R_SAT}])
    _fire(c, sid, [{"type": "forced_custody_loss", "cell": "blue", "target": R_SAT, "mode": "drop"}])
    assert _all(c, sid) == {"white": [], "blue": [], "red": []}


@pytest.mark.verifies("FR-6210")
def test_skipped_effect_notice_is_white_only(env):
    _, sid, mgr, c = env
    mgr._apply_inject_effects(mgr.world, [{"type": "anomaly", "target": B_SAT, "subsystem": "power"}], mgr.sim.rng)
    t = _all(c, sid)
    assert len(t["white"]) == 1 and "inject effect skipped" in t["white"][0]
    assert t["blue"] == t["red"] == []


@pytest.mark.verifies("FR-6210")
def test_every_effect_type_is_in_the_matrix():
    covered = {"anomaly", "sensor_outage", "gs_outage", "space_weather", "spawn_debris",
               "conjunction_warning", "message", "scripted_manoeuvre", "reveal_asset", "forced_custody_loss"}
    uncovered = INJECT_EFFECT_TYPES - covered
    # political_consequence and patch_cyber_vuln append no message (see the test below).
    assert uncovered == {"political_consequence", "patch_cyber_vuln"}


@pytest.mark.verifies("FR-6210")
def test_non_message_effects_append_no_message(env):
    _, sid, mgr, c = env
    n = len(mgr.world.messages)
    mgr._apply_inject_effects(mgr.world, [{"type": "political_consequence", "note": "x"},
                                          {"type": "patch_cyber_vuln", "target": B_SAT, "vector": "v"}],
                              mgr.sim.rng)
    assert len(mgr.world.messages) == n


# -- entry points (FR-4420, FR-4440) ---------------------------------------------------------------

@pytest.mark.verifies("FR-6210", "FR-4430")
def test_future_dated_white_inject_obeys_addressing(env):
    _, sid, mgr, c = env
    _fire(c, sid, [_anom(B_SAT, cause=CAUSE)], at=mgr.world.now + 60 * SEC)
    assert _all(c, sid) == {"white": [], "blue": [], "red": []}   # nothing until it fires
    mgr.advance_to(mgr.world.now + 120 * SEC)
    t = _all(c, sid)
    assert t["white"] == [f"{B_SAT}: anomaly declared ({CAUSE})"]
    assert t["blue"] == [f"{B_SAT}: anomaly declared"]
    assert t["red"] == []


@pytest.mark.verifies("FR-6210", "FR-4420")
def test_condition_triggered_anomaly_never_reaches_the_opposing_cell():
    vig = _vig(injects=[
        {"id": "deb", "trigger": {"type": "time", "at_sim_s": 0},
         "effects": [{"type": "spawn_debris", "regime": "LEO", "altitude_km": 500, "n_fragments": 1}]},
        {"id": "cond", "trigger": {"type": "condition", "metric": {"kind": "debris_present"}},
         "effects": [_anom(B_SAT, cause=CAUSE)]},
    ])
    _, sid, mgr, c = _session(vig)
    from spacesim.session.manager import BUS_TICK_PERIOD_S
    mgr.advance_to(mgr.world.now + int(3 * BUS_TICK_PERIOD_S * SEC))
    assert mgr.world.assets[B_SAT].bus_state.safe_mode.active
    t = _all(c, sid)
    assert t["white"] == [f"{B_SAT}: anomaly declared ({CAUSE})"]
    assert t["blue"] == [f"{B_SAT}: anomaly declared"]
    assert t["red"] == []


_ENV = {"environmental_anomalies": {"base_rate_per_day": 5, "assets": [B_SAT], "subsystem": "telemetry",
                                    "cause": CAUSE},
        "space_weather_series": [{"at_sim_s": 0, "kp": 9}]}

# Firing times recorded on the parent commit (b022b1e) for seed 5 over 3 simulated hours: the RNG
# stream is untouched by IP-1084 (the recipients are a pure function of the target's owner).
_PARENT_ENV_FIRINGS = [(1893458100000000 + d * SEC, B_SAT) for d in (0, 1500, 3000, 5100, 5700, 6000)]


def _env_run():
    _, sid, mgr, c = _session(_vig(extra=_ENV), seed=5)
    mgr.advance_to(mgr.ctx.start_epoch + 3 * 3600 * SEC)
    return sid, mgr, c


def _firings(mgr):
    return [(e.sim_time, f["asset"]) for e in mgr.sim.eventlog.entries
            if e.kind == "env_anomaly_check" for f in e.payload.get("fired", [])]


@pytest.mark.verifies("FR-6210", "FR-4440")
def test_environmental_anomaly_tick_obeys_addressing_and_rng_is_untouched():
    sid, mgr, c = _env_run()
    fired = _firings(mgr)
    assert fired, "the fixture must actually fire"
    assert fired == _PARENT_ENV_FIRINGS
    t = _all(c, sid)
    assert t["red"] == []
    assert t["blue"] and all(x == f"{B_SAT}: anomaly declared" for x in t["blue"])
    assert t["white"] and all(CAUSE in x for x in t["white"])
    assert not any(B_SAT in x or CAUSE in x for x in t["red"])


# -- sweep over every other cell-scoped read (FR-6210) -----------------------------------------------

@pytest.mark.verifies("FR-6210")
def test_red_cell_scoped_reads_carry_no_blue_sentinel_or_cause(env):
    _, sid, mgr, c = env
    _fire(c, sid, [_anom(B_SAT, cause=CAUSE), _anom(B_SAT, subsystem="telemetry", cause=CAUSE),
                   {"type": "sensor_outage", "target": B_SENS, "cause": CAUSE}])
    for path in ("view", "scene", "alarms", "activity", "coaching", "conjunctions", "orders",
                 "next_contacts"):
        r = c.get(f"/api/sessions/{sid}/{path}/red")
        assert r.status_code == 200, path
        blob = json.dumps(r.json())
        for s in (B_SAT, B_SENS, CAUSE):
            assert s not in blob, (path, s)
    r = c.get(f"/api/sessions/{sid}/ssn/red/requests")
    assert r.status_code == 200 and CAUSE not in json.dumps(r.json())


@pytest.mark.verifies("FR-6210")
def test_blue_cell_scoped_reads_carry_no_red_sentinel_or_cause(env):
    _, sid, mgr, c = env
    _fire(c, sid, [_anom(R_SAT, cause=CAUSE), {"type": "sensor_outage", "target": R_SENS, "cause": CAUSE}])
    for path in ("view", "scene", "alarms", "activity", "coaching", "conjunctions", "orders",
                 "next_contacts"):
        blob = json.dumps(c.get(f"/api/sessions/{sid}/{path}/blue").json())
        for s in (R_SAT, R_SENS, CAUSE):
            assert s not in blob, (path, s)


@pytest.mark.verifies("FR-6210", "FR-4620")
def test_controller_view_panels(env):
    _, sid, mgr, c = env
    _fire(c, sid, [_anom(B_SAT, cause=CAUSE)])
    cv = c.get(f"/api/sessions/{sid}/controller_view?cell=white").json()
    assert [m["text"] for m in cv["truth"]["messages"]] == [f"{B_SAT}: anomaly declared ({CAUSE})",
                                                             f"{B_SAT}: anomaly declared"]
    assert [m["text"] for m in cv["blue"]["messages"]] == [f"{B_SAT}: anomaly declared"]
    assert cv["red"]["messages"] == []
    assert CAUSE not in json.dumps(cv["red"]) and CAUSE not in json.dumps(cv["blue"]["messages"])


@pytest.mark.verifies("FR-6210", "FR-7330")
def test_aar_playback_cell_viewpoint_is_filtered(env):
    api, sid, mgr, c = env
    _fire(c, sid, [_anom(B_SAT, cause=CAUSE)])
    mgr.advance_to(mgr.world.now + 10 * SEC)
    assert api.playback_start(sid, viewpoint="red", speed=1.0, seat="red").ok
    api.playback_advance(sid, 3600.0, seat="red")
    st = api.playback_state(sid, seat="red")
    assert st is not None and st["messages"] == []
    assert CAUSE not in json.dumps(st)
    assert api.playback_start(sid, viewpoint="blue", speed=1.0, seat="blue").ok
    api.playback_advance(sid, 3600.0, seat="blue")
    st = api.playback_state(sid, seat="blue")
    assert [m["text"] for m in st["messages"]] == [f"{B_SAT}: anomaly declared"]


# -- determinism and persistence (ADR-0002, FR-7220) --------------------------------------------------

@pytest.mark.verifies("FR-6210", "FR-4430")
def test_replay_equals_live_and_rewind_has_no_duplicates(env):
    _, sid, mgr, c = env
    t0 = mgr.world.now
    _fire(c, sid, [_anom(B_SAT, cause=CAUSE), {"type": "sensor_outage", "target": B_SENS, "cause": CAUSE}])
    live = _all(c, sid)
    assert mgr.sim.replay().model_dump_json() == mgr.world.model_dump_json()
    mgr.advance_to(t0 + 30 * SEC)
    assert _all(c, sid) == live


@pytest.mark.verifies("FR-6210", "FR-7220")
def test_save_load_round_trip_keeps_per_cell_messages(env):
    api, sid, mgr, c = env
    _fire(c, sid, [_anom(B_SAT, cause=CAUSE)])
    before = _all(c, sid)
    state = mgr.save_state()
    mgr2 = SessionManager.from_state(json.loads(json.dumps(state)))
    api._sessions["sess-zq2"] = mgr2
    assert _all(c, "sess-zq2") == before
    assert before["red"] == []


@pytest.mark.verifies("FR-6210", "FR-4440")
def test_env_tick_replay_equals_live():
    _, mgr, _ = _env_run()
    assert mgr.sim.replay().model_dump_json() == mgr.world.model_dump_json()


# -- at_sim_t booleans (IP-1082 family) ---------------------------------------------------------------

@pytest.mark.verifies("NFR-1600", "FR-4330")
@pytest.mark.parametrize("val", [True, False])
def test_inject_at_sim_t_boolean_is_a_400_and_changes_nothing(env, val):
    _, sid, mgr, c = env
    n = len(mgr.sim.eventlog.entries)
    r = c.post(f"/api/sessions/{sid}/inject?cell=white",
               json={"inject": [_anom(B_SAT, cause=CAUSE)], "at_sim_t": val})
    assert r.status_code == 400 and "at_sim_t" in r.json()["detail"]
    assert len(mgr.sim.eventlog.entries) == n and not mgr.world.assets[B_SAT].bus_state.safe_mode.active


@pytest.mark.verifies("NFR-1600", "FR-4330")
def test_inject_edit_at_sim_t_boolean_is_a_400(env):
    _, sid, mgr, c = env
    _fire(c, sid, [_anom(B_SAT)], at=mgr.world.now + 600 * SEC)
    handle = "white-1"     # the first future-dated White inject's stable handle (IP-1066)
    r = c.post(f"/api/sessions/{sid}/injects/{handle}/edit?cell=white", json={"at_sim_t": True})
    assert r.status_code == 400 and "at_sim_t" in r.json()["detail"]


@pytest.mark.verifies("NFR-1600", "FR-4330")
@pytest.mark.parametrize("bad", [True, False])
def test_manager_backstop_rejects_boolean_at_sim_t(env, bad):
    _, sid, mgr, c = env
    with pytest.raises(ValueError, match="at_sim_t"):
        mgr.fire_inject([_anom(B_SAT)], at_sim_t=bad)
    api = InProcessSession()
    api._sessions["s"] = mgr
    assert api.fire_inject("s", [_anom(B_SAT)], at_sim_t=bad).ok is False
