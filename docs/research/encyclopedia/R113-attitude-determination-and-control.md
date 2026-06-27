# R113 — Attitude Determination and Control

> **Document ID:** R113
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R103](R103-satellite-command-and-control.md)
> **Referenced By:** [R109](R109-sensor-operations.md), [R111](R111-power-and-thermal-operations.md), FS-105
> **Produces:** implementation constraints for [`engine/bus.py`](../../../spacesim/engine/bus.py) (`AttitudeState`), [`engine/buscommands.py`](../../../spacesim/engine/buscommands.py) (`adcs.*`)
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R103](R103-satellite-command-and-control.md) (Satellite C2), [R109](R109-sensor-operations.md) (Sensor Operations — pointing for collection), [R111](R111-power-and-thermal-operations.md)
> (Power and Thermal — the ADCS/array-illumination coupling not yet modeled)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 1

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

ADCS is currently the simulator's lightest-weight bus subsystem — a mode flag and a pointing-ok
boolean rather than a full pointing/slew-time model — and this topic exists so an implementer
extending it knows exactly what is and isn't modeled before assuming richer pointing physics exist.

## 2. Scope

Covers: the `AttitudeState` mode/pointing-ok model, safe-mode-driven attitude state, and the
desaturation verb's no-op-vs-real-momentum distinction. Does **not** cover: the C2 chain ADCS
commands flow through ([R103](R103-satellite-command-and-control.md)), sensor pointing geometry itself ([R109](R109-sensor-operations.md)), or the
unmodeled power/illumination coupling's eventual implementation ([R111](R111-power-and-thermal-operations.md)).

## 3. Concepts

**Attitude state is a mode enum, not a quaternion/pointing-vector model.** `AttitudeState` carries
only `mode` (`nominal`/`slew`/`safe`) and `pointing_ok: bool` — there is no actual attitude
quaternion, slew-rate, or target-pointing-vector state in the engine today. `adcs.point_payload`
sets `mode="slew"` and records a `target` string in the command's outcome label; it does not
compute or store an actual pointing geometry.

**Safe mode forces attitude into `safe`, not the reverse.** `enter_safe_mode`/`recompute_status` set
`bus.attitude.mode = "safe"` whenever the bus is safed — attitude state is *driven by* overall bus
mode for safety, not an independent fault path that can itself trigger safing in the current model.

**Desaturation is a no-op restoration, not a momentum-budget simulation.** `adcs.desaturate`
restores `mode="nominal"`/`pointing_ok=True`/`status="green"` if the bus is nominal — there is no
modeled reaction-wheel momentum buildup that desaturation actually drains. In real ADCS, reaction
wheels accumulate angular momentum from external torques (solar pressure, gravity gradient) and
periodically require a momentum-unload/desaturation maneuver (commonly via magnetic torquers for
small Earth-orbiting spacecraft) to return wheel speeds to a usable range
([NASA, *5.0 Guidance, Navigation, and Control*, Small Spacecraft Technology State of the Art](https://www.nasa.gov/smallsat-institute/sst-soa/guidance-navigation-and-control/)
([Wayback](https://web.archive.org/web/2026/https://www.nasa.gov/smallsat-institute/sst-soa/guidance-navigation-and-control/))) —
the verb exists here as an operator action with an observable telemetry effect, not a
physically-derived momentum model.

**Pointing-payload coupling to array illumination is explicitly not modeled.** [R101](R101-orbital-mechanics-for-operations.md) §7 and [R111](R111-power-and-thermal-operations.md) §6
both flag that ADCS pointing affecting solar-array illumination (and therefore charge rate) is a
real coupling the engine does not yet implement — a future feature should not assume pointing mode
changes today's power balance.

### Sources

- *NASA, 5.0 Guidance, Navigation, and Control, Small Spacecraft Technology State of the Art* — [live](https://www.nasa.gov/smallsat-institute/sst-soa/guidance-navigation-and-control/)
  · [snapshot](https://web.archive.org/web/2026/https://www.nasa.gov/smallsat-institute/sst-soa/guidance-navigation-and-control/)
  · accessed 2026-06-27.

## 4. Operational Context

Real ADCS is one of the more physically dense bus subsystems — reaction wheels, momentum budgets,
slew-time/settling constraints, and a direct coupling between attitude and both payload pointing and
solar-array illumination. The simulator's deliberately thin model (mode + boolean) keeps the v1
scope bounded while still letting ADCS gate payload availability and show up as a distinct SOH
status the operator must manage.

## 5. Implementation Guidance

- **Don't assume a quaternion or slew-rate state exists** — any feature reading "current pointing
  direction" with precision beyond the `mode` enum is reading state the engine doesn't have; treat
  adding real pointing geometry as its own scoped Implementation Package.
- **A new ADCS verb should still flow through `apply_command`'s `(success, label)` contract**, like
  the existing `adcs.set_mode`/`adcs.desaturate`/`adcs.point_payload` verbs, not bypass it.
- **If you implement the ADCS↔array-illumination coupling ([R111](R111-power-and-thermal-operations.md) §6/[R101](R101-orbital-mechanics-for-operations.md) §7's flagged gap)**, scope
  it as a documented Implementation Package that ties `AttitudeState.mode` into `advance_bus`'s
  `sunlit` input — don't quietly bolt it onto an unrelated power-model change.
- **Treat `pointing_ok=False` as the gate other systems should read** (e.g. for payload
  availability), not the `mode` string directly, since `mode` values may grow over time.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer — any pointing-related UI must be honest that
today's ADCS model is mode-level, not vector-level.

## 7. Related Topics

[R103](R103-satellite-command-and-control.md) (the C2 chain ADCS commands flow through), [R109](R109-sensor-operations.md) (sensor pointing for collection, currently
modeled via `look_angle_deg` independent of bus attitude state), [R111](R111-power-and-thermal-operations.md) §6 (the unmodeled
pointing/illumination coupling).
