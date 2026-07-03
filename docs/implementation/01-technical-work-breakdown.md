# Technical Work Breakdown

> **Document ID:** IMPL-PLAN-01
> **Version:** 1.0
> **Status:** ♻️ Living (extended per tranche)
> **Dependencies:** [`docs/features/feature-index.md`](../features/feature-index.md), the
> Feature Specification corpus, [`00-master-build-plan.md`](00-master-build-plan.md)
> **Referenced By:** [`packages/INDEX.md`](packages/INDEX.md), `ROADMAP.md` (Theme: Implementation
> Packages)
> **Produces:** the hierarchical decomposition from Feature Specification → work unit → package,
> and the rationale for every split/no-split decision this pass made
> **Feature Mapping:** FS-112, FS-113, FS-114, FS-115 (this tranche)
> **Related Topics:** [`00-master-build-plan.md`](00-master-build-plan.md),
> [`docs/features/feature-index.md`](../features/feature-index.md)

[↑ Docs index](../INDEX.md) · [Master Build Plan](00-master-build-plan.md) ·
[Packages index](packages/INDEX.md) · [Feature index](../features/feature-index.md)

## Purpose

This is the Technical Work Breakdown (TWBS) for converting an approved Feature Specification into
one or more Implementation Packages. It exists to record *why* each package was cut where it was
cut — the rationale, not just the result — so a future planner extending this plan does not have to
re-derive it. Created on this, the first invocation of `07-implementation-planning`; extended per
tranche thereafter, oldest tranche first.

## Tranche 1 (2026-07): FS-112, FS-113, FS-114, FS-115

**Why this tranche.** These four Feature Specifications (closing Findings F-02/F-10 in
`docs/feature-planning/05-feature-review.md`) were approved with each one's own build status
explicitly flagged **unverified** — no prior Implementation Package or FS narrative had confirmed
whether the described capability exists in `spacesim/`. Per `packages/INDEX.md`, authoring a
package for any of them first required that verification. This tranche performed that
verification (reading the current source tree against each FS's Acceptance Criteria) before
cutting any package, per this skill's Step 1/Step 2 discipline.

**What the verification found.** All four Features are **partially or fully built**, but none
matches its Feature Specification exactly — the source tree diverges from FR-stated behavior in
different ways for each:

| Feature | FR(s) | Build status found | Divergence from FS |
|---|---|---|---|
| FS-112 Classification Banner | FR-4510, NFR-3100 | **Partially built.** `content/vignette.py:47` carries a `classification` field (default `"UNCLASSIFIED-TRAINING"`); `ui_web/static/index.html:96` renders a banner on every screen. | The rendered banner is a **hard-coded literal string** (`UNCLASSIFIED // TRAINING`), never read from `Vignette.classification` — a session built with a different banner value would render the wrong one. No White-Cell-facing UI sets/overrides the value (FR-4510's "set at scenario build" input has no control surface). Not embedded in `session/aar.py`'s `export_csv` or `manager.py`'s `save_state` (both silently omit it). |
| FS-113 Observer Read-Only Access | FR-6510 | **Not built.** No "observer" seat/role concept exists anywhere in `session/`, `ui_web/server.py`, or `ui_web/static/app.js` — the cell selector is a fixed White/Blue/Red set (`app.js:406` `setCell`). | Full gap — genuinely forward design. The dependency this Feature needs (fog-of-war filtering, `session/cells.py` `CellController.view()`) is already shipped and reusable as-is. |
| FS-114 Hot-Seat Hand-Off Screen-Blank Menu | FR-6610 | **Built**, `ui_web/static/index.html:597` (`#handover` dialog) + `app.js:2717-2733` (blank/blur + Resume). | FR-6610 describes an **automatically detected** trigger ("the current seat's occupancy has ended") and a **seat-selection menu** presented until a seat is "explicitly chosen." The shipped mechanism is a **manually clicked** `⏸ Handover` button, and "Resume" auto-computes the next cell by fixed cycle (`blue→red`, `red→blue`, else `→white`) rather than offering an explicit choice — there is no seat-selection menu, only a single Resume action. The blank/no-leak postcondition (FR-6610's hard requirement) is satisfied; the trigger and menu semantics are not. |
| FS-115 Session Setup: Vignette Selection & Seat Assignment | FR-4110, FR-4210 | **Split finding.** FR-4110 (vignette selection with tunable, defaulted parameters) is **built and tested** (`session/manager.py:35` `SessionManager.__init__`, `content/vignette.py`'s `Parameter` model, `spacesim/tests/test_content.py:62` `test_parameter_override_flows_into_roe`). FR-4210 (seat-to-role assignment against a vignette's declared `roles_needed`, with a hard gate on an unmet mandatory entry) is **not built at all** — no `roles_needed` field exists on the `Vignette` model, and cell selection is a flat White/Blue/Red picker with no seat/role/asset binding or staffing gate. | See split rationale below. |

**Split decisions this pass made:**

1. **FS-112 → one package (`IP-1120`), not split.** The gap (wire the rendered banner to
   `Vignette.classification`, add a build-time selection control, embed the value in `aar.py`
   export + `manager.py` save state) is one coherent seam — a single data value threaded through
   three call sites — not three independently schedulable units. Splitting it would be splitting
   for count, which this skill's own guidance forbids.
2. **FS-113 → one package (`IP-1130`), not split.** A single, coherent new capability (seat/role
   concept + read-only enforcement at the `SessionAPI`/`ui_web/server.py` boundary) with no
   internal seam large enough to justify two packages.
3. **FS-114 → one package (`IP-1140`), not split, but its Definition of Done separates the
   already-satisfied postcondition (no leaked content) from the still-open divergence (manual
   trigger vs. FR-6610's automatic-detection language; no explicit seat-choice menu) rather than
   claiming the package fully closes FR-6610 as literally written.** This is a verification/finding
   matter, not a work-unit split — the code is one small, cohesive client-side mechanism.
4. **FS-115 → two lettered packages (`IP-1150`, `IP-1151`), split by build-status seam** — mirroring
   the `FS-105 → IP-1050/IP-1051` precedent, but split here because the two halves are in
   genuinely different *situations* (as-built vs. forward design), not merely different subsystems:
   - **IP-1150** (FR-4110, vignette selection with tunable/defaulted parameters) — as-built,
     `COMPLETE` pending `09-package-verification`.
   - **IP-1151** (FR-4210, seat-to-role assignment against `roles_needed` with a hard understaffed-
     start gate) — forward design, not yet authorized, `BLOCKED` on `IP-1150` reaching `VERIFIED`
     per this plan's own READY-requires-VERIFIED-dependency rule.
   A single package could not honestly carry one situation-vocabulary entry (`VERIFIED`-track vs.
   `READY`/`BLOCKED`-track) for two halves in different states — the existing corpus's own
   status vocabulary forced this split.

**Package IDs assigned** (per the `IP-<series><seq>0` convention, `FS-1xx → IP-10x0`, checked
against `packages/INDEX.md` for collisions — `IP-1120`, `IP-1130`, `IP-1140`, `IP-1150`, `IP-1151`
were all unclaimed):

| Package | Feature | Situation | Entry status |
|---|---|---|---|
| [IP-1120](packages/IP-1120-classification-banner.md) | FS-112 | Partially built (gap-closing) | 🟡 BLOCKED (on `IP-1150` → `VERIFIED`; also not authorized) |
| [IP-1130](packages/IP-1130-observer-read-only-access.md) | FS-113 | Forward design | 🟡 READY (not authorized) |
| [IP-1140](packages/IP-1140-hot-seat-handoff.md) | FS-114 | As-built (with a documented divergence) | 🔵 COMPLETE (pending `09-package-verification`) |
| [IP-1150](packages/IP-1150-vignette-selection.md) | FS-115 (FR-4110 slice) | As-built | 🔵 COMPLETE (pending `09-package-verification`) |
| [IP-1151](packages/IP-1151-seat-role-assignment.md) | FS-115 (FR-4210 slice) | Forward design | 🔴 BLOCKED (on `IP-1150` → `VERIFIED`; also not authorized) |

No package in this tranche is authorized for coding (MSTR-006 §3) — `IP-1130` alone is `READY`
in the pure sense (no blocking package dependency), and even it requires a separate, explicit user
go-ahead before any of its Implementation Tasks begin.

## Related

[`00-master-build-plan.md`](00-master-build-plan.md) · [`packages/INDEX.md`](packages/INDEX.md) ·
[`docs/features/feature-index.md`](../features/feature-index.md) ·
[`docs/master/MSTR-006-governance-principles.md`](../master/MSTR-006-governance-principles.md)
