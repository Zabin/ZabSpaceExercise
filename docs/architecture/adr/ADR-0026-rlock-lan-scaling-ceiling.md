# ADR-0026 — RLock/LAN-scaling contention ceiling (unresolved)

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0026
- **Title:** No stated ceiling for per-session `RLock` contention under many concurrent LAN clients
- **Status:** Deferred

## Context

ADR-0014 records the per-session `RLock` + lazy-clock mechanism as the accepted multiplayer
authority design. GDS-03 Open Question 4 states: "neither this document nor GDS-01 §13 Open
Question 2... states where that serialization starts to matter" as concurrent LAN client count
grows. The architecture review (`reviews/architecture-review.md` §6 findings 1–2) raised this as
a scaling question that "has now passed through three ladder levels unaddressed" (GDS-01, GDS-03,
and the review itself).

## Decision

**No decision has been made.** The `RLock`-per-session mechanism (ADR-0014) is accepted as the
multiplayer-authority design, but no document states a concrete participant-count, tab-count, or
contention ceiling at which it would need to change.

## Alternatives Considered

Not yet evaluated, since no sizing target has been set to evaluate against:

- Establish an explicit LAN participant/tab-count ceiling (mirroring the existing ~24-satellite
  single-host sizing guideline, ADR-0019) backed by load testing.
- Replace the single per-session `RLock` with finer-grained locking (e.g. per-resource) if/when a
  concrete contention problem is observed, rather than pre-optimizing without data.
- Accept the current design as sufficient for the documented concurrency model (up to 16 notional
  participants, `build-spec/01` §2) without further sizing work, on the basis that 16 RLock
  acquisitions per session is unlikely to be a bottleneck — this has not been measured or decided.

## Rationale

Not applicable — resolving this requires a sizing decision (and likely a load test), which is
outside the scope of a documentation reconciliation pass.

## Consequences

Until resolved: LAN-cooperative deployments beyond the documented ~16-participant concurrency
model (`build-spec/01` §2) have no stated guarantee of acceptable performance, and the clock-lag
watchdog (ADR-0019's mechanism) only signals *sim*-clock lag, not lock-contention specifically.

## Related

GDS-01 §13 Open Question 2; GDS-03 Open Question 4; `reviews/architecture-review.md` §6 findings
1–2; ADR-0014, ADR-0019.
