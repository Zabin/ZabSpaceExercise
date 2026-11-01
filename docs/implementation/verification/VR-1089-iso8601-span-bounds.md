# VR-1089 — ISO-8601 UTC Bounds on the Three Time-Span Exports

[↑ Verification index](INDEX.md) · [Package](../packages/IP-1089-iso8601-span-bounds.md) · [Master Build Plan](../00-master-build-plan.md)


## Version
**v2.0 — VERIFIED** (fresh-session re-verification, tree `1163b3d`, on top of `b53a2a1` tests/message and `d9d64b3` v1.0). v1.0 (RETURNED, tree `d1b0232`) is kept below as history.

## Result (v2.0)
**VERIFIED** — 0 failed checks. F1 (Medium) and F2/F3/F4 (Low) are closed. Code, tests, gates, RTM, ledgers and every training page that mentions the bounds are true against the shipped app.

## Re-verification evidence
| Finding | Evidence | Result |
|---|---|---|
| F1 training pages | Driven live (uvicorn loopback, vignette 01, `ISR-EO-1`). `08` worked example run both ways: ISO `Z`, integer, and mixed bounds give identical telemetry CSV, ephemeris csv and ric; OEM differs only in `CREATION_DATE`. First row `2030-03-15T06:00:00+00:00`, matching the doc. `09a` messages triggered and equal to the quoted text: no-zone (`t1: ... is not an ISO-8601 UTC timestamp (YYYY-MM-DDThh:mm:ss[.ffffff]Z or +00:00; ...) or integer microseconds`), `t2: 'banana'`, wholly-outside span, over-ceiling sampling. Read and grep: `12a:92,127`, `13:247`, `13a:134-137`, `14:250`, `14a:95`, `08:108-136`, glossary, `15` row, WCM-15/16 (12a), BLU-13/14, RED-12/13 all state ISO-or-integer and a 400 naming the bound; no page still says 422 or integer-only (grep for `valid integer`/`422` on the bounds finds none) | pass |
| F2 | Parity test now builds a co-orbital session with a Blue-owned track and asserts bodies longer than 5 lines. Mutation: ISO path shifted by 1 s in `span_bounds.py` -> `test_http_iso_and_integer_bodies_identical_all_routes_and_formats` (and 3 others) FAIL; reverted | pass |
| F3 | 5000-digit string -> 400 `t1: integer microseconds has too many digits (5000); give an ISO-8601 UTC timestamp or a smaller integer` | pass |
| F4 | `2100-02-29` -> 400 `t2: ... has an out-of-range date field`; `2032-02-29` accepted (200, rows); `2000-02-29` parses (refused only as a wholly-outside span) | pass |
| Earlier behaviours | formats, refusals, clamp/reject, guard order and fog covered by `test_span_bounds.py` (all pass) plus the probes above | pass |

## Observation (Low, not a defect)
Swapping `t1` and `t2` returns 200 with a header-only file (confirmed for telemetry csv, ephemeris csv and oem, and with integer bounds too). It is pre-existing, deliberate behaviour (`sample_times` returns `[]` when `t2 < t1`), unchanged by this package, and `08:136` states it plainly ("gives a header-only CSV rather than an error"). A 400 would be friendlier; route to the backlog if wanted. Not a finding against IP-1089.

## Test run (v2.0)
Named: `test_doc_integrity.py`, `test_training_sources.py`, `test_training*.py`, `test_test_origins.py`, `test_origin_retag.py`, `test_span_bounds.py`, `test_determinism.py`, `test_import_guard.py` all pass. Each mode once with `--junitxml`: unfiltered 2203 tests, 0 fail, 0 error, 4 skip, exit 0; `-m "not browser"` 2161, 0 fail, 5 skip, exit 0; `-m browser` 42, 0 fail, exit 0. Worktree clean afterwards.

## Ledgers
Master Build Plan package table recounted: 91 `VERIFIED` (90 before this update), 0 `COMPLETE`, 3 `READY` (`IP-1092/1093/1094`), 94 packages; the status line and the row agree. Header-vs-rows script: the only mismatch is the `IP-1089` package file's own `Status:` header, still `READY` since authoring (not touched by `09`; reconcile in the next ledger reconciliation, as was done for `IP-1088`). Not a verification failure.

## Pipeline note
Verified in a fresh session; the implementer's and the v1.0 verifier's sessions are not this one.

---

# v1.0 (history) — RETURNED

## Package
`IP-1089` (`FR-7450`; FS-121 v2.3), implementing commits `ee2bf73` + `d1b0232` on `claude/ip-1089-build`, parent `dbce510`. Verified in a fresh session (independent of the implementer) on tree `d1b0232`.

## Result
**RETURNED** — 1 failed check (documentation, Medium). Code, tests, gates, RTM and ledgers pass; the shipped training manuals still state the now-false pre-package behavior.

## Definition of Done audit
| Item | Evidence | Result |
|---|---|---|
| New tests green, observed failing first | `test_span_bounds.py` 38 tests pass; on the parent (`dbce510`) over real HTTP every route answers `422 int_parsing` for an ISO bound | pass |
| Full suite `-m "not browser"` green | 2161 tests, 0 fail, 0 error, 5 skip, exit 0 (`--junitxml`) | pass |
| Permanent gates | `test_determinism.py`, `test_import_guard.py` pass by name; `git diff dbce510 HEAD -- spacesim/engine` empty | pass |
| `test_doc_integrity.py`, `test_test_origins.py` (+ `test_origin_retag.py`) green | pass | pass |
| RTM Test column regenerated | `--origin-report=rtm` leaves the tree clean; `test_the_committed_matrix_test_column_equals_the_generated_one` passes in the unfiltered run | pass |
| Documentation per Manual impact | see Documentation audit | **fail** |

## Verification Checklist audit
| Item | Evidence | Result |
|---|---|---|
| `span_bounds.py` pure | imports only `math`, `re`, `typing`; no clock/RNG/engine/ui_web | pass |
| No other `t1`/`t2` parsing on the three exports; `_clamp_or_reject` the only caller | grep: only `ephemeris.py:48-49` calls `parse_span_bound`; manager's `int(t1)` pre-cast removed. Live route table has exactly four routes with `t1`/`t2`: the three exports plus the series read (`t0`/`t1`, deliberately out of scope per FR-7450); no route missed | pass |
| Parity test covers all three exports and three formats | test present; but see F2 (ephemeris legs vacuous) | pass with finding |
| Series, RIC view, ledger, AAR untouched | diff; series `t0=<ISO>` still 422 | pass |
| 400 detail names `t1`/`t2` and a reason | probed every refused form below | pass (one gap, F3) |
| Gates and full suite | above | pass |
| Docs in sync | F1 | **fail** |

## Requirements audit
`FR-7450`: `span_bounds.py` + `ephemeris._clamp_or_reject`; tested by `test_span_bounds.py`; RTM cell filled (FS-121 v2.3, 8+ tests). `FR-2320`, `FR-7410`, `FR-7420`, `FR-7430`, `NFR-3710`: regression-protected, existing tests green, RTM cells regenerated and equal to tool output. Pass.

## Test run
`python3 -m pytest` unfiltered: 2203 tests, 0 failed, 4 skipped, exit 0. `-m "not browser"`: 2161, 0 failed, 5 skipped, exit 0 (the extra skip is the RTM-equality test, which skips under a marker filter and passes unfiltered). `-m browser`: 42, 0 failed, exit 0. Gates and `test_vignette_tutorials.py` run by name: green. Each mode run once.

## Real-HTTP probe (uvicorn loopback, vignette 02 for real satellite data)
Telemetry CSV, truth ephemeris, cell-observed ephemeris x csv/oem/ric: ISO `Z`, `+00:00`, mixed ISO/int pairs and digit-string bounds give bodies equal to the microsecond request (OEM `CREATION_DATE` aside), with real rows (truth 7, Blue 7 after an observe order). Fog: Blue gets its own track rows; Red/Observer/White get header-only; telemetry Red/Observer 404 as before. Accepted: fractions of 1..6 digits, negative integers, `-0`. Refused 400 naming `t1`: naive, `+05:00`, `-00:00`, date-only, lower-case `t`/`z`, leading/trailing space or newline, empty, `NaN`, `Infinity`, `true`, `1.5`, `1e6`, `+5`, Unicode digits, `0x10`, comma fraction, 7 fractional digits, 2030-02-30. Wholly out of range (ISO or integer) rejected; partial span clamped identically; `t1>t2` returns the header only, as before; `MAX_EXPORT_SAMPLES` still refused in 0.0 s via ISO or integer before replay. Arithmetic equals `datetime` across 2030-12-31, 2030-03-01, 2032-02-29, 2100-02-28, 2000-02-29; sixth digit exact, no rounding.

## Mutations (copy of the tree; `test_span_bounds.py`)
Killed: accept naive; accept other offsets; 7-digit rule dropped; parser skipped on truth route; parser skipped on telemetry route; integer fallback broken; digits read as date; bool accepted; lower-case accepted; fraction left-padded wrongly; bound name dropped from message. Survived: leap-second branch removed (equivalent, the later `ss > 59` still refuses); century-year leap rule removed (2100-02-29 untested, F4). Guard reorder not separately mutated (the parser is the first statement of `_clamp_or_reject`; refused-bound-no-replay test exists).

## Documentation audit
Manual impact claim: *update*. Delivered: `08-http-api-reference.md:108` rewritten (accepted forms, one example, 400 rule); §15.1 rows for ephemeris and telemetry CSV carry `session/span_bounds.py`; CLAUDE.md code-map bullet added; route docstrings. Sources resolve; `test_doc_integrity` green. Handed off to `08-training-manual-authoring` (in the package's Manual impact): `WCM-15`, `WCM-16`, `BLU-13`, `BLU-14`, `RED-12`, `RED-13`, 12a. Not delivered or accurate: **F1**. Refusal text is described in 08 but not quoted per reason (F3, Low).

## Scope audit
Inside the declared set (+ implied tests/docs). `docs/training/08` and `15` edited beyond the "docstrings and one Sources cell" limit; benign and accurate.

## Findings
| ID | Finding | Severity | Owner |
|---|---|---|---|
| F1 | Shipped manuals now state false behavior: `docs/training/13a-blue-cell-rules-and-delivery.md:135` ("an ISO date such as `2030-03-15T06:00:00Z` gets a `422` ... `Input should be a valid integer`") and `14a-red-cell-rules-and-delivery.md:95` are wrong for the three exports; `12a:92,128`, `13:247`, `14:249` say integer-only. 13a and 14a are not in the package's hand-off list, and no Manual-impact item with owner and due-before-release exists in the backlog or an implementation summary. | Medium | `08-code-implementation` re-run (record the hand-off with owner/due date) then `08-training-manual-authoring` |
| F2 | Parity test's ephemeris legs use `leo-isr-denial` with `ISR-EO-1`/`JAM-NORTH`; `JAM-NORTH` is not a satellite, so truth and Blue ephemeris bodies are header-only (OEM bodies empty) and the ISO-vs-integer equality is vacuous for them. Only the telemetry leg compares data. The code is correct (my probe with real satellites matches), but the test would not catch a data-path divergence. | Low | `08-code-implementation` |
| F3 | A digit string over 4300 characters is refused with Python's "Exceeds the limit (4300 digits)..." message, which does not name `t1`/`t2`. | Low | `08-code-implementation` |
| F4 | No test for a century non-leap date (2100-02-29); mutation survives. | Low | `08-code-implementation` |

## Pipeline note
Verified in a fresh session; the implementer's session is not this one.
