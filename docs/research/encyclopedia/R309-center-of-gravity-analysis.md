# R309 — Center of Gravity Analysis

> **Document ID:** R309
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R302](R302-operational-art.md)
> **Referenced By:** [R310](R310-effects-based-operations.md)
> **Produces:** the vocabulary for identifying what a vignette's design is actually testing an operator's ability to protect or attack
> **Feature Mapping:** vignette authoring (`docs/scenarios/`)
> **Related Topics:** [R302](R302-operational-art.md) (Operational Art), [R310](R310-effects-based-operations.md) (Effects-Based Operations — the direct consumer of
> this topic's COG concept), [R301](R301-campaign-design.md) (Campaign Design)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 1

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

A well-designed vignette implicitly identifies a "center of gravity" — the specific capability or
asset whose loss would be most damaging to a side's freedom of action — and structures objectives
around protecting or attacking it. This topic gives a vignette author the formal vocabulary to
identify that deliberately, since an unclear COG produces a vignette whose objectives feel arbitrary
rather than doctrinally motivated.

## 2. Scope

Covers: the center-of-gravity concept and the critical capabilities/critical requirements/critical
vulnerabilities (CC/CR/CV) analytical chain, and the attacker/defender asymmetry in COG
identification. Does **not** cover: the broader tactics-to-strategy reasoning COG analysis sits
inside (that is [R302](R302-operational-art.md), Operational Art) or how a COG finding is converted
into a cascading-effects plan (that is [R310](R310-effects-based-operations.md), Effects-Based
Operations).

## 3. Concepts

**Center of gravity: the source of an actor's power and freedom of action.** The concept originates
with Carl von Clausewitz's *On War* (1832) and was formalized for modern joint planning use by Joe
Strange and Richard Iron in
["Understanding Centers of Gravity and Critical Vulnerabilities"](https://theforge.defence.gov.au/sites/default/files/adfwtc04_centres_of_gravity_and_critical_vulnerabilities_by_strange_and_iron.pdf)
(*Joint Force Quarterly*, 2005), which defines a center of gravity not necessarily as the most
physically powerful asset, but as the one whose loss or neutralization most degrades the actor's
ability to achieve its objectives — for a Blue constellation, this might be a single high-value C2
relay node (`ISL_LINK`-critical) rather than the largest or most expensive satellite; for Red, it
might be a specific SDA/custody-denial capability rather than a weapons platform.

**Critical capabilities, critical requirements, critical vulnerabilities (the CC/CR/CV chain).**
Strange and Iron's analytical model chains a COG's critical capabilities (what it can do that
matters) to its critical requirements (the conditions/resources needed for those capabilities to
function — e.g. a ground station's uplink access, [R107](R107-ground-segment-operations.md)) to its
critical vulnerabilities (the specific exploitable weaknesses in those requirements — e.g. an
undefended ground segment, the doctrinal basis for the `ground_modem`/`seize_c2` cyber vector,
[R116](R116-cyber-operations-against-space-systems.md)). This chain is the formal reasoning path
from "what matters" to "what should an effect category actually target."

**COG analysis differs for the attacker and the defender of the same system.** Strange and Iron note
that a force's own COG analysis of its own assets (what must be protected) and an adversary's COG
analysis of the same assets (what would be most valuable to attack) should converge on the same node
if both sides are doctrinally sound — a vignette where Blue's defended asset and Red's actual
objective don't match is either a deliberate deception-themed design (testing whether Blue correctly
identifies the real threat) or an unintentional design flaw.

### Sources

- *Joe Strange and Richard Iron, "Understanding Centers of Gravity and Critical Vulnerabilities"*
  (Joint Force Quarterly, 2005; Australian Defence Force "The Forge" reprint) — [live](https://theforge.defence.gov.au/sites/default/files/adfwtc04_centres_of_gravity_and_critical_vulnerabilities_by_strange_and_iron.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://theforge.defence.gov.au/sites/default/files/adfwtc04_centres_of_gravity_and_critical_vulnerabilities_by_strange_and_iron.pdf)
  · accessed 2026-06-27.

## 4. Operational Context

Center-of-gravity analysis (from Clausewitz through modern joint planning doctrine) is the standard
first step in targeting and campaign design precisely because resources for both offense and defense
are finite — effort spent protecting or attacking a non-COG asset is doctrinally wasted effort, and
real operational planning treats correct COG identification as the single highest-leverage analytical
step in the entire planning process.

## 5. Implementation Guidance

- **A vignette's threat picture (`intro_brief`) should make the intended COG for each side
  identifiable, even if not stated as a literal label** — a Blue cell should be able to infer, from
  the brief and the scenario's asset layout, which asset/capability matters most; if every asset
  seems equally important, the vignette likely lacks a clear COG and its objectives may feel
  arbitrary.
- **A vignette's `objectives` block should be checkable against the CC/CR/CV chain**: does
  completing the objective actually deny a critical requirement of the opposing side's COG, or is it
  a plausible-sounding but doctrinally disconnected task? Use [R305](R305-mission-analysis.md)'s essential-task framing alongside
  this check.
- **A deception-themed vignette (deliberately mismatched apparent vs. real COG) should be tagged as
  such in author-facing notes**, distinguishing intentional design from an unintentional COG-target
  mismatch that would otherwise look like the same thing to a reviewer.

## 6. Feature Mapping

Vignette authoring (`docs/scenarios/`) is the direct consumer.

## 7. Related Topics

[R302](R302-operational-art.md) (Operational Art, the broader connective layer), [R310](R310-effects-based-operations.md) (Effects-Based Operations, which uses COG
identification as its starting point), [R301](R301-campaign-design.md) (Campaign Design, where COG can shift across a
multi-vignette sequence).
