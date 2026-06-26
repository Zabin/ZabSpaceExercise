# R307 — Wargaming Theory

> **Document ID:** R307
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** —
> **Referenced By:** R308, DOM-003
> **Produces:** the validity vocabulary behind what conclusions a White-Cell-run exercise can responsibly support
> **Feature Mapping:** FS-106 (White Cell Dashboard), DOM-003
> **Related Topics:** R308 (Red Teaming Methodology), DOM-003 (White Cell Framework, the direct
> consumer), DOM-005 (Validation Framework)

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-003 §10 already cites this topic by ID for "what makes a wargame's conclusions valid, informs
how much White Cell intervention is appropriate before the exercise stops teaching what it claims
to." This document supplies that content: the methodological literature on what a wargame can and
cannot validly demonstrate, so White Cell facilitation guidance and any future assessment claim
about exercise outcomes are appropriately bounded.

## 2. Concepts

**Wargames are not predictive models; they are structured arguments.** A single wargame run, even a
well-designed one, does not predict what would happen in a real conflict — it produces an argument,
grounded in the chosen rules/scenario/participant decisions, about a *possibility space*. Treating
"Blue won the exercise" as evidence Blue's real-world doctrine is sound is a well-documented
wargaming-validity error (the "wargame as oracle" fallacy); the legitimate claim is narrower:
"under these specific conditions and rules, this is what these specific participants did and why."

**Insight-generation vs. analytical wargaming.** This simulator is squarely a PME/educational
wargame whose purpose is insight-generation for *trainees* (practicing judgment, per MSTR-003) —
distinct from analytical wargaming whose purpose is generating *generalizable findings* for force-
design or doctrine decisions. DOM-004/DOM-005's research-use extension would, if pursued, need to
explicitly state which mode a given study is operating in, since the validity standards differ
sharply (an analytical claim needs the rigor R401-R413 describe; a PME insight does not, but also
shouldn't be oversold as one).

**The facilitator's intervention changes what the game can validly demonstrate.** Every White Cell
inject, clock adjustment, or hand-tuned Red posture (DOM-003 §4-7) is a deliberate departure from a
"closed," fully-scripted exercise — appropriate and even necessary for pedagogy, but it means the
exercise's outcome reflects facilitator choices as much as participant skill, and any claim drawn
from the outcome must account for that (this is precisely why DOM-003 §10 frames facilitator
restraint as a wargaming-validity question, not just a facilitation-style preference).

**Free play vs. rigid (scripted) wargaming.** A rigid wargame follows a pre-determined script
regardless of participant action (useful for consistent, comparable training across cohorts but
poor at teaching genuine adaptive judgment); free play lets outcomes diverge based on participant
decisions (better for the judgment-under-uncertainty pedagogy MSTR-003 describes, harder to compare
across runs). This simulator's deterministic-per-seed engine with a live facilitator is a hybrid:
free play within a session, but replayable/comparable via AAR branch-compare (P7) across alternate
decision points within the *same* recorded run.

## 3. Operational Context

Professional wargaming design literature treats validity-of-claims as the central methodological
question (what can this specific game legitimately tell us, given its abstractions and the mode it
was run in) — a discipline that exists precisely because wargames are persuasive and easy to
over-interpret, and the field's own internal critique is "we have seen wargame conclusions oversold
as predictive when they were never designed to be."

## 4. Implementation Guidance

- **Any AAR or assessment feature must avoid language implying a single exercise run "proves" a
  trainee's real-world competency** — per §2's insight-generation framing, report observed behavior
  in *this* run, with the bounded claim that is actually defensible, not an inflated one.
- **A future research-use feature (FS-301, DOM-004) studying exercise outcomes across many runs must
  explicitly declare whether it's making an insight-generation claim (PME-appropriate) or an
  analytical claim (requiring R401-R413's full rigor)** — and must not silently upgrade the former
  into the latter.
- **White Cell facilitation guidance (DOM-003) should explicitly note that heavy intervention,
  while pedagogically valid, narrows what a given run's outcome can be used to claim** — a feature
  exposing "how much was this run facilitator-steered" (e.g. inject count/timing in the AAR) would
  usefully support this kind of honest self-assessment.

## 5. Feature Mapping

DOM-003 (White Cell Framework) and FS-106 (White Cell Dashboard) are the direct consumers.

## 6. Related Topics

R308 (Red Teaming Methodology, the adversarial-design half of wargaming validity), DOM-003 (the
direct consumer), DOM-005 (Validation Framework, the rigor standard for any analytical claim).
