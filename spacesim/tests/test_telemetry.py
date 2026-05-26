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
