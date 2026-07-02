# R107 — Ground Segment Operations

> **Document ID:** R107
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R101](R101-orbital-mechanics-for-operations.md), [R103](R103-satellite-command-and-control.md)
> **Referenced By:** [R110](R110-communications.md), [R118](R118-space-surveillance-networks.md), [R128](R128-ground-network-contact-scheduling.md), [R130](R130-downlink-operations-and-data-return.md), [R135](R135-ground-segment-operations-as-contested-terrain.md), FS-105
> **Produces:** implementation constraints for [`engine/entities.py`](../../../spacesim/engine/entities.py) (`GroundSite`), [`engine/access.py`](../../../spacesim/engine/access.py)
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R101](R101-orbital-mechanics-for-operations.md) (Orbital Mechanics — the geometry ground contact depends on), [R103](R103-satellite-command-and-control.md) (Satellite C2), [R110](R110-communications.md) (Communications)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 1

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

The ground segment is the physical anchor for two of the six access channels (`command_uplink`,
`telemetry_downlink`) and the thing that makes "command window" a real constraint rather than a
balance dial. This topic gives an implementer the `GroundSite` model so new ground-segment features
(a new station type, an outage mechanic, a terrain-aware mask) compose correctly with `access.py`.

## 2. Scope

Covers: the `GroundSite` elevation-mask/refraction model and station-health gating of access
windows. Does **not** cover: the orbital geometry feeding `look_angles` ([R101](R101-orbital-mechanics-for-operations.md)), the C2 chain a
ground contact delivers ([R103](R103-satellite-command-and-control.md)), or link-quality/jamming on that contact ([R110](R110-communications.md)).

## 3. Concepts

**A ground site gates by elevation, not just line-of-sight.** `AccessProvider._ground_sat_predicate`
requires the satellite's elevation above the site's horizon to exceed `elevation_mask_deg` (or a
per-azimuth `mask_table` for terrain-aware horizons) — a satellite can be geometrically visible and
still below the usable contact elevation.

**Per-azimuth mask tables model real terrain.** A station ringed by mountains in one direction has
a higher effective mask in that azimuth band; `site_mask(az_deg)` looks up the matching `mask_table`
entry (with wrap-around band support) rather than assuming a uniform horizon — this is FUTURE-WORK
§10.C.12's terrain-aware horizon model, already wired into the predicate.

**A degraded ground station drops out of the access scene entirely.** `scene_from_world` excludes
any asset acting as a site whose `health == "degraded"` from `Scene.sites` — an outage (e.g. the
`gs_outage` inject template) doesn't lower a probability, it removes the station's command/downlink
path until the outage clears. This is the same "denied, not crashed" doctrine [R103](R103-satellite-command-and-control.md) describes for
command validation, applied to infrastructure.

**Atmospheric refraction is an optional, not default, correction.** `AccessConfig.atmospheric_refraction`
gates whether `_refracted_elevation` (the Bennett/Sæmundsson empirical refraction formula —
[Sæmundsson, "Astronomical Refraction," *Sky and Telescope* 72:70 (1986-07)](https://www.scribd.com/document/240955446/1-s2-0-008366569390113X-main-pdf),
as adjusted and reproduced in [Meeus, *Astronomical Algorithms*, 2nd ed., ch. 16](https://airmass.org/notes)
([Wayback](https://web.archive.org/web/2026/https://airmass.org/notes))) is applied — a ~0.5° lift at the
horizon that vanishes by ~20° elevation. Off by default; a vignette wanting higher ground-segment
fidelity can enable it without changing the predicate's structure.

### Sources

- *Sæmundsson, "Astronomical Refraction," Sky and Telescope 72:70* (1986-07) — [live](https://www.scribd.com/document/240955446/1-s2-0-008366569390113X-main-pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.scribd.com/document/240955446/1-s2-0-008366569390113X-main-pdf)
  · accessed 2026-06-27.
- *airmass.org, Description of methods and algorithms (summarizing Meeus, Astronomical Algorithms ch. 16)* — [live](https://airmass.org/notes)
  · [snapshot](https://web.archive.org/web/2026/https://airmass.org/notes)
  · accessed 2026-06-27.

## 4. Operational Context

Real ground segments are a hard operational constraint, not a convenience: a station's usable
contact window is bounded by both geometry (elevation mask, often terrain-driven) and
availability (maintenance, weather, host-nation agreements). Losing a station to an outage is a
common real-world anomaly category, and the simulator's `gs_outage` inject exists specifically to
let White Cell rehearse that.

## 5. Implementation Guidance

- **A new station type (e.g. a mobile or shipborne terminal) should still produce a `GroundSite`**
  consumed by the existing `_ground_sat_predicate` — don't build a parallel access predicate for a
  new station class.
- **An outage/degradation mechanic should set `health="degraded"`**, the existing exclusion
  condition in `scene_from_world`, rather than inventing a second "is this station up" flag that
  `AccessProvider` doesn't know about.
- **Per-azimuth fidelity (terrain masking) should extend `mask_table`**, not branch the predicate —
  the table format already supports wrap-around bands.
- **Don't add refraction-style corrections as always-on** — follow the `AccessConfig` pattern of an
  explicit, vignette-level fidelity toggle so existing baselines aren't silently changed.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer — any new station/outage feature must reflect
through the same uplink/downlink access windows the operator console already shows.

## 7. Related Topics

[R101](R101-orbital-mechanics-for-operations.md) (the orbital geometry feeding `look_angles`), [R103](R103-satellite-command-and-control.md) (the C2 chain the ground segment delivers),
[R110](R110-communications.md) (Communications — the link-quality side of the same ground contact), [R118](R118-space-surveillance-networks.md) (SSN — ground-based
sensor sites use the same `GroundSite`/elevation-mask machinery), [R128](R128-ground-network-contact-scheduling.md) (Ground-Network Contact
Scheduling — the multi-mission contention layer a future fidelity increase would add above this
topic's per-station model).
