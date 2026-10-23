# Release Plan

> **Reading note:** This catalog decomposes an approved requirements baseline that, per
> `ROADMAP.md`, already corresponds to a **shipped system** (Phases P0–P8 complete). The bucket
> assignments below are therefore reconstructed against build history — using each Feature's
> dependency depth (`04-feature-dependency-graph.md`), MoSCoW priority (from the requirements
> baseline), and the Requirements Traceability Matrix's own Impl. Package column (a real-file-path
> citation vs. `UNASSIGNED`) as the three evidence sources — not invented forward planning. Where
> the RTM shows `UNASSIGNED`, the bucket reflects "needs a traceability/verification pass," never
> "needs new development," unless stated otherwise.
>
> **Amended 2026-10-03** (`05-feature-decomposition`, six new FR leaves for `BL-0107`/`BL-0109`/
> `BL-0111`/`BL-0122`/`BL-0079`): unlike the rest of this plan, the three brand-new Features this
> amendment adds (**FEAT-1600**, **FEAT-7400**, **FEAT-8200**) are genuine forward planning, not a
> build-history reconstruction — their new leaves (`FR-1670`, `FR-7440`, `FR-8210`, `FR-8220`) are
> unimplemented (RTM `UNASSIGNED`), even though each Feature also carries pre-existing, already-
> `VERIFIED` sibling leaves. Bucketed at **Release 2** below on priority (`Should`) and dependency
> grounds (each depends only on already-Release-1-or-earlier-bucketed Features), consistent with
> this plan's existing Release-2 treatment of other `Should`-priority, not-yet-authorized Features
> (`FEAT-9100`, `FEAT-10100`, `FEAT-10200`). `FEAT-4400`/`FEAT-4600` each gained one new, Could-
> priority, unimplemented leaf (`FR-4450`/`FR-4620`) — both Features keep their existing bucket
> (the new leaf is additive, not a reason to reschedule the whole Feature).
>
> **Amended 2026-10-17** (run #151, full inventory sweep, `BL-0153`): the 42 leaves assigned this
> run added 22 dependency edges (`04-feature-dependency-graph.md`). Re-checking every Feature's
> bucket against its prerequisites found **six** placements where a Feature sat in an earlier
> bucket than one it depends on — five created by the new edges and one pre-existing
> (FEAT-1100 Prototype on FEAT-7100 MVP). Each is fixed by moving the earlier Feature, never by
> ignoring the edge: **FEAT-7100** MVP → Prototype; **FEAT-1300**, **FEAT-1400**, **FEAT-5100** MVP
> → Release 1; **FEAT-4400** Release 2 → Release 1. Four new Features are bucketed: **FEAT-5400**,
> **FEAT-5500** (Release 2), **FEAT-11100**, **FEAT-11300** (Release 1). Since this plan
> reconstructs a shipped system, no move changes what is built; it makes the buckets agree with the
> graph. Checked mechanically: no Feature is now bucketed before any prerequisite.
>
> **Amended 2026-10-23** (run #212, GDS ladder alignment sweep): the 8 new edges put two Features
> before a prerequisite — FEAT-1100 (Prototype) on FEAT-5300 (MVP), and FEAT-8100 (MVP) on
> FEAT-6200 (Release 1). Fixed by moving the prerequisites earlier: **FEAT-5300** MVP → Prototype
> (it has no prerequisites of its own) and **FEAT-6200** Release 1 → MVP (its prerequisites
> FEAT-6100 and FEAT-1500 are MVP). The three new Features, **FEAT-12100**, **FEAT-12200** and
> **FEAT-12300**, go to Release 1. Checked mechanically again: no Feature is bucketed before any
> prerequisite. Totals: 4 Prototype + 4 MVP + 29 Release 1 + 11 Release 2 = 48.

## Bucket assignments

### Prototype

| Feature | Justification |
|---|---|
| **FEAT-1100** Deterministic, Sub-Stepped Simulation Clock | The single load-bearing invariant (`CLAUDE.md` #1); nothing else in the catalog is buildable/testable without it. Foundational per the dependency graph. |
| **FEAT-1200** Orbital Propagation & Access-Window Geometry | Highest fan-out Feature in the catalog (10 direct dependents as of 2026-10-17); the geometric substrate every other Epic schedules against. |
| **FEAT-5300** Load-Time Vignette Validation *(moved from MVP, 2026-10-23)* | Must-priority; a dependency of FEAT-4100 — no session can start without a validated vignette. Now also a prerequisite of FEAT-1100 (`NFR-1610`, failure-atomic event application, builds on `NFR-1600`, robustness to invalid input), so it cannot sit after the Prototype clock. It has no prerequisites of its own. |
| **FEAT-7100** Ordered Event Log *(moved from MVP, 2026-10-17)* | Head of the catalog's critical path, and a prerequisite of FEAT-1100 itself — so it cannot sit in a later bucket than the Prototype clock. Its earlier MVP placement contradicted its own stated reason ("FEAT-1100 itself depends on it"). |

### MVP

| Feature | Justification |
|---|---|
| **FEAT-1500** Custody, Track Confidence & Weapons-Quality Gate | Must-priority; gates every engagement-intent action, a dependency of FEAT-3400 and FEAT-6200. |
| **FEAT-6100** SessionAPI Single Seam | Must-priority; the architectural boundary (ADR-0002/0003) that makes the engine UI-agnostic — needed before any UI-facing Feature can be built safely. |
| **FEAT-6200** Fog-of-War Filtering at the Session Boundary *(moved from Release 1, 2026-10-23)* | Must-priority, RTM-verified built (`session/cells.py`). FEAT-8100 (this bucket) now depends on it through `NFR-3010` (belief visibly distinct from truth, citing `FR-6210`): a console without its fog-of-war boundary is not a minimum viable trainer. Its prerequisites FEAT-6100 and FEAT-1500 are both MVP. |
| **FEAT-8100** Browser-Based Operator Console Presentation | Must-priority; without a presentation layer no other Feature is reachable by a human. *(2026-10-23)* Now depends on FEAT-6200 (MVP) and FEAT-1100 (Prototype) through its human-factors leaves `NFR-3010`/`NFR-3020`, so it is no longer buildable from day one. |

### Release 1

| Feature | Justification |
|---|---|
| **FEAT-2100–2500** (Bus SOH, Bus-Gates-Payload, Pass-Gated Telemetry, Payload-Type Actions, Safe-Mode Loop) | All Must-priority; RTM cites real built files for all five (`engine/bus.py`, `busmodel.py`, `buscommands.py`, `recovery.py`). Complete bus-operator training core, depends only on MVP-bucketed FEAT-1200. |
| **FEAT-3100–3200, 3400** (Plan-First Commands, SSN Tasking, Execute-Time Re-Validation) | All Must-priority, RTM-verified built (`engine/orders.py`, `engine/ssn.py`). |
| **FEAT-3300** Unified Planned-Activity Scheduler | Must-priority per requirements, but RTM Impl. Package is `UNASSIGNED` — placed here on priority/dependency grounds; the traceability gap itself is a Release-1-scoped verification task, not new development (see `05-feature-review.md`). |
| **FEAT-3500** Role-Scoped Command Catalog & Assignment Scoping | Must-priority; both included FRs show RTM `UNASSIGNED` — same verification-task framing as FEAT-3300. |
| **FEAT-4100, 4200, 4300, 4600, 4700** (Vignette Selection, Seat Assignment, Clock Control Authority, God-View/View-As, Manual Adjudication) | All Must-priority and narratively covered by the existing `FS-106-white-cell-dashboard.md` (confirming real, shipped White Cell control-plane functionality) despite `UNASSIGNED` RTM citations — placed at Release 1 on priority/narrative-coverage grounds, with the citation gap flagged as Release-1-scoped verification work. |
| **FEAT-5200** TLE Import with Manual/Keplerian Fallback | Must-priority, RTM-verified built; depends only on Prototype-bucketed FEAT-1200. |
| **FEAT-6300, 6400** (Lazy Clock/Locking, Hot-Seat/LAN Sharing) | All Must-priority, RTM-verified built (`session/manager.py`, `session/inprocess.py`); this is the entire P8 multiplayer transport. *(FEAT-6200, the fog-of-war boundary, moved to MVP 2026-10-23.)* |
| **FEAT-1300** Impulsive Maneuver & Δv Budget Accounting *(moved from MVP, 2026-10-17)* | Must-priority; the core resource-scarcity mechanic every order type checks. Now depends on FEAT-3100 (Release 1) through `FR-1320`'s plan-time purpose tags, so it cannot precede it. FEAT-3400 (Release 1) still depends on it — consistent. |
| **FEAT-1400** Five-D's Counterspace Effect Resolution *(moved from MVP, 2026-10-17)* | Must-priority; the doctrinal core of the simulator. Now depends on FEAT-3100/FEAT-3400 (Release 1) through `FR-1440`'s delivery-path jamming. Also carries the two unimplemented Must leaves `FR-1460`/`FR-1470` (resource bounds), which go to `06` next. |
| **FEAT-4400** Inject Authoring & Firing *(moved from Release 2, 2026-10-17)* | Must-priority and RTM-verified built. FEAT-2300 (Release 1) now depends on it through `FR-2320`, and its old Release-2 placement rested only on phase history (P4.5), so it moves up rather than pulling the bus-operator core back. Its prerequisites (FEAT-1100, 1200, 6100) are all earlier. Carries unimplemented `FR-4440` (Should) and `FR-4450` (Could). |
| **FEAT-5100** In-App Iterative Vignette Builder *(moved from MVP, 2026-10-17)* | Must-priority; built in Tranche 3 (`IP-1171`–`IP-1174`), not with the MVP core. Now depends on FEAT-4200 (Release 1) through `FR-5160`'s seat/role matrix. FEAT-4500 and FEAT-5200 depend on it, both in this bucket or later. |
| **FEAT-11100** Role-Scoped, Source-Anchored, Current Operator Manuals *(new 2026-10-17)* | Must-priority (`FR-11000` family) and already in place (`docs/training/`, run continuously since 2026-07-04). No Feature-level prerequisite; bucketed with the shipped core it documents. |
| **FEAT-11300** Vignette Learning Path & Verified Playbooks *(new 2026-10-17)* | Must-priority and in place (`training/16`, `test_vignette_tutorials.py`). Depends on FEAT-11100 and FEAT-4100, both Release 1 or earlier. |
| **FEAT-12100** Test-Origin Traceability & Major-Release Verification *(new 2026-10-23)* | Must-priority (`NFR-2820`, `NFR-3840`; `NFR-1510`/`NFR-2830` at each major release). Owner direction `BL-0310`. Prerequisites FEAT-1100 and FEAT-5300 are Prototype. Not yet implemented — the next `06` candidates include it. |
| **FEAT-12200** Automated Browser Verification of Load-Bearing Console Rules *(new 2026-10-23)* | Must-priority (`NFR-2840`), owner decision `BL-0304`. Prerequisites FEAT-8100 and FEAT-6200 are MVP. Not yet implemented. |
| **FEAT-12300** Documentation Integrity Checks *(new 2026-10-23)* | Must/Should leaves `NFR-3800`–`NFR-3830` (owner direction on `BL-0297`); needed before the build-spec/design retirement (`BL-0292`) can be checked. Prerequisite FEAT-11100 is Release 1. Not yet implemented. |
| **FEAT-7200, 7300** (Save/Resume, AAR Replay/Scrub/Branch-Compare) | Both Must-priority (branch-compare is Should for FR-7320 specifically), RTM-verified built (`session/manager.py`, `session/aar.py`). |

### Release 2

| Feature | Justification |
|---|---|
| **FEAT-9100** Doctrine-Preset-Driven AI-Red Automation | **Should**-priority by the requirements baseline's own explicit statement (FR-9110: "a vignette remains fully playable with a human-seated... Red cell; AI-Red is a valuable convenience... not a precondition for any vignette's playability") — the one Feature in the catalog whose own source requirement states it is not MVP/Release-1-critical, despite being the strategic review's single highest-priority *future* recommendation (FC-02/GAP-08 fog-of-war parity, which is explicitly **not** part of this Feature's baseline scope). |
| **FEAT-4500** Classification Banner | Must-priority per its FR, but this catalog's motivating audit found **zero** Feature Specification coverage anywhere in the existing corpus and an `UNASSIGNED` RTM citation — placed at Release 2 specifically to force a verification-then-documentation pass (confirm it is actually built, then close both the FS and RTM gaps) rather than let it continue riding silently inside another document. |
| **FEAT-6500** Observer Read-Only Access | Must-priority per its FR, same treatment as FEAT-4500 — one of the two capabilities this catalog's motivating audit specifically flagged as having no Feature Specification anywhere. |
| **FEAT-6600** Hot-Seat Hand-Off Screen-Blank Menu | Must-priority per its FR (closes GDS-05's own prior Open Question 1), same treatment — the second of the two audit-flagged gaps, and the deepest node on the catalog's critical path. |
| **FEAT-10100** Automated Non-Aggregating Competency Rubric Computation *(new 2026-07)* | **Should**-priority, same reasoning pattern as FEAT-9100 — valuable but not a precondition for any vignette's playability. Additionally gated on `MSTR-006` §3 authorization (forward-design, not yet implemented) independent of its now-resolved `ADR-0017` conflict (`ADR-0032`). |
| **FEAT-10200** Multi-Run/Cohort Structured Research-Data Export *(new 2026-07)* | **Should**-priority, depends on FEAT-10100 (same bucket, dependency-consistent). Additionally gated on `MSTR-006` §3 authorization and on `IP-2010` (FEAT-10100's implementation package) reaching `COMPLETE` first — its own now-resolved `ADR-0029` conflict (`ADR-0033`) does not remove either gate. |
| **FEAT-1600** Sensor Modality-Specific Access & Effectiveness Models *(new 2026-10-03)* | Six of its seven leaves (`FR-1610`-`FR-1660`) are `Should`-priority and already `VERIFIED` built — this Feature's bucket is driven by its one brand-new, unimplemented leaf, `FR-1670`, also `Should`-priority. Depends only on FEAT-1200 (Prototype-bucketed) — no dependency blocks Release 2. Additionally gated on `BL-0112`'s research grounding landing before `06-feature-specification` can design `FR-1670`'s concrete default range/degradation curve. |
| **FEAT-7400** State-Vector/Ephemeris & TLE Export *(new 2026-10-03)* | Three of its four leaves (`FR-7410`-`FR-7430`) are `Must`-priority and already `VERIFIED` built — this Feature's bucket is driven by its one brand-new, unimplemented leaf, `FR-7440`, `Should`-priority. Depends on FEAT-7100 (MVP-bucketed) and FEAT-6200 (Release-1-bucketed) — no dependency blocks Release 2. Additionally gated on `BL-0110`'s mean-element-fit design decision before `FR-7440` can be built. |
| **FEAT-5400** External Vignette Library Directories *(new 2026-10-17)* | **Should**-priority (`FR-5410`/`FR-5420`), built and verified (`IP-1180`). Same treatment as other Should-tier Features here. Depends only on FEAT-5300 (MVP). |
| **FEAT-5500** Save Running Session as a New Starting Vignette *(new 2026-10-17)* | **Should**-priority (`FR-5510`), built and verified (`IP-1200`). Depends on FEAT-5400 (this bucket) and FEAT-7200 (Release 1). |
| **FEAT-8200** Live RIC-Frame Relative-Motion View & CATS Overlay *(new 2026-10-03)* | **Should**-priority (both `FR-8210`/`FR-8220`), entirely unimplemented (RTM `UNASSIGNED`). Depends on FEAT-6200 (Release-1), FEAT-1200 (Prototype), and FEAT-8100 (MVP) — all already earlier-bucketed, so no dependency blocks Release 2. Additionally gated on `BL-0108`/`BL-0112`'s research grounding before `06-feature-specification` can design it. |

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
- **FEAT-8200** (Live RIC-Frame View & CATS Overlay, new 2026-10-03) — entirely unimplemented,
  with two open upstream research gaps (`BL-0108`, `BL-0112`) that must close before
  `06-feature-specification` can design it; the single newest and least-grounded Feature in the
  catalog.

### Foundational (critical path or blocking, per `04-feature-dependency-graph.md`)

FEAT-1200, FEAT-7100, FEAT-1100, FEAT-2100, FEAT-3100, FEAT-6200, and *(2026-10-23)* FEAT-5300 (now a co-head of the longest chain) — see the dependency graph's
"Blocking Features" table for fan-out counts. *(2026-10-17:)* FEAT-1300 and FEAT-3400 are now on
the longest chain too (FEAT-7100 → 1100 → 1200 → 3100 → 1300 → 3400 → 10100 → 10200).

### Optional (no other Feature depends on them — deferrable *within this graph* without blocking
anything; this is a dependency-graph property, not a statement about priority or value)

*(Recomputed from the graph 2026-10-17.)* FEAT-1400, FEAT-1600, FEAT-2300, FEAT-2400, FEAT-2500,
FEAT-3300, FEAT-3500, FEAT-4300, FEAT-4500, FEAT-4600, FEAT-5200, FEAT-5500, FEAT-6500, FEAT-6600,
FEAT-7400, FEAT-8200, FEAT-9100, FEAT-10200, FEAT-11300, and *(2026-10-23)* FEAT-12100, FEAT-12200, FEAT-12300. **Removed 2026-10-17** (each now has a
dependent): FEAT-4200 (FEAT-3400, FEAT-5100), FEAT-4400 (FEAT-2300), FEAT-4700 (FEAT-3400),
FEAT-7200 (FEAT-5500), FEAT-8100 (FEAT-8200 — already true since 2026-10-03, missed then). Several of these (e.g.
FEAT-2500 Safe-Mode Loop, FEAT-6600 Hot-Seat Hand-Off) are Must-priority, high-value Features in
their own right — "optional" here means only that no *sibling Feature's construction* is blocked
by deferring them, not that the capability itself is low-value. **FEAT-7300 removed from this
list (2026-07):** it now has a dependent (`FEAT-10100`) and is no longer a leaf node in the
dependency graph.

### Deferred

None within this catalog (see the "Future" bucket note above for why deferred-candidate items live
upstream of this catalog, not inside it).
