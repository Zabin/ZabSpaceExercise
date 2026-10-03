> **Document ID:** FS-123
> **Version:** 1.0
> **Status:** ✅ Ready for implementation planning (`FR-1230`); `FR-4440` shares one Open Question
> with it (the index-to-scaling mapping function) that must be resolved before either can be
> implemented
> **Note on this repository's chain:** no `05-feature-decomposition` Feature Catalog exists here
> (per this skill's own Gotchas); this document's approved input is the just-baselined
> requirements themselves — `docs/requirements/01-functional-requirements.md` `FR-1230`, `FR-4440`
> — plus [`R131` v1.1](../research/encyclopedia/R131-space-environment-and-space-weather-operations.md)
> §3 and the real baseline code they extend (`spacesim/engine/perturbations.py`,
> `spacesim/session/manager.py`).
> **Dependencies:** [FS-106](FS-106-white-cell-dashboard.md) v2.1 (the existing `space_weather`
> inject effect and its `severity` field, which this Feature is additive to, not a replacement for)
> **Referenced By:** [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0074` (item B8),
> `BL-0104` (the index-to-scaling design question),
> [docs/requirements/01-functional-requirements.md](../requirements/01-functional-requirements.md)
> `FR-1230`, `FR-4440`
> **Produces:** a deterministic coupling from a declared space-weather index time series into LEO
> drag decay (`FR-1230`) and environment-induced anomaly rate (`FR-4440`) — both blocked on Open
> Question 1 for full closure
> **Feature Mapping:** FS-123 (this document)
> **Related Topics:** [FS-122](FS-122-sensor-modality-models.md) (unrelated capability, same
> release increment)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template.*

# FS-123 — Space-Weather-Index-Driven Drag and Anomaly-Rate Coupling

## Purpose

Couple a declared space-weather index time series (F10.7 solar flux, Kp/Ap geomagnetic index) into
two consequences that are currently either unwired or coarse: `engine/perturbations.py`'s existing
`secular_drag_decay()` function is not called by the runtime propagator at all (`FR-1230`'s own
Rationale, `docs/FUTURE-WORK.md` §2/§13 R12/GAP-01), and the existing `space_weather` inject's
`severity` field scales only eclipse drain/telemetry signatures, not the rate of environment-induced
anomaly injects (`FR-4440`). Both must remain deterministic — a declared index value at a declared
simulated time, never a wall-clock or out-of-band read (`CLAUDE.md` invariant 1; `ADR-0002`).

## Scope

**In scope:** accepting a space-weather index time series as vignette data or an inject payload
(`FR-1230`'s own Inputs); scaling LEO drag decay from it via `engine/perturbations.py`
(`FR-1230`); scaling the firing rate of environment-induced anomaly injects (the `anomaly` effect
type `FR-4430` already introduced) from the same declared series (`FR-4440`).

**Out of scope (named, not silently absorbed):** the specific mathematical mapping from an index
value to a drag-decay multiplier or an anomaly-firing-rate multiplier — neither `FR-1230`/`FR-4440`
nor `R131` v1.1 §3 commits to a formula, only that F10.7/Kp are the correct numeric inputs (Open
Question 1, `docs/pipeline/backlog.md` `BL-0104`); the existing `severity`-driven eclipse
drain/telemetry-signature scaling (`FS-106` v2.1's own, unchanged scope).

## Requirements Implemented

- `FR-1230` — Space-weather-index-driven LEO drag coupling.
- `FR-4440` — Space-weather-index-driven anomaly rate scaling.

## User Workflows

1. **White Cell declares a space-weather index time series in a vignette, or fires a `space_weather`
   inject carrying one.** The declared series (per-index values at declared simulated times) becomes
   part of the deterministic input state, exactly like the existing `space_weather` inject's
   `severity` field is today.
2. **The simulation propagates a LEO Asset.** At each propagation step, the currently-effective index
   value(s) scale a drag-decay term applied via `secular_drag_decay()` (or an equivalent
   deterministic function of the declared index and elapsed simulated time), for Assets in a regime
   where drag is physically material.
3. **The simulation evaluates whether to fire an environment-induced anomaly.** The currently-
   effective index value(s) scale the rate at which `FR-4430`'s `anomaly` effect fires, higher during
   a higher-severity index period.
4. **Facilitator/analyst replays the exercise.** Because the index series is itself vignette data or
   an inject payload already covered by the `EventLog`, replaying the identical
   `(initial_state, ordered eventlog, seed)` reproduces byte-identical propagated state and anomaly
   firing sequence (`FR-1120`; `ADR-0002`).

## System Behaviour

- **Normal path — `FR-1230`.** A declared index time series is read by the propagator at each step
  for a LEO-regime Asset; the resulting drag-decay term composes with the existing propagation
  output. No declared series: behavior is unchanged from baseline (no drag coupling), per `FR-1230`'s
  own Preconditions framing.
- **Normal path — `FR-4440`.** The same declared series scales the firing-rate check
  `session/manager.py`'s existing condition/schedule mechanism already performs for the `anomaly`
  effect type. No declared series: no rate scaling (baseline `FR-4430` behavior unchanged).
- **Edge case — the exact mapping function.** Not specified by either FR's own text (Open Question
  1) — this document does not invent one.
- **Determinism, both leaves.** Because the index series enters as declared data (vignette-authored
  or an inject payload), not a live external feed, replay reproduces identical results
  (`FR-1230`/`FR-4440`'s shared Postcondition).

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `engine/perturbations.py` | Owns `secular_drag_decay()` and the other pure perturbation functions; extended (or newly wired into the runtime propagator, per `FR-1230`'s own Rationale that it exists but is uncoupled today) to consume the declared index value(s). |
| `engine/propagator.py` | Owns the runtime propagation loop; the coupling point where `FR-1230`'s scaled drag term is applied to a LEO-regime Asset's propagated state. |
| `session/manager.py` | Owns the existing inject-effect firing mechanism (`_apply_inject_effects`, `_h_condition_check`) `FR-4440` extends with index-driven rate scaling for the `anomaly` effect type. |
| `content/vignette.py` | Owns vignette-authored data ingestion — the declared index time series' schema, alongside the existing `space_weather` inject payload shape. |

## Interfaces Used

- `INT-0008` (SessionManager → Engine Clock/Scheduler/EventLog/OrderSystem) — the existing interface
  both the propagation coupling (`FR-1230`) and the inject-firing coupling (`FR-4440`) operate
  through; no new interface.
- `INT-0016` (White Cell Inject → Engine direct mutation bypass) — the existing interface the
  declared index series enters through when delivered as an inject payload, per `FR-4440`'s own
  citation.

## Data Model Changes

- A space-weather index time series (per-index values at declared simulated times) becomes part of
  vignette-authored data and/or the existing `space_weather` inject payload shape — additive to the
  existing `severity` enum, not a replacement (`FR-1230`'s own Rationale). No change to `WorldState`'s
  own shape beyond carrying this declared series, consistent with the existing `space_weather`
  state already tracked (per `CLAUDE.md`'s code map).

## State Changes

The declared index time series is read-only input state for the duration it is in effect — it is
not a session-runtime-mutable value outside of a new inject/vignette-data declaration itself
(mirroring how the existing `severity` field already behaves).

## Error Handling

- No declared index series: both leaves are no-ops, reproducing exactly today's behavior (no drag
  coupling, no anomaly-rate scaling) — stated explicitly in both FRs' own Preconditions.
- An index value outside a physically plausible range: not addressed by either FR's own text (Open
  Question 2).

## Performance Considerations

None named by `FR-1230`/`FR-4440` — both are a small, deterministic scaling computation per
propagation/firing-check step, not a new computational class.

## Security Considerations

None — this Feature introduces no new trust boundary; the declared index series is White-Cell-
authored data, consistent with every other vignette/inject data field.

## Acceptance Criteria

1. Given two index time series with differing Kp/F10.7 values, the same Asset's propagated altitude
   decay differs measurably and consistently with the higher-drag series decaying faster; replaying
   either run reproduces identical results. *(`FR-1230`)*
2. Given two runs differing only in their declared index time series (one quiescent, one
   high-severity), the high-severity run's environment-induced anomaly rate is measurably higher;
   replaying either run reproduces identical firing times. *(`FR-4440`)*

## Verification Plan

- Criterion 1 — Test: two propagation runs over an identical LEO Asset/duration, differing only in
  the declared index series; compare resulting altitude decay; re-run each and diff for byte
  identity.
- Criterion 2 — Test: two sessions differing only in the declared index series; compare the count/
  timing of fired `anomaly` effects over an identical duration; re-run each and diff for byte
  identity.

## Dependencies

None beyond the already-existing `FR-4410`/`FR-4430` (inject mechanism, `anomaly` effect type) and
`engine/perturbations.py`'s own existing (uncoupled) drag functions, both pre-existing baseline
code this Feature wires together rather than creates from scratch.

## Risks

- **Ambiguity risk (Open Questions 1-2 below) is the dominant risk for this Feature.** Neither leaf
  can be implemented to a specific, testable numeric behavior without a concrete mapping function —
  an Implementation Package attempted before Open Question 1 closes would have to invent one,
  which this specification explicitly declines to do.
- **Coordination risk with `FR-4430`'s existing `anomaly` effect and `FR-1062`'s condition-check
  scheduling.** `FR-4440`'s rate-scaling must compose with, not replace, the existing
  `_h_condition_check`/`_apply_inject_effects` mechanism `IP-1062` already shipped.

## Open Questions

1. **What is the concrete mapping function from a declared Kp/F10.7 value to a drag-decay multiplier
   (`FR-1230`) or an anomaly-firing-rate multiplier (`FR-4440`)?** Neither the backlog row (`BL-0074`)
   nor `R131` v1.1 §3 specifies one — only that a real relationship exists and that F10.7/Kp are the
   correct numeric inputs. This is squarely a design-level choice (a specific formula or lookup
   table) an Implementation Package needs before it can write a single, testable function. Needs
   resolution during `07-implementation-planning` (or an earlier `03`/`04` pass if the mapping
   itself needs research grounding beyond what `R131` already provides) — this document does not
   invent one, per `docs/pipeline/backlog.md` `BL-0104`'s own explicit routing.
2. **What is the observable behavior for a declared index value outside a physically plausible
   range** (e.g. a negative F10.7, an implausibly extreme Kp)? Neither FR's own Preconditions/
   Acceptance Criteria address this. Needs a `04-requirements-engineering` amendment or an
   `07-implementation-planning` design decision — this document does not invent one.

## Related ADRs

`ADR-0002` (deterministic core — both leaves' shared determinism Postcondition); `ADR-0006`
(sub-stepped deterministic clock — the propagation/firing-check cadence both leaves' scaling
computation runs against).

## Related Interfaces

None beyond `INT-0008`/`INT-0016` already cited under Interfaces Used.
