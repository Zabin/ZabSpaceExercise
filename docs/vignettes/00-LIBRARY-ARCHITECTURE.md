# Vignette Library Architecture & Plan

[← Vignettes index](INDEX.md) · [↑ Docs index](../INDEX.md)

The vignette library is the **content layer** of the simulator — every exercise scenario is a YAML
file under `spacesim/content/vignettes/`, loaded by `content/vignette.py` and run by the same
deterministic engine. This document describes how the library is organized, what each track
exists to teach, and where in the doctrine literature each scenario lives.

> **Authority:** the engine contract (schema, channels, payload types, objective metrics) is
> documented in [`../build-spec/03-architecture-and-data.md`](../build-spec/03-architecture-and-data.md)
> and the matching code paths under `spacesim/engine/`. This document orchestrates *what*
> vignettes exist and *why* — not *how* the engine runs them.

---

## 1. Library structure (four tracks)

The library is partitioned into four pedagogical tracks. Each track answers a different question:

| Track | Question | Naming prefix | Audience |
|---|---|---|---|
| **A. Mission-set trials** | "What is it like to operate this *one* mission system, in isolation?" | `mt-*` | Bus & payload operators |
| **B. Red COA library** | "What does Red *do*? What is most-likely vs. most-dangerous for each adversary?" | `coa-*` | Blue + White-Cell (threat library) |
| **C. Learning stream** | "How does a student progress from basics to capstone?" | `learn-*` / `00-*` | Trainee operators |
| **D. Novel concepts** | "What does the simulator make possible that no current vignette explores?" | `nv-*` | Designers, advanced exercises |

The four tracks share one engine, one schema, and one set of access channels — they differ only in
content (asset mix, parameters, injects, objectives). A vignette can be promoted between tracks
as the library matures (today's "novel concept" can become tomorrow's "mission-set trial").

---

## 2. Section A — Mission-set individual trials

**Purpose.** Each operational space mission set has a distinctive rhythm (collection cadence,
output product, sensitivity to attack). A trainee should be able to encounter each one in
isolation, without the noise of integrated multi-domain pressure, before facing the capstone.

**Coverage:**

| Mission set | Payload type | Vignette ID | Status |
|---|---|---|---|
| Electro-optical ISR | `isr_eo` | `01-leo-isr-denial` | ✅ existing |
| Synthetic-aperture ISR | `isr_sar` | `mt-isr-sar` | ✅ new (this plan) |
| SATCOM (cyber-led story) | `satcom` | `06-satcom-cyber-link` | ✅ existing |
| SIGINT / ELINT geolocation | `sigint` | `mt-sigint-geolocate` | ✅ new (this plan) |
| Weather / environmental | `weather` | `mt-weather-collect` | ✅ new (this plan) |
| PNT / GNSS | `pnt` | `03-gnss-ew-campaign` | ✅ existing |
| SDA / custody | (sensor-driven) | `07-sda-custody-hunt` | ✅ existing |
| Space control (kinetic) | (effector) | `05-da-asat-crisis` | ✅ existing |

The three **new** mission-set trials fill the SAR / SIGINT / Weather gaps:

- **`mt-isr-sar`** — SAR's all-weather, day/night collection makes it a different problem than EO:
  longer dwell, larger downlink products, immunity to dazzle. Teaches **why** the joint commander
  asks for SAR in a specific weather/lighting condition.
- **`mt-sigint-geolocate`** — Three SIGINT passes from different geometries form a geolocation
  triangle. Teaches **multi-pass intelligence accumulation** rather than single-shot collection.
- **`mt-weather-collect`** — Routine collection cadence under benign threat, with a focus on
  storage management, downlink scheduling, and the bus-evolution game (eclipse, SoC, thermal).

---

## 3. Section B — Red COA library (most-likely / most-dangerous)

**Purpose.** "Threat library" canon for the White-Cell. Each adversary gets one **Most-Likely (ML)**
COA — what they'd realistically do day-to-day — and one **Most-Dangerous (MD)** COA — the worst
plausible outcome. White-Cell picks one to run; the same Blue fleet faces different doctrine.

**Doctrine sources:** `docs/research/01-doctrine-western.md`,
`docs/research/02-doctrine-non-western.md`, and the open-source canon (Secure World Foundation
*Global Counterspace Capabilities* 2025/26; CSIS Space Threat Assessment).

| Actor | ML scenario (vignette) | MD scenario (vignette) |
|---|---|---|
| **Russia (VKS)** | Sustained EW campaign vs. PNT + SATCOM (`coa-russia-ml`) | DA-ASAT debris strike + cyber link denial (`coa-russia-md`) |
| **China (PLA SSF)** | Early integrated jam + cyber + RPO at Taiwan opening (`coa-china-ml`) | Decisive kinetic + co-orbital + cyber + EW under A2/AD (`coa-china-md`) |
| **Misc (Iran / NK / proliferator)** | Regional EW spoiler vs. SATCOM and PNT (`coa-misc-iran-ml`) | (future) DA-ASAT proliferation crisis |

### Why ML/MD pairs (not just one threat per actor)

Doctrine analysts distinguish ML and MD because:
- **ML** drives day-to-day posture, custody priorities, and resource allocation. It's frequent.
- **MD** drives war reserves, escalation thresholds, debris policy. It's rare but defining.

A White-Cell that only ever runs MD scenarios (kinetic ASATs every time) trains Blue to over-react;
one that only runs ML (sustained EW only) trains Blue to under-react. **Both must be in the
library** and the choice between them is itself a White-Cell teaching point.

### Russia ML (`coa-russia-ml`) — sustained EW

Lead with pervasive, deniable, reversible electromagnetic attack on PNT and SATCOM — the workhorse
of Russian counterspace (Tirada-2 SATCOM jam, Pole-21 GNSS jam, RB-109A Bylina EW C2). No kinetic, no debris, no political ceiling.
Blue's task: **sustain service through chronic interference** — frequency-hop, shift users, request
SSN custody on the jammers.

### Russia MD (`coa-russia-md`) — kinetic + cyber under crisis

The Nov 2021 Nudol pattern: a DA-ASAT strike on a contested LEO satellite, generating tracked
debris, **plus** a coordinated cyber attack on a SATCOM ground modem during the crisis window.
Blue's task: **survive the kinetic strike** (maneuver, decoy, or accept loss) **while** keeping
SATCOM up under cyber pressure.

### China ML (`coa-china-ml`) — early integrated disruption

PLA SSF doctrine: seize the initiative at opening of conflict (e.g. Taiwan). Synchronized jam +
cyber + GEO RPO posturing in the first 30 minutes. No kinetic (held for escalation). Blue's task:
**maintain three mission streams** (ISR delivery, SATCOM availability, GEO custody) under
distributed pressure without burning Δv that's needed later.

### China MD (`coa-china-md`) — decisive counterspace strike

Late-crisis A2/AD finale: a confirmed-intent inspector approaches a Blue ISR satellite **and** a
DA-ASAT strike removes a key SATCOM relay **and** an EW campaign denies GNSS over the operational
theater. Blue's task: **triage** — which mission survives?

### Misc — Iran ML (`coa-misc-iran-ml`)

A regional EW spoiler: ground-based jamming of a Blue SATCOM downlink and a GPS user bubble over a
disputed region. No on-orbit threat. Demonstrates that even non-spacefaring adversaries can
contest Blue's space-enabled operations.

### Future Red COA expansions (not in this implementation)

- `coa-china-rpo-loiter` — sustained "Shijian" inspector loiter (intelligence + latent threat)
- `coa-russia-luch` — GEO RPO shadowing (Olymp-class persistent observer)
- `coa-india-ml` — DA-ASAT proliferation case ("Mission Shakti" lineage)
- `coa-nk-cyber` — opportunistic cyber on commercial SATCOM modems

---

## 4. Section C — Expanded learning stream

**Purpose.** The current learning stream goes from `00-training-basics` (≈30 min) directly to
`08-multi-domain-taiwan` (capstone). That's a steep cliff. The expanded stream adds one or more
intermediate vignettes that teach **one or two** integration patterns at a time.

| Step | Vignette | What it adds over the previous step |
|---|---|---|
| **1. Basics** | `00-training-basics` | Core loop: SOH, sensor task, command plan, execute at window |
| **2. Recovery** | `learn-intermediate-recovery` (NEW) | Multi-step safe-mode recovery: detect → contact → diagnose → patch → re-enable |
| **3. Coordination** | (future) `learn-multi-asset` | Two Blue assets, two Red effects, simultaneous decisions |
| **4. Capstone** | `08-multi-domain-taiwan` | Full integration; all mission sets under pressure |

The **`learn-intermediate-recovery`** vignette focuses on the safe-mode recovery chain (the most
operationally distinctive sequence in real satellite operations). It uses a single Blue ISR
satellite and a single Red cyber unit; Red drops the bus into safe mode and Blue must walk the
recovery script in the right order, observing telemetry signatures along the way.

---

## 5. Section D — Novel concepts

**Purpose.** Vignettes that exercise simulator capabilities not yet tested by any other scenario,
or that combine capabilities in unfamiliar ways. These are also a tool to expose engine gaps —
when an idea is hard to encode in YAML, the engine often needs a new primitive.

| Vignette | Capability exercised | Status |
|---|---|---|
| **`nv-isl-relay-debris`** | ISL command relay + debris-corridor maneuver planning | ✅ new (this plan) |
| (future) `nv-coalition-sda` | Coalition SDA feed (shared track catalog across blue + allied cell) | engine work needed |
| (future) `nv-mega-constellation` | 24-sat proliferated constellation resilience under jamming | content-only |
| (future) `nv-frequency-hop-ecccm` | Blue `def.frequency_hop` defeats Red jam; tests anti-jam ECCM | content-only |
| (future) `nv-spoof-vs-jam` | GNSS spoof (false signals) distinguished from GNSS jam (denial) | engine work needed |

**`nv-isl-relay-debris`** — Blue has two ISR sats, only one in view of any blue ground station;
the other can only be commanded via ISL relay. Mid-scenario a debris-corridor advisory arrives:
the second satellite must maneuver to avoid an estimated conjunction. The command must thread
through the ISL link, the maneuver consumes Δv, and the operator learns the
**ISL-relay-of-relay** workflow. This vignette exercises a code path (`engine/orders.py`
`_best_isl_window`) that no current vignette stresses end-to-end.

---

## 6. Authoring rules

When adding a vignette, follow these rules (encoded in the loader + tests):

1. **Satellite caps.** ≤24 orbital assets total, ≤3 per `group` (see `build-spec/01-context-and-scope.md` §3.1).
   Enforced by `content/vignette.build_world` since A1.
2. **Red doctrine profile must be in the canon.** One of `china_integrated`, `russia_ew_first`,
   `generic` — these are the profiles `session/redai.py` knows. Custom doctrines are future work.
3. **At least one Blue + one Red objective.** Even "training" vignettes follow the metric DSL so
   AAR replay can score them.
4. **Parameters expose White-Cell dials.** The default parameter set should be playable; advanced
   options (e.g. `red_ew_intensity`, `safe_mode_susceptibility`) belong in `parameters:`.
5. **Tutorials are optional but encouraged for `learn-*` vignettes.** A `tutorial:` block with
   per-cell step scripts (≥5 steps each) drives the manual walkthrough renderer.
6. **Coordinate naming convention.** IDs use kebab-case; asset IDs use ALL-CAPS-WITH-HYPHENS;
   the prefix on the vignette ID indicates the track (`mt-`, `coa-`, `learn-`, `nv-`).
7. **Realistic ground placement.** Ground stations, jammers, DA-ASAT sites, and sensors must use
   real-world coordinates from open sources — see [GROUND-INFRASTRUCTURE](GROUND-INFRASTRUCTURE.md).
   Validated by `test_vignette_library.test_known_site_coords_match_canonical` and the
   "no origin / no ocean dead-zone" sanity tests.

---

## 7. Registry — complete vignette manifest (post-plan)

After this plan lands the library contains **19 vignettes**:

### Original 9
`00-training-basics`, `01-leo-isr-denial`, `02-geo-rpo-shadowing`, `03-gnss-ew-campaign`,
`04-co-orbital-threat-escort`, `05-da-asat-crisis`, `06-satcom-cyber-link`,
`07-sda-custody-hunt`, `08-multi-domain-taiwan`

### Section A additions (3) — mission-set trials
`mt-isr-sar`, `mt-sigint-geolocate`, `mt-weather-collect`

### Section B additions (5) — Red COA library
`coa-russia-ml`, `coa-russia-md`, `coa-china-ml`, `coa-china-md`, `coa-misc-iran-ml`

### Section C additions (1) — learning stream
`learn-intermediate-recovery`

### Section D additions (1) — novel concepts
`nv-isl-relay-debris`

All 10 new vignettes are validated by `spacesim/tests/test_vignette_library.py`: each must load,
build a world that respects the satellite caps, start a session, evaluate objectives, and render
both cells' views without error.

---

## 8. Roadmap

**v1.1 candidates** (deferred but slotted):
- `coa-china-rpo-loiter`, `coa-russia-luch`, `coa-india-ml`, `coa-nk-cyber`
- `learn-multi-asset` (Section C step 3)
- `nv-coalition-sda`, `nv-mega-constellation`, `nv-frequency-hop-eccm`

**Engine work required for additional vignettes** (tracked in [`../FUTURE-WORK.md`](../FUTURE-WORK.md)):
- Coalition SDA / shared-track-catalog primitive (§9 strategic)
- GNSS spoof distinct from GNSS jam (extends `effects.py` outcome set)
- Conjunction screening + `prop.collision_avoid` (§3 catalog-verb gap, also needed for `nv-isl-relay-debris` to fully realize)

All future expansions follow the same four-track structure described in §1.
