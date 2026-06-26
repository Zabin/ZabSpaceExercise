# MSTR-003 — Educational Philosophy

> **Document ID:** MSTR-003
> **Version:** 1.0
> **Status:** ✅ Stable
> **Dependencies:** MSTR-001
> **Referenced By:** DOM-001, DOM-002, DOM-003, DOM-007, DOM-009, all training-facing FS-2xx
> **Produces:** the pedagogical constraints DOM-001 (Training) and DOM-002 (Assessment) must satisfy
> **Feature Mapping:** FS-106 (White Cell Dashboard), FS-107 (After Action Review), FS-201 (Competency Assessment)
> **Related Topics:** [`docs/training/07-white-cell-facilitation.md`](../training/07-white-cell-facilitation.md),
> [`docs/vignettes/00-vignette-framework.md`](../vignettes/00-vignette-framework.md)

[↑ Docs index](../INDEX.md) · [Master index](MSTR-005-documentation-map.md)

## 1. Purpose

States the pedagogical theory SpaceSim is built on, so that every training-facing feature
(vignette design, assessment, the White Cell console, AAR) can be checked against a stable
standard instead of each being designed from individual intuition.

## 2. The core pedagogical claim

**Judgment under uncertainty cannot be taught by lecture; it has to be practiced and debriefed.**
SpaceSim's entire design — fog-of-war, plan-first command, reversible-by-default effects, full
replay — exists to manufacture *safe, repeatable* practice opportunities for decisions that are
otherwise either unavailable (classified) or irreversible (real operations) to practice on.

This claim has direct design consequences, enumerated below. Every consequence is a constraint a
Feature Specification must respect, not a suggestion.

## 3. Plan-execute as the unit of learning

The atomic unit of operator learning in SpaceSim is **not** "click a button and see an effect," it
is: *form a belief from imperfect custody → commit to a plan against a window you cannot
instantly verify → wait for the window → observe the outcome → update your belief.* This is the
OODA loop (research: R201 "OODA Loops") made structurally unavoidable rather than merely
recommended. Pedagogically:

- **Why this matters:** real space operations are plan-execute, not point-and-click; an interface
  that lets you skip the "commit before verify" step teaches a false mental model of the domain.
- **Design consequence:** any new command/order type must go through `OrderSystem` (validate →
  window → execute) per MSTR-002 §2 invariant 4. A feature that bypasses this for UX convenience is
  a pedagogical regression, not a quality-of-life win.

## 4. Fog-of-war as the central teaching device, not an obstacle

Red and Blue render only what their own `TrackCatalog`/`CellView` has earned through custody. This
is deliberately uncomfortable — operators routinely act on incomplete or wrong beliefs, and the
debrief is where the gap between belief and ground truth becomes the lesson. A White Cell viewing
god-view alongside both cells' belief views (the `/godview` truth + per-cell belief panels) is the
mechanism that makes this teachable: the facilitator can show *exactly* where and why a cell's
mental model diverged from reality.

**Design consequence:** any feature that would let a cell "peek" at ground truth outside the
custody/SDA model (a debug shortcut, a convenience query) undermines the central lesson and must be
gated to White-only / god-view-only surfaces, never exposed to Red/Blue play surfaces.

## 5. Reversibility as a deliberate teaching gradient

Most effects (EW/cyber/proximity) are reversible; kinetic effects are rare, consequential, and
require an explicit confirm step (see `app.js`'s "kinetic consequence-confirm"). This creates a
**graduated risk ladder** for trainees: early exercises can be played with low-stakes reversible
effects so operators learn the planning/custody/window mechanics without fear of an
irrecoverable mistake; advanced vignettes introduce kinetic options once the fundamentals are
internalized, at which point the *consequence* (debris, escalation, the moral/legal weight per
`docs/research/07-legal-norms-and-roe.md`) becomes the lesson.

**Design consequence:** vignette difficulty progression (DOM-001, DOM-009) should be expressed
partly in terms of *which effect categories are made available/likely*, not only in terms of fleet
size or Red aggressiveness.

## 6. Replay/AAR as where learning is consolidated

The exercise itself is where decisions are made; the **After Action Review** is where learning is
consolidated. SpaceSim's P7 capstone replay (scrub, branch-compare) exists specifically so a
facilitator can rewind to a decision point, show what the cell believed at that moment (not
hindsight-corrected), and optionally branch to show an alternative outcome. This is a deliberate
implementation of **reflective practice** (Kolb-style experience → reflection → conceptualization →
re-experimentation cycle), not just a VCR feature.

**Design consequence:** any new telemetry/state surface must be replayable from the eventlog
(MSTR-002 §5), because if it isn't, it cannot be used in an AAR — and an exercise feature that
cannot be debriefed has, pedagogically, only half shipped.

## 7. White Cell as instructional designer, not referee

The White Cell is not a neutral rules arbiter in the boardgame sense — it is the **instructor**,
authoring injects, adjusting pacing, and steering the exercise toward the learning objectives of
*this* session (DOM-003). The tooling (inject library, coaching notes embedded in vignettes,
mission-brief panels) exists to reduce the facilitation burden so a subject-matter expert who is
not a software engineer can run a pedagogically sound exercise without scripting it from scratch.

## 8. Competency, not just completion

An exercise "succeeding" (objectives flipped) is necessary but not sufficient evidence of learning.
DOM-002 (Assessment Framework) and the research in R200 (Decision Sciences, especially bounded
rationality and decision support) exist to give White Cell and program evaluators a vocabulary for
*how* a cell succeeded or failed — was custody built deliberately or by luck, was a kinetic option
taken with appropriate escalation awareness, did the cell's belief track ground truth or diverge —
not just *whether* it succeeded.

## 9. Implications for documentation itself

Because the educational philosophy treats "debrief on real, traceable decisions" as central, the
documentation tree (MSTR-005) must itself support traceability from a stated **training
objective** to the mechanic that exercises it. A Feature Specification that cannot name which
training objective it serves (FS template §"Educational Value") has skipped the step that justifies
its existence in a PME tool, as distinct from a generic game feature.

## 10. Related topics

- Decision sciences underpinning judgment-under-uncertainty: R201–R214 (Tier R200).
- Wargaming/red-teaming theory underpinning White Cell design: R301–R312 (Tier R300).
- Research methods for measuring whether the educational claims in this document actually hold in
  practice (pre/post assessment, control vignettes): R401–R413 (Tier R400), DOM-005 (Validation).
