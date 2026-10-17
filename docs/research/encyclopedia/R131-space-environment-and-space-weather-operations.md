# R131 — Space Environment and Space Weather Operations

> **Document ID:** R131
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R110](R110-communications.md), [R111](R111-power-and-thermal-operations.md)
> **Referenced By:** [R121](R121-telemetry-logging-and-attack-signatures.md), [R117](R117-directed-energy-and-kinetic-effects.md)
> **Produces:** implementation constraints for [`engine/perturbations.py`](../../../spacesim/engine/perturbations.py) (`atmospheric_density`, `drag_acceleration`, `secular_drag_decay`), [`engine/bus.py`](../../../spacesim/engine/bus.py) (`advance_bus`'s `storm_mult`), [`engine/world.py`](../../../spacesim/engine/world.py) (`WorldState.space_weather`), and the `space_weather` inject type in [`session/manager.py`](../../../spacesim/session/manager.py); (v1.1) a numeric index-series (F10.7/Kp) input shape for `BL-0074`/B8's index-driven drag/anomaly-rate feature
> **Feature Mapping:** FS-105 (Spacecraft Operations), FS-104 (SDA Tasking)
> **Related Topics:** [R110](R110-communications.md) (Communications — the jam/interference signature this topic's ionospheric effects can be confused with), [R111](R111-power-and-thermal-operations.md) (Power and Thermal Systems Operations — the eclipse-drain model space weather scales), [R121](R121-telemetry-logging-and-attack-signatures.md) (Telemetry, Logging, and Attack-Signature Modeling — the symptom layer an environmental event must be disambiguated within), [R127](R127-conjunction-assessment-and-collision-avoidance.md) (Conjunction Assessment — drag-driven orbit uncertainty), [R117](R117-directed-energy-and-kinetic-effects.md) (Directed Energy and Kinetic Effects — debris-persistence-by-altitude shares this topic's drag mechanism, v1.2)
> **Last Reviewed:** 2026-09-27
> **Primary Sources Consulted:** 4 (2 for the v1.0 storm/scintillation/SEU content; 2 new for
> v1.1's numeric-index-driven drag content)

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

*v1.1 changelog (2026-09-27): grounds `BL-0074`/B8 (an index time series driving deterministic
LEO drag and anomaly rate) — a new §3 subsection on the real F10.7/Kp numeric-index inputs to
atmospheric density models, and a new §5 bullet on how to wire them without inventing an unsourced
formula. No existing content changed in substance.*

## 1. Purpose

Identified as **GAP-01** in the Independent Strategic Review Board report
([`docs/reviews/strategic-review-2026-07.md`](../../reviews/strategic-review-2026-07.md) Part 3):
the simulator already has a `space_weather` inject type and an eclipse-drain multiplier
(`advance_bus`'s `storm_mult`), and `engine/perturbations.py` has an unwired
`secular_drag_decay` function — but no encyclopedia topic explains what real geomagnetic/solar
storms actually do to spacecraft operations, or why the *hardest* SDA/operator judgment a real
storm forces is distinguishing an environmental anomaly from an adversarial one using the same
telemetry symptoms. This topic supplies that grounding so a future feature (a richer storm model,
a telemetry linkage, or an attack-vs-environment training drill) is built on the real operational
texture rather than an invented one.

## 2. Scope

Covers: the physical mechanisms by which geomagnetic/solar storms affect drag, RF propagation,
onboard electronics, and power systems; the real forecasting/index infrastructure operators
actually use; and the operational craft of disambiguating an environmental anomaly from an
adversarial one. Does **not** cover: the bus/payload state machine the affected parameters live on
([R111](R111-power-and-thermal-operations.md)), the jam-signature model this topic's ionospheric
effects can be mistaken for ([R110](R110-communications.md), [R115](R115-electronic-warfare-in-space-operations.md)),
or the general symptom-not-diagnosis telemetry design this topic's disambiguation problem is an
instance of ([R121](R121-telemetry-logging-and-attack-signatures.md)).

## 3. Concepts

**Geomagnetic storms increase LEO drag by heating and expanding the upper atmosphere.** During a
storm, energy deposited by ionospheric currents and precipitating energetic particles heats the
thermosphere, increasing neutral gas density at typical LEO altitudes (300–600 km) by a factor of
roughly 2–10 during a major event, producing a sudden increase in aerodynamic drag and accelerated
orbital decay ([Orbital Radar, "How Solar Storms Affect Satellites — Drag, Radiation & Charging"](https://orbitalradar.com/space-weather/solar-storms-and-satellites)
([Wayback](https://web.archive.org/web/2026/https://orbitalradar.com/space-weather/solar-storms-and-satellites))
· [NOAA/NWS SWPC, "Geomagnetic Storms"](https://www.spaceweather.gov/phenomena/geomagnetic-storms)
([Wayback](https://web.archive.org/web/2026/https://www.spaceweather.gov/phenomena/geomagnetic-storms))).
This is exactly the mechanism `engine/perturbations.py:atmospheric_density`/`drag_acceleration`/
`secular_drag_decay` model at the propagator level — but as of this writing, `advance_bus`'s
`storm_mult` (§ below) scales *battery eclipse drain*, not drag; the drag-decay path and the
bus-power path are two independent, currently unconnected consumers of a storm event.

**A storm that barely registers on NOAA's severity scale can still be operationally significant for
LEO fleets.** On 2022-02-03, SpaceX launched 49 Starlink satellites into a low (~210 km) insertion
orbit; a geomagnetic storm rated only **G1** — the lowest of NOAA's five-step G-scale — arrived
days later and increased atmospheric drag by up to 50% above pre-launch expectations, causing 38 of
the 49 satellites to lose enough altitude to re-enter within days
([Space.com, "SpaceX says a geomagnetic storm just doomed 40 Starlink internet satellites"](https://www.space.com/spacex-starlink-satellites-lost-geomagnetic-storm)
([Wayback](https://web.archive.org/web/2026/https://www.space.com/spacex-starlink-satellites-lost-geomagnetic-storm))
· [Baruah et al., "The Loss of Starlink Satellites in February 2022: How Moderate Geomagnetic
Storms Can Adversely Affect Assets in Low-Earth Orbit," *Space Weather* 22, e2023SW003716 (2024)](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2023SW003716)
([Wayback](https://web.archive.org/web/2026/https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2023SW003716))).
Space weather alone was not sufficient — the low insertion altitude and the satellites' high
drag-to-inertia ratio compounded it — but the event is the canonical real-world illustration that
"severity" as scored by a public index and "operational consequence" for a specific fleet are not
the same thread: a vignette-author lesson directly relevant to how `space_weather.severity`
(`{"none","minor","severe"}`) is authored against a specific force's orbital regime.

**Ionospheric scintillation degrades RF links independently of any adversary jamming.** Storm-driven
plasma irregularities in the ionosphere cause rapid amplitude/phase fluctuations ("scintillation")
in radio signals; satellite links are especially exposed because the signal crosses the ionosphere
twice (up and back down), and severe scintillation can prevent a receiver from maintaining phase
lock entirely ([NOAA/NWS SWPC, "Ionospheric Scintillation"](https://www.swpc.noaa.gov/phenomena/ionospheric-scintillation)
([Wayback](https://web.archive.org/web/2026/https://www.swpc.noaa.gov/phenomena/ionospheric-scintillation))).
The observable pattern — degraded `cn0_dbhz`, elevated `ber`, intermittent `uplink_lock` loss — is
**the same parameter set** [R121](R121-telemetry-logging-and-attack-signatures.md) documents as
the EW-jam signature (`telemetry.py`'s `comms.rx_power_dbm`/`cn0_dbhz`/`ber`/`uplink_lock` group).
This is the operational core of GAP-01: a storm and a jamming campaign can look identical on the
link-budget telemetry an operator sees first.

**NOAA's G/S/R space-weather scales exist precisely to give operators a shared, quantified severity
vocabulary independent of any single mission's symptom telemetry.** NOAA's Space Weather Prediction
Center scores three independent 1–5 scales — G (geomagnetic storms), S (solar radiation storms), R
(radio blackouts) — each explicitly listing satellite-operations effects per level (e.g., G2:
possible surface charging and orientation-correction needs; higher levels: memory-device upsets and
imaging-sensor noise) ([NOAA/NWS SWPC, "NOAA Space Weather Scales"](https://www.spaceweather.gov/noaa-scales-explanation)
([Wayback](https://web.archive.org/web/2026/https://www.spaceweather.gov/noaa-scales-explanation))).
This is the real-world corroborating signal an operator uses to disambiguate: an anomaly that
*coincides in time* with an independently-published, externally-verifiable G/S/R index reading is
environmentally attributable; an anomaly with no such coincidence is not.

**Single-event upsets (SEUs) are a distinct, radiation-driven electronics failure mode, separate
from both drag and RF effects.** A single energetic particle (galactic cosmic ray, solar energetic
particle, or a trapped proton encountered in the South Atlantic Anomaly or polar regions) striking a
semiconductor can flip a logic state, producing a transient fault — commonly a command-reject,
memory-scrub, or unexpected reset — that looks, at the telemetry-symptom level, like the FSW-error/
CPU-load pattern [R121](R121-telemetry-logging-and-attack-signatures.md) documents as the *cyber*
signature ([Wikipedia's overview cites, and is corroborated by, the SIDC and ScienceDirect literature
on SEU causation](https://en.wikipedia.org/wiki/Single-event_upset)
([Wayback](https://web.archive.org/web/2026/https://en.wikipedia.org/wiki/Single-event_upset));
*Single source (Tier D corroborating a Tier B claim)* — the underlying SEU-mechanism claim is
well-established in the peer-reviewed radiation-effects literature the Wikipedia article surveys,
used here only as a navigational pointer per the methodology's Tier D rule). SEU rate correlates
with orbital geometry (SAA transits, polar-region crossings) more than with storm severity directly,
which is itself a corroborating signal distinct from the G-scale.

**Real operators run storm mitigation as a scheduled, forecast-driven posture change, not a reactive
one.** Ahead of a forecast storm, LEO operators may pre-emptively raise orbital altitude to increase
drag margin, and safe-mode postures are sometimes adopted ahead of predicted charging-risk events —
a deliberate anticipatory response, not a symptom-triggered reaction
([Orbital Radar, *op. cit.*](https://orbitalradar.com/space-weather/solar-storms-and-satellites)).
This is the doctrinal precedent for treating a `space_weather` inject as something White Cell can
*telegraph* (an advisory) before firing the severity change, mirroring how the existing inject
library's `space_weather_severe` template already pairs the severity effect with an advisory
message to all cells.

**Two independent numeric indices, not one, are the real inputs a density model consumes — F10.7
for the slow solar-cycle baseline, Kp/Ap for fast geomagnetic disturbances.** The F10.7 index
(solar radio flux at 10.7 cm wavelength) tracks the Sun's extreme-ultraviolet output, which is
absorbed high in the thermosphere and heats it — this sets the atmosphere's gradual, weeks-to-years
baseline density; the Kp/Ap index measures fast geomagnetic disturbances driven by coronal mass
ejections and storms, the same event class §3 above already covers qualitatively
([Orbital Radar, "F10.7 Solar Flux Index: Satellite Drag Explained"](https://orbitalradar.com/glossary/solar-flux)
([Wayback](https://web.archive.org/web/2026/https://orbitalradar.com/glossary/solar-flux))). Real
high-precision density models (NRLMSISE-00, JB2008) take **both** the daily F10.7 value and its
81-day running average, plus a geomagnetic index, as inputs — never a single scalar "severity"
value — because the slow solar-cycle term and the fast storm term are physically distinct and can
move independently (a quiet-Kp period during high solar maximum still elevates baseline density;
a sharp Kp spike during solar minimum still spikes density transiently)
([SPENVIS, "Help: Atmosphere and ionosphere models"](https://www.spenvis.oma.be/help/background/atmosphere/models.html)
([Wayback](https://web.archive.org/web/2026/https://www.spenvis.oma.be/help/background/atmosphere/models.html))).
This is the concrete numeric-index shape `BL-0074`/B8 asks for: an index *time series* (not a
single enum value) is exactly how the real world represents this input, and the existing
`space_weather.severity` enum (`{"none","minor","severe"}`) is a coarse, already-useful
*qualitative* proxy for a small number of common vignette-authoring cases — B8's index-series
input is an additive, more granular alternative for the same underlying physics, not a
replacement for the existing enum.

### Sources

- *Orbital Radar, "How Solar Storms Affect Satellites — Drag, Radiation & Charging"* — [live](https://orbitalradar.com/space-weather/solar-storms-and-satellites)
  · [snapshot](https://web.archive.org/web/2026/https://orbitalradar.com/space-weather/solar-storms-and-satellites)
  · accessed 2026-07-01.
- *NOAA/NWS Space Weather Prediction Center, "Geomagnetic Storms"* — [live](https://www.spaceweather.gov/phenomena/geomagnetic-storms)
  · [snapshot](https://web.archive.org/web/2026/https://www.spaceweather.gov/phenomena/geomagnetic-storms)
  · accessed 2026-07-01.
- *Space.com, "SpaceX says a geomagnetic storm just doomed 40 Starlink internet satellites"* (event
  2022-02-03/2022-02-08) — [live](https://www.space.com/spacex-starlink-satellites-lost-geomagnetic-storm)
  · [snapshot](https://web.archive.org/web/2026/https://www.space.com/spacex-starlink-satellites-lost-geomagnetic-storm)
  · accessed 2026-07-01.
- *Baruah et al., "The Loss of Starlink Satellites in February 2022: How Moderate Geomagnetic Storms
  Can Adversely Affect Assets in Low-Earth Orbit," Space Weather 22, e2023SW003716 (2024)* — [live](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2023SW003716)
  · [snapshot](https://web.archive.org/web/2026/https://agupubs.onlinelibrary.wiley.com/doi/10.1029/2023SW003716)
  · accessed 2026-07-01.
- *NOAA/NWS Space Weather Prediction Center, "Ionospheric Scintillation"* — [live](https://www.swpc.noaa.gov/phenomena/ionospheric-scintillation)
  · [snapshot](https://web.archive.org/web/2026/https://www.swpc.noaa.gov/phenomena/ionospheric-scintillation)
  · accessed 2026-07-01.
- *NOAA/NWS Space Weather Prediction Center, "NOAA Space Weather Scales"* — [live](https://www.spaceweather.gov/noaa-scales-explanation)
  · [snapshot](https://web.archive.org/web/2026/https://www.spaceweather.gov/noaa-scales-explanation)
  · accessed 2026-07-01.
- *Single-event upset (Tier D navigational pointer to the peer-reviewed SEU-mechanism literature it
  surveys)* — [live](https://en.wikipedia.org/wiki/Single-event_upset)
  · [snapshot](https://web.archive.org/web/2026/https://en.wikipedia.org/wiki/Single-event_upset)
  · accessed 2026-07-01.
- *Orbital Radar, "F10.7 Solar Flux Index: Satellite Drag Explained"* — [live](https://orbitalradar.com/glossary/solar-flux)
  · [snapshot](https://web.archive.org/web/2026/https://orbitalradar.com/glossary/solar-flux)
  · accessed 2026-09-27.
- *SPENVIS, "Help: Atmosphere and ionosphere models"* — [live](https://www.spenvis.oma.be/help/background/atmosphere/models.html)
  · [snapshot](https://web.archive.org/web/2026/https://www.spenvis.oma.be/help/background/atmosphere/models.html)
  · accessed 2026-09-27.

## 4. Operational Context

Real spacecraft operations centers treat space weather as a standing, externally-forecast
operational input, not an occasional curiosity: NOAA SWPC (and equivalent allied services) publish
continuously updated G/S/R index forecasts specifically so operators can correlate an onboard
anomaly against an independent, external severity signal before concluding it is hostile. The
February 2022 Starlink loss is the clearest recent illustration that this correlation is not always
clean — a G1 event (the mildest category) still produced an operationally severe drag anomaly for
one specific fleet at one specific altitude, meaning "check the public index" is necessary but not
always sufficient corroboration; operators additionally look for whether the anomaly's *pattern* is
geometry-correlated (SAA/polar-crossing timing for SEUs, sun-angle/eclipse timing for thermal, storm
onset-and-decay timing for drag/scintillation) versus adversary-correlated (tied to a specific
geographic jammer footprint, a specific uplink session, or a specific target-selection pattern that
storms do not produce).

## 5. Implementation Guidance

- **A richer storm model should extend `world.space_weather`'s existing `{"severity": ...}` shape**
  (`engine/world.py`) rather than introducing a parallel environmental-state object — `severity` is
  already the shared vocabulary the `space_weather` inject, `advance_bus`'s `storm_mult`, and the
  vignette schema (`orbital_environment.space_weather`) all key off.
- **If a future feature wires storm severity into `engine/telemetry.py`'s attack-signature model
  (currently unconnected — `telemetry.py` does not read `world.space_weather` at all despite
  `session/manager.py`'s inline comment describing an intended "FSW errors climb in 'severe'"
  linkage), it must add a genuine environmental term, not reuse the cyber `_attack_term` branch** —
  conflating the two would make the attack-vs-environment disambiguation this topic exists to ground
  literally impossible to teach, since the underlying signal would be identical by construction.
  Per [R121](R121-telemetry-logging-and-attack-signatures.md) §5, a new environmental term needs its
  own flag and its own `_attack_term` branch, keyed off `world.space_weather["severity"]`, distinct
  from any effect-category flag.
- **Wiring `secular_drag_decay`/`atmospheric_density`/`drag_acceleration` (`engine/perturbations.py`,
  currently pure functions not yet called from the propagator) to `space_weather.severity` should
  scale density by storm severity**, mirroring the real 2–10× density-multiplication range cited
  above, rather than inventing an unsourced multiplier — and should stay a pure, deterministic
  function of `(severity, altitude)` to preserve replay-exactness (MSTR-002 invariant 1).
- **An index-series feature (`BL-0074`/B8) should add a new, additive `space_weather` shape
  (e.g. a time-keyed F10.7/Kp series) alongside the existing `severity` enum, not replace it** —
  both key the same `atmospheric_density`/`drag_acceleration` consumer, so the density function
  should accept either input form and derive an internal density multiplier from whichever is
  present (index series takes precedence if both are somehow set), keeping every existing
  `severity`-only vignette's behavior byte-identical. Deriving a numeric multiplier from F10.7/Kp
  should interpolate between the same 2–10× real-world range this topic already cites for
  qualitative severity, not introduce an independent, differently-scaled formula — a vignette
  author should get a comparable drag effect whichever input form they choose. The rate of
  environment-induced anomalies (B8's second ask) should scale with the same derived multiplier,
  reusing the multiplier as a single shared "how disturbed is the environment right now" signal
  rather than deriving anomaly rate from the raw index independently of drag.
- **A disambiguation training feature (e.g. the "attack-signature diagnosis trainer" concept in the
  strategic review's Part 5) should present the G/S/R-index-style corroborating signal alongside
  telemetry**, not just the symptom telemetry alone — the real disambiguation skill this topic
  documents depends on cross-referencing an independent severity index, which the current engine has
  no analog of exposing to the operator UI.
- **A `space_weather` inject fired by White Cell should be advisory-first when representing a
  real-world-plausible storm** (matching the existing `space_weather_severe` template's paired
  advisory message), reserving a *silent* severity change for vignettes deliberately testing whether
  Blue/Red correctly diagnose an unannounced anomaly — conflating the two authoring patterns would
  blur the pedagogical point of either.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer for any telemetry/bus-model extension; FS-104
(SDA Tasking) is the consumer for any feature surfacing environmental corroboration alongside SDA
custody/anomaly assessment.

## 7. Related Topics

[R110](R110-communications.md) (Communications — the ionospheric-scintillation/jam-signature
overlap), [R111](R111-power-and-thermal-operations.md) (Power and Thermal Systems Operations — the
eclipse-drain model `storm_mult` scales), [R121](R121-telemetry-logging-and-attack-signatures.md)
(Telemetry, Logging, and Attack-Signature Modeling — the symptom-not-diagnosis design this topic's
disambiguation problem is the hardest instance of), [R127](R127-conjunction-assessment-and-collision-avoidance.md)
(Conjunction Assessment — drag-driven orbit uncertainty feeding conjunction risk).
