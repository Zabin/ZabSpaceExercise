# Functional Requirements Baseline

> **Status:** Draft — amended (strategic-review reconciliation, 2026-07; no numbered FR added or
> modified — see "Strategic review reconciliation" section near the end of this document and
> [`reviews/requirements-update-report.md`](../reviews/requirements-update-report.md)); further
> amended (DOM-002/004/005 backfill, 2026-07; no numbered FR added — see "DOM-002/004/005 backfill"
> section near the end of this document and
> [`reviews/requirements-domain-backfill-report.md`](../reviews/requirements-domain-backfill-report.md));
> further amended (`ADR-0032`/`ADR-0033` conflict resolution, 2026-07; **two numbered FR leaves
> added** — `FR-10110`, `FR-10210`, promoted from `CR-19`/`CR-20` — see "ADR-0017/ADR-0029 conflict
> resolution" section near the end of this document).
> **ADR range now ADR-0001 through ADR-0033** (32 `Accepted`, 1 `Superseded` — `ADR-0029` by
> `ADR-0033`).
> **Authoritative inputs (per explicit instruction for this baseline):**
> [`research/encyclopedia/INDEX.md`](../research/encyclopedia/INDEX.md) (Encyclopedia),
> [`architecture/01-concept-of-operations.md`](../architecture/01-concept-of-operations.md) (GDS-01,
> ConOps), [`architecture/02-system-context.md`](../architecture/02-system-context.md) (GDS-02,
> System Context), [`architecture/03-architecture.md`](../architecture/03-architecture.md) (GDS-03,
> System Architecture), [`architecture/04-domain-model.md`](../architecture/04-domain-model.md)
> (GDS-04, Domain Model), [`design/05-interface-control-document.md`](../design/05-interface-control-document.md)
> (ICD), [`architecture/adr/INDEX.md`](../architecture/adr/INDEX.md) (ADR-0001 through ADR-0033, all
> `Accepted` except `ADR-0029`, `Superseded` by `ADR-0033`), [`architecture/strategic-assumptions-register.md`](../architecture/strategic-assumptions-register.md)
> (added 2026-07).
> **Priority scale used throughout:** MoSCoW (Must / Should / Could / Won't).

## A note on a pre-existing requirement tag scheme — read before using this document

`docs/build-spec/02-requirements-and-operations.md` §5–6 contains a legacy, pre-GDS requirement-tag
scheme: **FR-E1–E8** (engine), **FR-B1–B5** (bus/payload), **FR-P1–P6** (planning/tasking),
**FR-W1–W7** (White Cell), **FR-S1–S3** (scenario builder), **FR-L1–L2** (logging), and **OR-1–OR8**
(hot-seat operations). **Corrected 2026-07 (was previously stated as "the build spec wins" —
see `reviews/requirements-update-report.md`, which fixes this document to match the correction
[`ADR-0031`](../architecture/adr/ADR-0031-governance-record-consistency.md) already made to the
identically-stale language in `architecture/00-vision.md` §7):** per `CLAUDE.md`'s "Authoritative
source & reading order" and `architecture/INDEX.md`'s blanket-supersession declaration,
`docs/architecture/` (the GDS ladder) is authoritative over `docs/build-spec/` in its entirety,
including for GDS-05 specifically (`architecture/05-functional-requirements.md`, `✅ Authored,
merge gate closed`, per `ROADMAP.md`) — build-spec/02 §5–6 is **legacy reference only, not
binding**. This document is **not** a second, competing requirements baseline: it is a hierarchical
elaboration of the same underlying capabilities, re-derived independently from the GDS-01–04/ICD/ADR
baseline named above (not from build-spec/02 itself, which is intentionally excluded from this
pass's authoritative-input list), and **cross-referenced** to the corresponding build-spec tag(s) in
each requirement's **Source Documents** field where a correspondence exists, purely for historical
traceability — the build-spec tag carries no binding weight where it conflicts with this document,
GDS-05, or any other authored GDS level.

This document is accompanied by a Non-Functional Requirements baseline
([`02-non-functional-requirements.md`](02-non-functional-requirements.md)) and a Requirements
Traceability Matrix ([`03-requirements-traceability-matrix.md`](03-requirements-traceability-matrix.md));
a separate standalone Requirements Review document was not produced for this baseline (see
[`../reviews/requirements-review.md`](../reviews/requirements-review.md) and
[`../reviews/requirements-baseline-review.md`](../reviews/requirements-baseline-review.md) for the
review passes actually run against it).

---

## FR-1000 — Simulation Engine Core & Determinism

### FR-1100 — Deterministic, sub-stepped simulation clock

#### FR-1110 — Single authoritative simulation clock

- **ID:** FR-1110
- **Title:** Maintain a single authoritative simulation clock
- **Description:** The system shall maintain exactly one authoritative simulated-UTC clock per
  session, and shall advance world state strictly as a function of the current simulated time,
  the current state, and the ordered event log.
- **Rationale:** A wargame's outcomes must be reproducible and auditable; a single clock with no
  side-channel time source is the precondition for determinism (GDS-01 §7; GDS-03 §4 "Determinism").
- **Priority:** Must
- **Inputs:** Current `WorldState`; ordered `EventLog`; a clock-advance request.
- **Outputs:** An updated `WorldState` at the new simulated time.
- **Preconditions:** A constructed Session with an initialized clock.
- **Postconditions:** The simulated clock value strictly increases (or is rewound under White Cell
  control, FR-4300); no component other than the White Cell control interface advances it.
- **Acceptance Criteria:** Given a session at sim time T, when any non-White-Cell interface is
  invoked, the simulated clock value is unchanged after the call returns.
- **Verification Method:** Test
- **Dependencies:** FR-4300
- **Source Documents:** GDS-03 §4 "A single clock owner"; GDS-01 §7; ADR-0016.
- **Related ADRs:** ADR-0016
- **Related Interfaces:** INT-0002, INT-0008
- **Related Requirements:** FR-1120, FR-1130, FR-4300

#### FR-1120 — Deterministic replay

- **ID:** FR-1120
- **Title:** Reproduce identical state from initial state, event log, and seed
- **Description:** The system shall guarantee that replaying an identical ordered event log and
  random seed against an identical initial state produces byte-identical world state at every
  point in the replay.
- **Rationale:** Determinism is the load-bearing invariant underpinning rewind, undo,
  branch-from-rewind, and AAR replay (GDS-01 §7; ADR-0002).
- **Priority:** Must
- **Inputs:** Initial `WorldState`; ordered `EventLog`; RNG seed.
- **Outputs:** Reconstructed `WorldState` at any point in the replay.
- **Preconditions:** A valid, ordered `EventLog` and seed exist.
- **Postconditions:** The reconstructed state is identical, field-for-field, to the originally
  produced state at that point.
- **Acceptance Criteria:** Given the same `(initial_state, event_log, seed)` tuple replayed twice,
  the resulting `WorldState` is byte-identical both times.
- **Verification Method:** Test
- **Dependencies:** FR-1110, FR-7100
- **Source Documents:** GDS-01 §7; GDS-03 §2.1, §4 "Determinism"; build-spec/02 §5.1 FR-E2 (binding
  statement); ADR-0002.
- **Related ADRs:** ADR-0002
- **Related Interfaces:** INT-0008, INT-0014
- **Related Requirements:** FR-1110, FR-4300, FR-7100, FR-7300

#### FR-1130 — Sub-stepped event scheduling

- **ID:** FR-1130
- **Title:** Advance the clock to the next scheduled event without skipping it
- **Description:** When advancing simulated time, the system shall sub-step to the next scheduled
  event rather than applying a single large time step that could pass over a scheduled event
  (e.g., a short low-Earth-orbit access window) without processing it.
- **Rationale:** A naive large step at high time multipliers would silently skip short LEO passes
  and break the realism the exercise depends on (`CLAUDE.md` invariant 5; ADR-0006).
- **Priority:** Must
- **Inputs:** Current `WorldState`; the next-scheduled-event time from the `Scheduler`; a requested
  time multiplier/advance amount.
- **Outputs:** A sequence of intermediate world states, one per processed event, up to the
  requested target time.
- **Preconditions:** At least one event is scheduled, or the target time is reached with none
  pending.
- **Postconditions:** Every event whose scheduled time falls within the advanced interval is
  processed in order; none is skipped.
- **Acceptance Criteria:** Given a scheduled event inside an advance interval, after the advance
  completes the event's effects are present in the resulting state regardless of the requested
  time multiplier.
- **Verification Method:** Test
- **Dependencies:** FR-1110
- **Source Documents:** ADR-0006; GDS-03 §2.1 "Interfaces."
- **Related ADRs:** ADR-0006
- **Related Interfaces:** INT-0008
- **Related Requirements:** FR-1110, FR-1220

### FR-1200 — Orbital propagation and access geometry

#### FR-1210 — Moderate-fidelity orbital propagation

- **ID:** FR-1210
- **Title:** Propagate satellite orbits at moderate fidelity
- **Description:** The system shall propagate each satellite's orbit using a Keplerian + J2 model
  for fictional/moderate-fidelity assets, or an SGP4-class propagator for TLE-sourced real
  satellites, behind a common propagation interface.
- **Rationale:** Moderate fidelity is the deliberate, documented tradeoff between realism and
  accessibility for the training population (GDS-01 §1, §11; ADR-0009).
- **Priority:** Must
- **Inputs:** An Asset's `OrbitState` (Keplerian elements or TLE lines); a target simulated time.
- **Outputs:** Position/velocity state (ECI), derived ground track, eclipse/lighting status.
- **Preconditions:** The Asset has a valid orbit source (`kepler` or `tle`).
- **Postconditions:** A propagated state consistent with the chosen fidelity model at the
  requested time.
- **Acceptance Criteria:** Given a satellite with a valid TLE, the propagated ground track matches
  the reference SGP4 implementation's output within the documented tolerance.
- **Verification Method:** Test
- **Dependencies:** None
- **Source Documents:** GDS-01 §11 ("orbital fidelity model... assumed sufficient"); GDS-03 §2.1;
  build-spec/02 §5.1 FR-E3 (binding statement); ADR-0009.
- **Related ADRs:** ADR-0009
- **Related Interfaces:** INT-0008
- **Related Requirements:** FR-1220, FR-5200

#### FR-1220 — Access window computation across six channels

- **ID:** FR-1220
- **Title:** Compute access windows for all six access channels
- **Description:** The system shall compute access windows — intervals during which a given
  command, observation, jamming, engagement, or proximity action is geometrically possible — for
  each of the six access channels: command uplink, telemetry downlink, sensor observation, jam
  footprint, weapon engagement, and RPO proximity.
- **Rationale:** "You can only command, observe, or attack when access windows permit" is a
  foundational design constraint of the simulator (`CLAUDE.md`; GDS-01 §1; ADR-0011).
- **Priority:** Must
- **Inputs:** Propagated orbital/ground-site geometry for the relevant Asset(s)/Sensor(s)/Ground
  Station(s); the requested channel.
- **Outputs:** A set of `AccessWindow` intervals (start/end simulated time) for the requested
  channel and actor pair.
- **Preconditions:** The actor and target both have valid, propagatable position state.
- **Postconditions:** Windows reflect current geometry and are recomputed (or cached and
  invalidated) consistently as simulated time advances.
- **Acceptance Criteria:** Given a known orbital pass geometry, the computed access window's
  start/end times match the geometrically derived line-of-sight or elevation-mask crossing times
  within the documented tolerance, for each of the six channels.
- **Verification Method:** Test
- **Dependencies:** FR-1210
- **Source Documents:** `CLAUDE.md` "Six access channels"; GDS-03 §2.1; build-spec/02 §5.1 FR-E4
  (binding statement); ADR-0011.
- **Related ADRs:** ADR-0011
- **Related Interfaces:** INT-0008
- **Related Requirements:** FR-1210, FR-1130, FR-3110, FR-3210

### FR-1300 — Maneuver and resource accounting

#### FR-1310 — Impulsive maneuver with delta-v budget enforcement

- **ID:** FR-1310
- **Title:** Apply impulsive maneuvers against a finite delta-v budget
- **Description:** The system shall support impulsive maneuvers that edit an Asset's orbital
  elements and decrement that Asset's remaining delta-v budget; the system shall reject a maneuver
  that would drive the budget negative.
- **Rationale:** Fuel is described as "the operator's hardest constraint" (CLAUDE.md doc title
  `14-delta-v-economy.md`); GDS-04 §1.3 models `delta_v_ms` as a bounded resource.
- **Priority:** Must
- **Inputs:** A maneuver definition (entry mode, target parameters); the Asset's current
  `delta_v_ms`.
- **Outputs:** An updated `OrbitState`; an updated, decremented `delta_v_ms`.
- **Preconditions:** The Asset's `delta_v_ms` is sufficient for the requested maneuver's cost.
- **Postconditions:** `delta_v_ms` never goes negative (GDS-04 §9 validation rule); a maneuver
  exceeding the remaining budget is rejected at order validation, not partially applied.
- **Acceptance Criteria:** Given an Asset with `delta_v_ms = X`, a maneuver costing more than `X`
  is rejected before any orbital element changes; a maneuver costing `≤ X` succeeds and leaves
  `delta_v_ms = X - cost`.
- **Verification Method:** Test
- **Dependencies:** FR-1210
- **Source Documents:** GDS-04 §3 (Asset `resources.delta_v_ms`), §9 validation rules; build-spec/02
  §5.1 FR-E5 (binding statement).
- **Related ADRs:** (none directly — restates a GDS-04 validation rule)
- **Related Interfaces:** INT-0008
- **Related Requirements:** FR-1210, FR-3110

### FR-1400 — Counterspace effect resolution

#### FR-1410 — Five-D's effect resolution with reversibility and attribution

- **ID:** FR-1410
- **Title:** Resolve counterspace effects to a five-D's outcome
- **Description:** The system shall resolve an applied effect in one of the five counterspace
  categories (direct-ascent, co-orbital, electronic warfare, directed energy, cyber) to an outcome
  on the deceive/disrupt/deny/degrade/destroy ladder, recording reversibility, debris generation
  (kinetic only), attribution signal, and resource consumption as side effects.
- **Rationale:** The five-D's taxonomy with explicit reversibility/attribution/debris tracking is
  the simulator's doctrinal model of counterspace operations (`CLAUDE.md` "Five effect categories");
  ADR-0012.
- **Priority:** Must
- **Inputs:** An `EffectInstance` (template, actor, target, category).
- **Outputs:** An `EffectOutcome` (achieved outcome, success, side effects).
- **Preconditions:** The effect's required access channel is open (except the cyber exception,
  FR-1420); the actor's resources are sufficient.
- **Postconditions:** Side effects (debris, resource consumption, custody change, attribution
  signal, political consequence) are recorded consistently with the effect template's declared
  properties.
- **Acceptance Criteria:** Given a kinetic effect template with `debris_risk` set, a successful
  resolution always produces a `spawn_debris` side effect; given a non-kinetic, reversible effect
  template, no `spawn_debris` side effect is ever produced.
- **Verification Method:** Test
- **Dependencies:** FR-1220
- **Source Documents:** `CLAUDE.md` "Five effect categories... Cyber is the exception"; GDS-03
  §2.1; build-spec/02 §5.1 FR-E6 (binding statement); ADR-0012.
- **Related ADRs:** ADR-0012
- **Related Interfaces:** INT-0008
- **Related Requirements:** FR-1220, FR-1420, FR-1510

#### FR-1420 — Cyber exception handling

- **ID:** FR-1420
- **Title:** Resolve cyber effects outside the access-window gate
- **Description:** The system shall resolve cyber effects without requiring an open access window,
  instead gating success on a modeled access vector and the target's cyber posture.
- **Rationale:** Cyber is the explicitly documented exception to window-gating among the five
  effect categories (`CLAUDE.md`; ADR-0012).
- **Priority:** Must
- **Inputs:** A cyber `EffectInstance` (vector, payload, target); the target's `cyber.posture` and
  `cyber.vulnerabilities`.
- **Outputs:** An `EffectOutcome` reflecting success/detection probability and attribution.
- **Preconditions:** A modeled access vector exists for the chosen vector/payload combination.
- **Postconditions:** No access-window check is performed for this effect category; the outcome
  depends only on vector/payload/posture/dwell.
- **Acceptance Criteria:** Given a target with no open access window for any of the six channels,
  a cyber effect against that target is still resolvable (success/failure determined by
  vector/posture, not by window state).
- **Verification Method:** Test
- **Dependencies:** FR-1410
- **Source Documents:** `CLAUDE.md` "Cyber is the exception"; build-spec/02 §5.1 FR-E8 (binding
  statement); ADR-0012.
- **Related ADRs:** ADR-0012
- **Related Interfaces:** INT-0008
- **Related Requirements:** FR-1410, FR-1220

### FR-1500 — Custody, tracks, and the weapons-quality gate

#### FR-1510 — Track confidence decay and reset

- **ID:** FR-1510
- **Title:** Decay track confidence over time and reset it on observation
- **Description:** The system shall maintain, per cell, a confidence value on each held `Track`
  that decays as a function of time since last observation and resets (increases) when a new
  observation of that object occurs.
- **Rationale:** Custody confidence decay is the simulator's instance of the decision-cycle pattern
  (observe → classify) and underlies the weapons-quality gate (GDS-01 §1; GDS-04 §1.9; ADR-0013).
- **Priority:** Must
- **Inputs:** A `Track`'s current confidence and last-observation time; the current simulated time;
  any new observation event for that object.
- **Outputs:** An updated `Track.confidence` value.
- **Preconditions:** A `Track` exists for the object in the requesting cell's `TrackCatalog`.
- **Postconditions:** Confidence strictly decreases with elapsed time absent a new observation;
  confidence increases upon a new observation.
- **Acceptance Criteria:** Given a `Track` last observed at `T0` with confidence `C0`, querying
  confidence at `T1 > T0` with no intervening observation yields a value `< C0`; an observation at
  `T1` yields a value `≥ C0`.
- **Verification Method:** Test
- **Dependencies:** FR-1220
- **Source Documents:** GDS-04 §1.9, §5 (`Track.confidence`); build-spec/02 §5.1 FR-E7 (binding
  statement); ADR-0013.
- **Related ADRs:** ADR-0013
- **Related Interfaces:** INT-0007, INT-0010
- **Related Requirements:** FR-1520, FR-3210, FR-6200

#### FR-1520 — Weapons-quality track gate

- **ID:** FR-1520
- **Title:** Gate engagement on a weapons-quality track
- **Description:** The system shall permit an engagement-intent action against a target only when
  that target's held `Track` has confidence at or above a configured threshold and is
  characterized; the system shall reject the action otherwise.
- **Rationale:** The weapons-quality gate is the doctrinal control preventing engagement on
  insufficiently confirmed custody (GDS-04 §1.9; ADR-0013).
- **Priority:** Must
- **Inputs:** A requested engagement action; the target's `Track` (confidence, `characterized`
  flag).
- **Outputs:** An accept/reject decision with a reason on rejection.
- **Preconditions:** A `Track` for the intended target exists in the requesting cell's
  `TrackCatalog`.
- **Postconditions:** No engagement-intent action is scheduled or executed against a target whose
  `Track` fails the gate at validation or execution time.
- **Acceptance Criteria:** Given a `Track` with confidence below threshold or `characterized=false`,
  an engagement order against that target is rejected at both plan-time and execute-time
  validation.
- **Verification Method:** Test
- **Dependencies:** FR-1510
- **Source Documents:** GDS-04 §1.9 ("weapons-quality track exists when confidence ≥ threshold AND
  characterized"); ADR-0013.
- **Related ADRs:** ADR-0013
- **Related Interfaces:** INT-0007
- **Related Requirements:** FR-1510, FR-3110, FR-3400

---

## FR-2000 — Bus & Payload Operations

### FR-2100 — Bus state of health

#### FR-2110 — Subsystem SOH modeling with soft/hard limits

- **ID:** FR-2110
- **Title:** Model live bus subsystem state-of-health against soft/hard limits
- **Description:** The system shall maintain a live state-of-health value for each Asset's power,
  attitude, thermal, propellant, command-and-data-handling, and comms subsystems, evaluating each
  against configured soft and hard limits to produce a green/yellow/red status.
- **Rationale:** SOH monitoring against limits is the core bus-operator training objective
  (GDS-01 §1; GDS-04 §3 `bus_state`; build-spec/02 §5.2 FR-B1).
- **Priority:** Must
- **Inputs:** Subsystem-specific live parameters (e.g., battery state of charge, propellant
  fraction); configured soft/hard limit thresholds.
- **Outputs:** Per-subsystem status (`green`/`yellow`/`status`).
- **Preconditions:** The Asset has an initialized `bus_state`.
- **Postconditions:** Status reflects the current parameter value against its limits at every
  evaluation.
- **Acceptance Criteria:** Given a subsystem parameter crossing a configured soft limit, the
  subsystem's status transitions from `green` to `yellow` at the next evaluation; crossing the
  hard limit transitions it to `red`.
- **Verification Method:** Test
- **Dependencies:** None
- **Source Documents:** GDS-04 §3 `bus_state`; build-spec/02 §5.2 FR-B1 (binding statement).
- **Related ADRs:** (none directly)
- **Related Interfaces:** INT-0008
- **Related Requirements:** FR-2210, FR-2310, FR-2510

### FR-2200 — Bus-gates-payload

#### FR-2210 — Payload availability gated by bus health

- **ID:** FR-2210
- **Title:** Gate payload operation on bus subsystem health
- **Description:** The system shall prevent payload operation when a prerequisite bus subsystem
  is unavailable (e.g., insufficient power, unachievable pointing, full storage), independent of
  whether the operator attempts the action.
- **Rationale:** Realistic bus/payload coupling is a stated training objective (GDS-01 §1; GDS-04
  §3 `payload_state`/`bus_state` relationship; build-spec/02 §5.2 FR-B2).
- **Priority:** Must
- **Inputs:** Current `bus_state` (power, attitude, storage); a requested payload action.
- **Outputs:** An accept/reject decision for the payload action.
- **Preconditions:** A `bus_state` snapshot exists for the Asset.
- **Postconditions:** No payload action that requires an unavailable bus resource is executed.
- **Acceptance Criteria:** Given an Asset with zero available power, a payload-power-on action is
  rejected; given full onboard storage, an ISR collection action is rejected.
- **Verification Method:** Test
- **Dependencies:** FR-2110
- **Source Documents:** GDS-04 §3; build-spec/02 §5.2 FR-B2 (binding statement).
- **Related ADRs:** (none directly)
- **Related Interfaces:** INT-0008
- **Related Requirements:** FR-2110, FR-2410

### FR-2300 — Pass-gated telemetry

#### FR-2310 — Telemetry pass-gating and stored-telemetry dump

- **ID:** FR-2310
- **Title:** Pass-gate ground-visible telemetry with stored-dump catch-up
- **Description:** The system shall update an Asset's ground-visible SOH snapshot only at a
  telemetry-downlink contact; between contacts the displayed snapshot shall remain the
  timestamped last-known value; the system shall support a stored-telemetry dump at the next
  contact that reveals events that occurred out of contact.
- **Rationale:** Pass-gated telemetry is fundamental to operating "on belief, not ground truth"
  (`CLAUDE.md`; GDS-01 §1; build-spec/02 §5.2 FR-B3).
- **Priority:** Must
- **Inputs:** The Asset's live SOH state (ground truth); the current telemetry-downlink access
  window state.
- **Outputs:** The ground-visible SOH snapshot, timestamped; a stored-telemetry dump payload on
  request at contact.
- **Preconditions:** A telemetry-downlink `AccessWindow` is open for the dump to occur.
- **Postconditions:** The displayed snapshot's timestamp never advances outside of an open
  telemetry-downlink window.
- **Acceptance Criteria:** Given an Asset whose SOH changes between two contacts, the
  ground-visible snapshot does not reflect that change until the next telemetry-downlink contact
  occurs.
- **Verification Method:** Test
- **Dependencies:** FR-1220, FR-2110
- **Source Documents:** GDS-04 §3 `last_telemetry_time`; build-spec/02 §5.2 FR-B3 (binding
  statement).
- **Related ADRs:** ADR-0004
- **Related Interfaces:** INT-0007, INT-0008
- **Related Requirements:** FR-2110, FR-6200

### FR-2400 — Payload-type-specific operations

#### FR-2410 — Type-specific operator actions and monitors

- **ID:** FR-2410
- **Title:** Expose payload-type-specific operator actions and monitors
- **Description:** The system shall expose, for each supported payload type (SATCOM, ISR-EO,
  ISR-SAR, SIGINT, SDA, space-control, PNT, missile warning, weather), the set of operator actions
  and monitoring displays specific to that payload type.
- **Rationale:** Operating different mission types is an explicit training objective (GDS-01 §1,
  §6 "Typical user scenarios"; build-spec/02 §5.2 FR-B4).
- **Priority:** Must
- **Inputs:** The Asset's `payload_state.type`.
- **Outputs:** A type-appropriate action set and monitoring display.
- **Preconditions:** The Asset's payload type is one of the supported types.
- **Postconditions:** Only actions valid for the payload's type are offered.
- **Acceptance Criteria:** Given a SATCOM payload, frequency/beam-replan and customer-shift actions
  are offered and a SIGINT-only action (e.g., geolocation collection) is not.
- **Verification Method:** Test
- **Dependencies:** FR-2210
- **Source Documents:** GDS-01 §6; build-spec/02 §5.2 FR-B4 (binding statement).
- **Related ADRs:** (none directly)
- **Related Interfaces:** INT-0004, INT-0008
- **Related Requirements:** FR-2210, FR-3500

### FR-2500 — Safe-mode loop

#### FR-2510 — Safe-mode entry, diagnosis, and multi-pass recovery

- **ID:** FR-2510
- **Title:** Support the full safe-mode attack/detection/recovery loop
- **Description:** The system shall transition an Asset into safe mode upon a qualifying
  fault/environment/cyber/EW/bus-stress condition (subject to a configured susceptibility check),
  disabling its payload and pointing it sunward, and shall support a multi-pass, ground-driven
  recovery procedure that returns the Asset to nominal mode or re-enters safe mode if the root
  cause persists.
- **Rationale:** The safe-mode loop is the simulator's defensive-operations and recovery training
  centerpiece (GDS-01 §7; build-spec/02 §5.2 FR-B5).
- **Priority:** Must
- **Inputs:** A qualifying safe-mode-triggering condition; the configured susceptibility
  parameter; operator-issued recovery commands.
- **Outputs:** An updated `bus_state.safe_mode` (active, cause, defender diagnosis, recovery plan
  progress); a return to `nominal` or a re-safe transition.
- **Preconditions:** The Asset is in `nominal` mode when the triggering condition occurs (for
  entry); the Asset is in `safe_mode` (for recovery).
- **Postconditions:** The payload is disabled while `safe_mode.active = true`; recovery only
  succeeds when all required steps complete and the root cause no longer persists.
- **Acceptance Criteria:** Given an Asset in `safe_mode` with an unresolved root cause, completing
  the recovery procedure without addressing the root cause results in re-entry to `safe_mode`, not
  a stable `nominal` state.
- **Verification Method:** Test
- **Dependencies:** FR-2110, FR-2210
- **Source Documents:** `docs/design/12-safe-mode-loop.md` (descriptive elaboration); GDS-04 §3
  `safe_mode`; build-spec/02 §5.2 FR-B5 (binding statement).
- **Related ADRs:** (none directly)
- **Related Interfaces:** INT-0008
- **Related Requirements:** FR-2110, FR-3110

---

## FR-3000 — Command Planning & Sensor Tasking

### FR-3100 — Plan-first commanding

#### FR-3110 — Planned-activity creation with delivery path

- **ID:** FR-3110
- **Title:** Plan commands for execution at the next valid access window
- **Description:** The system shall allow an operator to create a Planned Activity (command-kind)
  that executes at the earliest valid access window (or a chosen future window) via ground uplink,
  inter-satellite-link relay (where geometry and peer permit), or stored program; the activity
  shall remain editable and cancellable until uplink occurs.
- **Rationale:** Plan-first commanding — never acting instantly on perfect knowledge — is a
  load-bearing invariant (`CLAUDE.md` invariant 4; GDS-01 §10; ADR-0005).
- **Priority:** Must
- **Inputs:** A command intent (verb, target Asset, parameters); the chosen delivery path.
- **Outputs:** A `PlannedActivity` in `DRAFT` or `PLANNED` state with a `scheduled_window`.
- **Preconditions:** A valid Role Assignment binding the operator to the target Asset; an open or
  future-computable `AccessWindow` for the chosen delivery path (not required for `stored_program`
  delivery, scheduled by time/condition instead).
- **Postconditions:** The Planned Activity is not executed before its scheduled window opens; it
  can be cancelled or edited any time before uplink.
- **Acceptance Criteria:** Given a Planned Activity in `PLANNED` state before its window opens, an
  operator cancellation removes it from the active queue with no effect on `WorldState`.
- **Verification Method:** Test
- **Dependencies:** FR-1220
- **Source Documents:** GDS-01 §10; GDS-04 §6.5 `PlannedActivity`; build-spec/02 §5.3 FR-P1
  (binding statement); ADR-0005.
- **Related ADRs:** ADR-0005
- **Related Interfaces:** INT-0004, INT-0006, INT-0008
- **Related Requirements:** FR-1220, FR-3300, FR-3400, FR-3500

#### FR-3120 — Cancellation and editing before uplink

- **ID:** FR-3120
- **Title:** Allow cancellation or editing of a Planned Activity before execution
- **Description:** The system shall allow the owning operator to cancel or edit a Planned Activity
  at any point in its `DRAFT` or `PLANNED` state, prior to its `ACTIVE`/execution transition.
- **Rationale:** Editability before commit is part of the plan-first model (GDS-04 §6.5
  lifecycle).
- **Priority:** Must
- **Inputs:** A cancellation or edit request against an existing `PlannedActivity` id.
- **Outputs:** The activity's updated or removed state.
- **Preconditions:** The activity is in `DRAFT` or `PLANNED` state.
- **Postconditions:** An activity already `ACTIVE` or `EXECUTED` cannot be cancelled or edited
  through this requirement's path.
- **Acceptance Criteria:** A cancellation request against an `EXECUTED` activity is rejected; the
  same request against a `PLANNED` activity succeeds and the activity no longer appears in the
  active queue.
- **Verification Method:** Test
- **Dependencies:** FR-3110
- **Source Documents:** GDS-04 §6.5 `PlannedActivity` lifecycle.
- **Related ADRs:** ADR-0005
- **Related Interfaces:** INT-0004, INT-0006
- **Related Requirements:** FR-3110

### FR-3200 — Sensor tasking via Mock SSN

#### FR-3210 — SSN request submission under single-task contention

- **ID:** FR-3210
- **Title:** Task SDA sensors subject to single-task contention
- **Description:** The system shall allow an operator to task a sensor with a search/track/
  characterize/cue intent, subject to that sensor's geometry constraints and a single-task
  contention rule (a sensor serves at most its declared `task_capacity` simultaneous tasks).
- **Rationale:** Scarce SDA sensors and contention are an explicit training objective (GDS-01 §1;
  build-spec/02 §5.3 FR-P2).
- **Priority:** Must
- **Inputs:** A collection-kind Planned Activity or SSN Request (sensor, intent, target).
- **Outputs:** A staged/pending request; eventually, on resolution, a `Track` update.
- **Preconditions:** The sensor's current task count is below `task_capacity`; the requesting
  cell's Role Assignment covers the sensor or the target's collection intent.
- **Postconditions:** A request exceeding the sensor's `task_capacity` is rejected or queued per
  the contention rule, not silently double-booked.
- **Acceptance Criteria:** Given a sensor with `task_capacity = 1` already serving one task, a
  second concurrent tasking request is rejected or queued, never executed concurrently with the
  first.
- **Verification Method:** Test
- **Dependencies:** FR-1220
- **Source Documents:** GDS-04 §1.13 SSN Request; build-spec/02 §5.3 FR-P2 (binding statement);
  ADR-0010.
- **Related ADRs:** ADR-0010
- **Related Interfaces:** INT-0009
- **Related Requirements:** FR-3220, FR-1510

#### FR-3220 — SSN delivery into the requesting cell's TrackCatalog

- **ID:** FR-3220
- **Title:** Deliver resolved sensor-tasking results into the requester's TrackCatalog
- **Description:** The system shall deliver a resolved SSN Request's result as a `Track`
  creation/update into the requesting cell's `TrackCatalog`, after the request's priority-SLA-plus-
  processing-delay resolution completes; a request cancelled before collection shall produce no
  Track side effect.
- **Rationale:** The "request and wait" texture of the mock SSN is a deliberate design choice
  modeling real sensor scarcity (GDS-03 §2.3; GDS-04 §1.13).
- **Priority:** Must
- **Inputs:** A staged SSN Request whose resolution delay has elapsed.
- **Outputs:** A `Track` update/creation in the requesting cell's `TrackCatalog`.
- **Preconditions:** The request was not cancelled before its collection event fired.
- **Postconditions:** A cancelled-before-collection request produces no Track update.
- **Acceptance Criteria:** Given a staged request cancelled before its resolution time, no Track
  update for that request's target appears in the requester's `TrackCatalog`.
- **Verification Method:** Test
- **Dependencies:** FR-3210
- **Source Documents:** GDS-04 §1.13 "Lifecycle"; GDS-03 §2.3 "Responsibilities"; ICD INT-0010;
  ADR-0010.
- **Related ADRs:** ADR-0010
- **Related Interfaces:** INT-0009, INT-0010
- **Related Requirements:** FR-3210, FR-1510

### FR-3300 — Unified planned-activity scheduler

#### FR-3310 — Single scheduler for commands and collection tasks

- **ID:** FR-3310
- **Title:** Schedule commands and collection tasks on one shared scheduler
- **Description:** The system shall implement command-kind and collection-kind Planned Activities
  on a single scheduling mechanism so that queueing, timeline display, undo, and time-travel
  behave identically for both kinds.
- **Rationale:** A single scheduler avoids divergent behavior between the two kinds of plan-first
  action (GDS-04 §6.5; build-spec/02 §5.3 FR-P3).
- **Priority:** Must
- **Inputs:** A Planned Activity of either `kind` (`command` or `collection`).
- **Outputs:** A scheduled entry queryable through one queue/timeline regardless of kind.
- **Preconditions:** The activity has a valid `kind` and `actor_ref`.
- **Postconditions:** Undo/time-travel operations apply identically to both kinds.
- **Acceptance Criteria:** Given a rewind to a sim time before a collection-kind activity's
  execution, the activity returns to its pre-execution state exactly as a command-kind activity
  would under the same rewind.
- **Verification Method:** Test
- **Dependencies:** FR-3110, FR-3210
- **Source Documents:** GDS-04 §6.5 (`PlannedActivity.kind`); build-spec/02 §5.3 FR-P3 (binding
  statement).
- **Related ADRs:** (none directly)
- **Related Interfaces:** INT-0008
- **Related Requirements:** FR-3110, FR-3210, FR-4300

### FR-3400 — Re-validation at execution time

#### FR-3410 — Execute-time re-validation of every planned activity

- **ID:** FR-3410
- **Title:** Re-validate ownership, window, resources, ROE, and track gate at execution
- **Description:** The system shall re-validate every Planned Activity at its execution time
  against current ownership, access-window validity, resource sufficiency, rules of engagement,
  and (for engagement intents) the weapons-quality track gate, failing gracefully with a recorded
  reason if any check fails.
- **Rationale:** State can change between plan-time and execute-time (e.g., resource depletion, a
  closed window); re-validation prevents stale plans from executing illegally (GDS-04 §6.5
  "Validation"; build-spec/02 §5.3 FR-P4).
- **Priority:** Must
- **Inputs:** A Planned Activity reaching its scheduled execution point; current `WorldState`.
- **Outputs:** Either a successful execution and resulting state change, or a `FAILED` activity
  state with a `fail_reason`.
- **Preconditions:** The activity has reached its scheduled execution trigger.
- **Postconditions:** No activity executes while failing any of the five re-validation checks.
- **Acceptance Criteria:** Given an activity whose resource requirement became unaffordable after
  planning but before execution, the activity transitions to `FAILED` with a resource-related
  `fail_reason`, and no resource is consumed.
- **Verification Method:** Test
- **Dependencies:** FR-3110, FR-1310, FR-1520
- **Source Documents:** GDS-04 §6.5 "Validation"; build-spec/02 §5.3 FR-P4 (binding statement).
- **Related ADRs:** ADR-0005, ADR-0013
- **Related Interfaces:** INT-0008
- **Related Requirements:** FR-3110, FR-1310, FR-1520

### FR-3500 — Role-scoped command catalog

#### FR-3510 — Order panel limited to the seated role's legal commands

- **ID:** FR-3510
- **Title:** Offer only commands legal for the seated role and asset
- **Description:** The system shall present, in the order/command interface, only the commands
  legal for the operator's seated role (bus vs. payload) and the targeted Asset, drawn from that
  Asset's command database.
- **Rationale:** Role-scoped command availability prevents an operator from issuing commands
  outside their assigned responsibility (GDS-01 §2 "Intended users"; build-spec/02 §5.3 FR-P5).
- **Priority:** Must
- **Inputs:** The operator's Role Assignment (bus/payload/both); the target Asset's command
  database.
- **Outputs:** A filtered command list appropriate to the role and asset.
- **Preconditions:** A valid Role Assignment exists for the operator and the targeted Asset.
- **Postconditions:** A command outside the role's scope (e.g., a payload command attempted by a
  bus-only-assigned operator) is not offered, and is rejected if attempted directly.
- **Acceptance Criteria:** Given an operator with a bus-only Role Assignment, a payload-only
  command for that Asset does not appear in the offered command list and is rejected if submitted.
- **Verification Method:** Test
- **Dependencies:** None
- **Source Documents:** GDS-04 §1.10 Role Assignment; build-spec/02 §5.3 FR-P5 (binding statement).
- **Related ADRs:** ADR-0004
- **Related Interfaces:** INT-0004
- **Related Requirements:** FR-2410, FR-3110, FR-3520

#### FR-3520 — Role Assignment scoping: bus-only, payload-only, or both

- **ID:** FR-3520
- **Title:** Scope a Role Assignment to bus-only, payload-only, or both per Asset
- **Description:** The system shall allow a Role Assignment to be scoped, per Asset or
  constellation, to bus operation only, payload operation only, or both, and shall enforce that
  scope as a system behavior in its own right, independent of the order-panel command filtering
  that scope produces (FR-3510).
- **Rationale:** GDS-05 OR-2 and GDS-04 §1.10 both state a Role Assignment "maps a seat to a role
  (bus, payload, or both)"; FR-3510 describes only the UI-filtering *consequence* of this rule, not
  the cardinality rule itself, leaving no leaf a tester could check to verify the rule is enforced
  independent of its UI side effect (GDS-04 §1.10 Role Assignment; build-spec/02 §6 OR-2).
- **Priority:** Must
- **Inputs:** A Role Assignment creation/edit request specifying bus-only, payload-only, or both
  for a given Asset.
- **Outputs:** A Role Assignment record carrying the specified scope.
- **Preconditions:** The requester holds the White Cell role (only White Cell may create/modify
  Role Assignments, GDS-04 §1.10 Constraints).
- **Postconditions:** A command outside a Role Assignment's scope (e.g., a payload-verb command
  attempted under a bus-only scope) is rejected at execution time, whether or not it was also
  filtered from the order panel.
- **Acceptance Criteria:** Given a Role Assignment scoped to bus-only for Asset X, a payload-verb
  command submitted directly for Asset X (bypassing the order panel) is rejected.
- **Verification Method:** Test
- **Dependencies:** None
- **Source Documents:** GDS-05 "Operational Rules" OR-2; GDS-04 §1.10 Role Assignment;
  build-spec/02 §6 OR-2 (binding statement).
- **Related ADRs:** ADR-0004
- **Related Interfaces:** INT-0004, INT-0006
- **Related Requirements:** FR-3510

---

## FR-4000 — White Cell Exercise Control

### FR-4100 — Vignette selection and parameter tuning

#### FR-4110 — Vignette selection with tunable, defaulted parameters

- **ID:** FR-4110
- **Title:** Select and tune a vignette before starting an exercise
- **Description:** The system shall allow White Cell to select a vignette and adjust its tunable
  parameters before starting an exercise; every parameter shall have a default such that the
  vignette is runnable unmodified.
- **Rationale:** White Cell facilitators are explicitly assumed to operate without a programming
  background (GDS-01 §3; build-spec/02 §5.4 FR-W1).
- **Priority:** Must
- **Inputs:** A Vignette definition; optional parameter overrides.
- **Outputs:** A Session initialized with the selected/overridden parameter values.
- **Preconditions:** The Vignette file is valid (FR-5310).
- **Postconditions:** Unmodified parameters take their declared default value.
- **Acceptance Criteria:** Given a Vignette with no parameter overrides supplied, the started
  Session uses every parameter's documented default value.
- **Verification Method:** Test
- **Dependencies:** FR-5310
- **Source Documents:** GDS-01 §5; build-spec/02 §5.4 FR-W1 (binding statement).
- **Related ADRs:** (none directly)
- **Related Interfaces:** INT-0002
- **Related Requirements:** FR-4210, FR-5310

### FR-4200 — Role and seat assignment

#### FR-4210 — Seat-to-role assignment at setup

- **ID:** FR-4210
- **Title:** Assign operator seats to roles and assets at setup
- **Description:** The system shall allow White Cell to assign each operator seat to one or more
  roles, specifying for each assigned Asset/constellation whether the seat holds bus, payload, or
  both responsibilities, informed by the vignette's declared `roles_needed`.
- **Rationale:** Seat assignment precedes and gates role-scoped command access (GDS-01 §5 step 2;
  build-spec/02 §5.4 FR-W2).
- **Priority:** Must
- **Inputs:** The vignette's `roles_needed`; White Cell's seat-to-role mapping input.
- **Outputs:** A set of Role Assignments.
- **Preconditions:** A Vignette is loaded (FR-4110).
- **Postconditions:** Every `roles_needed` entry the vignette declares mandatory has at least one
  bound seat before the exercise may start.
- **Acceptance Criteria:** Given a vignette with an unmet mandatory `roles_needed` entry, the
  system reports it as unsatisfied rather than allowing the exercise to start silently understaffed.
- **Verification Method:** Test
- **Dependencies:** FR-4110
- **Source Documents:** GDS-01 §5 step 2; GDS-04 §1.10 Role Assignment; build-spec/02 §5.4 FR-W2
  (binding statement).
- **Related ADRs:** (none directly)
- **Related Interfaces:** INT-0002
- **Related Requirements:** FR-3510, FR-4110

### FR-4300 — Single point of time control

#### FR-4310 — Exclusive White Cell clock control

- **ID:** FR-4310
- **Title:** Restrict clock control to White Cell
- **Description:** The system shall allow only the White Cell role to start, pause, resume,
  fast-forward (via time multiplier), and rewind the simulated clock; no operator-cell interface
  shall expose clock control.
- **Rationale:** Single point of time control prevents operators from gaining an unfair tempo
  advantage and keeps the exercise narratively coherent (GDS-01 §10; ADR-0016).
- **Priority:** Must
- **Inputs:** A clock-control request (start/pause/resume/rewind/multiplier) and the requester's
  role.
- **Outputs:** An updated clock state, or a rejection if the requester is not White Cell.
- **Preconditions:** The requester holds the White Cell role for the session.
- **Postconditions:** No non-White-Cell-issued clock-control request changes the clock state.
- **Acceptance Criteria:** Given a clock-control request issued by a Blue or Red cell role, the
  request is rejected and the clock state is unchanged.
- **Verification Method:** Test
- **Dependencies:** FR-1110
- **Source Documents:** GDS-01 §10; build-spec/02 §5.4 FR-W3 (binding statement); ADR-0016.
- **Related ADRs:** ADR-0016
- **Related Interfaces:** INT-0002
- **Related Requirements:** FR-1110, FR-6300

### FR-4400 — Inject authoring and firing

#### FR-4410 — Immediate and scheduled inject application

- **ID:** FR-4410
- **Title:** Fire injects immediately or at a scheduled simulated time
- **Description:** The system shall allow White Cell to apply a scripted or manually authored
  inject either immediately or scheduled for a future simulated time, applying its effects outside
  the normal Planned-Activity/access-window path; future-scheduled injects shall replay
  byte-identically on save/resume.
- **Rationale:** Injects are the documented, accepted bypass of plan-first commanding for White
  Cell narrative control (GDS-01 §4; ADR-0005; build-spec/02 §5.4 FR-W4).
- **Priority:** Must
- **Inputs:** An Inject definition (immediate or with `at_sim_t`).
- **Outputs:** Applied effects on the targeted Assets/Ground Stations/Sensors/Tracks; an
  `EventLog` entry.
- **Preconditions:** A non-repeatable inject must not have already fired.
- **Postconditions:** A scheduled inject applies at its `at_sim_t` regardless of save/resume in
  between, reproducing byte-identically.
- **Acceptance Criteria:** Given a session saved and resumed before a scheduled inject's
  `at_sim_t`, the inject still fires at the correct simulated time after resume, with identical
  effects to an unsaved run.
- **Verification Method:** Test
- **Dependencies:** FR-1120
- **Source Documents:** GDS-04 §1.12 Inject; build-spec/02 §5.4 FR-W4 (binding statement);
  ADR-0005.
- **Related ADRs:** ADR-0005
- **Related Interfaces:** INT-0002, INT-0016
- **Related Requirements:** FR-1120, FR-7200

### FR-4500 — Classification banner

#### FR-4510 — Classification banner set and displayed

- **ID:** FR-4510
- **Title:** Set and display the classification banner on every screen and export
- **Description:** The system shall allow White Cell to set a classification banner
  (UNCLASSIFIED//EXERCISE or UNCLASSIFIED//TRAINING) at scenario build, and shall display it on
  every screen and include it in every exported file.
- **Rationale:** All content is unclassified training material, and the banner makes that explicit
  at every touchpoint (GDS-01 §4; build-spec/02 §5.4 FR-W5).
- **Priority:** Must
- **Inputs:** A selected classification banner value at scenario build.
- **Outputs:** The banner rendered on every UI screen; the banner embedded in every export.
- **Preconditions:** A classification value is set at vignette build time.
- **Postconditions:** No screen or export omits the banner.
- **Acceptance Criteria:** Given a session with banner X set, every screen render and every AAR
  export file produced during that session displays/embeds banner X.
- **Verification Method:** Test
- **Dependencies:** FR-5100
- **Source Documents:** GDS-01 §4; build-spec/02 §5.4 FR-W5 (binding statement).
- **Related ADRs:** (none directly)
- **Related Interfaces:** INT-0002, INT-0001
- **Related Requirements:** FR-5100, FR-7300

### FR-4600 — God-view and cell-view-as

#### FR-4610 — White Cell god-view with per-cell view-as

- **ID:** FR-4610
- **Title:** Provide White Cell a god-view and the ability to view as a specific cell
- **Description:** The system shall provide White Cell a god-view combining ground truth and both
  cells' belief states, and shall allow White Cell to switch to viewing the session exactly as Red
  or as Blue would see it, for adjudication purposes.
- **Rationale:** White Cell must adjudicate fairly using both ground truth and each side's actual
  belief state (GDS-04 §8; build-spec/02 §5.4 FR-W6).
- **Priority:** Must
- **Inputs:** A god-view or view-as-cell request from White Cell.
- **Outputs:** The requested view (god-view, or the named cell's exact `CellView`).
- **Preconditions:** The requester holds the White Cell role.
- **Postconditions:** A view-as-cell request never grants White Cell write access to that cell's
  state through the view-as path.
- **Acceptance Criteria:** Given White Cell viewing as Red, the displayed data matches exactly what
  a Red-seated operator would see via INT-0004, no more and no less.
- **Verification Method:** Test
- **Dependencies:** FR-6200
- **Source Documents:** GDS-04 §8 Fog-of-war view model; build-spec/02 §5.4 FR-W6 (binding
  statement); ADR-0004.
- **Related ADRs:** ADR-0004
- **Related Interfaces:** INT-0002, INT-0007
- **Related Requirements:** FR-6200

### FR-4700 — Manual adjudication

#### FR-4710 — No automated scoring; manual adjudication only

- **ID:** FR-4710
- **Title:** Adjudicate manually with no automated scoring
- **Description:** The system shall not compute or display an automated score or win/loss
  determination; outcomes shall be adjudicated and narrated manually by White Cell.
- **Rationale:** Manual adjudication is an explicit v1 design decision (GDS-01 §10; ADR-0017).
- **Priority:** Must
- **Inputs:** None (absence of a feature).
- **Outputs:** None — the system provides raw state/event-log data (FR-7100, FR-7300) for White
  Cell's manual use, never a computed score.
- **Preconditions:** N/A
- **Postconditions:** No interface in the system surfaces an automatically computed score or
  win/loss verdict.
- **Acceptance Criteria:** A review of every outbound interface confirms none returns a computed
  score or win/loss field.
- **Verification Method:** Inspection
- **Dependencies:** None
- **Source Documents:** GDS-01 §10; build-spec/02; ADR-0017.
- **Related ADRs:** ADR-0017, ADR-0029
- **Related Interfaces:** (none — absence of an interface)
- **Related Requirements:** FR-7100, FR-7300

#### FR-4720 — Adjust safe-mode dials and other live parameters mid-exercise

- **ID:** FR-4720
- **Title:** Adjust safe-mode dials and other live exercise parameters mid-exercise
- **Description:** The system shall allow White Cell to adjust safe-mode threshold dials and other
  live, White-Cell-configurable exercise parameters while a session is running, without requiring
  a session restart.
- **Rationale:** GDS-05 FR-W7 names this capability directly. "Other live parameters" is an
  intentionally open-ended set — the specific parameters a White Cell control panel exposes are a
  design matter for that panel, not a fixed list to be enumerated at the requirements layer — so
  this leaf states the capability and its open-endedness explicitly rather than leaving the
  catch-all phrase unaddressed (GDS-05 "White Cell control" FR-W7; build-spec/02 §5.4).
- **Priority:** Must
- **Inputs:** A White-Cell parameter-adjustment request against a running session.
- **Outputs:** The updated parameter value, applied to the live session.
- **Preconditions:** The requester holds the White Cell role; a running session exists.
- **Postconditions:** No session restart is required for an adjusted parameter to take effect.
- **Acceptance Criteria:** Given a running session, White Cell adjusting a safe-mode dial takes
  effect on the next evaluation of that dial, with no session restart.
- **Verification Method:** Demonstration
- **Dependencies:** None
- **Source Documents:** GDS-05 "White Cell control" FR-W7; build-spec/02 §5.4.
- **Related ADRs:** (none directly)
- **Related Interfaces:** INT-0002
- **Related Requirements:** FR-4710

---

## FR-5000 — Scenario / Vignette Authoring

### FR-5100 — In-app vignette builder

#### FR-5110 — Iterative in-app vignette composition

- **ID:** FR-5110
- **Title:** Author a vignette iteratively in-app before saving
- **Description:** The system shall allow White Cell to compose a vignette (force lay-down,
  parameters, injects, intro briefs) across multiple round trips, accumulating partial state,
  before a single save/build action emits a complete vignette file.
- **Rationale:** Scenario authoring is recognized as a distinct, multi-step interaction separate
  from one-shot vignette loading (ADR-0027; ICD INT-0003).
- **Priority:** Must
- **Inputs:** Incremental authoring inputs across an authoring session.
- **Outputs:** A complete vignette definition file on save/build.
- **Preconditions:** White Cell role; no running session required.
- **Postconditions:** No partial/incomplete vignette file is emitted by an in-progress (unsaved)
  authoring session.
- **Acceptance Criteria:** Given an authoring session with several incremental inputs but no final
  save/build action, no vignette file is written to disk.
- **Verification Method:** Test
- **Dependencies:** None
- **Source Documents:** ICD INT-0003; ADR-0027.
- **Related ADRs:** ADR-0027
- **Related Interfaces:** INT-0003
- **Related Requirements:** FR-5210, FR-5310

### FR-5200 — TLE import and fallback

#### FR-5210 — Space-Track import with manual/Keplerian fallback

- **ID:** FR-5210
- **Title:** Import TLEs from Space-Track at build time with a manual fallback
- **Description:** The system shall attempt to import two-line elements from Space-Track.org at
  scenario-build time when reachable, and shall accept manual TLE entry or Keplerian-element
  synthesis as a fallback when Space-Track is unreachable or unavailable; no network access shall
  be required after vignette creation.
- **Rationale:** Offline-first runtime with an optional, build-time-only network dependency is a
  load-bearing invariant (`CLAUDE.md` invariant; ADR-0018).
- **Priority:** Must
- **Inputs:** A real-satellite identifier for TLE lookup, or manually entered TLE/Keplerian data.
- **Outputs:** A populated `OrbitState` for the force-added Asset.
- **Preconditions:** None for the manual/Keplerian path; network reachability for the Space-Track
  path.
- **Postconditions:** Once a vignette is created, no further network access is required to run it.
- **Acceptance Criteria:** Given Space-Track is unreachable, manual TLE entry still successfully
  produces a valid `OrbitState` for the force-added Asset.
- **Verification Method:** Test
- **Dependencies:** FR-1210
- **Source Documents:** GDS-01 §9; GDS-02 §3–§4; build-spec/02 §5.5 FR-S2 (binding statement);
  ADR-0018.
- **Related ADRs:** ADR-0018
- **Related Interfaces:** INT-0013
- **Related Requirements:** FR-1210, FR-5310

### FR-5300 — Vignette validation

#### FR-5310 — Load-time vignette validation with precise errors

- **ID:** FR-5310
- **Title:** Validate a vignette at load time and report errors precisely
- **Description:** The system shall validate a vignette at load time (well-formed TLEs, every
  declared `roles_needed` satisfiable, every referenced template exists) and shall reject an
  invalid vignette with a precise, actionable error rather than a partial or silent load.
- **Rationale:** "Invalid scenario data fails loudly at load" is a stated error-handling posture
  (GDS-01 §10; GDS-04 §9; build-spec/02 §5.5 FR-S3).
- **Priority:** Must
- **Inputs:** A vignette file.
- **Outputs:** Either a successfully loaded `WorldState`, or a rejection with a specific error
  identifying the failing element.
- **Preconditions:** None.
- **Postconditions:** No partially loaded `WorldState` exists after a failed validation.
- **Acceptance Criteria:** Given a vignette referencing a non-existent asset template, the load is
  rejected and the error identifies the missing template by name.
- **Verification Method:** Test
- **Dependencies:** None
- **Source Documents:** GDS-04 §1.1 "Constraints", §9; build-spec/02 §5.5 FR-S3 (binding
  statement).
- **Related ADRs:** ADR-0007
- **Related Interfaces:** INT-0011
- **Related Requirements:** FR-4110, FR-5210

---

## FR-6000 — Session, Multiplayer & Fog-of-War

### FR-6100 — SessionAPI as the single seam

#### FR-6110 — All non-engine access routed through SessionAPI

- **ID:** FR-6110
- **Title:** Route all simulation state/control access through the Session Layer seam
- **Description:** The system shall require that every access to simulation state or control from
  the Operator Console, AI-Red, or AAR/replay pass through the Session Layer's single seam; no
  component other than the Session Layer shall hold a direct structural dependency on engine
  internals from outside the engine.
- **Rationale:** A single seam keeps the engine UI-agnostic and presentation swappable
  (`CLAUDE.md` invariant 2; ADR-0003).
- **Priority:** Must
- **Inputs:** Any operator/White-Cell/AI-Red/AAR request.
- **Outputs:** A `CellView`/god-view/AAR/Ack response.
- **Preconditions:** A constructed Session object.
- **Postconditions:** Every mutating call is logged to the `EventLog`.
- **Acceptance Criteria:** A static review of the Operator Console codebase confirms no import of
  an engine-internal module outside the Session Layer's seam.
- **Verification Method:** Inspection
- **Dependencies:** None
- **Source Documents:** GDS-03 §2.2, §2.4; ICD INT-0006; ADR-0002, ADR-0003.
- **Related ADRs:** ADR-0002, ADR-0003
- **Related Interfaces:** INT-0006
- **Related Requirements:** FR-6200

### FR-6200 — Fog-of-war at the boundary

#### FR-6210 — Cell-scoped views filtered server-side

- **ID:** FR-6210
- **Title:** Filter every cell-scoped view at the session-layer boundary
- **Description:** The system shall produce each cell's view of the world (`CellView`) by filtering
  ground truth at the Session Layer boundary, exposing only that cell's own assets, held tracks,
  perceivable effects, and addressed messages; no cell-scoped interface shall expose another
  cell's private data.
- **Rationale:** Fog-of-war enforced at the boundary, not by the UI withholding data, is a
  load-bearing invariant (`CLAUDE.md` invariant 3; ADR-0004).
- **Priority:** Must
- **Inputs:** Ground-truth `WorldState`; the requesting cell identity.
- **Outputs:** A `CellView` scoped to that cell.
- **Preconditions:** A `WorldState` exists.
- **Postconditions:** No field of another cell's private state appears in the returned `CellView`.
- **Acceptance Criteria:** Given Red and Blue cells with disjoint custody, a request for Blue's
  `CellView` never includes a Red-only `Track` that Blue has no custody of.
- **Verification Method:** Test
- **Dependencies:** FR-6110, FR-1510
- **Source Documents:** GDS-04 §8 Fog-of-war view model; ICD INT-0007; ADR-0004.
- **Related ADRs:** ADR-0004
- **Related Interfaces:** INT-0006, INT-0007
- **Related Requirements:** FR-6110, FR-1510, FR-4610

#### FR-6220 — Documented no-cell ground-truth exception

- **ID:** FR-6220
- **Title:** Permit a documented, named set of no-cell ground-truth endpoints
- **Description:** The system shall permit exactly the documented set of no-cell, ground-truth-
  exposing interfaces (god-view, event log, save, AAR, objectives-equivalent flows) to bypass
  per-cell filtering, as an explicit, accepted v1 trust-boundary exception rather than an
  unbounded one.
- **Rationale:** The LAN trust model names this exception explicitly rather than leaving it as an
  unaudited gap (GDS-01 §4; ADR-0015).
- **Priority:** Must
- **Inputs:** A request to one of the named no-cell endpoints.
- **Outputs:** Ground-truth data, unfiltered.
- **Preconditions:** None — no per-cell binding is required for these specific endpoints by design.
- **Postconditions:** No interface outside this explicitly named set bypasses cell filtering.
- **Acceptance Criteria:** A static review confirms the unfiltered-access exception applies only
  to the named endpoint set and no other.
- **Verification Method:** Inspection
- **Dependencies:** FR-6210
- **Source Documents:** GDS-01 §4 "Trust model"; `CLAUDE.md` "LAN trust model"; ADR-0015.
- **Related ADRs:** ADR-0004, ADR-0015
- **Related Interfaces:** INT-0001, INT-0005
- **Related Requirements:** FR-6210

### FR-6300 — Server-authoritative multiplayer clock and locking

#### FR-6310 — Server-authoritative lazy clock shared across connections

- **ID:** FR-6310
- **Title:** Advance the session clock exactly once regardless of connected client count
- **Description:** The system shall advance a session's simulated clock exactly once per real-time
  interval regardless of how many browser clients are connected, using a server-authoritative
  lazy-catch-up mechanism rather than a per-client clock.
- **Rationale:** Multiple LAN-connected clients must observe one consistent session timeline
  (GDS-01 §8; ADR-0014).
- **Priority:** Must
- **Inputs:** Any read request from any connected client; the session's wall-clock anchor and
  rate.
- **Outputs:** A caught-up `WorldState` consistent across all clients' simultaneous reads.
- **Preconditions:** A running, multi-client-connected session.
- **Postconditions:** Two clients reading at the same wall-clock instant observe the same
  simulated time.
- **Acceptance Criteria:** Given two simulated clients polling the same session concurrently, both
  observe an identical simulated clock value for reads issued within the same catch-up cycle.
- **Verification Method:** Test
- **Dependencies:** FR-1110
- **Source Documents:** GDS-01 §8; `CLAUDE.md` "Multiplayer workflow"; ADR-0014.
- **Related ADRs:** ADR-0014, ADR-0026
- **Related Interfaces:** INT-0001, INT-0006
- **Related Requirements:** FR-1110, FR-4310

#### FR-6320 — Per-session mutation locking

- **ID:** FR-6320
- **Title:** Serialize concurrent mutations to a session
- **Description:** The system shall serialize all state-mutating operations against a given session
  using a per-session lock, preventing two concurrent requests from corrupting shared session
  state.
- **Rationale:** LAN-cooperative play allows concurrent requests from multiple seats; serialized
  mutation is required for a consistent, deterministic state (ADR-0014).
- **Priority:** Must
- **Inputs:** Two or more concurrent mutating requests against the same session.
- **Outputs:** Sequential application of each mutation, in receipt order.
- **Preconditions:** A running session.
- **Postconditions:** No interleaved partial mutation is ever observable.
- **Acceptance Criteria:** Given two concurrent order-submission requests against the same Asset,
  both are applied sequentially with no lost update.
- **Verification Method:** Test
- **Dependencies:** FR-6310
- **Source Documents:** ADR-0014; ADR-0026 (the ~16-participant LAN concurrency ceiling this
  locking design targets).
- **Related ADRs:** ADR-0014, ADR-0026
- **Related Interfaces:** INT-0006
- **Related Requirements:** FR-6310

### FR-6400 — Hot-seat and LAN-cooperative session sharing

#### FR-6410 — One Session object shared across hot-seat and LAN modes

- **ID:** FR-6410
- **Title:** Serve both hot-seat and LAN-cooperative play from one session model
- **Description:** The system shall support both single-browser hot-seat play and multi-tab/
  multi-machine LAN-cooperative play from the same underlying Session object, differing only in how
  many browser clients are connected, not in the session model itself.
- **Rationale:** Both modes are explicitly clarified as sharing one Session object, not two
  distinct models (GDS-01 §8 "Review reconciliation").
- **Priority:** Must
- **Inputs:** One or more browser client connections to the same session identifier.
- **Outputs:** A consistent session state visible to every connected client.
- **Preconditions:** A started session with a shareable URL/session identifier.
- **Postconditions:** No behavioral divergence in session semantics between one connected client
  and several.
- **Acceptance Criteria:** Given the same sequence of operator actions issued first via a single
  hot-seat browser and then via multiple LAN-connected browsers, the resulting `WorldState` is
  identical in both cases.
- **Verification Method:** Test
- **Dependencies:** FR-6310
- **Source Documents:** GDS-01 §8; ADR-0014.
- **Related ADRs:** ADR-0014
- **Related Interfaces:** INT-0001, INT-0006
- **Related Requirements:** FR-6310

### FR-6500 — Observer read-only access

#### FR-6510 — Observer read-only view with no command ability

- **ID:** FR-6510
- **Title:** Provide Observers a White-Cell-designated read-only view
- **Description:** The system shall give an Observer seat a read-only view — either god-view or a
  specific cell's `CellView`, as designated by White Cell — with no ability to issue any
  command-kind or collection-kind action.
- **Rationale:** Observers are explicitly assessment/learning roles with no command authority
  (GDS-01 §2; build-spec/02 §6 OR-5).
- **Priority:** Must
- **Inputs:** White Cell's view-designation for the Observer seat; the Observer's read requests.
- **Outputs:** The designated view, read-only.
- **Preconditions:** White Cell has set the Observer's view designation.
- **Postconditions:** No mutating request submitted by an Observer-seated session is ever applied.
- **Acceptance Criteria:** Given an Observer-seated session attempting to submit a command, the
  request is rejected and no `WorldState` change occurs.
- **Verification Method:** Test
- **Dependencies:** FR-6210
- **Source Documents:** GDS-01 §2; GDS-02 §2 row 5; ICD INT-0005; build-spec/02 §6 OR-5 (binding
  statement).
- **Related ADRs:** ADR-0004
- **Related Interfaces:** INT-0005, INT-0006
- **Related Requirements:** FR-6210

### FR-6600 — Hot-seat hand-off and screen-blank menu

#### FR-6610 — Screen-blank pending-handoff menu between hot-seat role changes

- **ID:** FR-6610
- **Title:** Blank sensitive content during a pending hot-seat role hand-off
- **Description:** The system shall, when a hot-seat role change is pending (the current seat's
  occupancy has ended and a new seat has not yet been selected), blank the previously displayed
  cell's sensitive content and present a seat-selection menu, until a seat is selected.
- **Rationale:** GDS-05 OR-3 requires a "blank screen / hand off" menu between hot-seat role
  changes so a departing operator's belief state is not left visible to the next person at the
  keyboard; this leaf closes GDS-05's own Open Question 1 (OQ1), which records that no FR leaf
  previously covered this behavior (GDS-05 "Operational Rules" OR-3, OQ1; build-spec/02 §6 OR-3).
- **Priority:** Must
- **Inputs:** A hot-seat role-change/hand-off trigger (e.g., a seat-relinquish action).
- **Outputs:** A seat-selection menu, with no prior cell's sensitive content visible.
- **Preconditions:** An active session; a hot-seat role change is pending.
- **Postconditions:** No previously displayed cell's sensitive content remains visible once the
  hand-off menu is shown; the menu persists until a seat is selected.
- **Acceptance Criteria:** Given a hot-seat hand-off from Red to Blue on the same browser, no
  Red-cell data remains on screen once the hand-off menu is shown, and none reappears until a seat
  is explicitly selected.
- **Verification Method:** Demonstration
- **Dependencies:** FR-6410
- **Source Documents:** GDS-05 "Operational Rules" OR-3 (OQ1); build-spec/02 §6 OR-3.
- **Related ADRs:** ADR-0004
- **Related Interfaces:** INT-0001, INT-0006
- **Related Requirements:** FR-6410, FR-6210

---

## FR-7000 — Logging, Replay & After-Action Review

### FR-7100 — Event log

#### FR-7110 — Ordered, timestamped event log of every state-changing event

- **ID:** FR-7110
- **Title:** Append every state-changing event to an ordered event log
- **Description:** The system shall append every state-changing event — orders, executions,
  effects, injects, White-Cell controls, time controls — to an ordered, simulated-time-stamped
  event log, sufficient to deterministically reconstruct the exercise.
- **Rationale:** The event log is the foundation for replay, AAR, and CSV/branch-to-live
  capabilities (GDS-01 §7; build-spec/02 §5.6 FR-L1, FR-L2).
- **Priority:** Must
- **Inputs:** Every state-changing event as it occurs.
- **Outputs:** An appended, ordered `EventLogEntry`.
- **Preconditions:** A running session.
- **Postconditions:** The log's entries are sufficient, combined with the initial state and seed,
  to reproduce the exercise exactly (FR-1120).
- **Acceptance Criteria:** Given a completed exercise's event log, replaying it from the initial
  state reproduces a `WorldState` history identical to the one recorded live.
- **Verification Method:** Test
- **Dependencies:** FR-1120
- **Source Documents:** GDS-04 §7 `EventLogEntry`; build-spec/02 §5.6 FR-L1 (binding statement).
- **Related ADRs:** ADR-0002
- **Related Interfaces:** INT-0008, INT-0014
- **Related Requirements:** FR-1120, FR-7200, FR-7300

### FR-7200 — Save and resume

#### FR-7210 — Deterministic save-file round trip

- **ID:** FR-7210
- **Title:** Save and resume a session deterministically
- **Description:** The system shall persist a complete session snapshot — `WorldState`, full
  `EventLog`, Snapshots, Role Assignments — on demand or at exercise end, and shall reproduce the
  exact saved state when that save is loaded by a later session.
- **Rationale:** Save/resume is required for multi-sitting exercises and is split in ownership
  between the act of saving and the on-disk format (ADR-0022).
- **Priority:** Must
- **Inputs:** A save request against a running/completed session; a save file for a resume
  request.
- **Outputs:** A save file on disk; on resume, a reconstructed `WorldState` matching the saved
  state.
- **Preconditions:** A running or completed Session, for save; a valid save file, for resume.
- **Postconditions:** A resumed session's state is identical to the state at the moment of save.
- **Acceptance Criteria:** Given a session saved at sim time T and immediately resumed, the
  resumed `WorldState` is identical to the pre-save `WorldState` at T.
- **Verification Method:** Test
- **Dependencies:** FR-7110
- **Source Documents:** GDS-04 §1.14 Session "Persistent state"; ICD INT-0012; ADR-0022.
- **Related ADRs:** ADR-0022
- **Related Interfaces:** INT-0012
- **Related Requirements:** FR-7110, FR-4410, FR-7220

#### FR-7220 — Save-file content/session ownership split

- **ID:** FR-7220
- **Title:** Distinguish and independently re-import a save file's content portion from its
  session portion
- **Description:** The system shall structure a save file such that its Vignette/content portion
  (force lay-down, templates, and parameters as originally loaded) is distinguishable from, and
  independently re-importable apart from, its Session/event-log portion (`WorldState` history,
  `EventLog`, Snapshots, Role Assignments).
- **Rationale:** ADR-0022 splits save-file ownership between the act of saving (Session Layer) and
  the resulting on-disk content boundary (Content & Data); this leaf asserts that split as an
  enforced, testable invariant rather than assumed background, closing ICD §7 issue 4's "ambiguous
  ownership" flag at the requirements level (ADR-0022; ICD INT-0012, §7 issue 4).
- **Priority:** Must
- **Inputs:** A save file produced by FR-7210.
- **Outputs:** A separately extractable content portion and session portion from the same save
  file.
- **Preconditions:** A save file produced per FR-7210.
- **Postconditions:** The content portion of a save file can be loaded as a fresh vignette's
  starting state without that save's session/event-log history; the two portions are never merged
  into an undifferentiated blob.
- **Acceptance Criteria:** Given a save file, the Vignette/content portion can be extracted and
  loaded as a new session's starting vignette independent of the original session's event log.
- **Verification Method:** Test
- **Dependencies:** FR-7210
- **Source Documents:** ADR-0022; ICD INT-0012, §7 issue 4.
- **Related ADRs:** ADR-0022
- **Related Interfaces:** INT-0011, INT-0012
- **Related Requirements:** FR-7210

### FR-7300 — AAR replay, scrub, and branch-compare

#### FR-7310 — Read-only replay/scrub without disturbing the live session

- **ID:** FR-7310
- **Title:** Replay and scrub the event log read-only
- **Description:** The system shall allow White Cell (and Observer, where designated) to replay the
  event log and scrub to any point in simulated time, read-only, without altering the live
  session's state.
- **Rationale:** AAR replay is explicitly read-only against the engine (GDS-01 §5 step 5; ICD
  INT-0014).
- **Priority:** Must
- **Inputs:** A scrub-to-time request against a completed or in-progress session's event log.
- **Outputs:** A reconstructed `WorldState` at the requested point, for display only.
- **Preconditions:** A non-empty `EventLog`.
- **Postconditions:** The live session's `WorldState`/clock is unaffected by a replay/scrub
  request.
- **Acceptance Criteria:** Given a live session at sim time T, issuing a scrub-to-`T-100s` request
  does not change the live session's clock or `WorldState`; the live session remains at T.
- **Verification Method:** Test
- **Dependencies:** FR-7110
- **Source Documents:** GDS-01 §5 step 5; ICD INT-0014; ADR-0002.
- **Related ADRs:** ADR-0002
- **Related Interfaces:** INT-0014
- **Related Requirements:** FR-7110, FR-1120

#### FR-7320 — Branch comparison

- **ID:** FR-7320
- **Title:** Compare two branches from a common rewind point
- **Description:** The system shall allow comparison of two diverging branches of an exercise from
  a common rewind point, to show how a decision changed the outcome.
- **Rationale:** Branch-compare is named as a specific AAR capability supporting after-action
  learning (GDS-01 §5 step 5).
- **Priority:** Should
- **Inputs:** Two event-log branches sharing a common ancestor point.
- **Outputs:** A comparative view of both branches' divergent state/outcomes.
- **Preconditions:** Both branches share a common rewind point in their event-log history.
- **Postconditions:** Neither branch's underlying event log is altered by the comparison.
- **Acceptance Criteria:** Given two branches diverging at sim time T, the comparison view
  correctly attributes each branch's post-T state to its own event log.
- **Verification Method:** Test
- **Dependencies:** FR-7310
- **Source Documents:** GDS-01 §5 step 5; GDS-01 §8 "Replay/AAR mode."
- **Related ADRs:** ADR-0002
- **Related Interfaces:** INT-0014
- **Related Requirements:** FR-7310

---

## FR-8000 — Operator Console Presentation

### FR-8100 — Browser-based presentation over the SessionAPI

#### FR-8110 — Browser/web presentation layer

- **ID:** FR-8110
- **Title:** Present the operator console as a browser-based web application
- **Description:** The system shall present all human-facing interaction (White Cell, Blue, Red,
  Observer) through a browser-based web client communicating with a FastAPI server process, rather
  than a desktop GUI toolkit.
- **Rationale:** FastAPI + browser presentation is the selected architecture, superseding an
  earlier PyQt option, because it makes the LAN-multiplayer seam nearly free (GDS-03 §2.4;
  ADR-0008).
- **Priority:** Must
- **Inputs:** Operator/White-Cell interaction in a standards-compliant browser.
- **Outputs:** A rendered belief view; submitted intents to the server.
- **Preconditions:** A standards-compliant browser; the server process running.
- **Postconditions:** No interaction path requires a non-browser desktop client.
- **Acceptance Criteria:** Every documented user-facing capability in this baseline is reachable
  through a standards-compliant browser session against the running server.
- **Verification Method:** Demonstration
- **Dependencies:** None
- **Source Documents:** GDS-03 §2.4; ICD INT-0001; ADR-0008.
- **Related ADRs:** ADR-0008
- **Related Interfaces:** INT-0001
- **Related Requirements:** FR-6110

---

## FR-9000 — AI-Red

### FR-9100 — Doctrine-preset-driven Red automation

#### FR-9110 — AI-Red issues Planned Activities per a doctrine preset

- **ID:** FR-9110
- **Title:** Generate Red Planned Activities from a doctrine preset
- **Description:** The system shall, when Red's seat is configured to use an AI-Red preset instead
  of a human operator, generate Planned Activities on Red's behalf consistent with the configured
  doctrine preset (`russia_ew_first`, `china_integrated`, or `generic`), issued through the same
  path a human Red operator's activities would take.
- **Rationale:** AI-Red is a documented session-layer feature substituting for an unseated/
  facilitator-played Red cell (GDS-01 §8; ADR-0021). Priority is Should, not Must, because a
  vignette remains fully playable with a human-seated or facilitator-played Red cell; AI-Red is a
  valuable convenience for under-staffed exercises, not a precondition for any vignette's
  playability, unlike the Must-tier leaves it depends on (FR-3110, FR-3410). AI-Red's direct
  ground-truth read (INT-0015) is also a named, accepted v1 trade-off against the fog-of-war-
  filtered `CellView` a human Red operator uses — this epistemic asymmetry is intentionally not
  remediated in v1 and remains a tracked future-work gap, not an oversight (ADR-0024;
  `FUTURE-WORK.md` §1 "AI-Red fog-of-war parity").
- **Priority:** Should
- **Inputs:** The configured doctrine preset; current `WorldState` (read directly — see Related
  Interfaces note below).
- **Outputs:** Red-attributed Planned Activities, created exactly as if issued by a human.
- **Preconditions:** Red's seat is configured to use an AI-Red preset rather than a human operator;
  this configuration is mutually exclusive with a human operator concurrently occupying the same
  Role Assignment — AI-Red substitutes for an unseated Red, it does not run as a parallel,
  simultaneous source alongside a human-seated Red.
- **Postconditions:** AI-Red-issued Planned Activities are indistinguishable, in the event log,
  from human-Red-issued activities of the same kind.
- **Acceptance Criteria:** Given an AI-Red-controlled Red seat under the `china_integrated` preset,
  the resulting Planned Activities are consistent with that preset's doctrinal profile and pass
  the same execute-time re-validation (FR-3410) as a human-issued activity.
- **Verification Method:** Test
- **Dependencies:** FR-3110, FR-3410
- **Source Documents:** GDS-01 §8; GDS-03 §2.2 "Responsibilities"; ICD INT-0015; ADR-0021.
- **Related ADRs:** ADR-0021, ADR-0024, ADR-0030 *(added 2026-07: ADR-0030 generalizes the
  determinism-placement rule ADR-0021 already applies to AI-Red specifically — see
  `reviews/requirements-update-report.md`)*
- **Related Interfaces:** INT-0008, INT-0015
- **Related Requirements:** FR-3110, FR-3410

---

## FR-10000 — Assessment & Research Instrumentation *(new 2026-07, DOM-002/004/005 backfill)*

**Numbering note:** every leading digit 1–9 is already claimed by a top-level category above
(FR-1000 Simulation Engine Core through FR-9000 AI-Red), so this category — added by the
2026-07 DOM-002/004/005 backfill pass, once `ADR-0032`/`ADR-0033` resolved the conflicts that
originally routed its content to `CR-19`/`CR-20` — extends the scheme to a 5-digit leaf ID rather
than reuse or renumber an existing 4-digit bucket. See `reviews/requirements-domain-backfill-
report.md` and `reviews/requirements-adr-conflict-resolution-report.md` for the full derivation.

### FR-10100 — Competency assessment rubric

#### FR-10110 — Automated non-aggregating competency rubric-tier computation

- **ID:** FR-10110
- **Title:** Compute per-dimension rubric-tier competency results without aggregating into a score
- **Description:** The system shall compute, for each cell per exercise, a qualitative rubric-tier
  result for each implemented measurement dimension (custody quality, window discipline, and
  belief-truth divergence in the first iteration; resource economy, escalation discipline, and
  time-to-decision deferred per FS-201's own stated scope), derived read-only from existing
  eventlog/custody/order-log/AAR-snapshot state, and shall never aggregate these per-dimension
  results into a single composite score, ranking, or win/loss determination.
- **Rationale:** DOM-002 §§3–6 names this as the capability that replaces the engine's binary
  objective-flip signal with a richer measurement of *how* a cell demonstrated a vignette's
  intended competency; FS-201 elaborates it in full. `ADR-0032` carves this specific design —
  non-adjudicative, non-aggregating, purely descriptive — out of `ADR-0017`'s "no automated
  scoring or assessment mechanism" prohibition; `FR-4710`'s prohibition on a composite score/
  win-loss determination is explicitly unaffected and remains the boundary this requirement must
  not cross.
- **Priority:** Should — valuable for facilitator debrief and longitudinal tracking, but (like
  `FR-9110` AI-Red) not a precondition for any existing vignette's playability; every vignette
  remains fully playable with only the pre-existing binary objective-flip signal.
- **Inputs:** `Track` confidence history at time of action vs. decision (custody quality);
  `OrderSystem` rejection rate / `dry_run()` usage pattern (window discipline); AAR's `snapshot_at()`
  god-view/belief-view diff (belief-truth divergence).
- **Outputs:** A rubric-tier result (one of a small set of qualitative tiers per dimension, e.g.
  "speculative / adequate / disciplined" for custody quality) per implemented dimension, per cell,
  per exercise.
- **Preconditions:** A completed or in-progress exercise with eventlog, custody, order-log, and AAR
  snapshot data available.
- **Postconditions:** The computation produces no `WorldState` mutation; no per-dimension result is
  ever aggregated into a single composite score, ranking, or win/loss determination.
- **Acceptance Criteria:** Given a completed exercise, the per-cell per-exercise report presents
  rubric-tier results for the three first-iteration dimensions side-by-side for both cells without
  collapsing them into one number; the computation produces zero `WorldState` mutations across an
  arbitrary number of invocations.
- **Verification Method:** Test
- **Dependencies:** FR-1510, FR-3410, FR-7310
- **Source Documents:** DOM-002 §§3–6; FS-201 (Scope, System Behaviour, Acceptance Criteria);
  ADR-0032.
- **Related ADRs:** ADR-0017, ADR-0032
- **Related Interfaces:** None — no ICD interface currently names this scoring/report boundary;
  FS-201's own Open Questions flag the same gap. Left `UNASSIGNED` in the traceability matrix
  rather than guessed.
- **Related Requirements:** FR-4710 (the sibling prohibition this requirement must not cross),
  FR-1510, FR-3410, FR-7310

### FR-10200 — Research analytics export

#### FR-10210 — Multi-run/cohort structured research-data export

- **ID:** FR-10210
- **Title:** Export structured, condition-labeled records across many seeded runs
- **Description:** The system shall support batch execution of N seeded simulations of a given
  vignette and shall export, for each run, a structured record containing the vignette identifier,
  the seed, an experimenter-supplied condition label, and that run's `FR-10110` rubric-tier
  results, without relaxing engine determinism to characterize run-to-run variability.
- **Rationale:** DOM-004 §5 names this as the capability closing the stated gap that "a researcher
  today would have to script directly against `eventlog`/`save` artifacts"; FS-301 elaborates it
  in full. `ADR-0033` supersedes `ADR-0029` (which had previously rejected exactly this dedicated
  export/analysis interface) to authorize it.
- **Priority:** Should — valuable for instrument-grade research use, but not a precondition for
  standard PME exercise play; no existing vignette or training workflow depends on it.
- **Inputs:** A vignette identifier; a set/range of seeds; an experimenter-supplied condition
  label; per-run `FR-10110` output.
- **Outputs:** A structured multi-run export artifact — one record per run, each carrying its
  vignette ID, seed, condition label, and `FR-10110` rubric-tier results.
- **Preconditions:** `FR-10110` rubric computation is available for each run in the batch.
- **Postconditions:** Each seeded run remains independently, byte-identically reproducible; no
  non-determinism is introduced within or between runs to characterize variability — variability
  is sampled by driving the engine across many seeds externally (DOM-005 §6), never by relaxing
  `engine/`'s own determinism.
- **Acceptance Criteria:** Given a batch of N seeded runs of the same vignette, the exported record
  set contains exactly N entries, each tagged with its own seed/vignette-ID/condition label and
  `FR-10110` output; re-running the same seed against the same vignette reproduces byte-identical
  underlying state (verified via the existing determinism property test's own mechanism).
- **Verification Method:** Test
- **Dependencies:** FR-10110, FR-1120
- **Source Documents:** DOM-004 §§4–6; FS-301 (Scope, System Behaviour); ADR-0033.
- **Related ADRs:** ADR-0029 (superseded), ADR-0033
- **Related Interfaces:** None — no ICD interface currently names this export boundary; FS-301's
  own Open Questions flag the same gap. Left `UNASSIGNED` in the traceability matrix rather than
  guessed.
- **Related Requirements:** FR-10110, FR-1120

**Explicitly not authorized by this category:** any human-subjects-research feature (cross-
institution or de-identified trainee data collection) remains out of scope without separate
authorization and the institution's own IRB/ethics process — `CR-21` records this boundary and is
unaffected by `FR-10110`/`FR-10210`'s addition.

---

## Candidate Requirements

The following read as requirements but cannot be traced to a settled statement in this baseline's
authoritative inputs — each corresponds to an Open Question left explicitly unresolved in GDS-01,
GDS-04, or the ICD. They are excluded from the numbered FR-1xxx baseline above and from any future
traceability matrix's baseline rows.

- **CR-01 — AI-Red fog-of-war parity.** AI-Red currently reads `WorldState` directly rather than
  through a fog-of-war-filtered `CellView` (ICD INT-0015; ADR-0024 records this as a tracked
  future-work gap, not settled behavior). A requirement that AI-Red's reads be parity-filtered like
  a human Red operator's cannot be written today because no approved document commits to *when* or
  *how* this gap closes. **Source:** ADR-0024; `FUTURE-WORK.md` §1 "AI-Red fog-of-war parity."
- **CR-02 — Per-connection / per-cell authentication.** The LAN trust model is explicitly
  client-side trust with no per-connection authentication (ADR-0015; ICD INT-0001 Open question 2).
  A requirement to authenticate cell selection cannot be written because no approved document
  commits to adding it — it is named only as a documented v1 limitation. **Source:** ADR-0015;
  ConOps §4, §12 risk table.
- **CR-03 — Push-based (WebSocket) state delivery.** ICD §7 issue 11 notes a documented-but-not-
  built future WebSocket push migration exists only in a non-binding pre-GDS design note
  (`design/07-api-and-networking.md`), not in any approved GDS/ADR document. **Source:** ICD §7
  issue 11.
- **CR-04 — Command-relationship layering (OPCON/TACON-equivalent).** ConOps §13 Open Question 7
  explicitly leaves this as an unresolved design question, not a committed capability. **Source:**
  GDS-01 §13 Open Question 7.
- **CR-05 — Resilience under sustained, multi-front degradation.** ConOps §13 Open Question 8
  explicitly leaves open whether/how the system should model sustained denial beyond a single
  fault event. **Source:** GDS-01 §13 Open Question 8.
- **CR-06 — Observer mid-exercise reassignment.** ConOps §13 Open Question 3 leaves unresolved
  whether an Observer's view assignment can change after session start. **Source:** GDS-01 §13
  Open Question 3.
- **CR-07 — AI-Red doctrine-preset selection guidance.** ConOps §13 Open Question 4 notes no
  document states *which* preset to choose for a given training objective; this is guidance, not a
  system behavior, and no approved document commits the system itself to providing it.
  **Source:** GDS-01 §13 Open Question 4.
- **CR-08 — Save-file/Snapshot cross-version compatibility.** GDS-04 Open Question 4 (restated in
  ICD §7 issue 7) leaves open whether a save produced by one engine build is expected to load under
  a later build — no approved document commits to a compatibility guarantee, so FR-7210 above is
  scoped only to same-build round trips. **Source:** GDS-04 §10 Open Question 4; ICD §7 issue 7.
- **CR-09 — Unified supertype for Planned Activity and SSN Request.** GDS-04 Open Question 3
  (restated in ICD §7 issue 6) leaves open whether these two "request now, result later" entities
  should share a formal supertype; no approved document commits to such a refactor. **Source:**
  GDS-04 §10 Open Question 3; ICD §7 issue 6.
- **CR-10 — AccessWindow as a persisted vs. derived entity.** GDS-04 Open Question 2 (restated in
  ICD §7 issue 5) leaves open whether `AccessWindow` must be a stored record for some future AAR
  display, or remains purely recomputed; no approved document commits either way. **Source:**
  GDS-04 §10 Open Question 2; ICD §7 issue 5.
- **CR-11 — Partial vignette-authoring state ownership.** ICD §7 issue 10 flags that where
  in-progress, unsaved vignette-builder state lives (server-session-scoped vs. browser-local) is
  unstated by any approved document — this may indicate a missing interface, not merely a missing
  requirement detail. **Source:** ICD §7 issue 10.

**CR-12–CR-18 added 2026-07**, following `reviews/strategic-review-2026-07.md`'s disposition in
`reviews/architecture-update.md`: each corresponds to a candidate component/concept that pass added
to GDS-02/03/04 explicitly marked "not built, not scheduled, not committed" — the same evidentiary
status as CR-01–CR-11 above, just newly named rather than newly built. See
`reviews/requirements-update-report.md` for the full derivation.

**CR-19–CR-21 added 2026-07**, following a `requirements-engineering` pass against DOM-002
(Assessment Framework), DOM-004 (Research Framework), and DOM-005 (Validation Framework) —
closing `docs/feature-planning/05-feature-review.md` Finding F-01 (these domains ground shipped
Feature Specifications FS-201/FS-202/FS-301 with zero corresponding requirement anywhere in this
baseline). See "DOM-002/004/005 backfill" near the end of this document and
`reviews/requirements-domain-backfill-report.md` for the full analysis. **CR-19 and CR-20 were
subsequently promoted to the numbered baseline** (see `## FR-10000` above) once the project owner
resolved their blocking ADR conflicts via `ADR-0032`/`ADR-0033` — retained below, marked
`PROMOTED`, for audit-trail continuity rather than deleted. **CR-21 remains a Candidate**, unaffected
by that promotion.

- **CR-19 — Automated competency-assessment rubric computation. `PROMOTED 2026-07 → FR-10110`,
  once `ADR-0032` resolved the blocking conflict below.** DOM-002 §§3–6 and FS-201 describe an
  always-available, automated computation of qualitative rubric tiers (custody quality, window
  discipline, belief-truth divergence, …) per cell per exercise. This could not be written as a
  baselined FR when first identified because it was in direct tension with two Accepted decisions:
  ADR-0017 ("No automated scoring or assessment mechanism exists in v1... outcomes are adjudicated
  and narrated by the White Cell facilitator") and FR-4710 above (already baselined: "the system
  shall not compute or display an automated score or win/loss determination"). DOM-002 §5
  deliberately designed the rubric to avoid a single composite score specifically to distinguish
  "rubric-tier reporting" from "scoring/win-loss" — the project owner resolved this by amending
  ADR-0017 with a narrow carve-out (`ADR-0032`) rather than rescoping FS-201 or rejecting the
  capability. **Source:** DOM-002 §§3–6; FS-201 (Scope, System Behaviour); ADR-0017; ADR-0032;
  FR-4710 (this document); `IP-2010`'s header note.
- **CR-20 — Dedicated multi-run/cohort research-export interface. `PROMOTED 2026-07 → FR-10210`,
  once `ADR-0033` resolved the blocking conflict below.** DOM-004 §5 and FS-301 describe a
  purpose-built export/cohort-management layer (structured per-run records with condition-label
  metadata, across many seeded runs) to close the stated gap that "a researcher today would have
  to script directly against `eventlog`/`save` artifacts." This could not be written as a
  baselined FR when first identified because it directly conflicted with an Accepted decision:
  ADR-0029 ("Raw AAR/event-log access... plus the existing CSV/JSON export at
  `/api/sessions/{sid}/aar/export.{csv,json}`... is treated as sufficient for the researchers/
  assessment-designers stakeholder... no new dedicated export/analysis interface or owning
  subsystem is introduced"). ADR-0029's own Alternatives Considered section explicitly named and
  rejected "introduce a dedicated export/analysis interface for assessment designers" — precisely
  what FS-301 proposes. The project owner resolved this by superseding ADR-0029 outright
  (`ADR-0033`), authorizing the dedicated interface FS-301 originally proposed. **Source:** DOM-004
  §5; FS-301 (Scope, User Workflows); ADR-0029 (superseded); ADR-0033.
- **CR-21 — Human-subjects research authorization/ethics boundary.** DOM-004 §6 states that any
  future feature enabling human-subjects research (e.g., cross-institution de-identified trainee
  data collection) requires separate authorization and the institution's own IRB/ethics process,
  and "must not be assumed authorized merely because this framework describes the capability gap."
  This is not in conflict with any ADR, but no approved document commits the system to *any*
  concrete human-subjects-research feature today — `FR-10110`/`FR-10210` (promoted from CR-19/CR-20
  above) are structured-aggregate assessment/export capabilities, not a human-subjects research
  program in the IRB sense, so this boundary remains unaddressed by their promotion. A requirement
  would still be vacuous until a concrete human-subjects-research feature is proposed; recorded
  here so the constraint is not silently forgotten if/when one is. **Source:** DOM-004 §6.

- **CR-12 — Proliferated-Constellation Aggregation Layer.** No layer/mesh-level tasking, health
  rollup, or aggregated-custody construct exists for constellations larger than the ≤3-satellite cap
  (ADR-0019); a proliferated architecture (tens to hundreds of objects) cannot be represented without
  per-asset drill-down times N. A requirement committing the system to represent proliferated
  constellations cannot be written today because no approved document commits to building this
  layer — it is named only as a not-built, not-scheduled candidate component. **Source:** GDS-03 §5
  "Proliferated-Constellation Aggregation Layer"; `strategic-review-2026-07.md` §6.3 R13, FC-06,
  GAP-10; `FUTURE-WORK.md` §13.
- **CR-13 — Coalition / Multi-Cell Generalization.** The Session/CellController model grants Role
  Assignments against exactly Blue and Red (plus White/Observer); no releasability tiers, per-nation
  ROE, or coalition SSN pooling exist for multiple Blue-side cells. A requirement to generalize
  fog-of-war to N cells with asymmetric information-sharing policies cannot be written today because
  no approved document commits to it. **Source:** GDS-03 §5 "Coalition / Multi-Cell
  Generalization"; GDS-04 §3 "Coalition Cell / Multi-Blue Structure"; GDS-02 Open Question 5
  (coalition-partner actor); `strategic-review-2026-07.md` §6.3 R14, FC-09; `FUTURE-WORK.md` §13.
- **CR-14 — Commercial / Gray-Actor Class and purchasable SDA/comms services.** Asset ownership is
  binary (`blue`/`red`/`neutral`, GDS-04 §1.2); no actor class exists for a commercial operator whose
  custody data or SATCOM/imagery services either cell could lease, or whose assets present a
  targeting/attribution dilemma distinct from a state actor's. A requirement to add a commercial SDA
  feed to the mock SSN or a commercial actor class cannot be written today because no approved
  document commits to either. **Source:** GDS-02 candidate future external systems table
  ("Commercial SDA/services provider"); GDS-03 §5 "Commercial / Gray-Actor Class"; GDS-04 §3
  "Commercial / Gray Actor"; [Strategic Assumptions Register](../architecture/strategic-assumptions-register.md)
  A3; `strategic-review-2026-07.md` §1.7, §6.2 R11, FC-10, GAP-03; `FUTURE-WORK.md` §7, §13.
- **CR-15 — Campaign / Session-Persistence Container.** Session is the largest unit of persistent
  state and ends at `ENDED(log written)` (GDS-04 §1.14); no entity represents state that survives
  across Sessions (custody decay over weeks, Δv burn over months, co-orbital loitering). A
  requirement for cross-session persistence or time-compression cannot be written today because no
  approved document commits to it. **Source:** GDS-03 §5 "Campaign / Session-Persistence Container";
  GDS-04 §3 "Campaign / Session-Persistence Container"; `strategic-review-2026-07.md` W7, §6.3 R15,
  FC-13; `FUTURE-WORK.md` §13.
- **CR-16 — Ground-Segment-as-Terrain Cyber Model.** Cyber effects resolve per-asset today
  (ADR-0012's exception); ground stations, networks, and the C2 chain are modeled only as access
  endpoints (GDS-04 §1.4), not as attackable/defendable objects whose compromise could falsify
  telemetry or deny uplink independent of any single asset's own state. A requirement to model the
  ground segment as contested terrain cannot be written today because no approved document commits
  to it. **Source:** GDS-03 §5 "Ground-Segment-as-Terrain Cyber Model"; `strategic-review-2026-07.md`
  §6.3 R17, FC-11, GAP-12; `FUTURE-WORK.md` §13.
- **CR-17 — Persistent Debris / STM Environment Layer.** The debris-cone estimate
  (`engine/engage.py`) is advisory only and `prop.collision_avoid` is unwired (`FUTURE-WORK.md` §2);
  no persistent environment object represents debris continuing to exist and gate future Access
  Windows after the Effect that created it resolves. A requirement for persistent, world-changing
  debris consequence cannot be written today because no approved document commits to it. **Source:**
  GDS-03 §5 "Persistent Debris / STM Environment Layer"; GDS-04 §3 "Persistent Debris / Environment
  Object"; `strategic-review-2026-07.md` §6.3 R16, FC-08, GAP-02; `FUTURE-WORK.md` §2, §13.
- **CR-18 — Facilitator / cross-session adjudication-consistency support.** GDS-01 §12's "Negative
  training" risk row (added by the strategic-review reconciliation) names "facilitator/adjudication
  drift across sessions with no consistency-support mechanism" as one of four unmitigated
  negative-training candidates and states plainly "no mitigation implemented in v1." A requirement
  for a consistency-support mechanism (checklist, rubric, cross-facilitator calibration aid) around
  manual adjudication (ADR-0017) cannot be written today because no approved document commits to
  building one — full treatment is explicitly deferred to DOM-005 (Validation Framework) once
  authored, per [`ADR-0031`](../architecture/adr/ADR-0031-governance-record-consistency.md). The
  risk row's other three named candidates are **not** duplicated here because each already has
  baseline coverage: AI-Red's ground-truth-read exploitability is CR-01/CNFR-06; Δv-as-terminal-life
  is FR-1310's own intentional, documented v1 scope (not a gap); the fixed five-D effect ontology is
  FR-1410's own intentional, documented v1 scope, tracked as assumption A2 in the
  [Strategic Assumptions Register](../architecture/strategic-assumptions-register.md). **Source:**
  GDS-01 §12 "Negative training" risk row; `strategic-review-2026-07.md` §4.5, §6.1 R6; ADR-0031.

---

## Strategic review reconciliation (strategic-review-2026-07.md)

In response to [`reviews/strategic-review-2026-07.md`](../reviews/strategic-review-2026-07.md) and
its disposition in [`reviews/architecture-update.md`](../reviews/architecture-update.md), this
document was reviewed against the changed architecture-tier inputs (new ADR-0030/ADR-0031, the
Strategic Assumptions Register, and the amended GDS-01/02/03/04/ICD sections). Full analysis in
[`reviews/requirements-update-report.md`](../reviews/requirements-update-report.md). Summary of what
changed here:

- **No numbered `FR-1xxx` baseline requirement was added, removed, or had its content modified.**
  Every architecture-tier change from the strategic review lands as a not-built, not-scheduled
  candidate component/concept (GDS-03 §5, GDS-04 §3) or a named-but-unmitigated risk (GDS-01 §12) —
  neither rises to a committed, testable system behavior, so none crosses this document's own bar
  for a numbered leaf (a candidate cannot be promoted to baseline within the same pass that names it).
- Added **CR-12 through CR-18**, seven new Candidate Requirements mirroring the six new GDS-03 §5 /
  GDS-04 §3 candidate components/concepts and the new GDS-01 §12 negative-training risk row, so the
  requirements-tier documentation does not silently omit what the architecture tier now names.
- Added `ADR-0030` to `FR-9110`'s Related ADRs (AI-Red is exactly the component ADR-0030's
  determinism doctrine generalizes from).
- Corrected the stale "build spec wins" language in the pre-existing-tag-scheme note above (it
  independently duplicated the same stale claim [`ADR-0031`](../architecture/adr/ADR-0031-governance-record-consistency.md)
  already fixed in `architecture/00-vision.md` §7) and the stale claim that no NFR baseline/matrix
  exists.
- Updated the Authoritative-inputs header's ADR range (`ADR-0029` → `ADR-0031`) and added the
  Strategic Assumptions Register as a cited input.

## DOM-002/004/005 backfill (2026-07)

In response to `docs/feature-planning/05-feature-review.md` Finding F-01 (three shipped Feature
Specifications — FS-201, FS-202, FS-301 — grounded in Domain documents DOM-002/004/005 with zero
corresponding requirement anywhere in this baseline), this document was reviewed against those
three domain documents and their FS-201/FS-301 output. Full analysis in
[`reviews/requirements-domain-backfill-report.md`](../reviews/requirements-domain-backfill-report.md).
Summary of what changed here:

- **No numbered `FR-1xxx` baseline requirement was added.** Every candidate capability DOM-002/004
  describe either directly conflicts with an Accepted ADR (ADR-0017 for DOM-002/FS-201's automated
  rubric computation; ADR-0029 for DOM-004/FS-301's dedicated research-export interface) or is not
  concrete enough to write a testable requirement against yet (DOM-004 §6's human-subjects
  boundary, which has no concrete feature to constrain today). This is a materially different
  outcome than the Feature Catalog's own prior estimate ("roughly 6–9 additional Features," per
  `docs/feature-planning/05-feature-review.md` Finding F-01's original Recommendation) — that
  estimate assumed a clean backfill and did not anticipate these two ADR conflicts, which only
  surfaced during this pass. See the backfill report for the full reasoning, including why DOM-005
  (Validation Framework) yields **zero** new leaves at all: it is validation-methodology guidance
  (how to check an instrument's validity), not a new system capability, and its one arguably
  system-level statement (Monte Carlo over seeds without relaxing determinism, §6) restates the
  already-baselined NFR-1500 determinism invariant rather than adding a new one.
- Added **CR-19 through CR-21**, three new Candidate Requirements — see the Candidate Requirements
  section above.

## ADR-0017/ADR-0029 conflict resolution — CR-19/CR-20 promotion (2026-07)

Following direct project-owner decision (per explicit instruction: amend `ADR-0017` with a narrow
carve-out for `CR-19`; supersede `ADR-0029` outright for `CR-20`), `ADR-0032` and `ADR-0033` were
authored resolving both blocking conflicts the "DOM-002/004/005 backfill" pass above found. This
is a same-baseline follow-up, not a new backfill pass — re-running this document's own Step 0
against the two new ADRs, per this skill's own "we added an ADR — update the requirements" worked
example. Summary of what changed here:

- **Added a new top-level category, `## FR-10000` — Assessment & Research Instrumentation**, with
  two new baselined leaves: **`FR-10110`** (automated non-aggregating competency rubric-tier
  computation, promoted from `CR-19` now that `ADR-0032` narrows `ADR-0017`'s prohibition) and
  **`FR-10210`** (multi-run/cohort structured research-data export, promoted from `CR-20` now that
  `ADR-0033` supersedes `ADR-0029`). Both leaves cite `Should` priority — neither is a precondition
  for any existing vignette's playability, the same reasoning `FR-9110` (AI-Red) already uses for
  a valuable-but-optional capability.
- **`CR-19` and `CR-20` are marked `PROMOTED` in place in the Candidate Requirements section**, not
  deleted — the audit trail of why each was originally blocked, and how, is preserved. `CR-21`
  remains an active Candidate, unaffected by either promotion (it addresses a human-subjects-
  research boundary that neither `FR-10110` nor `FR-10210` — both structured-aggregate, non-
  identifying capabilities — triggers).
- **No existing baselined FR was modified.** `FR-4710` (no automated score/win-loss) is unchanged
  and remains the boundary `FR-10110` must not cross, per `ADR-0032`'s own narrow-carve-out framing.
- This category's numbering (`FR-10000`, five digits) is a deliberate, explicit extension of the
  4-digit `FR-1000`–`FR-9110` scheme, not a renumbering of it — every leading digit 1–9 was already
  claimed by an existing top-level category before this pass. See `## FR-10000`'s own numbering
  note above.

## Next

This document's companion Non-Functional Requirements baseline
([`02-non-functional-requirements.md`](02-non-functional-requirements.md)) and Requirements
Traceability Matrix ([`03-requirements-traceability-matrix.md`](03-requirements-traceability-matrix.md))
already exist alongside it — see "Strategic review reconciliation" above for the most recent
amendment to all three. GDS-10 (Requirements Traceability Matrix) remains the eventual
architecture-tier authoring target this document's matrix does not substitute for
(`architecture/INDEX.md` §1).
