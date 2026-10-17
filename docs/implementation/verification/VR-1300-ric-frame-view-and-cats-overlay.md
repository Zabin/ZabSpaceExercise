# VR-1300 — Verification Report: Live RIC-Frame Relative-Motion View & CATS Overlay

> **Document ID:** VR-1300
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1300](../packages/IP-1300-ric-frame-view-and-cats-overlay.md), [FS-130](../../features/FS-130-ric-frame-view-and-cats-overlay.md) v1.0 (`FR-8210`, `FR-8220`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of IP-1300
> **Feature Mapping:** FS-130 (`FR-8210`, `FR-8220`)
> **Related Topics:** [`spacesim/engine/sun.py`](../../../spacesim/engine/sun.py),
> [`spacesim/session/ephemeris.py`](../../../spacesim/session/ephemeris.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py),
> [`spacesim/ui_web/static/ricview.js`](../../../spacesim/ui_web/static/ricview.js)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1300 — Live RIC-Frame Relative-Motion View & CATS Overlay
- **Version verified:** 1.0
- **Tree state verified:** commit `dcce680` (branch `claude/chart-prompt-file-90hm9u`). Implementing
  commit: `152754e`, sequenced after the package was authored at `b10717a` (2026-10-03,
  `07-implementation-planning`) and authorized 2026-10-10 (MSTR-006 §3).
- **Independence:** first verification pass, fresh session with no involvement in `b10717a` or
  `152754e`. No prior `09-package-verification` run on this package.

## Result

**VERIFIED, with 2 Low findings.** Both `FR-8210` (live, operator-selectable RIC-frame
relative-motion view) and `FR-8220` (CATS illumination-phase-angle overlay) are fully and correctly
implemented. Every claim in the Implementation Summary was independently re-derived — not merely
re-run — against fresh reference geometries and fresh HTTP probes the implementing session's own
fixtures do not already cover. `BL-0158` is adjudicated **DONE, accepted, no remediation required**
(see below). Full suite 772 passed, 3 skipped; both permanent gates green.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `cats_phase_angle_deg()` returns correct values at the 0°/90°/180° reference geometries. | `engine/sun.py:81-98`. Independently re-derived (not from `test_cats_angle.py`'s own fixtures): a fresh target position `[7000, 1234, -500]` km and a chaser placed along/against/perpendicular to the real `sun_unit_eci()` output at an arbitrary epoch gave 0.0°, 180.0°, 90.00000000000003° and (for an intermediate 60°-constructed geometry) 59.99999999999999° — exact to float precision. Coincident chaser/target independently probed → `ValueError` raised, matching the docstring's stated contract. | ✅ Pass |
| The live-RIC function's output matches `to_ric()`'s own existing output for a known case. | `session/ephemeris.py:125-183::live_ric_view()` calls `to_ric()` (`:64-87`, byte-identical to its pre-package body — `git show 152754e -- session/ephemeris.py` touches only new code, confirmed by diff) for every visible object relative to the resolved origin state; `test_live_ric_view_truth_matches_to_ric_at_current_sim_time` (`test_ephemeris.py:279`) cross-checks against an independently-computed `to_ric()` call, not a hand-copied constant. | ✅ Pass |
| A cell-scoped request renders only that cell's visible objects; an out-of-custody origin/chase/target selection is rejected; the White-Cell/no-cell variant renders every object. | Independently probed via a fresh `TestClient` session on a *different* vignette (`leo-isr-denial`, seed 7) than any of the implementer's own tests use: a blue-scoped request for a red asset's id as `origin` → `404 {"detail": "origin 'RED-SURF' has no state visible to blue"}`; a white-scoped request with coincident `chase`/`target` → `404` (the `cats_phase_angle_deg` `ValueError` caught cleanly by the route, not a 500) — an edge case not present in any shipped test. On the `co-orbital-threat-escort` vignette, a white-scoped request with distinct chase/target returned both the blue asset and its escort (truth, not a cell's belief), confirmed against `manager.py:814-828::get_ric_view()`'s explicit `cell == "white"` branch through `get_godview()` (`:858-859`, returns `self.sim.world` — ground truth, same object `build_scene()`'s cell-filtered path never reaches, since that function's asset/track loops filter strictly on `owner == cell`/`t.owner == cell` with no `"white"` case — read directly at `scene.py:81-122`, not assumed). | ✅ Pass |
| The CATS overlay appears only when both `chase`/`target` are supplied; it does not alter `FR-8210`'s own view when absent. | `ephemeris.py:169-180`: `cats` stays `None` unless both are non-`None`; `objects` is built before the `cats` block and is never conditioned on it. Independently probed: a white-scoped request with `origin` only → `cats: null`; a request with only `chase` set (no `target`) also returns `cats: null`, matching `test_live_ric_view_cats_only_when_both_chase_and_target_supplied`'s `only_chase` case. | ✅ Pass |
| Full existing test suite green, zero regressions, both permanent gates green. | 775 total outcomes in a from-scratch run (772 passed + 3 skipped + 0 F/E, independently tallied character-by-character from the raw dot-stream, since this environment's pytest run does not surface its own final summary line to the capture pipe); exit code 0. `test_determinism.py` + `test_import_guard.py` run together: 14 passed. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Every new test named above exists and is green. | `test_cats_angle.py` (6 tests), `test_ephemeris.py::test_live_ric_view_*` (8 tests, confirmed by name: `truth_matches_to_ric_at_current_sim_time`, `reselecting_origin_rerenders_relative_to_new_origin`, `cell_scoped_renders_belief_not_truth`, `cell_scoped_limits_objects_to_cells_own_picture`, `rejects_origin_outside_cells_custody`, `rejects_chase_or_target_outside_cells_custody`, `cats_only_when_both_chase_and_target_supplied`, `is_read_only_and_deterministic`), `test_web.py::test_ric_view_*` (5 tests: `route_cell_scoped_returns_only_cells_own_picture`, `route_rejects_origin_outside_cells_custody`, `route_white_renders_every_object_from_ground_truth`, `client_surface_is_served`, `route_requires_origin`). All 19 confirmed present by direct grep and green in an isolated run of the three files. | ✅ Pass |
| `python3 -m pytest spacesim/tests/test_determinism.py` remains green. | 6 passed (run jointly with the import-guard gate: 14 passed total, both files individually dot-confirmed with zero `F`). | ✅ Pass |
| `python3 -m pytest spacesim/tests/test_import_guard.py` remains green. | 8 passed. `engine/sun.py`'s one addition (`cats_phase_angle_deg`) uses only `numpy`/`math`, no wall-clock/RNG/forbidden import — confirmed by reading the function body directly. | ✅ Pass |
| Independently confirm, by reading the shipped code, that the White-Cell/no-cell variant actually renders ground truth (not a cell-filtered subset). | Read `manager.py:814-828` and `scene.py:81-122` directly (not cited from the Implementation Summary): `build_scene()`'s asset loop (`:88 if a.owner != cell: continue`) and track loop (`:119 if t.owner != cell: continue`) have no `"white"` special case, exactly as the package's own Implementation Task 1 warned; `get_ric_view()` therefore branches explicitly (`if cell == "white": return ephemeris.live_ric_view(self.get_godview(), None, ...)`), passing `cell=None` into `live_ric_view()`'s no-cell/ground-truth path (`ephemeris.py:101,104,116-117` — `cell is None` reads every on-orbit asset's own true orbit with no ownership filter at all). Independently probed end-to-end on a fresh session/vignette: the white-scoped response contained every on-orbit object in the vignette (both blue and red), not one cell's belief. | ✅ Pass |
| Independently confirm `cats_phase_angle_deg()` is not duplicated anywhere else in `engine/`. | `grep -rn "phase_angle\|cats_phase"` across `spacesim/engine/` returns exactly one definition site (`sun.py:81`); the only other `acos`/`dot` combinations in `engine/` are `orbit.py`'s argument-of-perigee/true-anomaly derivations (`:167,174,179`), an unrelated orbital-elements computation, not a second phase-angle implementation. `test_cats_angle.py::test_phase_angle_is_defined_only_once_in_engine` encodes the same check as a standing regression test. | ✅ Pass |

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-8210 | `session/ephemeris.py::live_ric_view()`; `session/manager.py`/`inprocess.py::get_ric_view()`; `ui_web/server.py` `GET /ric_view/{cell}` | `test_ephemeris.py::test_live_ric_view_*`, `test_web.py::test_ric_view_route_*` | `docs/requirements/03-requirements-traceability-matrix.md`'s `FR-8210` row cites `IP-1300` and the correct test names — confirmed current, left unchanged (already accurate at `COMPLETE`, no correction needed). | ✅ Pass |
| FR-8220 | `engine/sun.py::cats_phase_angle_deg()`; `ephemeris.py::live_ric_view()`'s `cats` block | `test_cats_angle.py`, `test_ephemeris.py::test_live_ric_view_cats_only_when_both_chase_and_target_supplied`, `test_web.py::test_ric_view_route_white_renders_every_object_from_ground_truth` | `FR-8220` row cites `IP-1300` and the correct test names — confirmed current, left unchanged. | ✅ Pass |

## Test run

```
python3 -m pytest -q                                                                    # full suite
  → 775 outcomes tallied from the raw dot-stream: 772 passed, 3 skipped, 0 failed/errored; exit 0
python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py  # both gates
  → 14 passed in 1.64s
python3 -m pytest spacesim/tests/test_cats_angle.py spacesim/tests/test_ephemeris.py spacesim/tests/test_web.py
  → 19 new/touched tests confirmed present and green (isolated run)
```
Plus ad hoc independent probes via `fastapi.testclient.TestClient` against fresh sessions on
vignettes (`leo-isr-denial`, `co-orbital-threat-escort`) not reused verbatim from the implementer's
own fixtures, and a from-scratch `cats_phase_angle_deg()` reference-geometry script (see Definition
of Done row 1) — both recorded above as their own audit evidence, not merely "tests passed."

## Scope audit

`git show --stat 152754e` touches exactly: `CLAUDE.md`, `ROADMAP.md`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`,
`docs/requirements/03-requirements-traceability-matrix.md`, `spacesim/engine/sun.py`,
`spacesim/session/ephemeris.py`, `spacesim/session/inprocess.py`, `spacesim/session/manager.py`,
`spacesim/tests/test_cats_angle.py`, `spacesim/tests/test_ephemeris.py`, `spacesim/tests/test_web.py`,
`spacesim/ui_web/server.py`, `spacesim/ui_web/static/index.html`, `spacesim/ui_web/static/ricview.js`,
`spacesim/ui_web/static/style.css` — 16 files. Every engine/session/server/test file is exactly the
package's own declared `Files to Modify`/`Tests to Add`. `static/index.html` and `static/style.css`
are **not** individually named in the package's `Files to Modify` list (only `static/app.js`
"and/or a new sibling file" is) — this is `BL-0158`'s first half, adjudicated below as an implied,
necessary consequence of adding the panel, not an unexplained excursion. **Notably absent, as with
every first-pass package in the 2026-09/2026-10 batches:** `IP-1300`'s own package document (no
Status/DoD/checklist boxes updated) and `FS-130`'s `Referenced By` status annotation (still reads
"`READY`, not yet authorized") — see Findings L1. `docs/implementation/01-technical-work-breakdown.md`
also still shows `IP-1300` as `🟡 READY` (same staleness category, a different ledger).

## BL-0158 adjudication

`BL-0158` bundles two distinct concerns; both are adjudicated here as instructed.

1. **File-list omission (`index.html`/`style.css` not named in Files to Modify).** Confirmed real
   but **not a Definition-of-Done defect**: the package's own text already hedges with "and/or a new
   sibling file... mirroring `globe.js`'s own separation from `app.js`," and wiring a new menu entry,
   panel markup, script tag, and panel-specific CSS into `index.html`/`style.css` is exactly the kind
   of "necessary, undeclared-but-expected consequence" `VR-1290`'s own scope audit accepted for a
   constructor-signature change propagating to every call site — the same precedent applies here to a
   new UI panel propagating into the shared shell files every other panel (`tutorial-panel`,
   `inspector`, etc.) already lives in. **Adjudicated: accepted, not a scope excursion, no
   remediation required.**
2. **Browser panel verified only by `node --check` + a served-asset test, not driven live.**
   Independently confirmed this is **exactly the standing project norm, not a lower bar for this
   package**: `VR-1174` (Vignette Creator UI Surfaces), `VR-1220`, and every other UI-touching
   package in this verification index was verified the same way — API-level probing of the routes
   the client-side code calls, plus `node --check`/served-file tests for the JS itself, never an
   actual browser-driven session (no VR report in this index's history mentions `run-spacesim` or a
   screenshot). `CLAUDE.md`'s own standing text ("The browser GUI is unverified headless... every
   backend path is test-covered") is stated as the project's *accepted* standard, not an aspiration
   `IP-1300` fell short of. This verification pass went beyond that bar on the backend side: fresh
   `TestClient` probes against two vignettes neither reused from the implementer's tests, plus
   `node --check ricview.js` (passes — confirmed here independently, not merely cited). Reading
   `ricview.js` directly confirms it is a straightforward, correctly-shaped consumer of the documented
   JSON response shape (`v.objects[].ric_r`/`range_m`/`source`, `v.cats.phase_angle_deg`), with no
   logic beyond rendering what the server already returns. **Adjudicated: accepted, meets the
   project's own established UI-verification bar exactly — no stricter, no laxer. No remediation
   required.**

`BL-0158` → **DONE** (both halves adjudicated, no action routed to `08`).

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| L1 | `IP-1300`'s own package document was never updated by the implementing commit (`152754e`) — Status header still reads the pre-implementation `🟡 READY`/"Not authorized for coding," DoD/Verification-Checklist boxes unchecked. `FS-130`'s `Referenced By` metadata still describes `IP-1300` as "`READY`, not yet authorized." `docs/implementation/01-technical-work-breakdown.md`'s per-package table also still shows `IP-1300` as `🟡 READY`. Same documentation-hygiene pattern already recorded as a Low finding against every other first-pass package in the 2026-09/2026-10 batches (`VR-1220`/`VR-1240`/`VR-1250`/`VR-1270`/`VR-1290`/`VR-1280`). Functional work is complete and correct. | Low | `08-code-implementation` (doc-only follow-up) |
| L2 | `BL-0158`'s file-list-omission half (see adjudication above) is a real, if harmless, package-authoring gap: `07-implementation-planning` should name `static/index.html`/`static/style.css` explicitly whenever a package's own design calls for a new menu entry/panel, the same way it already names the JS file, so this class of "implied but unlisted" file doesn't recur. | Low | `07-implementation-planning` (process note for future packages, not a defect in this one) |

## Related

[IP-1300](../packages/IP-1300-ric-frame-view-and-cats-overlay.md) · [FS-130](../../features/FS-130-ric-frame-view-and-cats-overlay.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md) ·
[docs/pipeline/backlog.md](../../pipeline/backlog.md) `BL-0157` (training-manual coverage, unblocked by
this report — routed to `08-training-manual-authoring`), `BL-0158` (adjudicated `DONE` above)
