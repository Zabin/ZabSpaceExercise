# IP-1170 — ISR Beam-Mode Coverage: Weather & Missile-Warning

> **Package ID:** IP-1170
> **Version:** 1.0
> **Status:** 🔵 COMPLETE *(implemented 2026-07-05 by `08-code-implementation` — `BEAM_MODES["weather"]`/
> `["mw"]` + `_DEFAULT_MODE` entries added to `spacesim/engine/isr.py`, 9 new tests in
> `spacesim/tests/test_isr.py`, full suite 575 passed/3 skipped (up from 566/3, +9), both permanent
> gates green. Awaiting `09-package-verification` to advance to `VERIFIED`.)*
> **Dependencies:** None (independent engine-only fix; every citation below checked directly
> against the current `spacesim/engine/isr.py`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [FS-117](../../features/FS-117-vignette-creator.md) (this package closes the precondition
> `FR-5170`'s own Postcondition names for the `weather`/`mw` typed sub-schemas)
> **Produces:** real `BEAM_MODES` entries for `weather`/`mw`, so [IP-1171](IP-1171-typed-payload-bus-parameters.md)'s
> typed sub-schemas for those two payload types have an engine parameterization to bind to, closing
> `docs/pipeline/backlog.md` `BL-0053`
> **Feature Reference:** [FS-117 — Vignette Creator](../../features/FS-117-vignette-creator.md)
> (prerequisite, not itself one of `FS-117`'s cited requirements — see Requirements Covered)
> **Supersedes:** none — new package
> **Related Topics:** [`spacesim/engine/isr.py`](../../../spacesim/engine/isr.py),
> [`docs/research/encyclopedia/R109-sensor-operations.md`](../../research/encyclopedia/R109-sensor-operations.md)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*This is a forward-design package scoped as `FS-117`'s tranche prerequisite, not one of `FS-117`'s
own cited requirements — no `FR-xxxx`/`NFR-xxxx` names this fix directly (it is an engine
completeness gap `R109`'s research pass surfaced, tracked as `BL-0053`). It is sequenced first in
Tranche 3 because `FR-5170`'s own Postcondition explicitly discloses that a `weather`/`mw` typed
parameter set has no observable engine effect until this ships.*

## Package ID

IP-1170

## Title

ISR Beam-Mode Coverage: Weather & Missile-Warning

## Objective

Add real `BEAM_MODES` entries for the `weather` and `mw` (missile-warning) payload types to
`engine/isr.py`, grounded in `R109`'s GOES-R ABI (weather) and SBIRS-GEO scan/stare (missile
warning) research, so these two payload types stop silently falling back to generic EO stripmap
numbers.

> **This is a forward-design package. Per MSTR-006 §3, this document's own specification is not
> itself an authorization to write code** — a separate, explicit user go-ahead is required before
> any Implementation Task below begins.

## Feature Reference

[FS-117 — Vignette Creator](../../features/FS-117-vignette-creator.md) (tranche prerequisite —
see header note; the payload types this fix parameterizes are two of the eight `FR-5170` covers)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-5170 (partial, precondition only) | Typed per-payload-type parameter sub-schemas | `FR-5170`'s own Postcondition states a `weather`/`mw` typed parameter set has no observable engine effect until this gap closes. This package does not implement `FR-5170` itself (see [IP-1171](IP-1171-typed-payload-bus-parameters.md)) — it removes the precondition blocking that requirement's `weather`/`mw` half from being more than a plausible-looking but inert field. |

## Architecture Components

- **C1 Simulation Engine** — `engine/isr.py`'s `BEAM_MODES` dict and `_DEFAULT_MODE` mapping gain
  `weather`/`mw` entries. No other engine module changes; `beam_params()`/`available_modes()`'s own
  logic is unchanged (they already correctly look up whatever `BEAM_MODES` contains — the gap is
  purely missing data, not missing code).

## Interfaces

None — `engine/isr.py` is a pure-computation module (`orders.py` calls `beam_params()` at
observe-schedule time); this package adds data to an existing lookup table, no new interface.

## Files to Create

None.

## Files to Modify

- `spacesim/engine/isr.py` *(proposed)* — add two new top-level keys to `BEAM_MODES`:
  - `"weather"`: modes grounded in `R109`'s GOES-R Advanced Baseline Imager characteristics
    (0.5–2 km resolution depending on band, 30 s–15 min revisit depending on scan mode) — a small
    mode set (e.g. `full_disk`/`conus`/`mesoscale`, mirroring GOES-R's own named scan modes) with
    `swath_km`/`resolution_m`/`power_factor`/`duty_cycle`/`gain_factor` fields in the same shape
    every existing entry uses.
  - `"mw"`: modes grounded in `R109`'s SBIRS-GEO scan/stare dichotomy — a `scan` mode (wide
    coverage, coarser revisit) and a `stare` mode (narrow, persistent dwell on a cued area),
    following the existing `isr_eo`/`isr_sar` precedent of a handful of named modes per type.
  - `_DEFAULT_MODE["weather"]` and `_DEFAULT_MODE["mw"]` — a sensible default mode name for each
    (e.g. the wider-coverage mode, matching `isr_eo`'s `"stripmap"`/`sda`'s `"nominal"` pattern of
    defaulting to a middle-ground mode, not the most extreme one).

**Explicitly out of scope for this package:** any change to `PayloadState`, the vignette schema, or
the Creator's UI — those are [IP-1171](IP-1171-typed-payload-bus-parameters.md)'s concern. This
package only makes the *existing* `beam_params()`/`available_modes()` lookup return real numbers
for these two payload types instead of falling back to generic EO defaults; it does not change how
or when those functions are called.

## Implementation Tasks

**Complete (2026-07-05, `08-code-implementation`).**

1. ✅ Wrote 9 failing tests in `spacesim/tests/test_isr.py` first (test-first, per `CLAUDE.md`),
   covering `available_modes("weather")`/`available_modes("mw")`, `beam_params()` defaults and
   mode-specific values for both new types, the relative mesoscale/conus/full_disk and scan/stare
   orderings, and a regression check that `isr_eo`/`isr_sar`/`sda` are byte-identical. Confirmed all
   9 failed before implementation.
2. ✅ Added `BEAM_MODES["weather"]` (`mesoscale`/`conus`/`full_disk`) and `BEAM_MODES["mw"]`
   (`scan`/`stare`), plus `_DEFAULT_MODE["weather"] = "conus"` and `_DEFAULT_MODE["mw"] = "scan"`.
   `resolution_m` and the mesoscale/conus/full_disk duty-cycle ordering are directly grounded in
   `R109`'s cited GOES-R figures; `mw`'s `scan`/`stare` gain-factor and swath ordering is faithful
   to `R109`'s relative scan-vs-stare comparison. `swath_km` (both types) and `mw`'s `resolution_m`
   are illustrative order-of-magnitude values not independently re-cited from a numeric source —
   flagged, not silently guessed (see the Implementation Summary's Outstanding Issues).
3. ✅ Confirmed `orders.py`'s two `beam_params`/`available_modes` call sites (lines 531, 755) need no
   change — both call generically with a payload-type string, no hardcoded type list.
4. ✅ Full suite re-run: 575 passed/3 skipped (up from 566/3, +9 — the exact 9 new tests), zero
   regressions to `isr_eo`/`isr_sar`/`sda`.

## Tests to Add

- `spacesim/tests/test_isr.py` (existing file, extended) — 9 new tests, all passing:
  `test_available_modes_weather_not_eo_fallback`, `test_available_modes_mw_not_eo_fallback`,
  `test_beam_params_weather_default_mode_is_conus`,
  `test_beam_params_weather_mesoscale_is_finest_and_fastest`,
  `test_beam_params_weather_full_disk_is_coarsest_and_slowest`,
  `test_beam_params_mw_default_mode_is_scan`, `test_beam_params_mw_stare_has_higher_gain_than_scan`,
  `test_beam_params_weather_mw_distinct_from_isr_eo_defaults`,
  `test_beam_params_isr_eo_sar_sda_unchanged_by_weather_mw_addition`.

- `spacesim/tests/test_isr.py` *(existing file, extend)* or a new `test_isr_beam_modes.py` — one
  test per Acceptance Criterion:
  - `available_modes("weather")` returns weather-specific mode names, not `isr_eo`'s.
  - `available_modes("mw")` returns `mw`-specific mode names (at least `scan`/`stare`), not
    `isr_eo`'s.
  - `beam_params("weather")`/`beam_params("mw")` (no explicit mode) resolve to each type's own
    `_DEFAULT_MODE`, with numbers distinct from `isr_eo`'s stripmap defaults.
  - Regression: `beam_params("isr_eo")`/`beam_params("isr_sar")`/`beam_params("sda")` are
    byte-identical to before this package (no existing entry touched).

## Documentation Updates

- `ROADMAP.md` Implementation Packages theme — this package's row (added at planning time) updated
  to `COMPLETE`.
- `docs/pipeline/backlog.md` `BL-0053` — left to the pipeline manager's own harvest step (not this
  package's write scope) to flip to `DONE` once `09-package-verification` confirms.
- `docs/research/encyclopedia/R109-sensor-operations.md` — no change needed; confirmed unchanged,
  it already grounds the numbers this package consumes.
- `docs/requirements/03-requirements-traceability-matrix.md` `FR-5170`'s Test/Impl. Package cells —
  updated from `UNASSIGNED` to `spacesim/tests/test_isr.py` / `IP-1170`, both explicitly annotated
  as covering only the weather/mw engine-precondition slice, not `FR-5170`'s full typed-sub-schema/
  UI scope (that remains `IP-1171`'s to close).
- `CLAUDE.md`'s Code Map — `engine/isr.py`'s entry updated from "EO/SAR/SDA" to "EO/SAR/SDA/
  weather/mw," citing this package and `BL-0053`.

## Definition of Done

- [x] **Explicit user authorization obtained** for this package's Implementation Tasks (MSTR-006
  §3, 2026-07-05, project owner, recorded in `docs/pipeline/pipeline-journal.md` run #45).
- [x] `BEAM_MODES["weather"]` and `BEAM_MODES["mw"]` exist with `R109`-grounded, type-specific
  numbers (not copies of `isr_eo`'s). **Note:** resolution_m/duty_cycle are directly grounded in
  `R109`'s cited GOES-R/SBIRS figures; `swath_km` (both types) and `mw`'s `resolution_m` are
  illustrative order-of-magnitude values, not independently re-cited from a numeric source — see
  Outstanding Issues in the Implementation Summary.
- [x] `_DEFAULT_MODE["weather"]`/`_DEFAULT_MODE["mw"]` resolve to a real mode name for each type
  (`"conus"`/`"scan"`).
- [x] `available_modes("weather")`/`available_modes("mw")` no longer fall back to `isr_eo`'s modes.
- [x] Every existing `isr_eo`/`isr_sar`/`sda` test continues to pass unchanged.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] The new test file/additions exist and are green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green (pure data addition to a
  side-effect-free lookup module; no RNG, no wall-clock, no world-state mutation).
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green (no new import added).
- [ ] Full existing suite re-run with zero regressions.
- [ ] Independently confirm (not merely re-cite) that `BL-0053`'s originally-reported symptom
  (`beam_params("weather")`/`beam_params("mw")` returning generic EO numbers) no longer reproduces.

## Dependencies

- **Upstream:** None — this package's only "dependency" is the `R109` research grounding, already
  authored and unchanged.
- **Downstream:** [IP-1171](IP-1171-typed-payload-bus-parameters.md) depends on this package —
  its `weather`/`mw` typed sub-schemas are only meaningfully engine-effective once this ships.
- **Build-sequencing:** First in Tranche 3 — independent of every other package in this tranche,
  but a real precondition for `IP-1171`'s two payload types.

## Risks

- **Scoped narrowly on purpose.** It would be tempting to fold this into `IP-1171` since both touch
  "weather/mw payload parameterization" — kept separate because this package is pure `engine/isr.py`
  data (`C1` seam, no vignette-schema or `PayloadState` change), while `IP-1171` is a genuine
  Domain Model extension (`C1`+`C5` seam). Splitting lets this small, low-risk fix ship (and be
  verified) independently of the larger typed-parameter package, per `FS-117`'s own Open Question 6
  naming this exact sequencing choice for this skill to make.
- **No number in this package is invented** — every figure must trace to `R109`'s already-authored
  GOES-R/SBIRS grounding; if `08-code-implementation` cannot find a specific number in `R109` for a
  particular field, that is a research gap to flag, not a number to guess.

## Rollback Considerations

Purely additive — two new `BEAM_MODES` keys and two new `_DEFAULT_MODE` entries, no existing key
touched. Reverting removes the two payload types' real parameterization and restores today's
silent-fallback-to-EO behavior; no data migration concern (no persisted state depends on these
values beyond a live `beam_params()` call at observe-schedule time).
