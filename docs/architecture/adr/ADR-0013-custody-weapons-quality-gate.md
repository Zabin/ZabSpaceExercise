# ADR-0013 — Custody confidence decay and the weapons-quality gate

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0013
- **Title:** Track custody decays without observation; engagement requires a weapons-quality gate
- **Status:** Accepted

## Context

The SDA training loop — "task scarce sensors, build and lose custody, characterize threats"
(GDS-01 §1) — requires custody to be a perishable, gated resource rather than a permanent fact.
GDS-01 §7 names the custody/track-confidence lifecycle: `UNKNOWN → TRACKED(low confidence) →
CHARACTERIZED`, with confidence decaying without observation and potentially falling below "the
weapons-quality gate (`confidence ≥ threshold AND characterized`)." Grounded in `research/
encyclopedia` R105 (custody theory).

## Decision

Custody confidence decays over time without renewed observation; offensive engagement against a
target requires the target to pass a weapons-quality gate — confidence at or above a threshold
*and* characterized, not merely detected.

## Alternatives Considered

- **Permanent custody once acquired** (no decay) — rejected: would remove the SDA tasking-and-
  recontact loop the tool is built to teach (GDS-01 §1), making sensor scarcity irrelevant after
  first detection.
- **A single binary "tracked/not tracked" state with no weapons-quality distinction** — rejected:
  conflates "I know something is there" with "I can responsibly engage it," which is the precise
  distinction real custody/targeting doctrine draws (`research/encyclopedia` R105, R117).

## Rationale

Decay-plus-gate models the real operational tension between sensor scarcity and engagement
authority, which is the SDA loop's pedagogical point.

## Consequences

- `Track` confidence must be recomputed on-demand (decay is a function of elapsed time since last
  observation, not a background tick).
- Any offensive engagement order must validate against the weapons-quality gate before being
  allowed to proceed, tying `Custody`/`Track` into the `OrderSystem`'s validation step (ADR-0005).
- SSN/sensor tasking contention (ADR-0010, `research/encyclopedia` R104) is the lever that
  determines whether a cell can re-establish custody before it decays below the gate.

## Related

GDS-01 §1, §7; GDS-03 §2.1; `research/encyclopedia/R100-index.md` (R105, R117).
