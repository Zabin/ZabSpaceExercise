# IP-1091 — Clock-Lag Watchdog Test (NFR-1300)

> **Package ID:** IP-1091
> **Version:** 1.0
> **Status:** VERIFIED 2026-10-24 ([VR-1091](../verification/VR-1091-clock-lag-watchdog-test.md), fresh session; READY before that) — authored 2026-10-23 by `07-implementation-planning`, pipeline run #224. Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** Owner-authorized 2026-10-23 (master build plan row; `run #230` ledger note). Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** [IP-1090](IP-1090-multiplayer-session-transport.md) (the lazy clock and the
> watchdog), `VERIFIED`.
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md),
> [`backlog.md`](../../pipeline/backlog.md) `BL-0309`
> **Produces:** the test `NFR-1300` names as its verification, which does not exist today.
> **Feature Reference:** [FS-109](../../features/FS-109-multiplayer-session-transport.md) (the
> lazy clock); `NFR-1300` (`FEAT-1200`); GDS-10 finding F1; requirements review R3.

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Test-only remediation.*

---

## Package ID

IP-1091.

## Objective

**As built at `eba9c04`**, `SessionManager._record_catch_up_lag` (`session/manager.py` line 366)
keeps the last eight catch-up wall costs; with at least four samples it sets a warning when their
average exceeds 0.3 s (severity `high` above 0.8 s, else `medium`, with the asset count and a
message) and clears it otherwise; `clock_state()` (line 403) returns it as `lag_warning`, served by
`GET /api/sessions/{sid}/clock` (`server.py` line 435). No test exercises any of this. After this
package, tests do.

## Requirements Covered

NFR-1300.

## Architecture Components

Tests only (C2 session layer exercised).

## Interfaces

INT-0002 (`GET …/clock`), read by one test.

## Files to Create/Modify

- **Create** `spacesim/tests/test_clock_lag_watchdog.py`.

## Implementation Tasks

1. Write the tests below, feeding synthetic wall costs to `_record_catch_up_lag` (no real timing,
   so the tests are deterministic and fast).
2. Run them; they should pass on the current code (this package adds missing coverage; if one
   fails, that is a defect to report, not to fix here — route back to `07`).
3. Full suite, both gates.

## Tests to Add

| Test | Verifies | Asserts |
|---|---|---|
| Fewer than four samples: no warning, however large | `NFR-1300` | `lag_warning` is `None` |
| Four samples averaging above 0.3 s: `medium` warning with average, asset count and message | `NFR-1300` | fields present and correct |
| Average above 0.8 s: `high` | `NFR-1300` | severity |
| Average falling back below 0.3 s clears the warning | `NFR-1300` | `None` again |
| Only the last eight samples count | `NFR-1300` | an old spike no longer affects the average after eight newer samples |
| The warning reaches White through `GET /api/sessions/{sid}/clock` | `NFR-1300` | response `lag_warning` matches |

## Documentation Updates

RTM `NFR-1300` Test cell; GDS-10 finding F1 is `03`'s to close at its next pass.

## Definition of Done

1. The six tests exist, pass and are tagged `NFR-1300`.
2. No production file changed.
3. Full suite and both gates green.

## Verification Checklist

- [ ] Tests use synthetic samples (no sleeps, no wall-clock dependence) — read them.
- [ ] Only the new test file changed.
- [ ] Both gates green by name.

## Dependencies

IP-1090 — `VERIFIED`.

## Risks

Testing a private method couples the test to its name; acceptable here because `NFR-1300` names
that method as its verification target. If it is renamed, the test should move with it.

## Rollback Considerations

Delete the test file.
