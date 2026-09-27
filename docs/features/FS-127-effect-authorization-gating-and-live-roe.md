> **Document ID:** FS-127
> **Version:** 1.0
> **Status:** ✅ Ready for implementation planning — one Open Question (shared effect-classification
> taxonomy with `FS-129`) should be confirmed jointly before either Feature's Implementation Package
> is written
> **Note on this repository's chain:** no `05-feature-decomposition` Feature Catalog exists here
> (per this skill's own Gotchas); this document's approved input is the just-baselined requirements
> themselves — `docs/requirements/01-functional-requirements.md` `FR-3430`, `FR-3440` — plus the
> real baseline code they extend (`engine/orders.py`, `session/manager.py`).
> **Dependencies:** [FS-116](FS-116-role-scoped-command-catalog.md) (`FR-4210` roles — the seat/role
> concept `FR-3430`'s designated-controller-role approval reuses), [FS-129](FS-129-jamming-delivery-and-effect-detectability.md)
> (shares one open effect-classification-taxonomy question with this Feature, `BL-0105`)
> **Referenced By:** [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0076` (item B10),
> `BL-0105` (the shared-taxonomy consistency note),
> [docs/requirements/01-functional-requirements.md](../requirements/01-functional-requirements.md)
> `FR-3430`, `FR-3440`
> **Produces:** an optional per-effect-type controller-role approval workflow (`FR-3430`) and a
> live, logged mid-session ROE-flag-change mechanism (`FR-3440`), satisfying both in full
> **Feature Mapping:** FS-127 (this document)
> **Related Topics:** [FS-129](FS-129-jamming-delivery-and-effect-detectability.md) (per-effect-class
> detectability/attribution settings — shares the same effect-type/reversibility-category
> classification scheme, `BL-0105`)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template.*

# FS-127 — Optional Effect-Authorization Gating and Live Rules-of-Engagement Changes

## Purpose

Add two related controller-authority capabilities the baseline lacks: an optional approval
workflow gating a declared effect type/reversibility category on a designated controller role's
decision before it executes (`FR-3430`), and a way for that same role to change a cell's ROE flags
mid-session, logged so replay stays deterministic (`FR-3440`). `FR-3430`'s Rationale states the gap
directly: the baseline enforces only fixed per-cell ROE flags (`FR-3420`), with jamming not gated at
all and no approval-workflow concept for any effect type.

## Scope

**In scope:** a vignette-declared gating rule (effect type/reversibility category → required
controller role) that an order matching it must clear before executing, with the request/decision/
elapsed-time logged (`FR-3430`); a controller-issued ROE-flag change during a running session,
logged as an ordinary `EventLog` entry for deterministic replay (`FR-3440`).

**Out of scope (named, not silently absorbed):** the specific effect-type/reversibility-category
taxonomy both this Feature and `FS-129` key off — confirming both cite the same enumeration is a
joint Open Question (Open Question 1), not decided unilaterally here; any change to `FR-3420`'s
existing per-cell static ROE mechanism beyond making it live-changeable (`FR-3440` is additive to
`FR-3420`, not a replacement).

## Requirements Implemented

- `FR-3430` — Optional per-effect-type controller-role authorization gating.
- `FR-3440` — Live, logged mid-session Rules-of-Engagement changes.

## User Workflows

1. **White Cell declares a gating rule in a vignette.** The vignette names an effect type and/or
   reversibility category and a required controller role (per `FR-4210`'s existing role concept).
2. **An operator issues an order matching a gated rule.** The order does not execute immediately;
   an approval request is recorded, and the order awaits the designated controller role's decision.
3. **The designated controller reviews and decides.** The controller (holding that role) approves or
   denies; the decision and the elapsed time since the request are both recorded.
4. **A designated controller changes a cell's ROE flags mid-session.** The change (kinetic, cyber, or
   any per-effect-type gating rule from `FR-3430`) takes effect from the simulated time of the
   change, logged as an `EventLog` entry.
5. **Facilitator/analyst replays the exercise.** Replaying the identical
   `(initial_state, ordered eventlog, seed)` reproduces the identical sequence of ROE states at the
   identical simulated times (`FR-3440`'s own Postcondition).

## System Behaviour

- **Normal path — `FR-3430`.** An order matching a declared gating rule is held pending until the
  designated controller role records a decision; an order with no matching rule is unaffected,
  executing per its existing gates (`FR-3420`, `FR-3410`).
- **Normal path — `FR-3440`.** A controller-issued ROE-flag change is recorded as an `EventLog`
  entry effective from its simulated time; an order issued before that time is evaluated under the
  prior value, one issued after under the new value.
- **Edge case — `FR-3430`, no matching gating rule declared.** The order executes per its existing
  gates, unaffected (`FR-3430`'s own Preconditions).
- **Edge case — `FR-3430`, a pending order awaiting decision when the session ends/rewinds.** Not
  addressed by `FR-3430`'s own text (Open Question 2).
- **Determinism — `FR-3440`.** Replaying the identical event log reproduces the identical ROE-state
  sequence, per `FR-3440`'s own Postcondition and `ADR-0002`.

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `content/vignette.py` | Owns the vignette-declared gating-rule schema (effect type/reversibility category → required controller role), additive to the existing `roe` block (`FR-3420`/`ADR-0035`-era shape). |
| `engine/orders.py` (`OrderSystem`) | Owns holding a gated order pending a decision, and resolving the per-cell ROE flag (`FR-3420`'s existing mechanism) against a live-changed value (`FR-3440`) rather than only the vignette-declared static one. |
| `session/manager.py` | Owns recording the approval request/decision/elapsed-time (`FR-3430`) and the live ROE-change event (`FR-3440`) into the `EventLog`, and resolving `FR-4210`'s existing role concept against the designated-controller check. |
| Operator Console (`ui_web/`) | Presents the pending-approval surface to the designated controller role, and the ROE-flag-change control to that same role. |

## Interfaces Used

- `INT-0002` (White Cell ↔ Console exercise control) — the existing interface both the approval-
  decision surface and the ROE-flag-change control operate through, consistent with `FR-4720`'s
  existing live-parameter-adjustment precedent.
- `INT-0008` (SessionManager → Engine Clock/Scheduler/EventLog/OrderSystem) — the existing interface
  both the gated-order hold/release and the ROE-change `EventLog` entry operate through.

## Data Model Changes

- The vignette's existing `roe` schema (`FR-3420`/`ADR-0035`) gains an additive gating-rule field
  (effect type/reversibility category → required controller role) for `FR-3430`.
- A new `EventLog` entry shape for a live ROE-flag change (`FR-3440`), additive — no existing entry
  shape is altered.
- No new top-level entity for the approval workflow itself — a pending/decided approval is tracked
  as `EventLog` entries (request, decision), consistent with the project's existing "the log is the
  record" pattern (`NFR-2600`).

## State Changes

- A gated order transitions from pending-approval to either executing (approved) or rejected
  (denied) — an additive state on top of the existing `Order.status` values (`queued`/`rejected`/
  `cancelled`), per `FR-3430`.
- A cell's effective ROE value transitions at the simulated time of a live change (`FR-3440`),
  read by `FR-3420`'s existing per-cell resolution mechanism as a time-varying value rather than a
  single fixed one.

## Error Handling

- An order matching a gated rule with no controller decision yet: held pending, not executed and
  not rejected outright — `FR-3430`'s own Postconditions.
- A pending order at session end/rewind (Open Question 2): not addressed.
- A ROE-change request from an operator not holding the designated controller role: rejected,
  consistent with every other role-gated action in this project (`FR-4210`'s existing pattern).

## Performance Considerations

None named by `FR-3430`/`FR-3440` — both are bounded, per-order or per-change operations, not a new
computational class.

## Security Considerations

- `NFR-2600` (complete, ordered, timestamped action log) already covers the logging obligation both
  leaves' own Postconditions restate — no new NFR needed (per the Should-tier batch's own Review,
  Finding in `docs/reviews/requirements-update-should-tier-batch.md` §1).
- `FR-4210` (roles) is the trust boundary both leaves depend on: only an operator holding the
  designated controller role may decide a gated order or change ROE flags — an Implementation
  Package must not let any other role perform either action.

## Acceptance Criteria

1. Given a gated effect type and a pending order of that type, the order does not execute until the
   designated controller role records an approval decision; the `EventLog` shows the request, the
   decision, and the elapsed time between them. *(`FR-3430`)*
2. Given a controller-issued ROE change at simulated time T, an order issued by the affected cell
   before T is evaluated under the prior ROE value and one issued after T under the new value;
   replaying the session reproduces this identically. *(`FR-3440`)*

## Verification Plan

- Criterion 1 — Test: a gated effect type's order held pending; assert no execution until a decision
  is recorded; assert the `EventLog` carries request/decision/elapsed-time.
- Criterion 2 — Test: a live ROE change at a known simulated time; orders issued before and after;
  assert each evaluates under the correct value; replay and diff for byte identity.

## Dependencies

`FR-3420` (per-cell independent ROE, unchanged base mechanism), `FR-4210` (roles, the controller
trust boundary), `FR-7110` (event log, the recording mechanism both leaves reuse).

## Risks

- **Ambiguity risk (Open Questions 1-2 below).**
- **Shared-taxonomy risk with `FS-129` (Open Question 1).** If this Feature's gating-rule
  classification and `FS-129`'s detectability-settings classification are implemented as two
  independent enumerations rather than one shared one, a future vignette author configuring both
  could see inconsistent effect-type/reversibility-category behavior between the two mechanisms.

## Open Questions

1. **Do `FR-3430` (this Feature) and `FR-1450` (`FS-129`) consume the same effect-type/
   reversibility-category enumeration, or two independent ones?** Both requirements key off "an
   effect's type and/or its five-D's reversibility category" for two different purposes (an approval
   workflow vs. a detectability/attribution model). Neither requirement's own text commits to a
   shared enumeration explicitly. Per `docs/pipeline/backlog.md` `BL-0105`'s own routing: confirm
   during `07-implementation-planning` (whichever of this Feature/`FS-129` is implemented first)
   that both consume one shared enumeration, rather than each defining its own — this document does
   not invent the enumeration itself.
2. **What happens to a pending-approval order when the session ends or is rewound before a decision
   is recorded?** Neither `FR-3430`'s own text nor any related requirement addresses this. Needs a
   `07-implementation-planning` design decision — this document does not invent one.

## Related ADRs

`ADR-0002` (deterministic core — `FR-3440`'s replay-reproducibility Postcondition); `ADR-0005`
(plan-first commanding — `FR-3430`'s hold-pending-approval mechanism is consistent with, not a
violation of, plan-first commanding: the order is still planned first, only its execution gate is
new).

## Related Interfaces

None beyond `INT-0002`/`INT-0008` already cited under Interfaces Used.
