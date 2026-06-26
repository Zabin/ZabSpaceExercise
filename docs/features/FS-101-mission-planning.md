# FS-101 — Mission Planning

> **Document ID:** FS-101
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [DOM-001](../domains/DOM-001-training-framework.md), [R101](../research/encyclopedia/R101-orbital-mechanics-for-operations.md), [R112](../research/encyclopedia/R112-propulsion-and-maneuver-planning.md), [R120](../research/encyclopedia/R120-access-window-and-geometry-planning.md)
> **Referenced By:** [R101](../research/encyclopedia/R101-orbital-mechanics-for-operations.md), [R112](../research/encyclopedia/R112-propulsion-and-maneuver-planning.md), [R120](../research/encyclopedia/R120-access-window-and-geometry-planning.md), [R311](../research/encyclopedia/R311-course-of-action-analysis.md)
> **Produces:** the planning surface consumed by [FS-105](FS-105-spacecraft-operations.md) once a plan is committed
> **Feature Mapping:** FS-101 (this document)
> **Related Topics:** [DOM-001](../domains/DOM-001-training-framework.md) §7, [R311](../research/encyclopedia/R311-course-of-action-analysis.md) (course-of-action analysis, candidate future scope)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

## 1. Purpose

Mission Planning is the capability by which a cell formulates and previews orders **before**
committing them — the UI-and-workflow expression of the project's load-bearing "plan-first"
invariant ([`CLAUDE.md`](../../CLAUDE.md) §"Load-bearing invariants" #4): operators plan commands that
execute at the next valid access window and task sensors for collection; they never act instantly
on perfect knowledge. FS-101 is the specification for that planning surface, independent of which
specific bus/payload verb is being planned (that detail belongs to [FS-105](FS-105-spacecraft-operations.md)).

## 2. Scope

In scope: order drafting, pre-commit validation/preview (the "why can't I?" feedback loop), window
visibility (when will this plan actually execute), and Δv/resource-cost preview for maneuver plans.
Out of scope: the actual execution-time behavior of a committed order (owned by
[FS-102](FS-102-command-scheduling.md)), and the console chrome for non-planning operator actions ([FS-105](FS-105-spacecraft-operations.md)).

## 3. Capability requirements

- **Plans must be previewable without commitment.** A cell must be able to see whether a candidate
  order would validate, when its access window opens/closes, and what it would cost, without that
  preview being indistinguishable from actually issuing the order. This is a read-only operation
  with no World-state side effect.
- **Plans must reflect real regime and propagator constraints, not idealized reachability.** Per
  [R101](../research/encyclopedia/R101-orbital-mechanics-for-operations.md) §6, a planning UI must not offer an action against a target the orbital regime makes
  physically unreachable, nor imply continuous access where the underlying geometry is windowed.
- **Maneuver plans must preview real Δv cost across all supported entry modes.** Per
  [R112](../research/encyclopedia/R112-propulsion-and-maneuver-planning.md) §5, a planning UI must surface Δv-economy honestly for whichever of the six entry modes
  (eci / lvlh / finite_burn / target_coe / hohmann / plane_change) the operator is using — collapsing
  them to a single generic "maneuver" estimate would hide a real operational tradeoff.
- **Window display must reflect genuine sampled/bisected geometry.** Per [R120](../research/encyclopedia/R120-access-window-and-geometry-planning.md) §5, a planning UI
  showing "next window" or "window closes in" must be driven by the same access computation the
  engine uses to gate execution — not a separately-computed or idealized continuous-access estimate
  that could disagree with what actually happens at execution time.
- **A rejected/invalid plan must explain why, not just that it failed.** Consistent with the
  pre-disabled-button pattern ([DOM-007](../domains/DOM-007-human-factors-framework.md) §4), the planning surface should tell the
  operator *which* constraint blocked the plan (no window, regime mismatch, insufficient resource)
  so the operator learns the domain constraint, not just "no."

## 4. Non-goals

- Mission Planning does not add a new effect category or gameplay mechanic — it is a workflow layer
  over existing order/window primitives.
- Course-of-action comparison (planning and weighing *multiple* candidate plans against each other)
  is explicitly **not** in this version's scope; [R311](../research/encyclopedia/R311-course-of-action-analysis.md) §5 names a future COA-comparison feature as
  a candidate extension under FS-101, not a requirement of this spec.

## 5. Educational value

Per [DOM-001](../domains/DOM-001-training-framework.md) §7, this feature must state which objective class(es) it serves: Mission
Planning exercises the "plan against real constraints" competency directly — a cell that learns to
read window/regime/Δv feedback before committing is practicing the same judgment a real operator
exercises, not a simulator-specific skill. It applies across the training progression wherever a
vignette requires a maneuver, tasking, or engagement plan (i.e., most of the 19-vignette library).

## 6. Non-functional requirements

- **Replay-safety.** The preview/validation path must be a read-only mirror of the real
  validate→window path (the same contract `dry_run()` already provides at the engine layer per
  [`CLAUDE.md`](../../CLAUDE.md)'s order-system description) — it must schedule, register, or book nothing.
- **Human factors.** Per [DOM-007](../domains/DOM-007-human-factors-framework.md) §3, the friction of "you must plan, you cannot act
  instantly" is *intentional* and must read that way to the operator — the UI should make clear
  this is a domain constraint, not a bug or a slow control.

## 7. Open questions

- Whether `training_objectives:` should become an explicit vignette schema field (currently implicit
  in `intro_brief` prose) is flagged in [DOM-001](../domains/DOM-001-training-framework.md) §8 as candidate scope for an FS-101-derived
  Implementation Package — not decided in this spec.
- Course-of-action comparison ([R311](../research/encyclopedia/R311-course-of-action-analysis.md) §5) is named as a candidate future extension, not committed
  scope; if pursued, it should be evaluated as either an FS-101 revision or a new FS ID rather than
  assumed.

## 8. Related Topics

[R101](../research/encyclopedia/R101-orbital-mechanics-for-operations.md) (regime/propagator constraints), [R112](../research/encyclopedia/R112-propulsion-and-maneuver-planning.md) (Δv economy), [R120](../research/encyclopedia/R120-access-window-and-geometry-planning.md) (access-window
computation), [R311](../research/encyclopedia/R311-course-of-action-analysis.md) (COA analysis, candidate extension), [DOM-001](../domains/DOM-001-training-framework.md) (owning training framework),
[FS-102](FS-102-command-scheduling.md) (what happens after a plan is committed), [FS-105](FS-105-spacecraft-operations.md) (the console this planning surface
lives inside).
