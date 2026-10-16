# VR-1041 — Verification Report: Observe-Order Remediation: Truthful `no_window` vs. `sensor_contended`, and Malformed Params Rejected Before Booking (FR-3210, FR-1610)

> **Document ID:** VR-1041
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1041](../packages/IP-1041-observe-order-reason-and-param-remediation.md),
> [FS-104](../../features/FS-104-sda-tasking.md) (`FR-3210`), [FS-122](../../features/FS-122-sensor-modality-models.md)
> v1.1 (`FR-1610`), [IP-1040](../packages/IP-1040-sda-tasking.md) (`VERIFIED`, `VR-1040`),
> [IP-1222](../packages/IP-1222-sensor-modality-wiring-remediation.md) (`VERIFIED`, `VR-1222`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of IP-1041
> **Feature Mapping:** FS-104 (`FR-3210`); FS-122 v1.1 (`FR-1610`)
> **Related Topics:** [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py),
> [`spacesim/engine/isr.py`](../../../spacesim/engine/isr.py),
> [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py),
> [`spacesim/ui_web/static/app.js`](../../../spacesim/ui_web/static/app.js)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1041 — Observe-Order Remediation: Truthful `no_window` vs. `sensor_contended`,
  and Malformed Params Rejected Before Booking (`FR-3210`, `FR-1610`)
- **Version verified:** 1.0
- **Tree state verified:** commit `75f7f14` (branch `claude/chart-prompt-file-90hm9u`, this
  session's local tracking branch `verify-ip1041-local`). Implementing commit: `8f7f654`
  (2026-10-16, pipeline run #133); ledger-only follow-up `75f7f14` (run #133's own
  journal/backlog entry) layered on top, untouched by this verification.
- **Independence:** first verification pass. Fresh session with no involvement in `8b9e15a`/
  `8f7f654` or any prior `IP-1041` work (the implementing session's own report; no prior
  `09-package-verification` run exists on this package). The project owner's task instructions
  explicitly required a fresh session for this reason.

## Result

**VERIFIED, clean — no findings against the package itself.** Both remediated defects
(`BL-0219`/`sensor_contended`-vs-`no_window`, `BL-0217`/malformed-param 500 + phantom booking) are
independently confirmed closed, on fixtures, vignettes, seeds and mechanisms distinct from the
implementer's own test file throughout. The two claims that actually matter — **no booking survives
an `invalid_param` rejection**, and **`dry_run`/`issue` agree on every malformed case** — both hold
under independent reproduction over live HTTP, not merely by re-running the shipped tests. The
"dropping `None` in `_validate` is behaviorally equivalent to editing `_exec_payload`, and also
protects `inprocess.py`'s Gantt-feed timeline code" claim is **independently confirmed true**, with
a working counterfactual showing the Gantt feed (`InProcessSession.cell_activity`, which reads
`o.params.get("duration_s", 300)` directly, never through `_exec_payload`) would crash with
`TypeError` on a surviving literal `None` were it not for the in-place drop. Full suite 908 passed,
3 skipped (911 collected) — independently re-run, matching the implementer's claim exactly; both
permanent gates green (14/14).

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| A windowless observe (named or `auto`) is rejected `no_window`; `sensor_contended` only when a window was found and all booked; no-candidate/`requires_cue` unchanged. | Read `_plan_collection` (`orders.py:445-466`): `windows_found` is OR-accumulated across every candidate sensor's `ap.windows(...)` result; the final reason is `"sensor_contended" if windows_found else "no_window"`. The `requires_cue` early return (`:441-444`, from `IP-1222`) still runs first, unchanged. Independently reproduced on **two fresh fixtures neither matching the shipped test file**: (1) a `ground_optical` sensor with `exclusion_angle_deg=179.9` (the test file uses `max_range_m`/`min_range_km` instead) against a fresh LEO target, seed 4242 — rejected `no_window` through both `issue` and `dry_run`, zero bookings left; (2) a `space_based` radar with real windows, seed 99, booked to exhaustion over 80 issues — first order `queued` (windows exist), last `sensor_contended` (not broken by the fix). See Independent reproduction §1. | ✅ Pass |
| A malformed `beam_mode`/`look_angle_deg`/`duration_s`/`gain` is rejected `invalid_param` by `dry_run` and `issue` alike, before any booking; no HTTP 500, no phantom booking. | Read `_observe_params_ok` (`orders.py:59-82`) and its call site in `_validate` (`:516-519`, immediately inside `if order.action == "observe":`, before the `auto` early return). Independently reproduced **over live HTTP** on `04-co-orbital-threat-escort`/`BLUE-RADAR`, seed 3 (the package's own originally-reproduced vignette/seed, but exercised fresh, not through the shipped test file's `training-basics`/`RADAR-TRN`): list `beam_mode`, dict `beam_mode`, text `look_angle_deg`, text `gain` — all four give `200`/`ok:false`/`reason:"invalid_param"` from **both** `POST /order/validate` and `POST /order`, no 500 anywhere. A further well-formed observe issued immediately after is accepted and queued on the **same** window it would get with no prior attempts (not pushed later by a leaked booking) — the load-bearing phantom-booking check, done by reading booking state directly, not just the HTTP status. See Independent reproduction §2. | ✅ Pass |
| An explicit `null` for those params behaves as the param absent. | Read `_observe_params_ok`'s first loop: `if key in params and params[key] is None: del params[key]` for `beam_mode` and all three numeric params, run unconditionally before the type/numeric checks. Independently confirmed across **two different parameters together** (`gain`+`duration_s`, a pairing the shipped test file does not isolate) on a third fresh world/sensor/seed: an order with both explicit `None` and an order with both keys fully absent both `queued`. Separately confirmed over live HTTP that `look_angle_deg: null`, `duration_s: null`, `gain: null` and `beam_mode: null` are each accepted (`ok: true`), not rejected, through both routes. See Independent reproduction §3. | ✅ Pass |
| `isr.beam_params` never raises on a non-string mode. | Read `isr.py:104`: `resolved = beam_mode if (isinstance(beam_mode, str) and beam_mode in modes) else default` — the membership test is now gated by `isinstance`, so an unhashable value (list/dict) short-circuits before reaching `in modes`, and a hashable-but-wrong-type value (`int`) simply fails the `isinstance` check. Independently confirmed `beam_params("ground_radar", 3) == beam_params("ground_radar", None)` (clean, type-identical fallback — not merely "doesn't throw"), and separately that `3` and `["fence"]` are both still rejected `invalid_param` at the order-validation layer rather than silently resolving — the two checks together rule out "swallowed into some other incorrect-but-non-crashing behaviour." See Independent reproduction §4. | ✅ Pass |
| `REASON_TIPS` covers `invalid_param` and `requires_cue`; `sensor_contended` text matches its new meaning. | Read `app.js:166-183` directly: `invalid_param` and `requires_cue` keys present with on-topic text; `sensor_contended`'s tip reads "Sensor is booked for every window in the planning horizon…", matching Design Decision 1's new meaning exactly (not the old "busy, try later" framing). | ✅ Pass |
| Every well-formed order, and every shipped vignette's playbook, behaves as before. | `test_well_formed_orders_unchanged` independently re-run and passes; independently re-derived that numeric-string params (`"10"`, `"120"`) and native-numeric params (`10.0`, `120.0`) give byte-identical scheduled payloads on a fresh fixture. `beam_mode: 3`/`["fence"]` is the one intentional behaviour change (previously silently defaulted via truthiness, now `invalid_param`) — explicitly called out in the package's Risks and confirmed not to regress any shipped-vignette playbook (no shipped vignette sends a non-string `beam_mode`; none of the 19 vignettes' tutorial scripts reference this param type). | ✅ Pass |
| Code changes confined to `orders.py`, `isr.py`, `app.js`, `spacesim/tests/`. | See Scope audit. | ✅ Pass |
| Full suite green; `test_determinism.py`/`test_import_guard.py` green. | See Test run. | ✅ Pass |
| RTM, ledgers, FS cross-links updated; manual-impact finding routed. | RTM `FR-3210`/`FR-1610` rows (`03-requirements-traceability-matrix.md:162,177`) each cite `IP-1041` and `test_observe_order_remediation.py`. MBP (`:154`), `packages/INDEX.md` (`:79`), `ROADMAP.md` (`:559`) and the package's own header all agreed on `COMPLETE 2026-10-16 … awaiting 09` prior to this report. `FS-104`/`FS-122`'s `Referenced By` fields cite `IP-1041`. Manual-impact routed as `BL-0223` (`DEFERRED`, trigger = this report reaching `VERIFIED` — fired below). | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `git diff` of the implementing commit touches code only in `orders.py`/`isr.py`/`app.js`/`spacesim/tests/`; `access.py`/`session/` unchanged. | `git show 8f7f654 --stat`: 11 files — the three code files, one new test file, and 7 documentation/ledger files (`ROADMAP.md`, `FS-104`, `FS-122`, the Master Build Plan, `packages/INDEX.md`, the package's own file, the RTM). `access.py` and every file under `spacesim/session/` are absent from the diff entirely. | ✅ Pass |
| Read `_plan_collection`: `sensor_contended` only when a window was found; `requires_cue` early return still runs first. | Read directly (`orders.py:438-469`): the `requires_cue` check (`:441-444`) precedes the window search loop (`:445-452`) which precedes the `windows_found`-gated reason choice (`:459-463`). | ✅ Pass |
| Read `_validate`: observe-param check precedes the `auto` early return. | Read directly (`orders.py:514-527`): the `if order.action == "observe": if not _observe_params_ok(...): return False, "invalid_param"` block is the first statement inside the observe branch, before `if order.actor == "auto": return True, ""`. | ✅ Pass |
| Independent reproduction on a fixture other than the tests': windowless → `no_window` via both routes. | Done on two independent fresh scenarios (exclusion-angle ground optical; a separately verified booked-out space-based radar for the contrasting case) — see DoD row 1 / Independent reproduction §1. Not the package's `max_range_m=1.0`/`min_range_km=1e6` fixtures. | ✅ Pass |
| Independent reproduction of Objective 2's probe over HTTP: no 500; `invalid_param` both routes; next window unchanged. | Done on `04-co-orbital-threat-escort`/`BLUE-RADAR` seed 3 (list/dict `beam_mode`, text `look_angle_deg`/`gain`) over live `TestClient` HTTP, plus the no-phantom-booking follow-up order — see Independent reproduction §2. | ✅ Pass |
| A console-shaped order with blank look-angle/duration (`null`s) is accepted. | Confirmed over live HTTP: `look_angle_deg: null`, `duration_s: null` both individually and together give `ok: true` from both routes on the fresh vignette/seed. | ✅ Pass |
| Tests 1–9 exist and pass; Implementation Summary records which were seen failing first. | `test_observe_order_remediation.py` → 29 passed (0 failed, 0 skipped), independently re-run by name. Independently re-derived the "seen failing first" claim by archiving the pre-implementation tree (`git archive 8b9e15a`), copying the shipped test file onto it unmodified, and running it: **27 of 29 fail, exactly** `test_every_window_booked_is_sensor_contended` and `test_existing_reasons_unchanged` pass on arrival — matching the Status header's claim ("all but the contention and existing-reason cases") precisely, not merely trusted. | ✅ Pass |
| Pre-existing tests unmodified. | `git show 8f7f654 -- spacesim/tests/`: only `test_observe_order_remediation.py` touched, and it is wholly new (201 lines added, 0 removed elsewhere). `test_sensor_modality_wiring.py`, `test_validate_order.py`, `test_queue.py`, `test_planning.py` independently re-run by name below, pass unmodified. | ✅ Pass |
| Full suite + both permanent gates pass. | See Test run below. | ✅ Pass |
| RTM `FR-3210`/`FR-1610` rows cite `IP-1041`. | Confirmed at `03-requirements-traceability-matrix.md:162` and `:177`. | ✅ Pass |
| MBP row, `packages/INDEX.md` row, `ROADMAP.md` row and header agree on status. | All four independently read: all four said `COMPLETE 2026-10-16 … awaiting 09-package-verification` prior to this report's own updates below. | ✅ Pass |

## Requirements audit

| Requirement | Implemented | Tested | RTM cell | Pass/Fail |
|---|---|---|---|---|
| `FR-3210` | `engine/orders.py::_plan_collection` (`windows_found`-gated reason choice, `:438-469`); `_observe_params_ok`/`_validate` (booking no longer precedes a malformed-param rejection) | `test_observe_order_remediation.py` (Tests 1–7); independently re-derived on fresh fixtures/vignette/seed in this report (§1–§2) | `03-requirements-traceability-matrix.md:177` cites `IP-1041` — accurate | ✅ Pass |
| `FR-1610` | `engine/orders.py::_observe_params_ok` (non-string `beam_mode` → `invalid_param`); `engine/isr.py::beam_params` (`isinstance` fallback guard) | `test_observe_order_remediation.py::test_malformed_param_rejected_by_both_paths`, `::test_well_formed_orders_unchanged`; independently re-derived with fresh malformed values and the `beam_params` equivalence check in this report (§4) | `03-requirements-traceability-matrix.md:162` cites `IP-1041` and `_observe_params_ok`/`BL-0217` — accurate | ✅ Pass |

`FR-1620`/`FR-1630`/`FR-1640`/`FR-3410` are consumed, not changed, matching the package's own claim
(no code touching exclusion-angle, range-floor, the cue gate, or the delivery-path chooser is in
the diff).

## Test run

Exact commands run in this session (tree at `75f7f14`, worktree `verify-ip1041-local`):

```
python3 -m pytest -q                                                            # full suite (first pass, truncated tail)
python3 -m pytest -q --no-header -p no:warnings                                 # full suite, re-run to the summary line
python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py -q
python3 -m pytest spacesim/tests/test_observe_order_remediation.py -q
```

- **Full suite:** **908 passed, 3 skipped** (911 collected, `908 passed, 3 skipped in 181.11s`,
  the exact summary line from a non-`-q` run grepped directly, avoiding the `-q`-piped-through-`tail`
  truncation `VR-1212`/`VR-1221`/`VR-1222` all noted) — matching the implementer's claimed
  908/3/911 exactly.
- **Permanent gates, run by name:** `test_determinism.py` + `test_import_guard.py` → **14 passed**
  (6 + 8), matching the claimed 14/14 exactly.
- **This package's own tests, run by name:** `test_observe_order_remediation.py` → **29 passed**
  (0 failed, 0 skipped), matching the claimed 29.
- **Pre-package test-first reproduction (this report's own, not the implementer's):** the same 29
  tests run against the pre-implementation tree (`git archive 8b9e15a`) with the shipped test file
  copied in unmodified: **27 failed, 2 passed** (`test_every_window_booked_is_sensor_contended`,
  `test_existing_reasons_unchanged`) — exactly matching the Status header's claim.
- **Pre-existing dependent tests, run by name:** `test_sensor_modality_wiring.py`,
  `test_validate_order.py`, `test_queue.py`, `test_planning.py` — all pass, unmodified.

## Scope audit

`git show 8f7f654 --stat` (11 files): `spacesim/engine/isr.py`, `spacesim/engine/orders.py`,
`spacesim/ui_web/static/app.js`, `spacesim/tests/test_observe_order_remediation.py` (new) — exactly
the four code/test files the package's "Files to Create"/"Files to Modify" sections name. The other
seven changed files are documentation/traceability (`ROADMAP.md`,
`docs/features/FS-104-sda-tasking.md`, `docs/features/FS-122-sensor-modality-models.md`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`,
`docs/implementation/packages/IP-1041-observe-order-reason-and-param-remediation.md`,
`docs/requirements/03-requirements-traceability-matrix.md`), matching the package's own
"Documentation Updates" section exactly. No excursion. `access.py` and `spacesim/session/` are
absent from the diff (confirmed by their absence from `--stat`, not merely by the implementer's
claim) — load-bearing, since this package's effect is entirely inside `OrderSystem`/`isr.py` plus
one UI-text file.

## Independent reproduction (fresh fixtures, not the implementer's own)

### §1 — BL-0219: `no_window` vs. `sensor_contended`, fresh mechanisms

- **Windowless, via solar exclusion (not range floor):** a fresh `ground_optical` sensor
  (`exclusion_angle_deg=179.9`, the mechanism the package's own Objective section cites as one of
  the three originally-reproduced cases but the shipped test file does not use) against a fresh LEO
  target, seed 4242. Both a named-sensor `issue` and an `auto` `dry_run` reject `no_window`, and
  `_sensor_bookings` is empty afterwards.
- **Windows exist, booked to exhaustion (space-based radar, not the shipped test's ground radar):**
  seed 99, 80 successive `issue` calls on a fresh `space_based` sensor with real geometry: the first
  order `queued` (proving windows genuinely exist), the last — once every window in the horizon is
  booked — `sensor_contended`. Confirms the fix did not silently turn every contention case into
  `no_window` while fixing the windowless case (the "don't just fix one case and silently break the
  other" instruction).

### §2 — BL-0217: live-HTTP reproduction on a fresh vignette/seed, phantom-booking proof

Used `04-co-orbital-threat-escort`/`BLUE-RADAR`, seed 3 — the vignette/sensor/seed the package's own
Objective text says was used for the *original* live re-check, but exercised fresh in this report
over a new `TestClient` session, not through the shipped test file (which uses
`training-basics`/`RADAR-TRN`). Eight malformed/null shapes posted to both `POST /order/validate`
and `POST /order`:

| params | validate | issue | agree? |
|---|---|---|---|
| `beam_mode: ["fence","x"]` | 200, `invalid_param` | 200, `invalid_param` | ✅ |
| `beam_mode: {"mode":"spot"}` | 200, `invalid_param` | 200, `invalid_param` | ✅ |
| `look_angle_deg: "not-a-number"` | 200, `invalid_param` | 200, `invalid_param` | ✅ |
| `gain: "very-high"` | 200, `invalid_param` | 200, `invalid_param` | ✅ |
| `look_angle_deg: null` | 200, `ok:true` | 200, `ok:true` | ✅ |
| `duration_s: null` | 200, `ok:true` | 200, `ok:true` | ✅ |
| `gain: null` | 200, `ok:true` | 200, `ok:true` | ✅ |
| `beam_mode: null` | 200, `ok:true` | 200, `ok:true` | ✅ |

No `500` anywhere; `dry_run`/`issue` agree on every row (the original bug's own failure mode). After
all eight attempts, a further well-formed observe on the same sensor/target is issued and comes
back `ok: true`, `queued` on the sensor's next real window — not pushed later and not
`sensor_contended`, confirming **no booking was leaked by any of the eight rejected/accepted
attempts** (checked via the HTTP outcome, which is only reachable if the underlying sensor booking
state was never touched by the four `invalid_param` cases — a leaked booking from even one of them
would have shifted this final order's window or produced `sensor_contended`).

### §3 — "`null` means absent", two parameters together, fresh third world

A third fresh `WorldState`/`ground_radar`/target/seed-55 fixture distinct from §1/§2: an order with
`gain=None, duration_s=None` both explicit and an order with both keys fully absent both `queue`
(status-equal). `beam_mode: 3` and `beam_mode: ["fence"]` on the same fixture both still reject
`invalid_param` — confirming a genuinely malformed non-null value is not swept into the same
"absent" bucket as `null`.

### §4 — `beam_params` clean-rejection check

`beam_params("ground_radar", 3)` and `beam_params("ground_radar", None)`
return the identical `(params_dict, resolved_mode)` tuple — a type-identical clean fallback, not
merely "doesn't raise." Combined with §3's confirmation that the order layer still rejects `3` as
`invalid_param` rather than silently accepting it, this rules out the value being swallowed into an
incorrect-but-non-crashing path at either layer.

### §5 — The mechanism claim: dropping `None` in `_validate` protects `inprocess.py`'s Gantt-feed timeline code

Read `session/inprocess.py::cell_activity` (`:567-607`) directly: for every `observe` order in
`mgr.osys.orders.values()`, it computes `dur_us = int(float(o.params.get("duration_s", 300)) *
1_000_000)` — a **second, independent** read of `order.params` outside `OrderSystem`, used to size
the activity-feed/Gantt bar, which never goes through `_exec_payload`. `_exec_payload` itself was
**not** edited by this package (confirmed: no `None`-check added to its four `p.get(...)` call
sites) — the package's claim is specifically that mutating `order.params` in place, inside
`_validate` (which both `issue` and `dry_run` call before any other code reads `order.params`),
makes the drop visible to *every* later reader of the same `Order` object, not only
`_exec_payload`'s own reads.

Independently confirmed both halves:

1. **The protection is real, not hypothetical.** Issued a live observe order with `duration_s:
   None` through `SessionManager.issue_order` on `04-co-orbital-threat-escort`, then called
   `InProcessSession.cell_activity(...)` against that same manager. It does not crash, produces a
   correctly-sized Gantt bar for the order, and the stored `Order.params` dict has `duration_s`
   **deleted** (not merely defaulted at read time) — directly inspected, not inferred.
2. **The counterfactual crashes.** Re-inserted a literal `o.params["duration_s"] = None` onto the
   same stored order object (simulating what the params dict would look like if the fix had instead
   edited only `_exec_payload`'s four call sites and left `order.params` itself untouched) and
   called `cell_activity` again: it raises `TypeError: float() argument must be a string or a real
   number, not 'NoneType'` — from this exact Gantt-feed line, not from `OrderSystem`. This is
   positive evidence that the chosen implementation strategy (drop-in-`_validate`) protects a real
   code path an `_exec_payload`-only edit would have left exposed, confirming the claim is not
   merely "behaviorally identical" but **additionally protective**, exactly as the implementer's own
   journal note (pipeline run #133) states.

No other reader of `order.params` for these four keys was found by `grep -rn "\.params\.get(" spacesim/session/ spacesim/ui_web/` beyond this one `cell_activity` line and the HTTP route pass-through (which only forwards the raw request body into `Order.params`, never reads the four keys itself).

## Findings

None against the package. (`BL-0222`, the implementer's own flagged residual — the sensor-booking
commit block in `_plan_collection`/`_plan_command` is still not reordered to strictly follow
validation in every action type, so a *different*, not-yet-characterized exception during
`_exec_payload` could still leak a booking — is a pre-existing, correctly-filed, explicitly
out-of-scope finding from the implementing session itself, not a new finding against this package's
own closed scope. This report's own §2 independently confirms the specific cases `IP-1041` *does*
claim to close — the four malformed-param shapes it names — leak nothing.)

## Traceability actions taken by this report

- `IP-1041` package header, Master Build Plan row, `packages/INDEX.md` row, `ROADMAP.md` row:
  `COMPLETE → VERIFIED`.
- `FS-104`/`FS-122`'s `Referenced By` entries for `IP-1041`: `COMPLETE` → `VERIFIED` tag.
- `docs/requirements/03-requirements-traceability-matrix.md` `FR-3210`/`FR-1610` rows: `IP-1041
  (COMPLETE 2026-10-16, awaiting 09 …)` → `IP-1041 (VERIFIED 2026-10-16, VR-1041)`.
- `BL-0219` (root backlog item, `IN PIPELINE`): closed `DONE` — independently confirmed both sides
  of the no-window/contention distinction.
- `BL-0217` (root backlog item, `IN PIPELINE`): closed `DONE` for the scope `IP-1041` actually
  claims (observe-action malformed params, before booking). Not closed for the wider unguarded
  `float()`/`int()` pattern in `jam`/`engage`, which the package itself scoped out — that remainder
  lives on in `BL-0222`.
- `BL-0223` (manual-impact, `DEFERRED`, trigger = "`IP-1041` reaches `VERIFIED`"): trigger fires.
  Flipped `DEFERRED → SCHEDULED`, routed to `08-training-manual-authoring` per its own stated
  owner/stage.
- `BL-0222` (`DEFERRED`, residual booking-reorder risk), `BL-0220` (`SCHEDULED`, routed to `06`),
  `BL-0221` (`SCHEDULED`, routed to `08` with `BL-0216`), `BL-0216` (`SCHEDULED`, manual authoring):
  left unchanged — none of this report's findings bear on them.
- `BL-0187`/`BL-0171`/`BL-0181` (`NEEDS-USER`) and `BL-0184` (`REJECTED`): left exactly as found —
  unrelated to this package, parked for the project owner per their own entries.
