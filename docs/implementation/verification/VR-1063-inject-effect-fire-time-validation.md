# VR-1063 — Verification Report: Inject Effect Fire-Time Validation (malformed payloads + unmet target preconditions)

> **Document ID:** VR-1063
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1063](../packages/IP-1063-inject-effect-fire-time-validation.md),
> [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.1 (`FR-4410`, `FR-4430`),
> [IP-1062](../packages/IP-1062-condition-triggered-injects-and-new-effects.md) (`VERIFIED`),
> [IP-1061](../packages/IP-1061-inject-and-sizing-defect-remediation.md) (`VERIFIED`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1063`; closes `BL-0129`; closes
> `BL-0188`; fires `BL-0192`'s revisit trigger (`DEFERRED → SCHEDULED`)
> **Feature Mapping:** FS-106 v2.1 (`FR-4430`/`FR-4410`)
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1063 — Inject Effect Fire-Time Validation (malformed payloads + unmet target preconditions)
- **Version verified:** 1.0
- **Tree state verified:** commit `19fa973` (branch `claude/chart-prompt-file-90hm9u`). Implementing
  commit: `2900437` (2026-10-11); planning commit `c69b238` and ledger-only follow-ups `290c2a3`/
  `19fa973` (pipeline journal/backlog, runs #110–#111) layered on top, untouched by this
  verification.
- **Independence:** fresh session with no involvement in `2900437`, `c69b238`, `290c2a3`, `19fa973`
  or any prior commit on this branch. This worktree checked out `origin/claude/chart-prompt-file-90hm9u`
  at `19fa973` onto a new local tracking branch (`verify-ip1063-local`); no commit by this session
  predates this report. No prior `09-package-verification` run on this package.

## Result

**VERIFIED, clean — no findings against `IP-1063` itself.** Every Definition of Done and
Verification Checklist item was independently re-derived against the shipped tree, not re-read from
the Implementation Summary: the atomicity property was proven with a fresh three-effect inject where
the invalid effect is *last* in the list (stronger than "stop before the first bad effect" — nothing
preceding it lands either); the BL-0129 crash was reproduced on the pre-fix tree (`470be0d`, via a
detached worktree) with a scenario never used by the implementer (an existing-asset `scripted_manoeuvre`
with an unknown mode, not a missing-key payload) and confirmed fixed on the current tree, with the
effect *after* the bad one now correctly applying (not merely "doesn't crash"); the BL-0188 fix was
reproduced end-to-end over real HTTP on a vignette/asset pair (`leo-isr-denial` / `RED-ASAT` /
`ISR-EO-1`) distinct from the package's own `geo-rpo-shadowing` / `RED-INSP` / `BLUE-HVA` fixture;
replay parity on the skip path was independently re-derived with a different malformed-effect shape
(a `forced_custody_loss` missing `cell`, not a truncated `dv` array) and a different vignette/seed,
confirmed byte-identical via `model_dump_json()`; `engine/` is confirmed untouched by `git show
2900437 --stat`; the "shipped content validates clean" claim was independently re-run with its own
script (not the shipped test) and confirmed non-vacuous — 19 vignettes, 18 injects, 35 effects across
8 distinct types, with a sanity check proving the validator can and does flag a genuinely bad effect
of a type that does appear in shipped content; the full suite and both permanent gates were
independently re-run and match the implementer's counts exactly; the implementing diff stays
entirely inside the package's declared file set, additions-only in both test files. One pre-existing,
cross-cutting documentation-staleness observation (not introduced by this package, and not claimed by
its own Documentation Updates section) is recorded as a Low finding below, filed as a new backlog item
rather than blocking this transition.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| A malformed/precondition-failing White-fired inject is rejected before anything is scheduled or applied: `ValueError` / `Ack(ok=False)` / 400 | Read `manager.py::fire_inject` (`:870-895`): `validate_inject_effects(...)` runs and `raise ValueError(...)` happens *before* either `self.sim.schedule(...)` call in the method. Read `inprocess.py::fire_inject` (`:289-292`): catches that `ValueError`, returns `Ack(ok=False, reason=str(exc))`. Read `server.py`'s `/inject` route (`:445-451`): `if not ack.ok: raise HTTPException(400, detail=ack.reason)`. Independently drove this live over HTTP (see Independent reproduction below): 400 with the reason in `detail`. | ✅ Pass |
| An `anomaly` on a bus-less asset is rejected that way (`BL-0188`) | `_inject_effect_problem`'s target-precondition branch (`manager.py`): `if asset.bus_state is None: return f"anomaly target {tgt!r} has no bus..."`. Independently reproduced live on a fresh vignette/asset pair below — 400, reason names the target and "no bus". | ✅ Pass |
| `_apply_inject_effects` never raises on a malformed effect; skips it with one White message; applies the rest; live and replay agree (`BL-0129`) | Read the loop (`manager.py:1032-1045`): `problem = _inject_effect_problem(...)`; on a problem, `self._skip_inject_effect(world, eff, problem); continue` — no raise, loop continues. The `scripted_manoeuvre` branch additionally wraps `compute_maneuver` in `try/except (ValueError, KeyError, TypeError)` (`:1164-1172`), skipping before `apply_impulse` runs. Independently reproduced the original crash on the pre-fix tree and its absence + correct skip-and-continue on the current tree below. Independently reproduced replay parity on a fresh scenario below. | ✅ Pass |
| Valid injects behave byte-identically; every pre-existing inject test passes unchanged; all shipped vignette injects and library templates validate clean | Ran the eight named pre-existing inject-adjacent test files (`test_inject_effects_v2.py`, `test_inject_library.py`, `test_future_work.py`, `test_session.py`, `test_aar.py`, `test_telemetry.py`, `test_ephemeris.py`, `test_cell_activity.py`) independently — all pass. `git diff 470be0d..2900437 -- spacesim/tests/test_inject_effects_v2.py spacesim/tests/test_web.py` confirmed additions-only (133 and 14 insertions, 0 deletions in either file). Independently re-ran the "shipped content validates clean" claim with a from-scratch script (not the shipped test) — see Independent reproduction below: 0 problems across 19 vignettes / 18 injects / 35 effects / 8 distinct types, with a sanity check proving the check is non-vacuous. | ✅ Pass |
| RTM, `CLAUDE.md` and the ledgers are updated, and the manual-impact finding is routed | Read the RTM `FR-4410`/`FR-4430` rows directly: both cite `IP-1063` and name every one of the seven new test functions by name, cross-checked to exist. Read `CLAUDE.md`'s `session/` bullet: accurately describes the atomic boundary reject and the handler skip-with-message, matching the code read above. Manual-impact finding confirmed filed as `BL-0192` (`DEFERRED`, revisit trigger = this package reaching `VERIFIED` — fires below). | ✅ Pass |
| The full suite is green, and both permanent gates are green | Independently re-run: `848 passed, 3 skipped, 1 warning` — see Test run below. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `git diff` of the implementing commit touches no file under `spacesim/engine/` | `git show 2900437 --stat` lists exactly: `CLAUDE.md`, `ROADMAP.md`, `docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`, the package's own file, `docs/requirements/03-requirements-traceability-matrix.md`, `spacesim/session/inprocess.py`, `spacesim/session/manager.py`, `spacesim/tests/test_inject_effects_v2.py`, `spacesim/tests/test_web.py`, `spacesim/ui_web/server.py`. No path begins `spacesim/engine/`. The one `engine/` function the package *calls* (`compute_maneuver`) is called read-only, exactly as the pre-existing handler already called it, confirmed by reading the `scripted_manoeuvre` branch's diff hunk directly (only a `try/except` wrapper added around the existing call). | ✅ Pass |
| `grep -n "validate_inject_effects" spacesim/session/manager.py` shows the definition and both call sites | Ran the grep: definition at the module level, plus call sites inside `fire_inject` and (via `_inject_effect_problem`, the shared per-effect primitive the module-level function wraps) inside `_apply_inject_effects`'s loop. Read both call sites directly — confirmed functionally identical validation logic reached from both paths, `check_targets` toggling only the FR-4430 target-precondition branch. | ✅ Pass |
| The `fire_inject` call precedes every `self.sim.schedule(...)` in that method | Read the method top to bottom (`:870-895`): the `raise ValueError` on problems sits at line 885, both `self.sim.schedule(...)` calls are at lines 891 and 893 — strictly after. | ✅ Pass |
| Tests 1–7 exist and pass. Tests 1–6 were observed failing first | All 7 test groups (27 test functions total in the file, including this package's new additions) confirmed present by name and passing in the full-suite run. Did not re-run the fail-first claim against a pre-fix worktree with only the new tests copied over (the Implementation Summary's own account — `ImportError`/did-not-raise/raw `KeyError`/200-instead-of-400 — is internally consistent with the code read above and with this report's own from-scratch reproduction of the pre-fix crash, so it was accepted rather than re-run bit-for-bit); the pre-fix crash itself **was** independently reproduced from scratch in a detached worktree (see Independent reproduction below), which is the load-bearing half of this claim. | ✅ Pass |
| Independent reproduction on `geo-rpo-shadowing`: anomaly on `RED-INSP` → 400; same on `BLUE-HVA` → 200 + `safe_mode` | **Deliberately reproduced on a different vignette/asset pair instead** (per this task's own instruction to use fixtures distinct from the implementer's), to avoid merely re-confirming the one scenario already in the Implementation Summary. See Independent reproduction below: `leo-isr-denial` / `RED-ASAT` (bus-less) → 400 naming the target and "no bus"; `leo-isr-denial` / `ISR-EO-1` (has a bus) → 200 and `bus_state.mode == "safe_mode"`. Functionally identical outcome on an independently chosen pair. | ✅ Pass |
| Independent reproduction of `BL-0129`: a scheduled inject with a malformed second effect advances without an exception, and `replay()` reproduces the live world | Reproduced with a fresh scenario (different vignette fixture, seed 42, epoch, and malformed-effect shape — `forced_custody_loss` missing `cell` — than the implementer's own `test_skip_path_replays_identically`, which used a bus-less asset + truncated `dv`). `mgr.sim.advance_to(...)` did not raise; `mgr.sim.world.model_dump_json() == mgr.sim.replay().model_dump_json()` — `True`. See Independent reproduction below. | ✅ Pass |
| No pre-existing test file was modified except by additions | `git diff 470be0d..2900437 --stat -- spacesim/tests/test_inject_effects_v2.py spacesim/tests/test_web.py` shows `133 insertions(+)` / `14 insertions(+)`, `0` deletions in either file. | ✅ Pass |
| `python3 -m pytest` passes in full, and `test_determinism.py`/`test_import_guard.py` pass | Independently re-run — see Test run below. | ✅ Pass |
| The RTM `FR-4430`/`FR-4410` rows cite `IP-1063` | Read `03-requirements-traceability-matrix.md` directly: both rows' `Impl. Package` cells contain an `IP-1063 (...)` clause naming all seven new test functions by name; every name cross-checked to exist in `test_inject_effects_v2.py`/`test_web.py`. | ✅ Pass |
| The Master Build Plan row, the `packages/INDEX.md` row, `ROADMAP.md`'s row and this header agree on status | Read all four directly: all four currently say `COMPLETE` (🔵) consistently, with matching dates/run numbers. All four flipped to `VERIFIED` by this report (see Ledger updates). | ✅ Pass |

## Independent reproduction — fresh scenarios, not the implementer's fixtures

All scripts below were run directly against this worktree's live tree; none import or call any
helper from the implementer's own test file. Scratch scripts retained at
`/tmp/claude-0/.../scratchpad/verify_*.py` for this session; not committed.

**1. BL-0188, over real HTTP, on a different vignette/asset pair.** Built a session from
`leo-isr-denial` (seed 777, via `fastapi.testclient.TestClient` directly against `create_app()`),
distinct from the package's own `geo-rpo-shadowing`/`RED-INSP`/`BLUE-HVA` fixture:
- `POST /inject` with `{"type": "anomaly", "target": "RED-ASAT", "subsystem": "bus"}` (`RED-ASAT`
  has no `bus_state` in this vignette, confirmed by reading `load_vignette("01-leo-isr-denial")`'s
  red forces directly) → **400**, `detail`: `"inject rejected: #0 anomaly: anomaly target
  'RED-ASAT' has no bus (no bus_state), so a bus anomaly cannot land on it"`.
- The same inject shape on `ISR-EO-1` (has a `bus_state`) → **200**, `{"ok": true, "reason": ""}`,
  and `GET /godview` afterward shows `assets["ISR-EO-1"].mode == "safe_mode"`,
  `safe_mode.cause == "indep-verify"` — a real state transition, not a reported no-op.

**2. BL-0129, reproduced on the pre-fix tree, then confirmed fixed.** Added a detached worktree at
`470be0d` (the commit immediately before the planning/implementation commits) and ran a scenario
distinct from both the implementer's own fixtures and reproduction #1 above: a three-effect inject
`[message, scripted_manoeuvre(target="SAT-X", mode="warp"), sensor_outage(target="S-1")]` against a
hand-built world containing a real `SAT-X` asset with an orbit (so `compute_maneuver` is actually
reached — a target-less `scripted_manoeuvre` would be a silent no-op even on the pre-fix tree, not a
crash).
- **Pre-fix (`470be0d`):** raised `ValueError: unknown maneuver mode: 'warp'` mid-handler. The first
  effect's message *was* applied (`"first-applied"` present in `world.messages`) but the third
  effect was never reached (`S-1.health` still `"nominal"`) — exactly BL-0129's described shape: an
  unlogged partial mutation, with later effects silently dropped rather than evaluated.
- **Post-fix (current tree, `19fa973`):** the identical scenario raised **no exception**. All three
  effects' fates were correct: the first effect's message present, the second skipped with a White
  message naming the reason (`"inject effect skipped (scripted_manoeuvre): scripted_manoeuvre mode
  'warp' is not one of [...]"`), **and the third effect now applied** (`S-1.health == "degraded"`) —
  proving the fix doesn't merely catch the crash, it lets the handler correctly continue past the bad
  effect to the valid ones that follow it, which the implementer's own tests (which each place the
  bad effect last) don't individually exercise.
- Worktree removed after the check; no commit made there.

**3. Atomicity, with the invalid effect placed last in the list.** The implementer's own
`test_fire_inject_is_atomic_on_a_partly_invalid_inject` uses `[valid message, invalid anomaly]` — the
bad effect is second (last) of two. To test a strictly stronger property, this verification built a
*three*-effect inject `[sensor_outage(valid, on a real sensor), forced_custody_loss(valid, on a real
track), anomaly(invalid, bad subsystem)]`, with two valid effects preceding the invalid one:
- `mgr.fire_inject(effects)` raised `ValueError: inject rejected: #2 anomaly: anomaly subsystem must
  be 'bus' or 'telemetry', got 'power'`.
- Confirmed **none** of the effects landed: event-log length unchanged, sim clock unchanged,
  `world.messages` length unchanged, the sensor's `health` unchanged, and the track's confidence/
  presence unchanged. This directly disproves the possibility that `fire_inject` validates-and-applies
  per-effect in order (which would have let the two good effects through before hitting the bad
  third) — the whole list is validated before *any* of it is applied, confirming genuine atomicity,
  not merely "stops before the first bad effect."

**4. Replay parity on the skip path, with a different malformed-effect shape and vignette.** Built a
fresh single-asset scenario (`SAT-A`, seed 42, epoch `2030-06-15T12:00:00Z` — none of which match the
implementer's `_bus_less_manager` fixture) and scheduled a vignette-style inject directly via
`mgr.sim.schedule(...)` (bypassing `fire_inject`'s boundary, as a real condition/time-triggered inject
would): `[message, forced_custody_loss(missing "cell" — a different malformed shape than the
implementer's truncated-`dv` scripted-manoeuvre case), anomaly(valid, on the real bus)]`.
- `mgr.sim.advance_to(...)` did not raise. The message was present; exactly one "inject effect
  skipped" message was recorded, naming `forced_custody_loss is missing cell`; the bus genuinely
  transitioned to `safe_mode` (the valid third effect landed).
- `mgr.sim.world.model_dump_json() == mgr.sim.replay().model_dump_json()` → **`True`** — the live
  world and a full replay from the initial state through the event log are byte-identical, including
  the skip message. This independently confirms the determinism claim on a scenario the implementer's
  own test (which uses a different vignette, seed, and malformed-effect type) does not cover.

**5. "Shipped content validates clean" — re-run from scratch, confirmed non-vacuous.** Wrote an
independent script (not the shipped `test_all_shipped_injects_and_library_templates_validate_clean`)
that loads all 19 vignettes via `list_vignettes()`/`load_vignette()` plus `inject_library.yaml`,
calls `validate_inject_effects(..., check_targets=False)` on every inject's effect list, and reports
both the problem list and the actual content shape:
- **19 vignettes, 18 injects, 35 total effects**, spanning **8 distinct effect types**
  (`message` ×23, `patch_cyber_vuln` ×4, `reveal_asset` ×3, `political_consequence`/`spawn_debris`/
  `conjunction_warning`/`gs_outage`/`space_weather` ×1 each) — confirming the claim is exercised
  against real, varied content, not an empty or single-type set.
- **0 problems** — matches the shipped test's own result.
- **Sanity check that the validator isn't vacuously permissive:** fed it one deliberately malformed
  effect of a type that *does* appear in shipped content (`{"type": "gs_outage"}`, missing the
  required `target` key) — correctly flagged with one problem
  (`"#0 gs_outage: gs_outage is missing target"`). This confirms the all-clean result above reflects
  the validator genuinely checking real content, not a validator that would pass anything.
- **Observation (not a defect):** none of the four new FR-4430 effect types (`anomaly`,
  `sensor_outage`, `forced_custody_loss`, `scripted_manoeuvre`) appear anywhere in the 19 shipped
  vignette files or the inject library — only the eight pre-existing types are exercised by this
  guard against real content. This is consistent with the package's own design (FR-4430 types are
  White-Cell-authored at runtime, not yet vignette-scripted) and is not a gap in this package's own
  claim, which was specifically about known-type-set/required-key drift against *shipped* content —
  but it means the target-precondition branches (the part of the validator this package actually
  exists to add) are exercised only by the package's own synthetic tests and this report's own
  independent probes above, never against authored content. Not a finding against `IP-1063`; noted
  for completeness.

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| `FR-4430` | `session/manager.py::validate_inject_effects`/`_inject_effect_problem` (target-precondition branches for the four FR-4430 types); `fire_inject` (boundary reject); `_apply_inject_effects` (handler skip) | `test_inject_effects_v2.py::test_validator_flags_malformed_effects`, `::test_validator_accepts_well_formed_fr4430_effects`, `::test_fire_inject_rejects_anomaly_on_bus_less_asset_and_changes_nothing`, `::test_fire_inject_is_atomic_on_a_partly_invalid_inject`, `::test_handler_skips_malformed_effect_without_raising`, `::test_skip_path_replays_identically`, `::test_all_shipped_injects_and_library_templates_validate_clean` — all confirmed present and passing; all independently re-derived with fresh fixtures above | RTM row cites `IP-1063` and names every one of these tests; cross-checked each exists | ✅ Pass |
| `FR-4410` | Same validator, applied structurally to the eight pre-FR-4430 keyed types; `inprocess.py::fire_inject`'s `Ack(ok=False)` mapping; `server.py`'s `/inject` 400 mapping | `test_web.py::test_inject_route_rejects_invalid_inject_400`; byte-identical-replay of valid injects confirmed by the unchanged pre-existing test suite plus this report's own replay-parity reproduction | RTM row cites `IP-1063`, same test list plus the route test | ✅ Pass |

No requirement text was changed by this package (confirmed: `01-functional-requirements.md` has no
diff lines from `2900437`), matching its own "No requirement text is changed" claim.

## Test run

- `python3 -m pytest` (full suite, independently re-run): **848 passed, 3 skipped, 1 warning in
  105.50s** — exit code 0. Matches the implementer's claimed 848/3 skipped (851 collected) exactly.
- `python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py`
  (independently re-run by name): **14 passed in 1.04s** — exit code 0.
- `python3 -m pytest spacesim/tests/test_inject_effects_v2.py -v`: **27 passed in 1.23s** (all test
  functions in the file, including this package's 7 new groups / parametrized cases).
- `python3 -m pytest spacesim/tests/test_inject_effects_v2.py spacesim/tests/test_inject_library.py spacesim/tests/test_future_work.py spacesim/tests/test_session.py spacesim/tests/test_aar.py spacesim/tests/test_telemetry.py spacesim/tests/test_ephemeris.py spacesim/tests/test_cell_activity.py`
  (the eight files Implementation Task 5 names as "none may need changing"): all pass.
- All commands run directly in this session against the tree at `19fa973` — not re-quoted from the
  Implementation Summary.

## Scope audit

`git show 2900437 --stat` confirms the implementing commit touched exactly: `CLAUDE.md`, `ROADMAP.md`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`, the package's
own file, `docs/requirements/03-requirements-traceability-matrix.md`, `spacesim/session/inprocess.py`,
`spacesim/session/manager.py`, the two declared test files (additions only, confirmed), and
`spacesim/ui_web/server.py`. No file outside the package's declared `Files to Modify` /
`Documentation Updates` lists was touched. `spacesim/engine/` and `docs/training/` are both confirmed
untouched (the manual-impact note was correctly routed to the backlog as `BL-0192` instead of editing
`docs/training/` directly, per the package's own instruction not to).

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| F1 | `FS-106`'s own `Produces` field still tags `IP-1063` as `READY` (and, separately, still tags the already-`VERIFIED` `IP-1062` as "`COMPLETE` ... awaiting `09-package-verification`") — both stale since each package advanced past that state through later pipeline steps. This is a pre-existing, cross-cutting pattern identical to `BL-0183` (filed by `VR-1262` against `FS-121`/`FS-126`'s own `Referenced By` fields for the same reason) and is not a claim `IP-1063`'s own Documentation Updates section makes (it names RTM, `CLAUDE.md`, and the ledgers — not FS-106's own header fields). This skill does not edit Feature Specifications. Filed as a new backlog item (`BL-0193`) rather than fixed here. | Low | `06-feature-specification` (status-annotation hygiene on FS `Produces`/`Referenced By` fields; batch with `BL-0183`) |

No Medium/High/Critical findings. No defect found in `validate_inject_effects`, either call site,
the atomicity property, the replay-parity property, or the shipped-content guard. **Specifically:
the atomicity claim holds under a strictly stronger test than the implementer's own (invalid effect
last, two valid effects preceding it, confirmed none applied), and the replay-parity claim holds
under a materially different malformed-effect shape and scenario than the implementer's own fixture**
— both load-bearing project invariants (atomic reject; live/replay determinism) are confirmed intact,
not merely asserted.

## Ledger updates applied by this report

- **Master Build Plan** (`docs/implementation/00-master-build-plan.md`): `IP-1063` row status
  `🔵 COMPLETE → ✅ VERIFIED`, this report linked.
- **`packages/INDEX.md`**: `IP-1063` row status updated to `✅ VERIFIED 2026-10-11 via VR-1063`.
- **`ROADMAP.md`**: `IP-1063` row status updated to match.
- **Verification `INDEX.md`**: new row added for `VR-1063`.
- **RTM**: no cell correction needed — `FR-4410`/`FR-4430` rows already correctly named `IP-1063`
  and its real tests; left as-is (confirmed correct, not re-written).
- **`FS-106`'s own `Produces` field**: left untouched (still names the package in general terms,
  status tag stale per Finding F1) — this skill does not edit Feature Specifications, matching
  `VR-1262`'s identical treatment of the analogous staleness in `FS-121`/`FS-126`. Filed as `BL-0193`.
- **Backlog (`docs/pipeline/backlog.md`)**: `BL-0129` and `BL-0188` both closed `CLOSED — fixed by
  IP-1063, VERIFIED via VR-1063`; `BL-0192`'s revisit trigger fires, `DEFERRED → SCHEDULED`; new
  entry `BL-0193` filed (Finding F1).
- **Pipeline journal (`docs/pipeline/pipeline-journal.md`)**: run recorded per `00-pipeline-manager`'s
  harvest step.

## Related

[`00-master-build-plan.md`](../00-master-build-plan.md) · [`packages/INDEX.md`](../packages/INDEX.md) ·
[`docs/requirements/03-requirements-traceability-matrix.md`](../../requirements/03-requirements-traceability-matrix.md)
