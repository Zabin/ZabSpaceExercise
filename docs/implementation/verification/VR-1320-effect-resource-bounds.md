# VR-1320 — Verification Report: Effect Resource Bounds: Salvo Bounded by Remaining Rounds (Validation and Execution); Jamming Leaves the Power Rating Alone (FR-1460, FR-1470)

> **Document ID:** VR-1320
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1320](../packages/IP-1320-effect-resource-bounds.md),
> [FS-132](../../features/FS-132-effect-resource-bounds.md) v1.0,
> [IP-1051](../packages/IP-1051-spacecraft-operations-effects-console.md) (`VERIFIED`),
> [IP-1052](../packages/IP-1052-order-param-hardening.md) (`VERIFIED`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1320`
> **Feature Mapping:** FS-132 v1.0 (`FR-1460`, `FR-1470`)
> **Related Topics:** [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js),
> [ADR-0037](../../architecture/adr/ADR-0037-jammer-power-is-a-rating-not-a-consumable.md);
> [VR-1310](VR-1310-load-time-vignette-validation.md)/[VR-1052](VR-1052-order-param-hardening.md)
> (the "independently reproduce on fresh fixtures, confirm by direct state read, not just status"
> standard this report follows)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1320 — Effect Resource Bounds: Salvo Bounded by Remaining Rounds (Validation
  and Execution); Jamming Leaves the Power Rating Alone (`FR-1460`, `FR-1470`)
- **Version verified:** 1.0
- **Tree state verified:** commit `f93a299` (branch `claude/chart-prompt-file-90hm9u`). Implementing
  commit: `ed9cdcf` (2026-10-17, pipeline run #154); ledger-only follow-up `f93a299` (run #154's own
  journal/backlog entry) layered on top, untouched by this verification.
- **Independence:** first verification pass. Fresh session with no prior involvement in `ed9cdcf` or
  any prior `IP-1320` work.

## Result

**VERIFIED, clean — no findings against the package itself.** Every Definition of Done and
Verification Checklist item is confirmed against the actual tree, not the Implementation Summary.
The salvo-overdraft fix is independently confirmed at **all three** claimed gate points — `dry_run`,
`issue`, and execution — on a fresh vignette (`coa-china-md`, seed `999999`, distinct from the
implementer's own `leo-isr-denial`/`da-asat-crisis` fixtures) for the preview/issue gates, and on a
hand-built fixture with different asset ids, ammo count and seed (`RQ-SHOOTER`/`HOSTILE-A`/
`HOSTILE-B`, seed `271828`) for the execute-time re-check, because `coa-china-md`'s own orbital
geometry offers only one direct-ascent-reachable LEO target (a second target in GEO/MEO is
correctly refused `no_window`, an unrelated geometry rejection — not a defect). On both fixtures the
effector's `resources.ammo` was read directly from `WorldState`, never inferred from the HTTP/order
status alone, and never went negative; the rejected issue left the order queue, scheduler and
ammo count byte-identical to before. The jammer-power-unchanged claim is independently confirmed
across **three sequential** jam orders (`barrage`/`spot`/`sweep`) on the same fresh fixture, reading
`resources.power_w` directly after each one — it never moved from its authored rating (`0.0`). The
failed-salvo and failed-maneuver log-entry shapes were compared directly on two fresh hand-built
fixtures: both carry `{t, template, target, achieved: "failed", success: False}`; the ammo record
additionally carries `category` (every engage/jam effect-log record carries it; maneuver records
never do) and `reason` (additive, per Design Decision 2) — a reasonable reading of "the same way,"
not a byte-identical schema across two different event kinds (see Independent reproduction §3).
OQ3's all-or-nothing behaviour (a missed/rejected salvo costs no rounds) is confirmed unchanged and
accurately described as out of scope. The `test_salvo_float_truncation_unchanged` fixture fix is
confirmed to be exactly the one-line ammo bump the package describes, with the 2.7→2 truncation
assertion untouched and still meaningfully exercised (ammo=3 keeps the bound's own check,
`2 > 3`, false, so the test still isolates truncation). Full suite 985 passed, 3 skipped (988
collected) — independently re-run, matching the implementer's claim exactly; both permanent gates
green (14/14), run by name. The implementing diff touches exactly the files the package names,
confirmed by reading `git show ed9cdcf --stat` and the diff itself line by line.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| All Tests to Add exist and pass; tests 1, 3, 4 and 5 were seen failing first. | `test_effect_resource_bounds.py` run by name: 13 collected, 13 passed. The package's own header states 6 failed first (oversized salvo, queued overdraw, successful jam at 0 W and 250 W, the two seeded jam-outcome tests' power assertion) and 7 passed on arrival; this matches the file's own structure (tests 1/4/5(×4 parametrized)/6(×2) cover exactly those cases) and is architecturally necessary — before the diff, `_validate` had no `insufficient_ammo` branch and `_h_effect` subtracted `power_w` on every successful jam, so those assertions could not have passed. | ✅ Pass |
| Full suite green, with no previously passing test now failing except the one fixture adjustment named above; `test_determinism.py` and `test_import_guard.py` green. | 985 passed, 3 skipped (988 collected) — independently re-run, see Test run below. Gates 14/14 by name. `git show ed9cdcf --stat` confirms the only test-file changes are the new `test_effect_resource_bounds.py` and the single named line in `test_order_param_hardening.py`. | ✅ Pass |
| Each case in the Objective's reproduction table behaves as FS-132 requires. | Independently reproduced on fresh fixtures distinct from the implementer's own — see Independent reproduction §1–§3. | ✅ Pass |
| `git diff --stat` touches only `engine/orders.py`, `static/app.js`, the two test files and the docs. | `git show ed9cdcf --stat`: `CLAUDE.md`, `ROADMAP.md`, `docs/features/FS-132-effect-resource-bounds.md`, `docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`, `docs/implementation/packages/IP-1320-effect-resource-bounds.md`, `docs/requirements/03-requirements-traceability-matrix.md`, `spacesim/engine/orders.py`, `spacesim/tests/test_effect_resource_bounds.py`, `spacesim/tests/test_order_param_hardening.py`, `spacesim/ui_web/static/app.js` — 11 files, all named or clearly documentation. No `engine/` file outside `orders.py` touched. | ✅ Pass |
| Documentation updates done; status `COMPLETE`. | RTM `FR-1460`/`FR-1470` rows, `FS-132` Referenced By, `CLAUDE.md` code map, MBP row + counts, `packages/INDEX.md`, ROADMAP row all confirmed updated prior to this report (see Traceability audit). Status was `COMPLETE` at the start of this verification pass, as required for eligibility. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| 1. `_validate` returns `insufficient_ammo` for a consumed salvo above the remaining rounds, after `no_ammo` and before the weapons-quality check; `dry_run` and `issue` agree. | Read directly (`orders.py:625-641`): `no_ammo` at line 635, the new `insufficient_ammo` check at 637-638, the weapons-quality track check at 639-641 — order confirmed. Both `issue` (line 250) and `dry_run` (line 260) call the shared `_plan` → `_validate` path (lines 271-276). Independently reproduced agreement on a fresh fixture (`coa-china-md`, seed 999999): both rejected `insufficient_ammo` for the same oversized order. | ✅ Pass |
| 2. `_validate` and the engage plan's `consume` use one shared rounds computation. | `_engage_rounds` (`orders.py:147-154`) is called at both line 637 (`_validate`) and line 814 (the engage plan's `consume` entry) — the same function, confirmed by direct read, not duplicated logic. | ✅ Pass |
| 3. `_h_effect` re-checks rounds before resolving, logs the failed record with `reason: "insufficient_ammo"`, and charges nothing on that path. | Read directly (`orders.py:1006-1020`): the re-check and failed-record append happen before `self.resolver.resolve(...)` (line 1021) is ever called, and `return`s immediately — no charge, no RNG draw. Independently reproduced on the fresh `RQ-SHOOTER`/`HOSTILE-A`/`HOSTILE-B` fixture (seed 271828): the second of two queued 2-round engagements against a 3-round effector produced exactly one `achieved: "failed"` record with `reason: "insufficient_ammo"`, its resolver was never called (`resolver.calls` check analogue — confirmed via the forced resolver only being invoked once), and its target's `health` stayed untouched (not `"destroyed"`). | ✅ Pass |
| 4. No code path subtracts from `resources.power_w` (`grep` in `engine/`). | `grep -rn "power_w" spacesim/engine/` shows only: `jam.py`'s pure helper functions (`effective_radius_km`, `power_draw_w` — neither called from the consumption path any more), `entities.py`'s field declaration, and `orders.py`'s own `power_w` *parameter* reads (success-probability math, lines 736/744) plus the two IP-1320 comments explaining its absence. No `-=` or mutation of `resources.power_w` anywhere in `engine/`. Independently confirmed live: across three sequential jam orders (`barrage`/`spot`/`sweep`) on a fresh fixture, `resources.power_w` read `0.0` before and after every one. | ✅ Pass |
| 5. `test_salvo_float_truncation_unchanged` still asserts `consume.ammo == 2`; only its effector's rounds changed. | Read directly (`test_order_param_hardening.py:264-269`): the assertion `_scheduled(mgr.osys, order.id)["consume"]["ammo"] == 2` is byte-identical to before the diff (confirmed by `git show ed9cdcf` diff, which adds only the two comment lines and `mgr.world.assets["RED-ASAT"].resources.ammo = 3`). The test still exercises truncation: `salvo_n=2.7` → `_engage_rounds` computes `max(1, int(2.7)) == 2`, and with `ammo=3` the new bound (`2 > 3` is false) does not interfere, so the assertion's pass still depends entirely on the truncation (`int(2.7) == 2`), not on the new bound happening to let it through for an unrelated reason. | ✅ Pass |
| 6. `REASON_TIPS` has an `insufficient_ammo` key. | Read directly (`app.js` `REASON_TIPS`, confirmed in the `ed9cdcf` diff): `insufficient_ammo: "Salvo is larger than the rounds this effector has left — reduce the salvo."` present, placed next to `no_ammo` per the comment above the table. (Browser GUI unverified headless, per `CLAUDE.md`; checked by inspection as the package itself specifies.) | ✅ Pass |
| 7. Full suite and both permanent gates (`test_determinism.py`, `test_import_guard.py`) green. | 985 passed, 3 skipped (988 collected); `test_determinism.py` 6 passed, `test_import_guard.py` 8 passed, run by name together (14 passed). See Test run below. | ✅ Pass |

## Requirements audit

| ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| `FR-1460` | `engine/orders.py::_validate` (lines 637-638, after `no_ammo`/before WQ) + `_h_effect` (1012-1020, execute-time re-check) | `spacesim/tests/test_effect_resource_bounds.py` (tests 1-4, 7); independently re-derived on a fresh fixture (§1 below) | RTM row names FS-132, the test file and `IP-1320` with a one-line description of where in the code — confirmed accurate by direct read, corrected to `VERIFIED` by this report | ✅ Pass |
| `FR-1470` | `engine/orders.py` jam plan (no `power_w` entry in `consume`, line ~767) + `_h_effect` (no `power_w` branch, line 1037) | `spacesim/tests/test_effect_resource_bounds.py` (test 5, 6); independently re-derived across three sequential orders on a fresh fixture (§2 below) | Same row structure as `FR-1460`; confirmed accurate, corrected to `VERIFIED` | ✅ Pass |

## Test run

Commands run, exact:

```
python3 -m pytest spacesim/tests/test_effect_resource_bounds.py -v
python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py -v
python3 -m pytest
```

- `test_effect_resource_bounds.py`: **13 passed** (13 collected).
- Permanent gates by name: **14 passed** (`test_determinism.py` 6, `test_import_guard.py` 8).
- Full suite: **985 passed, 3 skipped, 1 warning (988 collected) in 119.45s** — matches the
  implementer's claimed counts exactly (baseline 972 passed / 3 skipped / 975 collected, +13 new).

## Scope audit

`git show ed9cdcf --stat` (11 files changed, 259 insertions, 17 deletions): `CLAUDE.md`,
`ROADMAP.md`, `docs/features/FS-132-effect-resource-bounds.md`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`,
`docs/implementation/packages/IP-1320-effect-resource-bounds.md`,
`docs/requirements/03-requirements-traceability-matrix.md`, `spacesim/engine/orders.py`,
`spacesim/tests/test_effect_resource_bounds.py` (new), `spacesim/tests/test_order_param_hardening.py`,
`spacesim/ui_web/static/app.js`. All within the package's declared `Files to Create`/`Files to
Modify` plus the named documentation set. No excursion.

## Independent reproduction

### §1 — Salvo overdraft, all three gate points, fresh fixtures

Fixture: vignette `coa-china-md` (never used by the implementer's own tests or reproduction),
seed `999999`, shooter `RED-ASAT` (ammo 2, not the implementer's `ammo=1`/`ammo=2` fixtures'
exact ids), target `BLUE-ISR-PRIMARY`.

- **(a) `dry_run`:** an `engage` with `salvo_n=3` against a 2-round effector → `rejected`,
  `fail_reason == "insufficient_ammo"`.
- **(b) `issue`:** the identical order, issued → `rejected`, `fail_reason == "insufficient_ammo"`.
  Direct state read: `world.assets["RED-ASAT"].resources.ammo` was `2` before and `2` after the
  rejected issue (not inferred from the returned status). The scheduler's pending-event count was
  identical before and after (61 → 61) — nothing was scheduled by the rejection.
- **(c) execution:** `coa-china-md`'s own geometry offers only one LEO target a ground-based
  direct-ascent interceptor can reach in this window (a second, GEO-based target was correctly
  refused `no_window` — a geometry rejection, not a defect, and not evidence against the fix). The
  execute-time re-check (W3: two queued engagements that together exceed ammo) was therefore
  reproduced on a small hand-built fixture using different ids, ammo and seed than
  `test_effect_resource_bounds.py`'s own `_kinetic_world` (`INT`/`RSAT0`/`RSAT1`, ammo 2, seed 7):
  here, `RQ-SHOOTER` (ammo 3), targets `HOSTILE-A`/`HOSTILE-B`, seed `271828`, two salvo-2
  engagements queued before either executes. Result, read directly from `WorldState`: final ammo
  `1` (never negative), effect log carries exactly one `achieved: "destroy"` record (HOSTILE-A,
  resolved, target destroyed) and exactly one `achieved: "failed", success: False,
  reason: "insufficient_ammo"` record (HOSTILE-B) — HOSTILE-B's `health` was confirmed *not*
  `"destroyed"`, i.e. the failed engagement never resolved and had no side effect.

### §2 — Jammer power_w unchanged, three sequential orders, fresh fixture

Same `coa-china-md`/seed-999999 session. `RED-JAM-PNT` (default, unauthored `power_w`, i.e.
`0.0` — the vignette never sets it, same as the implementer's `0.0` case but a different asset
id/vignette) against `BLUE-PNT`. Three sequential `jam` orders (`barrage`, `spot`, `sweep`), each
issued, advanced to execution, and `resources.power_w` read directly from `WorldState`
immediately after each one: `0.0` → `0.0` → `0.0` → `0.0`. The rating never moved across three
orders in sequence, not just one.

### §3 — Failed-salvo vs. failed-maneuver log-entry shape

Failed-salvo record (from §1c): `{"t": 0, "template": "da_asat_mrbm_kkv", "category":
"direct_ascent", "target": "HOSTILE-B", "achieved": "failed", "success": False, "reason":
"insufficient_ammo"}`.

Failed-maneuver record, built on a fresh hand-built fixture (`SAT-X`, 100 m/s Δv budget, ground
station `GS-X`, seed `161803` — distinct from `test_orders.py`'s own `SAT`/`GS`/seed-default
fixture): two 60 m/s prograde maneuvers queued before either executes (each individually within
budget, together they are not). Result: `{"t": 0, "template": "maneuver", "target": "SAT-X",
"achieved": "failed", "success": False}`.

Both records share `{t, template, target, achieved: "failed", success: False}` — the four fields
FS-132 OQ2 and `_h_maneuver`'s own re-validation record actually carry. The ammo record
additionally carries `category` (every engage/jam effect-log entry carries it, success or
failure — maneuver entries structurally never do, since `maneuver` is a different handler/event
kind with its own record shape) and `reason` (additive, confirmed by Design Decision 2's own
wording — "the extra `reason` key is additive; no effect-log reader keys on its absence"). This is
parity in the sense FS-132 OQ2 asked for — "the failed-execution record should follow the
existing failed-manoeuvre shape... (template, target, achieved = failed, success = false)" — not
a byte-identical schema across two different event kinds, and the package never claimed the
latter.

### §4 — OQ3 (all-or-nothing) accuracy

Confirmed in §1c: the failed engagement charged **zero** rounds (final ammo `1`, not `0` — a
successful salvo of 2 from 3 would leave 1; a charged-on-failure rule would have left ammo
negative or the same `1` only coincidentally, but the code path at `orders.py:1012-1020` `return`s
before reaching the charging step at line 1033-1036, which runs only `if cons and
outcome.success`). The as-built rule — rounds are charged only on success, and a rejected/failed
salvo is entirely uncharged, never partially — is unchanged and accurately described. This does
not bear on `BL-0249`'s routing to `04` (a separate, non-blocking requirements question about
*whether* that rule should change) and that entry is left untouched.

## Findings

None against the package.

## Traceability audit

- `docs/requirements/03-requirements-traceability-matrix.md`: `FR-1460`/`FR-1470` rows named
  FS-132, `test_effect_resource_bounds.py` and `IP-1320` — confirmed accurate; this report updates
  both cells' `IP-1320` annotation from `COMPLETE 2026-10-17, awaiting 09` to `VERIFIED 2026-10-17
  via VR-1320`.
- `docs/implementation/00-master-build-plan.md`: the `IP-1320` row and the two Package Status
  footer lines are updated `COMPLETE → VERIFIED` by this report (see commit).
- `docs/implementation/packages/INDEX.md`, `ROADMAP.md`, `docs/features/FS-132-effect-resource-bounds.md`
  (`Referenced By`), `IP-1320`'s own header: all updated to `VERIFIED` by this report.
- `docs/pipeline/backlog.md`: `BL-0238`/`BL-0245` closed to `DONE` (both named `FR-1460`/`FR-1470`
  reaching `IP-1320` `VERIFIED` as their terminal step); `BL-0250`'s revisit trigger ("`IP-1320`
  reaches `VERIFIED`") fires: `DEFERRED → SCHEDULED`.

## Pipeline position

Stage 09 — Package Verification. Upstream: `08-code-implementation` (run #154, commit `ed9cdcf`).
Downstream: no other package depends on `IP-1320`; `09-training-manual-review`/
`10-integration-review` pick this epic's thread up per the pipeline journal's own Position block.
