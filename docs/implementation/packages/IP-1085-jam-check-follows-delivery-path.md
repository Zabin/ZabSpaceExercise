# IP-1085 — A Jam Denies a Command Only on the Delivery Path It Actually Covers: Stored Programs Run, Relayed Commands Face the Crosslink (FR-1440)

> **Package ID:** IP-1085
> **Version:** 1.0
> **Status:** ✅ VERIFIED — authored 2026-10-25 by `07-implementation-planning`; implemented by `08-code-implementation`; verified by `09-package-verification` ([VR-1085](../verification/VR-1085-jam-check-follows-delivery-path.md)). Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive, recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256 (fix bugs before release; no new features) and the run #262 go-ahead, covers it: finding `H-2` of the unreviewed-packages integration review is a defect against `FR-1440`'s own Postcondition in a `VERIFIED` package. Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** [IP-1290](IP-1290-jamming-delivery-and-effect-detectability.md), [IP-1052](IP-1052-order-param-hardening.md), [IP-1250](IP-1250-maneuver-ledger.md) (all `VERIFIED`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md), [`01-technical-work-breakdown.md`](../01-technical-work-breakdown.md) ("Release-push remediation, pass 8"); source: [`integration-review-unreviewed-packages.md`](../../reviews/integration-review-unreviewed-packages.md) `H-2`.
> **Produces:** execution payloads for `maneuver` and `command` orders that carry the delivery path chosen at planning time, and one shared jam-denial rule for both handlers that consults the link that path actually uses; the stored-program counter to an uplink jam works as taught.
> **Feature Reference:** [FS-129 — Jamming Delivery and Effect Detectability](../../features/FS-129-jamming-delivery-and-effect-detectability.md) (`FR-1440`); [FS-102 — Command Scheduling](../../features/FS-102-command-scheduling.md) (the three delivery paths, `FR-3110`)
> **Related Topics:** [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py), [`spacesim/engine/effects.py`](../../../spacesim/engine/effects.py) (read-only reference: `is_link_denied`)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Bug-fix package (one defect, one seam). Prose only; no code in this document.*

---

## Package ID

IP-1085.

## Title

Make the uplink-jam check path-aware: a stored program is unaffected, a crosslink relay is judged against the crosslink.

## Objective

**The defect (review `H-2`, High; reproduced read-only over HTTP in the planning pass).** `OrderSystem._h_maneuver` (`engine/orders.py`, line 1090) and `_h_command` (line 1143) both test `is_link_denied(world, payload["actor"], world.now, link="uplink")` with no regard to the order's delivery path. Reproduced on `01-leo-isr-denial`: Red's `JAM-NORTH` jams `ISR-EO-1` with `link_target: "uplink"`; Blue queues a `maneuver` carrying `stored_at` at a time inside the jam window (the order is accepted, `delivery_path: "stored_program"`); at execution the log shows `execute_maneuver` with `applied: False` and `effect_log` reads `achieved: "jammed"`, the budget untouched. A stored program runs onboard and uses no uplink. `FR-1440`'s Postcondition is explicit: "A command whose delivery path is not covered by an active jam is unaffected". Its title and Inputs also name **crosslink** jamming, and no handler consults a crosslink jam: an `isl_relay` command is neither tested against `crosslink` nor exempt from `uplink`. The pre-planned stored program is the standard Blue counter to an uplink jam, so the defect removes the lesson the mechanic exists to teach.

**The three delivery paths and the link each uses (`_plan_command`, `engine/orders.py` line 466; paths named in `FR-3110`/`IP-1020`):**

| Path | Planned from | Link it depends on | Denied by |
|---|---|---|---|
| `ground_uplink` | a `command_uplink` window from the `via` station | the uplink | an active `uplink` jam on the actor |
| `isl_relay` | an `isl_link` window from a cell-owned `isl_capable` relay to the actor | the crosslink | an active `crosslink` jam on the actor or on the relay |
| `stored_program` | the `stored_at` instant on a `stored_program` asset | none (onboard) | nothing a link jam can do |

(`sensor_collect` and `cyber` orders are not commands and are untouched; `downlink` already checks the `downlink` link.)

## Requirements Covered

| ID | How |
|---|---|
| `FR-1440` | Postcondition: a command whose delivery path is not covered by an active jam is unaffected (stored program under an uplink jam; relayed command under an uplink-only jam); AC: a command whose path is covered fails at execute-time re-validation (ground uplink under an uplink jam; relayed command under a crosslink jam); no jam, executes normally. Crosslink jamming, named by the leaf and consulted by no handler today, is consulted. |
| `FR-3110` | The three delivery paths keep their planning behaviour; only the execution-time denial test changes. |
| `FR-3410` | The denial is still decided at execute-time re-validation. |
| `ADR-0002` (determinism) | The path is recorded in the execution payload, so the decision is a pure function of the logged payload and the world; replay equals live. |

## Architecture Components

`engine/orders.py`: `OrderSystem._plan_command` and `_exec_payload` (the maneuver and command payload builders, lines 758-980), `_h_maneuver`, `_h_command`, and one new private helper both handlers share. `engine/effects.py::is_link_denied` is read, not changed (it already scopes by `link`). Load-bearing invariants: deterministic core (the new payload keys are plain data; no clock or RNG; the helper reads `world.active_effects` as the current code does); the engine import boundary (no new import beyond what `orders.py` already uses); plan-first (planning still does not consult active jams; the jam is judged at execution, as today); the session/UI layers are untouched.

## Interfaces

- `execute_maneuver` and `execute_command` event payloads gain two additive keys: `delivery_path` (`ground_uplink` | `isl_relay` | `stored_program`) and `relay` (the relay asset id for `isl_relay`, otherwise absent or `None`). The path is derived from the planned `AccessWindow.channel` (`command_uplink`, `isl_link`, `stored`), which is known when the payload is built, before `order.delivery_path` is assigned; no `_exec_payload` signature change is required.
- The failure record appended to `world.effect_log` on a jam-denied command keeps `achieved: "jammed"` and `success: False` and gains an additive `path` key naming the path and the jammed link.
- No route, request or response shape changes (`GET /orders/{cell}` already shows `delivery_path`).

### Design Decisions

1. **Carry the path in the payload; do not re-derive it at execution.** At execution the handler has only the payload, and re-planning would consult windows that have since moved. The payload is the existing, logged record (`EventLog` replays it verbatim), so the decision is replay-exact.
2. **One shared rule, two handlers.** A private helper (for example `_delivery_jammed(world, payload)`) returns whether the payload's path is denied at `world.now`; `_h_maneuver` and `_h_command` call it in place of their inline `is_link_denied(... link="uplink")`. The rule: `stored_program` is never denied; `ground_uplink` is denied by an active `uplink` jam on the actor; `isl_relay` is denied by an active `crosslink` jam on the actor or on the named relay.
3. **A payload without the new keys behaves as before.** An event recorded or saved before this package has no `delivery_path`; the helper treats a missing key as `ground_uplink` (today's rule: an `uplink` jam on the actor). Replay of every existing log and save is therefore byte-identical; only newly planned orders gain the corrected behaviour. A scheduled-but-unexecuted event inside a pre-fix save keeps the old behaviour until it fires; recorded in Risks, not migrated.
4. **Crosslink on the relay as well as on the actor.** An `ActiveEffect` is keyed by the jammed asset id (`ActiveEffect.target`, `link_target`). A crosslink jam aimed at the relay breaks the relay's side of the path as surely as one aimed at the actor, so both are checked; a jam on an unrelated asset is not.
5. **Fail, do not delay.** `FR-1440` allows "fails or is delayed"; the as-built behaviour is fail, and `FR-3410`'s re-validation model has no retry. Unchanged.
6. **Footprint is a property of the jam, not of the check.** Whether a jam covers the actor is decided when the jam order resolves (`ModerateEffectResolver` only creates an `ActiveEffect` when the jam's access window and probability roll succeed); an off-footprint jammer's order is rejected with no window and creates no effect. The check here consults the resulting active effects only. The matrix includes an off-footprint jammer to pin that an out-of-reach jam never denies any path.
7. **Documentation of the lesson.** The Blue and Red manuals describe stored program as a delivery path without a caveat; after this package the path-versus-link table above is behaviour a manual should state. Routed to `08-training-manual-authoring` (manual-impact, `15-manual-traceability.md` §15.1 row for `FR-1440`); this package edits no `docs/training/` file.

## Files to Create

- `spacesim/tests/test_jam_delivery_paths.py` — the matrix below (a new file avoids touching pinned rows in `test_origin_retag.py`).

## Files to Modify

- `spacesim/engine/orders.py` — `_exec_payload` (maneuver and command branches: add `delivery_path`, `relay`), the shared denial helper, `_h_maneuver` and `_h_command` call sites, the `effect_log` failure record.
- `spacesim/tests/test_orders.py` — `test_maneuver_delivery_denied_by_active_uplink_jam_at_execute_time` (line 440) and its no-jam sibling build a ground-uplink order and still pass; the builder confirms and adds nothing else there.
- `CLAUDE.md` — one sentence in the `orders.py` code-map entry (doc step).
- `docs/requirements/03-requirements-traceability-matrix.md` — Test column regenerated (generated, never hand edited).

## Implementation Tasks

1. Test-first: write the matrix; confirm the stored-program-under-uplink-jam, relay-under-uplink-jam (must execute) and relay-under-crosslink-jam (must fail) cases fail on the parent, and the ground-uplink cases pass.
2. Thread `delivery_path` and `relay` into the two payloads from the planned window's channel and actor.
3. Add the shared helper and switch both handlers to it; keep the missing-key default.
4. Add the legacy-payload and replay tests.
5. Run the new tests, `test_orders.py`, `test_planning.py`, `test_order_param_hardening.py`, `test_effects.py`, `test_jam.py`, the AAR and replay tests, `test_determinism.py`, `test_import_guard.py`, then the full suite; regenerate the RTM Test column in the same commit.
6. Doc step; run `test_doc_integrity.py` and `test_test_origins.py`.

## Tests to Add

Engine-level cases use the fixtures the existing `test_orders.py` and `test_planning.py` already use (a LEO satellite, a ground station placed under it, an ISL-capable relay as in `test_command_delivered_via_isl_when_sooner_than_a_distant_ground_pass`); one HTTP regression reproduces the review. Each carries `@pytest.mark.verifies("FR-1440", ...)`.

**Matrix (`FR-1440`).** For both `maneuver` and `command` (one bus verb), across the three paths, assert the outcome (`applied`/`achieved`, delta-v or state change) for each jam condition. Paths x conditions:

| Path | no jam | uplink jam on actor | crosslink jam on actor | crosslink jam on relay | downlink jam on actor | jam on an unrelated asset |
|---|---|---|---|---|---|---|
| `ground_uplink` | executes | **fails** | executes | executes | executes | executes |
| `isl_relay` | executes | executes | **fails** | **fails** | executes | executes |
| `stored_program` | executes | executes | executes | executes | executes | executes |

1. The 18 cells above for `maneuver` and the 18 for `command` (parametrised), each also asserting the failure record's `achieved: "jammed"`/`success: False` where it fails and that delta-v and orbit (or the bus state) are untouched.
2. Timing: a jam that has expired before execution, and one that starts after, never denies any path (the window bounds in `is_link_denied` are inclusive of `start..end`; the test pins the boundary instants).
3. Footprint: a jammer too far from the actor to have a window (its order is rejected, no active effect) leaves every path unaffected; a jammer in reach with a failed probability roll (seeded) likewise.
4. `delivery_path` and `relay` appear in the logged `execute_maneuver`/`execute_command` payloads; `relay` is the relay asset id for `isl_relay` and absent otherwise.
5. Legacy payload: an `execute_maneuver` event scheduled by hand without the new keys, under an uplink jam, fails exactly as before (the missing-key default), and a recorded log containing such an event replays to a world equal to the original.
6. Replay equals live (`world.model_dump_json()` against `sim.replay()`) for a run containing one of each path under jams.
7. HTTP regression of the review: `01-leo-isr-denial`, Red jams `ISR-EO-1` uplink, Blue queues a `maneuver` with `stored_at` inside the jam window; after the step the maneuver is applied, delta-v is spent, and `effect_log` has no `jammed` entry for it. The same order with `via` a station fails as before.
8. `dry_run` (`POST /order/validate`) output unchanged for all three paths (planning does not consult jams).

About 8 test functions (the matrix parametrised, about 40 cases).

## Documentation Updates

- `CLAUDE.md` code map: `orders.py` entry, one sentence (path-aware jam denial; payload keys).
- Not written by this package: the Blue and Red manual text and `15-manual-traceability.md` §15.1 (routed to `08-training-manual-authoring`, Design Decision 7); `docs/requirements/` (the leaf already states the Postcondition the fix meets; the crosslink-relay target convention in Design Decision 4 is offered to `04` as a Note).
- `docs/implementation/00-master-build-plan.md`, `packages/INDEX.md`, the TWBS: written in this planning pass.

## Definition of Done

- A stored-program command is never denied by a link jam; a ground-uplink command is denied by an uplink jam and by no other link; a relayed command is denied by a crosslink jam on the actor or the relay and by no other link.
- Existing logs and saves replay byte-identically; new payloads carry the path.
- The review's reproduction passes as a permanent HTTP test.
- New tests green; RTM Test column regenerated in the same commit; full suite, `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`, `test_test_origins.py` green; no allow-list grew.

## Verification Checklist

- [ ] Re-derive `H-2` on the parent commit: the stored-program maneuver under an uplink jam logs `jammed`/`applied: False`; on this commit it applies and spends delta-v.
- [ ] Re-derive the crosslink gap on the parent: an `isl_relay` command under a `crosslink` jam executes (no handler consults it); on this commit it fails.
- [ ] The path table in this package is checked against `_plan_command` in the tree (the verifier re-reads the three branches), not copied.
- [ ] A payload without the new keys still behaves as the pre-fix rule; a pre-fix log replays equal.
- [ ] `engine/effects.py::is_link_denied` is byte-unchanged; planning and `dry_run` do not consult jams.
- [ ] Permanent gates, documentation checks green.

## Dependencies

All `VERIFIED`: `IP-1290`, `IP-1052`, `IP-1250`. Edits `engine/orders.py` only; no `manager.py`, no `server.py`. May run in parallel with `IP-1084` (disjoint files). Must precede `IP-1087` (shared file `engine/orders.py`). `IP-1160` also edits `engine/orders.py` (role scoping); the regions differ (planning/validation versus the execute handlers), so the merge is textual.

## Risks

- **A scheduled-but-unexecuted event inside a pre-fix save** has no `delivery_path` and keeps the old rule when it fires (Design Decision 3). Accepting this keeps replay of recorded history exact; a one-off migration would have to rewrite logged payloads, which the append-only log forbids.
- **The relay-jam convention** (Design Decision 4) is a modelling choice; if the owner prefers "crosslink jams only the actor", the relay clause is one line to drop and one matrix column to flip.
- **A vignette or tutorial that relied on the stored-program-is-jammed behaviour.** Unlikely (no shipped vignette sets a link-scoped uplink jam against a stored program), but the builder greps vignettes, `test_vignette_tutorials.py` and the playbooks for `link_target` and `stored_at` together and records the result.
- **Matrix size.** About 40 parametrised cases build small worlds; they must stay fast (engine-level, no HTTP except the regression).

## Rollback Considerations

Revert the commit. The handlers return to the uplink-only check (the defect returns); the two additive payload keys already written to logs are ignored by the old handlers, so no save or log needs migrating in either direction.
