# ADR-0005 — Plan-first commanding model

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0005
- **Title:** Operators plan commands; execution happens at the next valid access window
- **Status:** Accepted

## Context

Real satellite operations cannot command, observe, or attack on demand — only when orbital
geometry and ground access permit (`build-spec/01` §1.1, the founding problem statement). GDS-01
§10 names "plan-first commanding" as an operational constraint; `CLAUDE.md` invariant 4 makes it
load-bearing: "Operators *plan* commands that execute at the next valid access window... they
never act instantly on perfect knowledge."

## Decision

All operator commands and sensor tasking are **planned**, not executed immediately. Execution
happens at the next valid access window via ground uplink, ISL relay, or a stored program,
enforced by the engine's `OrderSystem` (validate → window → execute, GDS-03 §4).

## Alternatives Considered

- **Instant/on-demand commanding** (command executes the moment it's issued) — rejected: this is
  the precise mechanic the tool exists to teach against (`build-spec/01` §1.1); it would
  eliminate the access-window scheduling lesson entirely.
- **A separate "instant override" mode for White Cell convenience** — not adopted; no document
  proposes one, and the cyber action is the only documented exception, and even it is
  window-*independent* rather than instant in the sense of bypassing validation (GDS-03 §2.1).

## Rationale

This is the central training mechanic ("space operations are fundamentally scheduling against
orbital geometry," GDS-01 §1); relaxing it anywhere would undermine the tool's purpose.

## Consequences

- Every order type must carry a window-computation step (`AccessProvider`) before execution.
- The UI's dry-run preview (`OrderSystem.dry_run()`) exists specifically to let operators see
  "why can't I?" before committing a plan (GDS-03 §2.1, §2.4).
- The cyber exception (window-independent execution, gated instead by `{access_vector,
  success_prob, persistence, patchable}`) is a deliberate, narrow carve-out — see ADR-0012.

## Related

GDS-01 §10, GDS-03 §2.1/§4, `CLAUDE.md` invariant 4, build-spec/01 §1.1.
