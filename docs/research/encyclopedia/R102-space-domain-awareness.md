# R102 — Space Domain Awareness

> **Document ID:** R102
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R101](R101-orbital-mechanics-for-operations.md)
> **Referenced By:** [R104](R104-collection-management.md), [R105](R105-custody-theory.md), [R109](R109-sensor-operations.md), [R118](R118-space-surveillance-networks.md), [R119](R119-space-situational-data-fusion.md), FS-104
> **Produces:** implementation constraints for [`engine/custody.py`](../../../spacesim/engine/custody.py), SSN dispersion model
> **Feature Mapping:** FS-104 (SDA Tasking)
> **Related Topics:** [R105](R105-custody-theory.md) (Custody Theory), [R118](R118-space-surveillance-networks.md) (Space Surveillance Networks), [R119](R119-space-situational-data-fusion.md) (Data Fusion)

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Space Domain Awareness (SDA) is the discipline this entire simulator is structured around at the
session-boundary level (fog-of-war, MSTR-002 §2 invariant 3). A coding agent needs a clear model of
what SDA actually is — detect, track, characterize, attribute — to implement anything touching
sensors, custody, or the SSN correctly.

## 2. Scope

Covers: the SDA task chain (detect → track → characterize → attribute) and how each stage maps to
an engine concept. Does **not** cover: the confidence-decay mechanics of an individual track ([R105](R105-custody-theory.md)
owns that) or the SSN's specific dispersion/turnaround model ([R118](R118-space-surveillance-networks.md)).

## 3. Concepts

**The SDA task chain.** Real SDA work is commonly decomposed into four stages:

1. **Detect** — an object is observed at all (a sensor pass produces a measurement).
2. **Track** — repeated detections are associated into a continuous trajectory estimate.
3. **Characterize** — physical/behavioral properties are inferred (size, maneuverability, mission
   type) beyond bare position/velocity.
4. **Attribute** — the object is associated with an owner/operator and, for hostile-context
   objects, an intent assessment.

**Mapping to the engine.** `Track` ([R105](R105-custody-theory.md)) is principally the *track* stage's data structure, with
confidence decay modeling the reality that an un-refreshed track's positional certainty degrades
over time. *Detect* is the sensor-observation access channel firing. *Characterize* and *attribute*
are currently lighter-weight in the engine (largely vignette-authored ground truth revealed at
appropriate custody levels) — a documented current simplification, not a missing feature; see §5.

**Why this matters for fog-of-war.** A cell's entire belief state is the accumulated output of this
chain applied through *their own* sensors/SSN access — this is precisely what makes the
`TrackCatalog`/`CellView` boundary (MSTR-002 §2 invariant 3) meaningful: it's not an arbitrary
data filter, it's "show me only what this cell's SDA chain has actually produced."

## 4. Operational Context

Real-world SDA is resource-constrained and adversarial: sensors are scarce, tasking competes across
many objects of interest, and a sophisticated actor may deliberately complicate detection/tracking
(maneuvering, deploying decoys). The simulator's collection-management contention ([R104](R104-collection-management.md)) and the
SSN's coverage/dispersion model ([R118](R118-space-surveillance-networks.md)) exist to make this resource scarcity *felt* by the operator,
not just stated.

## 5. Implementation Guidance

- **Don't conflate "detected" with "characterized/attributed."** A new sensor or SDA-adjacent
  feature should be explicit about which stage(s) of the chain it advances — granting a cell
  attribution-level information from a bare detection event is a fog-of-war leak even if it never
  touches `/godview` directly.
- **If you add characterization/attribution depth**, model it as additional `Track` fields/states
  gated by sustained custody (consistent with [R105](R105-custody-theory.md)'s confidence-decay model), not as a one-shot
  reveal — this preserves the "custody must be earned and maintained" lesson (MSTR-003 §4).
- **SDA outputs should always flow through the existing custody/track structures**, never as a
  parallel ad hoc "this cell now knows X" flag — parallel state is how fog-of-war boundaries quietly
  break.

## 6. Feature Mapping

FS-104 (SDA Tasking) is the direct consumer: any sensor-tasking feature should be describable in
terms of which SDA chain stage(s) it advances and for which cell.

## 7. Related Topics

[R105](R105-custody-theory.md) (Custody Theory — the track-stage data structure), [R109](R109-sensor-operations.md) (Sensor Operations — the
detect-stage mechanics), [R118](R118-space-surveillance-networks.md) (SSN — a structured, multi-actor detect/track source), [R119](R119-space-situational-data-fusion.md) (Data
Fusion — combining multiple SDA sources into one custody picture).
