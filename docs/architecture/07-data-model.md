# GDS-07 — Data Model

> **Document ID:** GDS-07
> **Version:** 1.1 (2026-10-23, run #217: OQ1–OQ3 decisions recorded). v1.0: run #201.
> **Status:** ✅ Authored — merge gate closed (see "Merge gate" below)
> **Dependencies:** GDS-06
> **Referenced By:** GDS-08
> **Produces:** GDS-08
> **Feature Mapping:** N/A — program-level
> **Related Topics:** [`design/04-data-model.md`](../design/04-data-model.md) (merge source —
> persistence/schema portion, superseded by this document; the conceptual-entity portion went to
> GDS-04), [GDS-04](04-domain-model.md) (the concepts these structures store),
> [GDS-06](06-non-functional-requirements.md) (NFR-3, NFR-12, NFR-13, NFR-15 constrain them),
> ADR-0002, ADR-0007, ADR-0022, ADR-0036, ADR-0038. Absorbs DOM-002 §5 and DOM-004 §4–§5 (see
> "Merge gate").

[↑ Architecture index](INDEX.md) · [Docs index](../INDEX.md)

## Purpose

What SpaceSim stores, in what shape, where, and who reads and writes it. GDS-04 says what each
concept *means*; this document says what fields carry it and what crosses a storage boundary: the
canonical in-memory state, the event log, the files the system reads and writes, and the rules that
keep them valid. It describes the shipped models (`pydantic` v2 in `spacesim/`), summarized as
field groups rather than reproduced as code; the source of truth for an exact field is the model
class this document names.

---

## 1. Representation conventions

- **Time.** Sim time is an integer count of microseconds since the Unix epoch, everywhere inside
  the engine (`engine/simtime.py`), so time arithmetic has no float drift and replay is exact.
  ISO-8601 UTC strings appear only at boundaries: vignette files (`start_epoch_utc`), API responses,
  exports.
- **Units.** SI inside the engine (metres, m/s, seconds); angles in degrees in stored fields whose
  names say so (`i_deg`, `elevation_mask_deg`); delta-v in m/s; power in watts.
- **Identity.** Every entity has a stable string ID chosen by the vignette author (`SAT-7`,
  `STATION-BRAVO`) or minted by a counter for runtime objects (`ord-12`, `ssn-3`, `white-4`).
  Counters are part of state, so IDs replay identically.
- **Models.** Every stored structure is a `pydantic` v2 model, so one definition validates input,
  serializes to JSON or YAML, and round-trips a save. Content files are YAML; save files and API
  payloads are JSON.
- **Ownership.** Each structure belongs to exactly one subsystem, per GDS-03 and ADR-0022: the
  engine owns world state and the event log; the session layer owns sessions, the order and SSN
  registries, and the save-file envelope; content owns the vignette schema.

## 2. Canonical state: `WorldState`

`engine/world.py::WorldState` is the whole ground truth of one exercise at one instant. Everything a
cell sees is derived from it; nothing outside the engine mutates it except through logged events.

| Field | Holds |
|---|---|
| `now` | Current sim time (µs). |
| `assets` | Every satellite, ground station, jammer, interceptor, cyber unit and terrestrial force, by ID (`Asset`). |
| `sensors` | Every observation sensor, ground or space-based (`Sensor`). |
| `tracks` | Each cell's custody records, keyed by owning cell then object (`Track`). |
| `active_effects` | Effects currently in force (`EffectInstance`). |
| `debris` | Debris fields from destructive effects (`DebrisField`). |
| `effect_log`, `consequences` | Resolved-effect history and its political/attribution consequences. |
| `messages` | Messages addressed to a cell (inject text, alerts, results). |
| `mission` | Objective state the vignette's objectives are evaluated against. |
| `ssn_staged` | SSN products collected but not yet delivered. |
| `space_weather` | Current space-weather values and, if declared, the index series (ADR-0039). |
| `conjunctions`, `entities`, `counters` | Conjunction records, generic extra entities, and the ID counters above. |

**Principal entity shapes** (field groups; see the named class for the full list):

- **`Asset`** (`engine/entities.py`): identity (`id`, `owner`, `kind`, `group`, `civilian`);
  position (`orbit` for space assets, `location` for terrestrial ones, `elevation_mask_deg`,
  `mask_table`); resources (`AssetResources`: `delta_v_ms`, `power_w` — a rating, never consumed
  (ADR-0037) — and `ammo`); defense (`hardening`, `cyber_posture`, `cyber_vulnerabilities`,
  `threat_warning`); commanding (`isl_capable`, `isl_peers`, `stored_program`); health (`health`,
  `bus_state`, `payload_state`); drag (`ballistic_coeff_m2_kg`, opt-in).
- **`OrbitState`** (`engine/orbit.py`): `source` (`kepler` for fictional assets, `tle` for real
  ones), `epoch`, Keplerian elements (`a_m`, `e`, `i_deg`, `raan_deg`, `argp_deg`, `ta_deg`), the
  two TLE lines when TLE-sourced, and the derived `regime`.
- **`Sensor`** and **`GroundSite`**: location or orbit, masks and range limits, `health`
  (`nominal`/`degraded`), and the six optional modality fields from IP-1220 (`beam_mode`,
  `exclusion_angle_deg`, `min_range_km`, `altitude_band_affinity`, `requires_cue`, `host_asset_id`)
  plus `usable_phase_angle_deg`.
- **`BusState`** (`engine/bus.py`): one block per subsystem (power, attitude, thermal, propulsion,
  C&DH, comms), the bus `mode`, a `SafeModeState` (cause as truth, the defender's diagnosis
  separately, recovery progress), and `last_telemetry_time` — which is what makes the ground view
  stale between passes.
- **`PayloadState`**: generic payload status plus exactly one typed sub-model matching `type`
  (`satcom`, `isr_eo`, `isr_sar`, `sigint`, `sda`, `weather`, `mw`, `pnt`), auto-populated with an
  authored default and never overwriting an authored value.
- **`Track`** (`engine/custody.py`): the owning cell's belief about one object — `confidence`
  (decays on read), `characterized`, `classification`, `state_estimate` (an `OrbitState` that may be
  stale), uncertainty, `source`, and the last collection's footprint and beam mode. A
  weapons-quality track is `confidence ≥ threshold` and `characterized`.
- **`EffectInstance`** (`engine/effects.py`): template, five-D category, segment, actor, target,
  reversibility and kinetic flags, debris risk, attribution, escalation weight, gating access
  channel, intended outcome, cyber fields (`access_vector`, `success_prob`, `persistence_s`), the
  active window, and the issuing order's action type.

## 3. The event log

`engine/eventlog.py` holds the record that makes the state reproducible (NFR-3, NFR-12).

- **`EventLogEntry`**: `seq` (strict order), `sim_time`, `kind`, `actor` (`blue`, `red`, `white`,
  `system`), `payload` (the action, inject or result) and `reversible_undo`. Handlers may enrich a
  payload in place before it is logged (an executed manoeuvre records `applied` and
  `remaining_delta_v_ms`), so the log carries outcomes as well as intents.
- **Kinds.** Scheduled kinds include `bus_tick`, `execute_effect`, `inject`, `inject_admin`,
  `condition_check`, `env_anomaly_check`, `ssn_collect`, `ssn_deliver`, `recovery_confirm` and
  `recovery_finish`; logged control kinds include `roe_change`, `effect_gate_request`,
  `effect_gate_decision` and `handler_error` (ADR-0038's no-op failure record).
- **`Snapshot`**: `seq`, `sim_time`, a full serialized `WorldState` and the RNG state, used by the
  engine to speed rewind and replay. Snapshots are an optimization: state at any point is defined
  by replaying the log from the initial state, never by trusting a snapshot.
- **RNG state** is part of persisted state (`engine/rng.py::SeededRng` is serializable), so a
  replay draws the same numbers in the same order.

## 4. What is stored, where

| Artifact | Format | Location | Written by | Read by | Notes |
|---|---|---|---|---|---|
| **Vignette** | YAML | `spacesim/content/vignettes/`, configured external directories, the configured user-save directory | Authors; `vignette_export.save_vignette` (Vignette Creator, save-as-scenario) | `content/vignette.py::load_vignette` | §5 |
| **Save file** | JSON | Downloaded by the facilitator (`GET /api/sessions/{sid}/save`) | `SessionManager.save_state` | `InProcessSession.load_save` → `SessionManager.from_state` | §6 |
| **Inject library** | YAML | `spacesim/content/inject_library.yaml` | Authors | White Cell inject builder | Five reusable templates. |
| **Configuration** | YAML | `spacesim.config.yaml` (or `SPACESIM_CONFIG`) | Facilitator | `spacesim/config.py` | `ServerConfig` (host, port, reload) and optional `ContentConfig` (external vignette dirs, user-save dir). Absent file means defaults. |
| **Base map** | JSON | `spacesim/ui_web/static/world.json` (committed) | `tools/build_coastlines.py`, offline | Browser map and globe | Static coastlines and borders. |
| **Exports** | CSV, CCSDS OEM, TLE text, JSON | Returned to the browser for download | Session-layer export functions | The user | §7 — derived and write-only; never read back by the system. |

Nothing else is persisted. In particular there is no database, no user or trainee record, and no
server-side store of saves: a save exists only as the file the facilitator downloaded.

## 5. Vignette file

`content/vignette.py::Vignette` is the loadable scenario. Field groups:

- **Identity and framing:** `id`, `title`, `classification`, `learning_objectives`,
  `doctrinal_basis`, `estimated_duration_min`, `intro_brief` (per cell), `tutorial`, `coaching`.
- **Setting:** `start_epoch_utc`, `geography`, `orbital_environment`, `red_doctrine_profile`.
- **Forces:** `blue_forces`, `red_forces`, `neutral_forces` (each a list of inline `Asset`
  definitions — there are no asset templates; ADR-0036), `sensors`.
- **Rules and dials:** `objectives`, `escalation_thresholds`, `parameters` (typed White Cell dials:
  `Parameter` = id, label, type, options/min/max, default, affects), `roe` (optional per-cell;
  absent means the legacy flat flags apply to both cells), `effect_gating_rules`,
  `effect_detectability_config`.
- **Events:** `injects` (`Inject` = id, label, trigger — time or condition — effects, repeatable).
- **Staffing:** `roles_needed` (`RoleRequirement` = asset or constellation, role, mandatory).
- **Environment:** `initial_space_weather`, `space_weather_series`, `environmental_anomalies`.
- **Carried-forward state** (save-as-scenario only): `initial_tracks`, `simulator_version`.

`build_world()` turns a vignette plus parameter values into the initial `WorldState` and a
`VignetteContext` (start epoch, resolved parameter values, per-cell ROE, objectives, SSN networks,
gating and detectability rules). Every optional field is additive: absent, it changes nothing, so
every shipped vignette loads and behaves identically when the schema grows (NFR-7, `NFR-2010`).

## 6. Save file

The save is an envelope around the event log, not a dump of world state. `SessionManager.save_state`
writes:

| Key | Holds |
|---|---|
| `vignette_id` | Which vignette to reload. **The vignette itself is not embedded** (see OQ1). |
| `overrides`, `classification` | White Cell parameter values and the classification banner. |
| `seed`, `final_time`, `started` | RNG seed, the sim time saved at, whether the exercise had started. |
| `eventlog` | The full `EventLog`. |
| `pending` | Scheduled-but-unfired events (time, kind, actor, payload, tag). |
| `orders`, `ssn_requests` | The order registry and SSN request registry, with their states. |

**Resume** reloads the vignette by ID, rebuilds the world by replaying the event log to
`final_time` (the deterministic core makes this exact), re-schedules the pending events, and
restores both registries and their ID counters. A loaded event log longer than
`MAX_EVENTLOG_REPLAY_ENTRIES` (100,000) is refused before any replay (NFR-15).

A second, engine-level save shape exists: `engine/simulation.py::SavedSession` (initial state,
seed, final time, snapshots, event log). Only the determinism test uses it; the web save path does
not (see OQ3).

## 7. Exports (derived, write-only)

Each export is computed from replayed state at request time and handed to the user; none is read
back. All time-span exports share one sampling choke point (`ephemeris.sample_times`) and the
`MAX_EXPORT_SAMPLES` cap (NFR-15).

| Export | Format | Source |
|---|---|---|
| AAR timeline | CSV | `session/aar.py::export_csv` |
| Per-asset telemetry over a span | CSV | `SessionManager.telemetry_export` (values from `engine/telemetry.py::sample`) |
| Truth and cell-observed ephemeris | CSV, CCSDS OEM | `session/ephemeris.py` (ECI or RIC frame) |
| Manoeuvre ledger | CSV | `SessionManager.maneuver_ledger` |
| Current-epoch TLE | TLE text | `session/ephemeris.py::quick_tle` → `engine/tle_export.py` |
| Research runs | CSV, JSON | `session/research_export.py` (`RunRecord`) |
| Vignette (save-as-scenario) | YAML | `content/vignette_export.py` (§5) |

**Fog of war applies to exports.** A cell's export reads only its own assets and its own
`Track.state_estimate`; only White Cell's exports read ground truth.

## 8. Research and assessment records

*(Absorbs DOM-004 §4–§5 and DOM-002 §5.)*

- **The event log is the research record.** Because it is complete and deterministic (NFR-3,
  NFR-12), a run is fully described by vignette + parameter values + seed + event log: a
  researcher varies one input and replays, and nothing needs hand-coding by an observer.
- **`RunRecord`** (`session/research_export.py`) is one row per run: `vignette_id`, `seed`,
  `condition_label`, and the assessment report verbatim. `spacesim/tools/research_batch.py` produces one per
  seed from a fresh, isolated session.
- **The assessment report is a rubric, never a single score.** Each dimension (custody quality,
  window discipline, belief-truth divergence) is reported on its own scale; no composite is stored
  or exported, because the dimensions are not commensurable. Any aggregation for a study is an
  analysis step outside the instrument (ADR-0032).
- **Belief at decision time is recorded, not recomputed.** An order's execution payload carries
  `custody_confidence_at_decision`, captured at issue time, and assessment reads it back verbatim.

## 9. Derived views (computed, never stored)

`CellView`, the render-from-custody scene, telemetry samples and the telemetry "database" per
subsystem, `dry_run()` results, RIC views and the controller view are computed from `WorldState`
on each read and never persisted. Each is replay-safe (NFR-13). A cell's view is produced only at
the `SessionAPI`/`CellController` boundary (ADR-0004); White Cell's god-view and the named
ground-truth reads (`FR-6220`) are the only unfiltered paths.

## 10. Validation rules (as built)

- **At load** (`load_vignette`, FR-5310ff.): every problem is collected and the load refused as a
  whole with `VignetteValidationError` (400 `invalid_vignette`), leaving the session registry
  untouched. Checked: each entity's own validators; a space asset has an orbit and a terrestrial
  asset a location (cyber units exempt); TLEs parse and propagate; IDs are unique; `roles_needed`
  refers to real assets; `build_world` succeeds; space-weather series are physical.
- **Paths:** vignette IDs and save targets pass the traversal guard before any filesystem access
  (`NFR-3700`).
- **At order issue and again at execute:** ownership, access window or delivery path, resources
  (delta-v cannot go negative; an engage salvo cannot exceed rounds left), ROE per issuing cell at
  the order's own issue time, the weapons-quality gate for engagements, and any matching gating rule
  (ADR-0005; GDS-05 FR-P).
- **Injects:** a malformed inject, or one whose effect's precondition fails, is refused atomically
  before it is scheduled.

---

## Departures from the legacy `design/04-data-model.md`

The GDS level is authoritative; these are stated so they are not mistaken for drift:

- **No asset templates.** `design/04` gives each asset a `template` reference and each template a
  `telemetry_db` and `command_db`. As built, assets are defined inline in the vignette (ADR-0036);
  the telemetry database is computed per subsystem at read time (`engine/telemetry.py`); the command
  catalog is code (`engine/buscommands.py`).
- **Flattened asset fields.** The `posture` and `comms` blocks became top-level fields (`hardening`,
  `cyber_posture`, `isl_capable`, `isl_peers`, `stored_program`); `provides` and `ground_segment`
  were not built.
- **Sensors.** `fov_deg`, `capabilities`, `task_capacity`, `current_tasks` and a
  `up/degraded/down` status were not built; sensors carry range limits, a `network`, a
  `nominal/degraded` health and the IP-1220 modality fields. Tasking contention is computed by the
  order system, not stored on the sensor.
- **Planned activities.** `design/04`'s `PlannedActivity` with a seven-state lifecycle is, as built,
  `engine/orders.py::Order` with statuses `draft`, `queued`, `rejected`, `cancelled`, `executed`,
  plus `pending_approval` for gated orders; collection tasking is an `observe` order.
- **Effect outcomes** are not a stored type: results go to the event log, `effect_log` and
  `consequences`.
- **Time** is integer microseconds, not ISO strings or float seconds.

## Open Questions

- **OQ1–OQ3 decided 2026-10-23** (pipeline run #217; to take effect when the self-contained save ships). OQ1: the owner chose to embed (`BL-0302`, "save the active state in the scenario regardless of original vignette file"), elaborated as [FS-110](../features/FS-110-save-and-resume.md) v2.0 Design Decisions 1–2: the save carries its replay baseline (the loaded vignette plus every White Cell force edit folded in) in vignette form, and resume reads only the save (`FR-7230`). OQ2: FS-110 Decision 3 — saves carry a save-format version and the simulator version; a save with no format version resumes by vignette ID as today; a simulator-version mismatch warns, never refuses. OQ3: FS-110 Decision 4 — `SavedSession` stays as it is (the determinism test's shape); no convergence. §6 is updated to the new envelope when the package that builds it is verified. The three entries below are kept as the question record.
- **OQ1 — Saves do not embed their vignette.** Resume reloads the vignette by ID, so a save made
  against a vignette that is later edited, renamed or removed either fails to load or, worse,
  replays against different initial conditions without warning. Options: embed the vignette (or a
  content hash) in the save, or refuse to resume on a hash mismatch. Needs an owner decision.
- **OQ2 — No format version on save files.** A save carries no schema or simulator version
  (only exported vignettes carry `simulator_version`), so a save from an older build cannot be
  recognized as such. Should saves carry `simulator_version` and a format version?
- **OQ3 — Two save shapes.** `SavedSession` (engine) and `save_state` (session) both describe "a
  saved run". Keep both (engine-level for tests, envelope for the web), or converge on one?
- **OQ4 — No persistent learner identity.** DOM-002 §7 asks for per-trainee competency reporting
  across exercises. Nothing stores a trainee identity or links runs over time; `RunRecord` is per
  run and per cell. This is a capability gap, not a data-model defect, and it is a feature
  decision (FS-201 scope), recorded here so the data model does not imply it exists.

## Merge gate (closed)

- [x] **Absorbed the persistence/schema content of `design/04-data-model.md`.** §1 (identifiers and
  units) → §1; §2 (`OrbitState`) and §3 (assets, ground stations, sensors) → §2; §4 (effects) → §2
  and the departures list; §5 (tracks) → §2; §6 (vignette schema) → §5; §6.5 (planned activities) →
  §2 and departures; §7 (event log, snapshot) → §3, with the save envelope added in §6; §8 (cell
  view) → §9; §9 (validation rules) → §10, updated to as-built. Each was checked against the shipped
  `pydantic` models, and every difference is listed under "Departures".
- [x] **Split drawn consistently with GDS-04.** GDS-04 keeps concepts and relationships; this
  document holds field groups, formats, locations and validation, and points back to GDS-04 rather
  than restating what each entity means.
- [x] **DOM content absorbed (`BL-0293`).** Absorbed: DOM-004 §4 (the event log as reproducible,
  complete research record) and §5 (research export with run metadata, now `RunRecord`) into §8;
  DOM-002 §5 (rubric, never a single score) into §8. Recorded as a gap rather than absorbed: DOM-002
  §7 (longitudinal per-trainee reporting) → OQ4. No other DOM section has data-model content.
- [x] **Decision recorded:** **this document is the authoritative data model**, and
  `design/04-data-model.md` is superseded in full: GDS-04 already took its conceptual portion, and
  this document takes its schema portion, corrected to the shipped models. `design/04` is not
  edited here; it retires with the rest of `docs/design/` (apart from the ICD) once GDS-10 closes
  (`BL-0292`). This departs from GDS-04's own merge decision, which kept `design/04` authoritative
  for the schema: that decision predates the owner's 2026-10 instruction to retire `design/` with
  build-spec, and with both halves now absorbed nothing in `design/04` remains authoritative.

## Next

`GDS-08` (UI Architecture) may now begin. OQ1–OQ3 are for an owner decision; OQ4 belongs to
FS-201's scope.
