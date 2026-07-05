# R109 — Sensor Operations

> **Document ID:** R109
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R101](R101-orbital-mechanics-for-operations.md)
> **Referenced By:** [R102](R102-space-domain-awareness.md), [R104](R104-collection-management.md), [R118](R118-space-surveillance-networks.md), [R119](R119-space-situational-data-fusion.md), [R129](R129-sigint-collection-and-geolocation-accuracy.md), [R134](R134-pnt-warfare-and-navigation-denial-operations.md), [R137](R137-bus-and-payload-parameter-catalog.md), FS-104
> **Produces:** implementation constraints for [`engine/entities.py`](../../../spacesim/engine/entities.py) (`Sensor`), [`engine/isr.py`](../../../spacesim/engine/isr.py)
> **Feature Mapping:** FS-104 (SDA Tasking)
> **Related Topics:** [R102](R102-space-domain-awareness.md) (Space Domain Awareness), [R104](R104-collection-management.md) (Collection Management), [R118](R118-space-surveillance-networks.md) (Space Surveillance Networks)
> **Last Reviewed:** 2026-07-05
> **Primary Sources Consulted:** 3

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

A "sensor" in this simulator is a specific, narrow entity (`Sensor`) with an access predicate and a
beam-mode database behind it ([`engine/isr.py`](../../../spacesim/engine/isr.py)) — this topic gives an implementer the concrete model
so a new sensor type is wired consistently rather than as a bespoke one-off.

## 2. Scope

Covers: the `Sensor` access-predicate split (space-based vs. ground), the beam-mode swath/
resolution/power trade, and collection's coupling to host power. Does **not** cover: the SDA
chain stage sensors advance ([R102](R102-space-domain-awareness.md)), tasking contention ([R104](R104-collection-management.md)), or the SSN's
aggregation of multiple sensors into a network ([R118](R118-space-surveillance-networks.md)).

## 3. Concepts

**Sensors come in two access flavors: `space_based` and ground.** `AccessProvider._observation_predicate`
branches on `sensor.kind`: a space-based sensor's access depends on range/line-of-sight/lighting to
another satellite computed from both orbits; a ground sensor's access depends on elevation mask,
range, and (if `needs_lighting`) both target sunlit-state and the sensor site being in darkness
(`twilight_deg`) — modeling the real constraint that an optical ground sensor needs both a lit
target and a dark sky.

**Beam mode trades swath/resolution/power/duty-cycle/gain.** This mirrors the real SAR
stripmap-vs-spotlight trade documented for operational systems like
[Capella Space's X-SAR constellation](https://www.eoportal.org/satellite-missions/capella-x-sar)
([Wayback](https://web.archive.org/web/2026/https://www.eoportal.org/satellite-missions/capella-x-sar))
and [TerraSAR-X](https://www.eoportal.org/satellite-missions/terrasar-x)
([Wayback](https://web.archive.org/web/2026/https://www.eoportal.org/satellite-missions/terrasar-x)):
stripmap/wide-area modes sustain continuous wide-swath imaging at coarser resolution, while
spotlight modes steer the beam to a fixed ground patch for higher resolution at the cost of swath
and revisit. [`engine/isr.py`](../../../spacesim/engine/isr.py)'s `BEAM_MODES` database
gives each payload type (`isr_eo`, `isr_sar`, `sda`) a small menu of modes (e.g. `wide_area` vs.
`spotlight`) each with a distinct `swath_km`, `resolution_m`, `power_factor`, `duty_cycle`, and
`gain_factor` — choosing a tighter beam buys confidence (`gain_factor`) at the cost of power draw
and a duty-cycle/thermal limit on how long it can be sustained per pass.

**Effective gain degrades off-nadir.** `effective_gain()` ([R102](R102-space-domain-awareness.md)/custody-consuming) scales the
requested gain down with `look_angle_deg` and the chosen beam's parameters — a sensor slewed far
off nadir produces a weaker observation than the same sensor looking straight down, independent of
range.

**A sensor's collection drains its host's battery, not an abstract budget.** When the actor has a
`bus_state`, `OrderSystem._h_observe` computes `isr.soc_drain(bp, duration_s)` and applies it
directly to `battery_soc` — sensor tasking is not a free action; it costs the same power budget
[R111](R111-power-and-thermal-operations.md) governs.

**Weather and missile-warning payloads have no `BEAM_MODES` entry today — a genuine coverage gap
(added for `BL-0052` grounding).** `engine/isr.py`'s `BEAM_MODES` database has exactly three
payload-type keys (`isr_eo`, `isr_sar`, `sda`); the `weather` and `mw` (missile-warning) payload
types `buscommands.py`'s `wx.*`/`mw.*` verbs already operate on (`wx.schedule_collection`,
`wx.request_sector`, `mw.add_stare_area`) have no beam-mode parameterization at all — `beam_params()`
silently falls back to generic EO stripmap numbers for any payload type it doesn't recognize. This
is the sharpest of the "typed per-payload-type sub-schema" gaps `BL-0052`'s design decision will
need to close, not merely document. Real-world grounding for each:

- **Weather imaging** — GOES-R series' Advanced Baseline Imager (ABI) images at **0.5-2 km spatial
  resolution** (band-dependent: 0.5 km visible, 1-2 km IR/water-vapor bands) with **temporal
  revisit as fast as 30-60 seconds** for a storm-tracking mesoscale sector, 5 minutes for
  full-CONUS, and 10-15 minutes for a full-disk scan
  ([NOAA GOES-R, "Instruments: Advanced Baseline Imager (ABI)"](https://www.goes-r.gov/spacesegment/abi.html)).
  A `weather` payload sub-schema's realistic fields are therefore closer to "resolution_km" (0.5-2
  range) and "revisit_s"/mode (mesoscale-fast vs. full-disk-slow) than a `swath_km` figure — the
  operationally interesting trade is temporal, not spatial, resolution.
- **Missile warning (OPIR)** — SBIRS-GEO carries two distinct sensor types: a continuously
  **scanning** sensor providing persistent global strategic warning (roughly 2× the revisit rate
  and 3× the sensitivity of the legacy DSP system it replaced), and a **staring/step-staring**
  sensor that dedicates itself to a smaller theater area for much faster revisit and higher
  sensitivity at the cost of global coverage
  ([Missile Defense Advocacy Alliance / CSIS Missile Threat, "Space-Based Infrared System
  (SBIRS)"](https://missilethreat.csis.org/defsys/sbirs/)). A `mw` payload sub-schema's realistic
  fields should therefore capture this same scan-vs-stare mode dichotomy (matching
  `mw.add_stare_area`'s existing stare-area concept in `buscommands.py`) rather than a single
  fixed sensitivity/range number — the mode choice itself (persistent-global vs. dedicated-theater)
  is the operationally meaningful parameter, mirroring the EO/SAR beam-mode trade this topic already
  documents for ISR.

### Sources

- *eoPortal, Capella Space X-Band Synthetic Aperture Radar* — [live](https://www.eoportal.org/satellite-missions/capella-x-sar)
  · [snapshot](https://web.archive.org/web/2026/https://www.eoportal.org/satellite-missions/capella-x-sar)
  · accessed 2026-06-27.
- *eoPortal, TerraSAR-X* — [live](https://www.eoportal.org/satellite-missions/terrasar-x)
  · [snapshot](https://web.archive.org/web/2026/https://www.eoportal.org/satellite-missions/terrasar-x)
  · accessed 2026-06-27.
- *NOAA GOES-R Program, "Instruments: Advanced Baseline Imager (ABI)"* — [live](https://www.goes-r.gov/spacesegment/abi.html)
  · [snapshot](https://web.archive.org/web/2026/https://www.goes-r.gov/spacesegment/abi.html)
  · accessed 2026-07-05.
- *Missile Defense Advocacy Alliance (citing CSIS Missile Threat), "Space-Based Infrared System (SBIRS)"* — [live](https://missilethreat.csis.org/defsys/sbirs/)
  · [snapshot](https://web.archive.org/web/2026/https://missilethreat.csis.org/defsys/sbirs/)
  · accessed 2026-07-05.

## 4. Operational Context

Real sensor operations are defined by exactly these trades: wider swath sees more but resolves
less, tighter beams cost more power and thermal margin, off-nadir geometry degrades quality, and a
sensor pass that fills the storage buffer needs a downlink before it can collect again — the
simulator's beam-mode database and storage/power coupling exist to make these trades real planning
decisions rather than background flavor text.

## 5. Implementation Guidance

- **A new sensor modality should add an entry to the relevant `BEAM_MODES` payload-type table**,
  not bypass `effective_gain`/`soc_drain` with bespoke math — this keeps power/duty-cycle/gain
  trades consistent across modalities.
- **Ground-sensor lighting logic (`needs_lighting` + twilight check) should be reused as-is** for
  any new optical ground modality; don't re-derive day/night gating per sensor type.
- **Always route a new sensor's collection drain through the host `BusState`**, per [R111](R111-power-and-thermal-operations.md)'s
  "every load through `charge_rate_per_s`-style abstraction" rule — a sensor that doesn't touch the
  bus budget is a dead/decoupled-field bug waiting to happen.
- **Footprint geometry for map rendering should reuse `isr.footprint_polygon`/`ground_heading_deg`**
  rather than a parallel geometry computation.
- **Before building typed `weather`/`mw` payload sub-schemas, add `BEAM_MODES` entries for both
  payload types** (per the gap above) — a typed schema over a field that silently falls back to
  generic EO numbers would let a vignette author configure a parameter the engine doesn't actually
  honor, which is worse than not offering the field at all.

## 6. Feature Mapping

FS-104 (SDA Tasking) is the direct consumer — any sensor-tasking UI should expose the beam-mode
trade explicitly (swath vs. resolution vs. power) rather than hiding it behind a single "task
sensor" button. The forthcoming Vignette Creator Feature Specification (`docs/pipeline/backlog.md`
`BL-0052`) depends on this topic's weather/missile-warning subsection above for its typed
per-payload-type parameter sub-schemas, and on the `BEAM_MODES` coverage gap it identifies.

## 7. Related Topics

[R102](R102-space-domain-awareness.md) (SDA — the chain stage sensors advance), [R104](R104-collection-management.md) (Collection Management — the contention model
sensors are tasked under), [R118](R118-space-surveillance-networks.md) (SSN — sensors aggregated into a per-cell network), [R111](R111-power-and-thermal-operations.md) (Power and
Thermal — the budget sensor collection draws from).
