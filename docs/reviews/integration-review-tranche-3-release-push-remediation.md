# Integration Review — Tranche 3 (release-push remediation: White-only extension, console refusal wiring, save robustness, undo/rewind bounds, test-origin retag)

> **Stage:** 10 — Integration Review (fresh session; took no part in implementing or verifying any package in scope)
> **Reviewed commit:** `d7f6791` (branch `claude/test-tag-review-1`, tip incl. `VR-1334`; review branch `claude/integration-review-tranche-3`)
> **Date:** 2026-10-24
> **Scope (explicit package list):** `IP-1311`, `IP-1102`, `IP-1072`, `IP-1073`, `IP-1103`, `IP-1074`, `IP-1335`, `IP-1075`, `IP-1334`
> **Headline:** **0 Critical, 0 High, 5 Medium, 7 Low.** The set composes, every gate is green, and tranche-2 findings `F-01`-`F-04` are closed end to end (one small residual of `F-01`, M-4 below). The remaining defects are one save/advance asymmetry, one palette seam, and a large block of status text that nobody owns (the tranche-2 documentation findings `F-05`-`F-11` were not in any package and are still open).
> **Previous review of this kind:** [`integration-review-tranche-2-white-controls-saves-test-origins.md`](integration-review-tranche-2-white-controls-saves-test-origins.md)

## 1. Scope confirmation

All nine packages read `VERIFIED` on the Master Build Plan, `packages/INDEX.md` and `ROADMAP.md`, and each has a Verification Report in `docs/implementation/verification/`
(`VR-1311`, `VR-1102`, `VR-1072`, `VR-1073`, `VR-1103`, `VR-1074`, `VR-1335`, `VR-1075`, `VR-1334`; `verification/INDEX.md` lists each). Nothing was reviewed around a hole.

Production footprint of the stack against tranche 2's tip (`63e6081`): `session/manager.py` (+220), `ui_web/server.py`, `ui_web/static/app.js`, `creator.js`, `panels.js`, `index.html`, `style.css`,
`content/vignette.py`, `session/inprocess.py` and **one engine file, `engine/simulation.py` (+4/-1, `undo_last` landing time)**. That edit reads the stored initial state only (`int(self._initial_state.get("now", 0))`);
no clock, no RNG, no import.

## 2. Gates and evidence run at `d7f6791`

| Check | Result |
|---|---|
| `python3 -m pytest -m "not browser" --junitxml=…` | exit 0; **1614 tests, 0 failures, 0 errors, 6 skipped** (3 long-standing data-dependent skips in `test_defensive_audit_2026.py` / `test_derived_probabilities.py`, plus 3 by-design "partial run" skips in `test_origin_retag.py` / `test_test_origins.py`, see L-5); 157 s |
| `python3 -m pytest -m browser --junitxml=…` | exit 0; **23 tests, 0 failures, 0 skipped** (Chromium at `/opt/pw-browsers`); whole suite = 1637 |
| Permanent gates and checks: `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`, `test_test_origins.py` | exit 0 (re-run after this report was written, see §10) |
| `pytest --origin-report` | **0 untagged tests**; allow-list file is comments only |
| Allow-list sizes | `doc_integrity_allow_links.txt` 64 lines (unchanged from tranche 2: no shrink), `…_indexes.txt` 3 entries, `…_ledgers.txt` 2 entries (FS-106, FS-110; both still needed, see M-5), `test_origin_allowlist.txt` empty |
| Route-table probe (ad hoc, not committed) | all 42 mutating routes enumerated from `app.routes`; seat matrix in §3 |
| Save round trip on all 19 vignettes | start, step, force-add TLE, step, undo, rewind-to-mid, `GET /save`, `POST /load_save`, re-save, compare `seed/eventlog/final_time/baseline`: **19 of 19 identical, 0 warnings**; then rewind-to-start, save, load again: 19 of 19 `200` |
| Headless Chromium as White, Blue, Red, Observer | see §3 |

## 3. Dimension 1 — Interface consistency

**Route table (derived).** Guarded by `_require_white` (query seat): `clock, param, start, step, advance, rewind, undo, inject, force/tle, force/bulk_import, force/ground, load_save, save_vignette, creator/state (PUT), creator/asset (PATCH, DELETE), creator/seats, red_step, roles/assign, observer/view`; inline `cell != "white"` on `injects/{h}/cancel|edit`; `_refuse_player_seat_on_create` on `POST /api/sessions` and `/draft` (refuses a *named* player seat, allows an absent seat; deliberate, documented in the docstring). `_reject_observer` only: `order, order/validate, *_compute, preview/consequence, cancel, gate/decide, roe/change, recovery, ssn/*`. **Unguarded: `aar/playback/{start,advance,viewpoint,speed}`** (L-4). Probe results with a valid body: draft 200/403/403/403/200 (white/blue/red/observer/none), `load_save` 400/403/403/403/403, `red_step` 200/403/403/403/403, `undo` 400/403/403/403/403, creator asset DELETE 200/403/403/403/403, `start` 200/403/403/403/403. FastAPI validates the body before the seat check (an empty body gives 422 for every seat); harmless, no side effect.

**Console driven in Chromium** (one session, one tab per seat, `?cell=` plus a click on the Observer button):

| Seat | White controls (+1m/+10m/+1h, Rewind, Pause, Session, Creator) | Palette time entries | Settings > Load session of a saved file | Unhandled rejections |
|---|---|---|---|---|
| White | visible, work (`step`, `rewind` to `start_epoch`, `clock` all 200) | offered | `load_save` 200, tab moves to the new session | none |
| Blue / Red | hidden | not offered (IP-1073) | `load_save` 403, **"Load failed: White Cell control: refused…"** shown, polling continues (clock readout kept advancing) | none |
| Observer | hidden | not offered | same refusal | none |

* `loadSaveFile` now stops the realtime clock only after a successful load; the refusal is visible (closes tranche-2 `F-01`). Bookmark chips refuse without posting for non-White.
* **Residual:** the palette still lists "fire inject …" and "inject lib: …" for Blue, Red and Observer. Running one posts `/inject`, gets 403, and writes the reason into `#inject-result`, which lives in a `.white-only` (hidden) panel, so the player sees nothing (M-4).
* Observer after switching from Blue keeps issuing dry-run `order/validate` calls that now return 403, 2 console errors per tab (L-3).
* `GET /windows/blue/BLUE-RADAR` returns 404 on page load (a sensor id used as an asset id), pre-existing console noise (L-3).
* Creator: White opened a draft and added a TLE with no error; Save-as-scenario returned the explanatory 400 ("no user-save directory configured") in the result line, as designed when `content.user_save_dir` is unset.
* `tools/record_walkthrough.py` Beat 6 now advances as `cell=white` and raises on a refusal; `run-spacesim/SKILL.md` curl recipe carries `?cell=white` (closes `F-04`).

**New bounds vs save, load, AAR, playback.** `rewind` outside `[start_epoch, now]` gives 400 (future and `t=0` both checked); `undo` with an empty log gives 400, `undo` of everything lands on `start_epoch` and re-arms the scheduler; on a draft session both are 400. No other caller of `rewind_to`/`undo_last` exists (`grep`: only `server.py`, `inprocess.py`, `manager.py`). `aar/playback/start` works on a loaded save. Round trips after undo/rewind are exact (§2). **One asymmetry found:** M-2.

## 4. Dimension 2 — Invariant sweep

| Invariant | Evidence | Result |
|---|---|---|
| Deterministic core | `git diff 63e6081..HEAD -- spacesim/engine` is the single `simulation.py` hunk (reads `_initial_state["now"]`); `test_determinism.py`, `test_import_guard.py` green; 19/19 save-replay equality | Holds |
| Engine import boundary | import-guard green | Holds |
| Fog of war at the seam | No new cell-scoped read added; `start_epoch` on `GET /clock` is not ground truth. `content`/`baseline` in `/save` remain on the `FR-6220` list | Holds |
| Plan-first, sub-stepped clock | `rewind`/`undo` only re-arm via `_arm_schedule`; running state left unchanged (see L-6) | Holds |
| Content-as-data | `content` portion stays the vignette file shape; pre-start Creator edits and deletes now appear in `content` (probe: edited asset's owner and a deleted asset reflected; tranche-2 `F-03` closed) | Holds |

## 5. Dimension 3 — Behavioural coherence

* **Closed tranche-2 items verified end to end:** `F-02` (every Creator edit, `save_vignette`, `seats`, `red_step`, session/draft creation refused for a named player seat; matrix above), `F-03` (content equals saved force after edits, `test_save_load_robustness`), `F-13` (dropping `seed`, `eventlog`, `baseline`, `content` or `final_time` from a save each gives 400, never 500), `F-15` (`roles/assign` and `observer/view` now use the query seat like the rest).
* **Save vs advance (M-2):** `validate_save` (IP-1103) refuses a save whose `final_time` is more than 366 days past the start, but nothing bounds `POST /advance`. Probe: advance 30 days, save, load = 200; advance 370 days, save, load = `400 save key 'final_time' is beyond the maximum span`. A session White legitimately advanced produces a save that the same system refuses to load.
* **Backwards time (L-1):** IP-1074 bounds rewind, but `POST /step` with a negative `dt_sim_s` and `POST /advance` with `t` before now still raise `ValueError` out of `Simulation.advance_to` as an HTTP 500.
* **Two forward-time paths in the console:** toolbar +1m/+10m/+1h use `/step`; the palette and `stepBy` use `/advance` with `SCENE.now + s` (the last polled time, which can lag the server's lazy clock). Same effect, different routes and arithmetic; harmless today, and the source of the L-1 exposure.
* **Load failure readout (L-2):** a refused load in a joined Blue/Red tab replaces the `#session` readout ("session sess-1") with "Load failed: …" although the tab remains connected and live.
* **Rewind and the running clock (L-6):** rewind keeps the clock running; `IP-1074` Decision 4 ("should a rewind pause the clock?") is recorded as an open owner question and is unanswered.

## 6. Dimension 4 — Traceability coherence

* Master Build Plan, `packages/INDEX.md`, `verification/INDEX.md` and `ROADMAP.md` agree that all nine are `VERIFIED` with a VR link. RTM Test cells for the tranche's requirements are generated and agree (checked by `test_test_origins`); `FR-4310`, `FR-4320`, `FR-7220`, `FR-7230` cite the new tests. The "Not met as built" notes in `01-functional-requirements.md` are gone.
* **Package headers (M-3):** line 5 of `IP-1311` ("COMPLETE … awaiting 09"), `IP-1102` ("COMPLETE … awaiting 09"), `IP-1075` ("READY") and `IP-1334` ("COMPLETE … awaiting 09") disagree with their `VERIFIED` ledger rows, **and the ten tranche-2 headers (`IP-1068`, `1101`, `1091`, `1069`, `1330`, `1350`, `1340` "READY"; `1331`, `1332`, `1333` "BLOCKED") are unchanged**. 14 of the 19 packages touched in tranches 2 and 3 carry a wrong header. The Master Build Plan rows for `IP-1311`, `IP-1074` and `IP-1334` also keep "awaiting `09`" / "pending `09`" sentences in their notes next to the `VERIFIED` cell. `IP-1350`'s ledger check cannot see package headers, so the suite is green.
* **Feature index and allow-lists (M-5):** `FS-106` and `FS-110` still read "Ready for implementation planning" for versions that now have `VERIFIED` packages, so the two `doc_integrity_allow_ledgers.txt` lines cannot be deleted; no allow-list shrank in this tranche.

## 7. Dimension 5 — Documentation coherence

* **Updated correctly:** `CLAUDE.md` code map (IP-1072/1073/1074/1075 text), `08-http-api-reference.md` (seat requirement, rewind span, `start_epoch`), `10-ui-reference.md`, WCM-4 in `12-white-cell-manual.md`, the `FR-4310` notes.
* **Not updated (M-1):** three training curl examples still omit `?cell=white` and now return 403: `docs/training/05-core-concepts.md:104` (`force/tle`), `:164` (`load_save`), `07-white-cell-facilitation.md:53` (`inject`). This is tranche-2 `F-05`; `IP-1073` fixed the tools and the skill but no package covered the manuals.
* **Open since tranche 2 (M-5, unchanged):** `CLAUDE.md` line 19 "469 tests green" (suite is 1637), line 27/131 "browser GUI unverified headless" (23 headless tests exist), line 174 allow-list text (list is empty), "Authoritative source" still calls GDS-06-GDS-10 scaffold-only; GDS-10 `FR-W3` row still says "FR-4310 not met as built"; GDS-07 §6 / GDS-09 §4 / GDS-08 line 137 statements from tranche-2 `F-08`.
* **Not documented (L-7):** `GET /clock`'s `start_epoch` and the 400 span rule are in the training API reference but not in GDS-09; the 366-day save cap (`MAX_SAVE_SPAN_US`) is in no manual, GDS or requirement text I could find.

## 8. Findings

| ID | Finding | Packages / artifacts | Description | Severity | Recommended owner |
|---|---|---|---|---|---|
| M-1 | Training curls return 403 (tranche-2 `F-05` still open) | `docs/training/05-core-concepts.md:104,164`; `07-white-cell-facilitation.md:53` | `POST force/tle`, `load_save`, `inject` examples omit `?cell=white`; learners following the manual get 403. | Medium | `08-training-manual-authoring` then `09-training-manual-review` |
| M-2 | A legitimately advanced session produces a save the system refuses | IP-1103 `validate_save` / `MAX_SAVE_SPAN_US` (366 days) vs `POST /advance` (`server.py:479`), `GET /save`, `POST /load_save` | No bound on advance; advance +370 days, save, load = 400. Either bound advance to the same span or define the cap as relative to something the engine enforces. | Medium | `04-requirements-engineering` (span rule) then `07`/`08` |
| M-3 | 14 package headers contradict the ledger; ledger check blind to them | `IP-1311`, `1102`, `1075`, `1334` (new) and the ten tranche-2 packages; MBP rows `IP-1311/1074/1334` notes | Pre-build or "awaiting 09" status on `VERIFIED` packages. | Medium | `07-implementation-planning` (headers, MBP notes); check extension via `00-intake` |
| M-4 | Palette offers White-only inject entries to every seat; the refusal is written to a hidden element | `app.js` `PALETTE.items` (inject entries, ~2680), `fireInject`, `#inject-result` in a `.white-only` panel | Residual of tranche-2 `F-01`: Blue/Red/Observer choose "fire inject …", get 403, see nothing. Server enforcement holds. | Medium | `07` then `08-code-implementation` (one-line seat gate, plus a browser case) |
| M-5 | Tranche-2 documentation findings `F-06`-`F-11` not closed by any package | `CLAUDE.md` 19/27/131/174/42-52; GDS-10 `FR-W3`; GDS-07/08/09; `feature-index.md` FS-106/FS-110; two `doc_integrity_allow_ledgers.txt` lines; Master Build Plan tally | See §6-§7. Nothing new broke; nothing was owned. | Medium | per tranche-2 report: `03`, `04`, `05`/`06`, `07`, `08` doc-update step; `11` for the status line |
| L-1 | Backwards `step`/`advance` gives HTTP 500 | `server.py:474-482`, `engine/simulation.py:74` | Same class IP-1074 fixed for rewind. | Low | `07` then `08` |
| L-2 | A refused load overwrites a live tab's session readout | `app.js` `showLoadFailure` writes `#session` | Blue tab shows "Load failed" while still connected. | Low | `07` then `08` |
| L-3 | Console noise: Observer 403 dry-runs; `GET /windows/blue/BLUE-RADAR` 404 | `app.js` preview after seat switch; sensor id used as asset id | Console errors on every load; the browser suite does not assert on them. | Low | `07` then `08` |
| L-4 | `aar/playback/*` POSTs unguarded | `server.py:960-992` | Any seat, including Observer, can start/advance/retarget the shared playback cursor (ground-truth viewpoint). Known (`VR-1072` F3, "scope decision outstanding"); no one owns the decision. | Low | `04-requirements-engineering` (scope), then `07` |
| L-5 | Fragile guard counts | `test_origin_retag.py` (`COLLECTED_UPPER = 1700`, `COLLECTED_BEFORE = 1464`; 170 exact tag rows), `test_origin_id_widening.py` (13 and 7 pinned counts) | Suite is 1637: 63 tests of headroom, then the guard fails on ordinary growth; adding one test to `test_assessment.py` or `test_research_batch.py` fails the widening test. The count test self-skips under `-m "not browser"` and `-m browser` (hence 6 skips, not 3-4 as ledgers say), so it runs only in an unfiltered run. | Low | `07` (re-express as "no test lost", not a fixed window) then `08` |
| L-6 | Rewind leaves the clock running (open owner question) | IP-1074 Decision 4 | After rewind-to-start a running clock keeps advancing in real time. | Low | project owner decision, then `07` |
| L-7 | Bounds and the save-span cap are undocumented in GDS/requirements | GDS-09 §4, `01-functional-requirements.md` (`FR-4310`, `FR-7230`) | `start_epoch` on `/clock` and the 366-day cap appear only in code, tests and one training table. | Low | `03-architecture-design-synthesis` / `04` |

## 9. Quality gate

* [x] Every package in scope confirmed `VERIFIED` before the review began.
* [x] All five dimensions exercised with stated evidence.
* [x] Full suite, browser suite and permanent gates run at `d7f6791`; results in §2.
* [x] Every finding has a severity and an owner; none was fixed in-pass.
* [x] Written: this report and the `ROADMAP.md` review entry only (no `docs/reviews/INDEX.md` exists; `docs/pipeline/` untouched).

## 10. Recommendation and next step

No Critical or High findings. Tranche-2 `F-01` to `F-04` (plus `F-03`, `F-13`, `F-15`) are closed; `F-05` to `F-11` are open and now the largest block of debt. Next: run `07-implementation-planning` for one small remediation package covering M-2, M-4, L-1 to L-3 and L-5 (ask `04-requirements-engineering` first about the span rule in M-2 and the playback scope in L-4), and send M-1, M-3 and M-5 to their owning skills as one documentation batch. Re-run this review only if the remediation changes shipped code; otherwise `11-release-readiness` can consume this report with M-1 to M-5 recorded as known deviations.
