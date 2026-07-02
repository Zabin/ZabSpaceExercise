# R509 — AI Integration Patterns

> **Document ID:** R509
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R501](R501-human-ai-teaming.md), [R503](R503-ai-decision-support.md)
> **Referenced By:** —
> **Produces:** the cross-cutting checklist for safely integrating any future AI capability into this trainer, synthesizing [R501](R501-human-ai-teaming.md)-[R508](R508-future-command-and-control.md) and DOM-008 into reusable design patterns
> **Feature Mapping:** every future [R500](R500-index.md)-adjacent feature proposal (in-world AI or coding-agent practice) — the capstone topic of the tier
> **Related Topics:** all of [R501](R501-human-ai-teaming.md)-[R508](R508-future-command-and-control.md), DOM-008 (AI Integration Framework, in its entirety — this
> topic is [R500](R500-index.md)'s analog to [R312](R312-space-strategy.md)'s strategic capstone role in [R300](R300-index.md))
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 0 directly (synthesis topic; draws entirely on the 12 primary sources already cited across R501-R508 — see §3 Sources)

[↑ Tier R500 index](R500-index.md) · [Encyclopedia index](INDEX.md)

**DOM-008 §6 tag:** both — this is the cross-cutting capstone topic explicitly meant to apply to
both in-world AI and coding-agent practice, per DOM-008 §6's requirement that every [R500](R500-index.md) topic state
its applicability.

## 1. Purpose

[R501](R501-human-ai-teaming.md)-[R508](R508-future-command-and-control.md) each address one AI-adjacent concept (teaming, autonomy, decision support, future warfare
concepts, MDO, machine reasoning, autonomous planning, future C2) individually. This is the tier's
capstone topic: it synthesizes them into a reusable, cross-cutting checklist any future AI-related
feature proposal in this project — whether in-world (a) or coding-agent practice (b), per DOM-008
§5's distinction — should be run through before being built.

## 2. Scope

Covers: the six-pattern synthesis checklist itself, and which underlying R501-R508 finding each
pattern draws on. Does **not** introduce new primary-source claims beyond what R501-R508 already
establish (this is a synthesis topic by design, per MSTR-007 §5's duplication rule — a citation
appearing in an underlying topic is not re-derived here, only pointed to) and does **not** cover
DOM-008 itself in full (referenced, not restated). A future pattern (Pattern 7+) may be added here
only once a genuinely new R5xx topic supplies the underlying finding for it.

## 3. Concepts

**Pattern 1 — Determinism-first.** Per CLAUDE.md's load-bearing invariant and [R506](R506-machine-reasoning.md) §3's symbolic-vs-
sub-symbolic distinction (grounded in [Newell & Simon 1976](https://dl.acm.org/doi/10.1145/360018.360022) and the
[DARPA XAI accuracy/explainability tradeoff](https://onlinelibrary.wiley.com/doi/full/10.1002/ail2.61)): any AI-adjacent feature must preserve `(initial_state, eventlog, seed) →
byte-identical state`. A proposal requiring this to be relaxed "because it's just the AI" (DOM-008
§5's named anti-pattern) fails this check regardless of how compelling the feature otherwise is.

**Pattern 2 — Legibility-by-default.** Per DOM-008 §3 and [R506](R506-machine-reasoning.md) §3's citation of the DoD's
**Traceable** AI Ethical Principle ([U.S. Army, 2020](https://www.army.mil/article/233690/dod_adopts_5_principles_of_artificial_intelligence_ethics)):
any in-world AI's behavior (Red preset or hypothetical advisor) should be traceable to a documented,
inspectable rule, not an opaque internal state — a White Cell facilitator should always be able to
answer "why did it do that."

**Pattern 3 — Advisor-not-decider, checked at the right grain.** Per DOM-008 §4, [R503](R503-ai-decision-support.md) §3's citation of
the [Cummings (2004) Patriot fratricide analysis](https://arc.aiaa.org/doi/10.2514/6.2004-6313), and [R507](R507-autonomous-planning-systems.md) §3's
CASPER-replanning finding: the advisor-only ceiling must be checked at the grain of each individual
decision point, not just the feature's overall framing — a feature that silently repeats an
"advisory" action many times without renewed sign-off (as CASPER's real onboard replanner does, and
as the Patriot case shows a formally-advisory system doing under time pressure) can functionally cross
into decider territory even while remaining formally advisory at each step.

**Pattern 4 — Fog-of-war parity.** Per [R501](R501-human-ai-teaming.md) §3's shared-mental-model citation
([Cannon-Bowers, Salas & Converse, 1993](https://www.researchgate.net/publication/226781970_Shared_Mental_Models)) and DOM-008 §3's parallel
constraint on Red: any in-world AI's information access must match the same fog-of-war boundary a
human in the same role would have — no god-view-derived advantage for an AI assistant, no
unfair epistemic advantage for an AI Red.

**Pattern 5 — Pedagogical justification, not just technical feasibility.** Per [R503](R503-ai-decision-support.md) §3's "always-correct
advisor" concern and [R507](R507-autonomous-planning-systems.md) §3's finding that both of its real precedents (NASA CASPER,
Starlink collision avoidance) were justified operationally rather than pedagogically: a feature's
justification in this PME context must be that it improves the trainee's learning outcome, not merely
that it is technically achievable, flight-proven elsewhere, or makes the simulator more "realistic" —
CLAUDE.md and MSTR-003 both establish operator-skill development as the actual point, which is a
different bar than either real precedent had to clear.

**Pattern 6 — Coding-agent boundary awareness.** Per DOM-008 §5: an agent doing coding-agent work (b)
that builds or extends in-world AI (a) must not relax (a)'s constraints (determinism, legibility,
advisor-only, fog-of-war parity) as a shortcut — the boundary between "I am extending the simulator"
and "I am the kind of in-world entity the simulator constrains" must stay clear to the agent doing
the work.

### Sources

This topic introduces no new primary sources — it is a synthesis of claims already cited in R501-R508.
Per pattern: Pattern 1 draws on [R506](R506-machine-reasoning.md) §3 (Newell & Simon 1976; Gunning et al. 2021); Pattern 2 draws on
[R506](R506-machine-reasoning.md) §3 (U.S. Army/DoD AI Ethical Principles 2020); Pattern 3 draws on [R503](R503-ai-decision-support.md) §3 (Cummings
2004) and [R507](R507-autonomous-planning-systems.md) §3 (Chien et al. 2006); Pattern 4 draws on [R501](R501-human-ai-teaming.md) §3 (Cannon-Bowers, Salas &
Converse 1993); Pattern 5 draws on [R507](R507-autonomous-planning-systems.md) §3 (Chien et al. 2006; Starlink SAT-51385). See each
linked topic's own `### Sources` subsection for the full live/Wayback/accessed-date citation record.

## 4. Operational Context

Cross-cutting AI-integration checklists of this kind are standard practice in any organization
integrating AI into a high-stakes or training-critical system, precisely because individual
feature-by-feature review ([R501](R501-human-ai-teaming.md)-[R508](R508-future-command-and-control.md)'s per-topic guidance) tends to miss interaction effects and
repeated anti-patterns that only become visible when checked as a synthesized list — this is this
project's analog to that practice, scoped to its own specific invariants (determinism, fog-of-war,
advisor-only) rather than generic AI-safety language. The DoD's own five-principle AI Ethics framework
([R506](R506-machine-reasoning.md) §3) is itself exactly this kind of cross-cutting checklist at a much larger organizational
scale, which is the closest real-world structural precedent for what this topic does at this
project's scale.

### Sources

Uses the sources already cited in R501-R508 (see §3's per-pattern attribution above); no additional
sources introduced in this section.

## 5. Implementation Guidance

- **Run every future AI-adjacent feature proposal — in-world (a) or coding-agent practice (b), per
  DOM-008 §5 — through Patterns 1-6 explicitly before building it**, and document which patterns
  were checked in the feature's design notes.
- **Patterns 1, 2, and 4 (determinism, legibility, fog-of-war parity) are non-negotiable
  architectural constraints** — a proposal failing any of these should not proceed regardless of its
  other merits.
- **Patterns 3 and 5 (advisor-grain check, pedagogical justification) require judgment, not a binary
  check** — flag ambiguous cases for explicit user/maintainer review (per DOM-008 §4's "pending
  authorization" framing for anything beyond advisory) rather than resolving the ambiguity
  unilaterally.
- **Pattern 6 is a standing instruction to any future coding agent (including this project's own
  documentation-authoring agents) working on [R500](R500-index.md)-adjacent content or any `redai.py`/advisor-feature
  code**: do not blur the in-world-AI/coding-agent distinction DOM-008 §5 draws.

## 6. Feature Mapping

Every future [R500](R500-index.md)-adjacent feature proposal is the direct consumer; this is the capstone synthesis
topic for the tier, analogous to [R312](R312-space-strategy.md)'s role for [R300](R300-index.md).

## 7. Related Topics

[R501](R501-human-ai-teaming.md) (Human-AI Teaming), [R502](R502-autonomy-in-space-operations.md) (Autonomy in Space Operations), [R503](R503-ai-decision-support.md) (AI Decision Support), [R504](R504-future-space-warfare-concepts.md)
(Future Space Warfare Concepts), [R505](R505-multi-domain-operations.md) (Multi-Domain Operations), [R506](R506-machine-reasoning.md) (Machine Reasoning), [R507](R507-autonomous-planning-systems.md)
(Autonomous Planning Systems), [R508](R508-future-command-and-control.md) (Future Command and Control), DOM-008 (AI Integration
Framework).
