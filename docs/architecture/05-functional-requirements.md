# GDS-05 — Functional Requirements

> **Document ID:** GDS-05
> **Version:** 1.2 *(2026-10-23, run #217: FR-W3 + `FR-4320`, FR-L3 + `FR-7230`)*; 1.1 *(2026-10-17: §8 added, `BL-0056`)*
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
disagreement was found while authoring this document (see "Merge gate" below). Leaves added to
`requirements/01` after the merge are tagged in §8 (added 2026-10-17); a future leaf that has no tag
here is a gap to close in the same `03`/`04` pass, not a second baseline.

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
  **fast-forward**, and **rewind** (rewind via deterministic replay). Clock control and the White
  Cell's other lifecycle and facilitation controls are refused, on the server, to any other seat.
  *(→ FR-4310, FR-4320; ADR-0016; FR-4320 added 2026-10-23, owner decision `BL-0307`)*
- **FR-W4** White Cell shall fire **injects** (scripted or manual), immediately or scheduled for a
  future sim time, from a reusable inject library; future-dated injects replay byte-identical on
  save/resume. *(→ FR-4410)*
- **FR-W5** White Cell shall set the **classification banner**, shown on every screen and exported
  file. *(→ FR-4510)*
- **FR-W6** White Cell shall have a **god-view** (ground truth + both cells' belief) and the
  ability to view **as Red** or **as Blue** for adjudication. *(→ FR-4610)*
- **FR-W7** White Cell shall be able to set the **safe-mode dials** and other live parameters
  mid-exercise. *(→ FR-4710 scope, FR-4720; manual-adjudication boundary per ADR-0017)*

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
  satisfiable, every reference from one element of the vignette to another resolves; assets, sensors and effects are authored inline, with no template reference — `BL-0233`) and report errors precisely. *(→ FR-5310, FR-5311–FR-5314)*

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
  GDS-01 §4 "trust model"; FR-6610, the leaf added since — see Open Questions OQ1)*
- **OR-4 Wall clock continues.** Time runs in real wall-clock by default during play; operators
  negotiate hot-seat time with White Cell, who may **pause** for a timeout or to manage handoffs.
  *(→ FR-4310)*
- **OR-5 Observer view.** Observers get a read-only view set by White Cell (god-view or a specific
  cell), with no command ability. *(→ FR-6510)*
- **OR-6 One session per exercise.** Each exercise is one `Session`, run in one sitting and shared by
  every seat (hot-seat or LAN). One server process may host several sessions at once (`/api/sessions`
  discovery), up to a fixed cap, and a session can be saved and resumed in a new process; how well
  this must hold is GDS-06 NFR-14. *(→ FR-6410 scope; reworded 2026-10-22, `BL-0300` — see OQ2)*
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

## 8. Capability statements added after the merge (2026-07 → 2026-10)

*Added 2026-10-17 (pipeline run #161, `BL-0056`).* Between this document's merge and this pass,
`requirements/01` gained 65 leaves with no capability tag here: owner-requested intake batches
(the 2026-09-26/27 external validation report, items B1–B17), the Vignette Creator design
(`ADS-5100A`/`ADS-5100B`), the training-corpus elevation, the assessment/research ADRs
(`ADR-0032`/`ADR-0033`), the load-validation and effect-resource-bounds batches (`ADR-0037`), and a
handful of session-layer leaves the merge never tagged. Each tag below restates its leaves at
capability grain. **No capability is introduced here:** every tag traces to its leaves' own Source
Documents, which name the owner request, ADS or ADR. Tags continue each family's numbering; two
new families cover assessment (`FR-A`) and the training corpus (`FR-T`).

### 8.1 Simulation engine and effects (FR-E, continued)

- **FR-E9** Space weather shall scale LEO drag and the anomaly rate through a space-weather index.
  *(→ FR-1230, FR-4440)*
- **FR-E10** Each manoeuvre shall be recorded in a per-asset ledger with a purpose tag, and the
  ledger shall be exportable. *(→ FR-1320)*
- **FR-E11** A kinetic kill shall carry a debris-field persistence estimate by altitude.
  *(→ FR-1430)*
- **FR-E12** Jamming an uplink or crosslink shall degrade the command and relay delivery paths it
  covers, and each effect class's detectability and attribution difficulty shall be configurable.
  *(→ FR-1440, FR-1450)*
- **FR-E13** Effects shall respect resource bounds: a salvo never exceeds the remaining rounds, and
  jamming does not consume the jammer's power rating. *(→ FR-1460, FR-1470; ADR-0037)*
- **FR-E14** Sensors shall be modelled by modality: radar fence/dish beam modes, optical solar/lunar
  exclusion, a space-based minimum range and altitude-band affinity, cue-dependent tasking,
  passive-RF multilateration, hosted sensors following their host's orbit, and phase-angle (CATS)
  refinement of passive-EO access windows. *(→ FR-1610–FR-1670)*

### 8.2 Bus and payload operations (FR-B, continued)

- **FR-B6** Payload and bus parameters shall be typed per payload type and per bus subsystem
  (power, propulsion). *(→ FR-5170, FR-5180; ADS-5100B)*
- **FR-B7** A cell shall export one asset's telemetry over a time span as CSV, fog-scoped like the
  live telemetry view. *(→ FR-2320)*

### 8.3 Command planning and authorization (FR-P, continued)

- **FR-P7** Rules of engagement shall be held per cell, may optionally gate each effect type behind
  a controller-role authorization, and may be changed live, with every change logged.
  *(→ FR-3420, FR-3430, FR-3440)*
- **FR-P8** A role assignment shall be scoped bus-only, payload-only or both. *(→ FR-3520; refines
  OR-2/FR-W2)*

### 8.4 White Cell control (FR-W, continued)

- **FR-W8** White Cell shall author injects that fire when a deterministic engine-evaluated
  condition becomes true, use the anomaly/sensor-outage/custody-loss/scripted-manoeuvre effect
  types, and edit or cancel a scheduled inject before it fires. *(→ FR-4420, FR-4430, FR-4450)*
- **FR-W9** White Cell shall see each cell's picture beside truth in a side-by-side controller
  view. *(→ FR-4620)*

### 8.5 Scenario builder (FR-S, continued)

- **FR-S4** The Vignette Creator shall offer a synchronized JSON view, a 2D/3D initial-state
  preview, TLE and lat/long asset entry, an asset menu (edit/reassign/delete) and a
  seat-count/seat-role matrix. *(→ FR-5120–FR-5160; ADS-5100A)*
- **FR-S5** The builder shall import many objects at once from a TLE or CCSDS OMM file.
  *(→ FR-5220)*
- **FR-S6** Vignettes shall load from configured external directories as well as the built-in
  library, and saving shall write only to a configured user directory, never by path traversal.
  *(→ FR-5410, FR-5420)*
- **FR-S7** White Cell shall save a running session's current state as a new starting vignette.
  *(→ FR-5510)*

### 8.6 Logging, save and export (FR-L, continued)

- **FR-L3** A session shall save and resume deterministically, with save-file content ownership
  split from session ownership, and resume from the save's own contents whatever has since happened
  to the vignette file. *(→ FR-7210, FR-7220, FR-7230 — FR-7230 added 2026-10-23, owner decision
  `BL-0302`)*
- **FR-L4** Replay shall be read-only against the live session and may run at variable speed from
  truth or one cell's viewpoint. *(→ FR-7310, FR-7330)*
- **FR-L5** State vectors shall export over a time span — truth through White Cell, a cell's own
  observed picture through that cell — in ECI and RIC, as CSV and CCSDS OEM with a companion RIC
  file, and a quick TLE export shall exist for a cell-visible satellite. *(→ FR-7410–FR-7440)*

### 8.7 Session and presentation (OR, continued)

- **OR-9 Session seam.** All non-engine access shall go through the `SessionAPI`; the clock is
  server-authoritative and shared across connections; mutations lock per session; and exactly a
  documented, named set of no-cell endpoints may expose ground truth. *(→ FR-6110, FR-6310,
  FR-6320, FR-6220; ADR-0014, ADR-0015, ADR-0026 — session-layer leaves the merge did not tag)*
- **OR-10 Presentation.** The console is a browser/web layer, with a live, operator-selectable
  RIC-frame relative-motion view and a CATS phase-angle overlay for its chase satellite.
  *(→ FR-8110, FR-8210, FR-8220)*

### 8.8 Assessment and research (FR-A, new family)

- **FR-A1** Competency rubric tiers shall be computed automatically per dimension, never
  aggregated into a composite score. *(→ FR-10110; ADR-0032)*
- **FR-A2** Multi-run and cohort research data shall export as structured files. *(→ FR-10210;
  ADR-0033)*

### 8.9 Training corpus (FR-T, new family)

- **FR-T1** The training corpus shall give every seat role-scoped manual coverage, anchor each
  section to its sources, and keep a bidirectional feature ⇄ manual index.
  *(→ FR-11110, FR-11120, FR-11210)*
- **FR-T2** A sequenced learning path shall order the vignette library, each rung linked to its
  manual prerequisites. *(→ FR-11310, FR-11320)*
- **FR-T3** A training-artifact update shall ride the package that changes the behaviour, and the
  vignette playbooks shall be machine-verified. *(→ FR-11410, FR-11420)*

---

## Open Questions

- **OQ1 — OR-3's "blank screen" mechanism has no FR-1xxx leaf.** `requirements/01` does not carry a
  dedicated requirement for the hot-seat screen-blank menu; it is implied by GDS-01 §4's trust model
  discussion but was not derived as a standalone leaf. Either add an `FR-6xxx` leaf for it in a
  future revision of `requirements/01`, or record here that it is intentionally treated as a UI
  affordance rather than a session-layer behavior. Left open rather than resolved unilaterally.
  **Resolved (2026-10-17, `BL-0056`):** `requirements/01` now carries `FR-6610` ("Screen-blank
  pending-handoff menu between hot-seat role changes"); OR-3 maps to it.
- **OQ2 — OR-6 (single exercise per process) vs. multi-session discovery.** `build-spec/02` §6
  states "v1 runs a single exercise per process instance," but the shipped `/api/sessions`
  discovery endpoint (P8, LAN multiplayer) suggests multiple `Session` objects can coexist in one
  process. This document restates OR-6 as written in the merge source rather than resolving the
  apparent tension; flagged for the build-spec/02 owner to confirm whether OR-6's wording is stale
  post-P8.
  **Resolved (2026-10-22, `BL-0300`):** the wording was stale. OR-6 now states the as-built model —
  one `Session` per exercise, several sessions per process up to a cap, save and resume into a new
  process — and its quality attribute is [GDS-06](06-non-functional-requirements.md) NFR-14.

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
