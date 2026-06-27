# Tier R100 — Space Operations Foundation

[↑ Encyclopedia index](INDEX.md)

The simulator's direct subject matter: orbital mechanics, SDA, C2, custody, ground/constellation/
sensor operations. Coverage check method: every named engine subsystem in `CLAUDE.md`'s "Code map"
should have at least one topic here an implementer extending it would read first (MSTR-007 §7).

| ID | Title | Scope (one line) | Depends on | Status |
|---|---|---|---|---|
| [R101](R101-orbital-mechanics-for-operations.md) | Orbital Mechanics for Operations and Implementation | Implementation-focused orbital mechanics; points to [`research/04-orbital-mechanics-primer.md`](../04-orbital-mechanics-primer.md) for derivations. | — | ✅ |
| [R102](R102-space-domain-awareness.md) | Space Domain Awareness | SDA as a discipline: detection, tracking, characterization, attribution. | [R101](R101-orbital-mechanics-for-operations.md) | ✅ |
| [R103](R103-satellite-command-and-control.md) | Satellite Command and Control | The C2 chain: uplink, command validation, execution windows. | [R101](R101-orbital-mechanics-for-operations.md) | ✅ |
| [R104](R104-collection-management.md) | Collection Management | Sensor tasking, contention, prioritization across competing demands. | [R102](R102-space-domain-awareness.md), [R109](R109-sensor-operations.md) | ✅ |
| [R105](R105-custody-theory.md) | Custody Theory | What custody means, confidence decay, the weapons-quality gate. | [R102](R102-space-domain-awareness.md) | ✅ |
| [R106](R106-mission-operations.md) | Mission Operations | The operator's day-to-day workflow: plan, task, execute, assess. | [R103](R103-satellite-command-and-control.md) | ✅ |
| [R107](R107-ground-segment-operations.md) | Ground Segment Operations | Ground stations, contact scheduling, downlink/uplink constraints. | [R101](R101-orbital-mechanics-for-operations.md), [R103](R103-satellite-command-and-control.md) | ✅ |
| [R108](R108-constellation-operations.md) | Constellation Operations | Multi-satellite coordination, the ≤3-sat operated-individually guideline. | [R106](R106-mission-operations.md) | ✅ |
| [R109](R109-sensor-operations.md) | Sensor Operations | EO/SAR/SDA sensor modalities, beam modes, footprint geometry. | [R101](R101-orbital-mechanics-for-operations.md) | ✅ |
| [R110](R110-communications.md) | Communications | Uplink/downlink/ISL, jamming/interference, link denial. | [R101](R101-orbital-mechanics-for-operations.md) | ✅ |
| [R111](R111-power-and-thermal-operations.md) | Power and Thermal Systems Operations | EPS/battery/eclipse cycling, thermal state — the bus SOH model. | [R103](R103-satellite-command-and-control.md) | ✅ |
| [R112](R112-propulsion-and-maneuver-planning.md) | Propulsion and Maneuver Planning | Δv economy, the six maneuver entry modes, Hohmann/plane-change. | [R101](R101-orbital-mechanics-for-operations.md) | ✅ |
| [R113](R113-attitude-determination-and-control.md) | Attitude Determination and Control | ADCS modes, pointing constraints, their operational consequences. | [R103](R103-satellite-command-and-control.md) | ✅ |
| [R114](R114-command-and-data-handling.md) | Command and Data Handling | Onboard storage, dump/playback, the CDH subsystem model. | [R103](R103-satellite-command-and-control.md) | ✅ |
| [R115](R115-electronic-warfare-in-space-operations.md) | Electronic Warfare in Space Operations | Jamming taxonomy (barrage/spot/sweep/deceptive), effective radius/success. | [R110](R110-communications.md) | ✅ |
| [R116](R116-cyber-operations-against-space-systems.md) | Cyber Operations Against Space Systems | The cyber exception, vectors × payloads, attribution, persistence/patchability. | [R103](R103-satellite-command-and-control.md) | ✅ |
| [R117](R117-directed-energy-and-kinetic-effects.md) | Directed Energy and Kinetic Effects | Engagement geometry, salvo Pₖ, debris-cone consequences. | [R105](R105-custody-theory.md) | ✅ |
| [R118](R118-space-surveillance-networks.md) | Space Surveillance Networks | SSN dispersion presets, hybrid turnaround, coalition vs. national affiliation. | [R102](R102-space-domain-awareness.md) | ✅ |
| [R119](R119-space-situational-data-fusion.md) | Space Situational Data Fusion | Combining multiple sensor/SSN inputs into a single custody picture. | [R105](R105-custody-theory.md), [R118](R118-space-surveillance-networks.md) | ✅ |
| [R120](R120-access-window-and-geometry-planning.md) | Access Window and Geometry Planning | The six access channels, window caching, sub-stepped scheduling. | [R101](R101-orbital-mechanics-for-operations.md) | ✅ |

**Status:** All 20 R100 topics are authored (✅). The first batch ([R101](R101-orbital-mechanics-for-operations.md), [R102](R102-space-domain-awareness.md), [R103](R103-satellite-command-and-control.md), [R105](R105-custody-theory.md), [R111](R111-power-and-thermal-operations.md)) was
chosen because those topics map directly to the simulator's highest-traffic subsystems (orbits,
custody, C2, bus power) and were flagged in the Jun 2026 audits as areas where implementers had
previously misunderstood causality (e.g. the SoC/eclipse confusion in `AUDIT-2026-06-UI-TTC.md`
§2). The remaining 15 topics were completed in a second pass, each grounded directly in the
corresponding `engine/` module so Tier R100 now comprehensively covers every named subsystem in
`CLAUDE.md`'s "Code map" per the coverage check method stated above. Tier R100 is closed; Tiers
[R200](R200-index.md)-[R500](R500-index.md) remain gated on explicit authorization to bulk-author (see their respective index files).
