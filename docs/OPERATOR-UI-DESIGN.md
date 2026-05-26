# Satellite Bus & Payload Operator UI — Design Specification

**Document type:** UI/UX design specification (implementation-ready)
**Status:** Design proposal — to be implemented to augment the existing tool
**Audience:** Claude Code (implementer), White Cell facilitators, UX reviewers
**Companions (authoritative):** `09-gui-principles.md` (UX north star), `05-cell-interfaces.md`
(cells & permitted actions), `06-bus-and-payload-operations.md` (bus/payload reality),
`13-operator-command-catalog.md` (the verb catalog), `11-command-planning-and-tasking.md`
(plan-first + tasking), `12-safe-mode-loop.md` (recovery), `10-sda-3d-viewer.md` (belief render).
**Implemented surfaces this builds on:** `spacesim/engine/{bus,telemetry,orders,effects,custody}.py`,
`spacesim/session/{manager,cells,scene,aar}.py`, and the FastAPI routes in `spacesim/ui_web/server.py`
(`/view`, `/scene`, `/telemetry`, `/windows`, `/orders`, `/cancel`, `/alarms`, `/aar`, `/save`, …).

> This spec describes the **operator console** layer — the part of the UI an individual Red/Blue
> operator (and White Cell when driving a side) uses to **monitor, troubleshoot, and task** their
> bus and payload. It refines and extends the current minimal web front end; it does not change the
> deterministic engine or the fog-of-war boundary, both of which it consumes verbatim.

---

## 0. How to read this document

The spec is organized so an implementer can build it panel-by-panel:

1. **§1–§3** establish *who* operates, the *principles*, and the *screen architecture* (the frame
   every later panel lives in).
2. **§4–§7** are the four operator surfaces: the **fleet/monitoring** surface (§4), the **bus
   subsystem console** (§5), the **payload consoles by mission type** (§6), and the **command &
   tasking** surface (§7).
3. **§8–§10** are the cross-cutting *user flows*: **monitoring**, **troubleshooting/diagnosis**, and
   **tasking**, written as step sequences with explicit button logic.
4. **§11** covers **per-cell differences** (every operator type for White/Red/Blue).
5. **§12–§15** are the *engineering annexes*: interaction grammar & button-state logic, the widget
   library, the data/API binding, and wireframes.
6. **§16–§18**: phasing, acceptance criteria, open questions, glossary.

Each interactive element is specified as **`control → precondition → action → result → why-disabled`**
so button logic is unambiguous.

---

## 1. Operators, roles, and cells

### 1.1 The three cells (recap)
- **White Cell** — facilitator. Sees ground truth (god-view), controls time, fires injects, may
  *drive* Red or Blue in a solo exercise. Uses every operator console below, plus the control panel.
- **Blue Cell** — friendly operators. Defensive posture: keep the fleet healthy, deliver mission
  product, detect/diagnose/recover from attack.
- **Red Cell** — adversary operators. Offensive posture: deny/degrade/destroy Blue space capability
  with reversible-first effects.

A cell sees **only its own assets and its own SDA custody** (fog-of-war, enforced server-side in
`CellController.view`). The operator console is identical in *layout* for Red and Blue; only the
*inventory* and the *available actions* differ.

### 1.2 Operator types (the seat the human holds)
Concurrency is **hot-seat** in v1 (up to 16 notional participants, one keyboard); the console must
make the *active role* obvious and switching cheap. Three operator archetypes, each a filter on what
the console shows and offers:

| Operator type | Owns | Primary surfaces | Command scope (`roles` field in `command_db`) |
|---|---|---|---|
| **Bus operator (TT&C)** | spacecraft bus health & safety | Fleet rollup, Bus console (§5), Command queue | PART 1 verbs (`eps.*`, `adcs.*`, `prop.*`, `tcs.*`, `cdh.*`, `comms.*`) |
| **Payload operator** | the mission payload | Payload console (§6), Tasking, Command queue | PART 2 verbs for that payload type |
| **SDA / tasking operator** | the cell's sensors & TrackCatalog | Tasking (§7.4), belief map/3D, Track panel | `sda.*` + sensor `task_*` (PART 2.4) |

In small exercises one human holds **bus + payload + SDA** for an asset (OR-2); the console therefore
**unifies** them into one screen and uses the `roles` field on each command to show/hide verbs rather
than forcing a seat change. A **role selector** (Bus / Payload / SDA / All) filters the command menu
and the default panel focus without hiding situational awareness.

### 1.3 Mission types covered
Every mission type in the catalog has a payload console (§6): **SATCOM**, **ISR-EO/IR**, **ISR-SAR**,
**SIGINT/ELINT**, **SDA/inspector**, **Space-control effector** (EW / directed-energy / RPO / cyber /
kinetic), **PNT**, **Missile Warning**, **Weather/environmental**. Ground assets (stations, jammers,
interceptors, cyber units) get a reduced console (no bus; action-only).

---

## 2. Design principles applied to the operator console

Inherits all of `09-gui-principles.md` (P1–P7). The console makes them concrete:

- **P1 Geometry never hidden** → a persistent **pass-timeline ribbon** and **next-contact countdown**
  are always on screen for the selected asset; every command form shows its scheduled window.
- **P2 Plan-first** → the primary verb is *Plan* (queue to next window), not *Execute now*. *Execute
  now* exists only when a realtime/ISL/cyber path is available and is visually secondary.
- **P3 Show belief, mark uncertainty** → tracks/telemetry carry confidence/limit coloring; pass-gated
  telemetry shows its **as-of timestamp** and greys when stale.
- **P4 Always answer "why can't I?"** → disabled controls carry a machine-generated reason string from
  the order validator (`OrderSystem._validate` already returns these: `no_window`,
  `roe_kinetic_not_authorized`, `no_weapons_quality_track`, `insufficient_delta_v`, `not_owner`, …).
- **P5 Reversible for the trainee** → queued orders are cancellable (`/cancel`); planning is a sandbox.
- **P6 One screen, three contexts** → map/3D, timeline, decision panel co-visible; troubleshooting and
  tasking open in side rails, never full-screen modals.
- **P7 Doctrinal symbology** → APP-6-style affiliation (Blue/Red/Yellow/Green/Grey), confidence
  encoding (solid/aging-ellipse/ghost/"?"), consistent everywhere.

Two **console-specific** principles added here:

- **C1 — Symptoms, not verdicts.** Monitoring and troubleshooting surfaces show *physical telemetry*
  (RX power, FSW error count, optics temperature). The console **never labels the cause** ("you are
  being jammed"). The operator diagnoses. This is already true of `telemetry.py` and the alarm feed;
  the UI must preserve it (see §9).
- **C2 — The bus gates the payload, visibly.** When the bus blocks a payload action (no power, bad
  attitude, safe mode, full storage), the payload control is disabled with the *bus* reason, and the
  offending bus parameter is one click away.

---

## 3. Screen architecture

### 3.1 Canonical layout (single display)
A fixed region grid keeps the world, the clock, and the decision panel co-visible (P6). Regions:

```
┌───────────────────────────────────────────────────────────────────────────────────┐
│ TOOLBAR  vignette · seat(cell+role) · SIM-CLOCK(UTC,T±, ×mult) · play/step/rewind   │ A
├───────────────┬───────────────────────────────────────────────┬─────────────────────┤
│ FLEET RAIL    │ WORLD VIEW  (2D belief map ⇆ 3D globe tabs)     │ DECISION RAIL       │
│ • SOH rollup  │  render-from-custody; coastlines+borders;       │  context-sensitive: │ B
│ • next-contact│  own assets known, tracks as uncertainty vols   │  • Command compose  │
│ • alarms dot  │                                                 │  • Tasking          │
│ • posture     │                                                 │  • Subsystem detail │
├───────────────┼───────────────────────────────────────────────┴─────────────────────┤
│ PASS-TIMELINE RIBBON (selected asset) — uplink/downlink/observe/jam/engage/RPO lanes │ C
├───────────────────────────────────────────────────────────────────────────────────┤
│ WORKBENCH (tabbed): Bus console · Payload console · Command queue · Telemetry graphs │ D
├───────────────────────────────────────────────────────────────────────────────────┤
│ ALARM / EVENT / INTEL FEED  (scrolling, newest first)                                │ E
└───────────────────────────────────────────────────────────────────────────────────┘
```

- **A Toolbar** — global state + time (White Cell time controls disabled for Red/Blue). The **seat
  chip** shows cell + active role and is the cell/role switcher.
- **B Three columns** — Fleet rail (entry to monitoring), World view (situational awareness), Decision
  rail (the active task: compose/task/inspect).
- **C Ribbon** — the always-visible geometry anchor (P1).
- **D Workbench** — the deep surfaces (bus, payload, queue, graphs) as tabs so they share space
  without hiding B/C.
- **E Feed** — alarms (limit crossings, safe-mode), injects, attribution signals, AAR markers.

### 3.2 Selection model
A **single "selected asset"** drives B-right, C, and D. Selecting an asset in the Fleet rail, the map,
the 3D globe, or the ribbon all set the same selection (one source of truth). A secondary **"selected
target"** (an enemy track) is set by clicking a track and feeds offensive command forms.

### 3.3 Multi-display & presentation mode
Per §5 of GUI principles: regions B-center (world) and C+D can detach to a second screen; a
**high-contrast presentation mode** (large type, thicker symbols) supports projector use. Layout is
re-flowable, not pixel-fixed.

### 3.4 Density & responsiveness
Military information density (P-audience): compact gauges, no whitespace padding for its own sake, but
strict alignment. Optimistic UI for LAN latency: an issued order shows **`queued (pending)`** until the
server (SessionManager) acks, then resolves to `queued`/`rejected`.

---

## 4. Monitoring surface — Fleet rail & SOH rollup

The **entry point** for every exercise and the home of the monitoring flow (§8). Implements the
mission-control "fleet → satellite → subsystem → parameter" drill-down (`06` §3.1).

### 4.1 Fleet rail (region B-left)
One row per own asset (from `GET /view/{cell}.own_assets`; White uses god-view):

```
●  ISR-EO-1      LEO-SSO     ◷ 04:12   ⚡84% ⛽62% 📡   ⚠2
│  │             │           │         │              │
SOH ID          regime    next-contact resource gauges  alarm count
```

- **SOH dot** — single green/yellow/red rollup = worst subsystem (red if `bus_state.mode==safe_mode`).
  Computed exactly like `bus.overall_status`. **Button logic:** click row → select asset (drives B/C/D).
- **Next-contact countdown** (◷) — time to the asset's next command/telemetry window from
  `GET /windows/{cell}/{asset}`; colors **amber < 5 min**, **red < 1 min** (P1, draws the eye).
- **Resource micro-gauges** — battery SoC, propellant, ammo/power as appropriate; from telemetry DB.
- **Posture icon** — escort / threat-warning / hardened / jamming (active `def.*`/`sc.*` postures).
- **Alarm badge** (⚠N) — count of off-nominal parameters + safe-mode for this asset (from `/alarms`).

A **filter bar** above the rail: All / Bus-red / Payload-degraded / Under-attack-symptoms / Safed.

### 4.2 Roll-up coloring rules
| Color | Meaning | Trigger |
|---|---|---|
| 🟢 green | nominal | all subsystems green, mode nominal |
| 🟡 yellow | degraded / watch | any subsystem soft-limit breached (yellow) |
| 🔴 red | hard limit / safed / lost | any hard-limit breach, `safe_mode`, or `health==destroyed` (LOS) |

The dot is **not** an attack indicator (C1) — a red dot from jamming-driven RX power looks identical to
a red dot from an eclipse power sag. The operator drills in to tell them apart.

### 4.3 Alarm / event feed (region E)
Newest-first list, each line = `time · asset · physical reading · [status]` from
`telemetry.subsystem_log` + `political_consequence` + inject messages. Lines are **symptoms** (C1).
Clicking an alarm **deep-links**: selects the asset and opens the relevant subsystem graph in D.

---

## 5. Bus subsystem console (Workbench tab: "Bus")

The bus operator's deep surface. Six subsystem cards matching `bus.py`: **EPS, ADCS, Propulsion,
Thermal, C&DH, Comms** — plus a **Safe-mode/Recovery** strip when `mode==safe_mode`.

### 5.1 Subsystem card anatomy
Each card is a consistent widget:

```
┌ EPS — Electrical Power ──────────────── 🟡 ┐   header: subsystem + rollup status
│ Battery SoC     84%  ▁▂▃▄▅  [soft 30 hard 15]│   parameter rows: value · sparkline · limits
│ Bus voltage   28.0V  ▅▅▅▅▅                    │
│ Array current  8.0A  (eclipse: 0.1A)          │
│ ───────────────────────────────────────────  │
│ [Shed load] [Restore] [Charge mode▾] [Bus▾]   │   command buttons (PART 1 verbs, role-gated)
└───────────────────────────────────────────────┘
```

- **Parameter rows** read from `GET /telemetry/{cell}/{asset}` (current value + status + limits).
  Each row is clickable → opens the full **time-series graph** in the Telemetry tab (§5.3).
- **Sparkline** — a tiny inline 30-point series so trends are visible without leaving the card.
- **Limit chips** — soft/hard thresholds; the value colors against them (`status_low`/`status_high`).
- **Command buttons** — the PART 1 verbs for that subsystem, each following the button-logic contract
  (§12). Buttons that need a window show *Plan* (queue) by default; *Execute now* only if realtime.

### 5.2 The six bus cards (telemetry shown + buttons)

| Card | Parameters surfaced (from `telemetry.py`) | Buttons (verbs) |
|---|---|---|
| **EPS** | `battery_soc`, `bus_voltage_v`, `array_current_a`, eclipse flag | `eps.shed_load`, `eps.restore_load`, `eps.set_charge_mode`, `eps.select_bus` |
| **ADCS** | `attitude_error_deg`, `wheel_rpm`, pointing mode | `adcs.slew_to`, `adcs.set_mode`, `adcs.desaturate`, `adcs.point_payload` |
| **Propulsion** | `propellant_frac`, `tank_pressure_kpa`, Δv remaining/"years of life" | `prop.maneuver`, `prop.stationkeep`, `prop.collision_avoid`, `prop.cancel_burn` |
| **Thermal** | `payload_temp_c`, `optics_temp_c`, heater states | `tcs.set_heater`, `tcs.set_mode` |
| **C&DH** | `cpu_load_pct`, `fsw_error_count`, `cmd_reject_count`, `storage_frac`, `fsw_mode` | `cdh.set_time`, `cdh.load_stored_program`, `cdh.clear_stored_program`, `cdh.dump_storage`, `cdh.reset_subsystem`, `cdh.clear_fault` |
| **Comms** | `rx_power_dbm`, `cn0_dbhz`, `ber`, `uplink_lock`, `downlink_lock` | `comms.config_link`, `comms.point_antenna`, `comms.enable_isl`, `comms.set_crypto` |

### 5.3 Telemetry graph drill-down (Workbench tab: "Telemetry")
The troubleshooting heart. For any parameter: a line graph (`graph.js`) of the seeded series from
`GET /telemetry/{cell}/{asset}/{param}` with soft/hard limit lines and a status-colored trace, plus a
**parameter picker** grouped by subsystem and the **symptom log**. Controls:

- **Time window** — last 30 min / 1 h / since-start / custom (maps to `t0,t1`).
- **Overlay** — plot two parameters together (e.g. `rx_power_dbm` vs `cn0_dbhz`) to compare signatures.
- **Compare-to-nominal** — ghost a clean baseline so the deviation is obvious (helps trainees).

Because the series is **read-time, seeded, and replay-safe** (`telemetry.py`), the graph is identical
on every view and during AAR scrub — no new state.

### 5.4 Pass-gated telemetry semantics
Telemetry the *ground last received* (`bus_state.ground_view`) is shown with its **as-of timestamp**;
between contacts the cards show a **"stale since HH:MM"** banner and grey the values. The live
(truth) series is only available to White god-view; Red/Blue see the pass-gated snapshot — this is the
"you find out at the next pass" lesson and is the reason a safed satellite can be discovered late.

### 5.5 Safe-mode / recovery strip
When `bus_state.safe_mode.active`, a strip appears across the Bus tab showing the recovery checklist
(the ordered chain from `13` §1.7 / `recovery.py`): **establish contact → dump telemetry → clear fault
→ restore loads → set attitude → re-enable payload → verify**. Each step is a button that *plans* the
corresponding command to the next pass; completed steps check off; a blocked step shows
`blocked_reason` (e.g. "root cause persists: unpatched ground_modem") with a deep-link to the fix
(`def.patch_cyber`). Passes-used and re-safe events are shown inline. See §9.3.

---

## 6. Payload consoles by mission type (Workbench tab: "Payload")

One console per payload type. Each follows the same skeleton — **Status block · Monitors · Tasking/
controls · Product/queue** — but the content is mission-specific. All payload controls obey **C2**
(bus-gated). Verbs are PART 2 of the catalog.

### 6.1 SATCOM
- **Status:** transponder power/temp, link utilization, **interference level** (how jamming is
  *experienced* — not labeled as jamming).
- **Monitors:** carrier/interference telemetry, beam/coverage map, customer load per transponder.
- **Controls:** `satcom.set_transponder`, `satcom.set_frequency_plan`, `satcom.reconfigure_beam`
  (flexible payload only — button hidden otherwise), `satcom.shift_users`,
  `satcom.mitigate_interference`, `satcom.report_interference`.
- **Troubleshooting flow:** rising `interference_level` + comms `rx_power_dbm`↑/`cn0`↓ → operator
  *infers* jamming → `satcom.shift_users` / `mitigate_interference`; `report_interference` feeds
  geolocation. (GEO SATCOM is continuously in view → near-realtime controls.)

### 6.2 ISR — EO/IR and SAR
- **Status:** collection schedule vs. target windows, onboard `storage_frac`, downlink backlog,
  **last image quality**, sun-angle/weather (EO) — SAR is all-weather.
- **Monitors:** collection-vs-downlink split (the core ISR lesson), storage fill, image-quality
  readout (degradation from dazzle/weather shows here without a "dazzled" label).
- **Controls:** `isr.schedule_collection`, `isr.set_mode` (spot/strip/IR/SAR), `isr.collect_now`,
  `isr.prioritize_downlink`, `isr.downlink`, `isr.calibrate`, `isr.assess_quality`.
- **Tasking flow:** schedule target → engine queues collection to the target pass → collect fills
  storage → `prioritize_downlink` → `downlink` at a ground pass → product delivered. Storage full →
  `collect_now` disabled with "storage full — downlink first" (C2).

### 6.3 SIGINT / ELINT
- **Status:** intercept activity, receiver band/dwell, geolocation confidence, storage/backlog.
- **Monitors:** emitter list with geolocation-confidence ellipses (belief, not truth).
- **Controls:** `sigint.task_collection` (freq range/region), `sigint.set_band`, `sigint.geolocate`
  (needs multiple looks), `sigint.downlink`.
- **Tasking flow:** task a region/band → collect over the area → multiple looks shrink the geolocation
  ellipse → downlink the fix (e.g., locating a Red jammer to enable counter-fire). Product is a
  geolocation, delivered after downlink.

### 6.4 SDA / inspector (space-based surveillance)
- **Status:** sensor pointing, task capacity, per-object track quality/uncertainty.
- **Monitors:** the cell's **TrackCatalog** with confidence decay; the same belief stream the map/3D
  draw (`/scene`).
- **Controls:** `sda.task_search`, `sda.task_track`, `sda.task_characterize`, `sda.cue`,
  `sda.downlink`. (This is the tasking surface of §7.4 for a *space* sensor.)
- **Flow:** see §7.4 (shared tasking flow). Inspector at close range uses `sc.inspect` for high-quality
  characterization.

### 6.5 Space-control effector (counterspace)
The Red offensive payload console (also Blue if a vignette grants it). Effector resources + **uncertain
effect assessment** (you rarely get "kill confirmed").
- **Status:** effector charge/power/ammo, target track quality (the **weapons-quality gate**),
  engagement geometry/range, `last_effect_assessment` (unknown/likely/confirmed).
- **Controls (ROE- and gate-bound):** `sc.ew_jam`, `sc.ew_spoof`, `sc.de_dazzle`, `sc.rpo_approach`,
  `sc.rpo_station`, `sc.inspect`, `sc.engage_kinetic`, `sc.cyber_effect`.
- **Button logic highlights:**
  - `sc.engage_kinetic` → disabled unless **ROE kinetic_authorized** AND a **weapons-quality track**
    AND ammo ≥ 1; requires a **consequence confirm** ("debris-generating; political cost: HIGH") (P4,
    §12.3). Maps to engine `engage` (rejection reasons surface verbatim).
  - `sc.cyber_effect` → **not pass-gated**; needs an `access_vector` matching a target vulnerability;
    shows posture/patched state if known.
  - `sc.rpo_approach` → consumes Δv; shows the closing window and that the approach is **observable by
    the defender's SDA**.

### 6.6 PNT, Missile Warning, Weather (lighter consoles)
- **PNT:** signal-integrity/timing monitors + ground-monitoring status; `pnt.set_integrity`,
  `pnt.report_status`. The fight is at the user/ground level (jam/spoof), surfaced as a degraded
  user-bubble overlay.
- **Missile Warning:** continuous IR-staring health + **alert pipeline**; `mw.set_sensor_mode`,
  `mw.report_alerts`. Dazzle/cyber tamper shows as **degraded/altered alerts** (no "tampered" label).
- **Weather:** simple ISR-like schedule→downlink chain; `wx.schedule_collection`, `wx.downlink`.

### 6.7 Ground assets (no bus console)
Stations (passive — enable windows), jammers (`sc.ew_jam`/reposition), interceptors
(`sc.engage_kinetic`), cyber units (`sc.cyber_effect`), terrestrial forces (conceal/relocate). These
get an **action-only** console: a verb list + the relevant geometry (footprint/reach), no SOH cards.

---

## 7. Command composition & queue (Decision rail + Workbench "Queue")

### 7.1 The command-compose flow (button logic)
Select-then-act (P1/§4 of GUI principles):

1. **Select asset** (any surface) → Decision rail shows the **action menu**: only the verbs whose
   `command_db.roles` match the active role *and* whose `gates` can plausibly be met, each annotated
   with **cost** and **earliest execution window**. (Mirrors `OrderSystem` action set: `maneuver`,
   `downlink`, `observe`, `jam`, `engage`, `cyber`, …; the UI maps catalog verbs onto these.)
2. **Pick a verb** → a **parameter form** appears from the verb's `params_schema` (e.g.
   `prop.maneuver` → burn vector + execute-at; `sc.ew_jam` → target + outcome + success bias). The
   form pre-fills a sensible template (the client `PARAM_TEMPLATE` already does this per kind).
3. **Choose delivery** → the engine proposes the **earliest** of ground-uplink / ISL-relay / stored
   (it already picks earliest in `_issue_command`); the form shows the chosen path + window and lets
   the operator override to a specific future window on the ribbon (P-§4 plan-on-the-timeline).
4. **Plan** (primary) → posts `POST /order`; the order enters the queue as `queued` with its window
   and `delivery_path`. **Execute now** (secondary) only shown when a realtime/ISL/cyber path exists.
5. **Validation** → on reject, the form shows the reason inline (P4) and keeps the inputs for repair.

Irreversible/escalatory verbs add a **consequence confirm** step between 4 and the post (§12.3).

### 7.2 Command lifecycle (state machine)
```
DRAFT ──Plan──▶ QUEUED ──window arrives──▶ (engine re-validates) ──▶ EXECUTED
  │                │                                   │
  └─edit/clear     ├─Cancel──▶ CANCELLED               └─fail──▶ FAILED {reason}
                   └─(rewind/branch drops queued)
```
- **QUEUED** rows are **cancellable** (`POST /cancel`) — replay-safe (the engine skips a cancelled,
  not-yet-fired event so it never logs).
- **EXECUTED/FAILED** are read-only history; FAILED shows the execute-time reason ("lost window",
  "insufficient delta-v", "ROE changed").

### 7.3 Command queue panel (Workbench "Queue")
Columns: **actor · verb · target · delivery path · scheduled window (countdown) · status · [✕]**.
Filter by status; sort by window. The **[✕]** cancel button is present only on `queued` rows. The
panel reads `GET /orders/{cell}` (fog-filtered) and is the cell's editable plan (P5).

### 7.4 Tasking flow (SDA / sensor) — Decision rail "Tasking"
Tasking is *commanding a sensor* and shares the compose flow, with a tasking-specific form:

1. **Pick intent:** Search (draw/define a volume) · Track (an object) · Characterize (an object) · Cue
   (hand a track to another sensor). (`sda.task_*` / `sigint.task_collection`.)
2. **Pick sensor or `auto`:** the tool lists which of the cell's sensors can service it and **when**
   (next viable window, expected yield), and *why not* for the rest ("optical: target in daylight",
   "radar: below horizon until 21:10Z"). `auto` lets the engine pick the earliest viable, non-contended
   sensor (`_issue_collection` already does this).
3. **Priority:** routine / priority / immediate.
4. **Plan** → enters the **collection plan** (same queue, kind `collection`).
5. **On report:** the track's confidence rises and its **uncertainty volume visibly shrinks** on the
   map/3D (`/scene`), and characterization may flip "?"→classified — *which can unlock a
   previously-blocked engagement* (task → custody → unlock, the central loop).

**Contention** is shown explicitly: a sensor doing one thing at a time pushes an overlapping task to a
later window (the engine serializes it). The UI surfaces the trade ("tasking A drops custody of B
until 21:40Z") — a key teaching moment for the SDA-suppression objective.

---

## 8. User flow — Monitoring

The default loop a healthy-state operator runs continuously.

```
1. Scan FLEET RAIL rollup dots  ───────────────▶ all green? keep scanning / advance time
2. A dot goes 🟡/🔴 or ⚠ badge increments
3. Click the asset  → World view centers, ribbon loads its passes, Bus/Payload tabs populate
4. Read the asset rollup → which subsystem card is off-green?
5. Open that subsystem card → which parameter row is off-limit?
6. (optional) Click the row → Telemetry graph for trend + compare-to-nominal
7. Note next contact (ribbon/countdown) — when can I act?
8. Decide: plan a corrective command (→ §7) OR keep watching OR escalate to troubleshooting (§9)
```

Button logic at each step is **non-destructive** (reading never changes state). The flow is the
mission-control loop from `06` §3: *monitor SOH → drill → decide → plan in the window → review after*.

---

## 9. User flow — Troubleshooting & diagnosis

The console's distinctive value: it presents **symptoms** and supports inference, never the answer
(C1). Drives off the implemented attack signatures in `telemetry.py`.

### 9.1 Generic diagnosis flow
```
1. Symptom appears: payload stops producing / alarm fires / rollup red
2. Confirm scope: one parameter, one subsystem, one asset, or the fleet?
3. Open Telemetry graph for the off-nominal parameter(s); overlay related params
4. Match the SIGNATURE (the operator's mental model — also in the manual's clue table):
     • RX power↑ + C/N0↓ + BER↑ + lock intermittent ............ link interference (jam/spoof)
     • FSW error/cmd-reject counters climbing + CPU↑ + FSW=safe . command-path / cyber intrusion
     • Payload SNR↓ + optics temp↑ during a pass ............... directed-energy / dazzle
     • A closing track on the map/3D (not a bus signal) ........ RPO / co-orbital approach
     • Battery SoC↓ + bus voltage sag (in eclipse) ............. power / environmental
     • All telemetry ceases (LOS) .............................. kinetic kill / total loss
5. Cross-check with SDA: is there a track/closing object? Is the symptom pass-correlated?
6. Form a hypothesis → choose a mitigation (payload re-plan, posture, recover, or counter-task SDA)
7. Act (→ §7) and watch the parameter for recovery (signatures recede when the effect window ends)
```

The UI **assists** the inference without giving the verdict: compare-to-nominal ghosting, parameter
overlay, pass-correlation shading on the graph (shade the time spans when the asset was in a hostile
footprint per the belief map), and the symptom log. It must **not** print "jamming detected."

### 9.2 Attack-signature → operator-action reference
| Symptom cluster (telemetry) | Likely cause | Console action | Verb(s) |
|---|---|---|---|
| RX power↑, C/N0↓, BER↑, lock flaps | EW jam/spoof | shift users / anti-jam / hop; geolocate; report | `satcom.shift_users`, `satcom.mitigate_interference`, `def.frequency_hop`, `sigint.geolocate` |
| FSW errors↑, cmd-reject↑, CPU↑, FSW=safe | Cyber intrusion / forced safe | clear fault, reset FSW, **patch the vector**, recover | `cdh.clear_fault`, `cdh.reset_subsystem`, `def.patch_cyber`, recovery chain |
| Payload SNR↓, optics temp↑ on a pass | Directed energy / dazzle | re-point off threat; assess quality; maneuver | `adcs.slew_to`, `isr.assess_quality`, `def.maneuver_evade` |
| Closing track on belief view | RPO / co-orbital | characterize; evade; escort | `sda.task_characterize`, `def.maneuver_evade`, `def.escort_posture` |
| SoC↓ + voltage sag | Power/eclipse fault | shed loads; charge mode; check timeline | `eps.shed_load`, `eps.set_charge_mode` |
| Total LOS | Kinetic / catastrophic | confirm via SDA debris; (irrecoverable) | — |

### 9.3 Safe-mode recovery flow (the multi-pass mini-loop)
When a satellite safes, the **Recovery strip** (§5.5) guides the defender (`12-safe-mode-loop.md`):
```
1. Detect (indirect): payload stopped producing (symptom, immediate)
2. Confirm: stored-telemetry dump at next contact reveals SAFE_MODE + entered-at timestamp
3. Diagnose: fault vs attack, which subsystem (attack attribution is deliberately hard)
4. Recover (across passes): plan the ordered chain; each step checks off or fails/retries
5. Root cause: if it persists (e.g. unpatched modem) the sat is RE-SAFED → strip shows blocked_reason
   → fix the cause (def.patch_cyber / kill the jammer) → recovery sticks
6. Verify nominal → strip clears, payload re-enables
```
`safe_mode_recovery_difficulty` (quick/realistic/punishing) scales the pass count; the strip shows
**passes used** so the operator feels the tempo cost.

---

## 10. User flow — Tasking (recap as a flow)
```
1. Decide intent (search / track / characterize / cue) and the object/volume
2. Open Tasking rail → pick sensor or 'auto'; read each sensor's next window + why-not
3. Set priority; Plan → collection enters the queue
4. Advance to the collection window → report updates the TrackCatalog
5. Observe: confidence ↑, uncertainty volume ↓ on map/3D; "?"→classified on characterize
6. If a weapons-quality track results → the engage verb unlocks (gate satisfied)
7. Manage contention: if a higher-priority object needs the sensor, re-task and accept the custody trade
```

---

## 11. Per-cell operator consoles (all types covered)

The layout is shared; the inventory, verb sets, and emphasis differ. Below, every operator type per
cell, with its console focus.

### 11.1 Blue Cell (defensive)
| Operator | Assets | Console emphasis | Signature actions |
|---|---|---|---|
| **Bus/TT&C** | Blue satellites | Bus console, recovery strip, pass timeline | shed load, desaturate, station-keep, clear fault, patch cyber |
| **ISR payload** | EO/IR/SAR sats | collection plan, storage, downlink, quality | schedule/collect/prioritize/downlink, assess quality |
| **SATCOM payload** | GEO/LEO SATCOM | interference monitor, beam/freq plan | shift users, mitigate interference, reconfigure beam |
| **PNT/MW/Weather** | MEO/GEO/HEO | integrity/alert monitors | set integrity, report alerts/status |
| **SDA/tasking** | Blue sensors (ground/space) | TrackCatalog, tasking, custody | search/track/characterize/cue; sustain custody |
| **Defense** | any Blue asset | posture controls | threat-warning, harden, maneuver-evade, escort, frequency-hop, patch cyber, disperse |

### 11.2 Red Cell (offensive)
| Operator | Assets | Console emphasis | Signature actions |
|---|---|---|---|
| **Space-control effector** | jammers, dazzlers, RPO inspectors, cyber units, interceptors | target track quality, effect assessment, ROE | ew_jam/spoof, de_dazzle, rpo_approach/station, inspect, cyber_effect, engage_kinetic |
| **SDA/tasking** | Red radar/optical | find & track Blue assets to enable effects | search/track/characterize; cue effectors |
| **Bus/TT&C** | Red satellites (inspectors) | keep effectors healthy + maneuvering | maneuver, station-keep, desaturate |
| **Terrestrial** | surface group, mobile EW | concealment vs known passes | conceal, relocate, employ EW |

Red's console foregrounds the **weapons-quality gate** and **ROE** (most offensive buttons are disabled
until a track + authority exist) and the **uncertain effect assessment** (no clean kill confirmation).

### 11.3 White Cell (facilitator + driver)
- **God-view monitoring:** the Fleet rail shows *both* sides (ground truth); a **"see-as Red/Blue"**
  toggle renders that cell's fog-filtered console for adjudication.
- **Control panel** (separate rail): vignette dials (parameters), **time controls** (play/pause/ff/
  rewind/undo/branch), **inject menu** (dropdown of the vignette's injects), classification banner.
- **Driving a side:** White can adopt Red or Blue's console (the seat chip switches); permission/
  visibility logic is identical to a networked client (no engine change).
- **AAR:** the timeline **scrubber** (`/aar/at?seq=`) replays read-only to any decision; **branch
  compare** shows how a choice flipped objectives; **save/resume** persists the session.

---

## 12. Interaction grammar & button-state logic

The single contract every control obeys, so implementation is mechanical.

### 12.1 Control contract
```
control:        <verb or action>
visible_if:     role matches command_db.roles AND asset kind supports verb
enabled_if:     all gates plausibly satisfiable now-or-at-next-window
on_activate:    open params form → choose delivery → Plan (POST /order) | Execute now
result:         queued (with window+path) | rejected (reason shown inline)
disabled_tip:   the validator reason string (P4) — never a silent disabled control
```

### 12.2 Disabled-state reasons (authoritative strings)
Surface the engine's own reasons verbatim so UI and engine never drift:
`no_window`, `no_command_station`, `no_downlink_station`, `roe_kinetic_not_authorized`,
`roe_cyber_not_authorized`, `no_weapons_quality_track`, `no_ammo`, `insufficient_delta_v`,
`not_owner`, `no_such_asset`, `no_such_sensor`, `sensor_contended`. Each maps to a plain-language
tooltip (e.g. `no_weapons_quality_track` → "No weapons-quality track — task a sensor to characterize
the target first," with a **[Task sensor]** shortcut).

### 12.3 Consequence-confirm (irreversible/escalatory only)
`engage`/`sc.engage_kinetic`, any debris-generating or high-`escalation_weight` effect → a confirm
modal stating the consequence in doctrinal terms ("Debris-generating strike. Political cost: HIGH.
Debris may threaten your own LEO assets.") with **Confirm / Cancel**. Routine planning has **no**
confirm (P5, reduce friction).

### 12.4 Keyboard & accessibility
- `j/k` next/prev asset; `w` jump to next window; `c` compose; `t` task; `g` graph; `space` (White)
  pause/step. Tab order follows the region grid A→E.
- Not color-only: status carries shape/label too (●/▲/■ + text). High-contrast mode toggle. ARIA
  labels on every gauge/graph.

---

## 13. Widget library

Reusable components (build once, used across §4–§11):

| Widget | Inputs | States | Used by |
|---|---|---|---|
| **SOH dot** | subsystem statuses, mode | green/yellow/red | fleet rail, queue, AAR |
| **Resource gauge** | value, soft/hard, unit | nominal/warn/alarm | fleet rail, cards |
| **Parameter row** | value, status, limits, sparkline | green/yellow/red/stale/LOS | bus & payload cards |
| **Telemetry graph** | series, spec, overlays | trace colored by status; limit lines; ghost-nominal | Telemetry tab |
| **Pass-timeline ribbon** | windows per channel | lanes; countdown; selectable future windows | region C |
| **Track row / belief marker** | track | solid / aging-ellipse / ghost / "?" | track panel, map, 3D |
| **Command form** | verb params_schema | draft/valid/invalid; delivery chooser | decision rail |
| **Queue row** | order | queued(✕)/executed/failed/cancelled | queue tab |
| **Alarm line** | symptom record | severity color; deep-link | feed |
| **Recovery strip** | safe_mode + recovery state | step checklist; blocked reason | bus tab |
| **Seat chip** | cell, role | switcher | toolbar |

All consume existing JSON shapes (`CellView`, `SceneView`, telemetry DB/series, order list, alarms,
windows, AAR snapshot) — no new server models required beyond what exists.

---

## 14. Data / API binding (what each panel calls)

| Panel | Endpoint(s) | Cadence |
|---|---|---|
| Fleet rail / SOH | `GET /view/{cell}` (+ `/godview` for White), `/windows/{cell}/{asset}` | on tick + on action |
| World view (2D/3D) | `GET /scene/{cell}` | on tick |
| Pass-timeline ribbon | `GET /windows/{cell}/{asset}` | on select + horizon advance |
| Bus & payload cards | `GET /telemetry/{cell}/{asset}` | on tick |
| Telemetry graph | `GET /telemetry/{cell}/{asset}/{param}?t0&t1&n` | on open / window change |
| Command compose | `POST /order` (+ `/cancel`) | on action |
| Command queue | `GET /orders/{cell}` | on tick + on action |
| Tasking | `POST /order` (action=observe), `/windows`, `/scene` | on action |
| Alarm feed | `GET /alarms/{cell}` | on tick |
| Objectives/feed | `GET /objectives`, `/eventlog` | on tick |
| White control panel | `POST /param`, `/start`, time routes, `/inject`, `GET /injects` | on action |
| AAR | `GET /aar`, `/aar/at?seq=`, `/aar/objectives?seq=` | on scrub |
| Save/resume | `GET /save`, `POST /load_save` | on action |

**Push-readiness:** reads are keyed off the event-log sequence; when LAN multiplayer lands, the server
pushes view/scene/telemetry deltas over WebSocket (the contract already expresses this via
`get_eventlog(since_seq)`), and the console flips from polling to push with no UI change.

---

## 15. Wireframes (key screens)

### 15.1 Bus console (Blue ISR sat, jamming symptom present)
```
WORKBENCH › Bus                                              ISR-EO-1 · 🟡 · stale since 06:11Z
┌ EPS 🟢 ┐ ┌ ADCS 🟢 ┐ ┌ PROP 🟢 ┐ ┌ TCS 🟢 ┐ ┌ C&DH 🟢 ┐ ┌ COMMS 🟡 ───────────────┐
│ SoC 84%│ │ err .05°│ │ prop 62%│ │ pl 15C │ │ cpu 31% │ │ RX -67dBm  ▲ [soft -80] │
│ V 28.0 │ │ whl 2.0k│ │ p 1.5MPa│ │ op -10 │ │ err  0  │ │ C/N0 41 dB-Hz  ▼        │
│ I 8.0A │ │ mode nad│ │ Δv 41m/s│ │        │ │ stor 0.4│ │ BER 8e-3  ▲             │
│[Shed]… │ │[Slew]…  │ │[Burn]…  │ │[Htr]…  │ │[Dump]…  │ │ lock ⚠ intermittent      │
└────────┘ └─────────┘ └─────────┘ └────────┘ └─────────┘ │[Cfg][Antenna][ISL][Crypto]│
                                                          └───────────────────────────┘
PASS TIMELINE  |■■ uplink 06:18 ─────  □ downlink 06:41 ────────────── jam-footprint ▓▓▓ now |
```

### 15.2 Telemetry graph (diagnosis)
```
WORKBENCH › Telemetry      param: comms.rx_power_dbm   window: 1h   [overlay: cn0_dbhz] [ghost-nominal]
 -62 ┤        ╭─────────────╮                                  ── rx_power (RED while high)
     │ ──ghost nominal ~ -95 ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄            ┄┄ soft -80   ── hard -70
 -95 ┤────────╯             ╰────────────────────             shaded ▓ = in hostile footprint
     └───────────────────────────────────────────── t
 LOG: 06:20 comms.rx_power_dbm -67 dBm [RED] · cn0 41 [YELLOW] · ber 8e-3 [RED]
```

### 15.3 Command compose (kinetic, with gate + confirm)
```
DECISION › Compose — RED-ASAT (interceptor)
  Verb: engage ▾        Target: ISR-EO-1 (track: conf 0.91 ✓ characterized ✓ → weapons-quality ✓)
  Delivery: weapon-engagement window @ 06:24Z (ground)        ROE: kinetic AUTHORIZED ✓   Ammo: 1 ✓
  [ Plan ]   ⚠ Consequence: debris-generating; political cost HIGH; threatens own LEO.  → [Confirm]
```

### 15.4 Tasking rail
```
DECISION › Task sensor
  Intent: ( ) Search  (•) Characterize  ( ) Track  ( ) Cue        Object: RED-INSP
  Sensor:  (•) auto   ( ) BLUE-OPT  next 06:30Z yield: characterize   ( ) BLUE-RADAR  ✗ below horizon
  Priority: ( ) routine (•) priority ( ) immediate                 [ Plan collection ]
```

---

## 16. Implementation phasing

Layered so each phase is shippable and testable against the existing API:

1. **P-UI-1 Console frame** — region grid (A–E), seat chip, selection model, fleet rail with SOH dot +
   countdown, alarm feed. (Consumes `/view`, `/windows`, `/alarms`.)
2. **P-UI-2 Bus console** — six subsystem cards + parameter rows + sparklines; command buttons wired to
   `/order` with the button-state contract; disabled reasons.
3. **P-UI-3 Telemetry graphs** — graph tab with overlay/ghost-nominal/pass-correlation shading.
4. **P-UI-4 Payload consoles** — one component, mission-type content packs (SATCOM/ISR/SIGINT/SDA/
   space-control/PNT/MW/Weather).
5. **P-UI-5 Command queue + compose + consequence-confirm** — full lifecycle + cancel.
6. **P-UI-6 Tasking rail** — intent/sensor/priority + contention surfacing.
7. **P-UI-7 Recovery strip + White control panel + AAR scrubber polish.**
8. **P-UI-8 Accessibility & presentation mode; keyboard; multi-display reflow.**

Each phase is **backend-complete already** — these are front-end builds over existing endpoints.

## 17. Acceptance criteria (sample, per surface)
- **Monitoring:** a degrading subsystem turns the fleet dot yellow→red and an operator can reach the
  offending parameter graph in ≤ 3 clicks; stale telemetry is visibly marked with its as-of time.
- **Troubleshooting:** with a jam active, the comms graph shows the RX-power/C/N0/BER signature and the
  console **never names "jamming"**; the why-can't-I tooltips match engine reasons exactly.
- **Tasking:** a `characterize` task that yields a weapons-quality track visibly enables a previously
  disabled `engage` button (the same transition the engine enforces).
- **Command logic:** every disabled control shows a reason; `engage` requires the confirm; a queued
  order is cancellable and disappears from the plan without side effects.
- **Per-cell:** Red never sees a Blue asset in any panel; White can "see-as" either cell.

## 18. Open questions / future
- **Pass-plan builder:** a drag-to-sequence multi-command "pass plan" (chain with `depends_on`) — the
  queue already supports ordering; the builder is a richer compose mode.
- **Constellation aggregation (v2):** manage >3 sats as a group; current spec is per-asset.
- **Symbology pack:** finalize the APP-6-adapted space symbol set (shapes per object type).
- **Δv "years of life" economy panel** (`14-delta-v-economy.md`) as a dedicated propulsion sub-tab.
- **Coalition/shared SDA feed** rendering (lower-control external tracks).

## Appendix A — Payload console detail packs

Each pack is a **content pack** for the single payload-console component (§6 skeleton: *Status ·
Monitors · Controls · Product/queue*). An implementer instantiates the component with the pack's
fields. Buttons reference catalog verbs (`13-operator-command-catalog.md`); all are bus-gated (C2).

### A.1 SATCOM
- **Status block:** transponder power / temperature, link utilization %, `interference_level` (0–1).
- **Monitors:** carrier-vs-interference trend (graph), beam/coverage footprint, per-transponder load.
- **Controls:** `satcom.set_transponder` (power/gain), `satcom.set_frequency_plan`,
  `satcom.reconfigure_beam` *(flexible payload only — hidden otherwise)*, `satcom.shift_users`,
  `satcom.mitigate_interference` *(needs anti-jam capability)*, `satcom.report_interference`.
- **Product/queue:** none (continuous service); shows mitigation actions in the queue.
- **Troubleshoot micro-flow:** `interference_level`↑ & comms `rx_power`↑/`cn0`↓ → infer interference →
  `shift_users` to a clean transponder → `mitigate_interference` (hop/null) → `report_interference`
  to feed SIGINT geolocation. **Empty/edge:** flexible-beam controls hidden on fixed payloads.

### A.2 ISR — EO/IR
- **Status:** collection schedule vs. target windows, `storage_frac`, downlink backlog, last image
  quality, sun-angle/weather flag.
- **Monitors:** collection plan timeline, storage gauge, image-quality readout (dazzle/weather shows
  as degraded quality — unlabeled).
- **Controls:** `isr.schedule_collection`, `isr.set_mode` (spot/strip/IR), `isr.collect_now`
  *(over target + good attitude)*, `isr.prioritize_downlink`, `isr.downlink` *(downlink pass)*,
  `isr.calibrate`, `isr.assess_quality`.
- **Product/queue:** collection plan + downlink queue (re-orderable).
- **Troubleshoot:** quality drop during a pass → `assess_quality` → if pattern matches dazzle (SNR↓,
  optics temp↑ on the graph) → `adcs.slew_to` off the threat / `def.maneuver_evade`. Storage full →
  `collect_now` disabled ("storage full — downlink first").

### A.3 ISR — SAR
As EO/IR but **all-weather, day/night** (no sun-angle/weather gate); `isr.set_mode` offers SAR modes
(spot/stripmap/scan). Quality degradation is RF-domain (e.g., interference), not lighting.

### A.4 SIGINT / ELINT
- **Status:** intercept activity, receiver band/dwell, geolocation confidence, storage/backlog.
- **Monitors:** emitter list with geolocation-confidence ellipses (belief); spectrum-occupancy strip.
- **Controls:** `sigint.task_collection` (freq range/region), `sigint.set_band` (coverage vs.
  sensitivity), `sigint.geolocate` *(needs multiple looks)*, `sigint.downlink`.
- **Product/queue:** tasking plan; downlinked **emitter fixes**.
- **Troubleshoot/employ:** locate a Red jammer (multiple looks shrink the fix ellipse) → downlink →
  hand the fix to counter-fire. Few looks → "geolocation low confidence — task additional passes."

### A.5 SDA / inspector
- **Status:** sensor pointing, task capacity, per-object track quality/uncertainty.
- **Monitors:** TrackCatalog (shared belief stream `/scene`); uncertainty volumes on map/3D.
- **Controls:** `sda.task_search`, `sda.task_track`, `sda.task_characterize`, `sda.cue`,
  `sda.downlink`; close-range `sc.inspect` for an inspector.
- **Product/queue:** collection plan; track updates.
- **Flow:** §7.4 + §10 (task → custody → unlock). Contention shown explicitly.

### A.6 Space-control effector
- **Status:** effector charge/power/ammo, target track quality (weapons-quality gate), engagement
  geometry/range, `last_effect_assessment` (unknown/likely/confirmed).
- **Monitors:** target track (belief), footprint/reach overlay, ROE banner.
- **Controls:** `sc.ew_jam`, `sc.ew_spoof`, `sc.de_dazzle`, `sc.rpo_approach`, `sc.rpo_station`,
  `sc.inspect`, `sc.engage_kinetic` *(ROE + weapons-quality + ammo + confirm)*, `sc.cyber_effect`
  *(not pass-gated; access vector)*.
- **Product/queue:** active effects + their windows; effect-assessment readouts.
- **Edge:** most buttons disabled until a track + ROE exist (reasons shown); effect assessment stays
  "unknown" unless an SDA look confirms it (uncertain BDA).

### A.7 PNT
- **Status/Monitors:** signal-integrity & timing, ground-monitoring station status, user-bubble
  health overlay (where jam/spoof bites at the user level).
- **Controls:** `pnt.set_integrity`, `pnt.report_status`.
- **Troubleshoot:** denial is local/reversible at the user bubble; surfaced as a degraded-bubble map,
  not a satellite fault.

### A.8 Missile Warning
- **Status/Monitors:** IR-staring sensor health, **alert pipeline** integrity.
- **Controls:** `mw.set_sensor_mode`, `mw.report_alerts`.
- **Troubleshoot:** dazzle/cyber tamper appears as **degraded/altered alerts** — the operator must
  judge alert trustworthiness, not read a "tampered" flag.

### A.9 Weather / environmental
- **Status/Monitors:** sensing schedule, storage, product backlog.
- **Controls:** `wx.schedule_collection`, `wx.downlink` (simple ISR-like chain).

---

## Appendix B — Notification & feed taxonomy (region E)

The single feed shows four record kinds, visually distinct, all **symptom-level** (C1):

| Kind | Source | Style | Example |
|---|---|---|---|
| **Alarm** | telemetry limit crossing / safe-mode (`/alarms`) | red/amber, asset-tagged | `06:20 ISR-EO-1 comms.rx_power_dbm -67 dBm [RED]` |
| **Effect symptom** | perceived effect on own asset (`CellView.visible_effects`) | amber, "source unknown" unless overt | `SAT-7: deny (source unknown)` |
| **Intel / attribution** | attribution signal, SIGINT/SDA report | blue | `attribution signal on SAT-7 (confidence 0.5)` |
| **Inject / message** | White Cell inject (`messages`) | grey, italic | `OSINT leak: commercial SAR shows the surface group` |

Feed rules: newest first; click → deep-link (select asset + open relevant graph); a **filter chip row**
(Alarms / Effects / Intel / Injects); unread count on the region tab. Never a record that names an
attacker for the victim unless the effect's `attribution == overt`.

---

## Appendix C — Component UI states (loading / empty / error / stale)

Every data-bound widget defines four non-happy states so the build is complete:

| Widget | Loading | Empty | Error | Stale |
|---|---|---|---|---|
| Fleet rail | skeleton rows | "No assets for this cell" | "view unavailable — retry" | n/a |
| Telemetry graph | spinner in plot | "no series" | "telemetry unavailable" | grey trace + "as-of HH:MM" |
| Pass timeline | shimmer lanes | "no passes in 6 h" | — | n/a |
| Track panel | — | "no custody — task a sensor" + **[Task]** | — | aging ellipse / ghost |
| Command queue | — | "(empty)" | reject toast w/ reason | n/a |
| Alarm feed | — | "(no alarms)" | — | n/a |
| 3D globe / map | "loading map…" | own-assets only | falls back to 2D | n/a |

Bus/payload cards show **stale** prominently (pass-gated, §5.4): grey values + "stale since HH:MM"
banner, because acting on stale SOH is itself a teachable mistake.

---

## Appendix D — Additional wireframes

### D.1 Fleet rail (Blue, mixed health)
```
FLEET  [All|Bus-red|Payload|Under-attack|Safed]
🔴 SATCOM-1   GEO     ◷ live   ⚡95% 📡   ⚠3   safed
🟡 ISR-EO-1   LEO-SSO ◷ 04:12  ⚡84% ⛽62% 📡 ⚠2
🟢 GNSS-1     MEO     ◷ 22:40  ⚡95%        ⚠0
🟢 GS-NORTH   ground  (enables passes)
```

### D.2 SATCOM payload console (interference present)
```
WORKBENCH › Payload — SATCOM-1                                         🟡  ROE: cyber AUTHORIZED
 Transponders  [TP-1 ▓▓▓▓ 92%] [TP-2 ▓▓ 41%]      Interference level ▓▓▓▓▓▓▓ 0.7  ▲
 Beam: regional  Utilization 88%                  Carrier/Interference  graph ↗
 [Set transponder▾][Freq plan▾][Reconfigure beam][Shift users][Mitigate (hop/null)][Report interf.]
 Hint: interference high & carrier degraded — consider shifting users / anti-jam; report to geolocate.
```

### D.3 White Cell control panel
```
WHITE CONTROL                                            see-as: (•)White ( )Blue ( )Red
 Parameters: red_kinetic_authorized [off] safe_mode_susceptibility [fragile▾] fog_of_war [realistic▾]
 Time:  ⏸ ▶  ×60 ▾   [+1m][+10m][+1h]   ⟲ Rewind   ↶ Undo
 Injects: [commercial_imagery_leak ▾]  [Fire]
 Session: [Save] [Load]      AAR: [Open scrubber]
```

---

## 19. Glossary (console terms)
- **SOH rollup dot** — single worst-subsystem health indicator per asset.
- **Pass-gated telemetry** — values are the last *received* snapshot; stale between contacts.
- **Signature** — the telemetry pattern an attack produces; the operator's diagnostic clue (never a
  labeled verdict).
- **Weapons-quality track** — confident + characterized track that unlocks engagement.
- **Delivery path** — how a command reaches the asset: ground uplink / ISL relay / stored program.
- **Recovery strip** — the guided multi-pass safe-mode recovery checklist.
- **See-as** — White Cell rendering a player cell's fog-filtered console.
- **Compose / Plan / Execute now** — draft a command / queue it to a window / run it on an available
  realtime-or-ISL path.
