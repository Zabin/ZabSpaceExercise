# Architecture Update — disposition of `strategic-review-2026-07.md`

> **Status:** Complete — disposition recorded for all 24 recommendations; documentation changes for
> every `Accepted (actioned)` item are landed as of this revision.
> **Source:** [`strategic-review-2026-07.md`](strategic-review-2026-07.md) (SRB-2026-07), Part 6
> "Recommendations" (R1–R24).
> **Reviewed against:** GDS-01 (Concept of Operations), GDS-02 (System Context), GDS-03
> (Architecture), GDS-04 (Domain Model), the Interface Control Document
> (`design/05-interface-control-document.md`), and the ADR set (`architecture/adr/`) — the six
> artifacts this update was scoped to. Requirements (GDS-05, `docs/requirements/`) were **not**
> modified, per instruction.

[↑ Docs index](../INDEX.md) · [Reviews](strategic-review-2026-07.md)

---

## 1. How this disposition was made

`strategic-review-2026-07.md` itself states its own ground rules (its "Ground rules observed by
this board" section): it does not rewrite approved architecture, create implementation tasks,
generate code, or modify requirements; its product is blind spots, risks, and opportunities, and
"resolution belongs to the project's own governance mechanisms." This update *is* that resolution
step for the review's 24 formal recommendations (Part 6). Each recommendation is dispositioned as
one of:

- **Accepted (actioned)** — the recommendation is agreed, and the architecture-tier documentation
  change it implies has been made in this pass, scoped strictly to the six documents above.
- **Accepted (deferred)** — the recommendation is agreed in principle, but its correct action is
  outside this pass's scope: new engine/UI capability (implementation, not documentation), research
  authoring (a different skill's job — `02-research-doctrine-exercises`/`02-research-ow-orbital-mechanics`),
  domain-framework authoring (`docs/domains/`, out of the six-document scope), or continuation of
  the GDS ladder's own already-scheduled sequential authoring (GDS-06–10, also out of scope). These
  are tracked so the acceptance is not lost, not silently implemented.
- **Rejected** — none. See §4 for why.

No recommendation required a requirements change, and none was rejected — see §4 for the reasoning
on both points before reading the recommendation is a rubber stamp.

## 2. Disposition table

| # | Recommendation (abridged) | Disposition | Action taken / where tracked |
|---|---|---|---|
| R1 | Close the encyclopedia sourcing/scope defect (GAP-13), R500 first | Accepted (deferred) | Encyclopedia-wide labor task for `02-research-doctrine-exercises`/`02-research-ow-orbital-mechanics`, not an edit to the six scoped documents. Tracked in `FUTURE-WORK.md` §13 (new, added by this update) and the [Strategic Assumptions Register](../architecture/strategic-assumptions-register.md) A10. |
| R2 | Author GDS-06–10 (NFRs first) | Accepted (deferred) | Already the architecture ladder's own next scheduled step (`architecture/INDEX.md` §1: "GDS-06 is the next level to author") — this update does not pre-empt the `03-architecture-design-synthesis` skill's sequential workflow. Register entry A11 names the risk of leaving it open. |
| R3 | Publish a strategic-assumptions register (A1–A8) as a living document | **Accepted (actioned)** | New [`architecture/strategic-assumptions-register.md`](../architecture/strategic-assumptions-register.md), cross-linked from GDS-01 §11/§13. Extended with three assumptions the review's own §4.10 named (A9–A11) that weren't in the original A1–A8 list. |
| R4 | State the AI-determinism doctrine (A6) in one ADR | **Accepted (actioned)** | New [`ADR-0030`](../architecture/adr/ADR-0030-ai-determinism-doctrine.md). Resolves assumption A6 in the register. |
| R5 | Reconcile DOM-002/DOM-005 status with FS-201/FS-301; fix GDS-00 §7's stale "build spec wins" language | **Accepted (actioned)**, split | The GDS-00 §7 language is corrected (a stale-text fix, precedent ADR-0028). The DOM-002/DOM-005 status gap is **acknowledged, not retroactively closed** — see §3 below for why closing it now would be worse than leaving it open. Both sub-decisions recorded in new [`ADR-0031`](../architecture/adr/ADR-0031-governance-record-consistency.md). |
| R6 | Add a negative-training risk section to DOM-005 | Accepted (actioned), partial | DOM-005 itself is unauthored (out of the six-document scope; see R5). The risk register content is placed where it *can* land today: a new **Negative training** row in GDS-01 §12 Risks, naming the same four candidates the review cites. Full validation-criteria treatment remains DOM-005's job once authored. |
| R7 | Close AI-Red fog-of-war parity (FC-02 fog parity / ADR-0024's gap) | Accepted (deferred) | Already fully tracked — ADR-0024, `FUTURE-WORK.md` §1 "AI-Red fog-of-war parity", and GDS-01/02/03's respective Open Questions already record this gap and its disposition. No new documentation gap existed to close; this is implementation work. |
| R8 | Ship the headless Monte Carlo harness (IN-02/FC-14) | Accepted (deferred) | New capability, but one that requires no architecture change — it is a runner + output schema built entirely on existing seams (determinism, seeded RNG, `EventLog`, FS-301 export) that GDS-01/03 already document. Tracked in `FUTURE-WORK.md` §13. |
| R9 | Commission GAP-07 (training transfer) research to shape DOM-002/DOM-005 before they harden | Accepted (deferred) | Research commissioning + domain-framework authoring, both out of the six-document scope. Directly informs R5/R6's eventual full closure. Tracked in `FUTURE-WORK.md` §13. |
| R10 | Build counterfactual AAR (IN-01) + belief-vs-truth analytics (IN-06) | Accepted (deferred) | Feature work fully contained within existing architecture (AAR replay, `EventLog`, per-cell Track vs. ground truth) — GDS-03 §2.2/§5 already describe the seams these would use; no new candidate component was needed in §5's table. Tracked in `FUTURE-WORK.md` §13. |
| R11 | Add a commercial SDA feed to the mock SSN (thin end of FC-10) + one commercial-entanglement vignette | **Accepted (actioned)**, partial | Architecturally acknowledged now: new "Commercial SDA/services provider" row in GDS-02's candidate-future-external-systems table, and "Commercial / Gray Actor" concept in GDS-03 §5 and GDS-04 §3. The feed implementation and vignette itself are deferred (already tracked in `FUTURE-WORK.md` §7 per the review's own citation). |
| R12 | Fund GAP-01 (space environment) research + an environment term in effect/telemetry | Accepted (deferred) | Research + engine work, out of the six-document scope. Tracked in `FUTURE-WORK.md` §13 and register A2 (adjacent). |
| R13 | Proliferated-constellation program (FC-06 + GAP-10) | Accepted (deferred), direction acknowledged | New "Proliferated-Constellation Aggregation Layer" candidate component added to GDS-03 §5 and GDS-04 §3, explicitly not-built/not-scheduled. Implementation is High difficulty/Future Release per the review's own placement. |
| R14 | Coalition play (FC-09 + R316) | Accepted (deferred), direction acknowledged | New "Coalition / Multi-Cell Generalization" candidate component added to GDS-03 §5 and GDS-04 §3; GDS-02 Open Question 5 given a corroborating cross-reference. Implementation deferred (Future Release, High difficulty). |
| R15 | Campaign container + time compression (FC-13) | Accepted (deferred), direction acknowledged | New "Campaign / Session-Persistence Container" candidate component added to GDS-03 §5 and GDS-04 §3. Implementation deferred. |
| R16 | Persistent debris + conjunction wiring (FC-08 + GAP-02) | Accepted (deferred), direction acknowledged | New "Persistent Debris / STM Environment Layer" candidate component added to GDS-03 §5 and GDS-04 §3. Implementation deferred. |
| R17 | Ground-segment-as-terrain cyber deepening (FC-11 + GAP-12) | Accepted (deferred), direction acknowledged | New "Ground-Segment-as-Terrain Cyber Model" candidate component added to GDS-03 §5. Implementation deferred. |
| R18 | Scenario generator (IN-07) + facilitator authoring UX (FS-108 promotion) | Accepted (deferred) | Feature/tooling work on the existing Content & Data subsystem (GDS-03 §2.5) — no new architecture concept required. FS-108 promotion is `docs/features/` tier work, out of scope here. Tracked in `FUTURE-WORK.md` §13. |
| R19 | Document the distributed-use security growth path + GAP-11 federation-compatibility study, before the first multi-site request | **Accepted (actioned)**, partial | Cross-referenced now at the point it matters most: ICD §7 item 2 (INT-0001 authentication gap) and new ICD §7 item 12 (federation/GAP-11 not examined). The growth-path document and federation study themselves are real authoring work, deferred and tracked in `FUTURE-WORK.md` §13. |
| R20 | Human-AI teaming laboratory program (FC-01 + FC-15) | Accepted (deferred), Long-Term Vision | No architecture edit — the review's own placement is Long-Term Vision, research-first. Noted in disposition only; revisit when FC-01 is scheduled (register A4's trigger). |
| R21 | AI-vs-AI doctrine exploration (IN-08) | Accepted (deferred), Long-Term Vision | Depends on R7 (AI-Red fog parity) and R8 (Monte Carlo harness) landing first; no architecture edit needed until then. |
| R22 | Cislunar research line (FC-07 + GAP-04) | Accepted (deferred), research-only | Research work, out of scope. Does not contradict GDS-02/04's current Earth-centric framing (Kepler+J2, GMST ECI↔ECEF) — purely additive future scope per the review's own "research now, build later" framing. |
| R23 | Multi-domain effects abstraction (FC-12 + GAP-09) | **Accepted (actioned)**, light touch | GDS-01 §6 already carries an illustrative, explicitly-not-implemented cross-domain-dependency scenario (added during the R313–R317 integration) — the natural landing point for this recommendation. No new edit was needed there since that scenario already states the caveat this recommendation would otherwise ask for; recorded here as "already covered," not as a new document change. |
| R24 | Training-transfer longitudinal validation study (follow-through on R9) | Accepted (deferred), Long-Term Vision | Depends on R9/DOM-002/DOM-005 landing first. No architecture edit. |

## 3. Why R5/R6 stop short of a full fix (worked example of the deferral discipline)

R5 and R6 are the two recommendations most tempting to "just finish" — DOM-002/DOM-005 could be
stub-authored in an afternoon, and it would make the status column green. This update deliberately
does not do that, and the reasoning is worth stating once rather than leaving implicit:

- FS-201 and FS-301 are **shipped, tested, working features.** They are not broken. The
  inconsistency is that the domain frameworks *that formally justify them* were never authored —
  a paperwork-ordering problem, not a functional defect.
- The review's own R9 recommends commissioning GAP-07 (training-transfer) research specifically so
  DOM-002/DOM-005 are "not authored twice." Authoring them now, under this update's time box, to
  close a status color, would produce exactly the rushed-then-redone outcome R9 warns against.
- [`ADR-0031`](../architecture/adr/ADR-0031-governance-record-consistency.md) records this
  reasoning formally and splits the two defects R5 bundles together: the stale text (GDS-00 §7) is
  cheap and unambiguous to fix, so it is fixed; the domain-framework gap is real and substantive,
  so it is named and left for the correct future process rather than papered over.

This is the general pattern this update follows wherever a recommendation's "correct" action would
require inventing content outside this pass's actual scope: acknowledge, cross-reference, and track
— never fabricate a shortcut version of the real deliverable.

## 4. Why nothing was rejected

Every one of the 24 recommendations was checked against `CLAUDE.md`'s six load-bearing invariants
(deterministic core, UI-agnostic engine, fog-of-war at the boundary, plan-first commanding,
sub-stepped clock, content-as-data) and against every `Accepted` ADR. None proposes relaxing
determinism, moving fog-of-war enforcement out of the session-layer boundary, allowing instant
window-independent commanding outside the cyber exception, or any other invariant violation — the
review's own Part 5 "Innovation Opportunities" section states it "deliberately avoided ideas
requiring new architecture," and Part 6's recommendations follow that same discipline. Where the
review's own Red Team (Part 4) raised a genuine tension against the baseline (e.g. "byte-identical
determinism may be a stronger invariant than the mission requires," §4.1 finding 2), the board
explicitly declined to recommend relaxing it — so there was nothing in that finding to disposition
as a recommendation in the first place. Consequently every recommendation lands as **Accepted**, at
either the *actioned* or *deferred* granularity in §2 — none warranted an outright **Rejected**.

## 5. Consolidated changelog — every document change made in this pass

Each document below also carries its own "Strategic review reconciliation" section recording the
same changes in place, immediately above its Merge gate (or, for the ICD, above its still-open
Merge gate). This section is the single cross-document index so a reader doesn't have to open all
six to see the full picture — the same convention `architecture-review-changelog.md` established
for the prior review.

### New documents

| Document | Purpose | Recommendation |
|---|---|---|
| [`architecture/strategic-assumptions-register.md`](../architecture/strategic-assumptions-register.md) | Living register of 11 load-bearing assumptions (A1–A11), each with a break condition and a review trigger | R3 |
| [`architecture/adr/ADR-0030-ai-determinism-doctrine.md`](../architecture/adr/ADR-0030-ai-determinism-doctrine.md) | States the general rule that non-deterministic components stay outside `engine/` and enter only via ordered `SessionAPI` events | R4 |
| [`architecture/adr/ADR-0031-governance-record-consistency.md`](../architecture/adr/ADR-0031-governance-record-consistency.md) | Corrects GDS-00 §7's stale supersession language; formally acknowledges (without retroactively closing) the DOM-002/DOM-005-vs-FS-201/FS-301 status gap | R5 |
| This document (`reviews/architecture-update.md`) | Disposition record for all 24 recommendations | — (the review's own requested deliverable) |

### GDS-00 — Vision

| Section | Change | Recommendation |
|---|---|---|
| §7 Relationship to the build spec | Rewritten to state the already-declared blanket supersession of `build-spec/` accurately, replacing stale "build spec wins" language | R5 (via ADR-0031) |
| Metadata | Cross-references to ADR-0031 and the strategic review; version bumped 1.0 → 1.1 | — |

### GDS-01 — Concept of Operations

| Section | Change | Recommendation |
|---|---|---|
| §12 Risks | New **Negative training** risk row naming AI-Red exploitability, Δv terminality, the fixed five-D ontology, and adjudication drift | R6 |
| §11/§13 (no direct edit) | A1–A11 consolidated in the new Strategic Assumptions Register rather than duplicated inline | R3 |
| (conceptual) Assumption A6 | Marked resolved, pointing to ADR-0030 | R4 |
| Metadata | Cross-references to the strategic review, this disposition document, the register, and ADR-0030; version bumped 1.3 → 1.4 | — |

### GDS-02 — System Context

| Section | Change | Recommendation |
|---|---|---|
| Candidate future external systems table | New "Commercial SDA/services provider" row | R11 |
| Open Question 5 (coalition-partner actor) | Appended corroborating citation to R14/§4.7 | R14 |
| Metadata | Cross-references to the strategic review and this disposition document; version bumped 1.4 → 1.5 | — |

### GDS-03 — Architecture

| Section | Change | Recommendation |
|---|---|---|
| §5 Forward-looking architectural considerations | Six new candidate components: Proliferated-Constellation Aggregation Layer, Coalition/Multi-Cell Generalization, Commercial/Gray-Actor Class, Campaign/Session-Persistence Container, Ground-Segment-as-Terrain Cyber Model, Persistent Debris/STM Environment Layer | R13, R14, R11, R15, R17, R16 |
| Metadata | Cross-references to the strategic review, this disposition document, and ADR-0030; version bumped 1.3 → 1.4 | — |

### GDS-04 — Domain Model

| Section | Change | Recommendation |
|---|---|---|
| §3 Forward-looking domain concepts | Four new candidate concepts: Commercial/Gray Actor, Coalition Cell/Multi-Blue Structure, Persistent Debris/Environment Object, Campaign/Session-Persistence Container | R11, R14, R16, R15 |
| Metadata | Cross-references to the strategic review and this disposition document; version bumped 1.2 → 1.3 | — |

### Interface Control Document (`design/05-interface-control-document.md`)

| Section | Change | Recommendation |
|---|---|---|
| §7 item 2 | Appended cross-reference to R19's security-growth-path recommendation | R19 |
| §7 item 12 (new) | Distributed simulation/exercise-interoperability federation (GAP-11) not examined against any interface — flagged | R19 |
| Header metadata | ADR count reference updated 0029 → 0031; cross-references to the strategic review and this disposition document added | — |

### ADR set

| Document | Change |
|---|---|
| `architecture/adr/INDEX.md` | Added ADR-0030/ADR-0031 rows; updated total count 29 → 31; added a new paragraph explaining the third category of ADR (review-driven, distinct from both "already-implicit" and "resolved Open Question") |
| `architecture/INDEX.md` §3 | Updated ADR count 29 → 31 with a pointer to this disposition document |

### Not edited (explicit — see §2/§3 above for why)

- `docs/domains/INDEX.md` (DOM-002, DOM-005 rows) — left `⛔`, intentionally, per ADR-0031.
- `docs/features/feature-index.md` (FS-201, FS-301) — left `✅ Done`, correctly; not misrepresented
  to force-match DOM-002/DOM-005's status.
- `docs/requirements/` (GDS-05 and its elaboration) — **not modified**, per instruction; no
  recommendation in this review required a requirements change (see §2 — every actioned item is a
  clarification, cross-reference, or new not-built candidate-component/concept entry, never a
  functional requirement).
- `docs/architecture/06-non-functional-requirements.md` through `10-requirements-traceability-matrix.md`
  (GDS-06–10) — out of this pass's six-document scope; R2's disposition leaves their authoring to
  the ladder's own sequential process.

## 6. Related

[`strategic-review-2026-07.md`](strategic-review-2026-07.md) (the source review) ·
[`architecture-review-changelog.md`](architecture-review-changelog.md) (the prior review's
equivalent changelog, whose format this document follows) ·
[`architecture/strategic-assumptions-register.md`](../architecture/strategic-assumptions-register.md) ·
[`architecture/adr/ADR-0030-ai-determinism-doctrine.md`](../architecture/adr/ADR-0030-ai-determinism-doctrine.md) ·
[`architecture/adr/ADR-0031-governance-record-consistency.md`](../architecture/adr/ADR-0031-governance-record-consistency.md) ·
[`FUTURE-WORK.md`](../FUTURE-WORK.md) §13 (deferred-item tracking added by this update) ·
[`ROADMAP.md`](../../ROADMAP.md).
