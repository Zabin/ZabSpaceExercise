# IP-2010 — Competency Assessment: Rubric Computation

> **Package ID:** IP-2010
> **Version:** 1.2 (2026-07-03 — implemented by `08-code-implementation`; see Status below. v1.1
> resolved BL-0002, the "aware vs. unaware" divergence-signal design question, per the project
> owner's decision recorded in `docs/pipeline/pipeline-journal.md` run #4; see "Files to Modify,"
> Implementation Tasks items 3/6, Tests to Add, Definition of Done, Verification Checklist, and
> Risks below.)
> **Status:** ✅ VERIFIED *(2026-07-04, [`VR-2010`](../verification/VR-2010-competency-assessment.md)
> — every Definition of Done/Verification Checklist item this package itself claims confirmed
> against the live tree; full suite green (566 passed/3 skipped), both permanent gates green; RTM
> `FR-10110` cell updated. **Two Medium findings filed against FS-201 itself, not against this
> package's honesty**: FS-201's own Acceptance Criteria include a longitudinal per-trainee report
> (explicitly, knowingly deferred by this package's own Implementation Tasks item 5 — not a
> surprise) and self-assessment/debrief-mode accessibility (not implemented, and not flagged
> anywhere in this package's text as excluded — genuinely missed at authoring time). See `VR-2010`'s
> Findings for the full reasoning and recommended routing. Was 🔵 COMPLETE *(implemented
> 2026-07-03 — `session/assessment.py` (new),
> `custody_confidence_at_decision` capture in `engine/orders.py`'s `_exec_payload()` via a new
> `engine/custody.py` helper, `session/inprocess.py` wrapper, `/api/sessions/{sid}/assessment`
> endpoint + White Cell Dashboard panel. Full suite green (507 passed/3 skipped, up from 490/3 —
> 17 new tests), both permanent gates (`test_determinism.py`, `test_import_guard.py`) green.
> Entered `COMPLETE`, not `VERIFIED` — per this skill's rule, only `09-package-verification`'s own
> independent pass may write `VERIFIED`.)* Was 🟡 READY *(authorized, unblocked 2026-07-02 — the
> blocking conflict, this package's Objective building exactly the automated-assessment mechanism
> ADR-0017 read as prohibiting, is resolved by
> [ADR-0032](../../architecture/adr/ADR-0032-descriptive-rubric-not-automated-scoring.md), which
> carves out non-adjudicative, descriptive, non-aggregating rubric-tier reporting from ADR-0017's
> "assessment mechanism" prohibition; the underlying capability is baselined as
> [`FR-10110`](../../requirements/01-functional-requirements.md). **MSTR-006 §3 authorization
> obtained 2026-07-03** (project owner, recorded in `docs/pipeline/pipeline-journal.md` run #2).)*)*
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

> **This was authored as a forward-design package: the capability did not exist in `spacesim/` at
> authoring time.** Per MSTR-006 §3, this document's own specification was not itself an
> authorization to write code — that separate, explicit user go-ahead was obtained 2026-07-03 (see
> the Status field above), and `08-code-implementation` has since implemented the tasks below
> (2026-07-03, see Status).

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
  eventlog-recorded rejection reasons. **Amended 2026-07-03** (resolving BL-0002, see Implementation
  Tasks item 6 below): `engine/custody.py` gains one new pure helper and `engine/orders.py`'s
  `_exec_payload()` gains one new deterministic capture step, so this package is no longer a *pure*
  consumer of the engine — it adds a small, read-only, non-mutating recording step to the existing
  order-issue pipeline. This remains within C1's existing invariants (no `WorldState` mutation, no
  RNG, replay-safe) — it is the same class of change as the effect `success_prob` values `_exec_payload`
  already computes and embeds into the same event payloads.
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

- `spacesim/engine/custody.py` *(amended 2026-07-03, resolving BL-0002)* — add one new pure helper,
  e.g. `confidence_at_decision(world, cell, target, now) -> Optional[float]`: looks up
  `world.track_for(cell, target)` (the same lookup `orders.py`'s engage-gate already uses,
  `orders.py:348`) and returns `track.current_confidence(now)` rounded to 3 dp, or `None` if the
  cell holds no track on `target`. Pure read, no state, no RNG — same purity class as
  `Track.current_confidence`/`is_weapons_quality` it wraps.
- `spacesim/engine/orders.py` *(amended 2026-07-03, resolving BL-0002)* — `_exec_payload()`
  (`orders.py:394`) calls the new helper once, at the top, using `order.target` and `order.issued_at`
  (the sim-time the operator actually clicked Issue, already stored on every `Order` — not the later
  window-open execution time), and merges the result into every returned payload dict under a new key
  `custody_confidence_at_decision`. `None` when the order has no target or the cell holds no track on
  it (e.g. `downlink`, most `command` verbs). `dry_run()` never reaches `_exec_payload` (only
  `commit=True` does, per `_plan`'s existing branch), so this adds nothing to the non-mutating
  preview path and does not touch its replay-safety guarantee.
- `spacesim/session/inprocess.py` *(proposed)* — add thin wrapper functions
  (`assessment_report(session, cell)` or similar) mirroring the existing `aar_report`/
  `aar_snapshot_at` wrapper pattern (`inprocess.py:742-750`), so the new module is reachable the
  same way AAR is.
- `spacesim/ui_web/server.py` / `spacesim/ui_web/static/app.js` *(proposed, White Cell Dashboard
  extension)* — a new report panel/endpoint hosted within IP-1060's existing facilitator surface;
  no new authority tier, per FS-106's stated additive-only constraint.

**Cross-package note:** `engine/custody.py` and `engine/orders.py` are also cited by the already-
`VERIFIED` `IP-1030` and `IP-1020`/`IP-1010`/`IP-1051`. This amendment is strictly additive — a new
helper function and a new payload key appended to existing dicts — and changes no existing field,
signature, or behavior those packages document, so it does not reopen their `VERIFIED` status. State
this explicitly in `09-package-verification`'s pass on this package: confirm no existing
`_exec_payload` return field or `custody.py` public signature changed shape.

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
   point **whose eventlog payload carries a non-`None` `custody_confidence_at_decision`** (item 6
   below — i.e. only decisions the cell actually took against a tracked target), compare the cell's
   `build_scene()` belief against ground truth at that `seq` to classify low vs. high divergence;
   for high-divergence points, split `-aware`/`-unaware` using the recorded
   `custody_confidence_at_decision` value against `WEAPONS_QUALITY_THRESHOLD` (`custody.py`, 0.8) —
   below it is `-aware` (the confidence number the operator's live track table/dry-run preview
   displayed at the moment of decision was already visibly marginal, and the cell acted anyway);
   at/above it is `-unaware` (nothing in the operator-visible display suggested staleness, so the
   divergence was not something the interface gave the cell a chance to notice). **The scorer reads
   the recorded field only — it never recomputes confidence via `aar.state_at()`/replay for this
   classification**, which is the whole point of item 6's resolution below (an explicit,
   decision-time-captured signal, not a post-hoc reconstruction).
4. Implement the per-cell/per-exercise report surface as an additive extension of IP-1060's White
   Cell Dashboard, presenting all three tiers side-by-side per cell — never collapsed into a
   composite number (FS-201 §6's explicit non-goal).
5. **Explicitly do not implement** in this package: the two deferred dimensions (resource economy,
   escalation discipline — need a vignette-schema resource/ROE budget baseline that does not exist)
   or time-to-decision (needs an OODA-tightness reference baseline per
   [R208](../../research/encyclopedia/R208-ooda-loops.md)); and do not implement longitudinal
   per-trainee persistence (no trainee-identity/cross-session model exists in `spacesim/` today —
   flagged as a dependency for a future IP-2011 or similar, not designed here).
6. **Resolved 2026-07-03** (was an open design question, put to the project owner as backlog item
   `BL-0002` and answered via the pipeline manager's gate check — see
   `docs/pipeline/pipeline-journal.md` run #4): the "aware vs. unaware" signal is **instrumented
   explicitly at decision time**, not reconstructed post-hoc. Add `custody_confidence_at_decision`
   to every targeted `DECISION_KINDS` event's payload (`engine/orders.py`'s `_exec_payload()`,
   `engine/custody.py`'s new `confidence_at_decision()` helper — see "Files to Modify" above) —
   the same confidence number `scene.py`'s `RenderTrack.confidence` already surfaces live to the
   operator (`app.js`'s track table, per `CLAUDE.md`'s Code Map), captured at the sim-time the
   order was actually issued. This reuses the existing, already-calibrated
   `WEAPONS_QUALITY_THRESHOLD` as the "visibly marginal" band rather than inventing a new number —
   see Risks below for the one caveat this still carries.

## Tests to Add

*(Proposed — none exist yet; write test-first per `CLAUDE.md`'s mandatory workflow once authorized.)*

- `spacesim/tests/test_assessment.py` *(new)* — one test per scoring function's tier boundaries
  (e.g., a fixture exercise where a cell's known custody-confidence history should score
  `disciplined` vs. `speculative`), plus a dedicated test asserting each scoring function produces
  zero `WorldState` mutation (replay-safety, mirroring the pattern already used for `dry_run()`,
  `scene.py`, and `aar.py`). Additionally, for the belief-truth-divergence tier specifically:
  - a fixture asserting `score_belief_truth_divergence`'s aware/unaware split reads
    `custody_confidence_at_decision` from the eventlog payload and does **not** recompute it —
    constructed so that recomputing confidence post-hoc via `aar.state_at()` at the same `seq`
    would give a *different* value than what was captured at issue time (e.g. the track decayed
    further between issue and a later replay-inspection point), proving the scorer is reading the
    stored decision-time value, not reconstructing one.
- `spacesim/tests/test_orders.py` *(amended)* — assert `_exec_payload()` populates
  `custody_confidence_at_decision` on every `DECISION_KINDS`-producing action with a target the
  cell holds a track on, matching `Track.current_confidence()` sampled at `order.issued_at`; assert
  it is `None` for actions with no target or no owned track (e.g. `downlink`); assert `dry_run()`
  never invokes the new helper (still zero eventlog/registry/booking writes).
- An addition to `spacesim/tests/test_determinism.py`'s scope (or a parallel property test)
  asserting the scoring module never introduces replay divergence, and that
  `custody_confidence_at_decision` replays byte-identically (it is a pure read of deterministic
  `WorldState`, no RNG, so this should already hold — the test makes it a permanent regression
  guard rather than an assumption).

## Documentation Updates

- Supersedes [`docs/implementations/IMP-201A-competency-assessment.md`](../../implementations/IMP-201A-competency-assessment.md).
- `ROADMAP.md` Implementation Packages theme updated.
- `CLAUDE.md`'s Code Map should gain a `spacesim/session/assessment.py` entry once implemented (not
  added by this package, which contains no code changes).

## Definition of Done

*(Implemented 2026-07-03 by `08-code-implementation` — every item below is now satisfied against
the shipped code and tests; `09-package-verification` independently re-confirms this, per its own
process, before the package may advance to `VERIFIED`.)*

- [x] **Explicit user authorization obtained** for this package's Implementation Tasks, per
  MSTR-006 §3 (2026-07-03, project owner, recorded in `docs/pipeline/pipeline-journal.md` run #2).
- [x] `score_custody_quality`/`score_window_discipline`/`score_belief_truth_divergence` each return
  one of FS-201 §3's named tiers, never a numeric average.
- [x] The per-cell/per-exercise report presents all three dimensions side-by-side without collapsing
  to a composite number.
- [x] Deferred dimensions (resource economy, escalation discipline, time-to-decision) are absent
  from the report, not substituted with a default.
- [x] Every scoring function is verified read-only (no `WorldState` mutation) by a dedicated test.
- [x] Each reported dimension's report surface discloses that it has not undergone a DOM-005 §5
  validity check beyond face validity (per FS-201's Validation Discipline requirement) — the report
  must not imply a validated metric.
- [x] `custody_confidence_at_decision` is populated on every `DECISION_KINDS` event whose order had
  a target the issuing cell held a track on, and is `None` on every event without one, verified by a
  dedicated test in `test_orders.py`.
- [x] `score_belief_truth_divergence`'s aware/unaware split reads the recorded
  `custody_confidence_at_decision` field only — never recomputes confidence via
  `aar.state_at()`/replay for this classification (the differentiating fixture in
  `test_assessment.py` proves this).

## Verification Checklist

*(Executed 2026-07-04 by `09-package-verification` —
[`VR-2010`](../verification/VR-2010-competency-assessment.md).)*

- [x] `spacesim/tests/test_assessment.py` exists and is green — 13 tests.
- [x] `python3 -m pytest spacesim/tests/test_determinism.py` remains green after this module lands.
- [x] Manual review confirms no scoring function calls any `WorldState`-mutating engine handler.
- [~] FS-201's Acceptance Criteria (§"Acceptance Criteria" in the Feature Spec) are each traceable to
  a specific test in `test_assessment.py`. **4 of 6 are; 2 are not** — the longitudinal per-trainee
  report (already disclosed as out of scope by this package's own Implementation Tasks item 5) and
  self-assessment/debrief-mode accessibility (not disclosed as excluded anywhere in this package —
  see `VR-2010` Findings #1/#2). Filed as Medium findings against FS-201's scope, not against this
  package's own honesty.
- [x] `spacesim/tests/test_orders.py`'s new `custody_confidence_at_decision` assertions are green,
  and confirm no existing `_exec_payload()` return field or `custody.py` public signature changed
  shape (the "Cross-package note" in Files to Modify above — `IP-1030`/`IP-1020`/`IP-1010`/`IP-1051`
  remain correctly `VERIFIED`, no re-verification needed).
- [x] Manual confirmation that `dry_run()` still performs zero eventlog/registry/booking writes
  (the new helper is only reachable from `issue()`'s `commit=True` path) —
  `test_dry_run_never_captures_custody_confidence` confirms this directly.

## Dependencies

- **Upstream:** IP-1030 (custody data source, already shipped), IP-1010/IP-1020 (window-discipline
  rejection data, already shipped), IP-1070 (belief-truth-divergence mechanism, already shipped) —
  all three upstream dependencies are satisfied; this package's design is blocked on nothing except
  authorization.
- **Downstream:** IP-3010 (Research Analytics) was implemented (2026-07-04, run #10) against this
  package's `assessment_report` output shape while this package was `COMPLETE`, not yet `VERIFIED`
  — `VR-2010` confirmed the shape is unchanged, resolving `BL-0018` cleanly with no impact on
  `IP-3010`'s already-shipped `RunRecord` schema.
- **Build-sequencing:** This package was the critical-path predecessor to IP-3010 in the Master
  Build Plan's dependency graph; both are now implemented.

## Risks

- **Authorization risk (resolved 2026-07-03):** this package was implemented-eligible only once an
  explicit, separate user go-ahead was recorded (MSTR-006 §3) — this document's own specification
  never constituted that authorization by itself; the go-ahead is now on record in the pipeline
  journal.
- **The "aware vs. unaware" divergence signal (§"Implementation Tasks" item 6) is resolved, but
  carries one residual disclosure obligation, not a design gap:** `WEAPONS_QUALITY_THRESHOLD` (0.8)
  was calibrated as the engage hard-gate boundary (FR-1520), not validated as a perceptual/awareness
  boundary for every action type this scorer now covers (jam/observe/maneuver targets are not
  gated by it the way engage is). Reusing it as the "operator-visibly-marginal" band is a reasonable,
  non-arbitrary choice — it is the one number already displayed and already meaningful to operators —
  but it is still a design choice, not a measured fact, and the report's DOM-005 §5 face-validity
  disclosure (Definition of Done, above) must say so explicitly rather than presenting the
  aware/unaware split as validated.
- Modifying `engine/custody.py`/`engine/orders.py` — files two already-`VERIFIED` packages
  (`IP-1030`, `IP-1020`/`IP-1010`/`IP-1051`) document — creates a small cross-package-boundary risk:
  if a future edit to this new capture step ever changes an *existing* field's shape (not just adds
  the new one), those packages' `VERIFIED` status would be stale without anyone re-running
  `09-package-verification` on them. Mitigated by keeping this change strictly additive (new
  function, new payload key, no existing signature touched) and by the Verification Checklist item
  above that makes this an explicit, checked claim rather than an assumption.
- Deferred dimensions (resource economy, escalation discipline, time-to-decision) each require
  baseline data structures that do not yet exist; a future author adding them without their required
  baselines would produce a metric that cannot be meaningfully scored.
- Any implementation that mutates `WorldState` (even "temporarily") during scoring would violate the
  replay-safety invariant this entire design depends on.
- **New findings (2026-07-04, `VR-2010`):** FS-201's own Acceptance Criteria are broader than what
  this package built. (1) A longitudinal per-trainee report across exercises is entirely
  unimplemented — already disclosed by this package's Implementation Tasks item 5, so not a
  surprise, but worth recording that FS-201 itself (marked `✅ Done`) has an unimplemented
  Acceptance Criterion. (2) Self-assessment/debrief-mode accessibility (Blue/Red operators viewing
  their own rubric) is not implemented — the shipped panel is White-Cell-only (`index.html`'s
  `white-only` CSS class) — and, unlike (1), this exclusion was never flagged anywhere in this
  package's own text. Routed to `06-feature-specification` to reconcile FS-201's Acceptance
  Criteria against what was actually built.

## Rollback Considerations

Rollback is still low-complexity, but the 2026-07-03 amendment (v1.1) touches two existing engine
files, not only new ones — rollback now has two parts: (1) removing the new
`session/assessment.py` module and its wrapper functions/panel fully reverts the reporting
capability with no data-migration concern, since no other shipped capability depends on it (IP-3010
is the only planned downstream consumer, and it cannot exist before this package ships); (2)
removing the `custody_confidence_at_decision` capture from `engine/custody.py`/`engine/orders.py`
is also low-risk to revert — it is an additive payload key on eventlog entries, not a schema
migration, so old saves/eventlogs replay identically whether or not the key is present (readers must
already tolerate its absence via `.get(...)`/`Optional`, since it is `None`-valued on most existing
action types). No existing test, save-file schema, or previously-defined eventlog field is changed
by this package's design — only a new, optional field is added.
