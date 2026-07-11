# Data Model — Entities, Assets, Actions, Schemas

This is the contract for state. All types are intended as `pydantic` models so they validate and
(de)serialize cleanly to/from YAML content files and JSON save files. Times are simulated UTC.

## 1. Core identifiers and units
- `SimTime` — simulated UTC instant (store as ISO-8601 / epoch seconds).
- IDs are stable strings: `AssetId`, `TargetId`, `StationId`, `SensorId`, `OrbitId`.
- Units: SI in the engine (meters, m/s, seconds, radians internally; degrees at the UI boundary).
- Delta-v in m/s; power in watts; angles documented per field.

## 2. Orbit & geometry

```yaml
OrbitState:
  source: kepler | tle           # fictional assets use kepler; real ones use tle
  epoch: SimTime
  # Keplerian (fictional / moderate):
  a_m:        # semi-major axis (m)
  e:          # eccentricity
  i_deg:      # inclination
  raan_deg:   # right ascension of ascending node
  argp_deg:   # argument of perigee
  ta_deg:     # true anomaly at epoch
  # TLE (real named satellites added by White Cell):
  tle_line1:  # optional
  tle_line2:  # optional
  regime: LEO | LEO_SSO | MEO | GEO | HEO | CISLUNAR   # derived, cached
```

`ECIState` (engine-internal): position+velocity vectors at a time; `GeoPoint`: lat/lon/alt.

## 3. Assets (instances created from templates)

```yaml
Asset:
  id: SAT-7
  name: "BLUEEYE-1"              # White Cell may set a real name
  owner: blue | red | neutral
  template: ISR_EO              # references an asset_template (see research file 05)
  kind: satellite | ground_station | sensor | jammer | interceptor | directed_energy | cyber_unit | terrestrial_force
  orbit: OrbitState | null       # null for terrestrial assets
  location: GeoPoint | null      # for terrestrial assets/stations
  provides: [imagery]            # services to terrestrial forces
  resources:
    delta_v_ms: 150              # remaining maneuver budget (satellites)
    power_w: 2000
    ammo: 0                      # interceptors/escorts
  posture:                       # passive/active defense toggles (Blue loadout)
    maneuver: true
    deception: true
    hardening: false
    dispersal: false
    redundancy: false
  health: nominal | degraded | destroyed
  ground_segment: [STATION-A, PROC-CENTER-1]   # for satellites
  comms:                          # how this satellite can receive commands
    isl_capable: false            # can relay/receive via inter-satellite link
    isl_peers: []                 # asset ids it can crosslink with (geometry permitting)
    stored_program: true          # accepts time/condition-triggered onboard commands
  bus_state:                      # live state-of-health (see ../research/06); pass-gated to UI
    power:      {battery_soc: 0.0..1.0, in_eclipse: false, status: green}
    attitude:   {pointing_ok: true, mode: nominal, status: green}  # mode: nominal|slew|safe
    thermal:    {status: green}
    propulsion: {propellant_frac: 1.0, status: green}
    cdh:        {storage_frac: 0.0, fsw_mode: nominal, status: green}
    comms:      {uplink_lock: false, downlink_lock: false, status: green}
    mode: nominal                 # nominal | safe_mode (safe_mode disables the payload)
    safe_mode:                    # full attack/detection/recovery loop — see 12-safe-mode-loop.md
      active: false
      entered_at: SimTime | null
      cause: null                 # fault|environment|cyber|ew|bus_stress (truth; White-Cell-visible)
      defender_confirmed: false   # has the defender confirmed via a contact?
      defender_diagnosis: unknown # unknown|suspected_attack|fault|<subsystem>
      recovery: {plan: [PlannedActivity...], step_index: 0, passes_used: 0, blocked_reason: null}
    last_telemetry_time: SimTime  # when ground last received FRESH soh (between passes = stale)
  payload_state:                  # shape varies by payload type (see ../research/06 §2)
    type: satcom|isr_eo|isr_sar|sigint|sda|space_control|pnt|missile_warning|weather
    health: green                 # green|yellow|red
    detail: {...}                 # type-specific: transponders / collection_queue / tasking / effector
  cyber:                          # for assets with a network attack surface
    vulnerabilities: [{vector: ground_modem, patchable: true, patched: false}]
    posture: medium
```

Each asset **template** also carries a `telemetry_db` (every SOH/payload parameter, its units,
and soft/hard alarm limits — drives the UI displays and alarms) and a `command_db` (legal
commands, their arguments, and pre-release constraints — the authoritative list of what the
order panel may offer). These mirror the real telemetry/command databases at the heart of
mission-control software (see `../research/06-bus-and-payload-operations.md` §3).

### Ground stations & sensors
```yaml
GroundStation:
  id: STATION-BRAVO
  owner: blue
  location: GeoPoint
  elevation_mask_deg: 7
  channels: [command_uplink, telemetry_downlink]
  status: up | degraded | down

Sensor:
  id: RADAR-1
  owner: blue
  kind: ground_radar | ground_optical | space_based
  location: GeoPoint | null      # null if space-based (then has orbit)
  orbit: OrbitState | null
  fov_deg: ...
  needs_lighting: false          # true for optical: needs target sunlit + site in darkness
  weather_sensitive: false       # true for optical: cloud/space-weather can deny
  capabilities: [detect, track, characterize]   # what yields it can produce
  task_capacity: 1               # how many simultaneous tasks (contention/prioritization)
  current_tasks: []              # references to active collection_tasks
  status: up | degraded | down
```
Space-based SDA sensors and coalition/shared feeds are modeled here too: a `space_based`
sensor has an `orbit` and is constrained by its own passes; a shared feed is represented as a
low-control sensor that periodically injects external `Track` updates. See
`11-command-planning-and-tasking.md` Part B for the tasking workflow.

## 4. Effects & weapons (templates → instances)

Effect templates come from `../research/03-counterspace-taxonomy.md`. An **EffectInstance** is a
template applied by an actor to a target:

```yaml
EffectInstance:
  template: ew_uplink_jam        # references an effect_template
  category: electronic_warfare   # direct_ascent|co_orbital|electronic_warfare|directed_energy|cyber
  segment: link                  # orbital|link|terrestrial
  actor: JAMMER-2
  target: SAT-9 | USER-AREA-3 | STATION-RED-1
  reversible: true
  kinetic: false
  debris_risk: none              # none|low|high
  attribution: ambiguous         # overt|ambiguous|covert
  escalation_weight: 3
  requires: jam_footprint        # access channel that gates it (none for cyber)
  intended_outcome: deny         # deceive|disrupt|deny|degrade|destroy
```

```yaml
EffectOutcome:
  achieved_outcome: deny | degrade | none | ...
  success: true
  side_effects:
    - {type: spawn_debris, region: {...}}        # kinetic only
    - {type: consume, resource: power_w, amount: ...}
    - {type: custody_change, object: SAT-9, delta: ...}
    - {type: attribution_signal, to: blue, confidence: 0.4}
    - {type: political_consequence, severity: high}
```

## 5. SDA custody / tracks
```yaml
Track:
  object: RED-OBJ-1
  owner: blue                    # who holds this track
  last_observation: SimTime
  confidence: 0.0..1.0           # decays over time; reset by observation window
  characterized: false           # has the object's purpose been determined?
  classification: unknown        # friend|hostile|neutral|unknown (affiliation for symbology)
  state_estimate: OrbitState     # may be stale/uncertain
  uncertainty:                   # drives the 3D viewer's growing ellipsoid (10-sda-3d-viewer)
    along_track_km: 0.0          # grows with time-since-observation (v1: simple growth model;
    radial_km: 0.0               #   later: true covariance from an estimator)
    cross_track_km: 0.0
  source: own_sensor | coalition_feed | inferred
```
A "weapons-quality track" exists when `confidence ≥ threshold` AND `characterized`. Other
subsystems read this gate before allowing an engagement. The viewer renders this object with a
solidness/ghosting and an uncertainty volume derived from `confidence` and `uncertainty`.

## 6. Vignette, parameter, inject (content schema)
Defined in `../vignettes/00-vignette-framework.md`; summarized here as the loadable shape:
```yaml
Vignette:
  id, title, classification, learning_objectives[], doctrinal_basis[]
  red_doctrine_profile: china_integrated | russia_ew_first | generic
  start_epoch_utc, geography, orbital_environment
  blue_forces: [Asset...], red_forces: [Asset...], neutral_forces: [Asset...]
  objectives: {blue:[Objective], red:[Objective]}
  escalation_thresholds: {...}
  parameters: [Parameter...]     # the White Cell dials (typed)
  injects: [Inject...]
  roles_needed: [RoleRequirement...]  # IP-1151 (FR-4210) — optional; absent/empty means no
                                       # mandatory staffing requirement (every vignette shipped
                                       # before this package). See RoleRequirement below.
  roe: {blue: {kinetic_authorized, cyber_authorized}, red: {...}}  # IP-1172 (FR-3420, NFR-2010) —
                                       # optional per-cell ROE; absent means the legacy flat
                                       # red_kinetic_authorized/cyber_authorized parameters apply
                                       # identically to both cells (every vignette shipped before
                                       # this package). A missing cell/sub-key in an explicit block
                                       # defaults to false (fail safe).
```

```yaml
RoleRequirement:                 # IP-1151 (FR-4210) — a seat/role staffing requirement
  asset_or_constellation: str
  role: bus | payload | both     # default "both"
  mandatory: bool                # default true
```
A White-Cell-facing seat-assignment step (`session/manager.py`'s Role Assignment registry) binds
seats to `{asset_or_constellation, role}` against a vignette's declared `roles_needed`; an unmet
`mandatory` entry hard-blocks `Start` (`SessionManager.staffing_report()`, gated in
`InProcessSession.start()`). Runtime enforcement of an assigned Role Assignment's scope is
[FS-105](../features/FS-105-spacecraft-operations.md)'s concern, not produced by this schema.

`content/vignette.py`'s `build_world()` resolves `roe` into `VignetteContext.roe`, always a fully
cell-keyed `{"blue": {...}, "red": {...}}` dict regardless of which of the two paths above produced
it — `engine/orders.py`'s `OrderSystem` never sees or branches on the legacy-vs-explicit distinction
(IP-1172, FR-3420/NFR-2010).

```yaml
PayloadState:                    # engine/bus.py — one Optional typed sub-model per payload type
  type: str                      # satcom | isr_eo | isr_sar | sigint | sda | weather | mw | pnt | ...
  satcom: {bandwidth_class, data_rate_kbps_max}                     # IP-1171 (FR-5170), R110
  isr_eo: {swath_km, resolution_m, power_factor, duty_cycle, gain_factor}   # R109
  isr_sar: {swath_km, resolution_m, power_factor, duty_cycle, gain_factor}  # R109
  sigint: {band, mode}                                              # R129 (via engine/sigint.py)
  sda: {swath_km, resolution_m, power_factor, duty_cycle, gain_factor}      # R109
  weather: {swath_km, resolution_m, power_factor, duty_cycle, gain_factor}  # R109 (GOES-R ABI)
  mw: {swath_km, resolution_m, power_factor, duty_cycle, gain_factor}       # R109 (SBIRS-GEO)
  pnt: {baseline_accuracy_m}                                        # R134 (GPS SPS ≤9m/95%)
```
`PayloadState`'s `_populate_typed_params` validator auto-populates exactly the one field matching
`type` with that type's R109/R110/R129/R134-grounded default (an *authored* baseline, distinct from
`engine/isr.py`'s `BEAM_MODES` runtime table an operator selects among at order-issue time) — every
other of the 8 fields stays `None`, and an explicit vignette-authored value is never overwritten
(IP-1171, FR-5170). `FR-5180`'s bus power/propulsion authoring needed no schema change:
`Asset.model_validate()` already routes a vignette's per-asset `resources.delta_v_ms` /
`bus_state.power.charge_rate_per_s`/`drain_rate_per_s` overrides to the live fields `advance_bus()`
reads — `AssetResources.power_w` is confirmed never written by this path (IP-1171, FR-5180).

## 6.5 Planned activities (commands & collection tasks share one scheduler)
Both "command a satellite" and "task a sensor" are **planned activities** scheduled against
access windows. Implement them on one scheduler with two `kind`s so the queue, timeline,
undo, and time-travel work identically for both (see `11-command-planning-and-tasking.md`).

```yaml
PlannedActivity:
  id:
  kind: command | collection
  actor_ref:                     # asset (command) or sensor (collection)
  intent:                        # command verb OR collection intent (search|track|characterize|cue)
  params: {...}
  delivery:                      # how/when it reaches the actor
    path: ground_uplink | isl_relay | stored_program | sensor_collect
    via: STATION-BRAVO | SAT-RELAY-2 | onboard | RADAR-1
    scheduled_window: {start_utc, end_utc}   # computed from geometry; null for stored/cyber
  priority: routine | priority | immediate
  state: DRAFT | PLANNED | ACTIVE | EXECUTED | REPORTED | FAILED | CANCELLED
  fail_reason: null
  depends_on: [activity_id]      # optional chaining into a multi-step plan
```
Validation at accept-time and again at execute-time: ownership, a valid window/delivery path,
resources, ROE/authorities, and (for engagements) the weapons-quality track gate.

## 7. Session & event log
```yaml
EventLogEntry:
  seq: int                       # strict ordering
  sim_time: SimTime
  kind: order | order_result | inject | white_control | maneuver_complete | window_open | ...
  actor: red | blue | white | system
  payload: {...}                 # the action/inject/result
  reversible_undo: bool          # can White Cell undo this cleanly?

Snapshot:
  sim_time: SimTime
  world_state: WorldState        # full serialized state
  rng_state: ...
```

## 8. Fog-of-war view model (what a cell is allowed to see)
The engine holds ground truth; `CellController` produces a **filtered view** per cell:
```yaml
CellView:
  cell: blue
  own_assets: [full detail]
  known_tracks: [Track...]       # only objects this cell has custody of (per fog setting)
  visible_effects: [...]         # effects this cell can perceive/attribute given attribution rules
  windows: [AccessWindow...]     # upcoming windows for own assets
  messages: [...]                # injects/alerts addressed to this cell
```
White Cell's view is god-view (ground truth + both cells' views). Hidden parameters (e.g.,
`red_intent`) are visible only to White.

## 9. Validation rules (pydantic validators to implement)
- A satellite asset must have an `orbit`; a terrestrial asset must have a `location`.
- `delta_v_ms` cannot go negative; maneuvers exceeding budget are rejected at order validation.
- Kinetic effects must set `debris_risk` and are blocked unless the vignette ROE authorizes them.
- TLE-sourced orbits must parse; on failure, reject the asset with a clear error (White Cell UI
  surfaces it when importing real satellites).
