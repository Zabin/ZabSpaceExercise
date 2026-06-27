# MSTR-002 — Architecture Principles

> **Document ID:** MSTR-002
> **Version:** 1.0
> **Status:** ✅ Stable
> **Dependencies:** MSTR-001
> **Referenced By:** MSTR-007, all DOM-*, all FS-*, all IMP-*, `docs/architecture/`
> **Produces:** the constraints every Feature Specification and Implementation Package must satisfy
> **Feature Mapping:** N/A — program-level
> **Related Topics:** [`docs/design/01-architecture-overview.md`](../design/01-architecture-overview.md),
> [`CLAUDE.md`](../../CLAUDE.md) §"Load-bearing invariants"

[↑ Docs index](../INDEX.md) · [Master index](MSTR-005-documentation-map.md)

## 1. Purpose

This document is the **single normative statement** of the architectural constraints every part of
SpaceSim must satisfy, regardless of which layer or feature is being touched. It elevates and
explains the six invariants already enforced in `CLAUDE.md` and adds the principles a Feature
Specification or Implementation Package author must reason from when none of the existing
constraints directly answer a design question. `docs/design/01-architecture-overview.md` is the
detailed *how*; this document is the *why*, kept stable across phases.

## 2. The six load-bearing invariants

These are gates, not guidelines. A pull request, Implementation Package, or generated code that
violates one of these is wrong by definition, independent of test results.

1. **Deterministic core.** `engine/` reads no wall clock, uses no unseeded RNG.
   `(initial_state, ordered eventlog, seed) → byte-identical state`, always. This is what makes
   rewind/undo/branch *exact* rather than approximate, and what makes AAR replay trustworthy as a
   training artifact (a debrief built on a non-reproducible run teaches the wrong lesson). The
   Phase-1 determinism property test (`test_determinism.py`) is the permanent gate; no
   Implementation Package may propose a change that requires relaxing it.
2. **UI-agnostic engine.** `engine/` imports no UI or transport code, enforced by an AST-scanning
   test (`test_import_guard.py`), not a linter convention. This is what lets the same engine drive a
   desktop UI, a web UI, or a headless batch-experiment harness (see DOM-004/DOM-005) without
   forking core logic.
3. **Fog-of-war at the boundary.** Filtering to a cell's belief state happens at
   `SessionAPI`/`CellController`, never in the UI layer. A UI bug can leak pixels; it must never be
   able to leak ground truth, because the *only* enforcement point is the session boundary. Any
   Feature Specification that adds a new read path (a new endpoint, a new telemetry stream) must
   say explicitly which side of this boundary it sits on.
4. **Plan-first.** Operators plan commands that execute at the next valid access window and task
   sensors for collection; they never act instantly on perfect knowledge. This is a pedagogical
   requirement as much as a technical one — see DOM-001 §"Plan-execute as the unit of learning" —
   and it constrains UI design (no "instant fire" button can exist without a window check behind
   it) and engine design (every effect-producing action routes through `OrderSystem`).
5. **Sub-step the clock.** Advance to the next scheduled event, never past it. A naive large step at
   high time-acceleration silently skips short LEO passes — this is a *correctness* bug
   (a missed access window the operator never saw), not a performance nuance, and it is why
   `Scheduler` exists as a first-class engine component rather than a simple `for tick in range(...)`.
6. **Content is data.** Vignettes, asset templates, and effect templates are data files (YAML), not
   Python. If a new feature's scenario-specific logic starts leaking into `spacesim/engine/*.py` or
   `spacesim/content/*.py` as bespoke branches, that is a design smell — the fix is almost always a
   new injectable primitive (an effect template field, a vignette schema extension) rather than a
   special case in code. Implementation Packages must flag any deviation from this explicitly as a
   risk (see the IMP- template's "Risks" section).

## 3. Layering principle

```
engine/    — deterministic core. No UI, no network, no wall clock, no unseeded RNG.
session/   — SessionManager, CellController (fog-of-war), SessionAPI (the network seam).
content/   — vignettes / assets / effects as data, + TLE import.
ui_web/    — the chosen front end. Depends on session, never reaches past it into engine internals.
tests/     — pytest, including the permanent determinism property test.
```

Each layer may depend only on the layers below it in this list. `ui_web/` never imports from
`engine/` directly; it always goes through `session/`. This is what makes fog-of-war enforcement
possible at all — if the UI could read engine state directly, the boundary in invariant 3 would
have no teeth.

## 4. Seam principle (interfaces over implementations)

Three explicit seams exist so a higher-fidelity or alternative implementation can be substituted
without touching callers:

- `Propagator` — Kepler+J2 (fictional orbits) vs. `sgp4` (real TLEs). A future high-fidelity
  numerical propagator (see R101, R-Tier "Future Operations" hooks) drops in here.
- `AccessProvider` — the six access channels (`command_uplink`, `telemetry_downlink`,
  `sensor_observation`, `jam_footprint`, `weapon_engagement`, `rpo_proximity`) and their window
  caching.
- `EffectResolver` — the five-D's effect taxonomy + the cyber exception.

**Architecture principle:** any new physical or doctrinal model (a new sensor type, a new effect
category) should be evaluated first against "does this fit an existing seam?" before a new one is
proposed. Proliferating seams without a forcing function (an actual second implementation) is
itself an anti-pattern — `perturbations.py`'s drag/J3/J4/third-body/SRP functions, for example, are
deliberately *pure functions composed by a future propagator*, not yet a fourth seam, because no
second consumer exists yet.

## 5. Replay-safety principle

Several modules (`scene.py`, `telemetry.py`, `orders.dry_run()`) are explicitly **pure / read-only**
— they compute a view without mutating `WorldState` or consuming RNG. This property, "replay-safe,"
is load-bearing for two reasons: (a) it is what lets `dry_run()` power "why can't I do this"
pre-disabled UI buttons without side effects, and (b) it is what lets AAR replay/scrub re-derive any
historical telemetry or scene view deterministically from the eventlog without re-running the whole
simulation with side effects. Any new read-oriented capability (a new telemetry stream, a new
belief-state view) must preserve this property; Implementation Packages must state explicitly
whether a new function is replay-safe and how that was verified (typically: no `rng.` calls, no
assignment into `world.*` state).

## 6. Degrade, don't crash

`AccessProvider` treats an unknown endpoint id (e.g., a command planned `via` a station not in the
force) as "no access," not an exception. This reflects a general principle: **operator error or
incomplete vignette data should produce a sensible in-world failure (denied, no window, etc.), not
a stack trace.** Implementation Packages for new commands/orders must specify the degrade behavior
for every invalid-input case, not just the happy path.

## 7. Using this document

When a Feature Specification or Implementation Package author hits a design question not directly
answered by `docs/build-spec/` or `docs/design/`, the six invariants (§2) and the five derived
principles (§3–§6) are the test to apply: *does the proposed design preserve determinism,
UI-agnosticism, boundary-enforced fog-of-war, plan-first interaction, sub-stepped time, and
data-driven content — and does it degrade gracefully rather than crash on bad input?* If yes,
proceed and cite which principle(s) the design satisfies. If a genuine conflict exists, escalate per
[`MSTR-006`](MSTR-006-governance-principles.md) §3 rather than quietly working around it.
