# R306 — Operational Assessment

> **Document ID:** R306
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R310](R310-effects-based-operations.md)
> **Referenced By:** DOM-002
> **Produces:** the doctrinal vocabulary distinguishing output/performance/effect measures the existing objective-flip model conflates
> **Feature Mapping:** FS-201 (Competency Assessment)
> **Related Topics:** [R310](R310-effects-based-operations.md) (Effects-Based Operations), DOM-002 §3 ("why binary objective-flip is
> insufficient" — the exact gap this topic names doctrinally)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 1

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-002 §3 already states, in engineering terms, that binary objective-flip success/failure is
insufficient evidence of "did the cell win" vs. "did the cell demonstrate competency." This topic
supplies the formal military-doctrine vocabulary (measures of performance vs. measures of
effectiveness) for that exact distinction, so a future assessment feature is built on a recognized
doctrinal framework rather than a bespoke one invented from scratch.

## 2. Scope

Covers: the MOP/MOE/outcome hierarchy and assessment as a continuous process. Does **not** cover:
the cascading-effects model MOE presupposes (that is [R310](R310-effects-based-operations.md),
Effects-Based Operations) or the specific competency-assessment rubric design (FS-201 territory,
out of scope for this doctrinal topic).

## 3. Concepts

**Measures of Performance (MOP) vs. Measures of Effectiveness (MOE).** Joint doctrine defines a MOP
as a criterion used to assess friendly actions tied to measuring task accomplishment, and a MOE as a
criterion used to assess changes in system behavior, capability, or operational environment tied to
measuring attainment of an end state, achievement of an objective, or creation of an effect
([JP 3-0, *Joint Operations*](https://irp.fas.org/doddir/dod/jp3_0.pdf), via the JP 3-0/5-0 family's
assessment chapter). A MOP asks "was the task executed as planned" (a binary, output-level check —
did the engagement order fire, did the jam footprint cover the target); a MOE asks "did the task
achieve the intended operational effect" (did the engagement actually deny the adversary capability,
did the jam meaningfully degrade adversary SDA). The engine's current objective-flip is closer to a
MOP than a MOE — it confirms a task-level condition was met, not that the deeper operational effect
([R310](R310-effects-based-operations.md)) was achieved.

**Measures of Outcome.** A further level beyond MOE: did the overall campaign/strategic objective
advance, independent of whether any single operation's MOE was met (an operation can meet its MOE
and still not advance the strategic outcome if circumstances changed). Relevant to [R301](R301-campaign-design.md)'s campaign-
level framing: a mission-set's overall success is an outcome-level judgment, not reducible to any one
vignette's objective-flip.

**Assessment as a continuous process, not an end-of-mission verdict.** Joint assessment doctrine
treats assessment as conducted throughout an operation (are early indicators trending toward or away
from the intended effect), not only as a final pass/fail — this is the doctrinal argument for why
DOM-002's proposed measurement dimensions (custody quality, window discipline, etc., tracked across
the exercise) are a more faithful assessment design than a single end-state check.

### Sources

- *JP 3-0, Joint Operations* (Joint Chiefs of Staff; assessment chapter, MOP/MOE definitions) — [live](https://irp.fas.org/doddir/dod/jp3_0.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://irp.fas.org/doddir/dod/jp3_0.pdf)
  · accessed 2026-06-27.

## 4. Operational Context

Joint doctrine's MOP/MOE/outcome framework exists precisely because "the task was completed" and
"the operation achieved its purpose" are routinely different answers in real operations — assessment
doctrine treats conflating them as a known, named failure mode, which is exactly the failure mode
DOM-002 §3 independently rediscovered from first principles for this simulator's objective-flip
model.

## 5. Implementation Guidance

- **A future DOM-002-derived assessment feature should map its dimensions onto this MOP/MOE
  distinction explicitly** — e.g., "window discipline" and "custody quality" are closer to MOPs
  (was the task executed well); a future "did the cell's actions actually deny Red's objective"
  dimension would be a MOE, and the two should be reported and labeled distinctly, not blended into
  one score (consistent with DOM-002 §5's rubric-not-single-score principle).
- **A vignette's `objectives` block (the engine's literal flip-condition) should be understood and
  documented as an MOP-level proxy for a MOE the vignette designer actually cares about** — per [R305](R305-mission-analysis.md),
  a vignette author should be able to state the intended MOE an objective is a proxy for, so a future
  assessment feature inherits that traceability rather than treating the flip condition as
  self-justifying.
- **Don't build a single "mission effectiveness" score by averaging MOPs** — per [R310](R310-effects-based-operations.md)/EBO reasoning,
  effects don't aggregate linearly from task completions; a future composite metric needs its own
  explicit model, not an unweighted average dressed up as effectiveness.

## 6. Feature Mapping

FS-201 (Competency Assessment) is the direct consumer.

## 7. Related Topics

[R310](R310-effects-based-operations.md) (Effects-Based Operations, the cascading-effects model MOE is built on), DOM-002 §3 (the
engineering-level statement of the gap this topic formalizes).
