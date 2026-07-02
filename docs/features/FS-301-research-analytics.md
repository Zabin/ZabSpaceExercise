# FS-301 — Research Analytics

> **Document ID:** FS-301
> **Version:** 1.0
> **Status:** ✅ Done *(spec only — the underlying capability remains a documented gap per [DOM-004](../domains/DOM-004-research-framework.md) §5;
> [IMP-301A](../implementations/IMP-301A-research-analytics.md) exists as a design-only package per `MSTR-006` §3 — it is not an
> implementation-authorizing document, and any human-subjects element requires separate
> authorization + IRB/ethics process per [DOM-004](../domains/DOM-004-research-framework.md) §6)*
> **Dependencies:** [DOM-004](../domains/DOM-004-research-framework.md), [DOM-005](../domains/DOM-005-validation-framework.md) §7, [DOM-002](../domains/DOM-002-assessment-framework.md) §4
> **Referenced By:** [DOM-004](../domains/DOM-004-research-framework.md), [DOM-005](../domains/DOM-005-validation-framework.md), [DOM-002](../domains/DOM-002-assessment-framework.md), [IMP-301A](../implementations/IMP-301A-research-analytics.md)
> **Produces:** structured multi-run/cohort export of [FS-201](FS-201-competency-assessment.md)'s measurement dimensions
> **Feature Mapping:** FS-301 (this document)
> **Related Topics:** [FS-201](FS-201-competency-assessment.md) (the per-exercise instrument this feature exports at scale)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `feature-specification` skill's 20-field template; it supersedes this file's prior ad hoc structure while retaining its existing Document ID, status, and metadata per MSTR-006 §5.*

## Feature ID

FS-301

## Title

Research Analytics

## Purpose

Research Analytics closes the gap [DOM-004](../domains/DOM-004-research-framework.md) §5 names explicitly: a researcher who wants to use
SpaceSim as an instrument-grade research apparatus (e.g., studying "does fog-of-war severity affect
escalation rate") currently has no purpose-built data-export or cohort-management layer and must
script directly against raw `eventlog`/`save` artifacts. FS-301 is the candidate-closing Feature
Specification, tagged per [DOM-004](../domains/DOM-004-research-framework.md) §8 as explicitly supporting instrument-grade research rather
than ordinary in-session play. The export feature exists because SpaceSim has the properties a
research instrument needs — reproducibility (deterministic per-seed replay), full behavioral trace
(eventlog), and a controlled-manipulation surface (vignette YAML, doctrine presets, Red AI
parameters as data).

## Scope

In scope: structured export of run-level data (the [DOM-002](../domains/DOM-002-assessment-framework.md) §4 six measurement dimensions, or
whichever subset [FS-201](FS-201-competency-assessment.md) implements) across many runs/cohorts, with condition-label metadata
(vignette, seed, experimental condition) attached.

Out of scope: running or designing actual studies (the researcher's/institution's responsibility,
governed by [DOM-004](../domains/DOM-004-research-framework.md) §6's ethics boundary); the per-exercise instrument itself ([FS-201](FS-201-competency-assessment.md)); and
statistical-analysis tooling beyond structured export (analysis is the researcher's responsibility,
using [R401](../research/encyclopedia/R401-experimental-design-and-controls.md)–[R413](../research/encyclopedia/R413-data-analysis-and-reporting.md)'s methods vocabulary).

**Two distinct "research" activities — boundary statement:** Per [DOM-004](../domains/DOM-004-research-framework.md) §3, this feature exists
for **instrument-grade research** (using SpaceSim to study human decision-making/training
effectiveness), which is categorically distinct from **encyclopedia authoring** (equipping coding
agents with domain knowledge, owned by [MSTR-007](../master/MSTR-007-research-philosophy.md)). FS-301 must not be confused with, or
treated as a consumer of, the R100–R500 encyclopedia corpus — they serve unrelated purposes despite
both being called "research."

## Requirements Implemented

None identified — the FR-xxxx/NFR-xxxx requirements corpus (`docs/requirements/`) contains no
explicit citation of this Feature ID. This is a traceability gap, not a deliberate
non-applicability; closing it is Phase 8 traceability-review work (MSTR-006 §7), not something this
rewrite may resolve by inference.

## User Workflows

- A researcher configures a batch run: selects a vignette, a range of seeds, and an experimental
  condition label. The engine executes N seeded simulations of that vignette and collects the
  distribution of each measurement dimension ([FS-201](FS-201-competency-assessment.md)'s rubric output per run).
- The researcher exports the resulting per-run records as structured data (each record includes
  the vignette ID, seed, condition label, and the per-dimension rubric results from [FS-201](FS-201-competency-assessment.md)).
- The researcher uses the exported data in their own analysis tooling; SpaceSim does not provide
  the statistical-analysis step.

## System Behaviour

- **Export must run across seeded Monte Carlo batches without relaxing engine determinism.** Per
  [DOM-005](../domains/DOM-005-validation-framework.md) §6, characterizing typical (not single-run) behavior means driving the engine across
  many seeds externally — never by introducing non-determinism inside `engine/`. An Implementation
  Package must specify "run N seeded simulations of vignette X, collect distribution of [metric],"
  never "relax determinism to sample variability."
- **Export must read FS-201's already-computed rubric output, not reimplement dimension scoring.**
  The per-run record is exactly [FS-201](FS-201-competency-assessment.md)'s per-exercise rubric output (whichever dimensions
  that spec's current iteration implements), plus run-identifying metadata (vignette ID, seed,
  condition label) that [FS-201](FS-201-competency-assessment.md) itself has no reason to carry for a single exercise.
- **Any quantitative claim derived from exported data must cite its DOM-005 §5 validity check.**
  Per [DOM-005](../domains/DOM-005-validation-framework.md) §7, a metric that has only passed face validity must be reported as such in any
  research output this feature enables — FS-301 does not itself elevate a metric's validity merely
  by making it exportable at scale.
- **No human-subjects research capability is in scope.** Per [DOM-004](../domains/DOM-004-research-framework.md) §6, collecting
  de-identified trainee performance across institutions, IRB-gated consent flows, and similar
  human-subjects features are explicitly out of scope without separate authorization and the
  institution's own IRB/ethics process. Any future Implementation Package derived from FS-301 must
  repeat this statement.

## Subsystem Responsibilities

The source document does not provide a per-subsystem breakdown. The export feature reads from
[FS-201](FS-201-competency-assessment.md)'s computed rubric output and the engine's `Simulation`/`SavedSession` structures (which
already support seeded replay per [`CLAUDE.md`](../../CLAUDE.md)'s `engine/simulation.py` description). The source
document does not assign responsibilities to named subsystems in a formal table. Flagged as an Open
Question below.

## Interfaces Used

The source document does not cite ICD interface IDs for this feature. The export reads from
[FS-201](FS-201-competency-assessment.md)'s output (which has no explicit ICD interface defined) and drives the engine via
existing seeded-replay mechanisms. No named ICD interface covers the research-export boundary.
Flagged as an Open Question below.

## Data Model Changes

Not addressed in the source document — no existing content to carry forward. The per-run export
record schema (vignette ID, seed, condition label, per-dimension rubric results) is implied by the
feature's description but not formally specified. Flagged as an Open Question below.

## State Changes

- A batch run drives the engine through N seeded simulations sequentially (or in any order the
  batch runner controls), collecting one export record per run.
- Each run produces a new [FS-201](FS-201-competency-assessment.md) rubric result as part of the run's session output.
- No state is mutated in the engine beyond normal per-run session state, which is discarded
  between runs (each run starts from a clean seeded initial state).

## Error Handling

- An export batch must not introduce non-determinism between runs — each seeded run must be
  independently reproducible given the same vignette ID and seed.
- The source document does not enumerate other failure modes for the batch export.

## Performance Considerations

- **Determinism across seeded Monte Carlo batches.** Per [DOM-005](../domains/DOM-005-validation-framework.md) §6, variability is sampled by
  running many seeds, never by introducing non-determinism within a run — this is an architectural
  constraint inherited from the engine's load-bearing determinism invariant (ADR-0002).
- **Offline-first.** Batch runs must not require network access (per ADR-0018's offline-first
  runtime principle); Space-Track TLE data is build-time-only, not run-time.

## Security Considerations

Not addressed in the source document beyond the human-subjects boundary. No human-subjects data
(cross-institution de-identified trainee records, IRB-gated consent) is in scope. The source
document does not discuss export-file access controls or data sensitivity. Flagged as an Open
Question below.

## Acceptance Criteria

Derived from the source document's capability requirements, restated as checkable conditions:

- A batch run of N seeded simulations of vignette X produces N per-run export records, each
  containing: vignette ID, seed, condition label, and the FS-201 rubric output for that run.
- The export reads FS-201's computed output; it does not reimplement dimension scoring.
- No non-determinism is introduced inside `engine/` to produce variability — variability is sampled
  by varying the seed across runs.
- No human-subjects capability (cross-institution data collection, IRB-gated flows) is present.
- Each exported metric's validity-check level (per DOM-005 §5) is disclosed alongside the metric
  in any output that claims quantitative meaning.

## Verification Plan

The source document does not state a Verification Method per criterion. Test (automated) is implied
for the no-non-determinism constraint, consistent with the determinism property test (the Phase-1
gate). Inspection is likely appropriate for the no-scoring-reimplementation criterion. Flagged as
an Open Question below.

## Dependencies

[DOM-004](../domains/DOM-004-research-framework.md), [DOM-005](../domains/DOM-005-validation-framework.md) §7, [DOM-002](../domains/DOM-002-assessment-framework.md) §4 (per the existing metadata block's Dependencies field).
[FS-201](FS-201-competency-assessment.md) is a functional prerequisite (the instrument whose output this feature exports at
scale) — it is named in `Produces` / `Related Topics` but not in the metadata block's Dependencies
field.

## Risks

- If the export re-implements any of FS-201's dimension scoring rather than reading FS-201's
  already-computed output, the two could diverge — a risk named explicitly in the source
  document's capability requirements.
- If any human-subjects capability is added to an Implementation Package without separate
  authorization and IRB/ethics process, it violates [DOM-004](../domains/DOM-004-research-framework.md) §6's explicit non-goal statement.
- Any Implementation Package that introduces non-determinism inside `engine/` to simulate
  variability would violate the load-bearing determinism invariant (ADR-0002).

## Open Questions

- No FR-xxxx/NFR-xxxx in `docs/requirements/` explicitly cites FS-301; this is a traceability gap
  for Phase 8 review (MSTR-006 §7), not a deliberate non-applicability.
- The source document does not assign a per-subsystem Subsystem Responsibilities table.
- The per-run export record schema (vignette ID, seed, condition label, per-dimension rubric
  results) is implied but not formally specified; whether it requires a new Domain Model entity or
  extends an existing export format is unresolved.
- No ICD interface explicitly names the research-export boundary; whether a new INT-xxxx interface
  is required is unresolved for Phase 8.
- The source document does not address export-file access controls or data sensitivity.
- The source document does not state formal Verification Methods per criterion.

## Related ADRs

None identified — no ADR in `docs/architecture/adr/` explicitly names the research-export or
instrument-grade research capability as a settled decision point. ADR-0002 (deterministic core)
applies as a constraint on the batch-run mechanism, but does not name FS-301 specifically.

## Related Interfaces

None identified — no ICD interface in `docs/design/05-interface-control-document.md` explicitly
names the research-export or instrument-grade research boundary. This is a traceability gap for
Phase 8 review if a named interface is required for the IMP-301A implementation design.
