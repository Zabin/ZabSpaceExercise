# ADR-0018 — Offline-first runtime; Space-Track optional and build-time-only

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0018
- **Title:** Runtime requires no network; Space-Track TLE import is optional and build-time-only
- **Status:** Accepted

## Context

The deployment context (government laptops, possibly air-gapped training environments) requires
the exercise to run without network access. GDS-01 §4 states: "runtime requires no network; the
only network dependency is an *optional* Space-Track TLE import at scenario-build time, with
manual TLE entry as a fallback." This is build-spec/01's pre-existing **Decision D2**
("offline-first; Space-Track only at vignette-build time"), restated and carried forward unchanged
by GDS-01/GDS-02.

## Decision

SpaceSim's runtime (the running exercise) never requires network access. The only network call
anywhere in the system is an optional, build-time-only pull of real TLEs from Space-Track.org,
with manual TLE/Keplerian entry as an always-available offline fallback.

## Alternatives Considered

- **Always-online operation** (e.g. live TLE refresh during a run) — rejected: contradicts the
  offline-capable deployment requirement (`build-spec/01` §1.4, §3.1) and would make the exercise
  dependent on an external service's uptime during live play.
- **No TLE import at all** (fictional assets only) — rejected: GDS-02 §4 records real-TLE
  force-add as a supported data source for added realism; removing it would lose that capability
  entirely rather than just making it optional.

## Rationale

Keeping the one network dependency optional and build-time-only means a training session can
always run regardless of network availability, while still allowing realism-enhancing real-TLE
content when network access exists.

## Consequences

- Space-Track being unavailable or changing its auth model is a named risk (GDS-01 §12),
  mitigated by the bundled-snapshot + manual-entry fallback — never a runtime blocker.
- No other live external system may be introduced without revisiting this decision; GDS-02 §3
  confirms no identity provider, scoring service, or LMS integration exists.

## Related

GDS-01 §4, §9, §12; GDS-02 §1, §4, §6, §8; build-spec/01 Decision D2.
