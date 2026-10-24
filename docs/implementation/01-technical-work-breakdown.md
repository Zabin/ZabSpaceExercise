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
| [IP-1174](packages/IP-1174-vignette-creator-ui-surfaces.md) | FS-117 §`FR-5120`-`FR-5160` | Forward design | 🔵 COMPLETE (authorized 2026-07-05; implemented 2026-09-26; awaiting `09-package-verification`) |

None of these five packages is authorized for coding — per MSTR-006 §3, being fully specified (and
having every *upstream Feature/architecture* dependency already closed) is not itself an
authorization; a separate, explicit user go-ahead is required per package before any Implementation
Task begins.

## Remediation Tranche (2026-09-26): IP-1061 — intake defects A1–A4

Source: `00-intake` entries `BL-0062`–`BL-0065` (external user validation report, 26 Sep 2026),
triaged by `00-pipeline-manager` run #53. No new Feature Specification — the defects are shipped
behaviour diverging from already-approved baseline (`FR-4410` via FS-106/`IP-1060`; `NFR-1300` via
ADR-0019).

```
FS-106 §FR-4410 ─┬─ A1  time inject at at_sim_s 0 never fires (+ rewind no-double-fire)  ─┐
                 ├─ A2  inject_library.yaml comment names a non-existent route            ├─► IP-1061
                 └─ A3  duplicate, divergent space_weather branch in _h_inject            │
NFR-1300 / ADR-0019 ── A4  hard 24-sat / 3-per-group cap in build_world()                 ─┘
```

**No-split rationale.** Four defects, one package: each is a few lines, all four are
regression-testable in the existing `test_inject_library.py` / `test_content.py`, and they touch
only `session/manager.py`, `content/vignette.py`, and one YAML comment — no seam crossing, no
engine change, one coherent Definition of Done ("shipped behaviour matches the approved
baseline"). Splitting A4 (content) from A1–A3 (session) would double the verification cost for no
isolation benefit. A5 (`BL-0066`, directed-energy path) is **excluded** — the user chose a distinct
DE path, which is new specified behaviour and enters at `06-feature-specification`, not a
remediation. A2 is a comment-only fix per the user's 2026-09-26 decision (no alias route).

| Package | Status | Authorization |
|---|---|---|
| [IP-1061](packages/IP-1061-inject-and-sizing-defect-remediation.md) | 🔵 COMPLETE | Authorized 2026-09-26 (MSTR-006 §3); implemented 2026-09-26 |

## Tranche 4 (2026-09-27, in progress): Must-tier external validation report batch

Source: `docs/pipeline/backlog.md` `BL-0067`/`BL-0068`/`BL-0069`/`BL-0070`/`BL-0071`/`BL-0082`
(external user validation report, 26 Sep 2026, items B1/B2/B3/B4/B5/B16). Six Feature
Specifications now `✅ Ready for implementation planning` (run #61-#63): `FS-118` (B16), `FS-106`
v2.1 (B4), `FS-120` (B5), `FS-119` (B1), `FS-121` + `FS-103` v1.1 (B2/B3). Planned one package per
Feature Specification (no cross-Feature split), in the priority order the pipeline journal
recorded:

```
FS-118 (FR-5410/FR-5420/NFR-3700)              ─► IP-1180   [done]
FS-106 v2.1 (FR-4420/FR-4430 slice)             ─► IP-1062   [done]
FS-120 (FR-5510)                                ─► IP-1200   [done]
FS-119 (FR-5220)                                ─► IP-1190   [done]
FS-121 + FS-103 v1.1 (FR-7410/FR-7420)          ─► IP-1210   [this pass — LAST]
```

**All six Must-tier packages are now written.** This closes the external validation report intake
batch's `07-implementation-planning` tranche in full.

**No-split rationale (IP-1180).** `FS-118`'s three requirements (external-directory load,
user-directory save retargeting, generalized traversal guard) share one seam — `content/
vignette.py`/`content/vignette_export.py`/`config.py` — and one coherent Definition of Done ("the
catalog and the save path both honor the plural set of configured content roots, safely"). No
engine change, no UI-route-shape change. Splitting the load-side extension from the save-side
retargeting would double the verification cost (both share the same generalized traversal-guard
helper) for no isolation benefit.

**No-split rationale (IP-1062).** `FS-106` v2.1's two requirements (condition-triggered firing,
four new effect types) share one seam — `session/manager.py`'s inject dispatch — and the four new
effect types are naturally implemented as siblings in the same shared effect-application helper
the condition-check path also calls. Splitting "the condition-evaluation mechanism" from "the new
effect types" would leave the condition-trigger half with nothing to demonstrate (no effect type it
could plausibly fire without at least one of the others already existing, and the eight pre-existing
effect types already work with `time`-typed triggers, so a condition trigger firing an old effect
type is a valid, cheap demonstration — but the two new-effect-type engine touches, `Sensor.health`
and the `scripted_manoeuvre`/`forced_custody_loss` engine calls, are exactly the shared-helper
additions the condition path also needs to dispatch through) — one coherent Definition of Done, one
package.

**No-split rationale (IP-1200).** `FS-120`'s single requirement (`FR-5510`) is one coherent
extension of one existing function pair (`export_vignette()`/`save_vignette()`) plus two additive
schema fields — no seam crossing, one package.

**No-split rationale (IP-1190).** `FS-119`'s single requirement (`FR-5220`) covers two file
formats sharing one batch entry point and one per-object failure-reporting contract — splitting
"TLE parsing" from "OMM parsing" into separate packages would duplicate the batch-orchestration/
reporting logic for no isolation benefit; one package, two parser functions.

**No-split rationale (IP-1210).** `FR-7410` (truth export) and `FR-7420` (cell-observed export)
share one time-span replay mechanism (`aar.state_at_time`) and one serializer (ECI/RIC transform +
CSV/CCSDS OEM writers), per `ADS-1500`'s own System Architecture — splitting them into two packages
would either duplicate the shared serializer or create an artificial cross-package dependency for
a seam that isn't real (both variants are thin, differently-sourced callers of the same
machinery). One package, two sampling functions sharing one serializer.

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1180](packages/IP-1180-external-vignette-directories.md) | FS-118 | 🔵 COMPLETE | Granted 2026-09-27 — implemented same day (661/3, both gates green), awaiting `09` in a fresh session |
| [IP-1062](packages/IP-1062-condition-triggered-injects-and-new-effects.md) | FS-106 v2.1 | 🔵 COMPLETE | Granted 2026-09-27 — implemented same day (678/3, both gates green), awaiting `09` in a fresh session |
| [IP-1200](packages/IP-1200-save-as-scenario.md) | FS-120 | 🔵 COMPLETE | Granted 2026-09-27 — implemented same day (689/3, both gates green), awaiting `09` in a fresh session |
| [IP-1190](packages/IP-1190-bulk-tle-omm-import.md) | FS-119 | 🔵 COMPLETE | Granted 2026-09-27 — implemented same day (638/3, both gates green), awaiting `09` in a fresh session |
| [IP-1210](packages/IP-1210-ephemeris-export.md) | FS-121/FS-103 v1.1 | 🔵 COMPLETE | Granted 2026-09-27 — implemented same day (707/3, both gates green), awaiting `09` in a fresh session |

**All six Must-tier packages are now written and specification-complete.** None is authorized for
coding (MSTR-006 §3) — that is a separate, explicit decision for the project owner, per package or
in bulk. **Note:** `IP-1180` and `IP-1200` both extend the same function (`save_vignette()`/
`export_vignette()`) — whichever is implemented second must be built against the first's actual
landed diff, not against either package document's description alone (see each package's own
Dependencies/Risks).

## Should-tier batch (run #78)

Seven packages against the eight Feature Specifications `06-feature-specification` drafted for the
Should-tier external-validation-report intake batch (`FS-122`, `FS-124`-`FS-129`). **No-split
rationale, every package in this batch:** each Feature Specification's own scope fits a single
subsystem seam (`engine/` core, or one `session/` read/write path) with one coherent Definition of
Done — none spans a seam wide enough to warrant a lettered slice, unlike `FS-105`'s bus/payload-vs-
effects split or `FS-117`'s five-way Tranche 3 split. One package per Feature Spec.

**`FS-122` covers two backlog items in one package (`IP-1220`).** `BL-0073`/B7 (five sensor
variants) and `BL-0083`/B17 (hosted sensor) share the same new `FR-1600` requirement parent and the
same `engine/entities.py`/`access.py`/`isr.py` seam — splitting them into two packages would
duplicate the `Sensor`-field-addition task and create an artificial cross-package dependency for a
seam that isn't real. One package, six leaves.

**`FS-123` (B8, space-weather-index drag/anomaly-rate coupling) has no package this run.** Its own
two Open Questions (`BL-0104`: the index-to-scaling mapping function; `BL-0121`: implausible-index-
value handling) are physics/design decisions this skill's own rules forbid inventing — per Step 0's
"every Open Question that blocks a planning decision must be resolved" gate, planning stopped here
rather than guessing a formula. The next free ID in this series (`IP-1230`) is reserved for it once
`04`/`06` resolves both questions.

**`IP-1270`/`IP-1290` share one design dependency, not a file seam.** `FR-3430` (`FS-127`, B10) and
`FR-1450` (`FS-129`, B15) independently describe "an effect's type and/or its five-D's
reversibility category" in identical words (`BL-0105`) — rather than each package inventing its own
classification vocabulary, `IP-1270` (authored first, per the user-directed batch order) commits to
the shared enumeration (order action type × five-D's reversibility category, both already-named
engine vocabularies) and `IP-1290` cites that resolution. This is a sequencing dependency between
two otherwise-independent packages (different files, `engine/orders.py`'s ROE-gating extension vs.
`engine/effects.py`'s jam-delivery/detectability extension), not a file-level split rationale.

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1220](packages/IP-1220-sensor-modality-models.md) | FS-122 | 🟡 READY | Not authorized (MSTR-006 §3); every dependency `VERIFIED` |
| [IP-1240](packages/IP-1240-debris-field-persistence-estimate.md) | FS-124 | 🟡 READY | Not authorized (MSTR-006 §3); every dependency `VERIFIED` |
| [IP-1250](packages/IP-1250-maneuver-ledger.md) | FS-125 | 🟡 READY | Not authorized (MSTR-006 §3); every dependency `VERIFIED` |
| [IP-1260](packages/IP-1260-telemetry-csv-export.md) | FS-126 | 🔴 BLOCKED | Not an authorization block — depends on `IP-1062` reaching `VERIFIED` (currently `COMPLETE` only) |
| [IP-1270](packages/IP-1270-effect-authorization-gating-and-live-roe.md) | FS-127 | 🟡 READY | Not authorized (MSTR-006 §3); every dependency `VERIFIED`; resolves the shared taxonomy `IP-1290` reuses |
| [IP-1280](packages/IP-1280-variable-speed-aar-replay.md) | FS-128 | 🟡 READY | Not authorized (MSTR-006 §3); every dependency `VERIFIED` |
| [IP-1290](packages/IP-1290-jamming-delivery-and-effect-detectability.md) | FS-129 | 🟡 READY | Not authorized (MSTR-006 §3); every dependency `VERIFIED`; reuses `IP-1270`'s shared taxonomy — sequence after or coordinate closely |

**None of the seven is authorized for coding (MSTR-006 §3)** — a separate, explicit decision for the
project owner, per package or in bulk. **Sequencing note:** `IP-1270` before (or tightly
coordinated with) `IP-1290`; `IP-1260` cannot begin `08-code-implementation` until `IP-1062` clears
`09-package-verification` in a fresh session; the remaining four (`IP-1220`, `IP-1240`, `IP-1250`,
`IP-1280`) have no cross-package ordering constraint.

## RIC-view/CATS-overlay tranche (run #85)

One package against `FS-130` (Live RIC-Frame Relative-Motion View & CATS Overlay), the first
Feature Specification in this set authored against a real `05-feature-decomposition` Feature
Catalog entry (`FEAT-8200`). **No-split rationale:** `FR-8210`'s live-view mechanism and `FR-8220`'s
CATS overlay share one read path (the overlay is computed inline on the same request, not a
separate round trip) and touch the same small seam (`engine/sun.py`, `session/ephemeris.py`,
`session/manager.py`/`inprocess.py`'s read-method pair, one new HTTP route) — splitting them into
two packages would duplicate the fog-of-war-rejection test pattern and create an artificial
cross-package dependency for a seam that isn't real, the same reasoning `IP-1220` applied to its
own six-leaf bundle.

`FS-130` carried three Open Questions; this package resolves two at the implementation-planning
level (`BL-0155` route/parameter shape, `BL-0156` origin-selection persistence — both ordinary `07`
design decisions FS-130's own prose explicitly routed here) and deliberately leaves the third
(`BL-0154`, CATS-angle display-banding) open, shipping the simplest grounded design (an unbanded
numeric readout) rather than inventing a banding scheme no input document commits to.

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1300](packages/IP-1300-ric-frame-view-and-cats-overlay.md) | FS-130 | ✅ VERIFIED | `VERIFIED` 2026-10-10 via [`VR-1300`](verification/VR-1300-ric-frame-view-and-cats-overlay.md) |

**Not authorized for coding (MSTR-006 §3)** — a separate, explicit decision for the project owner.
No cross-package sequencing constraint; this package has no dependency on any other currently
open package in this plan.

## Quick-TLE-export tranche (run #91)

One package against `FS-121` v2.0's `FR-7440` slice (Quick TLE export for a cell-visible
satellite, `FEAT-7400`). `FR-7410`-`FR-7430` in the same Feature Specification are already
`VERIFIED` under `IP-1210` and are not re-planned. **Slice rationale (new package, not an
`IP-1210` revision):** `FR-7440` shares `IP-1210`'s fog-of-war posture but none of its code path
(no time-span replay, no CSV/OEM serializer) — reopening a `VERIFIED` package for unrelated new
scope would muddy its verification record; numbered `IP-1211` as the FS-121 series' next slice.
**No-split rationale:** the engine conversion (`engine/tle_export.py`), the session read
(`quick_tle()` + two pass-throughs), the route and the console panel are one thin vertical read
path with one Definition of Done; splitting engine from UI would create an artificial dependency
for a seam with no other consumer.

Resolves FS-121 v2.0 Open Questions 4/6/7/8 (`BL-0110`, `BL-0160`, `BL-0161`, `BL-0162`) as
Design Decisions; Open Question 5 (`BL-0159`, own-asset scope) is a requirements question
`DEFERRED` to `04`, honoured by following `FR-7440` literally. `BL-0110`'s choice (option (a), a
single-epoch SGP4 mean-element fit) was grounded by a throwaway planning prototype (not committed)
that measured ≤ ~51 m round-trip residual across LEO/MEO/GEO/HEO/equatorial/retrograde cases.

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1211](packages/IP-1211-quick-tle-export.md) | FS-121 v2.0 (`FR-7440`) | ✅ VERIFIED (2026-10-10, `VR-1211`) | Pre-authorized by the project owner (MSTR-006 §3, 2026-10-10 session task instruction) — this package only |

No cross-package sequencing constraint.

## Telemetry-series-history remediation (pipeline run #99, 2026-10-11)

One remediation package for `BL-0170` (live telemetry series route back-dates current world state
across its window; disagrees with the `VERIFIED` `IP-1260` export at every historical point,
against `FR-2320`'s cross-route parity Postcondition). Planned against `FS-126` (`FR-2320`) with
`FS-121` (`FR-7410`/`FR-7420`) as a behaviour-preserving migration target.

Work units (all owned by `IP-1261`):

1. **Engine — stepwise replay generator** (additive sibling of `replay()`; `replay()` untouched).
2. **Session — time-keyed helper** in `session/aar.py` (single forward pass + live-tail shortcut).
3. **Fix — `get_series`** routed through the helper.
4. **Migration — `telemetry_export` + `truth_ephemeris` + `cell_observed_ephemeris`** onto the
   helper, output identical.
5. **Regression + parity + cost-guard tests** (`BL-0170` scenarios A-D).

**No-split rationale:** units 1-2 have no consumer other than 3-4, and unit 3 alone (`BL-0170`
Option 1, per-seq replay in `get_series`) was rejected on lock-hold cost, so the fix is not
shippable without the helper. Splitting the migration (4) into a follow-on package was considered
and rejected: it would leave two different time-span replay mechanisms live at once, and the
migration's own guard (exact-equality tests against the existing outputs) is cheap and belongs with
the helper's introduction. **New package, not an `IP-1260` revision:** `IP-1260` is `VERIFIED`;
the defect is in the pre-existing `get_series` path `IP-1260` explicitly did not touch
(`VR-1260`), so it is planned as a remediation slice (`IP-1261`, mirroring `IP-1061` under
`IP-1060`). `BL-0171` (`FR-2310` pass-gating of historical points) is a `04` question and is not
in this package; if adopted, it layers on this package's helper as a separate package.

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1261](packages/IP-1261-telemetry-series-history-remediation.md) | FS-126 (`FR-2320`) + FS-121 (`FR-7410`/`FR-7420`, migration) | 🟢 READY | Pre-authorized by the project owner (MSTR-006 §3, 2026-10-11 session task instruction) — this iteration's packages |

No cross-package sequencing constraint.

## Export sampling-bounds remediation (pipeline run #104, 2026-10-11)

One remediation package for `BL-0176` (REV-TRN-002 F1): the three time-span exports accept an
explicit `interval_s` that `session/ephemeris.py::sample_times` floors to a 1 µs step, so a single
request can replay an unbounded number of instants under the session lock. Planned against
`FS-121` (`FR-7410`/`FR-7420`, closing Open Question 2's explicit-interval half) and `FS-126`
(`FR-2320`).

Work units (all owned by `IP-1262`):

1. **Validation + ceiling in `sample_times`**, the single choke point all three exports share
   (`interval_s` finite and `> 0`; arithmetic sample-count check against `MAX_EXPORT_SAMPLES`
   before any list is built or replay run).
2. **Route docstrings** naming the new 400 (status mapping already exists).
3. **Tests**, plus the `BL-0174` rider: a regression test for `get_series`'s reversed window.

**No-split rationale:** units 1-2 are a few lines behind one function; splitting would produce
packages with no independent Definition of Done. The `BL-0174` rider is folded in because it is a
single test under the same `FR-2320` anchor and same test module, and `08-code-implementation`
can only execute test work through a package — a standalone one-test package was judged not worth
its own verify cycle. The ceiling value (10,000) is set from this pass's own measurement on
`multi-domain-taiwan` at +6 h (~1.25 s for a 10,000-instant telemetry export).

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1262](packages/IP-1262-export-sampling-bounds.md) | FS-121 (`FR-7410`/`FR-7420`) + FS-126 (`FR-2320`) | 🟢 READY | Pre-authorized by the project owner (MSTR-006 §3, 2026-10-11 session task instruction) — this iteration's packages |

No cross-package sequencing constraint.

## Inject fire-time validation remediation (pipeline run #110, 2026-10-11)

One remediation package covers two inject-path defects in the same seam,
`session/manager.py`'s inject-effect dispatch:

- `BL-0129` (Medium, `VR-1062` M1, open since 2026-09-27): a malformed effect raises mid-handler
  after earlier effects have already mutated the world, so the live state diverges from replay.
- `BL-0188` (Low, REV-TRN-003 F2): an `anomaly` on a bus-less asset is accepted with `ok: true` and
  does nothing.

Planned against `FS-106` v2.1 (`FR-4430` Precondition; `FR-4410`).

Work units (all owned by `IP-1063`):

1. **A pure validator** (`validate_inject_effects`): structural checks for every keyed effect type,
   plus FR-4430 target-precondition checks that include "anomaly needs a `bus_state`".
2. **Boundary wiring:** `fire_inject` rejects atomically, `InProcessSession` maps the failure to
   `Ack(ok=False)`, and `/inject` returns 400.
3. **Handler guard:** skip an invalid effect whole with one White message, and never raise.
4. **Tests,** including replay parity on the skip path and "all shipped content validates clean".

**No-split rationale:** units 1–3 share one function, and units 2 and 3 are its two call sites.
Splitting boundary from handler would give two packages editing the same 130-line method with no
independent Definition of Done.

**`BL-0184` deliberately not planned.** The manager routed it here (the telemetry export answers
422, not 400, for `interval_s <= 0`/NaN). This pass found that behaviour is an explicit, disclosed
decision of `IP-1262` (Design Decision 1: "the telemetry route's existing `gt=0` (a 422) stays as an
earlier guard"), independently verified by `VR-1262`. Reversing a verified package's documented
decision is not a remediation of a defect. It is returned to `00-pipeline-manager` with a
recommendation to close it as by-design, unless the project owner wants uniform 400s across the
three export routes. It is also a different seam (the HTTP route layer), so it would not belong in
this package anyway.

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1063](packages/IP-1063-inject-effect-fire-time-validation.md) | FS-106 (`FR-4430`, `FR-4410`) | 🟢 READY | Pre-authorized by the project owner (MSTR-006 §3, 2026-10-11 session task instruction) — this iteration's packages |

No cross-package sequencing constraint.

## Own-satellite quick-TLE remediation (pipeline run #118, 2026-10-15)

`04-requirements-engineering` amended `FR-7440` (`BL-0159`, run #116) so "visible" includes the
requesting cell's own satellites, and `FS-121` v2.1 (run #117) specified it. The shipped `IP-1211`
(`VERIFIED`) rejects an own satellite without a `Track` (its Design Decision 5). Work units:

1. **Session:** add an own-asset branch to `session/ephemeris.py::quick_tle`, ahead of the track
   lookup (ownership beats a track), with `source: "own"`; reject an own asset with no orbit.
2. **Console:** add own on-orbit satellites to `tleexport.js`'s cell picker, plus a source label.
3. **Tests:** replace the one superseded `IP-1211` test; add session-layer and route tests,
   including the cross-cell negative.

**No-split rationale:** unit 2 is a few lines that only make unit 1 reachable from the console, and
both share one Definition of Done (FS-121 AC11). Splitting would leave a package with no
independently testable outcome.

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1212](packages/IP-1212-own-satellite-tle-export.md) | FS-121 v2.1 (`FR-7440`) | ✅ VERIFIED (`VR-1212`; was 🟢 READY when planned) | Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization) |

No cross-package sequencing constraint.

## CATS phase-angle observation gain (pipeline run #124, 2026-10-15)

`FS-122` v1.1 (run #123) added `FR-1670`, `FEAT-1600`'s last unbuilt leaf. `FR-1610`–`FR-1660` are
built (`IP-1220`, `VERIFIED`). Work units:

1. **Model:** an optional usable-phase-angle range on `Sensor`, with a validator that rejects
   malformed ranges and ranges on non-`needs_lighting` sensors.
2. **Gain:** a pure factor helper (linear fall-off outside the range) and one additive
   `effective_gain` argument.
3. **Wiring:** the observe branch of `_exec_payload` computes the angle at `win.start` with the
   shared `cats_phase_angle_deg`.
4. **Tests:** factor shape, composition and regression, end-to-end for ground, space-based and
   hosted sensors, the validator, shipped-content unchanged, and the single-definition check.

**No-split rationale:** all four units sit in `engine/`, share one Definition of Done (FS-122 AC7–11)
and are individually small. Unit 3 cannot be tested without units 1–2, and units 1–2 have no
observable outcome without unit 3. As the next slice of the FS-122 series it takes `IP-1221`.

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1221](packages/IP-1221-cats-phase-angle-observation-gain.md) | FS-122 v1.1 (`FR-1670`) | ✅ VERIFIED (`VR-1221`; was 🟢 READY when planned) | Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization) |

No cross-package sequencing constraint.

## Sensor-modality wiring remediation (pipeline run #128, 2026-10-16)

Run #127 (`08-training-manual-authoring`) found that two `IP-1220` requirements are not reached end
to end (`BL-0212`: `FR-1610` fence/dish never selected; `BL-0213`: `auto` sensor selection skips
`FR-1640`'s cue gate) and that `FR-1630`'s affinity is an unchecked string (`BL-0214`). Work units:

1. **Beam mode:** in the observe branch of `_exec_payload`, select the `ground_radar` table for a
   radar sensor whose requested mode (order param, else the sensor's `beam_mode`) is a radar key;
   leave every other path unchanged.
2. **Cue gate:** filter `requires_cue` sensors without a held track out of `auto` candidates, and
   reject with `requires_cue` when that empties the list.
3. **Affinity:** type `altitude_band_affinity` as `Regime`; compare `LEO`/`LEO_SSO` as one band.
4. **Validator:** reject an unknown radar `beam_mode` at `Sensor` validation.
5. **Tests:** end-to-end for each, plus shipped-content-unchanged.

**No-split rationale:** all units are small edits in `engine/orders.py`, `isr.py` and
`entities.py` along the same sensor-observe seam, found together and remediating one package
(`IP-1220`). Each could be a package on its own, but none is large enough to justify a separate
verification pass, and units 1 and 4 share the radar-mode definition. As the next slice of the
FS-122 series it takes `IP-1222`.

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1222](packages/IP-1222-sensor-modality-wiring-remediation.md) | FS-122 v1.1 (`FR-1610`, `FR-1630`, `FR-1640`) | ✅ VERIFIED (`VR-1222`, 2026-10-16; was 🟢 READY at authoring) | Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization) |

No cross-package sequencing constraint.

## Observe-order remediation (pipeline run #132, 2026-10-16)

Run #131's training review ([REV-TRN-006](../reviews/training-review-runs122-127-scope.md) F2/F3)
found two code defects on the sensor-tasking and session-load seams (`BL-0219`, `BL-0220`), and fired
`BL-0217`'s revisit trigger. Planning re-checked each live at `9fc25a4` and found `BL-0217` wider than
filed: string `look_angle_deg`/`gain` and an explicit `null` also crash, and every such crash leaves a
phantom sensor booking. Work units:

1. **Reason:** in `_plan_collection`, report `sensor_contended` only when a window was found and
   every one was booked; otherwise `no_window`.
2. **Param validation:** reject a malformed observe `beam_mode`/`look_angle_deg`/`duration_s`/`gain`
   in `_validate` (before the `auto` early return, before any booking) with `invalid_param`; treat an
   explicit `null` as absent; guard `isr.beam_params` against a non-string mode.
3. **Console tips:** `REASON_TIPS` for `invalid_param` and `requires_cue`; corrected
   `sensor_contended` text.
4. **Tests:** both reasons, both paths, no phantom booking, HTTP outcome, `null` defaults,
   well-formed orders unchanged.

**Split / no-split rationale.**

- Units 1–3 are one package. They are small edits on one seam (`OrderSystem`'s observe planning and
  validation) with one shared test fixture, found together. Unit 2's booking leak is also a source
  of false `sensor_contended`, so it is the same symptom as unit 1. The FS-104 series takes
  `IP-1041`, next to the as-built `IP-1040`.
- **`BL-0220` is not packaged.** It violates `FR-5310` (load-time vignette validation with a
  precise error). The Feature Catalog assigns `FR-5310` to `FEAT-5300`, which has no Feature
  Specification. `FS-115` excludes vignette-file validity explicitly, and the catalog lists
  `FR-5310` under its Excluded Requirements. This skill plans only from an approved
  specification, so `BL-0220` routes to `06-feature-specification` (an FS for `FEAT-5300`, or an
  owner decision to fold it into an existing spec).
- The `jam`/`engage` numeric-param crash class is left for a later pass (see `IP-1041` Risks).

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1041](packages/IP-1041-observe-order-reason-and-param-remediation.md) | FS-104 (`FR-3210`) + FS-122 v1.1 (`FR-1610`) | 🟢 READY | Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization) |

No cross-package sequencing constraint.

## Order-parameter hardening (pipeline run #136, 2026-10-16)

`BL-0222`'s revisit trigger fired when `IP-1041` reached `VERIFIED` (run #134). Planning reproduced
the defect class live at `d2ded6a` on `leo-isr-denial` seed 5. It is wider than filed: besides
jam/engage, cyber, maneuver and command routing params crash. A ghost `queued`/`draft` order is left
in the registry. `power_w: "inf"` and `dv: [NaN,0,0]` corrupt `WorldState` permanently. A
wrong-length `dv` is accepted and raises inside `Simulation.advance_to`. Work units:

1. **Per-action param check** in `_validate`, immediately after `unknown_action`, with `null` =
   absent (extends `IP-1041`'s helper pattern; observe unchanged).
2. **Plan-then-commit ordering** in `issue`, `_continue_plan`, `_plan_command`, `_plan_collection`
   and `_plan_cyber`: build the payload before any status, booking, registry or scheduler write.
3. **Console tip:** `REASON_TIPS.invalid_param` action-neutral.
4. **Tests:** every action's refusals through both paths, no ghost or corrupted state, a
   monkeypatched-failure no-state test, `null` defaults, well-formed orders unchanged.

**Split / no-split rationale.**

- Units 1–4 are one package. They change one seam (`OrderSystem`'s validate → plan → commit
  pipeline in one file), share one fixture (one vignette carries a jammer, an interceptor, a
  satellite and stations), and fix one symptom class (a malformed order that is not refused up
  front). Splitting validation from reordering would leave Test 8's guarantee half-delivered.
  FS-105 is the primary spec (effects console), so the package takes `IP-1052`, next to the as-built
  `IP-1050`/`IP-1051`. FS-102 is co-cited.
- **Not packaged:**
  - Range rules (`salvo_n` ≤ 0 or above `ammo`, negative power or dwell): no requirement states
    them. Routed to `04-requirements-engineering`.
  - `Simulation.advance_to` dropping a raising handler's event unlogged: an engine-wide
    determinism question beyond order params. Routed to `03`/`07`.

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1052](packages/IP-1052-order-param-hardening.md) | FS-105 v1.1 + FS-102 (`FR-3110`, `FR-1310`, `FR-1410`, `FR-1420`) | 🟢 READY | Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization) |

No cross-package sequencing constraint (`IP-1160`, `BLOCKED`, also edits `_validate`; whichever
lands second rebases).

## Load-time vignette validation (pipeline run #145, 2026-10-16)

FS-131 v1.1 (`FEAT-5300`; `FR-5310`–`FR-5314`, `NFR-1600`, `NFR-2200`) is the first spec for a Must
Feature with no prior code. It absorbs `BL-0220` (bare 500 at load, silent **Load**) and `BL-0237`
(a malformed TLE crashes on the first advance). Work units:

1. **Gate** (`content/vignette.py`): `VignetteValidationError` and a pure `validate_vignette`.
   It covers schema and entity validators surfaced at load, TLE initialise/propagate,
   orbit/location presence (cyber units exempt), unique ids, `roles_needed` references, and a
   `build_world` catch-all. All problems are collected.
2. **Registry ordering** (`session/inprocess.py`): build the manager before eviction or the
   counter increment (FS-131 OQ5).
3. **Wire form** (`ui_web/server.py`): 400 `invalid_vignette` with problems, 404 unknown id, 400
   path guard (FS-131 OQ4).
4. **Console** (`app.js::loadSession`): show the refusal at **Load**.
5. **Tests:** one file covering criteria 1–9 and 11.

**Split / no-split rationale.**

- Units 1–5 are **one package**. They are a single request path (Load → session layer → content
  gate → HTTP → console) with a single symptom class (an invalid vignette that is not refused up
  front). Each acceptance criterion needs the whole path: criterion 1 asserts a 400 at HTTP, which
  needs units 1 and 3; criterion 8 needs units 1 and 2. A content-only package would leave
  `BL-0220`'s 500 in place.
- **Not packaged:** FS-131 criterion 10 (`FR-5310`'s template clause) is blocked on `BL-0233` at
  `03`. The `CR-23`/`CR-24` checks are not baselined. The manual impact is routed to
  `08-training-manual-authoring` after `VERIFIED`.

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1310](packages/IP-1310-load-time-vignette-validation.md) | FS-131 v1.1 (`FR-5310`–`FR-5314`, `NFR-1600`, `NFR-2200`) | 🟢 READY | Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization) |

No cross-package sequencing constraint.

## Effect resource bounds (pipeline run #153, 2026-10-17)

**Input:** [FS-132](../features/FS-132-effect-resource-bounds.md) v1.0 — `FEAT-1400`'s resource-bound
slice (`FR-1460`, `FR-1470`).

**Work units.**

1. **Validation bound** (`engine/orders.py::_validate`, engage branch): `insufficient_ammo` on a
   consumed salvo above the remaining rounds, with a shared rounds helper.
2. **Execute-time re-check** (`_h_effect`): no resolution, failed record, no charge.
3. **Jam power** (jam plan `consume` + `_h_effect` consumption): stop touching `power_w`.
4. **Console tip** (`app.js` `REASON_TIPS`).
5. **Tests**, plus one fixture adjustment in `test_order_param_hardening.py`.

**Split / no-split rationale.**

- Units 1–5 are **one package**. Units 1–3 are all in one file, one code path (the effect order's
  plan → validate → execute → consume step), and verified together: `FR-1460`'s postcondition
  needs units 1 and 2, and unit 3 edits the same consumption lines. Splitting `FR-1470` out would
  give two packages editing the same eight lines of `_h_effect`.
- **Not packaged:** rating enforcement for jams (ADR-0037 excludes it); salvo range rules
  (`CR-25`); whether a missed salvo consumes rounds (`BL-0249`, `04`). The manual impact is routed
  to `08-training-manual-authoring` after `VERIFIED` (`BL-0250`).

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1320](packages/IP-1320-effect-resource-bounds.md) | FS-132 v1.0 (`FR-1460`, `FR-1470`) | 🟢 READY | Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization) |

No cross-package sequencing constraint, except that `IP-1160` (`BLOCKED`) would rebase over it.

## Vignette id-scan robustness (pipeline run #158, 2026-10-17)

**Input:** [FS-131](../features/FS-131-load-time-vignette-validation.md) v1.1 — Behaviour 5 and
Acceptance Criterion 6 (`FR-5310`, `NFR-1600`), for the `BL-0252` defect REV-TRN-008 found: an
unguarded `yaml.safe_load` in `load_vignette`'s built-in declared-id scan.

**Work units.**

1. **Shared "declared id of a file" helper** (`content/vignette.py`), used by the built-in and the
   external-root declared-id scans.
2. **Tests** (`test_vignette_id_scan.py`).

**Split / no-split rationale.**

- One package. It is one function in one file, and both scans must change together, or the roots
  drift again (the cause of the defect). It is a separate package from `IP-1310` because that one
  is `VERIFIED` and closed. The fix is to the id-resolution step that runs before `IP-1310`'s gate,
  not to the gate.
- **Not packaged:** a "some files in this folder could not be read" notice (a new behaviour, not
  in FS-131; via `00-intake` if wanted); FS-131 criterion 10 (`BL-0233`).

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1311](packages/IP-1311-vignette-id-scan-robustness.md) | FS-131 v1.1 (`FR-5310`, `NFR-1600`) | 🟢 READY | Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization) |

No cross-package sequencing constraint.

## Tranche — owner-prioritized `DEFERRED` backlog clearance follow-ups (2026-10-17, pipeline run #166)

The project owner asked (2026-10-17) for the long tail of `DEFERRED` backlog entries to be cleared.
The entries that needed code or tests, plus findings the clearance pass itself surfaced, are cut
into five packages along real seams:

1. **`IP-1021` — engine event loop** (`engine/simulation.py`, `engine/handlers.py`): ADR-0038.
   Its own package: it is the one change to a load-bearing invariant, Medium severity, and must be
   reviewable alone.
2. **`IP-1223` — observe beam modes** (`engine/orders.py` + console list): FS-122 v1.2. Its own
   package: an engine validation rule plus its console mirror, one Definition of Done.
3. **`IP-1065` — White Cell console and session small fixes** (`app.js`, `index.html`,
   `inprocess.py::cell_activity`, `manager.py::bulk_import`, `tools/render_manual.py`): five
   independent one-function fixes on the same console/session seam plus two doc follow-ups. **Not
   split** into five packages: each is a few lines with one test, and one run covers them; they
   share no production function, so each hunk stays separately revertible.
4. **`IP-1064` — condition-inject follow-ups** (`manager.py` condition/tick code,
   `content/vignette.py`, `engine/busmodel.py`): `VR-1062`'s three remaining Lows, which all touch
   the same tick-arming and condition-check code — split from `IP-1065` because they share that
   code with each other, not with the console.
5. **`IP-1131` — test-only coverage**: four regression tests over four FS slices. One package
   because no production file changes; mixing them with a code package would blur "no production
   change" as a checkable DoD item.

**Not packaged (disposed without code):** `BL-0006` (cyber decisions carry no
`custody_confidence_at_decision`; cyber is window- and track-independent by ADR-0012, so whether
cyber should be scored for belief-truth divergence is a design question for FS-201, not a code
gap) and `BL-0126` (creator preview colour-by-owner: an enhancement beyond `FR-5130`, which is met).

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1021](packages/IP-1021-failure-atomic-event-application.md) | FS-102 v1.1 + ADR-0038 | 🟢 READY | Pre-authorized (MSTR-006 §3, standing 2026-10-11) |
| [IP-1223](packages/IP-1223-beam-mode-follows-sensor-modality.md) | FS-122 v1.2 | 🟢 READY | Pre-authorized |
| [IP-1065](packages/IP-1065-console-and-session-small-fixes.md) | FS-106/102/118/120/119 | 🟢 READY | Pre-authorized |
| [IP-1064](packages/IP-1064-condition-inject-follow-ups.md) | FS-106 v2.1 | 🟢 READY | Pre-authorized |
| [IP-1131](packages/IP-1131-verification-coverage-follow-ups.md) | FS-113/115/102 + NFR-3400 | 🟢 READY | Pre-authorized |

No cross-package sequencing constraint.

## Missed salvo consumes its rounds (pipeline run #176, 2026-10-17)

**Input:** [FS-132](../features/FS-132-effect-resource-bounds.md) v1.1 — System Behaviour 3, State
Changes, Error Handling (v1.1 rows), Acceptance Criteria 2, 8, 9 (`FR-1480`, and `FR-1460`'s
amended AC), for the project owner's 2026-10-17 decision on `BL-0249`: misses consume interceptors.

| Unit | Work | Seam |
|---|---|---|
| 1 | Drop the `outcome.success` term from `_h_effect`'s ammo charge, so every engagement that reaches resolution is charged | C1 engine, `engine/orders.py` consumption step |
| 2 | Tests: miss charged (+ later `insufficient_ammo`), destroyed-target charged, exact-salvo miss, outcome parity, replay | `spacesim/tests/test_effect_resource_bounds.py` |

**Split / no-split rationale.** One package, a new FS-132 slice (`IP-1321`) rather than a reopened
`IP-1320`: `IP-1320` is `VERIFIED` and its record stays as verified; this is a separate,
owner-directed rule change to one condition in the same consumption step. Units 1–2 are one file
plus its test file and are verified together. **Not packaged:** the manual (`RED-5`, §15.1 row) —
routed to `08-training-manual-authoring` after `VERIFIED`; the `FEAT-1400` catalog row
(`BL-0275`, `05`).

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1321](packages/IP-1321-missed-salvo-consumes-rounds.md) | FS-132 v1.1 (`FR-1480`) | 🟢 READY | Pre-authorized by the project owner (MSTR-006 §3, standing 2026-10-11 pre-authorization; owner decision `BL-0249`) |

No cross-package sequencing constraint.

## Space-weather-index coupling (pipeline run #188, 2026-10-18)

**Input:** [FS-123](../features/FS-123-space-weather-index-coupling.md) v1.1 (`FR-1230`,
`FR-4440`), with its design basis in
[ADR-0039](../architecture/adr/ADR-0039-space-weather-index-to-multiplier-mapping.md). This is the
owner-prioritized stalled batch, `BL-0074` (item B8).

| Unit | Work | Seam |
|---|---|---|
| 1 | Pure mapping, lookup and validator functions | C1 engine, `engine/perturbations.py` |
| 2 | Opt-in drag step on the `bus_tick` grid, plus the `Asset.ballistic_coeff_m2_kg` field | C1 engine, `engine/busmodel.py`, `engine/entities.py` |
| 3 | Vignette fields (`space_weather_series`, `environmental_anomalies`), load-time refusal, `build_world` conversion | C3 content, `content/vignette.py` |
| 4 | Inject-boundary validation, series application (key update, not dict replacement), the `env_anomaly_check` tick | C2 session, `session/manager.py` |
| 5 | Tests (mapping, drag, anomaly, replay, refusal, opt-out byte-identity) | `spacesim/tests/test_space_weather_index.py` |

**Split / no-split rationale.** One package. Units 1–4 cannot be verified separately:

- FS-123's acceptance criteria each need the series to flow end to end, from authored data
  (Unit 3) or an inject (Unit 4), through the mapping (Unit 1), into an effect (Unit 2 or Unit 4).
- Criterion 4 (opt-out byte-identity) is a property of all four units together.

Splitting drag from anomalies would duplicate Units 1, 3 and 4's series plumbing across two
packages that touch the same functions. The package is moderately sized: five files plus one test
file, all additive.

**Not packaged:** operator-manual prose, routed through §15.1 to `08-training-manual-authoring`
after `VERIFIED`, and the `FR-4440` Notes line (`BL-0281`, `04`).

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1230](packages/IP-1230-space-weather-index-coupling.md) | FS-123 v1.1 (`FR-1230`/`FR-4440`) | 🟢 READY | Pre-authorized (MSTR-006 §3: the standing 2026-10-11 pre-authorization plus the owner's 2026-10-18 stalled-batch instruction) |

No cross-package sequencing constraint.

## Controller view and pending-inject queue (pipeline run #191, 2026-10-18)

**Input:** [FS-106](../features/FS-106-white-cell-dashboard.md) v2.3: `FR-4450` (`FEAT-4400`) and
`FR-4620` (`FEAT-4600`). This is the owner-prioritized stalled batch, `BL-0079` (item B13).

| Unit | Work | Seam | Package |
|---|---|---|---|
| 1 | Handles, logged `inject_admin` cancel/edit, override fold, handler skip, re-arm, pending listing | C2 session, `session/manager.py`, `inprocess.py` | IP-1066 |
| 2 | Routes and the White pending-inject list (cancel / edit) | C4 console, `server.py`, `app.js`, `index.html` | IP-1066 |
| 3 | Single-instant composite read (truth + both `CellView`s) | C2 session, `manager.py`, `inprocess.py` | IP-1067 |
| 4 | White-only route and the text Compare panel | C4 console | IP-1067 |

**Split rationale.** The work is two packages along the requirement seam, which FS-106 v2.3
already treats as independent (`FR-4620`'s Notes):

- `IP-1066` changes the deterministic inject path: new event kind, handler checks and re-arm. Its
  risk sits in replay and rewind.
- `IP-1067` is a pure read composition with no state.

Neither depends on the other, and each verifies on its own. Bundling them would make one
Definition of Done mix a determinism-sensitive change with a read-only one.

| Package | FS | Status | Authorization |
|---|---|---|---|
| [IP-1066](packages/IP-1066-pending-inject-edit-cancel.md) | FS-106 v2.3 (`FR-4450`) | 🟢 READY | Pre-authorized (standing 2026-10-11 + owner's 2026-10-18 stalled-batch instruction) |
| [IP-1067](packages/IP-1067-side-by-side-controller-view.md) | FS-106 v2.3 (`FR-4620`) | 🟢 READY | Pre-authorized (same) |

No cross-package sequencing constraint. **Not packaged:** the manual prose (`WCM-5` and the
god-view section), routed via §15.1 after `VERIFIED`.

## White-only controls enforced at the server (pipeline run #219, 2026-10-23)

**Input:** [FS-106](../features/FS-106-white-cell-dashboard.md) v2.4: `FR-4310` (corrected) and
`FR-4320` (`FEAT-4300`), owner decision `BL-0307`; requirements review R1 (High).

| Unit | Work | Seam | Package |
|---|---|---|---|
| 1 | White-only guard at the route boundary for the 12 routes; `load_save` gains the seat parameter | C2 HTTP boundary, `server.py` | IP-1068 |
| 2 | One refusal test per control and seat; existing tests name `white` | `spacesim/tests/` | IP-1068 |

**One package, not two.** The guard is a few lines at one seam, and the tests are what the
remediation exists for (a package claim without a test is how R1 happened); splitting the
existing-test calling-convention update into its own package would leave the suite red between
them.

## Self-contained saves (pipeline run #220, 2026-10-23)

**Input:** [FS-110](../features/FS-110-save-and-resume.md) v2.0 (`FEAT-7200`): `FR-7230`, `FR-7220`,
`FR-7210` (force-edit defect `BL-0315`), `NFR-1800`.

| Unit | Work | Seam | Package |
|---|---|---|---|
| 1 | Save gains content portion, replay baseline, versions; resume from them; legacy branch | C2 `session/manager.py` | IP-1101 |
| 2 | Load-time validation and warnings | C2 `session/inprocess.py` | IP-1101 |
| 3 | Route returns warnings; console shows them | C4 `server.py`, `app.js` | IP-1101 |

**One package.** The three units change one round trip and are verified by one test file; the
client change is a few lines. FS-110 Open Question 4 is decided in the package (resume from the
carried baseline; the exporter drops injects, briefs and parameters, so a rebuild cannot be exact).

## Test-origin traceability (pipeline run #221, 2026-10-23)

**Input:** [FS-133](../features/FS-133-test-origin-traceability.md) (`FEAT-12100`): `NFR-2820`,
`NFR-3840`, `NFR-2830`, `NFR-1510`.

| Unit | Work | Seam | Package |
|---|---|---|---|
| 1 | Marker registration, strict markers, collection recorder, ledger reader, checks, allow-list, report option; tag the two gate modules | `pyproject.toml`, `spacesim/tests/` | IP-1330 |
| 2 | Tag 22 engine and content modules | `spacesim/tests/` | IP-1331 |
| 3 | Tag 32 session-layer modules | `spacesim/tests/` | IP-1332 |
| 4 | Tag 16 web and cross-cutting modules; allow-list empty | `spacesim/tests/` | IP-1333 |
| — | Dependency lock (`NFR-1510`) | release | none now: produced at the first major release and checked by `11` (`BL-0318`) |

**Why four packages.** The infrastructure is small and must land first; the backfill is ~914 test
functions that each need a judgment about what they assert, too much for one reviewable run, so it
is cut by layer (the grouping came from each module's imports). The allow-list lets the suite stay
green between packages; it may only shrink.

## Browser suite (pipeline run #222, 2026-10-23)

**Input:** [FS-134](../features/FS-134-browser-console-rule-suite.md) (`FEAT-12200`): `NFR-2840`.

| Unit | Work | Seam | Package |
|---|---|---|---|
| 1 | Browser lookup, in-process server fixture, canvas-label init script | `spacesim/tests/` | IP-1340 |
| 2 | Rules (a)–(c) tests, skip-with-reason | `spacesim/tests/` | IP-1340 |
| 3 | Dependency, marker, hook, `CLAUDE.md` | `pyproject.toml`, `.claude/hooks/` | IP-1340 |

**One package:** a handful of tests on one fixture. FS-134 Open Question 1 decided in the package
(wrap the drawing calls; no client change). Measured: Playwright 1.64.1 needs an explicit executable
for the installed Chromium 1194 build.

## Documentation integrity (pipeline run #223, 2026-10-23)

**Input:** [FS-135](../features/FS-135-documentation-integrity-checks.md) (`FEAT-12300`): `NFR-3800`,
`NFR-3810`, `NFR-3820`, `NFR-3830`.

| Unit | Work | Seam | Package |
|---|---|---|---|
| 1 | Live-set walk; links, indexes, ledger-pair checks; allow-lists | `spacesim/tests/` | IP-1350 |
| 2 | Retired-documents register and check (`NFR-3810`) | `spacesim/tests/` + the register | not yet planned — blocked on `BL-0319` (owner) |

**Why split here:** unit 2 cannot be planned without the owner's decision on where the register
lives; units in 1 need nothing more.

## Small remediations: panel registry and watchdog test (pipeline run #224, 2026-10-23)

| Unit | Work | Seam | Package |
|---|---|---|---|
| 1 | Register the Compare and Assessment panels; hide White-only panels from other seats' menu | C4 `panels.js` | IP-1069 (`BL-0305`, `NFR-3030`) |
| 2 | Test the clock-lag watchdog | `spacesim/tests/` | IP-1091 (`BL-0309`, `NFR-1300`) |

**Two packages, not one:** different seams, different specs (FS-106/FS-201 vs FS-109), no shared
files; each is small enough to build and verify on its own.

## Release-push remediation (2026-10-24)

**Input:** the open bug rows of `docs/pipeline/backlog.md` and the in-progress item `IP-1311`, under the
owner's release-push directive (journal run #256: pause new features; remediation packages for bugs,
in-progress and critical items only). Sources: `BL-0323`, `0326`, `0327`, `0333`, `0350`, `0352`,
`0353`; `BL-0359` F-13; integration review of tranche 2 F-01–F-04; the `FR-4320` scope extension
(`BL-0321`, `BL-0324`, `BL-0351`); the weak-tag findings `BL-0341`, `BL-0344`, `BL-0347`;
`BL-0252` (`IP-1311`, already planned). Every package cited is a remediation of a defect in a
`VERIFIED` package; no Feature Specification is new.

| Unit | Work | Seam | Package |
|---|---|---|---|
| 1 | Vignette id scan skips an unreadable file (already planned) | `content/vignette.py` | IP-1311 (`BL-0252`) |
| 2 | Legacy save with a missing vignette; missing-key saves; content portion = saved force | `session/manager.py` `validate_save`/`save_state`; `ui_web/server.py` `load_save` | IP-1102 (`BL-0326`, `BL-0352`, `BL-0359` F-13) |
| 3 | Creator edits, `save_vignette`, `red_step`, seats route White-only; creation refuses a player seat | `ui_web/server.py` guards | IP-1072 (`BL-0321`, `BL-0324`, `BL-0351`) |
| 4 | Palette/bookmark time entries by seat; control-error reporting; `loadSaveFile` refusals; dry-run race; menu scroll; recorder and skill recipe | `static/app.js`, `index.html`, `style.css`; `tools/`; `.claude/skills/run-spacesim` | IP-1073 (`BL-0323`, `0327`, `0333`, `0350`, `0353`) |
| 5 | Weak origin tags to fitting leaves, with a guard test | `spacesim/tests/`, RTM column | IP-1334 (`BL-0341`, `0344`, `0347`) |

**Why this cut.** The cut follows the repository's own seams and the backlog's grouping:

- **Save robustness is its own package (units 2).** `BL-0326`, `BL-0359` F-13 and `BL-0352` are all
  in `IP-1101`'s code (`validate_save`, `save_state`) and share fixtures (a temporary content
  directory); the console's reaction to a refused load is a different seam and is unit 4. The
  backlog proposed putting `BL-0352` and F-13 "with the client package"; they are server-side
  defects and splitting them from the console keeps each package to one seam and one test style
  (HTTP/unit vs browser).
- **The `FR-4320` extension is a server-only package (unit 3), not part of the client package.**
  It changes guards in one file and needs no browser; its risk (existing tests that call the newly
  guarded routes without a seat) is different from the client package's (browser flakiness).
- **One client package for five console/tooling bugs (unit 4).** They share files (`app.js`), one
  new status element, and the browser-suite harness. The tooling items (`BL-0353`) ride along
  because they are the same defect class (a caller that assumes unguarded time control) and are
  tiny; they would not justify a package alone.
- **Retag is last and separate (unit 5).** Test-only, but it touches decorator lines in modules the
  other packages edit and regenerates the RTM column, so it follows them.
- **Not split further:** `BL-0323` (race) and `BL-0333` (CSS) are one-line to few-line fixes in
  files unit 4 already touches; separate packages would each cost a verification cycle for a
  trivial change.
- **`IP-1311` is not replanned.** It is complete as a plan and `READY`; only its slot in the order
  is recorded here.

**Ordering and file conflicts.** `IP-1102` and `IP-1072` both edit `ui_web/server.py` (different
routes); `IP-1073` edits `test_browser_console_rules.py`; `IP-1334` edits tag lines across ~20 test
modules. Order: `IP-1311` ∥ `IP-1102` → `IP-1072` → `IP-1073` → `IP-1334`. Content dependencies:
only `IP-1102` → `IP-1073` (test 4's real 400); the rest is conflict avoidance.

**Deliberately excluded from this tranche (not bugs / not release-blocking):** `FR-7450` ISO export
bounds (a feature, `06`→`07`), `IP-1160` (feature), GDS-06…GDS-10 authoring, the vignette cleanup
sweep, `BL-0355` package-header corrections (a documentation defect, not a bug), `BL-0359` F-10–F-12
and F-14–F-16 (Low; documentation, optional consolidation, a test-coverage extension, a design
note, an exit code), integration review F-05 (training-manual curl examples, owned by
`08-training-manual-authoring`), F-06–F-09 (documentation owners), and the no-leaf test findings for
`04` (`BL-0342`, `0345`, `0348`).

**Spec lag flagged upstream.** FS-106 v2.4 predates the 2026-10-24 `FR-4320` extension, and
GDS-09 §4 / OQ1 and `design/07` still describe the shorter White-only list. `IP-1072` proceeds on
the requirement leaf, which is binding and names the routes; a v2.5 note on FS-106 (`06`) and the GDS
update (`03`) are recommended.

## Release-push remediation, pass 2 (2026-10-24)

**Input:** the open bugs the independent verifiers of `IP-1311`, `IP-1102`, `IP-1072` and `IP-1073`
found (`VR-1311` F-1, `VR-1102` F-1/F-2/F-3, `VR-1072` F1, `VR-1073` F3; backlog `BL-0361`–`BL-0364`,
`BL-0368`), under the same owner release-push directive (journal run #256: bugs, in-progress and
critical items only; no new features). Every package cited corrects a defect in a `VERIFIED` package;
no Feature Specification is new.

| Unit | Work | Seam | Package |
|---|---|---|---|
| 1 | `validate_save` completion: non-object `overrides`, bad `pending`/`orders`/`ssn_requests` rows, `final_time` range, `classification` type; pin the legacy wording and the server backstop; `IP-1102` Decision 4 note | `session/manager.py::validate_save`; `test_save_load_robustness.py` | IP-1103 (`BL-0362`, `BL-0363`) |
| 2 | Rewind bounded to `[start_epoch, now]`; "rewind to start" means the exercise start; `start_epoch` on the clock state; palette and toolbar use it | `session/manager.py`, `session/inprocess.py`, `ui_web/server.py`, `static/app.js` | IP-1074 Part A (`VR-1073` F3) |
| 3 | `roles/assign` and `observer/view` refuse by query seat with 403; docstring corrected | `ui_web/server.py` | IP-1074 Part B (`BL-0364`, `VR-1072` F1) |
| 4 | Origin reader and RTM generator accept five-digit `FR-` IDs; 20 assessment/research tests retagged | `spacesim/tests/baseline_ids.py`, two test modules, RTM column | IP-1335 Parts A, B (`BL-0368`) |
| 5 | Top-level list/scalar YAML case for the vignette id scan | `test_vignette_id_scan.py` | IP-1335 Part C (`BL-0361`) |

**Why this cut (three packages).**

- **Save validation is its own package (unit 1).** One function, one test module, HTTP/unit style;
  it completes `IP-1102` and has no overlap with the console or clock work.
- **Rewind and the two seat routes share a package (units 2, 3).** Different bugs, but both are
  White Cell control correctness in the same files (`ui_web/server.py`, `session/manager.py`), the
  same requirement family (`FR-4310`/`FR-4320`) and the same test style (HTTP against a started
  session). Separately each is small enough that a verification cycle apiece would cost more than the
  change; split them if the build finds Part A larger than expected (Part A is the Medium and is
  written first so it can ship alone). The rewind range guard sits in `SessionManager`, not in the
  route, so every caller is protected, and the engine's `rewind_to` is untouched.
- **Retag infrastructure, retag and the scan test share a package (units 4, 5).** All test-only. The
  scan test (`BL-0361`) is one case and was proposed by the backlog for the "retag/hardening sweep";
  `BL-0368` is the defect that blocks 20 of `IP-1334`'s retags, so it must precede `IP-1334` and
  carries those 20 itself. `IP-1334` is adjusted by a dependency note only (its two modules' rows are
  delivered by `IP-1335`); it is not replanned.
- **Not split further:** the `final_time` ceiling, the `orders` row checks and the `classification`
  check are one function's worth of validation; the `start_epoch` field, the guard and the client
  change are one behaviour.

**Ordering and file conflicts.** `IP-1103` and `IP-1074` both edit `session/manager.py` and
`ui_web/server.py` in different regions; `IP-1074` and `IP-1335` both add tests that the RTM
regeneration must include; `IP-1334` retags decorator lines in modules the others edit. Order:
`IP-1103` → `IP-1074` → `IP-1335` → `IP-1334`. Content dependencies: only `IP-1335` → `IP-1334` (the
carve-out); the rest is conflict avoidance.

**Deliberately not planned (not bugs, too design-heavy, or owned elsewhere):**

- **Auto-pause on rewind.** Whether a rewound exercise should pause the lazy clock is a change to the
  clock model (`FR-4310`), not a bug. `IP-1074` preserves current behaviour and pins it; the question
  goes to the owner and `04`.
- **A requirement leaf for the rewind range.** None states it; `IP-1074` derives it from `FR-4310`
  and the AAR/ephemeris span (`FR-7330`/`FR-7410`). Recommend `04` add a sentence to `FR-4310`.
- **`BL-0366`** (`aar/playback/*` has no seat check): needs a scope decision on `FR-4320` (`04`);
  Info, deferred in the backlog.
- **`BL-0370`** (`build_world` mutates its input vignette): a design question with one consumer
  working around it; deferred in the backlog.
- **`BL-0365`** (documentation: `CLAUDE.md` code map, `FR-4320` Notes, GDS-09 §4, FS-106 v2.5,
  training pages): documentation defects owned by `04`/`03`/`06`/`08-training-manual-authoring`.
- **`BL-0367`** (skip count 4 versus 3): a currency item for the `CLAUDE.md` sweep (`BL-0358`).
- **`BL-0369`** (no-leaf test gaps): `04` work.
- **`VR-1073` F1** (View menu `max-height` assumes a one-row toolbar; at 1100x700 with the White
  toolbar wrapped one entry fails the actionability check), **F4** (recorder hard-codes browser and
  `ffmpeg` paths), **F5** (cosmetic status line): not in this pass's brief; F1 is a Low console bug
  that a later pass may take, F4 is environment fragility.

## Release-push remediation, pass 3 (2026-10-24)

**Input:** `VR-1074` F1 (Medium): undo past the first event puts the sim clock at epoch 0 (1970); pre-existing, made visible by `IP-1074`'s rewind bound. Same owner directive (journal run #256: bugs only).

| Unit | Work | Seam | Package |
|---|---|---|---|
| 1 | Undo lands on `start_epoch` (never 0); undo with nothing to undo refused; `now >= start_epoch` invariant pinned across undo, rewind, advance and load | `engine/simulation.py::undo_last`, `session/manager.py::undo_last`, `session/inprocess.py`, `ui_web/server.py` `/undo` | IP-1075 |

**Why one package, and why not folded into `IP-1074`.** `IP-1074` is `VERIFIED`; the defect is outside its scope and checklist, and a verified package is not reopened. The engine line, the manager guard, the route mapping and the tests are one behaviour and one verification pass. **Other callers audited, no separate unit:** `rewind_to` is already guarded, `advance_to`/catch-up cannot move backwards, `from_state` is protected by `IP-1103`'s `validate_save`; they get pinning tests inside `IP-1075`. **Ordering:** after `IP-1335`/`IP-1334` only to avoid test-file conflicts. **Not planned:** a `FR-4310` sentence on undo/rewind bounds (recommended to `04`), and auto-pause on undo (owner question, as for rewind).

## Release-push remediation, pass 4 (2026-10-24)

**Input:** the tranche 3 integration review (`docs/reviews/integration-review-tranche-3-release-push-remediation.md`: `M-2`, `M-3`, `M-4`, `L-1` to `L-4`) and the two requirements added by baseline-maintenance pass 2: `FR-4330` (time control bounded to the exercise span; the advance half "required, not yet built") and `FR-7340` (AAR playback obeys the requesting seat; "required, not yet built"). Same owner directive (journal run #256: bugs, in-progress and critical items only; no new features). Every package corrects a defect in a `VERIFIED` package or builds a requirement that already exists; no Feature Specification is new.

| Unit | Work | Seam | Package |
|---|---|---|---|
| 1 | Advance and step accepted only in `[now, start_epoch + 366 days]`; backwards or beyond-span or non-finite is a 400, never a 500; the running clock stops at the span's end; `stepBy` uses `/step` | `session/manager.py`, `session/inprocess.py`, `ui_web/server.py`, `app.js::stepBy` | IP-1076 |
| 2 | Palette inject entries White-only (plus audit of the other palette entries); refused inject shown in the visible status line | `app.js` palette, `fireInject` | IP-1076 |
| 3 | Refused Load does not overwrite a live tab's `#session`; Observer dry-run not sent; no `GET /windows/<sensor>` (cause: the ribbon asks for windows of a sensor id, which `ASSETS` holds beside assets) | `app.js` `showLoadFailure`, `previewOrder`, `drawRibbon` | IP-1076 |
| 4 | Tag-only retag of the existing rewind, undo and save-ceiling tests to `FR-4330`, with the matching `IP-1334` guard rows | `test_white_control_correctness.py`, `test_undo_clock_floor.py`, `test_save_load_robustness.py`, `test_origin_retag.py` `EXPECTED` rows | IP-1076 |
| 5 | Seat check on the five `aar/playback/*` routes (white any; player own viewpoint; observer read-only; no seat refused; 403 before any change or disclosure) | `session/inprocess.py`, `ui_web/server.py` | IP-1077 |
| 6 | 14 package headers and 3 ledger notes reconciled with their `VERIFIED` rows; recorded sweep | `docs/implementation/` only | IP-1078 |

**Why three packages, and why this cut.** The brief asked for one package and a split "if large".

- *Units 1-4 are one package* (`IP-1076`): they share `manager.py`, `inprocess.py`, `server.py` and `app.js`, one clock concept (the span) and one browser harness, and each is small. The palette, load-readout and console-noise items are all "the console does not show or send the right thing for a refusal"; splitting them from the bound would force `IP-1076`'s `stepBy` change (palette advance uses `/step`, which the bound makes necessary) to land in two packages. About 18 new tests; the largest package in the pass but one verification pass. The tag-only retag rides with it because the retagged tests are exactly the ones the bound's new tests sit beside, and because the `IP-1334` guard pins the tag sets, which forces the same-commit `EXPECTED` row edit.
- *Unit 5 is its own package* (`IP-1077`): a different feature (`FS-107`, AAR), a different requirement (`FR-7340`), no console surface, no browser case, and a separate verification story (a seat matrix plus a no-disclosure check). Bundling it would make `IP-1076`'s checklist mix a clock bound with a fog-of-war boundary. It touches `server.py` and `inprocess.py` in different regions from `IP-1076`.
- *Unit 6 is its own package* (`IP-1078`): documentation only; `07` may not write `VERIFIED`, so the planner cannot make the edit in the planning pass; fourteen unrelated file edits would bury `IP-1076`'s diff; the edit is independent of every code package and can run in any order.

**Ordering and file conflicts.** `IP-1076` then `IP-1077` (both edit `server.py`, both add to the RTM Test column and push the count-pinned guard in `test_origin_retag.py`); `IP-1078` any time, last by preference so its Master Build Plan note edits do not collide with the code packages' status rows. No content dependency among the three.

**Decisions made while planning (recorded, owner may override).**
- The span is the save cap restated (366 days from `start_epoch`), reused from `SessionManager.MAX_SAVE_SPAN_US`; no `end_epoch` is exposed and nothing is configurable (`FR-4330` Notes).
- The lazy real-time clock is clamped at the span's end rather than left to run past it (otherwise Play bypasses the bound); it is not auto-paused (owner question, same family as `L-6`).
- Playback keeps its single shared cursor per session; per-seat cursors are an open design question (`FR-7340` Notes), not built. An absent seat is refused on every playback route, because no tool or console surface calls them without one.
- Observer may read playback state exactly as `FR-7340` states; whether that read should honour the Observer's designation is a requirements question, recorded.
- The `GET /windows/blue/BLUE-RADAR` 404 was investigated: a real client defect, not noise to suppress. The ribbon requests windows for the first actor in the picker, and the picker lists sensors (`BLUE-RADAR` is a `sensors:` entry) as well as assets; the route correctly answers 404 for an id not in `world.assets`. Fixed in the client; the route's fog/ownership contract is unchanged.

**Not planned here (and why).**
- `M-1` (three training curl examples without `?cell=white`): `docs/training/` belongs to `08-training-manual-authoring`, reviewed by `09-training-manual-review`; not a code or `docs/implementation/` item. The packages above list the training pages they affect but do not edit them.
- `M-5`, `L-7` (`CLAUDE.md` status text, GDS-07/08/09/10 statements, `feature-index.md` `FS-106`/`FS-110` rows and the two `doc_integrity_allow_ledgers.txt` lines, GDS coverage of `start_epoch` and the 366-day cap): owned by `03`, `04`, `06`, `11`; `FR-4330` already states the cap in the requirements, which closes the requirements half of `L-7`.
- `L-5` (count-pinned guards): a test-guard redesign, not a bug fix for the release; the packages report the headroom (about 63 tests at the review tip; `IP-1076` and `IP-1077` use about 38) and a follow-up should re-express the guard as "no test lost".
- `L-6` (does rewind or undo pause the running clock): an open owner decision.
- A check that compares package-file headers with the ledger: a new capability (`IP-1350` family); recommended to `00-intake` by `IP-1078`.
- `VR-1073` F1, F4, F5 and the other deferred `BL-` items listed in the pass 2 section: unchanged.

## Release-push remediation, pass 5 (2026-10-24)

**Input:** the tranche 3 integration review `L-5` (count-pinned guards), `VR-1078` F1/F2/F3 (31 stale package headers, three "Not yet authorized" rows, nine "Awaiting 09" sentences, `IP-1078`'s own header) and GDS-07 `OQ5` (the event-log cap does not see a real save's log; branch `claude/stale-docs-gds`, commit `4eac964`). Same owner directive (journal run #256: bugs, in-progress and critical items), plus the owner's instruction in this session to fix stale documents before the release and to resolve the guard "as you see fit".

| Unit | Work | Seam | Package |
|---|---|---|---|
| 1 | Remove the collected-count bounds and their test from the retag guard; keep the pinned tag sets; fail a removed module, do not fail a deselected one; no check skips under both browser filters; mutation tests pin that a deleted or retagged pinned test fails | `spacesim/tests/test_origin_retag.py` (and `baseline_ids.py` if the pure helper lives there) | IP-1079 |
| 2 | 31 older headers plus `IP-1078`'s reconciled with the ledger; three "Not yet authorized" and the "Awaiting 09" sentences removed; sweep recorded in the tree | `docs/implementation/` only | IP-1080 |
| 3 | The 100,000-entry cap counts a real save's `{"entries": [...]}` log, first in `validate_save`, before model validation and replay; the constant moves to `SessionManager` with an alias on `InProcessSession` | `session/manager.py`, `session/inprocess.py`, a new test file | IP-1081 |

**Why three packages, and why this cut.** Three unrelated seams with three different verification stories, each small.

- *Unit 1 (`IP-1079`) is its own package*: test-only, one file, verified by mutation; it must not ride with a production fix because the point is that the guard stops gating growth. Decision recorded: remove, do not widen. Widening `COLLECTED_UPPER` repeats `L-5` at the next threshold, and the count test protects nothing the per-row checks do not (each pinned row already fails if its test is deleted, renamed or retagged). The skip rule is made precise instead (absent from disk fails, present but not collected is not applicable), which also removes the check that skipped under both `-m browser` and `-m "not browser"`. The frozen `VR` notes that cite the 1700 ceiling are not edited.
- *Unit 2 (`IP-1080`) is its own package*: `07` may not write `VERIFIED`, so it cannot do the edits now; 32 header edits would bury a code diff; same rules as `IP-1078`. It is deliberately a second pass rather than an extension of `IP-1078` (which is `VERIFIED` and not reopened).
- *Unit 3 (`IP-1081`) is its own package*: a production bug in `FS-110`'s save path with a boundary-heavy test matrix. Design decision: the cap becomes the first rung of `validate_save` (one refusal path, ahead of the double `EventLog.model_validate`), rather than patching the inline check to accept a dict, so every caller of `validate_save` is protected and the amplifier the cap exists to stop is stopped before pydantic runs. The constant moves down a layer because `session/manager.py` cannot import `session/inprocess.py`; the old name stays as an alias. A bare list over the cap is still refused as oversize (the audit test stays valid); at or under the cap it remains "malformed", as today.

**Ordering and file conflicts.** `IP-1079` → `IP-1081` → `IP-1080`. `IP-1081` adds about 9 tests and `IP-1079` about 5 net, so the suite moves from 1671 to about 1685; the `IP-1334` ceiling of 1700 would not yet fail, but `IP-1079` removes it first so that nothing is gated on the count. `IP-1080` last: its Master Build Plan note edits sit near the status rows the other two update. No content dependency among the three.

**Not planned here (and why).** Closing GDS-07 `OQ5` (owned by `03`, after `IP-1081` is `VERIFIED`); a check comparing package-file headers with the ledger (a new capability, `IP-1350` family, via `00-intake`; `IP-1080` ends with a recorded sweep instead); any edit of a `VR-xxxx`; HTTP request-body size limits (a deployment concern, noted in `IP-1081` Risks).

## Related

[`00-master-build-plan.md`](00-master-build-plan.md) · [`packages/INDEX.md`](packages/INDEX.md) ·
[`docs/features/feature-index.md`](../features/feature-index.md) ·
[`docs/master/MSTR-006-governance-principles.md`](../master/MSTR-006-governance-principles.md)
