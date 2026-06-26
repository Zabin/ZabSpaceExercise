# R509 — AI Integration Patterns

> **Document ID:** R509
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** R501, R503
> **Referenced By:** —
> **Produces:** the cross-cutting checklist for safely integrating any future AI capability into this trainer, synthesizing R501-R508 and DOM-008 into reusable design patterns
> **Feature Mapping:** every future R500-adjacent feature proposal (in-world AI or coding-agent practice) — the capstone topic of the tier
> **Related Topics:** all of R501-R508, DOM-008 (AI Integration Framework, in its entirety — this
> topic is R500's analog to R312's strategic capstone role in R300)

[↑ Tier R500 index](R500-index.md) · [Encyclopedia index](INDEX.md)

**DOM-008 §6 tag:** both — this is the cross-cutting capstone topic explicitly meant to apply to
both in-world AI and coding-agent practice, per DOM-008 §6's requirement that every R500 topic state
its applicability.

## 1. Purpose

R501-R508 each address one AI-adjacent concept (teaming, autonomy, decision support, future warfare
concepts, MDO, machine reasoning, autonomous planning, future C2) individually. This is the tier's
capstone topic: it synthesizes them into a reusable, cross-cutting checklist any future AI-related
feature proposal in this project — whether in-world (a) or coding-agent practice (b), per DOM-008
§5's distinction — should be run through before being built.

## 2. Concepts

**Pattern 1 — Determinism-first.** Per CLAUDE.md's load-bearing invariant and R506's symbolic-vs-
sub-symbolic distinction: any AI-adjacent feature must preserve `(initial_state, eventlog, seed) →
byte-identical state`. A proposal requiring this to be relaxed "because it's just the AI" (DOM-008
§5's named anti-pattern) fails this check regardless of how compelling the feature otherwise is.

**Pattern 2 — Legibility-by-default.** Per DOM-008 §3 and R506: any in-world AI's behavior (Red
preset or hypothetical advisor) should be traceable to a documented, inspectable rule, not an opaque
internal state — a White Cell facilitator should always be able to answer "why did it do that."

**Pattern 3 — Advisor-not-decider, checked at the right grain.** Per DOM-008 §4, R503, and R507's
plan-adaptation concern: the advisor-only ceiling must be checked at the grain of each individual
decision point, not just the feature's overall framing — a feature that silently repeats an
"advisory" action many times without renewed sign-off can functionally cross into decider territory
even while remaining formally advisory at each step.

**Pattern 4 — Fog-of-war parity.** Per R501's shared-mental-model concern and DOM-008 §3's parallel
constraint on Red: any in-world AI's information access must match the same fog-of-war boundary a
human in the same role would have — no god-view-derived advantage for an AI assistant, no
unfair epistemic advantage for an AI Red.

**Pattern 5 — Pedagogical justification, not just technical feasibility.** Per R503's "always-correct
advisor" concern and R507's skill-removal concern: a feature's justification in this PME context must
be that it improves the trainee's learning outcome, not merely that it is technically achievable or
makes the simulator more "realistic" — CLAUDE.md and MSTR-003 both establish operator-skill
development as the actual point.

**Pattern 6 — Coding-agent boundary awareness.** Per DOM-008 §5: an agent doing coding-agent work (b)
that builds or extends in-world AI (a) must not relax (a)'s constraints (determinism, legibility,
advisor-only, fog-of-war parity) as a shortcut — the boundary between "I am extending the simulator"
and "I am the kind of in-world entity the simulator constrains" must stay clear to the agent doing
the work.

## 3. Operational Context

Cross-cutting AI-integration checklists of this kind are standard practice in any organization
integrating AI into a high-stakes or training-critical system, precisely because individual
feature-by-feature review (R501-R508's per-topic guidance) tends to miss interaction effects and
repeated anti-patterns that only become visible when checked as a synthesized list — this is this
project's analog to that practice, scoped to its own specific invariants (determinism, fog-of-war,
advisor-only) rather than generic AI-safety language.

## 4. Implementation Guidance

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
  documentation-authoring agents) working on R500-adjacent content or any `redai.py`/advisor-feature
  code**: do not blur the in-world-AI/coding-agent distinction DOM-008 §5 draws.

## 5. Feature Mapping

Every future R500-adjacent feature proposal is the direct consumer; this is the capstone synthesis
topic for the tier, analogous to R312's role for R300.

## 6. Related Topics

R501 (Human-AI Teaming), R502 (Autonomy in Space Operations), R503 (AI Decision Support), R504
(Future Space Warfare Concepts), R505 (Multi-Domain Operations), R506 (Machine Reasoning), R507
(Autonomous Planning Systems), R508 (Future Command and Control), DOM-008 (AI Integration
Framework).
