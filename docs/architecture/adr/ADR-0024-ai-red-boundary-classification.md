# ADR-0024 — AI-Red's actor/boundary classification

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0024
- **Title:** AI-Red stays permanently internal; epistemic parity with human cells is a tracked future-work gap, not resolved now
- **Status:** Accepted

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

An implementation check (`spacesim/session/redai.py`) confirms empirically that `RedDoctrine`
reads `self.mgr.world` (ground truth `WorldState`) directly in `_blue_satellites()`,
`_red_assets()`, and `_first_vulnerable()` — i.e. it currently has full visibility into Blue's
assets, including unpatched cyber vulnerabilities, when choosing doctrine-flavored orders. It does
not read through a fog-of-war-filtered `CellView` the way a human Red operator would.

## Decision

Two sub-questions, decided separately by the project owner:

1. **Boundary classification.** AI-Red's classification as a permanently internal, session-layer
   feature (ADR-0021) is **locked in**. No pluggable/external (e.g. LLM-driven) Red boundary is
   planned; GDS-02 §2/§5, GDS-03 §2.2, and GDS-04's Role Assignment entity should continue to treat
   AI-Red as internal-only with no external-actor interface.
2. **Epistemic parity.** AI-Red's current ground-truth access (confirmed above) is **recorded as a
   known gap, not accepted as deliberate design**. AI-Red should eventually reason over a
   fog-of-war-filtered `CellView` like a human Red operator would. No code change is scheduled now;
   the gap is tracked in [`FUTURE-WORK.md`](../../FUTURE-WORK.md) §1 ("AI-Red fog-of-war parity").

## Alternatives Considered

- Keep AI-Red permanently internal, with explicit epistemic parity to the fog-of-war view a human
  Red would see, implemented immediately — **rejected for now**: parity is the right end state but
  is deferred as future work rather than blocking this documentation pass.
- Keep AI-Red internal but explicitly grant it ground-truth access as a deliberate, documented
  design choice (e.g. for difficulty tuning) — **rejected**: the project owner chose to flag this
  as a gap to close, not a feature to keep.
- Design a pluggable AI-Red boundary now (treating it as a potential external actor) even before
  an LLM-driven implementation exists — **rejected**: the project owner chose to lock in
  internal-only.

## Rationale

The boundary question is locked in because no pluggable/external Red implementation exists or is
planned, and there is no value in carrying speculative pluggability in the architecture for a
feature with no concrete design. The epistemic-parity question is resolved as "fix later, not now"
because closing it requires routing `RedDoctrine` through `CellController`/`SessionAPI` like a
human operator — a behavior change to AI-Red's targeting fidelity, not a documentation
clarification, and out of scope for this reconciliation pass.

## Consequences

- GDS-02 §2 Open Question 2, GDS-03 Open Question 2, and GDS-01 §13 Open Question 6 are resolved:
  AI-Red remains internal (no actor-classification change needed in GDS-02/03/04), and the
  epistemic-parity gap is acknowledged and tracked rather than left ambiguous.
- `FUTURE-WORK.md` §1 carries the AI-Red fog-of-war parity item so a future implementer can pick it
  up: route `RedDoctrine`'s target/vulnerability selection through Red's `CellView` instead of
  `self.mgr.world`.
- Until that future-work item lands, AI-Red retains a documented fidelity advantage over a human
  Red operator — acceptable for v1's PME training context, but no longer an undocumented gap.

## Related

GDS-01 §13 Open Question 6; GDS-02 §2 Open Question 2; GDS-03 Open Question 2;
`reviews/architecture-review.md` §1 finding 4, §8 findings 1 and 3; ADR-0021;
`spacesim/session/redai.py`; `FUTURE-WORK.md` §1.
