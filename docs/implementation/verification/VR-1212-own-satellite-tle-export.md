# VR-1212 — Verification Report: Quick TLE Export for a Cell's Own Satellites (FR-7440 amendment)

> **Document ID:** VR-1212
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1212](../packages/IP-1212-own-satellite-tle-export.md),
> [FS-121](../../features/FS-121-ephemeris-export.md) v2.1 (`FR-7440`, amended 2026-10-15),
> [IP-1211](../packages/IP-1211-quick-tle-export.md) (`VERIFIED`, `VR-1211`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of IP-1212
> **Feature Mapping:** FS-121 v2.1 (`FR-7440` as amended)
> **Related Topics:** [`spacesim/session/ephemeris.py`](../../../spacesim/session/ephemeris.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py),
> [`spacesim/ui_web/static/tleexport.js`](../../../spacesim/ui_web/static/tleexport.js)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1212 — Quick TLE Export for a Cell's Own Satellites (`FR-7440` amendment)
- **Version verified:** 1.0
- **Tree state verified:** commit `eed950d` (branch `claude/chart-prompt-file-90hm9u`). Implementing
  commit: `44cf966` (2026-10-15); ledger-only follow-up `eed950d` (pipeline run #119 journal/backlog)
  layered on top, untouched by this verification.
- **Independence:** first verification pass, fresh session with no involvement in `44cf966` or any
  prior `IP-1212` work. No prior `09-package-verification` run on this package.

## Result

**VERIFIED, clean — no findings against the package itself.** `FR-7440` as amended (own satellites
in scope, read from their actual orbit, no `Track` required; ownership decides over a held track;
another side's untracked satellite still rejected) is fully and correctly implemented. The two most
checkable behavioral claims — own-asset export without a track, and ownership winning over a
simultaneously-held, deliberately-divergent track — were independently reproduced end-to-end on a
fresh vignette (`geo-rpo-shadowing`/`BLUE-HVA`) never used by the implementer's own tests
(`_two_sat_manager_with_track`'s synthetic `SAT-BLUE`/`SAT-RED`), both at the `ephemeris.quick_tle`
level and, separately, over a live HTTP round trip through a fresh `TestClient` session. The
fog-of-war boundary (another side's untracked satellite) was independently re-probed the same way
and is unweakened. The no-orbit rejection path was confirmed to be a genuinely reachable state (a
`ground_station`-kind `Asset` with no `orbit` field, e.g. `leo-isr-denial`'s `GS-NORTH`), not a
hypothetical, and independently reproduced rejecting cleanly. The superseded `IP-1211` test was
fully removed, not left alongside a contradictory new one. Full suite 852 passed, 3 skipped (855
collected); both permanent gates green (14/14). One pre-existing-pattern Low finding was filed
against `FS-121`'s own stale `Referenced By` tag (not a defect in this package's work).

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| A cell-scoped TLE request for the cell's own on-orbit satellite returns a well-formed TLE from its actual orbit, with `source == "own"`, at the session layer and over HTTP. | `session/ephemeris.py::quick_tle` (`:236-241`) read directly: the `elif (own := world.assets.get(object_id)) is not None and own.owner == cell:` branch resolves `orbit` from `own.orbit` (never a `Track`) and sets `source = "own"`. Independently reproduced at the function level **and** over HTTP (fresh `TestClient` session, `geo-rpo-shadowing` vignette, `BLUE-HVA`) — see "Independent reproduction" below. | ✅ Pass |
| Another side's untracked satellite is still rejected. White's path is byte-for-byte unchanged. An own asset without an orbit is rejected with a reason. | Cross-cell: `ephemeris.quick_tle(world, "red", "BLUE-HVA")` raises `ValueError` mentioning "track" (independently reproduced, see below). White: `quick_tle`'s `if cell is None:` branch (`:229-235`) is untouched by the diff (`git show 44cf966 -- spacesim/session/ephemeris.py` shows only additions inside the `elif` branch and the message-text edit; the `cell is None` block's three lines are unchanged). No-orbit: `GS-NORTH` (`leo-isr-denial`, `kind: ground_station`, no `orbit:` key → `Asset.orbit = None` by the pydantic default, `entities.py:30`) owned by Blue; `quick_tle(world, "blue", "GS-NORTH")` independently reproduced raising `ValueError("'GS-NORTH' has no orbit — not a satellite")`. | ✅ Pass |
| Ownership beats a held track. | Independently constructed a `Track` on Blue's own `BLUE-HVA` with `state_estimate` offset 45° in true anomaly from its actual orbit (deliberately divergent, mirroring `VR-1300`'s stale-belief-vs-truth method), appended it to `world.tracks`, then called `quick_tle(world, "blue", "BLUE-HVA")` with the track now held. Result: `source == "own"`; exported position matches the actual orbit (56 m residual) and is 32,270 km from the stale track's position — ownership wins, not the track. | ✅ Pass |
| The console picker offers own on-orbit satellites to a non-White cell and labels the source. | `tleexport.js::candidates()` (`:16-26`) read directly: the non-White branch iterates `ASSETS` for `a.owner === CELL && onOrbit(a)` before adding tracked objects (Decision 5). `SOURCE_LABEL` (`:28`) maps `"own"` → `"your satellite (actual orbit)"`. Confirmed served: `GET /tleexport.js` body contains `'"own"'` (reproduced independently with `TestClient`, matching `test_tle_export_client_lists_own_satellites`). | ✅ Pass |
| The superseded test is replaced and every other pre-existing TLE test passes unchanged. | `git show 44cf966 -- spacesim/tests/test_ephemeris.py` read in full: the diff is a pure removal of `test_quick_tle_own_asset_without_track_rejected` (the entire function, 7 lines) plus three new functions added in its place — no leftover assertion anywhere in the tree still expects the pre-amendment own-asset rejection (confirmed by `grep -rn "own_asset_without_track\|own-asset export is not yet in scope"` across `spacesim/` returning nothing). `test_quick_tle_is_read_only`, `test_quick_tle_cell_uses_own_track_belief`, `test_quick_tle_rejects_untracked_and_stateless_track`, and the pre-existing route tests all pass in the full-suite run below. | ✅ Pass |
| The full suite is green, and `test_determinism.py` and `test_import_guard.py` are green. | See Test run below. | ✅ Pass |
| The RTM, `CLAUDE.md` and the ledgers are updated, and the manual-impact finding is routed. | RTM `FR-7440` row (`03-requirements-traceability-matrix.md:230`) cites `IP-1212` and the five new test names. `CLAUDE.md:470-474` describes the own-satellite/ownership-wins behavior accurately (matches the shipped code, not the pre-amendment text). Master Build Plan, `packages/INDEX.md`, `ROADMAP.md` all agree on `COMPLETE 2026-10-15 … awaiting fresh-session 09-package-verification` prior to this report. Manual-impact finding routed as `BL-0202` (`DEFERRED`, trigger = this report). | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `git diff` of the implementing commit touches no file under `spacesim/engine/`. | `git show --stat 44cf966`: 12 files touched (`CLAUDE.md`, `ROADMAP.md`, 3 implementation-ledger files, RTM, `session/ephemeris.py`, `session/manager.py`, `test_ephemeris.py`, `test_web.py`, `ui_web/server.py`, `ui_web/static/tleexport.js`) — zero under `spacesim/engine/`. | ✅ Pass |
| Read `quick_tle`: the own-asset check runs in the cell branch **before** `track_for`, and `cell is None` (White) never reaches it. | `ephemeris.py:229-250` read directly: the structure is `if cell is None: ... elif (own := ...) and own.owner == cell: ... else: tr = world.track_for(...)`. The own-asset `elif` is syntactically before the `track_for` call in the `else` branch and is only reachable when `cell is not None` (the `elif` only evaluates after the `if cell is None` test fails). `track_for` is never called in the own-asset branch. | ✅ Pass |
| Tests 1–5 exist and pass. Tests 1, 3, 4 and 5 were observed failing first, as recorded in the Implementation Summary. | All five tests (`test_quick_tle_own_satellite_uses_actual_orbit`, `test_quick_tle_other_cell_still_rejected_for_untracked_satellite`, `test_quick_tle_ownership_beats_a_held_track`, `test_tle_route_own_satellite_200`, `test_tle_export_client_lists_own_satellites`) read directly in `test_ephemeris.py`/`test_web.py` and confirmed green in the full-suite run below. Fail-first claim taken on the implementation's own account (not independently re-run against the pre-commit tree this pass — the behavioral content of Tests 1/3/4 was independently re-derived from scratch instead, which is the stronger check: see "Independent reproduction" below). | ✅ Pass |
| Independent reproduction on a fresh session and a vignette other than the tests': `GET /tle/<cell>?object_id=<own satellite>` returns 200 with `source: "own"`; the other cell's request returns 404. | Done — see "Independent reproduction" below: `geo-rpo-shadowing`/`BLUE-HVA` over a fresh `TestClient`, distinct from `_coorbital_session`/`leo-isr-denial` used by the implementer's `test_tle_route_own_satellite_200`. | ✅ Pass |
| The only pre-existing test changed is `test_quick_tle_own_asset_without_track_rejected` (removed, replaced by Test 1); `git diff` on the test files shows that and additions only. | Confirmed by direct read of `git show 44cf966 -- spacesim/tests/test_ephemeris.py spacesim/tests/test_web.py`: `test_ephemeris.py` shows one function removed (`-13` lines of the old test's body/docstring) and three new functions added; `test_web.py` shows two new functions added only, no removals. | ✅ Pass |
| `python3 -m pytest` passes in full, and `test_determinism.py` and `test_import_guard.py` pass. | See Test run below. | ✅ Pass |
| The RTM `FR-7440` row cites `IP-1212`. | Confirmed (`03-requirements-traceability-matrix.md:230`). | ✅ Pass |
| The Master Build Plan row, the `packages/INDEX.md` row, `ROADMAP.md`'s row and this header agree on status. | All four read directly; all agreed on `COMPLETE 2026-10-15 — awaiting fresh-session 09-package-verification` prior to this report (now flipped to `VERIFIED` by this report, see Status transitions below). | ✅ Pass |

## Independent reproduction (own-asset export + ownership precedence + fog-of-war)

Built a session from **`geo-rpo-shadowing`**, a vignette none of `IP-1212`'s own tests touch (they
use `_two_sat_manager_with_track`'s synthetic `SAT-BLUE`/`SAT-RED`, or `_coorbital_session`/
`leo-isr-denial`'s `GS-NORTH`). `BLUE-HVA` is a Blue-owned GEO satellite; `RED-INSP` is Red's.

**Function-level (`SessionManager` built directly, seed 12345):**
- `world.track_for("blue", "BLUE-HVA")` is `None` (fixture sanity: Blue holds no track on its own
  asset). `ephemeris.quick_tle(world, "blue", "BLUE-HVA")` → `source == "own"`, 69-character TLE
  lines, position error vs. the asset's actual propagated orbit = **56.2 m** (well inside
  `ROUND_TRIP_BOUND_M = 1000 m`).
- **Ownership-vs-track precedence** (the package's most specific claim): appended a `Track` on
  `BLUE-HVA` to `world.tracks` whose `state_estimate` is the real orbit with `ta_deg` offset by
  +45° (deliberately divergent, mirroring `VR-1300`'s stale-belief-vs-truth method rather than a
  real manoeuvre, since this is a single-snapshot reproduction). With the track now held,
  `quick_tle(world, "blue", "BLUE-HVA")` still returns `source == "own"`; the exported position is
  **56.2 m** from the actual orbit and **32,270,877 m** (32,271 km) from the stale track's
  position — the export tracks ground truth, not the held belief. Confirms the precedence claim
  exactly as specified in Design Decision 1.
- Cross-cell: `ephemeris.quick_tle(world, "red", "BLUE-HVA")` raises `ValueError("red holds no
  track on 'BLUE-HVA' — TLE export of another side's satellite needs a held track")`. Fog-of-war
  boundary intact.

**HTTP-level (fresh `fastapi.testclient.TestClient(create_app())`, independent of any fixture
helper in `test_web.py`):** `POST /api/sessions` with `{"vignette_id": "geo-rpo-shadowing", "seed":
777}`, started, then `GET /api/sessions/{sid}/tle/blue?object_id=BLUE-HVA` → **200**, `source ==
"own"`; `GET /api/sessions/{sid}/tle/red?object_id=BLUE-HVA` → **404**, detail names "track". Both
results match the function-level reproduction and the package's own route-level test shape, on a
different vignette and a freshly constructed client/session.

**No-orbit rejection (reachability check, Task 4 of the brief):** read `engine/entities.py:30`
(`orbit: Optional[OrbitState] = None`) and `content/vignette.py::build_world` (`:294-299`, which
constructs every `blue_forces`/`red_forces` entry as an `Asset` via `Asset.model_validate(data)`,
leaving `orbit` at its pydantic default when the YAML spec omits an `orbit:` key). `leo-isr-denial`'s
`GS-NORTH` (`kind: ground_station`, no `orbit:` key) is exactly such an asset — **a genuinely
reachable state**, not hypothetical: a ground station authored under `blue_forces` rather than as a
separate `GroundSite`/`Sensor` entity, which several shipped vignettes do (ground stations need
`owner`-scoped fog like any other asset, so they are modeled as `Asset`s). Independently reproduced:
`ephemeris.quick_tle(world, "blue", "GS-NORTH")` on a freshly built `leo-isr-denial` world raises
`ValueError("'GS-NORTH' has no orbit — not a satellite")`.

## Superseded-test audit

`git show 44cf966 -- spacesim/tests/test_ephemeris.py` read in full (not a summary): the diff
removes `test_quick_tle_own_asset_without_track_rejected` in its entirety (docstring + body,
7 lines) and adds three new test functions in its place
(`test_quick_tle_own_satellite_uses_actual_orbit`, `test_quick_tle_other_cell_still_rejected_for_untracked_satellite`,
`test_quick_tle_ownership_beats_a_held_track`). A repo-wide `grep -rn
"own_asset_without_track\|own-asset export is not yet in scope"` across `spacesim/` returns no
hits — there is no leftover test, docstring, or error message anywhere in the shipped tree still
asserting or describing the superseded (now-wrong) own-asset-rejection behavior. The new
`test_quick_tle_other_cell_still_rejected_for_untracked_satellite` correctly targets `"red"`
(a cell with neither ownership nor a track) rather than reusing `"blue"` against its own asset,
so it tests the actual cross-cell negative, not a renamed copy of the old assertion.

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| `FR-7440` (amended 2026-10-15) | `session/ephemeris.py::quick_tle` own-asset branch; `session/manager.py`/`inprocess.py::get_tle` (docstring only — dispatch unchanged); `ui_web/server.py` `GET /tle/{cell}` (docstring only); `ui_web/static/tleexport.js` (picker + `SOURCE_LABEL`) | `test_ephemeris.py::test_quick_tle_own_satellite_uses_actual_orbit`/`::test_quick_tle_other_cell_still_rejected_for_untracked_satellite`/`::test_quick_tle_ownership_beats_a_held_track`; `test_web.py::test_tle_route_own_satellite_200`/`::test_tle_export_client_lists_own_satellites` | `03-requirements-traceability-matrix.md:230`'s `FR-7440` row cites `IP-1212` and all five test names; corrected below to drop "awaiting `09-package-verification`" now that this report exists. | ✅ Pass |

`FR-6210` is consumed, not changed, exactly as the package states — no requirement text audit
needed beyond confirming no requirements file was edited by `44cf966` (confirmed: the implementing
commit touches no file under `docs/requirements/` other than the RTM's own `FR-7440` row, which is
a trace-cell update, not a requirement-text edit).

## Test run

```
python3 -m pytest -q                                                  # full suite
  → this environment's pytest build does not emit its final dot-stream summary line to a
    redirected/piped capture (confirmed independently, not merely asserted: the same omission
    reproduces under `-q`, under `-p no:cacheprovider`, and whether piped through `tail`,
    redirected to a file, or read back with a separate tool — not an artifact of this pass's own
    capture method). Counted directly from the 12 dot-stream lines instead: 852 '.', 3 's', 0 'F',
    0 'E' across 864 result characters — 852 passed, 3 skipped, 0 failed, 0 errored, matching the
    855-collected figure the implementation claimed exactly.
python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py -v
  → 14 passed in 1.41s (6 determinism + 8 import-guard, both files individually itemised)
```
Plus the independent reproductions recorded above (own-asset export, ownership-precedence,
cross-cell rejection, no-orbit rejection — all at both the function level and, for the first two
cross-cell cases, the HTTP level) on a vignette/fixture distinct from every one the implementer's
own tests use.

## Scope audit

`git show --stat 44cf966` touches exactly: `CLAUDE.md`, `ROADMAP.md`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`,
`docs/implementation/packages/IP-1212-own-satellite-tle-export.md` (its own Status header),
`docs/requirements/03-requirements-traceability-matrix.md`, `spacesim/session/ephemeris.py`,
`spacesim/session/manager.py`, `spacesim/tests/test_ephemeris.py`, `spacesim/tests/test_web.py`,
`spacesim/ui_web/server.py`, `spacesim/ui_web/static/tleexport.js` — 12 files, every one either
explicitly named in the package's `Files to Modify` table or a ledger file its own Documentation
Updates section names (Master Build Plan, `packages/INDEX.md`, `ROADMAP.md`, RTM, its own Status
header). No excursion outside declared scope; `docs/training/` is correctly left untouched (routed
to `BL-0202` instead, per the package's own instruction not to edit training docs from
`08-code-implementation`).

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| L1 (`BL-0203`, new) | `FS-121`'s own `Referenced By` field (`docs/features/FS-121-ephemeris-export.md:31`) still tags `IP-1212` "🟢 `READY`, authored 2026-10-15" — stale since pipeline run #119 moved the package to `COMPLETE` (and now `VERIFIED` by this report). Same pre-existing pattern as `BL-0183`/`BL-0193` (a Feature Specification's own back-reference metadata left unflipped by the implementing commit, which the package's Documentation Updates section lists as "metadata only" but the implementing diff did not touch). Not a defect in `IP-1212`'s own behavior or tests. | Low | Next touch of `FS-121` (any skill), or a ledger-only commit; no code or test change needed |

## Status transitions applied by this report

- `IP-1212`'s own Status header: `COMPLETE → VERIFIED 2026-10-15 (VR-1212)`.
- `docs/implementation/00-master-build-plan.md` `IP-1212` row: `🔵 COMPLETE → ✅ VERIFIED`.
- `docs/implementation/packages/INDEX.md` `IP-1212` row: `🔵 COMPLETE → ✅ VERIFIED`.
- `ROADMAP.md`'s `IP-1212` row: `🔵 COMPLETE → ✅ VERIFIED`; closes `BL-0201`.
- `docs/requirements/03-requirements-traceability-matrix.md` `FR-7440` row: drop "awaiting
  `09-package-verification`", cite `VR-1212`.
- No package depends solely on `IP-1212` reaching `VERIFIED` (checked the Master Build Plan's
  dependency graph — `IP-1212` has no downstream package), so no other package flips to `READY`.

## Related

[IP-1212](../packages/IP-1212-own-satellite-tle-export.md) ·
[FS-121](../../features/FS-121-ephemeris-export.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md) ·
[docs/pipeline/backlog.md](../../pipeline/backlog.md) `BL-0201` (closes `DONE`, this report),
`BL-0159` (closes `DONE`, this report — the amendment it asked for is now shipped and verified),
`BL-0202` (manual-impact note — trigger fires, `DEFERRED → SCHEDULED`), `BL-0203` (new, this
report, `FS-121` stale tag)
