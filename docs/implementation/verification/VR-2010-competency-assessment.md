# VR-2010 — Verification Report: Competency Assessment — Rubric Computation

> **Document ID:** VR-2010
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-2010](../packages/IP-2010-competency-assessment.md), [FS-201](../../features/FS-201-competency-assessment.md)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition for IP-2010; the adjudication of `BL-0007`; the resolution of `BL-0018`
> **Feature Mapping:** FS-201
> **Related Topics:** [`spacesim/session/assessment.py`](../../../spacesim/session/assessment.py), [`spacesim/engine/custody.py`](../../../spacesim/engine/custody.py), [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-2010 — Competency Assessment: Rubric Computation (FS-201)
- **Version verified:** 1.2
- **Tree state verified:** commit `e7a098a084fa42c77cd80d856fbc7ed668abe689` (branch `claude/pipeline-skill-ijwd1f`)
- **Independence:** this package was implemented in an earlier session turn of the same overall
  conversation (run #5, several runs and a compaction boundary before this verification). No code
  was written this run before this pass began; every claim below was re-derived from the tree by
  reading the actual source, not by trusting the Implementation Summary. Proceeding without a
  fresh-session caveat, consistent with this project's convention of accepting reduced
  same-conversation independence when the implementation happened many runs earlier (cf. `VR-1150`).

## Result

**VERIFIED** — every Definition of Done and Verification Checklist item this package itself claims
is confirmed; full suite green; both permanent gates green; requirements traceability corrected.
Two Medium findings are filed against **FS-201's own Acceptance Criteria being broader than what
IP-2010 built** (not against IP-2010's honesty — it never claimed to satisfy either) — see
Findings. `BL-0007` is adjudicated (the `index.html` scope inclusion was appropriate). `BL-0018` is
resolved: nothing found here requires any change to `IP-3010`'s already-shipped `RunRecord` schema.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Explicit user authorization obtained (MSTR-006 §3). | `docs/pipeline/pipeline-journal.md` run #2. | ✅ Pass |
| Each scoring function returns one of FS-201 §3's named tiers, never a numeric average. | `assessment.py:27-29` — `CustodyTier`/`WindowTier`/`DivergenceTier` are `Literal[...]` string types; `score_custody_quality`/`score_window_discipline`/`score_belief_truth_divergence` (lines 50-161) each return only these literal strings. `test_assessment_report_presents_dimensions_side_by_side_never_a_composite` asserts `not isinstance(cell_report["custody_quality"], (int, float))`. | ✅ Pass |
| The per-cell/per-exercise report presents all three dimensions side-by-side without collapsing to a composite. | `assessment_report(mgr)` (`assessment.py:164-175`) returns `{cell: {custody_quality, window_discipline, belief_truth_divergence, disclosure}}` for `cell in ("blue","red")` — no aggregate field. Confirmed by `test_assessment_report_presents_dimensions_side_by_side_never_a_composite`. | ✅ Pass |
| Deferred dimensions (resource economy, escalation discipline, time-to-decision) are absent, not defaulted. | Same test asserts `"resource_economy" not in cell_report`, etc. `assessment.py`'s module docstring states this explicitly. | ✅ Pass |
| Every scoring function is verified read-only (no `WorldState` mutation) by a dedicated test. | `test_scoring_functions_never_mutate_world_state` — calls all three scorers + `assessment_report`, asserts `model_dump_json()` unchanged before/after. | ✅ Pass |
| Each reported dimension discloses no DOM-005 §5 validity check beyond face validity. | `assessment.py:37-41`'s `DISCLOSURE` constant, embedded verbatim in every `assessment_report` cell dict (`"disclosure": DISCLOSURE`). | ✅ Pass |
| `custody_confidence_at_decision` populated on every targeted `DECISION_KINDS` event, `None` otherwise. | `orders.py:408-410` (`_exec_payload`) calls `confidence_at_decision(self.world.tracks, order.cell, order.target, order.issued_at)` once, merges into every returned payload dict (lines 457, 500, 568, 582, 588, 597). `test_custody_confidence_at_decision_captured_for_targeted_actions` and `test_custody_confidence_at_decision_none_without_target_or_track` confirm both branches. | ✅ Pass |
| `score_belief_truth_divergence`'s aware/unaware split reads the recorded field only, never recomputes via replay. | `assessment.py:136-161` reads `e.payload.get("custody_confidence_at_decision")` directly from the eventlog entry, never calls `aar.state_at()`/`current_confidence()` for the aware/unaware classification itself (only for the belief-vs-truth position comparison, a separate concern). `test_belief_truth_divergence_reads_recorded_confidence_not_replay_recomputed` constructs a fixture where a post-hoc recompute would differ from the stored value and confirms the stored value wins. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `spacesim/tests/test_assessment.py` exists and is green. | 13 tests, all passing (see Test run). | ✅ Pass |
| `python3 -m pytest spacesim/tests/test_determinism.py` remains green. | 14 passed (run with `test_import_guard.py`). | ✅ Pass |
| Manual review confirms no scoring function calls any `WorldState`-mutating engine handler. | Read `assessment.py` in full: every function reads `mgr.sim.eventlog`, `mgr.osys.orders`, or replays via `aar.state_at` (itself read-only, confirmed by its own docstring and `IP-1070`'s `VERIFIED` status) — no `sim.schedule`/handler dispatch/`world.*=` assignment anywhere in the module. | ✅ Pass |
| FS-201's Acceptance Criteria are each traceable to a specific test. | **4 of 6 are.** Two are not, and are filed as Findings #1/#2 below — one (deferred dimensions/no-composite path) was already an explicit, disclosed exclusion in IP-2010's own Implementation Tasks item 5; the other (self-assessment-mode accessibility) was not flagged anywhere in IP-2010's own text as excluded. | ⚠️ Partial — see Findings |
| `test_orders.py`'s new assertions are green, and no existing `_exec_payload()`/`custody.py` signature changed shape. | 12 relevant tests in `test_orders.py` pass (part of the 25 counted in Test run). Read `custody.py`/`orders.py` in full: `Track`'s existing fields/methods (`current_confidence`, `is_weapons_quality`, etc.) are untouched; `confidence_at_decision` is a wholly new module-level function, not a method addition to an existing class. `_exec_payload`'s existing keys are untouched; `custody_confidence_at_decision` is a new key appended to each payload dict. `IP-1030`/`IP-1020`/`IP-1010`/`IP-1051` remain correctly `VERIFIED` — nothing they document changed shape. | ✅ Pass |
| Manual confirmation that `dry_run()` performs zero eventlog/registry/booking writes. | `orders.py:141-150` (`dry_run`) calls `_plan(order, commit=False)`; `_plan` (`orders.py:152-179`) only calls `_exec_payload` inside `if commit:` (line 177-178). `test_dry_run_never_captures_custody_confidence` confirms no `custody_confidence_at_decision` capture occurs via `dry_run`. | ✅ Pass |

## Adjudication of `BL-0007` (index.html scope inclusion)

**Question:** was modifying `spacesim/ui_web/static/index.html` (new `#assessment-panel` markup)
appropriate, given IP-2010's `Files to Modify` names only `ui_web/server.py`/`ui_web/static/app.js`
explicitly?

**Adjudicated: appropriate, not scope creep.** `Files to Modify`'s own text describes "a new report
panel" for the White Cell Dashboard extension — a report panel necessarily requires HTML structure
somewhere, and this project's own established precedent (the AAR panel, which also required
`index.html` markup alongside its `app.js` logic) already treats "a new panel" as implicitly
including its markup. Read directly: `index.html:588-596` adds a `white-only` `<section>` with
`#assessment-blue`/`#assessment-red`/`#assessment-disclosure` elements — a minimal, additive block
with no restructuring of any existing panel. `BL-0007` closes with no further action.

## Resolution of `BL-0018` (IP-3010 schema-stability question)

**Question:** does anything found in this verification pass materially affect `IP-3010`'s
already-shipped `RunRecord` schema (built against `assessment_report`'s output shape while `IP-2010`
was `COMPLETE`, not yet `VERIFIED`)?

**Resolved: no.** `assessment_report(mgr) -> dict`'s signature and output shape
(`{cell: {custody_quality, window_discipline, belief_truth_divergence, disclosure}}` for
`cell in ("blue", "red")`) are exactly what this verification pass confirmed against the live tree
— unchanged from what `IP-3010` was built against. `IP-3010`'s `RunRecord.assessment: dict` field
stores this verbatim; nothing here requires revisiting that schema.

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-10110 (automated non-aggregating competency rubric-tier computation) | `session/assessment.py` (three scoring functions + `assessment_report`), `engine/custody.py`'s `confidence_at_decision`, `engine/orders.py`'s `_exec_payload` capture | `tests/test_assessment.py` (13 tests), `tests/test_orders.py` (custody-confidence-capture tests) | Already correctly cited (`IP-2010`) — **corrected this pass** to note `VERIFIED` rather than "pending 09-package-verification." | ✅ Pass |

## Test run

Commands run, in order, on commit `e7a098a084fa42c77cd80d856fbc7ed668abe689`:

```
python3 -m pytest -q spacesim/tests/test_assessment.py spacesim/tests/test_orders.py -v
  → 25 passed in 4.14s

python3 -m pytest -q spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py
  → 14 passed

python3 -m pytest -q   (full suite)
  → 566 passed, 3 skipped, 0 failed (counted programmatically — this pytest configuration
    suppresses the usual summary line)
```

Both permanent gates green. Full suite has zero failures. The 3 skips are pre-existing and
unrelated to this package.

## Scope audit

Every file this package's own `Files to Modify`/`Files to Create` names was touched, and no other
file was: `spacesim/session/assessment.py` (new), `spacesim/engine/custody.py` (additive helper),
`spacesim/engine/orders.py` (additive capture in `_exec_payload`), `spacesim/session/inprocess.py`
(wrapper), `spacesim/ui_web/server.py` (endpoint), `spacesim/ui_web/static/app.js`+`index.html`
(panel — the `index.html` inclusion is adjudicated above as implied scope, not an excursion). Tests:
`spacesim/tests/test_assessment.py` (new), `spacesim/tests/test_orders.py` (amended) — both named
in `Tests to Add`. No file outside this set was touched by the implementing diff.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| 1 | **FS-201 Acceptance Criterion "a longitudinal per-trainee report aggregates dimension-by-dimension results across exercises" is entirely unimplemented.** This is not a surprise: `IP-2010`'s own Implementation Tasks item 5 and Risks section explicitly and knowingly deferred this ("no trainee-identity/cross-session model exists... flagged as a dependency for a future IP-2011 or similar, not designed here"). The finding is that FS-201 itself is marked `✅ Done` while one of its own stated Acceptance Criteria has no implementation and no test — a spec-vs-build gap worth recording formally rather than leaving implicit. | Medium (real, but fully disclosed and anticipated by the package itself — not a hidden defect) | `06-feature-specification`, to either narrow FS-201's Acceptance Criteria to what this iteration actually delivers (with the longitudinal capability moved to its own future Feature) or explicitly track the gap until a future `IP-2011`-equivalent package closes it. |
| 2 | **FS-201 Acceptance Criterion "the report is accessible in all three assessment modes: automated in-engine, facilitator rubric (FS-106), and self-assessment/debrief (FS-107)" is only partially met.** The shipped panel (`index.html:588`) carries the `white-only` CSS class and lives in the White Cell Dashboard view group — satisfying the facilitator-rubric mode, but Blue/Red operators have no in-UI path to their own rubric during self-assessment/debrief. Unlike Finding #1, **this exclusion is not flagged anywhere in `IP-2010`'s own text** — it appears to have been missed at authoring time rather than deliberately scoped out. The `/api/sessions/{sid}/assessment` endpoint itself is not cell-gated server-side (consistent with this app's existing no-cell ground-truth endpoint pattern), so the underlying data is technically reachable — but not through the normal UI flow, which is what "accessible... in self-assessment/debrief mode" means in practice. | Medium (a real, silently-missed spec gap, not disclosed like Finding #1) | `06-feature-specification` first (confirm whether self-assessment-mode access was actually intended for this iteration, or should be descoped alongside Finding #1), then `07-implementation-planning` for a small gap-closing package (likely just relaxing the panel's visibility, or adding a Blue/Red-facing read-only view) if confirmed in scope. |
| 3 | `IP-2010`'s own `Files to Modify` proposed `confidence_at_decision(world, cell, target, now)`; the shipped signature is `confidence_at_decision(tracks: list[Track], cell, target, now)` — takes the track list directly rather than a `WorldState`, to avoid an import cycle (`custody.py` is imported by `world.py`, so importing `WorldState` back into `custody.py` would cycle). Documented inline in the function's own docstring; functionally equivalent, called correctly from `orders.py` (`self.world.tracks`). | Low (a well-justified, documented implementation-detail deviation, not a defect) | None — informational only. |

No Critical/High findings. No test failure, no scope excursion beyond the adjudicated `index.html`
inclusion, no unchecked DoD item the package itself claimed as done.

## Related

[IP-2010](../packages/IP-2010-competency-assessment.md) · [FS-201](../../features/FS-201-competency-assessment.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md)
