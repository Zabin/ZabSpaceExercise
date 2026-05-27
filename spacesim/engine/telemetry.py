"""Subsystem telemetry — realistic, seeded, read-time signals for operator troubleshooting.

This is a **pure read-time derived signal** (like ``session.scene.build_scene``): it never mutates
``WorldState`` and never draws the engine RNG, so it cannot perturb deterministic replay. Each
parameter is ``baseline(real state) + seeded value-noise + attack term``. The noise is a pure hash
of ``(seed, asset, param, time-bucket)`` interpolated for continuity, so a series is exactly
repeatable for a given session seed.

**Attack signatures** are deliberately *symptoms, not labels* — the value (e.g. receiver RX power)
deviates and may breach its own limit, but nothing here says "you are being jammed". The operator
diagnoses from the graphs/logs. Each vector leaves at least one sign:
  * EW jam     → comms.rx_power_dbm ↑, cn0_dbhz ↓, ber ↑, uplink_lock intermittent
  * Cyber      → cdh.cpu_load_pct ↑, fsw_error_count ↑, cmd_reject_count ↑ (fsw=safe at safe mode)
  * Directed E → payload.snr_db ↓, thermal.optics_temp_c ↑
  * RPO        → (SDA cue in the belief scene) + attitude wheel/error bump if evading
  * Kinetic    → loss-of-signal (destroyed asset returns no telemetry)
  * Power      → power.battery_soc + bus_voltage_v sag in eclipse / power-red
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

from spacesim.engine.bus import status_high, status_low


@dataclass(frozen=True)
class ParamSpec:
    id: str
    subsystem: str
    label: str
    unit: str
    nominal: float
    amp: float          # noise amplitude (physical units)
    soft: float
    hard: float
    higher_is_bad: bool


PARAMS: dict[str, ParamSpec] = {p.id: p for p in [
    ParamSpec("battery_soc", "power", "Battery SoC", "frac", 0.9, 0.01, 0.30, 0.15, False),
    ParamSpec("bus_voltage_v", "power", "Bus voltage", "V", 28.0, 0.15, 26.0, 24.0, False),
    ParamSpec("array_current_a", "power", "Array current", "A", 8.0, 0.2, 1.0, 0.2, False),
    ParamSpec("attitude_error_deg", "attitude", "Attitude error", "deg", 0.05, 0.02, 1.0, 5.0, True),
    ParamSpec("wheel_rpm", "attitude", "Reaction wheel", "rpm", 2000.0, 25.0, 5500.0, 6500.0, True),
    ParamSpec("payload_temp_c", "thermal", "Payload temp", "degC", 15.0, 0.5, 35.0, 50.0, True),
    ParamSpec("optics_temp_c", "thermal", "Optics temp", "degC", -10.0, 0.5, 5.0, 20.0, True),
    ParamSpec("propellant_frac", "propulsion", "Propellant", "frac", 1.0, 0.002, 0.15, 0.05, False),
    ParamSpec("tank_pressure_kpa", "propulsion", "Tank pressure", "kPa", 1500.0, 5.0, 900.0, 700.0, False),
    ParamSpec("cpu_load_pct", "cdh", "CPU load", "%", 30.0, 2.0, 80.0, 95.0, True),
    ParamSpec("fsw_error_count", "cdh", "FSW errors", "count", 0.0, 0.0, 5.0, 20.0, True),
    ParamSpec("cmd_reject_count", "cdh", "Cmd rejects", "count", 0.0, 0.0, 3.0, 10.0, True),
    ParamSpec("storage_frac", "cdh", "Storage", "frac", 0.2, 0.01, 0.85, 0.98, True),
    ParamSpec("rx_power_dbm", "comms", "RX power", "dBm", -95.0, 1.0, -80.0, -70.0, True),
    ParamSpec("cn0_dbhz", "comms", "C/N0", "dB-Hz", 55.0, 0.6, 45.0, 38.0, False),
    ParamSpec("ber", "comms", "Bit error rate", "ratio", 1e-6, 0.0, 1e-4, 1e-3, True),
    ParamSpec("uplink_lock", "comms", "Uplink lock", "bool", 1.0, 0.0, 0.5, 0.5, False),
    ParamSpec("snr_db", "payload", "Payload SNR", "dB", 30.0, 0.8, 15.0, 8.0, False),
]}

_MICRO = 1_000_000
_BUCKET_S = 30
_ORBIT_S = 5400.0


def _h01(*parts) -> float:
    digest = hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:8]
    return int(digest, 16) / 0xFFFFFFFF


def _noise(seed: int, asset: str, param: str, t: int) -> float:
    """Continuous seeded value-noise in [-1, 1] (interpolated between 30 s buckets)."""
    step = _BUCKET_S * _MICRO
    b, frac = divmod(t, step)
    a = _h01(seed, asset, param, b) * 2 - 1
    c = _h01(seed, asset, param, b + 1) * 2 - 1
    return a + (c - a) * (frac / step)


def _active(world, asset_id: str, t: int):
    """Flags + onset times for attacks currently affecting the asset (read from active_effects)."""
    flags = {"jam": False, "cyber": False, "de": False}
    onset = {}
    for ae in world.active_effects:
        if ae.target != asset_id or not (ae.start <= t <= ae.end):
            continue
        if ae.category == "electronic_warfare" and ae.outcome in ("deny", "disrupt"):
            flags["jam"] = True; onset.setdefault("jam", ae.start)
        elif ae.category == "cyber":
            flags["cyber"] = True; onset.setdefault("cyber", ae.start)
        elif ae.category == "directed_energy":
            flags["de"] = True; onset.setdefault("de", ae.start)
    return flags, onset


def _baseline(asset, spec: ParamSpec, t: int) -> float:
    bus = getattr(asset, "bus_state", None)
    if bus is not None:
        if spec.id == "battery_soc":
            return bus.power.battery_soc
        if spec.id == "storage_frac":
            return bus.cdh.storage_frac
        if spec.id == "propellant_frac":
            return bus.propulsion.propellant_frac
        if spec.id == "bus_voltage_v":
            return 24.5 if bus.power.status == "red" else (27.4 if bus.power.in_eclipse else 28.0)
        if spec.id == "array_current_a":
            return 0.1 if bus.power.in_eclipse else 8.0
    if spec.id in ("fsw_error_count", "cmd_reject_count"):
        return 0.0
    if spec.id == "uplink_lock":
        return 1.0
    if spec.id == "ber":
        return 1e-6
    # gentle orbital drift for free-running analog params
    return spec.nominal + 0.5 * spec.amp * math.sin(2 * math.pi * (t / _MICRO) / _ORBIT_S)


def _mitigation(asset) -> float:
    """SATCOM anti-jam in effect (0..1) — shrinks the jam signature (satcom.mitigate_interference)."""
    p = getattr(asset, "payload_state", None)
    return getattr(p, "interference_mitigation", 0.0) if p is not None else 0.0


def _attack_term(asset, world, spec: ParamSpec, t: int, flags, onset) -> float:
    bus = getattr(asset, "bus_state", None)
    safed = bus is not None and bus.mode == "safe_mode"
    pid = spec.id
    jam = 1.0 - _mitigation(asset)                    # operator anti-jam reduces the experienced jam
    if pid == "rx_power_dbm" and flags["jam"]:
        return 28.0 * jam                             # jammer energy raises measured RX power
    if pid == "cn0_dbhz" and flags["jam"]:
        return -14.0 * jam
    if pid == "ber":
        return 8e-3 * jam if flags["jam"] else 0.0
    if pid == "uplink_lock" and flags["jam"]:
        return -1.0 if _noise(0, asset.id, "lock", t) < 0 else 0.0   # intermittent lock
    if pid == "cpu_load_pct" and (flags["cyber"] or (safed and bus.safe_mode.cause == "cyber")):
        return 45.0
    if pid in ("fsw_error_count", "cmd_reject_count"):
        start = onset.get("cyber")
        if start is None and safed and bus.safe_mode.cause == "cyber":
            start = bus.safe_mode.entered_at
        if start is not None and t >= start:
            rate = 0.04 if pid == "fsw_error_count" else 0.012   # counts/s while present
            return min(spec.hard * 2.5, rate * (t - start) / _MICRO)
        return 0.0
    if pid == "snr_db":
        if safed:
            return -28.0                              # payload off in safe mode
        if flags["de"]:
            return -16.0
    if pid == "optics_temp_c" and flags["de"]:
        return 12.0
    if pid == "attitude_error_deg" and safed:
        return 2.5                                    # slew to sun-point
    return 0.0


def sample(world, asset_id: str, param_id: str, t: int, seed: int, nominal: bool = False) -> dict:
    """Physical value + limit status of one parameter at time ``t`` (read-only).

    ``nominal=True`` returns the clean baseline+noise with **no attack term** — the "what it should
    look like" ghost the troubleshooting overlay draws so deviation under attack is obvious (§5.3).
    A destroyed asset still has a nominal trace (loss-of-signal is an attack symptom, not nominal).
    """
    spec = PARAMS[param_id]
    asset = world.assets.get(asset_id)
    if asset is None:
        return {"param": param_id, "value": None, "status": "los", "unit": spec.unit}
    if getattr(asset, "health", "nominal") == "destroyed" and not nominal:
        return {"param": param_id, "value": None, "status": "los", "unit": spec.unit}

    val = _baseline(asset, spec, t) + _noise(seed, asset_id, param_id, t) * spec.amp
    if not nominal:
        flags, onset = _active(world, asset_id, t)
        val += _attack_term(asset, world, spec, t, flags, onset)

    if spec.unit == "frac":
        val = max(0.0, min(1.0, val))
    if param_id == "ber":
        val = max(1e-9, val)
    if param_id == "uplink_lock":
        val = 1.0 if val > 0.5 else 0.0

    status = (status_high if spec.higher_is_bad else status_low)(val, spec.soft, spec.hard)
    return {"param": param_id, "value": round(val, 6), "status": status, "unit": spec.unit}


def series(world, asset_id: str, param_id: str, t0: int, t1: int, n: int, seed: int,
           nominal: bool = False) -> list[dict]:
    if n < 2:
        n = 2
    step = (t1 - t0) / (n - 1)
    out = []
    for i in range(n):
        t = int(t0 + i * step)
        s = sample(world, asset_id, param_id, t, seed, nominal=nominal)
        out.append({"t": t, "value": s["value"], "status": s["status"]})
    return out


def telemetry_db(world, asset_id: str, t: int, seed: int) -> dict:
    """Parameter list grouped by subsystem with current value/status — drives the drill-down menu."""
    db: dict[str, list] = {}
    for spec in PARAMS.values():
        s = sample(world, asset_id, spec.id, t, seed)
        db.setdefault(spec.subsystem, []).append({
            "id": spec.id, "label": spec.label, "unit": spec.unit,
            "value": s["value"], "status": s["status"], "soft": spec.soft, "hard": spec.hard,
        })
    return db


def subsystem_log(world, asset_id: str, t: int, seed: int) -> list[str]:
    """Recent symptom log — off-nominal parameters as physical readings (no cause is named)."""
    from spacesim.engine.simtime import to_iso
    out = []
    for spec in PARAMS.values():
        s = sample(world, asset_id, spec.id, t, seed)
        if s["value"] is not None and s["status"] != "green":
            out.append(f"{to_iso(t)[11:19]}  {spec.subsystem}.{spec.id} = {s['value']} {spec.unit}  [{s['status'].upper()}]")
    asset = world.assets.get(asset_id)
    if asset is not None and getattr(asset, "bus_state", None) is not None and asset.bus_state.mode == "safe_mode":
        out.append(f"{to_iso(t)[11:19]}  bus mode = SAFE_MODE; payload disabled")
    return out
