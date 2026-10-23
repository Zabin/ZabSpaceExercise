# IP-1101 — Self-Contained Saves (FR-7230, FR-7220, FR-7210 force-edit fix)

> **Package ID:** IP-1101
> **Version:** 1.0
> **Status:** 🟢 READY — authored 2026-10-23 by `07-implementation-planning`, pipeline run #220.
> Every dependency is `VERIFIED`.
> **Authorization (MSTR-006 §3):** **not yet given for this package.** The owner decided the
> behavior (`BL-0302`); the build go-ahead is a separate decision, asked before `08` runs.
> **Dependencies:** [FS-110](../../features/FS-110-save-and-resume.md) v2.0 (the spec);
> [IP-1100](IP-1100-save-and-resume.md) (save/resume as built), [IP-1310](IP-1310-load-time-vignette-validation.md)
> (`validate_vignette`), [IP-1200](IP-1200-save-as-scenario.md) (`simulator_version()`) — all `VERIFIED`.
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](INDEX.md), [`backlog.md`](../../pipeline/backlog.md) `BL-0302`, `BL-0315`
> **Produces:** a save that resumes from its own contents, carries an extractable content portion,
> keeps White Cell force edits, and records its format and simulator versions.
> **Feature Reference:** [FS-110](../../features/FS-110-save-and-resume.md) v2.0 (`FEAT-7200`)
> **Related Topics:** [IP-1068](IP-1068-white-only-controls-server-enforcement.md) (also edits the
> `load_save` route — independent, but merge carefully); GDS-07 §6 (updated by `03` after this
> package is verified)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Remediation and forward design.*

---

## Package ID

IP-1101.

## Objective

**As built at `79930d2`**, `SessionManager.save_state` (`session/manager.py` line 964) writes
`vignette_id`, `overrides`, `classification`, `seed`, `final_time`, `started`, `eventlog`,
`pending`, `orders`, `ssn_requests`; `SessionManager.from_state` (line 985) reloads the vignette
**by ID** (`load_vignette`), rebuilds the world from it, and replays the event log. Three defects
follow (FS-110 v2.0):

1. An edited, renamed or deleted vignette file changes or prevents resume (`FR-7230`).
2. The save holds no content, so its content portion cannot be extracted (`FR-7220`, recorded
   verified, not met).
3. White Cell force edits (`add_tle` line 482, `bulk_import`, `add_ground_asset` line 600 — each
   re-baselines `sim._initial_state` and refuses after start) are in neither the save nor the event
   log, so resume drops them (`FR-7210`, `BL-0315`; reproduced 2026-10-23).

After this package a save also carries:

| New content | What it is | Serves |
|---|---|---|
| **Content portion** | The vignette **as originally loaded**, verbatim (`self.vignette`), with every force-added asset appended to its owner's force list, in the vignette file format | `FR-7220` (extractable, parameters as originally loaded), FS-110 Decision 1 |
| **Replay baseline** | The serialized starting world the event log replays from (`sim._initial_state`) | `FR-7210`, `FR-7230`: exact resume by construction |
| **Format version** and **simulator version** | A save-format marker and `spacesim.version.simulator_version()` | FS-110 Decision 3 |

## Design Decisions

1. **Resume uses the replay baseline, not a rebuild** (FS-110 Open Question 4, decided here). The
   world-to-vignette exporter (`content/vignette_export.py::export_vignette`) drops injects,
   briefs, tutorials, coaching, parameters and gating rules, so rebuilding from an exported vignette
   cannot be exact. The save therefore carries the baseline world itself; resume installs it as the
   simulation's initial state, builds the vignette context (objectives, injects, ROE, gating) from
   the content portion with the saved overrides, and replays the event log. Exactness no longer
   depends on any conversion.
2. **The content portion is the original vignette plus force-added assets** — not an export of the
   current world — because `FR-7220` asks for parameters "as originally loaded". Force-added assets
   are those in the baseline whose IDs are not in the loaded vignette's forces; they are appended to
   the matching `blue_forces`/`red_forces`/`neutral_forces` list in the same dump form the exporter
   uses. (Live sessions cannot delete or edit vignette assets; the Creator's draft edits are not
   saved through this path.)
3. **Legacy saves** (no format version) take today's path unchanged: reload by ID. The response
   tells the caller the save depended on its vignette file.
4. **Warnings travel in the load response**, not the world: `load_save` returns
   `{"session": …, "warnings": [...]}`. Writing a message into `WorldState` at resume would make the
   resumed world differ from the saved one. The console shows the warnings to the White Cell.
5. **Validation.** The content portion is checked with `validate_vignette` (`content/vignette.py`
   line 388) and the baseline with the `WorldState` model's own validation, before any replay; a
   failure refuses the load with the problems listed and creates no session.

## Requirements Covered

FR-7210, FR-7220, FR-7230, NFR-1800 — FS-110 v2.0's Requirements Implemented.

## Architecture Components

C2 Session/Application Layer (`session/manager.py`, `session/inprocess.py`), C5 Content & Data
(`content/vignette.py`, read only — the format owner per ADR-0022), C4 Operator Console
(`ui_web/server.py` response, `static/app.js` warning display). No engine change.

## Interfaces

INT-0012 (save round trip): the save body gains four keys; every existing key is kept.
INT-0011 (vignette load): resume and extraction both use the existing loader and validator.
INT-0002: `POST /api/sessions/load_save` returns `warnings` alongside `session`.

## Files to Create/Modify

- **Modify** `spacesim/session/manager.py` — `save_state` adds the content portion, the replay
  baseline, the format version and the simulator version; `from_state` branches on the format
  version: new saves build from the content portion and install the baseline, legacy saves keep
  today's code path; return or expose the warnings list (Design Decision 4).
- **Modify** `spacesim/session/inprocess.py` — `load_save` (line 1053) validates the content
  portion and baseline before constructing the manager (after the existing event-log bound), and
  returns the warnings with the session ID.
- **Modify** `spacesim/ui_web/server.py` — `load_save` route returns `warnings`.
- **Modify** `spacesim/ui_web/static/app.js` — `loadSaveFile` (line 1861) shows any warnings to
  the user (a visible message; no new panel).
- **Create** `spacesim/tests/test_self_contained_save.py`.
- **Modify** `spacesim/tests/test_session_features.py` / `test_web.py` only if an existing test
  asserts the exact key set of a save (re-check; no assertion about behavior may change).
- **Docs:** `CLAUDE.md` code map (`session/` save/resume line); RTM rows `FR-7210`, `FR-7220`,
  `FR-7230`, `NFR-1800`; `docs/training/12-white-cell-manual.md` save/resume section (per
  `training/15` §15.1) if it says a save needs its vignette file.

## Implementation Tasks

1. Baseline suite run.
2. Write the tests below first; record which fail (expected: everything except the legacy-path and
   immediate-resume tests).
3. Implement `save_state` additions (Design Decisions 1–2).
4. Implement `from_state`'s new-format branch and legacy branch (Design Decisions 1, 3).
5. Implement validation in `load_save` and the warnings (Decisions 4–5); route and client display.
6. Full suite, both gates; docs.

## Tests to Add

In `spacesim/tests/test_self_contained_save.py`. Every test that edits or deletes a vignette file
copies a shipped vignette into a temporary external content directory first (`content:`
configuration, IP-1180) — never touch a shipped file.

| Test | Verifies (marker IDs) | Asserts |
|---|---|---|
| Immediate round trip, every shipped vignette (parametrized) | `FR-7210` | resumed world dump equals pre-save world dump at T |
| Resume after the vignette file is edited | `FR-7230` | resumed state equals saved state, not the edited file's |
| Resume after the file is deleted, and after it is renamed | `FR-7230` | resume succeeds; state equals saved state |
| Force-added TLE and ground assets survive (saved before start; and after start + advance) | `FR-7210` | both assets present with identical state after resume (`BL-0315`) |
| Content portion extracts and loads as a fresh vignette | `FR-7220` | it passes `validate_vignette`, starts a session, contains the force-added assets, and carries the original parameter declarations |
| Content portion's starting world matches the baseline for every shipped vignette with no force edits | `FR-7220` | building it with the saved overrides gives the same world as the saved baseline (fidelity of the content portion) |
| Invalid content portion refused | `FR-7230`, `NFR-1800` | load refused with the problems listed; session count unchanged |
| Legacy save (format version removed) | `FR-7210` | resumes by ID as before; warnings say it depended on the vignette file |
| Simulator-version mismatch | `FR-7230` | resumes; warnings name both versions |
| Resume in a fresh `InProcessSession` (new process stand-in) | `NFR-1800` | state equals saved state |

## Documentation Updates

RTM rows (Test and Package cells; `FR-7220`'s "not met" note is `04`'s to retire after `09`);
`CLAUDE.md` code map; the White Cell manual's save section if it needs it. GDS-07 §6 is `03`'s and
is updated after verification (`BL-0311` follow-on, recorded in GDS-07 v1.1).

## Definition of Done

1. A new save resumes identically whether its vignette file is unchanged, edited, renamed or
   deleted.
2. Force-added assets survive save and resume.
3. The content portion extracts, validates and starts a session, with parameters as originally
   loaded.
4. Legacy saves resume as before, with a warning; version mismatch warns.
5. An invalid content portion is refused before replay with no session created.
6. All tests above exist, tagged, with the failing-first run recorded; no existing assertion changed.
7. Full suite and both permanent gates green; docs updated.

## Verification Checklist

- [ ] Each Tests to Add row exists and passes; the edit/delete/rename tests use a temporary
      directory (read them).
- [ ] Reverting `from_state` to reload by ID makes the `FR-7230` tests fail (demonstrate once).
- [ ] `save_state` output keeps every pre-existing key.
- [ ] `git diff` touches only the files listed.
- [ ] Full suite counts recorded; `test_determinism.py` and `test_import_guard.py` green by name.
- [ ] Every new test carries a `verifies` marker with the IDs shown.

## Dependencies

`IP-1100`, `IP-1310`, `IP-1200` — all `VERIFIED`. No package depends on this one.

## Risks

- **Save size.** The baseline and content portion add roughly one vignette and one world to each
  save; acceptable (no NFR sets a limit), but note the size in the completion summary.
- **Legacy saves in the wild** keep the vignette-file dependence; only new saves are
  self-contained (FS-110 Decision 3).
- **Fidelity test failure.** If the "content portion's starting world matches the baseline" test
  fails for some vignette, resume is still exact (Decision 1), but extraction is not faithful for
  that vignette: stop and report it to `06`/`04` rather than weakening the test.
- **Concurrent edit with IP-1068** on the `load_save` route signature; whichever lands second merges.

## Rollback Considerations

Revert the commit. Saves written by the new code still carry every legacy key, so the old code
resumes them by ID (ignoring the new keys) — a rollback does not strand any save whose vignette file
still exists.
