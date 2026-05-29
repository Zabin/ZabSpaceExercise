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
| `POST /api/sessions/{sid}/inject` `{inject}` | Fire an inject (id or `{effects}`) |
| `POST /api/sessions/{sid}/order` `{cell, actor, action, target, params}` | Issue an order |
| `GET /api/sessions/{sid}/orders/{cell}` · `POST …/cancel` `{cell, order_id}` | Command queue · cancel a queued order |
| `GET /api/sessions/{sid}/windows/{cell}/{asset}` | Upcoming passes (pass-timeline ribbon) |
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

**Order actions:** `maneuver`, `downlink`, `observe`, `jam`, `engage`, `cyber`. Common params:
`via` (ground station, for uplink/downlink), `dv` (3-vector, maneuver), `intent`
(observe: search/track/characterize/cue), `target`, `outcome`, `success_prob`, `access_vector`
(cyber). Rejected orders return a human-readable `reason`.

---
