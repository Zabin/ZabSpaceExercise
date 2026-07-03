# FS-110 — Save & Resume

> **Document ID:** FS-110
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [DOM-003](../domains/DOM-003-white-cell-framework.md) §6, [ADR-0022](../architecture/adr/ADR-0022-save-file-ownership-split.md)
> **Referenced By:** [FS-106](FS-106-white-cell-dashboard.md) (the White-only save/resume trigger surface this mechanism serves), [docs/feature-planning/03-feature-catalog.md](../feature-planning/03-feature-catalog.md) `FEAT-7200`
> **Produces:** the persisted session artifact [FS-107](FS-107-after-action-review.md)'s AAR replay reads from
> **Feature Mapping:** FS-110 (this document)
> **Related Topics:** [FS-106](FS-106-white-cell-dashboard.md) (facilitator-facing save/resume trigger), [FS-107](FS-107-after-action-review.md) (AAR replay over a saved/resumed event log)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template. It is a **new**
Feature Specification, split out of `FS-106-white-cell-dashboard.md` v1.0 per
`docs/feature-planning/05-feature-review.md` Finding F-03 — the prior v1.0 draft bundled this
mechanism (its own dedicated ADR-0022 and its own ICD issue closure, §7 issue 4) inside the White
Cell facilitator UI document.*

## Feature ID

FS-110

## Title

Save & Resume

## Purpose

Persist a complete session snapshot on demand or at exercise end and reproduce it exactly when
resumed, with the save file's Vignette/content portion independently extractable from its
Session/event-log portion — per `docs/feature-planning/03-feature-catalog.md` `FEAT-7200`'s own
Purpose field.

## Scope

In scope: the deterministic save/resume round trip (`WorldState`, full `EventLog`, Snapshots, Role
Assignments); the save file's content/session ownership split (independent re-extractability of the
Vignette/content portion apart from the Session/event-log portion). Out of scope: *who* is
authorized to trigger a save/resume request ([FS-106](FS-106-white-cell-dashboard.md)'s
facilitator-facing panel); cross-build/cross-version save-file compatibility (CR-08 in the
requirements baseline — an explicitly out-of-scope candidate, same-build round trips only); AAR
replay/scrub over a resumed session's event log ([FS-107](FS-107-after-action-review.md)).

## Requirements Implemented

FR-7210 (deterministic save-file round trip), FR-7220 (save-file content/session ownership split),
NFR-1800 (single-sitting, single-process exercise availability) — per
`docs/feature-planning/03-feature-catalog.md` `FEAT-7200`'s `Included Requirements`.

## User Workflows

- A facilitator (via [FS-106](FS-106-white-cell-dashboard.md)'s panel) or another authorized caller
  requests a save of the current or completed session; a save file is written to disk.
- A later session load reads that save file and reconstructs a `WorldState` identical to the state
  at the moment of save.
- A content author or facilitator extracts a save file's Vignette/content portion and loads it as a
  fresh vignette's starting state, independent of that save's own Session/event-log history.

## System Behaviour

- **A save persists a complete session snapshot** (FR-7210): `WorldState`, the full `EventLog`,
  Snapshots, and Role Assignments, taken on demand or at exercise end.
- **A resume reproduces the exact saved state** (FR-7210): the resumed `WorldState` is identical,
  field-for-field, to the state at the moment of save.
- **The save file's content and session portions are structurally distinguishable and
  independently re-importable** (FR-7220): the Vignette/content portion (force lay-down, templates,
  parameters as originally loaded) can be extracted and loaded as a new session's starting vignette
  without that save's Session/event-log history; the two portions are never merged into an
  undifferentiated blob.
- **v1 supports single-sitting, single-process availability only** (NFR-1800): there is no
  mid-exercise save/resume across process restarts in v1 — the save/resume path described here is
  for deliberate, on-demand or end-of-exercise persistence, not crash recovery. GDS-05's own Open
  Question 2 flags an unresolved tension between this "single exercise per process" framing and the
  shipped `/api/sessions` multi-session discovery endpoint (FS-109); this document restates the
  documented v1 boundary as written rather than resolving that tension (see Open Questions).

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `session/manager.py` (`SessionManager`) | Owns the save/resume operation itself: serializes `WorldState`/`EventLog`/Snapshots/Role Assignments on save; deserializes and reconstructs identical state on resume. |
| Content & Data (`content/vignette.py` and the save file's own on-disk format) | Owns the content/session ownership split within the save file (ADR-0022) — the Vignette/content portion's independent extractability. |
| `session/aar.py` | Consumes a resumed session's `EventLog` for replay (FS-107) — a downstream consumer of this Feature's output, not a subsystem this Feature's own behavior depends on. |

## Interfaces Used

INT-0011 (Session Layer → Content & Data, vignette/template load) — the content-portion
re-extraction path. INT-0012 (Session Layer → Content & Data/Filesystem, save round trip) — the
save/resume round trip itself.

## Data Model Changes

None beyond the existing Session entity's persisted fields (`WorldState`, `EventLog`, Snapshots,
Role Assignments — `docs/architecture/04-domain-model.md` §1.14 Session, "Persistent state"). The
content/session ownership split (FR-7220) is a structural property of the on-disk save-file format,
not a new Domain Model entity.

## State Changes

- A save request transitions no live session state itself — it is a read-and-persist operation
  against the current state.
- A resume request reconstructs a full `WorldState`/`EventLog`/Snapshot/Role-Assignment set into a
  new or continued session, identical to the state at save time.

## Error Handling

- The requirements baseline does not enumerate failure modes for a corrupted or partial save file
  beyond the round-trip and content/session-split guarantees stated above — flagged as an Open
  Question.
- Cross-build/cross-version save-file compatibility is explicitly out of scope (CR-08, candidate,
  not baselined) — a save produced by one engine build is not guaranteed loadable by a later build;
  no error-handling contract beyond same-build round trips is specified.

## Performance Considerations

No NFR beyond NFR-1800 (single-sitting/single-process availability boundary, cited above) applies
specifically to this Feature per the requirements baseline.

## Security Considerations

- Per `CLAUDE.md`'s LAN trust model, `/save` is one of the documented no-cell, ground-truth-exposing
  endpoints (ADR-0015) — this Feature's save output is ground truth, not fog-of-war-filtered, by
  the same accepted v1 trust-boundary exception FS-109's Security Considerations describes for
  other no-cell endpoints.

## Acceptance Criteria

- A session saved at sim time T and immediately resumed produces a `WorldState` identical to the
  pre-save state at T.
- A save file's Vignette/content portion, extracted and loaded independently, produces a valid
  fresh vignette starting state with no dependency on that save's own event-log history.

## Verification Plan

Test (automated) for both Acceptance Criteria above, consistent with FR-7210/FR-7220's own stated
Verification Method ("Test") in `docs/requirements/01-functional-requirements.md`.

## Dependencies

`FEAT-7100` (Ordered Event Log) in the Feature Catalog — save/resume persists and reconstructs the
event log this Feature depends on existing first. No other `FS-xxx` document is a prerequisite.

## Risks

- Splitting this mechanism out of FS-106 (v1.0) creates a cross-document seam with
  [FS-106](FS-106-white-cell-dashboard.md): a future change to who may trigger a save/resume
  request must be coordinated between both documents.
- `IMP-106A-white-cell-dashboard.md`/`IP-1060` were written against FS-106's prior, broader scope
  and now over-cite relative to both FS-106 v2.0 and this new document — reconciling the
  Implementation Package layer is a follow-on task, not performed here.

## Open Questions

- **GDS-05 Open Question 2** (restated in `docs/requirements/02-non-functional-requirements.md`'s
  NFR-1800 entry): tension between the "single exercise per process" v1 framing and the shipped
  multi-session `/api/sessions` discovery endpoint (FS-109) is not resolved by this document —
  restated here as inherited from the upstream requirements baseline, per that baseline's own
  instruction not to re-resolve it downstream.
- **Domain ownership:** as with FS-109, `docs/domains/DOM-003-white-cell-framework.md` §6 frames
  save/resume as White-Cell-domain territory (a facilitation concern: "can I resume a multi-week
  course's exercise across sessions"). This document specifies the underlying mechanism itself,
  usable regardless of which cell or facilitator triggers it — flagged for the domain owner, not
  resolved here.
- Corrupted/partial save-file error handling is not enumerated in the requirements baseline; whether
  this needs a new NFR or is intentionally left to implementation discretion is open.

## Related ADRs

ADR-0022 (save-file ownership split) —
`docs/architecture/adr/ADR-0022-save-file-ownership-split.md`.

## Related Interfaces

INT-0011, INT-0012 — per `docs/design/05-interface-control-document.md` (both are also this
document's Interfaces Used).
