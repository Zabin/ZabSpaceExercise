# R501 — Human-AI Teaming

> **Document ID:** R501
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** —
> **Referenced By:** [R502](R502-autonomy-in-space-operations.md), [R503](R503-ai-decision-support.md), [R509](R509-ai-integration-patterns.md)
> **Produces:** the vocabulary for how a human operator and an AI advisor would share a decision loop, framing DOM-008 §4's "advisor not decider" constraint
> **Feature Mapping:** any future in-world AI decision-support feature (🅿️ pending authorization per DOM-008 §4)
> **Related Topics:** [R210](R210-decision-support-systems.md) (Decision Support Systems — the 4-level spectrum this topic's teaming
> models map onto), DOM-008 (AI Integration Framework — §4's advisor-only constraint), [R503](R503-ai-decision-support.md) (AI
> Decision Support)
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 3 (Tier B peer-reviewed human-factors literature — see §3, §4 Sources)

[↑ Tier R500 index](R500-index.md) · [Encyclopedia index](INDEX.md)

**DOM-008 §6 tag:** in-world AI (a future trainee-facing advisor), with implications for coding-agent
practice noted in §5 below.

## 1. Purpose

DOM-008 §4 establishes "advisor, not decider" as the standing constraint on any future in-world AI
assistance to a trainee. This topic supplies the human-AI teaming vocabulary that constraint is a
specific instance of — the general models for how decision authority and information flow are
divided between a human and an AI system sharing a task, so a future feature proposal can be checked
against the full range of teaming models, not just the binary "automated or not."

## 2. Scope

Covers: the general vocabulary for classifying how automation/AI participates in a human's task
(levels-of-automation taxonomy, over-trust/under-trust failure modes, shared mental models, workload
allocation) as it applies to DOM-008 §4's "advisor, not decider" constraint on a future in-world AI.
Does **not** cover: the specific degrees of autonomy applicable to bus/payload commanding
([R502](R502-autonomy-in-space-operations.md)'s job), the concrete mechanics of what an advisor
surfaces and how ([R503](R503-ai-decision-support.md)'s job), or DOM-008 §4 itself, which this topic
grounds but does not restate in full. Also does not cover autonomous *planning* algorithms
([R507](R507-autonomous-planning-systems.md)) — this topic is about the human-AI relationship, not
the AI's internal reasoning method.

## 3. Concepts

**Teaming models range from tool to teammate to delegate.** This maps onto the widely-cited
function-based automation taxonomy of
[Parasuraman, Sheridan & Wickens (2000)](https://doi.org/10.1109/3468.844354), which classifies
automation across four function types — information acquisition, information analysis, decision and
action selection, and action implementation — and, within each, a 10-point level scale from "the
human does everything" (level 1) to "the computer acts autonomously, ignoring the human" (level 10).
A tool-level AI only responds to explicit queries with no initiative (low levels on all four
functions); a teammate-level AI proactively surfaces relevant information or analysis without being
asked but never selects or executes an action (higher levels on acquisition/analysis, low levels on
decision/action); a delegate-level AI takes autonomous action within a bounded scope (high levels on
decision and action implementation). DOM-008 §4's "advisor, not decider" line places any future
in-world AI assistance at or below the teammate level on the *decision and action selection* function
specifically, explicitly ruling out delegate-level autonomous decision-making for the trainee even
if the AI is teammate- or delegate-level on the acquisition/analysis functions.

**Trust calibration: neither over-trusting nor under-trusting the AI partner.**
[Parasuraman & Riley (1997)](https://doi.org/10.1518/001872097778543886) name and distinguish the two
failure directions: *misuse* is over-reliance on automation leading to monitoring failures or
decision biases even when the automation is wrong, and *disuse* is neglect or under-utilization of a
genuinely reliable automated aid (commonly driven by prior false-alarm experience). The specific
misuse mechanism most documented in aviation is **automation bias** — the tendency to use an
automated recommendation as a heuristic replacement for independently seeking and processing
information, rather than as one input to be weighed
([Mosier & Skitka, 1996](https://doi.org/10.1177/154193129604000413);
[Mosier & Skitka, 1999](https://doi.org/10.1177/154193129904300346)). Mosier & Skitka's cockpit
studies found pilots who reported an internalized sense of personal accountability for the outcome
were significantly more likely to independently cross-check automated outputs against other cues and
less likely to commit automation-induced errors than pilots who treated the automated output as
already-verified. Calibrated trust requires the AI's confidence/uncertainty to be genuinely legible
to the operator, not just its bottom-line recommendation — an interface that presents a
recommendation without its basis or confidence invites exactly the heuristic-replacement pattern
Mosier & Skitka document.

**Shared mental models.** Effective human-AI teaming requires the human to have an accurate model of
what the AI does and doesn't know, and — to the extent the AI models the human at all — vice versa.
The team-cognition literature (originating in human-human team research:
[Cannon-Bowers, Salas & Converse, 1993](https://www.researchgate.net/publication/226781970_Shared_Mental_Models))
holds that shared or overlapping cognitive representations of the task, roles, and available
information let teammates predict each other's actions and interpret each other's outputs correctly
without constant explicit negotiation; a mismatch degrades exactly that predictive ability. A future
in-world advisor that draws on different information than the trainee currently has access to (e.g.
ground truth the trainee's fog-of-war view doesn't show) would violate this requirement and create a
dangerous shared-mental-model mismatch, distinct from and in addition to DOM-008 §4's decision-
authority constraint.

**Workload and attention allocation.** A well-designed human-AI team allocates the AI to tasks that
reduce the human's workload at exactly the moments cognitive load is highest, rather than adding a
new information stream to monitor at all times — a future advisor feature should be evaluated against
whether it reduces or adds to the trainee's attentional burden, consistent with the working-memory
capacity limits [R205](R205-cognitive-psychology-foundations.md) already documents for this corpus.

### Sources

- *Parasuraman, R., Sheridan, T.B. & Wickens, C.D. (2000). A Model for Types and Levels of Human
  Interaction with Automation. IEEE Transactions on Systems, Man, and Cybernetics—Part A, 30(3),
  286–297.* — [live (DOI)](https://doi.org/10.1109/3468.844354)
  · [snapshot](https://web.archive.org/web/2026*/https://doi.org/10.1109/3468.844354)
  · accessed 2026-07-02.
- *Parasuraman, R. & Riley, V. (1997). Humans and Automation: Use, Misuse, Disuse, Abuse. Human
  Factors, 39(2), 230–253.* — [live (DOI)](https://doi.org/10.1518/001872097778543886)
  · [snapshot](https://web.archive.org/web/2026*/https://doi.org/10.1518/001872097778543886)
  · accessed 2026-07-02.
- *Mosier, K.L. & Skitka, L.J. (1996). Automation Bias, Accountability, and Verification Behaviors.
  Proceedings of the Human Factors and Ergonomics Society Annual Meeting, 40(4), 204–208.* —
  [live (DOI)](https://doi.org/10.1177/154193129604000413)
  · [snapshot](https://web.archive.org/web/2026*/https://doi.org/10.1177/154193129604000413)
  · accessed 2026-07-02.
- *Mosier, K.L. & Skitka, L.J. (1999). Automation Use and Automation Bias. Proceedings of the Human
  Factors and Ergonomics Society Annual Meeting, 43(3), 344–348.* —
  [live (DOI)](https://doi.org/10.1177/154193129904300346)
  · [snapshot](https://web.archive.org/web/2026*/https://doi.org/10.1177/154193129904300346)
  · accessed 2026-07-02.
- *Cannon-Bowers, J.A., Salas, E. & Converse, S. (1993). Shared Mental Models in Expert Team
  Decision Making.* In N.J. Castellan Jr. (Ed.), Individual and Group Decision Making. —
  [live](https://www.researchgate.net/publication/226781970_Shared_Mental_Models)
  · [snapshot](https://web.archive.org/web/2026*/https://www.researchgate.net/publication/226781970_Shared_Mental_Models)
  · accessed 2026-07-02.

## 4. Operational Context

Human-AI teaming research — running from cockpit automation-bias studies through the broader
levels-of-automation and trust-calibration literature cited in §3 — is the active research base most
directly relevant to any future in-world AI assistance in this simulator, and has documented both
classes of failure (misuse/automation bias, disuse) in enough operational depth that any future
advisor-feature design should treat avoiding both as a first-class design requirement, not an
afterthought. The aviation-cockpit setting these studies were conducted in is a reasonable analog for
a White/Blue/Red operator console: a time-pressured operator monitoring several automated subsystems
while retaining decision authority is structurally similar to a Blue operator monitoring bus/payload
telemetry and custody tracks while retaining engagement/maneuver authority.

### Sources

Uses the same sources cited inline in §3 (Parasuraman & Riley 1997; Mosier & Skitka 1996, 1999); no
additional sources introduced in this section.

## 5. Implementation Guidance

- **Any future in-world AI decision-support feature must be designed at or below the
  "teammate" level per DOM-008 §4** — surfacing information or flagging a consideration, never taking
  or recommending a single "decide this for you" action (the Parasuraman/Sheridan/Wickens
  decision-and-action-selection function, §3, is where the ceiling applies specifically).
- **A future advisor's information access must be restricted to exactly the same fog-of-war view the
  trainee has** (per the shared-mental-model concern in §3, and DOM-008 §3's parallel constraint on
  Red presets) — an advisor with god-view-derived insight breaks the shared mental model and
  effectively decides for the trainee by surfacing otherwise-unavailable certainty.
- **Any recommendation the advisor surfaces must expose its basis/confidence, not just a bottom-line
  suggestion** — per Mosier & Skitka's accountability finding (§3), an opaque recommendation invites
  the automation-bias heuristic-replacement pattern regardless of how the advisor is otherwise scoped.
- **Evaluate any future advisor feature's effect on trainee workload explicitly** (does it reduce
  attentional burden at high-load moments, or add a new stream to monitor) before building it — per
  the workload-allocation concern in §3.
- **Coding-agent note (DOM-008 §5):** an agent implementing any future advisor feature is doing
  coding-agent work (b) that builds in-world AI (a); the agent must not relax the advisor's
  information-access constraint "to make the demo more impressive."

## 6. Feature Mapping

Any future in-world AI decision-support feature is the direct consumer; none exists yet (🅿️ pending
authorization).

## 7. Related Topics

[R210](R210-decision-support-systems.md) (Decision Support Systems, the 4-level spectrum),
[R205](R205-cognitive-psychology-foundations.md) (working-memory limits underlying the workload
concern), DOM-008 (AI Integration Framework §4), [R503](R503-ai-decision-support.md)
(AI Decision Support, the direct downstream elaboration), [R502](R502-autonomy-in-space-operations.md)
(the bus/payload-specific autonomy-degree vocabulary this topic explicitly defers to).
