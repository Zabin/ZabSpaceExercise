[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md) ·
[Blue cell manual](13-blue-cell-manual.md) · [Traceability matrix](15-manual-traceability.md)

## 13a. Blue cell manual — operator seats, orders awaiting approval, and how commands reach your satellite

Part of the [Blue cell manual](13-blue-cell-manual.md); section IDs continue the `BLU-n` scheme and
are cross-referenced in [`15-manual-traceability.md`](15-manual-traceability.md). Red has a matching
set in [14a](14a-red-cell-rules-and-delivery.md).

### BLU-15 · The Operator seat field: bus operator, payload operator, or both

**What it is.** Some exercises ask you to *crew* a satellite: one person flies the **bus** (power,
attitude, thermal, comms, defence verbs such as `def.patch_cyber`) and another runs the **payload**
(imaging, SATCOM, sensors: `isr.collect_now`, `satcom.shift_users`). White Cell gives each person an
**operator seat** name such as `blue-bus-op` and binds it to an asset and a role (Bus, Payload or Both).
The **Operator seat** box in the order form is where you type your name. It is *not* the Blue / Red /
White button in the toolbar.

**Do I need it?** Only if White tells you to. In the 19 shipped vignettes nothing is crewed, so leave
the box empty. An empty box means "no role check": every command you are otherwise allowed to issue is
allowed. The server also skips the check if you leave the name out, even for a crewed satellite, so
the field is a rehearsal of crew discipline, not a lock.

**Procedure.**

1. In the order form (the **Satellite command** panel) find **Operator seat** under **Actor**. The grey hint
   reads `optional - your Role Assignment name`.
2. Type the exact name White gave you (up to 64 characters: letters, digits, space, `-`, `_`, `.`).
   It is remembered for this session in your browser.
3. Choose your **Actor** (the crewed satellite). The **Action** list now offers only the bus or payload
   commands your seat covers; commands for the other role are not listed. Base actions such as
   Maneuver, Observe, Downlink are not role-gated and stay listed. If your name is not bound to that
   satellite, only those base actions are offered.
4. Compose the command as usual. The green/red preview line under the form checks your seat too.

**What a refusal looks like.** The preview shows a red line, and Issue is disabled:

- `This operator seat is not assigned to that asset — ask White Cell to bind it, or clear the Operator
  seat field.` (reason `role_scope_not_assigned`). Your seat name is wrong, or White has not bound it to this
  satellite. Check the spelling, or ask White.
- `That command belongs to the other role on this asset — your operator seat covers only its own role.`
  (reason `role_scope_out_of_scope`). A bus operator tried a payload command, or the reverse. Hand it to
  your crewmate, or ask White to bind your seat as Both.

If you bypass the preview, Issue answers `REJECTED: role_scope_not_assigned` (or `..._out_of_scope`)
and no order is created: nothing appears in the queue, nothing is logged.

**Good to know.** The role is checked when you press Issue. If White re-binds your seat afterwards,
commands already queued stay queued and only your *next* submission uses the new binding. Commands
for an asset the other cell owns are refused first with `This asset belongs to another cell.`

> **Sources:** `spacesim/ui_web/static/app.js` (`REASON_TIPS`, `refreshRoleScope`, `onOpSeatChange`,
> `composeBody`) · `spacesim/ui_web/static/index.html` (`o-seat`) · `spacesim/session/manager.py`
> (`role_scope_check`, `role_scope_for`) · [`12c`](12c-white-cell-rules-and-staffing.md) (WCM-18) · FR-3510, FR-3520

### BLU-16 · My order says "pending_approval"

Some exercises put certain orders (for example a jam, a cyber action or a strike) behind an
**approval gate**: White Cell, or another named role, must approve before the order is planned. If you
issue one you see status `pending_approval` in your **Command queue**, with no window and no delivery
path yet. That is not an error: nothing has been scheduled, nothing will fire until it is decided.

1. Tell White (voice or chat) which order is waiting; give the order id (`ord-3`).
2. You cannot cancel it while it waits (`order not found / not cancellable`). If White approves, the status
   becomes `queued` with a window computed from *that moment*, so the window may be later than the
   preview suggested. If White denies, it becomes `rejected` with reason `gate_denied`; re-plan.
3. If the exercise is saved and resumed meanwhile, the order stays pending. In the rare case its gate
   no longer exists, it comes back `rejected` with reason `gate_lost_on_resume`.

**Rules of engagement can change in play.** White may switch a flag during the exercise. From then on
new `engage` or `cyber` orders are judged against the new ROE: a preview that used to be green turns red
with "ROE does not authorize kinetic effects." (`roe_kinetic_not_authorized`) or "ROE does not authorize
cyber effects." (`roe_cyber_not_authorized`). Orders you issued earlier keep the ROE that applied when you
issued them. Re-read your **Mission brief** ROE line after White announces a change.

> **Sources:** `spacesim/engine/orders.py` (`decide_gated_order`, `rebuild_pending`, `_effective_roe`) ·
> `spacesim/session/manager.py` (`list_orders`) · `spacesim/ui_web/static/app.js` (`REASON_TIPS`) ·
> [`12c`](12c-white-cell-rules-and-staffing.md) (WCM-19) · FR-3430, FR-3440

### BLU-17 · How a command gets to your satellite, and what a jam can stop

Every command picks one of three routes; the **Command queue** shows it as the **delivery path**.

| Delivery path | In plain terms | Can an enemy uplink jam stop it? |
|---|---|---|
| `ground_uplink` | A ground station you own transmits during a pass | **Yes** - if your satellite's uplink is jammed when the command executes |
| `isl_relay` | Another of your satellites passes it over a crosslink | Not by an uplink jam. A **crosslink** jam on your satellite or on the relay stops it |
| `stored_program` | You give a run time (`stored_at`); the satellite carries the command out on its own then | **No** - it uses no link at the moment it runs |

Jamming comes in three kinds, by the link it attacks: **uplink** (commands up), **downlink** (imagery and
telemetry down) and **crosslink** (satellite to satellite). A jam order that names no link attacks the
**downlink**, so by default an enemy jam hurts your imagery delivery, not your commands.

**What you see when a command is jammed.** The queue still moves the order from `queued` to `executed`
once its window opens - that label only says the window came and went. Check the outcome elsewhere: a
manoeuvre that did not happen is missing from your **manoeuvre ledger**, the satellite's orbit and
**Δv** are unchanged, and White's ground-truth effect log records the command as `jammed` on a path such as
`ground_uplink:uplink`. If a command seems to have done nothing, assume it was jammed, replan through a
different path (stored program, or crosslink via a satellite not being jammed), and see [BLU-6](13-blue-cell-manual.md#blu-6--diagnose-an-attack-from-telemetry)
for the telemetry signature.

**Choosing a path.** The planner picks the soonest valid route. A ground uplink needs a **via**
station (the order form's station picker). A stored program needs a run time: open **Advanced (raw JSON
params)** under the form and add `"stored_at": <sim time in microseconds since the Unix epoch, for example
1899787735628382>` (the same number format as the `window` of a queued order in `GET /orders/blue`). There is
no form field for it. Commands that must survive an uplink jam (a burn you cannot miss) are the ones to
store in advance this way.

> **Sources:** `spacesim/engine/orders.py` (`_delivery_keys`, `_delivery_jammed`, `_jammed_record`,
> `_h_maneuver`, `_h_command`) · `spacesim/engine/effects.py` (`is_link_denied`) ·
> `spacesim/session/manager.py` (`list_orders`, `maneuver_ledger`) · [`05-core-concepts.md`](05-core-concepts.md)
> §"Plan-first commanding & delivery paths" · FR-1440

### BLU-18 · Manoeuvre ledger: how much Δv have I spent, and on what

Every manoeuvre of yours that actually executed is listed in a per-satellite **manoeuvre ledger**: when it
happened, what it cost, the purpose tag you gave it, and the Δv you had left afterwards. There is no
console panel for it yet; open the URL in a browser tab or save the CSV.

1. Pick a satellite you own (for example `ISR-EO-1`) and note your session id (`sess-1`, shown in the
   address bar after `#`).
2. Open `http://127.0.0.1:8000/api/sessions/sess-1/maneuver_ledger/blue/ISR-EO-1`. You see rows such as
   `{"t":1899787431879026,"cost":1.0,"purpose_tag":"phasing","remaining_delta_v_ms":79.0}`. For a
   spreadsheet use the same address ending `/export.csv`: columns `t,cost,purpose_tag,remaining_delta_v_ms`.
3. `t` is sim time in **microseconds since the Unix epoch** (divide by 1,000,000 for seconds). `cost` and
   `remaining_delta_v_ms` are metres per second. Set the tag when you plan the manoeuvre by adding
   `"purpose_tag":"phasing"` in **Advanced (raw JSON params)**; it defaults to blank.

An empty list means no manoeuvre has executed yet; a queued, jammed or refused one is not in it. A
satellite that is not yours, or does not exist, answers `404 no maneuver ledger for this asset
(fog/ownership)`. A manoeuvre forced by White Cell as a scripted inject moves the satellite but does not
appear here.

**Time in every export.** The URL parameters `t1` and `t2` of the telemetry CSV and ephemeris exports are
integer microseconds, as above; an ISO date such as `2030-03-15T06:00:00Z` gets a `422` with `Input should be
a valid integer`. The *files* you get back show both: the CSV has a `t` column (microseconds) and a `utc`
column (ISO). A span entirely outside the recorded exercise is refused (`requested time span [0, 5] is
wholly outside the session's recorded range [...]`); a span partly outside is quietly clipped to the range.
The ephemeris export also needs `reference_id` (the object the frame is relative to), and the live
RIC view and TLE export answer `404 ... has no state visible to blue` for anything you cannot see. Full
parameter lists are in BLU-11 to BLU-14.

> **Sources:** `spacesim/session/manager.py` (`maneuver_ledger`) · `spacesim/ui_web/server.py`
> (`maneuver_ledger`, `maneuver_ledger_export_csv`) · `spacesim/engine/orders.py` (`_h_maneuver`) ·
> `spacesim/session/ephemeris.py` (`sample_times`) · FR-1320, FR-7410, FR-2320
