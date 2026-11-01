# IP-1081 — The Loaded Save's 100,000-Entry Event-Log Cap Counts a Real Save's Log (`{"entries": [...]}`), Not Only a Bare List (NFR-3710, FR-7230, NFR-1600)

> **Package ID:** IP-1081
> **Version:** 1.0
> **Status:** VERIFIED 2026-10-24 ([VR-1081](../verification/VR-1081-save-eventlog-cap-counts-real-saves.md), fresh session; READY before that) — authored 2026-10-24 by `07-implementation-planning`. Shipped test count: 10 test functions (16 collected) in `test_save_eventlog_cap.py`; the body's "about 9" / "Nine new tests" are the planning estimate ([VR-1081](../verification/VR-1081-save-eventlog-cap-counts-real-saves.md) F4), left as written.
> **Earlier status record (superseded by the line above; retained as history, unedited):** READY — authored 2026-10-24 by `07-implementation-planning` (release-push remediation pass 5). Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive of 2026-10-24, recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256 (bugs, in-progress and critical items), covers it: a bounded-work guard that does not fire on real saves is a bug in a `VERIFIED` package's behaviour. Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** [IP-1101](IP-1101-self-contained-saves.md) (`VERIFIED`; `validate_save`, the save envelope), [IP-1102](IP-1102-save-load-robustness.md) and [IP-1103](IP-1103-save-validation-completion.md) (`VERIFIED`; the 400-with-reason and no-session-consumed contract), the June 2026 audit item §D7 that introduced the cap (`test_defensive_audit_2026.py`).
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md), [`01-technical-work-breakdown.md`](../01-technical-work-breakdown.md) ("Release-push remediation, pass 5"); the defect is recorded as `OQ5` in [GDS-07](../../architecture/07-data-model.md) on branch `claude/stale-docs-gds` (commit `4eac964`).
> **Produces:** a load that refuses a save whose event log exceeds `MAX_EVENTLOG_REPLAY_ENTRIES` in either shape, before any model validation, replay or session is created.
> **Feature Reference:** [FS-110 — Save and Resume](../../features/FS-110-save-and-resume.md)
> **Related Topics:** [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py), [`spacesim/session/manager.py`](../../../spacesim/session/manager.py), [`spacesim/ui_web/server.py`](../../../spacesim/ui_web/server.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Bug-fix package (one defect, small). Prose only; no code in this document.*

---

## Package ID

IP-1081.

## Title

Make the load-time event-log size cap see the log shape `save_state` actually writes.

## Objective

**Defect (GDS-07 `OQ5`).** `InProcessSession.load_save_with_warnings` (`session/inprocess.py`, lines about 1120-1127) reads `state["eventlog"]` and refuses it when `isinstance(eventlog, list)` and `len(eventlog) > MAX_EVENTLOG_REPLAY_ENTRIES` (100,000). But `SessionManager.save_state` (`session/manager.py`, line about 1116) writes `"eventlog": self.sim.eventlog.model_dump()`, which is an object, `{"entries": [...]}`. The cap therefore never fires on a save the product itself wrote. Worse, `SessionManager.validate_save` runs next and calls `EventLog.model_validate` on the whole object (twice: once to check, once for the last-event bound), so an over-cap save is fully pydantic-validated, and `from_state` then replays it: the compute and memory amplifier `NFR-3710` says must be refused "before any replay or sampling begins". The audit's test (`test_load_save_rejects_huge_eventlog`) passes only because it builds a bare list, a shape `validate_save` would reject anyway as malformed (`EventLog.model_validate` accepts only the object form). The guard's one test exercises a shape no real save has.

**Correct behaviour, from the requirements.**
- `NFR-3710` (Bounded work on untrusted input; GDS-06 NFR-15): the number of entries in a loaded save's event log is capped; an over-limit request is refused before any replay begins; the cap is `MAX_EVENTLOG_REPLAY_ENTRIES` (100,000).
- `FR-7230` / `NFR-1600`: an unusable save is a refusal with a reason (HTTP 400 on `POST /api/sessions/load_save`, `ValueError` in process), naming the problem, never a 500, and it consumes no session id and changes no registry state (`IP-1102`, `IP-1103`).
- `FR-7210`: a valid save (one the product wrote, within the cap) loads unchanged, with the same warnings.

So: the count is the number of event-log entries whichever shape carries them; more than the cap is refused with a reason naming the count and the limit; exactly the cap is accepted; the check runs before the log is model-validated or replayed.

## Requirements Covered

| ID | How |
|---|---|
| `NFR-3710` | The cap is applied to the real save shape, before validation and replay. |
| `FR-7230` | An over-cap save is an unusable save: refused with a reason, 400, no session, no registry change. |
| `NFR-1600` | Never a 500; the over-cap refusal and the unchanged refusals of other malformed shapes. |
| `FR-7210` | A save the product wrote loads as before (valid saves unaffected). |

## Architecture Components

`session/manager.py::SessionManager.validate_save` (and one new small static helper beside it), `session/inprocess.py::InProcessSession.load_save_with_warnings` and the `MAX_EVENTLOG_REPLAY_ENTRIES` constant, `ui_web/server.py::load_save` (unchanged; it already maps `ValueError` to 400). Layering: `session/manager.py` may not import `session/inprocess.py`, so the constant's home moves down (Design Decision 2). Load-bearing invariants: deterministic core untouched (nothing in `engine/`); fog-of-war untouched; the `/load_save` route stays White-only (`FR-4310`).

## Interfaces

- `POST /api/sessions/load_save` (unchanged request and success body `{session, warnings}`): an over-cap save, in either log shape, now answers 400 with `detail` of the existing form, "eventlog has N entries; limit is 100000", and creates no session.
- `SessionManager.validate_save(state)` (static): gains the cap check as the first thing it does with `state["eventlog"]`, ahead of `EventLog.model_validate`; raises `ValueError` with the same message. Its other behaviour is unchanged.
- A new static helper on `SessionManager` returns the entry count for a log value: the length for a list; the length of `entries` for an object whose `entries` is a list; otherwise "not countable" (so the existing malformed-shape errors fire unchanged). A bool, string, number or `None` log is not countable.

### Design Decisions

1. **Count both shapes; the real shape is the object.** A bare list is not a shape `save_state` ever writes and `validate_save` refuses it as malformed once under the cap; it stays counted so that the existing audit test (and any older client) still gets the size refusal, not a pydantic dump of 100,000 rows. A not-countable value falls through to the existing "malformed" or "missing key" refusals; this package invents no new reason for them.
2. **One place, below the session layer.** The cap moves into `SessionManager.validate_save` (with its constant, `SessionManager.MAX_EVENTLOG_REPLAY_ENTRIES = 100_000`), so every caller of `validate_save` is protected and the check precedes `EventLog.model_validate` in the same function. `InProcessSession.MAX_EVENTLOG_REPLAY_ENTRIES` stays as a read-through alias of the manager constant (the audit test and any reader reference it by that name; same value). The inline check in `load_save_with_warnings` is removed; the method keeps calling `validate_save` first, before `from_state` and before the session counter moves. Relation to `validate_save`: the cap is the first rung of validation, not a separate pre-check, so there is one refusal path and one message.
3. **Boundary.** The cap is strict greater-than, as today: exactly 100,000 entries is accepted by the cap check; 100,001 is refused. (A save's log over the cap cannot arise from play: the product itself would have to write more than 100,000 entries; the cap remains a hostile-input bound.)
4. **Cheap before costly.** The count must not materialise anything new: `len` of an already-parsed list. The over-cap path must not call `EventLog.model_validate` (tested by a spy).
5. **No new time/size limits.** Other bounded-work limits (`MAX_LIVE_SESSIONS`, `MAX_EXPORT_SAMPLES`) are unchanged; request body size at the HTTP layer is out of scope (a deployment concern).
6. **Not changed:** the `save_state` shape (no migration; old saves keep loading), `final_time` and span checks, `from_state`. The GDS-07 `OQ5` text is owned by `03`; it closes when this package is `VERIFIED` (a pointer for the pipeline, not an edit made here).

## Files to Create

- `spacesim/tests/test_save_eventlog_cap.py` — the new tests (Tests to Add). Alternatively appended to `test_save_load_robustness.py` if the builder prefers its helpers (`_client`, `_good_state`); a new file avoids touching that module's pinned rows in `test_origin_retag.py`.

## Files to Modify

- `spacesim/session/manager.py` — `validate_save` cap check and helper; the constant.
- `spacesim/session/inprocess.py` — remove the inline cap check; alias the constant.
- `spacesim/tests/test_defensive_audit_2026.py` — only if the existing test needs a docstring pointer; its behaviour must still pass unchanged (a bare list over the cap is still refused).
- `docs/requirements/03-requirements-traceability-matrix.md` — Test column regenerated by `python3 -m pytest --origin-report=rtm` (generated, never hand edited).
- Documentation named below.

## Implementation Tasks

1. Test-first: write the matrix below; confirm the dict-shaped over-cap cases fail today (the save is not refused at the cap, or is refused only after full validation) and the others pass.
2. Add the helper and the cap to `validate_save`; move the constant; alias it on `InProcessSession`; remove the inline check.
3. Grep every use of `MAX_EVENTLOG_REPLAY_ENTRIES` and of `load_save`/`validate_save` (server, tests, tools) and confirm none depends on the inline check.
4. Run the new tests, `test_save_load_robustness.py`, `test_self_contained_save.py`, `test_defensive_audit_2026.py`, `test_determinism.py`, `test_import_guard.py`, then the full suite; regenerate the RTM Test column in the same commit (`NFR-2850`).
5. Update the documentation named below.

## Tests to Add

All marked with the requirement leaf shown (`NFR-3710` by preference, `FR-7230`/`NFR-1600` where the assertion is about the refusal contract). Entries are minimal valid log rows (`seq`, `sim_time`, `kind`, `payload`) of a cheap handler kind, built in memory; no test plays 100,000 events.

1. **Dict shape over the cap is refused.** A self-contained-format save whose `eventlog` is `{"entries": [N+1 rows]}`: `validate_save` raises `ValueError` naming "100001" and "100000"; via the API route: 400 with that detail. (`NFR-3710`, `FR-7230`.)
2. **Dict shape exactly at the cap passes the cap.** Same save with exactly 100,000 rows: `validate_save` does not raise on the count (it may raise on a later check only if the fixture is otherwise invalid; the fixture is made otherwise valid, with `final_time` at or after the last row). If a full load at the cap completes in a few seconds the builder asserts a 200; otherwise the validate-level assertion stands and the choice is recorded. (`NFR-3710`.)
3. **Bare list over the cap is still refused** by the same message; the existing audit test still passes unchanged. (`NFR-3710`.)
4. **Bare list at or under the cap** keeps today's behaviour: refused as malformed (not as oversize). (`NFR-1600`.)
5. **Not-countable logs** (missing key, `None`, a string, a number, an object with no `entries`, an object whose `entries` is not a list): the same errors as today ("missing required key", "malformed"), no new reason, no exception other than `ValueError`. (`NFR-1600`.)
6. **Refusal consumes nothing and is early.** After an over-cap refusal through `InProcessSession.load_save_with_warnings`: the session registry and counter are unchanged, and the next good load returns `sess-1`. A spy on `EventLog.model_validate` shows it was not called for the over-cap save. (`FR-7230`, `NFR-3710`.)
7. **Valid saves unaffected.** A real `save_state` of a started, advanced session (and a legacy-shaped save) loads with the same warnings as before (extend the pattern of `test_valid_saves_still_load_with_same_warnings`). (`FR-7210`.)
8. **Alias.** `InProcessSession.MAX_EVENTLOG_REPLAY_ENTRIES` equals `SessionManager.MAX_EVENTLOG_REPLAY_ENTRIES`, both 100,000. (`NFR-3710`.)
9. **HTTP 400, not 500.** The over-cap dict save through the test client answers 400 (never 500) and the response is JSON with a `detail`. (`NFR-1600`.)

About 9 tests added; the existing audit test's origin is already `NFR-3710`-compatible (the builder checks its current tag; it is not retagged unless it is wrong, and then the `IP-1334` guard row in `test_origin_retag.py` is edited in the same commit).

## Documentation Updates

- `docs/implementation/00-master-build-plan.md`: the `IP-1081` row and tally line (written in this planning pass).
- `docs/implementation/packages/INDEX.md`: the `IP-1081` row.
- `CLAUDE.md` code-map prose for `session/inprocess.py`/`manager.py` is not touched by this planning pass (outside `docs/implementation/`); the builder (`08`) updates any sentence that names where the cap lives, as its documented doc step.
- GDS-07 `OQ5`, `docs/requirements/` and `docs/pipeline/` are not written here; the closing of `OQ5` is for `03` after `VERIFIED`.

## Definition of Done

- An over-cap event log in either shape is refused with a reason, 400 on the route, before model validation and replay, with no session created and no registry change.
- Exactly the cap is accepted by the cap check; a real saved session loads unchanged with the same warnings.
- One refusal path (`validate_save`); the inline check is gone; the constant has one home with a read-through alias.
- Nine new tests green; the audit test unchanged and green; RTM Test column regenerated in the same commit; full suite, `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`, `test_test_origins.py` green; no allow-list grew.

## Verification Checklist

- [ ] Re-derive the defect: on the parent commit a dict-shaped 100,001-entry save is not refused at the cap; on this commit it is, and `EventLog.model_validate` is not reached.
- [ ] Read `validate_save`: the cap is the first use of `state["eventlog"]` after the required-key and type checks, ahead of both `model_validate` calls.
- [ ] Boundary: 100,000 accepted, 100,001 refused, for the object and the list shape.
- [ ] Refusal contract: 400 with reason, JSON detail, no session id consumed, registry unchanged, no 500 for any not-countable shape.
- [ ] Valid and legacy saves load with unchanged warnings.
- [ ] The alias and the old test name still resolve; no other caller depended on the inline check.
- [ ] `FR-4310`: the route still refuses a non-White seat before any of this.
- [ ] Permanent gates and documentation checks green.

## Dependencies

All `VERIFIED`: `IP-1101`, `IP-1102`, `IP-1103`. Independent of `IP-1079` and `IP-1080`; edits `session/manager.py`, `session/inprocess.py` in regions no other open package touches. Adds tests, so build `IP-1079` first if both are in one branch (not required).

## Risks

- **Test cost at the boundary:** a 100,000-row log in memory is a few hundred thousand objects; validate-level tests stay quick, a full replay at the cap may not (Test 2 permits the validate-level assertion).
- **Moving the constant** could break a reader that patches `InProcessSession.MAX_EVENTLOG_REPLAY_ENTRIES` to a small value to test the cap: with a read-through alias that patch would no longer take effect. The builder greps for it (Task 3); if any test patches the alias, either the check reads the alias through `InProcessSession` at the call site or the test is rewritten to patch the manager constant, recorded in the completion note.
- **A pydantic limit on very large payloads** at the HTTP layer is a separate concern (body size), not addressed here.

## Rollback Considerations

Revert the commit. The cap returns to the list-only inline check; saves already written are unaffected (no format change).
