# IP-1072 — White-Only Controls, Second Tranche: Creator Edits, Vignette Saves, Red-AI Step and Session Creation Refuse Other Seats (FR-4320)

> **Package ID:** IP-1072
> **Version:** 1.0
> **Status:** 🟢 READY — authored 2026-10-24 by `07-implementation-planning` (release-push remediation pass).
> Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive of 2026-10-24,
> recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256, authorizes
> remediation packages for bugs, in-progress and critical items, and run #256 names the `FR-4320`
> scope extension as release-blocking. Authoring is not itself the authorization; that recorded
> decision is.
> **Dependencies:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4 (the spec; see
> Risks on its text); [IP-1068](IP-1068-white-only-controls-server-enforcement.md) (`VERIFIED`,
> [VR-1068](../verification/VR-1068-white-only-controls-server-enforcement.md)) whose guard and
> test pattern this extends; [IP-1130](IP-1130-observer-read-only-access.md) and
> [IP-1173](IP-1173-vignette-creator-draft-session.md) / [IP-1174](IP-1174-vignette-creator-ui-surfaces.md)
> (the routes concerned), all `VERIFIED`.
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0321`, `BL-0324`,
> `BL-0351`
> **Produces:** a server that refuses every control `FR-4320` now lists, as extended on 2026-10-24,
> from any seat but White, and a test per newly covered control.
> **Feature Reference:** [FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4
> (`FEAT-4300`; `FR-4320` as extended 2026-10-24)
> **Related Topics:** [`requirements-change-log.md`](../../requirements/requirements-change-log.md)
> (CHG for the `FR-4320` extension); integration review of tranche 2 F-02, F-15

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package (forward design). `IP-1068` is complete as specified; the requirement was
widened afterwards (`BL-0321`, `BL-0324`, `BL-0351`), and this package builds the widening.*

---

## Package ID

IP-1072 (FS-106 slice; `IP-1060`–`IP-1069` are taken, `IP-1070` belongs to FS-107).

## Title

White-only controls, second tranche: the routes `IP-1068` did not cover.

## Objective

`FR-4320` as extended now requires refusal of: creating a session or a Vignette Creator draft;
editing a Creator draft (its state, its assets, its seat declaration); saving a draft or a running
session as a vignette or scenario; triggering the Red doctrine AI's step. Probed on 2026-10-24
(integration review F-02): a Blue `PUT /creator/state` and a Blue `red_step` both return 200.

Route table at `fca85bf` (`ui_web/server.py`), and the change:

| Control | Route | Guard now | Guard after |
|---|---|---|---|
| Create session | `POST /api/sessions` (line ~405) | none | refuse an explicit `blue`/`red`/`observer` seat |
| Create draft | `POST /api/sessions/draft` (~412) | none | same |
| Save vignette/scenario | `POST /{sid}/save_vignette` (~419) | Observer | White only |
| Replace draft state | `PUT /{sid}/creator/state` (~531) | Observer | White only |
| Edit asset | `PATCH /{sid}/creator/asset/{id}` (~537) | Observer | White only |
| Delete asset | `DELETE /{sid}/creator/asset/{id}` (~545) | Observer | White only |
| Seat declaration | `POST /{sid}/creator/seats` (~557) | White only (own inline check) | unchanged; fold into the shared helper |
| Red doctrine AI step | `POST /{sid}/red_step` (~576) | Observer | White only |

**Not in scope, by `FR-4320`'s own text:** orders, their dry-run and compute helpers, order
cancellation, recovery, SSN requests, every cell-scoped read, and the draft reads (`GET
creator/state`, `creator/scene`, `creator/seats`), which are ground-truth reads under `FR-6220`.
`GET /save` is a read and stays out.

### Design Decisions

1. **Reuse `_require_white` for the in-session controls** (save_vignette, Creator edits, red_step,
   the seats route). A request naming no seat is refused, exactly as `IP-1068` refuses it. Order of
   checks stays `_require(sid)` first (unknown session → 404), then the seat check, 
   test 178 pins.
2. **Creation names its seat by the same `cell` query parameter**, which the console's `api.post`
   already attaches to every POST. `FR-4320`'s note leaves the mechanism to this package and
   requires only that a creation request naming a non-White seat is refused. A second helper,
   for example `_refuse_player_seat_on_create(cell)`, raises 403 when `cell` is `blue`, `red` or
   `observer` and **allows an absent `cell`**. Reason: session creation precedes seat selection in
   the hot-seat flow and in the documented curl recipes, tools and several hundred existing tests
   create sessions with no seat; refusing them would break all of that without protecting anything
   the requirement describes (it speaks of a request that *names* a non-White seat). The asymmetry
   with the controls above (absent seat refused) is deliberate and goes in the helper's docstring
   and the completion note. Observer already needs the 403 text the other guards use.
3. **No change to what the routes do** once the guard passes. Response shapes are unchanged.
4. **Update existing tests that call the newly guarded routes with no seat** to pass
   `?cell=white` (the pattern `IP-1068` used for its seven touched modules). Creation tests need no
   change. Do not delete or weaken an assertion.

## Feature Reference

[FS-106](../../features/FS-106-white-cell-dashboard.md) v2.4 and `FR-4320`. The spec text predates
the 2026-10-24 extension; the requirement is the binding statement (GDS-05 is the authority and
`FR-4320`'s leaf already names the routes). See Risks.

## Requirements Covered

| ID | How |
|---|---|
| `FR-4320` | Every control newly listed is refused for a non-White seat; session registry, draft registry and save directory unchanged on refusal. |

Related, not covered here: `FR-4310` (clock, done by `IP-1068`), `FR-5110` / `FR-5510` (the save
features whose routes are guarded), `FR-6220` (the reads left open).

## Architecture Components

- **C4 Web layer** (`ui_web/server.py`): the guard calls only.
- **C2 Session Layer**: untouched. The rejection happens before `SessionManager` or
  `InProcessSession` is reached, as `IP-1068` and `IP-1130` do.

Engine untouched; determinism and import guard unaffected.

## Interfaces

- **INT-0001** (HTTP): the eight routes above return 403 with a reason for a non-White seat. Success
  responses unchanged. 403 body matches `IP-1068`'s `detail` convention.

## Files to Create

- `spacesim/tests/test_white_only_extension.py`.

## Files to Modify

Checked against the tree at `fca85bf`:

- `spacesim/ui_web/server.py`: add the creation helper next to `_require_white` (line ~340); replace
  `_reject_observer(cell)` with `_require_white(cell)` in `save_vignette`, `creator_set_state`,
  `creator_edit_asset`, `creator_delete_asset`, `red_step`; give `load` and `create_draft` a
  `cell: Optional[str] = None` parameter and call the creation helper; replace `declare_seats`'s
  inline check with `_require_white(cell)` keeping its message intent.
- Existing tests that hit the newly guarded in-session routes without a seat, to pass
  `params={"cell": "white"}`: expected `spacesim/tests/test_web.py` (Creator and save_vignette
  cases near lines 514–620), `test_vignette_creator_session.py`, `test_vignette_creator_ui.py`,
  `test_vignette_export.py`, `test_observer.py` (its Observer cases keep passing: Observer is
  refused either way). Find the full set by running the suite and reading the 403 failures; do not
  guess.

No other production file changes. `static/*.js` needs no change: `api.post/put/patch/del` already
attach the active seat, and the console starts as White.

## Implementation Tasks

1. Mark the package `IN PROGRESS` (header, MBP row, index, `ROADMAP.md`) before editing.
2. Write the tests below; see tests 1–4 fail against the current server for the stated reason.
3. Implement Design Decisions 1–3.
4. Run the whole suite; fix the existing tests that now get 403 per Design Decision 4. Run
   `test_determinism.py` and `test_import_guard.py`.
5. Documentation updates, then mark `COMPLETE`.

## Tests to Add

`spacesim/tests/test_white_only_extension.py`, module marker `@pytest.mark.verifies("FR-4320")`,
following `test_white_only_controls.py`'s structure (`NON_WHITE = ["blue", "red", "observer", None]`,
a before/after state snapshot, a freshly created client per test).

1. **In-session controls refused for every non-White seat.** Parametrize the five routes
   (`save_vignette`, `PUT creator/state`, `PATCH creator/asset/{id}`, `DELETE creator/asset/{id}`,
   `red_step`) by the four non-White seats, on a started session or a draft as the route needs.
   Assert 403 and that the snapshot (asset set, event log length, order count, `user_save_dir`
   listing) is unchanged. Before the change: 200 for blue, red and None.
2. **Seat declaration** refused for every non-White seat, accepted for white (regression of the
   existing inline check through the shared helper).
3. **Creation refused when the request names a player seat.** `POST /api/sessions` and
   `POST /api/sessions/draft` with `cell` in blue/red/observer: 403 and `GET /api/sessions` lists no
   new session; the draft registry has no new draft. Before: 200.
4. **`save_vignette` writes nothing for a refused seat.** With `content.user_save_dir` pointed at a
   temporary directory (IP-1180's configuration), a refused call leaves the directory empty; the
   same call as white writes exactly one file.
5. **White succeeds everywhere.** The same eight requests naming `white` return their normal
   success status.
6. **Creation with no seat still works.** `POST /api/sessions` and `/draft` with no `cell` return
   200 (pins Design Decision 2 so the asymmetry cannot drift unnoticed).
7. **Unknown session is 404 before the seat check** for each in-session route (mirrors
   `IP-1068`'s check, so a probe cannot tell sessions apart by seat).
8. **Reads stay open.** `GET creator/state`, `creator/scene`, `creator/seats` return 200 with no
   seat (`FR-6220`, override marker), so the guard does not over-reach.

## Documentation Updates

- `docs/requirements/01-functional-requirements.md`: `FR-4320`'s Notes sentence "the extension is
  not yet built" is stale after this lands; the edit belongs to `04-requirements-engineering`,
  not to the implementer. Route it as a finding in the completion note.
- `docs/requirements/03-requirements-traceability-matrix.md`: the `FR-4320` Test and Implementation
  Package cells gain this file and `IP-1072` (Test column generated by
  `python3 -m pytest --origin-report=rtm`, same commit).
- `docs/features/FS-106-white-cell-dashboard.md`: `Referenced By` only.
- `docs/architecture/09-api-specification.md` §4 and OQ1 describe the White-only set; route to
  `03-architecture-design-synthesis`, do not edit here.
- `CLAUDE.md`: the "White Cell controls are refused to any request not naming the `white` seat"
  sentence in the LAN trust-model paragraph gains the extended list; the `ui_web/` code-map bullet's
  `_reject_observer` guard sentence notes the creation helper.
- Training manual: `docs/training/08-http-api-reference.md` states the seat requirement for these
  routes. Manual upkeep through `docs/training/15-manual-traceability.md` §15.1; authoring goes to
  `08-training-manual-authoring`.
- MBP row and tally, `packages/INDEX.md`, `ROADMAP.md`, this header.

## Definition of Done

- All Tests to Add exist and pass; tests 1 and 3 were seen failing first.
- The eight routes refuse as the Objective table says; the success path is unchanged.
- The whole suite is green with no assertion weakened; `test_determinism.py` and
  `test_import_guard.py` green.
- `git diff --stat` touches only `ui_web/server.py`, tests, and docs.
- Documentation updates done; status `COMPLETE`.

## Verification Checklist

1. Each row of the Objective table has the stated guard in `server.py` (read the code).
2. Reproduce independently: a Blue `PUT creator/state` and a Blue `red_step` now give 403 and
   change nothing; the same as White succeed.
3. A Blue `POST /api/sessions?cell=blue` gives 403 and the registry is unchanged; with no `cell` it
   still gives 200.
4. `save_vignette` as Blue leaves the save directory unchanged.
5. The derived route table (re-derive from `app.routes`, as `VR-1068` F1 did) shows no route that
   `FR-4320` lists and that lacks the White check.
6. Full suite and both permanent gates green.
7. Every new test carries a `verifies` marker naming a live baseline ID; RTM Test column regenerated.

## Dependencies

`IP-1068`, `IP-1130`, `IP-1173`, `IP-1174` (all `VERIFIED`). No other open package edits the
guarded routes. `IP-1102` and `IP-1072` both edit `ui_web/server.py` (different routes): build
serially, `IP-1102` first, as the Master Build Plan orders them.

## Risks

- **Spec text lag.** FS-106 v2.4 predates the `FR-4320` extension, and GDS-09 §4 / OQ1 and
  `design/07` still describe the shorter list. The requirement leaf is binding and names the
  routes, so the package proceeds on it; the recommendation to `06` (a v2.5 note on FS-106) and
  `03` is recorded here for the Master Build Plan, not worked around.
- **Console flows that create or save from a non-White seat.** A Blue tab that clicks Load or
  saves as scenario now gets a visible refusal. `loadVignette` and `saveAsScenario` already show
  errors (`IP-1310`, `IP-1065`); the Creator UI's behaviour on a refused edit is checked by
  `IP-1073`'s browser tests, not here.
- **Hidden callers without a seat.** Tools and skill recipes (for example `tools/record_walkthrough.py`
  and `run-spacesim`) may call the newly guarded routes. The walkthrough recorder's creation call is
  unaffected (creation allows no seat); `IP-1073` fixes its time-advance beat. Grep `tools/` and
  `.claude/skills/` for the eight routes during the task and report any other caller.
- **Not authentication.** Same trust level as `IP-1068` and `IP-1130`; a participant who lies about
  their seat bypasses it.

## Rollback Considerations

Revert the commit. No data or format change. The existing tests edited to pass `?cell=white` keep
passing under the old server (the parameter is ignored there).
