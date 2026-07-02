# IMP-201A — Competency Assessment: Rubric Computation Design

> **Document ID:** IMP-201A
> **Version:** 1.0
> **Status:** ⛔ Planned (design only; no code exists)
> **Dependencies:** [FS-201](../features/FS-201-competency-assessment.md)
> **Referenced By:** [IMP-301A](IMP-301A-research-analytics.md) (the forward-design export package that would consume this one's output)
> **Produces:** the rubric output [FS-301](../features/FS-301-research-analytics.md)'s forward-design export would aggregate
> **Feature Mapping:** FS-201
> **Related Topics:** [`spacesim/engine/custody.py`](../../spacesim/engine/custody.py), [`spacesim/engine/orders.py`](../../spacesim/engine/orders.py), [`spacesim/session/aar.py`](../../spacesim/session/aar.py)

[↑ Implementation index](INDEX.md) · [Docs index](../INDEX.md)

> **Superseded.** This document's content has been re-derived and re-published under the canonical
> `docs/implementation/packages/` tier as
> [**IP-2010**](../implementation/packages/IP-2010-competency-assessment.md). This file is retained
> for historical reference and is not deleted, but [`IP-2010`](../implementation/packages/IP-2010-competency-assessment.md)
> is the document of record going forward — see
> [`docs/implementation/00-master-build-plan.md`](../implementation/00-master-build-plan.md)
> §"Relationship to the prior `docs/implementations/` corpus." **This remains a forward-design,
> not-yet-implemented, not-yet-authorized package under its new ID (MSTR-006 §3) — superseding it
> does not change its authorization status.**

## 1. Situation

**Forward design.** Unlike IMP-101A through IMP-107A, this package describes a capability that
does **not** exist in `spacesim/` today. Per [DOM-002](../domains/DOM-002-assessment-framework.md) and FS-201's own status line, automated
rubric scoring is ⛔ Planned — the engine currently exposes only the binary objective-flip signal
this spec is meant to replace. Per [`MSTR-006`](../master/MSTR-006-governance-principles.md) §3, this document is a design, not an
authorization to write code: a separate, explicit user go-ahead is required before any of this is
implemented.

## 2. What already exists vs. what is missing

FS-201 §3 scopes the first iteration to three dimensions chosen specifically because their inputs
already exist as unambiguous engine data:

| Dimension | Existing data source | Status |
|---|---|---|
| Custody quality | `Track.current_confidence()`/`is_weapons_quality()` (`custody.py:45`, `:53`, documented in [IMP-103A](IMP-103A-custody-management.md) §2-3) | Data exists; no scoring function reads it for rubric purposes |
| Window discipline | `OrderSystem._validate()`/`dry_run()` rejection strings (`orders.py:323`, `:136`, documented in [IMP-101A](IMP-101A-mission-planning.md) §2, [IMP-102A](IMP-102A-command-scheduling.md) §2) | Data exists (rejection reasons are already returned per-attempt); no aggregation across attempts exists |
| Belief-truth divergence | `aar.state_at()` + `scene.build_scene()` composed at a shared `seq` (documented in [IMP-107A](IMP-107A-after-action-review.md) §3) | The diff mechanism exists; no quantification of *how much* divergence, or a tier threshold, exists |

The two **deferred** dimensions (resource economy, escalation discipline) and time-to-decision are
explicitly out of this package's design scope per FS-201 §3 — they require a vignette-schema
addition (a resource/ROE budget baseline) or an OODA-tightness reference baseline ([R208](../research/encyclopedia/R208-ooda-loops.md)) that
does not yet exist, and inventing one is a separate, larger design decision this package does not
make.

## 3. Proposed shape (not yet implemented)

A new read-only module, analogous in spirit to `session/aar.py` (pure functions over replayed
state, no `WorldState` mutation, per FS-201 §3's "no new gameplay mechanic" / `MSTR-002` §5
replay-safety requirement) would expose, per cell per exercise:

```
score_custody_quality(mgr, cell) -> "speculative" | "adequate" | "disciplined"
score_window_discipline(mgr, cell) -> "frequent-invalid-attempts" | "occasional" | "disciplined"
score_belief_truth_divergence(mgr, cell) -> "high-divergence-unaware" | "high-divergence-aware" | "low-divergence"
```

each returning one of FS-201 §3's named tiers — never a numeric average across dimensions (FS-201
§6's explicit non-goal). A plausible (not yet validated) sketch of each:

- **Custody quality**: sample `current_confidence()` across the exercise's `Track`s at the moments
  the cell actually acted on them (e.g., at each `engage`/`observe` order's issue time, via the
  existing eventlog) rather than at arbitrary intervals — a cell that consistently acted only on
  high-confidence tracks scores `disciplined`; one that frequently acted on low-confidence or
  uncharacterized tracks scores `speculative`.
- **Window discipline**: count `dry_run()`/`issue()` rejection attempts (already returned as
  `(bool, str)` per [IMP-101A](IMP-101A-mission-planning.md) §4) against successful issuances over the exercise; a high
  ratio of rejected-for-window-reasons attempts suggests `frequent-invalid-attempts`.
- **Belief-truth divergence**: at each decision point in `aar.report()`'s `DECISION_KINDS`
  timeline ([IMP-107A](IMP-107A-after-action-review.md) §4), compare the cell's `build_scene()` belief against ground truth at
  that `seq`; a cell whose belief matched truth closely scores `low-divergence`, while a cell that
  acted confidently on badly wrong belief scores `high-divergence-unaware` (vs.
  `high-divergence-aware`, which would require some signal the cell *recognized* the gap — itself
  an open design question, §5).

## 4. Report surfaces (not yet implemented)

FS-201 §3 requires two surfaces, both presenting the rubric — never a single leaderboard number:

- **Per-cell/per-exercise**: a facilitator-facing summary, naturally hosted as an extension of
  [FS-106](../features/FS-106-white-cell-dashboard.md)'s dashboard (consistent with [IMP-106A](IMP-106A-white-cell-dashboard.md) — this would be additive to White's
  existing surface, not a new authority tier).
- **Longitudinal per-trainee**: requires persisting rubric output across multiple exercises tied to
  a trainee identity — no such identity/persistence model exists in `spacesim/` today (sessions are
  ephemeral unless explicitly saved via `SessionManager.save_state()`); this package does not design
  that persistence layer, only flags it as a dependency a future IMP-201B (or similar) would need
  to resolve.

## 5. Open design questions

- **"Aware" vs. "unaware" divergence** (§3's belief-truth tier) needs a signal that the cell
  *recognized* its belief was wrong — e.g., did the cell re-task a sensor after an unexpected
  outcome? This is not derivable from `aar.py` alone as currently built and needs further design
  before implementation.
- **Validation status**: per FS-201 §5 (DOM-005 §7), none of the three sketches in §3 above have
  undergone any DOM-005 §5 validity check (face validity, internal consistency, sensitivity to
  manipulation) — they are proposals, not validated metrics, and must be reported as such if and
  when implemented.
- **Resource economy / escalation discipline dimensions**: deferred per FS-201 §3; would need a
  vignette-schema addition (a resource/ROE budget baseline) this package does not design.
- **Rubric-tier authoring**: out of scope per FS-201 §6 ([FS-202](../features/FS-202-rubric-authoring.md), itself an unauthorized
  candidate FS with no IMP package per [`MSTR-006`](../master/MSTR-006-governance-principles.md) §3).

## 6. Non-goals (restated from FS-201)

No composite single score; no human-subjects research use (that boundary belongs to
[FS-301](../features/FS-301-research-analytics.md)/[IMP-301A](IMP-301A-research-analytics.md)); no rubric-tier authoring tooling.

## 7. Related Topics

[FS-201](../features/FS-201-competency-assessment.md) (the spec this designs toward), [IMP-103A](IMP-103A-custody-management.md) (custody data source), [IMP-102A](IMP-102A-command-scheduling.md)/[IMP-101A](IMP-101A-mission-planning.md)
(window-discipline data source), [IMP-107A](IMP-107A-after-action-review.md) (belief-truth-divergence mechanism), [IMP-301A](IMP-301A-research-analytics.md) (the
downstream forward-design export consumer), [IMP-106A](IMP-106A-white-cell-dashboard.md) (the dashboard this package's per-exercise
surface would extend).
