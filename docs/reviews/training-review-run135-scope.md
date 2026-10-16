[↑ Docs index](../INDEX.md) · [Pipeline journal](../pipeline/pipeline-journal.md) ·
[Training index](../training/INDEX.md) · [Traceability matrix](../training/15-manual-traceability.md)

# Training Review — Run #135 Scope (Sensor Modality, Observe Rejection Reasons, Controller Events)

> **Document ID:** REV-TRN-007
> **Skill:** `09-training-manual-review`
> **Scope:** every section `08-training-manual-authoring` run #135 (`6c8c174`, closing
> `BL-0216`/`BL-0221`/`BL-0223`) touched:
> - `06-the-vignette-library.md` "Authoring sensors" table (rows `altitude_band_affinity`,
>   `requires_cue`, `beam_mode`), its closing paragraph and its Sources footer;
> - `12-white-cell-manual.md` `WCM-2` sensor paragraph and footer;
> - `13-blue-cell-manual.md` `BLU-4` and `14-red-cell-manual.md` `RED-4` sensor-limit paragraphs
>   and footers;
> - `07-white-cell-facilitation.md` controller-event table (`sensor_outage`, `forced_custody_loss`
>   rows);
> - `09-troubleshooting-and-glossary.md` §10 "An order is rejected" bullet and its new footer;
> - `15-manual-traceability.md` §15.1 sensor-modality row and §15.2 `WCM-2`/`BLU-4`/`RED-4` rows.
>
> Each touched section was read whole, not just the changed lines.
> **Commit reviewed:** `0458fd3` (branch `claude/chart-prompt-file-90hm9u` tip at review time). No
> commit after `6c8c174` touches `docs/training/`. Code has moved since run #135: `IP-1052`
> (`7bdfc94`, `VERIFIED` by `VR-1052`) widened `invalid_param` to every order action. Accuracy is
> judged against the code at `0458fd3`, which is what ships.
> **Independence:** this review ran in a fresh agent context with no part in run #135, in
> `IP-1220`/`1221`/`1222`/`1041`/`1052`, or in any earlier commit on this branch. The commits carry
> the same orchestration-thread `Claude-Session` trailer as this review — the same thread-level
> arrangement as REV-TRN-005/006 and `VR-1041`/`VR-1052`: separate agent contexts under one owner
> session.
> **Upstream:** `08-training-manual-authoring` (run #135) · **Downstream:**
> `10-integration-review`, `11-release-readiness`

## Headline

Run #135's prose is **accurate against shipped behaviour in every behavioural claim checked**: the
radar gains, the order-over-sensor mode precedence, the load-time checks, the `LEO_SSO` = `LEO`
rule, the `auto` cue skip and its all-cue rejection, `no_window` vs `sensor_contended`, and both
`07` controller-event rows. It was driven on fresh fixtures (a 97.6°/700 km target and a
`co-orbital-threat-escort` seed 61 HTTP session); the author used code reads and its own probe.
Traceability is clean: 294 relative links with 0 broken, 43 section IDs with 0 orphans, 0
missing footer paths, and every symbol a touched footer or §15 row names exists. The playbook and
training suites passed 20/20.

**No Critical or High findings.** There are 4 findings, all Low:

- **F1:** `06` says only the HTTP API can send a radar `fence`/`dish` mode. The console's command
  menu can also send it, through the order composer's raw JSON params box.
- **F2:** the corpus does not say what the sensor-tasking **Mode** dropdown does to a radar. Any
  entry other than `auto` replaces the radar's own mode with an imaging-SAR mode. `spotlight`
  gives 1.8 × gain, more than `dish`.
- **F3:** the manual says "look-ahead" for the window search; the console tooltip for the same
  reasons says "planning horizon". Neither term is in the glossary.
- **F4:** `09` §10's `invalid_param` text is stale since `IP-1052`. This is already filed as
  `BL-0228`; this review confirms it and adds nothing new.

## Dimensions exercised

### 1. Accuracy — prose claims vs. shipped behaviour

**Code reads** (at `0458fd3`):

- `engine/isr.py`: `BEAM_MODES["ground_radar"]` (`fence` `gain_factor` 0.50, `dish` 1.60),
  `_DEFAULT_MODE`, `beam_params` (the non-string guard), `altitude_band` (`LEO_SSO` → `LEO`),
  `effective_gain`.
- `engine/entities.py`: `Sensor.beam_mode`/`altitude_band_affinity: Optional[Regime]`/
  `requires_cue`, `_check_radar_beam_mode`.
- `engine/orders.py`: `_observe_params_ok`, `_order_params_ok`, `_candidate_sensors`,
  `_auto_blocked_by_cue`, `_plan_collection`, the named-sensor `requires_cue` check in `_validate`,
  and the observe branch of `_exec_payload` (order mode wins, else the sensor's mode; only a
  `fence`/`dish` request switches to the `ground_radar` table).
- `session/manager.py::_apply_inject_effects` (`sensor_outage` message text with
  `cleared`/`declared`; `forced_custody_loss` sets `confidence` and `last_observation = world.now`,
  or removes the track on `mode: drop`).
- `ui_web/static/index.html` `#task-beam-mode` options, and `app.js` `REASON_TIPS`,
  `composeBody`, `actionsFor`, `ACTIONS_BY_KIND` and the command-menu actor list.

**Engine probe** (fresh fixtures: a sun-synchronous 97.6°/700 km target, a radar at its
sub-point, seed 31; not the author's fixture):

| Claim (section) | Observed |
|---|---|
| A radar with no mode keeps its usual gain (`06`) | gain 1.0 (resolved `stripmap`) |
| `fence` halves the gain, `dish` is 1.6 × (`06`) | order `fence` → 0.5; order `dish` → 1.6; sensor `dish` → 1.6 |
| An order's mode overrides the sensor's (`06`) | sensor `dish` + order `fence` → 0.5, `fence` |
| `Fence`, or any non-radar mode, on a radar stops the build (`06`, `WCM-2`) | `Fence` and `stripmap` both raise `ValidationError` |
| Misspelt regime stops the build; `LEO_SSO` accepted (`06`, `WCM-2`) | `Leo` rejected; `LEO_SSO`, `LEO` accepted |
| Affinity mismatch halves gain; `LEO` not penalised against an SSO target (`06`) | `LEO` 1.0, `LEO_SSO` 1.0, `GEO` 0.5, none 1.0 |
| Named cue sensor, untracked target → `requires_cue`, preview the same (`06`, `BLU-4`, `RED-4`) | `issue` and `dry_run` both `rejected`/`requires_cue` |
| `auto` skips cue sensors (`06`, `BLU-4`, `RED-4`) | mixed fleet: `queued` on the uncued sensor `P` |
| `auto` with only cue sensors → `requires_cue` (`06`) | `issue` and `dry_run` both `requires_cue`; with a track held, `queued` on `C` |
| Windowless → `no_window` (`06`, `BLU-4`, `RED-4`, `09` §10) | `ground_optical`, `exclusion_angle_deg` 179.9 → `no_window` |
| All windows booked → `sensor_contended` (same) | 7th repeat issue on one radar → `sensor_contended` |
| Malformed observe field → `invalid_param`; `null` = absent (`09` §10) | `gain: "high"`, list `beam_mode`, text `look_angle_deg`/`duration_s` → `invalid_param` on both routes; `gain: null` → `queued` |

**HTTP probe** (`co-orbital-threat-escort` seed 61, `BLUE-RADAR` → `RED-COORB`, `TestClient`;
REV-TRN-006 used seeds 7/13): `POST …/order/validate` with `beam_mode` `fence`/`dish`/absent/
`spotlight` all `ok`; `POST …/order` with `{"beam_mode": "fence"}` queued, and the scheduled
`execute_observe` carries `("fence", 0.5)`. This is the same body and route that the command
menu's `composeBody()` sends (F1).

**`07` rows:** both checked against `_apply_inject_effects` line by line. The `sensor_outage`
restore message is `<id>: sensor outage cleared`. `forced_custody_loss` resets
`last_observation` to the inject time. Both match.

Pre-existing text in the touched `09` §10 bullet (`roe_kinetic_not_authorized` "enable it via the
`red_kinetic_authorized` dial", `insufficient_delta_v`, `not_owner`) was sampled. It is consistent
with `_validate` and with the corpus's use of "dial" for a vignette parameter override in `07`/`12`.

### 2. Traceability integrity

- Link/anchor script over all of `docs/training/*.md`: **294 relative links, 0 missing targets,
  0 bad anchors.**
- Section IDs: 38 `###` headings in `12`/`13`/`14`, plus `WCM-12`…`WCM-16` in `12a`, give **43
  IDs. Every one has a §15.2 row, with 0 orphans.** This matches REV-TRN-006's 43.
- Every backticked `spacesim/…` path in the corpus exists (0 missing). Every function a touched
  footer or §15 row names exists in the named file: `_check_usable_phase_angle`,
  `_check_radar_beam_mode`, `_observation_predicate`, `_sensor_orbit`, `_validate`,
  `_candidate_sensors`, `_auto_blocked_by_cue`, `_plan_collection`, `_resolve_sensor_id`,
  `_observation_phase_angle_deg`, `effective_gain`, `altitude_band`, `phase_angle_factor`,
  `_apply_inject_effects`, `_inject_effect_problem`, `_observe_params_ok`, `_plan_command`,
  `REASON_TIPS`, `build_world`.
- **Forward ⇄ reverse consistency:** the §15.1 sensor-modality row names `WCM-2`/`BLU-4`/`RED-4`.
  Their §15.2 rows and inline footers name the same new symbols (`_check_radar_beam_mode` on
  `WCM-2`; `_candidate_sensors`/`_plan_collection` on `BLU-4`/`RED-4`). They agree in both
  directions.
- The new `09` §10 footer cites `_observe_params_ok` only. Since `IP-1052`, `_order_params_ok`
  is the general gate. That gap is part of F4 (`BL-0228`).
- `09` §11 (glossary) still has no Sources footer. It was not touched by run #135 and is already
  tracked as `BL-0225`.

### 3. Coverage

- The sensor-modality capability reaches all three roles that use it: `WCM-2` (authoring and
  load checks), `BLU-4` (defensive tasking) and `RED-4` (targeting). Each section now carries the
  `auto` cue skip, the radar beam mode and the `no_window`/`sensor_contended` distinction.
- The latest `VERIFIED` packages were checked against the forward index. `IP-1222` and `IP-1041`
  are covered by this scope. `IP-1052` is not yet reflected: `invalid_param` now applies to every
  action, but the corpus describes observe fields only (F4, `BL-0228`).
- **No shipped vignette uses any modality field.** A grep of `content/vignettes/*.yaml` for
  `beam_mode`, `altitude_band_affinity`, `requires_cue`, `exclusion_angle_deg`, `min_range_km`,
  `host_asset_id` and `usable_phase_angle_deg` returns 0 matches. So the learning path and rung
  ladder are unaffected, and FR-11310 is unchanged.

### 4. Pedagogy

- Audience fit (MSTR-003 / NFR-3600): the new prose is operator-action-first. It says what the
  preview reason means and what to do about it ("get a first look with another sensor", "cancel a
  queued task or try later"), in short declarative sentences. Field values are shown in code
  font, and it warns about capitalisation (`Fence`) where that matters.
- Module sizes (NFR-3500, about 300 lines): `06` 105, `07` 99, `09` 39, `12` 214, `13` 271, `14`
  262, `15` 237. All are within the guideline.
- Terminology: the manual says "look-ahead" for the window search. The console tooltips for the
  same reasons say "planning horizon" (`REASON_TIPS.no_window`/`sensor_contended`). Neither term
  is in the `09` §11 glossary (F3).
- R600 grounding: run #135 made no sequencing or scaffolding choices; it only corrected as-built
  facts. No R6xx citation was owed, and there is no grounding gap.

## Findings

| Finding | Artifact(s) | Description | Severity | Recommended owner |
|---|---|---|---|---|
| F1 | `06-the-vignette-library.md` `beam_mode` row | The row says "Only the HTTP API can send this, because the console's **Beam mode** dropdown does not list the two radar modes." The dropdown claim is true. But a ground radar appears in the command menu's actor list (`ACTIONS_BY_KIND.ground_radar = ["observe"]`), and the composer's **Advanced (raw JSON params)** box sends `{"beam_mode": "fence"}` through `composeBody()` to the same `POST …/order` route. The HTTP probe shows that body queues with gain 0.5. The prose undersells the console. Reword it to say the sensor-tasking **Mode** dropdown can't select `fence`/`dish`, but the command menu's raw JSON params box can. | Low | `08-training-manual-authoring` |
| F2 | `06` `beam_mode` row; `BLU-4`/`RED-4` | The corpus says `auto` applies the radar's own mode. It does not say what the other **Mode** dropdown entries do on a radar. As built, any non-`auto` entry replaces the radar's declared `fence`/`dish` with that name on the imaging-SAR table. On a `dish` radar, `spotlight` gives 1.8 (above `dish`'s 1.6) and `scan` falls back to `stripmap` 1.0. Operators can raise or lower a radar's gain by accident. Add one sentence: on a radar, leave the Mode dropdown on `auto`. Whether the console should offer SAR modes for a radar at all is a design question. It belongs with `BL-0224` (the dropdown has no `fence`/`dish`), decided at the `FS-122`-chain `10-integration-review`. | Low | `08-training-manual-authoring` (prose); `BL-0224`'s `10` review (console design) |
| F3 | `06` closing paragraph, `BLU-4`, `RED-4`, `09` §10; `app.js` `REASON_TIPS` | Two terms are used for one concept: the manual says "look-ahead", the console says "planning horizon". Neither is in the glossary. Pick one in the manual (the console's term, since operators read it on screen), or add a glossary entry naming both. | Low | `08-training-manual-authoring` |
| F4 | `09` §10 `invalid_param` text and footer; §15.1 sensor row's `invalid_param` mention | Stale since `IP-1052`: `invalid_param` now applies to jam/engage/cyber/maneuver/command params as well as observe, and its gate is `_order_params_ok`. **Already filed as `BL-0228`**; this review confirms it and files nothing new. | Low | `08-training-manual-authoring` (`BL-0228`) |

Nothing was fixed in this pass.

## Verification-suite result

`python3 -m pytest spacesim/tests/test_vignette_tutorials.py spacesim/tests/test_training.py`
at `0458fd3`: **20 passed** (16 + 4). `test_sensor_modality_wiring.py` (10) and
`test_observe_order_remediation.py` (29) were run alongside as the code slice behind this scope:
**all passed** (59 in total, 0 failed, 0 skipped).
