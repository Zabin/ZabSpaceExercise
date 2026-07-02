# Architecture Decision Records (ADR) Index

Router for `docs/architecture/adr/`. Each `ADR-NNNN` records one architectural decision made in
`GDS-01` (Concept of Operations), `GDS-02` (System Context), `GDS-03` (Architecture), or the
research encyclopedia (`docs/research/encyclopedia/`) those three ground their decisions against.
Six of the first 29 (ADR-0024–0029) originally recorded a source document's Open Question rather
than a settled decision; all six have since been resolved by explicit project-owner decision — see
"Scope and method" below. Two further ADRs (ADR-0030–0031) were added in response to
[`reviews/strategic-review-2026-07.md`](../../reviews/strategic-review-2026-07.md); see
[`reviews/architecture-update.md`](../../reviews/architecture-update.md) for that review's full
disposition. Two more (ADR-0032–0033) were added 2026-07 to resolve conflicts a `requirements-
engineering` pass found between DOM-002/004 (Assessment/Research Frameworks) and ADR-0017/ADR-0029
— see [`reviews/requirements-domain-backfill-report.md`](../../reviews/requirements-domain-backfill-report.md).
**ADR-0033 is this corpus's first `Superseded` entry** (of `ADR-0029`) — see "Scope and method"
below for why that milestone matters.

[↑ Architecture index](../INDEX.md) · [Docs index](../../INDEX.md)

## Scope and method

This is a **record of decisions already present in the corpus, not a place new decisions are
invented**. Every ADR below traces to a specific section of GDS-01/02/03 (cited in its "Related"
section) or to a build-spec/01 §4 "Decision D-number" the GDS documents already restate. ADR-0024
through ADR-0029 originally traced to a source document's Open Question rather than a settled
decision and were marked `Status: Proposed`/`Deferred` with a "Decision" field stating plainly that
no decision had been made yet. Per the project owner's direct resolution of all six (captured via
`AskUserQuestion`), each now carries `Status: Accepted` and a concrete Decision/Rationale/
Consequences — several of which authorize a follow-up edit to another document, tracked in that
ADR's own "Consequences" section.

## Decisions

| ID | Title | Status |
|---|---|---|
| [ADR-0001](ADR-0001-layered-single-process-architecture.md) | Layered single-process architecture | Accepted |
| [ADR-0002](ADR-0002-deterministic-core.md) | Deterministic core | Accepted |
| [ADR-0003](ADR-0003-sessionapi-single-seam.md) | `SessionAPI` as the single seam out of the engine | Accepted |
| [ADR-0004](ADR-0004-fog-of-war-at-boundary.md) | Fog-of-war enforced at the session-layer boundary | Accepted |
| [ADR-0005](ADR-0005-plan-first-commanding.md) | Plan-first commanding model | Accepted |
| [ADR-0006](ADR-0006-substepped-clock.md) | Sub-stepped deterministic clock | Accepted |
| [ADR-0007](ADR-0007-content-as-data.md) | Content as data, not code | Accepted |
| [ADR-0008](ADR-0008-fastapi-browser-over-pyqt.md) | FastAPI + browser presentation (supersedes PyQt) | Accepted |
| [ADR-0009](ADR-0009-moderate-orbital-fidelity.md) | Moderate orbital fidelity (Keplerian + J2, sgp4) | Accepted |
| [ADR-0010](ADR-0010-mock-ssn-internal.md) | Mock SSN is internal, not external | Accepted |
| [ADR-0011](ADR-0011-six-access-channels.md) | Six access channels taxonomy | Accepted |
| [ADR-0012](ADR-0012-five-ds-cyber-exception.md) | Five-D's effect taxonomy with cyber exception | Accepted |
| [ADR-0013](ADR-0013-custody-weapons-quality-gate.md) | Custody confidence decay and weapons-quality gate | Accepted |
| [ADR-0014](ADR-0014-lazy-clock-rlock-multiplayer.md) | Server-authoritative lazy clock + per-session RLock | Accepted |
| [ADR-0015](ADR-0015-lan-trust-model.md) | LAN trust model: client-side cell selection | Accepted |
| [ADR-0016](ADR-0016-single-point-of-time-control.md) | Single point of time control | Accepted |
| [ADR-0017](ADR-0017-manual-adjudication.md) | Manual adjudication; no automated scoring in v1 | Accepted |
| [ADR-0018](ADR-0018-offline-first-runtime.md) | Offline-first runtime; Space-Track build-time-only | Accepted |
| [ADR-0019](ADR-0019-sizing-guideline-not-engine-cap.md) | Sizing guideline, not an engine-enforced cap | Accepted |
| [ADR-0020](ADR-0020-tech-stack.md) | Tech stack selection | Accepted |
| [ADR-0021](ADR-0021-ai-red-session-layer-feature.md) | AI-Red is a session-layer feature | Accepted |
| [ADR-0022](ADR-0022-save-file-ownership-split.md) | Save-file ownership split (session vs. content) | Accepted |
| [ADR-0023](ADR-0023-one-directional-dependency-graph.md) | One-directional subsystem dependency graph | Accepted |
| [ADR-0024](ADR-0024-ai-red-boundary-classification.md) | AI-Red stays permanently internal; epistemic parity is a tracked future-work gap | Accepted |
| [ADR-0025](ADR-0025-telemetry-scene-placement-split.md) | Pure render/diagnostic helpers are placed by whether they require cell identity | Accepted |
| [ADR-0026](ADR-0026-rlock-lan-scaling-ceiling.md) | The RLock design's stated ceiling is the existing ~16-participant LAN concurrency model | Accepted |
| [ADR-0027](ADR-0027-scenario-authoring-boundary.md) | The in-app vignette builder is a distinct boundary-crossing interaction | Accepted |
| [ADR-0028](ADR-0028-pyqt-build-spec-staleness.md) | `build-spec/03` §7.1/§7.2 rewritten to describe the shipped FastAPI + browser presentation | Accepted |
| [ADR-0029](ADR-0029-assessment-scoring-workflow-ownership.md) | Raw AAR/event-log access is sufficient for the assessment-designer stakeholder | **Superseded by ADR-0033** |
| [ADR-0030](ADR-0030-ai-determinism-doctrine.md) | AI-determinism doctrine: non-deterministic components stay outside `engine/` | Accepted |
| [ADR-0031](ADR-0031-governance-record-consistency.md) | Governance-record consistency: GDS-00 §7 correction; DOM-002/DOM-005 status gap acknowledged | Accepted |
| [ADR-0032](ADR-0032-descriptive-rubric-not-automated-scoring.md) | Descriptive rubric-tier reporting carved out of ADR-0017's "no automated... assessment mechanism" (amends ADR-0017) | Accepted |
| [ADR-0033](ADR-0033-dedicated-research-export-interface.md) | A dedicated multi-run/cohort research-export interface is authorized (supersedes ADR-0029) | Accepted |

ADR-0001 through ADR-0023 record decisions already settled and reflected in the shipped system at
the time this ADR set was first authored. ADR-0024 through ADR-0029 originally recorded questions
the source documents (GDS-01/02/03 and the architecture review) left genuinely open — each one
said so plainly in its own "Decision" field rather than inventing a resolution. The project owner
has since resolved all six via direct decisions (captured through `AskUserQuestion` and recorded in
each ADR's updated Decision/Rationale/Consequences). The distinction worth preserving for
traceability is not "settled vs. open" anymore, but *how* each was settled: ADR-0001–0023 were
already implicit in the shipped system when authored; ADR-0024–0029 required an explicit,
separately-dated project-owner decision, several of which (ADR-0024, ADR-0027, ADR-0028) authorize
concrete follow-up edits to other documents — see each ADR's "Consequences" section for what those
follow-ups are and whether they have been completed.

**ADR-0030 and ADR-0031** are a third category: neither a decision already implicit in the shipped
system nor a resolved Open Question, but a decision made *in direct response to an external
review* — [`reviews/strategic-review-2026-07.md`](../../reviews/strategic-review-2026-07.md)'s
recommendations R4 and R5 respectively (see [`reviews/architecture-update.md`](../../reviews/architecture-update.md)
for that review's full disposition of all 24 recommendations). ADR-0030 states a general rule
(non-deterministic components stay outside `engine/`) that was already true by construction of
ADR-0002/0003/0021 combined, made explicit to close a named assumption gap. ADR-0031 corrects one
stale governance-record statement (GDS-00 §7) and explicitly declines to paper over a second,
real gap (DOM-002/DOM-005 vs. FS-201/FS-301 status) rather than retrofitting it.

**ADR-0032 and ADR-0033** are a fourth category: the first two decisions in this corpus that amend
or supersede a prior ADR's own Decision text, rather than adding a new, independent decision.
Both arose from a `requirements-engineering` pass finding that `DOM-002`/`FS-201` and
`DOM-004`/`FS-301` — Feature Specifications this corpus's own Feature Catalog and Feature Review
had already flagged as gapped (`docs/feature-planning/05-feature-review.md` Finding F-01) —
directly conflicted with `ADR-0017` and `ADR-0029` respectively. The project owner resolved both,
asked directly per-conflict: `ADR-0032` **narrows** `ADR-0017` (a carve-out, not a reversal —
`ADR-0017` remains `Accepted` and its core "no composite score, no automated win/loss" prohibition
is unchanged); `ADR-0033` **supersedes** `ADR-0029` outright (the project owner chose to authorize
the dedicated research-export interface `ADR-0029` had previously rejected, rather than work around
it). `ADR-0033` is this corpus's first `Superseded` entry. Of 33 ADRs, 32 are `Accepted` and 1 is
`Superseded`.

## Related

[`architecture/01-concept-of-operations.md`](../01-concept-of-operations.md) (GDS-01),
[`architecture/02-system-context.md`](../02-system-context.md) (GDS-02),
[`architecture/03-architecture.md`](../03-architecture.md) (GDS-03),
[`research/encyclopedia/INDEX.md`](../../research/encyclopedia/INDEX.md),
[`build-spec/01-context-and-scope.md`](../../build-spec/01-context-and-scope.md) §4 (the
pre-existing Decision D1–D10 log several ADRs above restate or supersede),
[`reviews/architecture-review.md`](../../reviews/architecture-review.md) (source of every
unresolved-decision ADR's corroborating citations),
[`reviews/strategic-review-2026-07.md`](../../reviews/strategic-review-2026-07.md) and
[`reviews/architecture-update.md`](../../reviews/architecture-update.md) (source of ADR-0030–0031);
[`reviews/requirements-domain-backfill-report.md`](../../reviews/requirements-domain-backfill-report.md)
(source of ADR-0032–0033).
