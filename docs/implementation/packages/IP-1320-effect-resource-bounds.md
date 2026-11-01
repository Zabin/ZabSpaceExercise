# IP-1320 — Effect Resource Bounds: Salvo Bounded by Remaining Rounds (Validation and Execution); Jamming Leaves the Power Rating Alone (FR-1460, FR-1470)

> **Package ID:** IP-1320
> **Version:** 1.0
> **Status:** VERIFIED 2026-10-17 ([VR-1320](../verification/VR-1320-effect-resource-bounds.md), fresh session; COMPLETE before that).
> **Earlier status record (superseded by the line above; retained as history, unedited):** 🔵 COMPLETE — 2026-10-17, `08-code-implementation`, pipeline run #154, awaiting a
> **fresh-session** `09-package-verification`. `engine/orders.py`: `_engage_rounds` (shared by
> `_validate`'s new `insufficient_ammo` check — after `no_ammo`, before the weapons-quality gate —
> and the engage plan's `consume`); `_h_effect` re-checks rounds before resolving (failed record
> with `reason: "insufficient_ammo"`, no resolve/RNG/charge); the jam plan emits no `power_w`
> consumption and `_h_effect` has no `power_w` branch (unused `power_draw_w` import dropped from
> the jam branch). `app.js` `REASON_TIPS.insufficient_ammo`. `test_salvo_float_truncation_unchanged`:
> effector rounds raised to 3, assertion unchanged. Tests: `test_effect_resource_bounds.py`
> (13 collected). **6 seen failing first** (oversized salvo; queued overdraw; successful jam at
> 0 W and 250 W; the two seeded jam-outcome tests on their power assertion). 7 passed on arrival
> as planned or by as-built behaviour: exact salvo, absent/`None` salvo ×2, zero rounds, replay,
> and the two *failed*-jam cases (as built, a failed jam already charged nothing). Task 5: every
> shipped tutorial `engage` uses the default salvo of 1; no test asserted a drifted `power_w`.
> Full suite 985 passed / 3 skipped (988 collected, JUnit; baseline 972/3/975); gates 14/14.
> *(Was 🟢 READY — authored 2026-10-17 by `07-implementation-planning`, pipeline run #153.)*
> Every dependency is `VERIFIED`. **Authorization (MSTR-006 §3):** this package falls under the
> project owner's standing pre-authorization of 2026-10-11 for the packages this iteration
> reaches (same precedent as `IP-1310`/`IP-1052`/`IP-1041`). Authoring the package is not itself
> the authorization; that standing decision is.
> **Dependencies:** [FS-132](../../features/FS-132-effect-resource-bounds.md) v1.0 (the spec).
> [IP-1051](IP-1051-spacecraft-operations-effects-console.md) (engage/jam effect paths) and
> [IP-1052](IP-1052-order-param-hardening.md) (the param shape check this bound runs after) are
> `VERIFIED`.
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0238`, `BL-0245`
> **Produces:** an effector that can never be driven below zero rounds — refused at preview and
> issue, and re-checked at execution — and a jammer whose power rating never changes.
> **Feature Reference:** [FS-132 — Effect Resource Bounds](../../features/FS-132-effect-resource-bounds.md)
> (`FEAT-1400` slice)
> **Related Topics:** [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js),
> [ADR-0037](../../architecture/adr/ADR-0037-jammer-power-is-a-rating-not-a-consumable.md)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package (forward design) for two Must leaves baselined 2026-10-16/17. It decides
FS-132's two `07`-level Open Questions (1: reason code; 2: failed-execution record).*

---

## Package ID

IP-1320 (FS-132 → `IP-1320`, the FS-1xx → `IP-1xx0` convention; `IP-1310` is FS-131's).

## Title

Effect Resource Bounds: salvo bounded by remaining rounds at validation and execution; jamming
leaves the jammer's power rating unchanged.

## Objective

**Reproduction at `c10bbf3`** (code reads in this run; the ammunition case was reproduced live in
run #142 on `da-asat-crisis` seed 142):

| Case | As built |
|---|---|
| Effector with 1 round, `engage` with `salvo_n: 5` | `_validate` passes (only `ammo < 1` is refused); a successful engagement leaves `ammo = -4` |
| Effector with 2 rounds, two 2-round engagements queued | both pass validation; `_h_effect` has no execute-time re-check, so the second success leaves `ammo = -2` |
| Successful `jam` from a jammer rated 0 W (the default) | `_h_effect` subtracts `power_draw_w(...)` from `resources.power_w`, which goes negative |

After this package:

- an engagement whose consumed salvo exceeds the remaining rounds is rejected `insufficient_ammo`
  by `dry_run` and `issue` alike;
- at execution, an engagement the rounds no longer cover does not resolve and is logged as failed;
- a jam never changes `resources.power_w`.

## Feature Reference

[FS-132](../../features/FS-132-effect-resource-bounds.md) v1.0 — System Behaviour 1–5, State
Changes, Error Handling, Acceptance Criteria 1–7. Open Question 3 (whether a *missed* salvo should
consume rounds) is out of scope (`BL-0249`, routed to `04`); the as-built rule — rounds are
charged only on success — is kept.

## Requirements Covered

| ID | How |
|---|---|
| `FR-1460` | Validation bound in `_validate` (preview == issue) plus the execute-time re-check in `_h_effect`, so ammunition is never negative after an engagement executes. |
| `FR-1470` | `_h_effect` stops subtracting from `resources.power_w`; the jam plan stops emitting a `power_w` consumption. |

This matches FS-132's Requirements Implemented exactly; none added, none dropped.

## Architecture Components

- **C1 Simulation Engine** (`engine/orders.py` — `OrderSystem._validate`, the jam and engage
  branches of the effect planner, `_h_effect`): the only behaviour change.
- **C4 Operator Console** (`ui_web/static/app.js` `REASON_TIPS`): one new tip.
- **C2 Session Layer**: unchanged — `validate_order` and `issue` already relay `fail_reason`.

The engine import boundary is unchanged. No new module.

## Interfaces

- **INT-0008** (SessionManager → OrderSystem): `issue`/`dry_run` gain one possible
  `fail_reason`, `insufficient_ammo`. Shape unchanged.
- **INT-0004** (Operator ↔ Console): the tip text for the new reason.

### Design Decisions

1. **Reason code (FS-132 OQ1): a new `insufficient_ammo`.** It mirrors `insufficient_delta_v`
   (the `FR-1310` analogue) and keeps `no_ammo` meaning "no rounds at all". Check order inside the
   `engage` branch of `_validate` is unchanged and extended: ROE → `no_ammo` (`ammo < 1`) →
   **`insufficient_ammo`** (`max(1, salvo) > ammo`) → weapons-quality track.
   - The salvo figure is the one the consumption step charges: `max(1, int(salvo_n))`, with
     `salvo_n` defaulting to 1 when absent or `None` (IP-1052's "null = absent" rule). The param
     shape check (`_order_params_ok`) already ran first, so `int(...)` cannot fail.
   - Factor the "rounds this engagement consumes" computation into one private helper used by both
     `_validate` and the engage plan's `consume` entry, so they cannot drift.
2. **Execute-time re-check (FS-132 Behaviour 2, OQ2).** At the top of `_h_effect`, before
   `self.resolver.resolve(...)`: if the payload's `consume` carries `ammo`, and the actor exists
   and holds fewer rounds than that, append one effect-log record and return without resolving,
   charging, or drawing from the RNG. The record mirrors `_h_maneuver`'s failed re-validation:
   `{"t", "template": effect.template, "category": effect.category, "target": effect.target,
   "achieved": "failed", "success": False, "reason": "insufficient_ammo"}`. The extra `reason` key
   is additive; no effect-log reader keys on its absence (the log is read only through
   `WorldState` dumps, god view, saves and the AAR snapshot).
3. **Jam power (FS-132 Behaviour 4, ADR-0037).** Remove the `power_w` entry from the jam plan's
   `consume` dict, and remove the `power_w` branch from `_h_effect`'s consumption step. The jam's
   `success_prob`, footprint, `link_target` and `EffectInstance` are untouched, and so is the RNG
   sequence (consumption ran after resolution and drew nothing).
4. **Determinism.** The validation bound is a pure comparison. The execute-time re-check depends
   only on world state at that event, so replay reproduces it. For any history that did not
   overdraw before, the event stream and RNG draws are identical to today's.
5. **Scope boundaries.** No rating enforcement for jams (ADR-0037). No zero/negative/fractional
   salvo range rule (`CR-25`; the existing `test_salvo_float_truncation_unchanged` behaviour —
   2.7 → 2 rounds — stays). No change to whether a missed salvo consumes rounds (`BL-0249`). Saved
   sessions that already carry negative values load and replay unchanged.

## Files to Create

- `spacesim/tests/test_effect_resource_bounds.py`.

## Files to Modify

Each was checked against the tree at `c10bbf3`:

- `spacesim/engine/orders.py`:
  - `_validate` (starts line 584): the `engage` branch (lines 615–628, `no_ammo` at 625) gains the
    `insufficient_ammo` check per Design Decision 1.
  - The effect planner's jam branch (`consume` built at lines 757–758): drop the `power_w` entry.
  - The effect planner's engage branch (`salvo_n` at 769, `consume` at 802): use the shared
    rounds helper.
  - `_h_effect` (starts line 994; consumption at 1008–1015): the execute-time re-check before
    resolution, and removal of the `power_w` branch.
- `spacesim/ui_web/static/app.js`: `REASON_TIPS` (lines 166–180) gains
  `insufficient_ammo` (for example "Salvo is larger than the rounds this effector has left —
  reduce the salvo."). Keys mirror `_validate` verbatim, per the comment above the table.
- `spacesim/tests/test_order_param_hardening.py`: `test_salvo_float_truncation_unchanged`
  (line 264) issues a 2.7 salvo from `leo-isr-denial`'s `RED-ASAT`, which holds **1** round, so the
  new bound would reject it. Give that test's effector enough rounds (for example set
  `mgr.world.assets["RED-ASAT"].resources.ammo = 3` in the test) so it keeps testing what it is
  named for — truncation — and nothing else. Do not change its assertion.

## Implementation Tasks

1. Mark the package `IN PROGRESS` (header, MBP row, `packages/INDEX.md`, ROADMAP) before editing.
2. Write the tests below and see each new-behaviour test fail first (1, 3, 4, 5); tests 2, 6 and 7
   should pass on arrival.
3. Implement Design Decisions 1–3 in `engine/orders.py`.
4. Adjust `test_salvo_float_truncation_unchanged`'s fixture rounds as above; add the `REASON_TIPS`
   entry.
5. Search the tests and the vignette `tutorial`/`coaching` blocks for an `engage` whose salvo
   exceeds its effector's rounds, or an assertion on a jammer's `power_w`; fix only fixtures this
   package's behaviour change breaks, and list each in the completion note.
6. Run the full suite plus `test_determinism.py` and `test_import_guard.py`. Fix only defects this
   package introduced.
7. Do the documentation updates, then mark `COMPLETE`.

## Tests to Add

`spacesim/tests/test_effect_resource_bounds.py`, built on small `WorldState`/`OrderSystem`
fixtures in the style of `test_orders.py` (interceptor at the target's sub-point, a weapons-quality
`Track`, `roe={"blue": {"kinetic_authorized": True}}`):

1. **Oversized salvo refused at both paths** (criterion 1): an effector with `ammo=2`; `engage`
   with `salvo_n=3` → `dry_run` and `issue` both `rejected` / `insufficient_ammo`; the order queue,
   scheduler and event log are unchanged by the issue.
2. **Exact salvo accepted** (criterion 2): `ammo=2`, `salvo_n=2` → `queued`; advance through a
   successful resolution (seeded so Pₖ succeeds, or force success by patching the resolver in the
   test) → `ammo == 0`.
3. **Default and `None` salvo count as 1** (Design Decision 1): `ammo=1`, `salvo_n` absent and
   `salvo_n=None` → accepted; `ammo=0` → `no_ammo` (criterion 3, unchanged).
4. **Queued overdraw fails at execution** (criterion 4): `ammo=2`, two accepted 2-round
   engagements against two targets, both forced to succeed; after both execution times
   `ammo == 0`, the second effect-log record is `achieved == "failed"`, `success is False`,
   `reason == "insufficient_ammo"`, and the second target is not destroyed.
5. **Jam leaves the rating alone** (criterion 5): a jammer with `power_w` `0.0` and one with
   `250.0`; after a successful and a failed jam each, `power_w` is unchanged.
6. **Jam outcomes unchanged** (criterion 6): for a fixed vignette (`leo-isr-denial`) and seed, the
   effect-log entries (template, category, target, achieved, success) of a scripted jam sequence
   equal a recorded expectation taken before the change (record it in step 2).
7. **Replay** (criterion 7, determinism): rebuild test 4's world with `replay()` from its
   initial state and event log; the replayed world's `model_dump()` equals the live one.

The console tip is checked by **Inspection** of `REASON_TIPS` (browser GUI unverified headless,
`CLAUDE.md`).

## Documentation Updates

- `docs/requirements/03-requirements-traceability-matrix.md`: `FR-1460` and `FR-1470` rows —
  Feature Spec → `FS-132`, Test → `test_effect_resource_bounds.py`, Impl. Package → `IP-1320`.
- `docs/features/FS-132-effect-resource-bounds.md`: `Referenced By` only.
- `CLAUDE.md` "Code map" `engine/orders.py` bullet: one clause that `engage` is bounded by
  remaining rounds (`insufficient_ammo`, re-checked at execution) and jamming no longer consumes
  `power_w`.
- MBP row and counts, `packages/INDEX.md`, ROADMAP row, this header.
- Manual impact (`09` §10's reason list; `RED-5`/`BLU-3` where engagements are described) is
  **not** edited here. It is routed to `08-training-manual-authoring` once `VERIFIED` (`BL-0250`).

## Definition of Done

- All Tests to Add exist and pass; tests 1, 3, 4 and 5 were seen failing first.
- Full suite green, with no previously passing test now failing except the one fixture adjustment
  named above; `test_determinism.py` and `test_import_guard.py` green.
- Each case in the Objective's reproduction table behaves as FS-132 requires.
- `git diff --stat` touches only `engine/orders.py`, `static/app.js`, the two test files and the
  docs.
- Documentation updates done; status `COMPLETE`.

## Verification Checklist

1. `_validate` returns `insufficient_ammo` for a consumed salvo above the remaining rounds, after
   `no_ammo` and before the weapons-quality check; `dry_run` and `issue` agree.
2. `_validate` and the engage plan's `consume` use one shared rounds computation.
3. `_h_effect` re-checks rounds before resolving, logs the failed record with
   `reason: "insufficient_ammo"`, and charges nothing on that path.
4. No code path subtracts from `resources.power_w` (`grep` in `engine/`).
5. `test_salvo_float_truncation_unchanged` still asserts `consume.ammo == 2`; only its effector's
   rounds changed.
6. `REASON_TIPS` has an `insufficient_ammo` key.
7. Full suite and both permanent gates (`test_determinism.py`, `test_import_guard.py`) green.

## Dependencies

`IP-1051` and `IP-1052` (both `VERIFIED`). No package depends on `IP-1320`. `IP-1160` (`BLOCKED`,
not authorized) also edits `engine/orders.py` (`_validate`); if it is later authorized, it rebases
over this package's small `engage`-branch change.

## Risks

- **Fixtures that relied on overdraw.** One is known (`test_salvo_float_truncation_unchanged`).
  Task 5 searches for others.
- **Forcing success in tests.** Pₖ is random per seed. Tests should force the outcome (patch the
  resolver or pick a seed and assert it) rather than depend on a lucky seed silently.
- **Silent execute-time failures.** A W3 failure happens with nobody acting at that moment. The
  failed record is the only trace; it appears in god view, saves and AAR like a failed manoeuvre.
- **`IP-1160` rebase** (above).

## Rollback Considerations

Revert the commit. No data migration and no persisted-format change: the effect-log record's extra
`reason` key is additive, and old saves (including ones with negative values) replay unchanged.
