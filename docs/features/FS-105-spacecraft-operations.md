# FS-105 — Spacecraft Operations

> **Document ID:** FS-105
> **Version:** 1.1
> **Status:** ✅ Done (v1.0 scope); the v1.1 directed-energy slice is **✅ Done — implementation-ready**,
> all four Open Questions closed; ready for `07-implementation-planning`
> **Changelog (v1.1, 2026-09-26):** Added `Requirements Implemented`/System-Behaviour/Open-Questions
> coverage for the directed-energy (DE) order/resolution path, closing backlog `BL-0066` (external
> validation report A5, user decision 2026-09-26: a distinct DE path, not a documented DE→jam
> mapping). Updated twice more the same day: once `R117` v1.1 (`02-research-ow-orbital-mechanics`,
> closing `BL-0086`) supplied real DE grounding (probability model, reversibility split settled),
> and once `ADR-0034`/`ADR-0035` (`03-architecture-design-synthesis`, closing `BL-0088`/`BL-0089`)
> settled the gating access channel (reuses `weapon_engagement`) and confidence tier (follows the
> reversibility branch; no new tier). No v1.0-scope field's substance changed.
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

*This document follows the `06-feature-specification` skill's 20-field template; it supersedes this file's prior ad hoc structure while retaining its existing Document ID, status, and metadata per MSTR-006 §5.*

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

None identified for the v1.0 scope — the FR-xxxx/NFR-xxxx requirements corpus (`docs/requirements/`)
contains no explicit citation of this Feature ID. This is a traceability gap, not a deliberate
non-applicability; closing it is Phase 8 traceability-review work (MSTR-006 §7), not something this
rewrite may resolve by inference.

**v1.1 addition:** `FR-1410` (Five-D's effect resolution with reversibility and attribution) names
`directed_energy` as one of the five categories a counterspace action must resolve to. FS-105's own
v1.0 Scope already states this console "resolves every one of the five effect categories" — but as
of `32ca02a` (confirmed directly against the live tree, `08-code-implementation` run #55's sibling
finding `BL-0066`), no order ever produces a `directed_energy`-category effect: `engine/effects.py`
declares `directed_energy` as a `Category` literal and `engine/entities.py` an asset `kind`,
`engine/telemetry.py` carries a DE attack signature (SNR/optics-temp), but the `jam` order always
sets `category="electronic_warfare"` (`engine/orders.py:443`) and the UI maps every
`directed_energy`-kind asset to the `jam` action (`ui_web/static/app.js:73`). This v1.1 addition
specifies the *behavioral shape* of closing that gap; see Open Questions below for what it cannot
yet specify.

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

### Directed-energy (DE) order/resolution path (v1.1 addition)
- A Red or Blue operator commanding a `directed_energy`-kind asset issues a distinct DE order
  (not the `jam` action) against a target, resolved to a `directed_energy`-category effect —
  closing the `FR-1410` gap named above.
- The operator sees the DE-specific attack signature (`engine/telemetry.py`'s existing SNR/
  optics-temp model) become reachable on the target's telemetry once a DE effect actually executes
  — today this signature exists in code but no order can ever trigger it.
- Whether this order uses the existing consequence-confirm pattern (§ System Behaviour, kinetic/DE)
  depends on the reversibility question in Open Questions below.

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
- **(v1.1) A DE order must resolve to `category="directed_energy"`, never silently to
  `electronic_warfare`.** `FR-1410` names DE as a distinct category, and the engine already
  declares it as one — the gap is purely that no order path reaches it.
- **(v1.1, updated) DE's success probability must derive from a declared irradiance-at-range
  model, never an operator-typed number.** Per `R117` v1.1 §3.2/§5: effectiveness is a function of
  power, range, aperture, and beam quality (spot size ∝ wavelength × range / aperture), falling off
  with range — continuous physics, not a discrete per-class table the way kinetic engagement's
  `INTERCEPTORS` table is. A ground-based DE order's reachability/effectiveness must also account
  for the atmosphere-limited, weather-dependent range `R117` v1.1 describes; a space-based DE
  order's does not.
- **(v1.1, updated) A DE effect must resolve to one of two outcome branches by an irradiance/dwell
  threshold, not a single fixed reversibility flag.** Per `R117` v1.1 §3.2/§5: a dazzle-class effect
  (low irradiance/short dwell) resolves reversibly (`deny`/`disrupt`); a damage-class effect
  (threshold-crossing irradiance/sustained dwell) resolves irreversibly (`degrade`/`destroy`) and
  must use the same consequence-confirm pattern kinetic engagement uses. An HPM-class DE effect
  defaults to the irreversible branch, since real HPM reversibility is not attacker-controllable
  (`R117` v1.1 §3.2). The exact numeric threshold is an Implementation Package parameter (Open
  Questions below), not specified here.
- **(v1.1, settled by `ADR-0034`) A DE order is gated by the existing `weapon_engagement` access
  channel** — the same reachability predicate (`AccessProvider._weapon_predicate`) already used by
  kinetic engagement. No seventh access channel exists or is needed; DE's effectiveness math (the
  irradiance model above) is computed inside the resolver, exactly as jam's and kinetic's own
  effectiveness math already is, distinct from the channel-level reachability check.
- **(v1.1, settled by `ADR-0035`) A DE order's custody precondition follows its reversibility
  branch, reusing the two existing tiers:** a dazzle-branch order requires no custody precondition
  in `_validate` (identical to `jam`'s existing behavior); a damage-branch order requires the full
  weapons-quality gate (identical to `engage`'s existing behavior). No new confidence tier exists.

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
- **(v1.1)** A DE order against a `directed_energy`-kind asset produces an effect whose `category`
  field is `directed_energy`, never `electronic_warfare` — checkable directly against the
  resulting `EffectInstance`/event-log entry.
- **(v1.1, updated)** Two DE orders at different ranges against the same target (all else equal)
  produce different success probabilities, with the shorter-range order's probability at least as
  high as the longer-range order's — checkable by comparing two `EffectInstance.success_prob`
  values against `R117` v1.1's irradiance-falls-with-range model, without needing a specific
  formula's exact output.
- **(v1.1, updated)** A DE effect that crosses the (Implementation-Package-defined) damage
  threshold produces `reversible=False`; one that does not produces `reversible=True` — checkable
  directly against the resulting `EffectInstance`, and gated through the same consequence-confirm
  UI as kinetic engagement when `reversible=False`.
- **(v1.1, settled by `ADR-0034`)** A DE order is rejected with a `weapon_engagement`-channel
  no-access reason when no such window exists — checkable identically to how a rejected `engage`
  order is checked today, with `directed_energy` substituted for the effect category.
- **(v1.1, settled by `ADR-0035`)** A DE-dazzle order against a target with no track at all still
  succeeds or fails on its irradiance model alone (no `no_weapons_quality_track` rejection); a
  DE-damage order against a target with a track that is not weapons-quality is rejected
  `no_weapons_quality_track` — checkable directly against `_validate`'s outcome for each branch.

## Verification Plan

The source document does not state a Verification Method per criterion. Test (automated) is implied
for consequence-confirm, window-computation parity, and custody legibility (the last via existing
fog-of-war tests). Demonstration is likely the appropriate method for operator-rhythm and causal
power/thermal display. Flagged as an Open Question below.

**v1.1:** Test (automated) for the one settled acceptance criterion (DE order → `category="directed_energy"`
effect). The remaining DE criteria have no Verification Method yet because they have no content yet
— blocked on the same research pass named in Open Questions.

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
- **(v1.1, resolved same day) `R117`'s own title ("Directed Energy and Kinetic Effects") did not
  match its content** — every substantive claim was kinetic-`engage`-only, with no DE-specific
  physics, probability model, or reversibility characterization. Routed to
  `02-research-ow-orbital-mechanics`, which closed the gap (`BL-0086` → `R117` v1.1). This risk is
  retired; the two Open Questions §3.2/§5 explicitly declined to resolve (gating channel,
  weapons-quality tier) are real architecture decisions, not a research-grounding gap, and are
  tracked below rather than as a risk.
- ~~A DE-damage effect being irreversible would be the engine's second `reversible=False`
  category, tensioning MSTR-002's framing.~~ **Retired by `ADR-0035`:** the "MSTR-002" attribution
  doesn't hold up on direct read — `MSTR-002` makes no reversibility claim at all; the actual
  source is `CLAUDE.md`'s "most effects are reversible...not kinetic" summary, which already
  accommodates DE's two-branch shape ("most," not "all"). No amendment needed. (A small,
  non-blocking citation-accuracy finding on `R117` itself is tracked as `BL-0090`.)

## Open Questions

- No FR-xxxx/NFR-xxxx in `docs/requirements/` explicitly cites FS-105; this is a traceability gap
  for Phase 8 review (MSTR-006 §7), not a deliberate non-applicability.
- The source document does not assign a per-subsystem Subsystem Responsibilities table for the
  console's many component interactions.
- The source document does not address Data Model Changes; whether the console requires any new
  Domain Model entities is unresolved.
- The source document does not address Security Considerations beyond the fog-of-war boundary.
- The source document does not state formal Verification Methods per criterion.

**v1.1 additions, updated in this same version once `R117` v1.1 (`02-research-ow-orbital-mechanics`,
closing `BL-0086`) supplied real DE grounding — two of the original four are now settled enough to
state as System Behaviour/Acceptance Criteria (moved there; struck through below for the record),
two remain genuinely open and now block `07-implementation-planning`:**

- ~~DE's success/kill probability model is uncharacterized.~~ **Settled by `R117` v1.1 §3.2/§5:**
  DE effectiveness derives from an irradiance-at-range model (spot size ∝ wavelength × range /
  aperture; effectiveness falls with range) — a continuous physics-based model, not a discrete
  per-class table like kinetic's `INTERCEPTORS`. See System Behaviour and Acceptance Criteria below
  for the resulting behavioral contract. (The exact formula/constants are an Implementation Package
  decision within this shape, not a spec-level one.)
- ~~DE's reversibility split is undecided.~~ **Settled in shape by `R117` v1.1 §3.2/§5:** DE splits
  into two outcome branches by an irradiance/dwell threshold — a low-irradiance/short-dwell effect
  is reversible (`deny`/`disrupt`), a threshold-crossing high-irradiance/sustained-dwell effect is
  irreversible (`degrade`/`destroy`); HPM's attacker-uncontrollable reversibility (`R117` §3.2)
  means an HPM-class DE effect should default to the irreversible branch. **Still open:** no
  open-source irradiance-threshold figure was found (`R117` v1.1 §5) — the numeric crossing point
  is a tunable Implementation Package parameter, not a spec-level fact, and does not by itself
  block `07`.
- ~~DE's gating access channel remains an architecture decision.~~ **Closed by `ADR-0034`:** DE
  reuses `weapon_engagement`; no seventh channel.
- ~~Whether DE needs a new, lower-than-weapons-quality confidence tier remains an architecture
  decision.~~ **Closed by `ADR-0035`:** DE's custody precondition follows its reversibility branch
  (dazzle: none, like `jam`; damage: weapons-quality, like `engage`); no new tier.

**All four v1.1 Open Questions are now closed.** `FS-105` v1.1's directed-energy slice is
implementation-ready; the numeric dazzle/damage irradiance threshold (noted above, in System
Behaviour) remains a tunable Implementation Package parameter, not a spec-level blocker, consistent
with how kinetic engagement's own Pₖ constants are an Implementation Package detail, not a spec-
level one.

## Related ADRs

ADR-0011 (six access channels taxonomy) — `docs/architecture/adr/ADR-0011-six-access-channels.md`;
ADR-0005 (plan-first commanding model) — `docs/architecture/adr/ADR-0005-plan-first-commanding.md`;
ADR-0034 (v1.1 — DE reuses `weapon_engagement`, no seventh channel) —
`docs/architecture/adr/ADR-0034-directed-energy-reuses-weapon-engagement-channel.md`; ADR-0035
(v1.1 — DE confidence tier follows its reversibility branch, no new tier) —
`docs/architecture/adr/ADR-0035-directed-energy-confidence-tiers-by-branch.md`.

## Related Interfaces

INT-0004 (Blue/Red Cell Operator ↔ Operator Console); INT-0008 (SessionManager → Simulation Engine
Clock/Scheduler/EventLog/OrderSystem) — per `docs/design/05-interface-control-document.md`.
