# IMP-107A — After Action Review: Replay/Scrub/Branch-Compare

> **Document ID:** IMP-107A
> **Version:** 1.0
> **Status:** ✅ Done (as-built — documents existing, test-covered code)
> **Dependencies:** [FS-107](../features/FS-107-after-action-review.md)
> **Referenced By:** [IMP-106A](IMP-106A-white-cell-dashboard.md) (the White-only trigger controls that invoke this instrument)
> **Produces:** the replay/snapshot surface [FS-201](../features/FS-201-competency-assessment.md)'s "belief-truth divergence" dimension would read from
> **Feature Mapping:** FS-107
> **Related Topics:** [`spacesim/session/aar.py`](../../spacesim/session/aar.py), [`spacesim/engine/simulation.py`](../../spacesim/engine/simulation.py), [`spacesim/session/scene.py`](../../spacesim/session/scene.py)

[↑ Implementation index](INDEX.md) · [Docs index](../INDEX.md)

> **Superseded.** This document's content has been re-derived, re-verified against the current
> source tree, and re-published under the canonical `docs/implementation/packages/` tier as
> [**IP-1070**](../implementation/packages/IP-1070-after-action-review.md). This file is retained
> for historical reference and is not deleted, but [`IP-1070`](../implementation/packages/IP-1070-after-action-review.md)
> is the document of record going forward — see
> [`docs/implementation/00-master-build-plan.md`](../implementation/00-master-build-plan.md)
> §"Relationship to the prior `docs/implementations/` corpus."

## 1. Situation

**As-built.** This package documents the existing `session/aar.py` replay/scrub/branch-compare
instrument.

## 2. Replay as the foundation

`state_at(mgr, seq)` (`aar.py:40`) is the single primitive everything else in this module is built
on: it calls `replay(initial_state, seed, eventlog, handlers, up_to_seq=seq)`
(`engine/simulation.py`) to reconstruct the exact `WorldState` at any event-log sequence number.
Because the engine is deterministic (per `CLAUDE.md`'s load-bearing invariant #1 —
`(initial_state, ordered eventlog, seed) → byte-identical state`), this reconstruction is exact,
not an approximation, and **read-only**: `state_at()` builds a fresh `WorldState` from scratch
on every call rather than mutating the live session's `mgr.sim.world` — satisfying FS-107 §3
bullet 1's replay-safety requirement by the same mechanism `dry_run()` ([IMP-101A](IMP-101A-mission-planning.md) §2) and
`scene.py` ([IMP-103A](IMP-103A-custody-management.md) §5) already use: a pure function over historical state, never a side
effect on it.

`objectives_at(mgr, seq)` (`:51`) and `snapshot_at(mgr, seq)` (`:56`) are both thin wrappers around
`state_at()` — the scrubber's "jump to any decision point" capability is just calling either with
a different `seq`; `snapshot_at()`'s payload (clock, objectives, per-asset health/bus-mode,
debris count) is intentionally "light" (per its docstring, `:57`) for fast scrubbing rather than a
full god-view dump.

## 3. Belief-vs-truth comparison

FS-107 §3 bullet 2 requires the god-view-vs-belief diff to be a first-class, queryable capability.
The mechanism is compositional rather than a dedicated AAR method: `state_at(mgr, seq)` returns a
raw `WorldState`, and `scene.build_scene(world, cell)` (`scene.py:81`) — the same per-cell
fog-of-war render [IMP-103A](IMP-103A-custody-management.md) §4 documents for the live session — accepts any `WorldState`,
not only the live one. Calling `build_scene(state_at(mgr, seq), "blue")` and comparing it against
`state_at(mgr, seq)` directly (god truth) at the identical `seq` is the belief-vs-truth diff FS-107
and [DOM-002](../domains/DOM-002-assessment-framework.md) §4 require — both sides of the comparison are produced by code paths this
package and [IMP-103A](IMP-103A-custody-management.md) already document, composed rather than duplicated. This is also what
keeps the diff visually distinguishable at every timeline point (FS-107 §5's human-factors
requirement): belief and truth are never merged into one rendered object at any `seq`.

## 4. Branch comparison

`report(mgr)` (`aar.py:90`) builds an `AARReport` (`:31`): a `timeline` of `AAREvent`s
(`:23`) filtered to `DECISION_KINDS` (`:19` — `execute_effect`, `execute_maneuver`,
`execute_downlink`, `execute_observe`, `inject`, `recovery_finish`, `recovery_confirm`; the filter
exists so the timeline reads as decisions, not every scheduling/bookkeeping event), each with a
human-readable `_summarize()` (`:72`) string, plus `consequences` and `final_objectives`.
`compare_branches(report_a, report_b)` (`:105`) diffs two such reports — event counts and which
`(side, objective_id)` pairs flipped between them (`:110`-`:112`) — operating purely on two already-
built `AARReport`s, neither of which is the canonical session: producing `report_b` from a
diverged replay (a different rewind point or a different decision taken from there) never alters
`report_a`'s session, satisfying FS-107 §3 bullet 3 ("examine 'what if' without altering the
canonical record") because the comparison function itself has no session-mutating capability at
all — it is a pure diff over two data objects.

## 5. Self-assessment use

Nothing in `report()`/`compare_branches()`/`snapshot_at()` is gated to a White-only caller or
requires facilitator state — `aar_report`/`aar_objectives_at`/`aar_snapshot_at`
(`inprocess.py:742`-`750`) take only a session id and (optionally) a cell-scoped call via
`build_scene()` as §3 describes. This satisfies FS-107 §3 bullet 4: a trainee invoking the same
calls against their own session to walk their own decision points requires no new engine feature
beyond what a facilitator uses — only the surrounding UI affordance and facilitation guidance
([FS-106](../features/FS-106-white-cell-dashboard.md)/[DOM-003](../domains/DOM-003-white-cell-framework.md)) differ between the two uses, not the instrument.

## 6. Export

`export_csv(rep)` (`aar.py:120`) renders an `AARReport` as three CSV sections (META, TIMELINE,
OBJECTIVES) — the FUTURE-WORK §10.E.20 item this docstring cites is the export *format's* further
evolution, not this package's scope; the as-built CSV export already exists and is what this
package documents.

## 7. Satisfying FS-107's capability requirements

- **Read-only w.r.t. the live session** (§3 bullet 1): §2 — `state_at()` is a pure reconstruction.
- **Belief-vs-truth comparison first-class** (§3 bullet 2): §3 — `build_scene()` composed with
  `state_at()` at a shared `seq`.
- **Branch comparison without altering the canonical record** (§3 bullet 3): §4 —
  `compare_branches()` is a pure diff over two `AARReport`s.
- **Doubles as self-assessment with no new engine feature** (§3 bullet 4): §5.
- **Educational value stated** (§3 bullet 5): per FS-107 §1/Purpose, AAR's distinct educational
  value is reflective learning against one's own past belief state — this package adds no new
  educational-value claim beyond what FS-107 already states; it documents the mechanism only.

## 8. Test coverage (existing)

Replay exactness is gated by the Phase-1 determinism property test (`test_determinism.py`), which
AAR's `state_at()` depends on directly; AAR-specific behavior (timeline filtering, branch-compare
flips, CSV export) is covered by the existing AAR test suite. No new tests are proposed by this
package.

## 9. Related Topics

[FS-107](../features/FS-107-after-action-review.md) (the spec this documents), [IMP-103A](IMP-103A-custody-management.md) (the `scene.py`/custody render this
package composes with for belief-vs-truth diffs), [IMP-106A](IMP-106A-white-cell-dashboard.md) (the White-only trigger controls
hosting this instrument), [`spacesim/session/aar.py`](../../spacesim/session/aar.py), [`spacesim/engine/simulation.py`](../../spacesim/engine/simulation.py).
