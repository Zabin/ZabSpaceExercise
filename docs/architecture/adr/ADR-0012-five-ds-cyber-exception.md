# ADR-0012 — Five-D's effect taxonomy with a cyber exception

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0012
- **Title:** Counterspace effects resolve into five categories (deceive/disrupt/deny/degrade/
  destroy); cyber is the one window-independent exception
- **Status:** Accepted

## Context

The tool teaches "weighing counterspace effects across the escalation ladder... with attention to
reversibility, attribution, and debris" (GDS-01 §1). GDS-03 §2.1 names the `EffectResolver` seam's
job as resolving orders into "the five-D effect categories (deceive/disrupt/deny/degrade/destroy)
plus the cyber exception (window-independent, resolved against `{access_vector, success_prob,
persistence, patchable}`)." `CLAUDE.md` "Key facts" restates the same taxonomy. Grounded in
`research/03-counterspace-taxonomy.md` and `research/encyclopedia` R115/R116/R117.

## Decision

Every offensive/defensive effect resolves into exactly one of five categories (deceive, disrupt,
deny, degrade, destroy), each gated behind the relevant access-channel window — except cyber,
which resolves window-independently against `{access_vector, success_prob, persistence,
patchable}` rather than through a window-gated channel.

## Alternatives Considered

- **Treating cyber as just another window-gated access channel** — rejected: cyber attacks (e.g.
  a pre-positioned payload triggered later) do not require a live geometric access window at
  execution time the way EW/kinetic/RPO effects do; forcing it through the same gate would
  misrepresent real cyber-operations doctrine (`research/encyclopedia` R116).
- **A flatter effect model** (e.g. binary success/fail with no escalation-ladder structure) —
  rejected: the escalation-ladder framing (deceive→disrupt→deny→degrade→destroy) is itself a
  named training objective (GDS-01 §1), not an implementation detail.

## Rationale

The five-D ladder mirrors real counterspace doctrine and gives operators a graduated set of
reversible-to-irreversible choices to weigh; carving cyber out as window-independent matches how
cyber operations actually work (persistent compromise, not a live geometric pass).

## Consequences

- `EffectResolver` must special-case cyber's resolution path distinctly from the other four/five
  channels' window-gated path.
- The architecture review's "six access channels vs. cyber as a full channel" finding was checked
  against this exact text and found not to be a real inconsistency (GDS-03's Review reconciliation
  section) — the exception is already stated adjacent to the five-D bullet.

## Related

GDS-01 §1; GDS-03 §2.1; `CLAUDE.md` "Key facts"; `research/03-counterspace-taxonomy.md`;
`research/encyclopedia/R100-index.md` (R115, R116, R117).
