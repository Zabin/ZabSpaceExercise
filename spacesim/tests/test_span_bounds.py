"""IP-1089 (FR-7450) — ISO-8601 UTC span bounds on the three time-span exports."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from spacesim.engine import simtime
from spacesim.session import ephemeris
from spacesim.ui_web.server import create_app

try:
    from spacesim.session.span_bounds import parse_span_bound
except ImportError:  # fail-first: the module does not exist yet
    parse_span_bound = None

pytestmark = pytest.mark.verifies("FR-7450")

_MICROS = [0, 1, 1_700_000_000_123_456, 951_782_400_000_000, 1_893_456_000_000_000,
           simtime.from_iso("2030-01-01T00:00:00Z"), 1_709_251_199_999_999, 4_102_444_799_000_000]


@pytest.mark.parametrize("us", _MICROS)
def test_iso_round_trips_simtime_to_iso(us):
    iso = simtime.to_iso(us)  # '+00:00' form, fraction only when non-zero
    assert parse_span_bound(iso, "t1") == us
    assert parse_span_bound(iso.replace("+00:00", "Z"), "t1") == us


def test_fraction_lengths_and_integer_forms():
    assert parse_span_bound("2030-01-01T00:00:00.5Z", "t1") == simtime.from_iso("2030-01-01T00:00:00Z") + 500_000
    assert parse_span_bound("2030-01-01T00:00:00.000001+00:00", "t1") == simtime.from_iso("2030-01-01T00:00:00Z") + 1
    assert parse_span_bound(123, "t1") == 123
    assert parse_span_bound("-123", "t1") == -123
    assert parse_span_bound("20261031", "t1") == 20261031  # digits-only is microseconds, never a date


@pytest.mark.parametrize("bad", [
    "2030-01-01T00:00:00", "2030-01-01T00:00:00+05:00", "2030-01-01T00:00:00.1234567Z", "2030-01-01",
    "20301231T000000Z", "2030-W01-1T00:00:00Z", "2030-001T00:00:00Z", "2030-12-31T23:59:60Z",
    "2030-13-01T00:00:00Z", "2030-02-30T00:00:00Z", "2030-01-01t00:00:00Z", "2030-01-01T00:00:00z",
    "", "garbage", "1.5", "2030-01-01T24:00:00Z", "2030-01-01T00:60:00Z",
])
def test_refusals_name_bound_and_reason(bad):
    with pytest.raises(ValueError, match=r"^t2: .+"):
        parse_span_bound(bad, "t2")


@pytest.mark.parametrize("bad", [True, False, float("nan"), float("inf"), 1.5, None])
def test_non_integer_guards(bad):
    with pytest.raises(ValueError, match=r"^t1: "):
        parse_span_bound(bad, "t1")


# ---- HTTP parity ------------------------------------------------------------------------------
def _session():
    """A co-orbital session in which Blue holds a state-bearing Track on RED-COORB, so every
    ephemeris body below is non-trivial (satellites on both ends, a Blue-owned Track)."""
    from spacesim.engine.custody import Track
    from spacesim.session.inprocess import InProcessSession
    api = InProcessSession()
    c = TestClient(create_app(api))
    sid = c.post("/api/sessions", json={"vignette_id": "co-orbital-threat-escort", "seed": 1}).json()["session"]
    c.post(f"/api/sessions/{sid}/start?cell=white")
    c.post(f"/api/sessions/{sid}/clock?cell=white", json={"running": False})
    world = api._sessions[sid].sim.world
    trk = Track(object="RED-COORB", owner="blue", last_observation=world.now, confidence=0.9,
                state_estimate=world.assets["RED-COORB"].orbit.model_copy(deep=True))
    world.tracks.append(trk)
    api._sessions[sid].sim._initial_state["tracks"].append(trk.model_dump())  # survives replay
    c.post(f"/api/sessions/{sid}/step?cell=white", json={"dt_sim_s": 600})
    # the recorded range: [initial epoch, current sim time] (the lazy clock may have drifted a few us)
    end = c.get(f"/api/sessions/{sid}/save").json()["final_time"]
    first = c.get(f"/api/sessions/{sid}/telemetry/blue/BLUE-ESCORT/export.csv").text.splitlines()[1]
    start = int(first.split(",")[0])
    return c, sid, start, end


def _routes(sid):
    p = f"/api/sessions/{sid}"
    eph = {"object_id": "RED-COORB", "reference_id": "BLUE-HVA"}
    return [(f"{p}/telemetry/blue/BLUE-ESCORT/export.csv", {}),
            (f"{p}/ephemeris/truth", eph), (f"{p}/ephemeris/blue", eph)]


def _norm(text):  # the OEM header stamps a wall-clock CREATION_DATE (pre-existing, not an input)
    return "\n".join(l for l in text.splitlines() if not l.startswith("CREATION_DATE"))


def _get(c, url, base, t1, t2, fmt=None, **kw):
    q = dict(base, t1=t1, t2=t2, interval_s=60, **kw)
    if fmt:
        q["format"] = fmt
    return c.get(url, params=q)


def test_http_iso_and_integer_bodies_identical_all_routes_and_formats():
    c, sid, start, end = _session()
    iso1 = simtime.to_iso(start).replace("+00:00", "Z")
    iso2 = simtime.to_iso(end)
    for url, base in _routes(sid):
        fmts = [None] if "telemetry" in url else ["csv", "oem", "ric"]
        for fmt in fmts:
            ref = _get(c, url, base, start, end, fmt)
            assert ref.status_code == 200, (url, fmt, ref.text)
            assert len(ref.text.splitlines()) > 5, (url, fmt)  # non-trivial body, not header-only
            assert _norm(_get(c, url, base, iso1, iso2, fmt).text) == _norm(ref.text)
            assert _norm(_get(c, url, base, iso1, end, fmt).text) == _norm(ref.text)  # mixed pair
            assert _norm(_get(c, url, base, start, iso2, fmt).text) == _norm(ref.text)


@pytest.mark.verifies("FR-7450", "NFR-3710")
def test_http_refusals_are_400_naming_bound():
    c, sid, start, end = _session()
    for url, base in _routes(sid):
        r = _get(c, url, base, "2030-01-01T00:00:00", end)
        assert r.status_code == 400 and r.json()["detail"].startswith("t1: ")
        r = _get(c, url, base, start, "nonsense")
        assert r.status_code == 400 and r.json()["detail"].startswith("t2: ")


def test_http_partial_clamp_wholly_out_and_max_samples_via_iso():
    c, sid, start, end = _session()
    far = simtime.to_iso(end + 10_000_000_000)
    far2 = simtime.to_iso(end + 20_000_000_000)
    before = simtime.to_iso(start - 3_600_000_000)
    for url, base in _routes(sid):
        assert _get(c, url, base, far, far2).status_code == 400
        a = _get(c, url, base, before, simtime.to_iso(end + 10_000_000_000))
        b = _get(c, url, base, start - 3_600_000_000, end + 10_000_000_000)
        assert a.status_code == 200 and _norm(a.text) == _norm(b.text)
        r = c.get(url, params=dict(base, t1=before, t2=simtime.to_iso(end), interval_s=0.0001))
        assert r.status_code == 400 and str(ephemeris.MAX_EXPORT_SAMPLES) in r.json()["detail"]


def test_refused_bound_causes_no_replay(monkeypatch):
    from spacesim.session import aar
    c, sid, start, end = _session()

    def boom(*a, **k):
        raise AssertionError("replay ran")
    monkeypatch.setattr(aar, "worlds_at_times", boom)
    for url, base in _routes(sid):
        assert _get(c, url, base, "bad", end).status_code == 400


@pytest.mark.verifies("FR-7450", "FR-2320")
def test_telemetry_omitted_bounds_default_unchanged():
    c, sid, start, end = _session()
    url = f"/api/sessions/{sid}/telemetry/blue/BLUE-ESCORT/export.csv"
    full = c.get(url, params={"interval_s": 60})
    explicit = c.get(url, params={"t1": start, "t2": end, "interval_s": 60})
    assert full.status_code == 200 and full.text == explicit.text
    only1 = c.get(url, params={"t1": simtime.to_iso(start), "interval_s": 60})
    assert only1.text == explicit.text


def test_out_of_scope_routes_do_not_use_the_parser():
    c, sid, start, end = _session()
    r = c.get(f"/api/sessions/{sid}/telemetry/blue/BLUE-ESCORT/snr_db",
              params={"t0": "2030-01-01T00:00:00Z", "t1": end})
    assert r.status_code == 422  # series window stays integer-only


def test_digit_string_over_int_conversion_limit_names_bound():
    with pytest.raises(ValueError, match=r"^t1: .*digits"):
        parse_span_bound("9" * 5000, "t1")
    assert parse_span_bound("9" * 30, "t1") == int("9" * 30)


def test_leap_day_accepted_and_non_leap_century_refused():
    assert parse_span_bound("2032-02-29T00:00:00Z", "t1") == simtime.from_iso("2032-02-29T00:00:00Z")
    assert parse_span_bound("2000-02-29T00:00:00Z", "t1") == simtime.from_iso("2000-02-29T00:00:00Z")
    with pytest.raises(ValueError, match=r"^t2: .*date"):
        parse_span_bound("2100-02-29T00:00:00Z", "t2")
