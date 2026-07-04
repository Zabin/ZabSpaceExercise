# R604 — Cognitive Load & Scaffolding in Complex-System Training

> **Document ID:** R604
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R602](R602-adult-learning-theory.md)
> **Referenced By:** [R605](R605-learning-path-and-progression-design.md), [R608](R608-software-onboarding-and-tutorial-design.md)
> **Produces:** the theoretical grounding for `ops_fidelity`'s tactical/realistic/full_ttc dial as a
> deliberate cognitive-load scaffold, not just a display option
> **Feature Mapping:** `ops_fidelity` (`content/vignette.py`, `engine/bus.py`), FR-11110
> **Related Topics:** [R602](R602-adult-learning-theory.md) (Adult Learning Theory, the audience this
> load-management applies to), [R605](R605-learning-path-and-progression-design.md) (Learning-Path &
> Progression Design, which sequences *across* vignettes the way this topic scaffolds *within* one),
> [R608](R608-software-onboarding-and-tutorial-design.md) (Software Onboarding, applying scaffolding to
> the in-app tutorial)

> **Verification note (this authoring pass):** citations below were sourced via live web search and
> corroborated across ≥2 independent results per claim; direct WebFetch of source pages was blocked
> by this session's egress policy (proxy denial on external hosts, per `/root/.ccr/README.md`) and is
> deferred to this corpus's separate formal verification pass
> ([`../10-sources-and-methodology.md`](../10-sources-and-methodology.md) §5.3).

> **Last Reviewed:** 2026-07-04
> **Primary Sources Consulted:** 3

[↑ Tier R600 index](R600-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

The simulator's operator console is a genuinely complex multi-panel interface — 14 panels per
`10-ui-reference.md` — taught to an audience that includes first-time users of the tool
(training-basics vignette). `ops_fidelity`'s tactical/realistic/full_ttc dial already exists in code as
a way to simplify or elaborate bus telemetry, but the training corpus had no stated theory for *why*
that dial is pedagogically correct rather than merely a convenient feature flag. This topic supplies
that theory: cognitive load theory and the scaffolding concept, so `08-training-manual-authoring` and
`08-vignette-development` can reason about complexity-introduction deliberately rather than by feel.

## 2. Scope

Covers Sweller's cognitive load theory (intrinsic/extraneous/germane load) and Wood, Bruner & Ross's
scaffolding concept, and their joint implication that a learner's total capacity is a real, limited
resource that a training designer must actively budget, not something more explanation always
improves. Does **not** cover the adult-learner assumptions this load-management is layered on top of
([R602](R602-adult-learning-theory.md)), sequencing *across* separate exercises
([R605](R605-learning-path-and-progression-design.md)), or in-app tutorial-specific scaffolding
patterns ([R608](R608-software-onboarding-and-tutorial-design.md)).

## 3. Concepts

**Three additive kinds of cognitive load, only one of which helps learning.** John Sweller's cognitive
load theory holds that working memory has limited capacity, and instructional material imposes three
kinds of load that sum together: **intrinsic load** (the inherent complexity of the material itself —
e.g., the real difficulty of understanding access windows), **extraneous load** (load imposed by *how*
the material is presented, not what it is — confusing layout, irrelevant detail, poor sequencing — and
the only kind good design can eliminate), and **germane load** (effortful processing that actually
builds the learner's schema — the "good" load worth spending capacity on)
([Sweller, J. (1988). Cognitive load during problem solving: Effects on learning. *Cognitive Science*,
12(2), 257-285](https://www.sciencedirect.com/topics/psychology/cognitive-load-theory); extended in
[Sweller, J. (1994). Cognitive load theory, learning difficulty, and instructional design. *Learning
and Instruction*, 4(4)](https://education.nsw.gov.au/content/dam/main-education/about-us/educational-data/cese/2017-cognitive-load-theory.pdf)).
The design implication is specific: reduce extraneous load aggressively (it never helps), don't try to
eliminate intrinsic load (the material really is that complex), and design activities that spend the
learner's remaining capacity on germane load.

**Scaffolding: temporary support withdrawn as competence grows, not permanent simplification.** Wood,
Bruner & Ross's foundational study defines scaffolding as a process enabling "a child or novice to
solve a task or achieve a goal that would be beyond his unassisted efforts," through six functions:
recruiting interest, reducing the task's degrees of freedom, maintaining direction toward the goal,
marking critical features, controlling frustration, and demonstrating the task
([Wood, D., Bruner, J. S., & Ross, G. (1976). The Role of Tutoring in Problem Solving. *Journal of
Child Psychology and Psychiatry*, 17, 89-100](https://acamh.onlinelibrary.wiley.com/doi/10.1111/j.1469-7610.1976.tb00381.x)).
The defining property distinguishing scaffolding from mere simplification is that it is **temporary
and withdrawn as the learner's own competence grows** — a permanently simplified interface is not
scaffolding, it is a different (permanently reduced-capability) tool.

**`ops_fidelity` as a literal, code-level instance of both concepts.** `tactical` mode (one health bar
per satellite) reduces intrinsic *and* extraneous load simultaneously — appropriate when a trainee's
germane-load budget should go entirely toward space-control decision-making, not subsystem diagnosis.
`full_ttc` mode (detailed subsystem telemetry) restores the full intrinsic load because TT&C-operator
training's entire *point* is that specific germane load. Read this way, `ops_fidelity` is not merely a
display preference — it is a scaffold, and per Wood/Bruner/Ross's definition should be **withdrawn**
(a trainee moved from `tactical` toward `realistic`/`full_ttc`) as competence grows, a progression this
topic recommends `08-vignette-development` consider making explicit across the learning path's rungs
rather than leaving it a session-start parameter chosen once.

### Sources

- *Sweller, J. (1988). Cognitive load during problem solving: Effects on learning. Cognitive Science, 12(2), 257-285* — summary — [live](https://www.sciencedirect.com/topics/psychology/cognitive-load-theory) · [snapshot](https://web.archive.org/web/2026*/https://www.sciencedirect.com/topics/psychology/cognitive-load-theory) · accessed 2026-07-04.
- *Cognitive load theory: Research that teachers really need to understand* (NSW Dept. of Education, summarizing Sweller 1994) — [live](https://education.nsw.gov.au/content/dam/main-education/about-us/educational-data/cese/2017-cognitive-load-theory.pdf) · [snapshot](https://web.archive.org/web/2026*/https://education.nsw.gov.au/content/dam/main-education/about-us/educational-data/cese/2017-cognitive-load-theory.pdf) · accessed 2026-07-04.
- *Wood, D., Bruner, J. S., & Ross, G. (1976). The Role of Tutoring in Problem Solving. Journal of Child Psychology and Psychiatry, 17, 89-100* — [live](https://acamh.onlinelibrary.wiley.com/doi/10.1111/j.1469-7610.1976.tb00381.x) · [snapshot](https://web.archive.org/web/2026*/https://acamh.onlinelibrary.wiley.com/doi/10.1111/j.1469-7610.1976.tb00381.x) · accessed 2026-07-04.

## 4. Operational Context

Complex-system operator training (aviation, nuclear-plant operations, and this simulator's own space-C2
domain) routinely uses fidelity/complexity dials for exactly this reason: a novice pilot trains on
simplified instrumentation before full-glass-cockpit complexity, not because the simple version is
"the real thing simplified for marketing" but because intrinsic load must be introduced in a sequence
the learner's germane-load budget can actually absorb. The training-basics vignette's own design (a
minimum-viable 1-satellite-1-ground-station fleet) is an unstated instance of exactly this principle —
this topic makes the principle explicit so future rungs are designed against it deliberately.

## 5. Implementation Guidance

- **Recommend a fidelity progression across the learning path**, not just per-session choice: Stage 0
  (training-basics) and early Stage 1 rungs at `tactical` or `realistic`, later rungs at `realistic`,
  and only mission-set/specialty tracks needing TT&C depth at `full_ttc` — this operationalizes the
  scaffold-withdrawal principle into `training/16-learning-path.md`'s own rung table.
  ([R605](R605-learning-path-and-progression-design.md) owns the actual rung sequencing; this topic
  supplies the reason a fidelity recommendation belongs there.)
- **A manual module introducing a genuinely complex mechanic (SDA custody, five-D's effects) should
  front-load orientation (reduce extraneous load) before depth (preserve intrinsic load)** — state the
  mental model in one paragraph before the parameter tables, matching the existing convention in
  `13-blue-cell-manual.md`/`14-red-cell-manual.md`'s BLU-4/RED-4 sections.
- **Don't confuse "shorter module" with "less load."** NFR-3500's module-size convention (~50-300
  lines) is about extraneous load (navigability, focus) — cutting *intrinsic* content to hit a length
  target instead misapplies this topic; the correct move is fewer topics per module, not less depth per
  topic that genuinely needs it.
- **A future in-app scaffold (e.g., a "reduce panel count" mode) should be framed and named as
  temporary/withdrawable**, per Wood/Bruner/Ross's definition — a permanent "simple mode" is a
  different product decision, not scaffolding, and should not borrow this topic's citation to justify
  itself.

## 6. Feature Mapping

`ops_fidelity` (`content/vignette.py`'s parameter, `engine/bus.py`'s SOH collapse logic) is this
topic's most direct code-level instance; FR-11110 (role-scoped coverage) benefits from this topic's
distinction between reducing extraneous load (always good) and reducing intrinsic content (a scoping
decision, not a load-management one).

## 7. Related Topics

[R602](R602-adult-learning-theory.md) (Adult Learning Theory, the professional-adult audience this
load-management is calibrated for), [R605](R605-learning-path-and-progression-design.md)
(Learning-Path & Progression Design, sequencing load *across* the vignette library the way this topic
scaffolds load *within* one exercise), [R608](R608-software-onboarding-and-tutorial-design.md)
(Software Onboarding & Tutorial Design, progressive disclosure as this topic's UI-pattern analog).
