# R209 — Planning Theory

> **Document ID:** R209
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** R202, R206
> **Referenced By:** R106, R311, R507
> **Produces:** the vocabulary for plan revision underlying `OrderSystem`'s plan/cancel/replace model
> **Feature Mapping:** FS-101 (Mission Planning)
> **Related Topics:** R106 (Mission Operations — the concrete plan/task/execute/assess loop), R202
> (Decision Theory), R208 (OODA Loops — the cycle planning sits inside), R507 (Autonomous Planning
> Systems)

[↑ Tier R200 index](R200-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

"Plan-first" (MSTR-002 §2 invariant 4) is the simulator's load-bearing invariant, but a plan in this
system is never a one-shot, fire-and-forget artifact — it is committed against a window that may not
materialize as expected, observed by custody that may degrade, and is explicitly cancelable
(`OrderSystem`'s tag-cancel). This topic gives the implementer the planning-theory vocabulary for why
a *revisable* plan, not a rigid one, is the correct model under partial information.

## 2. Concepts

**A plan is a commitment under uncertainty, not a prediction.** Planning theory distinguishes a plan
(a commitment to a course of action, made now, to be executed later) from a prediction (a claim
about what will happen) — issuing an `Order` commits to *attempting* an action at the next valid
window; it does not predict the window will be exactly as currently modeled, especially if intervening
events (a maneuver invalidating cached windows, R120 §2) change the geometry.

**Plan revision must be cheap, or operators will under-plan.** If canceling or replacing a
committed plan is costly or impossible, decision-makers rationally avoid committing to plans at all,
which defeats the plan-first model's purpose. `OrderSystem`'s replay-safe tag-cancel (cancel-before-
execute leaves no trace in the eventlog, R103/R118) is the concrete mechanism keeping plan revision
cheap, consistent with this principle.

**Hierarchical planning: nested levels of commitment.** Mission-level intent (the vignette's
objectives) constrains operational-level plans (which targets/windows to pursue) which constrain
tactical-level orders (the specific `Order` issued) — R305 (Mission Analysis, Tier R300) covers the
intent-translation step; this topic covers the structural fact that plans at different grains have
different revision costs and time horizons.

**Contingency planning and branch points.** A well-formed plan anticipates likely deviations (a
window not materializing, a track dropping below weapons-quality) and pre-commits to a fallback —
the AAR's branch-compare feature (P7) is the debrief-side mirror of this: it lets a facilitator show
what *would* have happened under an alternative branch, which is pedagogically most useful when
compared against a plan that explicitly considered that branch versus one that didn't.

## 3. Operational Context

Real operational planning (military, but also any plan-under-uncertainty domain like emergency
response) treats a plan as a living, revisable commitment with named branch/decision points, not a
fixed script — "no plan survives contact with the enemy" is the doctrinal aphorism for exactly the
gap this topic formalizes between plan-as-prediction and plan-as-revisable-commitment.

## 4. Implementation Guidance

- **A new order type must support the same cancel-before-execute revision path as existing
  actions** — per R118's guidance, an order type that can't be cleanly cancelled before its window
  reintroduces a planning-revision cost the rest of the engine deliberately avoids.
- **A future "contingency" or "if-then" order feature (candidate, not yet built) should be modeled as
  an explicit branch point in the plan, not as conditional logic hidden inside a single order** —
  keeping branch points explicit and visible is what makes them debrief-able in the AAR per MSTR-003
  §6.
- **Don't let a future autonomous planning assistant (R507) silently re-plan on the operator's
  behalf when conditions change** — per DOM-008 §4, surfacing "this plan's window assumption no
  longer holds, reconsider" is advisory; automatically substituting a new plan is not.

## 5. Feature Mapping

FS-101 (Mission Planning) is the direct consumer — any planning UI enhancement should preserve the
cheap-revision property this topic identifies as load-bearing.

## 6. Related Topics

R106 (Mission Operations, the concrete loop), R202 (Decision Theory), R208 (OODA Loops, the cycle
planning sits inside), R507 (Autonomous Planning Systems, the forward-looking extension).
