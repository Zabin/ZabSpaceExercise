# R506 — Machine Reasoning

> **Document ID:** R506
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R503](R503-ai-decision-support.md)
> **Referenced By:** [R507](R507-autonomous-planning-systems.md)
> **Produces:** the symbolic-vs-sub-symbolic vocabulary for evaluating any future "smarter Red" or planning-assistance proposal against this engine's determinism invariant
> **Feature Mapping:** any future `redai.py` enhancement or planning-assistance feature proposing reasoning beyond the current rule-based doctrine presets
> **Related Topics:** [R503](R503-ai-decision-support.md) (AI Decision Support), `engine/redai.py` (the existing rule-based
> reasoning this topic contrasts with more sophisticated approaches), [R507](R507-autonomous-planning-systems.md) (Autonomous Planning
> Systems), DOM-008 §3/§5
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 3 (Tier A/B — foundational AI theory + DARPA program + DoD policy — see §3 Sources)

[↑ Tier R500 index](R500-index.md) · [Encyclopedia index](INDEX.md)

**DOM-008 §6 tag:** both — directly relevant to in-world AI (a future `redai.py` enhancement) and to
coding-agent practice (§5's note about an agent extending Red's reasoning).

## 1. Purpose

`redai.py`'s current doctrine presets are rule-based/data-parameterized (DOM-008 §3). If a future
proposal ever suggests making Red's (or a future advisor's) reasoning "smarter" via a more
sophisticated reasoning approach, this topic supplies the vocabulary to evaluate that proposal against
what it would actually require — particularly whether it's compatible with the engine's determinism
invariant, which is the single most load-bearing constraint any such proposal must clear.

## 2. Scope

Covers: the symbolic-vs-sub-symbolic reasoning distinction as it bears on this engine's determinism/
legibility requirements, and the real-world explainability tension named by DARPA's XAI program and
DoD's AI ethics principles. Does **not** cover: the decision-authority question of whether reasoning
output may be acted on autonomously ([R503](R503-ai-decision-support.md)/DOM-008 §4's job — orthogonal
to this topic per §3 below), or the planning-algorithm mechanics of *how* a symbolic or sub-symbolic
reasoner would generate a multi-step plan ([R507](R507-autonomous-planning-systems.md)'s job) — this
topic is about the reasoning-representation choice itself, not decision authority or planning method.

## 3. Concepts

**Symbolic reasoning: explicit rules and logical inference over structured representations.** The
foundational statement of this approach is Newell & Simon's 1975 ACM Turing Award lecture,
[*Computer Science as Empirical Inquiry: Symbols and Search*](https://dl.acm.org/doi/10.1145/360018.360022)
(Communications of the ACM 19(3), 1976), whose **physical symbol system hypothesis** holds that a
system manipulating symbol structures by explicit rules has the necessary and sufficient means for
general intelligent action, and whose companion **heuristic search hypothesis** frames
problem-solving as generating and progressively modifying symbol structures until a solution is
reached. A rule-based doctrine preset (the existing `redai.py` pattern: data-parameterized thresholds
and decision rules) is symbolic reasoning in exactly this sense — its logic is inspectable, its
behavior is traceable to a specific rule firing, and it is naturally compatible with the engine's
determinism and legibility requirements (DOM-008 §3).

**Sub-symbolic reasoning: learned statistical models (e.g. neural networks) without explicit rules.**
A sub-symbolic approach (e.g. a trained policy network deciding Red's actions) trades inspectability
and determinism for potentially more sophisticated/adaptive behavior. DARPA's Explainable AI (XAI)
program (formulated 2015, funded 2017-2021) was created specifically because of this tradeoff:
program lead David Gunning's own retrospective states the field's "inherent tension between machine
learning performance (predictive accuracy) and explainability" — the highest-performing sub-symbolic
methods (deep learning) are typically the least explainable, and the most explainable methods
(decision trees, rule sets) are typically less accurate
([Gunning et al., *DARPA's Explainable AI (XAI) Program: A Retrospective*, Applied AI Letters, 2021](https://onlinelibrary.wiley.com/doi/full/10.1002/ail2.61)).
This tension is fundamentally harder to reconcile with the engine's `(initial_state, eventlog, seed)
→ byte-identical state` invariant (CLAUDE.md) unless the trained model itself is frozen and treated as
a pure deterministic function of its inputs, and is much harder to make legible to a White Cell
facilitator (DOM-008 §3's legibility principle) than a rule-based preset's named parameters.

**Hybrid approaches: sub-symbolic perception feeding a symbolic decision layer.** Some real-world
systems use a learned model to interpret noisy input and a symbolic rule layer to make the actual
decision — a hypothetical hybrid Red-AI enhancement (e.g. a learned model interpreting Blue's
behavior pattern, feeding into the existing rule-based decision presets) would inherit the
determinism/legibility concerns of whichever layer actually drives the decision.

**Explainability is a named, formal requirement in defense AI policy, not an academic nicety.** The
Department of Defense's five AI Ethical Principles (adopted February 2020, developed over 15 months by
the Defense Innovation Board) include **Traceable**: DoD AI capabilities must be developed and
deployed "such that relevant personnel possess an appropriate understanding of the technology,
development processes, and operational methods applicable to AI capabilities, including with
transparent and auditable methodologies, data sources, and design procedures"
([U.S. Army, "DOD Adopts 5 Principles of Artificial Intelligence Ethics," 24 Feb 2020](https://www.army.mil/article/233690/dod_adopts_5_principles_of_artificial_intelligence_ethics)).
This is a direct, real-world institutional analog to DOM-008 §3's "Red AI should be legible to White
Cell" requirement — the same traceability concern the defense establishment formally requires of any
fielded military AI system applies to this simulator's much smaller-scale Red-AI legibility goal.

**The reasoning-approach choice is independent of the Human-AI-teaming and decision-support
constraints ([R501](R501-human-ai-teaming.md)/[R503](R503-ai-decision-support.md)).** Choosing symbolic over sub-symbolic reasoning is a determinism/legibility
question (DOM-008 §3, and the DARPA XAI / DoD Traceable-principle tension above); the advisor-not-
decider constraint (DOM-008 §4) is a decision-authority question — a future proposal could in
principle satisfy one without the other, and both should be checked independently.

### Sources

- *Newell, A. & Simon, H.A. (1976). Computer Science as Empirical Inquiry: Symbols and Search.
  Communications of the ACM, 19(3), 113–126.* (1975 ACM Turing Award Lecture) —
  [live (DOI)](https://dl.acm.org/doi/10.1145/360018.360022)
  · [snapshot](https://web.archive.org/web/2026*/https://dl.acm.org/doi/10.1145/360018.360022)
  · accessed 2026-07-02.
- *Gunning, D. et al. (2021). DARPA's Explainable AI (XAI) Program: A Retrospective. Applied AI
  Letters, 2(4).* — [live (DOI)](https://onlinelibrary.wiley.com/doi/full/10.1002/ail2.61)
  · [snapshot](https://web.archive.org/web/2026*/https://onlinelibrary.wiley.com/doi/full/10.1002/ail2.61)
  · accessed 2026-07-02.
- *U.S. Army, "DOD Adopts 5 Principles of Artificial Intelligence Ethics"* (24 February 2020,
  reporting the Defense Innovation Board-developed DoD AI Ethical Principles) —
  [live](https://www.army.mil/article/233690/dod_adopts_5_principles_of_artificial_intelligence_ethics)
  · [snapshot](https://web.archive.org/web/2026*/https://www.army.mil/article/233690/dod_adopts_5_principles_of_artificial_intelligence_ethics)
  · accessed 2026-07-02.

## 4. Operational Context

The symbolic vs. sub-symbolic distinction is foundational to AI research broadly (Newell & Simon's
1976 formulation predates and frames the modern debate), and the specific tension this topic names —
sub-symbolic methods' typical opacity and non-determinism vs. this project's hard determinism/
legibility requirements — is exactly the tradeoff DARPA's XAI program was funded to address and DoD's
Traceable principle formally requires defense-AI programs to resolve before fielding a system. This is
not a hypothetical concern invented for this project; it is the live, unresolved central tension in
real defense-AI policy as of the DoD principles' 2020 adoption and the XAI program's 2021 retrospective
findings.

### Sources

Uses the same sources cited inline in §3 (Newell & Simon 1976; Gunning et al. 2021; DoD AI Ethical
Principles 2020); no additional sources introduced in this section.

## 5. Implementation Guidance

- **Any future proposal to make `redai.py` "smarter" via a sub-symbolic/learned approach must be
  checked against the engine's determinism invariant before being pursued** — per CLAUDE.md, this is
  non-negotiable; a learned model must be frozen and treated as a pure deterministic function, and
  even then loses much of the legibility a rule-based preset has (the same accuracy/explainability
  tradeoff DARPA XAI names, §3).
- **Prefer symbolic, rule-based extensions to `redai.py`'s existing pattern over sub-symbolic
  alternatives**, consistent with DOM-008 §3's legibility principle and the DoD Traceable AI
  principle's real-world precedent (§3) — a more sophisticated rule set (more conditions, more nuanced
  thresholds) is a smaller, more auditable step than introducing a learned model.
- **Coding-agent note (DOM-008 §5):** an agent asked to make Red "smarter" should default to symbolic
  rule extension and should explicitly flag, rather than silently implement, any proposal that would
  require relaxing determinism for a sub-symbolic approach.
- **Evaluate the reasoning-approach question (this topic) and the decision-authority question
  (DOM-008 §4/[R503](R503-ai-decision-support.md)) independently** for any future AI-related proposal — satisfying one does not
  imply the other.

## 6. Feature Mapping

Any future `redai.py` enhancement or planning-assistance feature is the direct consumer; the existing
`redai.py` presets remain purely symbolic/rule-based today.

## 7. Related Topics

[R503](R503-ai-decision-support.md) (AI Decision Support), `engine/redai.py`, [R507](R507-autonomous-planning-systems.md) (Autonomous Planning Systems), DOM-008 §3/§5.
