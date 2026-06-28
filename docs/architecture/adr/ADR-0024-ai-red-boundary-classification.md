# ADR-0024 — AI-Red's actor/boundary classification (unresolved)

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0024
- **Title:** Whether AI-Red is permanently internal, or could become a pluggable/external actor with ground-truth-vs-filtered epistemic parity unresolved
- **Status:** Proposed

## Context

ADR-0021 records that AI-Red is placed in the session layer today because it only ever acts
through `SessionAPI`. But GDS-02 §2 Open Question 2 states: "If a future document treats AI-Red as
pluggable/replaceable by an external service (e.g. an LLM-driven Red), that would change this
classification — not resolved here, since no such design exists today." GDS-03 Open Question 2
and a related gap GDS-04 previously had (AI-Red absent from the Role Assignment entity's
description) independently flag the same underlying placement question. Separately, GDS-01 Open
Question 6 asks whether AI-Red's doctrine preset (`redai.py`) "reasons over the same fog-of-war-
filtered Cell View a human Red would see, or over ground truth" — a fairness-relevant question no
document answers either way. The architecture review (`reviews/architecture-review.md` §1 finding
4, §8 findings 1 and 3) treats all of these as corroborating evidence of one load-bearing,
unresolved question rather than three unrelated gaps.

## Decision

**No decision has been made.** AI-Red's classification as internal-only (ADR-0021) is accepted
for the current, shipped implementation, but whether that classification should remain permanent
if a pluggable/external (e.g. LLM-driven) Red is ever introduced is explicitly unresolved. Whether
the current `redai.py` reasons over ground truth or the fog-of-war-filtered view is also
unresolved — no document states it either way.

## Alternatives Considered

Not yet evaluated against each other, because the underlying question (will AI-Red ever become
pluggable/external, and does fairness require epistemic parity with human cells) has not been
decided:

- Keep AI-Red permanently internal, with explicit epistemic parity to the fog-of-war view a human
  Red would see (would require an implementation audit of `redai.py`'s current data access).
- Keep AI-Red internal but explicitly grant it ground-truth access as a deliberate, documented
  design choice (e.g. for difficulty tuning) rather than an oversight.
- Design a pluggable AI-Red boundary now (treating it as a potential external actor) even before
  an LLM-driven implementation exists, to avoid a later breaking change to GDS-02/03/04's actor
  classification.

## Rationale

Not applicable — no decision has been made. Resolving this requires either an implementation
audit (what does `redai.py` actually read today?) or a forward-looking design decision about
whether to support pluggable Red doctrine implementations, both of which are out of scope for a
documentation-only reconciliation pass.

## Consequences

Until resolved: GDS-02 §2, GDS-03 §2.2/Open Question 2, and GDS-01 §13 Open Question 6 all remain
open, and any future GDS-05 (or later) decomposition that touches AI-Red should treat this as a
single load-bearing question, not three independent gaps.

## Related

GDS-01 §13 Open Question 6; GDS-02 §2 Open Question 2; GDS-03 Open Question 2;
`reviews/architecture-review.md` §1 finding 4, §8 findings 1 and 3; ADR-0021.
