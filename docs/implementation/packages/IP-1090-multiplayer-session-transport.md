# IP-1090 — Multiplayer / LAN Session Transport

> **Package ID:** IP-1090
> **Version:** 1.0
> **Status:** ✅ VERIFIED
> **Dependencies:** FS-109
> **Referenced By:** IP-1060 (the White-only clock-control trigger this mechanism serves), [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** the consistent-clock, consistent-lock substrate every cell-facing package reads through
> **Feature Reference:** [FS-109 — Multiplayer / LAN Session Transport](../../features/FS-109-multiplayer-session-transport.md)
> **Supersedes:** none — new package, split out of [IP-1060](IP-1060-white-cell-dashboard.md) v1.0
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py), [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*This package is **new**, split out of `IP-1060-white-cell-dashboard.md` v1.0 per
`docs/feature-planning/05-feature-review.md` Finding F-03, mirroring `FS-109`'s own split from
`FS-106` v1.0. The code citations below are not newly verified — they are the same
`manager.py`/`inprocess.py` evidence `IP-1060` v1.0 (and its superseded predecessor, `IMP-106A`)
already established, reorganized under the Feature boundary FS-109 now owns.*

## Package ID

IP-1090

## Title

Multiplayer / LAN Session Transport

## Objective

Guarantee a session's clock advances exactly once per real-time interval regardless of connected
client count, and that concurrent mutations from multiple clients never corrupt shared session
state — serving hot-seat and LAN-cooperative play identically from one Session object.

**Situation: already implemented, tested, in production use.**

## Feature Reference

[FS-109 — Multiplayer / LAN Session Transport](../../features/FS-109-multiplayer-session-transport.md)

## Requirements Covered

| Req ID | Title (abridged) | How this package covers it |
|---|---|---|
| FR-6310 | Server-authoritative lazy clock shared across connections | `catch_up()`/`_catch_up_locked()` (`manager.py:206`, `:148`), `_wall_anchor`/`_sim_anchor`/`_rate`/`_clock_running` fields — clock state lives once on `SessionManager`, guarded by the per-session lock; every connected client's read triggers the same `catch_up()`, with no per-tab pacing state to desynchronize. |
| FR-6320 | Per-session mutation locking | The per-session lock (`session/inprocess.py`'s `_locked` critical section) serializes all mutating operations against a given session. |
| FR-6410 | One Session object shared across hot-seat and LAN modes | `SessionManager`/`InProcessSession` hold exactly one Session model regardless of connected-client count; no separate "LAN session" data structure or code path exists. |
| NFR-1400 | LAN multiplayer concurrency ceiling is a documented, untested estimate | `_locked` critical section design targets ~16 participants (ADR-0026); no automated load test exists or is required for v1. |

`clock_state()` (`manager.py:210`) is the read-only status query FS-106's dashboard (IP-1060)
consumes but does not itself implement. `list_sessions()` (`session/inprocess.py`) is the session-
discovery surface consulted by the dashboard's session-admin panel.

## Architecture Components

- **C2 Session / Application Layer** — `SessionManager` (`manager.py`), `InProcessSession`
  (`inprocess.py`).

## Interfaces

**INT-0001** (Browser ↔ Operator Console, HTTP transport) — every connected client's poll/action
loop is subject to the catch-up/locking behavior this package implements. **INT-0006** (Operator
Console → Session Layer, the `SessionAPI` seam) — clock-control and mutating requests route through
this seam before reaching this package's mechanism.

## Files to Create

None — capability already implemented.

## Files to Modify

None — this package documents shipped code.

### Reference files

- `spacesim/session/manager.py` — `catch_up()` (`:206`), `_catch_up_locked()` (`:148`),
  `_wall_anchor`/`_sim_anchor`/`_rate`/`_clock_running` fields, `_record_catch_up_lag()` (`:173`),
  `clock_state()` (`:210`).
- `spacesim/session/inprocess.py` — `_locked(sid)` critical-section context manager, `list_sessions()`
  (session discovery).

## Implementation Tasks

All **already complete**:

1. ✅ Implement the server-authoritative lazy clock (`_wall_anchor`/`_sim_anchor`/`_rate`/
   `_clock_running`, guarded by the per-session lock) so clock state lives once, with no per-tab
   pacing to desynchronize, and a clock-lag watchdog (`_record_catch_up_lag`) surfaces real-hardware
   keep-up capability.
2. ✅ Implement `_locked(sid)` wrapping every mutating call against a session.
3. ✅ Implement one Session model serving both hot-seat and LAN-cooperative modes with no
   mode-specific branch.

## Tests to Add

None — covered by `spacesim/tests/test_session.py` (clock/lock behavior).

## Documentation Updates

- Split out of [IP-1060](IP-1060-white-cell-dashboard.md) v1.0; see that package's own v2.0
  Documentation Updates note.
- `ROADMAP.md` and `00-master-build-plan.md` updated to add this package.

## Definition of Done

- [x] Two clients reading concurrently observe an identical simulated clock value within the same
  catch-up cycle.
- [x] Two concurrent mutating requests against the same session apply sequentially with no lost
  update.
- [x] The same action sequence produces identical `WorldState` via hot-seat or multi-LAN-client
  play.

## Verification Checklist

- [x] `manager.py:148,173,206,210` and `inprocess.py`'s `_locked`/`list_sessions` read and confirmed
  against the current tree.
- [x] `spacesim/tests/test_session.py` present and green.

## Dependencies

- **Upstream:** None — self-contained session-layer module.
- **Downstream:** [IP-1060](IP-1060-white-cell-dashboard.md) (the White-only clock-control trigger
  this mechanism propagates for).
- **Build-sequencing:** None — already shipped.

## Risks

- The ~16-participant concurrency ceiling (NFR-1400/ADR-0026) is untested — a larger cohort session
  is the most likely real-world scenario to expose it.
- This package's split from IP-1060 v1.0 creates a cross-package seam: a future change to who may
  trigger a clock-control request must be coordinated between both packages.

## Rollback Considerations

Rollback surface: `spacesim/session/manager.py`'s clock-anchor fields and `session/inprocess.py`'s
locking/discovery surface. Clock-anchor fields participate in the save/resume schema (IP-1100); a
revert requires re-verification against `test_session.py` and the determinism property test before
landing.
