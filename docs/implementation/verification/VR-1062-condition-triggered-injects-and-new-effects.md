# VR-1062 — Verification Report: Condition-Triggered Injects & New Inject Effect Types

> **Document ID:** VR-1062
> **Version:** 2.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1062](../packages/IP-1062-condition-triggered-injects-and-new-effects.md), [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.1 (`FR-4420`, `FR-4430`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of IP-1062 (this v2.0 pass)
> **Feature Mapping:** FS-106 v2.1 (`FR-4420`/`FR-4430` slice)
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/engine/bus.py`](../../../spacesim/engine/bus.py),
> [`spacesim/engine/entities.py`](../../../spacesim/engine/entities.py),
> [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1062 — Condition-Triggered Injects & New Inject Effect Types
- **Version verified:** 1.0 (remediated)
- **Tree state verified:** commit `d2fc118` (branch `claude/chart-prompt-file-90hm9u`). Remediating
  commit: `2edef60` (`fix(IP-1062): route anomaly bus effect through
  enter_safe_mode/exit_safe_mode (BL-0128)`).
- **Independence:** second verification pass (v2.0), fresh session with no involvement in either
  the `2edef60` remediation or the v1.0 (`853bd7f`-era) report that returned this package on
  Finding H1. All claims below re-derived independently.

## Result

**VERIFIED — the v1.0 High finding (`BL-0128`) is fixed and independently reconfirmed.** The
`anomaly` effect's `subsystem: "bus"` branch (and its `restore` mirror) now calls
`enter_safe_mode()`/`exit_safe_mode()` from `engine/bus.py`, so `safe_mode.active`/`cause`/
`entered_at` are fully consistent and `begin_recovery()` accepts a safed asset. Full suite green
(753 passed, 3 skipped), both permanent gates green. **One Medium finding remains open by design**
(`BL-0129`, malformed-effect-payload mid-handler exception) — confirmed still unfixed, correctly
tracked as a separate `SCHEDULED` backlog item outside this remediation's declared scope, not a
surprise or an omission.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Explicit user authorization for the remediation (MSTR-006 §3). | Package header: "authorized 2026-09-27, project owner's direct instruction." | ✅ Pass |
| `anomaly` bus-subsystem branch now uses `enter_safe_mode`/`exit_safe_mode` (`BL-0128`). | `manager.py:19` imports both from `engine/bus.py`; `manager.py:944-949`: `subsystem == "bus"` branch calls `exit_safe_mode(asset.bus_state)` on restore, else `enter_safe_mode(asset.bus_state, world.now, cause)`. `enter_safe_mode` (`bus.py:301-306`) sets `bus.mode`, `bus.safe_mode = SafeModeState(active=True, entered_at=now, cause=cause)`, attitude/CDH safe modes, and recomputes status — the full state `begin_recovery` needs, not merely `bus.mode`. | ✅ Pass |
| `begin_recovery` accepts an anomaly-safed asset. | `test_anomaly_safed_asset_is_accepted_by_begin_recovery` (`test_inject_effects_v2.py:78-88`) asserts `result["reason"] != "not_safed"` after an anomaly effect. Independently re-run: passes. Independent manual probe (see Test run) confirms `begin_recovery("blue","SAT-1","")` on a freshly anomaly-safed asset no longer returns `not_safed`. | ✅ Pass |
| Strengthened existing bus-subsystem test asserts full `safe_mode` state, not just `mode`. | `test_anomaly_bus_subsystem_sets_safe_mode_and_restore_clears_it` (`:55-75`) asserts `bus.safe_mode.active`, `.cause`, `.entered_at`, and that restore clears `.active`. | ✅ Pass |
| Full suite green, both permanent gates green. | 753 passed, 3 skipped (up from 678 at implementation time — growth from the other 8 packages in this batch, not a regression). `test_determinism.py` 6 passed, `test_import_guard.py` 8 passed. | ✅ Pass |
| `BL-0091`/`BL-0095` design decisions (scripted-manoeuvre entry mode, deleted-target no-op, Δv bypass) remain correctly implemented (unchanged by this remediation, re-confirmed). | `manager.py`'s `scripted_manoeuvre` branch: no read or write of `asset.resources.delta_v_ms` anywhere in `_apply_inject_effects` (`grep -n delta_v_ms spacesim/session/manager.py` returns only unrelated ledger-display lines, none inside the effect-application method). `test_scripted_manoeuvre_changes_orbit_via_eci_mode_bypassing_delta_v_budget` / `_via_hohmann_mode` both green. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `test_condition_triggered_injects.py` and new effect-type tests exist and are green. | `test_condition_triggered_injects.py` (9 tests) + `test_inject_effects_v2.py` (11 tests, including the new `test_anomaly_safed_asset_is_accepted_by_begin_recovery`) — all green. | ✅ Pass |
| `test_determinism.py` remains green. | 6 passed. | ✅ Pass |
| `test_import_guard.py` remains green. | 8 passed. No `spacesim/engine/` file (`bus.py`, `entities.py`, `orders.py`) gained a wall-clock read or non-`rng.py` random use; `enter_safe_mode`/`exit_safe_mode` are pure functions of their arguments, unchanged by this remediation. | ✅ Pass |
| Full suite re-run, zero regressions, `test_inject_library.py` in particular. | `test_inject_library.py` — all green (re-run standalone and as part of the full suite). | ✅ Pass |
| Independently confirm the firing-state check filters by `e.sim_time < world.now`. | `manager.py:997`: `if e.kind == "condition_check" and e.sim_time < before_t:` inside the helper that answers "has this inject already fired" — confirmed by direct read, not by re-citing the package. | ✅ Pass |
| Independently confirm `scripted_manoeuvre` never reads/writes `delta_v_ms`. | Confirmed by direct read of the effect branch (see DoD row above) — the branch calls `compute_maneuver()`/`apply_impulse()` only, no `AssetResources` field access. | ✅ Pass |
| Independently round-trip a condition-triggered inject through rewind/replay. | `test_condition_inject_fires_at_identical_tick_under_replay` (`test_condition_triggered_injects.py:88-107`) does exactly this against `mgr.sim.replay()` — live and replayed firing tick/time match. Independently re-run: passes. A second independent probe (fresh script, not the package's own test) reproduced the same result against a differently-parameterized custody condition. | ✅ Pass |

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-4420 | `manager.py::_h_condition_check`, `_arm_schedule`'s conditional `condition_check` scheduling | `test_condition_triggered_injects.py` (9 tests) | `docs/requirements/03-requirements-traceability-matrix.md` — see RTM correction below | ✅ Pass |
| FR-4430 | `manager.py::_apply_inject_effects`'s four new branches (`anomaly`, `sensor_outage`, `forced_custody_loss`, `scripted_manoeuvre`); `entities.py::Sensor.health`; `orders.py::scene_from_world`'s degraded-sensor filter | `test_inject_effects_v2.py` (11 tests) | RTM correction below | ✅ Pass |

## Test run

Commands run on the `d2fc118` tree:

```
python3 -m pytest -q                                                              # full suite
  → 753 passed, 3 skipped, 1 warning in 168.20s

python3 -m pytest spacesim/tests/test_determinism.py -q                           # gate 1
  → 6 passed
python3 -m pytest spacesim/tests/test_import_guard.py -q                          # gate 2
  → 8 passed

python3 -m pytest spacesim/tests/test_inject_effects_v2.py \
  spacesim/tests/test_condition_triggered_injects.py \
  spacesim/tests/test_inject_library.py -q
  → 33 passed
```

Independent manual probe (`begin_recovery` on an anomaly-safed asset, not the package's own test):
```
SessionManager + a bare Asset with BusState(); _apply_inject_effects(anomaly/bus/no restore)
→ bus.mode == "safe_mode"; bus.safe_mode.active == True; entered_at == world.now
begin_recovery("blue", "SAT-1", "") → reason != "not_safed"   (confirms BL-0128 fix)
```

## Scope audit

`git show --stat 2edef60` touches: `docs/implementation/00-master-build-plan.md`,
`docs/implementation/packages/IP-1062-condition-triggered-injects-and-new-effects.md`,
`docs/pipeline/backlog.md`, `spacesim/session/manager.py`,
`spacesim/tests/test_inject_effects_v2.py`. All within the package's own declared surface
(`Files to Modify` names `session/manager.py`) or natural test/doc companions. No
`spacesim/engine/` file touched by the remediation itself — `enter_safe_mode`/`exit_safe_mode`
were pre-existing, unmodified functions the remediation now calls correctly. No unexplained
excursion.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| M1 *(pre-existing, `BL-0129`, correctly out of this remediation's scope)* | A malformed new-effect payload (missing `mode`/`cell`/`target`, or an unknown manoeuvre mode) still raises mid-handler in `_apply_inject_effects` — confirmed unchanged by this remediation (no try/except added around the four new branches). Only reachable through malformed authoring; tracked separately as `BL-0129`, `SCHEDULED`. Not a defect of this package's own Definition of Done, which never claimed to fix it. | Medium (open, tracked) | `07-implementation-planning` (per `BL-0129`'s own routing) |
| L1 (new, cosmetic) | The `anomaly` effect's subsystem-mapping interpretation (Design Decision 4 — "bus"→safe mode, "telemetry"→comms degraded) remains an implementation-time interpretation not yet ratified by `04-requirements-engineering`/`06-feature-specification`, as the package's own Risks section already discloses. No new information from this pass; restated for completeness since this report is the traceability audit of record for `FR-4430`. | Low | `06-feature-specification` (per the package's own routing, unchanged) |

## RTM correction applied by this report

`docs/requirements/03-requirements-traceability-matrix.md`'s `FR-4420`/`FR-4430` rows updated:
`Implementation Package` cell confirmed as `IP-1062` (`VERIFIED`, this report), `Test` cell
confirmed against the actual test files above.

## Related

[IP-1062](../packages/IP-1062-condition-triggered-injects-and-new-effects.md) ·
[FS-106](../../features/FS-106-white-cell-dashboard.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md)

## Prior pass (v1.0, superseded)

v1.0 returned this package on Finding H1 (`BL-0128`): the `anomaly` effect's bus-subsystem branch
set `bus_state.mode` directly instead of calling `enter_safe_mode()`/`exit_safe_mode()`, leaving
`safe_mode.active` unset and `begin_recovery` refusing with `not_safed`. v1.0 also surfaced Medium
finding `BL-0129` (malformed-payload mid-handler exception, still open, tracked separately) and 4
Low findings (subsystem-mapping interpretation, among others); `FR-4420` (the condition trigger,
including replay and rewinds) was independently confirmed sound at v1.0 already. This v2.0 pass
confirms the H1 fix and closes the package to `VERIFIED`.
