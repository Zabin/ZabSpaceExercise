# R603 — Simulation-Based Learning & Debriefing

> **Document ID:** R603
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R601](R601-instructional-systems-design.md)
> **Referenced By:** [R607](R607-assessment-of-learning-in-wargames.md)
> **Produces:** the debrief-structure rationale for the AAR and coaching-notes features, and for
> `07-white-cell-facilitation.md`'s facilitation guidance
> **Feature Mapping:** `session/aar.py` (AAR replay/scrub/branch-compare), `Vignette.coaching` (coaching
> notes), MSTR-001 §1 item 3 ("after-action reflection")
> **Related Topics:** [R601](R601-instructional-systems-design.md) (Instructional Systems Design, the
> evaluate-phase this topic elaborates), [R607](R607-assessment-of-learning-in-wargames.md) (Assessment
> of Learning in Wargames, which builds on this topic's debrief structure), [R208](R208-ooda-loops.md)
> (OODA Loops — the AAR's per-decision-point structure), `docs/training/05-core-concepts.md` §"Red
> doctrine & After-Action Review"

> **Verification note (this authoring pass):** citations below were sourced via live web search and
> corroborated across ≥2 independent results per claim; direct WebFetch of source pages was blocked
> by this session's egress policy (proxy denial on external hosts, per `/root/.ccr/README.md`) and is
> deferred to this corpus's separate formal verification pass
> ([`../10-sources-and-methodology.md`](../10-sources-and-methodology.md) §5.3).

> **Last Reviewed:** 2026-07-04
> **Primary Sources Consulted:** 2

[↑ Tier R600 index](R600-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

MSTR-001 §1 names "after-action reflection" as one of three things the program exists to teach
simultaneously, and states the educational payoff "lives in the debrief, not the button-presses." This
topic gives that claim a formal grounding — the simulation-based-learning literature's finding that
debriefing, not the exercise itself, is where the learning actually consolidates — so
`08-training-manual-authoring`'s AAR-facing manual sections and `08-vignette-development`'s coaching
notes are built on a stated theory of *why* debrief structure matters, not just "AAR is good practice."

## 2. Scope

Covers why debriefing is the primary locus of learning in simulation-based training (not the
simulation itself), the structural elements of an effective debrief (military AAR doctrine, healthcare
simulation debriefing frameworks), and how they map onto this simulator's AAR/coaching mechanics. Does
**not** cover competency measurement or rubric design during/after a debrief
([R607](R607-assessment-of-learning-in-wargames.md)), wargame-design-specific debrief patterns beyond
the general simulation-learning literature, or the OODA-loop decision-point taxonomy the AAR could use
to structure a scrub session ([R208](R208-ooda-loops.md), already authored).

## 3. Concepts

**The debrief, not the exercise, is where learning consolidates.** Fanning & Gaba's foundational review
of debriefing in simulation-based learning states that experiential learning alone, without a
structured facilitated reflection afterward, produces inconsistent and often superficial learning —
debriefing is "the single most important element" for learning from a simulated experience because it
gives the learner space to reconcile what they intended, what they observed, and what actually happened
([Fanning, R. M., & Gaba, D. M. (2007). The Role of Debriefing in Simulation-Based Learning.
*Simulation in Healthcare*, 2(2), 115-125](https://pubmed.ncbi.nlm.nih.gov/19088616/); corroborated by
[Scientific Research Publishing's reference listing](https://www.scirp.org/reference/referencespapers?referenceid=2630837)
and a hosted copy at [aku.edu](https://www.aku.edu/cime/Documents/Reading%20material%20module%206.pdf)).
This directly supports MSTR-001 §1's own framing, verbatim.

**The military After-Action Review: a self-discovery structure, not a lecture.** U.S. Army Training
Circular TC 25-20 defines an AAR as "a professional discussion of an event, focused on performance
standards, that enables soldiers to discover for themselves what happened, why it happened, and how to
sustain strengths and improve on weaknesses" — critically, a *discussion the participants drive*, not a
critique delivered by the facilitator
([TC 25-20, *A Leader's Guide to After-Action Reviews*, Department of the Army, 1993](https://www.studocu.com/en-us/document/united-states-army-war-college/introduction-to-strategic-logic/leaders-guide-to-the-aar-tc25-20/104623865);
corroborated by a DTIC-hosted foundational-theory paper on the AAR process,
[dtic.mil](https://apps.dtic.mil/sti/pdfs/ADA368651.pdf)). TC 25-20 structures the AAR in four phases:
planning, preparing, conducting, and following up (using the results) — the "following up" phase is
often the one an informal debrief skips, and is exactly what this simulator's replayable, byte-exact
AAR (§4 below) makes cheap to actually do.

**Branch-compare is a debrief technique with no live-exercise analog.** Because this simulator's AAR
can rewind and continue differently (branch-compare, `session/aar.py`), it can do something neither
Fanning & Gaba's live-simulation debrief nor a live military AAR can: show the *counterfactual* outcome
of a different decision, not just describe it verbally. This is a genuine capability advantage over the
literature's baseline case, not merely an implementation of it — flagged here because it means the
manual/facilitation guidance for branch-compare has no directly-citable precedent to lean on beyond the
general principle that concretely showing consequences beats describing them.

### Sources

- *Fanning, R. M., & Gaba, D. M. (2007). The Role of Debriefing in Simulation-Based Learning. Simulation in Healthcare, 2(2), 115-125* — [live](https://pubmed.ncbi.nlm.nih.gov/19088616/) · [snapshot](https://web.archive.org/web/2026*/https://pubmed.ncbi.nlm.nih.gov/19088616/) · accessed 2026-07-04.
- *TC 25-20, A Leader's Guide to After-Action Reviews* (Department of the Army, 1993) — [live](https://www.studocu.com/en-us/document/united-states-army-war-college/introduction-to-strategic-logic/leaders-guide-to-the-aar-tc25-20/104623865) · [snapshot](https://web.archive.org/web/2026*/https://www.studocu.com/en-us/document/united-states-army-war-college/introduction-to-strategic-logic/leaders-guide-to-the-aar-tc25-20/104623865) · accessed 2026-07-04.
- *Foundations of the After Action Review Process* — DTIC — [live](https://apps.dtic.mil/sti/pdfs/ADA368651.pdf) · [snapshot](https://web.archive.org/web/2026*/https://apps.dtic.mil/sti/pdfs/ADA368651.pdf) · accessed 2026-07-04.

## 4. Operational Context

Military units treat the AAR as a standard, load-bearing part of every training exercise, not an
optional add-on — TC 25-20 was formalized specifically because inconsistent, lecture-style debriefs
were producing weaker training transfer than a structured, participant-driven discussion. Healthcare
simulation training (where Fanning & Gaba's review originates) converged on the same finding
independently, from a different professional domain, which is itself evidence the "debrief is where
learning happens" claim generalizes across simulation-based training contexts rather than being
specific to one field — relevant because this simulator sits in neither domain natively but borrows
from both.

## 5. Implementation Guidance

- **`07-white-cell-facilitation.md` should frame the AAR as a discussion White Cell *facilitates*, not
  a report White Cell *delivers*** — TC 25-20's "discover for themselves" framing argues against a
  facilitator-scripted debrief script; guidance should give White Cell prompting questions (per Perla's
  "why did you decide that" pattern, [R607](R607-assessment-of-learning-in-wargames.md)) rather than a
  fixed narrative to read.
- **Coaching notes (`Vignette.coaching`) should be authored as discussion-seeding prompts, not verdicts**
  — a coaching note that states "you should have jammed here" pre-empts the self-discovery the AAR
  structure depends on; one framed as "what did you know about the geometry at this point?" preserves
  it. Vignette-authoring guidance in `08-vignette-development` should apply this distinction.
- **Manual sections describing the AAR (`12-white-cell-manual.md` WCM-9) should explicitly name the
  branch-compare capability as a debrief tool**, not just a technical feature — its pedagogical value
  (showing rather than describing a counterfactual) is the actual reason it matters to a facilitator,
  and that framing is currently implicit rather than stated.
- **Follow TC 25-20's four-phase structure when writing facilitation guidance**: planning (what
  decision points to focus the debrief on, chosen before the exercise ends), preparing (reviewing the
  event log/scrub points), conducting (the discussion itself), following up (what changes next time) —
  a manual section that only covers "conducting" is missing three of the four phases TC 25-20 treats as
  necessary.

## 6. Feature Mapping

`session/aar.py` (replay/scrub/branch-compare — the mechanism this topic's debrief structure runs
through); `Vignette.coaching` (the authored prompts this topic's self-discovery principle constrains);
`docs/training/07-white-cell-facilitation.md` and `12-white-cell-manual.md` §WCM-9 (the manual surfaces
this topic directly grounds).

## 7. Related Topics

[R601](R601-instructional-systems-design.md) (Instructional Systems Design, ADDIE's Evaluate phase this
topic elaborates), [R607](R607-assessment-of-learning-in-wargames.md) (Assessment of Learning in
Wargames, building competency measurement on top of this topic's debrief structure),
[R208](R208-ooda-loops.md) (OODA Loops, a candidate taxonomy for structuring a scrub session by decision
stage), MSTR-001 §1 (program vision's after-action-reflection goal).
