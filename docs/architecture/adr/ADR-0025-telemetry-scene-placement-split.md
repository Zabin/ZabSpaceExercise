# ADR-0025 — telemetry.py vs. scene.py subsystem placement (unresolved)

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0025
- **Title:** Whether pure, read-only render/diagnostic helpers belong to the engine or the session layer
- **Status:** Deferred

## Context

`telemetry.py` lives in `spacesim/engine/` while the structurally similar `scene.py` lives in
`spacesim/session/`. GDS-03 Open Question 3 states both are "pure, read-only, replay-safe, and
render belief/diagnostic views rather than mutating state," yet they live in different layers with
no stated placement rule distinguishing them. GDS-03 explicitly "followed the existing file
locations rather than reconciling them into one placement rule." The architecture review
(`reviews/architecture-review.md` §2 finding 2) independently reached the same flag, which GDS-03
records as corroborating weight that this is a real seam, not a false positive.

## Decision

**No decision has been made.** The current file locations (`telemetry.py` in engine,
`scene.py` in session) are accepted as the as-built state, but no rule has been articulated for
*why* one belongs to one layer and not the other, and no decision has been made on whether to
reconcile them into a single placement going forward.

## Alternatives Considered

Not yet evaluated, since no placement rule has been proposed:

- Move both to the engine (rationale candidate: both are pure functions of `WorldState`, with no
  dependency on session-layer concepts like fog-of-war or cell identity at the point they execute).
- Move both to the session layer (rationale candidate: both exist specifically to serve
  presentation-facing belief/diagnostic views, which is a session-layer concern per GDS-03 §2.2).
- Leave them split, with an explicit rule for future pure-render helpers (e.g. "engine if it needs
  no cell context, session if it needs to know which cell is asking").

## Rationale

Not applicable — this is a code-organization question, not a behavioral one (GDS-03 explicitly
calls it "a possible future code-organization cleanup, not a behavioral issue"), and resolving it
requires a placement-rule decision outside a documentation-only pass.

## Consequences

Until resolved: a future implementer adding a third pure-render/diagnostic helper has no stated
rule to follow, and may either compound the inconsistency or accidentally invent a third
inconsistent placement.

## Related

GDS-03 Open Question 3; `reviews/architecture-review.md` §2 finding 2.
