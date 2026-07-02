# IMP-106A — White Cell Dashboard: Session/Inject/Clock Control Plane

> **Document ID:** IMP-106A
> **Version:** 1.0
> **Status:** ✅ Done (as-built — documents existing, test-covered code)
> **Dependencies:** [FS-106](../features/FS-106-white-cell-dashboard.md)
> **Referenced By:** [IMP-107A](IMP-107A-after-action-review.md) (the AAR instrument this dashboard's White-only controls invoke)
> **Produces:** the facilitation control surface [FS-108](../features/FS-108-inject-authoring.md) (candidate, unauthorized) would extend
> **Feature Mapping:** FS-106
> **Related Topics:** [`spacesim/session/manager.py`](../../spacesim/session/manager.py), [`spacesim/session/redai.py`](../../spacesim/session/redai.py)

[↑ Implementation index](INDEX.md) · [Docs index](../INDEX.md)

> **Superseded.** This document's content has been re-derived, re-verified against the current
> source tree, and re-published under the canonical `docs/implementation/packages/` tier as
> [**IP-1060**](../implementation/packages/IP-1060-white-cell-dashboard.md). This file is retained
> for historical reference and is not deleted, but [`IP-1060`](../implementation/packages/IP-1060-white-cell-dashboard.md)
> is the document of record going forward — see
> [`docs/implementation/00-master-build-plan.md`](../implementation/00-master-build-plan.md)
> §"Relationship to the prior `docs/implementations/` corpus."

## 1. Situation

**As-built.** This package documents the existing `SessionManager` surface (god-view, clock
authority, inject firing, Red-doctrine presets, save/resume) that FS-106 specifies as the White
Cell facilitator's console.

## 2. God-view without granting Red/Blue access

`SessionManager.get_godview()` (`manager.py:554`) returns the raw `WorldState` — unfiltered ground
truth — and is deliberately a **separate** method from `get_view(cell)`/`get_scene(cell)`
(`:520`, `:523`), which route through `CellController`'s fog-of-war filtering (per `CLAUDE.md`'s
"Fog-of-war at the boundary" invariant). FS-106 §3 bullet 1's requirement ("god-view without
granting Red/Blue any new ground-truth access") is structural, not a permissions check on a shared
method: there is no code path by which `get_view("blue")` can return what `get_godview()` returns,
and no cell argument that makes `get_godview()`'s caller anything other than White (enforced at
the `SessionAPI` layer, consistent with the LAN trust model `CLAUDE.md` documents — White-cell
endpoints are no-cell, ground-truth-by-design).

## 3. Inject authoring against the existing library

`InProcessSession.inject_library()` and `SessionManager.list_injects()` (`manager.py:425`) expose
the five reusable templates from `content/inject_library.yaml` (debris breakup, GNSS-jam advisory,
ambiguous RPO, GS outage, geomagnetic storm, per `CLAUDE.md`'s code map) as data, not engine-side
template duplication. `fire_inject(inject, at_sim_t)` (`:492`) is the single firing path — whether
invoked "Now," at "+seconds," or at an absolute UTC time, it resolves to one scheduled
`_h_inject` event (`:564`) and `_inject_effects()` (`:511`) — satisfying FS-106 §3 bullet 2's
"expose the templates with an editable-JSON + scheduler, don't duplicate execution" requirement:
the dashboard's job is populating `inject`'s parameters and a `at_sim_t`, not reimplementing what
the inject does.

## 4. Clock as a single point of authority

`set_clock(running, rate)` (`:131`) and `catch_up()` (`:206`)/`_catch_up_locked()` (`:148`)
implement the server-authoritative lazy clock `CLAUDE.md`'s multiplayer section describes: clock
state (`_wall_anchor`, `_sim_anchor`, `_rate`, `_clock_running`) lives once on `SessionManager`,
guarded by the per-session lock, and every connected client's read triggers the same `catch_up()`
— there is no per-tab pacing state to desynchronize. `clock_state()` (`:210`) is the read-only
status query the dashboard's pause/resume toolbar reflects. `_record_catch_up_lag(wall_cost_s,
target_us)` (`:173`) is the clock-lag watchdog `CLAUDE.md`'s "Key facts" section names — it
detects when real hardware can't keep up with the requested rate and is what the facilitator's
"is the simulation keeping pace" signal is grounded in, rather than an invented heuristic.
`rewind_to(t)` (`:219`) and `undo_last(n)` (`:229`) are the White-only AAR-adjacent controls FS-106
§2 names as in-scope (distinct from the AAR replay/scrub *instrument* itself, [IMP-107A](IMP-107A-after-action-review.md)'s
scope) — both call `_rebind()` (`:236`) afterward to reconstruct order/SSN bookings consistent with
the rewound state, satisfying FS-106 §3 bullet 3's "applies identically to every connected client"
requirement: rewinding mutates the one shared `WorldState`/`EventLog`, not a per-tab view.

## 5. Session administration

`save_state()`/`from_state()` (`:430`, `:450`) are the save/resume mechanism FS-106 §3 bullet 4
treats as a facilitation concern (a multi-week course resuming an exercise) rather than generic
infrastructure; `add_tle(asset_id, line1, line2, owner, kind)` (`:286`) is the force-add path a
facilitator uses mid-exercise. (Session discovery/pop-out-layout-token routing live in
`session/inprocess.py`'s `list_sessions()` and the `ui_web` layer per `CLAUDE.md`'s multiplayer
workflow section — out of `manager.py`'s direct scope but consulted by the same dashboard.)

## 6. Red-doctrine-preset visibility and control

`RedDoctrine` (`redai.py:19`) reads `manager.ctx.red_doctrine_profile` (`:22`) — the profile
selection the dashboard exposes — and `step()` (`:32`) issues doctrine-flavored orders **through
the same `OrderSystem`/`issue_order()`** a human Red cell would use (`:44`, `:56`, `:62`): the
inline module docstring (`:3`-`:4`) is explicit that this is "fully constrained by windows, ROE,
and custody," not a privileged shortcut. Three presets are implemented — `russia_ew_first` (jam-led,
`:40`-`:46`), `china_integrated` (jam + cyber via `_first_vulnerable()`'s patch-state scan, `:48`-
`:58`, `:67`), and `generic` (cautious sensor-tasking only, `:60`-`:63`) — satisfying FS-106 §3
bullet 5's "visibility into which preset drives Red, ability to switch... mid-exercise" requirement:
`ctx.red_doctrine_profile` is a runtime-readable/settable field, not baked into a vignette at load
time only.

## 7. Mission-set sequencing and the assess beat

FS-106 §3 bullets 6-7 (mission-set/campaign sequencing visibility, cross-cell assess-beat view) are
satisfied by the same `get_godview()`/`objectives()` (`:560`) surface §2 documents — White's
dashboard is the one place both cells' objective state is visible simultaneously, which is what
"assess, viewed across both cells at once" (distinct from FS-105's per-cell plan/task beats)
concretely means in code: no separate cross-cell objective aggregation exists beyond reading
`objectives()` from the unfiltered `WorldState`.

## 8. Satisfying FS-106's capability requirements

Mapped one-by-one in §2 (god-view isolation), §3 (inject), §4 (clock), §5 (administration), §6
(Red doctrine), §7 (mission-set/assess visibility) above. The required authority-tier statement
(FS-106 §5, DOM-003 §8) holds: every mechanism cited here is additive to White's existing
`SessionManager` surface and none grants `get_view`/`get_scene` (the Red/Blue-facing paths) any
new ground-truth access.

## 9. Test coverage (existing)

`spacesim/tests/test_session.py` covers clock/rewind/undo/save-resume; Red-doctrine presets are
covered by their own test path; inject firing is covered alongside the inject-library tests. No
new tests are proposed by this package.

## 10. Related Topics

[FS-106](../features/FS-106-white-cell-dashboard.md) (the spec this documents), [IMP-107A](IMP-107A-after-action-review.md) (the AAR instrument this dashboard's
controls invoke), [`spacesim/session/manager.py`](../../spacesim/session/manager.py), [`spacesim/session/redai.py`](../../spacesim/session/redai.py).
