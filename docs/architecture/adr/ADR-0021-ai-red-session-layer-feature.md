# ADR-0021 — AI-Red is a session-layer feature, not a privileged internal actor

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0021
- **Title:** `redai.py` is placed in the session layer and acts only through `SessionAPI`
- **Status:** Accepted

## Context

Red may be played by a doctrine-flavored AI preset instead of human operators (GDS-01 §2, §8).
GDS-03 §2.2 places `redai.py` inside the session layer, "generat[ing] orders on Red's behalf
through the same `SessionAPI` path a human Red would use — not a privileged internal actor."

## Decision

AI-Red is implemented as a session-layer feature (`spacesim/session/redai.py`) that issues orders
through the same `SessionAPI` surface a human Red operator would use, rather than as a privileged
caller with direct engine access or a distinct internal subsystem.

## Alternatives Considered

- **AI-Red with direct engine access** (bypassing `SessionAPI`) — rejected: would violate
  ADR-0003 (the single-seam rule) and create a second, privileged path into the engine that human
  operators don't have.
- **AI-Red as its own subsystem** (a sixth box alongside engine/session/presentation/content/SSN)
  — rejected: GDS-03 §2.2 treats it as one of the session layer's several responsibilities
  (alongside `SessionManager`, `CellController`, `scene.py`, `aar.py`), not as an independently
  decomposed subsystem with its own ownership/interfaces section.

## Rationale

Routing AI-Red through the exact same `SessionAPI` path as a human operator guarantees it cannot
accidentally bypass any validation, fog-of-war, or plan-first commanding rule that applies to
humans — "fairness by construction" rather than by separate enforcement.

## Consequences

- Any rule change to `SessionAPI` (validation, windowing, fog-of-war) automatically applies to
  AI-Red without separate code paths to keep in sync.
- This placement decision is explicitly *not final*: GDS-02 §2 Open Question 2, GDS-03 Open
  Question 2, and a related GDS-04 gap all flag that a future pluggable/external AI-Red (e.g.
  LLM-driven) could change this classification — that is recorded as its own unresolved decision,
  ADR-0024, not contradicted by this one.
- Whether AI-Red, once inside `SessionAPI`, reasons over the same fog-of-war-filtered view a human
  Red sees or over ground truth is a separate, also-unresolved question (GDS-01 Open Question 6,
  folded into ADR-0024).

## Related

GDS-01 §2, §8; GDS-03 §2.2.
