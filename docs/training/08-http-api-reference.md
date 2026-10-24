[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 9. HTTP API reference

All UI actions go through these endpoints (base `http://127.0.0.1:8000`). Reads are fog-filtered
per cell, server-side. The seat is a `cell` query parameter (`?cell=white`, `blue`, `red` or `observer`)
that the caller asserts about itself; the console attaches it to every change it makes. This is
seat enforcement on a trusted LAN, not authentication.

- **White Cell controls need `?cell=white`.** These are refused with **403** when the request names any
  other seat or none at all: `clock` (set), `param`, `start`, `step`, `advance`, `rewind`, `undo`,
  `inject`, `force/tle`, `force/bulk_import`, `force/ground`, `red_step`, `load_save`, `save_vignette`,
  the Creator routes (`creator/state`, `creator/asset`, `creator/seats`), `roles/assign`,
  pending-inject cancel/edit, and `observer/view`. Only the query-string seat counts; a `cell` inside
  a request body is not authority. Nothing changes on a refusal.
- **Creating a session** (`POST /api/sessions`, `…/draft`) is refused with 403 only if the request
  *names* Blue, Red or Observer; leaving `cell` off is allowed, so a script can create a session
  before choosing seats.
- **Player-facing changes** (orders, previews, `cancel`, `gate/decide`, `roe/change`, `recovery`, SSN
  requests) accept Blue, Red or White but refuse `cell=observer` with 403 ("the Observer seat is read-only").

| Method & path | Purpose |
|---|---|
| `GET /api/vignettes` | List the scenario library |
| `POST /api/sessions` `{vignette_id, overrides, seed}` | Load a scenario → returns a session id |
| `POST /api/sessions/{sid}/param` `{param_id, value}` | Set a dial (before start) |
| `POST /api/sessions/{sid}/start` | Start the exercise |
| `POST /api/sessions/{sid}/step` `{dt_sim_s}` / `…/advance` `{t}` | Advance time |
| `POST /api/sessions/{sid}/rewind` `{t}` · `…/undo` `{n}` | Time travel; rewind `t` must lie in `[start_epoch, now]` (`start_epoch` is on `GET …/clock`), else 400 naming the span; `undo` with nothing to undo (or `n` below 1) is a 400, and an undo that drops every logged action lands on `start_epoch` |
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
| `GET /api/sessions/{sid}/telemetry/{cell}/{asset}/export.csv?t1&t2&interval_s` | One asset's telemetry over a span as CSV (`t,utc,asset,subsystem,param,value,unit,status`). Own assets only (White: any); bounds default to the recorded range |
| `GET /api/sessions/{sid}/ric_view/{cell}?origin&chase&target` | Live RIC-frame relative motion about `origin`; with `chase` + `target` also the CATS phase angle. Own assets + own tracks only (White: truth); 404 outside custody |
| `GET /api/sessions/{sid}/tle/{cell}?object_id` | Copyable current-epoch TLE for one satellite. Own satellites from their actual orbit, others only from a held track (White: truth); 404 with the reason otherwise |
| `GET /api/sessions/{sid}/ephemeris/{cell}?object_id&reference_id&t1&t2&interval_s&format` | The cell's believed ephemeris over a span, ECI + RIC about `reference_id`. `format` = `csv` (default), `oem` (CCSDS OEM, ECI only) or `ric` |
| `GET /api/sessions/{sid}/ephemeris/truth?…` (same query) | Ground-truth ephemeris, White only (no cell binding) |
| `GET /api/sessions/{sid}/maneuver_ledger/{cell}/{asset}` · `…/export.csv` | Per-asset manoeuvre ledger (time, Δv cost, purpose tag, remaining Δv) as JSON · CSV |
| `GET /api/sessions/{sid}/alarms/{cell}` | Fleet alarms / event feed |
| `GET /api/sessions/{sid}/godview` | Ground truth (White only) |
| `GET /api/sessions/{sid}/objectives` · `…/eventlog` | Objective status · event log |
| `GET /api/sessions/{sid}/aar` · `…/aar/objectives?seq=` · `…/aar/at?seq=` | AAR report · objectives · snapshot at a point |
| `GET /api/sessions/{sid}/aar/export.csv` · `…/aar/export.json` | AAR download as CSV · JSON |
| `GET /api/sessions/{sid}/save` · `POST /api/sessions/load_save` | Save a session · resume from a saved state (a save that cannot be used — missing keys, malformed parts, or a legacy save whose vignette file is gone — is refused with HTTP 400 and a reason; see below) |

**Refusal summary (what a script sees).**

| Situation | Response |
|---|---|
| White Cell route without `?cell=white` | 403, "White Cell control: refused unless the request names the white seat" |
| `POST /api/sessions` naming a player seat | 403, "sessions are created by the white seat, not the blue seat" |
| `rewind` to a time before `start_epoch` or after now | 400, message gives `[start_epoch, now]` in sim microseconds; the session is unchanged |
| `undo` with nothing logged | 400, "nothing to undo"; `n` below 1 is 400 "undo count must be at least 1" |
| `load_save` with an unusable save | 400 with the reason, and no session is created. Reasons include: not a JSON object; a missing or mistyped required key (e.g. `vignette_id`, `seed`); a malformed `eventlog` or list entry; `final_time` earlier than the save's last logged event or the exercise start, or more than 366 days past the start; a legacy save whose vignette file is no longer available; an embedded vignette that fails validation |
| `inject` that is malformed, or targets something it cannot (e.g. an `anomaly` on an asset with no bus) | 400 naming the reason; nothing is applied |

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

Time-span bounds (`t1`, `t2`) are integer microseconds of sim UTC. A span that is wholly outside
the recorded range is a 400. A request that would sample too many instants is also a 400, and
the message names the ceiling. The role manuals walk through each export:
[WCM-12–16](12a-white-cell-analysis-and-exports.md), [BLU-11–14](13-blue-cell-manual.md),
[RED-10–13](14-red-cell-manual.md).

> **Sources:** `spacesim/ui_web/server.py` (route table, `_require_white`, `_reject_observer`,
> `_refuse_player_seat_on_create`, `rewind`, `undo`, `load_save`, incl. `get_ric_view`, `get_tle`,
> `telemetry_export_csv`, `maneuver_ledger*`, `aar_export_*`, `ephemeris_truth`,
> `ephemeris_cell_observed`) · `spacesim/session/ephemeris.py` (`MAX_EXPORT_SAMPLES`) ·
> `spacesim/engine/orders.py` (order actions and params)

---
