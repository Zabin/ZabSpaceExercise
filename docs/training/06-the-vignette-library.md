[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 7. The vignette library

The simulator ships 19 runnable vignettes split across the canonical 8 numbered scenarios, a
training scenario, and four expansion tracks (mission-set trials, Red COA library, learning
stream, novel concepts). Every vignette carries a per-cell **`intro_brief`** block authored in
its YAML and surfaced in the in-tool **Mission brief** panel (View ▾ → Mission brief). The brief
is the first thing a new operator should read.

### The canonical 8 numbered scenarios (start here)

| # | Title | Teaches |
|---|---|---|
| 1 | LEO ISR Denial | Pass windows; the collect-vs-downlink split; reversible vs. kinetic effects |
| 2 | GEO RPO Shadowing | Ambiguous RPO intent; custody decay in GEO |
| 3 | GNSS EW Campaign | Local, reversible PNT denial; MEO is kinetically safe |
| 4 | Co-Orbital Threat & Escort | Active defense: escort and maneuver-to-evade |
| 5 | DA-ASAT Crisis | Escalation, debris, attribution, political cost |
| 6 | SATCOM Cyber & Link | Ground/link segment; cyber acts outside passes |
| 7 | SDA Custody Hunt | Custody decay; sensor contention; breaking custody |
| 8 | Multi-Domain Capstone | Integrated campaign across every subsystem |

### Training onboarding

| ID | Title | Teaches |
|---|---|---|
| `training-basics` | Training: Basics | The core operator loop on a minimum-viable fleet (1 sat + 1 GS) |

### Track A — mission-set trials

| ID | Title | Teaches |
|---|---|---|
| `mt-isr-sar` | SAR ISR | SAR is all-weather/day-night; succeeds when EO fails |
| `mt-sigint-geolocate` | SIGINT Geolocation | Multi-pass TDOA/FDOA convergence |
| `mt-weather-collect` | Weather Collection | Cadence: SoC, eclipse, storage, downlink timing |

### Track B — Red COA library

| ID | Title | Teaches |
|---|---|---|
| `coa-russia-ml` | Russia ML — Sustained EW | Reversible deniable EW from Tirada-2 (SATCOM) and Pole-21 (GNSS); RB-109A Bylina coordinates |
| `coa-russia-md` | Russia MD — DA-ASAT + Cyber | Nudol-class kinetic with cyber surprise |
| `coa-china-ml` | China ML — Early Integrated Disruption | PLA SSF jam + cyber + RPO opening |
| `coa-china-md` | China MD — Decisive Counterspace Strike | Late-crisis A2/AD: kinetic + RPO + cyber + EW |
| `coa-misc-iran-ml` | Iran ML — Regional EW Spoiler | Non-spacefaring adversary contests ground |

### Track C — learning stream

| ID | Title | Teaches |
|---|---|---|
| `learn-intermediate-recovery` | Safe-Mode Recovery | Diagnose attack signature → reset → root-cause patch |

### Track D — novel concepts

| ID | Title | Teaches |
|---|---|---|
| `nv-isl-relay-debris` | ISL Relay + Debris-Corridor Maneuver | Out-of-LOS bird commanded via cross-link |

---

Every vignette is a YAML data file in `spacesim/content/vignettes/` — copy one to author your own.

### Authoring sensors: optional modality fields

Each entry under a vignette's `sensors:` list needs only `id`, `owner`, `kind` (`ground_radar`,
`ground_optical` or `space_based`) and a `location` (ground) or `orbit` (space). Ground optical
sensors also set `needs_lighting: true`: the target must be sunlit and the site dark. The fields
below are all **optional**. Leave a field out and the sensor behaves as it always has. No shipped
vignette uses any of them yet, so they matter only when you author your own.

| Field | Applies to | What it does in the shipped build |
|---|---|---|
| `exclusion_angle_deg` | ground sensors (meant for `ground_optical`) | Removes every instant when the Sun is within this many degrees of the line of sight to the target. Those instants never count as an observation window. |
| `min_range_km` | `space_based` | Removes every instant when the target is closer than this. It is a hard floor, checked before `max_range_m`. |
| `altitude_band_affinity` | observing sensor (meant for `space_based`) | One orbit regime, written exactly as `LEO`, `LEO_SSO`, `MEO`, `GEO`, `HEO` or `CISLUNAR`. When the target is in a different altitude band, the observation's custody gain is **halved**. `LEO_SSO` counts as `LEO`, so a `LEO` sensor is not penalised against a sun-synchronous target. Any other spelling (for example `Leo`) makes **Load** refuse the vignette (see [below](#when-a-vignette-wont-load)). |
| `requires_cue` | any sensor | `true` means the sensor will not look at a target the tasking cell holds no track on. An order that names the sensor is rejected with reason `requires_cue`. An order left on **auto** skips the sensor and uses another one. If every sensor the cell owns needs a cue, the auto order is also rejected `requires_cue`. The dry-run preview shows the same reason. |
| `host_asset_id` | `space_based` (leave out `orbit`) | The sensor rides on that satellite. Its position follows the host's orbit, including after manoeuvres. An observe order may name either the sensor id or the host satellite id, with the same result. |
| `usable_phase_angle_deg` | passive EO only (`needs_lighting: true`) | `[lo, hi]` in degrees, the usable Sun–target–sensor (CATS) phase-angle range. Inside the range the gain is unchanged. Outside it, gain falls off linearly to zero at 0° and at 180°. The angle is taken at the start of the window. A range with `lo > hi`, a bound outside 0–180, or a range on a sensor without `needs_lighting` makes **Load** refuse the vignette (see [below](#when-a-vignette-wont-load)). Suggested values are `[0, 90]` for a ground telescope and `[0, 150]` for a space-based one. There is no default range. |
| `beam_mode` | `ground_radar` | The radar's default mode: `fence` (wide area, half the custody gain) or `dish` (narrow, 1.6 × the gain). An observe order sent with `beam_mode` `fence` or `dish` overrides it for that look. The sensor-tasking panel's **Mode** dropdown does not list the two radar modes. To send one from the console, pick the radar as the actor in the command menu, choose `observe`, and put `{"beam_mode": "fence"}` (or `"dish"`) in its **Advanced (raw JSON params)** box. The HTTP API takes the same field. On a radar, leave the **Mode** dropdown on `auto`, and the sensor's own mode applies. Any other entry replaces the radar's mode with that imaging-radar mode: `spotlight` gives 1.8 × the gain, more than `dish`, and `scan` gives the plain gain. With no mode on the sensor or the order, the radar keeps its usual gain. Any other value on a radar, including `Fence` with a capital letter, makes **Load** refuse the vignette (see [below](#when-a-vignette-wont-load)). |

Range and exclusion fields decide **whether** a window exists. Affinity, phase angle and radar
beam mode decide **how much** custody one look adds. Use the dry-run preview to check that a sensor
you wrote can still find a window before you rely on it in an exercise. If the sensor can never see
the target within the planning horizon (the next 24 hours of sim time), the preview says
`no_window`. `sensor_contended` means it can see the target but is already booked for every
window it found.

> **Sources:** `spacesim/engine/entities.py` (`Sensor`, `_check_usable_phase_angle`,
> `_check_radar_beam_mode`) ·
> `spacesim/engine/access.py` (`_observation_predicate`, `_sensor_orbit`) ·
> `spacesim/engine/orders.py` (`_validate`, `_candidate_sensors`, `_auto_blocked_by_cue`,
> `_plan_collection`, `_resolve_sensor_id`, `_observation_phase_angle_deg`, observe gain and
> radar mode in `_exec_payload`) ·
> `spacesim/engine/isr.py` (`effective_gain`, `altitude_band`, `phase_angle_factor`,
> `BEAM_MODES["ground_radar"]`) ·
> `spacesim/content/vignette.py` (`build_world`, `validate_vignette`) ·
> `spacesim/ui_web/static/app.js` (`composeBody`, `ACTIONS_BY_KIND`) ·
> `spacesim/ui_web/static/index.html` (`#task-beam-mode`, `#o-params`) · FR-1610–FR-1670

### When a vignette won't load

Every vignette is checked in full when you press **Load**. If anything in it is wrong, no session is
made. The session line in the **Cell & Time** panel shows **Load failed:** with one line that names
the first problem, then a list of **every** problem the check found. Each list item gives the place
in the file and the reason, for example:

- `blue_forces[ISR-EO-1].orbit — a satellite must declare an orbit`
- `sensors[s1] — … ground_radar beam_mode must be one of ['dish', 'fence'], got 'Fence'`
- `roles_needed[0].asset_or_constellation — 'nosuch' is not a declared asset or group`

The place reads as *section*`[`*entry id or position*`]`.*field*. Fix every listed item in the
YAML, then press **Load** again. The vignette still appears in the picker while it is broken. The
picker only checks that the file has a `vignette:` block with an `id`, so a broken vignette is
caught at **Load**, not when the list is built.

A refused **Load** changes nothing else. It does not close an open session to make room, and it
does not use up a session number (`sess-N`). A misspelt vignette id is a different error: the
readout says the vignette was not found.

The check refuses a vignette when:

- the file is not valid YAML, or has no `vignette:` block;
- a field has the wrong type, or a value a field does not accept (this includes every sensor-field
  rule in the table above);
- a satellite has no `orbit`, or any other asset has no `location`. A `cyber_unit` is the one
  exception: it needs neither;
- a TLE orbit cannot be read, or cannot be propagated to the vignette's `start_epoch_utc`;
- the same asset id appears twice in `blue_forces`, `red_forces` and `neutral_forces` together, or
  the same sensor id appears twice in `sensors`;
- a `roles_needed` entry names an asset or constellation group the vignette does not declare;
- an `initial_tracks` entry is malformed, or the world cannot be built from the file for any
  other reason (that reason is then listed under `build`).

> **Sources:** `spacesim/content/vignette.py` (`load_vignette`, `validate_vignette`,
> `VignetteValidationError`, `list_vignettes`) · `spacesim/session/inprocess.py` (`load_vignette`:
> session built before any eviction or id use) · `spacesim/ui_web/server.py`
> (`_vignette_load_errors`: 400 `invalid_vignette` / 404) · `spacesim/ui_web/static/app.js`
> (`loadSession`) · FR-5310–FR-5314 · NFR-1600

**Where to find what:**
- **Mission brief panel** (View ▾ → Mission brief, auto-opens on first load) — situation,
  mission, friendly forces, threat picture, ROE, deadline, success criteria, tool tips.
- **Tutorial panel** (View ▾ → Tutorial panel) — per-cell move-by-move script for your current cell.
- [§11 vignette playbooks](11-vignette-playbooks.md) — the same move-by-move script as the
  Tutorial panel, in markdown form for offline review.

---
