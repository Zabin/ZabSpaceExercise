# FS-103 — Custody Management

> **Document ID:** FS-103
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [DOM-009](../domains/DOM-009-doctrine-development-framework.md), [R105](../research/encyclopedia/R105-custody-theory.md)
> **Referenced By:** [DOM-009](../domains/DOM-009-doctrine-development-framework.md), [R105](../research/encyclopedia/R105-custody-theory.md), [DOM-002](../domains/DOM-002-assessment-framework.md) (custody quality dimension), [IMP-103A](../implementations/IMP-103A-custody-management.md)
> **Produces:** the custody/track-confidence surface consumed by [FS-104](FS-104-sda-tasking.md) (tasking that updates custody) and
> [FS-105](FS-105-spacecraft-operations.md) (effects gated by weapons-quality custody)
> **Feature Mapping:** FS-103 (this document)
> **Related Topics:** [R104](../research/encyclopedia/R104-collection-management.md) (collection feeding custody), [R115](../research/encyclopedia/R115-electronic-warfare-in-space-operations.md)-[R117](../research/encyclopedia/R117-directed-energy-and-kinetic-effects.md) (effect categories with custody
> preconditions), [DOM-002](../domains/DOM-002-assessment-framework.md) §4 (custody quality as an assessment dimension)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `feature-specification` skill's 20-field template; it supersedes this file's prior ad hoc structure while retaining its existing Document ID, status, and metadata per MSTR-006 §5.*

## Feature ID

FS-103

## Title

Custody Management

## Purpose

Custody Management is the capability by which a cell builds, maintains, and consults confidence in
its track picture of an object — the operational expression of fog-of-war's central claim that a
cell never sees ground truth directly, only a custody-mediated belief. Per [R105](../research/encyclopedia/R105-custody-theory.md) §5, this
feature is the **direct owner** of the custody model surfaced to operators; [DOM-009](../domains/DOM-009-doctrine-development-framework.md) names it as
one of the two Feature Specifications the doctrine-translation pipeline depends on (the other being
[FS-104](FS-104-sda-tasking.md)).

## Scope

In scope: how track confidence is displayed, how it decays over time absent fresh collection, and
how the "weapons-quality" threshold gates downstream effects. Out of scope: the sensor/SSN tasking
that produces fresh custody data ([FS-104](FS-104-sda-tasking.md)), and the effects themselves once their custody
precondition is satisfied ([FS-105](FS-105-spacecraft-operations.md)).

## Requirements Implemented

None identified — the FR-xxxx/NFR-xxxx requirements corpus (`docs/requirements/`) contains no
explicit citation of this Feature ID. This is a traceability gap, not a deliberate
non-applicability; closing it is Phase 8 traceability-review work (MSTR-006 §7), not something this
rewrite may resolve by inference.

## User Workflows

- A cell operator observes a track in the console; its confidence is displayed as a continuous,
  decaying value rather than a binary tracked/untracked flag.
- As time passes without fresh collection, the operator can observe confidence falling — the display
  reflects *how stale* the track is, not just whether one exists.
- Before committing a gated action (jam, engage, or other effect with a custody precondition), the
  operator can see whether the current confidence clears the weapons-quality threshold, per the
  pre-disabled-button pattern.
- Custody history is available for AAR replay: a facilitator or trainee can query what a cell's
  confidence in a track was at any prior decision point, and compare it against ground truth at
  that moment.

## System Behaviour

- **Custody confidence must be displayed as a continuous/decaying quantity, never a binary
  "tracked/untracked" flag.** On-demand decay tied to elapsed sim time and fresh collection events
  (per [`CLAUDE.md`](../../CLAUDE.md)'s `engine/custody.py` description) — the UI must reflect *how stale* a track's
  confidence is, not just whether one exists.
- **The weapons-quality gate must be visible before an operator attempts a gated action.** Any
  effect category with a custody precondition ([R115](../research/encyclopedia/R115-electronic-warfare-in-space-operations.md)-[R117](../research/encyclopedia/R117-directed-energy-and-kinetic-effects.md)) must expose, ahead of commitment,
  whether the current confidence clears that gate — consistent with the pre-disabled-button
  pattern ([FS-101](FS-101-mission-planning.md) §3, [DOM-007](../domains/DOM-007-human-factors-framework.md) §4).
- **Belief must stay visually distinguishable from ground truth.** Per [DOM-007](../domains/DOM-007-human-factors-framework.md) §4, custody
  confidence indicators (color, iconography) must never be conflatable with an assertion of
  ground-truth fact — this is the single most load-bearing UI rule in the entire fog-of-war
  pedagogy, independent of whether the backend already enforces the boundary correctly.
- **Custody history must be retrievable for after-action review.** [DOM-002](../domains/DOM-002-assessment-framework.md) §4's
  "belief-truth divergence" assessment dimension depends on being able to compare a cell's custody
  confidence at a decision point against ground truth at that same point — custody state must be a
  first-class, queryable part of the historical record, not a transient display-only value.
- **Doctrine differences live in data, not feature logic.** Per [DOM-009](../domains/DOM-009-doctrine-development-framework.md) §4, a vignette's SSN
  dispersion preset implies sparser or denser collection, but Custody Management's decay/display
  behavior must be uniform across vignettes; the doctrine difference lives in the data feeding it.

## Subsystem Responsibilities

The source document does not provide a per-subsystem breakdown. [`CLAUDE.md`](../../CLAUDE.md) names
`engine/custody.py` (`Track`, on-demand confidence decay, weapons-quality gate) and
`session/CellController` (fog-of-war filtering, per INT-0007) as the relevant components, but the
source document does not assign responsibilities to them in a formal table. Flagged as an Open
Question below.

## Interfaces Used

Per the verified mapping for FS-103: INT-0007 (CellController → Simulation Engine
Custody/TrackCatalog) — per `docs/design/05-interface-control-document.md`. The source document
does not itself cite ICD interface IDs; this is carried forward from the verified Related Interfaces
mapping (field 21).

## Data Model Changes

Not addressed in the source document — no existing content to carry forward. The source document
notes custody state must be a "first-class, queryable part of the historical record" for AAR
purposes, implying existing `EventLog`/`Snapshot` structures must capture it, but does not specify
schema changes. Flagged as an Open Question below.

## State Changes

- Confidence starts at some value when a track is first established (implied from collection
  events) and decays over elapsed sim time without fresh collection.
- The weapons-quality gate is a threshold state: below it, certain effect categories become
  unavailable; at or above it, they are gated-open.
- Custody history is a write-once append (AAR-queryable); confidence reads never mutate it.

## Error Handling

The source document does not enumerate error states. The implicit constraint: custody confidence
queries (for display or for AAR) must not themselves mutate confidence — only real collection
events and on-demand decay tied to actual elapsed sim time may change it (replay-safety constraint).

## Performance Considerations

- **Replay-safety.** Custody confidence queries (for display or for AAR) must not themselves mutate
  confidence — only the on-demand decay computation tied to actual elapsed sim time and fresh
  collection events may change it.
- **Human factors.** Belief/ground-truth legibility (§"System Behaviour" above) is named in
  [DOM-007](../domains/DOM-007-human-factors-framework.md) §4 as load-bearing for the entire console — this is not a styling choice.

## Security Considerations

Not addressed in the source document — no existing content to carry forward. The fog-of-war
boundary (a cell's TrackCatalog reflects only its own belief, never ground truth) is a security-
relevant invariant already enforced at the `CellController` layer ([ADR-0004](../architecture/adr/ADR-0004-fog-of-war-at-boundary.md)), but the source
document does not discuss it under this heading. Flagged as an Open Question below.

## Acceptance Criteria

Derived from the source document's capability requirements, restated as checkable conditions:

- Track confidence is displayed as a continuous value that decreases over elapsed sim time without
  fresh collection; binary "tracked/untracked" framing is not used.
- Before an operator can commit an action gated by weapons-quality custody, the console shows
  whether the current confidence meets the threshold.
- Custody confidence indicators are visually distinct from ground-truth assertions — a trainee
  cannot mistake a stale belief track for a confirmed ground-truth position.
- A past custody confidence value (at any replayed decision point) is queryable via AAR, including
  comparison against ground truth at that point.
- Vignette differences in SSN dispersion produce different collection volumes (and therefore
  different confidence trajectories) without altering the custody-decay or weapons-quality-gate logic.

## Verification Plan

The source document does not state a Verification Method per criterion. Test (automated) is implied
by the replay-safety constraint and the determinism invariant; the belief/ground-truth legibility
criterion is more naturally verified by Inspection or Demonstration. Flagged as an Open Question
below.

## Dependencies

[DOM-009](../domains/DOM-009-doctrine-development-framework.md) and [R105](../research/encyclopedia/R105-custody-theory.md) (per the existing metadata block's Dependencies field). [FS-104](FS-104-sda-tasking.md) and
[FS-105](FS-105-spacecraft-operations.md) are downstream consumers of this feature's output, not upstream dependencies of FS-103
itself. [DOM-002](../domains/DOM-002-assessment-framework.md) and [R104](../research/encyclopedia/R104-collection-management.md)/[R115](../research/encyclopedia/R115-electronic-warfare-in-space-operations.md)-[R117](../research/encyclopedia/R117-directed-energy-and-kinetic-effects.md) are noted as related topics.

## Risks

The source document does not state risks explicitly. The following are restated faithfully from
material the document discusses as constraints:

- If belief indicators are styled in a way that can be confused with ground-truth assertions, the
  entire fog-of-war pedagogy is undermined regardless of backend correctness — this is identified
  as the single most load-bearing UI rule in [DOM-007](../domains/DOM-007-human-factors-framework.md) §4.
- If custody state is stored only as a transient display value (not a first-class historical
  record), the AAR / assessment consumer ([FS-201](FS-201-competency-assessment.md)'s "belief-truth divergence" dimension) has
  no queryable data to operate on.

## Open Questions

- No FR-xxxx/NFR-xxxx in `docs/requirements/` explicitly cites FS-103; this is a traceability gap
  for Phase 8 review (MSTR-006 §7), not a deliberate non-applicability.
- The source document does not assign a per-subsystem Subsystem Responsibilities table; how
  `engine/custody.py` and `session/CellController` divide custody display and decay ownership is
  unresolved in this document.
- The source document does not address Data Model Changes; whether the historical custody record
  requires schema additions beyond existing `EventLog`/`Snapshot` structures is unresolved.
- The source document does not address Security Considerations beyond the fog-of-war boundary
  already established by ADR-0004; whether any additional access-control concern exists for
  custody history is unresolved.
- The source document does not state formal Verification Methods per criterion; Test/Inspection/
  Demonstration assignments are inferred from context, not stated in the source.

## Related ADRs

ADR-0013 (custody confidence decay and weapons-quality gate) —
`docs/architecture/adr/ADR-0013-custody-weapons-quality-gate.md`.

## Related Interfaces

INT-0007 (CellController → Simulation Engine Custody/TrackCatalog) — per
`docs/design/05-interface-control-document.md`.
