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

## 1. Purpose

Competency Assessment replaces the engine's current binary objective-flip success/failure signal
with a richer, rubric-based measurement of *how* a cell demonstrated the competency a vignette was
designed to exercise — per [DOM-002](../domains/DOM-002-assessment-framework.md) §3, a cell can flip an objective through luck or exploit
without ever forming a correct custody-based belief, and conversely can demonstrate excellent
tradecraft and still lose. This spec is the FS-201 capability [DOM-002](../domains/DOM-002-assessment-framework.md) and [DOM-005](../domains/DOM-005-validation-framework.md) both
explicitly require.

## 2. Scope

In scope: the six measurement dimensions ([DOM-002](../domains/DOM-002-assessment-framework.md) §4), the rubric-tier reporting model, and the
per-cell/per-exercise and longitudinal report surfaces. Out of scope: tooling to *author or adjust*
rubric tiers ([FS-202](FS-202-rubric-authoring.md), candidate), and multi-run/cohort export for instrument-grade research
([FS-301](FS-301-research-analytics.md)).

## 3. Capability requirements (per DOM-002 §8)

Per [DOM-002](../domains/DOM-002-assessment-framework.md) §8, this spec must, and does:

- **Enumerate which of the six dimensions it implements in its first iteration**, explicitly stating
  which are deferred and why. The six candidate dimensions ([DOM-002](../domains/DOM-002-assessment-framework.md) §4) are: custody quality,
  window discipline, resource economy, escalation discipline, belief-truth divergence, and
  time-to-decision. **First-iteration scope (this spec): custody quality, window discipline, and
  belief-truth divergence** — these three are derivable most directly from data the engine already
  and unambiguously produces (`Track` confidence history, `OrderSystem` rejection/`dry_run()` usage,
  AAR's `snapshot_at()` god-view/belief diff per [FS-107](FS-107-after-action-review.md)). **Deferred:** resource economy and
  escalation discipline (both need a vignette-specific resource/ROE *budget* baseline to score
  against meaningfully, which does not yet exist as structured data — candidate scope for a future
  vignette-schema addition); time-to-decision (needs a defined "OODA-loop tightness" reference
  baseline per [R208](../research/encyclopedia/R208-ooda-loops.md), not yet established).
- **Specify the rubric tiers per dimension.** Per [DOM-002](../domains/DOM-002-assessment-framework.md) §5, each dimension is reported on its
  own qualitative scale, not collapsed into a numeric average:
  - *Custody quality:* speculative / adequate / disciplined.
  - *Window discipline:* frequent-invalid-attempts / occasional / disciplined.
  - *Belief-truth divergence:* high-divergence-unaware / high-divergence-aware / low-divergence.
- **Specify where the report surfaces.** Per-cell per-exercise (the immediate debrief artifact,
  hosted as a facilitator-facing summary view) and longitudinally per-trainee across exercises in
  the training progression ([DOM-001](../domains/DOM-001-training-framework.md) §4) — both surfaces present the rubric, never a single
  leaderboard number, per [DOM-002](../domains/DOM-002-assessment-framework.md) §5.
- **State explicitly: no new gameplay mechanic.** This feature is a read-only analytics layer over
  existing engine state (eventlog, custody history, order log, AAR snapshots). A scoring computation
  must not mutate `WorldState` — consistent with [`MSTR-002`](../master/MSTR-002-architecture-principles.md) §5's replay-safety principle.

## 4. Assessment modes

Per [DOM-002](../domains/DOM-002-assessment-framework.md) §6, this spec supports (without requiring all three at once): **automated, in-engine**
(the §3 baseline, always available), **facilitator rubric** (a White Cell observer's qualitative
judgment, informed by but not limited to the automated dimensions, surfaced via [FS-106](FS-106-white-cell-dashboard.md)), and
**self-assessment / debrief reflection** (the AAR walkthrough itself, requiring no new engine
feature beyond [FS-107](FS-107-after-action-review.md)).

## 5. Validation discipline (per DOM-005 §7)

Per [DOM-005](../domains/DOM-005-validation-framework.md) §7, any quantitative claim this feature or its future Implementation Package makes
about what a dimension "means" must cite which [DOM-005](../domains/DOM-005-validation-framework.md) §5 validity check(s) (face validity, internal
consistency, sensitivity to manipulation) were applied, even informally — a metric that has only
passed face validity must be reported as such, never silently treated as fully validated. This spec
does not itself claim any of its three first-iteration dimensions have completed §5's checks; that
is an Implementation Package and ongoing-validation responsibility, not satisfied merely by writing
this document.

## 6. Non-goals

- No composite single score is computed (per [DOM-002](../domains/DOM-002-assessment-framework.md) §5's explicit rejection of forced numeric
  averaging across non-commensurable dimensions).
- No human-subjects research use is in scope here — that boundary belongs to [FS-301](FS-301-research-analytics.md)/[DOM-004](../domains/DOM-004-research-framework.md) §6.
- Rubric-tier *authoring* tooling (letting a facilitator define new tiers) is [FS-202](FS-202-rubric-authoring.md), not this spec.

## 7. Related Topics

[DOM-002](../domains/DOM-002-assessment-framework.md) (owning framework), [DOM-005](../domains/DOM-005-validation-framework.md) (validation discipline this spec must satisfy), [DOM-001](../domains/DOM-001-training-framework.md)
(longitudinal progression context), [R306](../research/encyclopedia/R306-operational-assessment.md) (the operational-assessment vocabulary this feature's
dimensions draw on), [R310](../research/encyclopedia/R310-effects-based-operations.md) (MOP/MOE caution applicable to any future effectiveness-scoring
dimension), [FS-107](FS-107-after-action-review.md) (belief-truth-divergence data source), [FS-103](FS-103-custody-management.md) (custody-quality data source),
[FS-202](FS-202-rubric-authoring.md) (candidate authoring tooling), [FS-301](FS-301-research-analytics.md) (downstream multi-run export consumer).
