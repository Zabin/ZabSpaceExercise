# ADR-0023 — One-directional subsystem dependency graph

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0023
- **Title:** Subsystem dependencies flow one way only: presentation → session → engine/SSN; nothing depends on content's code
- **Status:** Accepted

## Context

Keeping the engine UI-agnostic and content swappable requires that dependency arrows never point
backward. GDS-03 §3's subsystem dependency diagram shows: Presentation → Session, Session →
Engine, Session → SSN, SSN → Engine, with Session and Engine each having a schema-only (not code)
dependency on Content. The document states explicitly: "No arrow points back toward presentation
or content from the engine or session layer."

## Decision

Subsystem dependencies are strictly one-directional: Presentation depends on Session; Session
depends on Engine and on the mock SSN; the SSN depends on Engine; both Session and Engine depend
on Content & Data only at the schema/data-shape level, never on its code. No subsystem depends
back toward Presentation or Content's code.

## Alternatives Considered

- **Bidirectional engine↔session coupling** (e.g. engine calling back into session for fog-of-war
  decisions) — rejected: would violate `CLAUDE.md` invariant 2 (UI-agnostic engine) and blur the
  fog-of-war boundary (ADR-0004).
- **Content depending on engine/session code** (e.g. vignette loader importing session-layer
  types directly) — rejected: GDS-03 §2.5 states content has "no dependency on the engine,
  session, or presentation subsystems' *code* — only on the data shapes they expect," preserving
  content's swappability (ADR-0007).

## Rationale

A strictly one-directional graph is what makes the engine testable in isolation, the presentation
layer replaceable without touching the engine, and content editable without recompiling/changing
any subsystem's code — the structural property underlying invariants 2 and 6 simultaneously.

## Consequences

- Any proposed feature that would require a back-arrow (e.g. the engine querying the UI for
  display state, or content code importing session types) is a structural violation requiring
  explicit reconsideration of this decision, not a routine implementation choice.
- The import-guard test is the automated enforcement mechanism for the engine's half of this
  graph.

## Related

GDS-03 §3; `CLAUDE.md` invariants 2, 6.
