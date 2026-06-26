# R502 — Autonomy in Space Operations

> **Document ID:** R502
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** R501
> **Referenced By:** R507, R508
> **Produces:** the real-world autonomy-levels vocabulary for any future bus/payload autonomous-mode feature
> **Feature Mapping:** any future autonomous bus/payload behavior feature (e.g. autonomous safe-mode recovery beyond the existing `RecoverySystem`, autonomous collision avoidance)
> **Related Topics:** R501 (Human-AI Teaming, the general framing), `engine/recovery.py`
> (`RecoverySystem`, the existing deterministic-rule-based autonomy this topic's levels classify),
> R507 (Autonomous Planning Systems), R508 (Future Command and Control)

[↑ Tier R500 index](R500-index.md) · [Encyclopedia index](INDEX.md)

**DOM-008 §6 tag:** in-world AI (modeling a real spacecraft's onboard autonomy, distinct from any
coding-agent practice).

## 1. Purpose

Real spacecraft already carry meaningful onboard autonomy (autonomous safe-mode entry, autonomous
collision-avoidance maneuvers, increasingly autonomous mission planning on some platforms) —
independent of any "AI" framing, this is existing space-operations practice. This topic gives the
implementer the standard autonomy-levels vocabulary for classifying both the engine's existing
autonomous behavior (`RecoverySystem`'s rule-based safe-mode recovery) and any future addition, so a
new feature's autonomy level is a deliberate design choice rather than an accident of implementation.

## 2. Concepts

**Levels of autonomy, from human-in-the-loop to fully autonomous.** A standard spectrum: human
operates directly (no autonomy) → system recommends, human decides → system acts but human can
veto/override within a window → system acts and reports after the fact → fully autonomous, no human
notification — `RecoverySystem`'s existing safe-mode recovery sits toward the "acts and reports"
end for fault response, since the bus enters safe mode and recovers via documented rule-based passes
without per-event human sign-off, but the recovery rules themselves are fully deterministic and
documented (not adaptive/learned), which is a meaningfully different autonomy character than an
adaptive/learning autonomous system.

**Rule-based autonomy vs. adaptive/learned autonomy.** Real spacecraft autonomy today is
overwhelmingly rule-based (documented fault trees, deterministic thresholds) rather than adaptive/
learned — this matches this simulator's deterministic-engine constraint well: `RecoverySystem`'s
multi-pass recovery is exactly this kind of rule-based autonomy, fully legible to a White Cell
facilitator and replay-exact, in contrast to a hypothetical learned/adaptive autonomous controller
whose behavior would be harder to make legible or replay-exact.

**Autonomy appropriateness depends on the time-criticality and reversibility of the decision.** A
collision-avoidance maneuver decision (seconds-to-minutes window, often unreversible if missed) is a
classic case for higher autonomy in real operations; a mission-replanning decision (more time
available, more consequential, more reversible) is more often left at lower autonomy with a human
in the loop — this distinction is the basis for evaluating where a future autonomy feature in this
simulator should sit on the spectrum.

**Autonomy and the trust-calibration problem (R501) compound at the spacecraft level.** An operator
who doesn't understand what their own asset's safe-mode autonomy will or won't do under a given fault
condition is poorly equipped to predict their own asset's behavior — this is a distinct, asset-level
instance of the legibility concern R501 raises at the advisor level.

## 3. Operational Context

Levels of autonomy in spacecraft operations is established aerospace engineering and mission-
operations practice (most real operational satellites already carry some autonomous fault response),
not a speculative future-AI topic — this grounds any future feature extending the engine's autonomous
behavior in existing real-world practice rather than inventing new territory.

## 4. Implementation Guidance

- **Classify any future autonomous bus/payload feature by its autonomy level explicitly** (using the
  spectrum above) in its design documentation, the same way `RecoverySystem`'s existing rule-based
  recovery should be described as such if not already.
- **Prefer rule-based, deterministic autonomy over adaptive/learned autonomy for any new feature**,
  consistent with the engine's load-bearing determinism invariant (CLAUDE.md) — an adaptive/learned
  autonomous controller would be a significant departure from this constraint and should be flagged
  as such if ever proposed.
- **Place a new autonomous feature's autonomy level according to the decision's time-criticality and
  reversibility** — a time-critical, low-reversibility decision (collision avoidance) is the strongest
  candidate for higher autonomy; a higher-reversibility, more time-available decision should default
  to a lower autonomy level with explicit human sign-off.
- **Document, in any vignette or `intro_brief` referencing autonomous behavior, exactly what the
  asset's autonomy will and won't do** — per the legibility concern above, an operator should be able
  to predict their own asset's autonomous response to a documented fault condition.

## 5. Feature Mapping

Any future autonomous bus/payload behavior feature is the direct consumer; `engine/recovery.py`'s
existing `RecoverySystem` is the current rule-based-autonomy precedent.

## 6. Related Topics

R501 (Human-AI Teaming), `engine/recovery.py` (`RecoverySystem`), R507 (Autonomous Planning
Systems), R508 (Future Command and Control).
