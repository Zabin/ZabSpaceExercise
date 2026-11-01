# IP-1103 — Save Validation Completion: The Remaining Unusable Saves Are Refused Before Replay (FR-7230, NFR-1600)

> **Package ID:** IP-1103
> **Version:** 1.0
> **Status:** VERIFIED 2026-10-24 ([VR-1103](../verification/VR-1103-save-validation-completion.md), fresh session; `COMPLETE` before that) — authored 2026-10-24 by `07-implementation-planning` (release-push remediation pass 2).
> Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive of 2026-10-24,
> recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256, authorizes
> remediation packages for bugs, in-progress and critical items. Authoring is not itself the
> authorization; that recorded decision is.
> **Dependencies:** [FS-110](../../features/FS-110-save-and-resume.md) v2.0 (the spec);
> [IP-1102](IP-1102-save-load-robustness.md) (`VERIFIED`, [VR-1102](../verification/VR-1102-save-load-robustness.md)),
> which this completes.
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0362`, `BL-0363`
> **Produces:** a `validate_save` that refuses every malformed field it can see before replay, two
> tests that pin the legacy-save wording and the server backstop independently, and a completion
> note recording Design Decision 4 of `IP-1102`.
> **Feature Reference:** [FS-110 — Save and Resume](../../features/FS-110-save-and-resume.md)
> **Related Topics:** [VR-1102](../verification/VR-1102-save-load-robustness.md) F-1, F-2, F-3;
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py) (`validate_save`)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package (forward design). Low risk: one validator, one server `except`, tests. It
only turns inputs that are accepted-then-fail-later, or 500, into a 400 with a reason.*

---

## Package ID

IP-1103 (FS-110 → `IP-110x`; `IP-1101` the format, `IP-1102` the first robustness slice, this the
completion).

## Title

Save validation completion: type-check the remaining fields; pin the wording and the backstop.

## Objective

`IP-1102` made the three listed bad-save classes a 400. `VR-1102` F-1 found the same class still
reachable; each row below is a reproduction the verifier ran against `validate_save`
(`session/manager.py`) and `SessionManager.from_state`:

| Input | As built | Required |
|---|---|---|
| `overrides` present and not an object (e.g. a string) | **500** — `from_state` calls `.get` on it | 400 naming `overrides` |
| `pending[i].t` null, a string, a float, or a bool | 200; fails later (or schedules at a nonsense time) | 400 naming `pending` and the field |
| `orders[i]` with junk values (e.g. `cell` not blue/red, `actor`/`action` not strings) | 200; the order is built or fails later | 400 naming `orders` |
| `ssn_requests[i]` with junk values | 200 | 400 naming `ssn_requests` |
| `final_time` negative, or beyond a sane ceiling | 200; the replay is asked to run to it (cost, nonsense clock) | 400 naming `final_time` |
| `classification` present and not a string | 200 | 400 naming `classification` |
| non-object JSON body | 422 from FastAPI | unchanged (acceptable) |

`VR-1102` F-2: two mutations survive: dropping the `FileNotFoundError` re-raise in `validate_save`,
and dropping only the server backstop in `load_save` — each covers the other, and the legacy test
asserts the id but not the "not available" wording. `VR-1102` F-3: `IP-1102` Design Decision 4
(ground sites are assets and are covered; the vignette `sensors` list has no pre-start edit route)
has no completion note.

After this package every row is a 400 with a reason, a refused load still registers nothing, a valid
legacy and a valid self-contained save load exactly as before, and both defences are separately
pinned.

## Feature Reference

[FS-110](../../features/FS-110-save-and-resume.md) v2.0: the load path's rejection of an unusable
save with a reason, and the guarantee that a refused load leaves the session registry untouched.

## Requirements Covered

| ID | How |
|---|---|
| `FR-7230` | Resume refuses a save it cannot honestly replay, precisely, before replay. |
| `NFR-1600` | No input gives a server error; each is a client error naming the problem. |

Both are in `IP-1102`'s Requirements Covered and FS-110's list; none added, none dropped.

## Architecture Components

- **C2 Session Layer** (`session/manager.py::SessionManager.validate_save`): the only logic change.
- **C4 Operator Console / HTTP** (`ui_web/server.py::load_save`): unchanged in behaviour; the existing
  `except (ValueError, FileNotFoundError)` is the backstop the new test exercises.

Engine untouched; determinism and import guard unaffected (validation runs before any replay).

## Interfaces

- **INT-0001** (HTTP) `POST /api/sessions/load_save`: more inputs return 400; response shapes
  unchanged. A valid save's response is byte-identical.
- No new route, field or error code.

### Design Decisions

1. **Validate by building, where a model exists.** `orders` rows are checked by constructing the
   same `Order` model `from_state` builds, and `ssn_requests` rows by constructing `SSNRequest`; a
   construction failure becomes the `ValueError` naming the key and the row index. This keeps the
   validator from drifting from the loader. `pending[].t` is checked for a true integer (not bool),
   `kind` for a non-empty string, `payload` for an object or absent.
2. **`final_time` bounds.** Lower bound: the save's start epoch (the baseline `now` for a
   self-contained save; `ctx.start_epoch` of the loaded vignette for a legacy save) and the time of
   the last event-log entry. Upper bound: the start epoch plus a named ceiling constant for the span
   (one calendar year of sim time is the suggested value; the implementer confirms it exceeds the
   longest vignette horizon and any legitimate saved session by reading how far existing tests and
   vignettes advance, and records the figure). The ceiling exists to stop a replay-cost request, not
   to model the exercise. Do not use `SessionManager.horizon` as the ceiling: a session can advance
   past it.
3. **`overrides` and `classification`.** `overrides` absent/None or an object; `classification`
   absent/None or a string. Anything else is refused.
4. **Wording is pinned, not just status.** The legacy missing-vignette message ("which is not
   available in the content directories") and the key names in each message are contract for the
   console, which shows them verbatim (`IP-1073`).
5. **Both defences stay.** The `validate_save` re-raise and the server `except` are kept (a
   `FileNotFoundError` can still arise from `from_state`'s own load); tests pin each alone.
6. **Completion note (F-3).** The package-level note records `IP-1102` Design Decision 4's outcome:
   ground sites are assets and are covered by the same loop; the vignette `sensors` list has no
   pre-start edit route, so there is nothing to reconcile. Written in `IP-1102`'s completion section
   by the implementer (a notes-only edit; the verified package body is not otherwise changed).

## Files to Create

- None required. New tests go in the existing module below. (If the module would pass about 400
  lines, a sibling `test_save_validation_completion.py` is acceptable.)

## Files to Modify

Checked against the tree at `501b36d`:

- `spacesim/session/manager.py`: `validate_save` (starts line 1027; the `pending`/`orders`/
  `ssn_requests` loop at 1050–1060 and the integer checks at 1041–1043 are extended; the legacy
  `try` at 1062–1069 is unchanged). `from_state` (1085) is not changed.
- `spacesim/tests/test_save_load_robustness.py`: new cases (helpers `_good_state`, `_legacy`,
  `_refused`, `LOAD` exist).
- `docs/implementation/packages/IP-1102-save-load-robustness.md`: completion note only (F-3).

No change to `ui_web/server.py` is planned; if a case cannot be refused in `validate_save` and needs
the server `except` widened, say so in the completion note.

## Implementation Tasks

1. Mark the package `IN PROGRESS` (header, MBP row, `packages/INDEX.md`, `ROADMAP.md`).
2. Write the tests below; see each fail first (the `overrides` string case as a 500, the rest as a
   200).
3. Extend `validate_save` per Design Decisions 1–3.
4. Add the two pinning tests (Decision 4/5) and confirm each fails under its mutation (below).
5. Full suite plus `test_determinism.py`, `test_import_guard.py`, `test_doc_integrity.py`,
   `test_test_origins.py`. Regenerate the RTM Test column (`--origin-report=rtm`).
6. Write the completion note (Decision 6); documentation updates; mark `COMPLETE`.

## Tests to Add

Module marker already `verifies("FR-7230", "NFR-1600")`; each new test inherits it (add
`FR-7220` only where a test pins content behaviour).

1. **Non-mapping `overrides`.** A string, a list and a number each: 400 naming `overrides`, registry
   unchanged. Fails first as a 500.
2. **`pending` rows.** `t` null, `"5"`, `1.5`, `true`: each 400 naming `pending`; `kind` missing or
   empty: 400; a valid row still loads.
3. **`orders` and `ssn_requests` junk.** An order with an unknown `cell`, a non-string `action`, a
   wrong-typed `id`: 400 naming `orders` and the index. Same for an `ssn_requests` row.
4. **`final_time`.** Negative, below the last event time, and above the ceiling: each 400 naming
   `final_time`; a `final_time` equal to the last event time and the saved value both load. A
   boundary pair at the ceiling (just inside loads, just outside refuses).
5. **`classification`.** A number and an object: 400; absent and a string load.
6. **No trace and no regression.** After the whole refused set, `GET /api/sessions` is unchanged;
   a valid self-contained save and a valid legacy save load with the same warnings as before.
7. **Wording pin (F-2).** The legacy missing-vignette 400's `detail` contains "not available in the
   content directories" and the id. Fails if the message text changes.
8. **Backstop pin (F-2).** With `SessionManager.validate_save` replaced by a no-op (monkeypatch),
   a legacy save naming a missing vignette is still a 400 from the server `except`, not a 500.
   Fails under the "drop only the server backstop" mutation.
9. **Re-raise pin (F-2).** Calling `validate_save` directly with that legacy save raises
   `ValueError` (not `FileNotFoundError`). Fails under the "drop the re-raise" mutation.

## Documentation Updates

- `IP-1102` completion note (Decision 6).
- `docs/training/` API reference lists the save-refusal reasons: update only if it enumerates them
  (check `docs/training/` for `load_save`); owner `08-training-manual-authoring` otherwise.
- RTM Test column regenerated, never hand edited; `FS-110` `Referenced By`; MBP row and tally,
  `packages/INDEX.md`, `ROADMAP.md`, this header.

## Definition of Done

- Tests 1–5 and 7–9 exist and were seen failing first (tests 8 and 9 failing under the stated
  mutations); all pass.
- No input in the Objective table returns 500 or is accepted; the non-object body stays 422.
- A refused load registers nothing; valid saves load unchanged.
- Full suite green, both permanent gates green; RTM regenerated.
- `git diff --stat` shows only `manager.py`, tests, and docs.
- Completion note written; status `COMPLETE`.

## Verification Checklist

1. Each Objective-table row, driven through `POST /api/sessions/load_save?cell=white`, returns 400
   with the key named (verifier's own probe, not only the tests).
2. `final_time` ceiling constant is named, documented, and exceeds every shipped vignette's span
   and every save in the existing tests.
3. Mutations in a scratch copy: drop the `overrides` check, the `pending[].t` check, the `final_time`
   check, the re-raise, the server backstop: each fails at least one test.
4. A valid legacy and a valid self-contained save load with the same warnings.
5. `git diff` touches only the files named above.
6. Full suite, `test_determinism.py`, `test_import_guard.py` green; `--origin-report=rtm` unchanged
   after regeneration.

## Dependencies

`IP-1102` (`VERIFIED`). Ordering: build **first** of the three remediation-2 packages. It edits
`manager.py` and `test_save_load_robustness.py` only, disjoint from `IP-1074`'s regions.

## Risks

- **A ceiling that refuses a legitimate save.** Mitigated by Decision 2 (read real spans first, state
  the figure) and verification check 2.
- **Validation drifting from the loader.** Mitigated by Decision 1 (construct the same models).
- **Message wording is user-visible.** The console shows the text verbatim (`IP-1073`); tests pin it.

## Rollback Considerations

Revert the commit. No data format, route or schema change; saves written before and after are the
same.
