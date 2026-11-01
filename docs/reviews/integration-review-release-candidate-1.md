# Integration Review — Release Candidate 1 (whole candidate: White-only controls, save robustness, time bounds, playback seats, test-origin guard, dependency lock, documentation passes)

> **Stage:** 10 — Integration Review (fresh session; took no part in implementing or verifying any package in scope)
> **Reviewed commit:** `30717a3` (branch `claude/integration-review-final`, tip = `claude/release-candidate-1`)
> **Date:** 2026-10-25
> **Scope (explicit package list):** `IP-1311`, `IP-1102`, `IP-1072`, `IP-1073`, `IP-1103`, `IP-1074`, `IP-1335`, `IP-1075`, `IP-1076`, `IP-1077`, `IP-1078`, `IP-1079`, `IP-1080`, `IP-1081`, `IP-1334`, plus the documentation, requirements and dependency changes merged with them (requirements passes 1-3, GDS-07..10 corrections, the `CLAUDE.md` sweep, feature-index statuses, training updates, "major" wording in the skills, `requirements.lock` and the `pyproject.toml` floors).
> **Headline:** **0 Critical, 0 High, 3 Medium, 6 Low.** The candidate composes. Every suite, in every mode and in a fresh venv built from `requirements.lock`, is green with the same numbers; 19 of 19 vignettes round-trip; the seat rule is uniform over the whole route table. Tranche-3 findings `M-1`..`M-5` and `L-1`, `L-3`..`L-5`, `L-7` are closed; tranche-2 `F-01`..`F-11`, `F-13`..`F-15` are closed. The three Mediums are a way for one White request to make every read of a session fail, a console toolbar path that still throws instead of showing a refusal, and a `CLAUDE.md` code map that omits four of the packages in scope.
> **Previous reviews of this kind:** [`integration-review-tranche-3-release-push-remediation.md`](integration-review-tranche-3-release-push-remediation.md), [`integration-review-tranche-2-white-controls-saves-test-origins.md`](integration-review-tranche-2-white-controls-saves-test-origins.md)

## 1. Scope confirmation

All fifteen packages read `VERIFIED` in the Master Build Plan, `packages/INDEX.md` and `ROADMAP.md`, and each has a Verification Report that `verification/INDEX.md` lists (`VR-1311`, `1102`, `1072`, `1073`, `1103`, `1074`, `1335`, `1075`, `1076`, `1077`, `1078`, `1079`, `1080`, `1081`, `1334`; 82 `VR-*.md` files, 82 index rows). I recounted the ledger myself: `packages/INDEX.md` holds 83 package rows, **82 `VERIFIED`, 1 `BLOCKED` (`IP-1160`, unauthorized by design), 0 of any other status**; the Master Build Plan table also has 83 rows and its newest tally line (line 915) says the same. A script comparing every package file's `Status` blockquote with the ledger found no disagreement (the three apparent hits were multi-line headers whose `Status` line is further down and reads `VERIFIED`). Nothing was reviewed around a hole.

Production delta against the tranche-3 review commit `d7f6791`: `session/manager.py` (+49), `session/inprocess.py` (+94/-46), `ui_web/server.py` (+43/-15), `ui_web/static/app.js` (+19/-5). **No file under `spacesim/engine/` or `spacesim/content/` changed** (`git diff d7f6791..HEAD --stat -- spacesim/engine spacesim/content` is empty).

## 2. Gates and evidence run at `30717a3`

| Check | Result |
|---|---|
| `python3 -m pytest --junitxml=…` (unfiltered, default addopts) | **exit 0; 1700 tests, 0 failures, 0 errors, 3 skipped** (the three long-standing data-dependent vignette skips: `test_defensive_audit_2026` x2, `test_derived_probabilities`); 214 s |
| `python3 -m pytest -m "not browser" --junitxml=…` | exit 0; 1669 tests, 0 failures, 4 skipped (the same 3 plus the by-design partial-collection skip in `test_test_origins.py`); 164 s |
| `python3 -m pytest -m browser --junitxml=…` | exit 0; **31 tests, 0 failures, 0 skipped** (Chromium under `/opt/pw-browsers`); 45 s. 1669 + 31 = 1700 |
| **Fresh venv from `requirements.lock`** (`python3 -m venv`; `pip install -r requirements.lock`; `pip install --no-deps -e .`; CPython 3.13.17; proxy CA, TLS verification on) | `pip check`: no broken requirements. Unfiltered suite: **exit 0; 1700 tests, 0 failures, 0 errors, 3 skipped**, identical to the system-environment run (one extra `StarletteDeprecationWarning` about `httpx`). The browser tests ran there too (skip count is the same 3). Lock pins confirmed in the venv: `pydantic 2.14.1`, `numpy 2.5.4`, `fastapi 0.162.0`, `starlette 1.10.0`, `playwright 1.64.1`, `pytest 9.1.1`. |
| `pyproject.toml` floors vs lock | Every floor equals the lock's pin (`pydantic 2.14.1`, `numpy 2.5.4`, `sgp4 2.27`, `pyyaml 6.0.3`, `fastapi 0.162.0`, `uvicorn 0.54.0`, `pytest 9.1.1`, `hypothesis 6.170.9`, `skyfield 1.55`, `httpx 0.28.1`, `pillow 13.0.0`, `playwright 1.64.1`). Observation: the default system environment carries `pydantic 2.13.5` and `numpy 2.5.3`, below the floors, and the whole suite is also green there; the floors are validated, not minimal. |
| Permanent gates `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`, `test_test_origins.py` run alone | exit 0 (44 passed, 1 skipped = the partial-collection skip); `test_doc_integrity.py` was re-run after this report and the `ROADMAP.md` entry were written (§10) |
| `pytest --origin-report` | **0 untagged tests**. Exits 5 ("no tests ran"), see L-3 |
| Shrink-only allow-lists (non-comment entries) | `doc_integrity_allow_links.txt` **38** (was 64 in tranche 3; shrank by 26), `…_indexes.txt` **0** (was 3), `…_ledgers.txt` **0** (was 2), `test_origin_allowlist.txt` **0** |
| Ledger recount | 82 `VERIFIED` / 1 `BLOCKED` of 83 (§1) |
| Engine delta | none since `d7f6791`; since tranche 2's `63e6081` only the single `simulation.py` hunk reviewed in tranche 3 |

## 3. Dimension 1 — Interface consistency

### 3.1 Seat rule over the whole route table (derived from `app.routes`, plus source inspection)

Every `POST`/`PUT`/`PATCH`/`DELETE` route under `/api` was enumerated (43) and its handler source checked for its guard; the White group and the creation routes were also probed with six seat values (`white`, `blue`, `red`, `observer`, absent, `bogus`).

| Group | Routes | Guard | Probe result |
|---|---|---|---|
| White-only (`_require_white`, query seat) | `clock, param, start, step, advance, rewind, undo, inject, force/tle, force/bulk_import, force/ground, creator/state (PUT), creator/asset (PATCH, DELETE), creator/seats, red_step, roles/assign, observer/view, save_vignette, load_save` | 403 for every seat but `white` | `white` 200/400 (valid body, domain result), `blue`/`red`/`observer`/absent/`bogus` **all 403** for the 15 routes probed with a valid body; `roles/assign`, `observer/view`, `param`, `creator/state`, `PATCH creator/asset` answered 422 to my hand-made bodies for every seat (body validation precedes the guard) and were confirmed by source |
| White-only, inline | `injects/{h}/cancel`, `injects/{h}/edit` | `cell != "white"` | white 400 (unknown handle), others 403 |
| Creation | `POST /api/sessions`, `POST /api/sessions/draft` | `_refuse_player_seat_on_create` (named player seat refused; absent seat allowed, deliberate) | white 200, blue/red/observer 403, absent 200 |
| Observer-rejecting only (play surface) | `order, order/validate, *_compute, preview/consequence, cancel, gate/decide, roe/change, recovery, ssn/*` | `_reject_observer(req.cell)` (the cell the order is for) | by source; same client-asserted trust as before |
| AAR playback | `aar/playback/{start,advance,viewpoint,speed}` (POST), `…/state` (GET) | `playback_seat_decision` on the query seat (IP-1077) | `white` any; `blue` start `blue` 200, start `truth` 403, viewpoint `red`/`truth` 403; `red` cannot read or drive a Blue playback (403); Observer `state` 200, `advance` 403; absent/`White`/`WHITE`/empty/`x` seat 403 everywhere |

No mutating route is unguarded. The tranche-2 dual-channel note (`F-15`) is closed: `roles/assign` and `observer/view` are `_require_white` on the query seat and `08-http-api-reference.md` says that only the query-string seat counts.

### 3.2 Console driven in headless Chromium, one tab per seat (session `leo-isr-denial` and `mt-isr-sar`, real server on loopback)

| Step | White | Blue / Red | Observer |
|---|---|---|---|
| Time controls visible | +1m/+10m/+1h, Rewind, Pause, Session, Creator all visible | all hidden | all hidden |
| `+1m` / `+10m` | `/step` 200; clock moved exactly 60 s and 660 s | n/a | n/a |
| Palette | offers advance, rewind and inject entries; `advance 1 hour` moved 3,600 s; `rewind to start` landed on `start_epoch` (0 offset) | no time entries, no inject entries | no time entries, no inject entries |
| Toolbar Rewind | lands on `start_epoch` | n/a | n/a |
| Fire inject (`dazzlers_online`) | "✓ fired" | n/a | n/a |
| AAR slider | label updates | n/a | n/a |
| Settings > Save session | download, 19 KB | n/a | n/a |
| Settings > Load session (the downloaded file) | `load_save` 200, tab moves to `sess-2` | **403, "Load failed: White Cell control: refused unless the request names the white seat" in the status line; `#session` readout kept; polling alive** | same as Blue/Red |
| Save as scenario | prompts accepted: "✓ saved …/ir-scn.yaml" | n/a | n/a |
| Creator | New draft, add TLE (asset listed), Save as vignette: "saved: …/ir-draft.yaml" | n/a | n/a |
| Unhandled page errors | **one**, see M-2 (toolbar `+1m` at the span end) | none | none |
| Blue switched to Observer on one tab | n/a | n/a | no 403 dry-run calls (tranche-3 `L-3` closed) |

Playback has **no console control** (documented in `12-white-cell-manual.md` WCM-9): the "playback-adjacent UI" is the AAR slider and bookmarks, both exercised above; the playback routes were driven directly (§3.1, §5).

### 3.3 Time bounds across advance, undo, rewind, load, validate, Creator

* `step`/`advance`: finite, forward-only, `<= start_epoch + 366 days`; `NaN`, `Infinity`, negative, `1e30`, `1e400`, `10**30`, `true` each give a 400 with the reason, nothing changed. **Exception:** a JSON `NaN`/`Infinity` for `advance.t` or `rewind.t` gives HTTP 500 (M-1).
* `rewind`: `[start_epoch, now]` only; `start_epoch - 1` and `10**30` give 400.
* `undo`: `n = 0`, `-3` give 400; `n = 10**12` with entries present undoes all and lands on `start_epoch`; on an empty log gives 400.
* The ceiling is the same figure in all three places: `SessionManager._span_ceiling()` (advance), `MAX_SAVE_SPAN_US` (save validation) and the pinned running clock (`catch_up`). Probe: for each of the 19 vignettes, `advance` to exactly `start + 366 d` gives 200 and the save loads (19/19), +1 µs gives 400. For each of the 19, `save_vignette` with `as_scenario=true` (new `start_epoch` = the save moment), a session of the saved scenario advances to its **own** `start + 366 d` (200), refuses +1 µs (400), and its save loads (19/19).
* A running clock at rate 600 pins at the ceiling and stays "running" (also covered by the new browser test). Closes tranche-3 `M-2` (§7).

## 4. Dimension 2 — Invariant sweep

| Invariant | Evidence | Result |
|---|---|---|
| Deterministic core | No engine file changed since `d7f6791`; `test_determinism.py` green; **replay-equals-live probe, 19 of 19 vignettes**: pre-start TLE force-add, start, step, step, `undo`, step, `rewind` to mid, step, freeze clock, `GET /save`, `POST /load_save`, compare live vs loaded `godview`, `scene/blue`, and re-save `eventlog`/`final_time`/`seed`/`baseline`/`content`: all identical, 0 warnings | Holds |
| Engine import boundary | `test_import_guard.py` green; no engine diff | Holds |
| Fog of war at the SessionAPI seam | New in scope: IP-1077 playback. A Blue playback of `da-asat-crisis` after one hour: keys `cell, now, own_assets, own_sensors, known_tracks, visible_effects, effect_windows, messages, objectives`; the only Red asset (`RED-ASAT`) appears in neither the playback state nor `/scene/blue`. Blue cannot select the `red` or `truth` viewpoint; once White switches the shared playback to `truth`, Blue's `state` is 403. `/save` content/baseline remain on the `FR-6220` named list | Holds |
| Plan-first | No order or tasking path changed | Holds |
| Sub-stepped clock | `SessionManager.advance_to` still ends in `Simulation.advance_to` (unchanged); the new checks run before it and `catch_up` clamps the target, never skips an event | Holds |
| Content-as-data | The only content-facing change is `vignette.py` tag/ID scanning (IP-1311); the span, cap and seat rules are code constants backed by requirements, not scenario logic | Holds |

## 5. Dimension 3 — Behavioural coherence (IP-1076, IP-1077, IP-1081 with rewind, undo, save, load, AAR, playback)

* **Rewind/undo vs save/load.** After an `undo`, a `rewind` to mid-exercise and further steps, the save reloads to an identical world (§4). Undoing every entry lands on `start_epoch`; the next `step` runs from there.
* **Creator and force-add vs the bounds.** A force-add (`force/tle`, `bulk_import`, `ground`) is refused once the session has started (`"cannot edit force after start"`, pre-existing since IP-1064); before start it adds no event-log entry, so it interacts with neither the 366-day span nor the 100,000-entry cap. Creator drafts reject `step`/`advance`/`rewind`/`undo` (draft sessions have no clock). All 19 vignettes accepted a pre-start force-added ISS TLE and then round-tripped.
* **Playback vs rewind/undo/load (L-2).** A playback is one cursor per session, shared by every seat (documented in WCM-9, so a player starting its own viewpoint replacing White's truth playback is the documented design, not a finding). After a live `rewind` to 10 minutes, a Blue playback that had been advanced to 2 hours still reports `now` at 2 hours (beyond the end of the recorded log) from `state`; the next `advance` clamps it to the live end. After a `load_save` no playback exists (404 until started). No leak, only a misleading cursor.
* **Event-log cap vs live use (L-1).** IP-1081 makes the 100,000-entry cap the first rung of `validate_save` for both log shapes. A live session has no such bound: 100 `inject` calls added 100 entries in 0.3 s, so a scripted client reaches 100,000 in about five minutes, after which its save is refused at load. The same class as tranche-3 `M-2`, but needing a script rather than an exercise: ordinary `step`/`advance`/`roe/change` add no entries (300 steps + 300 ROE changes left the log at 1 entry); the 19 vignettes end 366-day sessions with 24-97 entries.
* **Clock controls (M-1).** `POST /clock` accepts any float: JSON `NaN`, `Infinity` and `-Infinity` are stored as the rate. From then on **every read of that session returns HTTP 500** (`GET /clock`, `/godview`, `/scene/blue`, `/save`, `/objectives`, each of which calls `catch_up`); `POST /clock {"running": false}` also 500s, and a `POST /clock {"running": true, "rate": 1}` restores it. A negative rate (-5) and a huge one (1e18) are accepted and harmless (the ceiling clamps the latter).
* **Console toolbar (M-2).** See §3.2 and the findings table.

## 6. Dimension 4 — Traceability coherence

* Master Build Plan, `packages/INDEX.md`, `verification/INDEX.md` and `ROADMAP.md` agree on all fifteen packages (each present once or more in all four, `VERIFIED`, with its VR). Total tally agrees everywhere it is stated (82 / 0 / 0 / 1). The remaining "awaiting 09" sentences in the Master Build Plan are dated log entries (lines 913-930) and the run #54 note at line 665; they describe the moment they were written.
* RTM: no row still says "awaiting 09", "COMPLETE 2026-10-23" or "feature specification pending"; `FR-4330` (new, pass 2) is present with `FS-106 (v2.4)`; the Test column is generated and `test_test_origins.py` agrees. The "not met as built" notes are gone from `01-functional-requirements.md` (one line, 47, records that they were removed).
* GDS-10 `FR-W3` row now cites `IP-1060, 1068, 1072-1076` as `VERIFIED`. GDS-10 §6 still carries run #217 coverage counts ("Of the 59 packages, 57 are `VERIFIED`") under a status note that says so and defers regeneration to its OQ1 (L-4).
* `feature-index.md`: FS-106 reads "Done (v2.4 …)" and FS-110 "Done (v1.0; v2.0 additions built by IP-1101-IP-1103, VERIFIED)"; both former `…_ledgers.txt` entries are deleted.

## 7. Dimension 5 — Documentation coherence

* **Updated and consistent:** `docs/training/08-http-api-reference.md` (seat rule, step/advance refusals, `load_save` reasons, playback seat table), `12-white-cell-manual.md` WCM-4/WCM-9/WCM-10 (advance bounds, pinned clock, shared playback cursor, 366-day save cap), `15-manual-traceability.md` rows for the bounds and the playback routes; GDS-07 line 191, GDS-08 line 258, GDS-09 lines 163-166 and OQ5; requirements `FR-4330`, `FR-7230` (100,000 and 366 days). The training curl examples carry `?cell=white` (§8).
* **Stale or missing:**
  * `CLAUDE.md` code map has no text for **IP-1076** (`_span_ceiling`, step/advance `ValueError` to 400, pinned running clock), **IP-1077** (`playback_seat_decision`, `PlaybackSeatRefused`), **IP-1081** (the cap's new home `SessionManager.MAX_EVENTLOG_REPLAY_ENTRIES`, first rung of `validate_save`) or **IP-1103** (`MAX_SAVE_SPAN_US`, `_check_final_time_span`); `grep` finds none of `_span_ceiling`, `playback_seat_decision`, `MAX_SAVE_SPAN`, `366`, `MAX_EVENTLOG` in it (M-3). The sibling packages' text (IP-1072/1074/1075) *is* there.
  * `CLAUDE.md` line 125 (P5 bullet) still reads "browser GUI unverified headless"; line 27-29 was corrected and now says the headless suite covers the load-bearing rules (L-4).
  * `ROADMAP.md` line 26 still says "The **Build Spec wins on any conflict**", which `CLAUDE.md` line 45 declares applies nowhere (L-4).
* **Counts in `CLAUDE.md` line 19** ("1700 tests; 1697 passed, 3 skipped; `-m "not browser"` collects 1669 and reports 4 skipped") match what I measured exactly.
* **"Major" wording:** the skills (`04`, `09`, `11`, `README.md`) now say "every release" (owner decision `BL-0318`) and agree with each other and with `NFR-1510`/FS-133; every remaining "major release" in `docs/` outside the pipeline journal and review reports is annotated as superseded by `BL-0318`.

## 8. Closure of earlier findings

### 8.1 Tranche 3 (`M-1`..`M-5`, `L-1`..`L-7`)

| ID | Was | Status | Evidence |
|---|---|---|---|
| M-1 | Training curls returned 403 | **Closed** | `05-core-concepts.md:104,118,164` and `07-white-cell-facilitation.md:53` carry `?cell=white`; `05:167` states the rule. A grep of every `curl` that names `/api/sessions/` in `docs/` (outside pipeline/reviews), `README*` and the skills finds no White-only POST without the seat. The remaining unseated hits are GETs or the session-create call (absent seat is allowed) |
| M-2 | A legitimately advanced session produced a save the system refused | **Closed** | `manager.py` `_span_ceiling()` (start + `MAX_SAVE_SPAN_US`) bounds `step`/`advance`/`catch_up`; probes in §3.3 (19/19 vignettes advance to the ceiling and reload; +1 µs is 400); browser test `test_advance_beyond_the_span_is_refused_visibly_and_the_running_clock_stops_at_the_end` |
| M-3 | 14 package headers contradicted the ledger | **Closed** | script in §1 (no disagreement over 83 files); `IP-1078`/`IP-1080` VERIFIED; the four MBP row notes cleaned (remaining "awaiting 09" text is dated log, §6) |
| M-4 | Palette offered White-only inject entries to every seat | **Closed** | `app.js:2692,2696` gate both inject groups on `CELL === "white"`; `fireInject` also calls `reportControlError`; Chromium: Blue/Red/Observer palettes list no time and no inject entry; browser tests `test_a_non_white_seat_is_not_offered_inject_entries_in_the_palette`, `test_a_refused_inject_is_reported_in_the_visible_status_line` |
| M-5 | Tranche-2 documentation findings unowned | **Closed, one residual** | `CLAUDE.md` lines 19, 27, 169 and "Authoritative source" corrected; GDS-10 `FR-W3` row; GDS-07/08/09 statements; FS-106/FS-110; both ledger allow-list lines deleted; residual items are L-4 below |
| L-1 | Backwards `step`/`advance` was a 500 | **Closed** | §3.3 (400 with reason); `inprocess.py` maps the `ValueError` to `Ack(ok=False)`, `server.py` to 400. A JSON `NaN` `t` is still a 500 (M-1 below) |
| L-2 | A refused load overwrote a live tab's session readout | **Closed** | `showLoadFailure` writes `#control-status` when `SID` is set; Chromium Blue/Red/Observer: `#session` kept, polling alive |
| L-3 | Console noise: Observer 403 dry-runs, `GET /windows/blue/BLUE-RADAR` 404 | **Closed** | `previewOrder` returns early for `observer`, `drawRibbon` does not ask for a sensor's windows; Blue-to-Observer switch produced no 4xx; browser test `test_the_console_asks_for_no_windows_of_a_sensor_and_no_observer_dry_run` |
| L-4 | `aar/playback/*` POSTs unguarded | **Closed** | IP-1077; probe matrix §3.1 |
| L-5 | Fragile guard counts in `test_origin_retag.py` / `test_origin_id_widening.py` | **Closed** | IP-1079 removed the collected-count window (the unfiltered run and the filtered runs both pass; the one self-skip left is the partial-collection check in `test_test_origins.py`, which is by design) |
| L-6 | Rewind leaves the clock running (owner question) | **Still open** | Unchanged and still an owner decision (IP-1074 Decision 4); WCM-4 documents that the running state is left as it was. Carried as L-6 below |
| L-7 | Bounds and the 366-day cap undocumented in GDS/requirements | **Closed** | `FR-4330` (`01-functional-requirements.md:1759-1798`), `FR-7230` (line 3100), GDS-09 lines 163-166 and OQ5, GDS-07 line 191, `08-http-api-reference.md` |

### 8.2 Tranche 2 (`F-01`..`F-16`)

| ID | Status | Evidence |
|---|---|---|
| F-01 Console not wired to refusals | **Closed, with a residual** | Palette/bookmark/load/inject paths show the reason (Chromium §3.2). The toolbar `+1m/+10m/+1h` handler is still unwrapped (M-2) |
| F-02 `FR-4320` scope gap | **Closed** | §3.1 matrix: Creator edits, `save_vignette`, `red_step`, session/draft creation |
| F-03 Save `content` diverges from `baseline` after Creator edits | **Closed** | `test_content_equals_the_saved_force_after_pre_start_edits` in the RTM; 19/19 round trips compare `content` equal |
| F-04 Tools and skill assumed unguarded controls | **Closed** | `tools/record_walkthrough.py:183` advances as `cell=white`; `run-spacesim/SKILL.md` recipe carries the seat |
| F-05 Training examples/API reference | **Closed** | `08-http-api-reference.md` lines 6-14, 62, 72-75; curls (M-1 above) |
| F-06 Ten stale package headers | **Closed** | §1 |
| F-07 Requirement notes and RTM cells | **Closed** | §6 |
| F-08 GDS statements contradict the built system | **Closed** | `grep` for "not embedded", "five White-only", "not registered with the panel" in GDS-07/08/09 finds nothing; OQ1/OQ5 updated |
| F-09 `CLAUDE.md` out of date | **Closed, residuals** | counts, allow-list text and authoritative-source section fixed; code-map omissions and line 125 are M-3 / L-4 |
| F-10 No current Master Build Plan tally | **Closed** | line 915 and 913 (82/0/0/1) |
| F-11 Feature-index statuses and two allow-list lines | **Closed** | §6 |
| F-12 Two readers of the same ledgers; two allow-list formats | **Still open (cosmetic)** | `baseline_ids.py` and `test_doc_integrity.py` still each parse the feature index and package index; carried as L-5 |
| F-13 Damaged save gave HTTP 500 | **Closed** | IP-1102/IP-1103 `validate_save`; 400 for every missing key (probes in tranche 3, regression tests in `test_save_load_robustness.py`) |
| F-14 Browser suite did not cover seat gating | **Closed** | 31 browser tests now include non-White time/inject/bookmark/load cases |
| F-15 Two seat channels | **Closed** | §3.1 |
| F-16 `--origin-report` exits 5 | **Still open** | `python3 -m pytest --origin-report` still exits 5; carried as L-3 |

## 9. Findings

| ID | Finding | Packages / artifacts | Description | Severity | Recommended owner |
|---|---|---|---|---|---|
| M-1 | One White request can make every read of a session return 500; `NaN` time targets give 500 | `POST /clock` (`ClockRequest.rate: float`, `SessionManager.set_clock`), `catch_up`; `TimeRequest.t` for `advance`/`rewind`; IP-1076 scope, `NFR-1600` | `{"running": true, "rate": NaN}` (or `Infinity`, `-Infinity`; Starlette's JSON parser accepts the literals) is stored unchecked. Every following `GET /clock`, `/godview`, `/scene/{cell}`, `/save`, `/objectives` is HTTP 500 for every seat until White posts a finite rate (the pause call itself also 500s). `{"t": NaN}` on `advance` and `rewind` is a 500, not the 400 the span rule promises. Negative and 1e18 rates are accepted. Not reachable from the console (the rate is a fixed list), only by a script or a hand-built request; White-seat assertion is client-trusted, so it is a one-request denial for any LAN participant | Medium | `04-requirements-engineering` (state the valid rate range under `NFR-1600`), then `07-implementation-planning` and `08-code-implementation` |
| M-2 | Toolbar `+1m/+10m/+1h` throws instead of showing the refusal at the span end | `app.js:370` (`const step = async …` bound at `:2351`), IP-1076 AC "refusal visible in the status line", `12-white-cell-manual.md` WCM-4 | The palette (`stepBy`) was fixed to `try/catch` and `reportControlError`; the three toolbar buttons call `step()` with no catch. Chromium, White, clock advanced to `start + 366 d`, click `+1m`: `POST /step` 400, an uncaught page error whose text is the raw JSON `detail`, and `#control-status` stays empty. The manual says these buttons are refused with the reason. The browser suite covers only the palette path, so it is green. `setServerClock` (Pause) has the same shape but cannot be refused for White | Medium | `07-implementation-planning` then `08-code-implementation` (wrap `step`; add a toolbar case to the browser suite) |
| M-3 | `CLAUDE.md` code map omits four packages in scope | `CLAUDE.md` code map; IP-1076, IP-1077, IP-1081, IP-1103 | The durable guide has no text for the 366-day advance ceiling and pinned clock, the playback seat rule, the cap's new home and first-rung check, or the save-span check. The package-owning skills' doc-update step is the stated route for this; IP-1072/1074/1075 were done, these four were not. A future session reading the guide would not learn that `advance` is bounded or that playback is seat-gated | Medium | `08-code-implementation` doc-update step (via a docs-only package from `07`) |
| L-1 | Live event log is unbounded while load refuses more than 100,000 entries | `manager.py` `MAX_EVENTLOG_REPLAY_ENTRIES` (IP-1081), `inject`/order intake | 100 `inject` calls = 100 entries in 0.3 s; about five minutes of scripted calls make a session whose own save cannot be loaded back. Same class as tranche-3 `M-2`, reachable only by a script. Either cap the live log at the same figure with a 400, or state that the cap applies to saves only | Low | `04-requirements-engineering` then `07`/`08` |
| L-2 | Playback cursor is not reset or clamped when the live log is rewound or undone | `session/aar.py` `PlaybackSession`, `inprocess.py` `_playbacks` | After a live rewind the playback `state` still reports a moment later than the end of the recorded log until the next `advance` clamps it. No leak (state is rebuilt from the current log and cell-filtered); a misleading readout for an API consumer | Low | `07` then `08` |
| L-3 | `pytest --origin-report` exits 5 (tranche-2 `F-16`) | `spacesim/tests/conftest.py` | The read-only report clears every item, so pytest reports "no tests ran" with exit code 5; a script that treats non-zero as failure misreads a successful report | Low | `07` then `08` |
| L-4 | Residual stale statements | `CLAUDE.md:125`; `ROADMAP.md:26`; `docs/architecture/10-…matrix.md` §6 counts | "browser GUI unverified headless" (P5 bullet) contradicts the narrowed line 27; ROADMAP's header still says the Build Spec wins on any conflict; GDS-10 §6 coverage counts are run #217 figures (flagged as such, regeneration is its `OQ1`) | Low | `08-code-implementation` doc step (CLAUDE.md), `03-architecture-design-synthesis` (GDS-10 §6), `11-release-readiness` (ROADMAP legend) |
| L-5 | Two parsers of the same ledgers; two allow-list formats (tranche-2 `F-12`) | `baseline_ids.py`, `test_doc_integrity.py`, `test_origin_allowlist.txt`, `doc_integrity_allow_*.txt` | A format change to `feature-index.md` or `packages/INDEX.md` must be fixed in two readers. Both lists are now empty or shrinking, so the practical risk is small | Low | `07` (optional consolidation package) |
| L-6 | Rewind leaves the clock running (tranche-3 `L-6`, open owner question) | IP-1074 Decision 4 | A facilitator who rewinds with the clock running sees it resume immediately. Documented behavior; no one has decided | Low | project owner, then `07` |

## 10. Quality gate

* [x] Every package in scope confirmed `VERIFIED` before the review began (§1).
* [x] All five dimensions exercised with stated evidence (§3-§7).
* [x] Full suite, `-m "not browser"`, `-m browser`, the permanent gates and a fresh-venv lock run executed at `30717a3` with real exit codes and `--junitxml` (§2). `test_doc_integrity.py` re-run after writing the report and the `ROADMAP.md` entry: green.
* [x] Every finding has a severity and an owner; nothing was fixed in-pass. Probes were run from throwaway scripts in the session scratchpad and are not committed.
* [x] Written: this report and the `ROADMAP.md` review entry only. `docs/pipeline/` untouched.

## 11. Recommendation and next step

No Critical or High findings, so the candidate may advance to `11-release-readiness`. The three Mediums are small and independent of each other: a validation gap on `rate`/`NaN` (one request can take a session's reads down, recoverable by White), one unwrapped toolbar handler, and a documentation omission. My recommendation to the release assessment is **GO with M-1 to M-3 recorded as known deviations**, or, if the owner prefers a clean tag, one short remediation package for M-1 and M-2 (both touch `server.py`/`manager.py`/`app.js` and one browser case) plus the `CLAUDE.md` text for M-3, followed by a re-run of this review limited to those files. The lock-built environment reproduces the suite exactly, so the dependency pins are not a reason to hold the release.
