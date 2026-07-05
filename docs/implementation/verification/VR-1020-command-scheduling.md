[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md) ·
[Verification index](INDEX.md) · [Docs index](../../INDEX.md)

# VR-1020 — Verification Report: Command Scheduling (Order/OrderSystem Lifecycle)

## Package

- **ID:** IP-1020
- **Title:** Command Scheduling — Order/OrderSystem Lifecycle
- **Version verified:** 1.0
- **Commit hash verified:** `9e184b66fc7eacece4ff580d2fb7ba71af500c21`

**Process note:** 2 of 11 as-built packages in the `BL-0004` retro-verification sweep (after
`IP-1010`, `VR-1010`). Treated as `COMPLETE` for the purposes of this pass per that sweep's
established convention.

## Result

**✅ VERIFIED** (0 hard failures; 1 Medium finding on the package's own lifecycle-naming claim, 1
Low citation-drift finding)

## Definition of Done audit

| Item | Evidence | Pass/fail |
|---|---|---|
| Four lifecycle states are each independently observable; no direct `queued → confirmed` path | **See Finding 1.** The specific state names claimed (`executing`, `executed-unconfirmed`, `confirmed`) do not exist anywhere in the code — `grep` for each across `spacesim/` returns zero hits in any order-lifecycle context. What *does* exist and is independently observable: `Order.status` stores `queued`/`rejected`/`cancelled` (declared but never actually reached: `draft`, `executed`); `SessionManager.list_orders()` (`manager.py:339-353`) computes a derived, display-only `"executed"` label once `now > earliest_window[0]` — safe only because the sub-stepped clock invariant guarantees the scheduled event already fired by then. The underlying guarantee (states are real and distinguishable, not collapsed to instant) holds; the specific vocabulary this DoD item and the package's own Objective use does not match the code. | ⚠️ Pass on substance, not on the letter — see Finding 1 |
| Stored/ISL delivery is visibly distinct from direct uplink via `Order.via` field | Confirmed: `order.delivery_path` (not literally named `via`, a second citation imprecision, minor) takes `ground_uplink`/`isl_relay`/`stored_program`/`sensor_collect` (`orders.py:80`); `_plan_command()` (`:231`) branches all three delivery paths explicitly. | ✅ Pass |
| `cancel()` never returns an ambiguous result | `cancel()` (`orders.py:206`) returns `bool` unconditionally; `True` only while `status == "queued"` (`:209`), `False` otherwise — confirmed by direct read. `test_queue.py::test_cancel_prevents_execution_and_is_replay_safe` exercises this. | ✅ Pass |
| Sensor-tasking contention is visible via `list_orders()`, not silently resolved | `_plan_collection()` (`orders.py:287`) sets `fail_reason = "sensor_contended"` on a contended request (`:303`), which `list_orders()`'s `"reason"` field surfaces (`manager.py:351`) — visible, not silently dropped. `test_queue.py::test_cancel_observe_frees_sensor_for_rebooking` and `test_pass_capacity_limits_commands_per_window` exercise contention/release directly. | ✅ Pass |
| "Time until window" is computed from the same `AccessProvider.windows()` the engine gates execution on | `windows_ahead()` (`manager.py:361`) and `_next_window()` (`orders.py:391`) both call the same `AccessProvider.windows()` — no separate display-only estimator exists. | ✅ Pass |
| Cyber's non-windowed resolution is structurally distinct (`earliest_window = None`), not a cosmetic UI flag | Confirmed: `_plan_cyber()` (`orders.py:600-603`) sets `order.earliest_window = None` and `order.delivery_path = "cyber"` explicitly, with an inline comment ("cyber is not pass-gated") — a real structural distinction, not a display label. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/fail |
|---|---|---|
| `orders.py:128,201,226,270,282,319,573` read and confirmed against the current tree | **Line numbers have drifted**: `issue` `:128→133`, `cancel` `:201→206`, `_plan_command` `:226→231`, `_best_isl_window` `:270→275`, `_plan_collection` `:282→287`, `_candidate_sensors`/`_contended` `:314/:319→319/324` (all a consistent +5, matching `VR-1010`'s finding on the same file), but `_plan_cyber` `:573→600` (+27 — a larger, inconsistent offset, because `IP-2010`'s v1.1 `custody_confidence_at_decision` capture and related cyber-payload code landed between `_plan_collection` and `_plan_cyber` since this package was authored). Content confirmed correct at every new location. | ✅ Pass (citation drift, Finding 2) |
| Order-system test suite present and green | `python3 -m pytest spacesim/tests/test_orders.py spacesim/tests/test_queue.py spacesim/tests/test_clock_and_time.py` — 22 passed. Full suite: 566 passed/3 skipped (unchanged since `VR-1010`). | ✅ Pass |
| No FR/NFR explicitly cites FS-102 | Confirmed independently: `docs/features/FS-102-command-scheduling.md` and a grep of `01-functional-requirements.md` for "FS-102" — no hits. | ✅ Pass |

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state (before → after this VR) | Pass/fail |
|---|---|---|---|---|
| FR-3110 | `engine/orders.py` (`issue`, commit-side share with `IP-1010`) | `test_validate_order.py`, `test_orders.py`, `test_queue.py` | Updated to note both `VR-1010` and `VR-1020` now confirmed (was flagging `IP-1020` as awaiting its own pass) | ✅ Pass |
| FR-3410 | `engine/orders.py` (delivery-path selection) | same as above | Same update as `FR-3110` | ✅ Pass |
| FR-1130 | `engine/clock.py` (`Scheduler`, sub-stepped advance) | `test_clock_and_time.py` | Test: `UNASSIGNED` → filled (this VR); Impl. Package left `UNASSIGNED` — `clock.py` is foundational engine infra with no single owning `IP-xxxx` | ✅ Pass |
| FR-1420 | `engine/orders.py`'s `_plan_cyber` routing half | `test_orders.py::test_cyber_resolves_outside_any_pass_window` | Test: `UNASSIGNED` → filled (this VR, `orders.py` routing half only — `effects.py`/`cyber.py`'s own resolution mechanism is a different package's territory, Impl. Package cell left as-is) | ✅ Pass |
| NFR-1600 | `engine/orders.py`'s `cancel()` | `test_queue.py::test_cancel_prevents_execution_and_is_replay_safe` | Already filled by `VR-1010` (orders.py half); this package's specific `cancel()` contribution reconfirmed, no cell change needed | ✅ Pass |

## Test run

```
$ python3 -m pytest
566 passed, 3 skipped, 1 warning in 82.14s

$ python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py -v
14 passed in 0.88s

$ python3 -m pytest spacesim/tests/test_orders.py spacesim/tests/test_queue.py spacesim/tests/test_clock_and_time.py -v
22 passed in 2.25s
```

No regression from `VR-1010` (run #18)'s count.

## Scope audit

**Files to Create: none. Files to Modify: none** — no implementing diff to scope-check. The three
"Reference files" (`orders.py`, `clock.py`, `inprocess.py`) were each read for this verification.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| 1 | The package's Objective and Definition of Done describe a "four-state lifecycle (`queued → executing → executed-unconfirmed → confirmed`)." None of `executing`, `executed-unconfirmed`, or `confirmed` exist anywhere in the code as order-lifecycle values — confirmed by grepping the whole `spacesim/` tree. The actual mechanism is simpler: `Order.status` stores `queued`/`rejected`/`cancelled` (only these three are ever actually reached), and `SessionManager.list_orders()` computes a *derived, display-only* `"executed"` label once the sim clock has passed the order's window start — safe only because of the sub-stepped-clock invariant, not because any handler writes `"executed"` back onto the `Order`. The functional guarantee (states are real, observable, and not collapsed to instant) holds; the specific vocabulary does not match the code. Also minor: the DoD's "`Order.via` field" should read `Order.delivery_path`. | Medium | `07-implementation-planning`, next touch of `IP-1020` — restate the Objective/DoD in the actual 3-status-plus-derived-display-label terms, or confirm with `06-feature-specification` whether FS-102's own text uses this same invented vocabulary and needs the same correction |
| 2 | `orders.py` line citations have drifted: a consistent +5 for six of seven cited functions (same drift `VR-1010` found in this file), but `_plan_cyber` drifted +27 (`IP-2010`'s v1.1 cyber-payload code landed between it and `_plan_collection`). Content confirmed correct at the new locations. | Low | Fold into `IP-1020`'s next package-maintenance touch; no dedicated run. Same drift class as `BL-0016`/`BL-0032`. |

No Critical/High findings.

## Related

[`IP-1020`](../packages/IP-1020-command-scheduling.md) ·
[`FS-102`](../../features/FS-102-command-scheduling.md) ·
[`00-master-build-plan.md`](../00-master-build-plan.md) ·
[`03-requirements-traceability-matrix.md`](../../requirements/03-requirements-traceability-matrix.md)
