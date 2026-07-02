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

**Reconciliation — how the 11 existing `FS-xxx` documents map onto this catalog's 36 `FEAT-xxxx` rows:**

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
| FS-201 Competency Assessment | *(none — see Finding F-01)* | Not derivable from `docs/requirements/` at all |
| FS-202 Rubric Authoring *(candidate, unauthorized)* | *(none — see Finding F-01)* | Same |
| FS-301 Research Analytics | *(none — see Finding F-01)* | Same |

**Update (2026-07): Findings F-02 and F-10 are now resolved.** FEAT-4500 (Classification Banner) →
[FS-112](../features/FS-112-classification-banner.md); FEAT-6500 (Observer Read-Only Access) →
[FS-113](../features/FS-113-observer-read-only-access.md); FEAT-6600 (Hot-Seat Hand-Off) →
[FS-114](../features/FS-114-hot-seat-handoff.md); FEAT-4100/FEAT-4200 (Vignette Selection/Seat
Assignment) → [FS-115](../features/FS-115-session-setup.md). All four are newly authored, not
split from an existing document (unlike FS-109/110/111) — each explicitly flags its own **build
status as unverified** in its Risks/Open Questions sections, since no prior FS-corpus narrative
existed to confirm against. Verifying build status against the actual `spacesim/` source tree is
the one remaining piece of both findings' remediation, not performed by this review.

## Quality-gate verification

- **Completeness:** All 49 baselined `FR-xxxx` leaves and all 23 baselined `NFR-xxxx` leaves are
  each owned by exactly one Feature in `03-feature-catalog.md` — verified by direct enumeration
  against `docs/requirements/01`/`02`'s leaf lists (49 `- **ID:** FR-` occurrences; 23 confirmed by
  `02`'s own Completion Report). No FR/NFR ID is missing; none appears twice.
- **Epic assignment:** All 36 Features appear in exactly one Epic's `Features Included` list in
  `02-epic-catalog.md` (5+5+5+7+3+6+3+1+1 = 36, matching the catalog's own Summary table).
- **Release assignment:** All 36 Features appear in exactly one bucket in `01-release-plan.md`
  (2 Prototype + 8 MVP + 21 Release 1 + 5 Release 2 + 0 Future = 36).
- **Circular dependencies:** Two found and resolved with stated rationale, not silently broken —
  see `04-feature-dependency-graph.md`'s "Circular dependencies found" section and Finding F-05
  below.
- **Candidate/non-baselined items:** 18 Candidate Requirements, 7 Candidate NFRs, 15 Strategic
  Review Future Concepts, and 13 Strategic Review Gaps are deliberately **excluded** from every
  Feature's `Included Requirements` — they are not approved, so this skill does not group them
  (see Finding F-04).

## Findings

| # | Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| F-01 | Architectural inconsistency / requirements-baseline gap | FS-201, FS-202, FS-301, DOM-002, DOM-004, DOM-005 | Three existing Feature Specifications (Competency Assessment, Rubric Authoring, Research Analytics) are grounded directly in Domain documents (DOM-002/004/005) but have **no corresponding FR-xxxx/NFR-xxxx leaf anywhere in `docs/requirements/`**. This Feature Catalog decomposes `docs/requirements/` exhaustively and correctly produces zero Features for assessment/research/validation capability — the gap is upstream, in the requirements baseline itself, not in this decomposition. | High | Run `requirements-engineering` against DOM-002/004/005 to backfill FR/NFR leaves for competency-assessment, rubric-computation, cohort-export, and validation-methodology capabilities before this catalog can represent them. Estimated yield: roughly 6–9 additional Features at this catalog's grain. |
| F-02 | Missing Feature Specification — **RESOLVED 2026-07** | FEAT-4500 → FS-112, FEAT-6500 → FS-113, FEAT-6600 → FS-114 | Classification Banner, Observer Read-Only Access, and Hot-Seat Hand-Off Screen-Blank Menu each had a real, Must-priority baselined FR (FR-4510, FR-6510, FR-6610), but **zero presence in any of the 11 existing `FS-xxx` documents** and an `UNASSIGNED` Impl. Package citation in the RTM. This confirmed the original audit finding verbatim. | High | **Done:** FS-112/FS-113/FS-114 authored directly from the requirements baseline (no prior narrative to draw on). **Not yet done:** build-status verification against `ui_web/static/`, `session/`, and `session/aar.py` export paths — each new document flags this as its own top Open Question. |
| F-03 | Feature too large (existing FS, not this catalog) — **RESOLVED 2026-07** | FS-106-white-cell-dashboard.md → FS-106 v2.0, FS-109, FS-110, FS-111 | The existing FS-106 document bundled **ten** of this catalog's 36 Features across **three different Epics** (EP-4000 White Cell Control, EP-6000 Multiplayer Transport, EP-7000 Save/Resume, EP-9000 AI-Red) — including two capabilities (multiplayer clock/locking, AI-Red) that each carry their own dedicated ADRs (ADR-0014/0026 for multiplayer; ADR-0021/0024/0030 for AI-Red) and their own source module (`session/inprocess.py`; `session/redai.py`). This was the single largest cohesion violation found. | High | **Done:** FS-106 narrowed to v2.0 (White Cell control-plane proper: clock-authority trigger/god-view/injects/adjudication); FS-109 (Multiplayer/LAN Transport, FEAT-6300/6400); FS-110 (Save/Resume, FEAT-7200); FS-111 (AI-Red, FEAT-9100) authored. **`IMP-106A`/`IP-1060` reconciliation is also done:** IP-1060 narrowed to v2.0; IP-1090/IP-1100/IP-1110 authored (reorganizing IP-1060 v1.0's already-verified code citations, no new verification performed); `00-master-build-plan.md`'s package table/dependency graph/summary stats updated; `IMP-106A` (frozen, superseded) gained a forward-pointer note only. |
| F-04 | Missing Features (not yet approved — informational, not a defect) | CR-01–18, CNFR-01–07, FC-01–15, GAP-01–13 | The 18 Candidate Requirements, 7 Candidate NFRs, and the July-2026 Strategic Review's 15 Future Concepts / 13 Gaps are **correctly excluded** from this catalog per this skill's own constraint (only approved/baselined requirements are decomposed). Substantial overlap exists between these sets (e.g. FC-02/GAP-08 = CR-01/CNFR-06; FC-06/GAP-10 = CR-12; FC-09 = CR-13; FC-10/GAP-03 = CR-14; FC-13 = CR-15; FC-11/GAP-12 = CR-16; FC-08/GAP-02 = CR-17), so the unique count of not-yet-approved capability concepts is roughly **25 CR/CNFR-tier items + 8 FC items with no CR yet (FC-01, FC-03, FC-04, FC-05, FC-07, FC-12, FC-14, FC-15) + a handful of GAP-only research topics (GAP-01, GAP-06, GAP-07, GAP-09) that don't yet even have a candidate-requirement framing** — see the reconciliation arithmetic below. | Medium (informational) | This is the primary source of the gap between this catalog's 36 Features and the user's expected 50–80 — see "Reconciling the 50–80 expectation" below. Not resolved by this catalog; requires `requirements-engineering` (to baseline the CR/CNFR tier) and possibly `architecture-design-synthesis` first (for the FC items with no CR yet). |
| F-05 | Architectural inconsistency (source requirements document) | FR-1110, FR-4310, FR-1120, FR-7110 | Two 2-node circular dependency citations exist in `docs/requirements/01-functional-requirements.md`'s own `Dependencies` fields (FEAT-1100↔FEAT-4300; FEAT-1100↔FEAT-7100), both from the same root cause: a leaf FR citing a sibling *category* ID rather than the specific leaf inside it. Resolved for this graph with stated rationale (see `04-feature-dependency-graph.md`); not silently fixed. | Medium | The requirements owner may want to tighten FR-1110's and FR-1120's `Dependencies` fields to cite the specific leaf (FR-4310, FR-7110) rather than the category header, which would make the intended direction unambiguous without changing meaning. |
| F-06 | Requirements traceability gap (pre-existing, confirmed independently) | 13 of 49 FR leaves | FR-1130, FR-3310, FR-3510, FR-3520, FR-4110, FR-4210, FR-4510, FR-4610, FR-4710, FR-4720, FR-6510, FR-6610, FR-7220 all show `UNASSIGNED` in the RTM's own Impl. Package column (≈27% of the baseline). Most (all except FR-4510/FR-6510/FR-6610, per Finding F-02) are narratively described as shipped in an existing `FS-xxx` document despite the missing citation — a documentation-hygiene gap, not necessarily a build gap. | Medium | A dedicated traceability-verification pass (grep the actual `spacesim/` source tree per FR, as the RTM's own stated method describes) would close most of this without new development. |
| F-07 | Feature possibly too large (judgment call, not a defect) | FEAT-8100, FEAT-1100 | FEAT-8100 (Browser Console) bundles 1 FR with 6 cross-cutting NFRs (performance, hardware floor, config, portability, accessibility, external-integration boundary); FEAT-1100 bundles 3 FR with 5 NFRs (determinism, sub-stepping, maintainability, data-integrity, test-gating). Both were deliberately bundled here (stated in each Feature's own Description) rather than distributing each NFR to every Feature it touches, to avoid restating the same cross-cutting quality attribute 6–8 times across the catalog. A stricter reviewer could reasonably prefer the distributed alternative. | Low | Acceptable as designed; flagged for awareness, not required to change. |
| F-08 | Feature possibly too small (judgment call, not a defect) | FEAT-1300 | Impulsive Maneuver & Δv Budget Accounting owns exactly one FR (FR-1310) and cites no ADR of its own ("none directly — restates a GDS-04 validation rule"). A stricter reviewer could merge it into FEAT-1200 (Orbital Propagation & Access-Window Geometry) as a sub-capability rather than a standalone Feature. | Low | Kept standalone here because Δv is independently named as "the operator's hardest constraint" (a distinct user-facing training objective) and has its own dedicated design document (`design/14-delta-v-economy.md`) — but this is a closer call than the catalog's other single-FR Features (e.g. FEAT-9100 AI-Red, which has three dedicated ADRs). |
| F-09 | Architectural inconsistency (deliberate, disclosed) | EP-9000 | EP-9000 (AI-Red) is a single-Feature Epic, which the Best Practices guidance generally discourages ("an Epic that exists to hold exactly one Feature is a sign the Epic layer added no organizing value"). Kept as its own Epic here specifically because of its outsized strategic weight (the Strategic Review's #1 tracked gap, FC-02/GAP-08) despite module-wise fitting naturally under EP-3000 (Command Planning) or EP-4000 (White Cell). | Low | Disclosed rather than hidden; a reviewer who weighs strict subsystem-alignment over strategic signaling could reasonably fold EP-9000 into EP-3000. |
| F-10 | Missing Feature Specification (found during F-03's remediation) — **RESOLVED 2026-07** | FEAT-4100, FEAT-4200 → FS-115 | While splitting FS-106 (Finding F-03), a close read of FS-106 v1.0's actual User Workflows (not just this catalog's earlier mapping guess) confirmed it never covered vignette selection/parameter tuning (FR-4110) or seat-to-role assignment (FR-4210) at all — these session-setup capabilities had **zero presence in any existing `FS-xxx` document**, matching the pattern of F-02's three findings exactly. | High | **Done:** FS-115 authored, folding FEAT-4100/FEAT-4200 into one "Session Setup" document since both are Must-priority, sequential, White-Cell-only setup-phase steps with a direct Feature Catalog dependency edge between them. **Not yet done:** build-status verification, same as F-02. |

## Reconciling the 50–80 expectation

This catalog, decomposed strictly from the **approved** requirements baseline, lands at **36
Features** — short of the 50–80 range the audit anticipated. That gap is real, but it is not a
decomposition-granularity problem; it is an **upstream approval-status problem**, fully accounted
for by Findings F-01 and F-04:

| Source of additional Features once upstream work closes the gap | Estimated yield |
|---|---|
| **This catalog (approved FR/NFR baseline only)** | **36** |
| DOM-002/004/005 backfilled into FR/NFR form (F-01) — competency assessment, rubric authoring, research analytics, validation methodology | ~6–9 |
| 18 Candidate Requirements + 7 Candidate NFRs, once baselined by `requirements-engineering` (most map close to 1:1 with this catalog's grain; a few, like CR-01/CNFR-06, are one Feature not two) | ~20–22 |
| 8 Strategic Review Future Concepts with no Candidate Requirement yet (FC-01, 03, 04, 05, 07, 12, 14, 15), once run through architecture/requirements authoring | ~8–10 |
| Remaining Strategic Review Gaps with no CR/FC framing yet (GAP-01 space weather, GAP-06 attribution/messaging, GAP-07 training transfer, GAP-09 PNT warfare) | ~3–5 |
| **Total once fully baselined** | **≈73–82** |

This lands squarely inside the 50–80 range — confirming the original audit's instinct was correct,
but the missing ~40 Features are **not missing decomposition work**, they are **missing upstream
requirements/domain authoring** that this skill is explicitly not permitted to invent (per its own
"SHALL NOT create new requirements" rule). The next concrete steps, in dependency order:

1. Run `requirements-engineering` against DOM-002/DOM-004/DOM-005 to close Finding F-01.
2. Run `requirements-engineering` to formally baseline (promote from Candidate to numbered) as many
   of CR-01–18/CNFR-01–07 as the project owner authorizes.
3. For the 8 Future Concepts with no Candidate Requirement yet, run `architecture-design-synthesis`
   first (several — FC-06, FC-09 — already have GDS-03/04 candidate-component treatment; FC-07
   cislunar and FC-15 human-machine-teaming instrumentation do not yet).
4. Re-run this `feature-decomposition` skill's Step 0 (inventory) incrementally against the delta,
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
