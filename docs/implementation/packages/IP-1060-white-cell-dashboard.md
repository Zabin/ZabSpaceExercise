# IP-1060 — White Cell Dashboard: Session/Inject/Clock Control Plane

> **Package ID:** IP-1060
> **Version:** 1.0
> **Status:** ✅ VERIFIED
> **Dependencies:** FS-106
> **Referenced By:** IP-1070 (the AAR instrument this dashboard's controls invoke), [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** the facilitation control surface a future authorized FS-108 (Inject Authoring, currently unauthorized) would extend
> **Feature Reference:** [FS-106 — White Cell Dashboard](../../features/FS-106-white-cell-dashboard.md)
> **Supersedes:** [`docs/implementations/IMP-106A-white-cell-dashboard.md`](../../implementations/IMP-106A-white-cell-dashboard.md)
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py), [`spacesim/session/redai.py`](../../../spacesim/session/redai.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

## Package ID

IP-1060

## Title

White Cell Dashboard — Session/Inject/Clock Control Plane

## Objective

Give the White Cell facilitator an unrestricted god-view (both cells' belief + ground truth,
without granting Red/Blue any new ground-truth access), inject authoring/scheduling against the
existing template library, single-point-of-authority clock control, session administration
(save/resume/discovery/pop-out), and Red-doctrine-preset visibility/control — every capability
tracing back to White Cell's role as instructional designer, not neutral referee.

**Situation: already implemented, tested, in production use.**

## Feature Reference

[FS-106 — White Cell Dashboard](../../features/FS-106-white-cell-dashboard.md)

## Requirements Covered

FS-106's "Requirements Implemented" field reports no explicit FR/NFR citation (documented gap).
Functional coverage per the RTM's `session/manager.py`/`session/redai.py` mapping:

| Req ID | Title (abridged) | How this package covers it |
|---|---|---|
| FR-4310 | Exclusive White Cell clock control | `set_clock()` (`manager.py:131`), enforced at the `SessionAPI` layer as a no-cell-argument, White-only endpoint |
| FR-4410 | Inject authoring/firing (immediate or scheduled) | `fire_inject()` (`:492`), `list_injects()` (`:425`) |
| FR-7210 | Save/resume | `save_state()`/`from_state()` (`:430`, `:450`) |
| FR-6310 | Server-authoritative lazy clock | `catch_up()`/`_catch_up_locked()` (`:206`, `:148`), `_wall_anchor`/`_sim_anchor`/`_rate`/`_clock_running` |
| FR-9110 | AI-Red substitution for unseated Red | `redai.py`'s `RedDoctrine.step()` issuing orders through the same `OrderSystem` a human uses |
| NFR-1300 | Sizing soft guideline / clock-lag watchdog | `_record_catch_up_lag()` (`:173`) |

## Architecture Components

- **C2 Session / Application Layer** — `SessionManager` (`manager.py`), `redai.py`.
- **C6 White Cell facilitator** — the sole consumer of this package's god-view/clock/inject/admin
  surface.

## Interfaces

**INT-0002** (White Cell Facilitator ↔ Operator Console, exercise control); **INT-0003** (in-app
scenario builder) — per the ICD and FS-106's verified Related Interfaces field.

## Files to Create

None — capability already implemented.

## Files to Modify

None — this package documents shipped code.

### Reference files

- `spacesim/session/manager.py` — `get_godview()` (`:554`), `get_view()`/`get_scene()` (`:520`,
  `:523`), `list_injects()` (`:425`), `fire_inject()` (`:492`), `set_clock()` (`:131`),
  `catch_up()`/`_catch_up_locked()` (`:206`, `:148`), `_record_catch_up_lag()` (`:173`),
  `clock_state()` (`:210`), `rewind_to()`/`undo_last()` (`:219`, `:229`), `_rebind()` (`:236`),
  `save_state()`/`from_state()` (`:430`, `:450`), `add_tle()` (`:286`), `objectives()` (`:560`).
- `spacesim/session/redai.py` — `RedDoctrine` (`:19`), `step()` (`:32`), the three doctrine presets
  (`russia_ew_first`, `china_integrated`, `generic`).
- `spacesim/session/inprocess.py` — `list_sessions()` (session discovery, out of `manager.py`'s
  direct scope but part of this dashboard's surface).

## Implementation Tasks

All **already complete**:

1. ✅ Implement `get_godview()` as a structurally separate method from `get_view()`/`get_scene()` —
   no code path lets a cell-scoped call return ground truth, and no cell argument makes
   `get_godview()`'s caller anything but White (enforced at `SessionAPI`).
2. ✅ Expose the five `inject_library.yaml` templates as editable-JSON + Now/+seconds/absolute-UTC
   scheduled data, resolving through one `fire_inject()` path regardless of scheduling mode.
3. ✅ Implement the server-authoritative lazy clock (`_wall_anchor`/`_sim_anchor`/`_rate`/
   `_clock_running`, guarded by the per-session lock) so clock state lives once, with no per-tab
   pacing to desynchronize, and a clock-lag watchdog surfaces real-hardware keep-up capability.
4. ✅ Implement `rewind_to()`/`undo_last()` with `_rebind()` reconstructing order/SSN bookings
   consistent with the rewound state.
5. ✅ Implement save/resume and TLE force-add as facilitation-scoped session-administration actions.
6. ✅ Implement `RedDoctrine` issuing orders through the same `OrderSystem.issue_order()` a human
   Red cell would use — no privileged shortcut — with the active preset runtime-readable/settable.

## Tests to Add

None — covered by `spacesim/tests/test_session.py` (clock/rewind/undo/save-resume), the Red-doctrine
preset test path, and the inject-library test suite.

## Documentation Updates

- Supersedes [`docs/implementations/IMP-106A-white-cell-dashboard.md`](../../implementations/IMP-106A-white-cell-dashboard.md).
- `ROADMAP.md` Implementation Packages theme updated.

## Definition of Done

- [x] No code path exists by which a Red/Blue-scoped call returns what `get_godview()` returns.
- [x] Inject firing has exactly one execution path regardless of scheduling mode.
- [x] Clock transitions apply identically to every connected client with no per-tab divergence.
- [x] Red-doctrine orders are fully constrained by windows/ROE/custody — no bypass of the ordinary
  `OrderSystem` gate.
- [x] Session save/resume round-trips without data loss.

## Verification Checklist

- [x] `manager.py:131,148,173,206,210,219,229,236,286,425,430,450,492,520,523,554,560` and
  `redai.py:19,32` read and confirmed against the current tree.
- [x] `spacesim/tests/test_session.py` present and green.
- [x] No FR/NFR explicitly cites FS-106 (confirmed absence) — recorded as a traceability gap.

## Dependencies

- **Upstream:** None — self-contained session-layer module (consumes engine state read-only for
  god-view/clock purposes).
- **Downstream:** IP-1070 (the AAR instrument this dashboard's White-only controls invoke).
- **Build-sequencing:** None — already shipped.

## Risks

- Composing multiple inject templates into a pre-scripted sequence ahead of a session is explicitly
  out of this package's scope — FS-106 §9 names it as not currently possible; treating it as in
  scope in a future change would be a silent scope addition requiring a dedicated Feature Spec
  (FS-108 or a new ID).
- Granting any capability to Red/Blue through this dashboard that provides indirect ground-truth
  access (even unintentionally, e.g., via a shared computed field) would compromise the fog-of-war
  boundary regardless of framing — the single most critical invariant for this feature.

## Rollback Considerations

Rollback surface: `spacesim/session/manager.py` (all cited methods) and `spacesim/session/redai.py`.
Clock-anchor fields and inject-queue state participate in the save/resume schema
(`save_state()`/`from_state()`); a revert requires re-verification against `test_session.py` and the
determinism property test before landing.
