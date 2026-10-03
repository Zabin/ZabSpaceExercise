> **Document ID:** FS-128
> **Version:** 1.0
> **Status:** ✅ Ready for implementation planning
> **Note on this repository's chain:** no `05-feature-decomposition` Feature Catalog exists here
> (per this skill's own Gotchas); this document's approved input is the just-baselined requirement
> itself — `docs/requirements/01-functional-requirements.md` `FR-7330` — plus the real baseline
> code it extends (`session/aar.py`).
> **Dependencies:** [FS-107](FS-107-after-action-review.md) (After Action Review — the point-in-time
> reconstruction mechanism this Feature's continuous playback is additive to)
> **Referenced By:** [IP-1280](../implementation/packages/IP-1280-variable-speed-aar-replay.md)
> (Implementation Package, `READY`, not yet authorized),
> [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0078` (item B12),
> `BL-0093` (the `INT-0014` interface-stretch note, now covering this Feature's own stretch too),
> [docs/requirements/01-functional-requirements.md](../requirements/01-functional-requirements.md)
> `FR-7330`, `docs/FUTURE-WORK.md` §13 R10 (belief-vs-truth analytics, adjacent)
> **Produces:** variable-speed timeline playback from ground truth or a single cell's fog-respecting
> viewpoint, satisfying `FR-7330` in full
> **Feature Mapping:** FS-128 (this document)
> **Related Topics:** [FS-121](FS-121-ephemeris-export.md) (Ephemeris Export — a sibling
> `INT-0014`-stretching capability from the same requirements batch)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template.*

# FS-128 — Variable-Speed AAR Replay from Truth or a Single Cell's Viewpoint

## Purpose

Let a facilitator or analyst play back a recorded exercise's timeline at a configurable speed, from
ground truth or from a single named cell's fog-of-war-respecting viewpoint — additive to the
existing point-in-time reconstruction `FR-7310` already provides, which has no continuous
variable-speed mode or per-cell-viewpoint presentation.

## Scope

**In scope:** continuous timeline playback at a requested, configurable speed; a requested viewpoint
of either ground truth or one named participating cell.

**Out of scope (named, not silently absorbed):** any change to `FR-7310`'s own point-in-time
reconstruction (`state_at`/`state_at_time`) — this Feature is additive to it, reusing the same
reconstruction mechanism at successive moments, not a replacement; branch comparison (`FR-7320`,
unchanged).

## Requirements Implemented

- `FR-7330` — Variable-speed AAR replay from truth or a single cell's viewpoint.

## User Workflows

1. **Facilitator/analyst opens AAR replay for a recorded exercise.** They choose a playback speed and
   a viewpoint: ground truth, or one of the exercise's participating cells.
2. **The system plays back the timeline.** Reconstructed state advances continuously at the chosen
   speed, filtered to the chosen viewpoint.
3. **The facilitator/analyst pauses, changes speed, or switches viewpoint mid-playback.** The
   playback continues from the current point at the newly chosen speed/viewpoint.

## System Behaviour

- **Normal path — ground-truth viewpoint.** The played-back state at any moment matches `FR-6220`'s
  no-cell ground-truth view at that simulated time.
- **Normal path — cell viewpoint.** The played-back state at any moment matches what `FR-6210`'s
  fog-of-war filter would produce for that cell at that simulated time — never ground truth
  presented as that cell's belief (`FR-7330`'s own Postcondition, explicit).
- **Edge case — playback at a non-default speed.** Does not disturb the live session, reusing
  `FR-7310`'s existing non-disturbance guarantee (`FR-7330`'s own Acceptance Criteria).
- **Edge case — mid-playback viewpoint switch.** Not addressed by `FR-7330`'s own text beyond
  "a requested viewpoint" being an input at any point (Open Question 1).

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `session/aar.py` | Owns `state_at`/`state_at_time` (`FR-7310`) this Feature's continuous playback calls repeatedly at successive simulated times; extended with the playback-speed/viewpoint request handling. |
| `session/cells.py` (`CellController`) | Owns the fog-of-war filter (`FR-6210`) the cell-viewpoint playback path must call at each played-back moment — reused, not reimplemented. |
| Operator Console (`ui_web/`) | Presents the playback control (speed, viewpoint selection, pause). |

## Interfaces Used

- `INT-0014` (AAR/Replay → Engine) — the existing interface `FR-7310`'s point-in-time reconstruction
  already operates through; this Feature stretches its documented shape a second way (continuous,
  per-cell-viewpoint playback, distinct from `FR-7410`/`FR-7420`'s own export-format/frame stretch),
  per `docs/pipeline/backlog.md` `BL-0093`'s extended entry — not a new finding, folded into the
  same tracked interface-model note.
- `INT-0006` (Console → SessionAPI seam) — the existing interface the playback control operates
  through.

## Data Model Changes

None — this Feature reads the existing recorded `EventLog`/`WorldState` history via `FR-7310`'s
existing reconstruction mechanism; no new persisted entity.

## State Changes

None to session/persistent engine state — playback is a read-only operation over a recorded
exercise, reusing `FR-7310`'s existing non-disturbance guarantee.

## Error Handling

- A requested cell viewpoint naming a cell that did not participate in the recorded exercise: not
  addressed by `FR-7330`'s own text (Open Question 2).
- A requested playback speed outside a sane bound: not addressed by `FR-7330`'s own text (not
  flagged as an Open Question — no numeric bound is implied by any source document, consistent with
  the Should-tier batch's Review not manufacturing an NFR target where none exists).

## Performance Considerations

None named by `FR-7330` — continuous playback is a bounded, repeated invocation of `FR-7310`'s
existing reconstruction at successive moments, not a new computational class.

## Security Considerations

`ADR-0004` (fog-of-war at the boundary): a cell-viewpoint playback must never present ground truth
as that cell's own belief — `FR-7330`'s own Postcondition, and this Feature's central security
constraint.

## Acceptance Criteria

1. Given a recorded exercise and a requested cell viewpoint, the played-back state at any moment
   matches what `FR-6210`'s fog-of-war filter would produce for that cell at that simulated time.
   *(`FR-7330`)*
2. Given a requested ground-truth viewpoint, the played-back state at any moment matches `FR-6220`'s
   no-cell ground-truth view. *(`FR-7330`)*
3. Playing back at a non-default speed does not disturb the live session. *(`FR-7330`, `FR-7310`)*

## Verification Plan

- Criterion 1 — Test: play back a recorded exercise with a known fog-of-war-filtered history for one
  cell; assert the played-back state matches at several sampled moments.
- Criterion 2 — Test: play back the same exercise with the ground-truth viewpoint; assert the
  played-back state matches `FR-6220`'s view at the same moments.
- Criterion 3 — Test: play back at a non-default speed while the live session continues in parallel;
  assert the live session's own state is unaffected.

## Dependencies

`FR-7310` (read-only replay/scrub, the reconstruction mechanism this Feature calls repeatedly),
`FR-6210`/`FR-6220` (the fog-of-war/ground-truth views this Feature's two playback modes must
reproduce exactly).

## Risks

- **Ambiguity risk (Open Questions 1-2 below).**
- **`INT-0014` interface-stretch, already tracked (`BL-0093`).** Not a new risk this Feature
  introduces — folded into the existing tracked finding rather than filed separately.

## Open Questions

1. **What is the observable behavior of a mid-playback viewpoint switch?** Does playback continue
   from the same simulated moment under the new viewpoint, or restart? `FR-7330`'s own text does not
   state this. Needs a `07-implementation-planning` design decision — this document does not invent
   one.
2. **What is the observable behavior of a requested cell viewpoint naming a cell that did not
   participate in the recorded exercise?** Not addressed by `FR-7330`'s own text. Needs a
   `07-implementation-planning` design decision — this document does not invent one.

## Related ADRs

`ADR-0002` (deterministic core — the reconstruction mechanism this Feature repeatedly invokes is
itself deterministic replay); `ADR-0004` (fog-of-war at the boundary — this Feature's central
security constraint).

## Related Interfaces

None beyond `INT-0006`/`INT-0014` already cited under Interfaces Used.
