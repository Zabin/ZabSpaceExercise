"""IP-1230 (FS-123 v1.1, ADR-0039; FR-1230/FR-4440) — a declared F10.7/Kp index series drives
opt-in LEO drag and an opt-in environmental-anomaly rate, deterministically; non-physical index
values are refused at load and at the White inject boundary; vignettes that opt into nothing are
byte-identical to before."""
from __future__ import annotations

import math

import pytest

from spacesim.content.vignette import Vignette, VignetteValidationError, validate_vignette
from spacesim.engine import perturbations as pt
from spacesim.engine.orbit import R_EARTH_EQ
from spacesim.session.manager import BUS_TICK_PERIOD_S, SessionManager

HOUR = 3600 * 1_000_000
_LEO_A = R_EARTH_EQ + 400e3
_LEO_ORBIT = {"a_m": _LEO_A, "e": 0.0, "i_deg": 51.6, "raan_deg": 0.0, "argp_deg": 0.0, "ta_deg": 0.0}
_GEO_ORBIT = {"a_m": 42_164e3, "e": 0.0, "i_deg": 0.0, "raan_deg": 0.0, "argp_deg": 0.0, "ta_deg": 0.0}
_TLE1 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
_TLE2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"


def _vig(*, series=None, assets=None, anomalies=None, injects=None, extra=None) -> Vignette:
    raw = {
        "id": "test-space-weather-index", "title": "Space-weather index test",
        "start_epoch_utc": "2030-01-01T00:00:00Z",
        "blue_forces": assets if assets is not None else [
            {"id": "LEO-1", "kind": "satellite", "orbit": dict(_LEO_ORBIT),
             "ballistic_coeff_m2_kg": 0.02, "bus_state": {}},
        ],
        "red_forces": [], "neutral_forces": [], "sensors": [],
        "injects": injects or [],
    }
    if series is not None:
        raw["space_weather_series"] = series
    if anomalies is not None:
        raw["environmental_anomalies"] = anomalies
    raw.update(extra or {})
    return Vignette.model_validate(raw)


def _run(vig: Vignette, hours: float, seed: int = 7) -> SessionManager:
    mgr = SessionManager(vig, seed=seed)
    mgr.start()
    mgr.set_clock(False)
    mgr.advance_to(mgr.ctx.start_epoch + int(hours * HOUR))   # absolute target: no wall-clock drift
    return mgr


# --- 1. mapping anchors (AC 2) ---------------------------------------------------------------

@pytest.mark.verifies("FR-1230")
@pytest.mark.parametrize("f107,want", [(50, 0.3), (150, 1.0), (300, 3.0), (40, 0.3), (400, 3.0), (100, 0.65)])
def test_f_solar_anchors(f107, want):
    assert pt.f_solar(f107) == pytest.approx(want)


@pytest.mark.verifies("FR-1230")
@pytest.mark.parametrize("kp,want", [(0, 1.0), (2, 1.0), (4, 1.0), (5, 2.0), (7, 6.0), (9, 10.0)])
def test_f_geo_anchors(kp, want):
    assert pt.f_geo(kp) == pytest.approx(want)


@pytest.mark.verifies("FR-4440")
def test_drag_and_anomaly_multipliers():
    t0 = 1_000
    assert pt.drag_multiplier([{"t": 0, "f107": 150, "kp": 7}], t0) == pytest.approx(6.0)
    assert pt.drag_multiplier([{"t": 0, "f107": 300, "kp": 9}], t0) == pytest.approx(30.0)
    # the anomaly multiplier ignores F10.7
    assert pt.anomaly_rate_multiplier([{"t": 0, "f107": 300, "kp": 2}], t0) == pytest.approx(1.0)
    assert pt.anomaly_rate_multiplier([{"t": 0, "f107": 50, "kp": 7}], t0) == pytest.approx(6.0)


# --- 2. step-held lookup -----------------------------------------------------------------------

@pytest.mark.verifies("FR-1230")
def test_index_in_effect_is_step_held_per_index():
    series = [{"t": 10, "f107": 200, "kp": 3}, {"t": 20, "kp": 6}]
    assert pt.index_in_effect(series, 5, "kp") is None
    assert pt.drag_multiplier(series, 5) == 1.0
    assert pt.index_in_effect(series, 15, "kp") == 3
    assert pt.index_in_effect(series, 25, "kp") == 6
    assert pt.index_in_effect(series, 25, "f107") == 200   # only kp changed at t=20


# --- 3. validator ------------------------------------------------------------------------------

@pytest.mark.verifies("FR-1230")
def test_index_series_problems_accepts_valid_series():
    assert pt.index_series_problems([{"at_sim_s": 0, "f107": 150, "kp": 2}, {"at_sim_s": 60, "kp": 9}],
                                    "at_sim_s") == []


@pytest.mark.verifies("FR-1230")
@pytest.mark.parametrize("entry", [
    {"at_sim_s": 0, "kp": -1}, {"at_sim_s": 0, "kp": 9.5}, {"at_sim_s": 0, "kp": float("nan")},
    {"at_sim_s": 0, "f107": 0}, {"at_sim_s": 0, "f107": -5}, {"at_sim_s": 0, "kp": True},
    {"at_sim_s": 0}, {"kp": 3}, {"at_sim_s": -1, "kp": 3}, "not-a-dict",
])
def test_index_series_problems_refuses_bad_entries(entry):
    assert pt.index_series_problems([entry], "at_sim_s")


# --- 4/5. drag responds and replays (AC 1) -------------------------------------------------------

def _a(mgr, asset="LEO-1") -> float:
    return mgr.world.assets[asset].orbit.a_m


@pytest.mark.verifies("FR-1230")
def test_active_series_decays_faster_than_quiescent_and_both_decay():
    quiet = _run(_vig(series=[{"at_sim_s": 0, "f107": 70, "kp": 1}]), 6)
    active = _run(_vig(series=[{"at_sim_s": 0, "f107": 250, "kp": 7}]), 6)
    assert _a(quiet) < _LEO_A
    assert _a(active) < _a(quiet)


@pytest.mark.verifies("FR-1230")
def test_drag_run_replays_byte_identically():
    mgr = _run(_vig(series=[{"at_sim_s": 0, "f107": 250, "kp": 7}]), 3)
    assert mgr.sim.replay().model_dump() == mgr.world.model_dump()


# --- 6. qualifying assets only (AC 6) -----------------------------------------------------------

def _mixed_fleet():
    return [
        {"id": "TLE-1", "kind": "satellite", "orbit": {"source": "tle", "tle_line1": _TLE1, "tle_line2": _TLE2},
         "ballistic_coeff_m2_kg": 0.02},
        {"id": "GEO-1", "kind": "satellite", "orbit": dict(_GEO_ORBIT), "ballistic_coeff_m2_kg": 0.02},
        {"id": "LEO-NOBC", "kind": "satellite", "orbit": dict(_LEO_ORBIT)},
    ]


@pytest.mark.verifies("FR-1230")
def test_only_qualifying_assets_are_drag_coupled():
    with_series = _run(_vig(assets=_mixed_fleet(), series=[{"at_sim_s": 0, "f107": 300, "kp": 9}]), 2)
    control = _run(_vig(assets=_mixed_fleet()), 2)
    for aid in ("TLE-1", "GEO-1", "LEO-NOBC"):
        assert with_series.world.assets[aid].orbit.model_dump() == control.world.assets[aid].orbit.model_dump()


# --- 7/8. anomaly rate responds and replays (AC 3) ------------------------------------------------

_ANOM_ASSETS = [{"id": f"SAT-{k}", "kind": "satellite", "orbit": dict(_LEO_ORBIT), "bus_state": {}} for k in range(3)]
_ANOM_BLOCK = {"base_rate_per_day": 20, "assets": ["SAT-0", "SAT-1", "SAT-2"], "subsystem": "telemetry"}


def _firings(mgr) -> list[tuple[int, str]]:
    return [(e.sim_time, f["asset"]) for e in mgr.sim.eventlog.entries
            if e.kind == "env_anomaly_check" for f in e.payload.get("fired", [])]


@pytest.mark.verifies("FR-4440")
def test_high_kp_fires_more_environmental_anomalies():
    quiet = _run(_vig(assets=_ANOM_ASSETS, anomalies=dict(_ANOM_BLOCK), series=[{"at_sim_s": 0, "kp": 1}]), 24, seed=3)
    storm = _run(_vig(assets=_ANOM_ASSETS, anomalies=dict(_ANOM_BLOCK), series=[{"at_sim_s": 0, "kp": 8}]), 24, seed=3)
    assert len(_firings(quiet)) > 0
    assert len(_firings(storm)) > len(_firings(quiet))
    # a firing applies the existing anomaly effect (telemetry -> comms red + a message)
    assert any("anomaly declared (space_weather)" in m["text"] for m in storm.world.messages)


@pytest.mark.verifies("FR-4440")
def test_environmental_anomaly_firings_replay_identically():
    mgr = _run(_vig(assets=_ANOM_ASSETS, anomalies=dict(_ANOM_BLOCK), series=[{"at_sim_s": 0, "kp": 8}]), 6, seed=5)
    assert _firings(mgr)
    assert mgr.sim.replay().model_dump() == mgr.world.model_dump()


@pytest.mark.verifies("FR-4440")
def test_bus_anomaly_skips_an_already_safed_asset():
    block = {"base_rate_per_day": 500, "assets": ["SAT-0"], "subsystem": "bus"}
    mgr = _run(_vig(assets=_ANOM_ASSETS[:1], anomalies=block, series=[{"at_sim_s": 0, "kp": 9}]), 2, seed=1)
    fired = _firings(mgr)
    assert len(fired) == 1     # first firing safes it; later draws are not re-entries
    assert mgr.world.assets["SAT-0"].bus_state.safe_mode.active


# --- 9. refusal at load (AC 5) ------------------------------------------------------------------

@pytest.mark.verifies("FR-1230")
@pytest.mark.parametrize("kwargs,where", [
    ({"series": [{"at_sim_s": 0, "kp": 12}]}, "space_weather_series"),
    ({"series": [{"at_sim_s": 0, "f107": -5}]}, "space_weather_series"),
    ({"assets": [{"id": "LEO-1", "kind": "satellite", "orbit": dict(_LEO_ORBIT), "ballistic_coeff_m2_kg": 0}]},
     "ballistic_coeff_m2_kg"),
    ({"anomalies": {"base_rate_per_day": 1, "assets": ["GHOST"]}}, "environmental_anomalies"),
    ({"anomalies": {"base_rate_per_day": -1, "assets": ["LEO-1"]}}, "environmental_anomalies"),
    ({"extra": {"initial_space_weather": {"severity": "none", "index_series": [{"t": 0, "kp": 10}]}}},
     "initial_space_weather"),
])
def test_load_refuses_non_physical_values(kwargs, where):
    problems = validate_vignette(_vig(**kwargs))
    assert problems and any(where in p["where"] for p in problems), problems


@pytest.mark.verifies("FR-1230")
def test_load_vignette_raises_validation_error(tmp_path, monkeypatch):
    import yaml
    from spacesim.content import vignette as vmod
    raw = _vig(series=[{"at_sim_s": 0, "kp": 12}]).model_dump()
    raw["id"] = "bad-sw"
    (tmp_path / "bad-sw.yaml").write_text(yaml.safe_dump({"vignette": raw}))
    monkeypatch.setattr(vmod, "VIGNETTE_DIR", tmp_path)
    with pytest.raises(VignetteValidationError) as err:
        vmod.load_vignette("bad-sw")
    assert any(p["where"] == "space_weather_series" and "kp" in p["reason"] for p in err.value.problems), err.value.problems


# --- 10. refusal at the inject boundary (AC 5) ---------------------------------------------------

@pytest.mark.verifies("FR-1230")
def test_fire_inject_refuses_out_of_range_series_and_changes_nothing():
    mgr = SessionManager(_vig(), seed=0)
    mgr.start()
    mgr.set_clock(False)
    before = mgr.world.model_dump()
    n_events = len(mgr.sim.eventlog.entries)
    with pytest.raises(ValueError, match="kp"):
        mgr.fire_inject([{"type": "space_weather", "index_series": [{"offset_s": 0, "kp": 12}]}])
    assert mgr.world.model_dump() == before
    assert len(mgr.sim.eventlog.entries) == n_events


@pytest.mark.verifies("FR-1230")
def test_http_inject_with_out_of_range_series_is_400():
    from fastapi.testclient import TestClient
    from spacesim.session.inprocess import InProcessSession
    from spacesim.ui_web.server import create_app
    api = InProcessSession()
    sid = api.load_vignette("leo-isr-denial", seed=1)
    api.start(sid)
    c = TestClient(create_app(api))
    r = c.post(f"/api/sessions/{sid}/inject?cell=white",
               json={"inject": [{"type": "space_weather", "index_series": [{"offset_s": 0, "f107": -1}]}]})
    assert r.status_code == 400
    assert "f107" in r.json()["detail"]


@pytest.mark.verifies("FR-1230")
def test_series_inject_applies_from_fire_time_and_drives_drag():
    mgr = SessionManager(_vig(), seed=0)
    mgr.start()
    mgr.set_clock(False)
    mgr.advance_to(mgr.sim.clock.now + HOUR)
    a_before = _a(mgr)            # no series yet: no decay
    assert a_before == pytest.approx(_LEO_A)
    mgr.fire_inject([{"type": "space_weather", "index_series": [{"offset_s": 0, "f107": 250, "kp": 7}]}])
    series = mgr.world.space_weather["index_series"]
    assert series == [{"t": mgr.sim.clock.now, "f107": 250.0, "kp": 7.0}]
    mgr.advance_to(mgr.sim.clock.now + HOUR)
    assert _a(mgr) < a_before


# --- 11. opt-out byte-identity (AC 4) ------------------------------------------------------------

@pytest.mark.verifies("FR-1230")
def test_shipped_vignette_unaffected_by_empty_series_and_no_bcs():
    from spacesim.content.vignette import load_vignette
    base = load_vignette("leo-isr-denial")
    opted = base.model_copy(update={"space_weather_series": []})
    a = SessionManager(base, seed=11); a.start(); a.set_clock(False)
    b = SessionManager(opted, seed=11); b.start(); b.set_clock(False)
    for m in (a, b):
        m.advance_to(m.ctx.start_epoch + 2 * HOUR)
    assert "index_series" not in a.world.space_weather
    assert a.world.model_dump() == b.world.model_dump()
    assert [(e.kind, e.sim_time) for e in a.sim.eventlog.entries] == \
           [(e.kind, e.sim_time) for e in b.sim.eventlog.entries]
    assert not any(e.kind == "env_anomaly_check" for e in a.sim.eventlog.entries)


@pytest.mark.verifies("FR-4440")
def test_series_without_bcs_or_anomaly_block_changes_no_orbit():
    assets = [{"id": "LEO-NOBC", "kind": "satellite", "orbit": dict(_LEO_ORBIT)}]
    with_series = _run(_vig(assets=assets, series=[{"at_sim_s": 0, "f107": 300, "kp": 9}]), 2)
    control = _run(_vig(assets=assets), 2)
    assert with_series.world.assets["LEO-NOBC"].model_dump() == control.world.assets["LEO-NOBC"].model_dump()
    assert [e.kind for e in with_series.sim.eventlog.entries] == [e.kind for e in control.sim.eventlog.entries]


# --- 12. severity / series coexistence (Design Decision 3) ---------------------------------------

@pytest.mark.verifies("FR-1230")
def test_series_inject_leaves_severity_and_severity_inject_keeps_series():
    mgr = SessionManager(_vig(), seed=0)
    mgr.start()
    mgr.set_clock(False)
    mgr.fire_inject([{"type": "space_weather", "severity": "severe"}])
    assert mgr.world.space_weather == {"severity": "severe"}
    mgr.fire_inject([{"type": "space_weather", "index_series": [{"kp": 6}]}])
    assert mgr.world.space_weather["severity"] == "severe"
    assert mgr.world.space_weather["index_series"][0]["kp"] == 6.0
    mgr.fire_inject([{"type": "space_weather", "severity": "clear"}])
    assert mgr.world.space_weather["severity"] == "none"
    assert len(mgr.world.space_weather["index_series"]) == 1


@pytest.mark.verifies("FR-1230")
def test_later_series_inject_replaces_entries_at_or_after_its_start():
    mgr = SessionManager(_vig(series=[{"at_sim_s": 0, "kp": 1}, {"at_sim_s": 7200, "kp": 8}]), seed=0)
    mgr.start()
    mgr.set_clock(False)
    mgr.advance_to(mgr.sim.clock.now + HOUR)
    mgr.fire_inject([{"type": "space_weather", "index_series": [{"offset_s": 0, "kp": 3}]}])
    kps = [e["kp"] for e in mgr.world.space_weather["index_series"]]
    assert kps == [1, 3]      # the t=+2h Kp 8 entry is superseded by the inject's own series


@pytest.mark.verifies("FR-1230")
def test_vignette_series_is_stored_in_absolute_sim_time():
    mgr = SessionManager(_vig(series=[{"at_sim_s": 60, "f107": 120}]), seed=0)
    start = mgr.ctx.start_epoch
    assert mgr.world.space_weather["index_series"] == [{"t": start + 60_000_000, "f107": 120.0}]
    assert mgr.world.space_weather["severity"] == "none"
    assert math.isfinite(BUS_TICK_PERIOD_S)
