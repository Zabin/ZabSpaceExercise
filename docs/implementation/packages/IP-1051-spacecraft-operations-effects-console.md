# IP-1051 — Spacecraft Operations: Effect Resolution & Console UX

> **Package ID:** IP-1051
> **Version:** 1.0
> **Status:** ✅ VERIFIED
> **Dependencies:** FS-105 (§3.2, §3.3, §4), IP-1030 (custody/weapons-quality gate), IP-1010 (kinetic consequence preview parity)
> **Referenced By:** IP-1050 (sibling package, bus/payload command & telemetry), [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** the executed-effect surface IP-1070 replays and IP-2010 assesses
> **Feature Reference:** [FS-105 — Spacecraft Operations](../../features/FS-105-spacecraft-operations.md) (§3.2, §3.3, §4)
> **Supersedes:** [`docs/implementations/IMP-105B-spacecraft-operations-effects-console.md`](../../implementations/IMP-105B-spacecraft-operations-effects-console.md)
> **Related Topics:** [`spacesim/engine/effects.py`](../../../spacesim/engine/effects.py), [`spacesim/engine/jam.py`](../../../spacesim/engine/jam.py), [`spacesim/engine/engage.py`](../../../spacesim/engine/engage.py), [`spacesim/engine/cyber.py`](../../../spacesim/engine/cyber.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

## Package ID

IP-1051

## Title

Spacecraft Operations — Effect Resolution & Console UX

## Objective

Resolve all five counterspace effect categories (EW/jam, cyber, kinetic/DE, plus maneuver and
downlink as the non-attack windowed actions) through one shared `EffectInstance`/`EffectOutcome`
model with explicit per-category tradeoff surfaces (jam modulation, cyber vector/posture, kinetic
Pₖ/debris), the consequence-confirm pattern for irreversible actions, and defender-side modifiers
that make ROE/defensive posture genuinely consequential rather than decorative.

Second of FS-105's two lettered packages (companion to IP-1050, which covers §3.1).

**Situation: already implemented, tested, in production use.**

## Feature Reference

[FS-105 — Spacecraft Operations](../../features/FS-105-spacecraft-operations.md) §3.2, §3.3, §4

## Requirements Covered

FS-105's "Requirements Implemented" field reports no explicit FR/NFR citation (documented gap).
Functional coverage per the RTM's `engine/effects.py`/`engine/cyber.py` mapping:

| Req ID | Title (abridged) | How this package covers it |
|---|---|---|
| FR-1410 | Five-D's effect resolution with reversibility/attribution/debris | `EffectInstance`/`EffectOutcome` (`effects.py:35,60`), `ModerateEffectResolver.resolve()` (`:103`) |
| FR-1420 | Cyber resolves outside the access-window gate | `_plan_cyber` sets `earliest_window = None` (`orders.py:575`); `cyber.py`'s `effective_success()`/`attribution_score()` (`:65`,`:75`) |
| FR-1520 | Weapons-quality track gate (engagement) | Consumed transitively via IP-1030's gate at `orders.py:349` before any kinetic/DE effect resolves |
| FR-3410 | Execute-time re-validation | `_h_effect` (`orders.py:623`) is the single dispatch point for every windowed effect category |

## Architecture Components

- **C1 Simulation Engine** — `engine/effects.py` (`EffectInstance`/`EffectResolver`), `engine/jam.py`,
  `engine/engage.py`, `engine/cyber.py`, `orders.py:_h_effect`/`_plan_cyber`.
- **C2 Session / Application Layer** — `InProcessSession.preview_consequence()` (kinetic-consequence
  pre-commit parity, shared with IP-1010).

## Interfaces

**INT-0004** (Blue/Red Cell Operator ↔ Operator Console); **INT-0008** (SessionManager → Simulation
Engine Clock/Scheduler/EventLog/OrderSystem) — per the ICD and FS-105's verified Related Interfaces
field.

## Files to Create

None — capability already implemented.

## Files to Modify

None — this package documents shipped code.

### Reference files

- `spacesim/engine/effects.py` — `EffectInstance` (`:35`), `EffectOutcome` (`:60`),
  `EffectResolver`/`ModerateEffectResolver` (`:83-84`, `:103`), `_effective_probability()` (`:168`),
  `_victim_cell()` (`:202`), `is_link_denied()`/`is_link_spoofed()` (`:207`, `:214`).
- `spacesim/engine/jam.py` — `effective_radius_km()` (`:57`), `effective_success_prob()` (`:69`),
  `power_draw_w()` (`:111`), `available_modulations()` (`:117`), `jam_footprint_polygon()` (`:87`).
- `spacesim/engine/engage.py` — `kill_probability()` (`:62`), `kill_probability_from_class()`
  (`:124`), `debris_cone_estimate()` (`:162`).
- `spacesim/engine/cyber.py` — `effective_success()` (`:65`), `attribution_score()` (`:75`),
  `available_vectors()`/`available_payloads()` (`:94`, `:98`).
- `spacesim/engine/orders.py` — `_h_effect` (`:623`), `_plan_cyber` (`:573`),
  `_FREQ_HOP_RESIDUAL`/`_EVASION_RESIDUAL` (`:89-100`), `world.consequences` append (`:635-636`).

## Implementation Tasks

All **already complete**:

1. ✅ Implement `EffectInstance`/`EffectOutcome` as the single typed record every effect category
   populates, dispatched through one handler (`_h_effect`) so the console can render all five
   categories through one history view.
2. ✅ Implement per-category tradeoff surfaces: jam modulation (barrage/spot/sweep/deceptive) moving
   effectiveness/footprint/power together; cyber vector/payload/posture/dwell inputs; kinetic Pₖ/
   debris-cone math shared identically between pre-commit preview and post-commit resolution.
3. ✅ Implement the cyber non-windowed exception structurally (`earliest_window = None`), not as a
   cosmetic console flag.
4. ✅ Wire defender-side modifiers (`_FREQ_HOP_RESIDUAL`, `_EVASION_RESIDUAL`) into the same
   probability math the attacker's effect resolves against, so defensive posture is genuinely
   consequential.
5. ✅ Implement `political_consequence` side effects appended to `world.consequences` as the
   source-of-truth for escalation/ROE framing — not a UI-side label.
6. ✅ Enforce the fog-of-war boundary (`_victim_cell()`, `is_link_denied()`/`is_link_spoofed()`) so a
   cell's console only ever renders effects scoped to itself.

## Tests to Add

None — covered by the effect-resolution, jam, engage, and cyber test suites, and wherever
kinetic-consequence preview/commit parity is exercised in the same test.

## Documentation Updates

- Supersedes [`docs/implementations/IMP-105B-spacecraft-operations-effects-console.md`](../../implementations/IMP-105B-spacecraft-operations-effects-console.md).
- `ROADMAP.md` Implementation Packages theme updated.

## Definition of Done

- [x] All five effect categories resolve through one `EffectInstance`/`EffectOutcome` model.
- [x] EW/jam, cyber, and kinetic/DE each expose their real tradeoff explicitly (no single
  undifferentiated action button).
- [x] Cyber's non-windowed resolution is structurally, not just visually, distinct.
- [x] Kinetic/DE consequence preview and post-commit resolution share identical math (no divergence
  possible between the confirm dialog and the actual outcome).
- [x] Defensive verbs measurably change attacker success probability, not merely display a defense
  indicator.
- [x] `world.consequences` is the sole source of truth for escalation/ROE framing.

## Verification Checklist

- [x] `effects.py:35,60,83-84,103,168,202,207,214`; `jam.py:57,69,87,111,117`; `engage.py:62,124,162`;
  `cyber.py:65,75,94,98`; `orders.py:89-100,573,623,635-636` read and confirmed against the current
  tree.
- [x] Effect-resolution, jam, engage, and cyber test suites present and green.
- [x] No FR/NFR explicitly cites FS-105 (confirmed absence) — recorded as a traceability gap.

## Dependencies

- **Upstream:** IP-1030 (weapons-quality gate consulted before kinetic/DE effects), IP-1010 (shared
  kinetic-consequence preview math).
- **Downstream:** IP-1070 (AAR replays effect history), IP-2010 (assessment reads effect/consequence
  data).
- **Build-sequencing:** None — already shipped; sequenced alongside IP-1050 as FS-105's two lettered
  sub-packages.

## Risks

- A new effect category or fidelity tier added without its own domain/research grounding would
  create an ungrounded capability claim — named explicitly as a non-goal/risk in FS-105.
- The panel-manager contract (every new console panel a first-class citizen: close/float/resize/
  reset-to-dock) is asserted as a requirement on any future console work but is not independently
  verifiable from `engine/` code alone — flagged in the source IMP-105B as a constraint for future
  console implementers, carried forward here unchanged.

## Rollback Considerations

Rollback surface: `spacesim/engine/effects.py`, `engine/jam.py`, `engine/engage.py`,
`engine/cyber.py`, and the `_h_effect`/`_plan_cyber` call sites in `spacesim/engine/orders.py`.
`world.consequences` and `EffectInstance`/`EffectOutcome` participate in the eventlog/save schema; a
revert requires re-verification against the effect-resolution test suites and the determinism
property test before landing.
