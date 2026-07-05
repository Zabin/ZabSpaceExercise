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

## Tranche 2 (2026-07-05): FS-116

**Why this tranche.** `11-release-readiness`'s
[release assessment](../reviews/release-assessment-fs-tracked-baseline.md) found `FEAT-3500`
(Role-Scoped Command Catalog & Assignment Scoping) — Must-priority, Release-1-bucketed — had zero
owning Feature Specification and zero implementation anywhere in `spacesim/`, despite the release
plan's own text assuming its RTM `UNASSIGNED` cells were merely a citation gap. `06-feature-
specification` authored `FS-116` to close the spec gap; two Open Questions blocked
implementation-readiness (no interface carries a seat identifier distinct from cell; the engine's
three-way verb taxonomy doesn't map onto the two-way role-scope model), both resolved by `ADS-3500`
(`03-architecture-design-synthesis`, Workflow B). This tranche plans the single package that
closes the remaining implementation gap.

**No split.** `FS-116` covers exactly one coherent unit of work — an offer-time filter (`FR-3510`)
and an execution-time gate (`FR-3520`) over the *same* seat-resolution/verb-classification logic,
touching a small, contiguous set of files (`session/manager.py`, `session/inprocess.py`,
`ui_web/server.py`, `ui_web/static/app.js`). Unlike `FS-105`/`FS-115` (split by architecturally
distinct concerns or by build-status seam), there is no internal seam here large enough to justify
two packages — one package, `IP-1160`, covers the whole Feature.

**Package ID assigned** (per the `IP-<series><seq>0` convention, `FS-116 → IP-1160`, checked
against `packages/INDEX.md` for collisions — unclaimed):

| Package | Feature | Situation | Entry status |
|---|---|---|---|
| [IP-1160](packages/IP-1160-role-scoped-command-enforcement.md) | FS-116 | Forward design | 🔴 BLOCKED (not authorized — MSTR-006 §3; every dependency package already `VERIFIED`) |

`IP-1160` is not authorized for coding — per MSTR-006 §3, being fully specified (and every
dependency already `VERIFIED`) is not itself an authorization; a separate, explicit user go-ahead
is required before any Implementation Task begins.

## Tranche 3 (2026-07-05): FS-117

**Why this tranche.** `FS-117` (Vignette Creator — In-App Authoring, Typed Parameters & Per-Cell
ROE) reached v1.1 — every capability it specifies now traces to a baselined requirement
(`FR-5110`/`FR-5120`-`FR-5180`/`FR-3420`/`NFR-2000`/`NFR-2010`), closing the Critical Open Question
that had blocked planning. `FEAT-5100` (the Feature Catalog entry this consolidates) is 0% built —
no prior FS, no code — so every package below is genuinely forward-design, not an as-built record.

**Three design-fork decisions resolved before packaging** (via `AskUserQuestion`, this pass — the
same class of in-pass design resolution `IP-2010`'s run #4 amendment used): (1) typed
per-payload-type/bus parameter sub-schemas bridge to the engine via new, strongly-typed fields
directly on `PayloadState` (not a UI-side conversion to the existing generic `detail: dict`); (2)
per-cell ROE uses a nested `roe: {blue: {...}, red: {...}}` structure on the `Vignette` schema (not
a flat `Parameter`-style list); (3) a vignette using only the legacy global ROE pair is
**auto-upgraded** to the explicit per-cell block on next save through the Creator (not left
byte-identical forever) — chosen so the on-disk schema stays current with the simulator's actual
per-cell capability, consistent with `NFR-2010`'s additive-evolution intent (a save always adds
the new shape; it never *removes* the ability to read the legacy shape, so no vignette becomes
unloadable).

**Split by seam, five packages** — mirroring the `FS-105 → IP-1050`/`IP-1051` precedent
(architecturally distinct concerns, not a count-padding split):

1. **`IP-1170` — ISR Beam-Mode Coverage: Weather & Missile-Warning** (prerequisite). `engine/isr.py`'s
   `BEAM_MODES` has zero entries for the `weather`/`mw` payload types (`BL-0053`) — confirmed
   directly (`beam_params()` silently falls back to generic EO stripmap numbers for either type).
   This is a hard precondition for two of `FR-5170`'s eight typed payload sub-schemas (`FS-117`
   Open Question 6, its own Risks section, and `FR-5170`'s own Postcondition all name it). Scoped
   as its own small, engine-only prerequisite package — a different seam (`C1` `engine/isr.py`)
   from every other package in this tranche, and independently valuable (a real engine gap
   `FS-105`/`FS-104`'s existing ISR tasking already exercises for the other six payload types)
   rather than bundled into the UI-facing work that merely exposes it.
2. **`IP-1171` — Typed Payload & Bus Parameter Domain Model** (`FR-5170`, `FR-5180`). `C1`/`C5` seam:
   new typed pydantic sub-models on `PayloadState` per payload type, plus vignette-schema/loader
   wiring so authored values reach `PowerState.charge_rate_per_s`/`drain_rate_per_s` and
   `AssetResources.delta_v_ms` (already-live fields — no new engine fields needed for the bus half,
   confirmed by reading `bus.py`/`entities.py` directly) rather than the dead `power_w`.
3. **`IP-1172` — Per-Cell Rules of Engagement Enforcement** (`FR-3420`, `NFR-2010`). `C1`/`C5` seam:
   the nested `roe:` vignette field, `build_world()`'s reconstruction of `VignetteContext.roe` as a
   cell-keyed dict, `engine/orders.py`'s two ROE check sites (confirmed at lines 349/358, both
   reached via the single `_validate()` method both `issue()` and `dry_run()` call — one fix site,
   not two), and the auto-upgrade-on-save logic.
4. **`IP-1173` — Vignette Creator Draft Session & Reverse Serialization** (`FR-5110`). `C2` seam: a
   draft authoring session is an unstarted `SessionManager` instance registered in
   `InProcessSession._sessions` the same way a normal session is (confirmed — `SessionManager.start()`
   is a distinct call from `__init__`/registration, and the existing `MAX_LIVE_SESSIONS`
   eviction in `_evict_if_full()` already provides a coarse answer to Open Question 2's "abandoned
   draft session" concern, noted rather than re-solved from scratch); a new "Save as Vignette"
   reverse-serialization function (`WorldState`+`VignetteContext` → `Vignette` YAML) is genuinely
   new — no such function exists anywhere today (`save_state()`/`from_state()` serialize
   session/game state, not authorable vignette content).
5. **`IP-1174` — Vignette Creator UI Surfaces** (`FR-5120`, `FR-5130`, `FR-5140`, `FR-5150`,
   `FR-5160`). `C4` seam: JSON view, 2D/3D preview (reusing `session/scene.py`'s `build_scene()` in
   ground-truth mode), TLE/lat-long/asset-entry forms (reusing the existing `POST
   /api/sessions/{sid}/force/tle` route), asset menu, and the seat-count-declaration + seat/role
   matrix UI (reusing `FS-115`/`IP-1151`'s existing `assign_role`/`staffing_report`). Depends on
   `IP-1171`/`IP-1172` (needs the typed schemas and per-cell ROE fields to present forms/selectors
   for) and `IP-1173` (needs the draft-session API this UI is a thin client over).

**Package IDs assigned** (per the `IP-<series><seq>0` convention, `FS-117 → IP-1170` family;
checked against `packages/INDEX.md` for collisions — `IP-1170`-`IP-1179` unclaimed):

| Package | Feature | Situation | Entry status |
|---|---|---|---|
| [IP-1170](packages/IP-1170-isr-beam-mode-coverage.md) | FS-117 (prerequisite, `BL-0053`) | Forward design | 🔴 BLOCKED (not authorized — MSTR-006 §3) |
| [IP-1171](packages/IP-1171-typed-payload-bus-parameters.md) | FS-117 §`FR-5170`/`FR-5180` | Forward design | 🔴 BLOCKED (not authorized — MSTR-006 §3; depends on `IP-1170`) |
| [IP-1172](packages/IP-1172-per-cell-roe-enforcement.md) | FS-117 §`FR-3420`/`NFR-2010` | Forward design | 🔴 BLOCKED (not authorized — MSTR-006 §3) |
| [IP-1173](packages/IP-1173-vignette-creator-draft-session.md) | FS-117 §`FR-5110` | Forward design | 🔴 BLOCKED (not authorized — MSTR-006 §3) |
| [IP-1174](packages/IP-1174-vignette-creator-ui-surfaces.md) | FS-117 §`FR-5120`-`FR-5160` | Forward design | 🔴 BLOCKED (not authorized — MSTR-006 §3; depends on `IP-1171`/`IP-1172`/`IP-1173`) |

None of these five packages is authorized for coding — per MSTR-006 §3, being fully specified (and
having every *upstream Feature/architecture* dependency already closed) is not itself an
authorization; a separate, explicit user go-ahead is required per package before any Implementation
Task begins.

## Related

[`00-master-build-plan.md`](00-master-build-plan.md) · [`packages/INDEX.md`](packages/INDEX.md) ·
[`docs/features/feature-index.md`](../features/feature-index.md) ·
[`docs/master/MSTR-006-governance-principles.md`](../master/MSTR-006-governance-principles.md)
