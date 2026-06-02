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

### Blue — recover from the cyber attack

Red's cyber on `ground_modem` flipped `ISR-EO-1` into **safe mode**: the payload is off, the bus
survives, the orbit is unchanged. Reversible effects are only operationally meaningful if the
defender can clear them, so the recovery loop is the second half of the lesson. **Switch back to
Blue** (or reload the session and run Red's steps again as White Cell, then switch) and walk
through the procedure below in order. The order matters: skip the patch and recovery will
re-safe the satellite on the next pass.

**Step 7 — Discover it on the next telemetry contact.** Click **Blue**, then click `ISR-EO-1` in
the fleet rail. The badge turned **red**, the bus mode reads `safe_mode`, and the drill-down
shows the `cdh.faults` log line that flagged the modem. Cyber is **not** window-gated, so the
attack landed when Red issued it — but you only **see** it when the next downlink contact
returns telemetry. The fleet rollup dot turns red as soon as that telemetry lands.

![Safe-mode recovery strip](../manual/10-safe-mode-recovery.png)

**Step 8 — Patch the vulnerability FIRST.** In the recovery strip, click **Patch (def.patch_cyber)**
(or compose it manually: Actor `ISR-EO-1`, Action `command`, Params
`{"verb":"def.patch_cyber","vector":"ground_modem","via":"GS-TRN"}`). *When:* queues to the next
command-uplink pass and executes there. *Result:* the matching entry in `ISR-EO-1`'s
`cyber_vulnerabilities` flips `patched: true`. **This is the root cause — the cyber attack
exploited an unpatched modem; until you patch it, the access vector is still open and the
attacker's stored access keeps re-safing the satellite.**

> If you skip this step and start recovery first, the engine will mark the asset
> `re-safed: root cause persists (cyber)` after the recovery passes finish — recovery is
> **deterministically** reverted because the vulnerability is still open. The recovery strip
> shows a red warning explaining what to remove before retrying.

**Step 9 — Begin recovery.** Click **Begin recovery** in the recovery strip (or
`POST /api/sessions/{sid}/recovery/blue/ISR-EO-1 {"via":"GS-TRN"}`). The engine schedules
**two `realistic`-difficulty passes** over the next command-uplink windows: pass 1 confirms the
diagnosis (`establish_contact` + `dump_telemetry`), pass 2 applies the `patch` + `re_enable`
steps and exits safe mode. The recovery strip updates after each pass — chips fill in left to
right as `confirmed → diagnose → patch → re_enable → done`.

The number of passes is the safe-mode-loop §6.3 model: `base × recovery_difficulty`
(`quick`=1, `realistic`=2, `punishing`=3). White Cell can change this with the
`recovery_difficulty` vignette dial.

**Step 10 — Advance through the recovery passes.** Click **+10m** until the clock crosses the
second pass. *Result:* `ISR-EO-1` exits safe mode, the badge turns green, the payload is back
online, and the `effect_log` records `{achieved: "recovered", success: true}`. If you patched in
step 8, recovery sticks. If you didn't, you'll see a red `⚠ root cause persists` row instead —
patch and run **Begin recovery** again.

**Step 11 — Re-attempt the mission (optional).** With the satellite recovered, re-issue the
downlink from Blue step 3 (`downlink via GS-TRN`) and advance to the window. If you do this
*before* the original delivery deadline expired, `deliver_isr` flips back to MET — a complete
recovery, not just a survived attack. This is the contrast the AAR draws: a successful Red
attack against a slow defender vs. a survived attack against a fast one, byte-identical from
the same starting state.

> **In a single block, the whole recovery in Python:**
>
> ```python
> from spacesim.engine.orders import Order
> # Step 8 — patch the modem vulnerability (queues to next GS-TRN command pass)
> api.issue_order(sid, "blue", Order(
>     cell="blue", actor="ISR-EO-1", action="command",
>     params={"verb": "def.patch_cyber", "vector": "ground_modem", "via": "GS-TRN"}))
> # Step 9 — schedule the multi-pass recovery chain
> r = api.begin_recovery(sid, "blue", "ISR-EO-1", via="GS-TRN")
> # Step 10 — advance past the second (final) pass and confirm
> api.advance_to(sid, r["finish_at"] + 1)
> bus = api.get_view(sid, "blue").own_assets[0]["bus_state"]
> assert bus["mode"] == "nominal" and not bus["safe_mode"]["active"]
> ```

The lesson: cyber is the only effect category that bypasses access windows on attack, but
**recovery still costs passes**. A defender who patches eagerly and starts recovery on the
first telemetry contact wins back the asset in two passes (~one orbit at LEO); a defender who
skips the patch loses two passes to a re-safe and starts over. That asymmetry — and the
operator's choice in it — is what the vignette is teaching.

> **Watch it in 3D.** Throughout, the **3D globe** (drag to rotate, **tilt**, **zoom**, **zoom-to**
> an asset) and the **2D belief map** (zoom / pan / center / layer toggles) render only the active
> cell's belief — own assets known, hostile objects as uncertainty volumes.
>
> ![3D globe](../manual/14-globe-overview.png)

---
