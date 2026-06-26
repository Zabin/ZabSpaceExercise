# FS-102 — Command Scheduling

> **Document ID:** FS-102
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R103](../research/encyclopedia/R103-satellite-command-and-control.md)
> **Referenced By:** [R103](../research/encyclopedia/R103-satellite-command-and-control.md)
> **Produces:** the executed-order surface consumed by [FS-105](FS-105-spacecraft-operations.md)'s telemetry/confirmation views
> **Feature Mapping:** FS-102 (this document)
> **Related Topics:** [FS-101](FS-101-mission-planning.md) (plan-time preview of the same latency), [R107](../research/encyclopedia/R107-ground-segment-operations.md) (ground-segment access),
> [R110](../research/encyclopedia/R110-communications.md) (link/comms posture)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

## 1. Purpose

Command Scheduling specifies how a **committed** order (one a cell has already planned and issued,
distinct from [FS-101](FS-101-mission-planning.md)'s pre-commit preview) moves through the real-world latency chain a satellite
command actually has to survive: validate → window → execute → confirm. No DOM document owns this
ID directly; it is grounded entirely in [R103](../research/encyclopedia/R103-satellite-command-and-control.md) §5, which names it (with FS-105) as the
direct consumer of the real C2 latency model.

## 2. Scope

In scope: the lifecycle and status visibility of an issued order from commit to confirmation,
including uplink/stored delivery paths and cancellation. Out of scope: the planning/preview
workflow before commit ([FS-101](FS-101-mission-planning.md)), and the bus/payload semantics of any individual command verb
([FS-105](FS-105-spacecraft-operations.md)).

## 3. Capability requirements

- **The validate→window→execute→confirm latency must be real, not collapsed.** Per [R103](../research/encyclopedia/R103-satellite-command-and-control.md) §5, a
  scheduling UI must not present command execution as instantaneous once issued — an operator
  should be able to see that a command is queued, awaiting its access window, or already executed
  but not yet confirmed via telemetry, as genuinely distinct states.
  - **Validate**: the command passes its plan-time gate (resource/state preconditions).
  - **Window**: the command waits for its access channel (uplink, or relevant channel) to open.
  - **Execute**: the command fires at the engine tick the window opens (or, for stored/ISL
    delivery, at the later real delivery time).
  - **Confirm**: telemetry downlink reports the post-execution state back to the operator — this
    may lag execution by a further access-window wait.
- **Stored/relay delivery paths must be visible as distinct from direct uplink.** A command that
  must wait for ISL relay or stored delivery (rather than direct uplink) is operationally different
  from one with an immediate window — the scheduling surface must not flatten this distinction.
- **A queued order must be cancellable before execution, and the UI must reflect cancellation
  unambiguously** (no ambiguous state where it's unclear whether a cancel raced the execution tick).
- **Order queue and contention must be visible.** Where multiple orders compete for the same
  resource (e.g., sensor tasking contention), the scheduling surface must show the contention, not
  silently pick a winner with no explanation.

## 4. Non-goals

- Command Scheduling does not decide *what* a command does (bus/payload semantics) — that is
  [FS-105](FS-105-spacecraft-operations.md)'s scope, layered on top of this lifecycle.
- This spec does not cover the cyber-effect exception (cyber resolves immediately against posture,
  not at a future access window per [`CLAUDE.md`](../../CLAUDE.md)'s effects model) — that distinct, non-windowed
  resolution path belongs to the effect category itself ([R116](../research/encyclopedia/R116-cyber-operations-against-space-systems.md)), surfaced via [FS-105](FS-105-spacecraft-operations.md).

## 5. Non-functional requirements

- **Determinism-consistent display.** Whatever the scheduling UI shows about "time until window"
  must be computed from the same access-window logic the engine actually gates execution on — a
  display estimate that can disagree with the real gate (per [FS-101](FS-101-mission-planning.md) §3's window-display
  requirement) is a defect, not a UI approximation.
- **Human factors.** The latency itself is intentional friction ([DOM-007](../domains/DOM-007-human-factors-framework.md) §3) — real space
  operators cannot collapse the validate→window→execute→confirm chain either; the UI's job is to
  make that chain legible, not to hide or fake-shorten it.

## 6. Related Topics

[R103](../research/encyclopedia/R103-satellite-command-and-control.md) (the C2 latency model this spec is grounded in), [R107](../research/encyclopedia/R107-ground-segment-operations.md) (ground-station access constraints on uplink/downlink
windows), [R110](../research/encyclopedia/R110-communications.md) (link posture effects on command delivery), [FS-101](FS-101-mission-planning.md) (the pre-commit preview of this
same latency chain), [FS-105](FS-105-spacecraft-operations.md) (the console surface that displays scheduled-command state).
