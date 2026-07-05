# FS-116 — Role-Scoped Command Catalog & Assignment Scoping

> **Document ID:** FS-116
> **Version:** 1.1
> **Status:** ✅ Ready for implementation planning (both Open Questions closed — see below)
> **Dependencies:** [FS-115](FS-115-session-setup.md) (produces the Role Assignment record this
> Feature enforces, `FR-4210`), [FS-105](FS-105-spacecraft-operations.md) (the bus/payload command
> catalog — `BUS_VERBS`/`PAYLOAD_VERBS`/`DEFENSE_VERBS` — this Feature filters/enforces against),
> [ADS-3500](../architecture/ADS-3500-role-scoped-command-enforcement.md) (resolves both Open
> Questions this document's v1.0 could not — the seat-identifier interface amendment and the
> `DEFENSE_VERBS` role-scope classification)
> **Referenced By:** [docs/feature-planning/03-feature-catalog.md](../feature-planning/03-feature-catalog.md)
> `FEAT-3500`, [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0049`/`BL-0014`,
> [release-assessment-fs-tracked-baseline.md](../reviews/release-assessment-fs-tracked-baseline.md)
> Finding 2 (the release-readiness audit that surfaced this Feature had zero owning spec and zero
> implementation), [IP-1160](../implementation/packages/IP-1160-role-scoped-command-enforcement.md)
> (the Implementation Package planned against this spec)
> **Produces:** the enforcement layer `FS-105`'s bus/payload command catalog and `FS-115`'s Role
> Assignment record need to actually gate command legality by seated role, not merely by asset
> capability/ownership
> **Feature Mapping:** FS-116 (this document)
> **Related Topics:** [FS-113](FS-113-observer-read-only-access.md) (a structurally similar
> "reject an out-of-scope mutating request server-side, not merely hide it in the UI" pattern, at
> the cell level rather than the role level)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template. It is a **new**
Feature Specification closing the gap `11-release-readiness`'s
[release assessment](../reviews/release-assessment-fs-tracked-baseline.md) found: `FEAT-3500`
(Role-Scoped Command Catalog & Assignment Scoping) is a Must-priority Feature bucketed in Release 1
per `docs/feature-planning/01-release-plan.md`, with two Must-priority requirements (`FR-3510`,
`FR-3520`) — and until this document, it had no owning Feature Specification anywhere in the corpus
and no implementation anywhere in `spacesim/`. That absence was flagged once before as `BL-0014`
(Medium, filed 2026-07-03 during `IP-1151`'s implementation, re-derived independently at `IP-1151`'s
verification) but not recognized as release-blocking until the readiness audit specifically checked
"is every planned Feature actually delivered." The project owner authorized closing this gap via the
full `06`→`07`→`08`→`09` pipeline (Path A) rather than descoping the Feature.*

*v1.1 (this revision): v1.0's two Open Questions blocked implementation-readiness; the project owner
routed both upstream to `03-architecture-design-synthesis` rather than have this skill or
`07-implementation-planning` improvise an answer.
[ADS-3500](../architecture/ADS-3500-role-scoped-command-enforcement.md) resolved both. This revision
updates every field their resolutions affect; fields the resolutions did not touch are unchanged
from v1.0.*

## Feature ID

FS-116

## Title

Role-Scoped Command Catalog & Assignment Scoping

## Purpose

Ensure an operator only ever sees, and can only ever execute, commands legal for their seated role
(bus/payload/both) and assigned Asset — per `docs/feature-planning/03-feature-catalog.md`
`FEAT-3500`'s own Purpose field, carried forward verbatim.

## Scope

In scope: filtering the order/command interface to the commands legal for the operator's seated
role and targeted Asset (`FR-3510`); independently enforcing a Role Assignment's bus-only/
payload-only/both scope as a system behavior at command-execution time, not merely as a UI filter,
so a command outside scope is rejected even if it bypassed the order panel entirely (`FR-3520`).

Out of scope, per the Feature Catalog's own `Excluded Requirements`/`Scope` fields: creating or
editing a Role Assignment itself (`FR-4210` — `FEAT-4200`/[FS-115](FS-115-session-setup.md), already
`VERIFIED`); the physical/asset-capability legality checks a command must also pass regardless of
role (`can_issue()`'s existing payload-type/bus-health/Δv gates in
[FS-105](FS-105-spacecraft-operations.md), unaffected by this Feature — role-scope is an *additional*
gate, not a replacement for the existing one); cell-level fog-of-war filtering (Blue/Red/White,
`FR-6210`, [FS-113](FS-113-observer-read-only-access.md)'s Observer pattern) — a structurally similar
but distinct concern this Feature does not touch.

## Requirements Implemented

FR-3510 (order panel offers only role-and-asset-legal commands, rejects an out-of-scope command
submitted directly), FR-3520 (a Role Assignment's bus-only/payload-only/both scope is enforced as
its own system behavior, independent of and in addition to the UI filter) — per the Feature
Catalog's `Included Requirements` for `FEAT-3500`. Both requirements are carried forward verbatim;
none invented.

## User Workflows

- A Blue or Red operator, seated under a Role Assignment scoped to `bus-only` for Asset X, opens
  the order/command interface for Asset X: the offered command list contains only `BUS_VERBS`
  legal for that asset's current state (per `FS-105`'s existing `can_issue()` gates) — no
  `PAYLOAD_VERBS` appear, regardless of whether the asset's payload would otherwise accept them.
- The same operator attempts to submit a payload-scoped command for Asset X by any path that
  bypasses the order panel (e.g., a direct API call): the system rejects it, citing the role-scope
  mismatch as the failure reason — distinct from (and checked independently of) the existing
  asset-capability/ownership/window checks `FS-105`/`FS-101` already perform.
- An operator seated under a `both`-scoped Role Assignment for Asset X sees and may issue both
  `BUS_VERBS` and `PAYLOAD_VERBS` for that asset, subject to every other existing gate unchanged.
- White Cell (unscoped by any Role Assignment, per `GDS-04` §1.10's own constraints — Role
  Assignments bind operator seats, not the facilitator) is unaffected by this Feature's filtering;
  White Cell's own command authority is out of this Feature's scope.

## System Behaviour

- **Seat resolution (per `ADS-3500` Decision Log entry 1):** every command submission carries an
  optional `seat` identifier, client-asserted at the same trust level `cell` already is (no new
  authentication mechanism). When a `seat` is supplied and the targeted Asset has a covering
  `roles_needed` entry, the Session Layer resolves that seat's Role Assignment from the existing
  mapping (`FS-115`) before either check below runs. When `seat` is omitted, or the Asset has no
  covering `roles_needed` entry, neither check applies — the behavior every one of the 19 currently
  shipped vignettes already exhibits is unchanged.
- **Order-panel filtering (`FR-3510`, presentation-layer consequence):** given the resolved Role
  Assignment for the targeted Asset, the offered command list is the intersection of `FS-105`'s
  asset-legal verbs (`can_issue()`'s existing gates) and the verbs the Role Assignment's scope
  covers — `BUS_VERBS ∪ DEFENSE_VERBS` for `bus`, `PAYLOAD_VERBS` for `payload`, all three sets for
  `both` (per `ADS-3500` Decision Log entry 2, which classifies every `DEFENSE_VERBS` entry as
  `bus`-scope). A command the Role Assignment does not cover for that Asset never appears in the
  offered list.
- **Execution-time role-scope enforcement (`FR-3520`, session-layer behavior):** independent of
  whether a command was ever offered in the panel, every command submission carrying a resolvable
  `seat`/Role-Assignment pair is checked against that scope for the targeted Asset before it is
  accepted into the existing plan-first pipeline (`FS-101`'s window/ownership/resource checks,
  `FS-102`'s execute-time re-validation). A command outside the Role Assignment's scope is rejected
  with a role-scope-specific reason, at both submission time and (per `FR-3520`'s postcondition)
  again at execution time if state could have changed between the two — mirroring the
  re-validation pattern `FR-3410`/`FS-102` already establishes for other plan-first checks, applied
  to this new gate rather than duplicating its mechanism.
- **Both-scoped or no-Role-Assignment-required actors:** an operator with a `both` scope, or an
  action White Cell issues directly (not subject to any Role Assignment per `GDS-04` §1.10), is
  unaffected by either check above.
- **Edge case — the targeted Asset has no covering Role Assignment for the acting seat at all:**
  treated identically to an out-of-scope command (rejected, both offer-time and execution-time),
  since an uncovered Asset is a strict subset of "not covered by this Role Assignment's scope."

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| **C2 Session / Application Layer** (`GDS-03` §2.2) | Owns the execution-time enforcement (`FR-3520`), including resolving the submitted `seat` identifier against the existing Role Assignment mapping (`ADS-3500` Decision Log entry 1). `GDS-04` §1.10's own Domain Model text already commits to this: a Role Assignment "determines which Planned Activities a given human... may legally issue (**checked by the Session layer's permission logic**, `GDS-03` §2.2)." This is the same seam that already owns the Role Assignment mapping itself (`GDS-03` §2.2 "Ownership of data" — the seat→asset mapping, `FS-115`'s `SessionManager.assign_role`/`role_assignments`) and the same architectural pattern `ADR-0004` establishes for the structurally similar fog-of-war boundary (enforce once, server-side, at this exact seam — not the UI, not the engine). |
| **C4 Operator Console** (presentation) | Owns the offer-time filtering (`FR-3510`'s UI-filtering consequence) — trusts the Session Layer's role-scope data the same way it already trusts `CellController`'s fog-of-war output verbatim (`ADR-0004`'s established pattern), rather than deciding legality itself. |
| **C1 Simulation Engine** | **Not** a home for this Feature's logic — `engine/buscommands.py`'s `can_issue()` takes no operator/seat/cell parameter today and, per `CLAUDE.md` invariant 2 (UI-agnostic engine, no concept of "cell"), must not gain one; role-scope enforcement is session-layer state (the Role Assignment mapping) applied to the engine's existing verb catalog (`BUS_VERBS`/`PAYLOAD_VERBS`), not a new engine capability. |

## Interfaces Used

- **INT-0004** (Blue/Red Cell Operator ↔ Operator Console) — already states, as a *Precondition*,
  "a valid Role Assignment binding the operator's seat to the targeted Asset/Sensor (`GDS-04` §1.10)"
  for this exact interface; this Feature is the enforcement of that precondition, not a new
  interface concern. Its concrete realization gains an optional `seat` field per `ADS-3500` Decision
  Log entry 1.
- **INT-0006** (Operator Console → Session Layer, `SessionAPI`, the single seam) — the boundary
  where `FR-3520`'s execution-time enforcement lives, per the reasoning in Subsystem Responsibilities
  above. Its concrete realization (`SessionManager.issue_order`/`InProcessSession.issue_order`)
  gains the same optional `seat` parameter, per `ADS-3500` Decision Log entry 1 — additive and
  backward-compatible with every existing call site.

## Data Model Changes

None beyond what `GDS-04` §1.10 (Role Assignment) and `FS-115` already define — confirmed by
`ADS-3500`, which resolved the seat-identifier gap as an *interface* addition (an optional request
parameter), not a Domain Model change. This Feature reads the existing Role Assignment mapping
(`seat → {asset_or_constellation, role}`); it does not add a new entity, attribute, or relationship
to the Domain Model. It adds a read-time *derivation* (resolve the acting seat's Role Assignment for
a given Asset, then intersect against `BUS_VERBS ∪ DEFENSE_VERBS`/`PAYLOAD_VERBS` per `ADS-3500`'s
verb-classification table), not new persistent state.

## State Changes

None. This Feature is a read-time gate over existing state (the Role Assignment mapping, the
existing command catalog); it creates, transitions, or retires no session or persistent state of
its own.

## Error Handling

- A command submission outside the acting seat's Role Assignment scope for the targeted Asset is
  rejected with a role-scope-specific failure reason (distinct from `no_such_asset`/
  `no_payload_for_verb`/window/ownership failure reasons `FS-101`/`FS-102`/`FS-105` already define),
  at both submission and (if applicable) execution time.
- An Asset with no Role Assignment at all covering the acting seat is treated as a rejection, not a
  crash or silent no-op (see System Behaviour's edge case).
- This Feature's checks are additive to, and independent of, every existing plan-first/execute-time
  check — a role-scope pass does not bypass any existing gate, and an existing-gate failure is not
  masked by a role-scope pass.

## Performance Considerations

None beyond what the existing plan-first pipeline already bears (`FR-3410`'s execute-time
re-validation, already Test-verified per `VR-1010`/`VR-1020`). Role-scope resolution is a
dictionary lookup against already-in-memory session state (the Role Assignment mapping), not a new
I/O or computation cost class.

## Security Considerations

This Feature's `FR-3520` postcondition — reject at execution time "whether or not it was also
filtered from the order panel" — is this project's standard defense-in-depth posture applied to a
new boundary: the UI filter is a convenience, never the enforcement (the same posture `ADR-0004`
established for fog-of-war and `IP-1130`/`FS-113` established for the Observer seat's mutation
rejection). Per the project's documented LAN trust model (`CLAUDE.md` "LAN trust model
(load-bearing)"), the *cell* a request asserts is already client-side trust — this Feature does not
change that boundary; it adds a *finer-grained, still server-side* check one level inside an
already-trusted cell (which seat, and which role that seat holds), consistent with how `FS-113`'s
Observer rejection is "enforced at this same trust level, not a stronger one."

## Acceptance Criteria

1. Given an operator seated under a Role Assignment scoped `bus-only` for Asset X, the order panel
   for Asset X offers zero `PAYLOAD_VERBS`, regardless of Asset X's payload state — and offers every
   asset-legal `BUS_VERBS`/`DEFENSE_VERBS` command (per `ADS-3500`'s classification of `DEFENSE_VERBS`
   as `bus`-scope).
2. Given the same operator, a payload-verb command for Asset X submitted by any path that bypasses
   the order panel is rejected with a role-scope-specific reason, not silently accepted and not
   accepted-then-ignored.
3. Given an operator seated under a `both`-scoped Role Assignment for Asset X, every `BUS_VERBS`,
   `PAYLOAD_VERBS`, and `DEFENSE_VERBS` command legal per `FS-105`'s existing gates is offered and
   accepted, unchanged from today's behavior.
4. Given an Asset with no Role Assignment covering the acting seat, every command for that Asset is
   rejected with the same role-scope reason as an out-of-scope command (not a different, unhandled
   failure mode).
5. Given a command submission that omits the `seat` identifier, or targets an Asset with no covering
   `roles_needed` entry, neither role-scope check applies — behavior is unchanged from today for
   every one of the 19 currently shipped vignettes.
6. Every existing `FS-101`/`FS-102`/`FS-105` acceptance criterion (window/ownership/resource/
   asset-capability gating) continues to pass unchanged — this Feature adds a gate, it does not
   relax or bypass any existing one.

## Verification Plan

Per each requirement's own `Verification Method` (`Test`, both `FR-3510` and `FR-3520`): automated
tests exercising Acceptance Criteria 1–5 against a fixture Role Assignment scoped each of
`bus-only`/`payload-only`/`both` (including at least one `DEFENSE_VERBS` command per scope, per
`ADS-3500`'s classification), plus a regression run of the full existing test suite to confirm
Acceptance Criterion 6. Consistent with this project's test-first mandate (`CLAUDE.md` "Test-driven
workflow") — the implementing package must encode each Acceptance Criterion as a failing test
before implementation.

## Dependencies

[FS-115](FS-115-session-setup.md) (`FR-4210` — produces the Role Assignment record this Feature
reads and enforces; already `VERIFIED`), [FS-105](FS-105-spacecraft-operations.md) (the
`BUS_VERBS`/`PAYLOAD_VERBS`/`DEFENSE_VERBS` catalog and `can_issue()` gates this Feature filters/
enforces against, without modifying; already `VERIFIED`).

## Risks

- **This Feature was undelivered for the entire prior project history despite being Must-priority
  and Release-1-bucketed** — the release plan's own text characterized its RTM `UNASSIGNED` cells
  as "a traceability gap, not new development," an assumption this document's own authoring (and the
  release-readiness audit that preceded it) found does not hold. Treat this Feature's implementation
  as new development, not a citation fix.
- **`FS-115`'s own text (its `Dependencies` field and `Scope` section) already asserts this Feature's
  existence and a dependency relationship in the *opposite* direction** ("FS-105 (Role Assignment
  scope this Feature produces)," and "the runtime enforcement... is `FS-105`'s and `FEAT-3500`'s
  concern") — checked directly against `FS-105`'s own text, which contains zero mention of
  `FR-3510`/`FR-3520`/Role Assignment/`FEAT-3500` anywhere. `FS-115`'s cross-reference was aspirational,
  written before this Feature had any spec to point to. This document is that missing spec;
  `FS-115`'s stale cross-reference (pointing at `FS-105` rather than this document) should be
  corrected at `FS-115`'s next maintenance touch — flagged here, not fixed here (this skill does
  not edit other Features' specs).
- **`docs/architecture/03-architecture.md` §2.2 names the Role Assignment mapping's implementation
  as "`RoleRegistry`"** — grepping the shipped tree finds no such class; the actual implementation is
  a plain `role_assignments` dict on `SessionManager`. A naming imprecision in the architecture
  document, not a defect this Feature Specification can fix (out of this skill's write scope) —
  flagged for the architecture owner's awareness.
- **The Feature Catalog's own `Related ADRs: ADR-0004` citation for `FEAT-3500` is imprecise**:
  `ADR-0004`'s actual decision text is scoped specifically to cell-level fog-of-war (Blue/Red/White),
  not role-level (bus/payload) enforcement — a structurally analogous but textually distinct
  concern. This document instead grounds its Subsystem Responsibilities in `GDS-04` §1.10's own
  domain-model text (which does explicitly commit to "the Session layer's permission logic" for
  Role Assignment enforcement) rather than stretching `ADR-0004` to cover a decision it does not
  actually make. Flagged for `05-feature-decomposition`'s catalog owner, not corrected here.

## Open Questions

Both of v1.0's Open Questions are **closed** as of this revision, resolved by
[ADS-3500](../architecture/ADS-3500-role-scoped-command-enforcement.md):

1. ~~No existing interface carries a "seat" identifier — only "cell."~~ **Resolved**
   (`ADS-3500` Decision Log entry 1): `INT-0004`/`INT-0006`'s concrete realizations gain an optional
   `seat` field/parameter, resolved by the Session Layer against the existing Role Assignment
   mapping. `GDS-01` §2's multi-seat concurrency model is preserved, not narrowed — the project owner
   explicitly declined the single-active-Role-Assignment-per-cell simplification that would have
   sidestepped this question at that model's expense.
2. ~~`DEFENSE_VERBS` doesn't map cleanly onto the two-way `bus`/`payload` role-scope model.~~
   **Resolved** (`ADS-3500` Decision Log entry 2): every `DEFENSE_VERBS` entry is classified as
   `bus`-scope (a `bus-only` Role Assignment includes `BUS_VERBS ∪ DEFENSE_VERBS`; `payload-only`
   includes only `PAYLOAD_VERBS`; `both` includes all three sets).

`ADS-3500` itself carries two residual, non-blocking Open Questions of its own (whether `seat`
should become mandatory once more vignettes declare `roles_needed`; whether a third
`defense`-scope category is ever needed) — neither blocks `07-implementation-planning` against this
document.

## Related ADRs

ADR-0004 (cited by the Feature Catalog; see Risks for why this document does not lean on it as the
governing decision for this Feature's own enforcement seam — `GDS-04` §1.10 is the more precise
source), ADR-0005 (plan-first order validation, the existing mechanism this Feature's execution-time
check attaches to).

## Related Interfaces

INT-0007 (Session Layer → Engine, the boundary `CellController` already uses for its own
per-cell-view filtering — cited for architectural analogy, not directly used by this Feature),
INT-0008 (Session Layer ↔ Engine, the seam `FS-101`/`FS-102`'s existing order validation/scheduling
already crosses — this Feature's execution-time check sits alongside that existing traffic, not
inside it).
