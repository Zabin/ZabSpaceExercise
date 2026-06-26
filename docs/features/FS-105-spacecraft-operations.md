# FS-105 — Spacecraft Operations

> **Document ID:** FS-105
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [DOM-001](../domains/DOM-001-training-framework.md), [DOM-007](../domains/DOM-007-human-factors-framework.md), [R103](../research/encyclopedia/R103-satellite-command-and-control.md), [R106](../research/encyclopedia/R106-mission-operations.md), [R107](../research/encyclopedia/R107-ground-segment-operations.md), [R108](../research/encyclopedia/R108-constellation-operations.md),
> [R110](../research/encyclopedia/R110-communications.md), [R111](../research/encyclopedia/R111-power-and-thermal-operations.md), [R112](../research/encyclopedia/R112-propulsion-and-maneuver-planning.md), [R113](../research/encyclopedia/R113-attitude-determination-and-control.md), [R114](../research/encyclopedia/R114-command-and-data-handling.md), [R115](../research/encyclopedia/R115-electronic-warfare-in-space-operations.md), [R116](../research/encyclopedia/R116-cyber-operations-against-space-systems.md),
> [R117](../research/encyclopedia/R117-directed-energy-and-kinetic-effects.md), [R120](../research/encyclopedia/R120-access-window-and-geometry-planning.md), [R303](../research/encyclopedia/R303-deterrence-theory.md), [R304](../research/encyclopedia/R304-escalation-dynamics.md)
> **Referenced By:** [DOM-001](../domains/DOM-001-training-framework.md), [DOM-007](../domains/DOM-007-human-factors-framework.md), all of [R103](../research/encyclopedia/R103-satellite-command-and-control.md)/[R106](../research/encyclopedia/R106-mission-operations.md)-[R120](../research/encyclopedia/R120-access-window-and-geometry-planning.md) (each names FS-105 as a direct or
> co-direct consumer)
> **Produces:** the executed-state surface consumed by [FS-107](FS-107-after-action-review.md) (AAR replay) and [FS-201](FS-201-competency-assessment.md) (assessment data)
> **Feature Mapping:** FS-105 (this document)
> **Related Topics:** [FS-101](FS-101-mission-planning.md) (the planning surface that feeds this console), [FS-102](FS-102-command-scheduling.md) (the execution
> lifecycle this console displays), [FS-103](FS-103-custody-management.md)/[FS-104](FS-104-sda-tasking.md) (custody/tasking surfaces hosted within this console)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

## 1. Purpose

Spacecraft Operations is the operator console itself — the surface through which a Red or Blue cell
issues every bus/payload command, observes telemetry, monitors state of health, and resolves every
one of the five effect categories. It is, by a wide margin, the largest feature surface in the
program: nearly every R100-tier topic ([R103](../research/encyclopedia/R103-satellite-command-and-control.md), [R106](../research/encyclopedia/R106-mission-operations.md)-[R120](../research/encyclopedia/R120-access-window-and-geometry-planning.md)) names FS-105 as a direct
or co-direct consumer. This spec consolidates those many individually-scoped consumption notes into
one coherent feature boundary rather than treating the console as an undifferentiated catch-all.

## 2. Scope

In scope: the full operator console — bus/payload command issuance (via [FS-102](FS-102-command-scheduling.md)'s scheduling
lifecycle), telemetry/SOH display, subsystem drill-down, all five effect categories' operator-facing
controls (jam, engage, observe, maneuver, downlink, cyber, and bus/payload `command` verbs), and the
consequence-confirm pattern for irreversible actions. Out of scope: planning/preview before commit
([FS-101](FS-101-mission-planning.md)), the command lifecycle mechanics themselves ([FS-102](FS-102-command-scheduling.md)), custody/tasking internals
([FS-103](FS-103-custody-management.md)/[FS-104](FS-104-sda-tasking.md), though their controls are hosted in this console), and White Cell's
cross-cell facilitator view ([FS-106](FS-106-white-cell-dashboard.md)).

## 3. Capability requirements

### 3.1 Bus and subsystem operations
- **Mission/plan/task/assess beats** ([R106](../research/encyclopedia/R106-mission-operations.md) §5) must be visible as the console's operating
  rhythm — the console should not present mission operations as an undifferentiated stream of
  buttons disconnected from this cycle.
- **Comms-posture commands** ([R110](../research/encyclopedia/R110-communications.md) §5) must surface through the existing bus subsystem panel,
  not a bespoke comms screen.
- **Power/thermal state must surface causally, not just numerically** ([R111](../research/encyclopedia/R111-power-and-thermal-operations.md) §5,
  [DOM-007](../domains/DOM-007-human-factors-framework.md) §4) — an operator must be able to tell *why* SoC or temperature is moving (eclipse,
  heater draw, attack signature), not just see the number change.
- **Pointing/attitude UI must be honest about ADCS fidelity** ([R113](../research/encyclopedia/R113-attitude-determination-and-control.md) §5) — today's model is
  mode-level, not vector-level; the console must not imply finer pointing control than the engine
  actually models.
- **Storage/downlink gating must be visibly respected** ([R114](../research/encyclopedia/R114-command-and-data-handling.md) §5) — any collection or downlink
  control must show the C&DH storage gate, not let an operator queue collection the bus cannot
  store.
- **Constellation vignettes are operated per-asset, not aggregated** ([R108](../research/encyclopedia/R108-constellation-operations.md) §5) — this
  spec does not include fleet-level aggregation; that would be new FS scope, not a silent FS-105
  extension.

### 3.2 Effect categories (the five D's + cyber exception)
- **Maneuver plans, once committed, must preview/confirm real Δv cost** ([R112](../research/encyclopedia/R112-propulsion-and-maneuver-planning.md) §5),
  consistent with [FS-101](FS-101-mission-planning.md)'s pre-commit version of the same requirement.
- **EW (jam) controls must expose the modulation tradeoff explicitly** ([R115](../research/encyclopedia/R115-electronic-warfare-in-space-operations.md) §5):
  effectiveness vs. detectability vs. attribution, not a single undifferentiated "jam" button.
- **Cyber controls must make the non-windowed resolution model clear** ([R116](../research/encyclopedia/R116-cyber-operations-against-space-systems.md) §5) — cyber
  resolves immediately against the target's posture, not at a future access window; the console
  must not visually imply cyber waits on a window the way other effect categories do.
- **Kinetic/DE engagement must preserve the consequence-confirm pattern** ([R117](../research/encyclopedia/R117-directed-energy-and-kinetic-effects.md) §5) for any
  new engagement-class feature — irreversible actions require deliberate confirmation, never a
  single click indistinguishable from a reversible one.
- **Window display for any windowed action must use genuine sampled/bisected geometry**
  ([R120](../research/encyclopedia/R120-access-window-and-geometry-planning.md) §5), matching [FS-101](FS-101-mission-planning.md) §3's requirement for the planning side of the same data.

### 3.3 Escalation and doctrine
- **Escalation tagging traces to real escalation-dynamics theory** ([R304](../research/encyclopedia/R304-escalation-dynamics.md) §5) — the
  kinetic consequence-confirm UX and any new effect category's "how escalatory is this" framing
  should be grounded in [R304](../research/encyclopedia/R304-escalation-dynamics.md), not invented ad hoc per feature.
- **ROE/deterrence framing is a console responsibility, not flavor** ([R303](../research/encyclopedia/R303-deterrence-theory.md) §5) — the ROE
  chip state visible at time of order is part of what makes escalation-discipline assessment
  ([DOM-002](../domains/DOM-002-assessment-framework.md) §4) possible at all.

## 4. Human factors (required per DOM-007 §7)

Per [DOM-007](../domains/DOM-007-human-factors-framework.md) §7, this spec states explicitly:
- **Intentional friction** (§3 of [DOM-007](../domains/DOM-007-human-factors-framework.md)): plan-first command latency, window gating, and the
  consequence-confirm gate are domain-accurate and must read as such, not as UI slowness.
- **Belief-vs-truth legibility** (§4): every custody/track display hosted in this console inherits
  [FS-103](FS-103-custody-management.md) §3's requirement that belief never be visually conflatable with ground truth.
- **Panel-manager contract** (§5): every new console panel must be a first-class citizen of the
  panel manager (close/float/resize/reset-to-dock) from the start, never a fixed-grid cell retrofit.

## 5. Educational value

Per [DOM-001](../domains/DOM-001-training-framework.md) §7, Spacecraft Operations serves the broadest objective-class coverage of any
feature in the program (it is the console every vignette's hands-on play happens through) — its
educational value is "operating a real bus/payload under real constraints," applicable across the
entire training progression, not a single objective class.

## 6. Non-goals

- No new effect category, gameplay mechanic, or fidelity tier is introduced by this spec — it is the
  unified operator-facing surface over capabilities each owned/grounded by its respective R10x topic.
- Fleet-level constellation aggregation ([R108](../research/encyclopedia/R108-constellation-operations.md) §5) is explicitly out of scope; a future
  aggregation feature needs its own FS ID.

## 7. Related Topics

See the `Dependencies`/`Referenced By` block above for the full R100-tier grounding set. [FS-101](FS-101-mission-planning.md)
(pre-commit planning), [FS-102](FS-102-command-scheduling.md) (execution lifecycle), [FS-103](FS-103-custody-management.md)/[FS-104](FS-104-sda-tasking.md) (custody/tasking surfaces
hosted here), [FS-106](FS-106-white-cell-dashboard.md) (the facilitator's cross-cell view of the same underlying state), [FS-107](FS-107-after-action-review.md)
(replay of this console's history), [DOM-007](../domains/DOM-007-human-factors-framework.md) (the human-factors constraints this spec satisfies).
