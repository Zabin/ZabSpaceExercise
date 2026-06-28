# ADR-0006 — Sub-stepped deterministic clock

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0006
- **Title:** Clock advances to the next scheduled event, never past it
- **Status:** Accepted

## Context

At high time multipliers (e.g. 600×), a naive large time-step would skip short LEO passes and
break realism. `CLAUDE.md` invariant 5 ("Sub-step the clock") names this directly; GDS-03 §2.1
attributes the responsibility to the `Clock`/`Scheduler`.

## Decision

The simulation clock always advances to the next scheduled event in `Scheduler`'s ordered queue,
never stepping past it, regardless of the configured time multiplier.

## Alternatives Considered

- **Fixed large time-steps for performance at high multipliers** — rejected: would silently skip
  short access windows, undermining the access-window-scheduling lesson at the heart of the tool
  (ADR-0005) and breaking determinism guarantees if events fire out of true order.
- **Variable step size heuristically tuned per scenario** — not adopted; no document describes
  scenario-specific step tuning, and it would reintroduce the same risk of skipping a short pass
  if mistuned.

## Rationale

Correctness (never missing a scheduled event) is prioritized over raw stepping throughput; the
risk table (GDS-01 §12, "Wall-clock + heavy propagation stalls the UI") names the actual
mitigation as off-UI-thread propagation and window caching, not larger steps.

## Consequences

- Performance at high multipliers depends on propagation/window-caching efficiency, not on
  stepping coarsely — this is the documented mitigation path (GDS-01 §12).
- Every event handler must be safe to fire in strict scheduled order with no batching shortcuts.

## Related

GDS-01 §12, GDS-03 §2.1, `CLAUDE.md` invariant 5.
