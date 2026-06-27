# R122 — Safe-Mode Recovery

> **Document ID:** R122
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R114](R114-command-and-data-handling.md), [R116](R116-cyber-operations-against-space-systems.md)
> **Referenced By:** FS-105
> **Produces:** implementation constraints for [`engine/recovery.py`](../../../spacesim/engine/recovery.py)
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R114](R114-command-and-data-handling.md) (Command and Data Handling — `cdh.clear_fault`, the lighter path this topic
> distinguishes itself from), [R116](R116-cyber-operations-against-space-systems.md) (Cyber Operations — the persistent root cause that can re-safe a
> satellite), [R103](R103-satellite-command-and-control.md) (Satellite Command and Control — the command-uplink windows recovery passes consume)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 1

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Real spacecraft safe-mode recovery is a multi-pass ground procedure spread over several
command-uplink contacts, not a single button press — `engine/recovery.py`'s `RecoverySystem` models
that explicitly, including the case where recovery doesn't stick because the inducing cause (e.g. an
unpatched cyber vulnerability) is still present. This topic gives the implementer the
`RecoverySystem` step/pass model so a new fault-recovery-adjacent feature uses the same chain rather
than a single-event shortcut that erases the realism the multi-pass design exists to capture.

## 2. Scope

Covers: the `RecoverySystem` confirm→diagnose→patch→re-enable step chain, the
`difficulty`-scaled pass count, the re-safe-on-persistence rule, and how this differs from
`cdh.clear_fault`'s lighter-weight single-command path. Does **not** cover: the safe-mode entry
trigger itself or the `SafeModeState` fields it advances ([R114](R114-command-and-data-handling.md)), or the cyber-vulnerability
patch state recovery checks for persistence ([R116](R116-cyber-operations-against-space-systems.md)).

## 3. Concepts

**Recovery is scheduled as two deterministic events over real command-uplink windows, not resolved
instantly.** `begin_recovery` finds the next 24 hours of `COMMAND_UPLINK` access windows via the
same `AccessProvider` every other channel uses, schedules `recovery_confirm` at the first window and
`recovery_finish` at the `passes_used`-th window — recovery genuinely takes wall-clock-equivalent
time to execute because it requires real contact opportunities with the satellite, the same
access-window-gated principle [R103](R103-satellite-command-and-control.md) and [R120](R120-access-window-and-geometry-planning.md) document for ordinary commanding.

**Pass count scales with a named difficulty tier, not a single hardcoded number.**
`PASSES_FOR_DIFFICULTY` (`quick`/`realistic`/`punishing`: 1/2/3) is the §6.3 model cited in the
module docstring — `passes_needed()` reads this table, and `begin_recovery` clamps to
`min(n, len(wins))` if fewer windows exist in the 24-hour lookahead than the difficulty calls for,
so a satellite with a sparse contact schedule recovers over however many windows are actually
available rather than failing outright.

**`recovery_confirm` establishes contact and dumps telemetry before diagnosis can begin.**
`_h_confirm` sets `defender_confirmed = True`, derives `defender_diagnosis` (`"suspected_attack"` for
`cyber`/`ew` causes, otherwise the literal cause or `"fault"`), calls `refresh_ground_view` to dump
stored telemetry, and appends `"establish_contact"`/`"dump_telemetry"` to `steps_done` — modeling
that the first real pass is spent confirming what happened and getting data down, not yet fixing
anything; `current_step` advances to `"diagnose"` for the recovery-strip UI to reflect.

**Recovery only completes if the root cause is actually resolved — otherwise the satellite is
re-safed.** `_h_finish` checks `root_cause_persists` against `_root_cause_unresolved`, which for a
`cyber`-caused safe mode checks whether any entry in `sat.cyber_vulnerabilities` is still unpatched;
if so, the satellite is **not** recovered — `blocked_reason` is set, `current_step` becomes
`"blocked"`, and an `effect_log` entry records `achieved: "re_safed", success: False`. This is the
concrete mechanism behind the module docstring's "if the inducing cause persists... the satellite is
re-safed: the defender must remove the root cause" rule — a multi-pass recovery procedure that
ignores root cause and just "tries again" would contradict how real spacecraft fault-recovery
procedures work, where reset/safing repeats until the underlying anomaly is actually corrected, not
merely until a fixed number of recovery attempts have elapsed
([NASA, *Spacecraft Anomalies and Failures Workshop* proceedings, NASA/CP-2017-219455](https://ntrs.nasa.gov/api/citations/20170006869/downloads/20170006869.pdf)
([Wayback](https://web.archive.org/web/2026/https://ntrs.nasa.gov/api/citations/20170006869/downloads/20170006869.pdf))).

**Successful recovery appends the remaining standard steps and exits safe mode atomically.** When
the root cause is resolved (or doesn't apply), `_h_finish` appends `"patch"`/`"re_enable"` to
`steps_done` if not already present, calls `exit_safe_mode` (bus mode → `"nominal"`), sets
`current_step = "done"`, and logs `achieved: "recovered", success: True` — `passes_used` is
preserved on the now-exited `safe_mode` state for post-recovery inspection rather than being reset,
so an AAR review can see how many passes the recovery actually took.

**`RecoverySystem` is the heavyweight multi-pass path; `cdh.clear_fault` is a separate,
lighter-weight single-command path.** `buscommands.py`'s `cdh.clear_fault` verb directly sets
`bus.cdh.fsw_mode = "nominal"` and calls `recompute_status` in one step — it does not check
`cyber_vulnerabilities`, does not require command-uplink-window scheduling beyond the single command
itself, and does not produce the `steps_done`/`current_step`/`blocked_reason` recovery-strip state.
These are two intentionally different remedies for two different severities of fault: a transient
FSW fault clears with one command, while a safe-mode entry — especially one with a persistent root
cause — requires the full multi-pass `RecoverySystem` chain.

### Sources

- *NASA, Spacecraft Anomalies and Failures Workshop proceedings, NASA/CP-2017-219455* —
  [live](https://ntrs.nasa.gov/api/citations/20170006869/downloads/20170006869.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://ntrs.nasa.gov/api/citations/20170006869/downloads/20170006869.pdf)
  · accessed 2026-06-27.

## 4. Operational Context

Real spacecraft fault-recovery procedures are run by ground teams over a sequence of contacts,
because diagnosing root cause, commanding a fix, and verifying it stuck each generally requires a
separate pass and cannot be compressed into a single ground-station contact, and a documented
recurring failure mode in spacecraft anomaly post-mortems is exactly the re-safe loop this module
models: a recovery attempt that doesn't address the actual root cause and is followed by the
satellite re-entering safe mode on the next fault trigger (NASA/CP-2017-219455, *op. cit.*). The
simulator's `root_cause_persists` re-safe path exists to make that real operational frustration — a
recovery that "completes" by procedure but doesn't actually fix anything — a genuine planning
consequence rather than something the engine quietly papers over.

## 5. Implementation Guidance

- **A new safe-mode cause must extend `_root_cause_unresolved` with its own persistence check** (the
  way the `cyber` branch checks `cyber_vulnerabilities`) — a cause with no persistence check
  silently always recovers on schedule, which erases the re-safe consequence for that cause.
- **A new recovery-adjacent feature must schedule its steps over real `COMMAND_UPLINK` windows via
  `AccessProvider`**, never resolve instantly — bypassing the windowing would contradict the same
  plan-first / access-gated invariant every other commanding path in the engine respects.
- **Don't conflate `cdh.clear_fault` with `RecoverySystem`** — a new feature needing a quick,
  single-command remedy for a transient fault should extend `buscommands.py`'s verb table, not add a
  new branch to `RecoverySystem`; a feature needing the full confirm→diagnose→patch→re-enable
  multi-pass chain (especially anything with a persistence/root-cause dimension) belongs in
  `RecoverySystem`.
- **A new difficulty tier must add an entry to `PASSES_FOR_DIFFICULTY`**, keeping the
  `min(n, len(wins))` clamp behavior intact so a sparse-contact satellite still recovers (just over
  fewer total passes) rather than the chain silently failing to schedule.
- **Preserve `steps_done`/`current_step`/`blocked_reason` as the UI-facing progress contract** — any
  new recovery path should keep updating these fields so the recovery-strip UI continues to reflect
  genuine procedure state instead of a binary safe/not-safe flag.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer — the recovery strip UI surfaces
`current_step`/`steps_done`/`blocked_reason` from `SafeModeState`; a new recovery-adjacent feature
must keep populating these fields rather than introducing a parallel progress representation.

## 7. Related Topics

[R114](R114-command-and-data-handling.md) (the `SafeModeState`/`cdh.clear_fault` structures this topic's heavier path coexists with),
[R116](R116-cyber-operations-against-space-systems.md) (the cyber-vulnerability persistence check `_root_cause_unresolved` consumes), [R103](R103-satellite-command-and-control.md) (the
command-uplink access windows recovery passes are scheduled against).
