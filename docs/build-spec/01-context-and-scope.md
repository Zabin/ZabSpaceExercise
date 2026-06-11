[← Build Spec index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 0. How to read this document

This is the project-start specification for a single-machine, hot-seat professional military
education (PME) wargaming tool for space control and orbital warfare. It is written to the depth
a real project kickoff requires: scope, stakeholders, decisions, functional and non-functional
requirements, architecture, data formats, milestones, acceptance criteria, risks, and a
glossary. Reading order for a new implementer:

1. This PSD §1–§6 (context, scope, decisions, requirements).
2. `01-architecture-overview.md` and `04-data-model.md` (the contract).
3. The research files in `../research/` (why the rules are what they are).
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
- Single-machine hot-seat **and** LAN cooperative both supported (one FastAPI server, N browser
  tabs / machines polling it; fog-of-war enforced server-side at the `SessionAPI` boundary —
  see `FUTURE-WORK.md` §1). Not a dedicated-server architecture and not internet-public.
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
- The eight specified vignettes (`../vignettes/`) plus the ability to author more.

### 3.2 Deferred (explicit non-goals for v1)
| Deferred item | Target | Why deferred |
|---|---|---|
| ~~LAN multiplayer~~ | ✅ shipped in M8 | HTTP polling against the single FastAPI server; per-session RLock + server-authoritative lazy clock; no separate dedicated-server architecture |
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
