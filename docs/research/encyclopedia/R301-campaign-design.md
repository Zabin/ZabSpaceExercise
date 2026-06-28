# R301 — Campaign Design

> **Document ID:** R301
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** —
> **Referenced By:** [R302](R302-operational-art.md), [R305](R305-mission-analysis.md), [R312](R312-space-strategy.md), [R313](R313-joint-and-combined-operations.md), DOM-009
> **Produces:** the structural vocabulary behind multi-vignette mission-set progression
> **Feature Mapping:** FS-106 (White Cell Dashboard), vignette authoring (`docs/scenarios/`)
> **Related Topics:** [R302](R302-operational-art.md) (Operational Art), [R305](R305-mission-analysis.md) (Mission Analysis), [R312](R312-space-strategy.md) (Space Strategy), DOM-001
> §4 (vignette progression), DOM-009 (doctrine-to-content translation)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 1

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

The simulator's 19-vignette library includes explicit "mission-set" groupings (3 mission-set
vignettes per `CLAUDE.md`) — a sequence of related operations toward a connected strategic end,
distinct from a single stand-alone scenario. This topic gives the implementer the campaign-design
vocabulary needed to extend that grouping coherently, rather than treating "mission-set" as an
arbitrary content tag.

## 2. Scope

Covers: the joint-doctrine definition of a campaign as a connected sequence of major operations,
branch/sequel structure, and the throughline a campaign-level center of gravity provides across
tactically distinct vignettes. Does **not** cover: the tactics-to-strategy connective reasoning
*within* a single operation (that is [R302](R302-operational-art.md), Operational Art), or the
translation of a campaign's intent into one vignette's checkable task list (that is
[R305](R305-mission-analysis.md), Mission Analysis).

## 3. Concepts

**A campaign is a series of related major operations linked in time, space, and purpose to
achieve a strategic objective** — the working joint-doctrine definition in [JP 5-0, *Joint
Planning*ed.](https://www.jcs.mil/Doctrine/Joint-Doctrine-Pubs/5-0-Planning-Series/) (validated
2020-12-01). Individual vignettes can share a fictional universe without being a campaign in this
sense; what makes a sequence a campaign is that an outcome in one operation plausibly changes the
starting conditions or objectives of the next (e.g. a Blue cell that loses custody of a key asset
in mission-set vignette 1 should plausibly face a harder SDA picture in vignette 2).

**Branches and sequels.** JP 5-0 explicitly links campaign planning and execution to contingency
planning by defining a *branch* as a planned option built into the base plan for changing the
disposition, orientation, or direction of movement to aid success of the operation, and a *sequel*
as the subsequent major operation based on the possible outcomes of the current operation —
[JP 5-0](https://www.jcs.mil/Doctrine/Joint-Doctrine-Pubs/5-0-Planning-Series/) §III.4. The
engine's AAR branch-compare (P7) is a *debrief-time* branch-exploration tool that lets a facilitator
inspect alternate decision points within an already-recorded run; it is not a live branch/sequel
campaign-execution engine — a true branching campaign (the next vignette selected based on the
outcome of the current one, in JP 5-0's sense) is not yet implemented and would be new Feature
Specification scope, not an extension of AAR.

**Center of gravity persists across a campaign even as tactical situations change**
([R309](R309-center-of-gravity-analysis.md)). A campaign-design document should identify the
*strategic* objective threading through the sequence (e.g. "maintain assured access to a specific
orbital regime") distinct from each vignette's local, tactical objectives — this is the throughline
DOM-009's translation pipeline needs in order to keep a mission-set's vignettes doctrinally coherent
rather than independently-designed episodes loosely bundled.

### Sources

- *JP 5-0, Joint Planning* (Joint Chiefs of Staff, validated 2020-12-01) — [live](https://www.jcs.mil/Doctrine/Joint-Doctrine-Pubs/5-0-Planning-Series/)
  · [snapshot](https://web.archive.org/web/2026/https://www.jcs.mil/Doctrine/Joint-Doctrine-Pubs/5-0-Planning-Series/)
  · accessed 2026-06-27.

## 4. Operational Context

Real military campaign design explicitly sequences operations toward a strategic end — campaign
plans nest a series of operations under one campaign objective, each operation's success criteria
feeding the next via its branch/sequel structure — and after-action assessment from one operation
legitimately changes planning assumptions for the next, exactly the property a "mission-set"
vignette grouping should aspire to model, even at PME-appropriate scale.

## 5. Implementation Guidance

- **A new mission-set vignette group should state its persistent strategic objective explicitly** in
  the vignette's `intro_brief` or a new metadata field, distinct from each member vignette's own
  `objectives` — this gives DOM-009's doctrine-translation step something concrete to check
  coherence against.
- **If branching campaign progression is ever built, model it as a branch/sequel structure per
  JP 5-0 §III.4** (state transfer between vignettes, conditional vignette selection keyed to the
  prior outcome) as a new Feature Specification, not an extension of the AAR's read-only
  branch-compare — conflating the two would blur AAR's deliberately read-only, replay-safe design
  (MSTR-002 §5) with a new state-mutating mechanic.
- **Don't encode a hardcoded vignette-sequence dependency in engine code** — per MSTR-002 §2
  invariant 6, a campaign sequence (even informal, doc-only today) should remain expressible as
  vignette-file metadata/ordering, not a code-level chain.

## 6. Feature Mapping

FS-106 (White Cell Dashboard) is the nearest existing consumer (a facilitator running a mission-set
needs to see the sequence); a future campaign-progression feature would be new FS scope.

## 7. Related Topics

[R302](R302-operational-art.md) (Operational Art, the tactics-to-strategy connective layer within one operation), [R305](R305-mission-analysis.md) (Mission
Analysis), [R312](R312-space-strategy.md) (Space Strategy, the strategic end a campaign serves), DOM-009 (translation pipeline).
