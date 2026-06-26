# R119 — Space Situational Data Fusion

> **Document ID:** R119
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R105](R105-custody-theory.md), [R118](R118-space-surveillance-networks.md)
> **Referenced By:** FS-104
> **Produces:** implementation constraints for [`engine/custody.py`](../../../spacesim/engine/custody.py) (`Track.source`), the SSN→TrackCatalog delivery path
> **Feature Mapping:** FS-104 (SDA Tasking)
> **Related Topics:** [R105](R105-custody-theory.md) (Custody Theory), [R118](R118-space-surveillance-networks.md) (Space Surveillance Networks), [R102](R102-space-domain-awareness.md) (Space Domain Awareness)

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Data fusion in this simulator is deliberately narrow: multiple sources (organic sensors, SSN
requests) write into the *same* `Track` rather than each maintaining a separate belief object that
must later be reconciled. This topic exists so a future feature implementing richer multi-source
fusion (confidence-weighted combination, conflicting-source arbitration) understands the current
single-track-per-object-per-cell model it would be extending.

## 2. Concepts

**Fusion today is "last observation wins," not multi-source weighting.** `observe()` ([R105](R105-custody-theory.md))
unconditionally resets `confidence`/`last_observation`/`uncertainty` to the new report's values —
there is no confidence-weighted blending of an organic detection with a concurrent SSN product; the
most recent qualifying observation simply overwrites the track's working state. This is a
deliberate, documented simplification ([R102](R102-space-domain-awareness.md) §3), not a missing accuracy feature, but a future
"genuine fusion" feature must not assume the engine already does confidence-weighted combination.

**`Track.source` records provenance but does not yet drive different trust weighting.** The
`source: str = "own_sensor"` field exists on `Track` to record where the current observation came
from, but nothing in `observe()` currently varies the *update rule* by source — a genuine fusion
feature (e.g. trusting a characterized SSN product more than a fresh organic detection of lower
quality) would need to extend `observe()`'s logic to read and act on `source`, not just record it.

**SSN delivery and organic observation write to the same `TrackCatalog` through the same primitive.**
`ssn.py`'s delivery handler and `OrderSystem._h_observe` both ultimately call `observe()` on a
`Track` in the requesting cell's catalog — this is exactly [R102](R102-space-domain-awareness.md) §5's "SDA outputs should always flow
through the existing custody/track structures" guidance in practice: there is one fusion point, not
two parallel ones.

**Auto-cueing is the one existing cross-source coupling.** The SSN auto-cue mechanism ([R104](R104-collection-management.md) §2)
reads an organically-produced track's confidence band to decide whether to *request* an SSN product
— this is sequencing (one source triggers a request to another), not fusion (combining two
concurrent measurements into one improved estimate). Don't mistake the auto-cue path for actual
multi-source fusion; it produces a second, later observation of the same object, which then
overwrites via the same last-observation-wins rule.

## 3. Operational Context

Real SDA data fusion combines multiple, often heterogeneous sources (radar, optical, SIGINT, SSN
partner products) into a single best estimate, typically weighting by source reliability and
recency rather than simply taking the latest report — the simulator's current "most recent
observation wins" model is a deliberate v1 simplification of this real, harder problem, sufficient
because each individual observation already resets confidence to a meaningful value via its own
`quality` parameter.

## 4. Implementation Guidance

- **Don't assume confidence-weighted multi-source fusion exists today** — any feature claiming to
  "fuse" two sources should explicitly state whether it means sequencing (one source cues another,
  as auto-cue does) or actually implement weighted combination as new logic in `observe()`.
- **If you implement genuine multi-source fusion, treat it as its own scoped Implementation
  Package** — extending `observe()`'s update rule to read `Track.source` and weight accordingly,
  with its own validation method ([R105](R105-custody-theory.md)'s confidence-decay model must remain intact for the
  no-new-observation case).
- **Keep fusion outputs inside `TrackCatalog`/`Track`** — per [R102](R102-space-domain-awareness.md) §5, never write a second,
  parallel "fused confidence" field outside the existing structure; that would reopen exactly the
  fog-of-war-leak risk [R102](R102-space-domain-awareness.md) warns about.
- **Preserve per-cell independence ([R105](R105-custody-theory.md) §2) even under fusion** — a fusion feature must never let
  one cell's organic detection improve the other cell's track; fusion combines *a single cell's*
  multiple sources, never crosses the cell boundary.

## 5. Feature Mapping

FS-104 (SDA Tasking) is the direct consumer — a richer fusion feature would extend, not replace,
the existing tasking UI's track-confidence display.

## 6. Related Topics

[R105](R105-custody-theory.md) (the `Track`/confidence-decay structure fusion would extend), [R118](R118-space-surveillance-networks.md) (SSN — one of the two
current sources writing into the same track), [R102](R102-space-domain-awareness.md) (the SDA chain and its fog-of-war-boundary
guidance fusion must respect).
