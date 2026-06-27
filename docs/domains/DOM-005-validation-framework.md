# DOM-005 — Validation Framework

> **Document ID:** DOM-005
> **Version:** 1.0
> **Status:** ⛔ Planned
> **Dependencies:** MSTR-001, MSTR-002, DOM-002, DOM-004
> **Referenced By:** DOM-002, FS-201, FS-301
> **Produces:** validation criteria consumed by FS-201 and FS-301's Implementation Packages
> **Feature Mapping:** FS-201, FS-301
> **Related Topics:** R409 (verification), R410 (validation), R407 (Monte Carlo), R408 (sensitivity analysis), DOM-002

[↑ Docs index](../INDEX.md)

## 1. Purpose

Distinguishes — and gives a concrete method for closing the gap between — **engine verification**
("did we build the model right," already covered by the existing pytest suite, esp. the
determinism property test) and **model/assessment validation** ("did we build the right model" —
does an in-engine measurement, like DOM-002's custody-quality dimension, actually correspond to the
real-world competency it claims to measure, and does the physics/access model behave like the real
domain it represents closely enough for the training conclusions to transfer).

## 2. Scope

In scope: validation criteria and methods for (a) simulator fidelity claims (does the access-window
model behave plausibly relative to real orbital mechanics) and (b) assessment-instrument validity
(does DOM-002's rubric track real skill). Out of scope: running the actual studies (DOM-004's
research-instrument capability, gated separately) — this document specifies *how* such a study
would be evaluated for soundness, not the study itself.

## 3. Verification is already strong; validation is the gap

The project's existing test discipline (determinism property test, import guard, 470+ pytest tests
incl. `test_power_calibration.py`'s regression pin on baseline SoC) is verification: it confirms the
implemented engine matches its own specification. No equivalent process currently confirms that the
specification itself produces *operationally plausible* behavior or that a derived assessment score
means what it claims to mean. DOM-005 exists to name this gap precisely so future Feature
Specifications (FS-201, FS-301) don't accidentally present verification results as if they were
validation evidence.

## 4. Validation method for fidelity claims

For any "moderate fidelity" claim (MSTR-001 §4) — e.g., the recalibrated power-drain constants from
`AUDIT-2026-06-UI-TTC.md` §2 producing a "gentle 0.79-1.00 SoC cycle... 21% DoD" — the validation
method is: **compare the simulated quantity's behavior against documented real-world reference
values cited in the relevant research encyclopedia topic** (e.g., a future R1xx topic on power
budgeting would cite typical LEO bus depth-of-discharge ranges), and record the comparison as an
explicit table in the topic document or a dedicated validation note, not just as a "looks
reasonable" judgment call. The Jun 2026 audit's power-model fix (`AUDIT-2026-06-UI-TTC.md` §2) is
the existing precedent for this kind of validation reasoning — it should be cited as the worked
example when a future R1xx document needs one.

## 5. Validation method for assessment instruments (DOM-002 rubric)

Three checks, borrowed from standard instrument-validation practice (R410), applied at whatever
scale is actually available (even informally, with a handful of exercise runs, before any
larger-scale study is authorized per DOM-004 §6):

1. **Face validity** — does a subject-matter expert (a real space-operations instructor) agree that
   high scores on a DOM-002 dimension correspond to behavior they'd call competent?
2. **Internal consistency** — across repeated runs of the same vignette by cells of presumably
   similar skill, do the dimension scores cluster sensibly rather than swinging on noise (custody
   confidence decay randomness, Red AI variance)?
3. **Sensitivity to manipulation** — if a vignette is deliberately made harder along one axis (e.g.
   tighter ROE, faster custody decay), does the relevant DOM-002 dimension move in the expected
   direction? (This is literally R408's sensitivity-analysis method applied to the instrument
   itself.)

## 6. Monte Carlo as the validation workhorse

Because the engine is deterministic per-seed (MSTR-002 §2 invariant 1), validation studies that
need to characterize *typical* behavior (not one run) should drive the engine across many seeds —
this is R407's Monte Carlo method applied externally, never by relaxing determinism inside
`engine/`. A validation Implementation Package must specify this explicitly: "run N seeded
simulations of vignette X, collect distribution of [metric]," never "introduce non-determinism into
the engine to sample variability."

## 7. What this framework expects from FS-201 / FS-301

Any Implementation Package under FS-201 or FS-301 that makes a quantitative claim about what a
metric "means" must cite which §5 check(s) were applied, even informally, and must not claim
statistical validity beyond what the available sample size supports. A metric that has only passed
face validity (§5.1) should be reported as such, not silently treated as validated.

## 8. Related topics

R409/R410 (verification vs. validation, the formal vocabulary this document operationalizes), R407
(Monte Carlo), R408 (sensitivity analysis), DOM-002 (the instrument this framework is designed to
validate), DOM-004 (the broader research-use context this validation discipline serves).
