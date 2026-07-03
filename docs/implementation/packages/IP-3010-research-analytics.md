# IP-3010 — Research Analytics: Multi-Run Export

> **Package ID:** IP-3010
> **Version:** 1.1 (2026-07-03 — authorization obtained; see Status below.)
> **Status:** 🟡 READY *(fully unblocked 2026-07-03, run #9. **IP-2010 → `COMPLETE`** cleared
> 2026-07-03 (run #5) — this package's own `Dependencies` field requires `COMPLETE`, not `VERIFIED`,
> and the Master Build Plan has consistently treated that sub-condition as satisfied since. **MSTR-006
> §3 authorization obtained 2026-07-03** (project owner, via `00-pipeline-manager` run #9, batching
> the standing `BL-0005` `NEEDS-USER` backlog item into that run's gate check) — the last of the five
> gated packages in this plan to receive it. **Note added 2026-07:** this package's Objective — a
> dedicated multi-run/cohort export interface — directly conflicted with ADR-0029 ("no new dedicated
> export/analysis interface... is introduced," Accepted) for the entire time this package existed at
> v1.0, without that conflict ever being recorded in this header the way IP-2010's ADR-0017 conflict
> was — a documentation gap `docs/reviews/requirements-domain-backfill-report.md` found
> independently. That conflict is now resolved:
> [ADR-0033](../../architecture/adr/ADR-0033-dedicated-research-export-interface.md) supersedes
> ADR-0029 and authorizes this package's design as written; the underlying capability is now also
> baselined as [`FR-10210`](../../requirements/01-functional-requirements.md). Was 🔴 BLOCKED
> *(blocked on IP-2010 reaching `COMPLETE` and on its own separate MSTR-006 §3 authorization, both
> unrelated to the now-resolved ADR-0029 conflict).*)*
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

> **This was authored as a forward-design package: the capability described here does not yet exist
> in `spacesim/`.** Both preconditions this package's own text originally named are now cleared:
> `IP-2010` reached `COMPLETE` 2026-07-03 (run #5), and per MSTR-006 §3, this document's own
> specification was not itself an authorization to write code — that separate, explicit user
> go-ahead was obtained 2026-07-03 (run #9; see the Status field above). `IP-3010` is now `READY`
> and eligible for `08-code-implementation`.

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

- `spacesim/tools/research_batch.py` *(new, proposed location — mirrors `tools/build_coastlines.py`'s
  precedent of an offline utility outside the live `ui_web`/`session` request path)* — the
  `run_batch(vignette_id, seeds, condition_label, n_steps_or_until) -> list[RunRecord]` function.
- `spacesim/session/research_export.py` *(new, proposed)* — `RunRecord` schema (pydantic model:
  `vignette_id`, `seed`, `condition_label`, plus IP-2010's per-dimension rubric fields) and a CSV/
  JSON export function extending `aar.export_csv()`'s flattening pattern (one row per run, one
  column per dimension/metadata field) rather than inventing a new export format.

## Files to Modify

None proposed beyond the new files above — this package's design does not require modifying any
existing shipped module; it is purely additive, consuming IP-2010's scoring functions and
`engine/simulation.py`'s existing seeded-replay machinery as-is.

## Implementation Tasks

**Not started — `READY` and authorized (2026-07-03, run #9); awaiting `08-code-implementation`.**
The following is the proposed task sequence:

1. Confirm IP-2010's scoring-function signatures/tier-value sets are `COMPLETE` and stable (this
   package's `RunRecord` schema is defined in terms of them; a schema change in IP-2010 after this
   package starts would require revisiting this package's own schema).
2. Implement `run_batch()` as an external driver: construct N `Simulation`/`SessionManager`
   instances, one per seed, running each to completion (or a configured step/time bound)
   sequentially or in any order the batch runner controls — never introducing shared mutable state
   between runs.
3. Implement `RunRecord` capturing `vignette_id`, `seed`, `condition_label`, and IP-2010's rubric
   output for that run — calling IP-2010's scoring functions exactly once per run, never
   reimplementing their logic.
4. Implement CSV/JSON export of `list[RunRecord]`, extending `aar.export_csv()`'s pattern.
5. **Explicitly do not implement** in this package: any statistical-analysis tooling beyond
   structured export (FS-301 §6 non-goal — analysis is the researcher's responsibility using
   [R401](../../research/encyclopedia/R401-experimental-design-and-controls.md)–[R413](../../research/encyclopedia/R413-data-analysis-and-reporting.md));
   any cohort-management data model beyond the flat `condition_label` field (named in FS-301 §2
   scope but explicitly not designed in detail by this package); and any human-subjects research
   capability (cross-institution de-identified trainee data collection, IRB-gated consent flows) —
   any future package adding such a mechanism must trigger DOM-004 §6's separate authorization/IRB
   process explicitly, not inherit it implicitly from this one.

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

- Supersedes [`docs/implementations/IMP-301A-research-analytics.md`](../../implementations/IMP-301A-research-analytics.md).
- `ROADMAP.md` Implementation Packages theme updated.
- `CLAUDE.md`'s Code Map should gain `spacesim/tools/research_batch.py` and
  `spacesim/session/research_export.py` entries once implemented (not added by this package, which
  contains no code changes).

## Definition of Done

*(Forward-looking gate — the two preconditions below are now satisfied; the rest awaits
`08-code-implementation`.)*

- [x] **IP-2010 has reached `COMPLETE`** (hard precondition — this package's schema is otherwise
  provisional, per FS-301 §4's "export must read FS-201's already-computed rubric output, not
  reimplement it" constraint). Cleared 2026-07-03, run #5.
- [x] **Explicit user authorization obtained** for this package's Implementation Tasks, per
  MSTR-006 §3, separate from and in addition to the above. Obtained 2026-07-03, run #9.
- [ ] A batch run of N seeded simulations of vignette X produces N `RunRecord`s, each containing
  `vignette_id`, `seed`, `condition_label`, and IP-2010's rubric output for that run.
- [ ] No non-determinism is introduced inside `engine/` to produce variability across runs.
- [ ] The export reads IP-2010's computed output without reimplementing any dimension-scoring logic.
- [ ] No human-subjects capability (cross-institution data collection, IRB-gated flows) exists
  anywhere in this package's code.
- [ ] Each exported metric's validity-check level (per DOM-005 §5, inherited from IP-2010's own
  disclosure) is carried through to the export, not silently dropped.

## Verification Checklist

*(To be executed once implemented; not yet applicable.)*

- [ ] `spacesim/tests/test_research_batch.py` exists and is green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green after this module lands.
- [ ] Manual review confirms `run_batch()` contains no scoring logic duplicated from
  `session/assessment.py` (IP-2010).
- [ ] Manual review confirms no code path in this package collects or persists cross-institution
  trainee-identifying data.

## Dependencies

- **Upstream:** IP-2010 (**hard blocking dependency**, cleared 2026-07-03/run #5 — `IP-2010` is
  `COMPLETE`, the threshold this package's own field states; not yet `VERIFIED`, see Risks below),
  `engine/simulation.py`'s existing seeded-replay machinery (already shipped, no blocker).
- **Downstream:** None currently planned.
- **Build-sequencing:** This package is the second and final step of the critical path
  IP-2010 → IP-3010 in the Master Build Plan; now `READY` and eligible for
  `08-code-implementation`.

## Risks

- **Blocking-dependency risk (residual, downgraded 2026-07-03):** this package's `RunRecord` schema
  is defined against `IP-2010`'s actual, now-implemented output shape (`COMPLETE`, not yet
  `VERIFIED`). If `IP-2010`'s own `09-package-verification` pass surfaces a material finding against
  its scoring-function signatures or tier-value sets, this package's schema would need revisiting —
  `08-code-implementation` should check `IP-2010`'s verification status (`COMPLETE` vs. `VERIFIED`)
  before implementing, per Implementation Tasks item 1, rather than assuming `COMPLETE` remains a
  stable foundation.
- **Authorization risk (resolved 2026-07-03, run #9):** MSTR-006 §3's explicit, separate user
  go-ahead is now on record (`docs/pipeline/pipeline-journal.md` run #9).
- If any future revision of this package adds a human-subjects capability without triggering DOM-004
  §6's separate authorization and IRB/ethics process, it violates FS-301's explicit non-goal.
- If the batch runner is implemented with any shared mutable state between seeded runs (e.g., a
  cached `Simulation` instance reused across seeds), determinism/reproducibility could be silently
  compromised — each run must start from a clean seeded initial state.

## Rollback Considerations

This package proposes wholly new files (`tools/research_batch.py`,
`session/research_export.py`) with no planned downstream consumer at authoring time; removing them
fully reverts this capability with no data-migration concern and no impact on any other package in
this Master Build Plan.
