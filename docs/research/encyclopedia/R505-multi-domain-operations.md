# R505 — Multi-Domain Operations

> **Document ID:** R505
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R504](R504-future-space-warfare-concepts.md)
> **Referenced By:** —
> **Produces:** forward-looking context for whether/how this simulator's space-only scope might one day model effects flowing to/from other domains
> **Feature Mapping:** any future cross-domain vignette concept (e.g. a space-effect with a documented cyber- or terrestrial-domain trigger/consequence)
> **Related Topics:** [R504](R504-future-space-warfare-concepts.md) (Future Space Warfare Concepts), [R310](R310-effects-based-operations.md) (Effects-Based Operations — the
> cascading-effects vocabulary this topic's cross-domain effects would need), [R302](R302-operational-art.md) (Operational
> Art — lines of operation, the connective concept across domains)
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2 (Tier A doctrine + DoD strategy document — see §3 Sources)

[↑ Tier R500 index](R500-index.md) · [Encyclopedia index](INDEX.md)

**DOM-008 §6 tag:** neither in-world AI nor coding-agent practice — forward-looking doctrinal context
for potential future scope extension.

## 1. Purpose

This simulator is deliberately space-domain-scoped (per CLAUDE.md, the engine models space/ground
assets and access channels, not a full joint-force simulation). Multi-domain operations (MDO) doctrine
— the real-world military framework for synchronizing effects across space, cyber, air, land, and
maritime domains — is nonetheless the strategic context space control actually sits inside in
practice. This topic gives the implementer that context, primarily to inform vignette *narrative*
framing (`intro_brief`) rather than to motivate building a full cross-domain engine.

## 2. Scope

Covers: the doctrinal shape of multi-domain operations/JADC2 (why space effects are valued for their
cross-domain enabling role, not in isolation) as narrative grounding for vignette `intro_brief`
content, and the explicit argument for why this stays narrative rather than mechanical. Does **not**
cover: the emerging counterspace-capability concepts MDO doctrine interacts with
([R504](R504-future-space-warfare-concepts.md)'s job), the cascading-effects vocabulary a genuine
cross-domain mechanical effect would need if ever authorized
([R310](R310-effects-based-operations.md)'s job), or operational-art connective concepts generally
([R302](R302-operational-art.md)'s job) — this topic is specifically about the space-to-other-domain
boundary question, not operational art broadly.

## 3. Concepts

**MDO doctrine: synchronizing effects across domains toward a single objective, not domain-by-domain
stovepiping.** The U.S. Army's foundational multi-domain concept document,
[TRADOC Pamphlet 525-3-1, *The U.S. Army in Multi-Domain Operations 2028*](https://madsciblog.tradoc.army.mil/tag/tradoc-pamphlet-525-3-1-the-u-s-army-in-multi-domain-operations-2028/)
(6 December 2018), frames the problem explicitly as adversaries achieving strategic aims through
"layered standoff" across all domains — land, sea, air, space, and cyberspace — and the joint force's
answer as rapid, continuous cross-domain integration rather than domain-by-domain campaigns. A
real MDO-framed space effect (e.g. denying adversary SDA) is valuable specifically because of what it
enables in another domain (e.g. a terrestrial maneuver that depends on the adversary not detecting
it) — this is the doctrinal reason a vignette's `intro_brief` can usefully gesture at a cross-domain
stake (the space effect matters *because* of a terrestrial consequence) even though the engine itself
only models and resolves the space-domain mechanics.

**JADC2 is the current DoD implementation vector for cross-domain synchronization at the C2 layer.**
The Department of Defense's own
[*Summary of the Joint All-Domain Command and Control (JADC2) Strategy*](https://media.defense.gov/2022/Mar/17/2002958406/-1/-1/1/SUMMARY-OF-THE-JOINT-ALL-DOMAIN-COMMAND-AND-CONTROL-STRATEGY.PDF)
(signed March 2022) states the goal as "developing the warfighting capability to sense, make sense,
and act at all levels and phases of war, across all domains" — a real-world architectural effort to
fuse sensor and effector data across domains that this simulator's `SessionAPI`/`CellController`
fog-of-war boundary is a distant, single-domain analog of (a session-scoped, cell-filtered "sense and
act" boundary, not a cross-domain one). JADC2's five lines of effort (data enterprise, human
enterprise, technology enterprise, nuclear C2/C3 integration, mission-partner information sharing) are
DoD-scale infrastructure concerns well beyond this simulator's scope, but the underlying "sense, make
sense, act, across domains" framing is the doctrinal backdrop any future cross-domain vignette
narrative should draw on.

**The space-domain-only engine boundary is a deliberate scope choice, not an oversight.** CLAUDE.md's
architecture is space/ground-asset-scoped by design; a cross-domain *narrative* stake in a vignette's
`intro_brief` is doctrinally appropriate (per the MDO framing above) and costs nothing
architecturally, but actually modeling a cyber-domain or terrestrial-domain effect mechanically
(building toward anything resembling JADC2's actual cross-domain data/sensor fusion) would be a
significant scope expansion that should not be undertaken implicitly through vignette-authoring
pressure.

**Cyber is the one channel already partially cross-domain.** The existing `cyber` action (not
window-gated, [`engine/cyber.py`](../../../spacesim/engine/cyber.py)) already models an attack vector (`access_vector`) that in reality
often originates terrestrially (a compromised ground-segment supply chain, ties to [R116](R116-cyber-operations-against-space-systems.md)'s
`ground_modem`/`seize_c2` vector) — this is the existing engine feature closest to genuine
cross-domain modeling, and any future MDO-themed vignette content should build on this existing
mechanic rather than inventing a new one.

**Dependencies and seams: where a future cross-domain mechanical link, if ever authorized, would have
to attach.** If a future feature ever modeled a genuine cross-domain *mechanical* consequence (e.g. a
terrestrial inject affecting space-domain access), it would need a documented seam analogous to
`AccessProvider`/`EffectResolver` (CLAUDE.md), not an ad hoc special case — this is a forward-looking
note, not a description of anything currently planned or authorized.

### Sources

- *U.S. Army Training and Doctrine Command. TRADOC Pamphlet 525-3-1: The U.S. Army in Multi-Domain
  Operations 2028* (6 December 2018) —
  [live](https://madsciblog.tradoc.army.mil/tag/tradoc-pamphlet-525-3-1-the-u-s-army-in-multi-domain-operations-2028/)
  · [snapshot](https://web.archive.org/web/2026*/https://madsciblog.tradoc.army.mil/tag/tradoc-pamphlet-525-3-1-the-u-s-army-in-multi-domain-operations-2028/)
  · accessed 2026-07-02.
- *U.S. Department of Defense. Summary of the Joint All-Domain Command and Control (JADC2) Strategy*
  (signed March 2022) —
  [live](https://media.defense.gov/2022/Mar/17/2002958406/-1/-1/1/SUMMARY-OF-THE-JOINT-ALL-DOMAIN-COMMAND-AND-CONTROL-STRATEGY.PDF)
  · [snapshot](https://web.archive.org/web/2026*/https://media.defense.gov/2022/Mar/17/2002958406/-1/-1/1/SUMMARY-OF-THE-JOINT-ALL-DOMAIN-COMMAND-AND-CONTROL-STRATEGY.PDF)
  · accessed 2026-07-02.

## 4. Operational Context

Multi-domain operations is the dominant organizing doctrine in current (2020s) U.S. and allied joint
military planning specifically because single-domain campaigns are increasingly understood as
strategically insufficient in isolation (TRADOC 525-3-1's "layered standoff" framing, §3) — this is
the real-world strategic backdrop space control exercises in this simulator are implicitly part of,
even though the engine itself remains correctly scoped to the space domain alone. JADC2's active,
ongoing (as of the 2022 strategy) DoD implementation effort confirms this is current operating
doctrine, not a superseded or historical framework.

### Sources

Uses the same sources cited inline in §3 (TRADOC 525-3-1; DoD JADC2 Strategy Summary 2022); no
additional sources introduced in this section.

## 5. Implementation Guidance

- **Use MDO doctrine to inform `intro_brief` narrative framing** (the space effect matters because of
  a stated cross-domain consequence, per TRADOC 525-3-1's layered-standoff logic) **without expanding
  the engine's actual mechanical scope** — a narrative stake costs nothing architecturally and is
  doctrinally well-grounded; a mechanical cross-domain effect (anything resembling JADC2's actual
  cross-domain sensor/data fusion) would be a significant, currently unauthorized scope expansion.
- **Build any future cross-domain-themed vignette content on the existing `cyber` action's
  partially-cross-domain character** (its terrestrial-originating attack vectors) rather than
  inventing a new cross-domain mechanic.
- **If a genuine cross-domain mechanical feature is ever proposed, require it to define a documented
  seam first** (analogous to `AccessProvider`/`EffectResolver`), per MSTR-002's seam principle, rather
  than special-casing a cross-domain effect directly into existing space-domain logic — and treat it
  as a JADC2-scale undertaking in miniature, not a small addition, given the real DoD effort's scope.

## 6. Feature Mapping

Any future cross-domain vignette concept (narrative-only, per the guidance above) is the direct
consumer; no mechanical cross-domain feature exists or is currently authorized.

## 7. Related Topics

[R504](R504-future-space-warfare-concepts.md) (Future Space Warfare Concepts), [R310](R310-effects-based-operations.md) (Effects-Based Operations), [R302](R302-operational-art.md) (Operational Art).
