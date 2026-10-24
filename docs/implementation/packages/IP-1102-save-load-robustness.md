# IP-1102 — Save Load Robustness: Every Bad Save Is a 400 With a Reason, and the Saved Content Is the Saved Force (FR-7220, FR-7230, NFR-1600)

> **Package ID:** IP-1102
> **Version:** 1.0
> **Status:** 🟢 READY — authored 2026-10-24 by `07-implementation-planning` (release-push remediation pass).
> Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **given.** The owner's release-push directive of 2026-10-24,
> recorded in [`pipeline-journal.md`](../../pipeline/pipeline-journal.md) run #256, authorizes
> remediation packages for bugs, in-progress and critical items. This package covers three open
> bugs. Authoring is not itself the authorization; that recorded decision is.
> **Dependencies:** [FS-110](../../features/FS-110-save-and-resume.md) v2.0 (the spec);
> [IP-1101](IP-1101-self-contained-saves.md) (`VERIFIED`, [VR-1101](../verification/VR-1101-self-contained-saves.md)),
> the package whose behaviour this hardens.
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0326`, `BL-0352`,
> `BL-0359` (F-13)
> **Produces:** a `load_save` that answers every unusable save with HTTP 400 and a reason naming
> the problem, never a 500; and a save whose `content` portion is the force the session actually
> had at save time.
> **Feature Reference:** [FS-110](../../features/FS-110-save-and-resume.md) v2.0 (`FEAT-7200`;
> `FR-7210`, `FR-7220`, `FR-7230`, `NFR-1800`)
> **Related Topics:** [VR-1101](../verification/VR-1101-self-contained-saves.md) F1;
> [integration review of tranche 2](../../reviews/integration-review-tranche-2-white-controls-saves-test-origins.md)
> F-03 and F-13

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation package (forward design) for three defects left by `IP-1101`. Server and session layer
only; the console's handling of a refused load is `IP-1073`.*

---

## Package ID

IP-1102 (FS-110 → `IP-110x`; `IP-1100` and `IP-1101` are taken, so this slice takes the next free
number in the series).

## Title

Save load robustness: three bugs in the self-contained save, found by verification and integration
review.

## Objective

Close three open bugs, each reproduced by the reviewer who filed it:

| Row | Defect (as built at `fca85bf`) | After this package |
|---|---|---|
| `BL-0326` (VR-1101 F1) | A **legacy** save (no `save_format`) whose vignette file is missing: `validate_save` returns early, `from_state` calls `load_vignette(state["vignette_id"])`, and the `FileNotFoundError` is not mapped, so `POST /api/sessions/load_save` returns **500**. | A 400 whose detail names the vignette id the save depends on and says the file is not available. |
| `BL-0359` F-13 (IR F-13) | A save with `save_format` set but `seed`, `eventlog`, `final_time` or `baseline`/`content` missing: `validate_save` checks only `content` and `baseline`, so `from_state` raises `KeyError` on `state["seed"]` and the route returns **500**. The same gap exists for a legacy save missing `vignette_id`, `seed` or `eventlog`, and for a malformed `eventlog`, `pending`, `orders` or `ssn_requests` entry. | A 400 naming the missing or malformed key. Nothing is replayed, no session is registered, no id is consumed. |
| `BL-0352` (IR F-03) | After a **pre-start** edit or delete of a vignette-built asset (the Creator or force edits), `save_state` builds `content` from the unmodified `self.vignette` and appends only assets not in `_built_asset_ids`. Edits and deletes of built assets are therefore absent from `content`, though `baseline` has them. Resume is right (the baseline wins) but the `FR-7220` content portion is not the saved force. | `content`'s force lists equal the force in `baseline`: a deleted built asset is gone, an edited one (including an owner change) appears as edited, and untouched built assets stay exactly as authored. |

**Not changed:** the 400 contract for every refusal `IP-1101` already makes; the legacy-save warning;
resume correctness; the save's key set and `save_format` version (the added content fidelity is a
change of values, not of shape); `FR-4320` (`load_save` is White-only already, `IP-1068`).

## Feature Reference

[FS-110](../../features/FS-110-save-and-resume.md) v2.0: criterion on refusing a malformed save
before replay, the content/session split, and resume without the vignette file. The v2.0 text
treats a save "that cannot be used" as a refusal with a reason; the three rows above are cases it
left as a 500.

## Requirements Covered

| ID | How |
|---|---|
| `FR-7220` | `BL-0352`: the content portion is the saved force, edits and deletes included. |
| `FR-7230` | `BL-0326` / F-13: an unusable save (missing vignette file for a legacy save, missing keys) is refused with a reason, and a self-contained save still resumes without its vignette file. |
| `NFR-1600` | None of the three cases crashes; each is a client error. |

All are in FS-110 v2.0's Requirements Implemented list or its `NFR-1600` cross-reference through
`IP-1101`; none added, none dropped. (`FR-7210`, `NFR-1800` are untouched but their existing tests
must stay green.)

## Architecture Components

- **C2 Session Layer** (`session/manager.py`: `validate_save`, `save_state`, `__init__`'s
  `_built_asset_ids`; `session/inprocess.py`: `load_save_with_warnings`, unchanged unless the
  ordering of checks needs it).
- **C4 Web layer** (`ui_web/server.py::load_save`): maps `FileNotFoundError` defensively as a
  second line, so no future unmapped loader error becomes a 500 on this route.

The engine is untouched; the import guard and determinism gate are unaffected. A save's replay is
byte-identical to before for every save that resumed before.

## Interfaces

- **INT-0001** (HTTP) `POST /api/sessions/load_save`: three more inputs now give 400 (response shape
  `{detail}` unchanged). The 200 shape `{session, warnings}` is unchanged.
- `GET /api/sessions/{sid}/save`: same keys; `content`'s force lists change value in the
  pre-start-edit case only.

### Design Decisions

1. **Required-key validation lives in `validate_save`, before replay.** It runs for both formats.
   Self-contained: `content`, `baseline`, `seed`, `eventlog`, `final_time`. Legacy: `vignette_id`,
   `seed`, `eventlog`, `final_time`. A missing key, a wrong type (seed and final_time must be
   integers, eventlog a mapping that `EventLog.model_validate` accepts, `pending`/`orders`/
   `ssn_requests` lists of mappings when present) raises `ValueError` naming the key. The existing
   eventlog-length bound in `load_save_with_warnings` stays first.
2. **Legacy availability is checked in `validate_save`, not by catching late.** For a legacy save it
   calls `load_vignette(vignette_id)` in a try block and re-raises `FileNotFoundError` as
   `ValueError("the save depends on vignette '<id>', which is not available in the content
   directories")`. A `VignetteValidationError` is already a `ValueError` and passes through. The
   server's `except ValueError` then yields the 400. The server route additionally catches
   `FileNotFoundError` as a backstop.
3. **Content fidelity by comparison, not regeneration.** At construction (next to
   `_built_asset_ids`) the manager records each built asset's dumped form. `save_state` then, for
   every built asset id: absent from the baseline means drop its entry from the owner's content
   list; present and unequal to the recorded dump means replace its entry with the baseline form
   (the same `{k: v for k, v in adict.items() if k != "owner"}` shape the appended assets already
   use, moved to the new owner's list if the owner changed); present and equal means leave the
   authored entry verbatim. Verbatim-when-untouched keeps content-as-data fidelity (authored YAML
   shape, templates and aliases survive), which is why the content is not simply rebuilt from the
   baseline wholesale.
4. **Scope of "force".** The defect row names assets. The implementer checks, by reading
   `_built_asset_ids`'s neighbours and the force-edit paths, whether ground sites and sensors can be
   edited or deleted before start the same way; if they can, the same rule applies to them and the
   test list gains one case each. If they cannot, say so in the package's completion note.
5. **Determinism and safety.** No engine, RNG or clock change. Validation is pure and runs before
   any `SessionManager` is built, so a refusal consumes no session id and registers nothing.

## Files to Create

- `spacesim/tests/test_save_load_robustness.py`.

## Files to Modify

Checked against the tree at `fca85bf`:

- `spacesim/session/manager.py`: `validate_save` (line ~1007; gains the key and type checks and the
  legacy availability check), `save_state` (line ~971; the content-building loop at lines ~982–987),
  `__init__` near line 155 (record built-asset dumps beside `_built_asset_ids`).
- `spacesim/ui_web/server.py`: `load_save` route (line ~1031): add `FileNotFoundError` to the caught
  errors as a backstop (a 400, not a 500).
- Existing tests that assert a specific refusal message may need their expected text widened;
  `spacesim/tests/test_self_contained_save.py` is the likely one. Do not weaken any assertion.

No other production file changes. `session/inprocess.py::load_save_with_warnings` is expected to
need no change (it already calls `validate_save` before `from_state`); confirm.

## Implementation Tasks

1. Mark the package `IN PROGRESS` (header, MBP row, `packages/INDEX.md`, `ROADMAP.md`) before editing.
2. Write the tests below; run them and see tests 1–6 fail for the stated reason (500 or wrong
   content) before changing production code. Tests 7–9 should already pass.
3. Implement Design Decisions 1–2 (validation), then 3–4 (content fidelity).
4. Run the full suite, `test_determinism.py` and `test_import_guard.py`. Fix only defects this
   package introduced.
5. Documentation updates, then mark `COMPLETE`.

## Tests to Add

`spacesim/tests/test_save_load_robustness.py`, module marker
`@pytest.mark.verifies("FR-7230", "NFR-1600")`; per-test overrides named below. HTTP tests use
`TestClient(create_app(), raise_server_exceptions=False)` with `?cell=white`. Vignette-file
fixtures use a temporary external content directory (the pattern in `test_self_contained_save.py`),
never a shipped file.

1. **Legacy save, vignette file gone → 400.** Build a legacy-shaped save (drop `save_format`,
   `content`, `baseline`) whose `vignette_id` names no file: status 400, detail contains the id.
   Before the change: 500.
2. **Self-contained save missing `seed` → 400 naming `seed`.** Same for `eventlog` and
   `final_time` (parametrized). Before: 500.
3. **Legacy save missing `vignette_id`, `seed` or `eventlog` → 400** naming the key (parametrized).
4. **Malformed optional parts → 400.** `pending` not a list, an `orders` entry that is not a mapping
   or lacks required fields, `eventlog` not a mapping: each 400 with the key named.
5. **A refused load leaves no trace.** After each refusal in tests 1–4, `GET /api/sessions` lists
   the same sessions as before and the next accepted load receives the next unused id.
6. **Content equals the saved force (`FR-7220`, override marker).** On a not-yet-started session:
   delete one vignette-built asset, change another's owner, add one by TLE. `save_state()["content"]`
   contains no entry for the deleted asset, the changed one under its new owner's list, the added
   one, and the untouched built assets with entries byte-identical to `Vignette.model_dump` of the
   loaded vignette. Before: deleted and changed assets still show their original form.
7. **Resume is unchanged.** A round trip of the test-6 save yields a world equal to the pre-save
   world, and `from_state` from the `content` portion alone (baseline replaced by one built from
   content) builds the same asset id set. (`FR-7210`, override marker.)
8. **No regression on valid saves.** One valid legacy save and one valid self-contained save, with
   an inject pending and an order queued, load 200 with the same warnings as before.
9. **Untouched session: content is the authored vignette.** `save_state()["content"]` equals
   `Vignette.model_dump(mode="json")` exactly when nothing was edited (`FR-7220`).

If Design Decision 4 finds ground sites or sensors editable pre-start, add the analogue of test 6
for each.

## Documentation Updates

- `docs/requirements/03-requirements-traceability-matrix.md`: the Test and Implementation Package
  cells for `FR-7220` and `FR-7230` gain this file / `IP-1102` (the Test column is generated:
  `python3 -m pytest --origin-report=rtm`, same commit).
- `docs/features/FS-110-save-and-resume.md`: `Referenced By` only.
- `docs/training/08-http-api-reference.md` and `docs/training/10-ui-reference.md` §10.1.3: state the
  load refusal contract (400 with a reason, including a legacy save whose vignette file is missing).
  Manual upkeep goes through the traceability matrix `docs/training/15-manual-traceability.md` §15.1
  rows for those sections; if the `IP-1101` manual pass already added the 400 contract, note that and
  add only the new cases. Route any prose that needs authoring to `08-training-manual-authoring`.
- MBP row and tally, `packages/INDEX.md`, `ROADMAP.md`, this header.
- `CLAUDE.md`: the session-layer `SessionManager` bullet's `IP-1101` clause gains one clause for the
  required-key validation and the content-fidelity rule.

## Definition of Done

- All Tests to Add exist and pass; tests 1, 2, 6 were seen failing first.
- No `load_save` input in the Objective table returns 500; each returns 400 with the stated reason.
- `save_state()["content"]` equals the saved force after pre-start edits and deletes.
- Full suite green with no previously passing test now failing; `test_determinism.py` and
  `test_import_guard.py` green.
- `git diff --stat` touches only `session/manager.py`, `ui_web/server.py`, tests, and docs.
- Documentation updates done; status `COMPLETE`.

## Verification Checklist

1. `validate_save` checks the required keys and types for both formats and the legacy vignette
   availability, before any replay (read the code; no `from_state` call precedes it).
2. Reproduce independently: a legacy save naming a missing vignette gives 400, not 500.
3. Reproduce independently: delete a built asset pre-start, save, and read `content`: the asset is
   absent; resume still produces the post-delete world.
4. `GET /api/sessions` is unchanged by a refused load.
5. A valid legacy and a valid self-contained save still load with the same warnings.
6. Full suite and both permanent gates (`test_determinism.py`, `test_import_guard.py`) green.
7. Every new test carries a `verifies` marker naming a live baseline ID; the RTM Test column was
   regenerated, not hand edited.

## Dependencies

`IP-1101` (`VERIFIED`). `IP-1068` (`VERIFIED`) governs the route's White-only check, untouched.
Ordering: land before `IP-1073`, whose browser test of a refused load uses these real refusals.
`IP-1311` edits `content/vignette.py`, no overlap. `IP-1072` edits other routes in `server.py`;
build serially (see the Master Build Plan note) to avoid a merge conflict in that file.

## Risks

- **Over-eager content replacement.** If the equality test between recorded and baseline forms is
  too strict (a field reordering, a default filled in on dump), untouched assets would be rewritten
  and the "verbatim when untouched" property (test 9) would fail. Test 9 is the guard; compare
  parsed dicts, not strings.
- **Owner change across buckets.** The three buckets are `blue_forces`, `red_forces`,
  `neutral_forces`; an asset moved to a bucket that does not exist must not crash. The existing
  append code has the same shape; reuse it.
- **A message text another test pins.** Widening an expected message is acceptable; weakening an
  assertion is not.

## Rollback Considerations

Revert the commit. No format version change and no persisted-state change: saves written by this
code load under the old code (the content values differ only after pre-start edits), and saves
written before load under this code.
