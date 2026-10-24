# VR-1069 — Verification Report: Compare and Assessment Panels Join the Panel Manager (NFR-3030)

> **Document ID:** VR-1069
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1069](../packages/IP-1069-white-only-panels-registered.md) v1.0,
> [FS-106](../../features/FS-106-white-cell-dashboard.md), [FS-201](../../features/FS-201-competency-assessment.md)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → IN PROGRESS` return of `IP-1069`
> **Feature Mapping:** FS-106 / FS-201 (`FEAT-8100`)

[↑ Verification index](INDEX.md) · [Docs index](../../INDEX.md)

## Package

IP-1069 v1.0, implementing commit `3fe281a`; tree verified at `7e516b6` (branch `claude/verify-ip-1069`, from
`claude/verify-ip-1091`). Independent fresh session (no part in implementation).

## Result

**RETURNED** — 1 failed check (High-Medium: the Compare panel is registered but gets no panel controls in a real
browser, so it cannot be floated or docked by drag/button; the package's own static tests cannot see this).

## Definition of Done audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Both panels registered; non-White seats are not offered them in the menu | Registered: `panels.js` lines 23-24. Menu filter (`buildMenu`, line 143) adds the `white-only` class to a menu item when its panel section has it; `style.css:13` `body:not([data-cell="white"]) .white-only {display:none !important}` and `app.js:563` `setAttribute("data-cell", c)` make that hide. Browser: White lists 12 panels incl. both; Blue and Red list 9, neither Compare nor Assessment (nor AAR, also White-only) | Pass |
| 2 | Registry test passes and was seen failing first; tagged | Module `pytestmark = verifies("NFR-3030")`; 3 pass. Reverted `panels.js` to `3fe281a^`: all 3 fail (registry equality, two-panels, menu filter) — claim reproduced | Pass |
| 3 | Full suite and both gates green | Below | Pass |
| (Objective) | "closed, floated, resized, reopened and reset like the other ten" (package Produces / Objective; `NFR-3030` "closable, floatable, resizable and resettable") | Real browser (below): `assessment-panel` gets the ✕/▣/⠿ controls and drags to float; **`compare-panel` gets no `.panel-tools` at all**. It is closable/reopenable only through the View menu, cannot be floated by drag, has no dock/close button | **Fail** |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| `PANELS` has twelve entries matching `index.html`'s panel sections | 12 `{ id:` entries; test asserts set equality with the 12 `class="panel"` sections | Pass |
| Menu filter reads the seat and the `white-only` class | Reads the section's `white-only` class (line 143) and relies on the page's seat-driven `body[data-cell]` rule, as the package prescribes; verified in browser for all three seats | Pass |
| Only `panels.js` and the new test changed | `git show --stat 3fe281a`: those two plus ROADMAP, master build plan, packages index, journal (status bookkeeping) | Pass |
| Both gates green by name | Below | Pass |

## Requirements audit

| ID | Implemented | Tested | RTM | Result |
|---|---|---|---|---|
| NFR-3030 | `panels.js` registry + menu filter; `index.html` | `test_panel_registry.py` (3 tests, generated Test cell) | Test cell lists the 3; Impl. Package cell was `UNASSIGNED` (see findings) | **Fail** for Compare (registered but `injectControls` finds no `<h2>`) |

## Browser check (headless Chromium via Playwright, real server, vignette 01, script run from the scratchpad, not committed)

| Check | Result |
|---|---|
| White menu lists Compare + Assessment (12 entries) | Pass |
| Blue / Red menu does not list them (9 entries each) | Pass |
| Assessment: ✕ closes, menu checkbox reopens, drag floats | Pass |
| Compare: ✕ button present | **Fail** (no `.panel-tools`; the panel has no `<h2>`, only a `<details><summary>`; `headerOf()` returns null so `injectControls` returns early) |
| Compare: close/reopen via menu checkbox | Pass |
| Compare: float by drag | **Fail** (no grip/handle) |
| Reset layout: closed Assessment returns, panels docked | Pass |
| Page errors | none |

Note: with the browser at 1000 px height, the end of the View menu (the new entries) is outside the viewport and the
menu has no scroll (`.menu-pop` has no max-height/overflow); a real click needed a scripted click. Pre-existing
layout limitation, newly relevant because the entries were appended at the bottom.

## Break checks (throwaway edits to `panels.js`, each reverted; `git status` clean after)

| Mutation | Result |
|---|---|
| Delete the `assessment-panel` registry entry | 2 tests fail — caught |
| Revert to pre-package `panels.js` | 3 tests fail — caught (failing-first reproduced) |
| Disable the filter (`classList.contains("white-only")` -> `"zzz"`) | **0 tests fail** — not caught: the test only looks for the string `white-only` anywhere in `buildMenu`, and the code comment contains it |

## Test run

- `python3 -m pytest --tb=short --junitxml=…` (full suite): exit 0; junit 1273 tests, 0 failures, 0 errors, 4 skipped.
- `python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py spacesim/tests/test_panel_registry.py`: exit 0, 17 passed.

## Scope audit

`3fe281a` touched `panels.js`, the new test, and status bookkeeping only. In scope.

## Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| F1 | Compare panel is registered but `panels.js::headerOf` finds no `<h2>` in `#compare-panel` (it uses `<details>/<summary>`), so no grip/dock/close controls are injected and it cannot be floated by drag; `NFR-3030` ("closable, floatable") and the package Objective are not met for it. Fix options: give the panel a `handle: "summary"` registry entry (or an `<h2>`), then re-verify float/dock/close in a browser | High (defeats the package's purpose for one of two panels) | `08-code-implementation` re-run |
| F2 | `test_menu_builder_filters_white_only_panels` is satisfied by a comment; disabling the filter does not fail it. Also nothing statically checks that a registered panel gets controls (F1 slipped through). Suggest a check that each registered panel has an `<h2>` or declares a `handle` | Medium | `07-implementation-planning` (test hardening) / `IP-1340` browser suite case |
| F3 | RTM `NFR-3030` Impl. Package cell is `UNASSIGNED`; to be filled on the next pass (not edited here because the package is returned) | Low | `08-code-implementation` |
| F4 | View menu has no max-height/scroll; entries at the bottom are unreachable by mouse on short viewports | Low | backlog (`08-code-implementation`) |

## Related

[`00-master-build-plan.md`](../00-master-build-plan.md) · [`packages/INDEX.md`](../packages/INDEX.md) ·
[`docs/requirements/03-requirements-traceability-matrix.md`](../../requirements/03-requirements-traceability-matrix.md)
