> **Document ID:** FS-121
> **Version:** 1.0
> **Status:** ✅ Ready for implementation planning (`FR-7410` slice); `FR-7420` slice remains
> **Blocked on FS-103 v1.1's confirmed design** for its own detailed workflow — see Open Questions
> **Note on this repository's chain:** no Feature Catalog exists here; the approved input is
> `docs/requirements/01-functional-requirements.md` `FR-7410`/`FR-7420` (new parent `FR-7400`),
> grounded in [ADS-1500](../architecture/ADS-1500-per-cell-custody-estimated-state-and-export.md)
> (System Architecture, Decision Log).
> **Dependencies:** [FS-103](FS-103-custody-management.md) v1.1 (`Track.state_estimate`'s confirmed
> independence from truth, and the replay-based history mechanism `FR-7420` reuses), [FS-107](FS-107-after-action-review.md)
> (`FR-7310`/`session/aar.py::state_at` — the replay mechanism both `FR-7410`'s and `FR-7420`'s
> time-span sampling are built on), `FR-6220` (no-cell ground-truth endpoints, the binding `FR-7410`
> must use)
> **Referenced By:** [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0069` (external
> validation report, 26 Sep 2026, item B3)
> **Produces:** truth and cell-observed ephemeris export in ECI/RIC, CSV/CCSDS OEM, satisfying
> `FR-7410`/`FR-7420`
> **Feature Mapping:** FS-121 (this document)
> **Related Topics:** [ADS-1500](../architecture/ADS-1500-per-cell-custody-estimated-state-and-export.md),
> [FS-103](FS-103-custody-management.md) v1.1, [FS-107](FS-107-after-action-review.md)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template.*

# FS-121 — Ephemeris Export (Truth and Cell-Observed, ECI/RIC, CSV/CCSDS OEM)

## Purpose

Let White Cell export ground-truth state vectors, and let a cell export its own believed
(custody-estimated) state vectors, for a time span, in ECI and RIC frames, as CSV and CCSDS OEM
files — a capability the baseline entirely lacks (god-view returns only current-instant truth as
JSON; AAR export covers the event log, not state vectors). `FR-7410`/`FR-7420`'s own Rationale
states this directly.

## Scope

**In scope:** (1) a no-cell, White-Cell-only truth ephemeris export over a requested time span, in
ECI and RIC-relative-to-a-chosen-object, as CSV and CCSDS OEM (`FR-7410`); (2) a cell-scoped,
fog-of-war-respecting export of that same cell's own believed state vectors over the same kind of
time span/frame/format set (`FR-7420`).

**Out of scope:** the underlying estimated-state-history mechanism itself, already designed by
`ADS-1500` (reused here, not re-specified); any change to `FS-103`'s custody model or `FS-107`'s AAR
replay mechanism, both of which this Feature consumes unchanged.

## Requirements Implemented

`FR-7410` (truth ephemeris export), `FR-7420` (cell-observed ephemeris export).

## User Workflows

1. **Truth export (White Cell).** White Cell specifies a time span, one or more assets, a reference
   object (for RIC), and a format (CSV or CCSDS OEM); the system returns ground-truth state vectors
   for that span in both ECI and RIC-relative-to-the-reference-object form, via one of the existing
   no-cell endpoints (`FR-6220`).
2. **Cell-observed export (a Blue or Red cell operator).** The requesting cell specifies a time span,
   one or more tracked-object identifiers, a reference object, and a format; the system returns that
   cell's own believed state vectors (never ground truth, never another cell's belief) for the span,
   via a cell-scoped endpoint.

## System Behaviour

- **Truth export** samples ground truth (`Asset.orbit`, propagated via the existing `Propagator`
  seam) at each requested time in the span, transforms to ECI directly and to RIC relative to the
  chosen reference object's own truth state, and serializes to the requested format. Reachable only
  through the existing no-cell endpoints (`/godview`, `/eventlog`, `/save`, `/aar*`, `/objectives`
  per `FR-6220`) — never a new cell-scoped route (`ADR-0004`, `ADR-0015`).
- **Cell-observed export** samples, at each requested time T in the span, the requesting cell's own
  belief state via the mechanism `ADS-1500` designs: replay the deterministic `EventLog` to the
  position nearest T (`engine/simulation.py::replay`, the same call `session/aar.py::state_at`
  already makes), read that cell's reconstructed `Track.state_estimate`, and forward-propagate it to
  exactly T. A time T at which the cell holds no `Track` on the object produces no point for that T
  (an empty result, not a fabricated one) — `FR-7420`'s own Postcondition.
- **RIC reference-object rule (cell-observed export only):** if the reference object is the
  requesting cell's own owned Asset, its ground-truth orbit is used directly (a cell always knows
  its own asset's true state exactly); if the reference object is itself only tracked, the same
  cell's own `Track.state_estimate` for it (at the same T) is used, never ground truth
  (`ADS-1500` Decision 5).
- **`FR-7420` is blocked on nothing architecturally** (`ADS-1500` resolved `BL-0068`'s domain-model
  question in full) but its detailed workflow depends on `FS-103` v1.1's confirmed design being read
  by whoever writes its Implementation Package — flagged in Open Questions only insofar as this
  document's own Acceptance Criteria for `FR-7420` cannot be exercised until that reading happens
  (a sequencing note, not an unresolved design question).

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| Session Layer (new export function, sibling to `session/aar.py`) | Drives replay across the requested time span (a generalization of `aar.py::state_at`'s single-point replay) for both truth and cell-observed variants; reads the appropriate state source per variant. |
| `engine/simulation.py` (`replay`) | Reconstructs `WorldState` at each sampled time — unchanged, reused as-is. |
| `engine/propagator.py` (`Propagator`) | Forward-propagates the sampled state (truth `Asset.orbit` or a cell's `Track.state_estimate`) to exactly the requested time — unchanged, reused as-is. |
| A new shared ephemeris serializer (ECI/RIC transform, CSV/CCSDS OEM writers) | Parameterized by state source (truth vs. cell-observed); shared between `FR-7410` and `FR-7420` rather than duplicated, per `ADS-1500`'s System Architecture. |
| `ui_web/server.py` | Exposes the truth export through an existing no-cell route and the cell-observed export through a new cell-scoped route, both per `ADR-0004`/`FR-6220`'s existing binding rules. |

## Interfaces Used

`INT-0014` (AAR/Replay → Simulation Engine, EventLog/WorldState) — the interface both exports drive,
per `ADS-1500`'s System Architecture, generalized from a single-point read to a time-span read.
Flagged (Requirements Review Finding 6, `docs/reviews/requirements-update-must-tier-batch.md`,
backlog `BL-0093`) as a documented-shape stretch: `INT-0014` describes single-point replay reads,
not a time-span/multi-format export. Not resolved here — routed to whoever next touches the ICD.
`INT-0007` (`CellController` → Custody/TrackCatalog) for the cell-observed variant's fog-of-war
binding.

## Data Model Changes

None. Both exports read existing entities (`Asset.orbit`, `Track.state_estimate`) through the
existing replay mechanism; no new Domain Model entity, per `ADS-1500` Decision 2/3.

## State Changes

None — both exports are read-only, exactly like `FR-7310`'s AAR replay/scrub (no live session state
is mutated by producing an export).

## Error Handling

- A requested time span outside the session's own recorded event-log range: not addressed by
  `FR-7410`/`FR-7420`'s own text — see Open Questions.
- A cell-observed export request for an object the requesting cell never held a `Track` on at any
  point in the span: produces an empty result for that object across the whole span (an extension
  of the same-T empty-point behavior above), not an error.
- A malformed/out-of-range reference-object identifier: rejected with a specific reason, consistent
  with the existing "invalid input fails loudly" posture (`FR-5310`'s analogous rule for vignette
  loading).

## Performance Considerations

- **Replay cost scales with sample count × eventlog length** (`ADS-1500` Constraints/Risks) — a
  naive per-sample full replay from `initial_state` could be slow for a fine-grained sample rate
  over a long time span. `ADS-1500` explicitly leaves the mitigation (coarser default sampling,
  reuse of `Snapshot` checkpoints) to `07-implementation-planning`, not this document.

## Security Considerations

- Truth export must remain reachable only through the existing no-cell endpoints (`FR-6220`,
  `ADR-0015`'s documented LAN trust boundary) — never a new cell-scoped route, per `FR-7410`'s own
  Postcondition.
- Cell-observed export must enforce the same fog-of-war-at-the-boundary rule (`ADR-0004`) every
  other cell-scoped read already does — reads only the requesting cell's own `Track`, never another
  cell's, never ground truth.

## Acceptance Criteria

1. Given a time span and a reference object, the truth export's CSV and CCSDS OEM files both contain
   state vectors matching the engine's own truth at each sampled time, correctly transformed into
   RIC relative to the chosen reference object; the export is reachable only via an existing no-cell
   endpoint. *(`FR-7410`)*
2. Given the estimated-state-history mechanism (`ADS-1500`, already resolved), a cell-observed export
   request from cell C for object X returns C's own estimated state at each sampled time, matching
   `CellController`'s existing fog-of-war filtering rule — no ground truth, no other cell's belief
   state. *(`FR-7420`)*

## Verification Plan

Test (automated) for both criteria, per `FR-7410`/`FR-7420`'s own stated Verification Method.
Criterion 2's test suite should include the negative assertion (a cell-observed export never
contains ground truth or another cell's belief), mirroring the existing fog-of-war test pattern
(`spacesim/tests/test_scene.py`).

## Dependencies

`FR-6220` (no-cell endpoints), `FS-107`/`FR-7310` (the replay mechanism both variants reuse), `FS-103`
v1.1 (the confirmed custody-independence finding and the replay-based history design).

## Risks

- **Interface-model stretch (see Interfaces Used)** — `INT-0014`'s documented shape may need an
  architecture-owner edit before an Implementation Package can cite it cleanly for a time-span
  export, though neither `FR-7410` nor `FR-7420` is itself blocked by this (per `BL-0093`'s own
  "not blocking" framing).
- **Performance risk (see Performance Considerations)** — sizing the sampling-rate/time-span ceiling
  is deferred to implementation planning, with no numeric target from any source document.
- **Shared-serializer coupling risk.** Building one serializer shared between `FR-7410` and
  `FR-7420` (per `ADS-1500`'s System Architecture) means a serialization defect affects both exports
  at once — an acceptable, deliberate coupling (avoiding duplication), but worth naming so an
  Implementation Package tests both variants against any serializer change.

## Open Questions

1. **Behavior for a requested time span outside the session's own recorded event-log range** — not
   addressed by either requirement's text. Needs a `04-requirements-engineering` amendment or an
   explicit `07` decision (clamp to the recorded range? reject outright?).
2. **Sampling-rate/performance ceiling** — carried from `ADS-1500`'s own Open Question 2, restated
   here since it directly bounds this Feature's practical usability for a long time span.
3. *(Sequencing note, not a design ambiguity)* Whoever writes the Implementation Package for
   `FR-7420` should read `FS-103` v1.1's confirmed System Behaviour note (`Track.state_estimate`'s
   independence from truth) directly before starting, since it is the load-bearing fact this
   Feature's entire cell-observed variant depends on.

## Related ADRs

`ADR-0002` (deterministic core — the replay guarantee both exports depend on), `ADR-0004`
(fog-of-war at the boundary), `ADR-0015` (LAN trust model — the no-cell endpoint binding `FR-7410`
must respect).

## Related Interfaces

`INT-0007` (Custody/TrackCatalog), `INT-0014` (AAR/Replay — see Interfaces Used).
