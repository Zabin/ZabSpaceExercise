# IP-1060 — White Cell Dashboard: God-View, Inject, Clock-Authority Trigger & Adjudication

> **Package ID:** IP-1060
> **Version:** 2.0 — narrowed to match FS-106 v2.0
> **Status:** ✅ VERIFIED
> **Dependencies:** FS-106
> **Referenced By:** IP-1070 (the AAR instrument this dashboard's controls invoke), IP-1090
> (the multiplayer transport this dashboard's clock/session-admin controls trigger), IP-1100
> (the save/resume mechanism this dashboard's admin panel triggers), IP-1110 (the AI-Red mechanism
> this dashboard's preset selector controls), [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** the facilitation control surface a future authorized FS-108 (Inject Authoring, currently unauthorized) would extend
> **Feature Reference:** [FS-106 — White Cell Dashboard](../../features/FS-106-white-cell-dashboard.md) (v2.0)
> **Supersedes:** [`docs/implementations/IMP-106A-white-cell-dashboard.md`](../../implementations/IMP-106A-white-cell-dashboard.md)
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py), [`spacesim/session/redai.py`](../../../spacesim/session/redai.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Version 2.0 narrows this package's scope to match `FS-106` v2.0, per `docs/feature-planning/
05-feature-review.md` Finding F-03: the prior v1.0 draft covered the entire pre-split FS-106
surface (god-view, inject, clock, session admin, Red-doctrine). The multiplayer lazy-clock/locking
mechanism, save/resume, and AI-Red doctrine automation are now covered by their own sibling
packages — [IP-1090](IP-1090-multiplayer-session-transport.md), [IP-1100](IP-1100-save-and-resume.md),
[IP-1110](IP-1110-ai-red-doctrine-automation.md) — reusing the same verified code citations this
package's v1.0 draft (and its superseded predecessor, `IMP-106A`) already established, reorganized
along the new Feature boundaries rather than re-verified from scratch.*

## Package ID

IP-1060

## Title

White Cell Dashboard — God-View, Inject, Clock-Authority Trigger & Manual Adjudication

## Objective

Give the White Cell facilitator an unrestricted god-view (both cells' belief + ground truth,
without granting Red/Blue any new ground-truth access), inject authoring/scheduling against the
existing template library, the White-only trigger surface for clock/pacing and rewind/undo/branch
controls, and manual adjudication (no automated scoring, live parameter adjustment) — every
capability tracing back to White Cell's role as instructional designer, not neutral referee.

**Situation: already implemented, tested, in production use.**

## Feature Reference

[FS-106 — White Cell Dashboard](../../features/FS-106-white-cell-dashboard.md) (v2.0)

## Requirements Covered

| Req ID | Title (abridged) | How this package covers it |
|---|---|---|
| FR-4310 | Exclusive White Cell clock control (trigger surface) | `set_clock()` (`manager.py:131`), enforced at the `SessionAPI` layer as a no-cell-argument, White-only endpoint. The multi-client propagation this triggers is [IP-1090](IP-1090-multiplayer-session-transport.md)'s `catch_up()`/`_catch_up_locked()`, not this package's. |
| FR-4410 | Inject authoring/firing (immediate or scheduled) | `fire_inject()` (`:492`), `list_injects()` (`:425`), resolving to one scheduled `_h_inject` event (`:564`) and `_inject_effects()` (`:511`) regardless of scheduling mode. |
| FR-4610 | God-view with per-cell view-as | `get_godview()` (`:554`) — deliberately a **separate** method from `get_view(cell)`/`get_scene(cell)` (`:520`, `:523`), which route through `CellController`'s fog-of-war filtering; no code path lets a cell-scoped call return what `get_godview()` returns. |
| FR-4710, FR-4720 | Manual adjudication (no automated scoring; live parameter adjustment) | No scoring/win-loss field exists on any outbound interface (inspection); live parameter adjustment is the same class of mechanism as `set_clock()`'s runtime-settable fields. |

`rewind_to()`/`undo_last()` (`manager.py:219`, `:229`) — the AAR-adjacent trigger surface FS-106 v2.0
names as in scope (the replay/scrub *instrument* itself is [IP-1070](IP-1070-after-action-review.md)) —
both call `_rebind()` (`:236`) afterward to reconstruct order/SSN bookings consistent with the
rewound state. `objectives()` (`:560`) is the cross-cell assess-beat surface FS-106's User Workflows
describe (research-grounded, not itself FR-traced — see FS-106 v2.0's own Open Questions).

**Removed from this package's scope in v2.0** (now covered by sibling packages, same underlying
code, cited there instead): `catch_up()`/`_catch_up_locked()`, `_wall_anchor`/`_sim_anchor`/`_rate`/
`_clock_running`, `_record_catch_up_lag()` → [IP-1090](IP-1090-multiplayer-session-transport.md);
`save_state()`/`from_state()`, `add_tle()` → [IP-1100](IP-1100-save-and-resume.md); `RedDoctrine`/
`step()`/doctrine presets (`redai.py`) → [IP-1110](IP-1110-ai-red-doctrine-automation.md).

## Architecture Components

- **C2 Session / Application Layer** — `SessionManager` (`manager.py`), the god-view/inject/
  clock-trigger/adjudication methods specifically.
- **C6 White Cell facilitator** — the sole consumer of this package's surface.

## Interfaces

**INT-0002** (White Cell Facilitator ↔ Operator Console, exercise control) — per the ICD and
FS-106 v2.0's verified Related Interfaces field. **INT-0003 removed in v2.0** (see FS-106 v2.0's
own Interfaces Used correction — this package's actual scope never touched the in-app scenario
builder).

## Files to Create

None — capability already implemented.

## Files to Modify

None — this package documents shipped code.

### Reference files

- `spacesim/session/manager.py` — `get_godview()` (`:554`), `get_view()`/`get_scene()` (`:520`,
  `:523`), `list_injects()` (`:425`), `fire_inject()` (`:492`), `_h_inject` (`:564`),
  `_inject_effects()` (`:511`), `set_clock()` (`:131`), `clock_state()` (`:210`),
  `rewind_to()`/`undo_last()` (`:219`, `:229`), `_rebind()` (`:236`), `objectives()` (`:560`).

## Implementation Tasks

All **already complete**:

1. ✅ Implement `get_godview()` as a structurally separate method from `get_view()`/`get_scene()` —
   no code path lets a cell-scoped call return ground truth, and no cell argument makes
   `get_godview()`'s caller anything but White (enforced at `SessionAPI`).
2. ✅ Expose the five `inject_library.yaml` templates as editable-JSON + Now/+seconds/absolute-UTC
   scheduled data, resolving through one `fire_inject()` path regardless of scheduling mode.
3. ✅ Implement `set_clock()` as the sole White-only entry point for clock-control requests, and
   `rewind_to()`/`undo_last()` with `_rebind()` reconstructing order/SSN bookings consistent with
   the rewound state.
4. ✅ Confirm no outbound interface returns a computed score/win-loss field (inspection).

## Tests to Add

None — covered by `spacesim/tests/test_session.py` (clock-trigger/rewind/undo) and the
inject-library test suite.

## Documentation Updates

- Supersedes [`docs/implementations/IMP-106A-white-cell-dashboard.md`](../../implementations/IMP-106A-white-cell-dashboard.md)
  (unchanged from v1.0; that document now additionally carries a forward-pointer note to the three
  new sibling packages, per its own "Superseded" banner's maintenance rule).
- `ROADMAP.md` Implementation Packages theme updated for the v2.0 narrowing and the three new
  sibling packages.
- `docs/implementation/00-master-build-plan.md` updated: package count, dependency graph, and Wave
  1 parallel-opportunity list now include IP-1090/IP-1100/IP-1110.

## Definition of Done

- [x] No code path exists by which a Red/Blue-scoped call returns what `get_godview()` returns.
- [x] Inject firing has exactly one execution path regardless of scheduling mode.
- [x] Clock-control-trigger requests are accepted only from White Cell.
- [x] No outbound interface returns a computed score/win-loss field.

## Verification Checklist

- [x] `manager.py:131,210,219,229,236,425,492,511,520,523,554,560,564` read and confirmed against
  the current tree.
- [x] `spacesim/tests/test_session.py` present and green.
- [x] FR-4310/FR-4410/FR-4610/FR-4710/FR-4720 citations confirmed against FS-106 v2.0's own
  `Requirements Implemented` field (closing part of Finding F-06's traceability gap for these five
  leaves specifically).

## Dependencies

- **Upstream:** None — self-contained session-layer module (consumes engine state read-only for
  god-view/clock-trigger purposes).
- **Downstream:** IP-1070 (the AAR instrument this dashboard's White-only controls invoke).
- **Build-sequencing:** None — already shipped.

## Risks

- Composing multiple inject templates into a pre-scripted sequence ahead of a session is explicitly
  out of this package's scope — FS-106 §9 (DOM-003 §9) names it as not currently possible; treating
  it as in scope in a future change would be a silent scope addition requiring a dedicated Feature
  Spec (FS-108 or a new ID).
- Granting any capability to Red/Blue through this dashboard that provides indirect ground-truth
  access would compromise the fog-of-war boundary regardless of framing.
- **This v2.0 narrowing introduces a cross-package seam that did not exist in v1.0.** A future
  change to clock-control authority now requires coordinated updates to this package *and*
  IP-1090; the two must be kept in sync explicitly.

## Rollback Considerations

Rollback surface: `spacesim/session/manager.py`'s god-view/inject/clock-trigger/adjudication
methods specifically (see Reference files) — no longer the whole file's clock-anchor/save-resume
surface, which now belongs to IP-1090/IP-1100's own Rollback Considerations. A revert requires
re-verification against `test_session.py` and the determinism property test before landing.
