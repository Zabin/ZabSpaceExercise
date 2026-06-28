# ADR-0003 — SessionAPI as the single seam out of the engine

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0003
- **Title:** UI-agnostic engine with `SessionAPI` as the one seam to everything outside it
- **Status:** Accepted

## Context

The engine must stay testable and swappable independent of presentation technology
(`CLAUDE.md` invariant 2). GDS-03 §2.2 describes the session layer as "the one seam between the
engine and everything outside it," with `SessionAPI` as the in-process call interface that
"doubles as the HTTP API's backing implementation."

## Decision

`spacesim/engine/` imports no UI or transport code. All access to the engine from presentation,
multiplayer transport, or AI-Red goes through `SessionAPI` (via `SessionManager`/`CellController`)
— no subsystem outside the session layer calls into the engine directly.

## Alternatives Considered

- **Presentation calling the engine directly** (bypassing a session seam) — rejected: would
  duplicate fog-of-war and clock-authority logic into the UI layer, violating invariant 3 and
  GDS-03 §2.4's explicit "out of scope: any simulation logic" for presentation.
- **Multiple seams** (e.g. a separate API for AI-Red vs. human operators) — rejected: GDS-03 §2.2
  explicitly routes `redai.py` "through the same `SessionAPI` path a human Red would use," so
  AI-Red is not a privileged internal caller with its own interface.

## Rationale

One seam means one place to enforce determinism-preserving call ordering, fog-of-war, and
multiplayer locking; it also means the session layer — not the engine — is the only thing that
needs to know about wall-clock time, since GDS-03 §2.2 states the session layer is "the *only*
place in the whole system permitted to read the wall clock."

## Consequences

- Any new client type (a future native app, a CLI tool, a different AI doctrine) integrates by
  calling `SessionAPI`, not by acquiring engine access another way.
- The import-guard test enforces this structurally, not just by convention.
- AI-Red's classification as "internal because it only ever acts through `SessionAPI`" (GDS-03
  Open Question 2) is itself downstream of this decision — see ADR-0024.

## Related

GDS-03 §1, §2.1–§2.2, `CLAUDE.md` invariant 2, `design/01-architecture-overview.md`.
