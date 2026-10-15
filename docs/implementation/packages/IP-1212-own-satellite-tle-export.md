# IP-1212 — Quick TLE Export for a Cell's Own Satellites (FR-7440 amendment)

> **Package ID:** IP-1212
> **Version:** 1.0
> **Status:** ✅ VERIFIED — VERIFIED 2026-10-15 ([VR-1212](../verification/VR-1212-own-satellite-tle-export.md), `09-package-verification`, fresh session): own-satellite export without a held track, ownership-beats-a-held-track precedence, the cross-cell fog-of-war rejection, and the no-orbit rejection all independently reproduced on `geo-rpo-shadowing`/`BLUE-HVA`, distinct from this package's own fixtures, at both the function and HTTP levels. The superseded `test_quick_tle_own_asset_without_track_rejected` confirmed fully removed with no leftover contradicting assertion anywhere in the tree. Full suite 852 passed/3 skipped (855 collected) and both permanent gates (14) independently re-run and confirmed. 1 Low finding (`BL-0203`): `FS-121`'s `Referenced By` stale-tag, same pre-existing pattern as `BL-0183`/`BL-0193`, not a defect in this package.
> *(COMPLETE 2026-10-15, `08-code-implementation`, pipeline run #119): `quick_tle` own-asset branch ahead of the track lookup (`source: "own"`, own asset without orbit rejected, stale message fixed); `tleexport.js` picker lists own on-orbit satellites + `SOURCE_LABEL`; `get_tle`/route docstrings. Replaced the superseded `test_quick_tle_own_asset_without_track_rejected`; 5 new tests (Tests 1, 3, 4, 5 observed failing first; Test 2 passed on arrival as intended). Full suite 852 passed/3 skipped (855 collected, JUnit; baseline 848/3), both permanent gates green (14).)*
> *(Authored 2026-10-15 by `07-implementation-planning`, pipeline run #118.)*
> Authorized by the project owner 2026-10-11 (MSTR-006 §3) through the standing pre-authorization of
> the packages this iteration reaches. Same precedent as `IP-1261`/`IP-1262`/`IP-1063`.
> **Dependencies:** [FS-121](../../features/FS-121-ephemeris-export.md) v2.1 (`FR-7440`, System
> Behaviour "state source" and "Rejection", Acceptance Criteria 7 and 11),
> [IP-1211](IP-1211-quick-tle-export.md) (`VERIFIED`, `VR-1211`; this package supersedes its
> Design Decision 5 only)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0201` (from
> `BL-0159`), [requirements update report](../../reviews/requirements-update-parked-questions-batch.md)
> **Produces:** a cell-scoped quick TLE export that accepts the requesting cell's own satellites
> (from their actual orbit, no `Track` needed), while another side's untracked satellite is still
> rejected
> **Feature Reference:** [FS-121 — Ephemeris & TLE Export](../../features/FS-121-ephemeris-export.md)
> v2.1 (`FR-7440`)
> **Supersedes:** `IP-1211` Design Decision 5 only (own asset without a `Track` rejected). Every
> other `IP-1211` decision stands.
> **Related Topics:** [`spacesim/session/ephemeris.py`](../../../spacesim/session/ephemeris.py),
> [`spacesim/ui_web/static/tleexport.js`](../../../spacesim/ui_web/static/tleexport.js)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*This is a remediation package. Source: `BL-0201`. On 2026-10-15 `04-requirements-engineering`
amended `FR-7440` (`BL-0159`): "visible" now means `FR-6210`'s view, the cell's own satellites
plus its held tracks. `06-feature-specification` then raised `FS-121` to v2.1. `IP-1211` is
`VERIFIED` against the pre-amendment text and is not reopened. Numbered `IP-1212` as the next slice
in the `FS-121` series. Every file, function and line cited below was checked against the tree at
`9cb18e8`.*

## Package ID

IP-1212

## Title

Quick TLE Export for a Cell's Own Satellites (FR-7440 amendment)

## Objective

Today `session/ephemeris.py::quick_tle` (`:212-252`) serves a named cell only from that cell's own
`Track` on the object. A cell holds no `Track` on its own fleet, so `GET /tle/blue?object_id=<a Blue
satellite>` returns 404 *"blue holds no track … (own-asset export is not yet in scope)"*. The
console's TLE picker (`tleexport.js::candidates`, `:12-24`) doesn't offer own satellites at all.

After this package:

- A cell-scoped request for a satellite **the requesting cell owns** returns a TLE fitted to that
  satellite's actual orbit (`Asset.orbit`, `ADS-1500` Decision 5). No `Track` is needed.
  **Ownership decides:** even if the cell somehow also holds a `Track` on its own satellite, the
  actual orbit is used.
- A request for another side's satellite is unchanged. The cell's own `Track.state_estimate` is
  used if held; otherwise the request is rejected.
- An own asset with no orbit (e.g. a ground station) is rejected with a reason.
- The cell's TLE picker lists its own on-orbit satellites as well as its tracks, and labels the
  source of each TLE.

### Design Decisions

1. **One new branch in `quick_tle`, at the top of the cell path.** It mirrors `_live_state`'s
   existing own-asset rule (`:116-136`): `asset is not None and asset.owner == cell`. It goes in
   the cell branch *before* the `track_for` lookup, so ownership wins over a held track (FS-121 v2.1
   System Behaviour). It reuses the same `_PROP.rv` → `orbit_to_tle` path as the other two
   branches, so no new conversion code is added and `IP-1211` Design Decisions 1–4 (fit method,
   identity, rejection of unrepresentable orbits, read-only) apply unchanged.
2. **A distinct `source` value, `"own"`.** It is not `"truth"`, which today marks White's no-cell
   ground-truth path, and not `"track"`. A cell reading its own satellite is not White's god-view,
   and the label lets the console say *"your satellite (actual orbit)"*. The response shape is
   otherwise identical (same keys).
3. **The untracked rejection message drops its stale parenthetical.** "(own-asset export is not yet
   in scope)" becomes false. The message keeps the word "track", which the existing
   `test_tle_route_untracked_is_404` asserts.
4. **White's path is unchanged.** `get_tle("white", …)` still calls `quick_tle(godview, None, …)`.
   The new branch only runs when `cell is not None`.
5. **Picker candidates.** For a non-White cell, add every entry of `ASSETS` (which, in a cell view,
   holds only that cell's `own_assets` plus `own_sensors`, per `app.js` refresh `:1184`) whose kind
   is an on-orbit kind. Use the same kind filter White's branch already applies (`:15-19`): not
   `ground*`, not `space_based`, no `network`. Then add the tracks as today. The server stays the
   only enforcer: the picker is a convenience, and a hand-crafted request is still filtered at the
   boundary.

## Feature Reference

- **FS-121** v2.1: System Behaviour "Quick TLE export — state source" (new own-satellite branch) and
  "Rejection (edge cases)" (narrowed); Error Handling (narrowed untracked rule); Security
  Considerations (the ownership check stays at the boundary); Acceptance Criteria 7 (reworded) and
  11 (new); Open Question 5 (closed).

## Requirements Covered

| Requirement | How |
|---|---|
| `FR-7440` (amended 2026-10-15) | Own satellites are exportable from their actual orbit. Another side's untracked satellite is still rejected. No cell-scoped TLE of a non-owned satellite is derived from truth. |

`FR-6210` is consumed, not changed: the own-asset rule is exactly what the cell's view already
exposes. No requirement text is changed by this package.

## Architecture Components

- `session/ephemeris.py` (`quick_tle`): the one behavioural change.
- `session/manager.py` (`get_tle`) and `ui_web/server.py` (`GET /tle/{cell}`): docstrings only.
- `ui_web/static/tleexport.js`: picker candidates and the source label.
- `engine/` is untouched (`engine/tle_export.py` is reused as-is). The import guard and
  determinism gates are unaffected by construction.

## Interfaces

- `quick_tle(world, cell, object_id) -> dict` keeps its signature. For `cell` naming the owner of
  `object_id`, it now returns `source: "own"` instead of raising `ValueError`.
- `GET /api/sessions/{sid}/tle/{cell}?object_id=` now returns **200** for an own on-orbit
  satellite, and **404** (with a reason) for an own asset without an orbit. Every other case is
  unchanged.
- `INT-0006`/`INT-0007` are unchanged.

## Files to Create

None.

## Files to Modify

| File | Change |
|---|---|
| `spacesim/session/ephemeris.py` | `quick_tle` (`:212-252`): add the own-asset branch (Design Decision 1) with `source = "own"` (Decision 2); reject an own asset whose `orbit is None`; drop the stale parenthetical from the untracked message (Decision 3). Rewrite the docstring's Design Decision 5 sentence to cite `IP-1212`/`FR-7440` (amended). |
| `spacesim/session/manager.py` | `get_tle` docstring (`:928-936`): a cell exports its own satellites from their actual orbit and others only from its own `Track`. |
| `spacesim/ui_web/server.py` | `get_tle` route docstring (`:738-748`): same wording. |
| `spacesim/ui_web/static/tleexport.js` | Header comment (`:2-7`); `candidates()` (`:12-24`) adds own on-orbit satellites for a non-White cell (Decision 5); the source label (`:55`) gains `"own"` → "your satellite (actual orbit)"; the empty-picker hint (`:46`) no longer says only tracks qualify. |
| `spacesim/tests/test_ephemeris.py` | Replace `test_quick_tle_own_asset_without_track_rejected` (`:438-444`), which encodes the superseded Design Decision 5, with the new tests below. This is the only pre-existing test this package may change. |
| `spacesim/tests/test_web.py` | New route-level tests (below). |

## Implementation Tasks

1. Write Tests 1–5 first and observe them fail against the current tree: Test 1 and Test 3 raise
   `ValueError`; Test 4 returns 404; Test 5's served-JS assertion is absent. Test 2 guards the
   unchanged cross-cell rejection, so it should pass on arrival.
2. Remove `test_quick_tle_own_asset_without_track_rejected`. Its replacement is Test 1. Record the
   removal and the reason (Design Decision 5 superseded by amended `FR-7440`) in the Implementation
   Summary.
3. Implement Design Decisions 1–3 in `quick_tle`.
4. Update the two docstrings (Decision 4 notes White is unchanged).
5. Update `tleexport.js` (Decision 5 and the label).
6. Run the full suite plus both permanent gates.
7. Update the documentation and ledgers (below).

## Tests to Add

All in the existing fixtures' style. `_two_sat_manager_with_track` gives Blue `SAT-BLUE` and Red
`SAT-RED`, and Blue holds a `Track` on `SAT-RED`.

1. **`test_quick_tle_own_satellite_uses_actual_orbit`** (`test_ephemeris.py`). `quick_tle(world,
   "blue", "SAT-BLUE")` returns `source == "own"`, 69-character lines, and an SGP4 position at its
   epoch within `ROUND_TRIP_BOUND_M` of `SAT-BLUE`'s propagated `Asset.orbit` (FS-121 AC11).
2. **`test_quick_tle_other_cell_still_rejected_for_untracked_satellite`** (`test_ephemeris.py`).
   `quick_tle(world, "red", "SAT-BLUE")` still raises `ValueError` mentioning "track": Red owns
   nothing named `SAT-BLUE` and holds no track on it (AC7 and AC11's cross-cell negative).
3. **`test_quick_tle_ownership_beats_a_held_track`** (`test_ephemeris.py`). Give Blue a `Track` on
   its own `SAT-BLUE` whose `state_estimate` is deliberately offset (e.g. `ta_deg + 30`). The TLE
   still reproduces the actual orbit (within the bound) and not the offset estimate (more than
   10 km away), and `source == "own"`.
4. **`test_tle_route_own_satellite_200`** (`test_web.py`). On `_coorbital_session`, find a Blue-owned
   satellite id from `/godview`. `GET /tle/blue?object_id=<it>` returns 200 with `source == "own"`
   and `cell == "blue"`. `GET /tle/red?object_id=<it>` returns 404. Separately, on a
   `leo-isr-denial` session (`_new_session`), the Blue-owned ground station `GS-NORTH` (an own
   asset with no orbit; `co-orbital-threat-escort` has none, because its `BLUE-RADAR` is a sensor,
   not an asset) returns 404 with a reason from `GET /tle/blue?object_id=GS-NORTH`.
5. **`test_tle_export_client_lists_own_satellites`** (`test_web.py`). The served `/tleexport.js`
   contains the `"own"` source label. This is a static-surface check in the style of
   `test_tle_export_client_surface_is_served`; the GUI itself is unverified headless, per project
   posture.

`test_quick_tle_is_read_only`, `test_quick_tle_cell_uses_own_track_belief`,
`test_quick_tle_rejects_untracked_and_stateless_track` and the existing route tests must pass
unchanged.

## Documentation Updates

- RTM (`docs/requirements/03-requirements-traceability-matrix.md`): the `FR-7440` row adds
  `IP-1212` to its Impl. Package cell and names Tests 1–5.
- `CLAUDE.md` code map: if the `session/ephemeris.py` or quick-TLE text says own assets are
  excluded, correct it; otherwise add one clause that a cell exports its own satellites from their
  actual orbit.
- `docs/training/15-manual-traceability.md` §15.1 "Quick TLE export" row: this changes
  operator-visible behaviour (own satellites now in the picker and exportable). Route a
  manual-impact finding for `WCM-14`/`BLU-12`/`RED-11` to `08-training-manual-authoring`; do not
  edit `docs/training/` from `08-code-implementation`.
- This package's Status header, the Master Build Plan row, `packages/INDEX.md`, `ROADMAP.md`'s
  implementation-package row, and `FS-121`'s `Referenced By` (metadata only).

## Definition of Done

- A cell-scoped TLE request for the cell's own on-orbit satellite returns a well-formed TLE from
  its actual orbit, with `source == "own"`, at the session layer and over HTTP.
- Another side's untracked satellite is still rejected. White's path is byte-for-byte unchanged.
  An own asset without an orbit is rejected with a reason.
- Ownership beats a held track.
- The console picker offers own on-orbit satellites to a non-White cell and labels the source.
- The superseded test is replaced and every other pre-existing TLE test passes unchanged.
- The full suite is green, and `test_determinism.py` and `test_import_guard.py` are green.
- The RTM, `CLAUDE.md` and the ledgers are updated, and the manual-impact finding is routed.

## Verification Checklist

- [x] `git diff` of the implementing commit touches no file under `spacesim/engine/`.
- [x] Read `quick_tle`: the own-asset check runs in the cell branch **before** `track_for`, and
      `cell is None` (White) never reaches it.
- [x] Tests 1–5 exist and pass. Tests 1, 3, 4 and 5 were observed failing first, as recorded in the
      Implementation Summary.
- [x] Independent reproduction on a fresh session and a vignette other than the tests':
      `GET /tle/<cell>?object_id=<own satellite>` returns 200 with `source: "own"`; the other
      cell's request returns 404.
- [x] The only pre-existing test changed is `test_quick_tle_own_asset_without_track_rejected`
      (removed, replaced by Test 1); `git diff` on the test files shows that and additions only.
- [x] `python3 -m pytest` passes in full, and `test_determinism.py` and `test_import_guard.py` pass.
- [x] The RTM `FR-7440` row cites `IP-1212`.
- [x] The Master Build Plan row, the `packages/INDEX.md` row, `ROADMAP.md`'s row and this header
      agree on status.

**Independently verified `09-package-verification` (fresh session), 2026-10-15 — see
[VR-1212](../verification/VR-1212-own-satellite-tle-export.md). `COMPLETE → VERIFIED`.**

## Dependencies

- **Packages:** `IP-1211` (`VERIFIED`, `VR-1211`). Its function is the one modified, so this
  package is `READY`.
- **Spec/requirement:** `FS-121` v2.1 and amended `FR-7440`, both landed (runs #116–#117).
- **Authorization:** granted by the project owner 2026-10-11 (MSTR-006 §3) through the standing
  pre-authorization of this iteration's packages.
- **Parallelism:** there is no ordering constraint with any other open package.

## Risks

- **Fog-of-war regression.** The new branch must not let a cell read a *non-owned* satellite at
  truth. Test 2 and the route's cross-cell 404 in Test 4 guard this. A reviewer should also confirm
  the branch tests `asset.owner == cell` and nothing broader.
- **`source` value consumers.** Only `tleexport.js` reads the TLE payload's `source` (checked
  `\.source` across `static/`: the other hits, `ricview.js` and `app.js:1226`, read different
  payloads). A new value is additive, and the label change covers it.
- **Picker kind filter.** Reusing White's filter could include a kind with no orbit if a vignette
  authors one. The server rejects such a request with a reason (Test 4's ground-station case), so
  the worst case is a picker entry that returns an explained error, not a wrong TLE.

## Rollback Considerations

Reverting the implementing commit restores `IP-1211`'s behaviour exactly: own satellites are
rejected again, and the superseded test returns. There are no schema, persisted-format or
`SavedSession` changes. The only externally visible change is that previously-404 own-satellite
requests now return 200.
