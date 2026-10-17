# FS-132 — Effect Resource Bounds (Salvo Ammunition, Jammer Power Rating)

> **Document ID:** FS-132
> **Version:** 1.1 (2026-10-17, run #175: adds `FR-1480` — a salvo is charged whether it hits or
> misses — and closes Open Question 3 with the project owner's answer; see the change note at the
> end). v1.0: 2026-10-17, run #152.
> **Status:** ✅ Ready for implementation planning (v1.1 delta: `FR-1480`). The v1.0 scope
> (`FR-1460`, `FR-1470`) is built: `IP-1320` `VERIFIED` (`VR-1320`).
> *(Status line updated 2026-10-17, pipeline run #163, `BL-0200`: it described the spec's readiness for planning, which lagged the built Feature. Open Questions recorded below are historical unless marked otherwise; the cited package's Design Decisions record how each was settled where the build needed it.)*
> **Approved input:** the Feature Catalog entry `FEAT-1400` (Five-D's Counterspace Effect
> Resolution) in [`docs/feature-planning/03-feature-catalog.md`](../feature-planning/03-feature-catalog.md),
> following the FS-130/FS-131 convention. This spec covers the **resource-bound slice** of
> `FEAT-1400` only — `FR-1460` and `FR-1470`, the two leaves the run #151 sweep added, and (v1.1)
> `FR-1480`, an `FR-1400` child added 2026-10-17 (`BL-0249`) that joins `FEAT-1400` by the same
> parentage rule; the catalog row does not list it yet (`BL-0275`, routed to `05`). The rest of
> `FEAT-1400` is specified elsewhere: `FR-1410`/`FR-1420` in [FS-105](FS-105-spacecraft-operations.md),
> `FR-1430` in [FS-124](FS-124-debris-field-persistence-estimate.md), `FR-1440`/`FR-1450` in
> [FS-129](FS-129-jamming-delivery-and-effect-detectability.md). `Affected Subsystems`/
> `Affected Interfaces`/`Related ADRs` are carried forward from the catalog entry. The catalog entry
> was not edited.
> **Dependencies:** [FS-105](FS-105-spacecraft-operations.md) (the engage/jam order paths and
> effect resolution this spec bounds); [FS-102](FS-102-command-scheduling.md) (execute-time
> re-validation, `FR-3410`).
> **Referenced By:** [IP-1320](../implementation/packages/IP-1320-effect-resource-bounds.md) (Implementation Package, ✅ `VERIFIED` 2026-10-17 via [VR-1320](../implementation/verification/VR-1320-effect-resource-bounds.md)); [IP-1321](../implementation/packages/IP-1321-missed-salvo-consumes-rounds.md) (Implementation Package for the v1.1 `FR-1480` delta, ✅ `VERIFIED` 2026-10-17 via [VR-1321](../implementation/verification/VR-1321-missed-salvo-consumes-rounds.md)); [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0238`, `BL-0245`, `BL-0249` (closed);
> [docs/requirements/01-functional-requirements.md](../requirements/01-functional-requirements.md)
> `FR-1460`, `FR-1470`, `FR-1480`; [ADR-0037](../architecture/adr/ADR-0037-jammer-power-is-a-rating-not-a-consumable.md);
> [`03-feature-catalog.md`](../feature-planning/03-feature-catalog.md) `FEAT-1400`
> **Produces:** three resource-bookkeeping guarantees on the effect path: an effector never fires
> more rounds than it holds, every salvo fired is charged whether it hits or misses, and jamming
> never changes a jammer's power rating.
> **Feature Mapping:** FS-132 (this document)
> **Related Topics:** [FS-125](FS-125-maneuver-ledger.md) (the Δv analogue: `FR-1310`'s bound and
> its execute-time re-check), [FS-127](FS-127-effect-authorization-gating-and-live-roe.md) (ROE
> gate on the same `engage` validation path)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

## Feature ID

FS-132

## Title

Effect Resource Bounds (Salvo Ammunition, Jammer Power Rating)

## Purpose

GDS-04 §1.2 states that an asset's resource levels cannot go negative. As built (2026-10-17), two
effect paths break that rule: a kinetic engagement may request more rounds than the effector
holds, and a successful jam subtracts its draw from the jammer's power figure, which defaults to
0 W. Both leave a negative number in ground truth, god view and save files. This Feature brings
both paths back inside the domain-model constraint (`FEAT-1400` Purpose: "resource side effects
tracked explicitly"). A third gap (v1.1): a salvo that misses costs no rounds, although fired
interceptors are spent; the project owner decided that every shot fired is charged (`FR-1480`).

## Scope

In scope:

- The ammunition bound on a kinetic engagement, at validation (preview and issue) and at
  execution (`FR-1460`).
- Removing jamming's effect on the jammer's power rating (`FR-1470`, `ADR-0037`).
- Charging a fired salvo whether it hits or misses (`FR-1480`, v1.1).

Out of scope:

- Enforcing a power rating (refusing a jam whose requested power exceeds the rating). `ADR-0037`
  excludes it, and `FR-1470`'s Notes say it would need an owner request.
- Range rules for other order parameters: a salvo of zero or less, a fractional salvo, and negative
  power, bandwidth or dwell (candidate `CR-25`, not baselined).
- *(v1.0 only: whether a failed engagement should consume its salvo — Open Question 3, now
  closed and in scope as `FR-1480`.)*
- Partial salvos: a salvo is charged as a whole; there is no per-round hit/miss accounting
  (`FR-1480` charges "the salvo").
- The Δv bound (`FR-1310`, FS-125) and directed energy (FS-105 v1.1).

## Requirements Implemented

- **`FR-1460`** — Reject a kinetic engagement whose salvo exceeds the effector's remaining
  ammunition (Must).
- **`FR-1470`** — Leave a jamming effector's power rating unchanged when a jam executes (Must).
- **`FR-1480`** — Charge a kinetic engagement's salvo against the effector's ammunition whether the
  engagement hits or misses (Must; v1.1).

Related, not implemented here: `FR-1410` (resource consumption as a side effect, FS-105),
`FR-3410` (execute-time re-validation of resources, FS-102), `FR-5180` (bus power authoring fields;
the same `power_w` field is dead for satellites).

## User Workflows

**W1 — Red (or White) plans an oversized salvo.** A Red operator with kinetic ROE selects an
interceptor asset with `N` rounds left, chooses `engage` against a weapons-quality-tracked target,
and enters a salvo larger than `N`. The live dry-run preview shows the order as blocked, with a
reason that says there is not enough ammunition, and **Issue** stays disabled. If the operator
sends the order anyway (for example through the HTTP API), it is rejected with the same reason and
nothing is scheduled.

**W2 — Red plans a salvo within the remaining rounds.** Same as W1 with a salvo of `N` or fewer.
The preview shows the order as valid; Issue schedules it at the next `weapon_engagement` window.

**W3 — Two engagements are queued that together exceed the rounds.** An interceptor holds 2
rounds. Red issues two 2-round engagements at different targets before either executes. Each
passes validation on its own (2 ≤ 2). The first executes and resolves. When the second reaches its
window, the effector holds fewer rounds than the salvo needs; the second engagement does not
resolve, the event record shows it failed at execution, and the effector's rounds stay at zero or
above.

**W3a — Red's salvo misses (v1.1, `FR-1480`).** An interceptor holds 2 rounds. Red issues a
1-round engagement; it executes at its window and misses (the target survives). The effector now
holds 1 round — the miss cost the round it fired, exactly as a hit would have. A later 2-round
engagement from the same effector is refused `insufficient_ammo` at preview and issue, because only
1 round remains.

**W4 — Blue or Red jams.** A cell orders a `jam` from a jammer (any authored power rating,
including the default 0 W). The jam resolves exactly as it does today. Afterwards the jammer's
power rating, as seen in White's god view and in a save file, is the rating the vignette authored.

## System Behaviour

1. **Validation bound (`FR-1460`).** When an `engage` order is validated, its salvo — taken as the
   number of rounds the engagement would actually consume — is compared with the effector's
   remaining ammunition. A salvo larger than the remaining rounds is rejected with a reason that
   states insufficient ammunition. The comparison runs in the shared validation step, so the
   dry-run preview and the issue path give the same answer (`FR-1460` AC: "by both the preview and
   issue paths"), and a rejected order schedules nothing, books nothing and logs no effect.
   - The existing order of checks is kept: ROE, then ammunition, then the weapons-quality track. An
     effector with no rounds at all keeps its existing `no_ammo` result.
   - *"The rounds it would consume":* as built, the consumption step charges at least one round for
     any salvo (`max(1, salvo_n)`). The bound uses that same figure, so the check and the charge
     cannot disagree. The zero-or-negative salvo range rule itself stays out of scope (`CR-25`).
2. **Execute-time bound (`FR-1460` Postcondition, `FR-3410`).** When an engagement reaches its
   execution moment, the effector's remaining rounds are re-checked against the salvo before the
   effect resolves. If the rounds no longer cover it (W3), the engagement does not resolve and no
   rounds are charged; the effect record shows a failed execution with the reason, mirroring how a
   manoeuvre that no longer has enough Δv fails at execution (FS-125, `FR-1310`). This is what
   makes "ammunition is never negative after the engagement executes" hold when orders are queued.
3. **Every fired salvo is charged, hit or miss (`FR-1480`, `FR-1460` AC; v1.1).** An engagement
   that passes the execute-time re-check (behaviour 2) is fired: it resolves, and the effector is
   left with `N` minus the salvo **whether the resolution succeeds or fails**. *(v1.0 charged only
   a successful engagement.)*
   - "Fired" means "reached resolution". That includes an engagement whose target was already
     destroyed when its window came (the resolver reports it as not achieved without a roll); no
     source describes an abort, and `FR-1480`'s Notes treat it as fired.
   - An engagement that fails the execute-time re-check (behaviour 2) is still **not** fired and
     charges nothing; behaviour 2 runs first, so the charge can never drive the rounds negative.
   - The charge does not change the resolution: the success probability, the RNG draw and the
     effect outcome for the same seed are exactly as before. Only the rounds bookkeeping after a
     miss changes.
4. **Jamming does not touch the rating (`FR-1470`, `ADR-0037`).** When a jam executes, successful
   or not, the jammer's power rating is not changed. The jam's success probability, footprint,
   link target, effect outcome and effect-log entry are exactly as before for the same seed —
   effectiveness already comes from the order's own power parameter, not from the rating.
5. **Determinism (NFR-1500 via FEAT-1100, `CLAUDE.md` invariant 1).** All three changes are pure
   comparisons, the removal of a write, or the removal of a condition on a write, inside the
   deterministic event handlers. Neither reads a
   clock nor draws from the RNG. For the same initial state, event log and seed, the engine
   produces the same state, except that the jammer's rating no longer drifts and an oversized
   execute is a recorded failure instead of a negative count.

## Subsystem Responsibilities

| Subsystem (GDS-03 / ICD) | Responsibility here |
|---|---|
| **C1 Simulation Engine** — order system | Validation bound (behaviour 1); execute-time re-check before resolution (behaviour 2); the consumption step charges every fired salvo regardless of outcome (behaviour 3, v1.1); the consumption step stops subtracting from the jammer's power rating (behaviour 4). |
| **C1 Simulation Engine** — effect resolver | Unchanged. It still resolves the effect and reports success; it does not own resource bookkeeping. |
| **C2 Session/Application Layer** | Unchanged. It already relays the validation reason to the caller and the dry-run preview to the console. |
| **C4 Operator Console** | Shows the new rejection reason with a plain-language tip, like the existing reason tips (see Open Question 1). |

No new subsystem.

## Interfaces Used

- **INT-0008** (SessionManager → Engine Clock/Scheduler/EventLog/OrderSystem) — the order issue,
  dry-run and execute handlers live behind it. No change to its shape.
- **INT-0004** (Cell Operator ↔ Operator Console) — carries the rejection reason and its tip.

## Data Model Changes

None. The effector's ammunition and the jammer's power rating already exist as asset resource
levels (GDS-04 §1.2 "Persistent state"). No field is added, renamed or removed. A jammer's rating
simply stops changing.

## State Changes

- An `engage` order that fails the validation bound is **rejected** and never enters the queue.
- An `engage` that fails the execute-time re-check produces a **failed** effect-log record; the
  effector's rounds are unchanged and the target is unaffected.
- *(v1.1)* An `engage` that is fired and **misses** reduces the effector's rounds by its salvo
  (previously unchanged). Its effect-log record is unchanged. A saved session is replayed from its
  event log, so a session saved before this change that contains a miss will, when loaded, show the
  rounds charged for that miss; a later engagement in it that the miss now leaves uncovered fails
  the execute-time re-check (behaviour 2) instead of resolving.
- A jam no longer changes the jammer's `power_w`. Previously saved sessions that already carry a
  negative jammer rating load unchanged (save files are replayed, not re-validated against this
  rule); new play does not create negative ratings.

## Error Handling

| Condition | Observable result |
|---|---|
| Salvo larger than remaining rounds, at preview or issue | Rejected, reason states insufficient ammunition; Issue pre-disabled; nothing scheduled |
| Effector holds no rounds | Rejected `no_ammo` (unchanged) |
| Rounds spent by an earlier queued engagement before this one executes | Not resolved; failed effect-log record; no rounds charged |
| Fired engagement misses (v1.1) | Effect-log record as before (not achieved); salvo charged |
| Fired engagement whose target was already destroyed (v1.1) | Effect-log record as before (not achieved); salvo charged |
| Jam on a jammer rated 0 W (the default) | Resolves as before; rating stays 0 |

## Performance Considerations

One integer comparison at validation and one at execution. No new access computation, no extra
pass through the scheduler. Replay-safe and dry-run-safe like the existing checks (NFR-1500,
NFR-1700 via FEAT-1100).

## Security Considerations

None new. The checks are engine-internal and cell-agnostic: the same bound applies to Blue, Red
and White-issued engagements. Fog-of-war (ADR-0004) is unaffected — the reason concerns the
issuing cell's own effector.

## Acceptance Criteria

1. Given an effector with `N` rounds (`N ≥ 1`), an `engage` with a salvo of `N + 1` is rejected at
   dry-run **and** at issue with a reason stating insufficient ammunition, and the order queue,
   sensor bookings and event log are unchanged by the rejected issue.
2. Given the same effector, an `engage` with a salvo of exactly `N` is accepted; once it executes
   the effector holds 0 rounds afterwards, **whether it succeeds or fails** (v1.1: was "if it
   succeeds").
3. Given an effector with 0 rounds, `engage` is still rejected `no_ammo`.
4. Given an effector with 2 rounds and two accepted 2-round engagements queued, after both
   execution moments have passed the effector holds 0 or more rounds (never negative), the second
   engagement is recorded as failed at execution, and its target was not affected by it.
5. Given a jammer with an authored power rating `R` (including the default 0), after it executes a
   successful jam and after it executes a failed jam, its power rating in ground truth is `R`.
6. For a fixed vignette and seed, a scripted sequence of jams produces the same effect-log outcomes
   (success/fail, achieved outcome, category, target) before and after this change.
7. The determinism property test and the engine import guard stay green.
8. *(v1.1, `FR-1480`)* Given an effector with 2 rounds and an accepted 1-round engagement that
   executes and **fails**, the effector holds 1 round afterwards and the target is not destroyed;
   a following 2-round `engage` from it is rejected `insufficient_ammo`. Given an accepted
   engagement whose target is already destroyed at its execution moment, the salvo is charged.
9. *(v1.1)* For a fixed seed, an engagement's effect-log outcome (success/fail, achieved outcome)
   is the same before and after the v1.1 change; only the effector's rounds differ after a miss.
   The live world after a missed engagement equals the world rebuilt by `replay()`.

## Verification Plan

| Criterion | Method |
|---|---|
| 1–5 | Test (automated, engine/session level) — `FR-1460`/`FR-1470` Verification Method: Test |
| 8–9 | Test (automated, engine level) — `FR-1480` Verification Method: Test |
| 6 | Test — compare effect-log outcomes for a fixed seed, with and without the change |
| 7 | Test — `test_determinism.py`, `test_import_guard.py` |

## Dependencies

[FS-105](FS-105-spacecraft-operations.md) (engage/jam paths, `FR-1410`);
[FS-102](FS-102-command-scheduling.md) (execute-time re-validation, `FR-3410`). Catalog edges:
`FEAT-1400` depends on `FEAT-1200`, `FEAT-3100`, `FEAT-3400`.

## Risks

- **Shipped tutorials or tests that rely on the old behaviour.** A test or playbook that asserts a
  negative jammer rating, or fires an oversized salvo, would change. Low likelihood; the package
  should search the tests and the vignette tutorial scripts before changing behaviour.
- **Scripted engagements.** The Red doctrine presets (`session/redai.py`) issue no `engage` orders
  today (checked 2026-10-17), but vignette tutorial scripts and tests do. Any that requests more
  rounds than its effector holds would now be rejected rather than overdraw — intended, but the
  package should check them.
- **(v1.1) Fixtures and scripts that rely on a free miss.** A test, tutorial script or playbook
  that fires a second engagement from a 1-round effector after a miss would now be refused
  `no_ammo`. The package should search the tests and vignette `tutorial`/`coaching` blocks.
- **(v1.1) Old saves replay under the new rule** (State Changes). Intended — the engine has one
  rule — but a facilitator re-opening an old save may see fewer rounds than when it was saved.
- **Execute-time failure visibility.** A W3 failure happens without an operator action at that
  moment. It must be visible in the effect log and AAR the same way a failed manoeuvre is, or a
  player cannot tell why the second strike never landed.

## Open Questions

1. **Rejection reason text (`07`-level, default given).** `FR-1460` requires "a reason stating
   insufficient ammunition" but names no code. Default: a new reason distinct from `no_ammo`,
   mirroring the existing `insufficient_delta_v` (FR-1310), with a console tip saying how many
   rounds remain. Reusing `no_ammo` would also satisfy the requirement but would read as "no
   rounds at all" when some remain. Decided by `07`; it must also reach the console's reason tips
   and the manual's reason list (`09` §10, `BLU-3`/`RED-3`/`RED-5`).
2. **Execute-time failure record (`07`-level, default given).** The failed-execution record should
   follow the existing failed-manoeuvre shape in the effect log (template, target, achieved =
   failed, success = false), so AAR and assessment readers need no new case. `07` confirms against
   the effect-log consumers (`aar.py`, `assessment.py`).
3. **Does a failed engagement consume its salvo? — CLOSED 2026-10-17 (v1.1): yes.** The project
   owner decided that misses consume interceptors too: ammunition is charged on every shot fired,
   not only on hits (`BL-0249`). `04` baselined it as `FR-1480` (promoted from `CR-28`) and
   amended `FR-1460`'s Acceptance Criteria; this spec implements it as System Behaviour 3 and
   Acceptance Criteria 2, 8 and 9. *(v1.0 text, kept for the record: as built, rounds were charged
   only when the engagement succeeded; no requirement said either way; this spec kept the as-built
   rule and routed the question to `04`.)*

## Related ADRs

ADR-0012 (five-D effects resolution, carried from `FEAT-1400`); ADR-0037 (jammer power is a
rating, not a consumable).

## Related Interfaces

INT-0016 (White Cell inject path — not used; injects do not issue engagements);
INT-0014 (AAR replay — reads the failed-execution record but is not changed).

## Change note — v1.1 (2026-10-17, run #175)

- **Added `FR-1480`** (Must; promoted from `CR-28` on the project owner's 2026-10-17 decision,
  `BL-0249`): Requirements Implemented, Scope, Purpose, Produces, W3a, System Behaviour 3,
  Subsystem Responsibilities (C1), State Changes, Error Handling, Acceptance Criteria 2 (amended),
  8 and 9 (new), Verification Plan, Risks.
- **Closed Open Question 3** with the owner's answer (a missed salvo consumes its rounds).
- Unchanged: behaviours 1, 2 and 4, Acceptance Criteria 1 and 3–7, interfaces, data model (no
  field added), ADRs. `FR-1480` joins `FEAT-1400` by parentage; the catalog row is updated by `05`
  (`BL-0275`). The catalog entry was not edited here.
