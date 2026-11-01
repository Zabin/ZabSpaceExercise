# GDS-06 — Non-functional Requirements

> **Document ID:** GDS-06
> **Version:** 1.1 (2026-10-23, pipeline run #217 maintenance: owner decisions on OQ1–OQ3 recorded, `BL-0299`; the `04` hand-off marked applied, run #211). v1.0: run #200.
> **Status:** ✅ Authored — merge gate closed (see "Merge gate" below)
> **Dependencies:** GDS-05
> **Referenced By:** GDS-07
> **Produces:** GDS-07
> **Feature Mapping:** N/A — program-level
> **Related Topics:** [`build-spec/04-nfr-milestones-and-risks.md`](../build-spec/04-nfr-milestones-and-risks.md)
> §9 (merge source — superseded by this document, see "Merge gate" below),
> [`requirements/02-non-functional-requirements.md`](../requirements/02-non-functional-requirements.md)
> (companion hierarchical elaboration with full traceability fields),
> [GDS-05](05-functional-requirements.md), [GDS-03](03-architecture.md),
> [`adr/INDEX.md`](adr/INDEX.md) (ADR-0002, -0004, -0006, -0007, -0014, -0015, -0018, -0019, -0026,
> -0030, -0038). Absorbs DOM-005 §3–4 and §6, DOM-007 §3–6 and DOM-008 §3 (see "Merge gate").

[↑ Architecture index](INDEX.md) · [Docs index](../INDEX.md)

## Purpose

The authoritative statement of **how well** SpaceSim must do what GDS-05 says it does: the quality
attributes (determinism, robustness, performance, security, maintainability, usability,
portability, documentation integrity) every capability must preserve. Stated at quality-attribute
grain, one tag per attribute, so a stakeholder can ask "is the system X enough" and find the
statement, its verification method and the requirement leaves that elaborate it.

This document is the result of closing GDS-06's merge gate: `build-spec/04` §9 (`NFR-1`…`NFR-10`)
is restated and reconciled with the shipped system here, the existing `requirements/02` baseline
is mapped under each tag, and the relevant domain-framework content is folded in.

## Relationship to other non-functional requirement artifacts

| Document | Grain | Role |
|---|---|---|
| `build-spec/04-nfr-milestones-and-risks.md` §9 | Tag (`NFR-1`…`NFR-10`) | **Superseded.** Kept on disk only until build-spec is retired (`BL-0292`); new work cites GDS-06 or `requirements/02`. |
| **GDS-06 (this document)** | Tag (`NFR-1`…`NFR-19`) | **Authoritative for what quality must hold.** `NFR-1`…`NFR-10` keep their legacy numbers so existing citations resolve; `NFR-11`…`NFR-19` state attributes the legacy list never named. |
| `requirements/02-non-functional-requirements.md` | Leaf (`NFR-1100`…) | **Authoritative for full traceability**: Rationale, Metric/verification method, Priority, Affected subsystems, Dependencies, Related ADRs per leaf. |

Tag `NFR-n` (one or two digits, this document) and leaf `NFR-nnnn` (four digits, `requirements/02`)
are different schemes; each tag below lists its leaves. Where a tag has **no leaf yet**, that is a
gap for `04-requirements-engineering` to close, listed in §"Gaps handed to 04". Where a leaf's text
no longer matches the shipped system, that is listed in §"Leaf corrections handed to 04"; this
document states the as-built truth and does not edit `requirements/02` itself.

---

## 1. Determinism and integrity

Traces to `CLAUDE.md` load-bearing invariants 1 and 5; ADR-0002, ADR-0006, ADR-0030, ADR-0038.

- **NFR-3 Determinism.** Identical `(initial state, ordered event log, seed)` reproduces
  byte-identical state at every point, verified by state hashes and enforced by the permanent
  determinism property test (`spacesim/tests/test_determinism.py`). This is what makes rewind,
  undo, branch and AAR replay exact rather than approximate. It binds every component, including
  in-world AI: Red doctrine decisions draw only from the seeded RNG, and any non-deterministic
  computation (ML inference, unseeded randomness, wall-clock reads beyond the session layer's
  clock anchor) is prohibited inside `engine/` and may affect the world only through an ordinary
  `SessionAPI` call (ADR-0030; absorbs DOM-008 §3, second bullet). Variability across runs is
  studied by driving many seeds externally, never by relaxing determinism within one run (absorbs
  DOM-005 §6). *(→ `NFR-1500`, `NFR-2400`; FR-E2 / `FR-1120`)*
- **NFR-11 Sub-stepped time.** The clock advances to the next scheduled event and never steps past
  it, at any time multiplier; a short LEO pass is never skipped by a large step. *(→ `NFR-1700`;
  ADR-0006)*
- **NFR-12 Event-log completeness.** Every state-changing event (orders, executions, effects,
  injects, White Cell controls, time controls) is appended to an ordered, timestamped event log
  that is sufficient on its own to reconstruct the exercise. The log is both the integrity
  foundation and the facilitator's adjudication record (ADR-0017). *(→ `NFR-2500`, `NFR-2600`;
  FR-L1/FR-L2)*
- **NFR-13 Replay-safe reads.** Every read or derived view (belief scene, telemetry, dry-run
  validation, AAR replay and scrub, time-span exports, RIC view, controller view) leaves live
  `WorldState`, the RNG and the event log untouched: looking never changes what happens. The
  codebase already treats this as a rule (`scene.py`, `telemetry.py`, `orders.dry_run()`,
  `aar.state_at_time()` are each documented as replay-safe), but no requirement states it.
  *(→ no leaf — gap G1)*

## 2. Robustness and reliability

Traces to GDS-01 trust model; ADR-0038; `CLAUDE.md` "Status".

- **NFR-6 Robustness.** An invalid vignette or TLE fails at load with a precise, actionable White
  Cell error and leaves the session registry untouched (load-time validation, `FR-5310`ff.). The
  running engine never crashes on a legal operator action; an illegal action is blocked with an
  explanation before commit (`dry_run()`); a tactically poor but legal action runs to its natural
  outcome. **Failure atomicity (ADR-0038):** if an event handler raises during a live advance, the
  world and RNG are restored to exactly what the event log reproduces, a no-op `handler_error`
  record takes the event's place in the log, and the advance continues — so a defect degrades one
  event, visibly, instead of corrupting state or stopping the exercise. *(→ `NFR-1600`;
  failure atomicity has no NFR leaf — gap G2; `FR-1120` cites ADR-0038)*
- **NFR-14 Availability.** An exercise runs for the length of one sitting inside one server
  process, and **can be saved mid-exercise and resumed in a new process** from the save file
  (`InProcessSession.save`/`load_save`, FS-110). One process hosts several sessions at once
  (`/api/sessions` discovery, LAN multiplayer), up to a fixed live-session cap. There is no
  automatic crash recovery: a session not saved before a crash is lost. *(→ `NFR-1800`, which is
  stale — see correction C1; GDS-05 OQ2)*

## 3. Performance and scale

Traces to GDS-02 deployment context; ADR-0014, ADR-0019, ADR-0026.

- **NFR-2 Hardware floor.** The application runs at interactive frame rates in its 2D views on a
  typical government laptop (integrated graphics, 16 GB RAM) for vignettes at the sizing guideline
  (~24 satellites, all six access channels). The guideline is guidance, not a cap: the engine
  enforces no satellite or constellation limit, and the clock-lag watchdog
  (`SessionManager._record_catch_up_lag`) warns White Cell when the host cannot keep up.
  *(→ `NFR-1200`, `NFR-1300`; ADR-0019)*
- **NFR-4 Responsiveness.** Window computation and state advance for a guideline-sized vignette
  keep the UI responsive at time multipliers up to at least 600×. With the server-authoritative
  lazy clock (ADR-0014), the clock advances exactly once per read regardless of how many clients
  are connected; per-session locking is designed for roughly 16 LAN participants, a documented
  estimate that has never been load-tested (ADR-0026). No numeric latency or frame-rate target
  exists in any source (open question OQ4). *(→ `NFR-1100`, `NFR-1400`)*

## 4. Security

Traces to GDS-02 trust boundary; ADR-0015, ADR-0018; `CLAUDE.md` "LAN trust model".

- **NFR-1 Offline runtime.** A running exercise needs no network access. **As built, the
  application makes no network call at all**: TLE and CCSDS OMM import take pasted or file text,
  and the optional build-time Space-Track pull ADR-0018 once described was never built and has
  been dropped (owner decision, `BL-0299`; ADR-0018 revised 2026-10-23). *(→ `NFR-3200`; ADR-0018)*
- **NFR-5 Research-grade secure development.** Every loaded file is validated, never executed
  (no scenario-embedded code); file access is confined to configured content roots by the
  path-traversal guard, applied identically to built-in, external and user-save directories; no
  telemetry phone-home; no hard-coded secrets; nothing that would block a later RMF/ITSG-33
  review. No formal accreditation is required. **Dependency versions are declared as minimum
  versions (`>=`) during development, and every dependency is locked to an exact version at each
  release** (owner decisions `BL-0299`, `BL-0318`). *(→ `NFR-2200`, `NFR-1510`, `NFR-3700`)*
- **NFR-15 Bounded resource use on untrusted input.** Inputs that could force unbounded work are
  capped before the work starts: a loaded save's event log (`MAX_EVENTLOG_REPLAY_ENTRIES`,
  100,000), live sessions per process (`MAX_LIVE_SESSIONS`, 32; the oldest is evicted at the cap),
  and samples per
  time-span export (`MAX_EXPORT_SAMPLES`, 10,000, rejected before any replay). These shipped from
  the June 2026 audit (§D7) and IP-1262 but no requirement states the attribute. *(→ no leaf —
  gap G3)*
- **Trust boundary (documented, not hardened).** Cell selection is client-side trust. Fog-of-war
  is enforced exactly once, server-side, at the `SessionAPI`/`CellController` boundary for every
  cell-scoped response (ADR-0004, invariant 3, `FR-6210`), while the named ground-truth endpoints
  (`FR-6220`) expose truth without a cell binding. Deploy only on a trusted, cooperative LAN; a
  hostile participant can read another cell's picture by naming it. Per-cell authentication is
  deferred hardening (`CNFR-04`). This is stated under the NFR-5 tag rather than as a new tag
  because it is the accepted boundary of NFR-5's posture. *(→ `NFR-2300`; ADR-0015; tension with
  accreditation horizon carried as OQ5)*

## 5. Maintainability and extensibility

Traces to invariants 2 and 6; ADR-0001, ADR-0007, ADR-0009, ADR-0023.

- **NFR-7 Maintainability.** The engine stays UI- and transport-agnostic (no UI/transport imports,
  no wall-clock reads, no `random` outside `rng.py`, all enforced by the AST import-guard test).
  Content — vignettes, asset and effect templates, inject templates, Red doctrine presets — is
  data, never Python; scenario logic does not leak into code, and a new Red posture is a new preset,
  not a new engine branch (DOM-008 §3, first bullet). Vignette-schema changes are additive: every shipped
  vignette still loads and behaves identically after a schema extension. The three fidelity seams
  (`Propagator`, `AccessProvider`, `EffectResolver`) are documented and independently testable, so
  a higher-fidelity model substitutes without call-site changes. Development is test-first with
  the full suite green before every commit. **There is no coverage target** (owner decision,
  `BL-0299`): what matters is that tests are written to show each feature and requirement is
  satisfied, and every test declares the requirement it verifies (`BL-0310`, `NFR-2820`). The
  legacy 80% figure is withdrawn. The whole suite is audited for relevance at each release.
  *(→ `NFR-1900`, `NFR-2000`, `NFR-2010`, `NFR-2100`, `NFR-2800`, `NFR-2820`, `NFR-2830`)*
- **NFR-16 Configuration.** Deployment settings (server host, port, reload; external vignette
  directories; user-save directory) live in one optional YAML file, its path overridable by
  `SPACESIM_CONFIG`, so a facilitator changes them without editing code. *(→ `NFR-2700`; the
  `content:` section added by IP-1180 is not yet in the leaf — see correction C5)*

## 6. Portability and interoperability

Traces to GDS-02 §2–§4; ADR-0008, ADR-0018, ADR-0020.

- **NFR-8 Portability.** Windows-first for the target laptop, with no OS-specific dependency that
  would prevent Linux or macOS development. *(→ `NFR-2900`)*
- **Interoperability boundary.** The client is a standard browser over HTTP(S) to the FastAPI
  server; there is no external identity provider, learning-management system or scoring service.
  TLE and CCSDS OMM (KVN) are the supported import formats; TLE, CSV and CCSDS OEM are the export
  formats. Federation (HLA/DIS/LVC) is not examined (`CNFR-07`). Stated under NFR-8 as a boundary,
  not a new tag. *(→ `NFR-3300`, `NFR-3200`)*

## 7. Usability and human factors

Traces to GDS-01 user classes; MSTR-003. Absorbs DOM-007 §3–§6 in full.

- **NFR-9 Accessible, legible presentation.** *(Added 2026-10-23: the load-bearing rules below —
  belief not truth, affordances reflect permission, kinetic confirmation — are verified in a real
  browser by an automated suite, owner decision `BL-0304` → `NFR-2840`.)*
  - Affiliation and confidence are conveyed by shape and label, never color alone; a high-contrast
    presentation mode exists for projector and classroom use; common actions have keyboard
    shortcuts, extended consistently (`j/k/c/g`) rather than forked per feature.
  - **Intentional vs accidental friction.** The tool is deliberately hard where the domain is hard:
    access windows, fog-of-war, kinetic confirmation. Every other difficulty is accidental friction
    to be removed. A design that adds friction must say which kind it is and justify intentional
    friction by the training objective.
  - **Belief is visibly not truth.** A cell's custody and confidence picture is distinguishable
    from ground truth at a glance.
  - **Causes are surfaced, not just values.** A moving telemetry value shows why it moves (the
    eclipse-drain precedent).
  - **Summary and detail agree.** A preview (sparkline, badge, thumbnail) shares data source,
    window and scaling with the view it previews.
  - **Affordances reflect actual permission.** An action the engine can already tell will fail is
    disabled before the click, with the reason (`dry_run()`), not refused after it.
  - **Panels follow the panel-manager contract.** Every panel can be closed, floated, resized and
    reset to dock from its first release.
  - **In-world AI is legible to White Cell.** The facilitator can see which Red doctrine preset is
    active and what behavior to expect (DOM-008 §3, third bullet).

  *(→ `NFR-3000` covers the first bullet only; the rest have no leaf — gap G4)*
- **NFR-10 Classification hygiene.** The White-Cell-selected classification banner renders on every
  screen and every exported file; default content is unclassified and fictional. *(→ `NFR-3100`;
  FR-W5)*

## 8. Training-corpus and documentation quality

Traces to MSTR-001 §2 (training corpus as co-equal product, 2026-07-04); GDS-01
"Training-corpus elevation".

- **NFR-17 Training-artifact quality.** Training artifacts describe only as-built behavior and
  change in the same change set as the behavior they document; modules stay single-topic and
  retrievable; presentation suits semi-technical operators, with pedagogical choices grounded in
  the R600 tier. *(→ `NFR-3400`, `NFR-3500`, `NFR-3600`)*
- **NFR-18 Documentation integrity** *(new, `BL-0297`, owner decision 2026-10-20).* The live
  documentation tree is mechanically consistent, and an automated suite that runs with the rest of
  the tests proves it, so package verification gates on it and integration review and release
  readiness cite its result as evidence:
  1. every relative link in a live document resolves to an existing file;
  2. no live document references a path or ID recorded in a retired-documents register;
  3. each `INDEX.md` agrees with the files in its folder;
  4. the status ledgers agree (`ROADMAP.md`, the Master Build Plan, the package index,
     `architecture/INDEX.md` §1, the feature index);
  5. training `Sources:` footers resolve to real code (the existing `NFR-3400` check).

  Frozen history — the pipeline journal's run log and archives, Verification Reports, review
  reports and ADR decision records — is exempt: it records what was true when written. Prose
  accuracy is not mechanically checkable and stays with human review (`10-integration-review`'s
  documentation-coherence dimension, `09-training-manual-review`). **Current state:** a read-only
  scan on 2026-10-19 found 82 broken relative links across 10 live files, so the suite's first
  green run includes that cleanup. *(→ no leaf — gap G5; `test_training_sources.py` is the
  precedent for item 5)*
- **NFR-19 Model credibility (verification is not validation)** *(absorbs DOM-005 §3–§4).* Tests
  verify that the engine matches its own specification; they do not show that the specification
  behaves plausibly. Every moderate-fidelity behavior that a training lesson depends on (power
  budget, custody decay, jam and engagement outcomes) is validated by comparing simulated
  quantities against reference values cited in the research encyclopedia, recorded as an explicit
  comparison (the June 2026 power-model recalibration is the worked precedent), never as a
  "looks reasonable" judgment. Assessment-instrument validation (DOM-005 §5) is a feature-level
  method for FS-201, not a system quality attribute, and is not absorbed here. *(→ no leaf — gap
  G6)*

Observability has no tag: no source commits to a metrics or tracing surface; the clock-lag
watchdog is a targeted reliability signal under NFR-2 (`CNFR-01` stays a candidate).

---

## Load-bearing invariant traceability

The merge gate requires every `CLAUDE.md` invariant with a non-functional character to be
traceable from here.

| Invariant (`CLAUDE.md`) | Quality tag | Leaf / FR | ADR | Enforcing check |
|---|---|---|---|---|
| 1. Deterministic core | NFR-3 | `NFR-1500`, `NFR-2400`; `FR-1120` | ADR-0002, ADR-0030 | `test_determinism.py` |
| 2. UI-agnostic engine | NFR-7 | `NFR-1900` | ADR-0001, ADR-0023 | `test_import_guard.py` |
| 3. Fog-of-war at the boundary | NFR-5 (trust boundary) | `NFR-2300`; `FR-6210`, `FR-6220` | ADR-0004, ADR-0015 | `test_scene.py`, `test_controller_view.py`, `test_defensive_audit_2026.py` |
| 4. Plan-first | — (functional) | `FR-3110` (GDS-05 FR-P) | ADR-0005 | order-system tests |
| 5. Sub-stepped clock | NFR-11 | `NFR-1700` | ADR-0006 | `test_clock_and_time.py` |
| 6. Content is data | NFR-7 | `NFR-2000`, `NFR-2010` | ADR-0007 | vignette load tests |
| (codebase rule) Replay-safe reads | NFR-13 | none — G1 | — | per-module tests only |
| (ADR rule) Failure-atomic events | NFR-6 | none — G2 | ADR-0038 | `test_failure_atomic_events.py` |

Plan-first is behavioral, not a quality attribute, so it is stated in GDS-05 and only listed here
for completeness.

## Gaps handed to 04

*Applied 2026-10-23 by `04-requirements-engineering`, run #211 (`BL-0298` done): G1 → `NFR-2410`,
G2 → `NFR-1610`, G3 → `NFR-3710`, G4 → `NFR-3010`–`NFR-3060`, G5 → `NFR-3800`–`NFR-3840`,
G6 → `NFR-2810`; corrections C1–C6 below applied to their leaves. See
[`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md).
The text below is kept as the hand-off record.*

Attributes this document states that have no `requirements/02` leaf. Each is for
`04-requirements-engineering` to derive as a leaf (or record why not):

- **G1 — Replay-safe reads (NFR-13).** Testable as: each read path leaves the world hash, RNG state
  and event-log length unchanged.
- **G2 — Failure-atomic event application (NFR-6, ADR-0038).** Already tested; needs its NFR leaf.
- **G3 — Bounded resource use on untrusted input (NFR-15).** Testable per cap.
- **G4 — Human-factors constraints (NFR-9, bullets 2–8).** Most are inspection-verified design
  constraints; `04` decides which become leaves and which stay design guidance.
- **G5 — Documentation integrity (NFR-18, `BL-0297`).** The candidate NFR this level exists to
  frame; verification is the automated suite described above.
- **G6 — Model credibility (NFR-19).** Verification method: a recorded comparison table per
  validated behavior.

## Leaf corrections handed to 04

`requirements/02` leaves whose text no longer matches the shipped system:

- **C1 — `NFR-1800`** says there is no mid-exercise save/resume across process restarts. FS-110 ships
  save and resume into a new process (`save`/`load_save`).
- **C2 — `NFR-3200`** (and ADR-0018) describe a Space-Track import at build time; none exists. Either
  reword to "no network access at all; Space-Track import is unbuilt" or file the import as a
  feature.
- **C3 — `NFR-2200`** verification method says dependency versions are pinned; they are minimum
  floors. Needs an owner decision: pin (with a lock file), or reword the requirement.
- **C4 — `NFR-1900`** asserts ≥80% engine coverage; nothing measures it. Either add a coverage tool to
  the suite or drop the figure.
- **C5 — `NFR-2700`** names only host/port/reload; the configuration file now also carries the
  `content:` section (IP-1180).
- **C6 — every leaf's Source documents field** cites `build-spec/04` §9 `NFR-n`; add the GDS-06 tag
  alongside, as `requirements/01` did when GDS-05 closed (that document's own open issue 4).

## Open Questions

- ~~**OQ1 — Dependency pinning (C3).**~~ **Resolved 2026-10-23 (owner, `BL-0299`):** minimum
  versions during development; every dependency locked to an exact version at each release
  (`NFR-1510`). Refined 2026-10-24 (`BL-0318`): the word "major" is dropped; the lock and the
  relevance audit apply at every release, reviewed in `11-release-readiness`.
- ~~**OQ2 — Coverage measurement (C4).**~~ **Resolved 2026-10-23 (owner, `BL-0299`):** no coverage
  target; tests must show features and requirements are satisfied, and declare what they verify
  (`NFR-2820`, `BL-0310`).
- ~~**OQ3 — Space-Track import (C2).**~~ **Resolved 2026-10-23 (owner, `BL-0299`):** dropped. The
  application makes no network call; ADR-0018 carries a revision note.
- **OQ4 — Numeric performance targets.** No source states a frame-rate or latency number for NFR-2 or
  NFR-4 (`CNFR-02`). Left qualitative until a measured baseline exists.
- **OQ5 — Accreditation horizon.** NFR-5's "nothing that blocks a later RMF/ITSG-33 review" and the
  accepted unauthenticated cell selection are each consistent for v1 but conflict at an
  accreditation horizon. Carried from `requirements/02`'s open issue 2; not adjudicated here.
- ~~**OQ6 — Single-exercise wording (GDS-05 OQ2).**~~ **Resolved 2026-10-22:** GDS-05's OR-6 was
  reworded to the multi-session reality and its OQ2 closed; `NFR-1800` was corrected in run #211.

## Departures from the legacy build-spec text

The GDS level is authoritative; these are stated so no one mistakes them for drift:

- `NFR-1`: the legacy text implies a Space-Track pull exists; as built there is no network call, and the pull is now dropped (`BL-0299`).
- `NFR-5`: "dependency pinning" is not the as-built posture (minimum versions; a lock at each release, `BL-0299`/`BL-0318`).
- `NFR-6`: extended with failure atomicity (ADR-0038), which postdates the legacy text.
- `NFR-7`: the 80% coverage figure was never measured and is withdrawn (no coverage target, `BL-0299`); schema additivity (`NFR-2010`) added.
- `NFR-9`: extended with the DOM-007 human-factors constraints.
- `NFR-11`–`NFR-19`: new tags for attributes the legacy list never named.

## Merge gate (closed)

- [x] **Absorbed §9 of `build-spec/04-nfr-milestones-and-risks.md`.** All ten legacy tags
  (`NFR-1`…`NFR-10`) are restated above under their original numbers, each reconciled with the
  shipped system and mapped to its `requirements/02` leaves; every departure is listed in
  "Departures from the legacy build-spec text".
- [x] **Cross-checked against `CLAUDE.md`'s load-bearing invariants.** Every invariant with a
  non-functional character (determinism, UI-agnostic engine, fog-of-war, sub-stepped clock,
  content-as-data) is traceable in the invariant table above, together with two codebase rules
  that act as invariants (replay-safe reads, failure-atomic events). Plan-first is functional and
  stays in GDS-05.
- [x] **Reconciled with `requirements/02` instead of restarting it.** Every one of its 28 numbered
  leaves (`NFR-1100`…`NFR-3700`) maps under a tag above. Six leaf corrections (C1–C6) and six gaps
  (G1–G6) are handed to `04`; none is resolved by editing `requirements/02` here.
- [x] **DOM content absorbed (`BL-0293`).** Absorbed: DOM-005 §3, §4 and §6 (into NFR-19 and
  NFR-3); DOM-007 §3, §4, §5 and §6 (into NFR-9); DOM-008 §3 (into NFR-3, NFR-7 and NFR-9). Not absorbed,
  and why: DOM-005 §5 (assessment-instrument validation — a feature-level method for FS-201);
  DOM-006 (content and feature governance — process, not a system quality attribute; belongs with
  the MSTR governance documents `01-vision` now owns); DOM-001–004 and DOM-009 (no non-functional
  content).
- [x] **Decision recorded:** consistent with GDS-05 and the blanket supersession in `CLAUDE.md`,
  **this document is the authoritative non-functional statement**, and `build-spec/04` §9 is
  superseded. `build-spec/04` is not edited here: it is retired as a whole once GDS-10 closes
  (`BL-0292`), and until then `CLAUDE.md` and `architecture/INDEX.md` already mark it legacy and
  non-binding. `requirements/02` stays the leaf-level elaboration, exactly as `requirements/01` is
  for GDS-05; its pending corrections are C1–C6.

## Next

`GDS-07` (Data Model) may now begin. `04-requirements-engineering` owes gaps G1–G6 and corrections
C1–C6 (both applied in run #211); Open Questions OQ1–OQ3 were decided by the owner on 2026-10-23 (`BL-0299`).
