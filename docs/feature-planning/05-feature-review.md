# Feature Review

## Mapping note (read first, per this skill's own gotcha rule)

This repository's `docs/features/` directory is **already populated** with 11 full **Feature
Specification** documents (`FS-101`…`FS-301`), governed by a different, pre-existing chain
(`docs/master/MSTR-005-documentation-map.md`: Training Objective → Domain → Research → optional
`ADS-xxx` → **`FS-xxx`** → `IMP-xxx` → code → tests). Those `FS-xxx` files are downstream,
implementation-adjacent specification documents, not this skill's catalog rows. To avoid colliding
with that existing ID space and document type, this decomposition's outputs live under
**`docs/feature-planning/`** and use the prefix **`FEAT-xxxx`** for its 36 catalog rows, per this
skill's own stated rule for exactly this situation.

**Reconciliation — how the existing `FS-xxx` documents map onto this catalog's `FEAT-xxxx` rows:**

*Extended 2026-10-17 (pipeline run #162, `BL-0247`): rows FS-112–FS-132 added, each derived from
the FS's own Feature mapping / approved-input header and the owning Feature of the leaves it newly
implements (an FS's "Requirements Implemented" field also lists leaves it only depends on; those do
not change its mapping). "Slice" means the FS specifies only the named leaves of a Feature whose
other leaves live in another FS. The table was originally written for the first 11 documents.*

| Existing FS-xxx | Maps onto (FEAT-xxxx) | Note |
|---|---|---|
| FS-101 Mission Planning | FEAT-3100 | 1:1 |
| FS-102 Command Scheduling | FEAT-3300, FEAT-3400 | One FS covers two catalog Features |
| FS-103 Custody Management | FEAT-1500 | 1:1 |
| FS-104 SDA Tasking | FEAT-3200 | 1:1 |
| FS-105 Spacecraft Operations | FEAT-2100, FEAT-2200, FEAT-2300, FEAT-2400, FEAT-2500, FEAT-1400 | One FS covers six catalog Features (the whole bus/payload Epic plus effect resolution) |
| **FS-106 White Cell Dashboard** *(v2.0, narrowed 2026-07)* | FEAT-4300, FEAT-4400, FEAT-4600, FEAT-4700 | **Resolved** — see Finding F-03 below; split into four documents |
| FS-107 After Action Review | FEAT-7300 (built on FEAT-7100) | 1:1 |
| FS-108 Inject Authoring *(candidate, unauthorized)* | Authoring-UX layer over FEAT-4400 | Not itself a baselined FR — see Finding F-06 |
| **FS-109 Multiplayer / LAN Session Transport** *(new 2026-07)* | FEAT-6300, FEAT-6400 | Split out of FS-106 v1.0 per Finding F-03 |
| **FS-110 Save & Resume** *(new 2026-07)* | FEAT-7200 | Split out of FS-106 v1.0 per Finding F-03 |
| **FS-111 AI-Red Doctrine Automation** *(new 2026-07)* | FEAT-9100 | Split out of FS-106 v1.0 per Finding F-03 |
| FS-112 Classification Banner | FEAT-4500 | 1:1 — Finding F-02 |
| FS-113 Observer Read-Only Access | FEAT-6500 | 1:1 — Finding F-02 (cites `FR-4610`, owned by FEAT-4600, as a dependency) |
| FS-114 Hot-Seat Hand-Off | FEAT-6600 | 1:1 — Finding F-02 |
| FS-115 Session Setup | FEAT-4100, FEAT-4200 | One FS covers two catalog Features — Finding F-10 |
| FS-116 Role-Scoped Command Catalog | FEAT-3500 | 1:1 (`IP-1160` `BLOCKED` on authorization) |
| FS-117 Vignette Creator | FEAT-5100 | 1:1 — consolidates the catalog entry (`ADS-5100A`/`ADS-5100B`) |
| FS-118 External Vignette Directories | FEAT-5400 | 1:1 (`FR-5410`/`FR-5420`/`NFR-3700`) |
| FS-119 Bulk TLE/OMM Import | FEAT-5200 | Slice: `FR-5220` only; `FR-5210` was already built |
| FS-120 Save-as-Scenario | FEAT-5500 | 1:1 (`FR-5510`) |
| FS-121 Ephemeris Export | FEAT-7400 | 1:1 since v2.0 (all four leaves) |
| FS-122 Sensor Modality Models | FEAT-1600 | 1:1 (all seven leaves since v1.1) |
| FS-123 Space-Weather Index Coupling | FEAT-1200, FEAT-4400 | Cross-Feature slice: `FR-1230` (FEAT-1200) + `FR-4440` (FEAT-4400) |
| FS-124 Debris-Field Persistence Estimate | FEAT-1400 | Slice: `FR-1430` |
| FS-125 Manoeuvre Ledger | FEAT-1300 | Slice: `FR-1320` |
| FS-126 Telemetry CSV Export | FEAT-2300 | Slice: `FR-2320` |
| FS-127 Effect Authorization Gating & Live ROE | FEAT-3400 | Slice: `FR-3420`/`FR-3430`/`FR-3440` |
| FS-128 Variable-Speed AAR Replay | FEAT-7300 | Slice: `FR-7330` (FS-107 owns the rest of FEAT-7300) |
| FS-129 Jamming Delivery & Effect Detectability | FEAT-1400 | Slice: `FR-1440`/`FR-1450` |
| FS-130 RIC-Frame View & CATS Overlay | FEAT-8200 | 1:1 |
| FS-131 Load-Time Vignette Validation | FEAT-5300 | 1:1 (`FR-5310`–`FR-5314`) |
| FS-132 Effect Resource Bounds | FEAT-1400 | Slice: `FR-1460`/`FR-1470` (FS-105 owns `FR-1410`/`FR-1420`) |
| FS-201 Competency Assessment | FEAT-10100 | **Resolved 2026-07** — see Finding F-01 and the update note below |
| FS-202 Rubric Authoring *(candidate, unauthorized)* | *(none — see Finding F-01)* | Rubric-authoring tooling itself was not baselined; only FS-201's own rubric-tier computation (FR-10110) was |
| FS-301 Research Analytics | FEAT-10200 | **Resolved 2026-07** — see Finding F-01 and the update note below |

**Update (2026-07): Findings F-02 and F-10 are now resolved.** FEAT-4500 (Classification Banner) →
[FS-112](../features/FS-112-classification-banner.md); FEAT-6500 (Observer Read-Only Access) →
[FS-113](../features/FS-113-observer-read-only-access.md); FEAT-6600 (Hot-Seat Hand-Off) →
[FS-114](../features/FS-114-hot-seat-handoff.md); FEAT-4100/FEAT-4200 (Vignette Selection/Seat
Assignment) → [FS-115](../features/FS-115-session-setup.md). All four are newly authored, not
split from an existing document (unlike FS-109/110/111) — each explicitly flags its own **build
status as unverified** in its Risks/Open Questions sections, since no prior FS-corpus narrative
existed to confirm against. Verifying build status against the actual `spacesim/` source tree is
the one remaining piece of both findings' remediation, not performed by this review.

**Update (2026-07): Finding F-01 is now resolved, closing the last two `*(none)*` rows in the
reconciliation table above.** Once `CR-19`/`CR-20` were promoted to baselined `FR-10110`/`FR-10210`
and Epic `EP-10000` (Features `FEAT-10100`/`FEAT-10200`) was added to `03-feature-catalog.md`,
[FS-201](../features/FS-201-competency-assessment.md) (whose own "Requirements Implemented" field
already cites `FR-10110`) became `FEAT-10100`'s Feature Specification, and
[FS-301](../features/FS-301-research-analytics.md) (already citing `FR-10210`) became `FEAT-10200`'s.
No new `FS-xxx` document was authored for either — the existing specs already fully describe the
capability their new owning Feature names, per this skill's "don't re-derive what the Feature
Catalog entry already decided" rule; only this table's back-reference was stale. `FS-202` (Rubric
Authoring) remains unmapped: it is a still-unauthorized candidate over FS-201's rubric-tier output,
not itself a baselined requirement's Feature.

## Quality-gate verification

**Re-verified 2026-10-23 (run #212, GDS ladder alignment sweep) — supersedes the 2026-10-17 block
below where they differ.** Same mechanical checks, against the requirements documents as updated by
run #211 ([`reviews/requirements-update-gds-ladder-batch.md`](../reviews/requirements-update-gds-ladder-batch.md)):

- **Completeness:** all **106** baselined FR leaves and all **47** baselined NFR leaves are each
  owned by exactly one of the **48** Features; none missing, none owned twice, no Feature owns an ID
  that is not a baselined leaf. The 21 run #211 leaves were placed this run, plus `FR-1480`, which
  no Feature owned (F-21).
- **Epic assignment:** all 48 Features in exactly one Epic (6+5+5+7+5+6+4+2+1+2+2+3 = 48, twelve
  Epics).
- **Release assignment:** 4 Prototype + 4 MVP + 29 Release 1 + 11 Release 2 + 0 Future = 48, and
  no Feature is bucketed before any prerequisite (F-23).
- **Dependencies:** 75 edges, each recorded on both ends; **no cycle**; the diagram's edge set
  equals the catalog's. Longest chain still 7 edges.

**Re-verified 2026-10-17 (run #151, full inventory sweep, `BL-0153`) — supersedes the bullets
below where they differ.** Checked mechanically against the requirements documents' own leaf
headings and the catalog's own tables:

- **Completeness:** all **103** baselined FR leaves and all **28** baselined NFR leaves are each
  owned by exactly one of the **45** Features. None missing, none owned twice, no Feature owns an
  ID that is not a baselined leaf. (Before this sweep 37 FR and 5 NFR leaves had no owner — F-11.)
- **Epic assignment:** all 45 Features in exactly one Epic (6+5+5+7+5+6+4+2+1+2+2 = 45, eleven Epics).
- **Release assignment:** all 45 in exactly one bucket — 3 Prototype + 4 MVP + 27 Release 1 + 11
  Release 2 + 0 Future = 45 — and no Feature is bucketed before any prerequisite (F-18).
- **Dependencies:** 67 edges, each recorded on both ends; **no cycle** (F-14 records the one the
  sweep avoided); the Mermaid diagram's edge set equals the catalog's.


- **Completeness (updated 2026-07; partially updated 2026-10-03 — see Finding F-11):** All 49
  original baselined `FR-xxxx` leaves, the 2 new `FR-10000`-category leaves (`FR-10110`/
  `FR-10210`, promoted from `CR-19`/`CR-20` once `ADR-0032`/`ADR-0033` resolved their blocking
  conflicts), and all 23 baselined `NFR-xxxx` leaves are each owned by exactly one Feature in
  `03-feature-catalog.md` (now **41 Features**, up from 38 — see Finding F-11 for the three new
  ones). No FR/NFR ID among these is missing; none appears twice. **This bullet is honestly
  incomplete against the requirements document's current full FR count** — see Finding F-11: a
  large number of FR leaves added to `01-functional-requirements.md` between this catalog's
  original authoring and 2026-10-03 (the Must-tier, Should-tier, and FS-117 intake batches) remain
  outside every Feature's `Included Requirements`, this run's own scope limitation notwithstanding.
- **Epic assignment:** All 41 Features appear in exactly one Epic's `Features Included` list in
  `02-epic-catalog.md` (6+5+5+7+3+6+4+2+1+2 = 41, matching the catalog's own updated Summary).
- **Release assignment:** All 41 Features appear in exactly one bucket in `01-release-plan.md`
  (2 Prototype + 8 MVP + 21 Release 1 + 10 Release 2 + 0 Future = 41).
- **Circular dependencies:** Two found and resolved with stated rationale, not silently broken —
  see `04-feature-dependency-graph.md`'s "Circular dependencies found" section and Finding F-05
  below.
- **Candidate/non-baselined items:** 18 Candidate Requirements, 7 Candidate NFRs, 15 Strategic
  Review Future Concepts, and 13 Strategic Review Gaps (count at original authoring time — after
  the DOM-002/004/005 backfill and subsequent `CR-19`/`CR-20` promotion, **19 Candidate
  Requirements remain** — `CR-01`–`CR-18`, `CR-21`) are deliberately **excluded** from every
  Feature's `Included Requirements` — they are not approved, so this skill does not group them
  (see Finding F-04).

## Findings

| # | Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| F-01 | Architectural inconsistency / requirements-baseline gap — **FULLY RESOLVED 2026-07 (in two stages)** | FS-201, FS-301, DOM-002, DOM-004, DOM-005, FR-10110, FR-10210, CR-21, ADR-0032, ADR-0033 | Three existing Feature Specifications (Competency Assessment, Rubric Authoring, Research Analytics) were grounded directly in Domain documents (DOM-002/004/005) but had **no corresponding FR-xxxx/NFR-xxxx leaf anywhere in `docs/requirements/`**. Stage 1 (`04-requirements-engineering` against DOM-002/004/005) found this was not a clean backfill: DOM-002/FS-201's automated rubric computation conflicted with ADR-0017 and DOM-004/FS-301's dedicated research-export interface directly conflicted with ADR-0029. | High | **Stage 1 done:** zero new baselined FR/NFR leaves at first — `CR-19`/`CR-20`/`CR-21` added to Candidate Requirements instead, since baselining either conflicting capability would have contradicted an Accepted ADR. DOM-005 yielded no new leaf at all (validation methodology, not a system capability). **Stage 2 done (same session, on direct project-owner instruction):** the project owner resolved both conflicts — `ADR-0032` narrows `ADR-0017` with a carve-out, `ADR-0033` supersedes `ADR-0029` outright — and `CR-19`/`CR-20` were promoted to baselined `FR-10110`/`FR-10210` (Epic `EP-10000`, Features `FEAT-10100`/`FEAT-10200` added to this catalog). `CR-21` remains an active, unaffected Candidate. This corrects this row's own original prior "roughly 6–9 additional Features" estimate twice over: first down to 0, then up to 2 concrete Features once the conflicts were actually resolved rather than merely documented. |
| F-02 | Missing Feature Specification — **RESOLVED 2026-07** | FEAT-4500 → FS-112, FEAT-6500 → FS-113, FEAT-6600 → FS-114 | Classification Banner, Observer Read-Only Access, and Hot-Seat Hand-Off Screen-Blank Menu each had a real, Must-priority baselined FR (FR-4510, FR-6510, FR-6610), but **zero presence in any of the 11 existing `FS-xxx` documents** and an `UNASSIGNED` Impl. Package citation in the RTM. This confirmed the original audit finding verbatim. | High | **Done:** FS-112/FS-113/FS-114 authored directly from the requirements baseline (no prior narrative to draw on). **Not yet done:** build-status verification against `ui_web/static/`, `session/`, and `session/aar.py` export paths — each new document flags this as its own top Open Question. |
| F-03 | Feature too large (existing FS, not this catalog) — **RESOLVED 2026-07** | FS-106-white-cell-dashboard.md → FS-106 v2.0, FS-109, FS-110, FS-111 | The existing FS-106 document bundled **ten** of this catalog's 36 Features across **three different Epics** (EP-4000 White Cell Control, EP-6000 Multiplayer Transport, EP-7000 Save/Resume, EP-9000 AI-Red) — including two capabilities (multiplayer clock/locking, AI-Red) that each carry their own dedicated ADRs (ADR-0014/0026 for multiplayer; ADR-0021/0024/0030 for AI-Red) and their own source module (`session/inprocess.py`; `session/redai.py`). This was the single largest cohesion violation found. | High | **Done:** FS-106 narrowed to v2.0 (White Cell control-plane proper: clock-authority trigger/god-view/injects/adjudication); FS-109 (Multiplayer/LAN Transport, FEAT-6300/6400); FS-110 (Save/Resume, FEAT-7200); FS-111 (AI-Red, FEAT-9100) authored. **`IMP-106A`/`IP-1060` reconciliation is also done:** IP-1060 narrowed to v2.0; IP-1090/IP-1100/IP-1110 authored (reorganizing IP-1060 v1.0's already-verified code citations, no new verification performed); `00-master-build-plan.md`'s package table/dependency graph/summary stats updated; `IMP-106A` (frozen, superseded) gained a forward-pointer note only. |
| F-04 | Missing Features (not yet approved — informational, not a defect) | CR-01–18, CNFR-01–07, FC-01–15, GAP-01–13 | The 18 Candidate Requirements, 7 Candidate NFRs, and the July-2026 Strategic Review's 15 Future Concepts / 13 Gaps are **correctly excluded** from this catalog per this skill's own constraint (only approved/baselined requirements are decomposed). Substantial overlap exists between these sets (e.g. FC-02/GAP-08 = CR-01/CNFR-06; FC-06/GAP-10 = CR-12; FC-09 = CR-13; FC-10/GAP-03 = CR-14; FC-13 = CR-15; FC-11/GAP-12 = CR-16; FC-08/GAP-02 = CR-17), so the unique count of not-yet-approved capability concepts is roughly **25 CR/CNFR-tier items + 8 FC items with no CR yet (FC-01, FC-03, FC-04, FC-05, FC-07, FC-12, FC-14, FC-15) + a handful of GAP-only research topics (GAP-01, GAP-06, GAP-07, GAP-09) that don't yet even have a candidate-requirement framing** — see the reconciliation arithmetic below. | Medium (informational) | This is the primary source of the gap between this catalog's 36 Features and the user's expected 50–80 — see "Reconciling the 50–80 expectation" below. Not resolved by this catalog; requires `04-requirements-engineering` (to baseline the CR/CNFR tier) and possibly `03-architecture-design-synthesis` first (for the FC items with no CR yet). |
| F-05 | Architectural inconsistency (source requirements document) | FR-1110, FR-4310, FR-1120, FR-7110 | Two 2-node circular dependency citations exist in `docs/requirements/01-functional-requirements.md`'s own `Dependencies` fields (FEAT-1100↔FEAT-4300; FEAT-1100↔FEAT-7100), both from the same root cause: a leaf FR citing a sibling *category* ID rather than the specific leaf inside it. Resolved for this graph with stated rationale (see `04-feature-dependency-graph.md`); not silently fixed. | Medium | The requirements owner may want to tighten FR-1110's and FR-1120's `Dependencies` fields to cite the specific leaf (FR-4310, FR-7110) rather than the category header, which would make the intended direction unambiguous without changing meaning. |
| F-06 | Requirements traceability gap (pre-existing, confirmed independently) | 13 of 49 FR leaves | FR-1130, FR-3310, FR-3510, FR-3520, FR-4110, FR-4210, FR-4510, FR-4610, FR-4710, FR-4720, FR-6510, FR-6610, FR-7220 all show `UNASSIGNED` in the RTM's own Impl. Package column (≈27% of the baseline). Most (all except FR-4510/FR-6510/FR-6610, per Finding F-02) are narratively described as shipped in an existing `FS-xxx` document despite the missing citation — a documentation-hygiene gap, not necessarily a build gap. | Medium | A dedicated traceability-verification pass (grep the actual `spacesim/` source tree per FR, as the RTM's own stated method describes) would close most of this without new development. |
| F-07 | Feature possibly too large (judgment call, not a defect) | FEAT-8100, FEAT-1100 | FEAT-8100 (Browser Console) bundles 1 FR with 6 cross-cutting NFRs (performance, hardware floor, config, portability, accessibility, external-integration boundary); FEAT-1100 bundles 3 FR with 5 NFRs (determinism, sub-stepping, maintainability, data-integrity, test-gating). Both were deliberately bundled here (stated in each Feature's own Description) rather than distributing each NFR to every Feature it touches, to avoid restating the same cross-cutting quality attribute 6–8 times across the catalog. A stricter reviewer could reasonably prefer the distributed alternative. | Low | Acceptable as designed; flagged for awareness, not required to change. |
| F-08 | Feature possibly too small (judgment call, not a defect) | FEAT-1300 | Impulsive Maneuver & Δv Budget Accounting owns exactly one FR (FR-1310) and cites no ADR of its own ("none directly — restates a GDS-04 validation rule"). A stricter reviewer could merge it into FEAT-1200 (Orbital Propagation & Access-Window Geometry) as a sub-capability rather than a standalone Feature. | Low | Kept standalone here because Δv is independently named as "the operator's hardest constraint" (a distinct user-facing training objective) and has its own dedicated design document (`design/14-delta-v-economy.md`) — but this is a closer call than the catalog's other single-FR Features (e.g. FEAT-9100 AI-Red, which has three dedicated ADRs). |
| F-09 | Architectural inconsistency (deliberate, disclosed) | EP-9000 | EP-9000 (AI-Red) is a single-Feature Epic, which the Best Practices guidance generally discourages ("an Epic that exists to hold exactly one Feature is a sign the Epic layer added no organizing value"). Kept as its own Epic here specifically because of its outsized strategic weight (the Strategic Review's #1 tracked gap, FC-02/GAP-08) despite module-wise fitting naturally under EP-3000 (Command Planning) or EP-4000 (White Cell). | Low | Disclosed rather than hidden; a reviewer who weighs strict subsystem-alignment over strategic signaling could reasonably fold EP-9000 into EP-3000. |
| F-10 | Missing Feature Specification (found during F-03's remediation) — **RESOLVED 2026-07** | FEAT-4100, FEAT-4200 → FS-115 | While splitting FS-106 (Finding F-03), a close read of FS-106 v1.0's actual User Workflows (not just this catalog's earlier mapping guess) confirmed it never covered vignette selection/parameter tuning (FR-4110) or seat-to-role assignment (FR-4210) at all — these session-setup capabilities had **zero presence in any existing `FS-xxx` document**, matching the pattern of F-02's three findings exactly. | High | **Done:** FS-115 authored, folding FEAT-4100/FEAT-4200 into one "Session Setup" document since both are Must-priority, sequential, White-Cell-only setup-phase steps with a direct Feature Catalog dependency edge between them. **Not yet done:** build-status verification, same as F-02. |
| F-11 | Requirements-baseline completeness gap — **RESOLVED 2026-10-17 by the run #151 sweep (F-13)**; original text: **this run's own scope is explicitly partial, by instruction** (informational, not a defect of this run's actual output) | `FR-1600`-family (`FR-1610`-`FR-1670`), `FR-7400`-family (`FR-7410`-`FR-7440`), `FR-8200`-family (`FR-8210`/`FR-8220`), `FR-4450`, `FR-4620`, plus every other FR leaf baselined between this catalog's original 49-FR authoring and 2026-10-03 that this run did **not** touch (the Must-tier batch `FR-4420`/`FR-4430`/`FR-5220`/`FR-5410`/`FR-5420`/`FR-5510`; the Should-tier batch `FR-1230`/`FR-1320`/`FR-1430`-`FR-1450`/`FR-2320`/`FR-3430`/`FR-3440`/`FR-4440`/`FR-7330`; the `FS-117` batch `FR-5120`-`FR-5180`/`FR-3420`; the `ADR-0032`/`ADR-0033` conflict-resolution batch, already counted above as `FR-10110`/`FR-10210`) | This `05-feature-decomposition` run was explicitly scoped (by the invoking instruction) to decompose only the six FR leaves baselined this same session for `BL-0107`/`BL-0109`/`BL-0111`/`BL-0122`/`BL-0079`, plus — as a necessary side effect of giving `FR-1670`/`FR-7440` a cohesive Feature home rather than an isolated one — their six already-`VERIFIED` siblings (`FR-1610`-`FR-1660`, `FR-7410`-`FR-7430`). Every other FR leaf added to `01-functional-requirements.md` since this catalog's original authoring pass remains outside every Feature's `Included Requirements` — a real, pre-existing completeness gap this run did not close and was not asked to close. | Medium (a genuine, large completeness gap; not Critical because every un-decomposed FR is independently `VERIFIED`-built and narratively traceable through the existing `FS-xxx` corpus per `CLAUDE.md`'s Code Map, so no capability is silently un-tracked — only un-cataloged at this planning layer) | A future, dedicated `05-feature-decomposition` pass should re-run Step 0's inventory against the full current `01-functional-requirements.md` and close this gap in one sweep, rather than letting each new intake batch's own narrowly-scoped `05` run leave an ever-larger residue of undecomposed-but-shipped FR leaves behind it. Not performed by this run, which was explicitly instructed not to touch any FR already covered by an existing catalog entry and, by extension, not instructed to backfill FRs that were never covered at all. |
| F-12 | Open upstream research gates (informational — correctly left open, not resolved here) | FEAT-1600 (`FR-1670`), FEAT-8200 (`FR-8210`, `FR-8220`), `BL-0108`, `BL-0112`, `BL-0151`, `BL-0152` | Two of this run's three new Features carry an open research gap that must close before `06-feature-specification` can design them: `BL-0108` (no R1xx topic grounds RIC-frame relative-motion display as an operational concept, blocks `FEAT-8200`/`FR-8210`'s design) and `BL-0112` (no R1xx topic grounds the Sun-target-observer CATS phase angle, blocks `FEAT-8200`/`FR-8220`'s and `FEAT-1600`/`FR-1670`'s concrete design). `BL-0151`/`BL-0152` (the concrete default phase-angle range/curve ambiguity, and the shared-computation note between `FR-1670`/`FR-8220`) are two further open, `06`-routed findings this run's upstream `04-requirements-engineering` pass already harvested. | Low (correctly deferred, not a defect — each gap's own revisit trigger is stated as before `06-feature-specification`, not before this decomposition) | No action from this skill — `03-feature-catalog.md`'s own Open Questions fields for `FEAT-1600`/`FEAT-8200` already name these gates explicitly, so whoever runs `06-feature-specification` next sees them without needing this review document open at the same time. Resolve via `02-research-ow-orbital-mechanics` before specifying either Feature in depth. |
| F-13 | Requirements-baseline completeness — **resolved this run** (`BL-0153`) | 37 FR + 5 NFR leaves: `FR-1230`, `FR-1320`, `FR-1430`–`FR-1470`, `FR-2320`, `FR-3420`–`FR-3440`, `FR-4420`–`FR-4440`, `FR-5120`–`FR-5180`, `FR-5220`, `FR-5311`–`FR-5314`, `FR-5410`, `FR-5420`, `FR-5510`, `FR-7330`, `FR-11110`–`FR-11420`, `NFR-2010`, `NFR-3400`–`NFR-3700` | Step 0 re-run against the whole current baseline. 28 leaves joined existing Features by parentage; 14 went to four new Features (FEAT-5400, FEAT-5500, FEAT-11100, FEAT-11300; new Epic EP-11000). `FR-1460`/`FR-1470` (`BL-0238`/`BL-0245`) joined FEAT-1400. | Info | None — closes F-11. Re-run the same mechanical check on every future delta pass so the residue cannot rebuild. |
| F-14 | Requirement assigned outside its parent's Feature (to avoid a cycle) | `FR-5314`; FEAT-4200, FEAT-5300, FEAT-4100 | By parentage `FR-5314` (declared roles name declared assets) is FEAT-5300's. But it depends on `FR-4210` (FEAT-4200), FEAT-4200 depends on FEAT-4100, and FEAT-4100 on FEAT-5300 — so placing it there makes `FEAT-5300 → FEAT-4200 → FEAT-4100 → FEAT-5300`. It went to FEAT-4200, which owns the `roles_needed` concept the check protects; FEAT-4200 now depends on FEAT-5300 directly. The leaf is still specified and built by FS-131/`IP-1310`, which is fine: an FS may span Features (FS-102, FS-105 already do). | Low | No action required. If the requirements owner prefers parentage to match, `04` could re-parent `FR-5314` under `FR-4200`; that is cosmetic. |
| F-15 | Feature possibly too small (judgment call) | FEAT-5500 | One FR (`FR-5510`). Kept standalone: it is its own `FR-5500` group with its own FS (FS-120) and package (`IP-1200`), and folding it into FEAT-5400 or FEAT-7200 would mix a content-export capability with directory policy or session resume. | Low | Keep; revisit if a second save-as leaf appears. |
| F-16 | Missing architecture detail | FEAT-11100, FEAT-11300 (EP-11000) | The training corpus has no component in the ICD's C1–C12 set, and GDS-03 names no subsystem for `docs/training/`, so both Features carry "none" in Affected Subsystems/Interfaces. The `FR-11000` family's own Related Interfaces fields say the same ("documentation artifact"). Not assigned a subsystem here (this skill does not draw architecture). | Low | `03-architecture-design-synthesis`, at its next GDS-03 touch: say whether the training corpus is a named component or deliberately outside the component model. |
| F-17 | Epic-level mutual dependencies (informational) | EP-1000 ↔ EP-3000; EP-4000 ↔ EP-5000 | The new edges make two Epic pairs depend on each other (e.g. FEAT-3100 → FEAT-1300 while FEAT-1200 → FEAT-3100). The Feature graph has no cycle, so build order is still well defined; Epics are thematic groupings, not build units. | Low | None required. A reader planning by Epic should plan by the Feature graph. |
| F-18 | Release buckets inconsistent with dependencies — **fixed in Step 4 this run** | FEAT-7100, FEAT-1300, FEAT-1400, FEAT-5100, FEAT-4400 | Six Feature-before-prerequisite placements: FEAT-1100 (Prototype) on FEAT-7100 (MVP) — pre-existing and missed by earlier passes; FEAT-1300, FEAT-1400 (MVP) on FEAT-3100/3400 (Release 1); FEAT-5100 (MVP) on FEAT-4200 (Release 1); FEAT-2300 (Release 1) on FEAT-4400 (Release 2). Fixed by moving FEAT-7100 → Prototype, FEAT-1300/1400/5100 → Release 1, FEAT-4400 → Release 1, each justified in `01-release-plan.md`. This is Step 4's own output, not a review edit. | Low | None further. The plan reconstructs a shipped system; no move changes what is built. |
| F-19 | Features that grew (judgment call) | FEAT-1400 (2 → 7 FRs), FEAT-3400 (1 → 4), FEAT-5100 (1 → 7 FRs + 2 NFRs) | Each grew by its own `FR-x400`/`FR-5100` children, all one stakeholder need and one subsystem; none is split. FEAT-1400 now mixes resolution math with resource-bound validation (`FR-1460`/`FR-1470`), which are verified together in the consumption step. | Low | Keep. Revisit FEAT-5100 if the Creator gains a second, separable workflow. |
| F-20 | Downstream gaps (next stage) | `FR-1460`, `FR-1470` (FEAT-1400); `FR-1230` (FEAT-1200), `FR-4440` (FEAT-4400) | `FR-1460`/`FR-1470` are Must, unimplemented, with no FS. `FR-1230`/`FR-4440` (space weather, `BL-0074`) are Should, unimplemented, with no FS, and carry open design questions (`BL-0104`, `BL-0121`). The FS ⇄ FEAT mapping table at the top of this review also predates FS-116–FS-131. | Medium (`FR-1460`/`FR-1470` are Must) | `06-feature-specification` next on `FR-1460` + `FR-1470` (extend FS-105, which owns `FR-1410`, or a small remediation FS), then one `07` remediation package. Space-weather stays where its backlog entries route it. Refresh the mapping table at the next `05` touch. |

### Findings added 2026-10-23 (run #212, GDS ladder alignment sweep)

| # | Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| F-21 | Requirement not assigned (found by the mechanical check) — **fixed this run** | `FR-1480`; FEAT-1400 | `FR-1480` (a fired salvo is charged whether it hits or misses, `IP-1321`, owner decision `BL-0249`) was baselined after the run #151 sweep by a `04` pass that no `05` delta followed, so no Feature owned it. It joins FEAT-1400 beside `FR-1460`, which it refines. | Low | None further. As F-13 already says: run the mechanical check on every `04` delta, not only on large sweeps. |
| F-22 | Architectural inconsistency (deliberate, disclosed) | EP-12000; FEAT-12100, FEAT-12200, FEAT-12300 | Every other Epic follows one `FR-x000` group; EP-12000 holds only NFRs (`NFR-1510`, `NFR-2820`–`NFR-2840`, `NFR-3800`–`NFR-3840`). These constrain how the product is verified, released and documented, so distributing them across product Features (the F-07 bundling pattern) would put the test-marker backfill or a link checker inside, say, FEAT-1100, where no specification would naturally pick it up. | Low | Keep. The three Features map one-to-one onto the three pieces of work the owner decided (`BL-0310`, `BL-0304`, `BL-0297`). |
| F-23 | Release buckets inconsistent with new dependencies — **fixed in Step 4 this run** | FEAT-5300, FEAT-6200, FEAT-1100, FEAT-8100 | `NFR-1610` (FEAT-1100, Prototype) cites `NFR-1600` (FEAT-5300, MVP); `NFR-3010` (FEAT-8100, MVP) cites `FR-6210` (FEAT-6200, Release 1). Fixed by moving the prerequisites earlier: FEAT-5300 → Prototype, FEAT-6200 → MVP; both have only earlier-bucketed prerequisites. | Low | None further. As with F-18, the plan reconstructs a shipped system; no move changes what is built. |
| F-24 | Verified requirements not met as built (carried from the requirements review) | FEAT-4300 (`FR-4310`, `FR-4320`); FEAT-7200 (`FR-7220`, `FR-7230`) | Requirements review R1: `FR-4310` is recorded verified (`IP-1060`/VR-1060) but the server accepts clock, step, advance, rewind and undo from any non-Observer seat. R2: `FR-7220` is recorded verified (VR-1100) but a save holds only the vignette ID and overrides. The new leaf in each Feature (`FR-4320`, `FR-7230`) is the owner decision that fixes it. | **High** (FEAT-4300) / Medium (FEAT-7200) | FEAT-4300: `07` remediation package for `FR-4310` + `FR-4320` (`BL-0307`); FS-106 v2.0 already specifies clock authority, so check at `07` whether it needs a revision for the `FR-4320` control list. FEAT-7200: `06` revision of FS-110 for `FR-7230`, stating how it also satisfies `FR-7220`. |
| F-25 | Features that grew (judgment call) | FEAT-8100 (1 FR + 6 → 11 NFRs); FEAT-9100 (+`NFR-3060`); FEAT-6100 (+`NFR-3710`) | FEAT-8100 now holds the five human-factors leaves `NFR-3010`–`NFR-3050` on top of F-07's six cross-cutting NFRs. `NFR-3060` (White Cell can see the active Red doctrine preset) went to FEAT-9100, which owns presets, rather than FEAT-4600 (god-view). `NFR-3710` (bounded work on untrusted input) went to FEAT-6100, the seam untrusted requests cross, though its three caps live in `inprocess.py` and `ephemeris.py`. | Low | Keep. If the human-factors leaves get their own specification, split them out of FEAT-8100 into a "Console Human-Factors Rules" Feature at the next `05` touch rather than growing FEAT-8100 further. |
| F-26 | Downstream gaps (next stage) | FEAT-7200, FEAT-12100, FEAT-12200, FEAT-12300; `BL-0305`, `BL-0309`, `BL-0312` | No specification yet covers `FR-7230`, `NFR-2820`/`NFR-2830`/`NFR-3840`/`NFR-1510`, `NFR-2840`, or `NFR-3800`–`NFR-3830`. `NFR-3030` (panel-manager contract) has a known gap in the Compare and Assessment panels (`BL-0305`); `NFR-1300` has no test (`BL-0309`). | Medium | `06-feature-specification`, one per run: FS-110 revision (`FR-7230`); a new FS for FEAT-12100 (marker registration and backfill); a new FS for FEAT-12200 (name the browser tooling and run mode, review R7, and decide `BL-0312`'s friction rule); FEAT-12300 after them (it rides `BL-0297`). `BL-0305`/`BL-0309` go straight to `07` as remediation. |

## Reconciling the 50–80 expectation

This catalog, decomposed strictly from the **approved** requirements baseline, lands at **36
Features** — short of the 50–80 range the audit anticipated. That gap is real, but it is not a
decomposition-granularity problem; it is an **upstream approval-status problem**, fully accounted
for by Findings F-01 and F-04:

| Source of additional Features once upstream work closes the gap | Estimated yield |
|---|---|
| **This catalog (approved FR/NFR baseline only, updated 2026-07, partially updated 2026-10-03 — see Finding F-11)** | **41** |
| DOM-002/004/005 backfilled into FR/NFR form (F-01) — **fully resolved: 2 baselined (`FR-10110`/`FR-10210`, already counted in the 38 above, via `EP-10000`), 1 Candidate Requirement remains (`CR-21`, counted in the row below)** | 0 (already counted above) |
| 19 remaining Candidate Requirements (`CR-01`–`CR-18`, `CR-21`) + 7 Candidate NFRs, once baselined by `04-requirements-engineering` where the project owner resolves each one's blocking condition (most map close to 1:1 with this catalog's grain; a few, like CR-01/CNFR-06, are one Feature not two) | ~20–22 |
| 8 Strategic Review Future Concepts with no Candidate Requirement yet (FC-01, 03, 04, 05, 07, 12, 14, 15), once run through architecture/requirements authoring | ~8–10 |
| Remaining Strategic Review Gaps with no CR/FC framing yet (GAP-01 space weather, GAP-06 attribution/messaging, GAP-07 training transfer, GAP-09 PNT warfare) | ~3–5 |
| **Total once fully baselined** | **≈69–78** |

This still lands squarely inside the 50–80 range — confirming the original audit's instinct was
correct — but the path there is narrower than first estimated: DOM-002/004/005 contributed candidate
requirements (now folded into the CR/CNFR row) rather than a clean, separate FR/NFR bloc, and two of
those three candidates are blocked on an *architecture* decision (amend or accept ADR-0017/ADR-0029),
not merely an *authorization* decision the way most of CR-01–18 are. The missing ~35–45 Features are
**not missing decomposition work**, they are **missing upstream requirements/domain/architecture
work** that this skill is explicitly not permitted to invent (per its own "SHALL NOT create new
requirements" rule). The next concrete steps, in dependency order:

1. ~~Run `04-requirements-engineering` against DOM-002/DOM-004/DOM-005 to close Finding F-01.~~ **Done**
   — see `reviews/requirements-domain-backfill-report.md`.
2. ~~Resolve the `CR-19`/`ADR-0017` and `CR-20`/`ADR-0029` conflicts.~~ **Done** — `ADR-0032`
   (narrows `ADR-0017`) and `ADR-0033` (supersedes `ADR-0029`), per direct project-owner decision;
   `CR-19`/`CR-20` promoted to `FR-10110`/`FR-10210`. `IP-2010` returned to `READY`; `IP-3010`
   remains `BLOCKED` on `IP-2010` reaching `COMPLETE` (unrelated to the now-resolved ADR conflict).
   Separately, run `04-requirements-engineering` to formally baseline (promote from Candidate to
   numbered) as many of the remaining 19 `CR-01–18,21`/7 `CNFR-01–07` as the project owner
   authorizes.
3. For the 8 Future Concepts with no Candidate Requirement yet, run `03-architecture-design-synthesis`
   first (several — FC-06, FC-09 — already have GDS-03/04 candidate-component treatment; FC-07
   cislunar and FC-15 human-machine-teaming instrumentation do not yet).
4. Re-run this `05-feature-decomposition` skill's Step 0 (inventory) incrementally against the delta,
   per this skill's own recommended-usage guidance — not a full regeneration.
5. Separately, close Finding F-03 (split FS-106) and Finding F-02 (author the three missing specs)
   regardless of the above — those are FS-xxx-authoring work items against **already-approved**
   Features already present in this catalog, and do not require any upstream requirements work.
   **Update (2026-07): Findings F-02, F-03, and F-10 are all done.** FS-106 narrowed to v2.0;
   FS-109/FS-110/FS-111 (F-03) and FS-112/FS-113/FS-114/FS-115 (F-02/F-10) authored — 15 documents
   now in `docs/features/` where 11 stood before. **Two follow-on tasks remain, neither performed by
   this authoring pass. **Update:** (a) `IMP-106A`/`IP-1060` reconciliation is now done (see F-03's
   row above). (b) Verify build status for FS-112/113/114/115 against the actual `spacesim/` source
   tree remains open — each of those four explicitly does not assume either answer, since none had
   any prior FS-corpus narrative to confirm against.
