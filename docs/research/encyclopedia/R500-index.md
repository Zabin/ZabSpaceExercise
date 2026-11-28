# Tier R500 — Future Operations

[↑ Encyclopedia index](INDEX.md)

Forward-looking context for the in-world AI constraint ([MSTR-003](../../master/MSTR-003-educational-philosophy.md) §2a) and long-horizon Feature Specs. 9 topics.

| ID | Title | Scope (one line) | Depends on | Status |
|---|---|---|---|---|
| [R501](R501-human-ai-teaming.md) | Human-AI Teaming | How a human operator and an AI advisor share a decision loop. | — | ✅ |
| [R502](R502-autonomy-in-space-operations.md) | Autonomy in Space Operations | Degrees of autonomy in bus/payload operations, real and simulated. | [R501](R501-human-ai-teaming.md) | ✅ |
| [R503](R503-ai-decision-support.md) | AI Decision Support | What an AI advisor can surface without deciding for the trainee ([MSTR-003 §2a](../../master/MSTR-003-educational-philosophy.md)). | [R501](R501-human-ai-teaming.md) | ✅ |
| [R504](R504-future-space-warfare-concepts.md) | Future Space Warfare Concepts | Emerging counterspace concepts beyond the current five-D's taxonomy. | — | ✅ |
| [R505](R505-multi-domain-operations.md) | Multi-Domain Operations | Space integrated with other domains (cyber, air, land, maritime). | [R504](R504-future-space-warfare-concepts.md) | ✅ |
| [R506](R506-machine-reasoning.md) | Machine Reasoning | Symbolic/sub-symbolic reasoning approaches relevant to future planners. | [R503](R503-ai-decision-support.md) | ✅ |
| [R507](R507-autonomous-planning-systems.md) | Autonomous Planning Systems | Systems that generate/adapt plans with reduced human-in-the-loop. | [R502](R502-autonomy-in-space-operations.md), [R506](R506-machine-reasoning.md) | ✅ |
| [R508](R508-future-command-and-control.md) | Future Command and Control | C2 architectures anticipating higher autonomy/AI integration. | [R502](R502-autonomy-in-space-operations.md), [R507](R507-autonomous-planning-systems.md) | ✅ |
| [R509](R509-ai-integration-patterns.md) | AI Integration Patterns | Cross-cutting patterns for safely integrating AI into a trainer like this one. | [R501](R501-human-ai-teaming.md), [R503](R503-ai-decision-support.md) | ✅ |

**Status: 9 of 9 topics complete — tier fully closed (2026-07-02), GAP-13 remediation done.**
Every topic now carries the mandatory §2 Scope section (MSTR-007 §4.2) and is cited per
`docs/research/10-sources-and-methodology.md`'s convention — inline citations at every substantive
AI/autonomy/teaming claim site, a `### Sources` subsection on every `##` section (live URL + Wayback
snapshot + accessed date, or a cited `spacesim/session/redai.py`/`engine/recovery.py` file:line for
claims about the simulator's own present-tense practice), and each forward-looking claim grounded in
a real, dated, named source rather than presented as settled fact with no provenance — Tier A/B
sources include ECSS-E-ST-70-11C (spacecraft autonomy levels), NASA's DS1 Remote Agent and EO-1/
CASPER flight reports, DARPA's Mosaic Warfare and XAI program releases, the DoD JADC2 strategy and AI
Ethical Principles, Starlink's own collision-avoidance public filing, and the peer-reviewed
human-automation-teaming/automation-bias literature (Parasuraman, Sheridan, Wickens, Riley, Mosier,
Skitka, Cummings, Cannon-Bowers/Salas/Converse, Newell & Simon). Each topic's R500 tag (in-world
AI, coding-agent practice, both, or neither) is intact from the original draft. [R509](R509-ai-integration-patterns.md) is the
tier's capstone, synthesizing R501-R508's findings into six reusable integration patterns without
re-deriving their citations (see R509 §3 Sources for the per-pattern attribution). Per
The former future-work list §13 (Recommendation R1), R500 was sequenced first for GAP-13 remediation
("zero citations, most speculative claims") — with this tier closed, **R400 (Research Methods) is
now the GAP-13 priority**, per the `02-research-methods-and-validation` skill's workflow. Last reviewed
across the tier: 2026-07-02.

## Tag convention

Every R501-R509 topic must explicitly carry the **R500 tag**, in its Implementation Guidance section, whether the
concept it describes applies to in-world AI (Red doctrine presets today; any future advisor) or
coding-agent practice (this repository's documentation-driven development model) or both, since
conflating them is the most likely failure mode for this tier (a topic on "machine reasoning" could
easily drift into discussing LLM-agent practice when the simulator's actual gap is an in-world
planning assistant, or vice versa). The constraint on in-world AI is stated in
[MSTR-003](../../master/MSTR-003-educational-philosophy.md) §2a; the constraint on coding-agent
practice is [MSTR-006](../../master/MSTR-006-governance-principles.md) §4 and §8.
