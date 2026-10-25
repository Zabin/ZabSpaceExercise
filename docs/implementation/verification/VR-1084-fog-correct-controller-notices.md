# VR-1084 — Verification Report: Controller-Set Anomaly and Sensor-Outage Notices Are Addressed by Ownership (FR-6210, FR-4430, FR-4440, FR-4420; `H-1`)

> **Document ID:** VR-1084
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1084](../packages/IP-1084-fog-correct-controller-notices.md) v1.0
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1084`
> **Feature Mapping:** [FS-106](../../features/FS-106-white-cell-dashboard.md), [FS-123](../../features/FS-123-space-weather-index-coupling.md)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

IP-1084 v1.0, implementing commit `5d1d761` on branch `claude/ip-1084-build` (parent `b022b1e`). Verified in a fresh
session in a separate worktree; the implementation was not done in this session.

## Result

**VERIFIED** — 0 failed checks. One Low (scope) and four Info observations (below); none blocks.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| No Red read carries a Blue target's id / fact / cause (and vice versa); White has the cause; owner has the fact | Adversarial probe run against the parent (`git archive HEAD~1`) and this commit: Red's `view`, `scene`, `alarms`, `activity`, `coaching`, `conjunctions`, `orders`, `next_contacts`, `brief`, `ephemeris/red`, `ssn/red/{requests,coverage}`, `telemetry|windows|recovery|maneuver_ledger/red/{blue asset}`, `tle`, `ric_view`, `/controller_view` red panel, AAR `playback` red viewpoint, AAR `aar`/`export.csv`/`export.json`, `GET /api/sessions`. Parent: `view` carries `BLUESAT-ZQ1`, `BLUESENS-ZQ4`, the cause, `anomaly`, `outage` on all four paths (immediate, future-dated, condition, env tick), the playback red viewpoint and the `controller_view` red panel too. Fix: Red `view.messages == []`, `controller_view.red.messages == []`, playback red clean; Blue sees `X: anomaly declared` / `X: sensor outage declared`, no cause. Residual id strings on the fix are only (a) 404 error text echoing the requester's own query parameter, byte-identical before and after the inject, and (b) ground-truth no-cell endpoints (`observer/view`, `aar/at`), by design under `FR-6220` | pass |
| Three entry points obey; pinned-unchanged effects keep recipients | Probe: immediate, future-dated (`white-N`), condition (`debris_present`), env tick all clean for Red. Pinned rows: `test_pinned_unchanged_effect_recipients` (10 cases) green; every `world.messages.append` in `spacesim/` enumerated by grep (`manager.py` 1101/1534/1556/1578/1589/1600/1619/1687/1729/1731/1737, `engine/ssn.py:387` cell-addressed) — each is a matrix row or the completeness test | pass |
| Effect application, RNG stream, event-log shape, replay equality unchanged | Same scenario on parent vs fix: event-log hash identical (`c1ea3dba…`), world hash excluding `messages` identical, env-tick firings identical `[(1893458100000000, BLUESAT-ZQ1)]`, replay-equals-live true on both. The test's hard-coded `_PARENT_ENV_FIRINGS` was re-run on the real parent tree: equal (6 firings) | pass |
| New tests green; RTM regenerated in same commit; suites and gates green; no allow-list grew | See Test run; `python3 -m pytest --origin-report=rtm` run on the tree leaves `git status` clean; no `*allow*` file in the diff | pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| Re-derive `H-1` on the parent | Reproduced (above): parent `GET /view/red` returns both notices with cause | pass |
| Enumerate message-appending lines from the tree | Done by grep (above); only `manager.py:1729/1731` (helper) address by ownership; others are the pinned set | pass |
| Owner text never contains the cause; White text equals pre-fix text | `test_anomaly_*`, `test_sensor_outage_*`; probe `blue_msgs`. (The owner's own asset view still carries `bus_state.safe_mode.cause` — package Design Decision 3, outside `H-1`; Info 1) | pass |
| Env tick fires at same times; replay equals live; save/load | See DoD row 3; `test_env_tick_replay_equals_live`, `test_save_load_round_trip_keeps_per_cell_messages` | pass |
| `CellController.view` and `engine/` byte-unchanged | `git diff HEAD~1 HEAD -- spacesim/session/cells.py spacesim/engine` empty | pass |
| Gates, doc checks, browser suite | See Test run | pass |

## Mutation testing (fresh scratch copy; each restored)

| Mutation | Result |
|---|---|
| Owner message sent to both `blue` and `red` | `test_anomaly_white_cause_owner_fact_opponent_nothing` fails |
| Drop the neutral-target White-only rule (neutral owner gets a player message) | `test_anomaly_on_neutral_asset_is_white_only` fails |
| Owner message carries the cause | `test_anomaly_white_cause_owner_fact_opponent_nothing` fails |
| Env tick broadcasts to all three cells | `test_environmental_anomaly_tick_obeys_addressing_and_rng_is_untouched` fails |
| Condition path appends a Red-addressed message | `test_condition_triggered_anomaly_never_reaches_the_opposing_cell` fails |
| Boolean `at_sim_t` allowed in `fire_inject` | `test_manager_backstop_rejects_boolean_at_sim_t[True]` fails |
| Boolean `at_sim_t` allowed at the server (`_NUMBER_ONLY` entries removed) | `test_inject_at_sim_t_boolean_is_a_400_and_changes_nothing[True/False]` fail |

## Boolean `at_sim_t`

`POST /inject` and `POST /injects/{h}/edit` with `at_sim_t: true|false` return 400 (server `_NUMBER_ONLY` guard) and nothing is logged; the manager backstops (`fire_inject`, `edit_inject`) raise `ValueError`. Callers send numbers or omit: `static/app.js` (`injectScheduleAt()` returns a number or `null`; edit path `Math.round(...)`), `tools/render_manual.py` and `docs/training/` examples show µs numbers; grep for boolean `at_sim_t` outside the new test file finds none.

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| FR-6210 | `manager.py::_notice_by_owner` | `test_inject_notice_fog.py` (40 tests) | names the file; regeneration is a no-op | pass |
| FR-4430 | `manager.py` anomaly / sensor_outage branches | same, plus `test_inject_effects_v2.py` | same | pass |
| FR-4440 | env tick via the same branch | `test_environmental_anomaly_tick_*`, `test_space_weather_index.py` (tightened to the White address) | same | pass |
| FR-4420 | condition path via the same branch | `test_condition_triggered_anomaly_*` | same | pass |

## Test run

| Command | Result |
|---|---|
| `python3 -m pytest -q` (unfiltered, `--junitxml`) | exit 0; 1851 tests, 0 failures, 0 errors, 3 skipped |
| `python3 -m pytest -q -m "not browser"` | exit 0; 1818 tests, 0 failures, 4 skipped (one skip differs from the unfiltered run; environment-conditional, not this package's) |
| `python3 -m pytest -q -m browser` | exit 0; 33 passed, 0 skipped |
| `test_determinism.py` / `test_import_guard.py` | exit 0 each (6 / 8 passed) |
| `test_doc_integrity.py` / `test_test_origins.py` / `test_origin_retag.py` | exit 0 each (9 / 21 passed + 1 skipped / 42) |

## Documentation audit

`docs/training/07-white-cell-facilitation.md` table rows rewritten to the ownership rule and match the code; `CLAUDE.md` code-map sentence for `_notice_by_owner` and the boolean rejection is accurate; RTM Test column equals tool output; MBP table recounted from rows before this run: 84 `VERIFIED`, 4 `READY`, 1 `COMPLETE`, 0 `BLOCKED` = 89, matching the implementer's tally; after this run 85 / 4 / 0 / 0 = 89. The "Training" `12-white-cell-manual.md` was grepped for the old "announced to all three cells" wording for these effects: none.

## Scope audit

Files changed: `session/manager.py`, `tests/test_inject_notice_fog.py`, `tests/test_space_weather_index.py`, `docs/training/07-…`, `CLAUDE.md`, RTM, ledgers: all declared. **`spacesim/ui_web/server.py` (one `_NUMBER_ONLY` line) is not declared** — the package said it edits `manager.py` only — and the boolean-`at_sim_t` rejection is not in the package text; it is in this verification's directive and is covered by tests.

## Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| 1 | Undeclared `server.py` edit and boolean-`at_sim_t` rejection absent from the package text (and its `NFR-1600`/`FR-4330` tags absent from Requirements Covered). Behaviour correct and mutation-tested | Low | `07` package note at next repair; no code action |
| 2 | Info: the owner's own asset view still shows `safe_mode.cause` (Design Decision 3, outside `H-1`); owner decision pending | Info | owner |
| 3 | Info: `FR-4430` still lacks a "who is told" Postcondition (routed to `04` by the package) | Info | `04-requirements-engineering` |
| 4 | Info: `tle`/`ric_view` 404 detail echoes the requested id and distinguishes "no track" vs unknown only as before; unchanged by this package | Info | none |
| 5 | Info: the package file header still reads `READY` (a verifier does not edit packages); ledgers carry `VERIFIED` | Info | none |

No cell-scoped leak found; side channels (message order/count, ids, error messages, tracks, `white-*` handles) show no Blue-derived trace in Red output.
