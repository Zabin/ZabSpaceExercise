# FS-103 — Custody Management

> **Document ID:** FS-103
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [DOM-009](../domains/DOM-009-doctrine-development-framework.md), [R105](../research/encyclopedia/R105-custody-theory.md)
> **Referenced By:** [DOM-009](../domains/DOM-009-doctrine-development-framework.md), [R105](../research/encyclopedia/R105-custody-theory.md), [DOM-002](../domains/DOM-002-assessment-framework.md) (custody quality dimension)
> **Produces:** the custody/track-confidence surface consumed by [FS-104](FS-104-sda-tasking.md) (tasking that updates custody) and
> [FS-105](FS-105-spacecraft-operations.md) (effects gated by weapons-quality custody)
> **Feature Mapping:** FS-103 (this document)
> **Related Topics:** [R104](../research/encyclopedia/R104-collection-management.md) (collection feeding custody), [R115](../research/encyclopedia/R115-electronic-warfare-in-space-operations.md)-[R117](../research/encyclopedia/R117-directed-energy-and-kinetic-effects.md) (effect categories with custody
> preconditions), [DOM-002](../domains/DOM-002-assessment-framework.md) §4 (custody quality as an assessment dimension)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

## 1. Purpose

Custody Management is the capability by which a cell builds, maintains, and consults confidence in
its track picture of an object — the operational expression of fog-of-war's central claim that a
cell never sees ground truth directly, only a custody-mediated belief. Per [R105](../research/encyclopedia/R105-custody-theory.md) §5, this
feature is the **direct owner** of the custody model surfaced to operators; [DOM-009](../domains/DOM-009-doctrine-development-framework.md) names it
as one of the two Feature Specifications the doctrine-translation pipeline depends on (the other
being [FS-104](FS-104-sda-tasking.md)).

## 2. Scope

In scope: how track confidence is displayed, how it decays over time absent fresh collection, and
how the "weapons-quality" threshold gates downstream effects. Out of scope: the sensor/SSN tasking
that produces fresh custody data ([FS-104](FS-104-sda-tasking.md)), and the effects themselves once their custody
precondition is satisfied ([FS-105](FS-105-spacecraft-operations.md)).

## 3. Capability requirements

- **Custody confidence must be displayed as a continuous/decaying quantity, never a binary
  "tracked/untracked" flag.** A cell's belief in a track's position/identity degrades over time
  without fresh observation (on-demand decay, per [`CLAUDE.md`](../../CLAUDE.md)'s `engine/custody.py` description) —
  the UI must reflect *how stale* a track's confidence is, not just whether one exists.
- **The weapons-quality gate must be visible before an operator attempts a gated action.** Any
  effect category with a custody precondition ([R115](../research/encyclopedia/R115-electronic-warfare-in-space-operations.md)-[R117](../research/encyclopedia/R117-directed-energy-and-kinetic-effects.md)) must let the operator see, ahead of
  commitment, whether the current custody confidence clears that gate — consistent with the
  pre-disabled-button pattern ([FS-101](FS-101-mission-planning.md) §3, [DOM-007](../domains/DOM-007-human-factors-framework.md) §4).
- **Belief must stay visually distinguishable from ground truth.** Per [DOM-007](../domains/DOM-007-human-factors-framework.md) §4, custody
  confidence indicators (color, iconography) must never be conflatable with an assertion of
  ground-truth fact — this is the single most load-bearing UI rule in the entire fog-of-war
  pedagogy, independent of whether the backend already enforces the boundary correctly.
- **Custody history must be retrievable for after-action review.** [DOM-002](../domains/DOM-002-assessment-framework.md) §4's "belief-truth
  divergence" assessment dimension depends on being able to compare a cell's custody confidence at
  a decision point against ground truth at that same point — custody state must be a first-class,
  queryable part of the historical record, not a transient display-only value.

## 4. Non-goals

- This spec does not define new collection mechanics (sensor tasking, SSN requests) — it defines
  how their *output* (custody confidence) is represented and consulted.
- This spec does not define the assessment rubric that consumes custody data ([FS-201](FS-201-competency-assessment.md)) — it only
  guarantees the data is structured so that consumer can use it.

## 5. Doctrine traceability

Per [DOM-009](../domains/DOM-009-doctrine-development-framework.md) §4, any vignette-specific custody/SDA assumption (e.g., a scenario's SSN dispersion
preset implying sparser or denser collection) must be expressible as data (dispersion preset
parameters), not a custody-model special case in engine code — Custody Management's behavior must
be uniform across vignettes; doctrine differences live in the data feeding it, not in this feature's
logic.

## 6. Non-functional requirements

- **Replay-safety.** Custody confidence queries (for display or for AAR) must not themselves mutate
  confidence — only the on-demand decay computation tied to actual elapsed sim time and fresh
  collection events may change it.
- **Human factors.** See §3's belief/ground-truth-legibility requirement — this is the feature
  [DOM-007](../domains/DOM-007-human-factors-framework.md) §4 names explicitly as load-bearing for the entire console.

## 7. Related Topics

[R105](../research/encyclopedia/R105-custody-theory.md) (the custody model this spec surfaces), [R104](../research/encyclopedia/R104-collection-management.md) (collection management, the upstream input),
[R115](../research/encyclopedia/R115-electronic-warfare-in-space-operations.md)-[R117](../research/encyclopedia/R117-directed-energy-and-kinetic-effects.md) (effect categories gated by custody), [DOM-009](../domains/DOM-009-doctrine-development-framework.md) (doctrine-translation pipeline this feature
supports), [DOM-002](../domains/DOM-002-assessment-framework.md) (downstream assessment consumer), [FS-104](FS-104-sda-tasking.md) (the tasking feature that produces
fresh custody data), [FS-105](FS-105-spacecraft-operations.md) (effects gated on this feature's output).
