# GDS-08 — UI Architecture

> **Document ID:** GDS-08
> **Version:** 1.0
> **Status:** ✅ Authored — merge gate closed (see "Merge gate" below)
> **Dependencies:** GDS-07
> **Referenced By:** GDS-09
> **Produces:** GDS-09
> **Feature Mapping:** N/A — program-level
> **Related Topics:** [`design/09-gui-principles.md`](../design/09-gui-principles.md),
> [`design/05-cell-interfaces.md`](../design/05-cell-interfaces.md),
> [`design/10-sda-3d-viewer.md`](../design/10-sda-3d-viewer.md) (merge sources, superseded by this
> document); [`build-spec/07-operator-console.md`](../build-spec/07-operator-console.md) and
> [`design/06-white-cell-controls.md`](../design/06-white-cell-controls.md) (related legacy UI
> material, also absorbed); [GDS-01](01-concept-of-operations.md) (user classes),
> [GDS-06](06-non-functional-requirements.md) NFR-9 (usability constraints), ADR-0004, ADR-0005,
> ADR-0008, ADR-0016.

[↑ Architecture index](INDEX.md) · [Docs index](../INDEX.md)

## Purpose

How people use SpaceSim: who the screens are for, how the console is laid out, how a user moves
around it, and the workflows each seat runs. It sits between GDS-07 (what is stored) and GDS-09
(the service contract the screens call): this level names screens, panels and workflows and the
rules they follow, and leaves endpoints and payloads to GDS-09.

## Verification status (read first)

The browser client is **unverified end to end.** Every backend path a screen depends on
(endpoints, fog filtering, validation reasons, objectives, AAR, multiplayer clock and locking) is
covered by the pytest suite, but no automated test drives the browser and asserts what it shows.
`tools/record_walkthrough.py` and `tools/render_manual.py` drive a headless browser to produce the
manual's screenshots and walkthrough video; they assert nothing. So this document describes the
UI **as implemented** in `spacesim/ui_web/static/`, read from its source, and does not claim
behavior has been verified in a browser. Where it says a control "is disabled with the reason",
the backend half of that (the reason) is tested and the rendering half is not.

---

## 1. Users

From GDS-01, restated for the screens:

- **Red and Blue operators** are semi-technical space operators (CAF and allied, in a PME
  setting). They understand orbits, passes, SDA and counterspace; they are not software power
  users or astrodynamicists. They think in tasks and timelines ("get eyes on this object before the
  landing window"), work under time pressure and ambiguity, and expect military information density
  and doctrinal terms (custody, characterization, ROE). The tool does the math; they decide.
- Within a cell, three operator roles share one console: **bus/TT&C** (bus health and safety),
  **payload** (the mission payload) and **SDA/tasking** (the cell's sensors and track catalog). A
  role selector (All / Bus / Payload / SDA) filters the command menu, so one hot-seat person can
  switch focus without losing the picture.
- **White Cell** facilitates: sets up and starts sessions, controls time, fires injects, watches
  both cells and runs the after-action review.
- **Observer** is a read-only seat White Cell designates; it can watch but never command.

**North star:** an operator who knows the domain is productive in minutes without the manual and
is never surprised by why an action was or wasn't allowed.

## 2. Principles

These bind every screen. P1–P7 come from `design/09`, C1–C2 from the console specification, and the
human-factors constraints in GDS-06 NFR-9 apply on top.

- **P1 — Geometry is never hidden.** Every command is bound to a pass or window; next-contact
  countdowns and the pass-timeline ribbon are always visible, so the operator cannot forget that a
  satellite below the horizon cannot be commanded.
- **P2 — Plan first, not click to act.** The default is to plan an action for its next valid window
  (ADR-0005). Instant actions are the exception (ISL available, cyber, ground-segment actions).
- **P3 — Show belief, mark uncertainty.** A cell sees the world as its SDA believes it to be, never
  as ground truth. Every displayed object carries a visible confidence; stale tracks visibly decay;
  known, estimated and unknown are distinguishable at a glance.
- **P4 — Always answer "why can't I?"** An unavailable action says why, in operator language, before
  the click. No silent dead controls (§6).
- **P5 — Reversible for the trainee.** Planning is non-destructive and queued orders are
  cancellable; White Cell has true time travel.
- **P6 — One screen, three contexts.** The world view, the timeline and the decision panel are
  co-visible; modal dialogs are rare.
- **P7 — Doctrinal, consistent symbology.** Shapes, colors and labels mean the same thing in every
  view (§5).
- **C1 — Symptoms, not verdicts.** Telemetry, alarms and the recovery strip show physical readings
  only (RX power, FSW error count, optics temperature). The console never labels the cause; the
  operator diagnoses. A red health dot from jamming looks the same as one from an eclipse power sag.
- **C2 — The bus gates the payload, visibly.** When the bus blocks a payload action (safe mode,
  power red, storage full), the payload control is disabled with the bus reason, and the offending
  bus parameter is one click away.

**Anti-patterns** (each would destroy a lesson): a god view with perfect truth for a player cell;
instant execution that ignores passes; next-window information buried in a menu; asking the
operator for orbital-element math or frame choices; silent disabled controls; consumer-game styling.

## 3. Presentation architecture

- **A thin browser client over the session API** (ADR-0008): vanilla JavaScript, no framework, no
  external libraries or network dependencies at runtime, served by the FastAPI server. Every screen
  is a view of server responses; the client holds no authoritative state.
- **No fog-of-war logic in the client** (ADR-0004). The server filters every cell-scoped response at
  the `SessionAPI`/`CellController` boundary; the client renders what it receives verbatim. This is
  what makes "no cheating" structural, not cosmetic.
- **Render from custody, once.** The 2D belief map and the 3D globe draw from the same
  render-from-custody scene (`GET /scene/{cell}`), so the two views can never disagree about what a
  cell knows.
- **The server owns time** (ADR-0014, ADR-0016). The client polls; the server's lazy clock advances
  exactly once however many clients poll. Only White Cell can pause, resume, rewind or change the
  rate.
- **Modules** (`spacesim/ui_web/static/`): `app.js` (console, menus, panels' content, polling),
  `panels.js` (panel manager), `globe.js` (3D orthographic globe), `world.js` + `world.json`
  (shared coastline drawing for both viewers), `graph.js` (telemetry graphs and sparklines),
  `symbology.js` (affiliation and confidence symbols), `creator.js` (Vignette Creator),
  `ricview.js` (RIC-frame view), `tleexport.js` (TLE export), `index.html`, `style.css`.
- **Mutations carry the seat.** Every mutating call sends the caller's seat as a `cell` parameter;
  the server rejects any mutation that names the Observer seat (IP-1130). Cell selection is still
  client-side trust (GDS-06, NFR-5 trust boundary).

## 4. Screen architecture

One console page serves every seat. Its regions stay co-visible on one display by default:

| Region | Panels | What it shows |
|---|---|---|
| **Toolbar** (top) | Seat selector (White / Blue / Red / Observer), UTC and local clocks, White-only pause/resume and rewind, handover, Session / Creator / View / Settings / Help menus, classification banner | Who you are, what time it is, the controls for your seat. |
| **Brief** | Mission brief | The vignette's per-cell brief with live ROE, objective deadlines and countdown; opens on first load. |
| **Left rail** | Cell & Time; Fleet SOH rollup | Own assets: health dot (worst subsystem), next-contact countdown (amber under 5 min, red under 1 min), power gauge, bus mode, alarm badge; filter (all, bus red, payload degraded, under attack, safed). |
| **World view** (centre) | 3D globe; 2D belief map | The cell's belief picture (§5). |
| **Decision rail** | Tasking (sensor); Satellite command | Plan-first composition, preview, queue (§7). |
| **Timeline** | Activity timeline | Past, current and scheduled activity, fog-filtered: one lane for a player cell; Blue, Red and neutral lanes for White. |
| **Detail** | Subsystem drill-down | Per-subsystem cards for the selected asset (§7.3). |
| **White Cell** | Compare (truth beside each cell's picture, one instant), After-action review, Assessment | Facilitation and debrief, visible to White only. |

**One selection drives everything.** Selecting an asset in the rail, map, globe or ribbon updates
the decision rail, timeline and drill-down together.

**Panel manager** (`panels.js`). Each managed panel can be dragged out to float, resized, closed and
reopened (View → Panels), and the arrangement persists per browser. Floating a panel takes it out of
the grid so the rest reflow, which stops one tall panel from shoving the others around (GDS-06
NFR-9, panel-manager contract). **As built, the Compare and Assessment panels are not registered
with the panel manager** (see OQ2).

**Multiple screens.** View → Pop out opens a second window that joins the same session and shows
only the panels for one layout token (`globe`, `map`, `globe+map`, `fleet`, `order`, `aar`, or
`full`), via `?layout=…&cell=…#sess-N`. A facilitator can spread the globe, map, fleet, orders and
AAR across monitors; every window polls the same server clock.

## 5. The belief picture (2D map and 3D globe)

The viewers draw **only the viewing cell's belief**, never ground truth (absorbs `design/10` §1–§3):

- **Own assets** always appear at their known state, with orbit path, footprints and health badges:
  the cell commands them, so it knows where they are.
- **Other objects** appear only if the cell holds a track on them, and as that track says:
  - current, high confidence: solid marker, thin path;
  - aging: translucent marker inside an uncertainty volume that grows with time since observation;
  - propagated only: dashed ghost path and a large uncertainty volume;
  - detected but uncharacterized: hollow "?" marker.
- **Never drawn for a player cell:** objects it has not detected; true positions of objects it holds
  only stale tracks on; characterization it has not earned; the other cell's plans, queue or health.
- **Ground sites:** own stations and sensors with their current coverage.
- **Affiliation:** blue friendly, red hostile, yellow unknown or uncharacterized, green neutral,
  grey or hatched debris; also encoded by shape and label so color is never the only cue
  (`symbology.js`, an APP-6-adapted convention, not formal APP-6).
- **Time:** the picture moves with the sim clock; uncertainty volumes grow between observations and
  shrink when a tasked sensor reports. After a White Cell rewind the picture re-renders from belief
  at that time, exactly (determinism).
- **White Cell** sees ground truth by default and can view as either cell; the Compare panel shows
  truth beside each cell's picture at one instant.

The lesson the viewer exists to teach: an uncertainty volume blooming over a hostile track you
stopped watching, right before a decision window.

## 6. The button-state contract ("why can't I?")

Every command control follows one contract:

- **Visible if** the seated role matches the verb's role and the asset kind supports the verb.
- **Enabled if** the server's dry-run validation (`POST /order/validate`, backed by
  `OrderSystem.dry_run()`) returns ok. The dry run is read-only: it schedules, registers and books
  nothing, so the client can probe every candidate on every tick.
- **Disabled tip** is the validator's reason string mapped to plain language, for example "No command
  window for SAT-7 until 14:32Z", "Insufficient delta-v", "ROE does not authorize kinetic effects",
  "No custody — task a sensor first".
- **On activate:** open the parameter form, preview delivery path and window, then plan.
- **Result:** queued, with window and path; or rejected, with the reason inline.

**Consequence confirm.** Kinetic and cyber orders require an explicit acknowledgement that states
the consequence ("kinetic, debris-generating; political cost HIGH"). A live consequence preview
(severity, escalation weight, reversibility, debris risk, attribution, civilian risk) updates as the
operator edits; it is advisory, and ROE gating stays server-side. Routine planning asks for no
confirmation.

## 7. Workflows

### 7.1 Session setup (White Cell)

Session menu → pick a vignette (built-in or external directory), seed, optional classification
override → **Load** (refused with every validation problem listed if the vignette is invalid) →
assign seats to roles against the vignette's staffing requirements (an unmet mandatory role blocks
Start) → optionally designate the Observer → **Start** (paused). The URL becomes `…/#sess-N`; other
participants open it on their own machines and choose a seat.

### 7.2 Plan and command (Red, Blue)

Select an asset → the Satellite command panel lists only the verbs legal for it and the seated
role → choose a verb; the form pre-fills, and verb-specific assistants compute manoeuvre, jam,
engagement, cyber and SIGINT figures → the preview shows delivery path (ground uplink, ISL relay,
stored program) and scheduled window, or the reason it cannot be planned → **Issue** → the order
appears in the queue with its window and can be cancelled until it executes. Several assets can be
commanded in one batch.

### 7.3 Monitor health (Red, Blue)

Fleet rail → an amber or red dot → the Subsystem drill-down opens on that asset with one card per
subsystem (power, attitude, thermal, propulsion, C&DH, comms, payload). Each card shows parameter
chips with status color and a sparkline, plus the verbs for that subsystem. A chip opens a full
graph with a compare-to-nominal ghost (the clean baseline without attack terms), a second-parameter
overlay and shading for hostile-effect spans the cell can perceive. A **stale-telemetry banner**
("stale since HH:MM") rides each card between passes, so the operator knows they are acting on old
data. Alarms deep-link to the asset and parameter.

### 7.4 Recover from safe mode (Blue)

When the selected asset is safed, a recovery strip shows the defender's diagnosis (unknown until the
first confirmation pass), passes used against passes needed, and the recovery chain. **Begin
recovery** asks the server to pick an uplink station with a window. If an unpatched cyber
vulnerability exists, a **Patch** shortcut pre-fills `def.patch_cyber`; without it, recovery
re-safes, and the re-safe reason is shown verbatim.

### 7.5 Task a sensor (Red, Blue)

Tasking panel → intent (search, track, characterize, cue), sensor (auto or a named own sensor),
target, priority → plan. "Auto" lets the engine pick the earliest viable, uncontended sensor. SSN
requests (a separate surveillance network) are planned and cancelled from the same panel. Learning
about an object always means tasking and waiting for the collection window; there is no "click the
enemy satellite and read its truth".

### 7.6 Facilitate (White Cell)

- **Time:** pause and resume for everyone; rewind; undo; the clock advances only through White Cell
  and logs every control.
- **Injects:** fire a vignette inject, or build one from the inject library (template → JSON editor →
  now, +seconds or absolute UTC → schedule). Pending injects can be edited or cancelled before they
  fire.
- **Rules of engagement and gating:** change a cell's ROE flag live; approve or reject an order held
  for authorization.
- **Watch:** god view; view as either cell; the Compare panel (truth beside both pictures at one
  instant); objectives; coaching notes; conjunction screening.
- **Save:** download a save file; load one to resume; save the current state as a new scenario.

### 7.7 After-action review (White Cell)

The AAR panel scrubs the exercise read-only, from truth or from one cell's viewpoint, at variable
speed, without disturbing the live session; branch comparison and the assessment rubric sit
alongside. Exports (timeline CSV, telemetry, ephemeris, manoeuvre ledger, TLE) are available from
the relevant panels (GDS-07 §7).

### 7.8 Author a vignette (White Cell)

Creator menu → a draft session that never advances its clock → add orbital assets by TLE and ground
assets by latitude and longitude (or a curated site) → edit the synchronized JSON view → preview the
initial state in 2D and 3D from ground truth → declare seats and roles → save to the configured
user-save directory.

### 7.9 Hot-seat handover

On one machine, the handover control blanks the screen to a pending-handoff menu between role
changes, so the next person does not see the previous cell's picture.

## 8. Navigation and accessibility

- **Menus:** Session (vignette, load, start, save-as-scenario, observer, seats and roles), Creator,
  View (display mode, briefing and tutorial, panels, RIC frame view, TLE export, pop-out), Settings
  (save, load, coaching, inspect vignette), Help.
- **Command palette** (Ctrl-K / ⌘K): a fuzzy menu over assets, time advances, seats, injects,
  inject-library templates and display toggles.
- **Keyboard:** `j`/`k` cycle the selected asset, `c` focuses composition, `g` opens the drill-down;
  ignored while a text field has focus.
- **Display modes:** presentation mode (larger, high contrast, for projectors), colorblind-safe
  palette (Okabe-Ito), high contrast, large text; each persists per browser.
- **Time display:** a canonical UTC clock plus a selectable local-time row (client-side only).
- **Latency:** in LAN play the client stays responsive while awaiting the server, and a stale-network
  indicator shows when polling falls behind.

---

## Departures from the legacy text

The GDS level is authoritative; these are stated so they are not mistaken for drift:

- **Branches, jump-to-event and commit locks** (`design/06` §2): rewind and undo exist; named
  what-if branches the facilitator switches between, and "lock a point against rewind", were not
  built. AAR branch comparison exists as a read-only report.
- **Save contents** (`design/06` §5): a save stores the event-log envelope described in GDS-07 §6,
  not `{initial_state, seed, snapshots, eventlog, branches}`.
- **Inject effect names** (`design/06` §3): the shipped set is GDS-05's (`message`, `reveal_asset`,
  `political_consequence`, `patch_cyber_vuln`, `gs_outage`, `space_weather`, `conjunction_warning`,
  `spawn_debris`, `anomaly`, `sensor_outage`, `forced_custody_loss`, `scripted_manoeuvre`), not
  `design/06`'s list.
- **Timeline drag-and-drop planning** (`design/09` §4) and **right-click "task sensor on this
  object"** (`design/10` §5) were not built; planning starts from the command and tasking panels.
- **Optimistic "queued (pending)" states** (`design/09` §5): the client waits for the server
  response rather than rendering an optimistic state.
- **Detach viewers** (`build-spec/07` §16.12) became the pop-out layout tokens in §4.
- **Single-player cell switching** (`design/05`): the seat selector is the same, but it now also
  serves LAN multiplayer and the Observer seat.

## Open Questions

- **OQ1 — No automated UI verification.** The client is unverified end to end. Should a browser test
  (the walkthrough tool's headless browser already exists) assert the load-bearing UI rules — no
  ground truth in a player cell's views, the disabled-with-reason contract, consequence confirm — or
  does backend coverage stay the accepted bar for v1? Owner decision; it sets how much of this
  document can ever be called verified.
- **OQ2 — Compare and Assessment panels are outside the panel manager.** Both White-only panels are
  missing from `panels.js`'s registry, so they cannot be floated, resized, closed or reopened like
  every other panel — contrary to the panel-manager contract (GDS-06 NFR-9). A small UI fix.
- **OQ3 — APP-6 conformance.** Symbology is APP-6-adapted, not conformant. Is a conformant symbol
  pack wanted (it is listed as future work), or is the adapted convention the intended standard?

## Merge gate (closed)

- [x] **Absorbed `design/09-gui-principles.md`**: §1 → §1; §2 (P1–P7) → §2; §3 (visual language) →
  §5; §4 (interaction patterns) → §6–§7; §5 (accessibility and deployment) → §8 and §4 (pop-outs);
  §6 (anti-patterns) → §2; §7 (build-phase mapping) dropped as history.
- [x] **Absorbed `design/05-cell-interfaces.md`**: shared UX elements → §4 and §7; permitted actions
  by asset kind and the validation steps → §6–§7 (the per-verb list itself is GDS-05 and the command
  catalog's, not repeated); fog of war and attribution → §5; White Cell view → §7.6; single-player
  switching → §3–§4 and departures.
- [x] **Absorbed `design/10-sda-3d-viewer.md`**: §1–§3 → §5; §4 (time) → §5; §5 (interaction) → §5
  and departures; §6 (fidelity now vs. later) is GDS-04/GDS-06 material and is not repeated; §7
  (tech notes) → §3; §8 → §5.
- [x] **Also absorbed the related legacy UI text** the merge sources point to: `build-spec/07`
  §16.1–§16.14 (users, C1–C2, screen architecture, fleet rail, drill-down, compose, recovery,
  per-cell consoles, button-state contract, accessibility, inject builder, activity timeline,
  conjunctions and coaching) into §1–§8; its per-panel endpoint table goes to GDS-09; its verb
  catalog stays with `design/13` and the code. `design/06` §2–§5 → §7.6 and departures.
- [x] **Did not claim verified UI behavior.** "Verification status" states the client is unverified
  end to end and why; OQ1 asks whether that should change.
- [x] **DOM content (`BL-0293`).** DOM-007 was already absorbed into GDS-06 NFR-9, which this
  document applies rather than restates (§2, §4). No other DOM section has UI content.
- [x] **Decision recorded:** **this document is the authoritative UI architecture.**
  `design/09`, `design/05` and `design/10` are superseded in full, and `build-spec/07` and
  `design/06` are superseded for their UI content. None is edited here; they retire with build-spec
  and the rest of `docs/design/` (apart from the ICD) once GDS-10 closes (`BL-0292`).

## Next

`GDS-09` (API Specification) may now begin; it takes this document's screen-to-endpoint binding.
OQ1 and OQ3 need owner decisions; OQ2 is a UI defect for `07`.
