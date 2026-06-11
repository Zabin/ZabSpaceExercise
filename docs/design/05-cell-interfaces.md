# Cell Interfaces — Red / Blue / White UX and Permitted Actions

This document defines what each cell sees and may do. In v1 a **single player** drives any cell
via a cell-switcher; the permission/visibility rules below are written as if the cells are
separate so they hold unchanged when LAN multiplayer is added.

## Shared UX elements (Red and Blue)

Both operational cells work from the same core layout; only ownership and visibility differ.

1. **World map** — 2D map (optional 3D globe later) showing *own* assets always, and *other*
   assets only where the cell holds custody (per fog setting). Ground tracks, sensor/jammer
   footprints, ground stations, and debris fields render here.
2. **Asset roster / fleet SOH rollup** — list of own assets with a **red/yellow/green
   state-of-health (SOH) rollup** (power, attitude, thermal, propellant, storage, comms),
   fuel/power/ammo, current posture, and a live **"next contact" countdown** per asset. One
   click drills from fleet → satellite → subsystem → individual telemetry parameter, mirroring
   real mission-control software.
3. **Pass-timeline ribbon** — per selected asset, a horizontal timeline of upcoming access
   windows colored by channel (uplink/downlink/observation/jam/engagement/proximity). This is
   the cell's primary planning surface — it makes the orbital constraint tangible.
4. **Telemetry & payload panel** — for the selected asset, its bus SOH and **payload-specific**
   readouts (SATCOM transponder/interference, ISR collection queue/storage/downlink, SIGINT/SDA
   tasking & custody, space-control effector status), each color-coded against soft/hard limits.
   Crucially, this shows the **last pass-gated snapshot with its timestamp** — between contacts
   it may be stale, and the operator knows it. (See `../research/06-bus-and-payload-operations.md`.)
5. **Order / pass-plan panel** — context-sensitive list of commands legal *for the selected
   asset right now or at its next window*, drawn from the asset's command database. Orders are
   assembled into a **pass plan**, validated before release, and show **when they will execute**
   (the scheduled window) rather than executing instantly.
6. **Command/collection queue** — pending activities with scheduled execution times; cancellable
   while still queued.
7. **Track / SDA panel** — known tracks with confidence meters (decaying), and characterization
   status.
8. **Alarm / message / intel feed** — out-of-limit **alarms** (e.g., a satellite that entered
   **safe mode** while out of contact, surfaced when its stored telemetry dumps at the next
   pass), injects, and attribution signals ("an effect was observed on SAT-7; source
   unconfirmed").

> The defining UX principle: **the interface never lets a cell pretend orbital geometry doesn't
> exist.** Every action is tied to a window, and the countdown/ribbon keep that front-of-mind.

## Permitted actions by asset kind

The Order panel is generated from the asset kind + the vignette's ROE parameters. Representative
action set:

| Asset kind | Actions (subject to ROE & windows) |
|---|---|
| Satellite (ISR) | image(target), downlink, maneuver(dv), set_posture, frequency_hop |
| Satellite (SATCOM) | reallocate_users, maneuver(dv), set_posture, frequency_hop |
| Satellite (escort) | escort(asset), maneuver(dv), interpose(threat) |
| Satellite (RPO/co-orbital) | rpo_close(target), inspect(target), deploy_subsat, (engage if ROE) |
| Ground station | (passive; enables uplink/downlink windows) |
| Sensor | task_observation(target), prioritize(track) |
| Jammer | jam(target, uplink|downlink), cease_jam, reposition |
| Directed energy | dazzle(target), cease |
| Interceptor (DA-ASAT) | engage(target) — only if `kinetic_authorized` ROE true |
| Cyber unit | cyber(vector) — not window-gated; subject to defender posture |
| Terrestrial force | conceal (time to known passes), relocate, employ (consumes PNT/SATCOM) |

Every order passes through `CellController.validate()`:
1. **Ownership** — actor belongs to this cell.
2. **ROE/permission** — action allowed by the vignette parameters (e.g., kinetic off → engage
   rejected with a clear reason).
3. **Resources** — sufficient delta-v/power/ammo.
4. **Window** — `AccessProvider` supplies the next valid window (or "none required" for cyber).
   The order is queued to that window.
5. **Track gate** — engagements require a weapons-quality track on the target.

Rejected orders return a **human-readable reason** the UI shows ("Cannot command SAT-7: no
ground-station contact for 11 min; order queued for 06:14:00Z" or "Engagement blocked: kinetic
ASAT not authorized in this vignette").

## Fog-of-war and attribution (per cell)

- A cell sees other-side assets **only** through its own SDA custody (governed by `fog_of_war`).
  With `realistic_sda`, losing custody means the object disappears from the map until
  re-acquired.
- **Effects are perceived before they're attributed.** Per `attribution_difficulty`, a victim
  first sees *symptoms* (degraded imagery, lost link) and only later — maybe — an attributable
  source. This is central to the RPO/EW/DE/cyber vignettes and is enforced in the `CellView`
  filter, not left to the UI.

## White Cell view (god-view + control)

White Cell sees **ground truth**: both cells' assets, both `CellView`s, hidden parameters (e.g.,
`red_intent`), the full event log, and the escalation/scoring state. White Cell does not "play"
an operational side in v1 but can:
- drive Red and/or Blue when running a session solo (single-player),
- inject events, adjust parameters live, and control time (next doc),
- observe each cell's filtered view to understand what the players know.

(Full White Cell controls are specified in `06-white-cell-controls.md`.)

## Single-player cell-switching (v1)
A top-level **cell selector** lets the one player adopt White, Red, or Blue. Switching to an
operational cell shows *that cell's* fog-filtered view; switching to White restores god-view.
This is purely a UI/session concern — the permission and visibility logic is identical to what
separate networked clients will use later, so no engine change is needed for multiplayer.

## Related specifications
The operator experience is detailed across three companion documents:
- `09-gui-principles.md` — human-factors and UX principles for semi-technical CAF space
  operators (the user class this tool targets).
- `10-sda-3d-viewer.md` — the 3D viewer that renders the cell's **SDA belief state** (not
  ground truth), shared with the 2D map via a common render-from-custody layer.
- `11-command-planning-and-tasking.md` — the plan-first command workflow (ground uplink, ISL
  relay, stored program) and the SDA sensor-tasking workflow, unified on one scheduler.
