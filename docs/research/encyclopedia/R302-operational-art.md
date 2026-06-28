# R302 — Operational Art

> **Document ID:** R302
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R301](R301-campaign-design.md)
> **Referenced By:** [R305](R305-mission-analysis.md), [R309](R309-center-of-gravity-analysis.md), [R310](R310-effects-based-operations.md), [R316](R316-joint-and-combined-operations.md)
> **Produces:** the vocabulary for the tactics↔strategy connective layer a vignette's objectives should reflect
> **Feature Mapping:** vignette authoring (`docs/scenarios/`)
> **Related Topics:** [R301](R301-campaign-design.md) (Campaign Design), [R309](R309-center-of-gravity-analysis.md) (Center of Gravity Analysis), [R310](R310-effects-based-operations.md) (Effects-Based
> Operations), [R305](R305-mission-analysis.md) (Mission Analysis)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 1

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

A single vignette's objectives (e.g. "establish custody on Red asset X," "maintain command uplink to
Blue asset Y") are tactical-level statements — operational art is the doctrinal layer explaining
*why* a particular tactical objective was chosen to serve a strategic end. This topic gives a
vignette author the vocabulary to make that linkage explicit rather than choosing tactical objectives
arbitrarily.

## 2. Scope

Covers: the operational level of war as the connective layer between tactics and strategy, lines of
operation/effort, and operational reach/tempo/culmination as planning considerations. Does **not**
cover: multi-operation campaign sequencing (that is [R301](R301-campaign-design.md)) or identifying
*what* the operation should be aimed at (that is [R309](R309-center-of-gravity-analysis.md), Center
of Gravity Analysis).

## 3. Concepts

**Operational art is the connective tissue between individual tactical actions and the strategic
objective they're meant to serve.** Joint doctrine defines operational art as the cognitive approach
by commanders and staffs — supported by their skill, knowledge, experience, creativity, and
judgment — to develop strategies, campaigns, and operations to organize and employ military forces by
integrating ends, ways, and means ([JP 5-0, *Joint Planning*](https://www.jcs.mil/Doctrine/Joint-Doctrine-Pubs/5-0-Planning-Series/),
validated 2020-12-01, §III.1). It answers "why this sequence of tactical objectives, and not some
other sequence, advances the strategic goal" — distinct from tactics (how to execute a given action,
the engine-mechanics layer this simulator already models in detail) and strategy (what overall end
is sought, [R312](R312-space-strategy.md)).

**Lines of operation and lines of effort.** JP 5-0 defines a *line of operation* as a line that
defines the directional orientation of a force in time and space in relation to the enemy, linking
the force to its base of operations and objectives, and a *line of effort* as a line that links
multiple tasks using the logic of purpose rather than geographic reference to focus efforts toward
establishing operational and strategic conditions ([JP 5-0](https://www.jcs.mil/Doctrine/Joint-Doctrine-Pubs/5-0-Planning-Series/)
§IV.3). A vignette's objective set can be read as instantiating one or more lines — e.g. a sequence
of access windows building toward sustained custody of a regime is a line of operation; "degrade
adversary SDA confidence" pursued through a mix of EW, cyber, and deception across multiple assets is
a line of effort — useful vocabulary for DOM-009's doctrine-translation step when justifying why a
vignette's objectives were chosen as they were.

**Operational reach and culmination.** JP 5-0 defines *operational reach* as the distance and
duration across which a force can successfully employ military capabilities, and a *culminating
point* as the point at which a force no longer has the capability to continue its form of operations,
offensive or defensive — in this simulator's terms, this maps to Δv/SoC/ammo/storage budgets
([R111](R111-power-and-thermal-operations.md), [R112](R112-propulsion-and-maneuver-planning.md),
[R118](R118-space-surveillance-networks.md)'s `PRIORITY_COST`) imposing a real culmination point on
a sustained operation, not an abstract notion.

**Tempo.** The rate of operations relative to the adversary's ability to respond — directly related
to [R208](R208-ooda-loops.md)'s OODA-loop tightness, but at the operational rather than
individual-decision level: a campaign-level tempo advantage means consistently outpacing Red's
adaptation across many tactical exchanges, not just one.

### Sources

- *JP 5-0, Joint Planning* (Joint Chiefs of Staff, validated 2020-12-01) — [live](https://www.jcs.mil/Doctrine/Joint-Doctrine-Pubs/5-0-Planning-Series/)
  · [snapshot](https://web.archive.org/web/2026/https://www.jcs.mil/Doctrine/Joint-Doctrine-Pubs/5-0-Planning-Series/)
  · accessed 2026-06-27.

## 4. Operational Context

Real operational-level planning explicitly works this tactics-strategy connective layer (the
"operational level of war" in joint doctrine) — a campaign plan justifies each operation's objectives
in terms of lines of operation/effort toward the campaign's end state, and operational reach/tempo
are standard planning considerations precisely because resource exhaustion and pace, not just tactical
skill, decide real campaigns.

## 5. Implementation Guidance

- **A vignette's `intro_brief` mission statement should be traceable to a line of operation/effort**,
  even informally — this gives DOM-009's doctrine-translation step a concrete artifact to check, and
  gives a White Cell facilitator language for explaining to trainees *why* a vignette's objectives
  are shaped the way they are, beyond "these are the win conditions."
- **A vignette's resource budget (fleet size, Δv allowance, SSN dispersion preset) should be tuned to
  produce a meaningful culmination point relative to the vignette's intended duration** — an
  unlimited-resource vignette removes the operational-reach lesson entirely, which is a deliberate
  design choice only when explicitly intended (e.g. an onboarding vignette where resource scarcity
  would distract from the mechanic being taught).
- **Don't conflate tempo (operational-level pacing across many exchanges) with the engine's
  time-acceleration control** — White Cell's clock speed (DOM-003 §5) is a facilitation tool, not a
  simulated tempo advantage; a tempo *lesson* should come from the scenario's resource/access design,
  not from literally running the clock faster for one side.

## 6. Feature Mapping

Vignette authoring (`docs/scenarios/`) is the direct consumer; no dedicated FS exists yet for
operational-art tooling.

## 7. Related Topics

[R301](R301-campaign-design.md) (Campaign Design, the multi-operation context), [R309](R309-center-of-gravity-analysis.md) (Center of Gravity), [R310](R310-effects-based-operations.md) (Effects-Based
Operations), [R305](R305-mission-analysis.md) (Mission Analysis, the intent-translation step that produces tactical objectives
from operational-art reasoning).
