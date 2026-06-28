# ADR-0010 — Mock SSN is internal, not an external system

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0010
- **Title:** The mock Space Surveillance Network is fully internal to SpaceSim, despite its external-service flavor
- **Status:** Accepted

## Context

`build-spec/08-ssn.md` §17 describes a per-cell `SSNNetwork` that operators "request and wait"
against — structurally resembling an external sensor-tasking service. GDS-02 §1 Open Question 1
(in its prior revision) asked whether this placed the SSN across the system boundary; GDS-02 §1
records the question as **resolved**: "no real external system behind it, so it sits inside the
boundary, not across it." GDS-03 §2.3 elaborates the SSN as its own internal subsystem precisely
because of this external *flavor*, grounded in `research/encyclopedia` R118 (space surveillance
networks).

## Decision

The mock SSN runs entirely inside the same FastAPI process as the rest of the engine, with no real
external system behind it. It is modeled as a fifth internal subsystem (alongside engine, session,
presentation, content) rather than as a boundary-crossing external actor or service.

## Alternatives Considered

- **Modeling the SSN as an external service** (even if mocked) — rejected: GDS-02 §1 found "no
  real external system behind it"; treating it as external would misrepresent the boundary and
  complicate the system-context diagram with a non-existent dependency.
- **Folding the SSN into the generic sensor-tasking path with no distinct subsystem identity** —
  rejected: GDS-03 §2.3 calls it out separately specifically because its request-and-wait texture
  and dispersion-preset/turnaround-SLA logic are distinct enough to warrant its own
  responsibilities/interfaces/ownership entry, even though it shares the engine's clock/event
  substrate.

## Rationale

Naming the SSN as a distinct internal subsystem captures its real architectural shape (event-driven
inside the deterministic substrate, with its own staged-state ownership) without inventing a
boundary crossing that doesn't exist.

## Consequences

- `world.ssn_staged` is owned exclusively by the SSN subsystem; no separate network/IPC path
  exists for SSN requests — they ride the same `CellController`/`SessionAPI` path as other sensor
  tasking (GDS-03 §2.3).
- Future designs that want a *pluggable* or *real* external SSN (sensor-tasking against a real
  network) would need to revisit this decision; no such design exists today.

## Related

GDS-02 §1 (Open Question 1, resolved); GDS-03 §2.3; build-spec/08-ssn.md §17;
`research/encyclopedia/R100-index.md` (R118).
