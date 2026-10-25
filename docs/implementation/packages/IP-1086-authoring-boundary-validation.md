# IP-1086 — One Shared Asset Validator at Every Authoring Boundary: Force-Add, Bulk Import, Creator Edits, Creator Save and the Load Gate Agree (FR-5310, FR-5311, FR-5220, FR-5110)

> **Package ID:** IP-1086
> **Version:** 1.0
> **Status:** READY — authored 2026-10-25 by `07-implementation-planning` (release-push remediation pass 8). Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive, recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256 (fix bugs before release; no new features) and the run #262 go-ahead, covers it: findings `H-3`, `M-1` and `M-3` of the unreviewed-packages integration review are bugs in `VERIFIED` packages (a 500 on the headline use of the Creator and bulk import). Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** [IP-1310](IP-1310-load-time-vignette-validation.md), [IP-1190](IP-1190-bulk-tle-omm-import.md), [IP-1173](IP-1173-vignette-creator-draft-session.md), [IP-1174](IP-1174-vignette-creator-ui-surfaces.md), [IP-1180](IP-1180-external-vignette-directories.md), [IP-1101](IP-1101-self-contained-saves.md), [IP-1200](IP-1200-save-as-scenario.md) (all `VERIFIED`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md), [`01-technical-work-breakdown.md`](../01-technical-work-breakdown.md) ("Release-push remediation, pass 8"); source: [`integration-review-unreviewed-packages.md`](../../reviews/integration-review-unreviewed-packages.md) `H-3`, `M-1`, `M-3`.
> **Produces:** one pure asset-authoring validator (`FR-5311` TLE propagation at the exercise start epoch plus physical bounds on Keplerian elements) called by the load gate, force-add TLE, OMM and bulk import, and the Creator's edit routes; a pre-save validation pass in the Vignette Creator's save; a per-asset guard in the scene, window and contact reads so one un-propagatable asset can no longer 500 a cell's picture.
> **Feature Reference:** [FS-131 — Load-Time Vignette Validation](../../features/FS-131-load-time-vignette-validation.md); [FS-117 — Vignette Creator](../../features/FS-117-vignette-creator.md); [FS-119 — Bulk TLE/OMM Import](../../features/FS-119-bulk-tle-omm-import.md) (`FR-5220`); [FS-120 — Save as Scenario](../../features/FS-120-save-as-scenario.md) (`FR-5510`)
> **Related Topics:** [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py), [`spacesim/content/vignette_export.py`](../../../spacesim/content/vignette_export.py), [`spacesim/session/manager.py`](../../../spacesim/session/manager.py), [`spacesim/session/scene.py`](../../../spacesim/session/scene.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Bug-fix package (three linked defects, one validator). Prose only; no code in this document.*

---

## Package ID

IP-1086.

## Title

Validate an asset once, in one place, at every point an author or White Cell can introduce it; make the read paths survive an asset that still cannot be propagated.

## Objective

Three findings with one root cause: the load gate (`IP-1310`) checks what the other authoring paths do not, and the read sinks have no guard of their own.

**Unit 1 (review `H-3`, High) — a stale-epoch TLE is accepted, then poisons the cell.** `_force_add_tle_object` (`session/manager.py`, line 627) proves a TLE only at *its own* epoch (`sat.sgp4(sat.jdsatepoch, …)`) and stamps `epoch=start_epoch`. The propagator ignores the stamp: `_tle_rv` (`engine/propagator.py`, line 87) feeds absolute sim time to SGP4. Every shipped vignette starts in 2030, so a current ISS TLE (epoch 2024) is accepted by `POST /force/tle` (200) and `POST /force/bulk_import` (200, `ok: true`), and then, after `start`, `GET /scene/blue`, `GET /windows/blue/ISS` and `GET /next_contacts/blue` are HTTP 500 (`sgp4 propagation error code 6`); on a draft, `GET /creator/scene` is 500 (all reproduced read-only in the planning pass; the traceback lands in `session/scene.py::_geo` and `engine/access.py::elevation_and_az`). The same TLE saved from the Creator is **refused** at load by `IP-1310`'s `FR-5311` check (`validate_vignette`, `content/vignette.py` line 445), so the two gates disagree about one object and the author sees a crash first and a rejection later. Real TLEs are the headline use of `IP-1173`/`IP-1174`/`IP-1190`.

**Unit 2 (review `M-1`, Medium) — unphysical Keplerian elements pass every gate.** A draft with `e: 1.5` or `a_m: -5` is accepted by `PUT /creator/state`, saved, loaded (`POST /api/sessions` 200), started and advanced, after which `GET /scene/blue` and `GET /creator/scene` are HTTP 500 (`math domain error` in `_j2_rates`); an `a_m` of 1000 m (inside the Earth) is accepted and renders. `FR-5310`-`FR-5314` list TLE parse, orbit-or-location presence, unique ids and role references; physical bounds are not stated, so `IP-1310` is correct to its spec and the gap is upstream (routed to `04`). Negative `delta_v_ms`/`ammo`/`power_w` and an asset id such as `../x` are likewise accepted. The OMM path of `IP-1190` (`_force_add_omm_object`, line 653) builds a Kepler `OrbitState` from file values with no bound check either.

**Unit 3 (review `M-3`, Medium) — the Creator saves files the load gate then refuses.** `save_vignette` (`content/vignette_export.py`, line 62) calls `export_vignette` and writes the file with no `validate_vignette` pass. Reproduced: a satellite with no orbit, a ground station with no location and a bad TLE each save with HTTP 200 and `{"vignette_id", "path"}`; `POST /api/sessions` for the saved id is then 400 `invalid_vignette` with the precise problem (the load gate itself is good). The author gets a success message and discovers the defect in a later session.

**Read-path robustness (the review's recommended second half of `H-3`).** `build_scene`, the window read and the contact read have no per-asset guard, so one asset that cannot be propagated (a TLE that decays mid-exercise, an element set that still slips through) takes down the whole cell's map, globe and fleet countdown. After this package such an asset is omitted from the cell-scoped picture and the others render.

**Left alone, by decision.** The Creator's `PUT /creator/state` stays tolerant of **incomplete** assets (a satellite with no orbit yet, a ground station with no location yet): `FR-5110` and `FR-5120` are iterative composition across round trips, "accumulating partial state", with the completeness requirement (`FR-5312`) enforced at save and load. Only values that are never valid (bounds, a TLE that cannot propagate) are refused at edit time. The engine is unchanged: `ModeratePropagator` raising on an undefined propagation is correct; the guard is at the session layer.

## Requirements Covered

| ID | How |
|---|---|
| `FR-5311` | A TLE-sourced orbit must initialise and propagate at the exercise start epoch: now enforced identically at load, force-add, bulk import and Creator edit (one function). |
| `FR-5310` | Load-time validation reports precisely; the shared validator adds the physical element bounds (a Note offered to `04`) so the load gate, the Creator and the force-add paths accept exactly the same assets. |
| `FR-5312` | Orbit-or-location presence stays a save/load rule; `PUT /creator/state` is not made stricter than the iterative-authoring requirement allows. |
| `FR-5220` | Bulk import keeps per-object failure reporting and continuation past a malformed object; a stale-epoch or unphysical object is a per-object failure with a reason, never an accepted asset. |
| `FR-5110` | Postcondition (no partial or incomplete vignette file from an authoring session): the Creator save refuses to write an invalid vignette; an existing file with the same id is left untouched on refusal. |
| `FR-5120`, `FR-5150` | The synchronized JSON view and the asset-menu edit refuse never-valid values with a reason naming the asset. |
| `NFR-1600` | No authoring action leaves a session in which a read 500s. |

## Architecture Components

- `content/vignette.py` — the shared validator (new public pure function) and `validate_vignette`'s per-asset loop, which calls it in place of its inline TLE check. Imported by `session/manager.py` (already imports from this module).
- `content/vignette_export.py::save_vignette` — pre-write validation.
- `session/manager.py` — `_force_add_tle_object`, `_force_add_omm_object`, `bulk_import` (through the two), `creator_set_state`, `creator_edit_asset`, `windows_ahead`, `next_contacts`, and `creator_scene` (inherits the scene guard).
- `session/scene.py::build_scene` — per-asset guard.
- Load-bearing invariants: deterministic core (the validator is pure: no clock, no RNG, deep-copies nothing it mutates; the guards are read-only and add no state); engine import boundary (nothing under `engine/` changes; `content/` and `session/` may import `engine/`, not the reverse); fog-of-war (an omitted asset is omitted from its owner's picture only; no cross-cell data is added); content is data.

## Interfaces

- **New (internal):** a pure function in `content/vignette.py`, for example `asset_authoring_problems(asset, start_epoch, prop=None) -> list[str]`, returning one human-readable reason per violation (empty when valid). It checks, for a validated `Asset`: (a) `FR-5311` — a `tle` orbit must hold both lines and propagate with `ModeratePropagator.rv(orbit, start_epoch)`; the reason text keeps today's `"TLE does not parse/propagate: <error>"` wording so existing assertions hold; (b) Keplerian bounds — all six elements finite, `0 <= e < 1`, perigee radius `a_m * (1 - e)` greater than `R_EARTH_EQ`, `0 <= i_deg <= 180`; (c) resources non-negative (`delta_v_ms`, `power_w`, `ammo`); (d) the asset id matches the id charset the rest of the system uses (`_ID_RE`: letters, digits, `_ . -`, 1-128, no leading `.`/`~`). It does **not** check orbit or location presence (those stay in `validate_vignette`).
- `validate_vignette` calls it for every force entry; the `where` path and the load-time error text are unchanged for the TLE case.
- `POST /force/tle`, `POST /force/bulk_import`, `PUT /creator/state`, `PATCH /creator/asset/{id}`: refusals use the existing `Ack(ok=False, reason)` / per-object report shapes; the reason names the asset and the violated rule. **No `server.py` change is expected** (the routes already return those shapes); the builder confirms.
- `POST /save_vignette`: an invalid vignette is HTTP 400, `detail` the `VignetteValidationError` message (`vignette '<id>' is invalid: <where>: <reason>; …`) the route's existing `except ValueError` already maps; no file is written.
- `GET /windows/{cell}/{asset}`: an asset whose propagation fails answers `{"asset", "now", "windows": []}` plus an additive `"error": "propagation_failed"`; `GET /next_contacts/{cell}` reports `null` for it; `GET /scene/{cell}` and `GET /creator/scene` omit it.

### Design Decisions

1. **One function, three callers, no copy.** The load gate's inline TLE check moves into the shared function; the force-add, OMM, bulk and Creator paths call the same function with the session's own `ctx.start_epoch` (equal to the vignette's `start_epoch_utc` by construction). A test asserts both gates return the same reasons for the same asset, and a grep-style test asserts `ModeratePropagator.rv` is not called for validation anywhere else in `content/` or `session/manager.py` outside the shared function.
2. **The check epoch is the exercise start, as in `IP-1310`.** A TLE that is valid at the start epoch but decays later in the exercise is not rejected here (it would need a horizon that no requirement states); the read-path guard covers it. Recorded as a residual.
3. **Completeness is a save rule, bounds are an edit rule.** See "Left alone". The Creator edit routes reject only never-valid values; the save and the load gate reject incomplete assets. This is the same split the requirements draw between `FR-5110`/`FR-5120` and `FR-5312`.
4. **Physical bounds are conservative.** `e < 1` and perigee above the equatorial radius exclude exactly the cases that crash or are inside the Earth, and every shipped Kepler orbit (40 across the 19 vignettes: minimum perigee radius 6,928,137 m, all circular) passes. The builder sweeps all 19 vignettes, the inject library, the Creator fixtures and the test suite's authored vignettes before enabling the bounds; if a shipped asset fails a rule, that rule is dropped from this package and filed (the id-charset and non-negative-resource rules are the likeliest to meet an old fixture).
5. **Pre-save validation runs on the exported `Vignette`.** `save_vignette` already builds it; running `validate_vignette` on that model is the exact check the load gate will run, so a saved file is loadable by construction. It applies to both the Creator draft and save-as-scenario (`IP-1200`) because both go through this function. The write is skipped on any problem; an existing same-id file is not touched.
6. **The read guard is local and silent.** `build_scene` wraps each asset's propagation (position and ground-track sampling) and skips the asset on `ValueError`/`ArithmeticError`; `windows_ahead` catches the same around the window search. Read paths must not mutate the world, so no message is appended; the omission is the signal, and the fleet rail and `view` still list the asset. A failure is deterministic for a given world, so replay is unaffected.
7. **Test fixtures that force-add the 2024 ISS TLE must change.** Many existing tests force-add a TLE with epoch 2024 into 2030-epoch sessions (`test_bulk_import*.py`, `test_vignette_creator_*.py`, `test_web.py`, `test_white_only_extension.py`, `test_console_small_fixes.py`, `test_self_contained_save.py`, `test_save_load_robustness.py`, `test_vignettes.py`). After this package such a TLE is correctly refused. The builder adds one shared test helper (in `spacesim/tests/conftest.py` or a small helper module) that returns a TLE valid at a given epoch (generated with `engine/tle_export.py::state_to_tle` from a Kepler state at the vignette start, round-trip-checked by that module) and moves those tests to it; tests that exist to prove the refusal keep the 2024 TLE. This is the largest mechanical part of the package and the main schedule risk.

## Files to Create

- `spacesim/tests/test_authoring_boundary_validation.py` — the matrix below.
- A small shared test helper for in-epoch TLEs (Design Decision 7), in the existing `spacesim/tests/conftest.py` or a helper module beside it.

## Files to Modify

- `spacesim/content/vignette.py` — the shared function; `validate_vignette` calls it (the inline TLE block at lines 444-450 is replaced).
- `spacesim/content/vignette_export.py` — `save_vignette`: run `validate_vignette` on the exported model before any write.
- `spacesim/session/manager.py` — `_force_add_tle_object`, `_force_add_omm_object`, `creator_set_state`, `creator_edit_asset`, `windows_ahead`, `next_contacts`.
- `spacesim/session/scene.py` — `build_scene` per-asset guard.
- The existing tests named in Design Decision 7 — fixture migration only; no assertion about refusal is weakened.
- `CLAUDE.md` — one sentence each in the `vignette.py`, `vignette_export.py` and `manager.py` code-map entries (doc step).
- `docs/requirements/03-requirements-traceability-matrix.md` — Test column regenerated (generated, never hand edited).

## Implementation Tasks

1. Test-first: write the matrix; confirm the stale-epoch, element-bound and pre-save cases fail on the parent (500s, accepted assets, 200 saves) and the incomplete-asset-at-edit and valid-asset cases pass.
2. Sweep (Design Decision 4): evaluate the draft bounds against all 19 vignettes, `inject_library.yaml`, the Creator fixtures and the authored vignettes in the tests; adjust or drop a rule only on evidence, and record it.
3. Write the shared function; switch `validate_vignette` to it (existing `IP-1310` tests must pass unchanged); add the callers one at a time (force-add TLE, OMM, Creator set/edit, Creator save).
4. Add the read guards; add the regression for the review's three 500 reads.
5. Migrate the fixtures (Design Decision 7); run the affected test files after each batch.
6. Run the new tests, `test_vignette_load_validation.py`, `test_vignette_library.py`, `test_vignette_creator_session.py`, `test_vignette_creator_ui.py`, `test_vignette_export.py`, `test_bulk_import*.py`, `test_content.py` (save-as-scenario), `test_scene.py`, `python3 -m pytest -m browser`, `test_determinism.py`, `test_import_guard.py`, then the full suite; regenerate the RTM Test column in the same commit.
7. Doc step; run `test_doc_integrity.py` and `test_test_origins.py`.

## Tests to Add

Each carries `@pytest.mark.verifies(...)` with the leaf shown. HTTP through the `TestClient` unless marked engine-level; the Creator tests configure `content.user_save_dir`/`external_vignette_dirs` to a temporary directory as the existing Creator tests do.

**Unit 1 — one validator, every path (`FR-5311`, `FR-5220`).**
1. The 2024 ISS TLE against a 2030-start session: `POST /force/tle` is `ok: false` with a reason naming the epoch problem and the asset; no asset is added; `GET /scene/blue`, `/windows`, `/next_contacts` after `start` are 200 (parametrised over normal session and draft, where the draft case also checks `GET /creator/scene` 200).
2. The same TLE through `POST /force/bulk_import` (TLE format), alone and mixed with a valid in-epoch TLE and a malformed block: the stale one is `ok: false` with the reason, the valid one `ok: true`, the malformed one reported, order and continuation preserved (`FR-5220` per-object reporting).
3. An in-epoch TLE (helper) is accepted on every path and the scene renders it.
4. Agreement: for a table of assets (valid in-epoch TLE, stale TLE, malformed lines, `e: 1.5`, `a_m: -5`, `a_m: 1000`, `e: 0.999` with a sub-surface perigee, valid circular LEO), the reasons returned by `validate_vignette` (as a vignette), `_force_add_tle_object`/`_force_add_omm_object` and the Creator edit are the same strings.
5. No duplicate logic: the only propagation call used for validation under `content/` and `session/manager.py` is inside the shared function (an AST or grep-level test, in the style of the existing `test_import_guard.py` checks).

**Unit 2 — bounds (`FR-5310`).**
6. OMM bulk import with `e >= 1`, negative or sub-surface `a_m`: per-object failure with a reason; a valid object in the same file imports.
7. `PUT /creator/state`, `PATCH /creator/asset/{id}` with `e: 1.5`, `a_m: -5`, `a_m: 1000`, `i_deg: 200`, non-finite elements, negative `delta_v_ms`/`ammo`/`power_w`, an id such as `../x` or one with a space: each refused with a reason naming the asset; the draft is unchanged (atomic); an *incomplete* asset (satellite with no orbit) is still accepted.
8. A vignette file with `e: 1.5` / `a_m: -5` / a negative resource: `POST /api/sessions` is 400 `invalid_vignette` naming the element (load gate), and an external-directory listing still works.
9. Sweep: all 19 shipped vignettes, `inject_library.yaml` and the Creator's curated sites pass the validator unchanged (the guard against a bound that breaks content).
10. Reproduction of the review: before this package a draft with `e: 1.5` reached `GET /scene/blue` 500; the permanent test asserts the draft refuses the element at the first PUT.

**Unit 3 — pre-save validation (`FR-5110`).**
11. Draft with a satellite without an orbit, a ground station without a location, and a bad TLE (three cases): `POST /save_vignette` is 400, `detail` names the asset and the rule, **no file exists** in the save directory; with an existing same-id file, its bytes are unchanged after the refusal.
12. A valid draft saves (200) and the saved id loads (`POST /api/sessions` 200); a save-as-scenario of a started session still saves and loads for the 19-vignette round trip the review ran (spot-check three).
13. The Creator console shows the 400 message on a refused save (browser test, following the existing Creator UI test pattern; the existing console handler surfaces non-2xx `detail`, the test pins that it does for this error).

**Read-path robustness (`NFR-1600`).**
14. An asset whose propagation raises (a TLE that decays by `start + N hours`, advanced past that instant; a hand-built `OrbitState` with `e: 1.5` injected into the world below the validators): `GET /scene/{owner}` is 200 and omits it, `/windows` answers with an empty list and `error`, `/next_contacts` has `null`, every other asset still renders; the other cell's scene is unaffected; `view`, `alarms`, `orders` still list the asset.
15. Replay equality and determinism: the guarded reads mutate nothing (`world.model_dump_json()` before and after is equal).

**Documentation checks.**
16. `test_doc_integrity.py` and `test_test_origins.py` green; no allow-list grew.

About 16 test functions (several parametrised) plus the fixture migration.

## Documentation Updates

- `CLAUDE.md` code map: the shared validator, the pre-save validation, the read guards (three short sentences).
- Not written by this package: `FR-5310` gains the physical-bounds clause and `FR-5220`/`FR-5110` gain "uses the same validation as load" (routed to `04-requirements-engineering`; the build does not wait on it, the tests tag the existing leaves); the Creator and bulk-import manual text (a TLE must be valid at the exercise start; the refusal wording) via `15-manual-traceability.md` §15.1 to `08-training-manual-authoring`.
- `docs/implementation/00-master-build-plan.md`, `packages/INDEX.md`, the TWBS: written in this planning pass.

## Definition of Done

- A TLE that cannot propagate at the exercise start epoch is refused with a reason on every path (load, force-add, bulk, Creator edit, Creator save), and the same asset gets the same verdict from each.
- Unphysical elements, negative resources and bad asset ids are refused at the Creator, the OMM import and the load gate.
- An invalid Creator vignette cannot be saved (400, no file written); a saved vignette always loads.
- `scene`, `windows`, `next_contacts` and `creator/scene` never 500 on an un-propagatable asset.
- Per-object bulk-import reporting is preserved; the iterative-composition behaviour of the Creator is preserved.
- New tests green; fixtures migrated; RTM Test column regenerated in the same commit; full suite, `python3 -m pytest -m browser`, `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`, `test_test_origins.py` green; no allow-list grew.

## Verification Checklist

- [ ] Re-derive `H-3` on the parent commit (force-add the 2024 ISS TLE; `/scene` 500) and on this commit (refused with a reason; scene 200).
- [ ] Re-derive `M-1` and `M-3` the same way (first PUT accepted and scene 500 on the parent; refused here; invalid save 200 on the parent, 400 and no file here).
- [ ] The verifier greps the tree for any second TLE or element validation outside the shared function.
- [ ] Every shipped vignette still loads; the validator's bounds are the ones the package states; any rule dropped by the sweep is recorded.
- [ ] `PUT /creator/state` still accepts an incomplete asset; `POST /save_vignette` refuses it.
- [ ] `engine/` is byte-unchanged; permanent gates, documentation checks and the browser suite green.

## Dependencies

All `VERIFIED`: `IP-1310`, `IP-1190`, `IP-1173`, `IP-1174`, `IP-1180`, `IP-1101`, `IP-1200`. Edits `session/manager.py` (build after `IP-1084`, before `IP-1087`), `content/vignette.py`, `content/vignette_export.py`, `session/scene.py`, and many test files for fixture migration. Does not edit `server.py` or `engine/`. `IP-1160` and `IP-1083` also edit `manager.py` in other regions.

## Risks

- **Fixture migration size (Design Decision 7).** About ten test modules change a fixture. Each batch is run before the next; a test that proves refusal keeps the stale TLE.
- **Bounds break content.** Mitigated by the sweep and the drop-the-rule clause; nothing under `spacesim/content/vignettes/` is edited by this package.
- **Behaviour change for old saves.** A save written before this package that contains a force-added stale TLE (now refused) loads as a 400 `invalid_vignette`/save-content refusal with the reason (via `validate_save`'s content check) instead of loading into a session whose map 500s. Intended; recorded in the commit.
- **Start-epoch-only check.** A TLE valid at the start and decayed later is still possible; the read guard covers the 500, not the fidelity. Residual, recorded.
- **Silent omission from the scene.** A player may wonder why an asset has no map marker; the fleet rail still lists it and the omission is deterministic. A visible indicator is a console feature, out of scope here.
- **Shared-function placement.** `session/manager.py` importing from `content/vignette.py` is the existing dependency direction; `engine/` must not import it (the import-guard test enforces).

## Rollback Considerations

Revert the commit (and the fixture migration with it). Force-add and the Creator return to accepting stale TLEs and unphysical elements, and the Creator save to writing unvalidated files (the defects return). No data format, save format or event-log record changes; files saved by the Creator under this package are ordinary valid vignettes and remain loadable after a rollback.
