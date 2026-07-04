# R607 — Assessment of Learning in Wargames & Exercises

> **Document ID:** R607
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R603](R603-simulation-based-learning-and-debriefing.md)
> **Referenced By:** none yet (a leaf topic; downstream consumers are the assessment feature and
> training-artifact skills, not further R6xx topics)
> **Produces:** the formative/summative distinction and wargame-debrief-question framing that grounds
> FS-201's competency-assessment design and the AAR's own debrief practice
> **Feature Mapping:** FS-201 (Competency Assessment), `session/assessment.py`, FR-10110 (competency
> rubric-tier computation), DOM-002 (assessment domain framework)
> **Related Topics:** [R603](R603-simulation-based-learning-and-debriefing.md) (Simulation-Based
> Learning & Debriefing, the discussion structure this topic's assessment sits inside),
> [R208](R208-ooda-loops.md) (OODA Loops, already the basis for FS-201's time-to-decision metric),
> [R202](R202-decision-theory.md) (Decision Theory, single-agent decision criteria this topic's
> assessment must not conflate with mere speed)

> **Verification note (this authoring pass):** citations below were sourced via live web search and
> corroborated across ≥2 independent results per claim; direct WebFetch of source pages was blocked
> by this session's egress policy (proxy denial on external hosts, per `/root/.ccr/README.md`) and is
> deferred to this corpus's separate formal verification pass
> ([`../10-sources-and-methodology.md`](../10-sources-and-methodology.md) §5.3).

> **Last Reviewed:** 2026-07-04
> **Primary Sources Consulted:** 2

[↑ Tier R600 index](R600-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

`session/assessment.py` (built by `IP-2010`, verified `VR-2010`) already computes non-aggregating
competency rubric tiers and `custody_confidence_at_decision`-informed scoring — but VR-2010's own
findings (`BL-0019`, `BL-0020`) surfaced FS-201 acceptance criteria the shipped code doesn't fully meet
(a longitudinal per-trainee report; self-assessment-mode accessibility). This topic supplies the
formal assessment-theory grounding — Kirkpatrick's four levels and wargame-specific debrief-as-assessment
practice — that any future package closing those gaps, or any manual/vignette-side assessment framing,
should be built against.

## 2. Scope

Covers formative vs. summative assessment (Scriven's foundational distinction) and Kirkpatrick's
four-level training-evaluation model, applied specifically to wargame/exercise assessment where no
single "correct answer" exists and the White Cell adjudicates judgment rather than grading a fixed
rubric alone. Does **not** cover debrief *structure* generally ([R603](R603-simulation-based-learning-and-debriefing.md),
already authored), the OODA-loop metric FS-201 already implements ([R208](R208-ooda-loops.md)), or
single-agent decision-quality criteria ([R202](R202-decision-theory.md)).

## 3. Concepts

**Formative vs. summative: the same exercise data can serve two different, incompatible purposes.**
Michael Scriven's foundational distinction: **formative** evaluation happens while the activity is
still "malleable" and serves to improve an ongoing process; **summative** evaluation happens after
completion and serves to judge the finished result
([Scriven's 1967 distinction, corroborated via multiple independent educational-evaluation
summaries](https://en.wikipedia.org/wiki/Formative_assessment); Bloom's own 1968 mastery-learning work,
[R605](R605-learning-path-and-progression-design.md), explicitly took up Scriven's term the following
year to argue formative assessment should drive remediation, not grading). Applied to this simulator:
the AAR's debrief function is inherently **formative** (improve the next exercise), while
`session/assessment.py`'s rubric-tier computation risks being read as **summative** (a grade) if
presented without care — FS-201's own "non-aggregating" design choice (VR-2010 confirmed this) is
already a formative-leaning design decision; this topic supplies the citation for *why* that choice is
correct rather than merely a stylistic preference.

**Kirkpatrick's four levels: reaction, learning, behavior, results — increasingly hard to measure, and
increasingly valuable.** Donald Kirkpatrick's four-level training-evaluation model: **Level 1
(Reaction)** — did the trainee find the exercise engaging/relevant; **Level 2 (Learning)** — did they
acquire the intended knowledge/skill; **Level 3 (Behavior)** — did it change their actual on-the-job
behavior, typically only measurable weeks to months later; **Level 4 (Results)** — did it produce a
tangible organizational outcome
([Kirkpatrick's model, corroborated across multiple independent training-industry summaries](https://trainingindustry.com/wiki/measurement-and-analytics/the-kirkpatrick-model/)
and [Kirkpatrick Partners' own site](https://www.kirkpatrickpartners.com/the-kirkpatrick-model/)).
FS-201's rubric-tier computation and time-to-decision metric are **Level 2** instruments (learning
within the exercise) — the model's own structure explains why VR-2010's flagged gap (a longitudinal
per-trainee report, BL-0019) is asking for something closer to **Level 3** (behavior change across
exercises over time), a materially different and harder measurement than what Level 2 in-exercise
scoring can supply, which is useful framing for whoever eventually scopes that gap-closing work.

**Wargame-specific debrief-as-assessment: the "why," not the score, is the point.** Peter Perla's
foundational treatise on wargaming practice frames a wargame as "a conversation between its developers
and its players," where the single most important debrief question is *why* — why did the players
decide what they decided, why did the designers embed the assumptions they embedded — and provides
structured question lists to drive this rather than a scoring rubric
([Perla, P. P. *The Art of Wargaming: A Guide for Professionals and Hobbyists*, Naval Institute Press,
1990, rev. 2011](https://thetidesofhistory.com/2021/11/28/book-review-the-art-of-wargaming-by-peter-perla/);
corroborated by [PAXsims' coverage of Perla's design framework](https://paxsims.wordpress.com/2018/12/13/26106/)).
This is directly compatible with — and reinforces — FS-201's non-aggregating design and
[R603](R603-simulation-based-learning-and-debriefing.md)'s self-discovery framing: a wargame assessment
that reduces to a single score misses the actual pedagogical payoff, which is surfacing *why* a
decision was made, not whether it scored well.

### Sources

- *Formative assessment* (Scriven's 1967 distinction, formative/summative), corroborated across independent educational-evaluation sources — [live](https://en.wikipedia.org/wiki/Formative_assessment) · [snapshot](https://web.archive.org/web/2026*/https://en.wikipedia.org/wiki/Formative_assessment) · accessed 2026-07-04. *(Tertiary cross-check per `10-sources-and-methodology.md` §2 Tier D convention — used here only as a navigational pointer corroborating the well-established Scriven/Bloom history, not as a stand-alone citation for a contested claim.)*
- *The Kirkpatrick Model* — Training Industry — [live](https://trainingindustry.com/wiki/measurement-and-analytics/the-kirkpatrick-model/) · [snapshot](https://web.archive.org/web/2026*/https://trainingindustry.com/wiki/measurement-and-analytics/the-kirkpatrick-model/) · accessed 2026-07-04.
- *Kirkpatrick Partners — What is The Kirkpatrick Model?* (the model's originating organization) — [live](https://www.kirkpatrickpartners.com/the-kirkpatrick-model/) · [snapshot](https://web.archive.org/web/2026*/https://www.kirkpatrickpartners.com/the-kirkpatrick-model/) · accessed 2026-07-04.
- *Perla, P. P. The Art of Wargaming: A Guide for Professionals and Hobbyists* (Naval Institute Press, 1990/2011) — review summary — [live](https://thetidesofhistory.com/2021/11/28/book-review-the-art-of-wargaming-by-peter-perla/) · [snapshot](https://web.archive.org/web/2026*/https://thetidesofhistory.com/2021/11/28/book-review-the-art-of-wargaming-by-peter-perla/) · accessed 2026-07-04.
- *Peter Perla on wargame design* — PAXsims — [live](https://paxsims.wordpress.com/2018/12/13/26106/) · [snapshot](https://web.archive.org/web/2026*/https://paxsims.wordpress.com/2018/12/13/26106/) · accessed 2026-07-04.

## 4. Operational Context

Professional wargaming institutions (CNA, the Naval War College, RAND) treat assessment and debrief as
inseparable from design itself — Perla's own career (CNA senior analyst) is representative of a field
where the analyst's job *is* structuring the "why" conversation, not scoring outcomes. This is a
genuinely different assessment culture than most corporate/academic training (which Kirkpatrick's model
originates from), and the tension between the two is exactly what FS-201 sits in: a rubric-tier
computation (Kirkpatrick Level 2-style measurement) embedded inside a wargame whose actual pedagogical
tradition (Perla) resists reducing the exercise to a score.

## 5. Implementation Guidance

- **Frame `session/assessment.py`'s rubric tiers as formative inputs to the AAR discussion, never as a
  final grade surfaced without discussion** — manual/UI copy describing the assessment panel should
  make this explicit, closing the interpretive gap VR-2010's own findings implicitly flagged.
- **When scoping BL-0019's longitudinal-report gap, name it as a Kirkpatrick Level 3 measurement
  problem explicitly** — this reframes the feature-specification conversation from "we haven't built
  it yet" to "this needs a materially different measurement design (cross-session behavior tracking)
  than Level 2 in-exercise scoring," which should change how `06-feature-specification` scopes the work.
- **Any future debrief-facilitation guidance for White Cell should borrow Perla's "why" question
  pattern directly** — e.g., "why did you choose that access window," "why did you assess that RPO as
  hostile" — rather than inventing a new question taxonomy; this pairs directly with
  [R603](R603-simulation-based-learning-and-debriefing.md)'s self-discovery framing.
- **Self-assessment-mode accessibility (BL-0020) should be evaluated against Kirkpatrick Level 1-2**:
  a Blue/Red operator reviewing their own rubric tiers is a Level 1-2 (reaction/learning) use case
  distinct from White Cell's Level 2-3 facilitation use case — the feature gap may need two different
  presentations, not one panel exposed to a second audience unchanged.

## 6. Feature Mapping

FS-201 (Competency Assessment) and `session/assessment.py` are this topic's most direct code-level
targets — the formative/non-aggregating design VR-2010 already confirmed traces to Scriven's
distinction; the Level 2/Level 3 framing directly informs how BL-0019/BL-0020 should eventually be
scoped. DOM-002 (the assessment domain framework) is this topic's requirements-side counterpart.

## 7. Related Topics

[R603](R603-simulation-based-learning-and-debriefing.md) (Simulation-Based Learning & Debriefing, the
discussion structure this topic's assessment findings feed into), [R208](R208-ooda-loops.md) (OODA
Loops, already FS-201's time-to-decision grounding — this topic is complementary, not overlapping),
[R202](R202-decision-theory.md) (Decision Theory, single-agent decision-quality criteria this topic's
assessment must pair with rather than substitute for), `docs/pipeline/backlog.md` BL-0019/BL-0020 (the
open findings this topic reframes for future scoping).
