[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 7. The vignette library

The simulator ships 19 runnable vignettes split across the canonical 8 numbered scenarios, a
training scenario, and four expansion tracks (mission-set trials, Red COA library, learning
stream, novel concepts). Every vignette carries a per-cell **`intro_brief`** block authored in
its YAML and surfaced in the in-tool **Mission brief** panel (View ▾ → Mission brief). The brief
is the first thing a new operator should read.

### The canonical 8 numbered scenarios (start here)

| # | Title | Teaches |
|---|---|---|
| 1 | LEO ISR Denial | Pass windows; the collect-vs-downlink split; reversible vs. kinetic effects |
| 2 | GEO RPO Shadowing | Ambiguous RPO intent; custody decay in GEO |
| 3 | GNSS EW Campaign | Local, reversible PNT denial; MEO is kinetically safe |
| 4 | Co-Orbital Threat & Escort | Active defense: escort and maneuver-to-evade |
| 5 | DA-ASAT Crisis | Escalation, debris, attribution, political cost |
| 6 | SATCOM Cyber & Link | Ground/link segment; cyber acts outside passes |
| 7 | SDA Custody Hunt | Custody decay; sensor contention; breaking custody |
| 8 | Multi-Domain Capstone | Integrated campaign across every subsystem |

### Training onboarding

| ID | Title | Teaches |
|---|---|---|
| `training-basics` | Training: Basics | The core operator loop on a minimum-viable fleet (1 sat + 1 GS) |

### Track A — mission-set trials

| ID | Title | Teaches |
|---|---|---|
| `mt-isr-sar` | SAR ISR | SAR is all-weather/day-night; succeeds when EO fails |
| `mt-sigint-geolocate` | SIGINT Geolocation | Multi-pass TDOA/FDOA convergence |
| `mt-weather-collect` | Weather Collection | Cadence: SoC, eclipse, storage, downlink timing |

### Track B — Red COA library

| ID | Title | Teaches |
|---|---|---|
| `coa-russia-ml` | Russia ML — Sustained EW | Reversible deniable EW from Tirada-2 (SATCOM) and Pole-21 (GNSS); RB-109A Bylina coordinates |
| `coa-russia-md` | Russia MD — DA-ASAT + Cyber | Nudol-class kinetic with cyber surprise |
| `coa-china-ml` | China ML — Early Integrated Disruption | PLA SSF jam + cyber + RPO opening |
| `coa-china-md` | China MD — Decisive Counterspace Strike | Late-crisis A2/AD: kinetic + RPO + cyber + EW |
| `coa-misc-iran-ml` | Iran ML — Regional EW Spoiler | Non-spacefaring adversary contests ground |

### Track C — learning stream

| ID | Title | Teaches |
|---|---|---|
| `learn-intermediate-recovery` | Safe-Mode Recovery | Diagnose attack signature → reset → root-cause patch |

### Track D — novel concepts

| ID | Title | Teaches |
|---|---|---|
| `nv-isl-relay-debris` | ISL Relay + Debris-Corridor Maneuver | Out-of-LOS bird commanded via cross-link |

---

Every vignette is a YAML data file in `spacesim/content/vignettes/` — copy one to author your own.

**Where to find what:**
- **Mission brief panel** (View ▾ → Mission brief, auto-opens on first load) — situation,
  mission, friendly forces, threat picture, ROE, deadline, success criteria, tool tips.
- **Tutorial panel** (View ▾ → Tutorial panel) — per-cell move-by-move script for your current cell.
- [§11 vignette playbooks](11-vignette-playbooks.md) — the same move-by-move script as the
  Tutorial panel, in markdown form for offline review.

---
