# R211 — Heuristics and Satisficing

> **Document ID:** R211
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R206](R206-bounded-rationality.md)
> **Referenced By:** DOM-002
> **Produces:** the vocabulary distinguishing a competent shortcut from a tradecraft gap in DOM-002's rubric
> **Feature Mapping:** FS-201 (Competency Assessment)
> **Related Topics:** [R206](R206-bounded-rationality.md) (Bounded Rationality — the theory this topic's mechanism implements), [R207](R207-cognitive-biases.md)
> (Cognitive Biases — the failure mode when a heuristic misfires), [R202](R202-decision-theory.md) (Decision Theory)

> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2

[↑ Tier R200 index](R200-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

[R206](R206-bounded-rationality.md) establishes that boundedly-rational operators satisfice rather than optimize; this topic gives
the implementer the mechanism — specific heuristics — so a future assessment feature can recognize
*which* heuristic an operator is applying and judge whether it was a reasonable choice given the
situation, rather than scoring all non-optimal play as undifferentiated error.

## 2. Scope

Covers the specific heuristic mechanisms (satisficing, recognition-primed decision-making,
representativeness, anchoring-and-adjustment-as-heuristic) that implement bounded rationality's
behavioral prediction. Does **not** cover bounded rationality as a theory ([R206](R206-bounded-rationality.md),
this topic's mechanism-level elaboration), the failure mode when a heuristic misfires into bias
([R207](R207-cognitive-biases.md)), or the idealized decision-theoretic contrast case ([R202](R202-decision-theory.md)).

## 3. Concepts

**Satisficing: stop searching once an option clears an acceptability bar.** Rather than enumerating
and ranking every possible window/target/configuration, an operator who finds an access window that
is "good enough" (adequate elevation, sufficient Δv margin) and commits, rather than continuing to
search for a theoretically superior option, is satisficing — and per [R206](R206-bounded-rationality.md), this is the realistic,
often correct, model of operator behavior under genuine time pressure ([R120](R120-access-window-and-geometry-planning.md)'s SLA-bound windows).
This "fast and frugal" framing — a simple, one-reason decision rule that matches or outperforms
exhaustive comparison under real time constraints — is itself a modeled family of algorithms, not
just an intuition
([Gigerenzer, G. and Goldstein, D. G., "Reasoning the Fast and Frugal Way: Models of Bounded Rationality," *Psychological Review* 103, 1996](https://www.dangoldstein.com/papers/FastFrugalPsychReview.pdf)
([Wayback](https://web.archive.org/web/2026/https://www.dangoldstein.com/papers/FastFrugalPsychReview.pdf))).

**Recognition-primed decision-making (RPD).** Experienced operators under time pressure often skip
explicit option-comparison entirely, recognizing a situation as a familiar pattern and acting on the
first workable option that pattern-matches, only checking it mentally rather than exhaustively
comparing alternatives. This is a *named, well-studied expert heuristic* (Klein's RPD model, developed
from studying fireground commanders under time pressure), not a
shortcut indicating inexperience — a future assessment rubric should be able to distinguish "fast,
pattern-matched, correct" (RPD-consistent expert behavior) from "fast, careless, wrong"
([Klein, G., "Naturalistic Decision Making and Wildland Firefighting," USDA Forest Service](https://www.fs.usda.gov/eng/pubs/htmlpubs/htm95512855/page13.htm)
([Wayback](https://web.archive.org/web/2026/https://www.fs.usda.gov/eng/pubs/htmlpubs/htm95512855/page13.htm))).

**The representativeness heuristic.** Judging probability by similarity to a known pattern rather
than by base rates — relevant to custody/attribution judgments ([R102](R102-space-domain-awareness.md), [R116](R116-cyber-operations-against-space-systems.md)): an ambiguous RPO
approach that "looks like" a known hostile pattern may be over-weighted as hostile even if the
actual base rate of hostile RPO in the scenario is low. Distinct from confirmation bias ([R207](R207-cognitive-biases.md)): this
is a pattern-matching shortcut, not motivated reasoning from a prior belief.

**Anchoring-and-adjustment as a deliberate planning heuristic, not just a bias.** Starting from a
known reference point (a previous vignette's typical access-window cadence, a doctrine preset's
expected aggressiveness) and adjusting from there is a legitimate, efficient planning heuristic when
the anchor is a reasonable prior — it becomes the [R207](R207-cognitive-biases.md) bias only when the adjustment is
insufficient given new, more diagnostic evidence.

### Sources

- *Gigerenzer, G. and Goldstein, D. G., "Reasoning the Fast and Frugal Way: Models of Bounded
  Rationality," Psychological Review* 103 (1996) — [live](https://www.dangoldstein.com/papers/FastFrugalPsychReview.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://www.dangoldstein.com/papers/FastFrugalPsychReview.pdf)
  · accessed 2026-07-02.
- *Klein, G., "Naturalistic Decision Making and Wildland Firefighting," USDA Forest Service* — [live](https://www.fs.usda.gov/eng/pubs/htmlpubs/htm95512855/page13.htm)
  · [snapshot](https://web.archive.org/web/2026/https://www.fs.usda.gov/eng/pubs/htmlpubs/htm95512855/page13.htm)
  · accessed 2026-07-02.

## 4. Operational Context

Real expert operators (pilots, SOC analysts, ship-handlers) are extensively studied as using exactly
these heuristics rather than formal decision-theoretic calculation, and "naturalistic decision
making" research (Klein et al.) treats fast, heuristic, experience-driven judgment as the *normal*
and often *superior* mode of expert performance under time pressure — not a degraded substitute for
optimization.

## 5. Implementation Guidance

- **A DOM-002 rubric should be able to credit fast, pattern-consistent decisions as competent
  (RPD-consistent) rather than only crediting slow, deliberate option-comparison** — a "time-to-
  decision" metric ([R208](R208-ooda-loops.md), DOM-002 §4) read in isolation would penalize exactly the expert behavior
  this topic identifies as often optimal.
- **A future tutorial/coaching-note feature (already present per `Vignette.coaching`) can
  legitimately teach a named heuristic explicitly** (e.g. "in this scenario, satisficing on the
  first window inside the SLA is usually correct — don't over-search") as part of progressive skill-
  building, distinct from teaching a bias-correction.
- **Don't build an assessment metric that infers "representativeness heuristic misfire" from
  outcome alone** — distinguishing a reasonable pattern-match from a base-rate-neglect error
  requires knowing the actual scenario base rate, which the engine has (ground truth) but the
  trainee didn't; score the *process* ([R206](R206-bounded-rationality.md)), and only an AAR-level facilitator judgment, not an
  automated metric, should attempt to characterize which heuristic was in play.

## 6. Feature Mapping

FS-201 (Competency Assessment) is the direct consumer.

## 7. Related Topics

[R206](R206-bounded-rationality.md) (Bounded Rationality, the theory), [R207](R207-cognitive-biases.md) (Cognitive Biases, the failure mode), [R202](R202-decision-theory.md) (Decision
Theory, the idealized contrast case).
