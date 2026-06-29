# Requirements Baseline Review — Gate Decision for Feature Decomposition

A principal-systems-engineer gate review answering one question: **is the requirements baseline
stable enough to start decomposing it into Feature Specifications (`FS-xxx`)?** This is a synthesis
review — it does not re-derive findings already on record in
[`architecture-review.md`](architecture-review.md) (GDS-01–04) and
[`requirements-review.md`](requirements-review.md) (FR/NFR/ICD/ADRs), it reads them, checks what
was actually fixed by [`requirements-change-log.md`](../requirements/requirements-change-log.md)
and [`architecture-review-changelog.md`](architecture-review-changelog.md), and renders a gate
decision against what's left.

**Status:** Gate review — informational. Does not modify any reviewed document.

**Scope reviewed:**
- Functional Requirements — [`docs/requirements/01-functional-requirements.md`](../requirements/01-functional-requirements.md)
  (FR-1000–FR-9110, CR-01–CR-11) and its architecture-ladder counterpart
  [`docs/architecture/05-functional-requirements.md`](../architecture/05-functional-requirements.md) (GDS-05).
- Non-Functional Requirements — [`docs/requirements/02-non-functional-requirements.md`](../requirements/02-non-functional-requirements.md)
  (NFR-1100–NFR-3300, CNFR-01–CNFR-06); GDS-06 confirmed scaffold-only (no content to review).
- ICD — [`docs/design/05-interface-control-document.md`](../design/05-interface-control-document.md)
  (INT-0001–INT-0016); GDS-09 (API Specification) confirmed scaffold-only.
- Traceability Matrix — [`docs/requirements/03-requirements-traceability-matrix.md`](../requirements/03-requirements-traceability-matrix.md);
  GDS-10 confirmed scaffold-only.
- ADRs — all 29, [`docs/architecture/adr/INDEX.md`](../architecture/adr/INDEX.md), all `Status: Accepted`.
- The two prior reviews and their change logs, to determine what is still open versus what has
  already been closed.

---

## 1. Is the architecture stable?

**Yes.** GDS-00 through GDS-05 are authored, each with a closed merge gate and its own "Review
reconciliation" section. `architecture-review.md` found **no hard architectural defect**: no
circular dependency in the subsystem graph (the near-cycle in finding §5.2 was confirmed to be
clarity-only, and GDS-04 §1.11 was edited to make `Cell View`'s read-only, one-directional
relationship to `Track` explicit), no invariant violation at the code level, and the import-guard
test enforces the most safety-critical edge mechanically, not just in prose.

Every finding that escalated to a genuine open design question has a recorded owner:

| Finding | Resolution |
|---|---|
| Assessment/scoring has no owning subsystem/domain object | Resolved by **ADR-0029** (raw AAR/event-log access is sufficient; no scoring subsystem needed) — confirmed closed by `requirements-review.md` REQ-070 |
| AI-Red subsystem placement / epistemic parity | Resolved by **ADR-0024** (stays internal; epistemic gap accepted and tracked in `FUTURE-WORK.md`) |
| `scene.py` vs. `telemetry.py` placement split | Resolved by **ADR-0025** |
| Per-session `RLock` scaling ceiling | Resolved by **ADR-0026** (documented ~16-participant estimate, not load-tested, accepted as a v1 limitation) |
| Scenario-authoring boundary (no named actor/interface) | Resolved by **ADR-0027** |
| `build-spec/03` PyQt staleness | Resolved by **ADR-0028** |
| `SSN Request` vs. `Planned Activity` overlap | Left as an explicit, cross-referenced Open Question (GDS-04 OQ3) — a real seam, not a defect, and not blocking |
| Save-file/Snapshot version compatibility across builds | Left as an explicit Open Question (GDS-04 OQ4) — a forward-looking concern, not a current defect |

Six of the original nine open items were converted into `Accepted` ADRs (ADR-0024–0029) by
explicit project-owner decision; the remaining two are genuinely deferred design questions, not
contradictions, and both are narrow enough (a possible future supertype rename; a version-pinning
policy for save files) that they don't block decomposing *other* capability clusters now.

**No architecture-stability finding in this review's scope rises above "track it."**

---

## 2. Are interfaces defined?

**Yes, at the grain appropriate for feature decomposition — not at wire level, and that gap is
explicit, not silent.**

The ICD (`docs/design/05-interface-control-document.md`) defines all 16 cross-component interfaces
(`INT-0001`–`INT-0016`): direction, ownership, preconditions, and — per `requirements-review.md`
REQ-101 — a now-explicit precondition for `INT-0015` (AI-Red is mutually exclusive with a
concurrently human-seated Red on the same Role Assignment), added via `requirements-change-log.md`
CHG-013.

What the ICD does **not** define, by its own §1/§2 scope statement: wire-level message shapes, HTTP
verbs, JSON field names, or status codes — that's GDS-09's job, and GDS-09 is `⛔ Planned
(scaffold only)`. This is disclosed in the ICD's own header ("Inputs explicitly NOT treated as
authoritative") and corroborated, not contradicted, by `requirements-review.md` REQ-100: the ICD's
own §7 lists 11 self-identified under-definition issues (no wire-level contract, INT-0001 auth gap,
`AccessWindow` persisted-vs-derived, SSN-Request supertype, Snapshot version compatibility,
Space-Track credential handling, push-vs-poll, etc.), and the review confirms each maps cleanly to
either a Candidate Requirement (`CR-03`, `CR-09`, `CR-10`, `CR-11`) or an explicit FR Notes-field
disclosure — i.e., the gap was inherited honestly into the requirements baseline, not silently
dropped or independently rediscovered with different framing.

**Verdict:** component-boundary interfaces (who owns what, what crosses each boundary, under what
precondition) are defined and traceable. Wire-level contracts are not, and don't need to be before
feature decomposition starts — that detail belongs inside each `FS-xxx`/`IMP-xxx` once a feature
touches a given interface, which is exactly when GDS-09-equivalent detail should be authored
incrementally rather than all at once up front.

---

## 3. Are requirements testable?

**Yes, with two disclosed, non-blocking exceptions.**

- Every FR/NFR leaf carries a populated **Verification Method** field (Test / Demonstration /
  Analysis / Inspection). `requirements-review.md` §4 (Testability) sampled the Demonstration-tier
  leaves (FR-4510 classification banner, FR-4610 god-view toggle) and confirmed both correctly
  justify Demonstration over Test, consistent with `CLAUDE.md`'s own disclosure that "the browser
  GUI is unverified headless." No unjustified Analysis/Inspection/Demonstration choice was found
  anywhere sampled.
- **NFR-1100/NFR-1200** (UI responsiveness at 600× time multiplier; hardware-floor frame rate) carry
  **qualitative**, not numeric, acceptance criteria — correctly, per the
  `requirements-engineering` skill's own rule ("if the inputs don't specify a number, don't
  manufacture one"). No source document (build-spec, GDS-03) commits to a numeric latency/frame-rate
  target. This is the honest state, not an authoring defect, but it does mean these two leaves are
  harder to fail a build against mechanically than a numeric SLA would be. Tracked as an open issue
  in `requirements/02`'s own completion report; not blocking, since a future revision can tighten
  the number once one exists (e.g., from playtesting).
- **No FR/NFR is currently cited by an actual `spacesim/tests/test_*.py` file** (`requirements-review.md`
  REQ-030, confirmed by grep). The 469-test suite (`CLAUDE.md`) almost certainly already covers the
  majority of "Must"-tier, Test-verified leaves in substance — the gap is *citation*, not *coverage*:
  no test currently names an FR/NFR ID in a docstring or comment, so the correspondence is inferred,
  not mechanically checkable. The traceability matrix (`docs/requirements/03-...`) correctly marks
  this `UNASSIGNED` everywhere rather than guessing, which is the right honest baseline state but
  means "is every Must requirement actually tested" is not yet a one-query answer.

**Verdict:** the requirements are written testably (clear Acceptance Criteria, justified
verification methods); the *traceability from requirement ID to the actual test that verifies it*
is the weak link, and it's disclosed rather than papered over.

---

## 4. Are there unresolved blocking issues?

**No Critical-severity finding exists anywhere in the corpus.** `requirements-review.md`'s own
headline take: "Nothing found rises to Critical: no requirement contradicts another requirement, an
ADR, or the architecture as currently resolved." This review's own read of both prior reviews and
both change logs confirms that headline still holds — every High-severity finding from
`requirements-review.md` has since been either closed or explicitly, narrowly deferred:

| High finding | Current state |
|---|---|
| REQ-002/030 — No GDS-10/Step-4 traceability matrix exists anywhere | **Partially closed.** `docs/requirements/03-requirements-traceability-matrix.md` now exists (the project-owner-requested `docs/requirements/`-side deliverable), built honestly with `UNASSIGNED` wherever no explicit evidence exists. GDS-10 itself remains scaffold-only — this is recorded in the matrix's own header as a known, accepted asymmetry, not a contradiction. **Not blocking**, since the matrix that exists is queryable and was built without inference/guessing. |
| REQ-020 — `CLAUDE.md` supersession wording could be misread as superseding `requirements/`'s own baseline | Still open; the recommended fix is a one-sentence `CLAUDE.md` clarification, explicitly flagged in the review as outside that review's authorized edit scope (`CLAUDE.md` is project guidance, not a requirements artifact). **Not blocking decomposition** — GDS-05's own "Relationship to other requirement artifacts" section already resolves the substance; only the cross-reference is missing. |
| REQ-021/060 (= duplicate of GDS-05 OQ2) — OR-6 "single exercise per process" vs. shipped multi-session `/api/sessions` | **Genuinely still open.** `requirements-change-log.md` CHG-012 confirms this was only partially actionable within its authorized file set; the converse cross-reference (GDS-05 → `requirements/02`) was not added. The underlying tension (is OR-6's wording stale post-P8, or does single-exercise-per-process mean something narrower that coexists with multi-session discovery) is unresolved. **This is the one item in this whole review that is a genuine, unresolved factual ambiguity about a shipped behavior**, not just a documentation-sync gap — see §5 below. |
| REQ-072/080 — Role Assignment bus/payload/both cardinality rule had no FR leaf | **Closed.** `requirements-change-log.md` CHG-002 added FR-3520 stating the rule directly, with its own Acceptance Criteria. |
| REQ-081 (= REQ-010) — Hot-seat screen-blank/hand-off menu had no FR leaf | **Closed.** CHG-004 added FR-6600/FR-6610. *(Note: GDS-05's own OQ1 text was not correspondingly updated to point at the new FR-6610 leaf — a small residual cross-doc sync gap, cosmetic, not blocking.)* |
| REQ-100 — ICD's 11 self-identified under-definition issues | Corroborated as still open by design (each is a deliberate, disclosed v1 scope boundary, not an oversight); each maps to a Candidate Requirement. **Not blocking** — these are exactly the kind of detail that gets resolved per-feature during decomposition, not up front. |

**Verdict: no blocking issue.** The one item worth carrying forward with a named owner rather than
silently inheriting is **OQ2 / REQ-021** (OR-6 vs. multi-session) — see Recommendation 1 below.
Everything else is either closed, a cosmetic sync gap, or a deliberately-scoped-out wire-level
detail that belongs in feature-level work, not the baseline gate.

---

## 5. Are there scope risks?

Yes — four, all already identified and tracked in the existing corpus, none new to this review.
Carrying them forward explicitly here so feature decomposition inherits them as known constraints
rather than rediscovering them mid-implementation:

1. **AI-Red epistemic parity is an accepted, not resolved, trade-off** (ADR-0024; FR-9110 Notes;
   CNFR-06 added per `requirements-change-log.md` CHG-010). Any feature that touches AI-Red's
   behavior or fairness perception should re-read ADR-0024 before assuming ground-truth read access
   is incidental rather than load-bearing.
2. **LAN concurrency ceiling (~16 participants) is a documented estimate, never load-tested**
   (ADR-0026; NFR-1400). A feature that scales multiplayer further (more pop-outs, more cells, a
   larger vignette) should treat this as an open risk to re-validate, not a settled number.
3. **Push-vs-poll is an unstated default, not a requirement** (ICD §7 issue 11; `requirements-review.md`
   REQ-012, explicitly left unactioned in `requirements-change-log.md`'s "deliberately left
   unactioned" list as optional/low-priority). The entire FR-6xxx session/multiplayer cluster
   assumes polling without any NFR stating why. Low risk today; becomes a real scope risk the moment
   a future feature needs lower-latency updates (e.g. a faster AAR scrub or live coaching overlay),
   since switching to push later is an architecture change, not a tuning change.
4. **OR-6 / multi-session tension (REQ-021/060, OQ2)** — if "v1 runs a single exercise per process
   instance" is actually stale post-P8, any feature decomposition that assumes single-session
   semantics (e.g. a global, not per-session, configuration surface) risks building against the
   wrong invariant. This is the one item this review recommends resolving *before*, not during,
   decomposition of anything touching session/multiplayer scope — see Recommendation 1.

No scope risk found here is a reason to halt; all four are bounded, already named, and three of the
four are already tracked in `FUTURE-WORK.md` or an `Accepted` ADR. The fourth (OR-6 wording) is a
five-minute confirmation, not a redesign.

---

## Recommendations (non-blocking, to close before or during early decomposition)

1. **Resolve OQ2 / REQ-021 directly with the project owner**: is `build-spec/02`'s OR-6 wording
   stale post-P8, or does "single exercise per process" mean something that already coexists with
   `/api/sessions`'s multi-session discovery (e.g., "single *active* exercise per facilitator
   workflow," not "the process can only ever hold one `Session` object")? One sentence either way
   closes both GDS-05 OQ2 and `requirements/02`'s mirrored open issue.
2. Add the one-sentence `CLAUDE.md` clarification REQ-020 recommends (`docs/requirements/` is a
   sibling elaboration, not part of the superseded `build-spec/` set) — cosmetic, prevents a future
   reader from misreading the supersession scope.
3. Update GDS-05's own OQ1 text to point at the now-existing FR-6610 leaf, closing the residual
   sync gap left by `requirements-change-log.md` CHG-004.
4. As feature decomposition reaches the session/multiplayer and AI-Red clusters specifically,
   re-read ADR-0024 and ADR-0026 first — those two carry the highest-consequence accepted trade-offs
   in the baseline.

None of these block starting decomposition on other clusters (engine core, orbital propagation,
five-D effects, bus/payload, scenario content) today.

---

## Gate decision

**APPROVED FOR FEATURE DECOMPOSITION**

Reasons:
- Architecture (GDS-00–05) is authored, merge-gated, and free of Critical or unresolved-contradiction
  findings; every escalated open item from `architecture-review.md` either closed via an `Accepted`
  ADR (six of eight) or remains a narrow, explicitly-tracked Open Question that doesn't block other
  clusters.
- Interfaces are defined at the component-boundary grain needed to decompose into features; the
  wire-level gap (GDS-09 not yet authored) is disclosed and is correctly deferred to per-feature
  work rather than required up front.
- Requirements are written testably, with justified verification methods throughout and only two
  honestly-disclosed qualitative (not numeric) NFRs — a defect of missing source data, not of
  authoring discipline.
- No Critical-severity issue exists anywhere in the reviewed corpus; the one remaining High-severity
  open item with real substance (OR-6 vs. multi-session) is a single confirming sentence away from
  closed and does not touch the clusters most likely to be decomposed first.
- Scope risks are bounded, already named, and tracked in `FUTURE-WORK.md`/ADRs rather than being
  newly discovered here.

This approval does not certify GDS-06–GDS-10 as complete (they remain scaffold-only) or the ICD as
wire-level-complete — it certifies that the baseline is **stable and traceable enough that feature
decomposition can begin without rework risk from the architecture or requirements layers
underneath it**, carrying forward the four recommendations above as tracked, non-blocking follow-up.

## Related

[`docs/reviews/architecture-review.md`](architecture-review.md) ·
[`docs/reviews/architecture-review-changelog.md`](architecture-review-changelog.md) ·
[`docs/reviews/requirements-review.md`](requirements-review.md) ·
[`docs/requirements/requirements-change-log.md`](../requirements/requirements-change-log.md) ·
[`docs/requirements/01-functional-requirements.md`](../requirements/01-functional-requirements.md) ·
[`docs/requirements/02-non-functional-requirements.md`](../requirements/02-non-functional-requirements.md) ·
[`docs/requirements/03-requirements-traceability-matrix.md`](../requirements/03-requirements-traceability-matrix.md) ·
[`docs/design/05-interface-control-document.md`](../design/05-interface-control-document.md) ·
[`docs/architecture/adr/INDEX.md`](../architecture/adr/INDEX.md) ·
[`docs/architecture/INDEX.md`](../architecture/INDEX.md) ·
[`docs/FUTURE-WORK.md`](../FUTURE-WORK.md)
