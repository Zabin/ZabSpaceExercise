# IP-1030 — Custody Management: Track Confidence Model

> **Package ID:** IP-1030
> **Version:** 1.0
> **Status:** ✅ VERIFIED
> **Dependencies:** FS-103
> **Referenced By:** IP-1040 (produces the `observe()` calls this model consumes), IP-1050/IP-1051 (the `engage` gate), IP-1070 (AAR custody replay), [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** the custody-confidence surface IP-1051's console and IP-1070's AAR consume
> **Feature Reference:** [FS-103 — Custody Management](../../features/FS-103-custody-management.md)
> **Supersedes:** [`docs/implementations/IMP-103A-custody-management.md`](../../implementations/IMP-103A-custody-management.md)
> **Related Topics:** [`spacesim/engine/custody.py`](../../../spacesim/engine/custody.py), [`spacesim/session/scene.py`](../../../spacesim/session/scene.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

## Package ID

IP-1030

## Title

Custody Management — Track Confidence Model

## Objective

Give each cell a continuous, decaying confidence value per tracked object (never a binary
tracked/untracked flag), gate engagement-intent actions on a weapons-quality threshold visible
before commitment, and keep belief visually/structurally distinguishable from ground truth at every
consumption point — the operational expression of fog-of-war's central claim that a cell never sees
ground truth directly.

**Situation: already implemented, tested, in production use.**

## Feature Reference

[FS-103 — Custody Management](../../features/FS-103-custody-management.md)

## Requirements Covered

FS-103's "Requirements Implemented" field reports no explicit FR/NFR citation (documented gap).
Functional coverage per the RTM's `engine/custody.py` mapping:

| Req ID | Title (abridged) | How this package covers it |
|---|---|---|
| FR-1510 | Track confidence decay and reset on observation | `current_confidence()` (`custody.py:45`), `observe()` (`:57`) |
| FR-1520 | Weapons-quality track gate | `is_weapons_quality()` (`:53`), consulted by `OrderSystem._validate()` (`orders.py:349`) |
| FR-6210 | Fog-of-war filtering at the boundary | `scene.py:118-128` filters `world.tracks` to `t.owner == cell` before any render |
| NFR-1500 | Determinism (engine-wide) | `current_confidence()` is a pure function of `now`; no stored field mutates between observations |

## Architecture Components

- **C1 Simulation Engine** — `engine/custody.py` (`Track`, decay, weapons-quality gate),
  `engine/world.py` (`WorldState.tracks`, `track_for()`).
- **C2 Session / Application Layer** — `session/scene.py` (per-cell fog-of-war render),
  `session/aar.py` (historical custody reconstruction via replay).

## Interfaces

**INT-0007** (CellController → Simulation Engine Custody/TrackCatalog) — per the ICD and FS-103's
verified Related Interfaces field.

## Files to Create

None — capability already implemented.

## Files to Modify

None — this package documents shipped code.

### Reference files

- `spacesim/engine/custody.py` — `Track` (`:30`), `current_confidence()` (`:45`),
  `current_uncertainty_km()` (`:49`), `is_weapons_quality()` (`:53`), `observe()` (`:57`),
  `DEFAULT_HALF_LIFE_S`/`WEAPONS_QUALITY_THRESHOLD` (`:19`, `:21`).
- `spacesim/session/scene.py` — per-cell `tracks` filter and `RenderTrack` population (`:118-128`).
- `spacesim/engine/orders.py:349` — the `engage`-order weapons-quality rejection.
- `spacesim/session/aar.py:56` — `snapshot_at()`, the AAR replay point custody history composes with.

## Implementation Tasks

All **already complete**:

1. ✅ Implement on-demand exponential confidence decay
   (`confidence(now) = confidence_at_last_obs * 0.5 ** ((now - last_observation) / half_life_s)`)
   as a pure function of `now`, never a ticking stored field.
2. ✅ Implement `observe()` as the sole state-resetting path: overwrite confidence with fresh
   `quality`, reset `last_observation`, collapse uncertainty to zero.
3. ✅ Implement `is_weapons_quality()` requiring both `characterized` and confidence ≥ threshold
   (`0.8` default) — a confident-but-uncharacterized track still fails the gate.
4. ✅ Wire the gate into `OrderSystem._validate()` so both `dry_run()` and `issue()` surface the
   identical `"no_weapons_quality_track"` rejection pre-commitment (no console-side duplicate check).
5. ✅ Filter `scene.py`'s per-cell render to `t.owner == cell` so no cell ever receives another
   cell's or ground-truth `Track` rows; carry `characterized`/`classification` as separate fields
   rather than collapsing them into one indicator.

## Tests to Add

None — covered by `spacesim/tests/test_custody.py` (decay/observe/weapons-quality-gate) and the
order-system test suite (the `engage`-order rejection path).

## Documentation Updates

- Supersedes [`docs/implementations/IMP-103A-custody-management.md`](../../implementations/IMP-103A-custody-management.md).
- `ROADMAP.md` Implementation Packages theme updated.

## Definition of Done

- [x] Confidence is a continuous float, never a binary flag, at every display point.
- [x] The weapons-quality gate is visible pre-commitment via `dry_run()` parity with `issue()`.
- [x] No cell's `scene.py` render ever includes another cell's or ground-truth `Track` rows.
- [x] Historical custody at any AAR `snapshot_at()` point reconstructs correctly via pure replay.
- [x] Custody-confidence queries never mutate state (replay-safety).

## Verification Checklist

- [x] `custody.py:19,21,30,45,49,53,57` and `orders.py:349` read and confirmed against the current tree.
- [x] `spacesim/tests/test_custody.py` present and green.
- [x] No FR/NFR explicitly cites FS-103 (confirmed absence) — recorded as a traceability gap.

## Dependencies

- **Upstream:** None — self-contained engine module.
- **Downstream:** IP-1040 (SDA Tasking, whose `observe()` calls feed this model), IP-1050/IP-1051
  (console rendering and the engagement gate), IP-1070 (AAR custody-history replay), IP-2010
  (custody-quality rubric dimension reads this data).
- **Build-sequencing:** None — already shipped.

## Risks

- If a future console rework styles belief indicators in a way confusable with ground-truth
  assertions, the fog-of-war pedagogy is undermined regardless of this package's backend
  correctness — the single most load-bearing UI rule in the corpus
  ([DOM-007](../../domains/DOM-007-human-factors-framework.md) §4).
- If custody state were ever stored only as a transient display value (not reconstructible via
  eventlog replay), IP-1070's AAR and IP-2010's belief-truth-divergence dimension would have no
  queryable data to operate on — the current pure-function-over-replay design avoids this by
  construction and must be preserved in any future change.

## Rollback Considerations

Rollback surface: `spacesim/engine/custody.py` (all functions) and the `orders.py:349` gate call.
Because `Track` is plain pydantic state inside `WorldState.tracks` (no custody-specific persisted
schema beyond the existing save format), a revert requires no data migration — but must be
re-verified against `spacesim/tests/test_custody.py` and the determinism property test before
landing, since custody state participates in eventlog replay.
