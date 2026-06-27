# IMP-103A — Custody Management: Track Confidence Model

> **Document ID:** IMP-103A
> **Version:** 1.0
> **Status:** ✅ Done (as-built — documents existing, test-covered code)
> **Dependencies:** [FS-103](../features/FS-103-custody-management.md)
> **Referenced By:** [IMP-104A](IMP-104A-sda-tasking.md) (the tasking package that produces fresh `observe()` calls), [IMP-105A](IMP-105A-spacecraft-operations-bus-payload.md)/[IMP-102A](IMP-102A-command-scheduling.md) (the `engage` gate at `orders.py:349`)
> **Produces:** the custody confidence surface [FS-105](../features/FS-105-spacecraft-operations.md)'s console and [FS-107](../features/FS-107-after-action-review.md)'s AAR consume
> **Feature Mapping:** FS-103
> **Related Topics:** [`spacesim/engine/custody.py`](../../spacesim/engine/custody.py), [`spacesim/session/scene.py`](../../spacesim/session/scene.py)

[↑ Implementation index](INDEX.md) · [Docs index](../INDEX.md)

## 1. Situation

**As-built.** This package documents the existing `Track`/`observe()` confidence-decay model in
`engine/custody.py` and how it is surfaced for display and gating.

## 2. Decay model

`Track` (`custody.py:30`) stores confidence **as of `last_observation`**, not a continuously
ticking value — `current_confidence(now, half_life_s)` (`:45`) computes the decayed value on
demand:

```
confidence(now) = confidence_at_last_obs * 0.5 ** ((now - last_observation) / half_life_s)
```

with `DEFAULT_HALF_LIFE_S = 1800.0` (`:19`, 30-minute half-life). This is a pure function of
`now` — no stored field mutates between observations, which is what makes custody queries
replay-safe (FS-103 §6's non-functional requirement): calling `current_confidence()` from a
display read or from an AAR `snapshot_at()` (`aar.py:56`) call can never itself change state.
`current_uncertainty_km(now, growth)` (`:49`) mirrors this for the uncertainty volume, growing
linearly (`DEFAULT_GROWTH_KM_PER_S = 0.02`, `:20`) from the value frozen at the last observation
(`uncertainty_at_obs`, `:39`) rather than the live `uncertainty` field.

`observe(track, now, quality, characterizes, classification)` (`:57`) is the only path that
resets this state: it overwrites `confidence` with the fresh `quality` (clamped `[0, 1]`),
sets `last_observation = now`, and collapses both uncertainty fields back to zero — modeling a
report tightening the belief, not just refreshing a timestamp.

## 3. The weapons-quality gate

`is_weapons_quality(now, threshold=WEAPONS_QUALITY_THRESHOLD)` (`:53`, threshold `0.8` at `:21`)
requires **both** `characterized` and `current_confidence(now) >= threshold` — a track can be
confident but uncharacterized (object detected, identity unresolved) and still fail the gate.
This is consulted at exactly the point FS-103 §3 requires visibility: `OrderSystem._validate()`
(`orders.py:349`) blocks an `engage` order with `"no_weapons_quality_track"` if
`world.track_for(order.cell, order.target)` (`world.py:48`) is `None` or fails the gate — and
because this same `_validate()` runs on `dry_run()` (per [IMP-101A](IMP-101A-mission-planning.md) §2), the
pre-disabled-button preview surfaces this exact rejection string before commitment, satisfying
FS-103 §3's "visible before an operator attempts a gated action" requirement without a
console-side duplicate of the threshold check.

## 4. Display surface

`SceneView`'s per-cell render (`scene.py:118`-`128`) filters `world.tracks` to `t.owner == cell`
(fog-of-war: a cell only ever sees its own custody, never another cell's or ground truth) and
populates `RenderTrack.confidence`/`uncertainty_km` by calling the same `current_confidence()`/
`current_uncertainty_km()` methods at render time — there is no separate display-side decay
estimator, so the console's number and the gate's number are computed by the identical code path.
This continuous float (rounded to 3 decimals) is what satisfies FS-103 §3's "never a binary
tracked/untracked flag" requirement; `characterized`/`classification` are carried alongside as
separate fields so the UI can distinguish "low confidence" from "unidentified" rather than
collapsing them into one indicator — the basis for the belief/ground-truth visual distinction
[DOM-007](../domains/DOM-007-human-factors-framework.md) §4 requires (FS-103 §3 bullet 3); the actual color/iconography choice is a
console rendering concern outside this package's scope (see [IMP-105B](IMP-105B-spacecraft-operations-effects-console.md)).

## 5. Custody history for AAR

Because `Track` is plain pydantic state inside `WorldState.tracks` (`world.py:26`) and the decay
function is pure, `aar.snapshot_at(mgr, seq)` (`aar.py:56`) — which replays the eventlog to an
arbitrary sequence number and returns the `WorldState` at that point — reconstructs a fully valid
historical `Track` set: calling `current_confidence(now=<that_seq's_sim_time>)` against the
replayed state yields the cell's belief exactly as it stood then. This satisfies FS-103 §3's
"custody history must be retrievable for after-action review" requirement without custody needing
any AAR-specific storage of its own — the eventlog is the history, and custody is one of the
projections replay can produce at any point along it.

## 6. Satisfying FS-103's capability requirements

- **Continuous/decaying confidence, never binary** (§3 bullet 1): §2's exponential-decay formula,
  surfaced as a float by §4.
- **Weapons-quality gate visible pre-commitment** (§3 bullet 2): §3 — the same `_validate()` check
  on both `dry_run()` and `issue()`.
- **Belief visually distinguishable from ground truth** (§3 bullet 3): §4's per-cell `tracks`
  filter (no cell ever receives another cell's or ground-truth `Track` rows) plus the separate
  `characterized`/`classification` fields backing the console's iconography.
- **Custody history queryable for AAR** (§3 bullet 4): §5.

## 7. Test coverage (existing)

`spacesim/tests/test_custody.py` covers decay/observe/weapons-quality-gate behavior directly; the
`engage`-order rejection path (`orders.py:349`) is covered by the order-system test suite. No new
tests are proposed by this package.

## 8. Related Topics

[FS-103](../features/FS-103-custody-management.md) (the spec this documents), [IMP-104A](IMP-104A-sda-tasking.md) (the tasking package whose `observe()`
calls feed this model), [IMP-105B](IMP-105B-spacecraft-operations-effects-console.md) (console rendering of the confidence/characterization
distinction), [`spacesim/engine/custody.py`](../../spacesim/engine/custody.py), [`spacesim/session/scene.py`](../../spacesim/session/scene.py).
