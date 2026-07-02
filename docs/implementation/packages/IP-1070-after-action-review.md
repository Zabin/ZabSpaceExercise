# IP-1070 — After Action Review: Replay/Scrub/Branch-Compare

> **Package ID:** IP-1070
> **Version:** 1.0
> **Status:** ✅ VERIFIED
> **Dependencies:** FS-107, IP-1030 (`scene.py` composition for belief-vs-truth diffs)
> **Referenced By:** IP-1060 (White-only trigger controls that invoke this instrument), IP-2010 (belief-truth-divergence data source), [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** the replay/snapshot surface IP-2010's belief-truth-divergence dimension reads from
> **Feature Reference:** [FS-107 — After Action Review](../../features/FS-107-after-action-review.md)
> **Supersedes:** [`docs/implementations/IMP-107A-after-action-review.md`](../../implementations/IMP-107A-after-action-review.md)
> **Related Topics:** [`spacesim/session/aar.py`](../../../spacesim/session/aar.py), [`spacesim/engine/simulation.py`](../../../spacesim/engine/simulation.py), [`spacesim/session/scene.py`](../../../spacesim/session/scene.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

## Package ID

IP-1070

## Title

After Action Review — Replay/Scrub/Branch-Compare

## Objective

Turn a completed (or in-progress) exercise's full eventlog into a teaching artifact: read-only
scrub/replay, a first-class god-view-vs-belief diff at any timeline point, branch comparison for
"what if" exploration without altering the canonical record, and self-assessment use with no
facilitator gate — all built on the engine's determinism guarantee rather than a bespoke
replay mechanism.

**Situation: already implemented, tested, in production use.**

## Feature Reference

[FS-107 — After Action Review](../../features/FS-107-after-action-review.md)

## Requirements Covered

FS-107's "Requirements Implemented" field reports no explicit FR/NFR citation (documented gap).
Functional coverage per the RTM's `session/aar.py` mapping:

| Req ID | Title (abridged) | How this package covers it |
|---|---|---|
| FR-7310 | AAR replay/scrub | `state_at()` (`aar.py:40`), calling `replay()` (`engine/simulation.py`) |
| FR-7320 | AAR branch compare | `compare_branches()` (`aar.py:105`) |
| FR-1120 | Deterministic replay (byte-identical from state/eventlog/seed) | `state_at()` depends directly on this invariant; gated by the Phase-1 determinism property test |
| NFR-2500 | Action-log sufficiency | `report()`'s `DECISION_KINDS`-filtered timeline (`aar.py:19`, `:90`) |

## Architecture Components

- **C2 Session / Application Layer** — `session/aar.py` (`state_at`, `objectives_at`,
  `snapshot_at`, `report`, `compare_branches`, `export_csv`).
- **C1 Simulation Engine** — `engine/simulation.py` (`replay()`), `engine/eventlog.py`
  (`EventLog`/`Snapshot`), consumed read-only.

## Interfaces

**INT-0014** (Session Layer AAR/Replay → Simulation Engine EventLog/WorldState) — per the ICD and
FS-107's verified Related Interfaces field.

## Files to Create

None — capability already implemented.

## Files to Modify

None — this package documents shipped code.

### Reference files

- `spacesim/session/aar.py` — `state_at()` (`:40`), `objectives_at()` (`:51`), `snapshot_at()`
  (`:56`), `report()` (`:90`), `AARReport`/`AAREvent`/`DECISION_KINDS` (`:31`, `:23`, `:19`),
  `_summarize()` (`:72`), `compare_branches()` (`:105`), `export_csv()` (`:120`).
- `spacesim/engine/simulation.py` — `replay()`.
- `spacesim/session/scene.py` — `build_scene()` (`:81`), composed with `state_at()` for the
  belief-vs-truth diff.
- `spacesim/session/inprocess.py` — `aar_report`/`aar_objectives_at`/`aar_snapshot_at` (`:742-750`).

## Implementation Tasks

All **already complete**:

1. ✅ Implement `state_at()` as a pure reconstruction (a fresh `WorldState` built from scratch via
   `replay()` on every call), never mutating the live session's `mgr.sim.world`.
2. ✅ Implement `objectives_at()`/`snapshot_at()` as thin wrappers over `state_at()`, giving scrub-to-
   any-point behavior for free from one primitive.
3. ✅ Compose `build_scene(state_at(mgr, seq), cell)` against `state_at(mgr, seq)` directly (ground
   truth) at the identical `seq` as the belief-vs-truth diff — reusing IP-1030's fog-of-war render
   rather than duplicating it.
4. ✅ Implement `report()` filtered to `DECISION_KINDS` (real decisions, not scheduling bookkeeping)
   and `compare_branches()` as a pure diff over two already-built `AARReport`s, with no
   session-mutating capability.
5. ✅ Leave `report()`/`compare_branches()`/`snapshot_at()` ungated to White-only — any session-id
   caller (facilitator or trainee) can invoke the same functions for self-assessment.
6. ✅ Implement `export_csv()` (META/TIMELINE/OBJECTIVES sections) as the existing export format.

## Tests to Add

None — replay exactness is gated by the Phase-1 determinism property test
(`spacesim/tests/test_determinism.py`, which `state_at()` depends on directly); AAR-specific
behavior (timeline filtering, branch-compare flips, CSV export) is covered by the existing AAR test
suite.

## Documentation Updates

- Supersedes [`docs/implementations/IMP-107A-after-action-review.md`](../../implementations/IMP-107A-after-action-review.md).
- `ROADMAP.md` Implementation Packages theme updated.

## Definition of Done

- [x] `state_at()`/`objectives_at()`/`snapshot_at()` produce zero `WorldState` mutation under any
  call sequence.
- [x] The belief-vs-truth diff is queryable as a distinct output at any `seq`, not only as a combined
  render.
- [x] `compare_branches()` never alters either input `AARReport`'s originating session.
- [x] A trainee can invoke `report()`/`snapshot_at()` for their own session without any
  facilitator-only gate.
- [x] Belief and ground truth are never merged into one rendered object at any timeline point.

## Verification Checklist

- [x] `aar.py:19,23,31,40,51,56,72,90,105,120`, `scene.py:81`, and `inprocess.py:742-750` read and
  confirmed against the current tree.
- [x] `spacesim/tests/test_determinism.py` and the AAR test suite present and green.
- [x] No FR/NFR explicitly cites FS-107 (confirmed absence) — recorded as a traceability gap.
- [x] No ADR explicitly names AAR replay-safety as a settled decision point distinct from ADR-0002 —
  recorded as an open item for future ADR authoring, not silently resolved here.

## Dependencies

- **Upstream:** IP-1030 (`scene.py`'s fog-of-war render, composed for the belief-vs-truth diff).
- **Downstream:** IP-1060 (White-only trigger controls hosting this instrument), IP-2010
  (belief-truth-divergence rubric dimension reads `state_at`/`report`/`DECISION_KINDS` output
  directly).
- **Build-sequencing:** None — already shipped.

## Risks

- If AAR were ever treated as purely a facilitator tool in a future console change (self-assessment
  use not designed for), DOM-002 §6's stated self-assessment mode would be silently excluded — the
  source FS-107 names this as a design requirement, not an afterthought.
- Any future change that gives `snapshot_at()`/branch operations even a "temporary" `WorldState`
  mutation would violate the live-session replay-safety invariant this entire package depends on.

## Rollback Considerations

Rollback surface: `spacesim/session/aar.py` (entire module) and the `aar_*` wrapper functions in
`spacesim/session/inprocess.py`. AAR introduces no new persisted schema of its own (it is a pure
read layer over the existing `EventLog`/`WorldState`); a revert requires re-verification against the
determinism property test and the AAR test suite before landing.
