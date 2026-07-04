# IMP-301A — Research Analytics: Multi-Run Export Design

> **Document ID:** IMP-301A
> **Version:** 1.0
> **Status:** ⛔ Planned (design only; no code exists)
> **Dependencies:** [FS-301](../features/FS-301-research-analytics.md), [IMP-201A](IMP-201A-competency-assessment.md) (the per-exercise rubric output this package would aggregate)
> **Referenced By:** none yet
> **Produces:** structured multi-run/cohort export of FS-201's measurement dimensions
> **Feature Mapping:** FS-301
> **Related Topics:** [`spacesim/session/aar.py`](../../spacesim/session/aar.py) (the `export_csv` precedent), [`spacesim/engine/simulation.py`](../../spacesim/engine/simulation.py) (seeded replay)

[↑ Implementation index](INDEX.md) · [Docs index](../INDEX.md)

> **Superseded.** This document's content has been re-derived and re-published under the canonical
> `docs/implementation/packages/` tier as
> [**IP-3010**](../implementation/packages/IP-3010-research-analytics.md). This file is retained for
> historical reference and is not deleted, but [`IP-3010`](../implementation/packages/IP-3010-research-analytics.md)
> is the document of record going forward — see
> [`docs/implementation/00-master-build-plan.md`](../implementation/00-master-build-plan.md)
> §"Relationship to the prior `docs/implementations/` corpus." **Update (2026-07-04): `IP-3010`
> has since been authorized (MSTR-006 §3, run #9) and implemented (`COMPLETE`, run #10) — see
> `IP-3010`'s own header for current status; this historical file is not otherwise updated.**

## 1. Situation

**Forward design.** No purpose-built multi-run export layer exists in `spacesim/` today — per
[DOM-004](../domains/DOM-004-research-framework.md) §5's documented gap statement, a researcher currently has to script directly against
raw `eventlog`/`save` artifacts. This package is a design, not an authorization to implement, per
[`MSTR-006`](../master/MSTR-006-governance-principles.md) §3. It is also explicitly downstream of [IMP-201A](IMP-201A-competency-assessment.md): FS-301 §4's
"export must not duplicate FS-201's computation" requirement means this package cannot be
meaningfully designed in detail (what is the per-run record's schema?) until IMP-201A's rubric
output shape is at least sketched — which §2 of that package does, and this package treats as its
input contract.

## 2. What already exists vs. what is missing

The closest existing precedent is `aar.export_csv(rep)` (`aar.py:120`, documented in
[IMP-107A](IMP-107A-after-action-review.md) §6) — a single-run, three-section CSV export (META/TIMELINE/OBJECTIVES). It
demonstrates the export *pattern* (flatten an in-memory report object to CSV) but is explicitly
single-run and pre-dates any rubric dimension — it exports objective flips, not FS-201's tiers.
The deterministic seeded-replay machinery (`engine/simulation.py`'s `replay()`, the `_seed` field
on `Simulation`) already provides exactly the reproducibility property FS-301 §3 names as the
reason this feature is worth building (DOM-004 §4/§5 instrument-grade research requires
reproducibility, full behavioral trace, and a controlled-manipulation surface — all three already
exist; only the harvesting layer is missing).

## 3. Proposed shape (not yet implemented)

A batch-runner, external to `engine/` (consistent with FS-301 §4's "never relax determinism inside
engine/ to sample variability" requirement — Monte Carlo variation comes from varying the `seed`
argument to `Simulation`/`SessionManager` across many runs, not from any non-determinism inside the
engine itself):

```
run_batch(vignette_id, seeds: list[int], condition_label: str, n_steps_or_until) -> list[RunRecord]
```

where each `RunRecord` would be exactly IMP-201A's per-exercise rubric output (whichever
dimensions that package's eventual implementation covers — custody quality, window discipline,
belief-truth divergence, per FS-201 §3's first iteration) **plus** run-identifying metadata FS-201
itself has no reason to carry for a single exercise: `vignette_id`, `seed`, `condition_label`. This
mirrors FS-301 §3's explicit schema requirement and deliberately does not invent any scoring logic
of its own — `run_batch()` would call whatever IMP-201A's scoring functions are (once they exist),
once per seeded run, and collect results; it does not recompute or duplicate them (FS-301 §4 bullet
3).

A CSV/JSON export of `list[RunRecord]` would extend `aar.export_csv()`'s pattern (one row per run,
one column per dimension/metadata field) rather than inventing a new export format — consistent
with §2's observation that the flattening pattern already exists and should be reused, not
reinvented.

## 4. The two boundary statements this package must repeat (per FS-301 §3, §5)

Per FS-301 §3 bullet 3 and §5, any future implementation derived from this package must restate,
not assume settled:

- **No human-subjects research capability is in scope** without separate authorization and the
  institution's own IRB/ethics process (DOM-004 §6). This package's `run_batch()` sketch operates
  only on simulated cells (Red/Blue AI or facilitator-run exercises already in progress) — it does
  not propose any mechanism for collecting de-identified trainee performance data across
  institutions, and any future package that adds such a mechanism must trigger that authorization
  process explicitly, not inherit it implicitly from this one.
- **This is not the R100-R500 encyclopedia corpus's "research."** Per DOM-004 §3 and FS-301 §5,
  instrument-grade research (what this package designs toward) and encyclopedia authoring
  ([`MSTR-007`](../master/MSTR-007-research-philosophy.md)) are unrelated activities that happen to share the word "research" — this
  package's `run_batch()`/`RunRecord` design has no relationship to, and does not consume, the
  encyclopedia documents this same documentation corpus also produces.

## 5. Open design questions

- **Schema depends entirely on IMP-201A landing first.** Until IMP-201A's rubric functions exist
  (currently ⛔ Planned, not authorized), this package's `RunRecord` schema is necessarily
  provisional — it can only be as concrete as IMP-201A §3's sketch, which is itself unvalidated.
- **Validity-check citation discipline** (FS-301 §4 bullet 2, DOM-005 §7): any researcher using
  this export's output to make a quantitative claim must cite which DOM-005 §5 validity check(s)
  were applied to each dimension — this package does not and cannot satisfy that requirement on the
  researcher's behalf; it can only ensure the export carries enough metadata (which dimension, from
  which IMP-201A version) for the researcher to make that citation honestly.
- **Cohort management** (multiple trainees/sessions grouped by experimental condition) is named in
  FS-301 §2 scope but not designed here in any detail — `condition_label` in §3's sketch is a
  placeholder for whatever grouping scheme a real study would need; this package does not propose a
  cohort data model.
- **No statistical-analysis tooling** is in scope (FS-301 §6) — `R401`-`R413`'s methods vocabulary
  is the researcher's reference, not something this package implements.

## 6. Non-goals (restated from FS-301)

No human-subjects research capability; no statistical-analysis tooling beyond structured export;
no duplication of FS-201's/IMP-201A's scoring computation.

## 7. Related Topics

[FS-301](../features/FS-301-research-analytics.md) (the spec this designs toward), [IMP-201A](IMP-201A-competency-assessment.md) (the upstream per-exercise instrument this
package aggregates and cannot precede), [IMP-107A](IMP-107A-after-action-review.md) (the `export_csv` precedent), [`spacesim/engine/simulation.py`](../../spacesim/engine/simulation.py)
(seeded replay, the reproducibility property this feature depends on).
