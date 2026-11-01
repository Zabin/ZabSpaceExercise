# R139 — Passive-RF Emitter Characterization and Geolocation from Space

> **Document ID:** R139
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R129](R129-sigint-collection-and-geolocation-accuracy.md), [R109](R109-sensor-operations.md), [R120](R120-access-window-and-geometry-planning.md)
> **Referenced By:** `docs/feature-planning/06a-release-2-d3-d4-research.md` (Release 2.0 decision D4)
> **Produces:** implementation constraints for [`engine/ssn.py`](../../../spacesim/engine/ssn.py) (`passive_rf_fix`, `_is_emitting`), [`engine/sigint.py`](../../../spacesim/engine/sigint.py) (`geolocation_error_km`), [`engine/buscommands.py`](../../../spacesim/engine/buscommands.py) (`sigint.task_collection`), [`engine/orders.py`](../../../spacesim/engine/orders.py) (`observe` with `intent="characterize"`, `_h_observe`), [`engine/access.py`](../../../spacesim/engine/access.py) (`SENSOR_OBSERVATION` validity and `_ground_sat_predicate`), [`engine/custody.py`](../../../spacesim/engine/custody.py) (`Track.characterized`)
> **Feature Mapping:** Release 2.0 candidate F-04 / B-19 / B-20 (SIGINT characterization path, `mt-sigint-geolocate` objectives); FR-1650; FS-104 (SDA Tasking)
> **Related Topics:** [R129](R129-sigint-collection-and-geolocation-accuracy.md) (the band/mode/dwell accuracy model this topic adds technique and geometry to), [R109](R109-sensor-operations.md) §3.10 (the ≥3-receiver passive-RF rule FR-1650 baselines), [R105](R105-custody-theory.md) (custody "characterized" vs. emitter "characterized"), [R118](R118-space-surveillance-networks.md) (the network shape `passive_rf_fix` reuses), [R120](R120-access-window-and-geometry-planning.md) (access geometry and footprints)
> **Last Reviewed:** 2026-11-01
> **Primary Sources Consulted:** 3
> **Verification note:** authored 2026-11-01 in an environment where direct page fetch was blocked for every external host; each claim was checked against search-index abstracts of the cited page, not its full text. The snapshot links follow the corpus's `web/2026/` convention and were not individually confirmed. The footprint geometry in §3.4 is computed here from the vignette's own orbit elements (standard spherical-Earth horizon geometry, [R101](R101-orbital-mechanics-for-operations.md) / [`04-orbital-mechanics-primer.md`](../04-orbital-mechanics-primer.md)), so it needs no external source. Queued for the §5.3 verification pass.

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

[R129](R129-sigint-collection-and-geolocation-accuracy.md) grounds *how accurate* a SIGINT fix is
(√dwell, √N collectors, band). [R109](R109-sensor-operations.md) §3.10 grounds the rule that a
passive-RF fix needs ≥3 simultaneous receivers and an emitting target. Neither says what
**"characterized"** means for an emitter, which **techniques** (TDOA, FDOA, AOA, single-satellite
Doppler) produce a fix from orbit, or what **geometry** must hold at collection time. Release 2.0
decision D4 has to choose how a SIGINT order makes `mt-sigint-geolocate`'s `characterize_emitter`
reachable, and that choice depends on these facts. This topic supplies them, and checks the shipped
functions and vignette against them.

## 2. Scope

Covers: what an emitter characterization contains; space-based geolocation techniques and their
minimum receiver counts; what accuracy depends on (bandwidth, integration time, SNR, geometry) and how
it is reported (error ellipse, CEP); the common-view and emission preconditions; and how the shipped
`passive_rf_fix` / `geolocation_error_km` / `sigint.task_collection` fit those facts. Does **not**
cover: the band/mode table itself ([R129](R129-sigint-collection-and-geolocation-accuracy.md)), sensor
contention ([R104](R104-collection-management.md)), or orbital custody of *satellites*
([R105](R105-custody-theory.md)).

## 3. Concepts

### 3.1 "Characterized" means parameters, identity and a located fix with stated error

ELINT practice records each intercepted pulse as a **pulse descriptor word**: carrier frequency, pulse
amplitude, pulse width, time of arrival and angle of arrival, plus intra-pulse modulation where it is
measured. The pulse repetition interval (fixed, staggered or jittered) is derived from the TOA
sequence. The derived parameter set is then compared with an emitter library to **identify the
emitter type**
([US Patent 7,242,346, *Pulse descriptor word generator*](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7242346)
([Wayback](https://web.archive.org/web/2026/https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7242346));
[Microwave Journal, *Two cards to convert a microwave receiver into an ELINT system*](https://microwavejournal.com/articles/1662-two-cards-to-convert-a-microwave-receiver-into-a-state-of-the-art-elint-system)
([Wayback](https://web.archive.org/web/2026/https://microwavejournal.com/articles/1662-two-cards-to-convert-a-microwave-receiver-into-a-state-of-the-art-elint-system))).
The NSA's TechELINT category ("signal structure, emission characteristics, modes of operation, emitter
functions") quoted in [R129](R129-sigint-collection-and-geolocation-accuracy.md) §3 describes the same
product. A geolocation is reported as an **uncertainty region**, not a point. Its size depends on
signal bandwidth, collection duration, terrain and orbital geometry
([Hubble Network, *How HawkEye 360 finds RF signals from space*](https://hubble.com/community/guides/how-hawkeye-360-finds-rf-signals-from-space/)
([Wayback](https://web.archive.org/web/2026/https://hubble.com/community/guides/how-hawkeye-360-finds-rf-signals-from-space/))).
*Tier C explainer; the PDW parameter list is corroborated by the patent and trade sources above.*

So an emitter is **characterized** when the collecting cell holds all four of: (1) **detection**:
the emitter was transmitting and was intercepted; (2) **parameters**: band/frequency and
modulation/mode measured; (3) **location**: a fix with a stated error (1σ ellipse or CEP) at or below
the accuracy the task needs; (4) **time**: when it was characterized, because emitters move and go
silent. This is not the same as [R105](R105-custody-theory.md)'s custody "characterized" (an orbital
object's identity and orbit known well enough for the weapons-quality gate), even though both end up as
`Track.characterized`.

### 3.2 Techniques and minimum receivers

- **TDOA.** Each receiver pair's arrival-time difference defines a hyperboloid. Generic patents on
  satellite emitter geolocation intersect the hyperboloids with the Earth's surface, so an emitter
  **on the ground** at known altitude is fixed by three receivers (two independent TDOAs plus the Earth
  constraint)
  ([US Patent 7,667,640, *Determining a geolocation solution of an emitter on earth using satellite signals*](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7667640)
  ([Wayback](https://web.archive.org/web/2026/https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7667640))).
  This matches FR-1650's "≥3 for 2D, ≥4 for 3D".
- **FDOA.** Each receiver sees a different Doppler shift of the same carrier, and the differences
  define further surfaces. Fast-moving LEO receivers make FDOA strong. Joint TDOA/FDOA is more accurate
  than either alone
  ([KICS, *Emitter geolocation based on TDOA/FDOA measurements and its analysis*](https://journal.kics.or.kr/digital-library/34922)
  ([Wayback](https://web.archive.org/web/2026/https://journal.kics.or.kr/digital-library/34922))).
  Commercial practice flies **clusters of three** small satellites that record the same emission. The
  emitter's coordinates come from TDOA and FDOA, and HawkEye 360's Cluster 3 satellites fly about
  300 km apart
  ([Janes, *HawkEye 360 expands satellite-based RF data collection*](https://www.janes.com/defence-intelligence-insights/defence-news/hawkeye-360-expands-satellite-based-rf-data-collection)
  ([Wayback](https://web.archive.org/web/2026/https://www.janes.com/defence-intelligence-insights/defence-news/hawkeye-360-expands-satellite-based-rf-data-collection))).
  This continues the three-satellite PARCAE pattern of [R129](R129-sigint-collection-and-geolocation-accuracy.md).
- **Single-satellite Doppler over a pass.** One moving receiver can locate a stationary carrier from the
  Doppler curve across a pass. Cospas-Sarsat LEOSAR does this operationally for 406 MHz beacons. It
  needs at least three bursts, each pass gives **two** candidate positions (the "A/B" mirror ambiguity
  about the ground track), accuracy is typically a few km (ESA cites ≈4 km), and the system requirement
  is ≤20 km
  ([ESA, *MetOp — Search and Rescue*](https://www.esa.int/Applications/Observing_the_Earth/Meteorological_missions/MetOp/Overview7)
  ([Wayback](https://web.archive.org/web/2026/https://www.esa.int/Applications/Observing_the_Earth/Meteorological_missions/MetOp/Overview7));
  [NOAA SARSAT, *MEOSAR*](https://www.sarsat.noaa.gov/meosar.html)
  ([Wayback](https://web.archive.org/web/2026/https://www.sarsat.noaa.gov/meosar.html))).
  Without a trackable carrier, a single satellite can only use coarse signal-strength methods
  ([Clements et al., UT Austin Radionavigation Lab, *direct geolocation*](https://radionavlab.ae.utexas.edu/wp-content/uploads/2023/05/clements-direct-geolocation.pdf)
  ([Wayback](https://web.archive.org/web/2026/https://radionavlab.ae.utexas.edu/wp-content/uploads/2023/05/clements-direct-geolocation.pdf))).
  A second pass from a different geometry resolves the ambiguity. This is the physical meaning of a
  "multi-pass" geolocation.
- **AOA / interferometry.** A single platform measures a bearing with an antenna array. Sparse
  multi-satellite arrays give precise AOA, but grating-lobe ambiguity needs TDOA/FDOA to resolve it
  ([UniBw München, *hybrid geolocation approach*](https://athene-forschung.rz.unibw-muenchen.de/147917)
  ([Wayback](https://web.archive.org/web/2026/https://athene-forschung.rz.unibw-muenchen.de/147917))).
  *Single source (academic).*

### 3.3 Accuracy: bandwidth, integration time, SNR, geometry

Stein's ambiguity-function bounds (*IEEE Trans. ASSP*, June 1981), as restated in later patents and
course notes, give σ_TDOA ≈ 1/(β·√(B·T·SNR_eff)) and σ_FDOA ≈ 1/(T_rms·√(B·T·SNR_eff)). Here β is RMS
bandwidth, T is integration time and SNR_eff is the combined two-receiver SNR. Timing accuracy
therefore improves with **bandwidth**, and frequency accuracy with **integration time**
([Fowler, Binghamton EECE 522 notes, *ML for TDOA/FDOA*](https://ws2.binghamton.edu/fowler/fowler%20personal%20page/EE522_files/EECE%20522%20Notes_15%20ML%20for%20TDOA-FDOA_revised.pdf)
([Wayback](https://web.archive.org/web/2026/https://ws2.binghamton.edu/fowler/fowler%20personal%20page/EE522_files/EECE%20522%20Notes_15%20ML%20for%20TDOA-FDOA_revised.pdf))).
*Secondary restatement; the constants were not checked against Stein's text.* The measurement
covariance is mapped through the geometry Jacobian, giving CRLB = (HᵀC⁻¹H)⁻¹. That covariance is drawn
as an **error ellipse**, and CEP ≈ 0.75·√(σ_x²+σ_y²) to within about 10%
([US Patent 7,663,547, *weighted least-squares emitter geolocation*](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7663547)
([Wayback](https://web.archive.org/web/2026/https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7663547))).
In a 2026 TU Delft thesis, a tight three-satellite LEO formation geolocating GNSS jammers achieved
sub-kilometre mean errors (≈140–520 m depending on method and scenario)
([TU Delft repository, *Triple-satellite geolocation from LEO in a multi-emitter GNSS interference environment*](https://repository.tudelft.nl/record/uuid:9295cd30-63bd-4b62-9bd3-cec8df7b2edb)
([Wayback](https://web.archive.org/web/2026/https://repository.tudelft.nl/record/uuid:9295cd30-63bd-4b62-9bd3-cec8df7b2edb))).
*Single source (academic thesis).* `geolocation_error_km()`'s 1.5 km single-satellite, L-band, 180 s
reference falls between that formation result and Cospas-Sarsat's single-satellite few-km figure, so
it is a plausible moderate-fidelity anchor. Its √dwell term stands in for the T dependence above, and
its 1/√N term for the geometry/number-of-baselines gain.

### 3.4 Preconditions: common view and emission

Two physical preconditions hold for every technique:

1. **The emitter must be transmitting during the collection.** Emission control (EMCON) defeats
   passive geolocation completely. `passive_rf_fix` already enforces this through `_is_emitting`.
2. **TDOA/FDOA need the same emission at ≥2–3 receivers at the same time (common view).** For a ground
   emitter and a LEO receiver at altitude h with elevation mask ε, the Earth central angle of the
   receiver's visibility footprint is λ = 90° − ε − asin(cos ε · R_E/(R_E+h)). For `mt-sigint-geolocate`'s
   orbit (a = 7178.137 km, h ≈ 800 km): λ ≈ 27.3° at ε = 0° and ≈ 22.7° at ε = 5°. Two satellites in the
   same plane can see the same ground point only if their separation is at most 2λ (≈45–55°). The
   vignette places SIGINT-1/2/3 at 0°/120°/240° true anomaly in one plane, **so no two of them ever see
   RED-EMITTER at the same time.** No implementation of simultaneous multilateration, however correct,
   can characterize the emitter with this geometry. A HawkEye-like ~300 km spacing is ≈2.5° of arc at
   this altitude, which gives common view for almost the whole pass.

### Sources

- *US 7,242,346, Pulse descriptor word generator* — [live](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7242346) · [snapshot](https://web.archive.org/web/2026/https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7242346) · accessed 2026-11-01.
- *Microwave Journal, ELINT receiver cards* — [live](https://microwavejournal.com/articles/1662-two-cards-to-convert-a-microwave-receiver-into-a-state-of-the-art-elint-system) · [snapshot](https://web.archive.org/web/2026/https://microwavejournal.com/articles/1662-two-cards-to-convert-a-microwave-receiver-into-a-state-of-the-art-elint-system) · accessed 2026-11-01.
- *Hubble Network, How HawkEye 360 finds RF signals from space* — [live](https://hubble.com/community/guides/how-hawkeye-360-finds-rf-signals-from-space/) · [snapshot](https://web.archive.org/web/2026/https://hubble.com/community/guides/how-hawkeye-360-finds-rf-signals-from-space/) · accessed 2026-11-01.
- *US 7,667,640, emitter geolocation using satellite signals* — [live](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7667640) · [snapshot](https://web.archive.org/web/2026/https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7667640) · accessed 2026-11-01.
- *KICS, Emitter geolocation based on TDOA/FDOA* — [live](https://journal.kics.or.kr/digital-library/34922) · [snapshot](https://web.archive.org/web/2026/https://journal.kics.or.kr/digital-library/34922) · accessed 2026-11-01.
- *Janes, HawkEye 360 expands satellite-based RF data collection* — [live](https://www.janes.com/defence-intelligence-insights/defence-news/hawkeye-360-expands-satellite-based-rf-data-collection) · [snapshot](https://web.archive.org/web/2026/https://www.janes.com/defence-intelligence-insights/defence-news/hawkeye-360-expands-satellite-based-rf-data-collection) · accessed 2026-11-01.
- *ESA, MetOp Search and Rescue* — [live](https://www.esa.int/Applications/Observing_the_Earth/Meteorological_missions/MetOp/Overview7) · [snapshot](https://web.archive.org/web/2026/https://www.esa.int/Applications/Observing_the_Earth/Meteorological_missions/MetOp/Overview7) · accessed 2026-11-01.
- *NOAA SARSAT, MEOSAR* — [live](https://www.sarsat.noaa.gov/meosar.html) · [snapshot](https://web.archive.org/web/2026/https://www.sarsat.noaa.gov/meosar.html) · accessed 2026-11-01.
- *Clements et al., direct geolocation (UT Austin)* — [live](https://radionavlab.ae.utexas.edu/wp-content/uploads/2023/05/clements-direct-geolocation.pdf) · [snapshot](https://web.archive.org/web/2026/https://radionavlab.ae.utexas.edu/wp-content/uploads/2023/05/clements-direct-geolocation.pdf) · accessed 2026-11-01.
- *UniBw München, hybrid geolocation approach* — [live](https://athene-forschung.rz.unibw-muenchen.de/147917) · [snapshot](https://web.archive.org/web/2026/https://athene-forschung.rz.unibw-muenchen.de/147917) · accessed 2026-11-01.
- *Fowler, EECE 522 notes, ML for TDOA/FDOA* — [live](https://ws2.binghamton.edu/fowler/fowler%20personal%20page/EE522_files/EECE%20522%20Notes_15%20ML%20for%20TDOA-FDOA_revised.pdf) · [snapshot](https://web.archive.org/web/2026/https://ws2.binghamton.edu/fowler/fowler%20personal%20page/EE522_files/EECE%20522%20Notes_15%20ML%20for%20TDOA-FDOA_revised.pdf) · accessed 2026-11-01.
- *US 7,663,547, weighted least-squares emitter geolocation* — [live](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7663547) · [snapshot](https://web.archive.org/web/2026/https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/7663547) · accessed 2026-11-01.
- *TU Delft, Triple-satellite geolocation from LEO* — [live](https://repository.tudelft.nl/record/uuid:9295cd30-63bd-4b62-9bd3-cec8df7b2edb) · [snapshot](https://web.archive.org/web/2026/https://repository.tudelft.nl/record/uuid:9295cd30-63bd-4b62-9bd3-cec8df7b2edb) · accessed 2026-11-01.

## 4. Operational Context

A SIGINT crew characterizing a naval emitter works in this order. First, configure the payload: band,
intercept mode, dwell. That is a command the satellite receives over its TT&C uplink at a ground-station
pass. Second, collect when the emitter is in view of the cluster and transmitting. Collection is
window-gated by geometry, not by the uplink pass. Third, process the fix on the ground or on board,
report it with its error ellipse, and decide whether it meets the requirement (for example "good
enough to cue an ISR collect" or "good enough to target"). The adversary's main counter is EMCON:
go silent while the cluster is overhead. Jamming the collector is a secondary option, and an awkward
one because the collector is passive. A crew that schedules the collection for a predicted
transmission window and an overhead pass is doing the job. A crew that issues "geolocate" and expects
a result regardless of geometry is not, and the simulator should show the difference.

### Sources

Synthesis of §3's sources; no new claims.

## 5. Implementation Guidance

**How the shipped pieces fit the physics (checked against the code at `be41705`):**

- `passive_rf_fix(network, world, target_id, t, ap, three_d)` models **ground (SSN) receivers listening
  to an orbiting emitter**. Its test (`test_ssn.py::test_passive_rf_fix_requires_min_receivers_and_emitting_target`)
  uses a satellite target with `bus_state`. For `mt-sigint-geolocate` (space receivers, ground emitter)
  it returns `None` for **two independent reasons**: `_is_emitting` reads `asset.bus_state`, which a
  `ground_station` asset does not have (so the emitter is never "emitting"), and
  `AccessProvider._endpoints_present` accepts `SENSOR_OBSERVATION` only when the target is a satellite. Wiring it
  into an order unchanged (plan option (a) as worded) therefore **cannot** reach `characterize_emitter`.
- `geolocation_error_km(band, mode, dwell_s, n_collectors)` is a sound moderate-fidelity accuracy model
  (§3.3). It has no caller on the order path.
- `sigint.task_collection` sets `band`/`intercept_mode`/`dwell_s`/`confidence_threshold` in
  `payload_state.detail`. It runs when the command is **delivered** over TT&C, which is not when the
  emitter is in view.
- The `emitter_silent` inject is message-only. No engine state represents a ground emitter's emission,
  so the vignette's EMCON teaching point does nothing mechanically.

**Recommended path (the D4 answer):**

- **Do deliver characterization through the `observe` order with `intent="characterize"`**, issued by
  a SIGINT payload asset against the emitter. That keeps invariant 4 (plan-first, window-gated) and
  reuses `dry_run` for "why can't I?", `_h_observe` for the Track write, and the existing
  `characterizes = (intent == "characterize")` gate. **Don't** make the `sigint.task_collection` bus
  verb produce the Track (plan option (b)). A verb executes at command delivery, so it would
  characterize an emitter the satellite cannot see, which is physically wrong and bypasses access
  gating. The verb stays what it is: the configurator whose `detail` values the observe order reads.
- **Do generalize `passive_rf_fix` instead of writing a second fix function.** It should accept
  space-based receivers (SIGINT payload assets, or a declared SIGINT group) against a **ground** emitter
  as well as its current ground-receivers-vs-satellite case. Per receiver, a ground emitter uses the
  ground-site↔satellite visibility predicate the engine already has (`_ground_sat_predicate`, the
  geometry behind `command_uplink` and `jam_footprint`), with the emitter's elevation mask. Keep the
  FR-1650 counts: ≥3 simultaneous receivers for a surface fix (§3.2), ≥4 for 3D.
- **Do give a ground emitter an emission state** (an additive field on the emitter entity, default
  "emitting"), and turn the `emitter_silent` inject into a real effect that sets it for a duration.
  `_is_emitting` reads that field for ground emitters and keeps reading `bus_state.comms.status` for
  satellites.
- **Do define "characterized" as all three of:** emitting during the collection, a fix produced
  (`passive_rf_fix` not `None`), and `geolocation_error_km(band, mode, dwell_s, n_receivers) ≤`
  the objective's authored `max_error_km`. Default `max_error_km` to the payload's
  `confidence_threshold` if set, or else a vignette value. A collection that intercepts the emitter
  but misses on geometry or error yields a **detected, uncharacterized** Track (confidence raised,
  `characterized=False`). That is the honest middle state (§3.1 items 1–2 without item 3).
- **Do record the error** on the Track (for example the 1σ value in the existing `uncertainty`
  fields), so the belief scene can draw an error circle. `Track.state_estimate` is an `OrbitState` and
  cannot hold a ground fix. Adding a ground-location estimate is a `03`/`06` data-model decision, not
  something to improvise in the order handler.
- **Do fix the vignette geometry** (an `08-vignette-development` task): put the three SIGINT satellites
  in a cluster a few degrees apart (≈250–500 km, §3.2/§3.4) so common view exists, and change the
  learning objective from "multi-pass" to "three simultaneous look angles". Otherwise the mechanic
  ships correct and the objective stays unreachable.
- **Don't drop single-satellite multi-pass Doppler (§3.2) entirely.** It is real, it is what the
  current learning objective describes, and it is the right model for a lone collector. It needs state
  accumulated across passes (two passes to resolve A/B), so it is a sensible **Could** follow-on that
  reuses the same `characterized` predicate with N = passes.
- **Don't let a Red objective score custody confidence as the counter to characterization.**
  `deny_characterization` currently uses `deny_custody` with `min_conf: 0.7`. The physical counter is
  "the emitter is not characterized by the deadline", which is the exact complement of Blue's
  predicate. EMCON timing and jamming the collectors are Red's levers.

## 6. Feature Mapping

Release 2.0 F-04 / B-19 / B-20; FR-1650 (needs a delta to cover space receivers against a ground
emitter: route to `04-requirements-engineering`); FS-104 (SDA Tasking). The vignette consumer is
`mt-sigint-geolocate`. Its `preserve_constellation` description says "All 3 SIGINT sats" while its
metric targets only `SIGINT-1`, a separate content defect for `08-vignette-development`. The decision
memo is [`docs/feature-planning/06a-release-2-d3-d4-research.md`](../../feature-planning/06a-release-2-d3-d4-research.md).

## 7. Related Topics

[R129](R129-sigint-collection-and-geolocation-accuracy.md) (the accuracy model),
[R109](R109-sensor-operations.md) §3.10 (the passive-RF receiver rule),
[R105](R105-custody-theory.md) (custody characterization, not to be conflated),
[R118](R118-space-surveillance-networks.md) (the network shape),
[R120](R120-access-window-and-geometry-planning.md) (visibility geometry),
[R138](R138-satellite-service-availability-and-link-denial-measurement.md) (the companion Release 2.0
D3 topic).
