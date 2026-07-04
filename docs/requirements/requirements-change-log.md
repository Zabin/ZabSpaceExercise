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
