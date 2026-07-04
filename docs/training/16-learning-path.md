[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md) ·
[Vignette library](06-the-vignette-library.md) · [Playbooks](11-vignette-playbooks.md) ·
[Traceability matrix](15-manual-traceability.md)

## 16. The vignette learning path

The 19-vignette library is not a flat menu — it is a **learning path** a new operator walks from
zero knowledge to mission-set competence. This module sequences it (satisfying **FR-11310**) and
wires each rung to the manual modules a trainee should read first and to the playbook that walks
its objectives (**FR-11320**). Read it top to bottom the first time; return to it to pick the next
rung.

Each rung names:

- **Read first** — the shared concept modules and role-scoped manual sections
  ([White `WCM-n`](12-white-cell-manual.md) · [Blue `BLU-n`](13-blue-cell-manual.md) ·
  [Red `RED-n`](14-red-cell-manual.md)) that teach what the rung exercises.
- **New this rung** — the one mechanic the rung adds over the previous one (the reason it sits
  where it sits).
- **Playbook** — the move-by-move entry in [§11](11-vignette-playbooks.md), machine-verified
  against the engine (**FR-11420**).

> **How a facilitator uses this.** Assign a rung matched to the trainee's level, not always
> rung 0. A seasoned SATCOM operator new to *this tool* still starts at Stage 0 for the interface,
> then may jump straight to the mission-set track for their specialty. The path is a
> recommendation with a hard floor (Stage 0), not a mandatory single-file march.

---

### Stage 0 — Onboarding (start here, always)

**`training-basics` — Training: Basics** · both cells · ~30 min

- **Read first:** [01 Install & run](01-install-and-run.md) · [02 Interface](02-interface.md) ·
  your role manual's first sections ([WCM-1…4](12-white-cell-manual.md) /
  [BLU-1…3](13-blue-cell-manual.md) / [RED-1…3](14-red-cell-manual.md)).
- **New this rung:** the core operator loop — read the brief, plan a command against a pass
  window, advance time, watch it execute — on a minimum-viable fleet (1 satellite + 1 ground
  station) so nothing distracts from the loop itself.
- **Playbook:** the in-app **Tutorial panel** (View ▾) drives this one step-by-step for each cell.

### Stage 1 — Core mechanics ladder (the canonical 8)

Each rung adds exactly one core mechanic; walk them in order the first time. All eight have a
verified [§11 playbook](11-vignette-playbooks.md).

| Rung | Vignette | New this rung | Read first (beyond Stage 0) |
|---|---|---|---|
| 1 | **`leo-isr-denial`** — LEO ISR Denial | Pass windows; the collect-vs-downlink split; reversible vs. kinetic effects | [05 Core concepts](05-core-concepts.md) "Plan-first" & "SDA tasking"; [BLU-2/4](13-blue-cell-manual.md), [RED-2/5](14-red-cell-manual.md) |
| 2 | **`geo-rpo-shadowing`** — GEO RPO Shadowing | Ambiguous RPO intent; custody decay in GEO | [BLU-4/8](13-blue-cell-manual.md), [RED-4/5](14-red-cell-manual.md) (RPO / co-orbital) |
| 3 | **`gnss-ew-campaign`** — GNSS EW Campaign | Local, reversible PNT denial; MEO is kinetically safe | [05](05-core-concepts.md) "Cyber/EW"; [RED-5](14-red-cell-manual.md) (jam), [BLU-6](13-blue-cell-manual.md) (diagnose EW) |
| 4 | **`co-orbital-threat-escort`** — Co-Orbital Threat & Escort | Active defense: escort and maneuver-to-evade | [BLU-8](13-blue-cell-manual.md) (defensive maneuver/conjunctions), maneuver assistant [BLU-3](13-blue-cell-manual.md) |
| 5 | **`da-asat-crisis`** — DA-ASAT Crisis | Escalation, debris, attribution, political cost | [RED-5](14-red-cell-manual.md) (kinetic + ROE gate); [07 Legal/ROE](../research/07-legal-norms-and-roe.md); [WCM-5](12-white-cell-manual.md) (injects) |
| 6 | **`satcom-cyber-link`** — SATCOM Cyber & Link | Ground/link segment; cyber acts outside passes | [BLU-9](13-blue-cell-manual.md)/[RED-6](14-red-cell-manual.md) (cyber off-pass); [BLU-6](13-blue-cell-manual.md) (cyber signature) |
| 7 | **`sda-custody-hunt`** — SDA Custody Hunt | Custody decay; sensor contention; breaking custody | [BLU-4](13-blue-cell-manual.md)/[RED-4](14-red-cell-manual.md) (SDA loop), deeper |
| 8 | **`multi-domain-taiwan`** — Multi-Domain Capstone | Integrated campaign across every subsystem | the whole corpus; [WCM-8/9](12-white-cell-manual.md) (doctrine + AAR) |

### Stage 2 — Mission-set specialization (Track A)

After the ladder, go deep on a payload specialty. Order among these is free — pick your seat.

| Vignette | New this rung | Read first |
|---|---|---|
| **`mt-isr-sar`** — SAR ISR | SAR is all-weather/day-night; succeeds where EO fails | [BLU-3/4](13-blue-cell-manual.md) (ISR beam modes) |
| **`mt-sigint-geolocate`** — SIGINT Geolocation | Multi-pass TDOA/FDOA convergence | [BLU-4](13-blue-cell-manual.md); R129 (SIGINT geolocation) |
| **`mt-weather-collect`** — Weather Collection | Operations cadence: SoC, eclipse, storage, downlink timing | [BLU-5](13-blue-cell-manual.md) (bus health) |

### Stage 3 — Adversary doctrine (Track B, Red-focused)

The Red COA library — study these as Red's playbook of campaign shapes, or run them AI-Red as
White to give Blue a doctrinally-flavored opponent. Assumes Stage 1 mechanics.

| Vignette | New this rung | Read first |
|---|---|---|
| **`coa-russia-ml`** — Russia ML, Sustained EW | Reversible deniable EW, coordinated | [RED-5/8](14-red-cell-manual.md); [WCM-8](12-white-cell-manual.md) |
| **`coa-russia-md`** — Russia MD, DA-ASAT + Cyber | Kinetic with cyber surprise | [RED-5/6/8](14-red-cell-manual.md) |
| **`coa-china-ml`** — China ML, Early Integrated Disruption | Jam + cyber + RPO opening | [RED-4/5/6/8](14-red-cell-manual.md) |
| **`coa-china-md`** — China MD, Decisive Strike | Late-crisis A2/AD: kinetic + RPO + cyber + EW | full [RED manual](14-red-cell-manual.md) |
| **`coa-misc-iran-ml`** — Iran ML, Regional EW Spoiler | Non-spacefaring adversary contests the ground segment | [RED-5](14-red-cell-manual.md); [BLU-9](13-blue-cell-manual.md) (GS as terrain) |

### Stage 4 — Depth & novelty (Tracks C, D)

Standalone deep-dives; take them when the relevant mechanic needs reinforcement.

| Vignette | New this rung | Read first |
|---|---|---|
| **`learn-intermediate-recovery`** — Safe-Mode Recovery | Diagnose signature → reset → root-cause patch, end-to-end | [BLU-6/7](13-blue-cell-manual.md) (diagnose + recover); [05](05-core-concepts.md) "Safe-mode recovery" |
| **`nv-isl-relay-debris`** — ISL Relay + Debris-Corridor Maneuver | Command an out-of-LOS bird via cross-link | [BLU-2](13-blue-cell-manual.md) (delivery paths); [05](05-core-concepts.md) "delivery paths" |

---

### Keeping this path current

This module is a training artifact under the same currency contract as the manuals: it is
maintained by the `08-vignette-development` skill, reviewed by `09-training-manual-review`, and
every rung's vignette ID must match a file in `spacesim/content/vignettes/` (FR-11310 — the path
covers the library exactly). When a vignette is added, moved, or retired, its rung here moves in
the same change set, and the [§15 traceability matrix](15-manual-traceability.md) vignette rows
move with it. The per-vignette playbooks the rungs link to are machine-verified by
`spacesim/tests/test_vignette_tutorials.py` (FR-11420).

> **Sources:** `spacesim/content/vignettes/*.yaml` · [`06-the-vignette-library.md`](06-the-vignette-library.md) ·
> [`11-vignette-playbooks.md`](11-vignette-playbooks.md) · FR-11310/11320/11420

---
