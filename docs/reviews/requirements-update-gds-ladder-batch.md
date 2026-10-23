# Requirements update — GDS ladder alignment batch (2026-10-23)

> **Pass:** `04-requirements-engineering`, pipeline run #211 (delta update, not a fresh baseline).
> **Inputs:** [GDS-06](../architecture/06-non-functional-requirements.md) "Gaps handed to 04" (G1–G6)
> and "Leaf corrections handed to 04" (C1–C6); [GDS-10](../architecture/10-requirements-traceability-matrix.md)
> §6 findings F2–F5; GDS-07, GDS-08 and GDS-09 Open Questions; owner decisions recorded in
> [`docs/pipeline/backlog.md`](../pipeline/backlog.md): `BL-0299` (Space-Track dropped, no coverage
> target, dependencies locked at major releases), `BL-0302` (self-contained saves), `BL-0304`
> (browser test suite), `BL-0307` (White-only controls enforced server-side), `BL-0310` (test
> origin traceability and a major-release relevance audit).
> **Input mapping (skill roles → this repository):** Concept of Operations, System Context,
> Architecture, Domain Model → GDS-01…GDS-04; functional and non-functional statements → GDS-05 and
> GDS-06 (authoritative; the leaves here elaborate them); data, UI and API → GDS-07, GDS-08, GDS-09;
> ADRs → `docs/architecture/adr/`. Output files follow this repository's existing layout:
> `01-functional-requirements.md`, `02-non-functional-requirements.md`, the traceability matrix in
> `03-requirements-traceability-matrix.md`, this report, and `requirements-change-log.md`.

[↑ Reviews](../INDEX.md) · [Requirements](../requirements/01-functional-requirements.md)

## 1. What changed

**Functional (`01`), 104 → 106 leaves**
- **Added `FR-4320`** — White Cell lifecycle and facilitation controls refused for other seats
  (`BL-0307`).
- **Added `FR-7230`** — a save resumes independently of its original vignette file (`BL-0302`).
- **Reworded `FR-5210`** — "Manual TLE and Keplerian asset entry"; the Space-Track import is dropped
  (`BL-0299`). Same ID, narrower scope.
- **Notes on `FR-4310` and `FR-7220`** — both are recorded as verified, and neither is met as built
  (findings R1, R2).

**Non-functional (`02`), 28 → 47 leaves**
- **Gaps closed (GDS-06 G1–G6):**
  - `NFR-2410` read paths leave state unchanged (G1);
  - `NFR-1610` failure-atomic event application (G2);
  - `NFR-3710` bounded work on untrusted input (G3);
  - `NFR-3010`–`NFR-3060` human-factors constraints (G4);
  - `NFR-3800`–`NFR-3840` documentation integrity (G5, `BL-0297`);
  - `NFR-2810` fidelity claims validated against cited references (G6).
- **Owner decisions:**
  - `NFR-1510` dependencies locked at each major release (`BL-0299`);
  - `NFR-2820` every test declares its origin (`BL-0310`);
  - `NFR-2830` relevance audit at each major release (`BL-0310`);
  - `NFR-2840` load-bearing UI rules verified in a browser (`BL-0304`).
- **Corrections (GDS-06 C1–C6):**
  - `NFR-1800` now states save/resume across processes and several sessions per process (C1);
  - `NFR-3200` no network access at all, import by paste or file (C2);
  - `NFR-2200` minimum versions during development, locked at major releases (C3);
  - `NFR-1900` the 80% coverage figure is removed (C4);
  - `NFR-2700` the `content:` configuration section is added (C5);
  - every leaf now cites its GDS-06 tag first (C6).
- `NFR-3600`'s stale "R600 0/8" rationale is corrected. Section 16 is renamed to include
  documentation integrity.

**Traceability matrix (`03`)**
- **Rows:** 21 rows added. `FR-5210`, `NFR-1900` and `NFR-3200` reworded. `FR-3120`'s title
  corrected: it read "Sensor tasking" for a leaf about cancellation before uplink. `FR-4310` and
  `FR-7220` marked not met as built. Six foundational leaves marked as pre-package builds (GDS-10
  F4).
- **Header and indexes:** the header now names GDS-10 as authored (F2). The Requirement → Test note
  explains that the column will be filled from `@pytest.mark.verifies(...)` markers. The
  Requirement → Implementation Package note no longer claims that no feature/package convention
  exists (F2).

No Candidate Requirement was added or promoted.

## 2. Findings

| # | Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| R1 | Requirement lacking verification (a verified requirement is not met) | `FR-4310`, `IP-1060`, VR-1060 | `FR-4310` requires that a Blue or Red clock-control request be rejected. `IP-1060` states the requirement is "enforced at the `SessionAPI` layer", and VR-1060 accepted it, but no code enforces it and `test_session.py` does not assert the refusal. The server accepts `/clock`, `/step`, `/advance`, `/rewind` and `/undo` from any non-Observer seat (GDS-09 §4). | **High** | `07`: a remediation package for `FR-4310` and `FR-4320` together (`BL-0307`), with tests that assert the refusals. `09`: note the lesson that a package's enforcement claim must be checked against a test asserting it. |
| R2 | Requirement lacking verification (a verified requirement is not met) | `FR-7220`, VR-1100 | `FR-7220` requires the save's content portion to be extractable and re-importable on its own. The save carries only the vignette ID and parameter overrides (GDS-07 §6). VR-1100's test checks the round trip, not the content split. | Medium | `06`: specify `FR-7230` (self-contained saves, `BL-0302`), which also satisfies `FR-7220`; the spec should state how. |
| R3 | Requirement lacking verification | `NFR-1300` | Its verification names a clock-lag watchdog test that does not exist (GDS-10 F1). | Low | `07`: add the test (`BL-0309`), tagged `verifies("NFR-1300")`. |
| R4 | Conflict with architecture | `FR-5210`, `NFR-3200`, ADR-0018 | ADR-0018 still describes an optional build-time Space-Track pull; the owner dropped it and the requirements now say no network call at all. | Low | `03`: add a revision note to ADR-0018. |
| R5 | Conflict with architecture (wording) | GDS-06 NFR-5, NFR-7, OQ1–OQ3 | GDS-06 still says "pinning" is open, keeps the 80% figure as a correction, and lists OQ1–OQ3 as open; all three are now decided. | Low | `03`: update GDS-06 at its next touch (the decisions are recorded on `BL-0299`). |
| R6 | Missing requirement (deliberately not added) | DOM-007 §3 (as absorbed in GDS-06 NFR-9) | The rule that every console design states which friction is intentional is a design-process rule for specifications, not a quality of the running system, so no NFR was written for it. | Low | Owner or `06`: decide whether it belongs in the feature-specification template; until then it stays as guidance in GDS-06 NFR-9. |
| R7 | Dependency not yet in place | `NFR-2840` | The browser suite needs a headless browser in the test environment. The walkthrough tool uses one, but it is not in the project's dependency list or the new session hook. | Low | `06`: the browser-suite spec should name the tooling and how the suite runs (in the default run, or separately). |
| R8 | Traceability gap (expected) | `NFR-2820`, all Test cells | No test carries a `verifies` marker yet, so the Test column cannot be filled from markers. | Low | `07`→`08`: the registration and backfill package (`BL-0310`). |
| R9 | Derived artifact now stale | GDS-10 §4–§5 | GDS-10's tables predate the 21 leaves added here. | Low | `03`: regenerate GDS-10's table at the next `03` pass (GDS-10 §7). |

**Checked, no finding.** No new leaf duplicates an existing one, and none contradicts an Accepted
ADR other than R4. Each new leaf has a Source Documents citation to a section, and each Priority
uses MoSCoW. No new numeric target was introduced: the caps in `NFR-3710` are the shipped values,
cited from GDS-06 and GDS-09, not invented ones.

## 3. Next

Findings R1–R9 route as stated. Candidates for `06` specifications: self-contained saves
(`FR-7230`), the browser test suite (`NFR-2840`), and test-origin registration and backfill
(`NFR-2820`). Candidates for `07` remediation: `FR-4310`/`FR-4320` enforcement (`BL-0307`), the
panel registration (`BL-0305`, `NFR-3030`) and the watchdog test (`BL-0309`, `NFR-1300`).
