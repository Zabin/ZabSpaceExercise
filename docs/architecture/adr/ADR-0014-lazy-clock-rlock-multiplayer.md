# ADR-0014 — Server-authoritative lazy clock + per-session RLock

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0014
- **Title:** Multiplayer authority via a server-authoritative lazy clock and one RLock per session
- **Status:** Accepted

## Context

LAN-cooperative play connects multiple browser tabs/machines to one session; the server must
remain the single source of truth and the single clock owner regardless of how many clients are
connected (GDS-01 §8). GDS-03 §2.2 names the mechanism: a lazy clock (`_wall_anchor`,
`_sim_anchor`, `_rate`, `_clock_running`) with `catch_up()` invoked lazily on every read, plus a
per-session `RLock` wrapping every mutation, so the clock "advances exactly once regardless of
connected-tab count."

## Decision

`SessionManager` owns a server-authoritative lazy clock: time only actually advances when
computed lazily at read-time (`catch_up()`), re-anchored on every `start`/`rewind`/`undo`/
`advance` so the wall clock can never snap the sim backward. Every mutation to a session is
serialized through one `RLock` per session.

## Alternatives Considered

- **Per-client local clocks with periodic reconciliation** — rejected: would risk the clock
  drifting differently per client and complicate the single-clock-owner guarantee GDS-01 §10
  requires ("White Cell alone owns pause/resume/rewind/branch").
- **A background ticking thread that advances time eagerly** — rejected: lazy catch-up-on-read
  avoids needing a background thread per session entirely, and keeps the clock's only mutation
  points aligned with the explicit re-anchor events (start/rewind/undo/advance).
- **No locking, optimistic concurrency** — rejected: multiple simultaneous LAN clients mutating
  the same session without serialization risks corrupting the single ordered `EventLog`
  (ADR-0002's determinism guarantee).

## Rationale

Lazy catch-up plus one lock per session is the minimal mechanism that preserves "the server is the
single source of truth and the single clock owner" (GDS-01 §8) without requiring a background
scheduler thread per session.

## Consequences

- Every read-path in `inprocess.py` calls `catch_up(sid)` first, and every mutation wraps in
  `_locked(sid)` — a structural rule, not just a convention (GDS-03 §2.2).
- No stated ceiling exists for `RLock` contention under many concurrent LAN clients — flagged as
  its own unresolved question; see ADR-0026.
- Re-anchoring on every clock-changing operation is what prevents rewind from "snapping" time
  incoherently for connected clients.

## Related

GDS-01 §8; GDS-03 §2.2; `CLAUDE.md` "Multiplayer workflow."
