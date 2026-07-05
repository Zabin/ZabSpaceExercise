# Requirements Update Report — FS-117 (Vignette Creator) coverage pass

> **Status:** Complete — nine new baselined requirement leaves added and reviewed.
> **Source:** [`docs/pipeline/backlog.md`](../pipeline/backlog.md) `BL-0055` (Critical finding from
> `06-feature-specification`'s `FS-117` run): most of `FS-117` (Vignette Creator)'s
> architecture-committed scope had no owning `FR-xxxx`/`NFR-xxxx` anywhere in the baseline. The
> project owner explicitly chose to run `04-requirements-engineering` now rather than split
> delivery.
> **Scope:** `docs/requirements/01-functional-requirements.md`,
> `docs/requirements/02-non-functional-requirements.md`,
> `docs/requirements/03-requirements-traceability-matrix.md`. Read in full as inputs before this
> pass: [`FS-117`](../features/FS-117-vignette-creator.md),
> [`ADS-5100A`](../architecture/ADS-5100A-vignette-creator-session-and-ui.md),
> [`ADS-5100B`](../architecture/ADS-5100B-typed-parameters-and-per-cell-roe.md),
> [`R101`](../research/encyclopedia/R101-orbital-mechanics-for-operations.md),
> [`R107`](../research/encyclopedia/R107-ground-segment-operations.md),
> [`R109`](../research/encyclopedia/R109-sensor-operations.md),
> [`R110`](../research/encyclopedia/R110-communications.md),
> [`R111`](../research/encyclopedia/R111-power-and-thermal-operations.md),
> [`R112`](../research/encyclopedia/R112-propulsion-and-maneuver-planning.md),
> [`R134`](../research/encyclopedia/R134-pnt-warfare-and-navigation-denial-operations.md),
> [`R137`](../research/encyclopedia/R137-bus-and-payload-parameter-catalog.md).
> **No architecture was redesigned.** `ADS-5100A`/`ADS-5100B` and `GDS-04` are read as fixed inputs;
> nothing in `docs/architecture/` was edited to produce this report. **`GDS-05` (the
> architecture-ladder's own authoritative Functional Requirements level) was not updated in this
> pass** — see Finding 9 below, a genuine reconciliation gap this report surfaces rather than
> silently closes.

[↑ Docs index](../INDEX.md) · [FS-117](../features/FS-117-vignette-creator.md)

---

## 1. Bottom line

**Nine new baselined requirement leaves added:** `FR-5120`, `FR-5130`, `FR-5140`, `FR-5150`,
`FR-5160` (all new children under `FR-5100`'s existing parent), `FR-5170`, `FR-5180` (same),
`FR-3420` (a new child under `FR-3400`'s existing parent), and `NFR-2010`. Every one traces to a
specific section of `ADS-5100A`/`ADS-5100B` (or, for `FR-5140`/`FR-5170`/`FR-5180`, the underlying
R1xx research those documents themselves cite) — no invented number, no requirement written from
general software-engineering convention. `FS-117`'s Critical Open Question 1 is now closeable: a
follow-up `06-feature-specification` touch should update `FS-117`'s own `Requirements Implemented`
field to cite these nine IDs alongside `FR-5110`/`NFR-2000`.

**No existing `Candidate Requirement` matched this scope closely enough to promote.** `CR-13`
(Coalition / Multi-Cell Generalization) was checked directly and is the closest near-miss, but it
covers generalizing fog-of-war/ROE to *more than two* cells with releasability tiers — a
structurally different problem from making the *existing* two cells' (Blue/Red) ROE independent of
each other, which is what `FR-3420` requires. No promotion was made; `FR-3420` is a genuinely new
leaf, not a `CR-13` graduation.

## 2. New requirements added (summary — full text in `01-functional-requirements.md`/`02-non-functional-requirements.md`)

| ID | Title | Parent | Source |
|---|---|---|---|
| `FR-5120` | Synchronized JSON view of the in-progress vignette | `FR-5100` | `ADS-5100A` §2, §8 Risk 1 |
| `FR-5130` | 2D/3D initial-state preview | `FR-5100` | `ADS-5100A` §2, §6; `ADR-0004` |
| `FR-5140` | TLE and lat/long asset entry | `FR-5100` | `ADS-5100A` §2, §5; `R101`; `R107` |
| `FR-5150` | Asset menu (edit, reassign, delete) | `FR-5100` | `ADS-5100A` §2 |
| `FR-5160` | Seat-count declaration and seat/role-assignment matrix | `FR-5100` | `ADS-5100A` §2, §4; `BL-0051` |
| `FR-5170` | Typed per-payload-type parameter sub-schemas | `FR-5100` | `ADS-5100B` §3.1; `R109`, `R110`, `R134`, `R137` |
| `FR-5180` | Typed bus parameter sub-schemas (power, propulsion) | `FR-5100` | `ADS-5100B` §3.1; `R111`, `R112` |
| `FR-3420` | Per-cell independent Rules of Engagement | `FR-3400` | `ADS-5100B` §3.2, §10 Decision Log 3 |
| `NFR-2010` | Additive vignette-schema evolution | (new, sibling of `NFR-2000`) | `ADS-5100B` §6 |

## 3. Review findings (Step 3)

| # | Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| 1 | Missing requirement (now closed) | `FR-5120`–`FR-5180`, `FR-3420`, `NFR-2010` | The gap `BL-0055` named. | Critical (resolved) | Closed by this pass — no further action. |
| 2 | Dependency completeness | `FR-5170`, `FR-5180` | Both depend on `FR-5140`/`FR-5150` (an asset must exist before its typed parameters can be authored) — confirmed consistent, no missing dependency edge. | None | No action. |
| 3 | Architectural-fit check | `FR-5170` (`weather`/`mw` sub-schemas) | `FR-5170`'s own Postcondition explicitly states these two sub-schemas have no observable engine effect until `docs/pipeline/backlog.md` `BL-0053` (the `BEAM_MODES` gap) closes — checked against `ADS-5100B` §3.1/§7, consistent, not silently smoothed over. | Low (informational — already disclosed in the requirement itself) | No action; `07-implementation-planning` should sequence `BL-0053` before or alongside whichever package builds `FR-5170`'s weather/mw half. |
| 4 | Verification credibility | All nine new leaves | Every Acceptance Criterion is Test-verifiable against a running system or a specific file field (e.g. `FR-5180`'s "maps to `charge_rate_per_s`, never `power_w`") — none relies on Inspection/Analysis without justification. | None | No action. |
| 5 | Duplicate check | `FR-3420` vs. `FR-3410` | `FR-3410` already requires ROE re-validation as one of five execute-time checks; `FR-3420` does not duplicate this — it specifies that ROE resolution must be *per-cell*, a refinement of how `FR-3410`'s existing ROE check resolves, not a second, competing check. Confirmed no overlap in what each requirement's own Acceptance Criteria test. | None | No action; kept as a distinct leaf under `FR-3400`, cross-referenced in both directions. |
| 6 | Conflict check | `FR-3420` vs. all 19 shipped vignettes | `FR-3420`'s own Postcondition requires identical behavior for a vignette declaring only the legacy global ROE pair — checked against `engine/orders.py`'s current behavior directly (`self.roe.get(...)`, no `order.cell` reference today); the requirement is written to be additive, not a breaking change. | None | No action — `NFR-2010` exists specifically to make this obligation explicit and testable across the whole feature, not just this one requirement. |
| 7 | Traceability completeness | `FR-5130` | Cites `ADR-0004` (fog-of-war-at-the-boundary) as a *consistency* requirement (ground-truth preview follows the existing pattern), not as the pattern's origin — `ADR-0004`'s own decision text is scoped to cell-level fog-of-war specifically (a fact `ADS-3500`'s own Risks section already flagged for a different Feature). Citing it here as "consistent with," not "governed by," avoids repeating that same imprecision. | Low | No action needed; phrasing already correct in `FR-5130`'s own Rationale field. |
| 8 | Interface gap | `FR-5170`, `FR-5180` | Neither requirement cites an ICD interface ID — correctly, since both are Domain Model/content-schema extensions with no new interface, consistent with `ADS-5100B`'s own System Architecture section naming no new interface either. | None | No action; `Related Interfaces` fields correctly state "(none directly)" rather than forcing a citation. |
| 9 | **Reconciliation gap (new, this pass)** | `GDS-05` vs. `docs/requirements/01-functional-requirements.md` | `docs/architecture/05-functional-requirements.md` (GDS-05) is this project's stated architecture-ladder-authoritative FR source (`CLAUDE.md` reading order); this pass added nine leaves to `docs/requirements/01` (the "elaborated in full traceability detail" downstream document) without a corresponding `GDS-05` update, since editing `GDS-05` is `03-architecture-design-synthesis`'s scope, not this skill's. This mirrors the exact situation this skill's own Gotchas section warns about ("a project that already has its own GDS/ADS-style architecture ladder... check whether those sections are meant to be the authoritative input"). Not resolved here — named explicitly rather than silently left as an undetected drift. | Medium | A future `03-architecture-design-synthesis` maintenance touch to `GDS-05` should fold these nine leaves in, the same way `GDS-05`'s merge gate already absorbed `build-spec/02` §5–6's content. Filed to the pipeline backlog for tracking. |

No Critical or High findings remain open — Finding 1 (the originating gap) is resolved by this
pass's own content; Finding 9 (Medium) is a real but non-blocking documentation-reconciliation gap.

## 4. What this pass explicitly did not do

- Did not modify `FS-117`, `ADS-5100A`, or `ADS-5100B` — those remain this skill's read-only inputs.
- Did not promote any existing Candidate Requirement into the numbered baseline.
- Did not invent a number, target, or acceptance figure not already stated by `ADS-5100A`/`ADS-5100B`
  or the R1xx research they cite.
- Did not update `docs/architecture/05-functional-requirements.md` (GDS-05) — Finding 9 names this
  as a follow-up for the architecture owner, not something folded in here.

## Related

[`docs/features/FS-117-vignette-creator.md`](../features/FS-117-vignette-creator.md) ·
[`docs/architecture/ADS-5100A-vignette-creator-session-and-ui.md`](../architecture/ADS-5100A-vignette-creator-session-and-ui.md) ·
[`docs/architecture/ADS-5100B-typed-parameters-and-per-cell-roe.md`](../architecture/ADS-5100B-typed-parameters-and-per-cell-roe.md) ·
[`docs/pipeline/backlog.md`](../pipeline/backlog.md) `BL-0055`
