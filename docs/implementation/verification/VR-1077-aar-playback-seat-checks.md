# VR-1077 — Verification Report: AAR Playback Seat Checks (FR-7340, FR-4320, FR-6210)

> **Document ID:** VR-1077
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1077](../packages/IP-1077-aar-playback-seat-checks.md) v1.0,
> [FS-107](../../features/FS-107-after-action-review.md)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1077` (closes tranche 3 review `L-4`, `VR-1072` F3)
> **Feature Mapping:** FS-107

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1077 — AAR Playback Obeys the Requesting Seat (v1.0)
- **Implementing commit:** `1ca9e4f` (branch `claude/ip-1077-build`); parent `0f307a8`.
- **Independence:** fresh session; did not implement this package.

## Result

**✅ VERIFIED** — 0 failed checks; 3 Low findings, none blocking.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Tests 1-12 exist, seen failing first, pass | `test_aar_playback_seats.py` (14 collected). With the parent `inprocess.py`/`server.py` restored, 11 of 14 fail (ImportError on the pure rule, 200 where 403 required); the 3 that pass are White-succeeds, refused-untouched (log only) and the matrix-shape case. Restored afterwards | pass (Low F1, F2) |
| No route answers a player with another viewpoint's state; a refused request changes nothing | Real-HTTP matrix below; `/eventlog` and White's playback state identical before and after every refused call | pass |
| Interfaces matrix is what the code does, pinned by a test | `playback_seat_decision` (`inprocess.py:25-49`); `test_pure_check_matches_documented_matrix` covers 6 seats x all actions; HTTP matrix agrees | pass |
| Existing playback tests pass with `cell=white`, no assertion weakened | `test_web.py` diff: two lines, only `?cell=white` added (the third playback test already named it) | pass |
| Suite, gates, doc integrity, test origins green; RTM regenerated | See Test run | pass |
| Docs updated; MBP row `COMPLETE` | CLAUDE.md `ui_web` bullet, `docs/training/08-http-api-reference.md`, MBP, packages index, ROADMAP, RTM, FS-107 Referenced By. Gap: F3 | pass (Low) |

## Verification Checklist audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Reproduce the pre-fix disclosure on the parent and see it gone | Parent files: the Red-state, Observer-mutation, no-seat and viewpoint tests fail; fixed tree: Red `state` on a `truth` playback is 403 with no `assets`/`tracks` | pass |
| 2 | Every new test names its origin | Module `pytestmark` `FR-7340`; one `IP-1077`; `test_test_origins.py` green | pass |
| 3 | `spacesim/engine/` and `session/aar.py` unchanged; import guard green | `git diff 0f307a8 HEAD -- spacesim/engine spacesim/session/aar.py` is empty; `test_import_guard.py` green | pass |
| 4 | Determinism green | `test_determinism.py` green | pass |
| 5 | Every playback route accepts `cell`, refuses per the matrix | Routes found by source: start, advance, state, viewpoint, speed (5); all take `cell`; HTTP matrix below; a per-route mutation (seat forced to `white`) is caught for each | pass |
| 6 | Three `test_web.py` edits add only `cell=white` | Only two lines needed editing; both add only `?cell=white` | pass |
| 7 | Locking: check and act under one acquisition; no lock-order issue | Each `playback_*` runs check+act inside one `with self._locked(session)` (`mgr._lock`, an RLock; `_locked` does not call `catch_up`, unlike `_locked_read`). Concurrent smoke test below: no deadlock, no 5xx | pass |
| 8 | doc integrity, test origins green; RTM regenerated; no allow-list grew | Run; `--origin-report=rtm` prints "unchanged" (Test column equals tool output); no `*allow*` file in the diff | pass |
| 9 | Collected count below `COLLECTED_UPPER` (1700) | **1671 collected** (1641 not-browser + 30 browser); headroom 29 | pass |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| FR-7340 | `inprocess.py::playback_seat_decision` and the five `playback_*`; `server.py` routes + `_playback_ack` | `test_aar_playback_seats.py` | regenerated, Test entries present | pass |
| FR-4320 | same query-seat convention | no/unknown-seat cases | regenerated | pass |
| FR-6210 | player seat never receives another viewpoint's state | state-read and HTTP probes | regenerated | pass |
| FR-7330 | permitted behaviour unchanged | `test_web.py` playback tests, switch-continues case | unchanged | pass |

## Test run

- `python3 -m pytest -m "not browser" --junitxml` — exit 0; **1641 tests, 0 failures, 0 errors, 6 skipped**.
- `python3 -m pytest -m browser --junitxml` — exit 0; **30 passed, 0 skipped** (Chromium ran).
- Collected: 1671 (headroom 29 under `COLLECTED_UPPER` 1700).
- Gates by name, run together with the new module: `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`, `test_test_origins.py`, `test_aar_playback_seats.py` — exit 0.
- `python3 -m pytest --origin-report=rtm` — "unchanged".

### Behavioural probes (live uvicorn, httpx; leo-isr-denial, 05-da-asat-crisis, 08-multi-domain-taiwan)

| Case | Result |
|---|---|
| `start` by white (truth/blue/red) | 200 each |
| `start` by blue/red | 200 only for own cell; 403 for the other two |
| `start` by observer, no seat, `garbage` seat | 403 for every viewpoint |
| `state` with viewpoint truth: white / observer / blue / red / none / garbage | 200 / 200 / 403 / 403 / 403 / 403 (body truth-shaped only for white and observer) |
| `state` with viewpoint blue (red): white, observer, owner | 200; other player 403; none and garbage 403 |
| `viewpoint` by each seat to each viewpoint | White 200 for all; a player 200 only to its own; everything else 403; after each refusal the playback viewpoint was unchanged (read back as White) |
| Before any playback: advance / speed / viewpoint(blue) / state | white 404 / 200 `ok: false` / 200 `ok: false` / 404; blue 403 / 403 / 200 `ok: false` / 403; red, none, garbage 403; observer 403 / 403 / 403 / 404 |
| Blue end to end: start(blue), advance, state | 200, 200, 200 `CellView` shape; no `red` key or value in the payload on all three vignettes |
| `/eventlog` before and after the whole refused series | identical on all three vignettes |

Pre-playback 403 for a player: this discloses nothing. A refused player learns only its own permissions (403 is the same whether or not a playback exists, which is the order the package and `FR-7340` ask for). The one non-403 pre-playback answer, blue `viewpoint` naming `blue`, is an entitled request answered `ok: false, no_playback_session` to the seat that may ask; it exposes no state. The Observer's pre-playback `state` 404 is a permitted read. No contradiction with `FR-7340`.

### Concurrency

Live clock running at 600x on one session while two threads hammered playback advance/state/refused-viewpoint and two threads called `/step`: 320 requests, 0.8 s, all 200 or 403, no thread left alive, no 5xx. `_locked` takes `mgr._lock` (RLock) and does not call `catch_up`, so playback calls do not tick the live clock, as before the change.

### Mutations (scratch edits, restored with `git checkout -- spacesim`)

All 13 caught (a test fails): white no longer exempt; player `start`/`viewpoint` own-cell check removed; player `advance`/`speed`/`state` current-viewpoint check removed; Observer allowed to mutate; Observer state read refused; no-seat refusal removed; `_playback_ack` 403 mapping removed; `PlaybackSeatRefused` 403 mapping removed; the seat forced to `white` in each of the five routes (start, advance, state, viewpoint, speed). The working tree was clean afterwards.

## Scope audit

Source changes: `inprocess.py`, `server.py` (declared) and the new test module; `test_web.py` edits as declared; docs: CLAUDE.md, training 08, RTM, FS-107 `Referenced By`, ledgers. `spacesim/engine/` and `session/aar.py` untouched. No caller outside the tests uses the routes (`grep` over `static/`, `tools/`, `.claude/skills/` is empty). No `docs/pipeline/` change.

## Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| F1 | `test_refused_requests_leave_session_and_log_untouched` compares only `/eventlog` and passes on the parent, so it does not detect a refused request that mutates playback; the package named `save_state()` before/after. The other tests (`_snap` comparisons) do cover playback state, so the behaviour is pinned elsewhere. | Low | `08-code-implementation` follow-up |
| F2 | The completion note says 12 of 14 tests failed first; measured on the parent files it is 11 of 14 (the refused-untouched case also passes there). Wording only. | Low | `08-code-implementation` |
| F3 | `docs/training/12-white-cell-manual.md` (where playback is described, if anywhere) and the `FR-7340` Notes "required, not yet built" flip were neither edited nor listed in the completion note; the package defers the Notes flip to `04` after `VERIFIED`. | Low | `08-training-manual-authoring` / `04-requirements-engineering` |

Verifier-noted, not findings: the single shared playback cursor (a player's own-cell start replaces White's cursor) is the accepted Decision 3; per-seat cursors remain an open owner question. The Observer reads a ground-truth playback by design (Decision 5).
