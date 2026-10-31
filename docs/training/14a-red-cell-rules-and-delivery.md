[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md) ·
[Red cell manual](14-red-cell-manual.md) · [Traceability matrix](15-manual-traceability.md)

## 14a. Red cell manual — operator seats, orders awaiting approval, and choosing which link to jam

Part of the [Red cell manual](14-red-cell-manual.md); section IDs continue the `RED-n` scheme and are
cross-referenced in [`15-manual-traceability.md`](15-manual-traceability.md). Blue has the matching
view in [13a](13a-blue-cell-rules-and-delivery.md).

### RED-14 · The Operator seat field: crewing your own satellites

**What it is.** In a crewed exercise White Cell binds named **operator seats** (for example
`red-payload-op`) to one of your assets and a role: **Bus**, **Payload** or **Both**. Type your name in the
**Operator seat** box of the order form (under **Actor**); the server then accepts only the commands of
your role on that asset. The box is *not* the White / Blue / Red toolbar button.

**Do I need it?** Only when White tells you. None of the 19 shipped vignettes crews a satellite, so leave it
empty; an empty box (or omitting the seat in a script) means no role check at all.

**Procedure.** Type the exact seat name (up to 64 characters: letters, digits, space, `-`, `_`, `.`), then
pick the **Actor**. The **Action** list shows only your role's bus or payload commands for that asset
(base actions like Jam, Observe, Maneuver are never role-gated). Your own satellite's bus verbs include
power, attitude and defence verbs; payload verbs include collection and SATCOM controls.

**Refusals** (preview line in red, Issue disabled):

- `This operator seat is not assigned to that asset — ask White Cell to bind it, or clear the Operator
  seat field.` - wrong spelling, or no binding for that asset.
- `That command belongs to the other role on this asset — your operator seat covers only its own role.`

A role refusal creates no order and no log entry. Role is checked when you press Issue; if White re-binds
your seat later, only your next submissions are affected. Details and the White side are in
[`BLU-15`](13a-blue-cell-rules-and-delivery.md#blu-15--the-operator-seat-field-bus-operator-payload-operator-or-both)
and [`WCM-18`](12c-white-cell-rules-and-staffing.md).

> **Sources:** `spacesim/ui_web/static/app.js` (`REASON_TIPS`, `refreshRoleScope`, `onOpSeatChange`) ·
> `spacesim/ui_web/static/index.html` (`o-seat`) · `spacesim/session/manager.py` (`role_scope_check`) ·
> FR-3510, FR-3520

### RED-15 · My jam, cyber or strike is "pending_approval"

If the exercise puts your kind of action behind an **approval gate**, the order is accepted but shows
status `pending_approval` in your **Command queue**, with no window or delivery path. Nothing is scheduled
until the approver (usually White) decides. Tell White which order (`ord-4`) is waiting. You cannot cancel
it meanwhile (`order not found / not cancellable`).

- **Approved:** it becomes `queued`; the window and path are worked out at the moment of approval, so the
  pass you saw in the preview may have gone. Re-check your timeline.
- **Denied:** it becomes `rejected` with reason `gate_denied`.
- **Save/resume** keeps a waiting order; if its gate no longer exists it returns `rejected` with
  `gate_lost_on_resume`.

**ROE can change mid-exercise.** When White switches a flag, new `engage` or `cyber` orders use the new
setting and previews turn red with "ROE does not authorize kinetic effects." (`roe_kinetic_not_authorized`)
or "ROE does not authorize cyber effects." (`roe_cyber_not_authorized`). An order you already issued is
judged by the ROE in force when you issued it. Re-read the Mission brief ROE line after an announcement.

> **Sources:** `spacesim/engine/orders.py` (`decide_gated_order`, `rebuild_pending`, `_effective_roe`) ·
> `spacesim/ui_web/static/app.js` (`REASON_TIPS`) · [`12c`](12c-white-cell-rules-and-staffing.md)
> (WCM-19) · FR-3430, FR-3440

### RED-16 · Which link to jam: uplink, downlink or crosslink

A jam attacks one **link** of the target satellite. You choose the link with the `link_target` parameter;
the jam assistant has no field for it, so open **Advanced (raw JSON params)** under the form and add it,
for example `{"modulation":"barrage","power_w":200,"link_target":"uplink"}`. Accepted values are `uplink`,
`downlink` and `crosslink`; anything else, or leaving it out, means **downlink**.

| You jam | It stops | It does not stop |
|---|---|---|
| `uplink` | Commands sent from a ground station (`ground_uplink` path) when they execute during your jam | Stored programs; relayed (`isl_relay`) commands |
| `downlink` (default) | Imagery and telemetry delivery | Commands |
| `crosslink` | Commands relayed over a satellite-to-satellite link (`isl_relay`), if the target **or its relay** is jammed | Ground uplinks; stored programs |

Practical notes: a defender who stores a command in advance (`stored_program`) is immune to an uplink jam,
so look for the moment a defender has no other choice. Your jam must still be *active* when the
command's window executes - a footprint on the map is only a preview. The defender's **Command queue**
still reads `executed` for a command you jammed; they have to notice the missing effect, so expect them
to infer it from telemetry. Jamming uses nothing up; the jammer's power rating does not change. The
defender's frequency hopping and interference mitigation lower your success chance.

> **Sources:** `spacesim/engine/orders.py` (`_delivery_jammed`, `_jammed_record`, `link_target` in the jam
> plan) · `spacesim/engine/effects.py` (`is_link_denied`) · `spacesim/engine/jam.py` ·
> [`05-core-concepts.md`](05-core-concepts.md) · FR-1440

### RED-17 · Manoeuvre ledger: your Δv spend

Each executed manoeuvre of your satellites is recorded in a per-satellite **manoeuvre ledger** (time, cost,
purpose tag, Δv remaining). There is no console panel; open
`http://127.0.0.1:8000/api/sessions/sess-1/maneuver_ledger/red/<your-satellite>` (add `/export.csv` for a
spreadsheet; columns `t,cost,purpose_tag,remaining_delta_v_ms`). `t` is sim time in microseconds since the
Unix epoch; `cost` and `remaining_delta_v_ms` are metres per second. Tag a manoeuvre by adding
`"purpose_tag":"inspect"` under **Advanced (raw JSON params)** when you plan it. Queued, jammed or refused
manoeuvres are not listed; the other side's satellites answer `404 no maneuver ledger for this asset
(fog/ownership)`. As with every export, `t1`/`t2` are ISO-8601 UTC (`2030-03-15T06:00:00Z`) or integer microseconds (a bad bound gets a `400` naming
`t1`/`t2`), and a span wholly outside the recorded exercise is refused. Spend Δv
deliberately: the ledger is the quickest way to see how many burns you can still afford. The full
reference for Red's exports is RED-10 to RED-13.

> **Sources:** `spacesim/session/manager.py` (`maneuver_ledger`) · `spacesim/ui_web/server.py`
> (`maneuver_ledger`, `maneuver_ledger_export_csv`) · `spacesim/session/ephemeris.py` (`sample_times`) · FR-1320
