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
| [R409](R409-verification.md) | Verification | Confirming a model matches its own specification. | [R406](R406-modeling-practices.md) | ✅ |
| [R410](R410-validation.md) | Validation | Confirming a model/instrument matches the real-world phenomenon it represents. | [R409](R409-verification.md) | ✅ |
| [R411](R411-human-subjects-research.md) | Human Subjects Research | Ethics, consent, IRB-adjacent considerations for trainee data. | [R401](R401-experimental-design-and-controls.md) | ✅ |
| [R412](R412-survey-and-assessment-instrument-design.md) | Survey and Assessment Instrument Design | Building a rubric/survey that measures what it claims to. | [R404](R404-measurement-theory.md), [R410](R410-validation.md) | ✅ |
| [R413](R413-data-analysis-and-reporting.md) | Data Analysis and Reporting | Turning collected exercise data into a defensible finding. | [R403](R403-statistics-foundations.md), [R412](R412-survey-and-assessment-instrument-design.md) | ✅ |

**Status: 13 of 13 topics complete — tier fully closed (2026-07-02), GAP-13 remediation done.**
Every topic now carries the mandatory §2 Scope section (MSTR-007 §4.2) and is cited per
`docs/research/10-sources-and-methodology.md`'s convention — inline citations at every substantive
statistical/methodological claim site, a `### Sources` subsection on every `##` section (live URL +
Wayback snapshot + accessed date, or a cited `docs/AUDIT-2026-06-UI-TTC.md`/`spacesim/engine/rng.py`/
`spacesim/tests/test_determinism.py` file:line for claims about this project's own practice). Tier A
sources include NIST Technical Note 1297 (uncertainty), the NIST/SEMATECH e-Handbook of Statistical
Methods, DoDI 5000.61 and Sargent's simulation V&V framework (modeling/verification/validation),
the Belmont Report and 45 CFR 46 (human subjects), and this project's own determinism precedent
(Monte Carlo); Tier A/B foundational-methods sources include Fisher (1935), Campbell & Stanley
(1963), Popper (falsifiability), Stevens (1946, scales of measurement), Cronbach (1951, internal
consistency), Metropolis & Ulam (1949, Monte Carlo), Saltelli et al. (2008, sensitivity analysis),
Messick (1995, construct-irrelevant variance), Boehm (1981, verification/validation), Likert (1932),
Crowne & Marlowe (1960, social desirability bias), the ASA Ethical Guidelines for Statistical
Practice, and Tufte (1983, graphical integrity/Lie Factor). Grounded in DOM-002 (Assessment Framework
— six measurement dimensions as the dependent-variable/instrument-design substrate) and DOM-005
(Validation Framework — the verification/validation distinction and the `AUDIT-2026-06-UI-TTC.md` §2
worked validation precedent, cited directly at [R410](R410-validation.md)). Per
`docs/FUTURE-WORK.md` §13 (Recommendation R1), R500 (Future Operations) closed first and R400 second,
completing GAP-13 remediation across both tiers. Last reviewed across the tier: 2026-07-02.
