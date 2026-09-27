> **Document ID:** FS-120
> **Version:** 1.0
> **Status:** ✅ Ready for implementation planning
> **Note on this repository's chain:** no Feature Catalog exists here; the approved input is
> `docs/requirements/01-functional-requirements.md` `FR-5510` (new parent `FR-5500`).
> **Dependencies:** [FS-118](FS-118-external-vignette-directories.md) (`FR-5420` — the user-save
> directory target this Feature's write must land in), [FS-110](FS-110-save-and-resume.md)
> (`FR-7210`/`FR-7220` — the session save/resume mechanism this Feature is explicitly distinct
> from, per `FR-5510`'s own Rationale), [FS-117](FS-117-vignette-creator.md) (`IP-1173`'s
> `export_vignette`/`save_vignette` — the draft-session export mechanism this Feature is also
> explicitly distinct from)
> **Referenced By:** [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0071` (external
> validation report, 26 Sep 2026, item B5), [IP-1200](../implementation/packages/IP-1200-save-as-scenario.md)
> (Implementation Package, `NOT STARTED`, not yet authorized)
> **Produces:** a mid-exercise-state-to-new-vignette save capability satisfying `FR-5510`
> **Feature Mapping:** FS-120 (this document)
> **Related Topics:** [FS-118](FS-118-external-vignette-directories.md), [FS-110](FS-110-save-and-resume.md)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template.*

# FS-120 — Save-as-Scenario (Mid-Exercise State → New Starting Vignette)

## Purpose

Let White Cell save a running (or paused) session's *current* state as a new vignette whose start
epoch is the moment of save, carrying forward each cell's tracks, each side's remaining resources,
each asset's health, and current space-weather state, with the producing simulator's version
recorded in the file. `FR-5510`'s own Rationale is explicit that this is a third, distinct
capability alongside session save/resume (`FR-7210`/`FR-7220`, which persists a session's own
history for *resuming that session*) and the Vignette Creator's draft save (`IP-1173`, which
builds a vignette from an *unstarted draft's* state, never a running session's).

## Scope

**In scope:** a new save action against a running/paused session that (a) sets the resulting
vignette's start epoch to the save moment, (b) carries forward each cell's current `TrackCatalog`,
each side's remaining `AssetResources`, each asset's current `BusState`/`PayloadState` health, and
current space-weather state as that vignette's initial conditions, and (c) records the producing
simulator's version (source-control commit or package version) in the file.

**Out of scope:** *where* the resulting file is written — that is `FR-5420`/FS-118's scope, which
this Feature depends on rather than re-specifies; the Vignette Creator's existing unstarted-draft
save path (`IP-1173`), unchanged by this Feature.

## Requirements Implemented

`FR-5510` — Save a running session's current state as a new starting vignette.

## User Workflows

1. White Cell, mid-exercise (session running or paused), triggers a "save as new scenario" action.
2. The system builds a new vignette whose start epoch is the current simulated time, embedding each
   cell's current tracks, remaining resources, asset health, and space-weather state.
3. The system writes the file to the configured user-save directory (`FR-5420`), recording the
   simulator version that produced it.
4. White Cell (or another user) later loads the resulting vignette; the new session starts at the
   embedded epoch with the embedded state as its initial conditions.

## System Behaviour

- The resulting vignette's declared start epoch equals the save moment's simulated time — **not**
  the original vignette's own start epoch (the explicit behavior `FR-5510`'s Rationale contrasts
  with `FR-7210`, which preserves the original epoch on session resume).
- Each cell's `TrackCatalog` at the save moment is embedded as the new vignette's initial per-cell
  belief state — the first vignette-authoring capability in this repository to carry tracks forward
  at all (`FR-5510`'s own Rationale: neither existing save-adjacent path does this).
- Each side's `AssetResources` (remaining Δv, power, etc.) and each asset's `BusState`/
  `PayloadState` health reflect the save-moment's actual values, not the original vignette's
  authored defaults.
- Current space-weather state (from whatever inject/engine state currently represents it) is
  embedded as the new vignette's initial space-weather condition.
- The file records a simulator-version field (source-control commit or package version) — a new
  piece of vignette metadata no prior save-adjacent capability writes.
- Loading the resulting vignette reuses the existing `FR-5310` load-time validation path unchanged.

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `session/manager.py` (`SessionManager`) | Reads the running session's current `WorldState` (tracks, resources, health, space-weather) at the moment of the save-as-scenario request. |
| `content/vignette_export.py` | Builds the resulting `Vignette` object and writes it — the natural extension point, since it already owns `export_vignette`/`save_vignette` for the structurally-adjacent (but distinct, per Purpose) draft-save case; whether this Feature extends that module's existing functions or adds new sibling functions is an `07-implementation-planning` decision, not settled here. |
| `content/vignette.py` | Owns the resulting vignette's load-time validation (`FR-5310`), unchanged. |

## Interfaces Used

`INT-0011` (vignette/template load — the resulting file is loaded through this existing interface
unchanged) and `INT-0012` (save round trip — the closest existing interface for *producing* a
saved file, though `FR-5510`'s output is vignette/content, not a session save; per `ADR-0022`'s
existing ownership split between session-save and content, this Feature's output is content-side).

## Data Model Changes

The `Vignette` schema (`spacesim/content/vignette.py`) gains: an initial-tracks field (currently a
vignette has no notion of pre-populated per-cell tracks at load time — every existing vignette
starts with empty custody), and a simulator-version metadata field. Both are additive per `NFR-2010`
(additive vignette-schema evolution) — a vignette missing these fields (every one of the 19
existing library vignettes) continues to load as before (no initial tracks, no recorded version).

## State Changes

Produces a new vignette file; does not alter the source session's own state (a read-only snapshot
operation from the source session's point of view, analogous to `FR-7310`'s read-only replay
posture, though this Feature is not itself a replay).

## Error Handling

- A save-as-scenario request against a session with no cells' tracks yet (very early in an
  exercise): produces a vignette whose initial tracks are simply empty for that cell — not an
  error, per the additive-schema framing above.
- Requests against a session in an invalid state (e.g. already ended): not addressed by `FR-5510`'s
  own text — see Open Questions.

## Performance Considerations

None named by `FR-5510`. Building a snapshot of current state is comparable in cost to an existing
session save (`FR-7210`), not a new performance class.

## Security Considerations

Write-target safety (no path traversal, writes only to the configured user directory) is `FR-5420`/
FS-118's scope, which this Feature depends on rather than re-implements (`ADR-0007`, `NFR-3700`).

## Acceptance Criteria

1. Given a running session at sim time T with specific track/resource/health/space-weather state,
   saving as a new scenario and then loading the resulting vignette produces a session whose start
   epoch is T and whose initial tracks/resources/health/space-weather match the source session's
   state at T.
2. The resulting file records a simulator version.

## Verification Plan

Test (automated) for both criteria, per `FR-5510`'s own stated Verification Method.

## Dependencies

`FR-5420`/FS-118 (write-target safety), `FR-7210`/FS-110 (the session save/resume mechanism this
Feature is distinct from, cited for contrast), `IP-1173`/FS-117 (the draft-save mechanism this
Feature is distinct from, cited for contrast).

## Risks

- **Naming/conceptual confusion with the two existing save-adjacent capabilities.** An
  Implementation Package author who has not read this document's Purpose/Scope distinction risks
  conflating this Feature with either `FR-7210` (session resume) or `IP-1173`'s draft save,
  producing a capability that silently duplicates or corrupts one of the other two. This document's
  repeated explicit contrast (Purpose, Scope, System Behaviour) exists specifically to prevent that.
- **Schema-additivity risk.** Adding an initial-tracks field incorrectly (e.g. required rather than
  optional) would break every one of the 19 existing library vignettes' load path, violating
  `NFR-2010`. An Implementation Package must verify all 19 still load unchanged, the same regression
  discipline `FS-117`'s own `IP-1171`/`IP-1172` already established for their own additive-schema
  changes.

## Open Questions

1. **What is the observable behavior of a save-as-scenario request against a session in an invalid
   state** (already ended, mid-recovery, etc.)? `FR-5510`'s own Preconditions state only "a running
   or paused session exists" — not addressed for other states.
2. **Does the embedded space-weather state need its own schema representation**, or does the
   existing space-weather inject effect's own data shape already suffice as the vignette's initial
   condition? Not stated by `FR-5510`'s text; likely resolvable by direct inspection of the existing
   `space_weather` inject effect's payload shape at implementation-planning time, not a genuine
   requirements ambiguity — flagged for completeness rather than as a blocking gap.

## Related ADRs

`ADR-0007` (content as data), `ADR-0022` (save-file ownership split — session vs. content, the
precedent this Feature's content-side framing follows).

## Related Interfaces

`INT-0011`, `INT-0012` (see Interfaces Used).
