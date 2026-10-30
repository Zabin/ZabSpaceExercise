[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 11. Vignette playbooks — how each cell wins

A per-vignette tutorial for **both cells**: the objective in plain language, the move-by-move
sequence that completes it, and the gates that block the rest. Every "winning move" below is
driven through the real engine by `spacesim/tests/test_vignette_tutorials.py`, so these recipes
stay correct as the code changes. The same step scripts are embedded in each vignette's YAML and
surface in the app under **View ▾ → Tutorial panel** (scoped to your current cell).

**How to read a step.** *Actor* → *Action* → *Params* is exactly what you type in the **Satellite
command** panel. For the target, pick it from the **Target** dropdown, which lists the other
side's objects your cell already knows about. If it is not listed yet, type its id in the **or id**
box ([UI reference §10.6 row 4](10a-ui-reference-orders.md#106-satellite-command-compose-form)). After issuing, use **+10m** to
advance past the order's window so it executes. Objectives flip in the **Cell & Time → Objectives**
panel.

**Three recurring gates** show up across the library — call them out to trainees:

- **Window gate.** `observe`, `downlink`, `maneuver`, `jam`, `engage` only execute inside an
  access window. The order queues and fires at the next valid pass.
- **Weapons-quality gate.** `engage` (kinetic) is rejected until you hold a **characterized track
  with confidence ≥ 0.8** on the target. Characterize first.
- **ROE / command-path gates.** Kinetic ASAT is **off** unless White-Cell sets
  `red_kinetic_authorized`. Some scenarios omit a TT&C ground station, so `maneuver` returns
  `no_command_station` — those closing/evasion moves are driven by Red doctrine or White-Cell
  adjudication. Where a move depends on a gate, the step says so.

> **Cyber is the exception** — it is **not** window-gated. A `cyber` order executes off-pass, any
> time, against a declared `access_vector`.

---

### 11.0 — Training: Basics (`training-basics`)

The Stage 0 onboarding fleet: `ISR-EO-1` + `GS-TRN` against `JAM-TRN`, `RED-CYBER`, `RED-ASAT`.
Deadline **+1 h**. Walked screenshot-by-screenshot in [§4](04-guided-vignette.md).

| Cell | Objectives |
|---|---|
| Blue | `deliver_isr` · `keep_custody` (on `RED-TGT`) |
| Red | `deny_isr` · `disable_isr` (safe-mode `ISR-EO-1`) |

**Blue.** 1. *Review.* 2. `RADAR-TRN` → **observe** `RED-TGT` `{intent: characterize, classification: hostile}` (`keep_custody` MET). 3. `ISR-EO-1` → **downlink** `{via: GS-TRN}`. 4. Advance past the window (~T+52 min, no later than T+60 min) → `deliver_isr` MET. 5. *Confirm both objectives* at T+60 min (the panel is live; do not advance past the deadline). 6. Optional: **maneuver** `{dv: [0, 5, 0], via: GS-TRN}` queues to a pass about T+11 h — after the deadline, so it cannot change scoring (and `keep_custody` will have decayed by then).

**Red.** 1. *Review.* 2. `RED-RDR` → **observe** `ISR-EO-1`. 3. `JAM-TRN` → **jam** `ISR-EO-1` `{modulation: barrage, power_w: 200.0}` during the `GS-TRN` pass. 4. `RED-CYBER` → **cyber** `ISR-EO-1` `{vector: ground_modem, payload: seize_c2}` — off-pass and **chance-based (~62% per attempt)**: success safes the bird (`disable_isr` MET), failure does nothing — advance ~1 min and check the Objectives panel (`disable_isr` unmet = failed), then re-issue. 5. Advance past T+1 h → `deny_isr` MET (independent of the dice). 6. `RED-ASAT` → **engage** → **REJECTED (`roe_kinetic_not_authorized`)**.

**ROE defaults.** Red kinetic OFF (`red_kinetic_authorized = false`); cyber **ON** for both sides (`cyber_authorized = true`; White Cell can switch it off).

---

### 11.1 — LEO ISR Denial (`leo-isr-denial`)

| Cell | Objective | Win condition |
|---|---|---|
| Blue | `deliver_isr` | Deliver imagery before the +3 h landing window |
| Red | `deny_isr` | No imagery delivered in time |

**Blue — deliver the imagery.**
1. *Review* the order of battle: `ISR-EO-1` + ground stations `GS-NORTH`/`GS-EAST`.
2. `BLUE-RADAR` → **observe** `RED-SURF` `{intent: characterize, classification: hostile}` — build the SDA picture (a commercial-imagery inject also reveals the surface group at +45 min).
3. `ISR-EO-1` → **downlink** `{via: GS-NORTH}` — queues to the next station pass.
4. **+10m** until it executes → **`deliver_isr` MET**. If `GS-NORTH` is jammed, re-route `{via: GS-EAST}`.

**Red — deny it reversibly.**
1. `JAM-NORTH` → **jam** `ISR-EO-1` `{modulation: barrage, power_w: 200.0}` during Blue's `GS-NORTH` pass — the downlink window is denied. (Pₛ derives from modulation × power × bandwidth coverage; defender `def.frequency_hop` and `satcom.mitigate_interference` cut it further at the resolver — Audit 2026-06 Commands §C1.)
2. **+10m** past the +3 h deadline → **`deny_isr` MET**.
3. `RED-ASAT` → **engage** `ISR-EO-1` → **REJECTED (`roe_kinetic_not_authorized`)**: kinetic is off by default. *Teaching point:* the disproportionate option is the one the rules deny you.

---

### 11.2 — GEO RPO Shadowing (`geo-rpo-shadowing`)

| Cell | Objective | Win condition |
|---|---|---|
| Blue | `maintain_custody` | Keep custody of `RED-INSP` (confidence ≥ 0.5) |
| Red | `close_approach` | Close within 100 km of `BLUE-HVA` |

**Blue — hold custody.**
1. `BLUE-OPT` → **observe** `RED-INSP` `{intent: characterize, classification: hostile}` on a **lit** pass (the optical site needs darkness on the target). Confidence resets to 1.0 → **`maintain_custody` MET** while fresh.
2. Confidence **halves every 30 min**. **Re-task** `BLUE-OPT` `{intent: track}` before it crosses 0.5 to hold custody through the decision window.

**Red — close the distance.**
1. Plan the approach for when `BLUE-OPT` **can't see** (terminator), to break custody between looks.
2. `RED-INSP` → **maneuver** closing burns toward `BLUE-HVA`. *Gate:* this scenario has no Red TT&C station, so closing is **Red-doctrine / White-Cell-driven** — the lesson is the ambiguity of RPO intent, not the burn arithmetic. A Blue that kept custody can maneuver away.

---

### 11.3 — GNSS EW Campaign (`gnss-ew-campaign`)

| Cell | Objective | Win condition |
|---|---|---|
| Blue | `maintain_service` | PNT link still up at +1 h |
| Red | `deny_pnt` | PNT link denied in the user bubble |

**Blue — keep service up.**
1. `BLUE-RADAR` → **observe** `BLUE-GNSS` `{intent: track}` — a health track so you can read the jamming signature. The radar's pass opens about **T+4 min**, so click **+10m** once and the track appears in your Fleet panel.
2. **+10m** until the clock is past **T+1 h**. `maintain_service` is **MET** — even while Red is jamming, because the satellite stays healthy. *Reality check:* MEO is effectively safe from kinetic — the fight is electromagnetic and **local to the user bubble**, so there's no satellite to "save," only a link to keep clean.

**Red — deny PNT.**
1. `RED-JAM` → **jam** `BLUE-GNSS` `{modulation: barrage, power_w: 200.0}` — the window is already open at T+0; advance a minute and **`deny_pnt` MET**.
2. **+10m** until past T+1 h to sustain it (both cells end up MET). The denial is local and **reversible** — nothing is destroyed.

---

### 11.4 — Co-Orbital Threat & Escort (`co-orbital-threat-escort`)

| Cell | Objective | Win condition |
|---|---|---|
| Blue | `hva_survives` | `BLUE-HVA` alive at +1 h |
| Red | `neutralize_hva` | Drive `BLUE-HVA` into safe mode |

**Blue — keep the HVA alive.**
1. `BLUE-RADAR` → **observe** `RED-COORB` `{intent: characterize, classification: hostile}` — queued; the pass opens about **T+17 min**. Click **+10m** twice and the hostile track appears.
2. `BLUE-HVA` → **maneuver** `{dv: [0, 5, 0]}` is **refused** (`no_command_station`): active defense needs a command path. *If White-Cell adds a TT&C station* the same order can evade, and `BLUE-ESCORT` → **maneuver** can interpose; Δv spent vs. mission life is the tradeoff to teach.
3. **+10m** until past **T+1 h** → **`hva_survives` MET**. With no kinetic ROE and no organic safing path, the threat can pressure but not kill.

**Red — neutralize it.**
1. `RED-COORB` → **maneuver** aggressive RPO toward `BLUE-HVA` — **refused** (`no_command_station`) until White Cell adds a Red command-uplink path.
2. *Gate:* without White-Cell kinetic ROE **and** a weapons-quality track, `neutralize_hva` cannot complete. The vignette's lesson is **restraint** — pressure short of an irreversible act.

---

### 11.5 — DA-ASAT Crisis (`da-asat-crisis`)

| Cell | Objective | Win condition |
|---|---|---|
| Blue | `avoid_debris` | No debris-generating strike by +1 h |
| Red | `destroy_sat` | Destroy `BLUE-SAT` (kinetic **authorized** here) |

**Blue — survive the crisis.**
1. `BLUE-SAT` → **maneuver** `{dv: [0, 5, 0]}` is **refused** (`no_command_station`) — `BLUE-SAT` has 20 m/s of Δv but nothing can command it. *If White-Cell adds a TT&C station* the same order shifts it out of the intercept corridor.
2. **+10m** until past T+1 h. If no strike occurs, **`avoid_debris` MET**; a Red strike lands around **T+20–26 min**.

**Red — execute the intercept.** *(This is the one vignette where kinetic is on by default.)*
1. `RED-RADAR` → **observe** `BLUE-SAT` `{intent: characterize, classification: hostile}` — builds a **weapons-quality** track (confidence ≥ 0.8). The pass opens about **T+17 min**. (An `engage` issued before the track exists is refused: `no_weapons_quality_track`.)
2. **+10m** twice (T+20 min) so the track lands.
3. `RED-ASAT` → **engage** `BLUE-SAT` `{interceptor_class: mrbm_kkv}` — **queued** for about **T+20 to T+26 min** (kinetic authorized). Pₖ derives from the `INTERCEPTORS` database (4 classes sourced from the four open-source DA-ASAT test records; Audit 2026-06 Commands §M2). Target altitude is a hard reach cap; defender `def.maneuver_evade` halves Pₖ.
4. **+10m** once more (T+30 min, past the intercept) → **`destroy_sat` MET**, **but** a debris field forms, `avoid_debris` flips to failed, and White Cell can fire the manual `un_condemnation` inject. *Teaching point:* the strike works and is **irreversible** — debris denies the regime to both sides.

---

### 11.6 — SATCOM Cyber & Link (`satcom-cyber-link`)

| Cell | Objective | Win condition |
|---|---|---|
| Blue | `keep_service` | `BLUE-SATCOM` operational at +1 h |
| Red | `disable_satcom` | Drive `BLUE-SATCOM` into safe mode via the modem |

**Blue — keep service / recover.**
1. `BLUE-RADAR` → **observe** `BLUE-SATCOM` `{intent: track}` — a track to spot the safe-mode drop.
2. **Remove the root cause.** This scenario has **no organic command station**, so the modem patch comes via the White-Cell **`patch_modem` inject** — recovery only sticks once the `ground_modem` vulnerability is patched. *Teaching point:* cyber resilience is a **ground-segment** problem you can't always fix from the cockpit.
3. **+10m** to +1 h. If SATCOM is operational, **`keep_service` MET**.

**Red — exploit the modem.**
1. `RED-CYBER` → **cyber** `BLUE-SATCOM` `{vector: ground_modem, payload: seize_c2}` — **off-pass, any time**. Pₛ derives from vector × posture × dwell; the `seize_c2` payload models the Viasat-style "issue legitimate management commands" attack that drives the target into safe mode → **`disable_satcom` MET**.
2. With `root_cause_persists` on, it **re-safes** after any recovery until Blue patches the vector.

---

### 11.7 — SDA Custody Hunt (`sda-custody-hunt`)

| Cell | Objective | Win condition |
|---|---|---|
| Blue | `maintain_custody` | Keep custody of `RED-OBJ` (≥ 0.5) to +90 min |
| Red | `break_custody` | Custody below 0.5 at +90 min |

**Blue — keep the track alive with scarce sensors.**
Your own sensors cannot see `RED-OBJ` in time (`BLUE-RADAR-1`'s first pass is about **T+134 min**, after the deadline), so the **Space Surveillance Network** carries the hunt.
1. Command bar → **SSN request** `{intent: characterize, target: RED-OBJ, regime: LEO, priority: priority}` — state SCHEDULED, product due about **T+15 min** → **`maintain_custody` MET** once it lands.
2. **+10m** once, then file the **same request again** at T+10 (product about T+25 min). **Re-task before the 30-min half-life** — a missed re-task is a lost track.
3. Keep filing at **T+30, T+50 and T+70** with **+10m** clicks between; custody never lapses and **`maintain_custody` is MET** at T+90 min. With a single request, custody drops below 0.5 about 30 min after it lands and Red wins.

**Red — break the chain.**
1. The simplest win is to **make Blue lapse**: if Blue can't re-task before the half-life, confidence decays below 0.5 and **`break_custody` MET** at the deadline.
2. `RED-OBJ` → **maneuver** `{dv: [0, 5, 0]}` is **refused** (`no_command_station`); with a Red command-uplink path a burn timed **outside** a pass enlarges the uncertainty volume (otherwise Red-doctrine / White-Cell driven).

---

### 11.8 — Multi-Domain Capstone (`multi-domain-taiwan`)

The capstone runs **three Blue missions against three Red denials at once** — you cannot do
everything, so triage. Deadline +90 min.

| Cell | Objectives |
|---|---|
| Blue | `deliver_isr` · `keep_satcom` · `custody_inspector` |
| Red | `deny_isr` · `disable_satcom` · `shadow_hva` |

**Blue — run all three lanes.**
1. **ISR:** `ISR-EO-1` → **downlink** `{via: GS-NORTH}` — beat the window before `JAM-NORTH` denies it; re-route `{via: GS-EAST}` if jammed.
2. **GEO custody:** `BLUE-OPT` → **observe** `RED-INSP` `{intent: characterize, classification: hostile}`; re-task before the half-life to hold `custody_inspector`.
3. **SATCOM:** `BLUE-RADAR` → **observe** `SATCOM-1` `{intent: track}` and watch for the cyber safe-mode; the patch comes via the White-Cell `patch_modem` inject.
4. **+10m** and assess: `deliver_isr` MET if the downlink beat the jam; `keep_satcom` / `custody_inspector` held if defended.

**Red — synchronize the denial.**
1. **ISR:** `JAM-NORTH` → **jam** `ISR-EO-1` `{modulation: barrage, power_w: 200.0}` during the `GS-NORTH` pass.
2. **SATCOM:** `RED-CYBER` → **cyber** `SATCOM-1` `{vector: ground_modem, payload: seize_c2}` — off-pass → **`disable_satcom` MET**.
3. **GEO shadow:** `RED-INSP` → **maneuver** within 100 km of `SATCOM-1` for `shadow_hva` (needs a Red command-uplink path / doctrine).
4. **+10m** and hold: `deny_isr` + `disable_satcom` MET if sustained. Kinetic ASAT stays **off** unless White-Cell authorizes — escalation is a deliberate facilitator choice.

---

### 11.9 — Mission Trial: SAR ISR (`mt-isr-sar`)

| Cell | Objective | Win condition |
|---|---|---|
| Blue | `collect_sar` · `survive` | A SAR product reaches the ground, and `SAR-1` is operational at +90 min |
| Red | `deny_downlink` | No product delivered by +90 min |

**Blue — image through cloud and night.**
1. `SAR-1` → Action **`isr.collect_now`** (picked by name in the Action menu), Params `{via: GS-POLAR}` — queued for the `GS-POLAR` pass that opens about **T+19 min**; the payload then shows *collecting*. (A weather advisory at T+10 min says EO would be useless; SAR is unaffected.)
2. `SAR-1` → **downlink** `{via: GS-POLAR}` — same pass.
3. **+10m** twice (T+20 min) → **`collect_sar` MET**. **+10m** to past T+90 min → **`survive` MET**.

**Red — contest the pass.**
1. Click `RED-DAZZLE`: its Action menu offers only **jam** (an `engage` order would be refused, `roe_kinetic_not_authorized`), and dazzle blinds optics, which SAR does not use.
2. `RED-JAM` → **jam** `SAR-1` `{modulation: barrage, power_w: 200.0}` — window opens about **T+17 min**, just before Blue's pass. Blue's downlink inside the jam fails: `collect_sar` stays unmet and **`deny_downlink` MET** at the deadline.

---

### 11.10 — Mission Trial: Weather Collection (`mt-weather-collect`)

| Cell | Objective | Win condition |
|---|---|---|
| Blue | `deliver_wx` · `wx_op` | One product delivered, `WX-1` operational at +60 min |
| Red | `track_blue` | Hold a track on `WX-1` at confidence ≥ 0.5 |

**Blue — cadence.**
1. `WX-1` → **downlink** `{via: GS-WX-PRIMARY}` — the pass opens about **T+34 min**. **+10m** to past T+40 min → **`deliver_wx` MET**; to past T+60 min → **`wx_op` MET**.
2. *Optional:* `{via: GS-WX-BACKUP}` queues but its pass is about **T+230 min** — useless for this deadline, so the primary pass is the one that counts.

**Red — passive watch.**
1. `RED-SDA-SENSOR` (carried by `RED-SDA-PASSIVE`) → **observe** `WX-1` `{intent: track}` — window opens about **T+16 min**. **+10m** twice → **`track_blue` MET**.
2. Advance to past T+60 min: the track has decayed below 0.5 (next window about T+66 min). Custody is a cadence problem for the watcher too.

---

### 11.11 — Novel: ISL Relay + Debris Corridor (`nv-isl-relay-debris`)

| Cell | Objective | Win condition |
|---|---|---|
| Blue | `isr_b_survives` · `isr_b_op` | `ISR-B` alive and operational at +30 min |
| Red | `track_blue` | Hold a track on `ISR-A` |

**Blue — command around the gap.**
1. **+10m** once; read the advisory (sent at T+5 min): `ISR-B` closes with debris at about **T+17 min**. `ISR-A` is in view of `GS-NORTH` for the first 8 min; `ISR-B` is not.
2. `ISR-B` → **maneuver** `{dv: [0, 5, 0], via: GS-NORTH}` — queued with delivery path **`isl_relay`** (ground → `ISR-A` → `ISR-B`); Δv drops 100 → 95 m/s.
3. **+1m**, then **+10m** to past T+30 min → both objectives MET.

**Red — watch.** `RED-SDA-SENSOR` → **observe** `ISR-A` `{intent: track}` (window open from the start); **`track_blue` MET** at T+10 min, then decays below 0.5 by T+30 min unless re-tasked.

---

### 11.12 — Mission Trial: SIGINT Geolocation (`mt-sigint-geolocate`)

> **Known limitation.** Sensors can only observe orbiting objects, and the SIGINT payloads are not
> taskable sensors, so `characterize_emitter` cannot yet be reached by orders (an `observe` on
> `RED-EMITTER` is refused: `no_window` / `no_such_sensor`). Filed for the engine; the script below
> says so in-app. `preserve_constellation` is achievable.

| Cell | Objective | Win condition |
|---|---|---|
| Blue | `characterize_emitter` · `preserve_constellation` | Characterized track on `RED-EMITTER`; satellites alive at +60 min |
| Red | `deny_characterization` | No characterized track at +60 min |

**Blue.** Try `BLUE-OPTICAL` and `SIGINT-1` → **observe** `RED-EMITTER` (both refused, as above); **+10m** to past T+60 min → `preserve_constellation` MET.
**Red.** No orders; White Cell can fire the manual `emitter_silent` inject. Advance to past T+60 min → `deny_characterization` MET.

---

### 11.13 — Learning: Safe-Mode Recovery (`learn-intermediate-recovery`)

| Cell | Objective | Win condition |
|---|---|---|
| Blue | `recover_to_nominal` | `ISR-EO-LEARN` not in safe mode at +45 min |
| Red | `keep_safed` | `ISR-EO-LEARN` in safe mode |

**Blue — diagnose, patch, recover.**
1. *(Explanatory)* Read the green bus card; the only command path is `GS-LEARN`, whose pass opens about **T+41 min**.
2. *(Needs Red first: switch to the Red seat, fire, switch back.)* **+1m** twice: the bird is in safe mode with a cyber signature.
3. `ISR-EO-LEARN` → Action **`def.patch_cyber`** (by name in the Action menu), Params `{vector: ground_modem, via: GS-LEARN}` — closes the root cause.
4. Drill-down → **Begin recovery** (1 pass) → **+10m** past T+45 min → bus nominal, **`recover_to_nominal` MET**. Skip step 3 and the strip reports *root cause persists (cyber)*: the bird stays safed.

**Red.** `RED-CYBER` → **cyber** `ISR-EO-LEARN` `{vector: ground_modem, payload: seize_c2}` (about 62%; not window-gated). If the bird is still green after a minute, fire again. Once Blue patches, the exploit no longer works.

### 11.14 — Red COA: Russia ML, Sustained EW (`coa-russia-ml`)

*These five COA vignettes (11.14-11.18) have no scripted `tutorial:` block, so no Tutorial panel; the recipes below are driven on Seed 1 by `test_vignette_tutorials.py` (the Red COA tests). Red's ISR-kill COAs (11.15, 11.17) now carry a Red ground radar, `RED-RADAR`; the other three have no Red sensors.*

**Reading Blue's "available" flags.** `pnt_avail`/`satcom_avail`/`pnt_op`/`satcom_op` measure whether the **satellite** is healthy at the deadline, not whether its link is jammed, so a jammed link still reads ✓ (engine semantics, stated in each brief); judge jamming in the AAR and on Red's `deny_*` flags.

| Cell | Objective | Judged |
|---|---|---|
| Blue | `pnt_avail`, `satcom_avail` (`BLUE-PNT`, `BLUE-SATCOM` operational) | at T+60 min |
| Red | `deny_pnt`, `deny_satcom` (a link to each denied) | true as soon as the jam is active |

Red cyber is **off** here (`cyber_authorized` false); kinetic off.
**Red.** `RED-JAM-TIRADA` → **jam** `BLUE-PNT` and `RED-JAM-POLE` → **jam** `BLUE-SATCOM`, each `{modulation: barrage, power_w: 200}`; both queue at once. **+10m**: both `deny_*` flip to ✓ by T+30 min.
**Blue.** You see a `deny` symptom on both satellites, source unknown. Counter with `BLUE-PNT` → `def.frequency_hop` and `BLUE-SATCOM` → `satcom.mitigate_interference`, both `{via: GS-EUROPE}` (each queues to the next pass). Note: `pnt_avail`/`satcom_avail` read ✗ until the T+60 min deadline and then ✓ even under jamming (a jammed link does not make the satellite non-operational), so both sides can finish with their objectives met; judge the outcome in the AAR, not by the flags alone.

### 11.15 — Red COA: Russia MD, DA-ASAT + Cyber (`coa-russia-md`)

| Cell | Objective | Judged |
|---|---|---|
| Blue | `isr_survives` (T+30), `satcom_op` (T+60), `no_debris` (T+60) | deadlines |
| Red | `destroy_isr`, `safe_satcom` | by T+60 min |

Kinetic and cyber are both **on**. **Red.** `RED-CYBER` → **cyber** `BLUE-SATCOM` `{vector: ground_modem, payload: seize_c2}` (not window-gated, chance-based): on success `safe_satcom` flips ✓ (it did on Seed 1) and Blue's `satcom_op` stays ✗. `RED-RADAR` → **observe** `BLUE-ISR-LEO` `{intent: characterize, classification: hostile}` (pass about **T+16 min**; click **+10m** twice), then `RED-NUDOL` → **engage** `BLUE-ISR-LEO` `{interceptor_class: mrbm_kkv}` (window about **T+19-24 min**; before the track exists it is refused `no_weapons_quality_track`). **`destroy_isr` ✓** inside the T+30 min survival window, with debris. **Blue.** Task `BLUE-RADAR-W`/`-E` to watch; patch the modem first with `BLUE-SATCOM` → `def.patch_cyber` `{vector: ground_modem, via: GS-PRIME}` and keep `BLUE-ISR-LEO` ready with `def.maneuver_evade` `{via: GS-PRIME}`. The `nudol_alert` inject (White) warns Blue of the launcher spin-up.

### 11.16 — Red COA: China ML, Early Integrated Disruption (`coa-china-ml`)

| Cell | Objective | Judged |
|---|---|---|
| Blue | `isr_delivers`, `satcom_op`, `geo_custody` (on `RED-SJ-INSPECTOR`) | T+30 min |
| Red | `deny_isr`, `safe_satcom`, `rpo_close` (inspector within 50 km of `BLUE-GEO-COMM`) | T+30 min |

**Red.** `RED-CYBER` → **cyber** `BLUE-SATCOM` (ground_modem / seize_c2): `safe_satcom` ✓. `RED-JAM-COASTAL` → **jam** `BLUE-ISR` queues, but its pass is about T+95 min, after the window, so `deny_isr` stays ✗ inside T+30 min. `RED-SJ-INSPECTOR` → **maneuver** `{dv: [0, 20, 0], via: RED-TTC}` (Red's Hainan TT&C station) closes the inspector from about 74 km to under 50 km by about T+28 min: **`rpo_close` ✓**. **Blue.** `BLUE-ISR` → **downlink** `{via: GS-WESTPAC}` runs at once and `isr_delivers` flips ✓; `geo_custody` stays ✗ until a radar or optical sensor tracks the inspector; the `h_hour` inject marks the start of the Red package. 

### 11.17 — Red COA: China MD, Decisive Strike (`coa-china-md`)

| Cell | Objective | Judged |
|---|---|---|
| Blue | `any_isr`, `pnt_op`, `satcom_op` | T+45 min |
| Red | `kill_isr`, `deny_pnt`, `safe_satcom` | T+45 min |

**Red.** Cyber: `RED-CYBER` → **cyber** `BLUE-SATCOM-PRIMARY` → `safe_satcom` ✓. `RED-JAM-PNT` → **jam** `BLUE-PNT`: the window is open from T+0, so `deny_pnt` ✓ after a minute. `RED-RADAR` → **observe** `BLUE-ISR-PRIMARY` (pass about **T+18 min**) then `RED-ASAT` → **engage** (window about **T+22-28 min**): **`kill_isr` ✓**. **Blue.** `BLUE-ISR-PRIMARY` → **downlink** `{via: GS-WP}` runs near T+37 min: `any_isr` ✓ by T+50 min; `pnt_op` ✓; `satcom_op` ✗ once the cyber lands, so patch/recover `BLUE-SATCOM-PRIMARY` (11.13). The `decisive_warning` inject says kinetic strikes are authorized.

### 11.18 — Red COA: Iran ML, Regional EW Spoiler (`coa-misc-iran-ml`)

| Cell | Objective | Judged |
|---|---|---|
| Blue | `pnt_op`, `satcom_op` | T+45 min |
| Red | `deny_pnt`, `deny_satcom` | T+45 min |

**Red.** Both mobile jammers can jam both satellites from T+0 (the satellites were re-phased so the windows fall inside the scenario): `RED-MOBILE-JAM-1` → **jam** `BLUE-PNT`, `RED-MOBILE-JAM-2` → **jam** `BLUE-SATCOM`, each `{modulation: barrage, power_w: 200}`; after a minute both `deny_*` are ✓. **Blue.** Both objectives read ✓ at T+45 min even while jammed (satellite health, see above). The `jammer_moves` inject (White) degrades SSN custody of the jammers.

> **Sources:** `spacesim/content/vignettes/coa-russia-ml.yaml` · `spacesim/content/vignettes/coa-russia-md.yaml` ·
> `spacesim/content/vignettes/coa-china-ml.yaml` · `spacesim/content/vignettes/coa-china-md.yaml` ·
> `spacesim/content/vignettes/coa-misc-iran-ml.yaml` · `spacesim/session/redai.py` · FR-11320

---

> **Want to drive these headless?** Every step is a real `Order` through the `SessionAPI`. See the
> Python snippets in [§3 your first exercise](03-first-exercise.md) and
> [§4 guided vignette](04-guided-vignette.md); the same `actor / action / params` apply here.

---

> **Sources:** `spacesim/content/vignettes/*.yaml` (`tutorial:` blocks and `intro_brief:` deadlines) ·
> `spacesim/tests/test_vignette_tutorials.py` (`_Learner` / `_script` step drivers) ·
> [`16-learning-path.md`](16-learning-path.md) · FR-11320/11420
