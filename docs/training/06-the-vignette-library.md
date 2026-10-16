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
| `altitude_band_affinity` | observing sensor (meant for `space_based`) | One orbit regime, written exactly as `LEO`, `LEO_SSO`, `MEO`, `GEO`, `HEO` or `CISLUNAR`. When the target is in a different altitude band, the observation's custody gain is **halved**. `LEO_SSO` counts as `LEO`, so a `LEO` sensor is not penalised against a sun-synchronous target. Any other spelling (for example `Leo`) stops the vignette from building a session. |
| `requires_cue` | any sensor | `true` means the sensor will not look at a target the tasking cell holds no track on. An order that names the sensor is rejected with reason `requires_cue`. An order left on **auto** skips the sensor and uses another one. If every sensor the cell owns needs a cue, the auto order is also rejected `requires_cue`. The dry-run preview shows the same reason. |
| `host_asset_id` | `space_based` (leave out `orbit`) | The sensor rides on that satellite. Its position follows the host's orbit, including after manoeuvres. An observe order may name either the sensor id or the host satellite id, with the same result. |
| `usable_phase_angle_deg` | passive EO only (`needs_lighting: true`) | `[lo, hi]` in degrees, the usable Sun–target–sensor (CATS) phase-angle range. Inside the range the gain is unchanged. Outside it, gain falls off linearly to zero at 0° and at 180°. The angle is taken at the start of the window. A range with `lo > hi`, a bound outside 0–180, or a range on a sensor without `needs_lighting` stops the vignette from building a session. Suggested values are `[0, 90]` for a ground telescope and `[0, 150]` for a space-based one. There is no default range. |
| `beam_mode` | `ground_radar` | The radar's default mode: `fence` (wide area, half the custody gain) or `dish` (narrow, 1.6 × the gain). An observe order sent with `beam_mode` `fence` or `dish` overrides it for that look. Only the HTTP API can send this, because the console's **Beam mode** dropdown does not list the two radar modes. Leave the dropdown on `auto` and the sensor's own mode applies. With no mode on the sensor or the order, the radar keeps its usual gain. Any other value on a radar, including `Fence` with a capital letter, stops the vignette from building a session. |

Range and exclusion fields decide **whether** a window exists. Affinity, phase angle and radar
beam mode decide **how much** custody one look adds. Use the dry-run preview to check that a sensor
you wrote can still find a window before you rely on it in an exercise. If the sensor can never see
the target in the look-ahead, the preview says `no_window`. `sensor_contended` means it can see the
target but is already booked for every window it found.

> **Sources:** `spacesim/engine/entities.py` (`Sensor`, `_check_usable_phase_angle`,
> `_check_radar_beam_mode`) ·
> `spacesim/engine/access.py` (`_observation_predicate`, `_sensor_orbit`) ·
> `spacesim/engine/orders.py` (`_validate`, `_candidate_sensors`, `_auto_blocked_by_cue`,
> `_plan_collection`, `_resolve_sensor_id`, `_observation_phase_angle_deg`, observe gain and
> radar mode in `_exec_payload`) ·
> `spacesim/engine/isr.py` (`effective_gain`, `altitude_band`, `phase_angle_factor`,
> `BEAM_MODES["ground_radar"]`) ·
> `spacesim/content/vignette.py` (`build_world`) · FR-1610–FR-1670

**Where to find what:**
- **Mission brief panel** (View ▾ → Mission brief, auto-opens on first load) — situation,
  mission, friendly forces, threat picture, ROE, deadline, success criteria, tool tips.
- **Tutorial panel** (View ▾ → Tutorial panel) — per-cell move-by-move script for your current cell.
- [§11 vignette playbooks](11-vignette-playbooks.md) — the same move-by-move script as the
  Tutorial panel, in markdown form for offline review.

---
