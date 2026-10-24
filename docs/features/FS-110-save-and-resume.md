# FS-110 — Save & Resume

> **Document ID:** FS-110
> **Version:** 2.0
> **Status:** ✅ Ready for implementation planning (v2.0 additions); v1.0 scope ✅ Done
> **Dependencies:** [ADR-0022](../architecture/adr/ADR-0022-save-file-ownership-split.md), [GDS-07](../architecture/07-data-model.md) §6, [DOM-003](../domains/DOM-003-white-cell-framework.md) §6
> **Referenced By:** [IP-1102](../implementation/packages/IP-1102-save-load-robustness.md), [FS-106](FS-106-white-cell-dashboard.md) (the White-only save/resume trigger surface this mechanism serves), [docs/feature-planning/03-feature-catalog.md](../feature-planning/03-feature-catalog.md) `FEAT-7200`
> **Produces:** the persisted session artifact [FS-107](FS-107-after-action-review.md)'s AAR replay reads from
> **Implementation:** [IP-1100](../implementation/packages/IP-1100-save-and-resume.md) (v1.0, ✅ VERIFIED); [IP-1101](../implementation/packages/IP-1101-self-contained-saves.md) (v2.0, 🟢 READY 2026-10-23)
> **Feature Mapping:** FS-110 (this document) → `FEAT-7200`
> **Related Topics:** [FS-106](FS-106-white-cell-dashboard.md) (facilitator-facing save/resume trigger), [FS-107](FS-107-after-action-review.md) (AAR replay over a saved/resumed event log), [FS-120](FS-120-save-as-scenario.md) (save the *current* state as a new vignette — a different capability, see Scope), [FS-131](FS-131-load-time-vignette-validation.md) (the load-time validation a resumed save's content must pass)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template. v1.0 was split
out of `FS-106-white-cell-dashboard.md` v1.0 per `docs/feature-planning/05-feature-review.md`
Finding F-03.*

> **v2.0 (2026-10-23, pipeline run #213).** Adds `FR-7230` (a save resumes using only what it
> contains — owner decision `BL-0302`: "Save the active state in the scenario regardless of
> original vignette file") and specifies how the same change makes `FR-7220` true, which was
> recorded verified but is not met as built (requirements review R2; feature review F-24). It also
> covers a defect found while specifying (Open Question 1 below): **a White Cell force edit made
> during a session is lost on resume.** `NFR-1800` is restated to its corrected text (save and
> resume across processes). It resolves GDS-07 OQ1 (by the owner decision) and decides OQ2 and OQ3
> as `FR-7230`'s Notes delegate to this specification (Design Decisions below). Changes are marked
> *(v2.0)*; unmarked text is v1.0 and is built.

## Feature ID

FS-110

## Title

Save & Resume

## Purpose

Persist a complete session snapshot on demand or at exercise end and reproduce it exactly when
resumed, with the save file's Vignette/content portion independently extractable from its
Session/event-log portion — per `docs/feature-planning/03-feature-catalog.md` `FEAT-7200`'s own
Purpose field. *(v2.0)* The save is self-contained: resuming it needs nothing outside the file.

## Scope

In scope: the deterministic save/resume round trip (`WorldState`, full `EventLog`, Snapshots, Role
Assignments); the save file's content/session ownership split (independent re-extractability of the
Vignette/content portion apart from the Session/event-log portion); *(v2.0)* a self-contained save
that resumes identically whether the vignette file it was loaded from is unchanged, edited, renamed
or deleted; and the version information a save carries so that a save written before v2.0 can be
told apart from one written after.

Out of scope: *who* is authorized to trigger a save/resume request ([FS-106](FS-106-white-cell-dashboard.md)'s
facilitator-facing panel, and the White-only enforcement remediation `BL-0307`);
cross-build/cross-version save-file compatibility (`CR-08`, a candidate, not baselined — same-build
round trips only); AAR replay/scrub over a resumed session's event log ([FS-107](FS-107-after-action-review.md));
saving the session's **current** state as a new starting vignette ([FS-120](FS-120-save-as-scenario.md),
`FR-5510` — the content portion here is the session's **starting** conditions, not its current
state); crash recovery (`NFR-1800`: none is claimed).

## Requirements Implemented

FR-7210 (deterministic save-file round trip), FR-7220 (save-file content/session ownership split),
*(v2.0)* FR-7230 (resume independent of the original vignette file), NFR-1800 (one sitting per
session; save and resume across processes) — per `docs/feature-planning/03-feature-catalog.md`
`FEAT-7200`'s `Included Requirements`.

## Design Decisions *(v2.0)*

These settle the questions `FR-7230`'s Notes and GDS-07 §6 leave to this specification. Each is a
behavior commitment; how it is serialized is `07`'s choice within ADR-0022 (Content & Data owns the
on-disk format).

1. **The content portion is the session's replay baseline, in vignette form.** A save carries the
   starting conditions the event log replays from: the loaded vignette's content (force lay-down,
   ground sites, sensors, objectives, injects, briefs, tutorial and coaching blocks, ROE and gating
   rules) as originally loaded, **plus every White Cell force edit folded into the baseline since
   load**, plus the parameter overrides. This is GDS-07 OQ1's "embed the vignette" option, chosen
   by the owner (`BL-0302`). It is the starting state, not a snapshot of the current world — the
   event log carries everything after. Because it is in vignette form, it is also `FR-7220`'s
   extractable content portion: one content portion serves both requirements.
2. **Resume reads only the save.** A save that carries a content portion is resumed from it; the
   vignette library is not consulted, and the vignette ID in the save is kept as a label only (for
   display and AAR provenance).
3. **Legacy saves keep today's behavior** (GDS-07 OQ2, decided here). A save carries a save-format
   version and the simulator version (`spacesim.version.simulator_version()`, the same value
   exported vignettes already carry under `FR-5510`). A save with no format version is a pre-v2.0
   save: it is resumed as today, by reloading the vignette by ID, and the resumed session tells the
   White Cell that the save depended on the vignette file. `FR-7230`'s Preconditions limit the
   requirement to saves produced after it is implemented, so this is consistent with it. A
   simulator-version mismatch is reported to the White Cell as a warning, never a refusal — refusing
   would be a cross-version compatibility rule, which `CR-08` leaves unbaselined.
4. **The engine-level save shape is left alone** (GDS-07 OQ3, decided here). `engine/simulation.py::
   SavedSession` serves only the determinism test and already carries its own initial state;
   converging the two shapes is not needed by any requirement this Feature owns.

## User Workflows

- A facilitator (via [FS-106](FS-106-white-cell-dashboard.md)'s panel) or another authorized caller
  requests a save of the current or completed session; a save file is written to disk.
- A later session load — in the same or a new server process (`NFR-1800`) — reads that save file
  and reconstructs a `WorldState` identical to the state at the moment of save.
- *(v2.0)* Between the save and the load, the vignette file the session was loaded from may be
  edited, renamed or deleted (by a content author, or by updating the library); the load still
  reconstructs the saved state exactly.
- *(v2.0)* During a session the White Cell force-adds or edits assets (TLE add, ground asset add,
  and the other force edits); the session is saved and later resumed; the force-edited assets are
  present in the resumed session exactly as before the save.
- A content author or facilitator extracts a save file's Vignette/content portion and loads it as a
  fresh vignette's starting state, independent of that save's own Session/event-log history.

## System Behaviour

- **A save persists a complete session snapshot** (FR-7210): `WorldState` (as its replay baseline
  plus the event log that reproduces it), the full `EventLog`, Snapshots, Role Assignments, pending
  scheduled events, and the order and SSN request registries, taken on demand or at exercise end.
- **A resume reproduces the exact saved state** (FR-7210): the resumed `WorldState` is identical,
  field-for-field, to the state at the moment of save, and the resumed session continues exactly as
  the saved one would have (same pending events, registries and ID counters).
- *(v2.0)* **A save is self-contained** (FR-7230): resume uses only the save's content portion and
  session portion. Edge cases: the original vignette file edited after the save → the resumed
  state is the saved state, not one rebuilt from the edited file; the file renamed or deleted → the
  resume succeeds; a different vignette now holds the same ID → it is not consulted.
- *(v2.0)* **Force edits survive the round trip** (FR-7210): every edit the White Cell made to the
  force lay-down before the save — whether before or after the exercise started — is part of the
  content portion's baseline, so the resumed world contains it. (As built, these edits re-baseline
  the in-memory replay baseline but are written to neither the save nor the event log; Open
  Question 1.)
- **The save file's content and session portions are structurally distinguishable and
  independently re-importable** (FR-7220): the content portion can be extracted and loaded as a new
  session's starting vignette without that save's Session/event-log history; the two portions are
  never merged into an undifferentiated blob. *(v2.0)* The content portion is in the same format as
  an authored vignette file (ADR-0022: Content & Data owns both formats), so the extracted portion
  goes through the same load path and the same load-time validation as any vignette (FS-131).
- *(v2.0)* **Resuming validates the content portion as untrusted input.** A save arriving through
  `load_save` is content from outside the process; its content portion passes the same load-time
  validation a vignette file does (`FR-5310`–`FR-5314`, FS-131) before any replay, and the existing
  event-log length bound (`NFR-3710`, 100,000 entries) still applies before any replay.
- *(v2.0)* **Version information is reported, not enforced.** A pre-v2.0 save resumes by vignette
  ID with a White Cell notice that it depended on the vignette file (Design Decision 3); a save from
  a different simulator version resumes with a White Cell warning naming both versions.
- **Availability** (NFR-1800, corrected text): an exercise runs as one session in a server process
  for one sitting; one process may host several sessions up to the live-session cap; a session is
  resumable in a new process from a save taken mid-exercise. There is no automatic crash recovery —
  a session not saved before its process stops is lost. *(v2.0: replaces v1.0's "no mid-exercise
  save/resume across process restarts", which GDS-06 correction C1 found wrong; GDS-05 OQ2 is
  resolved by that correction.)*

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `session/manager.py` (`SessionManager`) | Owns the save/resume operation itself (ADR-0022, the *act* of saving): produces the save from the live session — *(v2.0)* including the content portion built from its current replay baseline and the version fields — and, on resume, reconstructs identical state from the save alone. |
| `session/inprocess.py` (`InProcessSession`) | Holds the save/load entry points under the session lock; enforces the event-log length bound and the live-session cap (`NFR-3710`) before any replay. *(v2.0)* Refuses a load whose content portion fails validation, leaving the session registry untouched (the FS-131 pattern). |
| Content & Data (`content/vignette.py`, `content/vignette_export.py`) | Owns the on-disk format of both portions (ADR-0022). *(v2.0)* Converts a replay baseline into vignette form (the existing world-to-vignette conversion `FR-5110`/`FR-5510` use) and back (the existing loader and world builder), and validates the content portion on load (FS-131). |
| `version.py` | *(v2.0)* Supplies the simulator version a save records (unchanged, already used by `FR-5510`). |
| `session/aar.py` | Consumes a resumed session's `EventLog` for replay (FS-107) — a downstream consumer, not a dependency. |

## Interfaces Used

INT-0011 (Session Layer → Content & Data, vignette/template load) — the content-portion load path,
used both for extraction (`FR-7220`) and, *(v2.0)*, for resume itself. INT-0012 (Session Layer →
Content & Data/Filesystem, save round trip) — the save/resume round trip. *(v2.0)* The HTTP routes
that carry a save in and out (`GET /api/sessions/{sid}/save`, `POST /api/sessions/load_save`,
GDS-09) keep their paths; only the body they carry grows.

## Data Model Changes

*(v2.0)* The save envelope (GDS-07 §6) gains:

- a **content portion** in vignette form, holding the replay baseline described in Design
  Decision 1 (it supersedes reloading by `vignette_id`, which stays as a label);
- a **save-format version** and the **simulator version** (Design Decision 3).

Every existing envelope key (`vignette_id`, `overrides`, `classification`, `seed`, `final_time`,
`started`, `eventlog`, `pending`, `orders`, `ssn_requests`) is kept, so the session portion is
unchanged. No Domain Model entity changes: the content portion is an existing entity (the Vignette,
GDS-04) inside an existing one (the Session's persistent state, GDS-04 §1.14). GDS-07 §6 must be
updated to match when this is built (Open Question 3).

## State Changes

- A save request transitions no live session state — it is a read-and-persist operation against the
  current state.
- A resume request reconstructs a full `WorldState`/`EventLog`/Snapshot/Role-Assignment set, plus
  pending events and registries, into a new session, identical to the state at save time.
- *(v2.0)* A refused resume (invalid content portion, over-limit event log) creates no session and
  leaves the session registry unchanged.

## Error Handling

- *(v2.0)* **Content portion fails validation** → the load is refused with the validation problems
  listed (the same problem list FS-131 produces for a vignette file); no session is created.
- **Event log over the bound** (`NFR-3710`) → refused before any replay (built).
- *(v2.0)* **Pre-v2.0 save whose vignette ID no longer resolves** → refused with an error naming
  the missing vignette and stating that the save predates self-contained saves. This is the only
  case in which a missing vignette file can stop a resume.
- *(v2.0)* **Simulator version differs** → resumed, with a White Cell warning (Design Decision 3).
- Cross-build/cross-version compatibility beyond that warning is out of scope (`CR-08`).
- A save whose session portion is malformed in some other way (missing keys, wrong types) is not
  enumerated by the requirements baseline; Open Question 2.

## Performance Considerations

- `NFR-3710`: the event-log bound and live-session cap are checked before any replay (built,
  unchanged).
- *(v2.0)* The content portion adds the size of one vignette to each save — small relative to the
  event log for any realistic session. No NFR sets a save-size target; none is invented here.
- Determinism (`NFR-1500`): resume replays from the content portion's baseline with the saved seed;
  the round trip must be exact, which is what the acceptance criteria test.

## Security Considerations

- Per the LAN trust model, `/save` is one of the documented no-cell, ground-truth-exposing endpoints
  (ADR-0015, `FR-6220`): the save contains ground truth, not a fog-of-war-filtered view. *(v2.0)*
  Embedding the content portion adds no new exposure: everything in it was already reachable
  through the same save's replay.
- *(v2.0)* A loaded save is untrusted input: its content portion is validated (FS-131) and its event
  log bounded (`NFR-3710`) before any replay. Embedding content removes the path through which a
  save named a vignette to load; no file path is read from a save.
- White-only enforcement of save and load is `FR-4320` (`BL-0307`), not this Feature.

## Acceptance Criteria

1. A session saved at sim time T and immediately resumed produces a `WorldState` identical to the
   pre-save state at T. *(Built.)*
2. A save file's Vignette/content portion, extracted and loaded independently, produces a valid
   fresh vignette starting state with no dependency on that save's own event-log history.
   *(v2.0: the content portion is the replay baseline in vignette form; the extracted portion passes
   load-time validation and starts a session.)*
3. *(v2.0, FR-7230)* Save a session at sim time T; **edit** the vignette file it was loaded from (for
   example, move an asset); resuming the save reproduces the state at T exactly.
4. *(v2.0, FR-7230)* Save a session at sim time T; **delete** (and, separately, rename) the vignette
   file; resuming the save succeeds and reproduces the state at T exactly.
5. *(v2.0, FR-7210)* Force-add an asset by TLE and a ground asset, then (a) before starting and (b)
   after starting and advancing, save and resume: both assets are present in the resumed world with
   the same state as before the save. (Fails today; see Open Question 1.)
6. *(v2.0)* A save whose content portion fails load-time validation is refused with the problems
   listed, and the session registry is unchanged.
7. *(v2.0)* A save produced before v2.0 (no format version) still resumes by vignette ID, and the
   White Cell is told it depended on the vignette file.
8. *(v2.0)* A save records the simulator version; resuming one whose recorded version differs from
   the running one succeeds and shows the White Cell a warning naming both.
9. Resuming in a new process (a fresh server or `InProcessSession`) reproduces the saved state
   (`NFR-1800`).

## Verification Plan

Test (automated) for every criterion, consistent with `FR-7210`/`FR-7220`/`FR-7230`'s and
`NFR-1800`'s Verification Method ("Test"). Criteria 3–5 are the requirement-level tests `FR-7230`'s
and `FR-7210`'s Acceptance Criteria name, and must use a vignette file in a temporary content
directory (never edit a shipped vignette). Each new test carries
`@pytest.mark.verifies(...)` naming the leaf it checks (`FR-7210`, `FR-7220`, `FR-7230` or
`NFR-1800`), per the project's test-origin rule (`BL-0310`). The determinism gate
(`test_determinism.py`) must stay green.

## Dependencies

`FEAT-7100` (Ordered Event Log) in the Feature Catalog — save/resume persists and reconstructs the
event log. *(v2.0)* Reuses, without changing, the vignette loader, world builder and validation of
[FS-131](FS-131-load-time-vignette-validation.md) (`FEAT-5300`) and the world-to-vignette conversion
of [FS-117](FS-117-vignette-creator.md)/[FS-120](FS-120-save-as-scenario.md); those are existing
code paths, not new Feature-level prerequisites.

## Risks

- *(v2.0)* **Vignette-form round trip may not be exact.** The content portion is built by the
  existing world-to-vignette conversion, which `IP-1173` records as having known limitations. If
  the baseline does not survive conversion field-for-field, criteria 1, 3 and 5 fail. `07` must
  either show the conversion is exact for every field the baseline holds or carry the baseline in a
  form that is (Open Question 4); the acceptance criteria decide, not the mechanism.
- *(v2.0)* **Two loaders for one format.** Resume and the vignette library would both load vignette
  content; if they diverge, a save could resume but fail to extract (or the reverse). Mitigation:
  one load path, as Subsystem Responsibilities states.
- Splitting this mechanism out of FS-106 (v1.0) created a cross-document seam with FS-106: a change
  to who may trigger save/resume must be coordinated between both (and now `BL-0307`).
- `FR-7220` and `FR-7210` were recorded verified (VR-1100) although neither held in full; the v2.0
  tests must assert the behaviors directly rather than re-run the old round-trip test.

## Open Questions

1. *(v2.0)* **Force edits are lost on resume (defect, found while specifying).** The force-edit
   operations (`SessionManager.add_tle` and its siblings) re-baseline the in-memory replay baseline
   so rewind keeps the edit, but neither the save nor the event log records them; resume rebuilds
   the baseline from the vignette file, so the edits vanish. Reproduced on 2026-10-23: an asset
   force-added by TLE is present before `save_state` and absent after `from_state`. Design Decision
   1 fixes it by saving the baseline. **Resolution path:** none upstream is needed — this
   specification already requires the behavior (criterion 5); recorded so `07` plans it inside the
   same package and `09` checks it, and filed to the backlog as a bug against `FR-7210`.
2. **Malformed session portion.** Failure modes for a save whose session portion is corrupt or
   partial are not enumerated by the requirements baseline. Matters because `load_save` accepts
   arbitrary JSON from the LAN. **Resolution path:** `04` could add an `NFR-1600`-family leaf; until
   then, an IP may refuse such a save with a clear error, which no requirement forbids.
3. *(v2.0)* **GDS-07 §6 and OQ1–OQ3 become stale when this is built.** GDS-07 still describes a save
   without embedded content and lists OQ1–OQ3 as open. **Resolution path:** `03`, at its next
   maintenance pass (rides `BL-0311`), records Design Decisions 1–4 against OQ1–OQ3 and updates
   §6 when the code ships.
4. *(v2.0)* **Exact form of the baseline in the save.** Whether the content portion alone (vignette
   form) is enough to rebuild the replay baseline exactly, or the save must also carry the baseline
   world as serialized, is not decidable from approved inputs — it depends on the conversion's
   fidelity (Risks). **Resolution path:** `07` decides with evidence (a round-trip check over the 19
   shipped vignettes plus force edits); either way the content portion stays in vignette form for
   `FR-7220`.
5. **Domain ownership** (v1.0, unchanged): DOM-003 §6 frames save/resume as White Cell territory;
   this document specifies the mechanism regardless of who triggers it. Flagged for the domain owner.

## Related ADRs

ADR-0022 (save-file ownership split) —
`docs/architecture/adr/ADR-0022-save-file-ownership-split.md`. *(v2.0)* ADR-0002 (deterministic
core; resume relies on it), ADR-0015 (LAN trust model; `/save` exposes ground truth).

## Related Interfaces

INT-0011, INT-0012 — per `docs/design/05-interface-control-document.md` (both are also this
document's Interfaces Used).
