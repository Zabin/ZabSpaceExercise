[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md) ·
[White Cell manual](12-white-cell-manual.md) · [Traceability matrix](15-manual-traceability.md)

## 12d. White Cell manual — clock refusals, saving, adding assets, and who sees which controls

Part of the [White Cell manual](12-white-cell-manual.md). Section IDs continue the `WCM-n` scheme;
[`15-manual-traceability.md`](15-manual-traceability.md) maps them both ways.

### WCM-21 · Time controls: bounds and the exact refusal messages

WCM-4 explains the controls. This is the lookup table for when one is refused. A refused control
changes nothing: the clock, the world and the event log stay exactly as they were. In the console the
reason appears in the red status line under the session label in the **Cell & Time** panel, prefixed
by the control (`Advance:`, `Rewind:`); the next successful jump clears it. The span of an exercise is
**its start time to start + 366 days**; times in the messages are microseconds of sim-UTC.

| You do | Limit | Message |
|---|---|---|
| **+1m / +10m / +1h** | not backwards, not a non-finite number | `step cannot move time backwards (dt_sim_s=-5.0); use rewind` |
| **+1m / +10m / +1h**, or an advance to a time | must not pass start + 366 days | `advance target 1931407260003905 is beyond the exercise span (start_epoch + 366 days = 1931407200000000, sim microseconds); state and clock unchanged` |
| Advance to a time (HTTP `/advance`, `t`) | not earlier than now | `advance target ... is earlier than now=...; time cannot move backwards (use rewind); state and clock unchanged` |
| **⟲ Rewind** (to the start), palette "rewind to start", a bookmark | target within `[start, now]` | `rewind target ... is outside the exercise span [start_epoch=..., now=...] (sim microseconds); use start_epoch to rewind to the start` |
| Undo (HTTP `/undo`, `n`) | `n` at least 1, something to undo | `undo count must be at least 1 (got 0)` · `nothing to undo` |
| Clock rate (HTTP `/clock`, `rate`) | greater than 0 and at most 10000 sim seconds per wall second | `clock rate 10001.0 is outside (0, 10000] sim seconds per wall second; the clock is unchanged` |
| Any of the above from Blue, Red, Observer or with no seat named | White only | `White Cell control: refused unless the request names the white seat` |

Things the table does not show:

- **Pause / Resume** (the toolbar button) starts and stops the shared clock, **and Resume resets the rate to
  the default 1.0** (verified: rate 60, Pause, Resume gives 1.0). The rate has no console control. After every
  Resume, re-send the rate through HTTP: `POST /api/sessions/{sid}/clock` with `{"running":true,"rate":60}`
  (rate 1 is real time; 0.001 and 10000 are accepted, 0 and 10001 are not).
- A **running clock at the end of the span** does not raise an error. It is pinned at start + 366 days: the
  clock still reads as running but stops advancing. Rewind to continue.
- **Undo** has no console button. `POST /api/sessions/{sid}/undo` with `{"n":1}` removes the last `n`
  actions (undoing past the first logged event returns to the start). Rewind and undo do not pause a
  running clock; pause first if you want to stand at the earlier moment.
- `/start` also works on a Creator draft session (it then runs a clock on a scratch force); do not start a draft.
  The Observer check reads the `cell` in the query string (`?cell=observer` is refused with 403); a request that
  puts `observer` only inside its JSON body is not caught, which is why trusted-LAN use is assumed.
- A time jump on a session you loaded but have not started also works; **▶ Start** is what arms the clock.
- Rewinding is exact: orders issued after the target are removed and replay differently if you act differently.

> **Sources:** `spacesim/session/manager.py` (`step`, `advance_to`, `rewind_to`, `undo_last`,
> `set_clock`, `_span_ceiling`) · `spacesim/ui_web/server.py` (`step`, `advance`, `rewind`, `undo`,
> `set_clock`, `_require_white`) · `spacesim/ui_web/static/app.js` (`stepBy`, `rewindTo`,
> `reportControlError`) · FR-4310, FR-4320, FR-4330, NFR-1600

### WCM-22 · Save and resume: what a save holds and every refusal

**Save.** **⚙ Settings ▾ → ⬇ Save session** downloads `<vignette id>-save.json` through the browser
(any seat can read it with `GET /api/sessions/{sid}/save`). One file carries everything needed to
resume without the original vignette file: the vignette exactly as loaded including assets you added
(`content`), the starting world used for replay (`baseline`), the seed, the whole event log, queued
orders, pending events, SSN requests, operator-seat bindings, overrides, the classification banner, the
`started` flag, the end time, and the simulator version. It is a snapshot of history, so loading it
rebuilds the exercise by replaying the log.

**Load.** **⚙ Settings ▾ → ⬆ Load session**, choose the `.json`. This is White-only. The new session is a
fresh session id; your current one is untouched. A resumed exercise starts with the clock **paused**
(so it does not fast-forward through the time since the save); press **Resume** or **▶ Start**.

**Warnings.** A pop-up `Save loaded with warnings:` lists them. The two you can see: `this save was
written by simulator version X; this is Y` (it still loads; replay may differ if the engine changed
between versions) and `legacy save: it depended on the vignette file 'ID' as it is now, not as it was
when saved` (an older save that stores only the vignette id).

**Refusals.** The file is checked before anything is replayed. If refused, the line **Load failed:
<reason>** appears (status line when a session is open, session label otherwise), nothing loads and
your session is untouched.

| Reason shown | Cause | What to do |
|---|---|---|
| `not a valid save file (...)` | The file is not JSON | Pick the right file; do not edit saves by hand |
| `save is missing required key 'content'` (also `baseline`, `seed`, `eventlog`, `final_time`) | Truncated or wrong file | Use the original download |
| `save key 'seed' must be an integer` (also `final_time`) | Damaged value | As above |
| `eventlog has 100002 entries; limit is 100000` | Too long to replay safely (cap 100,000 entries) | Resume an earlier save, or run shorter exercises |
| `save key 'eventlog' is malformed: ...` | Damaged log | Use the original download |
| `save key 'final_time' is earlier than the save's last logged event` | Damaged end time | Use the original |
| `save key 'final_time' is beyond the maximum span (366 days past the start epoch)` or `... earlier than the exercise start epoch` | End time outside the exercise span | Use the original |
| `the save depends on vignette 'ID', which is not available in the content directories` | An older save whose vignette file is gone | Restore the file, or add its folder to `content.external_vignette_dirs` |
| `save content portion refused: blue_forces[ID].orbit: a satellite must declare an orbit` (and similar) | The embedded vignette fails the same checks as Load | Fix the vignette inside the save, or use an earlier save |
| `save replay baseline is not a valid world: ...` | Damaged starting world | Use the original |
| `save key 'orders' has an entry missing actor, action` (also `pending`, `ssn_requests`) | Damaged list | Use the original |
| `White Cell control: refused unless the request names the white seat` | Loaded from a Blue, Red or Observer tab | Switch to White |

A save does not hold browser-only state: panel layout, the Operator seat you typed, the mission-brief
collapse state.

**Save as scenario** (**📋 Session ▾ → 💾 Save as scenario...**) is different: it writes the *current
state* as a new vignette that starts at the moment you saved. It needs `content.user_save_dir` (see
WCM-17). It keeps the force and sensors as they now are, tracks, resources, health, space weather, the
ROE declared at the start, and the objectives. It does **not** carry scripted injects, approval gates, the
intro brief and tutorial, the Red doctrine profile, or ROE changes you made during play. Use **Save
session** to pause and resume the *same* exercise; use Save as scenario to start a new one from here.

> **Sources:** `spacesim/session/manager.py` (`save_state`, `validate_save`, `from_state`,
> `_check_final_time_span`, `MAX_EVENTLOG_REPLAY_ENTRIES`, `MAX_SAVE_SPAN_US`) ·
> `spacesim/session/inprocess.py` (`load_save_with_warnings`) · `spacesim/ui_web/server.py` (`load_save`) ·
> `spacesim/ui_web/static/app.js` (`saveSession`, `loadSaveFile`, `showLoadFailure`) ·
> FR-7210, FR-7220, FR-7230, NFR-3710

### WCM-23 · Add real satellites before Start: TLE, OMM and what is refused

**Important timing.** Assets can be added only **between Load and Start** (or in a Creator draft, WCM-17).
After **▶ Start**, every add is refused: `cannot edit force after start`. (The older "mid-exercise" wording
in earlier versions of this manual no longer describes the product.) There is no console form for this on a
loaded session; use the API, or build the force in the Creator.

**Add one satellite by TLE** (a loaded, unstarted session):

```bash
curl -X POST 'http://127.0.0.1:8000/api/sessions/<SID>/force/tle?cell=white' -H 'Content-Type: application/json' \
  -d '{"id":"ISS","owner":"red","kind":"satellite","line1":"1 25544U ...","line2":"2 25544 ..."}'
```

`owner` is `blue`, `red` or `neutral`; the id may use letters, digits, `_`, `.`, `-`. Replies are
`{"ok":true}` or `{"ok":false,"reason":...}`:

- `invalid TLE: expected two 69-char lines starting with '1 ' and '2 '` - re-copy both lines whole.
- `invalid TLE for asset 'ID': TLE does not parse/propagate: sgp4 propagation error code 6 for TLE asset` -
  the element set cannot be computed at the exercise start time. Use a fresher one.
- `cannot edit force after start` - see above.

The exercise epoch, not the epoch printed in the TLE, is when the object is placed.

**Add several at once** - `POST /api/sessions/{sid}/force/bulk_import` with `{"format":"tle"|"omm",
"content":"<file text>","assignments":{...}}`. `tle` takes a multi-object TLE file (names optional);
`omm` takes CCSDS OMM in KVN `KEY = value` form (XML is not read). The reply is a list with one entry per
object: `{"raw_id","asset_id","ok","reason"}`; a bad object does not stop the others. `assignments` maps
each object's `raw_id` (its name line, or the OMM `OBJECT_NAME`) to `{"asset_id","owner","kind"}`;
an object with no assignment is returned `no side/template assignment provided` and nothing is
added, so call it once to see the `raw_id`s, then again with assignments. OMM objects need `SEMI_MAJOR_AXIS`
(kilometres), `ECCENTRICITY`, `INCLINATION`, `RA_OF_ASC_NODE`, `ARG_OF_PERICENTER`, `MEAN_ANOMALY` (degrees).
Per-object reasons you can meet:

- `invalid OMM element set: missing a_m, i_deg, ...` - a required field is absent.
- `invalid OMM element set for asset 'ID': orbit.e must satisfy 0 <= e < 1, got 1.5`
- `... orbit perigee radius a_m*(1-e) = 6000000 m must exceed the Earth's equatorial radius (6378137 m)`
- `... asset id 'bad id!' is not valid (letters, digits, '_', '.', '-'; 1-128 chars; no leading '.' or '~')`

Whole-file refusals are HTTP 400: `no recognizable TLE blocks found in file`, `no recognizable CCSDS OMM (KVN)
blocks found in file`. After Start a bulk import returns an empty list `[]` with no explanation - treat an empty
reply as "refused". Adding an object with an id that already exists replaces that asset without a warning;
check the id before you import.

> **Sources:** `spacesim/session/manager.py` (`add_tle`, `_force_add_tle_object`, `_force_add_omm_object`,
> `bulk_import`) · `spacesim/content/bulk_import.py` (`parse_multi_tle`, `parse_ccsds_omm`) ·
> `spacesim/content/vignette.py` (`asset_authoring_problems`) · `spacesim/ui_web/server.py` (`add_tle`,
> `bulk_import`) · FR-5220, FR-5310, FR-5311

### WCM-24 · Which controls each seat sees

The server decides what each seat may do; the toolbar only hides what it will refuse. In a loaded session:

| Control | White | Blue / Red | Observer |
|---|---|---|---|
| Seat buttons, **⏸ Handover**, **▦ View ▾**, **⚙ Settings ▾** (save/load/help) | yes | yes | yes |
| Satellite command (order form), fleet rail, tasking, Command queue, graphs | yes | yes (own assets only, own belief) | shown but every action is disabled and refused by the server |
| **⏸ Pause / ▶ Resume**, **+1m / +10m / +1h**, **⟲ Rewind** | yes | hidden | hidden |
| **📋 Session ▾** (Load, Start, Save as scenario, Observer view, Seat-to-role assignment) | yes | hidden | hidden |
| **🛠 Creator ▾** | yes | hidden | hidden |
| Injects panel, Build / schedule inject, pending injects | yes | hidden | hidden |
| Compare (truth beside each cell), AAR bookmarks, branch compare, assessment | yes | hidden | hidden |
| Load a save (⚙ Settings ▾ → Load session) | works | button visible, server refuses | refused |
| Operator seat field on the order form | yes | yes | disabled |

"Hidden" is a convenience. A Blue or Red tab (or any script) that sends a White request is refused with
`White Cell control: refused unless the request names the white seat`. The seat you choose is
trusted - there is no password - so run on a trusted LAN (see [`01-install-and-run.md`](01-install-and-run.md)).

> **Sources:** `spacesim/ui_web/static/app.js` (`setCell`) · `spacesim/ui_web/static/index.html`
> (`white-only` controls) · `spacesim/ui_web/server.py` (`_require_white`, `_reject_observer`) · FR-4320, FR-6220

### WCM-25 · Space weather, debris persistence and attribution settings (White)

Three smaller facilitation features, none with a dedicated console panel.

**Space weather.** The inject library template `space_weather_severe` (Build / schedule inject, WCM-5) sends
every cell a message (`Geomag storm advisory — eclipse drain elevated, watch SoC margins`). A custom
`space_weather` effect may also carry an `index_series`: a list of `{offset_s, kp, f107}` entries (Kp 0-9,
F10.7 above 0; a bad entry is refused with the reason, for example `kp must be a number in [0, 9]`). While a
series is in force, low-orbit satellites that have a ballistic coefficient set decay faster, and a vignette may
add a random environmental-anomaly rate; both are authored in the vignette YAML
(`space_weather_series`, `environmental_anomalies`), and no shipped vignette uses them. Players see
the effect only as messages and as changes in their own telemetry.

**Debris persistence.** A debris-creating event (the `debris_field_500km` template, or a destructive strike)
records how long the cloud is expected to last, by altitude: below 400 km `weeks_to_months`, 400-900 km
`years_to_decades`, above that `centuries`. White reads it in the ground-truth JSON (`GET /api/sessions/{sid}/godview`,
`debris[].persistence_estimate`); there is no console display and players do not see debris fields.
It is a teaching figure only and does not change access windows or conjunction screening.

**Attribution confidence.** When a jam or cyber effect lands, the victim gets an attribution signal whose
confidence normally depends only on how overt the effect was (95%, 50% or 15%). A vignette can set its own
figure per effect class with `effect_detectability_config` entries `{action_type?, reversibility_category?,
confidence}`, so a facilitator can make, say, all jams easy to attribute. Authored in YAML only.

> **Sources:** `spacesim/session/manager.py` (`_apply_inject_effects`) · `spacesim/engine/perturbations.py`
> (`index_series_problems`) · `spacesim/engine/effects.py` (`_persistence_estimate`, `DebrisField`,
> `ModerateEffectResolver`) · `spacesim/content/inject_library.yaml` · `spacesim/content/vignette.py`
> (`effect_detectability_config`) · FR-1230, FR-1430, FR-1450, FR-4440
