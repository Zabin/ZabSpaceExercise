# R308 — Red Teaming Methodology

> **Document ID:** R308
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R307](R307-wargaming-theory.md)
> **Referenced By:** DOM-003, DOM-008
> **Produces:** the doctrinal justification for "Red must be genuinely adversarial" (DOM-003 §7, DOM-008 §3)
> **Feature Mapping:** FS-106 (White Cell Dashboard), Red doctrine presets (`redai.py`)
> **Related Topics:** [R307](R307-wargaming-theory.md) (Wargaming Theory), [R203](R203-game-theory.md) (Game Theory), DOM-003 §7 (the direct consumer),
> DOM-008 §3 (Red AI design principles)

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-003 §7 already asserts "an unconvincing or passive Red teaches a false sense of security" as a
design principle for `redai.py` doctrine presets, citing this topic. This document supplies the
red-teaming methodology that backs that assertion, so future preset design and White-Cell-as-Red
facilitation decisions are grounded in the actual doctrine, not just an inherited assertion.

## 2. Concepts

**Red teaming's core purpose: surface blind spots a friendly-only perspective cannot see.** A red
team's value comes specifically from genuinely adopting the adversary's incentives, doctrine, and
decision logic rather than a watered-down or predictable version of it — a red team that plays to
lose, or that telegraphs intent, defeats the entire methodology's purpose, which is exactly DOM-003
§7's concern about a passive Red.

**Structural independence as a credibility safeguard.** Real red-teaming practice emphasizes giving
the red team genuine latitude and protecting it from pressure to "go easy" — the doctrinal parallel
in this simulator is `redai.py`'s presets being data-parameterized doctrine (DOM-008 §3) rather than
hand-tuned per-vignette to guarantee a particular Blue outcome; a preset tuned specifically to let
Blue win a given vignette has compromised this independence.

**Red teaming is not the same as worst-case adversary modeling.** A red team plays a *doctrinally
plausible* adversary, calibrated to real-world tactics/capability, not an omniscient, maximally
optimal one ([R203](R203-game-theory.md) already makes this point from the game-theory side) — a Red preset that is
unbeatable or that has god-view-derived information is not red-teaming, it's an unfair obstacle, and
fails the methodology in the opposite direction from passivity.

**Red teaming generates findings that must be fed back, not just survived.** The methodology's
output is meant to inform improvement (a finding from a red-team exercise should change a real
defensive posture/doctrine) — the AAR's purpose (MSTR-003 §6) is the direct analog: a vignette
"loss" against a credible Red is exactly the desired outcome if it produces a debrief insight Blue
carries forward, not a result to be avoided by softening Red.

## 3. Operational Context

Formal red-teaming (in cybersecurity, in military exercise design, in the original RAND wargaming
tradition) is institutionally protected and resourced specifically because organizations have a
documented, recurring tendency to unconsciously soften the adversary role unless deliberately
prevented from doing so — this is precisely the failure mode DOM-003 §7 is naming for this
simulator's Red-cell/Red-AI design.

## 4. Implementation Guidance

- **A new or revised `redai.py` doctrine preset must be evaluated against doctrinal plausibility, not
  against "does it let Blue win the intended way"** — tuning Red specifically to validate a vignette's
  intended solution path is the credibility-compromising move §2 warns against; if a vignette's
  intended solution doesn't work against a doctrinally faithful Red, the vignette's design (not Red's
  aggressiveness) should change.
- **A Red preset's information access must stay within the same fog-of-war model Blue operates
  under** (no god-view-derived decision logic) — per DOM-008 §3's determinism/legibility principles,
  giving Red an unfair epistemic advantage is a different failure mode from passivity, but equally
  invalidates the red-teaming exercise.
- **A future feature letting White Cell hand-play Red (DOM-003 §7) should include facilitation
  guidance reminding the facilitator of this topic's "don't soften the adversary" principle** — the
  human-Red failure mode is the same one a poorly-tuned preset exhibits, just human-driven instead
  of parameter-driven.

## 5. Feature Mapping

FS-106 (White Cell Dashboard) and `redai.py` doctrine-preset design are the direct consumers.

## 6. Related Topics

[R307](R307-wargaming-theory.md) (Wargaming Theory, the broader validity context), [R203](R203-game-theory.md) (Game Theory, why Red should be
doctrinally-credible rather than optimal), DOM-003 §7, DOM-008 §3.
