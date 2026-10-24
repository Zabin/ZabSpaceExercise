# IP-1067 — Side-by-Side Controller View: Ground Truth Beside Each Cell's Picture, One Instant (FR-4620)

> **Package ID:** IP-1067
> **Version:** 1.0
> **Status:** VERIFIED 2026-10-18 ([VR-1067](../verification/VR-1067-side-by-side-controller-view.md), fresh session; COMPLETE before that).
> **Earlier status record (superseded by the line above; retained as history, unedited):** 🔵 COMPLETE — 2026-10-18, `08-code-implementation`, pipeline run #193, awaiting a
> **fresh-session** `09-package-verification`. The package adds 10 tests in `test_controller_view.py`. **9 were seen failing first**; the one that passed on arrival pins the unknown-session 404. Full suite: **1108 passed / 3 skipped** (run #192 baseline 1098/3, plus 10). Gates: 14/14. No existing test changed.
> *(Was 🟡 IN PROGRESS — 2026-10-18, pipeline run #193.)*
> *(Was 🟢 READY.)* Authored 2026-10-18 by `07-implementation-planning`, pipeline run #191.
> Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** covered by two standing decisions:
> - the project owner's standing pre-authorization of 2026-10-11;
> - the owner's 2026-10-18 instruction extending it to every package that the stalled batch
>   `BL-0068`–`BL-0083` reaches. This package is `BL-0079`'s (item B13).
>
> **Dependencies:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.3 (the spec);
> [IP-1060](IP-1060-white-cell-dashboard.md) (the god-view and view-as) and
> [IP-1130](IP-1130-observer-read-only-access.md) (Observer rejection), both `VERIFIED`.
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0079`
> **Produces:** a White-only read that returns ground truth plus Blue's and Red's `CellView` for
> one simulated instant, and a console panel that shows them side by side.
> **Feature Reference:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.3
> (`FEAT-4600` `FR-4620`)
> **Related Topics:** [IP-1066](IP-1066-pending-inject-edit-cancel.md) (the sibling `FR-4450`
> package; independent of this one)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package.*

---

## Package ID

IP-1067.

## Objective

**As built at `d35639b`**, White reaches each cell's picture one call at a time. The calls are
`GET /godview` (`server.py` line 844, which goes to `InProcessSession.get_godview` and then to
`SessionManager.get_godview`) and `GET /view/{cell}`. Each read runs its own `catch_up`, so two
reads can describe different simulated instants.

After this package:

- `GET /api/sessions/{sid}/controller_view?cell=white` returns `{now, truth, blue, red}`.
  - All three come from **one** locked `catch_up`.
  - `truth` equals `get_godview().model_dump()` at that instant.
  - `blue` and `red` each equal that cell's `get_view(...)`, the `FR-4610` view-as result, at that
    instant.
- A non-White `cell` returns 403.
- The White console gains a "⚖ Compare" panel with three columns: Truth, Blue and Red.

## Feature Reference

[FS-106](../../features/FS-106-white-cell-dashboard.md) v2.3: System Behaviour ("Side-by-side
controller view"), the Subsystem Responsibilities `session/api.py`/`inprocess.py` row, Error
Handling, Security, the Acceptance Criterion "Side-by-side view", and the Verification Plan.

## Requirements Covered

| ID | How |
|---|---|
| `FR-4620` | A single-instant composite read plus the console panel. Each cell panel goes through the existing `CellController` filter, unchanged. |

## Architecture Components

- **C2 Session Layer**:
  - `SessionManager.controller_view()` composes the existing `get_godview()` and `get_view(cell)`.
    It adds no filtering of its own (ADR-0004).
  - `InProcessSession.controller_view()` performs one `_locked_read`.
- **C4 Operator Console**:
  - the route in `server.py`;
  - a panel in `index.html`/`app.js`, rendered from the composite read only, with no other fetch.

## Interfaces

**INT-0002 / INT-0007:** one new read route. No existing route changes.

### Design Decisions

1. **One instant.** `InProcessSession.controller_view(sid)` takes `_locked_read(sid)` once, which
   means one `catch_up` under the session lock. Inside that lock it calls
   `mgr.controller_view()`, which returns:

   ```
   {"now": world.now,
    "truth": get_godview().model_dump(),
    "blue": get_view("blue").model_dump(),
    "red": get_view("red").model_dump()}
   ```

2. **No new filter path.** The cell panels are produced by exactly `get_view` (CellController).
   The truth panel is exactly `get_godview`.
3. **White only.** The route requires `cell == "white"` and otherwise returns 403. This is a
   stricter gate than `/godview`, which takes no cell argument (FS-106 v2.3 Error Handling). The
   trust model is unchanged: the caller asserts `cell`, as the other White routes do.
4. **UI.**
   - A White-only `<section id="compare-panel">` with three `<pre>` columns, refreshed by a
     **🔄 Refresh** button and, while the panel is open, on each `refresh()`.
   - Each column lists the instant, the assets the side holds or knows, and for Blue and Red each
     known track with its confidence. The Truth column lists every asset with its health.
   - The panel is text, not a second map or globe, and it renders from the composite response
     only.

## Files to Create

- `spacesim/tests/test_controller_view.py`.

## Files to Modify

Checked at `d35639b`:

- `spacesim/session/manager.py`: add `controller_view()` next to `get_godview` (line 1047).
- `spacesim/session/inprocess.py`: add `controller_view(session)` next to `get_godview` (line 428).
- `spacesim/ui_web/server.py`: add a `GET /api/sessions/{sid}/controller_view` route next to
  `get_godview` (line 844).
- `spacesim/ui_web/static/index.html`: add the `#compare-panel` section next to `#aar-panel`
  (line 653).
- `spacesim/ui_web/static/app.js`: add `refreshComparePanel()` and its wiring.
- `CLAUDE.md` code map: add one clause.

## Implementation Tasks

1. Mark `IN PROGRESS`.
2. Write the tests below and see them fail first.
3. Implement Design Decisions 1–4.
4. Run the full suite plus both gates.
5. Update the ledgers: RTM `FR-4620`, `CLAUDE.md`, and MBP/INDEX/ROADMAP → `COMPLETE`. Route the
   manual impact (`WCM` god-view section) after `VERIFIED`.

## Tests to Add

1. With the clock paused, after some activity (`leo-isr-denial`, seed fixed, advanced 30 min):
   - `controller_view()["truth"]` equals `get_godview().model_dump()`;
   - `["blue"]` equals `get_view("blue").model_dump()`;
   - `["red"]` equals `get_view("red").model_dump()`;
   - `["now"]` equals `world.now`.
2. Single instant: `blue.now == red.now == truth.now == now`.
3. Fog: the Blue panel contains no Red-owned asset in `own_assets`, and the Red panel contains no
   Blue-owned asset there. Each panel equals the cell's own view, so its tracks are exactly that
   cell's tracks.
4. Read-only: calling it twice leaves `world.model_dump()` and the event-log length unchanged
   (clock paused).
5. HTTP:
   - `cell=white` returns 200 with the four keys;
   - `cell=blue`, `cell=red`, `cell=observer` or a missing `cell` return 403;
   - an unknown session returns 404.

## Documentation Updates

- The RTM `FR-4620` row.
- The `CLAUDE.md` code map.
- MBP, `packages/INDEX.md` and ROADMAP status.

## Definition of Done

- [ ] Design Decisions 1–4.
- [ ] Every test seen failing first, then passing.
- [ ] Full suite and both gates green.
- [ ] Ledgers updated; `COMPLETE`.

## Verification Checklist

- [ ] One `_locked_read` per call, so there is exactly one `catch_up`.
- [ ] The cell panels come from `get_view`, with no second filter.
- [ ] 403 for every non-White `cell`.
- [ ] Gates green, and the full-suite count reported.

## Dependencies

`IP-1060` and `IP-1130`, both `VERIFIED`. No package depends on `IP-1067`. It is independent of
`IP-1066`.

## Risks

- **Payload size.** The response is three full views in one payload. That is fine at about 24
  satellites, and it is the same data as three existing reads.
- **The UI is text-only.** The browser panel is unverified headless; only the backend contract is
  tested.

## Rollback Considerations

Additive: one route, one method each, and one panel. Reverting removes them, and no state is
involved.
