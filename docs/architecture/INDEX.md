# Architecture / Design Synthesis Index

Router for `docs/architecture/`. Two things live here, at two different granularities:

1. **`GDS-00`…`GDS-10`** — a single, global, top-to-bottom design-synthesis ladder for the whole
   project (Vision → Concept of Operations → System Context → Architecture → Domain Model →
   Functional Requirements → Non-functional Requirements → Data Model → UI Architecture → API
   Specification → Requirements Traceability Matrix). **Scaffolded now, content incomplete** — see
   §1 below for the gating rule.
2. **`ADS-xxx`** — the optional, per-capability-cluster Design Synthesis document (ten internal
   sections) defined in `MSTR-005` §3a, used when one capability cluster needs its own deep-dive
   synthesis even after the global ladder exists. Unchanged from the prior revision; see §2 below.

Both are produced by the `03-architecture-design-synthesis` skill
(`.claude/skills/03-architecture-design-synthesis/`).

> **This directory is now the single authoritative architecture/requirements source for the whole
> project, superseding `docs/build-spec/` in its entirety**, per `CLAUDE.md`'s "Authoritative
> source & reading order." This is a blanket declaration, not limited to levels whose merge gate
> has already closed (GDS-00–05) — it also covers GDS-06–10 below even though they are still
> scaffold-only: a not-yet-authored GDS level simply has no authoritative content yet, rather than
> the corresponding build-spec module "winning" by default. The §1 gating rule below (sequential,
> merge-gated *authoring* order) is a separate, still-binding process rule about how this ladder
> gets written — it is not the mechanism by which authority transfers; authority transferred to
> this directory as a whole already.

[↑ Docs index](../INDEX.md) · [Documentation map](../master/MSTR-005-documentation-map.md) §3a

## 1. The global ladder (`GDS-00`…`GDS-10`)

| ID | Document | Path | Purpose | Merges from (existing doc) | Status |
|---|---|---|---|---|---|
| GDS-00 | Vision | `architecture/00-vision.md` | Project goals | `master/MSTR-001-program-vision.md` | ✅ Authored — merge gate closed (MSTR-001 stays authoritative; GDS-00 is a cited derivative restatement) |
| GDS-01 | Concept of Operations | `architecture/01-concept-of-operations.md` | How users interact with the system | `build-spec/01-context-and-scope.md`, `build-spec/04` §11, `build-spec/05` §13–14, `training/05`, `training/07` (no single existing ConOps — net-new synthesis of scattered material) | ✅ Authored — merge gate closed (all source docs stay independently authoritative; GDS-01 is a consolidation layer above them) |
| GDS-02 | System Context | `architecture/02-system-context.md` | External systems and interfaces | `build-spec/01-context-and-scope.md` | ✅ Authored — merge gate closed (build-spec/01 stays authoritative; GDS-02 is a boundary-focused extraction) |
| GDS-03 | Architecture | `architecture/03-architecture.md` | High-level subsystem decomposition | `design/01-architecture-overview.md` | ✅ Authored — merge gate closed (design/01 and build-spec/03 §7-8 stay authoritative; GDS-03 is a subsystem-decomposition extraction restated against the as-built system) |
| GDS-04 | Domain Model | `architecture/04-domain-model.md` | Core entities and relationships | `design/04-data-model.md` (entity/relationship portion) | ✅ Authored — merge gate closed (design/04-data-model.md stays authoritative for the schema; GDS-04 is a conceptual extraction, the schema portion remains GDS-07's merge target) |
| GDS-05 | Functional Requirements | `architecture/05-functional-requirements.md` | The authoritative specification | `build-spec/02-requirements-and-operations.md` §5–6 | ✅ Authored — merge gate closed (build-spec/02 §5–6 superseded; GDS-05 is now authoritative — see its "Merge gate" section) |
| GDS-06 | Non-functional Requirements | `architecture/06-non-functional-requirements.md` | Performance, reliability, security, usability | `build-spec/04-nfr-milestones-and-risks.md` §9 | ⛔ Planned (scaffold only) |
| GDS-07 | Data Model | `architecture/07-data-model.md` | Persistent data structures | `design/04-data-model.md` (schema portion — same source file as GDS-04, different concern) | ⛔ Planned (scaffold only) |
| GDS-08 | UI Architecture | `architecture/08-ui-architecture.md` | Screens, navigation, workflows | `design/09-gui-principles.md` (+ `05-cell-interfaces.md`, `10-sda-3d-viewer.md`) | ⛔ Planned (scaffold only) |
| GDS-09 | API Specification | `architecture/09-api-specification.md` | Service boundaries and contracts | `design/07-api-and-networking.md` | ⛔ Planned (scaffold only) |
| GDS-10 | Requirements Traceability Matrix | `architecture/10-requirements-traceability-matrix.md` | Maps requirements to features, tests, and implementation | *(no existing counterpart — net-new; `ROADMAP.md` tracks documents, not requirement→test traceability)* | ⛔ Planned (scaffold only) |

### Gating rule (binding)

This ladder is **strictly sequential and gated**: `GDS-(N+1)` may not be started until `GDS-N` is
both (a) authored and (b) has finished merging in whatever existing-corpus content overlaps it
(the "Merges from" column above). The merge is not optional cleanup — it is part of what "done"
means for that level. Per the user's explicit instruction, this gate applies at every step of the
top-to-bottom iteration the `03-architecture-design-synthesis` skill will run.

**Progress:** GDS-00 through GDS-05 are authored with their merge gates closed (see their
Status cells above and each document's own "Merge gate" section for the recorded decision). GDS-05
is the first level whose merge gate **supersedes** rather than retains its source as authoritative
— see its own "Merge gate" section for why. GDS-06 (Non-functional Requirements) is the next level
to author.

Where a level's "Merges from" column says no counterpart was identified, that is not a free pass —
it means the authoring pass for that level must search the corpus itself before concluding there
is nothing to merge, and record the (possibly negative) finding in that document's own Open
Questions before the gate is considered closed.

This is new, separate content — it does not silently replace `MSTR-001`, `build-spec/`, or
`design/`. Those documents remain authoritative until a given `GDS-NN`'s merge step explicitly
folds their content in and updates their own `Status`/cross-references to point here. Until then,
treat any apparent disagreement between a `GDS-NN` stub and its existing counterpart as expected,
not a defect — the stub has no content yet.

## 2. Per-cluster `ADS-xxx` (unchanged)

`ADS-xxx` documents sit between **Domain + Research** and **Feature Specification** in the
traceability chain (`MSTR-005` §4):

```
DOM-xxx (domain framework) + R-xxx (research grounding)
        ↓
ADS-xxx (this directory) — architecture, domain model, requirements, constraints, risks, decisions
        ↓
FS-xxx (feature specification) → IMP-xxx (implementation package) → code → tests
```

Each `ADS-xxx` answers, for one capability cluster: what are the core concepts, which mechanics
are actually required, which candidate requirements conflict, what assumptions must be made
explicit, what the minimum viable shape is, and what is deferred.

`ADS-xxx` is **not required** for every feature — per `MSTR-005` §4, small/uncontested features can
skip straight to `FS-xxx`. It earns its place when a capability cluster has real design tension
the global ladder (§1) doesn't resolve at the system level.

**Document shape:** ten fixed sections per `MSTR-005` §3a: Executive Design Overview, System
Architecture, Domain Model, User Stories, Functional Requirements, Non-functional Requirements,
Constraints, Risks, Open Questions, Decision Log. Size discipline: ~8-15 pages equivalent
(`MSTR-006` §4); split into `ADS-xxxA`/`ADS-xxxB` rather than writing one oversized document.

| ID | Document | Capability cluster | Owning domain | Status |
|---|---|---|---|---|
| *(none yet)* | — | — | — | — |

No `ADS-xxx` has been authored yet. Add a row here (status `⛔ Planned`) before authoring a new
`ADS-xxx`, and mirror it in `ROADMAP.md`'s Architecture / Design Synthesis theme table, per the
index-before-content convention used elsewhere in this corpus (e.g.
`02-research-doctrine-exercises`'s workflow step 3).

## 3. Architecture Decision Records (`docs/architecture/adr/`)

A separate, flat record of individual architectural decisions extracted from GDS-01 (Concept of
Operations), GDS-02 (System Context), GDS-03 (Architecture), and the research encyclopedia —
distinct from both the sequential ladder in §1 and the per-cluster `ADS-xxx` in §2. Each
`ADR-NNNN` carries Decision ID, Title, Context, Decision, Alternatives Considered, Rationale,
Consequences, and a Status of `Accepted`, `Proposed`, or `Deferred`. See
[`adr/INDEX.md`](adr/INDEX.md) for the full list (33 ADRs as of this writing, 32 `Accepted` and 1
`Superseded`: 23 were already settled when first authored; 6 (ADR-0024–0029) originally recorded
Open Questions the ladder left genuinely open and were resolved afterward by explicit
project-owner decision; 2 (ADR-0030–0031) were added in direct response to
[`reviews/strategic-review-2026-07.md`](../reviews/strategic-review-2026-07.md) — see
[`reviews/architecture-update.md`](../reviews/architecture-update.md); 2 more (ADR-0032–0033) were
added to resolve conflicts a `04-requirements-engineering` pass found between `DOM-002`/`004` and
`ADR-0017`/`ADR-0029` — see [`reviews/requirements-domain-backfill-report.md`](../reviews/requirements-domain-backfill-report.md).
`ADR-0033` supersedes `ADR-0029`, this corpus's first `Superseded` entry).

## Related

[`MSTR-005`](../master/MSTR-005-documentation-map.md) §3a/§4 (document shape, chain placement),
[`MSTR-006`](../master/MSTR-006-governance-principles.md) §4/§5/§6 (size discipline, metadata
block, conflict handling), [`features/feature-index.md`](../features/feature-index.md) (the next
stage in the chain), [`domains/INDEX.md`](../domains/INDEX.md) (the frameworks this tier draws
from).
