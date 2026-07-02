# Tier R400 — Research Methods

[↑ Encyclopedia index](INDEX.md)

Justifies assessment/validation work (DOM-002, DOM-005). 13 topics.

| ID | Title | Scope (one line) | Depends on | Status |
|---|---|---|---|---|
| [R401](R401-experimental-design-and-controls.md) | Experimental Design and Controls | Isolating an effect by holding other variables constant. | — | ✅ |
| [R402](R402-hypotheses-and-variables.md) | Hypotheses and Variables | Stating falsifiable predictions; independent/dependent/confound variables. | [R401](R401-experimental-design-and-controls.md) | ✅ |
| [R403](R403-statistics-foundations.md) | Statistics Foundations | Descriptive/inferential statistics needed to read DOM-002 outputs. | — | ✅ |
| [R404](R404-measurement-theory.md) | Measurement Theory | Scales of measurement, reliability vs. validity. | [R403](R403-statistics-foundations.md) | ✅ |
| [R405](R405-uncertainty-analysis.md) | Uncertainty Analysis | Propagating and reporting uncertainty in a derived metric. | [R403](R403-statistics-foundations.md) | ✅ |
| [R406](R406-modeling-practices.md) | Modeling Practices | Building and documenting a model so its assumptions are auditable. | — | ✅ |
| [R407](R407-monte-carlo-methods.md) | Monte Carlo Methods | Repeated seeded simulation to characterize outcome distributions. | [R403](R403-statistics-foundations.md), [R406](R406-modeling-practices.md) | ✅ |
| [R408](R408-sensitivity-analysis.md) | Sensitivity Analysis | Varying one input to see how much it moves an outcome. | [R407](R407-monte-carlo-methods.md) | ✅ |
| [R409](R409-verification.md) | Verification | Confirming a model matches its own specification. | [R406](R406-modeling-practices.md) | 🚧 *(no §2 Scope; uncited)* |
| [R410](R410-validation.md) | Validation | Confirming a model/instrument matches the real-world phenomenon it represents. | [R409](R409-verification.md) | 🚧 *(no §2 Scope; uncited)* |
| [R411](R411-human-subjects-research.md) | Human Subjects Research | Ethics, consent, IRB-adjacent considerations for trainee data. | [R401](R401-experimental-design-and-controls.md) | 🚧 *(no §2 Scope; uncited)* |
| [R412](R412-survey-and-assessment-instrument-design.md) | Survey and Assessment Instrument Design | Building a rubric/survey that measures what it claims to. | [R404](R404-measurement-theory.md), [R410](R410-validation.md) | 🚧 *(no §2 Scope; uncited)* |
| [R413](R413-data-analysis-and-reporting.md) | Data Analysis and Reporting | Turning collected exercise data into a defensible finding. | [R403](R403-statistics-foundations.md), [R412](R412-survey-and-assessment-instrument-design.md) | 🚧 *(no §2 Scope; uncited)* |

**Status: incomplete, not done.** All 13 topics have substantive content but **none has the
mandatory §2 Scope section** (MSTR-007 §4.2) and **none is cited** per `docs/research/10-sources-
and-methodology.md`'s corpus-wide convention — zero `### Sources` subsections, zero URLs, zero YAML
frontmatter. Grounded in DOM-002 (Assessment Framework — six measurement dimensions as the
dependent-variable/instrument-design substrate) and DOM-005 (Validation Framework — the
verification/validation distinction and the `AUDIT-2026-06-UI-TTC.md` §2 worked validation
precedent) — but that grounding doesn't substitute for the source citations the methodology
requires for this tier's statistical/methodological claims.
