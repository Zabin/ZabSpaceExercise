# IP-1110 — AI-Red Doctrine Automation

> **Package ID:** IP-1110
> **Version:** 1.0
> **Status:** ✅ VERIFIED
> **Dependencies:** FS-111
> **Referenced By:** IP-1060 (the facilitator-facing preset selector this mechanism serves), [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** Red-attributed Planned Activities, indistinguishable in the event log from human-issued ones
> **Feature Reference:** [FS-111 — AI-Red Doctrine Automation](../../features/FS-111-ai-red-doctrine-automation.md)
> **Supersedes:** none — new package, split out of [IP-1060](IP-1060-white-cell-dashboard.md) v1.0
> **Related Topics:** [`spacesim/session/redai.py`](../../../spacesim/session/redai.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*This package is **new**, split out of `IP-1060-white-cell-dashboard.md` v1.0 per
`docs/feature-planning/05-feature-review.md` Finding F-03, mirroring `FS-111`'s own split from
`FS-106` v1.0. The code citations below are not newly verified — they are the same `redai.py`
evidence `IP-1060` v1.0 (and its superseded predecessor, `IMP-106A`) already established,
reorganized under the Feature boundary FS-111 now owns.*

## Package ID

IP-1110

## Title

AI-Red Doctrine Automation

## Objective

Substitute for an unseated Red cell by generating Planned Activities consistent with a configured
doctrine preset, through the same command path a human Red operator would use.

**Situation: already implemented, tested, in production use.**

## Feature Reference

[FS-111 — AI-Red Doctrine Automation](../../features/FS-111-ai-red-doctrine-automation.md)

## Requirements Covered

| Req ID | Title (abridged) | How this package covers it |
|---|---|---|
| FR-9110 | AI-Red substitution for unseated Red | `RedDoctrine` (`redai.py:19`) reads `manager.ctx.red_doctrine_profile` (`:22`); `step()` (`:32`) issues doctrine-flavored orders **through the same `OrderSystem`/`issue_order()`** a human Red cell would use (`:44`, `:56`, `:62`) — the inline module docstring (`:3`-`:4`) is explicit this is "fully constrained by windows, ROE, and custody," not a privileged shortcut. Three presets: `russia_ew_first` (jam-led, `:40`-`:46`), `china_integrated` (jam + cyber via `_first_vulnerable()`, `:48`-`:58`, `:67`), `generic` (cautious sensor-tasking only, `:60`-`:63`). |

## Architecture Components

- **C1 Simulation Engine** — `OrderSystem`/`issue_order()` (`engine/orders.py`), the path AI-Red
  activities route through, identical to a human operator's.
- **C8 Red Cell (AI-Red)** — `RedDoctrine` (`redai.py`), the preset selection/generation logic.

## Interfaces

**INT-0008** (Session Layer → Simulation Engine, Clock/Scheduler/EventLog/`OrderSystem`) — the path
AI-Red-generated activities are submitted and executed through. **INT-0015** (Session Layer,
AI-Red/`redai.py` → Simulation Engine, `WorldState` direct read) — the documented, accepted direct
ground-truth read (ADR-0024) this package does not remediate.

## Files to Create

None — capability already implemented.

## Files to Modify

None — this package documents shipped code.

### Reference files

- `spacesim/session/redai.py` — `RedDoctrine` (`:19`), `manager.ctx.red_doctrine_profile` (`:22`),
  `step()` (`:32`), `russia_ew_first` (`:40`-`:46`), `china_integrated` + `_first_vulnerable()`
  (`:48`-`:58`, `:67`), `generic` (`:60`-`:63`), `issue_order()` call sites (`:44`, `:56`, `:62`).

## Implementation Tasks

All **already complete**:

1. ✅ Implement `RedDoctrine` issuing orders through the same `OrderSystem.issue_order()` a human
   Red cell would use — no privileged shortcut — with the active preset runtime-readable/settable
   via `manager.ctx.red_doctrine_profile`.
2. ✅ Implement three doctrine presets (`russia_ew_first`, `china_integrated`, `generic`) each
   consistent with its named doctrinal profile.
3. ✅ Confirm generated activities pass the same execute-time re-validation as human-issued ones
   (no AI-Red-specific bypass in `engine/orders.py`).

## Tests to Add

None — covered by the existing Red-doctrine preset test path.

## Documentation Updates

- Split out of [IP-1060](IP-1060-white-cell-dashboard.md) v1.0; see that package's own v2.0
  Documentation Updates note.
- `ROADMAP.md` and `00-master-build-plan.md` updated to add this package.

## Definition of Done

- [x] Red-doctrine orders are fully constrained by windows/ROE/custody — no bypass of the ordinary
  `OrderSystem` gate.
- [x] Generated activities are indistinguishable from human-issued ones in the event log.

## Verification Checklist

- [x] `redai.py:19,22,32,40-46,48-58,60-63,67` read and confirmed against the current tree.
- [x] Red-doctrine preset test path present and green.

## Dependencies

- **Upstream:** None beyond the engine's own `OrderSystem` (already shipped, out of this pass's
  package scope).
- **Downstream:** [IP-1060](IP-1060-white-cell-dashboard.md) (the facilitator-facing preset
  selector/hand-tuning control that drives this package's `red_doctrine_profile` field).
- **Build-sequencing:** None — already shipped.

## Risks

- **AI-Red's ground-truth-read asymmetry (ADR-0024, INT-0015) is this package's largest known
  limitation** — named repeatedly across the project's governance record (strategic review
  FC-02/GAP-08) as the highest-priority tracked gap; not remediated by this package.
- This package's split from IP-1060 v1.0 creates a cross-package seam: a future change to
  preset-selection UX must be coordinated with this package if it implies a change to the
  generation mechanism itself.

## Rollback Considerations

Rollback surface: `spacesim/session/redai.py` entirely. A revert requires re-verification against
the Red-doctrine preset test path and the determinism property test before landing, since AI-Red's
non-deterministic-looking preset logic must still enter the deterministic core only as ordered,
logged events (ADR-0030).
