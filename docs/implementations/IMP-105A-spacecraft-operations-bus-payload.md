# IMP-105A — Spacecraft Operations: Bus/Payload Command & Telemetry

> **Document ID:** IMP-105A
> **Version:** 1.0
> **Status:** ✅ Done (as-built — documents existing, test-covered code)
> **Dependencies:** [FS-105](../features/FS-105-spacecraft-operations.md)
> **Referenced By:** [IMP-102A](IMP-102A-command-scheduling.md) (the `command` action's delivery/window lifecycle), [IMP-105B](IMP-105B-spacecraft-operations-effects-console.md) (the
> sibling package covering effect resolution & console UX)
> **Produces:** the executed-state surface [FS-107](../features/FS-107-after-action-review.md) replays and [FS-201](../features/FS-201-competency-assessment.md) assesses
> **Feature Mapping:** FS-105 (§3.1)
> **Related Topics:** [`spacesim/engine/buscommands.py`](../../spacesim/engine/buscommands.py), [`spacesim/engine/bus.py`](../../spacesim/engine/bus.py), [`spacesim/engine/orders.py`](../../spacesim/engine/orders.py)

[↑ Implementation index](INDEX.md) · [Docs index](../INDEX.md)

> **Superseded.** This document's content has been re-derived, re-verified against the current
> source tree, and re-published under the canonical `docs/implementation/packages/` tier as
> [**IP-1050**](../implementation/packages/IP-1050-spacecraft-operations-bus-payload.md). This file
> is retained for historical reference and is not deleted, but
> [`IP-1050`](../implementation/packages/IP-1050-spacecraft-operations-bus-payload.md) is the
> document of record going forward — see
> [`docs/implementation/00-master-build-plan.md`](../implementation/00-master-build-plan.md)
> §"Relationship to the prior `docs/implementations/` corpus."

## 1. Situation

**As-built.** FS-105 is split across two IMP packages because of its size (per
[`MSTR-006`](../master/MSTR-006-governance-principles.md) §4): this package (§3.1, "Bus and subsystem operations") covers the
`command` action's verb catalog, gating, and execution; [IMP-105B](IMP-105B-spacecraft-operations-effects-console.md) covers §3.2/§3.3 (the
five effect categories and the console UX wrapping them).

## 2. The verb catalog

`buscommands.py` partitions every bus/payload verb into three sets (`:18`-`:47`): `BUS_VERBS`
(power/attitude/storage/thermal/comms/prop, e.g. `eps.shed_load`, `adcs.set_mode`,
`cdh.dump_storage`), `PAYLOAD_VERBS` (mission-type-specific, e.g. `satcom.mitigate_interference`,
`isr.collect_now`, `sda.task_characterize`), and `DEFENSE_VERBS` (`def.patch_cyber`,
`def.maneuver_evade`, ...) — their union is `COMMAND_VERBS` (`:48`), the single source of truth
the order validator and the handler both consult, so the console can never offer a verb the engine
doesn't recognize. The inline comment at `:24`-`:32` records a deliberate **cut** list (verbs
removed during the Jun 2026 commands audit for having no consumer or a broken loop) alongside what
replaced them — evidence the catalog is actively curated against "only verbs with a faithful,
observable effect" (`:7`), not a speculative wishlist.

## 3. Plan-time gating: `can_issue`

`can_issue(world, actor_id, verb)` (`:524`) is the validator the order system calls before queuing
a `command` order: unknown verbs fail `"unknown_command"`; payload verbs check
`_PAYLOAD_TYPES_FOR[verb]` against the asset's actual `payload_state.type` (`"no_payload_for_verb"`
— FS-105 §2's "bus/payload fit," FR-B2) and, separately, whether `payload_available(bus_state)`
holds (`"payload_unavailable"` — the bus's safe-mode/power-red state can gate the payload even when
the payload type matches, satisfying §3.1's "storage/downlink gating must be visibly respected" via
the same mechanism that gates collection generally). `def.maneuver_evade` additionally requires a
minimum Δv (`:538`-`:540`, `"insufficient_delta_v"`) — a defense verb gated by the same resource
ledger maneuver orders consume, not a separate fuel pool.

## 4. Execution: `apply_command`

`apply_command(world, actor_id, verb, params, now)` (`:80`) is dispatched from inside the
deterministic event loop via `OrderSystem._h_command` (`orders.py:688`), itself scheduled as the
`execute_command` event built by `_exec_payload` (`orders.py:562`-`563`) when `order.action ==
"command"`. It **re-validates at execution time** (`:88`, "the asset may have been lost / safed
since planning") — the asset could have changed state between plan-time `can_issue` and the
window opening — and returns `(success, physical-outcome-label)`, e.g. `(True, "loads_shed")` or
`(False, "lost")`. The docstring (`:83`-`:85`) is explicit that this label is a **symptom, not a
verdict**: telemetry surfaces what changed physically, never a diagnosis, consistent with the
defender-fog principle that a cell never gets an authoritative cause string for free. Each verb
mutates `BusState`/`PayloadState` fields directly (e.g. `eps.shed_load` sets
`bus.power.loads_shed = True` and stands the payload down, `:95`-`:96`; `adcs.set_mode` sets
`bus.attitude.mode`/`pointing_ok`, `:123`-`:124`) and most call `recompute_status(bus)`
(`bus.py`) afterward so the SOH view reflects the change on the very next telemetry read.

Because `apply_command` runs inside `execute_command`, every mutation is replay-exact
(per `CLAUDE.md`'s determinism invariant) and observable through the existing pass-gated SOH and
read-time telemetry signatures (`engine/telemetry.py`) — there is no separate bus-command-specific
telemetry path.

## 5. Delivery and access

`command` orders use the `COMMAND_UPLINK` channel (`orders.py:43`) like any other uplinked order,
and (per `orders.py:161`) are eligible for the same stored/ISL delivery branching
[IMP-102A](IMP-102A-command-scheduling.md) §3 documents for `maneuver` — a bus/payload command queued while the direct
uplink channel is closed can still be delivered via relay, surfaced via the order's `via` field
exactly as any other order. `_h_command` (`orders.py:688`) is one of the six handler categories
[IMP-102A](IMP-102A-command-scheduling.md) §2 lists for the `executing → executed` transition.

## 6. Satisfying FS-105 §3.1's capability requirements

- **Comms-posture commands surface through the existing bus panel** (§3.1 bullet 2):
  `comms.enable_isl`/`comms.config_link` are ordinary `BUS_VERBS` (`:22`), dispatched and gated
  identically to every other bus verb — no bespoke comms screen exists in the engine layer.
- **Power/thermal causality** (§3.1 bullet 3): `eps.*`/`tcs.*` verbs mutate the same `BusState`
  fields the telemetry layer's attack-signature/eclipse model reads (`engine/telemetry.py`'s
  power-sag signature, per `CLAUDE.md`'s code map) — cause and displayed symptom share one state
  object, not two.
- **ADCS fidelity honesty** (§3.1 bullet 4): `adcs.set_mode` operates on `_ATTITUDE_MODES`
  (`"nominal"|"slew"|"safe"`, `:71`) — mode-level, not a vector/quaternion target — matching what
  the engine actually models; this package does not invent finer pointing fidelity.
- **Storage/downlink gating visible** (§3.1 bullet 5): §3's `payload_available()` check.
- **Constellation vignettes operated per-asset** (§3.1 bullet 6): every verb in §2-4 takes a single
  `actor_id` — no fleet-aggregate verb exists in this catalog (explicitly out of scope per FS-105
  §6).

## 7. Test coverage (existing)

`apply_command`/`can_issue` are covered directly by the order-system and bus-model test suites
(verb-by-verb gating and physical-outcome assertions); the Jun 2026 commands audit
(`docs/AUDIT-2026-06.md`) is the record of the cut/kept verb decisions in §2. No new tests are
proposed by this package.

## 8. Related Topics

[FS-105](../features/FS-105-spacecraft-operations.md) (the spec this documents, §3.1), [IMP-105B](IMP-105B-spacecraft-operations-effects-console.md) (the sibling package, §3.2/§3.3),
[IMP-102A](IMP-102A-command-scheduling.md) (the `command` action's shared execution lifecycle), [`spacesim/engine/buscommands.py`](../../spacesim/engine/buscommands.py),
[`spacesim/engine/bus.py`](../../spacesim/engine/bus.py).
