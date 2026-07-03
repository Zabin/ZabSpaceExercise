# FS-115 — Session Setup: Vignette Selection & Seat Assignment

> **Document ID:** FS-115
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [DOM-003](../domains/DOM-003-white-cell-framework.md), [FS-105](FS-105-spacecraft-operations.md) (Role Assignment scope this Feature produces), `FEAT-5300` (vignette validation, not yet its own Feature Specification)
> **Referenced By:** [docs/feature-planning/03-feature-catalog.md](../feature-planning/03-feature-catalog.md) `FEAT-4100`/`FEAT-4200`, [docs/feature-planning/05-feature-review.md](../feature-planning/05-feature-review.md) Finding F-10
> **Produces:** the started, staffed Session that every other Feature Specification's workflows begin from
> **Feature Mapping:** FS-115 (this document)
> **Related Topics:** [FS-106](FS-106-white-cell-dashboard.md) (the in-session facilitator console this setup phase precedes), [FS-112](FS-112-classification-banner.md) (the banner set during this same scenario-build workflow)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template. It is a **new**
Feature Specification closing Finding F-10 in `docs/feature-planning/05-feature-review.md`,
discovered while splitting `FS-106`: reading that document's actual v1.0 content showed it never
covered vignette selection or seat assignment at session setup at all, despite both having real,
Must-priority baselined FRs (FR-4110, FR-4210). This document covers both together, rather than as
two separate specs, because they are sequential, White-Cell-only, session-setup-phase steps with a
direct dependency edge between them in the Feature Catalog (`FEAT-4200 → FEAT-4100`) and no
independent value apart from each other — per this skill's own guidance against a Feature "too
small" to stand alone.*

## Feature ID

FS-115

## Title

Session Setup: Vignette Selection & Seat Assignment

## Purpose

Let White Cell select a vignette, tune its parameters, and bind operator seats to roles per the
vignette's declared `roles_needed` before an exercise starts — refusing to let a mandatory role go
silently unstaffed — per `docs/feature-planning/03-feature-catalog.md` `FEAT-4100`/`FEAT-4200`'s
own Purpose fields.

## Scope

In scope: selecting a vignette and applying optional parameter overrides (every unmodified
parameter takes its documented default); assigning each operator seat to one or more roles
(bus/payload/both) per Asset/constellation, per the vignette's `roles_needed`; reporting an unmet
mandatory `roles_needed` entry rather than allowing a silently understaffed start. Out of scope: the
vignette file's own load-time validation (`FEAT-5300`, a dependency, not yet its own Feature
Specification); in-app authoring of a new vignette (`FEAT-5100`); the runtime enforcement of an
assigned Role Assignment's scope once the exercise is running
([FS-105](FS-105-spacecraft-operations.md)'s and `FEAT-3500`'s concern, not this document's).

## Requirements Implemented

FR-4110 (vignette selection with tunable, defaulted parameters), FR-4210 (seat-to-role assignment
at setup) — per `docs/feature-planning/03-feature-catalog.md` `FEAT-4100`/`FEAT-4200`'s `Included
Requirements`.

## User Workflows

- White Cell selects a vignette from the available library and optionally overrides its tunable
  parameters.
- White Cell starts the session; every parameter left unmodified takes its documented default
  value.
- White Cell assigns each operator seat one or more roles (bus/payload/both) against the vignette's
  declared assets/constellations, informed by the vignette's `roles_needed`.
- If a mandatory `roles_needed` entry has no bound seat, the system reports it as unsatisfied;
  White Cell must resolve it before the exercise proceeds understaffed.

## System Behaviour

- **A selected vignette runs unmodified correctly** (FR-4110): given no parameter overrides, the
  started session uses every documented default value — this is a precondition for the tool being
  usable by a non-programmer facilitator (GDS-01 §3).
- **Seat assignment is informed by, and validated against, the vignette's declared `roles_needed`**
  (FR-4210): each assignment specifies bus, payload, or both responsibility for a given seat against
  a given Asset/constellation.
- **A silently understaffed start is prevented, not merely discouraged**: an unmet mandatory
  `roles_needed` entry is reported as unsatisfied rather than allowed to pass silently — this is a
  hard gate on session start, not an advisory warning.
- **Seat assignment depends on vignette selection having already occurred** (`FEAT-4200 →
  FEAT-4100` in the Feature Catalog): a seat cannot be assigned against a vignette's `roles_needed`
  before a vignette is selected.

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `session/manager.py` (`SessionManager`) | Initializes a Session from the selected Vignette and parameter overrides; applies documented defaults for unmodified parameters. |
| `content/vignette.py` (Content & Data) | Supplies the vignette's declared `roles_needed` that seat assignment is validated against (consumed here, not owned here — validation of the vignette file itself is `FEAT-5300`). |
| `ui_web/server.py` / `ui_web/static/` | Presents the vignette-selection and seat-assignment setup UI to White Cell, and surfaces the unsatisfied-`roles_needed` report if applicable. |

## Interfaces Used

INT-0002 (White Cell Facilitator ↔ Operator Console, exercise control) — both vignette selection
and seat assignment are White-Cell-only setup-phase actions over this interface.

## Data Model Changes

None beyond the existing Vignette entity's `roles_needed` field (per `docs/architecture/04-domain-
model.md`) and the Role Assignment entity (§1.10) this Feature produces — no new entity is
introduced; this Feature *produces* Role Assignment records that [FS-105](FS-105-spacecraft-
operations.md)/`FEAT-3500` later enforce at runtime.

## State Changes

- Vignette selection initializes a new Session with the selected vignette's (possibly overridden)
  parameter set.
- Each seat-assignment action creates a Role Assignment record binding a seat to a role/scope
  against a given Asset/constellation.
- A session with an unmet mandatory `roles_needed` entry does not transition to a startable state
  until that entry is resolved.

## Error Handling

- An unmet mandatory `roles_needed` entry is reported as unsatisfied, not allowed to start silently
  (FR-4210's own Acceptance Criteria) — the exact report format is not specified in the requirements
  baseline, flagged as an Open Question.
- The requirements baseline does not specify behavior for an invalid parameter override value at
  vignette selection (as opposed to an invalid vignette file, which is `FEAT-5300`'s concern) —
  flagged as an Open Question.

## Performance Considerations

None specified in the requirements baseline beyond what a one-time, setup-phase action implies (no
NFR in the baseline names vignette-selection or seat-assignment latency specifically).

## Security Considerations

Both vignette selection and seat assignment are exclusively White-Cell-role actions per their own
FRs — consistent with the project's broader White-Cell-authority model (DOM-003 §3), though neither
FR states an explicit rejection behavior for a non-White-Cell attempt the way FR-3520/FR-4310 do
for their respective domains; flagged as an Open Question.

## Acceptance Criteria

- Given a vignette with no parameter overrides supplied, the started session uses every documented
  default parameter value.
- Given a vignette with an unmet mandatory `roles_needed` entry, the system reports it as
  unsatisfied rather than allowing the exercise to start silently understaffed.

## Verification Plan

Test (automated) for both Acceptance Criteria above, consistent with FR-4110/FR-4210's own stated
Verification Method ("Test") in `docs/requirements/01-functional-requirements.md`.

## Dependencies

`FEAT-5300` (Load-Time Vignette Validation) in the Feature Catalog — vignette selection depends on
the selected file already being valid; not yet its own Feature Specification. No existing `FS-xxx`
document is a hard prerequisite, though [FS-105](FS-105-spacecraft-operations.md) is the nearest
downstream consumer of the Role Assignment records this Feature produces.

## Risks

- **This Feature's build status is unconfirmed** — as with FS-112/113/114, no prior FS document
  described vignette selection or seat assignment, and the RTM's Impl. Package citations for both
  FR-4110 and FR-4210 are `UNASSIGNED`. This specification is written directly from the
  requirements baseline and Feature Catalog entries.
- Combining two Feature Catalog entries (FEAT-4100, FEAT-4200) into one Feature Specification is a
  judgment call: if either capability later grows independent complexity (e.g., a richer seat-
  assignment UI with per-seat capability negotiation), splitting them into separate specs may
  become warranted — noted, not pre-empted, here.

## Open Questions

- **Build status is unverified** — confirm against `session/manager.py`/`ui_web/` directly (see
  Risks); if unbuilt, this specification is ready to hand to an Implementation Package.
- The exact unsatisfied-`roles_needed` report format, and behavior for an invalid parameter
  override value, are not specified in the requirements baseline.
- Neither FR-4110 nor FR-4210 states an explicit rejection behavior for a non-White-Cell attempt at
  vignette selection or seat assignment (unlike FR-3520/FR-4310's explicit rejection language) —
  whether this is an intentional omission or a baseline gap is worth raising with the requirements
  owner.
- `docs/domains/DOM-003-white-cell-framework.md` §2's Scope list does not currently name vignette
  selection/seat assignment explicitly (only "White Cell authority/visibility model, the inject
  mechanism, clock/pacing control, session administration") — this document grounds itself in
  DOM-003 as the closest fit (both are White-Cell-only setup-phase actions squarely within DOM-003
  §1's overall purpose), and DOM-003's frontmatter/scope has been updated to reference this
  document explicitly (see that document).

## Related ADRs

None directly — neither FR-4110 nor FR-4210 cites an ADR in the requirements baseline.

## Related Interfaces

INT-0002 — per `docs/design/05-interface-control-document.md` (also this document's sole
Interfaces Used entry).
