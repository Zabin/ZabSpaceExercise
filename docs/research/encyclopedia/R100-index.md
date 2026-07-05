# Tier R100 — Space Operations Foundation

[↑ Encyclopedia index](INDEX.md)

The simulator's direct subject matter: orbital mechanics, SDA, C2, custody, ground/constellation/
sensor operations. Coverage check method: every named engine subsystem in `CLAUDE.md`'s "Code map"
should have at least one topic here an implementer extending it would read first (MSTR-007 §7).

| ID | Title | Scope (one line) | Depends on | Status |
|---|---|---|---|---|
| [R101](R101-orbital-mechanics-for-operations.md) | Orbital Mechanics for Operations and Implementation | Implementation-focused orbital mechanics; points to [`research/04-orbital-mechanics-primer.md`](../04-orbital-mechanics-primer.md) for derivations. | — | ✅ Done |
| [R102](R102-space-domain-awareness.md) | Space Domain Awareness | SDA as a discipline: detection, tracking, characterization, attribution. | [R101](R101-orbital-mechanics-for-operations.md) | ✅ Done |
| [R103](R103-satellite-command-and-control.md) | Satellite Command and Control | The C2 chain: uplink, command validation, execution windows. | [R101](R101-orbital-mechanics-for-operations.md) | ✅ Done |
| [R104](R104-collection-management.md) | Collection Management | Sensor tasking, contention, prioritization across competing demands. | [R102](R102-space-domain-awareness.md), [R109](R109-sensor-operations.md) | ✅ Done |
| [R105](R105-custody-theory.md) | Custody Theory | What custody means, confidence decay, the weapons-quality gate. | [R102](R102-space-domain-awareness.md) | ✅ Done |
| [R106](R106-mission-operations.md) | Mission Operations | The operator's day-to-day workflow: plan, task, execute, assess. | [R103](R103-satellite-command-and-control.md) | ✅ Done |
| [R107](R107-ground-segment-operations.md) | Ground Segment Operations | Ground stations, contact scheduling, downlink/uplink constraints. | [R101](R101-orbital-mechanics-for-operations.md), [R103](R103-satellite-command-and-control.md) | ✅ Done |
| [R108](R108-constellation-operations.md) | Constellation Operations | Multi-satellite coordination, the ≤3-sat operated-individually guideline. | [R106](R106-mission-operations.md) | ✅ Done |
| [R109](R109-sensor-operations.md) | Sensor Operations | EO/SAR/SDA sensor modalities, beam modes, footprint geometry. | [R101](R101-orbital-mechanics-for-operations.md) | ✅ Done |
| [R110](R110-communications.md) | Communications | Uplink/downlink/ISL, jamming/interference, link denial. | [R101](R101-orbital-mechanics-for-operations.md) | ✅ Done |
| [R111](R111-power-and-thermal-operations.md) | Power and Thermal Systems Operations | EPS/battery/eclipse cycling, thermal state — the bus SOH model. | [R103](R103-satellite-command-and-control.md) | ✅ Done |
| [R112](R112-propulsion-and-maneuver-planning.md) | Propulsion and Maneuver Planning | Δv economy, the six maneuver entry modes, Hohmann/plane-change. | [R101](R101-orbital-mechanics-for-operations.md) | ✅ Done |
| [R113](R113-attitude-determination-and-control.md) | Attitude Determination and Control | ADCS modes, pointing constraints, their operational consequences. | [R103](R103-satellite-command-and-control.md) | ✅ Done |
| [R114](R114-command-and-data-handling.md) | Command and Data Handling | Onboard storage, dump/playback, the CDH subsystem model. | [R103](R103-satellite-command-and-control.md) | ✅ Done |
| [R115](R115-electronic-warfare-in-space-operations.md) | Electronic Warfare in Space Operations | Jamming taxonomy (barrage/spot/sweep/deceptive), effective radius/success. | [R110](R110-communications.md) | ✅ Done |
| [R116](R116-cyber-operations-against-space-systems.md) | Cyber Operations Against Space Systems | The cyber exception, vectors × payloads, attribution, persistence/patchability. | [R103](R103-satellite-command-and-control.md) | ✅ Done |
| [R117](R117-directed-energy-and-kinetic-effects.md) | Directed Energy and Kinetic Effects | Engagement geometry, salvo Pₖ, debris-cone consequences. | [R105](R105-custody-theory.md) | ✅ Done |
| [R118](R118-space-surveillance-networks.md) | Space Surveillance Networks | SSN dispersion presets, hybrid turnaround, coalition vs. national affiliation. | [R102](R102-space-domain-awareness.md) | ✅ Done |
| [R119](R119-space-situational-data-fusion.md) | Space Situational Data Fusion | Combining multiple sensor/SSN inputs into a single custody picture. | [R105](R105-custody-theory.md), [R118](R118-space-surveillance-networks.md) | ✅ Done |
| [R120](R120-access-window-and-geometry-planning.md) | Access Window and Geometry Planning | The six access channels, window caching, sub-stepped scheduling. | [R101](R101-orbital-mechanics-for-operations.md) | ✅ Done |
| [R121](R121-telemetry-logging-and-attack-signatures.md) | Telemetry, Logging, and Attack-Signature Modeling | `engine/telemetry.py`'s read-time seeded SOH telemetry + per-effect attack signatures (jam→RX power, cyber→FSW errors, DE→SNR, kinetic→LOS) and the nominal-baseline overlay. | [R103](R103-satellite-command-and-control.md) | ✅ Done |
| [R122](R122-safe-mode-recovery.md) | Safe-Mode Recovery | `engine/recovery.py`'s `RecoverySystem`: multi-pass safe-mode recovery, re-safe-on-persistence, and how it differs from the lighter-weight `cdh.clear_fault` path. | [R114](R114-command-and-data-handling.md), [R116](R116-cyber-operations-against-space-systems.md) | ✅ Done |
| [R123](R123-command-and-telemetry-console-software.md) | Real Satellite Command-and-Telemetry Console Software | Real mission-control software (ASIST/ITOS/COSMOS-OpenC3/EPOCH IPS) and command-catalog/procedure structure grounding the operator console + verb table. | [R103](R103-satellite-command-and-control.md), [R114](R114-command-and-data-handling.md) | ✅ Done |
| [R124](R124-ccsds-telemetry-and-telecommand-standards.md) | CCSDS Telemetry and Telecommand Packet Standards | The real packet/frame standards (CCSDS TC/TM space data link, COP-1) behind command validation, uplink/downlink framing, and command counters. | [R103](R103-satellite-command-and-control.md), [R114](R114-command-and-data-handling.md) | ✅ Done |
| [R125](R125-flight-operations-team-roles.md) | Flight Operations Team Roles and Console Positions | Real FOT organization (Flight Director, subsystem console operators, shift handover) grounding the White/Blue/Red cell and operator-console role model. | [R106](R106-mission-operations.md) | ✅ Done |
| [R126](R126-flight-rules-and-contingency-procedures.md) | Flight Rules and Contingency Procedures | Real flight-rule/contingency-procedure documents (NASA/ESA-style "if X, then Y" rule books) grounding ROE constraints and the recovery-chain procedure model. | [R103](R103-satellite-command-and-control.md), [R122](R122-safe-mode-recovery.md) | ✅ Done |
| [R127](R127-conjunction-assessment-and-collision-avoidance.md) | Conjunction Assessment and Collision Avoidance Operations | Real CA/COLA operations (18th SDS conjunction screening, CARA, maneuver decision thresholds) grounding custody-driven collision-avoidance maneuver planning. | [R102](R102-space-domain-awareness.md), [R105](R105-custody-theory.md), [R112](R112-propulsion-and-maneuver-planning.md) | ✅ Done |
| [R128](R128-ground-network-contact-scheduling.md) | Ground-Network Contact Scheduling and Conflict Resolution | Real multi-mission ground-network scheduling (DSN/AFSCN-style contention, conflict resolution) grounding `AccessProvider`-window-based contact allocation realism. | [R107](R107-ground-segment-operations.md), [R118](R118-space-surveillance-networks.md) | ✅ Done |
| [R129](R129-sigint-collection-and-geolocation-accuracy.md) | SIGINT Collection and Geolocation Accuracy | `engine/sigint.py`'s band/intercept-mode database (scan/track/geolocate) and the √dwell × √N-collector geolocation-error model, grounded against real ELINT/SIGINT collection and multilateration/TDOA geolocation practice (POPPY/PARCAE, TDOA accuracy). | [R109](R109-sensor-operations.md), [R104](R104-collection-management.md) | ✅ Done |
| [R130](R130-downlink-operations-and-data-return.md) | Downlink Operations and Data Return | `engine/orders.py`'s `downlink` action verb (`execute_downlink`'s `bitrate_cap_kbps`/`priority`/`partial_dump`) — the one order-verb type R103/R107/R114 each explicitly disclaimed covering; grounded against real priority-lane downlink scheduling, link-budget-bounded bitrate, and CFDP-style selective dump. | [R103](R103-satellite-command-and-control.md), [R114](R114-command-and-data-handling.md) | ✅ Done |
| [R131](R131-space-environment-and-space-weather-operations.md) | Space Environment and Space Weather Operations | Storm-driven drag/scintillation/SEU effects and the attack-vs-environment telemetry disambiguation problem. | [R110](R110-communications.md), [R111](R111-power-and-thermal-operations.md) | ✅ Done |
| [R132](R132-proliferated-constellation-c2-and-mesh-operations.md) | Proliferated-Constellation C2 and Mesh Operations | What changes at real proliferated (tens-hundreds-sat) scale beyond the ≤3-sat model — research-first, no feature yet. | [R108](R108-constellation-operations.md), [R118](R118-space-surveillance-networks.md) | ✅ Done |
| [R133](R133-space-logistics-launch-reconstitution-and-servicing-economics.md) | Space Logistics: Launch, Reconstitution, and Servicing Economics | Reconstitution timelines, refueling/servicing as Δv-economy extensions — closes GAP-05. | [R112](R112-propulsion-and-maneuver-planning.md) | ✅ Done |
| [R134](R134-pnt-warfare-and-navigation-denial-operations.md) | PNT Warfare and Navigation-Denial Operations | GNSS interference/spoofing operational patterns behind the `pnt.*` command verbs — closes GAP-09. | [R109](R109-sensor-operations.md), [R110](R110-communications.md) | ✅ Done |
| [R135](R135-ground-segment-operations-as-contested-terrain.md) | Ground Segment Operations as Contested Terrain | Cyber/physical attack surface of stations and networks, extending R107's cooperative-only treatment — closes GAP-12. | [R107](R107-ground-segment-operations.md), [R116](R116-cyber-operations-against-space-systems.md) | ✅ Done |
| [R136](R136-cislunar-and-xgeo-operations.md) | Cislunar and xGEO Operations | Custody/sensing regimes beyond GEO — research-first, closes GAP-04. | [R101](R101-orbital-mechanics-for-operations.md), [R102](R102-space-domain-awareness.md) | ✅ Done |

**Status: 36 of 36 topics complete — tier fully closed.** All
36 authored topics (R101-R136) have substantive §1 Purpose/§2 Scope/§3 Concepts/§4 Operational
Context/§5 Implementation Guidance/§6 Feature Mapping/§7 Related Topics content. A remediation pass
(2026-06-27) resolved the two systemic defects a prior MSTR-007 re-check had found in the original
20-topic set (R101-R120):

1. **§2 Scope sections.** All 20 originally-authored topics (R101-R120) now carry the mandatory §2
   Scope section (MSTR-007 §4.2) stating what each topic covers and explicitly excludes against its
   neighbors, in addition to R101/R102 which already had one.
2. **Citations.** All 20 originally-authored topics now carry at least one inline-cited claim plus a
   `### Sources` subsection (live URL + Wayback snapshot + accessed date) and `Last Reviewed` /
   `Primary Sources Consulted` frontmatter, per `docs/research/10-sources-and-methodology.md`'s
   citation convention.

Per MSTR-007 §7's coverage test (walk `CLAUDE.md`'s Code map against the tier), `engine/
telemetry.py` and `engine/recovery.py` previously had no topic an implementer extending them would
read first — that gap is now closed by fully-authored [R121](R121-telemetry-logging-and-attack-signatures.md) and
[R122](R122-safe-mode-recovery.md), each following the same seven-section shape and citation convention. Tiers
[R200](R200-index.md)-[R500](R500-index.md) had the same two systemic defects as of this tier's prior re-check — see
their own index files for their remediation status.

A second authoring pass (2026-06-27) added six further topics, [R123](R123-command-and-telemetry-console-software.md)-[R128](R128-ground-network-contact-scheduling.md), grounding the
real-world precedent behind `spacesim`'s command/console layer and several operational procedures
the simulator abstracts: real T&C console software and command catalogs ([R123](R123-command-and-telemetry-console-software.md)), the CCSDS
TC/COP-1 protocol standards beneath command validation ([R124](R124-ccsds-telemetry-and-telecommand-standards.md)), real flight-operations-team
console-position organization ([R125](R125-flight-operations-team-roles.md)), real flight-rule/contingency-procedure documents grounding
ROE and the recovery chain ([R126](R126-flight-rules-and-contingency-procedures.md)), real conjunction-assessment/collision-avoidance practice
([R127](R127-conjunction-assessment-and-collision-avoidance.md)), and real multi-mission ground-network contact scheduling ([R128](R128-ground-network-contact-scheduling.md)). Each follows the
same seven-section shape and citation convention, with bidirectional cross-links added to every
existing topic each new one grounds or extends.

**Re-audit (2026-06-27, code-vs-encyclopedia coverage pass).** Re-walking every `spacesim/engine/`
module against this tier (not just the `CLAUDE.md` Code map list) found one further engine
subsystem with implemented, user-facing behavior but no R1xx topic grounding it:
`engine/sigint.py` (the SIGINT band/mode database and the √dwell × √N-collector geolocation-error
formula reachable via `buscommands.sigint.task_collection` and the planned `POST /sigint/compute`
preview endpoint — see `docs/FUTURE-WORK.md` §11.A). The doctrine primers
([`research/02`](../02-doctrine-non-western.md), [`research/05`](../05-mission-types-and-counters.md))
mention SIGINT only in passing (mission-type taxonomy, non-Western programs) and never cite or
justify the specific accuracy model the code implements. **R129** (above) now closes this gap,
grounding `BANDS`/`MODES` against the ELINT/COMINT taxonomy and `geolocation_error_km()`'s
dwell/collector-count scaling against the POPPY/PARCAE TDOA multilateration precedent.

**Action-verb coverage check (2026-06-27).** `engine/orders.py` defines seven order-verb action
types (`jam`/`engage`/`observe`/`maneuver`/`downlink`/`cyber`/`command`, per `CLAUDE.md`'s
Code map). Checking each against this tier: `jam`→[R115](R115-electronic-warfare-in-space-operations.md),
`engage`→[R117](R117-directed-energy-and-kinetic-effects.md), `cyber`→[R116](R116-cyber-operations-against-space-systems.md),
`maneuver`→[R112](R112-propulsion-and-maneuver-planning.md), `observe`→[R109](R109-sensor-operations.md),
and `command`→[R103](R103-satellite-command-and-control.md) (the generic validate→window→execute
pipeline every verb, including the bus/payload catalog dispatch, runs through) each already had a
dedicated topic. `downlink` did not: [R103](R103-satellite-command-and-control.md),
[R107](R107-ground-segment-operations.md), and [R114](R114-command-and-data-handling.md) each
explicitly scope themselves *away* from the downlink action's own delivery/scheduling mechanics
(uplink-only, ground-site-model-only, storage-buffer-only respectively), leaving it the one verb
with no topic an implementer extending `execute_downlink` would read first. Closed by newly
authored **[R130](R130-downlink-operations-and-data-return.md)**, with all seven action verbs now
covered.

**Strategic-review gap-closure pass (2026-07-01).** The Independent Strategic Review Board report
([`docs/reviews/strategic-review-2026-07.md`](../../reviews/strategic-review-2026-07.md) Part 3)
identified 13 research gaps against the full corpus; 7 fell within this tier's scope. Two —
**GAP-01** (space environment/space-weather operations, no topic previously grounded the
attack-vs-environment telemetry disambiguation problem) and **GAP-10** (proliferated-constellation
C2/mesh operations, the flagship correction to the ≤3-sat sizing assumption) — are closed by newly
authored **[R131](R131-space-environment-and-space-weather-operations.md)** and
**[R132](R132-proliferated-constellation-c2-and-mesh-operations.md)** above, each following the
same seven-section shape and citation convention. The remaining five in-tier gaps (space
logistics/reconstitution, PNT warfare, ground-segment-as-contested-terrain, cislunar/xGEO, plus
GAP-02's debris-persistence extension to [R117](R117-directed-energy-and-kinetic-effects.md) rather
than a new topic) were recorded as `⛔ Planned` rows (`R133`-`R136`) per the index-before-content
rule (MSTR-007 §6) rather than bulk-authored in the same pass — full resolution status, source
leads, and the affected-architecture/requirements assessment for every gap (including the two
outside this tier's scope) is tracked in
[`docs/reviews/research-gap-resolution.md`](../../reviews/research-gap-resolution.md) (that report's
own text is not updated by this pass, per its own closing instruction — the corpus's index is the
mechanism for recording resolution).

**Deferred-gap authoring pass (2026-07-01, same day).** The four gaps recorded as `⛔ Planned` above
are now closed: **[R133](R133-space-logistics-launch-reconstitution-and-servicing-economics.md)**
(GAP-05 — responsive-launch/reconstitution tempo per the Victus Nox 2023 demonstration and
Northrop Grumman MEV-1/MEV-2 servicing-economics precedent), **[R134](R134-pnt-warfare-and-navigation-denial-operations.md)**
(GAP-09 — GNSS jam-vs-spoof operational patterns grounding the `pnt.flex_power`/`pnt.set_health_flag`
verbs against IS-GPS-200E flex power and real Baltic/Black Sea/Eastern-Mediterranean interference
data), **[R135](R135-ground-segment-operations-as-contested-terrain.md)** (GAP-12 — the Viasat
KA-SAT/AcidRain incident grounding `engine/cyber.py`'s `ground_segment`/`ground_modem` vectors, plus
NIST IR 8401 and CISA's 2024 ground-segment zero-trust guidance), and **[R136](R136-cislunar-and-xgeo-operations.md)**
(GAP-04 — the AFRL Oracle/CAPSTONE cislunar-SDA precedent and the CR3BP-vs-two-body structural
distinction the `Propagator` seam would need for any future beyond-GEO regime). All four follow the
same seven-section shape and citation convention as every other topic in this tier and carry
bidirectional cross-links into their declared dependency topics
([R101](R101-orbital-mechanics-for-operations.md), [R102](R102-space-domain-awareness.md),
[R107](R107-ground-segment-operations.md), [R109](R109-sensor-operations.md), [R110](R110-communications.md),
[R112](R112-propulsion-and-maneuver-planning.md), [R116](R116-cyber-operations-against-space-systems.md)).
Tier R100 is now fully closed at 36/36 topics; `docs/reviews/research-gap-resolution.md` is left
unmodified per its own closing instruction, since this index is the corpus's mechanism for recording
gap resolution.

**Vignette Creator grounding pass (2026-07-05).** `docs/pipeline/backlog.md` `BL-0052` (the
Vignette Creator, a large forthcoming White-Cell authoring feature) surfaced a confirmed research
gap: no existing topic enumerated realistic bus/payload parameter ranges, TLE-format/authoring
guidance, or ground-station-siting methodology — content the eventual `ADS-xxx` design-synthesis
pass for that feature needs to cite for its typed per-payload-type parameter sub-schemas rather than
invent. Rather than bulk-authoring new topics (the tier is closed, not frozen), this pass extended
seven existing topics with maintenance content, each following the existing citation convention:
[R101](R101-orbital-mechanics-for-operations.md) (TLE format + plausible element ranges by regime,
grounded against CelesTrak's NORAD TLE format reference), [R107](R107-ground-segment-operations.md)
(ground-station siting methodology — elevation mask, latitude-vs-regime coverage, network spacing,
coastal siting — complementing `docs/vignettes/GROUND-INFRASTRUCTURE.md`'s curated site list),
[R109](R109-sensor-operations.md) (identifies and grounds a genuine sub-gap: `weather` and `mw`
missile-warning payload types have zero `BEAM_MODES` entries in `engine/isr.py` at all, unlike
`isr_eo`/`isr_sar`/`sda` — grounded against GOES-R ABI and SBIRS-GEO scan/stare precedent),
[R110](R110-communications.md) (realistic SATCOM bandwidth/data-rate ranges by class, UHF narrowband
through Ka-band HTS), [R111](R111-power-and-thermal-operations.md) (EPS power budgets by satellite
size class, cross-referenced against the already-documented dead `power_w` field so the range
doesn't get mistaken for a field that's actually live), [R112](R112-propulsion-and-maneuver-planning.md)
(realistic total onboard Δv budget by mission class, distinct from the per-maneuver costs already
covered), and [R134](R134-pnt-warfare-and-navigation-denial-operations.md) (realistic baseline PNT
accuracy, grounded against the GPS SPS Performance Standard). No new `R1xx` row was added — every
extension fits an existing topic's own declared scope. `R109`'s weather/`mw` finding is the one
outright coverage gap this pass surfaced (not merely a missing range table) and is flagged in that
topic's own Implementation Guidance as a precondition for `BL-0052`'s typed sub-schema work, not
merely a nice-to-have.
