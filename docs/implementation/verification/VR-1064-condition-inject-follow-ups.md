# VR-1064 — Verification Report: Condition-Triggered Inject Follow-Ups (FR-4420, NFR-1100)

> **Document ID:** VR-1064
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1064](../packages/IP-1064-condition-inject-follow-ups.md),
> [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.1, [IP-1062](../packages/IP-1062-condition-triggered-injects-and-new-effects.md) (`VERIFIED`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md), [`backlog.md`](../../pipeline/backlog.md)
> `BL-0131`/`BL-0132`/`BL-0133`, `BL-0278`
> **Produces:** the `COMPLETE → IN PROGRESS` (returned) transition of `IP-1064`
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py),
> [`spacesim/engine/busmodel.py`](../../../spacesim/engine/busmodel.py),
> [`spacesim/tests/test_condition_triggered_injects.py`](../../../spacesim/tests/test_condition_triggered_injects.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1064 — Condition-Triggered Inject Follow-Ups (measured value in the firing
  record, start-anchored tick grids after a rewind, one log scan per tick).
- **Version verified:** 1.0
- **Tree state verified:** commit `9ed7b3d` (branch `claude/chart-prompt-file-90hm9u`, local
  tracking branch `verify-batch`). Implementing commit: `60799fd` (2026-10-17, pipeline run #170).
  `manager.py`, `vignette.py`, `busmodel.py` and the test module are unchanged since `60799fd`.
- **Independence:** first verification pass. Fresh session with no involvement in `60799fd`.

## Result

**RETURNED — 1 failed check (Medium), routed to `08-code-implementation`.** Items 2 and 3
(`BL-0132` and `BL-0133`) hold up under independent reproduction, as does the updated existing
test. Item 1 (`BL-0131`, `FR-4420` Outputs) does not. The record is supposed to carry "the
measured quantity that decided the firing" (Objective 1; Design Decision 1 says "the quantity
`_evaluate_metric` compares"). But `_h_condition_check` calls `_measure_metric` **after**
`_apply_inject_effects(world, inj.effects, rng)` (`manager.py`, the `if _evaluate_metric(…):` block).
So when an inject's own effects change the quantity its condition measured, the record shows the
post-effect value, not the one the decision saw.

**Reproduced** with a custody condition (`custody`, `blue` on `R1`, `min_conf 0.5`) that fires at
the first tick, seed 3. The value the decision compared was computed independently: a separate
manager with the same vignette minus the condition inject, advanced to the same tick, gives a
track confidence of 0.8909 at that instant.

| Condition inject's own effect | Recorded `fired[].value` | Confidence the decision compared | Correct? |
|---|---|---|---|
| `message` (what the shipped tests use) | 0.8908987181403393 | 0.8908987181403393 | ✅ |
| `forced_custody_loss` on the same track, `degrade_to: 0.0` | **0.0** | 0.8908987181403393 | ❌ |
| `forced_custody_loss` on the same track, `mode: drop` | **0.0** | 0.8908987181403393 | ❌ |

The audit log then claims a "custody ≥ 0.5" condition fired at confidence 0.0. The mismatch also
happens in the other direction, and this was reproduced too (seed 5): a `deny_custody` condition
(`min_conf 0.5`, `by_s 0`) fires with no track, so the decision saw confidence 0.0. Its effect is
`reveal_asset` for the same object, and the record shows **1.0**. Both effect types are shipped `FR-4430` inject
primitives (`IP-1062`). A scripted "when Blue gains custody, Red goes dark" inject is a natural
White Cell authoring pattern. The fire decision, fire-once behaviour, effects and replay are all
unaffected: only the informational `value` field is wrong. That is why the severity is Medium, not
High. It still fails `FR-4420`'s stated Output for a reachable configuration, and the package's
own Objective for item 1. Range metrics (`proximity`/`evade`) are not affected in practice,
because no inject effect moves an asset's position at the same instant (`scripted_manoeuvre`
changes velocity only).

**Suggested remedy (for `08`, not applied here):** call `_measure_metric` before
`_apply_inject_effects` in the same branch, and add a regression test whose condition inject
carries a `forced_custody_loss` on the measured track.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Tests 1–2 failed first and pass; existing condition/bus tests green. | Pre-fix scratch tree (a copy of the current tree with exactly `60799fd`'s hunks to `manager.py`, `vignette.py` and `busmodel.py` reverse-applied; `grep -c IP-1064` → 0 in each): 3 of 8 tests in the module fail. They are the updated first-tick test, the new proximity-value test and the new grid test. The two-inject fire-once test passes on both trees, as a behaviour-preservation test should. Post-fix: 8/8 pass. Full suite green. | ✅ Pass |
| Full suite and both permanent gates green; playbook suite green. | See Test run. | ✅ Pass |
| RTM and ledgers updated. | RTM `FR-4420` row cites the three new tests and `IP-1064` ✓; MBP/`packages/INDEX.md`/`ROADMAP.md` read `COMPLETE` ✓. The FS-106 `Referenced By` entry still read "planned"; that is not the reason for return. | ✅ Pass |

The DoD items are all met. The return comes from the Requirements audit (`FR-4420` Outputs) and
the package Objective item 1, which the shipped tests do not exercise: every condition inject in
the test module has a `message` effect only.

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Reproduce the rewind-grid case independently on a shipped vignette with a condition inject or a fixture. | No shipped vignette declares a condition inject, so two shipped vignettes were used at seed 2718, distinct from the implementer's synthetic fixture and seed 0. **(a)** `geo-rpo-shadowing` with a never-firing `proximity` condition inject appended (`BLUE-HVA`↔`RED-INSP`, `max_km 0.001`), which exercises both grids. **(b)** `leo-isr-denial` unchanged, `bus_tick` only. Each was run twice. One run advanced straight to `start + 9·step + 17 µs`. The other advanced to `start + 5·step`, rewound to `start + 3·step + ⌊7·step/11⌋ + 3 µs` (deliberately off-grid at an odd offset), then re-advanced to the same end. **Post-fix:** for both vignettes, the post-rewind `bus_tick`/`condition_check` times are identical (12 and 6 events), every tick is on `start_epoch + k·step`, and the **entire final world** (`model_dump_json`) is byte-identical between the two runs. **Pre-fix** (same probe on the scratch tree): ticks differ, are off-grid, and the final worlds differ. So the fix is what makes the rewind timeline match. | ✅ Pass |
| Confirm `_evaluate_metric`'s results are unchanged for every metric kind. | `git show 60799fd -- spacesim/content/vignette.py` only appends `_measure_metric` after `_evaluate_metric`, so `_evaluate_metric`'s body is byte-unchanged and its result is unchanged for all 14 metric kinds it handles. `_measure_metric` falls back to `_evaluate_metric` for the 10 unmeasured kinds. For `proximity`/`evade` it returns the same `_range_km` the decision compares. A `proximity` firing on `geo-rpo-shadowing` (seed 99) recorded 441.5383579759606 km, exactly the independently computed range at the tick. For `custody`/`deny_custody` it returns `current_confidence(now)`, the same expression the decision compares. **Except** that it is evaluated after the inject's effects (Result above). | ✅ Pass for `_evaluate_metric`; ❌ for the record (see Findings) |
| Run the full suite and both gates by name. | See Test run. | ✅ Pass |

## The updated existing test (flagged for scrutiny)

`test_condition_inject_fires_at_first_true_tick_and_records_fired_payload` previously asserted
`payload["fired"] == [{"inject_id": "cond-inject", "value": True}]`. Its original
(`60799fd^`) text was run on both trees. It **passes pre-fix** and **fails post-fix only** on the
`value` field (`0.8908987181403393 != True`). `FR-4420`'s Outputs and this package's Objective 1
deliberately replace that boolean with the measured confidence, so the old assertion now encodes
behaviour the spec removes, and correcting it is genuine. Every other assertion is kept: one
firing, exactly one `condition_check` entry, and `inject_id == "cond-inject"`. The new value check
(`float`, not `bool`, and `0.5 ≤ value ≤ 1.0` for a `min_conf 0.5` custody condition) is looser
than an exact match, but it is not a weakening. The independent probe shows the recorded value
equals the decision-time confidence exactly for this test's `message` effect. (A sharper "equals
the confidence the decision saw" assertion would still not have caught Finding 1, because the
test's effect never touches the track.)

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Pass/Fail |
|---|---|---|---|---|
| `FR-4420` — Outputs: the evaluated value is recorded | `content/vignette.py::_measure_metric`; `manager.py::_h_condition_check` records it | First-tick test (custody) and proximity-value test; both use `message`-only effects | Cites the tests and `IP-1064` | ❌ **Fail** — the recorded value is measured after the inject's own effects (Finding 1) |
| `FR-4420` — deterministic tick schedule unaffected by rewind position | `busmodel.py::schedule_ticks(anchor=)`; `_arm_schedule` uses `ctx.start_epoch` for both grids | `test_tick_grids_stay_on_the_start_anchored_grid_after_an_off_grid_rewind`; independent two-vignette probe with whole-world equality | As above | ✅ Pass |
| `NFR-1100` — one log scan per tick | `_fired_condition_inject_ids(before_t)`, built lazily once per `_h_condition_check` | `test_two_condition_injects_each_fire_once_at_the_same_tick`. Code read: same `e.sim_time < before_t` filter as before, so live and replay agree (Design Decision 3) | Not a separate RTM trace for this package | ✅ Pass |

## Test run

```
python3 -m pytest -p no:warnings -p no:cacheprovider               # full suite (tree db5f062 = 9ed7b3d minus ledgers)
python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py
# pre-fix scratch tree (60799fd's three code hunks reverse-applied), cwd = scratch copy:
python3 -m pytest -p no:warnings -p no:cacheprovider -q spacesim/tests/test_condition_triggered_injects.py
# original (60799fd^) test module, run against both trees ; vr probe (grid, value) on both trees
```

- **Full suite:** **1022 passed, 3 skipped** (1025 collected), run on the code tree at `db5f062`.
  `9ed7b3d` only adds ledgers on top. `test_vignette_tutorials.py` (the playbook suite) is green.
- **Permanent gates, run by name:** **14 passed**.
- **This package's module:** 8/8 pass; 3/8 fail on the pre-fix tree.

## Scope audit

`git show 60799fd --stat`: `manager.py`, `vignette.py`, `busmodel.py` (exactly the Files to
Modify), the existing test module (the location the package names), and the ledgers. No excursion.
`busmodel.py`'s new `anchor` argument is optional, and `start()` calls it unchanged. No engine
import added (the import guard passes).

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| 1 | `_h_condition_check` measures the firing record's `value` **after** applying the inject's own effects. A condition inject whose effects change the measured quantity (`forced_custody_loss` on the custody-measured track; `reveal_asset` with `deny_custody`) records the post-effect value: 0.0 for a `custody ≥ 0.5` firing that decided at 0.891, and 1.0 for a `deny_custody` firing that decided at 0.0. This contradicts `FR-4420` Outputs and the package's Objective 1 / Design Decision 1. Reproduced above. | Medium | `08-code-implementation` re-run on `IP-1064` (`BL-0278`). Measure before applying effects, and add a regression test with a self-affecting effect |

Not findings: (a) an older `world.now`-versus-`start_epoch` 1 µs difference after `start()` comes
from the intentional lazy multiplayer clock (`start()` arms the grid from `clock.now` before
`set_clock(True)`), and does not affect the grid, because both are anchored to `ctx.start_epoch`.
(b) The FS-106 `Referenced By` tag for `IP-1064` was ambiguous ("planned", shared with `IP-1065`).
It is now tagged as returned.

## Traceability actions taken by this report

- MBP row, `packages/INDEX.md` row, `ROADMAP.md` row: `COMPLETE → IN PROGRESS (returned by VR-1064)`;
  MBP Package Status line.
- RTM `FR-4420` cell: `IP-1064 (COMPLETE …, awaiting 09)` → `IP-1064 (RETURNED 2026-10-17 by
  VR-1064 — record value measured after effects, BL-0278)`. No trace cell was removed.
- FS-106 `Referenced By`: `IP-1064` tagged as returned.
- Backlog: `BL-0131` stays `IN PIPELINE`, with the return noted (its fix is the item that failed).
  `BL-0132`/`BL-0133` stay `IN PIPELINE` because they close when the package is `VERIFIED`; this
  report confirms both parts and records that. New `BL-0278` (Finding 1, `SCHEDULED` → `08`).
  `BL-0270`: `IP-1064` returned; its fresh-session `09` is owed again after the re-run.
