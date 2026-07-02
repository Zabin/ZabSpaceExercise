# R205 — Cognitive Psychology Foundations

> **Document ID:** R205
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** —
> **Referenced By:** [R206](R206-bounded-rationality.md), [R207](R207-cognitive-biases.md), [R208](R208-ooda-loops.md), DOM-007
> **Produces:** the perception/memory/attention vocabulary underlying [R206](R206-bounded-rationality.md)/[R207](R207-cognitive-biases.md)/DOM-007
> **Feature Mapping:** FS-101 (Mission Planning), DOM-007 (Human Factors)
> **Related Topics:** [R206](R206-bounded-rationality.md) (Bounded Rationality), [R207](R207-cognitive-biases.md) (Cognitive Biases), DOM-007 (Human Factors
> Framework — the UI-facing consumer of this topic's perception/attention vocabulary)

> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 1

[↑ Tier R200 index](R200-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

The operator console (fleet rail, command menu, 2D map, telemetry graphs) is a perception and
attention-management interface, not just a data display — how an operator notices a degraded
station, an expiring access window, or a confidence band crossing the weapons-quality threshold is a
cognitive-psychology question before it is a UI-design question. This topic gives the implementer
the substrate vocabulary (perception, attention, working memory) that [R206](R206-bounded-rationality.md)/[R207](R207-cognitive-biases.md)/DOM-007 build on.

## 2. Scope

Covers the perception/attention/working-memory substrate (selective attention, change blindness,
recognition-vs-recall, cognitive load) that operator-console design must respect. Does **not** cover
the decision-making layer built on this substrate ([R206](R206-bounded-rationality.md), Bounded
Rationality), systematic judgment distortions ([R207](R207-cognitive-biases.md), Cognitive Biases),
or UI-specific implementation beyond the console (DOM-007, the direct consumer).

## 3. Concepts

**Selective attention and the limits of working memory.** Humans can attend to and hold only a
small number of items in working memory at once
([Miller, G. A., "The Magical Number Seven, Plus or Minus Two," *Psychological Review* 63, 1956](https://pubmed.ncbi.nlm.nih.gov/13310704/)
([Wayback](https://web.archive.org/web/2026/https://pubmed.ncbi.nlm.nih.gov/13310704/))). A fleet rail showing many satellites with simultaneous alarm badges, countdowns, and
SoC/storage indicators is competing for this scarce resource — every additional always-visible
indicator has a real attentional cost, not a free one.

**Change blindness and the need for salient alerting.** Humans reliably fail to notice gradual or
off-focus changes (a station quietly dropping out of the scene, a confidence value slowly decaying)
unless a change is made salient through a deliberate cue (the alarm badge, the deep-link). This is
the cognitive justification for the engine surfacing explicit alarms rather than relying on an
operator to notice a state change by continuously re-scanning a dashboard.

**Recognition vs. recall.** Recognition (seeing an option and judging it familiar/correct) is
cognitively cheaper than recall (generating the option from memory). A command menu listing
available actions with live dry-run preview (per [R103](R103-satellite-command-and-control.md)/[R120](R120-access-window-and-geometry-planning.md)'s "see before you commit" pattern)
leans on recognition; a hypothetical command-line-only interface would force recall, a strictly
higher cognitive load for no operational benefit.

**Cognitive load and dual-task interference.** Splitting attention across two demanding mental
tasks (e.g., a complex maneuver-planning calculation alongside real-time alarm monitoring) degrades
performance on both relative to doing them separately — relevant to why time-pressure/urgency design
in vignettes (DOM-001's progression) should be a deliberate pedagogical lever, not an unintentional
side effect of cluttered UI.

### Sources

- *Miller, G. A., "The Magical Number Seven, Plus or Minus Two: Some Limits on Our Capacity for
  Processing Information," Psychological Review* 63 (1956) — [live](https://pubmed.ncbi.nlm.nih.gov/13310704/)
  · [snapshot](https://web.archive.org/web/2026/https://pubmed.ncbi.nlm.nih.gov/13310704/)
  · accessed 2026-07-02.

## 4. Operational Context

Real operator consoles (mission control, SOC dashboards) are explicitly designed around these same
constraints — alarm philosophy (what triggers a visible alert, how many can be active without
desensitizing the operator), display hierarchy (what's always visible vs. drill-down), and
recognition-over-recall interaction patterns are standard human-factors engineering practice in
safety-critical operations, not space-sim-specific inventions.

## 5. Implementation Guidance

- **A new always-visible UI indicator must be justified against working-memory limits** — adding it
  should mean removing or consolidating something else, or demonstrating it occupies a genuinely
  low-attention channel (e.g. peripheral color, not another number to read).
- **A new alarm/alert type should be designed for salience (the change-blindness problem), not just
  correctness** — a technically-correct indicator that blends into a busy display has, from a human-
  factors standpoint, failed even if its underlying data is right.
- **Prefer recognition-based interaction (menus, dry-run previews, pre-disabled buttons) over
  recall-based interaction for any new command surface** — consistent with the existing command-menu
  pattern; a feature requiring an operator to remember a command's exact syntax/parameters from
  scratch reintroduces a real cognitive cost the rest of the console avoids.

## 6. Feature Mapping

FS-101 (Mission Planning) and DOM-007 (Human Factors Framework) are the direct consumers — any new
console panel should be checked against this topic's attention/working-memory constraints before
being added.

## 7. Related Topics

[R206](R206-bounded-rationality.md) (Bounded Rationality, the decision-making layer built on this perceptual substrate), [R207](R207-cognitive-biases.md)
(Cognitive Biases, systematic perceptual/judgment distortions), DOM-007 (Human Factors Framework, the
UI-facing application of this topic).
