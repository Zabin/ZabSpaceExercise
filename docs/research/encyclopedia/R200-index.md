# Tier R200 — Decision Sciences

[↑ Encyclopedia index](INDEX.md)

Justifies the simulator's judgment-under-uncertainty design (MSTR-003 §2: plan-execute, fog-of-war,
the OODA loop made structural). 14 topics.

| ID | Title | Scope (one line) | Depends on | Status |
|---|---|---|---|---|
| R201 | Probability and Bayesian Reasoning | Updating belief proportional to evidence; the formal basis of custody confidence. | — | ✅ |
| R202 | Decision Theory | Formal frameworks for choosing under risk/uncertainty. | R201 | ✅ |
| R203 | Game Theory | Strategic interaction between Red/Blue as rational(ish) agents. | R202 | ✅ |
| R204 | Information Theory | Quantifying information value — relevant to collection management (R104). | R201 | ✅ |
| R205 | Cognitive Psychology Foundations | The perception/memory/attention substrate bounded rationality builds on. | — | ✅ |
| R206 | Bounded Rationality | Realistic decision-making under time/info/cognitive constraints. | R205 | ✅ |
| R207 | Cognitive Biases | Confirmation bias, anchoring, etc. — relevant to custody misjudgment. | R205 | ✅ |
| R208 | OODA Loops | Observe-Orient-Decide-Act as the simulator's structural unit of play. | R206 | ✅ |
| R209 | Planning Theory | How plans are formed/revised under partial information. | R202, R206 | ✅ |
| R210 | Decision Support Systems | What a decision aid can/should/shouldn't do (ties DOM-008 §4). | R202 | ✅ |
| R211 | Heuristics and Satisficing | "Good enough" decision strategies under bounded rationality. | R206 | ✅ |
| R212 | Multi-Criteria Decision Analysis | Scoring options against conflicting criteria — COA selection. | R202 | ✅ |
| R213 | Signaling Theory | How actions convey intent to an observer — escalation dynamics. | R203 | ✅ |
| R214 | Utility Theory | Formalizing preference/risk attitude as a maximand. | R202 | ✅ |

**Status:** all 14 topics authored (✅). Grounded in MSTR-003 (educational philosophy), DOM-002
(assessment), DOM-005 (validation), and DOM-008 (AI integration) — each topic exists because one of
those domain documents cites it as the formal justification for a design choice (e.g. MSTR-003 §10
cites R201-R214 collectively as the basis for judgment-under-uncertainty pedagogy).
