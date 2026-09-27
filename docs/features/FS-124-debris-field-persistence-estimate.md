> **Document ID:** FS-124
> **Version:** 1.0
> **Status:** ✅ Ready for implementation planning
> **Note on this repository's chain:** no `05-feature-decomposition` Feature Catalog exists here
> (per this skill's own Gotchas); this document's approved input is the just-baselined requirement
> itself — `docs/requirements/01-functional-requirements.md` `FR-1430` — plus
> [`R117` v1.2](../research/encyclopedia/R117-directed-energy-and-kinetic-effects.md) §3.1 and the
> real baseline code it extends (`engine/effects.py`, the `DebrisField` concept named in
> `docs/FUTURE-WORK.md` §13 R16/GAP-02).
> **Dependencies:** None (this Feature is additive, presentational-only, and touches no other
> Feature's own scope)
> **Referenced By:** [IP-1240](../implementation/packages/IP-1240-debris-field-persistence-estimate.md)
> (Implementation Package, `READY`, not yet authorized),
> [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0077` (item B11),
> [docs/requirements/01-functional-requirements.md](../requirements/01-functional-requirements.md)
> `FR-1430`, Candidate Requirement `CR-17` (this Feature is deliberately narrower than, not a
> promotion of)
> **Produces:** an estimated, altitude-derived persistence figure attached to every `DebrisField`,
> satisfying `FR-1430` in full
> **Feature Mapping:** FS-124 (this document)
> **Related Topics:** [FS-123](FS-123-space-weather-index-coupling.md) (`FR-1230`'s drag coupling —
> a related but independent altitude/decay concept this Feature's persistence estimate should stay
> consistent with in order of magnitude, per `FR-1430`'s own `FR-1230` Dependency)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template.*

# FS-124 — Debris-Field Persistence Estimate by Altitude

## Purpose

Show players and facilitator an estimated persistence figure for any spawned debris field, derived
from its altitude, so a destructive-effect or `spawn_debris` inject decision carries a visible,
realistic consequence signal — without building the fuller, deferred mechanism (persistent debris
that gates future Access Windows) `docs/FUTURE-WORK.md` §13 R16/GAP-02 and Candidate Requirement
`CR-17` still describe. `FR-1430`'s own Rationale states this distinction directly: this Feature is
**deliberately narrower** than `CR-17`.

## Scope

**In scope:** computing an altitude-derived `persistence_estimate` for each `DebrisField` at
creation time; displaying that figure wherever the field itself is already shown to a player or
facilitator.

**Out of scope (named, not silently absorbed):** any change to Access Window computation
(`FR-1220`) or conjunction-screening behavior as a consequence of the estimate — `FR-1430`'s own
Postcondition states explicitly that the estimate must not gate either; the fuller persistent-debris
environment layer `CR-17` describes remains unbaselined and untouched by this Feature.

## Requirements Implemented

- `FR-1430` — Debris-field persistence estimate by altitude.

## User Workflows

1. **A destructive effect or a `spawn_debris` inject creates a `DebrisField`.** The system computes
   the field's `persistence_estimate` from its altitude at creation time, alongside whatever other
   `DebrisField` attributes already exist.
2. **A player or facilitator views the debris field** (wherever it is already rendered — map/globe,
   conjunction-screening list, or equivalent existing surface). The persistence estimate is shown
   alongside it, with no additional interaction required.

## System Behaviour

- **Normal path.** At `DebrisField` creation, the field's altitude is read and a `persistence_estimate`
  is computed and attached; the existing rendering surface(s) display it without further
  computation on each subsequent read.
- **Edge case — altitude not determinable at creation time.** Not addressed by `FR-1430`'s own text
  (Open Question 1) — this is a narrow case (every destructive effect/`spawn_debris` inject that
  reaches `DebrisField` creation already has a resulting orbital state, so this may be
  vacuous, but the requirement itself does not state so explicitly).
- **Invariant — no gating consequence.** The estimate never changes Access Window computation
  (`FR-1220`) or conjunction-screening outcomes — `FR-1430`'s own Postcondition, and the boundary
  this Feature must not cross even if a future Implementation Package finds it tempting to wire the
  two together.

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `engine/effects.py` | Owns `DebrisField` creation (from a destructive `EffectInstance` or a `spawn_debris` inject effect); computes and attaches `persistence_estimate` at creation time. |
| Operator Console (`ui_web/`) | Displays `persistence_estimate` wherever a `DebrisField` is already rendered — no new rendering surface, an additional field on an existing one. |

## Interfaces Used

- `INT-0008` (SessionManager → Engine Clock/Scheduler/EventLog/OrderSystem) — the existing interface
  `DebrisField` creation already operates through; no new interface.

## Data Model Changes

`DebrisField` (the entity named in `docs/FUTURE-WORK.md` §13 R16/GAP-02, produced by
`engine/effects.py`) gains a `persistence_estimate` attribute, additive, computed once at creation
time from the field's altitude. No other entity changes.

## State Changes

None beyond the additive `persistence_estimate` attribute on each newly created `DebrisField` —
read-only after creation, not a runtime-mutable value.

## Error Handling

None named beyond Open Question 1 (altitude-not-determinable edge case) — every other path is a
straightforward computed-attribute attachment with no failure mode `FR-1430`'s own text implies.

## Performance Considerations

None named by `FR-1430` — a single computed value attached once per `DebrisField` creation, not a
per-tick or per-read computation.

## Security Considerations

None — this Feature introduces no new trust boundary; the estimate is derived from ground-truth
state already visible wherever a `DebrisField` is shown today (consistent with existing debris
visibility, unaffected by this Feature).

## Acceptance Criteria

1. Given two `DebrisField`s created at different altitudes, the lower-altitude field's
   `persistence_estimate` is shorter than the higher-altitude field's. *(`FR-1430`)*
2. Neither field's `persistence_estimate` changes either field's effect on Access Window
   computation or conjunction-screening outcome. *(`FR-1430`)*

## Verification Plan

- Criterion 1 — Test: two destructive effects (or `spawn_debris` injects) at different altitudes;
  compare the resulting fields' `persistence_estimate` values.
- Criterion 2 — Test: before/after comparison of Access Window computation and conjunction-screening
  behavior for an Asset near a `DebrisField`, with and without the estimate present, asserting no
  difference.

## Dependencies

`FR-1230` (space-weather-index-driven LEO drag coupling, `FS-123`) — a related, independent
altitude/decay concept `FR-1430`'s own Dependencies field names; this Feature's estimate should stay
consistent in order of magnitude, not literally computed from `FR-1230`'s runtime drag term (the two
remain separate computations per each FR's own scope).

## Risks

- **Ambiguity risk (Open Question 1 below).** A narrow, likely-vacuous edge case, low risk to
  implementation readiness.
- **Scope-creep risk (named explicitly, mitigated by this document's own Scope section).** The
  temptation to wire the estimate into Access Window/conjunction-screening gating (the fuller `CR-17`
  mechanism) is real given how closely related the two concepts are — an Implementation Package must
  not cross this boundary without a separate, future requirements/architecture pass explicitly
  authorizing it.

## Open Questions

1. **Is there any real path where a `DebrisField`'s altitude is not determinable at creation time?**
   `FR-1430`'s own Preconditions require a determinable altitude but do not state what happens if
   one somehow isn't available. Likely vacuous (every creation path already has a resulting orbital
   state), but not stated as settled fact by the requirement's own text. Needs a
   `07-implementation-planning` confirmation against the live `engine/effects.py` code, not invented
   here.

## Related ADRs

None directly — this Feature is an informational estimate, not a new engine mechanism or effect
category, per `FR-1430`'s own Related ADRs field.

## Related Interfaces

None beyond `INT-0008` already cited under Interfaces Used.
