# R210 — Decision Support Systems

> **Document ID:** R210
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R202](R202-decision-theory.md)
> **Referenced By:** [R503](R503-ai-decision-support.md), DOM-008
> **Produces:** the design vocabulary behind DOM-008 §4's "advisor, not decider" constraint
> **Feature Mapping:** FS-301 (Research Analytics, candidate AI-advisor scope)
> **Related Topics:** [R202](R202-decision-theory.md) (Decision Theory), [R503](R503-ai-decision-support.md) (AI Decision Support — the forward-looking
> application), DOM-008 §4 (the standing constraint this topic justifies)

[↑ Tier R200 index](R200-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-008 §4 states that any future in-world AI assistance must stay "advisor-only" without being any
more specific about what that means in practice. This topic supplies the decision-support-systems
literature's actual taxonomy of what a decision aid can do, so a future feature proposal can be
checked against real categories rather than an underspecified word.

## 2. Concepts

**The decision-support spectrum: data → information → recommendation → decision.** A system can
stop at any of four levels: (1) present raw data (a telemetry graph); (2) present processed/filtered
information (a custody confidence value, already a step above ground truth); (3) present a ranked
recommendation among options (a future "suggested COA" feature); (4) make the decision itself
(autonomous execution). DOM-008 §4's "advisor, not decider" line falls between (3) and (4) — level 3
is acceptable with explicit design review, level 4 is 🅿️ pending authorization.

**A decision aid changes behavior even without deciding — the "automation bias" risk.** Well-
documented finding: humans tend to over-trust a system's recommendation even when explicitly told
it's advisory only, especially under time pressure — directly relevant to any future level-3
feature in this simulator, since trainees are exactly the population (novice, time-pressured)
most susceptible to this effect.

**Transparency and explainability as a precondition for appropriate trust.** A decision aid that
shows *why* it's recommending something (the underlying custody confidence, the access-window
geometry) lets the operator calibrate trust appropriately; a black-box recommendation invites either
blind acceptance (automation bias) or blind rejection, both pedagogically unhelpful. This is the
formal justification for DOM-008 §4's framing: an *advisor that surfaces information* is safer than
one that surfaces only a conclusion, independent of accuracy.

**Decision aids can be evaluated for net effect on decision quality, not just accuracy.** A highly
accurate recommendation engine can still degrade an operator's learning (by inducing automation bias
or short-circuiting the OODA Orient stage, [R208](R208-ooda-loops.md)) even while "helping" in the narrow sense of correct
suggestions — DOM-005's validation framework, if ever applied to a future AI-advisor feature, should
measure trainee skill development over time, not just recommendation accuracy.

## 3. Operational Context

Military and aviation decision-support systems (targeting aids, collision-avoidance advisories) are
designed around exactly this level-1-through-4 distinction, with explicit human-factors review for
automation-bias risk before a system is certified to give recommendations rather than just data —
this is precedent, not an invented constraint specific to this simulator.

## 4. Implementation Guidance

- **Any future AI-advisor Feature Specification must state which decision-support level (1-4) it
  occupies and must not exceed level 3 without explicit design review per DOM-008 §4/§6.**
- **A level-3 (recommendation) feature must show its reasoning (transparency), not just a ranked
  output** — an opaque "Plan A is best" recommendation is a higher automation-bias risk than one
  that shows the custody/window/Δv inputs the ranking is based on.
- **A future assessment of an AI-advisor feature (DOM-005) should explicitly test for automation
  bias** (e.g., does trainee performance *without* the aid degrade after extended use *with* it) —
  not just whether the aid's own recommendations were accurate.

## 5. Feature Mapping

FS-301 (Research Analytics) is the most likely future home for any AI-advisor capability; this
topic's taxonomy is the gate any such proposal must pass through first.

## 6. Related Topics

[R202](R202-decision-theory.md) (Decision Theory, the underlying recommendation logic), [R503](R503-ai-decision-support.md) (AI Decision Support, this
topic's forward-looking elaboration), DOM-008 §4 (the standing constraint operationalized here).
