# FS-107 — After Action Review

> **Document ID:** FS-107
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [DOM-001](../domains/DOM-001-training-framework.md), [DOM-003](../domains/DOM-003-white-cell-framework.md), [DOM-002](../domains/DOM-002-assessment-framework.md) §6
> **Referenced By:** [DOM-001](../domains/DOM-001-training-framework.md), [DOM-003](../domains/DOM-003-white-cell-framework.md), [DOM-002](../domains/DOM-002-assessment-framework.md), [IMP-107A](../implementations/IMP-107A-after-action-review.md)
> **Produces:** the replay/snapshot surface [FS-201](FS-201-competency-assessment.md)'s "belief-truth divergence" dimension reads from
> **Feature Mapping:** FS-107 (this document)
> **Related Topics:** [FS-106](FS-106-white-cell-dashboard.md) (White-only controls that invoke this instrument), [FS-201](FS-201-competency-assessment.md)
> (downstream assessment consumer)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template; it supersedes this file's prior ad hoc structure while retaining its existing Document ID, status, and metadata per MSTR-006 §5.*

## Feature ID

FS-107

## Title

After Action Review

## Purpose

After Action Review is the read-only replay/scrub/branch-compare debrief instrument: the capability
by which a completed (or in-progress) exercise's full eventlog becomes a teaching artifact rather
than a discarded record. Named directly in [DOM-001](../domains/DOM-001-training-framework.md), [DOM-003](../domains/DOM-003-white-cell-framework.md), and [DOM-002](../domains/DOM-002-assessment-framework.md) §6 — three
independent framing documents all depend on the same underlying instrument for distinct purposes
(training delivery, facilitation, self-assessment). AAR's educational value is reflective learning:
letting a trainee or facilitator examine a decision against both the trainee's own belief state at
the time and the ground truth that belief diverged from — a distinct competency from in-the-moment
operation ([FS-105](FS-105-spacecraft-operations.md)).

## Scope

In scope: scrubbing/replaying the eventlog, branch comparison (diverging a replay from a chosen
point to compare alternate decisions), and snapshotting both god-view and per-cell belief state at
any point in the timeline. Out of scope: the White-only trigger controls for invoking AAR (hosted
in [FS-106](FS-106-white-cell-dashboard.md)), and any quantitative scoring derived from AAR data ([FS-201](FS-201-competency-assessment.md)).

## Requirements Implemented

None identified — the FR-xxxx/NFR-xxxx requirements corpus (`docs/requirements/`) contains no
explicit citation of this Feature ID. This is a traceability gap, not a deliberate
non-applicability; closing it is Phase 8 traceability-review work (MSTR-006 §7), not something this
rewrite may resolve by inference.

## User Workflows

- A facilitator (or trainee) scrubs the exercise timeline, observing how both cells' belief states
  and ground truth evolved over the course of the session.
- At any timeline point, the user takes a snapshot of god-view and per-cell belief state —
  queryable for comparison against ground truth at that same moment.
- The user branches from a chosen timeline point, replaying forward from that point with alternate
  decisions to compare "what if" outcomes; the branch does not alter the canonical session record.
- A trainee uses the AAR instrument independently (no facilitator required) to walk through their
  own decision points, observing where their belief diverged from ground truth and why.
- [FS-201](FS-201-competency-assessment.md)'s "belief-truth divergence" dimension reads from the god-view/belief diff at each
  `snapshot_at()` point — AAR exposes this diff queryably, not just as a single combined view.

## System Behaviour

- **AAR must be read-only with respect to the live session.** Per [`CLAUDE.md`](../../CLAUDE.md)'s description of
  `aar.py`, replay/scrub/`snapshot_at()` must never mutate `WorldState` — mirroring the replay-
  safety contract `dry_run()`/`scene.py` already establish for plan-time and rendering paths.
- **Belief-vs-truth comparison must be a first-class capability, not an afterthought.** The
  god-view-vs-belief-view diff at a given `snapshot_at()` point is explicitly named in [DOM-002](../domains/DOM-002-assessment-framework.md) §4
  as the data source for the "belief-truth divergence" assessment dimension — AAR must expose this
  diff queryably, not just render a single combined view.
- **Branch comparison must let a facilitator or trainee examine "what if" without altering the
  canonical record.** A compared branch is itself a replay artifact, not a new committed session
  state.
- **AAR must double as a self-assessment instrument with no new engine feature beyond itself.** Per
  [DOM-002](../domains/DOM-002-assessment-framework.md) §6, self-assessment / debrief reflection requires only facilitation guidance ([DOM-003](../domains/DOM-003-white-cell-framework.md))
  on top of this spec — AAR's design must not assume it is purely a facilitator tool.
- **Belief/ground-truth legibility at every timeline point.** Per [DOM-007](../domains/DOM-007-human-factors-framework.md) §4, the god-view-vs-belief
  diff display must keep the two visually distinct at every timeline point shown, not just the
  final state.

## Subsystem Responsibilities

The source document does not provide a per-subsystem breakdown. [`CLAUDE.md`](../../CLAUDE.md) names `session/aar.py`
(`replay/scrub/branch-compare + snapshot_at`) as the component implementing this feature, consuming
`engine/eventlog.py` and `engine/world.py` via INT-0014. The source document does not assign
responsibilities in a formal table. Flagged as an Open Question below.

## Interfaces Used

Per the verified mapping for FS-107: INT-0014 (Session Layer AAR/Replay → Simulation Engine
EventLog/WorldState) — per `docs/design/05-interface-control-document.md`. The source document does
not itself cite ICD interface IDs; this is carried forward from the verified Related Interfaces
mapping (field 21).

## Data Model Changes

Not addressed in the source document — no existing content to carry forward. The AAR instrument
reads existing `EventLog` and `WorldState`/`Snapshot` structures; whether it requires new Domain
Model entities is unresolved. Flagged as an Open Question below.

## State Changes

- A replay/scrub operation moves a logical "playhead" forward or backward through the eventlog
  without mutating `WorldState` in the live session — it reads snapshots, it does not write them.
- A branch creates a new replay context diverged from the canonical timeline at a chosen point; it
  does not modify the original session's `EventLog`.
- A `snapshot_at()` call captures the god-view/belief-view state at a given timeline point as a
  queryable read-only artifact.

## Error Handling

- Replay/scrub/snapshot operations must not produce any `WorldState` mutation — a system that
  produces a side effect in response to a read-only AAR query is a defect, not a recoverable error.
- The source document does not enumerate other failure modes for AAR operations.

## Performance Considerations

- **Replay-safety** is the dominant non-functional constraint for this feature — every AAR
  operation must be provably non-mutating.
- **Human factors.** The god-view/belief diff display must keep the two visually distinct at every
  timeline point — consistent with [DOM-007](../domains/DOM-007-human-factors-framework.md) §4's load-bearing legibility principle.

## Security Considerations

Not addressed in the source document — no existing content to carry forward. The AAR instrument
provides god-view access (ground truth + both cells' belief states); access must be limited to
White Cell per the LAN trust model (ADR-0015). The source document does not go beyond this
implicit constraint. Flagged as an Open Question below.

## Acceptance Criteria

Derived from the source document's capability requirements, restated as checkable conditions:

- Replay/scrub/`snapshot_at()` operations produce no `WorldState` mutation.
- The god-view/belief-view diff at any `snapshot_at()` point is queryable as a distinct output,
  not only as a combined rendering.
- A branch comparison diverges from a chosen timeline point without altering the canonical
  `EventLog`.
- A trainee can use the AAR instrument without facilitator involvement to review their own decision
  points.
- God-view and per-cell belief-view are visually distinct at every timeline point in the replay,
  not just the final state.

## Verification Plan

The source document does not state a Verification Method per criterion. Test (automated) is implied
for the no-mutation constraint (replay-safety), consistent with the project's determinism property
test mandate. Demonstration is likely the appropriate method for belief/ground-truth legibility and
trainee self-use. Flagged as an Open Question below.

## Dependencies

[DOM-001](../domains/DOM-001-training-framework.md), [DOM-003](../domains/DOM-003-white-cell-framework.md), [DOM-002](../domains/DOM-002-assessment-framework.md) §6 (per the existing metadata block's Dependencies field).
[FS-106](FS-106-white-cell-dashboard.md) (White-only controls that invoke this instrument) and [FS-201](FS-201-competency-assessment.md) (the assessment layer
reading AAR's belief-truth-divergence data) are adjacent features, not upstream dependencies of
FS-107 itself.

## Risks

- If the AAR instrument is treated as purely a facilitator tool (and self-assessment use is not
  designed for from the start), [DOM-002](../domains/DOM-002-assessment-framework.md) §6's stated self-assessment mode is silently excluded —
  the source document explicitly names this as a design requirement, not an afterthought.
- If `snapshot_at()` or branch operations are implemented with any `WorldState` mutation (even as a
  "temporary" side effect), the live-session replay-safety invariant is violated.

## Open Questions

- No FR-xxxx/NFR-xxxx in `docs/requirements/` explicitly cites FS-107; this is a traceability gap
  for Phase 8 review (MSTR-006 §7), not a deliberate non-applicability.
- No ADR in `docs/architecture/adr/` explicitly names AAR as a settled decision point; whether any
  ADR should be added to record AAR's replay-safety as an architectural decision (distinct from the
  general replay-safety principle already in `MSTR-002`/ADR-0002) is unresolved.
- The source document does not assign a per-subsystem Subsystem Responsibilities table.
- The source document does not address Data Model Changes; whether new entities beyond existing
  `EventLog`/`Snapshot` structures are needed is unresolved.
- The source document does not address Security Considerations beyond the implicit White-only access
  requirement.
- The source document does not state formal Verification Methods per criterion.

## Related ADRs

None identified — no ADR in `docs/architecture/adr/` explicitly names After Action Review as a
settled decision point. The general replay-safety principle is grounded in ADR-0002 (deterministic
core) and restated in MSTR-002, but neither specifically addresses AAR. This is a traceability gap
for future ADR authoring if the AAR replay-safety contract is judged to warrant an explicit ADR.

## Related Interfaces

INT-0014 (Session Layer AAR/Replay → Simulation Engine EventLog/WorldState) — per
`docs/design/05-interface-control-document.md`.
