# Tier R100 — Space Operations Foundation

[↑ Encyclopedia index](INDEX.md)

The simulator's direct subject matter: orbital mechanics, SDA, C2, custody, ground/constellation/
sensor operations. Coverage check method: every named engine subsystem in `CLAUDE.md`'s "Code map"
should have at least one topic here an implementer extending it would read first (MSTR-007 §7).

| ID | Title | Scope (one line) | Depends on | Status |
|---|---|---|---|---|
| R101 | Orbital Mechanics for Operations and Implementation | Implementation-focused orbital mechanics; points to `research/04-orbital-mechanics-primer.md` for derivations. | — | ✅ |
| R102 | Space Domain Awareness | SDA as a discipline: detection, tracking, characterization, attribution. | R101 | ✅ |
| R103 | Satellite Command and Control | The C2 chain: uplink, command validation, execution windows. | R101 | ✅ |
| R104 | Collection Management | Sensor tasking, contention, prioritization across competing demands. | R102, R109 | ✅ |
| R105 | Custody Theory | What custody means, confidence decay, the weapons-quality gate. | R102 | ✅ |
| R106 | Mission Operations | The operator's day-to-day workflow: plan, task, execute, assess. | R103 | ✅ |
| R107 | Ground Segment Operations | Ground stations, contact scheduling, downlink/uplink constraints. | R101, R103 | ✅ |
| R108 | Constellation Operations | Multi-satellite coordination, the ≤3-sat operated-individually guideline. | R106 | ✅ |
| R109 | Sensor Operations | EO/SAR/SDA sensor modalities, beam modes, footprint geometry. | R101 | ✅ |
| R110 | Communications | Uplink/downlink/ISL, jamming/interference, link denial. | R101 | ✅ |
| R111 | Power and Thermal Systems Operations | EPS/battery/eclipse cycling, thermal state — the bus SOH model. | R103 | ✅ |
| R112 | Propulsion and Maneuver Planning | Δv economy, the six maneuver entry modes, Hohmann/plane-change. | R101 | ✅ |
| R113 | Attitude Determination and Control | ADCS modes, pointing constraints, their operational consequences. | R103 | ✅ |
| R114 | Command and Data Handling | Onboard storage, dump/playback, the CDH subsystem model. | R103 | ✅ |
| R115 | Electronic Warfare in Space Operations | Jamming taxonomy (barrage/spot/sweep/deceptive), effective radius/success. | R110 | ✅ |
| R116 | Cyber Operations Against Space Systems | The cyber exception, vectors × payloads, attribution, persistence/patchability. | R103 | ✅ |
| R117 | Directed Energy and Kinetic Effects | Engagement geometry, salvo Pₖ, debris-cone consequences. | R105 | ✅ |
| R118 | Space Surveillance Networks | SSN dispersion presets, hybrid turnaround, coalition vs. national affiliation. | R102 | ✅ |
| R119 | Space Situational Data Fusion | Combining multiple sensor/SSN inputs into a single custody picture. | R105, R118 | ✅ |
| R120 | Access Window and Geometry Planning | The six access channels, window caching, sub-stepped scheduling. | R101 | ✅ |

**Status:** All 20 R100 topics are authored (✅). The first batch (R101, R102, R103, R105, R111) was
chosen because those topics map directly to the simulator's highest-traffic subsystems (orbits,
custody, C2, bus power) and were flagged in the Jun 2026 audits as areas where implementers had
previously misunderstood causality (e.g. the SoC/eclipse confusion in `AUDIT-2026-06-UI-TTC.md`
§2). The remaining 15 topics were completed in a second pass, each grounded directly in the
corresponding `engine/` module so Tier R100 now comprehensively covers every named subsystem in
`CLAUDE.md`'s "Code map" per the coverage check method stated above. Tier R100 is closed; Tiers
R200-R500 remain gated on explicit authorization to bulk-author (see their respective index files).
