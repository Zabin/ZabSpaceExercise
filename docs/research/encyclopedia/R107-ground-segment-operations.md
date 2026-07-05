# R107 — Ground Segment Operations

> **Document ID:** R107
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R101](R101-orbital-mechanics-for-operations.md), [R103](R103-satellite-command-and-control.md)
> **Referenced By:** [R110](R110-communications.md), [R118](R118-space-surveillance-networks.md), [R128](R128-ground-network-contact-scheduling.md), [R130](R130-downlink-operations-and-data-return.md), [R135](R135-ground-segment-operations-as-contested-terrain.md), FS-105
> **Produces:** implementation constraints for [`engine/entities.py`](../../../spacesim/engine/entities.py) (`GroundSite`), [`engine/access.py`](../../../spacesim/engine/access.py)
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R101](R101-orbital-mechanics-for-operations.md) (Orbital Mechanics — the geometry ground contact depends on), [R103](R103-satellite-command-and-control.md) (Satellite C2), [R110](R110-communications.md) (Communications)
> **Last Reviewed:** 2026-07-05
> **Primary Sources Consulted:** 2

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

**Ground-station siting methodology, for placing a new (non-catalog) site (added for `BL-0052`
grounding).** `docs/vignettes/GROUND-INFRASTRUCTURE.md` already curates ~45 real-world sites for
reuse, but names *what* they are, not *why* a real network operator would pick a location — the
rationale a White Cell facilitator needs to place a plausible new site via a lat/long entry surface.
Three siting factors dominate in practice:

1. **Elevation mask is the single biggest access-geometry lever a site choice controls.** A standard
   operational baseline is a **5° minimum elevation mask** in open terrain — matching this
   simulator's own `Asset.elevation_mask_deg` default (`entities.py`) exactly — with terrain/urban
   obstruction commonly pushing a real site to 10-20°+, which measurably shrinks usable pass
   duration and the contact's peak-elevation quality
   ([Minimum Elevation Angle Tradeoffs: Coverage vs. Link Margin](https://satellitegroundstation.com/resources/minimum-elevation-angle-tradeoffs-coverage-vs-link-margin/)).
   A vignette author placing a new ground site should treat a mask below ~5° as optimistic (flat,
   unobstructed terrain only) and a mask above ~20° as a realistic penalty for a mountainous/urban
   site, not an arbitrary number.
2. **Latitude drives which regimes a site can usefully serve.** A site's usable elevation-mask
   coverage of a given orbital regime degrades with latitude mismatch — full low-elevation coverage
   of high-inclination LEO passes is best from mid-to-high latitudes, while a GEO-arc-facing site
   (equatorial-facing antenna look angle) wants low-to-mid latitude siting so the GEO belt sits
   well above the local horizon rather than skimming it. A site near the poles serving a GEO
   relay would face the same low-elevation link-margin penalty item 1 describes, permanently.
3. **Network spacing trades station count against coverage/redundancy**, the same trade
   [R128](R128-ground-network-contact-scheduling.md) documents for contact scheduling: fewer,
   wider-spaced sites cost less to operate but produce gaps and contention; more, closer-spaced
   sites reduce per-site load and fill polar/high-latitude gaps a single low-to-mid-latitude site
   cannot reach — real multi-mission networks (DSN, AFSCN) resolve this with global spacing at
   roughly 120° longitude separation specifically to maintain near-continuous coverage, per
   [R128](R128-ground-network-contact-scheduling.md)'s own grounding.
4. **Coastal/geographic siting matters for downlink availability, not just clear sky.** Real
   ground-segment planning also weighs terrain masking (mountains, urban RF clutter) and
   local-interference environment — a coastal or otherwise open-horizon site is generally
   preferred over a valley/urban site for the same reason item 1's elevation-mask baseline assumes
   open terrain.

### Sources

- *Sæmundsson, "Astronomical Refraction," Sky and Telescope 72:70* (1986-07) — [live](https://www.scribd.com/document/240955446/1-s2-0-008366569390113X-main-pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.scribd.com/document/240955446/1-s2-0-008366569390113X-main-pdf)
  · accessed 2026-06-27.
- *airmass.org, Description of methods and algorithms (summarizing Meeus, Astronomical Algorithms ch. 16)* — [live](https://airmass.org/notes)
  · [snapshot](https://web.archive.org/web/2026/https://airmass.org/notes)
  · accessed 2026-06-27.
- *satellitegroundstation.com, "Minimum Elevation Angle Tradeoffs: Coverage vs Link Margin"* — [live](https://satellitegroundstation.com/resources/minimum-elevation-angle-tradeoffs-coverage-vs-link-margin/)
  · [snapshot](https://web.archive.org/web/2026/https://satellitegroundstation.com/resources/minimum-elevation-angle-tradeoffs-coverage-vs-link-margin/)
  · accessed 2026-07-05.

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
- **A vignette-creator lat/long entry surface for a new ground site should offer the curated
  `GROUND-INFRASTRUCTURE.md` list as the default/recommended path**, with free-entry coordinates as
  the fallback for a genuinely novel site — and if free-entry is used, surface this topic's siting
  factors (elevation-mask plausibility, latitude-vs-regime fit) as authoring guidance rather than
  accepting any lat/long pair silently.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer — any new station/outage feature must reflect
through the same uplink/downlink access windows the operator console already shows. The forthcoming
Vignette Creator Feature Specification (`docs/pipeline/backlog.md` `BL-0052`) depends on this
topic's ground-station siting subsection above for its lat/long entry surface.

## 7. Related Topics

[R101](R101-orbital-mechanics-for-operations.md) (the orbital geometry feeding `look_angles`), [R103](R103-satellite-command-and-control.md) (the C2 chain the ground segment delivers),
[R110](R110-communications.md) (Communications — the link-quality side of the same ground contact), [R118](R118-space-surveillance-networks.md) (SSN — ground-based
sensor sites use the same `GroundSite`/elevation-mask machinery), [R128](R128-ground-network-contact-scheduling.md) (Ground-Network Contact
Scheduling — the multi-mission contention layer a future fidelity increase would add above this
topic's per-station model).
