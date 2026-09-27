# VR-1062 — Verification Report: Condition-Triggered Injects & New Inject Effect Types

> **Document ID:** VR-1062
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1062](../packages/IP-1062-condition-triggered-injects-and-new-effects.md), [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.1 (`FR-4420`, `FR-4430`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → IN PROGRESS` return of IP-1062 (RETURNED)
> **Feature Mapping:** FS-106 v2.1 (`FR-4420`/`FR-4430` slice)
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/engine/bus.py`](../../../spacesim/engine/bus.py),
> [`spacesim/engine/entities.py`](../../../spacesim/engine/entities.py),
> [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1062 — Condition-Triggered Injects & New Inject Effect Types
- **Version verified:** 1.0
- **Tree state verified:** code at `d2818ff`. Branch tip `b95e4a8` differs only by docs-only
  verification commits. Implementing commit: `826dc32`.
- **Independence:** implemented by `08-code-implementation` in a prior context. This verification
  ran in a freshly spawned agent context with no memory of that work. **Disclosure:** the
  implementing commit's `Claude-Session` trailer names the same outer remote session ID this agent
  runs under. Every claim was re-derived from the source, a fresh test run, and independent probes.
  The probes used a real orbit-bearing proximity condition with rewinds, and drove the new effects
  against a started library vignette (`leo-isr-denial`).

## Result

**RETURNED — 1 failed check (High H1), plus 1 Medium and 4 Low findings.** The condition-trigger
mechanism (`FR-4420`) is sound. It fires at the first true tick, fires once, needs no mid-handler
append, replays byte-identically, and survives rewinds, all independently confirmed.

Three of the four new effects behave as specified. The `anomaly` effect with `subsystem: "bus"`
does not. It sets only `bus_state.mode = "safe_mode"` and leaves `safe_mode.active = False`, with
no cause recorded in `SafeModeState` and attitude/FSW modes still nominal. The result is an
internally inconsistent half-safe state:

- The operator's recovery strip reports `safe_mode: True`.
- `begin_recovery` refuses with `not_safed`.
- The `asset_safed` objective metric evaluates `False`.

So the "reuse the existing safe-mode/RecoverySystem recovery loop" behaviour promised by the
package's own Design Decision 4 is not delivered, and a trainee cannot recover the asset.

The full suite is green (707 passed, 3 skipped), and both permanent gates are green.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Explicit user authorization (MSTR-006 §3). | Granted 2026-09-27; recorded in the package and in the Master Build Plan. | ✅ Pass |
| A condition-triggered inject fires at the first scheduled tick where its condition is true, and never before. | `manager.py:949-972` `_h_condition_check` evaluates `content/vignette.py::_evaluate_metric` against the replayed `world` and writes `payload["fired"]` in place. There is no `eventlog.append` inside the handler (confirmed by reading `engine/simulation.py:66-78`: the append follows the handler call with the same payload dict). The probe used a `proximity` condition between two real Kepler orbits with the threshold set between sampled ranges. It fired first at tick 7, where the range first drops below the threshold (ranges 5479–10345 km, threshold 7225). `test_condition_inject_fires_at_first_true_tick_and_records_fired_payload` passes. | ✅ Pass |
| The same inject fires at the identical tick under replay of `(initial_state, eventlog, seed)`. | The probe compared `mgr.sim.replay()` against the live `WorldState` for the plain run, a rewind to the exact firing tick, a rewind to one tick before, and a rewind to a non-aligned time, followed by re-advancing. All four gave replay equal to live (`True`), and every run fired exactly once. `test_condition_inject_fires_at_identical_tick_under_replay` passes. See L3 for how the tick grid shifts after a non-aligned rewind. | ✅ Pass |
| A vignette with no condition-triggered injects schedules zero `condition_check` events. | `manager.py:158-165`: the `any(... == "condition")` guard. The test passes. | ✅ Pass |
| Each of the four new effect types produces the state change in System Behaviour; `forced_custody_loss` never touches another cell's `Track`. | `sensor_outage` (`:902-909`), `forced_custody_loss` (`:910-919`, using the cell-scoped `track_for`) and `scripted_manoeuvre` (`:920-937`) all behave as specified, and all 12 `test_inject_effects_v2.py` tests pass. `anomaly` (`:887-901`) does literally what System Behaviour's first sentence says (`bus_state.mode = "safe_mode"`). That leaves the asset in a state the rest of the engine does not treat as safed (see H1), which contradicts the same package's Design Decision 4 rationale. The recorded cause survives only in the event-log payload and a message; `SafeModeState.cause` stays `None`. | ❌ **Fail** (H1) |
| `scripted_manoeuvre` changes `asset.orbit` via the named entry mode without touching `delta_v_ms`. | `:920-937` calls `compute_maneuver()` then `self.osys.prop.apply_impulse()`, and reads or writes no `resources` field (read line by line). Probe on `ISR-EO-1`, `hohmann` mode: `a_m` went from 6978137 to 6928137 m (default 550 km target) while `delta_v_ms` stayed at 80.0. Both mode tests pass. | ✅ Pass |
| A degraded sensor is absent from `sensor_observation` endpoints, and restoring it brings it back. | `engine/orders.py:95` filter; `entities.py` `Sensor.health` defaults to `"nominal"`. `test_scene_from_world_excludes_degraded_sensor` passes. | ✅ Pass |
| Every existing inject-library and effect test still passes unchanged. | `test_inject_library.py` diff: only the `_KNOWN_EFFECT_TYPES` doc set changed. The full suite passes, including IP-1061's A1/A3 tests. | ✅ Pass |
| Full suite green; both gates green. | See Test run. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| New test files exist and pass. | `test_condition_triggered_injects.py` (5 tests) and `test_inject_effects_v2.py` (12 tests) all pass. | ✅ Pass |
| `test_determinism.py` passes. | 14 passed (with the import guard). | ✅ Pass |
| `test_import_guard.py` passes. | Same run. The engine changes are one additive field plus one filter line, with no clock or RNG use. | ✅ Pass |
| Full suite has zero regressions, especially `test_inject_library.py`. | 707 passed, 3 skipped. | ✅ Pass |
| Independently confirm the firing-state check filters by `e.sim_time < world.now`. | `manager.py:944`: `if e.kind == "condition_check" and e.sim_time < before_t`, called with `world.now`. That is a time filter, not list position, which is replay-safe. | ✅ Pass |
| Independently confirm `scripted_manoeuvre` does not read or write `delta_v_ms`. | Confirmed by reading `:920-937` and by the probe. | ✅ Pass |
| Independently round-trip a condition-triggered inject through a rewind and replay. | Done with four rewind variants (see the DoD rows above). | ✅ Pass |

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-4420 | `manager.py` (`_arm_schedule` condition-tick block, `_condition_inject_already_fired`, `_h_condition_check`, handler registration `:55`) | `test_condition_triggered_injects.py` (5) | `:172` is accurate. Annotated `RETURNED (VR-1062)` at package level; this requirement itself was confirmed met. | ✅ Pass (L1, L2) |
| FR-4430 | `manager.py::_apply_inject_effects` (4 new branches); `entities.py` `Sensor.health`; `orders.py` sensor filter | `test_inject_effects_v2.py` (12) | `:173`, annotated **H1: `anomaly`/bus leaves a half-safe, unrecoverable state**. | ❌ Fail (H1) |

## Test run

```
PYTHONPATH=. python3 <scratchpad>/p1062b.py     # condition/rewind/replay + malformed-effect probe
  → fired at tick 7; replay==live True for plain / rewind-to-fire-tick / rewind-before / rewind non-aligned
  → non-aligned rewind: fired at tick index 6 on the new grid (see L3)
  → repeatable=True always-true condition over 5 ticks: fired 1 time (see L1)
  → malformed effects: scripted_manoeuvre w/o mode → KeyError; mode 'bogus' → ValueError;
    forced_custody_loss w/o cell → KeyError; anomaly w/o target → KeyError (see M1)
  → hohmann scripted manoeuvre: delta_v_ms 80.0 → 80.0, a_m changed
PYTHONPATH=. python3 <scratchpad>/p1062c.py     # anomaly(bus) vs the safe-mode machinery
  → mode safe_mode, safe_mode.active False, cause None, attitude nominal, fsw nominal
  → asset_safed metric False; recovery_status safe_mode True; begin_recovery {'ok': False, 'reason': 'not_safed'}
PYTHONPATH=. python3 <scratchpad>/p1062d.py     # anomaly effects persist across 20 min of bus ticks → yes

python3 -m pytest -o addopts="" -q spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py  → 14 passed
python3 -m pytest -o addopts="" -q            → 707 passed, 3 skipped, 1 warning in 156.06s
```

## Scope audit

`git show --stat 826dc32` touched:

- **Code:** `session/manager.py`, `engine/entities.py`, `engine/orders.py`. These match Files to
  Modify exactly; `content/vignette.py` was correctly left unmodified.
- **Tests:** the new `test_condition_triggered_injects.py` and `test_inject_effects_v2.py`, plus the
  documentation-set line in `test_inject_library.py`.
- **Docs:** `CLAUDE.md`, `ROADMAP.md`, `FS-106`, the RTM, the Master Build Plan,
  `packages/INDEX.md`, `01-technical-work-breakdown.md`, the package, and
  `docs/pipeline/pipeline-journal.md`.

The journal edit is the same process note as `VR-1190` L2. No code outside scope.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| H1 | **The `anomaly` effect with `subsystem: "bus"` creates an inconsistent, operator-unrecoverable half-safe state.** It sets `bus_state.mode = "safe_mode"` directly, not through `engine/bus.py::enter_safe_mode()`. As a result `safe_mode.active` stays `False`, `safe_mode.cause`/`entered_at` stay unset, and `attitude.mode`/`cdh.fsw_mode` stay `nominal`. The effects: `recovery_status` shows `safe_mode: True` with recovery steps; `begin_recovery` returns `not_safed`; the `asset_safed` objective metric is `False`. The package's Design Decision 4 ("deliberately reusing the existing safe-mode/RecoverySystem recovery loop for player-visible consequences") is therefore not realized. The `restore: true` path has the mirror problem: on a genuinely safed asset it sets `mode = "nominal"` but leaves `safe_mode.active = True`. **Fix direction:** call `enter_safe_mode(bus, world.now, cause)` / `exit_safe_mode(bus)`, which also records the controller-set true cause in `SafeModeState.cause`. Add a test that `begin_recovery` accepts an anomaly-safed asset. The package's System Behaviour sentence should be corrected to match. `IP-1260`, which is `BLOCKED` on this package reaching `VERIFIED` for its `anomaly` dependency, stays blocked until this is fixed. | **High** | `08-code-implementation` re-run on IP-1062; `07-implementation-planning` to correct the System Behaviour text |
| M1 | **A malformed new-effect payload raises mid-handler, leaving an unlogged partial mutation.** Missing `mode`, `cell` or `target` keys, or an unknown manoeuvre mode, raise `KeyError`/`ValueError` from `_apply_inject_effects`. Earlier effects in the same list, or earlier condition-triggered injects in the same `condition_check` tick, have already mutated `world`, but `Simulation.advance_to` never logs the event. Live state then diverges from what replay reproduces, which violates invariant 1 in spirit. For a condition inject, the next tick re-evaluates, re-applies the partial effects, and raises again. The pre-existing `gs_outage`/`reveal_asset` branches share the pattern, but this package adds four new unguarded surfaces. IP-1061 explicitly set the posture that "a malformed inject cannot abort a running exercise". Only reachable through malformed authoring, since effects have no schema validation at load. | Medium | `07-implementation-planning` (validate inject effects at vignette load and inject-fire time, or guard per effect) |
| L1 | `Inject.repeatable` is ignored for condition-triggered injects. They always fire once (probe: `repeatable: true` with an always-true condition fired once in 5 ticks). `FR-4420`'s Precondition ("a *non-repeatable* … inject must not have already fired") implies repeatable ones may re-fire. | Low | `07-implementation-planning`/`04` (clarify, then implement or document) |
| L2 | The event-log "evaluated value" is always the literal `True` (`{"inject_id", "value": True}`), because `_evaluate_metric` returns a bool. `FR-4420`'s Output asks for "the condition's evaluated value". For a threshold condition, the measured quantity (range km, confidence) would be the informative value. | Low | `07-implementation-planning` |
| L3 | After a rewind to a time not aligned with the tick grid, `_arm_schedule` re-arms `condition_check` at `t + k·step`, so the tick grid shifts. Probe: an inject that originally fired at tick 7 fired at index 6 of the new grid, a different sim time from the un-rewound run. Replay of the resulting log is still exact, so determinism holds, but "rewind then re-advance unchanged" does not reproduce the original timeline. This is inherited from the pre-existing bus-tick re-arm behaviour. | Low | `07-implementation-planning` (anchor both grids to `start_epoch`) |
| L4 | `_condition_inject_already_fired` scans the whole event log once per condition inject per tick, and again on every rebuild, which is O(entries × ticks). Fine at current vignette scale; worth noting for long sessions. | Low | `07-implementation-planning` (optional) |

## Related

[IP-1062](../packages/IP-1062-condition-triggered-injects-and-new-effects.md) · [FS-106](../../features/FS-106-white-cell-dashboard.md) ·
[VR-1061](VR-1061-inject-and-sizing-defect-remediation.md) · [IP-1260](../packages/IP-1260-telemetry-csv-export.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md)
