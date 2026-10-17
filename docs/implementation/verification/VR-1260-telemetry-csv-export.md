# VR-1260 — Verification Report: Per-Asset Telemetry CSV Export Over a Time Span

> **Document ID:** VR-1260
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1260](../packages/IP-1260-telemetry-csv-export.md), [FS-126](../../features/FS-126-telemetry-csv-export.md) v1.0 (`FR-2320`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of IP-1260
> **Feature Mapping:** FS-126 v1.0 (`FR-2320`)
> **Related Topics:** [`spacesim/engine/telemetry.py`](../../../spacesim/engine/telemetry.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/session/ephemeris.py`](../../../spacesim/session/ephemeris.py),
> [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1260 — Per-Asset Telemetry CSV Export Over a Time Span
- **Version verified:** 1.0
- **Tree state verified:** commit `7712c61` (branch `claude/chart-prompt-file-90hm9u`, same tip
  this report commits onto). Implementing commit: `a53f9f8` (2026-10-10); ledger-only follow-ups
  `0125086`/`24ce1dd`/`7712c61` layered on top, untouched by this verification.
- **Independence:** first verification pass, fresh session with no involvement in `a53f9f8`
  (confirmed by this session's own git history — no prior commits by this session touch
  `spacesim/`). No prior `09-package-verification` run on this package.

## Result

**VERIFIED, with 1 Low finding (`BL-0168` part 4).** `FR-2320` (per-asset telemetry CSV export,
fog-of-war filtered, reflecting an active anomaly-inject perturbation at the correct simulated
times) is fully and correctly implemented. `BL-0168`'s four scope questions are adjudicated below
— parts 1–3 **accepted, necessary/correct, no remediation**; part 4 (stale `BLOCKED` header on the
package's own file) **confirmed genuine but cosmetic**, consistent with the same "own doc left
unupdated" Low finding every other package in this batch (`IP-1220`/`IP-1240`/`IP-1250`/`IP-1270`/
`IP-1280`/`IP-1290`, and `IP-1211`'s still-`READY` header) already carries without blocking
`VERIFIED`. The replay-per-sample correctness claim was independently re-derived from scratch on a
new scenario (different vignette timing, different seed, not the implementer's fixture) and
confirmed exact; the naive non-replay approach was separately shown to actually leak the anomaly
into all 10 pre-onset samples, proving the replay mechanism is necessary, not gratuitous. The
fog-of-war claim was independently probed over the live HTTP route via `TestClient`, not merely
read from the docstring. Full suite 813 passed / 3 skipped (816 collected); both permanent gates
green (14/14).

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Export reflects an active `anomaly`-inject perturbation at the correct simulated times. | Independently constructed a fresh scenario (seed 777, `ISR-EO-1`, inject fired at `t0+5min`, span `t0..t0+30min`, 30 s sampling — none of these parameters match the implementer's own `_export_mgr()` fixture, which uses seed 1 and a `+600s`/`+1200s` shape). `telemetry_export`'s 10 pre-onset `snr_db` rows were all nominal (`>20 dB`, `green`); all 51 post-onset rows showed the safe-mode payload-off drop (`<10 dB`, `red`). Cross-checked a 50-row subset against a from-scratch `Simulation.replay(up_to_seq=...)` + `telemetry.sample()` call built independently of both `manager.py` and `session/ephemeris.py` — zero mismatches. Separately demonstrated that sampling the *current* (final) world instead of a per-instant replay would have produced a false positive on **all 10** pre-onset rows (the naive-approach sanity check), which independently confirms the replay mechanism is load-bearing, not ornamental. Also confirmed by the shipped `test_telemetry_export_reflects_anomaly_perturbation_at_correct_times` and `test_telemetry_export_matches_live_endpoint_and_engine_sample_at_each_point`, both read directly and green. | ✅ Pass |
| Export is fog-of-war-filtered per requesting cell; a different cell's export never leaks. | `manager.py:886::telemetry_export` calls `self._owns(cell, asset_id)` (the same `_owns` helper `get_telemetry` already uses) and returns `None` otherwise — read directly, not trusted from the docstring. Independently probed the live route via `fastapi.testclient.TestClient` against a session built from scratch in this verification pass (not the implementer's `_client()`/`_new_session()` fixtures): `red` → 404, `observer` → 404 (a hostile participant asserting a cell it doesn't hold gets nothing, matching every other cell-scoped route's trust model per `CLAUDE.md`'s LAN trust-model note), `blue` → 200, `white` → 200 (ground truth, by design). Also confirmed by the shipped `test_telemetry_export_is_fog_scoped_per_requesting_cell`, read directly and green. | ✅ Pass |
| A partially out-of-range span is clamped; a wholly out-of-range span is rejected. | `ephemeris._clamp_or_reject`/`_valid_range` read directly: `t2 < lo or t1 > hi` raises `ValueError`, else clamps to `[max(t1,lo), min(t2,hi)]`. Independently probed boundary cases not in the shipped test file: the exact full-range span `[t0, now]` (both ends inclusive, no raise); `t2 == lo` and `t1 == hi` (single-point span, correctly accepted, not treated as "wholly outside" since the comparison is strict `<`/`>`); one microsecond past each boundary (`t0-1`, `now+1`) correctly raises `ValueError` naming the real range. Also confirmed by the shipped `test_telemetry_export_wholly_out_of_range_rejected`/`test_telemetry_export_partially_out_of_range_clamped`/`test_telemetry_export_default_span_is_the_recorded_range`, read directly and green. | ✅ Pass |
| Full existing test suite green, zero regressions, both permanent gates green. | See Test run below: 813 passed / 3 skipped (816 collected), 0 failed/errored; both gates 14 passed. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Every new test named above exists and is green. | `test_telemetry.py`: `test_telemetry_export_reflects_anomaly_perturbation_at_correct_times`, `test_telemetry_export_matches_live_endpoint_and_engine_sample_at_each_point`, `test_telemetry_export_is_fog_scoped_per_requesting_cell`, `test_telemetry_export_is_read_only_and_deterministic`, `test_telemetry_export_wholly_out_of_range_rejected`, `test_telemetry_export_partially_out_of_range_clamped`, `test_telemetry_export_default_span_is_the_recorded_range` (7, matching the claim). `test_web.py::test_telemetry_export_csv_route_is_cell_scoped_like_telemetry` (1). All 8 confirmed present by direct read and green in the full-suite run below. | ✅ Pass |
| `python3 -m pytest spacesim/tests/test_determinism.py` remains green. | `6 passed`. | ✅ Pass |
| `python3 -m pytest spacesim/tests/test_import_guard.py` remains green. | `8 passed`. Moot risk-wise in the strongest sense: `git log --oneline --follow -- spacesim/engine/telemetry.py` shows the implementing commit `a53f9f8` is **not** among the 3 commits that have ever touched `engine/telemetry.py` — the package genuinely introduced no new `engine/` code at all, so there is no new wall-clock read or global-RNG use to guard against. | ✅ Pass |
| Independently confirm the export route calls `engine/telemetry.py`'s existing function directly (no parallel/duplicated computation). | `manager.py:903-904` read directly: the per-row value is `telemetry.sample(world, asset_id, spec.id, t, seed)["value"]` — the identical function (`engine/telemetry.py::sample`) the live `/telemetry/{cell}/{asset}` JSON endpoint (`get_telemetry`) and the `/telemetry/{cell}/{asset}/{param}` series endpoint (`get_series`) already call. `grep -n "def sample\b" spacesim/` confirms exactly one definition. No second value-computation path exists in `manager.py`, `ephemeris.py`, or `server.py`. | ✅ Pass |

## `BL-0168` adjudication (four scope notes)

**Disposition: parts 1–3 DONE, accepted, no remediation; part 4 confirmed genuine, Low, no block.**

**(1) `session/inprocess.py` pass-through, not named in the package's own `Files to Modify`.**
Confirmed necessary: `server.py`'s routes call `api.<method>(sid, ...)` where `api` is an
`InProcessSession` instance, never `SessionManager` directly (confirmed by reading `server.py`'s
`create_app(api: InProcessSession)` signature and every other route). Every sibling read method —
`get_tle`, `maneuver_ledger`, `get_series` — has the identical one-method pass-through shape in
`inprocess.py`, confirmed by direct grep. This is the established, load-bearing wiring pattern for
this layer, not an invention; the package text's omission is an authoring gap in the package
document, not a defect in the implementation. Same precedent `VR-1300`/`BL-0158` already accepted
for an analogous implied file. **Accepted.**

**(2) Replay-per-sample instead of the live/final-world sampling the sibling `/{param}` series
route uses.** Confirmed both necessary and specified. `FS-126`'s own Security Considerations
section states the export "must be identical, in principle, to what the requesting cell's own live
telemetry endpoint would show at each sampled point" and Acceptance Criterion 1 requires the
perturbation to show "at the correct simulated times" — not merely "eventually." Read
`engine/telemetry.py::_attack_term` directly: several symptom branches (`cpu_load_pct`, `snr_db`,
`attitude_error_deg`, the `fsw_error_count`/`cmd_reject_count` safe-mode fallback) gate on
`bus.mode == "safe_mode"` / `bus.safe_mode.entered_at`, i.e. the asset's **current** bus state, not
a value that is itself time-filtered by `t`. Sampling the final world for every historical `t`
would therefore show these symptoms at *every* sampled instant once the asset is ever safed,
including instants before the inject actually fired — independently reproduced in this pass (see
DoD row 1: the naive approach leaked the anomaly into all 10 pre-onset rows of a fresh scenario).
Per-sample replay is the only way to satisfy the spec's own "identical to the live value at each
sampled point" postcondition for these specific symptom types. **Not scope creep — a correct,
spec-required design choice.**

**(3) No console UI control added — export is URL-only reachable.** Confirmed by grep: no
reference to `export.csv` or `telemetry_export` exists anywhere in `ui_web/static/*.js` or
`*.html`. Checked against `FS-126`'s own text: the Subsystem Responsibilities table names only
`engine/telemetry.py`, `session/manager.py`, `ui_web/server.py`; User Workflow 1 says only "An
operator (or facilitator) requests a telemetry export," naming no UI affordance; the package's own
`Files to Modify` list names only `manager.py` and `server.py`. Neither document ever committed to
a console button. **In scope as specified — not a gap in this package.** (A UI button remains a
legitimate future-enhancement idea; not filing a new backlog item for it here since BL-0168 itself
already routes "(3) to `00-intake`/`06` only if the owner wants a UI affordance" — left to the
owner's discretion, not manufactured as a defect.)

**(4) The package's own file header still reads `🔴 BLOCKED`.** Confirmed genuinely stale: the
Master Build Plan and `packages/INDEX.md` both correctly show `COMPLETE`/`VERIFIED`-pending, but
`docs/implementation/packages/IP-1260-telemetry-csv-export.md` line 5 is untouched since authoring.
This is a real but cosmetic documentation-currency gap, not a code or contract defect — and this
project already has an established pattern of accepting it as a non-blocking Low finding rather
than having `09-package-verification` edit the package file itself (which this skill's own rules
forbid even for a one-line fix): `IP-1220`/`IP-1240`/`IP-1250`/`IP-1270`/`IP-1280`/`IP-1290` were
all `VERIFIED` with the identical "package's own document left unupdated" Low finding, and
`IP-1211`'s own header still reads `READY` despite `VR-1211` verifying it. **Confirmed genuine,
Low severity, consistent with standing project precedent — does not block `VERIFIED`.** No new
`08-code-implementation` re-run is warranted solely for this; it may be swept up the next time any
of these headers are batch-corrected (a `10-integration-review`/doc-coherence matter, same shape as
the open `BL-0169`).

## Pre-existing-quirk claim (the live `/{param}` series route)

Independently confirmed via git history, not merely trusted: `git show a53f9f8 -- spacesim/ui_web/server.py` 
shows the implementing diff is purely additive (27 lines inserted immediately before the existing
`/{param}` route; the existing route's own body is untouched in the diff). `git show a53f9f8 --
spacesim/session/manager.py` shows `get_series` (the function backing that route) is likewise
untouched — the diff only *adds* `telemetry_export` after it. `git log --oneline --follow -S"def
get_series" -- spacesim/session/manager.py` shows `get_series` was introduced at commit `2c9ed07`,
long before `a53f9f8`. The quirk (sampling the live/final world across the whole requested window,
so an anomaly can appear to pre-date its own onset) is therefore genuinely pre-existing and
unaffected by this package, as claimed.

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-2320 | `session/manager.py::telemetry_export`; `session/inprocess.py::telemetry_export` (pass-through); `ui_web/server.py` `GET /api/sessions/{sid}/telemetry/{cell}/{asset}/export.csv` | `spacesim/tests/test_telemetry.py` (7 named tests above), `spacesim/tests/test_web.py::test_telemetry_export_csv_route_is_cell_scoped_like_telemetry` | `docs/requirements/03-requirements-traceability-matrix.md`'s `FR-2320` row correctly cites `FS-126`, all 8 test names, and `IP-1260`; corrected below to drop "awaiting `09-package-verification`" now that this report closes it. | ✅ Pass |

## Test run

```
python3 -m pytest -q --junitxml=/tmp/.../junit.xml                 # full suite
  → junit testsuite attrs: tests=816, failures=0, errors=0, skipped=3
    → 813 passed, 3 skipped (this environment's pytest run again did not surface its own
      dot-stream summary line to the capture pipe, as flagged by the implementing session and
      prior VRs — counted from the JUnit XML's own testsuite attributes, not assumed)
python3 -m pytest -q spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py
  → 14 passed (6 determinism + 8 import-guard, counts confirmed via --collect-only)
```
Plus the independent hand-checks recorded above: a fresh anomaly-timing scenario (different seed,
asset timing, and span than the implementer's fixture) with a from-scratch replay cross-check and
a naive-no-replay sanity demonstration; five fresh HTTP route probes via `TestClient` (own-cell,
cross-cell, observer, white, route-precedence, 400-path) against a session built independently in
this pass; five independent time-span boundary probes (exact full range, both exact single-point
boundaries, one microsecond past each boundary).

## Scope audit

`git show --stat a53f9f8` touches exactly: `CLAUDE.md`, `ROADMAP.md`,
`docs/features/FS-126-telemetry-csv-export.md`, `docs/implementation/00-master-build-plan.md`,
`docs/implementation/packages/INDEX.md`, `docs/requirements/03-requirements-traceability-matrix.md`,
`spacesim/session/inprocess.py`, `spacesim/session/manager.py`, `spacesim/tests/test_telemetry.py`,
`spacesim/tests/test_web.py`, `spacesim/ui_web/server.py` — 11 files. `manager.py` and `server.py`
are explicitly named in the package's `Files to Modify`; the two test files are explicitly named in
`Tests to Add`; the five doc files are explicitly named in `Documentation Updates`; `inprocess.py`
is the implied-file pass-through adjudicated accepted under `BL-0168`(1) above. No file outside
this accounted-for set was touched. No excursion.

## Findings

| # | Description | Severity | Recommended owner |
|---|---|---|---|
| F1 (`BL-0168` part 4, confirmed) | `IP-1260`'s own file header (line 5) still reads `🔴 BLOCKED`, stale against the Master Build Plan's `COMPLETE`/now `VERIFIED` status. Cosmetic only — does not affect any DoD/Verification Checklist item or the shipped behavior. Consistent with the same unaddressed pattern on `IP-1211` (still `READY`) and the six `IP-122x`/`IP-124x`/`IP-125x`/`IP-127x`/`IP-128x`/`IP-129x` packages (each `VERIFIED` with an identical "own document left unupdated" Low finding). | Low | Batch-correct across all affected package headers at the next `10-integration-review` pass (doc-coherence dimension) — same shape as the already-open `BL-0169`; not worth a dedicated `08-code-implementation` re-run on its own. |

No other findings. `BL-0168` parts 1–3 adjudicated accepted above with no finding filed against
them (they are not defects).

## Related

[IP-1260](../packages/IP-1260-telemetry-csv-export.md) · [FS-126](../../features/FS-126-telemetry-csv-export.md) ·
[00-master-build-plan.md](../00-master-build-plan.md) · [packages/INDEX.md](../packages/INDEX.md) ·
[03-requirements-traceability-matrix.md](../../requirements/03-requirements-traceability-matrix.md) ·
[docs/pipeline/backlog.md](../../pipeline/backlog.md) `BL-0168` (adjudicated above, all four parts),
`BL-0167` (training-manual coverage, left `DEFERRED`, unchanged by this report), `BL-0169`
(`ROADMAP.md` drift for the unrelated run #81 tranche, left `SCHEDULED`, unchanged by this report)
