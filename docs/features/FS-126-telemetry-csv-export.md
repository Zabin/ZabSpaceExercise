> **Document ID:** FS-126
> **Version:** 1.0
> **Status:** ✅ Ready for implementation planning
> **Note on this repository's chain:** no `05-feature-decomposition` Feature Catalog exists here
> (per this skill's own Gotchas); this document's approved input is the just-baselined requirement
> itself — `docs/requirements/01-functional-requirements.md` `FR-2320` — plus the real baseline
> code it extends (`engine/telemetry.py`, `spacesim/ui_web/server.py`).
> **Dependencies:** [FS-106](FS-106-white-cell-dashboard.md) v2.1 (`FR-4430`'s `anomaly` inject
> effect — the channel-perturbation source this Feature's export must reflect faithfully)
> **Referenced By:** [IP-1260](../implementation/packages/IP-1260-telemetry-csv-export.md)
> (Implementation Package, `BLOCKED` on `IP-1062` reaching `VERIFIED`),
> [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0075` (item B9),
> [docs/requirements/01-functional-requirements.md](../requirements/01-functional-requirements.md)
> `FR-2320`
> **Produces:** a fog-of-war-respecting, per-asset telemetry CSV export over a requested time span,
> satisfying `FR-2320` in full
> **Feature Mapping:** FS-126 (this document)
> **Related Topics:** [FS-121](FS-121-ephemeris-export.md) (Ephemeris Export — the sibling export
> capability this Feature's fog-of-war-respecting export pattern mirrors)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template.*

# FS-126 — Per-Asset Telemetry CSV Export Over a Time Span

## Purpose

Let a cell export its own pass-gated telemetry channel history for a named Asset over a requested
time span as CSV, for use outside the live console — closing the gap `FR-2320`'s own Rationale
names: 19 telemetry parameters per asset are exposed via JSON endpoints (read-time seeded,
`engine/telemetry.py`) with no export path, and a new-effect-type anomaly inject (`FR-4430`) must
perturb the exported channel(s) exactly as it perturbs the live JSON-endpoint values.

## Scope

**In scope:** exporting the requesting cell's own pass-gated telemetry channel values for a named
Asset and simulated time span as CSV.

**Out of scope (named, not silently absorbed):** any change to the pass-gating mechanism itself
(`FR-2310`, unchanged); any change to `FR-4430`'s existing anomaly-effect mechanism — this Feature
only requires that the export faithfully reflects whatever that mechanism already produces.

## Requirements Implemented

- `FR-2320` — Per-asset telemetry CSV export over a time span.

## User Workflows

1. **An operator (or facilitator) requests a telemetry export.** They name an Asset, their own cell
   (implicit, from their session), and a simulated time span.
2. **The system produces a CSV.** Each row is a sampled point across the requested span, with the
   requesting cell's own pass-gated telemetry channel values at that point — identical to what that
   cell's own live telemetry endpoint would show at the same simulated time.
3. **An anomaly-inject effect is active during part of the span.** The exported rows for the
   affected channel(s) show the perturbation at the correct simulated times, exactly as the live
   endpoint already would.

## System Behaviour

- **Normal path.** The export reads the same underlying telemetry function the live JSON endpoint
  reads (`engine/telemetry.py`), sampled across the requested span, and reflects the requesting
  cell's own pass-gated view (`FR-2310`) — never ground truth, never another cell's view.
- **Edge case — requested span partially or wholly outside the recorded session range.** Not
  addressed by `FR-2320`'s own text (Open Question 1); the sibling ephemeris-export capability
  (`FR-7410`/`FR-7420`, `FS-121`) already resolved an analogous question (clamp a partial
  out-of-range span, reject a wholly out-of-range one) but `FR-2320` does not itself state that the
  same rule applies here.
- **Edge case — an active anomaly-inject effect during the span.** The affected channel's exported
  values reflect the perturbation at the correct simulated times, read from the same function the
  live endpoint reads — no separate perturbation logic in the export path.

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `engine/telemetry.py` | Owns the read-time seeded telemetry sampling function(s) (`sample`/`series`) this export reuses directly — no parallel computation. |
| `session/manager.py` | Owns deriving the sampled-and-filtered export rows for a requested Asset/cell/span, applying the same fog-of-war filter (`FR-6210`) the live endpoint already applies. |
| `ui_web/server.py` | Exposes the new export route, cell-scoped like every other cell-scoped route. |

## Interfaces Used

- `INT-0006` (Console → SessionAPI seam) — the existing interface the export request operates
  through.
- `INT-0007` (CellController → Engine Custody) — the existing interface the fog-of-war-filtered read
  operates through, per `FR-2320`'s own citation of `FR-6210`.

## Data Model Changes

None — this Feature is a read-only export over `engine/telemetry.py`'s existing sampled values; no
new entity, no new persisted state.

## State Changes

None — a pure read/export operation, like `scene.py`'s render-from-custody pattern (`ADR-0025`).

## Error Handling

- A requested Asset/cell combination the requesting cell has no fog-of-war-filtered access to: the
  export must not silently substitute ground truth — mirrors `FR-2320`'s own "never ground truth"
  Postcondition, treated as a rejection, consistent with every other cell-scoped route's existing
  behavior (`FR-6210`).
- A requested time span partially or wholly outside the recorded range: Open Question 1.

## Performance Considerations

None named by `FR-2320` beyond what the existing telemetry-sampling function already respects — a
bounded, per-request sampling operation over the requested span, not a new computational class.

## Security Considerations

`FR-6210` (fog-of-war filtering) is this Feature's core constraint: the export must be identical, in
principle, to what the requesting cell's own live telemetry endpoint would show at each sampled
point — never another cell's or ground-truth values (`FR-2320`'s own Postconditions, explicit).

## Acceptance Criteria

1. Given an Asset with an active anomaly-inject effect (`FR-4430`) perturbing one telemetry channel,
   the CSV export for the affected cell shows the perturbation at the correct simulated times.
   *(`FR-2320`)*
2. A different cell's export of the same Asset never shows data that cell's own fog-of-war filter
   would not otherwise expose. *(`FR-2320`, `FR-6210`)*

## Verification Plan

- Criterion 1 — Test: fire an `anomaly` inject affecting one channel during a requested span; assert
  the exported rows show the expected perturbation at the correct times.
- Criterion 2 — Test: request the same Asset/span export as two different cells; assert each export
  matches only that cell's own fog-of-war-filtered live-endpoint values.

## Dependencies

`FR-2310` (pass-gated telemetry, unchanged), `FR-6210` (fog-of-war filtering, unchanged), `FR-4430`
(the anomaly-inject effect this export must faithfully reflect, unchanged by this Feature).

## Risks

- **Ambiguity risk (Open Question 1 below).** A genuine but narrow gap in the observable-behavior
  contract for an out-of-range span.
- **Fog-of-war regression risk.** Because this is a new export route, an Implementation Package must
  confirm it routes through the existing `CellController` filter rather than reading `WorldState`
  directly — the same risk class every new cell-scoped route in this project carries.

## Open Questions

1. **What is the observable behavior for a requested time span partially or wholly outside the
   recorded session range?** `FR-2320`'s own text does not state a rule. The sibling ephemeris-export
   capability (`FR-7410`/`FR-7420`) already resolved an analogous question (clamp partial,
   reject-wholly-out-of-range), but `FR-2320` does not itself commit to reusing that same rule.
   Needs a `07-implementation-planning` design decision — most naturally reusing `FS-121`'s existing
   precedent, but this document does not assert that as settled without an explicit decision.

## Related ADRs

`ADR-0004` (fog-of-war at the boundary) — this Feature's core constraint, per `FR-2320`'s own
Related ADRs field.

## Related Interfaces

None beyond `INT-0006`/`INT-0007` already cited under Interfaces Used.
