# R307 — Wargaming Theory

> **Document ID:** R307
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** —
> **Referenced By:** [R308](R308-red-teaming-methodology.md), DOM-003
> **Produces:** the validity vocabulary behind what conclusions a White-Cell-run exercise can responsibly support
> **Feature Mapping:** FS-106 (White Cell Dashboard), DOM-003
> **Related Topics:** [R308](R308-red-teaming-methodology.md) (Red Teaming Methodology), DOM-003 (White Cell Framework, the direct
> consumer), DOM-005 (Validation Framework)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 1

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-003 §10 already cites this topic by ID for "what makes a wargame's conclusions valid, informs
how much White Cell intervention is appropriate before the exercise stops teaching what it claims
to." This document supplies that content: the methodological literature on what a wargame can and
cannot validly demonstrate, so White Cell facilitation guidance and any future assessment claim
about exercise outcomes are appropriately bounded.

## 2. Scope

Covers: the wargame-as-argument vs. wargame-as-oracle distinction, insight-generation vs. analytical
wargaming purposes, the facilitator-intervention validity question, and free play vs. rigid
wargaming. Does **not** cover: the adversarial role-play design specifically (that is
[R308](R308-red-teaming-methodology.md), Red Teaming Methodology) or the statistical rigor an
analytical claim across many runs would require (that is [R401](R401-experimental-design-and-controls.md)-[R413](R413-data-analysis-and-reporting.md)).

## 3. Concepts

**Wargames are not predictive models; they are structured arguments.** Peter P. Perla's
[*The Art of Wargaming: A Guide for Professionals and Hobbyists*](https://www.usni.org/press/books/art-wargaming)
(Naval Institute Press, 1990; rev. ed. with John Curry, History of Wargaming Project, 2011) — the
text widely regarded as the foundational treatment of professional wargaming methodology and used at
US service academies and war colleges — defines wargaming as an applied discipline encompassing the
creation, use, synthesis, and analysis of wargames to conduct research, explore concepts, develop and
test hypotheses, and dynamically communicate insights, explicitly distinguishing this from
prediction: a wargame cannot predict nor fully replicate a real-world scenario, but it provides
insight into how participants make decisions that no other method affords short of actual combat.
Treating "Blue won the exercise" as evidence Blue's real-world doctrine is sound is a well-documented
wargaming-validity error; the legitimate claim is narrower: "under these specific conditions and
rules, this is what these specific participants did and why."

**Insight-generation vs. analytical wargaming.** This simulator is squarely a PME/educational
wargame whose purpose is insight-generation for *trainees* (practicing judgment, per MSTR-003) —
distinct from analytical wargaming whose purpose is generating *generalizable findings* for force-
design or doctrine decisions, a distinction Perla's framework treats as governing what conclusions a
given game can support. DOM-004/DOM-005's research-use extension would, if pursued, need to
explicitly state which mode a given study is operating in, since the validity standards differ
sharply (an analytical claim needs the rigor [R401](R401-experimental-design-and-controls.md)-[R413](R413-data-analysis-and-reporting.md) describe; a PME insight does not, but also
shouldn't be oversold as one).

**The facilitator's intervention changes what the game can validly demonstrate.** Every White Cell
inject, clock adjustment, or hand-tuned Red posture (DOM-003 §4-7) is a deliberate departure from a
"closed," fully-scripted exercise — appropriate and even necessary for pedagogy, but it means the
exercise's outcome reflects facilitator choices as much as participant skill, and any claim drawn
from the outcome must account for that (this is precisely why DOM-003 §10 frames facilitator
restraint as a wargaming-validity question, not just a facilitation-style preference).

**Free play vs. rigid (scripted) wargaming.** Perla's typology distinguishes a rigid wargame, which
follows a pre-determined script regardless of participant action (useful for consistent, comparable
training across cohorts but poor at teaching genuine adaptive judgment), from free play, which lets
outcomes diverge based on participant decisions (better for the judgment-under-uncertainty pedagogy
MSTR-003 describes, harder to compare across runs). This simulator's deterministic-per-seed engine
with a live facilitator is a hybrid: free play within a session, but replayable/comparable via AAR
branch-compare (P7) across alternate decision points within the *same* recorded run.

### Sources

- *Peter P. Perla, The Art of Wargaming: A Guide for Professionals and Hobbyists* (Naval Institute
  Press, 1990; rev. ed. 2011) — [live](https://www.usni.org/press/books/art-wargaming)
  · [snapshot](https://web.archive.org/web/2026/https://www.usni.org/press/books/art-wargaming)
  · accessed 2026-06-27.

## 4. Operational Context

Professional wargaming design literature treats validity-of-claims as the central methodological
question (what can this specific game legitimately tell us, given its abstractions and the mode it
was run in) — a discipline that exists precisely because wargames are persuasive and easy to
over-interpret, and the field's own internal critique is "we have seen wargame conclusions oversold
as predictive when they were never designed to be."

## 5. Implementation Guidance

- **Any AAR or assessment feature must avoid language implying a single exercise run "proves" a
  trainee's real-world competency** — per §3's insight-generation framing, report observed behavior
  in *this* run, with the bounded claim that is actually defensible, not an inflated one.
- **A future research-use feature (FS-301, DOM-004) studying exercise outcomes across many runs must
  explicitly declare whether it's making an insight-generation claim (PME-appropriate) or an
  analytical claim (requiring [R401](R401-experimental-design-and-controls.md)-[R413](R413-data-analysis-and-reporting.md)'s full rigor)** — and must not silently upgrade the former
  into the latter.
- **White Cell facilitation guidance (DOM-003) should explicitly note that heavy intervention,
  while pedagogically valid, narrows what a given run's outcome can be used to claim** — a feature
  exposing "how much was this run facilitator-steered" (e.g. inject count/timing in the AAR) would
  usefully support this kind of honest self-assessment.

## 6. Feature Mapping

DOM-003 (White Cell Framework) and FS-106 (White Cell Dashboard) are the direct consumers.

## 7. Related Topics

[R308](R308-red-teaming-methodology.md) (Red Teaming Methodology, the adversarial-design half of wargaming validity), DOM-003 (the
direct consumer), DOM-005 (Validation Framework, the rigor standard for any analytical claim).
