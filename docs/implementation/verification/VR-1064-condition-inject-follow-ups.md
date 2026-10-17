# VR-1064 — Verification Report: Condition-Triggered Inject Follow-Ups (FR-4420, NFR-1100)

> **Document ID:** VR-1064
> **Version:** 2.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1064](../packages/IP-1064-condition-inject-follow-ups.md),
> [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.1/v2.2, [IP-1062](../packages/IP-1062-condition-triggered-injects-and-new-effects.md) (`VERIFIED`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md), [`backlog.md`](../../pipeline/backlog.md)
> `BL-0131`/`BL-0132`/`BL-0133`, `BL-0278`, `BL-0270`
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1064` (this v2.0 pass)
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py),
> [`spacesim/engine/busmodel.py`](../../../spacesim/engine/busmodel.py),
> [`spacesim/tests/test_condition_triggered_injects.py`](../../../spacesim/tests/test_condition_triggered_injects.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1064 — Condition-Triggered Inject Follow-Ups (measured value in the firing
  record, start-anchored tick grids after a rewind, one log scan per tick).
- **Version verified:** 1.0 (remediated twice — `60799fd` then `34c6bac`).
- **Tree state verified:** branch `claude/chart-prompt-file-90hm9u`, tip `b9b1644` at the start of
  this pass (worked from a local tracking branch, `verify-ip1064-local`). Remediating commit for
  this pass's finding: `34c6bac` ("fix(IP-1064): measure condition-inject record value before
  applying effects (BL-0278)"), run #182.
- **Independence:** second verification pass (v2.0). Fresh session with no involvement in either
  `34c6bac` (the fix) or the v1.0 (`9ed7b3d`-era) report that returned this package on Finding 1.
  All claims below are re-derived independently; the v1.0 report's own fixtures are not reused —
  every scenario below uses different metric kinds, object/asset ids, and seeds than both v1.0's
  fixtures and the fixing session's new regression tests.

## Result

**VERIFIED — the v1.0 Medium finding (`BL-0278`) is fixed, confirmed general beyond the two shipped
regression cases, and nothing v1.0 already confirmed has regressed.**

`spacesim/session/manager.py::_h_condition_check` now reads (confirmed by direct read of the tree
at `b9b1644`):

```python
if _evaluate_metric(world, self.ctx, trig.get("metric", {})):
    # IP-1064 (BL-0131) — record the measured value that decided the firing, measured
    # before the inject's own effects can change it (VR-1064 Finding 1, BL-0278).
    value = _measure_metric(world, self.ctx, trig.get("metric", {}))
    self._apply_inject_effects(world, inj.effects, rng)
    fired.append({"inject_id": inj.id, "value": value})
```

The measurement now happens before `_apply_inject_effects` runs, and the captured local — not a
re-measurement — is what gets logged. `git show 34c6bac -- spacesim/session/manager.py` confirms
this is the entire code change: the line order is swapped and the call is captured into `value`;
no other logic in the function changed.

### Independent reproduction of the original defect's absence (fresh scenario, task item 1)

A fresh scenario distinct from both v1.0's fixture (`R1`/`seed 3`/`seed 5`) and the fixing
session's shipped tests (`SAT-BLUE`/`SAT-RED`): objects `OBSERVER-01` (blue) / `TARGET-99` (red),
seed `777`, a `custody ≥ 0.5` condition with effect `forced_custody_loss` (`mode: drop`) on the
same track. Run against the tree as it stands (`b9b1644`):

- The condition inject fires at `sim_time = start + 300_000_000 µs` (the first tick) and the log
  record is `{"inject_id": "cond-inject", "value": 0.8908987181403393}`.
- **Independently computed true value** (not taken from any control run, derived directly from
  `Track.current_confidence`'s documented formula, `confidence · 0.5^(dt/half_life)`, with
  `dt = 300.0 s`, `half_life = 1800.0 s`, `confidence = 1.0` set by the t=0 `reveal_asset`):
  `1.0 · 0.5^(300/1800) = 0.8908987181403393` — exact match to 16 significant digits.
  (Independent Python: `math` not even needed — `0.5 ** (300/1800)` evaluates to the same float.)
- After the tick, `mgr.world.track_for("blue", "TARGET-99")` is `None` — the effect's `drop`
  genuinely ran. The pre-fix code path (confirmed below) would have logged `0.0` here, not the
  true `0.8908987181403393`, reproducing exactly the class of defect `VR-1064` v1.0 found.

### Direct before/after reproduction on the live tree (not just trusting the tests)

The pre-fix hunk was reverse-applied to `spacesim/session/manager.py` in place (verified via
`diff` against `git show 34c6bac^:spacesim/session/manager.py`, confirming the only textual
difference is the line-order/capture change quoted above), the three shipped regression tests
were run, and the file was restored and confirmed clean (`git status` — no diff) immediately
after:

```
FAILED test_custody_record_value_is_measured_before_a_self_affecting_custody_loss[loss0]
  assert 0.0 == 0.8908987181403393
FAILED test_custody_record_value_is_measured_before_a_self_affecting_custody_loss[loss1]
  assert 0.0 == 0.8908987181403393
FAILED test_deny_custody_record_value_is_measured_before_a_self_affecting_reveal
  assert 1.0 == 0.0
3 failed, 8 deselected
```

These are exactly the numbers the fixing session's commit message and the v1.0 report claim
(`0.0` vs `0.8909`; `1.0` vs `0.0`). The file was restored byte-for-byte (`git status` clean,
and the restored module's 11/11 tests pass again) before any further work in this pass.

### A third, distinct condition-type/effect-type pairing (task item 2 — generality check)

Both shipped regression tests use `custody`/`deny_custody` metrics (a continuous confidence value)
paired with `forced_custody_loss`/`reveal_asset`. To confirm the fix is a general ordering fix in
`_h_condition_check` — not a patch narrowly aimed at those two metric kinds — a **boolean** metric
kind was paired with a **different** effect type: `asset_operational` (true iff not destroyed, not
safed, and past its deadline) with the inject's own effect `anomaly` (`subsystem: bus`), which
flips the asset into safe mode. `asset_operational`'s own post-effect re-evaluation would be
`False` (safed), so this exercises the same bug class on a path the shipped tests never touch.

Scenario: assets `SAT-A` (blue) / `SAT-B` (red, given a `BusState()` so `anomaly` has something to
act on), `by_s: 0` (deadline = start, so "operational" is already decidable at the first tick),
seed `42`.

- **On the fixed tree:** the condition fires at the first tick with `{"inject_id": "op-cond",
  "value": True}` — the decision-time value — while `SAT-B.bus_state.safe_mode.active` is `True`
  immediately after (the effect genuinely ran).
- **Independently computed pre-fix value:** calling `_evaluate_metric` for the same metric
  *after* manually driving the same `enter_safe_mode` call the effect uses gives `False`. This is
  exactly what the old (post-effect) measurement would have logged: a condition that *fired true*
  recorded as `False`. The fix generalizes: it is the single-capture-before-effects pattern in
  `_h_condition_check`, not a per-metric special case — the same `value = _measure_metric(...)`
  line runs for every metric kind the trigger declares, and nothing in `_measure_metric` or
  `_evaluate_metric` is specific to `custody`/`deny_custody`.

### Properties `VR-1064` v1.0 already confirmed, re-confirmed independently on this tree (task item 3)

- **Anchored tick grids survive an off-grid rewind.** The shipped test
  `test_tick_grids_stay_on_the_start_anchored_grid_after_an_off_grid_rewind` passes (part of the
  11/11 run below). `34c6bac`'s diff touches only `manager.py`'s `_h_condition_check` measurement
  order — `_arm_schedule`'s anchor logic (`ctx.start_epoch`, confirmed read at lines ~253–261) is
  untouched since the v1.0 pass that first confirmed it.
- **One event-log scan per tick, not per inject.** Instrumented independently: a vignette with
  **two** condition injects (`RED-7`/`RED-8`, thresholds that never fire), `SessionManager.
  _fired_condition_inject_ids` monkey-patched to count calls, advanced 3 ticks — **3** calls
  recorded (one per tick, not 6 = ticks × injects).
- **`_evaluate_metric` byte-unchanged.** `git log -p --follow -- spacesim/content/vignette.py` shows
  `_measure_metric` introduced exactly once (`60799fd`), and `34c6bac`'s diff touches only
  `spacesim/session/manager.py` — `vignette.py` is not in that commit's file list at all (its
  6-file `--stat` lists `ROADMAP.md`, the MBP, `packages/INDEX.md`, the RTM, `manager.py`, and the
  test module). `_evaluate_metric`'s and `_measure_metric`'s bodies are therefore unchanged since
  the v1.0 pass that already confirmed `_evaluate_metric`'s results for all 14 metric kinds.
- **Replay-determinism, fresh scenario.** A new scenario (`BLU-7`/`RED-7`, seed `314159`, a
  `custody` condition whose own effect is `forced_custody_loss(degrade_to=0.1)`, advanced 5 ticks)
  was run live and then replayed via `mgr.sim.replay()`. `mgr.world.model_dump() ==
  replayed.model_dump()` is `True` (also cross-checked with `json.dumps(..., sort_keys=True,
  default=str)` equality) — byte-identical, this project's standard determinism check, built fresh
  for this pass rather than reusing v1.0's or the shipped tests' fixtures.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Tests 1–2 failed first and pass; existing condition/bus tests green. | `spacesim/tests/test_condition_triggered_injects.py`: 11/11 pass on the fixed tree. Reverse-applying the pre-fix hunk reproduces exactly 3 failures with the claimed numbers (above), confirming the new tests are not vacuously true. | ✅ Pass |
| Full suite and both permanent gates green; playbook suite green. | See Test run. `test_vignette_tutorials.py` is included in the full-suite run and is green (no failures reported). | ✅ Pass |
| RTM and ledgers updated. | `FR-4420` RTM row cites the two new test names and `IP-1064 (COMPLETE 2026-10-17, re-run #182 ...)`; MBP/`packages/INDEX.md`/`ROADMAP.md` read `COMPLETE`, now advanced to `VERIFIED` by this report. The `FS-106` `Referenced By` tag (still reading "🟡 RETURNED" at the start of this pass, left stale by design — `08-code-implementation` must not touch Feature Specifications) is updated by this report, since `09` may touch ledgers of this kind. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Reproduce the rewind-grid case independently on a shipped vignette with a condition inject or a fixture. | Already independently confirmed by v1.0 on two shipped vignettes (`geo-rpo-shadowing`, `leo-isr-denial`), unaffected by `34c6bac` (no edit to `_arm_schedule`/`busmodel.py`). Re-confirmed this pass via the shipped grid test passing and a fresh third fixture's grid behaving identically. | ✅ Pass |
| Confirm `_evaluate_metric`'s results are unchanged for every metric kind. | `vignette.py` is not in `34c6bac`'s file list; `_evaluate_metric`'s body is unchanged since `60799fd`, already confirmed for all 14 kinds by v1.0. This pass additionally confirms the record now matches the decision-time value for a 3rd, boolean-kind metric (`asset_operational`) that v1.0 never exercised. | ✅ Pass |
| Run the full suite and both gates by name. | See Test run. | ✅ Pass |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Pass/Fail |
|---|---|---|---|---|
| `FR-4420` — Outputs: the evaluated value is recorded, including when the inject's own effects change the measured quantity | `manager.py::_h_condition_check` now measures before applying effects (`34c6bac`) | `test_custody_record_value_is_measured_before_a_self_affecting_custody_loss` (×2 parametrizations), `test_deny_custody_record_value_is_measured_before_a_self_affecting_reveal`, plus this report's own 3rd-pairing (`asset_operational`/`anomaly`) and fresh-scenario (`OBSERVER-01`/`TARGET-99`) probes | Cites the two new test names and `IP-1064` | ✅ **Pass** |
| `FR-4420` — deterministic tick schedule unaffected by rewind position | Unchanged since v1.0 (`busmodel.py::schedule_ticks(anchor=)`, `_arm_schedule` uses `ctx.start_epoch`) | `test_tick_grids_stay_on_the_start_anchored_grid_after_an_off_grid_rewind`; re-confirmed this pass | As above | ✅ Pass |
| `NFR-1100` — one log scan per tick | Unchanged since v1.0 (`_fired_condition_inject_ids(before_t)`) | `test_two_condition_injects_each_fire_once_at_the_same_tick`; re-confirmed this pass by an independent call-count instrumentation (3 calls for 3 ticks, 2 injects) | Not a separate RTM trace for this package | ✅ Pass |

## Test run

```
python3 -m pytest spacesim/tests/test_condition_triggered_injects.py -v     # 11 passed
python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py   # 14 passed
python3 -m pytest -q --tb=short                                             # full suite, run in background
```

- **This package's module:** **11/11 pass** (the original 8 + the 3 new BL-0278 regression
  cases: 2 parametrizations of `test_custody_record_value_is_measured_before_a_self_affecting_
  custody_loss` + `test_deny_custody_record_value_is_measured_before_a_self_affecting_reveal`).
  Reverse-applying the pre-fix hunk in isolation (restored immediately after, tree confirmed
  clean) reproduces exactly those 3 failing with the claimed values.
- **Permanent gates, run by name:** **14 passed** (`test_determinism.py`: 6, `test_import_guard.py`:
  8).
- **Full suite:** **1025 passed, 3 skipped** (1028 collected), **0 failed**, exit code 0. The
  harness's captured output for this long-running command truncates the trailing pytest summary
  line in this environment (confirmed on two independent runs); the counts above were
  cross-checked by parsing the progress-dot/skip-marker stream itself (`.`×1025, `s`×3 = 1028
  total markers, matching exit code 0 — no `F`/`E` markers present anywhere in either captured
  run) rather than taken on faith from the commit message. This matches the claimed `1025 passed /
  3 skipped` exactly.

## Scope audit

`git show 34c6bac --stat`: `ROADMAP.md`, `docs/implementation/00-master-build-plan.md`,
`docs/implementation/packages/INDEX.md`, `docs/requirements/03-requirements-traceability-matrix.md`
(all ledgers), `spacesim/session/manager.py` (7 lines changed — the measurement-order swap only,
confirmed by reading the full hunk), `spacesim/tests/test_condition_triggered_injects.py` (51 lines
added — the new tests only). No excursion: `content/vignette.py` and `engine/busmodel.py` (touched
by the original `60799fd` implementation, confirmed unchanged by v1.0, and still untouched by this
fix) are not in this commit's file list. The fix is minimal and matches exactly what the fixing
session's own report and `08`'s remediation task claimed.

## Findings

None. The v1.0 Medium finding (`BL-0278`) is fixed and the fix is confirmed general (task item 2)
rather than narrowly aimed at the two shipped test cases. No regression found in anything v1.0
already confirmed (anchored grids, one-scan-per-tick, `_evaluate_metric`, replay-determinism).

## Traceability actions taken by this report

- MBP row, `packages/INDEX.md` row, `ROADMAP.md` row: `IP-1064` `COMPLETE → VERIFIED`.
- RTM `FR-4420` cell: `IP-1064 (COMPLETE 2026-10-17, re-run #182 ...)` → `IP-1064 (VERIFIED
  2026-10-17 via VR-1064 v2.0)`.
- `FS-106` `Referenced By`: `IP-1064` tag updated from `🟡 RETURNED 2026-10-17, VR-1064` to
  `✅ VERIFIED 2026-10-17, VR-1064 v2.0` (left stale by the `08` re-run by design — `08` must not
  touch Feature Specifications; `09` is the correct owner of this ledger entry).
- Backlog: `BL-0131`/`BL-0132`/`BL-0133` → `DONE` (all three close on `IP-1064` reaching
  `VERIFIED`, per their own entries). `BL-0278` → `DONE` (the fix is confirmed, generalized, and
  unregressed). `BL-0270` (the five-package batch tracker) → closed: `IP-1064` was the only package
  still owed a fresh-session `09` on that list (`IP-1021`, `IP-1223`, `IP-1065`, `IP-1131` were
  already `VERIFIED`); this report's `VERIFIED` clears the list in full.

## Related

[IP-1064](../packages/IP-1064-condition-inject-follow-ups.md) ·
[FS-106](../../features/FS-106-white-cell-dashboard.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md)

## Prior pass (v1.0, superseded)

v1.0 (fresh session, tree `9ed7b3d`, implementing commit `60799fd`) returned this package on
Finding 1 (`BL-0278`): `_h_condition_check` measured the firing record's `value` *after*
`_apply_inject_effects` ran, so a condition inject whose own effects changed the measured quantity
(`forced_custody_loss` on a custody-measured track; `reveal_asset` with `deny_custody`) recorded
the post-effect value instead of the one the decision saw (`0.0` vs. a true `0.8909`; `1.0` vs. a
true `0.0`). v1.0 independently confirmed items 2–3 (anchored tick grids on two shipped vignettes;
one log scan per tick; `_evaluate_metric` byte-unchanged for all 14 metric kinds) and the
correctness of the one updated existing test — all unaffected by Finding 1 and unaffected by this
pass's fix. This v2.0 pass confirms the Finding 1 fix (`34c6bac`), confirms it generalizes beyond
the two shipped regression cases via an independent third condition-type/effect-type pairing, and
closes the package to `VERIFIED`.
