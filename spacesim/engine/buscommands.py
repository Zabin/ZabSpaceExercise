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
             "adcs.set_mode", "cdh.dump_storage"}
PAYLOAD_VERBS = {"satcom.mitigate_interference", "satcom.shift_users",
                 "isr.collect_now", "isr.schedule_collection"}
COMMAND_VERBS = BUS_VERBS | PAYLOAD_VERBS

# Payload verbs are valid only on a payload of a matching mission type (FR-B2: the bus/payload fit).
_PAYLOAD_TYPES_FOR = {
    "satcom.mitigate_interference": {"satcom"}, "satcom.shift_users": {"satcom"},
    "isr.collect_now": {"isr_eo", "isr_sar"}, "isr.schedule_collection": {"isr_eo", "isr_sar"},
}

_ATTITUDE_MODES = ("nominal", "slew", "safe")
_CHARGE_MODES = ("nominal", "fast", "trickle")


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
    return True, ""
