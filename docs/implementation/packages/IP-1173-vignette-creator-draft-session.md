# IP-1173 — Vignette Creator Draft Session & Reverse Serialization

> **Package ID:** IP-1173
> **Version:** 1.0
> **Status:** 🟢 READY *(MSTR-006 §3 authorization obtained 2026-07-05, project owner, recorded in
> `docs/pipeline/pipeline-journal.md` run #45 — no package-level dependency, so authorization was
> the only gate; independent of every other Tranche 3 package.)*
> **Dependencies:** [FS-117](../../features/FS-117-vignette-creator.md) v1.1 (`FR-5110`),
> [ADS-5100A](../../architecture/ADS-5100A-vignette-creator-session-and-ui.md) §2,
> [FS-109](../../features/FS-109-multiplayer-session-transport.md)/[IP-1090](IP-1090-multiplayer-session-transport.md)
> (the session-registry/locking machinery this package reuses, unmodified — `VERIFIED`),
> [FS-110](../../features/FS-110-save-and-resume.md)/[IP-1100](IP-1100-save-and-resume.md)
> (`save_state()`/`from_state()` — a related but distinct serialization concern, read for contrast
> only, not modified — `VERIFIED`)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** the draft-session lifecycle and "Save as Vignette" function
> [IP-1174](IP-1174-vignette-creator-ui-surfaces.md)'s UI surfaces are thin clients over
> **Feature Reference:** [FS-117 — Vignette Creator](../../features/FS-117-vignette-creator.md)
> (`FR-5110` slice)
> **Supersedes:** none — new package
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/session/inprocess.py`](../../../spacesim/session/inprocess.py),
> [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package. Confirmed directly against the live code at authoring time:
`SessionManager.__init__` and `SessionManager.start()` are distinct calls — a `SessionManager`
instance can exist, be registered in `InProcessSession._sessions`, and receive mutations (e.g. via
the existing `POST /api/sessions/{sid}/force/tle` route, which only requires the session id to
exist) without ever having `start()` called — exactly the "unstarted `SessionManager` instance"
`ADS-5100A` §2 specifies as the draft-session mechanism. No reverse-serialization function
(`WorldState`/`VignetteContext` → `Vignette` YAML) exists anywhere today — `save_state()`/
`from_state()` serialize session/game state (eventlog, pending orders, SSN requests), not
authorable vignette content — so this package's "Save as Vignette" function is genuinely new,
not a variant of the existing save/resume mechanism.*

## Package ID

IP-1173

## Title

Vignette Creator Draft Session & Reverse Serialization

## Objective

Let White Cell open an in-app authoring session backed by a server-side draft session (an unstarted
`SessionManager` instance, registered and locked the same way a normal session is), accumulate
asset/parameter/ROE edits across multiple round trips with no clock advance or scheduler activity,
and emit a complete `Vignette` YAML file only on an explicit "Save as Vignette" action — never a
partial file from an in-progress session.

> **This is a forward-design package. Per MSTR-006 §3, this document's own specification is not
> itself an authorization to write code** — a separate, explicit user go-ahead is required before
> any Implementation Task below begins.

## Feature Reference

[FS-117 — Vignette Creator](../../features/FS-117-vignette-creator.md) (`FR-5110` slice)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-5110 | Iterative in-app vignette composition | A new "create draft" entry point registers an unstarted `SessionManager` in `InProcessSession._sessions` (reusing the existing registry/locking/eviction machinery, never `start()`-ed); every Creator mutation (asset add/edit/reassign/delete, parameter edit, ROE selection, seat/role assignment) applies directly to this draft session's live `WorldState`/`VignetteContext`; a new reverse-serialization function converts the draft session's current state into a complete `Vignette` YAML file, called only by an explicit "Save as Vignette" action — no partial file is ever written before that action, since no other code path writes to `VIGNETTE_DIR`. |

## Architecture Components

- **C2 Session / Application Layer** — `session/inprocess.py` gains a "create draft session" entry
  point (parallel to `load_vignette()`, but constructing an empty/near-empty starting `WorldState`
  rather than one built from an existing vignette file) and never calls `start()` on it;
  `session/manager.py`/a new module gains the reverse-serialization function.
- **C5 Content & Data** — the reverse-serialization function is the mirror image of
  `content/vignette.py`'s `load_vignette()`/`build_world()`: it walks a `WorldState`'s assets/
  sensors and a `VignetteContext`'s parameter/ROE/objective state and emits a `Vignette`
  pydantic-model instance, then writes it to `VIGNETTE_DIR` via the same YAML-dump convention every
  hand-authored vignette file already follows.
- **C4 Operator Console** — not this package's concern (see [IP-1174](IP-1174-vignette-creator-ui-surfaces.md));
  this package only builds the session-layer API the UI will call.

## Interfaces

**INT-0003** (White Cell Facilitator ↔ Operator Console, "in-app scenario builder") — this
package's draft-session lifecycle and reverse-serialization function are the session-layer half of
`INT-0003`'s implementation; [IP-1174](IP-1174-vignette-creator-ui-surfaces.md) builds the
Operator-Console half over it.

## Files to Create

- `spacesim/content/vignette_export.py` *(proposed, new)* — the reverse-serialization function
  (`WorldState`, `VignetteContext` → `Vignette` model instance → YAML file), kept in a separate
  module from `vignette.py`'s existing load-direction logic for a clean read/write seam (mirrors
  the existing `load_vignette()`/`build_world()` pairing's own module, but as a new file rather than
  growing `vignette.py` with a second, opposite-direction responsibility — a naming/organization
  choice `08-code-implementation` may revisit if a single-module approach proves cleaner once the
  actual field-by-field mapping is written).

## Files to Modify

- `spacesim/session/inprocess.py` *(proposed)* — a new `create_draft_session(sid: str) -> Ack`-style
  method (or an optional-vignette-id parameter on the existing `load_vignette()`, if that proves
  the cleaner shape once implemented) that registers a `SessionManager` backed by an empty/minimal
  starting `WorldState` — never calling `start()`. Reuses the existing `_evict_if_full()` cap
  (`MAX_LIVE_SESSIONS`) unmodified, which already provides a coarse answer to `FS-117`'s Open
  Question 2 (an abandoned draft session is eventually evicted once enough other sessions are
  created — noted as an existing, adequate-for-v1 mechanism, not a gap this package must solve
  from scratch with a new TTL system).
- `spacesim/session/manager.py` *(proposed)* — depending on where `08-code-implementation` finds the
  cleanest seam, `SessionManager` may need small read accessors (e.g. exposing its current
  `world`/`ctx` cleanly) for `vignette_export.py` to consume — no change to `start()`,
  `advance_to()`, or any clock/scheduler logic, since a draft session must never exercise those
  paths.
- `spacesim/ui_web/server.py` *(proposed)* — new routes: a "create draft session" route
  (parallel to the existing session-creation route) and a "save as vignette" route calling the new
  reverse-serialization function and returning the written vignette's id/path. Both are additive;
  no existing route changes.

**Explicitly out of scope for this package:** every specific UI surface (JSON view, 2D/3D preview,
asset entry forms, asset menu, seat/role matrix) — those are [IP-1174](IP-1174-vignette-creator-ui-surfaces.md)'s
concern, which is a thin client over this package's session-layer API. This package also does not
implement the typed-parameter sub-models ([IP-1171](IP-1171-typed-payload-bus-parameters.md)) or
per-cell ROE ([IP-1172](IP-1172-per-cell-roe-enforcement.md)) schemas themselves — its
reverse-serialization function must be written to emit whatever `Vignette` shape those two packages
define, so it should be sequenced to land after (or be revised to reflect) their schemas, per
Dependencies below.

## Implementation Tasks

**Not started — authorized 2026-07-05 (MSTR-006 §3).** Proposed sequence:

1. Write a failing test asserting a "create draft session" call registers a `SessionManager` that
   is never `start()`-ed and produces no event log, before writing the entry point.
2. Add the draft-session creation entry point, reusing `InProcessSession`'s existing registry/
   locking/eviction machinery unmodified.
3. Write a failing test asserting the reverse-serialization function, given a hand-constructed
   `WorldState`/`VignetteContext`, produces a `Vignette` YAML file that `load_vignette()` can load
   back and reproduce (a round-trip test), before writing the function.
4. Implement the reverse-serialization function in the new `vignette_export.py` module, covering at
   minimum: assets (with their typed payload/bus parameters, once [IP-1171](IP-1171-typed-payload-bus-parameters.md)
   lands), ground sites, per-cell ROE (once [IP-1172](IP-1172-per-cell-roe-enforcement.md) lands),
   `roles_needed`/seat declarations (once [IP-1174](IP-1174-vignette-creator-ui-surfaces.md)'s
   seat/role matrix work defines the seat-count-declaration shape), and the basic vignette metadata
   fields (`id`, `title`, `classification`, etc.) the Creator's UI collects.
5. Add the "save as vignette" HTTP route calling this function, and confirm no partial file is ever
   written by any other code path (per `FR-5110`'s own Postcondition).
6. Confirm the draft session's clock never advances by construction — no test should be able to
   drive it forward via any existing time-control route, since a draft session is never `start()`-ed.

## Tests to Add

*(Proposed — none exist yet.)*

- `spacesim/tests/test_vignette_creator_session.py` *(new)* — one test per Acceptance Criterion:
  - Given a fresh draft session with several incremental asset/parameter edits but no save action,
    no file appears in `VIGNETTE_DIR` (`FR-5110`'s own literal Acceptance Criterion).
  - Given a draft session with a small force lay-down, "Save as Vignette" produces a file that
    `load_vignette()` can load and `build_world()` can build without error.
  - Given a draft session, no time-control route (`step`/`advance_to`/`red_step`) succeeds against
    it while it remains unstarted — confirms the "no clock advance, no scheduler activity"
    guarantee is enforced, not merely assumed.
  - Given `MAX_LIVE_SESSIONS` draft (or mixed draft/normal) sessions already live, creating one more
    evicts the oldest per the existing `_evict_if_full()` behavior, unmodified.

## Documentation Updates

- `ROADMAP.md` Implementation Packages theme — add this package's row.
- `docs/features/FS-117-vignette-creator.md`'s `Referenced By` metadata — add this package once
  authored (this pass); also close (or explicitly leave open with this package's noted resolution)
  Open Question 2 (abandoned-draft-session lifecycle) in a future `06-feature-specification` touch,
  citing the existing `_evict_if_full()` mechanism as the v1 answer.
- `CLAUDE.md`'s Code Map — a brief addition for `content/vignette_export.py` (or wherever the
  reverse-serialization function lands) and the draft-session entry point in `session/inprocess.py`.
- `docs/design/05-interface-control-document.md`'s `INT-0003` entry — update from
  "not yet implemented" (if it currently reads that way) to reflect this package's concrete
  implementation, mirroring `IP-1160`'s precedent of correcting an ICD entry as part of the first
  package that makes an interface real.

## Definition of Done

- [x] **Explicit user authorization obtained** for this package's Implementation Tasks (MSTR-006
  §3, 2026-07-05, project owner, recorded in `docs/pipeline/pipeline-journal.md` run #45).
- [ ] A draft session can be created, registered, and mutated via existing session-scoped routes
  (e.g. `force/tle`) without ever being `start()`-ed.
- [ ] No time-control route succeeds against an unstarted draft session.
- [ ] "Save as Vignette" produces a file `load_vignette()`/`build_world()` can load and build
  without error, for at least a minimal force lay-down.
- [ ] No partial/incomplete vignette file is ever written to `VIGNETTE_DIR` by any code path other
  than the explicit "Save as Vignette" action.
- [ ] The existing `MAX_LIVE_SESSIONS` eviction mechanism applies unmodified to draft sessions.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] `spacesim/tests/test_vignette_creator_session.py` exists and is green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green (a draft session never
  advances its clock, so it produces no event log to test determinism against; this item confirms
  no accidental clock-advance path was introduced).
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green.
- [ ] Full existing suite re-run with zero regressions (in particular, `test_session.py`/
  `test_session_features.py`'s existing session-registry/eviction tests, confirming this package's
  draft sessions don't break the existing normal-session lifecycle).
- [ ] Independently confirm (not merely re-cite), by reading the shipped code directly, that no
  code path other than the explicit "save as vignette" route writes to `VIGNETTE_DIR`.
- [ ] Independently round-trip at least one Creator-produced vignette file through
  `load_vignette()`/`build_world()` and confirm it builds a `WorldState` with the expected assets.

## Dependencies

- **Upstream:** [FS-117](../../features/FS-117-vignette-creator.md) v1.1,
  [ADS-5100A](../../architecture/ADS-5100A-vignette-creator-session-and-ui.md) §2 (binding
  grounding for the draft-session mechanism), the existing session registry/locking/eviction
  machinery in `session/inprocess.py` (`VERIFIED` via [IP-1090](IP-1090-multiplayer-session-transport.md),
  unmodified by this package).
- **Downstream:** [IP-1174](IP-1174-vignette-creator-ui-surfaces.md) — every UI surface is a thin
  client over this package's draft-session API. The reverse-serialization function's field coverage
  should be revisited once [IP-1171](IP-1171-typed-payload-bus-parameters.md)/
  [IP-1172](IP-1172-per-cell-roe-enforcement.md) land, so it emits their new schema shapes, not
  merely the fields that exist before those packages ship.
- **Build-sequencing:** Independent of [IP-1170](IP-1170-isr-beam-mode-coverage.md)/
  [IP-1171](IP-1171-typed-payload-bus-parameters.md)/[IP-1172](IP-1172-per-cell-roe-enforcement.md)
  at the session-layer/eviction level (different files, no shared seam) — but its
  reverse-serialization function's completeness is naturally staged after those three, since it
  should serialize whatever schema they define. `08-code-implementation` may build the draft-session
  lifecycle itself in parallel with those packages and land the export function's full field
  coverage last.

## Risks

- **Two data paths for one draft is the most likely implementation defect**, carried forward from
  `ADS-5100A`'s own Risk 1 and `FS-117`'s own Risks — this package's own draft-session state must
  be the single source of truth [IP-1174](IP-1174-vignette-creator-ui-surfaces.md)'s JSON view and
  form UI both read/write; this package does not itself introduce a second data path, but a
  careless `08-code-implementation` pass on the UI package could.
- **Reverse serialization is genuinely new code, not a variant of `save_state()`/`from_state()`** —
  a risk of underestimating its scope as "just call `save_state()`" is real; this package's own
  Files to Create explicitly separates it into a new module for this reason.
- **Abandoned-draft-session lifecycle (Open Question 2) is answered pragmatically, not definitively**
  — the existing `MAX_LIVE_SESSIONS` eviction cap is a coarse, already-existing mechanism, not a
  purpose-built TTL/resume-list; if draft-session accumulation under real White-Cell usage proves
  this insufficient, that is a future finding, not a defect in this package as scoped.
- **The reverse-serialization function's field coverage depends on two sibling packages' schemas**
  ([IP-1171](IP-1171-typed-payload-bus-parameters.md), [IP-1172](IP-1172-per-cell-roe-enforcement.md))
  — if `08-code-implementation` builds this package before those two, the exported vignette will be
  missing typed-parameter/per-cell-ROE fields until a follow-up pass adds them; this is an accepted,
  disclosed sequencing choice, not a silent gap.

## Rollback Considerations

The draft-session entry point and reverse-serialization function are both net-new, additive
surfaces — reverting `session/inprocess.py`'s new entry point and deleting
`content/vignette_export.py` (plus the two new HTTP routes) fully removes this package's
capability with no effect on any existing session/vignette-loading behavior. No data-migration
concern: a vignette file the Creator already produced remains a perfectly ordinary hand-editable
YAML file after rollback — nothing about `load_vignette()`/`build_world()` changes, since this
package only adds a new *writer*, never modifies the existing *reader*.
