> **Document ID:** FS-129
> **Version:** 1.0
> **Status:** ✅ Ready for implementation planning — one Open Question (shared effect-classification
> taxonomy with `FS-127`) should be confirmed jointly before either Feature's Implementation Package
> is written
> **Note on this repository's chain:** no `05-feature-decomposition` Feature Catalog exists here
> (per this skill's own Gotchas); this document's approved input is the just-baselined requirements
> themselves — `docs/requirements/01-functional-requirements.md` `FR-1440`, `FR-1450` — plus the
> real baseline code they extend (`engine/effects.py`, `engine/orders.py`).
> **Dependencies:** [FS-105](FS-105-spacecraft-operations.md) (Spacecraft Operations — the
> command-delivery path `FR-1440` degrades), [FS-127](FS-127-effect-authorization-gating-and-live-roe.md)
> (shares one open effect-classification-taxonomy question with this Feature, `BL-0105`)
> **Referenced By:** [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0081` (item B15),
> `BL-0105` (the shared-taxonomy consistency note),
> [docs/requirements/01-functional-requirements.md](../requirements/01-functional-requirements.md)
> `FR-1440`, `FR-1450`
> **Produces:** command/relay delivery-path degradation from a successful jam effect (`FR-1440`)
> and per-effect-class detectability/attribution-difficulty configuration (`FR-1450`), satisfying
> both in full
> **Feature Mapping:** FS-129 (this document)
> **Related Topics:** [FS-127](FS-127-effect-authorization-gating-and-live-roe.md) (shares the same
> effect-type/reversibility-category classification scheme, `BL-0105`)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template.*

# FS-129 — Jamming-Delivery Degradation and Per-Effect-Class Detectability Settings

## Purpose

Extend jamming's consequences beyond the baseline's telemetry-signature-only model to also degrade
command/relay delivery (`FR-1440`), and let each effect class carry its own configurable
detectability/attribution-difficulty setting rather than one fixed global value (`FR-1450`).
`FR-1440`'s own Rationale states the gap directly: `engine/effects.py`'s `is_link_denied` already
models a denied-link concept the delivery path (stored/ISL delivery, `FR-3110`) does not yet consult
for the jam effect category specifically.

## Scope

**In scope:** a successful uplink/crosslink jam causing a planned command routed through the jammed
link to fail delivery or be delayed, in addition to its existing telemetry-signature effect
(`FR-1440`); a per-effect-class (type and/or reversibility category) configurable
detectability/attribution-difficulty setting consulted at effect resolution (`FR-1450`).

**Out of scope (named, not silently absorbed):** the effect-type/reversibility-category taxonomy
itself, shared with `FS-127`'s `FR-3430` — confirming both cite the same enumeration is a joint Open
Question (Open Question 1), not decided unilaterally here; any change to jamming's existing
telemetry-signature effect (`FR-1440` is additive to it, not a replacement).

## Requirements Implemented

- `FR-1440` — Uplink/crosslink jamming degrades command and relay delivery paths.
- `FR-1450` — Per-effect-class detectability and attribution-difficulty configuration.

## User Workflows

1. **An operator issues a jam order against an uplink or crosslink.** The order resolves exactly as
   today (`FR-1410`), producing its existing telemetry-signature effect.
2. **A different operator (potentially a different cell) has a command scheduled for delivery
   through the jammed link at execute-time re-validation.** If the jam effect's footprint covers the
   command's delivery path at that moment, the command fails delivery or is delayed.
3. **White Cell declares per-effect-class detectability/attribution settings in a vignette.** Each
   named effect class (by type and/or reversibility category) carries its own configured values,
   consulted whenever an effect of that class resolves.

## System Behaviour

- **Normal path — `FR-1440`.** A planned command's execute-time re-validation (`FR-3410`) checks
  whether an active, successfully resolved jam effect's footprint covers its delivery path at the
  scheduled execution time; if so, the delivery fails or is delayed, recorded in the `EventLog`.
- **Edge case — `FR-1440`, no active jam covering the delivery path.** The command executes normally,
  unaffected (`FR-1440`'s own Postconditions).
- **Normal path — `FR-1450`.** An effect's detection/attribution outcome is computed using its own
  effect-class's configured setting where one is declared; where none is declared, the existing
  single fixed setting `FR-1410` already provides applies (`FR-1450`'s own Preconditions).

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `engine/effects.py` | Owns `is_link_denied` and the five-D's effect-resolution mechanism (`FR-1410`); extended so a jam effect's resolution is consulted by the delivery-path check (`FR-1440`) and so per-effect-class detectability/attribution settings are read where declared (`FR-1450`). |
| `engine/orders.py` (`OrderSystem`) | Owns `FR-3410`'s execute-time re-validation; extended to consult `is_link_denied`/the active-jam-footprint check for a command's delivery path. |
| `content/vignette.py` | Owns the vignette-declared per-effect-class detectability/attribution configuration schema (`FR-1450`), additive. |

## Interfaces Used

- `INT-0008` (SessionManager → Engine Clock/Scheduler/EventLog/OrderSystem) — the existing interface
  both the delivery-path check (`FR-1440`) and the per-class detectability read (`FR-1450`) operate
  through; no new interface, per `FR-1440`'s own citation of `ADR-0011`'s existing six-channel model.

## Data Model Changes

- No new access channel — `FR-1440` extends the existing `command_uplink` channel's consequence set,
  per `ADR-0011`.
- The vignette's existing effect-template data gains an additive per-effect-class detectability/
  attribution-difficulty field (`FR-1450`), keyed by effect type and/or reversibility category —
  shared enumeration with `FS-127`'s `FR-3430` pending Open Question 1's resolution.

## State Changes

None new — a jam effect's active/footprint state is already tracked by the existing effect-
resolution mechanism; `FR-1440` only adds a consequence check against it, not a new state.

## Error Handling

- A command whose delivery path is not covered by an active jam: unaffected, per `FR-1440`'s own
  Postconditions.
- An effect class with no declared detectability/attribution setting: falls back to the existing
  single fixed setting, per `FR-1450`'s own Preconditions — not an error, the documented default
  path.

## Performance Considerations

None named by `FR-1440`/`FR-1450` — both are bounded, per-order or per-effect-resolution checks, not
a new computational class.

## Security Considerations

None new — this Feature extends existing effect-resolution/delivery-path mechanisms within their
existing trust boundaries; no new cross-cell read path is introduced.

## Acceptance Criteria

1. Given an active uplink jam covering a command's delivery path at its scheduled execution time,
   the command fails or is delayed at execute-time re-validation; given no active jam on that path,
   the same command executes normally. *(`FR-1440`)*
2. Given two effect classes with differently configured detectability/attribution-difficulty
   settings, resolving one instance of each produces detection/attribution outcomes consistent with
   each class's own configured setting, not a shared default. *(`FR-1450`)*

## Verification Plan

- Criterion 1 — Test: an active jam covering, and separately not covering, a command's delivery path
  at execution time; assert the corresponding outcome.
- Criterion 2 — Test: two effect classes with distinct configured settings; assert each resolves
  detection/attribution independently of the other.

## Dependencies

`FR-1410` (five-D's effect resolution, the base mechanism both leaves extend), `FR-3410`
(execute-time re-validation, the delivery-path check's host), `FR-3110` (plan-first delivery path,
unchanged mechanism this Feature's check consults).

## Risks

- **Shared-taxonomy risk with `FS-127` (Open Question 1).** Same risk named in `FS-127`'s own Risks
  section — implementing two independent enumerations rather than one shared one would let the two
  mechanisms drift apart for the same effect class.

## Open Questions

1. **Do `FR-1450` (this Feature) and `FR-3430` (`FS-127`) consume the same effect-type/
   reversibility-category enumeration, or two independent ones?** Identical question to `FS-127`'s
   own Open Question 1 — stated here as well since it affects this Feature's own Implementation
   Package equally. Per `docs/pipeline/backlog.md` `BL-0105`'s own routing: confirm during
   `07-implementation-planning` (whichever of this Feature/`FS-127` is implemented first) that both
   consume one shared enumeration — this document does not invent the enumeration itself.

## Related ADRs

`ADR-0011` (six access channels taxonomy — `FR-1440` extends, does not replace, the existing
`command_uplink` channel's consequence set).

## Related Interfaces

None beyond `INT-0008` already cited under Interfaces Used.
