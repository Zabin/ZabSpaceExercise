[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md) ·
[White Cell manual](12-white-cell-manual.md) · [Traceability matrix](15-manual-traceability.md)

## 12c. White Cell manual — staffing, approval gates, ROE and injects in depth

Part of the [White Cell manual](12-white-cell-manual.md). It covers the controls that decide *who may
do what* in an exercise (operator seats, approval gates, live ROE changes) and the inject tools
beyond the basics in WCM-5. Section IDs continue the `WCM-n` scheme;
[`15-manual-traceability.md`](15-manual-traceability.md) maps them both ways.

### WCM-18 · Staff the exercise: operator seats and roles

**Two different "seats".** The **console seat** is the White / Blue / Red / Observer button in the
toolbar — which screen you are looking at. An **operator seat** is just a *name you invent* (for
example `blue-bus-op`) that you bind to one asset and one role. Players type that name into the
**Operator seat** field of the order form; the server then checks that the command belongs to that
operator's role. Nothing authenticates the name: it is a training aid on a trusted LAN
(see [`01-install-and-run.md`](01-install-and-run.md)).

**When it matters.** Only when the vignette's `roles_needed` list names the asset (or its group).
No built-in vignette declares one, so with the shipped library staffing never blocks **Start**, and
the **Operator seat** field changes nothing. Use it with a vignette you author or edit (the Creator
does not write `roles_needed`; add it to the saved YAML). Each entry names an asset or group, a role
(`bus`, `payload` or `both`) and whether it is mandatory (the default).

**Procedure — assign roles.**

1. Switch to **White** and open **📋 Session ▾**. Scroll to **Seat-to-role assignment**.
2. Type the **Seat** name (letters, digits, `-`, `_`, `.`, space; up to 64 characters), the **Asset /
   constellation** (an asset id or a group name from the vignette), and choose **Role**: **Both**,
   **Bus** or **Payload**. Press **Assign**. If either text box is empty nothing happens.
3. Read the line under the button, the **staffing report** (it shows `—` until the first time you press **Assign** or **Start**). It lists every mandatory requirement
   still uncovered, one per line as `unmet: ISR-EO-1 / bus`, or says `fully staffed (or this vignette
   declares no roles_needed)`. A `both` assignment covers a `bus` or `payload` requirement.
4. Press **▶ Start**. If anything mandatory is still unmet, a pop-up shows `unstaffed mandatory
   role(s): ISR-EO-1/bus, ISR-EO-1/payload` and the exercise does not start. Assign the missing
   roles and press Start again.

**What the server enforces afterwards.** For a `command` order (a bus, payload or defense verb such as
`eps.shed_load` or `isr.collect_now`) on an asset that `roles_needed` covers, issued with an
operator seat:

| Situation | Result |
|---|---|
| Seat bound to that asset, and the verb's role is covered | Order proceeds to the normal checks |
| Seat not bound to that asset, or not bound at all | Refused `role_scope_not_assigned` |
| Seat bound, but the verb belongs to the other role | Refused `role_scope_out_of_scope` |
| Order issued with **no** operator seat | No role check at all |
| Asset belongs to the other cell | The normal `not_owner` refusal, whatever the seat |

A role refusal is not logged, has no order id and cannot be replayed; the player just sees the
message (BLU-15 / RED-14). **Role is checked when the order is submitted.** Re-binding a seat later
(**Assign** again with the same seat name) changes what that seat can submit from then on; orders
already queued are not re-checked. Re-binding can also reopen a gap: after you move `op-bus` from bus to
payload the staffing report shows `unmet: ISR-EO-1 / bus` again, but a running exercise is not stopped.
Because the check keys on whatever seat name the player types, any player can type another seat's
name; treat it as a rehearsal of crew roles, not security.

**Check one seat's scope** (optional): `GET /api/sessions/{sid}/roles/scope?seat=op-bus&cell=blue`
returns what that seat is bound to and which verbs are bus or payload. Asking as Red about a Blue seat
returns `bound: false`.

> **Sources:** `spacesim/session/manager.py` (`assign_role`, `staffing_report`, `role_scope_check`,
> `role_scope_for`, `ROLE_SCOPE_BY_VERB`) · `spacesim/session/inprocess.py` (`start`) ·
> `spacesim/ui_web/server.py` (`assign_role`, `role_scope`) · `spacesim/ui_web/static/app.js`
> (`refreshStaffingReport`, `REASON_TIPS`, `onOpSeatChange`) · `spacesim/content/vignette.py`
> (`RoleRequirement`) · FR-4210, FR-3510, FR-3520

### WCM-19 · Approval gates and live ROE changes

**What a gate is.** A vignette can declare `effect_gating_rules`: each rule matches an action type
(`jam`, `cyber`, `engage`, ...) and/or a reversibility category (an `engage` counts as `destroy`, a `jam`
as `deny`) and names a `required_role` (normally `white`). A matching order is not planned. It waits in
the status `pending_approval` until that role approves or denies it. Only a vignette's YAML sets
gates; there is no console form to add one, and no built-in vignette declares any.

**What players see while an order waits.** The order is accepted (`ok`) with status `pending_approval`.
It appears in the player's **Command queue** with that status, no window and no delivery path. The
compose form's preview and the Issue button behave as for any valid order. The player cannot cancel
it (`order not found / not cancellable`); they wait for White. Nothing is scheduled, so nothing
executes, and the other cell sees nothing.

**How White approves or rejects — HTTP only.** The console has **no button** for this. Use the API
(from a terminal on the host, or any HTTP client), naming the White seat in the body:

```bash
curl -X POST 'http://127.0.0.1:8000/api/sessions/<SID>/gate/decide' -H 'Content-Type: application/json' \
  -d '{"cell":"white","order_id":"ord-1","approve":true}'
```

Find `order_id` in White's **Command queue** (or the **Command queue** panel for that cell). Replies:

| Reply | Meaning |
|---|---|
| `{"ok":true}` approve | Planning resumes now: window and delivery path are chosen at the *decision* time (`queued`), not at the time of issue |
| `{"ok":true}` with `"approve":false` | The order becomes `rejected` with reason `gate_denied` |
| `{"ok":false,"reason":"not_controller"}` | The `cell` you named is not the rule's `required_role` |
| `{"ok":false,"reason":"no_such_pending_order"}` | Wrong id, or it was already decided |

The request and the decision, with the elapsed time, are written to the event log
(`effect_gate_request`, `effect_gate_decision`) and show up in the AAR.

**Save and resume.** A save made while an order is pending keeps the order; after **Load session** it is
still `pending_approval` and can still be decided. If a pending order cannot be rebuilt (its gate rule is
gone or its request entry is missing) it is rejected with reason `gate_lost_on_resume` and the load
reports a warning.

**Change ROE mid-exercise — HTTP only.** The Mission brief shows each cell's ROE flags
(`kinetic_authorized`, `cyber_authorized`). To change one while the exercise runs:

```bash
curl -X POST 'http://127.0.0.1:8000/api/sessions/<SID>/roe/change' -H 'Content-Type: application/json' \
  -d '{"cell":"white","target_cell":"red","flag":"cyber_authorized","value":false}'
```

It takes effect from that simulated moment and is logged. An order is judged against the ROE in force
*when it was issued*; an `engage` or `cyber` order refused for ROE shows `roe_kinetic_not_authorized` or
`roe_cyber_not_authorized` ("ROE does not authorize ..."). Replies: `ok`, `not_controller` (the `cell` you
named is not `white`), `unknown_flag` (only the two flags above exist). The built-in vignettes with a
cyber-authorized switch (for example `training-basics`) can also be changed before Start through the
vignette parameters in WCM-2.

> **Sources:** `spacesim/engine/orders.py` (`decide_gated_order`, `issue_roe_change`, `_matching_gate`,
> `rebuild_pending`, `_effective_roe`) · `spacesim/ui_web/server.py` (`decide_gated_order`,
> `issue_roe_change`) · `spacesim/session/manager.py` (`list_orders`, `from_state`) ·
> `spacesim/ui_web/static/app.js` (`REASON_TIPS`) · FR-3420, FR-3430, FR-3440, FR-7220

### WCM-20 · Injects in depth: schedule, edit, cancel, conditions, who sees what

WCM-5 covers building and firing. This section covers what happens next.

1. **Schedule.** In **Build / schedule inject** choose **Schedule**: **Now (immediate)**, **+ seconds
   from now** (type the seconds) or **Absolute UTC** (a date-time picker). Press **Schedule / fire**. The
   result line shows `✓ scheduled for <UTC time> (1 effect)` or `✓ fired immediately (1 effect)`. A time already
   in the past fires immediately.
2. **See the queue.** The panel lists every not-yet-fired inject: its handle (a White inject is
   `white-1`, `white-2`, ...), its fire time (or `on condition`), and its effect types, each with
   **Cancel** and **Edit...**.
3. **Edit.** **Edit...** asks for the effects as a JSON list, then for a new fire time in seconds from
   now (blank keeps the old time). **Cancel** removes it. Refusals appear in the result line: `no
   pending inject 'white-9' (unknown, already fired, or cancelled)` (too late, or a typo), `edit
   rejected: #0 nope: unknown effect type 'nope'` (the edit is checked whole, and nothing changes).
4. **Rewind.** A scheduled inject survives a rewind: it returns to the queue if you rewind to before its
   time. Your own edit or cancel is part of the history, so rewinding to a moment before you made it
   puts the inject back as it was.
5. **Conditions.** A vignette can declare an inject that fires when something becomes true (for
   example two assets coming within a range, or an asset going into safe mode). The simulator checks
   the condition every 5 simulated minutes (the bus-tick period) and fires it once it is true. The queue shows it as `on condition`; you can still Cancel or Edit it.
   Conditions are written in the vignette YAML (`trigger: {type: condition, metric: {...}}`); the
   builder only makes timed injects.
6. **A bad effect.** A hand-built inject with a bad effect is refused whole (`inject rejected: #0
   anomaly: anomaly subsystem must be 'bus' or 'telemetry', got None`). A scripted vignette inject with a
   bad effect is skipped and only White is told (`inject effect skipped (...)`).
7. **Who sees what.** Effects that act on one side's private equipment tell the owner only the *fact*
   and tell White the cause. For an `anomaly` or `sensor_outage` on a Blue asset: White's Messages say
   what was injected; Blue sees only that the asset has a problem (safe mode, degraded comms, a sensor
   degraded); Red sees nothing. Neutral assets: White only. A plain `message` goes to the cells you list in `to`.

Rewind and bookmarks are in WCM-4; the fog rules behind "the fact, not the cause" are in
[`05-core-concepts.md`](05-core-concepts.md).

> **Sources:** `spacesim/session/manager.py` (`pending_injects`, `cancel_inject`, `edit_inject`,
> `_inject_overrides`, `_h_condition_check`, `_notice_by_owner`, `validate_inject_effects`) ·
> `spacesim/ui_web/static/app.js` (`fireBuiltInject`, `renderPendingInjects`, `pendingInjectAction`) ·
> `spacesim/ui_web/server.py` (`inject_cancel`, `inject_edit`, `injects_pending`) · FR-4420, FR-4430,
> FR-4450
