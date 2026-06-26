# FS-301 — Research Analytics

> **Document ID:** FS-301
> **Version:** 1.0
> **Status:** ✅ Done *(spec only — the underlying capability remains a documented gap per [DOM-004](../domains/DOM-004-research-framework.md) §5;
> no Implementation Package exists yet, and any human-subjects element requires separate
> authorization + IRB/ethics process per [DOM-004](../domains/DOM-004-research-framework.md) §6)*
> **Dependencies:** [DOM-004](../domains/DOM-004-research-framework.md), [DOM-005](../domains/DOM-005-validation-framework.md) §7, [DOM-002](../domains/DOM-002-assessment-framework.md) §4
> **Referenced By:** [DOM-004](../domains/DOM-004-research-framework.md), [DOM-005](../domains/DOM-005-validation-framework.md), [DOM-002](../domains/DOM-002-assessment-framework.md)
> **Produces:** structured multi-run/cohort export of [FS-201](FS-201-competency-assessment.md)'s measurement dimensions
> **Feature Mapping:** FS-301 (this document)
> **Related Topics:** [FS-201](FS-201-competency-assessment.md) (the per-exercise instrument this feature exports at scale)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

## 1. Purpose

Research Analytics closes the gap [DOM-004](../domains/DOM-004-research-framework.md) §5 names explicitly: today, a researcher who wants to
use SpaceSim as an instrument-grade research apparatus (e.g., studying "does fog-of-war severity
affect escalation rate") has no purpose-built data-export or cohort-management layer and must script
directly against raw `eventlog`/`save` artifacts. FS-301 is the candidate-closing Feature
Specification, tagged per [DOM-004](../domains/DOM-004-research-framework.md) §8 as explicitly supporting instrument-grade research rather
than ordinary in-session play.

## 2. Scope

In scope: structured export of run-level data (the [DOM-002](../domains/DOM-002-assessment-framework.md) §4 six measurement dimensions, or
whichever subset [FS-201](FS-201-competency-assessment.md) implements) across many runs/cohorts, with condition-label metadata
(vignette, seed, experimental condition) attached. Out of scope: running or designing actual studies
(that remains the researcher's/institution's responsibility, governed by [DOM-004](../domains/DOM-004-research-framework.md) §6's ethics
boundary), and the per-exercise instrument itself ([FS-201](FS-201-competency-assessment.md)).

## 3. Capability requirements (per DOM-004 §8)

Per [DOM-004](../domains/DOM-004-research-framework.md) §8, this spec must, and does:

- **Tag itself as supporting DOM-004 §4/§5 instrument-grade research.** This export feature exists
  specifically because SpaceSim has the properties a research instrument needs — reproducibility
  (deterministic per-seed replay), full behavioral trace (eventlog), and a controlled-manipulation
  surface (vignette YAML, doctrine presets, Red AI parameters as data) — and a researcher needs a
  structured way to harvest that, not a generic feature for ordinary play.
- **State the export schema's relationship to DOM-002 §4's six measurement dimensions.** The export
  schema's per-run record is exactly [FS-201](FS-201-competency-assessment.md)'s per-exercise rubric output (whichever dimensions
  that spec's current iteration implements — see [FS-201](FS-201-competency-assessment.md) §3), plus run-identifying metadata
  (vignette ID, seed, condition label) that [FS-201](FS-201-competency-assessment.md) itself has no reason to carry for a single
  exercise but a multi-run export cannot omit.
- **Carry an explicit non-goal statement matching DOM-004 §6.** No human-subjects feature (e.g.
  collecting de-identified trainee performance across institutions) is in scope without separate
  authorization and the institution's own IRB/ethics process — this spec does not substitute for
  that process and any future Implementation Package derived from FS-301 must repeat this statement
  rather than assume it is settled.

## 4. Capability requirements (general)

- **Export must run across seeded Monte Carlo batches without relaxing engine determinism.** Per
  [DOM-005](../domains/DOM-005-validation-framework.md) §6, characterizing typical (not single-run) behavior means driving the engine across many
  seeds externally — never by introducing non-determinism inside `engine/`. An Implementation
  Package must specify "run N seeded simulations of vignette X, collect distribution of [metric],"
  never "relax determinism to sample variability."
- **Any quantitative claim derived from exported data must cite its DOM-005 §5 validity check.**
  Per [DOM-005](../domains/DOM-005-validation-framework.md) §7, a metric that has only passed face validity must be reported as such in any
  research output this feature enables — FS-301 does not itself elevate a metric's validity merely
  by making it exportable at scale.
- **Export must not duplicate [FS-201](FS-201-competency-assessment.md)'s computation.** This feature reads [FS-201](FS-201-competency-assessment.md)'s already-computed
  per-exercise rubric output and packages it for multi-run analysis; it does not reimplement
  dimension scoring.

## 5. Two distinct "research" activities — boundary statement

Per [DOM-004](../domains/DOM-004-research-framework.md) §3, this feature exists for **instrument-grade research** (using SpaceSim to study
human decision-making/training effectiveness), which is categorically distinct from **encyclopedia
authoring** (equipping coding agents with domain knowledge, owned by [`MSTR-007`](../master/MSTR-007-research-philosophy.md)). FS-301 must
not be confused with, or treated as a consumer of, the R100-R500 encyclopedia corpus — they serve
unrelated purposes despite both being called "research."

## 6. Non-goals

- No human-subjects research capability (cross-institution de-identified data collection, IRB-gated
  consent flows) is in scope — see §3's required non-goal statement.
- No statistical-analysis tooling beyond structured export is in scope; the actual analysis is the
  researcher's responsibility, using [R401](../research/encyclopedia/R401-experimental-design-and-controls.md)-[R413](../research/encyclopedia/R413-data-analysis-and-reporting.md)'s methods vocabulary as needed (this spec does not implement
  those methods).

## 7. Related Topics

[DOM-004](../domains/DOM-004-research-framework.md) (owning framework, the gap statement this spec closes), [DOM-005](../domains/DOM-005-validation-framework.md) (validation discipline any
exported-data claim must satisfy), [DOM-002](../domains/DOM-002-assessment-framework.md) §4 (the measurement dimensions this feature exports at
scale), [FS-201](FS-201-competency-assessment.md) (the per-exercise instrument this feature aggregates), [`MSTR-007`](../master/MSTR-007-research-philosophy.md) (the
unrelated encyclopedia-authoring "research" activity this spec must not be confused with).
