# Mock Space Surveillance Network (SSN) — Design Plan

**Document type:** Feature design plan (to be implemented later to augment the tool)
**Status:** Proposal — design only; no engine/UI code in this document
**Audience:** Claude Code (implementer), White Cell facilitators, reviewers
**Companions:** `11-command-planning-and-tasking.md` (Part B sensor tasking — esp. *shared/coalition
feeds*), `07-sda-custody-hunt.md` (the SDA vignette), `05-cell-interfaces.md`, `09-gui-principles.md`,
`00-BUILD-SPECIFICATION.md` §16.7 (tasking rail).
**Implemented surfaces reused:** `spacesim/engine/access.py` (`AccessProvider`, `sensor_observation`
channel), `spacesim/engine/entities.py` (`Sensor`), `spacesim/engine/custody.py` (`Track`, decay),
`spacesim/engine/orders.py` (`observe` execution + contention), `spacesim/session/{manager,scene}.py`,
the deterministic scheduler/event-log, and the fog-of-war boundary in `CellController`.

**Decisions taken (confirmed with the user):**
- **Per-cell networks** — each cell submits to *its own* network: Blue → an **allied coalition SSN**,
  Red → a **national SSN** (potentially at different dispersion). Both sides get the capability.
- **Hybrid turnaround** — priority sets a *max wait*; if a real collection window opens sooner it is
  used; a **processing/dissemination delay** is then added before the product is delivered.
- **Four dispersion presets** — `sparse / regional / global / proliferated`, each setting site count,
  geographic spread, regime sensor mix, space-based count, and network concurrency.
- **Per-vignette opt-in** — off by default; enabled via `ssn_*` parameters; on in the SDA custody-hunt
  (V7) and capstone (V8) vignettes, optional elsewhere.

---

## 1. Purpose & concept

Today an operator only has **organic sensors** — the cell's own radars/optics/inspectors that it
tasks directly (`observe` / `sda.task_*`). Real space operators also draw on a **Space Surveillance
Network**: a dispersed, multi-site, multi-phenomenology sensor enterprise (radars, optical
telescopes, space-based observers) operated by a service/coalition, to which a unit **submits a
request for collection** and later **receives a product** (a track update / characterization) after
the network schedules, collects, processes, and disseminates it.

This feature adds a **mock SSN** so that, in selected vignettes, an operator can **submit a request
for an observation effect** against a target (or search volume) and have a realistic, dispersed
network fulfill it — subject to **coverage** (does the network reach that regime/geometry?),
**dispersion** (how dense/global is it?), and **turnaround** (how long until the product lands?).

It augments, rather than replaces, organic tasking: organic sensors are *direct control, immediate
intent, you own the geometry*; the SSN is *request-and-wait, broad coverage, someone else's geometry
and queue*. Teaching the difference — and the cost of depending on a network you don't control — is
the point. This is the realization of the **"shared/coalition feeds"** bullet in
`11-command-planning-and-tasking.md` §B.2, generalized to a per-cell national/coalition enterprise.

> **What "request for effects (observations)" means here:** the operator does not click an enemy and
> read truth. They submit a *request* (intent + target/volume + priority). The network returns a
> **Track update** (position/uncertainty, and optionally characterization) into the requesting cell's
> belief catalog — fog-respecting, confidence-bearing, and only as good as coverage allowed.

---

## 2. Concepts & terminology

| Term | Meaning |
|---|---|
| **SSN** | The dispersed sensor enterprise a cell can task by request (not by direct control). |
| **Network sensor** | A `Sensor` flagged as belonging to a cell's SSN (vs. an organic, hand-tasked sensor). |
| **Request** | A collection request: `{requester cell, intent, target|volume, regime, priority, submitted_at}`. |
| **Product** | The deliverable: a `Track` update (state + uncertainty, ± characterization), delivered after turnaround. |
| **Coverage** | Whether the network has a sensor of the right phenomenology *and* viable geometry for the target's regime, within the request horizon. |
| **Dispersion** | How many sites, how globally spread, and which regimes the network can see — a White-Cell preset. |
| **Turnaround / SLA** | Time from submission to product delivery: queue + collection-window wait + processing/dissemination delay. |
| **Concurrency cap** | How many requests the network can service at once (a capacity limit per preset). |

Organic vs. network is a **role distinction on `Sensor`**, not a new sensor physics model — network
sensors use the exact same `AccessProvider.sensor_observation` geometry (elevation mask for radar,
lighting for optical, LOS+range for space-based).

---

## 3. Per-cell network model

Each cell owns one network instance:

- **Blue** → `BLUE-SSN` (allied **coalition** feed): typically broader/more global, but "someone
  else's" — lower control, queue priority shared with notional partners (modeled as a higher base
  processing delay / lower concurrency relative to dispersion).
- **Red** → `RED-SSN` (**national**): may be denser in a region but narrower globally, depending on
  the chosen preset.

A network's sensors are `Sensor` objects with `owner == cell` and a marker `network: true` (so they
are *not* shown as directly-taskable organic sensors in the order panel; they are reached only via a
request). **Fog:** a request and its product belong to the requesting cell; the other cell never sees
either (enforced at the `CellController`/SessionManager boundary, like all reads).

White Cell (god-view) can see both networks, both request queues, and coverage maps, for adjudication.

---

## 4. Dispersion presets

A single enum `dispersion` per network (set per cell, per vignette). Each preset fixes the site
count, geographic spread, regime sensor mix, space-based count, network concurrency, and a base
processing-delay character. Concrete instantiation is **data** (auto-generated sites at fixed
lat/lons, or authored in the vignette).

| Preset | Sites (ground) | Geography | Regime mix | Space-based | Concurrency | Turnaround character |
|---|---|---|---|---|---|---|
| `sparse` | ~3 | one region | radar only (LEO/MEO) | 0 | 1 | big gaps; long waits; GEO uncovered |
| `regional` | ~5–6 | one hemisphere | radar + optical (LEO→GEO over region) | 0 | 2 | good regional, poor global; medium waits |
| `global` | ~8–12 | worldwide | radar + optical | 1 (GEO belt) | 3 | near-global LEO→GEO; short-medium waits |
| `proliferated` | ~16+ | worldwide, redundant | radar + optical | 2–3 (incl. cislunar) | 5 | fast, global, deep; short waits, few gaps |

Notes:
- The **coalition (Blue)** flavor applies a modifier: +1 site tier of spread but a higher base
  processing delay and one less concurrency than the raw preset (you benefit from partners' coverage
  but wait in a shared queue). A national (Red) network uses the preset as-is.
- Presets generate **named sites** (e.g. `BLUE-SSN-RDR-1`, `…-OPT-3`, `…-SBO-1`) so they appear on
  the belief map / coverage panel and so White Cell can see them.
- Sites are placed on a fixed, deterministic lat/lon schedule per preset (e.g., a longitude-spread
  ring + a couple of high-latitude sites) so coverage is reproducible.

---

## 5. Coverage model (global, and LEO → GEO)

Coverage answers: *can this network observe a target in regime R, with viable geometry, within the
request horizon?* It is the product of **phenomenology** (sensor type vs. regime) and **geometry**
(the existing access windows).

**Sensor-type → regime suitability** (drives which network sensors are *eligible* for a request):

| Sensor type | LEO | MEO | GEO | Cislunar/HEO-apogee | Constraints |
|---|---|---|---|---|---|
| `ground_radar` | ✅ best | ✅ | ⚠ weak (range) | ❌ | weather-independent; elevation mask |
| `ground_optical` | ⚠ fast-mover | ✅ | ✅ best | ⚠ (bright only) | needs target sunlit **and** site in darkness |
| `space_based` | ✅ | ✅ | ✅ | ✅ | LOS + range; reaches what the ground can't |

**Global coverage** is a function of site longitude/latitude spread: a target's regime + sub-point
must fall within some site's access geometry. `sparse`/`regional` leave **coverage gaps** (a LEO
target over an unserved longitude, or any GEO target if there is no optical/space-based sensor); the
request then returns **"no coverage"** (a teachable outcome) or queues until the target drifts into
coverage (within the SLA horizon).

**LEO → GEO specifically:**
- **LEO** — radar-dominant; many short windows; dense networks reacquire quickly.
- **MEO** — radar or optical; longer windows.
- **GEO** — optical (night + sunlit target) or space-based; a radar-only `sparse` net **cannot** do
  GEO at all (intended gap).
- **Cislunar/HEO apogee** — space-based only; only `proliferated` (with a cislunar observer) reaches.

Coverage is computed by reusing `AccessProvider.windows(sensor, target, sensor_observation, now,
horizon)` across the network's eligible sensors; a non-empty window within the horizon = covered.

---

## 6. The request model

A request is a `PlannedActivity` of a new kind `ssn_request` (parallel to `command`/`collection`):

```yaml
ssn_request:
  id:
  cell:            blue | red                 # requester (fog scope)
  intent:          search | track | characterize
  target_ref:      <object id>                # for track/characterize
  search_volume:   {regime, lon/lat bounds}   # for search
  regime:          LEO | MEO | GEO | cislunar # routes to eligible sensor types
  priority:        routine | priority | immediate
  submitted_at:    SimTime
  # filled by the network at submission:
  assigned_sensor: <network sensor id> | null
  collect_at:      SimTime | null             # chosen collection window start
  product_at:      SimTime | null             # collect_at + processing delay
  state:           SUBMITTED | SCHEDULED | COLLECTING | DELIVERED | FAILED {reason}
  expected_yield:  detect | track_update | characterization
```

- **Intents** map to the existing tasking semantics (search finds new objects; track shrinks an
  object's uncertainty; characterize resolves type → can unlock the weapons-quality gate).
- **Priority** sets the **max-wait horizon** (SLA) and the **processing delay** (see §7).
- A request is **fog-scoped** to its `cell`. Products land only in that cell's `TrackCatalog`.

---

## 7. Turnaround — the hybrid model

Turnaround = **queue → collection-window wait → processing/dissemination delay**.

### 7.1 Parameters (White-Cell-tunable; defaults below)
```
max_wait[priority]      = { immediate: 15 min, priority: 60 min, routine: 6 h }   # SLA horizon
processing_delay[prio]  = { immediate:  2 min, priority: 10 min, routine: 30 min } # ground proc + fusion + dissem
coalition_delay_bonus   = +50% processing_delay for a coalition (Blue) network    # shared queue
saturation_delay        = +1 processing_delay per request over the concurrency cap # network busy
```

### 7.2 Resolution (at submission, deterministic)
1. **Eligibility:** select network sensors whose type suits `regime` (§5) and that are not at
   capacity.
2. **Earliest viable window:** across eligible sensors, find the earliest `sensor_observation` window
   start `w` within `[now, now + max_wait[priority]]` (reuse `AccessProvider`).
3. **Hybrid rule:**
   - if a window `w` exists within the SLA horizon → `collect_at = w` (use the *sooner* real
     opportunity, even if before max_wait — that's the "hybrid" advantage);
   - else → the request **FAILS** with `no_coverage_within_sla` (the gap is real and teachable).
4. **Processing:** `product_at = collect_at + processing_delay[priority] (+ coalition/saturation
   modifiers)`.
5. **Assignment:** record `assigned_sensor`, `collect_at`, `product_at`; book the sensor for that
   window (contention, §9).

### 7.3 Execution (deterministic, replay-safe)
Two scheduled events on the engine timeline (both logged → reproduced exactly on replay):
- `ssn_collect` at `collect_at` — performs the measurement (samples the target's true state at that
  instant; like `observe`), staged but **not yet visible** to the requester.
- `ssn_deliver` at `product_at` — applies the staged measurement to the **requesting cell's** Track
  (confidence ↑, uncertainty ↓, characterization set if intent=characterize and the sensor is
  capable), and posts a feed message "SSN product delivered: <object>".

### 7.4 Worked timeline (example)
```
T+00:00  Blue submits: characterize RED-INSP (GEO), priority
T+00:00  network: eligible = optical + space-based; earliest viable optical window at T+00:18
         (target sunlit, site dark); collect_at=T+00:18; product_at=T+00:18+10m=T+00:28
T+00:18  ssn_collect — measurement staged
T+00:28  ssn_deliver — RED-INSP track in Blue's catalog: characterized, uncertainty collapsed
         feed: "SSN product delivered: RED-INSP (characterized)"
```
If Blue had only a `sparse` (radar-only) network, the same GEO request returns **FAILED:
no_coverage_within_sla** at submission — Blue must use organic optics or accept the gap.

---

## 8. Determinism, fog, and product quality

- **Determinism:** selection happens live at submission (not replayed); the *effects* (`ssn_collect`,
  `ssn_deliver`) are scheduled events in the log, so replay/rewind/AAR reproduce the exact catalog.
  Like all derived signals, no wall-clock or extra RNG is used; any roll (e.g., degraded product)
  draws the seeded engine RNG inside the `ssn_collect` handler so it stays in-state.
- **Fog:** request, queue, and product are visible only to the requester; White sees all. A product
  is a **belief** `Track` with confidence/uncertainty — never ground truth.
- **Product quality:** scales with sensor capability + geometry quality (window `quality`): a poor
  grazing pass yields a lower-confidence track / larger uncertainty; characterization may **fail**
  ("insufficient — re-request") on a weak geometry. Products **decay** after delivery like any track
  (custody must be sustained with follow-on requests), reinforcing the dependency cost.

---

## 9. Contention & capacity

- **Per-sensor:** one collection at a time (reuse the existing sensor-booking contention).
- **Network concurrency cap** (per preset): at most *N* in-flight requests; the *(N+1)*th adds a
  `saturation_delay` (and `immediate` requests may preempt `routine` ones, bumping the routine's
  `collect_at` to the next window). The UI shows queue depth and estimated turnaround.
- **Teaching point:** in V7 (custody hunt) a thin network forces prioritization — sustaining custody
  of one object via the SSN means *not* covering another; Red can exploit network saturation.

---

## 10. Data model additions

```yaml
# vignette parameters (per cell)
ssn_blue: {enabled: true,  dispersion: global,       affiliation: coalition}
ssn_red:  {enabled: true,  dispersion: regional,     affiliation: national}

# Sensor gains a flag (engine/entities.py)
Sensor: { ..., network: bool = false }      # network sensors are request-only, not hand-tasked

# Network instance (engine or session level)
SSNNetwork:
  cell:            blue | red
  affiliation:     coalition | national
  dispersion:      sparse | regional | global | proliferated
  sensors:         [<network sensor ids>]
  concurrency:     int                       # from preset (± affiliation)
  base_delay_s:    {routine, priority, immediate}
```

`build_world` (in `content/vignette.py`) instantiates each enabled network from its preset:
generates the named sites, tags them `network: true, owner: <cell>`, and registers the `SSNNetwork`.
Requests are tracked in a registry like `OrderSystem.orders` (so they list/cancel and survive
save/resume by the same mechanism).

---

## 11. Engine / session / API integration

A small **`SSNSystem`** (session layer, mirrors `OrderSystem`/`RedDoctrine`) that:
- holds the per-cell `SSNNetwork`s and a request registry;
- registers handlers `ssn_collect` and `ssn_deliver` on the `Simulation`;
- exposes `submit_request(cell, request) -> SSNRequestAck` (does §7.2 resolution + schedules events),
  `list_requests(cell)`, `cancel_request(cell, id)` (cancel-before-collect, replay-safe via the
  scheduler `tag` mechanism), and `coverage(cell, regime) -> {covered, sensors, next_window}`.

**SessionManager** gets thin pass-throughs (`request_ssn`, `list_ssn`, `ssn_coverage`); **InProcessSession**
+ **FastAPI** add:

| Endpoint | Purpose |
|---|---|
| `POST /sessions/{sid}/ssn/{cell}/request` `{intent,target,regime,priority,...}` | Submit a request → ack (assigned sensor, collect_at, product_at) or FAILED+reason |
| `GET /sessions/{sid}/ssn/{cell}/requests` | The cell's request queue/history (fog) |
| `POST /sessions/{sid}/ssn/{cell}/cancel` `{request_id}` | Cancel a not-yet-collected request |
| `GET /sessions/{sid}/ssn/{cell}/coverage?regime=` | Coverage summary + next viable window per regime |

It **reuses** `AccessProvider`, the `observe`/`Track` update path, contention, the scheduler/eventlog,
and the fog boundary — so the deterministic guarantees and tests already in place extend to it.

---

## 12. UI integration (augments the operator console)

In the **Tasking rail** (`00-BUILD-SPECIFICATION.md` §16.7) add a toggle: **Organic** vs **SSN request**.
When SSN is selected:

```
DECISION › Request SSN observation                         network: BLUE-SSN (coalition · global)
  Intent:  ( ) Search  (•) Characterize  ( ) Track     Target: RED-INSP (GEO)
  Priority: ( ) routine  (•) priority  ( ) immediate
  Coverage: ✅ optical @ T+00:18  ·  space-based @ T+00:41   (radar: ✗ regime GEO)
  Est. turnaround: collect ~T+00:18 → product ~T+00:28        [ Submit request ]
  ─ Requests ───────────────────────────────────────────────────────────────────
  #SSN-3 characterize RED-INSP  priority   SCHEDULED  collect T+00:18 → product T+00:28  [✕]
```

- The **coverage line** is computed from `/ssn/coverage` and answers "can the network even do this?"
  *before* submission (P4 "why can't I?" — e.g. "GEO: no optical/space-based in this network").
- The **estimate** shows collect→product times (the SLA), so the operator weighs SSN-wait vs.
  tasking an organic sensor.
- Delivered products appear in the **Track panel / belief map** exactly like organic reports (the
  uncertainty volume collapses on delivery), and a **feed** line announces them.
- A small **Coverage panel** (White Cell + owning operator) overlays network sites + their
  regime reach on the 2D/3D belief map (network sites drawn as a distinct glyph).

---

## 13. Vignette wiring (per-vignette opt-in)

Default **off**. Enabled where it teaches the most:

- **V7 SDA Custody Hunt** — Blue `global` coalition SSN; the lesson is **request-and-wait + network
  saturation** vs. Red trying to break custody. Turnaround and concurrency make prioritization bite.
- **V8 Multi-Domain Capstone** — Blue `proliferated` coalition; Red `regional` national — both sides
  request, coverage asymmetry is a planning factor.
- **V2 GEO RPO Shadowing** — optional Blue `regional` (optical-capable) to characterize the inspector
  if organic optics are scarce.
- Others: leave off unless a scenario specifically wants the network dependency.

Example vignette block:
```yaml
parameters:
  - {id: ssn_blue_dispersion, label: "Blue SSN dispersion", type: enum,
     options: [off, sparse, regional, global, proliferated], default: global}
  - {id: ssn_red_dispersion,  label: "Red SSN dispersion",  type: enum,
     options: [off, sparse, regional, global, proliferated], default: regional}
```

---

## 14. Failure modes & edge cases (all surfaced with reasons)

| Situation | Outcome | Operator sees |
|---|---|---|
| No eligible sensor type for regime (e.g. radar-only net, GEO target) | `FAILED: no_coverage_regime` | "Network has no optical/space-based — GEO not serviceable" |
| Eligible but no window within SLA horizon | `FAILED: no_coverage_within_sla` | "No pass within the priority window — raise priority or wait" |
| Network at concurrency cap | accepted but delayed | "Network saturated — turnaround +Δ" |
| Assigned sensor jammed/dazzled (own a network sensor under EW/DE) | degraded/failed product | lower-confidence track or "collection failed — re-request" |
| Target lost/destroyed before collect | `FAILED: target_lost` | feed note |
| Cancel before collect | `CANCELLED` (replay-safe) | row removed from queue |

---

## 15. Tests & acceptance (planned)

- **Coverage matrix:** a `sparse` (radar-only) net FAILS a GEO request with `no_coverage_regime`; a
  `global` net services it; LEO is serviced by all non-empty nets.
- **Hybrid turnaround:** `collect_at` = earliest viable window ≤ `max_wait[priority]`; `product_at` =
  `collect_at + processing_delay`; coalition adds the delay bonus; out-of-SLA → FAILED.
- **Determinism:** a request's `ssn_collect`/`ssn_deliver` replay byte-identically; cancel-before-
  collect leaves replay identical (the event never logs).
- **Fog:** Red cannot see Blue's requests/products/coverage; products land only in the requester's
  catalog.
- **Custody loop:** an SSN `characterize` that yields a weapons-quality track unlocks a
  previously-blocked engagement (same gate the engine enforces).
- **Save/resume + AAR:** in-flight requests survive save/resume and scrub correctly.

## 16. Phasing
1. **SSN-1 model+coverage:** `Sensor.network` flag, `SSNNetwork` + preset generation in `build_world`,
   `coverage()`; tests for the coverage matrix.
2. **SSN-2 requests+turnaround:** `SSNSystem.submit_request` (hybrid resolution), `ssn_collect`/
   `ssn_deliver` handlers, request registry + cancel; determinism/turnaround tests.
3. **SSN-3 API:** the four endpoints (fog-filtered) + save/resume of requests.
4. **SSN-4 UI:** tasking-rail SSN mode, coverage line + turnaround estimate, requests queue, coverage
   overlay on map/3D.
5. **SSN-5 vignettes:** wire `ssn_*` params into V7/V8 (+optional V2); manual + screenshots.

## 17. Open questions / future
- **Cost/credits:** should priority/immediate consume a finite "collection budget" to force triage?
  (Recommended as a later balance dial.)
- **Quality model fidelity:** map window `quality` → product confidence curve (tune per regime).
- **Commercial/third-party feeds:** a neutral commercial provider both cells can buy from (extends
  the per-cell model).
- **Cueing across organic + SSN:** let an organic detection auto-cue an SSN characterize request.

## 18. Glossary
- **SSN** — the dispersed, request-tasked surveillance network (vs. organic, hand-tasked sensors).
- **Request / product** — submitted intent / the delivered belief Track update.
- **Coverage** — phenomenology (sensor type vs regime) × geometry (access windows) within the SLA.
- **Dispersion preset** — `sparse/regional/global/proliferated`; sets sites, spread, regime mix,
  concurrency, base delay.
- **Turnaround (hybrid)** — earliest viable window within the priority's max-wait, plus a
  processing/dissemination delay; coalition and saturation add delay.
- **Affiliation** — `national` (preset as-is) vs `coalition` (broader coverage, shared-queue delay).
