"""Bus & payload state-of-health model (``01-research/06`` §5, ``12-safe-mode-loop.md`` §8).

Every satellite carries a small live ``BusState`` — power (battery + eclipse), attitude,
thermal, propulsion, onboard storage (C&DH), and comms — each limit-checked to green/yellow/red.
The bus **gates the payload**: in safe mode or a power-red condition the payload does no mission,
and full onboard storage blocks further ISR collection until a downlink. Telemetry is
**pass-gated**: ``ground_view`` is the last snapshot the ground actually received and only
refreshes on contact, so an out-of-contact event (e.g. entering safe mode) is discovered later.

This module is pure data + limit logic (pydantic only). The time-stepping that computes eclipse
from orbit geometry lives in ``busmodel.py`` to keep this importable by ``world.py`` without a cycle.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

Status = Literal["green", "yellow", "red"]
_RANK = {"green": 0, "yellow": 1, "red": 2}

# Limits (fractions). Power is "good when high"; storage/propellant thresholds below.
SOC_SOFT, SOC_HARD = 0.30, 0.15
STORAGE_SOFT, STORAGE_HARD = 0.85, 0.98
PROP_SOFT, PROP_HARD = 0.15, 0.05


def status_low(value: float, soft: float, hard: float) -> Status:
    """For quantities that are healthy when HIGH (battery SoC, propellant)."""
    if value <= hard:
        return "red"
    if value <= soft:
        return "yellow"
    return "green"


def status_high(value: float, soft: float, hard: float) -> Status:
    """For quantities that are unhealthy when HIGH (storage fill)."""
    if value >= hard:
        return "red"
    if value >= soft:
        return "yellow"
    return "green"


class PowerState(BaseModel):
    battery_soc: float = 1.0
    in_eclipse: bool = False
    status: Status = "green"
    charge_rate_per_s: float = 0.0   # SoC/s while sunlit
    drain_rate_per_s: float = 0.0    # SoC/s while in eclipse / under load
    loads_shed: bool = False         # non-critical loads shed (eps.shed_load) → reduced drain
    charge_mode: Literal["nominal", "fast", "trickle"] = "nominal"   # eps.set_charge_mode → scales charge


class AttitudeState(BaseModel):
    pointing_ok: bool = True
    mode: Literal["nominal", "slew", "safe"] = "nominal"
    status: Status = "green"


class ThermalState(BaseModel):
    status: Status = "green"
    mode: Literal["nominal", "survival", "operational"] = "operational"
    heater_on: bool = False


class PropulsionState(BaseModel):
    propellant_frac: float = 1.0
    status: Status = "green"


class CdhState(BaseModel):
    storage_frac: float = 0.0
    fsw_mode: Literal["nominal", "safe"] = "nominal"
    status: Status = "green"


class CommsState(BaseModel):
    uplink_lock: bool = False
    downlink_lock: bool = False
    status: Status = "green"
    isl_enabled: bool = False
    data_rate_kbps: int = 1024
    freq_hopping: bool = False               # def.frequency_hop → reduces experienced jam
    antenna_mode: str = "nominal"            # comms.point_antenna: nominal|earth|zenith|tracking


class SafeModeState(BaseModel):
    active: bool = False
    entered_at: Optional[int] = None
    cause: Optional[str] = None              # fault|environment|cyber|ew|bus_stress (truth)
    defender_confirmed: bool = False
    defender_diagnosis: str = "unknown"      # unknown|suspected_attack|fault|<subsystem>
    passes_used: int = 0
    blocked_reason: Optional[str] = None     # e.g. "root cause persists: unpatched ground_modem"


class PayloadState(BaseModel):
    type: str = "isr_eo"                      # satcom|isr_eo|isr_sar|sigint|sda|space_control|...
    health: Status = "green"
    collecting: bool = False                  # ISR: actively filling onboard storage
    collect_rate_per_s: float = 0.0           # storage fraction added per second while collecting
    interference_level: float = 0.0           # SATCOM: how jamming is *experienced*
    interference_mitigation: float = 0.0      # SATCOM: anti-jam/user-shift in effect (0..1), shrinks the jam signature
    last_effect_assessment: str = "unknown"   # space_control: unknown|likely|confirmed
    hardened: bool = False                    # def.harden → lowers effect/safe-mode susceptibility
    mode: str = "nominal"                     # isr.set_mode: wide|narrow|standby|nominal; pnt.set_integrity: standard|protected|degraded
    integrity_mode: str = "standard"          # pnt.set_integrity: standard|protected|degraded
    evasion_active: bool = False              # def.maneuver_evade: set while evasion burn is live
    detail: dict = Field(default_factory=dict)


class BusState(BaseModel):
    power: PowerState = Field(default_factory=PowerState)
    attitude: AttitudeState = Field(default_factory=AttitudeState)
    thermal: ThermalState = Field(default_factory=ThermalState)
    propulsion: PropulsionState = Field(default_factory=PropulsionState)
    cdh: CdhState = Field(default_factory=CdhState)
    comms: CommsState = Field(default_factory=CommsState)
    mode: Literal["nominal", "safe_mode"] = "nominal"
    safe_mode: SafeModeState = Field(default_factory=SafeModeState)
    last_update: int = 0
    last_telemetry_time: int = 0
    ground_view: Optional[dict] = None        # pass-gated snapshot of what the ground last saw


# -- limit checking & gating ---------------------------------------------------
def recompute_status(bus: BusState) -> None:
    bus.power.status = status_low(bus.power.battery_soc, SOC_SOFT, SOC_HARD)
    bus.propulsion.status = status_low(bus.propulsion.propellant_frac, PROP_SOFT, PROP_HARD)
    bus.cdh.status = status_high(bus.cdh.storage_frac, STORAGE_SOFT, STORAGE_HARD)
    if bus.mode == "safe_mode":
        bus.attitude.mode = "safe"
        bus.cdh.fsw_mode = "safe"


def overall_status(bus: BusState) -> Status:
    if bus.mode == "safe_mode":
        return "red"
    worst = max(
        (bus.power.status, bus.attitude.status, bus.thermal.status,
         bus.propulsion.status, bus.cdh.status, bus.comms.status),
        key=lambda s: _RANK[s],
    )
    return worst


def payload_available(bus: BusState) -> bool:
    """The payload can do its mission only if not safed and power is not red."""
    return bus.mode == "nominal" and bus.power.status != "red"


def can_collect(bus: BusState) -> bool:
    return payload_available(bus) and bus.cdh.storage_frac < 1.0


def downlink_storage(bus: BusState, fraction: float = 1.0) -> None:
    bus.cdh.storage_frac = max(0.0, bus.cdh.storage_frac - fraction)
    recompute_status(bus)


def advance_bus(bus: BusState, payload: Optional[PayloadState], now: int, sunlit: bool,
                space_weather: str = "none") -> None:
    """Evolve the bus over the elapsed sim time: battery charge/drain and ISR storage fill.

    Pure function of (state, time, lighting, environment) — deterministic and replay-safe.
    ``sunlit`` is supplied by the caller (computed from orbit geometry + Sun direction in busmodel.py).
    ``space_weather`` ∈ {"none", "minor", "severe"} scales eclipse drain (FUTURE-WORK §10.C.11).
    """
    dt = max(0.0, (now - bus.last_update) / 1_000_000)
    bus.power.in_eclipse = not sunlit
    storm_mult = {"none": 1.0, "minor": 1.3, "severe": 2.0}.get(space_weather, 1.0)
    drain = bus.power.drain_rate_per_s * (0.4 if bus.power.loads_shed else 1.0) * storm_mult
    charge = bus.power.charge_rate_per_s * {"fast": 1.5, "trickle": 0.5}.get(bus.power.charge_mode, 1.0)
    delta = (charge if sunlit else -drain) * dt
    bus.power.battery_soc = max(0.0, min(1.0, bus.power.battery_soc + delta))
    if payload is not None and payload.collecting and bus.mode == "nominal" and bus.cdh.storage_frac < 1.0:
        bus.cdh.storage_frac = min(1.0, bus.cdh.storage_frac + payload.collect_rate_per_s * dt)
    recompute_status(bus)
    bus.last_update = now


def enter_safe_mode(bus: BusState, now: int, cause: str) -> None:
    bus.mode = "safe_mode"
    bus.safe_mode = SafeModeState(active=True, entered_at=now, cause=cause)
    bus.attitude.mode = "safe"
    bus.cdh.fsw_mode = "safe"
    recompute_status(bus)


def exit_safe_mode(bus: BusState) -> None:
    """Recovery succeeded: return to nominal and re-enable the payload."""
    bus.mode = "nominal"
    bus.safe_mode = SafeModeState(active=False)
    bus.attitude.mode = "nominal"
    bus.cdh.fsw_mode = "nominal"
    recompute_status(bus)


# -- pass-gated telemetry & fidelity views -------------------------------------
def soh_snapshot(bus: BusState) -> dict:
    return {
        "mode": bus.mode,
        "power": bus.power.status,
        "attitude": bus.attitude.status,
        "thermal": bus.thermal.status,
        "propulsion": bus.propulsion.status,
        "cdh": bus.cdh.status,
        "comms": bus.comms.status,
        "battery_soc": bus.power.battery_soc,
        "storage_frac": bus.cdh.storage_frac,
        "safe_mode_active": bus.safe_mode.active,
        "safe_mode_entered_at": bus.safe_mode.entered_at,
    }


def refresh_ground_view(bus: BusState, now: int) -> None:
    """A contact (pass/ISL) delivers fresh telemetry: snapshot truth into the ground view."""
    bus.ground_view = soh_snapshot(bus)
    bus.last_telemetry_time = now


def bus_view(bus: BusState, ops_fidelity: str = "realistic") -> dict:
    """What the operator UI shows, scaled by the vignette's ops_fidelity dial."""
    if ops_fidelity == "tactical":
        return {"health": overall_status(bus)}  # collapsed to a single bar
    view = {
        "mode": bus.mode,
        "power": bus.power.status,
        "attitude": bus.attitude.status,
        "thermal": bus.thermal.status,
        "propulsion": bus.propulsion.status,
        "cdh": bus.cdh.status,
        "comms": bus.comms.status,
    }
    if ops_fidelity == "full_ttc":
        view["detail"] = soh_snapshot(bus)
    return view
