# ADR-0004 — Fog-of-war enforced at the session-layer boundary

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0004
- **Title:** Fog-of-war filtering lives at `SessionAPI`/`CellController`, never in the UI or engine
- **Status:** Accepted

## Context

Red and Blue must only ever see their own belief state, not ground truth (the core "operate on
belief, not ground truth" training lesson, GDS-01 §12 risk table). GDS-03 §2.2 names
`CellController` as "the fog-of-war boundary," rendering each cell's `CellView`/`TrackCatalog`
from custody, never ground truth.

## Decision

Fog-of-war filtering is enforced exactly once, at the `CellController`/`SessionAPI` boundary
inside the session layer. The engine (§2.1) has no concept of "cell"; the presentation layer
(§2.4) "enforces no fog-of-war logic of its own" and trusts the session layer's output verbatim.

## Alternatives Considered

- **Filtering in the UI** (client renders only what it's "supposed to" see) — rejected: a
  malicious or buggy client could simply read the unfiltered payload; `CLAUDE.md` invariant 3
  states filtering must happen server-side at this exact boundary.
- **Filtering inside the engine** (engine returns per-cell views directly) — rejected: would give
  the supposedly cell-agnostic deterministic core a concept of "cell," coupling physics/state
  logic to exercise role structure (GDS-03 §2.1 "out of scope: fog-of-war filtering").

## Rationale

A single, server-side filtering point is the only place this property can be tested and
guaranteed; pushing it anywhere else (client or engine) either weakens the guarantee or pollutes
an unrelated subsystem's responsibility.

## Consequences

- Every cell-scoped endpoint must pass through `CellController`; the no-cell god-view endpoints
  (`/godview`, `/eventlog`, `/save`, `/aar*`, `/objectives`) are a deliberate, documented exception
  to this rule, not an oversight (GDS-02 §9, GDS-03 §4 — see ADR-0015 for the related LAN trust
  decision).
- Tests at the API boundary are the canonical fog-of-war regression gate (GDS-01 §12).
- AI-Red's epistemic parity with this boundary (does it reason over filtered or ground-truth
  state?) is left genuinely open — see ADR-0024 and GDS-01 Open Question 6.

## Related

GDS-02 §9, GDS-03 §2.2/§4, `CLAUDE.md` invariant 3.
