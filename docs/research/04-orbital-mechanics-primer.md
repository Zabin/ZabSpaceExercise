---
last_reviewed: 2026-06-12
primary_sources_consulted: 22
status: stable
---

# Orbital Mechanics Primer — The Sim's Physics of Access

[← Research index](INDEX.md) · [↑ Docs index](../INDEX.md) · methodology: [`10-sources-and-methodology.md`](10-sources-and-methodology.md)

Orbital mechanics is the upstream physics layer the simulator's effect resolver, access
gate, and bus model all stand on. This file is the **primer**: regime taxonomy, the
access-window primitive that is the game's central mechanic, the moderate-fidelity
propagator ladder (Kepler+J2 / SGP4 / Skyfield reference), the integer-microsecond clock
that makes replay deterministic, the penumbra-aware Sun/eclipse model that the recent
TT&C audit wired into the power tick, and the four UI surfaces that turn all of it into
operator-visible schedule. Per-fidelity-tier validation depth lives in
[`04a-propagator-fidelity.md`](04a-propagator-fidelity.md) and debris/conjunction depth
lives in [`04b-debris-and-conjunction.md`](04b-debris-and-conjunction.md) (both Tier 3
deliverables of the [corpus expansion](../FUTURE-WORK.md#125-tier-1--citation-backfill--methodology)).

---

## 1. Orbital regimes (sets which actions are even possible)

An **orbital regime** is the altitude-and-period band a satellite lives in. Regime is
the first thing the simulator's effect resolver checks against an order, because regime
gates **what the attacker can physically reach** — a ground-launched interceptor sized
for ballistic-missile-defense intercepts cannot reach the GNSS constellation no matter
how the operator plans the shot, and a co-orbital tug phases to wherever it wants but
takes weeks to get there. This subsection defines the five regimes the engine
recognizes ([`engine/orbit.py:classify_regime`](../../spacesim/engine/orbit.py)) and
the dominant missions that drive each regime's gameplay menu. Per-pass and per-window
math live in §2 below; this subsection is about **reachability**, the upstream
constraint.

The Secure World Foundation's 2025 *Global Counterspace Capabilities* report makes the
load-bearing observation that **regime is the dominant variable** in counterspace
reachability — kinetic, co-orbital, EW, DE, and cyber each fall off at different
altitudes, so a defender's regime choice is in effect a survivability choice
([SWF 2025 Global Counterspace](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)).
The engine's [`engine/engage.py:INTERCEPTORS`](../../spacesim/engine/engage.py)
encodes the kinetic side of this gating as a hard `max_alt_km` ceiling per interceptor
class.

| Regime | Altitude band | Period | Dominant missions | Counter-reachability note |
|---|---|---|---|---|
| **LEO** (Low Earth Orbit) | ~160–2,000 km ([NASA NSSDC *Earth Fact Sheet*](https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html); [ESA *Types of orbits*](https://www.esa.int/Enabling_Support/Space_Transportation/Types_of_orbits)) | ~88–127 min ([ESA *Types of orbits*](https://www.esa.int/Enabling_Support/Space_Transportation/Types_of_orbits)) | ISR (optical, SAR, SIGINT), weather, broadband megaconstellations, ISS / crewed | Reachable by **every** counterspace category; the canonical kinetic-test regime |
| **MEO** (Medium Earth Orbit) | ~2,000–35,786 km; GPS at ~20,200 km ([ESA *Types of orbits*](https://www.esa.int/Enabling_Support/Space_Transportation/Types_of_orbits)) | ~2–24 h; GPS ~11 h 58 min ([ESA *Types of orbits*](https://www.esa.int/Enabling_Support/Space_Transportation/Types_of_orbits); [AU *Space Primer*, Ch. 6](https://www.airuniversity.af.edu/Portals/10/AUPress/Books/AU-18.pdf)) | GNSS (GPS, Galileo, GLONASS, Beidou-MEO), some SDA | DA-ASAT reach **rare** at this altitude; EW (jam/spoof the user-side signal) and cyber dominate |
| **GEO** (Geostationary Earth Orbit) | 35,786 km altitude (42,164 km semi-major axis) ([NASA NSSDC *Earth Fact Sheet*](https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html); [ESA *Types of orbits*](https://www.esa.int/Enabling_Support/Space_Transportation/Types_of_orbits)) | 23 h 56 min 4 s (one sidereal day) ([NASA NSSDC *Earth Fact Sheet*](https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html); [ITU-R Recommendation S.484-3](https://www.itu.int/rec/R-REC-S.484/en)) | Strategic SATCOM, missile-warning (SBIRS-GEO), broadcast, some SIGINT | Effectively un-reachable kinetically; **EW, cyber, RPO, DE** are the live categories |
| **HEO / Molniya** | Eccentric (e ≈ 0.74), apogee ~39,800 km over high northern latitudes ([ESA *Types of orbits*](https://www.esa.int/Enabling_Support/Space_Transportation/Types_of_orbits)) | ~12 h (twice-per-day apogee dwell) ([ESA *Types of orbits*](https://www.esa.int/Enabling_Support/Space_Transportation/Types_of_orbits)) | Russian early-warning (Tundra/Oko legacy), polar SATCOM, high-lat ISR | Apogee dwell sits above kinetic reach; perigee dip exposes to BMD-class only briefly |
| **Cislunar** | Beyond GEO out to and past the Earth–Moon Lagrange points L1–L5 (~321,000–448,000 km from Earth) and the lunar Near-Rectilinear Halo Orbit (NRHO) ([NASA *Artemis Gateway*](https://www.nasa.gov/mission/gateway/); [NASA NSSDC *Moon Fact Sheet*](https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html)) | Days to weeks | Future SDA, Artemis Gateway NRHO (planned habitation by ~2028), deep-space relay | No fielded kinetic, EW, or DE reach; SDA + cyber/supply-chain only |

The engine's interceptor-class table directly mirrors the LEO band's internal structure:
[`engine/engage.py:INTERCEPTORS["bmd_adapted"]`](../../spacesim/engine/engage.py) caps at
**600 km** (the SM-3 / Aegis-adapted envelope around the Burnt Frost 2008-02-21
geometry), `mrbm_kkv` caps at **1,000 km** (the SC-19 / FY-1C 2007-01-11 envelope at
~865 km and the PDV Mk-II / Microsat-R 2019-03-27 envelope at ~283 km), and `abm_heavy`
caps at **2,000 km** (the Nudol PL-19 / Cosmos-1408 2021-11-15 envelope at ~480 km, with
booster reserve to the LEO ceiling). The `coorbital` class has `max_alt_km: None` — a
co-orbital interceptor or grappler phases to GEO or HEO over weeks rather than reaching
ballistically, which is exactly the SJ-21 / Beidou-2 G2 tug pattern that the engine's
`reversible_option` flag captures
([SWF 2025 Global Counterspace](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)).
The teaching point is that **a defender who parks high is safe from every fielded
kinetic capability** — and a defender who parks low gains a short pass time, persistent
ground-track variety, and rich ISR product at the cost of being inside every interceptor's
envelope.

The corollary that drives the simulator's COA pacing: a regime choice made at force
design (months before the vignette starts) sets which counterspace doctrines an opponent
even can field. Vignettes 4–6 (LEO ISR-DE, MEO PNT-EW, GEO RPO) are structured around
this single observation — each vignette presents the trainee with a target in a different
regime and forces them to discover that the *menu* changes, not the *intent*.

Used by: [`engine/orbit.py:classify_regime`](../../spacesim/engine/orbit.py) (the
LEO / LEO_SSO / MEO / GEO / HEO / CISLUNAR literal split); [`engine/engage.py:INTERCEPTORS`](../../spacesim/engine/engage.py) (the `max_alt_km` field per class — `bmd_adapted: 600`, `mrbm_kkv: 1000`, `abm_heavy: 2000`, `coorbital: None`).

### Sources

- *NASA NSSDC Earth Fact Sheet* — [live](https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html)
  · [snapshot](https://web.archive.org/web/2026*/https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html)
  · accessed 2026-06-12.
- *ESA, "Types of orbits"* — [live](https://www.esa.int/Enabling_Support/Space_Transportation/Types_of_orbits)
  · [snapshot](https://web.archive.org/web/2026*/https://www.esa.int/Enabling_Support/Space_Transportation/Types_of_orbits)
  · accessed 2026-06-12.
- *AU Space Primer* (Air University Press, AU-18) — [live](https://www.airuniversity.af.edu/Portals/10/AUPress/Books/AU-18.pdf)
  · [snapshot](https://web.archive.org/web/2024*/https://www.airuniversity.af.edu/Portals/10/AUPress/Books/AU-18.pdf)
  · accessed 2026-06-12.
- *ITU-R Recommendation S.484-3* (geostationary orbit station-keeping) — [live](https://www.itu.int/rec/R-REC-S.484/en)
  · [snapshot](https://web.archive.org/web/2024*/https://www.itu.int/rec/R-REC-S.484/en)
  · accessed 2026-06-12.
- *NASA, "Gateway" program page* (Artemis lunar-orbiting platform; NRHO) — [live](https://www.nasa.gov/mission/gateway/)
  · [snapshot](https://web.archive.org/web/2026*/https://www.nasa.gov/mission/gateway/)
  · accessed 2026-06-12.
- *NASA NSSDC Moon Fact Sheet* (Earth–Moon distance for cislunar bounds) — [live](https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html)
  · [snapshot](https://web.archive.org/web/2026*/https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html)
  · accessed 2026-06-12.
- *SWF 2025 Global Counterspace Capabilities Report* — [live](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · [snapshot](https://web.archive.org/web/2026*/https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · accessed 2026-06-12.

---

## 2. The access window — the central game mechanic

The simulator's single load-bearing primitive is the **access window**: a half-open interval `[t_start, t_end]` during which some asset A can perform some operation X against some target B because the geometry permits it. Outside the window the order does not execute — it queues, or it fails the validate step in [`engine/orders.py`](../../spacesim/engine/orders.py), or it sits unresolved until the next valid pass. The window is not a UI affordance; it is a **physical fact** derived from the actor's orbit, the target's orbit (or ground location), an elevation mask, a lighting predicate, and a range or closing-rate test. The canonical reference for the pass-geometry math the windows derive from is Vallado's [*Fundamentals of Astrodynamics and Applications*, 4th ed. (Microcosm Press)](https://microcosmpress.com/publishing/fundamentals-of-astrodynamics-and-applications-fourth-edition/) — the topocentric look-angle, ground-track, and rise-set treatments in Vallado §4.4 and §11 are what every operational pass-prediction tool descends from. The simulator builds windows by sampling a boolean access predicate on a sub-stepped clock then bisecting the edges to ~1 s precision (see [`engine/access.py:_find_windows`](../../spacesim/engine/access.py)), caching per `(actor, target, channel)` and invalidating on every maneuver.

The **access taxonomy is much larger than the engine encodes**. Many doctrinally- and physically-distinct permutations alias onto a small set of access predicates because the *gating* physics is shared even when the *resolved effect* differs: a ground-launched RF photon climbing through the same atmosphere on the same elevation slant is doing the same access check whether it carries a command, a jam waveform, or a spoofed PNT signal — what differs is the resolver branch, not the predicate. This subsection enumerates the full set of physically-distinct permutations grouped by platform (ground / sea / air / space), direction (transmit / receive), mode (passive / active), and target (space asset / ground asset / RF receiver / EO optic / bus structure / orbital track). §2.8 below maps each permutation to the engine's six gating channels (plus the relay-path `isl_link`) and names which permutations are aliased, which are out-of-scope-for-v1, and which sit on the FUTURE-WORK queue.

### 2.1 Communication links (TT&C + SATCOM data)

The "talk to the satellite" / "satellite talks to me" / "satellites talk to each other" axis. All three are **active** by definition (someone has to transmit) and gated by elevation-mask + slant-path link-budget physics characterized by [ITU-R Recommendation P.681](https://www.itu.int/rec/R-REC-P.681/en) (land/maritime mobile-satellite propagation) and [ITU-R Recommendation S.484-3](https://www.itu.int/rec/R-REC-S.484/en) (geostationary station-keeping geometry).

- **2.1.1 Uplink — ground TX → space RX.** Operator console at a TT&C ground station radiates an RF command at the satellite's receive antenna; or a SATCOM user terminal radiates at a transponder. Predicate: the satellite is above the ground site's `elevation_mask_deg` (5°–10° floor; rooftop / mountain-shadowed sites can be higher), atmospheric absorption budget closes at the chosen frequency, and the satellite's antenna pattern includes the ground site's azimuth. Operational examples on the TT&C side: the [AFSCN](https://www.afspc.af.mil/About-Us/Fact-Sheets/Display/Article/249018/air-force-satellite-control-network/) and [NASA Space Network](https://esc.gsfc.nasa.gov/space-communications/SN) ground-station catalogs; on the SATCOM-user side, every WGS / AEHF / Inmarsat / Iridium uplink ([USSF 53rd SOPS WGS fact sheet](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/3743145/53rd-space-operations-squadron/)). Engine: `command_uplink` literal; both TT&C operator uplinks and SATCOM user uplinks alias onto this single predicate because the gating physics is identical.

- **2.1.2 Downlink — space TX → ground RX.** Satellite radiates telemetry or mission data; ground site demodulates. Predicate: same horizon math as 2.1.1 (the engine reuses `_ground_sat_predicate` for both directions), with the downlink frequency's atmospheric and rain-fade budget closing at the elevation slant. Operational examples: TT&C telemetry from every operator's ground catalog; SATCOM mission-data delivery (Maxar Direct-to-Customer, [AWS Ground Station](https://aws.amazon.com/ground-station/) commercial relay). Engine: `telemetry_downlink` literal; user downlinks alias onto this predicate.

- **2.1.3 Crosslink / inter-satellite link (ISL) — space TX → space RX.** Two satellites communicate directly without a ground hop. Predicate: line-of-sight between the two satellites (no Earth-occlusion) plus optical pointing or RF antenna pattern coverage; closing rate slow enough for the modem lock-time. Operational examples: the Tranche 1 Transport Layer's optical ISL constellation ([SDA T1TL Block 1 program](https://www.sda.mil/transport/)), Starlink Gen-2 optical ISL ([SpaceX Starlink technical info](https://www.spacex.com/updates/)), Iridium NEXT's Ka-band ISL. Engine: `isl_link` literal — present as a non-gating relay-path channel, used by [`engine/orders.py`](../../spacesim/engine/orders.py) for stored-delivery routing.

### 2.2 Passive sensing

The "I detect, I don't transmit" axis. Passive sensing leaves no electromagnetic signature for the target to detect, which is exactly its operational appeal — but it inherits whatever lighting / emission geometry nature provides.

#### Optical (target reflects sunlight, observer reads visible / IR)

- **2.2.1 Ground optical → space target (passive ground-based SDA).** Telescope at a fixed site observes a satellite. Predicate: target above the sensor's `min_elevation_deg`, target **sunlit** (satellite is outside Earth's shadow at sim time `t`, per [`engine/sun.py:eclipse_fraction`](../../spacesim/engine/sun.py)), observer **dark** (Sun is below the local horizon by `twilight_deg = −6°`, the civil-twilight floor codified in the [USNO Astronomical Almanac](https://aa.usno.navy.mil/faq/sun_approx) Sun-position approximation), and clear-line-of-sight (sky-clear-of-cloud). Operational examples: USSF [GEODSS](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/2197691/ground-based-electro-optical-deep-space-surveillance/) (Ground-Based Electro-Optical Deep Space Surveillance), MIT Lincoln Lab AMOS at Maui, commercial networks like [ExoAnalytic](https://exoanalytic.com/). Engine: `sensor_observation` literal with `needs_lighting=True` on the sensor record.

- **2.2.2 Space optical → space target (passive space-based SDA).** Satellite observes another satellite optically. Same lighting predicate as 2.2.1 — target must be sunlit relative to the observer — but the observer is itself orbiting, so observer-dark depends on the observer's own eclipse state rather than the ground twilight floor. Operational examples: [GSSAP](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/2197772/geosynchronous-space-situational-awareness-program/) near the GEO belt, the Space Based Space Surveillance (SBSS) Block 10 satellite ([USSF SBSS fact sheet](https://www.afspc.af.mil/About-Us/Fact-Sheets/Display/Article/249024/space-based-space-surveillance-block-10/)). Engine: aliased to `sensor_observation` with the observer's own eclipse_fraction substituted for the ground twilight test.

- **2.2.3 Space optical → ground target (passive EO ISR imaging).** Satellite optical payload images the Earth. Predicate: target above the satellite's slant horizon (the satellite's `look_angle_deg` to the target, typically capped at ≤45° off-nadir per [Maxar tasking guide](https://developers.maxar.com/docs/tasking/guides/tasking-guide)), target sunlit at the target's local time, and cloud-free at the target. Operational examples: Maxar WorldView, [Planet Tasking API](https://developers.planet.com/docs/tasking/), [Capella SAR](https://support.capellaspace.com/what-are-capellas-tasking-parameters) for the closely-related SAR case (SAR is active RF, listed in §2.3.3). Engine: `sensor_observation` with a target-cloud-cover and target-sunlit predicate; the look-angle / off-nadir gate is implemented in [`engine/isr.py`](../../spacesim/engine/isr.py).

#### RF (target emits, observer reads — passive SIGINT)

- **2.2.4 Ground RF → space TX emitter (passive SIGINT of satellite downlinks).** Ground receiver listens to a satellite's downlink without transmitting. Predicate: satellite is above the ground site's `elevation_mask_deg` (same horizon physics as §2.1) and is actively transmitting on the receiver's tuned band. Operational examples: commercial signal-of-opportunity tracking such as [LeoLabs](https://leolabs.space/) RF interferometry against transponders, [Kratos](https://www.kratosdefense.com/products/space/satellite-communications) ground-station catalogs. Engine: aliased to `sensor_observation` with `needs_lighting=False` and an emit-frequency filter; passive-vs-active SIGINT is not currently distinguished as a separate channel.

- **2.2.5 Space RF → space TX emitter (passive SIGINT of satellite emissions in orbit).** A space-based SIGINT bird listens to another satellite's emissions in orbit (uplink, downlink, or crosslink RF leakage). Predicate: line-of-sight between the two satellites + the target is actively transmitting in the receiver's band. Operational examples: NRO Mercury / Mentor / Trumpet historical SIGINT GEO birds ([NRO Center for the Study of National Reconnaissance public releases](https://www.nro.gov/History/NRO-History/)), commercial [HawkEye 360](https://www.he360.com/) cluster geolocation. Engine: not currently modeled as a separate channel; would alias to `sensor_observation` with space-to-space geometry.

- **2.2.6 Space RF → ground TX emitter (the classical SIGINT bird).** Space-based receiver listens to a ground emitter — radar, comm, missile-telemetry RF — and geolocates it via Doppler / TDOA / FDOA across a cluster. Predicate: emitter is within the receiver's footprint (the satellite's antenna pattern projected to the surface) and is actively transmitting. The geolocation accuracy scales with √dwell × √N collectors, per the open-source TDOA/FDOA literature and the [`engine/sigint.py:geolocation_error_km`](../../spacesim/engine/sigint.py) model. Operational examples: HawkEye 360 commercial RF geolocation; military equivalents reported in [SWF 2025 Global Counterspace](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report) per-actor SIGINT chapters. Engine: aliased to `sensor_observation` with the space-to-ground footprint geometry of [`engine/isr.py:footprint_polygon`](../../spacesim/engine/isr.py).

#### Doppler / range-rate (target emits or reflects, observer measures carrier shift)

- **2.2.7 Ground passive Doppler → space target.** Ground receiver measures the Doppler shift on a satellite's downlink (or on a known reference signal scattered off the satellite) and derives range-rate. Predicate: same horizon math as §2.1; the satellite must be transmitting (or reflecting a known signal — sometimes a third-party broadcast such as terrestrial DTV is used as the illuminator). Operational examples: LeoLabs RF interferometry, NRL's research on passive Doppler against GNSS-illuminated targets, the long-standing radio-amateur Doppler-from-downlink approach documented by [AMSAT](https://www.amsat.org/). Engine: aliased to `sensor_observation` with a range-rate quantity flag; passive-Doppler-only SDA is not currently a distinct engine channel.

- **2.2.8 Space passive Doppler → space target.** Satellite measures Doppler shift on another satellite's downlink or reflection. Predicate: line-of-sight + target emission or reflective illumination. Engine: not currently modeled as a separate channel; future SDA work.

### 2.3 Active sensing

The "I transmit a probe and read the echo" axis. Active sensing reveals the sensor's location and intent (the emission is detectable), but it provides cooperative-target-quality range data and works against non-emitting targets that passive sensing cannot see.

#### Radar (RF probe → RF echo)

- **2.3.1 Ground radar → space target (active SSN radar).** Ground-based radar transmits, satellite reflects, ground reads the echo. Predicate: satellite above the radar's elevation mask, target inside the radar's range-velocity envelope (the largest fielded VHF/UHF arrays like [AN/FPS-85](https://www.afspc.af.mil/About-Us/Fact-Sheets/Article/249020/an-fps-85-phased-array-radar/) at Eglin track to GEO; [Cobra Dane](https://www.afspc.af.mil/About-Us/Fact-Sheets/Article/249033/cobra-dane/) at Shemya covers the Pacific catalog; [Globus II](https://celestrak.org/columns/v04n01/) at Vardø is the dedicated GEO custody radar). The 18th SDS catalog is curated from fused outputs across this network ([USSF 18 SDS fact sheet](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/3740012/18th-space-defense-squadron/)). Engine: aliased to `sensor_observation` with `needs_lighting=False` (radar works through cloud and night).

- **2.3.2 Space radar → space target (active space-based SDA).** Satellite carries a small radar and probes another satellite's range / velocity. Predicate: line-of-sight + emit/receive within the radar's range cell. Operational examples: limited fielding; the [Tranche 1 Tracking Layer](https://www.sda.mil/tracking/) and various proposed inspector-class satellites carry radar but the catalog of operational systems is small. Engine: not currently modeled.

- **2.3.3 Space radar → ground target (active SAR ISR imaging).** Satellite SAR illuminates a ground target and resolves an image from the chirp returns. Predicate: target inside the satellite's slant range-azimuth swath (off-nadir between the SAR's minimum and maximum incidence angles, typically ~20°–40° for [Capella](https://support.capellaspace.com/what-are-capellas-tasking-parameters)), squint inside the SAR's design envelope (±30° for Capella), satellite at the correct point in its track. Operational examples: Capella, ICEYE, Umbra commercial constellations; the legacy NRO Onyx / Lacrosse / Topaz lineage on the military side ([NRO Center for the Study of National Reconnaissance](https://www.nro.gov/History/NRO-History/)). Engine: `sensor_observation` with the SAR-specific beam-mode database in [`engine/isr.py:BEAM_MODES["isr_sar"]`](../../spacesim/engine/isr.py) (stripmap / spotlight / fine / wide_area / polarimetric); off-nadir gates the predicate.

#### Laser ranging (laser pulse → retroreflector echo)

- **2.3.4 Ground laser → space retroreflector (Satellite Laser Ranging).** Ground SLR station fires a short laser pulse at a satellite's corner-cube retroreflector, times the round-trip, derives sub-cm range. Predicate: satellite above the SLR site's elevation mask, satellite carries a retroreflector, observer dark (visible-spectrum laser; works at night and twilight), atmosphere transmissive. Operational examples: the [International Laser Ranging Service (ILRS)](https://ilrs.gsfc.nasa.gov/) coordinates ~40 ground stations against ~100 LRA-equipped satellites; NASA's [Goddard SLR](https://cddis.nasa.gov/Techniques/SLR/SLR_overview.html) is the canonical reference. Used for the most-precise OD for LAGEOS-class, GRACE-FO, and reference satellites. Engine: not currently modeled — sub-cm range precision is below the simulator's "moderate fidelity" envelope; would be a high-fidelity-tier addition.

- **2.3.5 Space laser → space target.** Satellite-mounted laser ranges a second satellite. Predicate: line-of-sight + target carries either a retroreflector or a cooperative laser-comm terminal. Operational examples: very limited fielding; future operational concepts include laser-ranging between elements of distributed constellations. Engine: not currently modeled.

### 2.4 EW / Jamming (offensive RF)

The "I transmit noise / false signal to deny / corrupt the receiver" axis. All entries are active and the predicate is the receiver's horizon to the transmitter (whether the receiver is on a satellite, on a ground site, or on a user handset). Doctrinal framing: [USSF Space Doctrine Publication 3-104, *Electromagnetic Spectrum Operations*, 19 September 2025](https://www.starcom.spaceforce.mil/Portals/2/SDP%203-104%20Electromagnetic%20Spectrum%20Operations%2019%20September%202025%20(2).pdf); per-system inventory: [SWF 2025 Global Counterspace](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report) and [CSIS Space Threat Assessment 2025](https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf).

#### Jamming

- **2.4.1 Uplink jamming — ground TX → space RX.** Ground jammer radiates noise into the satellite's receive band; the satellite's transponder cannot lock on the legitimate uplink. **Wide blast radius** — denies the entire user base served by that transponder, not just one ground site. Operational example: [USSF Counter Communications System Block 10.2 (CCS Block 10.2)](https://www.spaceforce.mil/News/Article/2113447/counter-communications-system-block-102-achieves-ioc-ready-for-the-warfighter/), declared IOC 9 March 2020 — explicitly the Space Force's "first offensive weapon system" and **uplink-only** by design. Russian equivalents in the [Tirada-2](https://www.kyivpost.com/post/26469) and Bylina program lines per [SWF 2025 Russia chapter](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report). Engine: `jam_footprint` literal with the ground jammer's horizon predicate; the engine's `jam.link_target` parameter (per [`docs/AUDIT-2026-06-COMMANDS.md` §N9](../AUDIT-2026-06-COMMANDS.md)) selects uplink-vs-downlink-vs-crosslink scope.

- **2.4.2 Downlink jamming (local) — ground TX → ground RX.** Ground jammer radiates into a user-receiver's band; the user can't hear the satellite. **Local effect** (a GPS-denied bubble over a city, a SATCOM-denied bubble over an operating area), but **wide deployment** (every user in the bubble is denied). The canonical large-scale fielding is the Russian [Pole-21](https://tass.com/defense/1088451) networked GNSS-jam node — dozens of nodes deployed on cellular masts form a regional GNSS-denial network, first observed in occupied Luhansk in early 2019 per [SWF 2025 Russia chapter](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report). Engine: `jam_footprint` with the user-bubble centered on the jammer site; the ground-to-ground geometry is the jammer's RF horizon to the user receiver (limited by terrain).

- **2.4.3 Crosslink jamming — ground or space TX → space RX (ISL band).** Jammer radiates into the band a constellation's ISL uses; ISL doesn't close. Predicate: jammer-to-victim-satellite horizon (ground case) or line-of-sight (space case). Engine: aliased to `jam_footprint` with the victim's ISL receive band as the target; current vignettes do not exercise this case.

- **2.4.4 Space-borne downlink jam — space TX → ground RX.** A satellite radiates into a user's downlink band. Predicate: user is inside the satellite's antenna footprint and the satellite is at the correct point in its orbit. Operational examples: theoretical / future; the only acknowledged operational systems are ground-based. Engine: not currently modeled as a separate channel; would alias to `jam_footprint` with a space-borne emitter.

- **2.4.5 Space-borne uplink jam — space TX → space RX.** One satellite jams another satellite's receiver. Predicate: line-of-sight + emit/receive band match. Engine: not currently modeled; future.

#### Spoofing (false signal, not noise)

- **2.4.6 GNSS spoofing (user-side) — ground TX → ground / mobile RX.** Ground spoofer broadcasts a false GNSS constellation; user receivers lock onto the false signal and report a corrupted PNT solution. Predicate: spoofer is within RF horizon of the user receiver (terrestrial line-of-sight). Operational examples: the 2024 GPS spoofing incidents in the Black Sea, eastern Mediterranean, and around Kaliningrad cataloged in [CSIS STA 2025](https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf). Engine: not currently a separate channel — the cyber `spoof` payload in [`engine/cyber.py:PAYLOADS`](../../spacesim/engine/cyber.py) covers the operational case at a higher abstraction level.

- **2.4.7 Command-link spoofing — ground TX → space RX.** Adversary radiates a forged uplink command into the satellite's receive band, attempting to issue legitimate-looking commands. Predicate: same horizon as 2.1.1 + the adversary possesses (or has compromised) the satellite's command-authentication scheme. Operational examples: cyber-adjacent. Engine: handled by [`engine/cyber.py`](../../spacesim/engine/cyber.py) with the `seize_c2` payload and the `rf` access vector — not a separate access window because cyber is the deliberate exception (§2 above).

### 2.5 Directed Energy (DEW)

The "I deposit photons or electrons into the target to damage it" axis. DEW differs from jamming in that the receiver doesn't need to be tuned to a specific band — the energy is deposited as heat, photoelectrons, or sensor saturation. Doctrinal framing and per-system inventory: [SWF 2025 Global Counterspace](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report); per-class historical analyst material: [Bart Hendrickx, "Peresvet"](https://www.thespacereview.com/article/3967/1) (The Space Review, 2021) and [Breaking Defense, "Don't be dazzled by Russia's laser weapons claims"](https://breakingdefense.com/2022/05/dont-be-dazzled-by-russias-laser-weapons-claims-experts/).

#### Counter-optical (laser dazzles / scars EO sensor focal-plane)

- **2.5.1 Ground laser → space EO sensor optics.** Ground laser is pointed at a passing ISR satellite's optical aperture; the focal-plane array is dazzled (temporarily blinded) or scarred (permanent damage). Predicate: target above the laser site's elevation mask, observer-dark not required (the laser punches through), atmosphere transmissive at the laser wavelength, target's optic is pointed at the laser (look-at geometry). Operational examples: Russian [Peresvet](https://www.thespacereview.com/article/3967/1) mobile laser (announced 1 March 2018, full service December 2019), Chinese ground-based laser facilities in Xinjiang per [SWF 2025 China chapter](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report). Engine: not currently a separate channel — DE effects use `sensor_observation` line-of-sight gating with a degraded-payload outcome resolved by [`engine/effects.py:Category="directed_energy"`](../../spacesim/engine/effects.py).

- **2.5.2 Space laser → space EO sensor.** Satellite-mounted laser is pointed at another satellite's optical aperture. Predicate: line-of-sight + target's optic look-at geometry. Operational examples: theoretical / future; no acknowledged fielded systems. Engine: not currently modeled; the future-work case is in [FUTURE-WORK.md §2](../FUTURE-WORK.md).

#### Counter-RF (high-power microwave damages RF receiver electronics)

- **2.5.3 Ground HPM → space bus RF front-end.** Ground HPM transmitter deposits high-power RF energy into the satellite's receive band; the LNA or downconverter is damaged. Predicate: target above the HPM site's elevation mask, RF energy density at the target above the bus's damage threshold. Operational examples: US [AFRL Counter-electronics High-Power Microwave Advanced Missile Project (CHAMP)](https://afresearchlab.com/) (the airborne variant), various ground-based research programs; SWF 2025 names no operationally-fielded ground-based counter-satellite HPM. Engine: not currently modeled as a separate channel.

- **2.5.4 Space HPM → space bus RF.** Satellite-mounted HPM damages another satellite's electronics. Predicate: line-of-sight + power-density-at-target. Engine: not currently modeled.

#### Counter-bus (laser delivers thermal / structural damage)

- **2.5.5 Ground high-power laser → space bus.** Beyond-Peresvet-class laser energy deposits thermal load directly into bus structure (solar arrays, radiators, MLI). Predicate: target above the laser site's elevation mask, atmosphere transmissive, sustained dwell time. Operational examples: theoretical / future; no acknowledged fielded operational systems at the power level required for structural damage. The Russian Sokol-Eshelon historical program and Chinese ground-based facilities per SWF 2025 are at the dazzle/degrade power level, not structural-damage. Engine: not currently modeled.

- **2.5.6 Space high-power laser → space bus.** Satellite-mounted laser delivers structural damage. Engine: not currently modeled.

### 2.6 Kinetic engagement

The "I deliver mass at high velocity to the target" axis. Per-system depth lives in [`03-counterspace-taxonomy.md` §3](03-counterspace-taxonomy.md) (DA-ASAT) and §4 (co-orbital).

- **2.6.1 Ground-launched DA-ASAT → space target.** Interceptor launches from a fixed ground site, climbs to the target's orbital track, hits at hypervelocity. Predicate: launch site has line-of-sight to the target above `interceptor_mask_deg` (10°) **and** the target altitude is below the interceptor class's `max_alt_km` ceiling (engine literal in [`engine/engage.py:INTERCEPTORS`](../../spacesim/engine/engage.py): `bmd_adapted: 600 km`, `mrbm_kkv: 1000 km`, `abm_heavy: 2000 km`). Operational examples: SC-19 / DN-3 (FY-1C, 11 January 2007), Nudol / PL-19 (Cosmos-1408, 15 November 2021), PDV Mk-II (Microsat-R, 27 March 2019). Engine: `weapon_engagement` literal.

- **2.6.2 Sea-launched DA-ASAT → space target.** Interceptor launches from a sea platform. Same predicate as 2.6.1, with the launch position floating. Canonical operational example: Operation Burnt Frost (USA-193, 21 February 2008), [SM-3](https://www.lockheedmartin.com/en-us/products/standard-missile-3-sm-3.html) fired from USS *Lake Erie* (CG-70). Engine: aliased to `weapon_engagement` with the launch site treated as a mobile ground site at the ship's position; the simulator does not currently route sea-launched interceptors through a maritime-position channel.

- **2.6.3 Air-launched DA-ASAT → space target.** Interceptor launches from an aircraft platform. Same predicate, with the launch position at altitude (which trades booster size for available reach). Historical example: the [F-15 / ASM-135 ASAT test on Solwind P78-1 (13 September 1985)](https://www.nro.gov/History/NRO-History/) — the only US ground/air-launched DA-ASAT to actually intercept a satellite before Burnt Frost. Modern theoretical concepts include air-launched smallsat-killer variants. Engine: not currently modeled; would alias to `weapon_engagement` with an air-mobile launch position.

- **2.6.4 Space-launched kinetic kill vehicle → space target (co-orbital intercept).** A co-orbital satellite releases a kinetic projectile (or itself impacts) at hypervelocity. Predicate: phasing into the target's orbital regime (over days-to-weeks) + close-approach geometry — gated by RPO custody, not endgame homing. Operational examples: Russian Burevestnik / Nivelir "nesting-doll" 2017–2020 sequence (Kosmos-2542 / 2543 / 2535) per [SWF Russian Co-orbital ASAT Testing Fact Sheet, June 2025](https://www.swfound.org/publications-and-reports/russian-co-orbital-anti-satellite-testing-fact-sheet); analyst attribution of the per-projectile claim rests on a small community (see [`03-counterspace-taxonomy.md` §4](03-counterspace-taxonomy.md)). Engine: `weapon_engagement` with the `coorbital` interceptor class (no `max_alt_km` ceiling) and the §2.7 RPO predicate gating phasing.

- **2.6.5 Space-launched projectile → ground target (Fractional Orbital Bombardment, FOBS).** A satellite-borne projectile is de-orbited onto a ground target. Predicate: the de-orbit burn window + ground-impact geometry. The Soviet 1968 FOBS deployment ([NRO history](https://www.nro.gov/History/NRO-History/)) and the 2021 Chinese FOBS test are widely-discussed in open-source analysis. **Treaty problem:** orbital deployment of WMD-class payloads is prohibited by [Outer Space Treaty Article IV](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/outerspacetreaty.html) per [`07-legal-norms-and-roe.md` §1](07-legal-norms-and-roe.md). Engine: not currently modeled and explicitly out-of-scope for v1.

### 2.7 RPO / co-orbital proximity (orbital, no transmission required)

- **2.7.1 Space → space close-approach.** Two satellites' relative range falls below an SDA "close-approach" threshold. **No transmission required** — the access predicate is pure orbital geometry. Predicate: relative range below `rpo_threshold_m` (engine default **50 km** — the standard SDA close-approach tripwire used in the [USSF GSSAP fact sheet](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/2197772/geosynchronous-space-situational-awareness-program/) and commercial-SDA tracking literature including [CSIS Aerospace *Unusual Behavior in GEO: Luch/Olymp-K*](https://aerospace.csis.org/data/unusual-behavior-in-geo-olymp-k/)), with closing rate modeled per Clohessy-Wiltshire treatment in Vallado §6. Operational examples: GSSAP inspection passes, Luch/Olymp-K co-locations (~5 km separations reported), SJ-21 / Beidou-2 G2 docked tug operation January 2022 ([SpaceNews](https://spacenews.com/chinas-shijian-21-spacecraft-docked-with-and-towed-a-dead-satellite/)). Engine: `rpo_proximity` literal.

### 2.8 How the engine collapses these onto six channels (plus the ISL relay)

The simulator's `engine/access.py` exposes **six gating channels** + one relay-path channel. The table below maps the ~25 distinct permutations enumerated in §2.1–§2.7 onto those seven engine literals. **"Aliased"** means the engine reuses the same predicate as another permutation — the resolver branch differs but the gating physics is identical. **"Out-of-scope"** means the permutation is doctrinally / physically real but not modeled in v1 (most are queued in [`FUTURE-WORK.md` §2](../FUTURE-WORK.md)).

| Engine literal | Implements directly | Aliases (same predicate, different resolved effect) | Out-of-scope (research-aware, not yet modeled) |
|---|---|---|---|
| `command_uplink` | 2.1.1 (TT&C uplink) | 2.1.1 (SATCOM user uplink), 2.4.7 (command-link spoofing) | — |
| `telemetry_downlink` | 2.1.2 (TT&C downlink) | 2.1.2 (SATCOM user downlink) | — |
| `sensor_observation` | 2.2.1 (ground optical → space), 2.2.3 (space optical → ground EO ISR), 2.3.1 (ground radar → space), 2.3.3 (space SAR → ground) | 2.2.2 (space optical → space), 2.2.4–2.2.6 (passive RF SIGINT, all three platform combinations), 2.2.7 (passive Doppler), 2.5.1 (DE counter-optical line-of-sight) | 2.2.8 (space passive Doppler), 2.3.2 (space radar → space), 2.3.4–2.3.5 (laser ranging), 2.5.2 (space DE → space optic) |
| `jam_footprint` | 2.4.1 (uplink jam), 2.4.2 (downlink jam, local) | 2.4.3 (crosslink jam from ground), 2.4.6 (GNSS spoof — partial: ground horizon to user) | 2.4.4 (space-borne downlink jam), 2.4.5 (space-borne uplink jam), 2.4.3 from space, 2.5.3–2.5.6 (counter-RF HPM and counter-bus laser) |
| `weapon_engagement` | 2.6.1 (ground DA-ASAT), 2.6.4 (co-orbital intercept) | 2.6.2 (sea-launched), 2.6.3 (air-launched) | 2.6.5 (FOBS — explicitly out for OST Art. IV reasons per [`07-legal-norms-and-roe.md` §1](07-legal-norms-and-roe.md)) |
| `rpo_proximity` | 2.7.1 (space-space close approach) | — | — |
| `isl_link` (relay, not gating) | 2.1.3 (ISL) | — | — |

The engine's collapsing rule is consistent: **wherever the gating physics is shared, the predicate is shared and the effect resolver branches on category** (the `Outcome` and `Category` literals in [`engine/effects.py`](../../spacesim/engine/effects.py), per [`03-counterspace-taxonomy.md` §1](03-counterspace-taxonomy.md)). This keeps the six-channel API stable while still allowing the resolver to discriminate between, say, an uplink command and an uplink jam at the same site against the same satellite — both pass the same `command_uplink` predicate, but the effect path (success → telemetry-delivery vs. success → ActiveEffect-with-deny-outcome) is different.

The out-of-scope entries above are not bugs; they are **deliberate v1 scope choices** that the FUTURE-WORK queue and the per-class research files ([`03a-da-asat-systems.md`](03a-da-asat-systems.md), [`03b-coorbital-rpo.md`](03b-coorbital-rpo.md), [`03c-ew-jamming.md`](03c-ew-jamming.md), [`03d-directed-energy.md`](03d-directed-energy.md)) will source per-channel when those Tier 3 deliverables land. The role of *this* file is to enumerate the full taxonomy so that any future channel addition can cite this section as the doctrinal-and-physical justification rather than re-deriving it.

### Closing pedagogical claim

Every channel is fed the same orbital state. In the operational case that state arrives as a **Two-Line Element set** (TLE), the NORAD GP-element-set format documented by [CelesTrak](https://celestrak.org/NORAD/documentation/tle-fmt.php); the simulator's TLE force-add path routes TLEs through Skyfield/SGP4 into the [`SGP4Propagator`](../../spacesim/engine/propagator.py) seam, and from there into every channel predicate above without modification. Fictional vignettes route the same `OrbitState` through the Kepler+J2 [`ModeratePropagator`](../../spacesim/engine/propagator.py). The choice of propagator is invisible to `access.py` — the channel predicates only see ECI position-velocity at a sim time.

The pedagogical claim that **"you can only act in a window"** is the simulator's most load-bearing teaching point, and it comes straight from doctrine. The USSF *Spacepower* capstone publication ([Space Capstone Publication, June 2020](https://media.defense.gov/2022/Jan/19/2002924102/-1/-1/0/DOCTRINE%20FACT%20SHEET%20-%20HIERARCHY%20AND%20NUMBERING.DOCX.PDF)) frames space operations as fundamentally **premeditated**: the operator plans the command, the tasking, the jam burst, the engagement *before* the window opens, then waits for geometry to enable execution. This is why [`engine/orders.py`](../../spacesim/engine/orders.py)'s `OrderSystem` is a *plan-then-execute* state machine — every action verb (downlink, jam, observe, engage, maneuver, command) carries a `via` endpoint and a planned execution time, the validate step checks that the relevant channel will have a window before that time, and the executor fires the handler only when `world.now` enters the window. The trainee discovers, vignette by vignette, that **fleet design and window timing are the same skill** — a force that can't reach its target in the next 90 minutes can't act in the next 90 minutes, full stop. The cyber exception (`access_vector` + `success_prob` + `persistence`, no window gate; see [`03-counterspace-taxonomy.md` §7](03-counterspace-taxonomy.md)) is doctrinally significant precisely because it is the one verb the trainee can fire *outside* a window — which is also why it carries the highest attribution-ambiguity and lowest reversibility-of-evidence cost in the engine's scoring.

Used by: [`engine/access.py`](../../spacesim/engine/access.py) (the six channel literals `COMMAND_UPLINK`, `TELEMETRY_DOWNLINK`, `SENSOR_OBSERVATION`, `JAM_FOOTPRINT`, `WEAPON_ENGAGEMENT`, `RPO_PROXIMITY`, plus the `ISL_LINK` relay-path channel); [`engine/orders.py`](../../spacesim/engine/orders.py) (the window-gated validate/execute state machine that every action verb except `cyber` traverses); [`engine/geometry.py`](../../spacesim/engine/geometry.py) (topocentric look-angle math — `look_angles`, `elevation_from_unit_dir` — that every ground-station predicate calls); [`engine/isr.py`](../../spacesim/engine/isr.py) (the per-payload-type beam-mode + footprint database that gates §2.2.3 and §2.3.3); [`engine/sigint.py`](../../spacesim/engine/sigint.py) (the geolocation-error model that scores §2.2.6); [`engine/engage.py:INTERCEPTORS`](../../spacesim/engine/engage.py) (the per-interceptor-class altitude ceiling that gates §2.6.1–§2.6.4).

### Sources

- *Vallado, Fundamentals of Astrodynamics and Applications, 4th ed.* (Microcosm Press) — [live](https://microcosmpress.com/publishing/fundamentals-of-astrodynamics-and-applications-fourth-edition/)
  · [snapshot](https://web.archive.org/web/2026*/https://microcosmpress.com/publishing/fundamentals-of-astrodynamics-and-applications-fourth-edition/)
  · accessed 2026-06-12.
- *ITU-R Recommendation P.681* (propagation data required for the design of Earth-space land mobile telecommunication systems) — [live](https://www.itu.int/rec/R-REC-P.681/en)
  · [snapshot](https://web.archive.org/web/2026*/https://www.itu.int/rec/R-REC-P.681/en)
  · accessed 2026-06-12.
- *ITU-R Recommendation S.484-3* (geostationary orbit station-keeping geometry) — [live](https://www.itu.int/rec/R-REC-S.484/en)
  · [snapshot](https://web.archive.org/web/2024*/https://www.itu.int/rec/R-REC-S.484/en)
  · accessed 2026-06-12.
- *USNO Astronomical Almanac, "Approximate Solar Coordinates"* — [live](https://aa.usno.navy.mil/faq/sun_approx)
  · [snapshot](https://web.archive.org/web/2026*/https://aa.usno.navy.mil/faq/sun_approx)
  · accessed 2026-06-12.
- *CelesTrak, "NORAD Two-Line Element Set Format"* — [live](https://celestrak.org/NORAD/documentation/tle-fmt.php)
  · [snapshot](https://web.archive.org/web/2026*/https://celestrak.org/NORAD/documentation/tle-fmt.php)
  · accessed 2026-06-12.
- *USSF Doctrine Hierarchy Fact Sheet* (Space Capstone Publication, June 2020) — [live](https://media.defense.gov/2022/Jan/19/2002924102/-1/-1/0/DOCTRINE%20FACT%20SHEET%20-%20HIERARCHY%20AND%20NUMBERING.DOCX.PDF)
  · [snapshot](https://web.archive.org/web/2024*/https://media.defense.gov/2022/Jan/19/2002924102/-1/-1/0/DOCTRINE%20FACT%20SHEET%20-%20HIERARCHY%20AND%20NUMBERING.DOCX.PDF)
  · accessed 2026-06-12.
- *Space Doctrine Publication 3-104, Electromagnetic Spectrum Operations* (STARCOM, 19 September 2025) — [live](https://www.starcom.spaceforce.mil/Portals/2/SDP%203-104%20Electromagnetic%20Spectrum%20Operations%2019%20September%202025%20(2).pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://www.starcom.spaceforce.mil/Portals/2/SDP%203-104%20Electromagnetic%20Spectrum%20Operations%2019%20September%202025%20(2).pdf)
  · accessed 2026-06-12.
- *USSF GSSAP fact sheet* (space-based optical SDA in the GEO belt) — [live](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/2197772/geosynchronous-space-situational-awareness-program/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/2197772/geosynchronous-space-situational-awareness-program/)
  · accessed 2026-06-12.
- *USSF GEODSS fact sheet* (Ground-Based Electro-Optical Deep Space Surveillance) — [live](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/2197691/ground-based-electro-optical-deep-space-surveillance/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/2197691/ground-based-electro-optical-deep-space-surveillance/)
  · accessed 2026-06-12.
- *USSF SBSS fact sheet* (Space Based Space Surveillance Block 10) — [live](https://www.afspc.af.mil/About-Us/Fact-Sheets/Display/Article/249024/space-based-space-surveillance-block-10/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.afspc.af.mil/About-Us/Fact-Sheets/Display/Article/249024/space-based-space-surveillance-block-10/)
  · accessed 2026-06-12.
- *USSF AN/FPS-85 fact sheet* (canonical ground SSN phased-array radar) — [live](https://www.afspc.af.mil/About-Us/Fact-Sheets/Article/249020/an-fps-85-phased-array-radar/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.afspc.af.mil/About-Us/Fact-Sheets/Article/249020/an-fps-85-phased-array-radar/)
  · accessed 2026-06-12.
- *USSF Cobra Dane fact sheet* — [live](https://www.afspc.af.mil/About-Us/Fact-Sheets/Article/249033/cobra-dane/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.afspc.af.mil/About-Us/Fact-Sheets/Article/249033/cobra-dane/)
  · accessed 2026-06-12.
- *USSF 18 SDS fact sheet* (catalog custodian) — [live](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/3740012/18th-space-defense-squadron/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/3740012/18th-space-defense-squadron/)
  · accessed 2026-06-12.
- *USSF 53rd Space Operations Squadron / WGS payload-management fact sheet* — [live](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/3743145/53rd-space-operations-squadron/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/3743145/53rd-space-operations-squadron/)
  · accessed 2026-06-12.
- *USSF Counter Communications System Block 10.2 IOC announcement* (9 March 2020 — uplink-only offensive RF jam) — [live](https://www.spaceforce.mil/News/Article/2113447/counter-communications-system-block-102-achieves-ioc-ready-for-the-warfighter/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.spaceforce.mil/News/Article/2113447/counter-communications-system-block-102-achieves-ioc-ready-for-the-warfighter/)
  · accessed 2026-06-12.
- *AFSCN fact sheet* (Air Force Satellite Control Network — ground-station catalog) — [live](https://www.afspc.af.mil/About-Us/Fact-Sheets/Display/Article/249018/air-force-satellite-control-network/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.afspc.af.mil/About-Us/Fact-Sheets/Display/Article/249018/air-force-satellite-control-network/)
  · accessed 2026-06-12.
- *NASA Space Network (TDRSS)* — [live](https://esc.gsfc.nasa.gov/space-communications/SN)
  · [snapshot](https://web.archive.org/web/2024*/https://esc.gsfc.nasa.gov/space-communications/SN)
  · accessed 2026-06-12.
- *AWS Ground Station* (commercial pay-per-minute ground-station relay) — [live](https://aws.amazon.com/ground-station/)
  · [snapshot](https://web.archive.org/web/2024*/https://aws.amazon.com/ground-station/)
  · accessed 2026-06-12.
- *SDA Tranche 1 Transport Layer* (optical-ISL operational constellation) — [live](https://www.sda.mil/transport/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.sda.mil/transport/)
  · accessed 2026-06-12.
- *International Laser Ranging Service (ILRS), NASA Goddard* — [live](https://ilrs.gsfc.nasa.gov/)
  · [snapshot](https://web.archive.org/web/2024*/https://ilrs.gsfc.nasa.gov/)
  · accessed 2026-06-12.
- *Maxar tasking guide* (commercial ISR tasking with off-nadir limits) — [live](https://developers.maxar.com/docs/tasking/guides/tasking-guide)
  · [snapshot](https://web.archive.org/web/2024*/https://developers.maxar.com/docs/tasking/guides/tasking-guide)
  · accessed 2026-06-12.
- *Planet Tasking API* — [live](https://developers.planet.com/docs/tasking/)
  · [snapshot](https://web.archive.org/web/2024*/https://developers.planet.com/docs/tasking/)
  · accessed 2026-06-12.
- *Capella SAR tasking parameters* — [live](https://support.capellaspace.com/what-are-capellas-tasking-parameters)
  · [snapshot](https://web.archive.org/web/2024*/https://support.capellaspace.com/what-are-capellas-tasking-parameters)
  · accessed 2026-06-12.
- *HawkEye 360* (commercial passive RF geolocation cluster) — [live](https://www.he360.com/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.he360.com/)
  · accessed 2026-06-12.
- *LeoLabs* (commercial radar + RF SDA) — [live](https://leolabs.space/)
  · [snapshot](https://web.archive.org/web/2024*/https://leolabs.space/)
  · accessed 2026-06-12.
- *SWF 2025 Global Counterspace Capabilities Report* (per-actor inventory of EW, DEW, kinetic, cyber systems) — [live](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · [snapshot](https://web.archive.org/web/2026*/https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · accessed 2026-06-12.
- *CSIS Space Threat Assessment 2025* (GNSS spoof incidents 2024, EW per-actor) — [live](https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://csis-website-prod.s3.amazonaws.com/s3fs-public/2025-04/250425_Swope_Space_Threat.pdf)
  · accessed 2026-06-12.
- *Bart Hendrickx, "Peresvet: a Russian mobile laser system to dazzle enemy satellites"* (The Space Review, 2021 — counter-EO DE per-system) — [live](https://www.thespacereview.com/article/3967/1)
  · [snapshot](https://web.archive.org/web/2024*/https://www.thespacereview.com/article/3967/1)
  · accessed 2026-06-12.
- *Breaking Defense, "Don't be dazzled by Russia's laser weapons claims: Experts"* (counter-analyst review of Peresvet capability) — [live](https://breakingdefense.com/2022/05/dont-be-dazzled-by-russias-laser-weapons-claims-experts/)
  · [snapshot](https://web.archive.org/web/2024*/https://breakingdefense.com/2022/05/dont-be-dazzled-by-russias-laser-weapons-claims-experts/)
  · accessed 2026-06-12.
- *TASS, "Latest jamming system arrives for electronic warfare troops"* (Pole-21 GNSS-denial deployment) — [live](https://tass.com/defense/1088451)
  · [snapshot](https://web.archive.org/web/2024*/https://tass.com/defense/1088451)
  · accessed 2026-06-12.
- *Kyiv Post, "Ukrainian Special Ops Report Destruction of Russian 'Tirada-2' Satcom Jamming System"* (May 2024) — [live](https://www.kyivpost.com/post/26469)
  · [snapshot](https://web.archive.org/web/2024*/https://www.kyivpost.com/post/26469)
  · accessed 2026-06-12.
- *SWF Russian Co-orbital Anti-satellite Testing Fact Sheet* (June 2025; Nivelir / Burevestnik per-projectile attribution) — [live](https://www.swfound.org/publications-and-reports/russian-co-orbital-anti-satellite-testing-fact-sheet)
  · [snapshot](https://web.archive.org/web/2025*/https://www.swfound.org/publications-and-reports/russian-co-orbital-anti-satellite-testing-fact-sheet)
  · accessed 2026-06-12.
- *CSIS Aerospace Security, "Unusual Behavior in GEO: Luch/Olymp-K"* — [live](https://aerospace.csis.org/data/unusual-behavior-in-geo-olymp-k/)
  · [snapshot](https://web.archive.org/web/2025*/https://aerospace.csis.org/data/unusual-behavior-in-geo-olymp-k/)
  · accessed 2026-06-12.
- *SpaceNews, "China's Shijian-21 spacecraft docked with and towed a dead satellite"* (27 January 2022 — co-orbital tug case) — [live](https://spacenews.com/chinas-shijian-21-spacecraft-docked-with-and-towed-a-dead-satellite/)
  · [snapshot](https://web.archive.org/web/2024*/https://spacenews.com/chinas-shijian-21-spacecraft-docked-with-and-towed-a-dead-satellite/)
  · accessed 2026-06-12.
- *UNOOSA Outer Space Treaty* (Article IV WMD-in-orbit prohibition that bears on §2.6.5 FOBS) — [live](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/outerspacetreaty.html)
  · [snapshot](https://web.archive.org/web/2024*/https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/outerspacetreaty.html)
  · accessed 2026-06-12.
- *Lockheed Martin SM-3 product page* (sea-launched DA-ASAT Burnt Frost variant) — [live](https://www.lockheedmartin.com/en-us/products/standard-missile-3-sm-3.html)
  · [snapshot](https://web.archive.org/web/2024*/https://www.lockheedmartin.com/en-us/products/standard-missile-3-sm-3.html)
  · accessed 2026-06-12.
- *NRO Center for the Study of National Reconnaissance public releases* (NRO program history including F-15 / ASM-135 ASAT test and FOBS history) — [live](https://www.nro.gov/History/NRO-History/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.nro.gov/History/NRO-History/)
  · accessed 2026-06-12.
- *AMSAT* (radio-amateur Doppler-from-downlink reference) — [live](https://www.amsat.org/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.amsat.org/)
  · accessed 2026-06-12.
- *Kratos satellite communications ground systems* (commercial ground-station catalog supporting passive SIGINT use case) — [live](https://www.kratosdefense.com/products/space/satellite-communications)
  · [snapshot](https://web.archive.org/web/2024*/https://www.kratosdefense.com/products/space/satellite-communications)
  · accessed 2026-06-12.
- *AFRL CHAMP airborne HPM program reference* — [live](https://afresearchlab.com/)
  · [snapshot](https://web.archive.org/web/2024*/https://afresearchlab.com/)
  · accessed 2026-06-12.
- *NASA SLR Goddard overview* (Satellite Laser Ranging Service) — [live](https://cddis.nasa.gov/Techniques/SLR/SLR_overview.html)
  · [snapshot](https://web.archive.org/web/2024*/https://cddis.nasa.gov/Techniques/SLR/SLR_overview.html)
  · accessed 2026-06-12.

---

## 3. Moderate-fidelity propagation model (Kepler+J2 / SGP4 / Skyfield reference)

Every channel predicate in §2 ends in the same question: *where is the satellite at sim
time `t`?* The simulator answers it through a **fidelity seam** — a single
[`Propagator` Protocol](../../spacesim/engine/propagator.py) whose three methods
(`state_at`, `apply_impulse`, `ground_track`) are the only contract `engine/access.py`,
`engine/orders.py`, and `engine/busmodel.py` ever see. The v1 implementation,
[`ModeratePropagator`](../../spacesim/engine/propagator.py), routes fictional vignette
satellites through analytic two-body + J2 secular drift and real-named TLE assets through
[sgp4](https://celestrak.org/publications/AIAA/2006-6753/AIAA-2006-6753-Rev3.pdf). A
[`HighFidelityPropagator`](../../spacesim/engine/propagator.py) stub already
declares the same Protocol so a numerical-integration replacement (RK4/RK78 with drag,
third-body, SRP) drops in later without touching any gameplay code. The deferred
[`04a-propagator-fidelity.md`](../../04a-propagator-fidelity.md) Tier-3 deep-dive carries
the per-tier accuracy table, the Skyfield-vs-engine residual study, and the
validation-methodology decisions; this subsection states only what v1 ships and why.

**Tier 1 — Kepler two-body + J2 secular (the `ModeratePropagator` fictional path).**
Fictional vignette satellites store six Keplerian elements `(a, e, i, Ω, ω, ν)` on
[`OrbitState`](../../spacesim/engine/orbit.py); `elements_to_rv()` solves Kepler's
equation each call and applies the standard secular rates of the right ascension of the
ascending node `Ω`, argument of perigee `ω`, and mean anomaly `M` from the
J2 disturbing potential, with `J2 = 1.08263 × 10⁻³` (the
[NIMA EGM-96 / WGS-84 zonal value](https://celestrak.org/publications/AIAA/2006-6753/AIAA-2006-6753-Rev3.pdf)
the SGP4 spec uses). This is the textbook formulation: the secular rates are
`Ω̇ = −¹⁵⁄₂ · n · J2 · (Rₑ/p)² · cos i`, `ω̇ = ¾ · n · J2 · (Rₑ/p)² · (5 cos²i − 1)`,
and the mean-anomaly correction `Ṁ = n + ½ · n · J2 · (Rₑ/p)² · √(1−e²)(3 cos²i − 1)`,
all per [Vallado, *Fundamentals of Astrodynamics and Applications*, 4th ed.](https://microcosmpress.com/publishing/fundamentals-of-astrodynamics-and-applications-fourth-edition/)
chapters 2 and 9, themselves derived from the Brouwer–Lyddane mean-element framework
([Brouwer 1959](https://ui.adsabs.harvard.edu/abs/1959AJ.....64..378B/abstract);
[Lyddane 1963](https://ui.adsabs.harvard.edu/abs/1963AJ.....68..555L/abstract)) that
operational propagators still descend from. The teaching value is that the trainee
sees regime-correct precession behaviour out of the box — sun-synchronous LEOs precess
their nodes at the canonical ~1°/day to track the Sun, GEO inclined orbits keep their
semi-major axis essentially fixed across a multi-day vignette, and ground tracks shift
westward by the expected ~22.5° per orbit at the 90-minute LEO period — without paying
the integration cost of a numerical model the v1 hardware tier (a single White-Cell
laptop running ~24 satellites) cannot afford.

**Tier 2 — SGP4 for TLE-derived assets (the `_tle_rv` path).** When the operator
force-adds a satellite by Two-Line Element set (the
[NORAD GP-element format](https://celestrak.org/NORAD/documentation/tle-fmt.php)
discussed in §2), `OrbitState.source == "tle"` and `ModeratePropagator.rv()` lazy-imports
[`sgp4.api.Satrec`](https://pypi.org/project/sgp4/) and calls the canonical model
described in [Hoots & Roehrich 1980, *Spacetrack Report #3*](https://celestrak.org/NORAD/documentation/spacetrk.pdf)
and revised in [Vallado, Crawford, Hujsak & Kelso 2006, "Revisiting Spacetrack Report
#3" (AIAA 2006-6753)](https://celestrak.org/publications/AIAA/2006-6753/AIAA-2006-6753-Rev3.pdf)
— the same library every operational SDA pass-prediction tool relies on. SGP4 / SDP4
ingest TLE elements as Brouwer mean elements (Kozai convention) and produce TEME
position-velocity; the engine treats TEME as ECI through the same GMST rotation it uses
for Keplerian assets (`_tle_rv` in `propagator.py` is explicit about this — TEME→ECEF
via GMST only, no polar motion or nutation). The simplification is conscious: a TLE's
own positional uncertainty is **~1 km at epoch growing to ~3 km/day** for typical LEO
([Vallado et al. 2006](https://celestrak.org/publications/AIAA/2006-6753/AIAA-2006-6753-Rev3.pdf)),
so the sub-arcsecond difference between TEME-as-ECI and a precise IAU 2000A
TEME→ICRF transformation is far below the input uncertainty for any PME training use.

**Tier 3 — Skyfield as the validation reference (test-only).** The engine itself
never imports [Skyfield](https://rhodesmill.org/skyfield/) — Brandon Rhodes' modern
ephemeris and pointing library that wraps the JPL DE-series ephemerides and the IAU
2000A precession/nutation model. Skyfield lives only in
[`spacesim/tests/test_reference_skyfield.py`](../../spacesim/tests/test_reference_skyfield.py),
which propagates the same canonical ISS TLE (the
[Vallado SGP4 verification vector for NORAD 25544](https://celestrak.org/publications/AIAA/2006-6753/AIAA-2006-6753-Rev3.pdf))
through both the engine's `ModeratePropagator` + topocentric `look_angles()` pipeline
and Skyfield's full `(EarthSatellite - site).at(t).altaz()` pipeline, then compares the
elevation angles at one-minute cadence over a three-hour pass window. The test asserts
the worst-case elevation residual stays below **1°** — the operational tolerance for "we
agree with the reference" — and skips cleanly if Skyfield's bundled timescale isn't
available offline. The same canonical-TLE residual is what the deferred
[`04a-propagator-fidelity.md`](../../04a-propagator-fidelity.md) per-tier accuracy table
will extend across longer windows (24 h, 7 d) and additional sites.

**Deferred to the high-fidelity tier.** Four perturbations exist as pure functions in
[`engine/perturbations.py`](../../spacesim/engine/perturbations.py) but are *not yet
composed* by `ModeratePropagator`: rotating-atmosphere drag (`drag_acceleration` +
`secular_drag_decay` for the exponential US Standard Atmosphere supplement profile,
falling to ~0 above 1000 km), the J3 (pear-shape) and J4 zonal terms with
`J3 = −2.5327 × 10⁻⁶` and `J4 = −1.6196 × 10⁻⁶`, Sun and Moon third-body point-mass
gravity (`third_body_acceleration` with `MU_SUN = 1.327 × 10²⁰` m³/s² and
`MU_MOON = 4.905 × 10¹²` m³/s²), and solar radiation pressure (`srp_acceleration`
gated by the cylindrical eclipse-fraction model in
[`engine/sun.py`](../../spacesim/engine/sun.py)). Each function is pinned to a
[Vallado §8 (perturbations)](https://microcosmpress.com/publishing/fundamentals-of-astrodynamics-and-applications-fourth-edition/)
worked example by `test_perturbations_*`, ready for the `HighFidelityPropagator`
stub to compose them additively into an RK4/RK78 integrator at the M8 milestone.
The v1 omission is doctrinally honest — drag at LEO altitudes drives ~0.5 km of decay
over a three-day vignette and SRP plus luni-solar perturbations dominate GEO
station-keeping budgets, but neither effect changes which **access window** opens during
a vignette's ≤72-hour playable horizon, which is what the engine asks the propagator for.

**Known accuracy envelope.** Against the Skyfield reference at the canonical ISS TLE
the engine holds **< 1° elevation residual across a 3-hour pass window**
([`test_reference_skyfield.py`](../../spacesim/tests/test_reference_skyfield.py)
asserts this as the v1 floor). Vallado et al. 2006 reports the SGP4 model itself
contributes ~1 km / day of positional growth at LEO and degrades faster for high-drag
regimes ([Vallado et al. 2006](https://celestrak.org/publications/AIAA/2006-6753/AIAA-2006-6753-Rev3.pdf)),
so a typical 24-hour propagation sits inside a few arc-minutes of elevation error from
a ground site — comfortably below the channel-predicate elevation masks (5° / 10°)
that gate every order verb in §2. The deferred [`04a-propagator-fidelity.md`](../../04a-propagator-fidelity.md)
deep-dive carries the per-regime residual study across 24-hour and 7-day windows,
the SGP4-vs-Skyfield drift across LEO/MEO/GEO/HEO test orbits, and the
fail-the-build numeric thresholds that promote a residual regression from "interesting"
to "blocking."

Used by: [`engine/propagator.py`](../../spacesim/engine/propagator.py)
(`ModeratePropagator`, `SGP4Propagator` via `_tle_rv`, the `Propagator` Protocol seam,
and the `HighFidelityPropagator` stub for M8);
[`engine/orbit.py`](../../spacesim/engine/orbit.py) (`OrbitState`, `elements_to_rv`
with the `_j2_rates` secular precession, `rv_to_elements` for post-impulse osculating
elements, `classify_regime`); [`engine/perturbations.py`](../../spacesim/engine/perturbations.py)
(the pure-function library — drag, J3/J4, third-body Sun/Moon, SRP — that the M8
high-fidelity composition consumes).

### Sources

- *Vallado, Fundamentals of Astrodynamics and Applications, 4th ed.* (Microcosm Press) — [live](https://microcosmpress.com/publishing/fundamentals-of-astrodynamics-and-applications-fourth-edition/)
  · [snapshot](https://web.archive.org/web/2026*/https://microcosmpress.com/publishing/fundamentals-of-astrodynamics-and-applications-fourth-edition/)
  · accessed 2026-06-12.
- *Brouwer, "Solution of the Problem of Artificial Satellite Theory Without Drag,"
  Astronomical Journal 64 (1959) 378* — [live](https://ui.adsabs.harvard.edu/abs/1959AJ.....64..378B/abstract)
  · [snapshot](https://web.archive.org/web/2025*/https://ui.adsabs.harvard.edu/abs/1959AJ.....64..378B/abstract)
  · accessed 2026-06-12.
- *Lyddane, "Small Eccentricities or Inclinations in the Brouwer Theory of the
  Artificial Satellite," Astronomical Journal 68 (1963) 555* — [live](https://ui.adsabs.harvard.edu/abs/1963AJ.....68..555L/abstract)
  · [snapshot](https://web.archive.org/web/2025*/https://ui.adsabs.harvard.edu/abs/1963AJ.....68..555L/abstract)
  · accessed 2026-06-12.
- *Hoots & Roehrich, Spacetrack Report #3, "Models for Propagation of NORAD Element
  Sets"* (Aerospace Defense Command, December 1980) — [live](https://celestrak.org/NORAD/documentation/spacetrk.pdf)
  · [snapshot](https://web.archive.org/web/2024*/https://celestrak.org/NORAD/documentation/spacetrk.pdf)
  · accessed 2026-06-12.
- *Vallado, Crawford, Hujsak & Kelso, "Revisiting Spacetrack Report #3"*, AIAA/AAS
  Astrodynamics Specialist Conference, AIAA 2006-6753 (Rev. 3) — [live](https://celestrak.org/publications/AIAA/2006-6753/AIAA-2006-6753-Rev3.pdf)
  · [snapshot](https://web.archive.org/web/2024*/https://celestrak.org/publications/AIAA/2006-6753/AIAA-2006-6753-Rev3.pdf)
  · accessed 2026-06-12.
- *Skyfield documentation* (Brandon Rhodes) — [live](https://rhodesmill.org/skyfield/)
  · [snapshot](https://web.archive.org/web/2026*/https://rhodesmill.org/skyfield/)
  · accessed 2026-06-12.
- *CelesTrak, "NORAD Two-Line Element Set Format"* — [live](https://celestrak.org/NORAD/documentation/tle-fmt.php)
  · [snapshot](https://web.archive.org/web/2026*/https://celestrak.org/NORAD/documentation/tle-fmt.php)
  · accessed 2026-06-12.
- *sgp4 (Python package)* — [live](https://pypi.org/project/sgp4/)
  · [snapshot](https://web.archive.org/web/2026*/https://pypi.org/project/sgp4/)
  · accessed 2026-06-12.

---

## 4. Time and the timeline (sim-UTC integer microseconds)

Once the simulator has decided how to propagate orbits (§3) and how to derive access
windows from orbital state (§2), it needs a single authoritative answer to "what time is
it?" — and that answer has to survive a save / rewind / replay round-trip
byte-for-byte. This subsection covers the time scales the simulator nominally tracks
(UTC, TAI, UT1, GPS), the integer-microsecond representation that makes replay
deterministic, the `SimClock` + `Scheduler` ordering invariant that prevents a
fast-forward from skipping a short LEO pass, and the boundary at which all of that
crosses into ISO-8601 strings.

Real-world space operations juggle four time scales. **UTC** (Coordinated Universal
Time) is the civilian standard the simulator displays everywhere; it is steered to stay
within **0.9 seconds** of Earth-rotation time UT1 by inserting **leap seconds** at the
end of June or December when needed, announced six months in advance via
[IERS Bulletin C](https://www.iers.org/SharedDocs/News/EN/BulletinC) and explained in
plain language by [NIST](https://www.nist.gov/pml/time-and-frequency-division/time-realization/leap-seconds).
**TAI** (International Atomic Time) is the underlying continuous atomic time scale; the
offset has been **TAI − UTC = 37 s exactly** since the last leap second was inserted at
the end of 2016, and no leap second has been added since
([USNO Earth Orientation, *Leap Second*](https://maia.usno.navy.mil/products/leap-second);
[IERS Conventions 2010, Technical Note 36](https://www.iers.org/IERS/EN/Publications/TechnicalNotes/tn36.html)).
**GPS time** is a third, also-continuous scale — no leap seconds — pegged to UTC at the
GPS epoch (1980-01-06) and currently running **18 seconds ahead of UTC**
([gps.gov, *Towards Continuous Universal Time*](https://www.gps.gov/sites/default/files/2025-06/CGSICMeetings_Coleman_Sept2024.pdf);
[USNO leap-second page](https://maia.usno.navy.mil/products/leap-second)). **UT1** is
Earth-rotation time itself, derived from VLBI observation; its offset from UTC,
**DUT1 = UT1 − UTC**, is published weekly in
[IERS Bulletin A](https://www.iers.org/SharedDocs/News/EN/BulletinC). The simulator
displays UTC and uses UTC internally; SGP4 / TLE epochs are also nominally UTC, so the
TAI/GPS distinction never crosses the engine boundary in v1. A high-fidelity propagator
swap (§3) would need to thread UT1 in for sidereal-time conversion at sub-second
precision, but the moderate-fidelity GMST approximation in
[`engine/geometry.py`](../../spacesim/engine/geometry.py) does not.

The simulator stores sim time as **integer microseconds since the Unix epoch**, never as
a float ([`engine/simtime.py`](../../spacesim/engine/simtime.py); the choice is recorded
in the [`memory.md` decision log, 2026-05-24](../../memory.md)). The reason is the
load-bearing replay invariant from `CLAUDE.md`: `(initial_state, ordered eventlog, seed)
→ byte-identical state`. Float seconds drift — `0.1 + 0.2 ≠ 0.3` — and a 600× fast-forward
that accumulates 10⁶ float increments will not bit-match a single advance to the same
target. Integer microseconds give exact arithmetic and exact ordering at a precision
(1 µs) that comfortably covers every operational deadline the engine cares about
(pass-edge bisection in [`engine/access.py`](../../spacesim/engine/access.py) caches to
~1 s; bus-tick scheduling to ~10 ms). The helpers
[`engine/simtime.py:from_iso` / `to_iso`](../../spacesim/engine/simtime.py) only ever
*transform* values the caller passes in — they never read the wall clock — so they
remain safe inside the deterministic core under the Phase-0 import guard.

The clock itself never advances in a free-running loop. The `SimClock` holds the single
authoritative `now`, and the `Scheduler` is a time-ordered priority queue
([`engine/clock.py`](../../spacesim/engine/clock.py)). Its key invariant is **sub-stepping**:
to advance to a target time `T`, the caller pops every event with `t <= T` in order and
fires its handler before updating `now`. The clock is never allowed to jump past a
scheduled event — without this, a 600× fast-forward over a 90-minute LEO horizon would
skip 5-second pass windows entirely, breaking access-window realism. Ordering ties are
broken deterministically by `(t, insertion_index)` — a monotonic counter incremented on
every `schedule()` — so two events at the same microsecond fire in the order they were
scheduled, regardless of payload contents. This is what makes the `EventLog`
([`engine/eventlog.py`](../../spacesim/engine/eventlog.py)) replay-stable: the
`(t, seq, tag)` key is total, the heap is order-deterministic, and no payload-level
comparison is ever required.

ISO-8601 strings appear **only at the serialization boundary**: vignette YAML files
parse a `start_epoch_utc:` field through `from_iso`, the AAR scrub bar renders `to_iso`
for display, telemetry endpoints emit ISO timestamps for the browser front end, and the
TLE force-add path parses TLE epochs into microseconds at ingest. Inside the engine
nothing is ever a string and nothing is ever a float. The convention is one-way at each
boundary — string in / int internal / string out — and it is the reason a save written
on one machine, reloaded on a second, and replayed on a third produces the same byte
sequence on all three.

Used by: [`engine/simtime.py`](../../spacesim/engine/simtime.py) (the integer-microsecond
convention + `from_iso` / `to_iso` boundary conversion);
[`engine/clock.py`](../../spacesim/engine/clock.py) (`SimClock` + `Scheduler` with the
sub-step invariant and `(t, insertion_index)` deterministic ordering);
[`engine/eventlog.py`](../../spacesim/engine/eventlog.py) (timestamped `EventLog` entries
keyed by `(t, seq, tag)` so replay is byte-identical).

### Sources

- *IERS Bulletin C* (leap-second announcements; six-month advance notice; UTC kept within 0.9 s of UT1) — [live](https://www.iers.org/SharedDocs/News/EN/BulletinC)
  · [snapshot](https://web.archive.org/web/2026*/https://www.iers.org/SharedDocs/News/EN/BulletinC)
  · accessed 2026-06-12.
- *NIST, "Leap Seconds"* (UTC/TAI/UT1 explainer; 0.9 s tolerance) — [live](https://www.nist.gov/pml/time-and-frequency-division/time-realization/leap-seconds)
  · [snapshot](https://web.archive.org/web/2026*/https://www.nist.gov/pml/time-and-frequency-division/time-realization/leap-seconds)
  · accessed 2026-06-12.
- *IERS Conventions (2010), Technical Note 36* (canonical TAI / UTC / UT1 conventions) — [live](https://www.iers.org/IERS/EN/Publications/TechnicalNotes/tn36.html)
  · [snapshot](https://web.archive.org/web/2026*/https://www.iers.org/IERS/EN/Publications/TechnicalNotes/tn36.html)
  · accessed 2026-06-12.
- *USNO Earth Orientation, "Leap Second"* (TAI − UTC = 37 s since 2017-01-01; GPS − UTC = 18 s) — [live](https://maia.usno.navy.mil/products/leap-second)
  · [snapshot](https://web.archive.org/web/2026*/https://maia.usno.navy.mil/products/leap-second)
  · accessed 2026-06-12.
- *gps.gov, "Towards Continuous Universal Time and the Future of the Leap Second"* (GPS time continuous; no leap seconds; 18 s offset from UTC) — [live](https://www.gps.gov/sites/default/files/2025-06/CGSICMeetings_Coleman_Sept2024.pdf)
  · [snapshot](https://web.archive.org/web/2026*/https://www.gps.gov/sites/default/files/2025-06/CGSICMeetings_Coleman_Sept2024.pdf)
  · accessed 2026-06-12.
- *Project decision log* (`memory.md`, 2026-05-24: sim time stored as integer microseconds since the Unix epoch so replay is byte-identical) — [local file](../../memory.md).

---

## 5. Eclipse and lighting (penumbra-aware)

Once §3 has answered *where* a satellite is and §4 has answered *when*, the bus model
needs a third upstream input: **is the satellite illuminated, and if so, how much?**
Every PV-array charge tick, every optical-sensor "target sunlit, site dark" predicate,
and every solar-radiation-pressure perturbation depends on a single scalar — the fraction
of the solar disk visible at sim time `t`. Getting that scalar wrong by even a binary
step costs the power model exactly the way the [TT&C audit](../AUDIT-2026-06-UI-TTC.md)
found in June 2026: an unsmoothed terminator crossing turned a recoverable ~21%
depth-of-discharge into a ~63% sawtooth that collapsed the per-orbit energy budget. The
forward link is the bus / payload power calibration in
[`06-bus-and-payload-operations.md`](../../06-bus-and-payload-operations.md) §1.6.4.

The geometry is the textbook cylindrical-shadow construction: project the satellite
position onto the Sun line, and the satellite is in eclipse iff (a) the projection is
anti-sunward and (b) the perpendicular distance from the anti-sun axis is less than
Earth's shadow radius at that distance behind Earth. Because the Sun is an extended
source with angular radius **~0.265°** as seen from Earth
([NASA Sun fact sheet](https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html);
angular diameter 0.5286°), the shadow is two nested cones: an **umbra** that narrows
behind Earth at half-angle `α_umb = atan((R_sun − R_earth)/AU)`, and a **penumbra** that
widens at `α_pen = atan((R_sun + R_earth)/AU)`. The standard derivation, including the
linear interpolation of lit fraction across the penumbral annulus, is
[Vallado, *Fundamentals of Astrodynamics and Applications*, 4th ed.](https://microcosmpress.com/publishing/fundamentals-of-astrodynamics-and-applications-fourth-edition/)
§5.3, paralleled by [Curtis, *Orbital Mechanics for Engineering Students*](https://shop.elsevier.com/books/orbital-mechanics-for-engineering-students/curtis/978-0-12-374778-5)
ch. 12 — the references the engine's cone constants are pinned to.

The Sun direction is analytic and **offline-capable** by design. [`engine/sun.py:sun_unit_eci`](../../spacesim/engine/sun.py)
implements the low-precision series from the [USNO *Approximate Solar Coordinates*](https://aa.usno.navy.mil/faq/sun_approx)
page: mean longitude `L = 280.460 + 0.9856474·d`, mean anomaly `g = 357.528 +
0.9856003·d` (degrees, with `d` in days since J2000.0), ecliptic longitude `λ = L +
1.915°·sin g + 0.020°·sin 2g`, and obliquity `ε = 23.439° − 4×10⁻⁷·d`. The series is
good to ~0.01° through 2050 — two orders of magnitude tighter than any lighting
predicate the engine evaluates — and critically requires **no JPL DE-series ephemeris
download**, satisfying the deterministic-core invariant in `CLAUDE.md` that forbids
network input inside `engine/`. The same trade-off [`engine/propagator.py`](../../spacesim/engine/propagator.py)
makes when it routes fictional satellites through analytic Kepler+J2 (§3).

Pre-audit, [`engine/busmodel.py:_sunlit`](../../spacesim/engine/busmodel.py) fed a
**binary** `is_sunlit` boolean into `advance_bus`: at terminator the EPS charge term
flipped instantly from `+charge_rate` to `−drain_rate`, producing a square-wave DoD
curve. The [TT&C audit (2026-06-12)](../AUDIT-2026-06-UI-TTC.md) §2 traced the
resulting 1.00→0.37 sawtooth — ~63% DoD per ~97-minute orbit, roughly 3–4× a real LEO
bus — to that step discontinuity layered on a mis-calibrated drain rate (`0.0003` SoC/s
in vignette YAML). The fix recalibrated drain to `0.0001` SoC/s across all ten vignettes
(gentle ~21% DoD baseline) and replaced the binary predicate: [`engine/sun.py:eclipse_fraction`](../../spacesim/engine/sun.py)
returns a value in `[0, 1]` — 1.0 outside the penumbra, 0.0 inside the umbra, linear
interpolation across the annulus — and [`engine/bus.py:advance_bus`](../../spacesim/engine/bus.py)
blends `charge·lit − drain·(1−lit)` per second, so terminator crossings ramp over the
seconds the penumbra subtends rather than stepping. `test_power_calibration.py` pins
baseline SoC ≥ 0.30 over multiple orbits; see
[`06-bus-and-payload-operations.md`](../../06-bus-and-payload-operations.md) §1.6.4 for
the recalibrated battery-DoD table.

Eclipse geometry then drives orbit-regime selection at the design level a vignette
author has to think about. A 600-km LEO sits in Earth's shadow for **~35 of every
~95 minutes** — roughly 36% eclipse fraction — and that ratio sizes the array-to-battery
ratio on every real LEO bus. The exception is the **dawn-dusk sun-synchronous orbit**
(LTAN near 06:00 / 18:00), whose plane lies close to the terminator and which therefore
spends **near-zero time in eclipse** for much of the year — the reason Landsat-style
mid-morning SSO designs (LTAN ≈ 10:00–10:30) accept a ~30–35% eclipse fraction in
exchange for consistent solar illumination geometry on the imaged surface
([NASA Landsat, *Geometry of a Sun-Synchronous Orbit*](https://landsat.gsfc.nasa.gov/article/geometry-of-a-sun-synchronous-orbit)).
The engine reproduces this automatically because J2 secular precession of the ascending
node (§3) plus the analytic Sun direction combine to walk the orbit plane through
whatever lighting profile its `(i, Ω, LTAN)` implies — a dawn-dusk SSO gets the
favourable power budget the real mission does, with no special-case code path.

Used by: [`engine/sun.py:sun_unit_eci`](../../spacesim/engine/sun.py) (the analytic
USNO low-precision Sun direction); [`engine/sun.py:eclipse_fraction`](../../spacesim/engine/sun.py)
(cylindrical umbra/penumbra fraction in `[0,1]`);
[`engine/busmodel.py:_sunlit`](../../spacesim/engine/busmodel.py) (the audit-fix call
site that replaced the binary `is_sunlit`); [`engine/bus.py:advance_bus`](../../spacesim/engine/bus.py)
(penumbra-aware power tick blending `charge·lit − drain·(1−lit)`);
[`engine/perturbations.py:srp_acceleration`](../../spacesim/engine/perturbations.py)
(solar-radiation-pressure gated by the same lit fraction for the M8 high-fidelity
propagator).

### Sources

- *Vallado, Fundamentals of Astrodynamics and Applications, 4th ed.* (Microcosm Press),
  §5.3 cylindrical eclipse with umbra/penumbra cones — [live](https://microcosmpress.com/publishing/fundamentals-of-astrodynamics-and-applications-fourth-edition/)
  · [snapshot](https://web.archive.org/web/2026*/https://microcosmpress.com/publishing/fundamentals-of-astrodynamics-and-applications-fourth-edition/)
  · accessed 2026-06-12.
- *Curtis, Orbital Mechanics for Engineering Students* (Elsevier), ch. 12 eclipse
  geometry — [live](https://shop.elsevier.com/books/orbital-mechanics-for-engineering-students/curtis/978-0-12-374778-5)
  · [snapshot](https://web.archive.org/web/2026*/https://shop.elsevier.com/books/orbital-mechanics-for-engineering-students/curtis/978-0-12-374778-5)
  · accessed 2026-06-12.
- *NASA NSSDC, "Sun Fact Sheet"* (angular diameter 0.5286° ⇒ half-angle ≈ 0.265°) — [live](https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html)
  · [snapshot](https://web.archive.org/web/2026*/https://nssdc.gsfc.nasa.gov/planetary/factsheet/sunfact.html)
  · accessed 2026-06-12.
- *USNO, "Approximate Solar Coordinates"* (low-precision analytic series; ~0.01°
  accuracy through 2050) — [live](https://aa.usno.navy.mil/faq/sun_approx)
  · [snapshot](https://web.archive.org/web/2026*/https://aa.usno.navy.mil/faq/sun_approx)
  · accessed 2026-06-12.
- *NASA Landsat, "Geometry of a Sun-Synchronous Orbit"* (LTAN noon-crossing vs.
  dawn-dusk eclipse-fraction trade-off) — [live](https://landsat.gsfc.nasa.gov/article/geometry-of-a-sun-synchronous-orbit)
  · [snapshot](https://web.archive.org/web/2026*/https://landsat.gsfc.nasa.gov/article/geometry-of-a-sun-synchronous-orbit)
  · accessed 2026-06-12.
- *Project audit* (`docs/AUDIT-2026-06-UI-TTC.md` §2: binary `is_sunlit` replaced by
  smooth `eclipse_fraction()` in `busmodel._sunlit`; charge/drain recalibrated) — [local file](../../AUDIT-2026-06-UI-TTC.md).

---

## 6. What the operator sees (turning physics into UX)

The previous five subsections were about physics. This one is about **what the
operator actually sees** of that physics — and the central claim is that the
operator never sees raw orbits. They see *windows*. The orbital regime classifier
in [`engine/orbit.py`](../../spacesim/engine/orbit.py), the propagator seam in
[`engine/propagator.py`](../../spacesim/engine/propagator.py), the integer-microsecond
clock in [`engine/simtime.py`](../../spacesim/engine/simtime.py), the J2 secular
rates, the Sun-direction analytic in [`engine/sun.py`](../../spacesim/engine/sun.py)
— all of it surfaces in the GUI as one of four things: a countdown, a coloured
bar, a Gantt rectangle, or a pre-disabled Issue button. This is by design, and the
v1 [operator-console specification](../build-spec/07-operator-console.md) (PSD
Part 4 §16) makes the principle explicit as its load-bearing UI principle P1:
*geometry is never hidden, but it is always presented as schedule, never as
ephemeris.*

Four UI surfaces carry the entire access-window layer. (a) The **fleet rail's
next-contact countdown**, in [`app.js`](../../spacesim/ui_web/static/app.js)'s
`renderFleet()`, paints a per-asset `M:SS` to the next valid `command_uplink`
window — amber under five minutes, red under one — sourced from
`GET /next_contacts/{cell}` which reuses the same `_find_windows` bisection that
gates orders. (b) The **pass-timeline ribbon** (`drawRibbon()`) renders a per-asset
six-hour horizon as three coloured lanes — `cmd` / `tlm` / `obs` — one block per
window from `GET /windows/{cell}/{asset}`; the "now" cursor sweeps left-to-right
as the server clock advances. (c) The **activity Gantt** (`renderActivity()` /
`drawActivityGantt()`) sits below the world view and lays out past, present, and
scheduled orders as solid / outlined / dashed bars across all three cells (White
sees all three; Red / Blue see only their own, server-side fog-filtered through
`SessionAPI`). (d) The **order compose form's `previewOrder()`** dry-runs the
composed action against `POST /order/validate` on every edit and pre-disables the
**Issue** button with the engine's own reason — `no_valid_window`,
`payload_unavailable`, `via_unknown` — so a trainee never clicks "Issue" on an
order that can't fire. The Gantt and ribbon were tuned for visual consistency in
the [June 2026 UI audit](../AUDIT-2026-06-UI-TTC.md) §3.

Time-advance is exposed as a small set of horizons rather than a free scrub.
White Cell drives **+1m / +10m / +1h** buttons that call `POST /step` and let the
server re-anchor its lazy clock; the client otherwise polls `/clock` at ~1.5 s so
every connected tab observes the same server-authoritative `now`. This is the
multiplayer trade noted at the top of [`CLAUDE.md`](../../CLAUDE.md): the
server-side `_record_catch_up_lag` watchdog in
[`session/manager.py`](../../spacesim/session/manager.py) raises a White-Cell
warning when the wall clock starts outrunning the sim, so a hardware-overloaded
session is surfaced as UX rather than hidden as drift. This mirrors the
operational-console pattern in commercial mission-operations systems
([L3Harris InControl product description](https://www.l3harris.com/all-capabilities/incontrol-satellite-command-and-control)
and [ESA SCOS-2000, Peccia 2003](https://gsaw.org/wp-content/uploads/2020/06/2003s02peccia.pdf)),
both of which surface a constellation overview as a pass-schedule + alarm-roll
view with drill-down into per-spacecraft telemetry, not as raw orbital state.

The pedagogical effect is the point. A trainee given a six-hour ribbon, a fleet
rail of countdowns, and an Issue button that refuses to light up *outside* a
window does not need to be lectured on access. They discover, vignette by
vignette, that *their force is constrained by geometry* — that a LEO ISR sat is
unreachable for the next 38 minutes whether they like it or not, that a GEO
SATCOM target sits in a continuous-access pocket, and that the only verb without
a window gate is the cyber one (deliberately, per §2 above and
[`03-counterspace-taxonomy.md` §7](../03-counterspace-taxonomy.md)). The
[USSF *Spacepower* capstone](https://media.defense.gov/2022/Jan/19/2002924102/-1/-1/0/DOCTRINE%20FACT%20SHEET%20-%20HIERARCHY%20AND%20NUMBERING.DOCX.PDF)
framing of space operations as *premeditated* is, in the GUI, just what the
countdown means: you cannot react, only plan.

Used by: [`ui_web/static/app.js`](../../spacesim/ui_web/static/app.js)
(`refresh`, `renderFleet`, `drawRibbon`, `renderActivity` / `drawActivityGantt`,
`previewOrder`, the `+1m / +10m / +1h` step handlers and the `/clock` poll loop);
[`engine/access.py`](../../spacesim/engine/access.py) (the window data — six
channel literals + `_find_windows` bisection — that every one of those UI
surfaces ultimately renders).

### Sources

- *USSF Doctrine Hierarchy Fact Sheet* (Space Capstone Publication, June 2020 — premeditated / plan-then-execute framing for space operations) — [live](https://media.defense.gov/2022/Jan/19/2002924102/-1/-1/0/DOCTRINE%20FACT%20SHEET%20-%20HIERARCHY%20AND%20NUMBERING.DOCX.PDF)
  · [snapshot](https://web.archive.org/web/2024*/https://media.defense.gov/2022/Jan/19/2002924102/-1/-1/0/DOCTRINE%20FACT%20SHEET%20-%20HIERARCHY%20AND%20NUMBERING.DOCX.PDF)
  · accessed 2026-06-12.
- *L3Harris InControl — Satellite Command and Control* (commercial mission-operations system product description; constellation overview + per-spacecraft drill-down + scheduled-pass UX pattern) — [live](https://www.l3harris.com/all-capabilities/incontrol-satellite-command-and-control)
  · [snapshot](https://web.archive.org/web/2026*/https://www.l3harris.com/all-capabilities/incontrol-satellite-command-and-control)
  · accessed 2026-06-12.
- *Peccia, "SCOS-2000 — ESA's Spacecraft Control for the 21st Century"* (Ground System Architectures Workshop 2003 — canonical reference for the ESA mission-control-system console pattern the methodology file's §7 already endorses) — [live](https://gsaw.org/wp-content/uploads/2020/06/2003s02peccia.pdf)
  · [snapshot](https://web.archive.org/web/2024*/https://gsaw.org/wp-content/uploads/2020/06/2003s02peccia.pdf)
  · accessed 2026-06-12.

---

## 7. Cross-references

- **Engine modules sourced by this file.** [`engine/orbit.py:classify_regime`](../../spacesim/engine/orbit.py) (§1), [`engine/access.py`](../../spacesim/engine/access.py) (§2 — the six channel literals), [`engine/propagator.py`](../../spacesim/engine/propagator.py) (§3 — the `Propagator` Protocol seam), [`engine/simtime.py`](../../spacesim/engine/simtime.py) + [`engine/clock.py`](../../spacesim/engine/clock.py) + [`engine/eventlog.py`](../../spacesim/engine/eventlog.py) (§4), [`engine/sun.py`](../../spacesim/engine/sun.py) + [`engine/busmodel.py`](../../spacesim/engine/busmodel.py) (§5 — the audit-introduced smooth `_sunlit`), [`ui_web/static/app.js`](../../spacesim/ui_web/static/app.js) (§6).
- **Forward-references to Tier 3 deep-dives.** Per-fidelity-tier accuracy and validation methodology in [`04a-propagator-fidelity.md`](04a-propagator-fidelity.md). Debris evolution and conjunction screening in [`04b-debris-and-conjunction.md`](04b-debris-and-conjunction.md). The Tier 3 files are deferred — both are queued in [`FUTURE-WORK.md` §12.5.3](../FUTURE-WORK.md#1253-tier-3--counterspace-systems-and-physics).
- **Sibling primer files.** [`03-counterspace-taxonomy.md`](03-counterspace-taxonomy.md) for the counterspace categories and the five D's; [`05-mission-types-and-counters.md`](05-mission-types-and-counters.md) for the per-mission counters that each regime hosts; [`06-bus-and-payload-operations.md`](06-bus-and-payload-operations.md) for the bus-level consumers of the §5 eclipse model and the §3 propagator output.
- **Audit predecessor.** [`docs/AUDIT-2026-06-UI-TTC.md`](../AUDIT-2026-06-UI-TTC.md) — the TT&C audit that introduced the smooth `eclipse_fraction` in `busmodel._sunlit` (§5) and the recalibrated battery DoD per orbit consumed by [`06-bus-and-payload-operations.md` §1.6.4](06-bus-and-payload-operations.md).
- **Research encyclopedia.** [`encyclopedia/R101-orbital-mechanics-for-operations.md`](encyclopedia/R101-orbital-mechanics-for-operations.md) — the implementation-focused counterpart that consumes this file's full derivations (already cited in the reverse direction); [`encyclopedia/R102-space-domain-awareness.md`](encyclopedia/R102-space-domain-awareness.md) for the SSA/SDA consumers of §3's propagator output.

*Last reviewed: 2026-06-12. Pending review: every 12 months from `last_reviewed`.*
