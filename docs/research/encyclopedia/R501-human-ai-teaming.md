# R501 — Human-AI Teaming

> **Document ID:** R501
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** —
> **Referenced By:** [R502](R502-autonomy-in-space-operations.md), [R503](R503-ai-decision-support.md), [R509](R509-ai-integration-patterns.md)
> **Produces:** the vocabulary for how a human operator and an AI advisor would share a decision loop, framing DOM-008 §4's "advisor not decider" constraint
> **Feature Mapping:** any future in-world AI decision-support feature (🅿️ pending authorization per DOM-008 §4)
> **Related Topics:** [R210](R210-decision-support-systems.md) (Decision Support Systems — the 4-level spectrum this topic's teaming
> models map onto), DOM-008 (AI Integration Framework — §4's advisor-only constraint), [R503](R503-ai-decision-support.md) (AI
> Decision Support)

[↑ Tier R500 index](R500-index.md) · [Encyclopedia index](INDEX.md)

**DOM-008 §6 tag:** in-world AI (a future trainee-facing advisor), with implications for coding-agent
practice noted in §4 below.

## 1. Purpose

DOM-008 §4 establishes "advisor, not decider" as the standing constraint on any future in-world AI
assistance to a trainee. This topic supplies the human-AI teaming vocabulary that constraint is a
specific instance of — the general models for how decision authority and information flow are
divided between a human and an AI system sharing a task, so a future feature proposal can be checked
against the full range of teaming models, not just the binary "automated or not."

## 2. Concepts

**Teaming models range from tool to teammate to delegate.** A tool-level AI only responds to explicit
queries with no initiative; a teammate-level AI proactively surfaces relevant information without
being asked but never acts; a delegate-level AI takes autonomous action within a bounded scope — DOM-
008 §4's "advisor, not decider" line places any future in-world AI assistance at or below the
teammate level, explicitly ruling out delegate-level autonomous decision-making for the trainee.

**Trust calibration: neither over-trusting nor under-trusting the AI partner.** Over-trust
(automation bias, [R210](R210-decision-support-systems.md)) leads an operator to accept an AI recommendation without independent
verification even when it's wrong; under-trust leads to ignoring a genuinely useful recommendation —
calibrated trust requires the AI's confidence/uncertainty to be genuinely legible to the operator, not
just its bottom-line recommendation.

**Shared mental models.** Effective human-AI teaming requires the human to have an accurate model of
what the AI does and doesn't know, and vice versa to the extent the AI models the human — a future
in-world advisor that draws on different information than the trainee currently has access to (e.g.
ground truth the trainee's fog-of-war view doesn't show) would violate this requirement and create a
dangerous shared-mental-model mismatch, distinct from and in addition to DOM-008 §4's decision-
authority constraint.

**Workload and attention allocation.** A well-designed human-AI team allocates the AI to tasks that
reduce the human's workload at exactly the moments cognitive load is highest, rather than adding a new
information stream to monitor at all times — a future advisor feature should be evaluated against
whether it reduces or adds to the trainee's attentional burden ([R205](R205-cognitive-psychology-foundations.md)'s working-memory limits).

## 3. Operational Context

Human-AI teaming research (from aviation automation studies through more recent military
human-machine-teaming doctrine) is the active research base most directly relevant to any future
in-world AI assistance in this simulator, and has documented both classes of failure (over-trust/
automation bias, [R210](R210-decision-support-systems.md); under-trust/disuse) extensively enough that any future advisor-feature design
should treat avoiding both as a first-class design requirement, not an afterthought.

## 4. Implementation Guidance

- **Any future in-world AI decision-support feature must be designed at or below the
  "teammate" level per DOM-008 §4** — surfacing information or flagging a consideration, never taking
  or recommending a single "decide this for you" action.
- **A future advisor's information access must be restricted to exactly the same fog-of-war view the
  trainee has** (per the shared-mental-model concern above and DOM-008 §3's parallel constraint on
  Red presets) — an advisor with god-view-derived insight breaks the shared mental model and
  effectively decides for the trainee by surfacing otherwise-unavailable certainty.
- **Evaluate any future advisor feature's effect on trainee workload explicitly** (does it reduce
  attentional burden at high-load moments, or add a new stream to monitor) before building it — per
  the workload-allocation concern above.
- **Coding-agent note (DOM-008 §5):** an agent implementing any future advisor feature is doing
  coding-agent work (b) that builds in-world AI (a); the agent must not relax the advisor's
  information-access constraint "to make the demo more impressive."

## 5. Feature Mapping

Any future in-world AI decision-support feature is the direct consumer; none exists yet (🅿️ pending
authorization).

## 6. Related Topics

[R210](R210-decision-support-systems.md) (Decision Support Systems, the 4-level spectrum), DOM-008 (AI Integration Framework §4), [R503](R503-ai-decision-support.md)
(AI Decision Support, the direct downstream elaboration).
