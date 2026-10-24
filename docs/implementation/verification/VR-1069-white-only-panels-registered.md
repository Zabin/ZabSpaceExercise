# VR-1069 — Verification Report: Compare and Assessment Panels Join the Panel Manager (NFR-3030)

> **Document ID:** VR-1069
> **Version:** 2.0 (supersedes v1.0, which `RETURNED` the package)
> **Status:** ✅ Final
> **Dependencies:** [IP-1069](../packages/IP-1069-white-only-panels-registered.md) v1.0,
> [FS-106](../../features/FS-106-white-cell-dashboard.md), [FS-201](../../features/FS-201-competency-assessment.md)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1069` (this v2.0 pass)
> **Feature Mapping:** FS-106 / FS-201 (`FEAT-8100`)

[↑ Verification index](INDEX.md) · [Docs index](../../INDEX.md)

## Package

IP-1069 v1.0 after its re-run (`92ba158`, against v1.0 of this report); tree verified at `be7183a` (branch
`claude/reverify-ip-1069`, from `claude/verify-ip-1340`). Independent fresh session: it took no part in the
implementation, the re-run or the v1.0 verification.

## Result

**VERIFIED** — 0 failed checks. v1.0's one failed check (F1) and its Medium finding (F2) are closed; F3 is closed;
F4 stays open as a Low backlog item. Two new Low observations (below), neither a failed check.

## v1.0 findings re-checked against the shipped code

| v1.0 | Re-check | Result |
|---|---|---|
| F1 Compare gets no panel controls | `panels.js:23` registers `compare-panel` with `handle: "summary"`; `headerOf` now finds the `<summary>`. Real Chromium as White: `#compare-panel` has 3 buttons (grip/dock/close), as does Assessment | Closed |
| F2 filter test satisfied by a comment; nothing checks a registered panel has controls | Filter test strips `//` comments and requires `classList.contains("white-only")`; new `test_every_registered_panel_gets_panel_controls`. Break checks below catch both | Closed |
| F3 RTM `NFR-3030` Impl. Package cell `UNASSIGNED` | Now `IP-1069`; cell rewritten by this pass to read plainly (no longer "awaiting `09`") | Closed |
| F4 View menu has no scroll on short viewports | Not touched by the re-run (out of scope); unchanged | Open, Low, backlog |

## Definition of Done audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Both panels registered; non-White seats are not offered them | `panels.js:23-24`; `buildMenu` marks a menu item `white-only` from the panel section's class; `style.css:13`. Browser: White menu lists 12 incl. both; Blue and Red list 9, neither Compare, Assessment nor AAR | Pass |
| 2 | Registry test passes and was seen failing first; tagged | Module `pytestmark = verifies("NFR-3030")`; 4 tests pass. Independently reproduced: with `panels.js` from `92ba158^` the new controls test fails (`compare-panel (handle=None)`) | Pass |
| 3 | Full suite and both gates green | Below | Pass |
| (Objective) | Closed, floated, resized, reopened and reset like the other ten | Real browser, below: every behaviour passes for Compare and Assessment | Pass |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| `PANELS` has twelve entries matching `index.html`'s panel sections | Set-equality test passes; unregistering `drill-panel` or `assessment-panel` fails it | Pass |
| Menu filter reads the seat and the `white-only` class | `panels.js` `classList.contains("white-only")`; seat hiding by the shared CSS rule; verified for White/Blue/Red | Pass |
| Only `panels.js` and the new test changed | Re-run commit `92ba158`: `panels.js`, `test_panel_registry.py`, plus ROADMAP, master build plan, packages index, journal, RTM (status/trace bookkeeping) | Pass |
| Both gates green by name | Below | Pass |

## Requirements audit

| ID | Implemented | Tested | RTM | Result |
|---|---|---|---|---|
| NFR-3030 | `panels.js` registry, `handle: "summary"` for Compare, drag-click swallow, menu filter; `index.html` | `test_panel_registry.py` (4 tests, all tagged via module `pytestmark`) | Test cell lists the 4; Impl. Package cell `IP-1069` | Pass |

## Browser check (headless Chromium, real server on loopback, vignette index 1, seed 1; script in the scratchpad, not committed)

| Check | Result |
|---|---|
| Compare and Assessment each have 3 controls (grip, dock, close) | Pass |
| White menu lists both (12 entries); Blue and Red lists 9, neither listed | Pass |
| Dock click does not toggle the `<details>`, and does not float a docked panel | Pass |
| Drag by the grip floats Compare; release does not toggle | Pass |
| Drag started on the summary text floats it; release does not toggle | Pass |
| Plain click on the summary (after a drag, then again) toggles it each time | Pass |
| Regression probe: a drag that ends elsewhere (released over the page corner) leaves no toggle, and the next genuine click toggles (not swallowed) | Pass |
| Zero-move press/release toggles; keyboard Enter on the summary toggles | Pass |
| Dock, then close hides; menu checkbox reopens | Pass |
| Close both then Reset layout restores both; float both then Reset layout re-docks both | Pass |
| Page errors | none |

The swallow code adds a capture-phase click listener on the panel, removed by `setTimeout(0)`; a drag released
elsewhere leaves the listener for at most one task, so it cannot swallow a later click.

## Break checks (throwaway edits, each reverted; `git status` clean after)

| Mutation | Result |
|---|---|
| Remove Compare's `handle` | `test_every_registered_panel_gets_panel_controls` fails — caught |
| Revert to pre-fix `panels.js` | the same test fails — failing-first reproduced |
| Filter changed to `classList.contains("zzz")` | `test_menu_builder_filters_white_only_panels` fails — caught (v1.0 miss closed) |
| Delete the `assessment-panel` entry | 2 tests fail — caught |
| Delete the `drill-panel` entry | registry equality fails — caught |

## Test run

- `python3 -m pytest --tb=short --junitxml=…` (full suite): exit 0; junit 1284 tests, 0 failures, 0 errors, 3 skipped.
- `python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py spacesim/tests/test_panel_registry.py -q`: exit 0, 18 passed.
- `python3 -m pytest spacesim/tests/test_doc_integrity.py`: run after the ledger edits (green, see commit).

## Scope audit

Re-run commit `92ba158` touched `panels.js`, `test_panel_registry.py` and status/trace bookkeeping only. In scope.

## Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| F4 (carried) | View menu has no max-height/scroll; the Panels entries at the bottom are unreachable by mouse on short viewports | Low | backlog (`08-code-implementation`) |
| N1 | `startDrag` floats a panel on any pointerdown, so a plain click on the Compare summary toggles it and also floats it in place (out of flow). Same pre-existing behaviour as every `<h2>` header; Dock undoes it | Low | backlog (design call; not a defect against this package) |
| N2 | Master build plan row text for IP-1069 still carried the "RETURNED" note after the re-run; corrected by this pass | Low | closed here |

## Related

[`00-master-build-plan.md`](../00-master-build-plan.md) · [`packages/INDEX.md`](../packages/INDEX.md) ·
[`docs/requirements/03-requirements-traceability-matrix.md`](../../requirements/03-requirements-traceability-matrix.md)
