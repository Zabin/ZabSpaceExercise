# R503 — AI Decision Support

> **Document ID:** R503
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R501](R501-human-ai-teaming.md)
> **Referenced By:** [R506](R506-machine-reasoning.md), [R509](R509-ai-integration-patterns.md)
> **Produces:** the concrete decision-support-feature vocabulary directly operationalizing DOM-008 §4's "advisor, not decider" line
> **Feature Mapping:** any future in-world AI decision-support feature (🅿️ pending authorization per DOM-008 §4)
> **Related Topics:** [R210](R210-decision-support-systems.md) (Decision Support Systems — the general 4-level spectrum this topic
> applies to the specific in-world-AI case), DOM-008 §4 (the direct governing constraint), [R501](R501-human-ai-teaming.md)
> (Human-AI Teaming)

[↑ Tier R500 index](R500-index.md) · [Encyclopedia index](INDEX.md)

**DOM-008 §6 tag:** in-world AI (a hypothetical trainee-facing feature; not coding-agent practice).

## 1. Purpose

[R210](R210-decision-support-systems.md) supplies the general 4-level decision-support spectrum (data/information/recommendation/
decision); this topic applies that spectrum specifically to the concrete case DOM-008 §4 already
names — a future in-world AI assistant for the trainee — and works through what such a feature could
and could not legitimately do under the advisor-only constraint.

## 2. Concepts

**Where DOM-008 §4's line falls on [R210](R210-decision-support-systems.md)'s spectrum.** [R210](R210-decision-support-systems.md)'s levels 1-2 (data, information) are
clearly within bounds for any future in-world advisor; level 3 (recommendation — "here is a candidate
action and why") is the explicit ceiling DOM-008 §4 permits; level 4 (the system decides) is
explicitly out of bounds — a future feature proposal should be checked against landing at level 3 or
below, never level 4.

**The difference between surfacing a recommendation and surfacing reasoning.** A level-3 advisor can
either present a bare recommendation ("jam asset X") or present the reasoning behind it ("asset X's
custody confidence is below the weapons-quality threshold and a jam window opens in 4 minutes") —
the latter is doctrinally preferable per [R210](R210-decision-support-systems.md)'s automation-bias concern, since it gives the trainee
material to evaluate and potentially reject the recommendation rather than just a conclusion to
accept or decline.

**An advisor that only ever recommends the "correct" doctrinal action undermines the exercise's
educational purpose.** Per MSTR-003's plan-execute-as-the-unit-of-learning framing, a trainee who
always defers to an always-correct advisor never practices the judgment the exercise exists to train
— a future advisor feature should be evaluated against whether it preserves a genuine decision for
the trainee to make, not just technically avoid "deciding" while functionally removing the judgment
task.

**Explainability as a requirement, not a nice-to-have.** A recommendation without legible reasoning
is functionally closer to a level-4 decision than its formal level-3 classification suggests, since
an opaque recommendation invites uncritical acceptance (automation bias, [R210](R210-decision-support-systems.md)) precisely because the
trainee has no basis to evaluate it — any future advisor feature should be required to expose its
reasoning, not just its conclusion.

## 3. Operational Context

AI decision-support systems in real military and aviation contexts have repeatedly run into exactly
this tension — a recommendation system technically classified as "advisory" that in practice
functions as a decision-maker because operators uncritically accept its output — which is precisely
why DOM-008 §4's "advisor, not decider" framing and this topic's explainability requirement matter as
design constraints, not just labels.

## 4. Implementation Guidance

- **Any future in-world AI decision-support feature must cap itself at [R210](R210-decision-support-systems.md)'s level 3
  (recommendation), never level 4 (decision)**, per DOM-008 §4 — and should expose its underlying
  reasoning, not just a bare recommendation, per the explainability concern above.
- **Evaluate any proposed advisor feature against whether it preserves a genuine judgment task for
  the trainee** — per MSTR-003's plan-execute learning model, an advisor that is always right and
  always deferred to has defeated the exercise's pedagogical purpose even while staying formally
  within DOM-008 §4's letter.
- **Treat an opaque, unexplained recommendation as a design smell** — even if formally level 3, an
  unexplained recommendation functions like automation-bias bait and should be redesigned to expose
  its reasoning before being built.

## 5. Feature Mapping

Any future in-world AI decision-support feature is the direct consumer; none exists yet (🅿️ pending
authorization per DOM-008 §4).

## 6. Related Topics

[R210](R210-decision-support-systems.md) (Decision Support Systems, the general spectrum), DOM-008 §4 (the governing constraint), [R501](R501-human-ai-teaming.md)
(Human-AI Teaming).
