# FS-104 — SDA Tasking

> **Document ID:** FS-104
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [DOM-009](../domains/DOM-009-doctrine-development-framework.md), [R102](../research/encyclopedia/R102-space-domain-awareness.md), [R104](../research/encyclopedia/R104-collection-management.md), [R109](../research/encyclopedia/R109-sensor-operations.md), [R118](../research/encyclopedia/R118-space-surveillance-networks.md), [R119](../research/encyclopedia/R119-space-situational-data-fusion.md)
> **Referenced By:** [DOM-009](../domains/DOM-009-doctrine-development-framework.md), [R102](../research/encyclopedia/R102-space-domain-awareness.md), [R104](../research/encyclopedia/R104-collection-management.md), [R109](../research/encyclopedia/R109-sensor-operations.md), [R118](../research/encyclopedia/R118-space-surveillance-networks.md), [R119](../research/encyclopedia/R119-space-situational-data-fusion.md), [IMP-104A](../implementations/IMP-104A-sda-tasking.md)
> **Produces:** fresh custody data consumed by [FS-103](FS-103-custody-management.md)
> **Feature Mapping:** FS-104 (this document)
> **Related Topics:** [FS-103](FS-103-custody-management.md) (the custody picture this feature updates), [DOM-009](../domains/DOM-009-doctrine-development-framework.md) §6 (SSN
> dispersion presets as doctrine data)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template; it supersedes this file's prior ad hoc structure while retaining its existing Document ID, status, and metadata per MSTR-006 §5.*

## Feature ID

FS-104

## Title

SDA Tasking

## Purpose

SDA Tasking is the capability by which a cell directs its own sensors and/or requests off-board
(SSN) collection to advance its space domain awareness — detect, track, identify, characterize,
predict (the SDA chain per [R102](../research/encyclopedia/R102-space-domain-awareness.md) §3). It is the second of [DOM-009](../domains/DOM-009-doctrine-development-framework.md)'s two named Feature
Specifications (alongside [FS-103](FS-103-custody-management.md)) through which doctrine — collection-management posture and
SSN dispersion realism — becomes playable content.

## Scope

In scope: tasking own-sensor collection (beam-mode selection, contention resolution) and requesting
off-board SSN collection (priority/SLA tradeoff, collected-vs-delivered distinction). Out of scope:
how the resulting confidence is displayed/decayed afterward ([FS-103](FS-103-custody-management.md)), and data-fusion algorithms
themselves ([R119](../research/encyclopedia/R119-space-situational-data-fusion.md), referenced as grounding, not reimplemented here).

## Requirements Implemented

None identified — the FR-xxxx/NFR-xxxx requirements corpus (`docs/requirements/`) contains no
explicit citation of this Feature ID. This is a traceability gap, not a deliberate
non-applicability; closing it is Phase 8 traceability-review work (MSTR-006 §7), not something this
rewrite may resolve by inference.

## User Workflows

- A cell operator selects an own sensor and tasks it for collection against a target, choosing a
  beam mode (EO/SAR/SDA) and observing the beam-mode tradeoff (swath vs. resolution vs. power)
  explicitly before committing.
- Where multiple tasking requests compete for the same sensor resource, the operator observes the
  contention and its resolution rather than a silent winner selection.
- A cell operator submits an off-board SSN collection request and observes: the priority/SLA
  tradeoff (national vs. coalition affiliation affects both timing and availability), that the data
  being *collected* by the network is distinct from data *delivered* into the requester's own track
  catalog, and the elapsed time before delivery.
- Once collection data arrives, it updates the operator's track confidence in [FS-103](FS-103-custody-management.md)'s display,
  reducing staleness.

## System Behaviour

- **Tasking must be describable in terms of which SDA chain stage it advances.** Per [R102](../research/encyclopedia/R102-space-domain-awareness.md) §6, the
  feature should let the operator (and any future assessment instrument) identify *which* stage —
  detect, track, ID, characterize, or predict — a given tasking action is meant to advance, for
  which cell. This makes tasking purposeful rather than a generic "scan" button.
- **The beam-mode tradeoff must be explicit, not hidden behind a single button.** Per [R109](../research/encyclopedia/R109-sensor-operations.md) §5, the
  tasking surface must expose the real EO/SAR/SDA beam-mode tradeoff (swath vs. resolution vs.
  power) so the operator makes the tradeoff deliberately.
- **Sensor contention must be visible, not silently resolved.** Where multiple tasking requests
  compete for the same sensor resource, the feature must expose the contention and its resolution
  (consistent with [FS-102](FS-102-command-scheduling.md) §3's order-queue-contention requirement) rather than auto-selecting
  a winner invisibly.
- **SSN requests must show the priority/SLA tradeoff and the collected-vs-delivered distinction.**
  Per [R118](../research/encyclopedia/R118-space-surveillance-networks.md) §5, the SSN-facing interface must not present an off-board collection request as
  instant — the operator must see that a request resolves within a priority-dependent SLA window,
  and that data being *collected* by the network is distinct from data actually *delivered* into the
  requester's own track catalog (coalition vs. national affiliation affects both).
- **Fusion output must extend the existing tasking display, not replace it.** Per [R119](../research/encyclopedia/R119-space-situational-data-fusion.md) §5, any
  richer multi-source fusion capability must layer onto the existing track-confidence display
  ([FS-103](FS-103-custody-management.md)) rather than introducing a second, parallel confidence representation.
- **Doctrine differences live in data.** Per [DOM-009](../domains/DOM-009-doctrine-development-framework.md) §3-4, a vignette's collection-management
  posture (sparse/regional/global/proliferated SSN dispersion) is doctrine-derived data feeding
  this feature; SDA Tasking's behavior is uniform across vignettes; doctrine differences live in
  the dispersion-preset parameters, not in the tasking logic.

## Subsystem Responsibilities

The source document does not provide a per-subsystem breakdown. [`CLAUDE.md`](../../CLAUDE.md) names `engine/ssn.py`
(the mock SSN, per ADR-0010) and `engine/access.py` / `session/CellController` as relevant
components, but the source document does not assign responsibilities in a formal table. Flagged as
an Open Question below.

## Interfaces Used

Per the verified mapping for FS-104: INT-0009 (CellController/SessionAPI → Mock SSN) and INT-0010
(Mock SSN → Simulation Engine Scheduler/EventLog/Custody, delivery) — per
`docs/design/05-interface-control-document.md`. The source document does not itself cite ICD
interface IDs; these are carried forward from the verified Related Interfaces mapping (field 21).

## Data Model Changes

Not addressed in the source document — no existing content to carry forward. The SSN dispersion
presets referenced (sparse/regional/global/proliferated) are existing data structures (per
[`CLAUDE.md`](../../CLAUDE.md)); whether this feature requires any new Domain Model entities beyond existing
`SSNNetwork` and tasking structures is unresolved. Flagged as an Open Question below.

## State Changes

- A tasking request enters the SSN queue and transitions from requested → collected → delivered,
  with each transition producing a distinct observable state.
- An own-sensor tasking transitions from beam-mode-selected → contention-checked → executing →
  collection-delivered.
- Delivery updates [FS-103](FS-103-custody-management.md)'s custody state (refreshing confidence) but does not itself alter
  SDA Tasking's own state beyond marking the request complete.

## Error Handling

- Sensor contention must surface the conflict and its resolution, not silently select a winner.
- The source document does not enumerate additional failure modes for tasking or SSN requests
  (e.g., SSN request not fulfilled within SLA).

## Performance Considerations

- **Determinism.** SSN tasking resolution uses a deterministic handler (`ssn_collect` /
  `ssn_deliver`, per [`CLAUDE.md`](../../CLAUDE.md)) that stages on `world.ssn_staged` and delivers into the
  requester's `TrackCatalog` — this is replay-safe and must remain so.
- **Doctrine differences must not require engine changes.** Vignette-level dispersion-preset
  differences must be expressible as data parameters, not as per-vignette engine branches.

## Security Considerations

Not addressed in the source document — no existing content to carry forward. Coalition vs. national
affiliation affects SSN delivery timing and availability; whether this creates any access-control
concern beyond the existing fog-of-war boundary is unresolved. Flagged as an Open Question below.

## Acceptance Criteria

Derived from the source document's capability requirements, restated as checkable conditions:

- A tasking action is labeled with which SDA chain stage (detect/track/ID/characterize/predict) it
  is intended to advance.
- Own-sensor tasking exposes the EO/SAR/SDA beam-mode tradeoff explicitly before commitment.
- When multiple tasking requests contend for the same sensor, the contention and resolution are
  visible.
- An SSN collection request shows: the priority/SLA window, the collected-vs-delivered distinction,
  and the coalition vs. national affiliation effect on delivery timing.
- Any richer fusion-based confidence display layers onto the existing FS-103 track-confidence
  representation rather than introducing a second, parallel display.
- SDA Tasking behavior is uniform across vignettes; scenario-specific differences are expressed via
  dispersion-preset data, not by altering the tasking logic.

## Verification Plan

The source document does not state a Verification Method per criterion. Test (automated) is implied
by the determinism constraint (SSN delivery is tested as replay-safe per [`CLAUDE.md`](../../CLAUDE.md)). Flagged as
an Open Question below.

## Dependencies

[DOM-009](../domains/DOM-009-doctrine-development-framework.md), [R102](../research/encyclopedia/R102-space-domain-awareness.md), [R104](../research/encyclopedia/R104-collection-management.md), [R109](../research/encyclopedia/R109-sensor-operations.md), [R118](../research/encyclopedia/R118-space-surveillance-networks.md), [R119](../research/encyclopedia/R119-space-situational-data-fusion.md) (per the existing
metadata block's Dependencies field). [FS-103](FS-103-custody-management.md) is a downstream consumer (the custody surface
this feature feeds), not an upstream dependency of FS-104.

## Risks

- If SSN dispersion preset differences require engine special-casing (rather than data parameters),
  Custody Management's stated uniform behavior across vignettes is violated — this risk is named
  explicitly in [DOM-009](../domains/DOM-009-doctrine-development-framework.md) §4.
- Fusion output introducing a second, parallel confidence representation (rather than layering on
  FS-103's existing display) would create a conflicting confidence indicator, violating [R119](../research/encyclopedia/R119-space-situational-data-fusion.md) §5's
  stated constraint.

## Open Questions

- No FR-xxxx/NFR-xxxx in `docs/requirements/` explicitly cites FS-104; this is a traceability gap
  for Phase 8 review (MSTR-006 §7), not a deliberate non-applicability.
- The source document does not assign a per-subsystem Subsystem Responsibilities table.
- The source document does not address Data Model Changes beyond referencing existing SSN dispersion
  preset structures.
- The source document does not address Security Considerations for coalition vs. national SSN
  affiliation from an access-control perspective.
- The source document does not state formal Verification Methods per criterion.

## Related ADRs

ADR-0010 (mock SSN is internal, not external) —
`docs/architecture/adr/ADR-0010-mock-ssn-internal.md`.

## Related Interfaces

INT-0009 (CellController/SessionAPI → Mock SSN); INT-0010 (Mock SSN → Simulation Engine
Scheduler/EventLog/Custody, delivery) — per `docs/design/05-interface-control-document.md`.
