# IP-1290 — Jamming-Delivery Degradation and Per-Effect-Class Detectability Settings

> **Package ID:** IP-1290
> **Version:** 1.0
> **Status:** 🟡 READY *(authorized 2026-09-27 by the project owner's direct instruction, MSTR-006 §3)*
> **Dependencies:** [FS-129](../../features/FS-129-jamming-delivery-and-effect-detectability.md)
> v1.0 (`FR-1440`/`FR-1450`), `engine/effects.py`/`engine/orders.py` (`IP-1051`/`IP-1010`/`IP-1020`,
> `VERIFIED`), [IP-1270](IP-1270-effect-authorization-gating-and-live-roe.md) (the shared
> effect-classification enumeration this package reuses — see Design Decisions)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md),
> [docs/pipeline/backlog.md](../../pipeline/backlog.md) `BL-0081` (item B15), `BL-0105` (the
> shared effect-classification taxonomy question — **resolved by `IP-1270`, reused here**)
> **Produces:** command/relay delivery-path degradation from a successful jam effect (`FR-1440`)
> and per-effect-class detectability/attribution-difficulty configuration (`FR-1450`), satisfying
> both in full
> **Feature Reference:** [FS-129 — Jamming-Delivery Degradation and Per-Effect-Class Detectability Settings](../../features/FS-129-jamming-delivery-and-effect-detectability.md)
> **Supersedes:** none — new package
> **Related Topics:** [`spacesim/engine/effects.py`](../../../spacesim/engine/effects.py),
> [`spacesim/engine/orders.py`](../../../spacesim/engine/orders.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package. This package's own Open Question (`BL-0105`) is resolved by
[IP-1270](IP-1270-effect-authorization-gating-and-live-roe.md), authored earlier in this same
batch — this package cites that resolution rather than re-deciding it, per the user-directed
batch order.*

## Package ID

IP-1290

## Title

Jamming-Delivery Degradation and Per-Effect-Class Detectability Settings

## Objective

Extend a successful uplink/crosslink jam's consequences to also degrade a scheduled command's
delivery (in addition to its existing telemetry-signature effect), and let each effect class carry
its own configurable detectability/attribution-difficulty setting, falling back to the existing
single fixed setting where undeclared.

> **This package is authorized for coding.** Per MSTR-006 §3, the project owner gave explicit
> go-ahead 2026-09-27 (batched with five sibling packages from the same Should-tier intake round).

## Feature Reference

[FS-129 — Jamming-Delivery Degradation and Per-Effect-Class Detectability Settings](../../features/FS-129-jamming-delivery-and-effect-detectability.md)

## Requirements Covered

| Req ID | Title (abridged) | How this package's design covers it |
|---|---|---|
| FR-1440 | Uplink/crosslink jamming degrades command and relay delivery paths | `engine/orders.py`'s `FR-3410` execute-time re-validation gains a check of `engine/effects.py`'s existing `is_link_denied` against an active, successfully resolved jam effect's footprint at the command's scheduled delivery time; a covered command fails or is delayed. |
| FR-1450 | Per-effect-class detectability and attribution-difficulty configuration | A vignette-declared per-effect-class (per [IP-1270](IP-1270-effect-authorization-gating-and-live-roe.md)'s shared enumeration — effect action type crossed with five-D's reversibility category) detectability/attribution-difficulty setting, consulted at effect resolution; an undeclared class falls back to `FR-1410`'s existing single fixed setting. |

## Architecture Components

- **C1 Simulation Engine** (`engine/effects.py`) — owns `is_link_denied` and the five-D's
  effect-resolution mechanism (`FR-1410`); extended so a jam effect's resolution is consulted by the
  delivery-path check and so per-effect-class detectability/attribution settings are read where
  declared.
- **C1 Simulation Engine** (`engine/orders.py`) — owns `FR-3410`'s execute-time re-validation;
  extended to consult the active-jam-footprint check for a command's delivery path.
- **C5 Content & Data** (`content/vignette.py`) — owns the vignette-declared per-effect-class
  detectability/attribution configuration schema, additive.

## Interfaces

`INT-0008` (SessionManager → Engine Clock/Scheduler/EventLog/OrderSystem) — both the delivery-path
check and the per-class detectability read operate through this existing interface; no new access
channel, per `ADR-0011`'s existing six-channel model.

## Design Decisions (reusing FS-127/IP-1270's resolution)

1. **Open Question (`BL-0105`) — resolved by [IP-1270](IP-1270-effect-authorization-gating-and-live-roe.md)
   Design Decision 1, reused verbatim here, not re-derived.** The shared effect-classification
   enumeration is: effect action type (`jam`/`engage`/`observe`/`maneuver`/`downlink`/`cyber`/
   `command`) crossed with the existing five-D's reversibility category
   (`deceive`/`disrupt`/`deny`/`degrade`/`destroy`). `FR-1450`'s per-effect-class detectability/
   attribution configuration is declared against this same enumeration — an implementer must read
   `IP-1270`'s actual landed schema (not re-guess the shape) before writing this package's own
   configuration parsing, so the two mechanisms consume one shared vocabulary, not two independently
   maintained ones.

## Files to Create

None.

## Files to Modify

- `spacesim/engine/effects.py` — `is_link_denied` consulted by a new delivery-path check (see
  `orders.py` below); a new per-effect-class detectability/attribution lookup, keyed by the shared
  enumeration (Design Decision 1), consulted at effect resolution — falling back to `FR-1410`'s
  existing single fixed setting when the resolving effect's class has no declared entry.
- `spacesim/engine/orders.py` — `OrderSystem`'s `FR-3410` execute-time re-validation gains a check:
  for a scheduled command, is there an active, successfully resolved uplink/crosslink jam effect
  whose footprint covers the command's delivery path at its scheduled execution time? If so, the
  command fails delivery or is delayed (recorded in the `EventLog`).
- `spacesim/content/vignette.py` — a new additive effect-template field for the per-effect-class
  detectability/attribution configuration, keyed by [IP-1270](IP-1270-effect-authorization-gating-and-live-roe.md)'s
  shared enumeration — **must be read directly from that package's actual landed schema at
  implementation time**, not re-specified independently here.

## Implementation Tasks

1. **Before any other task, read `IP-1270`'s actual landed effect-classification schema directly
   from the shipped code** (assuming it has been implemented; if not yet implemented, coordinate
   sequencing per Dependencies below) — confirm the exact field names/shape this package's own
   configuration parsing must match.
2. Write a failing test asserting a command whose delivery path is covered by an active jam fails or
   is delayed at execute-time re-validation, before adding the delivery-path check.
3. Add the delivery-path check to `OrderSystem`'s `FR-3410` re-validation, consulting
   `is_link_denied`.
4. Write a failing test asserting a command not covered by an active jam is unaffected, regression-
   only.
5. Write a failing test asserting two effect classes with distinct configured detectability/
   attribution settings resolve independently of each other and of the existing single fixed
   setting, before adding the per-class lookup.
6. Add the per-effect-class detectability/attribution lookup and fallback to `effects.py`.
7. Re-run the full existing suite; confirm zero regressions to any existing jam/effect-resolution
   test.

## Tests to Add

- `spacesim/tests/test_orders.py` (or `test_effects.py`) — jam-covers-delivery-path failure/delay;
  no-active-jam regression.
- `spacesim/tests/test_effects.py` — per-effect-class detectability/attribution resolution,
  parametrized over declared vs. undeclared classes.

The two permanent gates (`spacesim/tests/test_determinism.py`, `spacesim/tests/test_import_guard.py`)
must be re-run green — both checks are deterministic reads of existing/declared state, no
wall-clock read or global RNG use introduced.

## Documentation Updates

- `CLAUDE.md` Code Map — `engine/effects.py`, `engine/orders.py` entries each gain a one-line note.
- `docs/requirements/03-requirements-traceability-matrix.md` — `FR-1440`/`FR-1450` rows' `Impl.
  Package`/`Test` cells updated from `UNASSIGNED` to `IP-1290`/the named test files.
- `docs/features/FS-129-jamming-delivery-and-effect-detectability.md` — `Referenced By` metadata
  gains this package's link.
- `docs/pipeline/backlog.md` — `BL-0105` confirmed `DONE` (already flipped by `IP-1270`; this
  package's own entry note references that resolution rather than re-closing it).

## Definition of Done

- [ ] A command covered by an active jam fails or is delayed at execute-time re-validation; an
  uncovered command is unaffected.
- [ ] Two effect classes with distinct configured settings resolve independently; an undeclared
  class falls back to the existing fixed setting.
- [ ] This package's configuration schema matches `IP-1270`'s actual landed enumeration exactly (not
  a re-derived guess).
- [ ] Full existing test suite green, zero regressions, both permanent gates green.

## Verification Checklist

*(To be executed by `09-package-verification` once this package reaches `COMPLETE`.)*

- [ ] Every new test named above exists and is green.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green.
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green.
- [ ] Independently confirm, by reading both packages' shipped code, that this package's
  effect-classification schema is identical in shape to `IP-1270`'s — not two independently
  evolved copies.

## Dependencies

- **Upstream:** [FS-129](../../features/FS-129-jamming-delivery-and-effect-detectability.md) v1.0
  (approved, `✅ Ready for implementation planning`); `FR-1410` (`IP-1051`, `VERIFIED`); `FR-3410`
  (`IP-1010`/`IP-1020`, `VERIFIED`); **[IP-1270](IP-1270-effect-authorization-gating-and-live-roe.md)
  — this package's per-effect-class configuration schema must match `IP-1270`'s actual landed
  enumeration; if `IP-1270` has not yet reached `COMPLETE` when this package begins
  `08-code-implementation`, its own package document's Design Decision 1 text (above) is the
  interim source of truth, but the shipped schema must still be re-confirmed once `IP-1270` lands.**
- **Downstream:** none.
- **Build-sequencing:** should be sequenced after `IP-1270`, or the two coordinated closely.

## Risks

- **Coordination risk with `IP-1270` (the dominant risk for this package).** If this package is
  implemented before `IP-1270` lands, or without re-reading `IP-1270`'s actual shipped schema, the
  two mechanisms could drift apart despite both packages' shared-enumeration intent.

## Rollback Considerations

Both mechanisms are additive to existing `engine/effects.py`/`engine/orders.py` behavior;
reverting the delivery-path check and the per-class detectability lookup to their prior absence
fully removes this package's capability with no data-migration concern — no vignette shipped before
this package declares a per-effect-class detectability setting.
