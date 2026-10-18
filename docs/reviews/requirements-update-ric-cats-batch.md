# Requirements Update Report — RIC-view / CATS-angle / TLE-export / controller-view intake batch (2026-10-03)

> **Status:** Complete — seven new baselined requirement leaves added (all FR, no new NFR) and
> reviewed. Six are `Should` priority; two (`FR-4450`, `FR-4620`) are `Could` priority, matching
> their source backlog row's own Could-tier disposition.
> **Source:** `docs/pipeline/backlog.md` — `BL-0107` (live, operator-selectable RIC/RSW
> relative-motion frame view, filed live this session), `BL-0109` (quick TLE export for a
> cell-visible satellite), `BL-0111` (CATS illumination-phase-angle overlay, extends `BL-0107`),
> `BL-0122` (CATS angle as an access-window criterion for any passive EO sensor), and `BL-0079`
> (Could-tier controller view with side-by-side per-cell truth and an editable pending-inject
> queue) — all five scheduled together by the pipeline manager's run #77/#78 triage to ride the
> same `04-requirements-engineering` pass. `BL-0113` (a design-question on `FR-1620`'s rejection-
> reason distinguishability, also routed to `04` but for a different, already-`IN PIPELINE`
> feature family, `FS-122`) was explicitly excluded from this pass's scope per the run's own
> target — it remains `SCHEDULED`, unchanged, for a future `04` pass.
> **Scope:** `docs/requirements/01-functional-requirements.md`,
> `docs/requirements/02-non-functional-requirements.md` (read in full; no NFR added or modified —
> see §2 below), `docs/requirements/03-requirements-traceability-matrix.md`. Read in full as
> inputs before this pass: `docs/pipeline/backlog.md` (the five source rows plus their companion
> research-gap/design-question rows `BL-0108`, `BL-0110`, `BL-0112`), `docs/architecture/04-domain-
> model.md` (GDS-04), `docs/design/05-interface-control-document.md` (ICD, INT-0001–0016),
> `docs/architecture/adr/INDEX.md` (ADR-0001–0035), the existing sibling leaves each new leaf was
> added alongside (`FR-1600`, `FR-4400`, `FR-4600`, `FR-7400`, `FR-8100` families), `engine/
> maneuver.py::lvlh_frame`, `session/ephemeris.py::to_ric()`, `engine/sun.py`
> (`sun_unit_eci`/`is_sunlit`/`eclipse_fraction`), `docs/research/encyclopedia/R101-orbital-
> mechanics-for-operations.md`, `R109-sensor-operations.md` §3.7, and `R112-propulsion-and-
> maneuver-planning.md` (grepped for `RIC`/`RSW`/`LVLH` — confirmed `R101` has zero matches and
> `R112` mentions `lvlh` only as a maneuver-entry-mode parameterization, corroborating `BL-0108`'s
> own research-gap finding firsthand rather than taking it on faith).
> **No architecture was redesigned.** GDS-03/GDS-04 and the ICD are read as fixed inputs; nothing
> in `docs/architecture/` was edited to produce this report.
> **No research pass was run first.** `BL-0108` (RIC-display research-gap) and `BL-0112` (CATS-
> angle research-gap) both carry an explicit `DEFERRED` disposition whose revisit trigger is
> "before `06-feature-specification` drafts/designs" the relevant leaf — not before this `04` pass.
> Both leaves this report baselines on that basis cite the existing transform-math/sunlit grounding
> plus the backlog's own single-source anchors (for `BL-0112`, the AGI/STK citation), and flag the
> open research gap honestly in their own Notes fields rather than treating it as resolved.

[↑ Docs index](../INDEX.md) · [Backlog](../pipeline/backlog.md)

---

## 1. Bottom line

**Seven new baselined requirement leaves added:**

- `FR-8210`, `FR-8220` (two leaves, new parent `FR-8200`, under `FR-8000`) — `BL-0107` (the live,
  operator-selectable RIC-frame view) and `BL-0111` (its CATS-angle overlay, extending `FR-8210`
  rather than standing alone, per `BL-0111`'s own stated relationship).
- `FR-7440` (new child under `FR-7400`'s existing parent) — `BL-0109`, quick TLE export for a
  cell-visible satellite.
- `FR-1670` (new child under `FR-1600`'s existing parent) — `BL-0122`, CATS-angle-based
  access-window refinement for any passive EO sensor, broader than `FR-8220`'s display-only use.
- `FR-4450` (new child under `FR-4400`'s existing parent) and `FR-4620` (new child under
  `FR-4600`'s existing parent) — `BL-0079`, split per this skill's atomicity rule into the editable
  pending-inject-queue capability and the side-by-side controller-view capability the single
  backlog row bundled together.

Every leaf traces to its backlog row plus, where the capability reuses existing engine machinery,
the specific code/requirement it reuses (`engine/maneuver.py::lvlh_frame`/`session/ephemeris.py::
to_ric()` for `FR-8210`; `engine/sun.py` for `FR-8220`'s distinction from existing sunlit/eclipse
machinery; `FR-6210`/`FR-6220` for every leaf's fog-of-war posture). No invented capability was
added beyond what the five backlog rows state.

**No NFR was added.** `FR-8210`'s live-update behavior is already covered by the existing
`NFR-1100` ("Responsive UI at high time-multipliers") and `NFR-1900` ("UI-agnostic engine with
enforced test coverage") — a new leaf restating an already-covered quality attribute is not a gap.
No other item in this batch implies a quality attribute the existing NFR baseline doesn't already
cover (checked against all sixteen NFR categories in
[`02-non-functional-requirements.md`](../requirements/02-non-functional-requirements.md), the same
discipline the Should-tier batch report applied).

## 2. New requirements added (summary — full text in `01-functional-requirements.md`)

| ID | Title | Parent | Priority | Source |
|---|---|---|---|---|
| `FR-1670` | Phase-angle (CATS) access-window refinement for passive EO sensors | `FR-1600` | Should | `BL-0122`; `BL-0112` (AGI/STK citation); `FR-1620` |
| `FR-4450` | Edit or cancel a scheduled inject before it fires | `FR-4400` | Could | `BL-0079`/B13 |
| `FR-4620` | Side-by-side controller view: each cell's picture beside truth | `FR-4600` | Could | `BL-0079`/B13; `FR-4610` |
| `FR-7440` | Quick TLE export for a cell-visible satellite | `FR-7400` | Should | `BL-0109`; `BL-0110` (design-question) |
| `FR-8210` | Live, operator-selectable RIC-frame relative-motion view | `FR-8200` (new) | Should | `BL-0107`; `FR-7410`/`FR-7420`/`FR-7430`; `BL-0108` (research-gap) |
| `FR-8220` | CATS illumination-phase-angle overlay for the RIC view's selected chase satellite | `FR-8200` (new) | Should | `BL-0111`; `BL-0112` (research-gap) |

(`FR-8200` is a new grouping parent under the existing `FR-8000 — Operator Console Presentation`
top-level capability, alongside `FR-8100`.)

## 3. Review findings

Per this skill's mandatory Step 3 review dimensions:

| # | Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| 1 | Duplicates | None found | Each of the six leaves covers a distinct observable behavior; `FR-8210`/`FR-8220` are deliberately layered (a view and its overlay) rather than duplicating one another, and `FR-4450`/`FR-4620` are deliberately split from one backlog row rather than merged into a single non-atomic leaf. | — | No action. |
| 2 | Conflicts | `FR-8210` vs. `FR-6210`/`FR-6220` (fog-of-war boundary) | None found. `FR-8210`'s cell-scoped rendering explicitly inherits `FR-6210`'s filtering rule (never ground truth, never another cell's belief), and its White-Cell/no-cell path explicitly rides the existing `FR-4610` god-view mechanism rather than opening a new unfiltered route — consistent with `ADR-0004`/`ADR-0015`'s existing trust-boundary posture. | — | No action. |
| 3 | Conflicts | `FR-7440` vs. `FR-6220` (no-cell ground-truth exception) | None found. `FR-7440`'s cell-scoped path is fog-of-war-filtered like every other cell-scoped route; its White-Cell/no-cell path reuses `FR-6220`'s already-named exception rather than adding a new one. | — | No action. |
| 4 | Conflicts | `FR-1670` vs. `FR-1620` (existing exclusion-angle predicate) | None found. `FR-1670` is explicitly written to compose with, not replace, `FR-1220`/`FR-1620` — a sensor with no declared phase-angle range is unaffected, matching `FR-1620`'s own non-default-opt-in pattern. | — | No action. |
| 5 | Ambiguities | `FR-1670`/`FR-8220` — concrete default phase-angle range/degradation curve | Neither the backlog rows nor the one AGI/STK citation `BL-0112` found specifies a concrete numeric default usable-phase-angle range or a shape for the effectiveness-degradation curve — only that the concept is real and operationally used. This is a design-level choice this pass deliberately does not make. | Low | Flag as an Open Question for `06-feature-specification` to resolve once `BL-0112`'s fuller research grounding lands (per `BL-0112`'s own disposition) — do not invent a specific range/curve here. |
| 6 | Ambiguities | `FR-8210` — no R1xx grounding for RIC-frame *display* as an operational concept | `BL-0108`'s finding, independently re-confirmed this pass by grepping `R101`/`R112` directly (zero `RIC`/`RSW` matches in `R101`; `R112` mentions `lvlh` only as a maneuver-entry-mode parameterization). `FR-8210` is baselined on the existing *transform-math* grounding (which is solid — `to_ric()`/`lvlh_frame()` are already implemented and tested via `FR-7410`/`FR-7420`/`FR-7430`), not on any operational-display-convention grounding, which genuinely does not yet exist in this project's research corpus. | Low | No requirements-baseline action needed — `BL-0108`'s own disposition correctly defers this to before `06-feature-specification` drafts `FR-8210`'s design, not before baselining. Flagged in `FR-8210`'s own Notes field so the gap is visible to whoever drafts that Feature Spec. |
| 7 | Shared-computation consistency note (not a defect, a heads-up) | `FR-8220` (display-only CATS overlay) vs. `FR-1670` (CATS-angle access-gating) | Both new leaves compute the same underlying Sun-target-observer phase angle for two different purposes (a live readout vs. an access-window predicate). Neither leaf invents a competing formula, and both are independently satisfiable as written, but a future implementation should use one shared phase-angle computation function, not two independently implemented ones that could drift apart — the same shape of finding the Should-tier batch report raised for `FR-3430`/`FR-1450`'s shared effect-classification taxonomy. | Low | Flag for whoever drafts the Feature Spec(s) for `BL-0111`/`BL-0122` to confirm both consume one shared phase-angle function. |
| 8 | Shared-scope split note (not a defect, a heads-up) | `FR-4450` vs. `FR-4620` (both from `BL-0079`) | `BL-0079`'s own backlog row requests both capabilities together ("a controller view showing each cell's picture beside truth and the pending inject queue with edit/cancel"). Per this skill's atomicity rule they are baselined as two independent leaves: a side-by-side view could exist without inject editing, and inject editing could exist without a side-by-side view. Each leaf's own Notes/Rationale field states this split explicitly so a reader does not mistake it for scope creep or scope loss. | — | No action — this is the correct atomicity outcome, recorded for audit-trail clarity. |
| 9 | Missing requirements | None found | Every capability named in the five backlog rows (the RIC view, its CATS overlay, the TLE export, the CATS access criterion, and both halves of the controller-view request) has at least one FR. | — | No action. |
| 10 | Impossible requirements | None found | All six leaves are physically and logically satisfiable given the existing engine architecture (`engine/maneuver.py::lvlh_frame`, `session/ephemeris.py::to_ric()`, `engine/sun.py`, `engine/access.py`, `session/cells.py`). `FR-7440`'s Acceptance Criteria are satisfiable by any of `BL-0110`'s three named implementation options, so the requirement itself (as opposed to one specific implementation shape) is not impossible. | — | No action. |
| 11 | Requirements that violate architecture | `FR-8210` vs. `ADR-0004` (fog-of-war at the boundary) | None found. `FR-8210`'s cell-scoped path reads through the existing `CellController`/`SessionAPI` boundary (`FR-6210`), not a new direct-engine-read path — consistent with `ADR-0004`'s requirement that filtering live at that boundary, not in the UI. | — | No action. |
| 12 | Requirements lacking verification | None found among the six new leaves | Every new leaf's Acceptance Criteria is checkable by a reviewer with no other context beyond the leaf and its cited sources. | — | No action. |
| 13 | Requirements lacking traceability | None found | Every new leaf cites its specific backlog row plus at least one real source-code location, existing FR, or research-gap/design-question row — no leaf relies on "implied by the architecture" or an uncited claim. | — | No action. |
| 14 | Interface-model note (not a new finding, a cross-reference) | `FR-8210` vs. `INT-0001`/`INT-0006`/`INT-0007` | `FR-8210` is the first requirement to cite all three of these interfaces together for one capability (a live, interactive view that is also fog-of-war-filtered). This is a normal composite use of existing interfaces, not a stretched shape like `INT-0014`'s prior `BL-0093` finding — no new ICD issue is raised. | — | No action. |

## 4. Candidate Requirements check

Checked all existing Candidate Requirements (`CR-01` through `CR-21` in
`01-functional-requirements.md`'s Candidate Requirements section) against this batch's five
backlog items. Grepped the full Candidate Requirements section for `RIC`, `RSW`, `relative
motion`, `CATS`, `phase angle`, `TLE`, and `controller view` — zero matches. No existing Candidate
overlaps this batch's scope; all six leaves are genuinely new baselined requirements, not
promotions of an existing Candidate.

## 5. Traceability matrix

`docs/requirements/03-requirements-traceability-matrix.md` gained six new master-matrix rows (one
per new leaf), each with `Future Feature`/`Test`/`Impl. Package` columns honestly `UNASSIGNED` (no
`FS-xxx`/`IP-xxxx` exists yet for any of these five backlog items, and no test exists yet). No row
carries a populated Research column — `BL-0108`/`BL-0112`'s research gaps remain open (per their
own `DEFERRED` disposition), so, consistent with this matrix's own stated discipline against
inferring a Research cell with no explicit citation, `FR-8210`/`FR-8220`/`FR-1670` cite only
backlog rows, existing FR leaves, and named engine-code locations in their own Source Documents —
none of which is an `R1xx`-style encyclopedia topic ID, so the Research column is correctly
`UNASSIGNED` rather than populated with a plausible-looking but uncited ID. `Arch. Component` and
`Interface` cells are filled from the existing GDS-03/ICD component legend (`C1`–`C12`,
`INT-0001`–`INT-0016`) per each leaf's own Related Interfaces field — no new component or
interface ID was invented. The ADR, Interface, and Architecture-Component reverse-index appendix
tables were also updated to list the six new leaves alongside their existing citers.

## 6. What this report does not do

- It does not resolve Finding 5's design ambiguity (the concrete phase-angle default/degradation
  curve) or Finding 7's shared-computation consistency note — both are routed to whoever drafts
  the eventual Feature Spec(s) for `BL-0111`/`BL-0122`, not decided here.
- It does not run `02-research-ow-orbital-mechanics` to close `BL-0108` or `BL-0112` — both
  remain `DEFERRED`, correctly, per their own revisit triggers (before `06-feature-specification`,
  not before this `04` pass).
- It does not resolve `BL-0110`'s design question (which current-epoch-TLE-generation option
  `FR-7440` should use) — that is explicitly a `06`/`07`-level design decision per `BL-0110`'s own
  disposition.
- It does not touch `BL-0113` (the `FR-1620` rejection-reason design-question) — a different
  feature family (`FS-122`, already `IN PIPELINE` at stage `08`), explicitly out of this pass's
  scope.
- It does not touch GDS-05 (the architecture-ladder's own Functional Requirements level) — the
  same pre-existing, left-open reconciliation gap every prior intake-batch report has named.

## Next

Per this skill's mandatory completion summary, restated here for the review report's own record:
**Recommendations** — resolve Finding 5 (concrete phase-angle default/degradation curve) and
Finding 7 (shared phase-angle computation) when `06-feature-specification` drafts Feature Specs
for `BL-0111`/`BL-0122`; no action needed on Finding 6 beyond `BL-0108`'s own already-recorded
disposition. **Next step** — return to `00-pipeline-manager` to harvest this run's findings into
the backlog and flip `BL-0107`/`BL-0109`/`BL-0111`/`BL-0122`/`BL-0079` from `SCHEDULED` to their
post-`04` disposition, then advance to `05-feature-decomposition` for the newly baselined
`FR-8210`/`FR-8220`/`FR-7440`/`FR-1670`/`FR-4450`/`FR-4620` leaves.
