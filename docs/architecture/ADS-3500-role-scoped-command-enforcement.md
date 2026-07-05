> **Document ID:** ADS-3500
> **Version:** 1.1
> **Status:** ✅ Authored
> **Dependencies:** [GDS-04](04-domain-model.md) §1.10 (Role Assignment), [GDS-03](03-architecture.md)
> §2.2 (Session/Application Layer), `design/05-interface-control-document.md` INT-0004/INT-0006
> (grounding input — see Decision Log for why this document, not the ICD, is the record of the
> amendment), `docs/requirements/01-functional-requirements.md` FR-3510/FR-3520
> **Referenced By:** [FS-116](../features/FS-116-role-scoped-command-catalog.md)
> **Produces:** the resolution of FS-116's two Open Questions; the seat-identifier interface
> amendment and the per-verb `bus`/`payload` classification of every `DEFENSE_VERBS` entry (v1.1 —
> no third "defense" scope category), both binding on FS-116's eventual Implementation Package
> **Feature Mapping:** FS-116
> **Related Topics:** [ADR-0004](adr/ADR-0004-fog-of-war-at-boundary.md) (the structurally similar
> "enforce once, server-side, at the session boundary" pattern this document extends to a new,
> distinct concern — role scope, not cell scope)

[↑ Architecture index](INDEX.md) · [Docs index](../INDEX.md)

# ADS-3500 — Role-Scoped Command Enforcement

*The first `ADS-xxx` authored in this project (Workflow B, per `architecture/INDEX.md` §2).
Authored specifically to resolve two Open Questions
[FS-116](../features/FS-116-role-scoped-command-catalog.md) surfaced and could not resolve within
its own authority — an interface gap (no existing request shape can express "which seat" issued a
command) and a domain-model gap (the engine's three-way verb taxonomy doesn't map onto the
requirements' two-way role-scope model). Workflow B, not the global ladder, because `GDS-09` (API
Specification — the level that would eventually formally own this interface decision) is still
scaffold-only and gated behind `GDS-06`-`08`; this cluster's design tension cannot wait for that
sequence to complete.*

*v1.1 (this revision): the project owner gave explicit product direction after v1.0 — "verbs
should be categorized as bus and payload; bus and payload verbs may provide a defensive effect but
no commands are purely defense actions." This corrects Decision Log entry 2, which had classified
every `DEFENSE_VERBS` entry as `bus`-scope wholesale. Every one of the eight `DEFENSE_VERBS` is now
individually reclassified as `bus` or `payload` based on which subsystem it actually mutates
(confirmed by reading `apply_command()`'s own implementation for each verb, not by category name)
— the "defense" grouping in `engine/buscommands.py` describes an *effect* (a defensive posture or
action), not a third *scope* category. Sections §3, §8, §9, and Decision Log entry 2 are updated;
all other sections are unaffected by this correction.*

## 1. Executive Design Overview

`FEAT-3500` (Role-Scoped Command Catalog & Assignment Scoping) needs to know, for any submitted
command, which seat's Role Assignment governs it — and today, nothing in the system's interfaces
carries that information. The Session Layer already owns the Role Assignment mapping itself
(`GDS-03` §2.2, `FS-115`/`IP-1151`), and `GDS-04` §1.10's own text already commits to the *concept*
("checked by the Session layer's permission logic") — but the concrete interface between the
Operator Console and the Session Layer only ever identifies the caller by `cell` (blue/red/white),
never by the finer-grained `seat` a Role Assignment actually binds. This document makes two
decisions: (1) extend that interface to carry a `seat` identifier, at the same client-asserted
trust level every other identifier in this system already carries (the documented LAN trust model);
(2) resolve which of the engine's three command-verb categories (`BUS_VERBS`/`PAYLOAD_VERBS`/
`DEFENSE_VERBS`) fall under which of the two role-scope categories (`bus`/`payload`) the
requirements baseline defines. Both decisions are additive — no existing interface, verb, or
enforcement path is removed or narrowed; a vignette that declares no `roles_needed` (all 19 shipped
vignettes, as of this writing) is entirely unaffected.

## 2. System Architecture

No new subsystem. The two decisions extend exactly the two subsystems `FS-116` already identified:

- **C4 Operator Console** — the order-submission request gains an optional `seat` field, exactly
  parallel to how it already carries `cell`. This is a client-asserted value, not a new
  authentication mechanism — consistent with `cell` itself, `IP-1130`'s Observer designation, and
  `IP-1151`'s `assign_role` calls, all of which are plain client-asserted strings under the
  project's documented LAN trust model (`CLAUDE.md` "LAN trust model (load-bearing)").
- **C2 Session / Application Layer** — `SessionManager.issue_order`/`InProcessSession.issue_order`
  gain an optional `seat` parameter, defaulting to `None` (preserving every existing call site's
  behavior unchanged). When `seat` is supplied and the targeted Asset has a covering `roles_needed`
  entry, the Session Layer resolves that seat's Role Assignment and applies the role-scope gate
  `FS-116` describes, before the order reaches `engine/orders.py`'s existing validation chain. When
  `seat` is omitted, or the Asset has no covering `roles_needed` entry, no role-scope gate applies —
  identical to today's behavior for every one of the 19 shipped vignettes.
- **C1 Simulation Engine** — unchanged. `engine/buscommands.py`'s `can_issue()` gains no new
  parameter; the role-scope gate is applied by the Session Layer *before* the engine's existing
  asset-capability checks run, not folded into them (`CLAUDE.md` invariant 2 — the engine has no
  concept of "cell" or "seat," and this decision does not give it one).

This is the same architectural pattern `ADR-0004` established for fog-of-war (enforce once,
server-side, at the Session Layer boundary, never in the UI or engine) applied to a structurally
similar but distinct concern. `ADR-0004`'s own decision text is scoped to cell-level fog-of-war
specifically — this document does not amend `ADR-0004` or claim it as direct authority; it applies
the same *pattern* to a new, separately-grounded case (`GDS-04` §1.10).

## 3. Domain Model

No new entity. The Role Assignment entity (`GDS-04` §1.10) is unchanged — this document only
clarifies which of the engine's existing command verbs fall under which of its two already-defined
scope values (`bus`, `payload`; `both` is the union). Per the project owner's explicit v1.1
direction, **there are only two role-scope categories — `DEFENSE_VERBS` is an effect grouping in
`engine/buscommands.py`, not a third scope category**: every verb in it is individually bus or
payload, decided by which subsystem `apply_command()` actually mutates, not by its `def.*` name
prefix.

| Verb category (`engine/buscommands.py`) | Role scope | Rationale |
|---|---|---|
| `BUS_VERBS` (EPS, ADCS, CDH, TCS, comms link config, propulsion) | `bus` | Platform-subsystem actions; already the requirement's own literal example ("a bus-only-assigned operator") in `FR-3510`'s Acceptance Criteria. |
| `PAYLOAD_VERBS` (SATCOM mission config, ISR, SIGINT, SDA tasking, weather, PNT, missile-warning) | `payload` | Every verb in this set is tied to a specific payload's mission function — the requirement's own literal "payload-only command" example. |
| `DEFENSE_VERBS` — reclassified individually (v1.1): | | |
| &nbsp;&nbsp;`def.frequency_hop` | `bus` | Mutates `bus.comms.freq_hopping` — the same `bus.comms` subsystem `comms.enable_isl`/`comms.config_link` (already `BUS_VERBS`) mutate. |
| &nbsp;&nbsp;`def.patch_cyber` | `bus` | Patches `a.cyber_vulnerabilities`, gating `recovery.py`'s safe-mode re-safing chain — a CDH/flight-software-domain concern (`CLAUDE.md`'s own telemetry framing: "cyber → FSW errors"), i.e. bus-domain. |
| &nbsp;&nbsp;`def.set_threat_warning` | `bus` | Sets `a.threat_warning`, an asset-wide situational-posture flag (not `payload_state`-scoped) — a platform-level state, consistent with the bus being this domain's "whole-ship" owner. |
| &nbsp;&nbsp;`def.maneuver_evade` | `bus` | Consumes `a.resources.delta_v_ms` — the identical propulsion resource pool `prop.cancel_burn`/`prop.collision_avoid`/`prop.station_keep` (already `BUS_VERBS`) consume; `payload_state.evasion_active` is set only as a secondary side-effect, not the primary action. |
| &nbsp;&nbsp;`def.escort_posture` | `bus` | Sets `a.threat_warning` and logs a `world.consequences` entry — the same asset-wide posture mechanism as `def.set_threat_warning`, not a `payload_state` mutation. |
| &nbsp;&nbsp;`def.disperse` | `bus` | Primary effect is `a.threat_warning = True` (a constellation-level maneuver posture, propulsion-adjacent like `def.maneuver_evade`); the conditional `payload_state.detail` update is a secondary annotation, not the action's substance. |
| &nbsp;&nbsp;`def.harden` | `payload` | Mutates `a.payload_state.hardened` directly — the implementation requires `payload_state` to exist at all (`return False, "no_payload"` otherwise), unlike every `bus`-classified verb above. |
| &nbsp;&nbsp;`def.set_deception_mode` | `payload` | The implementation's own comment states this "surfaces as a payload-side posture flag" (military deception per the USSF Space Warfighting Framework) — explicitly payload-domain by the code's own documentation. |

## 4. User Stories

- *As a Blue operator seated under a `bus-only` Role Assignment for Asset X, I can issue evasive
  maneuvers and patch cyber vulnerabilities on Asset X, but I cannot task Asset X's ISR sensor or
  harden its payload* — because `def.maneuver_evade`/`def.patch_cyber` are `bus`-scoped verbs while
  `isr.collect_now`/`def.harden` are `payload`-scoped, and neither is offered/accepted outside its
  own scope.
- *As a Blue operator seated under a `payload-only` Role Assignment for Asset X, I can task Asset
  X's sensors, manage its SATCOM configuration, and harden its payload, but I cannot maneuver Asset
  X or patch its cyber posture* — because those are `bus`-scoped verbs outside my assignment's
  scope.
- *As a White Cell facilitator authoring a new vignette that declares `roles_needed`, I can rely on
  the existing `roles_needed`/`assign_role`/`staffing_report` mechanism (`FS-115`) unchanged — this
  document adds no new authoring surface.*

## 5. Functional Requirements

This document creates no new `FR-xxxx` — it resolves ambiguity blocking two already-baselined
requirements from being implementable:

- **FR-3510** (order panel offers only role-and-asset-legal commands) — the `seat` identifier this
  document adds is the missing input that makes "the operator's seated role" resolvable at all.
- **FR-3520** (execution-time role-scope enforcement, independent of the UI filter) — the Domain
  Model clarification (§3 above) is the missing rule that makes "commands legal for this role"
  well-defined for every verb in the existing catalog, not just `BUS_VERBS`/`PAYLOAD_VERBS`.

## 6. Non-functional Requirements

- **Determinism (`CLAUDE.md` invariant 1):** the `seat` parameter and its role-scope resolution are
  read-time checks against already-in-memory session state (the Role Assignment mapping) — no
  wall-clock read, no RNG use, no engine-state mutation. Adding this parameter does not touch the
  engine and cannot affect `(initial_state, eventlog, seed) → byte-identical state`.
  (Traces to `NFR-2400`, state-hash data integrity — unaffected by a session-layer-only addition.)
- **Backward compatibility:** every existing call site of `issue_order` (all 566 currently-passing
  tests, all 19 shipped vignettes) continues to behave identically with `seat` defaulted to `None`
  — this is an additive interface change, not a breaking one.
- **Trust model consistency (`NFR-2300`, LAN trust boundary):** `seat` is asserted by the client at
  the same trust level as `cell` — this document introduces no new authentication mechanism and
  does not strengthen or weaken the documented v1 LAN trust boundary (`ADR-0015`).

## 7. Constraints

- Must not add a `seat`/role concept to `engine/` (`CLAUDE.md` invariant 2, UI-agnostic engine).
- Must not change `GDS-04` §1.10's Role Assignment entity or its `bus`/`payload`/`both` scope
  enumeration (a Domain Model change is a bigger, unbaselined step this document deliberately
  avoids — see Decision Log entry 2's rationale for classifying `DEFENSE_VERBS` under the existing
  two-value enumeration rather than adding a third).
- Must remain additive to every existing interface call site (no existing vignette, test, or client
  call may require modification to keep working).
- `docs/build-spec/` and `docs/design/05-interface-control-document.md` are grounding inputs, not
  documents this skill's authority edits directly (`03-architecture-design-synthesis`'s own Scope
  table) — the interface amendment is recorded here as this cluster's authoritative decision, per
  `architecture/INDEX.md`'s blanket supersession declaration, rather than by editing the ICD file.

## 8. Risks

- **The ICD (`design/05-interface-control-document.md`) itself still reads INT-0004/INT-0006 as
  carrying only `cell`, not `seat`, until someone updates it.** This document's decision is
  authoritative (per the supersession declaration), but the ICD's own text will read stale until
  either a future `GDS-09` authoring pass merges this decision in, or `FS-116`'s own eventual
  Implementation Package updates the ICD as part of its Documentation Updates (the more immediate,
  practical path — flagged for that package's authoring, not performed here).
- **Two of the eight per-verb classifications (`def.set_threat_warning`, `def.escort_posture`,
  `def.disperse`) rest on "asset-wide posture flag → bus" reasoning rather than a `bus.*`-namespaced
  field mutation** (unlike `def.frequency_hop`/`def.maneuver_evade`, which mutate `bus.comms`/
  propulsion resources directly). This is a defensible, code-grounded call (per §3's rationale
  column) but a softer one than the four verbs with a direct `bus.*` field mutation — if a future
  Feature needs finer-grained defense-verb scoping, revisit these three first.
- **Multi-seat-per-cell concurrency (`GDS-01` §2) is preserved, not simplified** — this was a
  deliberate choice (the project owner explicitly declined the "simplify scope to sidestep Q1"
  option that would have narrowed it). This means the eventual Implementation Package carries
  slightly more surface (an interface parameter change across the FastAPI route, both
  `issue_order` wrappers, and the `OrderRequest` model) than the simplified alternative would have.

## 9. Open Questions

1. **Should `seat` become mandatory rather than optional once enough vignettes declare
   `roles_needed`?** Left optional/backward-compatible in this document because every currently
   shipped vignette declares none; revisit if a future vignette-authoring push makes `roles_needed`
   common enough that an omitted `seat` becomes a live ambiguity rather than a "no gate applies"
   default. Route to a future `04-requirements-engineering` or `08-vignette-development` pass, not
   blocking `FS-116`'s implementation today.
2. ~~Whether a finer-grained third role-scope category (beyond `bus`/`payload`/`both`) is ever
   needed for `DEFENSE_VERBS`-like actions~~ — **closed by the project owner's explicit v1.1
   direction: there is no third category.** Every command is bus or payload (or both); "defense" is
   an effect a bus or payload verb can produce, never a scope category of its own.

Question 1 is residual and non-blocking — it does not prevent `07-implementation-planning` from
proceeding against `FS-116` with this document's decisions as its grounding.

## 10. Decision Log

| # | Decision | Rationale | Alternatives considered |
|---|---|---|---|
| 1 | Extend the operator-command interface (`INT-0004`'s concrete realization: `OrderRequest` in `spacesim/ui_web/server.py`; `INT-0006`'s concrete realization: `SessionManager.issue_order`/`InProcessSession.issue_order`) to carry an optional `seat: str \| None` field, resolved by the Session Layer against the existing Role Assignment mapping before applying `FS-116`'s role-scope gate. | Preserves `GDS-01` §2's existing many-roles-few-humans concurrency model (a cell may have more than one seated operator); consistent with the existing client-asserted trust level every other identifier in this system already carries; fully additive/backward-compatible with all 19 shipped vignettes and the full existing test suite. | (a) A single-active-Role-Assignment-per-cell simplification, avoiding any interface change — rejected: the project owner explicitly declined this option, since it would silently narrow `GDS-01` §2's documented concurrency model rather than making a deliberate, recorded architecture decision. (b) Deriving the acting seat from some other existing signal (e.g., a per-connection session token) — rejected: no such per-seat connection concept exists anywhere in the current session/transport layer (`session/inprocess.py`'s locking is per-session, not per-seat); inventing one would be a much larger change than adding one optional field. |
| 2 *(revised v1.1)* | **There are exactly two role-scope categories, `bus` and `payload` (`both` is their union) — no third "defense" category exists.** `DEFENSE_VERBS` is an *effect* grouping in `engine/buscommands.py` (verbs that produce a defensive posture/action), not a role-*scope* category; each of its eight members is individually classified `bus` or `payload` by which subsystem `apply_command()` actually mutates (see §3's table): `def.frequency_hop`/`def.patch_cyber`/`def.set_threat_warning`/`def.maneuver_evade`/`def.escort_posture`/`def.disperse` → `bus`; `def.harden`/`def.set_deception_mode` → `payload`. | **Directed by the project owner (v1.1):** "verbs should be categorized as bus and payload — bus and payload verbs may provide a defensive effect but no commands are purely defense actions." Confirmed against the actual `apply_command()` implementation for each of the eight verbs (not guessed from the `def.*` name prefix or the pre-existing, never-reviewed `app.js` `VERB_ROLE` tags) — four mutate a `bus.*`-namespaced field or the shared propulsion resource pool directly; two mutate `a.payload_state` directly (and fail with `no_payload` if it's absent); two (`def.set_threat_warning`, `def.escort_posture`) are asset-wide posture flags with no `bus.*`/`payload_state` field of their own, classified `bus` as the platform/"whole-ship" owner in this domain model. | *(v1.0, superseded)* Classify every `DEFENSE_VERBS` entry as `bus`-scope wholesale — rejected in v1.1: this session's own `app.js` had already, independently, tagged `def.harden` as `"payload"` (a coincidental but correct prior signal the v1.0 pass didn't weight before lumping all eight together), and reading `apply_command()` directly confirms `def.harden`/`def.set_deception_mode` are genuinely payload-side, not bus-side, actions. |

---

**Next step:** both of `FS-116`'s Open Questions are now closed by this document's Decision Log.
`07-implementation-planning` may proceed against `FS-116`, using this document's System
Architecture (§2) and Domain Model (§3) sections as the binding grounding for the interface and
verb-classification decisions its Implementation Package will carry out.
