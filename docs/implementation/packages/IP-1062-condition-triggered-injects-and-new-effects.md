# IP-1062 — Condition-Triggered Injects & New Inject Effect Types

> **Package ID:** IP-1062
> **Version:** 1.0
> **Status:** 🔵 COMPLETE *(implemented 2026-09-27, MSTR-006 §3 authorization granted the same day;
> awaiting `09-package-verification` in a fresh session — this session implemented it and may not
> verify its own work)*
> **Remediation (2026-09-27/28, authorized by the project owner per MSTR-006 §3):** an independent
> fresh-session verification pass ([VR-1062](../verification/VR-1062-condition-triggered-injects-and-new-effects.md))
> found the `anomaly` effect's `subsystem: "bus"` branch set `bus_state.mode = "safe_mode"`
> directly instead of calling `engine/bus.py::enter_safe_mode()`, leaving `safe_mode.active`
> `False` and `cause`/`entered_at` unset — `begin_recovery` refused with `not_safed` and the asset
> was operator-unrecoverable; the `restore: true` path had the mirror defect (Finding H1, High).
> Design Decision 4's own stated intent ("reusing the existing safe-mode/`RecoverySystem` recovery
> loop") was therefore not actually realized. **Fixed:** both branches now call
> `enter_safe_mode(bus, world.now, cause)`/`exit_safe_mode(bus)`. Added
> `test_anomaly_safed_asset_is_accepted_by_begin_recovery` (`test_inject_effects_v2.py`) plus
> stronger assertions on the existing bus-subsystem test (`safe_mode.active`/`cause`/`entered_at`).
> Full suite green (both permanent gates included). This unblocks `IP-1260` once this package is
> re-`VERIFIED`. Re-verification is a fresh `09-package-verification` pass, not yet run.
> **Dependencies:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.1
> (`FR-4420`/`FR-4430`), [IP-1061](IP-1061-inject-and-sizing-defect-remediation.md) (`COMPLETE`,
> not a build dependency but the most recent prior touch of the same `_h_inject`/`_arm_schedule`
> code this package also modifies — must not regress its A1/A3 fixes), `FR-1310` (the
> operator-order Δv gate this package's scripted-manoeuvre effect deliberately bypasses, per
> `ADR-0005`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [docs/pipeline/backlog.md](../../pipeline/backlog.md) `BL-0070` (external validation report,
> 26 Sep 2026, item B4), `BL-0091` (scripted-manoeuvre entry-mode ambiguity, resolved below),
> `BL-0095` (two Open Questions, resolved below)
> **Produces:** deterministic condition-triggered inject firing plus four new inject effect types
> (`anomaly`, `sensor_outage`, `forced_custody_loss`, `scripted_manoeuvre`), satisfying
> `FR-4420`/`FR-4430` in full
> **Feature Reference:** [FS-106 — White Cell Dashboard](../../features/FS-106-white-cell-dashboard.md) v2.1
> **Supersedes:** none — new package (sibling slice of `IP-1060`/`IP-1061`, same Feature Spec)
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/engine/maneuver.py`](../../../spacesim/engine/maneuver.py),
> [`spacesim/engine/custody.py`](../../../spacesim/engine/custody.py),
> [`spacesim/engine/entities.py`](../../../spacesim/engine/entities.py),
> [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package. Confirmed directly against the live code at authoring time:
`SessionManager._h_inject` (`session/manager.py` lines 714-785) is a flat `if/elif` dispatch over
`eff.get("type")`, called only for scheduled/immediate "inject" events; `_arm_schedule` (lines
143-172) only knows about `trigger.type == "time"`; `engine/maneuver.py::compute_maneuver()` (lines
251+) computes a Δv impulse but never applies it — application happens in `OrderSystem._h_maneuver`
(`engine/orders.py` lines 677-689) via `self.prop.apply_impulse(...)`, which also enforces the
`delta_v_ms` gate this package's scripted-manoeuvre effect must bypass; `engine/entities.py`'s
`Sensor` model (lines 68-77) has no health/availability field today, unlike `Asset.health` (used by
the existing `gs_outage` effect via `orders.py::scene_from_world`'s degraded-ground-station filter,
lines 86-94).*

## Package ID

IP-1062

## Title

Condition-Triggered Injects & New Inject Effect Types

## Objective

Let White Cell author an inject whose trigger is a deterministic condition over engine state
(range/custody/objective-state), evaluated only on scheduled engine ticks; and extend the inject
effect vocabulary with four new effect types (anomaly, sensor outage, forced custody loss, scripted
manoeuvre), all reusing existing engine machinery rather than introducing parallel mechanisms.

> **This is a forward-design package. Per MSTR-006 §3, this document's own specification is not
> itself an authorization to write code** — a separate, explicit user go-ahead is required before
> any Implementation Task below begins.

## Feature Reference

[FS-106 — White Cell Dashboard](../../features/FS-106-white-cell-dashboard.md) v2.1

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-4420 | Condition-triggered injects, evaluated deterministically | A new periodic `"condition_check"` event, scheduled at the same cadence as the existing `bus_tick` events, evaluates every not-yet-fired condition-triggered inject against the current `WorldState` at each tick; firing is a pure function of replayed state, so it reproduces byte-identically under replay with no wall-clock/out-of-band involvement. |
| FR-4430 | Four new inject effect types | `anomaly`, `sensor_outage`, `forced_custody_loss`, `scripted_manoeuvre` added as four new branches of the existing `_h_inject` dispatch (shared with the condition-triggered path via a common effect-application helper), each grounded in an existing engine mechanism (bus/comms status, a new `Sensor.health` field mirroring the existing ground-station-outage filter, `Track` mutation, `engine/maneuver.py`'s six entry modes + `Propagator.apply_impulse`). |

## Architecture Components

- **C2 Session / Application Layer** (`session/manager.py`) — owns the inject dispatch
  (`_h_inject`), the new condition-evaluation handler (`_h_condition_check`), and the extended
  `_arm_schedule` that queues condition-check ticks. Both handlers are session-layer, not
  engine-layer, code (consistent with every other inject handler already registered here) — this
  package introduces no new `spacesim/engine/` import-boundary crossing.
- **C1 Deterministic Core** (`engine/custody.py`, `engine/maneuver.py`, `engine/entities.py`,
  `engine/orders.py`) — supplies the pure, already-existing primitives this package's new effect
  branches call into (`Track` mutation, `compute_maneuver()`, `Propagator.apply_impulse()`,
  `Asset`/`Sensor` health fields) — no new engine subsystem, only two additive schema fields
  (below).
- **C5 Content & Data** (`content/vignette.py`) — no schema change to `Inject` itself (`trigger:
  dict`, `effects: list[dict]` already accept arbitrary shapes); a condition trigger and the four
  new effect types are new *data shapes* within these existing fields, per `ADR-0007`.

## Interfaces

`INT-0016` (White Cell → Simulation Engine, inject application) — this package's condition-trigger
path and four new effect types operate entirely through this existing interface (still a `WorldState`
direct-mutation inject, still deterministic-event-loop-scheduled); no ICD edit needed.

## Design Decisions (resolving `BL-0091` and `BL-0095`)

1. **`BL-0091` — scripted-manoeuvre entry-mode resolution.** A `scripted_manoeuvre` effect **must**
   resolve through `engine/maneuver.py`'s existing six entry modes (`eci`/`lvlh`/`finite_burn`/
   `target_coe`/`hohmann`/`plane_change`) via `compute_maneuver()` — never a distinct
   "set-resulting-state-directly" path. Rationale: a second, parallel manoeuvre code path would be
   a duplicate-mechanism risk (two ways to move an asset that could silently diverge in behavior),
   and every existing manoeuvre in the system (operator-issued orders, `dry_run()` previews) already
   goes through this one function — reusing it, not inventing a shortcut, is the "minimal surgery
   over invention" pattern this increment's other packages (`ADR-0034`/`ADR-0035`, `IP-1180`) also
   follow.
2. **`BL-0095` (part 1) — condition-triggered inject targeting a deleted/expired asset, track, or
   cell.** The condition simply evaluates false forever (never fires) — no error, no special-case
   handling. Rationale: this is the natural behavior of the condition-evaluation code itself (e.g.
   `world.track_for(cell, object)` already returns `None` for a nonexistent track, and a `None`
   result is treated as "condition not satisfied," not as an exceptional state) — no additional
   logic is needed to produce this behavior, so it is the cheapest, most consistent answer and
   requires no new error-handling branch.
3. **`BL-0095` (part 2) — scripted-manoeuvre Δv-gate bypass.** A scripted-manoeuvre inject effect
   **bypasses** `AssetResources.delta_v_ms` entirely — it neither checks nor deducts it. Rationale:
   `ADR-0005` already establishes injects as the documented, accepted bypass of plan-first
   commanding constraints for White-Cell narrative control; a facilitator scripting a manoeuvre is
   exercising that same documented authority, not issuing an operator order. **This is a
   consequential decision White Cell should understand: a scripted manoeuvre is "free" of the
   normal budget**, unlike every operator-issued manoeuvre order — flagged again in Risks below.
4. **New Design Decision (not from a filed backlog item, surfaced during this pass) — anomaly
   effect's "bus" vs. "telemetry" subsystem mapping.** `FR-4430` says only "bus or telemetry
   subsystem," but the live `BusState` model (`engine/bus.py`) has six per-subsystem `Status` fields
   (`power`, `attitude`, `thermal`, `propulsion`, `cdh`, `comms`), no field literally named
   "telemetry." This package maps `subsystem: "telemetry"` → `bus_state.comms.status = "red"`
   (`comms` is the subsystem `command_uplink`/`telemetry_downlink` access windows key off, the
   closest existing match to "telemetry"), and `subsystem: "bus"` → `engine/bus.py::enter_safe_mode()`/
   `exit_safe_mode()` (a whole-bus anomaly, reusing the existing safe-mode/`RecoverySystem` recovery
   loop for player-visible consequences rather than inventing a new health axis — **remediated
   2026-09-27/28 per `BL-0128`: the shipped code originally set `bus_state.mode` directly instead of
   calling `enter_safe_mode()`/`exit_safe_mode()`, leaving `safe_mode.active` unset and
   `begin_recovery` unable to accept the asset; fixed to call those functions so the full safe-mode
   state is consistent**). **This subsystem mapping is this package's own interpretation, not a
   literal requirements citation** — routed to `04-requirements-engineering`/`06-feature-specification`
   as a new Low finding (see Risks) so a future baseline touch can either confirm or override it.

## Files to Modify

- `spacesim/session/manager.py` —
  - Refactor `_h_inject`'s existing per-effect-type `if/elif` body (lines 714-785) into a shared,
    reusable helper, e.g. `_apply_inject_effects(world, effects, rng)`, called by both `_h_inject`
    (time/immediate trigger path, unchanged behavior) and the new condition-check handler (below) —
    a pure refactor for the eight existing effect types, verified by re-running every existing
    inject test unchanged before adding new behavior.
  - Add four new branches to that shared dispatch: `anomaly`, `sensor_outage`,
    `forced_custody_loss`, `scripted_manoeuvre` (see System Behaviour below for each).
  - Add `_h_condition_check(world, payload, rng)`: for each `inj in self.vignette.injects` whose
    `trigger.get("type") == "condition"`, not already fired (see "Firing-state derivation" below),
    evaluate the condition (range/custody/objective-state — reusing `content/vignette.py`'s
    existing `_range_km`/`_evaluate_metric`/`world.track_for` helpers, not a new parallel
    condition-evaluation vocabulary) against the current `world`; on a true evaluation, call the
    shared effect-application helper and record `{"inject_id": inj.id, "value": <evaluated value>}`
    into a local `fired` list. After the loop, set `payload["fired"] = fired` — mutating the same
    dict object `Simulation.advance_to()` will use for its own post-handler `eventlog.append(...)`
    call, so the firing tick and evaluated condition value are recorded in the event log with no
    additional/nested `eventlog.append` call from inside the handler (avoiding the replay-time
    list-mutation hazard a mid-handler append would introduce — see Risks).
  - **Firing-state derivation (no new `WorldState` field).** "Has this non-repeatable
    condition-triggered inject already fired" is derived by scanning
    `self.sim.eventlog.entries` for a prior entry with `kind == "condition_check"`,
    `e.sim_time < world.now`, and `inj.id` present in that entry's `payload.get("fired", [])` —
    exactly the same time-filtered eventlog-scan pattern `_arm_schedule` already uses for
    time-triggered injects (lines 157-162), safe under both live-run and replay because eventlog
    entries are strictly time-ordered immutable history, never a mutable "have we processed this
    far" pointer. No new Domain Model entity or `WorldState` field, consistent with FS-106 v2.1's
    own "no new Domain Model entity" framing (this is bookkeeping derived from existing history, not
    new state).
  - `__init__`: `self.sim.register_handler("condition_check", self._h_condition_check)`.
  - `_arm_schedule`: extended to also queue periodic `"condition_check"` events at
    `BUS_TICK_PERIOD_S` cadence (mirroring `self.bus.schedule_ticks(...)`'s own call), but **only**
    when `any(inj.trigger.get("type") == "condition" for inj in self.vignette.injects)` — avoiding
    eventlog bloat for the other 18 of 19 library vignettes, which declare no condition-triggered
    injects.
- `spacesim/engine/entities.py` — `Sensor` gains `health: Literal["nominal", "degraded"] = "nominal"`
  (additive; every existing vignette's sensors have no `health` key in YAML, defaulting to
  `"nominal"` — zero behavior change for any of the 19 library vignettes).
- `spacesim/engine/orders.py` — `scene_from_world()`'s `sensors=` line (line 93) extended to exclude
  degraded sensors, mirroring the existing ground-station filter immediately above it (lines
  86-92): `sensors={i: s for i, s in world.sensors.items() if s.health != "degraded"}`.
- `spacesim/content/vignette.py` — no schema change (`Inject.trigger`/`effects` already accept
  arbitrary dict shapes); this file is cited only because `_range_km`/`_evaluate_metric` are reused
  by `_h_condition_check`'s condition evaluation, not modified.

## System Behaviour — the four new effect types

- **`anomaly`** — `{"type": "anomaly", "target": <asset_id>, "subsystem": "bus"|"telemetry",
  "cause": <str>, "restore"?: bool}`. Calls `enter_safe_mode(bus, world.now, cause)` (subsystem
  `"bus"`) — or `exit_safe_mode(bus)` when `restore` is `true` — or sets/clears
  `bus_state.comms.status = "red"`/`"green"` (subsystem `"telemetry"`) — see Design Decision 4.
  Appends a `world.messages` entry naming `eff["cause"]`
  verbatim (mirrors the existing `gs_outage` message pattern, lines 740-742) — the event log's own
  copy of `eff["cause"]` (already logged as part of `payload["effects"]`) and this message both carry
  the controller-set value with no re-derivation, satisfying `FR-4430`'s Postcondition directly.
- **`sensor_outage`** — `{"type": "sensor_outage", "target": <sensor_id>, "cause"?: <str>,
  "restore"?: bool}`. Sets `world.sensors[target].health = "degraded"` (or `"nominal"` on
  `restore`) — the new `Sensor.health` field above. `scene_from_world()`'s new filter means
  `AccessProvider` sees no `sensor_observation` endpoint for a degraded sensor, exactly mirroring how
  a degraded ground station already loses `command_uplink`/`telemetry_downlink` access.
- **`forced_custody_loss`** — `{"type": "forced_custody_loss", "cell": <owner>, "target": <object>,
  "mode": "degrade"|"drop", "degrade_to"?: float}`. `tr = world.track_for(eff["cell"],
  eff["target"])`; if `tr is None`, no-op (nothing to degrade/drop — not an error, consistent with
  Design Decision 2's "missing target ⇒ no-op" posture). `mode == "drop"`: `world.tracks.remove(tr)`.
  `mode == "degrade"`: `tr.confidence = float(eff.get("degrade_to", 0.0))` and
  `tr.last_observation = world.now` (so `Track.current_confidence()` reflects the forced value
  immediately, not a decayed value computed from the *old* `last_observation`). Only ever touches
  the named `cell`'s own `Track` entries (`world.track_for` is already cell-scoped) — never another
  cell's, satisfying `FR-4430`'s Postcondition and `ADR-0004`.
- **`scripted_manoeuvre`** — `{"type": "scripted_manoeuvre", "target": <asset_id>, "mode":
  "eci"|"lvlh"|"finite_burn"|"target_coe"|"hohmann"|"plane_change", "params": {...}}`. Looks up
  `asset = world.assets.get(eff["target"])`; if `asset is None` or `asset.orbit is None`, no-op
  (Design Decision 2's posture, generalized). Otherwise calls
  `engine.maneuver.compute_maneuver(asset.orbit, eff["mode"], eff.get("params", {}), world.now,
  self.osys.prop)` to get `dv`, then applies it via `self.osys.prop.apply_impulse(asset.orbit, dv,
  world.now)` — the same propagator call `OrderSystem._h_maneuver` already uses — **without**
  checking or deducting `asset.resources.delta_v_ms` (Design Decision 3). Records the computed `dv`/
  `cost`/resulting orbit summary in a `world.messages` entry for White-Cell visibility (mirroring
  the informational-message pattern every other new effect type above also follows).

## Implementation Tasks

1. Write a failing test asserting `_apply_inject_effects` (the refactored shared helper) produces
   identical behavior to today's `_h_inject` for all eight existing effect types, before extracting
   it — a pure refactor, regression-only at this step.
2. Add `Sensor.health` to `engine/entities.py`; write a failing test asserting a sensor with no
   `health` key in its vignette YAML defaults to `"nominal"` (regression: all 19 library vignettes'
   sensors unaffected), before adding the field.
3. Extend `scene_from_world()`'s sensor filter; write a failing test asserting a `health="degraded"`
   sensor is absent from `AccessProvider`'s `sensor_observation` endpoints, before the change.
4. Write a failing test for the `sensor_outage`/`anomaly`/`forced_custody_loss`/`scripted_manoeuvre`
   effect types individually (targeted-state assertion per System Behaviour above, including the
   negative assertion that `forced_custody_loss` never touches a non-targeted cell's own `Track`),
   before adding each branch to the shared effect-application helper.
5. Write a failing test asserting `compute_maneuver()` + `apply_impulse()` change `asset.orbit` as
   expected for at least two of the six entry modes (`eci`, `hohmann`) without touching
   `asset.resources.delta_v_ms`, before wiring `scripted_manoeuvre`.
6. Write a failing test asserting a condition-triggered inject (e.g. a range-threshold condition
   between two named assets) fires at the first `condition_check` tick where the condition evaluates
   true, and records `payload["fired"]` on that tick's event-log entry, before adding
   `_h_condition_check`/the `_arm_schedule` extension.
7. Write a failing test asserting the SAME condition-triggered inject fires at the identical
   simulated tick on a replay of the same `(initial_state, eventlog, seed)` — `FS-106` v2.1's own
   Acceptance Criterion — before considering the feature complete.
8. Write a failing test asserting a vignette with **no** condition-triggered injects schedules zero
   `condition_check` events (the eventlog-bloat guard), before adding that conditional.
9. Write a failing test asserting a condition-triggered inject whose named asset/track/cell does not
   exist simply never fires (Design Decision 2) — no exception, no special log entry.
10. Re-run the full existing suite, in particular `test_inject_library.py` (the `IP-1061` regression
    suite this package's own refactor must not disturb) and the determinism/import-guard permanent
    gates.

## Tests to Add

- `spacesim/tests/test_content.py` or a new `spacesim/tests/test_inject_effects_v2.py` — the four
  new effect types (targeted-state assertions + the `forced_custody_loss` negative assertion), the
  `Sensor.health` default/filter regression, and the `scripted_manoeuvre` Δv-bypass assertion.
- `spacesim/tests/test_condition_triggered_injects.py` *(new)* — condition evaluation (range/
  custody/objective-state), fire-once (non-repeatable) semantics, the deleted-target no-op case, the
  zero-`condition_check`-events-when-unused guard, and the replay-determinism assertion (Task 7).
- `spacesim/tests/test_inject_library.py` — existing suite re-run unchanged (Task 1's refactor
  regression).

The two permanent gates (`spacesim/tests/test_determinism.py`, `spacesim/tests/test_import_guard.py`)
must be re-run green — no engine-layer file gains a wall-clock read or global RNG use, and the new
`_h_condition_check`/effect branches are session-layer code exactly like every existing inject
handler.

## Documentation Updates

- `CLAUDE.md` Code Map — `engine/entities.py`'s entry gains the `Sensor.health` addition;
  `engine/orders.py`'s entry gains the `scene_from_world()` sensor-filter note; `session/manager.py`'s
  description gains the condition-triggered-inject + four-new-effect-types note.
- `docs/requirements/03-requirements-traceability-matrix.md` — `FR-4420`/`FR-4430` rows'
  `Implementation Package` cell updated from `UNASSIGNED` to `IP-1062`; `Test` cell updated once the
  named test files exist.
- `docs/features/FS-106-white-cell-dashboard.md` — `Referenced By` metadata gains this package's
  link (metadata cross-link only). Its three Open-Question entries tied to `BL-0091`/`BL-0095`
  are not struck out by this package directly (that edit belongs to `06-feature-specification`),
  but this package's Design Decisions section gives `06` everything needed to close them.
- `docs/pipeline/backlog.md` — `BL-0091`/`BL-0095` updated: both fully resolved by this package's
  Design Decisions 1-3; recommend flipping both to `DONE` at the next `00-pipeline-manager` harvest.
  A new Low finding is recommended for the anomaly subsystem-mapping interpretation (Design
  Decision 4), routed to `04`/`06`.

## Definition of Done

- [x] **Explicit user authorization obtained** for this package's Implementation Tasks (MSTR-006
  §3) — granted 2026-09-27 by the project owner's direct instruction.
- [x] A condition-triggered inject (range/custody/objective-state) fires at the first scheduled
  engine tick where its condition evaluates true, and never fires before that.
  (`test_condition_inject_fires_at_first_true_tick_and_records_fired_payload`)
- [x] The same condition-triggered inject fires at the identical simulated tick under replay of the
  same `(initial_state, eventlog, seed)`. (`test_condition_inject_fires_at_identical_tick_under_replay`)
- [x] A vignette with no condition-triggered injects schedules zero `condition_check` events.
  (`test_vignette_with_no_condition_injects_schedules_zero_condition_check_events`)
- [x] Each of the four new effect types produces the state change described in System Behaviour;
  `forced_custody_loss` never changes a non-targeted cell's own `Track`.
  (`test_inject_effects_v2.py` — one test per effect type/branch, plus
  `test_forced_custody_loss_never_touches_another_cells_track`)
- [x] `scripted_manoeuvre` changes `asset.orbit` via the named entry mode without touching
  `asset.resources.delta_v_ms`. (`test_scripted_manoeuvre_changes_orbit_via_eci_mode_bypassing_delta_v_budget`,
  `test_scripted_manoeuvre_changes_orbit_via_hohmann_mode`)
- [x] A degraded sensor is absent from `AccessProvider`'s `sensor_observation` endpoints; restoring
  it makes it reappear. (`test_scene_from_world_excludes_degraded_sensor`)
- [x] Every existing inject-library/effect test still passes unchanged (the `_h_inject` refactor is
  behavior-preserving for all eight prior effect types) — `test_inject_library.py`'s full suite
  re-run with zero changes needed beyond the `_KNOWN_EFFECT_TYPES` documentation set.
- [x] Full existing test suite green, zero regressions, both permanent gates green: **678
  passed / 3 skipped** (up from 661/3), `test_determinism.py` and `test_import_guard.py` both
  green.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] `test_condition_triggered_injects.py` and the new effect-type tests exist and are green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green.
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green.
- [ ] Full existing suite re-run with zero regressions, in particular `test_inject_library.py`
  (the `IP-1061` A1/A3 fixes this package's refactor must not disturb).
- [ ] Independently confirm, by reading the shipped code, that `_h_condition_check`'s firing-state
  check filters by `e.sim_time < world.now` (not by list length/position) — the specific property
  that makes it replay-safe.
- [ ] Independently confirm the `scripted_manoeuvre` effect genuinely bypasses
  `asset.resources.delta_v_ms` (does not read or write it) by reading the code directly, not merely
  re-citing this package's own claim.
- [ ] Independently round-trip at least one condition-triggered inject through a rewind/replay and
  confirm it fires at the same tick both times.

## Dependencies

- **Upstream:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.1 (approved,
  `✅ Ready for implementation planning`), `engine/maneuver.py`'s six entry modes (baseline code,
  unmodified — only called, not changed), `engine/custody.py`'s `Track` model (unmodified),
  `engine/orders.py::scene_from_world()`'s existing ground-station-outage filter (the precedent this
  package's sensor filter mirrors).
- **Downstream:** none identified — this package's condition-trigger mechanism and new effect types
  are consumed only by White-Cell-authored vignette/inject-library content, not by any other queued
  Must-tier package.
- **Build-sequencing:** Independent of the other four remaining Must-tier packages (`FS-120`,
  `FS-119`, `FS-121`/`FS-103` v1.1) and of [IP-1180](IP-1180-external-vignette-directories.md)
  (different files, no shared seam).

## Risks

- **Mid-handler eventlog mutation would be a replay hazard if done wrong (see Files to Modify).**
  This package deliberately avoids having `_h_condition_check` call `eventlog.append()` directly
  (which would corrupt `Simulation._rebuild()`/`replay()`'s iteration over a list being appended to
  mid-loop) — instead it mutates the already-scheduled event's own `payload` dict in place, which
  `advance_to()`'s existing post-handler append captures naturally. `08-code-implementation` must
  preserve this exact mechanism, not "simplify" it into a direct append.
- **Anomaly subsystem-mapping is this package's own interpretation (Design Decision 4), not a
  literal requirements citation.** If `04-requirements-engineering`/`06-feature-specification`
  later disagrees with the `comms`/`safe_mode` mapping chosen here, the effect's payload shape
  (`subsystem: "bus"|"telemetry"`) stays stable — only the internal `BusState` field touched would
  need to change, a small, isolated fix.
- **Refactoring `_h_inject` into a shared helper touches code `IP-1061` (COMPLETE, same-day prior
  package) just modified.** The refactor must be verified behavior-preserving for all eight existing
  effect types (Implementation Task 1) before any new branch is added, to avoid silently
  reintroducing or masking `IP-1061`'s A1/A3 fixes.
- **`scripted_manoeuvre`'s Δv bypass (Design Decision 3) is a genuine behavior choice, not merely an
  implementation convenience** — a facilitator using this effect gets an "infinite budget" manoeuvre
  tool. This is consistent with `ADR-0005` but is worth a White-Cell-facing UI note (out of this
  package's scope; a candidate follow-on for whichever package builds the inject-authoring UI for
  this effect type).

## Rollback Considerations

The condition-check mechanism and four new effect types are additive: reverting `_arm_schedule`'s
extension and removing the four new dispatch branches (plus the `Sensor.health` field and its
`scene_from_world()` filter) fully removes this package's capability with no effect on any existing
vignette or inject-library template, since every one of the 19 library vignettes' injects use only
the eight effect types and the `time`-typed trigger this package leaves unchanged. No data-migration
concern: a vignette file authored with a condition trigger or a new effect type simply becomes
inert (its inject never fires / its effect type is unrecognized) after rollback — not a crash, since
the existing `_h_inject` dispatch already silently ignores an unrecognized `eff.get("type")` (no
`else` branch raises).
