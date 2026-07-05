# IP-1160 — Role-Scoped Command Catalog & Assignment Scoping

> **Package ID:** IP-1160
> **Version:** 1.0
> **Status:** 🔴 BLOCKED *(not authorized — MSTR-006 §3. Every dependency package is already
> `VERIFIED`, so this package is specification-complete and would be `READY` the moment
> authorization is granted; it is marked `BLOCKED` rather than `READY` only because that
> authorization is the one thing standing between this package and code, per this skill's own
> "READY means fully specified AND every dependency VERIFIED" rule — see Dependencies below for why
> the dependency half is already satisfied.)*
> **Dependencies:** [FS-116](../../features/FS-116-role-scoped-command-catalog.md) v1.1,
> [ADS-3500](../../architecture/ADS-3500-role-scoped-command-enforcement.md) (binding design
> grounding for the seat-identifier interface amendment and `DEFENSE_VERBS` classification),
> [IP-1151](IP-1151-seat-role-assignment.md) (produces the Role Assignment record this package
> reads — `VERIFIED`), [IP-1050](IP-1050-spacecraft-operations-bus-payload.md)/
> [IP-1051](IP-1051-spacecraft-operations-effects-console.md) (the command catalog this package
> filters/enforces against, unmodified — both `VERIFIED`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** the enforcement layer `FEAT-3500` describes — `FS-116`'s Requirements Implemented
> (`FR-3510`/`FR-3520`) become checkable Acceptance Criteria against running code
> **Feature Reference:** [FS-116 — Role-Scoped Command Catalog & Assignment Scoping](../../features/FS-116-role-scoped-command-catalog.md)
> **Supersedes:** none — new package, the first (and, per `FS-116`'s own Scope, only) package this
> Feature needs; no lettered split, see Technical Work Breakdown Tranche 2 for why
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py),
> [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js),
> [`spacesim/engine/buscommands.py`](../../../spacesim/engine/buscommands.py) (read-only reference,
> not modified)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*This is a forward-design package: `FEAT-3500` had zero implementation anywhere in `spacesim/` at
authoring time (confirmed independently three times — `08-code-implementation` run #8, `VR-1151`
run #15, and `11-release-readiness`'s [release assessment](../../reviews/release-assessment-fs-tracked-baseline.md)
Finding 2). `FS-116`'s two Open Questions (no interface carries a seat identifier; `DEFENSE_VERBS`
doesn't map onto the two-way role-scope model) are both closed as of `FS-116` v1.1, via `ADS-3500`
— this package plans against that resolved design, not an open one.*

## Package ID

IP-1160

## Title

Role-Scoped Command Catalog & Assignment Scoping

## Objective

Make the order/command interface offer only commands legal for an operator's seated role
(bus/payload/both) and targeted Asset, and independently reject at execution time any command
outside that Role Assignment's scope — whether or not it was ever offered — closing `FEAT-3500`'s
two Must-priority requirements against the design `ADS-3500` settled.

> **This is a forward-design package. Per MSTR-006 §3, this document's own specification is not
> itself an authorization to write code** — a separate, explicit user go-ahead is required before
> any Implementation Task below begins.

## Feature Reference

[FS-116 — Role-Scoped Command Catalog & Assignment Scoping](../../features/FS-116-role-scoped-command-catalog.md)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-3510 | Order panel offers only role-and-asset-legal commands | The client-side command-list builder (`app.js`'s `actionsFor()`) filters against the acting seat's resolved Role Assignment scope (via `ADS-3500`'s `BUS_VERBS ∪ DEFENSE_VERBS`/`PAYLOAD_VERBS`/both classification) whenever one exists for the targeted Asset; unchanged when none does. |
| FR-3520 | Role Assignment scope enforced at execution time, independent of the UI filter | `SessionManager.issue_order` gains a role-scope check — resolving the submitted `seat` against the existing Role Assignment mapping and rejecting an out-of-scope verb — before the order ever reaches `OrderSystem.issue()`, so a request that bypasses the order panel entirely is rejected identically to one the panel would have hidden. |

## Architecture Components

Per `FS-116`'s own Subsystem Responsibilities and `ADS-3500`'s System Architecture (§2):

- **C2 Session / Application Layer** — `SessionManager`/`InProcessSession` gain the execution-time
  role-scope gate (`FR-3520`) and the `seat`-resolution logic, applied *before* the existing
  plan-first pipeline (`OrderSystem.issue()`/`dry_run()`) runs. This is additive to, not a
  replacement for, `FS-101`/`FS-102`'s existing checks.
- **C4 Operator Console** — `app.js` gains the offer-time filter (`FR-3510`) and the client-side
  "which seat am I" concept this package's Risks section flags as genuinely new UI surface (today
  the client tracks `CELL` only, never a seat identifier).
- **C1 Simulation Engine** — untouched. `engine/buscommands.py`'s `can_issue()`/`COMMAND_VERBS`/
  `BUS_VERBS`/`PAYLOAD_VERBS`/`DEFENSE_VERBS` are read (imported), never modified — this package
  adds a session-layer gate in front of the engine's existing catalog, per `CLAUDE.md` invariant 2.

## Interfaces

**INT-0004** (Blue/Red Cell Operator ↔ Operator Console) and **INT-0006** (Operator Console →
Session Layer, `SessionAPI`) — both gain an optional `seat` field/parameter in their concrete
realizations, per `ADS-3500` Decision Log entry 1. Fully additive: every existing caller that omits
`seat` (every current test, every currently shipped vignette) is unaffected.

## Files to Create

None proposed — every addition fits within the existing `session/manager.py`/`session/inprocess.py`/
`ui_web/server.py`/`ui_web/static/app.js` structure (mirrors `IP-1130`/`IP-1151`'s restraint
principle: extend, don't create a parallel mechanism).

## Files to Modify

- `spacesim/session/manager.py` *(proposed)* — add a role-scope resolution helper (e.g., a method
  resolving `(seat, actor_id, verb) → allowed: bool`, reusing the existing `role_assignments`
  mapping and `_role_covers`-style matching `assign_role`/`staffing_report` already established at
  `IP-1151`) and a verb-classification lookup built from `engine.buscommands.BUS_VERBS`/
  `PAYLOAD_VERBS`/`DEFENSE_VERBS` (imported, not duplicated — `bus` scope = `BUS_VERBS ∪
  DEFENSE_VERBS`, per `ADS-3500` Decision Log entry 2). `issue_order(self, cell, order, seat=None)`
  gains the new parameter; when `seat` is supplied, `order.action == "command"`, and the targeted
  Asset has a covering `roles_needed` entry, the role-scope check runs before `self.osys.issue(order)`
  — a rejection short-circuits with a role-scope-specific `fail_reason`, mirroring `_order_ack`'s
  existing rejection shape rather than inventing a new response type. When `seat` is omitted or the
  Asset has no covering `roles_needed` entry, behavior is byte-identical to today.
- `spacesim/session/inprocess.py` *(proposed)* — `issue_order(self, session, cell, order, seat=None)`
  threads the new parameter through to `mgr.issue_order` unchanged in every other respect.
- `spacesim/ui_web/server.py` *(proposed)* — `OrderRequest` gains `seat: Optional[str] = None`; the
  `issue_order` route passes `req.seat` through. No new route needed — this is the same request
  shape, extended.
- `spacesim/ui_web/static/app.js` *(proposed)*:
  - A new client-side "which seat am I" concept — today the client tracks only `CELL`
    (White/Blue/Red/Observer); this package adds a lightweight seat-identifier input (mirroring the
    seat string `IP-1151`'s seat-assignment UI already collects from White Cell), stored in a new
    client variable and attached to every order submission (`composeBody()`) alongside `cell`.
  - `actionsFor(a)`: when the acting seat has a covering Role Assignment for asset `a` (fetched via
    the existing `/roles/staffing`-adjacent read path, or a small equivalent read of the seat's own
    binding), the offered list is automatically filtered to that Role Assignment's scope — replacing
    the free-standing `ROLE_FILTER` manual toggle's role as the *authoritative* filter in that case
    (the manual toggle remains available as an additional narrowing when no Role Assignment applies,
    unchanged from today).
  - **Correct the existing `VERB_ROLE` object's `def.harden` entry** (currently tagged `"payload"`,
    a pre-existing, never-reviewed cosmetic tag — see Risks) to `"bus"`, consistent with `ADS-3500`'s
    classification of every `DEFENSE_VERBS` entry as `bus`-scope. Also add the three `DEFENSE_VERBS`
    entries `VERB_ROLE` is currently missing entirely (`def.escort_posture`, `def.disperse`,
    `def.set_deception_mode`), tagged `"bus"`.

**Explicitly out of scope for this package** (per `FS-116`'s own Scope boundary, carried forward):
the base order actions (`jam`/`engage`/`observe`/`maneuver`/`downlink`/`cyber`) that
`engine/orders.py` dispatches directly — `FR-3510`/`FR-3520`'s "commands... drawn from that Asset's
command database" language and `FS-116`'s own Scope both point specifically at
`engine/buscommands.py`'s `COMMAND_VERBS` catalog (dispatched via the `"command"` action), not these
base actions; role-scoping the base actions is not this Feature's stated requirement.

## Implementation Tasks

**Not started — not authorized (MSTR-006 §3).** Proposed sequence once authorized:

1. Add the role-scope resolution helper to `SessionManager` (verb → `bus`/`payload` classification
   from the engine's existing three sets per `ADS-3500`'s table; seat → Role Assignment → scope
   resolution reusing `IP-1151`'s existing matching logic).
2. Wire `issue_order`'s new optional `seat` parameter through `SessionManager` → `InProcessSession` →
   `OrderRequest`/the HTTP route, confirming every existing call site (tests, vignette-driven flows)
   continues to omit it and behave unchanged.
3. Add the client-side seat-identifier concept and thread it into `composeBody()`.
4. Wire `actionsFor(a)`'s automatic Role-Assignment-driven filtering, alongside the existing manual
   `ROLE_FILTER` toggle (which remains for the no-Role-Assignment-applies case).
5. Correct `VERB_ROLE`'s `def.harden` tag and add the three missing `DEFENSE_VERBS` entries (see
   Files to Modify).
6. Write tests first (per `CLAUDE.md`'s mandatory test-first workflow) encoding every Acceptance
   Criterion below, then implement until green.

## Tests to Add

*(Proposed — none exist yet.)*

- `spacesim/tests/test_role_scope_enforcement.py` *(new)* — one test per Acceptance Criterion:
  - A `bus-only` Role Assignment for Asset X: submitting a `PAYLOAD_VERBS` command for X (bypassing
    any client-side filter, i.e. calling `issue_order` directly with `seat` set) is rejected with a
    role-scope-specific `fail_reason`; a `BUS_VERBS`/`DEFENSE_VERBS` command for X is accepted
    (subject to `FS-105`'s existing gates, unchanged).
  - A `payload-only` Role Assignment: the mirror image (payload commands accepted, bus/defense
    commands rejected).
  - A `both`-scoped Role Assignment: every asset-legal `BUS_VERBS`/`PAYLOAD_VERBS`/`DEFENSE_VERBS`
    command is accepted, unchanged from today.
  - An Asset with no Role Assignment covering the submitting seat at all: every command for that
    Asset is rejected with the same role-scope reason as an out-of-scope command.
  - A command submission that omits `seat` entirely, or targets an Asset with no covering
    `roles_needed` entry: neither role-scope check applies — byte-identical to today's behavior.
    (This is the regression case protecting all 19 currently shipped vignettes.)
- Regression: re-run the full existing suite (566 passed/3 skipped as of this package's authoring)
  to confirm no existing test's behavior changed.

## Documentation Updates

- `ROADMAP.md` Implementation Packages theme — add this package's row (done in the same pass as
  this package's authoring, per this skill's Step 4).
- `docs/features/FS-116-role-scoped-command-catalog.md`'s `Referenced By` metadata — add this
  package once authored (this pass).
- `docs/design/05-interface-control-document.md`'s `INT-0004`/`INT-0006` entries — still read as
  carrying only `cell`, not `seat` (a known, flagged staleness — `ADS-3500` Risks). **This package's
  own documentation-update step should correct those two entries directly**, since it is the first
  concrete code change that makes the amendment real, rather than waiting on a future `GDS-09`
  authoring pass.
- `CLAUDE.md`'s Code Map — a brief addition for the new role-scope helper in `session/manager.py`,
  mirroring `IP-1120`/`IP-1130`/`IP-1151`'s precedent of updating this field when a new session-layer
  mechanism ships.

## Definition of Done

- [ ] **Explicit user authorization obtained** for this package's Implementation Tasks (MSTR-006 §3)
  — not yet on record.
- [ ] `SessionManager.issue_order`/`InProcessSession.issue_order` accept an optional `seat`
  parameter; every existing call site that omits it behaves byte-identically to before this
  package.
- [ ] A `bus-only`/`payload-only`/`both` Role Assignment correctly gates command acceptance at
  `issue_order`, independent of whether the command was ever offered client-side (`FR-3520`).
- [ ] The order panel's offered command list is automatically filtered to the acting seat's Role
  Assignment scope when one covers the targeted Asset (`FR-3510`).
- [ ] `DEFENSE_VERBS` are treated as `bus`-scope throughout (both the session-layer check and the
  corrected `VERB_ROLE` client tags), per `ADS-3500` Decision Log entry 2.
- [ ] Every one of the 19 currently shipped vignettes (none declaring `roles_needed`) starts and
  plays with command issuance completely unaffected by this package.
- [ ] `docs/design/05-interface-control-document.md`'s `INT-0004`/`INT-0006` entries updated to
  reflect the `seat` field, closing `ADS-3500`'s flagged staleness.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] `spacesim/tests/test_role_scope_enforcement.py` exists and is green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green (this package's checks
  are session-layer, read-time-only — no engine mutation, no RNG use, no wall-clock read).
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green (no new import into
  `engine/` from `session/`/`ui_web/`; `engine/buscommands.py`'s existing verb sets are imported
  by `session/`, the normal, already-established direction).
- [ ] Full existing suite re-run with zero regressions (566 passed/3 skipped baseline at this
  package's authoring).
- [ ] Independently re-derive (not merely re-cite) that `DEFENSE_VERBS` role-scope handling matches
  `ADS-3500`'s classification table, by reading the shipped verb-classification helper directly.
- [ ] Independently confirm every one of the 19 shipped vignettes' command-issuance tests
  (`test_content.py`, `test_vignette_tutorials.py`, `test_bus_commands.py`) pass unchanged.

## Dependencies

- **Upstream:** [FS-116](../../features/FS-116-role-scoped-command-catalog.md) v1.1 and
  [ADS-3500](../../architecture/ADS-3500-role-scoped-command-enforcement.md) (both closed, no open
  design questions blocking this package); [IP-1151](IP-1151-seat-role-assignment.md) (`VERIFIED`
  — produces the Role Assignment record this package reads); [IP-1050](IP-1050-spacecraft-operations-bus-payload.md)/
  [IP-1051](IP-1051-spacecraft-operations-effects-console.md) (`VERIFIED` — the command catalog this
  package filters/enforces against, read-only). **Every dependency is `VERIFIED`** — the only
  remaining gate is MSTR-006 §3 authorization.
- **Downstream:** None yet — this closes `FEAT-3500`, the last Must-priority Feature in the release
  plan's Release 1 bucket without an owning package as of `11-release-readiness`'s assessment.
- **Build-sequencing:** Independent of every other currently-open package (there are none — all 18
  prior packages are `VERIFIED`); this is the sole package in Tranche 2.

## Risks

- **This Feature was undelivered for the entire prior project history despite being Must-priority
  and Release-1-bucketed** — carried forward from `FS-116`'s own Risks; this package is the first
  concrete step closing that gap, not a routine addition.
- **New client-side "seat" concept is genuinely new UI surface, not a wiring exercise.** Today's
  client tracks only `CELL`; introducing a seat identifier the operator asserts (mirroring `cell`'s
  own client-asserted trust level, per `ADS-3500` §2) is more UI work than threading an existing
  field through, and should be scoped/tested as such, not underestimated as "just add a parameter."
- **The pre-existing `VERB_ROLE`/`ROLE_FILTER` mechanism in `app.js` is a client-side-only,
  unenforced display convenience predating this Feature** (a personal "Bus/Payload/SDA/All" viewing
  filter with no connection to any Role Assignment, and a third "sda" tag that is a cosmetic
  sub-grouping of `payload`-scoped verbs, not a fourth role-scope category). Its one substantive
  conflict with `ADS-3500`'s classification — `def.harden` tagged `"payload"` there versus `"bus"`
  per `ADS-3500` Decision Log entry 2 — is resolved in favor of `ADS-3500` (the reviewed,
  authoritative decision) as a bug fix, not silently preserved; flagged here so the correction isn't
  read as an unexplained behavior change. This existing mechanism must not be mistaken for `FR-3510`'s
  actual implementation — it enforces nothing server-side and was never tied to a Role Assignment.
- **`ADS-3500`'s own two residual Open Questions** (mandatory `seat` once more vignettes declare
  `roles_needed`; a possible third `defense` role-scope category) are out of this package's scope to
  resolve — carried forward, non-blocking.

## Rollback Considerations

Every change this package proposes is additive and gated on an optional parameter defaulting to
absent/`None` (`seat`) or on a covering `roles_needed` entry that no currently shipped vignette
declares — reverting `SessionManager`'s role-scope helper, the `seat` parameter across
`issue_order`'s two wrappers and `OrderRequest`, the client-side seat concept, and `actionsFor()`'s
automatic filtering fully restores today's behavior with no data-migration concern (no persisted
state is added — `role_assignments` already established by `IP-1151` is unchanged in shape, only
newly *read* by this package's helper). The `VERB_ROLE` tag corrections (`def.harden` and the three
added `DEFENSE_VERBS` entries) are cosmetic client-side data and can be reverted independently of
everything else in this package without any functional consequence, since `VERB_ROLE` only ever
drove the pre-existing unenforced manual filter.
