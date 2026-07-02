# ADR-0030 — AI-determinism doctrine: non-deterministic components stay outside `engine/`

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0030
- **Title:** Any non-deterministic component (AI advisory, AI-Red, future ML) enters the
  deterministic core only as ordered, logged `SessionAPI` events — never as a direct `engine/`
  dependency or a wall-clock/model-call read inside `engine/`
- **Status:** Accepted

## Context

[`strategic-review-2026-07.md`](../../reviews/strategic-review-2026-07.md) §1.3 names this
project's assumption **A6**: "Determinism and AI integration are compatible without a stated
doctrine. The deterministic core (invariant 1) and any future non-deterministic AI participant
coexist only if AI outputs enter the engine as ordered, logged events. This is achievable within
the current architecture — the session layer is the right seam (ADR-0021) — but nothing in the
baseline states it as a rule, and a future implementer could violate it innocently." The review's
recommendation R4 (§6.1) asks that this be stated explicitly in one ADR, observing it is "already
implicitly true (ADR-0021)."

Checking that claim against the existing baseline: `CLAUDE.md`'s load-bearing invariant 1
("Deterministic core... No wall-clock reads and no global RNG anywhere in `engine/`") and invariant
2 ("UI-agnostic engine... imports no UI or transport code") already constrain `spacesim/engine/`
absolutely. ADR-0002 (deterministic core) and ADR-0003 (`SessionAPI` as the single seam) already
establish that every non-engine actor — human or otherwise — reaches simulation state only through
the session layer. ADR-0021 places AI-Red (`redai.py`) in the session layer specifically so it
"issues orders through the same `SessionAPI` surface a human Red operator would use," and its
Consequences already note this guarantees AI-Red "cannot accidentally bypass any validation... or
plan-first commanding rule that applies to humans." Every piece of the doctrine A6 asks for is
therefore already true by construction of ADR-0002/0003/0021 combined with `CLAUDE.md`'s
invariants — but, as the review observes, no single document states the general *rule*, only the
one AI-Red instance of it. A future feature (FC-01 AI-supported mission planning, or any other
ML-driven component) could read this gap as license to call a model, poll a clock, or read
non-seeded randomness from inside `engine/`, believing no rule forbids it because AI-Red's ADR
is scoped to AI-Red specifically.

## Decision

**All non-deterministic computation — LLM/ML inference, wall-clock reads for anything other than
the session layer's existing wall-clock anchor, any randomness not drawn from the engine's seeded
`SeededRng` — is prohibited inside `spacesim/engine/`, without exception, for any component
present or future.** A non-deterministic component (an AI advisory layer, AI-Red, a future
autonomous-adversary or autonomous-satellite feature) may only affect simulation state by:

1. Running entirely inside or above the session layer (`spacesim/session/`), never inside
   `spacesim/engine/` — the same placement rule ADR-0021 already applies to AI-Red, generalized to
   any future non-deterministic component.
2. Producing its output (a plan, an order, a critique, a doctrine decision) as an ordinary
   `SessionAPI` call — the identical call surface a human operator uses (`SessionAPI.issue_order`-
   equivalent, `dry_run()`, etc.) — so the output is validated, windowed, and fog-of-war-filtered
   exactly as a human's would be.
3. Having that call appended to the ordered `EventLog` like any other action, so replay/rewind/AAR
   reproduce the AI's decision exactly as recorded — not by re-invoking a possibly non-deterministic
   model at replay time.

Conversely: **the engine itself never calls out to a model, a clock, or an unseeded random source.**
`test_import_guard.py`'s existing AST scan of `spacesim/engine/` (forbidden imports, wall-clock
reads, non-`rng.py` `random` use) is the enforcement mechanism for this decision, not a new one —
this ADR states as policy what that test already polices as fact, and commits that any future
AI-touching code path must keep passing it.

## Alternatives Considered

- **Allow a bounded exception**: permit `engine/` to call a *fast, local, deterministic-at-a-fixed-
  seed* model (e.g. a small on-device classifier) directly, reasoning that determinism only
  requires reproducibility, not "no model calls." **Rejected** — a model's weights/version are an
  external dependency the engine cannot version-pin the way it pins its own code; a silently
  upgraded model would break byte-identical replay of *old* saves without changing a single line of
  `engine/` code, the exact failure mode the review's Red Team over-engineering finding worried
  about relaxing determinism for. Kept outside the seam instead, so a model upgrade is just a new
  session-layer component version, not an engine determinism regression.
- **Log AI outputs but let the engine re-derive them at replay time** (e.g. re-run the model during
  AAR scrub instead of replaying its logged decision). **Rejected** — this is exactly the failure
  A6 warns about: a re-invoked model is not guaranteed to return the same output twice, which would
  make AAR replay non-exact for any session containing an AI decision. Logging the *output*, not the
  *invocation*, is the only choice consistent with invariant 1.
- **Do nothing — treat A6 as already obvious from ADR-0002/0003/0021 and not worth a dedicated
  ADR.** **Rejected** per the review's own reasoning: "it is already implicitly true... making it
  explicit costs a page and prevents an invariant breach later." The cost of stating the rule is
  low and the review's confidence rating is High; a future coding agent extending FC-01/FC-02/FC-03
  benefits from a rule stated once at the general level rather than having to re-derive it from
  three separate ADRs scoped to narrower cases.

## Rationale

This ADR adds no new mechanism — every piece of enforcement it relies on (`test_import_guard.py`,
the `SessionAPI` seam, `EventLog` ordering) already exists and already ships. Its value is
closing assumption A6 by naming the *general* rule non-deterministic components must follow,
rather than leaving it inferable only from AI-Red's specific case (ADR-0021) or the engine's
own invariants (`CLAUDE.md` 1–2) considered separately. This is squarely the kind of "governance
and posture, no new capability" action the review's §6.1 table scopes R4 as: Value High,
Difficulty Low, Risk Low, Confidence High.

## Consequences

- Any future non-deterministic feature (FC-01 AI-supported mission planning, FC-02's adaptive
  AI-Red, FC-03 autonomous on-board behaviors, FC-15 human-machine-teaming instrumentation) is
  bound by this decision from design time, not discovered as a violation after implementation.
- `spacesim/tests/test_import_guard.py` remains the load-bearing enforcement mechanism; a future
  contributor extending it (e.g. to also flag a new forbidden import for a model-inference library)
  is executing this ADR's decision, not inventing a new one.
- GDS-01 §13's Open Question register treats strategic-review assumption A6 as **resolved** by this
  ADR — see GDS-01's "Strategic review reconciliation" section and the
  [Strategic Assumptions Register](../strategic-assumptions-register.md) entry for A6.
- No existing code changes as a result of this ADR — `redai.py` already complies (ADR-0021); this
  ADR generalizes the rule it already follows.

## Related

`CLAUDE.md` load-bearing invariants 1–2; ADR-0002 (deterministic core); ADR-0003 (`SessionAPI`
single seam); ADR-0021 (AI-Red session-layer placement); `spacesim/tests/test_import_guard.py`;
[`strategic-review-2026-07.md`](../../reviews/strategic-review-2026-07.md) §1.3 assumption A6,
§6.1 recommendation R4; [Strategic Assumptions Register](../strategic-assumptions-register.md).
