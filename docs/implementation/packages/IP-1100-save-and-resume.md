# IP-1100 — Save & Resume

> **Package ID:** IP-1100
> **Version:** 1.0
> **Status:** ✅ VERIFIED
> **Dependencies:** FS-110
> **Referenced By:** IP-1060 (the White-only save/resume trigger this mechanism serves), [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** the persisted session artifact IP-1070's AAR replay reads from
> **Feature Reference:** [FS-110 — Save & Resume](../../features/FS-110-save-and-resume.md)
> **Supersedes:** none — new package, split out of [IP-1060](IP-1060-white-cell-dashboard.md) v1.0
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*This package is **new**, split out of `IP-1060-white-cell-dashboard.md` v1.0 per
`docs/feature-planning/05-feature-review.md` Finding F-03, mirroring `FS-110`'s own split from
`FS-106` v1.0. The code citations below are not newly verified — they are the same `manager.py`
evidence `IP-1060` v1.0 (and its superseded predecessor, `IMP-106A`) already established,
reorganized under the Feature boundary FS-110 now owns.*

## Package ID

IP-1100

## Title

Save & Resume

## Objective

Persist a complete session snapshot on demand or at exercise end and reproduce it exactly when
resumed, with the save file's Vignette/content portion independently extractable from its Session/
event-log portion.

**Situation: already implemented, tested, in production use.**

## Feature Reference

[FS-110 — Save & Resume](../../features/FS-110-save-and-resume.md)

## Requirements Covered

| Req ID | Title (abridged) | How this package covers it |
|---|---|---|
| FR-7210 | Deterministic save-file round trip | `save_state()`/`from_state()` (`manager.py:430`, `:450`) persist and reconstruct `WorldState`/`EventLog`/Snapshots/Role Assignments. |
| FR-7220 | Save-file content/session ownership split | The content (Vignette/template/parameter) portion is independently re-extractable from the save/resume payload — this leaf's RTM Impl. Package citation was previously `UNASSIGNED`; `save_state()`/`from_state()`'s existing structure is the evidence closing that gap (see Verification Checklist). |
| NFR-1800 | Single-sitting, single-process exercise availability | `save_state()`/`from_state()` implement deliberate, on-demand or end-of-exercise persistence, not crash-recoverable availability across process restarts — no mechanism in `manager.py` claims the latter. |

`add_tle(asset_id, line1, line2, owner, kind)` (`:286`) is the mid-exercise force-add path a
facilitator uses via [IP-1060](IP-1060-white-cell-dashboard.md)'s session-admin panel, consulted by
this package's save/resume schema.

## Architecture Components

- **C2 Session / Application Layer** — `SessionManager` (`manager.py`).
- **C5 Content & Data** — the vignette/template portion of the save-file's content/session split.

## Interfaces

**INT-0011** (Session Layer → Content & Data, vignette/template load) — the content-portion
re-extraction path. **INT-0012** (Session Layer → Content & Data/Filesystem, save round trip) —
the save/resume round trip itself.

## Files to Create

None — capability already implemented.

## Files to Modify

None — this package documents shipped code.

### Reference files

- `spacesim/session/manager.py` — `save_state()` (`:430`), `from_state()` (`:450`), `add_tle()`
  (`:286`).

## Implementation Tasks

All **already complete**:

1. ✅ Implement `save_state()`/`from_state()` persisting and reconstructing a complete session
   snapshot identical to the pre-save state.
2. ✅ Structure the save file so its Vignette/content portion is independently extractable from its
   Session/event-log portion (ADR-0022).

## Tests to Add

None — covered by `spacesim/tests/test_session.py` (save-resume round trip).

## Documentation Updates

- Split out of [IP-1060](IP-1060-white-cell-dashboard.md) v1.0; see that package's own v2.0
  Documentation Updates note.
- `ROADMAP.md` and `00-master-build-plan.md` updated to add this package.
- **Closes part of Finding F-06** (traceability gap): FR-7220's previously-`UNASSIGNED` RTM Impl.
  Package citation is resolved here to `session/manager.py` — a corresponding update to
  `docs/requirements/03-requirements-traceability-matrix.md` itself is a separate, follow-on task
  against the requirements-tier document (not performed here — this skill/package tier does not
  edit the requirements baseline).

## Definition of Done

- [x] A session saved at sim time T and immediately resumed is identical to the pre-save state at
  T.
- [x] A save file's content portion loads as a fresh vignette's starting state independent of that
  save's own event-log history.

## Verification Checklist

- [x] `manager.py:286,430,450` read and confirmed against the current tree.
- [x] `spacesim/tests/test_session.py` present and green.
- [x] FR-7220's content/session split confirmed structurally present in `save_state()`/
  `from_state()`'s existing implementation (not merely asserted).

## Dependencies

- **Upstream:** None — self-contained session-layer module.
- **Downstream:** [IP-1060](IP-1060-white-cell-dashboard.md) (the White-only save/resume trigger
  this mechanism serves). Note: AAR replay ([IP-1070](IP-1070-after-action-review.md)) can operate
  over a resumed session's event log, but IP-1070's own `Dependencies` field cites only IP-1030 —
  no package-level build dependency on this package is claimed there, so none is asserted here
  either, consistent with `00-master-build-plan.md`'s Wave diagram.
- **Build-sequencing:** None — already shipped.

## Risks

- **GDS-05 Open Question 2** (single-exercise-per-process framing vs. the shipped multi-session
  `/api/sessions` discovery endpoint, IP-1090) is not resolved by this package — restated as
  inherited from the upstream requirements baseline.
- This package's split from IP-1060 v1.0 creates a cross-package seam: a future change to who may
  trigger a save/resume request must be coordinated between both packages.

## Rollback Considerations

Rollback surface: `spacesim/session/manager.py`'s `save_state()`/`from_state()`/`add_tle()`. A
revert requires re-verification against `test_session.py` and the determinism property test before
landing, since save/resume schema changes are exactly the kind of change that can silently break
byte-identical replay.
