[← Build Spec index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 17. Mock Space Surveillance Network (SSN)

**Status:** ✅ Implemented — `spacesim/engine/ssn.py`, `spacesim/session/manager.py`,
`spacesim/ui_web/server.py`, `spacesim/ui_web/static/app.js`, `spacesim/tests/test_ssn.py`.
Incomplete items are in `docs/FUTURE-WORK.md` §7.

### 17.1 Purpose

Adds a per-cell **request-and-wait** surveillance capability alongside organic (direct-control)
sensors. An operator submits a request to the network; the network schedules a collection window,
performs the measurement, and delivers a Track product after a processing delay — subject to
coverage, dispersion, and queue depth. The gap between organic (immediate, you own the geometry)
and SSN (delayed, someone else's geometry and queue) is the pedagogical point.

### 17.2 Per-cell network model

Each enabled cell owns one `SSNNetwork`:

- **Blue** → `BLUE-SSN`, **coalition** affiliation: broader coverage but a shared-queue processing
  delay bonus (+50%) and one less concurrency slot than the raw preset.
- **Red** → `RED-SSN`, **national** affiliation: preset used as-is (full concurrency, raw delay).

Network `Sensor` objects carry `network: bool = True` so they are hidden from the organic-tasking
picker and reached only via a request. White Cell (god-view) sees both networks, request queues,
and coverage maps.

### 17.3 Dispersion presets

| Preset | Ground sites | Geography | Regime mix | Space-based | Concurrency |
|---|---|---|---|---|---|
| `sparse` | ~3 | one region | radar (LEO/MEO) | 0 | 1 |
| `regional` | ~5–6 | one hemisphere | radar + optical (LEO→GEO over region) | 0 | 2 |
| `global` | ~8–12 | worldwide | radar + optical | 1 (GEO belt) | 3 |
| `proliferated` | ~16+ | worldwide, redundant | radar + optical | 2–3 (incl. cislunar) | 5 |

`instantiate_network(world, cell, dispersion)` generates named sites (e.g. `BLUE-SSN-RDR-1`)
at fixed deterministic lat/lons and registers them as `Sensor` objects.

### 17.4 Coverage model

Coverage = **phenomenology** (sensor type vs. regime) × **geometry** (access windows within the
SLA horizon). Sensor-type rules:

| Sensor type | LEO | MEO | GEO | Cislunar |
|---|---|---|---|---|
| `ground_radar` | ✅ | ✅ | ⚠ weak | ❌ |
| `ground_optical` | ⚠ fast | ✅ | ✅ best | ⚠ |
| `space_based` | ✅ | ✅ | ✅ | ✅ |

A radar-only (`sparse`) net **cannot service GEO** — an intentional, teachable gap.

### 17.5 Request model

```
SSNRequest fields:
  id, cell, intent (search|track|characterize), target, regime (LEO|MEO|GEO|cislunar),
  priority (routine|priority|immediate), submitted_at,
  assigned_sensor, collect_at, product_at,
  state (SUBMITTED|SCHEDULED|COLLECTING|DELIVERED|FAILED|CANCELLED)
```

Priority SLA horizons: `immediate` 15 min, `priority` 60 min, `routine` 6 h.

### 17.6 Hybrid turnaround

At submission (deterministic, not replayed):
1. Select eligible sensors (type × regime).
2. Find the earliest `sensor_observation` window within `[now, now + max_wait[priority]]`.
3. `collect_at` = that window start (sooner than max_wait if a window opens early).
4. `product_at` = `collect_at + processing_delay[priority]` × coalition/saturation modifiers.
5. No viable window → `FAILED: no_coverage_within_sla`.

Processing delays: `routine` 30 min, `priority` 10 min, `immediate` 2 min;
coalition adds ×1.5; each request over the concurrency cap adds another full delay.

### 17.7 Deterministic two-event pipeline

Two scheduled events on the engine log (replay-safe):

- **`ssn_collect`** at `collect_at` — samples the target's true orbit at that instant; stages in
  `world.ssn_staged[rid] = {"orbit": ..., "quality": float}`. Pure handler; not yet visible to
  the requester.
- **`ssn_deliver`** at `product_at` — pops staged data, applies `Track` update
  (`confidence` scaled by `0.5 + 0.5 × window_quality`; `characterized=True` for characterize
  intent), posts a feed message.

Cancel before collect: `tag_skip` both events; `world.ssn_staged` is never written; replay is
byte-identical. `world.ssn_staged` is a `WorldState` field (committed to replay) so `_h_deliver`
is a pure `(world, payload)` handler — no per-instance Python state involved.

### 17.8 Contention & capacity

Per-sensor booking reuses the existing `OrderSystem._sensor_bookings` mechanism. Network
concurrency cap: the *(N+1)*th request in-flight receives a saturation-delay penalty; `immediate`
priority may preempt `routine` requests.

### 17.9 Data model additions

- `Sensor.network: bool = False` (`engine/entities.py`) — marks a network (non-organic) sensor.
- `Asset.threat_warning: bool = False` (`engine/entities.py`) — set by `def.set_threat_warning`.
- `WorldState.ssn_staged: dict = {}` (`engine/world.py`) — in-flight collection staging.
- `VignetteContext.ssn_networks: dict` (`content/vignette.py`) — per-cell instantiated networks.

### 17.10 Session / API

`SessionManager` exposes `submit_ssn_request`, `list_ssn_requests`, `cancel_ssn_request`,
`ssn_coverage`; `InProcessSession` adds passthroughs; `save_state`/`from_state` persist and
rebuild the request registry + in-flight counters + bookings.

| Endpoint | Purpose |
|---|---|
| `POST /ssn/{cell}/request` | Submit → `SSNAck` (ok, collect_at, product_at) or FAILED+reason |
| `GET /ssn/{cell}/requests` | Cell's request queue/history (fog-filtered) |
| `POST /ssn/{cell}/cancel` | Cancel a not-yet-collected request |
| `GET /ssn/{cell}/coverage?regime=` | Coverage summary + next viable window |

### 17.11 UI integration

The tasking rail (`§16.7`) adds a **mode toggle**: Organic / SSN Request. SSN mode shows:
- regime selector + intent/priority pickers;
- a **coverage preview** (`/ssn/{cell}/coverage?regime=`) before submission;
- estimated `collect_at → product_at` so the operator weighs SSN-wait vs. organic tasking;
- live request queue with per-row cancel buttons.

Network sensors are filtered out of the organic actor/sensor pickers (`sensor.network`).

### 17.12 Vignette opt-in

Off by default. Enabled via `ssn_blue_dispersion` / `ssn_red_dispersion` parameters:

| Vignette | Blue | Red | Teaching point |
|---|---|---|---|
| V7 SDA Custody Hunt | `global` | off | request-and-wait + network saturation |
| V8 Multi-Domain Capstone | `proliferated` | `regional` | asymmetric coverage + both sides request |
| V2 GEO RPO Shadowing | `regional` | off | optional characterization of GEO inspector |

### 17.13 Failure modes

| Situation | Outcome | Operator sees |
|---|---|---|
| Radar-only net, GEO target | `FAILED: no_coverage_regime` | "no optical/space-based — GEO not serviceable" |
| No window within SLA | `FAILED: no_coverage_within_sla` | "no pass within priority window" |
| Cancel before collect | `CANCELLED` | row removed from queue |
| Network at capacity | accepted + delayed | turnaround estimate increases |

### 17.14 Acceptance tests (`spacesim/tests/test_ssn.py`)

- Coverage matrix: `sparse` fails GEO with `no_coverage_regime`; `global` services it; all
  non-empty presets service LEO.
- Hybrid turnaround: `collect_at` within SLA; `product_at = collect_at + processing_delay`;
  coalition multiplier applied; national net uses raw delay.
- Delivery: characterized track in Blue's catalog after `advance_to(product_at + 1)`; replay
  byte-identical.
- Cancel-before-collect: no track lands; replay byte-identical.
- Window quality: low-quality geometry (`quality=0.1`) delivers measurably lower confidence.
- Fog: Red cannot see Blue's requests/coverage; White sees both.
- Save/resume: in-flight request survives `save_state`/`from_state`; events still fire.
- Harden: `def.harden` reduces safe-mode probability at the effect resolver.
- Engage gate: SSN characterize that yields a weapons-quality track unlocks a previously blocked
  kinetic engagement.
