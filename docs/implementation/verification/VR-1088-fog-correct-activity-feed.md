# VR-1088 — Verification Report: The Per-Cell Activity Feed Is Filtered at the Session Boundary (FR-6210, FR-6220, FR-4450; M-1)

> **Document ID:** VR-1088
> **Version:** 2.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1088](../packages/IP-1088-fog-correct-activity-feed.md) v1.0
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → IN PROGRESS` return of `IP-1088` (not `VERIFIED`)
> **Feature Mapping:** [FS-106](../../features/FS-106-white-cell-dashboard.md)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

IP-1088, branch `claude/ip-1088-build`, tree `42d029d` (code and fog matrix in `f4f1ccb`), parent `83defa6`. Fresh-session verifier; not the implementing session.

## Result

**RETURNED** — 3 failed checks, all documentation (Medium). The code, the fog behaviour and every test gate pass; 0 code findings.

## Reproduction on the parent, and the fix

Parent `session/cells.py` and `session/inprocess.py` were swapped in from `83defa6` (then restored with `git checkout`). A future White inject (`fire_inject`, T+45 min and T+90 min, one `message` effect each) plus two directly-injected effects (a covert cyber on a Blue asset, an overt jam on a Red asset):

| Read | Parent | Fix |
|---|---|---|
| `/activity/blue` | effect row with template `cyber-secret-payload` + 3 inject rows | one row `cyber → ISR-EO-1 (degrade)`, no template, no inject |
| `/activity/red` | `barrage-X` template row + 3 inject rows | one row `jam → RED-SURF (deny) (attributed)` |
| `/activity/observer` (default designation) | 200, 3 inject rows | equals White |
| `/activity/neutral`, `/activity/bogus` | 200, inject rows | 400 `unknown cell '…'` |

Blue and Red JSON, with `now` normalised, is byte-identical between a session with the White items and one without, at two instants. No `WSECRET` sentinel, template name, opposing-cell id, count of effects or firing time appears in either body. White's feed equals the parent's for the same script (differences are only the few-microsecond wall-clock jitter of `now`). Further refusals: `White`, `WHITE`, `godview`, `observer `, `blue%20`, `neutral` give 400; an empty segment gives 404 (routing). Edit then cancel of two White injects leaves White with the edited time and no ghost; Blue and Red stay empty. After a rewind White still has its injects (2) and Blue/Red 0. Observer designated `blue`, `red`, `godview`, `white` returns exactly that cell's feed (`white`/`godview` equal White); only White may set the designation.

## Fog matrix (own, over the sources `cell_activity` reads)

Kinds enumerated from the code: orders (all states), pending injects (vignette, White-scheduled, edited, cancelled, re-armed after rewind), condition-triggered injects (no row), active effects (Blue-, Red-, neutral-owned, future-start), and the non-sources (gate request/decision, `condition_check`, `env_anomaly_check`, role assignment, SSN, recovery, messages, debris, save/load, `inject_admin`, IP-1083 `schedule`, IP-1084 notices), which are event-log or other-scheduler kinds that the feed does not read. Against the 12 package rows in `test_activity_fog_matrix.py` (12 tests, exact sets) and the own checks above: pass for White, Blue, Red, Observer (both designations), unknown cells.

## Mutation testing

9 of 9 mutations killed by `test_activity_fog_matrix.py`: allow the inject kind through; return the template label; skip the filter for observer; revert to raw scheduler events; accept unknown cells; show a future-start effect; show another cell's effects; show another cell's orders; fail-open on an unknown kind.

## Definition of Done and Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| Reproduction: Blue/Red/`bogus` no inject row, no sentinel; White does | above | pass |
| Matrix rows 1-12 each have a named test, exact sets | `test_activity_fog_matrix.py`, 12 tests | pass |
| Filter in `cells.py`, allow-list by kind, only path for non-White; `inprocess.py` has no per-cell `if` over rows | `CellController.activity_rows`; `inprocess.py` only assembles and calls it | pass |
| Invented kind dropped for a cell | `test_filter_is_fail_closed_on_unknown_kind`; mutation killed | pass |
| Log, scheduler, RNG identical across reads; rewind+advance reproduces feeds | `test_reads_do_not_touch_log_scheduler_rng_and_replay_equals_live`; engine diff empty | pass |
| Determinism and import-guard green; full suite green | below | pass |
| Documentation per Manual impact exists (`10b` §10.15, `02`, `08` row, `WCM-6`, `BLU-2`, `RED-2`, §15.1/§15.2) | see Documentation audit | **fail** |

## Requirements audit

`FR-6210`, `FR-6220`, `FR-4450`, `FR-4410`, `FR-6510`, `FR-1120`: implemented in `cells.py`/`inprocess.py`; tested in `test_activity_fog_matrix.py`; the regenerated RTM Test column equals the tool output (`--origin-report=rtm` run in the worktree leaves no diff). Pass. The activity feed has no requirement leaf (`CR-31`, known, routed upstream).

## Test run (exact commands, real exit codes)

| Command | Result |
|---|---|
| `python3 -m pytest -q --junitxml=…` (unfiltered) | exit 0; 2160 tests, 0 failed, 4 skipped |
| `python3 -m pytest -q -m "not browser"` | exit 0; 2119 tests, 0 failed, 5 skipped |
| `python3 -m pytest -q -m browser` | exit 0; 41 tests, 0 failed, 0 skipped |
| `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`, `test_test_origins.py`, `test_origin_retag.py`, `test_vignette_tutorials.py`, `test_cell_activity.py` (by name) | exit 0 |

The unfiltered and non-browser runs were started concurrently in one worktree; the one-skip difference (4 vs 5) is attributed to that and is not a finding (2119 + 41 = 2160). Own headless-Chromium check (White, Blue, Red, with a pending White inject): the activity panel renders its canvas for all three seats with no page error; the only console error is one 404 on first load for White (a static resource, unrelated to `/activity`).

## Documentation audit

| Item | Exists / accurate | Result |
|---|---|---|
| `10b` §10.15 fog bullets, row 10, `scheduled` row, Sources, cell-refusal line | present and accurate against the shipped feed | pass |
| `10b` §10.15 JSON/effect-label note (package: "the JSON note for effect labels") | not written; the JSON block is unchanged and says nothing about category+symptom labels | fail (Low) |
| `02` Gantt bullets; `08` row 44; `15` §15.1 row and Sources footer | present, accurate; `cells.py` named | pass |
| `12` WCM-6, `13` BLU-2, `14` RED-2 sentences (package: required, a create gap for BLU/RED) | not written (files untouched); no Manual-impact hand-off in the package, the Master Build Plan note, or `docs/pipeline/backlog.md` | **fail (Medium)** |
| Refusal message `unknown cell '<x>'` (HTTP 400) verbatim in `09`/`09a`/reference | `08` says "refused (400)" without the message; `09a` and `09` do not list it (`09a` line 72 still describes an unknown cell as harmless on a different route) | **fail (Medium)** |
| `15` §15.2 reverse row names the BLU-2/RED-2 anchors | `15` §15.1 row updated; the BLU/RED anchors rely on sections that were not written | covered by the WCM/BLU/RED finding |
| Tutorials | `test_vignette_tutorials.py` green | pass |

## Scope audit

Diff `83defa6..42d029d`: `cells.py`, `inprocess.py`, `server.py`, the new test, `CLAUDE.md`, `ROADMAP.md`, MBP, packages INDEX, RTM, and training docs `02`, `08`, `10b`, `15`. All in scope; `engine/` and `app.js` untouched.

## Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| F1 | `WCM-6`, `BLU-2`, `RED-2` sentences promised by Manual impact are not written, and no hand-off item is recorded (none in the package, MBP or backlog) | Medium | `08-training-manual-authoring` (or record the hand-off), via `08-code-implementation` re-run |
| F2 | The new 400 refusal (`unknown cell '<x>'`) appears in no refusal catalogue (`09a`/`09`) or verbatim in the reference | Medium | `08-training-manual-authoring` |
| F3 | `10b` §10.15 effect-label (category + symptom, no template) note not written | Low | `08-training-manual-authoring` |
| O1 | `/activity/white` is open to any request (LAN trust model, same as `/godview`); it is deliberately outside `FR-6220`'s named set. Observation, not a defect | Info | `04-requirements-engineering` (`CR-31`) |

## Next step

Re-run `08-code-implementation` (with `08-training-manual-authoring`) on IP-1088 to write or hand off F1-F3, then re-verify. No code change is needed.

---

## v2.0 — Re-verification (fresh session, 2026-10-31, tree `5b43524` on top of `3c27fc7`)

**Result: RETURNED again** — F2 and F3 are fixed; F1 is fixed for `WCM-6` and `BLU-2` but `RED-2` is inaccurate against the live feed (1 Low/Medium documentation finding, 0 code findings).

| Check | Evidence | Result |
|---|---|---|
| Code diff since `42d029d` | `git diff 42d029d..HEAD -- spacesim/` is empty | pass |
| `WCM-6`: scheduled injects appear on White's timeline only | Live `/activity/{cell}` (session with a White-scheduled inject, a Blue downlink order, a Red jam order, a Blue-asset effect and a Red-asset effect): White shows 2 `inject` rows; Blue and Red show none | pass |
| `BLU-2`: own orders and started effects on own assets, category + symptom only | Blue feed = `electronic_warfare → ISR-EO-1 (deny)` + `ISR-EO-1 downlink`; no template, no Red order, no inject | pass |
| `RED-2`: same for Red | Red feed = `cyber → RED-SURF (deny)` + `JAM-NORTH jam → ISR-EO-1`. The paragraph (`14-red-cell-manual.md` line 39) says the panel "shows only your own orders", but Red's feed also carries started effects on Red's own assets | **fail (Low-Medium)** |
| `09a` / `08` list `unknown cell '<x>'` | `/activity/purple` returns 400 `{"detail":"unknown cell 'purple'"}`; `09a` and `08` carry that text | pass |
| `10b` §10.15 effect-label note | White shows the template label (`jam-spot → ISR-EO-1 (deny)`), Blue/Red show category only (`electronic_warfare → …`, `cyber → …`); the note matches | pass |
| Sources footers / links | `test_doc_integrity.py` and `test_training_sources.py` green | pass |
| Browser | Headless Chromium (`/opt/pw-browsers`), session with a pending White inject: the Timeline panel renders its canvas, no page error. The seat switch in my script did not demonstrably change the seat, so the per-seat content was verified over HTTP, not in the browser | pass (limited) |

Tests, one run by name (`test_doc_integrity`, `test_training*`, `test_test_origins`, `test_origin_retag`, `test_activity_fog_matrix`, `test_determinism`, `test_import_guard`): exit 0, all pass. The full-suite modes were not re-run; I relied on the v1.0 runs (unfiltered 2160/0/4, non-browser 2119/0/5, browser 41/0/0), valid because the code is unchanged.

**MBP tally recount:** 90 package rows; 1 `IN PROGRESS` (`IP-1088`); the other 89 rows carry a `VERIFIED` status. The stated "88 VERIFIED + 1 IN PROGRESS — 90" sums to 89, so the MBP tally line has an off-by-one against its own total (pre-existing; not corrected here).

| # | Finding | Severity | Owner |
|---|---|---|---|
| F4 | `RED-2` says Red's timeline "shows only your own orders"; the live feed also shows started effects on Red's own assets (category + symptom). Add that, mirroring `BLU-2` | Low-Medium | `08-training-manual-authoring` |
| O2 | MBP tally line arithmetic (88 + 1 ≠ 90; recount 89 + 1) | Info | `07-implementation-planning` |

The package header was not edited (verifiers do not edit packages; it stays `READY`/as authored). Next step: fix F4, then a short re-verification.

---

## v3.0 — Re-verification (fresh session, 2026-10-31, tree `14906bb`)

**Result: VERIFIED** — the only open item (F4, `RED-2` wording) is closed; 0 findings.

| Check | Evidence | Result |
|---|---|---|
| Code diff since `42d029d` | `git diff 42d029d..HEAD -- spacesim/` is empty | pass |
| `RED-2` (`14-red-cell-manual.md` line 39) | Now says Red's timeline shows Red's own orders and any effect started on Red's own assets, by category and symptom only; never Blue's orders, effects on Blue's assets, or White's schedule/edits/cancels | pass |
| Live feed, `leo-isr-denial` (seed 1, driven through `InProcessSession.cell_activity`, the `/activity/{cell}` source): Blue `downlink` order, Red `jam` order, one effect on Blue's `ISR-EO-1`, one on Red's `RED-SURF`, two White-scheduled injects | Red: `cyber → RED-SURF (degrade)`, `JAM-NORTH jam → ISR-EO-1` (no template, no Blue order, no Blue-asset effect, no inject). Blue: `electronic_warfare → ISR-EO-1 (degrade)`, `ISR-EO-1 downlink` (no Red order/effect, no inject). White: all of the above with template labels (`BLUE-TPL`, `REDOWN-TPL`) plus both injects | pass |
| `BLU-2` / `WCM-6` | Same run: Blue sees own order + own-asset effect by category only; injects appear on White's feed only. Matches the text of both sections. Code path `CellController.activity_rows` is an allow-list (own-owner orders; own-owner started effects relabelled to category + symptom; every other kind dropped) | pass |
| Tests, one run: `test_doc_integrity`, `test_training_sources`, `test_training*`, `test_test_origins` | exit 0 (all pass, 1 skip) | pass |

**MBP tally (own recount of the package table in `00-master-build-plan.md`):** 90 package rows (90 distinct ids) before this verification = 89 `VERIFIED` + 1 `IN PROGRESS` (`IP-1088`). After: 90 `VERIFIED` + 0 `IN PROGRESS` = 90. The earlier "88 + 1 = 90" line was off by one; the ledger line written this run states the recounted figures.

IP-1088 rows set to `VERIFIED`: verification INDEX, MBP row and tally, packages INDEX, ROADMAP. No `docs/pipeline/` or package/spec edits. The ROADMAP citation is plain text (no new link).
