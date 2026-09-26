> **Document ID:** FS-119
> **Version:** 1.0
> **Status:** ✅ Ready for implementation planning
> **Note on this repository's chain:** no Feature Catalog exists here; the approved input is
> `docs/requirements/01-functional-requirements.md` `FR-5220`, a sibling leaf under `FR-5210`'s
> existing `FR-5200` parent. `FR-5210` itself (Space-Track import + manual fallback) has no owning
> Feature Specification in this repository as of `32ca02a` — a pre-existing gap this document does
> not silently absorb (see Open Questions).
> **Dependencies:** `FR-1210` (propagator seam), `FR-5140` (single manual TLE/lat-long entry, the
> capability `FR-5220` is a batch sibling of, not a replacement for)
> **Referenced By:** [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0067` (external
> validation report, 26 Sep 2026, item B1)
> **Produces:** a bulk TLE/CCSDS OMM multi-object import capability satisfying `FR-5220`
> **Feature Mapping:** FS-119 (this document)
> **Related Topics:** [FS-118](FS-118-external-vignette-directories.md) (same increment, adjacent
> content-ingestion concern)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template.*

# FS-119 — Bulk TLE and CCSDS OMM Multi-Object Import

## Purpose

Let White Cell import many objects from a single file — a multi-object TLE file or a CCSDS Orbit
Mean-Elements Message (OMM) file — in one operation, each assigned to a side and asset template,
instead of the baseline's one-object-per-call path. `FR-5220`'s Rationale states this directly: the
existing `POST /api/sessions/{sid}/force/tle` route and `FR-5140`'s manual paste both accept exactly
one object per call, with no OMM support and no batch side/template mapping.

## Scope

**In scope:** parsing a multi-object TLE file and a CCSDS OMM file; per-object side (cell)
assignment and asset-template assignment specified alongside the import; per-object
success/failure reporting so one malformed object does not abort the batch.

**Out of scope:** any change to the existing single-object `force/tle` route or `FR-5140`'s manual
paste path (both continue to exist unchanged, per `FR-5220`'s own Rationale distinguishing it from
both); Space-Track.org network import (`FR-5210`'s own, separate scope, unaffected).

## Requirements Implemented

`FR-5220` — Bulk TLE and CCSDS OMM multi-object import.

## User Workflows

1. White Cell selects a multi-object TLE file or a CCSDS OMM file for import (via the Vignette
   Creator or an equivalent White-Cell-only authoring surface).
2. White Cell assigns, per object in the file, a side (Blue/Red/neutral) and an asset template.
3. White Cell triggers the import; the system reports, per object, whether it succeeded (force-added
   as an Asset) or failed (with a specific reason), without aborting the remaining objects.

## System Behaviour

- Parses either format (multi-object TLE, CCSDS OMM) into a list of per-object orbital elements.
- For each object, resolves the assigned side/template and force-adds one `Asset` with a populated
  `OrbitState`, using the same underlying mechanism `FR-1210`'s propagator seam and `FR-5140`'s
  single-object path already use — this Feature batches the operation, it does not reimplement
  element-set validation or `OrbitState` construction.
- A malformed object (unparseable elements) is reported as a per-object failure; the batch continues
  processing the remaining objects (`FR-5220`'s own Postcondition).
- No network access is required (`ADR-0018`) — both formats are file-based, consistent with the
  offline-first posture `FR-5210`'s manual/Keplerian fallback already establishes.

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `content/` (TLE/OMM parsing) | Parses both file formats into per-object element sets; the concrete module/function is an `07-implementation-planning` decision (an extension of, or new sibling to, whatever module already parses a single TLE for `force/tle`). |
| `engine/propagator.py` | Constructs the resulting `OrbitState` per object, reusing the existing `Propagator` seam (`FR-1210`) — no new propagation logic. |
| Operator Console (`ui_web/`) | Presents the per-object side/template assignment UI and the per-object success/failure report. |

## Interfaces Used

`INT-0013` (Content & Data → Space-Track.org, TLE import) — cited as the closest existing
interface, per `FR-5220`'s own Source Documents, but flagged (Requirements Review Finding 5,
`docs/reviews/requirements-update-must-tier-batch.md`, backlog `BL-0092`) as a stretched fit: this
Feature's actual interaction is file-based and multi-object, not the network single-object fetch
`INT-0013` documents. This document does not invent a new interface ID — it is an Open Question for
whoever next touches the ICD (see Open Questions).

## Data Model Changes

None. Each imported object becomes an ordinary `Asset` with an `OrbitState`, identical in shape to
one produced by `FR-5140`'s single-object path or the existing `force/tle` route — no new entity.

## State Changes

Force-adds N new `Asset`s to the current session/draft-session state (one per successfully-parsed
object in the file), identical in kind to what a single `force/tle` call already does N times.

## Error Handling

- A malformed object within an otherwise-valid file: reported per-object, does not abort the batch
  (`FR-5220`'s Acceptance Criteria).
- A file that is neither valid multi-object TLE nor valid CCSDS OMM: rejected outright before any
  object is processed — not addressed explicitly by `FR-5220`'s own text beyond this inference; see
  Open Questions for whether a partially-recognizable file should attempt best-effort parsing.

## Performance Considerations

None named by `FR-5220`. A file large enough to strain the existing `~24 satellites` soft sizing
guideline (`ADR-0019`) is a White-Cell authoring-time concern, not a runtime one — this Feature
operates before a session starts.

## Security Considerations

Standard input validation applies (`NFR-2200`) — a malformed or adversarially-crafted file must be
rejected/reported, never executed as code, consistent with the existing "content is data"
invariant (`ADR-0007`).

## Acceptance Criteria

1. Given a multi-object TLE file with nine valid objects and one malformed object, the import
   produces nine force-added Assets with the specified side/template assignments, and reports the
   tenth object's failure without aborting the other nine.
2. Given a CCSDS OMM file with multiple objects, the same holds.

## Verification Plan

Test (automated) for both criteria, per `FR-5220`'s own stated Verification Method.

## Dependencies

`FR-1210` (propagator seam), `FR-5140` (single-object manual entry, the sibling this Feature
batches rather than replaces).

## Risks

- **Interface-model stretch (see Interfaces Used).** `INT-0013`'s documented shape does not cleanly
  fit this Feature's file-based batch interaction; an Implementation Package may need to wait on, or
  separately request, an ICD clarification.
- **CCSDS OMM parsing is new format support** — no existing code path in this repository parses OMM
  today (only TLE, per the baseline `force/tle` route); this is new parsing logic, not a reuse of an
  existing parser, unlike the TLE half of this Feature.

## Open Questions

1. **Does `INT-0013` need an architecture-owner edit (or a sibling interface) to cover this
   Feature's file-based batch path**, per the Requirements Review's own Finding 5 (`BL-0092`)? Not
   resolved here — routed to whoever next touches the ICD.
2. **What is the observable behavior for a file that is neither valid multi-object TLE nor valid
   CCSDS OMM** (as opposed to a valid file containing one malformed object)? `FR-5220`'s own text
   does not distinguish these two failure classes explicitly. Needs a `04-requirements-engineering`
   amendment or an explicit `07` design decision.
3. **Is there a maximum batch size, or does this Feature defer entirely to the existing `~24
   satellites` soft guideline** (`ADR-0019`, enforced today only via `SessionManager`'s clock-lag
   watchdog, not a hard cap)? Not addressed by `FR-5220`.

## Related ADRs

`ADR-0018` (offline-first runtime), `ADR-0019` (sizing is a soft guideline, not an engine-enforced
cap), `ADR-0007` (content as data).

## Related Interfaces

`INT-0011` (vignette/template load) — related but not used directly; force-added assets are not
themselves a vignette load, though they populate the same kind of Asset entity a vignette load
would.
