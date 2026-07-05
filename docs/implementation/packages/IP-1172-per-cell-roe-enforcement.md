# IP-1172 — Per-Cell Rules of Engagement Enforcement

> **Package ID:** IP-1172
> **Version:** 1.0
> **Status:** 🟢 READY *(MSTR-006 §3 authorization obtained 2026-07-05, project owner, recorded in
> `docs/pipeline/pipeline-journal.md` run #45 — no package-level dependency, so authorization was
> the only gate; independent of every other Tranche 3 package.)*
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

- `spacesim/content/vignette.py` *(proposed)*:
  - `Vignette` gains `roe: Optional[dict] = None` (each present key `"blue"`/`"red"` maps to
    `{"kinetic_authorized": bool, "cyber_authorized": bool}`).
  - `build_world()`'s `roe` construction (currently lines 218-221) becomes: if `vignette.roe` is
    present, use it directly (validated to have both cell keys, defaulting any missing
    sub-key/cell to `False`); otherwise, fall back to today's legacy-parameter-derived flat values
    and replicate them identically into both `roe["blue"]` and `roe["red"]` — this is the one
    branch point implementing `NFR-2010`'s backward-compatibility guarantee.
- `spacesim/engine/orders.py` *(proposed)* — `_validate()`'s two check sites (lines 349, 358)
  change from `self.roe.get("kinetic_authorized", False)` / `self.roe.get("cyber_authorized", False)`
  to `self.roe.get(order.cell, {}).get("kinetic_authorized", False)` / `...get("cyber_authorized", False)`.
  No change to `OrderSystem.__init__`'s signature or to `issue()`/`dry_run()` themselves — both
  already funnel through `_validate()`, so this is the single fix site for both entry points.

**Explicitly out of scope for this package:** the Creator's per-cell ROE selector UI — that is
[IP-1174](IP-1174-vignette-creator-ui-surfaces.md)'s concern; the auto-upgrade-on-save *mechanism*
itself (the reverse-serialization function that writes the upgraded shape back to disk) —
[IP-1173](IP-1173-vignette-creator-draft-session.md)'s concern. This package only makes the
per-cell shape a real, engine-enforced concept; it does not build the authoring UI or the save path.

## Implementation Tasks

**Not started — authorized 2026-07-05 (MSTR-006 §3).** Proposed sequence:

1. Write failing tests encoding both Acceptance Criteria below (per-cell divergent ROE gates
   correctly; legacy-only vignette behavior is unchanged) before any code change.
2. Add `Vignette.roe: Optional[dict] = None`.
3. Rewrite `build_world()`'s `roe` construction: explicit-shape branch first, legacy-fallback
   branch second, always producing a fully cell-keyed `{"blue": {...}, "red": {...}}` dict
   regardless of which branch ran.
4. Change `engine/orders.py`'s two `_validate()` check sites to resolve per `order.cell`.
5. Re-run every existing ROE-adjacent test (`test_orders.py` and any vignette test exercising
   `engage`/`cyber` actions) to confirm zero regression for all 19 currently shipped vignettes.

## Tests to Add

*(Proposed — none exist yet.)*

- `spacesim/tests/test_orders.py` *(existing file, extend)* or a new `test_per_cell_roe.py` — one
  test per Acceptance Criterion:
  - Given a vignette with an explicit `roe:` block where Blue's kinetic ROE is authorized and Red's
    is not, a kinetic order from Red is rejected (`roe_kinetic_not_authorized`) while an otherwise-
    identical kinetic order from Blue succeeds (subject to the existing weapons-quality/ammo gates,
    unchanged).
  - The mirror image for cyber ROE.
  - Given a vignette declaring only the legacy flat `red_kinetic_authorized`/`cyber_authorized`
    parameters (no `roe:` block), both cells' order-issuance behavior for `engage`/`cyber` actions
    is byte-identical to before this package — asserted directly against at least one of the 19
    currently shipped vignettes, not just a synthetic fixture.
  - Given a vignette with a `roe:` block that only partially specifies one cell (e.g. only
    `kinetic_authorized`, no `cyber_authorized` key), the missing sub-key defaults to `False` for
    that cell, not an exception.

## Documentation Updates

- `ROADMAP.md` Implementation Packages theme — add this package's row.
- `docs/features/FS-117-vignette-creator.md`'s `Referenced By` metadata — add this package once
  authored (this pass).
- `docs/design/04-data-model.md` §6 — gains the `Vignette.roe` field description, per this field's
  own "once implemented" instruction.
- Vignette-authoring reference documentation (`docs/vignettes/` conventions, if any describe the
  `parameters` mechanism) — a brief addition noting the new optional `roe:` block and its
  legacy-parameter fallback, so a hand-authoring White Cell user understands both paths remain
  valid.
- `CLAUDE.md`'s Code Map — a brief addition noting `engine/orders.py`'s ROE check is now per-cell,
  mirroring prior packages' precedent.

## Definition of Done

- [x] **Explicit user authorization obtained** for this package's Implementation Tasks (MSTR-006
  §3, 2026-07-05, project owner, recorded in `docs/pipeline/pipeline-journal.md` run #45).
- [ ] `Vignette.roe` exists, optional, defaulting to absent (no breakage of the 19 existing
  vignette YAML files, none of which declare it).
- [ ] A vignette with an explicit per-cell `roe:` block gates kinetic/cyber orders independently
  per `order.cell`.
- [ ] A vignette with only the legacy flat ROE parameters produces byte-identical order-issuance
  behavior to before this package, for all 19 currently shipped vignettes.
- [ ] `engine/orders.py`'s two `_validate()` check sites resolve ROE via `order.cell`, with no
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
