# FS-201 — Competency Assessment

> **Document ID:** FS-201
> **Version:** 1.0
> **Status:** ✅ Done *(spec only — `Status` describes this document, not the underlying capability,
> which remains ⛔ Planned per [DOM-002](../domains/DOM-002-assessment-framework.md); [IMP-201A](../implementations/IMP-201A-competency-assessment.md)
> exists as a design-only package per `MSTR-006` §3 — it is not an implementation-authorizing document)*
> **Dependencies:** [DOM-002](../domains/DOM-002-assessment-framework.md), [DOM-005](../domains/DOM-005-validation-framework.md) §7, [DOM-001](../domains/DOM-001-training-framework.md), [R306](../research/encyclopedia/R306-operational-assessment.md), [R310](../research/encyclopedia/R310-effects-based-operations.md)
> **Referenced By:** [DOM-002](../domains/DOM-002-assessment-framework.md), [DOM-005](../domains/DOM-005-validation-framework.md), [DOM-001](../domains/DOM-001-training-framework.md), [R306](../research/encyclopedia/R306-operational-assessment.md), [R310](../research/encyclopedia/R310-effects-based-operations.md), [IMP-201A](../implementations/IMP-201A-competency-assessment.md), [FS-202](FS-202-rubric-authoring.md)
> **Produces:** the per-cell/per-exercise and longitudinal competency report; export data consumed by
> [FS-301](FS-301-research-analytics.md)
> **Feature Mapping:** FS-201 (this document)
> **Related Topics:** [FS-202](FS-202-rubric-authoring.md) (candidate rubric-authoring tooling), [FS-103](FS-103-custody-management.md) (custody-quality data
> source), [FS-107](FS-107-after-action-review.md) (belief-truth-divergence data source)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `feature-specification` skill's 20-field template; it supersedes this file's prior ad hoc structure while retaining its existing Document ID, status, and metadata per MSTR-006 §5.*

## Feature ID

FS-201

## Title

Competency Assessment

## Purpose

Competency Assessment replaces the engine's current binary objective-flip success/failure signal
with a richer, rubric-based measurement of *how* a cell demonstrated the competency a vignette was
designed to exercise. Per [DOM-002](../domains/DOM-002-assessment-framework.md) §3, a cell can flip an objective through luck or exploit
without ever forming a correct custody-based belief, and conversely can demonstrate excellent
tradecraft and still lose — the binary signal captures neither case. This spec defines the FS-201
capability that [DOM-002](../domains/DOM-002-assessment-framework.md) and [DOM-005](../domains/DOM-005-validation-framework.md) both explicitly require.

## Scope

In scope: the six measurement dimensions ([DOM-002](../domains/DOM-002-assessment-framework.md) §4) — with first-iteration scope of three
(custody quality, window discipline, belief-truth divergence) and three deferred — the rubric-tier
reporting model, and the per-cell/per-exercise and longitudinal report surfaces. Out of scope:
tooling to *author or adjust* rubric tiers ([FS-202](FS-202-rubric-authoring.md), candidate), and multi-run/cohort export for
instrument-grade research ([FS-301](FS-301-research-analytics.md)).

## Requirements Implemented

None identified — the FR-xxxx/NFR-xxxx requirements corpus (`docs/requirements/`) contains no
explicit citation of this Feature ID. This is a traceability gap, not a deliberate
non-applicability; closing it is Phase 8 traceability-review work (MSTR-006 §7), not something this
rewrite may resolve by inference.

## User Workflows

- After an exercise, a facilitator (White Cell) views the per-cell per-exercise competency report:
  a rubric-tier result for each of the three first-iteration dimensions, presented side-by-side for
  both cells, never collapsed into a single composite number.
- A facilitator uses the report alongside the [FS-107](FS-107-after-action-review.md) AAR instrument to explain to trainees why
  their rubric tier was assigned — the rubric provides language; the AAR provides the timeline
  evidence.
- Longitudinally, a trainer tracks a per-trainee progression across multiple exercises ([DOM-001](../domains/DOM-001-training-framework.md) §4):
  the report surfaces dimension-by-dimension trend, never a leaderboard number.
- The facilitator can apply qualitative facilitator-rubric judgment ([DOM-002](../domains/DOM-002-assessment-framework.md) §6) alongside or
  instead of the automated dimensions, from the [FS-106](FS-106-white-cell-dashboard.md) White Cell Dashboard.
- A trainee can use the report in self-assessment mode alongside [FS-107](FS-107-after-action-review.md), with no new engine
  feature required.

## System Behaviour

- **First-iteration dimensions are custody quality, window discipline, and belief-truth divergence.**
  These three are derivable most directly from data the engine already unambiguously produces:
  `Track` confidence history ([FS-103](FS-103-custody-management.md)), `OrderSystem` rejection/`dry_run()` usage ([FS-102](FS-102-command-scheduling.md)),
  and AAR's `snapshot_at()` god-view/belief diff ([FS-107](FS-107-after-action-review.md)). **Deferred** (requires baseline data not
  yet structured): resource economy and escalation discipline (need a vignette-specific resource/ROE
  budget baseline); time-to-decision (needs an OODA-loop tightness reference baseline per [R208](../research/encyclopedia/R208-ooda-loops.md)).
- **Rubric tiers per dimension** ([DOM-002](../domains/DOM-002-assessment-framework.md) §5):
  - *Custody quality:* speculative / adequate / disciplined.
  - *Window discipline:* frequent-invalid-attempts / occasional / disciplined.
  - *Belief-truth divergence:* high-divergence-unaware / high-divergence-aware / low-divergence.
- **Report surfaces** are per-cell per-exercise (immediate debrief, facilitator-facing summary) and
  longitudinal per-trainee across exercises ([DOM-001](../domains/DOM-001-training-framework.md) §4) — both present the rubric, never a
  single leaderboard number, per [DOM-002](../domains/DOM-002-assessment-framework.md) §5.
- **No new gameplay mechanic.** This feature is a read-only analytics layer over existing engine
  state (eventlog, custody history, order log, AAR snapshots). A scoring computation must not
  mutate `WorldState` — consistent with [MSTR-002](../master/MSTR-002-architecture-principles.md) §5's replay-safety principle.
- **Assessment modes** ([DOM-002](../domains/DOM-002-assessment-framework.md) §6): automated in-engine (always available); facilitator rubric
  (White Cell qualitative judgment, surfaced via [FS-106](FS-106-white-cell-dashboard.md)); self-assessment / debrief
  reflection (AAR walkthrough, no new engine feature required per [FS-107](FS-107-after-action-review.md)).
- **Validation discipline** ([DOM-005](../domains/DOM-005-validation-framework.md) §7): any quantitative claim about what a dimension "means"
  must cite which DOM-005 §5 validity check(s) were applied. This spec does not claim any of its
  three first-iteration dimensions have completed those checks; that is an Implementation Package
  and ongoing-validation responsibility.

## Subsystem Responsibilities

The source document does not provide a per-subsystem breakdown. The scoring computation reads from
`engine/custody.py` (custody quality data), `engine/orders.py` / `dry_run()` (window discipline
data), and `session/aar.py` / `snapshot_at()` (belief-truth divergence data). The report surface
is presented via the [FS-106](FS-106-white-cell-dashboard.md) facilitator view. The source document does not assign these to a
formal responsibility table. Flagged as an Open Question below.

## Interfaces Used

The source document does not cite ICD interface IDs for this feature. The scoring computation reads
from internal engine/session state rather than crossing a named ICD boundary; the report surface is
hosted within [FS-106](FS-106-white-cell-dashboard.md)'s facilitator view (INT-0002 applies transitively). Flagged as an Open
Question below.

## Data Model Changes

Not addressed in the source document — no existing content to carry forward. The rubric-tier result
per dimension per cell per exercise must be stored somewhere queryable for the longitudinal report
surface, which implies new persistent state, but the source document does not specify a schema.
Flagged as an Open Question below.

## State Changes

- After each exercise, a rubric-tier result is computed for each implemented dimension per cell and
  stored as part of the session record.
- The longitudinal report aggregates stored results across sessions per trainee — implying a
  cross-session data structure not present in the single-exercise save format.
- The scoring computation itself is read-only with respect to `WorldState`; no state change occurs
  during computation.

## Error Handling

- The scoring computation must not mutate `WorldState` — a scoring operation that produces a
  side effect on live session state is a defect, not a recoverable error.
- Deferred dimensions (resource economy, escalation discipline, time-to-decision) must not produce
  a result in the absence of their required baseline data; the report must make the absence
  explicit, not silently substitute a default.
- The source document does not enumerate further error modes.

## Performance Considerations

- **No `WorldState` mutation.** The scoring computation must be provably read-only — consistent with
  the replay-safety principle ([MSTR-002](../master/MSTR-002-architecture-principles.md) §5, ADR-0002).
- **Validation discipline.** Per [DOM-005](../domains/DOM-005-validation-framework.md) §7, any metric reported must disclose which validity
  check(s) were applied — a metric that has only passed face validity must be reported as such.

## Security Considerations

Not addressed in the source document — no existing content to carry forward. The competency report
contains per-trainee performance data; access controls on who can view longitudinal records are not
discussed. Flagged as an Open Question below.

## Acceptance Criteria

Derived from the source document's capability requirements, restated as checkable conditions:

- The per-cell per-exercise report presents rubric-tier results for the three first-iteration
  dimensions (custody quality, window discipline, belief-truth divergence) side-by-side for both
  cells, without collapsing them into a composite number.
- Deferred dimensions (resource economy, escalation discipline, time-to-decision) are absent from
  the report, not substituted with a default, in the first iteration.
- A longitudinal per-trainee report aggregates dimension-by-dimension results across exercises.
- The scoring computation produces no `WorldState` mutation.
- The report is accessible in all three assessment modes: automated in-engine, facilitator rubric
  (from [FS-106](FS-106-white-cell-dashboard.md)), and self-assessment/debrief ([FS-107](FS-107-after-action-review.md)).
- No composite single score is produced (per [DOM-002](../domains/DOM-002-assessment-framework.md) §5's explicit rejection of numeric averaging
  across non-commensurable dimensions).

## Verification Plan

The source document does not state a Verification Method per criterion. Test (automated) is implied
for the no-mutation constraint and the absence-of-deferred-dimensions behavior. Demonstration is
likely the appropriate method for report surface accessibility across all three assessment modes.
Flagged as an Open Question below.

## Dependencies

[DOM-002](../domains/DOM-002-assessment-framework.md), [DOM-005](../domains/DOM-005-validation-framework.md) §7, [DOM-001](../domains/DOM-001-training-framework.md), [R306](../research/encyclopedia/R306-operational-assessment.md), [R310](../research/encyclopedia/R310-effects-based-operations.md) (per the existing
metadata block's Dependencies field). [FS-107](FS-107-after-action-review.md) (belief-truth divergence data source), [FS-103](FS-103-custody-management.md)
(custody quality data source), [FS-102](FS-102-command-scheduling.md) (window discipline data source via order log) are upstream
feature outputs that this feature reads; they are not in the metadata block's Dependencies field but
are functional prerequisites. [FS-202](FS-202-rubric-authoring.md) and [FS-301](FS-301-research-analytics.md) are downstream consumers, not
dependencies of FS-201.

## Risks

- The three deferred dimensions (resource economy, escalation discipline, time-to-decision) each
  require baseline data structures (vignette-specific resource/ROE budget, OODA-loop reference)
  that do not yet exist — a future author who adds them without their required baselines would
  produce a metric that cannot be meaningfully scored.
- Any rubric-tier computation that modifies `WorldState` (even temporarily) would violate the
  replay-safety invariant.
- Per [DOM-005](../domains/DOM-005-validation-framework.md) §7, if a dimension's validity check level is not disclosed in the report,
  it may be misconstrued as fully validated when it has only passed face validity.

## Open Questions

- No FR-xxxx/NFR-xxxx in `docs/requirements/` explicitly cites FS-201; this is a traceability gap
  for Phase 8 review (MSTR-006 §7), not a deliberate non-applicability.
- The source document does not assign a per-subsystem Subsystem Responsibilities table.
- The source document does not specify a schema for the rubric-tier result record; whether it
  requires a new Domain Model entity or extends the existing `EventLog`/`SavedSession` is
  unresolved.
- The longitudinal per-trainee aggregation implies a cross-session data structure not present in
  the existing save format — how this is stored and queried is unresolved.
- The source document does not address Security Considerations for per-trainee longitudinal data.
- The source document does not state formal Verification Methods per criterion.
- No ICD interface explicitly names the competency assessment scoring or report path; whether a new
  INT-xxxx interface is needed is unresolved for Phase 8.

## Related ADRs

ADR-0017 (manual adjudication; no automated scoring in v1) —
`docs/architecture/adr/ADR-0017-manual-adjudication.md`;
ADR-0029 (assessment-scoring-workflow-ownership: raw AAR/event-log access is sufficient for the
assessment-designer stakeholder) —
`docs/architecture/adr/ADR-0029-assessment-scoring-workflow-ownership.md`.

## Related Interfaces

None identified — no ICD interface in `docs/design/05-interface-control-document.md` explicitly
names the competency assessment scoring or report boundary as a distinct interface. This is a
traceability gap for Phase 8 review if a named interface is required for the IMP-201A implementation
design.
