# IP-1173 — Vignette Creator Draft Session & Reverse Serialization

> **Package ID:** IP-1173
> **Version:** 1.0
> **Status:** 🔵 COMPLETE *(implemented 2026-07-05 by `08-code-implementation` —
> `InProcessSession.create_draft_session`/`save_vignette` added, the new
> `content/vignette_export.py` reverse-serialization module, two new HTTP routes
> (`POST /api/sessions/draft`, `POST /api/sessions/{sid}/save_vignette`), and every time-control
> route (`step`/`advance_to`/`rewind_to`/`undo_last`/`red_doctrine_step`) rejects a draft session.
> 7 new tests, full suite 586 passed/3 skipped (up from 579/3, +7), both permanent gates green.
> Awaiting `09-package-verification` to advance to `VERIFIED`.)*
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

- `spacesim/content/vignette_export.py` *(implemented)* — `export_vignette()`/`save_vignette()`
  (`WorldState`, `VignetteContext` → `Vignette` model instance → YAML file), in a separate module
  from `vignette.py`'s existing load-direction logic, as proposed.

## Files to Modify

- `spacesim/session/inprocess.py` *(implemented)* — `create_draft_session(title: str = "Untitled
  Draft") -> str` registers a `SessionManager` backed by a near-empty `Vignette(id=..., title=...)`
  — never calling `start()`; tracked in a new `self._draft_sessions: set[str]`. Reuses the existing
  `_evict_if_full()` cap (`MAX_LIVE_SESSIONS`) unmodified (extended by one line to also discard an
  evicted sid from `_draft_sessions`, keeping the new set consistent — not a change to the cap
  logic itself), which already provides a coarse answer to `FS-117`'s Open Question 2. `step`/
  `advance_to`/`rewind_to`/`undo_last` each check `session in self._draft_sessions` and return
  `Ack(ok=False, ...)` before touching `SessionManager` at all; `red_doctrine_step` returns `[]`
  for a draft sid. `save_vignette(session, vignette_id, title, classification=...) -> str` calls
  the new module's `save_vignette()` under the session's read lock.
- `spacesim/session/manager.py` — **no change**, as anticipated; no read accessor was needed since
  `vignette_export.py` reads `mgr.world`/`mgr.ctx` directly (both already public attributes).
- `spacesim/ui_web/server.py` *(implemented)* — `POST /api/sessions/draft` (`DraftRequest{title}`
  → `{session}`) and `POST /api/sessions/{sid}/save_vignette` (`SaveVignetteRequest{vignette_id,
  title, classification?}` → `{vignette_id, path}`), both additive; no existing route changed.

**Explicitly out of scope for this package (confirmed unchanged during implementation):** every
specific UI surface — [IP-1174](IP-1174-vignette-creator-ui-surfaces.md)'s concern; the
typed-parameter sub-models ([IP-1171](IP-1171-typed-payload-bus-parameters.md)) and per-cell ROE
([IP-1172](IP-1172-per-cell-roe-enforcement.md)) schemas — this package's `export_vignette()`
serializes whatever fields `Asset`/`PayloadState`/`VignetteContext.roe` carry today (already
including `IP-1172`'s cell-keyed `roe`, since that package landed first in this session); it will
need a follow-up touch once `IP-1171`'s typed payload/bus sub-models ship, per Dependencies below —
not a defect in this pass, a disclosed sequencing consequence.

## Implementation Tasks

**Complete (2026-07-05, `08-code-implementation`).**

1. ✅ Wrote a failing test asserting `create_draft_session()` registers a never-`start()`-ed
   `SessionManager` with an empty event log, before writing the entry point.
2. ✅ Added the draft-session creation entry point, reusing `InProcessSession`'s existing registry/
   locking/eviction machinery unmodified (plus the one-line `_draft_sessions` cleanup addition).
3. ✅ Wrote a failing test asserting the reverse-serialization function, given a draft session with
   a force-added asset, produces a `Vignette` YAML file `load_vignette()`/`build_world()` can load
   back, before writing the function.
4. ✅ Implemented `export_vignette()` in the new `vignette_export.py` module: assets (bucketed by
   owner into `blue_forces`/`red_forces`/`neutral_forces` via `Asset.model_dump(exclude={"owner"})`
   — already carrying whatever typed/legacy fields the live `PayloadState`/`BusState` have),
   sensors, `ctx.roe` (already cell-keyed via `IP-1172`), `ctx.objectives`, and the basic vignette
   metadata fields (`id`, `title`, `classification`, `start_epoch_utc`). `roles_needed`/seat
   declarations deliberately omitted — no seat-count-declaration shape exists yet ([IP-1174](IP-1174-vignette-creator-ui-surfaces.md)'s
   concern); the field is optional/absent-safe, so this is not a gap this package must fill.
5. ✅ Added the "save as vignette" HTTP route; independently confirmed (grep across `spacesim/`)
   that `content/vignette_export.py`'s `save_vignette()` is the only code path that writes to
   `VIGNETTE_DIR`.
6. ✅ Confirmed the draft session's clock never advances: `step`/`advance_to`/`rewind_to`/
   `undo_last`/`red_doctrine_step` all reject a draft sid at the `InProcessSession` boundary
   (not inside `SessionManager` itself — see Risks for why that distinction matters).

## Tests to Add

- `spacesim/tests/test_vignette_creator_session.py` *(new)* — 6 tests: draft session created/
  registered/never-started; force-edit (asset add) accepted before any save; no partial file
  written before save; "Save as Vignette" produces a file `load_vignette()`/`build_world()` load
  and build without error; no time-control route (`step`/`advance_to`/`rewind_to`/`undo_last`/
  `red_doctrine_step`) succeeds against a draft session; `MAX_LIVE_SESSIONS` eviction applies to
  draft sessions unmodified (and cleans up `_draft_sessions` on eviction).
- `spacesim/tests/test_web.py::test_draft_session_create_add_asset_and_save_as_vignette` *(new)* —
  the same flow end to end through the HTTP routes (`POST /api/sessions/draft`, `force/tle`,
  `POST .../save_vignette`), confirming the saved file round-trips through `load_vignette()`/
  `build_world()`.

## Documentation Updates

- `ROADMAP.md` Implementation Packages theme — this package's row (added at planning time) updated
  to `COMPLETE`.
- `docs/features/FS-117-vignette-creator.md`'s `Referenced By` metadata — already present (added
  at planning time). Open Question 2 (abandoned-draft-session lifecycle) remains recorded there as
  open pending a future `06-feature-specification` touch — not closed by this package directly
  (out of this skill's scope to edit the FS), but this package's own text now names the
  `_evict_if_full()` mechanism as the concrete v1 answer for that future touch to cite.
- `CLAUDE.md`'s Code Map — `content/vignette_export.py` entry added; `session/inprocess.py`'s
  entry gained the `create_draft_session`/`save_vignette` addition.
- `docs/design/05-interface-control-document.md`'s `INT-0003` entry — updated from "not yet
  implemented"/open-question framing to reflect this package's concrete route shapes; §7 Issue 10
  marked resolved.
- `docs/requirements/03-requirements-traceability-matrix.md` — `FR-5110`'s Test/Impl. Package
  cells corrected (the prior `Impl. Package` cell cited `content/vignette.py`, which is the
  vignette *schema*, not the iterative-composition capability `FR-5110` actually describes);
  `session/inprocess.py`/`content/vignette_export.py` reverse-index rows updated/added.

## Definition of Done

- [x] **Explicit user authorization obtained** for this package's Implementation Tasks (MSTR-006
  §3, 2026-07-05, project owner, recorded in `docs/pipeline/pipeline-journal.md` run #45).
- [x] A draft session can be created, registered, and mutated via existing session-scoped routes
  (e.g. `force/tle`) without ever being `start()`-ed.
- [x] No time-control route succeeds against an unstarted draft session.
- [x] "Save as Vignette" produces a file `load_vignette()`/`build_world()` can load and build
  without error, for at least a minimal force lay-down.
- [x] No partial/incomplete vignette file is ever written to `VIGNETTE_DIR` by any code path other
  than the explicit "Save as Vignette" action.
- [x] The existing `MAX_LIVE_SESSIONS` eviction mechanism applies unmodified to draft sessions.

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
  disclosed sequencing choice, not a silent gap. **Resolved favorably at build time:** `IP-1172`
  landed first in this same session, so `export_vignette()` already emits the cell-keyed `roe`
  field; only `IP-1171`'s typed payload/bus sub-models (not yet built) are still missing.
- **The time-control rejection deliberately lives in `InProcessSession`, not `SessionManager`.**
  `SessionManager.step`/`advance_to`/`rewind_to` are called directly, unstarted, by a large number
  of engine-level unit tests unrelated to drafts (they construct a bare `SessionManager` and drive
  it without ever calling `.start()`) — adding a generic "reject if not started" check inside
  `SessionManager` itself would have been a much broader, almost certainly regression-inducing
  change, not a targeted one. The `_draft_sessions` set at the `InProcessSession` boundary (the
  actual HTTP-reachable layer) is what makes the rejection specific to *drafts*, not to "any
  not-yet-started session" generally — confirmed by running the full suite, which would have
  caught the broader alternative immediately.

## Rollback Considerations

The draft-session entry point and reverse-serialization function are both net-new, additive
surfaces — reverting `session/inprocess.py`'s new entry point and deleting
`content/vignette_export.py` (plus the two new HTTP routes) fully removes this package's
capability with no effect on any existing session/vignette-loading behavior. No data-migration
concern: a vignette file the Creator already produced remains a perfectly ordinary hand-editable
YAML file after rollback — nothing about `load_vignette()`/`build_world()` changes, since this
package only adds a new *writer*, never modifies the existing *reader*.
