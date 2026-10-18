# ADR-0039 — Space-weather index series: a two-factor piecewise-linear multiplier, refused out of range, applied on the existing tick grid

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0039
- **Title:** A declared F10.7/Kp series scales LEO drag by `f_solar(F10.7) × f_geo(Kp)` and scales
  a vignette-authored environmental-anomaly base rate by `f_geo(Kp)` alone. Both factors are
  piecewise-linear over fixed anchor tables. A non-physical index value is refused at the authoring
  and inject boundaries.
- **Status:** Accepted

## Context

`FR-1230` (index-driven LEO drag) and `FR-4440` (index-driven anomaly rate) are baselined, and
[FS-123](../../features/FS-123-space-weather-index-coupling.md) v1.0 specifies them. FS-123 carries
two Open Questions that it correctly did not answer itself:

1. **The mapping** from a declared index value to a drag multiplier and to an anomaly-rate
   multiplier (`BL-0104`).
2. **The behaviour for a non-physical index value** (`BL-0121`).

`07-implementation-planning` confirmed in run #78 that no package can be written without both
answers, and that it may not invent them. This is the same situation as FS-105's directed-energy
Open Questions, which `ADR-0034`/`ADR-0035` closed.

[R131 v1.2](../../research/encyclopedia/R131-space-environment-and-space-weather-operations.md)
(2026-10-18) grounds the anchors:

- Kp is bounded to [0, 9]. NOAA's G-scale starts at Kp 5 (G1) and ends at Kp 9 (G5).
- F10.7 runs from about 50 to more than 300 sfu over a solar cycle.
- 400 km density rises more than 10× across a solar cycle. This comes from a single modelled
  source and is flagged as such.
- A major storm raises LEO density 2–10×.
- Anomaly likelihood follows Kp above G1, not F10.7. This comes from a single proceedings source
  and is flagged, and contrary evidence is noted.

R131 §5 v1.2 also constrains the shape of the mapping: two multiplying factors, flat below storm
level, piecewise-linear rather than a fitted curve, refusal at the boundary, and an anomaly rate
scaled by the geomagnetic factor over an authored base rate. No source gives a closed-form curve,
so the remaining choice of exact anchor values is a design decision. This ADR records it.

The as-built code constrains how the series can be applied:

- Fictional assets propagate analytically from epoch elements (`engine/propagator.py`
  `ModeratePropagator`, `engine/orbit.py`).
- `engine/perturbations.py::secular_drag_decay()` is a pure function that nothing calls today.
- A deterministic `bus_tick` grid already exists (300 s, `engine/busmodel.py`), and so does a
  session-owned `condition_check` grid (`session/manager.py`), both anchored to the start epoch
  (`IP-1064`).
- No `Asset` carries a ballistic coefficient.
- No environment-induced anomaly source exists. The `anomaly` effect (`FR-4430`) fires only from
  injects.

## Decision

1. **Series shape and where it lives.** The index series extends the existing
   `WorldState.space_weather` dict, as R131 §5 directs. It is a list of time-keyed entries, each
   carrying `f107` and/or `kp`. Each index is a step function: its value holds from its entry
   until that index's next entry. Before an index's first entry, or when no series is declared,
   that index's factor is **1.0**. The `severity` enum is untouched and keeps driving only what it
   drives today. The series enters as vignette data or as the payload of a `space_weather` inject.

2. **Solar factor `f_solar(F10.7)`** — piecewise-linear through the anchors:

   | F10.7 (sfu) | 50 | 150 | 300 |
   |---|---|---|---|
   | `f_solar` | 0.3 | 1.0 | 3.0 |

   - The 10× span from 50 to 300 sfu follows Tang et al. 2021.
   - **150 sfu is the reference flux.** By convention it is the activity level at which
     `perturbations.py`'s static `_ATMOS_TABLE` density applies unscaled. This is a modelling
     convention, not a sourced claim about that table's provenance.
   - A positive value below 50 is clamped to 0.3, and a value above 300 is clamped to 3.0. Both
     are real (R131 v1.2), just outside the anchor table.

3. **Geomagnetic factor `f_geo(Kp)`** — piecewise-linear through the anchors:

   | Kp | 0 | 4 | 5 (G1) | 9 (G5) |
   |---|---|---|---|---|
   | `f_geo` | 1.0 | 1.0 | 2.0 | 10.0 |

   The factor is flat below storm level and spans the cited 2–10× across G1–G5. The intermediate
   values are 4.0 at Kp 6, 6.0 at Kp 7 and 8.0 at Kp 8.

4. **Drag multiplier:** `M = f_solar × f_geo`, with a range of 0.3 to 30.

5. **Anomaly-rate multiplier:** `f_geo` **alone**. F10.7 does not scale anomaly rate (R131 §5
   v1.2 refines v1.1's "reuse the drag multiplier" suggestion).

6. **Plausible range (`BL-0121`).**
   - A declared `kp` that is non-numeric, non-finite, or outside [0, 9] is **refused**.
   - A declared `f107` that is non-numeric, non-finite, or ≤ 0 is **refused**.
   - An entry with neither index, or with a malformed time key, is **refused**.
   - Refusal happens at the two existing boundaries: vignette load (`FR-5310` /
     `validate_vignette`, `IP-1310`) and the White-Cell inject boundary (`IP-1063`'s fire-time
     validation, 400). Following IP-1063's skip-never-raise rule, an invalid entry that still
     reaches the handler is skipped with one White message.
   - Values are never silently clamped into range, except the positive-F10.7 clamp in decision 2.

7. **Drag application model.**
   - Drag applies only to an asset with all three of the following:
     - a `kepler`-source orbit in regime `LEO` or `LEO_SSO` (`engine/orbit.py::classify_regime`);
     - a vignette-authored **ballistic coefficient** greater than 0 (Cd·A/m, m²/kg, a new
       optional asset field with **no default**);
     - a declared series in effect.
   - TLE-backed assets are excluded, because sgp4 already carries its own drag term (B*) and
     modifying a TLE is out of scope.
   - At each tick of the existing start-anchored 300 s grid, the semi-major-axis decrement over
     the tick is `secular_drag_decay(altitude, BC, dt) × M`, using the series values in effect at
     the tick's start.
   - The decrement is applied as a deterministic in-handler orbit update through the existing
     `Propagator` seam. It is re-epoched at the tick so position stays continuous at the tick
     instant, in the same way `apply_impulse` already updates an orbit.
   - With no series declared, or no qualifying asset, the drag step changes nothing: no state
     change, no RNG draw and no new event-log entries, so all 19 shipped vignettes stay
     byte-identical.

8. **Environmental-anomaly model (`FR-4440`).**
   - The source of environment-induced anomalies is a new, optional, vignette-authored block. It
     holds a base rate per asset per day, the eligible assets, and the `anomaly` effect fields
     (`subsystem`, `cause`) that `FR-4430` already defines. There is no hard-coded base rate,
     because no source gives one (R131 §5 v1.2).
   - At each tick of the start-anchored grid, each eligible asset with a bus fires with
     probability `p = 1 − exp(−base_rate × f_geo(Kp) × dt_days)`. The draw uses the handler's
     seeded `rng` and nothing else.
   - A firing applies the existing `anomaly` effect through `_apply_inject_effects`, unchanged.
   - The tick is session-owned, because the anomaly dispatch lives in `session/manager.py` and
     the engine may not import session code.
   - The tick is scheduled only when the vignette declares the block. Without a series,
     `f_geo` = 1.0 and anomalies fire at the base rate, unscaled. That is consistent with
     `FR-4440`'s "no rate scaling applies".

## Alternatives Considered

- **One blended scalar** (for example, one multiplier also driving anomaly rate, as R131 v1.1
  suggested) — rejected. The solar-cycle and storm terms are physically distinct and multiply.
  Anomaly likelihood tracks Kp and charging, not F10.7 (R131 v1.2).
- **An exponential or Jacchia-style fit** — rejected. Any coefficients would be unsourced at this
  fidelity, and R131 §5 directs piecewise-linear anchors.
- **Clamping every out-of-range value** — rejected. A negative F10.7 or a Kp of 12 is an authoring
  error. Clamping it hides the error and still produces a plausible-looking but meaningless run.
  The load-time and fire-time validation precedents (`IP-1310`, `IP-1063`) refuse such values.
- **A default ballistic coefficient for every satellite** — rejected. A default would be an
  invented number applied to all 19 shipped vignettes, and it would change their trajectories.
  Opt-in keeps them byte-identical.
- **Re-integrating drag numerically between ticks** — rejected for v1. It belongs to the
  `HighFidelityPropagator` seam (FUTURE-WORK §2). A 300 s secular step is consistent with
  moderate fidelity, and `secular_drag_decay` already assumes it.
- **Drawing environmental anomalies in the engine** — rejected. The `anomaly` dispatch is
  session-owned. Duplicating it in the engine would fork the effect path that `IP-1062`/`IP-1063`
  unified.

## Rationale

Every number in the anchor tables traces to R131 v1.2 (NOAA's G-scale and Kp bounds, NOAA's F10.7
range, Tang et al.'s ~10× span, and §3's 2–10× storm range), except two declared conventions: the
150 sfu reference, and the linear interpolation between anchors. Both are stated as conventions,
not as facts. Each factor stays within one order of magnitude, which keeps a vignette author's
intuition aligned with the research. Opt-in fields and an unchanged tick grid preserve invariant 1
and the byte-identity of every shipped vignette.

## Consequences

- **`06-feature-specification`:** revise FS-123 to v1.1, closing Open Questions 1 and 2 by
  citing this ADR, and adding the data-model items (series entries, the optional ballistic
  coefficient, the optional environmental-anomaly block) and the refusal rules to Error Handling.
  FS-123 then becomes ✅ Ready.
- **`07-implementation-planning`:** write `IP-1230`, which is already reserved.
- **`04-requirements-engineering` (note, not a blocker):** `FR-4440` presumes
  "environment-induced anomaly injects" exist. This ADR supplies their source, a vignette-authored
  base rate, as the reading of `FR-4440`'s "existing anomaly inject mechanism" input. A Notes line
  on `FR-4440` would record that reading.
- **No shipped vignette, test or replay changes behaviour** until a vignette opts in.

## Related

`FR-1230`, `FR-4440`, `FR-4430`, `FR-5310`
(`docs/requirements/01-functional-requirements.md`);
[FS-123](../../features/FS-123-space-weather-index-coupling.md);
[R131](../../research/encyclopedia/R131-space-environment-and-space-weather-operations.md)
v1.2 §3 "Quantitative anchors" and §5; `ADR-0002` (deterministic core); `ADR-0006` (sub-stepped
clock); `ADR-0034`/`ADR-0035` (the precedent of closing FS Open Questions); `IP-1063`, `IP-1064`,
`IP-1310`; backlog `BL-0074`, `BL-0104`, `BL-0121`.
