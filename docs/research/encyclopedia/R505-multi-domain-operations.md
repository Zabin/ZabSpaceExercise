# R505 — Multi-Domain Operations

> **Document ID:** R505
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** R504
> **Referenced By:** —
> **Produces:** forward-looking context for whether/how this simulator's space-only scope might one day model effects flowing to/from other domains
> **Feature Mapping:** any future cross-domain vignette concept (e.g. a space-effect with a documented cyber- or terrestrial-domain trigger/consequence)
> **Related Topics:** R504 (Future Space Warfare Concepts), R310 (Effects-Based Operations — the
> cascading-effects vocabulary this topic's cross-domain effects would need), R302 (Operational
> Art — lines of operation, the connective concept across domains)

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

## 2. Concepts

**MDO doctrine: synchronizing effects across domains toward a single objective, not domain-by-domain
stovepiping.** Real MDO doctrine treats a space effect (e.g. denying adversary SDA) as valuable
specifically because of what it enables in another domain (e.g. a terrestrial maneuver that depends
on the adversary not detecting it) — this is the doctrinal reason a vignette's `intro_brief` can
usefully gesture at a cross-domain stake (the space effect matters *because* of a terrestrial
consequence) even though the engine itself only models and resolves the space-domain mechanics.

**The space-domain-only engine boundary is a deliberate scope choice, not an oversight.** CLAUDE.md's
architecture is space/ground-asset-scoped by design; a cross-domain *narrative* stake in a vignette's
`intro_brief` is doctrinally appropriate and costs nothing architecturally, but actually modeling a
cyber-domain or terrestrial-domain effect mechanically (rather than narratively) would be a
significant scope expansion that should not be undertaken implicitly through vignette-authoring
pressure.

**Cyber is the one channel already partially cross-domain.** The existing `cyber` action (not
window-gated, `engine/cyber.py`) already models an attack vector (`access_vector`) that in reality
often originates terrestrially (a compromised ground-segment supply chain, ties to R116's
`ground_modem`/`seize_c2` vector) — this is the existing engine feature closest to genuine
cross-domain modeling, and any future MDO-themed vignette content should build on this existing
mechanic rather than inventing a new one.

**Dependencies and seams: where a future cross-domain mechanical link, if ever authorized, would have
to attach.** If a future feature ever modeled a genuine cross-domain *mechanical* consequence (e.g. a
terrestrial inject affecting space-domain access), it would need a documented seam analogous to
`AccessProvider`/`EffectResolver` (CLAUDE.md), not an ad hoc special case — this is a forward-looking
note, not a description of anything currently planned or authorized.

## 3. Operational Context

Multi-domain operations is the dominant organizing doctrine in current (2020s) U.S. and allied joint
military planning specifically because single-domain campaigns are increasingly understood as
strategically insufficient in isolation — this is the real-world strategic backdrop space control
exercises in this simulator are implicitly part of, even though the engine itself remains correctly
scoped to the space domain alone.

## 4. Implementation Guidance

- **Use MDO doctrine to inform `intro_brief` narrative framing** (the space effect matters because of
  a stated cross-domain consequence) **without expanding the engine's actual mechanical scope** — a
  narrative stake costs nothing architecturally and is doctrinally well-grounded; a mechanical
  cross-domain effect would be a significant, currently unauthorized scope expansion.
- **Build any future cross-domain-themed vignette content on the existing `cyber` action's
  partially-cross-domain character** (its terrestrial-originating attack vectors) rather than
  inventing a new cross-domain mechanic.
- **If a genuine cross-domain mechanical feature is ever proposed, require it to define a documented
  seam first** (analogous to `AccessProvider`/`EffectResolver`), per MSTR-002's seam principle, rather
  than special-casing a cross-domain effect directly into existing space-domain logic.

## 5. Feature Mapping

Any future cross-domain vignette concept (narrative-only, per the guidance above) is the direct
consumer; no mechanical cross-domain feature exists or is currently authorized.

## 6. Related Topics

R504 (Future Space Warfare Concepts), R310 (Effects-Based Operations), R302 (Operational Art).
