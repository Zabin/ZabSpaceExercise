# R114 — Command and Data Handling

> **Document ID:** R114
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R103](R103-satellite-command-and-control.md)
> **Referenced By:** [R109](R109-sensor-operations.md), FS-105
> **Produces:** implementation constraints for [`engine/bus.py`](../../../spacesim/engine/bus.py) (`CdhState`), [`engine/buscommands.py`](../../../spacesim/engine/buscommands.py) (`cdh.*`)
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R103](R103-satellite-command-and-control.md) (Satellite C2 — the stored-delivery/dump counterpart), [R111](R111-power-and-thermal-operations.md) (Power and
> Thermal Operations), [R109](R109-sensor-operations.md) (Sensor Operations — the storage that collection fills)

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Command and Data Handling (C&DH) is the onboard-storage gate that ties collection ([R109](R109-sensor-operations.md)) to
downlink ([R103](R103-satellite-command-and-control.md)) — a satellite that fills its storage buffer cannot collect further until a downlink
drains it. This topic gives the implementer the `CdhState` model so new collection or downlink
features respect the storage gate consistently.

## 2. Concepts

**Storage fill is a fraction with soft/hard thresholds, exactly like SoC.** `CdhState.storage_frac`
is limit-checked with `status_high(value, STORAGE_SOFT=0.85, STORAGE_HARD=0.98)` — unlike SoC
(healthy when high), storage is healthy when *low*; `status_high` exists specifically for this
inverted-sense quantity, paralleling `status_low` for power/propellant.

**Storage gates further collection, not just a display warning.** `can_collect(bus)` requires
`payload_available(bus) and bus.cdh.storage_frac < 1.0` — a full buffer is a hard stop on new
collection regardless of payload health, mirrored in `buscommands.apply_command`'s
`"cannot_collect"` rejection for `isr.collect_now`/`wx.schedule_collection`.

**Only a downlink (or `cdh.dump_storage`) drains storage.** `downlink_storage(bus, fraction)` is
called from `OrderSystem._h_downlink` on a successful, non-jammed downlink, scaled by the
`partial_dump` fraction if specified — `cdh.dump_storage` itself does *not* drain storage; it only
calls `refresh_ground_view` to recover a fresh telemetry snapshot after an out-of-contact period.
Don't conflate "dump telemetry" (an SOH-visibility verb) with "dump storage" (a downlink action).

**`fsw_mode` is the flight-software fault flag distinct from bus-wide safe mode.** `cdh.fsw_mode`
(`nominal`/`safe`) is set to `safe` by `enter_safe_mode` but can also be cleared independently via
`cdh.clear_fault`/`cdh.reset_subsystem` — a subsystem-level fault recovery path distinct from the
multi-pass `RecoverySystem` safe-mode chain ([R106](R106-mission-operations.md)-adjacent), useful for transient FSW faults that
don't require the full recovery sequence.

## 3. Operational Context

Real onboard storage is a hard, physical limit — a satellite genuinely cannot collect more data
than its recorder can hold, and operators plan downlink cadence specifically to keep ahead of
collection fill rate. The storage-gates-collection rule and the `partial_dump`/`bitrate_cap_kbps`
downlink parameters exist to make that real planning trade-off (collect vs. downlink cadence) felt
rather than abstracted away.

## 4. Implementation Guidance

- **A new collection-producing payload type must check `can_collect(bus)` before setting
  `collecting=True`**, exactly as `isr.collect_now`/`wx.schedule_collection`/`sigint.task_collection`
  already do — skipping this check lets storage silently exceed 1.0.
- **Only `downlink_storage` (via a successful downlink) should reduce `storage_frac`** — a new
  "clear storage" verb that isn't a downlink misrepresents the physical model; if a genuine
  non-downlink storage-clear is needed (e.g. an onboard purge), document it explicitly as a new,
  named physical capability rather than reusing the downlink semantics.
- **Don't confuse `cdh.dump_storage` (telemetry SOH refresh) with a downlink action** — they serve
  different purposes and a feature needing "recover visibility after an outage" wants the former,
  not the latter.
- **`fsw_mode` fault-clear verbs should stay distinct from the safe-mode recovery chain** — a
  feature needing to model a graver onboard fault should use `enter_safe_mode`/`RecoverySystem`,
  not extend `cdh.clear_fault`'s lighter-weight semantics to cover full safing.

## 5. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer — any new collection or downlink feature must
visibly respect the storage gate in the operator console.

## 6. Related Topics

[R103](R103-satellite-command-and-control.md) (the downlink delivery path C&DH gates), [R109](R109-sensor-operations.md) (the collection that fills storage), [R111](R111-power-and-thermal-operations.md)
(the broader bus SOH model C&DH's storage limit-checking pattern mirrors).
