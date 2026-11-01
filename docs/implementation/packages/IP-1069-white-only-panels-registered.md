# IP-1069 — Compare and Assessment Panels Join the Panel Manager (NFR-3030)

> **Package ID:** IP-1069
> **Version:** 1.0
> **Status:** VERIFIED 2026-10-24 ([VR-1069](../verification/VR-1069-white-only-panels-registered.md), fresh session; READY before that) — authored 2026-10-23 by `07-implementation-planning`, pipeline run #224. Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** Owner-authorized 2026-10-23 (master build plan row; `run #230` ledger note). Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** [IP-1067](IP-1067-side-by-side-controller-view.md) (the Compare panel) and
> [IP-2010](IP-2010-competency-assessment.md) (the Assessment panel), both `VERIFIED`.
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md),
> [`backlog.md`](../../pipeline/backlog.md) `BL-0305`
> **Produces:** the two White-only panels can be closed, floated, resized, reopened and reset like
> the other ten, and a test that every panel section is registered.
> **Feature Reference:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.3 (`FR-4620`, the
> Compare panel) and [FS-201](../../features/FS-201-competency-assessment.md) (the Assessment panel);
> the rule is `NFR-3030` (`FEAT-8100`), GDS-08 OQ2.
> **Related Topics:** [IP-1340](IP-1340-browser-console-rule-suite.md) (the browser suite; not needed here)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package.*

---

## Package ID

IP-1069.

## Objective

**As built at `eba9c04`**, `static/index.html` has twelve `<section class="panel …">` elements, and
`static/panels.js`'s `PANELS` registry (line 12) lists ten. Missing: `compare-panel` (line 657) and
`assessment-panel` (line 691), both `white-only`. They cannot be closed, floated, resized or reset,
breaking `NFR-3030` (`BL-0305`). After this package both are registered, and the View ▾ → Panels
menu does not offer White-only panels to other seats.

## Requirements Covered

NFR-3030.

## Architecture Components

C4 Operator Console (`static/panels.js`); no server or engine change.

## Interfaces

None.

## Files to Create/Modify

- **Modify** `spacesim/ui_web/static/panels.js` — add the two entries to `PANELS`; in the menu
  builder (line 130 onward) skip a panel whose section carries `white-only` when the seat is not
  White (the CSS rule at `style.css` line 13 already hides the section itself).
- **Create** `spacesim/tests/test_panel_registry.py` — static check (below).

## Implementation Tasks

1. Write the test; confirm it fails (two unregistered panels).
2. Register the panels; add the menu filter.
3. Full suite, both gates.

## Tests to Add

| Test | Verifies | Asserts |
|---|---|---|
| Every `<section class="panel…">` id in `index.html` appears in `panels.js`'s `PANELS` registry, and every registry id exists in `index.html` | `NFR-3030` | sets equal |
| The menu builder references the `white-only` class (static check that the filter exists) | `NFR-3030` | present |

The rendered behavior (float, resize, reset in a browser) is outside what a static test can show;
once `IP-1340`'s browser suite exists, a panel-manager case can be added there (not required here).

## Documentation Updates

`docs/training/12-white-cell-manual.md`, if it says the Compare or Assessment panel cannot be
moved (check `training/15` §15.1); RTM `NFR-3030` Test cell.

## Definition of Done

1. Both panels registered; non-White seats are not offered them in the menu.
2. The registry test passes and was seen failing first; tagged.
3. Full suite and both gates green.

## Verification Checklist

- [ ] `PANELS` has twelve entries matching `index.html`'s panel sections.
- [ ] The menu filter reads the seat and the `white-only` class (read the code).
- [ ] Only `panels.js` and the new test changed.
- [ ] Both gates green by name.

## Dependencies

IP-1067, IP-2010 — `VERIFIED`.

## Risks

Persisted layouts (`localStorage` key `panel-layout-v1`) gain two entries; existing layouts load
unchanged because unknown panels default to docked and visible.

## Rollback Considerations

Revert the commit; client-only.
