[↑ Docs index](../INDEX.md) · [Pipeline journal](../pipeline/pipeline-journal.md) ·
[Training index](../training/INDEX.md) · [Traceability matrix](../training/15-manual-traceability.md)

# Training Review — Runs #140 and #148 Scope (Order-Param Shape Check, Radar Mode Paths, Planning Horizon, Refused Load)

> **Document ID:** REV-TRN-008
> **Skill:** `09-training-manual-review`
> **Scope:** every section touched by two `08-training-manual-authoring` runs, batched (`BL-0244`
> and run #140's owed review):
> - **Run #140** (`a6e2a51`, closing `BL-0225`/`BL-0228`/`BL-0229`/`BL-0230`/`BL-0231`):
>   `09` §10 "An order is rejected" bullet and footer; `09` §11 "Planning horizon" glossary entry
>   and the module's first glossary footer; `06` `beam_mode` row, the closing paragraph and footer
>   of "Authoring sensors"; `BLU-3`/`RED-3` dry-run item and footers; `BLU-4`/`RED-4` sensor
>   paragraphs and footers; `10` §10.5 row 8 and §10.6 row 5; §15.1 sensor row and the new
>   order-param shape-check row; §15.2 `BLU-3`/`BLU-4`/`RED-3`/`RED-4` rows.
> - **Run #148** (`81f67d6`, closing `BL-0243`): `06` "When a vignette won't load" (new) and the
>   three sensor-table cells re-pointed at it; `WCM-2` "If Load is refused"; `09` §10
>   `Load failed:` bullet and footer; §15.1 load-validation row; §15.2 `WCM-2` row;
>   `training/INDEX.md` `06` row.
>
> Each touched section was read whole, not only the changed lines.
> **Commit reviewed:** `6d75495` (branch `claude/chart-prompt-file-90hm9u` tip at review time). No
> commit after `81f67d6` touches `docs/training/`. Code has moved since: `IP-1320` (`ed9cdcf`,
> `VERIFIED` by VR-1320) added the `insufficient_ammo` reason. That manual impact is already filed
> as `BL-0250` and is out of this scope. Accuracy is judged against the code at `6d75495`.
> **Independence:** this review ran in a fresh agent context with no part in run #140, run #148,
> or the packages they document (`IP-1052`, `IP-1222`, `IP-1310`). The commits carry the same
> orchestration-thread `Claude-Session` trailer as this review — the same thread-level arrangement
> as REV-TRN-005/006/007: separate agent contexts under one owner session.
> **Upstream:** `08-training-manual-authoring` (runs #140, #148) · **Downstream:**
> `10-integration-review`, `11-release-readiness`

## Headline

Both runs' prose is **accurate in nearly every behavioural claim checked**, driven on fresh
fixtures (an engine probe on `sda-custody-hunt` seed 4242, a `gnss-ew-campaign` seed 7171
dry-run probe, and a `TestClient` drive against a temporary vignette folder). Traceability is
clean: 302 relative links with 0 broken, 43 section IDs with 43 §15.2 rows, and every symbol a
touched footer or §15 row names exists. The playbook and training suites passed 20/20.

**No Critical or High findings.** There are 6 findings: 2 Medium, 4 Low.

- **F1 (Medium, prose):** `06` says a broken vignette "still appears in the picker". That is
  false for the first refusal case it lists: a file that is not valid YAML (or has no
  `vignette:`/`id`) is left out of the picker.
- **F2 (Medium, code bug exposed):** one unparseable `.yaml` placed in the built-in vignette folder makes
  a misspelt id return a **500**, not the "not found" the manual promises. It also breaks loading
  any vignette whose file name differs from its id and sorts after the bad file.
- **F3 (Low):** the `build` catch-all is only reported once every other problem is fixed, so
  "fix every listed item, then Load again" can turn up a new item.
- **F4 (Low):** "text for `salvo_n`" / "text where a number belongs" overstates the check:
  numeric text (`"3"`, `"200"`) is accepted.
- **F5 (Low):** the `06` raw-JSON radar instruction, followed literally, drops the box's
  pre-filled `"intent": "characterize"`.
- **F6 (Low):** `10` §10.5 row 8 calls the control **Beam mode**; on screen it is **Mode**, as
  the rest of the corpus says.

## Dimensions exercised

### 1. Accuracy — prose claims vs. shipped behaviour

**Code reads** (at `6d75495`): `engine/orders.py` `ORDER_PARAM_RULES`, `_param_value_ok`,
`_order_params_ok`, `_observe_params_ok`, `OrderSystem.__init__` (`horizon_s = 24 * 3600`), the
window searches that use `self.horizon`, and the observe branch of `_exec_payload` (default
`intent` `"track"`; order mode wins over sensor mode; only `fence`/`dish` switch to the
`ground_radar` table; a radar's payload type otherwise derives as `isr_sar`); `session/manager.py`
(builds `OrderSystem` with no `horizon_s`); `engine/isr.py` `BEAM_MODES` and `beam_params`;
`content/vignette.py` `list_vignettes`, `load_vignette`, `validate_vignette`,
`VignetteValidationError.message`, `_pydantic_problems`; `session/inprocess.py` `load_vignette`;
`ui_web/server.py` `_vignette_load_errors`; `ui_web/static/app.js` `REASON_TIPS`, `composeBody`,
`ACTIONS_BY_KIND`, `PARAM_TEMPLATE.observe`, `renderVerbForm`, `loadSession`, the command-menu
actor list; `index.html` `#task-beam-wrap` ("Mode"), `#task-beam-mode` options,
`#json-params-wrap` ("Advanced (raw JSON params)"), `#o-params`, `#session` inside
`#cell-time-panel` ("Cell & Time").

**Engine probe — radar mode paths** (`sda-custody-hunt` seed 4242, `BLUE-RADAR-1` → `RED-OBJ`,
sensor mode set in place; `_exec_payload` on the first real window; not the author's fixture):

| Claim (section) | Observed |
|---|---|
| No mode on sensor or order → usual gain (`06`) | `stripmap`, 1.0 |
| `fence` half, `dish` 1.6 × (`06`) | order `fence` 0.5; order `dish` 1.6; sensor `fence` 0.5; sensor `dish` 1.6 |
| Order mode overrides sensor mode (`06`) | sensor `dish` + order `fence` → `fence` 0.5; sensor `fence` + order `dish` → 1.6 |
| Dropdown on `auto` → sensor's own mode (`06`, `BLU-4`, `RED-4`, `10` §10.5) | `{}` and `{"beam_mode": null}` → sensor's mode in all three cases |
| Non-`auto` entry replaces the radar's mode; `spotlight` 1.8 ×, `scan` plain (`06`, `BLU-4`, `RED-4`, `10` §10.5) | `spotlight` → 1.8 on every sensor mode; `scan` → `stripmap` 1.0 on every sensor mode |
| A list as observe beam mode → `invalid_param` (`09` §10) | `["fence"]` → `rejected`/`invalid_param` |
| Planning horizon = 24 h (`06`, `09` §10/§11, `BLU-4`, `RED-4`) | `osys.horizon` = 24.0 h for a `SessionManager`-built order system |

**Shape-check probe** (`_order_params_ok` directly, then `dry_run` on `gnss-ew-campaign` seed
7171, `RED-JAM` → `BLUE-GNSS`):

| Claim (section) | Observed |
|---|---|
| `power_w: "inf"` → `invalid_param` (`09` §10, `RED-3`) | refused; `dry_run` `rejected`/`invalid_param`; `"lots"` the same |
| Text for `salvo_n` → `invalid_param` (`09` §10, `RED-3`) | `"three"` refused — but `"3"` accepted, and `2.7` accepted (F4) |
| `dv` not exactly three numbers (`09` §10, `BLU-3`, `10` §10.6) | `[1, 2]` refused; `[1, 2, 3]` accepted |
| Non-text `via` (`09` §10) | `via: 7` refused |
| `null` counts as left out (`09` §10, `BLU-3`, `RED-3`, `10` §10.6) | `power_w: null` → `queued`; `via: null` accepted |
| Numeric text where a number belongs (`BLU-3`) | `power_w: "200"` → `queued` (F4) |
| Console term is "planning horizon" (`09` §11) | `REASON_TIPS.no_window`/`sensor_contended` both say "planning horizon" |

**Command-menu radar path (`06`):** a ground radar sits in `sensors:`, and the command menu's
actor list is built from assets plus sensors with an `ACTIONS_BY_KIND` entry
(`ground_radar: ["observe"]`). `observe` has no `VERB_FORM_SCHEMA` form, so the raw JSON box is
the only params input. It is pre-filled `{"intent": "characterize"}` (`PARAM_TEMPLATE.observe`).
Replacing that with `{"beam_mode": "fence"}`, as the row says, sends no `intent`, and
`_exec_payload` then uses `"track"` (F5).

**Load-validation drive** (`TestClient` over `create_app()`, with `VIGNETTE_DIR` pointed at a
temporary folder holding copies of `01` and `07` plus a deliberately broken copy of `07`:
id `broken-07`, radar `beam_mode: Fence`, a duplicated sensor, and a Red asset repeated in
`blue_forces`; the author used a broken copy of `01` instead):

| Claim (section) | Observed |
|---|---|
| A broken vignette still shows in the picker (`06`) | `broken-07` listed (schema-broken case) |
| 400, message names the first problem, list names every problem as *where — reason* (`06`, `WCM-2`, `09` §10) | 400 `invalid_vignette`; message `…: blue_forces/red_forces[RED-OBJ]: asset id 'RED-OBJ' is declared 2 times (and 2 more problems)`; 3 problems: the duplicate asset, `sensors[BLUE-RADAR-1] — Value error, ground_radar beam_mode must be one of ['dish', 'fence'], got 'Fence'`, `sensors[BLUE-OPT-1] — sensor id 'BLUE-OPT-1' is declared 2 times` |
| `app.js` shows `Load failed:` + the list in **Cell & Time** (`06`, `WCM-2`, `09` §10) | `loadSession` writes `<b>Load failed:</b> msg` + `<ul>` of `where — reason` into `#session`, inside `#cell-time-panel` |
| Refused load evicts nothing, uses no `sess-N` (`06`, `WCM-2`, `09` §10) | `sess-1` loaded first; after the 400 and a 404 the registry still held only `sess-1`; the next good load got `sess-2` |
| Misspelt id → "not found" (`06`, `09` §10) | 404 `vignette 'nosuch' not found` — **but** 500 once an unparseable `.yaml` is in the folder (F2) |
| Not valid YAML → refused (`06`) | `bad-yaml.yaml` (file name = id) → 400 `invalid_vignette`, `bad-yaml.yaml: not valid YAML: …` |
| Picker only checks for a `vignette:` block with an `id` (`06`) | `bad-yaml` **not** listed: `list_vignettes` skips any file that fails to parse (F1) |

The rule list in `06` and `WCM-2` was checked line by line against `validate_vignette`: the
satellite-orbit / non-satellite-location rule with the `cyber_unit` exception, TLE parse and
propagate at `start_epoch_utc`, asset ids unique across the three force lists, sensor ids unique,
`roles_needed` naming a declared asset or `group`, `initial_tracks` via the `Track` model, and the
`build` catch-all. All match, with the ordering caveat in F3.

### 2. Traceability integrity

- Link/anchor script over all of `docs/training/*.md`: **302 relative links, 0 missing targets,
  0 bad anchors** (including `#10-troubleshooting`, `#authoring-sensors-optional-modality-fields`,
  `#when-a-vignette-wont-load`, `#blu-3--previews-before-you-commit`).
- Section IDs: 11 (`12`) + 5 (`12a`) + 14 (`13`) + 13 (`14`) = **43 IDs; §15.2 has 43 rows, 0
  orphans.**
- Every backticked `spacesim/…` path in the reviewed modules exists. Every symbol the touched
  footers and §15 rows name exists in the named file (`_order_params_ok`, `ORDER_PARAM_RULES`,
  `_observe_params_ok`, `_plan_collection`, `_plan_command`, `horizon_s`, `_candidate_sensors`,
  `_resolve_sensor_id`, `dry_run`, `REASON_TIPS`, `composeBody`, `ACTIONS_BY_KIND`, `loadSession`,
  `#task-beam-mode`, `#o-params`, `validate_vignette`, `VignetteValidationError`,
  `list_vignettes`, `load_vignette` ×2, `build_world`, `_vignette_load_errors`).
- **Forward ⇄ reverse consistency:** the new §15.1 shape-check row names `BLU-3`/`RED-3`; their
  §15.2 rows and inline footers both add `_order_params_ok`/`ORDER_PARAM_RULES`. The extended
  sensor row's new UI symbols (`#task-beam-mode`) appear in the `BLU-4`/`RED-4` footers and §15.2
  rows. The new load-validation row names `WCM-2`; the `WCM-2` footer and §15.2 row both add
  `validate_vignette`/`VignetteValidationError` and `app.js` `loadSession`. Consistent both ways.
- `09` §11 now has a Sources footer (`BL-0225` confirmed closed).
- Not in scope, noted only: `10-ui-reference.md` still has no Sources footers (`BL-0232`) and is
  475 lines (`BL-0198`); both are already tracked.

### 3. Coverage

- Order-param shape check: reaches `BLU-3`, `RED-3`, `09` §10 and `10` §10.6. The §15.1 row puts
  no White section against it. White can issue orders on a cell's behalf, but `WCM` has no
  order-composition section, so the shared `09`/`10` coverage applies. That matches the
  corpus's existing pattern for preview mechanics.
- Radar mode paths: `06` (authoring + console path), `BLU-4`, `RED-4`, `10` §10.5 row 8.
  Complete for the roles that task sensors.
- Refused Load: `06`, `WCM-2`, `09` §10. Loading is a White action, so `BLU`/`RED` "—" is right.
- Latest `VERIFIED` packages vs. the forward index: `IP-1052`, `IP-1222`, `IP-1310` are all now
  reflected. `IP-1320` is not yet (`insufficient_ammo` is absent from `09` §10). That is
  `BL-0250`, scheduled for `08-training-manual-authoring`, and not a new finding.
- No shipped vignette uses a sensor-modality field (grep of `content/vignettes/*.yaml`: 0
  files), so the learning path and FR-11310 rung assignment are unaffected by either run.

### 4. Pedagogy

- Audience fit (MSTR-003 / NFR-3600): both runs write operator-action-first prose. They say what
  you see, where, and what to do ("Fix every listed item in the YAML, then press **Load** again";
  "keep Mode on `auto`"). They give concrete examples in code font and define the one new term
  ("planning horizon") in the glossary where operators will look it up.
- Module sizes (NFR-3500, about 300 lines): `06` 148, `09` 61, `12` 225, `13` 279, `14` 270, `15`
  239 — within the guideline. `10` is 475 (`BL-0198`, already tracked).
- Worked examples: `06`'s three sample problem lines are real reasons the check emits (the
  `Fence` one abbreviated with "…" over pydantic's "Value error," prefix). The *section*`[`*entry*`]`.*field*
  pattern covers every example. The duplicate-asset form (`blue_forces/red_forces[RED-OBJ]`)
  joins two sections, which the pattern does not mention; it reads plainly, so it is not filed.
- R600 grounding: neither run made sequencing or scaffolding choices; they recorded as-built
  facts. No R6xx citation was owed, and there is no grounding gap.

## Findings

| Finding | Artifact(s) | Description | Severity | Recommended owner |
|---|---|---|---|---|
| F1 | `06-the-vignette-library.md` "When a vignette won't load" (2nd paragraph) | The section says "The vignette still appears in the picker while it is broken. The picker only checks that the file has a `vignette:` block with an `id`." That holds for schema errors, but `list_vignettes` skips any file that fails to parse, and any file with no `vignette:` block or no `id`. Those are the first refusal case the same section lists. An author with a YAML syntax error sees the vignette **disappear** from the picker, which the corpus never mentions. (Because such a file cannot be picked, its 400 "not valid YAML" readout can only be reached by an API call naming it, and only when the file is named exactly `<id>.yaml`.) Reword: a file that won't parse as YAML, or lacks `vignette:`/`id`, is left out of the picker. Check the YAML syntax first if your vignette is missing. Mirror one line in `09` §10. | Medium | `08-training-manual-authoring` |
| F2 | `spacesim/content/vignette.py` `load_vignette` (built-in declared-id scan); manual claims in `06`/`09` §10 | Code defect exposed by the review. The built-in folder scan that resolves an id by its declared `id` calls `yaml.safe_load` with no `YAMLError` guard. The external-folder scan and `list_vignettes` both have one. With one unparseable `.yaml` in `VIGNETTE_DIR`, `POST /api/sessions` returns **500** for a misspelt id (`nosuch`, expected 404) and for any vignette whose file name differs from its id and sorts after the bad file (`broken-07` in `zz-broken-07.yaml`: 500). Vignettes found earlier in sort order still load (`leo-isr-denial`, `sda-custody-hunt`: 200). This contradicts FS-131 OQ4 / `_vignette_load_errors`' "never a 500" and the manual's "the readout says the vignette was not found". **Save as vignette** writes to the external `user_save_dir`, not to this folder, so the defect needs a hand-placed or hand-edited file in the built-in `content/vignettes/`. The `06` authoring guidance does not tell authors to avoid that folder. Medium, because it breaks an explicit FS-131 "never a 500" criterion and loads of *other*, valid vignettes; it is not High, because it needs a broken file in the shipped folder. File via `00-intake` as a code bug (entry `07`, small remediation). No prose change is due until it is fixed. | Medium | `00-intake` → `07-implementation-planning` |
| F3 | `06` "When a vignette won't load"; `WCM-2` "If Load is refused" | Both say the list names **every** problem and to fix them all and Load again. `validate_vignette` runs its `build` catch-all only when no other problem was found, so a file can pass every listed fix and then be refused with a new `build` item. Add one sentence: if the only remaining problem is under `build`, it appears after the others are fixed. | Low | `08-training-manual-authoring` |
| F4 | `09` §10 `invalid_param` ("text for `salvo_n`"); `BLU-3` ("text where a number belongs"); `RED-3` ("text for `salvo_n`") | As built, numeric fields take anything `float()`/`int()` accepts: `"200"` for `power_w` queues, `"3"` and `2.7` for `salvo_n` pass (the run #140 author's own probe showed `"200"` queued). Only non-numeric text, non-finite values and wrong shapes are refused. Say "text that isn't a number" instead of "text". | Low | `08-training-manual-authoring` |
| F5 | `06` `beam_mode` row (command-menu path) | "put `{"beam_mode": "fence"}` … in its **Advanced (raw JSON params)** box". That box arrives pre-filled `{"intent": "characterize"}` for `observe`. Replacing it drops `intent`, and the look then runs as `"track"`, the engine default. Say to **add** `"beam_mode": "fence"` to what is there, for example `{"intent": "characterize", "beam_mode": "fence"}`. | Low | `08-training-manual-authoring` |
| F6 | `10-ui-reference.md` §10.5 row 8 | The control is named **Beam mode**; its on-screen label is **Mode** (`#task-beam-wrap`), which is what `06`, `BLU-4` and `RED-4` (run #140) call it. The label predates run #140, but run #140 edited this row and left the corpus naming one control two ways. Rename the row to **Mode**. | Low | `08-training-manual-authoring` |

Nothing was fixed in this pass.

## Verification-suite result

`python3 -m pytest spacesim/tests/test_vignette_tutorials.py spacesim/tests/test_training.py` at
`6d75495`: **20 passed** (16 + 4), 0 failed, 0 skipped. The probes above are ad-hoc scripts kept
in the reviewer's scratchpad. Nothing was added to the repository's test suite (review-only).
