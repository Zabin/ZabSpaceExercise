# ADR-0009 — Moderate orbital fidelity (Keplerian + J2, sgp4 for TLEs)

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0009
- **Title:** Moderate-fidelity orbital model (Keplerian + J2, sgp4 for real TLEs) chosen over high-fidelity propagation
- **Status:** Accepted

## Context

A high-fidelity astrodynamics model (full perturbation set, precise RF link budgets) is more
expensive to build and validate than the training objectives require. GDS-01 §11 states the
assumption directly: "The orbital fidelity model (Keplerian + J2, moderate fidelity) is assumed
sufficient for the training objectives in §1; a higher-fidelity model is a deferred upgrade behind
existing interfaces, not a v1 requirement." Grounded in `research/encyclopedia` R1xx (orbital
mechanics tier, R101) and `research/04-orbital-mechanics-primer.md`.

## Decision

Orbits are propagated with a moderate-fidelity model: Keplerian elements + J2 perturbation for
fictional assets, sgp4 for real-TLE-seeded assets — both behind a `Propagator` seam (GDS-03 §2.1)
so a higher-fidelity model can be substituted later without touching callers.

## Alternatives Considered

- **High-fidelity propagation** (full perturbation set: drag, J3/J4, third-body, SRP, precise RF
  link budgets) — deferred, not rejected outright: `research/encyclopedia` R1xx topics
  (`perturbations.py`'s pure functions) already exist as building blocks behind the seam, but
  GDS-01 §11 explicitly treats full integration as a v1.1+ upgrade, not a requirement.
- **A simplified circular-orbit-only model** — rejected: would not support the access-window and
  geometry realism the tool's core training objective depends on (GDS-01 §1).

## Rationale

Moderate fidelity is "sufficient for the training objectives" while staying within the hardware
floor (`build-spec/01` §3.3) and avoiding the validation burden of a full high-fidelity model;
the `Propagator` seam preserves the upgrade path without committing to it now.

## Consequences

- STK-savvy users may find the moderate-fidelity orbits "look wrong" — a named, accepted risk
  (GDS-01 §12) mitigated by validating against Skyfield and documenting the fidelity level
  explicitly rather than hiding it.
- `perturbations.py`'s drag/J3/J4/third-body/SRP functions exist as pure, composable building
  blocks for a future high-fidelity propagator but are not wired into the default path today.
- Any future fidelity upgrade must preserve the existing `Propagator`/`AccessProvider`/
  `EffectResolver` seam contracts.

## Related

GDS-01 §11, §12; GDS-03 §2.1; `research/encyclopedia/R100-index.md` (R101); `research/
04-orbital-mechanics-primer.md`.
