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

Both are produced by the `architecture-design-synthesis` skill
(`.claude/skills/architecture-design-synthesis/`).

[↑ Docs index](../INDEX.md) · [Documentation map](../master/MSTR-005-documentation-map.md) §3a

## 1. The global ladder (`GDS-00`…`GDS-10`)

| ID | Document | Path | Purpose | Merges from (existing doc) | Status |
|---|---|---|---|---|---|
| GDS-00 | Vision | `architecture/00-vision.md` | Project goals | `master/MSTR-001-program-vision.md` | ⛔ Planned (scaffold only) |
| GDS-01 | Concept of Operations | `architecture/01-concept-of-operations.md` | How users interact with the system | *(no direct counterpart identified — review `training/` and `build-spec/01` during authoring)* | ⛔ Planned (scaffold only) |
| GDS-02 | System Context | `architecture/02-system-context.md` | External systems and interfaces | `build-spec/01-context-and-scope.md` | ⛔ Planned (scaffold only) |
| GDS-03 | Architecture | `architecture/03-architecture.md` | High-level subsystem decomposition | `design/01-architecture-overview.md` | ⛔ Planned (scaffold only) |
| GDS-04 | Domain Model | `architecture/04-domain-model.md` | Core entities and relationships | `design/04-data-model.md` (entity/relationship portion) | ⛔ Planned (scaffold only) |
| GDS-05 | Functional Requirements | `architecture/05-functional-requirements.md` | The authoritative specification | `build-spec/02-requirements-and-operations.md` §5 | ⛔ Planned (scaffold only) |
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
top-to-bottom iteration the `architecture-design-synthesis` skill will run.

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
`research-doctrine-exercises`'s workflow step 3).

## Related

[`MSTR-005`](../master/MSTR-005-documentation-map.md) §3a/§4 (document shape, chain placement),
[`MSTR-006`](../master/MSTR-006-governance-principles.md) §4/§5/§6 (size discipline, metadata
block, conflict handling), [`features/feature-index.md`](../features/feature-index.md) (the next
stage in the chain), [`domains/INDEX.md`](../domains/INDEX.md) (the frameworks this tier draws
from).
