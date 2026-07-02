# FS-105 — Spacecraft Operations

> **Document ID:** FS-105
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [DOM-001](../domains/DOM-001-training-framework.md), [DOM-007](../domains/DOM-007-human-factors-framework.md), [R103](../research/encyclopedia/R103-satellite-command-and-control.md), [R106](../research/encyclopedia/R106-mission-operations.md), [R107](../research/encyclopedia/R107-ground-segment-operations.md), [R108](../research/encyclopedia/R108-constellation-operations.md),
> [R110](../research/encyclopedia/R110-communications.md), [R111](../research/encyclopedia/R111-power-and-thermal-operations.md), [R112](../research/encyclopedia/R112-propulsion-and-maneuver-planning.md), [R113](../research/encyclopedia/R113-attitude-determination-and-control.md), [R114](../research/encyclopedia/R114-command-and-data-handling.md), [R115](../research/encyclopedia/R115-electronic-warfare-in-space-operations.md), [R116](../research/encyclopedia/R116-cyber-operations-against-space-systems.md),
> [R117](../research/encyclopedia/R117-directed-energy-and-kinetic-effects.md), [R120](../research/encyclopedia/R120-access-window-and-geometry-planning.md), [R303](../research/encyclopedia/R303-deterrence-theory.md), [R304](../research/encyclopedia/R304-escalation-dynamics.md)
> **Referenced By:** [DOM-001](../domains/DOM-001-training-framework.md), [DOM-007](../domains/DOM-007-human-factors-framework.md), all of [R103](../research/encyclopedia/R103-satellite-command-and-control.md)/[R106](../research/encyclopedia/R106-mission-operations.md)-[R120](../research/encyclopedia/R120-access-window-and-geometry-planning.md) (each names FS-105 as a direct or
> co-direct consumer), [IMP-105A](../implementations/IMP-105A-spacecraft-operations-bus-payload.md), [IMP-105B](../implementations/IMP-105B-spacecraft-operations-effects-console.md)
> **Produces:** the executed-state surface consumed by [FS-107](FS-107-after-action-review.md) (AAR replay) and [FS-201](FS-201-competency-assessment.md) (assessment data)
> **Feature Mapping:** FS-105 (this document)
> **Related Topics:** [FS-101](FS-101-mission-planning.md) (the planning surface that feeds this console), [FS-102](FS-102-command-scheduling.md) (the execution
> lifecycle this console displays), [FS-103](FS-103-custody-management.md)/[FS-104](FS-104-sda-tasking.md) (custody/tasking surfaces hosted within this console)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `feature-specification` skill's 20-field template; it supersedes this file's prior ad hoc structure while retaining its existing Document ID, status, and metadata per MSTR-006 §5.*

## Feature ID

FS-105

## Title

Spacecraft Operations

## Purpose

Spacecraft Operations is the operator console itself — the surface through which a Red or Blue cell
issues every bus/payload command, observes telemetry, monitors state of health, and resolves every
one of the five effect categories. Nearly every R100-tier topic ([R103](../research/encyclopedia/R103-satellite-command-and-control.md), [R106](../research/encyclopedia/R106-mission-operations.md)-[R120](../research/encyclopedia/R120-access-window-and-geometry-planning.md)) names
FS-105 as a direct or co-direct consumer. This spec consolidates those many individually-scoped
consumption notes into one coherent feature boundary rather than treating the console as an
undifferentiated catch-all.

## Scope

In scope: the full operator console — bus/payload command issuance (via [FS-102](FS-102-command-scheduling.md)'s scheduling
lifecycle), telemetry/SOH display, subsystem drill-down, all five effect categories' operator-facing
controls (jam, engage, observe, maneuver, downlink, cyber, and bus/payload `command` verbs), and the
consequence-confirm pattern for irreversible actions. Out of scope: planning/preview before commit
([FS-101](FS-101-mission-planning.md)), the command lifecycle mechanics themselves ([FS-102](FS-102-command-scheduling.md)), custody/tasking internals
([FS-103](FS-103-custody-management.md)/[FS-104](FS-104-sda-tasking.md) — though their controls are hosted in this console), White Cell's
cross-cell facilitator view ([FS-106](FS-106-white-cell-dashboard.md)), and fleet-level constellation aggregation ([R108](../research/encyclopedia/R108-constellation-operations.md) §5 —
requires its own FS ID).

## Requirements Implemented

None identified — the FR-xxxx/NFR-xxxx requirements corpus (`docs/requirements/`) contains no
explicit citation of this Feature ID. This is a traceability gap, not a deliberate
non-applicability; closing it is Phase 8 traceability-review work (MSTR-006 §7), not something this
rewrite may resolve by inference.

## User Workflows

### Bus and subsystem operations
- An operator observes the mission/plan/task/assess beat rhythm ([R106](../research/encyclopedia/R106-mission-operations.md) §5) as the console's
  operating cycle — not an undifferentiated stream of buttons.
- An operator issues comms-posture commands through the existing bus subsystem panel ([R110](../research/encyclopedia/R110-communications.md) §5).
- An operator observes power and thermal state causally — understanding *why* SoC or temperature is
  moving (eclipse, heater draw, attack signature), not just seeing a number change ([R111](../research/encyclopedia/R111-power-and-thermal-operations.md) §5,
  [DOM-007](../domains/DOM-007-human-factors-framework.md) §4).
- An operator commands pointing/attitude mode and understands the console reflects mode-level
  control, not vector-level fidelity ([R113](../research/encyclopedia/R113-attitude-determination-and-control.md) §5).
- An operator observes the C&DH storage gate before queuing collection or downlink ([R114](../research/encyclopedia/R114-command-and-data-handling.md) §5).
- Constellation vignettes are operated per-asset — no fleet-level aggregate control exists in this
  spec ([R108](../research/encyclopedia/R108-constellation-operations.md) §5).

### Effect categories (the five D's + cyber exception)
- For maneuver plans already committed, the console previews/confirms real Δv cost ([R112](../research/encyclopedia/R112-propulsion-and-maneuver-planning.md) §5).
- EW (jam) controls expose the modulation tradeoff (effectiveness vs. detectability vs. attribution)
  explicitly ([R115](../research/encyclopedia/R115-electronic-warfare-in-space-operations.md) §5).
- Cyber controls make the non-windowed resolution model clear — cyber resolves against posture
  immediately, and the console does not imply a window wait ([R116](../research/encyclopedia/R116-cyber-operations-against-space-systems.md) §5).
- Kinetic/DE engagement requires the consequence-confirm pattern for irreversible actions ([R117](../research/encyclopedia/R117-directed-energy-and-kinetic-effects.md) §5).
- Window display for windowed actions uses genuine sampled/bisected geometry ([R120](../research/encyclopedia/R120-access-window-and-geometry-planning.md) §5).

### Escalation and doctrine
- ROE chip state is visible at time of order, grounding escalation-discipline assessment ([R303](../research/encyclopedia/R303-deterrence-theory.md) §5,
  [DOM-002](../domains/DOM-002-assessment-framework.md) §4).
- Escalation-tagging for kinetic consequence-confirm UX is grounded in [R304](../research/encyclopedia/R304-escalation-dynamics.md), not ad hoc per feature.

## System Behaviour

- **Mission/plan/task/assess beat must be visible as the console's operating rhythm.** Per [R106](../research/encyclopedia/R106-mission-operations.md) §5,
  the console must not present mission operations as an undifferentiated stream of buttons
  disconnected from this cycle.
- **Power/thermal state must surface causally.** An operator must be able to tell *why* SoC or
  temperature is moving — not just see the number change ([R111](../research/encyclopedia/R111-power-and-thermal-operations.md) §5, [DOM-007](../domains/DOM-007-human-factors-framework.md) §4).
- **Pointing/attitude UI must be honest about ADCS fidelity.** Today's model is mode-level, not
  vector-level; the console must not imply finer pointing control than the engine models ([R113](../research/encyclopedia/R113-attitude-determination-and-control.md) §5).
- **Storage/downlink gating must be visibly respected.** Any collection or downlink control must
  show the C&DH storage gate ([R114](../research/encyclopedia/R114-command-and-data-handling.md) §5).
- **EW modulation tradeoff must be explicit.** Effectiveness vs. detectability vs. attribution, not
  a single undifferentiated "jam" button ([R115](../research/encyclopedia/R115-electronic-warfare-in-space-operations.md) §5).
- **Cyber controls must make non-windowed resolution clear.** Cyber resolves immediately against
  posture; the console must not visually imply cyber waits on a window ([R116](../research/encyclopedia/R116-cyber-operations-against-space-systems.md) §5).
- **Kinetic/DE must use the consequence-confirm pattern.** Irreversible actions require deliberate
  confirmation, never a single click indistinguishable from a reversible one ([R117](../research/encyclopedia/R117-directed-energy-and-kinetic-effects.md) §5).
- **Window display uses genuine sampled/bisected geometry.** Consistent with [FS-101](FS-101-mission-planning.md) §3's requirement
  for the planning side of the same data ([R120](../research/encyclopedia/R120-access-window-and-geometry-planning.md) §5).
- **Belief must stay visually distinguishable from ground truth.** Every custody/track display
  hosted in this console inherits [FS-103](FS-103-custody-management.md) §3's requirement ([DOM-007](../domains/DOM-007-human-factors-framework.md) §4).

## Subsystem Responsibilities

The source document does not provide a formal per-subsystem breakdown. Per [`CLAUDE.md`](../../CLAUDE.md): the
operator console is `spacesim/ui_web/` (presentation layer); it consumes the Session Layer
(`SessionAPI`, `CellController`) which enforces fog-of-war; the engine's `OrderSystem`,
`EffectResolver`, `BusSystem`, `buscommands.py` implement the underlying command verbs. The source
document does not distribute responsibilities across these components in a table. Flagged as an Open
Question below.

## Interfaces Used

Per the verified mapping for FS-105: INT-0004 (Blue/Red Cell Operator ↔ Operator Console) and
INT-0008 (SessionManager → Simulation Engine Clock/Scheduler/EventLog/OrderSystem) — per
`docs/design/05-interface-control-document.md`. The source document does not itself cite ICD
interface IDs; these are carried forward from the verified Related Interfaces mapping (field 21).

## Data Model Changes

Not addressed in the source document — no existing content to carry forward. The console consumes
existing engine state (bus/payload SOH, `WorldState`, `EventLog`, custody) without the source
document specifying new Domain Model entities. Flagged as an Open Question below.

## State Changes

- Commanding a bus/payload verb transitions `BusState`/`PayloadState` (as described for
  `buscommands.py` in [`CLAUDE.md`](../../CLAUDE.md)); the console reflects the new state via telemetry.
- Consequence-confirm completion is a two-step operator action for irreversible orders; the console
  must ensure neither step is skippable.
- ROE chip state transitions are observable at time of order issuance; the console must capture
  the chip state in the historical record for [FS-201](FS-201-competency-assessment.md)'s escalation-discipline dimension.

## Error Handling

- The consequence-confirm pattern for kinetic/DE actions provides explicit confirmation before
  irreversible effect execution — not just a disable/enable guard.
- The pre-disabled-button pattern (per [FS-101](FS-101-mission-planning.md) §3, [DOM-007](../domains/DOM-007-human-factors-framework.md) §4) surfaces constraint reasons ("no window,"
  "insufficient custody," "C&DH gate") before an operator attempts a blocked action.
- The source document does not enumerate further error states or failure modes.

## Performance Considerations

- **Intentional friction** ([DOM-007](../domains/DOM-007-human-factors-framework.md) §3): plan-first command latency, window gating, and the
  consequence-confirm gate are domain-accurate and must read as such, not as UI slowness.
- **Belief-vs-truth legibility** ([DOM-007](../domains/DOM-007-human-factors-framework.md) §4): every custody/track display in this console inherits
  the load-bearing legibility requirement from [FS-103](FS-103-custody-management.md) §3.
- **Panel-manager contract** ([DOM-007](../domains/DOM-007-human-factors-framework.md) §5): every new console panel must be a first-class citizen
  of the panel manager (close/float/resize/reset-to-dock) from the start.

## Security Considerations

Not addressed in the source document beyond the fog-of-war boundary already enforced at
`CellController` (ADR-0004). The LAN trust model (ADR-0015) applies at the session layer, not at
the console layer; the source document does not discuss per-console security requirements. Flagged
as an Open Question below.

## Acceptance Criteria

Derived from the source document's capability requirements, restated as checkable conditions:

- Mission/plan/task/assess beat is discernible in the console's operation rhythm.
- Power/thermal state display explains the *cause* of a change (eclipse, heater, attack), not just
  the value.
- Attitude/pointing UI describes the mode-level control it actually provides, not vector-level.
- C&DH storage gate is visible before collection or downlink is queued.
- EW (jam) controls expose the modulation tradeoff (effectiveness/detectability/attribution) before
  commitment.
- Cyber controls do not imply a window wait; they show immediate-resolution behavior.
- Kinetic/DE engagement requires the two-step consequence-confirm — never a single-click path.
- Window display for windowed actions is derived from the same access-window geometry the engine
  uses for execution gating.
- Custody/track displays in this console satisfy FS-103's belief/ground-truth-legibility requirement.
- ROE chip state is captured at time of order for downstream assessment.

## Verification Plan

The source document does not state a Verification Method per criterion. Test (automated) is implied
for consequence-confirm, window-computation parity, and custody legibility (the last via existing
fog-of-war tests). Demonstration is likely the appropriate method for operator-rhythm and causal
power/thermal display. Flagged as an Open Question below.

## Dependencies

[DOM-001](../domains/DOM-001-training-framework.md), [DOM-007](../domains/DOM-007-human-factors-framework.md), [R103](../research/encyclopedia/R103-satellite-command-and-control.md), [R106](../research/encyclopedia/R106-mission-operations.md)-[R120](../research/encyclopedia/R120-access-window-and-geometry-planning.md), [R303](../research/encyclopedia/R303-deterrence-theory.md), [R304](../research/encyclopedia/R304-escalation-dynamics.md) (per the existing
metadata block's Dependencies field). [FS-101](FS-101-mission-planning.md) (pre-commit planning), [FS-102](FS-102-command-scheduling.md) (execution lifecycle),
[FS-103](FS-103-custody-management.md)/[FS-104](FS-104-sda-tasking.md) (custody/tasking surfaces hosted here) are upstream features this console
displays, not formal dependencies in the metadata block.

## Risks

- Fleet-level constellation aggregation ([R108](../research/encyclopedia/R108-constellation-operations.md) §5) being silently added into this console without
  its own FS ID is named explicitly as a risk to avoid in the source document's non-goals.
- A new effect category or fidelity tier being added without its own domain/research grounding would
  create an ungrounded capability claim — the source document names this as a non-goal and a risk
  boundary.

## Open Questions

- No FR-xxxx/NFR-xxxx in `docs/requirements/` explicitly cites FS-105; this is a traceability gap
  for Phase 8 review (MSTR-006 §7), not a deliberate non-applicability.
- The source document does not assign a per-subsystem Subsystem Responsibilities table for the
  console's many component interactions.
- The source document does not address Data Model Changes; whether the console requires any new
  Domain Model entities is unresolved.
- The source document does not address Security Considerations beyond the fog-of-war boundary.
- The source document does not state formal Verification Methods per criterion.

## Related ADRs

ADR-0011 (six access channels taxonomy) — `docs/architecture/adr/ADR-0011-six-access-channels.md`;
ADR-0005 (plan-first commanding model) — `docs/architecture/adr/ADR-0005-plan-first-commanding.md`.

## Related Interfaces

INT-0004 (Blue/Red Cell Operator ↔ Operator Console); INT-0008 (SessionManager → Simulation Engine
Clock/Scheduler/EventLog/OrderSystem) — per `docs/design/05-interface-control-document.md`.
