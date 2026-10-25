# VR-1086 — Verification Report: One Shared Asset Validator at Every Authoring Boundary (FR-5310, FR-5311, FR-5220, FR-5110; H-3, M-1, M-3)

> **Document ID:** VR-1086
> **Version:** 2.0 (supersedes v1.0, which `RETURNED` the package)
> **Status:** ✅ Final
> **Dependencies:** [IP-1086](../packages/IP-1086-authoring-boundary-validation.md) v1.0
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1086` (this v2.0 pass; v1.0 produced `COMPLETE → RETURNED`)
> **Feature Mapping:** [FS-131](../../features/FS-131-load-time-vignette-validation.md), [FS-119](../../features/FS-119-bulk-tle-omm-import.md), [FS-117](../../features/FS-117-vignette-creator.md), [FS-120](../../features/FS-120-save-as-scenario.md)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

IP-1086 v1.0 after its re-run: fix commit `cf3f64c` on top of implementing commit `107a787` and the v1.0 report `b871ff3`, branch `claude/ip-1086-build` (parent of the package `00ad25f`). Verified in a fresh session in a separate worktree; this session took no part in the implementation, the re-run or the v1.0 verification.

## Result

**VERIFIED** — 0 failed checks. v1.0's F1 (Medium), F2 (Medium), F3 (derived) and observations O1, O2 (Low) are closed. Three new Info observations, none a failed check.

## Scope of the re-run change

`git diff 107a787 cf3f64c` outside docs and tests is exactly two files: `session/manager.py` (+3 lines: `add_ground_asset` calls the shared validator, O1) and `ui_web/static/creator.js` (+5/-2: the TLE-paste and ground-add handlers now display an `Ack(ok=false)` reason, O2). `git diff 00ad25f HEAD -- spacesim/engine spacesim/ui_web` is `creator.js` only; `engine/` and `server.py` are byte-unchanged, as the package states. No allow-list file changed.

## v1.0 findings re-checked

Mutations were applied one at a time in a private `git archive` copy of the tree and run against `test_authoring_boundary_validation.py` (46+ cases); every mutation fails at least one test.

| v1.0 | Re-check | Result |
|---|---|---|
| F1 `0 <= e < 1` rule survives | Dropped: killed by `test_validator_unit_each_rule_fires_alone`, `test_e_and_nonfinite_rules_hold_at_load_gate_and_creator_and_omm_sites` and others (negative `e` now has a case at load, PUT, PATCH, OMM) | Closed |
| F1 non-finite rule survives | Dropped: killed by the same two tests (NaN / inf of every element, function level plus load gate, PUT, PATCH, OMM force-add) | Closed |
| F1 other rules | Dropped one at a time: perigee, inclination, id charset, leading-dot only, resources, TLE propagation, "a_m missing": each killed (named tests fail, not collateral) | Closed |
| F1 call sites | Skipped one at a time: load gate, force-add TLE, OMM force-add, `add_ground_asset`, `creator_set_state` (PUT), `creator_edit_asset` (PATCH), pre-save validation in `save_vignette`: each killed | Closed |
| F2 decaying-TLE reads | `test_tle_valid_at_start_that_decays_later_never_500s_the_reads` uses a real sgp4 element set accepted at the start and failing after about 6.5 h (not an injected `e` 1.5): at 5.9 h and 7.0 h scene/windows/next_contacts/view/alarms/orders are 200, the asset is omitted only after the decay, `windows` carries `error: propagation_failed`, `next_contacts` is `null`, the red cell is unaffected. Removing the scene asset guard, the windows guard, or the belief-track guard (`test_belief_track_with_an_unpropagatable_estimate_is_omitted_not_a_500`) each fails a test | Closed |
| F2 Creator browser test | `test_creator_browser.py` (marker `browser`) really drives Chromium against the real server: it ran, 3 of 3, 0 skipped in the browser run. Reverting `creator.js` to `107a787` fails the TLE-paste and ground-add tests; commenting out the save-path error display (both `error:` writers) fails the refused-save test (timeout waiting for the result text) | Closed |
| O1 `.hid` on `/force/ground` | Refused at the first call with `asset id '.hid' is not valid ...` (probe and `test_force_ground_applies_the_shared_id_rule[.hid]`); skipping the new call is killed | Closed |
| O2 TLE/ground add show the reason | Browser tests assert the visible `refused: ...` text naming the asset and rule, and that a valid in-epoch TLE shows `TLE added` and appears in the asset list | Closed |

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| A TLE that cannot propagate at the start epoch is refused with a reason on every path, same verdict | Own parity probe (not the builder's tests): the same decay-prone TLE gives `TLE does not parse/propagate: sgp4 propagation error code 1 for TLE asset` at the load gate, PUT, PATCH and force-add (draft and real session); bulk TLE and OMM per object (new tests, mutation-checked) | pass |
| Unphysical elements, negative resources, bad ids refused at Creator, OMM, load gate | Parity probe for `e` 1.5 / -0.1 / 1.0, `a_m` -5, `i` 200, negative `delta_v_ms`, ids `a b` and `.hid`: identical reason text at load, PUT and PATCH (OMM covered by the agreement and OMM tests) | pass |
| Invalid Creator vignette cannot be saved; a saved vignette loads | No-orbit draft: `POST /save_vignette` 400 naming the asset and rule, save directory empty; the 19-vignette sweep below saves and reloads | pass |
| `scene`, `windows`, `next_contacts`, `creator/scene` never 500 on an un-propagatable asset | See F2 row; the parent gives 500 for all of them after the stale-TLE force-add | pass |
| Per-object bulk reporting and iterative composition preserved | `test_bulk_import_stale_is_per_object_failure_valid_imports_malformed_reported`, OMM test, `test_creator_put_still_accepts_incomplete_assets` | pass |
| New tests green; fixtures migrated; RTM regenerated; suites, gates, docs green; no allow-list grew | See Test run; `--origin-report=rtm` leaves `git status` clean | pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| Re-derive H-3 on the parent and on this commit | Own probe on `git archive 00ad25f` and on the worktree. Parent: stale TLE `force/tle` `ok: true`; after `start`, scene / windows / next_contacts all 500; draft `creator/scene` 500. Fix: `ok: false` with the reason, no asset added, scene and next_contacts 200 (windows 404 because the asset does not exist). The plain 2024 ISS TLE propagates in 2030 under sgp4 2.27, so a decay-prone set is used (as in v1.0) | pass |
| Re-derive M-1 and M-3 | Parent: PUT accepts `e` 1.5 (scene 500), `a_m` -5 (scene 500), `e` -0.1, `a_m` 1000, `i` 200, `e` 0.999, id `../x`, negative `delta_v_ms` (all `ok: true`); a no-orbit draft saves 200 and writes a file. Fix: every one is `ok: false` with a reason; save is 400 and the directory stays empty | pass |
| No second TLE or element validation outside the shared function | Callers of `asset_authoring_problems`: `validate_vignette` and `SessionManager._authoring_problems` (five call sites); the AST/grep test asserts no `sgp4(sat.jdsatepoch` in `manager.py` | pass |
| Every shipped vignette still loads; bounds as stated; dropped rules recorded | Sweep over all 19: load, force-add of an in-epoch TLE, `start`, `step` 1800 s, scene and `next_contacts` for blue and red, `GET /save` then `load_save`, `save_vignette` of the started session then load: 19 of 19 clean, 0 false refusals; no rule was dropped | pass |
| `PUT` accepts an incomplete asset; save refuses it | Own probe (NOORB draft) and the incomplete-asset test | pass |
| `engine/` byte-unchanged; gates, doc checks, browser suite green | See Scope and Test run | pass |

## Requirements audit

| Req | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| FR-5311 | `asset_authoring_problems` TLE branch, five session call sites plus the load gate | agreement table, force/bulk/PUT/PATCH matrix, decay reads | Test column lists the module; regeneration is a no-op | pass |
| FR-5310 | Keplerian bounds, resources, id charset | each rule pinned (v1.0 F1 closed) | same | pass |
| FR-5312 | presence unchanged | incomplete-asset test | same | pass |
| FR-5220 | per-object failure for stale and unphysical objects | bulk and OMM tests | same | pass |
| FR-5110 | `save_vignette` pre-write validation; Creator console shows the refusal | invalid-draft matrix; browser test | same | pass |
| FR-5120, FR-5150 | PUT and PATCH refusal naming the asset | parametrised tests; browser tests | same | pass |
| NFR-1600 | scene, belief-track and window guards | decay reads, poisoned-world tests | same | pass |

Every `verifies` marker in the new and changed tests names a live baseline ID (`test_test_origins.py` and `test_origin_retag.py` green).

## Independent probes

- **Replay equals live.** A started `leo-isr-denial` session with a force-added in-epoch TLE, stepped 4 x 900 s: `GET /save` then `load_save` gives a godview equal to the live one (no differing keys apart from the lazy wall-clock fields I excluded).
- **Determinism and boundaries.** `test_determinism.py` (6) and `test_import_guard.py` (8) green by name; `engine/` unchanged, so the guards hold by construction.
- **Fog.** In the decay reads the red cell's scene and picture are unchanged when the blue asset decays.

## Test run

| Command | Result |
|---|---|
| `python3 -m pytest -q --junitxml=...` (unfiltered) | exit 0; 1995 tests, 0 failures, 0 errors, 3 skipped (the pre-existing "vignette does not accept order" skips) |
| `python3 -m pytest -q -m "not browser" --junitxml=...` | exit 0; 1959 tests, 0 failures, 4 skipped (the 3 above plus the partial-collection RTM equality skip, which runs in the unfiltered run) |
| `python3 -m pytest -q -m browser -rs --junitxml=...` | exit 0; 36 tests, 0 failures, 0 skipped (1959 + 36 = 1995; includes the 3 `test_creator_browser.py` tests, which ran) |
| `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`, `test_test_origins.py`, `test_origin_retag.py` | exit 0; 230 tests, 0 failures, 1 skipped |
| `python3 -m pytest --origin-report=rtm` | no diff; the committed Test column equals the tool output |
| Mutations (19, plus the `creator.js` revert) | all killed |

Ledger audit: the Master Build Plan table recounts to 86 `VERIFIED` / 1 `COMPLETE` / 2 `READY` = 89 before this update, and 87 / 0 / 2 = 89 after it.

## Findings

| ID | Finding | Severity | Owner |
|---|---|---|---|
| I1 | `test_creator_browser.py` imports its server and browser fixtures from `test_browser_console_rules.py` (a cross-module test import); a rename there would break it silently at collection of this file only. Works today | Info | none required |
| I2 | `windows_ahead` returns `error: propagation_failed` for any `ValueError`/`ArithmeticError` in the whole station loop, so a failing peer propagation is reported as the queried asset's failure. Read-only and deterministic; consistent with Design Decision 6 | Info | none required |
| I3 | Start-epoch-only TLE check remains a documented residual (Design Decision 2); the read guards prevent the 500, not the loss of fidelity. The omission of a decayed asset from the map has no on-screen indicator (package Risks) | Info | `05`/console feature, later |

## Next step

`IP-1086` is `VERIFIED`. Remaining `READY` packages are `IP-1087` and `IP-1160`; run `08-code-implementation` on `IP-1087` (critical path first).
