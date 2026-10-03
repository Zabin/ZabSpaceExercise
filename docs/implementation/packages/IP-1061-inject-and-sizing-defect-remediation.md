# IP-1061 — Inject Scheduling & Sizing-Cap Defect Remediation

> **Package ID:** IP-1061
> **Version:** 1.0
> **Status:** 🔵 COMPLETE *(implemented 2026-09-26 by `08-code-implementation`. All four defects
> fixed test-first: `_arm_schedule()` gained an initial-vs-re-arm distinction (A1), the two
> `space_weather` branches in `_h_inject()` were merged into one validating branch (A3), the
> `inject_library.yaml` comment was corrected (A2), and both hard-cap `ValueError` raises were
> removed from `build_world()` (A4). 5 new tests in `test_inject_library.py` (A1/A3); the 2
> `test_content.py` cap-enforcement tests were inverted to cap-removal tests in place (the 2
> at-limit tests were kept unchanged — still valid regardless of enforcement), so this package's
> own test count is +5 net. Full suite 603 passed/3 skipped (up from 598/3), both permanent
> gates green. Awaiting `09-package-verification` to advance to `VERIFIED`.)*
> **Dependencies:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.0 (`FR-4410`),
> [ADR-0019](../../architecture/adr/ADR-0019-sizing-guideline-not-engine-cap.md) (`NFR-1300`),
> [IP-1060](IP-1060-white-cell-dashboard.md) (`VERIFIED` — the as-built inject mechanism this
> package corrects)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0062`–`BL-0065`
> **Produces:** correct `at_sim_s: 0` inject firing without rewind double-fire; a single,
> validating `space_weather` inject branch; an accurate inject-library comment; removal of the
> hard satellite/constellation cap that contradicts ADR-0019
> **Feature Reference:** [FS-106 — White Cell Dashboard](../../features/FS-106-white-cell-dashboard.md)
> (`FR-4410` slice) + `NFR-1300` (no owning FS — RTM `UNASSIGNED`; ADR-0019 is the authority)
> **Supersedes:** none — new remediation package
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py),
> [`spacesim/content/inject_library.yaml`](../../../spacesim/content/inject_library.yaml)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package. Source: an external user validation report dated 26 Sep 2026 and filed by
`00-intake` as `BL-0062`–`BL-0065`. All four defects were confirmed against the live tree at
`32ca02a` when intake filed them. The line citations below were re-checked when this package was
written. Two decisions were made up front: A2 is fixed by correcting the comment only, with no
new route (user decision, 2026-09-26), and for A4 the code moves to match the ADR-0019 / NFR-1300
baseline rather than the baseline moving to match the code.*

## Package ID

IP-1061

## Title

Inject Scheduling & Sizing-Cap Defect Remediation

## Objective

Correct four shipped defects without adding any capability:

1. **A1 (`BL-0062`).** A vignette time inject at `at_sim_s: 0` must fire at session start.
   Rewinds must still never re-fire an inject that has already fired.
2. **A2 (`BL-0063`).** The inject-library header comment must name the real scheduling route.
3. **A3 (`BL-0064`).** The unreachable duplicate `space_weather` branch must be merged into one
   branch that validates severity.
4. **A4 (`BL-0065`).** `build_world()` must stop rejecting vignettes above ~24 satellites or
   above 3 per constellation, as ADR-0019 and `NFR-1300` already require.

## Feature Reference

[FS-106 — White Cell Dashboard](../../features/FS-106-white-cell-dashboard.md) (`FR-4410` —
immediate and scheduled inject application). A4 traces to `NFR-1300` / ADR-0019 directly; no
Feature Specification owns `NFR-1300` (the RTM row is `UNASSIGNED`).

## Requirements Covered

| Req ID | Title (abridged) | How this package covers it |
|---|---|---|
| FR-4410 | Immediate and scheduled inject application | A1: a scripted time inject at exactly the start epoch is applied, and future-scheduled injects still replay byte-identically across rewind (no double-fire). A3: the `space_weather` effect is applied through one deterministic branch. A2: the operator-facing library comment matches the real `POST /api/sessions/{sid}/inject` + `at_sim_t` interface. |
| NFR-1300 | Sizing is a soft guideline, not an engine-enforced cap | A4: the two `ValueError` raises in `build_world()` are removed. Sizing pressure stays with the existing clock-lag watchdog (`SessionManager._record_catch_up_lag`), as ADR-0019 states. |

## Architecture Components

- **C2 Session / Application Layer.** Two changes in `session/manager.py`:
  - `_arm_schedule()` (`:139-148`) gains an initial-vs-re-arm distinction.
  - `_h_inject()` (`:598ff`) merges its two `space_weather` branches (`:627` live, `:646` dead).
- **C5 Content & Data.** Two changes:
  - `content/vignette.py` `build_world()` (`:200-213`) loses its hard caps.
  - The `content/inject_library.yaml` header comment (`:19`) is corrected.
- **C1 Simulation Engine: no change.** `engine/simulation.py`'s `rewind_to()` (`:82-94`) keeps
  every event-log entry with `sim_time <= t`. That is the property the A1 re-arm rule relies on,
  and it is read, not modified. Determinism invariant 1 is unaffected: no wall-clock read and no
  RNG draw is added.

## Interfaces

- **No public API change.** `POST /api/sessions/{sid}/inject` and `InjectRequest.at_sim_t`
  (`ui_web/server.py:80-82`, `:341-344`) are unchanged; A2 only corrects the comment that
  documents them.
- **Scripted-inject event payload gains one key.** Scripted time injects scheduled by
  `_arm_schedule()` carry `inject_id` (the vignette `Inject.id`) alongside `effects` in their
  `"inject"` event payload. `_h_inject()` ignores unknown keys, so the key is inert on apply. It
  exists only so a re-arm can recognise an already-logged firing.
- **`space_weather` effect contract after A3:**
  - `severity` ∈ {`none`, `minor`, `severe`}; `clear` is an alias for `none`.
  - Any other value is coerced to `minor`, the dead branch's existing rule. Coercion is chosen
    over rejection so a malformed inject cannot abort a running exercise.
  - `world.space_weather` is reset to `{"severity": sev}`, and one message goes to all three
    cells.

## Files to Create

None. All tests go into existing test files (see Tests to Add).

## Files to Modify

| File | Change |
|---|---|
| `spacesim/session/manager.py` | `start()` (`:134-137`) arms with an *initial* flag; `rewind_to()` (`:250-256`) arms with a *re-arm* flag. `_arm_schedule()` (`:139-148`): see Implementation Tasks 1–2. `_h_inject()`: merge the `:627` and `:646` `space_weather` branches into one. |
| `spacesim/content/vignette.py` | Remove the `len(orbital) > 24` and the per-group `> 3` `ValueError` raises and their `Counter` scaffolding (`:200-213`). Replace the "Enforce v1 satellite caps (build-spec …)" comment with one citing ADR-0019 / `NFR-1300` (soft guideline; clock-lag watchdog is the backstop). |
| `spacesim/content/inject_library.yaml` | Line 19: replace `POST /api/sessions/{sid}/inject_schedule with at_sim_t` with `POST /api/sessions/{sid}/inject with an at_sim_t field (µs sim-UTC)`. Comment only. |
| `spacesim/tests/test_content.py` | Invert the four cap tests at `:101-125+`: 25 orbital assets and 4 satellites in one group must now **load without error**. Rename them accordingly and retitle the section header to ADR-0019. |
| `spacesim/tests/test_inject_library.py` | Add the A1 and A3 regression tests (see Tests to Add). |
| `docs/FUTURE-WORK.md` | §6 ("Sat / fleet caps validation — ✅ implemented"): rewrite to record that the hard cap was removed per ADR-0019 / `NFR-1300` by IP-1061, leaving only the soft guideline and the watchdog. |
| `docs/vignettes/00-LIBRARY-ARCHITECTURE.md` | `:180` "Satellite caps" bullet: restate as a soft sizing guideline (ADR-0019), not an enforced load-time rule. |

## Implementation Tasks

Test-first: write each test in Tests to Add, watch it fail against the current tree, then make
the change.

1. **A1, initial arming.** Give `_arm_schedule()` a keyword flag distinguishing the initial arm
   from a re-arm:
   - `start()` passes initial. The time-inject guard becomes `at >= from_t`, so an inject at
     `start_epoch` is scheduled at `now`.
   - `Simulation.advance_to()` pops events due `<= target`, so the inject fires on the first
     advance. It is logged at `sim_time == start_epoch`.
   - Every scripted time inject's scheduled payload includes `inject_id`.
2. **A1, re-arm after rewind.** `rewind_to(t)` passes re-arm. The guard is:
   - schedule if `at > t`; or
   - schedule if `at == t` **and** no retained event-log entry has `kind == "inject"`,
     `sim_time == t` and `payload.get("inject_id") == inj.id`.
   Because rewind keeps entries with `sim_time <= t`, an inject that already fired at `t` is
   found and skipped (no double fire). One that never fired (e.g. a rewind to `start_epoch`
   before the first advance) is re-armed (no lost inject). Bus ticks keep their current
   `start=from_t` behaviour, which is out of scope.
3. **A3.** Replace both `space_weather` branches with a single branch at the first branch's
   position:
   - read `severity`, default `minor`;
   - map `clear` → `none`;
   - coerce any value outside {`none`, `minor`, `severe`} to `minor`;
   - set `world.space_weather = {"severity": sev}`;
   - append the existing `Space weather: severity=…` message to `white`, `blue` and `red`.
   Delete the unreachable second branch.
4. **A2.** Correct the `inject_library.yaml:19` comment as specified in Files to Modify.
5. **A4.** Remove both raises in `build_world()`, update the comment, and invert the
   `test_content.py` cap tests.
6. **Docs.** Apply the FUTURE-WORK §6 and `00-LIBRARY-ARCHITECTURE.md` edits. Add IP-1061 to
   the RTM `Impl. Package` cells for `FR-4410` (alongside `IP-1060`) and `NFR-1300` (replacing
   `UNASSIGNED`).
7. Run the full suite and both permanent gates, then flip this package to `COMPLETE`.

## Tests to Add

All tests below go in `spacesim/tests/test_inject_library.py` unless stated otherwise.

- **`test_time_inject_at_zero_fires_at_start` (A1).** Build a vignette with a single
  `{trigger: {type: time, at_sim_s: 0}, effects: [message → blue, text "t0"]}` inject. Then
  `start()`, `set_clock(False)`, `step(10)`. Exactly one `t0` message exists, stamped at
  `start_epoch`. Fails today (0 messages).
- **`test_rewind_does_not_refire_fired_inject` (A1).**
  1. Arm an inject at `at_sim_s: 5`, step 10 s, then `rewind_to(start_epoch + 5 s)` and step 10 s.
  2. Exactly one message remains, and the inject's log entry appears exactly once.
  3. Repeat with an `at_sim_s: 0` inject and a rewind to `start_epoch`, after a step: again
     exactly one firing.
- **`test_rewind_to_start_before_first_advance_keeps_zero_inject` (A1).** Arm an inject at
  `at_sim_s: 0`, then `start()`, `set_clock(False)`, `rewind_to(start_epoch)` (no step in
  between), then `step(10)`. Exactly one firing: the inject is neither lost nor duplicated.
- **`test_space_weather_invalid_severity_coerced` (A3).** Fire
  `{type: space_weather, severity: "bogus"}`. `world.space_weather == {"severity": "minor"}`,
  and the message reports `minor`. Fails today (`bogus` is stored).
- **`test_space_weather_clear_alias_and_message` (A3).** `severity: "clear"` resolves to `none`,
  and exactly one `Space weather:` message is posted to all three cells.
- **In `spacesim/tests/test_content.py` (A4):**
  - `test_vignette_above_24_satellites_loads` (25 orbital assets build without error);
  - `test_constellation_above_3_loads` (4 in one group build without error).
- **Permanent gates:** `spacesim/tests/test_determinism.py` and
  `spacesim/tests/test_import_guard.py` must stay green. The whole suite must pass
  (baseline 598 passed / 3 skipped; the expected new count is baseline + 5 added tests, with the
  4 cap tests replaced by 2).

## Documentation Updates

- `docs/FUTURE-WORK.md` §6 and `docs/vignettes/00-LIBRARY-ARCHITECTURE.md:180` (see Files to
  Modify).
- RTM (`docs/requirements/03-requirements-traceability-matrix.md`): add IP-1061 to the
  `Impl. Package` cells of `FR-4410` and `NFR-1300`, and name the new tests in their test columns.
- `docs/training/15-manual-traceability.md` §15.1: check the inject-firing and vignette-loading
  rows. If a manual section states the 24/3 cap as enforced, or states that a 0 s inject cannot
  fire, route that as a manual-impact finding to `08-training-manual-authoring` rather than
  editing `docs/training/` from `08-code-implementation`.
- `CLAUDE.md` already states "no engine-enforced cap" and needs no change. Its code-map entry for
  `inject_library.yaml` does not cite the wrong route.
- This package's own Status header; the Master Build Plan row; `packages/INDEX.md`.

## Definition of Done

- A vignette time inject at `at_sim_s: 0` fires exactly once at session start.
- No scripted time inject fires twice across any rewind. A rewind to `start_epoch` before the
  first advance does not lose a 0 s inject.
- `_h_inject()` contains exactly one `space_weather` branch. It validates severity (coercing
  invalid values to `minor`), accepts `clear`, and posts a message.
- `inject_library.yaml` names `POST /api/sessions/{sid}/inject` + `at_sim_t` and nowhere names
  `inject_schedule`.
- `build_world()` raises no satellite-count or constellation-size error. The four old cap tests
  are replaced by the two "loads" tests.
- FUTURE-WORK §6, `00-LIBRARY-ARCHITECTURE.md:180` and the RTM cells are updated.
- The full suite is green and both permanent gates are green.

## Verification Checklist

- [x] `grep -c 'kind == "space_weather"' spacesim/session/manager.py` returns `1`.
- [x] `grep -n inject_schedule -r spacesim/` returns no hits (a pre-existing, unrelated test name,
      `test_fire_inject_scheduled_...`, contains `_scheduled_` not `_schedule` and does not match).
- [x] `grep -n "satellite cap\|constellation(s) exceed" spacesim/content/vignette.py` returns no
      hits.
- [x] Each of the 7 new tests exists and passes. 4 of the 5 A1/A3 tests were observed failing
      before the fix; `test_space_weather_clear_alias_and_message` already passed pre-fix (the
      live branch already handled `clear` correctly) — see Outstanding Issues in the
      Implementation Summary.
- [x] The intake reproduction script (the `BL-0062` / `BL-0064` evidence) re-run against the
      fixed tree:
  - `at_sim_s: 0` gives 1 message;
  - `bogus` severity gives `minor`.
- [x] `python3 -m pytest` passes in full (603 passed, 3 skipped). `test_determinism.py` and
      `test_import_guard.py` pass.
- [x] No file under `spacesim/engine/` was modified.
- [x] The RTM `FR-4410` / `NFR-1300` rows cite IP-1061.
- [x] The Master Build Plan row, the `packages/INDEX.md` row and this header all agree on status
      (`COMPLETE`).

## Dependencies

- **Package:** [IP-1060](IP-1060-white-cell-dashboard.md), `VERIFIED` (2026-07-04,
  [`VR-1060`](../verification/VR-1060-white-cell-dashboard.md)). This package corrects the inject
  mechanism IP-1060 documents as built.
- **Authorization:** granted 2026-09-26 (MSTR-006 §3).
- **Parallelism:** no ordering constraint with [IP-1174](IP-1174-vignette-creator-ui-surfaces.md)
  (disjoint files, except that both *read* `content/vignette.py`). The user chose to build this
  package first.

## Risks

- **Old saved sessions.** Their scripted-inject log entries predate `inject_id`. A rewind to
  exactly an inject's time in such a session could re-arm an already-fired inject, because the
  lookup cannot match an absent key. Mitigation:
  - the case needs a legacy save, a rewind to the exact microsecond of a scripted inject, and
    that inject still pending;
  - it is narrow and only affects saves made before this package.
  Record it in the Implementation Summary. Do not add a payload-equality fallback unless
  verification finds the case reachable in the shipped vignettes.
- **Bus ticks share `_arm_schedule`.** Only the inject guard changes. Bus-tick re-arming at
  `from_t` is left exactly as is, to avoid perturbing determinism baselines.
- **Uncapped vignettes on weak hardware.** Removing the cap lets large vignettes load. ADR-0019
  accepts this, with the clock-lag watchdog as the backstop; no new mitigation is in scope.
- **Hidden cap dependants.** Other tests or docs may assert the cap (e.g. a vignette-library test
  counting on the `ValueError`). `08` must grep for `≤24`, `satellite cap` and `constellation`
  across `spacesim/tests/` and `docs/` at implementation time and treat any hit as in-scope drift.

## Rollback Considerations

The change is purely subtractive or local. Reverting the implementing commit restores the prior
behaviour exactly: the `inject_id` payload key is inert on apply, and no schema, API or
persisted-format field is added. No data migration is needed. If only A4 were to be rolled back,
that would conflict with ADR-0019 and would need a superseding ADR, not a code revert.
