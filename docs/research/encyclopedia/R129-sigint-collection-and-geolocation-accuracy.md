# R129 — SIGINT Collection and Geolocation Accuracy

> **Document ID:** R129
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R109](R109-sensor-operations.md), [R104](R104-collection-management.md)
> **Referenced By:** FS-104
> **Produces:** implementation constraints for [`engine/sigint.py`](../../../spacesim/engine/sigint.py), [`engine/buscommands.py`](../../../spacesim/engine/buscommands.py) (`sigint.task_collection`)
> **Feature Mapping:** FS-104 (SDA Tasking)
> **Related Topics:** [R109](R109-sensor-operations.md) (Sensor Operations — the beam-mode/host-power model this topic mirrors for the SIGINT payload type),
> [R104](R104-collection-management.md) (Collection Management — the tasking-contention model SIGINT collection is booked under),
> [R102](R102-space-domain-awareness.md) (Space Domain Awareness — custody confidence vs. emitter geolocation confidence are parallel but distinct quantities),
> [R118](R118-space-surveillance-networks.md) (Space Surveillance Networks — the multi-collector aggregation pattern this topic's multilateration model parallels)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 5

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

`engine/sigint.py` mirrors `engine/isr.py`'s beam-mode-database pattern for the SIGINT payload
type, but for a different physical problem: instead of imaging a target, a SIGINT payload
intercepts an emitter's transmission and estimates *where the emitter is*. No R1xx topic
previously grounded this — R109 (Sensor Operations) covers EO/SAR imaging sensors, not passive RF
intercept and geolocation. This topic gives the implementer the real ELINT/SIGINT collection
discipline behind `BANDS`/`MODES` and the real multilateration/TDOA practice behind
`geolocation_error_km()`'s √dwell × √N-collector scaling, so a future SIGINT feature (a new band,
a new intercept mode, a higher-fidelity geolocation model) extends real intercept-geolocation
practice rather than an invented curve.

## 2. Scope

Covers: the real frequency-band/emitter taxonomy behind `BANDS`, the scan/track/geolocate
intercept-mode distinction behind `MODES`, and the real time-difference-of-arrival (TDOA)
multilateration practice behind `geolocation_error_km()`'s dwell- and collector-count-dependent
accuracy model. Does **not** cover: sensor-tasking contention/booking, which SIGINT collection
shares with every other modality ([R104](R104-collection-management.md)); the EO/SAR beam-mode
trade this topic's structure mirrors but does not duplicate ([R109](R109-sensor-operations.md));
or custody/track confidence decay, which is a related but distinct concept from emitter
geolocation uncertainty ([R105](R105-custody-theory.md)).

## 3. Concepts

**ELINT is a distinct SIGINT subdiscipline targeting non-communication electronic emissions, not
voice/data traffic.** Electronic intelligence (ELINT) is "intelligence-gathering that involves the
interception of non-communication signals, primarily those coming from electronic systems used in
defense and weaponry," as opposed to communications intelligence (COMINT), which targets
communications traffic
([TechTarget, *What is ELINT (electronic intelligence)?*](https://www.techtarget.com/whatis/definition/ELINT-electronic-intelligence)
([Wayback](https://web.archive.org/web/2026/https://www.techtarget.com/whatis/definition/ELINT-electronic-intelligence))) —
the real-world basis for `engine/sigint.py` modeling a payload that intercepts and characterizes
emissions (radars, beacons, jammers, navigation signals) rather than a comms-intercept model;
the NSA's own "TechELINT" sub-category "describes the signal structure, emission characteristics,
modes of operation, emitter functions, and weapons systems associations of such emitters as radars,
beacons, jammers, and navigational signals"
([National Security Agency, cited in Trenton Systems, *SIGINT vs. COMINT vs. ELINT*](https://www.trentonsystems.com/en-us/resource-hub/blog/sigint-vs-comint-vs-elint)
([Wayback](https://web.archive.org/web/2026/https://www.trentonsystems.com/en-us/resource-hub/blog/sigint-vs-comint-vs-elint))) —
the real basis for `BANDS`' frequency-keyed structure (UHF through W-band) standing in for the
emitter-type taxonomy a real ELINT analyst would key off instead.

**TDOA-based satellite multilateration is the real-world precedent for `geolocation_error_km()`'s
collector-count scaling.** The NRO's declassified POPPY ELINT satellite program "used the
principle of signals time difference of arrival, which enables precise locating of an object," and
"with multiple satellites in orbit, Poppy could geolocate emission sources, at least roughly"
([National Security Archive, *GRAB and POPPY: America's Early ELINT Satellites*, 1962-1977](https://nsarchive2.gwu.edu/NSAEBB/NSAEBB392/docs/37.pdf)
([Wayback](https://web.archive.org/web/2026/https://nsarchive2.gwu.edu/NSAEBB/NSAEBB392/docs/37.pdf))) —
the direct real-world precedent for `n_collectors` improving a fix at all. POPPY's successor
program, PARCAE, "consisted of clusters of three satellites... to enable precise geolocation via
signal triangulation"
([IEEE Spectrum, *A Cold War Satellite Program Called Parcae Revolutionized Signals Intelligence*](https://spectrum.ieee.org/reconnaissance-satellite)
([Wayback](https://web.archive.org/web/2026/https://spectrum.ieee.org/reconnaissance-satellite))) —
moving from "roughly" (few/single-satellite TDOA) to "precise" (three-satellite clusters) is the
real operational basis for `geolocation_error_km()`'s `baseline_factor = 1/√n_collectors` term:
more simultaneous TDOA baselines from more collectors is what actually buys precision, not a
single collector dwelling longer alone.

**TDOA accuracy is jointly a function of measurement precision and collector geometry, and spans
orders of magnitude in practice.** Both "precision in TDOA measurements and the relative geometry
between receivers and transmitter affect localization accuracy," with "traditional TDOA
implementations" achieving on the order of "100 meters" while "advanced carrier phase
differencing approaches can achieve accuracy of less than one meter"
([CRFS, *How accurate is TDOA geolocation?*](https://www.crfs.com/blog/how-accurate-tdoa-geolocation)
([Wayback](https://web.archive.org/web/2026/https://www.crfs.com/blog/how-accurate-tdoa-geolocation))) —
the real-world basis for treating geolocation accuracy as a continuous, multi-factor quantity
(`_REF_GEOLOC_KM` scaled by mode/band/dwell/collector terms) rather than a fixed per-mode constant,
and for `MODES`' `accuracy_factor` distinguishing a coarse `scan` from a dedicated `geolocate` pass
the way a real system distinguishes a basic single-baseline fix from a dedicated high-precision
collection.

### Sources

- *TechTarget, What is ELINT (electronic intelligence)?* —
  [live](https://www.techtarget.com/whatis/definition/ELINT-electronic-intelligence)
  · [snapshot](https://web.archive.org/web/2026/https://www.techtarget.com/whatis/definition/ELINT-electronic-intelligence)
  · accessed 2026-06-27.
- *Trenton Systems, SIGINT vs. COMINT vs. ELINT: Key Differences and Must-Know Use Cases* (citing NSA) —
  [live](https://www.trentonsystems.com/en-us/resource-hub/blog/sigint-vs-comint-vs-elint)
  · [snapshot](https://web.archive.org/web/2026/https://www.trentonsystems.com/en-us/resource-hub/blog/sigint-vs-comint-vs-elint)
  · accessed 2026-06-27.
- *National Security Archive, GRAB and POPPY: America's Early ELINT Satellites* —
  [live](https://nsarchive2.gwu.edu/NSAEBB/NSAEBB392/docs/37.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://nsarchive2.gwu.edu/NSAEBB/NSAEBB392/docs/37.pdf)
  · accessed 2026-06-27.
- *IEEE Spectrum, A Cold War Satellite Program Called Parcae Revolutionized Signals Intelligence* —
  [live](https://spectrum.ieee.org/reconnaissance-satellite)
  · [snapshot](https://web.archive.org/web/2026/https://spectrum.ieee.org/reconnaissance-satellite)
  · accessed 2026-06-27.
- *CRFS, How accurate is TDOA geolocation?* —
  [live](https://www.crfs.com/blog/how-accurate-tdoa-geolocation)
  · [snapshot](https://web.archive.org/web/2026/https://www.crfs.com/blog/how-accurate-tdoa-geolocation)
  · accessed 2026-06-27.

## 4. Operational Context

Real SIGINT/ELINT satellite collection is a two-stage problem distinct from imaging: first
intercept and characterize an emission (band, modulation/PRF, power), then — if geolocation is the
objective — fuse multiple simultaneous intercepts of the *same* emission from spatially separated
collectors into a TDOA fix. A single collector dwelling on an emitter for longer improves
*detection confidence and characterization*, but real precision geolocation has always required
multiple collectors observing the same emission at once (POPPY → PARCAE's evolution from
single/few-satellite "rough" fixes to three-satellite-cluster "precise" triangulation is exactly
this distinction). `sigint.py`'s `geolocation_error_km()` models both factors as independent,
multiplicative terms — `dwell_factor` for the detection/characterization side, `baseline_factor`
for the multilateration side — which matches the real two-factor structure rather than collapsing
geolocation into a single "more time = better fix" knob.

## 5. Implementation Guidance

- **Keep `n_collectors` and `dwell_s` as independent terms in any future revision of
  `geolocation_error_km()`** — collapsing them into a single combined "effort" scalar would lose
  the real distinction between dwelling longer on one collector (better characterization) and
  adding simultaneous collectors (better triangulation baseline), which the POPPY/PARCAE precedent
  shows are genuinely different operational levers.
- **A new band added to `BANDS` should set `atmos_loss_db` consistent with real RF propagation
  physics** (atmospheric/rain attenuation increases with frequency) — the existing table's
  monotonic increase from UHF (0.1 dB) through W-band (8.0 dB) already follows this; preserve that
  ordering for any new entry rather than picking an arbitrary value.
- **A `geolocate`-class mode should always carry the highest `dwell_s_default` and
  `accuracy_factor` of the mode set**, mirroring the real distinction between a quick `scan` and a
  dedicated high-precision collection pass — don't add a new mode that achieves `geolocate`-grade
  accuracy at `scan`-grade dwell, which would have no real precedent.
- **If a future feature models actual multi-satellite TDOA fixes (not just an abstract
  `n_collectors` scalar)**, ground the baseline geometry in the same real precedent this topic
  cites (three-satellite clusters, not two) before inventing a constellation-geometry requirement,
  and reuse [R118](R118-space-surveillance-networks.md)'s multi-collector aggregation pattern
  rather than building a third, parallel multi-sensor-fusion mechanism.
- **Don't conflate `geolocation_error_km()`'s output with custody/track confidence**
  ([R105](R105-custody-theory.md)) — an emitter geolocation fix and a custody track are different
  quantities (one is intercept-derived positional uncertainty, the other is identity/track
  confidence over time) even though both ultimately feed the same cell's SDA picture.

## 6. Feature Mapping

FS-104 (SDA Tasking) is the direct consumer — `buscommands.sigint.task_collection`'s
`band`/`intercept_mode`/`dwell_s`/`confidence_threshold` parameters and the planned
`POST /sigint/compute` preview endpoint (`docs/FUTURE-WORK.md` §11.A.6) are the implemented feature
this topic grounds.

## 7. Related Topics

[R109](R109-sensor-operations.md) (Sensor Operations — the beam-mode-database pattern this topic
mirrors for a passive-intercept payload type instead of an imaging one),
[R104](R104-collection-management.md) (Collection Management — the tasking/booking contention
model SIGINT collection shares with every other sensor modality),
[R105](R105-custody-theory.md) (Custody Theory — the related-but-distinct confidence quantity a
SIGINT geolocation fix should not be conflated with),
[R118](R118-space-surveillance-networks.md) (Space Surveillance Networks — the multi-collector
aggregation pattern a future multi-satellite TDOA feature should reuse rather than reinvent).
