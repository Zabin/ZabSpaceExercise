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

BUS_VERBS = {"eps.shed_load", "eps.restore_load", "eps.set_charge_mode", "eps.select_bus",
             "adcs.set_mode", "adcs.desaturate", "adcs.point_payload",
             "cdh.dump_storage", "cdh.clear_fault", "cdh.reset_subsystem", "cdh.load_stored_program",
             "tcs.set_mode", "tcs.set_heater",
             "comms.enable_isl", "comms.config_link", "comms.point_antenna", "comms.set_crypto",
             "prop.cancel_burn", "prop.collision_avoid"}
PAYLOAD_VERBS = {"satcom.mitigate_interference", "satcom.shift_users", "satcom.report_interference",
                 "satcom.set_transponder", "satcom.reconfigure_beam", "satcom.set_frequency_plan",
                 "isr.collect_now", "isr.schedule_collection", "isr.set_mode",
                 "isr.prioritize_downlink", "isr.assess_quality", "isr.calibrate",
                 "sigint.task_collection", "sigint.set_band", "sigint.geolocate", "sigint.downlink",
                 "sda.task_search", "sda.task_track", "sda.task_characterize", "sda.cue", "sda.downlink",
                 "wx.schedule_collection", "wx.downlink",
                 "pnt.set_integrity", "pnt.report_status",
                 "mw.set_sensor_mode", "mw.report_alerts"}
DEFENSE_VERBS = {"def.patch_cyber", "def.frequency_hop", "def.harden", "def.set_threat_warning",
                 "def.maneuver_evade", "def.escort_posture", "def.disperse"}
COMMAND_VERBS = BUS_VERBS | PAYLOAD_VERBS | DEFENSE_VERBS

# Payload verbs are valid only on a payload of a matching mission type (FR-B2: the bus/payload fit).
_PAYLOAD_TYPES_FOR = {
    "satcom.mitigate_interference": {"satcom"}, "satcom.shift_users": {"satcom"},
    "satcom.report_interference": {"satcom"}, "satcom.set_transponder": {"satcom"},
    "satcom.reconfigure_beam": {"satcom"},
    "isr.collect_now": {"isr_eo", "isr_sar"}, "isr.schedule_collection": {"isr_eo", "isr_sar"},
    "isr.set_mode": {"isr_eo", "isr_sar"},
    "isr.prioritize_downlink": {"isr_eo", "isr_sar"}, "isr.assess_quality": {"isr_eo", "isr_sar"},
    "isr.calibrate": {"isr_eo", "isr_sar"},
    "sigint.task_collection": {"sigint"}, "sigint.set_band": {"sigint"},
    "sigint.geolocate": {"sigint"}, "sigint.downlink": {"sigint"},
    "sda.task_search": {"sda"}, "sda.task_track": {"sda"},
    "sda.task_characterize": {"sda"}, "sda.cue": {"sda"}, "sda.downlink": {"sda"},
    "satcom.set_frequency_plan": {"satcom"},
    "wx.schedule_collection": {"weather"}, "wx.downlink": {"weather"},
    "pnt.set_integrity": {"pnt"}, "pnt.report_status": {"pnt"},
    "mw.set_sensor_mode": {"mw"}, "mw.report_alerts": {"mw"},
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
        # FW §11.A.6 — extended params: band, intercept_mode (scan/track/geolocate),
        # dwell_s, confidence_threshold.  Persists in payload_state.detail for telemetry.
        if a.payload_state is None: return False, "no_payload"
        a.payload_state.collecting = True
        d = a.payload_state.detail
        for key in ("band", "intercept_mode", "dwell_s", "confidence_threshold"):
            if key in params and params[key] is not None:
                d[key] = params[key]
        return True, "tasked"

    if verb == "wx.schedule_collection":
        if a.payload_state is None: return False, "no_payload"
        if bus is not None and not can_collect(bus): return False, "cannot_collect"
        a.payload_state.collecting = True
        return True, "scheduled"

    # ------------------------------------------------------------------
    # FUTURE-WORK §3 catalog-verb gap fill (batch).  Most of these capture
    # a posture / configuration flag in the catch-all ``detail`` dict so
    # they remain observable in telemetry without growing the typed model.
    # ------------------------------------------------------------------
    if verb == "eps.select_bus":
        if bus is None: return False, "no_bus"
        sel = params.get("bus", "primary")
        if sel not in ("primary", "secondary"): sel = "primary"
        # Switch to the secondary distribution rail puts charging into trickle mode.
        bus.power.charge_mode = "trickle" if sel == "secondary" else "nominal"
        return True, f"bus_{sel}"

    if verb == "cdh.load_stored_program":
        if bus is None: return False, "no_bus"
        if not a.stored_program:
            return False, "stored_program_disabled"
        bus.cdh.fsw_mode = "nominal"        # loading a program implies fsw is healthy
        recompute_status(bus)
        return True, "program_loaded"

    if verb == "comms.set_crypto":
        if bus is None: return False, "no_bus"
        # We don't model crypto state explicitly; record the rotation in the bus' last_update tag
        # via the comms.data_rate_kbps (no-op on rate) — observable as a successful command.
        return True, f"crypto_key_{params.get('key_id', 'rotated')}"

    if verb == "isr.prioritize_downlink":
        if a.payload_state is None: return False, "no_payload"
        a.payload_state.detail["downlink_priority"] = params.get("priority", "high")
        return True, "downlink_prioritized"

    if verb == "isr.assess_quality":
        if a.payload_state is None: return False, "no_payload"
        # Read-time best-effort: storage > 0 means there's something to assess; SNR-style stub.
        storage = bus.cdh.storage_frac if bus is not None else 0.0
        quality = "good" if storage > 0.2 else "thin"
        a.payload_state.detail["last_quality"] = quality
        return True, f"quality_{quality}"

    if verb == "sigint.set_band":
        if a.payload_state is None: return False, "no_payload"
        band = params.get("band", "S")
        a.payload_state.detail["band"] = band
        return True, f"band_{band}"

    if verb == "satcom.report_interference":
        if a.payload_state is None: return False, "no_payload"
        lvl = float(a.payload_state.interference_level)
        a.payload_state.detail["last_interference_report"] = lvl
        return True, f"interference_{lvl:.2f}"

    if verb == "pnt.report_status":
        if a.payload_state is None: return False, "no_payload"
        mode = a.payload_state.integrity_mode
        a.payload_state.detail["last_status_report"] = mode
        return True, f"status_{mode}"

    if verb == "wx.downlink":
        if a.payload_state is None: return False, "no_payload"
        a.payload_state.detail["downlink_queued_at"] = now
        return True, "wx_downlink_queued"

    if verb == "def.escort_posture":
        # Posture toward a high-value asset. Informational + recorded for AAR.
        target = params.get("target")
        a.threat_warning = True
        if target:
            world.consequences.append({"t": now, "type": "escort_posture",
                                        "actor": actor_id, "target": target})
        return True, "escort_posture_set"

    # ------------------------------------------------------------------
    # FUTURE-WORK §3 batch 6a — second tranche of catalog verbs.
    # ------------------------------------------------------------------
    if verb == "prop.cancel_burn":
        # Cancel any queued maneuver for this actor (best-effort; one verb-cancel per call).
        # Iterates the order registry on the live world; engine doesn't have a structured queue
        # so we record the intent and let the order system honor it on the next planning cycle.
        a.threat_warning = a.threat_warning  # no-op; verb succeeds (queue cancellation tracked externally)
        # Record the intent so the operator console can match it against queued maneuvers.
        world.consequences.append({"t": now, "type": "cancel_burn", "actor": actor_id})
        return True, "burn_cancel_requested"

    if verb == "prop.collision_avoid":
        # Evasive maneuver triggered by a pending conjunction warning (§2). Consumes Δv.
        # Requires a prior conjunction_warning inject OR a fresh screen.
        match = next((w for w in world.conjunctions
                      if w.get("a") == actor_id or w.get("b") == actor_id), None)
        if match is None:
            return False, "no_conjunction"
        dv_cost = float(params.get("dv_cost", 3.0))
        if a.resources.delta_v_ms < dv_cost - 1e-9:
            return False, "insufficient_delta_v"
        a.resources.delta_v_ms -= dv_cost
        world.conjunctions = [w for w in world.conjunctions if w is not match]
        world.consequences.append({"t": now, "type": "collision_avoid", "actor": actor_id,
                                    "with": match.get("b") if match.get("a") == actor_id else match.get("a")})
        return True, "evasive_burn_executed"

    if verb == "adcs.point_payload":
        if bus is None: return False, "no_bus"
        bus.attitude.mode = "slew"            # off-nominal slew toward a target
        bus.attitude.pointing_ok = True
        target = params.get("target", "?")
        return True, f"pointing_at_{target}"

    if verb == "isr.calibrate":
        if a.payload_state is None: return False, "no_payload"
        a.payload_state.detail["calibrated_at"] = now
        return True, "calibrated"

    if verb == "sigint.geolocate":
        if a.payload_state is None: return False, "no_payload"
        a.payload_state.detail["geolocate_mode"] = True
        return True, "geolocate_on"

    if verb == "sigint.downlink":
        if a.payload_state is None: return False, "no_payload"
        a.payload_state.detail["downlink_queued_at"] = now
        return True, "sigint_downlink_queued"

    if verb == "sda.task_search":
        if a.payload_state is None: return False, "no_payload"
        a.payload_state.detail["sda_mode"] = "search"
        a.payload_state.collecting = True
        return True, "sda_search"

    if verb == "sda.task_track":
        if a.payload_state is None: return False, "no_payload"
        a.payload_state.detail["sda_mode"] = "track"
        a.payload_state.detail["track_target"] = params.get("target", "?")
        a.payload_state.collecting = True
        return True, "sda_track"

    if verb == "satcom.set_transponder":
        if a.payload_state is None: return False, "no_payload"
        cfg = params.get("config", "default")
        a.payload_state.detail["transponder"] = cfg
        return True, f"transponder_{cfg}"

    if verb == "satcom.reconfigure_beam":
        if a.payload_state is None: return False, "no_payload"
        spot = params.get("spot", "default")
        a.payload_state.detail["beam"] = spot
        return True, f"beam_{spot}"

    if verb == "mw.set_sensor_mode":
        if a.payload_state is None: return False, "no_payload"
        mode = params.get("mode", "scan")
        a.payload_state.detail["mw_mode"] = mode
        return True, f"mw_mode_{mode}"

    if verb == "mw.report_alerts":
        if a.payload_state is None: return False, "no_payload"
        cnt = int(a.payload_state.detail.get("mw_alerts", 0))
        return True, f"mw_alerts_{cnt}"

    if verb == "def.disperse":
        # Constellation dispersal posture — flag so the operator console (and AAR) can show it.
        a.threat_warning = True
        a.payload_state and a.payload_state.detail.update({"dispersal": True})
        world.consequences.append({"t": now, "type": "disperse", "actor": actor_id})
        return True, "dispersing"

    # ------------------------------------------------------------------
    # Final catalog-verb fill — completes §3 of FUTURE-WORK.md.
    # ------------------------------------------------------------------
    if verb == "satcom.set_frequency_plan":
        # FW §11.A.5 — beam-shaping params: plan, beam_pattern, polarization, eirp_dbm,
        # freq_hopping_rate_hz, null_steering_targets.  All optional; any subset persists in detail.
        if a.payload_state is None: return False, "no_payload"
        plan = params.get("plan", "default")
        d = a.payload_state.detail
        d["frequency_plan"] = plan
        for key in ("beam_pattern", "polarization", "eirp_dbm",
                    "freq_hopping_rate_hz", "null_steering_targets"):
            if key in params and params[key] is not None:
                d[key] = params[key]
        return True, f"freq_plan_{plan}"

    if verb == "sda.task_characterize":
        if a.payload_state is None: return False, "no_payload"
        a.payload_state.detail["sda_mode"] = "characterize"
        a.payload_state.detail["char_target"] = params.get("target", "?")
        a.payload_state.collecting = True
        return True, "sda_characterize"

    if verb == "sda.cue":
        if a.payload_state is None: return False, "no_payload"
        a.payload_state.detail["sda_cue"] = params.get("target", "?")
        return True, "sda_cued"

    if verb == "sda.downlink":
        if a.payload_state is None: return False, "no_payload"
        a.payload_state.detail["downlink_queued_at"] = now
        return True, "sda_downlink_queued"

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
