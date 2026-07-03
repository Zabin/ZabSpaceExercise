# IP-2010 — Competency Assessment: Rubric Computation

> **Package ID:** IP-2010
> **Version:** 1.0
> **Status:** 🟡 READY *(authorized, not yet started — unblocked 2026-07-02: the blocking conflict — this
> package's Objective building exactly the automated-assessment mechanism ADR-0017 read as
> prohibiting — is resolved by [ADR-0032](../../architecture/adr/ADR-0032-descriptive-rubric-not-automated-scoring.md),
> which carves out non-adjudicative, descriptive, non-aggregating rubric-tier reporting from
> ADR-0017's "assessment mechanism" prohibition; the underlying capability is now also baselined as
> [`FR-10110`](../../requirements/01-functional-requirements.md). **MSTR-006 §3 authorization
> obtained 2026-07-03** (project owner, recorded in `docs/pipeline/pipeline-journal.md` run #2) —
> this is the fresh, separate go-ahead the prior 2026-07-02 approval could not itself constitute
> since it was interrupted by the (now-resolved) ADR-0017 conflict before any code was written.
> `08-code-implementation` may now pick up this package. Design/spec text below is otherwise
> unchanged from v1.0.)*
> **Dependencies:** FS-201, IP-1030 (custody data source), IP-1020/IP-1010 (window-discipline data
> source), IP-1070 (belief-truth-divergence data source)
> **Referenced By:** IP-3010 (the forward-design export package that would aggregate this package's
> output), [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** the per-cell/per-exercise rubric output IP-3010 would aggregate across runs
> **Feature Reference:** [FS-201 — Competency Assessment](../../features/FS-201-competency-assessment.md)
> **Supersedes:** [`docs/implementations/IMP-201A-competency-assessment.md`](../../implementations/IMP-201A-competency-assessment.md)
> **Related Topics:** [`spacesim/engine/custody.py`](../../../spacesim/engine/custody.py), [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py), [`spacesim/session/aar.py`](../../../spacesim/session/aar.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

## Package ID

IP-2010

## Title

Competency Assessment — Rubric Computation

## Objective

Replace the engine's current binary objective-flip success/failure signal with a richer,
rubric-tier measurement of *how* a cell demonstrated the competency a vignette was designed to
exercise, across the three first-iteration dimensions FS-201 §3 scopes as derivable from data the
engine already unambiguously produces: **custody quality**, **window discipline**, and
**belief-truth divergence**. No composite single score is produced.

> **This is a forward-design package: the capability described here does not exist in `spacesim/`
> today.** Per MSTR-006 §3, this document's own specification was not itself an authorization to
> write code — that separate, explicit user go-ahead was obtained 2026-07-03 (see the Status field
> above), and `08-code-implementation` may now begin the tasks below.

## Feature Reference

[FS-201 — Competency Assessment](../../features/FS-201-competency-assessment.md)

## Requirements Covered

**FR-10110** (automated non-aggregating competency rubric-tier computation, added 2026-07) is now
the primary requirement this package implements — see `docs/features/FS-201-competency-
assessment.md`'s own updated "Requirements Implemented" field. This package's proposed module also
reads from, and inherits the requirement obligations of, three upstream packages' already-covered
requirements, restated here as the *data-source* requirements this design depends on:

| Req ID | Title (abridged) | Relevance to this package's design |
|---|---|---|
| FR-10110 | Automated non-aggregating competency rubric-tier computation | The requirement this package implements in full |
| FR-1510 | Track confidence decay and reset | Source data for the custody-quality dimension (`Track.current_confidence()`) |
| FR-1520 | Weapons-quality track gate | Source data for the custody-quality dimension (`is_weapons_quality()`) |
| FR-3410 | Execute-time re-validation (rejection reasons) | Source data for the window-discipline dimension (`dry_run()`/`issue()` `(bool, str)` returns) |
| FR-7310 | AAR replay/scrub | Source data for the belief-truth-divergence dimension (`aar.state_at()`) |
| FR-4710 | No automated score/win-loss determination | The sibling prohibition this package's design must not cross (per ADR-0032's narrow carve-out) |
| NFR-1500 | Determinism (engine-wide) | This package's scoring functions must remain pure/read-only to avoid violating it |

## Architecture Components

- **C1 Simulation Engine** — read-only consumer of `engine/custody.py`, `engine/orders.py`'s
  eventlog-recorded rejection reasons.
- **C2 Session / Application Layer** — the proposed new module would live alongside `session/aar.py`
  as a sibling read-only analytics module; report surface hosted as an extension of IP-1060's White
  Cell Dashboard (`FS-106`).

## Interfaces

FS-201's "Interfaces Used" field states no ICD interface ID is cited, and "Related Interfaces"
confirms none exists for this boundary — an open Phase 8 item. This package does not propose a new
`INT-xxxx` interface; it proposes an internal module (`session/assessment.py`, see below) consumed
by the existing **INT-0002** (White Cell Facilitator ↔ Operator Console) surface IP-1060 already
implements, without crossing any new named boundary.

## Files to Create

- `spacesim/session/assessment.py` *(new)* — the proposed read-only scoring module, analogous in
  spirit to `session/aar.py`: pure functions over replayed/eventlog state, no `WorldState`
  mutation, per FS-201 §"No new gameplay mechanic."

## Files to Modify

- `spacesim/session/inprocess.py` *(proposed)* — add thin wrapper functions
  (`assessment_report(session, cell)` or similar) mirroring the existing `aar_report`/
  `aar_snapshot_at` wrapper pattern (`inprocess.py:742-750`), so the new module is reachable the
  same way AAR is.
- `spacesim/ui_web/server.py` / `spacesim/ui_web/static/app.js` *(proposed, White Cell Dashboard
  extension)* — a new report panel/endpoint hosted within IP-1060's existing facilitator surface;
  no new authority tier, per FS-106's stated additive-only constraint.

## Implementation Tasks

**Not started — authorized (MSTR-006 §3, 2026-07-03).** The following is the proposed task
sequence for `08-code-implementation`:

1. Implement `score_custody_quality(mgr, cell) -> Literal["speculative", "adequate", "disciplined"]`
   — sample `Track.current_confidence()` at the moments the cell actually acted on a track (each
   `engage`/`observe` order's issue time, via the eventlog), not at arbitrary intervals.
2. Implement `score_window_discipline(mgr, cell) -> Literal["frequent-invalid-attempts",
   "occasional", "disciplined"]` — count `dry_run()`/`issue()` rejection attempts against successful
   issuances across the exercise.
3. Implement `score_belief_truth_divergence(mgr, cell) -> Literal["high-divergence-unaware",
   "high-divergence-aware", "low-divergence"]` — at each `aar.report()` `DECISION_KINDS` timeline
   point, compare the cell's `build_scene()` belief against ground truth at that `seq`.
4. Implement the per-cell/per-exercise report surface as an additive extension of IP-1060's White
   Cell Dashboard, presenting all three tiers side-by-side per cell — never collapsed into a
   composite number (FS-201 §6's explicit non-goal).
5. **Explicitly do not implement** in this package: the two deferred dimensions (resource economy,
   escalation discipline — need a vignette-schema resource/ROE budget baseline that does not exist)
   or time-to-decision (needs an OODA-tightness reference baseline per
   [R208](../../research/encyclopedia/R208-ooda-loops.md)); and do not implement longitudinal
   per-trainee persistence (no trainee-identity/cross-session model exists in `spacesim/` today —
   flagged as a dependency for a future IP-2011 or similar, not designed here).
6. **Explicitly resolve before implementation begins** (open design question, not yet answered):
   what signal distinguishes "aware" from "unaware" high divergence for the belief-truth-divergence
   tier — not derivable from `aar.py` alone as currently built.

## Tests to Add

*(Proposed — none exist yet; write test-first per `CLAUDE.md`'s mandatory workflow once authorized.)*

- `spacesim/tests/test_assessment.py` *(new)* — one test per scoring function's tier boundaries
  (e.g., a fixture exercise where a cell's known custody-confidence history should score
  `disciplined` vs. `speculative`), plus a dedicated test asserting each scoring function produces
  zero `WorldState` mutation (replay-safety, mirroring the pattern already used for `dry_run()`,
  `scene.py`, and `aar.py`).
- An addition to `spacesim/tests/test_determinism.py`'s scope (or a parallel property test)
  asserting the scoring module never introduces replay divergence.

## Documentation Updates

- Supersedes [`docs/implementations/IMP-201A-competency-assessment.md`](../../implementations/IMP-201A-competency-assessment.md).
- `ROADMAP.md` Implementation Packages theme updated.
- `CLAUDE.md`'s Code Map should gain a `spacesim/session/assessment.py` entry once implemented (not
  added by this package, which contains no code changes).

## Definition of Done

*(Forward-looking gate — the authorization item below is now true; the rest is not yet.)*

- [x] **Explicit user authorization obtained** for this package's Implementation Tasks, per
  MSTR-006 §3 (2026-07-03, project owner, recorded in `docs/pipeline/pipeline-journal.md` run #2).
- [ ] `score_custody_quality`/`score_window_discipline`/`score_belief_truth_divergence` each return
  one of FS-201 §3's named tiers, never a numeric average.
- [ ] The per-cell/per-exercise report presents all three dimensions side-by-side without collapsing
  to a composite number.
- [ ] Deferred dimensions (resource economy, escalation discipline, time-to-decision) are absent
  from the report, not substituted with a default.
- [ ] Every scoring function is verified read-only (no `WorldState` mutation) by a dedicated test.
- [ ] Each reported dimension's report surface discloses that it has not undergone a DOM-005 §5
  validity check beyond face validity (per FS-201's Validation Discipline requirement) — the report
  must not imply a validated metric.

## Verification Checklist

*(To be executed once implemented; not yet applicable.)*

- [ ] `spacesim/tests/test_assessment.py` exists and is green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green after this module lands.
- [ ] Manual review confirms no scoring function calls any `WorldState`-mutating engine handler.
- [ ] FS-201's Acceptance Criteria (§"Acceptance Criteria" in the Feature Spec) are each traceable to
  a specific test in `test_assessment.py`.

## Dependencies

- **Upstream:** IP-1030 (custody data source, already shipped), IP-1010/IP-1020 (window-discipline
  rejection data, already shipped), IP-1070 (belief-truth-divergence mechanism, already shipped) —
  all three upstream dependencies are satisfied; this package's design is blocked on nothing except
  authorization.
- **Downstream:** IP-3010 (Research Analytics) cannot be implemented in more than provisional detail
  until this package's `RunRecord`-equivalent output shape is not just designed (already done, §
  "Proposed shape" above) but actually implemented — IP-3010 is accordingly `BLOCKED` on this
  package reaching `COMPLETE`, not merely `READY`.
- **Build-sequencing:** This package is the critical-path predecessor to IP-3010 in the Master Build
  Plan's dependency graph.

## Risks

- **Authorization risk (resolved 2026-07-03):** this package was implemented-eligible only once an
  explicit, separate user go-ahead was recorded (MSTR-006 §3) — this document's own specification
  never constituted that authorization by itself; the go-ahead is now on record in the pipeline
  journal.
- The "aware vs. unaware" divergence signal (§"Implementation Tasks" item 6) is an unresolved design
  question; implementing a plausible-but-unvalidated heuristic without flagging it as such would
  misrepresent an unvalidated metric as settled.
- Deferred dimensions (resource economy, escalation discipline, time-to-decision) each require
  baseline data structures that do not yet exist; a future author adding them without their required
  baselines would produce a metric that cannot be meaningfully scored.
- Any implementation that mutates `WorldState` (even "temporarily") during scoring would violate the
  replay-safety invariant this entire design depends on.

## Rollback Considerations

Since this package proposes wholly new files (`session/assessment.py` plus additive wrapper/panel
code), rollback is low-complexity relative to the as-built packages: removing the new module and its
wrapper functions/panel fully reverts this capability with no data-migration concern, because no
other shipped capability would depend on it (IP-3010 is the only planned downstream consumer, and it
cannot exist before this package ships). No existing test, save-file schema, or eventlog format is
touched by this package's proposed design.
