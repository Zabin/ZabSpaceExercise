# Requirements Update Report — disposition of `strategic-review-2026-07.md` at the requirements tier

> **Status:** Complete — requirements-tier disposition recorded for all 24 recommendations;
> documentation changes for every item that warranted one are landed as of this revision.
> **Source:** [`strategic-review-2026-07.md`](strategic-review-2026-07.md) (SRB-2026-07), Part 6
> "Recommendations" (R1–R24), as already dispositioned once at the architecture tier by
> [`architecture-update.md`](architecture-update.md).
> **Scope:** `docs/requirements/01-functional-requirements.md`,
> `docs/requirements/02-non-functional-requirements.md`,
> `docs/requirements/03-requirements-traceability-matrix.md` — the three documents
> `architecture-update.md` §5 explicitly left untouched ("`docs/requirements/` (GDS-05 and its
> elaboration) — **not modified**, per instruction"). This report is that follow-up pass, run with
> the `04-requirements-engineering` skill, per explicit instruction to determine whether any
> *accepted* recommendation requires a new Functional Requirement, a new Non-Functional
> Requirement, a modification to an existing requirement, or a traceability update — and, if so,
> to make it.
> **No architecture was redesigned.** GDS-00–05, the ADR set, the ICD, and
> `architecture/strategic-assumptions-register.md` are read as fixed inputs in this pass, exactly
> as `architecture-update.md` left them; nothing in `docs/architecture/` or `docs/design/` was
> edited to produce this report.

[↑ Docs index](../INDEX.md) · [Strategic review](strategic-review-2026-07.md) ·
[Architecture disposition](architecture-update.md)

---

## 1. Bottom line

**No numbered, baselined `FR-1xxx` or `NFR-1xxx` requirement was added, removed, or had its content
modified.** This confirms, independently and at the requirements tier, the same conclusion
`architecture-update.md` §1 already reached at the architecture tier ("No recommendation required a
requirements change"). Every one of the 24 recommendations either (a) needed no requirements-tier
action at all, because its architecture-tier disposition already fully captures it, or (b) named a
not-built, not-scheduled candidate component/concept/risk that belongs in this baseline's existing
**Candidate Requirements** mechanism — the same mechanism `docs/requirements/01` already used for
eleven pre-existing gaps (`CR-01`–`CR-11`) before this review ever ran. Candidates are explicitly
excluded from the numbered baseline by the `04-requirements-engineering` skill's own rule ("Never
promote a candidate into the numbered tree within the same pass that names it"), so adding them is
not a "new requirement" in the sense the task's question is really asking about — it is
**traceability bookkeeping** that keeps the requirements-tier documentation from silently omitting
what the architecture tier now names.

What this pass *did* find and fix, independent of any single recommendation, is a **documentation
hygiene defect of the same species `architecture-update.md` (via `ADR-0031`) already fixed once at
the architecture tier** — see §3.

## 2. Method

1. Read `strategic-review-2026-07.md` Part 6 (R1–R24) and `architecture-update.md`'s disposition
   table in full — the set of already-`Accepted` recommendations this pass is scoped to react to.
2. Read every document `architecture-update.md` §5 actually changed: `ADR-0030`, `ADR-0031`, the
   new [Strategic Assumptions Register](../architecture/strategic-assumptions-register.md), and the
   amended sections of GDS-00, GDS-01 §12, GDS-02 (candidate external-systems table + Open Question
   5), GDS-03 §5, GDS-04 §3, and ICD §7 items 2 and 12 — this is the requirements-engineering
   skill's Step 0 "changed inputs" pass (per the skill's own worked example: "we added ADR-014 —
   update the requirements," re-run Step 0 against the delta, not from scratch).
3. Read the current on-disk content of `docs/requirements/01`, `02`, and `03` in full, including
   their existing `Candidate Requirements`/`Candidate NFRs` sections (`CR-01`–`CR-11`,
   `CNFR-01`–`CNFR-06`) and the traceability matrix's reverse indices.
4. For each of the 24 recommendations, cross-checked `architecture-update.md`'s disposition against
   the current requirements baseline: does the architecture-tier action (actioned or deferred) leave
   behind something that reads as a requirement — a capability, a quality attribute, a risk needing
   a system-level mitigation — that isn't already visible somewhere in `docs/requirements/`? Table
   in §4.
5. Where a gap was found, applied the same discipline `CR-01`–`CR-11`/`CNFR-01`–`CNFR-06` already
   established: a new Candidate Requirement, not a baselined one, with a `Source` field citing the
   exact architecture-tier section that names it — never inventing a fact, a number, or a
   commitment the source documents don't themselves make.
6. Updated `docs/requirements/03-requirements-traceability-matrix.md`'s master-matrix rows and
   reverse indices to match, following its own stated "no cell populated by inference" discipline —
   every new cell is either a value drawn directly from a new candidate's own `Source` field, or
   `UNASSIGNED`.

## 3. The governance-consistency defect this pass found and fixed

`strategic-review-2026-07.md` §4.1 finding 1 and recommendation R5 flagged that `architecture/
00-vision.md` (GDS-00) §7 still carried stale "the build spec wins" language contradicting the
already-declared blanket GDS supersession (`architecture/INDEX.md`, `CLAUDE.md`). `ADR-0031`
corrected that one document. **The same defect existed independently, uncorrected, in
`docs/requirements/01-functional-requirements.md` and
`docs/requirements/02-non-functional-requirements.md`'s own header notes** — both documents quoted
or restated the pre-supersession rule when describing their relationship to the legacy build-spec
tag schemes (`build-spec/02` §5–6, `build-spec/04` §9):

- `requirements/01`'s "pre-existing requirement tag scheme" note stated: *"Per `CLAUDE.md`, the
  build spec 'is the binding v1 spec — on any conflict the build spec wins.' ... the build-spec tag
  remains the binding statement."* This was wrong on two counts even under the *old*,
  narrower supersession rule (a build-spec module stays authoritative only until its own GDS
  level's merge gate closes): GDS-05 (Functional Requirements) had **already closed its merge gate**
  (`✅ Authored, merge gate closed`, per `ROADMAP.md`) before this note was written, so build-spec/02
  §5–6 was already superseded on the old rule's own terms, let alone the current blanket one.
- `requirements/02`'s equivalent note stated: *"Build-spec/04 §9 therefore remains the binding NFR
  statement."* This one was defensible under the old rule (GDS-06 genuinely has no authored content
  yet), but is still stronger than `CLAUDE.md`'s current text supports: an unauthored GDS level's
  build-spec counterpart is "deprecated legacy reference, not a binding tie-breaker" — not
  "binding."

`architecture-update.md` could not have caught this: its own scope statement (§1) restricts it to
six named architecture-tier documents, and `docs/requirements/` is explicitly outside that list.
This report closes the gap `architecture-update.md` left open by its own honest scoping — the same
"correct a stale statement of an already-settled fact" pattern `ADR-0031` used, applied one tier
down. **This is a text correction, not a requirements-content change**: no `FR-1xxx`/`NFR-1xxx`
leaf's Description, Acceptance Criteria, or Priority was touched by this fix — only the header notes
describing each document's relationship to the legacy build-spec tag scheme.

## 4. Recommendation-by-recommendation requirements-tier disposition

Reading `architecture-update.md`'s own disposition column, not re-litigating it — this table asks
only "does the *requirements* tier need anything **on top of** what the architecture tier already
did."

| # | Architecture-tier disposition (from `architecture-update.md`) | Requirements-tier action needed? | What was done |
|---|---|---|---|
| R1 | Accepted (deferred) — encyclopedia labor, tracked in `FUTURE-WORK.md` §13 | None | No requirement describes encyclopedia sourcing; out of this baseline's subject matter entirely. |
| R2 | Accepted (deferred) — GDS-06–10 authoring is the ladder's own next step | None directly | `CR-18`'s source citation and the header corrections (§3) both note GDS-06's unauthored status; no new requirement needed beyond that existing framing. |
| R3 | **Accepted (actioned)** — new Strategic Assumptions Register | Traceability only | Register added as a cited **Authoritative input** in `01` and `02`'s headers and in `03`'s Method section; no assumption in the register states a system requirement itself (register is explicitly "descriptive, not binding" per its own text), so no Candidate was derived from it directly — individual candidates below cite specific register entries (A3, A9) where relevant. |
| R4 | **Accepted (actioned)** — new `ADR-0030` (AI-determinism doctrine) | Requirement modification (field-level only) | Added `ADR-0030` to `FR-9110`'s **Related ADRs** field and to the ADR→Requirement reverse index. No behavioral change to `FR-9110`'s Description/Acceptance Criteria — AI-Red already complied with what ADR-0030 generalizes (per ADR-0030's own Consequences), so the leaf's substance was already correct; only its cross-reference was incomplete. |
| R5 | **Accepted (actioned), split** — GDS-00 §7 fixed; DOM-002/DOM-005 gap acknowledged, not closed | Requirement modification (header text only) | See §3 above — independently found the same stale-language defect in `requirements/01` and `02` and fixed both, mirroring `ADR-0031`'s reasoning. The DOM-002/DOM-005 gap itself is **not** a requirements-baseline defect (FS-201/FS-301 already have `✅` FR/NFR-tier coverage in this baseline — e.g. no FR/NFR claims an assessment framework exists that doesn't); left exactly as `ADR-0031` left it. |
| R6 | **Accepted (actioned), partial** — new GDS-01 §12 "Negative training" risk row | New Candidate Requirement | Added **`CR-18`**. Three of the risk row's four named candidates already had baseline coverage (see `CR-18`'s own text for the cross-references); the fourth — facilitator/adjudication-consistency support — had none until now. |
| R7 | Accepted (deferred) — already tracked via `ADR-0024`/`FUTURE-WORK.md` §1 | None | Already fully covered by pre-existing `CR-01` and `CNFR-06`; nothing new to add. |
| R8 | Accepted (deferred) — Monte Carlo harness, `FUTURE-WORK.md` §13 | None | No architecture-tier candidate component or concept was added for this (it needs no new architecture per `architecture-update.md`'s own note); a headless batch runner is an implementation detail of existing determinism/seed/eventlog guarantees already stated in `NFR-1500`/`FR-1120`, not a new requirement. |
| R9 | Accepted (deferred) — commission GAP-07 research | None | Research-commissioning action; no system requirement implied. |
| R10 | Accepted (deferred) — counterfactual AAR + belief-vs-truth analytics | None | Both build entirely on already-baselined `FR-7310`/`FR-7320` (AAR replay/branch-compare) and the fog-of-war split (`FR-6210`); no new candidate component was added at the architecture tier (`architecture-update.md` R10 row: "no new candidate component was needed in §5's table"), so none is added here either. |
| R11 | **Accepted (actioned), partial** — new GDS-02 candidate external-system row + GDS-03/04 candidate entries | New Candidate Requirement | Added **`CR-14`**, consolidating the GDS-02 external-system row and the GDS-03/04 actor-class entries (they describe one gap from two angles — external interface vs. internal actor concept — and are cited together, as GDS-03 §5 itself does for the equivalent overlap on other rows). |
| R12 | Accepted (deferred) — GAP-01 research + environment term | None | Research + engine-term work; no architecture-tier candidate component was added for this recommendation specifically (only GAP-01 is named, in the register at an adjacent assumption, not as its own GDS-03/04 row), so no Candidate Requirement is derived either — there is nothing yet to cite. |
| R13 | Accepted (deferred), direction acknowledged — new GDS-03 §5 + GDS-04 §3 candidate component | New Candidate Requirement | Added **`CR-12`**. |
| R14 | Accepted (deferred), direction acknowledged — new GDS-03 §5 + GDS-04 §3 candidate component; GDS-02 OQ5 cross-ref | New Candidate Requirement | Added **`CR-13`**. |
| R15 | Accepted (deferred), direction acknowledged — new GDS-03 §5 + GDS-04 §3 candidate component | New Candidate Requirement | Added **`CR-15`**. |
| R16 | Accepted (deferred), direction acknowledged — new GDS-03 §5 candidate component | New Candidate Requirement | Added **`CR-17`**. |
| R17 | Accepted (deferred), direction acknowledged — new GDS-03 §5 candidate component | New Candidate Requirement | Added **`CR-16`**. |
| R18 | Accepted (deferred) — scenario generator + FS-108 promotion, `FUTURE-WORK.md` §13 | None | Content/tooling work on the already-baselined Content & Data subsystem (`FR-5110`, `FR-5310`); no new architecture-tier candidate component was added (`architecture-update.md`'s own note: "no new architecture concept required"), so no new requirements-tier entry either. |
| R19 | **Accepted (actioned), partial** — ICD §7 items 2 and 12 cross-referenced/added | New Candidate Requirement | Added **`CNFR-07`**, tracing to the new ICD §7 item 12 (GAP-11 federation gap). The item-2 half of R19 (security growth path) was already fully covered by pre-existing `CNFR-04`; not duplicated. |
| R20 | Accepted (deferred), Long-Term Vision | None | No architecture edit at that tier either; nothing to trace yet. |
| R21 | Accepted (deferred), Long-Term Vision | None | Depends on R7/R8 landing first; no new requirement content exists to name yet. |
| R22 | Accepted (deferred), research-only | None | Explicitly does not touch GDS-02/04's current Earth-centric framing; no requirement is implicated. |
| R23 | **Accepted (actioned), light touch** — "already covered" by an existing GDS-01 §6 scenario | None | No new GDS content was added for this recommendation (`architecture-update.md`'s own finding), so nothing new to trace at the requirements tier either. |
| R24 | Accepted (deferred), Long-Term Vision | None | Depends on R9 landing first; nothing to trace yet. |

**Fifteen of 24 recommendations needed no requirements-tier action beyond what `architecture-update.md`
already recorded.** Nine needed a traceability addition; of those, one (R4) was a field-level
cross-reference on an *existing* baselined leaf, and eight (R6, R11, R13–R17, R19) each produced
exactly one new Candidate Requirement. **Zero** needed a new baselined FR/NFR or a change to an
existing baselined FR/NFR's substantive content.

## 5. New IDs assigned

| ID | Title | Traces to (recommendation) |
|---|---|---|
| CR-12 | Proliferated-Constellation Aggregation Layer | R13 |
| CR-13 | Coalition / Multi-Cell Generalization | R14 |
| CR-14 | Commercial / Gray-Actor Class & purchasable SDA/comms services | R11 |
| CR-15 | Campaign / Session-Persistence Container | R15 |
| CR-16 | Ground-Segment-as-Terrain Cyber Model | R17 |
| CR-17 | Persistent Debris / STM Environment Layer | R16 |
| CR-18 | Facilitator / cross-session adjudication-consistency support | R6 |
| CNFR-07 | Distributed-simulation / exercise-interoperability federation | R19 |

All eight are added to their documents' existing `Candidate Requirements`/`Candidate NFRs`
sections, marked `CANDIDATE — NOT BASELINED` in the traceability matrix, exactly like the
pre-existing `CR-01`–`CR-11`/`CNFR-01`–`CNFR-06`. None is promoted to the numbered `FR-1xxx`/
`NFR-1xxx` baseline — per the `04-requirements-engineering` skill's own rule, a candidate cannot be
baselined in the same pass that names it, and in every one of these eight cases the architecture
tier itself explicitly marked the underlying component/concept/risk as "not built, not scheduled,
not committed" (GDS-03 §5's own header) or "no mitigation implemented in v1" (GDS-01 §12) — there is
no committed system behavior yet for a baselined requirement to describe.

## 6. Traceability updates made

All in `docs/requirements/03-requirements-traceability-matrix.md`:

- Eight new master-matrix rows (`CR-12`–`CR-18` in the Candidate Requirements table, `CNFR-07` in
  the Candidate NFRs table).
- Two new rows in the **ADR → Requirement** reverse index (`ADR-0030` → `FR-9110`; `ADR-0031` →
  `CR-18`).
- `CNFR-07` added to the **Architecture Component → Requirement** (C2) and **Interface →
  Requirement** (INT-0006) reverse indices, both via its own explicit ICD §7 item 12 cross-reference
  — not inferred.
- Nine new rows in the **Requirement → Future Feature** reverse index (`CR-12`–`CR-17`, `CNFR-07`),
  each citable only because the candidate's own `Source`/Source-documents field names the
  `FUTURE-WORK.md` section, per that index's existing discipline.
- The eight new candidates added to the **Requirement → Implementation Package** reverse index's
  `UNASSIGNED` bucket (honestly — none has shipped code; inventing a package path here would violate
  the matrix's own stated "no cell populated by inference" rule).
- The "Method and discipline" section's cited ADR range updated (`ADR-0029` → `ADR-0031`) and the
  Strategic Assumptions Register added as a read input.
- A "Strategic review reconciliation" section added, mirroring the convention already used across
  the GDS ladder and the ICD.

Corresponding "Strategic review reconciliation" sections were added to `01-functional-requirements.md`
and `02-non-functional-requirements.md` themselves, recording the same set of changes in place (the
same cross-document-index convention `architecture-update.md` §5 established for the GDS ladder).

## 7. What was deliberately not done

- **No FR/NFR was promoted from Candidate to baseline.** Even where a recommendation was
  architecture-tier "Accepted (actioned)" (R3, R4, R6 partial, R11 partial, R19 partial), the
  *system behavior* each implies remains not-built — actioning the *documentation* (a register, an
  ADR, a candidate-component row) is not the same as committing the *system* to a testable
  behavior, and only the latter crosses this baseline's bar for a numbered leaf.
- **No existing baselined FR/NFR's Description, Acceptance Criteria, or Priority was changed.** The
  strategic review's own Red Team finding that Δv-terminality and the fixed five-D ontology are
  candidates for a "negative training" critique (§4.5 of the review) does **not** mean `FR-1310` or
  `FR-1410` are wrong as written — both already document their v1 scope accurately and
  intentionally, and the review's own disposition (`architecture-update.md` §4) confirms nothing
  proposes relaxing either. Rewriting either leaf to hedge against a risk that is tracked elsewhere
  (the Strategic Assumptions Register, GDS-01 §12) would have manufactured a requirements defect
  that does not currently exist.
- **No new NFR category was added.** The skill's fixed 15-category taxonomy already accommodated
  every new candidate's nature (`CNFR-07` under Interoperability's existing category, alongside
  `NFR-3200`/`NFR-3300`).
- **DOM-002/DOM-005's authoring gap was not retroactively closed at the requirements tier either.**
  Same reasoning `ADR-0031` gives at the architecture tier (§3 there): a rushed requirements-tier
  patch to a domain-framework gap would be the "retrofitted twice" failure mode the review itself
  warns against. `CR-18` names the one concrete, currently-uncovered piece of that gap (adjudication
  consistency) without attempting to pre-author DOM-005's eventual validation-criteria content.

## 8. Related

[`strategic-review-2026-07.md`](strategic-review-2026-07.md) (the source review) ·
[`architecture-update.md`](architecture-update.md) (the architecture-tier disposition this report
follows and does not duplicate) ·
[`docs/requirements/01-functional-requirements.md`](../requirements/01-functional-requirements.md)
(§ "Strategic review reconciliation") ·
[`docs/requirements/02-non-functional-requirements.md`](../requirements/02-non-functional-requirements.md)
(§ "Strategic review reconciliation") ·
[`docs/requirements/03-requirements-traceability-matrix.md`](../requirements/03-requirements-traceability-matrix.md)
(§ "Strategic review reconciliation") ·
[`architecture/strategic-assumptions-register.md`](../architecture/strategic-assumptions-register.md) ·
[`architecture/adr/ADR-0030-ai-determinism-doctrine.md`](../architecture/adr/ADR-0030-ai-determinism-doctrine.md) ·
[`architecture/adr/ADR-0031-governance-record-consistency.md`](../architecture/adr/ADR-0031-governance-record-consistency.md) ·
[`FUTURE-WORK.md`](../FUTURE-WORK.md) §13 ·
[`ROADMAP.md`](../../ROADMAP.md).

---

*End of report. No document outside `docs/requirements/` (plus this report itself) was modified to
produce it.*
