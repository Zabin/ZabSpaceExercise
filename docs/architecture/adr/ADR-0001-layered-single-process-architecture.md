# ADR-0001 — Layered single-process architecture

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0001
- **Title:** Layered single-process architecture (engine / session / presentation / content + mock SSN)
- **Status:** Accepted

## Context

SpaceSim must run a deterministic simulation, enforce per-cell fog-of-war, serve one or more
browser clients, and keep scenario content editable without touching code. GDS-03 §1 records the
as-built decomposition: a **deterministic core** (`spacesim/engine/`), a **session/application
layer** (`spacesim/session/`) that is the one seam between the engine and everything else, a
**presentation** layer (`spacesim/ui_web/`) that is a thin client of the session layer, and
**content & data** (`spacesim/content/` + on-disk files). A fifth element, the mock Space
Surveillance Network, sits inside the engine/session boundary but is called out as its own
subsystem because of its external-service *flavor* (GDS-03 §1).

## Decision

SpaceSim is built as a **layered, single-process application** with one hard internal seam
(`SessionAPI`) between the deterministic engine and everything outside it. All four/five elements
run inside one FastAPI server process; no subsystem is a separately deployed service.

## Alternatives Considered

- **Microservice/multi-process decomposition** (e.g. engine as a separate process from the web
  server) — rejected implicitly: GDS-02 §1 states SpaceSim is "a single FastAPI server process,"
  and no document proposes splitting it. A multi-process design would also complicate the
  determinism guarantee (single ordered `EventLog`, single RNG stream).
- **No internal layering** (engine and UI code interleaved) — rejected: `CLAUDE.md` invariant 2
  ("UI-agnostic engine") and the import-guard test (`test_import_guard.py`) exist specifically to
  prevent this.

## Rationale

A single process with a layered internal seam gives determinism (one ordered event stream) for
free, keeps the engine UI-agnostic and therefore testable/swappable, and matches the deployment
model (single-machine hot-seat or LAN-cooperative against one server, `build-spec/01` §1.4).

## Consequences

- The engine can never depend on session/presentation code (enforced by the import guard).
- Scaling beyond one process (e.g. a dedicated multiplayer server pool) is out of scope for v1 and
  would require revisiting this decision — see GDS-03 Open Question 4 / ADR-0026 (RLock/LAN-scaling
  ceiling), which is a direct consequence of staying single-process.
- Adding a subsystem means deciding which of the four layers (or the SSN) owns it; GDS-03 §2
  exists specifically to make that decision auditable.

## Related

GDS-02 §1, GDS-03 §1 (`Mermaid` component diagram), `CLAUDE.md` invariants 1–2, 6.
