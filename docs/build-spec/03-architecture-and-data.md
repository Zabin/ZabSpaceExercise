[← Build Spec index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 7. Architecture (v1)

> **As-built note (ADR-0028):** this section originally described a PyQt/PySide desktop GUI
> planned at v1-design time. The shipped presentation is **FastAPI + browser**, per ADR-0008 and
> [`architecture/03-architecture.md`](../architecture/03-architecture.md) (GDS-03). §7.1/§7.2 below
> are rewritten to describe the as-built system directly; the PyQt description is retired.

This section summarizes; `01-architecture-overview.md` holds the detailed seam design (also
historical re: GUI choice — see the as-built note above). The v1 shape is a **single FastAPI
server process** with a strict internal boundary between a UI-agnostic engine and the
presentation layer; one or more browser clients (single-machine hot-seat or LAN) connect to that
one process, fog-of-war filtered server-side at the `SessionAPI`/`CellController` boundary.

### 7.1 Layered structure
```
┌─────────────────────────────────────────────────────────────┐
│  Browser client (HTML/CSS/JS, no build step, no framework)    │
│  - White Cell console      - Operator console (role-scoped)    │
│  - 2D belief map  - 3D orthographic globe  - SOH/telemetry      │
│  - in-app scenario builder  - inject panel  - classification    │
├─────────────────────────────────────────────────────────────┤
│  FastAPI server (`ui_web/server.py`) — HTTP polling per tab,    │
│  the network seam every browser client talks to                │
├─────────────────────────────────────────────────────────────┤
│  SessionAPI (the single seam into the engine; also the          │
│  in-process call interface FastAPI's handlers invoke)           │
│  - issue_order / cancel / task_sensor / set_clock / inject       │
│  - get_cell_view(role)  - get_white_view()  - load/build/save   │
├─────────────────────────────────────────────────────────────┤
│  Session layer                                                 │
│  - SessionManager (load/tune/start, lazy clock, rewind/replay)  │
│  - CellController (role permissions + fog-of-war CellView)     │
│  - per-session RLock (LAN multiplayer mutation serialization)  │
│  - ActionLog (ordered, deterministic, persisted at end)        │
├─────────────────────────────────────────────────────────────┤
│  Engine (deterministic, UI-agnostic, pure-Python)              │
│  - Clock  - World state (ground truth)  - per-cell TrackCatalog │
│  - Propagator*  - AccessProvider*  - EffectResolver*  (*seams)  │
│  - BusModel / PayloadModel  - SafeModeModel  - Scheduler        │
│  - Verb-preview helpers (pure, read-only):                      │
│      maneuver.py · isr.py · jam.py · engage.py · cyber.py       │
│      sigint.py · perturbations.py · sun.eclipse_fraction        │
├─────────────────────────────────────────────────────────────┤
│  Content & data                                                │
│  - Vignette YAML   - asset/effect/sensor templates (YAML/JSON) │
│  - bundled TLE snapshot  - Space-Track import (build-time only) │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Why these technology choices
- **Python engine:** mature astrodynamics ecosystem (Skyfield/sgp4) for the moderate model now and
  the high-fidelity swap later; one language for engine + presentation server lowers maintenance
  burden for a solo maintainer (Claude Code).
- **FastAPI + browser presentation (supersedes the originally-planned PyQt/PySide desktop GUI,
  ADR-0008):** the LAN-multiplayer seam comes nearly free — every browser tab (single-machine or
  LAN) talks HTTP to the same server process under a per-session `RLock`, with no separate desktop
  client to ship or update. 2D belief map and 3D orthographic globe are rendered in-browser
  (canvas), no native GUI toolkit or GPU dependency. (Original trade discussion vs. desktop in
  `02-tech-stack-recommendation.md`; superseded by ADR-0008.)
- **No paid dependencies** (D8): all libraries open-source; STK-like look achieved with custom
  2D/3D rendering and NATO-adapted symbology, not STK.
- **`SessionAPI` as the single seam.** Every browser client (LAN or local) hits the same
  `InProcessSession` via HTTP polling; the server-authoritative lazy clock on `SessionManager`
  advances sim time exactly once regardless of polling-tab count. The multiplayer transport is in
  production — see `FUTURE-WORK.md` §1.

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
