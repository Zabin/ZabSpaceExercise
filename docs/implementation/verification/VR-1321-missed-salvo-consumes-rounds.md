# VR-1321 — Verification Report: Missed Salvo Consumes Its Rounds: Charge Every Fired Engagement, Hit or Miss (FR-1480)

> **Document ID:** VR-1321
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1321](../packages/IP-1321-missed-salvo-consumes-rounds.md),
> [FS-132](../../features/FS-132-effect-resource-bounds.md) v1.1,
> [IP-1320](../packages/IP-1320-effect-resource-bounds.md) (`VERIFIED` via
> [VR-1320](VR-1320-effect-resource-bounds.md))
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1321`
> **Feature Mapping:** FS-132 v1.1 (`FR-1480`; amended AC of `FR-1460`)
> **Related Topics:** [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [VR-1320](VR-1320-effect-resource-bounds.md)/[VR-1052](VR-1052-order-param-hardening.md) (the
> "independently reproduce with fresh fixtures, check every boundary path including the one that
> must NOT trigger, don't just re-run" standard this report follows)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1321 — Missed Salvo Consumes Its Rounds: Charge Every Fired Engagement, Hit
  or Miss (`FR-1480`)
- **Version verified:** 1.0
- **Tree state verified:** commit `130535e` (branch `claude/chart-prompt-file-90hm9u`, read via a
  local branch `verify-ip1321` tracking `origin/claude/chart-prompt-file-90hm9u` — the named branch
  ref itself was held by a concurrent worktree). Implementing commit: `125329a` (2026-10-17,
  pipeline run #178).
- **Independence:** first verification pass; this session had no prior involvement in `125329a` or
  any prior `IP-1320`/`IP-1321` work (fresh session, as the task requires for this package).

## Result

**VERIFIED, clean — no findings against the package itself.** Every Definition of Done and
Verification Checklist item is confirmed against the actual tree, not the Implementation Summary.

The one-line change (`if cons and outcome.success:` → `if cons:` in `OrderSystem._h_effect`) was
read directly at `spacesim/engine/orders.py` lines 1077–1080: the charge now sits after the
resolver call (line 1062, so it covers a hit, a miss, and a resolved-but-"already destroyed" case
alike) and still strictly after the execute-time re-check's early `return` (lines 1053–1061), which
is untouched and still charges nothing on `insufficient_ammo`.

All four Objective-table cases were independently reproduced on **fresh fixtures** — a different
effector id (`SHOOTER` vs. the package's own `INT`), different target ids (`HOSTILE0`/`HOSTILE1`
vs. `RSAT0`/`RSAT1`), different seeds (101/202/303/404/505 vs. the package's 7), and a differently
laid-out orbit/world builder — never reusing `test_effect_resource_bounds.py`'s own
`_kinetic_world`/`_ForcedResolver`/`_engage` helpers:

1. **Forced miss** (`ForcedResolver(success=False)`, seed 101): `SHOOTER` ammo 3 → 2 after one
   1-round engagement; `HOSTILE0.health` stayed not-destroyed. Charged.
2. **Forced hit** (`ForcedResolver(success=True)`, seed 202): ammo 3 → 2, `HOSTILE0.health ==
   "destroyed"` — no regression from `IP-1320`'s already-`VERIFIED` hit-charging behaviour.
3. **Execute-time re-check failure — the one path that must NOT charge** (two queued 2-round
   engagements against a 2-round effector, seed 303, two distinct targets): final ammo `0`, never
   negative; exactly one effect-log record carries `reason == "insufficient_ammo"`; that record's
   own target's `health` was confirmed still not `"destroyed"` — the failed engagement never
   reached the resolver and charged genuinely nothing.
4. **Target already destroyed by a separate, earlier mechanism before the salvo's window opens**
   (real `ModerateEffectResolver`, seed 404, ammo 4): the engagement still executes, the resolver
   reports `achieved == "none"`, `success is False` (no roll possible against a dead target), and
   `SHOOTER` ammo still drops 4 → 3 — confirming FR-1480's Notes "every shot fired" interpretation
   is what is actually shipped, not an oversight.
5. **Replay determinism of a session containing a missed, charged salvo** (seed 505, ammo 2 → 1
   after a forced miss): `sim.replay().model_dump() == world.model_dump()` byte-for-byte, and the
   replayed world's `SHOOTER.resources.ammo` is still `1` — independently built, not trusted from
   the shipped `test_missed_salvo_replays_identically`.

The **"5 of 6 new tests failed first"** claim was independently re-derived, not merely re-run: the
fix was mechanically reverted in place (`if cons:` → `if cons and outcome.success:`), the new test
file re-run, and the file restored immediately after. Result: **exactly** the same 5 tests the
package names fail pre-fix (`test_missed_salvo_is_charged`,
`test_salvo_at_already_destroyed_target_is_charged`, `test_exact_salvo_charged_on_a_miss`,
`test_engagement_outcome_unchanged_and_charged_for_seed[2-none-False]`, and
`test_missed_salvo_replays_identically`), each failing with the expected `assert 2 == 1` /
`assert 2 == 0` shape; the seed-1 (hit) parametrization of
`test_engagement_outcome_unchanged_and_charged_for_seed` passes unchanged on both trees, exactly as
claimed. The working tree was confirmed clean (`git status --short`) before and after this
mechanical check — no residual edit.

`test_orders.py::test_kinetic_engage_requires_track_and_roe_then_spawns_debris`'s `ammo == 0`
assertion was read directly: it follows a *real-resolver* (not forced) engagement whose outcome is
asserted to be a **hit** (`health == "destroyed"`, debris and consequences recorded) before the
ammo check — a hit was always charged under both the old and new rule, so the assertion is
genuinely testing a hit-only scenario and remains correct by construction, not by coincidence.
`test_queued_engagements_cannot_overdraw` (the re-check-path test) is confirmed byte-unchanged by
this package's diff and still green.

Full suite **1022 passed, 3 skipped** — independently re-run, matching the implementer's claim
exactly (baseline 1016/3 + 6 new). Both permanent gates green, run by name (14/14).

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| All Tests to Add exist and pass; tests 1 and 2 were seen failing first. | `test_effect_resource_bounds.py` run by name: 19 collected, 19 passed. Independently re-derived "seen failing first" by mechanically reverting the fix and re-running: 5 of the 6 new tests fail (`test_missed_salvo_is_charged`, `test_salvo_at_already_destroyed_target_is_charged`, `test_exact_salvo_charged_on_a_miss`, `test_engagement_outcome_unchanged_and_charged_for_seed[2-none-False]`, `test_missed_salvo_replays_identically`); `test_engagement_outcome_unchanged_and_charged_for_seed[1-destroy-True]` (the hit case) passes on arrival — matching the package's header exactly, including which specific parametrization passes. Fix restored immediately after (`git checkout -- spacesim/engine/orders.py`); tree confirmed clean. | ✅ Pass |
| Full suite green; any test that asserted the old hit-only rule now asserts the new rule (none deleted); `test_determinism.py` and `test_import_guard.py` green. | 1022 passed, 3 skipped — independently re-run (see Test run below). No existing test deleted; `git show 125329a --stat` shows only additions to `test_effect_resource_bounds.py` (70 insertions, 0 deletions in that file) — no existing assertion was touched, matching the package's own Task 3 finding that no fixture needed to change. Gates 14/14 by name. | ✅ Pass |
| Each case in the Objective's table behaves as FS-132 v1.1 requires. | Independently reproduced on fresh fixtures distinct from the implementer's own (hit, miss, destroyed-target, re-check-failure) — see Result §1–§4 above. | ✅ Pass |
| `git diff --stat` touches only `engine/orders.py`, the test file(s) and the docs. | `git show 125329a --stat`: `CLAUDE.md`, `ROADMAP.md`, `docs/features/FS-132-effect-resource-bounds.md`, `docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`, `docs/implementation/packages/IP-1321-missed-salvo-consumes-rounds.md`, `docs/requirements/03-requirements-traceability-matrix.md`, `spacesim/engine/orders.py`, `spacesim/tests/test_effect_resource_bounds.py` — 9 files, all named or clearly documentation. No other `engine/` file touched. | ✅ Pass |
| Documentation updates done; status `COMPLETE`. | RTM `FR-1480`/`FR-1460` rows, `FS-132` Referenced By, `CLAUDE.md` code map, MBP row + counts, `packages/INDEX.md`, ROADMAP row all confirmed updated prior to this report (see Traceability audit). Status was `COMPLETE` at the start of this verification pass, as required for eligibility. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| 1. `_h_effect`'s ammo charge no longer depends on `outcome.success`; still sits after the resolver call and after the execute-time re-check's early return. | Read directly (`orders.py:1047–1080`): the re-check's early `return` is at line 1061 (before the resolver is ever called); `self.resolver.resolve(...)` runs at line 1062, the effect-log append at 1063–1070, and the charge block `if cons:` at line 1077 — strictly after both. No `outcome.success` term in the charge condition. | ✅ Pass |
| 2. A forced miss leaves `ammo` at `N − S`; a destroyed-target engagement likewise; a hit unchanged at `N − S`. | Independently reproduced on fresh fixtures, all three cases (Result §1, §2, §4 above): miss 3→2, hit 3→2, destroyed-target 4→3, all exactly `N − S` for `S = 1`. | ✅ Pass |
| 3. The re-check failure path (`reason: "insufficient_ammo"`) still charges nothing (`test_queued_engagements_cannot_overdraw` unchanged and green). | Read `git show 125329a` diff: that test is untouched (0 lines changed). Re-run: passes. Independently reproduced on a fresh two-target, two-queued-salvo fixture (Result §3 above): final ammo floors at exactly `0` (never negative), the failed record's target is untouched, and only one resolver call occurred for the two queued orders. | ✅ Pass |
| 4. No `power_w` mutation reappears (`grep` in `engine/`); a jam's payload carries no `ammo`. | `grep -n "power_w" spacesim/engine/orders.py`: all five hits are reads (success-probability math, lines 781/789) or comments (lines 814, 1081–1082) — no `-=`/assignment on `resources.power_w` anywhere in `engine/`. Jam's `consume` payload (read at `orders.py` jam plan) carries no `ammo` key, confirmed unchanged from `IP-1320`. | ✅ Pass |
| 5. Effect-log outcomes for a fixed seed are unchanged (test 4); replay equals live (test 5). | Re-run `test_engagement_outcome_unchanged_and_charged_for_seed` (seeds 1, 2): outcomes `(destroy, True)`/`(none, False)` as pinned, unchanged by the charge condition. Independently reproduced replay determinism on a fresh fixture, seed 505 (Result §5 above): `model_dump()` byte-identical. | ✅ Pass |
| 6. Full suite and both permanent gates (`test_determinism.py`, `test_import_guard.py`) green. | 1022 passed, 3 skipped; gates 14/14 (`test_determinism.py` 6, `test_import_guard.py` 8), run by name together. See Test run below. | ✅ Pass |

## Requirements audit

| ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| `FR-1480` | `engine/orders.py::OrderSystem._h_effect` (charge block, line 1072, `outcome.success` term removed) | `spacesim/tests/test_effect_resource_bounds.py` (`test_missed_salvo_is_charged`, `test_salvo_at_already_destroyed_target_is_charged`, `test_exact_salvo_charged_on_a_miss`, `test_engagement_outcome_unchanged_and_charged_for_seed`, `test_missed_salvo_replays_identically`); independently re-derived on fresh fixtures (Result §1–§5 above) | RTM row names FS-132 (v1.1), the test names and `IP-1321` with an accurate one-line description — confirmed accurate by direct read, corrected to `VERIFIED` by this report | ✅ Pass |
| `FR-1460` (amended AC) | Same change; the bound, re-check and Postcondition untouched (confirmed in Checklist item 3) | `spacesim/tests/test_effect_resource_bounds.py` (all `IP-1320` tests re-run green, unchanged) | RTM row's `IP-1321` annotation ("amended AC … by `IP-1321`") — confirmed accurate, corrected to `VERIFIED` by this report | ✅ Pass |

## Test run

Commands run, exact:

```
python3 -m pytest spacesim/tests/test_effect_resource_bounds.py -v
python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py -v
python3 -m pytest
```

- `test_effect_resource_bounds.py`: **19 passed** (19 collected).
- Permanent gates by name: **14 passed** (`test_determinism.py` 6, `test_import_guard.py` 8).
- Full suite: **1022 passed, 3 skipped, 1 warning (1025 collected) in ~130s** — matches the
  implementer's claimed counts exactly (baseline 1016 passed / 3 skipped + 6 new).
- Mechanical pre-fix re-derivation (fix reverted in place, test file re-run, fix restored): **5
  failed, 14 passed** — matches the package's "5 of 6 failed first" claim exactly, including which
  5. Working tree confirmed clean before and after (`git status --short`).

## Scope audit

`git show 125329a --stat` (9 files changed, 97 insertions, 9 deletions): `CLAUDE.md`,
`ROADMAP.md`, `docs/features/FS-132-effect-resource-bounds.md`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`,
`docs/implementation/packages/IP-1321-missed-salvo-consumes-rounds.md`,
`docs/requirements/03-requirements-traceability-matrix.md`, `spacesim/engine/orders.py`,
`spacesim/tests/test_effect_resource_bounds.py`. All within the package's declared `Files to
Modify` plus the named documentation set. No `engine/` file other than `orders.py` touched; no
`Files to Create` claimed (none declared, none created). No excursion.

## Findings

None against the package.

## Traceability audit

- `docs/requirements/03-requirements-traceability-matrix.md`: `FR-1480`/`FR-1460` rows named
  FS-132 (v1.1), the test file/names and `IP-1321` — confirmed accurate; this report updates both
  cells' `IP-1321` annotation from `COMPLETE 2026-10-17, awaiting 09` to `VERIFIED 2026-10-17 via
  VR-1321`.
- `docs/implementation/00-master-build-plan.md`: the `IP-1321` row and the Package Status footer
  lines are updated `COMPLETE → VERIFIED` by this report (see commit); the package-count tally is
  corrected to drop `IP-1321` from the `COMPLETE` bucket into `VERIFIED`.
- `docs/implementation/packages/INDEX.md`, `ROADMAP.md`,
  `docs/features/FS-132-effect-resource-bounds.md` (`Referenced By`), `IP-1321`'s own header: all
  updated to `VERIFIED` by this report.
- `docs/pipeline/backlog.md`: `BL-0249` closed to `DONE` per its own text ("Closes `DONE` when the
  package is `VERIFIED`"). `BL-0276`'s revisit trigger ("`IP-1321` reaching `VERIFIED`") fires:
  `DEFERRED → SCHEDULED`. `BL-0275` (the `FEAT-1400` catalog row not listing `FR-1480`) is
  unrelated to this package's own correctness and is left exactly as found — this verification's
  findings do not bear on it.

## Pipeline position

Stage 09 — Package Verification. Upstream: `08-code-implementation` (run #178, commit `125329a`).
Downstream: no package depends on `IP-1321`. `08-training-manual-authoring` is owed `BL-0276`
(now `SCHEDULED`) for the `RED-5`/§15.1 manual-impact fix. The project's remaining tranche
(`IP-1064` `IN PROGRESS`, `IP-1311` `READY`, `IP-1160` `BLOCKED`) continues per the Master Build
Plan's own status footer.
