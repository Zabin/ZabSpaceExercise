> **Document ID:** FS-123
> **Version:** 1.1
> **Status:** ✅ Done (built by `IP-1230`, `VERIFIED`). Both v1.0 Open Questions are closed by
> [ADR-0039](../architecture/adr/ADR-0039-space-weather-index-to-multiplier-mapping.md).
> **Note on this repository's chain:** the approved Feature inputs are the Feature Catalog's
> `FEAT-1200` (Included Requirements: `FR-1230`) and `FEAT-4400` (Included Requirements:
> `FR-4440`) in `docs/feature-planning/03-feature-catalog.md`. This spec covers both leaves
> because they share one index series. The other inputs are
> `docs/requirements/01-functional-requirements.md` `FR-1230`/`FR-4440`;
> [`R131` v1.2](../research/encyclopedia/R131-space-environment-and-space-weather-operations.md)
> §3/§5; ADR-0039; and the baseline code they extend (`spacesim/engine/perturbations.py`,
> `engine/propagator.py`, `engine/busmodel.py`, `session/manager.py`, `content/vignette.py`).
> **Dependencies:** [FS-106](FS-106-white-cell-dashboard.md) v2.1, for the existing
> `space_weather` inject effect and its `severity` field, which this Feature adds to rather than
> replaces, and for the `anomaly` effect type (`FR-4430`).
> **Referenced By:** [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0074` (item B8),
> `BL-0104`, `BL-0121`;
> [docs/requirements/01-functional-requirements.md](../requirements/01-functional-requirements.md)
> `FR-1230`, `FR-4440`; [ADR-0039](../architecture/adr/ADR-0039-space-weather-index-to-multiplier-mapping.md);
> [IP-1230](../implementation/packages/IP-1230-space-weather-index-coupling.md) (✅ VERIFIED
> 2026-10-18, [VR-1230](../implementation/verification/VR-1230-space-weather-index-coupling.md)).
> **Produces:** a deterministic coupling from a declared space-weather index time series into LEO
> drag decay (`FR-1230`) and into the rate of environment-induced anomalies (`FR-4440`).
> **Feature Mapping:** FS-123 (this document); `FEAT-1200` (`FR-1230`), `FEAT-4400` (`FR-4440`).
> **Related Topics:** [FS-122](FS-122-sensor-modality-models.md) (an unrelated capability in the
> same release increment); [FS-131](FS-131-load-time-vignette-validation.md) (the load-time
> validation gate this Feature's refusal rules extend).

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template.*

*v1.1 changelog (2026-10-18): Open Question 1 (the mapping) and Open Question 2 (out-of-range
values) are closed by ADR-0039, which was grounded on R131 v1.2. This revision updates Scope,
User Workflows, System Behaviour, Data Model Changes, Error Handling, Acceptance Criteria and
Verification Plan to state what ADR-0039 commits to. Purpose and Requirements Implemented are
unchanged.*

# FS-123 — Space-Weather-Index-Driven Drag and Anomaly-Rate Coupling

## Purpose

This Feature couples a declared space-weather index time series (F10.7 solar flux and the Kp
geomagnetic index) into two consequences that are unwired today:

- `engine/perturbations.py`'s `secular_drag_decay()` exists, but the runtime propagator never
  calls it (`FR-1230`'s Rationale; `docs/FUTURE-WORK.md` §2, §13 R12, GAP-01).
- Environment-induced anomalies have no rate at all (`FR-4440`).

Both couplings must stay deterministic. The index values are declared at declared simulated times
and are never read from a wall clock or an outside service (`CLAUDE.md` invariant 1; `ADR-0002`).

## Scope

**In scope:**

- Accepting an index time series as vignette data or as a `space_weather` inject payload
  (`FR-1230`'s Inputs).
- Scaling LEO drag decay from that series through `engine/perturbations.py` (`FR-1230`).
- Scaling the firing rate of environment-induced `anomaly` effects from the same series
  (`FR-4440`).
- The exact mapping, the refusal rules and the application model ADR-0039 fixes.

**Out of scope (named, not silently absorbed):**

- The existing `severity`-driven eclipse-drain and telemetry scaling. That is FS-106 v2.1's scope
  and is unchanged.
- Drag on TLE-backed assets. sgp4 carries its own drag term (ADR-0039 decision 7).
- Numerical (non-secular) drag integration. That belongs to the `HighFidelityPropagator` seam
  (FUTURE-WORK §2).
- Any operator-facing UI for authoring or plotting the series. No requirement asks for one.

## Requirements Implemented

- `FR-1230`: space-weather-index-driven LEO drag coupling.
- `FR-4440`: space-weather-index-driven anomaly rate scaling.

## User Workflows

1. **White Cell declares an index series.** The series is either authored in the vignette or
   carried by a `space_weather` inject that White Cell fires immediately or schedules. Each entry
   names a simulated time and an `f107` value, a `kp` value, or both. The series becomes part of
   the deterministic input state, the same way the existing `severity` field is today.
2. **The author opts assets into drag.** A vignette author gives an asset a ballistic coefficient
   (Cd·A/m). Only an asset with one can experience index-driven drag (ADR-0039 decision 7).
3. **The author opts into environmental anomalies.** A vignette author declares an
   environmental-anomaly block with a base rate per asset per day, the eligible assets, and the
   `anomaly` effect's `subsystem` and `cause` (ADR-0039 decision 8).
4. **The simulation advances.** On each tick of the existing start-anchored 300 s grid:
   - each opted-in LEO asset loses semi-major axis at the scaled rate;
   - each eligible asset may draw an environmental anomaly at the scaled rate.
5. **Facilitator or analyst replays.** Replaying the identical
   `(initial_state, ordered eventlog, seed)` reproduces byte-identical orbits and the identical
   anomaly firing sequence (`FR-1120`; `ADR-0002`).

## System Behaviour

- **Index in effect.** Each index is a step function: its value holds from its entry until that
  index's next entry. Before an index's first entry, or with no series declared, that index's
  factor is 1.0 (ADR-0039 decision 1).
- **Mapping (ADR-0039 decisions 2–5).**
  - `f_solar` is piecewise-linear through F10.7 = 50 / 150 / 300 sfu, giving 0.3 / 1.0 / 3.0. A
    positive F10.7 below 50 or above 300 is clamped to the end value.
  - `f_geo` is piecewise-linear through Kp = 0 / 4 / 5 / 9, giving 1.0 / 1.0 / 2.0 / 10.0.
  - The drag multiplier is `f_solar × f_geo`. The anomaly-rate multiplier is `f_geo` alone.
- **Normal path, `FR-1230`.** On each tick, an asset qualifies when it has all three of:
  - a `kepler`-source orbit in regime `LEO` or `LEO_SSO`;
  - an authored ballistic coefficient greater than 0;
  - a declared series.

  For a qualifying asset, the semi-major axis decreases by `secular_drag_decay(altitude, BC, dt)`
  × the drag multiplier, using the index values in effect at the tick's start. The update is
  re-epoched at the tick, so the asset's position is continuous at that instant. A higher-flux or
  higher-Kp series therefore decays faster.
- **Normal path, `FR-4440`.** On each tick, each eligible asset with a bus fires an anomaly with
  probability `1 − exp(−base_rate × f_geo × dt_days)`, drawn from the seeded RNG. A firing
  applies the existing `anomaly` effect unchanged, including safe-mode entry for
  `subsystem: bus`.
- **Edge cases.**
  - No series declared: no drag change, and anomalies fire at the base rate unscaled.
  - No anomaly block declared: no anomaly tick is scheduled at all.
  - Neither declared: behaviour is byte-identical to today for all 19 shipped vignettes, with no
    new event-log entries and no extra RNG draws.
  - A TLE asset, or a non-LEO asset: never drag-coupled.
  - An inject carrying a series while one is already in effect: the inject's entries take effect
    from their own times onward. Earlier entries remain history.
- **Determinism.** Everything is a function of declared data, simulated time and the seeded RNG.

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `engine/perturbations.py` | Owns `secular_drag_decay()` and the pure multiplier functions (`f_solar`, `f_geo`, the step-held index lookup). |
| `engine/propagator.py` | Owns the `Propagator` seam through which the re-epoched drag update to an asset's orbit is applied. |
| `engine/busmodel.py` (the existing `bus_tick` grid) | Hosts the per-tick drag step. It acts only when a series is declared. |
| `session/manager.py` | Validates the series at the White inject boundary, applies a series-carrying `space_weather` inject, and owns the environmental-anomaly tick, which fires the `anomaly` effect through `_apply_inject_effects`. |
| `content/vignette.py` | Owns the vignette schema for the series, the ballistic coefficient and the anomaly block, and their load-time refusal (`FR-5310` gate). |

## Interfaces Used

- `INT-0008` (SessionManager → engine Clock/Scheduler/EventLog/OrderSystem): the tick grid both
  couplings run on.
- `INT-0016` (White Cell inject → direct engine mutation bypass): the path a series-carrying
  inject takes.

No new interface is needed.

## Data Model Changes

All of these are additive and optional (ADR-0039 decisions 1, 7 and 8).

- `WorldState.space_weather` gains an optional index-series list beside `severity`. Each entry
  holds a simulated time plus `f107` and/or `kp`.
- A vignette may declare an initial series. Today's `initial_space_weather` already carries this
  dict.
- `Asset` gains an optional ballistic coefficient (m²/kg). It has no default; absent means no
  drag.
- A vignette may declare an optional environmental-anomaly block holding `base_rate_per_day`, the
  eligible asset ids, and the `anomaly` effect's `subsystem` and `cause`.

## State Changes

- The series is input state. It changes only through a new inject or the vignette's own
  declaration, as the existing `severity` field does.
- Asset orbits change on each drag tick. Assets' bus and safe-mode state changes when an
  environmental anomaly fires.
- Each anomaly firing is recorded in that tick's event-log payload, so AAR shows it.

## Error Handling

These rules come from ADR-0039 decision 6.

- **Refused at vignette load**, through the `FR-5310` gate:
  - a `kp` that is non-numeric, non-finite, or outside [0, 9];
  - an `f107` that is non-numeric, non-finite, or ≤ 0;
  - an entry with neither index, or with a malformed time key;
  - a ballistic coefficient ≤ 0;
  - an anomaly block with a negative or non-numeric base rate, an unknown asset, or a `subsystem`
    other than `bus`/`telemetry`.
- **Refused at the White inject boundary** with a 400 (`IP-1063` pattern): the same value rules
  for a series-carrying `space_weather` inject.
- **Skipped in the handler:** an invalid entry that still reaches the handler is skipped with one
  White message and never raises (`IP-1063`'s skip-never-raise rule).
- **Not refused:** a positive F10.7 outside 50–300 is clamped, not refused.

## Performance Considerations

The work is one small scalar computation per qualifying asset per 300 s tick. It adds no new event
kind for drag, which rides `bus_tick`, and adds anomaly ticks only for vignettes that opt in
(`NFR-1100`-class determinism and replay cost unchanged otherwise).

## Security Considerations

None. The series and the opt-in fields are White-authored data, like every other vignette or
inject field. Anomalies surface through the existing fog-filtered messages and pass-gated SOH.

## Acceptance Criteria

1. **Drag responds to the series, and replays.** Take the same opted-in LEO asset over the same
   duration in two runs. One run declares a quiescent series (F10.7 = 70, Kp = 1). The other
   declares an active series (F10.7 = 250, Kp = 7). The active run's semi-major-axis loss is
   larger. Replaying either run reproduces a byte-identical final world. *(`FR-1230`)*
2. **The mapping matches ADR-0039.**
   - The drag multiplier equals `f_solar × f_geo` at sample points, for example 1.0 at
     (150, 2), 6.0 at (150, 7), 0.3 at (40, 0) after clamping, and 30.0 at (300, 9).
   - The anomaly-rate multiplier ignores F10.7.
   *(`FR-1230`/`FR-4440`)*
3. **Anomaly rate responds to Kp, and replays.** Take two sessions with the same anomaly block
   and seed, differing only in their series (Kp = 1 versus Kp = 8). The Kp = 8 run fires more
   environmental anomalies over the same duration. Replaying either reproduces identical firing
   times. *(`FR-4440`)*
4. **Opt-out is byte-identical.** A vignette with none of the new fields, or with a series but no
   ballistic coefficients and no anomaly block, produces exactly the same final world and event
   log as before this Feature. *(`FR-1230`/`FR-4440` Preconditions)*
5. **Out-of-range values are refused.** A vignette declaring Kp = 12, or F10.7 = −5, fails to load
   with a validation error naming the field. A White inject carrying such a value is rejected with
   a 400 and changes nothing. *(ADR-0039 decision 6)*
6. **Only qualifying assets are coupled.** A TLE asset, a GEO asset, and a LEO asset without a
   ballistic coefficient are each unchanged by the series. *(`FR-1230` Precondition)*

## Verification Plan

All six criteria are verified by Test:

- **Criteria 1 and 3:** paired sessions, comparing the semi-major-axis loss or the firing count,
  plus a replay byte-diff.
- **Criterion 2:** unit tests of the pure multiplier functions.
- **Criterion 4:** a byte-identity check of a shipped vignette's final world and event log against
  the pre-change behaviour (for example, the determinism property test, plus an explicit
  before/after fixture).
- **Criterion 5:** load and HTTP-inject refusal tests.
- **Criterion 6:** a mixed-fleet test.

## Dependencies

- `FR-4410`/`FR-4430` (the inject mechanism and the `anomaly` effect, both `VERIFIED` via
  `IP-1062`/`IP-1063`).
- `FR-5310` (the load-time validation gate, `IP-1310`).
- The existing, currently uncoupled drag functions in `engine/perturbations.py`.

## Risks

- **Fidelity risk (accepted).** A secular decrement every 300 s is coarse. ADR-0039 records why
  that is acceptable at moderate fidelity.
- **Two single-source anchors.** The TIEGCM ~10× solar span and the Kp ≥ 5 anomaly onset are each
  single-source and flagged in R131 v1.2. A later citation pass (`BL-0280`) could move the anchor
  values. That change would be a data-table change, not a redesign.
- **RNG-stream coupling.** The anomaly draws add RNG consumption only for opted-in vignettes. An
  implementation that drew unconditionally would shift every shipped vignette's RNG stream and
  break criterion 4.

## Open Questions

None open. v1.0 Open Questions 1 and 2 are closed by ADR-0039 decisions 2–6. A related note,
not blocking: `FR-4440`'s Notes could record that ADR-0039's vignette-authored base rate is the
source of "environment-induced anomaly injects" (`BL-0281`, `04`).

## Related ADRs

- `ADR-0039` (the mapping, refusal rules and application model).
- `ADR-0002` (deterministic core).
- `ADR-0006` (sub-stepped deterministic clock).

## Related Interfaces

None beyond `INT-0008`/`INT-0016`, which are already listed under Interfaces Used.
