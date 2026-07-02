# Requirements Domain-Backfill Report — DOM-002/004/005 against the requirements baseline

> **Status:** Complete — DOM-002/004/005 read in full against the requirements baseline; every
> candidate capability dispositioned (baselined, routed to Candidate Requirements, or reported as
> yielding no requirement at all).
> **Source:** `docs/feature-planning/05-feature-review.md` Finding F-01 ("Three existing Feature
> Specifications — FS-201, FS-202, FS-301 — are grounded directly in Domain documents (DOM-002/
> 004/005) but have no corresponding FR-xxxx/NFR-xxxx leaf anywhere in `docs/requirements/`").
> **Scope:** `docs/requirements/01-functional-requirements.md`,
> `docs/requirements/02-non-functional-requirements.md`,
> `docs/requirements/03-requirements-traceability-matrix.md` — run with the
> `requirements-engineering` skill against DOM-002 (Assessment Framework), DOM-004 (Research
> Framework), DOM-005 (Validation Framework), and their existing output (FS-201 Competency
> Assessment, FS-202 Rubric Authoring [candidate], FS-301 Research Analytics).
> **No architecture was redesigned.** DOM-002/004/005, the ADR set, and FS-201/FS-301 are read as
> fixed inputs; nothing in `docs/domains/`, `docs/architecture/`, or `docs/features/` was edited to
> produce this report.

[↑ Docs index](../INDEX.md) · [Feature Review](../feature-planning/05-feature-review.md)

---

## 1. Bottom line

**Zero new leaves were added to the numbered `FR-1xxx`/`NFR-1xxx` baseline.** Three new Candidate
Requirements (`CR-19`–`CR-21`) were added; zero new Candidate NFRs were added. This is a materially
different outcome than `docs/feature-planning/05-feature-review.md` Finding F-01's own original
estimate ("roughly 6–9 additional Features" once this backfill ran) — that estimate assumed a clean
backfill and did not anticipate that two of the three domains' core capabilities directly conflict
with Accepted Architecture Decision Records discovered during this pass, not before it.

## 2. Method

Read, in full: `docs/domains/DOM-002-assessment-framework.md`, `DOM-004-research-framework.md`,
`DOM-005-validation-framework.md`; `docs/features/FS-201-competency-assessment.md` and
`FS-301-research-analytics.md` (the two non-candidate Feature Specifications these domains
ground); `docs/architecture/adr/ADR-0017-manual-adjudication.md` and
`ADR-0029-assessment-scoring-workflow-ownership.md` (both Accepted, both directly relevant per
below); `docs/requirements/01-functional-requirements.md` and `02-non-functional-requirements.md`
in full, to confirm numbering conventions (`FR-1000`–`FR-9110` are each a claimed top-level
category; `CR-01`–`CR-18`; `NFR-1100`–`NFR-3300`; `CNFR-01`–`CNFR-07`) before drafting anything.

## 3. The two conflicts this pass found

### 3.1 DOM-002/FS-201 vs. ADR-0017

DOM-002 §§3–6 and FS-201 describe an always-available, automated computation of qualitative rubric
tiers (custody quality, window discipline, belief-truth divergence, and three deferred dimensions)
per cell per exercise — the whole point of the Feature is to replace the engine's binary
objective-flip signal with something richer, computed automatically from eventlog/state data.

**ADR-0017** (Accepted): *"No automated scoring or assessment mechanism exists in v1... Outcomes
are adjudicated and narrated by the White Cell facilitator using the god-view, event log, and AAR
replay as their evidence base."* This is also the source for the already-baselined **FR-4710**
("the system shall not compute or display an automated score or win/loss determination").

DOM-002 §5 deliberately designed the rubric to avoid a single composite score — each dimension
reported on its own qualitative tier, never averaged — specifically, per its own text, to sidestep
"scoring" in the win/loss sense. This is a genuine, defensible distinction (rubric-tier reporting
is arguably not "scoring" in ADR-0017's narrower sense), but ADR-0017's own language is broader
than just scoring — it says "no automated scoring **or assessment mechanism**" — and no approved
document reconciles DOM-002's automated-rubric proposal against that broader phrase.
`docs/implementation/packages/IP-2010-competency-assessment.md`'s own header independently confirms
this is unresolved: it records the conflict as "never reconciled" and that a "Blocking Report" was
delivered directly to the project owner on 2026-07-02 (not itself a persisted document this report
can cite — evidently a chat-only deliverable from that session).

**Disposition:** routed to **CR-19**, not baselined. A requirement cannot be written until either
ADR-0017 is amended to carve out non-adjudicative descriptive measurement from its "assessment
mechanism" language, or DOM-002/FS-201 is rescoped to fit within the ADR as written.

### 3.2 DOM-004/FS-301 vs. ADR-0029

DOM-004 §5 and FS-301 describe a purpose-built export/cohort-management layer — structured per-run
records with condition-label metadata across many seeded runs — to close the stated gap that "a
researcher today would have to script directly against `eventlog`/`save` artifacts."

**ADR-0029** (Accepted): *"Raw AAR/event-log access (replay/scrub/branch-compare, plus the
existing CSV/JSON export at `/api/sessions/{sid}/aar/export.{csv,json}`) is treated as sufficient
for the 'researchers / assessment designers' stakeholder's needs. Researchers do their own
downstream analysis externally on this exported data; no new dedicated export/analysis interface
or owning subsystem is introduced."* ADR-0029's own **Alternatives Considered** section explicitly
names and rejects *"Introduce a dedicated export/analysis interface for assessment designers,
distinct from both the White Cell's adjudication view and the AAR replay UI"* — precisely what
FS-301 proposes.

This is a clearer, more direct conflict than §3.1's: no genuine distinction narrows it the way
DOM-002 §5 narrows the FS-201/ADR-0017 tension. FS-301 is, functionally, the alternative ADR-0029
already considered and rejected.

**Disposition:** routed to **CR-20**, not baselined. A requirement cannot be written until
ADR-0029 is revisited, or FS-301 is rescoped to the existing export path it currently proposes to
supersede.

### 3.3 DOM-004 §6 — human-subjects boundary (not a conflict, but not yet a requirement either)

DOM-004 §6 states that any future human-subjects-research feature requires separate authorization
and the institution's own IRB/ethics process, and explicitly warns this "must not be assumed
authorized merely because this framework describes the capability gap." This does not conflict
with any ADR, but — because CR-19/CR-20 above are themselves blocked — there is no concrete,
committed human-subjects-research feature today for a requirement to constrain. A requirement
written against a nonexistent feature would be vacuous.

**Disposition:** routed to **CR-21**, not baselined, so the constraint is recorded rather than
silently forgotten if/when a concrete feature is ever proposed.

## 4. Why DOM-005 yielded nothing at all

DOM-005 (Validation Framework) is different in character from DOM-002/004: it is
validation-*methodology* guidance (how to check whether an instrument's rubric tracks real skill,
how to check whether a fidelity claim is plausible) for a future Implementation Package's own
reasoning, not a description of a new system capability. Two specific checks against this
baseline's own writing rules confirm this conclusion rather than assert it:

- DOM-005 §7's disclosure rule ("any Implementation Package... must cite which §5 check(s) were
  applied... must not claim statistical validity beyond what sample size supports") describes a
  documentation obligation on a future engineering artifact, not an observable system behavior a
  tester could check against the running application — it fails this baseline's own "testable"
  and "implementation independent" writing rules (§ Writing rules, this skill's own governing
  document) in the same way `MSTR-007`'s citation discipline for the research encyclopedia is a
  project-governance rule, not a system NFR.
- DOM-005 §6's one arguably system-level statement — "characterize typical (not single-run)
  behavior by driving the engine across many seeds externally, never by relaxing determinism
  within a run" — restates the already-baselined **NFR-1500** (Determinism) applied externally.
  Adding a second NFR ID for the same invariant would be a duplicate, which this baseline's own
  writing rules forbid ("Consistent — no requirement may contradict another FR, an NFR... a real
  contradiction [or here, duplication] is a Requirements Review finding, not something to paper
  over").

**Disposition:** no new FR, no new NFR, no new Candidate Requirement, no new Candidate NFR from
DOM-005. This is the correct outcome for a domain document that is process guidance rather than a
capability specification — reported honestly rather than forcing a requirement to exist where the
source material doesn't commit to one.

## 5. New IDs assigned

| ID | Title | Status | Source |
|---|---|---|---|
| CR-19 | Automated competency-assessment rubric computation | Candidate — not baselined | DOM-002 §§3–6; FS-201; ADR-0017; FR-4710 |
| CR-20 | Dedicated multi-run/cohort research-export interface | Candidate — not baselined | DOM-004 §5; FS-301; ADR-0029 |
| CR-21 | Human-subjects research authorization/ethics boundary | Candidate — not baselined | DOM-004 §6 |

No `NFR-1xxx` or `CNFR-xx` ID was assigned (see §4).

## 6. Traceability updates made

- Added `CR-19`–`CR-21` to `01-functional-requirements.md`'s Candidate Requirements section and a
  new "DOM-002/004/005 backfill (2026-07)" reconciliation section near the end of that document.
- Added a matching "DOM-002/004/005 backfill (2026-07)" reconciliation section to
  `02-non-functional-requirements.md`, explaining the zero-new-NFR outcome.
- Added master-matrix rows for `CR-19`–`CR-21` to `03-requirements-traceability-matrix.md`
  (Candidate Requirements section, header renamed `CR-01–CR-18` → `CR-01–CR-21`); added `CR-19` to
  the `ADR-0017` reverse-index row and `CR-20` to the `ADR-0029` reverse-index row; added a
  matching "DOM-002/004/005 backfill (2026-07)" reconciliation section to that matrix.
- **Incidentally closed four pre-existing `UNASSIGNED` Impl. Package cells** (`FR-4610`, `FR-4710`,
  `FR-4720`, `FR-7220`) in the traceability matrix — not this pass's own scope, but a direct,
  mechanical side effect of this session's separate `IMP-106A`/`IP-1060` reconciliation work
  (`docs/feature-planning/05-feature-review.md` Finding F-03), landed in the same session and
  recorded here so the matrix's own changelog doesn't attribute it to the wrong pass.
- Updated `docs/feature-planning/05-feature-review.md` Finding F-01's own Recommendation to
  correct its prior "roughly 6–9 additional Features" estimate, which did not anticipate the
  ADR-0017/ADR-0029 conflicts §3 above documents.

## 7. What was deliberately not done

- **ADR-0017 and ADR-0029 were not amended, reinterpreted, or narrowed.** Both remain Accepted, as
  written. Resolving either conflict — by amending the ADR, or by rescoping DOM-002/FS-201 and
  DOM-004/FS-301 to fit within them — is a decision for whoever owns the architecture record, per
  this skill's own rule against unilateral conflict resolution.
- **FS-201 and FS-301 were not rewritten or rescoped.** Their existing Scope/System Behaviour
  sections are read as fixed inputs; if the project owner resolves §3's conflicts in a direction
  that changes what either Feature Specification should say, that is separate, explicit follow-up
  work against `docs/features/`, not something this pass performs by implication.
- **`docs/implementation/packages/IP-2010-competency-assessment.md`'s own BLOCKED status was not
  changed.** This report independently confirms the same conflict that package's header already
  named; it does not unblock it, since the underlying ADR-0017 conflict is exactly as unresolved
  after this pass as before it.
- **No architecture component (C1–C12) was assigned to CR-19/CR-20/CR-21.** DOM-002/004/005 are not
  yet represented in the C1–C12 component list at all (that list derives from `docs/design/05-
  interface-control-document.md`'s existing interfaces, none of which name an assessment/research
  boundary) — assigning one would be architecture work, not a candidate's traceability bookkeeping.

## 8. Related

[`docs/feature-planning/05-feature-review.md`](../feature-planning/05-feature-review.md) (Finding
F-01, the finding this report closes) · [`docs/domains/DOM-002-assessment-framework.md`](../domains/DOM-002-assessment-framework.md) ·
[`DOM-004-research-framework.md`](../domains/DOM-004-research-framework.md) ·
[`DOM-005-validation-framework.md`](../domains/DOM-005-validation-framework.md) ·
[`docs/features/FS-201-competency-assessment.md`](../features/FS-201-competency-assessment.md) ·
[`FS-301-research-analytics.md`](../features/FS-301-research-analytics.md) ·
[`docs/architecture/adr/ADR-0017-manual-adjudication.md`](../architecture/adr/ADR-0017-manual-adjudication.md) ·
[`ADR-0029-assessment-scoring-workflow-ownership.md`](../architecture/adr/ADR-0029-assessment-scoring-workflow-ownership.md) ·
[`docs/implementation/packages/IP-2010-competency-assessment.md`](../implementation/packages/IP-2010-competency-assessment.md)
(the package whose own header first flagged the ADR-0017 conflict, independently confirmed here at
the requirements tier).
