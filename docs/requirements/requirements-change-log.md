# Requirements Change Log

A record of every change applied to the requirements/ICD baseline in response to
[`docs/reviews/requirements-review.md`](../reviews/requirements-review.md). Each entry below
corresponds to one edit (an added leaf, an added field value, or a modified field) made to one of
the three documents the review's findings were applied against:

- [`docs/requirements/01-functional-requirements.md`](01-functional-requirements.md)
- [`docs/requirements/02-non-functional-requirements.md`](02-non-functional-requirements.md)
- [`docs/design/05-interface-control-document.md`](../design/05-interface-control-document.md)

**Scope discipline applied throughout:** no new capability was introduced. Every change either (a)
promotes a behavior already described in an approved source document (GDS architecture ladder,
an Accepted ADR, or `build-spec/`) into a checkable leaf/field that did not previously exist, (b)
adds a qualitative disclosure of an already-decided trade-off, or (c) corrects/backfills a
cross-reference. Numbering stability was maintained: every new FR leaf uses the existing
gap-numbering convention (a new `x20`/`x10`/`x600` slot under its existing parent group); no
existing FR/NFR ID was renumbered or removed.

**Two findings could not be applied as literally stated**, because re-reading the current on-disk
text did not reproduce the review's premise. Both are recorded honestly below (CHG-003, CHG-005)
rather than silently skipped or force-fitted.

---

## requirements/01-functional-requirements.md

### CHG-001
- **Previous state:** FR-3510's Related Requirements field read `FR-2410, FR-3110`.
- **New state:** `FR-2410, FR-3110, FR-3520`.
- **Reason:** Cross-reference the new sibling leaf (CHG-002) that states the Role Assignment
  cardinality rule FR-3510 only describes a consequence of.
- **Source review issue:** REQ-072 / REQ-080.

### CHG-002
- **Previous state:** No leaf existed stating the Role Assignment bus/payload/both cardinality
  rule itself; GDS-05 OR-2 and GDS-04 §1.10 described the rule only in prose, folded entirely into
  FR-3510's scope statement (which covers only the UI command-filtering consequence).
- **New state:** Added **FR-3520 — Role Assignment scoping: bus-only, payload-only, or both**, a
  new leaf under FR-3500, stating the cardinality rule as its own testable system behavior with
  its own Acceptance Criteria, distinct from FR-3510.
- **Reason:** FR-3510 describes a consequence, not the rule; no leaf existed a tester could check
  to verify the cardinality rule is enforced independent of the order-panel filtering it produces.
- **Source review issue:** REQ-072 / REQ-080.

### CHG-003
- **Previous state:** GDS-05 FR-W7 ("White Cell shall be able to set the safe-mode dials and other
  live parameters mid-exercise") is mapped "→ FR-4710 scope," but FR-4710's actual on-disk content
  is entirely about no-automated-scoring/manual adjudication and contains no language about
  safe-mode dials or live parameters at all.
- **New state:** Added **FR-4720 — Adjust safe-mode dials and other live exercise parameters
  mid-exercise**, a new sibling leaf under FR-4700, carrying FR-W7's actual content (including an
  explicit statement that "other live parameters" is an intentionally open-ended set, not an
  enumeration omission). FR-4710 itself was left unchanged.
- **Reason:** The review's REQ-051 finding attributed the "other live parameters" ambiguity to
  FR-4710, but on re-reading FR-4710's current text this is inaccurate — FR-4710 never contained
  FR-W7's content. The real gap was that no leaf anywhere in `requirements/01` carried FR-W7's
  substance at all (it was cross-mapped to FR-4710's scope but a corresponding leaf was never
  written). Editing FR-4710 to add unrelated language would have been incorrect; adding the
  missing sibling leaf is the faithful fix. This deviates from REQ-051's literal recommended
  resolution (which assumed editing FR-4710) but resolves the same underlying ambiguity.
- **Source review issue:** REQ-051 (applied with a corrected target, per the discrepancy above).

### CHG-004
- **Previous state:** No `FR-6xxx` leaf covered the hot-seat screen-blank/hand-off menu (GDS-05
  OR-3); GDS-05's own Open Question 1 (OQ1) records this gap, and it was otherwise documented only
  as prose in `CLAUDE.md`'s "LAN trust model" section.
- **New state:** Added a new group **FR-6600 — Hot-seat hand-off and screen-blank menu** containing
  **FR-6610 — Screen-blank pending-handoff menu between hot-seat role changes**, under FR-6000,
  after FR-6500.
- **Reason:** Promotes an already-decided behavior (named in GDS-05 OR-3) to a checkable leaf,
  closing GDS-05 OQ1 at the requirements-baseline side.
- **Source review issue:** REQ-010 / REQ-081.

### CHG-005
- **Previous state:** REQ-031 stated that some FR-6xxx leaves cite "no Related Interfaces entry at
  all." On re-reading the current text, this premise did not reproduce: every existing FR-6xxx
  leaf (FR-6110, FR-6210, FR-6220, FR-6310, FR-6320, FR-6410, FR-6510) already had at least one
  Related Interfaces entry. The real, narrower gap was citation *density* — most FR-6xxx leaves
  cited only one interface where the FR-9xxx/FR-3xxx clusters typically cite two (the specific
  engine-facing interface plus the SessionAPI seam, INT-0006, that mediates it).
- **New state:** Backfilled `INT-0006` onto FR-6210 (`INT-0007` → `INT-0006, INT-0007`), FR-6310
  (`INT-0001` → `INT-0001, INT-0006`), FR-6410 (`INT-0001` → `INT-0001, INT-0006`), and FR-6510
  (`INT-0005` → `INT-0005, INT-0006`) — each of these leaves' behavior is in fact mediated through
  the SessionAPI seam per FR-6110, so the addition is accurate, not invented.
- **Reason:** Matches citation density already present in the FR-9xxx/FR-3xxx clusters, per
  REQ-031's intent, applied against the actual (narrower) gap found on re-reading rather than the
  review's literal "no entry at all" framing.
- **Source review issue:** REQ-031.

### CHG-006
- **Previous state:** FR-7210's Related Requirements field read `FR-7110, FR-4410`.
- **New state:** `FR-7110, FR-4410, FR-7220`.
- **Reason:** Cross-reference the new sibling leaf (CHG-007) asserting the save-file ownership
  split FR-7210 assumes but does not itself state.
- **Source review issue:** REQ-082.

### CHG-007
- **Previous state:** No leaf in `requirements/01` directly stated the save-file content/session
  ownership split (ADR-0022) as an enforced, testable system behavior; ICD §7 issue 4 records this
  as resolved-in-principle by ADR-0022 but never promoted to a checkable FR.
- **New state:** Added **FR-7220 — Save-file content/session ownership split**, a new sibling leaf
  under FR-7200, citing ADR-0022 and ICD §7 issue 4 directly, with its own Acceptance Criteria.
- **Reason:** ADR-0022 intends the split as an enforced invariant, not merely a documentation
  clarification; this closes the gap between the ADR's intent and the FR baseline's silence on it.
- **Source review issue:** REQ-082.

### CHG-008
- **Previous state:** FR-9110's Rationale cited only ADR-0021/the unseated-Red substitution
  rationale, with no sentence explaining why AI-Red alone carries "Should" priority while sibling
  FR-9xxx-adjacent leaves are "Must," and no disclosure of the AI-Red/human-Red epistemic-parity
  gap at this leaf (the review's REQ-071 claimed this disclosure already existed in a "Notes"
  field; on re-reading, no such field or disclosure exists anywhere in FR-9110's current text).
- **New state:** Extended FR-9110's Rationale with two sentences: one justifying the Should tier
  (a vignette remains fully playable without AI-Red, unlike Must-tier dependencies), and one
  disclosing the AI-Red ground-truth-read epistemic asymmetry as an intentional, ADR-0024-tracked
  v1 trade-off, citing `FUTURE-WORK.md` §1.
- **Reason:** REQ-023 (Should-priority justification) plus a corrected application of REQ-071
  (the fairness disclosure REQ-071 assumed already existed did not; it has now actually been
  added).
- **Source review issue:** REQ-023; REQ-071 (applied with a corrected premise, per the discrepancy
  above).

### CHG-009
- **Previous state:** FR-9110's Preconditions read only "Red's seat is configured to use an AI-Red
  preset," not stating whether this is exclusive of a concurrently human-seated Red.
- **New state:** Extended to state the configuration is mutually exclusive with a human operator
  concurrently occupying the same Role Assignment — AI-Red substitutes for an unseated Red rather
  than running as a parallel, simultaneous source.
- **Reason:** Neither the ICD, GDS-04 §1.10, nor FR-9110 previously stated this interaction
  explicitly, even though it is implied by existing "substituting for an unseated... Red cell"
  language; this makes the implication explicit rather than assumed.
- **Source review issue:** REQ-101.

---

## requirements/02-non-functional-requirements.md

### CHG-010
- **Previous state:** No Candidate NFR addressed AI-Red epistemic parity/fairness as a quality
  attribute; the Candidate Requirements section ran `CNFR-01`–`CNFR-05`.
- **New state:** Added **CNFR-06 — AI-Red epistemic parity / fairness as a quality attribute**,
  excluded for the same reason ADR-0024 treats remediation as future-work, cross-referencing
  `requirements/01` FR-9110 (CHG-008).
- **Reason:** The NFR document's fixed 15-category taxonomy has no Fairness-equivalent category,
  and the FR-side disclosure (CHG-008) was not previously mirrored at the NFR/quality-attribute
  level; adding a Candidate entry (non-binding, already-excluded) records the gap without
  committing to a new binding requirement.
- **Source review issue:** REQ-071.

### CHG-011
- **Previous state:** Completion report read "Candidate requirement count: 5 (`CNFR-01`…
  `CNFR-05`)."
- **New state:** "Candidate requirement count: 6 (`CNFR-01`…`CNFR-06`)."
- **Reason:** Housekeeping consistency update following CHG-010.
- **Source review issue:** REQ-071 (housekeeping consequence).

### CHG-012
- **Previous state:** Completion report Open issue 1 read "...Not re-resolved here; see GDS-05's
  own Open Questions." (no explicit OQ ID), independently of NFR-1800's own blockquote which
  already cited "GDS-05 OQ2" by name.
- **New state:** Tightened to cite "(OQ2)" explicitly, and added a note that the cross-reference is
  currently one-directional (this document cites GDS-05 OQ2; GDS-05 OQ2 does not cite this
  document back), with closing the converse direction flagged as out of scope here since it
  requires editing GDS-05 itself.
- **Reason:** REQ-021/REQ-060 found two independent "open issue" trails for the same fact. On
  re-reading, `requirements/02` already partially satisfies this (NFR-1800's blockquote already
  names "GDS-05 OQ2") — the residual, actionable gap within this document's scope was only the
  Completion report's looser citation and the missing explicit note about the remaining
  one-directional asymmetry. The fully bidirectional fix (editing GDS-05 to cite back) is outside
  this task's authorized file set (`requirements/01`, `requirements/02`, the ICD) and is not
  applied here.
- **Source review issue:** REQ-021 / REQ-060 (partially applied; residual gap is out of scope for
  this edit pass — see Reason).

---

## docs/design/05-interface-control-document.md

### CHG-013
- **Previous state:** INT-0015's Preconditions read only "Red's seat is configured to use an
  AI-Red preset rather than a human operator," not stating whether this precludes a concurrently
  human-seated Red on the same Role Assignment.
- **New state:** Extended to state explicitly that this precondition is mutually exclusive with a
  human operator concurrently occupying the same Role Assignment for Red — AI-Red substitutes for
  an unseated Red rather than running as a parallel, simultaneous ground-truth-read source —
  mirroring the matching `requirements/01` FR-9110 Preconditions edit (CHG-009).
- **Reason:** Neither the ICD, GDS-04 §1.10, nor FR-9110 previously stated this interaction
  explicitly; this closes the gap identified at the interface-control level, consistent with the
  matching FR-side edit.
- **Source review issue:** REQ-101.

---

## Training-corpus elevation (2026-07-04) — new FR family + NFR section

Unlike CHG-001–CHG-013 (edits responding to `requirements-review.md`), this batch responds to an
**explicit project-owner decision** (recorded in `MSTR-001` §2 and the GDS-00/GDS-01
"Training-corpus elevation (2026-07-04)" sections) elevating the training corpus — manuals,
vignette learning path, briefs/tutorials — to a co-equal, requirement-bearing product with the
code. Numbering stability maintained: a new top-level family after the existing highest
(`FR-10000` → `FR-11000`), a new NFR section after the existing highest (§15 → §16,
`NFR-3300` → `NFR-3400`–`NFR-3600`); no existing FR/NFR ID renumbered, removed, or altered.

### CHG-014
- **Previous state:** No functional requirements existed for the training corpus; manuals and the
  vignette library's pedagogical sequencing were untracked by the baseline.
- **New state:** `requirements/01` gains the `FR-11000 — Training Corpus & Learning Path` family:
  `FR-11110` (role-scoped coverage), `FR-11120` (source anchoring), `FR-11210` (bidirectional
  index), `FR-11310` (sequenced learning path), `FR-11320` (per-rung manual linkage), `FR-11410`
  (currency rides the changing package), `FR-11420` (machine-verified playbooks — promoting the
  existing `test_vignette_tutorials.py` practice to requirement status). The family's preamble
  states explicitly that the current per-cell manual layout satisfies but is not mandated by
  `FR-11110`.
- **Reason:** Owner instruction 2026-07-04; MSTR-001 §2/§5 amendment in the same pass.
- **Source review issue:** N/A — owner-directed baseline extension, not a review finding.

### CHG-015
- **Previous state:** No NFRs constrained training-artifact quality.
- **New state:** `requirements/02` gains §16 "Training-artifact quality": `NFR-3400` (accuracy —
  as-built behavior only), `NFR-3500` (modularity/retrievability), `NFR-3600`
  (learner-appropriate presentation, R600-cited once that tier authors).
- **Reason:** Same owner instruction; the *how well* face of CHG-014's family.
- **Source review issue:** N/A — owner-directed baseline extension.

### CHG-016
- **Previous state:** The RTM carried no rows for training artifacts.
- **New state:** `requirements/03` gains master-matrix rows for `FR-11110`–`FR-11420` and
  `NFR-3400`–`NFR-3600`, with an explanatory note on how documentation-artifact rows populate
  cells honestly (real doc paths in Impl. Package cells; `(none)`/`UNASSIGNED` for
  component/interface cells no ICD entry models; R600 not citable until topics author).
- **Reason:** Keep the matrix complete over the extended baseline in the same change set.
- **Source review issue:** N/A — owner-directed baseline extension.

---

## GDS ladder alignment (2026-10-23) — `01`, `02`, `03`

Full derivation and findings: [`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md).

### CHG-017
- **Files:** `01-functional-requirements.md`
- **Change:** Added `FR-4320` (White Cell controls refused for other seats) and `FR-7230` (resume
  independent of the original vignette file). Reworded `FR-5210` to manual TLE/Keplerian entry
  (Space-Track dropped). Added "not met as built" notes to `FR-4310` and `FR-7220`.
- **Reason:** Owner decisions `BL-0307`, `BL-0302`, `BL-0299`; GDS-07 §6 and GDS-09 §4.
- **Source review issue:** R1, R2, R4.

### CHG-018
- **Files:** `02-non-functional-requirements.md`
- **Change:** Added 19 leaves: `NFR-1510`, `NFR-1610`, `NFR-2410`, `NFR-2810`–`NFR-2840`,
  `NFR-3010`–`NFR-3060`, `NFR-3710`, `NFR-3800`–`NFR-3840`. Corrected `NFR-1800`, `NFR-1900`,
  `NFR-2200`, `NFR-2700`, `NFR-3200` and `NFR-3600`. Every leaf now cites its GDS-06 tag first.
- **Reason:** GDS-06 gaps G1–G6 and corrections C1–C6; owner decisions `BL-0299`, `BL-0304`,
  `BL-0310`.
- **Source review issue:** R3, R5–R8.

### CHG-019
- **Files:** `03-requirements-traceability-matrix.md`
- **Change:** 21 rows added; `FR-5210`, `NFR-1900`, `NFR-3200` reworded; `FR-3120` title corrected;
  `FR-4310`/`FR-7220` marked not met as built; six foundational leaves marked pre-package; the header
  and the Test and Implementation Package index notes corrected.
- **Reason:** Keep the matrix complete over the extended baseline; GDS-10 findings F2 and F4.
- **Source review issue:** R1, R2, R8, R9.

## Generated Test column (2026-10-23, `BL-0322`) — `02`, `03`

Owner request: make test↔origin traceability bidirectional by generating the matrix's Test column
from the tests' declared origins. Review: [`reviews/requirements-update-bl-0322.md`](../reviews/requirements-update-bl-0322.md).

### CHG-020
- **Files:** `02-non-functional-requirements.md`
- **Change:** Added `NFR-2850` (§12 Testing). Removed test-file names from the verification text of
  `NFR-1610`, `NFR-1800`, `NFR-2010`, `NFR-2810`, `NFR-3020`, `NFR-3200` and `NFR-3710`, replaced by
  a pointer to the generated Test column. Kept the names where the test is the requirement's subject
  (`NFR-1500`/`NFR-1900`/`NFR-2400`/`NFR-2800`'s permanent gates; `NFR-3400`'s playbook test;
  `FR-11420`). **Removed names, as hints for the backfill:** `NFR-1610` → `test_failure_atomic_events.py`;
  `NFR-1800` → `test_session_features.py`, `test_web.py`; `NFR-2010` → `test_content.py`,
  `test_vignette_tutorials.py`; `NFR-2810` → `test_power_calibration.py`; `NFR-3020` →
  `test_validate_order.py`; `NFR-3200` → `test_bulk_import_session.py`, `test_content.py`;
  `NFR-3710` → `test_defensive_audit_2026.py`, `test_ephemeris.py`, `test_vignette_creator_session.py`.
- **Reason:** `BL-0322`; a hand-kept copy of requirement → test drifts.
- **Source review issue:** U1.

### CHG-021
- **Files:** `03-requirements-traceability-matrix.md`
- **Change:** Added row `NFR-2850`; header note that the Test column is to be generated and that its
  current cells are hand-filled hints until `IP-1330` exists.
- **Reason:** `BL-0322`.
- **Source review issue:** U2.

## Baseline-maintenance pass 1 (2026-10-24) — `01`, `02`, `03`

Owner-decided and stale-note items from the backlog and the tranche-2 integration review
([`reviews/integration-review-tranche-2-white-controls-saves-test-origins.md`](../reviews/integration-review-tranche-2-white-controls-saves-test-origins.md)
F-02, F-07). No new capability: three new leaves restate behavior the build already ships or an owner
decision already made. This repository has no standalone `03-requirements-review.md` (the
requirements-review role is filled by [`reviews/requirements-review.md`](../reviews/requirements-review.md)
and the per-batch reports in `reviews/`); this pass's review findings are recorded in "Review findings,
pass 1" below instead of in a new file.

### CHG-022
- **Files:** `01-functional-requirements.md`, `03-requirements-traceability-matrix.md`
- **Change:** Added `FR-7450` (ISO-8601 UTC span bounds on the time-span exports), promoting candidate
  `CR-22` (marked `PROMOTED` in place). Added `FR-7450` to the Related Requirements of `FR-2320`,
  `FR-7410`, `FR-7420`. New RTM row; `CR-22` row annotated. Marked **not yet built**.
- **Reason:** Owner decision on `BL-0181`, 2026-10-18 (human-readable timestamps).
- **Source review issue:** CR-22.

### CHG-023
- **Files:** `01-functional-requirements.md`, `03-requirements-traceability-matrix.md`
- **Change:** `FR-1610` Acceptance Criteria amended from "detects more transiting objects" to the
  gain/footprint trade with unchanged access windows; Notes record the history; Source Documents add
  `BL-0215`.
- **Reason:** Owner decision (A) on `BL-0215`, 2026-10-18; matches the build and `VR-1220`. Resolves
  finding F2 of the load-validation batch.
- **Source review issue:** F2 (load-validation batch).

### CHG-024
- **Files:** `01-functional-requirements.md`, `03-requirements-traceability-matrix.md`
- **Change:** `FR-4320` scope extended: refuse Blue, Red and Observer requests to fire, edit or cancel
  an inject, create a session or a Vignette Creator draft, edit a draft (state, assets, seat
  declaration), save a draft or session as a vignette or scenario, or trigger the Red AI step. Player
  routes (orders, compute and preview helpers, cancel, recovery, SSN) and cell-scoped reads are
  explicitly out of scope. Notes record that the original list is met (`IP-1068`) and the extension is
  not yet built; a `07` package is owed. Rationale, Source Documents, Related Requirements, AC and
  Postconditions updated.
- **Reason:** `BL-0321`, `BL-0324`, `BL-0351`; `VR-1068` F1; integration review tranche 2 F-02.
- **Source review issue:** F-02.

### CHG-025
- **Files:** `01-functional-requirements.md`, `03-requirements-traceability-matrix.md`
- **Change:** `FR-4310` and `FR-7220` Notes rewritten from "Not met as built" to "met as built" (with
  the history kept); `FR-7230` Notes record the shipped save format. RTM: `FR-7220` Impl. Package
  cell and `FR-7230` Future Feature cell (`FS-110`) made current; `NFR-2820`, `NFR-2830`, `NFR-2850`
  and `NFR-3840` cells updated from "COMPLETE, awaiting 09" to `VERIFIED` (`VR-1330`), and
  `NFR-2820` now names `IP-1331`–`IP-1333`.
- **Reason:** `BL-0325`, `BL-0329`, `BL-0356` (F-07). The GDS-10 `FR-W3` row and GDS-07 §6 are not
  this stage's to edit (see findings).
- **Source review issue:** F-07.

### CHG-026
- **Files:** `02-non-functional-requirements.md`, `03-requirements-traceability-matrix.md`
- **Change:** `NFR-1510` and `NFR-2830` (and the `NFR-2200` cross-reference) no longer say "major"
  release: the dependency lock and the test relevance audit apply at every release and are reviewed
  at the end of the pipeline in `11-release-readiness`. Priorities read "Must (at each release)".
- **Reason:** Owner decision on `BL-0318`, 2026-10-24.
- **Source review issue:** BL-0318.

### CHG-027
- **Files:** `02-non-functional-requirements.md`, `03-requirements-traceability-matrix.md`
- **Change:** `NFR-3810` reworded: a retired document is deleted (no archive folder, no register
  file); git history is the archive; no live document names a deleted path or ID in plain text,
  except the supersession note that records the deletion. Title and RTM row updated.
- **Reason:** Owner decision on `BL-0319`, 2026-10-24. The register option is not adopted; the list
  of deleted paths lives in the supersession note.
- **Source review issue:** BL-0319.

### CHG-028
- **Files:** `02-non-functional-requirements.md`, `03-requirements-traceability-matrix.md`
- **Change:** `NFR-3830` narrowed from five named ledgers to the three pairs the check compares
  (Master Build Plan vs package index; `architecture/INDEX.md` §1 vs `ROADMAP.md`; feature index vs
  spec headers). `NFR-3820` is unchanged; Notes route the feature-index naming question to `05`.
- **Reason:** `BL-0320`.
- **Source review issue:** BL-0320.

### CHG-029
- **Files:** `02-non-functional-requirements.md`
- **Change:** Status note on `NFR-2820` (marker and backfill met; allow-list empty). No leaf added.
- **Reason:** `BL-0356` (F-07).
- **Source review issue:** F-07.

### CHG-030
- **Files:** `01-functional-requirements.md`, `03-requirements-traceability-matrix.md`
- **Change:** Added leaves for two shipped behaviors with an approved source: `FR-2330` (telemetry
  attack signatures as symptoms and the nominal comparison trace; `R121`, GDS-08 §7.3) and `FR-4460`
  (the reusable inject library; GDS-05 FR-W4, `ADR-0036`). Added candidates `CR-29`–`CR-33`
  (defender countermeasure modifiers; ops-fidelity levels; activity-feed lanes; scene orbital
  elements and subsolar point; SIGINT geolocation scaling) — shipped, but no approved input commits
  the system to them. Recorded, in the candidates section, the items decided to be implementation
  detail or already covered.
- **Reason:** `BL-0342`, `BL-0345`, `BL-0348`.
- **Source review issue:** BL-0342, BL-0345, BL-0348.

### Review findings, pass 1

| # | Finding type | IDs | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| P1-1 | Not built | `FR-4320` (extension), `FR-7450` | The extension and the ISO-8601 leaf are baselined ahead of the build. | Medium | `07` remediation package for the route guards (`BL-0324`, `BL-0351`); `06`/`07` for `FR-7450`. |
| P1-2 | Stale record | GDS-10 `FR-W3` row; GDS-07 §6; GDS-09 §4/OQ1 | Still carry "not met as built" wording. Outside `docs/requirements/`. | Low | `03-architecture-design-synthesis` (GDS-07, GDS-10); `10-integration-review` (GDS-09), per `BL-0329`, `BL-0356`. |
| P1-3 | Inconsistent evidence | `BL-0321`/`BL-0324`/`BL-0351` | The backlog rows read `DEFERRED`/`SCHEDULED`, not `DECIDED`; the scope extension was applied on the caller's instruction that the owner decided it. | Low | `00-pipeline-manager` to record the decision. |
| P1-4 | Requirement lacking tests | `FR-3410`, `FR-3510`, `FR-3520`, `FR-4710`, `FR-4720`, `FR-6110`, `FR-6220`, `FR-6410`, `FR-6610`, `FR-7110`, `NFR-1100`, `NFR-1200`, `NFR-1400`, `NFR-1510`, `NFR-2000`, `NFR-2100`, `NFR-2300`, `NFR-2400`, `NFR-2500`, `NFR-2600`, `NFR-2800`, `NFR-2900`, `NFR-3000`, `NFR-3040`, `NFR-3060`, `NFR-3200`, `NFR-3300`, `NFR-3500`, `NFR-3600`, `NFR-3810` | The origin report lists these baseline leaves as named by no test. Several are Inspection/Analysis leaves (`NFR-1510`, `NFR-3500`, `NFR-3600`, `NFR-3810`), expected to have none. No leaf was changed. | Low | `08` retag/new tests for the Test-method leaves; `11-release-readiness` relevance audit (`NFR-2830`) for the rest. |
| P1-5 | Missing requirement (candidate) | `CR-29`–`CR-33` | Shipped behavior with no approved source. | Low | Owner request via `00-intake`, or `03` to author the source statement, before baselining. |
| P1-6 | Ambiguity | `NFR-3820` | Names `INDEX.md`; `docs/features/feature-index.md` is unchecked. | Low | `05-feature-decomposition` (rename or widen), `BL-0320`. |
| P1-7 | Code lags requirement | `NFR-3810` | The integration test's docstring still says the check waits on `BL-0319`; no test names the leaf. | Low | `08` with `BL-0292`'s deletion sweep. |

---

## Baseline-maintenance pass 2 (2026-10-24) — `01`, `03`

Record of shipped or verified behaviour only, plus two rules the integration review of tranche 3
([`reviews/integration-review-tranche-3-release-push-remediation.md`](../reviews/integration-review-tranche-3-release-push-remediation.md))
found unowned (`M-2`, `L-4`, `L-7`). No new capability.

### CHG-031
- **Files:** `01-functional-requirements.md`, `03-requirements-traceability-matrix.md`
- **Change:** Added `FR-4330` (time control bounded to the exercise span: rewind in `[start_epoch,
  now]`, rewind-to-start is the start epoch, undo with nothing to undo refused, advance bounded to the
  same span). Rewind, undo and the save-side cap are met as built; the **advance bound is marked
  required, not yet built** (`IP-1076` will build it). New RTM row.
- **Reason:** `M-2`, `L-1`, `L-7`; `IP-1074`, `IP-1075`, `IP-1103`.

### CHG-032
- **Files:** `01-functional-requirements.md`
- **Change:** `FR-7230` Acceptance Criteria gain the `final_time` span check (start..start+366 days,
  refused before replay, bounds inclusive); Notes record it met as built (`IP-1103`). `FR-4310`
  Acceptance Criteria and Related Requirements point to `FR-4330`.
- **Reason:** `L-7`; `IP-1103`, `VR-1103`.

### CHG-033
- **Files:** `01-functional-requirements.md`, `03-requirements-traceability-matrix.md`
- **Change:** Added `FR-7340` (AAR playback controls obey the requesting seat: White any viewpoint, a
  player seat only its own, Observer reads but cannot change). **Required, not yet built.** `FR-7330`
  and `FR-4320` cross-reference it. New RTM row.
- **Reason:** `L-4`; `VR-1072` F3.

### CHG-034
- **Files:** `01-functional-requirements.md`
- **Change:** `FR-4320` Notes: "the extension is not yet built" rewritten as met as built (`IP-1072`,
  `VR-1072`; seat assignment and Observer designation since `IP-1074`), history kept.
- **Reason:** Stale after `IP-1072`.

### CHG-035
- **Files:** `03-requirements-traceability-matrix.md`
- **Change:** Impl. Package cells of `FR-4310`, `FR-4320`, `FR-7220`, `FR-7230`, `NFR-1600`,
  `NFR-3020`, `NFR-3030`: `IP-1072`, `IP-1073`, `IP-1074`, `IP-1075`, `IP-1102` changed from
  `COMPLETE` to `VERIFIED` with their VR. Two stale `COMPLETE ... awaiting 09` cells for `IP-1261`/
  `IP-1262` (`FR-2320`-family and ephemeris rows) were not touched; they are outside this tranche.
- **Reason:** Integration review tranche 3 (stale status text); ledger says `VERIFIED`.

### CHG-036
- **Files:** `03-requirements-traceability-matrix.md`
- **Change:** Test column regenerated with `python3 -m pytest --origin-report=rtm` (not hand edited).
- **Reason:** `NFR-2850`.

### Review findings, pass 2

| # | Finding type | IDs | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| P2-1 | Not built | `FR-4330` (advance bound), `FR-7340` | Both rules are baselined ahead of the build. | Medium | `07` package `IP-1076` (advance bound, backwards step/advance 400); a `07` package for playback seat checks. |
| P2-2 | Test tagging | `FR-4330`, `FR-7340` | Existing rewind/undo/save-span tests name `FR-4310`/`FR-7230`/`NFR-1600`, not `FR-4330`. | Low | `08` retag with `IP-1076`. |
| P2-3 | Stale record | `IP-1261`, `IP-1262` RTM cells | Still say `COMPLETE ... awaiting 09`. | Low | `00-pipeline-manager`: confirm ledger status, then `04` next pass. |
| P2-4 | Owner question | rewind vs running clock (`L-6`); 366-day cap configurable? | Not decided; left out of the leaves. | Low | Project owner. |

---

## Baseline-maintenance pass 3 (2026-10-24) — `01`, `02`, `03`

Release-preparation pass on the owner's decisions of 2026-10-24 and the `BL-0342`/`BL-0345`/`BL-0348`/
`BL-0369` coverage gaps. Behaviour already shipped and verified, plus one policy restatement. No new
capability.

### CHG-037
- **Files:** `02-non-functional-requirements.md`
- **Change:** `NFR-1510` Description, Rationale, Metric and Notes restated as the owner's procedure: at each
  release readiness check the latest dependency versions, try updating to them, validate with the full
  suite in both modes, fix or hold back what breaks, then lock exact versions in the committed
  `requirements.lock` at the repository root; minimum versions only during development; "major" stays dropped.
- **Reason:** Owner decision, 2026-10-24: "Pin each release but check if the most up to date versions break
  anything and attempt to update to them before re-pinning."

### CHG-038
- **Files:** `01-functional-requirements.md`
- **Change:** `FR-4330` Notes: advance bound, backwards/non-finite refusal and running-clock stop recorded as
  met as built (`IP-1076`, `VR-1076`); rewind and undo as met (`IP-1074`, `IP-1075`); the pass-2 "required,
  not yet built" text marked superseded. New statement that whether a rewind pauses a running clock is
  unspecified, either is conformant, current behavior keeps it running, and it is not release-blocking.
- **Reason:** `IP-1076` `VERIFIED`; owner: the clock "can pause on rewind but doesn't matter" (closes `L-6`).

### CHG-039
- **Files:** `01-functional-requirements.md`
- **Change:** `FR-7340` Notes recorded as met as built (`IP-1077`, `VR-1077`); `FR-4320` Notes cross-reference
  made current.
- **Reason:** `IP-1077` `VERIFIED`.

### CHG-040
- **Files:** `01-functional-requirements.md`
- **Change:** `FR-7230` Acceptance Criteria extended with the 100,000-entry event-log cap (both log shapes,
  refused before parsing or replay, exactly the cap passes) and the unusable-save refusals; Notes record them
  as met as built (`IP-1081`, `IP-1102`, `IP-1103`).
- **Reason:** `IP-1081` `VERIFIED`; `NFR-3710` states the cap, the leaf did not.

### CHG-041
- **Files:** `01-functional-requirements.md`, `03-requirements-traceability-matrix.md`
- **Change:** Added `FR-1140` (simulated time as integer microseconds; ISO-8601 only at the boundary).
- **Reason:** `BL-0369`; approved source GDS-07 §1, GDS-09 §3.

### CHG-042
- **Files:** `01-functional-requirements.md`, `03-requirements-traceability-matrix.md`
- **Change:** Added `FR-7350` (after-action report export as CSV and JSON).
- **Reason:** `BL-0369`; approved sources GDS-07 §7, GDS-09 §3, `ADR-0033`/`ADR-0029`.

### CHG-043
- **Files:** `01-functional-requirements.md`, `03-requirements-traceability-matrix.md`
- **Change:** Added candidates `CR-34` (telemetry series history shape, pass-gating of historical points;
  open design question `BL-0171`) and `CR-35` (space-weather severity names and coercion). Recorded the
  disposition of all twelve `BL-0369` gap areas in the candidates section.
- **Reason:** `BL-0369`; no approved source commits the system to either behavior.

### CHG-044
- **Files:** `03-requirements-traceability-matrix.md`
- **Change:** Impl. Package and Future Feature cells of `FR-4330` (`IP-1076` `VERIFIED`, `FS-106` v2.4) and
  `FR-7340` (`IP-1077` `VERIFIED`, `FS-107`); the `FR-4310`/`FR-4320` notes made current. Stale "`COMPLETE`,
  awaiting `09`" cells for `IP-1081`, `IP-1261`, `IP-1262`, `IP-1210`, `IP-1171`, `IP-1063` set to `VERIFIED`
  per the Master Build Plan (closes `P2-3`).
- **Reason:** Ledger agreement (`NFR-3830`).

### CHG-045
- **Files:** `03-requirements-traceability-matrix.md`
- **Change:** Test column regenerated with `python3 -m pytest --origin-report=rtm` (not hand edited).
- **Reason:** `NFR-2850`.

### Review findings, pass 3

| # | Finding type | IDs | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| P3-1 | Stale text outside scope | `docs/features/FS-133-test-origin-traceability.md` (status line; `BL-0299` "locked at major releases") | Still says the lock is made "at the first major release". `NFR-1510` no longer says "major". | Low | `06` (feature specification FS-133). |
| P3-2 | Requirement lacking tests | `FR-1140`, `FR-7350` | New leaves; existing tests of these behaviors carry other tags. | Low | `08` retag (`test_clock_and_time.py`, `test_web.py` AAR export tests). |
| P3-3 | Not built | `FR-7450` | Still baselined ahead of the build. | Medium | `06`/`07` package (unchanged from pass 1, `P1-1`). |
| P3-4 | Open design question | `CR-34` / `BL-0171` | Pass-gating of historical telemetry points; `FR-2320` calls the export pass-gated but it is not. | Low | Project owner, then `03`/`04`. |
| P3-5 | Owner decision recorded | `FR-4330` | Rewind versus a running clock: unspecified, not release-blocking. | Info | None. |
| P3-6 | Open | `FR-4330` | Whether the 366-day span is configurable. | Low | Project owner. |

---

## Findings deliberately left unactioned (with reason)

These review findings were re-examined against the current document text and intentionally not
applied as edits, to avoid manufacturing changes the findings themselves do not actually require:

- **REQ-001, REQ-002, REQ-030** (skill Step-3/4 deliverable / GDS-10 traceability matrix gap) — this
  is a whole-baseline structural gap requiring a new `04-requirements-traceability-matrix.md` or
  GDS-10 authoring, not an edit to any of the three files in scope for this task.
- **REQ-011** (Observability category empty) — already correctly tracked via CNFR-01; no action
  proposed by the review itself beyond what CNFR-01 already states.
- **REQ-012** (push-vs-poll NFR gap) — the review's own recommended resolution is optional/Low and
  was not requested as part of this edit pass; left for a future pass.
- **REQ-013, REQ-020, REQ-022, REQ-032, REQ-040, REQ-041, REQ-050, REQ-061, REQ-070, REQ-090,
  REQ-091, REQ-100** — each is a confirmed non-finding, an already-correctly-excluded item, or
  (REQ-020) a finding whose recommended fix targets `CLAUDE.md`, which is outside the three files
  this task authorizes editing.

## Related

[`docs/reviews/requirements-review.md`](../reviews/requirements-review.md) ·
[`docs/requirements/01-functional-requirements.md`](01-functional-requirements.md) ·
[`docs/requirements/02-non-functional-requirements.md`](02-non-functional-requirements.md) ·
[`docs/design/05-interface-control-document.md`](../design/05-interface-control-document.md)
