# Feature Specifications — Index

[↑ Docs index](../INDEX.md) · [Master index](../master/MSTR-005-documentation-map.md) ·
[MSTR-005 Documentation Map](../master/MSTR-005-documentation-map.md) §4 (traceability chain) ·
[MSTR-006 Governance Principles](../master/MSTR-006-governance-principles.md) §5 (metadata block)

Feature Specifications (`FS-xxx`) describe **what a capability must do**, with no implementation
detail — they sit between the Domain/Research tiers (the *why*) and Implementation Packages
(`IMP-xxxA/B/C`, the *how*, Phase 5, not yet authorized) in the documentation-driven-development
chain:

```
Training Objective → Domain Document (DOM-00x) → Research (R1xx-R5xx) → Feature Spec (FS-xxx)
    → Implementation Package (IMP-xxxA/B/C) → Code → Tests
```

Per [`MSTR-006`](../master/MSTR-006-governance-principles.md) §4, a Feature Specification is sized at roughly 5-10 pages equivalent.

## Index

| ID | Title | Owning domain | Status | Notes |
|---|---|---|---|---|
| [FS-101](FS-101-mission-planning.md) | Mission Planning | DOM-001 | ✅ Done | Plan-first order authoring against real access-window/regime constraints. |
| [FS-102](FS-102-command-scheduling.md) | Command Scheduling | (R103-grounded; no owning DOM) | ✅ Done | The validate→window→execute→confirm latency surfaced honestly to the operator. |
| [FS-103](FS-103-custody-management.md) | Custody Management | DOM-009 | ✅ Done | Custody/track confidence as the gate for weapons-quality and effect preconditions. **v1.1** confirms `Track.state_estimate` is already independent of ground truth and closes the historical-record Open Question via `ADS-1500`'s replay-based design (`BL-0068`). |
| [FS-104](FS-104-sda-tasking.md) | SDA Tasking | DOM-009 | ✅ Done | Sensor/SSN tasking across the SDA chain (detect→track→ID→characterize→predict). |
| [FS-105](FS-105-spacecraft-operations.md) | Spacecraft Operations | DOM-001, DOM-007 | ✅ Done | The full operator console: bus/payload command, telemetry, effects, consequence-confirm. |
| [FS-106](FS-106-white-cell-dashboard.md) | White Cell Dashboard | DOM-003 | ✅ Done (v2.4: v2.3 additions built by `IP-1066`/`IP-1067`; `FR-4310`/`FR-4320` enforcement by `IP-1068`/`IP-1072`/`IP-1074`–`IP-1077`, all `VERIFIED`) | Facilitator god-view, inject scheduling, clock/pacing control authority (trigger surface), manual adjudication. **Narrowed in v2.0** — session transport, save/resume, and AI-Red generation are now FS-109/FS-110/FS-111. **v2.1** adds `FR-4420`/`FR-4430` (condition-triggered injects + four new effect types), closing `BL-0070` (item B4); three Open Questions left for `07`/`04`. **v2.2** ratifies the inject failure modes settled by `IP-1062`/`IP-1063` into Error Handling and closes those three Open Questions (`BL-0191`). **v2.3 (2026-10-18)** adds `FR-4450` (edit/cancel a pending inject) and `FR-4620` (side-by-side controller view), `BL-0079`. **v2.4 (2026-10-23)** adds `FR-4320` and moves `FR-4310`'s enforcement to the server boundary (found not built, `BL-0307`): every White Cell control refuses any request not naming the `white` seat. |
| [FS-107](FS-107-after-action-review.md) | After Action Review | DOM-001, DOM-003 | ✅ Done | Replay/scrub/branch-compare debrief instrument, incl. self-assessment mode. |
| [FS-108](FS-108-inject-authoring.md) | Inject Authoring *(candidate)* | DOM-003 | 🅿️ Scoped, not authorized | Templated/preview inject-authoring UX over the existing inject mechanism. |
| [FS-109](FS-109-multiplayer-session-transport.md) | Multiplayer / LAN Session Transport | DOM-003 §6 | ✅ Done | Server-authoritative lazy clock, per-session mutation locking, hot-seat/LAN session sharing. Split out of FS-106 v1.0. |
| [FS-110](FS-110-save-and-resume.md) | Save & Resume | DOM-003 §6 | ✅ Done (v1.0; v2.0 additions built by `IP-1101`–`IP-1103`, `VERIFIED`) | Deterministic save/resume round trip + content/session ownership split. Split out of FS-106 v1.0. **v2.0 (2026-10-23)** adds `FR-7230` (self-contained saves, `BL-0302`): the save carries its replay baseline in vignette form, which also makes `FR-7220` true; fixes force edits lost on resume; legacy saves resume by ID. |
| [FS-111](FS-111-ai-red-doctrine-automation.md) | AI-Red Doctrine Automation | DOM-009, DOM-008 | ✅ Done | Doctrine-preset-driven Red activity generation; fog-of-war-parity gap (ADR-0024) named, not resolved. Split out of FS-106 v1.0. |
| [FS-112](FS-112-classification-banner.md) | Classification Banner | DOM-003 | ✅ Done | Universal unclassified-training-material banner on every screen/export. Previously undocumented (Finding F-02); built and `VERIFIED` (see the Master Build Plan; stale "build status unverified" clause removed 2026-10-17, `BL-0031`). |
| [FS-113](FS-113-observer-read-only-access.md) | Observer Read-Only Access | (GDS-01/02-grounded; no owning DOM) | ✅ Done | White-Cell-designated read-only view, no command authority. Previously undocumented (Finding F-02); built and `VERIFIED` (see the Master Build Plan; stale "build status unverified" clause removed 2026-10-17, `BL-0031`). |
| [FS-114](FS-114-hot-seat-handoff.md) | Hot-Seat Hand-Off Screen-Blank Menu | (GDS-05 OR-3-grounded; no owning DOM) | ✅ Done | Blanks a departing operator's cell content during hot-seat role change. Previously undocumented (Finding F-02); built and `VERIFIED` (see the Master Build Plan; stale "build status unverified" clause removed 2026-10-17, `BL-0031`); the one Feature enforcing fog-of-war client-side rather than server-side. |
| [FS-115](FS-115-session-setup.md) | Session Setup: Vignette Selection & Seat Assignment | DOM-003 | ✅ Done | Vignette selection/tuning + seat-to-role assignment at exercise start. Previously undocumented (Finding F-10); built and `VERIFIED` (see the Master Build Plan; stale "build status unverified" clause removed 2026-10-17, `BL-0031`). |
| [FS-116](FS-116-role-scoped-command-catalog.md) | Role-Scoped Command Catalog & Assignment Scoping | (GDS-04 §1.10-grounded; no owning DOM) | ✅ Ready for implementation planning | Filters the order panel to the seated role's legal commands and enforces that scope at execution time. Newly authored — `FEAT-3500` had zero owning spec and zero implementation until this document (`11-release-readiness` Finding 2 / `BL-0049`); v1.1 closed both Open Questions v1.0 raised via `ADS-3500` (seat-identifier interface amendment; `DEFENSE_VERBS` classification); v1.2 corrected that classification per project-owner direction — there is no third "defense" role-scope category, only `bus`/`payload` (six `DEFENSE_VERBS` are `bus`, two — `def.harden`/`def.set_deception_mode` — are `payload`). |
| [FS-117](FS-117-vignette-creator.md) | Vignette Creator — In-App Authoring, Typed Parameters & Per-Cell ROE | FR-5100 family, FR-3420, NFR-2000/NFR-2010 | ✅ Done *(built; status updated 2026-10-17, `BL-0200`)* | Consolidates `FEAT-5100` (0% built) into one distinct Feature, folding in `BL-0051`/`BL-0052` fully: in-app iterative authoring via a server-side draft session (resolving `CR-11`), JSON view, 2D/3D ground-truth preview, TLE/lat-long/asset entry, asset menu, seat/role matrix, typed per-payload-type/bus parameter sub-schemas, and real per-cell ROE enforcement. Grounded in `ADS-5100A`/`ADS-5100B`. v1.1 closed the Critical Open Question v1.0 raised: `04-requirements-engineering` added `FR-5120`-`FR-5180`/`FR-3420`/`NFR-2010`, giving every part of this Feature's scope an owning requirement. |
| [FS-118](FS-118-external-vignette-directories.md) | External Vignette Directories & Safe Scenario Save Target | FR-5410/FR-5420, NFR-3700 | ✅ Done *(built; status updated 2026-10-17, `BL-0200`)* | Load vignettes from configured external directories alongside the built-in library; restrict `save_vignette` to a configured user directory; generalize the existing path-traversal guard to every new content root. Closes `BL-0082` (external validation report item B16). Four Open Questions (draft-save code-path identity, unreadable-external-directory behavior, no-user-directory-configured behavior, id-collision tie-break rule) left for `07-implementation-planning`/`04` to resolve. |
| [FS-119](FS-119-bulk-tle-omm-import.md) | Bulk TLE and CCSDS OMM Multi-Object Import | FR-5220 | ✅ Done *(built; status updated 2026-10-17, `BL-0200`)* | Import many objects from one TLE or CCSDS OMM file in one operation with per-object side/template assignment. Closes `BL-0067` (item B1). |
| [FS-120](FS-120-save-as-scenario.md) | Save-as-Scenario (Mid-Exercise State → New Starting Vignette) | FR-5510 | ✅ Done *(built; status updated 2026-10-17, `BL-0200`)* | Saves a running session's current tracks/resources/health/space-weather as a new vignette starting at the save moment, with simulator version recorded. Closes `BL-0071` (item B5). |
| [FS-121](FS-121-ephemeris-export.md) | State-Vector/Ephemeris & TLE Export (`FEAT-7400`) | FR-7410/FR-7420/FR-7430/FR-7440 | ✅ Done *(built; status updated 2026-10-17, `BL-0200`)* | Truth and cell-observed state-vector export, ECI/RIC, CSV/CCSDS OEM + companion RIC file, reusing the existing AAR replay mechanism per `ADS-1500` (closes `BL-0069`, item B3); v2.0 (2026-10-10) adds the quick, copyable, fog-of-war-filtered current-epoch TLE export for any cell-visible satellite (`BL-0109`). **v2.1 (2026-10-15):** amended `FR-7440` brings a cell's own satellites into TLE-export scope (`BL-0159`/`BL-0201`); remediation package owed against `IP-1211`. |
| [FS-122](FS-122-sensor-modality-models.md) | Sensor Modality Models | FR-1610-FR-1670 | ✅ Done *(v1.1 built, status updated 2026-10-17, `BL-0200`; v1.2 beam-mode behaviour built by `IP-1223`, `VERIFIED`)* | Fence/dish radar beam-mode variants, optical solar/lunar exclusion angle, space-based min-range/altitude-band affinity, cue-dependent tasking precondition, passive-RF multilateration network, hosted-sensor orbit-following. Closes `BL-0073` (item B7) and `BL-0083` (item B17). **v1.1 (2026-10-15):** adds `FR-1670`. A passive EO sensor with a declared usable phase-angle range has its observation gain degraded (smoothly, never rejected) outside that range. The angle comes from the shared `cats_phase_angle_deg` (`BL-0152`), and `R109` §3.11's 0–90°/0–150° are recommended author values, not implicit defaults (`BL-0151`). Closes `BL-0122` at spec. FR-1620 Open Question closed by reference (`BL-0113`). |
| [FS-123](FS-123-space-weather-index-coupling.md) | Space-Weather-Index-Driven Drag and Anomaly-Rate Coupling | FR-1230/FR-4440 | ✅ Done *(v1.1 built by `IP-1230`, `VERIFIED`; Open Questions closed by ADR-0039)* | Couples a declared Kp/F10.7 index time series into deterministic LEO drag decay and environment-induced anomaly firing rate. Closes `BL-0074` (item B8). |
| [FS-124](FS-124-debris-field-persistence-estimate.md) | Debris-Field Persistence Estimate by Altitude | FR-1430 | ✅ Done *(built; status updated 2026-10-17, `BL-0200`)* | An informational, altitude-derived persistence estimate on every `DebrisField`, deliberately narrower than Candidate Requirement `CR-17`. Closes `BL-0077` (item B11). |
| [FS-125](FS-125-maneuver-ledger.md) | Per-Asset Manoeuvre Ledger with Purpose Tags and CSV Export | FR-1320 | ✅ Done *(built; status updated 2026-10-17, `BL-0200`)* | A per-asset, purpose-tagged manoeuvre ledger view and CSV export, derived from existing `EventLog` state. Closes `BL-0072` (item B6). |
| [FS-126](FS-126-telemetry-csv-export.md) | Per-Asset Telemetry CSV Export Over a Time Span | FR-2320 | ✅ Done *(built; status updated 2026-10-17, `BL-0200`)* | Fog-of-war-respecting telemetry CSV export for a named asset/cell/time-span, reflecting `FR-4430`'s anomaly-inject channel perturbations. Closes `BL-0075` (item B9). |
| [FS-127](FS-127-effect-authorization-gating-and-live-roe.md) | Optional Effect-Authorization Gating and Live Rules-of-Engagement Changes | FR-3430/FR-3440 | ✅ Done *(built; status updated 2026-10-17, `BL-0200`)* | Controller-role approval workflow for gated effect types plus live, logged mid-session ROE-flag changes. Closes `BL-0076` (item B10). |
| [FS-128](FS-128-variable-speed-aar-replay.md) | Variable-Speed AAR Replay from Truth or a Single Cell's Viewpoint | FR-7330 | ✅ Done *(built; status updated 2026-10-17, `BL-0200`)* | Continuous, speed-adjustable timeline playback from ground truth or a fog-respecting single-cell viewpoint, additive to the existing point-in-time AAR reconstruction. Closes `BL-0078` (item B12). |
| [FS-129](FS-129-jamming-delivery-and-effect-detectability.md) | Jamming-Delivery Degradation and Per-Effect-Class Detectability Settings | FR-1440/FR-1450 | ✅ Done *(built; status updated 2026-10-17, `BL-0200`)* | Successful uplink/crosslink jamming now degrades command/relay delivery, not telemetry alone; each effect class carries its own configurable detectability/attribution-difficulty setting. Closes `BL-0081` (item B15). |
| [FS-130](FS-130-ric-frame-view-and-cats-overlay.md) | Live RIC-Frame Relative-Motion View & CATS Overlay | FR-8210/FR-8220 | ✅ Done *(built; status updated 2026-10-17, `BL-0200`)* | A live, operator-selectable RIC-frame relative-motion view, distinct from the existing one-shot CSV/CCSDS-OEM export (`FS-121`); a CATS illumination-phase-angle overlay for the view's selected chase satellite, extending it. The first FS in this set whose approved input is a real `05-feature-decomposition` Feature Catalog entry (`FEAT-8200`). Closes `BL-0107`/`BL-0111`. |
| [FS-131](FS-131-load-time-vignette-validation.md) | Load-Time Vignette Validation (`FEAT-5300`) | FR-5310–FR-5314, NFR-1600, NFR-2200 | ✅ Done (v1.1 built by `IP-1310`/`IP-1311`, `VERIFIED`), except the `FR-5310` template-reference clause, which is unbuilt and blocked (Open Question 1 → `04`/`03`, `BL-0233`) | One load-time gate: a vignette becomes a session or is refused with an error naming the failing element (schema/field rules incl. late-firing sensor validators, TLE well-formedness, `roles_needed` resolution, unique ids, unknown/unsafe ids), never a bare 500, a silent console or a later crash; a refused load leaves the session registry untouched. First concrete case: `BL-0220`. |
| [FS-132](FS-132-effect-resource-bounds.md) | Effect Resource Bounds — Salvo Ammunition, Jammer Power Rating (`FEAT-1400` slice) | FR-1460/FR-1470/FR-1480 | ✅ Done *(v1.0 built by `IP-1320`; v1.1 `FR-1480` built by `IP-1321`; both `VERIFIED`)* | An engagement never fires more rounds than its effector holds (checked at preview, issue and execution); every fired salvo is charged whether it hits or misses (v1.1, owner decision); a jam never changes the jammer's power rating (ADR-0037). |
| [FS-133](FS-133-test-origin-traceability.md) | Test-Origin Traceability & Release Verification (`FEAT-12100`) | NFR-1510/NFR-2820/NFR-2830/NFR-3840/NFR-2850 | ✅ Done (v1.1: `IP-1330`–`IP-1333`, `IP-1334`, `IP-1335` `VERIFIED`; the `NFR-1510` dependency lock is produced at every release by `11-release-readiness`, not by a package) | Every test carries a registered `verifies` marker naming its requirement leaf (else FS, else IP); a suite check fails on untagged tests and on IDs that don't resolve; a read-only origin report feeds the RTM Test column and the release relevance audit; every release ships a dependency lock (`BL-0310`, `BL-0299`). |
| [FS-134](FS-134-browser-console-rule-suite.md) | Automated Browser Verification of Load-Bearing Console Rules (`FEAT-12200`) | NFR-2840 | ✅ Done (built by `IP-1340`, `VERIFIED` 2026-10-24) | A small Playwright/headless-Chromium suite, in the default run (skipped loudly where no browser), that checks no ground truth in a player seat, disabled-with-reason before issue, and consequence confirmation for `engage`/`cyber` (`BL-0304`, GDS-08 OQ1). |
| [FS-135](FS-135-documentation-integrity-checks.md) | Documentation Integrity Checks (`FEAT-12300`) | NFR-3800/NFR-3810/NFR-3820/NFR-3830 | ✅ Done for `NFR-3800`/`NFR-3820`/`NFR-3830` (built by `IP-1350`, `VERIFIED`); the `NFR-3810` retired-document check is unbuilt and waits on an owner decision (OQ1, `BL-0319`) | Four checks in the full suite over live docs (frozen history exempt): relative links resolve (82 broken today), no live reference to a registered retired document, each `INDEX.md` lists its folder (3 unlisted today), paired status ledgers agree; a shrink-only allow-list makes the first green run the one-time cleanup (`BL-0297`). |
| [FS-201](FS-201-competency-assessment.md) | Competency Assessment | DOM-002 | ✅ Done | Read-only rubric-based measurement layer over existing engine state. |
| [FS-202](FS-202-rubric-authoring.md) | Rubric Authoring *(candidate)* | DOM-002 | 🅿️ Scoped, not authorized | Tooling for facilitators/instructors to define/adjust FS-201 rubric tiers. |
| [FS-301](FS-301-research-analytics.md) | Research Analytics | DOM-004, DOM-005 | ✅ Done | Structured multi-run/cohort export for instrument-grade research use. |

## Status legend

Per [`MSTR-006`](../master/MSTR-006-governance-principles.md) §2: ✅ Done · 🚧 In progress · ⛔ Planned · 🅿️ Scoped, not authorized.

**FS-106 was narrowed to v2.0** and **FS-109/FS-110/FS-111 were newly authored** per
`docs/feature-planning/05-feature-review.md` Finding F-03: FS-106 v1.0 bundled the White Cell
facilitator UI together with three architecturally distinct capabilities (multiplayer/LAN session
transport, save/resume, AI-Red doctrine automation), each carrying its own dedicated ADRs and
source module independent of the facilitator UI. `IMP-106A`/`IP-1060` (the Implementation Packages
written against FS-106's prior, broader scope) have not yet been reconciled against this split —
see each new document's own Risks section.

**FS-112/FS-113/FS-114/FS-115 were newly authored** closing Findings F-02 and F-10: four
Must-priority baselined capabilities (classification banner, Observer access, hot-seat hand-off,
vignette selection/seat assignment) with real FR citations had **zero presence in any of the prior
11 `FS-xxx` documents**. Unlike FS-109/110/111 (split from an existing, narratively-detailed
document), these four had no prior FS-corpus description to draw on — each is written directly from
the requirements baseline and Feature Catalog, and each explicitly flags its own build status as
**unverified** in its Risks/Open Questions sections; confirming whether the underlying code exists
is a follow-on task, not performed here.

**FS-130 is the first document in this set whose approved input is a real `05-feature-decomposition`
Feature Catalog entry** (`FEAT-8200`, in [`docs/feature-planning/03-feature-catalog.md`](../feature-planning/03-feature-catalog.md),
produced 2026-10-03). Every prior FS file's metadata notes "no Feature Catalog exists here" because
none did at the time each was written — that catalog now exists for a growing subset of this
baseline's FRs (see `docs/feature-planning/05-feature-review.md` Finding F-11 for which FRs it does
and does not yet cover), and a future FS authored against an already-catalogued Feature should cite
the catalog entry the same way FS-130 does, rather than repeating the now-stale "no catalog exists"
framing. **FS-121 v2.0 (2026-10-10)** follows that convention: it was extended in place to cover
all of `FEAT-7400` (adding `FR-7440`, recording the already-built `FR-7430`) rather than spawning a
new FS, since one Feature maps to one Feature Specification.

FS-108 and FS-202 are written as **lighter-weight candidate-scope stubs**, not full specs — both
are explicitly named "(candidate)" everywhere they appear in the existing corpus (`DOM-002`,
`DOM-003`), meaning their owning domain documents describe the *gap* they would close but stop
short of committing to them as scoped work. Per [`MSTR-006`](../master/MSTR-006-governance-principles.md) §3, anything beyond
documenting that gap (i.e., promoting them to full ✅ specs or beginning Implementation Packages)
requires explicit user authorization — this index does not assume that authorization.

## Authoring note

All FS files in this set follow the **`06-feature-specification` skill's 20-field template**
(Feature ID → Title → Purpose → Scope → Requirements Implemented → User Workflows → System
Behaviour → Subsystem Responsibilities → Interfaces Used → Data Model Changes → State Changes →
Error Handling → Performance Considerations → Security Considerations → Acceptance Criteria →
Verification Plan → Dependencies → Risks → Open Questions → Related ADRs → Related Interfaces).
The `06-feature-specification` skill governs all new and existing FS-xxx authoring in this repository;
the prior ad hoc per-section structure used in earlier drafts has been superseded in place — every
file retains its existing path, Document ID, and MSTR-006 §5 metadata block.

Each FS file is grounded in: (a) its owning Domain Document's `Produces`/`Feature Mapping`
frontmatter and any explicit "What this framework expects from FS-xxx" section; (b) the
research-encyclopedia topics whose own "Feature Mapping" section names that FS as a consumer; and
(c) verified ADR and ICD interface cross-references cited in each file's Related ADRs and Related
Interfaces fields. No FS file in this set introduces implementation detail (data models, API shapes,
code) — that is Phase 5's job (`docs/implementations/`, not yet authorized).
