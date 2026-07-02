# R203 — Game Theory

> **Document ID:** R203
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R202](R202-decision-theory.md)
> **Referenced By:** [R213](R213-signaling-theory.md), [R303](R303-deterrence-theory.md), [R304](R304-escalation-dynamics.md), [R308](R308-red-teaming-methodology.md)
> **Produces:** the strategic-interaction vocabulary behind Red/Blue asymmetric play
> **Feature Mapping:** FS-105 (Spacecraft Operations), DOM-003 (White Cell — Red posture design)
> **Related Topics:** [R202](R202-decision-theory.md) (Decision Theory), [R213](R213-signaling-theory.md) (Signaling Theory), [R303](R303-deterrence-theory.md) (Deterrence Theory), [R308](R308-red-teaming-methodology.md)
> (Red Teaming Methodology), DOM-008 §3 (Red AI design principles)

> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2

[↑ Tier R200 index](R200-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Red and Blue are not solving independent optimization problems — each cell's best action depends on
the other's (anticipated) action, and Red's behavior is itself parameterized doctrine (`redai.py`
presets), not a fixed environment. This topic gives the implementer the minimal game-theory
vocabulary needed to reason about that interaction correctly, distinct from single-agent decision
theory ([R202](R202-decision-theory.md)).

## 2. Scope

Covers the minimal game-theoretic vocabulary for Red/Blue strategic interaction: players/strategies/
payoffs, sequential vs. simultaneous-move structure, and information asymmetry (bluffing/pooling).
Does **not** cover single-agent decision criteria under risk/uncertainty ([R202](R202-decision-theory.md),
the foundation this topic extends), the signaling-specific vocabulary for how an action conveys
intent to an observer ([R213](R213-signaling-theory.md)), or the deterrence-specific application
([R303](R303-deterrence-theory.md)/[R304](R304-escalation-dynamics.md), Tier R300).

## 3. Concepts

**A game is defined by players, strategies, and payoffs — not by who "wins."** Red and Blue have
different, only partially-overlapping objective sets (vignette-specific `objectives`), and the
simulator does not require a zero-sum framing — a vignette where both cells can achieve their
distinct objectives is a valid, even common, design
([von Neumann, J. and Morgenstern, O., *Theory of Games and Economic Behavior*, 1944 — summarized in
Stanford Encyclopedia of Philosophy, "Game Theory"](https://plato.stanford.edu/entries/game-theory/)
([Wayback](https://web.archive.org/web/2026/https://plato.stanford.edu/entries/game-theory/))).

**Sequential vs. simultaneous-move games.** Most exchanges in this simulator are sequential with
imperfect information (Blue commits an order against an access window; Red's prior moves are
partially observed by Blue through custody, and vice versa) rather than simultaneous — this maps
directly to extensive-form game representations (a decision tree with information sets), not
simultaneous-move payoff matrices, and a future COA-analysis tool modeling Red/Blue interaction
should use the matching representation.

**Red's "strategy" is a doctrine preset, not optimal play.** `redai.py` presets are deliberately
*doctrinally-flavored and parameterized*, not a game-theoretically optimal adversary — per DOM-008
§3, this is intentional: a perfectly optimizing Red would not model real (imperfect, doctrine-bound)
adversary behavior, and would also be pedagogically uninstructive (an unbeatable optimal opponent
teaches frustration, not tradecraft).

**Bluffing and ambiguity as a strategic resource.** An ambiguous RPO approach (one of the five
existing inject templates, DOM-003 §4) is the concrete in-sim instance of a game-theoretic
information-asymmetry move — Red's true intent is deliberately withheld, forcing Blue to act on a
probability distribution over Red's possible objectives rather than a known type
— the formal "pooling equilibrium" case worked out in the extensive-form/imperfect-information game
literature Nash's equilibrium concept underlies
([Nash, J. F., "Equilibrium Points in n-Person Games," *PNAS* 36, 1950](https://pmc.ncbi.nlm.nih.gov/articles/PMC1063129/)
([Wayback](https://web.archive.org/web/2026/https://pmc.ncbi.nlm.nih.gov/articles/PMC1063129/))).

### Sources

- *von Neumann, J. and Morgenstern, O., "Theory of Games and Economic Behavior"* (1944), summarized
  in Stanford Encyclopedia of Philosophy, "Game Theory" — [live](https://plato.stanford.edu/entries/game-theory/)
  · [snapshot](https://web.archive.org/web/2026/https://plato.stanford.edu/entries/game-theory/)
  · accessed 2026-07-02.
- *Nash, J. F., "Equilibrium Points in n-Person Games," Proceedings of the National Academy of
  Sciences* 36 (1950) — [live](https://pmc.ncbi.nlm.nih.gov/articles/PMC1063129/)
  · [snapshot](https://web.archive.org/web/2026/https://pmc.ncbi.nlm.nih.gov/articles/PMC1063129/)
  · accessed 2026-07-02.

## 4. Operational Context

Real space-control competition is explicitly strategic in the game-theoretic sense: an adversary's
counterspace posture is itself a response to perceived defensive capability, and escalation/de-
escalation moves are read as signals about future intent, not just isolated actions — this is the
foundation both [R213](R213-signaling-theory.md) (Signaling Theory) and [R303](R303-deterrence-theory.md)/[R304](R304-escalation-dynamics.md) (Deterrence/Escalation) build on.

## 5. Implementation Guidance

- **A new Red doctrine preset should be documented as a strategy/parameter set within a stated game
  framing** (what does this preset assume about Blue's likely response?) so a future facilitator or
  assessment feature can reason about *why* a preset behaves as it does, not just *that* it does.
- **Don't design Red AI to perfectly best-respond to Blue's actual (not doctrine-typical) play** —
  per DOM-008 §3, this would make Red an optimal adversary rather than a credible doctrinal one,
  defeating the pedagogical purpose ([R308](R308-red-teaming-methodology.md)).
- **A future "Red intent" assessment or hint feature must stay within DOM-008 §4's advisor-only
  constraint** — surfacing a probability distribution over Red's likely objective is acceptable;
  resolving the ambiguity *for* the player is not.

## 6. Feature Mapping

DOM-003 (White Cell, Red posture design) and any future Red-AI-tuning feature are the direct
consumers; FS-105 (Spacecraft Operations) inherits the resulting Red behavior as the contested
environment.

## 7. Related Topics

[R202](R202-decision-theory.md) (Decision Theory, the single-agent foundation this topic extends), [R213](R213-signaling-theory.md) (Signaling Theory),
[R303](R303-deterrence-theory.md) (Deterrence Theory), [R308](R308-red-teaming-methodology.md) (Red Teaming Methodology, the doctrinal justification for why Red
must be genuinely adversarial rather than optimal).
