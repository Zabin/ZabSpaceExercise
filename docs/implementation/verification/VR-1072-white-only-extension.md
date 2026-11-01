# VR-1072 — Verification Report: White-Only Controls, Second Tranche (FR-4320 extension)

> **Document ID:** VR-1072
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1072](../packages/IP-1072-white-only-extension.md) v1.0,
> [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md)
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1072` (closes `BL-0321`, `BL-0324`, `BL-0351`)
> **Feature Mapping:** FS-106 (`FEAT-4300`)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1072 — White-Only Controls, Second Tranche (v1.0)
- **Implementing commit:** `73ad4ac` (branch `claude/ip-1072-build`); tree verified at that commit.
- **Independence:** fresh session; did not implement this package.

## Result

**✅ VERIFIED** — 0 failed checks; 2 Low findings and 1 Info finding (none block).

## Definition of Done audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Tests exist and pass; 1 and 3 seen failing first | `test_white_only_extension.py`: 49 tests pass. Scratch copy with parent `server.py` (`HEAD~1`): the in-session, seat-declaration-adjacent, creation and save tests fail (e.g. `test_creation_refused_when_it_names_a_player_seat[red/observer]`, `test_in_session_controls_refused_for_non_white[save_vignette-*]`, `test_save_vignette_writes_nothing...`). `server.py` restored; `git status` clean | Pass |
| 2 | Eight routes refuse as the table says; success unchanged | AST-derived table below; `server.py:436,547,555,561,580,590` `_require_white`; `:417,:425` `_refuse_player_seat_on_create`; `test_white_succeeds_everywhere` | Pass |
| 3 | Suite green, no assertion weakened; gates green | See Test run. Existing-test edits are `?cell=white` only (diff read line by line: 3 in `test_web.py`, 7 in `test_vignette_creator_ui.py`) | Pass |
| 4 | Diff touches only `server.py`, tests, docs | `git show --stat 73ad4ac`: `server.py`, 3 test files, `CLAUDE.md`, `ROADMAP.md`, MBP, packages index, package header, RTM | Pass |
| 5 | Documentation updates done; `COMPLETE` | CLAUDE.md trust-model sentence extended; RTM FR-4320 Implementation Package cell names `IP-1072`; ledgers set `COMPLETE` | Pass (see F2 for the code-map bullet) |

## Verification Checklist audit

| # | Item | Evidence | Result |
|---|---|---|---|
| 1 | Each Objective-table row has the stated guard | Read `server.py`: create session `load` (`:417`), draft (`:425`), save_vignette (`:436`), creator state/asset PATCH/DELETE (`:547/555/561`), seats (`:580`, shared helper, inline check removed), `red_step` (`:590`) | Pass |
| 2 | Blue `PUT creator/state` and Blue `red_step` give 403, change nothing; White succeeds | `test_in_session_controls_refused_for_non_white` (blue, red, observer, none; before/after snapshot) and `test_white_succeeds_everywhere`. Own probe: `red_step` white 200, blue/red/observer/none 403 | Pass |
| 3 | `POST /api/sessions?cell=blue` 403, registry unchanged; no `cell` 200 | `test_creation_refused_when_it_names_a_player_seat`, `test_creation_with_no_seat_still_works`. Own probe: `/draft` white 200, blue/red/observer 403, none 200 | Pass |
| 4 | `save_vignette` as Blue leaves save directory unchanged | `test_save_vignette_writes_nothing_for_refused_seat_and_one_file_for_white` | Pass |
| 5 | Route table re-derived from the live app shows no listed route lacking the check | Derived (AST over `server.py` decorators, cross-checked against `app.routes`; see table). Every control `FR-4320` lists is guarded or guarded by an equivalent existing mechanism (F1) | Pass |
| 6 | Full suite and both gates green | See Test run | Pass |
| 7 | New tests carry `verifies` marker with live ID; RTM regenerated | Module `pytestmark = verifies("FR-4320")`; `--origin-report=rtm` reports "unchanged" (Test column equals tool output) | Pass |

### Derived mutating-route table (51 handlers; GET/HEAD excluded)

| Class | Routes | Guard |
|---|---|---|
| FR-4320 White-only (`_require_white`) | `clock`, `param`, `start`, `step`, `advance`, `rewind`, `undo`, `inject`, `force/tle`, `force/bulk_import`, `force/ground`, `load_save` (IP-1068); `save_vignette`, `creator/state` PUT, `creator/asset` PATCH + DELETE, `creator/seats`, `red_step` (this package) | 403 for blue/red/observer/none |
| Creation | `POST /api/sessions`, `POST /api/sessions/draft` | `_refuse_player_seat_on_create`: 403 if `cell` is blue/red/observer; no seat allowed (Design Decision 2) |
| White-only by inline check | `injects/{h}/cancel`, `injects/{h}/edit` | `cell != "white"` -> 403 (pre-existing) |
| White-only by body seat (Ack, HTTP 200) | `roles/assign`, `observer/view` | engine/session layer returns `ok:false` "only White Cell may ..." when body `cell` is not white (F1) |
| Player-facing (deliberately exempt, `_reject_observer`) | `order`, `order/validate`, `maneuver/jam/engage/cyber/sigint compute`, `preview/consequence`, `cancel`, `gate/decide`, `roe/change`, `recovery`, `ssn request/cancel` | Observer refused only |
| Exempt, unguarded | `aar/playback/{start,advance,viewpoint,speed}` (playback cursor, not an FR-4320 listed control) | none |

## Requirements audit

| ID | Implemented | Tested | RTM | Result |
|---|---|---|---|---|
| FR-4320 | `ui_web/server.py` (above) | `test_white_only_extension.py` (49) + IP-1068's `test_white_only_controls.py` | Test column equals generated; Implementation Package cell names IP-1072 | Pass |

## Test run

- `python3 -m pytest -m "not browser" --junitxml=...`: exit 0; 1348 tests, 0 failures, 0 errors, 4 skipped.
- `python3 -m pytest -m browser`: exit 0, 10 passed.
- By name, each green: `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`, `test_test_origins.py`, `test_white_only_extension.py`, `test_white_only_controls.py`.
- `python3 -m pytest --origin-report=rtm`: "unchanged".
- Mutation (remove one guard at a time, restore after): `save_vignette`, `creator/state`, `creator/asset` PATCH, `creator/asset` DELETE, `creator/seats`, `red_step`, creation guard in `load`, creation guard in `create_draft` — 8 of 8 detected by the new file. Tree restored (`git status` clean).

## Scope audit

In scope. Existing-test edits are `?cell=white` additions only (10 call sites); no assertion changed. No other callers of the newly guarded routes in `tools/` or `.claude/skills/`; `static/creator.js` and `app.js` use `api.post/put/patch/del`, which attach the seat.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| F1 | `roles/assign` and `observer/view` (listed in FR-4320's text: "assign seats", "designate the Observer") refuse via the **body** `cell` and return HTTP 200 with `ok:false`, not 403, and ignore the query `cell`. A caller who names `white` in the body but `blue` in the query is accepted. `roles_assign` docstring in `server.py` (~line 380) says a White-only check exists but the route body has none (check lives in the session layer). Inconsistent with the 403 convention; consistent with the requirement's "refuse, with a reason". | Low | `07` package (unify onto `_require_white`) / backlog |
| F2 | Package asked for the CLAUDE.md `ui_web/` code-map bullet to note the creation helper; only the trust-model paragraph was updated. Also `FR-4320` Notes "not yet built" wording, GDS-09 §4, `training/08` remain routed (as the package says). | Low | `08-code-implementation` doc pass / `04`, `03`, `08-training-manual-authoring` |
| F3 | `aar/playback/*` POST routes carry no seat check (outside FR-4320's list; documented so a later scope decision is deliberate). A 422 body-validation error precedes the seat check on guarded routes with bad bodies (FastAPI order); harmless. | Info | none |
