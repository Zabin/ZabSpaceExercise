# Integration Review — Release Candidate 7 (delta over the RC-3 delta review)

> **Stage:** 10 — Integration Review (fresh session; took no part in implementing or verifying any package in scope)
> **Reviewed commit:** `ad727c3` (branch `claude/integration-review-rc7`, tip = `origin/claude/release-candidate-7`)
> **Date:** 2026-10-31
> **Scope (explicit package list):** `IP-1088` (activity-feed fog fix), `IP-1089` (FR-7450 ISO span bounds), `IP-1092` (retired-documents check), `IP-1093` (lock re-pin), `IP-1094` (`save_format` gate, Chromium lookup), plus the non-package changes merged since the RC-3 delta review (`8833b91..ad727c3`): requirements passes 4 and 5 (`FR-5310` amended, `FR-3520` amended, `FR-7240` added, `FR-6230`/`FR-7450`/`NFR-3810` recorded met), the README refresh, the starter snippets, the save/resume and ISO-bound manual changes, and the training fixes `8de366b`, `e2e1342`, `d86c845`.
> **Headline:** **0 Critical, 0 High, 3 Medium, 5 Low.** The candidate composes. The RC-3 `M-1` fog leak is closed and survives every probe; the five packages hold together; all 19 vignettes survive save/reload with replay equal to live. The Mediums are one stale manual statement that contradicts shipped behaviour and two carried, documented feature gaps. Nothing blocks the release.
> **Previous reviews:** [`integration-review-rc3-delta.md`](integration-review-rc3-delta.md), [`release-assessment-release-candidate-5.md`](release-assessment-release-candidate-5.md) (REV-REL-003).

## 1. Scope confirmation and evidence base

All five packages are `VERIFIED` in their own headers, the Master Build Plan, `packages/INDEX.md` and `ROADMAP.md`, each with a `VR-` file (`VR-1089` v2.0, `VR-1092` v2.0, `VR-1093`, `VR-1094` v2.0, `VR-1088` v3.0). A scripted recount of all 94 packages (header, MBP row, packages index row, ROADMAP row, `VR-` file) found **94 packages, 94 `VR-` files, 94 `VERIFIED`, 0 flagged**.

| Run | Command | Exit | Result |
|---|---|---|---|
| Unfiltered | `python3 -m pytest --junitxml` | see note | 2244 tests, 0 failures, 0 errors, **4 skipped** |
| Non-browser | `-m "not browser"` | 0 | 2202 tests, 0 failures, 0 errors, **5 skipped** |
| Browser | `-m browser` | 0 | 42 tests, 0 failures, **0 skipped** |
| Doc integrity | `test_doc_integrity.py` | 0 | green, also inside a fresh venv built from `requirements.lock` |

Note on the unfiltered run: its first run completed (`--junitxml`: 2244/0/0/4) but the chained exit-code capture was lost to a harness fault, so it was run a second time to obtain a real exit code; the second run's result is in section 8 (`UNFILTERED_RESULT`). The determinism gate and the import guard are inside the unfiltered run and green.

The skip counts equal `CLAUDE.md`'s statement (4 / 5 / 0). **The test totals do not**: `CLAUDE.md` line 19 says 2227 / 2185 / 42; the measured collection is **2244 / 2202 / 42**, +17 tests that arrived with `IP-1089`/`IP-1092`/`IP-1094` after the count was last written (`L-1`).

Probes (real HTTP through `TestClient` over `create_app`, and a real `python3 -m spacesim.ui_web` server in a fresh venv; scripts private to the reviewer):

* **Activity feed fog matrix (`IP-1088`), 19 vignettes.** Per vignette: load, start, three White message injects scheduled at +30/+45/+60 min, one edited (Red-only text), one cancelled, Red doctrine step plus 300 s sim step x4, then a feed read for White, Blue, Red and Observer; rewind to T+5 min, step 600 s, undo; feed read again; `GET /save` then `load_save`, feed read on the reloaded session, White feed of live and reloaded compared; AAR playback started from the Blue, Red and truth viewpoints and the state read scanned for the inject text. Result: **0 violations** at 6 checkpoints x 19 vignettes. A Blue or Red feed contains only `order` rows with `cell == seat` and `effect` rows on assets that seat owns; no row of kind `inject`, no `white-cell` actor, no inject text; the White feed after reload equals the live White feed. Feeds were non-trivial (e.g. `coa-misc-iran-ml`: White 18 / Blue 8 / Red 8 rows; `gnss-ew-campaign`: 10 / 4 / 4). Effect rows read `electronic_warfare -> BLUE-GNSS (deny)` for Blue (category plus symptom, no template name such as `ew_jam`, which White sees). Observer: default designation equals the White feed (injects included), designation `blue` or `red` gives exactly that seat's filtered feed.
* **Time-span exports (`IP-1089`, `FR-7450`).** ISO-8601 (`...+00:00`) and integer bounds on the telemetry CSV export and both ephemeris routes under White, Blue, Red, Observer and no seat. Telemetry export is fog-scoped as before (Blue asking for a Red asset: 404 `no telemetry for this asset (fog/ownership)`; Red asking for Blue: 404; Observer: 404 for both). Cell-observed ephemeris reads only the requesting cell's tracks and returns the documented header-only CSV when it holds none. Hostile bounds all give HTTP 400 naming `t1`: `2030-02-30T00:00:00Z`, `+02:00` offset, no zone, `NaN`, `1e999`, empty string, leap second `23:59:60Z`, an Arabic-Indic digit, a 5,000-digit integer (the CPython limit is caught and named), a 5-digit year; year `0000` is accepted and clamped (partial range, by spec). **The telemetry series read** (`GET /telemetry/{cell}/{asset}/{param}`) takes `t0`/`t1` as integers only (ISO gives 422), as the `FR-7450` Notes state; see `L-2` for the documentation gap.
* **`save_format` gate (`IP-1094`, `FR-7240`).** App-produced saves (advance, undo, rewind, force-added TLE and ground site before start, 19 vignettes saved at the end of the activity probe) reload with `godview` byte-equal to the live session. Hostile `save_format`: `null`, `0`, `1`, `3`, `true`, `false`, `2.0`, `"2"`, `""`, `[]`, `{}`, `-1`, 10^30, `"x"` are all HTTP 400 `save_format ... is not supported; supported formats: legacy (absent), 2`; `2` loads; an absent key reloads as a legacy save with the legacy warning; the format gate answers before the other `validate_save` checks (a save with `save_format: 7` and `seed: "x"` reports the format), and the other checks still fire (missing `content`, boolean `seed`, string `eventlog`: 400 each).
* **Retired-documents check (`IP-1092`, `NFR-3810`) on the real tree.** `retired_declarations()` and `retired_findings()` on the repository: 0 declarations, 0 problems, 0 findings; `doc_integrity_allow_retired.txt` is header-only. The check is green but **vacuous on the real tree** — no `Retired documents` section exists in any index because no document has ever been retired; it is exercised by its synthetic-tree tests (`L-4`).
* **Seat rules derived from the live route table** (42 mutating routes, derived with `inspect` over `app.routes`; body synthesised from each request model; each called as white, blue, red, observer, a bogus seat and no seat). Every White control (clock, param, start, step, advance, rewind, undo, inject and its pending admin routes, red_step, force routes, creator routes, roles/assign, observer/view, save_vignette, load_save, aar/playback/*) is 403 to blue, red, observer, a bogus seat and no seat. Observer is 403 on **every** mutating route including the path-cell routes (`/recovery/observer/...`, `/ssn/observer/...`) once the path carries `observer`. Session create/draft intentionally accept bogus/no seat and refuse player seats (`_refuse_player_seat_on_create`). `/gate/decide` and `/roe/change` still answer 200 `{"ok": false, "reason": "not_controller"}` to non-White (carried RC-3 `L-1`).
* **Non-finite sweep.** Every mutating route x 3 seats x every required body field x 10 hostile JSON values (`NaN`, `Infinity`, `-Infinity`, `1e999`, `1e308`, 2^53+1, `null`, `[]`, `{}`, `""`) = **4,950 requests, 0 responses of 5xx.**
* **README, installed exactly as written.** A clean `git archive` of `HEAD`, `python3 -m venv .venv`, `pip install -r requirements.lock && pip install --no-deps -e .` (CPython 3.13.17): installs clean, `pip check` reports no broken requirements, `python3 -m spacesim.ui_web` serves on 127.0.0.1:8000 (`/` 200, `/api/vignettes` returns 19, `POST /api/sessions` creates a session), and `determinism`, `import_guard` and `doc_integrity` pass inside that venv with the locked versions (fastapi 0.162.0, numpy 2.5.4, pydantic 2.14.2, skyfield 1.55, sgp4 2.27, uvicorn 0.54.0). The README's trust-model text (no authentication; the seat is whatever the request says; anyone reaching the port can act as White or read ground truth; loopback or isolated LAN only; no `--reload` for a shared session) matches `CLAUDE.md`'s trust model and the behaviour measured above.
* **Starter snippets.** The six snippets in `12b` (imaging satellite, ground station, jammer and interceptor, ground radar, objectives, timed inject) were extracted programmatically from the manual and assembled into one external vignette: it appears in `/api/vignettes`, loads, starts, steps 600 s and serves `scene/blue` with HTTP 200.
* **Chromium lookup (`IP-1094`).** `tools/record_walkthrough.py::find_chromium()` and `.claude/skills/run-spacesim/driver.py::find_chromium()` both return `/opt/pw-browsers/chromium-1243/chrome-linux64/chrome` (numeric newest-build sort, VR-1094 F2 closed).

## 2. Package-by-package result

| Package | Result | Notes |
|---|---|---|
| `IP-1088` | **Holds** | The fail-closed allow-list in `CellController.activity_rows` is the only filter; the feed read resolves `observer` through its designation and refuses any other seat name. RC-3 `M-1` is closed (section 4). |
| `IP-1089` | Holds | One parser (`span_bounds.parse_span_bound`) at the session boundary; the three export routes agree on every hostile input; the series read is deliberately outside it. |
| `IP-1092` | Holds, vacuously on this tree | See probe; failure modes (a)/(b)/(c) are covered by synthetic tests, not by any real declaration. |
| `IP-1093` | Holds | The lock installs, passes `pip check`, and the gates pass on it. |
| `IP-1094` | Holds | Gate and both Chromium lookups probed. |

## 3. Findings

| Finding | Packages/artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|
| M-1 | `docs/training/10b-ui-reference-views.md` row 7 and the `executed` status row (lines 160 and 173), `BL-0272` (`IP-1065`, `BL-0266`), `inprocess.py::cell_activity` | The Gantt reference still says an `executed` status "is never sent" and that a past order's bar "still draws as **queued**". Since `IP-1065` the feed derives `executed` for a queued order whose window has passed. The manual contradicts the shipped behaviour. The Manual-impact item `BL-0272` has been `SCHEDULED` since 2026-10-17 and has crossed three release candidates; its other sub-items (`10` Save as scenario, `01` External groups) are present in the manuals, so this is the one remaining stale statement. | Medium | `08-training-manual-authoring` (then `09-training-manual-review`) |
| M-2 | Save-as-scenario x `IP-1062`/`1270`/`1290`/`1230` (carried: RC-3 `M-3`, `BL-0389`) | `vignette_export.py` still carries no `effect_gating_rules`, `effect_detectability_config`, space-weather series, environmental-anomaly rate or inject schedule (no change to the file since RC-3). Documented as a v1.1 item in `12b`/`12d`; deferred in the backlog. | Medium (known deviation) | `07-implementation-planning`, or owner acceptance |
| M-3 | `IP-1270`, `IP-1250`, `static/app.js` (carried: RC-3 `M-4`) | The console still has no caller of `/gate/decide`, `/roe/change` or the manoeuvre ledger (`app.js`: 0 matches). Documented "HTTP only" in `12`/`12c`/`12d`. | Medium (known deviation) | `07-implementation-planning`, or owner acceptance |
| L-1 | `CLAUDE.md` line 19 | The status line says 2227 / 2185 / 42 tests; measured 2244 / 2202 / 42 (skip counts 4 / 5 / 0 are right). | Low | `08-code-implementation` doc step / `11-release-readiness` flip |
| L-2 | `docs/training/08-http-api-reference.md` line 54, `GET /telemetry/{cell}/{asset}/{param}` | The series read takes `t0` (start) and `t1` (end) as **integer microseconds only** and is not listed with its parameters; on the export routes `t1` is the **start** and `t2` the end, and they accept ISO. Same name, different meaning on two sibling routes, and the reference documents only the export form. The behaviour is as specified (`FR-7450` Notes exclude the series read). | Low | `08-training-manual-authoring` |
| L-3 | `POST /observer/view`, `inprocess.set_observer_view` | The designation is stored unvalidated: `"x"` returns `{"ok": true}`, after which `/activity/observer` is HTTP 400 and `GET /observer/view` returns 200 with no usable view. White-only and self-inflicted; `designation: "white"` is also accepted. | Low | `07` |
| L-4 | `IP-1092` check on the real tree | 0 `Retired documents` sections exist, so the check cannot fail on this tree today; its value rests on the synthetic tests. | Low (informational) | none; owner awareness |
| L-5 | Carried RC-3 Lows, untouched in this delta | `L-1` gate/ROE 200 `not_controller`; `L-2` `mt-*` `estimated_duration_min` 30/30/45 against deadlines of 90/60/60 min; `L-4` stale-epoch TLE accepted without a warning; `L-5` `POST /param` accepts an enum value outside `options` (`safe_mode_recovery_difficulty: "bogus"` gives `ok: true`, re-probed); `L-6` carried RC-1/unreviewed Lows (live-log bound, SSN reset on rewind, `--origin-report` exit 5, two allow-list formats). | Low | `07` / `08-vignette-development` |

## 4. Closure of earlier findings

### 4.1 `integration-review-rc3-delta.md`

| Finding | State | Evidence |
|---|---|---|
| M-1 activity read shows White's scheduled injects to Blue/Red | **Closed** | `IP-1088`: 0 violations over 19 vignettes x 6 checkpoints x 4 seats incl. edit, cancel, rewind, undo, save/reload, playback viewpoints (section 1); inject text absent from every Blue/Red/playback body; `FR-6230` records the rule. |
| M-2 `FR-3520` says execution time, gate is submission time | **Closed as an accepted deviation** | `FR-3520` amended (`CHG-047`), `FS-116` v1.3 states submission-time with accepted limitations (omitting `seat` skips the gate), owner decision on `BL-0388` recorded. Behaviour unchanged and documented. |
| M-3 save-as-scenario drops rules | **Open (known deviation)** | Here `M-2`. |
| M-4 no console control for gates/ROE/ledger | **Open (known deviation)** | Here `M-3`. |
| L-1 .. L-9 | Open, unchanged | `L-1`..`L-7` carried in `L-5`; `L-8`/`L-9`: the Manual-impact rows `BL-0271`, `0272`, `0276`, `0283`, `0286` are still `SCHEDULED`/`DEFERRED` in the backlog although four of five are visibly worked into the manuals (`BL-0271` by `cd7bdcd`); `BL-0272` is not fully worked (`M-1`). |

### 4.2 `release-assessment-release-candidate-5.md` (REV-REL-003)

| Item | State | Evidence |
|---|---|---|
| B-1 `IP-1088` inside no integration review | **Closed by this review** | Sections 1-3: `IP-1088` reviewed with real probes, no Critical/High. |
| B-2 learner-walkthrough gate not current (three commits) plus open Manual-impact item | **Partly closed here, owner-visible** | The three commits (`8de366b`, `e2e1342`, `d86c845`) are inside the green tutorial machine checks (`test_vignette_tutorials.py`) and the starter snippets were re-driven; an independent `09-training-manual-review` of them is not on file in `docs/reviews/` (not performed by this stage). Open Manual-impact items: `BL-0271` worked (`cd7bdcd`), `BL-0272` has one stale statement (`M-1`). |
| B-3 `FR-7450`, `FR-5310` clause, `NFR-3810` unbuilt | **Closed by delivery** | `FR-7450` built (`IP-1089`, probed); `NFR-3810` built (`IP-1092`, vacuous on the real tree, `L-4`); `FR-5310`'s template clause amended out (inline authoring, `FS-131` v1.2, `12b` says "no template references or includes") and the starter snippets load. |
| M-2/M-3/M-4 known deviations | Unchanged (here `M-2`, `M-3`; `FR-3520` accepted) | See 4.1. |
| D-1 `FEAT-3500` dormant: no shipped vignette declares `roles_needed` | **Still true** | 0 of 19 vignettes declare it (owner decision O-2 still pending). |
| S-3 lock re-pin | **Closed** | `IP-1093`; fresh-venv install and gates pass. |
| N4 README | **Closed** | README refreshed (`f5d1f3c`); install-as-written probe passes, trust-model text accurate. |
| V-1 `VR-1088` header stale | **Closed** | All 94 headers read `VERIFIED`. |

## 5. Documentation coherence

* **Counts.** 94 packages / 94 `VR-` files / 94 `VERIFIED` across headers, MBP, `packages/INDEX.md` and `ROADMAP.md` (scripted); the MBP final tally line reads `94 VERIFIED, 0 COMPLETE, 0 READY, 0 BLOCKED`. `CLAUDE.md` test totals are stale (`L-1`).
* **Feature to manual (scripted).** Of 38 `FS-` documents, 37 have a row in `15-manual-traceability.md` §15.1/§15.1a naming at least one manual section; `FS-133`/`134`/`135` carry the explicit reason "not operator-visible (test / CI tooling)"; `FS-202` has no row because it has no package (excluded in the build plan). No VERIFIED FS lacks both a section and a reason.
* **Manual coverage of the scope.** Activity-feed fog is in `08` (API reference, line 44) and the fog text of the cell manuals; ISO bounds in `08` (lines 108-137), the manuals and the glossary; the `save_format` refusal in `WCM-22`, `09a` and §15.1; README and starter snippets in `12b`; `CLAUDE.md` code map carries `IP-1088`, `IP-1089` (`span_bounds.py`) and `IP-1094`.
* **Open Manual-impact items for the scope:** `BL-0271` (worked), `BL-0272` (one stale statement, `M-1`), `BL-0276`, `BL-0283`, `BL-0286` (sections present: Red rounds in `14`, `WCM-25` space weather, pending injects in `12c`/`12d`, controller-view compare in `12`/`10`); the backlog dispositions are bookkeeping behind the manuals and need a `09-training-manual-review` to close.
* **Tutorials.** All tutorial and playbook checks run in the green suite.
* **Dependency lock.** `requirements.lock` re-pinned (`IP-1093`) and verified by fresh install.

## 6. Invariants

Determinism gate and import guard: green in the unfiltered run and again in the lock venv. Fog-of-war at the boundary: held by `activity_rows` (fail-closed by kind) and by the fog on `telemetry/export` and the cell ephemeris. No new wall-clock or global RNG read in `engine/`. Observer mutation-rejection held on all 42 mutating routes. Seat model: client-asserted, as documented.

## 7. Recommendation for the release assessment

**GO.** No Critical or High finding. The release-assessment blockers `B-1` (this review) and `B-3` (delivery) are cleared. `B-2` is a process condition: the owner should either order the `09-training-manual-review` delta over `8de366b`/`e2e1342`/`d86c845` and the starter snippets, or record the deferral. Before tagging, fix or accept `M-1` (one stale manual statement), correct the `CLAUDE.md` totals (`L-1`), and record owner decisions on `M-2`/`M-3` (documented v1.1 gaps) and `O-2` (dormant role scoping).

**Next step.** `11-release-readiness`, with `08-training-manual-authoring` queued for `M-1`/`L-2`.

## 8. Final suite record

* Unfiltered second run (real exit code): `UNFILTERED_RESULT`.
