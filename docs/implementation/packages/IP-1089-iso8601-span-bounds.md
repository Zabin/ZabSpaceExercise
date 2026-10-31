# IP-1089 — ISO-8601 UTC Span Bounds on the Time-Span Exports (`FR-7450`)

> **Package ID:** IP-1089
> **Version:** 1.0
> **Status:** READY (authored 2026-10-31 by `07-implementation-planning`; every dependency `VERIFIED`)
> **Authorization (MSTR-006 §3):** **given.** The project owner's go-ahead of 2026-10-31, in the planning session that commissioned this package ("build before release `FR-7450`", `BL-0181`, owner decision of 2026-10-18 promoted in `CHG-046`…`CHG-050`), covers this package and no other.
> **Dependencies:** [FS-121](../../features/FS-121-ephemeris-export.md) v2.3 (`FR-7450`, owns the parser), [FS-126](../../features/FS-126-telemetry-csv-export.md) (`FR-2320`), [IP-1210](IP-1210-ephemeris-export.md), [IP-1260](IP-1260-telemetry-csv-export.md), [IP-1261](IP-1261-telemetry-series-history-remediation.md), [IP-1262](IP-1262-export-sampling-bounds.md), [IP-1082](IP-1082-white-control-nonfinite-input-and-toolbar-refusal.md) (all `VERIFIED`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md), [01-technical-work-breakdown.md](../01-technical-work-breakdown.md)
> **Produces:** `spacesim/session/span_bounds.py` and the three exports' routes accepting an ISO-8601 UTC timestamp or integer microseconds for `t1`/`t2`.
> **Feature Reference:** [FS-121](../../features/FS-121-ephemeris-export.md) v2.3 "Span-bound parsing"; [FS-126](../../features/FS-126-telemetry-csv-export.md)
> **Supersedes:** none
> **Related Topics:** [`spacesim/session/ephemeris.py`](../../../spacesim/session/ephemeris.py), [`spacesim/session/manager.py`](../../../spacesim/session/manager.py), [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py)

[Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

## Package ID
IP-1089

## Title
One shared span-bound parser for the telemetry CSV, truth-ephemeris and cell-observed-ephemeris exports.

## Objective
Today `t1`/`t2` are integer microseconds on exactly three routes (`GET /telemetry/{cell}/{asset}/export.csv`, `GET /ephemeris/truth`, `GET /ephemeris/{cell}`; the `format=ric|oem|csv` companions share those routes). Make each accept an ISO-8601 UTC timestamp or integer microseconds, mixed pairs allowed, via one parser, refusing everything else with a 400 naming the bound and the reason. Exported values, `interval_s`, `MAX_EXPORT_SAMPLES` (IP-1262), clamping of a partly out-of-range span and rejection of a wholly out-of-range span stay byte-identical.

## Requirements Covered
`FR-7450` (primary); regression-protected, unchanged: `FR-2320`, `FR-7410`, `FR-7420`, `FR-7430`, `NFR-3710`.

## Architecture Components
Session layer helper (`session/`); route layer type change in `ui_web/server.py`. **Decision (FS-121 OQ10):** the parser is a new pure module `spacesim/session/span_bounds.py`, called from the single existing choke point `ephemeris._clamp_or_reject` (already shared by all three exports and run before any replay and before `sample_times`). Not in `SessionAPI`/`inprocess.py` (the protocol would have to carry strings through anyway), not in `engine/` (invariant 1/2 untouched; no engine file changes; the parser does its own calendar arithmetic from the matched fields and reads no clock). Error code: reuse the existing `ValueError` -> 400 `detail` path; wording `"t1: <reason>"` / `"t2: <reason>"`.

## Interfaces
- `parse_span_bound(value, name) -> int` (pure): accepts `int` (not `bool`, finite), a digits-only string (optional leading `-`) as integer microseconds, or an ISO string per `FR-7450`; raises `ValueError` naming `name` and reason (no zone designator, non-zero UTC offset, more than six fractional digits, date without time, leap second, out-of-range field, not a timestamp or integer, boolean/non-finite).
- Routes: `t1`/`t2` become `str` (telemetry: `Optional[str]`, omitted-bound defaults unchanged) so FastAPI no longer returns 422 for a timestamp; parsing happens inside the existing try/except that maps `ValueError` to 400. `SessionAPI`/`InProcessSession` signatures widen `t1`/`t2` to `int | str` (annotation only).
- `ephemeris._clamp_or_reject(mgr, t1, t2)` parses both bounds first, then runs its existing logic. `SessionManager.telemetry_export` stops pre-casting with `int(t1)` (the cast would raise a bare `ValueError` on a timestamp) and hands the raw value on.

## Files to Create/Modify
Create: `spacesim/session/span_bounds.py`; `spacesim/tests/test_span_bounds.py`. Modify (verified present): `spacesim/session/ephemeris.py` (`_clamp_or_reject`, lines ~41-52; `truth_ephemeris`/`cell_observed_ephemeris` annotations), `spacesim/session/manager.py` (`telemetry_export`, ~1574-1597), `spacesim/session/inprocess.py` (~494, ~1106-1117), `spacesim/session/api.py` (annotations if declared there), `spacesim/ui_web/server.py` (~1024, ~1207, ~1228; docstrings). No `engine/` file.

## Implementation Tasks
1. Tests first (below), observe failing. 2. Write `span_bounds.py`: strict anchored regex for the extended form with `Z`|`+00:00` only; digits-only branch first (never a date); field range checks incl. real month lengths and `:60` refusal; microseconds = days-from-civil arithmetic x 86_400_000_000 + time-of-day + fraction right-padded to six digits. 3. Wire into `_clamp_or_reject`; drop `int()` pre-cast in `telemetry_export`. 4. Change the three routes' parameter types; keep `ValueError` -> 400. 5. Update the three route docstrings.

## Tests to Add
All in `spacesim/tests/test_span_bounds.py`, each marked `@pytest.mark.verifies("FR-7450")` (plus `NFR-3710`/`FR-2320`/`FR-7410`/`FR-7420`/`FR-7430` where the case guards that leaf):
1. Unit: ISO with `Z`, `+00:00`, fractions of 1 and 6 digits equal `simtime.to_iso` round trip over a table incl. epoch, leap-day, year boundaries. 2. Unit refusals each naming bound + reason: naive, `+05:00`, seven fractional digits, date alone, basic format, week/ordinal date, `:60`, month 13, lower-case `z`/`t`, empty, garbage. 3. Digits-only and `-123` are microseconds, never dates (`20261031` is an integer). 4. Guards (IP-1082 pattern): `True`/`False`, `nan`, `inf`, float, `None` for a required bound refused. 5. HTTP parity: for truth ephemeris, cell-observed ephemeris and telemetry CSV, ISO bounds give the byte-identical body to the microsecond bounds, for `csv`, `oem`, `ric` formats; `+00:00` and a fractional second included. 6. Mixed pair accepted on all three. 7. Boundary/clamp unchanged: partly out-of-range ISO span clamped identically to the integer span; wholly out-of-range rejected; `MAX_EXPORT_SAMPLES` still 400 via ISO; refused bound causes no replay (monkeypatch replay to fail). 8. Telemetry omitted `t1`/`t2` defaults unchanged. 9. Out-of-scope routes unchanged: series `t0`/`t1`, `/ric_view`, `/maneuver_ledger` ignore this parser. 10. Fail-first note: cases 1, 2, 5, 6 must be observed failing before the parser exists. Existing `test_ephemeris.py` integer-microsecond cases stay green unmodified. Permanent gates `test_determinism.py`, `test_import_guard.py` re-run.

## Documentation Updates
**Manual impact:** *update*, assigned to `08-training-manual-authoring` after build (documents as-built only): `docs/training/08-http-api-reference.md` (the "integer microseconds of sim UTC" sentence ~line 108 -> ISO-8601 UTC or integer, accepted/refused forms, one worked example, the new refusal text); §15.1 rows "Ephemeris export, time-span" and "Per-asset telemetry CSV export, time-span" (add `session/span_bounds.py` to Sources); sections `WCM-15`, `WCM-16`, `BLU-13`, `BLU-14`, `RED-12`, `RED-13` and the 12a analysis/exports text show a timestamp instead of microseconds. No vignette change. `08-code-implementation` writes only the route docstrings and, if present, the single §15.1 Sources cell; hand-off recorded as a Manual-impact item for the rest. Also: package ledger rows (Master Build Plan, INDEX, ROADMAP); `FS-121`/`FS-126` `Referenced By` cross-links are `07`'s metadata-only edit at authoring (not made by this pass: read-only specs; owner to confirm).

## Definition of Done
All new tests green and observed failing first; full suite `-m "not browser"` green; both permanent gates green; `test_doc_integrity.py` and `test_test_origins.py` green; RTM Test column regenerated (`--origin-report=rtm`) in the same commit; documentation created/updated per Manual impact, and §15.1/§15.2 rows in sync with the shipped change (or each hand-off recorded as a Manual-impact item).

## Verification Checklist
- [ ] `span_bounds.py` exists, pure, no `datetime.now`/time/random, imports no `engine` module beyond `simtime` (if used) and nothing from `ui_web`.
- [ ] `grep` shows no other `t1`/`t2` parsing on the three exports and `_clamp_or_reject` is the only caller of the parser.
- [ ] ISO/integer parity test covers all three exports and three formats.
- [ ] Series window, RIC view, ledger and AAR routes untouched (diff).
- [ ] 400 detail names `t1`/`t2` and a reason for each refused form.
- [ ] Determinism and import-guard gates pass; full suite green.
- [ ] Documentation in sync: Manual-impact hand-offs recorded; §15.1 rows reference the parser.

## Risks
Calendar arithmetic off-by-one (mitigated by the round-trip table against `simtime.to_iso`); a hidden second caller still pre-casting with `int()` (mitigated by the grep checklist item); the FastAPI 422-to-400 change for a non-numeric string is a behavior change by design. Console friction: n/a (console shows no span inputs).

## Rollback Considerations
Revert the commit; routes return to `int` types, `span_bounds.py` and its test are deleted, no data/format migration. The exported bytes never change, so no save/format impact.
