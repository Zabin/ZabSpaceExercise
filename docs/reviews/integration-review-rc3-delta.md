# Integration Review — Release Candidate 3 (delta over the three earlier reviews)

> **Stage:** 10 — Integration Review (fresh session; took no part in implementing or verifying any package in scope)
> **Reviewed commit:** `8833b91` (branch `claude/integration-review-rc3`, tip = `claude/release-candidate-3`)
> **Date:** 2026-10-30
> **Scope (explicit package list):** `IP-1082`, `IP-1083`, `IP-1084`, `IP-1085`, `IP-1086`, `IP-1087`, `IP-1160`, plus the non-package changes merged with them: the vignette YAML scenario changes (16 files, `claude/release-candidate-1..HEAD`), the new tutorial/playbook machine checks, manual and traceability changes, requirements passes 1-3, and the dependency lock.
> **Headline:** **0 Critical, 0 High, 4 Medium, 9 Low.** The candidate composes. All 19 vignettes load, run to the end and survive save/reload with byte-equal replay; no mutating route returns 5xx for any non-finite or malformed number; the seven packages hold under combined probes. The Mediums are one new fog leak (cell activity read shows White's scheduled injects), one requirement/implementation divergence the owner has not decided, and two older Mediums that are still open.
> **Previous reviews:** [`integration-review-release-candidate-1.md`](integration-review-release-candidate-1.md), [`integration-review-unreviewed-packages.md`](integration-review-unreviewed-packages.md), [`integration-review-tranche-3-release-push-remediation.md`](integration-review-tranche-3-release-push-remediation.md)

## 1. Scope confirmation and evidence base

All seven packages are `VERIFIED` in the Master Build Plan, `packages/INDEX.md` and their own headers, and each has a `VR-` file. The ledger recount gives **89 packages, 89 `VR-` files, 89 `VERIFIED`** (the MBP status column spells it six ways, `✅`, `🟢`, plain, dated, so a plain `grep -c "✅ VERIFIED"` returns 81; the status text of the other eight rows is `VERIFIED`).

| Run | Command | Exit | Result |
|---|---|---|---|
| Unfiltered | `python3 -m pytest --junitxml` | 0 | 2144 tests, 0 failures, 0 errors, **3 skipped** |
| Non-browser | `-m "not browser"` | 0 | 2103 tests, 0 failures, **4 skipped** |
| Browser | `-m browser` | 0 | 41 tests, 0 failures, **0 skipped** |
| Doc integrity | `test_doc_integrity.py` | 0 | 9 passed (re-run after this report was added) |
| Origin report | `--origin-report` | **5** | untagged tests 0; exit 5 is the open RC1 `L-3` |

The numbers equal `CLAUDE.md` line 19 exactly (2141 passed / 3 skipped; 2103 / 4; 41 / 0). The determinism gate and the import guard are inside the unfiltered run and green. Allow-lists: `doc_integrity_allow_links.txt` 40 lines, `doc_integrity_allow_indexes.txt` and `_ledgers.txt` 1 each (header only), `test_origin_allowlist.txt` 2 (header only) — all shrink-only and no entry is a delta defect.

Probes (real HTTP through `TestClient` over `create_app`, scripts private to the reviewer):

* **19-vignette playthrough, RC3 and RC1 side by side.** Load, `start`, Red doctrine step plus 300 s sim steps to the vignette's duration, save/`load_save` at thirds, compare `godview` and both cells' `scene` between live and reloaded. RC3: 19/19 load, 0 step errors, **57/57 checkpoints replay-equal**. RC1: same.
* **Non-finite sweep.** Every mutating route in the live table (39) x 4 seats x every request field x 11 hostile values (`NaN`, `Infinity`, `1e999`, `1e308`, 2^53+1, `null`, `[]`, `{}`, `""`): **0 responses of 5xx**. A second sweep of nested fields (order params, inject effects, scripted manoeuvre, space-weather series, force/ground, ROE, SSN, playback, rewind/undo) and non-finite query values on 9 GET routes: 0 of 5xx.
* **Seat rules derived from the route table** (`inspect` of each endpoint plus a call as blue, red, observer, a bogus seat and no seat): every White control is 403 to every non-White seat, Observer is 403 on every mutating route, `injects/*` and `aar/playback/*` are 403 (viewpoint reaches `no_playback_session` for a participant, as documented). Exceptions are in `L-1`.
* **Interplay (role gate x gating rule x pending rebuild x rewind/undo x inject re-arm x save).** An external vignette (`roles_needed` + `effect_gating_rules`) was loaded: start is refused until a seat is staffed; a `bus` seat issuing a payload verb is `role_scope_out_of_scope`; a Red jam is `pending_approval`; save and `load_save` keep it pending (`IP-1087`); Blue, Red `not_controller`, Observer 403, White approves; the reloaded session replays equal to the live one; a rewind on the resumed session drops the order and a later decide is `no_such_pending_order`; two White-scheduled injects survive rewind and re-arm, fire once each on replay, and an undo re-arms the last fired one (`IP-1083`); out-of-range rewind targets are 400.
* **Clock bounds.** `running: true` with rate 0, -1, 10001, 1e308 is HTTP 400 with the reason, 10000 accepted; the manual (`12d`) states the same bounds.
* **Fog (`IP-1084`).** A controller `anomaly` on `ISR-EO-1` and a `sensor_outage` on `BLUE-RADAR`: Blue gets two messages with the cause, Red gets none and no alarm. A `telemetry` anomaly on a bus-less asset is refused whole (400).
* **Cell-scoped reads at T+2 min on all 19 vignettes** (21 `{cell}` GET routes): no other-cell asset id appears in any Red/Blue read except the authored `intro_brief` prose (by design).
* **Stale and unphysical authoring (`IP-1086`).** A 2024-epoch ISS TLE force-added into a 2030 vignette is accepted (`ok: true`) and the session then starts, steps and serves every scene, window and contact read with 200 (the read path is robust). A Creator asset with `e: 1.5` is refused in the response (`orbit.e must satisfy 0 <= e < 1`).

## 2. Package-by-package result

| Package | Result | Notes |
|---|---|---|
| `IP-1082` | Holds | Non-finite sweep clean; clock bounds 400; the manual states the bounds and the toolbar refusal text. |
| `IP-1083` | Holds | See interplay probe; replay of a rewound-then-re-fired inject equals live. |
| `IP-1084` | Holds | Fog probe above. A related read is not fixed, see `M-1`. |
| `IP-1085` | Holds on the evidence of `VR-1085` and the suite (unreviewed-packages `H-2` is closed); not re-reproduced in this pass. |
| `IP-1086` | Holds (partial: see `L-4`) | Unphysical elements refused; the Creator-save half is covered by `test_authoring_boundary_validation.py` (674 lines), not re-driven here because no `user_save_dir` is configured in the sandbox. |
| `IP-1087` | Holds | Interplay probe. `gate_lost_on_resume` is in the Blue, Red and White manuals. |
| `IP-1160` | Holds, with the two known deviations (`M-2`) | `roles/scope` is fog-correct per `VR-1160`; scope/binding refusal codes are in `09a`, `10a`, `12c`, `13a`. |

## 3. Findings

| Finding | Packages/artifacts involved | Description | Severity | Recommended owner |
|---|---|---|---|---|
| M-1 | `GET /activity/{cell}` (`session/inprocess.py` ~line 700), `IP-1066`/`IP-1083`, `FR-6220`, `IP-1084` | The activity (Gantt) read is cell-scoped but its scheduled-inject branch keeps every event whose actor is `white` for **every** cell (`ev_cell not in (cell, "white")`). Reproduced on `leo-isr-denial`: Blue and Red both receive `{kind: inject, status: scheduled, start: T+45 min, label: "inject (2 effects)"}`, and White-scheduled injects (`white-<n>`) show the same way. The cell learns that an inject exists, when it fires and how many effects it has. `FR-6220`'s acceptance criterion says no interface outside the named no-cell set bypasses cell filtering, and the named set does not include this route. The branch pre-dates this scope (present in RC1) but `IP-1066`/`IP-1083` made White-scheduled injects a first-class feature, and `IP-1084` closed the sibling leak. | Medium | `07` (remediation package), then `08` |
| M-2 | `IP-1160` (`VR-1160` `M-3`, `L-1`), `FR-3520`, `FS-116` | The role scope is checked at **submission**; `FR-3520` and `FS-116` still say "at command-execution time", and a rebinding applies only to later submissions. Omitting `seat` skips the gate. Both are the verifier's owner-decision items; no decision is recorded in the requirements baseline, so the requirement text and the shipped behavior disagree and the claimed enforcement is advisory against a client that omits `seat` (LAN trust). | Medium | project owner, then `04` (amend or build) |
| M-3 | `IP-1200`/`vignette_export.py` x `IP-1062`/`1270`/`1290`/`1230` (carried: unreviewed-packages `M-4`) | Save-as-scenario still does not carry `effect_gating_rules`, `effect_detectability_config`, the space-weather series or environmental-anomaly rate, or the vignette's inject schedule (`vignette_export.py` has no reference to any of them). The saved file is not a faithful continuation. Unchanged by any commit in this delta. | Medium | `07` then `08` (or owner defers) |
| M-4 | `IP-1270`, `IP-1250`, `static/app.js` (carried: unreviewed-packages `M-5`) | The console has no control for approve/deny of a gated order, the live ROE change, or the manoeuvre ledger (`app.js` has no caller of `/gate/decide`, `/roe/change` or a ledger route). The manuals say so plainly ("HTTP only") so this is documented, not hidden, but `FS-127`/`FS-125` list the console half. | Medium | `07` then `08`, or owner descopes in `FS-125`/`FS-127` |
| L-1 | `/gate/decide`, `/roe/change` (carried unreviewed `L-1`) | A Blue/Red/unknown seat gets HTTP 200 `{"ok": false, "reason": "not_controller"}`, not the 403 every other White control returns. No state changes. Documented in `12c`. | Low | `07` |
| L-2 | `mt-isr-sar`, `mt-weather-collect`, `mt-sigint-geolocate` YAML; `app.js` brief chip | The deadlines were extended (T+90, T+60, T+60 min) but `estimated_duration_min` stayed 30, 30, 45, so the mission brief's "Duration: ~30 min" contradicts its own deadline note (`sda-custody-hunt` 60 vs 90 is older). The engine horizon is 4x the label so nothing breaks. | Low | `08-vignette-development` |
| L-3 | `mt-weather-collect`, `nv-isl-relay-debris` (new Red sensors) | Red's only objective (`track_blue`, custody >= 0.5 on `WX-1` / `ISR-A`) is now attainable by the Red AI (it flipped false to true against RC1 in the Red-AI-plus-passive-Blue baseline) and Blue has no tool against a passive tracker. It is intended and documented ("you cannot interfere"), but the cell has no contest. `coa-russia-md`, `coa-china-md` and `coa-china-ml` outcomes are unchanged from RC1; `coa-misc-iran-ml` Red `deny_pnt` is true against a passive Blue (expected). No vignette became a trivial Red win against a playing Blue. | Low | `08-vignette-development` (decide whether the watcher is a contest) |
| L-4 | `IP-1086`, `POST /force/tle` | A stale-epoch TLE is still accepted with `ok: true` and no warning; only the read path was hardened. A facilitator learns of the stale orbit by an odd track, not by a message. | Low | `07` |
| L-5 | `POST /param` | An enum value outside the declared `options` is accepted before start (`safe_mode_recovery_difficulty: "bogus"` -> `ok: true`); the new parameter is read by `manager.py` with no check. Downstream effect not traced. | Low | `07` |
| L-6 | Carried Lows still open (re-checked or untouched by any commit in the delta) | unreviewed `L-4` (`/api/vignettes` returns absolute `path`), `L-5` (`bulk_import` after start: 200 `[]`; a 6,000-object file accepted), `L-6` (SSN registry reset on rewind), `L-7` (RIC picker default), `L-8` (scripted manoeuvre absent from the ledger), `L-9` (no shipped vignette uses `roe`, gating, detectability, space-weather or condition triggers - re-grepped: still none); RC1 `L-1` (unbounded live log), `L-2` (playback cursor after rewind), `L-3` (`--origin-report` exit 5, re-run), `L-5`, `L-6` (clock after rewind, owner question). | Low | as originally routed |
| L-7 | `CLAUDE.md` code map (carried unreviewed `L-2`) | Counts are right but the code map has no text for `IP-1052`, `IP-1041`, `IP-1061`, `IP-1064`, `IP-1065`, `IP-1131`, `IP-1223`. | Low | `08-code-implementation` doc step |
| L-8 | `VR-1082/1083/1085/1086/1087/1160` | Only `VR-1084` has a "Documentation audit" section. The content is in the manuals (see section 4), so this is a process gap, not an uncovered change. | Low | `09-package-verification` |
| L-9 | `docs/pipeline/backlog.md` `BL-0271`, `0272`, `0276`, `0283`, `0286` | Five Manual-impact rows are still `SCHEDULED`. Spot-check finds the sections present (Compare panel, missed-salvo/rounds in Red, space-weather in White), but no `09-training-manual-review` on file says so. | Low | `09-training-manual-review` |

## 4. Closure of earlier findings

### 4.1 `integration-review-unreviewed-packages.md`

| Finding | State | Evidence |
|---|---|---|
| H-1 anomaly/outage broadcast with true cause | **Closed** | Fog probe: Blue sees both with cause, Red sees nothing (`IP-1084`). |
| H-2 uplink jam fails stored-program/ISL commands | **Closed** | `IP-1085` verified (`VR-1085`) and in the green suite; not re-reproduced. |
| H-3 stale TLE poisons the scene | **Closed** (residual `L-4`) | Stale ISS TLE: start, step, scene, windows, next_contacts, alarms, conjunctions all 200. |
| M-1 unphysical elements | **Closed** | Creator `e: 1.5` refused. |
| M-2 pending order lost on resume | **Closed** | Interplay probe (`IP-1087`). |
| M-3 Creator saves unloadable files | **Closed (by suite)** | `test_authoring_boundary_validation.py`; not re-driven. |
| M-4 save-as-scenario drops rules | **Open** | `M-3` above. |
| M-5 console half missing | **Open** | `M-4` above (documented). |
| M-6 no manual sections | **Closed** | `12c`, `12d`, `13a`, `14a`, `09a`, `10a`, §15.1 rows for gates, ROE, roles, clock. |
| L-1 seat rule non-uniform | **Open** | `L-1`. |
| L-2 CLAUDE.md stale | **Open (residual)** | Counts fixed; code map gap `L-7`. |
| L-3 header drift | **Closed** | All 89 headers read `VERIFIED`. |
| L-4 .. L-9 | **Open** | `L-6`. |

### 4.2 `integration-review-release-candidate-1.md`

| Finding | State | Evidence |
|---|---|---|
| M-1 NaN/clock-rate 500 | **Closed** | 0 of 5xx over the sweeps; rate bounds 400. |
| M-2 toolbar throws at span end | **Closed** | Browser suite 41/0, `IP-1082`. |
| M-3 CLAUDE.md code map omits four packages | **Closed** | `_span_ceiling`/366, `IP-1077`, `IP-1081`, `IP-1103` all present. |
| L-1 unbounded live log | **Open** | 300 injects accepted. |
| L-2 playback cursor after rewind | **Open** | `aar.py` unchanged since RC1. |
| L-3 `--origin-report` exit 5 | **Open** | Re-run: exit 5. |
| L-4 residual stale statements | **Closed** | "browser GUI unverified" gone; ROADMAP header says the build spec "wins nowhere". |
| L-5 two parsers/allow-list formats | **Open** | Files unchanged. |
| L-6 rewind leaves clock running | **Open** | Owner question. |

## 5. Documentation coherence

* **Counts.** `CLAUDE.md` status line equals the measured runs. 89 packages / 89 VRs / 89 `VERIFIED`. Matrix: every `FS-` document is named in `15-manual-traceability.md` except `FS-202`, which has no package.
* **Manual coverage of the scope.** Rate bounds (`08`, `09a`, `12d`), non-finite refusals (`12d`), inject survival on rewind (`12c` item 4), `gate_lost_on_resume` (`12c`, `13a`, `14a`), role refusals (`09`, `09a`, `10a`, `12c`, `13a`), `unstaffed mandatory role(s)` (`09a`, `12c`). The new `safe_mode_recovery_difficulty` parameter appears in `04` but the dial is not described in the White parameter reference.
* **Open Manual-impact items:** `BL-0271`, `0272`, `0276`, `0283`, `0286` (see `L-9`).
* **Tutorials.** The new machine checks and all tutorials run inside the green suite.
* **Dependency lock.** `requirements.lock` (38 lines) is unchanged since RC1.

## 6. Recommendation for the release assessment

**GO, conditional.** No Critical or High finding; every gate is green and the counts reconcile. Before tagging, the owner should either schedule or consciously defer `M-1` (the one new fog leak: timing and count of White's scheduled injects visible to Red and Blue), and record a decision on `M-2` so `FR-3520` and the shipped behavior agree. `M-3`/`M-4` are known, documented gaps that can ship as v1.1 items listed in the release notes. Lows are routed as in section 3.

**Next step.** `11-release-readiness`, with `07-implementation-planning` queued for `M-1`.
