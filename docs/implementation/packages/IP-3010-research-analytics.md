# IP-3010 — Research Analytics: Multi-Run Export

> **Package ID:** IP-3010
> **Version:** 1.0
> **Status:** 🔴 BLOCKED *(blocked on IP-2010 reaching COMPLETE; also not authorized for
> implementation even once unblocked — see §"Definition of Done" and §"Risks")*
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

> **This is a forward-design package: the capability described here does not exist in `spacesim/`
> today, and it is additionally blocked on IP-2010 (a separate not-yet-implemented package)
> reaching `COMPLETE` before its own schema can be more than provisional.** Per MSTR-006 §3, this
> document specifies a scoped design — it is not an authorization to write code, independent of the
> blocking-dependency question.

## Feature Reference

[FS-301 — Research Analytics](../../features/FS-301-research-analytics.md)

## Requirements Covered

FS-301's "Requirements Implemented" field reports no explicit FR/NFR citation, and the RTM lists
FS-301 as `UNASSIGNED` in the Implementation-Package reverse index. This package's proposed batch
runner would depend on the following already-covered requirements as its architectural constraint
set:

| Req ID | Title (abridged) | Relevance to this package's design |
|---|---|---|
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

**Not started — blocked on IP-2010, and separately not authorized (MSTR-006 §3).** The following is
the proposed task sequence for when both the blocking dependency and authorization are resolved:

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

*(Forward-looking gate — none of the following is currently true.)*

- [ ] **IP-2010 has reached `COMPLETE`** (hard precondition — this package's schema is otherwise
  provisional, per FS-301 §4's "export must read FS-201's already-computed rubric output, not
  reimplement it" constraint).
- [ ] **Explicit user authorization obtained** for this package's Implementation Tasks, per
  MSTR-006 §3, separate from and in addition to the above.
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

- **Upstream:** IP-2010 (**hard blocking dependency** — this package cannot leave `BLOCKED` status
  until IP-2010 is `COMPLETE`), `engine/simulation.py`'s existing seeded-replay machinery (already
  shipped, no blocker).
- **Downstream:** None currently planned.
- **Build-sequencing:** This package is the second and final step of the critical path
  IP-2010 → IP-3010 in the Master Build Plan.

## Risks

- **Blocking-dependency risk (primary):** any attempt to implement this package's `RunRecord` schema
  in detail before IP-2010 lands would produce a schema that has to be revisited (or worse, diverges
  silently) once IP-2010's actual output shape is finalized — the schema in §"Files to Create" is
  explicitly provisional for this reason.
- **Authorization risk:** independent of the blocking dependency, MSTR-006 §3 requires a separate
  explicit user go-ahead before implementation begins.
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
