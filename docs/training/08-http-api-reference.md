[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 9. HTTP API reference

All UI actions go through these endpoints (base `http://127.0.0.1:8000`). Reads are fog-filtered
per cell, server-side.

| Method & path | Purpose |
|---|---|
| `GET /api/vignettes` | List the scenario library |
| `POST /api/sessions` `{vignette_id, overrides, seed}` | Load a scenario → returns a session id |
| `POST /api/sessions/{sid}/param` `{param_id, value}` | Set a dial (before start) |
| `POST /api/sessions/{sid}/start` | Start the exercise |
| `POST /api/sessions/{sid}/step` `{dt_sim_s}` / `…/advance` `{t}` | Advance time |
| `POST /api/sessions/{sid}/rewind` `{t}` · `…/undo` `{n}` | Time travel |
| `POST /api/sessions/{sid}/inject` `{inject, at_sim_t?}` | Fire an inject (id or `{effects}`); `at_sim_t` (µs UTC) schedules for later |
| `GET /api/sessions/{sid}/inject_library` | List reusable inject templates from `content/inject_library.yaml` |
| `POST /api/sessions/{sid}/order` `{cell, actor, action, target, params}` | Issue an order |
| `POST /api/sessions/{sid}/order/validate` `{...}` | Dry-run an order — returns `ok`/`reason` without mutating state |
| `POST /api/sessions/{sid}/preview/consequence` `{...}` | Severity / escalation / reversibility / attribution preview |
| `POST /api/sessions/{sid}/maneuver/compute` `{cell, actor, mode, params}` | Maneuver assistant: ECI/LVLH/finite_burn/target_coe/hohmann/plane_change |
| `POST /api/sessions/{sid}/jam/compute` `{cell, actor, params}` | Jam preview: effective radius + footprint polygon + Pₛ |
| `POST /api/sessions/{sid}/engage/compute` `{cell, actor, target, params}` | Engage preview: closing geometry + Pₖ + debris-cone |
| `POST /api/sessions/{sid}/cyber/compute` `{cell, actor, target, params}` | Cyber preview: vector × payload × posture → success/detect/attribution |
| `POST /api/sessions/{sid}/sigint/compute` `{cell, actor, params}` | SIGINT preview: band × mode × dwell → geolocation error |
| `GET /api/sessions/{sid}/orders/{cell}` · `POST …/cancel` `{cell, order_id}` | Command queue · cancel a queued order |
| `GET /api/sessions/{sid}/windows/{cell}/{asset}` | Upcoming passes (pass-timeline ribbon — cmd/tlm/obs lanes) |
| `GET /api/sessions/{sid}/conjunctions/{cell}` | Upcoming close approaches (filtered by ownership) |
| `GET /api/sessions/{sid}/coaching/{cell}` | Coaching notes from `vignette.coaching` due-now for this cell |
| `GET /api/sessions/{sid}/activity/{cell}?past_window_s&future_window_s` | Per-cell Gantt feed (past · present · scheduled). White=all cells; Blue/Red=own only |
| `GET /api/sessions/{sid}/injects` | List the vignette's injects |
| `POST /api/sessions/{sid}/force/tle` `{id, owner, line1, line2}` | Add a real satellite by TLE |
| `POST /api/sessions/{sid}/red_step` | AI-Red issues one doctrine round |
| `GET /api/sessions/{sid}/view/{cell}` | Fog-filtered cell view |
| `GET /api/sessions/{sid}/scene/{cell}` | Belief-render geometry (map/3D) |
| `GET /api/sessions/{sid}/telemetry/{cell}/{asset}[/{param}]` | Subsystem telemetry DB · a parameter series |
| `GET /api/sessions/{sid}/alarms/{cell}` | Fleet alarms / event feed |
| `GET /api/sessions/{sid}/godview` | Ground truth (White only) |
| `GET /api/sessions/{sid}/objectives` · `…/eventlog` | Objective status · event log |
| `GET /api/sessions/{sid}/aar` · `…/aar/objectives?seq=` · `…/aar/at?seq=` | AAR report · objectives · snapshot at a point |
| `GET /api/sessions/{sid}/save` · `POST /api/sessions/load_save` | Save a session · resume from a saved state |

Interactive API docs are auto-served at **http://127.0.0.1:8000/docs** (FastAPI/Swagger).

**Order actions:** `maneuver`, `downlink`, `observe`, `jam`, `engage`, `cyber`, `command`.
Common params:

- `maneuver`: `dv` (3-vector m/s in ECI), `via` (uplink station). Use `/maneuver/compute` first
  to convert higher-level entry modes into a Δv.
- `downlink`: `via` (preferred station), `bitrate_cap_kbps`, `priority` (routine/priority/immediate),
  `partial_dump: {fraction: 0..1}` (drain only a fraction of buffered storage).
- `observe` (ISR): `intent` (search/track/characterize/cue), `beam_mode`
  (wide_area/stripmap/spotlight/scan/fine/polarimetric), `look_angle_deg` (0–45), `duration_s`,
  `gain` (base, multiplied by mode `gain_factor` × cos look).
- `jam`: `modulation` (barrage/spot/sweep/deceptive), `power_w`, `bandwidth_hz`,
  `victim_bandwidth_hz`, `success_prob`.
- `engage` (kinetic): `salvo_n`, `interceptor_dv_ms`, `success_prob`.
- `cyber`: `vector` (rf/supply_chain/insider/ground_segment), `payload`
  (data_exfil/wiper/spoof/dwell), `dwell_s`, `persistence_h`, `attribution`, `access_vector`.
- `command`: `verb` (e.g. `prop.collision_avoid`, `satcom.set_frequency_plan` with
  `beam_pattern`/`polarization`/`eirp_dbm`/`freq_hopping_rate_hz`/`null_steering_targets`,
  `sigint.task_collection` with `band`/`intercept_mode`/`dwell_s`).

Rejected orders return a human-readable `reason`.

---
