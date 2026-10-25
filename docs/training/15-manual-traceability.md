[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 15. Per-cell manual traceability matrix

The **bidirectional cross-reference** that keeps the three role-scoped cell manuals
([White](12-white-cell-manual.md), with `WCM-12`–`WCM-16` in
[12a](12a-white-cell-analysis-and-exports.md), `WCM-17` in [12b](12b-white-cell-vignette-creator.md),
`WCM-18`–`WCM-20` in [12c](12c-white-cell-rules-and-staffing.md) and `WCM-21`–`WCM-25` in
[12d](12d-white-cell-clock-saves-and-controls.md) · [Blue](13-blue-cell-manual.md), `BLU-15`–`BLU-18` in
[13a](13a-blue-cell-rules-and-delivery.md) · [Red](14-red-cell-manual.md), `RED-14`–`RED-17` in
[14a](14a-red-cell-rules-and-delivery.md)) cheap to maintain. It exists so a change is never silently stranded
from its documentation:

- **Feature → manual (§15.1):** when you change a code feature, look it up here to see exactly
  which manual sections describe it, and update them in the same change.
- **Manual → feature (§15.2):** when you edit a manual section, this tells you which code and
  endpoints back it, so you can confirm the prose still matches reality.

Every manual section already carries an inline **`> Sources:`** footer naming its backing code —
this matrix is the inverse index that lets you start from the code instead. Keep both directions in
sync: **when you add or renumber a manual section, add its row to §15.2 and add its ID to every
feature row in §15.1 that it touches.** This upkeep rule is enforced by the pipeline hooks in
[`08-code-implementation`](../../.claude/skills/README.md) (code side) and the dedicated
training-corpus skills `08-training-manual-authoring` / `08-vignette-development` /
`09-training-manual-review` (see §15.3). The whole apparatus satisfies **FR-11120/FR-11210** of the
requirements baseline (the training corpus is a co-equal product — MSTR-001 §2).

Section IDs: `WCM-n` = White Cell manual, `BLU-n` = Blue cell manual, `RED-n` = Red cell manual.
The **vignette learning path** ([`16-learning-path.md`](16-learning-path.md)) is the corpus's
fourth traceable surface: it maps each vignette to the manual sections a trainee reads first and to
its playbook — §15.4 records that linkage's maintenance rule.

### 15.1 Feature → manual sections (forward index)

Start here when a **code feature changes**. The "Backing code (primary)" column names the module(s)
most likely to be edited; the manual sections are every place that behavior is documented.

| Feature / capability | Backing code (primary) | White | Blue | Red | Spec (FS) |
|---|---|---|---|---|---|
| Fog-of-war boundary & per-cell view | `session/cells.py` (`CellController`), `session/scene.py` | WCM-1, WCM-6 | BLU-1 | RED-1 | FS-103, FS-113 |
| Mission brief (`intro_brief`) | `content/vignette.py`, `server.py` `/brief` | WCM-2 | BLU-1 | RED-1 | FS-115 |
| Vignette load + parameter dials | `content/vignette.py`, `vignettes/*.yaml` | WCM-2 | — | — | FS-115 |
| `ops_fidelity` (tactical/realistic/full_ttc) | `content/vignette.py`, `bus.py` | WCM-2 | BLU-5 | RED-7 | FS-105 |
| Hot-seat / LAN / pop-out transport | `session/inprocess.py`, `server.py` | WCM-3 | — | — | FS-109, FS-114 |
| Server-authoritative clock, pause/jump; advance/step span bound (start + 366 days, forward-only, running clock pinned at the end) | `session/manager.py` (`step`, `advance_to`, `_span_ceiling`, `_catch_up_locked`), `engine/clock.py`, `app.js` (`stepBy`) | WCM-4 | — | — | FS-109 |
| Rewind / undo / branch (determinism); rewind bounds and refusal status line (`#control-status`; time, rewind and inject refusals; rewind/undo keep a running clock running) | `session/manager.py` (`rewind_to`, `undo_last`), `engine/simulation.py`, `server.py` (`/rewind`, `/undo`), `app.js` (`reportControlError`, `rewindTo`) | WCM-4, WCM-9 | — | — | FS-109, FS-110 |
| Injects + builder + library (incl. fire-time validation) | `content/inject_library.yaml`, `server.py` `/inject`, `session/manager.py` (`fire_inject`, `validate_inject_effects`, `_skip_inject_effect`), `app.js` (`fireBuiltInject`) | WCM-5 | — | — | FS-106, FS-108 |
| Activity timeline (Gantt) | `ui_web/static/app.js`, `session/scene.py` | WCM-6 | BLU-2 | RED-2 | FS-106 |
| Coaching notes | `content/vignette.py` (`Vignette.coaching`) | WCM-6 | — | — | FS-106 |
| Vignette tutorial step scripts (executable steps, both cells; deadlines stated in briefs) | `content/vignette.py` (`Vignette.tutorial`, `intro_brief`), `ui_web/static/app.js` (Tutorial panel), `tests/test_vignette_tutorials.py` (`_Learner`, `_script`) | — | — | — | FS-115 |
| Objectives / deadlines | `content/vignette.py`, `server.py` `/objectives` | WCM-6 | BLU-10 | RED-9 | FS-106 |
| TLE force-add | `engine/propagator.py`, `server.py` `/force/tle` | WCM-7 | — | — | FS-119 |
| Red doctrine presets + `red_step` | `session/redai.py` | WCM-8 | — | RED-8 | FS-111 |
| AAR replay / scrub / branch-compare | `session/aar.py` | WCM-9 | — | — | FS-107 |
| AAR playback routes and seat rules (single shared cursor per session; no console control) | `session/inprocess.py` (`playback_seat_decision`), `server.py` (`/aar/playback/*`) | WCM-9 | — | — | FS-128 |
| Save / resume (incl. refused load: `validate_save`, 366-day span cap) | `engine/simulation.py`, `session/manager.py` (`validate_save`), `server.py` `/save`, `/load_save` | WCM-10 | — | — | FS-110 |
| White-only seat enforcement (403 without `?cell=white`; creation refusal; seat-aware palette time and inject entries; Load refusal keeps the session readout; Observer sends no dry-run; refusal messages on Load / Save as scenario / Creator) | `server.py` (`_require_white`, `_refuse_player_seat_on_create`, `_reject_observer`), `app.js` (`PALETTE`, `reportControlError`, `showLoadFailure`, `saveAsScenario`, `previewOrder`, `drawRibbon`), `creator.js` | WCM-4, WCM-10 | — | — | FS-109, FS-113 |
| Clock-lag watchdog | `session/manager.py` (`_record_catch_up_lag`) | WCM-10 | — | — | FS-109 |
| Plan-first commanding + delivery paths | `engine/orders.py`, `engine/access.py` | — | BLU-2 | RED-2 | FS-102, FS-129 |
| Dry-run validity preview | `engine/orders.py` (`dry_run`) | — | BLU-3 | RED-3 | FS-101 |
| Consequence preview | `server.py` `/preview/consequence`, `engine/effects.py` | — | BLU-3 | RED-3, RED-5 | FS-101 |
| Maneuver assistant (6 modes) | `engine/maneuver.py` | — | BLU-3, BLU-8 | RED-3 | FS-101, FS-105 |
| ISR/observe assistant | `engine/isr.py` | — | BLU-3, BLU-4 | RED-3, RED-4 | FS-104 |
| Jam assistant + footprint | `engine/jam.py` | — | BLU-3, BLU-6 | RED-3, RED-5 | FS-101 |
| SDA tasking → custody → unlock | `engine/custody.py`, `engine/access.py` | — | BLU-4 | RED-4 | FS-103, FS-104 |
| Weapons-quality gate | `engine/custody.py` | — | BLU-4 | RED-4, RED-5 | FS-103 |
| Sensor modality authoring fields (`exclusion_angle_deg`, `min_range_km`, `altitude_band_affinity`, `requires_cue` incl. the `auto` skip, `host_asset_id`, `usable_phase_angle_deg`, radar `fence`/`dish` `beam_mode` incl. the command-menu raw-JSON path and the Mode-dropdown override; load-time checks), field table in `06`; observe rejection reasons (`no_window` vs `sensor_contended`, `requires_cue`, `invalid_param`) in `09` §10 | `engine/entities.py` (`Sensor`, `_check_usable_phase_angle`, `_check_radar_beam_mode`), `engine/access.py` (`_observation_predicate`, `_sensor_orbit`), `engine/orders.py` (`_validate`, `_observe_params_ok`, `_candidate_sensors`, `_auto_blocked_by_cue`, `_plan_collection`, `_resolve_sensor_id`, `_observation_phase_angle_deg`, radar mode in `_exec_payload`), `engine/isr.py` (`effective_gain`, `altitude_band`, `phase_angle_factor`, `BEAM_MODES["ground_radar"]`), `app.js` (`REASON_TIPS`, `composeBody`, `ACTIONS_BY_KIND`, `PARAM_TEMPLATE.observe`), `index.html` (`#task-beam-mode`) | WCM-2 | BLU-4 | RED-4 | FS-122 |
| Order-param shape check (`invalid_param` for every action; `null` = absent), `09` §10 | `engine/orders.py` (`_order_params_ok`, `ORDER_PARAM_RULES`, `_observe_params_ok`, called in `_validate`), `app.js` (`REASON_TIPS`) | — | BLU-3 | RED-3 | FS-101 |
| Bus/payload SOH + safe mode | `engine/bus.py`, `engine/busmodel.py` | WCM-2 | BLU-5 | RED-7 | FS-105 |
| Telemetry signatures + nominal ghost (history graph, per-instant) | `engine/telemetry.py`, `session/manager.py` (`get_series`), `session/aar.py` (`worlds_at_times`), `GET /telemetry/{cell}/{asset}/{param}` | WCM-6 | BLU-6 | RED-7 | FS-105 |
| Safe-mode recovery chain | `engine/recovery.py`, `engine/buscommands.py` | — | BLU-7 | RED-7 | FS-105 |
| Bus/payload command verbs | `engine/buscommands.py` | — | BLU-7 | RED-7 | FS-105, FS-116 |
| Conjunctions + collision avoid | `world.conjunctions`, `prop.collision_avoid` | — | BLU-8 | — | FS-105 |
| Cyber (off-pass exception) | `engine/cyber.py` | — | BLU-9 | RED-6 | FS-101 |
| Five D's effects | `engine/effects.py` | — | — | RED-5 | FS-101 |
| Kinetic engagement + ROE gate | `engine/engage.py` | — | — | RED-5 | FS-132 |
| Effect resource bounds (salvo limited to rounds left: `no_ammo`/`insufficient_ammo` at preview + issue, execute-time re-check of queued strikes, every fired salvo charged, hit or miss; jamming leaves the jammer's `power_w` unchanged), `09` §10 | `engine/orders.py` (`_validate`, `_engage_rounds`, `_h_effect`, jam plan), `app.js` (`REASON_TIPS.insufficient_ammo`) | — | — | RED-3, RED-5 | FS-132 |
| RPO / co-orbital proximity | `engine/access.py` (`rpo_proximity`) | — | BLU-6 | RED-5 | FS-101 |
| Per-cell playbooks / tutorial (incl. the `training-basics` onboarding script, `04-guided-vignette.md`, §11.0) | `test_vignette_tutorials.py`, `test_training.py`, `/vignettes/{id}/tutorial` | WCM-2 | BLU-10 | RED-9 | FS-115 |
| Vignette library (add/move/retire) | `content/vignettes/*.yaml` | WCM-2 | BLU-10 | RED-9 | FS-115 |
| Learning-path sequence & rung linkage | `16-learning-path.md`, `content/vignettes/*.yaml` | WCM-2 | BLU-10 | RED-9 | FS-115 |
| Classification banner | `content/vignette.py` (`Vignette.classification`), `session/manager.py`, `session/aar.py` | WCM-2 | — | — | FS-112 |
| Observer read-only seat (4th cell, no command ability) | `session/inprocess.py` (`set_observer_view`/`get_observer_view`), `ui_web/server.py` (`_reject_observer`) | WCM-1 | — | — | FS-113 |
| Load-time vignette validation (refused **Load**: `Load failed:` + every problem as *where — reason*; no session made, nothing evicted, no `sess-N` used; 404 for an unknown id; `build` item only once nothing else is wrong; an unparseable file is left out of the picker), rule list in `06` "When a vignette won't load", symptom in `09` §10 | `content/vignette.py` (`load_vignette`, `validate_vignette`, `VignetteValidationError`, `list_vignettes`), `session/inprocess.py` (`load_vignette`), `ui_web/server.py` (`_vignette_load_errors`), `app.js` (`loadSession`) | WCM-2 | — | — | FS-131 |
| External vignette folders + user save folder (`content:` config; two-key setup to load saves back) | `config.py` (`ContentConfig`), `content/vignette.py` (`list_vignettes`), `content/vignette_export.py` (`save_vignette`) | `01` §2.2 (shared) | — | — | FS-118 |
| Seat-to-role assignment / staffing gate | `content/vignette.py` (`Vignette.roles_needed`), `session/manager.py` (`assign_role`/`staffing_report`) | WCM-2 | — | — | FS-116 |
| Competency assessment (custody/window/divergence rubric) | `session/assessment.py`, `GET /assessment` | WCM-11 | — | — | FS-201 |
| Research analytics (offline batch export) | `tools/research_batch.py`, `session/research_export.py` | WCM-12 | — | — | FS-301 |
| Live RIC frame view + CATS phase-angle overlay | `engine/sun.py` (`cats_phase_angle_deg`), `session/ephemeris.py` (`live_ric_view`), `GET /ric_view/{cell}` | WCM-13 | BLU-11 | RED-10 | FS-130 |
| Quick TLE export (own satellites at actual orbit + tracked objects at belief; White: ground truth) | `engine/tle_export.py`, `session/ephemeris.py` (`quick_tle`), `GET /tle/{cell}`, `tleexport.js` (`candidates`, `SOURCE_LABEL`) | WCM-14 | BLU-12 | RED-11 | FS-121 |
| Ephemeris export, time-span (ECI/RIC, CSV/CCSDS OEM, truth + cell-observed) | `session/ephemeris.py` (`truth_ephemeris`, `cell_observed_ephemeris`, `write_csv`/`write_oem`/`write_ric_csv`, `sample_times`/`MAX_EXPORT_SAMPLES`), `session/aar.py` (`worlds_at_times`), `GET /ephemeris/truth`, `GET /ephemeris/{cell}` | WCM-15 | BLU-13 | RED-12 | FS-121 |
| Per-asset telemetry CSV export, time-span | `session/manager.py` (`telemetry_export`), `engine/telemetry.py` (`sample`, per-instant replay), `session/aar.py` (`worlds_at_times`), `session/ephemeris.py` (`sample_times`/`MAX_EXPORT_SAMPLES`), `GET /telemetry/{cell}/{asset}/export.csv` | WCM-16 | BLU-14 | RED-13 | FS-126 |
| Vignette Creator (draft session, TLE / lat-long asset entry, curated site picker, asset menu, JSON view, preview, seat declaration, save as vignette, play it) | `static/creator.js`, `session/manager.py` (`creator_*`, `declare_seats`), `content/vignette_export.py`, `config.py` (`ContentConfig`), `POST /api/sessions/draft`, `PUT /creator/state`, `POST /save_vignette` | WCM-17 | — | — | FS-117 |
| Operator seat + role-scoped commands (`roles_needed`, assign, staffing report, `role_scope_*` refusals, scope read) | `session/manager.py` (`assign_role`, `role_scope_check`, `staffing_report`), `static/app.js` (`o-seat`, `REASON_TIPS`), `GET /roles/scope`, `POST /roles/assign` | WCM-2, WCM-18 | BLU-15 | RED-14 | FS-116 |
| Approval gates (`pending_approval`, decide) and live ROE changes | `engine/orders.py` (`decide_gated_order`, `issue_roe_change`, `_matching_gate`, `rebuild_pending`), `POST /gate/decide`, `POST /roe/change` | WCM-19 | BLU-16 | RED-15 | FS-127 |
| Pending-inject queue, edit/cancel, condition injects, owner-fact fog (`_notice_by_owner`) | `session/manager.py` (`pending_injects`, `edit_inject`, `cancel_inject`, `_h_condition_check`, `_notice_by_owner`), `static/app.js` (`renderPendingInjects`) | WCM-5, WCM-20 | — | — | FS-106, FS-108 |
| Time-control bounds and refusal messages; clock-rate bounds | `session/manager.py` (`step`, `advance_to`, `rewind_to`, `undo_last`, `set_clock`), `ui_web/server.py` | WCM-4, WCM-21 | — | — | FS-109 |
| Save contents, Load refusals/warnings, save-as-scenario carry-over | `session/manager.py` (`save_state`, `validate_save`, `from_state`), `content/vignette_export.py`, `POST /load_save` | WCM-10, WCM-22 | — | — | FS-110, FS-120 |
| Force-add before Start (TLE, bulk TLE/OMM) and its refusals | `session/manager.py` (`add_tle`, `bulk_import`, `_force_add_omm_object`), `content/bulk_import.py` | WCM-7, WCM-23 | — | — | FS-119 |
| Which seat sees which console controls | `static/app.js` (`setCell`), `static/index.html` (`white-only`), `ui_web/server.py` (`_require_white`, `_reject_observer`) | WCM-24 | — | — | FS-113 |
| Delivery paths and link-scoped jamming (`ground_uplink` / `isl_relay` / `stored_program`; `link_target`) | `engine/orders.py` (`_delivery_jammed`), `engine/effects.py` (`is_link_denied`) | — | BLU-17 | RED-16 | FS-129 |
| Manoeuvre ledger and export time formats | `session/manager.py` (`maneuver_ledger`), `GET /maneuver_ledger/{cell}/{asset}` | WCM-15, WCM-16 | BLU-18 | RED-17 | FS-125 |
| Space-weather index coupling (`space_weather` inject with `index_series`; drag / anomaly rate; vignette `space_weather_series`) | `engine/perturbations.py`, `session/manager.py` (`_apply_inject_effects`) | WCM-25 | — | — | FS-123 |
| Debris persistence estimate (`persistence_estimate` in ground-truth `debris`; weeks / years / centuries by altitude) | `engine/effects.py` (`_persistence_estimate`, `DebrisField`) | WCM-25 | — | — | FS-124 |
| Per-effect-class attribution / detectability configuration (`effect_detectability_config`) | `engine/effects.py` (`ModerateEffectResolver`), `content/vignette.py` | WCM-25 | — | — | FS-129 |
| Hot-seat hand-off (**⏸ Handover** overlay: `HANDING OFF → RED`, then its **Resume** switches seat) | `static/app.js` (handover), `static/index.html` | WCM-3 | BLU-1 | RED-1 | FS-114 |
| *Not operator-visible (test / CI tooling):* test-origin traceability, the browser console-rule suite, documentation-integrity checks | `tests/test_test_origins.py`, `tests/test_browser_console_rules.py`, `tests/test_doc_integrity.py` | — (developer-only; no operator surface) | — | — | FS-133, FS-134, FS-135 |

### 15.1a Feature → shared modules (`01`–`11`)

*Added 2026-10-17 (`BL-0197`).* §15.1 indexes the role manuals only. A feature change can also
strand walkthrough and reference prose in the shared modules, as the target picker did (`BL-0084`
updated §10 and the role manuals, while `03`/`04`/`11` went stale until `BL-0194`/`BL-0195`).
When a feature in §15.1 changes, also check the shared sections its group names here. Section
names are the module's own headings.

| Feature group (§15.1 rows) | Shared module sections to check |
|---|---|
| Install, server launch, config, LAN binding | `01` §1–§2, §2.1, §2.2 · `09` §10 |
| Vignette load, picker, seed, load failures, external vignette folders | `01` §2.2 · `02` "The scenario picker" · `03` Step 1 · `06` "When a vignette won't load" · `09` §10 · `10` §10.1.1 |
| Mission brief | `02` "Mission brief — read this first" |
| Fog-of-war, god-view, Observer | `02` "White Cell god-view", "A player cell (fog-of-war)" |
| Hot-seat, LAN, pop-outs | `01` §2.1 · `10` §10.1 (Handover), §10.1.2 · `10b` §10.14 |
| Clock, pause/jump, rewind/undo/branch, refusal status line | `03` Steps 3–4 · `10` §10.1, §10.2 · `05` "Red doctrine & After-Action Review" |
| White-only seat enforcement, command-palette seat entries, scrollable View menu | `08` §9 · `10` §10.1, §10.1.2 · `10b` §10.14 · `05` "Adding real satellites by TLE", "Save & resume" · `07` §8 |
| Compose form, target picker, params, dry-run, `invalid_param`, reason tips | `02` "Commanding & White Cell menus", "Order-composition assistants" · `03` Step 2 · `04` (all three walkthroughs) · `05` "Plan-first commanding", "Live previews before commit" · `09` §10 · `10a` §10.6 · `11` (every playbook) |
| Maneuver / jam / engage / cyber assistants, consequence preview | `02` "Order-composition assistants", "Consequence preview & conjunction screening" · `05` "Live previews before commit" · `10a` §10.7–§10.8 |
| Sensor tasking, SSN, beam modes, custody, weapons-quality gate, sensor modality fields | `04` Blue/Red Step 2 · `05` "SDA sensor tasking → custody → unlock" · `06` "Authoring sensors: optional modality fields" · `10a` §10.5 · `11` |
| Effect resource bounds, kinetic engagement, ROE | `05` "Live previews before commit" · `09` §10 · `11` §11.5 |
| Activity timeline (Gantt) | `02` "Per-cell activity timeline (Gantt)" · `10b` §10.15 |
| Injects + builder + library | `02` "White-Cell inject builder" · `07` §8 · `09` §10 · `10` §10.3 |
| Bus SOH, safe mode, recovery, telemetry, drill-down | `04` "Blue — recover from the cyber attack" · `05` "Bus state-of-health & safe mode", "Safe-mode recovery", "Diagnosing attacks from telemetry" · `10b` §10.13 |
| Cyber | `04` Red walkthrough, Blue recovery · `05` "Cyber — the off-pass exception" |
| Conjunctions / collision avoid | `02` "Consequence preview & conjunction screening" · `05` "Conjunctions & collision avoidance" · `10` §10.2 |
| TLE force-add | `05` "Adding real satellites by TLE" |
| AAR, Red doctrine | `05` "Red doctrine & After-Action Review" · `10b` §10.12 |
| Save / resume | `05` "Save & resume" · `08` §9 · `10` §10.1.3 |
| Viewers (globe, map), accessibility, local time | `02` "Viewers — 2D map and 3D globe", "Local time + accessibility toggles" · `10` §10.1.2, §10.2 · `10b` §10.10–§10.11 |
| Any HTTP route added, renamed or reshaped | `08` §9 |
| Vignette library, playbooks, learning path | `06` (track tables) · `11` · `16` |
| Any new term an operator meets | `09` §11 Glossary |

> **Sources:** this index is derived from the shared modules' own headings (`01`–`11`, `10a`,
> `10b`) and §15.1's feature rows; it carries no code anchors of its own.

### 15.2 Manual section → backing features (reverse index)

Start here when you **edit a manual section** and want to confirm it still matches the code. This
mirrors each section's inline `> Sources:` footer.

#### White Cell manual (`WCM-n`)

`WCM-1`–`WCM-11` are in [`12-white-cell-manual.md`](12-white-cell-manual.md);
`WCM-12`–`WCM-16` are in [`12a-white-cell-analysis-and-exports.md`](12a-white-cell-analysis-and-exports.md);
`WCM-17` is in [`12b`](12b-white-cell-vignette-creator.md), `WCM-18`–`WCM-20` in [`12c`](12c-white-cell-rules-and-staffing.md)
and `WCM-21`–`WCM-25` in [`12d`](12d-white-cell-clock-saves-and-controls.md).

| § | Topic | Backing code / endpoints |
|---|---|---|
| WCM-1 | Role and view | `session/manager.py`, `session/cells.py` (`CellController`), `session/inprocess.py` (Observer, FR-6510) |
| WCM-2 | Set up the exercise | `content/vignette.py`, `vignettes/*.yaml`, `/brief/{cell}`, `session/manager.py` (classification, seat-to-role), `engine/entities.py` (`Sensor` modality fields, `_check_radar_beam_mode`), `content/vignette.py` (`validate_vignette`, `VignetteValidationError`, `list_vignettes`), `app.js` (`loadSession`, Load-failed readout) |
| WCM-3 | Hot-seat / LAN / pop-out | `session/inprocess.py`, `server.py` (`/api/sessions`) |
| WCM-4 | Time control | `session/manager.py` (`step`, `advance_to`, `_span_ceiling`, `rewind_to`, `undo_last`), `engine/clock.py`, `/clock`, `/step`, `/advance`, `/rewind`, `/undo`, `app.js` (`stepBy`, `rewindTo`, `reportControlError`), `#control-status` |
| WCM-5 | Injects | `content/inject_library.yaml`, `/inject`, `session/manager.py` (`fire_inject`, `validate_inject_effects`, `_skip_inject_effect`), `app.js` (`fireBuiltInject`, `fireInject`) |
| WCM-6 | Monitor both sides | `session/scene.py`, `app.js` (incl. `openDrill`), `Vignette.coaching`, `session/manager.py` (`get_telemetry`/`get_series`) |
| WCM-7 | TLE add | `engine/propagator.py`, `/force/tle` |
| WCM-8 | AI-Red doctrine | `session/redai.py`, `/red_step` |
| WCM-9 | After-Action Review | `session/aar.py`, `/aar*`, `/aar/playback/*`, `session/inprocess.py` (`playback_seat_decision`) |
| WCM-10 | Save/resume + lag watchdog | `engine/simulation.py`, `/save`, `/load_save` (`validate_save`), `_record_catch_up_lag` |
| WCM-11 | Competency assessment | `session/assessment.py`, `/assessment` |
| WCM-12 | Offline research batch exports | `tools/research_batch.py`, `session/research_export.py` |
| WCM-13 | RIC frame view & CATS phase angle (ground truth) | `engine/sun.py`, `session/ephemeris.py` (`live_ric_view`), `/ric_view/{cell}` |
| WCM-14 | Quick TLE export (ground truth) | `engine/tle_export.py`, `session/ephemeris.py` (`quick_tle`), `session/manager.py` (`get_tle`), `/tle/{cell}`, `tleexport.js` |
| WCM-15 | Ephemeris export, ground truth (URL-only) | `session/ephemeris.py` (`truth_ephemeris`, `sample_times`/`MAX_EXPORT_SAMPLES`), `session/aar.py` (`worlds_at_times`), `/ephemeris/truth` |
| WCM-16 | Per-asset telemetry CSV export (URL-only) | `session/manager.py` (`telemetry_export`), `engine/telemetry.py`, `session/aar.py` (`worlds_at_times`), `session/ephemeris.py` (`sample_times`/`MAX_EXPORT_SAMPLES`), `/telemetry/{cell}/{asset}/export.csv` |
| WCM-17 | Vignette Creator | `static/creator.js`, `session/manager.py` (`creator_set_state`, `creator_edit_asset`, `declare_seats`), `content/vignette.py` (`asset_authoring_problems`), `content/vignette_export.py`, `config.py` (`ContentConfig`) |
| WCM-18 | Operator seats and roles | `session/manager.py` (`assign_role`, `staffing_report`, `role_scope_check`), `session/inprocess.py` (`start`), `static/app.js` |
| WCM-19 | Approval gates and live ROE | `engine/orders.py` (`decide_gated_order`, `issue_roe_change`), `/gate/decide`, `/roe/change` |
| WCM-20 | Injects in depth | `session/manager.py` (`pending_injects`, `edit_inject`, `_h_condition_check`, `_notice_by_owner`), `static/app.js` |
| WCM-21 | Time controls: bounds and messages | `session/manager.py` (`step`, `advance_to`, `rewind_to`, `undo_last`, `set_clock`), `/step`, `/advance`, `/rewind`, `/undo`, `/clock` |
| WCM-22 | Save and resume | `session/manager.py` (`save_state`, `validate_save`, `from_state`), `/save`, `/load_save`, `content/vignette_export.py` |
| WCM-23 | Add satellites before Start | `session/manager.py` (`add_tle`, `bulk_import`), `content/bulk_import.py`, `/force/tle`, `/force/bulk_import` |
| WCM-24 | Which controls each seat sees | `static/app.js` (`setCell`), `static/index.html`, `ui_web/server.py` (`_require_white`, `_reject_observer`) |
| WCM-25 | Space weather, debris persistence, attribution settings | `engine/perturbations.py` (`index_series_problems`), `engine/effects.py` (`_persistence_estimate`, `ModerateEffectResolver`), `session/manager.py` (`_apply_inject_effects`) |

#### Blue cell manual (`BLU-n`)

| § | Topic | Backing code / endpoints |
|---|---|---|
| BLU-1 | Fog-of-war view | `session/cells.py` (`CellController`), `session/scene.py`, `/brief/blue` |
| BLU-2 | Plan-first commanding | `engine/orders.py` |
| BLU-3 | Previews before commit | `engine/orders.py` `dry_run`, `_order_params_ok`/`ORDER_PARAM_RULES`, `/preview/consequence`, `engine/{maneuver,isr,jam}.py` |
| BLU-4 | SDA tasking loop | `engine/custody.py`, `engine/access.py` (`_observation_predicate`), `engine/orders.py` (`requires_cue`, `_candidate_sensors`, `_plan_collection`, `_resolve_sensor_id`, observe mode in `_exec_payload`), `index.html` (`#task-beam-mode`) |
| BLU-5 | Bus health | `engine/bus.py`, `engine/busmodel.py` |
| BLU-6 | Diagnose from telemetry | `engine/telemetry.py`, `session/manager.py` (`get_series`), `session/aar.py` (`worlds_at_times`), `/telemetry/{cell}/{asset}/{param}` |
| BLU-7 | Recovery | `engine/recovery.py`, `engine/buscommands.py` |
| BLU-8 | Maneuver & conjunctions | `world.conjunctions`, `prop.collision_avoid`, `engine/maneuver.py` |
| BLU-9 | Cyber posture | `engine/cyber.py` |
| BLU-10 | Win the vignette | `11-vignette-playbooks.md`, `/vignettes/{id}/tutorial` |
| BLU-11 | RIC frame view & CATS phase angle | `engine/sun.py`, `session/ephemeris.py` (`live_ric_view`), `/ric_view/{cell}` |
| BLU-12 | Quick TLE export | `engine/tle_export.py`, `session/ephemeris.py` (`quick_tle`, own-satellite branch), `/tle/{cell}`, `tleexport.js` (`candidates`, `SOURCE_LABEL`) |
| BLU-13 | Ephemeris export, your own belief (URL-only) | `session/ephemeris.py` (`cell_observed_ephemeris`, `sample_times`/`MAX_EXPORT_SAMPLES`), `session/aar.py` (`worlds_at_times`), `/ephemeris/{cell}` |
| BLU-14 | Your telemetry CSV export (URL-only) | `session/manager.py` (`telemetry_export`), `engine/telemetry.py`, `session/aar.py` (`worlds_at_times`), `session/ephemeris.py` (`sample_times`/`MAX_EXPORT_SAMPLES`), `/telemetry/{cell}/{asset}/export.csv` |
| BLU-15 | Operator seat field | `static/app.js` (`REASON_TIPS`, `refreshRoleScope`), `session/manager.py` (`role_scope_check`) |
| BLU-16 | Orders awaiting approval; ROE changes | `engine/orders.py` (`decide_gated_order`, `_effective_roe`), `session/manager.py` (`list_orders`) |
| BLU-17 | Delivery paths and jamming | `engine/orders.py` (`_delivery_jammed`), `engine/effects.py` (`is_link_denied`) |
| BLU-18 | Manoeuvre ledger; export time formats | `session/manager.py` (`maneuver_ledger`), `session/ephemeris.py` (`sample_times`) |

#### Red cell manual (`RED-n`)

| § | Topic | Backing code / endpoints |
|---|---|---|
| RED-1 | Fog-of-war view | `session/cells.py` (`CellController`), `session/scene.py`, `/brief/red` |
| RED-2 | Plan-first commanding | `engine/orders.py` |
| RED-3 | Previews before commit | `engine/orders.py` `dry_run`, `_order_params_ok`/`ORDER_PARAM_RULES`, `_engage_rounds` (`insufficient_ammo`), `/preview/consequence`, `engine/{maneuver,isr,jam}.py` |
| RED-4 | SDA targeting | `engine/custody.py`, `engine/access.py` (`_observation_predicate`), `engine/orders.py` (`requires_cue`, `_candidate_sensors`, `_plan_collection`, `_resolve_sensor_id`, observe mode in `_exec_payload`), `index.html` (`#task-beam-mode`) |
| RED-5 | Five D's / effects | `engine/effects.py`, `engine/{jam,engage}.py`, `engine/access.py`, `engine/orders.py` (`_validate` `no_ammo`/`insufficient_ammo`, `_engage_rounds`, `_h_effect`), `app.js` (`REASON_TIPS.insufficient_ammo`) |
| RED-6 | Cyber wildcard | `engine/cyber.py` |
| RED-7 | Own-force management | `engine/bus.py`, `engine/recovery.py`, `engine/telemetry.py`, `session/manager.py` (`get_series`), `session/aar.py` (`worlds_at_times`), `app.js` (`renderFleet`/`rollup`), `vignettes/*.yaml` (`red_forces`, no `bus_state`) |
| RED-8 | Doctrine profiles | `session/redai.py` |
| RED-9 | Win the vignette | `11-vignette-playbooks.md`, `/vignettes/{id}/tutorial` |
| RED-10 | RIC frame view & CATS phase angle | `engine/sun.py`, `session/ephemeris.py` (`live_ric_view`), `/ric_view/{cell}` |
| RED-11 | Quick TLE export | `engine/tle_export.py`, `session/ephemeris.py` (`quick_tle`, own-satellite branch), `/tle/{cell}`, `tleexport.js` (`candidates`, `SOURCE_LABEL`) |
| RED-12 | Ephemeris export, your own belief (URL-only) | `session/ephemeris.py` (`cell_observed_ephemeris`, `sample_times`/`MAX_EXPORT_SAMPLES`), `session/aar.py` (`worlds_at_times`), `/ephemeris/{cell}` |
| RED-13 | Your telemetry CSV export (URL-only) | `session/manager.py` (`telemetry_export`), `engine/telemetry.py`, `session/aar.py` (`worlds_at_times`), `session/ephemeris.py` (`sample_times`/`MAX_EXPORT_SAMPLES`), `/telemetry/{cell}/{asset}/export.csv` |
| RED-14 | Operator seat field | `static/app.js` (`REASON_TIPS`, `refreshRoleScope`), `session/manager.py` (`role_scope_check`) |
| RED-15 | Orders awaiting approval; ROE changes | `engine/orders.py` (`decide_gated_order`, `_effective_roe`) |
| RED-16 | Which link to jam | `engine/orders.py` (`_delivery_jammed`), `engine/effects.py` (`is_link_denied`) |
| RED-17 | Manoeuvre ledger | `session/manager.py` (`maneuver_ledger`) |

### 15.3 Maintenance protocol (how this stays true)

The matrix is only useful if it stays current. Two mechanisms keep it so:

1. **Inline `> Sources:` footers** on every manual section are the ground truth; §15.1/§15.2 are
   the inverse index derived from them. On any edit, the footer and the matrix row move together.
2. **Pipeline hook.** Stage `08-code-implementation` includes the cell manuals in its
   documentation-update step: when an Implementation Package's `Documentation Updates` field (or the
   §15.1 lookup for the code it touched) names a manual section, that section — and this matrix row
   — are updated in the same package. Stage `10-integration-review`'s documentation-coherence
   dimension spot-checks that a shipped feature change did not leave a manual section stale.

If you change a feature in §15.1 and the manual section still reads correctly, no edit is needed —
but confirm it, don't assume it.

### 15.4 Vignette ⇄ learning-path linkage

The learning path ([`16-learning-path.md`](16-learning-path.md)) is the fourth traceable surface,
maintained by `08-vignette-development` and reviewed by `09-training-manual-review`:

- **Every vignette appears on exactly one rung** (FR-11310). Add/move/retire a vignette →
  its rung, its [§11 playbook](11-vignette-playbooks.md) entry, its
  [§6 library](06-the-vignette-library.md) row, and any vignette count in README/CLAUDE.md move
  in the same change set.
- **Every rung links its manual prerequisites and playbook** (FR-11320) — those links resolve to
  real sections here in the corpus. A renamed manual section that a rung's "Read first" points at
  must update the rung too.
- **The playbooks the rungs link to are machine-verified** by
  `spacesim/tests/test_vignette_tutorials.py` (FR-11420) — that test is the one automated staleness
  gate in the whole training corpus; keep it green when a vignette script changes. Since 2026-10-25 it
  also *executes* every step of the scripted vignettes' tutorials on a fixed seed (a step without a
  check fails the suite) and asserts each brief states the engine's real deadline, so a re-timed
  scenario fails here before it misleads a learner.

**Per-vignette linkage table** (rung ⇄ playbook ⇄ library; 19 rows, one per vignette):

| Vignette | Learning-path rung | Playbook (`11`) | Library row (`06`) |
|---|---|---|---|
| `training-basics` | Stage 0 | [11.0](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |
| `leo-isr-denial` | Stage 1 | [11.1](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |
| `geo-rpo-shadowing` | Stage 1 | [11.2](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |
| `gnss-ew-campaign` | Stage 1 | [11.3](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |
| `co-orbital-threat-escort` | Stage 1 | [11.4](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |
| `da-asat-crisis` | Stage 1 | [11.5](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |
| `satcom-cyber-link` | Stage 1 | [11.6](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |
| `sda-custody-hunt` | Stage 1 | [11.7](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |
| `multi-domain-taiwan` | Stage 1 | [11.8](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |
| `mt-isr-sar` | Stage 2 | [11.9](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |
| `mt-sigint-geolocate` | Stage 2 | [11.12](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |
| `mt-weather-collect` | Stage 2 | [11.10](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |
| `coa-russia-ml` | Stage 3 | [11.14](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |
| `coa-russia-md` | Stage 3 | [11.15](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |
| `coa-china-ml` | Stage 3 | [11.16](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |
| `coa-china-md` | Stage 3 | [11.17](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |
| `coa-misc-iran-ml` | Stage 3 | [11.18](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |
| `learn-intermediate-recovery` | Stage 4 | [11.13](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |
| `nv-isl-relay-debris` | Stage 4 | [11.11](11-vignette-playbooks.md) | [06](06-the-vignette-library.md) |

### 15.5 Requirements footing

This apparatus is not just convention — it satisfies a requirements-baseline family:
FR-11110 (role-scoped coverage), FR-11120 (source anchoring = the `> Sources:` footers),
FR-11210 (this bidirectional index), FR-11310/FR-11320 (§15.4 learning-path linkage),
FR-11410 (currency rides the changing package), FR-11420 (machine-verified playbooks), and
NFR-3400–3600 (accuracy / modularity / learner-appropriate presentation). See
[`docs/requirements/01-functional-requirements.md`](../requirements/01-functional-requirements.md)
§FR-11000 and [`02-non-functional-requirements.md`](../requirements/02-non-functional-requirements.md)
§16.

### 15.6 Layout evaluation (`BL-0026`)

**Question:** FR-11110 mandates role-scoped *coverage*, not the current per-cell-monolith layout
(`training/12-14`) specifically — the project owner asked (2026-07-04) whether a task-oriented cut
across cells would serve trainees better, now that
[R606](../research/encyclopedia/R606-minimalist-and-procedural-documentation.md) (minimalist,
task-centered technical documentation — Carroll's *The Nurnberg Funnel*) grounds the decision.

**R606's success criterion:** judge by task-completion speed for a reader mid-task, not by
comprehensiveness — "can a Blue operator who just hit a jam signature find the diagnosis procedure
fast, with minimal irrelevant material in the way," not "does this cover every mechanic somewhere."

**Evaluation.** Two structural options were weighed against that criterion:

1. **Per-cell (current).** Each of `BLU-n`/`RED-n`/`WCM-n` is already a *procedure layer*, not a
   reference — it deep-links shared concept modules (`05-core-concepts.md`,
   `02-interface.md`) rather than re-explaining mechanics, which is already the minimalist instinct
   R606 asks for. Almost every task a Blue or Red operator actually performs mid-exercise is
   inherently role-specific (Blue's SDA custody loop and Red's SDA targeting loop use the same
   engine mechanic but are procedurally distinct decisions), so a reader mid-task lands on exactly
   the section for their own role's version of that task with nothing from the other cell's
   perspective in the way — a fast path by R606's own standard.
2. **Task-oriented (cutting across cells).** A small number of mechanics genuinely mirror each
   other across Blue/Red — cyber (`BLU-9`/`RED-6`), previews-before-commit (`BLU-3`/`RED-3`), and
   SDA (`BLU-4`/`RED-4`) are the same underlying engine behavior read from each side. A unified
   "Cyber" or "Previews" module could serve both roles from one file. But collapsing these into
   cross-cell modules would cost the exact thing each per-cell manual already has going for it: a
   reader mid-task would now have to skip past the *other* cell's half of the module to find their
   own — for a corpus this size (9-10 sections per manual, each within NFR-3500's 50-300-line
   budget), that cost is not clearly recovered by the shared-authoring convenience it buys.

**Recommendation: keep the per-cell layout.** It already satisfies FR-11110's coverage mandate and
R606's task-completion-speed criterion for the large majority of sections. Restructuring the whole
corpus is not warranted by the evidence above. What *is* warranted, and applied in this same pass:
**cross-link the small set of genuinely mirror-image sections** so a reader who wants the other
side's version of the same mechanic can jump directly, rather than searching — `BLU-9`↔`RED-6`
(cyber), `BLU-3`↔`RED-3` (previews-before-commit), `BLU-4`↔`RED-4` (SDA) each now carry a one-line
"see also" cross-reference. This gets R606's cross-cutting benefit at near-zero restructuring cost,
without regressing the per-cell procedure-layer property that already works.

**Revisit trigger:** if the corpus grows enough that a single manual exceeds NFR-3500's module-count
guidance, or if a future role (beyond White/Blue/Red/Observer) needs a mechanic that spans more than
two cells, re-run this evaluation — the "small number of genuine mirrors" premise above would no
longer hold at that scale.

**Trigger check (2026-10-17, `BL-0035`): not fired.** The role manuals are 227 (`12`), 152 (`12a`),
280 (`13`) and 283 (`14`) lines, each inside NFR-3500's ~300-line guide; the White manual's 2026
split into `12`/`12a` kept each module in budget rather than signalling a layout problem. The seats
are still White, Blue, Red and Observer. Re-check at the next role added or the next manual past
300 lines.

---
