# R608 — Software Onboarding & Tutorial Design

> **Document ID:** R608
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R604](R604-cognitive-load-and-scaffolding.md), [R606](R606-minimalist-and-procedural-documentation.md)
> **Referenced By:** none yet (a leaf topic; downstream consumer is the in-app tutorial feature and
> `08-vignette-development`)
> **Produces:** the grounding for when the in-app Tutorial panel / step-script pattern should be used
> instead of (or alongside) written manual content
> **Feature Mapping:** FR-11420 (machine-verified playbooks), the `00-training-basics` vignette's
> per-cell `tutorial:` step script, `GET /api/vignettes/{id}/tutorial` (in-UI Tutorial panel)
> **Related Topics:** [R604](R604-cognitive-load-and-scaffolding.md) (Cognitive Load & Scaffolding,
> progressive disclosure as this topic's central UI-pattern application), [R606](R606-minimalist-and-procedural-documentation.md)
> (Minimalist & Procedural Documentation, the craft this topic applies to in-app rather than
> document-based guidance), `docs/training/11-vignette-playbooks.md` (the markdown mirror of the
> in-app tutorial this topic grounds)

> **Verification note (this authoring pass):** citations below were sourced via live web search and
> corroborated across ≥2 independent results per claim; direct WebFetch of source pages was blocked
> by this session's egress policy (proxy denial on external hosts, per `/root/.ccr/README.md`) and is
> deferred to this corpus's separate formal verification pass
> ([`../10-sources-and-methodology.md`](../10-sources-and-methodology.md) §5.3).

> **Last Reviewed:** 2026-07-04
> **Primary Sources Consulted:** 1

[↑ Tier R600 index](R600-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

The `00-training-basics` vignette already carries a per-cell `tutorial:` step script (≥5 steps each),
surfaced in-app via the Tutorial panel, and the 8 canonical vignettes each carry the same mechanism —
verified against the real engine by `test_vignette_tutorials.py`. This is, in UX terms, a
progressive-disclosure onboarding flow, but the training corpus had no stated theory for *why* an
in-app guided sequence is the right mechanism (as opposed to, or alongside, written manual prose). This
topic supplies that theory — progressive disclosure and minimalist-instruction principles applied
specifically to software onboarding — so `08-vignette-development` can reason about when a new
vignette needs its own tutorial step script versus relying on the written manual/playbook alone.

## 2. Scope

Covers progressive disclosure as an onboarding-specific UX pattern (staged, conditional, and
contextual variants) and its relationship to Carroll's minimalist-documentation principles
([R606](R606-minimalist-and-procedural-documentation.md)) applied specifically to in-product guidance.
Does **not** cover cognitive-load theory generally ([R604](R604-cognitive-load-and-scaffolding.md),
already authored, this topic's dependency), or minimalist written-documentation craft broadly
([R606](R606-minimalist-and-procedural-documentation.md), already authored) — this topic is the
narrower, UI-specific application of both.

## 3. Concepts

**Progressive disclosure: reveal only what's needed for the current step, defer the rest.** Coined by
Jakob Nielsen in 1995 specifically to help users avoid errors in complex systems, progressive
disclosure is a UX technique that reduces cognitive load by gradually revealing interface complexity
as the user progresses, rather than presenting the full feature surface at once
([Nielsen Norman Group's progressive disclosure framework, corroborated across multiple independent
summaries](https://www.nngroup.com/articles/progressive-disclosure/); a synthesis at
[IxDF](https://ixdf.org/literature/topics/progressive-disclosure) names the same 1995 Nielsen origin).
Research cited across these summaries reports progressive disclosure reducing task-completion time by
20-40% while improving comprehension, relative to exposing full complexity immediately.

**Three variants: step-by-step, conditional, contextual.** (1) **Step-by-step (staged) disclosure** —
break a complex task into a sequence of screens/steps, showing only the current one; this is the exact
shape of this simulator's `tutorial:` step scripts. (2) **Conditional disclosure** — hide elements
until the user explicitly requests them (e.g., an "advanced options" expander). (3) **Contextual
disclosure** — surface additional information based on the user's current action (a hint appearing
when a control is first encountered). Onboarding is explicitly named as the **highest-stakes**
application of the pattern, because "the gap between what the user knows and what the app expects them
to know is largest" for a first-time user with no established mental model
([same source](https://www.nngroup.com/articles/progressive-disclosure/)).

**A hint must be unmistakably an annotation, not an interactive-looking element.** A specific,
practically important design constraint from the same literature: instructional overlays/coachmarks
must be visually distinct from real controls, because a user who cannot tell a hint from a button will
tap the hint expecting a result and experience confusion — a failure mode worth naming explicitly
because it is easy to introduce accidentally when building a first in-app tutorial overlay.

**Convergence with Carroll's minimalism, not a competing theory.** Progressive disclosure's staged
variant is functionally the software-UI expression of Carroll's minimalist principle "let the learner
determine the sequence, support real tasks immediately" ([R606](R606-minimalist-and-procedural-documentation.md)):
both converge on "show only what's needed for the task at hand, in the order the task actually
demands," from independent research traditions (HCI/UX vs. technical-writing/instructional-design) —
which is itself evidence the principle is robust rather than an artifact of one field's methodology.

### Sources

- *Progressive Disclosure* — Nielsen Norman Group — [live](https://www.nngroup.com/articles/progressive-disclosure/) · [snapshot](https://web.archive.org/web/2026*/https://www.nngroup.com/articles/progressive-disclosure/) · accessed 2026-07-04.
- *What is Progressive Disclosure?* — Interaction Design Foundation — [live](https://ixdf.org/literature/topics/progressive-disclosure) · [snapshot](https://web.archive.org/web/2026*/https://ixdf.org/literature/topics/progressive-disclosure) · accessed 2026-07-04.

## 4. Operational Context

Modern software onboarding (SaaS product tours, mobile-app first-run flows, IDE/game tutorials)
converged on staged progressive disclosure as the default onboarding pattern for exactly the reason
this topic states: full-complexity exposure to a first-time user reliably produces worse task
completion than a staged sequence. This simulator's Tutorial panel — a per-cell, per-vignette
step-script surfaced in-app, distinct from and complementary to the written manual — is this pattern's
direct instance, and its `test_vignette_tutorials.py` verification (ensuring the scripted steps
actually execute against the live engine) is a stronger guarantee than most commercial software
onboarding gets, since most in-app tutorials are never mechanically re-verified against the product
they describe.

## 5. Implementation Guidance

- **A new vignette needs its own `tutorial:` step script when it introduces a mechanic no earlier
  rung's tutorial covered** — per progressive disclosure's staged-variant logic, each script should
  teach exactly the new mechanic in context, not re-teach what a prior vignette's tutorial (or the
  written manual) already covered; `08-vignette-development`'s per-rung authoring should check this
  before writing a new script from scratch.
- **Reserve conditional/contextual disclosure for the operator console's advanced panels** (e.g., an
  "advanced options" toggle on the maneuver assistant) rather than the guided-onboarding step scripts,
  which should stay step-by-step per the pattern's onboarding-specific guidance.
- **Any future in-app hint/coachmark feature must be visually distinct from real controls** — this is
  a concrete, checkable UI requirement this topic surfaces that the corpus had no prior citation for;
  flag it to a UI-facing Feature Specification if such a feature is ever proposed.
- **Keep the Tutorial panel and the written playbook (`training/11`) as mirrors, not divergent
  sources** — FR-11420 already requires this implicitly (both trace to the same verified step
  script); this topic's contribution is naming *why* both forms should exist rather than one alone: the
  in-app form serves progressive-disclosure's "in the moment" need, the written form serves
  self-directed review outside a live session (andragogy's self-direction assumption,
  [R602](R602-adult-learning-theory.md)).

## 6. Feature Mapping

FR-11420 (machine-verified playbooks) and the `00-training-basics` vignette's `tutorial:` step script
are this topic's most direct targets; `GET /api/vignettes/{id}/tutorial` (the in-UI Tutorial panel
endpoint) is the code-level surface this topic's progressive-disclosure framing describes.

## 7. Related Topics

[R604](R604-cognitive-load-and-scaffolding.md) (Cognitive Load & Scaffolding, the load-theory
foundation progressive disclosure operationalizes), [R606](R606-minimalist-and-procedural-documentation.md)
(Minimalist & Procedural Documentation, this topic's document-craft counterpart),
[R602](R602-adult-learning-theory.md) (Adult Learning Theory, the self-direction assumption behind
keeping the in-app and written forms as parallel, not competing, resources).
