# Tier R200 — Decision Sciences

[↑ Encyclopedia index](INDEX.md)

Justifies the simulator's judgment-under-uncertainty design (MSTR-003 §2: plan-execute, fog-of-war,
the OODA loop made structural). 14 topics.

| ID | Title | Scope (one line) | Depends on | Status |
|---|---|---|---|---|
| [R201](R201-probability-and-bayesian-reasoning.md) | Probability and Bayesian Reasoning | Updating belief proportional to evidence; the formal basis of custody confidence. | — | ✅ |
| [R202](R202-decision-theory.md) | Decision Theory | Formal frameworks for choosing under risk/uncertainty. | [R201](R201-probability-and-bayesian-reasoning.md) | ✅ |
| [R203](R203-game-theory.md) | Game Theory | Strategic interaction between Red/Blue as rational(ish) agents. | [R202](R202-decision-theory.md) | ✅ |
| [R204](R204-information-theory.md) | Information Theory | Quantifying information value — relevant to collection management ([R104](R104-collection-management.md)). | [R201](R201-probability-and-bayesian-reasoning.md) | ✅ |
| [R205](R205-cognitive-psychology-foundations.md) | Cognitive Psychology Foundations | The perception/memory/attention substrate bounded rationality builds on. | — | ✅ |
| [R206](R206-bounded-rationality.md) | Bounded Rationality | Realistic decision-making under time/info/cognitive constraints. | [R205](R205-cognitive-psychology-foundations.md) | ✅ |
| [R207](R207-cognitive-biases.md) | Cognitive Biases | Confirmation bias, anchoring, etc. — relevant to custody misjudgment. | [R205](R205-cognitive-psychology-foundations.md) | ✅ |
| [R208](R208-ooda-loops.md) | OODA Loops | Observe-Orient-Decide-Act as the simulator's structural unit of play. | [R206](R206-bounded-rationality.md) | ✅ |
| [R209](R209-planning-theory.md) | Planning Theory | How plans are formed/revised under partial information. | [R202](R202-decision-theory.md), [R206](R206-bounded-rationality.md) | ✅ |
| [R210](R210-decision-support-systems.md) | Decision Support Systems | What a decision aid can/should/shouldn't do (ties DOM-008 §4). | [R202](R202-decision-theory.md) | ✅ |
| [R211](R211-heuristics-and-satisficing.md) | Heuristics and Satisficing | "Good enough" decision strategies under bounded rationality. | [R206](R206-bounded-rationality.md) | ✅ |
| [R212](R212-multi-criteria-decision-analysis.md) | Multi-Criteria Decision Analysis | Scoring options against conflicting criteria — COA selection. | [R202](R202-decision-theory.md) | ✅ |
| [R213](R213-signaling-theory.md) | Signaling Theory | How actions convey intent to an observer — escalation dynamics. | [R203](R203-game-theory.md) | ✅ |
| [R214](R214-utility-theory.md) | Utility Theory | Formalizing preference/risk attitude as a maximand. | [R202](R202-decision-theory.md) | ✅ |

**Status:** all 14 topics authored (✅). Grounded in MSTR-003 (educational philosophy), DOM-002
(assessment), DOM-005 (validation), and DOM-008 (AI integration) — each topic exists because one of
those domain documents cites it as the formal justification for a design choice (e.g. MSTR-003 §10
cites [R201](R201-probability-and-bayesian-reasoning.md)-[R214](R214-utility-theory.md) collectively as the basis for judgment-under-uncertainty pedagogy).
