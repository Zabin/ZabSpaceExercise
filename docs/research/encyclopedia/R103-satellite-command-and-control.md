# R103 — Satellite Command and Control

> **Document ID:** R103
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** R101
> **Referenced By:** R106, R107, R113, R114, R116, FS-102, FS-105
> **Produces:** implementation constraints for `engine/orders.py`, `engine/buscommands.py`
> **Feature Mapping:** FS-102 (Command Scheduling), FS-105 (Spacecraft Operations)
> **Related Topics:** R106 (Mission Operations), R114 (Command and Data Handling), MSTR-002 §2 invariant 4 (plan-first)

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Satellite command and control (C2) is the mechanism by which an operator's intent becomes an
on-orbit action. This topic gives an implementer the operational model behind `OrderSystem`
(validate → window → execute) so new command/order types are designed consistently with how real
satellite C2 actually works, not as an arbitrary RPC.

## 2. Concepts

**The C2 chain.** Real satellite commanding has four stages: (1) command formulation (the operator
or ground software composes a command, often against a validated command dictionary), (2) uplink
delivery (subject to a command-uplink access window), (3) onboard validation (the spacecraft's
flight software checks the command against its own safety constraints before execution), (4)
execution and telemetry confirmation (the effect happens, and is confirmed via the next
telemetry-downlink window — not instantly).

**Mapping to the engine.** `OrderSystem.issue()`'s validate → window → execute pipeline mirrors
stages 1-2-4; stage 3 (onboard validation) maps to `can_issue` gating in `buscommands.py` (payload
verbs gated by payload type + bus availability) plus the safe-mode/SOH gating in `bus.py`. The
crucial implementation fact: **execution and confirmation are not the same moment as issuance** —
exactly the plan-first invariant (MSTR-002 §2 invariant 4), and exactly why `dry_run()` exists as a
separate, side-effect-free path to answer "would this be valid" before committing.

**Stored vs. real-time delivery.** Commands may be delivered live (within an uplink window) or
staged for store-and-forward delivery (ISL relay, onboard storage) when no direct uplink window is
available — `orders.py`'s "ISL/stored delivery" path. This reflects real operations: many missions
do not have continuous ground contact and rely on relay/store-forward C2.

## 3. Operational Context

A real operator cannot "just command" a satellite at will — every command competes for a scarce
uplink window, must pass onboard safety validation, and its effect is only confirmed on the next
downlink. Mission anomalies are frequently *C2 chain* failures (a command sent outside a window, a
command rejected by onboard safety logic) rather than payload failures — which is precisely why the
simulator's "denied, not crashed" degrade behavior (MSTR-002 §6) for invalid commands is doctrinally
accurate, not just good engineering practice.

## 4. Implementation Guidance

- **New command/order types must go through `OrderSystem`**, never bypass it for a "simpler" direct
  state mutation — this is both an architecture invariant (MSTR-002) and an operational-realism
  requirement (this topic).
- **Gate onboard validation (`can_issue`) on the same conditions a real flight-software safety check
  would use** — bus availability, payload type/mode compatibility, safe-mode status — not on
  arbitrary game-balance conditions.
- **Distinguish "command sent" from "command confirmed executed" in any new UI surface** — surfacing
  them as the same event misrepresents the real C2 latency this domain has.
- **When adding a relay/stored-delivery path for a new command type**, reuse the existing ISL/stored
  delivery machinery in `orders.py` rather than inventing a parallel queue.

## 5. Feature Mapping

FS-102 (Command Scheduling) and FS-105 (Spacecraft Operations) are the direct consumers — any
scheduling UI must reflect the real validate→window→execute→confirm latency, not collapse it.

## 6. Related Topics

R106 (Mission Operations — the broader workflow C2 sits inside), R114 (Command and Data Handling —
onboard storage/dump, the stored-delivery counterpart), R116 (Cyber Operations — the doctrinal
exception to window-gated C2), MSTR-002 §5 (replay-safety, relevant to why `dry_run()` must not
mutate state).
