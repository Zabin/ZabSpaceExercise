# IP-1220 — Sensor Modality Models

> **Package ID:** IP-1220
> **Version:** 1.0
> **Status:** 🟡 READY *(authorized 2026-09-27 by the project owner's direct instruction, MSTR-006 §3 — see Objective)*
> **Dependencies:** [FS-122](../../features/FS-122-sensor-modality-models.md) v1.0
> (`FR-1610`-`FR-1660`), `engine/entities.py`/`engine/access.py`/`engine/isr.py`/`engine/orders.py`/
> `engine/custody.py`/`engine/ssn.py` (all `VERIFIED` baseline code)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [docs/pipeline/backlog.md](../../pipeline/backlog.md) `BL-0073` (item B7), `BL-0083` (item B17),
> `BL-0113`/`BL-0114` (this Feature's two Open Questions)
> **Produces:** the six sensor-modality access/effectiveness models satisfying `FR-1610`-`FR-1660`
> in full
> **Feature Reference:** [FS-122 — Sensor Modality Models](../../features/FS-122-sensor-modality-models.md)
> **Supersedes:** none — new package
> **Related Topics:** [`spacesim/engine/entities.py`](../../../spacesim/engine/entities.py),
> [`spacesim/engine/access.py`](../../../spacesim/engine/access.py),
> [`spacesim/engine/isr.py`](../../../spacesim/engine/isr.py),
> [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [`spacesim/engine/ssn.py`](../../../spacesim/engine/ssn.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package.*

## Package ID

IP-1220

## Title

Sensor Modality Models

## Objective

Add six additive, optional `Sensor` fields and the access/effectiveness/tasking-precondition logic
they gate: a fence/dish beam-mode entry, a solar/lunar exclusion angle, a min-range/altitude-band
affinity, a cue-dependence precondition, a passive-RF multi-receiver network fix, and a
host-Asset-following position — satisfying `FR-1610`-`FR-1660` in full.

> **This package is authorized for coding.** Per MSTR-006 §3, the project owner gave explicit
> go-ahead 2026-09-27 (batched with five sibling packages from the same Should-tier intake round).

## Feature Reference

[FS-122 — Sensor Modality Models](../../features/FS-122-sensor-modality-models.md)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-1610 | Fence/dish radar beam-mode variants | A new `BEAM_MODES` entry (wide-field-of-regard, low-gain) alongside the existing `isr_eo`/`isr_sar`/`sda` payload-type entries — no new `Sensor.kind`, no branch in `_observation_predicate`. |
| FR-1620 | Optical sensor solar/lunar exclusion angle | New `Sensor.exclusion_angle_deg: Optional[float]` field; `_observation_predicate`'s ground-optical branch, after its existing lighting check, additionally rejects when the Sun's (or, if declared, Moon's) angular separation from the sensor's boresight is inside the declared radius. |
| FR-1630 | Space-based sensor minimum-range floor and altitude-band affinity | New `Sensor.min_range_km`/`altitude_band_affinity: Optional[float/str]` fields; `effective_gain()` gains a hard reject below `min_range_km` and a gain-degradation term outside the declared band, composing with the existing off-nadir `look_angle_deg` term. |
| FR-1640 | Cue-dependent sensor tasking precondition | New `Sensor.requires_cue: bool = False` field; `OrderSystem`'s plan-time validation and `dry_run()` reject/pre-disable a tasking of a `requires_cue` sensor against a target with no existing `Track` in the tasking cell's `TrackCatalog`. |
| FR-1650 | Passive-RF multilateration sensor network | A declared network of ≥3 member sensors (reusing the existing `SSNNetwork` aggregation pattern); a fix is produced only when the target's emission state is "on" and ≥3 (2D)/≥4 (3D) member receivers simultaneously have access. |
| FR-1660 | Satellite-hosted sensor follows host orbit | New `Sensor.host_asset_id: Optional[str]` field; a hosted sensor's position is read from the host Asset's current propagated orbital state at every access-window computation; observe orders may name either identifier. |

## Architecture Components

- **C1 Simulation Engine** (`engine/entities.py`, `engine/access.py`, `engine/isr.py`,
  `engine/orders.py`) — owns all six leaves' access-predicate/effectiveness/tasking-precondition
  logic; this package extends, does not replace, `AccessProvider._observation_predicate` and
  `isr.py`'s `effective_gain()`.
- **C2 Session/Application Layer** (`engine/custody.py`'s `Track`/`TrackCatalog`, read via
  `session/cells.py`) — consulted (not modified) by `FR-1640`'s cue-existence check.
- **C3 Mock SSN** (`engine/ssn.py`) — owns the network-aggregation pattern `FR-1650` reuses.

## Interfaces

`INT-0008` (SessionManager → Engine Clock/Scheduler/EventLog/OrderSystem) — every leaf's
computation operates through this existing interface. `INT-0009`/`INT-0010` (CellController/
SessionAPI → Mock SSN / Mock SSN → Engine delivery) — `FR-1650`'s network fix reuses these
unmodified. `INT-0007` (CellController → Engine Custody) — `FR-1640`'s cue check and `FR-1650`'s
fix-delivery both operate through this existing interface.

## Design Decisions (resolving FS-122's Open Questions)

1. **Open Question 2 (`BL-0114`) — `FR-1650`'s "no fix" state does not distinguish an
   insufficient-receiver-count cause from a non-emitting-target cause.** Both resolve to the
   identical observable outcome (no fix produced, no `Track` update) with no differentiated reason
   surfaced to the operator. Rationale: neither `FR-1650`'s own text nor `R109` §3.10 requires this
   distinction, and inventing one would add UI/API surface the requirement doesn't ask for; a
   future finding can request it explicitly if operators report needing it.
2. **Open Question 1 (`BL-0113`) — not decided here.** Whether an exclusion-angle rejection must
   carry a UI-distinguishable reason from a lighting-predicate rejection is routed to
   `04-requirements-engineering` (per `BL-0113`'s own disposition) — this package implements both
   checks as ordinary `AccessWindow`-rejection paths with no additional reason-code field, and will
   need a follow-up if `04` later baselines a distinguishability requirement.

## Files to Create

None.

## Files to Modify

- `spacesim/engine/entities.py` — `Sensor` gains: a beam-mode reference (reusing the existing
  swath/resolution/power/duty-cycle/gain schema, no new field shape); `exclusion_angle_deg:
  Optional[float] = None`; `min_range_km: Optional[float] = None`; `altitude_band_affinity:
  Optional[str] = None`; `requires_cue: bool = False`; `host_asset_id: Optional[str] = None`. All
  six additive, default-absent — a `Sensor` declaring none behaves exactly as today.
- `spacesim/engine/access.py` — `AccessProvider._observation_predicate`'s ground-optical branch
  gains the exclusion-angle check after its existing lighting check; the space-based branch gains
  the min-range-floor reject before its existing gain computation; a new resolution helper reads
  `host_asset_id` (when set) to substitute the host Asset's current orbital state for the sensor's
  own when computing any of the six access channels' geometry.
- `spacesim/engine/isr.py` — `BEAM_MODES` gains one new fence/dish-style entry (wide-field-of-regard,
  low-gain); `effective_gain()` gains an altitude-band-affinity degradation term, applied after the
  existing off-nadir `look_angle_deg` term.
- `spacesim/engine/orders.py` — `OrderSystem`'s plan-time validation and `dry_run()` gain a
  `requires_cue` check: reject/pre-disable a tasking of a cue-dependent sensor against a target
  with no existing `Track` in the tasking cell's `TrackCatalog`.
- `spacesim/engine/ssn.py` — a new passive-RF network variant reusing `SSNNetwork`'s existing
  member-list/dispersion-preset shape, gated on the target's emission state (read from the target
  Asset's existing state, not a new field this package introduces) and member-receiver access count
  (≥3 for 2D, ≥4 for 3D).

## Implementation Tasks

1. Write failing tests asserting the six new `Sensor` fields default to absent/`False` and produce
   byte-identical behavior to today when unset, before adding the fields.
2. Add the six additive fields to `Sensor`.
3. Write a failing test for the fence/dish `BEAM_MODES` entry (wide-field-of-regard sensor detects
   more transiting objects at lower per-object gain than a narrow-beam sensor observing the same
   volume), before adding the entry.
4. Write a failing test for `FR-1620`'s exclusion-angle rejection (parametrized over Sun-angle
   geometries crossing the declared boundary), before extending `_observation_predicate`.
5. Write a failing test for `FR-1630`'s min-range floor (rejected below, accepted above) and
   altitude-band-affinity degradation (parametrized over range/band membership), before extending
   `effective_gain()`/`_observation_predicate`.
6. Write a failing test for `FR-1640`'s cue-existence check (rejected with no `Track`, accepted with
   one), before extending `OrderSystem`.
7. Write a failing test for `FR-1650`'s network fix (parametrized over receiver count 2/3/4 and
   target emission state on/off), before adding the passive-RF network variant to `ssn.py`.
8. Write a failing test for `FR-1660`'s hosted-sensor position (before/after a host-Asset manoeuvre;
   an observe order naming each of the two identifiers produces the same result), before adding the
   `host_asset_id` resolution.
9. Re-run the full existing suite; confirm zero regressions to any existing sensor/access-window
   test.

## Tests to Add

- `spacesim/tests/test_entities.py` (or `test_access.py`) — the six new `Sensor` fields'
  default-absent regression.
- `spacesim/tests/test_isr.py` — fence/dish beam-mode trade; altitude-band-affinity gain
  degradation.
- `spacesim/tests/test_access.py` — exclusion-angle rejection parametrization; min-range floor.
- `spacesim/tests/test_orders.py` — cue-dependence tasking rejection/acceptance.
- `spacesim/tests/test_ssn.py` — passive-RF network fix parametrization (receiver count × emission
  state).
- `spacesim/tests/test_access.py` (or a new hosted-sensor test module) — hosted-sensor
  pre-/post-manoeuvre position; dual-identifier observe-order equivalence.

The two permanent gates (`spacesim/tests/test_determinism.py`, `spacesim/tests/test_import_guard.py`)
must be re-run green — no wall-clock read or global RNG use is introduced by any of the six leaves.

## Documentation Updates

- `CLAUDE.md` Code Map — `engine/entities.py`, `engine/access.py`, `engine/isr.py`,
  `engine/orders.py`, `engine/ssn.py` entries each gain a one-line note for their respective new
  field/check.
- `docs/requirements/03-requirements-traceability-matrix.md` — `FR-1610`-`FR-1660` rows'
  `Impl. Package`/`Test` cells updated from `UNASSIGNED` to `IP-1220`/the named test files.
- `docs/features/FS-122-sensor-modality-models.md` — `Referenced By` metadata gains this package's
  link (metadata cross-link only).
- `docs/pipeline/backlog.md` — `BL-0114` flips `DONE` (resolved by Design Decision 1 above);
  `BL-0113` stays open, routed to `04-requirements-engineering` as already dispositioned.

## Definition of Done

- [ ] All six new `Sensor` fields exist, default-absent, zero behavior change when unset.
- [ ] Fence/dish beam-mode trade produces the expected detection/gain contrast.
- [ ] Exclusion-angle check rejects/grants per the declared boundary, composing with the existing
  lighting predicate.
- [ ] Min-range floor rejects below threshold; altitude-band affinity degrades gain outside the
  declared band.
- [ ] Cue-dependent sensor tasking rejected without an existing `Track`, accepted with one.
- [ ] Passive-RF network fix produced only with a sufficient receiver count and an emitting target.
- [ ] Hosted-sensor position reflects the host Asset's current state, including post-manoeuvre;
  both naming identifiers produce identical results.
- [ ] Full existing test suite green, zero regressions, both permanent gates green.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] Every new test named above exists and is green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green.
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green.
- [ ] Independently confirm, by reading the shipped code, that the six fields are genuinely
  additive/optional (a `Sensor` with none set is byte-identical in behavior to the pre-package
  code) rather than merely tested that way.
- [ ] Independently confirm `FR-1650`'s network fix never bypasses `CellController`'s fog-of-war
  filter when delivering into a cell's `TrackCatalog`.

## Dependencies

- **Upstream:** [FS-122](../../features/FS-122-sensor-modality-models.md) v1.0 (approved, `✅ Ready
  for implementation planning`); `engine/entities.py`/`access.py`/`isr.py`/`orders.py`/`custody.py`
  (all `VERIFIED`, per the `BL-0004` retro-verification sweep); `engine/ssn.py` (`IP-1040`,
  `VERIFIED`).
- **Downstream:** none within this batch.
- **Build-sequencing:** independent of every other package in this batch (no shared file).

## Risks

- **`BL-0113` (exclusion-angle rejection-reason distinguishability) remains open**, routed to
  `04-requirements-engineering` — this package's own implementation does not add a distinguishable
  reason code; a future amendment could require revisiting this package's error-surfacing code.
- **`R109` §3.7's single-source 90° exclusion-angle figure (`BL-0103`)** informs only a plausible
  default for `exclusion_angle_deg`, never a hard-coded constant — this package leaves the field
  fully configurable with no shipped default value baked into engine logic beyond what a vignette
  author declares.

## Rollback Considerations

All six fields are additive and optional; reverting `Sensor` to omit them, and reverting the four
touched functions (`_observation_predicate`, `effective_gain`, the plan-time validator, the SSN
network variant) to their pre-package bodies, fully removes this package's capability with no
migration concern — no vignette shipped before this package declares any of the six fields.
