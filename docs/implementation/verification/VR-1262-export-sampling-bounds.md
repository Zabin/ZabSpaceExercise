# VR-1262 — Verification Report: Time-Span Export Sampling Bounds (`interval_s` floor + sample-count cap)

> **Document ID:** VR-1262
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1262](../packages/IP-1262-export-sampling-bounds.md),
> [FS-121](../../features/FS-121-ephemeris-export.md) v2.0 (`FR-7410`/`FR-7420`),
> [FS-126](../../features/FS-126-telemetry-csv-export.md) v1.0 (`FR-2320`)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of IP-1262; closes `BL-0176`; closes `BL-0174`
> (adjudicates it a real, correctly implemented rider — adopted and tested in full, not merely
> accepted as pre-existing-correct-and-untested, as `BL-0173`'s original finding described it)
> **Feature Mapping:** FS-121 v2.0 (`FR-7410`/`FR-7420`); FS-126 v1.0 (`FR-2320`)
> **Related Topics:** [`spacesim/session/ephemeris.py`](../../../spacesim/session/ephemeris.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1262 — Time-Span Export Sampling Bounds (`interval_s` floor + sample-count cap)
- **Version verified:** 1.0
- **Tree state verified:** commit `e700123` (branch `claude/chart-prompt-file-90hm9u`, the tip this
  report commits onto). Implementing commit: `4fd4591` (2026-10-11); ledger-only follow-up
  `e700123` (pipeline journal/backlog, run #105) layered on top, untouched by this verification.
- **Independence:** fresh session with no involvement in `4fd4591`, `c7d70dc`, `4578850` or any
  prior commit on this branch — this worktree was checked out directly from
  `origin/claude/chart-prompt-file-90hm9u` at `e700123` onto a local tracking branch
  (`local-verify-1262`), and no commit by this session predates this report. No prior
  `09-package-verification` run on this package.

## Result

**VERIFIED, clean — no findings against IP-1262 itself.** Every claim in the package's Definition
of Done and Verification Checklist was independently re-derived, not re-read: the arithmetic,
up-front sample-count ceiling is real (confirmed by reading `sample_times`' code and by timing a
request that would naively require ~10¹⁵ instants — it rejected in ~0.003–0.005 ms, not seconds);
`interval_s` validation rejects `0`, negative, `nan`, `+inf` and `-inf`, confirmed with fresh values
distinct from the package's own fixtures; the ceiling is exact (10,000 instants succeeds, 10,001
raises) on a scenario and span this session built from scratch; `sample_times` is confirmed by
direct call-site reading to be the single choke point for all three time-span exports
(`truth_ephemeris`, `cell_observed_ephemeris`, `SessionManager.telemetry_export`); the `BL-0174`
reversed-window rider was independently re-built on a fresh scenario and confirmed correct; the
full suite and both permanent gates were independently re-run and match the implementer's counts
exactly; the implementing diff stays entirely inside the package's declared file set, with
additions-only to the three test files. One pre-existing, cross-cutting documentation-hygiene
observation (not a defect introduced by this package, and not claimed by its own Documentation
Updates section) is recorded as a Low finding below, filed as a new backlog item rather than
blocking this transition.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| An explicit non-finite/non-positive `interval_s` is rejected by all three time-span exports (400 at the route; `ValueError` at the session layer) | Read `ephemeris.py::sample_times` directly (`:62-63`): `if interval_s is not None and not (math.isfinite(interval_s) and interval_s > 0): raise ValueError(...)`. Independently called it with fresh values `0`, `0.0`, `-1`, `-3.5`, `nan`, `inf`, `-inf` on a scenario this session built — every one raised. Independently drove all three HTTP routes (`/ephemeris/truth`, `/ephemeris/{cell}`, `/telemetry/{cell}/{asset}/export.csv`) with `interval_s=0`/`-1` on a fresh session of a different vignette (`leo-isr-denial`, not the implementer's `multi-domain-taiwan`) — every one returned 400. | ✅ Pass |
| A request whose clamped span and interval would exceed `MAX_EXPORT_SAMPLES` is rejected before any replay is run | Read the function body: the count (`(t2-t1)//step + 1`) is computed and compared to `MAX_EXPORT_SAMPLES` *before* the `while` loop that builds `times`, and `sample_times(...)` is called as a plain (non-generator) argument expression to `aar.worlds_at_times(...)` at every call site, so the `ValueError` fires before that generator is ever iterated. Independently timed a request that would naively build ~10¹⁵ and ~10¹³ instants: rejected in 0.003–0.005 ms (module level) and a wholly-different, HTTP-route-level request implying 1.44×10¹⁰ instants: rejected in 3.49 ms (includes FastAPI/TestClient overhead) — both are consistent with O(1) arithmetic, not with any replay or list-building step (which this project's own measurements, and this session's own valid-request timings below, put at seconds for mere thousands of instants). | ✅ Pass |
| Valid requests produce output identical to before: every pre-existing export test passes unchanged | `git show 4fd4591 -- spacesim/tests/test_ephemeris.py spacesim/tests/test_telemetry.py spacesim/tests/test_web.py \| grep '^-' \| grep -v '^---'` returns nothing — the diff is additions-only in all three files. Full suite independently re-run (833 passed/3 skipped) includes every pre-existing export test, all green. | ✅ Pass |
| The `BL-0174` reversed-window test exists and passes | `test_series_reversed_window_matches_forward_reversed` confirmed present in `test_telemetry.py` and passing in the independent full-suite run. Independently re-derived the same property from scratch on a fresh scenario/vignette (seed 7, own `verify-ip1262` fixture, param `battery_soc`, 15-point window) distinct from the implementer's fixture — see BL-0174 audit below. | ✅ Pass |
| RTM, `CLAUDE.md` and the ledgers are updated, and the manual-impact finding is routed | Read all diffs directly — see Traceability audit below. Manual-impact finding confirmed filed as `BL-0176`'s... correction, as `BL-0182`, `DEFERRED` with a revisit trigger on this very verification. | ✅ Pass |
| The full suite is green, and both permanent gates are green | Independently re-run: `833 passed, 3 skipped, 1 warning in 128.54s`; `test_determinism.py` + `test_import_guard.py`: `14 passed in 1.19s`. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| `git diff` of the implementing commit touches no file under `spacesim/engine/` | `git show 4fd4591 --stat` lists exactly: `CLAUDE.md`, `ROADMAP.md`, `docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`, the package's own file, `docs/requirements/03-requirements-traceability-matrix.md`, `spacesim/session/ephemeris.py`, `spacesim/tests/test_ephemeris.py`, `spacesim/tests/test_telemetry.py`, `spacesim/tests/test_web.py`, `spacesim/ui_web/server.py`. No path begins `spacesim/engine/`. | ✅ Pass |
| `grep -n "MAX_EXPORT_SAMPLES" spacesim/session/ephemeris.py` shows the constant and its use inside `sample_times`; the count check precedes list construction | Ran the grep: the constant is defined at module scope (`:31`) and referenced inside `sample_times` at the `count > MAX_EXPORT_SAMPLES` check. Read the function body directly: the check sits between step computation and the `times = []` / `while t <= t2` loop — textually and causally before any list element is appended. | ✅ Pass |
| Tests 1–7 exist and pass. Tests 1–6 were observed failing first | All 7 functions (Test 1 parametrized ×4 = 10 total) confirmed present by name (`test_sample_times_rejects_non_positive_or_non_finite_interval`, `test_sample_times_enforces_sample_count_ceiling_arithmetically`, `test_ephemeris_exports_propagate_over_ceiling_rejection`, `test_telemetry_export_over_ceiling_rejected_without_replay`, `test_series_reversed_window_matches_forward_reversed`, `test_ephemeris_routes_reject_non_positive_interval_400`, `test_telemetry_export_route_rejects_over_ceiling_interval_400`) and passing in the full-suite run. **Independently reproduced the fail-first claim** (not merely trusting the Implementation Summary): checked out a detached worktree at the pre-fix commit `daa1915`, copied *only* the three new/modified test files from `4fd4591` onto it (production code left at pre-fix state), and ran the new tests — result: **8 failed, 2 passed** out of the 10 parametrized cases, exactly matching "Tests 1–6 fail except the `nan` case (accident) and Test 7 (rider, pre-existing-correct)." Failures were genuine `AssertionError`s (`200 == 400`) and the pre-existing `OverflowError`/no-raise behavior the package describes, not test-harness artifacts. Worktree removed after the check; no commit made there. | ✅ Pass |
| Independent reproduction: `sample_times(0, 10_000_000, 0.0)` raises, and `GET /ephemeris/truth?...&interval_s=0` returns 400 on a fresh session | Ran `sample_times(0, 10_000_000, 0.0)` directly: raised `ValueError("interval_s must be a finite number > 0, got 0.0")`. Ran `GET /ephemeris/truth?...&interval_s=0` on a fresh session of `multi-domain-taiwan` (own session, own asset ids): `400`. Also ran the same shape of request on a second, independently-built fresh session of a *different* vignette (`leo-isr-denial`): `400`. | ✅ Pass |
| No pre-existing test in `test_ephemeris.py`, `test_telemetry.py` or `test_web.py` was modified | `git show 4fd4591 -- <the three files> \| grep '^-' \| grep -v '^---'` returns no output — confirmed additions-only. | ✅ Pass |
| `python3 -m pytest` passes in full, and `test_determinism.py`/`test_import_guard.py` pass | Independently re-run — see Test run below. | ✅ Pass |
| The RTM `FR-7410`/`FR-7420`/`FR-2320` rows cite `IP-1262` | Read `03-requirements-traceability-matrix.md` directly: all three rows' `Impl. Package` cells contain an `IP-1262 (...)` clause naming real test functions — every named test cross-checked to exist. | ✅ Pass |
| The Master Build Plan row, the `packages/INDEX.md` row, `ROADMAP.md`'s row and this header agree on status | Read all four directly: all currently say `🔵 COMPLETE` consistently. All four are flipped to `✅ VERIFIED` by this report (see Ledger updates). | ✅ Pass |

## Independent reproduction — fresh scenarios, not the implementer's fixtures

Built a standalone scenario in this session (`verify-ip1262`, seed `7`, two satellites `BLU-SAT-X`/
`RED-SAT-Y`, epoch `2031-06-15T00:00:00Z`, distinct from every fixture `test_ephemeris.py`/
`test_telemetry.py` use) plus a second scenario from the HTTP layer on `leo-isr-denial` (seed `99`)
and a third on `multi-domain-taiwan` (seed `42`, a different seed and offset — +3 h, not the
implementer's +6 h) — all via `SessionManager`/`TestClient` directly, not by importing or calling
any of the implementer's helper functions.

- **`interval_s` boundary values.** `0`, `0.0`, `-1`, `-3.5`, `nan`, `inf`, `-inf` each independently
  raised `ValueError` naming the offending value, both at the `sample_times` level and through all
  three HTTP routes.
- **Exact ceiling vs. one-over, derived arithmetically for a fresh span.** Computed
  `step_us = span_us // (MAX_EXPORT_SAMPLES - 1)` for this session's own 36,000 s span and
  confirmed `sample_times` returns exactly `10,000` instants at that step, and raises on one step's
  worth more span (`10,001` instants) — reproducing the package's "exactly at ceiling succeeds,
  one over fails" claim from first principles rather than re-running its own fixture.
- **Catastrophic-request timing proof (the load-bearing claim).** `sample_times(lo, hi,
  interval_s=1e-6)` over the fresh 36,000 s span (would naively build ~3.6×10¹⁰ instants) raised in
  **0.0044 ms**. A second, independently chosen pathological case — `sample_times(0, 10**15,
  interval_s=1e-9)` (would naively build ~10²⁴ instants, a scenario *six orders of magnitude* more
  extreme than the implementer's own ~10⁷-instant timing test) — raised in **0.0033 ms**. Both
  rejections are sub-millisecond and show **no growth with the attempted sample count**, which is
  the signature of an O(1) arithmetic check; a disguised generate-then-reject would instead show
  cost scaling with (or simply failing to terminate at) the attempted count. This directly and
  independently proves claim #2 in the task: the DoS-shaped defect this package exists to fix is
  genuinely closed, not merely claimed closed.
- **All three call sites independently exercised with the same catastrophic interval**:
  `mgr.telemetry_export(...)`, `ephemeris.truth_ephemeris(...)`, `ephemeris.cell_observed_ephemeris(...)`
  all raised the identical `ValueError` shape on the fresh scenario, confirming the single
  choke point is genuinely shared, not re-implemented per call site with only one path actually
  checked.
- **Route-level, end-to-end timing proof.** On the independently built `leo-isr-denial` session, a
  `GET /telemetry/blue/ISR-EO-1/export.csv?interval_s=1e-6` request spanning the session's full
  recorded range (implying ~1.44×10¹⁰ instants) returned **400 in 3.49 ms** (full FastAPI
  request/response round trip via `TestClient`, not a bare function call) — confirming the
  arithmetic check is reached and enforced at the HTTP boundary, not only in a unit-level call.
- **Valid requests are not over-rejected.** The same fresh scenarios produced correct non-empty
  output for ordinary requests (`telemetry_export`: 209 rows at `interval_s=60`;
  `truth_ephemeris`: 11 rows at `interval_s=60` over a 600 s window; HTTP ceiling-sized request at
  exactly 10,000 instants on `leo-isr-denial`: not separately re-derived at the route level beyond
  the module-level exact-ceiling check above, which is equivalent since the route is a thin
  pass-through with the identical `ValueError`→400 mapping already confirmed).

(Script retained at `/tmp/claude-0/.../scratchpad/verify_ip1262_direct.py` for this session; not
committed — scratch, not a project artifact.)

## Call-site audit — `sample_times` as the single choke point (independent, not trusting the docstring)

Ran `grep -n "sample_times" spacesim/session/*.py` directly. Three call sites exist outside the
function's own definition and tests:

- `spacesim/session/manager.py:911` — inside `SessionManager.telemetry_export`, as the argument to
  `aar.worlds_at_times(self, ephemeris.sample_times(t1, t2, interval_s))`.
- `spacesim/session/ephemeris.py:261` — inside `truth_ephemeris`, as the argument to
  `aar.worlds_at_times(mgr, sample_times(t1, t2, interval_s))`.
- `spacesim/session/ephemeris.py:285` — inside `cell_observed_ephemeris`, the same pattern.

All three pass `sample_times(...)`'s *return value* (a fully-built or exception-raising call,
evaluated eagerly as a plain function-call expression) into `aar.worlds_at_times`, which is itself
a generator function — so none of its body executes until iterated, and `sample_times`'s
`ValueError` is guaranteed to propagate before any replay step runs, for all three export paths.
No fourth, unaudited call site exists; `get_series` (the `BL-0174`/`BL-0173` reversed-window path)
is confirmed, by reading its body directly, to build its own `times` list without going through
`sample_times` at all — consistent with the package's Design Decision 4 ("`get_series` is out of
scope for the cap," already bounded by its route's `n: Query(..., le=2000)`), independently
confirmed by reading that route's declaration (`server.py`) rather than taking the package's word
for it.

## `BL-0174` rider audit (independent, fresh scenario)

Built a fresh `SessionManager` (own vignette fixture, seed `7`) and called `get_series` twice —
once forward (`t0=lo, t1=lo+3600s`), once reversed (`t0=lo+3600s, t1=lo`) — both `n=15`, parameter
`battery_soc` (not the implementer's parameter choice). The reversed call did not raise; its
returned timestamps were exactly the forward call's timestamps in reverse order
(`rev_times == list(reversed(fwd_times))`), and at every shared instant the `value` and `status`
matched the forward call exactly (`bl0174_reversed_window_times_match = True`,
`bl0174_reversed_window_values_match = True`). This independently confirms `VR-1261`'s own
adjudication of the underlying behavior and confirms the new rider test (`test_telemetry.py::
test_series_reversed_window_matches_forward_reversed`) is exercising a real, correctly-passing
property rather than a tautology.

## Requirements audit

| Req ID | Where implemented | Where tested | RTM cell state | Pass/Fail |
|---|---|---|---|---|
| FR-7410 | `session/ephemeris.py::sample_times` (shared), `truth_ephemeris` (caller) | `test_ephemeris.py::test_sample_times_rejects_non_positive_or_non_finite_interval`, `::test_sample_times_enforces_sample_count_ceiling_arithmetically`, `::test_ephemeris_exports_propagate_over_ceiling_rejection`; `test_web.py::test_ephemeris_routes_reject_non_positive_interval_400` — all confirmed present and passing; all independently re-derived with fresh inputs above | RTM row cites `IP-1262` and names every one of these tests; cross-checked each exists | ✅ Pass |
| FR-7420 | `session/ephemeris.py::sample_times` (shared), `cell_observed_ephemeris` (caller) | Same tests as FR-7410 (shared choke point, confirmed by call-site audit) | RTM row cites `IP-1262`, same test list | ✅ Pass |
| FR-2320 | `session/ephemeris.py::sample_times` (shared), `session/manager.py::telemetry_export` (caller) | `test_telemetry.py::test_telemetry_export_over_ceiling_rejected_without_replay`, `::test_series_reversed_window_matches_forward_reversed` (`BL-0174` rider); `test_web.py::test_telemetry_export_route_rejects_over_ceiling_interval_400` — all confirmed present, passing, and independently re-derived above | RTM row cites `IP-1262`, names these tests | ✅ Pass |

No requirement text was changed by this package (confirmed: `01-functional-requirements.md` has no
diff lines from `4fd4591`), matching its own "No requirement text is changed" claim.

## Test run

- `python3 -m pytest` (full suite, independently re-run): **833 passed, 3 skipped, 1 warning in
  128.54s** — exit code 0. Matches the implementer's claimed 833/3 skipped (836 collected) exactly,
  and the claimed baseline-plus-ten (823 + 10 = 833).
- `python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py`
  (independently re-run by name): **14 passed in 1.19s** — exit code 0.
- Both commands run directly in this session against the tree at `e700123` (implementing commit
  `4fd4591` already on this branch) — not re-quoted from the Implementation Summary.
- Separately, **fail-first independently reproduced**: the same 10 parametrized test cases run
  against a detached pre-fix worktree (`daa1915` + the new test files only) produced **8 failed, 2
  passed** — see Verification Checklist audit above.

## Scope audit

`git show 4fd4591 --stat` confirms the implementing diff touched exactly: `spacesim/session/
ephemeris.py`, `spacesim/ui_web/server.py` (docstrings only — confirmed by reading the diff hunks:
only docstring text changed, no route logic), the three declared test files (additions only,
confirmed), plus the declared documentation/ledger files (`CLAUDE.md`, `ROADMAP.md`,
`docs/implementation/00-master-build-plan.md`, `docs/implementation/packages/INDEX.md`, the
package's own file, `docs/requirements/03-requirements-traceability-matrix.md`). No file outside
the package's declared `Files to Modify` / `Documentation Updates` lists was touched. `spacesim/
engine/` and `docs/training/` are both confirmed untouched by this commit (`git log` on the three
manual files shows no commit by `4fd4591`); the manual-impact note was correctly routed to the
backlog (`BL-0182`) instead.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| F1 | `FS-121`'s and `FS-126`'s own `Referenced By` fields still tag `IP-1262` (and `IP-1261`) as `🟢 READY`, stale since both packages advanced past `READY` through `08-code-implementation`. This is a pre-existing, cross-cutting pattern (not introduced by `IP-1262` specifically — `IP-1261` carries the identical staleness in the same two documents) and is not a claim `IP-1262`'s own Documentation Updates section makes; `VR-1260`/`VR-1261` left the same fields untouched on the same grounds (this skill does not edit Feature Specifications). Filed as `BL-0183` rather than fixed here. | Low | `08-training-manual-authoring` or a future `06-feature-specification` touch-up (status-annotation hygiene on FS `Referenced By` fields; not a `09` fix) |

No Medium/High/Critical findings. No defect found in `sample_times`, its three call sites, the
route-level 400 mapping, or the `BL-0174` rider. **Specifically: claim #2 (the arithmetic pre-check)
holds** — every timing measurement in this report, across module-level and HTTP-route-level calls
and across six orders of magnitude of attempted sample count, stayed sub-10-millisecond, with no
observed growth tied to the attempted (rejected) count.

## Ledger updates applied by this report

- **Master Build Plan** (`docs/implementation/00-master-build-plan.md`): `IP-1262` row status
  `🔵 COMPLETE → ✅ VERIFIED`, this report linked.
- **`packages/INDEX.md`**: `IP-1262` row status updated to `✅ VERIFIED 2026-10-11 via VR-1262`.
- **`ROADMAP.md`**: `IP-1262` row status updated to match.
- **Verification `INDEX.md`**: new row added for `VR-1262`.
- **RTM**: no cell correction needed — `FR-7410`/`FR-7420`/`FR-2320` rows already correctly named
  `IP-1262` and its real tests; left as-is (confirmed correct, not re-written).
- **`FS-121`/`FS-126`'s own `Referenced By` fields**: left untouched (still name the package in
  general terms, status tag stale per Finding F1) — this skill does not edit Feature
  Specifications, matching `VR-1260`'s and `VR-1261`'s identical treatment. The staleness is
  instead filed as `BL-0183`.

## Related

[`00-master-build-plan.md`](../00-master-build-plan.md) · [`packages/INDEX.md`](../packages/INDEX.md) ·
[`docs/requirements/03-requirements-traceability-matrix.md`](../../requirements/03-requirements-traceability-matrix.md)
