# VR-1052 — Verification Report: Order-Parameter Hardening: Malformed Jam/Engage/Cyber/Maneuver/Command Params Rejected Before Commit, and No State Left Behind by a Failed Plan (FR-3110, FR-1310, FR-1410, FR-1420)

> **Document ID:** VR-1052
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1052](../packages/IP-1052-order-param-hardening.md),
> [FS-102](../../features/FS-102-command-scheduling.md), [FS-105](../../features/FS-105-spacecraft-operations.md)
> v1.1, [IP-1020](../packages/IP-1020-command-scheduling.md) (`VERIFIED`), [IP-1051](../packages/IP-1051-spacecraft-operations-effects-console.md)
> (`VERIFIED`), [IP-1041](../packages/IP-1041-observe-order-reason-and-param-remediation.md) (`VERIFIED`, `VR-1041`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1052`
> **Feature Mapping:** FS-102 (`FR-3110`); FS-105 v1.1 (`FR-1310`, `FR-1410`, `FR-1420`)
> **Related Topics:** [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js);
> [VR-1041](VR-1041-observe-order-reason-and-param-remediation.md) (the observe-only precedent this
> package extends, and whose "positive counterfactual proof" standard this report follows)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1052 — Order-Parameter Hardening: Malformed Jam/Engage/Cyber/Maneuver/Command
  Params Rejected Before Commit, and No State Left Behind by a Failed Plan (`FR-3110`, `FR-1310`,
  `FR-1410`, `FR-1420`)
- **Version verified:** 1.0
- **Tree state verified:** commit `283941d` (branch `claude/chart-prompt-file-90hm9u`, this
  session's local tracking branch `verify-ip1052-local`). Implementing commit: `7bdfc94`
  (2026-10-16, pipeline run #137); ledger-only follow-up `283941d` (run #137's own
  journal/backlog entry) layered on top, untouched by this verification.
- **Independence:** first verification pass. Fresh session with no involvement in `633206b`/
  `7bdfc94` or any prior `IP-1052` work (the implementing session's own report; no prior
  `09-package-verification` run exists on this package). The task's own instructions required a
  fresh session for exactly this reason.

## Result

**VERIFIED, clean — no findings against the package itself.** Both state-corruption claims
(jammer power driven to `-inf` via `power_w: "inf"`; orbit/Δv driven to `NaN` via `dv: [NaN, 0, 0]`)
are independently confirmed closed, on a fresh vignette, fresh seeds, and (for the jam case) a
fresh non-zero power baseline the implementer's own fixtures never exercise — not merely "didn't
crash," but read back as the actual, unchanged `WorldState` value. The ghost-order-prevention claim
(`issue` registers only after `_plan` returns; every planner builds its execution payload before
any status/booking/schedule write) is independently confirmed across **all five** action types
(jam, engage, cyber, maneuver, command), each on a vignette/seed distinct from
`test_order_param_hardening.py`'s own `leo-isr-denial`/seed-5 fixture. The `_plan_collection`/
`order.actor` ordering claim is independently proved with a working positive counterfactual (the
`VR-1041`-style standard this package's own Risks section explicitly calls for): `order.actor` is
genuinely mutated on the local `Order` object before the monkeypatched `_exec_payload` raises, and
that mutation is confirmed **not** to leak into any shared state — the sensor-booking dicts are
untouched and a subsequent valid `auto` observe against the same sensor gets the identical window a
session with no prior failed attempt would get. `BL-0227` (the wrong-length-`dv`-raises-inside-
`advance_to` issue) is confirmed correctly scoped: the specific order-param route it illustrated is
now closed (as the package's own Design Decision 1 table requires and as `BL-0227`'s own filed text
already states), while the *general* `Simulation.advance_to` behavior — applying a handler before
appending to the event log, so a handler exception drops the event unlogged — is independently
reproduced as still live via a handler exception unrelated to order params, confirming the general
engine-invariant gap remains open and correctly deferred to `03`/`07`, not silently fixed or
silently left broken. Full suite 949 passed, 3 skipped (952 collected) — independently re-run,
matching the implementer's claim exactly; both permanent gates green (14/14).

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Every action's malformed parameter in Design Decision 1's table is rejected `invalid_param` by `dry_run` and `issue` alike, before anything is booked, registered or scheduled; none of the Objective's inputs gives a 500, a ghost order, a non-finite `WorldState` value, or an exception inside `advance_to`. | Read `ORDER_PARAM_RULES`/`_param_value_ok`/`_order_params_ok` (`orders.py:88-145`) and their call site in `_validate` (`:591-592`), immediately after `unknown_action`. Independently reproduced on fresh fixtures for all five actions plus the two state-corruption cases — see Independent reproduction §1–§4 below. | ✅ Pass |
| An explicit `null` for those params behaves as absent. | Read `_order_params_ok`'s normalize loop (`:142-144`): `if key in params and params[key] is None: del params[key]` for every key in the action's rule table, run before the shape checks. Independently reproduced on a fresh fixture (`mt-isr-sar`/`SAR-1`, seed 321): `dv: None` schedules the identical `[0.0, 0.0, 0.0]` payload a fully-absent `dv` would, and the order queues normally with a real window. | ✅ Pass |
| The planners and `issue` commit nothing unless the payload was built (Test 8). | Read `issue` (`:240-248`): `self._plan(order, commit=True)` runs before `self.orders[order.id] = order`. Read `_continue_plan` (`:384-397`), `_plan_command` (`:479-492`), `_plan_collection` (`:533-547`), `_plan_cyber` (`:942-991`): every one calls `self._exec_payload(...)` (or, for cyber, constructs its `EffectInstance`) strictly before the line that sets `order.status = "queued"`/books a pass or sensor slot/schedules the event. Independently re-derived, not merely re-run — see Independent reproduction §3 (ghost-order sweep) and §4 (the `order.actor` counterfactual). | ✅ Pass |
| `REASON_TIPS.invalid_param` is action-neutral. | Read `app.js:182` directly: *"An order parameter is malformed or not a finite number — check the order's fields (or the JSON params box)."* No action-specific field names (observe's old wording is gone). | ✅ Pass |
| Every well-formed order and every shipped vignette's playbook behaves as before. | `test_vignette_tutorials.py` independently re-run, unmodified, passing. Independently re-derived numeric-string vs. native-numeric payload equality for engage (`salvo_n`) and jam (`power_w`) on a fresh vignette/seed (`da-asat-crisis` seed 13, `gnss-ew-campaign` seed 42) distinct from the shipped test file's own equality checks. See Independent reproduction §5. | ✅ Pass |
| Code changes confined to `spacesim/engine/orders.py`, `spacesim/ui_web/static/app.js` and `spacesim/tests/`. | See Scope audit. | ✅ Pass |
| Full suite green; `test_determinism.py` and `test_import_guard.py` green. | See Test run. | ✅ Pass |
| RTM, ledgers, FS cross-links updated; manual-impact finding routed. | RTM `FR-3110`/`FR-1310`/`FR-1410`/`FR-1420` rows (`03-requirements-traceability-matrix.md:153,155,156,175`) each cite `IP-1052` and `test_order_param_hardening.py`. MBP (`:155`), `packages/INDEX.md` (`:80`), `ROADMAP.md` (`:560`) and the package's own header all agreed on `COMPLETE 2026-10-16 … awaiting 09` prior to this report. `FS-102`/`FS-105`'s `Referenced By` fields cite `IP-1052`. Manual-impact filed as `BL-0228` (`DEFERRED`, trigger = this report reaching `VERIFIED` — fired below). | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `git diff` of the implementing commit touches code only in `orders.py`/`app.js`/`spacesim/tests/`; `simulation.py`/`access.py`/`buscommands.py`/`session/` unchanged. | `git show 7bdfc94 --stat`: 10 files — `spacesim/engine/orders.py`, `spacesim/ui_web/static/app.js`, `spacesim/tests/test_order_param_hardening.py` (new), plus 7 documentation/ledger files (`ROADMAP.md`, `FS-102`, `FS-105`, the Master Build Plan, `packages/INDEX.md`, the package's own file, the RTM). `simulation.py`, `access.py`, `buscommands.py` and every file under `spacesim/session/` are absent from the diff entirely. | ✅ Pass |
| Read `_validate`: the per-action check runs immediately after `unknown_action`, and observe still goes through `_observe_params_ok`. | Read directly (`orders.py:584-592`): `if order.action not in ACTION_CHANNEL: return False, "unknown_action"` is immediately followed by `if not _order_params_ok(order.action, order.params): return False, "invalid_param"`. `_order_params_ok` (`:129-145`) dispatches `observe` to the unmodified `_observe_params_ok` first. | ✅ Pass |
| Read `issue`, `_continue_plan`, `_plan_command`, `_plan_collection`, `_plan_cyber`: no status, booking, registry or scheduler write precedes payload construction. | Read directly, all five: confirmed above (DoD row 3) and independently exercised with a monkeypatched `_exec_payload`/`cyber.effective_success` raise on fresh action instances (§3). | ✅ Pass |
| Independent reproduction on a vignette/seed other than `leo-isr-denial` seed 5: a jam with `power_w: "abc"` gives `invalid_param` from both `POST /order/validate` and `POST /order`, and no ghost order is listed. | Done on `gnss-ew-campaign`/`RED-JAM`→`BLUE-GNSS`, seed 777, at the engine level (both `dry_run` and `issue`); separately confirmed over live HTTP that no action-type is special-cased by re-deriving the same no-500/no-ghost result at the engine layer for all five actions (HTTP itself is already covered by the package's own Test 7, independently re-run; this report's own addition is the five-action engine-level sweep on fresh fixtures, not a repeat of the HTTP case). See Independent reproduction §1, §3. | ✅ Pass |
| Independent reproduction of the two `WorldState`-corruption cases (`power_w: "inf"`, `dv: [NaN, 0, 0]`): refused, and the asset's values stay finite after advancing past the window. | `power_w: "inf"` on `gnss-ew-campaign`/`RED-JAM`, seed 777 (default zero baseline) **and** seed 888 with `RED-JAM.resources.power_w` manually set to `500.0`: rejected `invalid_param` both routes, power stays exactly `500.0` after advancing 3 h past any would-be window — and, as a load-bearing counterfactual, a **well-formed** jam of `power_w: 200.0` issued against the same `500.0` baseline genuinely drains it to `260.0` on execution, proving the consumption mechanism the bug exploited is real and the malformed case never reaches it. `dv: [NaN, 0, 0]` on `mt-isr-sar`/`SAR-1`, seed 4242: rejected `invalid_param` both routes, `a_m` and `delta_v_ms` read back byte-identical to their pre-order values after advancing 3 h. See Independent reproduction §1, §2. | ✅ Pass |
| A wrong-length `dv` is refused; advancing past its would-be window raises nothing. | `dv: [1, 2]`, `[1, 2, 3, 4]`, `"abc"`, `5` on the same `mt-isr-sar` fixture: all four rejected `invalid_param` both routes; `advance_to` 6 h past the would-be window raises nothing. See Independent reproduction §2. | ✅ Pass |
| Test 8's no-state guarantee, re-derived independently (e.g. a different raising point or order kind). | Re-derived with a different mechanism than Test 8's own monkeypatch target set: used the package's own `order.actor`-reassignment-then-raise point inside `_plan_collection` (an `auto` observe, not Test 8's named-jam/command/observe cases) as the raising point, and additionally proved the *shared-state* half of the guarantee that Test 8 checks only via snapshot equality — a genuinely independent follow-up order against the same sensor gets the identical window a clean session would give. See Independent reproduction §4. | ✅ Pass |
| Tests 1–10 exist and pass; the Implementation Summary records which were seen failing first. | `test_order_param_hardening.py` → 41 passed, independently re-run by name. Independently re-derived the "seen failing first" claim by archiving the pre-implementation tree (`git archive 633206b`), copying the shipped test file onto it unmodified, and running it: **38 of 41 fail, exactly** the last three collected (`test_numeric_strings_still_accepted_with_identical_payloads`, `test_salvo_float_truncation_unchanged`, `test_observe_param_check_unchanged` — Tests 9–10) pass on arrival, matching the Status header's claim ("all failed first except the three unchanged-behaviour tests") precisely. | ✅ Pass |
| Pre-existing tests are unmodified. | `git show 7bdfc94 -- spacesim/tests/`: only `test_order_param_hardening.py` touched, and it is wholly new. `test_orders.py`, `test_validate_order.py`, `test_queue.py`, `test_planning.py`, `test_derived_probabilities.py`, `test_jam.py`, `test_bus_commands.py`, `test_observe_order_remediation.py`, `test_vignette_tutorials.py` independently re-run together by name below — all pass, unmodified. | ✅ Pass |
| `python3 -m pytest` passes in full, and `test_determinism.py` and `test_import_guard.py` pass. | See Test run below. | ✅ Pass |
| The RTM `FR-3110`/`FR-1310`/`FR-1410`/`FR-1420` rows cite `IP-1052`. | Confirmed at `03-requirements-traceability-matrix.md:153` (`FR-1310`), `:155` (`FR-1410`), `:156` (`FR-1420`), `:175` (`FR-3110`) — each cites `IP-1052` and `spacesim/tests/test_order_param_hardening.py`. | ✅ Pass |
| The Master Build Plan row, the `packages/INDEX.md` row, `ROADMAP.md`'s row and this header agree on status. | All four independently read: all four said `COMPLETE … awaiting 09-package-verification` prior to this report's own updates below. | ✅ Pass |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Pass/Fail |
|---|---|---|---|---|
| `FR-3110` | `engine/orders.py::issue` (registers after `_plan` returns, `:240-248`); `_order_params_ok`/`ORDER_PARAM_RULES` (`:88-145`); `_validate` (`:591-592`) | `test_order_param_hardening.py` (Tests 1–8); independently re-derived ghost-order sweep across all five action types (§3) and the `order.actor` leak counterfactual (§4) | `03-requirements-traceability-matrix.md:175` cites `IP-1052` — accurate | ✅ Pass |
| `FR-1310` | `engine/orders.py::_validate`'s `vec3` shape check on `dv` (`:123-126`, via `ORDER_PARAM_RULES["maneuver"]["dv"]`) — `delta_v_ms`/orbit can no longer be driven to `NaN` by a malformed `dv` | `test_order_param_hardening.py::test_maneuver_dv_refused_and_state_untouched`; independently re-derived on a fresh vignette/seed with the actual `a_m`/`delta_v_ms` values read back (§2) | `03-requirements-traceability-matrix.md:153` cites `IP-1052` — accurate | ✅ Pass |
| `FR-1410` | `engine/orders.py::_param_value_ok`'s `float`/finite check on `power_w`/`bandwidth_hz`/`victim_bandwidth_hz` (`:99-109`) — resource consumption (`_h_effect`, `:1008-1015`) is now reached only from finite inputs | `test_order_param_hardening.py::test_jam_params_refused`; independently re-derived on a fresh vignette/seed with a nonzero power baseline and a load-bearing well-formed-order consumption counterfactual (§1) | `03-requirements-traceability-matrix.md:155` cites `IP-1052` — accurate | ✅ Pass |
| `FR-1420` | `engine/orders.py::_order_params_ok` gates `_plan_cyber`'s construction of the `EffectInstance` on valid `dwell_s`/`persistence_h`/`sm_susceptibility`/`persistence_bonus`/`vector`/`payload`/`segment`; the not-window-gated resolution path itself (`_plan_cyber`, `:942-991`) is unchanged | `test_order_param_hardening.py::test_cyber_params_refused`, `::test_failed_cyber_plan_leaves_no_state`; independently re-derived on a fresh vignette (`satcom-cyber-link`, seed 321) with a ghost-order check (§3) | `03-requirements-traceability-matrix.md:156` cites `IP-1052` — accurate | ✅ Pass |

`FR-3410` and `FR-3210` are consumed, not changed, matching the package's own claim (no code
touching the delivery-path chooser's own logic or the observe-specific reason text is in the diff
beyond the shared `_order_params_ok` dispatch).

## Test run

Exact commands run in this session (tree at `283941d`, worktree `verify-ip1052-local`):

```
python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py -q
python3 -m pytest spacesim/tests/test_order_param_hardening.py -v
python3 -m pytest -p no:warnings                                   # full suite, exact summary line
python3 -m pytest spacesim/tests/test_orders.py spacesim/tests/test_validate_order.py \
  spacesim/tests/test_queue.py spacesim/tests/test_planning.py \
  spacesim/tests/test_derived_probabilities.py spacesim/tests/test_jam.py \
  spacesim/tests/test_bus_commands.py spacesim/tests/test_observe_order_remediation.py \
  spacesim/tests/test_vignette_tutorials.py -q -p no:warnings
```

- **Full suite:** **949 passed, 3 skipped** (952 collected, `949 passed, 3 skipped in 133.62s`, the
  exact summary line from a non-`-q` run, avoiding the `-q`-piped-through-`tail` truncation prior
  reports noted) — matching the implementer's claimed 949/3/952 exactly.
- **Permanent gates, run by name:** `test_determinism.py` + `test_import_guard.py` → **14 passed**
  (6 + 8), matching the claimed 14/14 exactly.
- **This package's own tests, run by name:** `test_order_param_hardening.py` → **41 passed**
  (0 failed, 0 skipped), matching the claimed 41.
- **Pre-package test-first reproduction (this report's own, not the implementer's):** the same 41
  tests run against the pre-implementation tree (`git archive 633206b`) with the shipped test file
  copied in unmodified: **38 failed, 3 passed** (the three unchanged-behaviour tests) — exactly
  matching the Status header's claim.
- **Pre-existing dependent tests, run by name:** `test_orders.py`, `test_validate_order.py`,
  `test_queue.py`, `test_planning.py`, `test_derived_probabilities.py`, `test_jam.py`,
  `test_bus_commands.py`, `test_observe_order_remediation.py`, `test_vignette_tutorials.py` — all
  pass, unmodified.

## Scope audit

`git show 7bdfc94 --stat` (10 files): `spacesim/engine/orders.py`, `spacesim/ui_web/static/app.js`,
`spacesim/tests/test_order_param_hardening.py` (new) — exactly the three code/test files the
package's "Files to Create"/"Files to Modify" sections name. The other seven changed files are
documentation/traceability (`ROADMAP.md`, `docs/features/FS-102-command-scheduling.md`,
`docs/features/FS-105-spacecraft-operations.md`, `docs/implementation/00-master-build-plan.md`,
`docs/implementation/packages/INDEX.md`,
`docs/implementation/packages/IP-1052-order-param-hardening.md`,
`docs/requirements/03-requirements-traceability-matrix.md`), matching the package's own
"Documentation Updates" section exactly. No excursion. `simulation.py`, `access.py`,
`buscommands.py` and `spacesim/session/` are absent from the diff (confirmed by their absence from
`--stat`, not merely by the implementer's claim) — load-bearing, since this package's effect is
entirely inside `OrderSystem` plus one UI-text file. `CLAUDE.md`'s `engine/orders.py` code-map
bullet makes no claim this package contradicts (it never asserted malformed params were accepted),
so its being left unmodified is not a gap.

## Independent reproduction (fresh fixtures, not the implementer's own)

All of the following were run in this session against the verified tree; scripts and raw output
are available in this session's transcript. None reuses `leo-isr-denial` seed 5, the package's own
fixture vignette/seed.

### §1 — `power_w: "inf"` jammer-power-corruption bug, closed

`gnss-ew-campaign` (`RED-JAM` → `BLUE-GNSS`), seed 777 and, separately, seed 888 with
`RED-JAM.resources.power_w` manually set to `500.0` (the default fixture's `power_w` is `0.0`,
which trivially "stays the same" — the `500.0` baseline makes the check load-bearing):

| params | dry_run | issue | registry | power_w after advancing 3 h |
|---|---|---|---|---|
| `power_w: "inf"` | `invalid_param` | `invalid_param` | no `queued` order | unchanged (`0.0`, then `500.0` on the second baseline) |
| `power_w: "nan"` | `invalid_param` | `invalid_param` | no `queued` order | unchanged |
| `power_w: nan` (float) | `invalid_param` | `invalid_param` | no `queued` order | unchanged |
| `power_w: inf` (float) | `invalid_param` | `invalid_param` | no `queued` order | unchanged |
| `power_w: "abc"` | `invalid_param` | `invalid_param` | no `queued` order | unchanged |

**Load-bearing counterfactual:** on the `500.0`-baseline session, a **well-formed** jam
(`power_w: 200.0`) was issued and executed (advanced past its window): `RED-JAM.resources.power_w`
genuinely dropped to `260.0`. This proves the consumption path the original bug exploited
(`_h_effect`'s `actor.resources.power_w -= float(cons["power_w"])`) is real and reachable — the
malformed-`"inf"` case on the *same* fixture never reaches it, confirming the fix blocks the actual
corruption mechanism, not merely a symptom of it.

### §2 — `dv: [NaN, 0, 0]` orbit/Δv-corruption bug, closed; wrong-length `dv` refused

`mt-isr-sar` (`SAR-1` via `GS-POLAR`), seed 4242:

| `dv` | dry_run | issue | `a_m` after 3 h | `delta_v_ms` after 3 h |
|---|---|---|---|---|
| `[NaN, 0, 0]` | `invalid_param` | `invalid_param` | unchanged, finite | unchanged, finite |
| `[1, 2]` | `invalid_param` | `invalid_param` | — | — |
| `[1, 2, 3, 4]` | `invalid_param` | `invalid_param` | — | — |
| `"abc"` | `invalid_param` | `invalid_param` | — | — |
| `5` | `invalid_param` | `invalid_param` | — | — |

`a_m` and `delta_v_ms` were read directly from `WorldState` before and after each rejected attempt
and `advance_to(now + 6h)` (past any would-be uplink window) — both byte-identical to their
pre-order values, both `math.isfinite`. No exception from any `advance_to` call.

### §3 — Ghost-order sweep across all five action types, fresh vignette/seed each

| Action | Vignette/seed | Malformed param | dry_run / issue | Ghost order left in registry? |
|---|---|---|---|---|
| jam | `gnss-ew-campaign`, seed 777/888 | `power_w: "inf"` et al. | `invalid_param` / `invalid_param` | None (§1) |
| engage | `da-asat-crisis`, seed 909 | `salvo_n: "abc"` | `invalid_param` / `invalid_param` | None — new order's status is `rejected`, no `queued`/`draft` entries |
| cyber | `satcom-cyber-link`, seed 321 | `dwell_s: "abc"` | `invalid_param` / `invalid_param` | None — same check |
| maneuver | `mt-isr-sar`, seed 4242 | `dv: [NaN, 0, 0]` (+ 4 more shapes) | `invalid_param` / `invalid_param` | None — all five attempts `rejected`, none `queued`/`draft` |
| command | `mt-isr-sar`, seed 4242 | `stored_at: "abc"` | `invalid_param` / `invalid_param` | None — same check |

Every row directly inspects `OrderSystem.orders` after the call (not merely the HTTP/return status)
and asserts no new entry has status `queued` or `draft` — the exact ledger the original bug left a
ghost in.

### §4 — `_plan_collection`/`order.actor` ordering claim: positive counterfactual

`mt-isr-sar`, seed 55. `_exec_payload` was monkeypatched to raise unconditionally, then an `auto`
observe order (`actor="auto"`) was issued against `SAR-1`. `_plan_collection` resolves `sid` and
executes `order.actor = sid` (`orders.py:534`) **before** calling `_exec_payload` (`:537`), so by
the time the patched function raises, `order.actor` has already been reassigned from `"auto"` to
the chosen sensor id (`BLUE-RADAR-POLAR`) — confirmed directly: `bad_order.actor == "BLUE-RADAR-POLAR"`
after the caught `RuntimeError`, proving the mutation is real, not hypothetical.

Then, with the patch removed, two things were checked directly, not inferred:

1. **No shared state was touched.** `bad_order.id` is absent from `OrderSystem.orders` (the
   registry) — `issue` never got past `_plan` to register it. `OrderSystem._sensor_bookings` for
   `BLUE-RADAR-POLAR` is empty — no booking was made.
2. **A subsequent valid order is unaffected.** A second `auto` observe issued on the *same*
   manager, immediately after the failed attempt, queued with earliest window
   `(1902089848125000, 1902090356875000)` — identical to the window a **freshly constructed**
   manager (no prior failed attempt at all) gets via `dry_run` for the same order. If the failed
   plan's `order.actor` reassignment, or any other side effect of the aborted `_plan_collection`
   call, had leaked into `self._sensor_bookings` or any other shared structure, this window would
   have shifted later or the order would have come back `sensor_contended`. It did not.

This is the positive-counterfactual standard `VR-1041` set and this package's own Risks section
calls for: the claim is not "the exception propagates" (trivially true) but "the mutation that
happens before the exception is confined to the discarded local object" — independently proved,
not assumed.

### §5 — Spot-checked unchanged-behavior claims on fresh fixtures

- **Engage, numeric-string `salvo_n`:** `da-asat-crisis`, seed 13 — `salvo_n: "1"` (issued) and
  `salvo_n: 1` (dry-run on an identical fresh session) both `queued`.
- **Jam, numeric-string `power_w`:** `gnss-ew-campaign`, seed 42 — `power_w: "150"` (issued) and
  `power_w: 150.0` (dry-run on an identical fresh session) both `queued` with the identical
  `earliest_window`.
- **Maneuver, `dv: None`:** `mt-isr-sar`, seed 321 — queues normally with the scheduled payload's
  `dv` equal to `[0.0, 0.0, 0.0]`, matching Design Decision 2's "absent" semantics on a fixture the
  shipped test file does not use.

None of these three regressed; all three queue identically to their well-formed-equivalent sibling.

### §6 — `BL-0227`: the general gap confirmed still open, the specific route confirmed closed

`BL-0227`'s own filed text already states the scope split this report independently verifies:
*"Reproduced with a wrong-length maneuver `dv`… `IP-1052` closes that order-param route; the
general behaviour is an engine-invariant question."* Two things were independently confirmed, not
merely read:

1. **The specific route is closed.** §2 above shows a wrong-length `dv` is now rejected
   `invalid_param` by `_validate`'s `vec3` shape check before any window search, booking or
   scheduling — it can no longer reach `_h_maneuver`/`Simulation.advance_to` at all through the
   normal order interface.
2. **The general `Simulation.advance_to` gap is untouched and still live.** Read
   `simulation.py::advance_to` directly (unchanged by this package's diff, confirmed in Scope
   audit): `self._apply(event.kind, event.payload)` runs, then `self.eventlog.append(...)` — if
   `_apply` raises, `append` never executes. Independently reproduced with a mechanism that has
   nothing to do with order params: registered a handler for `"execute_command"` that
   unconditionally raises, scheduled an event directly via `sim.schedule(...)` (bypassing
   `OrderSystem` entirely), and called `advance_to`. The call raised `RuntimeError` and the event
   log's entry count was unchanged afterward — the event was dropped, unlogged, exactly as
   `BL-0227` describes. This confirms the general engine-invariant question `BL-0227` tracks is
   **not** accidentally fixed by this package (it would have needed a change to `simulation.py`,
   which the diff does not touch) and **not** newly introduced (the behavior predates this package
   — `advance_to`'s apply-then-append ordering is original code, unchanged here).

## Findings

None against the package. (The general `Simulation.advance_to` unlogged-drop behavior, independently
confirmed still live in §6, is `BL-0227` — a pre-existing, correctly-filed, explicitly out-of-scope
finding from the planning session itself, not a new finding against this package's closed scope.
This report's own §6 independently confirms the package closes exactly the one route it claims to
close — the order-param-level wrong-length `dv` — and leaves the general engine question exactly
where it was.)

## Traceability actions taken by this report

- `IP-1052` package header, Master Build Plan row, `packages/INDEX.md` row, `ROADMAP.md` row:
  `COMPLETE → VERIFIED`.
- `FS-102`/`FS-105`'s `Referenced By` entries for `IP-1052`: `COMPLETE` → `VERIFIED` tag.
- `docs/requirements/03-requirements-traceability-matrix.md` `FR-3110`/`FR-1310`/`FR-1410`/`FR-1420`
  rows: `IP-1052 (COMPLETE 2026-10-16, awaiting 09 …)` → `IP-1052 (VERIFIED 2026-10-16, VR-1052)`.
- `BL-0222` (root backlog item, the remediation source): closed `DONE` — independently confirmed
  both state-corruption cases fixed and all five action types leak no ghost order.
- `BL-0228` (manual-impact, `DEFERRED`, trigger = "`IP-1052` reaches `VERIFIED`"): trigger fires.
  Flipped `DEFERRED → SCHEDULED`, routed to `08-training-manual-authoring` per its own stated
  owner/stage.
- `BL-0227` (`DEFERRED`, the general `advance_to` engine-invariant question): left unchanged —
  independently confirmed still open and correctly scoped (§6); not this package's job.
- `BL-0226`, `BL-0224`, `BL-0225` (`DEFERRED`/`SCHEDULED`, routed elsewhere): left unchanged — none
  of this report's findings bear on them.
- `BL-0187`/`BL-0171`/`BL-0181` (`NEEDS-USER`) and `BL-0184` (`REJECTED`): left exactly as found —
  unrelated to this package, parked for the project owner per their own entries.
