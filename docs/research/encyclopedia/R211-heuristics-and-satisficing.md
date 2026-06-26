# R211 — Heuristics and Satisficing

> **Document ID:** R211
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** R206
> **Referenced By:** DOM-002
> **Produces:** the vocabulary distinguishing a competent shortcut from a tradecraft gap in DOM-002's rubric
> **Feature Mapping:** FS-201 (Competency Assessment)
> **Related Topics:** R206 (Bounded Rationality — the theory this topic's mechanism implements), R207
> (Cognitive Biases — the failure mode when a heuristic misfires), R202 (Decision Theory)

[↑ Tier R200 index](R200-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

R206 establishes that boundedly-rational operators satisfice rather than optimize; this topic gives
the implementer the mechanism — specific heuristics — so a future assessment feature can recognize
*which* heuristic an operator is applying and judge whether it was a reasonable choice given the
situation, rather than scoring all non-optimal play as undifferentiated error.

## 2. Concepts

**Satisficing: stop searching once an option clears an acceptability bar.** Rather than enumerating
and ranking every possible window/target/configuration, an operator who finds an access window that
is "good enough" (adequate elevation, sufficient Δv margin) and commits, rather than continuing to
search for a theoretically superior option, is satisficing — and per R206, this is the realistic,
often correct, model of operator behavior under genuine time pressure (R120's SLA-bound windows).

**Recognition-primed decision-making (RPD).** Experienced operators under time pressure often skip
explicit option-comparison entirely, recognizing a situation as a familiar pattern and acting on the
first workable option that pattern-matches, only checking it mentally rather than exhaustively
comparing alternatives. This is a *named, well-studied expert heuristic* (Klein's RPD model), not a
shortcut indicating inexperience — a future assessment rubric should be able to distinguish "fast,
pattern-matched, correct" (RPD-consistent expert behavior) from "fast, careless, wrong."

**The representativeness heuristic.** Judging probability by similarity to a known pattern rather
than by base rates — relevant to custody/attribution judgments (R102, R116): an ambiguous RPO
approach that "looks like" a known hostile pattern may be over-weighted as hostile even if the
actual base rate of hostile RPO in the scenario is low. Distinct from confirmation bias (R207): this
is a pattern-matching shortcut, not motivated reasoning from a prior belief.

**Anchoring-and-adjustment as a deliberate planning heuristic, not just a bias.** Starting from a
known reference point (a previous vignette's typical access-window cadence, a doctrine preset's
expected aggressiveness) and adjusting from there is a legitimate, efficient planning heuristic when
the anchor is a reasonable prior — it becomes the R207 bias only when the adjustment is
insufficient given new, more diagnostic evidence.

## 3. Operational Context

Real expert operators (pilots, SOC analysts, ship-handlers) are extensively studied as using exactly
these heuristics rather than formal decision-theoretic calculation, and "naturalistic decision
making" research (Klein et al.) treats fast, heuristic, experience-driven judgment as the *normal*
and often *superior* mode of expert performance under time pressure — not a degraded substitute for
optimization.

## 4. Implementation Guidance

- **A DOM-002 rubric should be able to credit fast, pattern-consistent decisions as competent
  (RPD-consistent) rather than only crediting slow, deliberate option-comparison** — a "time-to-
  decision" metric (R208, DOM-002 §4) read in isolation would penalize exactly the expert behavior
  this topic identifies as often optimal.
- **A future tutorial/coaching-note feature (already present per `Vignette.coaching`) can
  legitimately teach a named heuristic explicitly** (e.g. "in this scenario, satisficing on the
  first window inside the SLA is usually correct — don't over-search") as part of progressive skill-
  building, distinct from teaching a bias-correction.
- **Don't build an assessment metric that infers "representativeness heuristic misfire" from
  outcome alone** — distinguishing a reasonable pattern-match from a base-rate-neglect error
  requires knowing the actual scenario base rate, which the engine has (ground truth) but the
  trainee didn't; score the *process* (R206), and only an AAR-level facilitator judgment, not an
  automated metric, should attempt to characterize which heuristic was in play.

## 5. Feature Mapping

FS-201 (Competency Assessment) is the direct consumer.

## 6. Related Topics

R206 (Bounded Rationality, the theory), R207 (Cognitive Biases, the failure mode), R202 (Decision
Theory, the idealized contrast case).
