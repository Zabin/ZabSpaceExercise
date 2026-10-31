# Non-Functional Requirements Baseline

> **Status:** Draft — amended (strategic-review reconciliation, 2026-07; no numbered NFR added or
> modified — see "Strategic review reconciliation" section near the end of this document and
> [`reviews/requirements-update-report.md`](../reviews/requirements-update-report.md)); further
> amended (DOM-002/004/005 backfill, 2026-07; no numbered NFR added, no new Candidate NFR added —
> see "DOM-002/004/005 backfill" section near the end of this document and
> [`reviews/requirements-domain-backfill-report.md`](../reviews/requirements-domain-backfill-report.md));
> further amended (`ADR-0032`/`ADR-0033` conflict resolution, 2026-07; `01-functional-requirements.md`
> gained two new baselined FR leaves — `FR-10110`, `FR-10210` — this document gained none; the ADR
> range below was updated); further amended (`FS-117` Vignette Creator requirements-coverage pass,
> 2026-07-05; **one numbered NFR leaf added** — `NFR-2010` — see
> [`reviews/requirements-update-fs117.md`](../reviews/requirements-update-fs117.md)); further
> amended (Must-tier external-validation-report intake batch, 2026-09-26; **one numbered NFR leaf
> added** — `NFR-3700`, generalizing `NFR-2200`'s path-traversal posture to external vignette
> directories and the user-save directory — closing `docs/pipeline/backlog.md` `BL-0082` item B16's
> security-generalization concern; see `01-functional-requirements.md`'s companion note and
> `03-requirements-review.md`).
> further amended (GDS ladder alignment, 2026-10-23; **nineteen numbered NFR leaves added** and
> **six corrected** against the newly authored GDS-06…GDS-10 and the owner decisions of
> 2026-10-22/23 — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md)).
> further amended (baseline-maintenance pass 1, 2026-10-24; **no numbered NFR added** — `NFR-1510` and
> `NFR-2830` no longer say "major" release (`BL-0318`); `NFR-3810` reworded to deletion of retired
> documents with no register (`BL-0319`); `NFR-3830` narrowed to the three ledger pairs the check
> compares (`BL-0320`); a status note added to `NFR-2820` — see
> [`requirements-change-log.md`](requirements-change-log.md) CHG-026…CHG-029.)
> further amended (baseline-maintenance pass 3, 2026-10-24; **no numbered NFR added** — `NFR-1510`
> restated as the owner's check-latest, try, validate, hold-back, then pin procedure with the lock file
> `requirements.lock` named — see [`requirements-change-log.md`](requirements-change-log.md) CHG-037.)
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

## A note on the requirement tag schemes — read before using this document

**Updated 2026-10-23.** GDS-06 (Non-functional Requirements) is now authored with its merge gate
closed and **supersedes** `docs/build-spec/04-nfr-milestones-and-risks.md` §9. GDS-06 states each
quality attribute as a tag (`NFR-1`…`NFR-19`; `NFR-1`…`NFR-10` keep the legacy build-spec numbers);
this document elaborates each tag into leaves (`NFR-1100`…) with full traceability fields. Every
leaf's **Source documents** field now names its GDS-06 tag first. The legacy build-spec citations
that remain are historical only and go when build-spec retires (`BL-0292`).

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
  - **Source documents:** `GDS-06 NFR-4; build-spec/04-nfr-milestones-and-risks.md` §9 NFR-4; §11 Risks row
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
  - **Source documents:** `GDS-06 NFR-2; build-spec/04-nfr-milestones-and-risks.md` §9 NFR-2
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
  - **Source documents:** `GDS-06 NFR-2; CLAUDE.md` "Key facts"; `architecture/adr/ADR-0019-sizing-guideline-not-engine-cap.md`
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
  - **Source documents:** `GDS-06 NFR-4; architecture/adr/ADR-0026-rlock-lan-scaling-ceiling.md`
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
  - **Source documents:** `GDS-06 NFR-3; build-spec/04-nfr-milestones-and-risks.md` §9 NFR-3; `CLAUDE.md`
    "Load-bearing invariants" #1
  - **Related ADRs:** ADR-0002 (deterministic core)

- **NFR-1510 — Released builds install identical dependency versions** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md); procedure amended 2026-10-24, baseline-maintenance pass 3)*
  - **Description:** At each release readiness the project shall check the latest available version of every dependency, try updating to those versions, validate the result with the full test suite in both modes (the browser tests excluded, and the browser tests alone), fix, or hold back at its newest compatible version, any dependency whose update breaks something, and then lock every dependency, including indirect ones, to an exact version in the committed lock file `requirements.lock` at the repository root, so every install of that release resolves the same versions. During development, dependencies are declared with minimum versions only.
  - **Rationale:** Determinism (NFR-1500) is tested within one environment; a different numpy or sgp4 version on another machine could change numeric results, so saves and replays could diverge between installs of the same release. Owner decision (`BL-0299`, 2026-10-23): defer pinning to release time; refined by `BL-0318` (2026-10-24): the lock applies at every release, with no special class of release, and is reviewed at the end of the pipeline in `11-release-readiness`. Owner decision (release preparation, 2026-10-24): "Pin each release but check if the most up to date versions break anything and attempt to update to them before re-pinning" — a release should not freeze versions that are already stale when it ships, but must not take an update that has not been validated.
  - **Metric or verification method:** Inspection at release readiness, with test runs as evidence — (1) `requirements.lock` is committed at the repository root and names every dependency, direct and indirect, with an exact version (`==`); (2) the release record shows that the latest versions were checked and tried, that both suite modes passed on the pinned set, and which packages, if any, were held back and why; (3) installing from the lock file in a fresh environment passes the same two suite runs (`11-release-readiness` check, run at every release; a missing or unvalidated lock is NO-GO).
  - **Priority:** Must (at each release)
  - **Affected subsystems:** Build/dependency manifest (`pyproject.toml` minimum versions and the release's `requirements.lock`)
  - **Dependencies:** NFR-1500, NFR-2200
  - **Source documents:** GDS-06 NFR-5 (as corrected); `docs/pipeline/backlog.md` `BL-0299`, `BL-0318` owner decisions; owner decision of 2026-10-24 quoted in the Rationale (release-preparation instruction to `04`); `CLAUDE.md` "Release dependency lock" (the working procedure).
  - **Related ADRs:** ADR-0002, ADR-0020
  - **Notes:** The word "major" is dropped here as before (`BL-0318`); the lock is made at every release. The release procedure is written out in `CLAUDE.md`; this leaf states the required outcome, not the commands. Held-back packages are a reported exception, not a failure, provided the pinned set passes both suite modes. Some text outside this baseline still says the lock is made at "the first major release" (`docs/features/FS-133-test-origin-traceability.md`, status line and the `BL-0299` sentence); it is routed to `06`, not edited here.

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
  - **Source documents:** `GDS-06 NFR-6; build-spec/04-nfr-milestones-and-risks.md` §9 NFR-6, §3.3
  - **Related ADRs:** None identified

- **NFR-1610 — Failure-atomic event application** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md))*
  - **Description:** If applying a scheduled event raises an error during a live advance, the system shall restore the world and RNG to exactly the state the event log reproduces before that event, record a no-op failure entry in the event log in the event's place, and continue the advance.
  - **Rationale:** A defect in one handler must degrade one event visibly, not corrupt state or stop the exercise; the failure record keeps live and replayed state identical (ADR-0038). GDS-06 NFR-6 states it; no leaf did (gap G2).
  - **Metric or verification method:** Test — a handler that raises leaves world and RNG equal to the replayed state, logs a `handler_error` entry, and the advance continues (tests: the generated Test column, `NFR-2850`).
  - **Priority:** Must
  - **Affected subsystems:** `engine/simulation.py`, `engine/handlers.py`
  - **Dependencies:** NFR-1500, NFR-1600
  - **Source documents:** GDS-06 NFR-6 (gap G2); ADR-0038.
  - **Related ADRs:** ADR-0038, ADR-0002

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
  - **Source documents:** `GDS-06 NFR-11; CLAUDE.md` "Load-bearing invariants" #5
  - **Related ADRs:** ADR-0002

## 4. Availability

- **NFR-1800 — Exercise availability: one sitting per session, save and resume across processes**
  *(corrected 2026-10-23, GDS-06 correction C1: the prior text said there was no mid-exercise
  save/resume across process restarts; FS-110 ships one.)*
  - **Description:** An exercise runs as one Session inside a server process for the length of a
    sitting; one process may host several sessions at once, up to a fixed live-session cap; and a
    session shall be resumable in a new process from a save file taken mid-exercise. There is no
    automatic crash recovery: a session not saved before a process stops is lost.
  - **Rationale:** States the as-built availability model (GDS-06 NFR-14): multi-sitting
    exercises are carried by save/resume (FS-110, FR-7210), not by keeping a process alive, and
    LAN multiplayer hosts several sessions in one process (`/api/sessions`).
  - **Metric or verification method:** Test — save at sim time T, load the save into a new
    session, and the resumed state equals the saved state (tests: the generated Test column,
    `NFR-2850`); Inspection — no crash-recovery mechanism is claimed.
  - **Priority:** Must
  - **Affected subsystems:** `session/` (`SessionManager.save_state`/`from_state`,
    `InProcessSession.save`/`load_save`, `MAX_LIVE_SESSIONS`)
  - **Dependencies:** FR-7210, NFR-3710
  - **Source documents:** GDS-06 NFR-14; GDS-05 OR-6 (reworded 2026-10-22); FS-110.
  - **Related ADRs:** ADR-0022

## 5. Maintainability

- **NFR-1900 — UI-agnostic engine with enforced test coverage**
  - **Description:** The simulation engine shall remain UI-agnostic: no UI or transport imports in
    `engine/`, enforced by an import guard. *(Corrected 2026-10-23, GDS-06 C4, owner decision
    `BL-0299`: the former "at least 80% unit-test coverage" clause is removed. No coverage target is
    required or enforced; what matters is that tests verify the features and requirements —
    NFR-2820.)*
  - **Rationale:** Keeping the engine importable and testable independent of any UI is what allows
    the documented v2 seams (high-fidelity propagator swap, alternate front ends) without a
    rewrite.
  - **Metric or verification method:** Test — `spacesim/tests/test_import_guard.py` (AST-scans
    `engine/` for forbidden imports).
  - **Priority:** Must
  - **Affected subsystems:** `engine/` (all modules), test suite
  - **Dependencies:** NFR-1500
  - **Source documents:** `GDS-06 NFR-7; build-spec/04-nfr-milestones-and-risks.md` §9 NFR-7; `CLAUDE.md`
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
  - **Source documents:** `GDS-06 NFR-7; CLAUDE.md` "Load-bearing invariants" #6
  - **Related ADRs:** ADR-0007

- **NFR-2010 — Additive vignette-schema evolution**
  - **Description:** A vignette-schema extension (a new typed parameter sub-schema, a new
    per-cell-keyed structure replacing a previously flat one) shall be additive: every one of the
    currently shipped vignette YAML files shall continue to load and run with byte-identical
    behavior, without modification, after the extension ships.
  - **Rationale:** `FS-117` (Vignette Creator) introduces two schema-shape changes — typed
    per-payload-type/bus parameter sub-schemas (`FR-5170`/`FR-5180`) and a per-cell ROE structure
    (`FR-3420`) — both of which must not force a migration of the 19 currently shipped vignette
    files or change their observed behavior; this is a distinct quality attribute from `NFR-2000`
    (content stays data, not code) and was not previously stated anywhere in this baseline.
  - **Metric or verification method:** Test — every currently shipped vignette's existing
    loading/behavior tests (the generated Test column, `NFR-2850`) continue to pass unchanged after the schema
    extension ships.
  - **Priority:** Must
  - **Affected subsystems:** `content/vignette.py`, `engine/bus.py`, `engine/orders.py`
  - **Dependencies:** NFR-2000
  - **Source documents:** `GDS-06 NFR-7; docs/architecture/ADS-5100B-typed-parameters-and-per-cell-roe.md` §6
    (Non-functional Requirements — Backward compatibility).
  - **Related ADRs:** (none directly)

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
  - **Source documents:** `GDS-06 NFR-7; build-spec/04-nfr-milestones-and-risks.md` §9 NFR-7; `CLAUDE.md`
    "Orbital fidelity" key fact; `FUTURE-WORK.md` §2
  - **Related ADRs:** ADR-0009

## 7. Security

- **NFR-2200 — Research-grade secure development practice**
  - **Description:** The system shall follow standard secure development practices — input
    validation on all loaded files, no execution of scenario-embedded code, declared dependency
    versions (minimum versions during development; locked at each release — NFR-1510),
    least-privilege file access — without requiring formal accreditation in v1, while avoiding any
    practice that would block a later RMF/ITSG-33 review (no telemetry phone-home, no hard-coded
    secrets). *(Corrected 2026-10-23, GDS-06 C3, owner decision `BL-0299`: "dependency pinning"
    did not match the as-built floors.)*
  - **Rationale:** This is a research/training tool, not an accredited system, but the source
    material is explicit that v1 choices should not foreclose a future formal review.
  - **Metric or verification method:** Inspection — scenario loader rejects/validates rather than
    `eval`s content; every dependency declared with a minimum version in `pyproject.toml`; no
    outbound network call exists anywhere in `spacesim/`.
  - **Priority:** Must
  - **Affected subsystems:** `content/vignette.py` (load/validate), all subsystems (no
    scenario-embedded code execution)
  - **Dependencies:** NFR-2300
  - **Source documents:** `GDS-06 NFR-5; build-spec/04-nfr-milestones-and-risks.md` §9 NFR-5
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
  - **Source documents:** `GDS-06 NFR-5; CLAUDE.md` "LAN trust model (load-bearing)"; `architecture/adr/ADR-0015-lan-trust-model.md`;
    `AUDIT-2026-06.md` §D5, §F1
  - **Related ADRs:** ADR-0015

  > **Tension flagged, not resolved here:** NFR-2200's "no practice that would block later
  > RMF/ITSG-33 review" and NFR-2300's accepted unauthenticated cell-selection boundary sit in
  > tension with each other at a future-accreditation horizon (an unauthenticated fog-of-war
  > boundary is a likely RMF finding). Both source documents (build-spec/04 §9 NFR-5 and ADR-0015)
  > are internally consistent on their own terms for v1; this document flags the forward tension
  > for whoever scopes a v2 accreditation effort rather than resolving it unilaterally.

- **NFR-3700 — Path-traversal safety generalized to external content roots**
  - **Description:** The path-traversal guard `load_vignette` applies to the built-in
    `VIGNETTE_DIR` (rejecting, without touching the filesystem, any identifier containing a path
    separator, a parent-directory traversal token, an absolute-path marker, or a disallowed
    character) shall apply identically to every configured external vignette directory (`FR-5410`)
    and to the configured user-save directory (`FR-5420`) — no content root introduced by either
    requirement may be reachable by a traversal identifier that the existing `VIGNETTE_DIR` guard
    would already reject.
  - **Rationale:** `NFR-2200`'s "input validation on all loaded files" already commits to this
    posture for the single existing content root; `BL-0082` (item B16) explicitly asks for the same
    guard to generalize as external/user directories are added, and a directory-specific guard that
    is not re-verified per new root is exactly the kind of defect this document's Security section
    exists to rule out.
  - **Metric or verification method:** Test — a traversal identifier rejected against
    `VIGNETTE_DIR` is also rejected against every configured external directory and the configured
    user-save directory, with no filesystem access on rejection.
  - **Priority:** Must
  - **Affected subsystems:** `content/vignette.py` (`load_vignette`'s existing guard,
    `spacesim/content/vignette.py:140-153`), `content/vignette_export.py` (`save_vignette`)
  - **Dependencies:** NFR-2200
  - **Source documents:** `GDS-06 NFR-5; docs/pipeline/backlog.md` `BL-0082` (external validation report, 26 Sep
    2026, item B16); `requirements/01-functional-requirements.md` `FR-5410`, `FR-5420`;
    `spacesim/content/vignette.py:140-153` (existing guard, the pattern this NFR generalizes).
  - **Related ADRs:** ADR-0007, ADR-0018

- **NFR-3710 — Bounded work on untrusted input** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md))*
  - **Description:** Inputs that could force unbounded work shall be capped before the work starts: the number of entries in a loaded save's event log, the number of live sessions per process, and the number of samples in a time-span export. An over-limit request is refused (or, for live sessions, the oldest session evicted) before any replay or sampling begins.
  - **Rationale:** A hostile or mistaken request on the LAN must not be able to exhaust the host (June 2026 audit §D7; IP-1262). GDS-06 NFR-15 states it; no leaf did (gap G3).
  - **Metric or verification method:** Test — an over-limit save, export span and session count are each refused or evicted before work starts (tests: the generated Test column, `NFR-2850`).
  - **Priority:** Must
  - **Affected subsystems:** `session/inprocess.py` (`MAX_EVENTLOG_REPLAY_ENTRIES`, `MAX_LIVE_SESSIONS`), `session/ephemeris.py` (`MAX_EXPORT_SAMPLES`)
  - **Dependencies:** NFR-2200
  - **Source documents:** GDS-06 NFR-15 (gap G3); GDS-09 §8.
  - **Related ADRs:** ADR-0015

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
  - **Source documents:** `GDS-06 NFR-3; build-spec/04-nfr-milestones-and-risks.md` §9 NFR-3
  - **Related ADRs:** ADR-0002

- **NFR-2410 — Read paths leave state unchanged** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md))*
  - **Description:** Every read or derived view — cell views, the belief scene, telemetry, order dry-run validation, AAR replay and scrub, time-span exports, the RIC view and the controller view — shall leave the live world state, the RNG state and the event log unchanged.
  - **Rationale:** Looking must never change what happens: the UI polls these reads continuously and at any rate, and a read that mutated state would break determinism silently. The codebase treats this as a rule module by module; GDS-06 NFR-13 states it; no leaf did (gap G1).
  - **Metric or verification method:** Test — for each read path, the world-state hash, RNG state and event-log length are identical before and after the call. Today per-module tests cover some paths; a cross-cutting test is owed.
  - **Priority:** Must
  - **Affected subsystems:** `session/scene.py`, `engine/telemetry.py`, `engine/orders.py` (`dry_run`), `session/aar.py`, `session/ephemeris.py`, `session/manager.py` (`controller_view`, `telemetry_export`)
  - **Dependencies:** NFR-1500
  - **Source documents:** GDS-06 NFR-13 (gap G1); GDS-09 §1 (reads have no side effects).
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
  - **Source documents:** `GDS-06 NFR-12; architecture/05-functional-requirements.md` FR-L1/FR-L2;
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
  - **Source documents:** `GDS-06 NFR-12; architecture/05-functional-requirements.md` FR-L1;
    `architecture/adr/ADR-0017-manual-adjudication.md`
  - **Related ADRs:** ADR-0017, ADR-0002

## 11. Configuration

- **NFR-2700 — File-based server configuration with override**
  - **Description:** Deployment settings — the web server's host, port and reload behavior, and
    the optional `content:` section (external vignette directories, user-save directory) — shall be
    configurable via a single YAML file at the repository root (`spacesim.config.yaml`), with its
    path overridable via an environment variable (`SPACESIM_CONFIG`), without requiring a code
    change. *(Corrected 2026-10-23, GDS-06 C5: the `content:` section added by IP-1180.)*
  - **Rationale:** White Cell facilitators (not developers) need to change the bind address (e.g.
    to expose on a LAN) without editing source.
  - **Metric or verification method:** Demonstration — editing `spacesim.config.yaml`'s `host`/
    `port`/`reload` keys and re-running `python3 -m spacesim.ui_web` changes server bind behavior
    accordingly; `SPACESIM_CONFIG` pointed at an alternate file is honored.
  - **Priority:** Should
  - **Affected subsystems:** `spacesim/config.py`, `spacesim/ui_web/server.py`
  - **Dependencies:** None
  - **Source documents:** `GDS-06 NFR-16; training/01-install-and-run.md` (configuration section); `CLAUDE.md`
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
  - **Source documents:** `GDS-06 NFR-7; CLAUDE.md` "Test-driven workflow (mandatory)"; `build-spec/06-test-plan-and-schedule.md`
  - **Related ADRs:** ADR-0002

- **NFR-2810 — Fidelity claims validated against cited reference values** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md))*
  - **Description:** Each moderate-fidelity behavior a training lesson depends on (for example the power budget, custody decay, jamming and engagement outcomes) shall be validated by a recorded comparison of simulated quantities against reference values cited in the research encyclopedia, not by judgment alone.
  - **Rationale:** Tests verify that the engine matches its specification; they do not show that the specification behaves plausibly (GDS-06 NFR-19, absorbing DOM-005 §3–§4). The June 2026 power-model recalibration is the worked precedent.
  - **Metric or verification method:** Inspection — a comparison table exists for each such behavior, citing its reference values; a regression pin test keeps a validated calibration from drifting (tests: the generated Test column, `NFR-2850`).
  - **Priority:** Should
  - **Affected subsystems:** `engine/` (the calibrated models), `docs/research/encyclopedia/`
  - **Dependencies:** NFR-1500
  - **Source documents:** GDS-06 NFR-19 (gap G6); DOM-005 §3–§4 as absorbed into GDS-06.
  - **Related ADRs:** ADR-0009

- **NFR-2820 — Every test declares the requirement or feature it verifies** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md))*
  - **Description:** Every automated test shall declare, in a form a tool can read, the requirement leaf (`FR-xxxx`/`NFR-xxxx`) it verifies; where no leaf fits, the feature specification (`FS-xxx`); and a package ID (`IP-xxxx`) only for a test of a package's own completion criteria. Every declared ID shall exist in the baseline.
  - **Rationale:** Owner direction (`BL-0310`, 2026-10-23): "Tests should be traceable to their origin, eg feature/requirement they were written to verify." Today no test cites a requirement ID, so test traceability is inference (GDS-10 finding F3). The declared form is the `@pytest.mark.verifies(...)` marker.
  - **Metric or verification method:** Test — collecting the suite lists a `verifies` declaration for every test, and every declared ID resolves to a live baseline requirement, feature or package (the documentation-integrity check, NFR-3840); Inspection — `09-package-verification` checks each new test's declaration.
  - **Priority:** Must
  - **Affected subsystems:** `spacesim/tests/` (all tests), `pyproject.toml` (marker registration)
  - **Dependencies:** None
  - **Source documents:** `docs/pipeline/backlog.md` `BL-0310` owner direction; GDS-10 §6 F3, OQ2.
  - **Related ADRs:** None identified
  - **Notes:** *(Added 2026-10-24.)* Met as built: `IP-1330` (the marker and checks) and the backfill packages `IP-1331`, `IP-1332` and `IP-1333` are `VERIFIED` (`VR-1330`–`VR-1333`); the untagged-test allow-list is empty.

- **NFR-2830 — Test relevance audited at each release** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md))*
  - **Description:** At each release, the whole test suite shall be audited for relevance: tests with no declared origin, tests whose declared requirement is retired or superseded, tests that duplicate another test's check, and requirements in the release's scope with no test. Each finding shall be routed to its owning stage.
  - **Rationale:** Owner direction (`BL-0310`, 2026-10-23): auditing tests for relevance is part of verification, and runs at the end of the pipeline, at every release, in `11-release-readiness` (`BL-0318`, owner decision 2026-10-24: no special class of release).
  - **Metric or verification method:** Inspection — the Release Assessment records the audit's results (`11-release-readiness`).
  - **Priority:** Must (at each release)
  - **Affected subsystems:** `spacesim/tests/`, `docs/requirements/`
  - **Dependencies:** NFR-2820
  - **Source documents:** `docs/pipeline/backlog.md` `BL-0310` owner direction and run #209 cadence decision; `BL-0318` owner decision.
  - **Related ADRs:** None identified

- **NFR-2840 — Load-bearing UI rules verified by automated browser tests** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md))*
  - **Description:** An automated browser test shall verify, in the shipped browser client, that (a) a Red or Blue seat's views never display ground truth for objects the cell does not hold custody of, (b) a command the server would refuse is shown disabled with the refusal reason before it is issued, and (c) kinetic and cyber orders require an explicit consequence confirmation before they are sent.
  - **Rationale:** Every backend path is tested, but nothing verifies what the browser actually shows (GDS-08 "Verification status"). Owner decision (`BL-0304`, 2026-10-23): add a small browser suite for the load-bearing UI rules.
  - **Metric or verification method:** Test — a headless-browser test drives the console for each rule (a), (b) and (c) and asserts the rendered result.
  - **Priority:** Must
  - **Affected subsystems:** `spacesim/ui_web/static/`, `spacesim/tests/`
  - **Dependencies:** NFR-3010, NFR-3020, FR-6210
  - **Source documents:** GDS-08 "Verification status" and OQ1; `docs/pipeline/backlog.md` `BL-0304` owner decision.
  - **Related ADRs:** ADR-0004, ADR-0008

- **NFR-2850 — The traceability matrix's Test column is generated from declared test origins** *(new 2026-10-23, owner request — `BL-0322`)*
  - **Description:** The Test column of the requirements traceability matrix shall be produced from the origins the tests themselves declare (`NFR-2820`), never edited by hand: a requirement's Test cell lists exactly the tests whose declared origin names it, and is `UNASSIGNED` when none does. Requirement text shall not name test files as verification evidence, except where the named test is itself the subject of the requirement (the two permanent gates, and the playbook and training-source tests that `FR-11420` and `NFR-3400` require).
  - **Rationale:** Owner request (`BL-0322`, 2026-10-23): test-to-origin traceability must work in both directions without a hand-kept copy that can drift. The markers record test → requirement; generating the column gives requirement → tests from the same source. GDS-10 OQ1 asks the same of GDS-10's matrix.
  - **Metric or verification method:** Test — regenerating the column from the current suite's declared origins yields exactly the committed column (a stale or hand-edited cell fails); Inspection — no requirement leaf outside the stated exceptions names a test file.
  - **Priority:** Should
  - **Affected subsystems:** `docs/requirements/03-requirements-traceability-matrix.md`, `spacesim/tests/` (the origin report)
  - **Dependencies:** NFR-2820
  - **Source documents:** `docs/pipeline/backlog.md` `BL-0322` owner request; GDS-10 §7 and OQ1.
  - **Related ADRs:** None identified
  - **Notes:** Until the suite is backfilled (`IP-1331`–`IP-1333`), most generated cells are `UNASSIGNED` — the honest state. The test files this pass removed from leaf text are listed in `requirements-change-log.md` CHG-020 as hints for the backfill.

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
  - **Source documents:** `GDS-06 NFR-8; build-spec/04-nfr-milestones-and-risks.md` §9 NFR-8
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
  - **Source documents:** `GDS-06 NFR-9; build-spec/04-nfr-milestones-and-risks.md` §9 NFR-9;
    `design/09-gui-principles.md`
  - **Related ADRs:** None identified

- **NFR-3010 — Belief is visibly distinguishable from ground truth** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md))*
  - **Description:** A cell's custody and confidence picture shall be visually distinguishable from ground truth at a glance: every displayed object of another cell carries its confidence encoding (current, aging, propagated-only or uncharacterized), and objects the cell has not detected are not drawn.
  - **Rationale:** Conflating belief and truth in the UI undermines the fog-of-war lesson even when the backend enforces the boundary (GDS-06 NFR-9, absorbing DOM-007 §4; GDS-08 §5).
  - **Metric or verification method:** Test — NFR-2840 (a); Inspection of the render-from-custody layer (`symbology.js`, `globe.js`, `world.js`).
  - **Priority:** Must
  - **Affected subsystems:** `ui_web/static/` (`globe.js`, `world.js`, `symbology.js`)
  - **Dependencies:** FR-6210
  - **Source documents:** GDS-06 NFR-9 (gap G4); GDS-08 §2, §4–§6.
  - **Related ADRs:** None identified

- **NFR-3020 — An unavailable action states its reason before it is committed** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md))*
  - **Description:** Any command the server would refuse shall be presented as unavailable, with the server's refusal reason in operator language, before the operator commits it.
  - **Rationale:** Operators must never discover "you can't do that" only after committing (GDS-06 NFR-9, absorbing DOM-007 §4; GDS-08 §6, the button-state contract).
  - **Metric or verification method:** Test — the dry-run validation returns the reason without changing state (tests: the generated Test column, `NFR-2850`); NFR-2840 (b) for the rendered half.
  - **Priority:** Must
  - **Affected subsystems:** `engine/orders.py` (`dry_run`), `ui_web/static/app.js`
  - **Dependencies:** NFR-2410
  - **Source documents:** GDS-06 NFR-9 (gap G4); GDS-08 §2, §4–§6.
  - **Related ADRs:** None identified

- **NFR-3030 — Every panel obeys the panel-manager contract** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md))*
  - **Description:** Every console panel shall be closable, floatable, resizable and resettable to its dock through the panel manager from its first release.
  - **Rationale:** A panel bolted into a fixed grid is accidental friction that later needs retrofitting (GDS-06 NFR-9, absorbing DOM-007 §5; GDS-08 §4). As built, the Compare and Assessment panels are not registered (`BL-0305`).
  - **Metric or verification method:** Inspection — every panel in `index.html` is registered in `panels.js`.
  - **Priority:** Should
  - **Affected subsystems:** `ui_web/static/panels.js`, `index.html`
  - **Dependencies:** None
  - **Source documents:** GDS-06 NFR-9 (gap G4); GDS-08 §2, §4–§6.
  - **Related ADRs:** None identified

- **NFR-3040 — Summary and detail views agree** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md))*
  - **Description:** Any element that previews a fuller view (a sparkline, badge or thumbnail graph) shall use the same data source, time window and scaling as the view it previews.
  - **Rationale:** An operator correctly distrusts a preview that disagrees with its detail view (GDS-06 NFR-9, absorbing DOM-007 §4).
  - **Metric or verification method:** Inspection — each preview and its detail view read the same series endpoint with the same window.
  - **Priority:** Should
  - **Affected subsystems:** `ui_web/static/graph.js`, `app.js`
  - **Dependencies:** None
  - **Source documents:** GDS-06 NFR-9 (gap G4); GDS-08 §2, §4–§6.
  - **Related ADRs:** None identified

- **NFR-3050 — The cause of a moving telemetry value is shown** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md))*
  - **Description:** Where a telemetry value changes because of a modelled condition (for example eclipse-driven battery drain), the console shall show that condition next to the value.
  - **Rationale:** A falling value with no visible cause reads as a bug and defeats the lesson (GDS-06 NFR-9, absorbing DOM-007 §4; the eclipse-drain precedent).
  - **Metric or verification method:** Inspection — eclipse state is shown beside the power telemetry it drives.
  - **Priority:** Should
  - **Affected subsystems:** `engine/telemetry.py`, `ui_web/static/app.js`
  - **Dependencies:** None
  - **Source documents:** GDS-06 NFR-9 (gap G4); GDS-08 §2, §4–§6.
  - **Related ADRs:** None identified

- **NFR-3060 — White Cell can see the active Red doctrine preset** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md))*
  - **Description:** When AI-Red is active, White Cell shall be able to see which Red doctrine preset is active.
  - **Rationale:** A facilitator needs to know what Red is doing for pacing and debrief honesty (GDS-06 NFR-9, absorbing DOM-008 §3).
  - **Metric or verification method:** Inspection — the active preset is shown on a White Cell surface.
  - **Priority:** Should
  - **Affected subsystems:** `session/redai.py`, `ui_web/static/app.js`
  - **Dependencies:** None
  - **Source documents:** GDS-06 NFR-9 (gap G4); GDS-08 §2, §4–§6.
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
  - **Source documents:** `GDS-06 NFR-10; build-spec/04-nfr-milestones-and-risks.md` §9 NFR-10;
    `architecture/05-functional-requirements.md` FR-W5
  - **Related ADRs:** None identified

## 15. Interoperability

- **NFR-3200 — No network access; TLE/OMM import by paste or file**
  *(corrected 2026-10-23, GDS-06 C2, owner decision `BL-0299`: the Space-Track import this leaf
  described was never built and is dropped.)*
  - **Description:** The system shall make no network call at any time: TLE and CCSDS OMM (KVN)
    data enter by paste or file, and a vignette runs with no network connection.
  - **Rationale:** Training rooms may be offline or air-gapped (ADR-0018's offline-first runtime);
    as built, no code in `spacesim/` opens a network connection.
  - **Metric or verification method:** Test — TLE and OMM import succeed from pasted or file text
    (tests: the generated Test column, `NFR-2850`); Inspection — no network client is used
    anywhere in `spacesim/`.
  - **Priority:** Must
  - **Affected subsystems:** `content/` (TLE/OMM parsing), `session/` (force-add), Vignette Creator
  - **Dependencies:** None
  - **Source documents:** GDS-06 NFR-1; `architecture/02-system-context.md`;
    `architecture/05-functional-requirements.md` FR-S2.
  - **Related ADRs:** ADR-0018 (its build-time Space-Track pull is not built; revision note owed —
    see the GDS ladder alignment review)

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
  - **Source documents:** `GDS-06 NFR-8; architecture/02-system-context.md` §2–§4
  - **Related ADRs:** None identified

## 16. Training-artifact quality and documentation integrity *(new 2026-07-04, training-corpus elevation; documentation integrity added 2026-10-23)*

Qualities of the training corpus itself — the manuals, learning path, and vignette
briefs/tutorials elevated to co-equal product status by MSTR-001 §2 and the GDS-00/GDS-01
"Training-corpus elevation (2026-07-04)" sections. Functional shape lives in the FR-11000 family;
these are the *how well* constraints.

- **NFR-3400 — Training-artifact accuracy (documents as-built behavior only)**
  - **Description:** Every training artifact shall describe only shipped, as-built behavior —
    never planned, removed, or aspirational behavior — and shall be updated (or explicitly
    dispositioned as unaffected) in the same change set as any change to the behavior it
    documents.
  - **Rationale:** A trainer whose manual mis-states the tool actively harms the trainee; this is
    the NFR face of FR-11410, and assumption A12 tracks the residual enforcement risk.
  - **Metric or verification method:** Analysis — at stage 09/10 review, sampled manual sections
    mapped (via `training/15`) to the change set match observed behavior; the vignette playbook
    suite (`test_vignette_tutorials.py`) is green; and *(amended 2026-10-17, run #160, `BL-0027`)*
    an automated test confirms that every code path and symbol a training module's `> Sources:`
    footer names still exists, so a moved or renamed code path fails the suite. This is the
    mitigation `strategic-assumptions-register.md` A12 names ("extend the playbook-test pattern to
    manual `Sources:` anchors"); A12's trigger fired when `BL-0029` found real drift.
  - **Priority:** Must
  - **Affected subsystems:** `docs/training/`, `spacesim/content/vignettes/*.yaml` (briefs and
    tutorial blocks)
  - **Dependencies:** FR-11210, FR-11410
  - **Source documents:** GGDS-06 NFR-17; DS-01 "Training-corpus elevation (2026-07-04)";
    `strategic-assumptions-register.md` A12
  - **Related ADRs:** None identified

- **NFR-3500 — Modularity and retrievability of training modules**
  - **Description:** Training modules shall stay single-topic and small enough to read whole
    (~50–300 lines, the corpus-wide convention), routed by the theme index, so a reader (human or
    agent) can open exactly the module they need; role-scoped content shall be reachable within
    two links from the training index.
  - **Rationale:** `DOCUMENTATION-PLAN.md` goals 1–2 applied to the corpus that now carries
    requirement weight; MSTR-001 §3's independently-retrievable standard extended to the
    operator-facing tier.
  - **Metric or verification method:** Inspection — module line counts within the convention
    (split when exceeded); every training INDEX row resolves; role manuals linked from the index
    header.
  - **Priority:** Should
  - **Affected subsystems:** `docs/training/`
  - **Dependencies:** None
  - **Source documents:** `GDS-06 NFR-17; docs/DOCUMENTATION-PLAN.md` ("Keep modules small"); MSTR-001 §3
  - **Related ADRs:** None identified

- **NFR-3600 — Learner-appropriate presentation**
  - **Description:** Training artifacts shall be written for the stated audience — semi-technical
    operators, not developers: procedures phrased as operator actions (what to click/plan/read),
    jargon introduced before use or linked to the glossary, and each vignette rung's brief
    understandable without reading source code. Pedagogical choices (sequencing, scaffolding,
    debrief structure) shall cite their R600 grounding once the corresponding topic is authored.
  - **Rationale:** MSTR-003 (educational philosophy); the R600 tier exists precisely so
    "teachable" is a researched property, not a vibe. The R600 tier is fully authored (8/8,
    2026-07-04), so this NFR is fully verifiable.
  - **Metric or verification method:** Inspection at `09-training-manual-review` passes —
    audience check against MSTR-003; R600 citations present where the tier has authored topics;
    glossary linkage for introduced terms.
  - **Priority:** Should
  - **Affected subsystems:** `docs/training/`, vignette `intro_brief`/`tutorial`/`coaching`
    blocks
  - **Dependencies:** NFR-3400
  - **Source documents:** MGDS-06 NFR-17; STR-003; `docs/research/encyclopedia/R600-index.md`
  - **Related ADRs:** None identified

- **NFR-3800 — Relative links in live documents resolve** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md))*
  - **Description:** Every relative link in a live document shall resolve to an existing file.
  - **Rationale:** Broken links make the documentation tree unreliable; a read-only scan on 2026-10-19 found 82 in live files. GDS-06 NFR-18 (gap G5).
  - **Metric or verification method:** Test — the documentation-integrity suite (`BL-0297`) checks it on every run; frozen history (journal run log and archives, Verification Reports, review reports, ADR records) is exempt.
  - **Priority:** Should
  - **Affected subsystems:** `docs/` (live documents), `spacesim/tests/` (the suite)
  - **Dependencies:** NFR-3400
  - **Source documents:** GDS-06 NFR-18 (gap G5); `docs/pipeline/backlog.md` `BL-0297`, `BL-0310`.
  - **Related ADRs:** None identified

- **NFR-3810 — A retired document is deleted, declared, and no live document names it** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md); reworded 2026-10-24, `BL-0319`; made checkable 2026-10-31, pass 4)*
  - **Description:** A *retired document* is a documentation file (a Markdown file under `docs/`, or a root-level one such as `ROADMAP.md`) deliberately removed from the tree, whether it was dropped or renamed, and not a frozen-history file left in place. A retired document shall be deleted, not moved to an archive folder; the repository's version history is its archive. Each retirement shall be declared, in the commit that deletes the file, as one row in a `Retired documents` section (a second-level heading of that exact title) of the `INDEX.md` in the folder that held the file, giving the former path, the former document ID if it had one (for example a build-spec module number), the retirement date and the successor path or `none`. No live document other than a `Retired documents` section shall contain a declared path or ID, as a link, in backticks or in plain text; IDs are matched as whole tokens. A declared path shall not exist in the tree.
  - **Rationale:** Retiring a document must not leave live references to it (owner direction 2026-10-19; `BL-0297`). Owner decision (`BL-0319`, 2026-10-24): delete retired documents, with no archive folder and no separate register file; git history is the archive, and a git tag on the last commit that holds them is the preserved pointer if one is wanted. With deletion, `NFR-3800` already fails any live link to a deleted file, so this leaf covers the case links miss: a deleted path or ID named in backticks or plain text. A declaration inside an index the owning stage already maintains needs no new file, no new owner and no shared write, and `NFR-3820` already forces that index to agree with its folder. GDS-06 NFR-18 (gap G5).
  - **Metric or verification method:** Test — the documentation-integrity suite (`BL-0297`, `FS-135` check 2) reads every `Retired documents` section and fails when (a) a declared path still exists in the tree ("retired but not removed"), (b) a live document outside a `Retired documents` section contains a declared path or whole-token ID, or (c) a `Retired documents` row lacks a date or a successor (`none` is valid). A tree with no `Retired documents` section passes. Frozen history (journal run log and archives, Verification Reports, review reports, ADR records) is exempt. Inspection — no archive folder holds a retired document.
  - **Priority:** Should
  - **Affected subsystems:** `docs/` (live documents), `spacesim/tests/` (the suite)
  - **Dependencies:** NFR-3400, NFR-3800, NFR-3820
  - **Source documents:** GDS-06 NFR-18 (gap G5); `docs/pipeline/backlog.md` `BL-0297`, `BL-0310`, `BL-0319` owner decision.
  - **Related ADRs:** None identified
  - **Notes:** **Not yet built** (owner decision 2026-10-31: build before release; a `06`/`07` package is owed, `FS-135` check 2). **Design choices for the project owner:** (1) the declaration lives in the `INDEX.md` of the folder that held the retired file (this text's recommendation, replacing `FS-135`'s register file and its Open Questions 1 and 4); the alternatives are one section of `docs/INDEX.md` for every retirement, or a status marker on a surviving stub, which contradicts deletion. (2) A declared path or ID may be named nowhere live except its declaring row, so a supersession note elsewhere must name the successor, not the retired file; the alternative is an allow-list of referrers, which is more permissive and harder to check. Both are applied as written until the owner says otherwise. Retired requirement leaves are out of scope (`BL-0317`). Frozen-history folders that already exist (`docs/reviews/`, `docs/implementation/verification/`, `docs/architecture/adr/`, the pipeline archives) are unchanged by this leaf. `FS-135` check 2 and Open Questions 1, 4 and 5 are `06`'s to align.

- **NFR-3820 — Each index agrees with its folder** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md))*
  - **Description:** Each `INDEX.md` shall list exactly the documents in its folder.
  - **Rationale:** Indexes are how readers and agents find documents; a stale index hides or invents documents. GDS-06 NFR-18 (gap G5).
  - **Metric or verification method:** Test — the documentation-integrity suite (`BL-0297`) checks it on every run; frozen history (journal run log and archives, Verification Reports, review reports, ADR records) is exempt.
  - **Priority:** Should
  - **Affected subsystems:** `docs/` (live documents), `spacesim/tests/` (the suite)
  - **Dependencies:** NFR-3400
  - **Source documents:** GDS-06 NFR-18 (gap G5); `docs/pipeline/backlog.md` `BL-0297`, `BL-0310`.
  - **Related ADRs:** None identified

- **NFR-3830 — Status ledgers agree** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md))*
  - **Description:** Where two status ledgers use a shared status vocabulary, they shall report the same status for the same item. Three pairs are in scope: the Master Build Plan and the package index (packages); `architecture/INDEX.md` §1 and `ROADMAP.md` (GDS levels); the feature index and each feature specification's header (features).
  - **Rationale:** Ledgers drift when one is updated and another is not; GDS-10 is built from them. GDS-06 NFR-18 (gap G5). `BL-0320` (2026-10-24): `ROADMAP.md`'s free-text package and phase statuses use no vocabulary a program can map, so they are outside this leaf rather than checked by guesswork.
  - **Metric or verification method:** Test — the documentation-integrity suite (`BL-0297`) checks it on every run; frozen history (journal run log and archives, Verification Reports, review reports, ADR records) is exempt.
  - **Priority:** Should
  - **Affected subsystems:** `docs/` (live documents), `spacesim/tests/` (the suite)
  - **Dependencies:** NFR-3400
  - **Source documents:** GDS-06 NFR-18 (gap G5); `docs/pipeline/backlog.md` `BL-0297`, `BL-0310`.
  - **Related ADRs:** None identified
  - **Notes:** *(Reworded 2026-10-24, `BL-0320`.)* The earlier text named five ledgers; the check as built (`IP-1350`, `VR-1350`) compares only the three pairs above. Defining a shared vocabulary for `ROADMAP.md`'s free-text statuses would widen the leaf (a `05`/`03` decision). `NFR-3820` names `INDEX.md` files; `docs/features/feature-index.md` is a catalogue read by `NFR-3830`, not an `INDEX.md`, and whether to rename it or widen `NFR-3820` is routed to `05-feature-decomposition`.

- **NFR-3840 — Every declared test origin resolves** *(new 2026-10-23, GDS ladder alignment — see [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md))*
  - **Description:** Every requirement, feature or package ID a test declares as its origin (NFR-2820) shall exist in the live baseline and shall not be retired or superseded.
  - **Rationale:** A declared origin is only traceable if it points at something real and current (owner direction `BL-0310`). GDS-06 NFR-18 (gap G5).
  - **Metric or verification method:** Test — the documentation-integrity suite (`BL-0297`) checks it on every run; frozen history (journal run log and archives, Verification Reports, review reports, ADR records) is exempt.
  - **Priority:** Should
  - **Affected subsystems:** `docs/` (live documents), `spacesim/tests/` (the suite)
  - **Dependencies:** NFR-2820
  - **Source documents:** GDS-06 NFR-18 (gap G5); `docs/pipeline/backlog.md` `BL-0297`, `BL-0310`.
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

- **Total NFR count (numbered baseline):** 48 as of 2026-10-23 (28 before the GDS ladder
  alignment pass, which added 19; `NFR-2850` added the same day for `BL-0322`); numbering leaves gaps per category, consistent with
  `requirements/01`'s scheme. *(The figure of 23 recorded here originally predates `NFR-2010`,
  `NFR-3400`–`NFR-3600` and `NFR-3700`.)* Unchanged by
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
  4. **Resolved 2026-10-23:** GDS-06 is authored, and every leaf now cites its GDS-06 tag. *(Original
     text:)* GDS-06 remains unauthored — this document is explicitly *not* a substitute for the
     architecture ladder's own Non-Functional Requirements level; when GDS-06 is eventually
     authored and closes its merge gate against `build-spec/04` §9, this document's "pre-existing
     tag scheme" note and Source documents fields will need a pass to add GDS-06 cross-references,
     mirroring what happened to `requirements/01` when GDS-05 closed.
