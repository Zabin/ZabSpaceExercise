"""Bus & payload command verbs — a first real, deterministic batch (``13-operator-command-catalog.md``).

Each verb mutates the asset's ``BusState``/``PayloadState`` **inside the deterministic event loop**
(via the ``execute_command`` handler in ``orders.py``), so it is replay-safe and its effect shows up
in the pass-gated SOH and the read-time telemetry signatures — exactly the loop the operator console
drives. Only verbs with a faithful, observable effect in the current bus/payload model are
implemented here; the rest of the catalog is future work behind the same ``apply_command`` dispatch.

Verbs (this batch):
  bus:     eps.shed_load / eps.restore_load (power load management), adcs.set_mode (pointing mode)
  payload: satcom.mitigate_interference / satcom.shift_users (anti-jam — shrinks the jam signature)
"""

from __future__ import annotations

from spacesim.engine.bus import can_collect, payload_available, recompute_status, refresh_ground_view

BUS_VERBS = {"eps.shed_load", "eps.restore_load", "eps.set_charge_mode",
             "adcs.set_mode", "adcs.desaturate",
             "cdh.dump_storage", "cdh.clear_fault", "cdh.reset_subsystem",
             "tcs.set_mode", "tcs.set_heater",
             "comms.enable_isl", "comms.config_link", "comms.point_antenna"}
PAYLOAD_VERBS = {"satcom.mitigate_interference", "satcom.shift_users",
                 "isr.collect_now", "isr.schedule_collection", "isr.set_mode",
                 "sigint.task_collection", "wx.schedule_collection",
                 "pnt.set_integrity"}
DEFENSE_VERBS = {"def.patch_cyber", "def.frequency_hop", "def.harden", "def.set_threat_warning",
                 "def.maneuver_evade"}
COMMAND_VERBS = BUS_VERBS | PAYLOAD_VERBS | DEFENSE_VERBS

# Payload verbs are valid only on a payload of a matching mission type (FR-B2: the bus/payload fit).
_PAYLOAD_TYPES_FOR = {
    "satcom.mitigate_interference": {"satcom"}, "satcom.shift_users": {"satcom"},
    "isr.collect_now": {"isr_eo", "isr_sar"}, "isr.schedule_collection": {"isr_eo", "isr_sar"},
    "isr.set_mode": {"isr_eo", "isr_sar"},
    "sigint.task_collection": {"sigint"},
    "wx.schedule_collection": {"weather"},
    "pnt.set_integrity": {"pnt"},
}

_ISR_MODES = ("wide", "narrow", "standby", "nominal")
_ANTENNA_MODES = ("nominal", "earth", "zenith", "tracking")
_INTEGRITY_MODES = ("standard", "protected", "degraded")

_ATTITUDE_MODES = ("nominal", "slew", "safe")
_CHARGE_MODES = ("nominal", "fast", "trickle")
_THERMAL_MODES = ("nominal", "survival", "operational")


def is_payload_verb(verb: str) -> bool:
    return verb in PAYLOAD_VERBS


def apply_command(world, actor_id: str, verb: str, params: dict, now: int) -> tuple[bool, str]:
    """Apply a bus/payload command to the asset, returning (success, physical-outcome label).

    Re-validates at execution (the asset may have been lost / safed since planning). Returns a
    *physical* outcome label only — never a cause/verdict — consistent with the symptoms-not-verdicts
    rule the telemetry layer follows.
    """
    a = world.assets.get(actor_id)
    if a is None or getattr(a, "health", "nominal") == "destroyed":
        return False, "lost"
    bus = a.bus_state

    if verb == "eps.shed_load":
        if bus is None:
            return False, "no_bus"
        bus.power.loads_shed = True
        if a.payload_state is not None:
            a.payload_state.collecting = False   # shedding non-critical loads stands the payload down
        recompute_status(bus)
        return True, "loads_shed"

    if verb == "eps.restore_load":
        if bus is None:
            return False, "no_bus"
        bus.power.loads_shed = False
        recompute_status(bus)
        return True, "loads_restored"

    if verb == "eps.set_charge_mode":
        if bus is None:
            return False, "no_bus"
        mode = params.get("mode", "nominal")
        if mode not in _CHARGE_MODES:
            mode = "nominal"
        bus.power.charge_mode = mode
        return True, f"charge_{mode}"

    if verb == "adcs.set_mode":
        if bus is None:
            return False, "no_bus"
        mode = params.get("mode", "nominal")
        if mode not in _ATTITUDE_MODES:
            mode = "nominal"
        bus.attitude.mode = mode
        bus.attitude.pointing_ok = mode != "safe"
        return True, f"mode_{mode}"

    if verb == "cdh.dump_storage":
        if bus is None:
            return False, "no_bus"
        refresh_ground_view(bus, now)   # recover out-of-contact history: fresh SOH snapshot to the ground
        return True, "telemetry_dumped"

    if verb in ("satcom.mitigate_interference", "satcom.shift_users"):
        p = a.payload_state
        if p is None:
            return False, "no_payload"
        # Each application buys more anti-jam margin, capped — the jam signature shrinks but never vanishes.
        p.interference_mitigation = min(0.8, p.interference_mitigation + 0.4)
        return True, "interference_mitigated"

    if verb in ("isr.collect_now", "isr.schedule_collection"):
        if a.payload_state is None:
            return False, "no_payload"
        if bus is not None and not can_collect(bus):
            return False, "cannot_collect"      # safed / power-red / storage full (bus gates payload)
        a.payload_state.collecting = True        # fills onboard storage over the coming steps
        return True, "collecting"

    if verb == "def.patch_cyber":
        # Defender removes a cyber root cause: patch the matching vulnerability so recovery sticks.
        vector = params.get("vector")
        for v in getattr(a, "cyber_vulnerabilities", []):
            if vector is None or v.get("vector") == vector:
                v["patched"] = True
        return True, "patched"

    if verb == "cdh.clear_fault":
        if bus is None: return False, "no_bus"
        bus.cdh.fsw_mode = "nominal"
        recompute_status(bus)
        return True, "fault_cleared"

    if verb == "tcs.set_mode":
        if bus is None: return False, "no_bus"
        mode = params.get("mode", "operational")
        if mode not in _THERMAL_MODES: mode = "operational"
        bus.thermal.mode = mode
        return True, f"thermal_{mode}"

    if verb == "tcs.set_heater":
        if bus is None: return False, "no_bus"
        bus.thermal.heater_on = bool(params.get("on", True))
        return True, "heater_on" if bus.thermal.heater_on else "heater_off"

    if verb == "comms.enable_isl":
        if bus is None: return False, "no_bus"
        bus.comms.isl_enabled = bool(params.get("on", True))
        return True, "isl_enabled" if bus.comms.isl_enabled else "isl_disabled"

    if verb == "comms.config_link":
        if bus is None: return False, "no_bus"
        rate = int(params.get("data_rate_kbps", bus.comms.data_rate_kbps))
        bus.comms.data_rate_kbps = max(64, min(rate, 16384))
        return True, f"link_{bus.comms.data_rate_kbps}kbps"

    if verb == "def.frequency_hop":
        if bus is None: return False, "no_bus"
        bus.comms.freq_hopping = bool(params.get("on", True))
        return True, "freq_hopping_on" if bus.comms.freq_hopping else "freq_hopping_off"

    if verb == "def.harden":
        if a.payload_state is None: return False, "no_payload"
        a.payload_state.hardened = bool(params.get("on", True))
        return True, "hardened" if a.payload_state.hardened else "unhardened"

    if verb == "def.set_threat_warning":
        a.threat_warning = bool(params.get("on", True))     # informational posture (no engine gate)
        return True, "threat_warning_on" if a.threat_warning else "threat_warning_off"

    if verb == "cdh.reset_subsystem":
        if bus is None:
            return False, "no_bus"
        # Full subsystem reboot: exit fault state, restore attitude, recompute.
        bus.cdh.fsw_mode = "nominal"
        if bus.mode == "nominal":   # don't clear safe mode — that requires the recovery chain
            bus.attitude.mode = "nominal"
            bus.attitude.pointing_ok = True
        recompute_status(bus)
        return True, "subsystem_reset"

    if verb == "adcs.desaturate":
        if bus is None:
            return False, "no_bus"
        # Momentum-wheel desaturation: restore nominal pointing if not in safe mode.
        if bus.mode == "nominal":
            bus.attitude.mode = "nominal"
            bus.attitude.pointing_ok = True
            bus.attitude.status = "green"
        return True, "desaturated"

    if verb == "comms.point_antenna":
        if bus is None:
            return False, "no_bus"
        mode = params.get("mode", "nominal")
        if mode not in _ANTENNA_MODES:
            mode = "nominal"
        bus.comms.antenna_mode = mode
        return True, f"antenna_{mode}"

    if verb == "isr.set_mode":
        p = a.payload_state
        if p is None:
            return False, "no_payload"
        mode = params.get("mode", "nominal")
        if mode not in _ISR_MODES:
            mode = "nominal"
        p.mode = mode
        if mode == "standby":
            p.collecting = False
        return True, f"isr_mode_{mode}"

    if verb == "pnt.set_integrity":
        p = a.payload_state
        if p is None:
            return False, "no_payload"
        mode = params.get("mode", "standard")
        if mode not in _INTEGRITY_MODES:
            mode = "standard"
        p.integrity_mode = mode
        return True, f"integrity_{mode}"

    if verb == "def.maneuver_evade":
        dv_cost = float(params.get("dv_cost", 5.0))
        if a.resources.delta_v_ms < dv_cost - 1e-9:
            return False, "insufficient_delta_v"
        a.resources.delta_v_ms -= dv_cost
        if a.payload_state is not None:
            a.payload_state.evasion_active = True
        return True, "evasion_burn_executed"

    if verb == "sigint.task_collection":
        if a.payload_state is None: return False, "no_payload"
        a.payload_state.collecting = True
        return True, "tasked"

    if verb == "wx.schedule_collection":
        if a.payload_state is None: return False, "no_payload"
        if bus is not None and not can_collect(bus): return False, "cannot_collect"
        a.payload_state.collecting = True
        return True, "scheduled"

    return False, "unknown"


def can_issue(world, actor_id: str, verb: str) -> tuple[bool, str]:
    """Plan-time check used by the order validator: is this verb legal for this asset right now?"""
    if verb not in COMMAND_VERBS:
        return False, "unknown_command"
    a = world.assets.get(actor_id)
    if a is None:
        return False, "no_such_asset"
    if is_payload_verb(verb):
        need = _PAYLOAD_TYPES_FOR.get(verb)
        if a.payload_state is None or (need is not None and a.payload_state.type not in need):
            return False, "no_payload_for_verb"
        if a.bus_state is not None and not payload_available(a.bus_state):
            return False, "payload_unavailable"   # the bus gates the payload (safe mode / power-red)
    if verb == "def.maneuver_evade":
        min_dv = 1.0  # minimum Δv for an evasion burn (m/s)
        if a.resources.delta_v_ms < min_dv:
            return False, "insufficient_delta_v"
    return True, ""
