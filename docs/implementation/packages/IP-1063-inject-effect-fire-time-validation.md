# IP-1063 — Inject Effect Fire-Time Validation (malformed payloads + unmet target preconditions)

> **Package ID:** IP-1063
> **Version:** 1.0
> **Status:** 🟢 READY *(authored 2026-10-11, `07-implementation-planning`, pipeline run #110.
> Every dependency is `VERIFIED`. **Authorized** by the project owner on 2026-10-11 under the
> session pre-authorization of this iteration's packages, MSTR-006 §3. This follows the same
> precedent as `IP-1261`/`IP-1262`.)*
> **Dependencies:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.1 (`FR-4410`,
> `FR-4430`), [IP-1062](IP-1062-condition-triggered-injects-and-new-effects.md) (`VERIFIED`,
> `VR-1062` v2.0), [IP-1061](IP-1061-inject-and-sizing-defect-remediation.md) (`VERIFIED`; its "a
> malformed inject cannot abort a running exercise" posture is extended here, not changed)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0129` (from
> [VR-1062](../verification/VR-1062-condition-triggered-injects-and-new-effects.md) M1) and
> `BL-0188` (from [REV-TRN-003](../../reviews/training-review-run102-scope.md) F2)
> **Produces:** an inject path that (a) **rejects**, at the White Cell boundary, any inject whose
> effects are malformed or whose FR-4430 target precondition is unmet, applying nothing and naming
> the reason; and (b) **never raises mid-handler** for an inject that bypasses that boundary
> (vignette-authored time/condition injects). An invalid effect is skipped whole, leaving no
> partial mutation, and White receives a message.
> **Feature Reference:** [FS-106 — White Cell Dashboard](../../features/FS-106-white-cell-dashboard.md)
> v2.1, Error Handling ("the source document does not enumerate failure modes for inject
> scheduling") and `FR-4430`'s Precondition
> **Supersedes:** none — this is a new remediation package
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*This is a remediation package. It has two sources: `BL-0129` (Medium, `VR-1062` M1, open and
`SCHEDULED` for `07` since 2026-09-27) and `BL-0188` (Low, REV-TRN-003 F2, reproduced live in
pipeline run #108). Both live in the same seam, the inject-effect dispatch in
`session/manager.py`, and are fixed by the same mechanism: one pure validator used at two points.
It is numbered `IP-1063` as the next slice of the FS-106 inject series after `IP-1062`. `IP-1061` and
`IP-1062` are `VERIFIED` and are not reopened. Every file, function and line cited below was
re-checked against the tree at `470be0d`.*

## Package ID

IP-1063

## Title

Inject Effect Fire-Time Validation (malformed payloads + unmet target preconditions)

## Objective

1. **`BL-0129` — no mid-handler exceptions.**
   - `SessionManager._apply_inject_effects` (`manager.py:933-1066`) indexes payload keys directly:
     `eff["to"]`/`eff["target"]` (reveal_asset), `eff["target"]` (patch_cyber_vuln, gs_outage,
     anomaly, sensor_outage, scripted_manoeuvre), and `eff["cell"]`/`eff["mode"]`
     (forced_custody_loss, scripted_manoeuvre).
   - `scripted_manoeuvre` also calls `engine.maneuver.compute_maneuver`, which raises `ValueError`
     on an unknown mode (`maneuver.py`, the final `else` of its mode dispatch) or on bad
     mode-specific params.
   - A malformed effect therefore raises **inside the deterministic handler**, after earlier
     effects in the same inject have already mutated `world`. That leaves an unlogged partial
     mutation, so the live state diverges from replay. `VR-1062` M1 confirmed this still holds
     after `IP-1062`'s remediation.
2. **`BL-0188` — no silent accepted no-op.** An `anomaly` effect (either subsystem) on an asset
   with `bus_state is None` falls through the guard
   `if asset is not None and asset.bus_state is not None` (`:1020`). That changes nothing, and
   `POST /inject` still answers `{"ok": true}`. White gets no signal.
   - In practice this applies to every shipped Red satellite: 9 of 9 have no `bus_state`
     (REV-TRN-003).
   - The same silent no-op applies when any FR-4430 effect names an absent target. `IP-1062`'s
     Design Decision 2 made "missing target ⇒ no-op" deliberate **inside the handler**, and this
     package keeps that.
   - The White-facing boundary, though, should not report success for an inject that cannot land.
     `FR-4430`'s own Precondition is "the targeted Asset/Sensor/Track exists in the current
     `WorldState`".

### Design Decisions

1. **One pure validator, two call sites.** Add `validate_inject_effects(world, effects, *,
   check_targets) -> list[str]` in `session/manager.py`. It is a module-level function, or a
   `@staticmethod` next to `_apply_inject_effects`, as `08` prefers. It mutates nothing and draws
   no RNG, so it is safe to run inside the handler under replay. It returns one human-readable
   problem string per invalid effect, each prefixed with the effect's index and type; an empty
   list means valid.
   - **Structural checks (always):**
     - `effects` is a list, and each effect is a dict with a string `type` from the known set:
       the twelve handled types in `_apply_inject_effects`.
     - Required keys per type: `reveal_asset` → `to`, `target`; `patch_cyber_vuln` / `gs_outage` /
       `anomaly` / `sensor_outage` → `target`; `forced_custody_loss` → `cell` ∈ {`blue`,`red`} plus
       `target`; `scripted_manoeuvre` → `target` plus `mode` ∈ the six `compute_maneuver` modes
       (`eci`/`lvlh`/`finite_burn`/`target_coe`/`hohmann`/`plane_change`).
     - `anomaly.subsystem` ∈ {`bus`,`telemetry`}.
     - `forced_custody_loss.degrade_to`, if present, must be float-coercible.
     - `scripted_manoeuvre.params`, if present, must be a dict.
   - **Target-precondition checks (`check_targets=True` only):** `FR-4430`'s Precondition for the
     **four FR-4430 types only**.
     - `anomaly`: the target asset exists **and has a `bus_state`** (`BL-0188`).
     - `sensor_outage`: the target exists in `world.sensors`.
     - `forced_custody_loss`: `world.track_for(cell, target)` is not `None`.
     - `scripted_manoeuvre`: the target asset exists with an `orbit`, and a **dry run** of
       `compute_maneuver(...)` (pure, no `apply_impulse`) does not raise. This catches bad
       mode-specific params at the boundary.
   - The eight pre-FR-4430 types get structural checks only. Their missing-target posture
     (`FR-4410`, e.g. `gs_outage` on a non-ground-station) is left exactly as today; widening it
     is out of scope.
2. **Boundary: reject atomically** (`BL-0188`, `BL-0129` for White-authored injects).
   - `SessionManager.fire_inject` (`:780-797`) resolves `effects` as today. It then runs
     `validate_inject_effects(self.sim.world, effects, check_targets=True)` **before** scheduling
     or advancing anything.
   - On any problem it raises `ValueError("; ".join(problems))`. Nothing is scheduled, nothing is
     logged, and no clock moves.
   - `InProcessSession.fire_inject` (`inprocess.py:288-291`) catches that `ValueError` and returns
     `Ack(ok=False, reason=str(exc))`.
   - `POST /api/sessions/{sid}/inject` (`server.py:445-448`) raises `HTTPException(400,
     detail=ack.reason)` when `ack.ok` is false. The console's `api.post` only throws on a non-2xx
     status (`app.js:44-49`), so a 200 `{"ok": false}` would still render "✓ fired immediately" in
     `fireBuiltInject` (`app.js:380-400`). With a 400, the existing `catch` already shows the
     reason, so no `static/` change is required.
   - Precondition checks run against the world **at fire/schedule time**, for both immediate and
     future-dated injects (see Risks).
3. **Handler: skip, never raise** (`BL-0129` for injects that bypass the boundary).
   - At the top of each loop iteration in `_apply_inject_effects`, run the validator on that one
     effect with `check_targets=False`.
   - If it reports a problem, **skip that effect whole**, mutating nothing for it. Append one
     `world.messages` entry `{"to": ["white"], "text": "inject effect skipped: <problem>", "t":
     world.now}`, then continue with the next effect.
   - Separately, wrap only the pure `compute_maneuver(...)` call in the `scripted_manoeuvre` branch,
     catching `ValueError`/`KeyError`/`TypeError` raised by bad params. On failure, skip that effect
     with the same White message, **before** `apply_impulse` runs.
   - Both paths are pure functions of `(world, effect)`, so live and replay make identical
     decisions and append identical messages. Determinism is preserved.
   - **Target-precondition failures inside the handler stay silent no-ops**, unchanged:
     `IP-1062` Design Decision 2 and FS-106's open question on condition-triggered injects against
     deleted targets. Changing that is a `06` decision, not this package's.
4. **No change to valid injects.** Every inject that is well-formed and meets its precondition
   behaves byte-identically: same mutations, same messages, same event-log payload. Every shipped
   vignette inject and every `inject_library.yaml` template must validate clean (Test 7).

## Feature Reference

- **FS-106** v2.1, Error Handling: "the source document does not enumerate failure modes for inject
  scheduling". This package supplies the boundary behaviour as a package-level Design Decision,
  the same way `IP-1062` Design Decision 2 supplied the handler's. It is routed upstream for
  ratification (see Risks); it does not block.
- **FR-4430** Precondition ("the targeted Asset/Sensor/Track exists in the current `WorldState`")
  and Postconditions (unchanged). **FR-4410** (immediate/scheduled application, byte-identical
  replay), unchanged for valid injects.

## Requirements Covered

| Requirement | How |
|---|---|
| `FR-4430` | The White-facing inject boundary enforces the stated Precondition for the four FR-4430 effect types, and an `anomaly` on a bus-less asset is rejected rather than reported as applied. Malformed FR-4430 payloads never raise mid-handler. |
| `FR-4410` | Malformed payloads of the keyed pre-FR-4430 types (`reveal_asset`, `patch_cyber_vuln`, `gs_outage`) never raise mid-handler. Byte-identical replay of valid injects is preserved (Test 6 + determinism gate). |

No requirement text is changed. Determinism invariant 1 (CLAUDE.md, `NFR` determinism family) is
cited as the motivation for Design Decision 3; it is not newly claimed.

## Architecture Components

- `session/` layer: `session/manager.py` (the new validator; `fire_inject`;
  `_apply_inject_effects`) and `session/inprocess.py` (`fire_inject` maps `ValueError` to `Ack`).
- `ui_web/server.py`: the `/inject` route maps `Ack(ok=False)` to 400.
- `engine/` untouched. `compute_maneuver` is called read-only, exactly as the handler already calls
  it. The import guard and determinism gates are unaffected by construction.

## Interfaces

- **New:** `validate_inject_effects(world, effects, *, check_targets: bool) -> list[str]`. It is
  pure and has no side effects.
- **Changed:**
  - `SessionManager.fire_inject(inject, at_sim_t=None) -> None` keeps its signature. It newly
    raises `ValueError` (message: the joined problems) for an invalid inject, and applies and
    schedules nothing in that case.
  - `InProcessSession.fire_inject(...) -> Ack` keeps its signature. It newly returns
    `Ack(ok=False, reason=...)` for an invalid inject.
- **HTTP:** `POST /api/sessions/{sid}/inject` newly returns **400** with `detail` = the reason for
  an invalid inject. A valid inject still gets 200 with `{"ok": true, "reason": ""}`, unchanged.
- **Handler:** `_apply_inject_effects` keeps its signature. An invalid effect is skipped with one
  White message instead of raising. Valid effects are unchanged.

## Files to Create

None.

## Files to Modify

| File | Change |
|---|---|
| `spacesim/session/manager.py` | Add `validate_inject_effects` (Design Decision 1). Call it in `fire_inject` (`:780-797`) before scheduling and raise `ValueError` on problems (Design Decision 2). Add the per-effect skip-and-message guard at the top of the loop in `_apply_inject_effects` (`:938`), plus the `compute_maneuver` try/except in the `scripted_manoeuvre` branch (`:1051-1066`) (Design Decision 3). Docstrings. |
| `spacesim/session/inprocess.py` | `fire_inject` (`:288-291`): catch `ValueError` from `mgr.fire_inject` and return `Ack(ok=False, reason=str(exc))`. |
| `spacesim/ui_web/server.py` | `inject` route (`:445-448`): `if not ack.ok: raise HTTPException(status_code=400, detail=ack.reason)`. Docstring. |
| `spacesim/tests/test_inject_effects_v2.py` | New tests (below). |
| `spacesim/tests/test_web.py` | New route-level test (below). |

## Implementation Tasks

1. Write Tests 1–7 first. Observe Tests 1–5 fail against the current tree, recording each failure
   mode (`KeyError`/`ValueError` raised, or `ok: true` returned). Test 6 (replay parity on the
   skip path) fails today because the handler raises. Test 7 (shipped content validates clean)
   passes on arrival as a guard; that is expected.
2. Implement `validate_inject_effects` per Design Decision 1.
3. Wire the boundary (Design Decision 2) through `manager.fire_inject`, `inprocess.fire_inject` and
   the `/inject` route.
4. Wire the handler guard (Design Decision 3).
5. Re-run Tests 1–7 and the existing inject tests: `test_inject_effects_v2.py`,
   `test_inject_library.py`, `test_future_work.py`, `test_session.py`, `test_aar.py`,
   `test_telemetry.py`, `test_ephemeris.py`, `test_cell_activity.py`. **None may need changing.**
   The existing handler-level no-op tests (e.g. `test_forced_custody_loss_missing_target_is_a_no_op`,
   `test_scripted_manoeuvre_missing_asset_is_a_no_op`) call `_apply_inject_effects` directly, and
   Design Decision 3 keeps their behaviour. If any `mgr.fire_inject(...)` call site in the suite
   targets an absent object, stop and report: that would be a scope signal, not something to patch
   around.
6. Run the full suite and both permanent gates.

## Tests to Add

1. `test_inject_effects_v2.py`: `validate_inject_effects` returns a problem for each of these:
   - an `anomaly` with no `target`;
   - an `anomaly` with `subsystem: "power"`;
   - a `forced_custody_loss` with no `cell` and one with `cell: "purple"`;
   - a `scripted_manoeuvre` with `mode: "warp"`;
   - an effect with no `type`, and one with an unknown `type`;
   - a `reveal_asset` with no `to`.

   It returns `[]` for a well-formed example of each of the four FR-4430 types.
2. `test_inject_effects_v2.py` (`BL-0188`): on a manager whose world has a satellite with
   `bus_state=None`, `mgr.fire_inject([{"type": "anomaly", "target": <it>, "subsystem": "bus"}])`
   raises `ValueError` whose message names the target and the missing bus. The event-log length and
   `sim.clock.now` are unchanged afterwards.
3. `test_inject_effects_v2.py`: `mgr.fire_inject` is **atomic**. An inject of `[valid message,
   malformed anomaly]` raises `ValueError`, and `world.messages` does **not** contain the valid
   message, so nothing was applied.
4. `test_inject_effects_v2.py` (`BL-0129`): `_apply_inject_effects(world, [valid message,
   malformed forced_custody_loss (no cell), valid sensor_outage])` does **not** raise. Afterwards:
   - the first and third effects are applied;
   - the second is skipped;
   - exactly one `world.messages` entry addressed `["white"]` and starting `inject effect skipped`
     exists.
5. `test_web.py`: `POST /api/sessions/{sid}/inject` with an `anomaly` on a nonexistent target →
   **400**, with `detail` naming the target. A well-formed `message` inject → 200 and `ok: true`,
   unchanged.
6. `test_inject_effects_v2.py` (determinism of the skip path): schedule a **vignette-style** inject,
   bypassing `fire_inject`'s boundary by calling `mgr.sim.schedule(t, "inject", {"effects": [...]})`
   directly. Use a malformed second effect and a `scripted_manoeuvre` with params that make
   `compute_maneuver` raise. Advance past it, then `replay()` the event log from the initial state.
   The replayed world equals the live world, including both skip messages.
7. `test_inject_effects_v2.py`: every inject in every shipped vignette (`list_vignettes()` →
   `load_vignette`) and every template in `content/inject_library.yaml` passes
   `validate_inject_effects(..., check_targets=False)` with no problems. This is a regression
   guard that the known-type set and required keys match shipped content.

## Documentation Updates

- RTM (`docs/requirements/03-requirements-traceability-matrix.md`): add `IP-1063` and the new tests
  to the `FR-4430` and `FR-4410` rows' `Impl. Package` cells.
- `CLAUDE.md` code map: one clause on the `session/` bullet noting inject fire-time validation
  (reject at boundary, skip in handler).
- `docs/training/15-manual-traceability.md` §15.1: this changes operator-visible White behaviour.
  An invalid inject now shows "✗ … 400" with a reason instead of "✓ fired", and White may see an
  "inject effect skipped" message. Route a manual-impact finding for `WCM-5` (Injects), and
  `10-ui-reference.md` §10.3 if its builder rows describe the result line, to
  `08-training-manual-authoring`. Do **not** edit `docs/training/` from `08`.
- This package's Status header, the Master Build Plan row, `packages/INDEX.md`, and `ROADMAP.md`'s
  implementation-package row.

## Definition of Done

- A White-fired inject (immediate or scheduled) that is malformed, or whose FR-4430 target
  precondition is unmet, is rejected before anything is scheduled or applied:
  - `ValueError` from `SessionManager`;
  - `Ack(ok=False)` from `InProcessSession`;
  - **400** from `POST /inject`, with the reason.
- An `anomaly` on a bus-less asset is rejected that way (`BL-0188`).
- `_apply_inject_effects` never raises on a malformed effect. It skips that effect whole with one
  White message and applies the rest. Live and replay agree (`BL-0129`).
- Valid injects behave byte-identically. Every pre-existing inject test passes unchanged. All
  shipped vignette injects and library templates validate clean.
- RTM, `CLAUDE.md` and the ledgers are updated, and the manual-impact finding is routed.
- The full suite is green, and both permanent gates (`test_determinism.py`, `test_import_guard.py`)
  are green.

## Verification Checklist

- [ ] `git diff` of the implementing commit touches no file under `spacesim/engine/`.
- [ ] `grep -n "validate_inject_effects" spacesim/session/manager.py` shows the definition and
      **both** call sites (`fire_inject` and `_apply_inject_effects`).
- [ ] The `fire_inject` call precedes every `self.sim.schedule(...)` in that method (read it).
- [ ] Tests 1–7 exist and pass. Tests 1–6 were observed failing first, as recorded in the
      Implementation Summary.
- [ ] Independent reproduction on `geo-rpo-shadowing`: `POST /inject` with `{"type": "anomaly",
      "target": "RED-INSP", "subsystem": "bus"}` → 400. The same inject on `BLUE-HVA` → 200, and
      `bus_mode` becomes `safe_mode`.
- [ ] Independent reproduction of `BL-0129`: a scheduled inject with a malformed second effect
      advances without an exception, and `replay()` reproduces the live world.
- [ ] No pre-existing test file was modified except by additions (`git diff --stat`).
- [ ] `python3 -m pytest` passes in full, and `test_determinism.py` and `test_import_guard.py` pass.
- [ ] The RTM `FR-4430`/`FR-4410` rows cite `IP-1063`.
- [ ] The Master Build Plan row, the `packages/INDEX.md` row, `ROADMAP.md`'s row and this header
      agree on status.

## Dependencies

- **Packages:** `IP-1062` and `IP-1061`, both `VERIFIED`. This package edits the dispatch they
  established, so it is `READY`.
- **Authorization:** granted by the project owner 2026-10-11 (MSTR-006 §3) through the session
  pre-authorization of this iteration's packages.
- **Not dependencies:**
  - `BL-0187`, the open owner question on whether shipped Red satellites should get a `bus_state`.
    This package rejects the inject either way. If Red buses are later authored, those injects
    simply start being accepted.
  - `BL-0091` (scripted-manoeuvre Δv semantics), which is unchanged.
  - `BL-0184` (telemetry export 422 vs 400), a different seam and not planned here. See the TWBS
    note.
- **Parallelism:** there is no ordering constraint with any other open package.

## Risks

- **Future-dated inject against a not-yet-existing target.** The precondition is checked at
  schedule time against the current world, so White cannot pre-schedule an FR-4430 inject against
  an asset that will only be added later (e.g. by TLE force-add). No current workflow does this,
  and `FR-4430`'s own Precondition reads "current `WorldState`". If it is ever needed, relax
  `check_targets` for `when > now`; that is a one-line change. Disclosed rather than designed
  around.
- **Boundary behaviour is a package-level decision.** FS-106 v2.1's Error Handling explicitly does
  not enumerate inject failure modes. This package's reject-at-boundary decision should be ratified
  into FS-106 by `06-feature-specification`, together with the still-open FS-106 question on
  condition-triggered injects against deleted targets. That is a routed finding, not a blocker:
  the decision is the conservative one, because nothing is applied.
- **Known-type set drift.** A future effect type added to `_apply_inject_effects` but not to the
  validator's known set would be rejected at the boundary and skipped in the handler. Test 7 (all
  shipped content validates clean) and the validator living beside the dispatch keep this visible.
  The validator's docstring must say "extend alongside `_apply_inject_effects`".
- **White message volume.** One message per skipped effect. Only malformed authored content
  produces these, and Test 7 shows shipped content produces none.

## Rollback Considerations

Reverting the implementing commit restores the prior behaviour exactly: accept everything, raise
mid-handler on malformed payloads, and stay silent on bus-less anomalies. There are no schema,
`SavedSession`, persisted-format or event-log-shape changes. A saved session from before this
package replays identically after it, because valid injects are byte-identical. A pre-package save
containing a *malformed* scheduled inject would previously have raised on replay; it now replays
with a skip message instead. That is strictly more permissive, and it is disclosed.
