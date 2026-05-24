# Build Specification / Project Start Document (PSD)
## Space Control & Orbital Warfare Exercise Simulator — Version 1

**Document type:** Software Project Start / Requirements & Build Specification
**Audience:** Claude Code (implementer & maintainer), White Cell facilitators, future maintainers
**Status:** Baseline for v1 implementation
**Classification of this document:** UNCLASSIFIED // TRAINING
**Companion documents:** all files in `01-research/`, `02-vignettes/`, and `03-software-design/`.
This PSD is the authoritative entry point; where it references a companion file, that file holds
the detailed design.

---

## 0. How to read this document

This is the project-start specification for a single-machine, hot-seat professional military
education (PME) wargaming tool for space control and orbital warfare. It is written to the depth
a real project kickoff requires: scope, stakeholders, decisions, functional and non-functional
requirements, architecture, data formats, milestones, acceptance criteria, risks, and a
glossary. Reading order for a new implementer:

1. This PSD §1–§6 (context, scope, decisions, requirements).
2. `01-architecture-overview.md` and `04-data-model.md` (the contract).
3. The research files in `01-research/` (why the rules are what they are).
4. This PSD §7–§12 (architecture detail, milestones, acceptance, risk).
5. The vignettes and remaining design files as needed during each phase.

Requirements are tagged for traceability: **FR-x** (functional), **NFR-x** (non-functional),
**DR-x** (data), **UR-x** (UI/UX), **OR-x** (operations/hot-seat). Acceptance criteria in §10
reference these tags.

---

## 1. Project context & purpose

### 1.1 Problem statement
CAF and allied space operators need a hands-on environment to practice **space control and
orbital warfare** under realistic constraints — where you cannot command, observe, or attack a
satellite on demand, but only when orbital geometry and ground access permit, and where most
real effects are reversible electronic, cyber, and proximity actions rather than kinetic
strikes. Existing commercial tools (e.g., STK) model orbits superbly but are not counterspace
wargaming environments, are paid, and are not structured around Red/Blue/White exercise play.

### 1.2 Purpose of this tool
A facilitator-run (White Cell) exercise simulator in which Red and Blue cells operate fleets of
space and ground assets — as **bus and payload operators** — within authentic limitations:
pass-gated command and telemetry, scarce SDA sensors, finite fuel, and doctrinally grounded
counterspace effects. The tool teaches the *texture* of real space operations (monitor state of
health, plan a pass, task a sensor, weigh reversible vs. escalatory effects) alongside the
operational art of contesting the domain.

### 1.3 Primary training objectives
- Internalize that space operations are **scheduling against orbital geometry**.
- Practice operating a **satellite bus and payload** (state-of-health monitoring, pass planning,
  payload tasking) for multiple mission types.
- Exercise the **SDA loop**: task scarce sensors, build and lose custody, characterize threats.
- Weigh **counterspace effects** across the escalation ladder (deceive→disrupt→deny→degrade→
  destroy) with attention to reversibility, attribution, and debris.
- Rehearse **active and passive defense** and recovery (including from safe mode).

### 1.4 What this tool is NOT
- Not a high-fidelity astrodynamics or RF mission-planning tool (v1 is "moderate fidelity,"
  upgradeable — see `04-orbital-mechanics-primer.md`).
- Not a classified system or intelligence product; all content is unclassified training
  material with fictional default assets.
- Not a networked multiplayer system in v1 (single machine, hot-seat).
- Not a real satellite control system; it simulates the *experience*, not real spacecraft.

---

## 2. Stakeholders & users

| Stakeholder | Role | Needs from the tool |
|---|---|---|
| **White Cell** (facilitator, 2 seats) | Builds/selects scenarios, assigns roles, controls time, injects events, adjudicates, runs AAR | Scenario builder, role assignment, time control incl. pause, inject panel, god-view, classification control |
| **Blue Cell** (friendly, up to 6 operators) | Operate assigned Blue assets as bus and/or payload operators | Per-role asset access, SOH monitoring, pass planning, payload tasking, SDA |
| **Red Cell** (adversary, up to 6 operators) | Operate assigned Red assets; execute doctrine-flavored counterspace | Same operator capabilities as Blue, plus offensive effects |
| **Observers** (up to 2) | Watch the exercise for assessment/learning | Read-only view (god-view or a designated cell view, White-Cell-set) |
| **Maintainer** (Claude Code) | Build and evolve the tool | Clean architecture, tests, data-driven content, documented seams |

**Concurrency model (v1):** all 16 notional participants share **one terminal** via **hot-seat
swapping**. Only one person is "at the keyboard" at a time; White Cell coordinates who is up and
the outgoing user blanks the screen during handoff (see §6).

---

## 3. Scope

### 3.1 In scope for v1
- Single-machine desktop application, **offline-capable**, hot-seat multi-role play.
- Moderate-fidelity orbital model: Keplerian + J2, pass/access-window computation, impulsive
  maneuvers, eclipse/lighting (`04-orbital-mechanics-primer.md`).
- **2D visualization in ECI and RIC frames** (3D globe deferred to v1.1).
- Up to **~24 satellites total** across cells in the largest v1 scenario (deliberately under the
  48 ceiling), with **constellations of at most 3 satellites**, each operated and monitored
  **individually**.
- Bus + payload operations model with **state of health**, alarms, **safe mode** and its
  detection/recovery loop (`06-bus-and-payload-operations.md`, `12-safe-mode-loop.md`).
- The five counterspace effect categories and the SDA tasking loop
  (`03-counterspace-taxonomy.md`, `11-command-planning-and-tasking.md`).
- **Plan-first command model**: ground uplink at next pass, rare ISL relay, stored programs.
- **White Cell controls**: scenario selection & tuning, role assignment via checkboxes, genuine
  **wall-clock** time with pause and fast-forward/rewind, injects, classification banner.
- **In-app scenario builder** writing one **JSON file per vignette** (mission, roles needed,
  starting TLEs, start epoch, parameters, injects), with optional **Space-Track TLE import at
  build time** and manual TLE entry fallback.
- **Action logging** of all events (the data substrate for v2 replay/AAR), even though the
  replay UI itself is v2.
- The eight specified vignettes (`02-vignettes/`) plus the ability to author more.

### 3.2 Deferred (explicit non-goals for v1)
| Deferred item | Target | Why deferred |
|---|---|---|
| Networked / LAN multiplayer, dedicated server | v2+ | User wants single-machine hot-seat first |
| **3D globe viewer** | v1.1 | 2D ECI+RIC sufficient to start; 3D is high-effort |
| **Replay UI & automated AAR / CSV export** | v2 | Log now, build the viewer later; design the seam |
| **Replay→live "branch to live play"** (also the save story) | v2 | Depends on replay infrastructure |
| **Save / resume mid-exercise** | v2 | v1 runs in a single sitting |
| **Automated scoring** | v2 | White Cell adjudicates manually in v1 |
| **Constellation aggregation** (manage many sats as one) | v2 | v1 capped at 3-sat constellations, individual control |
| **High-fidelity propagation / RF link budgets** | later | Behind interfaces; moderate fidelity first |

### 3.3 Assumptions made for round-4 questions (White Cell may override in scenario data)
- **RIC reference (UR):** the RIC view is centered on the **operator-selected satellite**, with a
  one-click option to set the origin to *another* tracked object for **relative/RPO geometry**
  (the primary RIC use case). Default origin = the seat's first assigned asset.
- **In-app help (UR):** v1 provides **tooltips and a "why can't I?" affordance** on every
  disabled control, plus a one-screen role cheat-sheet; **no full interactive tutorial** in v1
  (White Cell briefs operators).
- **Error handling (NFR):** invalid scenario JSON **fails loudly at load** with a precise White
  Cell error (which field, which asset). In-play illegal actions are **blocked with explanation**.
  *Physically legal but tactically unwise* actions (e.g., a wasteful burn) are **allowed to run
  and produce their natural bad outcome** — that is a teaching feature, not an error.
- **Hardware floor (NFR):** must run acceptably on a **typical government laptop with integrated
  graphics** (no discrete GPU assumed); this steers the 2D-first rendering choice.
- **Theme (UR):** dark "ops-floor" theme by default, light theme available; **single resizable
  window with dockable panels**; NATO/APP-6-style symbology for asset/track types.

---

## 4. Key decisions log (with rationale)

| # | Decision | Rationale | Source |
|---|---|---|---|
| D1 | **Single-process desktop app, no server in v1** | User: standalone testable, hot-seat, no LAN | Round 1 Q6, Round 2 |
| D2 | **Offline-first; Space-Track only at vignette-build time** | User: no internet except space-track, with fallback | Round 1 Q1, Round 3 Q15 |
| D3 | **Python engine + desktop GUI (PyQt/PySide), 2D via Qt/QML or matplotlib-class rendering** | Integrated-graphics floor; STK-like 2D; Python physics libs; one language for engine+UI | NFR hardware, D2 |
| D4 | **Deterministic engine keyed on (state, action log, seed)** | Enables wall-clock fast-forward/rewind and v2 replay/branch | `01-architecture-overview.md` |
| D5 | **Data-driven content; JSON vignettes from an in-app builder** | User: in-app scenario builder, JSON per vignette | Round 2 Q11, Round 3 |
| D6 | **2D ECI + RIC for v1; 3D for v1.1** | User explicit | Round 3 Q13 |
| D7 | **Genuine wall clock; White Cell pause/ff/rewind** | User explicit; future per-terminal time | Round 3 Q14 |
| D8 | **No paid dependencies; STK-like look; NATO symbology** | User: avoid STK/paid, familiar visuals | Round 1 Q4, Round 3 Q18 |
| D9 | **Action logging in v1; replay/AAR/CSV in v2** | User: record now, replay later, branch-to-live as save | Round 3 Q10, Q16 |
| D10 | **Role assignment by White Cell checkboxes; splittable bus/payload seats** | User explicit | Round 2 Q7, Q8 |

---

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
  genuine autonomous opponent is a documented **v2 seam** (`08-build-roadmap.md` Phase 8), not a
  v1 deliverable. Vignette text and the parameter tooltips shall be worded accordingly.

---

---

## 7. Architecture (v1)

This section summarizes; `01-architecture-overview.md` holds the detailed seam design. The v1
shape is a **single-process desktop application** with a strict internal boundary between a
UI-agnostic engine and the GUI, so the future networked version (v2) can split them across a
process/network boundary without rewriting the engine.

### 7.1 Layered structure
```
┌─────────────────────────────────────────────────────────────┐
│  GUI (PyQt/PySide desktop, dockable panels, dark ops theme)    │
│  - White Cell console      - Operator console (role-scoped)    │
│  - 2D ECI view  - 2D RIC view   - SOH/telemetry  - timeline    │
│  - scenario builder        - inject panel  - classification    │
├─────────────────────────────────────────────────────────────┤
│  SessionAPI (in-process call interface; future: network RPC)   │
│  - submit_activity / cancel / task_sensor / set_time / inject  │
│  - get_cell_view(role)  - get_white_view()  - load/build/save  │
├─────────────────────────────────────────────────────────────┤
│  Session layer                                                 │
│  - SessionManager (load/tune/start, clock, rewind via replay)  │
│  - CellController (role permissions + fog-of-war CellView)     │
│  - RoleRegistry (seat→assets, bus/payload split)               │
│  - ActionLog (ordered, deterministic, persisted at end)        │
├─────────────────────────────────────────────────────────────┤
│  Engine (deterministic, UI-agnostic, pure-Python)              │
│  - Clock  - World state (ground truth)  - per-cell TrackCatalog │
│  - Propagator*  - AccessProvider*  - EffectResolver*  (*seams)  │
│  - BusModel / PayloadModel  - SafeModeModel  - Scheduler        │
├─────────────────────────────────────────────────────────────┤
│  Content & data                                                │
│  - Vignette JSON   - asset/effect/sensor templates (YAML/JSON) │
│  - bundled TLE snapshot  - Space-Track import (build-time only) │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Why these technology choices
- **Python engine:** mature astrodynamics ecosystem (Skyfield/Astropy/poliastro/sgp4) for the
  moderate model now and the high-fidelity swap later; one language for engine + UI lowers
  maintenance burden for a solo maintainer (Claude Code).
- **PyQt/PySide desktop GUI:** runs offline on a stock government laptop with integrated
  graphics; rich dockable-panel UX; 2D rendering via Qt Graphics/QML or a matplotlib-class
  canvas — no GPU dependency for v1. (Detailed trade vs. a web/Electron stack in
  `02-tech-stack-recommendation.md`; the desktop path is preferred for D2/D3.)
- **No paid dependencies** (D8): all libraries open-source; STK-like look achieved with custom
  2D rendering and NATO symbology, not STK.
- **In-process SessionAPI mirrors a future network API** so v2 LAN multiplayer is an
  infrastructure change, not an engine rewrite.

### 7.3 The 2D views (v1 mandatory)
- **ECI view:** inertial frame — orbits as closed paths, sub-satellite ground track on a 2D
  Earth map, ground stations, sensor/jammer footprints, day/night terminator. STK-like styling.
- **RIC view:** Radial / In-track / Cross-track relative frame centered on the
  **operator-selected satellite** (default: seat's primary asset), with a one-click option to set
  the origin to another tracked object for **RPO/proximity** geometry — the key view for
  co-orbital and escort play. Shows relative position/velocity and closest-approach prediction.
- Both views render **only the cell's belief state** for non-owned objects (render-from-custody),
  with confidence/uncertainty encoding (`09-gui-principles.md` §3); White Cell views may show
  truth.

### 7.4 Time & determinism in a wall-clock hot-seat
- A real-time loop advances the sim clock at the White-Cell multiplier; **pause** halts it.
- **Fast-forward** advances by replaying deterministically at higher speed; **rewind** truncates
  the action log to a chosen sim-time and re-propagates (exact, per FR-E2).
- Because state is a pure function of `(initial, log, seed)`, the wall clock is just a *driver*
  of how fast the log is consumed/extended — this is what makes rewind and the v2 replay/branch
  feature possible from the same substrate.

---

## 8. Data formats

Canonical schemas live in `04-data-model.md`; this section fixes the **file-level contracts** a
new implementer needs.

### 8.1 Vignette JSON (one file per scenario; written by the in-app builder — FR-S1)
```json
{
  "schema_version": "1.0",
  "id": "leo-isr-denial",
  "title": "LEO ISR Denial",
  "classification": "UNCLASSIFIED//TRAINING",
  "mission": "Red denies Blue imagery during a landing window; Blue maintains custody.",
  "learning_objectives": ["..."],
  "start_epoch_utc": "2030-03-15T06:00:00Z",
  "seed": 1234567,
  "roles_needed": {
    "blue": [
      {"role_id": "blue_isr_payload", "label": "Blue ISR Payload Op", "kind": "payload",
       "assets": ["BLUE-ISR-1","BLUE-ISR-2","BLUE-ISR-3"]},
      {"role_id": "blue_isr_bus", "label": "Blue ISR Bus Op", "kind": "bus",
       "assets": ["BLUE-ISR-1","BLUE-ISR-2","BLUE-ISR-3"]},
      {"role_id": "blue_sda", "label": "Blue SDA Op", "kind": "payload", "assets": ["BLUE-SDA-1"]}
    ],
    "red": [
      {"role_id": "red_ew", "label": "Red EW Op", "kind": "payload", "assets": ["RED-EW-1","RED-EW-2"]},
      {"role_id": "red_orbital", "label": "Red Orbital Op", "kind": "both", "assets": ["RED-INSP-1"]}
    ]
  },
  "assets": [
    {"id": "BLUE-ISR-1", "template": "ISR_EO", "owner": "blue",
     "tle": ["1 25544U ...","2 25544 ..."], "ground_segment": ["STATION-A","PROC-1"],
     "comms": {"isl_capable": false}, "fuel_dv_mps": 80}
  ],
  "ground_sites": [
    {"id": "STATION-A", "owner": "blue", "type": "ground_station", "lat": 51.0, "lon": -114.0, "elev_mask_deg": 7}
  ],
  "sensors": [
    {"id": "RADAR-1", "owner": "blue", "kind": "ground_radar", "lat": 50.0, "lon": -104.0,
     "capabilities": ["detect","track"], "task_capacity": 1}
  ],
  "parameters": [
    {"id": "red_ew_intensity", "type": "enum", "options": ["none","harassment","sustained","total"],
     "default": "sustained", "live_editable": true,
     "affects": "Number/power of Red jammers and AI-Red aggressiveness."},
    {"id": "safe_mode_susceptibility", "type": "enum", "options": ["robust","realistic","fragile"],
     "default": "realistic", "live_editable": true, "affects": "How easily effects induce safe mode."}
  ],
  "injects": [
    {"id": "imagery_leak", "label": "Commercial imagery leak", "trigger": {"type": "time", "at_sim": "T+00:45:00"},
     "effects": [{"type": "reveal_asset", "target": "RED-SURF-GRP", "to": "blue"}], "repeatable": false}
  ]
}
```
**Notes:** TLEs are the starting-state source (FR-S2); if a `tle` is absent the builder may
supply Keplerian elements instead. `roles_needed` drives White Cell's checkbox assignment (FR-W2).
`schema_version` lets v2 migrate older files.

### 8.2 Template libraries (shipped with the app, data-driven — D5)
- **Asset templates** (`ISR_EO`, `SATCOM_GEO`, `SDA_GEO`, …): regime defaults, payload type,
  `telemetry_db` (parameters + soft/hard limits), `command_db` (legal commands + constraints),
  vulnerabilities, available defenses. (`05-mission-types-and-counters.md`, `06-bus-...md`.)
- **Effect templates**: the common attribute block from `03-counterspace-taxonomy.md`
  (category, segment, outcome, reversibility, kinetic, debris_risk, attribution, escalation,
  access_constraint, engagement_time, consumes, optional `intended_outcome: safe_mode`).
- **Sensor templates**: kind, lighting/weather constraints, capabilities, task_capacity.

### 8.3 Action log (FR-L; v2 replay/AAR substrate)
Append-only, ordered, timestamped. Each entry: `{seq, sim_time, wall_time, actor_role, kind,
payload, resulting_state_hash}`. The `resulting_state_hash` lets replay verify determinism. At
exercise end the log is written to disk (JSON Lines). **The v2 CSV AAR is a projection of this
log; the v2 branch-to-live feature resumes the engine from a chosen `seq` and continues
appending to a new log** — design these reads/writes now even though the UI is later.

### 8.4 TLE handling & Space-Track (D2, FR-S2)
- **Build-time only:** the scenario builder may query Space-Track for current TLEs of chosen
  catalog objects. Credentials entered by White Cell; results **cached locally** for offline
  reuse.
- **Fallback when Space-Track is unreachable:** (a) a **bundled snapshot** of representative/
  generic TLEs ships with the app; (b) White Cell **pastes/enters TLEs manually**; (c) the
  builder can synthesize a TLE from entered Keplerian elements.
- **Runtime:** never requires network. A saved vignette is fully self-contained.

---

## 9. Non-functional requirements (NFR)

- **NFR-1 Offline:** the running application shall require **no network access**; only the
  scenario builder's optional TLE import touches the network (Space-Track), with documented
  fallbacks. (D2)
- **NFR-2 Hardware floor:** shall run acceptably on a **typical government laptop, integrated
  graphics, 16 GB RAM**, for scenarios up to ~24 satellites and the 6-channel window
  computation, at interactive frame rates in the 2D views.
- **NFR-3 Determinism:** identical `(initial state, action log, seed)` shall reproduce identical
  state (verified by state hashes); a property test shall enforce this. (FR-E2)
- **NFR-4 Performance:** window computation and state tick for ~24 satellites + sensors shall
  keep the UI responsive at time multipliers up to at least 600× without stalling the event loop
  (heavy propagation off the UI thread).
- **NFR-5 Security posture (research-grade):** standard secure development practices — input
  validation on all loaded files, no execution of scenario-embedded code, dependency pinning,
  least-privilege file access. No formal accreditation required for v1 (research tool), but no
  practice that would block later RMF/ITSG-33 review (e.g., no telemetry phone-home, no
  hard-coded secrets).
- **NFR-6 Robustness:** invalid scenario JSON or TLEs shall fail at load with a precise,
  actionable White Cell error; the running engine shall never crash on a *legal* operator action;
  illegal actions are blocked with explanation; tactically poor but legal actions run to their
  natural outcome. (§3.3)
- **NFR-7 Maintainability:** UI-agnostic engine with ≥80% unit-test coverage on engine logic;
  all content data-driven; the three fidelity seams (`Propagator`, `AccessProvider`,
  `EffectResolver`) documented and independently testable.
- **NFR-8 Portability:** Windows-first (typical CAF laptop), with no OS-specific dependencies
  that would prevent Linux/macOS dev use.
- **NFR-9 Accessibility:** affiliation/confidence conveyed by **shape/label, not color alone**;
  high-contrast presentation mode; keyboard shortcuts for common actions. (`09-gui-principles.md`)
- **NFR-10 Classification hygiene:** the White-Cell-selected banner renders on every screen and
  every exported file; default content is unclassified/fictional. (FR-W5)

---

## 10. Milestones & acceptance criteria

The build sequence is detailed in `08-build-roadmap.md`; this section states the **milestone
gates and acceptance criteria** that declare each milestone done. Requirement tags trace to §5/§9.

| Milestone | Delivers | Acceptance criteria (gate) |
|---|---|---|
| **M0 Skeleton** | Repo, test harness, CI-style local checks, data loaders | Project builds; a trivial vignette JSON loads and validates; lint/test pipeline runs. |
| **M1 Deterministic core** | Clock, world state, action log, state hashing | **NFR-3** property test passes: replay reproduces identical hashes across a random action sequence. (FR-E1/E2, FR-L1) |
| **M2 Orbits & windows** | Propagator + AccessProvider (moderate) | For a known TLE + station, computed pass times match a reference (Skyfield) within tolerance; all six channel windows compute. (FR-E3/E4) |
| **M3 Effects & SDA** | EffectResolver, TrackCatalog, custody decay, cyber exception | Jam denies a link in its footprint window; kinetic spawns debris + political consequence; cyber resolves outside any pass; custody decays/resets; weapons-quality gate blocks an under-tracked engagement. (FR-E6/E7/E8) |
| **M3.5 Bus & payload** | BusState SOH, payload gating, pass-gated telemetry, safe-mode induce | Battery drains in eclipse → red alarm; cyber induces safe mode per susceptibility dial; safe-mode discovered only at next pass via stored-telemetry dump; full storage blocks ISR collect. (FR-B1–B5) |
| **M4 Session & one vignette (headless)** | SessionManager, CellController/fog, RoleRegistry, in-process API | Scripted test plays **Vignette 1** to a win condition, then **rewinds and branches**; fog verified (Red cannot read Blue hidden state via API); roles scope asset access. (FR-W3/W6, OR-1/2, FR-E7) |
| **M4.5 Planning, tasking & recovery (headless)** | PlannedActivity scheduler, ISL/stored paths, sensor tasking, safe-mode recovery | Command queues to next pass *or* sooner via ISL; sensor tasking shrinks uncertainty and unlocks a gated engagement; multi-pass safe-mode recovery with **re-safe on persistent root cause**, then success after patch; `quick` dial → one-pass recovery. (FR-P1–P4, FR-B5) |
| **M5 GUI** | PyQt app: White Cell console, role-scoped operator console, **2D ECI + RIC**, SOH/telemetry, timeline, queue, inject panel, classification banner, scenario builder, hot-seat blank/handoff | A facilitator runs **Vignette 1 entirely from the GUI**: builds/loads it, assigns roles by checkbox, starts the **wall clock**, hot-seat-swaps Blue↔Red with screen blank, plans a command into a future pass, tasks a sensor, watches a jam degrade ISR and a satellite enter and recover from safe mode — with every disabled control explaining itself and the RIC view showing a relative approach. (FR-W1/2/4/5, FR-S1–S3, OR-1–6, UR, **the demo DoD below**) |
| **M6 Content** | Remaining 7 vignettes as JSON; scenario-builder validation polish | All 8 vignettes load, pass validation, and are playable; a White Cell user authors a new simple vignette in-app and saves valid JSON. (FR-S1–S3) |
| **M7 Logging & v2 seams** | Action-log persistence; documented seams for replay/AAR/CSV/branch-to-live, 3D, networking, constellation aggregation | Action log written at exercise end and proven sufficient to deterministically reconstruct the run offline; seam docs/scaffolds exist (no full v2 build). (FR-L1/L2, §3.2) |

### 10.1 Definition of Done — first demo (single named scenario)
**Vignette 1 "LEO ISR Denial," 2 Blue seats + 2 Red seats + 1 White, hot-seat on one laptop:**
White Cell builds the scenario (TLEs from Space-Track or bundled), assigns the four operator
roles by checkbox (incl. a split Blue ISR bus vs. payload seat), sets classification, and starts
the wall clock. Blue plans imaging + downlink across passes and tasks an SDA sensor; Red plans a
downlink jam and a cyber effect that induces **safe mode** on a Blue ISR satellite. Blue notices
the payload stop, **confirms safe mode at the next pass**, runs a recovery, and is briefly
**re-safed** until the root cause is addressed. Seats hand off via **screen blank**; White Cell
**pauses** once for a timeout and **rewinds** once to re-run a decision. The action log is
written at the end. **If all of that works from the GUI, v1 is a success.**

---

## 11. Risks & mitigations

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Wall-clock + heavy propagation stalls the UI | Sluggish, unusable at high multipliers | Med | Propagation off the UI thread; cache windows; precompute upcoming passes; NFR-4 gate. |
| Determinism broken by hidden nondeterminism (dict order, floats, RNG) | Rewind/replay diverge; v2 replay impossible | Med | Single seeded RNG; ordered structures; state hashing in CI; NFR-3 property test from M1. |
| Hot-seat fog leaks (one role sees another's private data) | Training value destroyed | Med | Enforce fog in the engine `CellView`, not the UI; test that the API itself withholds data (M4). |
| Scope creep into 3D/networking/replay too early | v1 slips | High | Hard non-goals (§3.2); seams documented but not built; demo DoD is the bar. |
| Space-Track unavailable or auth changes | Can't seed real TLEs | Med | Bundled snapshot + manual entry + Keplerian synthesis; runtime never needs network (D2). |
| Moderate-fidelity orbits look "wrong" to STK-savvy users | Credibility loss | Med | Validate pass times vs. Skyfield (M2); document fidelity explicitly; J2 included for realistic ground-track drift. |
| Safe-mode mechanic dominates play | Skews training | Low (now mitigated) | Tunable dials + detection/recovery counterplay (`12-safe-mode-loop.md`); default `realistic`. |
| Single maintainer (Claude Code) context loss between phases | Inconsistent build | Med | This PSD + companion docs as durable spec; per-phase acceptance gates; tests encode intent. |

---

## 12. Glossary

- **Access window** — interval when an actor asset can interact with a target via a channel.
- **AAR** — After-Action Review (v2 replay + CSV export).
- **Bus** — the spacecraft vehicle (power, attitude, thermal, propulsion, C&DH, comms).
- **Custody** — current knowledge of an object's location/state; decays without observation.
- **ECI / RIC** — Earth-Centered Inertial frame / Radial-In-track-Cross-track relative frame.
- **Hot seat** — one terminal shared by many roles, swapped in turn.
- **ISL** — Inter-Satellite Link (crosslink); a rare faster command path.
- **PlannedActivity** — unified scheduled command or collection task.
- **Payload** — the mission equipment (SATCOM, ISR, SIGINT, SDA, space-control, etc.).
- **Safe mode** — protective state that disables the payload; reversible; inducible by attack.
- **SDA** — Space Domain Awareness; the belief state from which views are rendered.
- **SOH** — State of Health (the bus health picture operators monitor).
- **The five D's** — deceive, disrupt, deny, degrade, destroy (effect outcomes).
- **TLE** — Two-Line Element set (orbital state from Space-Track or manual entry).
- **Weapons-quality track** — custody good enough (confidence + characterization) to engage.

---

*End of Project Start Document. Companion design files provide implementation detail; this PSD
is the baseline of record for v1 scope, requirements, and acceptance.*

---

# PSD Part 3 — Operator Workflows, State Machines, Test Plan, Schedule

The preceding sections define *what* and *why*. Part 3 adds the operational and engineering
detail a real project start needs before code: concrete operator walkthroughs, the key state
machines, a test strategy mapped to requirements, and a phased schedule. These reduce ambiguity
for the implementer and serve as the basis for acceptance.

## 13. Operator workflow walkthroughs

These narrate the **actual click-path** for each major role so the GUI (M5) is built around real
tasks, not abstract menus. Each references the requirements it satisfies.

### 13.1 White Cell — set up and start an exercise
1. Launch app → **New Exercise** → choose **Build new** or **Load vignette JSON**. (FR-S1)
2. If building: pick a base template or blank; set title, mission text, **start epoch**, **seed**,
   and **classification** (UNCLASSIFIED//EXERCISE or //TRAINING). (FR-W5)
3. Add assets: choose templates (e.g., `ISR_EO`, `SATCOM_GEO`), then set each asset's starting
   orbit by **importing a TLE from Space-Track** (if online) or **pasting/entering one manually**,
   or entering Keplerian elements. Assign ground sites and sensors. (FR-S2)
4. Define `roles_needed` (the builder suggests roles from the assets present): e.g., *Blue ISR
   Bus Op*, *Blue ISR Payload Op*, *Blue SDA Op*, *Red EW Op*, *Red Orbital Op*. (FR-W2, OR-2)
5. Set tunable parameters incl. the **safe-mode dials**; set injects. **Validate** → fix any
   precise errors (bad TLE, unsatisfied role). **Save JSON.** (FR-S3, NFR-6)
6. **Assign seats:** a checkbox matrix maps each human seat → roles → assets, and marks each role
   **bus / payload / both**. (FR-W2, OR-1/2)
7. **Start** → wall clock begins at the chosen multiplier. (FR-W3, OR-4)

### 13.2 White Cell — run the exercise
- Watch the **god-view**: ground truth, both cells' belief, SOH of all assets, the timeline,
  and a live event log. (FR-W6)
- **Manage the hot seat:** announce who's up; the active operator blanks the screen; White Cell
  confirms the next role; keyboard passes; new operator un-blanks into their role view. (OR-3)
- **Control time:** raise/lower the multiplier to skip dead time between passes; **pause** for a
  timeout or teaching point; **rewind** to re-run a decision. (FR-W3, OR-4)
- **Inject** scripted or manual events; **re-tune** live parameters (e.g., raise Red EW intensity
  or change a safe-mode dial). (FR-W4/W7)
- Adjudicate manually (v1 has no auto-scoring); narrate consequences.

### 13.3 Blue/Red — bus operator
1. Sit, un-blank into the assigned **bus** role; see only assigned assets. (OR-1)
2. Read the **fleet SOH rollup** (red/yellow/green); drill into a satellite → subsystem →
   parameter. Note the **telemetry timestamp** — is this fresh (in contact) or stale? (FR-B1/B3)
3. See **"next contact in 00:06:12 via STATION-A"**; open the **pass-timeline ribbon**. (FR-P1)
4. **Plan a pass:** queue bus commands (e.g., desaturate wheels, manage battery before eclipse,
   slew to attitude) into the next uplink window; the queue shows scheduled times; edit/cancel
   freely until uplink. (FR-P1/P3)
5. If a satellite has entered **safe mode**: confirm at next contact via the stored-telemetry
   dump, **diagnose**, and queue the multi-step **recovery procedure**; watch for **re-safe** if
   a root cause persists. (FR-B5, §12 of safe-mode doc)
6. Hand off (blank screen) when White Cell calls the next role. (OR-3)

### 13.4 Blue/Red — payload operator (per type)
- **SATCOM:** monitor transponder power/temperature and **interference level**; if a carrier
  degrades (a jam, experienced as interference — not a label), re-plan frequency/beam or shift
  customers. (FR-B4, taxonomy)
- **ISR:** build a **collection schedule** against target passes; watch **storage fill** and the
  **downlink backlog**; queue downlinks at ground/relay passes; read **image-quality** (a dazzle
  or weather shows as degraded product). (FR-B4) — exercises the collect-vs-downlink split.
- **SIGINT/SDA:** **task sensors** (search/track/characterize) within geometry and **single-task
  contention**; watch custody/uncertainty change on report; cue radar→optical. (FR-P2)
- **Space-control:** select target (needs a **weapons-quality track**), effect level on the five
  D's, and timing inside an engagement/proximity window; read **uncertain effect assessment**.
  (FR-E6/E7)

### 13.5 Red — a representative offensive sequence (Vignette 1)
1. Red EW Op pre-plans a **downlink jam** active over the landing area for the landing window.
2. Red Orbital Op tasks SDA to **maintain custody** of the Blue ISR sats (know when they image).
3. Red (cyber) attempts a **safe-mode inducement** on one Blue ISR sat (susceptibility per dial);
   if it succeeds, that sat's payload drops — Red has bought time without debris. (FR-B5)
4. Red weighs whether to escalate to kinetic (default **off**); doing so would spawn debris and a
   political-consequence inject. (FR-E6)

---

## 14. Key state machines

Explicit states the engine implements; the UI reflects them. (Detailed fields in
`04-data-model.md`.)

### 14.1 PlannedActivity (command or collection)
```
DRAFT ─▶ PLANNED ─▶ ACTIVE ─▶ EXECUTED            (commands)
                          └─▶ REPORTED            (collection)
   any ─▶ CANCELLED (operator)     ACTIVE ─▶ FAILED{reason}
```
Transitions gated by re-validation at execute time (ownership/window/resources/ROE/track). (FR-P4)

### 14.2 Bus mode / safe mode
```
NOMINAL ─(fault|power|attitude|thermal|cyber|ew|bus_stress, susceptibility check)─▶ SAFE_MODE
SAFE_MODE: payload OFF; bus autonomy points to sun, awaits ground
SAFE_MODE ─(recovery chain across passes; per-step success)─▶ NOMINAL
SAFE_MODE ─(root cause persists)─▶ SAFE_MODE  (re-safe)
```
Defender-visible substates: `defender_confirmed`, `defender_diagnosis`. (FR-B5)

### 14.3 Custody / Track confidence
```
UNKNOWN ─(detection)─▶ TRACKED(low conf) ─(characterize)─▶ CHARACTERIZED
TRACKED ─(no obs, time)─▶ confidence decays ─▶ may fall below gate ─▶ custody lost
any ─(observation window)─▶ confidence reset/raised, uncertainty shrinks
```
Weapons-quality gate = `confidence ≥ threshold AND characterized`. (FR-E7)

### 14.4 Exercise session
```
SETUP ─▶ ASSIGNED(roles) ─▶ RUNNING ⇄ PAUSED ─▶ ENDED(log written)
RUNNING ─(rewind)─▶ replays to earlier sim_time, continues  (deterministic)
```
(FR-W3, FR-L2)

---

## 15. Test plan

Testing is part of the deliverable, not an afterthought (NFR-7). Strategy by layer:

### 15.1 Engine unit tests (headless, fast, deterministic)
- **Propagation/windows (M2):** pass times for known TLEs vs. Skyfield reference within
  tolerance; J2 nodal drift present; eclipse intervals sane; all six channels produce windows.
- **Effects (M3):** each category→outcome; reversibility restores state; kinetic spawns a
  debris object and trips the political-consequence side effect; cyber resolves with no window.
- **Custody (M3):** decay curve; reset on observation; gate blocks under-tracked engagement.
- **Bus/payload (M3.5):** battery drains in eclipse and trips limits; storage fills and blocks
  collection; payload disabled when bus unhealthy; safe-mode inducement honors the susceptibility
  formula and dial.
- **Scheduler (M4.5):** ground-uplink vs. ISL path selection; stored-program trigger;
  re-validation failure paths; recovery chain incl. re-safe-on-persistence and the difficulty dial.

### 15.2 Determinism property test (NFR-3, from M1)
Generate randomized legal action sequences; assert that re-running from the same seed reproduces
identical per-tick **state hashes**; assert that **rewind→replay** matches the original forward
run up to the rewind point. Run in the local CI-style check on every change.

### 15.3 Fog-of-war / role tests (M4)
Assert the **API itself** (not just the UI) withholds: Red cannot read Blue hidden parameters,
unobserved objects, or another role's private state; a bus role cannot issue payload commands and
vice-versa; an operator cannot act on unassigned assets. (OR-1/2, FR-E7)

### 15.4 Scenario validation tests (M6)
Malformed TLE, missing `roles_needed` asset, unknown template, out-of-range parameter → precise
load-time errors (NFR-6). All 8 shipped vignettes load and validate.

### 15.5 GUI/workflow acceptance (M5, manual + scripted where possible)
Drive the **demo DoD** (§10.1) end-to-end; verify every disabled control explains itself; verify
the screen-blank hides sensitive content; verify the classification banner on screens and the
written log.

### 15.6 Performance test (NFR-2/4)
~24-satellite scenario at 600× on the reference laptop profile: UI stays responsive; window
computation does not block the event loop; memory stable over a 2-hour run.

---

## 16. Phased schedule & effort

Sequencing follows `08-build-roadmap.md`; this is the milestone-level view with relative effort
(S/M/L) and dependencies. (No calendar dates — single maintainer, user-driven pace.)

| Phase / Milestone | Effort | Depends on | Key output |
|---|---|---|---|
| M0 Skeleton | S | — | repo, loaders, test harness |
| M1 Deterministic core | M | M0 | clock, world, log, hashing, **determinism test** |
| M2 Orbits & windows | L | M1 | Propagator + AccessProvider (moderate) |
| M3 Effects & SDA | L | M2 | EffectResolver, custody, cyber exception |
| M3.5 Bus & payload + safe-mode induce | M | M3 | SOH, payload gating, pass-gated telemetry |
| M4 Session & Vignette 1 (headless) | M | M3.5 | SessionManager, fog CellView, roles |
| M4.5 Planning, tasking & recovery | M | M4 | unified scheduler, ISL, sensor tasking, recovery |
| M5 GUI (incl. 2D ECI+RIC, builder, hot-seat) | L | M4.5 | the playable app; **demo DoD** |
| M6 Content (7 vignettes + builder polish) | M | M5 | full vignette library |
| M7 Logging persistence & v2 seams | S | M5 | written log; documented seams |
| **v1.1** 3D belief-state globe | L | M5 | STK-like 3D viewer (`10-sda-3d-viewer.md`) |
| **v2** replay/AAR/CSV, branch-to-live, LAN, constellation aggregation | L+ | M7 | networked, replayable, scalable |

**Critical path:** M1→M2→M3→M3.5→M4→M4.5→M5. The 2D views and scenario builder are the long
poles in M5; start their design during M4.5.

---

## 17. Open items to confirm with White Cell before/after first demo

These are deliberately left open; sensible defaults are in place (§3.3) and can be changed in
data or a short follow-up without architectural impact:
1. Exact **NATO/APP-6-style symbol mapping** for each asset/track type (a lookup table — easy to
   adjust). 
2. Whether observers should default to **god-view** or a **named cell view**.
3. Default **time multiplier** per vignette (currently a parameter; confirm sensible defaults per
   scenario — GEO RPO wants high, LEO ISR wants modest).
4. Whether the **screen-blank** should also require a White Cell click to un-blank (extra
   discipline) or trust the verbal handoff (current default: verbal).
5. The precise **soft/hard limit values** in each asset template's `telemetry_db` (start from the
   research defaults; tune for teaching).

*End of PSD Part 3.*
