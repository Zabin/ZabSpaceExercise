# IP-1321 — Missed Salvo Consumes Its Rounds: Charge Every Fired Engagement, Hit or Miss (FR-1480)

> **Package ID:** IP-1321
> **Version:** 1.0
> **Status:** 🔵 COMPLETE — 2026-10-17, `08-code-implementation`, pipeline run #177, awaiting a
> **fresh-session** `09-package-verification`. `engine/orders.py::OrderSystem._h_effect`: the
> consumption step's `if cons and outcome.success:` is now `if cons:` (with an `IP-1321`/`FR-1480`
> comment), so `consume.ammo` is charged for every engagement that reaches resolution; the
> execute-time re-check still returns first and charges nothing. Tests: 6 added to
> `test_effect_resource_bounds.py` (19 collected). **5 seen failing first** (`assert 2 == 1` /
> `2 == 0`: miss, destroyed target, exact-salvo miss, seed-2 parity miss, replay-after-miss); the
> seed-1 parity case (a hit) passed on arrival as intended. *Note:* Implementation Task 2 expected
> Tests 3–5 to pass on arrival; tests 3, 4 (miss seed) and 5 assert the new charge, so they could
> not — the expectation was inaccurate, not the tests. Task 3: no test asserted the old hit-only
> rule (`test_orders.py`'s `ammo == 0` follows a *hit*, still correct), and every shipped tutorial
> `engage` fires once — no fixture changed. Full suite **1022 passed / 3 skipped** (run #173
> baseline 1016/3 + 6 new); gates 14/14.
> *(Was 🟡 IN PROGRESS — 2026-10-17, `08-code-implementation`, pipeline run #177.)*
> *(Was 🟢 READY — authored 2026-10-17 by `07-implementation-planning`, pipeline run #176.)*
> Every dependency is `VERIFIED`. **Authorization (MSTR-006 §3):** this package falls under the
> project owner's standing pre-authorization of 2026-10-11 for the packages this iteration
> reaches (same precedent as `IP-1320`/`IP-1311`/`IP-1021`), and the owner's 2026-10-17 decision on
> `BL-0249` asked for exactly this behaviour change. Authoring the package is not itself the
> authorization; that standing decision is.
> **Dependencies:** [FS-132](../../features/FS-132-effect-resource-bounds.md) v1.1 (the spec).
> [IP-1320](IP-1320-effect-resource-bounds.md) (the consumption step and execute-time re-check this
> package changes) is `VERIFIED`.
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0249`
> **Produces:** an effector whose rounds drop by the salvo every time an engagement is fired,
> whether it hits or misses.
> **Feature Reference:** [FS-132 — Effect Resource Bounds](../../features/FS-132-effect-resource-bounds.md)
> v1.1 (`FEAT-1400` slice)
> **Related Topics:** [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [`spacesim/tests/test_effect_resource_bounds.py`](../../../spacesim/tests/test_effect_resource_bounds.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package (forward design) for the owner-directed rule change `BL-0249`: a missed
salvo now consumes its interceptors. It changes one condition in the consumption step `IP-1320`
shipped.*

---

## Package ID

IP-1321 (a second FS-132 slice: `IP-1320` is v1.0's package; the FS-1xx → `IP-1xx0`/`IP-1xx1`
lettered-slice convention).

## Title

Missed salvo consumes its rounds: charge every fired engagement, hit or miss.

## Objective

**As built at `64c5058`** (read this run; `VR-1320` §4 confirmed it live):
`engine/orders.py::OrderSystem._h_effect` (line 1047) runs the execute-time rounds re-check
(lines 1051–1061), resolves the effect, appends the effect-log record, and then charges the salvo
only inside `if cons and outcome.success:` (line 1074; the subtraction is line 1077). So:

| Case | As built | After this package (FS-132 v1.1) |
|---|---|---|
| Effector with 2 rounds, 1-round engagement executes and **hits** | 1 round left | 1 round left (unchanged) |
| Same, engagement executes and **misses** | 2 rounds left | **1 round left** |
| Same, target already destroyed at the execution moment (resolver returns not achieved, no roll) | 2 rounds left | **1 round left** |
| Rounds no longer cover the salvo at execution (re-check fails) | not resolved, nothing charged | unchanged |

## Feature Reference

[FS-132](../../features/FS-132-effect-resource-bounds.md) v1.1 — System Behaviour 3, State
Changes (v1.1 bullet), Error Handling (two v1.1 rows), Acceptance Criteria 2, 8 and 9, Risks
(v1.1). Behaviours 1, 2 and 4 and Acceptance Criteria 1 and 3–7 are `IP-1320`'s and stay as
shipped.

## Requirements Covered

| ID | How |
|---|---|
| `FR-1480` | `_h_effect` charges the salvo for every engagement that reaches resolution, regardless of `outcome.success`. |
| `FR-1460` (AC as amended 2026-10-17) | Its amended AC ("once it executes — whether it hits or misses — it leaves the effector with `N` minus the salvo") is met by the same change; the bound, the re-check and the Postcondition are untouched. |

This matches FS-132 v1.1's delta exactly; `FR-1470` is not touched (a jam's payload carries no
`ammo` entry, so it still consumes nothing).

## Architecture Components

- **C1 Simulation Engine** (`engine/orders.py` — `OrderSystem._h_effect`): the only behaviour
  change.
- **C2 Session Layer**, **C4 Operator Console**: unchanged. No reason code is added; the console's
  `REASON_TIPS` already carries `no_ammo`/`insufficient_ammo`, which are what a player now meets
  sooner after a miss.

The engine import boundary is unchanged. No new module.

## Interfaces

- **INT-0008** (SessionManager → OrderSystem): no shape change. The observable difference is the
  effector's `resources.ammo` in ground truth (god view, saves, AAR snapshots) after a miss.

### Design Decisions

1. **One condition removed.** In `_h_effect`'s consumption step, charge `cons["ammo"]` whenever
   `cons` carries `ammo` and the actor exists — drop the `outcome.success` term. Nothing else in
   `_h_effect` moves: the re-check still runs before resolution (so the charge can never drive
   rounds negative — `FR-1460`), the resolver call, the RNG draw, the effect-log record and the
   political-consequence side effects are unchanged and stay in the same order.
2. **"Fired" = reached resolution** (FS-132 Behaviour 3). The charge sits after the resolver call,
   so it covers a hit, a miss, and the resolver's early "target already destroyed" return alike;
   it does not cover the re-check's early return (not fired).
3. **Whole-salvo charge.** The charged figure stays `cons["ammo"]` (the `_engage_rounds` value the
   validation bound uses). No per-round accounting (FS-132 Scope).
4. **Determinism.** The charge reads only the event payload and world state; no clock, no RNG.
   Replay of any event log reproduces it. For a history with no missed engagement, state is
   byte-identical to today's. A saved session containing a miss replays under the new rule (FS-132
   State Changes) — intended, not a determinism break.
5. **Comment hygiene.** Update the `IP-1320` comment above the charge to cite `FR-1480`; keep the
   `FR-1470`/ADR-0037 "no `power_w` branch" comment.

## Files to Create

None.

## Files to Modify

Each was checked against the tree at `64c5058`:

- `spacesim/engine/orders.py`: `OrderSystem._h_effect` (starts line 1047), consumption step at
  lines 1074–1079 (`if cons and outcome.success:` … `actor.resources.ammo -= int(cons["ammo"])`).
- `spacesim/tests/test_effect_resource_bounds.py` (created by `IP-1320`): add the tests below;
  rename `test_exact_salvo_accepted_and_charged_on_success` only if its name would now mislead
  (it may stay — it asserts the hit case, which is still correct).

No other production file. `spacesim/tests/test_orders.py::test_kinetic_engage_requires_track_and_roe_then_spawns_debris`
asserts `ammo == 0` after a *successful* engagement — still correct, not changed.

## Implementation Tasks

1. Mark the package `IN PROGRESS` (header, MBP row, `packages/INDEX.md`, ROADMAP) before editing.
2. Write the tests below; tests 1 and 2 must be seen failing first against the as-built code
   (a miss and a destroyed-target engagement each leave the rounds unchanged today). Tests 3–5 are
   expected to pass on arrival (they pin behaviour that must not change).
3. Search the tests for any assertion that a failed/missed engagement leaves rounds unchanged, and
   the vignette `tutorial`/`coaching` blocks and `test_vignette_tutorials.py` for a second
   engagement from an effector that a first, missed engagement would now exhaust. Update any test
   that asserts the old hit-only rule so it asserts the new one (do not delete it), and list each
   in the completion note with why the old assertion is now wrong.
4. Implement Design Decisions 1 and 5 in `engine/orders.py`.
5. Run the full suite plus `test_determinism.py` and `test_import_guard.py`. Fix only defects this
   package introduced.
6. Do the documentation updates, then mark `COMPLETE`.

## Tests to Add

In `spacesim/tests/test_effect_resource_bounds.py`, reusing its `_kinetic_world`, `_osys`,
`_engage` and `_ForcedResolver` fixtures:

1. **A miss is charged** (FS-132 AC 8, `FR-1480`): `ammo=2`, `_ForcedResolver(success=False)`;
   a 1-round engagement executes → effect-log record `success is False`; `ammo == 1`; the target
   is not destroyed; a following `engage` with `salvo_n=2` is rejected `insufficient_ammo` by
   `dry_run` and `issue`.
2. **Destroyed target is charged** (FS-132 AC 8, Behaviour 3): with the real
   `ModerateEffectResolver`, mark the target `health = "destroyed"` before the window; the
   engagement executes (`achieved == "none"`, `success is False`) and `ammo` drops by the salvo.
3. **Exact salvo, miss** (FS-132 AC 2 as amended): `ammo=2`, `salvo_n=2`, forced failure →
   `ammo == 0`.
4. **Outcome parity** (FS-132 AC 9): for a fixed seed and the real resolver, the effect-log
   outcome (`success`, `achieved`) of a scripted engagement equals what the same seed produces with
   the charge disabled (or a recorded expectation) — the change affects bookkeeping only.
5. **Replay after a miss** (FS-132 AC 9, determinism): the world after test 1's miss equals
   `replay()` of its initial state and event log (`model_dump()` equal).

The existing `IP-1320` tests (oversized salvo, queued overdraw with forced success, re-check charge
nothing, jam power unchanged) must stay green unchanged.

## Documentation Updates

- `docs/requirements/03-requirements-traceability-matrix.md`: `FR-1480` row — Future Feature →
  `FS-132`, Test → `test_effect_resource_bounds.py`, Impl. Package → `IP-1321`; `FR-1460` row's
  Impl. Package cell notes `IP-1321` for the amended AC.
- `docs/features/FS-132-effect-resource-bounds.md`: `Referenced By` only.
- `CLAUDE.md` "Code map" `engine/orders.py` bullet: if it describes the charge, one clause that a
  fired salvo is charged hit or miss (`FR-1480`).
- MBP row and counts, `packages/INDEX.md`, ROADMAP row, this header.
- **Manual impact is not edited here.** `RED-5` ("Rounds are spent only on success") and the
  `docs/training/15-manual-traceability.md` §15.1 effect-resource-bounds row ("rounds spent only on
  success") go to `08-training-manual-authoring` once this package is `VERIFIED` — the harvest of
  the `08` run files the backlog entry.

## Definition of Done

- All Tests to Add exist and pass; tests 1 and 2 were seen failing first.
- Full suite green; any test that asserted the old hit-only rule now asserts the new rule (none
  deleted); `test_determinism.py` and `test_import_guard.py` green.
- Each case in the Objective's table behaves as FS-132 v1.1 requires.
- `git diff --stat` touches only `engine/orders.py`, the test file(s) and the docs.
- Documentation updates done; status `COMPLETE`.

## Verification Checklist

1. `_h_effect`'s ammo charge no longer depends on `outcome.success`; it still sits after the
   resolver call and after the execute-time re-check's early return.
2. A forced miss leaves `ammo` at `N − S`; a destroyed-target engagement likewise; a hit
   unchanged at `N − S`.
3. The re-check failure path (`reason: "insufficient_ammo"`) still charges nothing
   (`test_queued_engagements_cannot_overdraw` unchanged and green).
4. No `power_w` mutation reappears (`grep` in `engine/`); a jam's payload carries no `ammo`.
5. Effect-log outcomes for a fixed seed are unchanged (test 4); replay equals live (test 5).
6. Full suite and both permanent gates (`test_determinism.py`, `test_import_guard.py`) green.

## Dependencies

`IP-1320` (`VERIFIED`). No package depends on `IP-1321`. `IP-1160` (`BLOCKED`, not authorized)
edits `engine/orders.py::_validate`, not `_h_effect`; no rebase concern.

## Risks

- **Tests or tutorials relying on a free miss** (FS-132 Risks v1.1). Task 3 searches; every
  shipped tutorial `engage` uses an effector with 1 round and fires once (checked `64c5058`:
  `00-training-basics`, `01-leo-isr-denial`, `05-da-asat-crisis`), so none issues a second strike.
- **Forced outcomes in tests.** Pₖ is random per seed; tests force the outcome with
  `_ForcedResolver` rather than depending on a lucky seed.
- **Old saves.** A save with a miss replays with the rounds charged (intended, FS-132 State
  Changes).

## Rollback Considerations

Revert the commit (restores the `outcome.success` term). No data migration and no persisted-format
change; saves replay under whichever rule the code carries.
