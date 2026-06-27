# R504 — Future Space Warfare Concepts

> **Document ID:** R504
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** —
> **Referenced By:** [R505](R505-multi-domain-operations.md)
> **Produces:** forward-looking context for whether/how a future counterspace capability beyond the existing five-D's taxonomy might be added
> **Feature Mapping:** any future vignette or capability addition extending beyond [`research/03-counterspace-taxonomy.md`](../03-counterspace-taxonomy.md)'s current five-D's scope
> **Related Topics:** [`research/03-counterspace-taxonomy.md`](../03-counterspace-taxonomy.md) (the five-D's taxonomy this topic looks
> beyond), [R310](R310-effects-based-operations.md) (Effects-Based Operations), [R505](R505-multi-domain-operations.md) (Multi-Domain Operations)

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

## 2. Concepts

**Directed-energy and non-kinetic physical effects beyond current jam/cyber/RPO modeling.**
High-power microwave and laser effects against space assets are an actively discussed real-world
capability category that sits awkwardly across the existing taxonomy — potentially non-kinetic
(reversible, like jam) but with a physical-damage mode (like kinetic) depending on dose, meaning a
naive "is this kinetic or not" binary (the engine's `reversible` flag) may not cleanly apply without
deliberate design work.

**Proliferated/disaggregated constellation warfare.** Real-world shift toward large proliferated
LEO constellations (versus a small number of high-value GEO assets) changes the COG calculus ([R309](R309-center-of-gravity-analysis.md))
substantially — a single-satellite loss matters far less when a constellation has hundreds of
near-identical nodes, which shifts the meaningful COG toward ground infrastructure, inter-satellite
links, or the constellation's command architecture rather than any single space vehicle.

**On-orbit servicing and its dual-use ambiguity.** Real-world on-orbit servicing/refueling
capabilities (legitimately for satellite life-extension) carry an inherent rendezvous-proximity-
operations capability indistinguishable, at the sensor level, from a hostile RPO approach — this is
already partially captured by the existing "ambiguous RPO" inject template (`inject_library.yaml`),
but a dedicated on-orbit-servicing vignette concept would extend this ambiguity into a sustained
operational theme rather than a single inject event.

**Cislunar and deep-space domain extension.** Emerging real-world strategic interest in cislunar space
(beyond GEO) introduces longer access-window timescales and different orbital-mechanics regimes than
this simulator's current LEO/MEO/GEO scope — a future cislunar vignette concept would need to confirm
the existing `Propagator`/`AccessProvider` seam (CLAUDE.md) actually generalizes to those longer
timescales before assuming it does.

## 3. Operational Context

Real-world space-strategy and counterspace-capability discourse (in defense-policy and space-security
literature) actively discusses all four of these concepts as emerging or near-future developments not
yet fully reflected in most existing counterspace taxonomies, including this simulator's five-D's
framework — this topic exists so a future capability-extension decision in this project starts from
an accurate picture of where the real-world frontier currently sits, rather than from this simulator's
existing taxonomy alone.

## 4. Implementation Guidance

- **Before forcing a genuinely novel future capability concept into one of the existing five-D's
  categories, check whether it actually fits** — per the directed-energy example above, a capability
  that straddles reversible/irreversible by design may need a new modeling approach (e.g. a graduated
  dose-dependent effect) rather than a forced binary classification.
- **A future proliferated-constellation vignette should reconsider its COG analysis ([R309](R309-center-of-gravity-analysis.md))
  explicitly** rather than reusing a single-high-value-asset COG framing by default — ground
  infrastructure or C2 architecture is the more doctrinally plausible COG for this concept.
- **A future on-orbit-servicing-themed vignette concept should build on the existing "ambiguous RPO"
  inject template** (`inject_library.yaml`) as its nearest existing mechanism, per MSTR-002's seam
  principle, rather than inventing a parallel ambiguity model.
- **Any future cislunar/deep-space vignette concept should first verify the `Propagator`/
  `AccessProvider` seam's behavior at the relevant timescales**, not assume the existing LEO/MEO/GEO-
  validated behavior generalizes without checking.

## 5. Feature Mapping

Any future vignette or capability addition extending beyond the current five-D's scope is the direct
consumer; none of these concepts is currently implemented.

## 6. Related Topics

[`research/03-counterspace-taxonomy.md`](../03-counterspace-taxonomy.md), [R310](R310-effects-based-operations.md) (Effects-Based Operations), [R505](R505-multi-domain-operations.md) (Multi-Domain
Operations).
