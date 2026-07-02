# R504 — Future Space Warfare Concepts

> **Document ID:** R504
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** —
> **Referenced By:** [R505](R505-multi-domain-operations.md)
> **Produces:** forward-looking context for whether/how a future counterspace capability beyond the existing five-D's taxonomy might be added
> **Feature Mapping:** any future vignette or capability addition extending beyond [`research/03-counterspace-taxonomy.md`](../03-counterspace-taxonomy.md)'s current five-D's scope
> **Related Topics:** [`research/03-counterspace-taxonomy.md`](../03-counterspace-taxonomy.md) (the five-D's taxonomy this topic looks
> beyond), [R310](R310-effects-based-operations.md) (Effects-Based Operations), [R505](R505-multi-domain-operations.md) (Multi-Domain Operations),
> [R132](R132-proliferated-constellation-c2-and-mesh-operations.md), [R133](R133-space-logistics-launch-reconstitution-and-servicing-economics.md),
> [R136](R136-cislunar-and-xgeo-operations.md) (the three R100-tier topics this document's original scope has since been superseded by)
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2 (Tier B annual counterspace-capability assessments — see §3 Sources)

[↑ Tier R500 index](R500-index.md) · [Encyclopedia index](INDEX.md)

**DOM-008 §6 tag:** neither in-world AI nor coding-agent practice directly — this topic is forward-
looking doctrinal context for future vignette/capability content, included in [R500](R500-index.md) for its
"future operations" relevance rather than its AI content.

## 1. Purpose

The simulator's five-D's taxonomy (deceive/disrupt/deny/degrade/destroy, `research/03-counterspace-
taxonomy.md`) captures the current real-world counterspace landscape reasonably completely. This
topic gives the implementer forward-looking context on emerging counterspace concepts not yet well
captured by that taxonomy, so a future vignette author or capability designer has doctrinal grounding
before deciding whether/how to extend the existing five categories rather than forcing a genuinely
novel concept into an ill-fitting existing bucket.

## 2. Scope

**Note on overlap since this topic's original drafting:** three of this topic's original four
concepts — proliferated-constellation warfare, on-orbit servicing's dual-use ambiguity, and
cislunar/deep-space extension — are now each covered by a dedicated R100-tier topic authored later
than this one ([R132](R132-proliferated-constellation-c2-and-mesh-operations.md),
[R133](R133-space-logistics-launch-reconstitution-and-servicing-economics.md),
[R136](R136-cislunar-and-xgeo-operations.md) respectively), each with its own citations and
Implementation Guidance specific to the engine seam it would extend. This topic **defers to those
three topics** for anything beyond a one-line pointer and does **not** re-derive their content (per
MSTR-007 §5's duplication rule) — see §3 below for the pointer-only treatment. What remains this
topic's own unique content is the **directed-energy dose-dependent reversibility question**, which
no other topic currently covers, and the **synthesizing "why five-D's may eventually need a sixth
category" framing** across all four concepts. Does **not** cover: the current kinetic-engagement
model ([R117](R117-directed-energy-and-kinetic-effects.md), which despite its title covers only
kinetic engagement, not directed-energy weapons — this topic's DE discussion is the only place DE
weapons are currently addressed in the corpus), Effects-Based Operations doctrine generally
([R310](R310-effects-based-operations.md)), or the cross-domain integration question
([R505](R505-multi-domain-operations.md)'s job).

## 3. Concepts

**Directed-energy and non-kinetic physical effects beyond current jam/cyber/RPO modeling.**
High-power microwave (HPM) and laser "dazzling"/damaging systems against space assets are tracked as
an active, growing capability category by both major annual open-source counterspace assessments —
the Secure World Foundation's *Global Counterspace Capabilities* report and CSIS's *Space Threat
Assessment* both maintain dedicated directed-energy sections tracking named national programs
([SWF Global Counterspace Capabilities 2025](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report);
[CSIS Space Threat Assessment 2025](https://www.csis.org/analysis/space-threat-assessment-2025)).
Unlike this simulator's current jam/cyber effects (fully reversible, `reversible=True`) or kinetic
engagement (fully irreversible, `reversible=False`), a directed-energy effect's physical consequence
is dose-dependent: a brief, low-power illumination can be a fully reversible sensor dazzle, while
sustained or high-power illumination of the same system can cause permanent detector damage — the
same weapon class can occupy either end of the reversible/irreversible axis depending on exposure,
which the engine's current binary `reversible` flag does not represent for any existing effect
category.

**Proliferated/disaggregated constellation warfare** is now covered in full by
[R132](R132-proliferated-constellation-c2-and-mesh-operations.md) (mesh C2, per-node vs.
constellation-level COG, the ground/ISL/C2-architecture COG shift) — this topic no longer duplicates
that content; see R132 directly for implementation guidance.

**On-orbit servicing and its dual-use ambiguity** is now covered in full by
[R133](R133-space-logistics-launch-reconstitution-and-servicing-economics.md) (launch
reconstitution, servicing economics, and the RPO-ambiguity angle) — this topic no longer duplicates
that content; see R133 and the existing "ambiguous RPO" inject template (`inject_library.yaml`)
directly.

**Cislunar and deep-space domain extension** is now covered in full by
[R136](R136-cislunar-and-xgeo-operations.md) (the `Propagator`/`AccessProvider` seam questions at
lunar-distance timescales and geometry) — this topic no longer duplicates that content; see R136
directly.

**Why these four concepts are grouped here as a single "beyond five-D's" question.** Despite now
being individually covered by dedicated topics, the four share a common structural implication for
this simulator worth stating once, synthetically: each concept either breaks a binary the current
engine assumes (DE's dose-dependent reversibility), shifts where the meaningful "target" of an effect
sits (proliferated constellations shifting COG off any single satellite, R132), blurs a
category the engine currently treats as clean (servicing vs. hostile RPO, R133), or extends a regime
boundary the engine's seams were designed to eventually cross but have not yet been asked to
(cislunar, R136). A future vignette or capability author encountering any of these four should expect
"which existing five-D's category does this belong to" to sometimes be the wrong question.

### Sources

- *SWF Global Counterspace Capabilities* (Secure World Foundation, 2025 edition), directed-energy
  chapter — [live](https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · [snapshot](https://web.archive.org/web/2026*/https://swfound.org/publications-and-reports/2025-global-counterspace-capabilities-report)
  · accessed 2026-07-02.
- *CSIS Space Threat Assessment 2025* (Aerospace Security Project), directed-energy chapter —
  [live](https://www.csis.org/analysis/space-threat-assessment-2025)
  · [snapshot](https://web.archive.org/web/2026*/https://www.csis.org/analysis/space-threat-assessment-2025)
  · accessed 2026-07-02.

## 4. Operational Context

Real-world space-strategy and counterspace-capability discourse (in defense-policy and space-security
literature, per the SWF/CSIS annual assessments cited above) actively discusses all four of these
concepts as emerging or near-future developments not yet fully reflected in most existing counterspace
taxonomies, including this simulator's five-D's framework — this topic exists so a future
capability-extension decision in this project starts from an accurate picture of where the real-world
frontier currently sits, rather than from this simulator's existing taxonomy alone.

### Sources

Uses the same sources cited inline in §3 (SWF 2025, CSIS 2025); no additional sources introduced in
this section.

## 5. Implementation Guidance

- **Before forcing a genuinely novel future capability concept into one of the existing five-D's
  categories, check whether it actually fits** — per the directed-energy example above, a capability
  that straddles reversible/irreversible by design (dose-dependent DE) may need a new modeling
  approach (e.g. a graduated dose-dependent effect with a permanent-damage probability that scales
  with exposure duration/power, rather than a forced binary classification) — this is the one concept
  in this topic with no dedicated R1xx topic yet; a future DE-effects feature should start here, not
  assume [R117](R117-directed-energy-and-kinetic-effects.md) already covers it (it does not).
- **A future proliferated-constellation, on-orbit-servicing, or cislunar vignette should start from
  [R132](R132-proliferated-constellation-c2-and-mesh-operations.md), [R133](R133-space-logistics-launch-reconstitution-and-servicing-economics.md),
  or [R136](R136-cislunar-and-xgeo-operations.md) respectively**, not from this topic — those three
  topics now carry the concrete Implementation Guidance for each.

## 6. Feature Mapping

Any future vignette or capability addition extending beyond the current five-D's scope is the direct
consumer. The directed-energy dose-dependence question has no implementation yet and no other R1xx
topic covering it; the other three concepts route to [R132](R132-proliferated-constellation-c2-and-mesh-operations.md), [R133](R133-space-logistics-launch-reconstitution-and-servicing-economics.md),
and [R136](R136-cislunar-and-xgeo-operations.md)'s own Feature Mapping sections.

## 7. Related Topics

[`research/03-counterspace-taxonomy.md`](../03-counterspace-taxonomy.md), [R117](R117-directed-energy-and-kinetic-effects.md) (Directed Energy and Kinetic
Effects — kinetic-only despite its title; does not cover DE), [R310](R310-effects-based-operations.md) (Effects-Based Operations),
[R505](R505-multi-domain-operations.md) (Multi-Domain Operations), [R132](R132-proliferated-constellation-c2-and-mesh-operations.md), [R133](R133-space-logistics-launch-reconstitution-and-servicing-economics.md),
[R136](R136-cislunar-and-xgeo-operations.md).
