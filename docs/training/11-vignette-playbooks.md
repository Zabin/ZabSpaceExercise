[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 11. Vignette playbooks — how each cell wins

A per-vignette tutorial for **both cells**: the objective in plain language, the move-by-move
sequence that completes it, and the gates that block the rest. Every "winning move" below is
driven through the real engine by `spacesim/tests/test_vignette_tutorials.py`, so these recipes
stay correct as the code changes. The same step scripts are embedded in each vignette's YAML and
surface in the app under **View ▾ → Tutorial panel** (scoped to your current cell).

**How to read a step.** *Actor* → *Action* → *Params* is exactly what you type in the **Satellite
command** panel (Target autocompletes from what your cell can see). After issuing, use **+10m** to
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
1. `BLUE-RADAR` → **observe** `BLUE-GNSS` `{intent: track}` — a health track so you can read the jamming signature.
2. **+10m** to the +1 h deadline. If the link is up, **`maintain_service` MET**. *Reality check:* MEO is effectively safe from kinetic — the fight is electromagnetic and **local to the user bubble**, so there's no satellite to "save," only a link to keep clean.

**Red — deny PNT.**
1. `RED-JAM` → **jam** `BLUE-GNSS` `{modulation: barrage, power_w: 200.0}` — denies the link in the bubble → **`deny_pnt` MET**.
2. **+10m** to sustain it. The denial is local and **reversible** — nothing is destroyed.

---

### 11.4 — Co-Orbital Threat & Escort (`co-orbital-threat-escort`)

| Cell | Objective | Win condition |
|---|---|---|
| Blue | `hva_survives` | `BLUE-HVA` alive at +1 h |
| Red | `neutralize_hva` | Drive `BLUE-HVA` into safe mode |

**Blue — keep the HVA alive.**
1. `BLUE-RADAR` → **observe** `RED-COORB` `{intent: characterize, classification: hostile}` — track the approaching co-orbital.
2. **+10m** to +1 h → **`hva_survives` MET**. With no kinetic ROE and no organic safing path, the threat can pressure but not kill.
3. *Active defense (if White-Cell adds a TT&C station):* `BLUE-HVA` → **maneuver** to evade, `BLUE-ESCORT` → **maneuver** to interpose. Δv spent vs. mission life is the tradeoff to teach.

**Red — neutralize it.**
1. `RED-COORB` → **maneuver** aggressive RPO toward `BLUE-HVA` (needs a Red command-uplink path).
2. *Gate:* without White-Cell kinetic ROE **and** a weapons-quality track, `neutralize_hva` cannot complete. The vignette's lesson is **restraint** — pressure short of an irreversible act.

---

### 11.5 — DA-ASAT Crisis (`da-asat-crisis`)

| Cell | Objective | Win condition |
|---|---|---|
| Blue | `avoid_debris` | No debris-generating strike by +1 h |
| Red | `destroy_sat` | Destroy `BLUE-SAT` (kinetic **authorized** here) |

**Blue — survive the crisis.**
1. **+10m** to +1 h. If no strike occurs, **`avoid_debris` MET**.
2. *Evade (if White-Cell adds a TT&C station):* `BLUE-SAT` → **maneuver** out of the predicted intercept corridor.

**Red — execute the intercept.** *(This is the one vignette where kinetic is on by default.)*
1. `RED-RADAR` → **observe** `BLUE-SAT` `{intent: characterize, classification: hostile}` — builds a **weapons-quality** track (confidence ≥ 0.8).
2. **+10m** to the look so the track lands.
3. `RED-ASAT` → **engage** `BLUE-SAT` `{interceptor_class: mrbm_kkv}` — **queued** (kinetic authorized). Pₖ derives from the `INTERCEPTORS` database (4 classes sourced from the four open-source DA-ASAT test records; Audit 2026-06 Commands §M2). Target altitude is a hard reach cap; defender `def.maneuver_evade` halves Pₖ.
4. **+10m** past intercept → **`destroy_sat` MET**, **but** a debris field forms, `avoid_debris` flips to failed, and the `un_condemnation` inject fires. *Teaching point:* the strike works and is **irreversible** — debris denies the regime to both sides.

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
1. `BLUE-RADAR-1` → **observe** `RED-OBJ` `{intent: characterize, classification: hostile}`. Confidence 1.0 → **`maintain_custody` MET** while fresh.
2. **Re-task before the 30-min half-life** — alternate to `BLUE-OPT-1` `{intent: track}` (needs lighting). The two sensors are **contended**, so prioritize: a missed re-task is a lost track.
3. Sustain confidence ≥ 0.5 all the way to +90 min.

**Red — break the chain.**
1. The simplest win is to **make Blue lapse**: if Blue can't re-task before the half-life, confidence decays below 0.5 and **`break_custody` MET** at the deadline.
2. `RED-OBJ` → **maneuver** a burn timed **outside** a pass enlarges the uncertainty volume (needs a Red command-uplink path; otherwise Red-doctrine / White-Cell driven).

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

> **Want to drive these headless?** Every step is a real `Order` through the `SessionAPI`. See the
> Python snippets in [§3 your first exercise](03-first-exercise.md) and
> [§4 guided vignette](04-guided-vignette.md); the same `actor / action / params` apply here.

---
