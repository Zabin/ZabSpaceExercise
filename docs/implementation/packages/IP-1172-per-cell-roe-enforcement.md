# IP-1172 — Per-Cell Rules of Engagement Enforcement

> **Package ID:** IP-1172
> **Version:** 1.0
> **Status:** 🔵 COMPLETE *(implemented 2026-07-05 by `08-code-implementation` — `Vignette.roe`
> added, `build_world()`'s roe construction made cell-keyed with a legacy fallback,
> `engine/orders.py`'s two `_validate()` check sites resolve per `order.cell`. Discovered and fixed
> material drift beyond this package's own file list: `session/inprocess.py`'s per-cell brief
> endpoint and seven test files constructed `OrderSystem`/read `ctx.roe` in the old flat shape —
> see Risks. 4 new tests, full suite 579 passed/3 skipped (up from 575/3, +4), both permanent gates
> green. Awaiting `09-package-verification` to advance to `VERIFIED`.)*
> **Dependencies:** [FS-117](../../features/FS-117-vignette-creator.md) v1.1 (`FR-3420`,
> `NFR-2010`), [ADS-5100B](../../architecture/ADS-5100B-typed-parameters-and-per-cell-roe.md) §3.2,
> [FS-101](../../features/FS-101-mission-planning.md)/[FS-102](../../features/FS-102-command-scheduling.md)
> (already-`VERIFIED` territory this package touches — `engine/orders.py`'s existing ROE check)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** genuine per-cell ROE gating in `engine/orders.py`, consumed by
> [IP-1174](IP-1174-vignette-creator-ui-surfaces.md)'s per-cell ROE selectors
> **Feature Reference:** [FS-117 — Vignette Creator](../../features/FS-117-vignette-creator.md)
> (`FR-3420`/`NFR-2010` slice)
> **Supersedes:** none — new package
> **Related Topics:** [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package. Confirmed directly against the live code at authoring time:
`engine/orders.py`'s two ROE checks (`self.roe.get("kinetic_authorized", False)` at line 349,
`self.roe.get("cyber_authorized", False)` at line 358 — both inside the single `_validate()` method
both `issue()` and `dry_run()` call) never reference `order.cell` — ROE is enforced as one global
flag pair today, regardless of which cell issued the order, despite the vignette schema's
`red_`-prefixed parameter naming implying otherwise. The per-cell ROE YAML shape (nested
`roe: {blue: {...}, red: {...}}`) and the auto-upgrade-on-save policy were both resolved by the
project owner during this same `07-implementation-planning` pass, closing `ADS-5100B` Open
Questions 3/4 and `FS-117` Open Questions 5/7.*

## Package ID

IP-1172

## Title

Per-Cell Rules of Engagement Enforcement

## Objective

Make kinetic and cyber ROE authorization resolve independently per issuing cell, replacing today's
single global flag pair, while preserving byte-identical behavior for a vignette that declares only
the legacy global ROE pair (until it is next saved through the Vignette Creator, at which point it
is auto-upgraded to the explicit per-cell shape).

> **This is a forward-design package. Per MSTR-006 §3, this document's own specification is not
> itself an authorization to write code** — a separate, explicit user go-ahead is required before
> any Implementation Task below begins.

## Feature Reference

[FS-117 — Vignette Creator](../../features/FS-117-vignette-creator.md) (`FR-3420`/`NFR-2010` slice)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-3420 | Per-cell independent Rules of Engagement | `Vignette` gains an optional nested `roe: {blue: {kinetic_authorized, cyber_authorized}, red: {...}}` field; `build_world()`'s `VignetteContext.roe` construction becomes cell-keyed (`{"blue": {...}, "red": {...}}`) rather than one flat dict; `engine/orders.py`'s two `_validate()` check sites resolve `self.roe.get(order.cell, {}).get("kinetic_authorized", False)` / `...get("cyber_authorized", False)` instead of the current cell-agnostic lookup — one fix site each, since both `issue()` and `dry_run()` already funnel through the same `_validate()` method. |
| NFR-2010 | Additive vignette-schema evolution | A vignette declaring only the legacy flat `red_kinetic_authorized`/`cyber_authorized` (or `red_cyber_authorized`) parameters continues to resolve to both cells sharing those same values — `build_world()`'s legacy-parameter path becomes the *fallback* that populates both `roe["blue"]` and `roe["red"]` identically when no explicit `roe:` block is present, so all 19 currently shipped vignettes' order-issuance behavior is unchanged until re-saved. |

## Architecture Components

- **C5 Content & Data** — `content/vignette.py`'s `Vignette` schema gains an optional `roe: Optional[dict] = None` field (nested per-cell shape); `build_world()`'s `roe` construction logic branches on whether this field is present.
- **C1 Simulation Engine** — `engine/orders.py`'s `OrderSystem._validate()` resolves ROE per
  `order.cell` instead of globally; `OrderSystem.__init__`'s `roe` parameter now always receives a
  cell-keyed dict from `session/manager.py` (never the old flat shape), so the engine-side check is
  a single, simple per-cell lookup with no legacy-shape branching inside the engine itself — all
  backward-compatibility logic lives in `content/vignette.py`'s `build_world()`, not in
  `engine/orders.py`, per `CLAUDE.md` invariant 2 (the engine stays UI/content-agnostic; it should
  not need to know about "legacy vs. new" vignette-authoring shapes, only about the resolved,
  always-cell-keyed structure).
- **C2 Session / Application Layer** — `session/manager.py`'s `OrderSystem(self.sim, roe=dict(self.ctx.roe))`
  construction is unchanged in form (still passes `ctx.roe` through), since `ctx.roe` itself is now
  always cell-keyed by the time it reaches this call.

## Interfaces

None directly — `FR-3420`'s own Related Interfaces is "(none directly)"; this is an internal
engine/content-schema change, not a new interface. The auto-upgrade-on-save behavior is part of
[IP-1173](IP-1173-vignette-creator-draft-session.md)'s "Save as Vignette" reverse-serialization
function, which this package's schema change is a prerequisite for (the serializer needs a
per-cell `roe:` shape to write into).

## Files to Create

None proposed.

## Files to Modify

- `spacesim/content/vignette.py` *(implemented)*:
  - `Vignette` gains `roe: Optional[dict] = None` (each present key `"blue"`/`"red"` maps to
    `{"kinetic_authorized": bool, "cyber_authorized": bool}`).
  - `build_world()`'s `roe` construction now branches: if `vignette.roe` is truthy, build a
    cell-keyed dict directly from it (missing cell/sub-key defaults to `False`); otherwise, fall
    back to the legacy-parameter-derived flat values and replicate them identically into both
    `roe["blue"]` and `roe["red"]` — this is the one branch point implementing `NFR-2010`'s
    backward-compatibility guarantee.
- `spacesim/engine/orders.py` *(implemented)* — `_validate()`'s two check sites changed from
  `self.roe.get("kinetic_authorized", False)` / `self.roe.get("cyber_authorized", False)` to
  `self.roe.get(order.cell, {}).get("kinetic_authorized", False)` / `...get("cyber_authorized", False)`.
  No change to `OrderSystem.__init__`'s signature or to `issue()`/`dry_run()` themselves.
- `spacesim/session/inprocess.py` *(implemented, not in this package's original file list — see
  Risks)* — the per-cell Mission Brief endpoint's `_cell_brief(c)` closure exposed
  `"roe": dict(ctx.roe)` (the whole, then-flat dict); now exposes `"roe": dict(ctx.roe.get(c, {}))`
  — that cell's own authorization only. The external API shape (`{kinetic_authorized,
  cyber_authorized}`) is unchanged, confirmed by `test_web.py::test_session_brief_returns_per_cell_blocks`
  passing unmodified; `ui_web/static/app.js`'s `roe.kinetic_authorized`/`roe.cyber_authorized`
  reads needed no change either.

**Explicitly out of scope for this package:** the Creator's per-cell ROE selector UI — that is
[IP-1174](IP-1174-vignette-creator-ui-surfaces.md)'s concern; the auto-upgrade-on-save *mechanism*
itself (the reverse-serialization function that writes the upgraded shape back to disk) —
[IP-1173](IP-1173-vignette-creator-draft-session.md)'s concern. This package only makes the
per-cell shape a real, engine-enforced concept; it does not build the authoring UI or the save path.

## Implementation Tasks

**Complete (2026-07-05, `08-code-implementation`).**

1. ✅ Wrote 4 new failing tests first (test-first): 2 in `test_orders.py` (per-cell divergent
   kinetic/cyber gating), 2 in `test_content.py` (explicit-block backward compatibility + partial
   sub-key defaulting). Confirmed all 4 failed before implementation.
2. ✅ Added `Vignette.roe: Optional[dict] = None`.
3. ✅ Rewrote `build_world()`'s `roe` construction: explicit-shape branch first (cell-keyed,
   missing cell/sub-key defaults to `False`), legacy-fallback branch second (both cells share the
   flat-parameter-derived value) — always producing a fully cell-keyed dict regardless of which
   branch ran.
4. ✅ Changed `engine/orders.py`'s two `_validate()` check sites to resolve per `order.cell`.
5. ✅ Re-ran the full suite: found and fixed real drift beyond this package's own anticipated
   scope (see Risks) — `session/inprocess.py`'s per-cell brief endpoint and seven pre-existing test
   files (`test_orders.py`, `test_planning.py`, `test_assessment.py`, `test_safe_mode.py`,
   `test_ssn.py`, `test_content.py`, `test_vignette_library.py`) constructed `OrderSystem`/read
   `ctx.roe` in the old flat shape. Fixed each (Step 7 — regressions this package's own change
   caused, not scope creep). Full suite: 579 passed/3 skipped (up from 575/3, +4), zero regressions
   for any of the 19 currently shipped vignettes.

## Tests to Add

- `spacesim/tests/test_orders.py` *(existing file, extended)* —
  `test_per_cell_roe_kinetic_divergent_gates_independently`,
  `test_per_cell_roe_cyber_divergent_gates_independently`: Blue authorized/Red not (and the mirror
  image for cyber) gates each cell's order-issuance independently, both passing.
- `spacesim/tests/test_content.py` *(existing file, extended)* —
  `test_explicit_per_cell_roe_gates_independently_and_is_backward_compatible` (an explicit,
  divergent per-cell `roe:` block resolves correctly; a legacy-only vignette's `ctx.roe` mirrors
  the same value to both cells), `test_partial_per_cell_roe_block_defaults_missing_subkey_to_false`
  (a `roe:` block specifying only one cell/sub-key defaults everything else to `False`, never
  raising or silently authorizing).
- `test_vignette_1_loads_and_builds_a_world`/`test_parameter_override_flows_into_roe` (pre-existing,
  updated in place) now assert `ctx.roe["blue"]`/`["red"]` instead of the old flat top-level keys.

## Documentation Updates

- `ROADMAP.md` Implementation Packages theme — this package's row (added at planning time) updated
  to `COMPLETE`.
- `docs/features/FS-117-vignette-creator.md`'s `Referenced By` metadata — already present (added
  at planning time).
- `docs/design/04-data-model.md` §6 — `Vignette.roe` field description added; a paragraph added
  noting `build_world()` always produces a cell-keyed `ctx.roe` regardless of which path (explicit
  or legacy-fallback) produced it.
- `docs/vignettes/00-vignette-framework.md` — the "Authorities / ROE" parameter category now notes
  the optional `roe:` block alongside the existing `red_kinetic_authorized` example, with the
  fail-safe defaulting rule.
- `CLAUDE.md`'s Code Map — `engine/orders.py`'s entry notes ROE is now resolved per issuing cell;
  `content/vignette.py`'s entry notes the new `Vignette.roe` field and its legacy fallback.
- `docs/requirements/03-requirements-traceability-matrix.md` — `FR-3420`'s Test/Impl. Package cells
  and `NFR-2010`'s Test cell (ROE slice only) updated from `UNASSIGNED`.

## Definition of Done

- [x] **Explicit user authorization obtained** for this package's Implementation Tasks (MSTR-006
  §3, 2026-07-05, project owner, recorded in `docs/pipeline/pipeline-journal.md` run #45).
- [x] `Vignette.roe` exists, optional, defaulting to absent (no breakage of the 19 existing
  vignette YAML files, none of which declare it).
- [x] A vignette with an explicit per-cell `roe:` block gates kinetic/cyber orders independently
  per `order.cell`.
- [x] A vignette with only the legacy flat ROE parameters produces byte-identical order-issuance
  behavior to before this package, for all 19 currently shipped vignettes.
- [x] `engine/orders.py`'s two `_validate()` check sites resolve ROE via `order.cell`, with no
  legacy-shape-awareness logic added to the engine itself (that logic lives entirely in
  `content/vignette.py`'s `build_world()`).

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] The new/extended test file exists and is green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green (ROE resolution is a
  read-time dict lookup inside an already-deterministic validate path — no RNG, no wall-clock, no
  new mutation).
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green (no new import into
  `engine/`).
- [ ] Full existing suite re-run with zero regressions.
- [ ] Independently confirm (not merely re-cite), by reading the shipped `_validate()` code
  directly, that both check sites resolve per-cell and that no engine-side legacy-shape branch was
  accidentally introduced (per this project's own architectural intent that the engine stay
  content-schema-agnostic).
- [ ] Independently re-run all 19 currently shipped vignettes' existing tests to confirm zero
  behavioral change.

## Dependencies

- **Upstream:** [FS-117](../../features/FS-117-vignette-creator.md) v1.1 (no open design questions
  blocking this slice — the YAML shape and auto-upgrade policy were both resolved this pass),
  [ADS-5100B](../../architecture/ADS-5100B-typed-parameters-and-per-cell-roe.md) §3.2 (binding
  grounding).
- **Downstream:** [IP-1174](IP-1174-vignette-creator-ui-surfaces.md) — the Creator's per-cell ROE
  selectors are a thin UI layer over this package's schema; [IP-1173](IP-1173-vignette-creator-draft-session.md)'s
  "Save as Vignette" auto-upgrade logic writes into the `roe:` shape this package defines.
- **Build-sequencing:** Independent of every other Tranche 3 package (different files, no shared
  seam with [IP-1170](IP-1170-isr-beam-mode-coverage.md)/[IP-1171](IP-1171-typed-payload-bus-parameters.md)/
  [IP-1173](IP-1173-vignette-creator-draft-session.md)) — could be built in parallel with any of
  them.

## Risks

- **This package's own file list materially undercounted the blast radius — corrected during
  implementation, not silently absorbed.** This package's original `Files to Modify` named only
  `content/vignette.py` and `engine/orders.py`. Making `OrderSystem.roe`/`ctx.roe` always cell-keyed
  in fact required a third production-code fix (`session/inprocess.py`'s per-cell Mission Brief
  endpoint, which exposed the *whole* then-flat `ctx.roe` rather than the querying cell's own) and
  touched seven pre-existing test files that constructed `OrderSystem` or read `ctx.roe` directly in
  the old flat shape (`test_orders.py`, `test_planning.py`, `test_assessment.py`,
  `test_safe_mode.py`, `test_ssn.py`, `test_content.py`, `test_vignette_library.py`). Every one of
  these was a direct, mechanical consequence of the *same* architecture decision this package
  already committed to (cell-keyed ROE) — not a new design choice — so fixing them in this run was
  the correct call per `08-code-implementation`'s own "fix defects this package's own changes
  introduce" rule, not scope creep. Confirmed no client-side (`app.js`) change was needed: the
  per-cell brief's external API shape stayed identical (`test_web.py::test_session_brief_returns_per_cell_blocks`
  passes unmodified).
- **This touches already-`VERIFIED` `FS-101`/`FS-102` territory** (`engine/orders.py`'s `_validate()`
  method) — carried forward from `FS-117`'s own Risks. Re-confirming `FS-101`/`FS-102`'s existing
  Acceptance Criteria still hold after this change is part of this package's own verification
  burden, not optional; the Verification Checklist's full-suite-regression item is the mechanism
  for this.
- **Auto-upgrade-on-save means a re-saved legacy vignette's file changes even if the author never
  touched ROE** — an explicit, deliberate choice (this pass's design-fork resolution), not an
  oversight; `NFR-2010`'s "additive" framing is about *readability* (the legacy shape is never
  rejected), not about *file stability* on every save. This package itself does not implement the
  save path — it only ensures the target shape the save path upgrades *into* is well-defined and
  engine-enforced.
- **A vignette author could theoretically hand-write a malformed `roe:` block** (wrong cell key,
  wrong sub-key name) — handled by the missing-key-defaults-to-`False` rule (fail safe: an
  unrecognized or absent authorization defaults to *not authorized*, never silently authorized).

## Rollback Considerations

`Vignette.roe` is optional/absent-safe — reverting `content/vignette.py`'s field and `build_world()`'s
branching, and `engine/orders.py`'s two `_validate()` check sites back to the flat global lookup,
fully restores today's behavior with no data-migration concern for any of the 19 currently shipped
vignettes (none declare `roe:` yet) or for any vignette a user might have already saved through a
not-yet-rolled-back Creator (its `roe:` block would simply stop being consulted, falling back to
whatever legacy parameters, if any, still exist in the same file — a graceful degradation, not a
load failure, since removing the engine's per-cell check does not remove the `roe:` field itself
from the schema in a rollback that only reverts `engine/orders.py`).
