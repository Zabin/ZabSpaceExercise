# Non-Functional Requirements Baseline

> **Status:** Draft — amended (strategic-review reconciliation, 2026-07; no numbered NFR added or
> modified — see "Strategic review reconciliation" section near the end of this document and
> [`reviews/requirements-update-report.md`](../reviews/requirements-update-report.md)); further
> amended (DOM-002/004/005 backfill, 2026-07; no numbered NFR added, no new Candidate NFR added —
> see "DOM-002/004/005 backfill" section near the end of this document and
> [`reviews/requirements-domain-backfill-report.md`](../reviews/requirements-domain-backfill-report.md));
> further amended (`ADR-0032`/`ADR-0033` conflict resolution, 2026-07; `01-functional-requirements.md`
> gained two new baselined FR leaves — `FR-10110`, `FR-10210` — this document gained none; the ADR
> range below was updated).
> **Authoritative inputs:**
> [`build-spec/04-nfr-milestones-and-risks.md`](../build-spec/04-nfr-milestones-and-risks.md) §9
> (NFR-1…NFR-10 — the legacy, pre-GDS NFR tag scheme),
> [`architecture/03-architecture.md`](../architecture/03-architecture.md) (GDS-03, System
> Architecture), [`architecture/02-system-context.md`](../architecture/02-system-context.md)
> (GDS-02, System Context), [`architecture/04-domain-model.md`](../architecture/04-domain-model.md)
> (GDS-04), [`architecture/05-functional-requirements.md`](../architecture/05-functional-requirements.md)
> (GDS-05), [`requirements/01-functional-requirements.md`](01-functional-requirements.md)
> (FR-1xxx baseline), [`design/05-interface-control-document.md`](../design/05-interface-control-document.md)
> (ICD), [`training/01-install-and-run.md`](../training/01-install-and-run.md) (configuration
> surface), [`architecture/adr/INDEX.md`](../architecture/adr/INDEX.md) (ADR-0001 through ADR-0033,
> all `Accepted` except `ADR-0029`, `Superseded` by `ADR-0033`), [`architecture/strategic-assumptions-register.md`](../architecture/strategic-assumptions-register.md)
> (added 2026-07).
> **Priority scale used throughout:** MoSCoW (Must / Should / Could / Won't), matching
> `requirements/01-functional-requirements.md`.
> **Field set used (per explicit instruction for this baseline — narrower than this skill's own
> default field list):** ID, Description, Rationale, Metric or verification method, Priority,
> Affected subsystems, Dependencies, Source documents, Related ADRs.

## A note on a pre-existing requirement tag scheme — read before using this document

`docs/build-spec/04-nfr-milestones-and-risks.md` §9 contains a legacy, pre-GDS
non-functional-requirement tag scheme: **NFR-1** (Offline) through **NFR-10** (Classification
hygiene). Per `CLAUDE.md`'s "Authoritative source & reading order," GDS-06 (Non-Functional
Requirements) — the architecture-ladder level that would eventually supersede build-spec/04 §9 the
way GDS-05 superseded build-spec/02 §5–6 — **has not been authored** (it remains
`⛔ Planned (scaffold only)`, per `architecture/INDEX.md` §1). **Corrected 2026-07** (see
`reviews/requirements-update-report.md`): per `CLAUDE.md`'s current text, an unauthored GDS level's
corresponding build-spec module is "deprecated legacy reference, not a binding tie-breaker" — the
prior wording here ("Build-spec/04 §9 therefore remains the binding NFR statement") predates that
blanket-supersession declaration and is corrected to match it, mirroring
[`ADR-0031`](../architecture/adr/ADR-0031-governance-record-consistency.md)'s identical fix to
`architecture/00-vision.md` §7. Build-spec/04 §9 is read here only because GDS-06 has authored
nothing yet to read instead — not because it binds.

This document is a hierarchical, traceable **elaboration** of that legacy tag scheme, in the same
non-competing relationship `requirements/01-functional-requirements.md` holds with build-spec/02 §5
(see that document's own header note, also corrected 2026-07). Each `NFR-1xxx`-series requirement
below is cross-referenced to its corresponding build-spec `NFR-N` tag in its **Source documents**
field where a correspondence exists, for historical traceability only; the traceability scaffolding
(Rationale, Metric/verification method, Dependencies, Related ADRs) this document adds is what the
build-spec's terse tag list does not itself carry, not evidence the tag "binds." Any apparent
conflict between an `NFR-1xxx` requirement below and its corresponding build-spec tag is **not** a
finding for this document to resolve — it is recorded under "Open issues" in the completion report.

This document is accompanied by a Requirements Traceability Matrix
([`03-requirements-traceability-matrix.md`](03-requirements-traceability-matrix.md)); a separate
standalone Requirements Review document was not produced for this baseline (see
[`../reviews/requirements-review.md`](../reviews/requirements-review.md) and
[`../reviews/requirements-baseline-review.md`](../reviews/requirements-baseline-review.md) for the
review passes actually run against it).

---

## 1. Performance

- **NFR-1100 — Responsive UI at high time-multipliers**
  - **Description:** The system shall keep the operator UI responsive (no stalled event loop) while
    advancing the simulation clock at multipliers up to at least 600× for scenarios of the
    documented sizing guideline (~24 satellites, all six access channels).
  - **Rationale:** White Cell routinely fast-forwards through quiet periods between contacts;
    a stalling UI breaks the hot-seat workflow and the wall-clock-driven training experience.
  - **Metric or verification method:** Demonstration/Test — `build-spec/04` NFR-4's existing
    acceptance framing (heavy propagation kept off the UI thread); no numeric latency target
    (e.g. ms frame budget) is stated in any source document, so none is asserted here.
  - **Priority:** Must
  - **Affected subsystems:** `engine/` (propagator, access provider), `session/` (clock
    catch-up), `ui_web/` (client poll loop)
  - **Dependencies:** NFR-1200 (hardware floor)
  - **Source documents:** `build-spec/04-nfr-milestones-and-risks.md` §9 NFR-4; §11 Risks row
    "Wall-clock + heavy propagation stalls the UI"
  - **Related ADRs:** ADR-0009 (moderate orbital fidelity), ADR-0014 (lazy-clock multiplayer)

- **NFR-1200 — Hardware-floor performance**
  - **Description:** The system shall run at interactive frame rates in the 2D views on a typical
    government laptop with integrated graphics and 16 GB RAM, for scenarios up to the documented
    sizing guideline.
  - **Rationale:** v1's deployment context is White-Cell-owned hardware in a training room, not a
    provisioned server; the tool must not require specialized graphics hardware.
  - **Metric or verification method:** Demonstration on reference hardware class; no numeric frame
    rate is stated in the source, so "interactive" is asserted qualitatively per the source wording.
  - **Priority:** Must
  - **Affected subsystems:** `ui_web/` (globe.js, world.js, graph.js rendering)
  - **Dependencies:** None
  - **Source documents:** `build-spec/04-nfr-milestones-and-risks.md` §9 NFR-2
  - **Related ADRs:** ADR-0019 (sizing guideline, not engine cap), ADR-0020 (tech stack)

## 2. Scalability

- **NFR-1300 — Sizing is a soft guideline, not an engine-enforced cap**
  - **Description:** The engine shall not hard-cap the number of satellites or constellation size a
    vignette may define; the ~24-satellite / ≤3-sat-constellation figures are sizing guidance for
    typical White-Cell hardware, not an enforced limit.
  - **Rationale:** Per ADR-0019, enforcing a hard cap would block legitimate larger user-authored
    vignettes; the actual operational signal for "too big for this hardware" is observed clock lag,
    not a count.
  - **Metric or verification method:** Inspection of `engine/` for absence of a hard satellite-count
    gate; Test — `SessionManager._record_catch_up_lag` watchdog fires a warning when the host
    falls behind real time, in place of a hard cap.
  - **Priority:** Must
  - **Affected subsystems:** `engine/`, `session/` (clock-lag watchdog)
  - **Dependencies:** NFR-1100
  - **Source documents:** `CLAUDE.md` "Key facts"; `architecture/adr/ADR-0019-sizing-guideline-not-engine-cap.md`
  - **Related ADRs:** ADR-0019

- **NFR-1400 — LAN multiplayer concurrency ceiling is a documented, untested estimate**
  - **Description:** The per-session `RLock` serialization model is designed around a LAN
    concurrency model of roughly 16 participants; this figure is a documented estimate, not a
    load-tested guarantee, and no finer-grained locking has been adopted in v1.
  - **Rationale:** ADR-0026 explicitly records that no load test was run to validate the ~16
    figure and that the contention ceiling is accepted as a known, documented limitation rather
    than engineered around in v1.
  - **Metric or verification method:** Inspection — ADR-0026's own Consequences section is the
    verification record; no automated load test exists, and none is required by any source
    document for v1.
  - **Priority:** Should
  - **Affected subsystems:** `session/inprocess.py` (`_locked` critical section), `ui_web/server.py`
  - **Dependencies:** NFR-1100
  - **Source documents:** `architecture/adr/ADR-0026-rlock-lan-scaling-ceiling.md`
  - **Related ADRs:** ADR-0026, ADR-0014

## 3. Reliability

- **NFR-1500 — Determinism (replay/rewind/branch exactness)**
  - **Description:** Replaying the identical tuple of (initial state, ordered action log, seed)
    shall reproduce byte-identical state at every tick, verified by state hashes, enforced by a
    permanent property test.
  - **Rationale:** Determinism is what makes rewind, undo, branch-to-live, and AAR replay exact
    rather than approximate; it is the single load-bearing invariant the whole engine design rests
    on.
  - **Metric or verification method:** Test — `spacesim/tests/test_determinism.py`, the canonical
    permanent gate cited by `build-spec/04` NFR-3, must remain green on every commit.
  - **Priority:** Must
  - **Affected subsystems:** `engine/` (all modules — no wall-clock reads, no global RNG outside
    `rng.py`), `engine/eventlog.py`, `engine/simulation.py`
  - **Dependencies:** None
  - **Source documents:** `build-spec/04-nfr-milestones-and-risks.md` §9 NFR-3; `CLAUDE.md`
    "Load-bearing invariants" #1
  - **Related ADRs:** ADR-0002 (deterministic core)

- **NFR-1600 — Robustness to invalid input and illegal actions**
  - **Description:** Invalid scenario JSON or TLEs shall fail at load with a precise, actionable
    White Cell error; the running engine shall never crash on a legal operator action; illegal
    actions are blocked with an explanation; tactically poor but legal actions are allowed to run to
    their natural outcome.
  - **Rationale:** A facilitator-run training tool cannot stop the exercise on a crash; errors must
    be recoverable and explainable in the room, not just logged.
  - **Metric or verification method:** Test — scenario-load validation tests; order-validation
    (`dry_run()`) tests asserting illegal actions are rejected with a reason and legal actions never
    raise.
  - **Priority:** Must
  - **Affected subsystems:** `content/vignette.py` (load/validate), `engine/orders.py`
    (validate/dry_run)
  - **Dependencies:** NFR-1500
  - **Source documents:** `build-spec/04-nfr-milestones-and-risks.md` §9 NFR-6, §3.3
  - **Related ADRs:** None identified

- **NFR-1700 — Sub-stepped clock advancement**
  - **Description:** The simulation clock shall advance to the next scheduled event, never skipping
    past it, even at high time multipliers — never a naive large fixed step.
  - **Rationale:** A naive large step at 600× would skip short LEO passes and silently break
    realism without any visible error.
  - **Metric or verification method:** Test — scheduler/event-ordering tests verifying no scheduled
    event is skipped across a range of time multipliers.
  - **Priority:** Must
  - **Affected subsystems:** `engine/clock.py` (`SimClock`, `Scheduler`)
  - **Dependencies:** NFR-1500
  - **Source documents:** `CLAUDE.md` "Load-bearing invariants" #5
  - **Related ADRs:** ADR-0002

## 4. Availability

- **NFR-1800 — Single-sitting, single-process exercise availability**
  - **Description:** v1 is designed to run a single exercise per process instance, for the duration
    of one sitting; there is no mid-exercise save/resume across process restarts in v1 (the
    `/save`/`/aar` ground-truth dump is for end-of-exercise/AAR use, not crash recovery).
  - **Rationale:** This is the documented v1 scope boundary; the source material frames anything
    beyond single-sitting availability (cross-restart resume, multi-exercise-per-process) as
    explicitly deferred.
  - **Metric or verification method:** Inspection — `build-spec/01-context-and-scope.md`'s decision
    log lists "Save/resume mid-exercise" as v2-deferred; no v1 acceptance criterion requires
    crash-recoverable availability beyond the running process's lifetime.
  - **Priority:** Should
  - **Affected subsystems:** `session/` (`SessionManager`)
  - **Dependencies:** None
  - **Source documents:** `build-spec/01-context-and-scope.md` (decision log, "Save / resume
    mid-exercise" row); `architecture/05-functional-requirements.md` OR-6
  - **Related ADRs:** None identified

  > **Open issue flagged, not resolved here:** GDS-05's own Open Questions (OQ2) already note an
  > unresolved tension between OR-6's "single exercise per process" wording and the shipped
  > `/api/sessions` multi-session discovery endpoint (P8 LAN multiplayer). This NFR restates the
  > documented v1 boundary as written rather than resolving that tension; see GDS-05 OQ2 for the
  > open question of record.

## 5. Maintainability

- **NFR-1900 — UI-agnostic engine with enforced test coverage**
  - **Description:** The simulation engine shall remain UI-agnostic (no UI or transport imports in
    `engine/`, enforced by an import guard) and shall carry at least 80% unit-test coverage on
    engine logic.
  - **Rationale:** Keeping the engine importable and testable independent of any UI is what allows
    the documented v2 seams (high-fidelity propagator swap, alternate front ends) without a
    rewrite.
  - **Metric or verification method:** Test — `spacesim/tests/test_import_guard.py` (AST-scans
    `engine/` for forbidden imports); coverage tool run against `engine/` reporting ≥80%.
  - **Priority:** Must
  - **Affected subsystems:** `engine/` (all modules), test suite
  - **Dependencies:** NFR-1500
  - **Source documents:** `build-spec/04-nfr-milestones-and-risks.md` §9 NFR-7; `CLAUDE.md`
    "Load-bearing invariants" #2
  - **Related ADRs:** ADR-0002, ADR-0007 (content-as-data)

- **NFR-2000 — Content as data, not code**
  - **Description:** Vignettes, asset templates, and effect templates shall be data files (YAML),
    not Python; scenario-specific logic shall not leak into engine code.
  - **Rationale:** Keeps new vignette authoring a content task rather than a code change, and keeps
    the engine's tested surface stable as the content library grows.
  - **Metric or verification method:** Inspection — `spacesim/content/vignettes/*.yaml` contains no
    embedded executable scenario logic; new vignettes added without engine code changes.
  - **Priority:** Must
  - **Affected subsystems:** `content/vignette.py`, `content/vignettes/*.yaml`
  - **Dependencies:** None
  - **Source documents:** `CLAUDE.md` "Load-bearing invariants" #6
  - **Related ADRs:** ADR-0007

## 6. Extensibility

- **NFR-2100 — Independently testable fidelity seams**
  - **Description:** The three fidelity seams — `Propagator`, `AccessProvider`, `EffectResolver` —
    shall be documented interfaces, independently testable, so a higher-fidelity implementation can
    be substituted later without changing call sites.
  - **Rationale:** v1 deliberately ships moderate-fidelity orbital mechanics; the seam is what makes
    a future high-fidelity propagator swap (already scaffolded as `HighFidelityPropagator`) a
    substitution rather than a rewrite.
  - **Metric or verification method:** Inspection — each interface has a documented contract and a
    dedicated test module exercising it independent of the others; Demonstration — the
    `HighFidelityPropagator` stub in `engine/propagator.py` satisfies the `Propagator` interface
    without engine changes elsewhere.
  - **Priority:** Should
  - **Affected subsystems:** `engine/propagator.py`, `engine/access.py`, `engine/effects.py`
  - **Dependencies:** NFR-1900
  - **Source documents:** `build-spec/04-nfr-milestones-and-risks.md` §9 NFR-7; `CLAUDE.md`
    "Orbital fidelity" key fact; `FUTURE-WORK.md` §2
  - **Related ADRs:** ADR-0009

## 7. Security

- **NFR-2200 — Research-grade secure development practice**
  - **Description:** The system shall follow standard secure development practices — input
    validation on all loaded files, no execution of scenario-embedded code, dependency pinning,
    least-privilege file access — without requiring formal accreditation in v1, while avoiding any
    practice that would block a later RMF/ITSG-33 review (no telemetry phone-home, no hard-coded
    secrets).
  - **Rationale:** This is a research/training tool, not an accredited system, but the source
    material is explicit that v1 choices should not foreclose a future formal review.
  - **Metric or verification method:** Inspection — scenario loader rejects/validates rather than
    `eval`s content; dependency versions pinned in the project's dependency manifest; no outbound
    telemetry call exists in `engine/`/`session/`/`ui_web/` except the documented optional
    Space-Track TLE import.
  - **Priority:** Must
  - **Affected subsystems:** `content/vignette.py` (load/validate), all subsystems (no
    scenario-embedded code execution)
  - **Dependencies:** NFR-2300
  - **Source documents:** `build-spec/04-nfr-milestones-and-risks.md` §9 NFR-5
  - **Related ADRs:** ADR-0018 (offline-first runtime)

- **NFR-2300 — Documented LAN trust boundary (client-side cell selection)**
  - **Description:** Cell selection (White/Blue/Red) is client-side trust with no per-cell
    authentication; fog-of-war filtering is enforced server-side at the `SessionAPI`/
    `CellController` boundary for cell-scoped endpoints, but ground-truth endpoints (`/godview`,
    `/eventlog`, `/save`, `/aar*`, `/objectives`) deliberately expose ground truth without a cell
    binding. This is an accepted v1 trust boundary for a trusted, cooperative LAN deployment, not a
    defect to silently harden.
  - **Rationale:** ADR-0015 explicitly accepts this exploitable-by-a-hostile-LAN-participant
    boundary as appropriate for the v1 PME training context (everyone in the room is cooperating),
    and names per-cell tokens as a deferred hardening option rather than a v1 requirement.
  - **Metric or verification method:** Inspection — ADR-0015's own Consequences section and
    `docs/AUDIT-2026-06.md` §D5/§F1 are the recorded verification; no penetration test is required
    or claimed for v1.
  - **Priority:** Must (as a *documented* boundary — hardening itself is explicitly Won't for v1)
  - **Affected subsystems:** `session/api.py` (`SessionAPI`, `CellView`), `ui_web/server.py`
  - **Dependencies:** None
  - **Source documents:** `CLAUDE.md` "LAN trust model (load-bearing)"; `architecture/adr/ADR-0015-lan-trust-model.md`;
    `AUDIT-2026-06.md` §D5, §F1
  - **Related ADRs:** ADR-0015

  > **Tension flagged, not resolved here:** NFR-2200's "no practice that would block later
  > RMF/ITSG-33 review" and NFR-2300's accepted unauthenticated cell-selection boundary sit in
  > tension with each other at a future-accreditation horizon (an unauthenticated fog-of-war
  > boundary is a likely RMF finding). Both source documents (build-spec/04 §9 NFR-5 and ADR-0015)
  > are internally consistent on their own terms for v1; this document flags the forward tension
  > for whoever scopes a v2 accreditation effort rather than resolving it unilaterally.

## 8. Data integrity

- **NFR-2400 — State-hash-verified determinism as the data-integrity mechanism**
  - **Description:** The system's data-integrity guarantee for simulation state is the same
    determinism property as NFR-1500: state hashes verify that no silent state corruption occurs
    across replay, rewind, undo, or branch.
  - **Rationale:** There is no separate data-integrity mechanism described in the source material
    beyond determinism + state hashing; treating it as a distinct NFR makes the data-integrity
    claim explicit rather than leaving it implicit inside Reliability.
  - **Metric or verification method:** Test — same `test_determinism.py` gate as NFR-1500, read for
    its data-integrity property (state hash equality) rather than its reliability property
    (reproducibility).
  - **Priority:** Must
  - **Affected subsystems:** `engine/eventlog.py` (`Snapshot`, state hashing), `engine/world.py`
  - **Dependencies:** NFR-1500
  - **Source documents:** `build-spec/04-nfr-milestones-and-risks.md` §9 NFR-3
  - **Related ADRs:** ADR-0002

- **NFR-2500 — Action log sufficiency for reconstruction**
  - **Description:** The action log shall be sufficient to deterministically reconstruct the
    exercise offline, and shall be written to disk at exercise end.
  - **Rationale:** This is the foundation for AAR replay, branch comparison, and any future
    branch-to-live capability; an incomplete log breaks all of them silently.
  - **Metric or verification method:** Test — AAR replay/scrub tests reconstructing a full exercise
    from its persisted action log and verifying state-hash equality against the live run.
  - **Priority:** Must
  - **Affected subsystems:** `engine/eventlog.py`, `session/aar.py`
  - **Dependencies:** NFR-2400
  - **Source documents:** `architecture/05-functional-requirements.md` FR-L1/FR-L2;
    `build-spec/04-nfr-milestones-and-risks.md` §10 M7
  - **Related ADRs:** ADR-0002

## 9. Observability

- *(none derivable from inputs — see Candidate Requirements)*

## 10. Logging

- **NFR-2600 — Complete, ordered, timestamped action log**
  - **Description:** Every state-changing event (orders, executions, effects, injects,
    white-controls, time-controls) shall be appended to an ordered, timestamped action log.
  - **Rationale:** The log is both the reliability/data-integrity foundation (NFR-2500) and the
    facilitator's manual-adjudication evidence base — ADR-0017 records that v1 has no automated
    scoring, so the action log + AAR replay is the only record White Cell adjudicates from.
  - **Metric or verification method:** Test — every order/effect/inject/control-plane mutation in
    the engine produces a corresponding `EventLogEntry`; verified by the existing event-log test
    suite.
  - **Priority:** Must
  - **Affected subsystems:** `engine/eventlog.py`, `engine/orders.py`, `engine/handlers.py`
  - **Dependencies:** NFR-2500
  - **Source documents:** `architecture/05-functional-requirements.md` FR-L1;
    `architecture/adr/ADR-0017-manual-adjudication.md`
  - **Related ADRs:** ADR-0017, ADR-0002

## 11. Configuration

- **NFR-2700 — File-based server configuration with override**
  - **Description:** Host, port, and reload behavior for the web server shall be configurable via a
    single YAML file at the repository root (`spacesim.config.yaml`), with its path overridable via
    an environment variable (`SPACESIM_CONFIG`), without requiring a code change.
  - **Rationale:** White Cell facilitators (not developers) need to change the bind address (e.g.
    to expose on a LAN) without editing source.
  - **Metric or verification method:** Demonstration — editing `spacesim.config.yaml`'s `host`/
    `port`/`reload` keys and re-running `python3 -m spacesim.ui_web` changes server bind behavior
    accordingly; `SPACESIM_CONFIG` pointed at an alternate file is honored.
  - **Priority:** Should
  - **Affected subsystems:** `spacesim/config.py`, `spacesim/ui_web/server.py`
  - **Dependencies:** None
  - **Source documents:** `training/01-install-and-run.md` (configuration section); `CLAUDE.md`
    "Server config."
  - **Related ADRs:** None identified

## 12. Testing

- **NFR-2800 — Test-driven, gated build process**
  - **Description:** Every build phase shall be developed test-first, with the Phase-1 determinism
    property test as a permanent, never-relaxed gate; the full suite shall be run and kept green
    before every commit.
  - **Rationale:** With a single maintainer and a deterministic core whose entire value proposition
    rests on exactness, test-first discipline and a permanent gate are how regressions are caught
    immediately rather than discovered later as a broken rewind.
  - **Metric or verification method:** Test — `python3 -m pytest` (full suite) and
    `python3 -m pytest spacesim/tests/test_determinism.py` (the permanent gate) both report all
    green prior to any commit, per the project's mandatory workflow.
  - **Priority:** Must
  - **Affected subsystems:** All (`spacesim/tests/`)
  - **Dependencies:** NFR-1500, NFR-1900
  - **Source documents:** `CLAUDE.md` "Test-driven workflow (mandatory)"; `build-spec/06-test-plan-and-schedule.md`
  - **Related ADRs:** ADR-0002

## 13. Portability

- **NFR-2900 — Windows-first, cross-platform development**
  - **Description:** The system shall be Windows-first (the typical target laptop), with no
    OS-specific dependency that would prevent Linux/macOS use for development.
  - **Rationale:** The deployment target is government-issued Windows laptops, but the maintainer's
    development environment is not constrained to Windows; the dependency set must work on both.
  - **Metric or verification method:** Inspection — the documented dependency list (`pydantic`,
    `numpy`, `sgp4`, `pyyaml`, `pytest`, `hypothesis`, `skyfield`, `fastapi`, `uvicorn`, `httpx`)
    contains no OS-specific package; Demonstration — install/run instructions are verified on more
    than one OS in `training/01-install-and-run.md`.
  - **Priority:** Must
  - **Affected subsystems:** Build/dependency manifest, `spacesim/` (no OS-specific imports)
  - **Dependencies:** None
  - **Source documents:** `build-spec/04-nfr-milestones-and-risks.md` §9 NFR-8
  - **Related ADRs:** ADR-0020 (tech stack)

## 14. Usability

- **NFR-3000 — Accessible presentation (shape/label, not color alone)**
  - **Description:** Affiliation and confidence shall be conveyed by shape and label, not color
    alone; a high-contrast presentation mode shall be available; common actions shall have keyboard
    shortcuts.
  - **Rationale:** A training tool used by varied personnel under time pressure must not depend on
    color discrimination alone for safety/affiliation-critical information.
  - **Metric or verification method:** Inspection — `ui_web` symbology uses distinct shapes/labels
    per affiliation independent of color; Demonstration — high-contrast presentation mode toggles
    correctly; keyboard nav (`j/k/c/g`) functions for documented common actions.
  - **Priority:** Should
  - **Affected subsystems:** `ui_web/static/` (`app.js`, `style.css`, `globe.js`)
  - **Dependencies:** None
  - **Source documents:** `build-spec/04-nfr-milestones-and-risks.md` §9 NFR-9;
    `design/09-gui-principles.md`
  - **Related ADRs:** None identified

- **NFR-3100 — Classification banner on every screen and export**
  - **Description:** The White-Cell-selected classification banner shall render on every screen and
    on every exported file; default content shall be unclassified/fictional.
  - **Rationale:** This is a PME training tool that must never be mistaken for, or leak the
    appearance of, real classified material.
  - **Metric or verification method:** Inspection — every UI view and export path renders the
    active banner string; default vignette content carries no real classification marking.
  - **Priority:** Must
  - **Affected subsystems:** `ui_web/static/` (banner component), `session/aar.py` (export paths)
  - **Dependencies:** None
  - **Source documents:** `build-spec/04-nfr-milestones-and-risks.md` §9 NFR-10;
    `architecture/05-functional-requirements.md` FR-W5
  - **Related ADRs:** None identified

## 15. Interoperability

- **NFR-3200 — TLE import from Space-Track with offline fallback**
  - **Description:** The scenario builder shall import TLEs from Space-Track.org at build time when
    reachable, and shall otherwise accept manual TLE entry/paste; after scenario creation, no
    network access shall be required to run the exercise.
  - **Rationale:** Space-Track is the only named external system in GDS-02's system context; the
    runtime must not depend on it being reachable, since training rooms may be offline or
    air-gapped.
  - **Metric or verification method:** Test — scenario builder succeeds with manually pasted TLEs
    when Space-Track is unreachable; a built scenario runs with no outbound network call.
  - **Priority:** Must
  - **Affected subsystems:** `content/` (TLE import), scenario builder UI
  - **Dependencies:** None
  - **Source documents:** `architecture/02-system-context.md` (external systems table);
    `build-spec/04-nfr-milestones-and-risks.md` §9 NFR-1; `architecture/05-functional-requirements.md`
    FR-S2
  - **Related ADRs:** ADR-0018 (offline-first runtime)

- **NFR-3300 — Browser-only client, no external identity/LMS/scoring integration**
  - **Description:** The client surface shall be a standard browser reachable over HTTP(S) from the
    FastAPI server; the system shall not integrate with any external identity provider, learning
    management system, or scoring service in v1.
  - **Rationale:** GDS-02 explicitly enumerates the system's external boundary and confirms no such
    integrations exist or are planned for v1 — stated here as an interoperability *boundary*, not a
    gap.
  - **Metric or verification method:** Inspection — GDS-02 §2–§4's external-actor and
    external-software tables name only Space-Track, the local filesystem, and browser clients; no
    LMS/IdP/scoring-service client code exists in `spacesim/`.
  - **Priority:** Must
  - **Affected subsystems:** `ui_web/server.py`
  - **Dependencies:** NFR-3200
  - **Source documents:** `architecture/02-system-context.md` §2–§4
  - **Related ADRs:** None identified

---

## Candidate Requirements

Items that read as non-functional requirements but do not trace to an approved source document.
Explicitly excluded from the numbered baseline above.

- **CNFR-01 — Observability (metrics/dashboards/tracing)**
  - **Description (candidate):** The system might benefit from structured runtime metrics (e.g.
    per-tick processing time, lock-wait time, memory) exposed for operational monitoring during an
    exercise.
  - **Why excluded:** No source document (build-spec/04 §9, GDS-02/03, any Accepted ADR) describes
    any metrics/telemetry/tracing surface. The clock-lag watchdog (`_record_catch_up_lag`, ADR-0019)
    is a targeted *reliability* signal for one specific failure mode, not a general observability
    capability, and is already captured under NFR-1300/Scalability rather than here.
  - **Source documents:** None found.

- **CNFR-02 — Numeric performance targets (latency/throughput figures)**
  - **Description (candidate):** A specific frame-rate or input-latency number (e.g. "p95 UI
    response < 100 ms") for NFR-1100/NFR-1200.
  - **Why excluded:** Per this skill's evidentiary rule, no source document states a numeric target
    — only qualitative language ("interactive frame rates," "responsive," "without stalling"). No
    number is invented; NFR-1100/NFR-1200 above are written qualitatively instead.
  - **Source documents:** None found (gap in `build-spec/04` §9 NFR-2/NFR-4).

- **CNFR-03 — Formal accreditation / RMF readiness as a standalone requirement**
  - **Description (candidate):** A requirement stating the system shall pass a specific
    accreditation framework (RMF/ITSG-33) by a stated date or milestone.
  - **Why excluded:** `build-spec/04` §9 NFR-5 explicitly states "no formal accreditation required
    for v1" — only that v1 choices should not *block* a later review. Promoting this to a positive
    accreditation requirement would contradict the source's own stated scope.
  - **Source documents:** `build-spec/04-nfr-milestones-and-risks.md` §9 NFR-5 (cited as the reason
    for exclusion, not as support for the candidate).

- **CNFR-04 — Per-cell authentication / token-based access control**
  - **Description (candidate):** A requirement that cell selection require per-cell authentication
    (e.g. session tokens) rather than client-side trust.
  - **Why excluded:** ADR-0015 explicitly accepts the unauthenticated model for v1 and defers
    per-cell tokens as a *future* hardening option, not a v1 requirement; baselining this now would
    contradict an Accepted ADR's Decision.
  - **Source documents:** `architecture/adr/ADR-0015-lan-trust-model.md` (cited as the reason for
    exclusion); `FUTURE-WORK.md` (where the deferred hardening option is tracked).

- **CNFR-05 — Cross-process/crash-recoverable availability**
  - **Description (candidate):** A requirement that an exercise be resumable after a process crash
    or restart, beyond the documented single-sitting model.
  - **Why excluded:** `build-spec/01`'s decision log lists "Save/resume mid-exercise" as v2-deferred
    by name; no v1 source document commits to crash-recoverable availability.
  - **Source documents:** `build-spec/01-context-and-scope.md` (decision log) — cited as the reason
    for exclusion.

- **CNFR-06 — AI-Red epistemic parity / fairness as a quality attribute**
  - **Description (candidate):** A requirement that AI-Red's read access be held to the same
    fog-of-war fairness standard as a human Red operator's `CellView`-filtered access, or that the
    asymmetry between them be measured/bounded.
  - **Why excluded:** ADR-0024 explicitly accepts AI-Red's direct ground-truth read (INT-0015) as a
    permanent, accepted v1 deviation and tracks remediation only as a future-work item
    (`FUTURE-WORK.md` §1), not a v1 commitment. The skill's fixed 15-category NFR taxonomy also has
    no Fairness-equivalent category to host a numbered NFR even where one might otherwise be
    warranted. `requirements/01` FR-9110 already discloses this asymmetry qualitatively at the
    functional-requirement level; this candidate records the same gap at the NFR/quality-attribute
    level so it is not visible only on the FR side.
  - **Source documents:** `architecture/adr/ADR-0024*.md`; `FUTURE-WORK.md` §1 "AI-Red fog-of-war
    parity"; `requirements/01-functional-requirements.md` FR-9110 (cross-reference).

- **CNFR-07 — Distributed-simulation / exercise-interoperability federation *(added 2026-07)***
  - **Description (candidate):** A requirement that the system support, or be examined for
    compatibility with, a federation standard (HLA/DIS/SISO) or LVC integration, so it could
    participate in a larger joint or coalition exercise.
  - **Why excluded:** No approved document commits to federation. ICD §7 item 12 (added by the
    strategic-review reconciliation) states plainly that this "has not been examined against any
    interface in this inventory" and is "flagged as a gap for a future ICD reviewer, not resolved
    here." NFR-3300 above (Interoperability) currently states no external identity/LMS/scoring-
    service integration exists or is planned "in v1" as a description of the system's current
    boundary, not as a commitment to ever add federation; a GAP-11 compatibility study of the
    `SessionAPI` seam (INT-0006) — recommended before any transport rework, per the review's own
    R19 — has not been done.
  - **Source documents:** `design/05-interface-control-document.md` §7 item 12; `strategic-review-2026-07.md`
    GAP-11, §6.3 R19; [Strategic Assumptions Register](../architecture/strategic-assumptions-register.md)
    A9 (adjacent — LAN trust model); `FUTURE-WORK.md` §13 "R19."

---

## Strategic review reconciliation (strategic-review-2026-07.md)

In response to [`reviews/strategic-review-2026-07.md`](../reviews/strategic-review-2026-07.md) and
its disposition in [`reviews/architecture-update.md`](../reviews/architecture-update.md), this
document was reviewed against the changed architecture-tier inputs. Full analysis in
[`reviews/requirements-update-report.md`](../reviews/requirements-update-report.md). Summary of what
changed here:

- **No numbered `NFR-1xxx` baseline requirement was added, removed, or had its content modified.**
  The one architecture-tier change with a plausible NFR angle — ICD §7 item 12's new federation
  gap (GAP-11/R19) — is an explicitly unexamined open question, not a committed quality attribute;
  it does not cross this document's bar for a numbered leaf.
- Added **CNFR-07**, a new Candidate Requirement for distributed-simulation/exercise-interoperability
  federation, so the NFR-tier documentation does not silently omit the new ICD §7 item 12 gap.
- Corrected the stale "build spec... remains the binding NFR statement" language in the
  pre-existing-tag-scheme note above (it independently asserted a stronger claim than
  `CLAUDE.md`'s current text supports for an unauthored GDS level) and the stale claim that no
  Traceability Matrix exists.
- Updated the Authoritative-inputs header's ADR range (`ADR-0029` → `ADR-0031`) and added the
  Strategic Assumptions Register as a cited input.

## DOM-002/004/005 backfill (2026-07)

In response to `docs/feature-planning/05-feature-review.md` Finding F-01, this document was
reviewed against DOM-002 (Assessment Framework), DOM-004 (Research Framework), and DOM-005
(Validation Framework) for any non-functional quality attribute these domains imply. Full analysis
in [`reviews/requirements-domain-backfill-report.md`](../reviews/requirements-domain-backfill-report.md).
Summary of what changed here:

- **No numbered `NFR-1xxx` requirement was added, and no new Candidate NFR was added.** DOM-005 —
  the domain document with the most plausible NFR-shaped content (validation methodology) — is
  process/methodology guidance for how a *future* Implementation Package should reason about an
  instrument's validity, not a system quality attribute this baseline can hold the running system
  to. Its one statement with genuine system-behavior shape ("characterize typical behavior by
  driving the engine across many seeds, never by relaxing determinism within a run," DOM-005 §6)
  restates NFR-1500 (Determinism) applied externally rather than describing a new constraint —
  adding a second NFR ID for the same invariant would be a duplicate, which this baseline's own
  writing rules forbid. DOM-002/004's candidate capabilities (automated rubric computation,
  dedicated research export) are functional in character and are addressed as `CR-19`/`CR-20` in
  `01-functional-requirements.md`, not here.

## ADR-0017/ADR-0029 conflict resolution (2026-07)

Following `ADR-0032`/`ADR-0033` (resolving the conflicts the backfill above found) and `CR-19`/
`CR-20`'s subsequent promotion to `FR-10110`/`FR-10210` in `01-functional-requirements.md`, this
document was reviewed for any non-functional quality attribute either new FR leaf implies. **No
new NFR was added.** Both leaves' own Postconditions (no `WorldState` mutation, no aggregation;
byte-identical seeded reproducibility) restate existing invariants (`NFR-1500` Determinism,
the replay-safety principle already governing every read-only Feature in this baseline) rather
than introducing a new one — consistent with this section's own reasoning above for why DOM-005
itself yielded nothing.

## Completion report

- **Total NFR count (numbered baseline):** 23 (`NFR-1100` through `NFR-3300`, leaving numbering
  gaps for future insertion per category, consistent with `requirements/01`'s scheme). Unchanged by
  the 2026-07 strategic-review reconciliation pass and by the 2026-07 DOM-002/004/005 backfill pass.
- **Candidate requirement count:** 7 (`CNFR-01`…`CNFR-07`). Unchanged by the DOM-002/004/005
  backfill pass — see that section above for why.
- **Categories with no derivable NFRs:** 1 of the 15 required categories — **Observability**
  (§9 above) — has no numbered NFR; its gap is recorded as `CNFR-01`. All other 14 categories
  (Performance, Scalability, Reliability, Availability, Maintainability, Extensibility, Security,
  Data integrity, Logging, Configuration, Testing, Portability, Usability, Interoperability) have
  at least one numbered NFR.
- **Open issues (flagged, not resolved in this document):**
  1. **GDS-05 OQ2 cross-reference (Availability):** NFR-1800 restates OR-6's "single exercise per
     process" framing as written, but GDS-05 already flags tension with the shipped multi-session
     `/api/sessions` discovery endpoint. Not re-resolved here; see GDS-05's own Open Questions
     (OQ2). Note: this is currently a one-directional cross-reference — NFR-1800 cites GDS-05 OQ2
     by ID, but GDS-05 OQ2 does not cite this NFR back. Closing that converse direction requires
     editing GDS-05 itself, which is outside this document's scope.
  2. **Security/accreditation tension (NFR-2200 vs. NFR-2300):** the "no practice that would block a
     later RMF/ITSG-33 review" language and the accepted unauthenticated LAN cell-selection
     boundary are both individually sourced and internally consistent, but sit in tension at a
     future-accreditation horizon. Flagged inline under §7 above; not adjudicated here.
  3. **No numeric performance targets exist in any source document** for Performance (NFR-1100/
     NFR-1200) — every Metric/verification-method field for those two items is qualitative by
     necessity, not by choice; see `CNFR-02`.
  4. **GDS-06 remains unauthored** — this document is explicitly *not* a substitute for the
     architecture ladder's own Non-Functional Requirements level; when GDS-06 is eventually
     authored and closes its merge gate against `build-spec/04` §9, this document's "pre-existing
     tag scheme" note and Source documents fields will need a pass to add GDS-06 cross-references,
     mirroring what happened to `requirements/01` when GDS-05 closed.
