[← Build Spec index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 9. Non-functional requirements (NFR)

- **NFR-1 Offline:** the running application shall require **no network access**; only the
  scenario builder's optional TLE import touches the network (Space-Track), with documented
  fallbacks. (D2)
- **NFR-2 Hardware floor:** shall run acceptably on a **typical government laptop, integrated
  graphics, 16 GB RAM**, for scenarios up to ~24 satellites and the 6-channel window
  computation, at interactive frame rates in the 2D views.
- **NFR-3 Determinism:** identical `(initial state, action log, seed)` shall reproduce identical
  state (verified by state hashes); a property test shall enforce this. (FR-E2)
- **NFR-4 Performance:** window computation and state tick for ~24 satellites + sensors shall
  keep the UI responsive at time multipliers up to at least 600× without stalling the event loop
  (heavy propagation off the UI thread).
- **NFR-5 Security posture (research-grade):** standard secure development practices — input
  validation on all loaded files, no execution of scenario-embedded code, dependency pinning,
  least-privilege file access. No formal accreditation required for v1 (research tool), but no
  practice that would block later RMF/ITSG-33 review (e.g., no telemetry phone-home, no
  hard-coded secrets).
- **NFR-6 Robustness:** invalid scenario JSON or TLEs shall fail at load with a precise,
  actionable White Cell error; the running engine shall never crash on a *legal* operator action;
  illegal actions are blocked with explanation; tactically poor but legal actions run to their
  natural outcome. (§3.3)
- **NFR-7 Maintainability:** UI-agnostic engine with ≥80% unit-test coverage on engine logic;
  all content data-driven; the three fidelity seams (`Propagator`, `AccessProvider`,
  `EffectResolver`) documented and independently testable.
- **NFR-8 Portability:** Windows-first (typical CAF laptop), with no OS-specific dependencies
  that would prevent Linux/macOS dev use.
- **NFR-9 Accessibility:** affiliation/confidence conveyed by **shape/label, not color alone**;
  high-contrast presentation mode; keyboard shortcuts for common actions. (`09-gui-principles.md`)
- **NFR-10 Classification hygiene:** the White-Cell-selected banner renders on every screen and
  every exported file; default content is unclassified/fictional. (FR-W5)

---

## 10. Milestones & acceptance criteria

This section is the **authoritative phase plan** — it consolidates the previously separate
`08-build-roadmap.md` (now retired). It states the **milestone gates, acceptance criteria, and
current status** for each milestone. Requirement tags trace to §5/§9; remaining items live in
`docs/FUTURE-WORK.md`.

| Milestone | Delivers | Acceptance criteria (gate) | Status |
|---|---|---|---|
| **M0 Skeleton** | Repo, test harness, CI-style local checks, data loaders | Project builds; a trivial vignette JSON loads and validates; lint/test pipeline runs. | ✅ done |
| **M1 Deterministic core** | Clock, world state, action log, state hashing | **NFR-3** property test passes: replay reproduces identical hashes across a random action sequence. (FR-E1/E2, FR-L1) | ✅ done (`test_determinism.py` is the permanent gate) |
| **M2 Orbits & windows** | Propagator + AccessProvider (moderate) | For a known TLE + station, computed pass times match a reference (Skyfield) within tolerance; all six channel windows compute. (FR-E3/E4) | ✅ done (Skyfield-validated <1° agreement; all six channels + ISL) |
| **M3 Effects & SDA** | EffectResolver, TrackCatalog, custody decay, cyber exception | Jam denies a link in its footprint window; kinetic spawns debris + political consequence; cyber resolves outside any pass; custody decays/resets; weapons-quality gate blocks an under-tracked engagement. (FR-E6/E7/E8) | ✅ done |
| **M3.5 Bus & payload** | BusState SOH, payload gating, pass-gated telemetry, safe-mode induce | Battery drains in eclipse → red alarm; cyber induces safe mode per susceptibility dial; safe-mode discovered only at next pass via stored-telemetry dump; full storage blocks ISR collect. (FR-B1–B5) | ✅ done |
| **M4 Session & one vignette (headless)** | SessionManager, CellController/fog, RoleRegistry, in-process API | Scripted test plays **Vignette 1** to a win condition, then **rewinds and branches**; fog verified (Red cannot read Blue hidden state via API); roles scope asset access. (FR-W3/W6, OR-1/2, FR-E7) | ✅ done |
| **M4.5 Planning, tasking & recovery (headless)** | PlannedActivity scheduler, ISL/stored paths, sensor tasking, safe-mode recovery | Command queues to next pass *or* sooner via ISL; sensor tasking shrinks uncertainty and unlocks a gated engagement; multi-pass safe-mode recovery with **re-safe on persistent root cause**, then success after patch; `quick` dial → one-pass recovery. (FR-P1–P4, FR-B5) | ✅ done |
| **M5 GUI** | Web app: White Cell console, role-scoped operator console, **2D map + 3D globe**, SOH/telemetry, timeline, queue, inject panel, classification banner, hot-seat handoff | A facilitator runs **Vignette 1 entirely from the GUI**: loads it, switches cells, plans a command into a future pass, tasks a sensor, watches a jam degrade ISR and a satellite enter and recover from safe mode — with every disabled control explaining itself. (FR-W1/2/4/5, FR-S1–S3, OR-1–6, UR, **the demo DoD below**) | ✅ done (FastAPI + browser; backend paths test-covered; browser visual rendering unverified-headless — see `FUTURE-WORK.md` §8) |
| **M6 Content** | Remaining 7 vignettes as YAML; scenario tooling | All 8 vignettes load, pass validation, and are playable; real-TLE asset addition works; Red doctrine profiles selectable. (FR-S1–S3) | ✅ done (all 8 vignettes + TLE force-add + Red doctrine presets `china_integrated`/`russia_ew_first`/`generic`) |
| **M7 Logging, AAR & v2 seams** | Action-log persistence; AAR replay; documented seams for high fidelity, networking, constellation aggregation | Action log written at exercise end and proven sufficient to deterministically reconstruct the run offline; AAR scrubber + branch comparison; seam docs/scaffolds exist (no full v2 build). (FR-L1/L2, §3.2) | ◻️ partial — action log + AAR scrubber + branch compare ✅; the **high-fidelity propagator swap** and **LAN multiplayer transport** seam-proofs (formerly Phase 8) are scaffolded only — see `FUTURE-WORK.md` §1, §2, §4. |

### 10.1 Definition of Done — first demo (single named scenario)
**Vignette 1 "LEO ISR Denial," 2 Blue seats + 2 Red seats + 1 White, hot-seat on one laptop:**
White Cell builds the scenario (TLEs from Space-Track or bundled), assigns the four operator
roles by checkbox (incl. a split Blue ISR bus vs. payload seat), sets classification, and starts
the wall clock. Blue plans imaging + downlink across passes and tasks an SDA sensor; Red plans a
downlink jam and a cyber effect that induces **safe mode** on a Blue ISR satellite. Blue notices
the payload stop, **confirms safe mode at the next pass**, runs a recovery, and is briefly
**re-safed** until the root cause is addressed. Seats hand off via **screen blank**; White Cell
**pauses** once for a timeout and **rewinds** once to re-run a decision. The action log is
written at the end. **If all of that works from the GUI, v1 is a success.**

### 10.2 v1 definition-of-done — checklist

The seven gates the v1 PME tool must meet (consolidated from the retired roadmap):

1. Deterministic engine with exact rewind/undo/branch (`test_determinism.py` permanent gate). ✅
2. Moderate-fidelity orbits + all six access-window channels + TLE. ✅
3. Full order/effect/cyber/custody model with the five-D's resolver and debris/escalation. ✅
4. Session layer with fog-of-war and the in-process `SessionAPI`. ✅
5. A working UI: world map + 3D globe, pass timelines, countdowns, order queue, fleet rail,
   subsystem drill-down with command-verb buttons, recovery strip, and the full White-Cell
   surface (time travel, injects, AAR scrubber). ✅ — see §16.
6. All eight vignettes loadable and tunable; fictional defaults plus real-TLE asset addition. ✅
7. **Clean seams** proven for high fidelity and LAN multiplayer. ◻️ scaffolded (engine/UI
   separation enforced by the import-guard test, `SessionAPI` Protocol exists), full
   seam-proofs in `FUTURE-WORK.md` §1 & §2.

---

## 11. Risks & mitigations

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Wall-clock + heavy propagation stalls the UI | Sluggish, unusable at high multipliers | Med | Propagation off the UI thread; cache windows; precompute upcoming passes; NFR-4 gate. |
| Determinism broken by hidden nondeterminism (dict order, floats, RNG) | Rewind/replay diverge; v2 replay impossible | Med | Single seeded RNG; ordered structures; state hashing in CI; NFR-3 property test from M1. |
| Hot-seat fog leaks (one role sees another's private data) | Training value destroyed | Med | Enforce fog in the engine `CellView`, not the UI; test that the API itself withholds data (M4). |
| Scope creep into 3D/networking/replay too early | v1 slips | High | Hard non-goals (§3.2); seams documented but not built; demo DoD is the bar. |
| Space-Track unavailable or auth changes | Can't seed real TLEs | Med | Bundled snapshot + manual entry + Keplerian synthesis; runtime never needs network (D2). |
| Moderate-fidelity orbits look "wrong" to STK-savvy users | Credibility loss | Med | Validate pass times vs. Skyfield (M2); document fidelity explicitly; J2 included for realistic ground-track drift. |
| Safe-mode mechanic dominates play | Skews training | Low (now mitigated) | Tunable dials + detection/recovery counterplay (`12-safe-mode-loop.md`); default `realistic`. |
| Single maintainer (Claude Code) context loss between phases | Inconsistent build | Med | This PSD + companion docs as durable spec; per-phase acceptance gates; tests encode intent. |

---

## 12. Glossary

- **Access window** — interval when an actor asset can interact with a target via a channel.
- **AAR** — After-Action Review (v2 replay + CSV export).
- **Bus** — the spacecraft vehicle (power, attitude, thermal, propulsion, C&DH, comms).
- **Custody** — current knowledge of an object's location/state; decays without observation.
- **ECI / RIC** — Earth-Centered Inertial frame / Radial-In-track-Cross-track relative frame.
- **Hot seat** — one terminal shared by many roles, swapped in turn.
- **ISL** — Inter-Satellite Link (crosslink); a rare faster command path.
- **PlannedActivity** — unified scheduled command or collection task.
- **Payload** — the mission equipment (SATCOM, ISR, SIGINT, SDA, space-control, etc.).
- **Safe mode** — protective state that disables the payload; reversible; inducible by attack.
- **SDA** — Space Domain Awareness; the belief state from which views are rendered.
- **SOH** — State of Health (the bus health picture operators monitor).
- **The five D's** — deceive, disrupt, deny, degrade, destroy (effect outcomes).
- **TLE** — Two-Line Element set (orbital state from Space-Track or manual entry).
- **Weapons-quality track** — custody good enough (confidence + characterization) to engage.

---

*End of Project Start Document. Companion design files provide implementation detail; this PSD
is the baseline of record for v1 scope, requirements, and acceptance.*

---
