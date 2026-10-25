# VR-1082 — Verification Report: White Control Non-Finite Input and Toolbar Refusal (NFR-1600, FR-4330, FR-4310, FR-7330)

> **Document ID:** VR-1082
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1082](../packages/IP-1082-white-control-nonfinite-input-and-toolbar-refusal.md) v1.0
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → RETURNED` (`IN PROGRESS`) transition of `IP-1082`
> **Feature Mapping:** [FS-106](../../features/FS-106-white-cell-dashboard.md), [FS-107](../../features/FS-107-after-action-review.md)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1082 — White Control Routes Refuse Non-Finite and Absurd Values; Toolbar Step Shows a Refusal; Playback Cursor Clamp; Code-Map Catch-Up (v1.0)
- **Implementing commit:** `7583ec9` (branch `claude/ip-1082-build`); parent `4f32ba3`.
- **Independence:** fresh session; did not implement this package.

## Result

**RETURNED** — 2 Checklist/DoD items fail (Medium F1; Low-Medium F2 against the "absurd values" contract), 2 Low and 3 Info findings. Everything else passes; the shape of the fix is right and the gap is one route family.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| No White control request can make a session's reads fail; every non-finite number is a 400 with a reason from one shared mechanism that the route-table test pins | Clock `NaN`/`Infinity` and the other 12 raw-JSON probes: parent 500 / poisoned reads (`clock`, `godview`, `save`, `objectives`, `scene` all 500) or 500; branch 400 naming the field, reads 200. One mechanism (`_refuse_nonfinite` via `_finite_json_guard`/`_playback_finite_guard`). **But** `POST /injects/{handle}/edit` (White-only, hand-rolled `cell != "white"` check) has no guard: `{"at_sim_t": NaN}` and `Infinity` are HTTP 500 (session stays readable), and `NaN` inside `effects` is silently stored as `null`. The route-table test finds White routes by the text `_require_white(` in the endpoint source, so it cannot see this route. See F1 | **FAIL** |
| Rate bounded per Decision 3; finite in-range behaviour, seat rule and responses unchanged | `running:true`: 0, -0, -5, 1e18, 1e308, 1e999, 10000.0001, 10001, `false` are 400; 1, 1.0, 60, 600, 10000, 10000.0, 5e-324, 1e-300, `"600"` are 200; `running:false` ignores any finite rate (200) and refuses non-finite (400). 404 then 403 then 400 order holds (blue/red/observer/no seat all 403 with a NaN body). Default 1x, `step`/`advance`/`undo` finite behaviour unchanged | PASS |
| Toolbar step buttons show a refusal in `#control-status`, no page error | Own headless-Chromium driver as White: `+1m/+10m/+1h` each move the clock exactly 60/600/3600 s with empty status and no error. At the 366-day end (clock 30 s short) `+1h/+10m/+1m` each show "Advance: ... beyond the exercise span ..." and `errors == []`. Parent: status empty and one uncaught page error per click (raw JSON `detail`) | PASS |
| Playback cursor never outside the recorded span | Rewind and undo after advancing, viewpoints truth/blue/red: `state` 200, stored cursor equals live now (within `[start, live]`), a following `advance` stays at live. Seat table identical to the parent (White all; Blue own viewpoint; Red 403 on a blue playback; Observer `state` only; no seat 403) | PASS |
| Four code-map bullets, line 125 and `ROADMAP.md` line 26 current | `CLAUDE.md` now contains `_span_ceiling`, `playback_seat_decision`, `MAX_SAVE_SPAN_US`, `366`, `MAX_EVENTLOG_REPLAY_ENTRIES`; the "browser GUI unverified headless" line replaced; the browser count 30 -> 33 matches the run; `ROADMAP.md:26` now names the GDS ladder. The new `IP-1082` bullet says the guard is "on every route that calls `_require_white`" — true of the text, but see F1 | PASS (note F1) |
| Tests green; RTM regenerated; gates green; no allow-list grew | See Test run. `--origin-report=rtm` on the branch reports "unchanged"; no `*allow*` file in the diff | PASS |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| Re-derive `M-1` on the parent; branch 400 and readable | Scratch copy of the parent `spacesim/` (`git archive 4f32ba3`), raw bodies via `content=`: `rate NaN`/`Infinity` -> 200 then all reads 500; `advance`/`rewind` `t NaN`, `undo n NaN`, playback `advance dt_s NaN` -> 500; playback `start`/`speed` `NaN` accepted (200). Branch: all 400, reads 200 | PASS |
| Every White control route in the live route table refuses `NaN`/`Infinity`; seat rule first | Route table re-derived (all POST/PUT/PATCH/DELETE routes, dependencies and source). 22 White routes plus `load_save` carry `_finite_json_guard`; 3 playback value routes carry `_playback_finite_guard`; **`injects/{handle}/edit` and `injects/{handle}/cancel` carry neither** (edit: 500 on NaN `at_sim_t`) | **FAIL** (F1) |
| Rate boundaries; 600 accepted | As above | PASS |
| Re-derive `M-2` | As above (parent: page errors + empty status; branch: reason shown, none) | PASS |
| Playback after rewind and undo in-span; fog unchanged | As above | PASS |
| `CLAUDE.md` terms present; stale lines gone | As above | PASS |
| `engine/` unchanged; gates, doc checks, browser suite green; excluded items untouched | `git diff 4f32ba3 7583ec9 --stat -- spacesim/engine` empty; runs below; no change to `--origin-report` exit code, event-log cap, parsers, rewind-pause | PASS |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| `NFR-1600` | `server.py` guards, `manager.py` `_require_finite`/`set_clock` | `test_white_control_nonfinite.py` + browser toolbar test | Regenerated, equals tool output | Partial (F1, F2: two routes still 500) |
| `FR-4330` | time routes + `MAX_CLOCK_RATE` | rate/time matrices | Same | PASS |
| `FR-4310` | seat rule first (403 before 400) | `test_a_non_white_request_with_a_nan_body_is_403_not_400` | Same | PASS |
| `FR-7330` | `PlaybackSession._finite`/`_clamp` | playback tests | Same | PASS (F2 aside) |
| `NFR-2840` | `stepBy` reuse | `test_a_refused_toolbar_step_shows_its_reason_and_raises_no_page_error[+1h/+1m]` | Same | PASS |
| `NFR-1100` | 600x accepted | `test_clock_accepts_in_range_rates_including_600x` | Same | PASS |

All 18 new test functions carry `@pytest.mark.verifies(...)` naming live IDs (`test_test_origins.py` green).

## Test run

All with real exit codes and `--junitxml` (quiet-mode summaries not relied on):

| Command | Exit | tests / fail / err / skip |
|---|---|---|
| `python3 -m pytest` | 0 | 1769 / 0 / 0 / 3 |
| `python3 -m pytest -m "not browser"` | 0 | 1736 / 0 / 0 / 4 (33 deselected) |
| `python3 -m pytest -m browser` | 0 | 33 / 0 / 0 / 0 |
| `test_determinism.py test_import_guard.py test_doc_integrity.py test_test_origins.py test_origin_retag.py test_white_control_nonfinite.py -rs` | 0 | 298 / 0 / 0 / 1 |

Skips: 3 are the unchanged content skips (`test_executed_observe_releases_sensor_booking`, `test_executed_command_releases_pass_booking`, `test_jam_ignores_operator_success_prob_override`). The 4th, in `-m "not browser"` and the gates subset only, is `test_the_committed_matrix_test_column_equals_the_generated_one` ("partial collection"): the RTM-equality guard skips loudly whenever the whole suite's origins are not collected; it ran and passed in the unfiltered run, and `--origin-report=rtm` independently shows no diff. Expected, not a defect.

**Mutations** (`test_white_control_nonfinite.py`, each restored with `git checkout`, tree clean after):

| Mutation | Caught |
|---|---|
| Remove the guard dependency from `undo` | yes (`undo-n-NaN`) |
| Remove `_require_finite` from `set_clock` | yes (manager backstop test) |
| Remove the three time-method backstops | yes |
| Remove the `state()` clamp / no-op the clamp | yes (`rewind-truth`) |
| Widen `MAX_CLOCK_RATE` to `10**9` | **no** (F3) |

## Scope audit

Diff touches only the package's files plus `docs/training/08-http-api-reference.md` (three rows) and the ledger rows. The package says the builder does not edit `docs/training/` unless the tree's doc-step rule allows it and routes it to `08-training-manual-authoring`; the rows are accurate against behaviour (Info F6). `spacesim/engine/` untouched. `ClockRequest.rate` and other request models unchanged.

## Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| F1 | `POST /api/sessions/{sid}/injects/{handle}/edit` (a White control with a hand-rolled seat check, so outside `_require_white(`) lacks the shared guard: `at_sim_t: NaN` / `Infinity` is HTTP 500 (NFR-1600); `NaN` inside `effects` is accepted and stored as `null`. The route-table test discovers routes by source text `_require_white(`, so it cannot catch this or any similar route; `CLAUDE.md`'s "every route that calls `_require_white`" is literally true but leaves it out. `injects/{handle}/cancel` carries no number but is the same family. Session stays readable (no poisoning) | Medium (fails the DoD "every non-finite number is a 400", Checklist route-table item) | `08-code-implementation` re-run: guard both inject-admin routes; make the route-table test discover White controls from the route table (any mutating route not player-seat-scoped), not by source text |
| F2 | Playback accepts a finite but absurd `speed` (`1e308`); the next `advance` is HTTP 500 (`int()` of an infinite product), as is `dt_s: 1e308`. Pre-existing, but the package title and Decision 3 promise refusal of "absurd values" and `NFR-1600` forbids 500s | Low-Medium | `08` re-run (bound `speed`/`dt_s` or catch `OverflowError`), or `07` if the owner wants the range stated first |
| F3 | The rate ceiling is not pinned: tests use `SessionManager.MAX_CLOCK_RATE` itself, so widening it to `10**9` passes; Decision 3 fixes 10,000 and `10000.0001` | Low | `08` (pin literal 10000 / 10000.0001) |
| F4 | `rate: true` is coerced to 1.0 with `running: true` (200); a subnormal rate such as `5e-324` is accepted and effectively freezes the clock | Info | none (harmless) |
| F5 | The 3-vs-4 skip difference is the expected partial-collection guard (above) | Info | none |
| F6 | `docs/training/08-http-api-reference.md` edited by the build though the package routes training edits to `08-training-manual-authoring`; content is accurate | Info | none |

## Next step

Re-run `08-code-implementation` on IP-1082 against F1-F3 (F1 required). Reverify in a fresh session.
