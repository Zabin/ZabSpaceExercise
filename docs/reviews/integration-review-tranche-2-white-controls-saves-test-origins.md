# Integration Review — Tranche 2 (White-only controls, self-contained saves, test-origin and documentation checks)

> **Stage:** 10 — Integration Review (fresh session; took no part in implementing or verifying any package in scope)
> **Reviewed commit:** `63e6081` (branch `claude/verify-ip-1333`, the top of the stacked chain; review branch `claude/integration-review-tranche-2`)
> **Date:** 2026-10-24
> **Scope (explicit package list, owner-authorized work of 2026-10-23/24):** `IP-1068`, `IP-1101`, `IP-1091`, `IP-1069`, `IP-1330`, `IP-1350`, `IP-1340`, `IP-1331`, `IP-1332`, `IP-1333`
> **Headline:** **0 Critical, 0 High, 9 Medium, 7 Low.** The set composes and every gate is green; the defects are half-wired client and tooling call sites, one requirements-scope gap, one data-fidelity gap in the new save, and a large amount of stale status text.
> **Previous review of this kind:** [`integration-review-18-package-tranche.md`](integration-review-18-package-tranche.md)

## 1. Scope confirmation

All ten packages are `VERIFIED` in all three places that carry the status: the Master Build Plan table
(`docs/implementation/00-master-build-plan.md` rows for each), `docs/implementation/packages/INDEX.md`, and `ROADMAP.md`.
Verification Reports present under `docs/implementation/verification/`: VR-1068, VR-1101, VR-1091, VR-1069 (v2.0, after a
`RETURNED` v1.0), VR-1330, VR-1350, VR-1340, VR-1331, VR-1332, VR-1333. Nothing was reviewed around a hole.

Production-code footprint of the set against `origin/main` (112 files, almost all tests and docs): `spacesim/session/manager.py`,
`spacesim/session/inprocess.py`, `spacesim/ui_web/server.py`, `spacesim/ui_web/static/app.js` (4 lines), `spacesim/ui_web/static/panels.js`,
`pyproject.toml`, the session-start hook (adds `playwright`). **`spacesim/engine/` is untouched** (`git diff --stat origin/main..HEAD -- spacesim/engine` is empty).

## 2. Gates and evidence run at `63e6081`

| Check | Command | Result |
|---|---|---|
| Full suite | `python3 -m pytest -p no:cacheprovider --junitxml=…` | exit 0; junit: **1284 tests, 0 failures, 0 errors, 3 skipped** (the same three long-standing data-dependent skips in `test_defensive_audit_2026.py` and `test_derived_probabilities.py`); 189 s. The 10 browser tests ran (not skipped). |
| Permanent gates | `test_import_guard.py`, `test_determinism.py` | exit 0; 14 tests, 0 failed, 0 skipped |
| Browser suite | `pytest -m browser` | exit 0; 10 tests, 0 skipped (Chromium at `/opt/pw-browsers`) |
| Doc-integrity and origin checks | `test_doc_integrity.py`, `test_test_origins.py` | exit 0 |
| Origin report | `pytest --origin-report` | prints; **0 untagged tests**; allow-list file is empty (comments only). Exit status is 5 ("no tests ran") by design. Working tree stayed clean (the report writes nothing). |
| Strict markers | `addopts = "-q --strict-markers"`; `pyproject.toml` registers both `browser` and `verifies(*ids)` | Both markers resolve; no unknown-marker errors; a module can carry both (`test_browser_console_rules.py` does). |
| Route-table probe (TestClient, ad hoc, not committed) | see §3 and findings | `load_save` blue and no-seat 403; blue `PUT /creator/state` 200; blue `red_step` 200; save with `seed` or `eventlog` removed 500 |

**Requirements no test names** (from `--origin-report`; 30): `FR-3410, FR-3510, FR-3520, FR-4710, FR-4720, FR-6110, FR-6220, FR-6410, FR-6610, FR-7110,
NFR-1100, NFR-1200, NFR-1400, NFR-1510, NFR-2000, NFR-2100, NFR-2300, NFR-2400, NFR-2500, NFR-2600, NFR-2800, NFR-2900, NFR-3000, NFR-3040, NFR-3060, NFR-3200,
NFR-3300, NFR-3500, NFR-3600, NFR-3810`. Context: `FR-3510/3520` are `IP-1160` (`BLOCKED`); `FR-6220` is verified by Inspection; `NFR-3810` is parked on `BL-0319`.
`FR-7110` (AAR replay) and `FR-6110`/`FR-6410`/`FR-6610` are leaves the set did not touch whose tests exist but are tagged to other IDs; that is a coverage-audit
item for the next major-release relevance audit (`NFR-2830`), not a defect of this set.

## 3. Dimension 1 — Interface consistency

**Checked:** every mutating route in `server.py` (42 decorators) against the `_require_white` / `_reject_observer` / body-`cell` guards; every `api.post/put/patch/del`
call in `app.js` and `creator.js`; `tools/` and `.claude/skills/run-spacesim`; the `load_save` route shape against `loadSaveFile`; the panel registry against IP-1340.

* **Guard coverage as built.** `_require_white` (query `cell`) guards `clock, param, start, step, advance, rewind, undo, inject, force/tle, force/bulk_import, force/ground, load_save`.
  `creator/seats` and the inject cancel/edit routes carry their own inline `cell != "white"` checks. `roles/assign` and `observer/view` are refused on the **body** `cell`
  inside `InProcessSession`, a second seat channel (F-15). The rest are Observer-only guarded.
* **`load_save`**: `_require_white(cell)` runs before `api.load_save_with_warnings`; refusal is 400 `{detail}` (`ValueError`), success `{session, warnings}`. Server side is coherent
  (tested: blue 403, no seat 403, observer 403, white 200). The **client** is not (F-01).
* **The browser always sends `cell=<its seat>`** through `api.post/_mutate`, so a White tab satisfies every guard, including the creator's `force/*` calls (`creator.js:46,69` use the same `api`).
  `driver.py` (run-spacesim) steps as White before switching cell, so it still works. IP-1340 correctly set up its sessions over HTTP naming `cell=white` (module docstring).
* **Seams that break or fail silently**: see F-01 (console), F-04 (`tools/record_walkthrough.py` Beat 6 steps as Blue through `stepBy(600)` and now gets a 403 it never reports; `run-spacesim/SKILL.md` curl recipe), F-05 (three training-manual curl examples).
* **IP-1069 registry vs IP-1340:** the two do not touch. `test_panel_registry.py` is a static registry check; the browser suite drives fog labels, the dry-run Issue gate and the consequence confirmation only. No browser test exercises the panel menu or White-only panel hiding (F-14). No contradiction, only a gap.
* **Markers:** `verifies` and `browser` coexist; browser tests are tagged `verifies("NFR-2840", …)` and are counted by the origin report. No conflict.

## 4. Dimension 2 — Invariant sweep

| Invariant | Evidence | Result |
|---|---|---|
| Deterministic core | `engine/` diff empty; `test_determinism.py` and `test_import_guard.py` green; the save/resume tests (`test_self_contained_save.py`) replay byte-identically | Holds |
| `from_state` determinism | The self-contained branch builds a `SessionManager` from the save's `content`, then installs `state["baseline"]` as `sim._initial_state` and the saved event log, and calls `_rebuild(stop_time=final_time)`. Replay input is therefore `(baseline, seed, eventlog)` exactly as the legacy path used `(world built from the vignette file, seed, eventlog)`; no wall clock, no RNG outside `SeededRng`. The only new inputs are validated first (`validate_save` runs before any replay or session registration). | Holds |
| Engine import boundary | No engine file changed; import-guard green | Holds |
| Fog of war at the SessionAPI seam | The new save content/baseline are served only by `GET /save`, which is on the `FR-6220` named list ("the save file (`FR-7210`)"), mirrored in CLAUDE.md and GDS-09 §4. I found no other route that returns `state["content"]` or `["baseline"]`: `creator_state`/`creator_scene` are also FR-6220-listed and return the world's asset list (unchanged by this set). The new portion adds full Red and Blue force definitions, objectives, briefs and tutorials to `/save`, but `/save` already returned the entire event log and pending queue, so no new category of ground truth is exposed. `/save` stays reachable by any seat (documented LAN trust model). | **Confirmed `/save` is on the list; no leak beyond FR-6220** |
| Plan-first, sub-stepped clock | No change to order or clock logic; IP-1091 is test-only; IP-1068 only adds a 403 in front of the same calls | Holds |
| Content-as-data | The save's `content` portion uses the vignette file format (`Vignette.model_dump`); no scenario logic added to Python | Holds, with the data-fidelity gap in F-03 |

## 5. Dimension 3 — Behavioural coherence

* **Duplicated or parallel mechanisms (F-12).** `baseline_ids.py` (IP-1330) and `test_doc_integrity.py` (IP-1350) each parse `docs/features/feature-index.md` and
  `docs/implementation/packages/INDEX.md` with their own regexes, for different purposes (ID set vs status words); a format change must be fixed in two readers. The RTM is parsed only by `baseline_ids.regenerate_matrix`
  (one parser, as intended). There are two allow-list formats: a bare module list (`test_origin_allowlist.txt`, now empty) and pipe-delimited `doc_integrity_allow_{links,indexes,ledgers}.txt` (links file is 8.8 KB, 64 lines).
  Both are shrink-only and tested, so the divergence is cosmetic, not behavioural.
* **Dual seat channel (F-15).** `roles/assign` and `observer/view` trust a **body** `cell`; every other White guard trusts the **query** `cell`. The console hard-codes `cell: "white"` in those two bodies regardless of the active seat, so the body check is satisfied by any tab that calls them. Same trust level (client-asserted), but two conventions for the same rule.
* **Workflow that dead-ends at a seam (F-01).** A Blue/Red/Observer user can still *see* "advance +1 min/+10 min/+1 hour" and "rewind to start" in the command palette (`PALETTE.items`, `app.js` ~2611) and bookmark chips that rewind (`app.js` ~2528). Before IP-1068 these silently worked (the breach). Now they fail with an unhandled promise rejection (no `.catch`, no global `unhandledrejection` handler).
  `loadSaveFile` (bound at `app.js:2259` with no catch) calls `stopRealtimeClock()` **before** the POST, so a refused or invalid load (403 for a non-White seat, 400 for IP-1101's refusal) leaves the tab with its poll loop stopped and no message. The 400 path IP-1101 added is never shown to the user.
* **Save content vs baseline (F-03).** After a pre-start Vignette Creator edit (`creator_edit_asset`, `creator_delete_asset`, `creator_set_state`) of an asset the vignette built, `save_state` leaves the `content` portion describing the original vignette (probe: an owner reassignment is absent from `content`, and a deleted asset is still listed) while `baseline` is correct. Resume is right because the baseline wins; but `FR-7220` ("the content portion can be extracted and loaded as a fresh vignette") yields a force that is not the one that was saved. `_built_asset_ids` only handles *additions*.
* **Hostile or damaged saves (F-13).** A save with `save_format` set but `seed` or `eventlog` missing gets through `validate_save` and raises `KeyError` in `from_state`: HTTP 500 rather than 400.

## 6. Dimension 4 — Traceability coherence

* **Master Build Plan vs packages/INDEX vs ROADMAP:** all ten rows read `VERIFIED` in all three (and the VR links resolve; the doc-integrity link check is green). One pre-existing row (`IP-1052`) carries a `🟢 VERIFIED` glyph where the other 66 use `✅`.
* **No current consolidated tally (F-10).** The newest package-status lines in the Master Build Plan (2026-10-24) say "other statuses as the run #250 line below", and the run #250 line says `IP-1331/1332/1333 COMPLETE`. Lines for runs #230-#236 carry "57 VERIFIED"; nowhere is the present state written down (67 `VERIFIED`, `IP-1311` `READY`, `IP-1160` `BLOCKED`; 69 rows). Notes at the foot of the plan (runs #219-#221) still say "READY, not yet authorized". The plan's *Feature Mapping* header omits FS-133/134/135 (it already omitted several earlier ones).
* **Package-file headers (F-06).** Every one of the ten package files still carries its pre-build status header:
  `IP-1068`, `IP-1101`, `IP-1091`, `IP-1069`, `IP-1330`, `IP-1350`, `IP-1340` say `🟢 READY — authored 2026-10-23 …` (line 5); `IP-1331`, `IP-1332`, `IP-1333` say `🔴 BLOCKED — on IP-1330 reaching …` (line 5).
  IP-1350's ledger check compares Master Build Plan, packages/INDEX, GDS INDEX and the FS pair only, so it cannot see package headers: that is why the suite is green with ten wrong headers.
* **RTM (`docs/requirements/03-requirements-traceability-matrix.md`) Impl. Package column (F-07):** `NFR-2820`, `NFR-2830`, `NFR-2850`, `NFR-3840` still say `IP-1330 (COMPLETE 2026-10-23, awaiting 09)` (now `VERIFIED`); `NFR-2820` does not name `IP-1331`/`1332`/`1333`; `FR-7230`'s Future Feature cell says "UNASSIGNED (BL-0302: feature specification pending)" though FS-110 v2.0 exists; `FR-7220`'s cell still reads "not met as built … 'not met as built' note stands until VERIFIED". Correct and current: `FR-4310`/`FR-4320` (`IP-1068`), `FR-7210`/`FR-7230`/`NFR-1800` (`IP-1101`), `NFR-1300` (`IP-1091`), `NFR-2840`, `NFR-3030`, `NFR-3800/3820/3830`. The Test column is generated and agrees (checked by `test_test_origins.py`).
* **Requirement notes (F-07):** `FR-4310` Notes (`01-functional-requirements.md:1590`) still read "**Not met as built** … no code enforces it"; `FR-7220` Notes (`:2857`) still read "**Not met as built**". Both are now false.
* **Feature index (F-11):** FS-106 ("Done (≤ v2.2, except `FR-4310` enforcement); v2.3-v2.4 … Ready for implementation planning"), FS-110 ("v2.0 additions Ready for implementation planning"), FS-133/134/135 ("Ready for implementation planning") are stale. Because the spec headers say the same, IP-1350's pair check passes; the two allow-listed `fs:` ledger lines (FS-106, FS-110) are exactly this tranche's stale state.
* **GDS-10** (`10-requirements-traceability-matrix.md`): FR-W3 row says "IP-1060 (FR-4310 not met as built)" with test `test_session.py`; the summary counts ("59 packages, 57 VERIFIED", line 185) are as of run #204 and say so.

## 7. Dimension 5 — Documentation coherence

* **CLAUDE.md (F-09).** (a) Line 174: "modules still on `spacesim/tests/test_origin_allowlist.txt` are tolerated; that list only shrinks" — the list is empty (IP-1333), so every test must now be tagged. (b) Line 19: "469 tests green, 3 skipped" — the suite is 1284 tests, 3 skipped. (c) "Authoritative source" section says GDS-06-GDS-10 are "currently scaffold-only" and tells the reader to treat build-spec as the only text for those topics; `docs/architecture/INDEX.md` §1 shows GDS-06-10 authored with closed merge gates. (d) Line 27 / P5 bullet: "browser GUI is unverified headless" — IP-1340 now verifies three console rules headlessly (the claim should be narrowed, not removed). (e) The code map does not list the new test infrastructure (`spacesim/tests/conftest.py`, `baseline_ids.py`, `test_browser_console_rules.py`, the doc-integrity allow-lists) or `SessionManager.validate_save`/`load_save_with_warnings`. The IP-1068 LAN-trust paragraph and IP-1101's code-map text *were* updated.
* **GDS (F-08).** `07-data-model.md` §6 still describes the old save envelope ("The vignette itself is not embedded") and its Open Questions OQ1-OQ3 are "decided … to take effect when the self-contained save ships" (it has shipped). `09-api-specification.md` §4 rule 3, the "Everything else … by UI convention only" paragraph, line 153 ("the five White-only checks"), line 209, and **OQ1** are now wrong. `08-ui-architecture.md` line 137 ("the Compare and Assessment panels are not registered with the panel manager (see OQ2)") is wrong since IP-1069. `06-non-functional-requirements.md` was not checked against `NFR-1300` beyond the RTM row.
* **Training corpus (F-05).** WCM-10 in `12-white-cell-manual.md` *was* updated (a save "carries the vignette it was started from"). Not updated: `docs/training/05-core-concepts.md` lines 104 and 164 (curl `force/tle`, `load_save`), `07-white-cell-facilitation.md` line 53 (curl `inject`) — each now returns 403 without `?cell=white` — and `08-http-api-reference.md`, which lists the White controls but says nothing about the seat requirement or about the new `{session, warnings}` response and 400 refusal of `load_save`. `10-ui-reference.md` §10.1.3 does not mention the legacy-save / version warning the console now raises with `alert()`.
* **INDEX files:** `docs/implementation/packages/INDEX.md`, `verification/INDEX.md` and `ROADMAP.md` list all ten packages and ten VRs. `docs/reviews/` has no `INDEX.md` (so the doc-integrity index check does not apply); `ROADMAP.md` carries the review-tracking entries, and this review is added there.

## 8. Findings

| ID | Finding | Packages / artifacts | Description | Severity | Recommended owner |
|---|---|---|---|---|---|
| F-01 | Console not wired to the new 403/400 behaviour | IP-1068, IP-1101; `app.js` palette (~2611-2614), bookmark chips (~2528), `loadSaveFile` (~1861, bound at 2259) | Palette "advance"/"rewind" entries and bookmark rewind are offered to Blue/Red/Observer and now fail silently (unhandled rejection). `loadSaveFile` stops the realtime clock before posting and never catches the 403 or IP-1101's 400, so a refused load gives no message and leaves polling stopped. | Medium | `07-implementation-planning` (remediation package) then `08-code-implementation` |
| F-02 | FR-4320 scope gap: other force-edit and White-authoring routes accept non-White seats | IP-1068, IP-1174 (`creator/*`), `server.py` | `PUT /creator/state`, `PATCH`/`DELETE /creator/asset/{id}`, `POST save_vignette`, `POST red_step`, `POST /api/sessions` and `/draft` are guarded only against the Observer. Probe: blue `PUT /creator/state` returns 200, blue `red_step` 200. FR-4320's list names TLE/bulk/ground add but "edit the force" arguably covers the Creator edits; `save_vignette` writes a file to `user_save_dir`. The requirement does not say whether these are in scope. | Medium | `04-requirements-engineering` (decide scope of FR-4320), then `07`/`08` |
| F-03 | Save `content` portion diverges from `baseline` after Creator edits | IP-1101 (`manager.py` `save_state`, `_built_asset_ids`), IP-1174 | Edits/deletes of vignette-built assets before start are not reflected in `content` (only additions are). Resume is correct (baseline wins) but the extracted content portion (FR-7220) is not the saved force. | Medium | `07-implementation-planning` then `08-code-implementation` |
| F-04 | Tool and skill callers still assume unguarded controls | IP-1068; `tools/record_walkthrough.py` Beat 6 (`stepBy(600)` as Blue); `.claude/skills/run-spacesim/SKILL.md` lines 84-85 | The walkthrough recorder's time advance is now a 403 it does not report (captures a stale scene); the skill's curl recipe for `start`/`step` omits `?cell=white` and fails. | Medium | `08-code-implementation` for the recorder (via a `07` package or `00-intake`); `run-spacesim` skill owner via `00-intake` |
| F-05 | Training manual examples now return 403, API reference silent | IP-1068, IP-1101; `docs/training/05-core-concepts.md:104,164`, `07-white-cell-facilitation.md:53`, `08-http-api-reference.md`, `10-ui-reference.md` §10.1.3 | Three curl examples omit `?cell=white`; API reference does not state the seat requirement or the `{session, warnings}` / 400 contract; UI reference omits the load warning. Check §15.1 rows for these sections. | Medium | `08-training-manual-authoring` (then `09-training-manual-review`) |
| F-06 | Ten package-file headers stale; ledger check cannot see them | `IP-1068`, `1101`, `1091`, `1069`, `1330`, `1350`, `1340` (`READY`), `IP-1331`, `1332`, `1333` (`BLOCKED`), all line 5; IP-1350 | Every package in scope still shows its pre-build status. IP-1350's ledger pairs exclude package headers, so no test fails. | Medium | `07-implementation-planning` (headers); extending the check goes through `00-intake` to `07` |
| F-07 | Requirement notes and RTM cells stale | `01-functional-requirements.md:1590` (FR-4310), `:2857` (FR-7220); RTM rows FR-4310/FR-7220/FR-7230/NFR-2820/2830/2850/3840; GDS-10 FR-W3 row and counts | "Not met as built" notes now false; four NFR rows say `IP-1330 COMPLETE, awaiting 09`; NFR-2820 omits IP-1331/1332/1333; FR-7230 "feature specification pending". | Medium | `04-requirements-engineering` (FR notes, RTM) and `03-architecture-design-synthesis` (GDS-10) |
| F-08 | GDS statements contradict the built system | `architecture/07-data-model.md` §6 and OQ1-OQ3; `09-api-specification.md` §4, lines 153/209, OQ1; `08-ui-architecture.md:137` | Describe saves without content, five White-only checks, un-registered panels. | Medium | `03-architecture-design-synthesis` |
| F-09 | CLAUDE.md out of date | `CLAUDE.md` lines 19, 27, 174, "Authoritative source", code map | See §7. | Medium | `08-code-implementation` doc-update step for the code map/workflow text; `11-release-readiness` for the status line |
| F-10 | Master Build Plan has no current tally; stale notes; Feature Mapping | `00-master-build-plan.md` lines 14, 749-759, 891-913 | See §6. | Low | `07-implementation-planning` |
| F-11 | Feature-index statuses stale (and their two allow-list entries) | `feature-index.md` FS-106, FS-110, FS-133, FS-134, FS-135; spec headers; `doc_integrity_allow_ledgers.txt` | Statuses read "Ready for implementation planning"; the two allow-list lines can be deleted once FS-106/FS-110 are corrected. | Low | `05-feature-decomposition` / `06-feature-specification` |
| F-12 | Two readers of the same ledgers; two allow-list formats | `baseline_ids.py`, `test_doc_integrity.py`, `test_origin_allowlist.txt`, `doc_integrity_allow_*.txt` | Parallel parsers of `feature-index.md` and `packages/INDEX.md`; bare-list vs pipe-delimited allow-lists. No behavioural conflict today. | Low | `07-implementation-planning` (consolidation package, optional) |
| F-13 | Damaged save with `save_format` but missing `seed`/`eventlog` gives HTTP 500 | IP-1101 `validate_save`/`from_state` | Required top-level keys are not validated before replay. | Low | `07` then `08-code-implementation` |
| F-14 | Browser suite does not cover the seat-gating or panel seams | IP-1340 vs IP-1068/IP-1069 | No headless test that a non-White seat does not see White controls/panels or that panel registration works in the page. | Low | `07-implementation-planning` (extend FS-134) |
| F-15 | Two seat channels for the White check | `roles/assign`, `observer/view` (body `cell`) vs all other guards (query `cell`) | Same trust level, inconsistent convention; the console hard-codes `cell:"white"` in those bodies. | Low | `03-architecture-design-synthesis` (document) or `08` |
| F-16 | `--origin-report` exits 5 | IP-1330 `conftest.py` | The report mode clears all items, so pytest reports "no tests ran" with exit 5; a script treating non-zero as failure will misread a successful report. | Low | `08-code-implementation` (via `07`) |

## 9. Stacked-branch risk (PRs #59-#80)

* **Topology.** `origin/main` (`bcfa9ff`, merge of #58) to the top is a single linear chain of 39 commits on 22 branches, each a strict descendant of the previous (counts from main: 2, 3, 4, 5, 6, 7, 11, 13, 15, 17, 19, 22, 23, 25, 27, 29, 30, 31, 32, 33, 36, 39). The top (`verify-ip-1333`) is 0 commits behind this review branch's base.
* **Merge in order with merge commits (tested in a scratch clone):** all 22 branches merged `--no-ff` in order with no conflicts, and the result is tree-identical to `claude/verify-ip-1333`. Merging only the top PR into main (or `--squash` of the top) is also conflict-free.
* **Squash-merge one PR at a time fails (tested):** squash-merging #59 into `main` and then merging the next branch conflicts in `docs/pipeline/pipeline-journal.md`, `docs/implementation/00-master-build-plan.md` **and `spacesim/ui_web/server.py`** (the child still carries the original, un-squashed commits). The same happens at every later PR.
* **Files edited by many branches (commit counts over the chain):** `docs/pipeline/pipeline-journal.md` 26, `ROADMAP.md` 23, `docs/implementation/packages/INDEX.md` 22, `docs/implementation/00-master-build-plan.md` 22, `docs/requirements/03-requirements-traceability-matrix.md` 15, `docs/pipeline/backlog.md` 14, `docs/implementation/verification/INDEX.md` 11, `CLAUDE.md` 5, `spacesim/tests/test_origin_allowlist.txt` 4, `pyproject.toml` 2, `server.py` 2, `panels.js` 2. All are append-or-edit-in-place ledgers, so any rebase or squash that breaks the shared ancestry produces many textual conflicts on the same lines.
* **Recommendation.** Merge **in order with real merge commits** (or fast-forward each, since the chain is linear), not squash and not rebase. Do not delete the base branch of a child PR until the child is retargeted or merged (GitHub retargets cleanly only when history is preserved). Alternatively, land the whole chain at once by merging the top PR (#80) into `main` with a merge commit and closing #59-#79 as included; that is one operation with no conflicts and identical content, at the cost of per-package PR history (the per-package commits remain in `git log`). Either way, merge the remediation for F-01 to F-09 as a **new** PR after the chain lands, not as additional commits on a branch in the middle of it (a mid-chain commit forces every later branch to be rebased, which is exactly the squash failure above). The journal and backlog are owned by the manager and should be merged by it last, if split out.

## 10. Quality gate

* [x] Every package in scope confirmed `VERIFIED` before the review began.
* [x] All five dimensions exercised and evidence stated (§3-§7).
* [x] Full suite and both permanent gates run at `63e6081`; results in §2.
* [x] Every finding has a severity and an owner; none was fixed in-pass.
* [x] Written: this report and the `ROADMAP.md` review entry only.

## 11. Recommendation and next step

No Critical or High findings. Per the skill, the set may advance to `11-release-readiness`, but the nine Medium findings are real: run `07-implementation-planning` to author one remediation package covering F-01, F-03, F-04 (recorder) and F-13, ask `04-requirements-engineering` to settle F-02's scope first, and send the documentation items (F-05 to F-09, F-10, F-11) to their owning skills, ideally as one batch **after** the stack is merged. Re-run this review on the remediation if it changes shipped code.
