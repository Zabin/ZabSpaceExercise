[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md) ·
[White Cell manual](12-white-cell-manual.md) · [Traceability matrix](15-manual-traceability.md)

## 12b. White Cell manual — build your own vignette (the Creator)

Part of the [White Cell manual](12-white-cell-manual.md). The section keeps the `WCM-n` ID scheme;
[`15-manual-traceability.md`](15-manual-traceability.md) maps it both ways. Read this when the
19 shipped vignettes do not fit your training goal and you want to put your own force on the board.

### WCM-17 · Vignette Creator: build a force, save it, play it

**What the Creator is.** A scratch pad for the *force* (satellites and ground sites) of a new
vignette. It is White-only: the **🛠 Creator ▾** button in the toolbar disappears when you switch to
Blue, Red or Observer, and the server refuses every Creator call that does not name the White seat.
It works on a **draft** — an unstarted session of its own, separate from any exercise you have
loaded. Nothing reaches disk until you press **💾 Save as vignette**.

**What it does not do.** The Creator builds assets only. The forms make a satellite with an orbit but no bus
or payload, and there is no way to add sensors, so edit the saved YAML to give an asset a payload or a sensor.
It does not write objectives, a mission
brief, ROE, injects, a tutorial, or Red doctrine; a saved file carries the defaults for all of them
(a 60-minute estimated duration, start time `2030-01-01T00:00:00Z`, no objectives). Add those by
editing the saved YAML afterwards. The seat counts and roles you set in the matrix (step 8) are
**not** written to the saved file either — see "Seats and roles" below.

**One-time set-up (the host does this once).** Saving needs a directory to write into, and a saved
file only shows up in the scenario picker if that same directory is also searched. In
`spacesim.config.yaml` (repo root) add both, then restart the server:

```yaml
content:
  user_save_dir: /home/me/my-vignettes
  external_vignette_dirs: [/home/me/my-vignettes]
```

Without `user_save_dir`, **Save as vignette** answers `error: {"detail":"no user-save directory configured — set
content.user_save_dir in spacesim.config.yaml"}` (the JSON wrapper is how the console shows it). Without the directory also listed under
`external_vignette_dirs`, the save succeeds but the vignette never appears in the picker (a **Load**
by id answers `vignette 'my-scn' not found`). See [`01-install-and-run.md`](01-install-and-run.md).

**Procedure.**

1. Switch to **White**, open **🛠 Creator ▾**. The menu has sections: **Draft**, **Add asset —
   orbital (TLE)**, **Add asset — ground (lat/long)**, **Asset list**, **JSON view**, **Seats &
   roles**, **Preview**.
2. Under **Draft**, type a **Title** (blank becomes `Untitled Draft`) and press **New draft**. The
   line under the buttons reads `draft sess-N created`. Until you do this, every other button
   answers `create a draft first` (Save) or does nothing.
3. **Add a ground site.** Under **Add asset — ground (lat/long)** type an **Id** (letters, digits,
   `_`, `.`, `-`, up to 64 characters), pick the **Cell** (Blue / Red / Neutral), leave **Kind** as
   `ground_station` (any text is accepted; only the name changes), then either choose a **Curated
   site** or type **Lat** and **Lon** yourself. The picker lists 52 real-world sites by name (for
   example `Schriever — Schriever SFB (AFSCN master), CO`); choosing one fills **Lat**/**Lon**, and
   you can still overtype them. Choose `(free entry)` to type coordinates freely. Press **Add
   (lat/long)**. You should see `asset added`. Latitude must be -90 to 90 and longitude -180 to 180;
   otherwise the line shows `error:` followed by the server's validation detail (for example `lat_deg
   must be in [-90, 90], got 138.8`).
4. **Add a satellite by TLE.** Under **Add asset — orbital (TLE)** fill **Id**, **Cell**, **Kind**
   (`satellite`), paste the two TLE lines into **Line 1** and **Line 2**, press **Add (TLE)**. You
   should see `TLE added`. A refusal reads `refused:` plus the reason:
   - `invalid TLE: expected two 69-char lines starting with '1 ' and '2 '` — the lines are
     truncated, swapped or not TLE lines. Re-copy them whole.
   - `invalid TLE for asset 'ID': TLE does not parse/propagate: sgp4 propagation error code 6 for TLE
     asset` — the orbit cannot be computed at the draft's start time (a decayed or far-out-of-date
     element set). Use a fresher TLE.
   The exercise start time is fixed at 2030-01-01, so the epoch printed in the TLE is not used to
   pick the start; the orbit is propagated *to* that time.
5. **Review and edit** in **Asset list**: press **↻ Refresh**. Each row shows `id (kind)`, a cell
   drop-down, **Set cell** (reassigns the asset to the chosen cell) and **✕ Delete**. Adding an
   asset with an id that already exists replaces the earlier one without a warning — check the list
   after typing an id.
6. **JSON view (advanced).** **Load from state** fills the box with `{"assets": [...]}`, the exact
   draft force. Edit it and press **Save to state** to replace the whole list at once: the line shows
   `saved` or `rejected: <reason>`, and a rejected edit changes nothing. Typical reasons: `invalid
   asset 'ID': resources.delta_v_ms must be a finite number >= 0, got -5.0`; `invalid asset 'ID':
   orbit perigee radius a_m*(1-e) = 100000 m must exceed the Earth's equatorial radius (6378137
   m); ...`; `invalid asset list: ...` (a missing `id` or a wrong field type); `invalid JSON: ...`
   (the box is not valid JSON). A satellite with no orbit is *allowed* here (you may still be
   drafting); it is caught when you save.
7. **Preview.** Press **🔭 Refresh preview (2D map / 3D globe)**. The 2D map and globe redraw with
   every asset at its true position — ground truth, no fog — and the main view shows the *draft*. Use it to catch a ground site on the wrong continent.
8. **Seats and roles (optional).** Pick a **Cell** (the menu opens on `White`; choose Blue or Red, or you get seats named `white-1`...), enter a **Count** and press **Declare seats**:
   seat names `blue-1`, `blue-2`, ... appear in the matrix, one row per seat, each with an asset
   drop-down, a role drop-down (`both`, `bus`, `payload`) and **Assign**. **Assign** binds that seat to
   the chosen asset and role in the draft. The matrix says `(declare seats and add assets first)` until
   you have both. This is a rehearsal of the staffing step in [`12-white-cell-manual.md`](12-white-cell-manual.md)
   (WCM-2 step 3, and [WCM-18](12c-white-cell-rules-and-staffing.md)); **it is not saved into the
   vignette file** (the saved file always has an empty `roles_needed`), so declare the staffing again in
   the YAML or, for a loaded exercise, in **Session ▾ → Seat-to-role assignment**.
9. **Save.** Type a **Vignette id** (the file name; same character rules as asset ids) and press **💾
   Save as vignette**. Success shows `saved: /path/to/my-scn.yaml`. Saving the same id again overwrites
   the file. The file is checked before it is written; a refusal shows `error:` and the reason, and
   writes nothing:
   - `vignette 'my-scn' is invalid: blue_forces[SATX].orbit: a satellite must declare an orbit (and 1 more
     problem)` — add the missing orbit or location (every satellite needs an orbit; every ground
     asset except a cyber unit needs a location). Fix it in the JSON view or the Asset list and save
     again.
   - A blank id shows `vignette id required`.
10. **Play it.** Reload the browser page (the picker is filled when the page opens). Your vignette
    appears in its own group labelled `External: <directory name>`, under the **Title** you typed in step 2 (not the file id). Choose it, press **Load**, then
    **▶ Start**, and run it like any other. It loads through the same checks as every built-in
    vignette; if anything is still wrong you get **Load failed:** with the list
    (see [`06-the-vignette-library.md`](06-the-vignette-library.md#when-a-vignette-wont-load)).

**What can go wrong, in one place.**

| You see | Cause | Fix |
|---|---|---|
| `create a draft first` | You pressed Save before **New draft** | Press **New draft** |
| `error: [{"type":"value_error", ...` | A field failed the server's shape check (an id with a space, a latitude outside range, an unknown cell) | Read the `msg` inside; correct the field |
| `refused: invalid TLE ...` | See step 4 | Re-copy the TLE or use a fresher one |
| `rejected: ...` | See step 6 | Fix the asset the message names |
| `error: White Cell control: refused unless the request names the white seat` | Creator called from a non-White seat | Switch to White |
| `error: no user-save directory configured ...` | `content.user_save_dir` unset | One-time set-up above |
| Saved, but not in the picker | Directory not under `external_vignette_dirs`, or the page was not reloaded | One-time set-up; reload |

**Limits worth knowing.** A draft cannot step or advance its clock from the console (the server
answers `draft sessions cannot advance time`); to see it run, save it and load it. Drafts stay in the
session list (`/api/sessions`) like any other session until the server evicts the oldest.

### Starter snippets: copy, paste, change the ids

Vignettes are **authored inline**: every asset, sensor and inject is written out in full inside the
vignette file. There are no template references or includes, so to reuse a piece you copy it and edit it.
The snippets below are lifted from the shipped `spacesim/content/vignettes/01-leo-isr-denial.yaml`
(sensor `beam_mode` line from the rules in [`06`](06-the-vignette-library.md#authoring-sensors-optional-modality-fields)).
Put them under the matching key of a vignette file (`blue_forces:`, `red_forces:`, `sensors:`, `objectives:`,
`injects:`). Each runs as shown; the combined file below was loaded, started and played as a check.

**Imaging satellite with bus and payload** (`blue_forces:`; the Creator forms cannot make the bus or payload):

```yaml
- id: ISR-EO-1
  kind: satellite
  orbit: {source: kepler, a_m: 6978137.0, e: 0.0, i_deg: 97.8, raan_deg: 342.0, argp_deg: 0.0, ta_deg: 0.0}
  resources: {delta_v_ms: 80.0, power_w: 1500.0}
  payload_state: {type: isr_eo, collect_rate_per_s: 0.002}
  bus_state:
    power: {battery_soc: 0.9, charge_rate_per_s: 0.00012, drain_rate_per_s: 0.0001}
```

**Ground station** (`blue_forces:`; this is the one the Creator's lat/long form makes):

```yaml
- id: GS-NORTH
  kind: ground_station
  location: {lat_deg: 24.25, lon_deg: 54.55, alt_m: 0.0}
  elevation_mask_deg: 5.0
```

**Jammer and one-round interceptor** (`red_forces:`):

```yaml
- id: JAM-NORTH
  kind: jammer
  location: {lat_deg: 27.13, lon_deg: 56.21, alt_m: 0.0}
  elevation_mask_deg: 0.0
- id: RED-ASAT
  kind: interceptor
  location: {lat_deg: 41.64, lon_deg: 86.24, alt_m: 0.0}
  resources: {ammo: 1}
```

**Ground radar sensor** (`sensors:`; delete `beam_mode` to use the default `dish`; the other value is `fence`):

```yaml
- id: BLUE-RADAR
  owner: blue
  kind: ground_radar
  beam_mode: fence
  location: {lat_deg: 30.57, lon_deg: -86.21, alt_m: 0.0}
  elevation_mask_deg: 5.0
```

**Objectives** (`objectives:`):

```yaml
blue:
  - {id: deliver_isr, desc: "Deliver confirmed imagery before the landing window", metric: {kind: deliver_before}}
red:
  - {id: deny_isr, desc: "Deny Blue imagery delivery during the window", metric: {kind: deny_delivery}}
```

**Timed inject** (`injects:`; fires 45 simulated minutes in; use `trigger: {type: manual}` for a button instead):

```yaml
- id: commercial_imagery_leak
  label: "Commercial SAR imagery reveals the surface group"
  trigger: {type: time, at_sim_s: 2700}
  effects:
    - {type: message, to: [blue, white], text: "OSINT leak: commercial SAR shows the surface group."}
```

A file needs `id`, `title` and `start_epoch_utc` at the top of the `vignette:` block. After saving the file in a
folder listed under `content.external_vignette_dirs`, reload the page: it appears under `External: <folder>`.
**Load** then checks every piece and lists any problem as **Load failed:** (WCM-2); a missing orbit or
location, a bad id or a TLE that will not propagate are caught there. With all six snippets above in one
file, Load succeeded, **Start** worked, a Blue downlink queued over `ground_uplink`, and `deliver_isr` turned met.

> **Sources:** `spacesim/content/vignettes/01-leo-isr-denial.yaml` (starter snippets) · `spacesim/ui_web/static/creator.js` (`newDraft`, `addTle`, `addGroundAsset`, `jsonSave`,
> `declareSeats`, `saveVignette`, `refreshPreview`) · `spacesim/ui_web/static/index.html` (`creator-menu`) ·
> `spacesim/session/manager.py` (`creator_set_state`, `creator_edit_asset`, `creator_delete_asset`,
> `declare_seats`, `_authoring_problems`) · `spacesim/content/vignette.py` (`asset_authoring_problems`,
> `validate_vignette`) · `spacesim/content/vignette_export.py` (`save_vignette`) ·
> `spacesim/config.py` (`ContentConfig`) · `spacesim/ui_web/server.py` (`creator_set_state`,
> `save_vignette`) · FR-5110–FR-5160, FR-5310–FR-5314, FR-5410/FR-5420
