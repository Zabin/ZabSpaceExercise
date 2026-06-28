# ADR-0015 — LAN trust model: client-side cell selection, no per-cell authentication

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0015
- **Title:** Cell selection is client-side trust; no per-cell authentication in v1
- **Status:** Accepted

## Context

LAN-cooperative play needs a way to let a browser tab declare "I am Blue" or "I am Red" without
building an identity/authentication system, given the target context is a cooperative training
room where everyone is on the same team learning together. GDS-01 §4 states this directly: "the
cell selector is client-side trust with no per-cell authentication." `CLAUDE.md` "LAN trust model"
documents it as "an explicit v1 trust boundary, not a defect," and names the specific exploit it
accepts: a hostile LAN participant could read another cell's belief state by sending the other
cell's name in the URL.

## Decision

The White/Blue/Red cell selector is client-side and unauthenticated. Fog-of-war filtering still
applies to every cell-scoped response (ADR-0004), but no cryptographic or session-token binding
ties a specific browser connection to a specific cell. The no-cell god-view endpoints
(`/godview`, `/eventlog`, `/save`, `/aar*`, `/objectives`) deliberately expose ground truth without
any cell binding at all.

## Alternatives Considered

- **Per-cell authentication tokens** — explicitly deferred, not rejected: `CLAUDE.md` names
  "Hardening options (per-cell tokens)" as tracked in `docs/FUTURE-WORK.md`, i.e. a known,
  intentionally-deferred upgrade path rather than an unconsidered gap.
- **A full identity-provider integration** — rejected outright: GDS-02 §2 confirms "there is no
  identity provider... in scope" for v1; this would also contradict the offline-first,
  no-LMS-integration constraint (ADR-0018).

## Rationale

The v1 target deployment is "everyone in the room is on the same team learning together"
(`CLAUDE.md`), where the cost of building real per-cell authentication outweighs the actual risk;
documenting the trust boundary explicitly (rather than silently shipping it) lets a deployer make
an informed decision about whether their LAN is sufficiently trusted.

## Consequences

- SpaceSim must only be deployed on a trusted LAN with cooperative participants — a documented
  deployment constraint, not a recommendation.
- `docs/AUDIT-2026-06.md` §D5/§F1 record this finding from a security-audit perspective,
  independently corroborating the same boundary.
- Hardening (per-cell tokens) remains available as a v1.1+ upgrade behind the existing
  `SessionAPI`/`CellController` seam without an architectural rework.

## Related

GDS-01 §4, §10, §12; GDS-02 §8; GDS-03 §4; `CLAUDE.md` "LAN trust model"; `docs/FUTURE-WORK.md`.
