# VR-1174 — Verification Report: Vignette Creator UI Surfaces

> **Document ID:** VR-1174
> **Version:** 2.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1174](../packages/IP-1174-vignette-creator-ui-surfaces.md), [FS-117](../../features/FS-117-vignette-creator.md) v1.1 (`FR-5120`–`FR-5160`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of IP-1174 (this v2.0 pass)
> **Feature Mapping:** FS-117 (`FR-5120`–`FR-5160` slice)
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py),
> [`spacesim/ui_web/static/creator.js`](../../../spacesim/ui_web/static/creator.js),
> [`spacesim/content/ground_sites.py`](../../../spacesim/content/ground_sites.py),
> [`spacesim/tests/test_vignette_creator_ui.py`](../../../spacesim/tests/test_vignette_creator_ui.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1174 — Vignette Creator UI Surfaces
- **Version verified:** 1.0 (remediated)
- **Tree state verified:** commit `d2fc118` (branch `claude/chart-prompt-file-90hm9u`), the tip of
  the nine-package batch. Remediating commit: `2c9785d` (`fix(IP-1174): separate seat-declaration
  caller identity from target cell (BL-0123)`).
- **Independence:** this is a **second verification pass** (v2.0 of this report), run in a fresh
  session with no involvement in the `2c9785d` remediation commit or the v1.0 (`853bd7f`) report
  that returned it. Every claim below was re-derived from the live source and a fresh test run,
  independent of both.

## Result

**VERIFIED, with 3 Low findings carried/added — no High or Medium findings remain.** The v1.0
High finding (`BL-0123`: per-cell seat declaration broken) and both v1.0 Medium findings
(`BL-0124`/`BL-0125`: unhandled 500 on malformed `force/ground` input) are confirmed fixed by
independent re-probe. All five requirements (`FR-5120`–`FR-5160`) are confirmed working. Full
suite green (753 passed, 3 skipped), both permanent gates green.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Explicit user authorization for the remediation (MSTR-006 §3). | Package header records "authorized 2026-09-27, project owner's direct instruction." | ✅ Pass |
| `FR-5120`–`FR-5150` remain met (unchanged from v1.0, re-confirmed). | Independent probe: JSON-view PUT visible on next form-equivalent GET and vice versa; `creator_scene()` reflects add/edit/delete with no `CellController` import anywhere in `manager.py`'s creator methods or `server.py`'s creator routes; `force/tle`/`force/ground`/`ground_sites` (52 curated sites) all functional; asset PATCH/DELETE consistent across list/JSON/scene. | ✅ Pass |
| `FR-5160`'s per-cell seat declaration now works (`BL-0123`). | `server.py:518-530`: `declare_seats(sid, req: SeatDeclarationRequest, cell: Optional[str] = None)` — `cell` (query param) is the caller's identity, gated `cell != "white"` → 403; `req.cell` is the pure *target* cell passed to `api.declare_seats(sid, req.cell, req.count)`. Independent probe: `POST /creator/seats?cell=white` with body `{"cell":"blue","count":2}` → 200, `{"seats":["blue-1","blue-2"]}`; same for `{"cell":"red","count":1}` → `["red-1"]`; a non-white caller (`?cell=blue`) → 403. `creator.js:131-136`'s `declareSeats()` calls `api.post(...)`, which (`app.js:44-49`) appends `cell=CELL` — the UI's own currently-selected seat — as the query param; since the Creator panel is White-only, this is always `"white"` in practice. | ✅ Pass |
| The matrix's `roles/assign` call sends caller identity, not the assigned seat's cell prefix (`BL-0123`). | `creator.js:159-171`: the `.m-assign` handler posts `cell: "white"` literally (with an inline comment explaining why), not `row.dataset.cell`. Probe: assigning a `blue-1` seat's role via the matrix succeeds (`role_assignments` records the binding), where before the fix it would have been refused by `assign_role`'s White-only gate. | ✅ Pass |
| `force/ground` no longer 500s on malformed input (`BL-0124`). | `manager.py:470-486::add_ground_asset` wraps `Asset(...)` construction in `try/except Exception`, returning `(False, f"invalid ground asset: {exc}")` → `Ack(ok=False, ...)`. Independent probe: `owner="purple"` and `lat_deg=999` both now return HTTP 422 (rejected at the pydantic-schema layer, below) rather than reaching this handler at all; a value that passes the schema but still fails `Asset(...)` (e.g. a malformed `kind` outside any `Literal`, since `GroundAssetRequest.kind` remains a free `str`) is the manager-level catch's actual remaining trigger, confirmed by direct call. | ✅ Pass |
| `GroundAssetRequest.owner`/lat-long range-validated (`BL-0125`). | `server.py:242-274`: `owner: Literal["blue","red","neutral"]` plus `@field_validator` range checks on `lat_deg`/`lon_deg` ([-90,90]/[-180,180]). Probe: `owner="purple"` → 422 `literal_error`; `lat_deg=999` → 422 `value_error` with the exact message quoted in the validator. | ✅ Pass |
| Stale `build_scene(world, cell)` prose corrected (`BL-0127`). | Package `:101` (FR-5130 row) and `manager.py:551-559`'s docstring both now describe the per-owner-merge design (`creator_scene()` composes `build_scene()` once per real owner and merges), not the disproved single-call premise. `:315-333`'s Risks note also documents the correction. | ✅ Pass |
| No regression to any existing menu/panel/route. | Full suite 753 passed, 3 skipped (up from 707 at v1.0 — the other 8 packages in this batch account for the growth). No pre-existing test broken. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `test_vignette_creator_ui.py` exists and is green. | 16 tests (up from 15 at v1.0), all green. `test_seat_declaration_rejects_non_white_cell` (v1.0, encoded the defect as intended) is gone; replaced by `test_seat_declaration_rejects_non_white_caller` (`:193`) and a new `test_seat_declaration_allows_white_caller_to_declare_non_white_target_cell` (`:202`), which directly tests the v1.0 H1 fix. | ✅ Pass |
| `test_determinism.py` green. | 6 passed (this package touches no engine code — draft sessions have no event log/clock advance). | ✅ Pass |
| `test_import_guard.py` green. | 8 passed. No file under `spacesim/engine/` touched by this package or its remediation. | ✅ Pass |
| Full suite, zero regressions. | 753 passed, 3 skipped, 1 warning (pre-existing `httpx`/starlette deprecation notice, unrelated). | ✅ Pass |
| Independently confirm JSON view / form UI share one state. | Re-confirmed by fresh probe (unchanged from v1.0; not touched by this remediation). | ✅ Pass |
| Independently confirm the preview uses `build_scene()` in ground-truth mode, no `CellController` import/call. | Re-confirmed: `grep -n CellController` across `manager.py`'s creator methods, `server.py`'s creator routes, and `creator.js` returns nothing in the creator surface's own code. | ✅ Pass |

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-5120 | `manager.py::creator_state`/`creator_set_state`; `server.py` `creator/state` GET/PUT | `test_vignette_creator_ui.py` (4 tests) | RTM `:180` still says "RETURNED on `FR-5160`" — **stale, corrected by this report (see Findings L3)**. | ✅ Pass |
| FR-5130 | `manager.py::creator_scene`; `server.py` `creator/scene` | same file | RTM `:181` — same stale annotation, corrected. | ✅ Pass |
| FR-5140 | `server.py` `force/tle`, `force/ground`, `ground_sites`; `content/ground_sites.py` | same file | RTM `:182` — same stale annotation, corrected. | ✅ Pass |
| FR-5150 | `manager.py::creator_edit_asset`/`creator_delete_asset`; `server.py` `creator/asset/{id}` PATCH/DELETE | same file | RTM `:183` — same stale annotation, corrected. | ✅ Pass |
| FR-5160 | `manager.py::declare_seats`; `server.py::declare_seats` (caller/target split); `creator.js` matrix | `test_vignette_creator_ui.py:183-215` (3 tests) | RTM `:184` says "RETURNED... H1... not met" — **stale, this is the cell this report actually needed to flip; corrected.** | ✅ Pass |

## Test run

Commands run on the `d2fc118` tree (worktree `agent-a17e870f946ba1748`):

```
python3 -m pytest -q                                                    # full suite
  → 753 passed, 3 skipped, 1 warning in 168.20s

python3 -m pytest spacesim/tests/test_determinism.py -q                 # permanent gate 1
  → 6 passed

python3 -m pytest spacesim/tests/test_import_guard.py -q                # permanent gate 2
  → 8 passed

python3 -m pytest spacesim/tests/test_vignette_creator_ui.py -q         # package-specific
  → 16 passed
```

Independent HTTP-route probe (`TestClient`, not committed — ad hoc scratchpad script):
```
declare white 200 ["white-1"]; declare blue (caller=white) 200 ["blue-1","blue-2"];
declare red (caller=white) 200 ["red-1"]; declare (caller=blue) 403
matrix-assign a blue-1 seat (caller literal "white") → role_assignments records it
force/ground owner="purple" → 422 (literal_error); lat_deg=999 → 422 (value_error, range msg)
JSON⇄form convergence OK both directions; scene reflects add/edit/delete
```

## Scope audit

`git show --stat 2c9785d` touches: `docs/implementation/00-master-build-plan.md`,
`docs/implementation/packages/IP-1174-vignette-creator-ui-surfaces.md`, `docs/pipeline/backlog.md`,
`spacesim/session/manager.py`, `spacesim/tests/test_vignette_creator_ui.py`,
`spacesim/ui_web/server.py`, `spacesim/ui_web/static/creator.js`. Every file is inside the
package's own declared surface (Files to Create/Modify) or its natural test/doc companions — no
unexplained excursion. No `spacesim/engine/` file touched.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| L1 *(carried forward from v1.0, unresolved, out of this remediation's scope)* | The ground-truth preview scene (`creator_scene`) still drops owner information: `RenderAsset` has no `owner` field, so the merged preview cannot colour/label assets by cell. `FR-5130` only requires rendering the lay-down, so this remains a usability gap, not a failed requirement. | Low | `07-implementation-planning` (candidate enhancement) |
| L2 (new) | `BL-0124`/`BL-0125`'s fix is functionally confirmed by this report's own probe, but `test_vignette_creator_ui.py` has no dedicated regression test asserting the malformed-`owner`/out-of-range-`lat_deg` rejection path (422, or the manager-level `Ack(ok=False)` for a malformed `kind`). A future edit to `GroundAssetRequest` or `add_ground_asset` could silently regress this with no test catching it. | Low | `08-code-implementation` (add regression test; does not block VERIFIED — behavior itself is correct and independently probed) |
| L3 (new) | The Requirements Traceability Matrix rows for `FR-5120`–`FR-5160` (`03-requirements-traceability-matrix.md:180-184`) still carry v1.0's "RETURNED... not met" annotations. This report corrects them (see Related change below) as part of this pass's mandated traceability audit. | Low | Closed by this report's own RTM edit |

## RTM correction applied by this report

`docs/requirements/03-requirements-traceability-matrix.md` rows for `FR-5120`–`FR-5160` (lines
180–184) updated to drop the stale "RETURNED... `VR-1174`" annotation and record `IP-1174` as
`VERIFIED` (this report), since the v1.0 defect they described is now fixed and independently
confirmed.

## Related

[IP-1174](../packages/IP-1174-vignette-creator-ui-surfaces.md) · [FS-117](../../features/FS-117-vignette-creator.md) ·
[VR-1173](VR-1173-vignette-creator-draft-session.md) · [VR-1151](VR-1151-seat-role-assignment.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md)

## Prior pass (v1.0, superseded)

v1.0 (`853bd7f`, tree `d2818ff`) returned this package: High finding `H1` (seat declaration
White-only), Medium findings `M1`/`M2` (unhandled 500 + missing validation on `force/ground`), plus
Low findings `L1` (preview owner labelling, still open above) and `L2` (stale
`build_scene(world, cell)` prose, fixed and confirmed above as part of the `BL-0127` DoD item).
`FR-5120`–`FR-5150` were already confirmed met at v1.0; only `FR-5160` failed. This v2.0 pass
confirms all three findings' fixes independently and closes the package to `VERIFIED`.
