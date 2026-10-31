# VR-1094 — Verification Report: Release Polish, Unknown Save Format Refused and Chromium Discovery (FR-7230)

> **Document ID:** VR-1094
> **Version:** 1.0
> **Status:** Final
> **Dependencies:** [IP-1094](../packages/IP-1094-release-polish-save-format-and-chromium.md) v1.0
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE -> IN PROGRESS` return of `IP-1094`
> **Feature Mapping:** FS-110 (`FR-7230`)

[Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1094, Release Polish: Unknown Save Format Refused; Chromium Discovery in the Run Tools (v1.0)
- **Implementing commit:** `c67a723`; tree verified at `c67a723` (branch `claude/ip-1094-build`, private worktree). Parent `5cc19d8` copied to a private subdirectory for the reproductions.
- **Independence:** fresh session; did not implement this package.

## Result

**RETURNED** - 0 failed code or behaviour checks; 1 Medium ledger finding (F1) and 1 Low (F2). The returned item is a one-line ROADMAP correction; nothing in `spacesim/`, the tools or the manuals needs rework except F2's optional selection fix.

## Definition of Done audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Tests green and observed failing first | Parent reproduction below: `save_format` 999 loads (HTTP 200, a session is created) on the parent. Mutation run in a private copy: drop the gate -> `test_validate_save_refuses_unsupported_format[999]` fails; allow `3` -> `[3]` fails; newest -> oldest, in each of the two scripts -> `test_newest_build_and_env_root` fails; ignore `PLAYWRIGHT_BROWSERS_PATH` in each script -> same test fails. Six of six mutants killed. | pass |
| 2 | Full suite and both permanent gates green | Below. | pass |
| 3 | The two tools find Chromium on this container (`chrome-linux64`) | `find_chromium()` from each script returns `/opt/pw-browsers/chromium-1243/chrome-linux64/chrome` (variable unset and set). The driver ran end to end against a live server (OK, screenshot 1 MB). `record_walkthrough.py` found Chromium and launched it; it then died in `new_page` (video recording) on Playwright's missing `ffmpeg` build, which is an environment limit separate from the lookup (`/opt/pw-browsers` holds `ffmpeg-1011`, Playwright wants another revision; its message says `playwright install ffmpeg`). | pass |
| 4 | Documentation created/updated per Manual impact, §15.1/§15.2 in sync, or hand-offs recorded | See Documentation audit. | pass |

## Verification Checklist audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | `save_format: 999` through `POST .../load_save` returns 400 naming supported formats; format 2 and legacy unchanged | Real HTTP, parent on :8791, fix on :8792, same saved state with `save_format` replaced: parent returned 200 and created a session for 999, 0, -1, 1, 3, "2", 2.0, true, null, absent and 2. Fix: 400 `save_format <v> is not supported; supported formats: legacy (absent), 2` for 999, 0, -1, 1, 3, "2", 2.0, true, null, and zero sessions created for every refusal; absent key and 2 load (200). A legacy save (the parent-recorded save with `save_format`, `content`, `baseline`, `simulator_version` removed) loads on both with the legacy warning and re-saves as format 2 with an identical eventlog. | pass |
| 2 | No `chromium-1194` literal remains in `tools/` or `.claude/skills/run-spacesim/` | `grep -rn chromium-1194` over both: no hits (the one SKILL.md mention was reworded). | pass |
| 3 | `driver.py` `o-target-pick` replaced by the live id | `index.html` has `id="o-target"` once, `o-target-pick` zero; driver output `target_picker: True`. | pass |
| 4 | Only the named skill-file lines changed | `run-spacesim/SKILL.md` diff: four hunks, all browser-path text (the glob, the `chromium-1194` mention, the `CHROME_EXE` mention, the "No Chromium found" line). The driver diff is the lookup function, its call, the docstring pointer and the probe id. | pass |
| 5 | `test_determinism.py`, `test_import_guard.py` green; no `engine/` diff | Both green by name; `git diff HEAD~1 -- spacesim/engine` is empty. | pass |
| 6 | Documentation in sync | See Documentation audit. | pass |

## Requirements audit

| ID | Implemented | Tested | RTM cell | Result |
|---|---|---|---|---|
| `FR-7230` | `manager.py` `SUPPORTED_SAVE_FORMATS` + first gate in `validate_save` | `test_save_format_gate.py` (`verifies("FR-7230")`) | `03-requirements-traceability-matrix.md` FR-7230 Test cell regenerated; GDS-10 FR-L3 row names IP-1094 | pass |
| `NFR-1600` | same gate refuses before replay, registry untouched (probed) | same | unchanged | pass |
| `NFR-2840` | `find_chromium()` x2 | `test_run_tool_browser_lookup.py` (`verifies("IP-1094")`) | precedent only | pass |

The format-gate itself has no requirement leaf; the package routes that to `04-requirements-engineering` (see Documentation audit, hand-offs).

## Behaviour probes

- **Explicit `null`:** refused (400). Judged right: legacy saves have no key at all, so a present `null` is a damaged value, not a legacy marker; the parent silently loaded it as legacy. `0` likewise (the parent loaded it as legacy via truthiness). `true` is refused despite `bool` being an `int` subtype (explicit `isinstance(bool)` guard).
- **Ordering:** the format gate runs right after the dict check and before the required-key, IP-1102 100,000-entry and IP-1103 checks: `{"save_format": 999}` alone and `{"save_format": 999, ..., 100001 entries}` both return the format message; a save with no format key and a bad `seed` still gets its own IP-1081/IP-1101 message. The existing validate_save tests all pass.
- **Round trips (real HTTP, fix server):** step, step, undo, advance, rewind, force-add TLE, step, save, load_save, re-save on `01-leo-isr-denial`, `02-geo-rpo-shadowing`, `03-gnss-ew-campaign`, `04-co-orbital-threat-escort`, `00-training-basics`: every load 200 with format 2, and the re-saved eventlog and `final_time` identical.
- **Browser lookup:** variable unset -> `/opt/pw-browsers/chromium-1243/chrome-linux64/chrome`; set to the real root -> same; set to an empty directory -> `No Chromium found under <that dir> (set PLAYWRIGHT_BROWSERS_PATH).`; fake tree with `chromium-1194/chrome-linux64`, `chromium-1243/chrome-linux64`, `chromium-999/chrome-linux`: **`chromium-999` chosen** (F2).

## Test run

| Mode | Command | Result |
|---|---|---|
| Unfiltered | `python3 -m pytest -q --junitxml=...` | exit 0; 2227 tests, 0 failures, 0 errors, 4 skipped |
| Not browser | `python3 -m pytest -q -m "not browser"` | exit 0; 2185 tests, 0 failures, 5 skipped |
| Browser | `python3 -m pytest -q -m browser` | exit 0; 42 tests, 0 failures, 0 skipped |
| Gates by name | `test_determinism.py test_import_guard.py test_doc_integrity.py test_test_origins.py test_origin_retag.py` plus the two new files | exit 0; 181 passed |

Both new test files carry `verifies` markers naming live IDs (`FR-7230`, `IP-1094`).

## Documentation audit

Manual impact claimed: *update (small)*. Operator-visible change re-derived from the diff: one new `load_save` 400 refusal. Run tools are developer tooling.

| Item | Exists | Accurate | Result |
|---|---|---|---|
| `08-http-api-reference.md` load-save row | yes | the quoted reason `save_format <value> is not supported; supported formats: legacy (absent), 2` is byte-identical to the live 400 detail for 999 | pass |
| `12d` WCM-22 refusals table row `save_format 999 is not supported; supported formats: legacy (absent), 2` | yes | matches the live message; the cause and remedy are true (a newer simulator's save; the version that wrote it) | pass |
| `15-manual-traceability.md` WCM-22 row (15.2) and the §15.1 save row | yes | Sources name `validate_save` incl. the `SUPPORTED_SAVE_FORMATS` gate; symbol exists | pass |
| `CLAUDE.md` IP-1094 bullet | yes | `SUPPORTED_SAVE_FORMATS`, gate position, the `legacy (absent), 2` text, `o-target` probe: all true against the tree | pass |
| Hand-offs | recorded in the package text (Manual impact; the `04` leaf routing from rc5 `S-1`); this report records the open `04` item: add a leaf for the save-format gate. No `docs/pipeline/` edit made by this run. | | pass (Low note F3) |

## Scope audit

Files touched are all in the package's list plus tests, the two RTM files (generated Test column), the two training pages, CLAUDE.md, and ledgers. Outside scope: **ROADMAP.md line for IP-1092** (F1).

## Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| F1 | The build commit changed the **IP-1092** row of ROADMAP.md from `READY` to `COMPLETE`. `IP-1092` is `READY` in its package header, the Master Build Plan and `packages/INDEX.md` (never built). The header-vs-rows script shows the ROADMAP row as the sole disagreement the build introduced. The build also left the `IP-1094` ROADMAP row at `READY` (corrected by this run). Revert the IP-1092 row to `READY (authorized - project owner go-ahead 2026-10-31, MSTR-006 §3)`. `test_doc_integrity` does not catch it. | Medium | `08-code-implementation` re-run (one line) |
| F2 | `find_chromium()` (both copies) picks "newest" with a lexical `sorted()`: with `chromium-999` and `chromium-1243` present it returns `chromium-999`. Latent (real revisions are four digits) and the package's own test uses equal-width versions. Sort by the integer after `chromium-`. | Low | `08-code-implementation` |
| F3 | The `04` requirement leaf for the format gate is routed only in package prose and this report; ensure `00-pipeline-manager` harvests it. | Low | `04-requirements-engineering` via intake |
| O1 | Pre-existing, not this package: `IP-1089` header still says `READY` while the three ledgers say `VERIFIED`. | Low | `07`/owner |
| O2 | `record_walkthrough.py` surfaces the missing-ffmpeg condition as a raw Playwright traceback with an install hint; clear enough, environment-bound. | Info | none |

Ledger recount after this run: 91 `VERIFIED`, 0 `COMPLETE`, 1 `IN PROGRESS`, 2 `READY`, 0 `BLOCKED`, 94 packages. Only the `IP-1094` rows changed.
