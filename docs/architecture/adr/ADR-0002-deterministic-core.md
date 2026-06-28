# ADR-0002 — Deterministic core

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0002
- **Title:** Deterministic core keyed on (initial state, ordered event log, seed)
- **Status:** Accepted

## Context

The exercise must support exact rewind/undo and branch-from-rewind (for AAR replay/scrub/
branch-compare), and reproducible training outcomes across runs. GDS-01 §7 states the engine is
"deterministic on `(initial_state, ordered eventlog, seed)`," and `CLAUDE.md` invariant 1 names
this the property that "is what makes rewind/undo/branch exact," gated permanently by the
Phase-1 determinism property test. Originally recorded as build-spec/01 Decision D4.

## Decision

The simulation core (`spacesim/engine/`) is deterministic: `(initial_state, ordered eventlog,
seed) → byte-identical state`, with no wall-clock reads and no uncontrolled RNG anywhere in the
engine — the only randomness source is a single seeded `SeededRng` (GDS-03 §2.1).

## Alternatives Considered

- **Non-deterministic / wall-clock-driven simulation** — rejected: would make rewind/replay
  approximate rather than exact, undermining AAR branch-compare (GDS-01 §7) and making the
  Phase-1 property test impossible to write meaningfully.
- **Per-subsystem independent RNG streams** — rejected: complicates reproducing a byte-identical
  state from `(initial_state, eventlog, seed)` alone; a single seeded stream keeps the contract
  to three inputs.

## Rationale

Determinism is the one property every other replay/rewind/branch/AAR feature depends on; building
it in from the core out is cheaper than retrofitting it once non-determinism has leaked into
event ordering or random outcomes.

## Consequences

- No subsystem in `engine/` may read the wall clock or call uncontrolled `random` — enforced by
  the AST-scanning `test_import_guard.py`.
- Every event-producing action must be appended to the ordered `EventLog`, including pure-preview
  paths' explicit avoidance of mutation (`telemetry.py`, `scene.py`, `dry_run()`).
- Any future high-fidelity propagator or external data feed must still resolve to a deterministic
  function of the three inputs, constraining future architecture choices (e.g. GDS-01 §11's
  "higher-fidelity model" deferral).

## Related

GDS-01 §7, GDS-03 §2.1/§4, `CLAUDE.md` invariant 1, build-spec/01 Decision D4.
