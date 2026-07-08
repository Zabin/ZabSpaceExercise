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

from pydantic import BaseModel, Field, model_validator

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
    # FW §11.B.11 — extended thermal model.
    temp_c: float = 20.0                       # current bus temperature (°C)
    temp_low_c: float = -20.0                  # survival-mode trigger when below this
    temp_high_c: float = 40.0                  # survival-mode trigger when above this
    heater_watts: float = 0.0                  # commanded heater power (W)
    radiator_capacity_w: float = 0.0           # heat-shed capacity (W); 0 disables the model
    survival_trigger_minutes: float = 5.0      # how long out-of-band before auto-survival


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
    # FUTURE-WORK §5: per-step recovery deep-links so the recovery strip can highlight progress.
    # Steps are tracked deterministically by the RecoverySystem handlers; the operator can see
    # which step is "current" (next to run) vs "done" or "blocked".
    current_step: str = "establish_contact"  # establish_contact|dump_telemetry|diagnose|patch|re_enable|done|blocked
    steps_done: list[str] = []


# IP-1171 (FR-5170) — typed per-payload-type authoring sub-models, one per the 8 typed payload
# types (satcom/isr_eo/isr_sar/sigint/sda/weather/pnt/mw). Authored defaults for the Vignette
# Creator's authoring surface, distinct from engine/isr.py's BEAM_MODES runtime table (a
# task-time mode selection) — no invented number; every field traces to a cited topic below.
class SatcomParams(BaseModel):
    # R110 §3 (SATCOM bandwidth-by-class subsection): narrowband military UHF tops out near
    # 384 kbit/s (CJCSI 6250.01G); wideband Ka-band HTS reaches the engine's own 16384 kbps clamp
    # ceiling (bus.py CommsState.data_rate_kbps / buscommands.py comms.config_link).
    bandwidth_class: Literal["narrowband", "wideband"] = "narrowband"
    data_rate_kbps_max: float = 384.0


class IsrEoParams(BaseModel):
    # Mirrors engine/isr.py BEAM_MODES["isr_eo"]["stripmap"] (this type's own _DEFAULT_MODE) —
    # R109's EO/SAR stripmap-vs-spotlight trade (Capella X-SAR / TerraSAR-X precedent) already
    # grounds the runtime table these authored defaults echo, rather than re-deriving a second
    # number.
    resolution_m: float = 3.0
    swath_km: float = 30.0


class IsrSarParams(BaseModel):
    # Mirrors engine/isr.py BEAM_MODES["isr_sar"]["stripmap"] — same R109 SAR trade as IsrEoParams.
    resolution_m: float = 3.0
    swath_km: float = 25.0


class SigintParams(BaseModel):
    # Mirrors engine/sigint.py's own BANDS/MODES defaults ("L" band, "track" mode) — R137 §3.5
    # attributes SIGINT's own characterization to R129, not R109; engine/sigint.py's
    # geolocation_error_km() is the live consumer of both fields' real names.
    default_band: str = "L"
    default_mode: str = "track"


class SdaParams(BaseModel):
    # Mirrors engine/isr.py BEAM_MODES["sda"]["nominal"] (this type's own _DEFAULT_MODE).
    resolution_m: float = 500.0
    swath_km: float = 500.0


class WeatherParams(BaseModel):
    # Mirrors engine/isr.py BEAM_MODES["weather"]["conus"] (IP-1170, VERIFIED — R109's GOES-R
    # ABI resolution/revisit grounding). Wired to a real, independently-verified BEAM_MODES entry,
    # not a placeholder — FR-5170's own Postcondition is satisfied for this type.
    resolution_m: float = 1000.0
    swath_km: float = 5000.0


class PntParams(BaseModel):
    # R134 (PNT Warfare): GPS civilian SPS baseline is <=9m/95% horizontal accuracy — the
    # single-digit-to-low-tens-of-meters band pnt.set_integrity's degraded/protected modes scale,
    # not an unrelated invented figure.
    accuracy_m: float = 9.0


class MwParams(BaseModel):
    # Mirrors engine/isr.py BEAM_MODES["mw"]["scan"] (IP-1170, VERIFIED — R109's SBIRS-GEO
    # scan/stare grounding).
    resolution_m: float = 1000.0
    swath_km: float = 20000.0


# Maps PayloadState.type -> (field name, sub-model class) for the 8 typed payload types only;
# space_control and any other type are deliberately left on the untyped `detail` dict.
_TYPED_PARAM_CLASSES: dict[str, type[BaseModel]] = {
    "satcom": SatcomParams,
    "isr_eo": IsrEoParams,
    "isr_sar": IsrSarParams,
    "sigint": SigintParams,
    "sda": SdaParams,
    "weather": WeatherParams,
    "pnt": PntParams,
    "mw": MwParams,
}


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
    deception_active: bool = False            # def.set_deception_mode: USSF SWF Apr 2025 §3.2 passive measure #2
    shutter_closed: bool = False              # isr.shutter_sensor: optics protected from laser dazzle/blinding; blocks collection
    detail: dict = Field(default_factory=dict)

    # IP-1171 (FR-5170) — one Optional typed sub-model field per payload type, populated only
    # when `type` matches; every other field stays None. Mirrors isr.py's own type->params lookup
    # shape without touching that runtime table.
    satcom: Optional[SatcomParams] = None
    isr_eo: Optional[IsrEoParams] = None
    isr_sar: Optional[IsrSarParams] = None
    sigint: Optional[SigintParams] = None
    sda: Optional[SdaParams] = None
    weather: Optional[WeatherParams] = None
    pnt: Optional[PntParams] = None
    mw: Optional[MwParams] = None

    @model_validator(mode="after")
    def _populate_typed_params(self) -> "PayloadState":
        cls = _TYPED_PARAM_CLASSES.get(self.type)
        if cls is not None and getattr(self, self.type) is None:
            setattr(self, self.type, cls())
        return self


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


def advance_bus(bus: BusState, payload: Optional[PayloadState], now: int, sunlit: float,
                space_weather: str = "none") -> None:
    """Evolve the bus over the elapsed sim time: battery charge/drain and ISR storage fill.

    Pure function of (state, time, lighting, environment) — deterministic and replay-safe.
    ``sunlit`` is the *lit fraction* in [0, 1] supplied by the caller (orbit geometry + Sun
    direction in busmodel.py). A ``bool`` is also accepted (True→1.0, False→0.0) for the unit
    tests and legacy callers. A tick that straddles the terminator blends charge and drain by
    the lit fraction rather than binary-switching — so the battery curve ramps smoothly through
    penumbra instead of stepping off a cliff (audit Jun 2026 §TT&C FIX 2; FW §11.B.10).
    ``space_weather`` ∈ {"none", "minor", "severe"} scales eclipse drain (FUTURE-WORK §10.C.11).
    """
    dt = max(0.0, (now - bus.last_update) / 1_000_000)
    lit = max(0.0, min(1.0, float(sunlit)))
    bus.power.in_eclipse = lit < 0.5
    storm_mult = {"none": 1.0, "minor": 1.3, "severe": 2.0}.get(space_weather, 1.0)
    drain = bus.power.drain_rate_per_s * (0.4 if bus.power.loads_shed else 1.0) * storm_mult
    charge = bus.power.charge_rate_per_s * {"fast": 1.5, "trickle": 0.5}.get(bus.power.charge_mode, 1.0)
    # Blend by lit fraction: full sun charges, full umbra drains, penumbra is a weighted mix.
    delta = (charge * lit - drain * (1.0 - lit)) * dt
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
        "in_eclipse": bus.power.in_eclipse,
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
