# IP-1151 — Session Setup: Seat-to-Role Assignment

> **Package ID:** IP-1151
> **Version:** 1.0
> **Status:** 🔴 BLOCKED *(on [IP-1150](IP-1150-vignette-selection.md) reaching `VERIFIED`, per
> FR-4210's own stated Precondition — "A Vignette is loaded (FR-4110)" — and this plan's
> READY-requires-VERIFIED-dependency rule. **MSTR-006 §3 authorization obtained 2026-07-03**
> (project owner, recorded in `docs/pipeline/pipeline-journal.md` run #2) — this package is
> pre-cleared to start the moment `IP-1150` reaches `VERIFIED`; authorization does not itself lift
> the `IP-1150` dependency gate.)*
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

> **This is a forward-design package: the capability described here does not exist in `spacesim/`
> today.** Per MSTR-006 §3, this document's own specification was not itself an authorization to
> write code — that separate, explicit user go-ahead was obtained 2026-07-03 (see the Status field
> above). Coding still waits on [IP-1150](IP-1150-vignette-selection.md) reaching `VERIFIED`
> (a functional gate, not an authorization gate).

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
5. **Explicitly resolve before implementation begins** (open design question, not yet answered):
   the exact unsatisfied-`roles_needed` report format (FS-115's own Open Questions flags this as
   unspecified in the requirements baseline), and behavior for an invalid parameter-override value
   at vignette selection (a sibling open question that belongs to
   [IP-1150](IP-1150-vignette-selection.md)'s scope if resolved, not this package's).
6. **Explicitly do not implement** in this package: runtime enforcement of an assigned Role
   Assignment's scope once the exercise is running — that is
   [FS-105](../../features/FS-105-spacecraft-operations.md)'s/`FEAT-3500`'s concern (already
   `VERIFIED` via `IP-1050`/`IP-1051` for the *command-filtering* consequence of a Role Assignment;
   this package only *produces* the Role Assignment record, per FS-115's own Scope boundary).

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
- `docs/features/FS-115-session-setup.md`'s `Referenced By` metadata — add this package (alongside
  `IP-1150`, cross-link only).
- `CLAUDE.md`'s Code Map — no new module proposed; no addition needed until implementation reveals
  otherwise.
- Vignette-authoring reference documentation (wherever the `Vignette` schema's fields are
  documented for content authors, e.g. `docs/design/04-data-model.md` §6) should gain a
  `roles_needed` entry once implemented — not performed by this package, which contains no code
  changes.

## Definition of Done

*(Forward-looking gate — the authorization item below is now true; the rest is not yet.)*

- [x] **Explicit user authorization obtained** for this package's Implementation Tasks (MSTR-006
  §3, 2026-07-03, project owner, recorded in `docs/pipeline/pipeline-journal.md` run #2) — still
  waits on [IP-1150](IP-1150-vignette-selection.md) reaching `VERIFIED` before work may begin.
- [ ] `Vignette.roles_needed` exists and defaults to an empty/absent list (no breakage of the 19
  existing vignette YAML files, none of which declare it).
- [ ] Seat-to-role assignment against a vignette's `roles_needed` produces Role Assignment records
  consumable by `FS-105`'s existing command-filtering mechanism.
- [ ] An unmet mandatory `roles_needed` entry is reported as unsatisfied and hard-blocks exercise
  start — not merely an advisory warning.
- [ ] A vignette with no `roles_needed` declared is never blocked from starting by this mechanism.

## Verification Checklist

*(To be executed once implemented; not yet applicable.)*

- [ ] `spacesim/tests/test_session_setup.py` exists and is green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green (this package's staffing
  gate must be a pre-start check, not something the deterministic core depends on).
- [ ] Re-run every existing vignette-loading test (`spacesim/tests/test_content.py`,
  `spacesim/tests/test_vignette_tutorials.py`) and confirm none regresses from the additive
  `roles_needed` field.
- [ ] Manual review confirms the produced Role Assignment record shape is actually consumable by
  the existing `FS-105`/`IP-1050` command-filtering mechanism (FS-115's own Dependencies field
  names `IP-1050`... actually `FS-105` as "the nearest downstream consumer" — confirm the
  interface, don't assume it).

## Dependencies

- **Upstream:** [IP-1150](IP-1150-vignette-selection.md) (vignette must be loaded first — this
  package's `roles_needed` gate has nothing to validate against before a vignette is selected) —
  `COMPLETE`, not yet `VERIFIED`; this package stays `BLOCKED` until `IP-1150` clears
  `09-package-verification`, consistent with this plan's own READY-requires-VERIFIED rule (mirrors
  how `IP-3010` stays `BLOCKED` on `IP-2010` reaching `COMPLETE`/`VERIFIED` in this same plan).
- **Downstream:** [FS-105](../../features/FS-105-spacecraft-operations.md)/`IP-1050`/`IP-1051`
  (already `VERIFIED`) are the consumers of the Role Assignment records this package would produce
  — no code change proposed to those packages by this one; FS-115's own Scope explicitly excludes
  runtime enforcement from this Feature.
- **Build-sequencing:** Must follow `IP-1150` to `VERIFIED`; independent of `IP-1120`/`IP-1130`/
  `IP-1140`.

## Risks

- **Authorization risk (resolved 2026-07-03):** MSTR-006 §3's explicit, separate user go-ahead is
  now on record in the pipeline journal — the remaining gate is functional (`IP-1150` → `VERIFIED`),
  not authorization.
- **Backward-compatibility risk if Implementation Task 1 is done carelessly:** all 19 existing
  vignette YAML files declare no `roles_needed` — if the staffing gate does not treat an absent
  list as "nothing mandatory," every existing vignette becomes unstartable the moment this package
  ships, a severe regression this package's design explicitly guards against (see Definition of
  Done and Tests to Add).
- **Report-format and downstream-consumption open questions are genuinely unresolved,** not
  merely deferred detail — FS-115's own Open Questions flags the report format as unspecified in
  the requirements baseline, and this package's own Verification Checklist calls out that the
  produced Role Assignment record's actual consumability by `FS-105`'s mechanism should be
  confirmed, not assumed, before this package is considered done.
- **RTM `Impl. Package` column shows `FR-4210` as `UNASSIGNED`**, consistent with this package
  filling that gap for the first time — no conflicting prior citation to reconcile.

## Rollback Considerations

Since this package proposes an additive schema field (`roles_needed`, optional/absent-safe) and new
registry/gate logic, rollback is low-complexity: removing the new field, registry, and gate fully
reverts to the current unstaffed-start-allowed behavior, with no data-migration concern for any
existing save file or vignette (none currently populate `roles_needed`).
