# Feature Planning — Index

[↑ Docs index](../INDEX.md) · [Requirements](../requirements/03-requirements-traceability-matrix.md) ·
[Features (FS-xxx specs)](../features/feature-index.md)

Output of the `05-feature-decomposition` skill run against the approved requirements baseline
(`docs/requirements/01`/`02`/`03`). **Not the same artifact as `docs/features/`**: this directory's
`FEAT-xxxx` rows are planning-grain catalog entries; `docs/features/`'s `FS-xxx` documents are full
downstream Feature Specifications. See `05-feature-review.md`'s mapping note for how the two relate
and for the row-by-row reconciliation between the 11 existing `FS-xxx` documents and this catalog's
36 `FEAT-xxxx` rows.

| Doc | Content |
|---|---|
| [`01-release-plan.md`](01-release-plan.md) | Bucket assignment (legacy tranche labels Prototype/MVP/Release 1/Release 2, all released as R1.0, plus Future; new buckets are named by release ID, e.g. R2.0) for all 48 Features *(as of 2026-10-23)*, with justification, plus the **Release state**: all buckets released, GO declared by the owner 2026-11-01. Release record: [REV-REL-004](../reviews/release-assessment-release-candidate-10.md). |
| [`02-epic-catalog.md`](02-epic-catalog.md) | 11 Epics (`EP-1000`–`EP-11000`), one per top-level requirements-baseline grouping. |
| [`03-feature-catalog.md`](03-feature-catalog.md) | 48 Features (`FEAT-1100`–`FEAT-12300`), full template, tracing every baselined FR/NFR leaf (106 FR + 48 NFR, 2026-10-23) exactly once. |
| [`04-feature-dependency-graph.md`](04-feature-dependency-graph.md) | Mermaid dependency diagram, critical path, blocking Features, parallel-build opportunities, 2 resolved circular-citation findings. |
| [`05-feature-review.md`](05-feature-review.md) | Findings (oversized/undersized/missing/duplicate Features, traceability gaps) and the reconciliation of "36 today" vs. the ~50–80 expected once upstream requirements/domain work closes the gap. |
| [`06-release-2-plan.md`](06-release-2-plan.md) | **Release 2.0 planning proposal** (2026-11-01, not authorized work): inventory of every candidate item after Release 1.0 (bugs, defects, backlog, candidate requirements, review findings), recommended theme, Must/Should/Could/Out scope, milestones M0–M3, quality gates, branching strategy, owner decisions and proposed intake rows. |

**Status:** complete for the approved FR/NFR baseline as of 2026-10-17 (full inventory sweep, run #151; first pass 2026-07). Candidate
Requirements (CR-01–18, CNFR-01–07) and the July-2026 Strategic Review's Future Concepts/Gaps
(FC-01–15, GAP-01–13) are deliberately not yet represented — see `05-feature-review.md` for what
upstream work that requires.
