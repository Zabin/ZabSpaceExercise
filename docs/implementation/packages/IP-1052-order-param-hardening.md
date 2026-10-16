# IP-1052 — Order-Parameter Hardening: Malformed Jam/Engage/Cyber/Maneuver/Command Params Rejected Before Commit, and No State Left Behind by a Failed Plan (FR-3110, FR-1310, FR-1410, FR-1420)

> **Package ID:** IP-1052
> **Version:** 1.0
> **Status:** 🟢 READY — authored 2026-10-16 by `07-implementation-planning`, pipeline run #136.
> Authorized by the project owner 2026-10-11 (MSTR-006 §3) through the standing pre-authorization
> of the packages this iteration reaches. Same precedent as `IP-1041`/`IP-1222`/`IP-1221`/`IP-1212`.
> **Dependencies:** [FS-102](../../features/FS-102-command-scheduling.md) (Error Handling: an
> unambiguous result; Performance: a display estimate that disagrees with the real gate is a
> defect); [FS-105](../../features/FS-105-spacecraft-operations.md) v1.1 (Error Handling: the
> pre-disabled pattern surfaces the constraint reason *before* the operator attempts the action);
> [IP-1020](IP-1020-command-scheduling.md), [IP-1051](IP-1051-spacecraft-operations-effects-console.md),
> [IP-1041](IP-1041-observe-order-reason-and-param-remediation.md) (all `VERIFIED`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0222`
> **Produces:** jam, engage, cyber, maneuver, command and downlink orders whose malformed parameters
> are refused `invalid_param` by `dry_run` and `issue` alike, instead of an HTTP 500, a ghost
> `queued`/`draft` order, a corrupted `WorldState` value (`-inf` power, `NaN` orbit), or an event
> that raises inside the deterministic event loop; and a planner that commits nothing (no booking,
> no registry entry, no `queued` status) unless the order's execution payload was built.
> **Feature Reference:** [FS-102 — Command Scheduling](../../features/FS-102-command-scheduling.md);
> [FS-105 — Spacecraft Operations](../../features/FS-105-spacecraft-operations.md) §3.2/§3.3/§4
> **Related Topics:** [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js);
> [IP-1041](IP-1041-observe-order-reason-and-param-remediation.md) (the observe-only precedent)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package. Source: `BL-0222` (Low, filed run #132 from `IP-1041`'s Risks and extended
run #133). Its revisit trigger ("`IP-1041` reaches `VERIFIED`") fired at run #134. Every file,
function and line below was checked against the tree at `d2ded6a`. Run #136 reproduced every defect
listed in the Objective on fresh sessions, and the reproduction is wider than `BL-0222` stated.*

## Package ID

IP-1052

## Title

Order-Parameter Hardening: Malformed Jam/Engage/Cyber/Maneuver/Command Params Rejected Before
Commit, and No State Left Behind by a Failed Plan

## Objective

`IP-1041` closed this defect class for `observe` only. The same class is live in every other order
action. Reproduced at `d2ded6a` (run #136):

- **Live HTTP:** `leo-isr-denial` seed 5 via `TestClient`.
- **Engine level:** `SessionManager(load_vignette("leo-isr-denial"), seed=5)`, with ROE and a
  weapons-quality track forced where a gate stood in the way.

1. **Jam (`_exec_payload` `:652-657`).** `power_w: "abc"`, `bandwidth_hz: null` or
   `victim_bandwidth_hz: [1]` makes `POST /order/validate` return `ok: true`, because `dry_run`
   never calls `_exec_payload`. `POST /order` then returns **HTTP 500**. Each 500 leaves a **ghost
   order** with status `queued` in `OrderSystem.orders`, shown by `GET /orders/red`, with no
   scheduled event behind it. It never executes and never clears. Two sources combine:
   - `issue` registers the order (`:179-185`) before planning;
   - `_continue_plan` sets `status = "queued"` (`:327`) before `_exec_payload` (`:329`) raises.

   `power_w: "inf"` is accepted, and when the jam executes the jammer's `resources.power_w` becomes
   **`-inf` permanently**. `"nan"` is also accepted.
2. **Engage (`:697`).** `salvo_n: "abc"`, `null` or `"nan"` gives the same picture: `dry_run`
   `queued`, `issue` raises, and a ghost `queued` order remains.
3. **Cyber (`_plan_cyber` `:865-914`).** `dwell_s: "abc"` (likewise `persistence_h`,
   `sm_susceptibility`, `persistence_bonus`) is `queued` in `dry_run` (`commit=False` returns at
   `:869`). `issue` sets `queued` at `:866` and then raises at `:883`, leaving a ghost `queued`
   order.
4. **Maneuver (`_validate` `:568-569`; `_exec_payload` `:853-863`).**
   - `dv: "abc"` or `[1, "x", 0]` raises inside `_validate` itself, so both routes return HTTP 500
     and `issue` leaves a ghost `draft` order.
   - `dv: null` is `queued` in `dry_run` but raises in `issue`.
   - `dv: [NaN, 0, 0]` is **accepted and executed**. The satellite's orbit `a_m` and its
     `delta_v_ms` both become `NaN` permanently, and the corruption replays faithfully.
   - `dv: [1, 2]` or `[1, 2, 3, 4]` is **accepted and queued**. When it executes,
     `_h_maneuver` raises **inside `Simulation.advance_to`** (`simulation.py:70-81`), and the
     triggering `advance` returns HTTP 500 to whoever caught up the clock. The handler raises before
     `eventlog.append`, so the event is dropped unlogged and the order stays `queued` forever.
5. **Command / maneuver / downlink routing params.**
   - `stored_at: "abc"` hits `int()` at `:390` and raises in both routes.
   - `verb: [1]` raises in `can_issue` (`buscommands.py:552`, an unhashable membership test), in
     both routes.
   - `via: [1]` raises in `AccessProvider.windows`' cache key (`access.py:110`), in both routes.

Every one of these is reachable from the console, not only from a raw client. Typing in the order
panel's JSON params box (`#o-params`, `app.js:472`) is enough. The structured forms clamp NaN to 0
(`numVal`, `app.js:994-996`), but the escape hatch does not.

After this package:
- every order action's parameters are checked in `_validate`, so `dry_run` and `issue` agree;
- a malformed parameter is refused with `invalid_param` before anything is booked, registered or
  scheduled;
- an explicit `null` means "not given", as in `IP-1041`;
- no `WorldState` field can be driven non-finite by an order parameter;
- the planners build the execution payload before committing anything, so an unforeseen exception
  in payload construction leaves no booking, no ghost order and no `queued` status behind it.

### Design Decisions

1. **One per-action parameter check, in `_validate`, immediately after `unknown_action`.** A helper
   (module-level, alongside `_observe_params_ok`, which stays as is and becomes the `observe` entry
   of the dispatch) checks `order.params` for the action. It returns `invalid_param` on the first
   malformed value and never raises. Running first means a malformed order is refused identically
   whether or not it would also fail ownership or ROE. That matches `IP-1041`, whose observe check
   is the first thing after `unknown_action`.

   Per action, a param that is present and not `None` must be:

   | Action | Param | Check |
   |---|---|---|
   | `jam` | `power_w`, `bandwidth_hz`, `victim_bandwidth_hz` | accepted by `float()` and finite |
   | `engage` | `salvo_n` | accepted by `int()` without raising (so NaN, inf and non-numeric strings are refused) |
   | `engage` | `interceptor_class` | a string |
   | `cyber` | `dwell_s`, `persistence_h`, `sm_susceptibility`, `persistence_bonus` | accepted by `float()` and finite |
   | `cyber` | `vector`, `payload`, `segment` | a string |
   | `maneuver` | `dv` | a list or tuple of exactly three values, each accepted by `float()` and finite |
   | `maneuver`, `command` | `stored_at` | accepted by `int()` without raising |
   | `maneuver`, `command`, `downlink` | `via` | a string |
   | `command` | `verb` | a string |
   | `jam` | `modulation`, `link_target` | a string |

   Anything those conversions accept today (an int, a float, a numeric string) is still accepted,
   so no well-formed client changes behaviour. `int()`'s existing truncation of a float `salvo_n`
   (`2.7` → 2) is unchanged; see Design Decision 5.
2. **An explicit `null` means "not given".** The helper deletes `None`-valued keys from
   `order.params` for the params in the table, the same mechanism `IP-1041` used for observe (its
   run #133 mechanism note). Every later reader therefore takes the absent default, including
   `_exec_payload`, `_plan_cyber`, `_validate`'s own `"via" not in order.params` checks and
   `inprocess.py`'s Gantt feed. One consequence: a `maneuver` or `command` with `via: null` and no
   `stored_at` is now rejected `no_command_station` instead of crashing. `dv: null` takes the
   `[0, 0, 0]` default.
3. **Plan, then commit.** Every planner builds the execution payload before it mutates anything:
   - `_continue_plan` (`:322-331`): with `commit`, build the payload before setting `status`,
     `earliest_window` and `delivery_path`.
   - `_plan_command` (`:411-424`): build the payload, then book `_pass_bookings`/`_order_pass`, then
     schedule.
   - `_plan_collection` (`:467-477`): build the payload, then append to `_sensor_bookings`/
     `_order_sensor`, then schedule.
   - `_plan_cyber` (`:865-914`): construct the `EffectInstance` before setting `status`.
   - `issue` (`:179-185`): enter the order in `self.orders` only after `_plan` returns.

   `_plan` and `_continue_plan` read no `self.orders` entry for the order being planned; the gated
   path keys `_pending` by `order.id`, which is still assigned first. So the move is a reordering
   with no behaviour change for any order that plans successfully. The scheduled payload, the
   booking and the status are identical, and only the order in which they are written changes. An
   unforeseen exception still propagates (it is **not** swallowed into a rejection, which would hide
   bugs), but it leaves no trace.
4. **Console tip generalised.** `REASON_TIPS.invalid_param` (`app.js:181`) currently names only the
   observe fields. It becomes action-neutral, naming the order's parameters and the JSON params box.
   No other UI code changes.
5. **Scope boundary: type and finiteness, not range.** No current requirement or spec states
   `salvo_n ≥ 1`, `salvo_n ≤ ammo`, `power_w ≥ 0` or non-negative `dwell_s`. Today `salvo_n: 0` or
   `-3` is accepted (ammo consumption is clamped `max(1, salvo_n)` at `:730`). Range rules are a
   requirements decision and are filed for `04-requirements-engineering` (Risks), not invented here.
   Downlink's `partial_dump`/`bitrate_cap_kbps`/`priority` are already tolerated at execute time
   (`_h_downlink` `:979-984`) and are not touched.
6. **The event loop itself is not changed.** `Simulation.advance_to` dropping an event whose handler
   raises (unlogged, with a possible partial mutation that replay would not reproduce) is an
   engine-wide determinism question beyond order params. This package removes the known order-param
   route into it (`dv` length); the general question is filed for `03`/`07` (Risks).

## Feature Reference

- **FS-102** (Command Scheduling), Error Handling: a result must be unambiguous, never an
  indeterminate outcome. A 500 that leaves a ghost `queued` order is indeterminate. Performance: a
  display estimate that disagrees with the real gate is a defect, and `dry_run` saying `queued` for
  an order `issue` cannot plan is exactly that.
- **FS-105** (Spacecraft Operations) §3.2/§3.3/§4, Error Handling: the pre-disabled-button pattern
  surfaces constraint reasons before the operator attempts a blocked action, which requires
  `dry_run` to see the same failure `issue` does.

## Requirements Covered

FS-102 and FS-105 cite no FR in their own "Requirements Implemented" fields (a documented gap,
unchanged here). Coverage, following `IP-1020`'s/`IP-1051`'s RTM mapping:

| Req ID | How this package covers it |
|---|---|
| `FR-3110` | A planned command-kind activity is created only from parameters that can be planned; a rejected one leaves no `DRAFT`/`PLANNED` ghost in the queue, and the cancellable queue therefore reflects only real activities. |
| `FR-1310` | A maneuver's `dv` is a finite 3-vector before the budget check, so `delta_v_ms` can no longer be driven to `NaN` (the "never goes negative" postcondition becomes checkable again). |
| `FR-1410` | Effect resource consumption (`power_w`, `ammo`) is recorded from finite inputs only; an `inf` power request can no longer drive the jammer's power to `-inf`. |
| `FR-1420` | Cyber parameters are validated before the effect is constructed; the not-window-gated path keeps its semantics. |

`FR-3410` (execute-time re-validation) and `FR-3210` are consumed and not changed.

## Architecture Components

- **C1 Simulation Engine:** `engine/orders.py` (`_validate`, a new module-level parameter-check
  helper, `issue`, `_continue_plan`, `_plan_command`, `_plan_collection`, `_plan_cyber`).
- **C6 UI (web):** `ui_web/static/app.js` `REASON_TIPS.invalid_param` text only.
- No session, content, server-route, access-predicate or `simulation.py` change.

## Interfaces

- `INT-0008` (SessionManager → Engine OrderSystem). No new interface, route, request field or
  response field. `OrderAck.reason` may now carry `invalid_param` for every action, and
  `no_command_station` for a `via: null` command with no `stored_at`.

## Files to Create

- `spacesim/tests/test_order_param_hardening.py` — this package's tests (Tests 1–10).

## Files to Modify

- `spacesim/engine/orders.py`:
  - module level, beside `_observe_params_ok` (`:59-84`): the per-action check (Design Decisions
    1–2);
  - `_validate` (`:514-585`): call it right after the `unknown_action` check;
  - `issue` (`:179-185`): register after `_plan` (Design Decision 3);
  - `_continue_plan` (`:307-331`), `_plan_command` (`:382-424`), `_plan_collection` (`:438-477`),
    `_plan_cyber` (`:865-914`): payload before commit (Design Decision 3).
- `spacesim/ui_web/static/app.js` — `REASON_TIPS.invalid_param` (`:181`) (Design Decision 4).

## Implementation Tasks

1. Mark this package `IN PROGRESS` on the Master Build Plan, `packages/INDEX.md`, `ROADMAP.md` and
   this header before any edit.
2. Write Tests 1–10 and see them fail. Tests 8–10 assert unchanged behaviour and may pass on
   arrival; record which did.
3. Add the per-action check and the `None` handling (Design Decisions 1–2).
4. Reorder the commit blocks and registry insertion (Design Decision 3).
5. Update `REASON_TIPS` (Design Decision 4).
6. Run the full suite and both permanent gates; fix only what this package broke.
7. Update the documentation and ledgers (Documentation Updates), then mark `COMPLETE`.

## Tests to Add

All in `spacesim/tests/test_order_param_hardening.py`. Engine fixtures may be a
`SessionManager(load_vignette("leo-isr-denial"), seed=…)` (it has `JAM-NORTH`, `RED-ASAT`,
`ISR-EO-1`, `GS-NORTH`), with `_static_roe` and a characterized `Track` set directly where a gate
would otherwise answer first. HTTP cases use `fastapi.testclient.TestClient` with
`raise_server_exceptions=False`, as `test_observe_order_remediation.py` does.

1. **Jam params refused by both paths.** For each of `power_w: "abc"`, `"inf"`, `float("nan")`,
   `bandwidth_hz: [1]` and `victim_bandwidth_hz: {"a": 1}`, a jam is rejected `invalid_param` by
   `dry_run` and `issue`, and no order is left in `OrderSystem.orders` with status `queued`.
2. **Engage params refused.** `salvo_n: "abc"`, `"nan"`, `float("inf")` and `interceptor_class: 3`
   are rejected `invalid_param` by both paths (with kinetic ROE and a weapons-quality track in
   place, so the check, not a gate, is what answers).
3. **Cyber params refused.** `dwell_s: "abc"`, `persistence_h: "inf"` and `vector: ["x"]` are
   rejected `invalid_param` by both paths, and nothing is scheduled.
4. **Maneuver `dv` refused.** `"abc"`, `[1, "x", 0]`, `[1, 2]`, `[1, 2, 3, 4]` and
   `[float("nan"), 0, 0]` are rejected `invalid_param` by both paths. After the attempts the actor's
   orbit and `delta_v_ms` are unchanged and finite, and advancing past the would-be window raises
   nothing.
5. **Routing params refused.** `stored_at: "abc"`, `verb: [1]` and `via: [1]` (command), and
   `via: [1]` (downlink) are rejected `invalid_param` by both paths; none raises.
6. **`null` means absent.** A jam with `power_w: None`, `bandwidth_hz: None` and
   `victim_bandwidth_hz: None` schedules a payload equal to the same order with those keys absent. A
   maneuver with `dv: None` and a valid `via` is accepted with a zero `dv`. A command with
   `via: None` and no `stored_at` is rejected `no_command_station`.
7. **HTTP: no 500, and the preview agrees.** Through `TestClient`, `POST /order/validate` and
   `POST /order` with jam `power_w: "abc"` both return 200 with `ok: false` and reason
   `invalid_param`, and `GET /orders/red` lists no order for the attempt.
8. **No state from a failed plan (Design Decision 3).** Monkeypatch `OrderSystem._exec_payload` to
   raise for one jam order, one command order (ground uplink) and one observe order. Each `issue`
   raises, and afterwards `orders`, `_pass_bookings`, `_order_pass`, `_sensor_bookings`,
   `_order_sensor` and the scheduler heap are exactly as before the call. A following well-formed
   order of the same kind gets the same window it would have got with no prior attempt.
9. **Well-formed orders unchanged.** Numeric strings (`power_w: "200"`, `salvo_n: "1"`,
   `dwell_s: "30"`, `stored_at` as a numeric string) are still accepted, and the scheduled payload of
   an ordinary jam, engage, cyber, maneuver and command order equals the pre-package payload for the
   same fixture.
10. **Observe unchanged.** `test_observe_order_remediation.py` passes unmodified, and an observe with
    `beam_mode: ["fence"]` is still `invalid_param`.

Existing tests must pass unmodified, in particular `test_orders.py`, `test_validate_order.py`,
`test_queue.py`, `test_planning.py`, `test_derived_probabilities.py`, `test_jam.py`,
`test_bus_commands.py`, `test_observe_order_remediation.py`, and `test_vignette_tutorials.py` (the
shipped playbooks). The Phase-1 determinism gate (`test_determinism.py`) and the engine import guard
(`test_import_guard.py`) must stay green: the changes read no wall clock, draw no RNG and import
nothing outside `engine/`.

## Documentation Updates

- `docs/requirements/03-requirements-traceability-matrix.md`: add `IP-1052` and the new test file to
  the `FR-3110`, `FR-1310`, `FR-1410` and `FR-1420` rows.
- `CLAUDE.md` code map: the `engine/orders.py` bullet, if the implementer's change makes it
  inaccurate.
- Status records: this package's Status header, the Master Build Plan row, `packages/INDEX.md`,
  `ROADMAP.md`'s implementation-package row, and the `Referenced By` metadata of `FS-102` and
  `FS-105` (metadata only).
- **Manual impact:** route to `08-training-manual-authoring` via the backlog.
  `09-troubleshooting-and-glossary.md` §10's `invalid_param` entry (run #135) currently names only
  observe fields, and `10-ui-reference.md`'s JSON-params escape-hatch description may want a note.

## Definition of Done

- Every action's malformed parameter in Design Decision 1's table is rejected `invalid_param` by
  `dry_run` and `issue` alike, before anything is booked, registered or scheduled. None of the
  Objective's inputs gives an HTTP 500, a ghost order, a non-finite `WorldState` value, or an
  exception inside `advance_to`.
- An explicit `null` for those params behaves as absent.
- The planners and `issue` commit nothing unless the payload was built (Test 8).
- `REASON_TIPS.invalid_param` is action-neutral.
- Every well-formed order and every shipped vignette's playbook behaves as before.
- Code changes are confined to `spacesim/engine/orders.py`, `spacesim/ui_web/static/app.js` and
  `spacesim/tests/`.
- The full suite is green, and `test_determinism.py` and `test_import_guard.py` are green.
- The RTM, the ledgers and the FS cross-links are updated, and the manual-impact finding is routed.

## Verification Checklist

- [ ] `git diff` of the implementing commit touches code only in `spacesim/engine/orders.py`,
      `spacesim/ui_web/static/app.js` and `spacesim/tests/`; `simulation.py`, `access.py`,
      `buscommands.py` and `session/` are unchanged.
- [ ] Read `_validate`: the per-action check runs immediately after `unknown_action`, and observe
      still goes through `_observe_params_ok`.
- [ ] Read `issue`, `_continue_plan`, `_plan_command`, `_plan_collection`, `_plan_cyber`: no status,
      booking, registry or scheduler write precedes payload construction.
- [ ] Independent reproduction on a vignette/seed other than `leo-isr-denial` seed 5: a jam with
      `power_w: "abc"` gives `invalid_param` from both `POST /order/validate` and `POST /order`, and
      no ghost order is listed.
- [ ] Independent reproduction of the two `WorldState`-corruption cases (`power_w: "inf"`,
      `dv: [NaN, 0, 0]`): refused, and the asset's values stay finite after advancing past the window.
- [ ] A wrong-length `dv` is refused; advancing past its would-be window raises nothing.
- [ ] Test 8's no-state guarantee, re-derived independently (e.g. a different raising point or order
      kind).
- [ ] Tests 1–10 exist and pass; the Implementation Summary records which were seen failing first.
- [ ] Pre-existing tests are unmodified.
- [ ] `python3 -m pytest` passes in full, and `test_determinism.py` and `test_import_guard.py` pass.
- [ ] The RTM `FR-3110`/`FR-1310`/`FR-1410`/`FR-1420` rows cite `IP-1052`.
- [ ] The Master Build Plan row, the `packages/INDEX.md` row, `ROADMAP.md`'s row and this header
      agree on status.

## Dependencies

- **Packages:** `IP-1020` (`VERIFIED`, `VR-1020`), `IP-1051` (`VERIFIED`, `VR-1051`) and `IP-1041`
  (`VERIFIED`, `VR-1041`; this package extends its helper pattern). All three are `VERIFIED`, so this
  package is `READY`.
- **Spec/requirement:** FS-102 v1.0 and FS-105 v1.1 (both `Done`), `FR-3110`/`FR-1310`/`FR-1410`/
  `FR-1420`, all landed. No spec change is needed.
- **Authorization:** granted by the project owner 2026-10-11 (MSTR-006 §3) through the standing
  pre-authorization of this iteration's packages.
- **Parallelism:** `IP-1160` (`BLOCKED`, unauthorized) also edits `_validate` (role-scoped command
  rejection). Whichever lands second rebases. No other open package touches `orders.py`.

## Risks

- **`invalid_param` on input that used to "work".** Only inputs that raise today are refused, plus
  non-finite numbers, wrong-length `dv` and non-string routing ids, all of which today crash, ghost or
  corrupt state. Test 9 guards numeric strings.
- **Registry-insertion move (Design Decision 3).** `issue` returning an order not in `self.orders`
  happens only when `_plan` raises, and then the exception propagates anyway. Rewind and undo clear
  and rebuild `orders` from the event log (`manager.py:399-404`) and are unaffected. The implementer
  must confirm that nothing between `issue`'s id assignment and `_plan`'s return reads
  `self.orders[order.id]`. A read was found nowhere at `d2ded6a`; if one exists, keep the
  registration early and remove the entry on exception instead.
- **Scope left out on purpose (filed by run #136):**
  - Range semantics for `salvo_n` (≤ 0, above `ammo`, fractional), `power_w < 0`, negative `dwell_s`:
    a requirements question for `04-requirements-engineering`.
  - `Simulation.advance_to` drops, unlogged, an event whose handler raises (a possible live/replay
    divergence if the handler mutated state first): an engine-invariant question for
    `03-architecture-design-synthesis`/`07`.

## Rollback Considerations

Reverting the implementing commit restores today's behaviour: 500s, ghost orders, and `-inf`/`NaN`
state from malformed params. There is no persisted-format, `SavedSession`, route or API-schema
change, and no content change. Accepted orders' payloads are unchanged (Design Decision 2 only
replaces values that crash today, and Design Decision 3 only reorders writes), so a save made while
the package was live replays identically after rollback. Rejected orders never reach the event log.
A save made *before* the package that contains a `NaN`-`dv` maneuver still replays to the same
`NaN` state after it. This package refuses new such orders and does not rewrite history.
