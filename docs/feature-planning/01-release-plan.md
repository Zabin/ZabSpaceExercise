# Release Plan

> **Reading note:** This catalog decomposes an approved requirements baseline that, per
> `ROADMAP.md`, already corresponds to a **shipped system** (Phases P0–P8 complete). The bucket
> assignments below are therefore reconstructed against build history — using each Feature's
> dependency depth (`04-feature-dependency-graph.md`), MoSCoW priority (from the requirements
> baseline), and the Requirements Traceability Matrix's own Impl. Package column (a real-file-path
> citation vs. `UNASSIGNED`) as the three evidence sources — not invented forward planning. Where
> the RTM shows `UNASSIGNED`, the bucket reflects "needs a traceability/verification pass," never
> "needs new development," unless stated otherwise.

## Bucket assignments

### Prototype

| Feature | Justification |
|---|---|
| **FEAT-1100** Deterministic, Sub-Stepped Simulation Clock | The single load-bearing invariant (`CLAUDE.md` #1); nothing else in the catalog is buildable/testable without it. Foundational per the dependency graph. |
| **FEAT-1200** Orbital Propagation & Access-Window Geometry | Highest fan-out Feature in the catalog (7 direct dependents); the geometric substrate every other Epic schedules against. |

### MVP

| Feature | Justification |
|---|---|
| **FEAT-7100** Ordered Event Log | Head of the catalog's critical path; FEAT-1100 itself depends on it. Must exist before determinism can be verified. |
| **FEAT-1300** Impulsive Maneuver & Δv Budget Accounting | Must-priority; the core resource-scarcity mechanic every order type ultimately checks. |
| **FEAT-1400** Five-D's Counterspace Effect Resolution | Must-priority; without it no counterspace action has an outcome — the doctrinal core of the simulator. |
| **FEAT-1500** Custody, Track Confidence & Weapons-Quality Gate | Must-priority; gates every engagement-intent action, a dependency of FEAT-3400 and FEAT-6200. |
| **FEAT-6100** SessionAPI Single Seam | Must-priority; the architectural boundary (ADR-0002/0003) that makes the engine UI-agnostic — needed before any UI-facing Feature can be built safely. |
| **FEAT-5300** Load-Time Vignette Validation | Must-priority; a dependency of FEAT-4100 — no session can start without a validated vignette. |
| **FEAT-5100** In-App Iterative Vignette Builder | Must-priority; the authoring path FEAT-4500 depends on. |
| **FEAT-8100** Browser-Based Operator Console Presentation | Must-priority; without a presentation layer no other Feature is reachable by a human. Zero Feature-level dependencies — buildable in parallel with the engine core. |

### Release 1

| Feature | Justification |
|---|---|
| **FEAT-2100–2500** (Bus SOH, Bus-Gates-Payload, Pass-Gated Telemetry, Payload-Type Actions, Safe-Mode Loop) | All Must-priority; RTM cites real built files for all five (`engine/bus.py`, `busmodel.py`, `buscommands.py`, `recovery.py`). Complete bus-operator training core, depends only on MVP-bucketed FEAT-1200. |
| **FEAT-3100–3200, 3400** (Plan-First Commands, SSN Tasking, Execute-Time Re-Validation) | All Must-priority, RTM-verified built (`engine/orders.py`, `engine/ssn.py`). |
| **FEAT-3300** Unified Planned-Activity Scheduler | Must-priority per requirements, but RTM Impl. Package is `UNASSIGNED` — placed here on priority/dependency grounds; the traceability gap itself is a Release-1-scoped verification task, not new development (see `05-feature-review.md`). |
| **FEAT-3500** Role-Scoped Command Catalog & Assignment Scoping | Must-priority; both included FRs show RTM `UNASSIGNED` — same verification-task framing as FEAT-3300. |
| **FEAT-4100, 4200, 4300, 4600, 4700** (Vignette Selection, Seat Assignment, Clock Control Authority, God-View/View-As, Manual Adjudication) | All Must-priority and narratively covered by the existing `FS-106-white-cell-dashboard.md` (confirming real, shipped White Cell control-plane functionality) despite `UNASSIGNED` RTM citations — placed at Release 1 on priority/narrative-coverage grounds, with the citation gap flagged as Release-1-scoped verification work. |
| **FEAT-5200** TLE Import with Manual/Keplerian Fallback | Must-priority, RTM-verified built; depends only on Prototype-bucketed FEAT-1200. |
| **FEAT-6200, 6300, 6400** (Fog-of-War Filter, Lazy Clock/Locking, Hot-Seat/LAN Sharing) | All Must-priority, RTM-verified built (`session/cells.py`, `session/manager.py`, `session/inprocess.py`); this is the entire P8 multiplayer transport plus the fog-of-war boundary — foundational to every cell-facing Feature. |
| **FEAT-7200, 7300** (Save/Resume, AAR Replay/Scrub/Branch-Compare) | Both Must-priority (branch-compare is Should for FR-7320 specifically), RTM-verified built (`session/manager.py`, `session/aar.py`). |

### Release 2

| Feature | Justification |
|---|---|
| **FEAT-4400** Inject Authoring & Firing | Must-priority and RTM-verified built (`session/manager.py`), but placed at Release 2 to reflect its actual phase history (P4.5, after the core P0–P4 loop) rather than Release 1's P4-and-earlier core. |
| **FEAT-9100** Doctrine-Preset-Driven AI-Red Automation | **Should**-priority by the requirements baseline's own explicit statement (FR-9110: "a vignette remains fully playable with a human-seated... Red cell; AI-Red is a valuable convenience... not a precondition for any vignette's playability") — the one Feature in the catalog whose own source requirement states it is not MVP/Release-1-critical, despite being the strategic review's single highest-priority *future* recommendation (FC-02/GAP-08 fog-of-war parity, which is explicitly **not** part of this Feature's baseline scope). |
| **FEAT-4500** Classification Banner | Must-priority per its FR, but this catalog's motivating audit found **zero** Feature Specification coverage anywhere in the existing corpus and an `UNASSIGNED` RTM citation — placed at Release 2 specifically to force a verification-then-documentation pass (confirm it is actually built, then close both the FS and RTM gaps) rather than let it continue riding silently inside another document. |
| **FEAT-6500** Observer Read-Only Access | Must-priority per its FR, same treatment as FEAT-4500 — one of the two capabilities this catalog's motivating audit specifically flagged as having no Feature Specification anywhere. |
| **FEAT-6600** Hot-Seat Hand-Off Screen-Blank Menu | Must-priority per its FR (closes GDS-05's own prior Open Question 1), same treatment — the second of the two audit-flagged gaps, and the deepest node on the catalog's critical path. |
| **FEAT-10100** Automated Non-Aggregating Competency Rubric Computation *(new 2026-07)* | **Should**-priority, same reasoning pattern as FEAT-9100 — valuable but not a precondition for any vignette's playability. Additionally gated on `MSTR-006` §3 authorization (forward-design, not yet implemented) independent of its now-resolved `ADR-0017` conflict (`ADR-0032`). |
| **FEAT-10200** Multi-Run/Cohort Structured Research-Data Export *(new 2026-07)* | **Should**-priority, depends on FEAT-10100 (same bucket, dependency-consistent). Additionally gated on `MSTR-006` §3 authorization and on `IP-2010` (FEAT-10100's implementation package) reaching `COMPLETE` first — its own now-resolved `ADR-0029` conflict (`ADR-0033`) does not remove either gate. |

### Future

*(No Feature is bucketed here.)* Every capability that would otherwise land in Future — AI-Red
fog-of-war parity, coalition play, proliferated constellations, commercial actors, campaign
persistence, ground-segment-as-terrain cyber, persistent debris, adjudication-consistency support,
and the rest — corresponds to a **Candidate Requirement** (CR-01–18/CNFR-01–07) or a **Strategic
Review Future Concept/Gap** (FC-01–15/GAP-01–13), *none of which are part of the approved baseline
this Feature Catalog decomposes*. They are not Features that got deferred; they are not yet
Features at all. See `05-feature-review.md` for the full disposition and what upstream work
(baselining a Candidate Requirement, or authoring new requirements from a Future Concept) would be
needed before any of them could enter this catalog.

---

## Cross-cutting summary

### Highest Value

- **FEAT-1100** (Deterministic Clock), **FEAT-1200** (Access-Window Geometry), **FEAT-6200**
  (Fog-of-War Filter) — the three Features that most directly encode this project's three
  load-bearing invariants (determinism, plan-first/access-gating, fog-of-war-at-the-boundary).
- **FEAT-9100** (AI-Red) — lower baseline priority (Should) but the single highest-value *future*
  lever per the July-2026 Strategic Review, since closing its fog-of-war-parity gap (CR-01) is
  named as prerequisite to nearly every AI-related research direction the review identifies.

### Highest Risk

- **FEAT-6200** (Fog-of-War Filter) — its named ground-truth exception set is also the documented
  v1 LAN trust boundary (ADR-0015); a hostile LAN participant can already read another cell's
  belief state by design, an accepted but real risk.
- **FEAT-6300** (Lazy Clock/Locking) — the ~16-participant concurrency ceiling (ADR-0026, NFR-1400)
  is a documented estimate, never load-tested.
- **FEAT-9100** (AI-Red) — carries the single most-flagged strategic gap in the project's own
  governance record (direct ground-truth read, ADR-0024).
- **FEAT-8100** (Browser Console) — framework-free hand-rolled JS is flagged as a cost multiplier
  for every future UI-scale Feature.

### Foundational (critical path or blocking, per `04-feature-dependency-graph.md`)

FEAT-1200, FEAT-7100, FEAT-1100, FEAT-2100, FEAT-3100, FEAT-6200 — see the dependency graph's
"Blocking Features" table for fan-out counts.

### Optional (no other Feature depends on them — deferrable *within this graph* without blocking
anything; this is a dependency-graph property, not a statement about priority or value)

FEAT-1400, FEAT-2300, FEAT-2400, FEAT-2500, FEAT-3300, FEAT-3500, FEAT-4200, FEAT-4300, FEAT-4400,
FEAT-4500, FEAT-4600, FEAT-4700, FEAT-5200, FEAT-6500, FEAT-6600, FEAT-7200, FEAT-8100,
FEAT-9100, FEAT-10200 *(new 2026-07)*. Several of these (e.g. FEAT-2500 Safe-Mode Loop, FEAT-6600
Hot-Seat Hand-Off) are Must-priority, high-value Features in their own right — "optional" here
means only that no *sibling Feature's construction* is blocked by deferring them, not that the
capability itself is low-value. **FEAT-7300 removed from this list (2026-07):** it now has a
dependent (`FEAT-10100`) and is no longer a leaf node in the dependency graph.

### Deferred

None within this catalog (see the "Future" bucket note above for why deferred-candidate items live
upstream of this catalog, not inside it).
