# IP-1262 — Time-Span Export Sampling Bounds (interval_s floor + sample-count cap)

> **Package ID:** IP-1262
> **Version:** 1.0
> **Status:** ✅ VERIFIED 2026-10-11 via [`VR-1262`](../verification/VR-1262-export-sampling-bounds.md)
> *(fresh-session, independent — clean, 1 Low finding: `FS-121`/`FS-126`'s own `Referenced By`
> fields still tag this package `READY`, stale and pre-existing, filed `BL-0183`, left unedited per
> the verifier's own Feature-Specification boundary. The arithmetic, up-front sample-count ceiling
> was independently confirmed real — not a disguised full-generation-then-reject — by timing a
> request implying ~10¹⁵–10²⁴ instants: rejected in 0.003–0.005 ms at the module level and 3.49 ms
> through a full HTTP round trip, with no growth tied to the attempted count. All three call sites
> independently confirmed to share `sample_times` by direct code read; the `BL-0174` rider
> independently re-built on a fresh scenario and confirmed correct; the fail-first claim
> independently reproduced on a detached pre-fix worktree (8/10 new cases failed, matching
> exactly). Full suite 833 passed/3 skipped, both permanent gates green (14/14), independently
> re-run.)* *(implemented 2026-10-11 by `08-code-implementation`, pipeline run #105;
> authorized by the project owner 2026-10-11, MSTR-006 §3. `session/ephemeris.py`: `MAX_EXPORT_SAMPLES =
> 10_000` + finite/`> 0` `interval_s` validation and an arithmetic count check in `sample_times` before
> any list/replay; three route docstrings. 10 new tests (Test 1 ×4 parametrized, Tests 2-7); Tests 1-6
> observed failing first (except Test 1's `nan` case, which already raised `ValueError` by accident, as
> the Objective notes), rider Test 7 passing on arrival as intended. Full suite 833 passed/3 skipped
> (836 collected, JUnit-tallied; baseline 823/3), both permanent gates green (14 passed). Measured on
> `multi-domain-taiwan` +6 h: a 9,999-instant telemetry export 1.26 s; an over-ceiling request rejected
> in ~0.1 ms.)*
> **Dependencies:** [FS-121](../../features/FS-121-ephemeris-export.md) v2.0 (`FR-7410`/`FR-7420`;
> resolves its Open Question 2, the sampling-rate/performance ceiling),
> [FS-126](../../features/FS-126-telemetry-csv-export.md) v1.0 (`FR-2320`),
> [IP-1210](IP-1210-ephemeris-export.md) (`VERIFIED`; its Design Decision 2 explicitly deferred a
> hard ceiling "to a future package if real usage shows it necessary"),
> [IP-1260](IP-1260-telemetry-csv-export.md) (`VERIFIED`),
> [IP-1261](IP-1261-telemetry-series-history-remediation.md) (`VERIFIED`, `VR-1261`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0176` (the defect,
> from [REV-TRN-002](../../reviews/training-review-run97-scope.md) F1) and `BL-0174` (rider:
> regression test for `get_series`'s reversed window)
> **Produces:** time-span exports that reject a non-positive or non-finite `interval_s`, and any
> request whose sample count would exceed a fixed ceiling, with a 400 that names the smallest
> acceptable interval. Previously such requests ran an unbounded replay under the session lock.
> **Feature Reference:** [FS-121 — Ephemeris Export](../../features/FS-121-ephemeris-export.md)
> (`FR-7410`/`FR-7420`, Performance Considerations + Open Question 2);
> [FS-126 — Per-Asset Telemetry CSV Export](../../features/FS-126-telemetry-csv-export.md) (`FR-2320`,
> "a bounded, per-request sampling operation")
> **Supersedes:** none — this is a new remediation package
> **Related Topics:** [`spacesim/session/ephemeris.py`](../../../spacesim/session/ephemeris.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*This is a remediation package. Source: `BL-0176` (found by `09-training-manual-review`, REV-TRN-002
F1; reproduced live; triaged `SCHEDULED` for this `07` pass by `00-pipeline-manager` run #103).
It is numbered `IP-1262` as the next slice in the FS-126 remediation series after `IP-1261`.
`IP-1210`/`IP-1260` are `VERIFIED` and are not reopened. Every file, function, and line cited below
was re-checked against the tree at `daa1915`.*

## Package ID

IP-1262

## Title

Time-Span Export Sampling Bounds (interval_s floor + sample-count cap)

## Objective

1. **Close the unbounded-sampling defect.** `session/ephemeris.py::sample_times` (`:48-63`) turns
   an explicit `interval_s` into an integer-microsecond step floored at **1 µs**
   (`max(int(interval_s * 1_000_000), 1)`), then builds every instant in `[t1, t2]`. Today:
   - `GET /ephemeris/truth` (`server.py:907`) and `GET /ephemeris/{cell}` (`:925`) declare
     `interval_s: Optional[float] = None` with no constraint, so `0` or a negative value is
     accepted.
   - `GET /telemetry/{cell}/{asset}/export.csv` (`:754`) declares `Query(None, gt=0)`, which still
     admits `1e-6`.
   - Any of these yields a 1 µs step: `sample_times(0, 10 s, 0.0)` builds 10,000,001 instants.
   - Each instant is then replayed by `aar.worlds_at_times` inside `InProcessSession._locked_read`.
     Over a real span (hours), one request holds the session for effectively unbounded time and
     freezes the exercise for every client.
   - `+inf` raises `OverflowError` in `int()`, which surfaces as a 500. `nan` raises `ValueError`
     and so becomes a 400 only by accident.
2. **Resolve FS-121 Open Question 2 / IP-1210 Design Decision 2's disclosed deferral.** Impose an
   explicit, documented ceiling. This planning pass measured the cost, so the ceiling rests on
   evidence (see Design Decisions).
3. **Rider (`BL-0174`).** Add the missing regression test for `get_series`'s reversed-window
   (`t1 < t0`) handling. `VR-1261` confirmed the behaviour correct but untested. This adds one
   test and no production change, under the same `FR-2320` anchor.

### Design Decisions

1. **One choke point.** Validation lives in `sample_times`, the single function all three
   time-span exports call (`truth_ephemeris :237`, `cell_observed_ephemeris :261`,
   `SessionManager.telemetry_export :911`).
   - Every caller already applies `_clamp_or_reject` first, so the count check runs on the
     **clamped** span.
   - Every route already maps `ValueError` to **400**.
   - No route-level duplicate is required. The telemetry route's existing `gt=0` (a 422) stays as
     an earlier guard.
2. **`interval_s` validity.** An explicitly supplied `interval_s` must be finite and `> 0`;
   otherwise `sample_times` raises `ValueError` with a message naming the value. `None` keeps
   today's default (`max(span/100, BUS_TICK_PERIOD_S)`), unchanged.
3. **Sample-count ceiling.** Add a module constant `MAX_EXPORT_SAMPLES = 10_000` in
   `session/ephemeris.py`.
   - `sample_times` computes the count arithmetically (`(t2 - t1) // step + 1`) **before**
     building the list.
   - If the count exceeds the ceiling, it raises `ValueError` naming the ceiling, the requested
     count, and the smallest `interval_s` that would fit (`(t2 - t1) / 1e6 / (MAX_EXPORT_SAMPLES - 1)`,
     rounded up).
   - Evidence, measured this pass on `multi-domain-taiwan` (seed 1) at +6 h (73 event-log
     entries), whole-span exports: `telemetry_export` takes 0.19 s at 1,000 samples, 0.88 s at
     5,000, and 1.25 s at 10,000. `truth_ephemeris` takes 1.1 s at 10,000.
   - So the ceiling bounds the worst-case lock hold at roughly 1–2 s on a realistic session,
     against today's unbounded hold.
   - The default interval always yields ≤ 101 samples, so default requests can never hit the
     ceiling.
   - A numeric ceiling is a `07` decision: FS-121 §Risks states the sizing "is deferred to
     implementation planning, with no numeric target from any source document". It is disclosed
     here and in the route docstrings.
4. **`get_series` is out of scope for the cap.** Its sample count is already bounded by the route's
   `n: Query(120, ge=2, le=2000)` (Audit Jun 2026 §D6). Only the `BL-0174` test touches it.

## Feature Reference

- **FS-121** v2.0: Performance Considerations ("replay cost scales with sample count × eventlog
  length … mitigation left to `07-implementation-planning`"), Risks, and Open Question 2. These
  were resolved at the default-interval level by `IP-1210` Design Decision 2; this package closes
  the explicit-interval half.
- **FS-126** v1.0: "a bounded, per-request sampling operation over the requested span, not a new
  computational class". Today's explicit-interval path is not bounded; this package makes it so.

## Requirements Covered

| Requirement | How |
|---|---|
| `FR-7410` | Truth export: invalid or over-ceiling sampling requests are rejected with 400 instead of running unbounded. Output for valid requests is unchanged. |
| `FR-7420` | Cell-observed export: same. |
| `FR-2320` | Telemetry CSV export: same. Plus the `BL-0174` reversed-window regression test for the series route's parity path. |

No requirement text is changed. `NFR-1100` (interactive responsiveness of on-demand console
reads) is cited as context for the ceiling, not claimed as newly satisfied.

## Architecture Components

- `session/` layer only: `session/ephemeris.py` (`sample_times`, new `MAX_EXPORT_SAMPLES`).
- `ui_web/server.py`: docstring updates only on the three export routes. The status-code mapping
  already exists, so there is no behavioural change in the routes themselves.
- `engine/` untouched. The import guard and determinism gates are unaffected by construction.

## Interfaces

- `sample_times(t1, t2, interval_s=None) -> list[int]` keeps its signature. It newly raises
  `ValueError` when (a) `interval_s` is not `None` and is not finite or `<= 0`, or (b) the computed
  count exceeds `MAX_EXPORT_SAMPLES`.
- HTTP:
  - `GET /ephemeris/truth`, `GET /ephemeris/{cell}`, `GET /telemetry/{cell}/{asset}/export.csv`
    newly return **400** for those requests, with the `ValueError` message as `detail`.
  - The telemetry route's `interval_s <= 0` stays a **422** (FastAPI `gt=0`).
  - Valid requests are byte-for-byte unchanged, except the OEM `CREATION_DATE` wall-clock stamp,
    which is pre-existing and not in scope.

## Files to Create

None.

## Files to Modify

| File | Change |
|---|---|
| `spacesim/session/ephemeris.py` | Add `MAX_EXPORT_SAMPLES`. Add validation and the arithmetic count check to `sample_times` (`:48-63`). Update its docstring to describe both rejection rules. |
| `spacesim/ui_web/server.py` | Docstrings of `telemetry_export_csv` (`:754`), `ephemeris_truth` (`:907`) and `ephemeris_cell_observed` (`:925`) name the 400 for invalid or over-ceiling sampling. |
| `spacesim/tests/test_ephemeris.py` | New tests (below). |
| `spacesim/tests/test_telemetry.py` | New tests (below), including the `BL-0174` rider. |
| `spacesim/tests/test_web.py` | New route-level tests (below). |

## Implementation Tasks

1. Write Tests 1–7 first and observe 1–6 fail against the current tree. Test 7 is the `BL-0174`
   rider: it passes on arrival, which is expected, because it guards existing correct behaviour.
2. In `sample_times`, after the existing `t2 < t1` early return:
   - Validate an explicit `interval_s` (finite and `> 0`).
   - Compute the step exactly as today.
   - Compute the count arithmetically.
   - Raise `ValueError` if the count exceeds `MAX_EXPORT_SAMPLES`, with the smallest fitting
     interval in the message.
   - Only then build the list.
3. Update the three route docstrings and `sample_times`' docstring.
4. Re-run Tests 1–7, the existing `test_ephemeris.py`/`test_telemetry.py`/`test_web.py` export
   tests (all must stay green unchanged), the full suite, and both permanent gates.
5. Record in the Implementation Summary: the measured time of a ceiling-sized request on
   `multi-domain-taiwan` at +6 h, and confirmation that no existing test needed changing.

## Tests to Add

1. `test_ephemeris.py`: `sample_times` with `interval_s=0`, `-5`, `float("inf")` and `float("nan")`
   each raises `ValueError`. Today they return 1 µs-step lists or raise `OverflowError`.
2. `test_ephemeris.py`: `sample_times` over a span with an interval giving
   `MAX_EXPORT_SAMPLES + 1` instants raises `ValueError`, and the message names the ceiling and a
   minimum interval. The **same** span at exactly the ceiling returns `MAX_EXPORT_SAMPLES` instants.
   Also assert the guard is arithmetic: with an interval that would give ~10⁷ samples, the raise
   returns quickly (time budget well under 1 s).
3. `test_ephemeris.py`: `truth_ephemeris` and `cell_observed_ephemeris` propagate the `ValueError`
   for an over-ceiling request.
4. `test_telemetry.py`: `SessionManager.telemetry_export` with `interval_s=1e-6` over a non-trivial
   span raises `ValueError` and does not run the replay. Spy on `aar.worlds_at_times` or
   `engine.simulation.replay_stepwise` and assert it is not called.
5. `test_web.py`: `GET /ephemeris/truth?...&interval_s=0` → 400, and `GET /ephemeris/blue?...&interval_s=-1`
   → 400. Both are 200-with-a-huge-body/hang today.
6. `test_web.py`: `GET /telemetry/blue/{asset}/export.csv?interval_s=0.000001` over a span → 400,
   with `detail` naming the ceiling.
7. `test_telemetry.py` (**`BL-0174` rider**): `get_series` with a reversed window (`t0 > t1`)
   does not raise. Its point timestamps are the forward call's timestamps reversed, and its
   value/status at every shared instant equal the forward call's.

## Documentation Updates

- RTM (`docs/requirements/03-requirements-traceability-matrix.md`): add `IP-1262` to the
  `Impl. Package` cells of `FR-7410`, `FR-7420` and `FR-2320`, and name the new tests.
- `CLAUDE.md` code map: the `session/` bullet's ephemeris text (if it names `sample_times`) or a
  short addition noting the `MAX_EXPORT_SAMPLES` ceiling.
- `docs/training/15-manual-traceability.md` §15.1: this changes operator-visible behaviour of the
  URL-only exports (a new 400). Route a manual-impact finding for `WCM-15`/`WCM-16`/`BLU-13`/`BLU-14`/
  `RED-12`/`RED-13` to `08-training-manual-authoring`. Do **not** edit `docs/training/` from `08`.
- This package's Status header, the Master Build Plan row, `packages/INDEX.md`, and `ROADMAP.md`'s
  implementation-package row.

## Definition of Done

- An explicit non-finite or non-positive `interval_s` is rejected by all three time-span exports
  (400 at the route; `ValueError` at the session layer).
- A request whose clamped span and interval would exceed `MAX_EXPORT_SAMPLES` is rejected before
  any replay is run.
- Valid requests produce output identical to before: every pre-existing export test passes
  unchanged.
- The `BL-0174` reversed-window test exists and passes.
- RTM, `CLAUDE.md` and the ledgers are updated, and the manual-impact finding is routed.
- The full suite is green, and both permanent gates (`test_determinism.py`, `test_import_guard.py`)
  are green.

## Verification Checklist

- [ ] `git diff` of the implementing commit touches no file under `spacesim/engine/`.
- [ ] `grep -n "MAX_EXPORT_SAMPLES" spacesim/session/ephemeris.py` shows the constant and its use
      inside `sample_times`. The count check precedes list construction (read the function).
- [ ] Tests 1–7 exist and pass. Tests 1–6 were observed failing first, as recorded in the
      Implementation Summary.
- [ ] Independent reproduction: `sample_times(0, 10_000_000, 0.0)` raises, and
      `GET /ephemeris/truth?...&interval_s=0` returns 400 on a fresh session.
- [ ] No pre-existing test in `test_ephemeris.py`, `test_telemetry.py` or `test_web.py` was
      modified (`git diff --stat` on them shows additions only).
- [ ] `python3 -m pytest` passes in full, and `test_determinism.py` and `test_import_guard.py` pass.
- [ ] The RTM `FR-7410`/`FR-7420`/`FR-2320` rows cite `IP-1262`.
- [ ] The Master Build Plan row, the `packages/INDEX.md` row, `ROADMAP.md`'s row and this header
      agree on status.

## Dependencies

- **Packages:** `IP-1210`, `IP-1260` and `IP-1261`, all `VERIFIED`. This package edits the
  sampling function they share, so it is `READY`.
- **Authorization:** granted by the project owner 2026-10-11 (MSTR-006 §3) through the session
  pre-authorization of this iteration's packages. This follows the same precedent as `IP-1261`.
- **Not a dependency:** `BL-0181` (accepting ISO-8601 `t1`/`t2`), which is a separate `04`
  question. `BL-0171` (`FR-2310` historical pass-gating) is unrelated.
- **Parallelism:** there is no ordering constraint with any other open package.

## Risks

- **Ceiling too low for a legitimate use.** At 10,000 samples, a 24 h span can still be sampled
  every ~8.6 s, and a 1 h span every 0.36 s. That is finer than any current vignette's dynamics
  need. If a real use needs more, raise the constant: it is one line, and the cost scales linearly
  (measured above).
- **Ceiling too high on a much longer event log.** Cost is O(samples + log length) after
  `IP-1261`'s single pass. A session with a far longer log than `multi-domain-taiwan` (+6 h,
  73 entries) costs more per sample.
  - The Implementation Summary records a fresh measurement at the ceiling.
  - If it materially exceeds ~2 s, file a finding rather than tuning silently.
- **Message drift.** Tests assert that the message *names* the ceiling and a minimum interval, not
  its exact wording. That keeps the guard meaningful without making it brittle.

## Rollback Considerations

Reverting the implementing commit restores the prior (unbounded) behaviour exactly. There are no
schema, API-shape, persisted-format or `SavedSession` changes, and no data migration. The only
externally visible change is that some previously accepted (pathological) requests now get a 400.
