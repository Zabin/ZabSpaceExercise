# ADR-0016 — Single point of time control

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0016
- **Title:** White Cell alone owns clock control; operators never advance time
- **Status:** Accepted

## Context

A multi-seat exercise needs exactly one party deciding when time advances, or pauses/rewinds,
to keep the exercise coherent across Red/Blue/White/Observer roles. GDS-01 §10 names this an
operational constraint: "White Cell alone owns pause/resume/rewind/branch; operators never control
the clock." GDS-02 §9 restates it as a structural property of every information flow: "Only the
White Cell flow can advance/pause/rewind time; all other inbound flows are time-stamped against
whatever the current sim time is."

## Decision

Clock-control operations (pause/resume/rewind/branch/time-multiplier) are reachable only through
the White Cell's session-layer calls; Blue/Red/Observer inbound flows are always time-stamped
against the current sim time and never themselves advance it.

## Alternatives Considered

- **Per-operator local time control** (e.g. each operator can fast-forward their own view) —
  rejected: would break the single-source-of-truth model (GDS-01 §8) and make multi-seat
  coordination incoherent, since orders are resolved against one shared sim time.
- **A voting/consensus model for clock control among connected clients** — not proposed in any
  document; out of scope.

## Rationale

Exactly one clock owner is the simplest model that keeps every cell's belief state, custody decay,
and scheduled events consistent with a single timeline — consistent with the determinism contract
(ADR-0002), which assumes one ordered event stream.

## Consequences

- The White-only pause/resume toolbar button and `/api/sessions/{sid}/clock` endpoint are the only
  client-facing surface for clock control (`CLAUDE.md` "Multiplayer workflow").
- This decision composes directly with the lazy-clock/RLock mechanism (ADR-0014): re-anchoring
  happens exactly at White Cell's clock-changing calls, never at an operator's read.

## Related

GDS-01 §10; GDS-02 §9; `CLAUDE.md` "Multiplayer workflow."
