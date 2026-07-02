# IP-1050 — Spacecraft Operations: Bus/Payload Command & Telemetry

> **Package ID:** IP-1050
> **Version:** 1.0
> **Status:** ✅ VERIFIED
> **Dependencies:** FS-105 (§3.1), IP-1020 (the `command` action's delivery/window lifecycle)
> **Referenced By:** IP-1051 (sibling package, effect resolution & console UX), [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** the executed-state surface IP-1070 replays and IP-2010 assesses
> **Feature Reference:** [FS-105 — Spacecraft Operations](../../features/FS-105-spacecraft-operations.md) (§3.1, "Bus and subsystem operations")
> **Supersedes:** [`docs/implementations/IMP-105A-spacecraft-operations-bus-payload.md`](../../implementations/IMP-105A-spacecraft-operations-bus-payload.md)
> **Related Topics:** [`spacesim/engine/buscommands.py`](../../../spacesim/engine/buscommands.py), [`spacesim/engine/bus.py`](../../../spacesim/engine/bus.py), [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

## Package ID

IP-1050

## Title

Spacecraft Operations — Bus/Payload Command & Telemetry

## Objective

Implement the full bus/payload command verb catalog (power/attitude/thermal/CDH/comms/prop plus
mission-type-specific payload verbs and defensive verbs), gated at plan-time on payload-type fit and
bus health and re-validated at execution time, so a cell's bus/payload operator training exercises
real subsystem coupling rather than an ungated button list.

FS-105 is split across two lettered packages per the size-discipline precedent this corpus follows
(originally MSTR-006 §4): this package covers §3.1 (bus/payload commands); IP-1051 covers §3.2-4
(the five effect categories and console human-factors requirements).

**Situation: already implemented, tested, in production use.**

## Feature Reference

[FS-105 — Spacecraft Operations](../../features/FS-105-spacecraft-operations.md) §3.1

## Requirements Covered

FS-105's "Requirements Implemented" field reports no explicit FR/NFR citation (documented gap).
Functional coverage per the RTM's `engine/bus.py`/`engine/buscommands.py` mapping:

| Req ID | Title (abridged) | How this package covers it |
|---|---|---|
| FR-2110 | Subsystem SOH modeling with soft/hard limits | `bus.py`'s `recompute_status()`, called after every verb mutation |
| FR-2210 | Payload availability gated by bus health | `can_issue()`'s `payload_available(bus_state)` check (`buscommands.py:524`) |
| FR-2410 | Type-specific operator actions and monitors | `BUS_VERBS`/`PAYLOAD_VERBS`/`DEFENSE_VERBS` partition (`buscommands.py:18-48`) |
| FR-3410 | Execute-time re-validation | `apply_command()` re-validates asset state at execution, not only plan time (`buscommands.py:88`) |
| FR-2510 | Safe-mode entry/diagnosis/recovery (indirect — verbs can trigger/recover safe mode) | `eps.shed_load`, `def.patch_cyber` and related verbs interact with `bus_state.safe_mode` |

## Architecture Components

- **C1 Simulation Engine** — `engine/buscommands.py` (verb catalog, `can_issue`, `apply_command`),
  `engine/bus.py` (`BusState`/`PayloadState` SOH), `engine/orders.py` (`_h_command`).
- **C7/C8 Blue/Red Cell operator** — the console's command issuers.

## Interfaces

**INT-0004** (Blue/Red Cell Operator ↔ Operator Console); **INT-0008** (SessionManager → Simulation
Engine Clock/Scheduler/EventLog/OrderSystem) — per the ICD and FS-105's verified Related Interfaces
field.

## Files to Create

None — capability already implemented.

## Files to Modify

None — this package documents shipped code.

### Reference files

- `spacesim/engine/buscommands.py` — `BUS_VERBS`/`PAYLOAD_VERBS`/`DEFENSE_VERBS`/`COMMAND_VERBS`
  (`:18-48`), `can_issue()` (`:524`), `apply_command()` (`:80`), `_ATTITUDE_MODES` (`:71`).
- `spacesim/engine/bus.py` — `BusState`, `PayloadState`, `recompute_status()`, `ThermalState`.
- `spacesim/engine/orders.py` — `_h_command` (`:688`), `_exec_payload` (`:562-563`).
- `spacesim/engine/telemetry.py` — the read-time SOH/attack-signature telemetry this package's
  mutations surface through (referenced, not modified by this package).

## Implementation Tasks

All **already complete**:

1. ✅ Partition every bus/payload verb into `BUS_VERBS`/`PAYLOAD_VERBS`/`DEFENSE_VERBS`, unioned as
   `COMMAND_VERBS` — the single source of truth both the validator and the handler consult, so the
   console can never offer a verb the engine doesn't recognize.
2. ✅ Implement `can_issue()` as the plan-time gate: unknown verbs rejected, payload verbs checked
   against the asset's actual `payload_state.type` and `payload_available(bus_state)`, `def.
   maneuver_evade` gated on minimum Δv from the shared resource ledger.
3. ✅ Implement `apply_command()` as the execution-time handler, re-validating asset state (the asset
   may have changed since planning) and mutating `BusState`/`PayloadState` fields directly, calling
   `recompute_status()` so SOH reflects the change on the next telemetry read.
4. ✅ Route `command` orders through the `COMMAND_UPLINK` channel with the same stored/ISL delivery
   branching every other order type uses (no bespoke delivery path for bus/payload commands).
5. ✅ Model attitude/pointing at mode level (`_ATTITUDE_MODES`: nominal/slew/safe), not
   vector/quaternion fidelity — matching what the engine actually models, per FS-105's explicit
   fidelity-honesty requirement.

## Tests to Add

None — covered by the order-system and bus-model test suites (verb-by-verb gating and
physical-outcome assertions). The June 2026 commands audit (`docs/AUDIT-2026-06-COMMANDS.md`) is
the record of the cut/kept verb decisions this catalog reflects.

## Documentation Updates

- Supersedes [`docs/implementations/IMP-105A-spacecraft-operations-bus-payload.md`](../../implementations/IMP-105A-spacecraft-operations-bus-payload.md).
- `ROADMAP.md` Implementation Packages theme updated.

## Definition of Done

- [x] Every offered console verb exists in `COMMAND_VERBS`; no verb is offered that the engine
  cannot execute.
- [x] Payload verbs are rejected when the payload type doesn't match or the bus can't support them,
  both at plan-time (`can_issue`) and execution-time (`apply_command`) re-validation.
- [x] Attitude/pointing UI never implies finer control than the mode-level model actually provides.
- [x] Every verb mutation is replay-exact and observable via the existing pass-gated SOH/telemetry
  path — no separate bus-command-specific telemetry channel exists.
- [x] Constellation vignettes are operated per-asset; no fleet-aggregate verb exists in this catalog.

## Verification Checklist

- [x] `buscommands.py:18-48,71,80,524` and `bus.py` (`BusState`/`PayloadState`/`recompute_status`)
  read and confirmed against the current tree.
- [x] Order-system and bus-model test suites present and green.
- [x] No FR/NFR explicitly cites FS-105 (confirmed absence) — recorded as a traceability gap.

## Dependencies

- **Upstream:** IP-1020 (the `command` action's shared execution lifecycle).
- **Downstream:** IP-1051 (sibling package — effect resolution consumes bus/payload state this
  package mutates), IP-1070 (AAR replays this state), IP-2010 (assessment reads this data).
- **Build-sequencing:** None — already shipped; sequenced alongside IP-1051 as FS-105's two
  lettered sub-packages.

## Risks

- Fleet-level constellation aggregation ([R108](../../research/encyclopedia/R108-constellation-operations.md)
  §5) being silently added to this catalog without its own Feature Spec ID is named explicitly as a
  non-goal/risk in FS-105.
- A new verb added without updating both `can_issue()` and `apply_command()` consistently would
  reintroduce the class of defect the June 2026 commands audit specifically remediated (verbs with
  no consumer or a broken gating/execution loop).

## Rollback Considerations

Rollback surface: `spacesim/engine/buscommands.py` (entire module) and the `apply_command()` call
site in `spacesim/engine/orders.py:688`. `BusState`/`PayloadState` are part of the existing save/
eventlog schema (`spacesim/engine/bus.py`); a revert requires re-verification against the
order-system and bus-model test suites plus the determinism property test before landing.
