---
last_reviewed: 2026-06-12
primary_sources_consulted: 38
status: stable
---

# Satellite Mission Types & Their Counters

[← Research index](INDEX.md) · [↑ Docs index](../INDEX.md) · methodology: [`10-sources-and-methodology.md`](10-sources-and-methodology.md)

This file is the **asset catalogue** for the simulator. Each mission type becomes a
satellite template with a regime, a value to its owner, the terrestrial services it
provides, the menu of effects that can hold it at risk, and a forward-link to the
deeper per-mission Tier 2 deliverables (`05a-isr-eo-sar.md`, `05b-satcom-pnt.md`,
`05c-sda-and-orbital-warfare.md`) that drill into operator workflow, threshold values,
and engine-mapping detail. The effect definitions are sourced in
[`03-counterspace-taxonomy.md`](03-counterspace-taxonomy.md); the regime reachability
rules in [`04-orbital-mechanics-primer.md`](04-orbital-mechanics-primer.md); the bus
and payload-operations doctrine in [`06-bus-and-payload-operations.md`](06-bus-and-payload-operations.md).

## 1. How to read this — the row taxonomy

Each mission entry below carries five rows: **Does** (what the mission produces),
**Regime** (where the bird lives, dictating reachability), **Deny it →** (the
terrestrial effect of cutting the service — the doctrinal "why this matters"),
**Counters ranked by realism** (non-kinetic before kinetic, matching observed
real-world behaviour per the Secure World Foundation [*Global Counterspace
Capabilities Report*](https://swfound.org/counterspace/) and the CSIS Aerospace
Security [*Space Threat Assessment* series](https://aerospace.csis.org/space-threat-assessment-series/)),
and **Engine mapping** (the asset-template type, the payload-ops verbs in
[`engine/buscommands.py`](../../spacesim/engine/buscommands.py), the access channel
in [`engine/access.py`](../../spacesim/engine/access.py), and the forward-link to the
Tier 2 deep-dive). The ordering of counters tracks the [USSF *Space Capstone
Publication*](https://media.defense.gov/2020/Aug/10/2002476466/-1/-1/0/SPACE%20CAPSTONE%20PUBLICATION_10%20AUG%202020.PDF)
("Spacepower") doctrine of preferring reversible effects (deceive / disrupt / deny /
degrade) before destructive ones — the five D's grounded in
[`03-counterspace-taxonomy.md` §1](03-counterspace-taxonomy.md). The 2022 destructive
DA-ASAT moratorium ([UN General Assembly Resolution 77/41](https://digitallibrary.un.org/record/3997622)
+ [SWF DA-ASAT test tracker](https://swfound.org/media/207225/swf_anti-satellite_weapons_2024.pdf))
puts kinetic counters at the bottom of every list as a policy floor as well as a
realism one.

---

## 2. Per-mission summaries

### 2.1 ISR — Electro-Optical / Infrared (EO/IR)
- **Does:** captures visible-and-infrared imagery of terrestrial targets; supports
  collection-management workflows like NIIRS-scored target characterization, change
  detection, and BDA ([NRO public history of the KH-program](https://www.nro.gov/About-NRO/NRO-History/);
  [NGA / FAS NIIRS reference](https://irp.fas.org/imint/niirs.htm)).
- **Regime:** LEO, typically Sun-synchronous mid-morning LTAN (10:00–10:30 for the
  Landsat / WorldView design point); see [`04-orbital-mechanics-primer.md` §5](04-orbital-mechanics-primer.md).
- **Deny it →** the adversary loses eyes on your manoeuvre, opening windows to mass
  forces or reposition unobserved.
- **Counters (ranked):** (1) **directed-energy dazzle** during a pass — [SWF Global
  Counterspace](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf)
  catalogues laser dazzlers as the lowest-escalation reversible effect; (2)
  **downlink jam** to deny imagery delivery (validated by [Maxar Tasking docs](https://pro-docs.maxar.com/en-us/Tasking/Tasking_requests_EO.htm)
  on the downlink dependency); (3) **cyber** against ground-segment tasking or
  imagery-processing pipelines (cross-link [`03-counterspace-taxonomy.md` §7](03-counterspace-taxonomy.md));
  (4) **camouflage / concealment / deception** timed to known pass windows ([USSF
  Space Capstone Publication](https://media.defense.gov/2020/Aug/10/2002476466/-1/-1/0/SPACE%20CAPSTONE%20PUBLICATION_10%20AUG%202020.PDF)
  recognises CCD as a terrestrial counter to overhead ISR); (5) **co-orbital
  inspection / shadow** — pre-positioned to threaten the bird; (6) DA-ASAT, with
  high political cost from the [UNGA 77/41 moratorium](https://digitallibrary.un.org/record/3997622).
- **Engine mapping:** asset template `type: ISR_EO`; payload-ops verbs
  `isr.collect_now`, `isr.schedule_collection`, `isr.set_mode` in
  [`engine/buscommands.py:PAYLOAD_VERBS`](../../spacesim/engine/buscommands.py);
  beam-modes in [`engine/isr.py:BEAM_MODES`](../../spacesim/engine/isr.py); access
  channel `sensor_observation` in [`engine/access.py`](../../spacesim/engine/access.py).
  Tier-2 forward-link: [`05a-isr-eo-sar.md`](05a-isr-eo-sar.md).

### 2.2 ISR — Synthetic Aperture Radar (SAR)
- **Does:** all-weather, day/night imaging using active radar illumination ([Capella
  SAR 101 primer](https://www.capellaspace.com/resources/sar-101-an-introduction-to-synthetic-aperture-radar);
  [NASA Earthdata SAR primer](https://www.earthdata.nasa.gov/learn/earth-observation-data-basics/sar)).
- **Regime:** LEO; common modes include stripmap, sliding spotlight, spotlight ([Capella
  collect modes](https://support.capellaspace.com/what-are-capellas-collect-modes);
  [ESA Sentinel-1 acquisition modes](https://sentinel.esa.int/web/sentinel/user-guides/sentinel-1-sar/acquisition-modes)).
- **Deny it →** removes the adversary's bad-weather and night surveillance — the
  EO-counter trick of waiting for cloud cover breaks against SAR.
- **Counters (ranked):** (1) **SAR / radar jamming** of the return path or downlink
  ([SWF Global Counterspace](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf)
  documents Russian / Chinese radar EW capability against space-based SAR); (2)
  **cyber** against the SAR processing chain; (3) **corner-reflector deception** and
  decoys ([CSIS Space Threat Assessment 2024](https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf)
  on terrestrial deception against SAR); (4) co-orbital; (5) DA-ASAT.
- **Engine mapping:** asset template `type: ISR_SAR`; same `isr.*` verbs as EO but
  with SAR-specific beam-modes in [`engine/isr.py:BEAM_MODES`](../../spacesim/engine/isr.py);
  jam modulation against the SAR receive band in [`engine/jam.py`](../../spacesim/engine/jam.py).
  Tier-2 forward-link: [`05a-isr-eo-sar.md`](05a-isr-eo-sar.md).

### 2.3 SIGINT / ELINT
- **Does:** intercepts communications (COMINT) and emitter signatures (ELINT) from
  orbit; geolocates terrestrial transmitters via dual-satellite TDOA / FDOA ([IEEE
  *Dual-Satellite Geolocation Based on TDOA and FDOA*](https://ieeexplore.ieee.org/document/8042318);
  [NRO public SIGINT history](https://www.nro.gov/foia-home/foia-sigint-satellite-story/)).
- **Regime:** LEO for short-dwell collectors, GEO for long-dwell ([CSIS Aerospace
  Security space-based SIGINT context](https://aerospace.csis.org/aerospace101/national-security-space-organizations/)).
- **Deny it →** protects your own emissions; forces the adversary to switch to other
  intelligence disciplines.
- **Counters (ranked):** (1) **EMCON and deception** on the ground (the cheapest
  counter — silence is free); (2) **uplink jam** of the SIGINT receiver's collection
  band; (3) **cyber** against ground SIGINT processing; (4) **co-orbital shadowing**
  to deny target characterization; (5) DA-ASAT, especially hard against GEO.
- **Engine mapping:** asset template `type: SIGINT`; geolocation math in
  [`engine/sigint.py:geolocation_error_km`](../../spacesim/engine/sigint.py) (scales
  √dwell × √N collectors); access channel `sensor_observation`.
  Tier-2 forward-link: [`05a-isr-eo-sar.md`](05a-isr-eo-sar.md) (SIGINT shares the
  ISR collection workflow).

### 2.4 GNSS / PNT (Positioning, Navigation, Timing)
- **Does:** delivers position fixes, weapons guidance, network time-sync — the
  single-highest-leverage space service per Ukraine-conflict observations ([CSIS
  *Extending the Battlespace to Space*](https://www.csis.org/analysis/space-threat-assessment-2024);
  [GPS interface specifications IS-GPS-200K](https://www.gps.gov/technical/icwg/IS-GPS-200K.pdf)
  and [IS-GPS-705J](https://www.gps.gov/sites/default/files/2025-07/IS-GPS-705J.pdf)).
- **Regime:** MEO (~20,200 km for GPS / Galileo / GLONASS; ~22,200 km for BeiDou) —
  kinetically very hard to reach ([`04-orbital-mechanics-primer.md` §1](04-orbital-mechanics-primer.md)).
- **Deny it →** degrades precision weapons, drones, logistics, finance, and
  time-sync. Validated daily against Ukraine ([CSIS Space Threat Assessment 2024 on
  GPS jamming in the Ukraine theatre](https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf)).
- **Counters (ranked):** (1) **downlink jamming of users** creates a local
  GPS-denied bubble — the dominant real-world counter; (2) **spoofing** (false
  position / time fed to the user receiver); (3) **cyber** against ground monitoring
  / control segments; (4) DA-ASAT essentially impractical at MEO.
- **Defences (the bird's side):** **M-code** modernization with stronger anti-jam
  signal structure ([GAO-21-145 *GPS Modernization*](https://www.gao.gov/products/gao-21-145));
  **flex-power** capability allowing the bird to shift power into a regional anti-jam
  beam ([GPS Modernization Fact Sheet](https://www.gps.gov/sites/default/files/2025-07/2006-fact-sheet.pdf);
  Lockheed Martin GPS IIIF — [SpaceNews](https://spacenews.com/lockheed-martin-presses-case-that-gps-upgrade-will-counter-jamming-threats/)
  notes "approximately 20 dB more powerful than the whole Earth coverage beam");
  inertial backup; alternative PNT (eLORAN, magnetometer-aided).
- **Engine mapping:** asset template `type: PNT_GPS`; payload-ops verb
  `pnt.flex_power` in [`engine/buscommands.py:PAYLOAD_VERBS`](../../spacesim/engine/buscommands.py);
  jam against the user / downlink band in [`engine/jam.py`](../../spacesim/engine/jam.py).
  Tier-2 forward-link: [`05b-satcom-pnt.md`](05b-satcom-pnt.md).

### 2.5 SATCOM — Military & Commercial Communications
- **Does:** beyond-line-of-sight comms, data relay, drone control, broadcast — the
  C2 backbone for distributed forces. Modern flex SATCOM examples include the
  software-defined [Eutelsat Quantum](https://www.airbus.com/en/newsroom/press-releases/2021-07-eutelsat-quantum-the-worlds-first-fully-flexible-software-defined),
  the US wideband [WGS / MAJE upgrade](https://www.spaceforce.mil/News/Article/3812876/),
  and the US protected [AEHF + legacy Milstar constellations](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/2197758/advanced-extremely-high-frequency-system/).
- **Regime:** GEO (wideband and protected) and LEO (proliferated mega-constellations
  — Starlink, OneWeb, Project Kuiper).
- **Deny it →** cuts C2 and ISR backhaul; isolates forces. The canonical case is the
  [Viasat KA-SAT cyber-and-EW outage 24 Feb 2022](https://www.csis.org/analysis/cyberattack-viasats-ka-sat-network).
- **Counters (ranked):** (1) **uplink jam** denies the whole transponder; **downlink
  jam** denies local users; (2) **cyber against modems / ground / user-segment**
  (the Viasat KA-SAT model); (3) **co-orbital shadow or close-in jam** in GEO ([SWF
  Global Counterspace](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf)
  on Russian Olymp-K + Luch inspector RPO against commercial SATCOM); (4) DA-ASAT
  at GEO is extremely hard.
- **Defences (the bird's side):** **frequency hopping** ([IEEE Standards Association
  Hedy Lamarr piece](https://standards.ieee.org/beyond-standards/honoring-hedy-lamarr/)
  on the 1941 patent that founded the technique); **spot-beam nulling** (N-1 nulls
  per N receivers; [USPTO 12,537,566](https://patents.google.com/patent/US12537566B2/en));
  **proliferation** (a LEO mega-constellation is hard to kill at scale);
  **interference geolocation** ([USPTO 10,972,191 TDOA/FDOA](https://patents.google.com/patent/US10972191B2/en)).
- **Engine mapping:** asset template `type: SATCOM_GEO` / `SATCOM_LEO`; payload-ops
  verbs `satcom.mitigate_interference`, `satcom.shift_users`, `satcom.geolocate_interference`
  in [`engine/buscommands.py:PAYLOAD_VERBS`](../../spacesim/engine/buscommands.py);
  jam modulation against the receive band in [`engine/jam.py`](../../spacesim/engine/jam.py).
  Tier-2 forward-link: [`05b-satcom-pnt.md`](05b-satcom-pnt.md).

### 2.6 Missile Warning / Missile Tracking
- **Does:** detects launches via IR; tracks ballistic, hypersonic, and cruise-missile
  threats; cues defence systems. Anchor platforms: [USSF SBIRS](https://www.spaceforce.mil/About-Us/Fact-Sheets/Fact-Sheet-Display/Article/2197746/space-based-infrared-system/)
  (legacy GEO + HEO) and [Next-Gen OPIR](https://www.ssc.spaceforce.mil/Newsroom/Article-Display/Article/2744261/)
  (emerging GEO + Polar replacement designed for the hypersonic-threat envelope).
- **Regime:** GEO and HEO for legacy SBIRS / DSP; **proliferated LEO** for the
  emerging tracking layer (SDA's Tracking Layer / Hypersonic and Ballistic Tracking
  Space Sensor, HBTSS).
- **Deny it →** blinds strategic and theatre warning — highly escalatory to attack
  per the [USSF Space Capstone Publication](https://media.defense.gov/2020/Aug/10/2002476466/-1/-1/0/SPACE%20CAPSTONE%20PUBLICATION_10%20AUG%202020.PDF).
- **Counters (ranked):** (1) **IR sensor dazzle** during a pass — reversible, low
  escalation; (2) **uplink jam** of the tasking link; (3) **cyber** to corrupt or
  delay alert pipelines; (4) co-orbital interference; (5) DA-ASAT — extremely hard
  at GEO/HEO and strategically grave ([GAO-21-105249 *Missile Warning Satellites*](https://www.gao.gov/products/gao-21-105249)
  on the cost and architecture).
- **Defences (the bird's side):** the emerging **proliferated LEO Tracking Layer
  exists precisely to be hard to kill** — losing one bird out of dozens does not
  blind the network.
- **Engine mapping:** asset template `type: MW_SBIRS` / `type: MW_LEO_TRACKING`;
  payload-ops verb `mw.add_stare_area` in [`engine/buscommands.py:PAYLOAD_VERBS`](../../spacesim/engine/buscommands.py);
  IR-sensor dazzle modelled in [`engine/effects.py`](../../spacesim/engine/effects.py)
  + the DEW database in [`engine/cyber.py`](../../spacesim/engine/cyber.py).

### 2.7 Weather / Environmental Monitoring
- **Does:** meteorology and space-weather data for operational planning. Anchor
  platforms: [NOAA GOES-R series](https://www.goes-r.gov/users/abiScanModeInfo.html)
  (GEO weather, 10-minute flex-mode full-disk imagery), [NOAA JPSS](https://www.jpss.noaa.gov/mission_and_instruments.html)
  (polar weather, 14 orbits/day twice-daily global coverage), and the [USSF DMSP](https://www.spaceforce.mil/About-Us/Fact-Sheets/Article/2197779/defense-meteorological-satellite-program/)
  (101-min sun-synchronous 830-km mil-met, 3000-km swath OLS sensor).
- **Regime:** LEO (polar) and GEO.
- **Deny it →** degrades planning (less directly kinetic, often a "soft" target).
- **Counters (ranked):** downlink jam; cyber data corruption; dazzle (low priority
  given the policy-soft nature of the target); co-orbital; DA-ASAT (very rare —
  escalation cost outweighs the soft-target value).
- **Engine mapping:** asset template `type: WEATHER`; payload-ops verb
  `wx.request_sector` in [`engine/buscommands.py:PAYLOAD_VERBS`](../../spacesim/engine/buscommands.py).

### 2.8 Space Domain Awareness (space-based SDA / inspector sats)
- **Does:** observes *other satellites*; provides custody, characterization,
  pattern-of-life, and targeting data for counterspace effects. Anchor platforms:
  [USSF GSSAP (Geosynchronous Space Situational Awareness Program)](https://www.spaceforce.mil/About-Us/Fact-Sheets/Article/2197772/geosynchronous-space-situational-awareness-program/),
  declared IOC 29 September 2015 — the dedicated American inspector class — and
  Russian Luch / Olymp-K + Chinese SJ-17 / SJ-21 ([SWF Global Counterspace](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf);
  [CSIS Space Threat Assessment 2024](https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf)).
- **Regime:** GEO (the GSSAP / inspector class) and LEO (the proliferated tracker
  layer).
- **Deny it →** **suppression of adversary counterspace targeting** — blind the
  enemy's ability to find and target your satellites. A doctrinally explicit
  objective per the [USSF Space Capstone Publication](https://media.defense.gov/2020/Aug/10/2002476466/-1/-1/0/SPACE%20CAPSTONE%20PUBLICATION_10%20AUG%202020.PDF).
- **Counters (ranked):** (1) **dazzle its optics** during a characterization pass;
  (2) **co-orbital interference** (inspect the inspector); (3) cyber against ground
  SDA fusion (the USSF 18 SDS catalogue at [space-track.org](https://www.space-track.org/)
  + the [CCSDS 508.0-B-1 CDM standard](https://public.ccsds.org/Pubs/508x0b1e2c2.pdf)
  define the SDA data plane); (4) deny its ground-station downlink; (5) DA-ASAT.
- **Engine mapping:** asset template `type: SDA`; SDA mock catalogue + dispersion
  presets in [`engine/ssn.py`](../../spacesim/engine/ssn.py); access channel
  `sensor_observation` against other space objects in [`engine/access.py`](../../spacesim/engine/access.py).
  Tier-2 forward-link: [`05c-sda-and-orbital-warfare.md`](05c-sda-and-orbital-warfare.md).

### 2.9 On-Orbit Servicing / RPO / "Bodyguard" Satellites
- **Does:** refuels, inspects, repairs, or **escorts and defends** friendly birds —
  dual-use with co-orbital attack. Open-source RPO record: USSF GSSAP routine GEO
  inspection; Russian Kosmos-2542 / 2543 "synchronisation with USA 245" 25 Nov 2019
  ([CSIS Space Threat Assessment 2020](https://aerospace.csis.org/space-threat-assessment-2020/));
  Chinese SJ-21 January 2022 graveyard-orbit BeiDou-G2 tow demonstration ([SWF Global
  Counterspace 2026](https://www.swfound.org/publications-and-reports/2026-global-counterspace-capabilities-report)).
- **Regime:** GEO and LEO.
- **Role in sim:** both a *defensive* asset (escort, sensor-blocker) and an
  ambiguous *offensive* one — countering an escort may require out-manoeuvring it or
  suppressing its tasking link. The legal substrate sits in
  [`07-legal-norms-and-roe.md` §2 (LOAC in space)](07-legal-norms-and-roe.md).
- **Counters (ranked):** (1) **cyber** against the OOS/RPO tasking link; (2)
  out-manoeuvre (Δv-fight); (3) co-orbital counter-RPO; (4) jam the rendezvous
  sensors; (5) DA-ASAT (rare; high political cost).
- **Engine mapping:** asset template `type: RPO`; manoeuvre handlers in
  [`engine/maneuver.py`](../../spacesim/engine/maneuver.py); proximity access
  channel `rpo_proximity` in [`engine/access.py`](../../spacesim/engine/access.py);
  political-consequence dial in [`engine/effects.py:political_consequence`](../../spacesim/engine/effects.py).
  Tier-2 forward-link: [`05c-sda-and-orbital-warfare.md`](05c-sda-and-orbital-warfare.md).

---

## 3. Ground & link segment targets (often the easiest counters)

Satellites are expensive to attack in orbit; their **ground and link segments are
softer** ([CSIS *Cyberattack on Viasat's KA-SAT Network*](https://www.csis.org/analysis/cyberattack-viasats-ka-sat-network);
[USSF Space Capstone Publication](https://media.defense.gov/2020/Aug/10/2002476466/-1/-1/0/SPACE%20CAPSTONE%20PUBLICATION_10%20AUG%202020.PDF)
on "terrestrial strike" and "space link interdiction"). The simulator lets players
target these directly:

| Target | Effect of denying it | Counters cited |
|---|---|---|
| **Ground / TT&C station** | Owner loses command + data for *all* satellites using that station | terrestrial strike; cyber; jam the station's uplink ([USSF SCP](https://media.defense.gov/2020/Aug/10/2002476466/-1/-1/0/SPACE%20CAPSTONE%20PUBLICATION_10%20AUG%202020.PDF)) |
| **Mission data processing centre** | Data collected but unusable | cyber; terrestrial strike ([CSIS Viasat case](https://www.csis.org/analysis/cyberattack-viasats-ka-sat-network)) |
| **Launch site / integration facility** | Cannot reconstitute losses | terrestrial strike pre- or post-launch ([SWF Global Counterspace](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf) on the reconstitution-denial pattern) |
| **User terminals** (GPS receivers, VSATs) | Local denial without touching the satellite | downlink jam; spoof; cyber ([CSIS Ukraine GPS-jamming pattern](https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf)) |

**Design point.** Because cyber and ground-segment attacks are *not* gated by
orbital pass windows, they are the flexible, fast options — balanced by requiring a
modelled access vector ([`engine/cyber.py:VECTORS`](../../spacesim/engine/cyber.py))
and a strong defender cyber / physical posture
([`engine/cyber.py:effective_success`](../../spacesim/engine/cyber.py)).
Commercial-cloud ground-station services like [AWS Ground Station](https://aws.amazon.com/ground-station/)
and [Microsoft Azure Orbital](https://learn.microsoft.com/en-us/azure/orbital/overview)
add a new category of ground target the simulator should expose: a
commercial-cloud-hosted ground segment whose physical location and access controls
sit outside the asset owner's own security perimeter.

---

## 4. Effect × mission-type matrix

The matrix below summarises which counter-categories apply at meaningful
likelihood to each mission type. The full effect taxonomy with success-probability
math lives in [`03-counterspace-taxonomy.md` §2](03-counterspace-taxonomy.md);
this matrix is the index that maps mission-type to applicable counter rows.

| Mission | EW (jam/spoof) | DEW (dazzle) | Cyber | Co-orbital (RPO) | DA-ASAT |
|---|---|---|---|---|---|
| ISR EO/IR        | downlink jam: high | dazzle: high | high | medium | low (high cost) |
| ISR SAR          | radar / downlink jam: high | low (active-RF, not optical) | medium | medium | low |
| SIGINT           | uplink jam: medium | low | medium | medium | low |
| GNSS / PNT       | downlink jam: very high; spoof: very high | low | medium (ground) | impractical (MEO) | impractical (MEO) |
| SATCOM (GEO)     | uplink + downlink jam: very high | low | very high (Viasat) | medium (Luch) | low |
| SATCOM (LEO meg) | downlink jam: medium per-user | low | medium per-bird | low | impractical at scale |
| Missile warning  | uplink jam: medium | dazzle: medium | medium | low | very low (high cost) |
| Weather          | downlink jam: medium | low | medium | low | very low |
| SDA / inspector  | low | dazzle: high | medium | high (counter-RPO) | low |
| OOS / RPO        | jam tasking: medium | low | medium | counter-RPO: high | low |

The likelihood scoring follows [SWF *Global Counterspace Capabilities*](https://swfound.org/media/207662/global_counterspace_capabilities_2024.pdf)
+ [CSIS *Space Threat Assessment 2024*](https://aerospace.csis.org/wp-content/uploads/2024/04/240417_Swope_SpaceThreatAssessment_2024.pdf)
+ [GAO-23-106042 on commercial-imagery contracts](https://www.gao.gov/products/gao-23-106042)
on the per-platform threat surface.

---

## 5. Turning this into asset templates

Each entry above becomes a YAML template the engine loads (canonical schema in
[`04-data-model.md`](../design/04-data-model.md)):

```yaml
asset_template:
  type: ISR_EO
  regime: LEO_SSO
  owner_value: high                # how much losing it hurts the owner's score
  provides: [imagery]              # terrestrial services enabled
  ground_segment: [station_refs, processing_center_ref]
  vulnerabilities:                 # ordered, realism-weighted (matches §4 matrix)
    - {effect: directed_energy_dazzle, likelihood: high}
    - {effect: ew_downlink_jam,        likelihood: high}
    - {effect: cyber_corrupt,          likelihood: med}
    - {effect: co_orbital_inspect,     likelihood: med}
    - {effect: da_asat,                likelihood: low, escalation: high}
  defenses_available: [maneuver, deception, hardening, downlink_encryption]
```

Asset-template loading is driven by [`engine/buscommands.py:_PAYLOAD_TYPES_FOR`](../../spacesim/engine/buscommands.py)
(the per-payload-type verb-gating dict); per-domain physics + databases live in
[`engine/isr.py`](../../spacesim/engine/isr.py), [`engine/sigint.py`](../../spacesim/engine/sigint.py),
[`engine/jam.py`](../../spacesim/engine/jam.py), [`engine/cyber.py`](../../spacesim/engine/cyber.py),
[`engine/engage.py`](../../spacesim/engine/engage.py).

---

## 6. Cross-references

- **Spine file.** Effect categories + the five D's + per-effect success-probability
  math live in [`03-counterspace-taxonomy.md`](03-counterspace-taxonomy.md).
- **Regime reachability.** Which counters can physically reach which orbits is
  sourced in [`04-orbital-mechanics-primer.md` §1](04-orbital-mechanics-primer.md)
  (regimes) and [`04-orbital-mechanics-primer.md` §2](04-orbital-mechanics-primer.md)
  (access taxonomy).
- **Operator workflow per mission.** Pre-pass / in-pass / post-pass loop + payload
  verb catalogue + recovery chain are in [`06-bus-and-payload-operations.md`](06-bus-and-payload-operations.md).
- **Legal substrate.** ROE design pattern + the 2022 DA-ASAT moratorium that
  bottoms every counter list lives in [`07-legal-norms-and-roe.md`](07-legal-norms-and-roe.md).
- **Tier 2 per-mission deep-dives (deferred).** [`05a-isr-eo-sar.md`](05a-isr-eo-sar.md)
  for ISR / SIGINT, [`05b-satcom-pnt.md`](05b-satcom-pnt.md) for SATCOM / PNT,
  [`05c-sda-and-orbital-warfare.md`](05c-sda-and-orbital-warfare.md) for SDA / RPO.
  Queued in [`FUTURE-WORK.md` §12.5.2](../FUTURE-WORK.md#1252-tier-2--per-mission-and-per-actor-deep-dives).
- **Engine modules sourced by this file.** [`engine/buscommands.py`](../../spacesim/engine/buscommands.py)
  (payload-ops verb catalogue + `_PAYLOAD_TYPES_FOR` gating); [`engine/isr.py:BEAM_MODES`](../../spacesim/engine/isr.py)
  (per-mission beam-mode db); [`engine/sigint.py:geolocation_error_km`](../../spacesim/engine/sigint.py)
  (TDOA/FDOA error model); [`engine/jam.py`](../../spacesim/engine/jam.py) (jam modulation db);
  [`engine/cyber.py:VECTORS`](../../spacesim/engine/cyber.py) (cyber access-vector db);
  [`engine/engage.py:INTERCEPTORS`](../../spacesim/engine/engage.py) (DA-ASAT reach table);
  [`engine/ssn.py`](../../spacesim/engine/ssn.py) (SDA mock catalogue);
  [`engine/maneuver.py`](../../spacesim/engine/maneuver.py) (RPO Δv-fight handlers);
  [`engine/access.py`](../../spacesim/engine/access.py) (the access channels every counter routes through).
- **Research encyclopedia.** [`encyclopedia/R104-collection-management.md`](encyclopedia/R104-collection-management.md) and [`encyclopedia/R109-sensor-operations.md`](encyclopedia/R109-sensor-operations.md) (the implementation-focused counterparts to §2's ISR/SIGINT/SDA mission entries); [`encyclopedia/R102-space-domain-awareness.md`](encyclopedia/R102-space-domain-awareness.md) (§2.8's SDA mission entry); [`encyclopedia/R110-communications.md`](encyclopedia/R110-communications.md) (§2.4/§2.5's PNT/SATCOM link-denial counters).

*Last reviewed: 2026-06-12. Pending review: every 12 months from `last_reviewed`.*
