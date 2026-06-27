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
| [R110](R110-communications.md) | Communications | Uplink/downlink/ISL, jamming/interference, link denial. | [R101](R101-orbital-mechanics-for-operations.md) | 🚧 *(no §2 Scope; uncited)* |
| [R111](R111-power-and-thermal-operations.md) | Power and Thermal Systems Operations | EPS/battery/eclipse cycling, thermal state — the bus SOH model. | [R103](R103-satellite-command-and-control.md) | 🚧 *(no §2 Scope; uncited)* |
| [R112](R112-propulsion-and-maneuver-planning.md) | Propulsion and Maneuver Planning | Δv economy, the six maneuver entry modes, Hohmann/plane-change. | [R101](R101-orbital-mechanics-for-operations.md) | 🚧 *(no §2 Scope; uncited)* |
| [R113](R113-attitude-determination-and-control.md) | Attitude Determination and Control | ADCS modes, pointing constraints, their operational consequences. | [R103](R103-satellite-command-and-control.md) | 🚧 *(no §2 Scope; uncited)* |
| [R114](R114-command-and-data-handling.md) | Command and Data Handling | Onboard storage, dump/playback, the CDH subsystem model. | [R103](R103-satellite-command-and-control.md) | 🚧 *(no §2 Scope; uncited)* |
| [R115](R115-electronic-warfare-in-space-operations.md) | Electronic Warfare in Space Operations | Jamming taxonomy (barrage/spot/sweep/deceptive), effective radius/success. | [R110](R110-communications.md) | 🚧 *(no §2 Scope; uncited)* |
| [R116](R116-cyber-operations-against-space-systems.md) | Cyber Operations Against Space Systems | The cyber exception, vectors × payloads, attribution, persistence/patchability. | [R103](R103-satellite-command-and-control.md) | 🚧 *(no §2 Scope; uncited)* |
| [R117](R117-directed-energy-and-kinetic-effects.md) | Directed Energy and Kinetic Effects | Engagement geometry, salvo Pₖ, debris-cone consequences. | [R105](R105-custody-theory.md) | 🚧 *(no §2 Scope; uncited)* |
| [R118](R118-space-surveillance-networks.md) | Space Surveillance Networks | SSN dispersion presets, hybrid turnaround, coalition vs. national affiliation. | [R102](R102-space-domain-awareness.md) | 🚧 *(no §2 Scope; uncited)* |
| [R119](R119-space-situational-data-fusion.md) | Space Situational Data Fusion | Combining multiple sensor/SSN inputs into a single custody picture. | [R105](R105-custody-theory.md), [R118](R118-space-surveillance-networks.md) | 🚧 *(no §2 Scope; uncited)* |
| [R120](R120-access-window-and-geometry-planning.md) | Access Window and Geometry Planning | The six access channels, window caching, sub-stepped scheduling. | [R101](R101-orbital-mechanics-for-operations.md) | 🚧 *(no §2 Scope; uncited)* |
| [R121](R121-telemetry-logging-and-attack-signatures.md) | Telemetry, Logging, and Attack-Signature Modeling | `engine/telemetry.py`'s read-time seeded SOH telemetry + per-effect attack signatures (jam→RX power, cyber→FSW errors, DE→SNR, kinetic→LOS) and the nominal-baseline overlay. | [R103](R103-satellite-command-and-control.md) | ⛔ Planned — no existing topic covers `telemetry.py`; gap found per MSTR-007 §7 coverage check. |
| [R122](R122-safe-mode-recovery.md) | Safe-Mode Recovery | `engine/recovery.py`'s `RecoverySystem`: multi-pass safe-mode recovery, re-safe-on-persistence, and how it differs from the lighter-weight `cdh.clear_fault` path. | [R114](R114-command-and-data-handling.md), [R116](R116-cyber-operations-against-space-systems.md) | ⛔ Planned — `RecoverySystem` is only name-dropped inside R114/R116 today, not covered as its own subject; gap found per MSTR-007 §7 coverage check. |

**Status: incomplete, not done.** All 20 authored R100 topics have substantive §1/§3/§4/§5/§6/§7
content, but a full re-check against MSTR-007 found two systemic defects that the original "✅
Done" status missed:

1. **18 of 20 topics (all but R101/R102) omit the mandatory §2 Scope section** (MSTR-007 §4.2) —
   they jump from "1. Purpose" straight to a "2. Concepts" section, with no boundary-against-
   neighboring-topics content anywhere in the document.
2. **All 20 topics are entirely uncited** — zero `### Sources` subsections, zero inline URLs, zero
   YAML `last_reviewed`/`primary_sources_consulted` frontmatter. `docs/research/10-sources-and-
   methodology.md` states its citation convention "applies to every file in this corpus"
   (`docs/research/`, which includes this tier), and the existing `01-07` primers comply (48-204
   citations each) — the encyclopedia never went through that pass.

Per MSTR-007 §7's coverage test (walk `CLAUDE.md`'s Code map against the tier), `engine/
telemetry.py` and `engine/recovery.py` also have no topic an implementer extending them would read
first — tracked above as new `⛔ Planned` rows R121/R122 rather than silently left out. Tier R100
is **not** closed pending a remediation pass (Scope sections + citations + R121/R122). Tiers
[R200](R200-index.md)-[R500](R500-index.md) have the same two systemic defects — see their own
index files.
