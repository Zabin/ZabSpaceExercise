# FS-102 — Command Scheduling

> **Document ID:** FS-102
> **Version:** 1.1 *(2026-10-17, pipeline run #163: Requirements Implemented now cites `FR-3310`/`FR-3410` (`BL-0050`); order-lifecycle wording matched to the as-built statuses (`BL-0258`). No behaviour changed.)*
> **Status:** ✅ Done
> **Dependencies:** [R103](../research/encyclopedia/R103-satellite-command-and-control.md)
> **Referenced By:** [FS-132](FS-132-effect-resource-bounds.md) (execute-time ammunition re-check, `FR-1460`), [R103](../research/encyclopedia/R103-satellite-command-and-control.md), [IMP-102A](../implementations/IMP-102A-command-scheduling.md), [IP-1052](../implementation/packages/IP-1052-order-param-hardening.md) (🟢 `VERIFIED` 2026-10-16, `VR-1052`; order-parameter hardening, `BL-0222`) · [IP-1021](../implementation/packages/IP-1021-failure-atomic-event-application.md) (🟢 `VERIFIED` 2026-10-17, `VR-1021`; failure-atomic event application, `BL-0264`/`BL-0227`), [IP-1065](../implementation/packages/IP-1065-console-and-session-small-fixes.md), [IP-1131](../implementation/packages/IP-1131-verification-coverage-follow-ups.md) *(planned 2026-10-17, run #166)*
> **Produces:** the executed-order surface consumed by [FS-105](FS-105-spacecraft-operations.md)'s telemetry/confirmation views
> **Feature Mapping:** FS-102 (this document)
> **Related Topics:** [FS-101](FS-101-mission-planning.md) (plan-time preview of the same latency), [R107](../research/encyclopedia/R107-ground-segment-operations.md) (ground-segment access),
> [R110](../research/encyclopedia/R110-communications.md) (link/comms posture)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template; it supersedes this file's prior ad hoc structure while retaining its existing Document ID, status, and metadata per MSTR-006 §5.*

## Feature ID

FS-102

## Title

Command Scheduling

## Purpose

Command Scheduling specifies how a **committed** order — one a cell has already planned and issued,
distinct from [FS-101](FS-101-mission-planning.md)'s pre-commit preview — moves through the real-world latency chain a
satellite command actually has to survive: validate → window → execute → confirm. Grounded entirely
in [R103](../research/encyclopedia/R103-satellite-command-and-control.md) §5, which names FS-102 (with [FS-105](FS-105-spacecraft-operations.md)) as the direct consumer of the real C2
latency model. No DOM document owns this ID directly.

## Scope

In scope: the lifecycle and status visibility of an issued order from commit to confirmation,
including uplink/stored-delivery paths and cancellation. Out of scope: the planning/preview
workflow before commit ([FS-101](FS-101-mission-planning.md)), and the bus/payload semantics of any individual command
verb ([FS-105](FS-105-spacecraft-operations.md)).

## Requirements Implemented

*Updated 2026-10-17 (`BL-0050`).* `05-feature-review.md` maps this FS onto `FEAT-3300` and
`FEAT-3400`. Their owned leaves this FS implements:

| ID | Owning Feature | How this FS covers it |
|---|---|---|
| `FR-3310` — Single scheduler for commands and collection tasks | FEAT-3300 | Commands, sensor-tasking `observe` orders and SSN requests all schedule their execution as events on the one deterministic `Scheduler`/`EventLog`, so queueing, cancellation before execution, undo and rewind behave the same for every kind (`FR-3310` Notes record the as-built mapping). The order queue and the SSN request list are separate operator surfaces, which `FR-3310`'s amended Outputs permit. |
| `FR-3410` — Execute-time re-validation | FEAT-3400 | The execution event re-checks the order when its window opens, not only at plan time (System Behaviour, *Execute*). |

`FR-3110`/`FR-3120` (command creation and editability, FEAT-3100) belong to
[FS-101](FS-101-mission-planning.md); `FR-3420`–`FR-3440` (FEAT-3400's ROE leaves) belong to
[FS-127](FS-127-effect-authorization-gating-and-live-roe.md); `FR-1460`'s execute-time
ammunition re-check belongs to [FS-132](FS-132-effect-resource-bounds.md).

## User Workflows

- A cell (Blue or Red operator) issues an order that has already passed plan-time validation; it
  enters the execution queue in **validate** state.
- The order waits for its access channel to open; the operator can observe it in **window** state,
  with a live "time until window" display.
- At the relevant engine tick, the order fires into **execute** state — for stored/ISL delivery,
  this may be a later real delivery tick, distinct from the window-open tick.
- Telemetry downlink reports post-execution state, completing the **confirm** phase; the operator
  observes the satellite's new state through [FS-105](FS-105-spacecraft-operations.md)'s telemetry view.
- If the operator wishes to cancel before execution, they may do so and receive unambiguous
  confirmation that the cancel raced successfully (or did not).
- Where multiple orders contend for the same resource (e.g., sensor-tasking contention), the
  operator observes the contention and its resolution rather than a silent outcome.

## System Behaviour

- **The validate→window→execute→confirm latency must be real, not collapsed.** Per [R103](../research/encyclopedia/R103-satellite-command-and-control.md) §5, the
  scheduling system must not present command execution as instantaneous — the four phases below are
  genuinely distinct and each is observable. *(Corrected 2026-10-17, `BL-0258`.)* They are phases
  the operator observes across two surfaces, not four stored order statuses. As built, an order's
  stored status is `queued`, `rejected` or `cancelled`. The order queue shows a `queued` order with
  its time until window (validate + window), and shows a derived, display-only `executed` label once
  the clock has passed the window start (execute). Confirmation is observed through the pass-gated
  telemetry of [FS-105](FS-105-spacecraft-operations.md), not as an order-queue status.
  - *Validate*: the command passes its plan-time gate (resource/state preconditions).
  - *Window*: the command waits for its access channel (uplink, or relevant channel) to open.
  - *Execute*: the command fires at the engine tick the window opens (or, for stored/ISL delivery,
    at the later real delivery time).
  - *Confirm*: telemetry downlink reports the post-execution state — this may lag execution by a
    further access-window wait.
- **Stored/relay delivery paths must be visible as distinct from direct uplink.** A command routed
  via ISL relay or stored delivery is operationally different from one with an immediate window;
  the scheduling surface must not flatten this distinction.
- **A queued order must be cancellable before execution.** The cancellation outcome must be
  unambiguous — no state where it is unclear whether a cancel raced the execution tick.
- **Order queue and contention must be visible.** Where multiple orders compete for the same
  resource, the scheduling surface must show the contention and its resolution.
- **"Time until window" display must match real execution gating.** Whatever the UI shows must be
  derived from the same access-window logic the engine actually uses to gate execution — a display
  estimate that diverges from the real gate is a defect (per [FS-101](FS-101-mission-planning.md) §3's consistent window-display
  requirement).
- **The cyber-effect exception.** Cyber resolves immediately against posture, not at a future access
  window — this non-windowed resolution path is out of this spec's scope (it belongs to the effect
  category itself, per [R116](../research/encyclopedia/R116-cyber-operations-against-space-systems.md)) but the scheduling surface must not visually imply cyber waits on
  a window the way other effect categories do.

## Subsystem Responsibilities

The source document does not provide a per-subsystem breakdown. The engine's `OrderSystem`
(validate → window → execute) and `Scheduler`/`SimClock` (sub-stepped execution, event sequencing)
are named in [`CLAUDE.md`](../../CLAUDE.md) as the components implementing this lifecycle, but the source document does
not distribute responsibilities across them in a formal table. Flagged as an Open Question below.

## Interfaces Used

Per the verified mapping for FS-102: INT-0004 (Blue/Red Cell Operator ↔ Operator Console) and
INT-0008 (SessionManager → Simulation Engine Clock/Scheduler/EventLog/OrderSystem) — per
`docs/design/05-interface-control-document.md`. The source document does not itself cite ICD
interface IDs; these are carried forward from the verified Related Interfaces mapping (field 21).

## Data Model Changes

Not addressed in the source document — no existing content to carry forward. Flagged as an Open
Question below.

## State Changes

The source document describes four named states for a committed order: validate → window → execute
→ confirm. Cancellation is a terminal state that may precede execute. Stored/ISL delivery
introduces an intermediate held state between window-open and actual execution. The document does
not enumerate these as a formal state-machine diagram.

## Error Handling

- A cancellation request must produce an unambiguous result — success or failure, not an
  indeterminate "may have raced" outcome visible to the operator.
- Contention for a resource (e.g., two orders competing for the same sensor) must be surfaced
  explicitly, not silently resolved.
- The source document does not enumerate further error states or failure modes.

## Performance Considerations

- **Determinism-consistent display.** Window countdown must be computed from the same access-window
  logic the engine actually gates execution on — a display estimate that can disagree with the real
  gate is a defect, not a UI approximation.
- **Human factors.** The latency chain is intentional friction ([DOM-007](../domains/DOM-007-human-factors-framework.md) §3) — real space operators
  cannot collapse the validate→window→execute→confirm chain; the UI's job is to make that chain
  legible, not to hide or fake-shorten it.

## Security Considerations

Not addressed in the source document — no existing content to carry forward. Flagged as an Open
Question below.

## Acceptance Criteria

Derived from the source document's capability requirements, restated as checkable conditions:

- A queued order awaiting its window, an executed order, and a confirmed post-execution state are
  visibly distinct: the queue shows `queued` with a time-until-window, then `executed` once the
  window start has passed (never before); confirmation appears in the asset's telemetry at the next
  downlink contact. *(Restated 2026-10-17, `BL-0258`; was "queued, awaiting-window,
  executed-unconfirmed, and confirmed are visibly distinct states in the scheduling surface".)*
- A stored/ISL delivery command is visibly distinct from a direct-uplink command in the queue.
- A queued order can be cancelled before execution; the cancel outcome (success or failed-race) is
  unambiguous.
- When multiple orders contend for the same resource, the contention and its resolution are visible.
- The "time until window" display is derived from the same access-window computation the engine uses
  for execution gating; the two cannot disagree.
- The cyber-effect non-windowed resolution path is visually distinct from windowed effect categories.

## Verification Plan

The source document does not state a Verification Method per criterion. Test (automated) is the
implied method for determinism-consistency and state-distinctness, given the project's
test-driven-workflow mandate ([`CLAUDE.md`](../../CLAUDE.md)) and the determinism property test as the permanent Phase-1
gate. Flagged as an Open Question below.

## Dependencies

[R103](../research/encyclopedia/R103-satellite-command-and-control.md) (per the existing metadata block's Dependencies field). [FS-101](FS-101-mission-planning.md) (pre-commit preview of
the same latency chain — out of scope here but tightly coupled) and [FS-105](FS-105-spacecraft-operations.md) (the operator console
that displays this feature's output) are named as adjacent features, not upstream dependencies of
FS-102 itself. [R107](../research/encyclopedia/R107-ground-segment-operations.md) and [R110](../research/encyclopedia/R110-communications.md) are noted as related topics, not formal dependencies in
the metadata block.

## Risks

The source document does not state risks explicitly. The following are restated faithfully from
material the document does discuss as constraints:

- A display estimate for "time until window" that is computed separately from the engine's
  access-window gate (e.g., a client-side approximation) could diverge from real execution timing
  — this would be a defect per the determinism-consistent display requirement.
- The cyber-exception's non-windowed resolution, if not made visually distinct, could mislead an
  operator into expecting a window wait that will never come.

## Open Questions

- ~~No FR-xxxx/NFR-xxxx in `docs/requirements/` explicitly cites FS-102.~~ **Resolved 2026-10-17
  (`BL-0050`):** FS-102 implements `FR-3310` and `FR-3410` (see Requirements Implemented).
- The source document does not assign a per-subsystem Subsystem Responsibilities table; how the
  engine's `OrderSystem`, `Scheduler`, and `SimClock` divide the validate/window/execute lifecycle
  in terms of ownership is unresolved here.
- The source document does not address Data Model Changes; whether the order-queue state machine
  requires any Domain Model addition beyond existing `Order`/`EventLog` structures is unresolved.
- The source document does not address Security Considerations; whether per-cell access controls
  apply to viewing another cell's scheduled commands is unresolved.
- The source document does not state a formal Verification Method per acceptance criterion; Test is
  assumed from project-wide convention, not the source document.

## Related ADRs

ADR-0005 (plan-first commanding model) — `docs/architecture/adr/ADR-0005-plan-first-commanding.md`;
ADR-0006 (sub-stepped deterministic clock) — `docs/architecture/adr/ADR-0006-substepped-clock.md`;
ADR-0011 (six access channels taxonomy) — `docs/architecture/adr/ADR-0011-six-access-channels.md`.

## Related Interfaces

INT-0004 (Blue/Red Cell Operator ↔ Operator Console); INT-0008 (SessionManager → Simulation Engine
Clock/Scheduler/EventLog/OrderSystem) — per `docs/design/05-interface-control-document.md`.
