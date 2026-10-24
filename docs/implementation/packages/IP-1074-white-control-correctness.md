# IP-1074 — White Control Correctness: Rewind Stays Inside the Exercise, and Seat and Observer Routes Answer 403 (FR-4310, FR-4320, NFR-1600)

> **Package ID:** IP-1074
> **Version:** 1.0
> **Status:** ✅ COMPLETE 2026-10-24 (pending `09`) — authored 2026-10-24 by `07-implementation-planning` (release-push remediation pass 2).
> Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive of 2026-10-24,
> recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256, authorizes
> remediation packages for bugs, in-progress and critical items. This package covers one Medium
> and one Low bug. Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4 (the spec);
> [IP-1068](IP-1068-white-only-controls-server-enforcement.md),
> [IP-1072](IP-1072-white-only-extension.md), [IP-1073](IP-1073-console-refusal-wiring.md) (all
> `VERIFIED`), which this corrects.
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0364`
> (`VR-1073` F3 was routed to the backlog in the same pass; if it holds a `BL` id by build time,
> cite it)
> **Produces:** a rewind that cannot leave the exercise's own time span, a "rewind to start" that
> means the start of the exercise, and `roles/assign` and `observer/view` that refuse by the
> request's seat with 403 like every other White Cell control.
> **Feature Reference:** [FS-106 — White Cell Dashboard](../../features/FS-106-white-cell-dashboard.md)
> **Related Topics:** [VR-1073](../verification/VR-1073-console-refusal-wiring.md) F3,
> [VR-1072](../verification/VR-1072-white-only-extension.md) F1,
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package (forward design). Two small, independent corrections in the White Cell control
surface, grouped because they share `ui_web/server.py`, the same test style and the same owner
requirement family. Part A is first because it is the Medium.*

---

## Package ID

IP-1074 (FS-106 → `IP-107x`; `IP-1072`, `IP-1073` taken).

## Title

White control correctness: bounded rewind with a real "rewind to start", and 403 on the two
body-seat routes.

## Objective

### Part A — rewind range (VR-1073 F3, Medium)

**Reproduction.** On a started session the command palette's "rewind to start" and the toolbar
Rewind both send `{"t": 0}`. `POST /api/sessions/{sid}/rewind` passes it to
`SessionManager.rewind_to` → `Simulation.rewind_to`, which keeps no events (all are after t=0),
rebuilds the world with `stop_time=0` and sets the sim clock to 1970. Observed: the call takes about
15 s; the lazy server clock, still running, then advances from 1970; the next `GET /save` is hundreds
of MB (the verifier saw about 566 MB). Nothing in the engine or session layer bounds `t`.

**Decision from the requirements.** `FR-4310` gives White the right to "rewind the simulated clock";
the simulation's own time span is `[ctx.start_epoch, current sim time]` — the same span
`session/aar.py::PlaybackSession` and `session/ephemeris.py` already use and enforce (a time before
the start is not part of the exercise; the AAR rejects a wholly out-of-range request). So:

- "Rewind to start" means `ctx.start_epoch`, the vignette's first instant (the session's initial
  world time), never epoch 0.
- A rewind target outside `[start_epoch, now]` is a client error: HTTP **400** with a reason naming
  the allowed span. Before the start is nonsense; after `now` is not a rewind (it would move the
  clock forward with no events, bypassing `advance`).
- `t == now` is allowed (a no-op rebuild; existing tests rely on it) and `t == start_epoch` is
  allowed.
- Clock state: a rewind keeps today's semantics — it re-anchors the lazy clock at the rewound time
  and leaves the running/paused state as it was (`SessionManager.rewind_to` already does this).
  The defect was the target, not the re-anchoring. Whether a rewind should also pause the clock is a
  behaviour change, not a bug fix; it is not decided here (see Design Decision 4).

After this package: palette "rewind to start" and the toolbar Rewind land on `start_epoch` in well
under a second on the sample vignettes; an out-of-range `t` is a 400 with nothing changed; the next
save is the size of a save at the start.

### Part B — seat checks on `roles/assign` and `observer/view` (VR-1072 F1, Low)

**Reproduction.** `POST /api/sessions/{sid}/roles/assign` and `.../observer/view` are named in
`FR-4320` ("assign seats", "designate the Observer") but refuse only through the **body** `cell`,
inside the session layer, returning HTTP 200 with `ok:false`. They ignore the query seat, so a
request with `cell=white` in the body and `?cell=blue` in the query is accepted; the refusal is not
a 403 like the other 18 guarded routes. The `assign_role` docstring (`server.py`, about line 380)
says the White-only check "already excludes" other seats, but the route has no check of its own.

After this package both routes call `_require_white` on the **query** seat first: 403 for blue, red,
observer, or no seat; the existing session-layer check stays as defence in depth.

## Requirements Covered

| ID | How |
|---|---|
| `FR-4310` | Rewind is a White-only clock control whose target must lie in the exercise's span; "rewind" never moves the clock out of it. |
| `FR-4320` | `roles/assign` and `observer/view` refuse any request not naming the white seat, with 403, like the rest of the list. |
| `NFR-1600` | An out-of-range rewind target is a 400 with a reason, not an accepted request that damages the session. |

All three are in FS-106's Requirements Implemented list; none added, none dropped. (No requirement
leaf states a rewind range; the range is derived from `FR-4310` plus the AAR/ephemeris span the
requirements `FR-7330`/`FR-7410` already fix. Routed upstream as a recommendation, below. It does
not block.)

## Architecture Components

- **C2 Session Layer**: `SessionManager.rewind_to` (range check), `SessionManager.clock_state`
  (additive `start_epoch`), `InProcessSession.rewind_to` (turns the refusal into `Ack(ok=False)`).
- **C4 Operator Console / HTTP**: `ui_web/server.py` (`rewind` route maps a refusal to 400;
  `roles/assign`, `observer/view` call `_require_white`), `ui_web/static/app.js` (rewind-to-start
  target).
- Engine untouched: `Simulation.rewind_to` keeps its contract; the guard sits above it. Determinism
  and import guard unaffected. The guard raises before any state changes.

## Interfaces

- **INT-0002** (clock) `POST /api/sessions/{sid}/rewind`: `t` outside `[start_epoch, now]` → 400
  `detail` naming the span; in range unchanged.
- `GET /api/sessions/{sid}/clock` gains an additive field `start_epoch` (sim microseconds). Existing
  fields unchanged.
- `POST .../roles/assign`, `POST .../observer/view`: 403 for a non-white query seat. The body field
  `cell` remains accepted; the query seat is the authority (Decision 2).

### Design Decisions

1. **Guard in `SessionManager.rewind_to`, raise `ValueError`.** Every caller then benefits (the
   session API, tests, any future route). `InProcessSession.rewind_to` catches it and returns
   `Ack(ok=False, reason=...)` (the pattern the draft-session refusal there already uses); the route
   maps `ok=False` to 400, as `inject` does. The span is `[self.ctx.start_epoch, self.sim.clock.now]`.
   Check the existing in-tree callers (`test_planning.py`, `test_ssn.py`, `test_inject_library.py`,
   `test_pending_inject_queue.py`, `test_session.py`, `test_self_contained_save.py`,
   `test_condition_triggered_injects.py`, `test_session_features.py`): they must all pass unchanged;
   if one rewinds outside the span it is a finding, not a reason to weaken the guard.
2. **Body `cell` on the two seat routes is not authority.** Keep the field (no API break; the
   console and Creator send it) but do not let it decide: after `_require_white(query cell)`, pass
   `"white"` to the session layer. The session-layer check remains for in-process callers, so a
   caller bypassing HTTP is still refused. This resolves the "white in body, blue in query" case by
   the query seat alone, consistent with every other guarded route.
3. **The client learns the start from the server.** `start_epoch` is added to the clock state the
   console already polls, rather than being parsed from the vignette brief's UTC string. `app.js`
   keeps the latest value; both "rewind to start" call sites (palette item and toolbar `rewind`) use
   it. If the value is not yet known, the client reads `/clock` first and does not send a guess.
4. **Not decided here: auto-pause on rewind.** Facilitators may expect a rewound exercise to wait
   for them. That is a behaviour change to `FR-4310`'s clock model and is design work (it touches
   what "rewind" means to a running multi-tab session), so this package keeps the current semantics
   and records the question in the completion note for the owner. The package's tests pin the
   running/paused state as unchanged, so a later decision is a deliberate change.
5. **Docstrings are corrected.** The `assign_role` and `set_observer_view` route docstrings state
   what the route now does. The `rewind` docstring states the span.

## Files to Create

- `spacesim/tests/test_white_control_correctness.py` (HTTP and session-level tests for both parts).

## Files to Modify

Checked against the tree at `501b36d`:

- `spacesim/session/manager.py`: `rewind_to` (line 425: add the range check before `self.sim.rewind_to`);
  `clock_state` (line 414: add `start_epoch`).
- `spacesim/session/inprocess.py`: `rewind_to` (line 218: convert the `ValueError` to
  `Ack(ok=False, reason=...)`; keep the draft refusal first).
- `spacesim/ui_web/server.py`: `rewind` route (line 482: raise 400 on `ok=False`, docstring);
  `set_observer_view` (line 360) and `assign_role` (line 372): add `cell: Optional[str] = None` and
  `_require_white(cell)`, pass `"white"` onward; correct the docstring at about line 380.
- `spacesim/ui_web/static/app.js`: toolbar `rewind` (line 366: uses `t: 0`), palette item (line 2644:
  `rewindTo(0)`), and the place the clock state is polled/stored (find the `/clock` consumer; add the
  `start_epoch` read). Bookmark rewinds (`rewindTo(b.t)`, line 2558) keep their own `t`.
- Existing tests that call the two routes without a query seat (each gets `?cell=white`; no
  assertion weakened): `test_observer.py` (lines 44, 59, 67, 166, 177), `test_session_setup.py`
  (line 157), `test_vignette_creator_ui.py` (line 238), `test_white_only_controls.py` (lines
  167–170: this one asserts the old body-seat refusal for blue/red/observer and its expectation
  changes to 403 for a non-white query seat; update it and say so in the completion note).
  Re-derive the list with a search for `roles/assign` and `observer/view` at build time.
- `spacesim/tests/test_browser_console_rules.py`: one new browser case (below).

## Implementation Tasks

1. Mark the package `IN PROGRESS` (header, MBP row, `packages/INDEX.md`, `ROADMAP.md`).
2. Write the tests below. Part A cases 1–3 and 6 and Part B cases fail first (200 where 400/403).
3. Implement Part A: guard, conversion, route mapping, `start_epoch`; then `app.js`.
4. Implement Part B: the two guards and docstrings; update the existing tests' query seats.
5. Run the browser marker (`-m browser`) and the non-browser suite; both permanent gates; the doc
   integrity and origin tests; regenerate the RTM Test column.
6. Documentation updates; mark `COMPLETE`.

## Tests to Add

Module `test_white_control_correctness.py`, module marker `verifies("FR-4310", "FR-4320",
"NFR-1600")`; tag per test with the narrowest ID.

Part A (`FR-4310`, `NFR-1600`):

1. **t=0 refused.** On a started session, `POST /rewind?cell=white {"t":0}` → 400, `detail` names
   the allowed span; sim time, eventlog length and clock running state identical before and after.
   (Fails first: 200.)
2. **Before start and after now refused.** `start_epoch - 1` and `now + 1`: 400, nothing changed.
3. **Edges allowed.** `t == start_epoch` → 200, clock `now == start_epoch`, events after it gone;
   `t == now` → 200 no-op.
4. **Rewind to start is quick and small.** After advancing a few hundred sim seconds, rewind to
   `start_epoch` and save: the saved JSON is no larger than a fresh started session's save plus a
   small slack. A wall-time bound is not asserted (flaky); the size and the clock value stand in for
   the reported 15 s and 566 MB.
5. **Clock state unchanged by a rewind.** With the clock running, then paused: after an in-range
   rewind the running flag is as before, `clock_state()["now"] == t`, and a `catch_up` with a
   patched wall clock advances from `t`, never from a stale anchor.
6. **`start_epoch` exposed.** `GET /clock` includes `start_epoch == ctx.start_epoch`.
7. **Layering.** `SessionManager.rewind_to(out_of_range)` raises `ValueError`;
   `InProcessSession.rewind_to` returns `Ack(ok=False)` and a draft session is still refused first.
8. **Non-white and non-integer.** A non-white seat is still 403 and a non-integer `t` still 422
   (unchanged behaviour, pinned so the guard's ordering is explicit).
9. **Browser (`-m browser`).** As White, choose "rewind to start" in the palette and press the
   toolbar Rewind: the intercepted request body's `t` equals the session's `start_epoch`, neither
   is 0, and no `pageerror` is raised. Fails first (sends 0).

Part B (`FR-4320`):

10. **Refusal by query seat.** For each of `roles/assign` and `observer/view`: blue, red, observer
    and no seat → 403; the staffing report and the observer designation unchanged afterward.
    (Fails first: 200 with `ok:false`.)
11. **Mismatched seats.** Body `white`, query `blue` → 403 (the reported hole). Body `blue`, query
    `white` → 200 and applied (Decision 2).
12. **White succeeds.** Both routes with `?cell=white` → 200, `ok:true`, effect visible
    (assignment in the staffing report; designation served by `GET observer/view`).
13. **Defence in depth.** `InProcessSession.assign_role` / `set_observer_view` called directly with
    a non-white `cell` still return `ok:false` (existing behaviour, pinned).

## Documentation Updates

- `CLAUDE.md`: the `ui_web/` code-map bullet and trust-model sentence list `roles/assign` and
  `observer/view` among the 403-guarded routes; the rewind range and `start_epoch` clock field in
  the `session/` bullet. (Same upkeep `IP-1072` did.)
- `docs/training/` API reference and the White Cell manual's clock section: rewind is bounded to the
  exercise and "rewind to start" means the vignette start; the 403 for seat routes. Check
  `docs/training/15-manual-traceability.md` §15.1 for the sections to touch; if the owner
  (`08-training-manual-authoring`) must do them, list them in the completion note.
- RTM Test column regenerated, never hand edited; `FS-106` `Referenced By`; MBP row and tally,
  `packages/INDEX.md`, `ROADMAP.md`, this header.
- Not edited here (other owners): `FR-4320` Notes and GDS-09 §4/OQ1 wording (`BL-0365`).

## Definition of Done

- All Part A and Part B tests exist, were seen failing first, and pass; browser case ran in Chromium.
- A rewind outside `[start_epoch, now]` is a 400 with nothing changed; "rewind to start" lands on
  `start_epoch`; the next save is start-sized.
- `roles/assign` and `observer/view` give 403 for any non-white query seat; success unchanged.
- No existing assertion weakened; every changed existing test edit is a query seat or the one
  documented expectation.
- Full suite (both markers) and both permanent gates green; RTM regenerated.
- `git diff --stat` shows only the files named above and docs.
- Completion note records Decision 4's open question; status `COMPLETE`.

## Verification Checklist

1. Re-derive the mutating-route table from the live app: no `FR-4320`-listed route lacks a
   `_require_white` on the query seat.
2. Drive the real server: advance a started session, rewind to 0 (400), rewind to the start (200,
   fast, `GET /save` small); repeat from the console palette in Chromium.
3. Mutations in a scratch copy: remove the range check; remove either seat guard; revert the
   client to `t: 0`: each fails at least one test.
4. `Simulation.rewind_to` and `engine/` are unchanged (`git diff` over `spacesim/engine/` empty).
5. All eight existing in-tree `rewind_to` callers pass unchanged.
6. Full suite, `-m browser`, `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`,
   `test_test_origins.py` green.

## Dependencies

`IP-1068`, `IP-1072`, `IP-1073` (all `VERIFIED`). Ordering: build **after `IP-1103`** (both edit
`session/manager.py` and `ui_web/server.py`, in different regions; sequencing avoids a merge
conflict) and **before `IP-1335` and `IP-1334`** (which retag decorators in tests this package
edits).

## Risks

- **Existing callers rewinding outside the span.** Mitigated by Decision 1 and checklist item 5.
- **Hidden reliance on `rewind(0)`.** The toolbar `rewind` and the palette are the only client
  callers found; a search for `"/rewind"` in `static/`, `tools/` and `.claude/skills/` at build time
  confirms it.
- **Query-seat authority changes existing curl recipes.** `training/` and `run-spacesim` recipes that
  call the two routes without `?cell=white` now get 403; the build searches them and fixes the
  recipes or notes the owner.
- **Auto-pause question** is deferred, not decided (Decision 4).

## Rollback Considerations

Revert the commit. The additive `start_epoch` clock field and the 400/403 mappings are the only
interface changes; no stored data changes.
