# IP-1073 — Console Wiring to the Server's Refusals: Seat-Aware Time Controls, Visible Load and Time-Control Errors, Race-Free Dry-Run Preview, Scrollable Menus (NFR-1600, NFR-3020, NFR-3030, FR-4310)

> **Package ID:** IP-1073
> **Version:** 1.0
> **Status:** ✅ VERIFIED 2026-10-24 ([VR-1073](../verification/VR-1073-console-refusal-wiring.md); implemented by `08-code-implementation`) — originally authored 2026-10-24 by `07-implementation-planning` (release-push remediation pass).
> Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive of 2026-10-24,
> recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256, authorizes
> remediation packages for bugs, in-progress and critical items; run #256 names `BL-0350`,
> `0327`, `0323`, `0333` and `0353`. Authoring is not itself the authorization; that recorded
> decision is. The `run-spacesim` skill-text edit in Files to Modify carries the separate owner
> authorization recorded in `BL-0353`'s row ("the skill text is an owner-authorized edit at the same
> time"); the implementer confirms it is on record before editing `.claude/skills/`.
> **Dependencies:** [FS-134](../../features/FS-134-browser-console-rule-suite.md) (the browser
> suite this extends), [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4;
> [IP-1340](IP-1340-browser-console-rule-suite.md), [IP-1068](IP-1068-white-only-controls-server-enforcement.md),
> [IP-1069](IP-1069-white-only-panels-registered.md), [IP-1101](IP-1101-self-contained-saves.md)
> (all `VERIFIED`); and, for ordering, [IP-1102](IP-1102-save-load-robustness.md) and
> [IP-1072](IP-1072-white-only-extension.md) (see Dependencies).
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0323`, `BL-0327`,
> `BL-0333`, `BL-0350`, `BL-0353`
> **Produces:** a console that does not offer or silently fail the controls the server now refuses,
> reports a refused save load, keeps its dry-run preview consistent with the last edit, and lets
> every menu entry be reached; and a walkthrough recorder and skill recipe that use the White seat
> for time control.
> **Feature Reference:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4
> (`FEAT-4300`), [FS-134](../../features/FS-134-browser-console-rule-suite.md) (`NFR-2840`)
> **Related Topics:** [VR-1101](../verification/VR-1101-self-contained-saves.md) F2;
> [VR-1069](../verification/VR-1069-white-only-panels-registered.md) F4;
> integration review of tranche 2 F-01 and F-04

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package (forward design) for five open console and tooling bugs. Client, CSS, one
tool script, one skill recipe; no server or engine change.*

---

## Package ID

IP-1073 (FS-106 client slice; `IP-1070` belongs to FS-107).

## Title

Console wiring to the server's refusals, plus the dry-run race and the View menu height.

## Objective

Five defects, each reproduced by the reviewer who filed it:

| Row | Defect at `fca85bf` (`ui_web/static/app.js` unless noted) | After this package |
|---|---|---|
| `BL-0350` (IR F-01) | The command palette offers "advance +1 min / +10 min / +1 hour" and "rewind to start" (`PALETTE.items`, lines ~2611–2614) to every seat, and bookmark chips rewind on click (~2528). `stepBy` / `rewindTo` (~2693) await the POST with no catch. Since `IP-1068` a non-White seat gets 403, so the entries fail as unhandled promise rejections with no message. | Non-White seats are not offered the four time entries; a bookmark click by a non-White seat sends no request and says why; any refusal that still arrives (a White tab whose request fails, or a stale seat) is reported in the console, never swallowed. |
| `BL-0327` (VR-1101 F2) and `BL-0350` | `loadSaveFile` (~1861) calls `JSON.parse`, then `stopRealtimeClock()`, then posts; it has no error handling. A refused load (403 for a non-White seat, 400 for a bad save) shows nothing, and polling stays stopped. The resume-warning `alert` has no headless coverage. | The clock is stopped only after the load succeeds; a refused or unparseable load shows its reason where load failures are already shown and leaves the session and polling untouched; the warning alert is covered by a browser test. |
| `BL-0323` | `previewOrder` (~623) posts `/order/validate` with no supersede guard, and `renderConsequencePreview` (~652) likewise; overlapping responses can land out of order and leave a stale preview and a wrongly enabled or disabled Issue button. The server still rejects at issue; the browser suite's `settle()` works around it. | A response is applied only if it belongs to the latest edit; superseded responses are discarded. |
| `BL-0333` (VR-1069 F4) | `.menu-pop` (`static/style.css` line ~54) has no `max-height` or scroll; on a 1000 px-tall viewport the bottom View-menu entries (including the new panels) fall outside the window and cannot be clicked. | Menus scroll within the viewport; every entry can be reached at 700 px height. |
| `BL-0353` (IR F-04) | `tools/record_walkthrough.py` Beat 6 calls `stepBy(600)` as Blue and gets an unreported 403, so the captured frames show a stale scene; `.claude/skills/run-spacesim/SKILL.md` (lines ~84–85) shows `start` and `step` curl calls without `?cell=white`, which now fail. | Beat 6 advances time as White through the API and fails loudly if the server refuses; the recipe's calls carry `?cell=white`. |

**Not changed:** server routes and their guards (`IP-1072`), the panel registry (`IP-1069`), the
classification of any order result, and training-manual curl examples (integration review F-05 is
owned by `08-training-manual-authoring`).

### Design Decisions

1. **Seat-aware time entries, by construction.** `PALETTE.items` builds the four time entries only
   when the active seat is `white` (the same predicate `setCell` uses for `.white-only`). The
   server's 403 remains the enforcement; this removes the dead-end, as `IP-1130` did for the
   Observer's buttons.
2. **One small reporting helper for control failures.** A function (for example
   `reportControlError(label, err)`) renders a short message in a dedicated, `aria-live="polite"`
   status line next to the existing session readout, with the server's `detail` when it is JSON and
   the raw text otherwise, clearing on the next successful control action. `stepBy`, `rewindTo` and
   the bookmark handler use it. `loadSaveFile` shows its refusal in the same element `loadVignette`
   already uses for "Load failed" (`#session`), so a refused load reads the same wherever it is
   triggered. Reuse the `loadVignette` detail-parsing (JSON `detail`, `problems` list) instead of
   writing a second parser; extract it if needed.
3. **Request ordering by a latest-edit token.** `previewOrder` increments a module-level counter
   before it awaits, keeps its own value, and applies its result (and starts
   `renderConsequencePreview`) only if the counter is unchanged; `renderConsequencePreview` carries
   the same guard. `refresh` already has the equivalent supersede guard; mirror its idiom rather than
   inventing a new one. No abort controllers are required.
4. **Menu height by CSS only.** `.menu-pop` gets a viewport-relative `max-height` (the toolbar's
   height subtracted) and `overflow-y: auto`. No JS.
5. **Recorder over API.** Beat 6 posts the advance with `cell=white` through the page's request
   context (not by switching the visible seat, so the recording stays a Blue view), checks the
   status, raises on non-2xx, then calls `refresh()` and waits for the clock readout to change.
6. **No change to what a White seat can do.** Every White-seat path behaves as before.

## Feature Reference

[FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4 (clock authority is White's; the
console must not offer a control the server refuses) and
[FS-134](../../features/FS-134-browser-console-rule-suite.md) (the browser suite that guards the
console's load-bearing rules).

## Requirements Covered

| ID | How |
|---|---|
| `FR-4310` | The console no longer offers time control to a seat that cannot use it and reports a refusal when one occurs. |
| `NFR-1600` | A refused load, a refused time control and an unparseable save file are handled, not thrown. |
| `NFR-3020` | The plan-first dry-run preview and the Issue gate always reflect the latest edit. |
| `NFR-3030` | Every menu entry (including the Compare and Assessment panel toggles) is reachable. |

All appear in the FS-106 / FS-134 requirement lists or their cited baseline; none added.

## Architecture Components

- **C4 Operator Console** (`static/app.js`, `static/index.html`, `static/style.css`).
- **Tooling** (`tools/record_walkthrough.py`, `.claude/skills/run-spacesim/SKILL.md`): consumers of
  the HTTP surface only.

Server, session layer and engine untouched; determinism and import-guard gates unaffected.

## Interfaces

- **INT-0001** (HTTP) consumed only: `POST advance`, `POST rewind`, `POST load_save`,
  `POST order/validate`, `POST preview/consequence`. No contract change.
- Console DOM: one new status element; no existing id changes.

## Files to Create

- `spacesim/tests/test_tooling_seat_recipes.py` (static check of the recorder and skill recipe).

## Files to Modify

Checked against the tree at `fca85bf`:

- `spacesim/ui_web/static/app.js`: `previewOrder` (line ~623) and `renderConsequencePreview` (~652)
  guard; `loadSaveFile` (~1861) order of operations and error handling; `PALETTE.items` (~2606)
  time entries; bookmark chip click handler in `renderBookmarks` (~2521–2530); `stepBy` /
  `rewindTo` (~2693–2694); the new reporting helper.
- `spacesim/ui_web/static/index.html`: the status element near `#session` (line ~246).
- `spacesim/ui_web/static/style.css`: `.menu-pop` (line ~54) and a rule for the status line.
- `spacesim/tests/test_browser_console_rules.py`: new browser tests added to the existing module
  (the `Console` class and the `server` / `pw_browser` fixtures live there); update the comment on
  `INIT_SCRIPT` that says the client has no supersede guard. Keep `settle()`; it is harmless.
- `tools/record_walkthrough.py`: Beat 6 (lines ~176–181).
- `.claude/skills/run-spacesim/SKILL.md`: the `start` and `step` lines of the curl recipe
  (~84–85), under the authorization noted above.

No other production file changes.

## Implementation Tasks

1. Mark the package `IN PROGRESS` (header, MBP row, index, `ROADMAP.md`) before editing.
2. Write the tests below and see browser tests 1, 3, 4, 5, 7 and static test 8 fail for the stated
   reason before changing code. Where Playwright or Chromium is absent the browser tests skip
   loudly (the suite's existing rule); the implementer runs them where a browser exists, since the
   console is otherwise unverified headless.
3. Implement Design Decisions 1–5.
4. Run the whole suite including `-m browser`, then `-m "not browser"`, plus `test_determinism.py`
   and `test_import_guard.py`. Fix only defects this package introduced.
5. Documentation updates, then mark `COMPLETE`.

## Tests to Add

Browser tests go in `spacesim/tests/test_browser_console_rules.py` (module marker `browser` and
`verifies("NFR-2840")`; per-test markers add the leaf named). Each drives the real page through the
existing `Console` helper.

1. **Non-White seats are not offered time control (`FR-4310`).** Seat Blue, open the palette
   (Ctrl-K), filter "advance" and "rewind": no matching entry. Seat White: all four present.
2. **A non-White bookmark click sends nothing and says why (`FR-4310`).** Seed a bookmark through
   `bmSave`, seat Blue, click the chip: no `/rewind` request is observed (`page.on("request")`), a
   message naming the White Cell appears in the status line, no page error is raised.
3. **A refused time control is reported, not thrown (`NFR-1600`).** As White, intercept the advance
   route with `page.route` to return 403 `{detail: ...}`; trigger "advance +1 min": the status line
   shows the detail and no unhandled rejection is recorded (`page.on("pageerror")` stays empty).
   Before: an unhandled rejection and no message.
4. **A refused load shows its reason and leaves the session running (`NFR-1600`).** With a live
   started session and polling on, choose a save file containing `{"save_format": 1}` only (the 400
   that `IP-1102` returns for missing keys): the `#session` area shows the reason, `REALTIME_ON` is
   still true afterwards, and the session id is unchanged. Repeat as Blue (403). Before: nothing
   shown and polling stopped.
5. **An unparseable file is reported.** Choose a file containing `not json`: a message appears, no
   page error, polling untouched.
6. **A legacy save's resume warning is shown (`FR-7230`).** Build a legacy-shaped save from
   `GET /save` (drop `save_format`, `content`, `baseline`), load it as White: the dialog captured by
   `Console.dialogs` contains "legacy save", and the session id changed. This is the headless
   coverage `VR-1101` F2 found missing.
7. **The dry-run preview follows the last edit (`NFR-3020`).** Delay the first `/order/validate`
   response with `page.route` (hold it until the second has been fulfilled), compose a refused
   order, then change it to an accepted one before the held response is released: the final preview
   text and the Issue button state match the accepted order, and the stale refusal never appears.
   Run the same with the roles reversed (accepted first, refused last). Before: the held, stale
   response wins about half the time.
8. **Menus reach their last entry at low height (`NFR-3030`).** Open a context with a 1500×700
   viewport, open the View menu: the menu's bottom edge is within the viewport, the menu is
   scrollable (`scrollHeight > clientHeight`), and after scrolling the last entry's centre is inside
   the viewport and a click on it succeeds (for example the Assessment panel toggle). Before: the
   bottom edge is below 700 and the last entry cannot be clicked.

Static (non-browser) test, new file `spacesim/tests/test_tooling_seat_recipes.py`, marker
`@pytest.mark.verifies("FR-4310")`:

9. **Recorder and recipe name the White seat for time control.** Parse `tools/record_walkthrough.py`
   and `.claude/skills/run-spacesim/SKILL.md` as text: every `/start`, `/step`, `/advance`,
   `/rewind` POST in the recipe carries `cell=white`; the recorder contains no `stepBy(` call in a
   beat executed under a non-White seat, and Beat 6 contains a status check on the advance request.
   Before: both fail. (A text check is a weak guard for a script that cannot run in CI; it is stated
   as such and exists to stop the recipe drifting from the server again.)

## Documentation Updates

- `docs/requirements/03-requirements-traceability-matrix.md`: the `FR-4310`, `NFR-3020`, `NFR-3030`
  Test cells regenerate from the new markers (`python3 -m pytest --origin-report=rtm`, same
  commit); Implementation Package cells gain `IP-1073`.
- `docs/features/FS-106-white-cell-dashboard.md`, `FS-134-browser-console-rule-suite.md`:
  `Referenced By` only.
- `CLAUDE.md`: the `ui_web/static/app.js` code-map bullet gains one clause (seat-aware palette time
  entries, control-error status line, latest-edit guard on the dry-run).
- Training manual: if the status line or the seat-aware palette changes an operator-visible
  procedure, `docs/training/10-ui-reference.md` and `docs/training/15-manual-traceability.md` §15.1
  name the sections; route authoring to `08-training-manual-authoring` (the three curl examples that
  omit `?cell=white`, integration review F-05, are the same owner's).
- MBP row and tally, `packages/INDEX.md`, `ROADMAP.md`, this header.

## Definition of Done

- All Tests to Add exist; browser tests 1, 3, 4, 7, 8 and static test 9 were seen failing first and
  pass; browser tests ran in an environment with Chromium (not only skipped).
- No unhandled rejection from any control in the palette, bookmarks or load flow (checked by
  `pageerror` in tests 3–5).
- Full suite green with `-m browser` and `-m "not browser"`; `test_determinism.py` and
  `test_import_guard.py` green.
- `git diff --stat` touches only the files listed above and docs.
- Documentation updates done; status `COMPLETE`.

## Verification Checklist

1. Palette items for a non-White seat contain no time entry (read `PALETTE.items`, and see test 1).
2. `loadSaveFile` calls `stopRealtimeClock()` only after the post succeeds and has a catch covering
   `JSON.parse` and the post.
3. `previewOrder` and `renderConsequencePreview` each discard a superseded response.
4. In a real browser at 700 px height every View-menu entry can be clicked (reproduce independently).
5. Beat 6 of the recorder checks the advance status; the skill recipe's `start`/`step` carry
   `?cell=white`.
6. Server files are untouched (`git diff --stat`).
7. Full suite, the browser marker, and both permanent gates green.
8. Every new test carries a `verifies` marker naming a live baseline ID; RTM Test column regenerated.

## Dependencies

`IP-1340`, `IP-1068`, `IP-1069`, `IP-1101` (all `VERIFIED`).

Ordering: build **after** `IP-1102` (test 4 uses its real 400 for a save with missing keys; before
it that case is a 500, which the client must also survive but which would not exercise the intended
reason text). Soft ordering after `IP-1072`: no shared file, but the console's Creator and save
flows then see the final guards when the browser suite runs. No file overlap with `IP-1311`.

## Risks

- **Browser tests are the only real check.** The console is unverified headless outside the
  `IP-1340` suite. A package whose tests all skip proves nothing; the Definition of Done requires a
  run with Chromium and the implementer reports where it ran.
- **Race tests can be flaky.** Test 7 must control response order with `page.route` rather than
  timing; if a delay-based version is used, it must wait on observable events, not sleeps.
- **Status line placement.** The toolbar is crowded; use the existing readout area and keep the
  element empty (zero height) when there is no message so layout is unchanged.
- **Skill-file edit authorization.** If the `BL-0353` authorization cannot be confirmed on record,
  skip only the SKILL.md edit, keep test 9's recipe assertion out, and note it in the completion
  report.

## Rollback Considerations

Revert the commit. No server, data or format change. The CSS and DOM additions are additive.
