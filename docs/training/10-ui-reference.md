[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 10. UI reference — every control, dropdown, and input

Exhaustive, scannable list of every interactive element in the web UI. Each section maps 1-for-1
to an annotated screenshot in [`../manual/`](../manual/INDEX.md) — the callout numbers on the
screenshot match the row numbers in each table.

For *narrative* introductions to the same features (when to use them, why they exist), read
[`02-interface.md`](02-interface.md) and [`05-core-concepts.md`](05-core-concepts.md). This
module is the reference.

| Section | Panel | Annotated screenshot |
|---|---|---|
| §10.1 | Header / toolbar | [`ref-01-header.png`](../manual/ref-01-header.png) |
| §10.2 | Cell & Time sidebar | [`ref-02-cell-time.png`](../manual/ref-02-cell-time.png) |
| §10.3 | Injects (White Cell) + builder | [`ref-03-injects.png`](../manual/ref-03-injects.png) |
| §10.4 | Fleet rail | [`ref-04-fleet.png`](../manual/ref-04-fleet.png) |
| §10.5 | Tasking (sensor) | [`ref-05-tasking.png`](../manual/ref-05-tasking.png) |
| §10.6 | Satellite command (compose) | [`ref-06-compose.png`](../manual/ref-06-compose.png) |
| §10.7 | Maneuver assistant | [`ref-07-maneuver.png`](../manual/ref-07-maneuver.png) |
| §10.8 | Jam assistant | [`ref-08-jam.png`](../manual/ref-08-jam.png) |
| §10.9 | Batch bar + fleet-subset helpers | [`ref-09-batch.png`](../manual/ref-09-batch.png) |
| §10.10 | 3D globe viewer | [`ref-10-globe.png`](../manual/ref-10-globe.png) |
| §10.11 | 2D belief map viewer | [`ref-11-map.png`](../manual/ref-11-map.png) |
| §10.12 | After-action review (AAR) | [`ref-12-aar.png`](../manual/ref-12-aar.png) |
| §10.13 | Subsystem drill-down | [`ref-13-drill.png`](../manual/ref-13-drill.png) |
| §10.14 | Modals, keyboard & mouse | [`ref-14-modals-keys.png`](../manual/ref-14-modals-keys.png) |
| §10.15 | Cell activity timeline | [`ref-15-activity.png`](../manual/ref-15-activity.png) |

---

### 10.1 Header / toolbar — always visible

![Header reference](../manual/ref-01-header.png)

The toolbar is the only persistent UI strip. White-cell-only controls (everything that mutates
the session — Pause/Resume, Rewind, time-step jumps, the Session menu) are hidden when the
operator switches to Blue or Red.

**Toolbar buttons (left to right):**

| # | Control | Type | Effect / valid values |
|---|---|---|---|
| 1 | Logo + title | label | Tints with the active cell accent. |
| 2 | UTC clock | label | Live sim-UTC time (server-authoritative). |
| 3 | Session summary chip | label (white-only) | `<vignette> · <sid> · loaded \| ▶ running` once a session is loaded. |
| 4 | White / Blue / Red | buttons | Switch the operator's seat (client-side `data-cell` swap; fog-of-war is enforced server-side). |
| 5 | ⏸ Pause / ▶ Resume | button (white-only) | `POST /api/sessions/{sid}/clock {running}` — drives the server-authoritative clock for **every** connected tab. |
| 6 | +1m / +10m / +1h | buttons (white-only) | `POST /step` for manual sim-time jumps. Server re-anchors so the wall clock doesn't snap the jump back. |
| 7 | ⟲ Rewind | button (white-only) | `POST /rewind` to t=0. Deterministic replay re-derives state byte-identical; the server re-anchors the clock at the rewound moment. |
| 8 | ⏸ Handover | button | Blur the screen + show "HANDING OFF" overlay (hot-seat seat-swap between cells). |
| 9 | 📋 Session ▾ | menu (white-only) | See §10.1.1 below. |
| 10 | ▦ View ▾ | menu | See §10.1.2 below. |
| 11 | ⚙ Settings ▾ | menu | See §10.1.3 below. |
| 12 | UNCLASSIFIED // TRAINING | banner | Always-visible classification marking. |

The three dropdown menus share the same wiring: click to open, click outside or press
**Esc** to close, opening one closes the others.

#### 10.1.1 Session menu (white-only)

| Section | Item | Effect |
|---|---|---|
| Vignette | Vignette dropdown | Pick a scenario from the library before Load. |
| Vignette | Seed input | Deterministic RNG seed (any non-negative integer; default 1). |
| Vignette | **Load** button | `POST /api/sessions` → creates the session id. The page URL gets `#sess-N` appended so it can be shared. |
| Vignette | **▶ Start** button | `POST /api/sessions/{sid}/start` + arms the server clock. Disabled until Load. |

#### 10.1.2 View menu

| Section | Item | Effect |
|---|---|---|
| Display mode | Presentation mode | Body class `present` (hides facilitator controls during demo). |
| Display mode | Projector mode | Body class `projector` (larger fonts, hides compose form for a White-Cell projector). |
| Display mode | Color-blind safe | Body class `cb` (Okabe-Ito palette). |
| Display mode | High contrast | Body class `hi-contrast` (WCAG-AAA palette). |
| Display mode | Large text | Body class `large-text` (17 px base + larger hit areas). |
| Pop out (multi-screen) | 3D globe | Open `/?layout=globe&cell=<current>#<sid>` in a new window — that window joins the same session and shows only the 3D globe panel. |
| Pop out | 2D belief map | Same pattern with `layout=map`. |
| Pop out | Globe + Map | `layout=globe+map` (both viewers side-by-side). |
| Pop out | Fleet & telemetry | `layout=fleet` — fleet rail + drill-down. |
| Pop out | Order compose | `layout=order` — compose form + activity timeline. |
| Pop out | AAR timeline | `layout=aar` — AAR scrubber. |

Pop-out windows reuse the polished panels — there is no separate "viewer" surface. Each
pop-out polls the server at 1.5 s like any other tab, so closing the parent doesn't kill them.

#### 10.1.3 Settings menu

| Section | Item | Effect |
|---|---|---|
| Session | ⬇ Save session | `GET /save` → download session JSON. |
| Session | ⬆ Load session | File picker + `POST /load_save` (the loaded session starts paused — White must Resume). |
| Tools | ? Coachmark tour | Walk the UI itself with a spotlight tip. |
| Tools | Tutorial panel | Per-vignette tutorial steps for the active cell. |
| Tools | Inspect vignette YAML | Open the vignette YAML inspector modal. |
| Tools | ? Help | Open the help modal (shortcuts + glossary + workflow tips). |

---

### 10.2 Cell & Time — sidebar panel (top)

![Cell & Time reference](../manual/ref-02-cell-time.png)

| # | Control | Type | Effect / valid values |
|---|---|---|---|
| 1 | UTC | read-only | Canonical sim time (`iso(NOW)` from the engine, always UTC). |
| 2 | Timezone selector | dropdown | Eastern (default) / Central / Mountain / Pacific / London / Paris/Berlin / Tokyo / UTC-only. |
| 3 | Local time | read-only | Renders NOW in the selected zone via `Intl.DateTimeFormat`. |
| 4 | Session label | read-only | The active session id. |
| 5 | Objectives | read-only color-coded list | Per-cell mission objectives, one row each. `✓` (green, bright text, green left-border) when met; `✗` (red mark, dim text, red left-border) when unmet. Blue/Red see only their own side (fog-of-war); White sees both sides with `blue` / `red` group labels. Object ids are prettified (`deliver_isr` → "Deliver ISR"). |
| 6 | Messages | read-only `<ul>` | Inbox for this cell (sorted newest first). |
| 7 | Coaching | read-only list | `GET /coaching/{cell}` — facilitator notes due-now for this cell. |
| 8 | Conjunctions | list + Evade buttons | `GET /conjunctions/{cell}` — each row carries a per-asset Evade button. |

The **Evade** button on a conjunction row issues a `command` order with `verb: prop.collision_avoid`
on the own asset, queued to the next command-uplink window.

---

### 10.3 Injects (White Cell) + Build / schedule inject

![Injects reference](../manual/ref-03-injects.png)

| # | Control | Type | Effect / valid values |
|---|---|---|---|
| 1 | Inject dropdown | dropdown | Vignette-defined injects from `GET /injects`. |
| 2 | Fire | button | `POST /inject` with `{inject: <id>}` — fires immediately. If the server rejects the inject (HTTP 400, see below), nothing is applied and **nothing appears on screen**: this button has no result line. If an expected message never shows in **Messages**, re-check the inject in the builder, which does report the reason. |
| 3 | Build / schedule inject | `<details>` toggle | Expands the builder panel below. |
| 4 | Template | dropdown | 5 library entries from `GET /inject_library` + `(custom)`. |
| 5 | Load | button | Pre-fills the JSON editor with the selected template's effects. |
| 6 | Effects | textarea | JSON list. Any `type` recognised by `manager._h_inject` (see below). |
| 7 | Schedule | dropdown | **Now** (immediate) / **+ seconds from now** / **Absolute UTC**. |
| 8 | + seconds from now | number | Visible only when Schedule=+s. Offset in seconds. |
| 9 | Absolute UTC | datetime-local | Visible only when Schedule=absolute. UTC literal (paste from the UTC clock). |
| 10 | Schedule / fire | button | `POST /inject` with `{inject:{effects:[…]}, at_sim_t:<µs>}`. Past timestamps clamp to "now". |
| 11 | Result line | read-only | `✓ fired immediately (N effects)` or `✓ scheduled for <UTC> (N effects)` on success. A rejected inject shows `✗ server error:` followed by the server's `inject rejected: #i <type>: <reason>` text, one entry per bad effect (`#i` is the effect's position, counting from 0). |

**Supported effect types in the editor:** `message`, `reveal_asset`, `political_consequence`,
`patch_cyber_vuln`, `gs_outage`, `space_weather`, `conjunction_warning`, `spawn_debris`, plus the
four controller events `anomaly` (needs `target` and `subsystem`: `bus` or `telemetry`),
`sensor_outage` (`target` = a sensor id), `forced_custody_loss` (`cell` = `blue`/`red` and
`target`) and `scripted_manoeuvre` (`target`, `mode` = one of the six manoeuvre modes, `params`).
See [`07-white-cell-facilitation.md`](07-white-cell-facilitation.md) for example payloads.

**Checked before anything fires.** The server checks the whole effect list when you click Fire or
Schedule / fire. It rejects the inject with HTTP 400, and applies **none** of its effects (even the
valid ones), when any effect:

- has an unknown `type`, is missing a required key, or has a malformed value (for example an
  `anomaly` subsystem other than `bus`/`telemetry`);
- is an `anomaly` whose target has no bus (for example, any shipped Red satellite);
- is a `sensor_outage` whose target is not a sensor;
- is a `forced_custody_loss` for a track that cell does not hold;
- is a `scripted_manoeuvre` whose target has no orbit, or whose `params` the manoeuvre maths refuses.

The same check runs when you fire a vignette inject by name with **Fire** (row 2).

A builder inject you schedule for later goes through the same check when you click Schedule /
fire. It is **not checked again when it fires**, so its targets may have changed by then.

Injects a vignette schedules by time or by condition are never checked at the console, because
they fire on their own. When one of these fires:

- a malformed effect is skipped, the rest still apply, and White alone gets the **Messages** line
  `inject effect skipped (<type>): <reason>`.

When any scheduled inject fires, vignette or builder:

- a well-formed effect whose target is missing or unsuitable at that moment (for example, the
  track is gone, or the satellite no longer has a bus) is skipped with **no** message;
- a `scripted_manoeuvre` whose `params` the manoeuvre maths now refuses is skipped with the same
  White-only `inject effect skipped` line.

---

### 10.4 Fleet rail

![Fleet rail reference](../manual/ref-04-fleet.png)

| # | Control | Type | Effect / valid values |
|---|---|---|---|
| 1 | Filter chips | 5 chips | **All** / **Bus-red** / **Payload-degraded** / **Under-attack** / **Safed** — filters the table client-side. |
| 2 | Row click | mouse | Opens the Subsystem drill-down for that asset. |
| 3 | Row shift+click | mouse | Toggles the row into the multi-asset batch (see §10.9). |

The next-contact countdown column is **read-only** (data from `GET /next_contacts/{cell}`).

---

### 10.5 Tasking (sensor)

![Tasking reference](../manual/ref-05-tasking.png)

| # | Control | Type | Effect / valid values |
|---|---|---|---|
| 1 | Mode chips | 2 chips | **Organic** (own sensor) / **SSN request** (national/coalition SSN). |
| 2 | Intent | dropdown | **search** / **track** / **characterize** / **cue**. |
| 3 | Sensor | dropdown | Organic mode only. `auto` lets the engine pick the earliest viable own sensor. |
| 4 | Regime | dropdown | SSN mode only. **LEO** / **MEO** / **GEO** / **HEO** / **cislunar**. |
| 5 | Target | dropdown + **or id** text input | Dropdown lists the other side's **known targets**: your tracks, grouped by owner, plus any non-own satellite/space-based/interceptor/directed-energy asset your fog-filtered view shows. White tasks on Blue's behalf and so sees every non-Blue asset. When the list is empty it says *no known targets yet*. The **or id** box takes precedence over the dropdown. Use it to task a sensor against an id you have not tracked yet; collection is how custody starts. If both are empty, Plan collection falls back to the compose form's target (§10.6 row 4). |
| 6 | Priority | dropdown | **routine** / **priority** / **immediate** (drives SSN SLA + organic queue order). |
| 7 | Plan collection | button | Organic: `POST /order` with `action: observe`. SSN: `POST /ssn/{cell}/request`. |
| 8 | Beam mode | dropdown | `auto` + **wide_area / stripmap / spotlight / scan / fine / polarimetric** (see `engine/isr.py`). On a ground radar keep `auto`: any other entry replaces the radar's own `fence`/`dish` mode. The radar modes are not listed here; send them through §10.6 row 5 (see [`06`](06-the-vignette-library.md#authoring-sensors-optional-modality-fields)). |
| 9 | Look angle | range slider | 0–45° off-nadir. Cosine roll-off applies to gain + swath width. |
| 10 | Duration (s) | number | 30–3600 s. Drives the SOC drain `base × power_factor × duration / 300`. |
| 11 | Coverage line | read-only | SSN mode: `GET /ssn/{cell}/coverage?regime=` — feasibility hint. |
| 12 | SSN queue rows | per-row [✕] cancel | `POST /ssn/{cell}/cancel`. |

---

### 10.6 Satellite command (compose form)

![Compose-form reference](../manual/ref-06-compose.png)

| # | Control | Type | Effect / valid values |
|---|---|---|---|
| 1 | Role filter chips | 4 chips | **All** / **Bus** / **Payload** / **SDA** — filters the Actor dropdown. |
| 2 | Actor | dropdown | Own assets (filtered by role chip + current cell). |
| 3 | Action | dropdown | Legal actions for the actor's `kind`: e.g. satellite ⇒ `downlink/maneuver/command`, jammer ⇒ `jam`. |
| 4 | Target | dropdown + **or id** text input | Uses the same known-target list as §10.5 row 5, with the selected actor's own side left out. The **or id** box takes precedence. Both fields are **enabled only for `jam` / `engage` / `cyber` / `observe`**. For any other action they are blanked and disabled because that order takes no target. |
| 5 | Params | JSON text, under **Advanced (raw JSON params)** | Pre-filled per action (see PARAM_TEMPLATE in `app.js`). Live dry-run on every keystroke. A field with the wrong type or a non-finite number (`"inf"`, a `dv` without exactly three numbers) shows ✗ `invalid_param`. A field set to `null` counts as left out. |
| 6 | Validity preview | read-only | ✓ queue · delivery_path · window OR ✗ reason (from `POST /order/validate`). |
| 7 | Consequence preview | read-only | severity / esc / reversible / debris / attribution (from `POST /preview/consequence`). |
| 8 | Issue order | primary button | `POST /order`. Disabled while validity preview is ✗. |
| 9 | ★ Save preset | button | Save the current order as a named playbook (`localStorage`, per vignette). |
| 10 | ? Coachmark tour | button | Start the in-page coachmark tour over compose form. |
| 11 | Playbook list | clickable rows | Click to load a saved preset back into the form. |
| 12 | Pass-timeline ribbon | read-only canvas | Three lanes (**cmd / tlm / obs**) for the selected actor, next 6 h. Hourly tick marks. |
| 13 | Queue rows | per-row [✕] cancel | `POST /cancel` (replay-safe — Scheduler skips the cancelled event). |

When **Action** is set to `maneuver` or `jam`, an additional assistant panel appears below
Params — see §10.7 / §10.8.

*Screenshot note:* `ref-05-tasking.png` and `ref-06-compose.png` were drawn before the target
picker shipped and still show **Target** as a single text box. Where a screenshot and a table row
disagree, follow the table row (§10.5 row 5, §10.6 row 4).

---

### 10.7 Maneuver assistant (Action = maneuver)

![Maneuver assistant reference](../manual/ref-07-maneuver.png)

| # | Control | Type | Effect / valid values |
|---|---|---|---|
| 1 | Maneuver mode | dropdown | **eci / lvlh / finite_burn / target_coe / hohmann / plane_change**. Switches the field set. |
| 2 | ECI Δv X / Y / Z | numbers | (mode=eci) m/s in the inertial frame. |
| 3 | LVLH R / T / N | numbers | (mode=lvlh) Radial / Along-track / Normal m/s in the orbit frame. |
| 4 | Finite-burn DirR/T/N + mag + dur | numbers | (mode=finite_burn) direction (normalised LVLH) + magnitude (m/s) + duration (s; informational). |
| 5 | Target-COE a / e / i / RAAN / ω | numbers | (mode=target_coe) blank = keep current. Matches velocity at same true anomaly. |
| 6 | Hohmann target altitude | number | (mode=hohmann) km. Two-burn transfer; second-burn line appears in result. |
| 7 | Plane-change Δi | number | (mode=plane_change) signed degrees. Rodrigues rotation about r̂. |
| 8 | Compute Δv → | button | `POST /maneuver/compute` — read-only preview. |
| 9 | Cost / new-orbit line | read-only | `Δv = <m/s>` · `new_orbit a/e/i…` · optional `second_burn`. Result also fills `o-params`. |

Click **Compute** then **Issue order** to queue the maneuver; the engine consumes Δv from the
asset's `resources.delta_v_ms` when the order executes at its window.

---

### 10.8 Jam assistant (Action = jam)

![Jam assistant reference](../manual/ref-08-jam.png)

| # | Control | Type | Effect / valid values |
|---|---|---|---|
| 1 | Modulation | dropdown | **barrage / spot / sweep / deceptive**. `deceptive` auto-overrides attribution to `overt`. |
| 2 | Power (W) | number | Transmit power. Drives the effective denial radius (`R ∝ √P`). |
| 3 | BW (kHz) | number | Jammer bandwidth. |
| 4 | Victim BW (kHz) | number | Target signal bandwidth (drives coverage weighting for sweep/spot). |
| 5 | Base P_s | number | Operator's base success probability (0–1). |
| 6 | Preview footprint | button | `POST /jam/compute`. Renders an orange dashed polygon on the 2-D map. |
| 7 | Summary / result line | read-only | `radius ≈ <km> · P(success) <p> · draw <W> · detect <%> · attr <bias>`. |

The preview polygon stays on the map until the operator changes the Action away from `jam`.

---

### 10.9 Batch bar + fleet-subset helpers

![Batch bar reference](../manual/ref-09-batch.png)

| # | Control | Type | Effect / valid values |
|---|---|---|---|
| 1 | Batch list | read-only | Comma-separated asset ids currently in the batch. |
| 2 | Issue to all | button | POSTs the current compose body once per batched asset. |
| 3 | Clear | button | Empty the batch. |
| 4 | Fleet-subset helpers | 4 buttons | **All own / ISR sats / SATCOM / Same group** — predicate-fill the batch. |

The **Same group** helper requires an Actor already selected and uses its `group` field.

---

### 10.10 3D globe viewer

![Globe reference](../manual/ref-10-globe.png)

| # | Control | Type | Effect / valid values |
|---|---|---|---|
| 1 | ＋ | button | Zoom in. |
| 2 | － | button | Zoom out. |
| 3 | tilt | range slider | –80° to +80°. |
| 4 | zoom-to | dropdown | Own assets + tracks; selecting an entry centres the camera. |
| 5 | map | checkbox | Toggle world coastlines + country borders. |
| 6 | spin | checkbox | Auto-rotate. |
| 7 | Canvas drag | mouse | Rotate the globe. |
| 8 | Canvas wheel | mouse | Zoom in/out. |
| — | Reset | button | Restore the default camera (no callout shown). |

---

### 10.11 2D belief map viewer

![Map reference](../manual/ref-11-map.png)

| # | Control | Type | Effect / valid values |
|---|---|---|---|
| 1 | ＋ | button | Zoom in. |
| 2 | － | button | Zoom out. |
| 3 | center | dropdown | Own assets + tracks; selecting centres the map on the asset. |
| 4 | map | checkbox | Toggle world coastlines + country borders. |
| 5 | tracks | checkbox | Toggle uncertainty rings + track labels. |
| 6 | grid | checkbox | Toggle the 30°-spaced lat/lon graticule. |
| 7 | Canvas drag | mouse | Pan the map (lat/lon offset). |
| 8 | Canvas wheel | mouse | Zoom in/out. |
| — | Reset | button | Restore the default camera (no callout shown). |

---

### 10.12 After-action review (AAR)

![AAR reference](../manual/ref-12-aar.png)

| # | Control | Type | Effect / valid values |
|---|---|---|---|
| 1 | Scrubber | range slider | 0 → `n_events`. Read-only replay; never disturbs the live session. |
| 2 | 📌 Bookmark | button | Pin the current sim moment to revisit later. |
| 3 | ⬇ CSV / ⬇ JSON | download links | `GET /aar/export.csv` / `GET /aar/export.json`. |
| 4 | Bookmark list | clickable rows | Click to jump the scrubber back to the bookmarked moment. |
| 5 | ＋ Save current branch | button | Name the live world for later comparison. |
| 6 | Compare selected | button | Diff two saved branches (objectives + assets). |
| 7 | Branch list | checkbox rows | Select up to two branches for the compare. |

---

### 10.13 Subsystem drill-down

![Drill-down reference](../manual/ref-13-drill.png)

| # | Control | Type | Effect / valid values |
|---|---|---|---|
| 1 | Orbital elements | read-only strip | a / e / i / Ω / ω / ν + period for the selected satellite, from the scene; refreshes on every poll so a maneuver's new orbit shows within ~1.5 s. Hidden for ground assets. |
| 2 | Parameter chips | clickable chips | Click to graph that telemetry parameter. |
| 3 | compare to nominal | checkbox | Overlay the clean baseline (`?nominal=1`). |
| 4 | overlay | dropdown | Pick a second parameter to overlay on the graph. |
| 5 | Graph canvas | read-only | 120-point line graph of the last hour of sim time (or since exercise start) from `GET /telemetry/{cell}/{asset}/{param}?n=120`; each point is that instant's own state. |
| 6 | Verb buttons | per-subsystem cards | One-click load the command verb into the compose form. |
| 7 | Begin recovery | button | (Recovery strip) `POST /recovery/{cell}/{asset}` — start the multi-pass chain. |
| 8 | Patch (def.patch_cyber) | button | (Recovery strip) Load the patch-cyber command pre-filled with the first unpatched vector. |

The recovery strip appears only when the selected asset's bus is in safe mode. The subsystem
log under the graph is read-only.

---

### 10.14 Modals, overlays, keyboard & mouse

![Modals + keyboard reference](../manual/ref-14-modals-keys.png)

#### Modals & overlays

| Modal | Trigger | Controls |
|---|---|---|
| Command palette | `⌘K` / `Ctrl+K` | text input · result list · `↑/↓` navigate · `Enter` run · `Esc` close |
| Handover | ⏸ Handover button | **Resume** button |
| Help | ? Help button | **Close** button |
| Tutorial | Tutorial button | **✕** close · clickable steps |
| Coachmark tour | ? Coachmark tour button | **← Back** · **Next →** · **✕ Close** |
| Vignette inspector | Inspect button | **⬇ Download YAML** · **Close** |

#### Keyboard shortcuts (global)

| Key | Effect |
|---|---|
| `j` / `k` | Cycle through actor select |
| `c` | Focus the compose form |
| `g` | Open Subsystem drill-down for the selected actor |
| `⌘K` / `Ctrl+K` | Open the command palette |
| `Esc` | Close palette / coachmark / handover |
| `↑` / `↓` | Navigate palette items |
| `Enter` | Run the highlighted palette item |
| `Shift+click` on fleet row | Toggle the row into the batch |

#### Mouse / canvas interactions

| Where | Action |
|---|---|
| 2D map canvas | Drag = pan · wheel = zoom |
| 3D globe canvas | Drag = rotate · wheel = zoom |
| AAR scrubber | Drag the slider thumb to scrub event-by-event |
| Fleet row | Click = open drill-down · shift+click = batch toggle |

---

### 10.15 Cell activity timeline (per-cell Gantt — past · present · scheduled)

![Activity timeline reference](../manual/ref-15-activity.png)

Each cell gets a Gantt-style ribbon showing what *that* cell has done, is doing, and has
scheduled. **Fog-of-war applies at the API boundary:**

- **White Cell** sees three lanes: BLUE, RED, NEUTRAL — every order, every active effect,
  every scheduled inject.
- **Blue Cell** sees only the BLUE lane — only its own orders and effects on its own assets.
- **Red Cell** sees only the RED lane — same fog-of-war contract.

The data feed is `GET /api/sessions/{sid}/activity/{cell}` — read-only, replay-safe, derived
from `osys.orders`, `world.active_effects`, and `sim.scheduler.pending()`.

| # | Control | Type | Effect / valid values |
|---|---|---|---|
| 1 | Past window | dropdown | **10 min / 30 min / 1 h / 3 h** — how far back to show. |
| 2 | Future window | dropdown | **30 min / 1 h / 2 h / 6 h** — how far ahead to show. |
| 3 | NOW vertical line | read-only | Bright-green line at the current sim time. |
| 4 | Lane label | read-only | One lane per visible cell (BLUE / RED / NEUTRAL for White; single lane for Blue or Red). |
| 5 | Executed bar | read-only | Filled cell-coloured rectangle. The order completed during this window. |
| 6 | Active bar | read-only | Filled + bright-green outline. The order's window straddles NOW (currently executing). |
| 7 | Queued / scheduled bar | read-only | Dashed cell-coloured outline. The order is waiting for its window. |
| 8 | Cancelled bar | read-only | Grey strikethrough. The order was cancelled before firing. |
| 9 | Rejected marker | read-only | Red **×**. The order was rejected at issue (no window). |
| 10 | Scheduled inject | read-only | Dashed neutral-coloured rectangle at the inject's `at_sim_t`. |
| 11 | Bar click | mouse | Shows `cell · actor · action · status · window · delivery_path` in the detail line below. |

Bars within a lane are stacked vertically per **actor** (asset id) so a single satellite's
activity reads as one row; multiple satellites stack within the same cell lane.

**Status semantics (engine source of truth):**

| Status | Meaning | Source |
|---|---|---|
| `executed` | Order has fired (`Order.status == "executed"`) | `osys.orders` |
| `active` | The bar's window contains NOW | computed at request time |
| `queued` | Order has a future window but has not fired yet | `osys.orders` |
| `cancelled` | Cancelled before firing (`POST /cancel`) | `osys.orders` |
| `rejected` | Rejected at issue (`Order.status == "rejected"`) | `osys.orders` |
| `scheduled` | Future inject in `sim.scheduler.pending()` | scheduler |

**Endpoint:** `GET /api/sessions/{sid}/activity/{cell}?past_window_s=<int>&future_window_s=<int>`
returns
```json
{
  "now": <µs UTC>,
  "t_start": <µs UTC>, "t_end": <µs UTC>,
  "cells": ["blue", "red", "neutral"],
  "activities": [
    {"kind": "order"|"inject"|"effect", "cell": "blue"|"red"|"neutral",
     "actor": "<asset id>", "action": "<verb>", "target": "<id>|null",
     "start": <µs>, "end": <µs>, "status": "...", "label": "...",
     "delivery_path": "<path>|null"}
  ]
}
```

---

### Cross-references

- **HTTP endpoints behind each control:** [`08-http-api-reference.md`](08-http-api-reference.md).
- **Why each panel exists (narrative):** [`02-interface.md`](02-interface.md), [`05-core-concepts.md`](05-core-concepts.md).
- **White-Cell facilitation patterns:** [`07-white-cell-facilitation.md`](07-white-cell-facilitation.md).
- **Build-spec operator-console contract:** [`../build-spec/07-operator-console.md`](../build-spec/07-operator-console.md).

---
