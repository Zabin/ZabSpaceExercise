# IP-1151 — Session Setup: Seat-to-Role Assignment

> **Package ID:** IP-1151
> **Version:** 1.1 (2026-07-03 — implemented by `08-code-implementation`; see Status below.)
> **Status:** ✅ VERIFIED *(2026-07-04, run #15, [`VR-1151`](../verification/VR-1151-seat-role-assignment.md)
> — every Definition of Done and Verification Checklist item independently re-confirmed against
> the live tree; full suite 566 passed/3 skipped, both permanent gates green. `BL-0014`'s negative
> finding (no role-based command-filtering consumer exists anywhere in the codebase) was
> independently re-derived, not merely re-cited, and is still true — `role_assignments` remains
> read only by `staffing_report()`. One new Low finding (`BL-0024`): `assign_role`'s White-Cell-only
> gate is tested against `cell="blue"`, not `cell="observer"` specifically — a test-coverage gap,
> not a functional one. This closes the "iterate through all `09-package-verification`" sweep: all
> 18 packages are now `VERIFIED` (`IP-1140` with a standing user-accepted-risk note). Was 🔵
> COMPLETE *(implemented 2026-07-03 — `Vignette.roles_needed`/`RoleRequirement`
> (additive, absent for all 19 existing vignettes), `SessionManager.assign_role`/`staffing_report`,
> `InProcessSession.start()` hard-gated on any unmet mandatory entry (not merely advisory),
> `/roles/assign`+`/roles/staffing` endpoints, a White-Cell-only seat-assignment UI step. Full
> suite green (559 passed/3 skipped, up from 547/3 — 12 new tests), both permanent gates green,
> all existing vignette-loading tests re-run and green. Entered `COMPLETE`, not `VERIFIED` — only
> `09-package-verification` may write `VERIFIED`. **One Definition-of-Done item cannot be cleanly
> checked: item 2's "consumable by FS-105's existing command-filtering mechanism" — this run found
> no role-based command-filtering mechanism anywhere in the codebase to be consumed by; see Risks
> below and the Master Build Plan's Risk item 8.** Was 🔴 BLOCKED *(on
> [IP-1150](IP-1150-vignette-selection.md) reaching `VERIFIED`, per FR-4210's own stated
> Precondition — cleared 2026-07-03, run #3, `VR-1150`. **MSTR-006 §3 authorization obtained
> 2026-07-03** (project owner, recorded in `docs/pipeline/pipeline-journal.md` run #2).)*)*)*
> **Dependencies:** FS-115 (FR-4210 slice), [IP-1150](IP-1150-vignette-selection.md) (vignette must
> be loaded first, per FR-4210's own Preconditions)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** Role Assignment records [FS-105](../../features/FS-105-spacecraft-operations.md)
> later enforces at runtime
> **Feature Reference:** [FS-115 — Session Setup: Vignette Selection & Seat Assignment](../../features/FS-115-session-setup.md) (FR-4210 portion)
> **Supersedes:** none — new package, sibling to [IP-1150](IP-1150-vignette-selection.md)
> **Related Topics:** [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*FS-115 covers two Feature Catalog entries. This package covers the `FEAT-4200`/FR-4210 half —
seat-to-role assignment against a vignette's declared `roles_needed`, with a hard gate against a
silently understaffed start. `07-implementation-planning`'s build-status verification pass
(`docs/implementation/01-technical-work-breakdown.md` Tranche 1) found this half **not built at
all**: no `roles_needed` field exists on the `Vignette` model, and the current seat/cell selector
(`app.js:406` `setCell`) is a flat White/Blue/Red picker with no per-Asset/constellation role
binding or staffing gate. See [IP-1150](IP-1150-vignette-selection.md) for the sibling,
already-built FR-4110 half.*

## Package ID

IP-1151

## Title

Session Setup: Seat-to-Role Assignment (FS-115, FR-4210 slice)

## Objective

Let White Cell bind each operator seat to one or more roles (bus, payload, or both) against a
specific Asset/constellation, informed by the vignette's declared `roles_needed`, and refuse to let
the exercise start while a mandatory `roles_needed` entry has no bound seat.

> **This was authored as a forward-design package: the capability did not exist in `spacesim/` at
> authoring time.** Per MSTR-006 §3, this document's own specification was not itself an
> authorization to write code — that separate, explicit user go-ahead was obtained 2026-07-03 (see
> the Status field above), and `08-code-implementation` has since implemented the tasks below
> (2026-07-03, see Status).

## Feature Reference

[FS-115 — Session Setup: Vignette Selection & Seat Assignment](../../features/FS-115-session-setup.md) (FR-4210 portion only — see IP-1150 for FR-4110)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-4210 | Seat-to-role assignment at setup | Adds a `roles_needed` declaration to the `Vignette` schema (a list of mandatory/optional `{asset_or_constellation, role}` entries), a White-Cell-facing seat-assignment step consuming it, and a hard gate on session start that reports any unmet mandatory entry rather than allowing a silently understaffed exercise to begin. |

## Architecture Components

- **C5 Content & Data** — `content/vignette.py`'s `Vignette` schema gains a `roles_needed` field
  (vignette-authoring surface, consumed here per FS-115's own Subsystem Responsibilities: "supplied
  here, not owned here").
- **C2 Session / Application Layer** — `session/manager.py`'s `SessionManager` gains a Role
  Assignment registry and the start-time staffing gate.
- **C4 Operator Console** / **C6 White Cell** — `ui_web/server.py`/`ui_web/static/app.js` gain a
  seat-assignment UI step (per-seat, per-Asset/constellation, bus/payload/both) and the
  unsatisfied-`roles_needed` report surface.

## Interfaces

**INT-0002** (White Cell Facilitator ↔ Operator Console, exercise control) — the same interface
[IP-1150](IP-1150-vignette-selection.md) uses; seat assignment is the second White-Cell-only
setup-phase step over it, sequenced after vignette selection per FR-4210's own Dependencies
(`FR-4110`).

## Files to Create

None proposed — additions fit within existing `content/vignette.py`/`session/manager.py` structure
(mirrors `IP-1130`'s restraint principle).

## Files to Modify

- `spacesim/content/vignette.py` *(proposed)* — add a `roles_needed: list[dict]` field to
  `Vignette` (each entry: `{asset_or_constellation: str, role: Literal["bus","payload","both"],
  mandatory: bool}` or equivalent), consistent with the existing `Parameter`/`Inject` model pattern
  already used for other declarative vignette-authoring fields in this same file.
- `spacesim/session/manager.py` *(proposed)* — add a Role Assignment registry (seat → {asset/
  constellation, role} bindings) and a `staffing_report()`-equivalent method returning any unmet
  mandatory `roles_needed` entry; gate `start()` (or the caller of it) on that report being empty,
  per FR-4210's Acceptance Criteria ("reports it as unsatisfied rather than allowing the exercise
  to start silently understaffed" — a hard gate, not merely an advisory warning per FS-115's own
  System Behaviour).
- `spacesim/ui_web/server.py` *(proposed)* — a seat-assignment endpoint (accepts a seat → role
  binding), and a staffing-report endpoint the setup UI polls before enabling `Start`.
- `spacesim/ui_web/static/app.js` *(proposed)* — a seat-assignment step in the session-setup flow
  (after vignette selection, per FR-4210's own sequencing dependency on FR-4110), reading the
  vignette's `roles_needed` and presenting the unsatisfied-entry report if applicable.

## Implementation Tasks

**Not started — not authorized (MSTR-006 §3).** The following is the proposed task sequence for
when authorization is granted:

1. Add the `roles_needed` field to the `Vignette` schema; update the vignette-authoring
   documentation/schema reference (not the 19 existing vignette YAML files themselves — the field
   is optional/additive, and an absent `roles_needed` list should be treated as "no mandatory
   staffing requirement," not an error, to avoid breaking every existing vignette).
2. Implement the Role Assignment registry on `SessionManager` and the seat → {asset/constellation,
   role} binding operation.
3. Implement the staffing-report check (any mandatory `roles_needed` entry with no bound seat) and
   gate exercise start on it being empty.
4. Add the seat-assignment UI step and the unsatisfied-entry report surface, sequenced after
   vignette selection in the setup flow.
5. **Resolved 2026-07-03 by `08-code-implementation`** (was an open design question): the
   unsatisfied-`roles_needed` report format is a `list[dict]`, one entry per unmet mandatory
   requirement, shaped identically to a `roles_needed` entry itself
   (`{asset_or_constellation, role, mandatory}`) — a low-stakes implementation-level choice
   (unlike, e.g., `IP-2010`'s `BL-0002` aware/unaware question), not escalated to the user, since
   no genuinely different design philosophy was at stake, just a data shape. The sibling
   parameter-override open question remains [IP-1150](IP-1150-vignette-selection.md)'s to resolve,
   untouched here.
6. **Explicitly do not implement** in this package: runtime enforcement of an assigned Role
   Assignment's scope once the exercise is running — that is
   [FS-105](../../features/FS-105-spacecraft-operations.md)'s/`FEAT-3500`'s concern. **Correction
   (2026-07-03, `08-code-implementation`): the parenthetical claim that this "already `VERIFIED`
   via `IP-1050`/`IP-1051` for the *command-filtering* consequence of a Role Assignment" was
   checked against the live code during implementation and found to be false** — no role-based
   (bus/payload/both) command-authorization concept exists anywhere in `FS-105`, `IP-1050`,
   `IP-1051`, `buscommands.py`, or `session/manager.py`; every existing command check is
   `cell`-based (blue/red/white ownership), not role-based. This does not change this package's own
   scope (it still only *produces* the Role Assignment record, per FS-115's own Scope boundary) —
   but the record currently has no consumer at all. See Risks below and the Master Build Plan's
   Risk item 8.

## Tests to Add

*(Proposed — none exist yet; write test-first per `CLAUDE.md`'s mandatory workflow once
authorized.)*

- `spacesim/tests/test_session_setup.py` *(new)* — one test per Acceptance Criterion:
  - Given a vignette with a mandatory `roles_needed` entry and no seat bound to it, the staffing
    report includes that entry as unsatisfied, and exercise start is refused.
  - Given every mandatory `roles_needed` entry has a bound seat, the staffing report is empty and
    exercise start succeeds.
  - Given a vignette with no `roles_needed` declared at all (the common case for all 19 existing
    vignette YAML files), the staffing report is trivially empty and start is not blocked — a
    backward-compatibility check this task's design explicitly requires (see Implementation Tasks
    item 1).

## Documentation Updates

- `ROADMAP.md` Implementation Packages theme — add this package's row.
- `docs/features/FS-115-session-setup.md`'s `Referenced By` metadata — already present (added at
  authoring time; verified unchanged).
- `CLAUDE.md`'s Code Map — a brief addition made (`content/vignette.py`'s `RoleRequirement`,
  `session/manager.py`'s `assign_role`/`staffing_report`), deviating from this field's original
  "no addition needed" per that clause's own escape valve, mirroring `IP-1120`/`IP-1130`'s
  precedent this same session.
- Vignette-authoring reference documentation — `docs/design/04-data-model.md` §6 gained a
  `RoleRequirement`/`roles_needed` entry, per this field's own instruction ("once implemented").

## Definition of Done

*(Implemented 2026-07-03 by `08-code-implementation`; independently re-confirmed 2026-07-04 by
`09-package-verification` — [`VR-1151`](../verification/VR-1151-seat-role-assignment.md) — every
item below is confirmed against the shipped code and tests, with one caveat on item 2 (see Status
above and Risks below, re-derived rather than re-cited by `VR-1151`).)*

- [x] **Explicit user authorization obtained** for this package's Implementation Tasks (MSTR-006
  §3, 2026-07-03, project owner, recorded in `docs/pipeline/pipeline-journal.md` run #2).
  [IP-1150](IP-1150-vignette-selection.md) reached `VERIFIED` 2026-07-03 (run #3, `VR-1150`),
  clearing the dependency gate this item used to note as still open.
- [x] `Vignette.roles_needed` exists and defaults to an empty/absent list (no breakage of the 19
  existing vignette YAML files, none of which declare it).
- [~] Seat-to-role assignment against a vignette's `roles_needed` produces Role Assignment records
  (`SessionManager.role_assignments`, `{asset_or_constellation, role}` per seat) in a plausible,
  self-consistent shape — **but "consumable by `FS-105`'s existing command-filtering mechanism" is
  not satisfied as literally stated: no such mechanism exists in the shipped code** (see
  Implementation Tasks item 6's correction and Risks below). The record is produced; nothing
  currently reads it.
- [x] An unmet mandatory `roles_needed` entry is reported as unsatisfied and hard-blocks exercise
  start — not merely an advisory warning (`InProcessSession.start()` returns `Ack(ok=False, ...)`
  before `SessionManager.start()` is ever called).
- [x] A vignette with no `roles_needed` declared is never blocked from starting by this mechanism
  (verified against `leo-isr-denial` and all 19 shipped vignettes via the re-run existing-vignette
  tests).

## Verification Checklist

*(Executed 2026-07-04 by `09-package-verification` —
[`VR-1151`](../verification/VR-1151-seat-role-assignment.md).)*

- [x] `spacesim/tests/test_session_setup.py` exists and is green — 12 tests.
- [x] `python3 -m pytest spacesim/tests/test_determinism.py` remains green (this package's staffing
  gate is a pre-start check in `session/`/`ui_web/`, not part of the deterministic core).
- [x] Re-run every existing vignette-loading test (`spacesim/tests/test_content.py`,
  `spacesim/tests/test_vignette_tutorials.py`) — 35 total passed with `test_session_setup.py`, no
  regression from the additive `roles_needed` field.
- [x] **Independently re-derived by `09-package-verification` (`VR-1151`), result unchanged: no.**
  Manual review confirms the produced Role Assignment record shape is **not** consumable by any
  `FS-105`/`IP-1050` command-filtering mechanism, because no such mechanism exists at all — every
  command check in the codebase is `cell`-based, not role-based (`role_assignments` is read only
  by `staffing_report()`). This checklist item correctly remains unsatisfied as literally stated;
  see `VR-1151`'s re-confirmation of `BL-0014`.

## Dependencies

- **Upstream:** [IP-1150](IP-1150-vignette-selection.md) (vignette must be loaded first — this
  package's `roles_needed` gate has nothing to validate against before a vignette is selected) —
  `VERIFIED` 2026-07-03 (`VR-1150`, run #3); this package's dependency gate cleared that same day.
- **Downstream:** **Corrected 2026-07-03 (`08-code-implementation`, run #8) — this claim was
  checked against the live code and found false.** [FS-105](../../features/FS-105-spacecraft-operations.md)/
  `IP-1050`/`IP-1051` do **not** currently consume Role Assignment records — no role-based
  command-filtering mechanism exists in the shipped code today (command authorization is entirely
  `cell`-based). The Role Assignment records this package produces have no consumer yet. FS-115's
  own Scope still explicitly excludes runtime enforcement from this Feature, so this package's own
  scope is unaffected — but the downstream relationship this field originally asserted does not
  exist and should not be relied upon until a future package actually builds it.
- **Build-sequencing:** Followed `IP-1150` to `VERIFIED`, as planned; independent of `IP-1120`/
  `IP-1130`/`IP-1140`.

## Risks

- **Authorization risk (resolved 2026-07-03):** MSTR-006 §3's explicit, separate user go-ahead is
  now on record in the pipeline journal, and the package has since been implemented (`COMPLETE`).
- **Backward-compatibility risk (mitigated, verified by test):** all 19 existing vignette YAML
  files declare no `roles_needed` — the staffing gate treats an absent/empty list as "nothing
  mandatory," verified by `test_existing_vignette_starts_without_any_role_assignment` and by
  re-running every existing vignette-loading test with no regression.
- **Report format — resolved 2026-07-03** (see Implementation Tasks item 5): a `list[dict]`
  mirroring `roles_needed`'s own entry shape, a low-stakes implementation choice, not escalated.
- **Downstream-consumption claim — resolved 2026-07-03, and the resolution is itself the finding:**
  not merely confirmed-or-not as this package originally framed it, but affirmatively **false as
  stated**. No role-based command-filtering mechanism exists anywhere in `FS-105`/`IP-1050`/
  `IP-1051`/`buscommands.py`/`session/manager.py`. This is now the standing risk item (see
  Dependencies above and the Master Build Plan's Risk item 8) — a future package would need to
  actually build FS-105-side consumption if runtime role enforcement is still wanted; until then,
  the Role Assignment record is produced but unused.
- **RTM `Impl. Package` column for `FR-4210` was `UNASSIGNED`, now filled** (2026-07-03, `IP-1151`)
  — no conflicting prior citation existed to reconcile.

## Rollback Considerations

*(Updated 2026-07-03 to reflect what actually shipped, not just what was proposed.)*

This package's schema field (`Vignette.roles_needed`, optional/absent-safe) and its registry/gate
logic remain additive, so rollback stays low-complexity: reverting `content/vignette.py`'s
`RoleRequirement`/`roles_needed` addition, `session/manager.py`'s `assign_role`/`_role_covers`/
`staffing_report`, and the `InProcessSession.start()` staffing check fully restores the prior
unstaffed-start-allowed behavior, with no data-migration concern for any existing save file or
vignette (none of the 19 shipped vignettes populate `roles_needed`).

The shipped surface is broader than originally proposed and rollback must cover all of it:
- `spacesim/ui_web/server.py`'s `RoleAssignmentRequest` model and the `/roles/assign` +
  `/roles/staffing` endpoints — reverting these has no effect on any other route (they are net-new,
  not modifications of existing ones).
- `spacesim/ui_web/static/app.js`'s seat-assignment wiring (`$("role-assign").onclick`,
  `refreshStaffingReport()`) and `index.html`'s "Seat-to-role assignment" menu section — purely
  additive UI; removing them leaves the rest of the session-menu unaffected.
- The `start()` bug fix in `app.js` (the client previously ignored the `/start` Ack's `ok` field
  entirely). **This fix is not separable from this package's gate**: without it, a refused
  `Ack(ok=False, ...)` from the new server-side staffing gate would be silently swallowed by the
  client, so a rollback that removes the server-side gate but leaves the client fix in place is
  safe (the fix simply becomes dormant), while a rollback that removes the client fix but keeps the
  server-side gate would silently break the UI's Start button. Roll back both together, or the
  server-side gate alone with the client fix left in place — never the client fix alone.
- `spacesim/tests/test_session_setup.py` (new file) would be deleted wholesale; no other test file
  was modified by this package.

No data-migration concern in any direction: `role_assignments` is in-memory `SessionManager` state,
not persisted to `save_state()`/`from_state()`, so no existing save file encodes it and none would
need migrating on rollback.
