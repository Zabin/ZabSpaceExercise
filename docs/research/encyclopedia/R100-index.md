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
| [R125](R125-flight-operations-team-roles.md) | Flight Operations Team Roles and Console Positions | Real FOT organization (Flight Director, subsystem console operators, shift handover) grounding the White/Blue/Red cell and operator-console role model. | [R106](R106-mission-operations.md) | ⛔ Planned — new topic, grounds the multi-seat operator structure no existing topic covers. |
| [R126](R126-flight-rules-and-contingency-procedures.md) | Flight Rules and Contingency Procedures | Real flight-rule/contingency-procedure documents (NASA/ESA-style "if X, then Y" rule books) grounding ROE constraints and the recovery-chain procedure model. | [R103](R103-satellite-command-and-control.md), [R122](R122-safe-mode-recovery.md) | ⛔ Planned — new topic, grounds the real-world precedent for ROE-as-rule-book and scripted recovery procedures. |
| [R127](R127-conjunction-assessment-and-collision-avoidance.md) | Conjunction Assessment and Collision Avoidance Operations | Real CA/COLA operations (18th SDS conjunction screening, CARA, maneuver decision thresholds) grounding custody-driven collision-avoidance maneuver planning. | [R102](R102-space-domain-awareness.md), [R105](R105-custody-theory.md), [R112](R112-propulsion-and-maneuver-planning.md) | ⛔ Planned — new topic, grounds custody/SDA-driven maneuver decisions that R105/R112 reference but don't grounded against real CA practice. |
| [R128](R128-ground-network-contact-scheduling.md) | Ground-Network Contact Scheduling and Conflict Resolution | Real multi-mission ground-network scheduling (DSN/AFSCN-style contention, conflict resolution) grounding `AccessProvider`-window-based contact allocation realism. | [R107](R107-ground-segment-operations.md), [R118](R118-space-surveillance-networks.md) | ⛔ Planned — new topic, grounds the scheduling-contention layer above raw access windows that R107/R118 assume but don't ground against real network scheduling practice. |

**Status: closed.** All 22 R100 topics have substantive §1 Purpose/§2 Scope/§3 Concepts/§4
Operational Context/§5 Implementation Guidance/§6 Feature Mapping/§7 Related Topics content, and a
remediation pass (2026-06-27) resolved the two systemic defects a prior MSTR-007 re-check had found:

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
