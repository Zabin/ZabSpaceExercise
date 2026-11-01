# VR-1081 — Verification Report: Save Event-Log Cap Counts a Real Save (NFR-3710, FR-7230, NFR-1600)

> **Document ID:** VR-1081
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1081](../packages/IP-1081-save-eventlog-cap-counts-real-saves.md) v1.0
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1081` (closes GDS-07 `OQ5` for `03` to record)
> **Feature Mapping:** [FS-110](../../features/FS-110-save-and-resume.md)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1081 — Save Event-Log Cap Counts a Real Save's `{"entries": [...]}` Log (v1.0)
- **Implementing commit:** `e30abed` (branch `claude/ip-1081-build`); parent `8911647`.
- **Independence:** fresh session; did not implement this package.

## Result

**✅ VERIFIED** — 0 failed checks; 2 Low and 2 Info findings, none blocking.

## Definition of Done audit

| Item | Evidence | Result |
|---|---|---|
| Over-cap log in either shape refused with a reason, 400, before validation/replay, no session, no registry change | Real `POST /api/sessions/load_save?cell=white`: dict 100,001 and list 100,001 both 400 "eventlog has 100001 entries; limit is 100000" in about 0.2 s; a 100,001-row dict whose last row is a poisoned (unknown-kind) entry gets the same cap error in 0.18 s (no replay); after 3 successful loads and all refusals the session list was `sess-1..sess-3` (refusals consumed no id) | pass |
| Exactly the cap accepted; a real saved session loads unchanged with the same warnings | dict 99,999 and 100,000: 200 (about 0.9 s each). All 19 vignettes: load, start, step 600 s, `save_state()`, JSON round-trip, `load_save_with_warnings` — 19/19 load | pass |
| One refusal path; inline check gone; one constant home with alias | `manager.py` `validate_save` holds the only check (after required-key/type checks, before `EventLog.model_validate`); `inprocess.py` diff removes the inline block; `SessionManager.MAX_EVENTLOG_REPLAY_ENTRIES = 100_000`, `InProcessSession.MAX_EVENTLOG_REPLAY_ENTRIES = SessionManager...` | pass |
| New tests green; audit test unchanged and green; RTM regenerated; full suite and gates green; no allow-list grew | 10 test functions (16 collected) in `test_save_eventlog_cap.py`; `test_defensive_audit_2026.py` untouched by the diff and green; `--origin-report=rtm` run again produced no diff; suites below; diff touches no `*allow*` file | pass (F1, F3) |

## Verification Checklist audit

| Item | Evidence | Result |
|---|---|---|
| Re-derive defect (parent not refused at cap; this commit refuses, no `model_validate`) | Parent `manager.py`/`inprocess.py` restored into a scratch copy: 5 of the 10 new tests fail (dict over-cap DID NOT RAISE, bare-list message, spy/no-consume test, alias AttributeError, HTTP 400); restored copy green. Spy test proves `EventLog.model_validate` is not called | pass |
| Cap is first use of `state["eventlog"]` after required-key/type checks, ahead of both `model_validate` calls | `manager.py` `validate_save` read: the only earlier use is the `None` check in the required-key loop; both `model_validate` calls follow | pass |
| Boundary 100,000 accepted / 100,001 refused, both shapes | HTTP probe above; list 100,000 refused as malformed (not oversize), list 100,001 refused as oversize | pass |
| 400 with reason, JSON detail, no id consumed, no 500 for not-countable shapes | `{}` (200, see F2), `null` (400 missing key), string, int, `[]`, list of non-dicts, `{"entries":[1,2]}`: 400 "malformed" with a pydantic reason; none 500 | pass |
| Valid and legacy saves load with unchanged warnings | 19/19 real saves; legacy path through `validate_save` is unchanged code and covered by `test_save_load_robustness.py`/`test_self_contained_save.py` (green) | pass (F1) |
| Alias and old test name resolve; no other caller depended on the inline check | `test_constant_alias` green; `test_load_save_rejects_huge_eventlog` green; grep shows no other reader of the inline path | pass |
| `FR-4310`: non-White seat refused first | `POST .../load_save?cell=blue` with an over-cap body: 403 "White Cell control: refused unless the request names the white seat" | pass |
| Permanent gates and documentation checks green | below | pass |

## Mutation audit (scratch copy of the tree; original untouched)

| Mutation | Test that fails |
|---|---|
| Cap comparison replaced by `False` (no cap) | `test_dict_shape_over_cap_refused_with_count_and_limit` |
| Count the bare list only | same test |
| Count the `{"entries"}` object only | `test_bare_list_over_cap_still_refused_same_message` |
| Cap check moved after `EventLog.model_validate` / the row loops | `test_bare_list_over_cap_still_refused_same_message` |
| Boundary `>` to `> cap + 1` | `test_dict_shape_over_cap_refused_with_count_and_limit` |
| Boundary `>` to `>=` | `test_dict_shape_exactly_at_cap_passes_the_cap` |
| Alias hard-coded to 99,999 | `test_constant_alias` |
| Constant set to 100,001 | `test_dict_shape_over_cap_refused_with_count_and_limit` |

Every mutation is killed.

## Requirements audit

| ID | Implemented | Tested | RTM | Result |
|---|---|---|---|---|
| `NFR-3710` | `manager.py::validate_save` / `_eventlog_entry_count` | `test_save_eventlog_cap.py` (dict, list, boundary, spy, alias), `test_defensive_audit_2026.py` | Test column regenerated; re-running the generator produces no diff | pass |
| `FR-7230` | same refusal path, `ValueError` to 400, no session | over-cap, consumes-nothing tests | as above | pass |
| `NFR-1600` | not-countable shapes keep their existing 400 reasons | not-countable parametrized test, HTTP 400 test | as above | pass |
| `FR-7210` | valid saves unchanged | `test_valid_saves_still_load` plus 19-vignette probe | as above | pass |

All 10 added tests carry `@pytest.mark.verifies` naming live IDs (`test_test_origins.py` green).

## Test run

| Command | Result |
|---|---|
| `python3 -m pytest -m "not browser" --junitxml=...` | exit 0 — 1665 passed, 4 skipped, 31 deselected |
| `python3 -m pytest -m browser --junitxml=...` | exit 0 — 31 passed, 1669 deselected |
| `test_determinism.py test_import_guard.py test_doc_integrity.py test_test_origins.py` (by name) | exit 0 — 44 passed, 1 skipped |
| `python3 -m pytest --origin-report=rtm` then `git status` | no diff (Test column equals tool output) |

## Scope audit

Diff `e30abed`: `session/manager.py`, `session/inprocess.py`, new `test_save_eventlog_cap.py`, RTM (generated), plus ledger rows (ROADMAP, MBP, packages INDEX) and one sentence in `docs/training/08-http-api-reference.md` (a documented doc step). `spacesim/engine/` has no change in the diff. In scope.

## Ledger audit

The `IP-1081` MBP tally line (79 `VERIFIED`, 2 `COMPLETE`, 1 `READY`, 1 `BLOCKED` = 83) was recounted from the MBP package rows: 79 / 2 / 1 / 1 — correct. After this report: 80 `VERIFIED`, 1 `COMPLETE` (`IP-1079`), 1 `READY` (`IP-1080`), 1 `BLOCKED` (`IP-1160`) = 83.

## Findings

| # | Finding | Severity | Owner |
|---|---|---|---|
| F1 | Package Test 7 asked for a real `save_state` of a started, advanced session and a legacy-shaped save; the shipped test loads only `_good_state()`. Verified manually here (19/19 vignettes after advance) and by existing suites, so behaviour is sound, but the new file does not pin it | Low | `08` (optional hardening) |
| F2 | `eventlog: {}` (object with no `entries`) loads as an empty log (200). This is the pre-existing `EventLog` default, not new, and an empty log is a legitimate fresh-session save; judged sensible. Package Test 5 listed it among the "same errors as today" shapes, but the test omits `{}`, so the decision is unpinned | Low | `07` (note) |
| F3 | The cap-boundary full-load test is validate-level only (the package permits this); a full 100,000-row load completes in about 0.9 s, so a 200 assertion would have been cheap | Info | none |
| F4 | The package's own header still reads `READY` (header reconciliation is `IP-1080`'s scope); the package says "9 tests", 10 shipped | Info | `IP-1080` |

GDS-07 `OQ5` may now be closed by `03`.
