# IP-1088 — The Per-Cell Activity Feed Is Filtered at the Session Boundary: Blue and Red Never See White's Scheduled Injects, and a Cell's Effect Bars Carry the Symptom, Not the Cause (FR-6210, FR-6220)

> **Package ID:** IP-1088
> **Version:** 1.0
> **Status:** ✅ VERIFIED — see [VR-1088](../verification/VR-1088-fog-correct-activity-feed.md) v3.0 and the Master Build Plan ledger (authored 2026-10-31 by `07-implementation-planning`).
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive, recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256 (fix bugs before release; no new features) and the run #262 go-ahead, covers it: finding `M-1` of the release-candidate-3 delta review is a fog-of-war violation (load-bearing invariant 3) in `VERIFIED` code. Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** [IP-1066](IP-1066-pending-inject-edit-cancel.md), [IP-1083](IP-1083-rewind-keeps-future-white-injects.md), [IP-1084](IP-1084-fog-correct-controller-notices.md), [IP-1130](IP-1130-observer-read-only-access.md) (all `VERIFIED`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md), [`01-technical-work-breakdown.md`](../01-technical-work-breakdown.md) ("Release-push remediation, pass 9")
> **Produces:** a `cell_activity` read whose Blue and Red answers are produced by one fail-closed per-kind filter in `session/cells.py`, a White feed that is unchanged, a refusal for an unrecognized cell, and a fog matrix over every entry kind the feed can carry.
> **Feature Reference:** [FS-106 — White Cell Dashboard](../../features/FS-106-white-cell-dashboard.md) (scheduled injects, `FR-4410`/`FR-4450`); the activity timeline has no requirement leaf of its own (`CR-31`, see Risks).
> **Related Topics:** [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py) (`cell_activity`), [`spacesim/session/cells.py`](../../../spacesim/session/cells.py) (`CellController`), [`integration-review-rc3-delta.md`](../../reviews/integration-review-rc3-delta.md) `M-1`.

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Bug-fix package (one defect, one seam). Prose only; no code in this document.*

---

## Package ID

IP-1088.

## Title

Filter the per-cell activity feed at the session boundary with one fail-closed rule per entry kind: White keeps everything, Blue and Red keep their own orders and the symptom of effects on their own assets, and nobody but White sees a scheduled inject.

## Objective

**The defect (review `M-1`, Medium; reproduced read-only over HTTP in the planning pass).** `InProcessSession.cell_activity` (`session/inprocess.py`, the scheduled-inject branch, "2) Scheduled non-order events") derives each pending inject's lane with `ev_cell = ev.actor if ev.actor in (blue, red, white, neutral) else "white"`, then skips it only when `cell != "white" and ev_cell not in (cell, "white")`. The second clause keeps every White-owned inject for every cell, and every inject event is White-owned. The fog rule written in the docstring ("Blue and Red see only their own orders and own-asset active effects") is therefore not what the code does.

**Reproduction** (FastAPI `TestClient`, `leo-isr-denial`, `POST /inject?cell=white` with `at_sim_t` = now + 45 minutes, one `message` effect): `GET /activity/blue`, `/activity/red`, `/activity/observer`, `/activity/neutral` and `/activity/bogus` each return `{kind: inject, cell: white, status: scheduled, start: T+45 min, label: "inject (1 effects)"}`. White's own read returns the same row. A cell therefore learns that White has an event pending, when it fires and how many effects it carries, before the inject is delivered to anyone. `FR-6220`'s Postcondition says no interface outside its named no-cell set bypasses cell filtering; this route is not in the set. The branch is older than `IP-1066`/`IP-1083`, which made White-scheduled injects (`white-<n>` handles, re-armed after a rewind) a first-class feature, and `IP-1084` closed the sibling leak in the message path.

**Further findings from the audit of every entry kind (same function, read-only, all confirmed by reading the code; none changes the repro above):**

1. *Unrecognized cell strings are accepted.* `cell_activity` filters with `cell != "white"`, so any string other than `white` is treated as a cell with its own lane: `neutral`, `observer` and `bogus` all answer 200 with `cells: [<that string>]`. For `neutral` the effect branch compares `target_owner != cell`, so it returns every effect on a neutral-owned asset: ground truth, with no seat bound to it. `observer` is not routed through the Observer designation (`IP-1130` says the Observer dispatches unmodified to the god-view or the designated cell's view and adds no path of its own).
2. *Effect bars are richer than the cell's own `CellView`.* The effect branch labels a bar `"<template> → <target> (<outcome>)"` and sets `action` to the category. `CellController.view` (`session/cells.py`) gives the owner of the target only `{target, symptom, attributed}` plus `effect_windows` with `{target, category, start, end, attributed}`, and withholds the source unless the effect is overtly attributable. The `template` name (for example which cyber payload) is therefore a field the activity feed discloses and the view does not.
3. *Future-start effects.* The branch labels an effect `scheduled` when `eff.start > now`. If an effect with a future start can sit in `world.active_effects`, its owner sees it before it begins. Whether one can exist is not established by reading; the matrix constructs one directly in the world to find out, and the filter rule below is safe either way.
4. *Entry kinds that are not in the feed today and must stay out.* The feed reads three sources only: `osys.orders`, `sim.scheduler.pending()` events whose kind is `inject`, and `world.active_effects`. The logged `inject_admin` entries (including `IP-1083`'s `schedule` entry and the edit/cancel entries), `effect_gate_request`/`effect_gate_decision`, `condition_check` and `env_anomaly_check` ticks, role assignments, and save/load events are event-log entries or other scheduler kinds and are not read. The matrix asserts this for every cell including White, so that a future change that adds one is caught. A pending-approval order is an order of the issuing cell and is already own-cell only.
5. *Orders.* The order lane filters on `o.cell != cell` and shows the issuing cell's own `actor`/`target`/`delivery_path`; that is the cell's own planning data. No finding.

## Requirements Covered

- `FR-6210` — cell-scoped views are filtered at the session boundary; no cell-scoped interface exposes another cell's private data (the Must-level basis for the fix).
- `FR-6220` — Postcondition: no interface outside the named no-cell set bypasses cell filtering. The activity route is not in the set and this package keeps it out (it does not add the route to the set).
- `FR-4450` and `FR-4410` — the pending-inject queue and injects are White-only knowledge until they fire; the matrix pins that the activity feed does not become a second listing of them.
- `FR-6510` — the Observer seat adds no filtering path of its own (the `observer` cell resolves through the designation).
- `FR-1120` — replay-equality: the read changes no event log, scheduler or RNG state.
- Not covered, routed upstream: the activity timeline has no requirement leaf (`CR-31`, `BL-0345`); see Risks.

## Architecture Components

`session/cells.py` (`CellController`, the existing home of per-cell filtering), `session/inprocess.py` (`cell_activity`, the `SessionAPI` implementation), `ui_web/server.py` (the route and its refusal mapping). `engine/` is not touched. `ui_web/static/app.js` is not touched: the renderer draws whatever rows it is given, and the rows only shrink for Blue and Red.

## Interfaces

`GET /api/sessions/{sid}/activity/{cell}?past_window_s&future_window_s`: the response envelope (`now`, `t_start`, `t_end`, `cells`, `activities`) and the row shape (`kind`, `cell`, `actor`, `action`, `target`, `start`, `end`, `status`, `label`, `delivery_path`) are unchanged. Changes: (a) fewer rows for Blue, Red and the Observer-as-cell; (b) an effect row's `label` and `action` carry the symptom and category only; (c) a cell value other than `white`, `blue`, `red`, `observer` is refused. White's answer is unchanged in shape and content except the effect label (b), which stays full for White (see Decision 2).

### Design Decisions

1. **What each cell's feed may contain (derived from `FR-6210` and `CellController.view`, which already is the statement of what a cell may know).**
   - *White:* everything the feed has today: all orders, all effects (including `neutral`-owned), every pending inject. Unchanged.
   - *Blue or Red:* (i) its own orders in every state (queued, active, executed, cancelled, rejected, pending approval), exactly as today; (ii) one row per effect on an asset it owns, carrying only what its `CellView` already grants: the target, the symptom (the outcome), the category, the window, and whether it is overtly attributed; (iii) nothing else. In particular **no inject row of any kind**: an inject is White's script, and what a cell may know of it arrives when it fires, as a message or an effect it can already see through (ii) and `CellView`. Nothing about a pending inject is the cell's business.
   - *The other side's orders and effects on the other side's assets:* never.
2. **Effect rows for a cell drop the `template` name.** The label becomes `"<category> → <target> (<symptom>)"`, plus ` (attributed)` only when the effect is overt; the `action` stays the category. White keeps the full `template` label because White is the controller. This closes finding 2 and is the narrowest change that makes the feed no richer than `CellView` and `effect_windows`. The alternative of leaving the template in (it names an effect on the cell's own asset) was refused: the template can reveal a covert cyber payload the opposing side chose, which `CellView` deliberately withholds.
3. **An effect that has not started is not shown to a cell.** A non-White effect row requires `start <= now`. Owners learn of an effect when it begins. If no such effect can exist the rule is inert; the matrix proves which.
4. **One fail-closed filter, in `CellController`.** `cell_activity` is split into (a) assembly of ground-truth rows from the three sources, each row tagged with its source kind and the owning cell, and (b) a pure `CellController` function that takes those rows, the requested cell and `now` and returns the cell's rows. The filter is an allow-list by kind: a cell receives a row only if its kind has an explicit rule for that cell; an unrecognized kind is dropped for Blue and Red and kept for White. A future lane (a new source) therefore cannot leak by omission. This is the same split `IP-1084` used for the message path (one helper, one place the rule lives), and it places the filter at the `SessionAPI`/`CellController` boundary, not in the UI.
5. **Unrecognized cells are refused.** `white`, `blue`, `red` are the cells. `observer` resolves through the Observer designation exactly as `get_observer_view` does (designation `white` gives the White feed, `blue`/`red` the filtered feed for that cell), with no parallel filtering path (`IP-1130`). Any other string (`neutral`, `bogus`, empty) is refused with the same refusal the sibling cell-scoped reads use for an unknown cell; the implementer reads `get_view`'s behavior on `bogus` first and matches it (HTTP 400 or 404), and states which in the test. Existing callers only ever pass the three real cells.
6. **The White feed is not redacted in this package.** White also sees `inject` rows with `cell: white`; the renderer's lane list is `blue/red/neutral`, and how it draws a `white` row is out of scope (no change to `app.js`).

## Files to Create

- `spacesim/tests/test_activity_fog_matrix.py` (the matrix; see Tests to Add).

## Files to Modify

All paths and symbols below were read in the planning pass.

- `spacesim/session/cells.py`: add the pure activity filter beside `CellController.view`.
- `spacesim/session/inprocess.py`: `cell_activity` (about lines 610-740): assemble tagged rows, call the filter, resolve `observer`, refuse an unrecognized cell; keep the docstring truthful (it already states the intended rule).
- `spacesim/ui_web/server.py`: the `cell_activity` route (about line 831): map the refusal; update the docstring.
- `spacesim/tests/test_cell_activity.py`: its existing cases use `white`, `blue` and `red` only and assert nothing about Blue/Red and injects; re-run unchanged, extend only if one asserts a label format that Decision 2 changes (none was found).
- `CLAUDE.md`: the code map `cells.py` and `inprocess.py` entries gain one sentence (08's doc step).

## Implementation Tasks

1. Write the fog matrix first (Tests to Add) and watch the inject, `neutral`/`bogus`/`observer` and template cases fail on the current code (red).
2. Split `cell_activity` into tagged ground-truth assembly and the `CellController` filter (Decision 4); behavior for White is byte-identical (a golden comparison of the White feed before and after on the same session is part of the matrix).
3. Implement the per-kind rules (Decision 1), the effect-label rule (Decision 2) and the not-yet-started rule (Decision 3).
4. Resolve `observer` through the existing designation and refuse other unknown cells (Decision 5); map the refusal in the route.
5. Run the matrix green, then the full suite and both permanent gates.
6. Documentation per the Documentation Updates field.

## Tests to Add

`spacesim/tests/test_activity_fog_matrix.py`. Real routes through `TestClient` (`POST /inject?cell=white`, `POST /order`, `GET /activity/{cell}`, rewind/undo/advance) on `leo-isr-denial` or an authored two-side vignette whose Blue and Red assets, sensors and injects carry unique sentinel ids, so a leak is a substring check on the whole JSON body. Tag each test `@pytest.mark.verifies("FR-6210", ...)` as shown; the package's own completion cases use `IP-1088`.

**Fog matrix: every entry kind x White / Blue / Red / Observer** (expected set asserted exactly, never "contains"). Observer rows run twice, once designated `white` (equals the White feed) and once `blue`/`red` (equals that cell's feed). Tags: `FR-6210`, `FR-6220`.

| # | Entry kind and state | White | Blue | Red |
|---|---|---|---|---|
| 1 | Blue-issued order: queued, active, executed, cancelled, rejected, pending approval | yes | yes | no |
| 2 | Red-issued order, same states | yes | no | yes |
| 3 | White-scheduled inject, time-based (`fire_inject(at_sim_t=...)`) | yes | no | no |
| 4 | Vignette-declared scheduled inject | yes | no | no |
| 5 | White inject re-armed after rewind and after undo (`IP-1083` `schedule` entry) | yes | no | no |
| 6 | Pending inject edited, then cancelled (`IP-1066` `inject_admin`) | edited time, then gone | no | no |
| 7 | Condition-triggered inject (armed, then fired) and its `condition_check` ticks | no row for the tick | no | no |
| 8 | Effect on a Blue asset (a jam and a cyber effect; one overt, one covert) | yes, full label | symptom row, no template, `(attributed)` only when overt | no |
| 9 | Effect on a Red asset | yes | no | symptom row |
| 10 | Effect on a neutral-owned asset | yes (neutral lane) | no | no |
| 11 | Effect with `start` in the future, injected directly into `world.active_effects` | yes | no | no |
| 12 | Environmental-anomaly tick, gate request and decision, role assignment, save and load | none of them is a row for anyone | none | none |

**Unrecognized and special cells (`FR-6510`, `FR-6210`).** `observer` follows its designation (both designations); `neutral`, `bogus` and an empty segment are refused; none returns a row. The White feed returns the same row set as before the change for the same session (golden comparison on a session built by a fixed script).

**Regression for the reported leak (`FR-6220`, `FR-4450`).** The exact reproduction: schedule at T+45 min, read `blue`, `red`, `observer`: no inject row, no sentinel, no count of effects, no firing time anywhere in the body; White's read still has it. Then advance past the firing time: the message the inject delivered is in the addressed cells' `CellView` (unchanged), and the feed still has no inject row for Blue and Red.

**Regression for the `IP-1083` schedule entry (`FR-4450`, `FR-1120`).** After the inject is scheduled, a rewind to before the scheduling and an advance back: White's feed shows one inject row (not zero, not two); Blue and Red show none, at every step.

**Replay equals live; log unchanged (`FR-1120`, `NFR` determinism).** Read the feed for all four cells at three instants; assert the event log, the scheduler's pending list and the RNG state are byte-identical before and after the reads. Rewind to an earlier instant and advance back to the same instant: each cell's feed equals the one read live at that instant. Re-run on a loaded save (`IP-1101` path): the filtered feeds equal the pre-save ones.

**Fail-closed filter (`IP-1088`).** A unit test on the `CellController` filter with a row of an invented kind: dropped for Blue and Red, kept for White.

**Permanent gates:** `test_determinism.py` and `test_import_guard.py` unchanged and green.

## Documentation Updates

- **Manual impact:** operator-visible change = Blue and Red no longer see White's scheduled injects; their effect bars show the category and symptom, not the template; the feed refuses an unrecognized cell. Look-up in `docs/training/15-manual-traceability.md` §15.1: row "Activity timeline (Gantt)" (line 48: `WCM-6`, `BLU-2`, `RED-2`, FS-106) and the §15.2 row at about line 130 (`02` "Per-cell activity timeline (Gantt)", `10b` §10.15). Sections:
  - *update* `docs/training/10b-ui-reference-views.md` §10.15: the fog bullets (Blue/Red see their own lane only, never scheduled injects), table row 10 ("Scheduled inject": White only), the `scheduled` status row (White only for injects), the JSON note for effect labels, and a one-line cell-refusal note; its Sources footer. Writer: `08-training-manual-authoring`.
  - *update* `docs/training/02-interface.md` "Per-cell activity timeline (Gantt)" (lines about 106-126): the Blue/Red bullet gains "never White's scheduled injects"; the dashed-neutral legend line is marked White-only. Writer: `08-training-manual-authoring`.
  - *update* `docs/training/08-http-api-reference.md` row at line 44: add "scheduled injects: White only; unknown cell refused". Writer: `08-code-implementation` (narrow line) or `08-training-manual-authoring`.
  - *update* `docs/training/12-white-cell-manual.md` `WCM-6` (line 168 area): your scheduled injects are on your timeline only; a player cell cannot see them before they fire (useful to the facilitator who worries about spoilers). Writer: `08-training-manual-authoring`.
  - *update* `docs/training/13-blue-cell-manual.md` and `14-red-cell-manual.md`: neither mentions the timeline today although §15.1 maps `BLU-2`/`RED-2` to it. Add one sentence each in the section the matrix names (BLU-2, RED-2): your timeline shows your own orders and the effects on your own assets, never White's schedule. This is a *create* gap, not only an update. Writer: `08-training-manual-authoring`.
  - *update* `docs/training/09-troubleshooting-and-glossary.md` Gantt glossary entry (line about 102): "orders and effects" stays true; no change unless the glossary lists injects (check; otherwise `none`).
  - *update* `docs/training/15-manual-traceability.md` §15.1 row 48 and §15.2 row 130: add the `BLU-`/`RED-` anchors above and the `cells.py` source. Writer: `08-training-manual-authoring`.
  - Vignette tutorials and `intro_brief`s: `none — no tutorial or brief refers to the timeline's inject rows` (grep before building; hand to `08-vignette-development` if one does).
- `CLAUDE.md` code map: the filter, one sentence (08's doc step).
- Not written by this package: a requirement leaf for the activity feed (`CR-31`) and `FR-6220`'s note that the route is deliberately not in the set (routed to `04-requirements-engineering`; the tests tag `FR-6210`/`FR-6220`).
- `docs/implementation/00-master-build-plan.md`, `packages/INDEX.md`, the TWBS, `ROADMAP.md`: written in this planning pass.

## Definition of Done

- The matrix is green and was red before the fix for rows 3-7, the `neutral`/`bogus` refusals and the template case.
- `GET /activity/{blue|red|observer-as-cell}` returns no inject row in any state; White's feed is unchanged (golden comparison).
- The filter lives in `CellController`, is an allow-list by kind, and is the only path by which a non-White feed is produced.
- Reads change no event log, scheduler or RNG state; live and replayed feeds are equal.
- Documentation created or updated per Manual impact, with the §15.1/§15.2 rows in sync with the shipped change (or each hand-off recorded as a Manual-impact item).
- Full suite green with the permanent gates; the doc-integrity and test-origin checks green.

## Verification Checklist

- [ ] Repeat the reproduction over HTTP: Blue, Red and `bogus` return no inject row and no sentinel; White does.
- [ ] Every matrix row 1-12 has a named test; each expected set is asserted exactly.
- [ ] `cells.py` holds the filter; `inprocess.py` contains no per-cell `if` over rows other than the call.
- [ ] A row of an invented kind is dropped for a cell in the unit test.
- [ ] Event log, scheduler and RNG are identical across the reads; rewind then advance reproduces each feed.
- [ ] `test_determinism.py` and `test_import_guard.py` green; full suite green.
- [ ] Documentation per Manual impact exists: `10b` §10.15, `02`, `08` row, `WCM-6`, `BLU-2`, `RED-2`, §15.1/§15.2 rows in sync; `test_doc_integrity.py` and `test_test_origins.py` green.

## Dependencies

[IP-1066](IP-1066-pending-inject-edit-cancel.md), [IP-1083](IP-1083-rewind-keeps-future-white-injects.md), [IP-1084](IP-1084-fog-correct-controller-notices.md), [IP-1130](IP-1130-observer-read-only-access.md): all `VERIFIED`. File overlap: `IP-1160` (`READY` or later) edits `session/manager.py` and `ui_web/server.py`; this package edits `inprocess.py` and `cells.py` and one route's docstring and error mapping, so the overlap is a few lines in `server.py` and merges in either order.

## Risks

- **The feed has no requirement leaf (`CR-31`).** What a cell may see is derived here from `FR-6210` and `CellView`, not from a stated requirement, and Decision 2 (drop the template) and Decision 3 are design choices. Routed to `04-requirements-engineering` to baseline the feed and its lanes; the build does not wait. If the owner wants cells to see the template of effects on their own assets, Decision 2 is a one-line reversal and its test row changes.
- **Observer resolution.** The `observer` cell now follows the designation; a client that today passes `observer` expecting a one-lane answer gets the designated view's answer. The console does not call it (read before building; `app.js` is expected to pass the seat's cell).
- **Refusing unknown cells could break a caller that passes something else.** Existing tests and the console pass only `white`, `blue`, `red`; the full-suite run is the check.
- **White's feed still carries a `white`-cell inject row that the renderer has no lane for.** Out of scope; recorded so the verifier does not read it as a defect of this package.

## Rollback Considerations

Pure read-path change with no state, schema, event-log or save-format effect. Revert the three source files and the test file to restore the previous behavior (including the leak). No migration.
