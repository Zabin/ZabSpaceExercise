# R206 — Bounded Rationality

> **Document ID:** R206
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R205](R205-cognitive-psychology-foundations.md)
> **Referenced By:** [R207](R207-cognitive-biases.md), [R208](R208-ooda-loops.md), [R209](R209-planning-theory.md), [R211](R211-heuristics-and-satisficing.md), DOM-002
> **Produces:** the realistic decision-making model DOM-002's rubric is calibrated against
> **Feature Mapping:** FS-201 (Competency Assessment)
> **Related Topics:** [R202](R202-decision-theory.md) (Decision Theory — the idealized model this topic replaces with a
> realistic one), [R205](R205-cognitive-psychology-foundations.md) (Cognitive Psychology Foundations), [R211](R211-heuristics-and-satisficing.md) (Heuristics and Satisficing), DOM-002
> §9 (explicit dependency on this topic)

[↑ Tier R200 index](R200-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-002 §9 explicitly cites this topic as informing "what 'good' decision-making looks like under
realistic constraints, not idealized optimality" — an assessment rubric graded against [R202](R202-decision-theory.md)'s
expected-value ideal would unfairly penalize realistic, competent play. This topic exists to give
the implementer that realistic baseline.

## 2. Concepts

**Bounded rationality: decisions made under real limits on time, information, and computation.**
Herbert Simon's core claim: human decision-makers do not (and structurally cannot) compute a true
expected-value-optimal choice over all options; they operate within bounds set by available time,
incomplete information, and finite cognitive capacity ([R205](R205-cognitive-psychology-foundations.md)) — and rational behavior must be judged
relative to those bounds, not against an unconstrained ideal.

**The simulator imposes the same bounds the theory describes, not just simulates them.** Custody
confidence decay forces action on incomplete information ([R105](R105-custody-theory.md)); access windows force decisions
under genuine time pressure ([R120](R120-access-window-and-geometry-planning.md)); the operator cannot exhaustively enumerate every possible Red
intent before acting. These are not narrative flavor — they are the actual constraints a real
operator would face, faithfully reproduced rather than abstracted away.

**Satisficing as the realistic decision rule.** Rather than searching for the optimal action, a
boundedly-rational agent searches until finding an option that meets an acceptability threshold,
then stops ([R211](R211-heuristics-and-satisficing.md) elaborates the mechanism). A Blue operator issuing a command against an adequate-
but-not-perfect access window, rather than waiting for a theoretically superior one that may not
materialize before a deadline, is satisficing — and that is *competent* play, not a flaw to be
penalized.

**Procedural vs. substantive rationality.** Substantive rationality judges the *outcome* against
the optimal choice; procedural rationality judges the *process* (was the reasoning sound given what
was knowable at decision time) — DOM-002's "custody quality" and "window discipline" dimensions are
explicitly procedural-rationality measures, scoring the decision process the operator actually had
access to, not whether the outcome was objectively best in hindsight.

## 3. Operational Context

Real military and space-operations decision-making is the canonical bounded-rationality domain:
time-critical targeting decisions, imperfect SDA pictures, and finite analyst bandwidth are exactly
the constraints the theory was developed to describe, which is why operational doctrine emphasizes
satisficing heuristics (rules of thumb, checklists, decision aids) over literal optimization.

## 4. Implementation Guidance

- **Any assessment rubric (DOM-002) must score procedural rationality (was the decision reasonable
  given the cell's actual belief state at the time), not substantive rationality (was it correct in
  hindsight)** — scoring against hindsight outcome would penalize a cell for acting correctly on
  imperfect information, directly contradicting MSTR-003 §6's "what the cell believed at that
  moment, not hindsight-corrected" AAR principle.
- **A future AI advisor ([R503](R503-ai-decision-support.md), DOM-008 §4) must not silently substitute an EV-optimal recommendation
  for the trainee's bounded-rational process** — surfacing the optimal answer defeats the purpose of
  practicing decision-making under the very bounds this topic describes.
- **Don't design vignette difficulty as "remove the bounds" (e.g. unlimited time, perfect custody)**
  — per MSTR-003 §2, manufacturing realistic bounded-decision practice is the entire point; removing
  the bounds removes the training value, not just the challenge.

## 5. Feature Mapping

FS-201 (Competency Assessment) is the direct consumer — every DOM-002 dimension must be checked
against this topic's procedural-rationality standard.

## 6. Related Topics

[R202](R202-decision-theory.md) (Decision Theory, the idealized baseline this topic replaces), [R205](R205-cognitive-psychology-foundations.md) (the perceptual substrate
the bounds operate on), [R211](R211-heuristics-and-satisficing.md) (Heuristics and Satisficing, the mechanism), DOM-002 (the rubric this
topic calibrates).
