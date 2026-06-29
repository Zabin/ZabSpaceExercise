# GDS-05 — Functional Requirements

> **Document ID:** GDS-05
> **Version:** 1.0
> **Status:** ✅ Authored — merge gate closed (see "Merge gate" below)
> **Dependencies:** GDS-04
> **Referenced By:** GDS-06
> **Produces:** GDS-06
> **Feature Mapping:** N/A — program-level
> **Related Topics:** [`build-spec/02-requirements-and-operations.md`](../build-spec/02-requirements-and-operations.md)
> §5–6 (merge source — superseded by this document, see "Merge gate" below),
> [`requirements/01-functional-requirements.md`](../requirements/01-functional-requirements.md)
> (companion hierarchical elaboration with full traceability fields — see "Relationship to other
> requirement artifacts" below), [GDS-04](04-domain-model.md), [GDS-01](01-concept-of-operations.md)

[↑ Architecture index](INDEX.md) · [Docs index](../INDEX.md)

## Purpose

The authoritative specification of what SpaceSim must do, stated at capability grain (one
statement per discrete behavior) and organized by the same six capability groups the system has
used since the original build spec: simulation engine, bus & payload operations, command planning
& sensor tasking, White Cell control, scenario builder, and logging — plus the operations/hot-seat
model that governs how humans use those capabilities. This document is the result of closing
GDS-05's merge gate: build-spec/02 §5–6 content has been transferred here and build-spec/02 has
been updated to point back to this document as the live source.

## Relationship to other requirement artifacts

Three documents now describe functional requirements; each has a distinct, non-competing role:

| Document | Grain | Role |
|---|---|---|
| `build-spec/02-requirements-and-operations.md` §5–6 | Capability-tag (`FR-E1`, `OR-3`, …) | **Superseded.** Kept on disk, unchanged, only because source-code docstrings and `04-nfr-milestones-and-risks.md` §10 acceptance criteria cite these tags by ID; the section now carries a pointer to this document as the live text. New work cites GDS-05/`requirements/01`, not this file. |
| **GDS-05 (this document)** | Capability-tag, restated | **Authoritative for what must be true**, at the same grain as the original tags so existing citations keep resolving to a real statement. This is the level at which a stakeholder asks "does the system do X" and gets a yes/no-checkable answer. |
| `requirements/01-functional-requirements.md` | Hierarchical leaf (`FR-1111`) | **Authoritative for full traceability.** Each GDS-05 tag below decomposes into one or more `FR-1xxx` leaves there, each carrying the full field set (Preconditions, Postconditions, Acceptance Criteria, Verification Method, Dependencies, Related ADRs/Interfaces/Requirements) that this document does not repeat. Use `requirements/01` when you need a test plan or a precise acceptance condition; use GDS-05 when you need the capability-level statement and its place in the architecture. |

Where this document and `requirements/01` would ever disagree on substance (not just grain), that
is a defect to fix, not a feature — both trace to the same GDS-00–04/ICD/ADR baseline. No
disagreement was found while authoring this document (see "Merge gate" below).

---

## 1. Simulation engine (FR-E)

Traces to GDS-03 §"Simulation Engine" and GDS-04 §1.3 (Orbit), §1.6 (Access Window), §1.8
(Effect), §1.9 (Track); load-bearing invariants 1, 2, 5 in `CLAUDE.md`.

- **FR-E1** The engine shall maintain a single authoritative **simulation clock** in UTC and
  advance state as a pure function of sim time, current state, and the ordered action log.
  *(→ `requirements/01` FR-1110, FR-1130)*
- **FR-E2** The engine shall be **deterministic**: replaying the same initial state + action log +
  seed reproduces identical state at every tick. *(→ FR-1120; gated permanently by the Phase-1
  determinism property test per `CLAUDE.md` invariant 1)*
- **FR-E3** The engine shall propagate each satellite using a **Keplerian + J2** model (TLE via
  sgp4 for real satellites) and derive ground tracks, eclipse, and lighting (moderate fidelity),
  behind a `Propagator` interface. *(→ FR-1210; ADR-0009)*
- **FR-E4** The engine shall compute **access windows** for six channels — command uplink,
  telemetry downlink, sensor observation, jam footprint, weapon engagement, RPO proximity — via an
  `AccessProvider` interface. *(→ FR-1220; ADR-0011)*
- **FR-E5** The engine shall model **impulsive maneuvers** that edit orbital elements and decrement
  a per-asset **delta-v/fuel budget**; an asset with no fuel cannot maneuver. *(→ FR-1310)*
- **FR-E6** The engine shall resolve **effects** in the five counterspace categories to outcomes on
  the five-D's ladder, with reversibility, debris generation (kinetic), attribution signals, and
  resource consumption, via an `EffectResolver` interface. *(→ FR-1410; ADR-0012)*
- **FR-E7** The engine shall maintain **per-cell SDA belief** (`TrackCatalog`) distinct from
  **ground truth**, with custody confidence that **decays** over time and **resets** on
  observation, including a **weapons-quality track gate** for engagements. *(→ FR-1510, FR-1520;
  ADR-0013)*
- **FR-E8** The engine shall apply the **cyber exception**: cyber effects are not pass-gated but
  require a modeled access vector and depend on the target's cyber posture. *(→ FR-1420;
  ADR-0012)*

## 2. Bus & payload operations (FR-B)

Traces to GDS-04 §1.2 (Asset bus/payload state) and `research/06-bus-and-payload-operations.md`.

- **FR-B1** Each satellite shall have a live **bus state of health** (power+eclipse, attitude,
  thermal, propellant, storage, comms) evolving over time, each parameter checked against
  **soft/hard limits** producing green/yellow/red status. *(→ FR-2110)*
- **FR-B2** The payload shall be **gated by the bus** (no power → payload off; bad attitude →
  cannot point; full storage → cannot collect). *(→ FR-2210)*
- **FR-B3** Ground-visible **telemetry shall be pass-gated**: the displayed SOH snapshot updates
  only on contact; between contacts it is a timestamped last-known value; a **stored-telemetry
  dump** at the next contact can reveal out-of-contact events. *(→ FR-2310)*
- **FR-B4** Each payload type (SATCOM, ISR-EO, ISR-SAR, SIGINT, SDA, space-control, PNT, missile
  warning, weather) shall expose its **type-specific operator actions and monitors**. *(→ FR-2410)*
- **FR-B5** The engine shall support **safe mode** with the full attack/detection/recovery loop and
  its White-Cell dials. *(→ FR-2510; see `design/12-safe-mode-loop.md`)*

## 3. Command planning & sensor tasking (FR-P)

Traces to GDS-04 §1.7 (Planned Activity); ADR-0005 (plan-first commanding).

- **FR-P1** Operators shall **plan commands** that execute at the earliest valid window (or a
  chosen future window), via **ground uplink**, **ISL relay** (when geometry/peer permit), or
  **stored program**; commands are editable/cancellable until uplink. *(→ FR-3110, FR-3120)*
- **FR-P2** Operators shall **task SDA sensors** (search/track/characterize/cue) subject to sensor
  geometry and **single-task contention**, updating the `TrackCatalog` on report. *(→ FR-3210,
  FR-3220)*
- **FR-P3** Commands and collection tasks shall share one **PlannedActivity scheduler** so queue,
  timeline, undo, and time-travel behave identically. *(→ FR-3310)*
- **FR-P4** The engine shall **re-validate** every planned activity at execution time (ownership,
  window, resources, ROE, track gate) and fail gracefully with a reason if invalid. *(→ FR-3410)*
- **FR-P5** The order panel shall offer only the commands legal for the **seated role** (bus vs.
  payload) and asset, drawn from the asset's `command_db`. *(→ FR-3510)*
- **FR-P6** For any maneuver, the tool shall present a **delta-v cost preview** before commit — in
  m/s and in "years of service life spent" — and shall track remaining budget, estimated life
  remaining, and drift-when-empty; burns exceeding a configurable years-of-life threshold require a
  deliberate confirm. *(→ FR-1310; see `design/14-delta-v-economy.md`)*

Plan-first composition assistants (maneuver, observe, jam, engage, cyber, sigint) compute a
read-only consequence preview through a non-mutating `/compute` endpoint before an order is
queued; this is the mechanism by which FR-P1/FR-P6 are made checkable in the UI without committing
state, and is itself covered by FR-3110's Acceptance Criteria in `requirements/01`.

## 4. White Cell control (FR-W)

Traces to GDS-01 §5–8 (White Cell workflow, lifecycle, operational modes); ADR-0016 (single point
of time control), ADR-0017 (manual adjudication).

- **FR-W1** White Cell shall **select and tune** a vignette; every tunable parameter renders as a
  typed control with its `affects` tooltip; defaults make a vignette runnable untouched. *(→
  FR-4110)*
- **FR-W2** White Cell shall **assign operator roles** via checkboxes at setup (which seat owns
  which assets, and bus vs. payload split), informed by the vignette's `roles_needed`. *(→
  FR-4210)*
- **FR-W3** White Cell shall control **wall-clock time**: run at a selectable multiplier, **pause**,
  **fast-forward**, and **rewind** (rewind via deterministic replay). *(→ FR-4310; ADR-0016)*
- **FR-W4** White Cell shall fire **injects** (scripted or manual), immediately or scheduled for a
  future sim time, from a reusable inject library; future-dated injects replay byte-identical on
  save/resume. *(→ FR-4410)*
- **FR-W5** White Cell shall set the **classification banner**, shown on every screen and exported
  file. *(→ FR-4510)*
- **FR-W6** White Cell shall have a **god-view** (ground truth + both cells' belief) and the
  ability to view **as Red** or **as Blue** for adjudication. *(→ FR-4610)*
- **FR-W7** White Cell shall be able to set the **safe-mode dials** and other live parameters
  mid-exercise. *(→ FR-4710 scope; manual-adjudication boundary per ADR-0017)*

## 5. Scenario builder (FR-S)

Traces to GDS-01 §9 (external systems); ADR-0018 (offline-first), ADR-0027 (scenario-authoring
boundary).

- **FR-S1** White Cell shall create/edit a vignette in-app and **save it as a JSON file**
  containing mission, `roles_needed`, starting TLEs, start epoch, parameters, and injects. *(→
  FR-5110)*
- **FR-S2** The builder shall **import TLEs from Space-Track** at build time when reachable, and
  otherwise accept **manual TLE entry/paste**; after creation, no network access is needed. *(→
  FR-5210; ADR-0018)*
- **FR-S3** The builder shall **validate** a scenario (well-formed TLEs, all `roles_needed`
  satisfiable, referenced templates exist) and report errors precisely. *(→ FR-5310)*

## 6. Logging (FR-L)

Traces to GDS-04 §1.14 (Session/event log); ADR-0002 (deterministic core).

- **FR-L1** The engine shall append every state-changing event (orders, executions, effects,
  injects, white-controls, time-controls) to an **ordered, timestamped action log**. *(→ FR-7110)*
- **FR-L2** The action log shall be **sufficient to deterministically reconstruct** the exercise
  (the foundation for replay/AAR/branch-to-live), and shall be written to disk at exercise end. *(→
  FR-7110, FR-7320)*

---

## 7. Operations & hot-seat model (OR)

The single most distinctive operational requirement: many notional roles, shared terminals,
hot-seat swapping, genuine wall clock. Traces to GDS-01 §4 (operational environment), §10
(operational constraints); ADR-0015 (LAN trust model), ADR-0026 (RLock LAN scaling ceiling).

- **OR-1 Role-scoped access.** When an operator sits, they select their **assigned seat/role**
  (selected by White Cell at setup) and see/act on **only their assigned assets**. Fog-of-war and
  ownership are enforced per role, not merely per side. *(→ FR-6210; ADR-0004)*
- **OR-2 Bus/payload seats.** A role may be **bus operator**, **payload operator**, or **both** for
  a given asset/constellation, per White Cell assignment. *(→ FR-3510 scope)*
- **OR-3 Soft handoff with screen blank.** The active user can invoke a **"blank screen / hand
  off" menu** that hides all sensitive content while White Cell selects the next user and the
  keyboard is physically passed. No hard login wall in v1; the blank is the privacy boundary. *(→
  GDS-01 §4 "trust model"; no dedicated FR-1xxx leaf — see Open Questions)*
- **OR-4 Wall clock continues.** Time runs in real wall-clock by default during play; operators
  negotiate hot-seat time with White Cell, who may **pause** for a timeout or to manage handoffs.
  *(→ FR-4310)*
- **OR-5 Observer view.** Observers get a read-only view set by White Cell (god-view or a specific
  cell), with no command ability. *(→ FR-6510)*
- **OR-6 One exercise at a time.** v1 runs a single exercise per process instance, in one sitting.
  *(→ FR-6410 scope)*
- **OR-7 Unseated-role behavior.** Because only one operator is seated at a time while the wall
  clock keeps running, every role's assets must have defined behavior while *unseated*: assets
  continue executing their already-queued `PlannedActivity`s (commands fire at their scheduled
  windows; stored programs and recovery chains proceed) but **no new decisions are made on their
  behalf.** This is why plan-first matters. White Cell may pause to prevent a role from being
  disadvantaged by time passing while unseated (OR-4). *(→ FR-3110's plan-first guarantee; ADR-0005)*
- **OR-8 "AI-Red"/"AI-Blue" is NOT an autonomous AI in v1.** Where vignette parameters mention
  "AI-Red aggressiveness," v1 means **White-Cell-driven scripted behavior**: the parameter scales
  the pre-scripted injects/plans the facilitator runs for an unseated or facilitator-played cell.
  A genuine autonomous opponent is a documented v2 seam (`docs/FUTURE-WORK.md` §1), not a v1
  deliverable. *(→ FR-9110; ADR-0021, ADR-0024)*

---

## Open Questions

- **OQ1 — OR-3's "blank screen" mechanism has no FR-1xxx leaf.** `requirements/01` does not carry a
  dedicated requirement for the hot-seat screen-blank menu; it is implied by GDS-01 §4's trust model
  discussion but was not derived as a standalone leaf. Either add an `FR-6xxx` leaf for it in a
  future revision of `requirements/01`, or record here that it is intentionally treated as a UI
  affordance rather than a session-layer behavior. Left open rather than resolved unilaterally.
- **OQ2 — OR-6 (single exercise per process) vs. multi-session discovery.** `build-spec/02` §6
  states "v1 runs a single exercise per process instance," but the shipped `/api/sessions`
  discovery endpoint (P8, LAN multiplayer) suggests multiple `Session` objects can coexist in one
  process. This document restates OR-6 as written in the merge source rather than resolving the
  apparent tension; flagged for the build-spec/02 owner to confirm whether OR-6's wording is stale
  post-P8.

## Merge gate (closed)

- [x] **Absorbed build-spec/02 §5–6 in full.** Every `FR-E*`, `FR-B*`, `FR-P*`, `FR-W*`, `FR-S*`,
  `FR-L*`, and `OR-*` tag is restated above verbatim in substance (wording tightened only where the
  source was duplicative), each cross-referenced to its `requirements/01` FR-1xxx leaf(ves) where
  one exists.
- [x] **Checked for conflict with `requirements/01-functional-requirements.md`.** None found — every
  GDS-05 tag above maps cleanly onto one or more existing FR-1xxx leaves; two source items (OR-3,
  parts of OR-6) had no corresponding leaf and are recorded as Open Questions above rather than
  papered over.
- [x] **Checked for conflict with GDS-01 through GDS-04.** None found; every tag above traces to a
  cited GDS section or ADR.
- [x] **Decision recorded:** per this turn's explicit project-owner instruction ("build spec
  document and other older documentation is being replaced by this new hierarchy"), this document
  — not `build-spec/02-requirements-and-operations.md` §5–6 — is now **the authoritative
  statement** of these requirements. `build-spec/02-requirements-and-operations.md` §5–6 has been
  updated with a pointer to this document (see that file) and is retained on disk, unmodified in
  substance, solely so that existing tag citations (source-code docstrings, `04-nfr-milestones-
  and-risks.md` §10 acceptance criteria) keep resolving to readable text. This is a deliberate
  departure from the GDS-00–04 merge-gate pattern (where the source document stayed authoritative
  and the GDS document was a layered extraction) — see `CLAUDE.md`'s updated "Authoritative source
  & reading order" section for the corresponding update to the project-wide reading order rule.

## Next

`GDS-06` (Non-functional Requirements) may now begin.
