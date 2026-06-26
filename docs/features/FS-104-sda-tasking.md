# FS-104 — SDA Tasking

> **Document ID:** FS-104
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [DOM-009](../domains/DOM-009-doctrine-development-framework.md), [R102](../research/encyclopedia/R102-space-domain-awareness.md), [R104](../research/encyclopedia/R104-collection-management.md), [R109](../research/encyclopedia/R109-sensor-operations.md), [R118](../research/encyclopedia/R118-space-surveillance-networks.md), [R119](../research/encyclopedia/R119-space-situational-data-fusion.md)
> **Referenced By:** [DOM-009](../domains/DOM-009-doctrine-development-framework.md), [R102](../research/encyclopedia/R102-space-domain-awareness.md), [R104](../research/encyclopedia/R104-collection-management.md), [R109](../research/encyclopedia/R109-sensor-operations.md), [R118](../research/encyclopedia/R118-space-surveillance-networks.md), [R119](../research/encyclopedia/R119-space-situational-data-fusion.md)
> **Produces:** fresh custody data consumed by [FS-103](FS-103-custody-management.md)
> **Feature Mapping:** FS-104 (this document)
> **Related Topics:** [FS-103](FS-103-custody-management.md) (the custody picture this feature updates), [DOM-009](../domains/DOM-009-doctrine-development-framework.md) §6 (SSN
> dispersion presets as doctrine data)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

## 1. Purpose

SDA Tasking is the capability by which a cell directs its own sensors and/or requests off-board
(SSN) collection to advance its space domain awareness — detect, track, identify, characterize,
predict (the SDA chain, [R102](../research/encyclopedia/R102-space-domain-awareness.md) §3). It is the second of [DOM-009](../domains/DOM-009-doctrine-development-framework.md)'s two named
Feature Specifications, alongside [FS-103](FS-103-custody-management.md), through which doctrine (collection-management
posture, SSN dispersion realism) becomes playable content.

## 2. Scope

In scope: tasking own-sensor collection (beam-mode selection, contention resolution) and requesting
off-board SSN collection (priority/SLA tradeoff, collected-vs-delivered distinction). Out of scope:
how the resulting confidence is displayed/decayed afterward ([FS-103](FS-103-custody-management.md)), and data-fusion algorithms
themselves ([R119](../research/encyclopedia/R119-space-situational-data-fusion.md), referenced as grounding, not reimplemented here).

## 3. Capability requirements

- **Tasking must be describable in terms of which SDA chain stage it advances.** Per [R102](../research/encyclopedia/R102-space-domain-awareness.md) §6, a
  sensor-tasking feature should let the operator (and any future assessment instrument) identify
  *which* stage — detect, track, ID, characterize, or predict — a given tasking action is meant to
  advance, for which cell. This is what makes tasking purposeful rather than a generic "scan"
  button.
- **The beam-mode tradeoff must be explicit, not hidden behind a single button.** Per [R109](../research/encyclopedia/R109-sensor-operations.md) §5, a
  sensor-tasking UI must surface the real EO/SAR/SDA beam-mode tradeoff (swath vs. resolution vs.
  power) so the operator makes the tradeoff deliberately.
- **Sensor contention must be visible, not silently resolved.** Where multiple tasking requests
  compete for the same sensor resource, the feature must expose the contention and its resolution
  (consistent with [FS-102](FS-102-command-scheduling.md) §3's order-queue-contention requirement) rather than auto-selecting a
  winner invisibly.
- **SSN requests must show the priority/SLA tradeoff and the collected-vs-delivered distinction.**
  Per [R118](../research/encyclopedia/R118-space-surveillance-networks.md) §5, an SSN-facing UI must not present an off-board collection request as instant — the
  operator must see that a request resolves within a priority-dependent SLA window, and that data
  being *collected* by the network is distinct from data actually *delivered* into the requester's
  own track catalog (coalition vs. national affiliation affects both).
- **Fusion output must extend the existing tasking display, not replace it.** Per [R119](../research/encyclopedia/R119-space-situational-data-fusion.md) §5, any
  richer multi-source fusion capability must layer onto the existing track-confidence display
  ([FS-103](FS-103-custody-management.md)) rather than introducing a second, parallel confidence representation.

## 4. Non-goals

- This spec does not define the custody-decay/display model itself ([FS-103](FS-103-custody-management.md)).
- This spec does not define new SSN dispersion presets or doctrine content — those are data
  ([DOM-009](../domains/DOM-009-doctrine-development-framework.md) §4), consumed by this feature, not authored by it.

## 5. Doctrine traceability

Per [DOM-009](../domains/DOM-009-doctrine-development-framework.md) §3-4, a vignette's collection-management posture (sparse/regional/global/proliferated
SSN dispersion, sensor-tasking realism for a given scenario) is doctrine-derived data feeding this
feature, not a special case coded into the tasking logic — SDA Tasking's behavior is uniform across
vignettes; the doctrine differences live in the dispersion-preset parameters.

## 6. Related Topics

[R102](../research/encyclopedia/R102-space-domain-awareness.md) (SDA chain model), [R104](../research/encyclopedia/R104-collection-management.md) (collection management), [R109](../research/encyclopedia/R109-sensor-operations.md) (sensor beam-mode tradeoffs), [R118](../research/encyclopedia/R118-space-surveillance-networks.md) (SSN),
[R119](../research/encyclopedia/R119-space-situational-data-fusion.md) (fusion), [DOM-009](../domains/DOM-009-doctrine-development-framework.md) (doctrine-translation pipeline), [FS-103](FS-103-custody-management.md) (the custody surface this feature feeds).
