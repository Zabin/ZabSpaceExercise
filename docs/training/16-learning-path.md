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
  Machine-verified by `test_vignette_tutorials.py` (FR-11420): Blue's script meets both objectives
  by the T+1 h deadline (its closing maneuver lands about T+11 h and cannot affect scoring); Red's
  jam always denies, while the cyber step is chance-based (~62% per attempt) and is retried. Cyber
  is ON by default (`cyber_authorized = true`); Red kinetic is OFF. Walkthrough: [04](04-guided-vignette.md).

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

After the ladder, go deep on a payload specialty. Order among these is free — pick your seat. Each has
a machine-verified step-by-step tutorial for both cells (in-app **View ▾ → Tutorial**) and a [§11 playbook](11-vignette-playbooks.md) entry.

| Vignette | New this rung | Read first |
|---|---|---|
| **`mt-isr-sar`** — SAR ISR | SAR is all-weather/day-night; succeeds where EO fails (deadline T+90 min) | [BLU-3/4](13-blue-cell-manual.md) (ISR beam modes); playbook [§11.9](11-vignette-playbooks.md) |
| **`mt-sigint-geolocate`** — SIGINT Geolocation | Multi-pass TDOA/FDOA convergence (deadline T+60 min). **Known limitation:** `characterize_emitter` is not yet reachable by orders; the tutorial says so and verifies the refusals | [BLU-4](13-blue-cell-manual.md); R129 (SIGINT geolocation); playbook [§11.12](11-vignette-playbooks.md) |
| **`mt-weather-collect`** — Weather Collection | Operations cadence: SoC, eclipse, storage, downlink timing (deadline T+60 min) | [BLU-5](13-blue-cell-manual.md) (bus health); playbook [§11.10](11-vignette-playbooks.md) |

### Stage 3 — Adversary doctrine (Track B, Red-focused)

The Red COA library — study these as Red's playbook of campaign shapes, or run them AI-Red as
White to give Blue a doctrinally-flavored opponent. Assumes Stage 1 mechanics.

| Vignette | New this rung | Read first |
|---|---|---|
| **`coa-russia-ml`** — Russia ML, Sustained EW | Reversible deniable EW, coordinated | [RED-5/8](14-red-cell-manual.md); [WCM-8](12-white-cell-manual.md) ; playbook [11.14](11-vignette-playbooks.md) |
| **`coa-russia-md`** — Russia MD, DA-ASAT + Cyber | Kinetic with cyber surprise | [RED-5/6/8](14-red-cell-manual.md) ; playbook [11.15](11-vignette-playbooks.md) |
| **`coa-china-ml`** — China ML, Early Integrated Disruption | Jam + cyber + RPO opening | [RED-4/5/6/8](14-red-cell-manual.md) ; playbook [11.16](11-vignette-playbooks.md) |
| **`coa-china-md`** — China MD, Decisive Strike | Late-crisis A2/AD: kinetic + RPO + cyber + EW | full [RED manual](14-red-cell-manual.md) ; playbook [11.17](11-vignette-playbooks.md) |
| **`coa-misc-iran-ml`** — Iran ML, Regional EW Spoiler | Non-spacefaring adversary contests the ground segment | [RED-5](14-red-cell-manual.md); [BLU-9](13-blue-cell-manual.md) (GS as terrain) ; playbook [11.18](11-vignette-playbooks.md) |

### Stage 4 — Depth & novelty (Tracks C, D)

Standalone deep-dives; take them when the relevant mechanic needs reinforcement.

| Vignette | New this rung | Read first |
|---|---|---|
| **`learn-intermediate-recovery`** — Safe-Mode Recovery | Diagnose signature → root-cause patch → recovery chain, end-to-end (deadline T+45 min; one-pass recovery by default) | [BLU-6/7](13-blue-cell-manual.md) (diagnose + recover); [05](05-core-concepts.md) "Safe-mode recovery"; playbook [§11.13](11-vignette-playbooks.md) |
| **`nv-isl-relay-debris`** — ISL Relay + Debris-Corridor Maneuver | Command an out-of-LOS bird via cross-link (deadline T+30 min) | [BLU-2](13-blue-cell-manual.md) (delivery paths); [05](05-core-concepts.md) "delivery paths"; playbook [§11.11](11-vignette-playbooks.md) |

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
> [`11-vignette-playbooks.md`](11-vignette-playbooks.md) · `spacesim/tests/test_vignette_tutorials.py` ·
> FR-11310/11320/11420

---
