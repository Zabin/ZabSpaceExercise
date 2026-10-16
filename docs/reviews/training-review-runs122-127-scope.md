[↑ Docs index](../INDEX.md) · [Pipeline journal](../pipeline/pipeline-journal.md) ·
[Training index](../training/INDEX.md) · [Traceability matrix](../training/15-manual-traceability.md)

# Training Review — Runs #122 and #127 Scope (Own-Satellite TLE, Controller-Event Payloads, Sensor Authoring Fields, Export Routes)

> **Document ID:** REV-TRN-006
> **Skill:** `09-training-manual-review`
> **Scope:** the sections two `08-training-manual-authoring` runs touched:
> - **Run #122, `d030e2d`** (closing `BL-0202`/`0204`/`0205`/`0206`): `BLU-12` and `RED-11` (quick
>   TLE export, rewritten for own satellites); the new `WCM-14` paragraph in `12a`; the §10.3
>   scheduling-check wording in `10-ui-reference.md`; the `07-white-cell-facilitation.md`
>   controller-events block, table and Sources footer; the two `01-install-and-run.md` anchors;
>   the `15` §15.1 TLE row and the §15.2 `WCM-14`/`BLU-12`/`RED-11` rows.
> - **Run #127, `df65302`** (closing `BL-0211`/`0207`): the `06-the-vignette-library.md`
>   "Authoring sensors" field table and footer; the `WCM-2` pointer paragraph and footer; the
>   `BLU-4`/`RED-4` cue/hosted-sensor paragraphs and footers; the `08-http-api-reference.md` §9
>   export rows, time-span note and Sources footer; the `15` §15.1 sensor-fields row and the §15.2
>   `WCM-2`/`BLU-4`/`RED-4` rows; the `training/INDEX.md` `06` row.
>
> Each touched section was read whole, not just the changed lines.
> **Commit reviewed:** `40af409` (branch `claude/chart-prompt-file-90hm9u` tip at review time). No
> commit after `df65302` touches `docs/training/`. Code has moved since run #127: `IP-1222`
> (`57772ba`, `VERIFIED` by `VR-1222`) changed three behaviours the `06` table describes. Accuracy
> is judged against the code at `40af409`, which is what ships.
> **Independence:** this review ran in a fresh agent context with no part in either authoring run,
> in `IP-1220`/`1221`/`1222`, or in any earlier commit on this branch. The commits carry the same
> orchestration-thread `Claude-Session` trailer as this review. That is the same thread-level
> arrangement as REV-TRN-005 and `VR-1221`/`VR-1222`: separate agent contexts under one owner
> session.
> **Upstream:** `08-training-manual-authoring` (runs #122, #127) · **Downstream:**
> `10-integration-review`, `11-release-readiness`

## Headline

Run #122's prose is **accurate against shipped behaviour in every claim checked**. It was driven
live on `co-orbital-threat-escort` seed 7; the author used `leo-isr-denial` seed 4 and
`training-basics` seed 1. Run #127's `08` §9 rows and time-span note are accurate. Its `06`
"Authoring sensors" table and `BLU-4`/`RED-4` paragraphs were accurate when written. Three `06`
rows and one `WCM-2` sentence are now wrong, because `IP-1222` fixed the defects they describe.
`BL-0216` already tracks this; the review confirms it and rates it Medium, not Low. Traceability
is clean: 0 broken links, 43 section IDs, 0 orphans and 0 missing footer paths. The playbook and
training suites passed 20/20.

**No Critical or High findings.** There are 4 findings:

- **F1 (Medium):** the `06`/`WCM-2` staleness after `IP-1222` (`BL-0216`).
- **F2 (Medium, a code defect the review exposed):** an observe order whose sensor has no window
  is rejected as `sensor_contended`, and the console shows "Sensor is busy". The corpus tells
  authors and operators to use exactly this preview to check that a sensor can see a target.
- **F3 (Low):** a malformed sensor field makes `POST /api/sessions` a bare 500, and **Load** shows
  nothing. The manual says only that the vignette will not build.
- **F4 (Low):** two small `07` table omissions.

## Dimensions exercised

### 1. Accuracy — prose claims vs. shipped behaviour

**Code reads** (at `40af409`):

- `session/ephemeris.py::quick_tle` (the own-satellite branch is checked before any Track lookup)
  and `ui_web/static/tleexport.js` (`onOrbit`, `candidates`, `SOURCE_LABEL`, empty-state text).
- `session/manager.py::_apply_inject_effects` (all four `FR-4430` branches, the message
  recipients, and the `scripted_manoeuvre` skip path at fire time) and `_skip_inject_effect`.
- `engine/entities.py::Sensor`, including `_check_usable_phase_angle` and `IP-1222`'s
  `_check_radar_beam_mode` and `altitude_band_affinity: Optional[Regime]`.
- `engine/access.py::_observation_predicate`: the space-based branch checks `min_range_km` before
  `max_range_m`; the ground branch checks the exclusion cone after lighting.
- `engine/orders.py`: `_plan_collection`, `_candidate_sensors`, `_auto_blocked_by_cue`,
  `_resolve_sensor_id` and `_validate`.
- `ui_web/server.py`: the route table for every §9 row added.
- `ui_web/static/app.js` (`REASON_TIPS`, `loadSession`, `api.post`).

**Live drive, run #122 scope** (in-process `TestClient`, `co-orbital-threat-escort` seed 7):

| Claim (location) | Exercised | Observed | Verdict |
|---|---|---|---|
| Own satellites export from the actual orbit, with no track needed (`BLU-12`, `RED-11`) | Blue `BLUE-HVA`, `BLUE-ESCORT`; Red `RED-COORB` | 200, `source: own` for all three | ✓ |
| Another side's untracked satellite is refused with `<cell> holds no track on '<id>'` (`BLU-12`, `RED-11`) | Blue → `RED-COORB`; Red → `BLUE-HVA` | 404 `blue holds no track on 'RED-COORB' — TLE export of another side's satellite needs a held track`, and the Red mirror | ✓ (the manual quotes the leading clause) |
| A tracked object exports from belief (`BLU-12`) | `BLUE-RADAR` observe on `RED-COORB`, advance until the track exists, re-export | 200, `source: track` | ✓ |
| White reads ground truth (`WCM-14`, §15.1) | White → `RED-COORB` | 200, `source: truth` | ✓ |
| Panel labels and empty state (`BLU-12`) | code read, `tleexport.js` | `SOURCE_LABEL` `own` → "your satellite (actual orbit)", `track` → "your track (belief)"; empty state "no own satellite or tracked object to export — task a sensor first"; ground stations filtered by `onOrbit` | ✓ |
| `anomaly` `bus` → safe mode, announced to all three cells; `restore` clears it (`07`) | inject on `BLUE-HVA`, `cause: probe SEU`, then `restore: true` | `safe_mode.active` True with `cause: probe SEU`, then False; messages `BLUE-HVA: anomaly declared (probe SEU)` and `BLUE-HVA: anomaly cleared` to `[white, blue, red]` | ✓ |
| `anomaly` `telemetry` → comms red; `restore` → green (`07`) | inject on `BLUE-HVA` | `comms.status` red, then green; announced to all three cells | ✓ |
| A bus anomaly needs a bus (`07`, §10.3) | inject on bus-less `RED-COORB` | 400 `inject rejected: #0 anomaly: anomaly target 'RED-COORB' has no bus …` | ✓ |
| `sensor_outage` → degraded, announced; `restore` → nominal (`07`) | inject on `BLUE-RADAR`, `cause: probe power` | `health` degraded, then nominal; `BLUE-RADAR: sensor outage declared (probe power)` to all three cells | ✓ (see **F4** for the cleared message) |
| `forced_custody_loss` sets confidence to `degrade_to`, defaulting to 0, with no message; `mode: drop` deletes the track (`07`) | on Blue's track of `RED-COORB`: `degrade_to: 0.3`, then no key, then `mode: drop` | confidence 0.3, then 0.0, then the track is gone; no message in any case | ✓ (see **F4** for the reset decay clock) |
| `scripted_manoeuvre` bypasses the Δv budget; only White is told, with the cost (`07`) | `lvlh`, `dv_t: 2.0` on `RED-COORB` | `delta_v_ms` 300.0 before and after; one message `RED-COORB: scripted manoeuvre (lvlh), cost=2.0 m/s` to `[white]` | ✓ |
| A builder inject scheduled for later is checked when you schedule it (§10.3) | bus-less `anomaly` at +600 s; `hohmann` with an altitude below the surface at +600 s | both 400 at scheduling. The `hohmann` refusal reads `scripted_manoeuvre params rejected: hohmann: target altitude is below Earth's surface`. Advancing past +600 s fired nothing and added no message | ✓ |
| §10.3: a `scripted_manoeuvre` the maths refuses at fire time is skipped with the White-only `inject effect skipped` line | code read, `_apply_inject_effects` (the `except` around `compute_maneuver` calls `_skip_inject_effect`, `to: ["white"]`) | matches. It is reachable only when the target's state changes between scheduling and firing, which the "now refuses" wording conveys | ✓ |
| `07` example ids exist in **Training: Basics** | `00-training-basics.yaml` | `ISR-EO-1`, `RADAR-TRN` and `RED-TGT` are all present | ✓ |
| `01` anchors (`BL-0206`) | link script | `08-http-api-reference.md#9-http-api-reference`, `03-first-exercise.md#headless-walkthrough-no-browser` and `03-first-exercise.md#4-your-first-exercise` all resolve | ✓ |

**Live drive, run #127 scope, at `40af409`.** I wrote a fresh `SessionManager` probe for this: a
deep copy of `co-orbital-threat-escort` (the author used `leo-isr-denial` seed 4), seed 13, with
the sensor list swapped for each case. For `08` §9 I used `TestClient` on
`co-orbital-threat-escort` seed 7.

| Claim (location) | Exercised | Observed at `40af409` | Verdict |
|---|---|---|---|
| `beam_mode` "has no effect in the shipped build"; "the radar `beam_mode` field has no effect yet" (`06`, `WCM-2`) | Radar with `beam_mode` unset, `fence` or `dish`; one observe each on `RED-COORB` | confidence 1.0 / **0.5** / 1.0. `fence` now takes effect; `dish`'s ×1.6 is capped at 1.0 here. `beam_mode: Fence` is **rejected when the session builds** | **F1** (`BL-0216`) |
| `altitude_band_affinity` "is not checked: `LEO` and `LEO_SSO` count as different regimes, and a misspelt regime halves every observation" (`06`) | affinity `Leo`; then `None`/`LEO`/`LEO_SSO`/`GEO` against LEO `RED-COORB` | `Leo` **rejected at build** (literal error naming the six regimes). Confidence 1.0 / 1.0 / **1.0** / 0.5: `LEO_SSO` now counts as `LEO`, and a mismatch still halves | **F1** (`BL-0216`); the halving rule itself ✓ |
| "An order that leaves the sensor as **auto** does **not** get this check today" (`06`) | the only Blue sensor has `requires_cue`, no track, `actor: auto` | validate and issue both rejected `requires_cue`. With a second, plain sensor, `auto` is accepted and picks that one | **F1** (`BL-0216`) |
| A named cue-dependent sensor is rejected `requires_cue`; the preview shows the same reason (`06`, `BLU-4`, `RED-4`) | named `BLUE-RADAR` with `requires_cue`, no track | validate and issue both `requires_cue` | ✓ |
| A hosted sensor answers to either name (`06`, `BLU-4`, `RED-4`) | `space_based` `ESC-CAM` with `host_asset_id: BLUE-ESCORT`; observe by each id, in fresh sessions | both accepted, with windows identical to within 1 µs | ✓ |
| A malformed or misplaced phase-angle range stops the vignette from building a session (`06`, `WCM-2`) | `[100, 20]` and `[0, 190]` on optical; `[0, 90]` on a radar; `[0, 90]` on optical | the first three are rejected with the documented reasons; the last builds | ✓ (what the operator sees: **F3**) |
| `min_range_km` and `exclusion_angle_deg` remove windows (`06`) | `min_range_km: 100000` on the hosted camera; `exclusion_angle_deg: 179` on a ground optical | no window in the look-ahead (0 windows counted directly), and the preview rejects the order, but with reason **`sensor_contended`** | removal ✓; the reason is **F2** |
| No shipped vignette uses any of these fields (`06`) | `grep` over `content/vignettes/*.yaml` for all seven field names | 0 hits | ✓ |
| §9 telemetry `export.csv`: CSV columns; own assets only (White: any); bounds default to the recorded range | Blue on `BLUE-HVA` without bounds; Blue on `RED-COORB`; White on `RED-COORB` | header `t,utc,asset,subsystem,param,value,unit,status`, 200; 404 (fog/ownership); 200 | ✓ |
| §9 `ric_view`: own assets and own tracks only (White: truth); 404 outside custody | Blue origin `BLUE-HVA`, then with chase + target; Blue origin `RED-COORB` (untracked); White origin `RED-COORB` | 200; 200; 404 `origin 'RED-COORB' has no state visible to blue`; 200 | ✓ |
| §9 `ephemeris/{cell}` `format` = `csv`/`oem`/`ric`; `ephemeris/truth` the same query | all three formats for Blue; truth CSV | ECI+RIC CSV header; `CCSDS_OEM_VERS = 2.0`; RIC-only header; truth CSV | ✓ |
| §9 `maneuver_ledger` JSON and CSV | Blue `BLUE-HVA`; Blue on `RED-COORB` | `[]`; header `t,cost,purpose_tag,remaining_delta_v_ms`; 404 | ✓ |
| §9 `aar/export.csv`, `aar/export.json` | both | 200, `section,key,value` CSV; JSON report | ✓ |
| Time-span note: integer µs; a wholly out-of-range span is a 400; too many instants is a 400 that names the ceiling | spans 10⁴ s past the end; `interval_s` 0.001 and 0.0001 | 400 `… is wholly outside the session's recorded range …`; 400 `… over the export ceiling of MAX_EXPORT_SAMPLES=10000; use interval_s >= 0.360038 …` on both telemetry and ephemeris | ✓ |

The ephemeris routes require `t1`/`t2`: omitting them gives a 422. §9 lists them without
"optional" and gives the recorded-range default only on the telemetry row, so it is accurate. A
Blue ephemeris request for an untracked object returns a header-only CSV, as `BLU-13` already
documents ("no row for that instant").

### 2. Traceability integrity

A scripted check over all of `docs/training/*.md` at `40af409`:

- **Links:** every relative link resolves to an existing file, and every anchor into a training
  `.md` resolves. **0 problems.** This includes run #127's
  `06-the-vignette-library.md#authoring-sensors-optional-modality-fields` (used from `WCM-2`,
  `BLU-4` and `RED-4`) and run #122's three `01` anchors.
- **Section IDs:** 43 `WCM`/`BLU`/`RED` IDs are defined across `12`/`12a`/`13`/`14`, with no
  duplicates. Every ID is cited in `15`, and every ID `15` cites is defined. **0 orphans.**
- **Footers:** every literal `spacesim/…` path in the corpus exists (0 missing). Every function or
  route name in the in-scope footers exists at `40af409`:
  - entities, access and orders: `_check_usable_phase_angle`, `_observation_predicate`,
    `_sensor_orbit`, `_validate`, `_candidate_sensors`, `_resolve_sensor_id`,
    `_observation_phase_angle_deg`, `_exec_payload`;
  - isr, maneuver and the vignette loader: `effective_gain`, `phase_angle_factor`,
    `BEAM_MODES["ground_radar"]`, `compute_maneuver`, `build_world`;
  - manager: `_apply_inject_effects`, `_inject_effect_problem`, `get_tle`;
  - `server.py` routes: `get_ric_view`, `get_tle`, `telemetry_export_csv`, `maneuver_ledger*`,
    `aar_export_csv`/`_json`, `ephemeris_truth`, `ephemeris_cell_observed`;
  - other: `MAX_EXPORT_SAMPLES`, plus `candidates` and `SOURCE_LABEL` in `tleexport.js`.
- **Footer ⇄ matrix:** these footers match their §15.2 rows: `WCM-2`, `WCM-14` (both now include
  `get_tle`/`tleexport.js`), `BLU-4`, `RED-4`, `BLU-12` and `RED-11`. The §15.1 sensor-fields
  row is a faithful subset of the `06` footer, and the §15.1 TLE row matches `BLU-12`/`RED-11`.
  **Pending with F1:** after `IP-1222`, the `06` footer and the §15.1 sensor-fields row name
  neither `Sensor._check_radar_beam_mode` nor `isr.altitude_band`. Both now back documented
  behaviour.
- `training/INDEX.md`'s `06` row describes the new section correctly.

### 3. Coverage

- **Sensor authoring fields (`FR-1610`–`FR-1670`).** These are author-facing, and a White Cell
  facilitator authors vignettes, so the White route (`WCM-2` → the `06` table) is the right one.
  Blue and Red meet the effects at tasking time, through the `requires_cue` reason, the
  hosted-sensor naming, and missing windows or reduced gain. `BLU-4`/`RED-4` now cover those.
  No role is left uncovered.
- **Own-satellite TLE export (`FR-7440` as amended):** this reaches every role that can use it:
  `BLU-12`, `RED-11` and `WCM-14` (the White paragraph points to the cell-side difference). The
  Observer exclusion is stated in `WCM-14`.
- **`FR-4430` controller events** are White-only, and `07` plus §10.3 cover them.
- **Recently shipped packages:** `IP-1222` (`VERIFIED`) changed `FR-1610`/`1630`/`1640`
  behaviour. Its manual impact is not yet in the corpus (**F1**). It is tracked as `BL-0216`,
  whose trigger fired at run #130. No other package that reached `VERIFIED` after run #127 has
  operator-visible behaviour.

### 4. Pedagogy

- **Audience fit (MSTR-003 / NFR-3600):** `BLU-4`/`RED-4` add operator actions ("get a first look
  with another sensor"; "check the preview's earliest window"). The `06` table is pitched at
  authors, which suits its home in the library module. The phase angle is defined inline
  ("Sun–target–sensor (CATS)") and the regimes are listed. `LVLH` in `07` is defined in
  `10-ui-reference.md` §10 (R/T/N, row 3); `07` does not link to it, which is acceptable for a
  White audience.
- **Module size (NFR-3500, ~300 lines):**
  - In-scope modules: `06` is 100 lines, `07` 99, `08` 84, `12` 213, `12a` 152, `13` 268 and
    `14` 260.
  - `10-ui-reference.md` is 475 lines, already tracked as `BL-0198`; run #122 changed wording
    but added no subsection.
- **Grounding:** no sequencing or scaffolding decision in scope needs R600 grounding.

## Findings

| Finding | Artifact(s) | Description | Severity | Recommended owner |
|---|---|---|---|---|
| F1 | `06-the-vignette-library.md` "Authoring sensors" (rows `altitude_band_affinity`, `requires_cue`, `beam_mode`, and the footer); `12-white-cell-manual.md` `WCM-2` (last sentence: "The radar `beam_mode` field has no effect yet"); `15` §15.1 sensor-fields row ("radar `beam_mode` inert") | **Stale since `IP-1222` (`VERIFIED`, `VR-1222`).** Four claims are now wrong at `40af409`. (a) A radar `beam_mode` of `fence`/`dish` takes effect: `fence` confidence 0.5 vs 1.0. (b) An unknown radar `beam_mode` is rejected when the session builds. (c) `altitude_band_affinity` is a checked regime: a misspelling such as `Leo` is rejected at build, and `LEO_SSO` counts as `LEO`. (d) `auto` selection honours `requires_cue`: it skips a cue-dependent sensor, and rejects `requires_cue` when every owned sensor needs a cue. An author following the table avoids a working feature and expects a silent halving where they will get a build error. Not Critical: no field, verb, panel or endpoint was removed or renamed, and the prose was accurate when written. **Medium**, on the REV-TRN-002 F2 / REV-TRN-004 F1 precedent for prose that contradicts as-built behaviour. Fix with `BL-0216` (already `SCHEDULED`). Also add `_check_radar_beam_mode` and `isr.altitude_band` to the `06` footer and the §15.1 row. | Medium | `08-training-manual-authoring` (`BL-0216`) |
| F2 | `engine/orders.py::_plan_collection` (`fail_reason = "sensor_contended" if sensor_ids else "no_window"`); `ui_web/static/app.js` `REASON_TIPS.sensor_contended`; in the corpus: `06` ("Use the dry-run preview to check that a sensor you wrote can still find a window"), `BLU-4`, `RED-4`, and `09-troubleshooting-and-glossary.md` (`no_window` = no pass in the look-ahead) | **Code defect the review exposed (pre-existing, not from runs #122/#127).** An observe order whose candidate sensor(s) have **no** window in the look-ahead, with no bookings at all, is rejected `sensor_contended`. The console renders that as "Sensor is busy — it can service this only at a later window." Reproduced 3 ways on fresh sessions: `min_range_km: 100000` (0 windows), `exclusion_angle_deg: 179`, and a shipped radar on a nonexistent target id. `no_window` is returned only when the cell owns no candidate sensor. The new prose sends authors and operators to exactly this preview to tell whether a sensor can see a target, and `09` teaches `no_window` as the no-pass reason. Fix in code: return `no_window` when no candidate had any window, and keep `sensor_contended` for windows that are all booked. Until then the prose could say what the preview shows. | Medium | `00-intake` (bug → `07` remediation); then `08-training-manual-authoring` if the prose needs an interim qualification |
| F3 | `ui_web/server.py` `POST /api/sessions` (`load`); `app.js::loadSession`; `06` and `WCM-2` ("stops the vignette from building a session" / "stops the vignette from loading") | A vignette with a malformed sensor field (a bad phase-angle range, and since `IP-1222` also an unknown radar `beam_mode` or a misspelt affinity) makes `POST /api/sessions` return a **bare HTTP 500 "Internal Server Error"** with no reason. The `ValidationError` from `build_world` is not caught. The console's `loadSession` has no `catch`, so **Load** visibly does nothing, and the reason appears only in the server log. The prose is accurate that the session will not build, but it gives the author no symptom and no place to find the reason. Reachable only with author-made content. Same silent-failure class as `BL-0196` (the Fire button). | Low | `00-intake` (bug: return a 400 naming the field, and surface it at Load); `08-training-manual-authoring` (say the symptom and that the reason is in the server console until fixed) |
| F4 | `07-white-cell-facilitation.md` controller-events table | Two small omissions. (a) The `sensor_outage` row gives the declared message but not the `restore` message (`<id>: sensor outage cleared`), though the `anomaly` row gives its `anomaly cleared` counterpart. (b) `forced_custody_loss` also resets the track's last-observation time to now, so decay restarts from `degrade_to` at the inject time. A facilitator planning a timed custody-loss inject would want that. Both observed live. | Low | `08-training-manual-authoring` |

## Verification runs (at `40af409`)

- `python3 -m pytest spacesim/tests/test_vignette_tutorials.py spacesim/tests/test_training.py -q`
  → **20 passed** (16 playbook + 4 training).
- Live-drive probes, the link/orphan/footer script and the HTTP 500 probe ran in the session
  scratchpad only. Nothing was written to the tree except this report and its ROADMAP
  review-theme entry.

## Pipeline position

Stage 09 peer (training review). This review wrote two files: this report and its ROADMAP
review-theme entry.

- F1 and F4 route to `08-training-manual-authoring`. F1 is `BL-0216`, and F4 can ride the same
  pass.
- F2 and F3 are code defects, so they route to `00-intake`. F2 matters more: the preview's
  reason is what the new prose relies on.

Next step: the most severe findings are both Medium. F1 is already scheduled. F2 needs a `07`
remediation package before the prose can rely on the preview reason, so file it ahead of, or
together with, the `BL-0216` authoring pass.
