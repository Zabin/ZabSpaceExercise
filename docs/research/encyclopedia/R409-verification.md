# R409 — Verification

> **Document ID:** R409
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R406](R406-modeling-practices.md)
> **Referenced By:** [R410](R410-validation.md)
> **Produces:** the formal vocabulary for the verification work DOM-005 §3 already says is strong in this codebase (pytest, the determinism property test)
> **Feature Mapping:** the entire `spacesim/tests/` suite, DOM-005 §3
> **Related Topics:** [R406](R406-modeling-practices.md) (Modeling Practices — the documented assumptions verification checks
> against), [R410](R410-validation.md) (Validation — the distinct, comparatively weaker discipline DOM-005 identifies as
> this project's actual gap), DOM-005 (Validation Framework)
> **Last Reviewed:** 2026-07-02
> **Primary Sources Consulted:** 2 (Tier A/B foundational software-engineering + M&S sources — see §3 Sources)

[↑ Tier R400 index](R400-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

DOM-005 §3 distinguishes verification (already strong in this codebase: pytest, the determinism
property test) from validation (the comparative gap). This topic supplies the formal verification
vocabulary, both to name precisely what the existing strong test suite is already doing well and to
make the boundary with [R410](R410-validation.md)'s validation explicit, since conflating the two is exactly the mistake
DOM-005 warns against.

## 2. Scope

Covers: the verification definition ("building it right"), unit vs. integration verification, why
verification alone is insufficient, and regression testing as ongoing verification, applied to
`spacesim/tests/`. Does **not** cover: the validation half of the distinction (does the spec itself
match reality) — [R410](R410-validation.md)'s job, this topic's direct counterpart — or the
documented-assumptions precondition verification checks against
([R406](R406-modeling-practices.md)'s job, assumed established here).

## 3. Concepts

**Verification: does the implementation match its own specification.** The canonical framing —
verification asks "are we building the product right" (as opposed to validation's "are we building
the right product") — traces to Barry Boehm's
[*Software Engineering Economics*](https://archive.org/details/softwareengineer0000boeh) (Prentice-
Hall, 1981), whose "solving the equations right" (verification) vs. "solving the right equations"
(validation) phrasing has become the standard software-engineering statement of the distinction.
Robert Sargent's simulation-specific framework (already cited at [R406](R406-modeling-practices.md)
§3) applies the same distinction to a simulation model: does
[`engine/orbit.py`](../../../spacesim/engine/orbit.py)'s Kepler+J2 implementation correctly compute
what the documented Kepler+J2 equations specify, independent of whether Kepler+J2 itself is a good
model of reality (that second question is validation, [R410](R410-validation.md)). The Phase-1
determinism property test is a verification test in this precise sense: it checks the implementation
satisfies its own stated contract `(initial_state, eventlog, seed) → byte-identical state`, not
whether that contract is a good representation of any external reality.

**Unit tests verify a component in isolation; integration tests verify components working together.**
`spacesim/tests/test_import_guard.py` (AST-scanning `engine/` for forbidden imports) is a verification
check on an architectural invariant, not a numerical one — verification covers both numerical
correctness and architectural/contract correctness.

**Verification is necessary but not sufficient.** A perfectly verified implementation (matches its
spec exactly) can still be invalid if the spec itself is wrong or unrealistic — this is precisely
Boehm's and Sargent's point, and DOM-005 §3's application of it: this codebase's verification (469
tests green per CLAUDE.md) is strong, but that strength says nothing about whether, e.g., a jam
success-probability formula's specified shape actually matches real-world EW behavior (a validation
question).

**Regression tests as ongoing verification.** Per CLAUDE.md's mandatory test-driven workflow, every
resolved design gap gets a regression test — this is verification's ongoing discipline: each fix is
locked in by encoding its expected (specified) behavior as a permanent, re-checked test, preventing
silent re-introduction of a bug already fixed once.

### Sources

- *Boehm, B.W. (1981). Software Engineering Economics.* Prentice-Hall —
  [live (Internet Archive)](https://archive.org/details/softwareengineer0000boeh)
  · [snapshot](https://web.archive.org/web/2026*/https://archive.org/details/softwareengineer0000boeh)
  · accessed 2026-07-02.
- *Sargent, R.G. Verification and Validation of Simulation Models* — same source cited at
  [R406](R406-modeling-practices.md) §3; not re-derived here in full, see that topic's Sources
  subsection for the live/Wayback/accessed-date record.

## 4. Operational Context

The verification/validation distinction ("building it right" vs. "building the right thing") is
foundational in software engineering (Boehm, 1981) and simulation credibility assessment (VV&A —
Verification, Validation, and Accreditation — is a formal discipline in military M&S specifically,
per DoDI 5000.61, already cited at [R406](R406-modeling-practices.md) §3) precisely because a
heavily-tested system can still produce wrong real-world conclusions if its specification, not its
implementation, is the source of error — DOM-005 names this exact gap for this project.

### Sources

Uses the same sources cited inline in §3 (Boehm 1981; Sargent) plus DoDI 5000.61 (cited in full at
[R406](R406-modeling-practices.md) §3); no additional sources introduced in this section.

## 5. Implementation Guidance

- **Continue the existing test-first discipline (CLAUDE.md's mandatory workflow) as this project's
  verification backbone** — every new `engine/` feature should get a failing test against its stated
  spec before implementation, exactly the existing pattern.
- **When writing a verification test, state explicitly what specification it is checking against**
  (a documented formula, an architectural invariant, a previously-fixed bug's expected behavior) —
  this keeps the test's scope (verification) visibly distinct from a validation claim ([R410](R410-validation.md)) it
  should not be conflated with.
- **Do not treat a green test suite as evidence of real-world fidelity** — per DOM-005 §3 and Boehm's
  distinction, a passing verification suite establishes the implementation matches its spec, not that
  the spec is a good model of the real phenomenon; that separate claim requires [R410](R410-validation.md)'s validation work.

## 6. Feature Mapping

The `spacesim/tests/` suite and DOM-005 §3 are the direct consumers.

## 7. Related Topics

[R406](R406-modeling-practices.md) (Modeling Practices, the documented assumptions verification checks against), [R410](R410-validation.md) (Validation,
the distinct and comparatively weaker discipline this project still needs), DOM-005 (Validation
Framework).
