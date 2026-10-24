# VR-1340 — Verification Report: Browser Suite for the Load-Bearing Console Rules (NFR-2840)

> **Document ID:** VR-1340
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1340](../packages/IP-1340-browser-console-rule-suite.md) v1.0,
> [FS-134](../../features/FS-134-browser-console-rule-suite.md)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1340`
> **Feature Mapping:** FS-134 (`FEAT-12200`)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1340 — Browser Suite for the Load-Bearing Console Rules (v1.0)
- **Implementing commit:** `876a5b8`; tree verified at `58e8b49` (branch `claude/verify-ip-1340`, from `claude/verify-ip-1350`). Chromium 141 build under `/opt/pw-browsers`, Playwright installed.
- **Independence:** fresh session; did not implement this package.

## Result

**✅ VERIFIED** — 0 failed checks; 4 Low findings (none blocks the transition).

## Definition of Done audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Browser tests run headless here and pass | Full suite: all 10 browser tests present in the junit xml with no skip/failure child; `-m browser` alone: 10 passed three runs in a row (16.5 s, 15.5 s, 16.0 s); plus six further runs of the four order-flow tests, 4 passed each | Pass |
| 2 | Each rule's test seen failing against a deliberately broken scratch client | Repeated by this verifier (below): all three rules fail; `app.js` restored from a byte copy, `git status` clean after | Pass |
| 3 | Without Playwright/Chromium the module skips with a named reason; rest of suite runs | `PLAYWRIGHT_BROWSERS_PATH=<empty dir> pytest -m browser -rs`: `1 passed, 9 skipped`, each reason `no Chromium build found under <dir> (and Playwright's own Chromium is not installed)`. Playwright-absent branch ("Playwright is not installed (pip install playwright)") read, not executed | Pass (F-4) |
| 4 | Playwright a minimum-version dev dependency, installed by the hook | `pyproject.toml` dev extra `playwright>=1.44`; `.claude/hooks/session-start.sh` install list ends `… httpx playwright`, no browser download | Pass |
| 5 | Every test tagged; full suite and both gates green | Module-level `pytestmark` plus per-test `verifies` (NFR-2840, NFR-3010, NFR-3020, all live; `--origin-report --origin-ids=NFR-2840` lists all 10); full suite and gates below | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| Full-suite output shows browser tests ran | junit: 1284 tests, 0 failures, 0 errors, 3 skipped; the 3 skips are the pre-existing ones (none in `test_browser_console_rules.py`) | Pass |
| Deliberate-break demonstration repeated | See "Deliberate breaks" — all three rules | Pass |
| No client file changed except stable-selector additions | `git show --stat 876a5b8`: no file under `spacesim/ui_web/` (zero selector additions needed). Later `panels.js` change belongs to IP-1069 | Pass |
| Server fixture binds loopback only, stops at teardown | Read: socket bound to `127.0.0.1:0`, uvicorn `host="127.0.0.1"`; `srv.should_exit = True` + `t.join(10)` after `yield`; browser and contexts closed in fixtures; the `SPACESIM_CONFIG` monkeypatch is undone | Pass |
| `pyproject.toml`, hook, `CLAUDE.md` updated; both gates green by name | Diff of `876a5b8` shows all three (marker `browser` registered; `-m browser`/`-m "not browser"` commands and install line in `CLAUDE.md`) | Pass |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| NFR-2840 | the module (rules a–c) | all 10 tests | Test column lists the 10 (generated; `--origin-report=rtm` leaves the tree unchanged); Impl. Package updated to VERIFIED by this run | Pass |
| NFR-3010 / NFR-3020 (named, not owned) | — | fog tests (3010); refused/malformed tests (3020) | Test cells filled and generated; Impl. Package stays UNASSIGNED (owned by other packages) | Pass |

## Test run

- `python3 -m pytest --tb=short --junitxml=…`: exit 0, junit 1284 tests, 0 failures, 0 errors, 3 skipped (190 s).
- `python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py spacesim/tests/test_doc_integrity.py`: 23 passed.
- `python3 -m pytest -m browser` x3: 10 passed each. Empty-browser-path run: 1 passed, 9 skipped with named reason.

## Deliberate breaks (scratch edits of `spacesim/ui_web/static/app.js`, restored; tree clean)

| Rule | Scratch edit | Result |
|---|---|---|
| (a) fog | after the scene fetch, append every non-own, non-White asset from `/godview` to the scene's assets | `test_blue_view_names_no_red_object…` fails (`['RED-OBJ'] == []`), `test_red_view_names_no_blue_object…` fails (`['GS-EAST', …, 'ISR-EO-1'] == []`) |
| (b) plan-first | refused-order branch of `previewOrder` sets `btn.disabled = false` | `test_a_refused_order_disables_issue…` fails (30 s wait timeout) |
| (c) confirm | `const consequence = null;` in `issueOrder` | `test_engage_…` and `test_cyber_…` fail (30 s wait timeout on "cancelled") |

## Non-vacuity and BL-0323 judgement

- Fog tests assert `hidden` (truth minus own tracks) is non-empty before checking, and check page text, every option in the order/tasking panels and every `fillText`/`strokeText` label. The tracked-object test uses a seeded variant vignette via `initial_tracks` (`br-blue-tracks-red`), asserts `tracked == {"RED-OBJ"}`, a drawn `RED-OBJ ±<km>` label and a 0.xx confidence in the custody row. The White test proves the hidden objects exist. Consequence tests assert dismissal sends nothing (order count unchanged, "cancelled" shown) and acceptance sends one; observe asserts no dialog.
- `settle()` waits for `window.__inflight === 0`, a counter on `/order/validate` fetches that `fetch` increments synchronously inside `previewOrder`, so each compose step finishes its dry-run before the next starts; this removes the out-of-order response race of `BL-0323` from the tests (six extra runs of the four order-flow tests all passed). It sidesteps rather than detects the defect, and the clock is paused so no background refresh adds a late preview (F-2).

## Scope audit

`876a5b8` touches the test module, `pyproject.toml`, hook, `CLAUDE.md`, ledgers, `ROADMAP.md`, journal and backlog. No production or client file. In scope.

## Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| F-1 | A broken rule in (b)/(c) surfaces as a 30 s Playwright wait timeout rather than a readable assertion, which slows and obscures a real regression. | Low | `08-code-implementation` |
| F-2 | The settle helper hides the `BL-0323` race; no test would catch it (or a regression of its later fix). Tests are only reliable while the clock is paused. | Low | `07` (with `BL-0323`) |
| F-3 | The fog check matches asset ids as text; a leak that renders under a display name or a changed label format would pass. | Low | `08-code-implementation` |
| F-4 | The skip test exercises `resolve_browser` with the Playwright default disabled, not the fixture's `pytest.skip` path; the Playwright-absent branch is not run. Skip reason was confirmed manually here. | Low | `08-code-implementation` |

## Ledger updates

`IP-1340` flipped `COMPLETE → VERIFIED` in the Master Build Plan (row and a status note), `packages/INDEX.md`, `ROADMAP.md`, verification `INDEX.md`; the RTM `NFR-2840` `Impl. Package` marker updated. The Test column was not hand-edited. `IP-1340` blocks no package.
