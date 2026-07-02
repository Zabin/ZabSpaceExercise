# IMP-105B — Spacecraft Operations: Effect Resolution & Console UX

> **Document ID:** IMP-105B
> **Version:** 1.0
> **Status:** ✅ Done (as-built — documents existing, test-covered code)
> **Dependencies:** [FS-105](../features/FS-105-spacecraft-operations.md)
> **Referenced By:** [IMP-105A](IMP-105A-spacecraft-operations-bus-payload.md) (the sibling package covering bus/payload command & telemetry)
> **Produces:** the executed-effect surface [FS-107](../features/FS-107-after-action-review.md) replays and [FS-201](../features/FS-201-competency-assessment.md) assesses
> **Feature Mapping:** FS-105 (§3.2, §3.3, §4)
> **Related Topics:** [`spacesim/engine/effects.py`](../../spacesim/engine/effects.py), [`spacesim/engine/jam.py`](../../spacesim/engine/jam.py), [`spacesim/engine/engage.py`](../../spacesim/engine/engage.py), [`spacesim/engine/cyber.py`](../../spacesim/engine/cyber.py)

[↑ Implementation index](INDEX.md) · [Docs index](../INDEX.md)

> **Superseded.** This document's content has been re-derived, re-verified against the current
> source tree, and re-published under the canonical `docs/implementation/packages/` tier as
> [**IP-1051**](../implementation/packages/IP-1051-spacecraft-operations-effects-console.md). This
> file is retained for historical reference and is not deleted, but
> [`IP-1051`](../implementation/packages/IP-1051-spacecraft-operations-effects-console.md) is the
> document of record going forward — see
> [`docs/implementation/00-master-build-plan.md`](../implementation/00-master-build-plan.md)
> §"Relationship to the prior `docs/implementations/` corpus."

## 1. Situation

**As-built.** This is the second of FS-105's two lettered packages (per
[`MSTR-006`](../master/MSTR-006-governance-principles.md) §4 size discipline): it covers §3.2 (the five effect categories'
operator-facing controls), §3.3 (escalation/ROE framing), and §4 (human-factors requirements),
where [IMP-105A](IMP-105A-spacecraft-operations-bus-payload.md) covers §3.1 (bus/payload commands).

## 2. The shared effect model

Every windowed effect category (jam, engage, observe-as-effect, downlink-denial) resolves through
one shared shape: `EffectInstance` (`effects.py:35`) carries `category`, `reversible`, `kinetic`,
`debris_risk`, `attribution`, `escalation_weight`, `success_prob`, and (for cyber)
`access_vector` — a single typed record every category populates differently rather than each
category inventing its own resolution schema. `EffectResolver.resolve()` (`:83`-`:84`,
implemented by `ModerateEffectResolver`, `:103`) returns `EffectOutcome` (`:60`): `achieved_outcome`,
`success`, and a `side_effects` list — `political_consequence` side effects are appended to
`world.consequences` (`orders.py:635`-`636`) and are what the console's escalation/ROE framing
(§3.3) reads, satisfying FS-105 §3.3's "escalation tagging traces to real theory" requirement by
construction: the consequence record, not a UI label, is the source of truth.

`OrderSystem._h_effect` (`orders.py:623`) is the handler every windowed effect category schedules
into — one dispatch point feeding `effect_log`/`consequences`, which is what lets the console
render all five effect categories through one history view rather than five parallel logs.

## 3. Per-category tradeoff surfaces

- **EW/jam** (FS-105 §3.2 bullet 2 — "modulation tradeoff explicit"): `jam.py`'s
  `effective_radius_km()` (`:57`), `effective_success_prob()` (`:69`), and `power_draw_w()`
  (`:111`) all take the same `mod` (modulation) parameter — barrage/spot/sweep/deceptive — so
  effectiveness, footprint, and power cost move together as one tradeoff the operator sets
  explicitly via `available_modulations()` (`:117`), not a single "jam" button hiding the choice.
  `jam_footprint_polygon()` (`:87`) is what the console's footprint overlay renders — genuine
  geometry, not a cosmetic radius.
- **Cyber** (FS-105 §3.2 bullet 3 — "non-windowed resolution model clear"): `_plan_cyber`
  (`orders.py:573`) sets `order.earliest_window = None` with the inline comment "cyber is not
  pass-gated (resolves now, against posture)" (`:575`) — the order itself carries the signal the
  console must render differently (no window countdown UI for cyber, per [IMP-102A](IMP-102A-command-scheduling.md) §3's
  "the non-windowed exception"). `cyber.py`'s `effective_success()` (`:65`) and
  `attribution_score()` (`:75`) take `vector`/`target_posture`/`dwell_s` — the operator's visible
  inputs — and `available_vectors()`/`available_payloads()` (`:94`, `:98`) enumerate the catalog
  the console offers.
- **Kinetic/DE engagement** (FS-105 §3.2 bullet 4 — "consequence-confirm pattern preserved"):
  `engage.py`'s `kill_probability()` (`:62`) and `kill_probability_from_class()` (`:124`) compute a
  real Pₖ from `miss_km`/`interceptor_dv_ms`/class, and `debris_cone_estimate()` (`:162`) is what
  backs the kinetic-consequence preview `InProcessSession.preview_consequence()`
  (`inprocess.py:466`, already cited in [IMP-101A](IMP-101A-mission-planning.md)) surfaces before commitment — the
  same real math drives both the pre-commit preview and the post-commit `EffectOutcome`, so the
  confirm dialog's numbers cannot diverge from what actually happens (the `dry_run()`/`issue()`
  parity pattern, applied here to kinetic consequence specifically rather than window/Δv).
- **Maneuver Δv preview/confirm** (FS-105 §3.2 bullet 1): the committed maneuver handler
  (`_h_maneuver`, `orders.py:646`) consumes the identical six-entry-mode `engine/maneuver.py`
  computation `InProcessSession.compute_maneuver()` (`inprocess.py:314`) exposes pre-commit — this
  is the commit-side half of the parity [IMP-101A](IMP-101A-mission-planning.md) §4 documents from the preview side.
- **Window display** (FS-105 §3.2 bullet 5): every windowed category's window comes from the same
  `AccessProvider.windows()` (`access.py:107`) [IMP-101A](IMP-101A-mission-planning.md) §4 and [IMP-102A](IMP-102A-command-scheduling.md) §2 already
  document — no category-specific display-only window estimator exists.

## 4. Defender-side modifiers (escalation-relevant realism)

The Jun 2026 commands audit (`orders.py:89`-`:100`) wired defensive verbs into the same Pₛ/Pₖ math
the attacker's effect resolves against: `_FREQ_HOP_RESIDUAL = 0.4` (frequency-hopping cuts residual
jam success to 40%) and `_EVASION_RESIDUAL = 0.4` (active evasion cuts kinetic Pₖ to 40% during
fly-out) are read inside `ModerateEffectResolver.resolve()`'s `_effective_probability()`
(`effects.py:168`) — meaning a defensive bus command issued before an attack genuinely changes the
attacker's success probability, not just a cosmetic defense indicator. This is what makes the ROE
chip and defensive posture genuinely consequential rather than decorative (FS-105 §3.3 bullet 2).

## 5. Human-factors requirements (FS-105 §4)

- **Intentional friction**: the window-gating behavior in §3 (and [IMP-102A](IMP-102A-command-scheduling.md) §2's four-state
  lifecycle) is the mechanism, not a UI delay layered on top — there is no code path that lets an
  effect resolve faster than the real access geometry permits except cyber's explicitly-flagged
  exception.
- **Belief-vs-truth legibility**: `_victim_cell()` (`effects.py:202`) and the fog-of-war boundary
  [IMP-103A](IMP-103A-custody-management.md) §4 documents jointly ensure a cell's console only ever renders effects/custody
  scoped to itself; `is_link_denied()`/`is_link_spoofed()` (`:207`, `:214`) are read-only queries a
  cell's own console consults, never another cell's ground truth.
- **Panel-manager contract** (§4 bullet 3, every new panel a first-class panel-manager citizen):
  this is a console-implementation discipline rather than an engine behavior; it is asserted as a
  requirement on any future console work, not separately verifiable from `engine/` code, and is
  flagged here as a constraint for whoever implements new panels rather than as already-tested
  engine behavior.

## 6. Satisfying FS-105 §3.2/§3.3/§4's capability requirements

Mapped one-by-one in §3 (effect-category tradeoffs), §4 (defender modifiers feeding §3.3's
escalation framing), and §5 (human factors) above.

## 7. Test coverage (existing)

`effects.py`'s resolver, the jam/engage/cyber math modules, and the defender-modifier wiring are
each covered by their respective existing test files (effect resolution, jam, engage, cyber test
suites); the kinetic consequence-preview/commit parity is covered wherever both are exercised in
the same test. No new tests are proposed by this package.

## 8. Related Topics

[FS-105](../features/FS-105-spacecraft-operations.md) (the spec this documents, §3.2-4), [IMP-105A](IMP-105A-spacecraft-operations-bus-payload.md) (the sibling package, §3.1),
[IMP-101A](IMP-101A-mission-planning.md) (the preview-side parity this package's commit-side math mirrors), [IMP-103A](IMP-103A-custody-management.md) (fog-of-war
boundary), [`spacesim/engine/effects.py`](../../spacesim/engine/effects.py), [`spacesim/engine/jam.py`](../../spacesim/engine/jam.py), [`spacesim/engine/engage.py`](../../spacesim/engine/engage.py),
[`spacesim/engine/cyber.py`](../../spacesim/engine/cyber.py).
