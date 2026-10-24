# VR-1073 — Verification Report: Console Wiring to the Server's Refusals (FR-4310, NFR-1600, NFR-3020, NFR-3030)

> **Document ID:** VR-1073
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1073](../packages/IP-1073-console-refusal-wiring.md) v1.0,
> [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4,
> [FS-134](../../features/FS-134-browser-console-rule-suite.md)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1073` (closes `BL-0323`, `BL-0327`, `BL-0333`, `BL-0350`, `BL-0353`)
> **Feature Mapping:** FS-106 (`FEAT-4300`), FS-134 (`NFR-2840`)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1073 — Console Wiring to the Server's Refusals (v1.0)
- **Implementing commit:** `4a3e40d` (branch `claude/ip-1073-build`); tree verified at that commit.
- **Independence:** fresh session; did not implement this package.

## Result

**✅ VERIFIED** — 0 failed checks; 2 Low findings, 2 Info findings, and 1 pre-existing Medium
observation (not this package's defect) routed to the backlog.

## Definition of Done audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Tests exist; 1, 3, 4, 7, 8 and static 9 seen failing first and passing; browser tests ran in Chromium | Scratch copy with the parent (`HEAD~1`) `app.js`/`creator.js`/`style.css`/`index.html`/recorder/SKILL.md: 9 of the 11 new browser cases fail (palette, bookmark, refused time control, refused load white and blue, unparseable file, both dry-run orderings, menu height); the 2 that pass on the parent are the legacy-warning coverage test and the player-seat `loadSession` test (coverage tests of existing behaviour, as the package states). Both static tests fail on the parent. `-m browser`: 21 passed, 0 skipped (Chromium 1243 from `/opt/pw-browsers`) | Pass |
| 2 | No unhandled rejection from palette, bookmarks or load flow | `pageerror` asserted empty in tests 2–5; own drive of the real console as White, Blue and Red: `pageerrors: []` in all three seats (stepBy, rewindTo, refused/unparseable/valid load, Save-as-scenario, Creator New draft). Console "Failed to load resource" lines are the expected 4xx network log entries only | Pass |
| 3 | Full suite green, both markers; gates green | Not-browser 1346 passed, 4 skipped, 21 deselected; browser 21 passed; `test_determinism.py` + `test_import_guard.py` 14 passed (see Test run) | Pass |
| 4 | `git diff --stat` touches only listed files and docs | See Scope audit | Pass (notes) |
| 5 | Documentation updates done; `COMPLETE` | CLAUDE.md code-map bullet extended; RTM regenerated (identical to tool output); ledgers `COMPLETE` before this run | Pass (F2) |

## Verification Checklist audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Palette items for a non-White seat contain no time entry | `app.js` `PALETTE.items`: the four time entries sit inside `if (CELL === "white")`. Drive: Blue and Red `palette_advance: []`, `palette_rewind: []`; White: 3 advance + 1 rewind. Mutation (guard replaced by `if (true)`) fails `test_a_non_white_seat_is_not_offered_time_control_in_the_palette` | Pass |
| 2 | `loadSaveFile` stops the clock only after the post succeeds; catch covers `JSON.parse` and the post | `app.js` `loadSaveFile`: `try { JSON.parse; api.post("/api/sessions/load_save") } catch { showLoadFailure; return }` then `stopRealtimeClock()`. Drive: bad save as White shows "save is missing required key 'content'", as Blue/Red shows the 403 reason; `REALTIME_ON` stays true and `SID` unchanged; `not json` shows "not a valid save file (…)". Mutation (catch → `throw e`) fails 3 tests | Pass |
| 3 | `previewOrder` and `renderConsequencePreview` each discard a superseded response | `PREVIEW_EDIT` token: `if (mine !== PREVIEW_EDIT) return;` after the validate post; `renderConsequencePreview(body, mine)` guards both its success and its catch path. Mutation (both guards removed) fails both orderings of test 7 | Pass |
| 4 | At 700 px every View-menu entry can be clicked (independent reproduction) | Real Chromium at 1500x700, Playwright `click(trial=True)` on all 28 View entries: default seat none blocked; White seat none blocked; Blue/Red menu bottom 673 px. Menu `scrollHeight` 987–1105 > `clientHeight` 627. Mutation (`max-height` removed) fails `test_a_menu_reaches_its_last_entry_at_low_height`. Narrow-window caveat: F1 | Pass (F1) |
| 5 | Beat 6 checks the advance status; recipe `start`/`step` carry `?cell=white` | `record_walkthrough.py` Beat 6: `page.request.post(.../advance?cell=white)`, `raise RuntimeError` on non-200, then `refresh()` and `wait_for_function("SCENE.now > …")`. SKILL.md diff is exactly the two curl lines gaining `?cell=white` (quoted URLs). Recorder run against a live server from a scratch copy: all beats ran through Beat 6 and the frames were captured (27) with no Beat 6 error; it stopped at the final `shutil.move` of the video file only (F4) | Pass (F4) |
| 6 | Server files untouched | `git diff HEAD~1 HEAD --stat` over `spacesim/ui_web/server.py`, `session/`, `engine/`: empty | Pass |
| 7 | Full suite, browser marker, both gates green | See Test run | Pass |
| 8 | Every new test carries a `verifies` marker naming a live ID; RTM regenerated | Markers: `FR-4310` (4), `NFR-1600` (4 cases), `FR-7230`, `NFR-3020` (2 cases), `NFR-3030`, static module `FR-4310`; `test_test_origins.py` + `test_doc_integrity.py` 30 passed, 1 skipped (partial-collection skip is by design). `python3 -m pytest --origin-report=rtm` in a scratch copy: "regenerated (unchanged)", file byte-identical to the committed RTM | Pass |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| `FR-4310` | `PALETTE.items`, `renderBookmarks`, `stepBy`/`rewindTo`, `reportControlError`, `#control-status` | `test_a_non_white_seat_is_not_offered_time_control_in_the_palette`, `…bookmark_click_sends_nothing_and_says_why`, `…player_seat_loading_a_vignette_sees_the_refusal`, static recipe/recorder tests | Test column lists them; Impl. Package names `IP-1073` | Pass |
| `NFR-1600` | `loadSaveFile`, `showLoadFailure`, `refusalParts`, `stepBy`/`rewindTo` catches | `…refused_time_control_is_reported_not_thrown`, `…refused_load_shows_its_reason…` (white, blue), `…unparseable_save_file_is_reported` | Listed | Pass |
| `NFR-3020` | `PREVIEW_EDIT` token in `previewOrder`/`renderConsequencePreview` | `…dry_run_preview_follows_the_last_edit` (both orders) | Listed | Pass |
| `NFR-3030` | `.menu-pop { max-height; overflow-y: auto }` | `…menu_reaches_its_last_entry_at_low_height` | Listed (affected-subsystems cell gains `ui_web/static/style.css`) | Pass |
| `FR-7230` (coverage) | existing (`IP-1101`) | `test_a_legacy_saves_resume_warning_is_shown` (closes the `VR-1101` F2 coverage gap) | Listed | Pass |

## Test run

All commands run in the worktree at `4a3e40d`.

| Command | Result |
|---|---|
| `python3 -m pytest -m "not browser"` | 1346 passed, 4 skipped, 21 deselected (the 4 skips are the same pre-existing ones as `VR-1072`: two `test_defensive_audit_2026`, one `test_derived_probabilities`, one `test_test_origins` partial-collection) |
| `python3 -m pytest -m browser` | 21 passed, 0 skipped; Chromium 1243, headless |
| `python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py` | 14 passed |
| `python3 -m pytest spacesim/tests/test_doc_integrity.py spacesim/tests/test_test_origins.py` | 30 passed, 1 skipped (run again after this report's ledger edits; see commit) |
| `python3 -m pytest --origin-report=rtm` (scratch copy) | RTM unchanged, identical to the committed file |

**Failing-first reproduction (scratch copy, parent client files):** 9 failed browser cases listed
under DoD 1; both static tests failed.

**Mutations (scratch copy of the final tree; each reverted):** remove the White-only palette guard;
remove both latest-edit guards; `loadSaveFile` catch to `throw`; remove menu `max-height`; `stepBy`
catch to `throw`; remove the bookmark seat check. Each failed at least one test (1, 2, 3, 1, 1 and
1 failing tests respectively).

**Live console drive (headless Chromium, 1500x700, `leo-isr-denial`, one run per seat):**

| Behaviour | White | Blue | Red |
|---|---|---|---|
| Palette "advance"/"rewind" | 3 + 1 offered | none | none |
| Forced `stepBy` / `rewindTo` | succeed, no message | `#control-status`: "Advance: White Cell control: refused unless the request names the white seat" (same for Rewind) | same as Blue |
| Refused save (`{"save_format":1}`) | "Load failed: save is missing required key 'content'" | "Load failed: White Cell control: refused …" | same as Blue |
| Unparseable file | "Load failed: not a valid save file (…)" | same | same |
| Valid save | loads, session id changes | refused with reason, session unchanged | same as Blue |
| Save-as-scenario (invoked directly) | reason shown ("no user-save directory configured") | 403 reason shown | same |
| Creator "New draft" (invoked directly) | "draft sess-N created" | "error: White Cell control: sessions are created by the white seat, not the blue seat" | same (red) |
| Unhandled page errors | none | none | none |

## Scope audit

Files in `git show --stat 4a3e40d`: `app.js`, `index.html`, `style.css`, `creator.js`,
`tools/record_walkthrough.py`, `.claude/skills/run-spacesim/SKILL.md`, the two test files
(`test_browser_console_rules.py` modified; `test_tooling_seat_recipes.py` created), and docs
(`CLAUDE.md`, `ROADMAP.md`, MBP, packages index and header, RTM, `FS-106`, two training pages).

- `creator.js` is outside the package's file list; added on the owner's instruction. The diff is
  limited to a `guard()` wrapper that catches a refused call and writes `error: <detail>` into
  `#creator-save-result`, plus wrapping the nine `onclick` assignments. No other behaviour changed.
  Accepted.
- `.claude/skills/run-spacesim/SKILL.md`: the diff is exactly the two curl lines gaining
  `?cell=white`, i.e. the `BL-0353` fix the owner approved. `BL-0353`'s backlog row records the
  authorization ("an owner-authorized edit"). Accepted.
- `docs/training/05-core-concepts.md` and `08-http-api-reference.md` were edited, although the
  package routes training-manual edits to `08-training-manual-authoring` (integration review F-05).
  The package's DoD allows "docs", and the edits are accurate (`?cell=white` on `red_step`; the
  White-only list matches `IP-1072`). Low (F2).
- No server, session or engine file changed.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| F1 | `.menu-pop` uses a fixed `max-height: calc(100vh - 70px)`, which assumes a one-row toolbar. With the White seat the toolbar wraps (146 px at 1500 px wide, 198 px at 1100 px), so at 700 px height the View menu's bottom edge is at 722 px (1500 wide) and 748 px (1100 wide). Every entry is still clickable at 1500x700, but at 1100x700 "Reset layout" fails Playwright's actionability check. The package test covers the default (single-row) toolbar only. A viewport-height token measured from the toolbar (or `position` relative to the menu's own top) would close it. | Low | `07` package repair (follow-up `08`) |
| F2 | The package listed `FS-134` Referenced By under Documentation Updates; `FS-134` still has no `IP-1073` reference. The two `docs/training/` edits are outside the package's stated owner (`08-training-manual-authoring`) though correct. | Low | `07`/`08` (doc housekeeping) |
| F3 | Pre-existing, not introduced here: the palette's "rewind to start" calls `rewindTo(0)`, which the server honours literally. On a started session the sim clock goes to t=0 (1970), the call takes about 15 s, the clock is left running and the next `GET /save` is hundreds of MB. It should rewind to the vignette start epoch. `IP-1073` Design Decision 6 deliberately left White behaviour unchanged. | Medium | `00-intake` bug, `07` remediation package |
| F4 | `tools/record_walkthrough.py` hard-codes `/opt/pw-browsers/chromium-1194/chrome-linux/chrome`, and video recording needs `ffmpeg-1013`; neither exists on this machine (1243 / 1011 installed). With scratch overrides the recorder ran every beat including Beat 6 and captured frames, then failed at `shutil.move` of the video. Environment fragility, not caused by `IP-1073`. | Info | `07`/`08` tooling |
| F5 | The `#control-status` line is cleared only by the next successful stepBy/rewindTo; a refused load writes to `#session` instead and nothing clears the status line on a seat switch. Cosmetic. | Info | `08` (optional) |

## Recommendations

- Verdict: `VERIFIED`. F1 and F3 should be filed to the backlog; neither blocks.
- Independence: this report was written in a fresh session by an agent that did not implement
  the package.
- Next step: `10-integration-review` for the console/White-only tranche once its remaining
  packages are `VERIFIED`; otherwise `08-code-implementation` on `IP-1334`.
