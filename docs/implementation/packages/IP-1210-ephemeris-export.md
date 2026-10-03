# IP-1210 — Ephemeris Export (Truth and Cell-Observed, ECI/RIC, CSV/CCSDS OEM)

> **Package ID:** IP-1210
> **Version:** 1.0
> **Status:** 🔵 COMPLETE *(implemented 2026-09-27, MSTR-006 §3 authorization granted the same day;
> awaiting `09-package-verification` in a fresh session — this session implemented it and may not
> verify its own work)*
> **Remediation (2026-09-27/28, authorized by the project owner per MSTR-006 §3 — fix to true
> RIC-frame velocity, not rename/document as inertial):** an independent fresh-session
> verification pass ([VR-1210](../verification/VR-1210-ephemeris-export.md)) found `to_ric()`
> returned the raw inertial relative velocity resolved onto the RIC basis, omitting the RIC
> frame's own rotation term — a co-orbital, RIC-stationary neighbour (constant RIC separation)
> reported a spurious −13.29 m/s radial velocity (Finding H1, High). **Fixed:** `to_ric()` now
> subtracts `ω × ric_r`, with `ω = |h_ref| / |r_ref|²` along the reference orbit's normal (`n_hat`
> — conserved specific-angular-momentum direction/rate for any two-body orbit), expressed in the
> RIC basis as `[0, 0, ω]` since `n_hat` is exactly the basis's own third row. Also fixed (Finding
> M1, Medium): `write_oem`'s KVN structure is now CCSDS-conformant — `CREATION_DATE`/`ORIGINATOR`
> precede a `META_START`/`META_STOP` block that actually wraps the metadata fields (previously
> empty, with the fields sitting outside it), epochs use the CCSDS ASCII time format (no
> `+00:00` suffix), and `REF_FRAME` is now `TEME` (the engine's own documented approximation —
> `engine/propagator.py`: "TEME treated as ECI at moderate fidelity" — not the more precise
> `EME2000` the prior label implied). Resolves `BL-0136` (Finding M2, the OEM/RIC tension) per the
> project owner's requirements-baseline amendment: new `FR-7430` requires a **companion
> RIC-specific export file** — implemented as `write_ric_csv()` plus a new `format=ric` option on
> both ephemeris HTTP routes, alongside the existing `format=csv` (ECI+RIC) and `format=oem`
> (ECI-only, CCSDS-conformant, per `FR-7410`/`FR-7420`'s amended text). New/strengthened tests in
> `test_ephemeris.py` (co-orbital-stationary + finite-difference cross-check for the velocity fix,
> a structural OEM-conformance test, a `write_ric_csv` test) and `test_web.py` (the new `format=ric`
> route). Full suite green (both permanent gates included). Re-verification is a fresh
> `09-package-verification` pass, not yet run.
> **Dependencies:** [FS-121](../../features/FS-121-ephemeris-export.md) v1.0
> (`FR-7410`/`FR-7420`), [FS-103](../../features/FS-103-custody-management.md) v1.1 (confirmed
> `Track.state_estimate` independence from truth), [ADS-1500](../../architecture/ADS-1500-per-cell-custody-estimated-state-and-export.md)
> (the replay-based export design this package builds exactly as specified), `FR-7310`/
> `session/aar.py` (`VERIFIED` via `IP-1070` — the replay mechanism this package generalizes from a
> single point to a time span), `FR-6220` (no-cell endpoints, the binding `FR-7410`'s route must use)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [docs/pipeline/backlog.md](../../pipeline/backlog.md) `BL-0069` (external validation report,
> 26 Sep 2026, items B2/B3), `BL-0098` (FS-121's two Open Questions, resolved below)
> **Produces:** truth and cell-observed ephemeris export in ECI/RIC, CSV/CCSDS OEM, satisfying
> `FR-7410`/`FR-7420` in full
> **Feature Reference:** [FS-121 — Ephemeris Export](../../features/FS-121-ephemeris-export.md)
> **Supersedes:** none — new package
> **Related Topics:** [`spacesim/session/aar.py`](../../../spacesim/session/aar.py),
> [`spacesim/engine/simulation.py`](../../../spacesim/engine/simulation.py),
> [`spacesim/engine/custody.py`](../../../spacesim/engine/custody.py),
> [`spacesim/engine/maneuver.py`](../../../spacesim/engine/maneuver.py) (`lvlh_frame`)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package. Confirmed directly against the live code at authoring time:
`session/aar.py::state_at(mgr, seq)` (lines 41-49) replays to an eventlog **sequence number**, not
a time — this package needs reconstruction at an arbitrary **time** T, so it adds one small,
additive sibling function rather than changing `state_at`'s existing contract (used unmodified by
the AAR scrubber, `IP-1070`, `VERIFIED`). `engine/simulation.py::replay()` (lines 153-198) already
accepts both `up_to_seq` and `final_time` — exactly the two parameters needed to reconstruct "the
world as it existed at time T" (replay up to the eventlog position at-or-before T, then pin
`world.now = T`), with no per-sample snapshot support in `aar.state_at`'s own call (it passes no
`snapshots=` argument), confirming `ADS-1500`'s own Risk citation that this is currently a full
replay-from-`initial_state` per sample. `engine/maneuver.py::lvlh_frame(r_eci, v_eci)` (lines 37-55,
already `public`, part of `__all__`) returns exactly the R/T/N (Radial/Transverse/Normal) unit-vector
triad this package's RIC transform needs — the same physical frame RIC uses under different letter
names (R=Radial, I=In-track≡Transverse, C=Cross-track≡Normal) — reused directly, not reimplemented.*

## Package ID

IP-1210

## Title

Ephemeris Export (Truth and Cell-Observed, ECI/RIC, CSV/CCSDS OEM)

## Objective

Let White Cell export ground-truth state vectors over a time span, and let a cell export its own
believed (custody-estimated) state vectors over a time span, in ECI and RIC-relative-to-a-chosen-
reference-object frames, as CSV and CCSDS OEM files — both variants driven by one shared
serializer and one shared time-span replay mechanism, per `ADS-1500`'s System Architecture.

> **This is a forward-design package. Per MSTR-006 §3, this document's own specification is not
> itself an authorization to write code** — a separate, explicit user go-ahead is required before
> any Implementation Task below begins.

## Feature Reference

[FS-121 — Ephemeris Export](../../features/FS-121-ephemeris-export.md)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-7410 | Truth ephemeris export | A new no-cell function samples ground truth (`world.assets[X].orbit`) at each time T in the requested span via time-span replay, transforms to ECI directly and to RIC relative to the reference object's own ground-truth state, and serializes via the shared writer. Reachable only through an existing no-cell route/pattern (`FR-6220`). |
| FR-7420 | Cell-observed ephemeris export | A new cell-scoped function samples the requesting cell's own `Track.state_estimate` for X at each T (empty result for a T with no Track, per `FS-121`'s own Postcondition), forward-propagates it to exactly T, resolves the RIC reference per the cell's-own-asset-vs.-tracked-object rule, and serializes via the same shared writer. |
| FR-7430 | Companion RIC-specific ephemeris export file (**added 2026-09-27, owner amendment resolving `BL-0136`**) | `write_ric_csv(rows)` — a dedicated CSV carrying only `t`/`ric_r`/`ric_v`, exposed via a new `format=ric` option on both `/ephemeris/truth` and `/ephemeris/{cell}`, alongside the existing `format=csv` (ECI+RIC) and `format=oem` (ECI-only). Pairs specifically with `write_oem`, since CCSDS OEM has no native RIC-relative data-line representation and `write_csv` already carries both. |

## Architecture Components

- **C2 Session / Application Layer** (`session/ephemeris.py`, new, sibling to `aar.py`) — owns
  time-span replay (a new `aar.py::state_at_time(mgr, t)` sibling of the existing `state_at(mgr,
  seq)`), the truth/cell-observed sampling functions, and the shared ECI/RIC/CSV/OEM serializer,
  per `ADS-1500`'s System Architecture diagram exactly.
- **C1 Deterministic Core** (`engine/simulation.py::replay`, `engine/propagator.py`,
  `engine/maneuver.py::lvlh_frame`) — supplies the replay reconstruction, forward-propagation, and
  RTN-frame primitives this package calls, unmodified.
- **C4 Operator Console** (`ui_web/`) — exposes the truth export through an existing no-cell route
  pattern and the cell-observed export through a new cell-scoped route, per `FR-6220`/`ADR-0004`.

## Interfaces

`INT-0014` (AAR/Replay → Simulation Engine) — the interface both exports drive, generalized from a
single-point replay read to a time-span read. Per the Requirements Review's own Finding 6
(`BL-0093`), this is a documented-shape stretch, **not resolved by this package** — routed to
whoever next touches the ICD, exactly as `FS-121` itself already states; this package's own design
does not require the ICD edit to proceed. `INT-0007` (`CellController` → Custody/TrackCatalog) for
the cell-observed variant's fog-of-war binding.

## Design Decisions (resolving `BL-0098`, carrying `ADS-1500`'s own Open Questions forward)

1. **A requested time span `[t1, t2]` that falls entirely outside the session's own recorded
   eventlog range (t1 after the last recorded time, or t2 before the initial epoch) is rejected
   outright**, with a specific error naming the session's actual valid range
   (`[initial_epoch, last_recorded_time]`). **A span that only partially overlaps the valid range is
   silently clamped to the overlapping portion**, and the export proceeds with however many samples
   fall inside it (not an error) — the same "outright-reject-the-nonsensical-whole, gracefully-
   degrade-the-partially-valid" posture `IP-1180`'s own Design Decision 2 already established for a
   different edge case in this same increment. This is this package's own interpretation, not a
   literal `FR-7410`/`FR-7420` citation — flagged as a Risk below, recommended for a future `04`
   amendment.
2. **No numeric sampling-rate/performance ceiling is imposed** — consistent with `ADS-1500`'s own
   Open Question 2 (no source document supplies one). This package instead: (a) requires the caller
   to specify an explicit sample interval (never "auto-dense" against an unbounded span); (b) when
   omitted, defaults to a coarse interval derived from the span itself (`span / 100`, clamped to a
   minimum of one bus-tick period, `BUS_TICK_PERIOD_S` — reusing the existing cadence constant
   rather than inventing a new one); (c) documents the O(samples × eventlog length) cost
   characteristic directly in the route's own error/help text, so a facilitator can reason about
   cost before requesting a fine-grained sample over a long span. Enforcement of a hard ceiling is
   left to a future package if real usage shows it necessary — an explicit, disclosed deferral,
   mirroring `ADS-1500`'s own choice not to invent a number no source supplies.

## Files to Create

- `spacesim/session/ephemeris.py` — the shared time-span export module:
  - `sample_times(t1: int, t2: int, interval_s: Optional[float] = None) -> list[int]`: builds the
    list of sampled instants per Design Decision 2's default-interval rule.
  - `truth_ephemeris(mgr, object_id: str, reference_id: str, t1: int, t2: int, interval_s:
    Optional[float] = None) -> list[dict]`: for each sampled T, calls the new
    `aar.state_at_time(mgr, T)`, reads `world.assets[object_id].orbit`/`world.assets[reference_id]
    .orbit`, propagates both to T via the existing `ModeratePropagator`, and returns a per-T ECI +
    RIC row (empty list on a wholly-out-of-range request per Design Decision 1; a partially-out-of-
    range request silently clamps `sample_times`' own bounds).
  - `cell_observed_ephemeris(mgr, cell: str, object_id: str, reference_id: str, t1: int, t2: int,
    interval_s: Optional[float] = None) -> list[dict]`: for each sampled T, calls
    `aar.state_at_time`, then `world.track_for(cell, object_id)`; a `None` track (or `None`
    `state_estimate`) produces no row for that T (`FR-7420`'s own Postcondition, an empty result,
    not a fabricated one); otherwise forward-propagates `tr.state_estimate` to T. Resolves the
    reference object per `FS-121`'s own rule: `world.assets[reference_id].orbit` (ground truth)
    directly if `world.assets[reference_id].owner == cell`; otherwise
    `world.track_for(cell, reference_id).state_estimate` (propagated to T) — never ground truth for
    a merely-tracked reference object.
  - `to_ric(r_target, v_target, r_ref, v_ref) -> tuple[np.ndarray, np.ndarray]`: calls
    `engine.maneuver.lvlh_frame(r_ref, v_ref)` to get the reference object's own R/T/N basis at T,
    projects `r_target - r_ref` onto that basis for `ric_r`; for `ric_v` (**remediated 2026-09-27/28
    per BL-0134**), projects `v_target - v_ref` onto the same basis and then subtracts the RIC
    frame's own rotation term `ω × ric_r` (`ω = |h_ref|/|r_ref|²` along the basis's own third row) —
    the true RIC-frame-relative velocity, not the raw inertial relative velocity resolved onto RIC
    axes (which the prior implementation returned).
  - `write_csv(rows: list[dict]) -> str` / `write_oem(rows: list[dict], object_id: str) -> str` /
    `write_ric_csv(rows: list[dict]) -> str` (**new, `FR-7430`, added in the 2026-09-27/28
    remediation**): `write_csv` carries both ECI and RIC (parameterized only by the already-uniform
    row shape both export functions produce: `{"t": int, "eci_r": [...], "eci_v": [...],
    "ric_r": [...], "ric_v": [...], "uncertainty_km"?: float, "confidence"?: float}` — the last two
    present only for the cell-observed variant, per `ADS-1500` Decision 4's "uncertainty as
    metadata" framing); `write_oem` carries ECI only, CCSDS-conformant KVN (OEM has no native
    RIC-relative data-line representation); `write_ric_csv` is the companion RIC-only file `FR-7430`
    requires, pairing with `write_oem` specifically (since `write_csv` already carries RIC).

## Files to Modify

- `spacesim/session/aar.py` — add `state_at_time(mgr, t: int) -> WorldState`: computes
  `seq = sum(1 for e in mgr.sim.eventlog.entries if e.sim_time <= t)`, then calls
  `replay(mgr.sim._initial_state, mgr.sim._seed, mgr.sim.eventlog, handlers=mgr.sim.handlers(),
  up_to_seq=seq, final_time=t)` — additive, does not change `state_at(mgr, seq)`'s existing
  behavior or any of its callers (the AAR scrubber, `IP-1070`, unaffected).
- `spacesim/ui_web/server.py` — a new no-cell route (e.g. `GET
  /api/sessions/{sid}/ephemeris/truth`) for `FR-7410`, reachable without a `cell` binding exactly
  like `/godview`/`/eventlog`/`/aar*` already are (`FR-6220`); a new cell-scoped route (e.g. `GET
  /api/sessions/{sid}/ephemeris/{cell}`) for `FR-7420`, filtered the same way every other
  cell-scoped read already is.

## Implementation Tasks

1. Write a failing test asserting `aar.state_at_time(mgr, t)` reconstructs a `WorldState` whose
   `now == t` and whose applied-event set matches exactly the events with `sim_time <= t`, before
   implementing it — confirmed as additive by re-running every existing `aar.py` test unchanged.
2. Write a failing test for `sample_times()`: an explicit `interval_s` produces the expected sample
   list; an omitted one defaults to `span/100` clamped to `BUS_TICK_PERIOD_S`; a wholly-out-of-range
   `[t1, t2]` produces an empty list; a partially-out-of-range span clamps to the overlapping
   portion — before implementing it.
3. Write a failing test for `truth_ephemeris()`: a known two-asset scenario's ground-truth ECI state
   at a sampled T matches a hand-computed value; the RIC-relative state relative to a chosen
   reference object matches a hand-computed projection via `lvlh_frame`, before implementing it.
4. Write a failing test for `cell_observed_ephemeris()`: a cell with an observed `Track` on X
   produces the expected propagated-`state_estimate` row at each T; a T before the cell's first
   observation of X produces no row for that T (not a fabricated one); a reference object that is
   the cell's own asset uses ground truth, one that is only tracked uses the cell's own
   `state_estimate` — each asserted independently, before implementing it. Include the negative
   assertion: the export never contains ground truth for an object the cell does not own, and never
   contains another cell's belief.
5. Write a failing test asserting `truth_ephemeris()`/`cell_observed_ephemeris()` are byte-identical
   across two calls against the same saved session (`FR-7410`/`FR-7420`'s determinism criterion),
   before considering either function complete.
6. Write a failing test for `write_csv()`/`write_oem()`: round-trip a known row set through each
   writer and assert the expected field values appear correctly formatted, before implementing them.
7. Wire the two new HTTP routes; write a failing test asserting the truth route is reachable with no
   `cell` query param and the cell-observed route enforces the same fog-of-war binding every other
   cell-scoped route already does, before adding the routes.
8. Re-run the full existing suite, in particular every existing `aar.py`/`test_aar.py` test.

## Tests to Add

- `spacesim/tests/test_aar.py` — `state_at_time()`'s new behavior, regression-checked against
  `state_at()`'s existing tests.
- `spacesim/tests/test_ephemeris.py` *(new)* — `sample_times()`'s interval/clamping/out-of-range
  behavior; `truth_ephemeris()`'s ECI/RIC correctness; `cell_observed_ephemeris()`'s empty-result/
  reference-object-rule/negative-assertion behavior; the replay-determinism assertion for both;
  `write_csv()`/`write_oem()`'s round-trip correctness.
- `spacesim/tests/test_web.py` — both new HTTP routes, including the cell-observed route's
  fog-of-war enforcement (mirroring the existing `test_scene.py` fog-of-war test pattern, per
  `FS-121`'s own Verification Plan).

The two permanent gates (`spacesim/tests/test_determinism.py`, `spacesim/tests/test_import_guard.py`)
must be re-run green — `session/ephemeris.py` is Session-Layer code built entirely on `replay()`
and the existing `Propagator`/`lvlh_frame` primitives, introducing no wall-clock read, no global
RNG use, and no new `engine/` import-boundary crossing.

## Documentation Updates

- `CLAUDE.md` Code Map — a new `session/ephemeris.py` entry added; `session/aar.py`'s entry gains
  the `state_at_time()` addition note.
- `docs/design/05-interface-control-document.md` — `INT-0014`'s entry prose updated to note the
  now-generalized time-span replay read (no interface ID/shape change, per this package's own
  Interfaces section — a citation update, not an ICD edit; the documented-shape stretch itself
  remains routed to whoever next touches the ICD, per `BL-0093`).
- `docs/requirements/03-requirements-traceability-matrix.md` — `FR-7410`/`FR-7420` rows'
  `Implementation Package` cell updated from `UNASSIGNED` to `IP-1210`; `Test` cell updated once
  the named test files exist.
- `docs/features/FS-121-ephemeris-export.md` — `Referenced By` metadata gains this package's link
  (metadata cross-link only). Its three Open Questions are not struck out by this package directly
  (belongs to `06-feature-specification`), but this package's Design Decisions give `06` everything
  needed to close Open Questions 1-2; Open Question 3 (the FS-103 v1.1 sequencing note) is now moot
  — this package was authored after reading FS-103 v1.1 directly, as that note itself anticipated.
- `docs/pipeline/backlog.md` — `BL-0098` updated: both Open Questions resolved by this package's two
  Design Decisions; recommend flipping to `DONE` at the next `00-pipeline-manager` harvest. `BL-0093`
  (the `INT-0014` ICD stretch) remains open/unchanged, still routed to the ICD owner.

## Definition of Done

- [x] **Explicit user authorization obtained** for this package's Implementation Tasks (MSTR-006
  §3) — granted 2026-09-27 by the project owner's direct instruction.
- [x] Given a time span and reference object, the truth export's CSV and CCSDS OEM files both
  contain state vectors matching the engine's own truth at each sampled time, correctly transformed
  into RIC; reachable only via a no-cell route.
  (`test_truth_ephemeris_eci_and_ric_correctness`, `test_ephemeris_truth_route_no_cell_binding`,
  `test_ephemeris_oem_format`)
- [x] Given the same time span, a cell-observed export request from cell C for object X returns C's
  own estimated state at each sampled time, matching `CellController`'s existing fog-of-war rule —
  no ground truth, no other cell's belief.
  (`test_cell_observed_ephemeris_uses_state_estimate_and_own_asset_reference`,
  `test_cell_observed_ephemeris_never_leaks_ground_truth_or_another_cells_belief`,
  `test_cell_observed_ephemeris_reference_object_only_tracked_uses_stale_state_estimate`,
  `test_ephemeris_cell_observed_route_fog_of_war_enforced`)
- [x] A wholly-out-of-range time span is rejected with a specific error; a partially-out-of-range
  span is silently clamped, not rejected. (`test_truth_ephemeris_wholly_out_of_range_raises`,
  `test_truth_ephemeris_partial_range_clamps_not_rejects`,
  `test_ephemeris_truth_route_wholly_out_of_range_is_400`)
- [x] Both exports are byte-identical across repeated calls against the same saved session.
  (`test_truth_ephemeris_deterministic_across_repeated_calls`)
- [x] Full existing test suite green, zero regressions, both permanent gates green: **707
  passed / 3 skipped** (up from 689/3), `test_determinism.py` and `test_import_guard.py` both
  green.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] `test_ephemeris.py`'s new tests exist and are green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green.
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green.
- [ ] Full existing suite re-run with zero regressions, in particular every existing `aar.py`/
  `test_aar.py` test (`state_at_time()`'s addition must not perturb `state_at()`).
- [ ] Independently confirm, by reading the shipped code, that the cell-observed export never reads
  `world.assets[...].orbit` for an object the requesting cell does not own.
- [ ] Independently round-trip at least one truth and one cell-observed export through both CSV and
  CCSDS OEM writers and confirm the numeric values match a hand-computed expectation.
- [ ] Independently confirm the wholly-vs-partially-out-of-range distinction (Design Decision 1)
  against a hand-constructed fixture of each kind.

## Dependencies

- **Upstream:** [FS-121](../../features/FS-121-ephemeris-export.md) v1.0 (approved,
  `✅ Ready for implementation planning`), [FS-103](../../features/FS-103-custody-management.md)
  v1.1 (the confirmed `Track.state_estimate` independence this package's cell-observed export
  depends on), [ADS-1500](../../architecture/ADS-1500-per-cell-custody-estimated-state-and-export.md)
  (the design this package builds exactly as specified), `session/aar.py`'s existing `state_at`/
  `replay()` machinery (`VERIFIED` via `IP-1070`, extended in place via one new additive sibling
  function), `engine/maneuver.py::lvlh_frame` (baseline code, reused unmodified).
- **Downstream:** none identified.
- **Build-sequencing:** Independent of the other five Must-tier packages this increment (different
  files, no shared seam).

## Risks

- **Performance risk (see `ADS-1500`'s own Constraints/Risks, carried forward unresolved).** A naive
  per-sample full replay from `initial_state` (confirmed: `aar.state_at`/`state_at_time` pass no
  `snapshots=` argument) scales as O(samples × eventlog length) — a fine-grained sample over a long
  time span on a long-running session could be slow. Design Decision 2's default-interval heuristic
  mitigates the common case but does not solve the underlying cost; a future package could pass
  `mgr.sim.snapshots` through to speed up replay-from-checkpoint, an optimization deliberately
  deferred here (matching `ADS-1500`'s own explicit non-decision).
- **Design Decision 1 (partial-range clamping) is this package's own interpretation**, not a literal
  `FR-7410`/`FR-7420` citation — flagged for a future `04-requirements-engineering` pass to
  formalize, consistent with this increment's own established pattern (`IP-1180`'s analogous
  disclosed interpretations).
- **RIC transform correctness depends on `lvlh_frame`'s existing R/T/N convention matching the
  file-format consumer's expectation of "RIC."** The two frames are physically identical (same
  three orthogonal directions), but a consumer expecting a specific axis-ordering convention in the
  written file must be accommodated by the serializer's own column labeling, not by changing
  `lvlh_frame` itself — named here so `08-code-implementation` does not conflate "the physics is the
  same" with "the column order in the CSV is automatically correct."

## Rollback Considerations

`session/ephemeris.py` is wholly new; `aar.py::state_at_time()` is a new additive sibling function
with no effect on `state_at()`'s existing callers. Reverting this package removes both export
routes and the new module with no effect on any existing session, save file, or AAR functionality —
no data-migration concern, since this package produces only downloadable export files, never
persistent session/engine state.
