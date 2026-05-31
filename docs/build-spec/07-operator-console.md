[← Build Spec index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 16. Operator console (UI specification) — v1 implemented

This section is the **authoritative v1 UI specification**. It consolidates the previously
separate `docs/OPERATOR-UI-DESIGN.md` (now retired) for everything the v1 console actually does;
future enhancements live in `docs/FUTURE-WORK.md`. The companion docs
`09-gui-principles.md`, `05-cell-interfaces.md`, `06-bus-and-payload-operations.md`,
`10-sda-3d-viewer.md`, `11-command-planning-and-tasking.md`, `12-safe-mode-loop.md`,
and `13-operator-command-catalog.md` provide the underlying research and verb catalog; this
section binds them to the implementation.

### 16.1 Users and operator types

The operating cells (Red/Blue) are semi-technical CAF / allied space operators. The console
preserves orbital reality (does not hide passes, custody, or ROE) and refuses to invent
information; the operator decides. Three operator archetypes share a single console layout,
with a **role selector** (All / Bus / Payload / SDA) filtering the command menu so a single
hot-seat human can switch focus without losing situational awareness (OR-2):

| Operator type | Owns | Primary surfaces | Verbs (`VERB_ROLE`) |
|---|---|---|---|
| **Bus / TT&C** | spacecraft bus health & safety | Fleet rollup, Bus subsystem cards, queue | `eps.*`, `adcs.*`, `tcs.*`, `cdh.*`, `comms.*`, `prop.*`, `maneuver`, `downlink` |
| **Payload operator** | the mission payload | Payload card in the drill-down, tasking rail | `satcom.*`, `isr.*`, `sigint.*`, `wx.*`, `def.harden` |
| **SDA / tasking** | the cell's sensors & TrackCatalog | TrackCatalog, tasking rail | `observe` (with `intent` and `priority`) |

White Cell uses the same console with **god-view** rendered via the cells switcher and has access
to the time/inject/save/load controls.

### 16.2 Design principles

Inherits P1–P7 from `09-gui-principles.md`, plus two console-specific principles:

- **C1 — Symptoms, not verdicts.** The drill-down's telemetry, alarms, and recovery strip show
  physical readings only (RX power, FSW error count, optics temperature). The console **never**
  labels the cause; the operator diagnoses. This is enforced at the engine layer
  (`engine/telemetry.py`) and preserved in every UI label.
- **C2 — The bus gates the payload, visibly.** When the bus blocks a payload action
  (safe mode, power-red, full storage), the payload control is pre-disabled with the **bus**
  reason from the order validator (`payload_unavailable`, `cannot_collect`, …), and the offending
  bus parameter is one click away in the drill-down.

P1 (geometry never hidden) → fleet-rail next-contact countdown + pass-timeline ribbon;
P2 (plan-first) → every command form previews its scheduled window;
P3 (show belief, mark uncertainty) → tracks with confidence decay, the stale-telemetry banner;
P4 (always answer "why can't I?") → the dry-run / validate endpoint pre-disables controls with
the engine's own reason string (§16.9);
P5 (reversible for the trainee) → queued orders are cancellable;
P6 (one screen, three contexts) → map/3D, timeline, decision panel co-visible;
P7 (doctrinal symbology) → APP-6-style affiliation + confidence encoding consistent across the
2D map and 3D globe.

### 16.3 Screen architecture

Region grid kept co-visible (single display by default; second display via **Detach viewers**):

```
┌───────────────────────────────────────────────────────────────────────────────┐
│ TOOLBAR  vignette · cell · sim-clock · step/rewind · save/load · present · detach │ A
├──────────────┬───────────────────────────────────────┬────────────────────────┤
│ FLEET RAIL   │ WORLD VIEW (3D globe + 2D belief map) │ DECISION RAIL          │ B
│ SOH, next-   │ render-from-custody; coastlines+      │ tasking · command     │
│ contact, ⚠   │ borders; tracks as uncertainty        │ compose · queue       │
├──────────────┴───────────────────────────────────────┴────────────────────────┤
│ PASS-TIMELINE RIBBON (selected asset) — uplink/downlink lanes                  │ C
├───────────────────────────────────────────────────────────────────────────────┤
│ SUBSYSTEM DRILL-DOWN  power · attitude · thermal · propulsion · cdh · comms · │ D
│   payload — each card: param chips + sparkline + verb buttons + graph         │
├───────────────────────────────────────────────────────────────────────────────┤
│ AAR SCRUBBER + ALARM/EVENT/MESSAGE FEED                                        │ E
└───────────────────────────────────────────────────────────────────────────────┘
```

Selecting an asset (in the rail, the map, the 3D globe, or the ribbon) drives B-centre, C, and
D as a single source of truth. A high-contrast **presentation mode** (toolbar toggle, body
class `.present`) is provided for projector / PME use.

### 16.4 Fleet rail and SOH rollup

One row per own asset (godview for White). Columns: SOH dot · ID · Kind · Next-contact countdown
· Power gauge · Bus mode · Alarm badge. The countdown is fed by `GET /next_contacts/{cell}`
(which reuses the pass-timeline window search) and colours amber < 5 min, red < 1 min. The SOH
dot is `worst-subsystem` (`engine/bus.overall_status`); the alarm badge counts off-nominal
parameters and safe-mode entries for that asset from `/alarms`.

The dot is **not** an attack indicator (C1): a red dot from jamming-driven RX power looks
identical to a red dot from an eclipse power sag. The operator drills in to tell them apart.

A **filter bar** narrows the rail: All / Bus-red / Payload-degraded / Under-attack / Safed.
Clicking an alarm line in the feed deep-links to that asset's drill-down with the relevant
parameter graph.

### 16.5 Subsystem drill-down (bus + payload console)

The drill-down opens on any selected asset and is laid out as **subsystem cards** keyed by the
telemetry sampler's subsystem keys (`power`, `attitude`, `thermal`, `propulsion`, `cdh`,
`comms`, `payload`). Each card carries:

- **Parameter chips** for that subsystem from `GET /telemetry/{cell}/{asset}` — value, status
  colour (green/yellow/red/los), and an inline **sparkline** (`Graph.spark`, 30-sample series).
- **Command-verb buttons** for the verbs whose `VERB_SUBSYSTEM` matches the card. Clicking a verb
  loads it into the compose form and runs the dry-run preview/pre-disable.
- A click on any chip opens its **full telemetry graph** below, with:
  - **Compare-to-nominal** ghost (toggle) — overlays the seeded clean baseline with no attack
    term (`telemetry.sample(..., nominal=True)`), so a jam/cyber/DE signature reads as the gap
    between the two lines.
  - **Two-parameter overlay** (selector) — normalised second trace from another parameter of
    the same asset for shape comparison.
  - **Pass-correlation shading** — hostile-effect time spans (`CellView.effect_windows`, fog-
    respecting) shaded behind the trace.

A **stale-telemetry banner** ("stale since HH:MM (Nm)" or "as-of HH:MM:SS") rides the card title
based on `bus_state.last_telemetry_time`, so an out-of-contact operator sees they're acting on
old data — the "you find out at the next pass" lesson.

When the asset is in **safe mode**, a **recovery strip** appears across the drill-down (§16.7).

### 16.6 Command composition, queue, and consequence-confirm

The compose flow is **plan-first**: pick a verb, the form pre-fills from `PARAM_TEMPLATE`, and
the dry-run preview shows the chosen delivery path + scheduled window — or the engine's reason
for refusing. The **Issue order** button is pre-disabled and its tooltip carries the reason.

The **queue panel** lists order status (`queued` / `executed` / `cancelled` / `failed (reason)`)
from `GET /orders/{cell}` and exposes a one-click cancel for queued rows (`POST /cancel`,
replay-safe — the Scheduler skips a cancelled, not-yet-fired event so it never logs).

**Consequence-confirm** fires for verbs whose entry exists in the client's `CONSEQUENCE` map —
currently `engage` ("kinetic, debris-generating; political cost HIGH") and `cyber` ("covert
but escalatory; ROE-gated; re-safe risk"). The form refuses to post without an explicit
acknowledgement.

**Live consequence preview** (FW §11.D.18, shipped). A second `#consequence-preview` line lives
under the validity preview and updates as the operator types. It calls
`POST /preview/consequence` with the full Order body and returns
`{severity, escalation_w, reversible, debris_risk, attribution, civilian_risk, notes}`. The
client styles the line by severity (`low` muted, `medium` yellow, `high` red); civilian-target
denial automatically bumps severity by one tier. The preview is advisory — final ROE gating
remains server-side.

#### 16.6.1 Verb-specific composition assistants (FW §11.A — shipped)

For complex verbs the compose form switches in a mode-specific assistant with a live preview
*before* the order is queued. All previews are read-only — they call a `/compute` endpoint on the
session API, never mutate state, and pre-fill `o-params` only when the operator clicks **Issue**.

- **`maneuver`** — six entry modes (ECI / LVLH / finite_burn / target_coe / hohmann /
  plane_change) backed by `engine/maneuver.py`. The preview returns
  `{dv, cost, new_orbit, second_burn?, duration_s?}`; the UI shows Δv, the new-orbit elements,
  and the second-burn line where Hohmann applies.
- **`observe`** (ISR) — beam-mode picker for EO/SAR/SDA with a 0–45° look-angle slider and a
  per-pass duration. Backed by `engine/isr.py` (`BEAM_MODES` table). Effective gain =
  `base × gain_factor × cos(look)`; SoC drain = `power_factor × duration / 300 s`. A
  4-corner footprint polygon stores on the resulting `Track.last_footprint` and renders dashed
  teal on the 2-D map after the collection window fires.
- **`jam`** — modulation × power × bandwidth picker backed by `engine/jam.py`. Posts to
  `POST /jam/compute` for a live `{modulation, power_w, effective_radius_km, footprint_polygon,
  success_prob, detectability, attribution_default, power_draw_w, center}` preview; the orange
  dashed footprint renders on the 2-D map until the operator changes action.
- **`engage`** — `POST /engage/compute` returns `{closing_geometry, salvo_n, interceptor_dv_ms,
  kill_probability, debris}`. Operator picks salvo and interceptor Δv.
- **`cyber`** — `POST /cyber/compute` returns `{vector, payload, target_posture, success_prob,
  detect_prob, attribution_default, reversible, escalation_weight, intended_outcome, patchable,
  min_persistence_h}` derived from `engine/cyber.py`'s `VECTORS × PAYLOADS` database.
- **`sigint`** — `POST /sigint/compute` returns expected geolocation error scaling by
  `√dwell × √N collectors × atmospheric loss`.

#### 16.6.2 Multi-asset batch (FW §11.C.13 — shipped)

The `#batch-bar` carries the legacy shift-click batch (asset rows toggle into the batch set) plus
four fleet-subset helpers: **All own**, **ISR sats**, **SATCOM**, **Same group**. Each
predicate-fills the batch from `ASSETS` filtered by `owner == active cell` and the helper's
condition (`payload startswith "isr"`, `payload == "satcom"`, or `group ==` the actor's group).
The existing **Issue to all** path then posts the current compose body once per batched asset.

### 16.7 Tasking rail and safe-mode recovery strip

The **tasking rail** is its own panel with `Intent` (Search / Track / Characterize / Cue) +
`Sensor` (auto, or a specific own sensor) + `Target` + `Priority`. The plan posts to `/order`
with `action: observe`; the engine's auto-select + contention handling
(`OrderSystem._plan_collection`) drives the result. Sensor "auto" lets the engine pick the
earliest viable, non-contended own sensor.

The **safe-mode recovery strip** appears in the drill-down when the selected asset's bus is
safed. It shows:

- The diagnosis (`safe_mode.defender_diagnosis`) — initially `unknown`; flips to
  `suspected_attack` / `fault` / specific subsystem after the first confirmation pass.
- Passes used / passes needed (`RecoverySystem.passes_needed`, scaled by the
  `safe_mode_recovery_difficulty` param).
- The ordered chain `establish_contact → dump_telemetry → clear_fault → restore_loads →
  set_attitude → enable_payload → verify_nominal` as informational steps.
- A **Begin recovery** button that calls `POST /recovery/{cell}/{asset}` — the manager
  auto-selects an own uplink station with a window (UI does not guess `via`).
- A **Patch (def.patch_cyber)** deep-link when the asset has an unpatched cyber vulnerability,
  pre-filled with the first unpatched vector — closes the recovery loop (without the patch,
  recovery re-safes; with it, recovery sticks).
- The `blocked_reason` from a re-safe is shown verbatim with the "remove the root cause" hint.

The recovery chain runs as logged events (`recovery_confirm` and `recovery_finish` handlers),
so the whole flow is deterministic and `Simulation.replay()` reproduces it byte-identical.

### 16.8 Per-cell consoles

Layout is identical across cells; inventory and verb sets differ.

**Blue Cell (defensive)** foregrounds the bus card stack, the recovery strip, anti-jam payload
verbs, and the tasking rail for custody. Signature actions: shed-load, set-charge-mode, slew,
mitigate-interference, schedule-collection, patch-cyber, frequency-hop, harden.

**Red Cell (offensive)** foregrounds the weapons-quality gate (the engage verb is disabled
until a characterised track exists), ROE banner, and the uncertain effect-assessment readout.
Signature actions: `cyber` (with the consequence-confirm), `jam`, `engage` (kinetic;
confirm-gated), `observe` to find/characterise Blue targets, RPO via `maneuver`.

**White Cell** uses god-view for monitoring and the toolbar's time / inject / save / load
controls, plus the AAR scrubber for read-only timeline scrubbing. Switching to Blue or Red
renders that cell's fog-filtered console (effectively "see-as").

### 16.9 Button-state contract (P4 — "why can't I?")

Every control follows a uniform contract:

```
visible_if:   role matches command_db.roles AND asset kind supports verb
enabled_if:   POST /order/validate returns ok (and any client-side guard passes)
on_activate:  open params form → choose delivery → Plan (POST /order)
disabled_tip: the validator's reason string, plain-language via REASON_TIPS
result:       queued (with window+path) | rejected (reason shown inline)
```

The dry-run validate path (`OrderSystem.dry_run` → `SessionManager.validate_order` →
`POST /order/validate`) is the read-only mirror of `/order`: it computes the verdict + window
+ delivery path **without** scheduling, registering, booking, or mutating any session state, so
the UI can probe every candidate on every tick without polluting the queue. This is the
mechanism for P4.

The validator's authoritative reason strings (surfaced verbatim, mapped to plain-language
tooltips in `REASON_TIPS`):

```
no_window               no_command_station       no_downlink_station
roe_kinetic_not_authorized                       roe_cyber_not_authorized
no_weapons_quality_track                         no_ammo
insufficient_delta_v                             not_owner
no_such_asset           no_such_sensor           sensor_contended
unknown_command         no_payload_for_verb      payload_unavailable
```

**Keyboard shortcuts** (ignored while a text field/select is focused): `j` / `k` cycle the
selected actor, `c` focuses compose, `g` opens the asset's drill-down.

### 16.10 Catalog verbs implemented (engine `command` action)

The order system's new `command` action carries a `verb` payload (uplink/stored delivery, same
path as `maneuver`); the handler dispatches to `buscommands.apply_command`, which mutates the
asset's `BusState` / `PayloadState` / `cyber_vulnerabilities` inside the deterministic event
loop (replay-safe, observable in SOH/telemetry).

| Verb | Effect (observable via) | Plan-time gates |
|---|---|---|
| `eps.shed_load` / `eps.restore_load` | `power.loads_shed` ⇒ eclipse drain ×0.4 (SoC sag rate) | bus present |
| `eps.set_charge_mode` | `power.charge_mode` ⇒ sunlit charge ×1.5/0.5 (`fast`/`trickle`) | bus present |
| `adcs.set_mode` | `attitude.mode` (SOH card) | bus present |
| `tcs.set_mode` / `tcs.set_heater` | `thermal.mode` / `thermal.heater_on` | bus present |
| `cdh.dump_storage` | `refresh_ground_view` ⇒ fresh SOH snapshot | bus present |
| `cdh.clear_fault` | `cdh.fsw_mode = nominal` (does not exit safe mode by itself) | bus present |
| `comms.enable_isl` | `comms.isl_enabled` | bus present |
| `comms.config_link` | `comms.data_rate_kbps` (clamped 64..16384) | bus present |
| `satcom.mitigate_interference` / `satcom.shift_users` | `payload.interference_mitigation` ⇒ jam terms ×(1 − mit) in telemetry | payload type `satcom` + payload available |
| `isr.collect_now` / `isr.schedule_collection` | `payload.collecting` ⇒ `storage_frac` fills | payload type `isr_eo`/`isr_sar` + `can_collect` |
| `sigint.task_collection` | `payload.collecting` | payload type `sigint` |
| `wx.schedule_collection` | `payload.collecting` | payload type `weather` + `can_collect` |
| `def.patch_cyber` | sets `cyber_vulnerabilities[vector].patched = True` ⇒ recovery sticks | bus present |
| `def.frequency_hop` | `comms.freq_hopping` ⇒ jam terms ×(1 − mit) (defensive parity) | bus present |
| `def.harden` | `payload.hardened` | payload present |
| `def.set_threat_warning` | `asset.threat_warning` | — |

Every verb is regression-tested in `spacesim/tests/test_bus_commands.py` (mutation observable +
replay-identical). Verbs not listed here either remain on their existing core actions
(`jam`/`engage`/`cyber`/`observe`/`maneuver`/`downlink`) or are catalogued in
`docs/FUTURE-WORK.md` §3 for future engine work.

### 16.11 Data / API binding

| Panel | Endpoint(s) | Cadence |
|---|---|---|
| Fleet rail / SOH | `GET /view/{cell}` (+ `/godview` for White), `/next_contacts/{cell}`, `/windows/{cell}/{asset}` | on tick + on action |
| World view (2D/3D) | `GET /scene/{cell}` | on tick |
| Pass-timeline ribbon | `GET /windows/{cell}/{asset}` | on select + horizon advance |
| Bus & payload cards | `GET /telemetry/{cell}/{asset}` | on tick |
| Telemetry graph (+ ghost, overlay) | `GET /telemetry/{cell}/{asset}/{param}?t0&t1&n` (+`&nominal=1`) | on open / window / toggle |
| Command compose (preview + issue + cancel) | `POST /order/validate`, `POST /order`, `POST /cancel` | on edit / on action |
| Command queue | `GET /orders/{cell}` | on tick + on action |
| Tasking rail (Organic) | `POST /order` (action=`observe`) | on action |
| Tasking rail (SSN) | `POST /ssn/{cell}/request`, `GET /ssn/{cell}/requests`, `POST /ssn/{cell}/cancel`, `GET /ssn/{cell}/coverage?regime=` | on edit / on tick / on action |
| Alarm feed | `GET /alarms/{cell}` | on tick |
| Recovery strip | `GET /recovery/{cell}/{asset}`, `POST /recovery/{cell}/{asset}` | on safe-mode + on action |
| Objectives / event log | `GET /objectives`, `/eventlog` | on tick |
| White control panel | `POST /param`, `/start`, time routes, `/inject` (with `at_sim_t`), `GET /injects`, `GET /inject_library` | on action |
| Inject builder (FW §11.D.19) | `GET /inject_library`, `POST /inject {inject:{effects:[]}, at_sim_t}` | on action |
| Consequence preview (FW §11.D.18) | `POST /preview/consequence` | on compose edit |
| Verb assistants (FW §11.A) | `POST /maneuver/compute`, `/jam/compute`, `/engage/compute`, `/cyber/compute`, `/sigint/compute` | on slider edit |
| Conjunction panel (FW §11.C.14) | `GET /conjunctions/{cell}` + `POST /order` with `verb: prop.collision_avoid` | on tick / on action |
| Coaching panel (FW §11.D.17) | `GET /coaching/{cell}` | on tick |
| Cell activity Gantt | `GET /activity/{cell}?past_window_s&future_window_s` | on tick / on window-control change |
| AAR | `GET /aar`, `/aar/at?seq=`, `/aar/objectives?seq=` | on scrub |
| Save / resume | `GET /save`, `POST /load_save` | on action |

The compose form is fog-respecting end-to-end: a player cell that asks for telemetry, recovery
status, or the next-contacts of another cell's asset is refused at the manager boundary, not
the UI. A pre-existing `refresh()` race (a slow god-view fetch could overwrite a newly-selected
player cell's view) is fixed with a supersede token (`REFRESH_SEQ`).

### 16.12 Accessibility, presentation mode, multi-display

- **Not colour-only.** Affiliation and confidence are also encoded by shape/label so the console
  is usable on poor projectors and for colour-vision-deficient operators.
- **Presentation mode.** A high-contrast, larger-type body class (`body.present`) is toggled
  from the toolbar for projector / PME use.
- **Three persisted palette/text toggles (FW §11.D.20 — shipped):**
  - **`cb-safe`** — Okabe-Ito colorblind-safe palette (deuteranopia + protanopia safe).
  - **`hi-contrast`** — WCAG-AAA contrast (`body.hi-contrast`): pure black background, pure white
    borders/text, yellow/cyan accents. Borders override to `#ffffff` site-wide for low-vision use.
  - **`large-text`** — bumps base font to 17 px and pads buttons/inputs for projector / low-vision.
  Each toggle persists in `localStorage` via the existing `applyToggle()` path and is also
  exposed in the `⌘K` command palette ("toggle cb-safe palette", "toggle high-contrast mode",
  "toggle large-text mode").
- **Multi-display reflow.** A toolbar **Detach viewers** action pops a second window rendering
  the cell's belief scene on a slow tick — sufficient for a second-screen setup. A full
  multi-region detach with shared selection state is in `FUTURE-WORK.md` §8.
- **Time-display block (FW user request).** The header's clock area is split into two rows:
  the canonical **UTC** clock (everything the engine touches is UTC microseconds) and a
  selectable **local timezone** row (Eastern default; Central / Mountain / Pacific /
  London / Paris / Tokyo / UTC-only). The timezone selector re-renders instantly via
  `Intl.DateTimeFormat` — no server round-trip — and the choice persists in `localStorage`.

### 16.13 Inject library + builder (FW §11.D.19 — shipped)

White-Cell injects gained a reusable **library** + an in-page **builder** alongside the legacy
fire-by-id dropdown:

- **Library** lives at `spacesim/content/inject_library.yaml`. Five templates ship:
  `debris_field_500km`, `gnss_jam_regional`, `rpo_ambiguous`, `gs_outage_diego_garcia`,
  `space_weather_severe`. Each is a valid `Inject` whose `effects` use only handlers that
  exist in `manager._h_inject` (`message`, `reveal_asset`, `political_consequence`,
  `patch_cyber_vuln`, `gs_outage`, `space_weather`, `conjunction_warning`, plus the new
  `spawn_debris` handler).
- **Builder UI** is a `<details>` panel below the Fire row: template picker → JSON editor →
  schedule selector (**Now** / **+ seconds from now** / **Absolute UTC** — pasted from the UTC
  clock literal) → **Schedule / fire** button → result line.
- **Replay-safe scheduling** — `fire_inject(at_sim_t=…)` (manager) clamps past timestamps to
  `now`, schedules future ones through `sim.scheduler` so they replay byte-identical on
  save/resume and through AAR scrub. The HTTP body is `{inject:{effects:[…]}, at_sim_t:<µs>}`.
- **`spawn_debris` handler** appends a `DebrisField` with `{regime, altitude_km, n_fragments}`
  to `world.debris`, raising the conjunction-screening surface for downstream planning.

### 16.13.1 Cell activity Gantt timeline (per-cell, fog-respecting)

A full-width Gantt panel sits between the viewers and the AAR panel, rendering **past +
present + scheduled** activity for the active cell.  Data is server-side fog-filtered:

- `cell == "white"` → three lanes (BLUE, RED, NEUTRAL).  Every order, every active effect,
  every scheduled inject across the exercise.
- `cell ∈ {blue, red}` → a single lane.  Only orders issued by that cell + active effects
  on its own assets.

**Status encoding** (server-computed, client-rendered):

| Status | Source | Visual |
|---|---|---|
| `executed` | `Order.status == "executed"` | solid cell-coloured rectangle |
| `active` | `start ≤ now ≤ end` for any queued order | solid + bright-green outline |
| `queued` | `Order.status == "queued"` with future window | dashed cell-coloured outline |
| `cancelled` | `Order.status == "cancelled"` | grey strikethrough |
| `rejected` | `Order.status == "rejected"` | red `×` marker (no window) |
| `scheduled` | `sim.scheduler.pending()` with `kind == "inject"` | dashed neutral outline |

The bar's start/end span the order's `earliest_window`; rejected orders use a 60-second
nominal marker around `issued_at`.  Clicking a bar prints
`cell · actor · action · status · window · delivery_path` into a detail line below the canvas.

Endpoint: `GET /api/sessions/{sid}/activity/{cell}?past_window_s&future_window_s`.  The
default display window is `[NOW - 30 min, NOW + 2 h]`; selectors let the operator widen to
`[-3 h, +6 h]`.  Read-only and replay-safe (no engine mutation), so White Cell can leave the
panel open during scrubbing or branching without disturbing the live session.

### 16.14 Conjunction screening + coaching (FW §11.C.14 + §11.D.17 — shipped)

- **Conjunctions sidebar** reads `GET /api/sessions/{sid}/conjunctions/{cell}` and renders one
  row per upcoming close approach with object A / object B / range / time-to-CA. When the
  active cell owns one of the objects, the row carries an **Evade** button that posts a
  `command` order with `verb: prop.collision_avoid` for the owned asset. The verb consumes a
  small Δv budget and queues to the next command-uplink window.
- **Coaching sidebar** reads `GET /coaching/{cell}` and renders the
  `vignette.coaching: list[{at_sim_t?, cell, title, body}]` notes whose `cell` matches the active
  cell (or is `white` = visible to all) and whose `at_sim_t` is `None` or `≤ world.now`. Useful
  for facilitator pointers like "discuss this delay in the AAR".

---

*End of PSD Part 4 — operator console specification.*

*End of PSD Part 3.*

---
