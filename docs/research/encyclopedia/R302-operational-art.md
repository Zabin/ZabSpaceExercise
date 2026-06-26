# R302 — Operational Art

> **Document ID:** R302
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** R301
> **Referenced By:** R305, R309, R310
> **Produces:** the vocabulary for the tactics↔strategy connective layer a vignette's objectives should reflect
> **Feature Mapping:** vignette authoring (`docs/scenarios/`)
> **Related Topics:** R301 (Campaign Design), R309 (Center of Gravity Analysis), R310 (Effects-Based
> Operations), R305 (Mission Analysis)

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

A single vignette's objectives (e.g. "establish custody on Red asset X," "maintain command uplink to
Blue asset Y") are tactical-level statements — operational art is the doctrinal layer explaining
*why* a particular tactical objective was chosen to serve a strategic end. This topic gives a
vignette author the vocabulary to make that linkage explicit rather than choosing tactical objectives
arbitrarily.

## 2. Concepts

**Operational art is the connective tissue between individual tactical actions and the strategic
objective they're meant to serve.** It answers "why this sequence of tactical objectives, and not
some other sequence, advances the strategic goal" — distinct from tactics (how to execute a given
action, the engine-mechanics layer this simulator already models in detail) and strategy (what
overall end is sought, R312).

**Lines of operation and lines of effort.** A line of operation connects actions in physical/
geographic space toward an objective (e.g. a sequence of access windows building toward sustained
custody of a regime); a line of effort connects actions toward a conceptual objective not tied to
geography (e.g. "degrade adversary SDA confidence" pursued through a mix of EW, cyber, and deception
across multiple assets). A vignette's objective set can be read as instantiating one or more lines —
useful vocabulary for DOM-009's doctrine-translation step when justifying why a vignette's objectives
were chosen as they were.

**Operational reach and culmination.** A force's operational reach is the distance/duration over
which it can sustain effective operations before culminating (running out of resources/momentum) —
in this simulator's terms, this maps to Δv/SoC/ammo/storage budgets (R111, R112, R118's
`PRIORITY_COST`) imposing a real culmination point on a sustained operation, not an abstract notion.

**Tempo.** The rate of operations relative to the adversary's ability to respond — directly related
to R208's OODA-loop tightness, but at the operational rather than individual-decision level: a
campaign-level tempo advantage means consistently outpacing Red's adaptation across many tactical
exchanges, not just one.

## 3. Operational Context

Real operational-level planning explicitly works this tactics-strategy connective layer (the
"operational level of war" in joint doctrine) — a campaign plan justifies each operation's objectives
in terms of lines of operation/effort toward the campaign's end state, and operational reach/tempo
are standard planning considerations precisely because resource exhaustion and pace, not just tactical
skill, decide real campaigns.

## 4. Implementation Guidance

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

## 5. Feature Mapping

Vignette authoring (`docs/scenarios/`) is the direct consumer; no dedicated FS exists yet for
operational-art tooling.

## 6. Related Topics

R301 (Campaign Design, the multi-operation context), R309 (Center of Gravity), R310 (Effects-Based
Operations), R305 (Mission Analysis, the intent-translation step that produces tactical objectives
from operational-art reasoning).
