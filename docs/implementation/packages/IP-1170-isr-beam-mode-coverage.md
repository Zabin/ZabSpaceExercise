# IP-1170 — ISR Beam-Mode Coverage: Weather & Missile-Warning

> **Package ID:** IP-1170
> **Version:** 1.0
> **Status:** 🔴 BLOCKED *(not authorized — MSTR-006 §3. No package-level dependency blocks this
> one; it is the tranche's own prerequisite, sequenced first per `01-technical-work-breakdown.md`
> Tranche 3.)*
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

**Not started — not authorized (MSTR-006 §3).** Proposed sequence once authorized:

1. Write a failing test asserting `available_modes("weather")`/`available_modes("mw")` return the
   new mode names (not `isr_eo`'s modes via fallback) and `beam_params("weather")`/`beam_params("mw")`
   return the new, type-specific numbers.
2. Add the two new `BEAM_MODES` entries and `_DEFAULT_MODE` mappings, grounded in `R109`'s cited
   figures.
3. Confirm `orders.py`'s existing call sites (`beam_params`/`available_modes` callers at
   observe-schedule time) require no change — they already accept any payload type string and look
   it up generically; this is purely a data-completeness fix.
4. Re-run the full existing ISR/observe test suite to confirm no regression to `isr_eo`/`isr_sar`/
   `sda` behavior (this package adds keys, touches none of the existing three).

## Tests to Add

*(Proposed — none exist yet.)*

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

- `ROADMAP.md` Implementation Packages theme — add this package's row.
- `docs/pipeline/backlog.md` `BL-0053` — flip to `DONE` once implemented and verified (the pipeline
  manager's own harvest step, not this package's write scope).
- `docs/research/encyclopedia/R109-sensor-operations.md` — no change needed; it already grounds the
  numbers this package consumes (confirmed at authoring time — the research pass predates this
  package and explicitly flagged the engine gap it fills).

## Definition of Done

- [ ] **Explicit user authorization obtained** for this package's Implementation Tasks (MSTR-006
  §3) — not yet on record.
- [ ] `BEAM_MODES["weather"]` and `BEAM_MODES["mw"]` exist with `R109`-grounded, type-specific
  numbers (not copies of `isr_eo`'s).
- [ ] `_DEFAULT_MODE["weather"]`/`_DEFAULT_MODE["mw"]` resolve to a real mode name for each type.
- [ ] `available_modes("weather")`/`available_modes("mw")` no longer fall back to `isr_eo`'s modes.
- [ ] Every existing `isr_eo`/`isr_sar`/`sda` test continues to pass unchanged.

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
