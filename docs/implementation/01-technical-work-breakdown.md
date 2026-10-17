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

## Related

[`00-master-build-plan.md`](00-master-build-plan.md) · [`packages/INDEX.md`](packages/INDEX.md) ·
[`docs/features/feature-index.md`](../features/feature-index.md) ·
[`docs/master/MSTR-006-governance-principles.md`](../master/MSTR-006-governance-principles.md)
