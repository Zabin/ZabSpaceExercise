[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md) ·
[Troubleshooting and glossary](09-troubleshooting-and-glossary.md)

## 10a. Refusal and error messages: what you see, why, and what to do

A lookup for the exact words the console and server give when something is refused. Find the message,
read the cause, do the fix. For the procedures behind each area follow the link in the last column.
Everything here is a refusal: **nothing changed** when you see it (the exercise, the clock and the
event log are as they were), unless the row says otherwise.

### Orders (Blue and Red)

The compose form shows a red line `✗ <text>` under the form and disables **Issue**; if the order reaches
the server anyway the result line reads `REJECTED: <reason code>`.

| Reason code / console text | Cause | Fix |
|---|---|---|
| `no_window` — "No access window in the planning horizon — wait for the next pass." | No pass in the next 24 simulated hours | Advance time, or pick another station or sensor |
| `no_command_station` — "No command path — set a ground station ('via') or a stored-program time." | Maneuver or command with no `via` and no `stored_at` | Choose a station in the form, or add `stored_at` (BLU-17) |
| `no_downlink_station` — "No downlink station — set a ground station ('via')." | Downlink with no station | Choose a station |
| `roe_kinetic_not_authorized` — "ROE does not authorize kinetic effects." | ROE forbids it, possibly changed by White during play | Ask White; BLU-16 / RED-15 |
| `roe_cyber_not_authorized` — "ROE does not authorize cyber effects." | Same, for cyber | Ask White |
| `no_weapons_quality_track` — "No weapons-quality track — task a sensor to characterize the target first." | Not enough custody for a strike | Build custody (BLU-4 / RED-4) |
| `no_ammo` — "No munitions remaining on this effector." | Magazine empty | Use another effector |
| `insufficient_ammo` — "Salvo is larger than the rounds this effector has left — reduce the salvo." | `salvo_n` too big | Lower the salvo; count rounds across queued strikes |
| `insufficient_delta_v` — "Insufficient delta-v for this maneuver." | Not enough Δv left | Smaller burn; check the manoeuvre ledger (BLU-18) |
| `not_owner` — "This asset belongs to another cell." | Ordering the other side's asset | Choose one of your own |
| `no_such_asset` / `no_such_sensor` — "Unknown asset." / "Unknown sensor." | Typo or asset destroyed | Pick from the list |
| `sensor_contended` — "Sensor is booked for every window in the planning horizon — cancel a queued task or try later." | All passes taken | Cancel a queued task |
| `requires_cue` — "This sensor needs a cue — get a first track on the target with another sensor." | Cue-only sensor | Detect with another sensor first |
| `invalid_param` — "An order parameter is malformed or not a finite number — check the order's fields (or the JSON params box)." | Wrong type or non-number in a field | Fix the field; `null` counts as left out |
| `unknown_action` — "Action not supported for this asset." / `unknown_command` — "Command verb not supported." | The asset cannot do that | Pick from the Action list |
| `no_payload_for_verb` — "This asset's payload can't run that command." | Wrong payload type | Use a verb for this payload |
| `payload_unavailable` — "Payload unavailable — bus is safed or power-red (clear that first)." | Safe mode or low power | Recover the bus (BLU-7) |
| `role_scope_not_assigned` — "This operator seat is not assigned to that asset — ask White Cell to bind it, or clear the Operator seat field." | Seat name wrong or unbound | BLU-15 / RED-14 |
| `role_scope_out_of_scope` — "That command belongs to the other role on this asset — your operator seat covers only its own role." | Bus seat sent a payload verb, or reverse | BLU-15 / RED-14 |
| `no_cyber_vector` (no console text; the raw code shows) | A cyber order with no `vector` | Choose a vector in the cyber form |
| status `pending_approval` (not a refusal) | Waiting for a gate decision | BLU-16 / RED-15 |
| `gate_denied` / `gate_lost_on_resume` (shown as the order's reason) | White denied it, or its gate vanished across a resume | Re-plan; WCM-19 |
| `order not found / not cancellable` | Cancelling an order that is unknown, already run, or waiting for approval | Nothing to do |

An order whose status flips to `executed` has reached its window; it can still have done nothing if the
link was jammed (BLU-17) or a re-check failed (no rounds left).

### White Cell controls

| Message | Where | Meaning and fix |
|---|---|---|
| `White Cell control: refused unless the request names the white seat` | Any White control from Blue, Red, Observer or a script with no seat | Switch to White (WCM-24) |
| `White Cell control: sessions are created by the white seat, not the blue seat` | Load from a non-White tab | Switch to White |
| `the Observer seat is read-only` | An Observer request that changes anything | Observers watch only |
| `only White Cell may cancel an inject` / `... may edit an inject` | Inject queue from a non-White seat | Switch to White |
| `unknown session sess-N` (HTTP 404) | Wrong id, or the server restarted, or 32 sessions were open and the oldest was dropped | Load again; resume from a save (WCM-22) |
| `vignette 'ID' not found` | Load of an unknown id | Pick from the picker; see Creator set-up in WCM-17 |
| `unknown cell 'purple'` (HTTP 400, `GET /activity/{cell}`) | A cell name other than white, blue, red or the observer designations | Use `white`, `blue` or `red` |
| `t1: '2030-03-15T06:00:00' is not an ISO-8601 UTC timestamp (...) or integer microseconds` (HTTP 400; also `t2:`) | A time bound with no `Z`/`+00:00`, another offset, more than 6 decimal digits, a date only, or text | Write `2030-03-15T06:00:00Z` or integer microseconds ([08](08-http-api-reference.md)) |
| `requested time span [...] is wholly outside the session's recorded range [...]` (HTTP 400) | The export span does not overlap the exercise so far | Choose times between the start and now |
| `requested sampling yields N instants, over the export ceiling of MAX_EXPORT_SAMPLES=10000; use interval_s >= X for this span` (HTTP 400) | Span too long for the sample step | Use the `interval_s` the message names |
| `body.dt_sim_s: a non-finite number (NaN or Infinity) is not allowed` | A number field holds NaN or Infinity | Send a real number |
| `cannot change parameters after start` | Changing a dial after Start | Set dials before Start (WCM-2) |
| `unstaffed mandatory role(s): ISR-EO-1/bus` (pop-up on Start) | Required seat bindings missing | WCM-18 |
| `cannot edit force after start` | Adding assets after Start | WCM-23 |
| `not_controller` / `unknown_flag` / `no_such_pending_order` | Gate and ROE replies | WCM-19 |
| `Load failed: ...` | Vignette or save refused | WCM-2 (vignette), WCM-22 (save) |

Time-control messages (`step cannot move time backwards ...`, `advance target ... is beyond the exercise span ...`,
`rewind target ... is outside the exercise span ...`, `clock rate ... is outside (0, 10000] ...`,
`undo count must be at least 1`, `nothing to undo`) are listed with causes in
[WCM-21](12d-white-cell-clock-saves-and-controls.md). Creator and force-add messages are in
[WCM-17](12b-white-cell-vignette-creator.md) and [WCM-23](12d-white-cell-clock-saves-and-controls.md).

### Looks wrong but is not a fault

- **The browser shows validation text such as `[{"type":"value_error", ...}]`.** The server rejected a
  field's shape; read the `msg` inside it. This is how the Creator reports a bad id, latitude or cell.
- **`GET /view/purple` returns an empty picture.** An unknown cell name gets an empty view, not an error.
- **A resumed session is paused.** On purpose, so it does not fast-forward; press Resume.
- **A running clock stopped at the end of the span.** It is pinned at start + 366 days; rewind.

> **Sources:** `spacesim/ui_web/static/app.js` (`REASON_TIPS`, `reportControlError`, `showLoadFailure`,
> `start`) · `spacesim/engine/orders.py` (`_validate`, `decide_gated_order`, `issue_roe_change`) ·
> `spacesim/ui_web/server.py` (`_require`, `_require_white`, `_reject_observer`, `_finite_json_guard`) ·
> `spacesim/session/manager.py` (`role_scope_check`, `validate_save`) ·
> `spacesim/session/inprocess.py` (`start`, `MAX_LIVE_SESSIONS`) · NFR-1600, FR-4310, FR-4320
