# R605 — Learning-Path & Progression Design

> **Document ID:** R605
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R601](R601-instructional-systems-design.md), [R604](R604-cognitive-load-and-scaffolding.md)
> **Referenced By:** none yet (a leaf topic; downstream consumers are training-artifact skills, not
> further R6xx topics)
> **Produces:** the theoretical grounding for `training/16-learning-path.md`'s rung structure and
> ordering rationale
> **Feature Mapping:** FR-11310 (sequenced learning path), FR-11320 (per-rung manual linkage)
> **Related Topics:** [R601](R601-instructional-systems-design.md) (backward design, applied here to
> multi-exercise sequencing), [R604](R604-cognitive-load-and-scaffolding.md) (load-scaffolding within
> one exercise, extended here across exercises), `docs/training/16-learning-path.md` (this topic's
> direct implementation)

> **Verification note (this authoring pass):** citations below were sourced via live web search and
> corroborated across ≥2 independent results per claim; direct WebFetch of source pages was blocked
> by this session's egress policy (proxy denial on external hosts, per `/root/.ccr/README.md`) and is
> deferred to this corpus's separate formal verification pass
> ([`../10-sources-and-methodology.md`](../10-sources-and-methodology.md) §5.3).

> **Last Reviewed:** 2026-07-04
> **Primary Sources Consulted:** 3

[↑ Tier R600 index](R600-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

The owner's own framing (2026-07-04, recorded in GDS-01's "Training-corpus elevation" section): "the
provided vignettes are designed to walk new users through their learning path from the very basic
intro to each satellite mission set." `training/16-learning-path.md` already implements a four-stage
rung structure (onboarding → mechanics ladder → mission-set/doctrine tracks → depth/novelty), but
without a stated theory the ordering choices (why this vignette before that one, why part-task
mission-set tracks come *after* the core ladder) are just one author's judgment call. This topic
supplies that theory — deliberate practice, part-task vs. whole-task training, and mastery-gated
progression — so future rung additions have a principled basis to extend from.

## 2. Scope

Covers progression-design theory: deliberate practice's requirement for effortful, feedback-rich
repetition; the part-task/whole-task training distinction and when to break a complex skill into
practiced sub-parts vs. train it as an integrated whole; and mastery learning's criterion-referenced
gating (advance only after demonstrating sufficient competence). Does **not** cover backward design's
general method (applied here, not re-derived — [R601](R601-instructional-systems-design.md)),
within-exercise load management ([R604](R604-cognitive-load-and-scaffolding.md)), or competency
measurement mechanics ([R607](R607-assessment-of-learning-in-wargames.md)).

## 3. Concepts

**Deliberate practice: expertise requires effortful, feedback-rich repetition on tasks just past
current competence — not mere exposure.** Ericsson, Krampe & Tesch-Römer's foundational study of
expert musicians found that accumulated deliberate practice — not innate talent — accounted for most
of the difference between skill levels, where "deliberate" specifically means practice on tasks
designed for the learner's current level, with immediate feedback, not simply repeated performance
([Ericsson, K. A., Krampe, R. Th., & Tesch-Römer, C. (1993). The Role of Deliberate Practice in the
Acquisition of Expert Performance. *Psychological Review*, 100, 363-406](https://pmc.ncbi.nlm.nih.gov/articles/PMC6731745/),
a 2019 replication/re-analysis corroborating the original finding's core claim while refining its scope).
Applied to this corpus: a vignette a trainee can already win without new judgment is not deliberate
practice, no matter how much time they spend on it — each rung must demand something the *previous*
rung didn't.

**Part-task training: isolate a sub-skill before demanding it inside the full task — but not always.**
Van Merriënboer's 4C/ID model (also grounding [R601](R601-instructional-systems-design.md)/
[R604](R604-cognitive-load-and-scaffolding.md)) explicitly names **part-task practice** as one of its
four components alongside whole learning tasks, used specifically for recurrent sub-skills that need
automatization (e.g., a specific procedure performed so often it should become near-automatic) —
distinct from **whole-task learning**, used for the non-recurrent, judgment-heavy skills that must be
practiced integrated from the start because isolating them loses exactly the integration-and-judgment
that is the actual point ([van Merriënboer, J. J. G., & Kirschner, P. A. *Ten Steps to Complex
Learning*](https://www.4cid.org/); [Blueprints for complex learning: The 4C/ID-model,
*Educational Technology Research and Development*](https://link.springer.com/article/10.1007/BF02504993)).
This directly justifies the learning path's own split: the mission-set tracks (Stage 2 — SAR ISR,
SIGINT geolocation, weather-collection cadence) are legitimately **part-task** (each isolates one
payload specialty's recurrent procedure), while the canonical ladder (Stage 1) is legitimately
**whole-task** (each rung is a complete, judgment-heavy exercise combining multiple mechanics, because
space-control decision-making is exactly the non-recurrent, integrated skill 4C/ID says should not be
decomposed).

**Mastery learning: advance on demonstrated competence, not elapsed time.** Bloom's mastery-learning
model holds that nearly all learners can reach a high competence level given the right conditions and
enough time — the design implication is criterion-referenced gating (a learner advances after
demonstrating sufficient mastery of prerequisite material, with targeted remediation otherwise) rather
than a fixed-pace curriculum that moves everyone together regardless of readiness
([Bloom, B. S. (1968). Learning for Mastery. *Evaluation Comment*, 1, 1-12](https://dl.icdst.org/pdfs/files1/3b3c79918ad75a1b2978742716506b44.pdf)).
The learning path's own "assign a rung matched to the trainee's level, not always rung 0" facilitator
guidance is already a mastery-learning-compatible design; this topic makes explicit that a *hard floor*
at Stage 0 (interface onboarding) is correct — interface competence is a genuine prerequisite everyone
needs regardless of prior domain expertise — while the rest of the path should remain masterable
out-of-order for a trainee who can demonstrate the prerequisite is already met.

### Sources

- *Ericsson, K. A., Krampe, R. Th., & Tesch-Römer, C. (1993). The Role of Deliberate Practice in the Acquisition of Expert Performance. Psychological Review, 100, 363-406* (with 2019 replication analysis) — [live](https://pmc.ncbi.nlm.nih.gov/articles/PMC6731745/) · [snapshot](https://web.archive.org/web/2026*/https://pmc.ncbi.nlm.nih.gov/articles/PMC6731745/) · accessed 2026-07-04.
- *van Merriënboer, J. J. G., & Kirschner, P. A. Ten Steps to Complex Learning* — 4C/ID model home — [live](https://www.4cid.org/) · [snapshot](https://web.archive.org/web/2026*/https://www.4cid.org/) · accessed 2026-07-04.
- *Blueprints for complex learning: The 4C/ID-model. Educational Technology Research and Development* — [live](https://link.springer.com/article/10.1007/BF02504993) · [snapshot](https://web.archive.org/web/2026*/https://link.springer.com/article/10.1007/BF02504993) · accessed 2026-07-04.
- *Bloom, B. S. (1968). Learning for Mastery. Evaluation Comment, 1, 1-12* — [live](https://dl.icdst.org/pdfs/files1/3b3c79918ad75a1b2978742716506b44.pdf) · [snapshot](https://web.archive.org/web/2026*/https://dl.icdst.org/pdfs/files1/3b3c79918ad75a1b2978742716506b44.pdf) · accessed 2026-07-04.

## 4. Operational Context

Flight and simulator-based operator training in every complex-systems domain (aviation type-rating
progressions, nuclear-plant operator qualification, military crew-served-weapon qualification tables)
uses exactly this structure: mandatory foundational qualification, a core progression of increasing
integrated complexity, and specialty tracks pursued after the core — not because tradition dictates it
but because deliberate practice's "just past current competence" requirement and 4C/ID's whole-task/
part-task distinction independently converge on this shape. The learning path's four-stage structure
is this simulator's instance of a training-design pattern that recurs wherever a complex, judgment-
heavy operational skill needs to be taught.

## 5. Implementation Guidance

- **Every new canonical-ladder rung must add exactly one new mechanic the previous rung didn't
  require** (the "New this rung" column `training/16` already carries) — this is deliberate practice's
  requirement operationalized; a rung that only rehashes prior mechanics is not earning its place in
  the whole-task progression and should be redirected to a mission-set or novel-concept track instead.
- **Keep mission-set trials framed as part-task, not as harder versions of the ladder** — per 4C/ID,
  their job is recurrent-procedure automatization for one payload specialty, so they should stay
  narrower and more repeatable than the ladder's whole-task exercises, not escalate in unrelated
  complexity.
- **Preserve Stage 0 as a genuine hard floor, not a skippable formality** — mastery learning's
  prerequisite-gating logic only holds if the gated prerequisite (interface competence) is actually
  verified; a facilitator letting an experienced-but-tool-unfamiliar operator skip Stage 0 is skipping
  a real prerequisite, not just a formality, and manual/facilitation guidance should say so plainly.
- **When authoring a new rung, state its deliberate-practice target explicitly** (what a trainee who
  wins this vignette can now do that they couldn't before) in the rung's own authoring notes — this
  gives `09-training-manual-review`'s pedagogy dimension something concrete to check the rung against.

## 6. Feature Mapping

FR-11310 (sequenced learning path) and FR-11320 (per-rung manual linkage) are this topic's direct
code/doc targets — `training/16-learning-path.md`'s four-stage structure, its whole-task/part-task
split between Stage 1 and Stage 2, and its "hard floor at Stage 0" facilitator note all trace to this
topic's Concepts section.

## 7. Related Topics

[R601](R601-instructional-systems-design.md) (Instructional Systems Design, the backward-design method
this topic applies at multi-exercise scale), [R604](R604-cognitive-load-and-scaffolding.md) (Cognitive
Load & Scaffolding, load management within a single exercise vs. across the path),
`docs/training/16-learning-path.md` (this topic's direct implementation).
