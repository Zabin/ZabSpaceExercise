# Research Encyclopedia — Index

[↑ Research index](../INDEX.md) · [Docs index](../../INDEX.md) · [MSTR-007 Research Philosophy](../../master/MSTR-007-research-philosophy.md)

A coding-agent-oriented knowledge corpus, distinct in purpose from the existing
[`research/01-07`](../INDEX.md) doctrine/physics primers — see
[`MSTR-007`](../../master/MSTR-007-research-philosophy.md) §2 and §5 for the exact relationship.
Six tiers; each has its own index enumerating every topic with ID, scope, dependencies, and status.

| Tier | Subject | Index | Status |
|---|---|---|---|
| R100 | Space Operations Foundation | [R100-index.md](R100-index.md) | ✅ Done (36/36 topics) |
| R200 | Decision Sciences | [R200-index.md](R200-index.md) | ✅ Done (14/14 topics) |
| R300 | Military Analysis | [R300-index.md](R300-index.md) | ✅ Done (20/20 topics) |
| R400 | Research Methods | [R400-index.md](R400-index.md) | 🚧 Incomplete |
| R500 | Future Operations | [R500-index.md](R500-index.md) | 🚧 Incomplete |
| R600 | Training Pedagogy & Instructional Design | [R600-index.md](R600-index.md) | ⛔ Scaffolded 2026-07-04 (0/8 topics) — grounds the training corpus elevated to co-equal product (MSTR-001 §2); owned by `02-research-training-pedagogy` |

**Authoring order:** per [`MSTR-007`](../../master/MSTR-007-research-philosophy.md) §6, each
tier's index is authored before its topic documents, and [R100](R100-index.md) (most directly tied
to the simulator's actual subsystems) is the priority tier for full authoring. Bulk-authoring of
[R200](R200-index.md)-[R500](R500-index.md) was authorized by the user ("all tiers").

**Re-audited against MSTR-007 (original finding, now remediated for R100).** All 68 topics across
the five tiers were previously marked "✅ Done" / "fully authored," but a structural and citation
re-check found two systemic defects the original pass missed:

1. **§2 Scope section** (MSTR-007 §4.2) was missing from most topics.
2. **Citation compliance** — `### Sources` subsections, inline URLs, and `Last Reviewed` /
   `Primary Sources Consulted` frontmatter per
   [`docs/research/10-sources-and-methodology.md`](../10-sources-and-methodology.md) were absent
   from most topics.

**R100 is now fully remediated and closed**: all 30 topics (R101-R130) carry §2 Scope, inline
citations, a `### Sources` subsection per `##` section, and `Last Reviewed`/`Primary Sources
Consulted` frontmatter. Per MSTR-007 §7's coverage test, two named `engine/` subsystems
(`telemetry.py`, `recovery.py`) were found to have no R100 topic an implementer extending them
would read first — closed by fully-authored R121/R122. A later code-vs-encyclopedia re-audit found
`engine/sigint.py` similarly ungrounded — closed by R129 — and `engine/orders.py`'s `downlink`
action verb lacked a dedicated topic — closed by R130. See [R100-index.md](R100-index.md) for the
full per-topic detail.

**R200 is now fully remediated and closed (2026-07-02)**: all 14 topics (R201-R214) carry §2 Scope,
inline citations to the seminal source for each formalism (Bayes & Price 1763, Shannon 1948, Simon
1955, Tversky & Kahneman 1974, Boyd's *A Discourse on Winning and Losing*, von Neumann & Morgenstern
1944, and others — see [R200-index.md](R200-index.md) for the full per-topic source list), a
`### Sources` subsection per cited section, and `Last Reviewed`/`Primary Sources Consulted`
frontmatter.

**R300 is now also fully closed (2026-07-02, 20/20 topics)**: R314's 11 unverified doctrine-citation
placeholders (blocked in an earlier session by no `WebFetch` network access) were verified against
live URLs, correcting one factual error found in the process (JP 3-13.4 was misdated in the
placeholder draft); the tier's last `⛔ Planned` gap, R320 (Commercial Space Actors and Strategic
Ambiguity, closing GAP-03), was authored — see [R300-index.md](R300-index.md) for detail.

[R400](R400-index.md)-[R500](R500-index.md) still carry the original two defects (missing §2 Scope,
no citations) — see each tier's own index file for status. None of the seven-section *content*
quality (Purpose/Concepts/Operational Context/Implementation Guidance/Feature Mapping/Related
Topics) is in question for those tiers either — this is a structural-completeness and sourcing
finding, not a rewrite of the substance. Phase 4 (Feature Specifications) should not treat R400/R500
as a finished dependency until their remediation pass lands.
