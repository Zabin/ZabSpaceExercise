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
             "comms.enable_isl", "comms.config_link",
             "prop.cancel_burn", "prop.collision_avoid", "prop.station_keep"}
# Audit 2026-06 Commands §M1 / Phase D — cut: isr.assess_quality, isr.calibrate (NIIRS is
# computed by ground processing; realism §2), sigint.set_band / sigint.geolocate /
# sigint.downlink (folded into sigint.task_collection + the downlink action), sda.cue /
# sda.downlink / wx.downlink (no consumer; covered by the downlink action), satcom.
# report_interference / satcom.set_transponder (no consumer; cosmetic),
# mw.set_sensor_mode / mw.report_alerts (broken-loop + replaced by mw.add_stare_area
# from realism §7). Comms cuts: comms.point_antenna / comms.set_crypto (no consumer or
# model). Added: mw.add_stare_area, satcom.geolocate_interference, wx.request_sector,
# prop.station_keep, isr.shutter_sensor from realism research §15 (§N8 closed).
PAYLOAD_VERBS = {"satcom.mitigate_interference", "satcom.shift_users",
                 "satcom.reconfigure_beam", "satcom.set_frequency_plan",
                 "satcom.geolocate_interference",
                 "satcom.null_steer",
                 "isr.collect_now", "isr.schedule_collection", "isr.set_mode",
                 "isr.prioritize_downlink",
                 "sigint.task_collection",
                 "sda.task_search", "sda.task_track", "sda.task_characterize",
                 "wx.schedule_collection", "wx.request_sector",
                 "pnt.set_integrity", "pnt.report_status",
                 "pnt.flex_power", "pnt.set_health_flag",
                 "mw.add_stare_area",
                 "isr.shutter_sensor"}
DEFENSE_VERBS = {"def.patch_cyber", "def.frequency_hop", "def.harden", "def.set_threat_warning",
                 "def.maneuver_evade", "def.escort_posture", "def.disperse",
                 "def.set_deception_mode"}
COMMAND_VERBS = BUS_VERBS | PAYLOAD_VERBS | DEFENSE_VERBS

# Payload verbs are valid only on a payload of a matching mission type (FR-B2: the bus/payload fit).
_PAYLOAD_TYPES_FOR = {
    "satcom.mitigate_interference": {"satcom"}, "satcom.shift_users": {"satcom"},
    "satcom.reconfigure_beam": {"satcom"}, "satcom.set_frequency_plan": {"satcom"},
    "satcom.geolocate_interference": {"satcom"},
    "satcom.null_steer": {"satcom"},
    "isr.collect_now": {"isr_eo", "isr_sar"}, "isr.schedule_collection": {"isr_eo", "isr_sar"},
    "isr.set_mode": {"isr_eo", "isr_sar"},
    "isr.prioritize_downlink": {"isr_eo", "isr_sar"},
    "isr.shutter_sensor": {"isr_eo", "isr_sar"},
    "sigint.task_collection": {"sigint"},
    "sda.task_search": {"sda"}, "sda.task_track": {"sda"}, "sda.task_characterize": {"sda"},
    "wx.schedule_collection": {"weather"}, "wx.request_sector": {"weather"},
    "pnt.set_integrity": {"pnt"}, "pnt.report_status": {"pnt"},
    "pnt.flex_power": {"pnt"}, "pnt.set_health_flag": {"pnt"},
    "mw.add_stare_area": {"mw"},
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
        if a.payload_state.shutter_closed:
            return False, "shuttered"           # optics protected from dazzle/blinding — can't collect
        if bus is not None and not can_collect(bus):
            return False, "cannot_collect"      # safed / power-red / storage full (bus gates payload)
        a.payload_state.collecting = True        # fills onboard storage over the coming steps
        return True, "collecting"

    if verb == "isr.shutter_sensor":
        # Closes the optical shutter against laser dazzle/blinding (docs/AUDIT-2026-06-COMMANDS.md
        # §N8); while shut the sensor cannot collect, so an open shutter is required first.
        p = a.payload_state
        if p is None:
            return False, "no_payload"
        p.shutter_closed = bool(params.get("on", True))
        if p.shutter_closed:
            p.collecting = False
        return True, "shutter_closed" if p.shutter_closed else "shutter_open"

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
        # Legacy verb retained for save-file back-compat (Audit 2026-06 Commands §M3).
        # New scenarios should use pnt.flex_power / pnt.set_health_flag, which model
        # the two real PNT operator actions; this verb just records the requested mode.
        p = a.payload_state
        if p is None:
            return False, "no_payload"
        mode = params.get("mode", "standard")
        if mode not in _INTEGRITY_MODES:
            mode = "standard"
        p.integrity_mode = mode
        return True, f"integrity_{mode}"

    if verb == "pnt.flex_power":
        # IS-GPS-200E flex power: MCS reallocates SV transmit power between P(Y) and
        # M-code to raise mil-signal power in jamming environments. Block IIIF adds
        # Regional Military Protection (regional M-code spot beam).
        # Realism research §6 / docs/research/05-mission-types-and-counters.md §4.
        p = a.payload_state
        if p is None:
            return False, "no_payload"
        on = bool(params.get("on", True))
        signal = params.get("signal", "M-code")
        if signal not in ("M-code", "PY"):
            signal = "M-code"
        p.detail["flex_power_on"] = on
        p.detail["flex_power_signal"] = signal
        if "region" in params and params["region"]:
            p.detail["flex_power_region"] = params["region"]
        # The protective effect is encoded as integrity_mode so the existing telemetry /
        # objective surface (which already reads integrity_mode for spoof-resistance
        # tests) sees the operator's action without growing the typed model.
        p.integrity_mode = "protected" if on else "standard"
        return True, "flex_power_on" if on else "flex_power_off"

    if verb == "pnt.set_health_flag":
        # 2 SOPS MCS sets an SV health flag and broadcasts the change to users via NANU.
        # Healthy=False simulates marking the SV unusable until the operator restores it.
        p = a.payload_state
        if p is None:
            return False, "no_payload"
        healthy = bool(params.get("healthy", True))
        sv_id = params.get("sv_id", actor_id)
        p.detail["sv_healthy"] = healthy
        # NANU-style consequence so AAR and White-Cell can see the broadcast.
        world.consequences.append({"t": now, "type": "nanu", "actor": actor_id,
                                    "sv_id": sv_id, "healthy": healthy})
        # Health flag affects users' integrity perception.
        p.integrity_mode = "standard" if healthy else "degraded"
        return True, "sv_healthy" if healthy else "sv_unhealthy"

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

    if verb == "isr.prioritize_downlink":
        if a.payload_state is None: return False, "no_payload"
        a.payload_state.detail["downlink_priority"] = params.get("priority", "high")
        return True, "downlink_prioritized"

    if verb == "pnt.report_status":
        if a.payload_state is None: return False, "no_payload"
        mode = a.payload_state.integrity_mode
        a.payload_state.detail["last_status_report"] = mode
        return True, f"status_{mode}"

    if verb == "satcom.geolocate_interference":
        # Realism research §5 — the WGS MAJE / commercial interference-geolocation function.
        # Detects, identifies, and geolocates an in-band interferer. Records the report as
        # a consequence so AAR / White-Cell / friendly cells can see the geolocation cue.
        p = a.payload_state
        if p is None:
            return False, "no_payload"
        lvl = float(p.interference_level)
        if lvl <= 0.05:
            return False, "no_interference_detected"
        # Geolocation precision (CEP km) scales with dwell time; reasonable defaults.
        dwell_s = float(params.get("dwell_s", 600.0))
        cep_km = round(50.0 / max(1.0, dwell_s / 600.0), 1)
        p.detail["last_interference_geoloc_cep_km"] = cep_km
        world.consequences.append({
            "t": now, "type": "interference_geoloc", "actor": actor_id,
            "interference_level": lvl, "cep_km": cep_km,
        })
        return True, f"geolocated_cep_{cep_km}km"

    if verb == "wx.request_sector":
        # Realism research §8 — GOES-R mesoscale domain sector (MDS) request. Forecaster
        # picks an AOI center + cadence; the payload images that box at the requested rate.
        p = a.payload_state
        if p is None:
            return False, "no_payload"
        if bus is not None and not can_collect(bus):
            return False, "cannot_collect"
        center = params.get("center") or [0.0, 0.0]
        cadence_s = int(params.get("cadence_s", 60))
        if cadence_s not in (30, 60):
            cadence_s = 60
        p.detail["mds_center"] = list(center)
        p.detail["mds_cadence_s"] = cadence_s
        p.collecting = True
        return True, f"sector_{cadence_s}s"

    if verb == "mw.add_stare_area":
        # Realism research §7 — SBIRS step-stare tasking: operator adds an AOI to the
        # starer's revisit list. The scanner keeps doing full-disk strategic warning.
        p = a.payload_state
        if p is None:
            return False, "no_payload"
        center = params.get("center") or [0.0, 0.0]
        revisit_s = int(params.get("revisit_s", 30))
        areas = list(p.detail.get("mw_stare_areas", []))
        areas.append({"center": list(center), "revisit_s": revisit_s})
        p.detail["mw_stare_areas"] = areas
        return True, f"stare_area_added_{revisit_s}s"

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

    if verb == "prop.station_keep":
        # Routine drift-correction burn (ITU-R S.484-3 geostationary station-keeping
        # geometry; docs/research/06-bus-and-payload-operations.md §6.5). Unlike
        # prop.collision_avoid this is the periodic maintenance burn every bus performs
        # — no conjunction precondition.
        dv_cost = float(params.get("dv_cost", 0.5))
        if a.resources.delta_v_ms < dv_cost - 1e-9:
            return False, "insufficient_delta_v"
        a.resources.delta_v_ms -= dv_cost
        return True, "station_kept"

    if verb == "adcs.point_payload":
        if bus is None: return False, "no_bus"
        bus.attitude.mode = "slew"            # off-nominal slew toward a target
        bus.attitude.pointing_ok = True
        target = params.get("target", "?")
        return True, f"pointing_at_{target}"

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

    if verb == "satcom.reconfigure_beam":
        if a.payload_state is None: return False, "no_payload"
        spot = params.get("spot", "default")
        a.payload_state.detail["beam"] = spot
        return True, f"beam_{spot}"

    if verb == "def.disperse":
        # Constellation dispersal posture — flag so the operator console (and AAR) can show it.
        a.threat_warning = True
        a.payload_state and a.payload_state.detail.update({"dispersal": True})
        world.consequences.append({"t": now, "type": "disperse", "actor": actor_id})
        return True, "dispersing"

    if verb == "def.set_deception_mode":
        # Military deception — passive defense #2 in the USSF Space Warfighting
        # Framework (10 Apr 2025) seven-measure menu, documented in
        # docs/research/01-doctrine-western.md §4.  Surfaces as a payload-side
        # posture flag observable in telemetry; the downstream effect-resolver
        # change (which would lower adversary custody confidence + raise
        # attribution ambiguity) is left as a separate change.
        if a.payload_state is None:
            return False, "no_payload"
        a.payload_state.deception_active = bool(params.get("on", True))
        return True, "deception_on" if a.payload_state.deception_active else "deception_off"

    if verb == "satcom.null_steer":
        # Adaptive beam-nulling against a named jammer.  USPTO 12,537,566
        # (cited in docs/research/06-bus-and-payload-operations.md §5.5):
        # "the number of undesirable sources that can be nulled equals one
        # less than the number of digital receivers".  Distinct from
        # satcom.mitigate_interference (broad anti-jam): null-steer is
        # angle-specific, target-named, and has a hard N-1 cap.
        p = a.payload_state
        if p is None:
            return False, "no_payload"
        target = params.get("target")
        if not target:
            return False, "no_target"
        n_rx = int(params.get("receiver_count", 4))
        cap = max(0, n_rx - 1)
        targets = list(p.detail.get("null_targets", []))
        if target in targets:
            return True, f"nulled_{target}"   # idempotent
        if len(targets) >= cap:
            return False, "null_cap_reached"
        targets.append(target)
        p.detail["null_targets"] = targets
        return True, f"nulled_{target}"

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
