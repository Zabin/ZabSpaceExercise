# Architecture Decision Records (ADR) Index

Router for `docs/architecture/adr/`. Each `ADR-NNNN` records one architectural decision already
made (or, where the source documents leave it genuinely open, explicitly not yet made) in
`GDS-01` (Concept of Operations), `GDS-02` (System Context), `GDS-03` (Architecture), or the
research encyclopedia (`docs/research/encyclopedia/`) those three ground their decisions against.

[↑ Architecture index](../INDEX.md) · [Docs index](../../INDEX.md)

## Scope and method

This is a **record of decisions already present in the corpus, not a place new decisions are
invented**. Every ADR below traces to a specific section of GDS-01/02/03 (cited in its "Related"
section) or to a build-spec/01 §4 "Decision D-number" the GDS documents already restate. Where a
source document states an Open Question rather than a settled decision, the corresponding ADR is
marked `Status: Proposed` or `Status: Deferred` and its "Decision" field states plainly that no
decision has been made — see ADR-0024 through ADR-0029.

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
| [ADR-0024](ADR-0024-ai-red-boundary-classification.md) | AI-Red's actor/boundary classification | Proposed (unresolved) |
| [ADR-0025](ADR-0025-telemetry-scene-placement-split.md) | `telemetry.py` vs. `scene.py` subsystem placement | Deferred (unresolved) |
| [ADR-0026](ADR-0026-rlock-lan-scaling-ceiling.md) | RLock/LAN-scaling contention ceiling | Deferred (unresolved) |
| [ADR-0027](ADR-0027-scenario-authoring-boundary.md) | Scenario-authoring workflow's boundary actor/interface | Proposed (unresolved) |
| [ADR-0028](ADR-0028-pyqt-build-spec-staleness.md) | PyQt build-spec staleness reconciliation | Deferred (unresolved) |
| [ADR-0029](ADR-0029-assessment-scoring-workflow-ownership.md) | Assessment/scoring stakeholder workflow ownership | Proposed (unresolved) |

ADR-0001 through ADR-0023 record decisions already settled and reflected in the shipped system.
ADR-0024 through ADR-0029 record questions the source documents (GDS-01/02/03 and the
architecture review) leave genuinely open — each one says so plainly in its own "Decision" field
rather than inventing a resolution.

## Related

[`architecture/01-concept-of-operations.md`](../01-concept-of-operations.md) (GDS-01),
[`architecture/02-system-context.md`](../02-system-context.md) (GDS-02),
[`architecture/03-architecture.md`](../03-architecture.md) (GDS-03),
[`research/encyclopedia/INDEX.md`](../../research/encyclopedia/INDEX.md),
[`build-spec/01-context-and-scope.md`](../../build-spec/01-context-and-scope.md) §4 (the
pre-existing Decision D1–D10 log several ADRs above restate or supersede),
[`reviews/architecture-review.md`](../../reviews/architecture-review.md) (source of every
unresolved-decision ADR's corroborating citations).
