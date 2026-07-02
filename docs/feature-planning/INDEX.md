# Feature Planning — Index

[↑ Docs index](../INDEX.md) · [Requirements](../requirements/03-requirements-traceability-matrix.md) ·
[Features (FS-xxx specs)](../features/feature-index.md)

Output of the `feature-decomposition` skill run against the approved requirements baseline
(`docs/requirements/01`/`02`/`03`). **Not the same artifact as `docs/features/`**: this directory's
`FEAT-xxxx` rows are planning-grain catalog entries; `docs/features/`'s `FS-xxx` documents are full
downstream Feature Specifications. See `05-feature-review.md`'s mapping note for how the two relate
and for the row-by-row reconciliation between the 11 existing `FS-xxx` documents and this catalog's
36 `FEAT-xxxx` rows.

| Doc | Content |
|---|---|
| [`01-release-plan.md`](01-release-plan.md) | Bucket assignment (Prototype/MVP/Release 1/Release 2/Future) for all 36 Features, with justification. |
| [`02-epic-catalog.md`](02-epic-catalog.md) | 9 Epics (`EP-1000`–`EP-9000`), one per top-level requirements-baseline grouping. |
| [`03-feature-catalog.md`](03-feature-catalog.md) | 36 Features (`FEAT-1100`–`FEAT-9100`), full template, tracing every baselined FR/NFR leaf exactly once. |
| [`04-feature-dependency-graph.md`](04-feature-dependency-graph.md) | Mermaid dependency diagram, critical path, blocking Features, parallel-build opportunities, 2 resolved circular-citation findings. |
| [`05-feature-review.md`](05-feature-review.md) | Findings (oversized/undersized/missing/duplicate Features, traceability gaps) and the reconciliation of "36 today" vs. the ~50–80 expected once upstream requirements/domain work closes the gap. |

**Status:** first pass, complete for the approved FR/NFR baseline as of 2026-07. Candidate
Requirements (CR-01–18, CNFR-01–07) and the July-2026 Strategic Review's Future Concepts/Gaps
(FC-01–15, GAP-01–13) are deliberately not yet represented — see `05-feature-review.md` for what
upstream work that requires.
