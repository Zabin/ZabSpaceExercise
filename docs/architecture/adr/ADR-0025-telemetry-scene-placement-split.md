# ADR-0025 — telemetry.py vs. scene.py subsystem placement

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0025
- **Title:** Pure render/diagnostic helpers are placed by whether they require cell identity, not by accident of history
- **Status:** Accepted

## Context

`telemetry.py` lives in `spacesim/engine/` while the structurally similar `scene.py` lives in
`spacesim/session/`. GDS-03 Open Question 3 states both are "pure, read-only, replay-safe, and
render belief/diagnostic views rather than mutating state," yet they live in different layers with
no stated placement rule distinguishing them. GDS-03 explicitly "followed the existing file
locations rather than reconciling them into one placement rule." The architecture review
(`reviews/architecture-review.md` §2 finding 2) independently reached the same flag, which GDS-03
records as corroborating weight that this is a real seam, not a false positive.

## Decision

A placement rule is adopted: **a pure render/diagnostic helper belongs in `engine/` if it is a
function of `WorldState` and an asset/object id alone (no cell-identity parameter), and belongs in
`session/` if it requires a cell identity to determine what to show (i.e. it is fog-of-war-aware)**.

Checked against the actual signatures:

- `telemetry.py`'s public functions — `sample(world, asset_id, param_id, t, seed, ...)`,
  `series(world, asset_id, param_id, t0, t1, n, seed, ...)`, `telemetry_db(world, asset_id, t,
  seed)`, `subsystem_log(world, asset_id, t, seed)` — take `world` and an asset id, never a cell.
  Telemetry is the same regardless of who is asking; it is a ground-truth-derived diagnostic
  signal, not a belief view. **Conforms to the rule as engine/-resident.**
- `scene.py`'s public function — `build_scene(world, cell)` — takes a `cell` parameter and
  explicitly renders "its own assets at their true positions, and other-side objects ONLY as
  tracks (the cell's belief)" (module docstring). It cannot be evaluated without knowing which
  side is asking. **Conforms to the rule as session/-resident**, consistent with fog-of-war being
  a session-layer concern (invariant 3, `CLAUDE.md`; ADR-0004).

Both files already satisfy this rule under the current placement — **no file move is required**.
The rule is adopted prospectively, to govern where a *future* pure render/diagnostic helper should
live: if it takes a cell identity, it belongs in `session/`; if it does not, it belongs in
`engine/`.

## Alternatives Considered

- Move both to the engine (rationale candidate: both are pure functions, with no mutation) —
  **rejected**: `scene.py` is not a pure function of `WorldState` alone — it requires cell
  identity to filter, which is a session-layer concern per invariant 3.
- Move both to the session layer (rationale candidate: both serve presentation-facing views) —
  **rejected**: `telemetry.py` has no cell-identity dependency at all; moving it to `session/`
  would be a layer violation in the other direction with no rule-based justification.
- Leave them split, with an explicit rule for future pure-render helpers — **adopted**, refined
  into the cell-identity test above rather than left unstated.

## Rationale

The cell-identity test is the one architectural distinction that actually differs between the two
files' signatures (confirmed by reading both modules), and it tracks the project's existing,
load-bearing fog-of-war boundary (invariant 3: "Filtering lives at the `SessionAPI`/
`CellController` layer, never in the UI" — and, by the same logic, never in `engine/` either,
since `engine/` must stay UI-and-session-agnostic per invariant 2). A rule based on cell-identity
is therefore consistent with invariants already in force, rather than an arbitrary new convention.

## Consequences

- A future implementer adding a third pure-render/diagnostic helper now has a concrete test to
  apply: does the function need to know which cell is asking? If yes, `session/`; if no, `engine/`.
- No refactor is required for the two existing files — both already conform.
- GDS-03 Open Question 3 is resolved: the split is not arbitrary, and is governed by this rule
  going forward.

## Related

GDS-03 Open Question 3; `reviews/architecture-review.md` §2 finding 2; `CLAUDE.md` invariants 2–3;
ADR-0004; `spacesim/engine/telemetry.py`; `spacesim/session/scene.py`.
