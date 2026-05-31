[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 5. Guided training vignette

The **Training: Basics** scenario (`training-basics`, top of the picker) is a hands-on tutorial
that walks each cell through the core loop. Both sides have a **six-step** sequence below — the
exact actor, action, parameters, *when* to issue, and the expected result. Every step is the real
order the engine executes (these steps are verified by `spacesim/tests/test_training.py`).

**Set up:** pick **Training: Basics**, **Seed = 1**, **Load** → **Start**. The order of battle:
Blue `ISR-EO-1` (LEO imager, modem vulnerability, fuel) with `GS-TRN` ground station and the
`RADAR-TRN` sensor; Red `RED-TGT` (a satellite Blue images), `JAM-TRN` (downlink jammer co-located
with the station), `RED-CYBER`, `RED-RDR`, and `RED-ASAT` (kinetic, off by default).

> In the command panel, **selecting an Actor filters the Action menu to that asset's legal
> actions** and pre-fills the parameter template — see ![command menu](../manual/17-command-menu.png)

### Blue — maintain custody and deliver imagery

**Step 1 — Review fleet & objectives.** Click **Blue**. Confirm `ISR-EO-1` is nominal and both
objectives read *pending*.

![Blue step 1](../manual/18-train-blue-1.png)

**Step 2 — Task the sensor to build custody.** Actor `RADAR-TRN`, Action `observe`, Target
`RED-TGT`, Params `{"intent":"characterize","classification":"hostile"}`. *When:* issue now; it
collects on RADAR-TRN's early pass. *Result:* a characterized track on RED-TGT — `keep_custody` MET.

![Blue step 2](../manual/19-train-blue-2.png)

**Step 3 — Plan the imagery downlink.** Actor `ISR-EO-1`, Action `downlink`, Params
`{"via":"GS-TRN"}`. *When:* issue now; it queues to the next `GS-TRN` pass. *Result:* `queued` via
`ground_uplink` with a scheduled execution time.

![Blue step 3](../manual/20-train-blue-3.png)

**Step 4 — Advance to the downlink window.** Click **+10m** until the clock passes the window.
*Result:* imagery delivered — `deliver_isr` MET.

![Blue step 4](../manual/21-train-blue-4.png)

**Step 5 — Maneuver to preserve the orbit.** Actor `ISR-EO-1`, Action `maneuver`, Params
`{"dv":[0,5,0],"via":"GS-TRN"}`. *When:* queues to the next command pass. *Result:* `queued`; the
5 m/s burn is debited from the fuel budget on execution.

![Blue step 5](../manual/22-train-blue-5.png)

**Step 6 — Confirm the objective.** Review the objectives panel: Blue delivered imagery in time.

![Blue step 6](../manual/23-train-blue-6.png)

### Red — deny the imagery with reversible effects

Reload **Training: Basics** (or **Rewind**) and click **Red**.

**Step 1 — Review own assets.** Confirm the jammer, cyber unit, radar, and interceptor.

![Red step 1](../manual/24-train-red-1.png)

**Step 2 — Find the Blue ISR satellite.** Actor `RED-RDR`, Action `observe`, Target `ISR-EO-1`,
Params `{"intent":"track"}`. *When:* issue now; reports on RED-RDR's early pass. *Result:* custody
on `ISR-EO-1`.

![Red step 2](../manual/25-train-red-2.png)

**Step 3 — Jam the downlink.** Actor `JAM-TRN`, Action `jam`, Target `ISR-EO-1`, Params
`{"success_prob":1.0,"outcome":"deny"}`. *When:* queues to the footprint window over the station.
*Result:* the link is denied during that window — a Blue downlink in this window would fail.

![Red step 3](../manual/26-train-red-3.png)

**Step 4 — Cyber the modem (off-pass).** Actor `RED-CYBER`, Action `cyber`, Target `ISR-EO-1`,
Params `{"access_vector":"ground_modem","outcome":"safe_mode","success_prob":1.0}`. *When:* any
time — cyber is **not** window-gated. *Result:* `ISR-EO-1` drops to **safe mode**; `disable_isr` MET.

![Red step 4](../manual/27-train-red-4.png)

**Step 5 — Attempt a kinetic strike (ROE check).** Actor `RED-ASAT`, Action `engage`, Target
`ISR-EO-1`. *Result:* **REJECTED — `roe_kinetic_not_authorized`.** Kinetic ASAT is off by default;
this teaches escalation restraint (White Cell can enable it with the `red_kinetic_authorized` dial).

![Red step 5](../manual/28-train-red-5.png)

**Step 6 — Advance and assess.** Click **+10m** past the delivery window. With nothing delivered,
`deny_isr` is MET — Red denied the imagery using only reversible effects.

![Red step 6](../manual/29-train-red-6.png)

> **Watch it in 3D.** Throughout, the **3D globe** (drag to rotate, **tilt**, **zoom**, **zoom-to**
> an asset) and the **2D belief map** (zoom / pan / center / layer toggles) render only the active
> cell's belief — own assets known, hostile objects as uncertainty volumes.
>
> ![3D globe](../manual/14-globe-overview.png)

---
