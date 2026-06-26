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

## 1. Purpose

After Action Review is the read-only replay/scrub/branch-compare debrief instrument: the capability
by which a completed (or in-progress) exercise's full eventlog becomes a teaching artifact rather
than a discarded record. It is named directly in [DOM-001](../domains/DOM-001-training-framework.md), [DOM-003](../domains/DOM-003-white-cell-framework.md), and [DOM-002](../domains/DOM-002-assessment-framework.md) §6 —
three independent framing documents all depend on the same underlying instrument for distinct
purposes (training delivery, facilitation, self-assessment).

## 2. Scope

In scope: scrubbing/replaying the eventlog, branch comparison (diverging a replay from a chosen
point to compare alternate decisions), and snapshotting both god-view and per-cell belief state at
any point in the timeline. Out of scope: the White-only trigger controls for invoking AAR (hosted in
[FS-106](FS-106-white-cell-dashboard.md)), and any quantitative scoring derived from AAR data ([FS-201](FS-201-competency-assessment.md)).

## 3. Capability requirements

- **AAR must be read-only with respect to the live session.** Per [`CLAUDE.md`](../../CLAUDE.md)'s description of
  `aar.py`, replay/scrub/`snapshot_at()` must never mutate `WorldState` — this mirrors the
  replay-safety contract `dry_run()`/`scene.py` already establish for plan-time and rendering paths.
- **Belief-vs-truth comparison must be a first-class capability, not an afterthought.** The
  god-view-vs-belief-view diff at a given `snapshot_at()` point is explicitly named in [DOM-002](../domains/DOM-002-assessment-framework.md) §4
  as the data source for the "belief-truth divergence" assessment dimension — AAR must expose this
  diff queryably, not just render a single combined view.
- **Branch comparison must let a facilitator or trainee examine "what if" without altering the
  canonical record.** A compared branch is itself a replay artifact, not a new committed session
  state.
- **AAR must double as a self-assessment instrument with no new engine feature beyond itself.** Per
  [DOM-002](../domains/DOM-002-assessment-framework.md) §6, "self-assessment / debrief reflection" is one of three assessment modes and requires
  only facilitation guidance ([DOM-003](../domains/DOM-003-white-cell-framework.md)) on top of this spec — AAR's design should not assume it
  is purely a facilitator tool; a trainee walking their own decision points is an intended use.
- **Must state, in its Educational Value section, which objective class(es) it serves.** Per
  [DOM-001](../domains/DOM-001-training-framework.md) §7: AAR's educational value is reflective learning — letting a trainee or facilitator
  examine a decision against both the trainee's own belief state at the time and the ground truth
  that belief diverged from, which is a distinct competency from in-the-moment operation (served by
  [FS-105](FS-105-spacecraft-operations.md)).

## 4. Non-goals

- AAR does not compute or report any rubric score itself — it is the data substrate [FS-201](FS-201-competency-assessment.md) reads,
  not the assessment layer.
- AAR does not provide live-session intervention (that is White Cell's clock/inject authority,
  [FS-106](FS-106-white-cell-dashboard.md)) — AAR's scope is the historical record, even when used during a still-running exercise.

## 5. Non-functional requirements

- **Replay-safety** (§3, above) is the dominant non-functional constraint for this feature.
- **Human factors.** Per [DOM-007](../domains/DOM-007-human-factors-framework.md) §4's belief-vs-truth legibility principle, AAR's god-view-vs-belief
  diff display must keep the two visually distinct at every timeline point shown, not just at the
  final state.

## 6. Related Topics

[DOM-001](../domains/DOM-001-training-framework.md) (training-delivery framing), [DOM-003](../domains/DOM-003-white-cell-framework.md) (facilitation framing, White-only trigger controls),
[DOM-002](../domains/DOM-002-assessment-framework.md) §6 (self-assessment framing), [FS-106](FS-106-white-cell-dashboard.md) (White-only controls that invoke this instrument),
[FS-201](FS-201-competency-assessment.md) (the assessment layer reading AAR's belief-truth-divergence data).
