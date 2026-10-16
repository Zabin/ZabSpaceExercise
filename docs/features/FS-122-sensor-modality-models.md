> **Document ID:** FS-122
> **Version:** 1.1 (2026-10-15 — adds `FR-1670`, the CATS illumination phase-angle refinement, the
> seventh leaf `FEAT-1600` bundles; v1.0 covered `FR-1610`-`FR-1660`, now built and `VERIFIED`)
> **Status:** ✅ Ready for implementation planning — `FR-1670` only (`FR-1610`-`FR-1660` are built,
> [IP-1220](../implementation/packages/IP-1220-sensor-modality-models.md) ✅ `VERIFIED`)
> **Approved Feature (v1.1):** [`FEAT-1600`](../feature-planning/03-feature-catalog.md) (Sensor
> Modality-Specific Access & Effectiveness Models; Included Requirements `FR-1610`-`FR-1670`). A
> Feature Catalog now exists (run #83, 2026-10-03), so the v1.0 note below about its absence
> describes the state when v1.0 was drafted.
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
> **Referenced By:** [IP-1041](../implementation/packages/IP-1041-observe-order-reason-and-param-remediation.md) (🟢 READY, observe-order remediation), [IP-1222](../implementation/packages/IP-1222-sensor-modality-wiring-remediation.md)
> (remediation package for `FR-1610`/`FR-1630`/`FR-1640` wiring, ✅ `VERIFIED` 2026-10-16 via
> [VR-1222](../implementation/verification/VR-1222-sensor-modality-wiring-remediation.md)),
> [IP-1221](../implementation/packages/IP-1221-cats-phase-angle-observation-gain.md)
> (Implementation Package for `FR-1670`, v1.1, ✅ `VERIFIED` 2026-10-16 via `VR-1221`),
> [IP-1220](../implementation/packages/IP-1220-sensor-modality-models.md)
> (Implementation Package, ✅ `VERIFIED`, [VR-1220](../implementation/verification/VR-1220-sensor-modality-models.md)),
> [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0073` (item B7),
> `BL-0083` (item B17), [docs/requirements/01-functional-requirements.md](../requirements/01-functional-requirements.md)
> `FR-1610`-`FR-1670`, [docs/reviews/requirements-update-should-tier-batch.md](../reviews/requirements-update-should-tier-batch.md),
> (v1.1) `BL-0122`, `BL-0151`, `BL-0152`, [docs/reviews/requirements-update-ric-cats-batch.md](../reviews/requirements-update-ric-cats-batch.md)
> **Produces:** five new sensor-modality access/effectiveness models (fence/dish radar, optical
> exclusion angle, space-based min-range/altitude-band, cue-dependent tasking, passive-RF
> multilateration) plus one hosted-sensor orbit-following model, satisfying `FR-1610`-`FR-1660` in
> full except where an Open Question below blocks full closure; (v1.1) a seventh, the passive-EO
> illumination phase-angle (CATS) effectiveness refinement, satisfying `FR-1670`
> **Feature Mapping:** FS-122 (this document)
> **Related Topics:** [FS-103](FS-103-custody-management.md) (custody/Track — `FR-1640`'s cue
> precondition and `FR-1650`'s network-fix output both interact with `Track`); (v1.1)
> [FS-130](FS-130-ric-frame-view-and-cats-overlay.md) (the display-only CATS overlay, `FR-8220`,
> which owns the shared phase-angle function this Feature reuses);
> [`R109` v1.3](../research/encyclopedia/R109-sensor-operations.md) §3.11 (CATS grounding)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template.*

# FS-122 — Sensor Modality Models (Fence/Dish Radar, Exclusion Angle, Range/Altitude-Band,
Cue-Dependence, Passive-RF Network, Hosted Sensor)

## Purpose

Give the six new sensor-modality requirements one coherent home: each adds a real-world sensor
behavior `FR-1220`'s generic six-channel access computation does not itself distinguish (a fence
vs. a dish radar, a solar/lunar exclusion cone, a minimum-range floor and altitude-band affinity, a
cue-dependent tasking precondition, a multi-receiver passive-RF network, and a satellite-hosted
sensor that follows its host's orbit). v1.1 adds a seventh (`FR-1670`): a passive electro-optical
sensor's observation becomes less effective when the target is poorly lit *as seen from that
sensor*, measured by the Sun-target-observer illumination phase angle (the "CATS angle", `R109`
§3.11). `FR-1600`'s own family preamble states the goal directly:
"complements, and does not duplicate," the generic access model and the `FR-3200` tasking-workflow
family.

## Scope

**In scope:** the six leaves' own access-predicate/effectiveness refinements — `FR-1610` (fence/dish
beam-mode variants), `FR-1620` (solar/lunar exclusion angle), `FR-1630` (min-range floor and
altitude-band affinity), `FR-1640` (cue-dependent tasking precondition), `FR-1650` (passive-RF
network fix), `FR-1660` (hosted-sensor orbit-following); (v1.1) `FR-1670` (illumination phase-angle
refinement for any passive EO sensor, ground- or space-based).

**Out of scope (named, not silently absorbed):** sensor tasking contention/arbitration (`FR-3200`
family, `FS-104`); the `BEAM_MODES` payload-type coverage gap for `weather`/`mw` payloads (a
pre-existing, separately tracked gap, `R109` §3 "genuine coverage gap"); the RIC-frame view and
its display-only CATS-angle readout (`FR-8210`/`FR-8220`, [FS-130](FS-130-ric-frame-view-and-cats-overlay.md),
built by `IP-1300`). FS-130 shows the phase angle to a user; `FR-1670` uses the same angle to
change an observation's effectiveness. Showing the angle in any tasking or preview surface is not
required by `FR-1670` and is not specified here.

## Requirements Implemented

- `FR-1610` — Fence/dish radar beam-mode variants.
- `FR-1620` — Optical sensor solar/lunar exclusion angle.
- `FR-1630` — Space-based sensor minimum-range floor and altitude-band affinity.
- `FR-1640` — Cue-dependent sensor tasking precondition.
- `FR-1650` — Passive-RF multilateration sensor network.
- `FR-1660` — Satellite-hosted sensor follows host orbit.
- `FR-1670` — Phase-angle (CATS) based access-window refinement for passive EO sensors *(v1.1)*.

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
7. **(v1.1) White Cell authors a passive EO sensor with a usable phase-angle range.** The vignette's
   sensor definition (a ground-optical sensor, or a space-based or hosted optical sensor) declares
   a usable phase-angle range in degrees (`FR-1670`). `R109` §3.11's recommended starting values
   are 0°–90° for a ground-based sensor and 0°–150° for a space-based one (see Data Model
   Changes). A Blue or Red operator then tasks that sensor with an ordinary observe order, with
   nothing new to enter. When the target is well lit as seen from the sensor, the observation is as
   effective as before. When the target is backlit beyond the declared range, the order still
   executes in its window but the observation is weaker: it raises the cell's track confidence
   less. A sensor that declares no range behaves exactly as today.

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
- **Normal path — `FR-1670` (v1.1).** For a sensor that declares a usable phase-angle range, the
  phase angle is computed at the observation instant: the scheduled time inside the access window
  at which the observe executes (`FR-1670` "at the time of observation"). It is the angle at the
  target between the target→Sun direction and the target→sensor direction, from 0° (target face
  fully lit as seen by the sensor) to 180° (backlit). The sensor position is the ground site for a
  ground sensor, its own orbit for a space-based sensor, and its host's current orbit for a hosted
  sensor (`FR-1660`). The angle is computed by the engine's one existing shared phase-angle
  function (`engine/sun.py` `cats_phase_angle_deg`, built by `IP-1300` for `FR-8220`). `BL-0152`
  requires both uses to share it, and that function's own docstring names `FR-1670` as its
  intended second caller, so no second phase-angle computation is introduced.
  - **Inside the declared range** (bounds inclusive): the observation is unaffected by this
    predicate (`FR-1670` Acceptance Criteria).
  - **Outside the declared range:** the observation's effectiveness is degraded rather than its
    window rejected. `FR-1670` allows either; `R109` §3.11 grounds a smooth degradation ("not a
    hard cliff") as real practice, so this spec chooses degradation. The degradation is
    continuous at the range bound (no jump at the limit). It does not increase as the angle moves
    further outside the range. It is strictly below the unaffected value for every angle outside
    the range. The exact curve is an `07-implementation-planning` design decision (Open Question
    3).
  - **Composition:** effectiveness enters through the same observation-gain seam `FR-1630`'s
    altitude-band affinity already uses. It is applied in addition to — never in place of — the
    existing look-angle and altitude-band degradations.
- **Edge case — `FR-1670`, window already rejected.** The existing lighting predicate (`FR-1220`:
  target sunlit and, for a ground sensor, site dark) and, where declared, the exclusion angle
  (`FR-1620`) run first and are unchanged. A window they reject stays rejected, and the phase-angle
  refinement never re-admits one (`FR-1670` Postconditions: composes with, never replaces).
- **Edge case — `FR-1670`, no declared range.** The sensor behaves exactly as today, per
  `FR-1670`'s own Preconditions. In particular, `R109` §3.11's recommended values are **not**
  applied to a sensor that does not declare a range, because that would change every existing
  optical sensor's behaviour, which `FR-1670` forbids.
- **Edge case — `FR-1670`, coincident sensor and target positions.** The shared function treats
  the angle as undefined there. This geometry cannot occur inside a valid access window (a
  space-based window already requires line of sight at nonzero range); the implementation must not
  let it raise mid-handler (Error Handling).

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `engine/entities.py` (`Sensor`) | Owns the new declarative fields this Feature introduces: a beam-mode reference for `FR-1610`, `exclusion_angle_deg` for `FR-1620`, `min_range_km`/`altitude_band_affinity` for `FR-1630`, `requires_cue` for `FR-1640`, a host-Asset reference for `FR-1660`. |
| `engine/access.py` (`AccessProvider`) | Owns `_observation_predicate`'s existing ground/space-based branching; extended with the exclusion-angle check (`FR-1620`) and the minimum-range/altitude-band check (`FR-1630`), layered on top of, not replacing, the existing lighting/off-nadir logic. |
| `engine/isr.py` | Owns `BEAM_MODES`/`effective_gain()`; extended with the fence/dish beam-mode entry (`FR-1610`) and the altitude-band-affinity gain degradation (`FR-1630`). |
| `engine/orders.py` (`OrderSystem`) | Owns plan-time validation and `dry_run()`; extended to check `requires_cue`/existing-`Track` (`FR-1640`) before permitting a cue-dependent sensor's tasking. |
| `engine/custody.py` (`Track`/`TrackCatalog`) | Consulted (not modified) by `FR-1640`'s cue-existence check and produced-into by `FR-1650`'s network fix. |
| `engine/ssn.py` (Mock SSN) | Owns the network-aggregation pattern `FR-1650` reuses for the passive-RF sensor network's multi-receiver fix, per `R109` §3.10's own recommendation. |
| `engine/entities.py` (`Sensor`) — v1.1 | Owns the one new optional declarative field for `FR-1670`: the sensor's usable phase-angle range. |
| `engine/sun.py` — v1.1 | Owns `cats_phase_angle_deg`, consumed unchanged as the single phase-angle computation (`BL-0152`). |
| `engine/orders.py` (`OrderSystem`) / `engine/isr.py` — v1.1 | Own the observation-gain computation (`effective_gain`, the `FR-1630` precedent seam); extended to apply the `FR-1670` degradation for a sensor that declares a range, at the observation instant. |
| `engine/access.py` (`AccessProvider`) — v1.1 | Unchanged by `FR-1670`: window geometry, lighting and exclusion-angle rejection stay as they are. Consulted for the observer position the existing predicates already resolve (ground site, sensor orbit, host orbit). |

## Interfaces Used

- `INT-0008` (SessionManager → Engine Clock/Scheduler/EventLog/OrderSystem) — the existing interface
  every one of the six leaves' access/effectiveness computation operates through; no new interface.
- `INT-0009`/`INT-0010` (CellController/SessionAPI → Mock SSN / Mock SSN → Engine delivery) — the
  existing interfaces `FR-1650`'s network-fix reuses, per its own citation of the SSN aggregation
  pattern.
- (v1.1) `FR-1670` operates entirely inside the engine's observe path under `INT-0008`, the only
  interface the RTM lists for it. No new interface, route or UI control is needed.
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
- (v1.1) `Sensor` gains one more optional, additive field for `FR-1670`: a usable phase-angle
  range, a lower and an upper bound in degrees within [0, 180], absent by default. The field name
  and shape are an `07` decision, following the six v1.0 fields' precedent. `R109` §3.11's
  single-source, ballpark figures (0°–90° ground, 0°–150° space-based) are the **recommended values
  for vignette authors**, used in this spec's acceptance criteria. They are not an implicit default
  (`BL-0151`; see the System Behaviour edge case). No change to `Track`, `Asset` or `WorldState`.

## State Changes

None to session/persistent engine state beyond the additive `Sensor` fields above, which are
vignette-authored (or force-added) declarative data, not runtime-mutable session state. This also
holds for v1.1's `FR-1670` field. Its effect lands only in the observation's existing outcome
(track confidence), through the existing observe handler.

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
- (v1.1) `FR-1670`: an observation degraded by the phase-angle refinement is not an error. The
  order executes normally and only its effectiveness is lower, so no rejection reason is surfaced.
  The phase-angle computation must never raise inside the deterministic observe handler; a
  geometry the shared function cannot evaluate is treated as unaffected (Edge case, coincident
  positions). A declared range that is malformed (lower bound above upper, or outside [0, 180]), or
  one declared on a sensor that is not passive EO, is Open Question 4.

## Performance Considerations

None named by `FR-1610`-`FR-1660` beyond what `FR-1220`'s existing access-window computation already
respects — each leaf is a bounded per-sensor or small-per-network additional check, not a new
computational class.
(v1.1) `FR-1670` adds one phase-angle evaluation per observation of a sensor that declares a range.
It is pure and deterministic (positions and sim time only, no RNG, no wall clock), so the Phase-1
determinism gate and replay (`NFR-1500`) are unaffected.

## Security Considerations

`ADR-0004` (fog-of-war at the boundary): `FR-1650`'s network fix is delivered into the requesting
cell's own `TrackCatalog` exactly as the existing SSN delivery path already does — no leaf in this
Feature introduces a new ground-truth-read path bypassing `CellController`. (v1.1) `FR-1670`'s
phase angle is computed engine-side from true positions, like every other access and lighting
computation. A cell only sees the result through its own track's confidence, and the angle is
never added to any cell-scoped response.

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
7. *(v1.1)* Given a ground-optical sensor declaring a usable range of 0°–90°, and an observation
   whose phase angle at the observation instant is inside that range, the resulting observation
   gain equals the gain the same sensor produces with no declared range (all else equal). Given a
   phase angle outside the range, the gain is strictly lower. *(`FR-1670`)*
8. *(v1.1)* The degradation is continuous at the bound: approaching the upper bound from outside,
   the gain tends to the unaffected value. It never increases as the angle moves further beyond
   the bound. *(`FR-1670`, `R109` §3.11 "not a hard cliff")*
9. *(v1.1)* The same holds for a space-based sensor declaring 0°–150°, and for a hosted sensor
   (observer position = host orbit, `FR-1660`). *(`FR-1670`)*
10. *(v1.1)* A window rejected by the lighting predicate or by a declared exclusion angle stays
    rejected whatever the phase angle. A sensor with no declared range produces results identical
    to before this version, for every shipped vignette. *(`FR-1670` Preconditions/Postconditions)*
11. *(v1.1)* The engine contains exactly one phase-angle computation (`cats_phase_angle_deg`),
    called by both the `FR-8220` overlay and the `FR-1670` refinement. *(`BL-0152`)*

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
- Criteria 7–9 (v1.1) — Test: the same sensor and target with and without a declared range,
  parametrized over geometries whose phase angle at the observation instant falls inside, at, and
  beyond the bound, for ground, space-based and hosted sensors.
- Criterion 10 (v1.1) — Test: a lit-window/exclusion-rejected geometry with a declared range, plus
  a regression run showing every shipped vignette's observe outcomes unchanged.
- Criterion 11 (v1.1) — Inspection/Test: extend `IP-1300`'s existing single-definition test to
  cover the new caller.

## Dependencies

- `FS-104` (SDA Tasking) — the tasking-contention workflow these access/effectiveness refinements
  sit underneath; not a build dependency, a scope boundary (see Scope, Out of scope).
- `FS-103` (Custody Management) — `FR-1640`'s cue-existence check and `FR-1650`'s fix delivery both
  read/write through `Track`/`TrackCatalog`, unchanged by this Feature.
- (v1.1) `FS-130` / `IP-1300` (✅ `VERIFIED`) — owns the shared `cats_phase_angle_deg` that
  `FR-1670` consumes. Build dependency satisfied. `FEAT-1600` depends on `FEAT-1200` (baseline
  access), which is built.

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
- **(v1.1) Single-source figure risk (`R109` §3.11, `BL-0151`).** The 0°–90°/0°–150° figures rest
  on one AMOS conference source. Because the range is author-declared and never an implicit
  default, a wrong figure affects only vignettes that adopt it, and it can be corrected in content.
- **(v1.1) Timing risk.** The existing observation gain is assembled when the observe payload is
  built against its chosen window. `FR-1670` requires the angle at the observation instant, so the
  package must evaluate it at the scheduled execution time, not at the issue time.
- **(v1.1) Content risk.** No shipped vignette declares a range, so `FR-1670` has no operator-visible
  effect until a vignette adopts it. Whether any should is a `08-vignette-development` content
  question, not this spec's.

## Open Questions

1. ~~**What distinguishes an exclusion-angle rejection from a lighting-predicate rejection in the
   observable error contract?**~~ **Closed (v1.1, by reference).** `04-requirements-engineering`
   (2026-10-15, [parked-questions batch](../reviews/requirements-update-parked-questions-batch.md),
   `BL-0113`) found that `FR-1620` does not require distinguishable reasons. As built, both rejections
   suppress the window at the same predicate layer, which satisfies `FR-1620`. No amendment; a
   distinct operator-visible reason would be a new feature through `00-intake`.
2. **Does `FR-1650`'s "no fix" observable state distinguish an insufficient-receiver-count cause
   from a non-emitting-target cause?** Neither is stated as needing to be distinguishable in
   `FR-1650`'s own text; an Implementation Package needs a concrete answer before committing to a
   specific "why no fix" surfaced reason (or the deliberate absence of one).
3. **(v1.1) The exact degradation curve outside the declared phase-angle range (`BL-0151` residual).**
   `R109` §3.11 grounds a smooth degradation but gives no function, and `FR-1670` states none. This
   spec fixes the contract: unaffected inside the range, continuous at the bound, non-increasing
   beyond it, strictly lower outside it. It does not pick the shape (for example, how far below the
   unaffected value the gain falls at 180°). That is an `07-implementation-planning` design
   decision, to be recorded in its package; if a cited shape is wanted, route it to
   `02-research-ow-orbital-mechanics` first.
4. **(v1.1) Malformed or misplaced range declarations.** `FR-1670` does not say what happens when a
   declared range has its lower bound above its upper bound, falls outside [0, 180], or is declared
   on a sensor that is not passive EO (e.g. a ground radar). The v1.0 precedent (`FR-1620`'s
   `exclusion_angle_deg`) applies the field without a kind check. Options: reject at vignette load,
   or ignore it. This is an `07` design decision; it does not block the normal path.
5. **(v1.1) What counts as "passive electro-optical" in the engine's sensor model.** `Sensor.kind`
   distinguishes `ground_optical` / `ground_radar` / `space_based`, and `needs_lighting` marks the
   optical lighting behaviour (the engine's own optical flag). This spec reads "passive EO" as a
   sensor with `needs_lighting` set, including a space-based or hosted one. If
   `04-requirements-engineering` intended a narrower or broader reading, `FR-1670` should say so;
   until then, `07` should adopt this reading.

## Related ADRs

`ADR-0011` (six access channels taxonomy — every leaf here refines, none replaces, the
`sensor_observation` channel this taxonomy already names); `ADR-0010` (Mock SSN is internal, not
external — `FR-1650`'s network-fix reuse of the SSN aggregation pattern stays consistent with this).

## Related Interfaces

`INT-0011` (Session Layer → Content & Data, vignette/template load) — unrelated to this Feature's
own runtime access/effectiveness computation, listed only because it is where a vignette's new
`Sensor` fields (this Feature's six additive fields) are authored/loaded.
