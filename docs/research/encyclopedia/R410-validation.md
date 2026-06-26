# R410 — Validation

> **Document ID:** R410
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R409](R409-verification.md)
> **Referenced By:** [R404](R404-measurement-theory.md), [R412](R412-survey-and-assessment-instrument-design.md)
> **Produces:** the formal validation vocabulary backing DOM-005's entire framework — the gap DOM-005 §1 identifies relative to this project's already-strong verification
> **Feature Mapping:** DOM-005 (Validation Framework, entire document), the worked `AUDIT-2026-06-UI-TTC.md` §2 precedent DOM-005 §4 cites
> **Related Topics:** [R409](R409-verification.md) (Verification — the distinct, comparatively strong discipline this topic
> contrasts with), [R404](R404-measurement-theory.md) (Measurement Theory — instrument validation as a special case of this
> topic), [R412](R412-survey-and-assessment-instrument-design.md) (Survey and Assessment Instrument Design)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-005 is built entirely around the verification/validation distinction ([R409](R409-verification.md) vs. this topic) and
names validation as this project's actual gap relative to its already-strong verification practice.
This topic supplies the formal validation vocabulary and methodology DOM-005's framework rests on,
grounded in the worked example DOM-005 §4 already cites: the `AUDIT-2026-06-UI-TTC.md` §2
power-calibration bug.

## 2. Concepts

**Validation: does the model/instrument represent the real-world phenomenon it claims to.**
Validation asks "did we build the right thing" — a fully verified jam-effect formula (correctly
implements its specified math, [R409](R409-verification.md)) can still be invalid if the specified formula itself doesn't
match real-world EW jam behavior; validation is the check against the external phenomenon, not
against the model's own internal spec.

**Face validity as the cheapest, weakest check.** Does the model/metric look, on inspection by a
domain-knowledgeable reviewer, like it represents the claimed phenomenon — useful as a first filter,
but easily fooled by a model that looks right but behaves wrong in an edge case, which is exactly
what the `AUDIT-2026-06-UI-TTC.md` §2 bug was: a power-calibration formula that likely looked
reasonable on inspection but produced a wrong result under specific conditions.

**Validation against ground truth, where ground truth is available.** Where a real-world reference
value exists (a known physical constant, a published real EW effectiveness figure, an expert SME
judgment), comparing the model's output against it is the strongest validation check — this is harder
in this simulator's domain than in, say, orbital mechanics (where Skyfield/sgp4 already provide a
validated reference for propagation) since adversarial effect-resolution behavior (jam/cyber success
probabilities) has less authoritative public ground truth to validate against.

**The `AUDIT-2026-06-UI-TTC.md` §2 precedent as the worked validation method.** DOM-005 §4 cites this
specific audit as the concrete instance of validation work already done in this project: a
power-calibration formula was checked not just for internal consistency (verification) but for
whether its calibrated output matched the physically expected behavior across the input range,
surfacing a bug verification alone had not caught — this is the template for future validation work:
check the model's behavior against an independent expectation, not just against its own internal
logic.

**Validation is never fully "done"; it is a standing practice, re-applied as the model evolves.**
Unlike a verification test (binary pass/fail against a fixed spec), a validation claim's confidence
should be revisited whenever the model's scope of use changes ([R406](R406-modeling-practices.md)) — a model validated for one
regime is not automatically validated for an extended one.

## 3. Operational Context

The verification/validation distinction is formalized in military modeling-and-simulation practice as
VV&A (Verification, Validation, and Accreditation) precisely because a heavily-verified-but-
unvalidated simulator can produce confident-looking but substantively wrong training conclusions —
this is the exact failure mode DOM-005 names as this project's current risk, and the
`AUDIT-2026-06-UI-TTC.md` precedent shows the risk is concrete, not hypothetical, for this codebase.

## 4. Implementation Guidance

- **Treat any future fidelity claim (a jam/cyber/engage formula's calibration, a propagator's
  accuracy) as requiring validation work distinct from and in addition to its existing verification
  tests** — per DOM-005 §1's framing, a green test suite is not validation evidence.
- **Use the `AUDIT-2026-06-UI-TTC.md` §2 method as the template for future validation audits**:
  check a formula's output against an independent physical/doctrinal expectation across its input
  range, specifically probing edge cases a purely internal-consistency check would not surface.
- **Where no authoritative real-world ground truth exists (most adversarial effect-resolution
  behavior), validate against doctrinal plausibility and SME-reviewable face validity instead**, and
  state explicitly in any writeup that this is a weaker validation standard than ground-truth
  comparison — don't claim a stronger validation than was actually performed.
- **Re-validate, don't assume validity carries over, when a model's scope of use is extended**
  (per [R406](R406-modeling-practices.md)) — e.g. a doctrine preset validated against one vignette's scenario state is not
  automatically validated against a substantially different one.

## 5. Feature Mapping

DOM-005 (Validation Framework) in its entirety is the direct consumer.

## 6. Related Topics

[R409](R409-verification.md) (Verification, the contrasting strong discipline), [R404](R404-measurement-theory.md) (Measurement Theory, instrument
validation as a special case), [R412](R412-survey-and-assessment-instrument-design.md) (Survey and Assessment Instrument Design).
