# VR-1086 — Verification Report: One Shared Asset Validator at Every Authoring Boundary (FR-5310, FR-5311, FR-5220, FR-5110; H-3, M-1, M-3)

> **Document ID:** VR-1086
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1086](../packages/IP-1086-authoring-boundary-validation.md) v1.0
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → IN PROGRESS` return of `IP-1086` (no `VERIFIED` transition)
> **Feature Mapping:** [FS-131](../../features/FS-131-load-time-vignette-validation.md), [FS-119](../../features/FS-119-bulk-tle-omm-import.md), [FS-117](../../features/FS-117-vignette-creator.md), [FS-120](../../features/FS-120-save-as-scenario.md)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

IP-1086 v1.0, implementing commit `107a787` on branch `claude/ip-1086-build` (parent `00ad25f`). Verified in a fresh
session in a separate worktree; the implementation was not done in this session. Nothing under `engine/` or
`ui_web/` changed (`git diff HEAD~1 -- spacesim/engine spacesim/ui_web` is empty).

## Result

**RETURNED** — 3 failed checks, all test coverage; 0 behavioural defects. The shipped behaviour is correct on every
path I drove; what is missing is the evidence the package itself asked for (tests that pin two validator rules and one
read guard, and three of the specified tests). Two Low observations besides.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| A TLE that cannot propagate at the start epoch is refused with a reason on every path, same verdict from each | Own harness (below) over 6 failing TLE element sets (high-drag stale epoch, decayed low perigee, mean motion 0 / 30, e near 1, garbage): refused with `TLE does not parse/propagate: sgp4 propagation error code N` at load (400 `invalid_vignette`), `PUT /creator/state`, `PATCH /creator/asset`, `POST /force/tle` (real and draft session), TLE bulk import (per object); the same string at load and Creator; a valid companion object in each bulk batch imports | pass |
| Unphysical elements, negative resources, bad ids refused at Creator, OMM import, load gate | `e` 1.5 / 1.0 / -0.1, `a_m` -5 / 1000, `e` 0.999 sub-surface, `i` 200, negative `delta_v_ms`/`ammo`/`power_w`, ids `../x`, `a b`, `.hid`: refused with the same reason string at load, PUT, PATCH, and (elements) OMM KVN bulk import with a valid companion imported. Non-finite elements refused by the function (engine-level probe) | pass |
| Invalid Creator vignette cannot be saved (400, no file); a saved vignette loads | No-orbit satellite and no-location station: `POST /save_vignette` 400 naming asset and rule; stale TLE injected below the edit gate: `ValueError`, no file; valid draft saves 200 and loads 200 | pass |
| `scene`, `windows`, `next_contacts`, `creator/scene` never 500 on an un-propagatable asset | A real TLE valid at the start and decayed after +2 h (force-added, `start`, `step` 3 h): parent 500s, fix 200 on scene (asset omitted), windows (`[]` + `error: propagation_failed`), next_contacts (`null`), view, alarms, orders, telemetry, godview, controller_view; red scene unchanged. e=1.5 injected into the world below the gate: same (builder test) | pass |
| Per-object bulk reporting and iterative Creator composition preserved | Bulk batches report each object in order; incomplete asset (no orbit) still accepted by PUT | pass |
| New tests green; fixtures migrated; RTM regenerated; full suite, browser, gates, doc checks green; no allow-list grew | See Test run; `--origin-report=rtm` leaves `git status` clean; `git show --stat` shows no allow-list file | pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| Re-derive H-3 on the parent and on this commit | Scratch copy of the parent (`git archive HEAD~1`): stale-epoch TLEs are accepted by `/force/tle` (200 `ok: true`, real and draft), by bulk import, by PUT/PATCH; `/scene`, `/windows`, `/next_contacts` 500 after `start`, `/creator/scene` 500. Fix: refused with reason, reads 200. The builder's note holds: the real 2024 ISS TLE (mean motion 15.5) propagates in 2030 under sgp4 2.27, so I used decay-prone sets that fail with sgp4 code 1/2/4/6 at 2030 | pass |
| Re-derive M-1 and M-3 | Parent: `e` 1.5 and `a_m` -5 accepted by PUT, load 200, then scene 500; invalid drafts save 200 and load 400. Fix: first PUT refused; save 400 and no file | pass |
| No second TLE/element validation outside the shared function | `grep twoline2rv/Satrec/.rv(/R_EARTH_EQ/_ID_RE` over `content/` and `session/`: only `asset_authoring_problems` validates (other `.rv` sites are ephemeris, scene and objective metrics) | pass |
| Every shipped vignette still loads; bounds as stated; dropped rules recorded | All 19 vignettes: load, force-add an in-epoch TLE, start, step 30 min, scene/next_contacts for both cells, `GET /save` then `load_save`, save-as-scenario then load: 19/19 clean (0 false refusals). No rule was dropped | pass |
| `PUT /creator/state` accepts an incomplete asset; save refuses it | Own probe and `test_creator_put_still_accepts_incomplete_assets` | pass |
| `engine/` byte-unchanged; gates, doc checks, browser suite green | See Test run | pass |

## Requirements audit

| Req | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| FR-5311 | `asset_authoring_problems` TLE branch, called by all paths | agreement table, force/bulk/PUT/PATCH matrix | Test column lists the new module; regeneration is a no-op | pass |
| FR-5310 | Keplerian bounds, resources, id charset | bounds matrix (`e` range and non-finite rules are not pinned, F1) | same | pass with F1 |
| FR-5312 | presence unchanged | incomplete-asset test | same | pass |
| FR-5220 | per-object failure for stale/unphysical objects | bulk and OMM tests | same | pass |
| FR-5110 | `save_vignette` pre-write validation | invalid-draft matrix, bad-TLE, valid round trip | same | pass |
| FR-5120, FR-5150 | PUT/PATCH refusal naming the asset | parametrised tests | same | pass |
| NFR-1600 | scene/window guards | poisoned-world tests (only an `e` 1.5 asset, F2) | same | pass with F2 |

All `verifies` markers name live baseline IDs (the origin suite is green).

## Independent probes

- **Reproduction on the parent** (private `git archive HEAD~1` copy, builder tests not used): stale TLE accepted at force-add/bulk/PUT/PATCH and the reads 500; `e` 1.5 / `e` 1.0 / `a_m` -5 reach a 500 scene; `e` -0.1, `a_m` 1000, sub-surface perigee, `i` 200, negative resources and bad ids are accepted at every gate; invalid drafts save with 200 then fail to load. All of these are refused with a reason on the fix.
- **No divergence.** The same bad object through the load gate (yaml in an external dir), PUT, PATCH and OMM/TLE force-add yields the same reason text for TLE, `e`, `a_m`, perigee, `i`, resources and id. The one intentional asymmetry: `add_tle` keeps its earlier 69-character line pre-check, which rejects garbage before the shared function runs.
- **Old saves replay.** Saves written by the parent (3 vignettes, started, 45 minutes stepped) load on the fix; the godview equals the parent's except the lazy wall-clock `now`, which differs by microseconds.
- **Decaying TLE read paths.** See DoD row 4; the other cell's picture is unchanged (fog intact), the fleet view still lists the asset.
- **Test migration.** The diff of the ten migrated modules is 24 changed lines, all the TLE fixture substitution (`in_epoch_tle()`); no assertion changed. `tle_helpers.in_epoch_tle` builds a 2030-epoch ISS-like set through `state_to_tle`, deterministic and cached. `test_white_only_controls.py` is migrated although Design Decision 7 does not list it (in scope by intent).

## Mutation testing

16 mutations, run in a private copy against the new module plus the load-validation, Creator-session, bulk-import-session and scene tests.

| Mutation | Result |
|---|---|
| drop id rule / resources rule / TLE propagation / perigee rule / inclination rule | killed |
| skip validation at load gate / `add_tle` / OMM / `creator_set_state` / `creator_edit_asset` | killed |
| skip pre-save validation | killed |
| scene asset guard removed / windows guard removed | killed |
| **drop the `0 <= e < 1` rule** | **survives** — the perigee rule (`a*(1-e) <= R`) still refuses `e` 1.5 and 1.0, so only a negative `e` (-0.1, refused on the fix, probe above) is exposed and no test uses one |
| **drop the non-finite rule** | **survives** — no test passes a non-finite element (the HTTP finite-JSON guard hides it, so it needs an engine-level case) |
| **remove the belief-track guard in `build_scene`** | **survives** — no test has an un-propagatable `Track.state_estimate` |

## Test run

| Command | Result |
|---|---|
| `python3 -m pytest -q --junitxml=…` (unfiltered) | exit 0; 1960 tests, 0 failures, 0 errors, 3 skipped (pre-existing "vignette does not accept order" skips) |
| `python3 -m pytest -q -m "not browser" --junitxml=…` | exit 0; 1927 tests, 0 failures, 4 skipped (the 3 above + the partial-collection RTM equality skip, which runs in the unfiltered run) |
| `python3 -m pytest -q -m browser -rs --junitxml=…` | exit 0; 33 tests, 0 failures, 0 skipped |
| `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`, `test_test_origins.py`, `test_origin_retag.py` | exit 0; 231 tests, 0 failures, 1 skipped |
| `python3 -m pytest --origin-report=rtm` | no diff; the committed Test column equals the tool output |
| `test_authoring_boundary_validation.py` | 46 passed |

## Scope audit

The implementing diff is `content/vignette.py`, `content/vignette_export.py`, `session/manager.py`, `session/scene.py`, the new test module, the new helper `tests/tle_helpers.py` (the package allows "conftest or a helper module beside it"), ten migrated test modules, `CLAUDE.md`, RTM, MBP, packages index and ROADMAP. `server.py` and `engine/` untouched, as the package states. `next_contacts` has no code change because it calls `windows_ahead` (the guard is inherited; covered by mutation "windows guard"). Ledger audit: MBP tally before this report recounts to 86 VERIFIED / 1 COMPLETE / 2 READY / 89 total.

## Findings

| ID | Finding | Severity | Owner |
|---|---|---|---|
| F1 | Two validator rules survive deletion: the `0 <= e < 1` rule (no negative-`e` case; `e` 1.5 and 1.0 are caught by the perigee rule instead) and the non-finite-elements rule. The package's Tests to Add item 7 lists non-finite elements, and its Unit 2 table lists `e` rules; neither is pinned. Add `e: -0.1` (PUT, PATCH, load, OMM) and a NaN / inf element case at the function level | Medium (hard fail of the "each rule has a test" bar) | `08-code-implementation` re-run |
| F2 | Package tests 13 and 14 are not delivered as specified. 14: no read test with a TLE that is valid at start and decays later (the poisoned-world fixture uses only `e` 1.5), so the real sgp4 failure path (`ValueError` from the propagator mid-exercise) and the belief-track guard in `build_scene` are unpinned. 13: item 13 asks for a browser test of the Creator console showing the 400 text; the delivered `test_creator_console_surfaces_refused_save_message` only greps `creator.js`/`app.js` for the strings `save_vignette` and `detail` (near-vacuous) | Medium | `08-code-implementation` re-run |
| F3 | Whole-package consequence of F1/F2: the mutation bar the verifier applies (every rule and every call site killed by a test) is not met for 3 of 16 mutations | (covered by F1/F2) | — |
| O1 | `POST /force/ground` is not routed through the shared validator: an id such as `.hid` (allowed by the route's `^[A-Za-z0-9_.\-]{1,64}$` pattern, refused by the shared rule's no-leading-dot) is accepted in a draft and only refused at save (400 with the reason). No crash; the package names force-add TLE/OMM/edit only | Low | `07` note for a later pass |
| O2 | The Creator console's TLE-paste form (`creator.js::addTle`) discards the `Ack`, so a now-common refusal (`ok: false` plus reason) is not shown to the author; the JSON view and save already show theirs. UI is outside this package's file list | Low | `08` UI follow-up / `05` |

## Next step

Re-run `08-code-implementation` on `IP-1086` for F1 and F2 (tests only; no production change is needed, I found no behavioural defect). Then re-run `09-package-verification`; the green full suite, browser suite, gates and the 19-vignette sweep above need only be repeated against the new commit.
