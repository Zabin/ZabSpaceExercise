"""Subsystem telemetry: determinism, read-only, per-attack signatures, fog, and the map data file."""

from __future__ import annotations

import json
from pathlib import Path

from spacesim.content.vignette import load_vignette
from spacesim.engine import telemetry as tel
from spacesim.engine.bus import BusState, enter_safe_mode
from spacesim.engine.effects import ActiveEffect
from spacesim.engine.entities import Asset
from spacesim.engine.simtime import minutes
from spacesim.engine.world import WorldState
from spacesim.session.manager import SessionManager

SEED = 42


def _world():
    w = WorldState(now=minutes(20))
    w.assets["SAT"] = Asset(id="SAT", owner="blue", kind="satellite", bus_state=BusState())
    return w


def _val(w, param, t=None):
    return tel.sample(w, "SAT", param, t if t is not None else w.now, SEED)["value"]


def test_sampling_is_deterministic_and_repeatable():
    w = _world()
    assert tel.sample(w, "SAT", "rx_power_dbm", 12345, SEED) == tel.sample(w, "SAT", "rx_power_dbm", 12345, SEED)
    s1 = tel.series(w, "SAT", "cn0_dbhz", 0, minutes(60), 50, SEED)
    s2 = tel.series(_world(), "SAT", "cn0_dbhz", 0, minutes(60), 50, SEED)
    assert s1 == s2
    # Different seed → different noise realization.
    assert tel.series(w, "SAT", "cn0_dbhz", 0, minutes(60), 50, SEED + 1) != s1


def test_sampling_is_read_only():
    w = _world()
    before = w.model_dump_json()
    tel.telemetry_db(w, "SAT", w.now, SEED)
    tel.series(w, "SAT", "battery_soc", 0, minutes(60), 100, SEED)
    assert w.model_dump_json() == before  # never mutates world state


def test_sampler_returns_physical_values_only_no_cause_label():
    w = _world()
    w.active_effects.append(ActiveEffect(target="SAT", outcome="deny", start=0, end=minutes(60),
                                         category="electronic_warfare"))
    s = tel.sample(w, "SAT", "rx_power_dbm", w.now, SEED)
    assert set(s.keys()) == {"param", "value", "status", "unit"}  # no "cause"/"attack" hint
    for entry in tel.telemetry_db(w, "SAT", w.now, SEED)["comms"]:
        assert "cause" not in entry and "attack" not in entry


def test_ew_jam_signature_raises_rx_power_and_recovers():
    clean = _world()
    nominal_rx = _val(clean, "rx_power_dbm", minutes(20))
    nominal_cn0 = _val(clean, "cn0_dbhz", minutes(20))
    nominal_cpu = _val(clean, "cpu_load_pct", minutes(20))
    w = _world()
    w.active_effects.append(ActiveEffect(target="SAT", outcome="deny", start=0, end=minutes(40),
                                         category="electronic_warfare"))
    assert _val(w, "rx_power_dbm", minutes(20)) > nominal_rx + 15   # receiver power climbs under jamming
    assert _val(w, "cn0_dbhz", minutes(20)) < nominal_cn0 - 8       # C/N0 drops
    assert _val(w, "ber", minutes(20)) > 1e-3                       # bit-error-rate spikes
    assert abs(_val(w, "cpu_load_pct", minutes(20)) - nominal_cpu) < 20  # unrelated subsystem quiet
    assert _val(w, "rx_power_dbm", minutes(50)) < nominal_rx + 5    # back to nominal after the window


def test_nominal_series_strips_attack_signature_for_compare_overlay():
    """The 'compare-to-nominal' ghost (§5.3) is baseline+noise with no attack term.

    Under jamming the real RX power climbs far above its nominal trace during the window, while the
    nominal series stays in-band — so the deviation the operator overlays is the signature itself.
    """
    w = _world()
    w.active_effects.append(ActiveEffect(target="SAT", outcome="deny", start=0, end=minutes(40),
                                         category="electronic_warfare"))
    real = tel.sample(w, "SAT", "rx_power_dbm", minutes(20), SEED)["value"]
    ghost = tel.sample(w, "SAT", "rx_power_dbm", minutes(20), SEED, nominal=True)["value"]
    assert real > ghost + 15                                   # attack term is visible as deviation
    # The nominal trace matches a never-attacked world's normal trace (only baseline+noise remain).
    clean = tel.sample(_world(), "SAT", "rx_power_dbm", minutes(20), SEED)["value"]
    assert ghost == clean
    # Outside the jam window the real and nominal traces converge.
    assert abs(tel.sample(w, "SAT", "rx_power_dbm", minutes(50), SEED)["value"]
               - tel.sample(w, "SAT", "rx_power_dbm", minutes(50), SEED, nominal=True)["value"]) < 5


def test_nominal_series_is_deterministic_and_read_only():
    w = _world()
    w.active_effects.append(ActiveEffect(target="SAT", outcome="deny", start=0, end=minutes(40),
                                         category="electronic_warfare"))
    before = w.model_dump_json()
    s1 = tel.series(w, "SAT", "cn0_dbhz", 0, minutes(60), 40, SEED, nominal=True)
    s2 = tel.series(_world(), "SAT", "cn0_dbhz", 0, minutes(60), 40, SEED, nominal=True)
    assert s1 == s2 and w.model_dump_json() == before


def test_cyber_signature_ramps_fsw_errors_under_safe_mode():
    w = _world()
    enter_safe_mode(w.assets["SAT"].bus_state, now=0, cause="cyber")
    early = _val(w, "fsw_error_count", minutes(1))
    late = _val(w, "fsw_error_count", minutes(30))
    assert late > early > 0                      # error counter climbs while the foothold persists
    assert _val(w, "cpu_load_pct", minutes(30)) > 60
    assert tel.sample(w, "SAT", "fsw_error_count", minutes(30), SEED)["status"] in ("yellow", "red")


def test_directed_energy_signature_drops_snr_and_heats_optics():
    w = _world()
    w.active_effects.append(ActiveEffect(target="SAT", outcome="degrade", start=0, end=minutes(40),
                                         category="directed_energy"))
    assert _val(w, "snr_db", minutes(20)) < _val(_world(), "snr_db", minutes(20)) - 8
    assert _val(w, "optics_temp_c", minutes(20)) > _val(_world(), "optics_temp_c", minutes(20)) + 6


def test_power_sag_and_kinetic_loss_of_signal():
    w = _world()
    w.assets["SAT"].bus_state.power.battery_soc = 0.1  # power-red
    from spacesim.engine.bus import recompute_status
    recompute_status(w.assets["SAT"].bus_state)
    assert tel.sample(w, "SAT", "battery_soc", w.now, SEED)["status"] == "red"
    assert _val(w, "bus_voltage_v") < 26.0

    w.assets["SAT"].health = "destroyed"
    s = tel.sample(w, "SAT", "rx_power_dbm", w.now, SEED)
    assert s["value"] is None and s["status"] == "los"   # loss of signal after a kill


def test_fog_blocks_other_cells_telemetry():
    mgr = SessionManager(load_vignette("training-basics"), seed=1)
    mgr.start()
    assert mgr.get_telemetry("blue", "ISR-EO-1") is not None      # own asset
    assert mgr.get_telemetry("red", "ISR-EO-1") is None           # other cell's asset → fog


def test_world_map_data_present_and_nontrivial():
    p = Path(__file__).resolve().parent.parent / "ui_web" / "static" / "world.json"
    data = json.loads(p.read_text())
    assert data["coast"] and data["borders"]
    pts = sum(len(s) for s in data["coast"]) + sum(len(s) for s in data["borders"])
    assert pts > 1000  # a real low-res world, not a stub


# -- IP-1260 (FR-2320) — per-asset telemetry CSV export over a time span ---------------------

def _export_mgr():
    """training-basics, clock paused; a bus `anomaly` inject (FR-4430) fires at +600 s and the
    session then runs on to +1200 s, so the recorded range brackets the perturbation's onset."""
    mgr = SessionManager(load_vignette("training-basics"), seed=1)
    mgr.start()
    mgr.set_clock(False)
    t0 = mgr.ctx.start_epoch
    mgr.advance_to(t0 + minutes(10))
    mgr.fire_inject([{"type": "anomaly", "target": "ISR-EO-1", "subsystem": "bus",
                      "cause": "export test"}])
    mgr.advance_to(t0 + minutes(20))
    return mgr, t0, t0 + minutes(10)


def _by_param(rows, param):
    return [r for r in rows if r["param"] == param]


def test_telemetry_export_reflects_anomaly_perturbation_at_correct_times():
    mgr, t0, t_anom = _export_mgr()
    rows = mgr.telemetry_export("blue", "ISR-EO-1", t0, mgr.sim.clock.now, interval_s=60)
    snr = _by_param(rows, "snr_db")
    assert len(snr) == 21
    before = [r for r in snr if r["t"] < t_anom]
    after = [r for r in snr if r["t"] >= t_anom]
    assert before and after
    # Payload SNR is nominal (~30 dB) before the anomaly safes the bus, ~2 dB (payload off) after —
    # read at each sampled time's own world state, not the end-of-span state.
    assert all(r["value"] > 25 and r["status"] == "green" for r in before)
    assert all(r["value"] < 8 and r["status"] == "red" for r in after)
    att = _by_param(rows, "attitude_error_deg")
    assert all(r["value"] < 1.0 for r in att if r["t"] < t_anom)
    assert all(r["value"] > 1.0 for r in att if r["t"] >= t_anom)


def test_telemetry_export_matches_live_endpoint_and_engine_sample_at_each_point():
    from spacesim.session import aar
    mgr, t0, _ = _export_mgr()
    now = mgr.sim.clock.now
    rows = mgr.telemetry_export("blue", "ISR-EO-1", t0, now, interval_s=300)
    # Every exported value is exactly engine/telemetry.py's own sample() on the world as of t.
    for r in rows:
        world_t = aar.state_at_time(mgr, r["t"])
        s = tel.sample(world_t, "ISR-EO-1", r["param"], r["t"], mgr.sim._seed)
        assert (r["value"], r["status"], r["unit"]) == (s["value"], s["status"], s["unit"])
    # And the final sample (t == now) is identical to the live JSON telemetry endpoint's reading.
    live = {p["id"]: p for sub in mgr.get_telemetry("blue", "ISR-EO-1")["subsystems"].values()
            for p in sub}
    last = [r for r in rows if r["t"] == now]
    assert len(last) == len(tel.PARAMS)
    for r in last:
        assert (r["value"], r["status"]) == (live[r["param"]]["value"], live[r["param"]]["status"])


def test_telemetry_export_is_fog_scoped_per_requesting_cell():
    mgr, t0, _ = _export_mgr()
    now = mgr.sim.clock.now
    assert mgr.telemetry_export("red", "ISR-EO-1", t0, now) is None      # another cell's asset
    assert mgr.telemetry_export("observer", "ISR-EO-1", t0, now) is None  # not a cell that owns it
    assert mgr.telemetry_export("blue", "NO-SUCH-ASSET", t0, now) is None
    blue = mgr.telemetry_export("blue", "ISR-EO-1", t0, now, interval_s=300)
    white = mgr.telemetry_export("white", "ISR-EO-1", t0, now, interval_s=300)
    assert blue == white   # White sees any asset, exactly as /telemetry/{cell}/{asset} does


def test_telemetry_export_is_read_only_and_deterministic():
    mgr, t0, _ = _export_mgr()
    now = mgr.sim.clock.now
    before = mgr.sim.world.model_dump()
    n_events = len(mgr.sim.eventlog.entries)
    a = mgr.telemetry_export("blue", "ISR-EO-1", t0, now, interval_s=120)
    b = mgr.telemetry_export("blue", "ISR-EO-1", t0, now, interval_s=120)
    assert a == b
    assert mgr.sim.world.model_dump() == before
    assert len(mgr.sim.eventlog.entries) == n_events and mgr.sim.clock.now == now


def test_telemetry_export_wholly_out_of_range_rejected():
    import pytest
    mgr, t0, _ = _export_mgr()
    now = mgr.sim.clock.now
    with pytest.raises(ValueError):
        mgr.telemetry_export("blue", "ISR-EO-1", now + minutes(1), now + minutes(2))
    with pytest.raises(ValueError):
        mgr.telemetry_export("blue", "ISR-EO-1", t0 - minutes(2), t0 - minutes(1))


def test_telemetry_export_partially_out_of_range_clamped():
    mgr, t0, _ = _export_mgr()
    now = mgr.sim.clock.now
    rows = mgr.telemetry_export("blue", "ISR-EO-1", t0 - minutes(5), now + minutes(5), interval_s=60)
    times = sorted({r["t"] for r in rows})
    assert times[0] == t0 and times[-1] <= now
    assert len(times) == 21   # clamped to [t0, now], sampled every 60 s


def test_telemetry_export_default_span_is_the_recorded_range():
    mgr, t0, _ = _export_mgr()
    rows = mgr.telemetry_export("blue", "ISR-EO-1", interval_s=600)
    assert sorted({r["t"] for r in rows}) == [t0, t0 + minutes(10), t0 + minutes(20)]
    assert {r["param"] for r in rows} == set(tel.PARAMS)
