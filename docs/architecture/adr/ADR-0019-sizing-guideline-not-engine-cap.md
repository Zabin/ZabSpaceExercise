# ADR-0019 — Sizing guideline, not an engine-enforced cap

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0019
- **Title:** ~24-satellite sizing and ≤3-satellite constellations are soft guidelines, not hard limits
- **Status:** Accepted

## Context

Sample vignettes need a sizing target matched to typical White-Cell facilitator hardware, but
user-authored vignettes should not be artificially blocked from scaling up on capable hosts.
GDS-01 §10 states: "~24 satellites is a soft sizing guideline for typical White-Cell facilitator
hardware; user-authored vignettes may scale beyond it on capable hosts. Constellations are capped
at 3 satellites each, individually operated/monitored." `CLAUDE.md` "Key facts" restates the same
guideline.

## Decision

The engine enforces no hard cap on satellite count or constellation size. ~24 satellites and
≤3-satellite, individually-operated constellations are sizing *guidelines* for the
Claude-authored sample vignettes, not validation rules the engine rejects content for violating.
The clock-lag watchdog (`SessionManager._record_catch_up_lag`) is the actual operational signal
that a scenario has outgrown its host, replacing any need for a hard-coded limit.

## Alternatives Considered

- **A hard engine-enforced cap** (reject vignettes above N satellites) — rejected: would block
  legitimate user-authored content on capable hardware for no functional reason; the real
  constraint is host performance, not a domain rule.
- **Constellation aggregation** (managing many satellites as one unit above the 3-sat threshold)
  — explicitly deferred to v2 (`build-spec/01` §3.2), not adopted in v1; constellations remain
  capped at 3, individually controlled.

## Rationale

A soft guideline plus a runtime performance signal (the watchdog) is more flexible than a
hard-coded cap and correctly locates the real constraint (hardware/wall-clock-vs-sim-clock lag),
not an arbitrary content rule.

## Consequences

- Vignette authors targeting larger hosts may exceed 24 satellites; nothing in `content/vignette.py`
  validates against the guideline as a hard rule.
- The clock-lag watchdog must remain accurate and visible to White Cell as the de facto capacity
  signal — this is the actual enforcement mechanism in practice.
- Constellation aggregation above 3 sats remains out of scope until the v2 deferred item is taken
  up.

## Related

GDS-01 §10; `CLAUDE.md` "Key facts"; build-spec/01 §3.1, §3.2 (deferred: constellation aggregation).
