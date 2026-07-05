> **Document ID:** ADS-5100B
> **Version:** 1.0
> **Status:** ✅ Authored
> **Dependencies:** [GDS-04](04-domain-model.md) (Domain Model — `Asset`/`BusState`/`PayloadState`),
> [R109](../research/encyclopedia/R109-sensor-operations.md),
> [R110](../research/encyclopedia/R110-communications.md),
> [R111](../research/encyclopedia/R111-power-and-thermal-operations.md),
> [R112](../research/encyclopedia/R112-propulsion-and-maneuver-planning.md),
> [R134](../research/encyclopedia/R134-pnt-warfare-and-navigation-denial-operations.md),
> [R137](../research/encyclopedia/R137-bus-and-payload-parameter-catalog.md),
> `docs/pipeline/backlog.md` `BL-0053`
> **Referenced By:** [ADS-5100A](ADS-5100A-vignette-creator-session-and-ui.md) (the UI surfaces
> that consume the schemas/enforcement this document specifies)
> **Produces:** the eventual Vignette Creator Feature Specification's Domain Model/Functional
> Requirements sections for typed parameters and per-cell ROE
> **Feature Mapping:** `FEAT-5100`, `BL-0052`, `FS-101`/`FS-102` (the existing ROE-check owners this
> document extends, not replaces)
> **Related Topics:** [ADS-5100A](ADS-5100A-vignette-creator-session-and-ui.md),
> [ADS-3500](ADS-3500-role-scoped-command-enforcement.md) (a structurally similar precedent for
> extending an existing global-ish mechanism to be cell/role-aware without breaking prior behavior)

[↑ Architecture index](INDEX.md) · [Docs index](../INDEX.md)

# ADS-5100B — Vignette Creator: Typed Parameter Schemas & Per-Cell ROE Enforcement

*Workflow B (per-cluster synthesis), sibling to [ADS-5100A](ADS-5100A-vignette-creator-session-and-ui.md).
This document covers two Domain Model extensions the Vignette Creator's UI exposes but which are
independently significant architectural decisions, each touching already-shipped, `VERIFIED`
Domain Model territory rather than being purely new-feature scope: (1) typed per-payload-type and
per-bus-subsystem parameter sub-schemas, replacing today's untyped `dict` bag; (2) real per-cell
ROE enforcement, replacing today's single global gate. Both were decided directly by the project
owner this session (`AskUserQuestion`); this document works out their design consequences.*

## 1. Executive Design Overview

Two of the project owner's four already-made decisions extend the engine's Domain Model beyond
what `FEAT-5100`'s original catalog entry scoped: typed payload/bus parameters (so "effective range
of payload" and "fuel level" are named, validated fields instead of an opaque dict), and real
per-cell ROE (so "ROE selectors per cell" in the Creator's UI actually gate per-cell behavior
rather than decorating a single global flag). The single biggest design tension this document
resolves: **both extensions must be additive to already-`VERIFIED` behavior** — 19 shipped
vignettes and `FS-101`/`FS-102`/`FS-105`'s existing passing test suites must continue to work
unchanged.

## 2. System Architecture

- **C1 Simulation Engine** — `engine/bus.py`'s `PayloadState` gains typed per-payload-type
  parameter support (mechanism TBD, §9 Open Question 1); `engine/orders.py`'s ROE gate
  (`self.roe.get("kinetic_authorized"/"cyber_authorized")`, currently one global dict checked
  regardless of `order.cell`) becomes cell-keyed.
- **C5 Content & Data** — `content/vignette.py`'s `Vignette` schema gains typed initial-parameter
  support per payload type, and its ROE construction (currently two `Parameter` entries,
  `red_kinetic_authorized`/`cyber_authorized`, folded into one global `roe` dict at
  `VignetteContext` build time) gains a per-cell shape.
- **C4 Operator Console** (the Vignette Creator, [ADS-5100A](ADS-5100A-vignette-creator-session-and-ui.md))
  is the consumer: its typed parameter forms bind to the schemas this document specifies; its ROE
  selectors bind to the per-cell structure this document specifies.
- **C2 Session Layer** — unaffected; ROE resolution happens at `OrderSystem` construction/read time
  (`engine/orders.py`), not the session layer.

## 3. Domain Model

### 3.1 Typed payload/bus parameter sub-schemas

Per-payload-type sub-schemas (one per `satcom`/`isr_eo`/`isr_sar`/`sigint`/`sda`/`weather`/`pnt`/`mw`),
each with named, validated fields grounded in [R137](../research/encyclopedia/R137-bus-and-payload-parameter-catalog.md)'s
completeness catalog and the range research it cross-references — this document does not re-derive
those ranges, only commits to the shape:

- `isr_eo`/`isr_sar`/`sda` sub-schemas mirror the existing `BEAM_MODES` mode-level fields (`swath_km`,
  `resolution_m`, `power_factor`, `duty_cycle`, `gain_factor`) already grounded in
  [R109](../research/encyclopedia/R109-sensor-operations.md) — these three are the least-risky to
  type, since the engine already parameterizes them per mode.
- `satcom`'s sub-schema centers on `data_rate_kbps` (bus-level, already live), grounded in
  [R110](../research/encyclopedia/R110-communications.md)'s bandwidth-by-class ranges.
- `pnt`'s sub-schema centers on a baseline accuracy figure, grounded in
  [R134](../research/encyclopedia/R134-pnt-warfare-and-navigation-denial-operations.md).
- `weather`/`mw` sub-schemas **cannot be considered fully wired until `BL-0053` lands** — the engine
  has zero `BEAM_MODES` entries for either type today (`beam_params()` silently falls back to
  generic EO numbers), so a typed schema for these two, absent that engine change, would let a
  vignette author configure a parameter the engine doesn't honor. This document commits to the
  *schema shape* for both (per [R109](../research/encyclopedia/R109-sensor-operations.md)'s own
  weather-imager-resolution/revisit and missile-warning scan-vs-stare framing) but flags the wiring
  itself as a hard precondition — see Constraints/Risks.
- The typed **bus** power sub-schema exposes `charge_rate_per_s`/`drain_rate_per_s` (already-live
  fields), **not** `AssetResources.power_w`, per [R111](../research/encyclopedia/R111-power-and-thermal-operations.md)'s
  explicit dead-field finding — exposing a field `advance_bus` never reads would be worse than not
  exposing a power parameter at all.
- The typed **bus** propulsion sub-schema exposes `AssetResources.delta_v_ms` (the "fuel level" the
  project owner named explicitly), grounded in
  [R112](../research/encyclopedia/R112-propulsion-and-maneuver-planning.md)'s total-Δv-budget-by-class
  table.

### 3.2 Per-cell ROE

Today's single `VignetteContext.roe: dict` (built from two global `Parameter`s,
`red_kinetic_authorized`/`cyber_authorized`, despite the "red_" naming applying globally regardless
of which cell issues the order — confirmed directly against `engine/orders.py`'s
`self.roe.get(...)` calls, which never reference `order.cell`) becomes a **cell-keyed structure**:
`{"blue": {"kinetic_authorized": bool, "cyber_authorized": bool}, "red": {...}}`. `OrderSystem`'s
ROE check resolves against `self.roe.get(order.cell, {})` instead of the flat dict. A vignette
declaring only the old two `Parameter`s (all 19 shipped vignettes) must resolve to **both cells
sharing the same values** — the current, implicit behavior — so no existing vignette's behavior
changes.

## 4. User Stories

- *As White Cell, I set Blue's kinetic ROE to "not authorized" and Red's to "authorized" in the
  Vignette Creator, start the exercise, and confirm a Blue kinetic order is rejected while an
  otherwise-identical Red order succeeds.*
- *As White Cell, I open an ISR-EO asset's payload parameter form and see fields specific to EO
  sensors (resolution, swath), and a SATCOM asset's form shows bandwidth fields instead — not the
  same generic key-value bag for both.*
- *As White Cell, I set a new satellite's fuel level using a realistic default informed by its
  mission class, rather than guessing a raw number with no anchor.*
- *As White Cell authoring a vignette with weather or missile-warning payloads, I understand (via
  the Creator's own UI, once `BL-0053` lands) that these payload types' parameters are honored by
  the engine the same way ISR/SATCOM parameters are — not a silently-ignored form field.*

## 5. Functional Requirements

- The system shall expose typed, validated parameter fields per payload type for authoring,
  grounded in [R109](../research/encyclopedia/R109-sensor-operations.md)/[R110](../research/encyclopedia/R110-communications.md)/[R134](../research/encyclopedia/R134-pnt-warfare-and-navigation-denial-operations.md),
  rather than an untyped dict.
- The system shall expose typed bus parameter fields (power, propulsion) that map to fields the
  engine actually reads, per [R111](../research/encyclopedia/R111-power-and-thermal-operations.md)'s
  dead-field finding — never a plausible-looking field with no live effect.
- The system shall enforce Rules of Engagement independently per cell, replacing today's single
  global gate, while preserving identical behavior for any vignette that declares only the legacy
  global `Parameter` pair.

## 6. Non-functional Requirements

- **Determinism (invariant 1):** both extensions are read-time/construction-time changes
  (parameter shape, ROE dict lookup key) — neither touches the event log, RNG, or scheduler. No
  determinism risk, but any Implementation Package should still run the full suite plus both
  permanent gates to confirm.
- **Backward compatibility:** the single highest-priority NFR for this document. All 19 shipped
  vignettes use the untyped payload dict and the legacy global-ROE `Parameter` pair — both must
  continue to build/run/pass their existing tests completely unchanged. Typed schemas are additive
  (optional fields alongside or bridging to the existing dict); per-cell ROE's default (both cells
  sharing one value set) must be indistinguishable from today's behavior when a vignette declares
  only the legacy shape.
- **UI-agnostic engine (invariant 2):** the per-cell ROE dict and typed payload sub-schemas are
  Domain Model/content-schema changes, not UI concepts — the engine gains a richer *data shape* to
  validate against, never a "cell" or "seat" behavioral concept it didn't already have (`order.cell`
  already exists and is read by other engine logic, per `ADS-3500`'s own prior analysis of the same
  file).

## 7. Constraints

- Must not change `engine/buscommands.py`'s existing verb→field mutation logic (`apply_command`)
  without a separate, explicit decision on how typed authoring fields bridge to the engine's
  existing runtime representation — this document commits to the *authoring-time* schema shape,
  not necessarily a wholesale *runtime* migration (see Open Questions).
- Must not touch `FS-101`/`FS-102`'s existing ROE-check call sites' external behavior for any
  vignette using the legacy global-`Parameter` ROE shape — the per-cell change must be an additive
  generalization, not a breaking rewrite.
- `weather`/`mw` typed sub-schemas are constrained by `BL-0053` — their fields can be *designed* now
  but cannot be considered *wired* until `engine/isr.py`'s `BEAM_MODES` gains entries for both types.

## 8. Risks

- **The typed-authoring-vs-untyped-runtime bridge is real, easily underestimated complexity.**
  If a future Implementation Package treats "add a typed schema" as purely an authoring-UI concern
  and doesn't also decide how the engine's existing `dict`-based `detail`/mutation logic consumes
  it, the typed fields risk becoming another "plausible but inert" surface — the same class of
  defect [R111](../research/encyclopedia/R111-power-and-thermal-operations.md)'s `power_w` finding
  already warns against.
- **Per-cell ROE touches already-`VERIFIED` `FS-101`/`FS-102` territory.** This is a bigger change
  than it looks from the Creator's UI side alone — it requires re-confirming those Features'
  existing acceptance criteria still hold, not just adding a new code path alongside them.
- **`BL-0053` is a hard precondition for two of the eight typed payload sub-schemas.** If a future
  Implementation Package builds the `weather`/`mw` sub-schemas without first (or simultaneously)
  adding their `BEAM_MODES` entries, it reproduces exactly the "typed field the engine ignores"
  problem this document elsewhere warns against for `power_w`.

## 9. Open Questions

1. **Exact typed-schema-to-engine bridging mechanism** — does the engine's `PayloadState`/`BusState`
   gain new strongly-typed fields directly (a bigger engine change), or does the Creator convert a
   typed authoring form into the existing `dict` shape at save time (a smaller, bridging change that
   defers the engine-side typing)? Both satisfy this document's Domain Model intent; they are very
   different implementation scopes. Route to `06-feature-specification`/`07-implementation-planning`
   to decide, informed by this document's Constraints.
2. **Whether `BL-0053`'s `BEAM_MODES` fix rides this feature's own Implementation Package, or ships
   as its own separate, earlier prerequisite package.** Not decided here — flagged as a sequencing
   question for `07-implementation-planning` once an FS exists.
3. **Exact per-cell ROE YAML shape** — a nested `{cell: {flag: bool}}` dict (as sketched in §3.2) vs.
   a flat `{"blue_kinetic_authorized": bool, "red_kinetic_authorized": bool, ...}` `Parameter`-style
   list extending the existing convention. Both satisfy this document's backward-compatibility
   constraint; the eventual FS should pick one and state the migration path for existing vignette
   YAML explicitly.
4. **Whether a vignette declaring only the legacy global ROE shape should be silently treated as
   "both cells share this value" forever, or auto-upgraded to an explicit per-cell block on next
   save.** Not decided here — a product/authoring-UX question for the eventual FS.

## 10. Decision Log

| # | Decision | Rationale | Alternatives considered |
|---|---|---|---|
| 1 | Introduce **typed per-payload-type parameter sub-schemas**, replacing the generic `PayloadState.detail` dict for authoring purposes. | Makes "effective range," "bandwidth," "accuracy" etc. named, validated, research-grounded fields instead of an opaque bag — the project owner's explicit request. | Keep the generic dict + a "smart UI" that merely knows which keys are meaningful per type — rejected by the project owner directly (`AskUserQuestion`): faster to ship but leaves the underlying schema loosely typed with no formal field definition. |
| 2 | Typed bus **power** parameters expose `charge_rate_per_s`/`drain_rate_per_s`, not `power_w`. | `power_w` is a confirmed dead field (`R111`) — exposing it as authorable would silently do nothing, worse than omitting a power parameter entirely. | Wire `power_w` into `advance_bus` first, then expose it — rejected for this pass: a separate, out-of-scope engine change with its own DoD-model implications (`R111` §5), not something this synthesis should fold in without a dedicated decision. |
| 3 | Build **real per-cell ROE enforcement** now, changing `engine/orders.py`'s check from a single global dict to a cell-keyed one. | The project owner's explicit choice (`AskUserQuestion`), over a cheaper cosmetic-selector alternative — "ROE selectors per cell" should actually gate per-cell behavior, not merely display two selectors that both write the same global flag. | A cosmetic per-cell selector mapping to today's single global flag — rejected by the project owner directly: would look per-cell in the UI while functioning identically to today, a misleading surface. |
| 4 | `weather`/`mw` sub-schemas are **designed now, wiring deferred to `BL-0053`.** | Keeps this synthesis's Domain Model complete (all 8 payload types have a committed schema shape) without blocking on an engine change that belongs to its own, separately-tracked backlog item. | Exclude `weather`/`mw` from this document's Domain Model entirely until `BL-0053` ships — rejected: would leave an incomplete Domain Model for a document whose whole purpose is completeness (per `R137`'s own grounding), and gives the eventual Implementation Package no committed shape to build toward once `BL-0053` lands. |

---

**Next step:** together with [ADS-5100A](ADS-5100A-vignette-creator-session-and-ui.md), this
document grounds the Vignette Creator Feature Specification `06-feature-specification` should
author next. Its four Open Questions are non-blocking but should be resolved during that FS's
drafting.
