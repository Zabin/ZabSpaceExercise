# R301 — Campaign Design

> **Document ID:** R301
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** —
> **Referenced By:** R302, R305, R312, DOM-009
> **Produces:** the structural vocabulary behind multi-vignette mission-set progression
> **Feature Mapping:** FS-106 (White Cell Dashboard), vignette authoring (`docs/scenarios/`)
> **Related Topics:** R302 (Operational Art), R305 (Mission Analysis), R312 (Space Strategy), DOM-001
> §4 (vignette progression), DOM-009 (doctrine-to-content translation)

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

The simulator's 19-vignette library includes explicit "mission-set" groupings (3 mission-set
vignettes per `CLAUDE.md`) — a sequence of related operations toward a connected strategic end,
distinct from a single stand-alone scenario. This topic gives the implementer the campaign-design
vocabulary needed to extend that grouping coherently, rather than treating "mission-set" as an
arbitrary content tag.

## 2. Concepts

**A campaign is a sequence of operations connected by a persistent strategic objective, not just a
shared setting.** Individual vignettes can share a fictional universe without being a campaign; what
makes a sequence a campaign is that an outcome in one operation plausibly changes the starting
conditions or objectives of the next (e.g. a Blue cell that loses custody of a key asset in
mission-set vignette 1 should plausibly face a harder SDA picture in vignette 2).

**Center of gravity persists across a campaign even as tactical situations change (R309).** A
campaign-design document should identify the *strategic* objective threading through the sequence
(e.g. "maintain assured access to a specific orbital regime") distinct from each vignette's local,
tactical objectives — this is the throughline DOM-009's translation pipeline needs in order to keep a
mission-set's vignettes doctrinally coherent rather than independently-designed episodes loosely
bundled.

**Branching vs. linear campaign structure.** A linear campaign always proceeds through the same
vignette sequence regardless of outcome; a branching campaign changes the next vignette's starting
conditions or even which vignette comes next based on the prior outcome. The engine's AAR
branch-compare (P7) is a *debrief-time* branch exploration tool, not a live campaign-branching
engine — a true branching campaign (next vignette selected based on outcome) is not yet implemented
and would be new Feature Specification scope, not an extension of AAR.

## 3. Operational Context

Real military campaign design explicitly sequences operations toward a strategic end (campaign
plans nest a series of operations under one campaign objective, each operation's success criteria
feeding the next), and after-action assessment from one operation legitimately changes planning
assumptions for the next — exactly the property a "mission-set" vignette grouping should aspire to
model, even at PME-appropriate scale.

## 4. Implementation Guidance

- **A new mission-set vignette group should state its persistent strategic objective explicitly** in
  the vignette's `intro_brief` or a new metadata field, distinct from each member vignette's own
  `objectives` — this gives DOM-009's doctrine-translation step something concrete to check
  coherence against.
- **If branching campaign progression is ever built, treat it as a new Feature Specification (state
  transfer between vignettes, conditional vignette selection), not an extension of the AAR's
  read-only branch-compare** — conflating the two would blur AAR's deliberately read-only,
  replay-safe design (MSTR-002 §5) with a new state-mutating mechanic.
- **Don't encode a hardcoded vignette-sequence dependency in engine code** — per MSTR-002 §2
  invariant 6, a campaign sequence (even informal, doc-only today) should remain expressible as
  vignette-file metadata/ordering, not a code-level chain.

## 5. Feature Mapping

FS-106 (White Cell Dashboard) is the nearest existing consumer (a facilitator running a mission-set
needs to see the sequence); a future campaign-progression feature would be new FS scope.

## 6. Related Topics

R302 (Operational Art, the tactics-to-strategy connective layer within one operation), R305 (Mission
Analysis), R312 (Space Strategy, the strategic end a campaign serves), DOM-009 (translation pipeline).
