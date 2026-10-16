# IP-1041 — Observe-Order Remediation: Truthful `no_window` vs. `sensor_contended`, and Malformed Params Rejected Before Booking (FR-3210, FR-1610)

> **Package ID:** IP-1041
> **Version:** 1.0
> **Status:** 🔵 COMPLETE — 2026-10-16, `08-code-implementation`, pipeline run #133. `_plan_collection` reports `sensor_contended` only when a window was found and all were booked, else `no_window`; `_validate` rejects a malformed observe `beam_mode`/`look_angle_deg`/`duration_s`/`gain` as `invalid_param` (module helper `_observe_params_ok`, before the `auto` early return and before any booking) and drops an explicit `null` so it takes the absent default; `isr.beam_params` falls back on a non-string mode; `REASON_TIPS` gained `invalid_param`/`requires_cue` and a corrected `sensor_contended`. Tests: `test_observe_order_remediation.py` (29 collected; all but the contention and existing-reason cases seen failing first). Full suite 908 passed / 3 skipped (911 collected; baseline 879/3/882) (JUnit), gates 14/14.
> *(Was 🟢 READY — authored 2026-10-16 by `07-implementation-planning`, pipeline run #132.)*
> Authorized by the project owner 2026-10-11 (MSTR-006 §3) through the standing pre-authorization
> of the packages this iteration reaches. Same precedent as `IP-1222`/`IP-1221`/`IP-1212`/`IP-1063`.
> **Dependencies:** [FS-104](../../features/FS-104-sda-tasking.md) (Acceptance Criteria: contention
> and its resolution are visible; Error Handling: contention surfaces the conflict);
> [FS-122](../../features/FS-122-sensor-modality-models.md) v1.1 (`FR-1610` beam-mode request;
> `FR-1620`/`FR-1630` window removal); [IP-1040](IP-1040-sda-tasking.md) (`VERIFIED`, `VR-1040`;
> the as-built tasking path this package corrects); [IP-1222](IP-1222-sensor-modality-wiring-remediation.md)
> (`VERIFIED`, `VR-1222`; owns the observe-branch beam-mode lines and the `auto` cue filter this
> package sits next to)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0219`, `BL-0217`
> **Produces:** an observe order whose rejection reason says what actually happened (no window
> vs. every window booked); and an observe order with a malformed parameter that is rejected with a
> reason, through `dry_run` and `issue` alike, instead of an HTTP 500 that leaks a sensor booking.
> **Feature Reference:** [FS-104 — SDA Tasking](../../features/FS-104-sda-tasking.md);
> [FS-122 — Sensor Modality Models](../../features/FS-122-sensor-modality-models.md) v1.1 (`FR-1610`)
> **Related Topics:** [REV-TRN-006](../../reviews/training-review-runs122-127-scope.md) F2;
> [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [`spacesim/engine/isr.py`](../../../spacesim/engine/isr.py),
> [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package. Sources: `BL-0219` (REV-TRN-006 F2, Medium), found while reviewing the run #127
sensor-authoring prose; and `BL-0217` (`IP-1222` Outstanding Issues, Low), whose revisit trigger
fired because this package touches observe-order planning. Every file, function and line cited below
was checked against the tree at `9fc25a4`. `BL-0220` (the session-load 500) was proposed for the same
batch and is **not** in this package: see Risks and the TWBS section.*

## Package ID

IP-1041

## Title

Observe-Order Remediation: Truthful `no_window` vs. `sensor_contended`, and Malformed Params Rejected
Before Booking (FR-3210, FR-1610)

## Objective

Two defects in the shipped observe-order path, both on `OrderSystem`'s sensor-tasking seam:

1. **A windowless observe is reported as contention (`BL-0219`, Medium).** `_plan_collection`
   (`orders.py:411-446`) walks each candidate sensor's windows and takes the first one not booked.
   When none is chosen it sets `fail_reason = "sensor_contended" if sensor_ids else "no_window"`
   (`:431`). So whenever the cell owns a candidate sensor, the reason is `sensor_contended`, even if
   that sensor has **no window at all** in the look-ahead and nothing is booked. The console shows
   it as "Sensor is busy — it can service this only at a later window." (`app.js:178`). Reproduced
   (run #131, fresh sessions on `co-orbital-threat-escort`): a hosted camera with
   `min_range_km: 100000` (0 windows, 0 bookings, counted directly), a ground optical with
   `exclusion_angle_deg: 179`, and a shipped radar against a nonexistent target id all returned
   `sensor_contended`. `no_window` is reachable only when the cell owns no candidate sensor. This
   contradicts FS-104's "contention and its resolution are visible" (a contention that does not
   exist is shown), `09-troubleshooting-and-glossary.md`'s `no_window` entry, and the run #127
   prose that tells authors to use the preview to check whether a sensor can see a target.
2. **Malformed observe params crash the request and leak a booking (`BL-0217`, Low, widened).**
   `_validate`'s observe branch (`:486-499`) never looks at `order.params`, and returns early for
   `auto` (`:487-488`). `_exec_payload`'s observe branch then evaluates the params: `beam_mode`
   (`:706`) reaches `isr.beam_params`, whose `beam_mode in modes` (`isr.py:104`) raises
   `TypeError` for an unhashable value; `float(...)` on `look_angle_deg` (`:707`), `duration_s`
   (`:708`) and `gain` (`:745`) raises for a non-numeric value **or an explicit `null`**. Re-checked
   live at `9fc25a4` (`co-orbital-threat-escort` seed 3, `BLUE-RADAR`):
   - `beam_mode` as a list or a dict, `look_angle_deg: "abc"` and `gain: "high"` each give
     **HTTP 500** on `POST /order`. `POST /order/validate` (`dry_run`) returns `ok: true` for the
     same order, because `commit=False` never calls `_exec_payload` (`:437-446`). The preview and
     the order disagree.
   - Each 500 happens **after** the booking at `:439` and before `self.sim.schedule`, so the sensor
     keeps a phantom booking for an order that does not exist. Over the probe, successive orders'
     windows moved later, and the sixth order was refused `sensor_contended` because the leaked
     bookings had filled the horizon. A rewind rebuilds bookings from the event log only
     (`manager.py:405-415`), so live state and rebuilt state disagree until the next rewind.
   - The console itself can send `null`: `app.js:573-574` sends `parseFloat(...)` of the look-angle
     and duration fields, and a blank field gives `NaN`, which `JSON.stringify` writes as `null`.

After this package, the reason distinguishes "no window" from "every window booked", a malformed
observe param is refused with a reason before anything is booked, `dry_run` and `issue` agree, and
every well-formed order behaves exactly as today.

### Design Decisions

1. **`no_window` unless a window was actually found (`BL-0219`).** `_plan_collection` records
   whether any candidate returned at least one window. When no window is chosen, the reason is
   `sensor_contended` only if at least one window was found (so every one found was booked), and
   `no_window` otherwise, including the existing no-candidate case. This is the rule the command
   path already uses (`:381-384`: `"pass_capacity_full" if gs_windows_exist else "no_window"`), so
   the two planners now speak the same vocabulary. The `requires_cue` early return added by
   `IP-1222` (`:415-419`) is unchanged and still runs first. `dry_run` and `issue` share
   `_plan_collection`, so both get the fix.
2. **Malformed observe params are a validation failure (`BL-0217`, widened).** A new check runs in
   `_validate`'s observe branch **before** the `auto` early return, so it covers `auto` and named
   sensors alike, and it runs before any window search or booking. It rejects with a new reason,
   `invalid_param`, when:
   - `beam_mode` is present, not `None`, and not a string;
   - `look_angle_deg`, `duration_s` or `gain` is present, not `None`, and either cannot be converted
     by `float()` or converts to a non-finite value.

   Anything `float()` accepts today (an int, a float, a numeric string such as `"30"`) is still
   accepted, so no well-formed client changes behaviour. Rejecting rather than silently defaulting
   matches `_validate`'s existing posture for other bad inputs (`no_such_sensor`, `not_owner`), and
   keeps the operator told.
3. **An explicit `null` means "not given".** In `_exec_payload`'s observe branch, a param whose
   value is `None` takes the same default as an absent one (`look_angle_deg` 0.0, `duration_s`
   300.0, `gain` 1.0, no `beam_mode`). This makes the console's blank look-angle/duration fields
   (Objective 2) work instead of crashing, and is the only behaviour change for an order that does
   not crash today: none, because every such order crashes today.
4. **`isr.beam_params` treats a non-string mode as unrecognised.** `beam_params`' docstring already
   says an unrecognised `beam_mode` falls back to the default mode (`isr.py:96-106`). A non-string
   value is unrecognised, so a type guard before the membership test returns the default instead of
   raising. This is defence in depth for direct engine callers and the execute-time call at
   `orders.py:1006`; with Design Decision 2 the order path never reaches it with a non-string.
   `IP-1222`'s own radar check is already `isinstance`-guarded (`:735-737`) and is unchanged.
5. **Console tips match the reasons.** `REASON_TIPS` in `app.js` (`:166-183`) gains `invalid_param`
   and `requires_cue` (the latter shipped in `IP-1220`/`IP-1222` with no tip), and the
   `sensor_contended` text is corrected to what the reason now means: every window in the planning
   horizon is already booked for this sensor. No other UI code changes.
6. **Scope boundary.** Only the observe action. `jam` (`power_w`, `bandwidth_hz`,
   `victim_bandwidth_hz`, `:616-622`) and `engage` (`salvo_n`, `:661`) have the same unguarded
   `float()`/`int()` pattern; they are filed for a later pass rather than widened here (Risks).

## Feature Reference

- **FS-104** (SDA Tasking): Acceptance Criteria ("When multiple tasking requests contend for the same
  sensor, the contention and resolution are visible") and Error Handling ("Sensor contention must
  surface the conflict and its resolution"). A false contention report breaks both.
- **FS-122** v1.1: `FR-1610` (the order's `beam_mode` request, User Workflow 1) and the
  window-removal rows (`FR-1620` exclusion, `FR-1630` range floor), whose effect an author checks
  through the preview.

## Requirements Covered

FS-104's own "Requirements Implemented" field cites no FR (a documented traceability gap,
unchanged here). Coverage, following `IP-1040`'s RTM mapping:

| Req ID | How this package covers it |
|---|---|
| `FR-3210` | Single-task contention: a rejection is labelled contention only when a window existed and was booked; a malformed request no longer leaves a phantom booking that creates false contention. |
| `FR-1610` | The order's `beam_mode` request: a non-string value is refused with a reason instead of crashing. |

`FR-1620`, `FR-1630`, `FR-1640` and `FR-3410` are consumed and not changed.

## Architecture Components

- **C1 Simulation Engine:** `engine/orders.py` (`_validate`, `_plan_collection`, the observe branch
  of `_exec_payload`); `engine/isr.py` (`beam_params`).
- **C6 UI (web):** `ui_web/static/app.js` `REASON_TIPS` text only.
- No session, content, server-route, or access-predicate change. `access.py` is not touched.

## Interfaces

- `INT-0008` (SessionManager → Engine OrderSystem), the interface the RTM lists for `FR-3210`. No new
  interface, route, request field or response field. `OrderAck.reason` may now carry
  `invalid_param`, and carries `no_window` where it used to carry `sensor_contended` for a windowless
  sensor.

## Files to Create

- `spacesim/tests/test_observe_order_remediation.py` — this package's tests (Tests 1–9).

## Files to Modify

- `spacesim/engine/orders.py`:
  - `_plan_collection` (`:411-446`): record whether any window was found; choose the reason at
    `:431` per Design Decision 1.
  - `_validate` (`:482-499`): the observe-param check before the `auto` early return at `:487-488`
    (Design Decision 2).
  - `_exec_payload` observe branch (`:698` onward): `None` → default for `beam_mode` (`:706`),
    `look_angle_deg` (`:707`), `duration_s` (`:708`) and `gain` (`:745`) (Design Decision 3).
- `spacesim/engine/isr.py` — `beam_params` (`:96-106`): non-string `beam_mode` treated as
  unrecognised (Design Decision 4).
- `spacesim/ui_web/static/app.js` — `REASON_TIPS` (`:166-183`) (Design Decision 5).

## Implementation Tasks

1. Mark this package `IN PROGRESS` on the Master Build Plan, `packages/INDEX.md` and `ROADMAP.md`
   before any edit.
2. Write Tests 1–9 and see them fail. Tests 3 and 9 assert unchanged behaviour and may pass on
   arrival; record which did.
3. Fix the reason choice in `_plan_collection` (Design Decision 1).
4. Add the observe-param validation, the `None` → default handling, and the `beam_params` guard
   (Design Decisions 2–4).
5. Update `REASON_TIPS` (Design Decision 5).
6. Run the full suite and both permanent gates; fix only what this package broke.
7. Update the documentation and ledgers (Documentation Updates), then mark `COMPLETE`.

## Tests to Add

All in `spacesim/tests/test_observe_order_remediation.py`. Fixtures may reuse
`test_sensor_modality_wiring.py`'s `_leo`/`_world`/`_radar`/`_osys` construction; the HTTP cases use
`fastapi.testclient.TestClient` on a shipped vignette, as `test_validate_order.py` does.

1. **Windowless sensor → `no_window`.** A cell's only sensor has no window to the target in the
   horizon (e.g. a space-based sensor with a `min_range_km` larger than any achievable range). A
   named observe and an `auto` observe are both rejected `no_window`, through `issue` and `dry_run`,
   and no booking exists afterwards. *(`BL-0219`)*
2. **Every window booked → `sensor_contended`.** A sensor with at least one window whose windows in
   the horizon are all booked (fill them with prior accepted orders, or seed `_sensor_bookings` over
   the whole horizon) is rejected `sensor_contended`. *(Design Decision 1, the contention case still
   reported)*
3. **No candidate sensor → `no_window` (regression).** `test_sensor_modality_wiring.py`'s
   `test_auto_with_no_sensor_keeps_existing_reason` must pass unmodified; this file adds no
   duplicate of it, but asserts the same for a named sensor id the cell does not own being rejected
   by its existing reason (`not_owner`), unchanged.
4. **Unknown target → `no_window`.** A shipped vignette's own radar observing a target id that does
   not exist is rejected `no_window`, not `sensor_contended`. *(REV-TRN-006 F2 repro)*
5. **Malformed params rejected by both paths.** For each of `beam_mode: ["fence"]`,
   `beam_mode: {"a": 1}`, `beam_mode: 3`, `look_angle_deg: "abc"`, `gain: "high"`,
   `duration_s: "long"`, `look_angle_deg: "inf"` and `gain: float("nan")`, an observe is rejected
   `invalid_param` by `dry_run` and by `issue`, for a named sensor and for `auto`. *(Design
   Decision 2; `BL-0217`)*
6. **No phantom booking.** After every rejection in Test 5, the sensor's bookings and the order
   system's `_order_sensor` map are exactly as before the attempt, and a following well-formed
   observe gets the same window it would have got with no prior attempts. *(Objective 2)*
7. **HTTP: 400-class outcome, not 500.** Through `TestClient` with `raise_server_exceptions=False`,
   `POST /order` with `beam_mode: ["fence"]` returns 200 with `ok: false` and reason
   `invalid_param` (the route returns the `OrderAck` as-is), and `POST /order/validate` returns the
   same reason. *(Objective 2)*
8. **`null` means default.** An observe with `look_angle_deg: None`, `duration_s: None`, `gain: None`
   and `beam_mode: None` is accepted, and its scheduled `execute_observe` payload equals that of the
   same order with those keys absent. *(Design Decision 3)*
9. **Well-formed orders unchanged.** An observe with numeric strings (`look_angle_deg: "10"`,
   `duration_s: "120"`) is still accepted, and the scheduled payload of an ordinary observe with
   numeric params is identical to the pre-package payload for the same fixture. `isr.beam_params`
   with a non-string mode returns the same result as with `None`. *(Design Decisions 2, 4)*

Existing tests must pass unmodified, in particular `test_sensor_modality_wiring.py`,
`test_validate_order.py`, `test_queue.py` (cancel releases the booking) and `test_planning.py`
(booking reconstruction on rewind). The Phase-1 determinism gate (`test_determinism.py`) and the
engine import guard (`test_import_guard.py`) must stay green: the engine changes read no wall clock,
draw no RNG, and import nothing outside `engine/`.

## Documentation Updates

- `docs/requirements/03-requirements-traceability-matrix.md` — the `FR-3210` and `FR-1610` rows: add
  `IP-1041` and the new test file.
- `CLAUDE.md` code map — the `engine/orders.py` bullet, if the implementer's change makes the
  existing text inaccurate (it lists the rejection vocabulary only by example).
- This package's Status header, the Master Build Plan row, `packages/INDEX.md`, `ROADMAP.md`'s
  implementation-package row, and the `Referenced By` metadata of `FS-104` and `FS-122` (metadata
  only).
- **Manual impact:** route to `08-training-manual-authoring` via the backlog, to ride `BL-0216`'s
  pass. `09-troubleshooting-and-glossary.md`'s rejection list should gain `sensor_contended`
  (every window booked) and `invalid_param`; the `06` "Authoring sensors" closing paragraph and
  `BLU-4`/`RED-4` can then say the preview reports `no_window` for a sensor that cannot see the
  target.

## Definition of Done

- A windowless observe (named or `auto`) is rejected `no_window`; `sensor_contended` is reported
  only when at least one window was found and all were booked; the no-candidate and `requires_cue`
  outcomes are unchanged.
- A malformed `beam_mode`, `look_angle_deg`, `duration_s` or `gain` is rejected `invalid_param` by
  `dry_run` and `issue` alike, before any booking; no HTTP 500 and no phantom booking remain for
  these params.
- An explicit `null` for those params behaves as the param absent.
- `isr.beam_params` never raises on a non-string mode.
- `REASON_TIPS` covers `invalid_param` and `requires_cue`, and the `sensor_contended` text matches
  its meaning.
- Every well-formed order, and every shipped vignette's playbook, behaves as before.
- Code changes are confined to `spacesim/engine/orders.py`, `spacesim/engine/isr.py`,
  `spacesim/ui_web/static/app.js` and `spacesim/tests/`.
- The full suite is green, and `test_determinism.py` and `test_import_guard.py` are green.
- The RTM, the ledgers and the FS cross-links are updated, and the manual-impact finding is routed.

## Verification Checklist

- [ ] `git diff` of the implementing commit touches code only in `spacesim/engine/orders.py`,
      `spacesim/engine/isr.py`, `spacesim/ui_web/static/app.js` and `spacesim/tests/`;
      `access.py` and `session/` are unchanged.
- [ ] Read `_plan_collection`: the reason is `sensor_contended` only when a window was found, and
      the `requires_cue` early return still runs first.
- [ ] Read `_validate`: the observe-param check precedes the `auto` early return.
- [ ] Independent reproduction on a fixture other than the tests': a windowless observe gives
      `no_window` through both `POST /order/validate` and `POST /order`.
- [ ] Independent reproduction of Objective 2's probe (list/dict `beam_mode`, string
      `look_angle_deg`/`gain`) over HTTP: no 500; `invalid_param` from both routes; the sensor's
      next window is unchanged afterwards.
- [ ] A console-shaped order with blank look-angle and duration (`null`s) is accepted.
- [ ] Tests 1–9 exist and pass; the Implementation Summary records which were seen failing first.
- [ ] Pre-existing tests are unmodified.
- [ ] `python3 -m pytest` passes in full, and `test_determinism.py` and `test_import_guard.py` pass.
- [ ] The RTM `FR-3210`/`FR-1610` rows cite `IP-1041`.
- [ ] The Master Build Plan row, the `packages/INDEX.md` row, `ROADMAP.md`'s row and this header
      agree on status.

## Dependencies

- **Packages:** `IP-1040` (`VERIFIED`, `VR-1040`) and `IP-1222` (`VERIFIED`, `VR-1222`). Both are
  `VERIFIED`, so this package is `READY`.
- **Spec/requirement:** FS-104 and FS-122 v1.1, `FR-3210`/`FR-1610`, all landed. No spec change is
  needed: the package makes the code report what FS-104 already requires to be visible.
- **Authorization:** granted by the project owner 2026-10-11 (MSTR-006 §3) through the standing
  pre-authorization of this iteration's packages.
- **Parallelism:** no ordering constraint with any other open package. `IP-1160` (`BLOCKED`,
  unauthorized) edits `orders.py` validation in the role-scoped command path, not the observe
  branch; whichever lands second rebases.

## Risks

- **A client that relied on `sensor_contended` for "cannot see".** No code in the tree branches on
  the reason (`grep` at `9fc25a4`: only `orders.py` sets it and `app.js` displays it), and no test
  asserts it. Red doctrine (`session/redai.py`) does not read it.
- **`invalid_param` on input that used to work.** Only inputs that raise today are refused, plus
  non-finite numbers (`"inf"`, `NaN`), which `float()` accepts today and which would propagate into
  footprint geometry. Test 9 guards numeric strings.
- **Scope left out on purpose:**
  - `BL-0220` (malformed sensor field → bare 500 on `POST /api/sessions`, silent Load). It belongs to
    `FR-5310` (load-time vignette validation with precise errors), which the Feature Catalog assigns
    to `FEAT-5300`, and `FEAT-5300` has no Feature Specification yet. `FS-115` explicitly leaves
    vignette-file validity to `FEAT-5300` (its Error Handling and the catalog's Excluded
    Requirements). Planning it here would be planning against an unspecified Feature, so it is
    routed to `06-feature-specification`.
  - The same unguarded `float()`/`int()` pattern in `jam` (`power_w`, `bandwidth_hz`,
    `victim_bandwidth_hz`) and `engage` (`salvo_n`). These are filed as a new backlog finding rather
    than widened here; the jam/engage paths have their own previews and tests.
- **Phantom bookings from other exceptions.** The booking at `:439` still precedes `_exec_payload`.
  Design Decision 2 removes the known raising inputs; reordering the commit block (payload first,
  then book) would remove the class. The implementer may make that reorder if it is a pure
  statement move with no behaviour change (the payload computation reads no bookings); if it is not,
  leave it and record it.

## Rollback Considerations

Reverting the implementing commit restores today's behaviour: windowless observes reported as
`sensor_contended`, malformed params raising a 500 and leaking a booking, `null` params crashing.
There is no persisted-format, `SavedSession`, route or API-schema change, and no content change. A
save made while the package was live replays identically after rollback for every accepted order,
because accepted orders' payloads are unchanged (Design Decision 3 only replaces values that crash
today). Rejected orders never reach the event log, so they leave nothing to replay.
