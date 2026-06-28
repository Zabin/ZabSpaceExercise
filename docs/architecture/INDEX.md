# Architecture / Design Synthesis Index

Router for `docs/architecture/` — the **Design Synthesis** tier (`ADS-xxx`). This directory was
empty and its purpose unresolved as of the Jun 2026 Phase 6-8 review (`ROADMAP.md` theme
"Phase 6-8 review" open question, resolved by this revision per `MSTR-005` §3a/§4 and
`MSTR-006` §4). It now has a defined ID scheme, document shape, and producer.

[↑ Docs index](../INDEX.md) · [Documentation map](../master/MSTR-005-documentation-map.md) §3a

## What lives here

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
explicit, what the minimum viable shape is, and what is deferred. It is produced by the
`architecture-design-synthesis` skill (`.claude/skills/architecture-design-synthesis/`).

`ADS-xxx` is **not required** for every feature — per `MSTR-005` §4, small/uncontested features can
skip straight to `FS-xxx`. It earns its place when a capability cluster has real design tension:
conflicting requirements, multiple plausible architectures, or load-bearing assumptions that need
to be recorded before a Feature Specification can commit to a shape.

## Document shape

Ten fixed sections per `MSTR-005` §3a: Executive Design Overview, System Architecture, Domain
Model, User Stories, Functional Requirements, Non-functional Requirements, Constraints, Risks,
Open Questions, Decision Log. Same required metadata block as every other document in this corpus
(`MSTR-006` §5). Size discipline: ~8-15 pages equivalent (`MSTR-006` §4); split into `ADS-xxxA`/
`ADS-xxxB` rather than writing one oversized document.

## Current corpus

| ID | Document | Capability cluster | Owning domain | Status |
|---|---|---|---|---|
| *(none yet)* | — | — | — | — |

No `ADS-xxx` has been authored yet — this tier was structurally defined by this revision but no
capability cluster has been run through the skill. Add a row here (status `⛔ Planned`) before
authoring a new `ADS-xxx`, and mirror it in `ROADMAP.md`'s Architecture / Design Synthesis theme
table, per the index-before-content convention used elsewhere in this corpus (e.g.
`research-doctrine-exercises`'s workflow step 3).

## Related

[`MSTR-005`](../master/MSTR-005-documentation-map.md) §3a/§4 (document shape, chain placement),
[`MSTR-006`](../master/MSTR-006-governance-principles.md) §4/§5/§6 (size discipline, metadata
block, conflict handling), [`features/feature-index.md`](../features/feature-index.md) (the next
stage in the chain), [`domains/INDEX.md`](../domains/INDEX.md) (the frameworks `ADS-xxx` draws
from).
