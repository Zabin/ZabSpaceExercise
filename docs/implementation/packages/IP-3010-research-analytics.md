# IP-3010 — Research Analytics: Multi-Run Export

> **Package ID:** IP-3010
> **Version:** 1.3 (2026-07-04 — independently verified; see Status below.)
> **Status:** ✅ VERIFIED *(2026-07-04, [`VR-3010`](../verification/VR-3010-research-analytics.md) —
> every Definition of Done/Verification Checklist item confirmed against the live tree; full suite
> green (566 passed/3 skipped), both permanent gates green; RTM `FR-10210` updated. `BL-0018`
> re-confirmed resolved against the current tree; `BL-0017` confirmed accurate. No new findings.
> Independence note: implemented run #10, verified run #12, same session — recorded explicitly in
> `VR-3010` per this project's verification-skill's own disclosure rule. Was 🔵 COMPLETE
> *(implemented 2026-07-04, run #10 — new `spacesim/tools/` subpackage
> (`research_batch.run_batch()`, seeded-Monte-Carlo batch runner) + `session/research_export.py`
> (`RunRecord` + CSV/JSON export). 7 new tests; full suite green (566 passed/3 skipped, up from
> 559/3), both permanent gates green. Entered `COMPLETE`, not `VERIFIED` — only
> `09-package-verification` may write `VERIFIED`.)* **MSTR-006 §3 authorization obtained 2026-07-03**
> (project owner, via `00-pipeline-manager` run #9, batching the standing `BL-0005` `NEEDS-USER`
> backlog item into that run's gate check) — the last of the five gated packages in this plan to
> receive it. **IP-2010 → `COMPLETE`** cleared 2026-07-03 (run #5) — this package's own
> `Dependencies` field requires `COMPLETE`, not `VERIFIED`, and the Master Build Plan has
> consistently treated that sub-condition as satisfied. **Note added 2026-07:** this package's
> Objective — a dedicated multi-run/cohort export interface — directly conflicted with ADR-0029 ("no
> new dedicated export/analysis interface... is introduced," Accepted) for the entire time this
> package existed at v1.0, without that conflict ever being recorded in this header the way
> IP-2010's ADR-0017 conflict was — a documentation gap `docs/reviews/
> requirements-domain-backfill-report.md` found independently. That conflict is now resolved:
> [ADR-0033](../../architecture/adr/ADR-0033-dedicated-research-export-interface.md) supersedes
> ADR-0029 and authorizes this package's design as written; the underlying capability is now also
> baselined as [`FR-10210`](../../requirements/01-functional-requirements.md). Was 🟡 READY *(fully
> unblocked 2026-07-03, run #9), was 🔴 BLOCKED before that (blocked on IP-2010 reaching `COMPLETE`
> and on its own separate MSTR-006 §3 authorization, both unrelated to the now-resolved ADR-0029
> conflict).*)*)*
> **Dependencies:** FS-301, IP-2010 (the per-exercise rubric output this package aggregates —
> **hard blocking dependency**, not merely a design reference)
> **Referenced By:** none yet
> **Produces:** structured multi-run/cohort export of IP-2010's measurement dimensions
> **Feature Reference:** [FS-301 — Research Analytics](../../features/FS-301-research-analytics.md)
> **Supersedes:** [`docs/implementations/IMP-301A-research-analytics.md`](../../implementations/IMP-301A-research-analytics.md)
> **Related Topics:** [`spacesim/session/aar.py`](../../../spacesim/session/aar.py) (the `export_csv` precedent), [`spacesim/engine/simulation.py`](../../../spacesim/engine/simulation.py) (seeded replay)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

## Package ID

IP-3010

## Title

Research Analytics — Multi-Run Export

## Objective

Close the gap DOM-004 §5 names explicitly: give a researcher a purpose-built batch-run and
structured-export layer (vignette ID, seed, condition label, plus IP-2010's per-run rubric output)
so instrument-grade research against SpaceSim does not require scripting directly against raw
`eventlog`/`save` artifacts — without relaxing engine determinism (variability comes from varying
the seed across runs, never from non-determinism inside `engine/`) and without reimplementing
IP-2010's scoring.

> **This was authored as a forward-design package: the capability did not exist in `spacesim/` at
> authoring time.** Both preconditions this package's own text originally named were cleared before
> implementation began: `IP-2010` reached `COMPLETE` 2026-07-03 (run #5), and per MSTR-006 §3, this
> document's own specification was not itself an authorization to write code — that separate,
> explicit user go-ahead was obtained 2026-07-03 (run #9; see the Status field above).
> `08-code-implementation` has since implemented the tasks below (2026-07-04, see Status).

## Feature Reference

[FS-301 — Research Analytics](../../features/FS-301-research-analytics.md)

## Requirements Covered

**FR-10210** (multi-run/cohort structured research-data export, added 2026-07) is now the primary
requirement this package implements — see `docs/features/FS-301-research-analytics.md`'s own
updated "Requirements Implemented" field. This package's proposed batch runner also depends on the
following already-covered requirements as its architectural constraint set:

| Req ID | Title (abridged) | Relevance to this package's design |
|---|---|---|
| FR-10210 | Multi-run/cohort structured research-data export | The requirement this package implements in full |
| FR-10110 | Automated non-aggregating competency rubric-tier computation (IP-2010) | Per-run output this package aggregates without reimplementing |
| FR-1120 | Deterministic replay (byte-identical from state/eventlog/seed) | The batch runner's reproducibility property depends directly on this invariant — each seeded run must be independently reproducible |
| NFR-1500 | Determinism (engine-wide) | This package must never relax determinism inside `engine/` to sample variability; variability comes only from varying the seed externally |
| NFR-3200 | Offline-first runtime | Batch runs must not require network access (per ADR-0018) |

## Architecture Components

- **C1 Simulation Engine** — read-only consumer of `engine/simulation.py`'s seeded `replay()`/
  `Simulation` machinery, driven N times externally (never modified internally).
- **C2 Session / Application Layer** — the proposed batch runner lives outside `engine/`, consuming
  IP-2010's `session/assessment.py` scoring functions once per seeded run.

## Interfaces

FS-301's "Interfaces Used" field states no ICD interface ID is cited — an open Phase 8 item. This
package proposes no new `INT-xxxx` interface; the batch runner is a new offline/CLI-style entry
point, not a live session-facing boundary.

## Files to Create

- `spacesim/tools/research_batch.py` *(created 2026-07-04 — this path required a new
  `spacesim/tools/` subpackage, the first of its kind; see Risks for a finding about this field's
  `tools/build_coastlines.py` precedent citation)* — `run_batch(vignette_id, seeds,
  condition_label, n_steps_or_until) -> list[RunRecord]`, as specified.
- `spacesim/session/research_export.py` *(created 2026-07-04)* — `RunRecord` pydantic schema
  (`vignette_id`, `seed`, `condition_label`, `assessment: dict`) and `export_csv`/`export_json`
  functions extending `aar.export_csv()`'s flattening pattern (one row per run, one column per
  dimension/metadata field for CSV) rather than inventing a new export format.

## Files to Modify

None proposed beyond the new files above — this package's design does not require modifying any
existing shipped module; it is purely additive, consuming IP-2010's scoring functions and
`engine/simulation.py`'s existing seeded-replay machinery as-is.

## Implementation Tasks

**Implemented 2026-07-04 by `08-code-implementation` (run #10).**

1. ✅ Confirmed IP-2010's scoring-function signatures/tier-value sets are `COMPLETE` and stable —
   `session/assessment.py`'s `assessment_report(mgr) -> dict` reads cleanly as a per-cell
   `{"blue": {...}, "red": {...}}` dict of tier strings + a `disclosure` note; a simple, stable
   shape to build against.
2. ✅ Implemented `run_batch()` as an external driver (`spacesim/tools/research_batch.py`):
   constructs one fresh `SessionManager` per seed inside the per-seed loop (never reused across
   iterations), advances each to `n_steps_or_until` sim-seconds from its own start (or the
   vignette's own estimated-duration horizon if omitted — "run to completion"); no shared mutable
   state between runs.
3. ✅ Implemented `RunRecord` (`spacesim/session/research_export.py`) capturing `vignette_id`,
   `seed`, `condition_label`, and IP-2010's `assessment_report` output for that run — called
   exactly once per run, never reimplemented.
4. ✅ Implemented CSV/JSON export of `list[RunRecord]`, extending `aar.export_csv()`'s pattern
   (`export_csv`/`export_json` in `research_export.py`) — one row per run, one column per
   cell/dimension pair for CSV.
5. **Confirmed not implemented**, per this package's own explicit exclusion: no
   statistical-analysis tooling beyond structured export, no cohort-management data model beyond
   the flat `condition_label` field, no human-subjects research capability of any kind.

## Tests to Add

*(Proposed — none exist yet; write test-first per `CLAUDE.md`'s mandatory workflow once unblocked
and authorized.)*

- `spacesim/tests/test_research_batch.py` *(new)* — asserts that two batch runs with identical
  `(vignette_id, seed)` produce byte-identical `RunRecord`s (the reproducibility property this
  entire feature exists to provide), and that varying only the seed produces the expected
  distribution shape for a fixture vignette with a known deterministic outcome per seed.
- A test asserting `run_batch()` never calls any IP-2010 scoring function more than once per run
  (no duplicated/reimplemented scoring).

## Documentation Updates

*(Implemented 2026-07-04 — all done.)*

- [x] Supersedes [`docs/implementations/IMP-301A-research-analytics.md`](../../implementations/IMP-301A-research-analytics.md)
  — that file's own banner updated to note this package's authorization/implementation.
- [x] `ROADMAP.md` Implementation Packages theme updated.
- [x] `CLAUDE.md`'s Code Map gained `spacesim/tools/research_batch.py` and
  `spacesim/session/research_export.py` entries.

## Definition of Done

*(Implemented 2026-07-04 by `08-code-implementation`; independently re-confirmed 2026-07-04 by
`09-package-verification` — [`VR-3010`](../verification/VR-3010-research-analytics.md). Every item
below holds against the live tree.)*

- [x] **IP-2010 has reached `COMPLETE`** (hard precondition — this package's schema is otherwise
  provisional, per FS-301 §4's "export must read FS-201's already-computed rubric output, not
  reimplement it" constraint). Cleared 2026-07-03, run #5.
- [x] **Explicit user authorization obtained** for this package's Implementation Tasks, per
  MSTR-006 §3, separate from and in addition to the above. Obtained 2026-07-03, run #9.
- [x] A batch run of N seeded simulations of vignette X produces N `RunRecord`s, each containing
  `vignette_id`, `seed`, `condition_label`, and IP-2010's rubric output for that run —
  `spacesim/tools/research_batch.py`'s `run_batch()`; confirmed by
  `test_run_batch_returns_one_record_per_seed_with_correct_metadata`.
- [x] No non-determinism is introduced inside `engine/` to produce variability across runs —
  `run_batch()` never touches `spacesim/engine/`; variability comes only from the `seed` parameter
  passed to a fresh `SessionManager` per run. Confirmed by
  `test_identical_vignette_and_seed_produce_byte_identical_run_records` and
  `test_run_batch_uses_a_fresh_session_manager_per_seed_no_shared_state` (two runs with the same
  seed produce byte-identical `RunRecord`s, proving no cross-run state leakage).
- [x] The export reads IP-2010's computed output without reimplementing any dimension-scoring
  logic — `run_batch()` calls `session/assessment.py`'s `assessment_report(mgr)` verbatim, exactly
  once per run; confirmed by `test_run_batch_never_reimplements_ip2010_scoring` (a monkeypatch
  spy asserting exactly one call per seed).
- [x] No human-subjects capability (cross-institution data collection, IRB-gated flows) exists
  anywhere in this package's code — `RunRecord`'s only fields are `vignette_id`/`seed`/
  `condition_label`/`assessment` (IP-2010's own per-cell tier dict); no trainee-identity or
  cross-institution field of any kind.
- [x] Each exported metric's validity-check level (per DOM-005 §5, inherited from IP-2010's own
  disclosure) is carried through to the export, not silently dropped — `assessment_report`'s
  `disclosure` field is part of the per-cell dict `RunRecord.assessment` stores verbatim, so it
  round-trips through both `export_csv` (as a `disclosure` column) and `export_json` unchanged.

## Verification Checklist

*(Executed 2026-07-04 by `09-package-verification` —
[`VR-3010`](../verification/VR-3010-research-analytics.md). Evidence below confirmed against the
live tree, not merely the Implementation Summary.)*

- [x] `spacesim/tests/test_research_batch.py` exists and is green — 7 tests, all passing.
- [x] `python3 -m pytest spacesim/tests/test_determinism.py` remains green after this module
  lands — confirmed (14 passed across both permanent gates, run together with
  `test_import_guard.py`).
- [x] Manual review confirms `run_batch()` contains no scoring logic duplicated from
  `session/assessment.py` (IP-2010) — `research_batch.py` imports and calls `assessment_report`
  directly; it defines no tier-boundary logic of its own. Also automated via
  `test_run_batch_never_reimplements_ip2010_scoring`.
- [x] Manual review confirms no code path in this package collects or persists cross-institution
  trainee-identifying data — confirmed by reading `research_export.py`'s `RunRecord` schema (see
  Definition of Done above).

## Dependencies

- **Upstream:** IP-2010 (**hard blocking dependency**, cleared 2026-07-03/run #5 — `IP-2010` was
  `COMPLETE`, the threshold this package's own field states, at implementation time; not yet
  `VERIFIED`, see Risks below), `engine/simulation.py`'s existing seeded-replay machinery (already
  shipped, no blocker), `session/assessment.py`'s `assessment_report` (IP-2010, read verbatim).
- **Downstream:** None currently planned.
- **Build-sequencing:** This package was the second and final step of the critical path
  IP-2010 → IP-3010 in the Master Build Plan; implemented 2026-07-04 (run #10), now `COMPLETE`.

## Risks

- **Blocking-dependency risk (residual, unchanged by implementation):** this package's `RunRecord`
  schema was implemented against `IP-2010`'s actual output shape while `IP-2010` is `COMPLETE`, not
  yet `VERIFIED`. If `IP-2010`'s own `09-package-verification` pass surfaces a material finding
  against its scoring-function signatures or tier-value sets, this package's schema (and its tests'
  golden-default assertions) would need revisiting — `09-package-verification` should check
  `IP-2010`'s verification status before signing off on `IP-3010` as built on stable ground.
- **Authorization risk (resolved 2026-07-03, run #9):** MSTR-006 §3's explicit, separate user
  go-ahead is now on record (`docs/pipeline/pipeline-journal.md` run #9).
- If any future revision of this package adds a human-subjects capability without triggering DOM-004
  §6's separate authorization and IRB/ethics process, it violates FS-301's explicit non-goal.
  **Confirmed respected in the 2026-07-04 implementation** — see Definition of Done.
- If the batch runner is implemented with any shared mutable state between seeded runs (e.g., a
  cached `Simulation` instance reused across seeds), determinism/reproducibility could be silently
  compromised — each run must start from a clean seeded initial state. **Confirmed avoided**:
  `run_batch()` calls `load_vignette()` and constructs a fresh `SessionManager` inside the per-seed
  loop, never reusing an instance across iterations.
- **New finding (2026-07-04, implementation):** this package's own `Files to Create` citation of
  `tools/build_coastlines.py` as the precedent for `spacesim/tools/research_batch.py`'s location is
  imprecise — `tools/build_coastlines.py` actually lives in the repo-root `tools/` directory (a
  non-package folder of standalone build scripts), not inside `spacesim/`. `spacesim/tools/` is a
  genuinely new subpackage (this package's first use), required because `run_batch()` must be
  importable by `spacesim/tests/` — the repo-root `tools/` scripts are not part of the installable
  package and aren't imported by anything. This does not change the correctness of the path this
  package instructed (`spacesim/tools/research_batch.py`, followed exactly), only the accuracy of
  the analogy drawn to justify it. Low severity, documentation-only.

## Rollback Considerations

*(Updated 2026-07-04 to reflect what actually shipped.)* This package added wholly new files
(`spacesim/tools/__init__.py` + `research_batch.py`, `spacesim/session/research_export.py`,
`spacesim/tests/test_research_batch.py`) with no downstream consumer; removing them fully reverts
this capability with no data-migration concern (no persisted state — `RunRecord`s are computed and
exported on demand, never written to any save file) and no impact on any other package in this
Master Build Plan. The one file this rollback would remove that other tooling could plausibly
notice is `spacesim/tools/__init__.py` itself, since it makes `spacesim/tools/` the first
subpackage of its kind — but nothing else in this pass depends on that subpackage existing, so its
removal is likewise self-contained.
