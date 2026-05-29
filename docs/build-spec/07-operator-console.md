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
| White control panel | `POST /param`, `/start`, time routes, `/inject`, `GET /injects` | on action |
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
- **Multi-display reflow.** A toolbar **Detach viewers** action pops a second window rendering
  the cell's belief scene on a slow tick — sufficient for a second-screen setup. A full
  multi-region detach with shared selection state is in `FUTURE-WORK.md` §8.

---

*End of PSD Part 4 — operator console specification.*

*End of PSD Part 3.*

---
