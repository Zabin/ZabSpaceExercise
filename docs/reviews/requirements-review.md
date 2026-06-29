# Requirements Review — Functional & Non-Functional Requirements, ICD, Architecture, ADRs

A principal-systems-engineer review of the project's requirements baseline against its
architecture, interface, and decision-record corpus.

**Status:** Review report — informational, non-binding. **Does not modify any reviewed
document.** No requirement, NFR, ICD interface, ADR, or architecture document was edited in the
production of this report.

**Scope reviewed:**
[`docs/requirements/01-functional-requirements.md`](../requirements/01-functional-requirements.md)
(FR-1000–FR-9110, CR-01–CR-11), [`docs/requirements/02-non-functional-requirements.md`](../requirements/02-non-functional-requirements.md)
(NFR-1100–NFR-3300, CNFR-01–CNFR-05), [`docs/design/05-interface-control-document.md`](../design/05-interface-control-document.md)
(INT-0001–INT-0016), the GDS architecture ladder
([`architecture/INDEX.md`](../architecture/INDEX.md), GDS-00 through GDS-05; GDS-06–GDS-10
confirmed scaffold-only), all 29 ADRs ([`architecture/adr/INDEX.md`](../architecture/adr/INDEX.md)),
and the `requirements-engineering` skill definition
(`.claude/skills/requirements-engineering/SKILL.md`) whose Step 1–2 outputs the FR/NFR documents
under review are.

**Method:** Cross-reading the requirements baseline against its own stated traceability fields,
against the GDS-05 capability statements it claims to elaborate, against the ICD interfaces it
cites, and against the 29 ADRs it must remain consistent with. This review treats
[`docs/reviews/architecture-review.md`](architecture-review.md) (GDS-01–GDS-04 only) as a sibling
document, not a subject to re-review: findings already on record there are **cross-referenced**,
not restated as new, unless this review found something that document's narrower scope (GDS-01–04
only, predates the requirements baseline and most of GDS-05/ICD) could not have surfaced. The
**requirements-engineering skill's own quality gate** (SKILL.md "Quality gate" checklist) is used
as an explicit audit checklist in §0 below, since the skill's documented deliverable set differs
from what exists on disk — itself the first finding.

**Severity scale:** **Critical** (blocks correct operation or creates an unresolvable
contradiction) · **High** (a real gap or conflict likely to cause rework if not addressed before
implementation extends the affected area) · **Medium** (a clarity/completeness gap with a
plausible workaround already in place) · **Low** (cosmetic, stylistic, or already self-flagged and
tracked elsewhere).

---

## 0. Skill-conformance check (new dimension, not in the task's ten but load-bearing for the rest)

The `requirements-engineering` skill's own spec (SKILL.md "Outputs") names exactly four
deliverables, in order, all under `docs/requirements/`: `01-functional-requirements.md`,
`02-non-functional-requirements.md`, `03-requirements-review.md`,
`04-requirements-traceability-matrix.md`. On disk, only the first two exist; `03` and `04` were
never produced. This review is being written to `docs/reviews/requirements-review.md` per this
task's explicit instruction — a third path, distinct from both the skill's prescribed
`docs/requirements/03-...` and this repository's existing `docs/reviews/architecture-review.md`
convention. This is noted for traceability, not treated as an error to fix (the task's explicit
path instruction controls); see **REQ-001** below.

| Issue ID | Severity | Description | Affected requirement(s) | Recommended resolution |
|---|---|---|---|---|
| **REQ-001** | Medium | The `requirements-engineering` skill's own contract names `docs/requirements/03-requirements-review.md` and `docs/requirements/04-requirements-traceability-matrix.md` as mandatory Step 3/4 deliverables. Neither exists. This document (at `docs/reviews/requirements-review.md`, per explicit task instruction) substantively fulfills Step 3's role but at a different path and name, and **Step 4 (the Requirements Traceability Matrix) has no equivalent anywhere** — GDS-10 is also scaffold-only (see REQ-002), so there is no traceability matrix in the entire repository in any location. | Whole FR/NFR baseline (no row-level forward traceability to Subsystem/Feature Spec/Implementation/Test exists anywhere) | Either (a) add `docs/requirements/04-requirements-traceability-matrix.md` per the skill's Step 4 template (one row per FR/NFR/candidate, `UNASSIGNED` where forward artifacts don't exist yet — explicitly the skill's own recommended honest state), or (b) treat GDS-10's eventual authoring as the matrix and record that decision in `architecture/INDEX.md`/`requirements/`'s cross-references so the skill's Step 4 isn't silently dropped. Either is acceptable; leaving it unaddressed is not, since "traceable requirements baseline" is the skill's stated purpose. |
| **REQ-002** | High | GDS-10 (Requirements Traceability Matrix) is confirmed scaffold-only (`architecture/10-requirements-traceability-matrix.md` — two unchecked merge-gate boxes, no content). This is the terminal deliverable of the entire GDS ladder and the only place a formal requirement→architecture→ADR→interface→test matrix could live authoritatively. Its absence means every traceability claim in this corpus (FR "Related ADRs"/"Related Interfaces" fields, the ICD's "Related architecture components," ADR "Related" sections) is an **informal, scattered cross-reference**, not a verifiable matrix — there is no single artifact that can be queried to answer "is every FR covered by a test" or "is every ADR consumed by at least one FR." | Whole baseline; GDS-10 itself | Author GDS-10 (or the skill's Step 4 matrix per REQ-001) before the baseline is treated as implementation-ready. This is already CNFR/GDS-level tracked (architecture/INDEX.md marks GDS-10 ⛔ Planned) — this finding corroborates that the gap is also a *requirements*-traceability blocker, not only an architecture-ladder completeness gap. |

---

## 1. Completeness

| Issue ID | Severity | Description | Affected requirement(s) | Recommended resolution |
|---|---|---|---|---|
| **REQ-010** | Medium | GDS-05's own Open Question 1 (OQ1) records that OR-3 ("blank screen / hand off" hot-seat menu) has **no corresponding `FR-1xxx`/`FR-6xxx` leaf** in `requirements/01`. This review independently confirms: no FR in `requirements/01`'s FR-6xxx (session/multiplayer) cluster covers the screen-blank affordance. It is mentioned only as prose inside `CLAUDE.md`'s "LAN trust model" section and OR-3's own text. | GDS-05 OR-3; `requirements/01` FR-6xxx cluster (gap) | Add an `FR-6xxx` leaf for the screen-blank/hand-off menu (precondition: active session, hot-seat role change pending; postcondition: sensitive content hidden until White Cell re-selects a seat), closing GDS-05 OQ1 at the same time. |
| **REQ-011** | Low | `requirements/02`'s Observability category is entirely empty (the NFR doc's own "Completion report" already self-flags this as CNFR-01, and explicitly states 14 of 15 standard categories are populated). Confirmed correct as self-reported — no NFR-3xxx leaf addresses observability (structured logging format, log levels, correlation IDs) distinct from the Logging category's NFR-3100/3200 (which cover *what* is logged, not operational observability tooling). | `requirements/02` (Observability category, entirely absent); CNFR-01 | Already tracked as CNFR-01 in the source document; no new action needed beyond what CNFR-01 already proposes (escalate to architecture owner once a concrete observability need is identified — e.g. log aggregation across multi-tab LAN sessions). |
| **REQ-012** | Medium | The ICD's own §7 lists 11 self-identified issues, several of which describe requirements-relevant gaps that have **no corresponding FR/NFR acknowledging them** even informally: specifically ICD §7 issue 11 (push-based WebSocket as a possibly-missing interface) has no NFR addressing push-vs-poll latency/staleness trade-offs anywhere in `requirements/02`'s Performance or Usability categories — the polling model is assumed throughout `requirements/01`'s FR-6xxx cluster without a requirement stating *why* polling (not push) is the chosen interaction model. | ICD §7 issue 11; `requirements/02` Performance/Usability categories (no leaf addresses push vs. poll) | Add an NFR (or a Note on an existing FR-6xxx leaf) stating polling is the accepted v1 model and citing the rationale (simplicity, LAN trust model, no infra for WebSocket fan-out), so a future reviewer doesn't mistake the silence for an oversight. |
| **REQ-013** | Low | `requirements/01`'s Candidate Requirements (CR-01–CR-11) and `requirements/02`'s Candidate NFRs (CNFR-01–05) are both self-disclosed gaps already explicitly excluded from the baseline by design (per the skill's own Step 1 "Candidate Requirements" rule). This review confirms all 16 trace correctly to a genuine missing-source-document condition (no CR/CNFR was found to actually have a traceable source that was wrongly excluded). No action beyond what each CR/CNFR's own Notes field already proposes. | CR-01–CR-11, CNFR-01–05 | None — correctly handled per the skill's own discipline. Listed here only so this review's Completeness section doesn't silently omit them. |

---

## 2. Consistency

| Issue ID | Severity | Description | Affected requirement(s) | Recommended resolution |
|---|---|---|---|---|
| **REQ-020** | High | **Authority-model tension between the requirements-engineering skill's stated relationship and `CLAUDE.md`'s blanket-supersession declaration.** The skill's own SKILL.md (last "Gotchas" bullet) instructs: if a project already has FR/NFR sections baked into its own architecture ladder, treat them as part of the skill's authoritative *input*, not produce "a second, competing FR/NFR set." GDS-05 (§"Relationship to other requirement artifacts") resolves this correctly *between GDS-05 and `requirements/01`* — explicitly stating they are non-competing, different-grain views of the same baseline, with disagreement-on-substance treated as a defect. However, `CLAUDE.md`'s "Authoritative source & reading order" section separately declares the *entire* GDS ladder "supersedes `docs/build-spec/` in its entirety... immediately, including for GDS levels that have not yet been authored." Read literally, this could be misconstrued as superseding `requirements/01`/`02` as well (since they are not part of the GDS ladder), even though GDS-05's own text explicitly disclaims any such relationship. The two statements are not in actual conflict once GDS-05 §"Relationship..." is read, but `CLAUDE.md`'s phrasing is broad enough to create the appearance of one for a reader who reads `CLAUDE.md` first (the documented reading order) and reaches GDS-05's disclaimer only several documents later. | `CLAUDE.md` "Authoritative source & reading order"; GDS-05 "Relationship to other requirement artifacts"; `requirements/01`/`02` (implicitly) | Add one clarifying sentence to `CLAUDE.md`'s supersession paragraph: "`docs/requirements/` is a sibling elaboration of GDS-05/06, not part of the superseded `docs/build-spec/` set — see GDS-05 §'Relationship to other requirement artifacts.'" This is a documentation-only fix to `CLAUDE.md`, outside this review's "do not modify requirements" scope (CLAUDE.md is project guidance, not a requirements artifact) — flagged for the project owner, not actioned here. |
| **REQ-021** | Medium | GDS-05's Open Question 2 (OQ2) flags that OR-6 ("v1 runs a single exercise per process instance") textually conflicts with the shipped `/api/sessions` multi-session discovery endpoint (P8). `requirements/01`'s own FR-6410 is cited by GDS-05 as the leaf "in scope" for OR-6, but this review confirms `requirements/01`'s NFR-side counterpart — `requirements/02`'s "Completion report" Open issue 1 — **independently flags the identical tension** without cross-referencing GDS-05 OQ2 by ID, and without either document referencing the other's restatement of the same open conflict. Two separate "open issue" trails exist for one unresolved fact. | GDS-05 OQ2; `requirements/02` Completion-report Open issue 1; FR-6410 | Merge the two open-issue trails: have `requirements/02`'s Open issue 1 cite "GDS-05 OQ2" explicitly (or vice versa) so a future resolver finds one record, not two independently-discovered duplicates of the same unresolved question. |
| **REQ-022** | Low (confirmed non-finding) | The architecture-review.md §3 finding 2 (six-access-channels vs. cyber-exception inconsistency) was checked against `requirements/01` FR-1220 (access windows) and FR-1420 (five-D's + cyber exception): both are written as properly separate, non-conflicting requirements, each correctly scoping cyber out of FR-1220's window-gating language. This upstream architecture-level finding does **not** recur as a defect at the requirements-leaf level. Recorded here so this review doesn't silently propagate an inapplicable upstream finding. | FR-1220, FR-1420 (confirmed consistent) | None — no action needed. |
| **REQ-023** | Medium | FR-9110 (AI-Red) carries **Priority: Should** — the only "Should"-priority leaf found in an otherwise heavily "Must"-weighted FR-9xxx/adjacent clusters review of `requirements/01`. This is not necessarily wrong (AI-Red is explicitly a v1-scoped-down, scripted-only feature per ADR-0021/ADR-0024, and "Should" may be the deliberately correct priority for it), but no other leaf in the document explains *why* AI-Red alone sits at a different priority tier than its sibling capabilities — the Rationale field cites ADR-0021/ADR-0024 for AI-Red's *scope*, not for its *priority level*. | FR-9110 | Add one sentence to FR-9110's Rationale explicitly justifying the "Should" tier (e.g. "scripted White-Cell-driven behavior is valuable but not required for a vignette to be playable, unlike Must-tier FR-E/FR-P leaves") so the priority isn't mistaken for an oversight by a future reader doing exactly this kind of cross-leaf priority scan. |

---

## 3. Traceability

| Issue ID | Severity | Description | Affected requirement(s) | Recommended resolution |
|---|---|---|---|---|
| **REQ-030** | High | (Restates REQ-002 from the dedicated angle of this section's required dimension.) With GDS-10 scaffold-only and no Step-4 matrix produced, **no FR or NFR in the baseline has a forward trace to a test artifact**, despite `requirements/01`/`02` both populating a "Verification Method" field (Test/Demonstration/Analysis/Inspection) on every leaf. The Verification Method field states *how* a requirement would be verified in principle; it does not point at an actual `spacesim/tests/...` file, so the field's claim is currently unauditable against the 469-test suite `CLAUDE.md` reports as green. | Whole baseline (forward trace to test, absent) | Populate GDS-10 or the skill's Step-4 matrix with at minimum the `Test` column for FR/NFR leaves whose Verification Method is "Test" (the majority) — many of these almost certainly already have a corresponding `spacesim/tests/test_*.py` file given the project's test-first workflow (`CLAUDE.md` "Test-driven workflow"); this would be a mechanical, low-risk first pass at GDS-10/the matrix rather than a from-scratch undertaking. |
| **REQ-031** | Medium | ICD interfaces are cited by `requirements/01` leaves inconsistently in granularity: some FRs cite a specific interface (e.g. FR-9110 → "ICD INT-0015"), while others in the same FR-9xxx-adjacent neighborhood (e.g. session/multiplayer FR-6xxx leaves that clearly depend on INT-0001 command/control or INT-0014-equivalent session interfaces per the ICD's own interface list) cite no "Related Interfaces" entry at all, even though a Session/CellController-mediated interface plainly exists for them per the ICD. This isn't a missing capability — it's an inconsistent application of the "Related Interfaces" field across otherwise-similar leaves. | `requirements/01` FR-6xxx cluster (uneven "Related Interfaces" population vs. FR-9110/FR-3xxx) | Pass over the FR-6xxx (session/multiplayer/fog-of-war) cluster specifically and backfill "Related Interfaces" citations to the matching INT-00xx ICD entries, matching the citation density already present in the FR-9xxx and FR-3xxx clusters. |
| **REQ-032** | Low | ADR-0024–0029's "Consequences" sections name several follow-up document edits (e.g. ADR-0024 → AI-Red boundary clarifications in GDS-02/03/04; ADR-0027 → scenario-authoring boundary edits; ADR-0028 → build-spec/03 §7.1/7.2 rewrite). This review spot-checked ADR-0024's and ADR-0027's consequences against GDS-02/GDS-04's "Review reconciliation" sections (both confirmed present and substantively matching what the ADRs promised) and ADR-0029's consequence against `requirements/01` FR-4710 (confirmed: FR-4710 cites ADR-0029 correctly). No broken follow-up-edit promise was found in the sample checked. Full verification of all six ADR-0024–0029 follow-ups against every cited target document was not exhaustively performed (time-boxed sampling only). | ADR-0024, ADR-0027, ADR-0029 (sampled, confirmed); ADR-0025, ADR-0026, ADR-0028 (not independently re-verified in this pass) | Optional: a future pass could exhaustively re-verify all six ADR "Consequences" follow-up commitments against their target documents; not urgent given the sampled results were clean and `architecture-review-changelog.md` already exists as a consolidated record of completed follow-ups. |

---

## 4. Testability

| Issue ID | Severity | Description | Affected requirement(s) | Recommended resolution |
|---|---|---|---|---|
| **REQ-040** | Medium (already self-flagged, corroborated here) | `requirements/02`'s own Completion-report Open issue 3 states no source document anywhere supplies a numeric performance target for NFR-1100/1200 (the Performance category). This review confirms: NFR-1100/1200's Acceptance Criteria are written qualitatively ("the UI shall remain responsive," paraphrased) rather than with a checkable threshold (e.g. "p95 command-menu render < 200ms"), which is **exactly the correct behavior per the skill's own Step 2 rule** ("If the inputs don't specify a number, write the requirement qualitatively... do not manufacture a number"). The requirement is therefore not a defect of the FR/NFR authoring — it is a defect of the *source* architecture corpus, which never committed to a number. Recorded here as confirmation, with the Testability angle made explicit: a qualitative Acceptance Criterion is materially harder to verify pass/fail on than a numeric one, which is the practical cost of this still-open gap. | NFR-1100, NFR-1200 | Already tracked (Completion-report Open issue 3); the actionable next step is for the architecture owner to supply a numeric target (even a soft one, e.g. from informal playtesting at the ~24-satellite sizing guideline) so a future revision of NFR-1100/1200 can tighten its Acceptance Criteria from qualitative to numeric. |
| **REQ-041** | Low | A handful of FR leaves in the FR-W (White Cell control) cluster use Verification Method "Demonstration" rather than "Test" (e.g. leaves describing UI affordances like the classification banner or god-view toggle). Per the skill's own writing rule, Analysis/Inspection/Demonstration choices should be "justified... if used instead of Test." Spot-checking FR-4510 (classification banner) and FR-4610 (god-view) found both correctly justify Demonstration (UI-rendering checks that the existing pytest suite doesn't cover, consistent with `CLAUDE.md`'s disclosure that "the browser GUI is unverified headless"). No unjustified Demonstration/Analysis/Inspection choice was found in the sample reviewed. | FR-4510, FR-4610 (confirmed correctly justified); full FR-4xxx cluster not exhaustively sampled | None required for the sampled leaves; if a future pass exhaustively reviews FR-4xxx, confirm the same Demonstration-justification pattern holds throughout. |

---

## 5. Ambiguity

| Issue ID | Severity | Description | Affected requirement(s) | Recommended resolution |
|---|---|---|---|---|
| **REQ-050** | Low | OR-7 (unseated-role behavior, GDS-05 §7) uses the phrase "no new decisions are made on their behalf" — clear in context but not itself an Acceptance-Criteria-grade statement; the corresponding `requirements/01` leaf (FR-3110's plan-first guarantee, per GDS-05's own cross-reference) does carry checkable Acceptance Criteria, so the ambiguity exists only at the GDS-05 capability-statement grain, which by GDS-05's own stated design ("restated... at the same grain as the original tags") is not meant to carry Acceptance-Criteria-level precision — that's `requirements/01`'s job, and it does the job correctly here. Confirmed non-issue once both grains are read together; recorded only because reading GDS-05 in isolation could look ambiguous. | GDS-05 OR-7 (capability grain, by design); FR-3110 (leaf grain, confirmed precise) | None — working as designed; no action. |
| **REQ-051** | Medium | `requirements/01` FR-W7 / FR-4710's text ("White Cell shall be able to set the safe-mode dials and other live parameters mid-exercise") leaves "other live parameters" undefined at the leaf level — it is a catch-all phrase rather than an enumerated list, which is borderline against the skill's own "unambiguous" writing rule (no "as appropriate"-style vagueness). The GDS-05 source text (FR-W7) itself uses the identical catch-all phrasing, so this is inherited ambiguity from the capability-grain statement, not something `requirements/01` introduced independently — but `requirements/01`'s leaf, unlike GDS-05's capability statement, is supposed to be the precision layer, and it did not tighten this particular phrase. | GDS-05 FR-W7; `requirements/01` FR-4710 | Either enumerate the "other live parameters" set explicitly in `requirements/01` FR-4710 (cross-checking against what the White-Cell control panel actually exposes per `spacesim/ui_web/static/app.js`), or add a Notes field stating the set is intentionally open-ended/extensible and is not meant to be enumerated. Either resolves the ambiguity; leaving it silent does not. |

---

## 6. Duplication

| Issue ID | Severity | Description | Affected requirement(s) | Recommended resolution |
|---|---|---|---|---|
| **REQ-060** | Medium | The GDS-05 OQ2 / `requirements/02` Open-issue-1 duplication already covered under Consistency (REQ-021) is also, structurally, a **duplication** finding: two independent "open issue" records for the identical unresolved fact (OR-6 vs. `/api/sessions`), neither referencing the other. Cross-listed here per this section's required dimension rather than re-described; see REQ-021 for the full description and recommended resolution. | GDS-05 OQ2; `requirements/02` Completion-report Open issue 1 | See REQ-021. |
| **REQ-061** | Low | No genuine FR-to-FR or NFR-to-NFR content duplication (two IDs describing the same behavior) was found anywhere in `requirements/01`/`02`. The hierarchical leaf numbering scheme (gaps left for insertion, atomic-behavior-per-leaf discipline) appears to have been followed correctly throughout — each leaf reviewed describes one distinct, non-overlapping behavior. This is a confirmed clean result, not a gap. | `requirements/01`, `requirements/02` (whole baseline) | None — no duplication found; recorded for completeness of this section's required coverage. |

---

## 7. Architectural alignment

| Issue ID | Severity | Description | Affected requirement(s) | Recommended resolution |
|---|---|---|---|---|
| **REQ-070** | Low (confirmed non-finding) | The architecture-review.md's headline finding (assessment/scoring has no owning subsystem/domain object, GDS-01–04 §1/§7) is now **closed at the requirements level**: ADR-0029 (dated after architecture-review.md) resolves it by deciding raw AAR/event-log access is sufficient, and `requirements/01` FR-4710 correctly cites ADR-0029 in its Related ADRs field. This review confirms the requirements baseline correctly reflects the *current*, resolved state of this question, even though the sibling architecture review (written before ADR-0029) still describes it as the architecture's most load-bearing open item. No action needed at the requirements level; flagged only so a reader cross-referencing both review documents understands why they appear to disagree (one predates the resolution, one postdates it). | FR-4710; ADR-0029; architecture-review.md §1 finding 1 / §7 findings 1–2 (superseded by ADR-0029, not contradicted by it) | None at the requirements level. Optional: architecture-review.md could gain a one-line "superseded by ADR-0029" annotation next to its own finding, but that document is out of this review's scope to edit. |
| **REQ-071** | Medium | AI-Red's epistemic-parity fairness question — independently flagged by architecture-review.md §8 finding 3 ("does AI-Red play by the same fog-of-war rules as human Red?") and resolved at the architecture level by ADR-0024 ("AI-Red stays permanently internal; epistemic parity is a tracked future-work gap") — is correctly reflected in `requirements/01` FR-9110's Notes field ("the gap... Source: ADR-0024; FUTURE-WORK.md §1"). This is a confirmed-aligned case, not a gap. However, `requirements/02` (NFR baseline) has **no NFR addressing fairness/equity as a quality attribute** even qualitatively, despite this being exactly the kind of cross-cutting non-functional concern (akin to Security or Usability) the architecture corpus itself treats as load-bearing enough to warrant an ADR. The NFR document's 15-category list (per the skill's fixed category set) has no "Fairness" or equivalent category at all — this is a structural gap in the skill's own category taxonomy, not an authoring miss within it. | `requirements/02` (no Fairness-equivalent NFR category); FR-9110 (correctly handles this at the FR level already) | Either add a qualitative NFR under an existing category (e.g. Usability or a new ad-hoc category) stating "AI-Red's epistemic asymmetry relative to human Red is an accepted, documented v1 trade-off, not a defect" — making the FR-9110 Notes-level disclosure also visible at the NFR/quality-attribute level — or explicitly note in `requirements/02`'s Candidate NFRs that fairness/epistemic-parity was considered and intentionally left uncategorized pending FUTURE-WORK.md resolution. |
| **REQ-072** | High | **`requirements/01`'s OR-2 scope-only treatment of "bus/payload seats."** GDS-05 OR-2 states a Role Assignment "may be bus operator, payload operator, or both for a given asset/constellation" and is marked "(→ FR-3510 scope)" — meaning OR-2 has no dedicated FR-1xxx leaf of its own, it is folded entirely into FR-3510's scope statement. Checking FR-3510 in `requirements/01` (the order panel offering only legal commands for the seated role/asset) confirms FR-3510 covers the *command-menu filtering* consequence of a bus/payload split, but **does not itself state the Role Assignment's own bus/payload/both cardinality rule** — that rule lives only in GDS-05's prose and in GDS-04 §1.10's domain-model description, with no `requirements/01` leaf asserting it as a system behavior in its own right (e.g. "the system shall allow a Role Assignment to scope to bus-only, payload-only, or both for a given asset"). This is a genuine, non-trivial missing requirement: FR-3510 describes a *consequence* of the rule, not the rule itself, so there is no leaf a tester could check to verify the cardinality rule is actually enforced (as opposed to its UI-filtering side effect). | GDS-05 OR-2; `requirements/01` FR-3510 (covers consequence, not the rule); GDS-04 §1.10 Role Assignment | Add a dedicated `FR-3xxx` leaf (e.g. FR-3520) stating the Role Assignment bus/payload/both cardinality rule directly, with its own Acceptance Criteria (e.g. "given a Role Assignment scoped to bus-only for Asset X, attempting to issue a payload-verb command for Asset X is rejected") distinct from FR-3510's UI-filtering behavior. |

---

## 8. Missing requirements

| Issue ID | Severity | Description | Affected requirement(s) | Recommended resolution |
|---|---|---|---|---|
| **REQ-080** | High | (Cross-listed from REQ-072 under this section's required dimension — see REQ-072 for full description.) The Role Assignment bus/payload/both cardinality rule has no dedicated FR leaf. | GDS-05 OR-2; FR-3510 | See REQ-072. |
| **REQ-081** | High | (Cross-listed from REQ-010 — see REQ-010 for full description.) OR-3's hot-seat screen-blank menu has no FR leaf at all, self-flagged as GDS-05 OQ1 and independently confirmed by this review. | GDS-05 OR-3 / OQ1 | See REQ-010. |
| **REQ-082** | Medium | The ICD's §7 issue 4 (save-file ownership ambiguity between Content & Data and Session) is recorded by the ICD as resolved-in-principle via ADR-0022, and `requirements/01`'s FR-7xxx (logging/AAR) cluster correctly assumes the resolved split when describing log/save behavior. However, no `requirements/01` leaf **directly states the save-file ownership split itself** as a system requirement (e.g. "the Vignette/content portion of a save file shall be distinguishable from and independently re-importable apart from the Session/event-log portion") — it is assumed as settled background rather than asserted as a checkable behavior anywhere in the FR baseline, even though ADR-0022 clearly intends it to be an enforced invariant, not merely a documentation clarification. | ADR-0022; ICD §7 issue 4; `requirements/01` FR-7xxx cluster (no leaf asserts the split as enforced behavior) | Add an FR leaf (likely FR-7xxx or a new FR-5xxx scenario-builder leaf, given the content/session boundary) stating the save-file ownership split as a testable system behavior, citing ADR-0022 directly. |

---

## 9. Over-constrained requirements

| Issue ID | Severity | Description | Affected requirement(s) | Recommended resolution |
|---|---|---|---|---|
| **REQ-090** | Low | No leaf in `requirements/01`/`02` was found to over-specify implementation (no class names, table schemas, or algorithm-level detail leaked into a Description/Acceptance-Criteria field — the skill's own "implementation independent" writing rule appears consistently honored across every leaf sampled). | None found | None — confirmed clean. |
| **REQ-091** | Medium | FR-P6 (delta-v cost preview, GDS-05) and its `requirements/01` leaf state a "configurable years-of-life threshold" requiring "a deliberate confirm" above it. The requirement is correctly behavior-level (not implementation-level), but it constrains the *existence* of a specific confirm-dialog interaction pattern at the requirements layer rather than stating the underlying need ("prevent an operator from spending a large fraction of remaining service life without being warned") and leaving the interaction mechanism to design. This borders on over-constraining a requirement with a UI-interaction-pattern detail ("a deliberate confirm") that is arguably a design choice, not a requirement. Low-to-medium severity because the existing `design/14-delta-v-economy.md` cross-reference suggests this was a deliberate, already-designed choice rather than an accidental over-specification. | FR-P6; `requirements/01` FR-1310/FR-3xxx delta-v leaves | Optional: if a future revision wants to tighten the implementation-independence discipline, restate the requirement as "the system shall require explicit operator acknowledgement before executing a maneuver whose cost exceeds the configured threshold" and let `design/14-delta-v-economy.md` own the specific confirm-dialog mechanism. Not urgent — current wording is functional and traceable as-is. |

---

## 10. Under-defined interfaces

| Issue ID | Severity | Description | Affected requirement(s) | Recommended resolution |
|---|---|---|---|---|
| **REQ-100** | High (corroborates ICD's own self-flagged issues) | The ICD's own §7 already lists 11 self-identified under-definition issues (no wire-level contract; INT-0001 auth gap; bidirectional-arrow ambiguity since resolved; save-file ownership ambiguity per ADR-0022; AccessWindow persisted-vs-derived per GDS-04 OQ2; SSN-Request-vs-Planned-Activity supertype per GDS-04 OQ3; Snapshot version-compatibility gap; Space-Track credential-handling gap; AI-Red ground-truth-read deviation per ADR-0024/INT-0015; partial-vignette-authoring-state ownership; possible missing push-based interface). This review confirms all 11 are still open as of this baseline (none have been silently closed without updating the ICD's own §7), and confirms each maps cleanly to a `requirements/01` Candidate Requirement or an explicit FR Notes-field disclosure — i.e. the requirements baseline correctly inherited the ICD's under-definition rather than either papering over it or independently rediscovering it with different framing. No new under-defined-interface finding beyond the ICD's own 11 was identified in this review. | ICD §7 (all 11 issues); CR-03, CR-09, CR-10, CR-11 (correctly cross-referenced) | None beyond what ICD §7 and the Candidate Requirements already propose. This is recorded as a corroboration, not a new finding, to satisfy this section's required coverage honestly rather than inventing a 12th issue where none was found. |
| **REQ-101** | Medium | INT-0015 (the AI-Red ground-truth-read interface, the one named, accepted deviation from fog-of-war) is well-documented in the ICD and correctly cited by FR-9110. However, the ICD does not state **what happens if AI-Red's ground-truth read is exercised concurrently with a human-Red hot-seat session** on the same Role Assignment (OR-7's "unseated-role" behavior) — i.e. whether AI-Red's read access is gated by seat occupancy at all, or is always-on regardless of whether a human is currently seated in Red. Neither the ICD, GDS-04 §1.10's Role Assignment entry, nor `requirements/01` FR-9110 states this interaction explicitly. | INT-0015; FR-9110; GDS-04 §1.10; OR-7 | Add a sentence to INT-0015's "Preconditions" (or FR-9110's Notes) stating whether AI-Red's ground-truth access is conditioned on Red being currently unseated, always active as a parallel doctrine-advisory source, or some other explicit rule — currently unstated in any reviewed document. |

---

## Summary table

| § | Dimension | Findings (IDs) | Highest severity |
|---|---|---|---|
| 0 | Skill-conformance | REQ-001, REQ-002 | High |
| 1 | Completeness | REQ-010, REQ-011, REQ-012, REQ-013 | Medium |
| 2 | Consistency | REQ-020, REQ-021, REQ-022, REQ-023 | High |
| 3 | Traceability | REQ-030, REQ-031, REQ-032 | High |
| 4 | Testability | REQ-040, REQ-041 | Medium |
| 5 | Ambiguity | REQ-050, REQ-051 | Medium |
| 6 | Duplication | REQ-060, REQ-061 | Medium (cross-listed) |
| 7 | Architectural alignment | REQ-070, REQ-071, REQ-072 | High |
| 8 | Missing requirements | REQ-080, REQ-081, REQ-082 | High (cross-listed ×2) |
| 9 | Over-constrained | REQ-090, REQ-091 | Medium |
| 10 | Under-defined interfaces | REQ-100, REQ-101 | High (corroboration) |

**Headline take:** the FR/NFR baseline is internally disciplined — no genuine duplication, no
unjustified ambiguity, no implementation leakage, and no over-constraint was found on review. The
baseline's real gaps are (a) **the skill's own Step 3/4 deliverables were never produced**
(REQ-001/002/030), leaving the entire corpus without a queryable traceability matrix; (b) **two
small but genuinely missing FR leaves** — the Role Assignment bus/payload cardinality rule
(REQ-072/080) and the hot-seat screen-blank menu (REQ-010/081) — where a real system behavior is
described only in prose at the architecture layer and never promoted to a checkable requirement;
and (c) a handful of **already-self-flagged open issues that exist in two places without
cross-referencing each other** (REQ-021/060, the OR-6/multi-session tension). Nothing found rises
to Critical: no requirement contradicts another requirement, an ADR, or the architecture as
currently resolved, and the assessment/scoring gap that dominated the prior architecture-level
review is confirmed closed by ADR-0029 (REQ-070).

## Related

[`docs/requirements/01-functional-requirements.md`](../requirements/01-functional-requirements.md) ·
[`docs/requirements/02-non-functional-requirements.md`](../requirements/02-non-functional-requirements.md) ·
[`docs/design/05-interface-control-document.md`](../design/05-interface-control-document.md) ·
[`docs/architecture/05-functional-requirements.md`](../architecture/05-functional-requirements.md) (GDS-05) ·
[`docs/architecture/04-domain-model.md`](../architecture/04-domain-model.md) (GDS-04) ·
[`docs/architecture/adr/INDEX.md`](../architecture/adr/INDEX.md) ·
[`docs/reviews/architecture-review.md`](architecture-review.md) (sibling review, GDS-01–04 only;
cross-referenced throughout rather than duplicated) ·
[`.claude/skills/requirements-engineering/SKILL.md`](../../.claude/skills/requirements-engineering/SKILL.md)
(the skill whose Step 1/2 outputs are this review's primary subject, and whose own Step 3/4 gap is
REQ-001/002's basis).
