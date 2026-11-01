# IP-1160 — Role-Scoped Command Catalog & Assignment Scoping

> **Package ID:** IP-1160
> **Version:** 1.2 *(2026-10-25, `07-implementation-planning`: authorized, re-validated against the
> current tree and made build-ready — see "Re-validation against the tree of 2026-10-25" below. v1.1
> corrected the per-verb `DEFENSE_VERBS` classification; the classification itself is unchanged.)*
> **Status:** ✅ VERIFIED *(authorized 2026-10-25 — MSTR-006 §3 go-ahead given by the project owner and
> recorded at pipeline-journal run #262: "authorize `IP-1160` now"; `FEAT-3500` stays in Release 1.
> Every dependency package is `VERIFIED`, so the "`READY` means fully specified and every dependency
> `VERIFIED`" rule is met.)*
> **Earlier status record (superseded by the line above; retained as history, unedited):** 🔴 BLOCKED
> *(not authorized — MSTR-006 §3; every dependency was already `VERIFIED`, so the package was
> specification-complete and would be `READY` the moment authorization was granted).*
> **Authorization (MSTR-006 §3):** project owner's go-ahead of 2026-10-25, journal run #262 (release
> assessment `REV-REL-002` blocker B2; answer given through `AskUserQuestion`).
> **Dependencies:** [FS-116](../../features/FS-116-role-scoped-command-catalog.md) v1.2,
> [ADS-3500](../../architecture/ADS-3500-role-scoped-command-enforcement.md) v1.1 (binding design
> grounding for the seat-identifier interface amendment and the per-verb `DEFENSE_VERBS`
> classification),
> [IP-1151](IP-1151-seat-role-assignment.md) (produces the Role Assignment record this package
> reads — `VERIFIED`), [IP-1050](IP-1050-spacecraft-operations-bus-payload.md)/
> [IP-1051](IP-1051-spacecraft-operations-effects-console.md) (the command catalog this package
> filters/enforces against, unmodified — both `VERIFIED`). Context packages that changed the files
> this package edits, all `VERIFIED`: [IP-1130](IP-1130-observer-read-only-access.md) (Observer
> rejection on the order routes), [IP-1068](IP-1068-white-only-controls-server-enforcement.md) /
> [IP-1074](IP-1074-white-control-correctness.md) / [IP-1082](IP-1082-white-control-nonfinite-input-and-toolbar-refusal.md)
> (the White-only seat rule and the non-finite guards), [IP-1340](IP-1340-browser-console-rule-suite.md)
> (the browser suite this package extends), [IP-1330](IP-1330-test-origin-marker-and-checks.md) /
> [IP-1334](IP-1334-test-origin-retag.md) / [IP-1079](IP-1079-origin-retag-guard-redesign.md) (test origins)
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
> not modified), [IP-1083](IP-1083-rewind-keeps-future-white-injects.md) (sibling; shares `manager.py`
> — see "Build ordering")

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*This is a forward-design package: `FEAT-3500` had zero implementation anywhere in `spacesim/` at
authoring time (confirmed independently three times — `08-code-implementation` run #8, `VR-1151`
run #15, and `11-release-readiness`'s [release assessment](../../reviews/release-assessment-fs-tracked-baseline.md)
Finding 2). `FS-116`'s two Open Questions (no interface carries a seat identifier; `DEFENSE_VERBS`
doesn't map onto the two-way role-scope model) are both closed as of `FS-116` v1.1, via `ADS-3500`
— this package plans against that resolved design, not an open one.*

*v1.1: the project owner gave further direction after this package's v1.0 draft —
there is no third "defense" role-scope category; every command is `bus` or `payload`, and a
defensive effect is a property either can have. `ADS-3500` v1.1 revised its per-`DEFENSE_VERBS`-verb
classification accordingly (six `bus`, two `payload`); this revision updates every field in this
package that referenced the superseded wholesale-`bus` call, including reversing this package's own
v1.0 plan to "correct" `app.js`'s already-correct `def.harden: "payload"` tag to `"bus"`.*

## Package ID

IP-1160

## Title

Role-Scoped Command Catalog & Assignment Scoping

## Objective

Make the order/command interface offer only commands legal for an operator's seated role
(bus/payload/both) and targeted Asset, and independently reject at execution time any command
outside that Role Assignment's scope — whether or not it was ever offered — closing `FEAT-3500`'s
two Must-priority requirements against the design `ADS-3500` settled.

> **Authorization is on record** (project owner, 2026-10-25, journal run #262; MSTR-006 §3).
> `08-code-implementation` may begin at "Implementation Tasks" below, test-first.

## Feature Reference

[FS-116 — Role-Scoped Command Catalog & Assignment Scoping](../../features/FS-116-role-scoped-command-catalog.md)

## Re-validation against the tree of 2026-10-25

This package was written on 2026-07-05. About 80 packages have landed since. Every file, class and
function it cites was re-read in the current tree (`claude/release-candidate-1`); what changed, and
what each change means for the build:

| What changed since v1.1 | Effect on this package |
|---|---|
| **Two different "seat" ideas now coexist in the server.** `IP-1068`/`IP-1072`/`IP-1074`/`IP-1076`/`IP-1077`/`IP-1082`/`IP-1130` use "seat" for the *console* seat — the `cell` the caller asserts (`white`/`blue`/`red`/`observer`) via the query string (`_require_white(cell)`) or the body (`_reject_observer(req.cell)`). `FS-116`/`ADS-3500` use "seat" for the *operator seat*: the free-text key of `SessionManager.role_assignments` that `IP-1151` binds to `{asset_or_constellation, role}`. | No design change; a naming hazard. The new field keeps the name `seat` (`ADS-3500` Decision 1 is binding) but every doc string, error text and UI label this package writes says **operator seat** and says it is *not* the console seat. The console-seat rules run first and are untouched (see "Interaction with the existing seat rule"). |
| `POST /order` and `POST /order/validate` already run `_reject_observer(req.cell)` and sit behind `_finite_json_guard_open` (IP-1082's route-table sweep covers every mutating route). They are **not** White-only (players issue orders). | `OrderRequest` gains one optional string field. The guard sweep is unaffected (the field is not numeric), but the sweep and `test_white_only_controls.py` must be re-run. |
| `OrderRequest.actor`/`target` are validated by `_validate_id`; the seat string `IP-1151` accepts is unvalidated free text (`RoleAssignmentRequest.seat: str`, `role: str`). | The new `OrderRequest.seat` is bounded (see task 3). The gate treats an assignment whose `role` is not one of `bus`/`payload`/`both` as granting nothing (fail closed) — `assign_role` is not changed (`IP-1151`'s surface). |
| `SessionManager.role_assignments` is **not in `save_state`** (grep: set in `__init__`, written by `assign_role`, read by `staffing_report`; absent from `save_state`/`from_state`). | A resumed session has no bindings, so with the gate on, every seat-bearing command would be refused after a load. Task 2 makes `save_state` carry `role_assignments` (additive key; a save without it loads as `{}`). See "Owner awareness". |
| `OrderSystem.issue` assigns an `ord-N` id and **registers even a rejected order**; `dry_run` registers nothing. | The role-scope refusal happens in `SessionManager` *before* `osys.issue`, builds a rejected order that is **not** registered and consumes no id (Design Decision 4). No event-log entry, no engine state: replay and determinism are untouched. |
| `app.js`: the command menu is now driven by `actionsFor(a)`, the live dry-run preview `previewOrder()` (IP-1073 latest-edit token), `composeBody()`; the engine's reason codes have a `REASONS` tooltip table; a command palette (`PALETTE`) exists. `VERB_ROLE` and `ROLE_FILTER` are unchanged. | The palette lists assets/time/cells/injects, **not** order verbs — no palette change is needed. New reason codes need two `REASONS` entries. `actionsFor` still does **not** offer `def.escort_posture`, `def.disperse` or `def.set_deception_mode` at all, and offers `pnt.set_integrity` (a `PAYLOAD_VERBS` member) with no `VERB_ROLE` tag (so the manual filter wrongly treats it as `bus`). |
| Test-origin rules (`IP-1330`…`IP-1335`, retag guard `IP-1079`): every test carries `@pytest.mark.verifies(...)` naming a live baseline ID; the RTM Test column is regenerated, never hand-edited. | "Tests to Add" names the IDs per test. `FR-3510` and `FR-3520` are live leaves. The retag guard pins only existing rows; new tests need no row. |
| No shipped vignette declares `roles_needed` (re-checked: zero of the 19). `validate_vignette` (`IP-1310`, `FR-5314`) already requires each entry to name a declared asset id or an `Asset.group`. | Unchanged: with no `roles_needed` the gate never applies, so shipped vignettes are untouched. The "covers" rule below uses the same id-or-group test. |

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-3510 | Order panel offers only role-and-asset-legal commands | The client-side command-list builder (`app.js`'s `actionsFor()`) filters the dotted bus/payload/defense verbs against the acting operator seat's Role Assignment scope whenever the targeted Asset is role-gated (covered by a `roles_needed` entry). The per-verb scope table is served by the server (`GET /roles/scope`) so the client holds no second copy. Unchanged when no `roles_needed` entry covers the Asset or no operator seat is entered. |
| FR-3520 | Role Assignment scope enforced at execution time, independent of the UI filter | `SessionManager.issue_order` (and its dry-run twin `validate_order`) gain a role-scope check — resolving the submitted operator `seat` against `role_assignments` and rejecting an out-of-scope or unassigned verb — before the order ever reaches `OrderSystem`, so a request that bypasses the order panel entirely is rejected identically to one the panel would have hidden. |

## Architecture Components

Per `FS-116`'s own Subsystem Responsibilities and `ADS-3500`'s System Architecture (§2):

- **C2 Session / Application Layer** — `SessionManager`/`InProcessSession` gain the execution-time
  role-scope gate (`FR-3520`), the per-verb scope table, and a read-only scope resolver, applied
  *before* the existing plan-first pipeline (`OrderSystem.issue()`/`dry_run()`) runs. Additive to,
  not a replacement for, `FS-101`/`FS-102`'s existing checks.
- **C4 Operator Console** — `app.js` gains the offer-time filter (`FR-3510`) and a small "operator
  seat" input (today the client tracks the console `CELL` only).
- **C1 Simulation Engine** — untouched. `engine/buscommands.py`'s `can_issue()`/`COMMAND_VERBS`/
  `BUS_VERBS`/`PAYLOAD_VERBS`/`DEFENSE_VERBS` are read (imported), never modified — this package
  adds a session-layer gate in front of the engine's existing catalog (`CLAUDE.md` invariant 2).

## Interfaces

**INT-0004** (Blue/Red Cell Operator ↔ Operator Console) and **INT-0006** (Operator Console →
Session Layer, `SessionAPI`) — both gain an optional operator-`seat` field/parameter in their
concrete realizations, per `ADS-3500` Decision Log entry 1. Fully additive: every existing caller
that omits `seat` (every current test, every currently shipped vignette) is unaffected. One new
read-only route (`GET /api/sessions/{sid}/roles/scope`, a no-cell read like the existing
`GET /roles/staffing`).

## Interaction with the existing seat rule (client-asserted seat model, LAN trust)

The role-scope gate is a **second, independent layer** that sits *inside* the existing rules and
changes none of them:

1. **Order of checks on `POST /order` and `POST /order/validate`:** unknown session (404) →
   Observer console seat refused (403, `_reject_observer(req.cell)`, IP-1130) → non-finite JSON
   (400, `_finite_json_guard_open`) → **new:** role-scope gate (a normal `OrderAck`, `ok=false`, not
   an HTTP error) → the engine's own validation chain (ownership, ROE, window, bus/payload
   availability). The role-scope refusal is therefore an *order refusal with a reason*, shown in the
   same place as every other "why can't I?" reason, not a 403.
2. **Trust level.** The operator `seat` is a client-asserted string, exactly like `cell`, the query
   seat, and `IP-1151`'s `assign_role` caller (`CLAUDE.md` "LAN trust model"). The gate is a real
   structural rejection (it holds for a request that bypasses the UI), but a participant who omits
   `seat`, or names another operator's seat, bypasses it the same way a participant can already
   name another cell. **This adds a rejection rule, not authentication.** Documentation must say so
   (this package updates the `CLAUDE.md` trust paragraph by one sentence).
3. **White Cell.** White issues orders on behalf of an asset's owner (`composeBody()` sets `cell`
   from the asset's owner when `CELL === "white"`). White binds seats (`roles/assign`, White-only by
   the query seat, unchanged) and normally leaves the operator seat empty, so White's orders are
   ungated. If White does type a seat, the gate applies like it would to anyone.
4. **No new White-only or Observer route is added to the mutating surface**; the one new route is a
   read, so `_require_white`/`_reject_observer`/finite-guard route sweeps (IP-1068, IP-1072,
   IP-1082) need no new rows — but they must be re-run (Verification Checklist).

## Files to Create

- `spacesim/tests/test_role_scope_enforcement.py` — the session and HTTP tests below.
- `spacesim/tests/test_role_scope_console_static.py` — a non-browser drift guard that parses
  `static/app.js` (see Tests to Add; runs everywhere, unlike the browser tests).

No new production module — every addition fits the existing `session/manager.py` /
`session/inprocess.py` / `ui_web/server.py` / `ui_web/static/` structure.

## Files to Modify

- `spacesim/session/manager.py`
  - Add the per-verb scope table `ROLE_SCOPE_BY_VERB: dict[str, "bus"|"payload"]` per `ADS-3500` §3:
    `bus` = `BUS_VERBS ∪ {def.frequency_hop, def.patch_cyber, def.set_threat_warning,
    def.maneuver_evade, def.escort_posture, def.disperse}`; `payload` = `PAYLOAD_VERBS ∪
    {def.harden, def.set_deception_mode}`. `BUS_VERBS`/`PAYLOAD_VERBS` are imported from
    `engine/buscommands`, not copied; `DEFENSE_VERBS` itself is never used as a set — only its eight
    members, each named once. A module-level assertion-style check is **not** used (no import-time
    failure); the partition is pinned by a test instead.
  - Add `role_scope_check(seat, order) -> Optional[str]` (pure; returns a reason code or `None`) and
    a covering helper (`_roles_needed_covers(asset)` — a `roles_needed` entry covers an asset when
    its `asset_or_constellation` equals the asset id or the asset's `group`). Reuse
    `_role_covers` for the bus/payload/both matching; reuse the same id-or-group test for "the
    seat's binding covers this asset".
  - `issue_order(self, cell, order, seat=None)` and `validate_order(self, cell, order, seat=None)`:
    when `seat` is given, run `role_scope_check`; on a reason, return a rejected `OrderAck`
    (`ok=False`, `status="rejected"`, `reason=<code>`, `id=""`) built without calling `osys`. When
    `seat` is omitted/empty, or the check returns `None`, the existing line runs unchanged
    (byte-identical).
  - Add `role_scope_for(seat) -> dict` (read-only; `{seat, bound, asset_or_constellation, role,
    verbs, gated_assets, bound_assets}`) for the route below. `gated_assets` = ids of every asset
    covered by any `roles_needed` entry; `bound_assets` = the subset the seat's binding covers.
  - `save_state()` adds `"role_assignments": copy of self.role_assignments`; `from_state()` restores
    it when present, `{}` otherwise (so every save written before this package loads exactly as
    before). `validate_save` accepts the key as optional.
- `spacesim/session/inprocess.py` — `issue_order(self, session, cell, order, seat=None)` and
  `validate_order(...)` thread the parameter; add `role_scope(session, seat)` as a locked read
  (`_locked_read`). `spacesim/session/api.py` (`SessionAPI` Protocol) gains the same optional
  parameter and the read, so the seam stays declared in one place.
- `spacesim/ui_web/server.py` — `OrderRequest` gains `seat: Optional[str] = None` with a length and
  charset bound (letters, digits, `-`, `_`, `.`, space; at most 64 characters) — a value that
  fails is a 422 like a bad `actor`; the `/order` and `/order/validate` routes pass `req.seat`
  through; add `GET /api/sessions/{sid}/roles/scope?seat=…` (no cell, like `/roles/staffing`).
- `spacesim/ui_web/static/app.js`
  - An **Operator seat** text input (new element in `index.html`, near the Actor picker), remembered
    per session in `localStorage` inside `try/catch` (the page must work with storage blocked).
    Empty = no operator seat = no gate (today's behaviour). `composeBody()` adds `seat` only when
    non-empty.
  - On seat change and on session load/refresh of roles, fetch `GET …/roles/scope?seat=` into a
    module variable; `actionsFor(a)` then, **only for dotted bus/payload/defense verbs** and **only
    when `a.id` is in `gated_assets`**, keeps a verb iff `a.id` is in `bound_assets` and the verb's
    scope (from the server's `verbs` table) is covered by the binding's role. The base actions
    (`jam`/`engage`/`observe`/`maneuver`/`downlink`/`cyber`) stay offered, out of scope per `FS-116`.
    The manual `ROLE_FILTER` toggle stays as an extra narrowing, unchanged.
  - Add `VERB_ROLE` entries for the verbs the manual filter mis-tags or omits: `pnt.set_integrity`
    (`"payload"`), `def.escort_posture` (`"bus"`), `def.disperse` (`"bus"`),
    `def.set_deception_mode` (`"payload"`). `def.harden: "payload"` is already right — do not touch.
    (Adding the three `def.*` entries is cosmetic until a later feature offers those verbs in
    `actionsFor`; they are included so the client and server tables cannot drift, pinned by the
    static test.)
  - Add `REASONS` tooltip text for `role_scope_not_assigned` and `role_scope_out_of_scope`, in plain
    language ("this operator seat is not assigned to that asset" / "that command belongs to the
    other role on this asset").
- `spacesim/ui_web/static/index.html` — the operator-seat input.
- `docs/design/05-interface-control-document.md` — `INT-0004`/`INT-0006` entries gain the optional
  `seat` (closes the staleness `ADS-3500` flagged).
- `CLAUDE.md` — one Code Map bullet (role-scope helper, `roles/scope` route, `role_assignments` now
  persisted in a save) and one sentence in the LAN-trust paragraph (the operator seat is
  client-asserted and omitting it skips the gate).
- `ROADMAP.md`, `docs/features/FS-116-…md` `Referenced By` — already reference this package (no
  change beyond the status row).

**Explicitly out of scope** (per `FS-116`'s Scope boundary, carried forward): the base order actions
(`jam`/`engage`/`observe`/`maneuver`/`downlink`/`cyber`) that `engine/orders.py` dispatches directly;
making `seat` mandatory; validating `role` at `assign_role` time; offering
`def.escort_posture`/`def.disperse`/`def.set_deception_mode` in the command menu.

## Implementation Tasks

Authorized — begin here, tests first (each numbered group's tests are written and seen failing before
its code):

1. **Scope table and pure check (`manager.py`).** `ROLE_SCOPE_BY_VERB` and `role_scope_check`. The
   rule, in order:
   a. `seat` empty, or `order.action != "command"`, or the actor asset is unknown, or **no
      `roles_needed` entry covers the actor** → no gate (`None`).
   b. The seat has no binding, or its binding does not cover the actor (id or group), or its `role`
      is not `bus`/`payload`/`both` → `role_scope_not_assigned`.
   c. The verb is not in the table → no gate here (the engine answers `unknown_command`).
   d. The verb's scope is not covered by the binding's role (`both` covers either) →
      `role_scope_out_of_scope`.
2. **Wire `issue_order`/`validate_order`** through `SessionManager` → `InProcessSession` →
   `SessionAPI`; refusal builds an unregistered rejected `OrderAck`. **Persist `role_assignments`**
   in `save_state`/`from_state`.
3. **HTTP:** `OrderRequest.seat` (bounded), pass-through on both order routes, `GET /roles/scope`.
4. **Client:** operator-seat input, `composeBody()`, scope fetch, `actionsFor()` filter, `VERB_ROLE`
   and `REASONS` additions, `previewOrder()` re-run on seat change (it already uses `composeBody()`,
   so a refused command pre-disables **Issue** with the reason through the existing path).
5. **Docs:** ICD entries, `CLAUDE.md`, and the `15-manual-traceability.md` §15.1 impact row — a
   manual-impact finding for `08-training-manual-authoring` (the White and Blue/Red manuals describe
   the order panel); this package does not edit `docs/training/`.
6. Regenerate the RTM Test column (`python3 -m pytest --origin-report=rtm`) in the same commit.

## Tests to Add

Test-first matrix. Every test carries `@pytest.mark.verifies(...)`; the leaves are `FR-3520` for the
enforcement and API tests, `FR-3510` for the offered-list tests, and `IP-1160` only for the package's
own Definition-of-Done regression tests. Fixture: a shipped vignette (`01-leo-isr-denial`, which has
satellites with payloads) loaded through `Vignette.model_validate` with a `roles_needed` block added
in the test (no shipped file is edited), as `test_session_setup.py::_vignette_with_roles` does.

`spacesim/tests/test_role_scope_enforcement.py` *(new)*:

| # | Case | Expectation | Origin |
|---|---|---|---|
| 1 | bus-only binding, payload verb (`isr.collect_now`) sent straight to `issue_order(seat=…)` | rejected, `role_scope_out_of_scope`, nothing registered, order counter unchanged, event log unchanged | FR-3520 |
| 2 | bus-only binding, `def.harden` and `def.set_deception_mode` | rejected (these two are `payload`) | FR-3520 |
| 3 | bus-only binding, `eps.shed_load` and the six `bus`-scoped `def.*` | not role-refused (ack reason is not a `role_scope_*` code; the engine's own answer stands) | FR-3520 |
| 4 | payload-only binding: mirror of 1–3 | mirror | FR-3520 |
| 5 | `both` binding: every `COMMAND_VERBS` member | never role-refused | FR-3520 |
| 6 | seat given, no binding for that seat | `role_scope_not_assigned` | FR-3520 |
| 7 | seat bound to a different asset | `role_scope_not_assigned` | FR-3520 |
| 8 | seat bound to a group id covering the asset | allowed per its role | FR-3520 |
| 9 | binding with `role="admin"` (unknown value) | refused, fail closed | FR-3520 |
| 10 | `seat` omitted, same out-of-scope verb | accepted exactly as today (byte-identical ack) | IP-1160 |
| 11 | asset with no covering `roles_needed` entry, seat given | no gate; byte-identical | IP-1160 |
| 12 | base action (`maneuver`, `observe`, `jam`) with a bus-only seat | no gate | FR-3520 |
| 13 | `validate_order` (dry-run) mirrors 1, 6, 10; registers nothing | same reasons, no state | FR-3520 |
| 14 | table partition: `set(ROLE_SCOPE_BY_VERB) == COMMAND_VERBS`; values only `bus`/`payload`; the `def.*` split is exactly six/two; every `BUS_VERBS`/`PAYLOAD_VERBS` member keeps its own scope | pass | FR-3520 |
| 15 | save → load keeps `role_assignments`; a pre-change save (key absent) loads with `{}` and behaves as today | pass | IP-1160 |
| 16 | determinism: a session driven with accepted role-scoped orders replays byte-identically; refused orders leave the event log untouched | pass | IP-1160 |
| 17 | HTTP: `POST /order` with `seat` refused → 200 with `ok=false` and the reason (not 403/422); Observer console seat still 403 first; over-long/odd `seat` → 422; `GET /roles/scope` shape; `roles/assign` still White-only | pass | FR-3520 |
| 18 | HTTP: a request omitting `seat` is unchanged for all six base actions and a bus verb (regression for the 19 shipped vignettes — iterate the shipped list with no `roles_needed`) | pass | IP-1160 |

`spacesim/tests/test_role_scope_console_static.py` *(new, runs without a browser)*:

| # | Case | Origin |
|---|---|---|
| 19 | parse `VERB_ROLE` out of `app.js`; for every dotted verb, its tag (`sda` counts as `payload`) equals `ROLE_SCOPE_BY_VERB` | FR-3510 |
| 20 | `app.js` `composeBody()` source references `seat`, `REASONS` has both new codes, `index.html` has the operator-seat input | FR-3510 |

`spacesim/tests/test_browser_console_rules.py` *(modified; `browser` marker, skips loudly without
Playwright/Chromium — the existing `skip` reason mechanism)*. Add one fixture variant of
`01-leo-isr-denial` with `roles_needed` (a `content` fixture variant, like the existing two) and
three tests tagged `@pytest.mark.verifies("FR-3510", "NFR-2840")`:

| # | Case |
|---|---|
| 21 | Blue console, operator seat bound bus-only to the satellite: the Action dropdown contains `eps.shed_load` and no `isr.*`/`def.harden`; payload-only seat: the mirror; `both`: all |
| 22 | Seat field empty: the dropdown is identical to today's (the full list) |
| 23 | With a bus-only seat, a directly typed payload verb (the params box path) leaves **Issue** disabled with the role-scope reason text before any send |

Existing tests that need changes: **none require `?cell=` or role changes** — every current caller
omits `seat`. The ones that must be *re-run* because they enumerate the route table or the request
models: `test_white_only_controls.py`, `test_white_only_extension.py`, `test_white_control_nonfinite.py`
(IP-1082 sweeps), `test_observer.py`, `test_session_setup.py`, `test_bus_commands.py`,
`test_vignette_tutorials.py`, `test_content.py`, `test_origin_retag.py`, `test_test_origins.py`,
`test_doc_integrity.py`. The retag guard pins only existing rows, so new tests add none; if
`test_bus_commands.py` is touched its pinned tags stay as they are.

Permanent gates (Verification Checklist): `test_determinism.py`, `test_import_guard.py`.

## Documentation Updates

- `docs/design/05-interface-control-document.md` — `INT-0004`/`INT-0006` gain `seat`.
- `CLAUDE.md` — Code Map bullet and the LAN-trust sentence (above).
- `ROADMAP.md` — this package's row (status `READY`); the generated RTM Test column for
  `FR-3510`/`FR-3520` (`--origin-report=rtm`).
- `docs/training/15-manual-traceability.md` §15.1 and the White/Blue manuals' order-panel sections —
  routed to `08-training-manual-authoring` as a manual-impact finding; **not written here**.

## Definition of Done

- [ ] `SessionManager.issue_order`/`validate_order` and the `InProcessSession`/`SessionAPI` wrappers
  accept an optional operator `seat`; every existing call site that omits it behaves byte-identically.
- [ ] A `bus-only`/`payload-only`/`both` Role Assignment gates command acceptance at `issue_order`
  and `validate_order`, independent of whether the command was offered client-side (`FR-3520`).
- [ ] The offered command list is filtered to the seat's scope when it covers a role-gated asset,
  and the client and server verb tables cannot drift (`FR-3510`, static test 19).
- [ ] Every `DEFENSE_VERBS` member is treated per its individual classification — six `bus`, two
  `payload` (`def.harden`, `def.set_deception_mode`) — in the server table and the client tags.
- [ ] A refusal registers no order, consumes no order id and writes nothing to the event log.
- [ ] `role_assignments` survives save/resume; a save without the key still loads.
- [ ] Every one of the 19 shipped vignettes (none declaring `roles_needed`) is unaffected.
- [ ] `INT-0004`/`INT-0006` updated; `CLAUDE.md` updated; RTM Test column regenerated.
- [ ] The Observer console-seat 403 and the White-only seat rule are unchanged (test 17).

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] Both new test modules exist and are green; the browser tests either pass or skip loudly.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green (session-layer,
  read-time-only — no engine mutation, no RNG use, no wall-clock read).
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green (`session/` imports the
  verb sets from `engine/`, the established direction; nothing new in `engine/`).
- [ ] Full suite re-run with zero regressions against the baseline recorded at the start of the
  build (the suite has grown well past the 566 recorded when this package was first written).
- [ ] `python3 -m pytest spacesim/tests/test_test_origins.py spacesim/tests/test_doc_integrity.py`
  green (every new test names `FR-3510`/`FR-3520`/`IP-1160`; no broken link; ledgers agree).
- [ ] The IP-1068/IP-1072/IP-1082 route-table sweeps pass with no new row needed.
- [ ] Independently re-derive (not merely re-cite) the `DEFENSE_VERBS` split by reading
  `ROLE_SCOPE_BY_VERB` and `engine/buscommands.apply_command`.
- [ ] A refused order leaves `orders`, the order counter and the event log exactly as before.
- [ ] A save written before this package (no `role_assignments`) loads and plays unchanged.

## Dependencies

- **Upstream:** [FS-116](../../features/FS-116-role-scoped-command-catalog.md) v1.2 and
  [ADS-3500](../../architecture/ADS-3500-role-scoped-command-enforcement.md) v1.1 (closed);
  [IP-1151](IP-1151-seat-role-assignment.md), [IP-1050](IP-1050-spacecraft-operations-bus-payload.md),
  [IP-1051](IP-1051-spacecraft-operations-effects-console.md) — all `VERIFIED`. **Authorization on
  record** (run #262), so the package is `READY`.
- **Downstream:** none. Closes `FEAT-3500`, the last Must-priority Feature in Release 1 without code.
  `11-release-readiness` is re-run once this package and `IP-1083` are `VERIFIED`.
- **Build ordering:** see below.

## Build ordering (relative to IP-1083)

`IP-1083` (rewind keeps future White injects) and this package are **independent** — neither needs the
other's behaviour — but both edit `session/manager.py`'s `save_state`/`from_state`. Recommended:
**`IP-1083` first, then `IP-1160`.** `IP-1083` is the smaller change and has no UI work; `IP-1160`
then adds its `role_assignments` key to a `save_state` that already carries `IP-1083`'s event-log
entries, and rebases over `fire_inject`/`_h_inject_admin` edits it does not touch. If they must be
built in parallel the only expected conflict is the `save_state`/`from_state` hunk (one dictionary key
each). `IP-1160` does not touch `engine/orders.py`; the older note that it "also edits `_validate`"
(TWBS, `IP-1052`/`IP-1320`) no longer applies.

## Owner awareness (no blocking decision)

`FS-116`'s two Open Questions are closed (`ADS-3500`). No owner decision blocks the build. Two points
are recorded for the owner's awareness, each with the default this package builds:

1. **`seat` stays optional** (`ADS-3500` §9 Q1, residual). Consequence: a participant who omits
   `seat` skips the gate (LAN trust). `FR-3520`'s acceptance test ("a payload-verb command submitted
   directly under a bus-only scope is rejected") is met for any request that names its seat. If the
   owner wants the gate to hold against an omitted seat on role-gated assets, that is a requirements
   change (`04`) and a one-line follow-up here.
2. **`role_assignments` is added to the save** (Files to Modify). Without it `FR-3520` silently stops
   working after a resume. It is additive and loads old saves unchanged. If the owner would rather keep
   saves out of this feature, strike task 2's persistence and accept that a resumed session needs
   White to re-bind seats.

## Risks

- **Undelivered Must feature** (carried forward from `FS-116`): this package is the first concrete
  step closing the gap, not a routine addition.
- **Name collision "seat"** (see Re-validation): a builder who reuses `_require_white(cell)`'s idea of
  a seat for this field will build the wrong thing. The tests and error texts use "operator seat".
- **The client filter is a convenience, the server gate is the control.** `VERB_ROLE`/`ROLE_FILTER`
  remain a client-only display filter; the new automatic filter reads the server's table, so a drifted
  client map can only mis-offer, never mis-enforce. Static test 19 pins the two together.
- **`actionsFor` offers a verb the server table scopes differently** (found: `pnt.set_integrity`
  untagged). Fixed by the added tags and pinned by test 19.
- **Resumed sessions** lose bindings unless task 2 lands (see Owner awareness 2).
- **A session that never binds seats** but whose vignette declares `roles_needed` and whose
  participants type a seat will see every command refused for that seat — correct per the rule, and
  the reason text says why.
- **Browser tests skip where Playwright/Chromium is absent**; the non-browser static test 19–20 and the
  HTTP tests carry the verification in that case.

## Rollback Considerations

Every change is additive and gated on an optional parameter defaulting to `None`, or on a
`roles_needed` entry that no shipped vignette declares. Reverting the helper, the parameter across the
three wrappers and `OrderRequest`, the new route, the client seat input and the `actionsFor` filter
restores today's behaviour. The only persisted addition is the `role_assignments` key in a save, which
older code ignores. The `VERB_ROLE`/`REASONS` additions are cosmetic client data and revert on their
own.
