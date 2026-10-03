> **Document ID:** FS-122
> **Version:** 1.0
> **Status:** ✅ Ready for implementation planning
> **Note on this repository's chain:** no `05-feature-decomposition` Feature Catalog exists here
> (per this skill's own Gotchas); this document's approved input is the just-baselined
> requirements themselves — `docs/requirements/01-functional-requirements.md` `FR-1610`-`FR-1660`
> (the new `FR-1600` family) — plus the research grounding those requirements cite
> ([`R109` v1.2](../research/encyclopedia/R109-sensor-operations.md) §3.6-§3.10) and the real
> baseline code they extend (`spacesim/engine/entities.py::Sensor`, `spacesim/engine/access.py`,
> `spacesim/engine/isr.py`).
> **Dependencies:** [FS-104](FS-104-sda-tasking.md) (SDA Tasking — the sensor-tasking workflow this
> Feature's access/effectiveness refinements sit underneath, distinct not duplicative per
> `FR-1600`'s own family preamble)
> **Referenced By:** [IP-1220](../implementation/packages/IP-1220-sensor-modality-models.md)
> (Implementation Package, `READY`, not yet authorized),
> [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0073` (item B7),
> `BL-0083` (item B17), [docs/requirements/01-functional-requirements.md](../requirements/01-functional-requirements.md)
> `FR-1610`-`FR-1660`, [docs/reviews/requirements-update-should-tier-batch.md](../reviews/requirements-update-should-tier-batch.md)
> **Produces:** five new sensor-modality access/effectiveness models (fence/dish radar, optical
> exclusion angle, space-based min-range/altitude-band, cue-dependent tasking, passive-RF
> multilateration) plus one hosted-sensor orbit-following model, satisfying `FR-1610`-`FR-1660` in
> full except where an Open Question below blocks full closure
> **Feature Mapping:** FS-122 (this document)
> **Related Topics:** [FS-103](FS-103-custody-management.md) (custody/Track — `FR-1640`'s cue
> precondition and `FR-1650`'s network-fix output both interact with `Track`)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template.*

# FS-122 — Sensor Modality Models (Fence/Dish Radar, Exclusion Angle, Range/Altitude-Band,
Cue-Dependence, Passive-RF Network, Hosted Sensor)

## Purpose

Give the six new sensor-modality requirements one coherent home: each adds a real-world sensor
behavior `FR-1220`'s generic six-channel access computation does not itself distinguish (a fence
vs. a dish radar, a solar/lunar exclusion cone, a minimum-range floor and altitude-band affinity, a
cue-dependent tasking precondition, a multi-receiver passive-RF network, and a satellite-hosted
sensor that follows its host's orbit). `FR-1600`'s own family preamble states the goal directly:
"complements, and does not duplicate," the generic access model and the `FR-3200` tasking-workflow
family.

## Scope

**In scope:** the six leaves' own access-predicate/effectiveness refinements — `FR-1610` (fence/dish
beam-mode variants), `FR-1620` (solar/lunar exclusion angle), `FR-1630` (min-range floor and
altitude-band affinity), `FR-1640` (cue-dependent tasking precondition), `FR-1650` (passive-RF
network fix), `FR-1660` (hosted-sensor orbit-following).

**Out of scope (named, not silently absorbed):** sensor tasking contention/arbitration (`FR-3200`
family, `FS-104`); the `BEAM_MODES` payload-type coverage gap for `weather`/`mw` payloads (a
pre-existing, separately tracked gap, `R109` §3 "genuine coverage gap"); the RIC-frame view and
CATS-angle overlay (`docs/pipeline/backlog.md` `BL-0107`/`BL-0111`, not yet baselined as FRs at the
time of this document).

## Requirements Implemented

- `FR-1610` — Fence/dish radar beam-mode variants.
- `FR-1620` — Optical sensor solar/lunar exclusion angle.
- `FR-1630` — Space-based sensor minimum-range floor and altitude-band affinity.
- `FR-1640` — Cue-dependent sensor tasking precondition.
- `FR-1650` — Passive-RF multilateration sensor network.
- `FR-1660` — Satellite-hosted sensor follows host orbit.

## User Workflows

1. **White Cell authors a fence-variant sensor in a vignette.** The vignette's sensor definition
   declares a wide-field-of-regard, low-gain beam-mode entry (`FR-1610`) alongside the existing
   narrow-beam entries `FR-1220`'s beam-mode trade already supports; no new authoring surface beyond
   the existing beam-mode table.
2. **White Cell authors a ground-optical sensor with an exclusion angle.** The sensor definition
   declares `exclusion_angle_deg` (`FR-1620`); an operator tasking that sensor sees the access
   window rejected whenever the excluded body falls inside the declared radius, on top of the
   existing lighting predicate.
3. **White Cell authors a space-based sensor with a range/altitude-band affinity.** The sensor
   definition declares `min_range_km` and/or `altitude_band_affinity` (`FR-1630`); an operator
   tasking that sensor against a too-close target is rejected, and against an out-of-band target
   sees degraded effectiveness rather than a hard rejection.
4. **An operator tasks a cue-dependent (e.g. laser-ranging) sensor.** The order panel (or its
   `dry_run` preview) rejects or pre-disables a tasking request against a target with no existing
   `Track` (`FR-1640`); the same sensor tasked against a target with an existing `Track` proceeds
   normally.
5. **An operator (or the SSN request path) tasks a passive-RF sensor network.** The system checks
   whether the target is currently emitting and whether at least 3 (2D) or 4 (3D) member receivers
   of the declared network simultaneously have access; a fix is produced only when both hold
   (`FR-1650`).
6. **An operator issues an observe order naming a hosted sensor's host asset, or the sensor itself.**
   Either name resolves to the same access/effectiveness computation, using the host Asset's current
   propagated orbital state, including after a manoeuvre (`FR-1660`).

## System Behaviour

- **Normal path — `FR-1610`.** A ground-kind sensor's access computation reads its declared
  beam-mode parameterization; a wide-field-of-regard entry produces access against more
  simultaneously-transiting objects at lower per-object gain, a narrow-beam entry the reverse —
  exactly the existing swath/gain trade `FR-1220`/`R109` §3 already generalizes.
- **Normal path — `FR-1620`.** The existing lighting predicate (target sunlit, site dark) is
  evaluated first; if it passes, the exclusion-angle check evaluates the Sun's (and, if declared,
  the Moon's) angular separation from the sensor's boresight against the declared radius, rejecting
  the window if inside it.
- **Edge case — `FR-1620`, no declared exclusion angle.** The sensor behaves exactly as today
  (lighting-only predicate), per `FR-1620`'s own Preconditions.
- **Normal path — `FR-1630`.** A space-based sensor's effectiveness computation (`effective_gain`)
  is evaluated only after a minimum-range check; below the declared floor the observation is
  rejected outright; above it, gain is further scaled down if the target lies outside the declared
  altitude band, composing with (not replacing) the existing off-nadir `look_angle_deg` degradation.
- **Normal path — `FR-1640`.** Plan-time validation (and its `dry_run` mirror) checks whether the
  named target has an existing `Track` in the tasking cell's `TrackCatalog` before permitting a
  cue-dependent sensor's tasking; absent one, the request is rejected (or pre-disabled in the UI)
  with a reason distinguishable from a generic access-window failure.
- **Normal path — `FR-1650`.** The declared network's member receivers' own individual access is
  evaluated per receiver; a fix is computed only if (a) the target's emission state is currently
  "on" and (b) the count of receivers with simultaneous access meets the 2D/3D threshold.
- **Edge case — `FR-1650`, non-emitting target.** No fix is produced regardless of receiver count or
  geometry (`FR-1650`'s own Postconditions) — this is a target-state precondition, not a geometry
  failure.
- **Normal path — `FR-1660`.** A hosted sensor's position is derived from its host Asset's current
  propagated orbital state at every access-window computation, including immediately after a
  manoeuvre (`FR-1310`) is applied to the host — never a stale, pre-manoeuvre position. An observe
  order naming either the host Asset or the hosted sensor directly resolves to the identical
  computation.

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `engine/entities.py` (`Sensor`) | Owns the new declarative fields this Feature introduces: a beam-mode reference for `FR-1610`, `exclusion_angle_deg` for `FR-1620`, `min_range_km`/`altitude_band_affinity` for `FR-1630`, `requires_cue` for `FR-1640`, a host-Asset reference for `FR-1660`. |
| `engine/access.py` (`AccessProvider`) | Owns `_observation_predicate`'s existing ground/space-based branching; extended with the exclusion-angle check (`FR-1620`) and the minimum-range/altitude-band check (`FR-1630`), layered on top of, not replacing, the existing lighting/off-nadir logic. |
| `engine/isr.py` | Owns `BEAM_MODES`/`effective_gain()`; extended with the fence/dish beam-mode entry (`FR-1610`) and the altitude-band-affinity gain degradation (`FR-1630`). |
| `engine/orders.py` (`OrderSystem`) | Owns plan-time validation and `dry_run()`; extended to check `requires_cue`/existing-`Track` (`FR-1640`) before permitting a cue-dependent sensor's tasking. |
| `engine/custody.py` (`Track`/`TrackCatalog`) | Consulted (not modified) by `FR-1640`'s cue-existence check and produced-into by `FR-1650`'s network fix. |
| `engine/ssn.py` (Mock SSN) | Owns the network-aggregation pattern `FR-1650` reuses for the passive-RF sensor network's multi-receiver fix, per `R109` §3.10's own recommendation. |

## Interfaces Used

- `INT-0008` (SessionManager → Engine Clock/Scheduler/EventLog/OrderSystem) — the existing interface
  every one of the six leaves' access/effectiveness computation operates through; no new interface.
- `INT-0009`/`INT-0010` (CellController/SessionAPI → Mock SSN / Mock SSN → Engine delivery) — the
  existing interfaces `FR-1650`'s network-fix reuses, per its own citation of the SSN aggregation
  pattern.
- `INT-0007` (CellController → Engine Custody) — the existing interface `FR-1640`'s cue-existence
  check and `FR-1650`'s fix-delivery-into-`TrackCatalog` both operate through.

## Data Model Changes

- `Sensor` (domain model, `GDS-04` §1.x sensor entity) gains: a beam-mode reference already
  generalized by the existing swath/resolution/power/duty-cycle/gain schema (`FR-1610`, no new
  field shape, a new table entry only); `exclusion_angle_deg: Optional[float]` (`FR-1620`);
  `min_range_km: Optional[float]`, `altitude_band_affinity: Optional[str]` (`FR-1630`);
  `requires_cue: bool` (`FR-1640`); a host-Asset reference, additive and absent for every
  non-hosted sensor (`FR-1660`). All six additions are optional/additive — a sensor declaring none
  of them behaves exactly as today.
- No change to `Track`/`TrackCatalog`'s own shape — `FR-1640`/`FR-1650` only read/write through the
  existing model.

## State Changes

None to session/persistent engine state beyond the additive `Sensor` fields above, which are
vignette-authored (or force-added) declarative data, not runtime-mutable session state.

## Error Handling

- `FR-1620`: an access window rejected by the exclusion-angle check carries a reason distinguishable
  from the existing lighting-predicate rejection (Open Question 1).
- `FR-1630`: a tasking below the minimum-range floor is rejected outright (not merely
  gain-degraded); a tasking outside the declared altitude band is accepted with degraded gain, not
  rejected.
- `FR-1640`: a cue-dependent sensor tasked against a target with no `Track` is rejected (or
  pre-disabled via `dry_run`) with a reason distinguishable from a generic access-window failure.
- `FR-1650`: fewer than 3 (2D)/4 (3D) receivers with simultaneous access, or a non-emitting target,
  both produce "no fix" — `FR-1650`'s own text does not distinguish these two failure causes in its
  observable contract (Open Question 2).

## Performance Considerations

None named by `FR-1610`-`FR-1660` beyond what `FR-1220`'s existing access-window computation already
respects — each leaf is a bounded per-sensor or small-per-network additional check, not a new
computational class.

## Security Considerations

`ADR-0004` (fog-of-war at the boundary): `FR-1650`'s network fix is delivered into the requesting
cell's own `TrackCatalog` exactly as the existing SSN delivery path already does — no leaf in this
Feature introduces a new ground-truth-read path bypassing `CellController`.

## Acceptance Criteria

1. Given a wide-field-of-regard sensor and a narrow-beam sensor observing the same volume, the wide
   variant detects more transiting objects at lower per-object gain than the narrow variant.
   *(`FR-1610`)*
2. Given a sensor with a declared exclusion angle and a geometry placing the Sun inside that angle,
   the access window is rejected; given the Sun outside that angle, the window is granted per the
   existing lighting predicate. *(`FR-1620`)*
3. Given a sensor with a declared minimum-range floor, an observation attempt closer than that floor
   is rejected; given a declared altitude-band affinity, effective gain against a target outside the
   declared band is measurably lower than against one inside it. *(`FR-1630`)*
4. Given a cue-dependent sensor and a target with no existing `Track`, the tasking request is
   rejected; given the same sensor and a target with an existing `Track`, the tasking request is
   accepted (subject to the normal access-window check). *(`FR-1640`)*
5. Given an emitting target and exactly 3 member receivers with access, a 2D fix is produced; given
   4 member receivers with access, a 3D fix is produced; given a non-emitting target, no fix is
   produced regardless of receiver count. *(`FR-1650`)*
6. Given a hosted sensor and a manoeuvre applied to its host Asset, the hosted sensor's subsequent
   access-window computation reflects the post-manoeuvre orbital state; an observe order naming the
   host Asset and one naming the hosted sensor directly produce the same result. *(`FR-1660`)*

## Verification Plan

- Criterion 1 — Test: two sensors sharing a beam-mode table, differing only in the wide/narrow
  entry, observing an identical multi-object scene.
- Criterion 2 — Test: parametrized over Sun-angle geometries crossing the declared exclusion
  boundary.
- Criterion 3 — Test: parametrized over range (below/above the floor) and altitude-band membership.
- Criterion 4 — Test: a cue-dependent sensor tasked with and without a pre-existing `Track`.
- Criterion 5 — Test: parametrized over receiver count (2/3/4) and target emission state (on/off).
- Criterion 6 — Test: a hosted sensor's access window computed before and after a host-Asset
  manoeuvre; an observe order naming each of the two identifiers.

## Dependencies

- `FS-104` (SDA Tasking) — the tasking-contention workflow these access/effectiveness refinements
  sit underneath; not a build dependency, a scope boundary (see Scope, Out of scope).
- `FS-103` (Custody Management) — `FR-1640`'s cue-existence check and `FR-1650`'s fix delivery both
  read/write through `Track`/`TrackCatalog`, unchanged by this Feature.

## Risks

- **Ambiguity risk (Open Questions 1-2 below).** Two genuine gaps in the requirements' own
  observable-error-contract text.
- **`R109` §3.7's single-source figure (`docs/pipeline/backlog.md` `BL-0103`).** The ~90°
  solar-phase exclusion figure informs only a plausible *default* for `exclusion_angle_deg`, never
  a hard-coded constant — `FR-1620` itself requires the field to be configurable, so this risk does
  not block implementation, only the choice of a shipped default value.
- **`BEAM_MODES` coverage gap (pre-existing, `R109` §3, not new to this Feature).** `FR-1610`'s new
  fence/dish entries must be added to the existing three-payload-type `BEAM_MODES` table — this
  Feature does not itself need to close the separately-tracked `weather`/`mw` gap, but an
  Implementation Package should not conflate the two.

## Open Questions

1. **What distinguishes an exclusion-angle rejection from a lighting-predicate rejection in the
   observable error contract?** `FR-1620`'s own Acceptance Criteria state both outcomes (rejected
   vs. granted) but not whether the two rejection *reasons* must be distinguishable to the operator
   (e.g. for a UI message). Needs a `04-requirements-engineering` amendment or an
   `07-implementation-planning` design decision — this document does not invent one.
2. **Does `FR-1650`'s "no fix" observable state distinguish an insufficient-receiver-count cause
   from a non-emitting-target cause?** Neither is stated as needing to be distinguishable in
   `FR-1650`'s own text; an Implementation Package needs a concrete answer before committing to a
   specific "why no fix" surfaced reason (or the deliberate absence of one).

## Related ADRs

`ADR-0011` (six access channels taxonomy — every leaf here refines, none replaces, the
`sensor_observation` channel this taxonomy already names); `ADR-0010` (Mock SSN is internal, not
external — `FR-1650`'s network-fix reuse of the SSN aggregation pattern stays consistent with this).

## Related Interfaces

`INT-0011` (Session Layer → Content & Data, vignette/template load) — unrelated to this Feature's
own runtime access/effectiveness computation, listed only because it is where a vignette's new
`Sensor` fields (this Feature's six additive fields) are authored/loaded.
