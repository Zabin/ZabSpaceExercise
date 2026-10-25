# IP-1087 — A Pending-Approval Order Is Still Decidable After Save and Resume (FR-3430, FR-7210, FR-7220)

> **Package ID:** IP-1087
> **Version:** 1.0
> **Status:** READY — authored 2026-10-25 by `07-implementation-planning` (release-push remediation pass 8). Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive, recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256 (fix bugs before release; no new features) and the run #262 go-ahead, covers it: finding `M-2` of the unreviewed-packages integration review is a bug in the interaction of two `VERIFIED` packages. Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** [IP-1270](IP-1270-effect-authorization-gating-and-live-roe.md), [IP-1101](IP-1101-self-contained-saves.md), [IP-1102](IP-1102-save-load-robustness.md), [IP-1103](IP-1103-save-validation-completion.md) (all `VERIFIED`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md), [`01-technical-work-breakdown.md`](../01-technical-work-breakdown.md) ("Release-push remediation, pass 8"); source: [`integration-review-unreviewed-packages.md`](../../reviews/integration-review-unreviewed-packages.md) `M-2`.
> **Produces:** a resumed session whose gated orders are decidable exactly as in the session that was saved; a recorded warning (not a 500, not a silent zombie) for a pending order whose gate cannot be reconstructed.
> **Feature Reference:** [FS-127 — Effect Authorization Gating and Live ROE](../../features/FS-127-effect-authorization-gating-and-live-roe.md) (`FR-3430`); [FS-110 — Save and Resume](../../features/FS-110-save-and-resume.md) (`FR-7210`, `FR-7220`)
> **Related Topics:** [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py), [`spacesim/session/manager.py`](../../../spacesim/session/manager.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Bug-fix package (one defect, one seam). Prose only; no code in this document.*

---

## Package ID

IP-1087.

## Title

Rebuild the pending-approval map from the saved order registry and the event log when a session is resumed.

## Objective

**The defect (review `M-2`, Medium; reproduced read-only over HTTP in the planning pass).** `SessionManager.save_state` (`session/manager.py`, line 1100) persists the order registry (`"orders": [vars(o) …]`), including an order whose `status` is `"pending_approval"`. `from_state` (line 1256) rebuilds that registry (`Order(**od)`) after `_rebind()`, but `OrderSystem._pending` (`engine/orders.py`, line 244), the map `decide_gated_order` (line 325) consults, is cleared by `_rebind` (line 572) and never rebuilt. Reproduced: a vignette declaring `effect_gating_rules: [{action_type: jam, required_role: white}]`, Red issues a jam (`status: pending_approval`), `GET /save`, `POST /load_save`: the loaded session lists `ord-1 pending_approval`, `POST /gate/decide` returns `{"ok": false, "reason": "no_such_pending_order"}`; the same call on the original session succeeds. The order is a permanent zombie (cancel is the only exit), and `FR-7220`'s "resume is exact" does not hold for gated exercises.

**What the requirements say (the question the directive asked).** `FR-3430`: "the order does not execute until the designated controller role records an approval decision; the `EventLog` shows the request, the decision, and the elapsed time". An order that was awaiting a decision when the session was saved is still awaiting it; nothing in `FR-3430` ends the wait at a save. `FR-7210`/`FR-7220` make resume exact (the save carries the vignette as loaded and the replay baseline, and the order registry and pending events are persisted so queued orders survive). The **event log is the source of truth**: it already holds the `effect_gate_request` entry (with `order_id`, `required_role`, `action_type`) for every pending order and an `effect_gate_decision` entry for every decided one. No new persisted field is needed.

**What is not changed.** `IP-1270` Design Decision 2 records that a rewind or undo discards pending-approval orders (the request entry survives in the log while the order registry is cleared by `_rebind`); that is a recorded design decision about *time travel*, distinct from a *resume of the same moment*, and is kept. The save format, the event-log record shapes and `validate_save` are unchanged.

## Requirements Covered

| ID | How |
|---|---|
| `FR-3430` | An order held for a controller decision stays held across a save and resume, and the decision (approve resumes planning; deny rejects with `gate_denied`) is logged with the elapsed time measured from the original request. |
| `FR-7210` | The saved session resumes to the saved state: the registry's pending orders are decidable again. |
| `FR-7220` | Resume is exact for gated exercises (the review's point). |
| `NFR-1600` | A corrupt or edited save (a pending order with no request entry, a gating rule no longer in the content) loads with a recorded warning and a defined order state, never a 500 and never a silent zombie. |
| `ADR-0002` (determinism) | The rebuilt map is a pure function of the restored registry, the restored event log and the content's gating rules; replay equals live after a resumed decision. |

## Architecture Components

`engine/orders.py::OrderSystem` gains one method that rebuilds `_pending` (for example `rebuild_pending()`), reusing `_matching_gate` (line 314) and scanning `self.sim.eventlog.entries` for `effect_gate_request` / `effect_gate_decision` the way `decide_gated_order` already scans for the request time. `session/manager.py::SessionManager.from_state` calls it once, after the order registry is restored and before the method returns, and appends any warning to `load_warnings`. Load-bearing invariants: deterministic core (the method reads restored state and the log, mutates only `_pending` and an unreconstructable order's own `status`/`fail_reason`; no clock, no RNG, no eventlog append); the engine import boundary (no new imports); fog-of-war unaffected (`/orders/{cell}` already filters by cell).

## Interfaces

- No route, request or response shape changes. `POST /load_save` already returns `{session, warnings}`; a new warning string appears there when a pending order cannot be rebuilt.
- `OrderSystem.rebuild_pending()` (internal): for every restored order with `status == "pending_approval"`, find its **last** `effect_gate_request` entry and require no `effect_gate_decision` for the same `order_id` after it, resolve the matching gate rule with `_matching_gate(order)`, and register `_pending[order.id] = (order, rule)`. An order that cannot be rebuilt (no request entry; a decision already logged; no rule matches the restored content) is set to `status = "rejected"`, `fail_reason = "gate_lost_on_resume"`, and one warning naming the order id and the cause is returned for `load_warnings`.

### Design Decisions

1. **Derive, do not persist.** The registry already carries the order and the log already carries the request; a second persisted copy of the pending map would be a second source of truth that could disagree with the log (the failure mode `IP-1270` Decision 2 and `FR-7220` both guard against). The map is derived at load from the two authoritative records.
2. **Pending state is recoverable only where the log says so.** The request entry is the proof that an order was held. An order marked `pending_approval` with no request entry cannot have come from this engine (a hand-edited or corrupt save); it is rejected with a reason and a warning rather than invented into a decidable state.
3. **The rule is re-matched, not stored.** `_matching_gate` is a pure function of the order and the content's gating rules, and the content portion of a self-contained save (`IP-1101`) carries those rules, so the re-matched rule equals the original. If the content changed (a legacy save resumed against an edited vignette file), no rule may match; that is the "gate lost" case above and is warned, which is also the correct behaviour for the legacy-save caveat `IP-1101` already warns about.
4. **A decision after resume is an ordinary decision.** `decide_gated_order` is unchanged: it logs `effect_gate_decision` with `elapsed_us` computed from the original request entry (so the elapsed time spans the save), then continues planning (`_continue_plan`) or rejects. After approval the order is scheduled like any queued order, and the next save carries it in the persisted pending-event list as today.
5. **`_rebind` and rewind are untouched.** `from_state` calls `_rebind()` once as it does today; the new method runs after the registry restore, not inside `_rebind`, so a rewind or undo still discards pending orders by `IP-1270` Decision 2. A test pins that: resume, then rewind, discards them.
6. **Ordering against `IP-1160` and `IP-1083`.** `IP-1160` (role-scoped commands) may add fields to `Order` that `vars(o)` persists; the rebuild must not drop them (a round-trip test over the whole `Order` is part of the matrix). `IP-1083` (rewind keeps future-dated White injects) edits the rewind path in `manager.py`; this package builds after it if both are in flight, because both touch `_rebind`'s neighbourhood. Neither is a semantic dependency.
7. **The cheap Low `L-1` is not folded in.** `POST /roe/change` answers a non-White seat with HTTP 200 `{"ok": false, "reason": "not_controller"}` rather than the 403 every other White control returns; changing a verified response contract needs its own pinned-test updates and an owner view of the console's reading of it, so it is listed in the completion note, not built here.

## Files to Create

- `spacesim/tests/test_gated_order_resume.py` — the matrix below (a new file avoids touching pinned rows in `test_origin_retag.py`).

## Files to Modify

- `spacesim/engine/orders.py` — the rebuild method on `OrderSystem`.
- `spacesim/session/manager.py` — `from_state`: call it after the order registry is restored; append its warnings to `load_warnings`.
- `CLAUDE.md` — one sentence in the `orders.py` and `manager.py` code-map entries (doc step).
- `docs/requirements/03-requirements-traceability-matrix.md` — Test column regenerated (generated, never hand edited).

## Implementation Tasks

1. Test-first: write the matrix; confirm the resume-then-decide cases fail on the parent (`no_such_pending_order`) and the cases that must not change (rewind discards; non-gated orders; decided orders) pass.
2. Add the method on `OrderSystem` and the single call in `from_state`; confirm the legacy-save branch (no `save_format`) takes the same path.
3. Add the warning cases (no request entry, rule gone) and check the `load_save` route returns them in `warnings`.
4. Run the new tests, `test_orders.py` and the other `IP-1270` gating tests, `test_save_load_robustness.py`, `test_self_contained_save.py`, `test_session_features.py`, `test_web.py`, `test_white_only_controls.py`, `test_determinism.py`, `test_import_guard.py`, then the full suite; regenerate the RTM Test column in the same commit.
5. Doc step; run `test_doc_integrity.py` and `test_test_origins.py`.

## Tests to Add

All through the HTTP `TestClient` (`POST /api/sessions` on an external-directory vignette declaring `effect_gating_rules`, `POST /order`, `GET /save`, `POST /load_save`, `POST /gate/decide`, `GET /orders/{cell}`) unless marked engine-level. Each carries `@pytest.mark.verifies(...)` with the leaf shown.

**Resume then decide (`FR-3430`, `FR-7220`).**
1. The review's reproduction: gated Red jam pending, save, load, `POST /gate/decide` by the required role with `approve: true` is `ok: true`; the order becomes `queued`, executes in its window and its effect applies; the decision entry in the loaded session's log carries `elapsed_us` measured from the original request (greater than the sim time advanced after the load).
2. Deny after resume: `approve: false` gives `rejected`/`gate_denied`; nothing is scheduled.
3. Wrong role after resume: `not_controller` (the rule's role, not the caller, decides), order still pending.
4. Two pending orders (a gated jam and a gated engage, different rules): one decided before the save, one after; on load only the undecided one is decidable; the decided one answers `no_such_pending_order`.
5. Decided before save: an order approved and queued before the save is not pending after load (status `queued`, no zombie), and a second decision is `no_such_pending_order`.
6. Save, load, save, load (twice): the pending order is still decidable.
7. Legacy-format save (no `save_format`) with a pending order: decidable after load.
8. Order registry round trip: every field of a restored pending `Order` equals the original (guards against `IP-1160` adding a field the rebuild drops).

**Unreconstructable gates (`NFR-1600`).**
9. A save edited so a `pending_approval` order has no `effect_gate_request` entry: load succeeds (200) with a warning naming the order; the order is `rejected`/`gate_lost_on_resume`; no 500.
10. A legacy save resumed against a vignette file whose gating rule was removed: load succeeds with the warning; the order is `rejected`/`gate_lost_on_resume`.
11. A save with an order `pending_approval` and a later `effect_gate_decision` entry for it (inconsistent): rejected with the warning, not re-opened.

**Unchanged behaviour (`FR-3430`, `IP-1270` Decision 2).**
12. Rewind (and undo) after a resume discards pending orders exactly as on a never-saved session.
13. A session with no gating rules: `from_state` rebuilds nothing, adds no warning, and its event log and order list are byte-equal to the parent commit's for the same save.

**Determinism (`ADR-0002`).**
14. After resume and a decision, replay equals live (`world.model_dump_json()` against `sim.replay()`), and a save taken after the decision loads to the same state.

About 14 test functions (several parametrised).

## Documentation Updates

- `CLAUDE.md` code map: `OrderSystem.rebuild_pending()` and its `from_state` call, one sentence each.
- Not written by this package: an `FR-3430`/`FR-7220` Note that pending orders survive a resume while a rewind discards them (routed to `04-requirements-engineering`); the White manual's gating text (via `15-manual-traceability.md` §15.1 to `08-training-manual-authoring`); the missing console Approve/Deny control (`M-5`, feature work, excluded).
- `docs/implementation/00-master-build-plan.md`, `packages/INDEX.md`, the TWBS: written in this planning pass.

## Definition of Done

- A gated order pending at save time is decidable after load, with the elapsed time measured from the original request; a decided or unreconstructable order is never presented as decidable.
- An unreconstructable pending order is rejected with a reason and a load warning, never a 500.
- Rewind and undo still discard pending orders; sessions with no gating rules are byte-unchanged.
- New tests green; RTM Test column regenerated in the same commit; full suite, `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`, `test_test_origins.py` green; no allow-list grew.

## Verification Checklist

- [ ] Re-derive `M-2` on the parent commit (`no_such_pending_order` after load) and on this commit (decidable).
- [ ] The verifier re-reads `save_state`/`from_state`/`_rebind` in the tree to confirm the order of restore, `_rebind` and the new call, and that no new persisted key was added to the save.
- [ ] The decision entry's `elapsed_us` spans the save.
- [ ] Rewind-after-resume still discards pending orders.
- [ ] The three unreconstructable cases warn and reject; none 500.
- [ ] Permanent gates and documentation checks green.

## Dependencies

All `VERIFIED`: `IP-1270`, `IP-1101`, `IP-1102`, `IP-1103`. Edits `engine/orders.py` (build after `IP-1085`) and `session/manager.py` (build after `IP-1084` and `IP-1086`). Does not edit `server.py`. Build after `IP-1083` if that is in flight (same neighbourhood as `_rebind`); `IP-1160` is independent (see Design Decision 6).

## Risks

- **Rule re-match on a legacy save.** Design Decision 3: warned, not guessed.
- **An `Order` field added by `IP-1160`.** Pinned by test 8.
- **The warning list reaches the console only through `load_save`'s existing `warnings` field.** The console already shows those; no change.
- **Pending orders and the `MAX_LIVE_SESSIONS` eviction.** An evicted live session is lost whole (not saved); unchanged and out of scope.

## Rollback Considerations

Revert the commit. A resumed gated session returns to listing pending orders it cannot decide (the defect returns). No save format or event-log record changes, so a save written under this package loads on the parent unchanged.
