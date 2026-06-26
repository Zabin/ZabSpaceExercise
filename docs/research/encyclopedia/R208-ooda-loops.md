# R208 — OODA Loops

> **Document ID:** R208
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R206](R206-bounded-rationality.md)
> **Referenced By:** DOM-002, MSTR-003
> **Produces:** the formal name for the loop MSTR-003 §3 calls "structurally unavoidable" and the basis for DOM-002's time-to-decision metric
> **Feature Mapping:** FS-101 (Mission Planning), FS-201 (Competency Assessment)
> **Related Topics:** [R206](R206-bounded-rationality.md) (Bounded Rationality), [R106](R106-mission-operations.md) (Mission Operations — the concrete plan/task/
> execute/assess loop this topic names formally), DOM-002 §4 ("time-to-decision... a proxy for
> OODA-loop tightness")

[↑ Tier R200 index](R200-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

MSTR-003 §3 names the OODA loop directly as the formal theory behind the simulator's plan-execute
unit of learning, and cites this topic by ID. This document gives the implementer the actual OODA
framework so that citation resolves to real content rather than a name-drop.

## 2. Concepts

**Observe-Orient-Decide-Act, as a continuous, contested cycle.** John Boyd's model: an actor
*observes* available information, *orients* it against existing mental models/doctrine/experience,
*decides* on an action, and *acts* — and the cycle immediately restarts, because the world has
changed (including by the actor's own action). Critically, OODA is not a one-shot pipeline; it is a
loop that runs continuously and competitively against an adversary's own loop.

**The "decision" step in this simulator is the order-issue moment; "observe" is custody-bounded.**
Mapped onto engine mechanics: Observe = whatever the cell's `TrackCatalog`/scene currently shows
(fog-of-war bounded, [R102](R102-space-domain-awareness.md)); Orient = the operator's mental model of the situation, informed by
mission brief/doctrine (not separately engine-modeled); Decide = forming and validating an `Order`
(`dry_run()` previews this step, [R103](R103-satellite-command-and-control.md)/[R120](R120-access-window-and-geometry-planning.md)); Act = `issue()` committing the order to execute at the
next valid window.

**Tightening one's own loop vs. disrupting the adversary's.** Boyd's competitive claim: an actor
that completes OODA cycles faster than its adversary gains a decisive advantage, partly by acting
before the adversary's orientation is even current. This is the formal justification for why
`time-to-decision` (DOM-002 §4) is a meaningful competency proxy: a cell that observes a window
opening and takes many sim-minutes to act has a slow loop relative to one that acts promptly, all
else equal — though see §4 below for the important caveat.

**Orientation is the step most vulnerable to bias and doctrine-mismatch.** Of the four steps,
Orient is where [R207](R207-cognitive-biases.md)'s cognitive biases and a cell's prior doctrinal assumptions do the most damage
— misreading an ambiguous RPO approach (DOM-003 §4's inject) as routine when it is hostile (or vice
versa) is an Orient-stage failure, not an Observe or Act failure, and a debrief that locates the
failure at the right OODA stage is more pedagogically useful than a generic "wrong call."

## 3. Operational Context

Boyd's OODA framework originated in air combat analysis and is now standard vocabulary across
military planning and cyber/SOC operations alike — "tightening the loop" and "getting inside the
adversary's OOPA loop" are live doctrinal phrases, and structured wargaming explicitly designs
scenarios to stress a player's loop (time pressure, deliberately ambiguous injects) for exactly the
reason MSTR-003 §2 states: this judgment cannot be taught by lecture.

## 4. Implementation Guidance

- **A "time-to-decision" metric (DOM-002 §4) must be reported as a loop-tightness proxy, not a
  context-free speed score** — fast action on a window that should have prompted more custody-
  building first ([R105](R105-custody-theory.md)) is not a tight, competent loop, it's a skipped Orient step; the metric needs
  to be paired with a custody-quality check, not read in isolation.
- **A future feature visualizing "where in the OODA loop did this decision go wrong" (an AAR
  enhancement) should use exactly these four stages as its taxonomy** — Observe (fog-of-war/custody
  gap), Orient (doctrine/bias misread), Decide (decision-criterion issue, [R202](R202-decision-theory.md)), Act (execution/
  window/validation failure) — rather than inventing a new failure taxonomy.
- **Don't design any feature that collapses Orient into Observe or Decide** — e.g., an AI advisor
  that goes straight from raw custody data to a recommended action without surfacing the
  orientation/interpretation step would erase the very stage MSTR-003 identifies as where judgment
  is actually exercised and practiced.

## 5. Feature Mapping

FS-201 (Competency Assessment) is the direct consumer of the time-to-decision metric; FS-101
(Mission Planning) is the surface where the loop is actually executed by the operator.

## 6. Related Topics

[R206](R206-bounded-rationality.md) (Bounded Rationality, the realistic constraints each OODA stage operates under), [R106](R106-mission-operations.md) (Mission
Operations, the concrete plan/task/execute/assess loop this formalism names), DOM-002 §4.
