# Requirements Update Report — Should-tier external-validation-report intake batch (2026-09-27)

> **Status:** Complete — thirteen new baselined requirement leaves added (all FR, no new NFR) and
> reviewed. All thirteen are `Should` priority, matching the source backlog rows' own priority tag.
> **Source:** External user validation report, 26 Sep 2026 (baseline `32ca02a`), filed to
> [`docs/pipeline/backlog.md`](../pipeline/backlog.md) as `BL-0073` (B7), `BL-0074` (B8), `BL-0077`
> (B11), `BL-0072` (B6), `BL-0075` (B9), `BL-0076` (B10), `BL-0078` (B12), `BL-0081` (B15), `BL-0083`
> (B17) — the Should-tier batch, scheduled together by the pipeline manager's run #75/#76 triage
> once the Must-tier batch's own gate closed and (for B7/B8/B11 specifically) their research
> grounding landed. Worked in the batch's own stated order: B7 → B8 → B11 → B6 → B9 → B10 → B12 →
> B15 → B17.
> **Scope:** `docs/requirements/01-functional-requirements.md`,
> `docs/requirements/02-non-functional-requirements.md` (read in full; no NFR added or modified —
> see §2 below), `docs/requirements/03-requirements-traceability-matrix.md`. Read in full as inputs
> before this pass: `docs/pipeline/backlog.md` (the nine source rows), the newly grounded research
> topics [`R109` v1.2](../research/encyclopedia/R109-sensor-operations.md) §3.6–§3.10,
> [`R117` v1.2](../research/encyclopedia/R117-directed-energy-and-kinetic-effects.md) §3.1, and
> [`R131` v1.1](../research/encyclopedia/R131-space-environment-and-space-weather-operations.md) §3,
> `docs/architecture/04-domain-model.md` (GDS-04), `docs/design/05-interface-control-document.md`
> (ICD, INT-0001–0016), `docs/architecture/adr/INDEX.md` (ADR-0001–0035), the existing `FR-1200`/
> `FR-1300`/`FR-1400`/`FR-2300`/`FR-3400`/`FR-4400`/`FR-7300` sibling leaves each new leaf was added
> alongside, and the existing Candidate Requirement `CR-17` (checked against `FR-1430`, not
> promoted — see §4).
> **No architecture was redesigned.** GDS-03/GDS-04 and the ICD are read as fixed inputs; nothing
> in `docs/architecture/` was edited to produce this report.

[↑ Docs index](../INDEX.md) · [Backlog](../pipeline/backlog.md)

---

## 1. Bottom line

**Thirteen new baselined requirement leaves added**, in the user-accepted priority order:

- `FR-1610`–`FR-1660` (six leaves, new parent `FR-1600`) — B7 (five sensor-modality variants) and
  B17 (hosted sensor), grouped under one new family since both are sensor-model requests grounded
  in the same research topic (`R109` v1.2).
- `FR-1230` (new child under `FR-1200`'s existing parent) — B8, space-weather-index-driven LEO drag
  coupling.
- `FR-4440` (new child under `FR-4400`'s existing parent) — B8, the anomaly-rate-scaling half of
  the same capability.
- `FR-1430` (new child under `FR-1400`'s existing parent) — B11, debris-field persistence estimate.
- `FR-1320` (new child under `FR-1300`'s existing parent) — B6, per-asset manoeuvre ledger.
- `FR-2320` (new child under `FR-2300`'s existing parent) — B9, per-asset telemetry CSV export.
- `FR-3430`, `FR-3440` (new children under `FR-3400`'s existing parent) — B10, effect-authorization
  gating and live ROE changes.
- `FR-7330` (new child under `FR-7300`'s existing parent) — B12, variable-speed AAR replay.
- `FR-1440`, `FR-1450` (new children under `FR-1400`'s existing parent) — B15, jamming-delivery
  degradation and per-effect-class detectability/attribution settings.

Every leaf traces to its backlog row (which itself cites the specific baseline code/requirement it
extends) plus, where applicable, an existing ADR or the newly grounded research topic (`R109`,
`R117`, `R131`) that closed the research-first prerequisite for B7/B8/B11. No invented capability
was added beyond what the nine backlog rows state.

**No NFR was added.** `FR-3430`'s approval-decision logging and `FR-3440`'s ROE-change logging are
both satisfied by the existing `NFR-2600` ("every state-changing event... appended to an ordered,
timestamped action log") — a new leaf's own Postconditions restating an already-covered NFR is not
a gap. No other item in this batch implies a quality attribute the existing NFR baseline doesn't
already cover (checked against all sixteen NFR categories in
[`02-non-functional-requirements.md`](../requirements/02-non-functional-requirements.md)).

## 2. New requirements added (summary — full text in `01-functional-requirements.md`)

| ID | Title | Parent | Source |
|---|---|---|---|
| `FR-1230` | Space-weather-index-driven LEO drag coupling | `FR-1200` | `BL-0074`; `R131` v1.1 §3; `ADR-0002` |
| `FR-1320` | Per-asset manoeuvre ledger with purpose tags and export | `FR-1300` | `BL-0072` |
| `FR-1430` | Debris-field persistence estimate by altitude | `FR-1400` | `BL-0077`; `R117` v1.2 §3.1; `CR-17` (deliberately narrower than) |
| `FR-1440` | Uplink/crosslink jamming degrades command and relay delivery paths | `FR-1400` | `BL-0081` |
| `FR-1450` | Per-effect-class detectability and attribution-difficulty configuration | `FR-1400` | `BL-0081` |
| `FR-1610` | Fence/dish radar beam-mode variants | `FR-1600` (new) | `BL-0073`; `R109` v1.2 §3.6 |
| `FR-1620` | Optical sensor solar/lunar exclusion angle | `FR-1600` (new) | `BL-0073`; `R109` v1.2 §3.7 |
| `FR-1630` | Space-based sensor minimum-range floor and altitude-band affinity | `FR-1600` (new) | `BL-0073`; `R109` v1.2 §3.8 |
| `FR-1640` | Cue-dependent sensor tasking precondition | `FR-1600` (new) | `BL-0073`; `R109` v1.2 §3.9 |
| `FR-1650` | Passive-RF multilateration sensor network | `FR-1600` (new) | `BL-0073`; `R109` v1.2 §3.10; `ADR-0010` |
| `FR-1660` | Satellite-hosted sensor follows host orbit | `FR-1600` (new) | `BL-0083`; `FR-5170` |
| `FR-2320` | Per-asset telemetry CSV export over a time span | `FR-2300` | `BL-0075`; `FR-4430` |
| `FR-3430` | Optional per-effect-type controller-role authorization gating | `FR-3400` | `BL-0076` |
| `FR-3440` | Live, logged mid-session ROE flag changes | `FR-3400` | `BL-0076`; `ADR-0002` |
| `FR-7330` | Variable-speed AAR replay from truth or a single cell's viewpoint | `FR-7300` | `BL-0078` |
| `FR-4440` | Space-weather-index-driven anomaly rate scaling | `FR-4400` | `BL-0074`; `R131` v1.1 §3 |

## 3. Review findings

Per this skill's mandatory Step 3 review dimensions:

| # | Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| 1 | Duplicates | None found | Each of the thirteen leaves covers a distinct observable behavior; none restates another leaf in this batch or an existing baseline leaf under a different ID. | — | No action. |
| 2 | Conflicts | `FR-1440`/`FR-1450` (B15) vs. `FR-1410`/`ADR-0011` | None found. `FR-1440` extends jam's existing consequences within the six-channel model (`ADR-0011`) rather than adding a seventh channel or bypassing `FR-3410`'s execute-time re-validation; `FR-1450` layers per-class configuration on top of `FR-1410`'s existing attribution-as-side-effect mechanism rather than replacing it. | — | No action. |
| 3 | Conflicts | `FR-3440` (live ROE changes) vs. `ADR-0016` (single point of time control) | None found. `FR-3440` is an ordinary logged operator action recorded in the `EventLog`, not a second clock-control mechanism; it does not touch `SimClock` ownership. | — | No action. |
| 4 | Ambiguities | `FR-1230`/`FR-4440` (B8) — exact index-to-scaling mapping function | Neither the backlog row nor `R131` v1.1 §3 specifies a concrete mathematical mapping from a declared Kp/F10.7 value to a specific drag-decay multiplier or anomaly-firing-rate multiplier — only that a real relationship exists and that F10.7/Kp are the two correct numeric inputs. This is a design-level choice, not a requirements-level one. | Low | Flag as an Open Question for `06-feature-specification` to resolve when a Feature Spec for B8 is drafted — do not invent a specific mapping formula here. |
| 5 | Ambiguities | `FR-1620` (B7) — single-source exclusion-angle figure | `R109` v1.2 §3.7's own text already flags its ~90° solar-phase exclusion figure as resting on a single source (also filed as `docs/pipeline/backlog.md` `BL-0103`). `FR-1620` itself does not bake in the 90° number — it requires only a *configurable* `exclusion_angle_deg` — so this ambiguity does not block the requirement's baseline status, only the specific default value a future implementation might choose. | Low | No requirements-baseline action needed; the configurability itself is what makes the single-source figure non-blocking. A future `02-research-ow-orbital-mechanics` pass finding a second source (per `BL-0103`'s own disposition) should inform, not gate, `06-feature-specification`'s eventual default-value choice. |
| 6 | Shared-taxonomy consistency note (not a defect, a heads-up) | `FR-3430` (B10, approval gating by effect type/reversibility category) vs. `FR-1450` (B15, detectability/attribution settings by effect type/reversibility category) | Both new leaves key their configuration off the same underlying classification scheme (an effect's type and/or its five-D's reversibility category, `FR-1410`) for two different purposes (an approval workflow vs. a detection/attribution model). Neither leaf invents a competing taxonomy, and the requirements as written are independently satisfiable, but a future implementation should use one shared effect-classification enumeration for both, not two parallel ones that could drift apart. | Low | Flag for whoever drafts the Feature Spec(s) for B10/B15 to confirm both consume the same effect-type/reversibility-category enumeration, rather than each defining its own. |
| 7 | Missing requirements | None found | Every capability named in the nine backlog rows (five B7 sensor variants, B8's two halves, B11, B6, B9, B10's two halves, B12, B15's two halves, B17) has at least one FR. | — | No action. |
| 8 | Impossible requirements | None found | All thirteen leaves are physically and logically satisfiable given the existing engine architecture (`AccessProvider`, `isr.py`'s `BEAM_MODES`, `EventLog`, `perturbations.py`). | — | No action. |
| 9 | Requirements that violate architecture | `FR-1660` (B17, hosted sensor) vs. `ADR-0023` (one-directional dependency graph) | None found. A hosted sensor reading its host Asset's already-propagated orbital state is a read of existing engine state, not a new dependency edge between subsystems. | — | No action. |
| 10 | Requirements lacking verification | None found among the thirteen new leaves | Every new leaf's Acceptance Criteria is checkable by a reviewer with no other context beyond the leaf and its cited sources. | — | No action. |
| 11 | Requirements lacking traceability | None found | Every new leaf cites its specific backlog row plus at least one real source-code location, ADR, or research topic — no leaf relies on "implied by the architecture" or an uncited claim. | — | No action. |
| 12 | Interface-model note (not a new finding, a cross-reference) | `FR-7330` vs. `INT-0014` | `FR-7330` cites `INT-0014` (AAR/Replay → Engine), the same interface the Must-tier batch's `FR-7410`/`FR-7420` already flagged as stretched by a state-vector/ephemeris export shape (`reviews/requirements-update-must-tier-batch.md` Finding 6, tracked as `BL-0093`). `FR-7330`'s variable-speed/per-cell-viewpoint playback is a related but distinct stretch of the same interface. | Low | Fold into the same `BL-0093` follow-up (an ICD extension for `INT-0014`, not a requirements-baseline defect) rather than filing a new, separate backlog entry for the same interface. |
| 13 | Prior-document citation defect (found while editing, not new to this batch) | `01-functional-requirements.md`'s Must-tier-batch changelog note | The note added for the Must-tier batch (2026-09-26) cited `03-requirements-review.md` for `FR-7420`'s blocking-dependency detail — no such file exists in this repository; the actual document is `reviews/requirements-update-must-tier-batch.md`. Fixed in place as part of this pass's own top-of-file changelog edit (the surrounding text was already being touched to add this batch's own note). | Low | Fixed same pass — no further action needed. |

## 4. Candidate Requirements check

Checked all existing Candidate Requirements (`CR-1` through `CR-21` in
`01-functional-requirements.md`'s Candidate Requirements section) against this batch's nine items.
One near-match: **`CR-17` — Persistent Debris / STM Environment Layer** overlaps `BL-0077`/B11's
debris-persistence request, but `CR-17`'s own text describes a materially larger capability
(persistent debris that *gates future Access Windows*) than B11 asks for (an *informational*
persistence estimate shown to players, with no gating consequence). `FR-1430` was written as its
own, narrower baselined leaf rather than a promotion of `CR-17` — `CR-17` remains open, unpromoted,
in the Candidate Requirements section, since the fuller gating mechanism it describes is still
unrequested and ungrounded beyond `R117`'s persistence-figure grounding. No other Candidate matched
this batch's scope closely enough to promote.

## 5. Traceability matrix

`docs/requirements/03-requirements-traceability-matrix.md` gained thirteen new rows (one per new
leaf), each with `Future Feature`/`Test`/`Impl. Package` columns marked `UNASSIGNED` (no `FS-xxx`/
`IP-xxxx` exists yet for any of the nine backlog items, and no test exists yet — these are
requirements, not implemented capabilities). Five rows (`FR-1230`, `FR-1430`, `FR-1610`–`FR-1650`,
`FR-4440`) carry a populated Research cell (`R131`, `R117`, `R109` respectively) for the first time
on a fresh leaf. `Arch. Component` and `Interface` cells are filled from the existing GDS-03/ICD
component legend (`C1`–`C12`, `INT-0001`–`INT-0016`) per each leaf's own Source Documents/
Dependencies fields — no new component or interface ID was invented.

## 6. What this report does not do

- It does not resolve Finding 4's design ambiguity (the index-to-scaling mapping function) or
  Finding 6's shared-taxonomy consistency note — both are routed to whoever drafts the eventual
  Feature Spec(s) for B8/B10/B15, not decided here.
- It does not re-litigate Finding 5's single-source figure — that remains `BL-0103`'s own,
  already-filed disposition (a future research pass, not a requirements-baseline blocker).
- It does not touch GDS-05 (the architecture-ladder's own Functional Requirements level) — same
  pre-existing, left-open reconciliation gap the Must-tier batch's own report already named.

## Next

Per this skill's mandatory completion summary, restated here for the review report's own record:
**Recommendations** — resolve Finding 4 (index-to-scaling mapping) and Finding 6 (shared
effect-classification taxonomy) when `06-feature-specification` drafts Feature Specs for B8/B10/
B15; fold Finding 12 into `BL-0093`'s existing ICD-extension follow-up rather than filing a
duplicate; no action needed on Finding 5 beyond `BL-0103`'s own already-recorded disposition.
**Next step** — return to `00-pipeline-manager` to harvest this run's findings into the backlog and
determine the next pipeline step (a `05-feature-decomposition`/`06-feature-specification` pass over
this now-baselined batch, alongside the seven packages still awaiting `09-package-verification` in
a fresh session).
