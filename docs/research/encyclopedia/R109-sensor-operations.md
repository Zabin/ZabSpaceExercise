# R109 — Sensor Operations

> **Document ID:** R109
> **Version:** 1.3
> **Status:** ✅ Done
> **Dependencies:** [R101](R101-orbital-mechanics-for-operations.md)
> **Referenced By:** [R102](R102-space-domain-awareness.md), [R104](R104-collection-management.md), [R118](R118-space-surveillance-networks.md), [R119](R119-space-situational-data-fusion.md), [R129](R129-sigint-collection-and-geolocation-accuracy.md), [R134](R134-pnt-warfare-and-navigation-denial-operations.md), [R137](R137-bus-and-payload-parameter-catalog.md), [R127](R127-conjunction-assessment-and-collision-avoidance.md) (v1.1, its own RIC-display §3.x cross-references this topic's phase-angle work), FS-104
> **Produces:** implementation constraints for [`engine/entities.py`](../../../spacesim/engine/entities.py) (`Sensor`), [`engine/isr.py`](../../../spacesim/engine/isr.py), [`engine/sun.py`](../../../spacesim/engine/sun.py) (`sun_unit_eci`, reused by §3.11's phase-angle computation); (v1.2) new-sensor-modality grounding for `BL-0073`/B7 (fence/dish radar, optical exclusion angles, space-based min-range/altitude band, laser ranging, passive-RF multilateration); (v1.3) Sun-target-observer illumination phase angle ("CATS angle") grounding for `BL-0111`/`BL-0112`/`BL-0122`
> **Feature Mapping:** FS-104 (SDA Tasking); (v1.3) `FEAT-8200`/`FEAT-1600` ([`docs/feature-planning/03-feature-catalog.md`](../../feature-planning/03-feature-catalog.md))
> **Related Topics:** [R102](R102-space-domain-awareness.md) (Space Domain Awareness), [R104](R104-collection-management.md) (Collection Management), [R118](R118-space-surveillance-networks.md) (Space Surveillance Networks), [R129](R129-sigint-collection-and-geolocation-accuracy.md) (SIGINT Collection and Geolocation Accuracy — the TDOA/multilateration model a passive-RF SDA sensor reuses, v1.2), [R127](R127-conjunction-assessment-and-collision-avoidance.md) (Conjunction Assessment — the RIC/RTN-frame relative-motion *display* convention §3.11's phase angle is shown alongside in `FEAT-8200`'s RIC view, v1.3)
> **Last Reviewed:** 2026-10-03
> **Primary Sources Consulted:** 13 (3 for the v1.0/v1.1 content; 6 for v1.2's sensor-variant
> grounding; 4 new for v1.3's CATS/phase-angle grounding)

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

> *v1.2 changelog (2026-09-27): grounds `BL-0073`/B7 — five new sensor-modality subsections below
> (§3.6-§3.10): fence/dish radar variants, optical solar/lunar exclusion angles, space-based
> min-range/altitude-band trade, cue-dependent laser ranging, and passive-RF multilateration
> (≥3 receivers). New §5 bullets tie each to a concrete `engine/entities.py::Sensor` or
> `engine/isr.py` extension point. No existing content changed in substance.*

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

### 3.6 Fence/dish radar variants (`BL-0073`/B7)

**A "fence" radar and a tracking dish are the same access-predicate shape at different scales, not
different physics.** The U.S. Space Fence, operational on Kwajalein Atoll since March 2020, is a
continuous-coverage S-band (2-4 GHz) phased-array radar using element-level digital beam forming
across **86,000 receive elements** (a 7,000 sq ft receiver, 2,000 sq ft transmitter) to sweep a
fixed detection fence and catalog objects as they cross it, rather than cueing to a single target
like a dish
([U.S. Space Force / Lockheed Martin coverage via Smithsonian Air & Space, "How Things Work: Space
Fence"](https://www.smithsonianmag.com/air-space-magazine/how-things-work-space-fence-180957776/))
([Wayback](https://web.archive.org/web/2026/https://www.smithsonianmag.com/air-space-magazine/how-things-work-space-fence-180957776/)).
Its higher wave frequency and geographic separation over legacy systems let it detect much smaller
microsatellites and debris. For this simulator, a "fence" variant is the same `ground`-kind
`Sensor` `AccessProvider._observation_predicate` already resolves — the distinguishing parameter is
a **wide, low-gain, continuous field of regard** (many objects transiting a fixed volume) versus a
**narrow, high-gain, steerable beam** (one cued target at a time), which is exactly the
swath/resolution/power trade §3's beam-mode discussion already generalizes; a fence is not a new
access channel, it is a beam-mode extreme.

### 3.7 Optical sensor solar/lunar exclusion angles (`BL-0073`/B7)

**A ground-based optical sensor's real constraint is an exclusion-angle cone around the Sun (and
often the Moon), not a simple day/night flag.** GEODSS — three sites (Diego Garcia, Maui HI,
Socorro NM), each with two 40" primary telescopes (2° FOV) plus a 15" auxiliary (6° FOV) — observes
deep-space (GEO-belt) objects only at night and only outside a solar-phase-angle exclusion cone
commonly cited around **90°** for ground-based deep-space optical sensors, with site-dependent
night-observation windows of roughly 10-14 hours per 24-hour day
([U.S. Space Force, "Ground-Based Electro-Optical Deep Space Surveillance" fact
sheet](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/2197760/ground-based-electro-optical-deep-space-surveillance/))
([Wayback](https://web.archive.org/web/2026/https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/2197760/ground-based-electro-optical-deep-space-surveillance/)).
This is the same constraint `needs_lighting`/`twilight_deg` already encodes (target sunlit + sensor
site dark), generalized: an exclusion-angle sensor additionally rejects a geometrically-valid,
correctly-lit access window if the Sun (or Moon, for a stricter site/instrument) falls inside a
configurable angular radius of the sensor's boresight — a single scalar (`exclusion_angle_deg`)
layered on top of the existing lighting predicate, not a new access channel.

### 3.8 Space-based sensor min-range/altitude-band trade (`BL-0073`/B7)

**A space-based optical SDA sensor is optimized for one altitude regime, not all of them at once.**
Peer-reviewed dual-altitude-band coverage analysis for spaceborne optical sensors with a
field-of-view constraint concludes the most effective concepts observe LEO objects from a
sun-synchronous LEO host and GEO objects from a GEO-resident host — attempting single-sensor
coverage across both bands simultaneously trades away performance in both
([*Journal of Spacecraft and Rockets*, "Dual-Altitude Band Coverage for Spaceborne Optical Sensor
with Field-of-View Constraint"](https://arc.aiaa.org/doi/abs/10.2514/1.A35630))
([Wayback](https://web.archive.org/web/2026/https://arc.aiaa.org/doi/abs/10.2514/1.A35630)). This
is consistent with the fielded systems: SBSS uses a two-axis gimballed telescope specialized for the
geostationary belt, and GSSAP satellites operate in near-geosynchronous orbit specifically to
monitor that same regime up close
([Air & Space Forces Magazine, "GSSAP"](https://www.airandspaceforces.com/weapons-platforms/gssap/))
([Wayback](https://web.archive.org/web/2026/https://www.airandspaceforces.com/weapons-platforms/gssap/)).
For this simulator, a space-based sensor's `kind="space_based"` access predicate should gain a
**minimum-range floor** (an RPO-adjacent sensor that saturates or cannot resolve a target closer
than some threshold — the too-close-to-focus case a fixed-focus optical payload genuinely has) and
an **altitude-band affinity** (a declared regime the sensor is tuned for, degrading `effective_gain`
outside it) rather than treating all space-based sensors as uniformly effective at any range/regime.

### 3.9 Cue-dependent laser ranging (`BL-0073`/B7)

**Laser ranging gives millimeter-level range precision independent of altitude, but only against a
cued, cooperative (retroreflector-equipped) target.** The International Laser Ranging Service
coordinates a global network of ground stations firing short-pulse lasers at passive cube-corner
retroreflector arrays on 150+ cooperative satellites (out to ~36,000 km, i.e. GEO), timing the
two-way flight to derive range with **mm-to-cm-level precision that does not degrade with distance
the way radar cross-section-limited detection does**
([NASA/ILRS, "International Laser Ranging Service"](https://ilrs.gsfc.nasa.gov/))
([Wayback](https://web.archive.org/web/2026/https://ilrs.gsfc.nasa.gov/)). The operationally
important consequence for this simulator: a laser-ranging sensor is not a general-search sensor — it
requires an existing cue (a prior track with a good-enough angular solution, or a designated
cooperative target) before it can lock and range, unlike a radar/EO sensor that can independently
detect an uncued object in its field of regard. This maps to a **`requires_cue: bool`** flag on the
`Sensor` model: when true, `OrderSystem._h_observe` must reject (or `dry_run` pre-disable) a laser
task issued against a target with no existing `Track`, rather than treating it as a normal
detect-from-scratch tasking.

### 3.10 Passive-RF multilateration (≥3 receivers) (`BL-0073`/B7)

**Passive-RF geolocation needs a network, not a single sensor — and it needs the target to be
emitting.** Time-Difference-of-Arrival (TDOA) multilateration requires **at least three spatially
separated receivers for a 2D fix, and at least four for a 3D fix (adding altitude)**; each receiver
pair's arrival-time difference defines a hyperbolic curve, and the intersection of those curves
(ideally from a non-symmetrical receiver geometry so no two curves coincide) is the estimated
transmitter location
([CRFS, "Guide to RF Geolocation"](https://www.crfs.com/guide-to-rf-geolocation))
([Wayback](https://web.archive.org/web/2026/https://www.crfs.com/guide-to-rf-geolocation)). Unlike
every other sensor kind this topic covers, a passive-RF sensor has **no independent access
predicate at all** — it can only produce a fix when (a) the target is actively transmitting (an
emission-dependent, not illumination-dependent, precondition) and (b) at least 3 (2D) or 4 (3D)
member receivers of a declared network simultaneously have access to that emission. This is the
same "aggregate multiple sensors into a network" pattern [R118](R118-space-surveillance-networks.md)'s
SSN already models for cross-sensor cataloging, reused here for a single fix rather than a catalog
build-up — not a new aggregation mechanism.

### 3.11 Sun-target-observer illumination phase angle / "CATS angle" (`BL-0111`/`BL-0112`/`BL-0122`)

**A passive EO sensor's usable observation geometry is governed by a three-body phase angle, not
only by the sensor's own boresight-vs-Sun exclusion angle (§3.7).** The relevant quantity —
variously called the illumination phase angle, the solar phase angle, or, in commercial mission-
planning tooling, the Camera-Target-Sun (CATS) angle / "LOS Sun Illumination Angle" — is measured
**at the target's location**, between the target→Sun vector and the target→observer (camera)
vector: 0° means the target's face toward the observer is fully sunlit (directly analogous to a
full moon as seen from Earth), 180° means the target is backlit/silhouetted from the observer's
viewpoint (a new moon) ([AGI, "Constraints - Sun"](https://help.agi.com/stk/12.2.0/content/stk/constraints-02.htm))
([Wayback](https://web.archive.org/web/2026/https://help.agi.com/stk/12.2.0/content/stk/constraints-02.htm));
([AGI, "New Feature in STK 11.1.1 - New Lighting Constraint"](https://www.agi.com/products/stk-systems-bundle/stk-professional/new-feature-in-stk-11-1-1-new-lighting-constraint))
([Wayback](https://web.archive.org/web/2026/https://www.agi.com/products/stk-systems-bundle/stk-professional/new-feature-in-stk-11-1-1-new-lighting-constraint)).
This is a genuinely different quantity from both `is_sunlit()`/`eclipse_fraction()` (`engine/sun.py`,
which model whether the target is illuminated by the Sun *in isolation*, a two-body question) and
§3.7's exclusion angle (the Sun's angular proximity to the *sensor's own boresight*, a sensor-centric
constraint) — the CATS/phase angle is the three-body relationship between all of Sun, target, and
observer, and it governs *how well-illuminated the target appears from the observer's specific
vantage point*, independent of whether the sensor itself is pointed anywhere near the Sun.

**Real SDA/photometric practice treats phase angle as operationally load-bearing, not cosmetic.**
Lower phase angle means stronger returned signal and more reliable detection/characterization: a
2022 AMOS sensor-performance comparison for space- and ground-based SDA architectures models
"difficult solar-phase-angle geometries" directly as a coverage-gap risk a sensor architecture must
be sized against, citing roughly a 90° usable-phase-angle constraint for ground-based optical SDA
sensors and a looser (order ~150°) constraint for space-based ones — ground-based sensors face a
tighter usable range because atmospheric/twilight effects compound with the phase-angle effect
itself, while a space-based sensor's main limit is simply how backlit the target becomes
([Bloom, Wysack, Griesbach & Lawitzke, "Space and Ground-Based SDA Sensor Performance
Comparisons," AMOS Conference 2022](https://amostech.com/TechnicalPapers/2022/Poster/Bloom.pdf))
([Wayback](https://web.archive.org/web/2026/https://amostech.com/TechnicalPapers/2022/Poster/Bloom.pdf)).
Independently, long-standing SDA photometric-characterization practice treats 0° phase angle as the
*reference* condition any off-angle photometric size/magnitude estimate must be corrected back
toward — debris-characterization campaigns reduce radar-cross-section/optical-signature
measurements "using the diffuse Lambertian spherical phase function correction to 0° phase angle"
before deriving a physical-size estimate, precisely because detectability and signature fidelity
both degrade smoothly as phase angle departs from 0°
([Africano et al., "Understanding Photometric Phase Angle Corrections," 4th European Conference on
Space Debris, 2005](https://conference.sdo.esoc.esa.int/proceedings/sdc4/paper/108/SDC4-paper108.pdf))
([Wayback](https://web.archive.org/web/2026/https://conference.sdo.esoc.esa.int/proceedings/sdc4/paper/108/SDC4-paper108.pdf)).
**Single-source flag (ballpark figures only):** the ground≈90°/space≈150° usable-range figures above
rest on one AMOS conference source and are reported here as an order-of-magnitude starting anchor
for a configurable default, not a precise universal constant — the same flagging discipline §3.7
already applies to its own 90° exclusion-angle figure, and for the same reason (a single technical-
conference source, not a cross-corroborated standard). This closes `docs/pipeline/backlog.md`
`BL-0151`'s open design ambiguity **partially**: a concrete, citable starting default now exists
(0°-90° usable for a ground-based passive EO sensor, 0°-150° for a space-based one, with
effectiveness degrading smoothly — not as a hard cliff — as the angle approaches the limit), but
`06-feature-specification` should treat this as a configurable, overridable default rather than a
hard-coded universal threshold, consistent with §3.7's own `exclusion_angle_deg` precedent.

### Sources (§3.11, CATS/illumination phase angle)

- *AGI, "Constraints - Sun" (STK 12.2.0 help)* — [live](https://help.agi.com/stk/12.2.0/content/stk/constraints-02.htm)
  · [snapshot](https://web.archive.org/web/2026/https://help.agi.com/stk/12.2.0/content/stk/constraints-02.htm)
  · accessed 2026-10-03.
- *AGI, "New Feature in STK 11.1.1 - New Lighting Constraint"* —
  [live](https://www.agi.com/products/stk-systems-bundle/stk-professional/new-feature-in-stk-11-1-1-new-lighting-constraint)
  · [snapshot](https://web.archive.org/web/2026/https://www.agi.com/products/stk-systems-bundle/stk-professional/new-feature-in-stk-11-1-1-new-lighting-constraint)
  · accessed 2026-10-03.
- *Bloom, Wysack, Griesbach & Lawitzke, "Space and Ground-Based SDA Sensor Performance
  Comparisons," AMOS Conference 2022* — [live](https://amostech.com/TechnicalPapers/2022/Poster/Bloom.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://amostech.com/TechnicalPapers/2022/Poster/Bloom.pdf)
  · accessed 2026-10-03.
- *Africano, Kervin, Hall, Sydney, Ross, Payne, Gregory, Jorgensen, Jarvis, Parr-Thumm, Stansbery &
  Barker, "Understanding Photometric Phase Angle Corrections," 4th European Conference on Space
  Debris, 2005* — [live](https://conference.sdo.esoc.esa.int/proceedings/sdc4/paper/108/SDC4-paper108.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://conference.sdo.esoc.esa.int/proceedings/sdc4/paper/108/SDC4-paper108.pdf)
  · accessed 2026-10-03.

**Single-source flag:** the ground≈90°/space≈150° usable-phase-angle figures rest on the Bloom et
al. 2022 AMOS source alone — treat as an order-of-magnitude anchor for a configurable default, not
a precise universal constant, pending a second corroborating source (same treatment §3.7 already
gives its own 90° exclusion-angle figure).

### Sources (§3.6-§3.10, new sensor modalities)

- *U.S. Space Force / Lockheed Martin (via Smithsonian Air & Space Magazine), "How Things Work:
  Space Fence"* — [live](https://www.smithsonianmag.com/air-space-magazine/how-things-work-space-fence-180957776/)
  · [snapshot](https://web.archive.org/web/2026/https://www.smithsonianmag.com/air-space-magazine/how-things-work-space-fence-180957776/)
  · accessed 2026-09-27.
- *U.S. Space Force, "Ground-Based Electro-Optical Deep Space Surveillance" fact sheet* —
  [live](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/2197760/ground-based-electro-optical-deep-space-surveillance/)
  · [snapshot](https://web.archive.org/web/2026/https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/2197760/ground-based-electro-optical-deep-space-surveillance/)
  · accessed 2026-09-27.
- *Journal of Spacecraft and Rockets, "Dual-Altitude Band Coverage for Spaceborne Optical Sensor
  with Field-of-View Constraint"* — [live](https://arc.aiaa.org/doi/abs/10.2514/1.A35630)
  · [snapshot](https://web.archive.org/web/2026/https://arc.aiaa.org/doi/abs/10.2514/1.A35630)
  · accessed 2026-09-27.
- *Air & Space Forces Magazine, "GSSAP"* — [live](https://www.airandspaceforces.com/weapons-platforms/gssap/)
  · [snapshot](https://web.archive.org/web/2026/https://www.airandspaceforces.com/weapons-platforms/gssap/)
  · accessed 2026-09-27.
- *NASA / International Laser Ranging Service, "International Laser Ranging Service"* —
  [live](https://ilrs.gsfc.nasa.gov/) · [snapshot](https://web.archive.org/web/2026/https://ilrs.gsfc.nasa.gov/)
  · accessed 2026-09-27.
- *CRFS, "Guide to RF Geolocation"* — [live](https://www.crfs.com/guide-to-rf-geolocation)
  · [snapshot](https://web.archive.org/web/2026/https://www.crfs.com/guide-to-rf-geolocation)
  · accessed 2026-09-27.

**Single-source flag:** the 90° solar-phase exclusion figure in §3.7 is cited from one source (the
Space Force fact sheet describes site/instrument operational practice but does not itself tabulate
a precise degree value per site) — treat it as an order-of-magnitude anchor for a configurable
`exclusion_angle_deg` default, not a precise universal constant, pending a second corroborating
source.

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
- **A fence/dish radar variant (§3.6) is a beam-mode parameterization, not a new `Sensor.kind`** —
  add it as a wide-field-of-regard, low-gain `BEAM_MODES` entry alongside existing modes; do not
  branch `AccessProvider._observation_predicate` on "fence vs. dish."
- **An exclusion-angle optical sensor (§3.7) should add `exclusion_angle_deg` alongside the
  existing `twilight_deg` field on the ground-sensor branch of `Sensor`**, checked in the same
  `_observation_predicate` pass that already computes Sun/target geometry — do not build a
  separate solar-exclusion subsystem.
- **A space-based sensor's min-range/altitude-band trade (§3.8) belongs in `effective_gain()`**:
  add a `min_range_km` floor (return zero/invalid gain below it) and an `altitude_band_affinity`
  parameter that degrades `effective_gain` outside the declared regime, mirroring how off-nadir
  `look_angle_deg` already degrades gain.
- **A cue-dependent sensor (§3.9, e.g. laser ranging) needs a `requires_cue: bool` field on
  `Sensor`**, checked by `OrderSystem._h_observe`/`dry_run()` to reject or pre-disable a tasking
  against a target with no existing `Track` — do not silently let it behave like a general-search
  sensor.
- **Passive-RF multilateration (§3.10) is an SSN-style network aggregation, not a per-sensor
  access predicate** — reuse [R118](R118-space-surveillance-networks.md)'s network-of-sensors
  pattern, gating a fix on ≥3 (2D) or ≥4 (3D) member receivers simultaneously having access to an
  *emitting* (not merely illuminated) target, rather than adding a bespoke multi-sensor code path.
- **The CATS/illumination phase angle (§3.11) is a pure geometry computation over existing
  primitives** — `sun_unit_eci()` (`engine/sun.py`) already gives the Sun direction; the target→
  observer vector is already available wherever an access-window or RIC-view computation runs. The
  phase angle itself is `arccos` of the dot product between the (negated) target→Sun unit vector
  and the target→observer unit vector — no new state, no new propagation. For `FR-8220`'s display
  overlay, compute and expose this value read-only, the same pure/non-mutating pattern
  `engine/scene.py`/`engine/telemetry.py` already use for read-time derived quantities. For
  `FR-1670`'s access-gating use, layer a configurable usable-range check (default 0°-90° ground /
  0°-150° space, per the single-source figures above) on top of the existing lighting (`FR-1220`)
  and, where declared, exclusion-angle (§3.7/`FR-1620`) predicates in `AccessProvider._observation_predicate`
  — do not invent a second geometry computation for the two use cases; one function, two callers.

## 6. Feature Mapping

FS-104 (SDA Tasking) is the direct consumer — any sensor-tasking UI should expose the beam-mode
trade explicitly (swath vs. resolution vs. power) rather than hiding it behind a single "task
sensor" button. The forthcoming Vignette Creator Feature Specification (`docs/pipeline/backlog.md`
`BL-0052`) depends on this topic's weather/missile-warning subsection above for its typed
per-payload-type parameter sub-schemas, and on the `BEAM_MODES` coverage gap it identifies.
The five new-sensor-modality subsections (§3.6-§3.10) ground `docs/pipeline/backlog.md` `BL-0073`
(B7) for the forthcoming `04-requirements-engineering` pass deriving its baselined FRs. §3.11 (v1.3,
2026-10-03) grounds `BL-0111`/`BL-0122`'s baselined `FR-8220` (the RIC-view CATS display overlay,
`FEAT-8200`, [`docs/feature-planning/03-feature-catalog.md`](../../feature-planning/03-feature-catalog.md))
and `FR-1670` (the CATS access-gating refinement, `FEAT-1600`) — closing the `BL-0112` research
gap both leaves' `06-feature-specification` pass is blocked on, and partially closing `BL-0151`'s
open design ambiguity with a concrete, single-source-flagged default range (see §3.11).

## 7. Related Topics

[R102](R102-space-domain-awareness.md) (SDA — the chain stage sensors advance), [R104](R104-collection-management.md) (Collection Management — the contention model
sensors are tasked under), [R118](R118-space-surveillance-networks.md) (SSN — sensors aggregated into a per-cell network, and the pattern §3.10's passive-RF
multilateration reuses), [R111](R111-power-and-thermal-operations.md) (Power and
Thermal — the budget sensor collection draws from), [R129](R129-sigint-collection-and-geolocation-accuracy.md) (SIGINT Collection and Geolocation Accuracy — the TDOA/multilateration model §3.10 reuses).
