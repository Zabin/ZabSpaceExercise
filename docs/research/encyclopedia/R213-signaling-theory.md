# R213 — Signaling Theory

> **Document ID:** R213
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R203](R203-game-theory.md)
> **Referenced By:** [R304](R304-escalation-dynamics.md), [R312](R312-space-strategy.md), [R318](R318-attribution-confidence-and-public-messaging.md)
> **Produces:** the vocabulary behind why an action's "message," not just its physical effect, matters in escalation dynamics
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R203](R203-game-theory.md) (Game Theory), [R304](R304-escalation-dynamics.md) (Escalation Dynamics — the direct application), [R117](R117-directed-energy-and-kinetic-effects.md)
> (Directed Energy and Kinetic Effects — the irreversible category where signaling stakes are
> highest)

> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2

[↑ Tier R200 index](R200-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

A kinetic engagement, a jamming footprint, or even a proximity-operations approach is read by the
opposing cell (and, doctrinally, by real-world observers) not only for its physical effect but as a
*signal* about intent and resolve. This topic gives the implementer the formal signaling-theory
vocabulary so that "this action also sends a message" is treated as a precise design constraint
(escalation, [R304](R304-escalation-dynamics.md)) rather than vague narrative color.

## 2. Scope

Covers signaling theory's core vocabulary (costly vs. cheap signals, pooling vs. separating
equilibria, the signal/index distinction, signal noise) as it applies to actions that carry both a
physical effect and a communicative meaning. Does **not** cover the game-theoretic foundation this
topic extends ([R203](R203-game-theory.md)), the escalation-specific application
([R304](R304-escalation-dynamics.md), Tier R300), or attribution-confidence-specific craft
([R318](R318-attribution-confidence-and-public-messaging.md), Tier R300).

## 3. Concepts

**A signal is an action whose value depends partly on how it's interpreted by an observer, not only
on its direct effect.** In game theory, signaling theory studies actions taken specifically (or
partly) because of what they communicate to another player about one's type, intent, or resolve —
distinct from an action chosen purely for its direct payoff. A related, load-bearing distinction:
*signals* are deliberate, potentially manipulable communications, while *indices* are unintentional,
harder-to-fake revelations
([Jervis, R., *The Logic of Images in International Relations*, Princeton University Press, 1970](https://archive.org/details/logicofimagesini0000jerv)
([Wayback](https://web.archive.org/web/2026/https://archive.org/details/logicofimagesini0000jerv))).

**Costly signals are more credible than cheap ones.** An action that is expensive or risky to take
(a kinetic engagement, genuinely costly in ammo/escalation risk per [R117](R117-directed-energy-and-kinetic-effects.md)) is a more credible signal
of resolve than a cheap one (a reversible jam, [R115](R115-electronic-warfare-in-space-operations.md)) — this is the formal reason the existing
reversible/irreversible asymmetry (MSTR-003 §5) doubles as a *signaling* asymmetry, not just a
risk-management one: kinetic action says something different to an adversary than EW action does,
independent of its tactical effect — the formal "costly signaling" result this topic borrows from
labor-market signaling economics, where costlier credentials are more informative precisely because
they are harder for a low-quality type to fake
([Spence, M., "Job Market Signaling," *Quarterly Journal of Economics* 87, 1973](https://www.sfu.ca/~allen/Spence.pdf)
([Wayback](https://web.archive.org/web/2026/https://www.sfu.ca/~allen/Spence.pdf))).

**Pooling vs. signaling equilibria.** If two genuinely different actor types (e.g., a Red cell
testing defenses vs. one preparing a real strike) would take the same observable action, an observer
cannot distinguish them from the action alone (a pooling equilibrium) — an ambiguous RPO approach
(DOM-003 §4's inject) is the concrete in-sim instance: a deliberately ambiguous action is one where
the designer has placed it in a pooling region by intent, and Blue's task is to gather enough
additional, costly-to-fake evidence (custody, [R102](R102-space-domain-awareness.md)) to separate the types.

**Signal jamming and noise.** An adversary or an inherently noisy environment can degrade a signal's
interpretability — relevant to why custody confidence (a noisy, decaying read) makes intent-signal
interpretation harder than ground truth would, and why attribution scoring ([R116](R116-cyber-operations-against-space-systems.md) §2) is itself
explicitly graded rather than binary, mirroring the inherent noisiness of real signaling.

### Sources

- *Jervis, R., The Logic of Images in International Relations* (Princeton University Press, 1970) — [live](https://archive.org/details/logicofimagesini0000jerv)
  · [snapshot](https://web.archive.org/web/2026/https://archive.org/details/logicofimagesini0000jerv)
  · accessed 2026-07-02.
- *Spence, M., "Job Market Signaling," Quarterly Journal of Economics* 87 (1973) — [live](https://www.sfu.ca/~allen/Spence.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.sfu.ca/~allen/Spence.pdf)
  · accessed 2026-07-02.

## 4. Operational Context

Real deterrence and crisis-signaling doctrine treats actions in contested domains as inherently
dual-purpose — a "demonstration" ASAT test or an RPO approach is read internationally as a signal
about resolve and capability, not merely assessed for its direct kinetic/operational effect, which is
precisely why real escalation-management doctrine (and the 2022 ASAT-test moratorium cited in
[`research/07-legal-norms-and-roe.md`](../07-legal-norms-and-roe.md)) treats the *signaling* dimension of an action as load-bearing.

## 5. Implementation Guidance

- **A new effect category or capability should state explicitly what it signals, not only what it
  does** — per [R304](R304-escalation-dynamics.md)/DOM-009 §4, an escalation-dynamics feature needs this stated to compute an
  escalation weight correctly (`PAYLOADS`' existing `escalation_weight` field in `cyber.py` is the
  concrete precedent: it already encodes a signaling-cost judgment, not just a physical-effect
  judgment).
- **A deliberately ambiguous inject (pooling-equilibrium design, like the existing RPO inject) should
  stay genuinely ambiguous in its engine-level data** — don't let an implementation detail (e.g. a
  hidden flag distinguishing "this is the hostile variant") leak into anything Blue can query,
  or the pooling equilibrium the inject is designed to create collapses by implementation accident.
- **A future Red-intent-signal assessment feature must stay within DOM-008 §4's advisor constraint**
  — surfacing "this pattern of behavior is consistent with signal type X with some uncertainty" is
  acceptable; resolving the signal for the player is not.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer for any feature involving escalation-sensitive
effect categories.

## 7. Related Topics

[R203](R203-game-theory.md) (Game Theory, the formal foundation), [R304](R304-escalation-dynamics.md) (Escalation Dynamics, the direct application), [R117](R117-directed-energy-and-kinetic-effects.md)
(the highest-stakes signaling category), DOM-009 §4 (legal/ROE load-bearing norms).
