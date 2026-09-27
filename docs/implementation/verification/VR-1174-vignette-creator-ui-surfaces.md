# VR-1174 — Verification Report: Vignette Creator UI Surfaces

> **Document ID:** VR-1174
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1174](../packages/IP-1174-vignette-creator-ui-surfaces.md), [FS-117](../../features/FS-117-vignette-creator.md) v1.1 (`FR-5120`–`FR-5160`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → IN PROGRESS` return of IP-1174 (RETURNED)
> **Feature Mapping:** FS-117 (`FR-5120`–`FR-5160` slice)
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py),
> [`spacesim/ui_web/static/creator.js`](../../../spacesim/ui_web/static/creator.js),
> [`spacesim/content/ground_sites.py`](../../../spacesim/content/ground_sites.py),
> [`spacesim/tests/test_vignette_creator_ui.py`](../../../spacesim/tests/test_vignette_creator_ui.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1174 — Vignette Creator UI Surfaces
- **Version verified:** 1.0
- **Tree state verified:** commit `e80d302` (branch `claude/chart-prompt-file-90hm9u`). That is
  `d2818ff` plus the docs-only `VR-1061` commit, so the code is identical to the tree the test run
  used. Implementing commit: `18c19a5`.
- **Independence:** implemented by `08-code-implementation` in a prior context. This verification
  ran in a freshly spawned agent context with no memory of that work. **Disclosure:** the
  implementing commit's `Claude-Session` trailer names the same outer remote session ID this agent
  runs under. Every claim was re-derived from the live source, a fresh test run, and an independent
  probe that drove the HTTP routes through `TestClient`.

## Result

**RETURNED: 1 failed check (High), plus 2 Medium and 2 Low findings.** Four of the five
requirements (`FR-5120`–`FR-5150`) are confirmed working. `FR-5160` is not met as specified:
seat-count declaration works for only one cell (White). Declaring Blue or Red seats, which the UI
itself offers, is refused with HTTP 403. The full suite is green (707 passed, 3 skipped) and both
permanent gates are green. The defect is a functional gap that the package's own tests encode as
intended behaviour, not a test failure.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Explicit user authorization obtained (MSTR-006 §3). | Recorded as run #45 (2026-07-05) in the package and the Master Build Plan. | ✅ Pass |
| The JSON view and form UI never disagree (`FR-5120`). | `manager.py:474-490`: `creator_state()` and `creator_set_state()` read and write `self.world.assets` directly, with no second representation. `creator_set_state` validates every entry before committing, so a bad write never half-applies. Probe: a JSON write (owner → `neutral`) was visible to the form read; a form PATCH (owner → `blue`) was visible to the JSON read; the invalid-owner PUT was rejected cleanly with an `Ack` reason. | ✅ Pass |
| 2D/3D preview updates on every add/edit/reassign/delete, with no `CellController` filtering (`FR-5130`). | `manager.py:517-538`: `creator_scene()` calls the unmodified `build_scene()` once per owner (`blue`, `red`, `neutral`) and merges the results. The only `CellController` strings added by the diff are comments and one test comment; the import at `manager.py:29` predates this package. Probe: the scene tracked every add, edit and delete. The scene's `RenderAsset` entries carry no `owner` field, so the preview cannot tell the cells apart (Finding L1). | ✅ Pass |
| TLE paste and lat/long entry both work with type/cell/name fields; the curated site list is offered before free entry (`FR-5140`). | `server.py:416-427`: `force/ground` plus `GET /api/ground_sites`. `force/tle` is unmodified. `content/ground_sites.py` parses 52 sites from `GROUND-INFRASTRUCTURE.md`; the probe got 52. The paths work for valid input, but `force/ground` with an invalid `owner`/`kind` returns **HTTP 500** (an unhandled pydantic `ValidationError` from `Asset(...)` at `manager.py:462-472`), and `lat_deg=999` is accepted without a range check (Finding M1). | ✅ Pass (with Medium finding) |
| Asset menu edit/reassign/delete is consistent across list, JSON view and preview (`FR-5150`). | `manager.py:492-515`; `server.py:441-453`. Probe: PATCH then DELETE were each reflected in the next state read and scene read. A PATCH cannot change the `id` because `id` is forced back. | ✅ Pass |
| A declared seat count plus matrix assignment produces `role_assignments` state identical in shape to `assign_role` (`FR-5160`). | For **White** seats only: `test_matrix_assignment_produces_role_assignments_identical_to_direct_assign_role` passes. The requirement is "declare how many seats exist **per cell**" (`FR-5160` title and description). `server.py:461-470` uses the request body's `cell` both as the caller-authorization check (`!= "white"` → 403) **and** as the target cell passed to `declare_seats(sid, req.cell, ...)`, so only `white-N` seats can ever be generated. Probe: `{"cell":"blue","count":2}` → 403 "only White Cell may declare seats", and the same for red. `index.html:147` offers White, Blue and Red. `creator.js:131-136` posts the chosen cell as `cell`, so choosing Blue or Red throws in `api.post` and the matrix never refreshes. The matrix's per-row `roles/assign` call then sends `cell = seat prefix` (`creator.js:151,160-164`), so even a Blue seat would be refused by `assign_role`'s White-only check (probe: `{"ok":false,"reason":"only White Cell may assign seat-to-role bindings"}`). `test_seat_declaration_rejects_non_white_cell` (`test_vignette_creator_ui.py:193`) asserts this defect as intended behaviour. | ❌ **Fail** (Finding H1) |
| No regression to any existing menu/panel/route. | Full suite 707 passed, 3 skipped. `test_observer.py` has 4 new Observer-guard entries (`force/ground`, `creator/state` PUT, `creator/asset` PATCH/DELETE), and all pass. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `test_vignette_creator_ui.py` exists and is green. | 15 tests (`:31`–`:200`), all green. One of them (`:193`) encodes the H1 defect. | ✅ Pass |
| `test_determinism.py` green. | 14 passed (with `test_import_guard.py`). | ✅ Pass |
| `test_import_guard.py` green. | Same run. No `spacesim/engine/` file was touched by `18c19a5`. | ✅ Pass |
| Full suite, zero regressions. | 707 passed, 3 skipped. | ✅ Pass |
| Independently confirm that the JSON view and form UI share one state by driving both. | Done by the probe (see the FR-5120 row), not by re-running the package's tests. | ✅ Pass |
| Independently confirm the preview uses `build_scene()` in ground-truth mode with no `CellController` import or call. | Confirmed by reading the code (see the FR-5130 row). The package's original "single ground-truth call" premise was wrong, as the Status header already discloses. The per-owner merge that replaced it is sound. | ✅ Pass |

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-5120 | `manager.py` `creator_state`/`creator_set_state`; `server.py` `creator/state` GET/PUT; `creator.js` JSON panel | `test_vignette_creator_ui.py:31-71` (4 tests) | `:180` cites the tests and `IP-1174`. Annotated this pass as `RETURNED (VR-1174)` at package level. | ✅ Pass |
| FR-5130 | `manager.py::creator_scene`; `server.py` `creator/scene`; `creator.js` preview | `:86`, `:96` | `:181`, annotated likewise. | ✅ Pass |
| FR-5140 | `server.py` `force/tle` (unmodified), `force/ground`, `ground_sites`; `content/ground_sites.py` | `:109`, `:121`, `:134` | `:182`, annotated likewise. | ✅ Pass (M1) |
| FR-5150 | `manager.py` `creator_edit_asset`/`creator_delete_asset`; `server.py` `creator/asset/{id}` PATCH/DELETE | `:149`, `:159`, `:169` | `:183`, annotated likewise. | ✅ Pass |
| FR-5160 | `manager.py::declare_seats`; `server.py` `creator/seats`; `creator.js` matrix | `:183`, `:193`, `:200` | `:184`, annotated as **not met, `VR-1174` H1**. | ❌ Fail |

## Test run

Commands run on the `d2818ff` code tree:

```
PYTHONPATH=. python3 <scratchpad>/p1174.py      # independent HTTP-route probe (not committed)
  → declare white 200 ["white-1","white-2"]; declare blue 403; declare red 403
  → assign blue: {"ok":false,"reason":"only White Cell may assign seat-to-role bindings"}
  → JSON⇄form convergence OK both directions; scene reflects add/edit/delete
  → force/ground owner="purple" → 500 Internal Server Error; lat_deg=999 → ok:true
  → ground_sites → 52

python3 -m pytest -o addopts="" -q spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py
  → 14 passed
python3 -m pytest -o addopts="" -q            (full suite)
  → 707 passed, 3 skipped, 1 warning in 156.06s
```

## Scope audit

`git show --stat 18c19a5` touches:

- **Production code:** the new `creator.js` and `content/ground_sites.py`. Modified:
  `session/manager.py`, `session/inprocess.py`, `ui_web/server.py`, `ui_web/static/app.js` and
  `ui_web/static/index.html`.
- **Tests:** the new `test_vignette_creator_ui.py`; `test_observer.py` was extended.
- **Docs:** `CLAUDE.md`, `ROADMAP.md`, `FS-117`'s status note, the RTM, the Master Build Plan,
  `packages/INDEX.md`, `01-technical-work-breakdown.md`, and the package itself.

`content/ground_sites.py` is outside the declared Files to Create. It is disclosed and anticipated
by the package's own Risk ("minimal parsing needed"), so it is an accepted excursion. The package
said the `session/manager.py` additions would be "small". They came to +96 lines, which is
proportionate. No unexplained excursion.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| H1 | **`FR-5160`'s per-cell seat declaration is not delivered.** `POST /creator/seats` overloads the body's `cell` as both the caller's identity (must be `white`) and the target cell for the seats, so only White seats (`white-1`…) can be declared. The Creator UI's Blue/Red options fail with an uncaught 403. The matrix's `roles/assign` call also sends the seat's own cell prefix as the caller identity, so a non-White row could never be assigned even if its seats existed. `test_seat_declaration_rejects_non_white_cell` pins the defect as if it were intended. **Fix direction (for 08, not done here):** separate the caller seat (the `cell` query parameter, the convention every other mutating route uses) from the target cell in the body, have the matrix call `roles/assign` as `white`, and invert the `:193` test to check the caller identity, not the target cell. | **High** | `08-code-implementation` re-run on IP-1174 |
| M1 | `POST /force/ground` has no input validation. An invalid `owner`/`kind` raises an unhandled `ValidationError` from `Asset(...)`, which surfaces as **HTTP 500** instead of an `Ack(ok=False, …)` (compare `creator_set_state`, which catches it). There is no `lat_deg`/`lon_deg` range check (`999` is accepted and stored). | Medium | `08-code-implementation` (same re-run) |
| M2 | `GroundAssetRequest.owner`/`kind` and the lat/long form share no validation vocabulary with `Asset`'s own `Literal` types. The same malformed-input path as M1 but at the schema level; the request model should constrain owner to `blue`/`red`/`neutral`. | Medium | `08-code-implementation` (same re-run) |
| L1 | The ground-truth preview scene (`creator_scene`) drops owner information: `RenderAsset` has no `owner` field, so the merged preview cannot colour or label assets by cell. `FR-5130` only requires rendering the lay-down, so this is a usability gap, not a failed requirement. | Low | `07-implementation-planning` (candidate enhancement) |
| L2 | The package's Objective, Architecture and Verification Checklist prose still describes the disproved single-call `build_scene(world, cell)` "ground-truth mode". The implementation note in Risks records the correction, but the prose was never updated. Carried forward from the implementing session's own routing. | Low | `07-implementation-planning` (package text) |

## Related

[IP-1174](../packages/IP-1174-vignette-creator-ui-surfaces.md) · [FS-117](../../features/FS-117-vignette-creator.md) ·
[VR-1173](VR-1173-vignette-creator-draft-session.md) · [VR-1151](VR-1151-seat-role-assignment.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md)
