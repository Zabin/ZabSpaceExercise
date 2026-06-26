# DOM-009 — Doctrine Development Framework

> **Document ID:** DOM-009
> **Version:** 1.0
> **Status:** 🚧 In progress
> **Dependencies:** MSTR-001, MSTR-003
> **Referenced By:** DOM-003, DOM-006, DOM-008, FS-103, FS-104
> **Produces:** the process by which research/doctrine content becomes vignette content (threat pictures, ROE, effect parameters)
> **Feature Mapping:** FS-103 (Custody Management), FS-104 (SDA Tasking)
> **Related Topics:** [`docs/research/01-doctrine-western.md`](../research/01-doctrine-western.md),
> [`docs/research/02-doctrine-non-western.md`](../research/02-doctrine-non-western.md), [`docs/research/03-counterspace-taxonomy.md`](../research/03-counterspace-taxonomy.md),
> R301-R312 (Military Analysis tier)

[↑ Docs index](../INDEX.md)

## 1. Purpose

Defines how real-world space doctrine (Western and non-Western counterspace doctrine, the
five-D's taxonomy, legal/ROE norms) becomes specific, playable simulator content — vignette threat
pictures, Red doctrine presets (DOM-008 §3), and ROE defaults — without either (a) flattening
doctrine into an oversimplified game mechanic, or (b) requiring every vignette author to be a
doctrine subject-matter expert from scratch.

## 2. Scope

In scope: the translation process from doctrine documents to vignette/ROE/effect parameters, and
the consistency check that translated content doesn't drift from its doctrinal source over time. Out
of scope: the doctrine content itself (owned by `docs/research/01-03`, `07`, and the R300 tier) and
the engine mechanics the doctrine is translated into (owned by `docs/build-spec/`, `docs/design/`).

## 3. The translation pipeline

```
Doctrine source            (research/01-02: Western/non-Western counterspace doctrine,
                             research/03: five-D's taxonomy, research/07: legal norms/ROE,
                             R301-R312: campaign design, deterrence, escalation, COG, EBO, COA)
        ↓  (DOM-009 translation step)
Doctrinal parameters        (which effect categories a Red posture favors, what ROE thresholds
                             a Blue cell operates under, what custody/SDA assumptions are realistic
                             for a given scenario's dispersion preset)
        ↓
Vignette / Red-preset content (YAML: intro_brief threat picture, ROE block, redai.py preset
                             selection, SSN dispersion preset)
```

**Design rule:** every vignette's threat picture and ROE block should be traceable to *which*
doctrine source(s) informed it (a comment or a `doctrine_basis:` metadata field — candidate
schema addition, see §6) so that a doctrine update (new research, a corrected counterspace taxonomy
entry) has a known set of downstream vignettes to review, rather than requiring a full-library
re-read.

## 4. Translation principles

- **Doctrine informs parameters; it does not become a special case in engine code.** Per MSTR-002
  §2 invariant 6, a new doctrinal posture should be expressible via existing data hooks
  (Red preset parameters, ROE chips, SSN dispersion presets) — if it can't be, that's a signal a
  new *engine primitive* is needed (an Implementation Package, properly specified), not a one-off
  scripted exception.
- **Realism is calibrated, not maximized.** Per MSTR-001 §4, fidelity is "moderate, behind
  interfaces" by design — a vignette's threat picture should be *doctrinally recognizable* to a
  subject-matter expert, not a literal classified-accurate reproduction. DOM-009's translation step
  is where this calibration judgment is made explicit and documented, rather than left as an
  unstated simplification.
- **Legal/ROE norms are load-bearing, not flavor.** `research/07-legal-norms-and-roe.md` already
  maps treaty law (OST), LOAC in space, and the 2022 ASAT-test moratorium to in-sim ROE. DOM-009's
  rule: any new effect category or weapon-class capability must go through this same mapping step
  before it ships in a vignette — a new kinetic option without a corresponding ROE/legal framing is
  a doctrine-development process failure, not just a content gap.

## 5. Doctrine review cadence

Doctrine is not static — counterspace doctrine and legal norms evolve. DOM-009 recommends a
periodic (not necessarily fixed-calendar) review pass: when `docs/research/01-03`/`07` are
substantively revised, a follow-up pass should check whether existing vignette threat
pictures/ROE/Red-preset parameters still reflect the updated doctrine, recording any drift as a
`ROADMAP.md`/`FUTURE-WORK.md` item rather than silently leaving stale content in place.

## 6. Open work

- `doctrine_basis:` as an explicit vignette/Red-preset metadata field is not yet implemented —
  candidate scope item for an FS-103/FS-104-derived Implementation Package, or a small standalone
  vignette-schema package.
- No current cross-reference exists from `redai.py` preset names back to the specific research
  document(s) that informed them; this is the concrete instance of §3's traceability gap.

## 7. Related topics

R301-R312 (Military Analysis tier — campaign design, deterrence, escalation, COG, EBO, COA, the
deeper doctrinal vocabulary this framework's translation step draws on beyond the existing
research/01-03/07 primers), DOM-003 §7 (White Cell's real-time use of Red doctrine presets), DOM-006
§3 (the content-change-class table this framework's outputs fall under when they modify vignette
content).
