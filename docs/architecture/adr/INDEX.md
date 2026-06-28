# Architecture Decision Records (ADR) Index

Router for `docs/architecture/adr/`. Each `ADR-NNNN` records one architectural decision made in
`GDS-01` (Concept of Operations), `GDS-02` (System Context), `GDS-03` (Architecture), or the
research encyclopedia (`docs/research/encyclopedia/`) those three ground their decisions against.
Six of the 29 (ADR-0024–0029) originally recorded a source document's Open Question rather than a
settled decision; all six have since been resolved by explicit project-owner decision — see
"Scope and method" below.

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
| [ADR-0029](ADR-0029-assessment-scoring-workflow-ownership.md) | Raw AAR/event-log access is sufficient for the assessment-designer stakeholder | Accepted |

ADR-0001 through ADR-0023 record decisions already settled and reflected in the shipped system at
the time this ADR set was first authored. ADR-0024 through ADR-0029 originally recorded questions
the source documents (GDS-01/02/03 and the architecture review) left genuinely open — each one
said so plainly in its own "Decision" field rather than inventing a resolution. The project owner
has since resolved all six via direct decisions (captured through `AskUserQuestion` and recorded in
each ADR's updated Decision/Rationale/Consequences), so all 29 ADRs are now `Accepted`. The
distinction worth preserving for traceability is not "settled vs. open" anymore, but *how* each was
settled: ADR-0001–0023 were already implicit in the shipped system when authored; ADR-0024–0029
required an explicit, separately-dated project-owner decision, several of which (ADR-0024,
ADR-0027, ADR-0028) authorize concrete follow-up edits to other documents — see each ADR's
"Consequences" section for what those follow-ups are and whether they have been completed.

## Related

[`architecture/01-concept-of-operations.md`](../01-concept-of-operations.md) (GDS-01),
[`architecture/02-system-context.md`](../02-system-context.md) (GDS-02),
[`architecture/03-architecture.md`](../03-architecture.md) (GDS-03),
[`research/encyclopedia/INDEX.md`](../../research/encyclopedia/INDEX.md),
[`build-spec/01-context-and-scope.md`](../../build-spec/01-context-and-scope.md) §4 (the
pre-existing Decision D1–D10 log several ADRs above restate or supersede),
[`reviews/architecture-review.md`](../../reviews/architecture-review.md) (source of every
unresolved-decision ADR's corroborating citations).
