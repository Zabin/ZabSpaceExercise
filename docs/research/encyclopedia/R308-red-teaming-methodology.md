# R308 — Red Teaming Methodology

> **Document ID:** R308
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R307](R307-wargaming-theory.md)
> **Referenced By:** DOM-003, DOM-008, [R319](R319-red-behavior-validation-methodology.md)
> **Produces:** the doctrinal justification for "Red must be genuinely adversarial" (DOM-003 §7, DOM-008 §3)
> **Feature Mapping:** FS-106 (White Cell Dashboard), Red doctrine presets (`redai.py`)
> **Related Topics:** [R307](R307-wargaming-theory.md) (Wargaming Theory), [R203](R203-game-theory.md) (Game Theory), DOM-003 §7 (the direct consumer),
> DOM-008 §3 (Red AI design principles)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 1

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-003 §7 already asserts "an unconvincing or passive Red teaches a false sense of security" as a
design principle for `redai.py` doctrine presets, citing this topic. This document supplies the
red-teaming methodology that backs that assertion, so future preset design and White-Cell-as-Red
facilitation decisions are grounded in the actual doctrine, not just an inherited assertion.

## 2. Scope

Covers: the structural-independence and credibility safeguards that make a red team's findings
trustworthy, and the distinction between doctrinally-plausible adversary modeling and worst-case
adversary modeling. Does **not** cover: the broader wargaming-validity question of what an exercise's
outcome can be claimed to demonstrate (that is [R307](R307-wargaming-theory.md)) or the
game-theoretic argument for bounded-rational rather than optimal adversary play (that is
[R203](R203-game-theory.md), Game Theory).

## 3. Concepts

**Red teaming's core purpose: surface blind spots a friendly-only perspective cannot see.** Micah
Zenko's [*Red Team: How to Succeed By Thinking Like the Enemy*](https://www.basicbooks.com/titles/micah-zenko/red-team/9780465048946/)
(Basic Books, 2015) defines red-teaming as a structured process that seeks to better understand the
interests, intentions, and capabilities of an institution or potential competitor through
simulations, vulnerability probes, and alternative analysis — a red team's value comes specifically
from genuinely adopting the adversary's incentives, doctrine, and decision logic rather than a
watered-down or predictable version of it. A red team that plays to lose, or that telegraphs intent,
defeats the entire methodology's purpose, which is exactly DOM-003 §7's concern about a passive Red.

**Structural independence as a credibility safeguard.** The UK Ministry of Defence's
[*Red Teaming Handbook*](https://www.gov.uk/government/publications/a-guide-to-red-teaming) (3rd
ed., Development, Concepts and Doctrine Centre, 2021) emphasizes giving the red team genuine
latitude and protecting it from pressure to "go easy," and warns that a red team whose findings are
shaped to support a predetermined conclusion has lost its analytic value. The doctrinal parallel in
this simulator is `redai.py`'s presets being data-parameterized doctrine (DOM-008 §3) rather than
hand-tuned per-vignette to guarantee a particular Blue outcome; a preset tuned specifically to let
Blue win a given vignette has compromised this independence in exactly the way the Handbook warns
against.

**Red teaming is not the same as worst-case adversary modeling.** Zenko (2015) and the MOD Handbook
both distinguish a red team playing a *doctrinally plausible* adversary, calibrated to real-world
tactics and capability, from an omniscient, maximally optimal one ([R203](R203-game-theory.md)
already makes this point from the game-theory side) — a Red preset that is unbeatable or that has
god-view-derived information is not red-teaming, it's an unfair obstacle, and fails the methodology
in the opposite direction from passivity.

**Red teaming generates findings that must be fed back, not just survived.** Zenko (2015) frames the
methodology's output as meant to inform improvement — a finding from a red-team exercise should
change a real defensive posture or doctrine — the AAR's purpose (MSTR-003 §6) is the direct analog: a
vignette "loss" against a credible Red is exactly the desired outcome if it produces a debrief
insight Blue carries forward, not a result to be avoided by softening Red.

### Sources

- *Micah Zenko, Red Team: How to Succeed By Thinking Like the Enemy* (Basic Books, 2015) — [live](https://www.basicbooks.com/titles/micah-zenko/red-team/9780465048946/)
  · [snapshot](https://web.archive.org/web/2026/https://www.basicbooks.com/titles/micah-zenko/red-team/9780465048946/)
  · accessed 2026-06-27.
- *UK Ministry of Defence, Development, Concepts and Doctrine Centre, Red Teaming Handbook* (3rd ed.,
  2021) — [live](https://www.gov.uk/government/publications/a-guide-to-red-teaming)
  · [snapshot](https://web.archive.org/web/2026/https://www.gov.uk/government/publications/a-guide-to-red-teaming)
  · accessed 2026-06-27.

## 4. Operational Context

Formal red-teaming (in cybersecurity, in military exercise design, in the original RAND wargaming
tradition) is institutionally protected and resourced specifically because organizations have a
documented, recurring tendency to unconsciously soften the adversary role unless deliberately
prevented from doing so — this is precisely the failure mode DOM-003 §7 is naming for this
simulator's Red-cell/Red-AI design.

## 5. Implementation Guidance

- **A new or revised `redai.py` doctrine preset must be evaluated against doctrinal plausibility, not
  against "does it let Blue win the intended way"** — tuning Red specifically to validate a vignette's
  intended solution path is the credibility-compromising move §3 warns against; if a vignette's
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

## 6. Feature Mapping

FS-106 (White Cell Dashboard) and `redai.py` doctrine-preset design are the direct consumers.

## 7. Related Topics

[R307](R307-wargaming-theory.md) (Wargaming Theory, the broader validity context), [R203](R203-game-theory.md) (Game Theory, why Red should be
doctrinally-credible rather than optimal), DOM-003 §7, DOM-008 §3.
