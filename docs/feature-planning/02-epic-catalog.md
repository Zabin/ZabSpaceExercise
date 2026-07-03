# Epic Catalog

Nine Epics, one per top-level `FR-x000` grouping in `docs/requirements/01-functional-requirements.md`
— the requirements baseline's own hierarchy already draws these lines, so Epic boundaries are taken
directly from it rather than redrawn (per this skill's Best Practices). Every Feature in
`03-feature-catalog.md` belongs to exactly one Epic below.

---

### EP-1000 — Simulation Engine Core & Determinism

| Field | Content |
|---|---|
| **Epic ID** | EP-1000 |
| **Title** | Simulation Engine Core & Determinism |
| **Purpose** | The deterministic substrate — clock, orbital geometry, maneuver/resource accounting, effect resolution, and custody — that every other Epic ultimately reads or writes through. |
| **Features Included** | FEAT-1100, FEAT-1200, FEAT-1300, FEAT-1400, FEAT-1500 |
| **Subsystems** | C1 Simulation Engine |
| **Estimated Scope** | Very Large — this Epic underpins the project's single load-bearing invariant (determinism) and the six-access-channel geometry every other Epic schedules against. |
| **Risks** | Any change here risks violating the determinism gate that the whole documentation-driven build discipline treats as permanent; the two resolved circular-citation findings (FEAT-1100↔FEAT-4300, FEAT-1100↔FEAT-7100) originate in this Epic's own requirements text. |
| **Dependencies** | EP-7000 (FEAT-1100 depends on FEAT-7100's event log) |

### EP-2000 — Bus & Payload Operations

| Field | Content |
|---|---|
| **Epic ID** | EP-2000 |
| **Title** | Bus & Payload Operations |
| **Purpose** | The spacecraft-operator training core: subsystem health, bus/payload coupling, pass-gated telemetry, mission-type-specific actions, and the safe-mode recovery loop. |
| **Features Included** | FEAT-2100, FEAT-2200, FEAT-2300, FEAT-2400, FEAT-2500 |
| **Subsystems** | C1 Simulation Engine |
| **Estimated Scope** | Large — five Features covering the full bus-operator training objective set. |
| **Risks** | Safe-mode recovery (FEAT-2500) is a multi-pass state machine; correctness there is what the training objective actually measures, so subtle recovery-logic bugs would silently undermine the pedagogy without crashing anything. |
| **Dependencies** | EP-1000 (orbital/access geometry gates telemetry contacts, FEAT-2300) |

### EP-3000 — Command Planning & Sensor Tasking

| Field | Content |
|---|---|
| **Epic ID** | EP-3000 |
| **Title** | Command Planning & Sensor Tasking |
| **Purpose** | The plan-first commanding model — for both command-kind orders and collection-kind sensor tasking — plus the shared scheduler and execute-time re-validation that keep both kinds honest. |
| **Features Included** | FEAT-3100, FEAT-3200, FEAT-3300, FEAT-3400, FEAT-3500 |
| **Subsystems** | C1 Simulation Engine, C2 Session/Application Layer, C3 Mock SSN |
| **Estimated Scope** | Large — the mechanism every operator action and every AI-Red action (EP-9000) ultimately flows through. |
| **Risks** | FEAT-3300 and FEAT-3500 both show `UNASSIGNED` RTM traceability on their included FRs — a documentation gap on an Epic that is otherwise clearly built and tested per `CLAUDE.md`'s code map. |
| **Dependencies** | EP-1000 (access geometry gates every plan; Δv and custody gate execute-time validation) |

### EP-4000 — White Cell Exercise Control

| Field | Content |
|---|---|
| **Epic ID** | EP-4000 |
| **Title** | White Cell Exercise Control |
| **Purpose** | Everything the facilitator role uniquely controls: vignette selection, seat assignment, sole clock authority, injects, the classification banner, god-view/view-as, and manual adjudication with live parameter tuning. |
| **Features Included** | FEAT-4100, FEAT-4200, FEAT-4300, FEAT-4400, FEAT-4500, FEAT-4600, FEAT-4700 |
| **Subsystems** | C6 White Cell, C4 Operator Console |
| **Estimated Scope** | Large — the largest Epic by Feature count (7), reflecting how much of the facilitator role this project's requirements baseline itemizes. |
| **Risks** | Five of this Epic's seven Features (FEAT-4100, FEAT-4200, FEAT-4500, FEAT-4600, FEAT-4700) show `UNASSIGNED` RTM traceability — the highest concentration of the traceability gap in the catalog. All are narratively covered by the existing `FS-106-white-cell-dashboard.md` document, so this reads as a citation gap rather than a build gap, but it is the Epic most in need of a verification pass (see `05-feature-review.md`). FEAT-4500 (Classification Banner) additionally has **zero** presence in any existing Feature Specification at all. |
| **Dependencies** | EP-1000 (clock authority sits over the clock mechanism), EP-5000 (vignette selection depends on vignette validation), EP-6000 (god-view depends on the fog-of-war filter) |

### EP-5000 — Scenario / Vignette Authoring

| Field | Content |
|---|---|
| **Epic ID** | EP-5000 |
| **Title** | Scenario / Vignette Authoring |
| **Purpose** | Turning a scenario concept into a runnable, validated vignette file — in-app iterative composition, TLE import with offline fallback, and load-time validation. |
| **Features Included** | FEAT-5100, FEAT-5200, FEAT-5300 |
| **Subsystems** | C5 Content & Data |
| **Estimated Scope** | Medium. |
| **Risks** | The strategic review independently flags scenario authoring as still "White-Cell-hostile" in practice (§4.2) — the requirement (FEAT-5100) may be nominally met while YAML hand-editing remains the dominant real workflow; this is a usability finding, not a traceability gap. |
| **Dependencies** | EP-1000 (TLE import needs the propagation seam) |

### EP-6000 — Session, Multiplayer & Fog-of-War

| Field | Content |
|---|---|
| **Epic ID** | EP-6000 |
| **Title** | Session, Multiplayer & Fog-of-War |
| **Purpose** | The session-layer seam, the fog-of-war filter it enforces, the LAN-multiplayer clock/locking transport, hot-seat/LAN session sharing, Observer access, and the hot-seat hand-off screen-blank behavior. |
| **Features Included** | FEAT-6100, FEAT-6200, FEAT-6300, FEAT-6400, FEAT-6500, FEAT-6600 |
| **Subsystems** | C2 Session/Application Layer, C4 Operator Console, C9 Observer |
| **Estimated Scope** | Very Large — six Features spanning three architecturally distinct concerns (the seam itself, fog-of-war, and multiplayer transport) that the existing FS corpus currently collapses into one document. |
| **Risks** | **This Epic contains both capabilities the motivating audit found with zero presence anywhere in the existing 11 `FS-xxx` documents** (FEAT-6500 Observer, FEAT-6600 Hot-Seat Hand-Off) **and** the entire P8 multiplayer transport (FEAT-6300/6400), which despite three dedicated ADRs (ADR-0014, ADR-0015, ADR-0026) is also undifferentiated inside the single `FS-106-white-cell-dashboard.md` document. This Epic is the single strongest candidate in the whole catalog for a Feature-Specification-authoring pass (see `05-feature-review.md`). |
| **Dependencies** | EP-1000 (the multiplayer clock depends on the core clock; fog-of-war depends on custody) |

### EP-7000 — Logging, Replay & After-Action Review

| Field | Content |
|---|---|
| **Epic ID** | EP-7000 |
| **Title** | Logging, Replay & After-Action Review |
| **Purpose** | The event log, deterministic save/resume with content-session ownership split, and the read-only AAR replay/scrub/branch-compare instrument built over both. |
| **Features Included** | FEAT-7100, FEAT-7200, FEAT-7300 |
| **Subsystems** | C1 Simulation Engine, C2 Session/Application Layer, C5 Content & Data, C11 Local filesystem |
| **Estimated Scope** | Large — foundational to EP-1000's own determinism guarantee (FEAT-1100 depends on FEAT-7100), not merely a downstream consumer of it. |
| **Risks** | FEAT-7200 (Save/Resume) is currently undifferentiated inside `FS-106-white-cell-dashboard.md` despite its own dedicated ADR (ADR-0022) and ICD issue closure — a second strong candidate for its own Feature Specification alongside the EP-6000 findings. |
| **Dependencies** | None outbound (this Epic is depended upon by EP-1000, not the reverse) |

### EP-8000 — Operator Console Presentation

| Field | Content |
|---|---|
| **Epic ID** | EP-8000 |
| **Title** | Operator Console Presentation |
| **Purpose** | The single architectural decision (browser-over-desktop-GUI) and its cross-cutting quality attributes — performance, hardware floor, accessibility, portability, configuration, external-integration boundary — that make every other Epic's capability reachable by a human. |
| **Features Included** | FEAT-8100 |
| **Subsystems** | C4 Operator Console, C12 Browser client |
| **Estimated Scope** | Small in Feature count, Large in actual surface area (a whole hand-rolled front end lives inside this one Feature's scope) — kept as a single Feature rather than split because the requirements baseline itself carries only one FR leaf (FR-8110) here, with the rest as cross-cutting NFRs rather than distinct functional capabilities. |
| **Risks** | The strategic review flags framework-free JS as a cost multiplier for future UI-scale Features (e.g. constellation aggregation) — a forward cost, not a current defect. |
| **Dependencies** | None (this Epic has no Feature-level build dependency on any other Epic) |

### EP-9000 — AI-Red

| Field | Content |
|---|---|
| **Epic ID** | EP-9000 |
| **Title** | AI-Red |
| **Purpose** | Doctrine-preset-driven automated Red-cell command generation, substituting for an unseated Red operator through the same command path a human would use. |
| **Features Included** | FEAT-9100 |
| **Subsystems** | C1 Simulation Engine, C8 Red Cell (AI-Red) |
| **Estimated Scope** | Small in Feature count (one FR leaf in the baseline), but strategically the highest-priority Epic in the whole catalog per the July-2026 Strategic Review (FC-02/GAP-08) — kept as its own Epic rather than folded into EP-4000 (White Cell) or EP-3000 (Command Planning) specifically *because* of that strategic weight, even though it is currently folded into `FS-106-white-cell-dashboard.md` in the existing (pre-catalog) documentation. |
| **Risks** | AI-Red's direct ground-truth read (INT-0015, ADR-0024) is an accepted v1 asymmetry and the single most-flagged strategic gap in the project's own governance record. |
| **Dependencies** | EP-3000 (AI-Red issues activities through the same plan-first/re-validation path as a human operator) |

---

### EP-10000 — Assessment & Research Instrumentation *(new 2026-07)*

| Field | Content |
|---|---|
| **Epic ID** | EP-10000 |
| **Title** | Assessment & Research Instrumentation |
| **Purpose** | Rubric-based competency measurement and multi-run/cohort research export — the capability area DOM-002 (Assessment) and DOM-004 (Research) ground, promoted from Candidate Requirements once their blocking ADR conflicts (`ADR-0017`, `ADR-0029`) were resolved by `ADR-0032`/`ADR-0033`. |
| **Features Included** | FEAT-10100, FEAT-10200 |
| **Subsystems** | C1 Simulation Engine, C2 Session/Application Layer |
| **Estimated Scope** | Small in Feature count (two FR leaves), but each was blocked on a direct Accepted-ADR conflict until this session's project-owner decisions resolved them — the only Epic in this catalog whose very existence required an architecture-tier reversal (`FEAT-10200`) or narrowing (`FEAT-10100`), not merely a decomposition choice. |
| **Risks** | `FEAT-10200` depends on `FEAT-10100`'s output; both remain `MSTR-006` §3 gated for implementation regardless of their ADR-tier resolution — a package being unblocked at the architecture tier is not an authorization to code (see `IP-2010`/`IP-3010`). |
| **Dependencies** | EP-1000 (FEAT-10200 depends on the core deterministic clock for reproducibility) |

---

## Summary

| Epic | Features | Epic-level Dependencies |
|---|---|---|
| EP-1000 Simulation Engine Core & Determinism | 5 | EP-7000 |
| EP-2000 Bus & Payload Operations | 5 | EP-1000 |
| EP-3000 Command Planning & Sensor Tasking | 5 | EP-1000 |
| EP-4000 White Cell Exercise Control | 7 | EP-1000, EP-5000, EP-6000 |
| EP-5000 Scenario / Vignette Authoring | 3 | EP-1000 |
| EP-6000 Session, Multiplayer & Fog-of-War | 6 | EP-1000 |
| EP-7000 Logging, Replay & After-Action Review | 3 | (none outbound) |
| EP-8000 Operator Console Presentation | 1 | (none) |
| EP-9000 AI-Red | 1 | EP-3000 |
| EP-10000 Assessment & Research Instrumentation *(new 2026-07)* | 2 | EP-1000 |
| **Total** | **38** | |

Every Feature in `03-feature-catalog.md` appears in exactly one Epic's `Features Included` list
above — cross-checked against the catalog's own Epic headers (38 Features total, matching the
catalog's Summary table).
