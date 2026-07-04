# R601 — Instructional Systems Design

> **Document ID:** R601
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** none (foundational — everything else in this tier builds on it)
> **Referenced By:** [R602](R602-adult-learning-theory.md), [R603](R603-simulation-based-learning-and-debriefing.md), [R605](R605-learning-path-and-progression-design.md)
> **Produces:** the systematic-design vocabulary (analyze → design → develop → implement → evaluate;
> backward design from objectives) that `08-training-manual-authoring` and `08-vignette-development`
> use when structuring a module or a learning-path rung
> **Feature Mapping:** FR-11110 (role-scoped manual coverage), FR-11310/FR-11320 (sequenced learning
> path + per-rung linkage)
> **Related Topics:** [R602](R602-adult-learning-theory.md) (Adult Learning Theory — *who* the design
> is for), [R605](R605-learning-path-and-progression-design.md) (Learning-Path & Progression Design —
> applies backward design to vignette sequencing), MSTR-003 (educational philosophy this topic grounds)

> **Verification note (this authoring pass):** citations below were sourced via live web search and
> corroborated across ≥2 independent results per claim; direct WebFetch of source pages was blocked
> by this session's egress policy (proxy denial on external hosts, per `/root/.ccr/README.md`) and is
> deferred to this corpus's separate formal verification pass
> ([`../10-sources-and-methodology.md`](../10-sources-and-methodology.md) §5.3).

> **Last Reviewed:** 2026-07-04
> **Primary Sources Consulted:** 4

[↑ Tier R600 index](R600-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

MSTR-001 §2 elevates the training corpus to a co-equal product with the code (2026-07-04), and
`08-training-manual-authoring`/`08-vignette-development` need a systematic method for *how* to
design a manual module or a vignette rung, not just a citation that "instructional design is a
field." This topic gives the implementer the two working frameworks — a systematic development
process (ADDIE) and an outcomes-first design method (backward design) — that ground the corpus's
module-authoring and learning-path-sequencing decisions in something more rigorous than habit.

## 2. Scope

Covers instructional-systems-design (ISD) as a systematic process: the ADDIE model's five phases
and Wiggins & McTighe's backward-design method (identify results → determine assessment evidence →
plan learning experiences). Does **not** cover the adult-learner-specific assumptions ISD should be
applied *with* ([R602](R602-adult-learning-theory.md)), cognitive-load-driven sequencing decisions
within a design ([R604](R604-cognitive-load-and-scaffolding.md)), or how this method concretely
produces the vignette learning path's rung order ([R605](R605-learning-path-and-progression-design.md),
which applies this topic rather than re-deriving it).

## 3. Concepts

**ADDIE: Analyze, Design, Develop, Implement, Evaluate.** A systematic instructional-design process
originally developed for U.S. Army interservice training in the 1970s at Florida State University's
Center for Educational Technology, later adapted across all U.S. armed-forces branches as the
Interservice Procedures for Instructional Systems Development (IPISD)
([Florida State University Learning Systems Institute history](https://lsi.fsu.edu/about-lsi/our-experience);
corroborated by [nwlink.com's History of the ADDIE Model](http://www.nwlink.com/~donclark/history_isd/addie.html)).
The five phases: *Analyze* the learner and the performance gap; *Design* objectives and assessment
strategy; *Develop* the actual materials; *Implement* with the learners; *Evaluate* and iterate. The
model, though originally drawn as a rigid waterfall, is now practiced cyclically/iteratively by most
practitioners.

**Backward design: start from the destination, not the first lesson.** Wiggins & McTighe's
*Understanding by Design* three-stage method: (1) **identify desired results** — what should the
learner understand and be able to do; (2) **determine acceptable evidence** — how will you know they
got there, decided *before* building content; (3) **plan learning experiences** — only now design the
actual instructional sequence
([Wiggins & McTighe, *Understanding by Design*, 2nd ed., ASCD, 2005](https://files.ascd.org/staticfiles/ascd/pdf/siteASCD/publications/UbD_WhitePaper0312.pdf);
corroborated by [UCF Faculty Center for Teaching and Learning](https://fctl.ucf.edu/teaching-resources/course-design/backward-design/)).
The method's core claim is that content-first design ("what should I cover") systematically produces
worse instruction than outcome-first design ("what should they be able to do, and how would I know") —
because content-first design has no forcing function to stop covering things the assessment doesn't
actually need.

**Merrill's First Principles: five conditions instruction should satisfy regardless of method.**
David Merrill's synthesis across instructional-design models: learning is promoted when learners are
(1) engaged in solving **real-world, task-centered problems**, not abstract topics in isolation;
(2) existing knowledge is **activated** as a foundation; (3) new knowledge is **demonstrated**, not
just told; (4) new knowledge is **applied** by the learner, not just observed; (5) new knowledge is
**integrated** into the learner's own practice
([Merrill, "First Principles of Instruction," *Educational Technology Research and Development*,
2002](http://www.nwlink.com/~donclark/hrd/learning/id/Merrill.html); corroborated by
[University of Iowa Tippie College's instructional-design model page](https://students.tippie.uiowa.edu/tippie-resources/technology/instructional-design/models/merrill)).
Merrill frames these as *principles*, not a *procedure* — they can be satisfied by ADDIE, by backward
design, or by neither, which is why this topic treats them as a checklist against any concrete module
rather than a competing process.

### Sources

- *ADDIE model history* — Florida State University Learning Systems Institute — [live](https://lsi.fsu.edu/about-lsi/our-experience) · [snapshot](https://web.archive.org/web/2026*/https://lsi.fsu.edu/about-lsi/our-experience) · accessed 2026-07-04.
- *History of the ADDIE Model* — nwlink.com (Don Clark) — [live](http://www.nwlink.com/~donclark/history_isd/addie.html) · [snapshot](https://web.archive.org/web/2026*/http://www.nwlink.com/~donclark/history_isd/addie.html) · accessed 2026-07-04.
- *Wiggins, G., & McTighe, J. (2005). Understanding by Design (2nd ed.). ASCD* — white-paper summary — [live](https://files.ascd.org/staticfiles/ascd/pdf/siteASCD/publications/UbD_WhitePaper0312.pdf) · [snapshot](https://web.archive.org/web/2026*/https://files.ascd.org/staticfiles/ascd/pdf/siteASCD/publications/UbD_WhitePaper0312.pdf) · accessed 2026-07-04.
- *Backward Design* — UCF Faculty Center for Teaching and Learning — [live](https://fctl.ucf.edu/teaching-resources/course-design/backward-design/) · [snapshot](https://web.archive.org/web/2026*/https://fctl.ucf.edu/teaching-resources/course-design/backward-design/) · accessed 2026-07-04.
- *Merrill, M. D. (2002). First Principles of Instruction. Educational Technology Research and Development, 50(3)* — summary — [live](http://www.nwlink.com/~donclark/hrd/learning/id/Merrill.html) · [snapshot](https://web.archive.org/web/2026*/http://www.nwlink.com/~donclark/hrd/learning/id/Merrill.html) · accessed 2026-07-04.

## 4. Operational Context

Military and PME training organizations are the *origin* of ADDIE, not a late adopter of a civilian
model — this simulator's own domain (professional military education) is the field ADDIE was built
for. A White Cell facilitator's own workflow (build/tune a vignette → run it → debrief) is structurally
an ADDIE cycle at exercise scale: Analyze (what should this cohort learn), Design/Develop (pick or
author a vignette and dials), Implement (run it), Evaluate (the AAR). Backward design shows up
whenever a curriculum designer resists the urge to write content before deciding what "success" looks
like — exactly the discipline `06-feature-specification`/`07-implementation-planning`'s own "Definition
of Done before Implementation Tasks" convention already applies to code, now applied to training
artifacts.

## 5. Implementation Guidance

- **Write a manual module's assessment criterion before its prose**, mirroring backward design's
  stage order: before drafting a `docs/training/` section, state what the reader should be able to
  *do* differently (plan a command? diagnose a jam signature?) and how a reviewer would check it —
  then write to that target. `09-training-manual-review`'s accuracy dimension is exactly this
  after-the-fact check; doing it design-first instead of review-first produces better modules.
- **Treat FR-11110's role-scoped-coverage requirement as an ADDIE "Analyze" deliverable, not an
  afterthought** — before writing a cell's manual content, explicitly analyze which operator-visible
  capabilities that role can exercise (the `training/15` §15.1 forward index *is* this analysis,
  kept current rather than done once).
- **When authoring a new learning-path rung** ([R605](R605-learning-path-and-progression-design.md)),
  state the rung's "desired result" (what mechanic it teaches) before picking which vignette
  demonstrates it — the learning path already does this implicitly (each rung names "New this
  rung"); make it explicit in any new rung's authoring notes.
- **Merrill's five principles are a checklist for any module**, not a rewrite mandate: a module that
  only *tells* (no demonstration, no application) is missing principles 3-4 even if its prose is
  otherwise excellent — `09-training-manual-review`'s pedagogy dimension should check for this
  specifically once it has this topic to cite.

## 6. Feature Mapping

FR-11110 (role-scoped manual coverage — the "Analyze" target); FR-11310/FR-11320 (sequenced learning
path — backward-designed from mission-set competence back to the onboarding rung); the
`08-training-manual-authoring` and `08-vignette-development` skills, which are this topic's direct
consumers when structuring new content.

## 7. Related Topics

[R602](R602-adult-learning-theory.md) (Adult Learning Theory, the audience assumptions ISD should be
applied with), [R604](R604-cognitive-load-and-scaffolding.md) (Cognitive Load & Scaffolding, sequencing
decisions within a design), [R605](R605-learning-path-and-progression-design.md) (Learning-Path &
Progression Design, applies backward design to the vignette library), MSTR-003 (educational
philosophy), MSTR-001 §2 (the training-corpus elevation this tier grounds).
