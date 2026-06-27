# Research Encyclopedia — Index

[↑ Research index](../INDEX.md) · [Docs index](../../INDEX.md) · [MSTR-007 Research Philosophy](../../master/MSTR-007-research-philosophy.md)

A coding-agent-oriented knowledge corpus, distinct in purpose from the existing
[`research/01-07`](../INDEX.md) doctrine/physics primers — see
[`MSTR-007`](../../master/MSTR-007-research-philosophy.md) §2 and §5 for the exact relationship.
Five tiers; each has its own index enumerating every topic with ID, scope, dependencies, and status.

| Tier | Subject | Index | Status |
|---|---|---|---|
| R100 | Space Operations Foundation | [R100-index.md](R100-index.md) | 🚧 Incomplete |
| R200 | Decision Sciences | [R200-index.md](R200-index.md) | 🚧 Incomplete |
| R300 | Military Analysis | [R300-index.md](R300-index.md) | 🚧 Incomplete |
| R400 | Research Methods | [R400-index.md](R400-index.md) | 🚧 Incomplete |
| R500 | Future Operations | [R500-index.md](R500-index.md) | 🚧 Incomplete |

**Authoring order:** per [`MSTR-007`](../../master/MSTR-007-research-philosophy.md) §6, each
tier's index is authored before its topic documents, and [R100](R100-index.md) (most directly tied
to the simulator's actual subsystems) is the priority tier for full authoring. Bulk-authoring of
[R200](R200-index.md)-[R500](R500-index.md) was authorized by the user ("all tiers").

**Re-audited against MSTR-007 and found incomplete (this revision).** All 68 topics across the
five tiers were previously marked "✅ Done" / "fully authored," but a structural and citation
re-check found two systemic defects the original pass missed:

1. **66 of 68 topics omit the mandatory §2 Scope section** (MSTR-007 §4.2) — only R101 and R102
   have one; every other document jumps from "1. Purpose" straight to a "2. Concepts" section.
2. **All 68 topics are entirely uncited** — zero `### Sources` subsections, zero inline URLs, zero
   YAML `last_reviewed`/`primary_sources_consulted` frontmatter, anywhere in the tier. The
   pre-existing `research/01-07` primers comply with the corpus-wide citation convention in
   [`docs/research/10-sources-and-methodology.md`](../10-sources-and-methodology.md) (48-204
   citations each); the encyclopedia tier never went through that pass despite the methodology
   file stating it "applies to every file in this corpus" (`docs/research/`).

Per MSTR-007 §7's coverage test, two named `engine/` subsystems (`telemetry.py`, `recovery.py`)
were also found to have no R100 topic an implementer extending them would read first — tracked as
new `⛔ Planned` rows R121/R122 in [R100-index.md](R100-index.md) rather than silently left out.

See each tier's own index file for the per-topic detail. None of the seven-section *content*
quality (Purpose/Concepts/Operational Context/Implementation Guidance/Feature Mapping/Related
Topics) is in question — this is a structural-completeness and sourcing finding, not a rewrite of
the substance. Phase 4 (Feature Specifications) should not treat this tier as a finished
dependency until the remediation pass lands.
