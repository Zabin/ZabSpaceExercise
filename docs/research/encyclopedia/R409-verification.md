# R409 — Verification

> **Document ID:** R409
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R406](R406-modeling-practices.md)
> **Referenced By:** [R410](R410-validation.md)
> **Produces:** the formal vocabulary for the verification work DOM-005 §3 already says is strong in this codebase (pytest, the determinism property test)
> **Feature Mapping:** the entire `spacesim/tests/` suite, DOM-005 §3
> **Related Topics:** [R406](R406-modeling-practices.md) (Modeling Practices — the documented assumptions verification checks
> against), [R410](R410-validation.md) (Validation — the distinct, comparatively weaker discipline DOM-005 identifies as
> this project's actual gap), DOM-005 (Validation Framework)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-005 §3 distinguishes verification (already strong in this codebase: pytest, the determinism
property test) from validation (the comparative gap). This topic supplies the formal verification
vocabulary, both to name precisely what the existing strong test suite is already doing well and to
make the boundary with [R410](R410-validation.md)'s validation explicit, since conflating the two is exactly the mistake
DOM-005 warns against.

## 2. Concepts

**Verification: does the implementation match its own specification.** Verification asks "did we
build the thing right" — i.e., does [`engine/orbit.py`](../../../spacesim/engine/orbit.py)'s Kepler+J2 implementation correctly compute
what the documented Kepler+J2 equations specify, independent of whether Kepler+J2 itself is a good
model of reality (that second question is validation, [R410](R410-validation.md)). The Phase-1 determinism property test is
a verification test in this precise sense: it checks the implementation satisfies its own stated
contract `(initial_state, eventlog, seed) → byte-identical state`, not whether that contract is a
good representation of any external reality.

**Unit tests verify a component in isolation; integration tests verify components working together.**
`spacesim/tests/test_import_guard.py` (AST-scanning `engine/` for forbidden imports) is a verification
check on an architectural invariant, not a numerical one — verification covers both numerical
correctness and architectural/contract correctness.

**Verification is necessary but not sufficient.** A perfectly verified implementation (matches its
spec exactly) can still be invalid if the spec itself is wrong or unrealistic — this is precisely
DOM-005 §3's point: this codebase's verification (469 tests green per CLAUDE.md) is strong, but that
strength says nothing about whether, e.g., a jam success-probability formula's specified shape
actually matches real-world EW behavior (a validation question).

**Regression tests as ongoing verification.** Per CLAUDE.md's mandatory test-driven workflow, every
resolved design gap gets a regression test — this is verification's ongoing discipline: each fix is
locked in by encoding its expected (specified) behavior as a permanent, re-checked test, preventing
silent re-introduction of a bug already fixed once.

## 3. Operational Context

The verification/validation distinction ("building it right" vs. "building the right thing") is
foundational in software engineering and simulation credibility assessment (VV&A — Verification,
Validation, and Accreditation — is a formal discipline in military M&S specifically) precisely because
a heavily-tested system can still produce wrong real-world conclusions if its specification, not its
implementation, is the source of error — DOM-005 names this exact gap for this project.

## 4. Implementation Guidance

- **Continue the existing test-first discipline (CLAUDE.md's mandatory workflow) as this project's
  verification backbone** — every new `engine/` feature should get a failing test against its stated
  spec before implementation, exactly the existing pattern.
- **When writing a verification test, state explicitly what specification it is checking against**
  (a documented formula, an architectural invariant, a previously-fixed bug's expected behavior) —
  this keeps the test's scope (verification) visibly distinct from a validation claim ([R410](R410-validation.md)) it
  should not be conflated with.
- **Do not treat a green test suite as evidence of real-world fidelity** — per DOM-005 §3, a passing
  verification suite establishes the implementation matches its spec, not that the spec is a good
  model of the real phenomenon; that separate claim requires [R410](R410-validation.md)'s validation work.

## 5. Feature Mapping

The `spacesim/tests/` suite and DOM-005 §3 are the direct consumers.

## 6. Related Topics

[R406](R406-modeling-practices.md) (Modeling Practices, the documented assumptions verification checks against), [R410](R410-validation.md) (Validation,
the distinct and comparatively weaker discipline this project still needs), DOM-005 (Validation
Framework).
