# R506 — Machine Reasoning

> **Document ID:** R506
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** R503
> **Referenced By:** R507
> **Produces:** the symbolic-vs-sub-symbolic vocabulary for evaluating any future "smarter Red" or planning-assistance proposal against this engine's determinism invariant
> **Feature Mapping:** any future `redai.py` enhancement or planning-assistance feature proposing reasoning beyond the current rule-based doctrine presets
> **Related Topics:** R503 (AI Decision Support), `engine/redai.py` (the existing rule-based
> reasoning this topic contrasts with more sophisticated approaches), R507 (Autonomous Planning
> Systems), DOM-008 §3/§5

[↑ Tier R500 index](R500-index.md) · [Encyclopedia index](INDEX.md)

**DOM-008 §6 tag:** both — directly relevant to in-world AI (a future `redai.py` enhancement) and to
coding-agent practice (§5's note about an agent extending Red's reasoning).

## 1. Purpose

`redai.py`'s current doctrine presets are rule-based/data-parameterized (DOM-008 §3). If a future
proposal ever suggests making Red's (or a future advisor's) reasoning "smarter" via a more
sophisticated reasoning approach, this topic supplies the vocabulary to evaluate that proposal against
what it would actually require — particularly whether it's compatible with the engine's determinism
invariant, which is the single most load-bearing constraint any such proposal must clear.

## 2. Concepts

**Symbolic reasoning: explicit rules and logical inference over structured representations.** A
rule-based doctrine preset (the existing `redai.py` pattern: data-parameterized thresholds and
decision rules) is symbolic reasoning — its logic is inspectable, its behavior is traceable to a
specific rule firing, and it is naturally compatible with the engine's determinism and legibility
requirements (DOM-008 §3).

**Sub-symbolic reasoning: learned statistical models (e.g. neural networks) without explicit rules.**
A sub-symbolic approach (e.g. a trained policy network deciding Red's actions) trades inspectability
and determinism for potentially more sophisticated/adaptive behavior — this is fundamentally harder
to reconcile with the engine's `(initial_state, eventlog, seed) → byte-identical state` invariant
(CLAUDE.md) unless the trained model itself is frozen and treated as a pure deterministic function of
its inputs, and is much harder to make legible to a White Cell facilitator (DOM-008 §3's legibility
principle) than a rule-based preset's named parameters.

**Hybrid approaches: sub-symbolic perception/sub-symbolic feeding a symbolic decision layer.** Some
real-world systems use a learned model to interpret noisy input and a symbolic rule layer to make the
actual decision — a hypothetical hybrid Red-AI enhancement (e.g. a learned model interpreting Blue's
behavior pattern, feeding into the existing rule-based decision presets) would inherit the
determinism/legibility concerns of whichever layer actually drives the decision.

**The reasoning-approach choice is independent of the Human-AI-teaming and decision-support
constraints (R501/R503).** Choosing symbolic over sub-symbolic reasoning is a determinism/legibility
question (DOM-008 §3); the advisor-not-decider constraint (DOM-008 §4) is a decision-authority
question — a future proposal could in principle satisfy one without the other, and both should be
checked independently.

## 3. Operational Context

The symbolic vs. sub-symbolic distinction is foundational to AI research broadly, and the specific
tension this topic names — sub-symbolic methods' typical opacity and non-determinism vs. this
project's hard determinism/legibility requirements — is exactly the kind of tradeoff real defense-AI
programs have had to confront when integrating machine-learned systems into contexts requiring
auditable, explainable, and reproducible behavior (e.g. test-and-evaluation requirements for
military AI systems).

## 4. Implementation Guidance

- **Any future proposal to make `redai.py` "smarter" via a sub-symbolic/learned approach must be
  checked against the engine's determinism invariant before being pursued** — per CLAUDE.md, this is
  non-negotiable; a learned model must be frozen and treated as a pure deterministic function, and
  even then loses much of the legibility a rule-based preset has.
- **Prefer symbolic, rule-based extensions to `redai.py`'s existing pattern over sub-symbolic
  alternatives**, consistent with DOM-008 §3's legibility principle — a more sophisticated rule set
  (more conditions, more nuanced thresholds) is a smaller, more auditable step than introducing a
  learned model.
- **Coding-agent note (DOM-008 §5):** an agent asked to make Red "smarter" should default to symbolic
  rule extension and should explicitly flag, rather than silently implement, any proposal that would
  require relaxing determinism for a sub-symbolic approach.
- **Evaluate the reasoning-approach question (this topic) and the decision-authority question
  (DOM-008 §4/R503) independently** for any future AI-related proposal — satisfying one does not
  imply the other.

## 5. Feature Mapping

Any future `redai.py` enhancement or planning-assistance feature is the direct consumer; the existing
`redai.py` presets remain purely symbolic/rule-based today.

## 6. Related Topics

R503 (AI Decision Support), `engine/redai.py`, R507 (Autonomous Planning Systems), DOM-008 §3/§5.
