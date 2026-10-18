# IP-1230 — Space-Weather-Index Coupling: Index-Driven LEO Drag and Environmental-Anomaly Rate (FR-1230, FR-4440)

> **Package ID:** IP-1230
> **Version:** 1.0
> **Status:** 🔵 COMPLETE — 2026-10-18, `08-code-implementation`, pipeline run #189, awaiting a
> **fresh-session** `09-package-verification`. 46 tests in `test_space_weather_index.py`; **42 seen failing first** on a pre-fix copy of the tree. 4 passed on arrival: the opt-out pins, the qualifying-asset pin, and the no-op replay. Full suite **1071 passed / 3 skipped** (baseline 1025/3, plus 46); gates 14/14. Deviations, disclosed: (1) Design Decision 8's validator is a pydantic `field_validator` rather than a `model_validator`, so a load refusal names `…ballistic_coeff_m2_kg`. (2) `index_series_problems` takes a `time_required` keyword, because an inject's `offset_s` defaults to 0 (Design Decision 2). (3) FS-123's `Referenced By` was not edited; `08` does not edit specs, so that is left for `09`, per the run #182 precedent.
> *(Was 🟡 IN PROGRESS — 2026-10-18, pipeline run #189.)*
> *(Was 🟢 READY. Authored 2026-10-18 by `07-implementation-planning` in pipeline run #188.)*
> Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** this package falls under the project owner's standing
> pre-authorization of 2026-10-11 for the packages this pipeline iteration reaches. The owner's
> 2026-10-18 instruction extended it explicitly to whatever packages the stalled original batch
> `BL-0068`–`BL-0083` reaches, and this package is `BL-0074`'s (item B8). Authoring the package is
> not itself the authorization; those standing decisions are.
> **Dependencies:** [FS-123](../../features/FS-123-space-weather-index-coupling.md) v1.1 (the
> spec) and [ADR-0039](../../architecture/adr/ADR-0039-space-weather-index-to-multiplier-mapping.md)
> (the mapping and the application model). Two packages are `VERIFIED` dependencies:
> [IP-1062](IP-1062-condition-triggered-injects-and-new-effects.md) (the `anomaly` effect) and
> [IP-1063](IP-1063-inject-effect-fire-time-validation.md) (inject boundary validation). Three
> more are `VERIFIED` and are reused unchanged:
> [IP-1310](IP-1310-load-time-vignette-validation.md) (the `validate_vignette` gate),
> [IP-1064](IP-1064-condition-inject-follow-ups.md) (the start-anchored tick grid) and
> [IP-1021](IP-1021-failure-atomic-event-application.md) (failure-atomic handlers).
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0074`
> **Produces:** a declared F10.7/Kp index series that, when a vignette opts in, decays LEO orbits
> and raises the rate of environmental anomalies, deterministically.
> **Feature Reference:** [FS-123 — Space-Weather-Index-Driven Drag and Anomaly-Rate Coupling](../../features/FS-123-space-weather-index-coupling.md)
> v1.1 (`FEAT-1200` `FR-1230`; `FEAT-4400` `FR-4440`)
> **Related Topics:** [`R131`](../../research/encyclopedia/R131-space-environment-and-space-weather-operations.md)
> v1.2, [`spacesim/engine/perturbations.py`](../../../spacesim/engine/perturbations.py),
> [`spacesim/engine/busmodel.py`](../../../spacesim/engine/busmodel.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package. `IP-1230` has been reserved for FS-123 since run #78.*

---

## Package ID

IP-1230 (FS-123 → `IP-1230`, per the FS-1xx → `IP-1xx0` convention).

## Objective

**As built at `a25caf4`** (read this run):

- `engine/perturbations.py::secular_drag_decay()` (line 161) exists, but nothing calls it.
- `world.space_weather` holds only `{"severity": ...}`. The `space_weather` inject branch of
  `SessionManager._apply_inject_effects` (`session/manager.py`, line 1086) **replaces** the whole
  dict, and defaults a missing `severity` to `"minor"`.
- `Asset` (`engine/entities.py`) has no ballistic coefficient.
- No environmental-anomaly source exists.

After this package, all of the following hold, each opt-in:

| Case | Before | After |
|---|---|---|
| A vignette with none of the new fields (all 19 shipped vignettes) | — | **Byte-identical** final world and event log |
| Opted-in LEO `kepler` asset (has `ballistic_coeff_m2_kg`), with a series declared | No decay | Semi-major axis decreases each 300 s `bus_tick` by `secular_drag_decay(alt, BC, 300) × f_solar × f_geo` |
| The same asset, with no series declared | No decay | No decay (no series in effect) |
| TLE, GEO/MEO, or a LEO asset without a ballistic coefficient | No decay | No decay |
| `environmental_anomalies` block declared | — | Each anchored tick, each listed asset fires the `anomaly` effect with probability `1 − exp(−rate × f_geo(Kp) × dt_days)` |
| A Kp outside [0, 9], or an F10.7 ≤ 0, in the vignette | Not applicable | `VignetteValidationError` naming the field |
| The same values in a White inject | Not applicable | 400 at the boundary, nothing changes |

## Feature Reference

[FS-123](../../features/FS-123-space-weather-index-coupling.md) v1.1 is covered in full: System
Behaviour, Data Model Changes, Error Handling, and Acceptance Criteria 1–6. The design basis is
ADR-0039 decisions 1–8.

## Requirements Covered

| ID | How |
|---|---|
| `FR-1230` | Index-driven drag on qualifying assets on the `bus_tick` grid. Pure functions in `perturbations.py`; the application step in `busmodel.py`. |
| `FR-4440` | A session-owned `env_anomaly_check` tick that scales the authored base rate by `f_geo` and fires the existing `anomaly` effect. |

This matches FS-123's Requirements Implemented exactly. `FR-5310` (load validation) and
`FR-4410`/`FR-4430` (the inject boundary) are extended, not newly covered.

## Architecture Components

- **C1 Simulation Engine:**
  - `engine/perturbations.py`: new pure functions.
  - `engine/busmodel.py`: the drag step inside `_h_tick`, and a `tick_period_s` constructor
    argument.
  - `engine/entities.py`: the new `Asset` field.
- **C2 Session Layer** (`session/manager.py`): inject validation and application of the series,
  plus the environmental-anomaly tick.
- **C3 Content** (`content/vignette.py`): two new optional vignette fields, their load-time
  validation, and the conversion in `build_world`.

The engine import boundary is unchanged: the engine imports nothing from session or content. No
new module, no UI and no API endpoint.

## Interfaces

- **INT-0008** (SessionManager → engine): new `env_anomaly_check` event kind, scheduled only for
  opted-in vignettes. `bus_tick` keeps its shape (empty payload).
- **INT-0016** (White inject → engine): the `space_weather` effect gains an optional
  `index_series` list.

### Design Decisions

1. **Stored form.**
   - `world.space_weather["index_series"]` is a list of `{"t": <sim micros>, "f107"?: float,
     "kp"?: float}`, sorted by `t`.
   - It is present only when declared. A world with no series has no `index_series` key, so the
     dumps of all 19 shipped vignettes are unchanged.
2. **Authoring forms.**
   - **Vignette:** a new optional `space_weather_series: list[dict]`, with entries
     `{at_sim_s: number ≥ 0, f107?, kp?}`. `build_world` converts each to the stored form
     (`t = start + at_sim_s·10⁶`).
   - **Save-as-scenario:** `initial_space_weather` may already carry a stored-form `index_series`
     (via `vignette_export.py`'s `dict(world.space_weather)`), and it loads verbatim, as today.
   - **Inject:** `{"type": "space_weather", "index_series": [{offset_s: number ≥ 0 (default 0),
     f107?, kp?}], "severity"?: ...}`. Offsets are relative to the inject's fire time. Applying
     the inject:
     1. converts the entries to the stored form;
     2. **drops existing stored entries with `t` ≥ the earliest new `t`**;
     3. appends the new entries and keeps the list sorted.
3. **Severity handling in the inject branch.** The branch updates keys instead of replacing the
   dict:
   - It sets `world.space_weather["severity"]` only when the effect carries `severity`, or when it
     carries neither `severity` nor `index_series`. The second case keeps today's `"minor"`
     default byte-for-byte.
   - A series-only inject leaves severity untouched.
   - `index_series` is preserved when a severity-only inject fires.
   - Behaviour for every existing inject is identical. Today's dict only ever holds `severity`, so
     setting the key and replacing the dict produce the same dump.
4. **Pure functions in `engine/perturbations.py`.** No clock, no RNG:
   - `f_solar(f107)` and `f_geo(kp)` use ADR-0039's anchor tables. Linear interpolation between
     anchors; F10.7 is clamped to [50, 300] before interpolating; Kp in [0, 4] maps to 1.0.
   - `index_in_effect(series, t, key)` returns the latest entry with `t_entry ≤ t` that carries
     `key`, or `None`.
   - `drag_multiplier(series, t)` is `f_solar(…) × f_geo(…)`, with a factor of 1.0 for an index
     that is `None`.
   - `anomaly_rate_multiplier(series, t)` is `f_geo(…)` only.
   - `index_series_problems(entries, time_key)` returns a `list[str]`. It refuses a non-dict
     entry, a missing or non-numeric or negative time key, an entry with neither index, a
     non-numeric, non-finite or out-of-[0, 9] `kp`, and a non-numeric, non-finite or ≤ 0 `f107`.
     `bool` is not accepted as a number. This single validator is shared by the load and inject
     paths.
5. **Drag step**, in `BusSystem._h_tick`, after the existing bus loop:
   - If `world.space_weather` has no `index_series`, return at once: no state change and no
     RNG.
   - Otherwise, for each asset in `world.assets` order that has `orbit.source == "kepler"`,
     `orbit.regime in ("LEO", "LEO_SSO")` and `ballistic_coeff_m2_kg` > 0, with
     `M = drag_multiplier(series, world.now)`:
     1. take `r, v = prop.rv(orbit, now)`, `a = |r|` and `alt = a − R_EARTH_EQ`;
     2. compute `Δa = −secular_drag_decay(alt, BC, tick_period_s) × M` (secular_drag_decay
        returns a negative value);
     3. if `Δa > 0`, apply the equivalent retrograde along-track Δv
        `dv = MU_EARTH·Δa / (2·a²·|v|)` with
        `orbit = prop.apply_impulse(orbit, −dv·v̂, now)`.
   - `apply_impulse` re-epochs through `rv_to_elements`, so position is continuous at the tick.
     This is the same seam `_h_maneuver` and `scripted_manoeuvre` already use.
   - `tick_period_s` is a new `BusSystem.__init__` keyword argument, default `300.0`.
     `SessionManager` passes `BUS_TICK_PERIOD_S`. This is a construction-time constant, so replay
     and rewind use the same dt.
   - No `delta_v_ms` is charged, because this is environment, not a manoeuvre.
6. **Environmental anomalies**, `session/manager.py`:
   - A new handler, `_h_env_anomaly_check`, registered beside `condition_check`.
   - `_arm_schedule` queues `env_anomaly_check` on the same start-anchored grid
     (`anchor + k·step`, mirroring the condition-check loop) **only when
     `vignette.environmental_anomalies` is set**.
   - The handler iterates `block["assets"]` in declared order and draws one `rng.random()` per
     listed asset per tick, unconditionally, so the RNG stream does not depend on world state.
     With `dt_days = BUS_TICK_PERIOD_S / 86400`, it fires if
     `draw < 1 − exp(−base_rate_per_day × anomaly_rate_multiplier(series, now) × dt_days)`.
   - Firing is skipped when the asset no longer exists, has no `bus_state`, or, for `subsystem:
     bus`, is already in safe mode (no re-entry). A fired anomaly applies
     `{"type": "anomaly", "target": id, "subsystem": block.subsystem, "cause": block.cause}`
     through `_apply_inject_effects` (existing path, message included).
   - The handler records `payload["fired"] = [{"asset": id, "p": p}, ...]`, using the same
     in-place payload pattern as `_h_condition_check`, so AAR shows each firing.
7. **Vignette `environmental_anomalies`** (optional dict). It holds:
   - `base_rate_per_day`: a number ≥ 0 (required);
   - `assets`: a non-empty list of declared asset ids (required);
   - `subsystem`: `"bus"` or `"telemetry"`, default `"bus"`;
   - `cause`: a string, default `"space_weather"`.

   `validate_vignette` refuses a missing or invalid field, an unknown asset id, or an asset with no
   bus.
8. **Asset field:** `ballistic_coeff_m2_kg: Optional[float] = None`. A `model_validator` refuses a
   value ≤ 0, or a non-finite one, so `validate_vignette`'s existing `Asset.model_validate` call
   reports it as `blue_forces[<id>].…`. No default (ADR-0039 decision 7).
9. **Boundary validation:**
   - `_inject_effect_problem`'s `space_weather` case returns the first
     `index_series_problems(effect["index_series"], "offset_s")` string, or
     `"index_series must be a list"` when the value is not a list.
   - The fire path (`fire_inject` → `validate_inject_effects`) therefore rejects the inject (400
     through the existing route), and the handler path skips it (IP-1063).
   - `validate_vignette` runs `index_series_problems` on `space_weather_series` (`at_sim_s`) and on
     `initial_space_weather.index_series` (`t`).
10. **Determinism.**
    - Every input is declared data, sim time, or the handler's seeded `rng`.
    - Without opt-in there are no new events, no RNG draws and no state change.
    - The determinism property test and the replay tests stay green.

## Files to Create

- `spacesim/tests/test_space_weather_index.py`: every test below.

## Files to Modify

Each file was checked against the tree at `a25caf4`:

- `spacesim/engine/perturbations.py`: add the Design Decision 4 functions after
  `secular_drag_decay` (line 161). No existing function changes.
- `spacesim/engine/busmodel.py`: `BusSystem.__init__` (line 24) gains `tick_period_s`, and
  `_h_tick` (line 55) gains the drag step after its loop. Import `MU_EARTH`/`R_EARTH_EQ` from
  `engine/orbit.py` and the new functions from `perturbations.py`.
- `spacesim/engine/entities.py`: `Asset` (line 24) gains `ballistic_coeff_m2_kg` plus a validator.
  The module already imports `model_validator`.
- `spacesim/content/vignette.py`:
  - `Vignette` (line 111) gains `space_weather_series: list[dict] = []` and
    `environmental_anomalies: Optional[dict] = None`.
  - `validate_vignette` (line 349) gains the checks from Design Decisions 7 and 9.
  - `build_world` (line 446) converts `space_weather_series` into `world.space_weather` **after**
    the existing `initial_space_weather` assignment, merging rather than replacing, and keeping
    any `severity`.
- `spacesim/session/manager.py`:
  - `_inject_effect_problem` (line 55) gains the `space_weather` case.
  - `__init__` (line 152, `BusSystem(self.sim)`) passes `tick_period_s=BUS_TICK_PERIOD_S` and
    registers `env_anomaly_check`.
  - `_arm_schedule` (line 240) gains the gated anomaly-tick loop.
  - The `space_weather` branch (line 1086) follows Design Decisions 2–3.
  - Add the new `_h_env_anomaly_check`.
- `CLAUDE.md` (code map): one clause each on `perturbations.py` and `busmodel.py` (index-driven
  drag), `vignette.py` (the two new fields) and `manager.py` (`env_anomaly_check`).

No UI or API file changes. `vignette_export.py` needs no change: `Asset.model_dump` carries the
new field, and `initial_space_weather` already copies the whole dict.

## Implementation Tasks

1. Mark the package `IN PROGRESS` (header, MBP row, `packages/INDEX.md`, ROADMAP) before editing.
2. Write the tests below, and see each behaviour test fail first against `a25caf4`. Tests 10 and
   11 (opt-out byte-identity) are expected to pass on arrival: they pin behaviour that must not
   change.
3. Implement Design Decisions 1–10.
4. Run the full suite plus `test_determinism.py` and `test_import_guard.py`, all green.
5. Ledgers:
   - RTM `FR-1230`/`FR-4440` rows (FS-123, tests, `IP-1230`);
   - FS-123 `Referenced By` (`IP-1230`, completed);
   - MBP, `packages/INDEX.md` and ROADMAP → `COMPLETE`;
   - the `CLAUDE.md` code map.
   Manual impact is routed through §15.1 to `08-training-manual-authoring` after `VERIFIED`.

## Tests to Add

All in `spacesim/tests/test_space_weather_index.py`:

1. **Mapping anchors** (`FS-123` AC 2):
   - `f_solar`: 50 → 0.3, 150 → 1.0, 300 → 3.0, 40 → 0.3 (clamped), 400 → 3.0, 100 → 0.65.
   - `f_geo`: 0, 2 and 4 → 1.0; 5 → 2.0; 7 → 6.0; 9 → 10.0.
   - `drag_multiplier` at (150, 7) → 6.0 and at (300, 9) → 30.0.
   - `anomaly_rate_multiplier` ignores `f107`.
2. **Step-held lookup:** before the first entry an index is `None` (factor 1.0); each index holds
   independently (an entry carrying only `kp` leaves the last `f107` in effect).
3. **Validator** (`index_series_problems`): accepts a valid series, and refuses Kp −1, Kp 9.5,
   Kp `NaN`, F10.7 0, F10.7 −5, a `bool`, an entry with neither index, and a missing or negative
   time key.
4. **Drag responds** (AC 1): two sessions on one LEO `kepler` asset (~400 km, BC 0.02). One has a
   quiescent series (F10.7 70, Kp 1) and the other an active one (F10.7 250, Kp 7), advanced
   6 h. The active run's semi-major axis is lower, and both are below the start value.
5. **Drag replays:** for each run in test 4, `sim.replay()` reproduces `world.model_dump()`
   exactly.
6. **Qualifying assets only** (AC 6): with a series declared, a TLE asset, a GEO `kepler` asset
   with a BC, and a LEO asset without a BC are each unchanged (their orbit dump equals a no-series
   control).
7. **Anomaly rate responds** (AC 3): the same `environmental_anomalies` block (high base rate,
   for example 20/day, with `subsystem: telemetry` so assets stay eligible) and the same seed, with
   Kp 1 versus Kp 8, over 24 h. Kp 8 fires more often (summed over the `env_anomaly_check`
   payloads).
8. **Anomaly replay:** firing times and assets are identical on `replay()`.
9. **Refusal at load** (AC 5): Kp 12 in `space_weather_series`, F10.7 −5, BC 0, and an
   `environmental_anomalies` block naming an unknown asset. Each raises
   `VignetteValidationError`, and its `problems` name the field.
10. **Refusal at the inject boundary** (AC 5): `fire_inject` with a `space_weather` effect whose
    `index_series` holds Kp 12 is rejected (the existing rejection path); the world is unchanged
    and nothing is scheduled. Also over HTTP: `POST /api/sessions/{sid}/inject` returns 400.
11. **Opt-out byte-identity** (AC 4): a shipped vignette (for example `leo-isr-denial`), seed
    fixed, advanced 2 h. The final `world.model_dump()` has no `index_series` key and no
    `env_anomaly_check` events, and the event-log kinds and count match a run in which the
    vignette carries an empty `space_weather_series` and no BCs.
12. **Severity untouched by a series inject; series kept by a severity inject**, per Design
    Decision 3. A severity-only inject still yields `{"severity": ...}` exactly when no series is
    present.

## Documentation Updates

- RTM rows for `FR-1230` and `FR-4440`.
- FS-123 `Referenced By`.
- The `CLAUDE.md` code map.
- MBP, `packages/INDEX.md` and ROADMAP status.

No training-manual prose in this package; it routes via §15.1 after `VERIFIED`.

## Definition of Done

- [ ] All Design Decisions 1–10 implemented.
- [ ] Every test above added; the behaviour tests were seen failing first.
- [ ] The full suite is green, and `test_determinism.py` and `test_import_guard.py` are green.
- [ ] No shipped vignette's behaviour changes (test 11, plus the existing tutorial and replay
  tests).
- [ ] Ledgers updated and the package `COMPLETE`.

## Verification Checklist

- [ ] `perturbations.py`'s anchor tables match ADR-0039 decisions 2 and 3 exactly.
- [ ] The drag step returns early with no series, and charges no `delta_v_ms`.
- [ ] `env_anomaly_check` is scheduled only when `environmental_anomalies` is set. One draw per
  listed asset per tick, always.
- [ ] Load and inject refusal go through the single shared `index_series_problems`.
- [ ] A series-only inject leaves severity untouched, and a severity-only inject keeps the series.
- [ ] Replay is byte-identical for an opted-in run (drag and anomaly).
- [ ] `test_determinism.py` and `test_import_guard.py` are green, and the full suite count is
  reported.

## Dependencies

All `VERIFIED`: `IP-1062`, `IP-1063`, `IP-1310`, `IP-1064`, `IP-1021`. No package depends on
`IP-1230`.

## Risks

- **RNG-stream leakage.** A draw made when the block is absent would shift every shipped
  vignette's RNG stream. Guard by scheduling the tick only when the block is declared; test 11
  pins this.
- **`apply_impulse` regime drift.** `rv_to_elements` recomputes `regime`. An asset decaying below
  the LEO band stays `LEO`, which is fine. An unrealistically large BC could decay an orbit into
  the atmosphere. Accepted at moderate fidelity; no re-entry model is in scope.
- **Secular-formula validity.** `secular_drag_decay` assumes a near-circular orbit, which is
  acceptable for LEO (ADR-0039 Alternatives).
- **The inject dict update (Design Decision 3)** must keep the existing `test_inject_*` and
  `IP-1061` severity tests green.

## Rollback Considerations

The change is additive and opt-in. Reverting the commit restores today's behaviour, and no shipped
vignette or save depends on the new fields. After a revert, a vignette authored with the new
fields still loads, because pydantic's default `extra="ignore"` drops the unknown fields
silently, but its series and anomalies no longer have any effect. That is acceptable for a
training tool.
