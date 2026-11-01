# VR-1076 — Verification Report: Time Advance Bound and Console Refusal Gaps (FR-4330, FR-4310, NFR-1600)

> **Document ID:** VR-1076
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1076](../packages/IP-1076-time-bound-and-console-refusals.md) v1.0,
> [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1076` (closes tranche 3 review `M-2`, `M-4`, `L-1`, `L-2`, `L-3`)
> **Feature Mapping:** FS-106

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1076 — Time Advance Bounded to the Exercise Span, Backwards Step Refused, Console Refusal Gaps (v1.0)
- **Implementing commit:** `bfcd4a7` (branch `claude/ip-1076-build`); tree verified at that commit (parent `6dd7463`).
- **Independence:** fresh session; did not implement this package.

## Result

**✅ VERIFIED** — 0 failed checks; 4 Low findings, none blocking.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Tests 1-18 exist, seen failing first, pass | `test_time_advance_bound.py` (13 collected) + 7 new browser cases. With the parent `manager.py`/`inprocess.py`/`server.py`/`app.js` restored in the worktree, 23 tests fail (10 server, 12 browser incl. the 5 moved ones, plus the moved `test_web.py` draft step); restored afterwards | pass |
| Advance/step beyond `start_epoch + 366 d`, before now, or non-finite is 400 with a reason, nothing changed; cap saves and loads; running clock stops at the cap | HTTP probes below; `manager.py:373-405`, `:444` | pass |
| Blue/Red/Observer not offered inject entries; refused inject/Load/time control visible; refused Load does not overwrite `#session` | Browser cases 14-16; mutations below | pass |
| No console error from `/windows/<sensor>` or Observer dry-run | Own Chromium drive of White, Blue, Red, Observer through every actor: 0 responses >= 400, `c.errors == []`, Observer sends no `/windows` or `/order/validate` | pass |
| Retags done, `EXPECTED` rows match, RTM regenerated, no allow-list grew | `test_origin_retag.py` green; `--origin-report=rtm` prints "unchanged"; no `*allow*` file in the diff | pass |
| Full suite (both partitions + one unfiltered), gates, doc integrity, test origins green | See Test run | pass |
| Docs updated; MBP row `COMPLETE` | CLAUDE.md `session/` bullet, training 08 and 10, MBP, packages index, ROADMAP, RTM. Gaps: F3 | pass (Low) |

## Verification Checklist audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Reproduce pre-fix symptoms on the parent and see each gone | Parent files: 370-day load, negative step, palette inject entries, hidden refusal, `BLUE-RADAR` 404 and Observer dry-run tests all fail; fixed tree passes | pass |
| 2 | Every new test names its origin | Module `pytestmark` FR-4330/NFR-1600; per-test `FR-4310`/`FR-4320`/`IP-1076`; browser cases tagged; `test_test_origins.py` green | pass |
| 3 | `git diff` of `spacesim/engine/` empty; import guard green | `git diff HEAD~1 HEAD -- spacesim/engine` is empty; `test_import_guard.py` green | pass |
| 4 | Determinism green; a refused advance appends nothing | `test_determinism.py` green; probe: refused calls leave `(now, eventlog length)` unchanged; test 12 passes | pass |
| 5 | `validate_save` wording and IP-1103 tests unchanged and green | `_check_final_time_span` untouched; `test_save_load_robustness.py` green | pass |
| 6 | Retagged tests AST-identical; `EXPECTED` rows equal the new tags | AST comparison (decorators stripped): 0 changed bodies in `test_save_load_robustness`, `test_undo_clock_floor`, `test_white_control_correctness`; the 8 `EXPECTED` rows match the markers and the guard passes | pass |
| 7 | Existing-test edits listed and none weakens | `test_web.py` draft step: `ok is False` became `status 400` plus "draft" in the detail (same refusal, new transport); 4 browser tests: mock URL `**/step*` and `#session`→`#control-status` waits; refused-Load test adds the `#session` unchanged assertion. Bodies otherwise AST-equal | pass |
| 8 | Palette audit in the completion note | MBP row: 17 sources examined, 6 White-only, all gated; the 2 AAR export entries are by design not seat-gated | pass |
| 9 | doc integrity and test origins green; RTM regenerated; no allow-list grew | Run; "unchanged" | pass |
| 10 | Collected count below `COLLECTED_UPPER` (1700) | **1657 collected** (+20); headroom 43 | pass |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| FR-4330 | `manager.py::_span_ceiling/step/advance_to/_catch_up_locked`; `inprocess.py`; `server.py` `/step`,`/advance` | `test_time_advance_bound.py`, browser span case, retagged rewind/undo/save-span tests | regenerated, first Test entries present | pass |
| FR-4310 | palette gate `app.js` | browser case 14, seat probes | regenerated | pass |
| NFR-1600 | refusals as 400 with reason; visible status line | server and browser cases | regenerated | pass |
| NFR-3020/3030 | console quiet on load and seat switch | browser case 17 | regenerated | pass |

## Test run

- `python3 -m pytest -m "not browser"` — **1627 passed** (the harness config suppresses the summary line; counted from the run, 0 failures).
- `python3 -m pytest -m browser -rs` — **30 passed, 0 skipped** (Chromium ran).
- Unfiltered `python3 -m pytest -rs` — **1654 passed, 3 skipped** (the 3 pre-existing vignette-applicability skips); the count-pinned and RTM-column guards ran.
- Gates by name: `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`, `test_test_origins.py`, `test_origin_retag.py`, `test_save_load_robustness.py` — green (the RTM-column check skips on partial collection and passes in the full run).
- `python3 -m pytest --origin-report=rtm` — "unchanged"; Test column equals tool output.

### Behavioural probes (real `/step` and `/advance`, TestClient over `create_app`, leo-isr-denial)

| Case | Result |
|---|---|
| white: normal step/advance | 200 |
| white: advance to now (no-op), step 0 | 200 |
| white: advance earlier than now / before start / -1 | 400, state unchanged |
| white: advance cap-1, cap | 200; cap+1 (one microsecond) 400, clock unchanged; advance to cap again 200 |
| white: at the cap, step of 1 microsecond | 400 |
| white: step negative / NaN / Infinity / -Infinity / 1e300 / 1e30 / 366 d + 1 s | 400 each, never 500 |
| white: advance 2**70 | 400; string step 422 |
| blue, red, observer, no seat, with in-span, out-of-span, negative and NaN bodies | 403 each, before any bound check, nothing changed |
| Cap save then `load_save` | 200, no warnings (the IP-1103 366-day ceiling and this bound agree exactly; no off-by-one) |
| Rewind then advance, then advance past the cap | 200, 200, 400 |
| Running clock at 600x, 30 sim seconds below the cap, read after waiting | `now` pinned at `start_epoch + 366 d`; save at the pin loads; rate 1e9 also pins |

### Determinism

All 19 shipped vignettes: 14 seeded random `step`/`advance`/`rewind`/`undo`/over-cap operations, then advance to the cap; the live world JSON equals the world rebuilt from the save, the clock is at the cap, and `validate_save` passes. 19 of 19 identical.

### Mutations (scratch edits, restored with `git checkout`)

Caught (a test fails): beyond-span guard removed; `>` changed to `>=` at the cap; clock clamp removed; `/step` and `/advance` 400 mapping removed; `InProcessSession.step` catch removed; palette inject White filter; palette library White filter; `#control-status` routing; `#session` preservation; Observer dry-run guard; sensor-ribbon fix; `stepBy` back to `/advance`; `fireInject` visible report; non-finite and huge step guards removed together; huge guard alone.

Survived (single mutation): backwards-target check, negative-step check, non-finite check alone, huge-step guard alone, and the `CELL !== "observer"` clause of `drawRibbon`. The first four are layered: `Simulation.advance_to` still raises on a backwards target, `int(NaN)` raises `ValueError`, and infinity is caught by the other guard; removing backwards and negative together also survives, so those two manager checks are equivalent to the engine's own (defence in depth, not a defect). The Observer ribbon clause is untested (F1).

## Scope audit

Source changes are inside the declared files (`manager.py`, `inprocess.py`, `server.py`, `app.js`, the new module, the browser module, the listed retags). `spacesim/engine/` untouched; no `docs/pipeline/` change. Documentation outside the declared list: `docs/training/10-ui-reference.md` (a correct, related edit). `docs/training/12-white-cell-manual.md` and FS-106 `Referenced By` were named in the package and not edited (F3).

## Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| F1 | The `CELL !== "observer"` clause in `drawRibbon` has no test: removing it survives all suites, and an Observer can select a satellite from `ASSETS`, so the `/windows` 404 would return for that seat. Add an Observer case to the console-quiet test. | Low | `08-code-implementation` follow-up |
| F2 | Browser case 17 uses `wait_for_timeout(300)` and `wait_for_function("1")`, against the package's "no fixed sleeps" risk note. Passes reliably (30/30 here). | Low | `08-code-implementation` follow-up |
| F3 | The package asked that training pages not edited be listed in the completion note; `12-white-cell-manual.md` (clock section, palette inject entries White-only) and FS-106 `Referenced By` were neither edited nor listed. No manual text is now false (the manual does not describe `/step` or `/advance`). | Low | `08-training-manual-authoring` |
| F4 | The `ROADMAP.md` table carries two identical `IP-1075` rows (pre-existing, not from this commit). `FR-4330` Notes still read "required, not yet built"; the package defers that flip to `04` after `VERIFIED`. | Low | `04-requirements-engineering` / `11` |

Verifier-noted, not findings: `step` accepts a JSON `true` as `1.0` (pydantic coercion); the filter in `drawRibbon` lists sensor kinds rather than whitelisting `satellite`, which is correct for the shipped kinds.
