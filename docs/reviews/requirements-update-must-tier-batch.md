# Requirements Update Report — Must-tier external-validation-report intake batch (2026-09-26)

> **Status:** Complete — nine new baselined requirement leaves added (eight FR, one NFR) and
> reviewed; one leaf (`FR-7420`) is baselined but flagged as not independently verifiable until a
> named upstream item closes (see Finding 4).
> **Source:** External user validation report, 26 Sep 2026 (baseline `32ca02a`), filed to
> [`docs/pipeline/backlog.md`](../pipeline/backlog.md) as `BL-0082` (B16), `BL-0070` (B4),
> `BL-0071` (B5), `BL-0067` (B1), `BL-0069` (B3) — the Must-tier batch, worked in the user-accepted
> order B16 → B4 → B5 → B1 → B3. `BL-0068` (B2, per-cell estimated element-set history) is a
> **sixth** Must-tier item entering at `03-architecture-design-synthesis`, not this stage; it is
> referenced here only because `FR-7420` depends on it.
> **Scope:** `docs/requirements/01-functional-requirements.md`,
> `docs/requirements/02-non-functional-requirements.md`,
> `docs/requirements/03-requirements-traceability-matrix.md`. Read in full as inputs before this
> pass: `docs/pipeline/backlog.md` (the five source rows), `docs/architecture/04-domain-model.md`
> (GDS-04), `docs/design/05-interface-control-document.md` (ICD, INT-0001–0016),
> `docs/architecture/adr/INDEX.md` (ADR-0001–0035), the existing `FR-4400`/`FR-5100`/`FR-5200`/
> `FR-7300` sibling leaves each new leaf was added alongside, and the cited source-code locations
> (`spacesim/content/vignette.py`, `spacesim/content/vignette_export.py`, `spacesim/config.py`,
> `spacesim/ui_web/server.py`).
> **No architecture was redesigned.** GDS-03/GDS-04 and the ICD are read as fixed inputs; nothing
> in `docs/architecture/` was edited to produce this report. Two Findings below (5, 6) note where
> the ICD's existing interfaces (`INT-0011`, `INT-0012`, `INT-0013`, `INT-0014`) are stretched by
> the new leaves' shape without yet being extended — an architecture-owner decision, not resolved
> here.

[↑ Docs index](../INDEX.md) · [Backlog](../pipeline/backlog.md)

---

## 1. Bottom line

**Nine new baselined requirement leaves added**, in the user-accepted priority order:

- `FR-5410`, `FR-5420` (new parent `FR-5400`) — B16, external vignette directories.
- `FR-4420`, `FR-4430` (new children under `FR-4400`'s existing parent) — B4, condition-triggered
  injects and four new inject effect types.
- `FR-5510` (new parent `FR-5500`) — B5, save-as-scenario.
- `FR-5220` (new child under `FR-5200`'s existing parent) — B1, bulk TLE/CCSDS OMM import.
- `FR-7410`, `FR-7420` (new parent `FR-7400`) — B3, truth and cell-observed ephemeris export.
- `NFR-3700` (Security) — generalizing the existing path-traversal guard to the new content roots
  `FR-5410`/`FR-5420` introduce.

Every leaf traces to its backlog row (which itself cites the specific baseline code/requirement it
extends) plus, where applicable, an existing ADR or research topic. No invented capability was
added beyond what the five backlog rows state.

**One leaf, `FR-7420`, is baselined but not fully closeable yet** — see Finding 4. This is the
correct honest state per this skill's own rules (a requirement's *existence* traces cleanly to the
backlog item; its *verifiability* is blocked on a sixth backlog item, `BL-0068`/B2, that enters at
a different pipeline stage). It is not withheld from the baseline, because the capability itself is
real and requested — only its Acceptance Criteria's testability is deferred.

## 2. New requirements added (summary — full text in `01-functional-requirements.md`/`02-non-functional-requirements.md`)

| ID | Title | Parent | Source |
|---|---|---|---|
| `FR-4420` | Condition-triggered injects, evaluated deterministically | `FR-4400` | `BL-0070`; `ADR-0002`, `ADR-0006` |
| `FR-4430` | New inject effect types (anomaly, sensor outage, custody loss, scripted manoeuvre) | `FR-4400` | `BL-0070`; `ADR-0004`, `ADR-0005` |
| `FR-5220` | Bulk TLE and CCSDS OMM multi-object import | `FR-5200` | `BL-0067`; `ADR-0018` |
| `FR-5410` | Load vignettes from configured external directories | `FR-5400` (new) | `BL-0082` |
| `FR-5420` | `save_vignette` writes only to a configured user directory | `FR-5400` (new) | `BL-0082` |
| `FR-5510` | Save a running session's current state as a new starting vignette | `FR-5500` (new) | `BL-0071`; `ADR-0022` |
| `FR-7410` | Truth ephemeris export (ECI/RIC, CSV/CCSDS OEM) | `FR-7400` (new) | `BL-0069`; `FR-6220` |
| `FR-7420` | Cell-observed ephemeris export (ECI/RIC, CSV/CCSDS OEM) | `FR-7400` (new) | `BL-0069`, `BL-0068`; `ADR-0004` |
| `NFR-3700` | Path-traversal safety generalized to external content roots | Security (§7) | `BL-0082`; `NFR-2200` |

## 3. Review findings

Per this skill's mandatory Step 3 review dimensions:

| # | Finding type | IDs involved | Description | Severity | Recommendation |
|---|---|---|---|---|---|
| 1 | Duplicates | `FR-5510` vs. `FR-7210`/`FR-7220` vs. FS-117/`IP-1173`'s draft save | None found. All three are distinct capabilities (session save/resume of a *running* session's own history; a Vignette Creator *unstarted draft's* one-shot content export; a *running* session's mid-exercise state exported as a *new* vignette's starting content) and are cross-referenced, not merged. | — | No action. |
| 2 | Conflicts | `FR-4420`/`FR-4430` vs. `ADR-0005` (plan-first commanding) | None found. Injects are `ADR-0005`'s own documented, accepted bypass of plan-first commanding for White Cell; a condition-triggered or scripted-manoeuvre inject exercises that existing exception, it does not create a new one or contradict the ADR. | — | No action. |
| 3 | Ambiguities | `FR-4430`'s "any named asset" for scripted manoeuvre | The requirement does not state whether a scripted-manoeuvre inject must still resolve through `engine/maneuver.py`'s existing six entry modes, or may specify a raw resulting state directly. The backlog row (`BL-0070`) does not settle this either. | Low | Flag as an Open Question for `06-feature-specification` to resolve when a Feature Spec for B4 is drafted — do not resolve it here, since it is a design-level (not requirements-level) choice between "reuse `maneuver.py`'s existing entry modes" and "a new direct-state-set path." |
| 4 | Missing requirements / sequencing dependency | `FR-7420` on `BL-0068` (B2) | `FR-7420`'s cell-observed export requires an independently-estimated per-cell state history (`BL-0068`, entering at `03-architecture-design-synthesis`) that does not exist yet — the baseline `Track` is a confidence-decayed copy of truth, not an estimate with its own error growth. `FR-7420` is baselined (the capability is genuinely requested and traces cleanly to `BL-0069`) but its Acceptance Criteria is explicitly marked non-final in `01-functional-requirements.md` pending `BL-0068`. | Medium | Do not implement `FR-7420` before `BL-0068`'s architecture-and-requirements work closes; `07-implementation-planning` must treat `FR-7420` as blocked until then. `FR-7410` (truth export) has no such dependency and may proceed independently. |
| 5 | Interface-model stretch (not a defect, a heads-up) | `FR-5220` vs. `INT-0013` | `INT-0013` (Content & Data → Space-Track.org, TLE import) is documented around a single-object, network-fetch shape; `FR-5220`'s multi-object, file-based (TLE **or** CCSDS OMM) bulk import is a related but structurally different interaction (no network call; a batch of objects; two input formats). The FR does not invent a new interface ID (per this skill's own rule), but the existing ICD entry may need an architecture-owner edit to describe this file-based batch path before `06-feature-specification` can cite `INT-0013` cleanly for it. | Low | Route to `03-architecture-design-synthesis`/whoever owns the ICD: either extend `INT-0013`'s description to cover the file-based batch path, or add a sibling interface ID. Not blocking — `FR-5220` itself is fully specified and testable without this edit. |
| 6 | Interface-model stretch (not a defect, a heads-up) | `FR-7410`/`FR-7420` vs. `INT-0014` | `INT-0014` (Session Layer AAR/Replay → Simulation Engine) is documented around event-log/`WorldState` replay reads, not a time-span state-vector/ephemeris export in two formats and two frames. The FRs cite `INT-0014` as the closest existing interface (both are Session-Layer-owned reads of engine state for White Cell's use) but this is the same kind of stretch as Finding 5. | Low | Same routing as Finding 5 — an ICD extension, not a requirements-baseline defect. |
| 7 | Requirements lacking verification | None found among the eight new baselined FRs (`FR-7420` excepted, per Finding 4) | Every new leaf's Acceptance Criteria is checkable by a reviewer with no other context beyond the leaf and its cited sources. | — | No action. |
| 8 | Requirements lacking traceability | None found | Every new leaf cites its specific backlog row plus at least one real source-code location, ADR, or research topic — no leaf relies on "implied by the architecture" or an uncited claim. | — | No action. |
| 9 | Requirements that violate architecture | None found | `NFR-3700`'s generalization of `NFR-2200` and `FR-5410`'s external-directory read path were checked against `ADR-0018` (offline-first runtime) and `ADR-0007` (content as data) — both are consistent; neither introduces a network dependency or moves scenario logic into code. | — | No action. |

## 4. Candidate Requirements check

No existing Candidate Requirement (`CR-1` through `CR-21` in `01-functional-requirements.md`'s
Candidate Requirements section) matched this batch's scope closely enough to promote. None of the
five source backlog rows was itself originally filed as a Candidate — each entered directly as a
`feature` item scheduled for this `04-requirements-engineering` pass. No promotion was made.

## 5. Traceability matrix

`docs/requirements/03-requirements-traceability-matrix.md` gained nine new rows (one per new
leaf), each with `Feature Spec` and `Implementation Package` columns marked `UNASSIGNED` (no
`FS-xxx`/`IP-xxxx` exists yet for any of the five items) and `Test` marked `UNASSIGNED` (no test
exists yet — these are requirements, not implemented capabilities). `Subsystem` is filled from the
same module each leaf's Source Documents already cites.

## 6. What this report does not do

- It does not resolve Finding 3's design ambiguity, or Findings 5/6's ICD stretch — both are
  routed to their owning skill/stage, not decided here.
- It does not implement, spec, or architect anything for `BL-0068` (B2) itself — that item enters
  the pipeline at `03-architecture-design-synthesis`, per the pipeline journal's own recorded
  disposition, not at this stage.
- It does not touch GDS-05 (the architecture-ladder's own Functional Requirements level) — per the
  same reconciliation gap `requirements-update-fs117.md` Finding 9 already flagged and left open;
  this pass does not close that pre-existing gap, only adds to the same un-reconciled situation
  consistently with how the FS-117 pass handled it.

## Next

Per this skill's mandatory completion summary, restated here for the review report's own record:
**Recommendations** — resolve Finding 3 (scripted-manoeuvre entry-mode choice) when `06-feature-
specification` drafts a Feature Spec for the B4 capability; route Findings 5/6 (ICD stretch) to
whoever next touches `INT-0013`/`INT-0014`; do not schedule `FR-7420`'s implementation before
`BL-0068` closes its own architecture-and-requirements work. **Next step** — proceed to
`03-architecture-design-synthesis` on `BL-0068` (B2), per the pipeline journal's already-recorded
ordering, since `FR-7420` (just baselined) depends on its outcome.
