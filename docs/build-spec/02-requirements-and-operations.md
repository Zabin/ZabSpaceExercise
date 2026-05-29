[← Build Spec index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 5. Functional requirements

Grouped by capability. Each is testable; acceptance criteria in §10 map back to these tags.

### 5.1 Simulation engine (FR-E)
- **FR-E1** The engine shall maintain a single authoritative **simulation clock** in UTC and
  advance state as a pure function of sim time, current state, and the ordered action log.
- **FR-E2** The engine shall be **deterministic**: replaying the same initial state + action log
  + seed reproduces identical state at every tick.
- **FR-E3** The engine shall propagate each satellite using a **Keplerian + J2** model and derive
  ground tracks, eclipse, and lighting (moderate fidelity), behind a `Propagator` interface.
- **FR-E4** The engine shall compute **access windows** for six channels (command uplink,
  telemetry downlink, sensor observation, jam footprint, weapon engagement, RPO proximity) via
  an `AccessProvider` interface.
- **FR-E5** The engine shall model **impulsive maneuvers** that edit orbital elements and decrement
  a per-asset **delta-v/fuel budget**; an asset with no fuel cannot maneuver.
- **FR-E6** The engine shall resolve **effects** in the five counterspace categories to outcomes
  on the five-D's ladder, with reversibility, debris generation (kinetic), attribution signals,
  and resource consumption, via an `EffectResolver` interface.
- **FR-E7** The engine shall maintain **per-cell SDA belief** (`TrackCatalog`) distinct from
  **ground truth**, with custody confidence that **decays** over time and **resets** on
  observation, including a **weapons-quality track gate** for engagements.
- **FR-E8** The engine shall apply the **cyber exception**: cyber effects are not pass-gated but
  require a modeled access vector and depend on the target's cyber posture.

### 5.2 Bus & payload operations (FR-B)
- **FR-B1** Each satellite shall have a live **bus state of health** (power+eclipse, attitude,
  thermal, propellant, storage, comms) evolving over time, each parameter checked against
  **soft/hard limits** producing green/yellow/red status.
- **FR-B2** The payload shall be **gated by the bus** (no power → payload off; bad attitude →
  cannot point; full storage → cannot collect).
- **FR-B3** Ground-visible **telemetry shall be pass-gated**: the displayed SOH snapshot updates
  only on contact; between contacts it is a timestamped last-known value; a **stored-telemetry
  dump** at the next contact can reveal out-of-contact events.
- **FR-B4** Each payload type (SATCOM, ISR-EO, ISR-SAR, SIGINT, SDA, space-control, PNT, missile
  warning, weather) shall expose its **type-specific operator actions and monitors** per
  `06-bus-and-payload-operations.md` §2.
- **FR-B5** The engine shall support **safe mode** with the full attack/detection/recovery loop
  and its White-Cell dials per `12-safe-mode-loop.md`.

### 5.3 Command planning & sensor tasking (FR-P)
- **FR-P1** Operators shall **plan commands** that execute at the earliest valid window (or a
  chosen future window), via **ground uplink**, **ISL relay** (when geometry/peer permit), or
  **stored program**; commands are editable/cancellable until uplink.
- **FR-P2** Operators shall **task SDA sensors** (search/track/characterize/cue) subject to
  sensor geometry and **single-task contention**, updating the `TrackCatalog` on report.
- **FR-P3** Commands and collection tasks shall share one **PlannedActivity scheduler**
  (`04-data-model.md` §6.5) so queue, timeline, undo, and time-travel behave identically.
- **FR-P4** The engine shall **re-validate** every planned activity at execution time
  (ownership, window, resources, ROE, track gate) and fail gracefully with a reason if invalid.
- **FR-P5** The order panel shall offer only the commands legal for the **seated role** (bus vs.
  payload) and asset, drawn from the asset's `command_db`, per the catalog in
  `13-operator-command-catalog.md`.
- **FR-P6** For any maneuver, the tool shall present a **delta-v cost preview** before commit —
  in m/s **and** in "years of service life spent" against the asset's annual upkeep rate — and
  shall track remaining budget, estimated life remaining, and drift-when-empty, per
  `14-delta-v-economy.md`. Burns exceeding a configurable years-of-life threshold require a
  deliberate confirm.

### 5.4 White Cell control (FR-W)
- **FR-W1** White Cell shall **select and tune** a vignette; every tunable parameter renders as a
  typed control with its `affects` tooltip; defaults make a vignette runnable untouched.
- **FR-W2** White Cell shall **assign operator roles** via checkboxes at setup (which seat owns
  which assets, and bus vs. payload split), informed by the vignette's `roles_needed`.
- **FR-W3** White Cell shall control **wall-clock time**: run at a selectable multiplier,
  **pause**, **fast-forward**, and **rewind** (rewind via deterministic replay).
- **FR-W4** White Cell shall fire **injects** (scripted or manual) of the supported effect types.
- **FR-W5** White Cell shall set the **classification banner** (UNCLASSIFIED//EXERCISE or
  UNCLASSIFIED//TRAINING), shown on every screen and exported file.
- **FR-W6** White Cell shall have a **god-view** (ground truth + both cells' belief) and the
  ability to view **as Red** or **as Blue** for adjudication.
- **FR-W7** White Cell shall be able to set the **safe-mode dials** and other live parameters
  mid-exercise.

### 5.5 Scenario builder (FR-S)
- **FR-S1** White Cell shall create/edit a vignette in-app and **save it as a JSON file**
  containing mission, `roles_needed`, starting **TLEs**, **start epoch**, parameters, and injects.
- **FR-S2** The builder shall **import TLEs from Space-Track** at build time when reachable, and
  otherwise accept **manual TLE entry/paste**; after creation, no network access is needed.
- **FR-S3** The builder shall **validate** a scenario (well-formed TLEs, all `roles_needed`
  satisfiable, referenced templates exist) and report errors precisely.

### 5.6 Logging (FR-L)
- **FR-L1** The engine shall append every state-changing event (orders, executions, effects,
  injects, white-controls, time-controls) to an **ordered, timestamped action log**.
- **FR-L2** The action log shall be **sufficient to deterministically reconstruct** the exercise
  (the foundation for v2 replay/AAR/CSV and branch-to-live), and shall be written to disk at
  exercise end.

---

## 6. Operations & hot-seat model (OR)

The single most distinctive operational requirement: **16 notional roles, one terminal, hot-seat
swapping, genuine wall clock.**

- **OR-1 Role-scoped access.** When an operator sits, they authenticate to their **assigned
  seat/role** (selected by White Cell at setup) and see/act on **only their assigned assets**.
  Fog-of-war and ownership are enforced per role, not merely per side.
- **OR-2 Bus/payload seats.** A role may be **bus operator**, **payload operator**, or **both**
  for a given asset/constellation, per White Cell assignment. Two people can jointly operate one
  satellite (one bus, one payload) in larger exercises; one person does both in small ones.
- **OR-3 Soft handoff with screen blank.** The active user can invoke a **"blank screen / hand
  off" menu** that hides all sensitive content while White Cell selects the next user and the
  keyboard is physically passed. No hard login wall in v1; the blank is the privacy boundary.
- **OR-4 Wall clock continues.** Time runs in real wall-clock by default during play; operators
  **negotiate hot-seat time with White Cell**, who may **pause** for a timeout or to manage
  handoffs. (v2/future: per-terminal concurrent time when networked.)
- **OR-5 Observer view.** Observers get a read-only view set by White Cell (god-view or a
  specific cell), with no command ability.
- **OR-6 One exercise at a time.** v1 runs a single exercise per process instance, in one sitting.
- **OR-7 Unseated-role behavior (critical for hot-seat).** Because only one operator is seated at
  a time while the **wall clock keeps running**, every role's assets must have defined behavior
  while *unseated*. v1 rule: **assets continue executing their already-queued PlannedActivities**
  (commands fire at their scheduled windows; stored programs and recovery chains proceed) but
  **no new decisions are made on their behalf.** They are neither frozen nor autonomously
  clever — they simply carry out the plan the operator left. This is why **plan-first** matters:
  an operator's queued plan is what "runs" while they're out of the seat. White Cell may **pause**
  to prevent a role from being disadvantaged by time passing while unseated (OR-4).
- **OR-8 "AI-Red"/"AI-Blue" is NOT an autonomous AI in v1.** Where vignette parameters mention
  "AI-Red aggressiveness," this v1 means **White-Cell-driven scripted behavior**: the parameter
  scales the *pre-scripted* injects/plans the facilitator runs for an unseated or
  facilitator-played cell (e.g., how many jammers activate, whether kinetic is authorized). A
  genuine autonomous opponent is a documented **v2 seam** (`docs/FUTURE-WORK.md` §1), not a
  v1 deliverable. Vignette text and the parameter tooltips shall be worded accordingly.

---

---
