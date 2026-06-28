# ADR-0026 — RLock/LAN-scaling contention ceiling

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0026
- **Title:** The per-session `RLock` design's stated ceiling is the existing ~16-participant LAN concurrency model
- **Status:** Accepted

## Context

ADR-0014 records the per-session `RLock` + lazy-clock mechanism as the accepted multiplayer
authority design. GDS-03 Open Question 4 states: "neither this document nor GDS-01 §13 Open
Question 2... states where that serialization starts to matter" as concurrent LAN client count
grows. The architecture review (`reviews/architecture-review.md` §6 findings 1–2) raised this as
a scaling question that "has now passed through three ladder levels unaddressed" (GDS-01, GDS-03,
and the review itself).

## Decision

The per-session `RLock` design's supported ceiling is **the existing documented LAN concurrency
model**: up to 16 notional participants per `build-spec/01` §2 (1–2 White, up to 6 Blue, up to 6
Red, up to 2 Observers). No new numeric ceiling is introduced beyond this — the project owner has
chosen to adopt the already-documented participant count as the stated ceiling rather than commit
to a separate load-test program right now.

## Alternatives Considered

- Establish a new, explicit LAN participant/tab-count ceiling backed by load testing — **not
  adopted now**: no load test has been run; the project owner chose to use the existing sizing
  guideline instead of commissioning new measurement work.
- Replace the single per-session `RLock` with finer-grained locking (e.g. per-resource) — **not
  adopted**: no concrete contention problem has been observed at the documented concurrency model,
  so pre-optimizing without data is not justified.
- Declare no ceiling needed at all — **not adopted**: the project owner chose to state a concrete
  ceiling rather than declare the question out of scope.

## Rationale

`build-spec/01` §2 already constrains intended v1 usage to a small, cooperative LAN/hot-seat group
(≤16 total seats). Adopting that existing, binding sizing constraint as the `RLock` design's
supported ceiling avoids introducing a second, independent sizing claim that could drift from the
build spec, and requires no new load-testing investment to state. If usage patterns are ever
expected to exceed that ceiling, a load test (the deferred alternative above) would be the
appropriate next step at that time — not before.

## Consequences

- LAN-cooperative deployments at or below the documented ~16-participant concurrency model
  (`build-spec/01` §2) are within the `RLock` design's stated supported envelope.
- Deployments intending to exceed that ceiling are explicitly out of the supported envelope until
  a load test is run; this is now a stated boundary rather than a silent gap.
- The clock-lag watchdog (ADR-0019's mechanism) still only signals *sim*-clock lag, not lock
  contention specifically — that distinction remains unchanged by this decision.

## Related

GDS-01 §13 Open Question 2; GDS-03 Open Question 4; `reviews/architecture-review.md` §6 findings
1–2; ADR-0014, ADR-0019; `build-spec/01-context-and-scope.md` §2.
