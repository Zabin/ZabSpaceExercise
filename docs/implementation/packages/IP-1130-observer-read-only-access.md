# IP-1130 — Observer Read-Only Access

> **Package ID:** IP-1130
> **Version:** 1.1 (2026-07-03 — implemented by `08-code-implementation`; see Status below.)
> **Status:** 🔵 COMPLETE *(implemented 2026-07-03 — a fourth, White-Cell-designated read-only seat.
> `_reject_observer(cell)` guards all 22 mutating routes (re-derived from the live route table at
> implementation time per this package's own Risks note, not merely the 20 explicitly enumerated
> below — the additional route is `/preview/consequence`, the same "preview/compute" class already
> included); `get_observer_view`/`observer_designation` dispatch unmodified to `get_godview`/
> `get_view`. Full suite green (547 passed/3 skipped, up from 519/3 — 28 new tests), both permanent
> gates green. Entered `COMPLETE`, not `VERIFIED` — only `09-package-verification` may write
> `VERIFIED`. Was 🟡 READY *(authorized, no blocking package dependency — the fog-of-war filter this
> package reuses is already shipped and exercised by every `VERIFIED` as-built package in this plan.
> **MSTR-006 §3 authorization obtained 2026-07-03** (project owner, recorded in
> `docs/pipeline/pipeline-journal.md` run #2).)*)*
> **Dependencies:** FS-113 (no `FS-xxx`/`IP-xxxx` hard prerequisite — see Dependencies below)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** the read-only Observer seat interaction model
> **Feature Reference:** [FS-113 — Observer Read-Only Access](../../features/FS-113-observer-read-only-access.md)
> **Supersedes:** none — new package, first Implementation Package written against FS-113
> **Related Topics:** [`spacesim/session/api.py`](../../../spacesim/session/api.py),
> [`spacesim/session/cells.py`](../../../spacesim/session/cells.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py),
> [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*This package was authored after `07-implementation-planning`'s required build-status verification
pass (`docs/implementation/01-technical-work-breakdown.md` Tranche 1) confirmed FS-113 is **not
built at all**: no "observer" seat/role concept exists anywhere in `session/`, `ui_web/server.py`,
or `ui_web/static/app.js` — the cell selector is a fixed White/Blue/Red set
(`ui_web/static/app.js:406` `setCell`, `index.html:2013` `.cell` buttons). This is a genuinely
forward-looking design, not a documentation pass.*

## Package ID

IP-1130

## Title

Observer Read-Only Access

## Objective

Add a fourth, White-Cell-designated seat kind — Observer — whose session can only read (god-view or
a specific cell's fog-of-war-filtered `CellView`, as White Cell designates) and can never mutate
`WorldState`, with the rejection enforced at the `SessionAPI`/`ui_web/server.py` boundary rather
than merely by omitting the option from the UI.

> **This was authored as a forward-design package: the capability did not exist in `spacesim/` at
> authoring time.** Per MSTR-006 §3, this document's own specification was not itself an
> authorization to write code — that separate, explicit user go-ahead was obtained 2026-07-03 (see
> the Status field above), and `08-code-implementation` has since implemented the tasks below
> (2026-07-03, see Status).

## Feature Reference

[FS-113 — Observer Read-Only Access](../../features/FS-113-observer-read-only-access.md)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-6510 | Observer read-only view with no command ability | Introduces an Observer seat kind whose view is White-Cell-designated (god-view or a named cell's `CellController.view()` output, reused unmodified) and whose every mutating request — order issuance, sensor tasking, inject firing, clock control, etc. — is rejected at the server boundary independent of what the UI offers, per the "structural rejection, not UI-only restriction" language in FS-113's own System Behaviour. |

## Architecture Components

- **C2 Session / Application Layer** — `session/api.py` (`SessionAPI` protocol gains an
  Observer-aware read path), `session/cells.py` (`CellController.view()` reused unmodified for the
  cell-view-designation case).
- **C4 Operator Console** — `ui_web/server.py` (the enforcement point: every mutating route
  rejects an Observer-seated session before touching `SessionManager`), `ui_web/static/app.js`
  (adds "Observer" as a selectable seat, hides/disables command controls when seated as Observer —
  a UX convenience, not the enforcement mechanism).
- **C9 Observer** — the new actor this package introduces, per
  `docs/architecture/02-system-context.md` §2 row 5's existing Observer actor entry (already named
  in the architecture, not yet realized in code).

## Interfaces

**INT-0005** (Observer ↔ Operator Console) — the Observer's own interaction surface, not yet
implemented; this package is what implements it. **INT-0006** (Operator Console → Session Layer,
the `SessionAPI` seam) — the path every attempted mutating request from an Observer-seated session
routes through before being rejected.

## Files to Create

None proposed — this capability is small enough to fit as additions to existing files, not a new
module (mirrors `IP-2010`'s own restraint principle of not creating structure the design doesn't
need).

## Files to Modify

- `spacesim/session/api.py` *(proposed)* — a `get_observer_view(session, designation)` method (or
  equivalent) on the `SessionAPI` protocol, where `designation` is either `"godview"` or a cell
  name; internally dispatches to the existing `get_godview`/`get_view` methods unmodified.
- `spacesim/session/manager.py` or `session/inprocess.py` *(proposed)* — a per-session Observer
  view-designation field, settable only by a White-Cell-seated request, read by the new
  `get_observer_view` path.
- `spacesim/ui_web/server.py` *(proposed)* — (a) a White-Cell-only endpoint to set an Observer's
  view designation; (b) an Observer-facing read endpoint dispatching to
  `get_observer_view`/`CellController.view()`; (c) a guard at the top of every existing mutating
  route (`/order`, `/order/validate`, `/step`, `/advance`, `/rewind`, `/undo`, `/inject`,
  `/force/tle`, `/red_step`, `/maneuver/compute`, `/jam/compute`, `/engage/compute`,
  `/cyber/compute`, `/sigint/compute`, `/cancel`, `/recovery/{cell}/{asset}`,
  `/ssn/{cell}/request`, `/ssn/{cell}/cancel`, `/clock`, `/param`, `/start` — the full list at
  `ui_web/server.py:201-410`) rejecting any request whose caller is seated as Observer, before the
  request reaches `SessionManager`.
- `spacesim/ui_web/static/app.js` *(proposed)* — add "Observer" to the seat/cell selector
  (`app.js:406` `setCell` and the `.cell` button wiring at `index.html:2013`); when seated as
  Observer, disable/hide command-issuing controls (UX only — the actual rejection happens
  server-side per the point above, since a request bypassing the UI must be rejected identically).

## Implementation Tasks

**Not started — authorized (MSTR-006 §3, 2026-07-03).** The following is the proposed task
sequence for `08-code-implementation`:

1. Add an Observer view-designation concept (god-view or a named cell) to session state, settable
   only by a White-Cell-seated caller.
2. Implement the Observer read path by dispatching to the existing, unmodified `get_godview`/
   `CellController.view()` — no new fog-of-war logic; Observer access to a cell's view must be
   pixel-identical to that cell's own operator's view (FS-113's own System Behaviour requirement).
3. Add the server-side mutation-rejection guard to every existing mutating route, keyed on the
   caller's seat being Observer — this must hold even for a request that never goes through the
   `ui_web/static/` client (FS-113's Security Considerations: "must hold even against a request
   that bypasses the UI entirely").
4. Add "Observer" as a selectable seat client-side and disable/hide command controls when seated as
   Observer (convenience layer over the server-side guarantee from task 3, not a substitute for it).
5. **Explicitly do not implement** in this package: CR-06 (mid-exercise Observer reassignment, an
   unbaselined candidate requirement per FS-113's own Open Questions) or a `docs/domains/`
   framework document for Observer (a documentation-tier gap FS-113 itself flags, out of this
   package's scope).

**Implementation notes (2026-07-03, added by `08-code-implementation`):**

- **The 20-route list in "Files to Modify" was a subset, per this package's own Risks section's
  explicit instruction to re-derive the current route table rather than trust it.** The shipped
  guard covers 22 mutating routes — the same 20 plus `/preview/consequence` (a political-cost
  preview endpoint, the same "compute/preview" class as the five `*/compute` routes already listed,
  simply not yet present or overlooked when this document was authored).
- **The mechanism "whose caller is seated as Observer" needed a concrete design this package left
  open.** Several of the 22 routes (`/clock`, `/param`, `/start`, `/step`, `/advance`, `/rewind`,
  `/undo`, `/inject`, `/force/tle`, `/red_step`) carry no `cell`-identifying field at all today
  (`OrderRequest` and friends do; these don't). The shipped design: `app.js`'s `api.post()` wrapper
  now attaches the caller's own current seat as a `cell` query parameter to *every* POST call
  (one centralized change, not touching each of the ~30 individual call sites), and each of those
  10 routes gained a matching `cell: Optional[str] = None` parameter read by the new
  `_reject_observer(cell)` helper; the other 12 routes already carry `cell` (body field or path
  param) and use that value directly — no query param needed, no duplication.
- **The Observer read path returns the resolved view directly (`GET /observer/view`, dispatching
  unmodified to `get_godview`/`get_view` per Task 2), but the client fetches a separate, tiny
  `GET /observer/designation` first** (`{"designation": "godview"|"blue"|"red"}`) and then calls
  the exact same `/godview` or `/view/{cell}` endpoint every other seat already calls — rather than
  parsing a merged response shape whose structure would depend on which was designated. This keeps
  the client's parsing code identical to what it already had for White/Blue/Red (no third, forked
  parsing path), which is the same "no parallel implementation" principle Task 2 itself states for
  the server-side read path, just carried one layer further to the client.

## Tests to Add

*(Proposed — none exist yet; write test-first per `CLAUDE.md`'s mandatory workflow once
authorized.)*

- `spacesim/tests/test_observer.py` *(new)* — one test per Acceptance Criterion:
  - Given White Cell designates an Observer's view as a specific cell, the Observer's session
    receives exactly that cell's `CellView` (byte-for-byte identical to what that cell's own
    operator would receive for the same request).
  - Given an Observer-seated session attempting to submit any command-kind or collection-kind
    action (order issuance, sensor tasking, clock control, inject firing), the request is rejected
    and no `WorldState` change occurs — parametrized across every mutating route this package's
    Files to Modify section lists, not just one representative endpoint.
  - Given an Observer-seated session attempting a mutating request that bypasses whatever
    client-side disabling exists (i.e. calling the server route directly), the same rejection
    applies — this is the test that actually exercises the "structural rejection, not UI-only"
    requirement.

## Documentation Updates

- `ROADMAP.md` Implementation Packages theme — add this package's row.
- `CLAUDE.md`'s Code Map — **implementation revealed a substantial-enough new capability (a fourth
  seat kind + a guard spanning 22 routes) to warrant a brief addition**, added under
  `session/inprocess.py` and `ui_web/server.py`'s existing entries plus the LAN trust model note
  (deviating from this field's original "no addition needed" — that clause's own escape valve).
- `docs/features/FS-113-observer-read-only-access.md`'s `Referenced By` metadata — already present
  (added at authoring time; verified unchanged).

## Definition of Done

*(Implemented 2026-07-03 by `08-code-implementation` — every item below is now satisfied against
the shipped code and tests; `09-package-verification` independently re-confirms this before the
package may advance to `VERIFIED`.)*

- [x] **Explicit user authorization obtained** for this package's Implementation Tasks (MSTR-006
  §3, 2026-07-03, project owner, recorded in `docs/pipeline/pipeline-journal.md` run #2).
- [x] An Observer's designated view (god-view or a named cell) is served identically to how that
  view is already served to its native audience (White Cell for god-view, the cell's own operator
  for a `CellView`) — no divergent code path, no divergent filtering (`get_observer_view` calls
  `get_godview`/`get_view` directly, no new filtering logic).
- [x] Every existing mutating route rejects an Observer-seated caller, verified by a parametrized
  test covering the full, re-derived 22-route table (a superset of Files to Modify's own list —
  see Implementation Tasks note above), not a sample.
- [x] The rejection holds for a request that bypasses the client UI (direct route call) — the
  parametrized test itself calls raw HTTP routes with no JS/UI involved at all.
- [x] No `WorldState` mutation occurs from any Observer-seated request in any test scenario
  (verified via eventlog-length comparison before/after each rejected call).

## Verification Checklist

*(To be executed once implemented; not yet applicable.)*

- [ ] `spacesim/tests/test_observer.py` exists, covers every mutating route, and is green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green (this package must not
  introduce any code path that mutates `WorldState` for an Observer-seated request).
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green.
- [ ] Manual review confirms `get_observer_view`'s cell-view branch calls the same
  `CellController.view()` function every existing cell-scoped endpoint uses — no parallel/forked
  filtering implementation.
- [ ] FS-113's Acceptance Criteria are each traceable to a specific test.

## Dependencies

- **Upstream:** The fog-of-war filter (`session/cells.py` `CellController.view()`) and god-view
  (`get_godview`) mechanisms this package reuses are already shipped and exercised by multiple
  `VERIFIED` as-built packages in this plan (e.g. `IP-1030`, `IP-1040`) — not themselves
  represented as a standalone package (`FEAT-6200`, Fog-of-War Filtering at the Session Boundary,
  is a Feature Catalog entry with no `FS-xxx`/`IP-xxxx` of its own yet, per FS-113's own
  Dependencies field). This package has no blocking package-level dependency in this plan.
- **Downstream:** None in this pass.
- **Build-sequencing:** Independent of every other package in this tranche; could be built in
  parallel with `IP-1120`/`IP-1140`/`IP-1150`/`IP-1151` if all were authorized simultaneously.

## Risks

- **Authorization risk (resolved 2026-07-03):** MSTR-006 §3's explicit, separate user go-ahead is
  now on record in the pipeline journal, and the package has since been implemented (`COMPLETE`).
- **Enforcement-completeness risk (mitigated, but a standing maintenance obligation, not a one-time
  fix):** the value of this Feature is entirely in *no* mutating route being missed. The shipped
  test (`test_observer.py`'s parametrized `_MUTATING_ROUTES` table, re-derived from the live route
  table at implementation time — 22 routes, not the 20 originally enumerated) mitigates today's
  gap, but is not self-maintaining: a route added to `ui_web/server.py` after this package ships
  will not automatically appear in that table, and a route whose author forgets both the
  `_reject_observer(cell)` call *and*, for a cell-less route, the new `cell` query parameter
  reopens the exact gap FR-6510 exists to close. `10-integration-review` or a future maintenance
  pass should periodically re-diff the route table against the test table.
- **LAN trust model interaction:** per `CLAUDE.md`'s documented LAN trust model, the cell/seat
  selector is client-side trust with no per-seat authentication — an Observer's *read* access to a
  cell's belief state already has the same LAN-trust caveat every other cell-scoped endpoint has
  (a hostile LAN participant could read Blue's view by requesting it, Observer-seated or not, per
  `CLAUDE.md`'s documented trust boundary). This package does not change that trust model, and
  should not be read as introducing a new one — it only adds the *write*-rejection Observer needs.
- **RTM title-mismatch, routed upstream, not fixed here:** `docs/requirements/03-requirements-
  traceability-matrix.md` row for `FR-6510` currently lists its Title column as "Multi-monitor
  pop-out windows" — a copy/paste defect (the correct title, "Observer read-only view with no
  command ability," is what `docs/requirements/01-functional-requirements.md:1170` — the RTM's own
  source of truth — states). This does not block authoring this package, but is flagged for
  whoever next touches the RTM (`04-requirements-engineering`'s territory).

## Rollback Considerations

Rollback surface: the new Observer-designation field, the new/modified endpoints, and the
per-route guard additions. Removing the guard additions reverts every route to its current
behavior; no existing seat's (White/Blue/Red) behavior is touched by this package, so rollback
carries no risk to any already-`VERIFIED` capability. No save-file or eventlog schema is touched.
