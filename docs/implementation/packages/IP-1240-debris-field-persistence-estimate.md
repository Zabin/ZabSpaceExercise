# IP-1240 — Debris-Field Persistence Estimate by Altitude

> **Package ID:** IP-1240
> **Version:** 1.0
> **Status:** 🟡 READY *(authorized 2026-09-27 by the project owner's direct instruction, MSTR-006 §3)*
> **Dependencies:** [FS-124](../../features/FS-124-debris-field-persistence-estimate.md) v1.0
> (`FR-1430`), `engine/effects.py` (`VERIFIED` baseline code, `IP-1051`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [docs/pipeline/backlog.md](../../pipeline/backlog.md) `BL-0077` (item B11), `BL-0115` (this
> Feature's one Open Question)
> **Produces:** an altitude-derived `persistence_estimate` attached to every `DebrisField`,
> satisfying `FR-1430` in full
> **Feature Reference:** [FS-124 — Debris-Field Persistence Estimate by Altitude](../../features/FS-124-debris-field-persistence-estimate.md)
> **Supersedes:** none — new package
> **Related Topics:** [`spacesim/engine/effects.py`](../../../spacesim/engine/effects.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package. Confirmed directly against the live code at authoring time:
`engine/effects.py`'s destructive-effect resolution and `spawn_debris` inject handling are the two,
and only two, code paths that construct a `DebrisField` — both reachable at this package's proposed
insertion point, with the resulting orbital state (and therefore altitude) already computed before
the `DebrisField` object is built in either path.*

## Package ID

IP-1240

## Title

Debris-Field Persistence Estimate by Altitude

## Objective

Compute and attach an estimated `persistence_estimate` to every `DebrisField` at creation time,
derived from its altitude, displayed wherever the field is already rendered — deliberately narrower
than Candidate Requirement `CR-17`'s deferred, fuller persistent-debris/gating mechanism.

> **This package is authorized for coding.** Per MSTR-006 §3, the project owner gave explicit
> go-ahead 2026-09-27 (batched with five sibling packages from the same Should-tier intake round).

## Feature Reference

[FS-124 — Debris-Field Persistence Estimate by Altitude](../../features/FS-124-debris-field-persistence-estimate.md)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-1430 | Debris-field persistence estimate by altitude | A new `persistence_estimate` attribute computed once at `DebrisField` creation (both the destructive-effect path and the `spawn_debris` inject path), from a pure function of altitude; displayed on the existing rendering surface(s) with no additional per-read computation. |

## Architecture Components

- **C1 Simulation Engine** (`engine/effects.py`) — owns `DebrisField` creation; extended to compute
  and attach `persistence_estimate` at both of its two construction sites.
- **C4 Operator Console** (`ui_web/`) — displays the new attribute wherever a `DebrisField` is
  already rendered; additive field on an existing response shape, no new route.

## Interfaces

`INT-0008` (SessionManager → Engine Clock/Scheduler/EventLog/OrderSystem) — the existing interface
`DebrisField` creation already operates through; no new interface.

## Design Decisions (resolving FS-124's Open Question)

1. **Open Question 1 (`BL-0115`) — confirmed by direct code reading, not a decision.** Both
   `DebrisField`-construction sites in `engine/effects.py` (destructive-effect resolution,
   `spawn_debris` inject handling) already have a fully computed resulting orbital state before
   constructing the `DebrisField`, so a determinable altitude is always available at this package's
   insertion point — the "altitude not determinable" edge case is confirmed unreachable in the
   current code, not merely assumed so.

## Files to Create

None.

## Files to Modify

- `spacesim/engine/effects.py` — a new pure function (e.g. `_persistence_estimate(altitude_km:
  float) -> <value>`), grounded on `R117` v1.2 §3.1's real-world debris-lifetime-by-altitude bands
  (weeks-months below ~300-400km; years-decades at 600-1000km; centuries above ~900km); called at
  both `DebrisField`-construction sites, attaching the result to the new `persistence_estimate`
  attribute.

## Implementation Tasks

1. Write a failing test asserting a lower-altitude `DebrisField`'s `persistence_estimate` is shorter
   than a higher-altitude one's, before writing `_persistence_estimate()`.
2. Write `_persistence_estimate()` as a pure function of altitude, citing `R117` v1.2 §3.1's banded
   figures directly in an inline comment (not re-deriving them).
3. Wire the function into both `DebrisField`-construction sites.
4. Write a failing test asserting neither field's `persistence_estimate` changes Access Window
   computation (`FR-1220`) or conjunction-screening outcome, before/alongside the above — a
   regression guard against the temptation to wire the estimate into gating (Scope boundary, per
   FS-124).
5. Re-run the full existing suite; confirm zero regressions to any existing debris/effects test.

## Tests to Add

- `spacesim/tests/test_effects.py` — `persistence_estimate` computed correctly at both construction
  sites; monotonic with altitude; does not affect Access Window/conjunction-screening behavior.

The two permanent gates (`spacesim/tests/test_determinism.py`, `spacesim/tests/test_import_guard.py`)
must be re-run green — `_persistence_estimate()` is a pure function of already-computed state, no
wall-clock read or global RNG use introduced.

## Documentation Updates

- `CLAUDE.md` Code Map — `engine/effects.py`'s entry gains a one-line note for
  `persistence_estimate`.
- `docs/requirements/03-requirements-traceability-matrix.md` — `FR-1430`'s row's `Impl.
  Package`/`Test` cells updated from `UNASSIGNED` to `IP-1240`/`test_effects.py`.
- `docs/features/FS-124-debris-field-persistence-estimate.md` — `Referenced By` metadata gains this
  package's link.
- `docs/pipeline/backlog.md` — `BL-0115` flips `DONE` (resolved by direct code reading, per Design
  Decision 1 above).

## Definition of Done

- [ ] `persistence_estimate` computed and attached at both `DebrisField`-construction sites.
- [ ] Lower-altitude fields show shorter estimates than higher-altitude ones.
- [ ] No change to Access Window computation or conjunction-screening outcome as a result of the
  estimate's presence.
- [ ] Full existing test suite green, zero regressions, both permanent gates green.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] `test_effects.py`'s new tests exist and are green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green.
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green.
- [ ] Independently confirm, by reading the shipped code, that `persistence_estimate` is read-only
  after creation and is never consulted by Access Window/conjunction-screening logic.

## Dependencies

- **Upstream:** [FS-124](../../features/FS-124-debris-field-persistence-estimate.md) v1.0
  (approved, `✅ Ready for implementation planning`); `engine/effects.py` (`IP-1051`, `VERIFIED`).
- **Downstream:** none.
- **Build-sequencing:** independent of every other package in this batch (no shared file).

## Risks

- **Scope-creep risk (named explicitly in FS-124's own Risks).** The temptation to wire the
  estimate into gating is real given how closely related this is to `CR-17`'s deferred fuller
  mechanism — this package's Implementation Task 4 exists specifically to guard against that.

## Rollback Considerations

`persistence_estimate` is a purely additive attribute computed from already-existing state;
reverting the two call sites and removing the attribute fully removes this package's capability
with no data-migration concern — no existing `DebrisField` (there being no persisted-across-session
debris state today) is affected.
