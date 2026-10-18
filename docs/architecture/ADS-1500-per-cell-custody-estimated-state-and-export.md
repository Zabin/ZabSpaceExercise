> **Document ID:** ADS-1500
> **Version:** 1.0
> **Status:** ✅ Authored
> **Dependencies:** [R105](../research/encyclopedia/R105-custody-theory.md) (Custody Theory),
> [ADR-0013](adr/ADR-0013-custody-weapons-quality-gate.md) (custody/weapons-quality gate),
> [ADR-0004](adr/ADR-0004-fog-of-war-at-boundary.md) (fog-of-war at the boundary),
> [ADR-0002](adr/ADR-0002-deterministic-core.md) (deterministic core — the replay mechanism this
> document reuses), `docs/pipeline/backlog.md` `BL-0068` (external validation report, 26 Sep 2026,
> item B2), `docs/requirements/01-functional-requirements.md` `FR-1510` (confidence decay), `FR-7420`
> (cell-observed ephemeris export, baselined but blocked pending this document)
> **Referenced By:** FS-103 (Custody Management — not yet updated; see Consequences)
> **Produces:** the resolution of `BL-0068`'s domain-model question; unblocks `FR-7420`'s
> verifiability and a future `06-feature-specification` pass for the B3 cell-observed export
> **Feature Mapping:** FS-103, and the not-yet-drafted Feature Spec for `FR-7410`/`FR-7420`
> (ephemeris export)
> **Related Topics:** [R105](../research/encyclopedia/R105-custody-theory.md) §3 ("Custody is
> per-cell"), `session/aar.py` (the existing replay/scrub mechanism this document's Decision 2
> reuses rather than duplicates)

[↑ Architecture index](INDEX.md) · [Docs index](../INDEX.md)

# ADS-1500 — Per-Cell Custody: Estimated-State History & Export

*Authored via Workflow B (per-cluster synthesis) to resolve `BL-0068` (item B2 of the external
validation report, 26 Sep 2026), which entered the pipeline at this stage rather than
`04-requirements-engineering` directly because the requester's own framing — "track state is a
copy of truth; no independent estimated element-set history" — asserts a domain-model defect that
needs verifying against the actual `engine/custody.py` implementation before any requirement can be
written against it. This document verifies that framing (finding it half right, half already
solved — see Executive Design Overview), and designs the missing half: how a cell's *history* of
belief about an object's state is reconstructed for export, without adding a new stored data
structure.*

## 1. Executive Design Overview

**The premise that a cell's `Track` is a live copy of ground truth is not accurate as of `32ca02a`.**
`engine/custody.py`'s `Track.state_estimate` is populated once, at observation time (`orders.py:745`,
`ssn.py:386`), as a snapshot of the target's orbital elements at that instant — it is never
re-synced to ground truth afterward. `session/scene.py`'s render path (`_geo(t.state_estimate, now)`)
forward-propagates that frozen snapshot using the same `Propagator` seam ground truth itself uses,
rather than re-reading `Asset.orbit` live. **This means an unobserved manoeuvre already does not
leak into a cell's belief** — the exact behavior `BL-0068` asks for — because the target's own truth
orbit changes independently of the frozen snapshot the cell is propagating forward. This is
confirmed by direct reading, not assumed; see Decision 1.

**What is genuinely missing, and is this document's actual design contribution, is two things:**
(a) there is no stored *history* of past `state_estimate` snapshots — only the current one, which
`observe()` overwrites in place on every re-observation — so a query for "what did cell C believe
object X's state was at a *past* time T" cannot be answered from live state alone once T predates
the most recent observation; and (b) no export path (TLE/OMM, cell-scoped, fog-of-war-respecting)
exists at all yet. Decision 2 shows (a) does not require a new stored structure: the engine's
existing deterministic replay (`ADR-0002`, `engine/simulation.py::replay`, already used by
`session/aar.py::state_at` for AAR scrub) reconstructs `WorldState.tracks` — including whatever
`state_estimate` was current — at any past point, which is exactly a "history" query answered by
replay instead of storage. Decision 3 designs the export capability itself.

## 2. System Architecture

No new subsystem. The design adds one new Session-Layer capability (a cell-observed ephemeris
export function, sibling to the already-baselined `FR-7410` truth export) that composes two
existing seams rather than introducing a third:

```
FR-7420 request (cell C, object X, time span [t1, t2], reference object, format)
        │
        ▼
Session Layer: for each sampled time T in [t1, t2] —
        │
        ├─▶ engine/simulation.py::replay(...) up to the eventlog seq nearest T   (ADR-0002, existing)
        │        — reconstructs WorldState as it existed at T, including cell C's own
        │          Track.state_estimate for X (whatever observation last set it by T)
        │
        ├─▶ session/scene.py-style propagation of that reconstructed state_estimate to exactly T
        │        (the same Propagator seam ground truth and the existing render path both use)
        │
        └─▶ CellController-equivalent binding: only cell C's own TrackCatalog entry is read,
                 never Asset.orbit (ground truth) and never another cell's Track     (ADR-0004)
        │
        ▼
Shared ephemeris serializer (ECI + RIC transform, CSV + CCSDS OEM) — the same serializer FR-7410's
truth export uses, parameterized by which state source fed it
```

No engine (`engine/custody.py`) change is required. The only new code is a Session-Layer export
function that drives replay across a time span instead of to one point (replay-to-one-point is
already what `aar.py::state_at`/`snapshot_at` do for the AAR scrubber) and feeds each reconstructed
instant through the existing propagation/serialization path.

## 3. Domain Model

No new entity. `Track` (§`engine/custody.py`) is unchanged — `state_estimate: Optional[OrbitState]`,
`uncertainty`/`uncertainty_at_obs`, `last_observation`, `confidence` all already carry everything a
single point-in-time belief needs. The "history" this cluster asked for is not a new entity; it is
a *view* over the existing `EventLog` (already the domain model's own record of every state-changing
event, `FR-7110`) filtered to one cell's `Track` mutations. This is the same relationship AAR replay
already has to the event log for the *entire* `WorldState` — this document just applies it narrowly
to one cell's one `Track`.

## 4. User Stories

- *As a Blue-cell operator, I want to export my own cell's believed ephemeris for a target I've been
  tracking over the last hour, so I can hand a TLE to an analyst without exposing ground truth I
  never actually observed.*
- *As White Cell running an AAR, I want to confirm that Blue's exported belief-state ephemeris for a
  contested object diverges from ground truth exactly where Blue's custody lapsed (a confidence dip,
  a missed re-observation window), so I can use the divergence itself as a teaching point.*
- *As a Feature Spec author for `FR-7420`, I want to know I am not required to design a new
  "estimated element-set history" table, so I don't duplicate the event log's own replay guarantee.*

## 5. Functional Requirements

This document does not introduce new numbered FRs (that is `04-requirements-engineering`'s job);
`FR-7420` is already baselined and this document exists to make its Acceptance Criteria verifiable.
The functional behavior this design commits to, for `06-feature-specification` to elaborate:

- A cell-observed ephemeris export for object X over `[t1, t2]` shall, at each sampled time T, use
  the reconstructed `WorldState` at T (via replay to the eventlog position nearest T) to read the
  requesting cell's own `Track.state_estimate` for X as of T, then forward-propagate that snapshot
  to exactly T using the same `Propagator` the render path already uses.
- A time T at which the requesting cell holds no `Track` on X at all (never observed, or T predates
  the cell's first observation) shall produce no belief-state point for that T, distinct from a
  point where the cell's belief exists but is now low-confidence — an empty query result at some T,
  not a fabricated one.
- The reference-object frame transform (RIC) shall use, for the reference object, **the same rule**:
  if the reference object is one of the requesting cell's own owned Assets, its ground-truth orbit
  is used directly (an owning cell's own asset state is never subject to its own custody model — see
  Decision 4); if the reference object is itself something the cell only holds a `Track` on, the
  cell's own `state_estimate` for that reference object (at the same T) is used, never ground truth.

## 6. Non-functional Requirements

- **Determinism (`CLAUDE.md` invariant 1, `ADR-0002`).** The export must be byte-identical across
  repeated calls against the same saved session — trivially satisfied, since it is built entirely
  from `replay()`, which is already the engine's canonical deterministic reconstruction path.
- **Fog-of-war at the boundary (`ADR-0004`).** The export function must read only the requesting
  cell's own `Track` entries, at the Session-Layer boundary, exactly like every other cell-scoped
  read (`CellController`/`session/cells.py`) — never a new, parallel filtering path (per `R105`'s own
  Implementation Guidance against "a parallel 'this cell knows about X' channel").
- **No engine-layer change (`ADR-0023`, one-directional dependency graph).** This design adds no new
  `engine/custody.py` field or method; the Session Layer already has everything it needs via
  `replay()` + the existing `Propagator`.

## 7. Constraints

- `docs/build-spec/` is silent on ephemeris export entirely (it predates this backlog item) — no
  conflict, nothing to flag.
- Replaying to many sampled times across a long `[t1, t2]` span is O(samples × eventlog length) with
  the current `replay()` implementation (full replay from `initial_state` each call, per
  `engine/simulation.py`); this is a real performance constraint on the export's practical time-span
  size, not a correctness one — flagged in Risks, not solved here (an incremental/checkpointed
  replay would be a `07-implementation-planning`-level optimization, not an architecture change).

## 8. Risks

- **Performance risk (see Constraints):** a naive per-sample full replay could be slow for a
  fine-grained sample rate over a long time span. Mitigation left to implementation planning:
  candidate approaches (coarser sampling by default, reusing `Snapshot`s `engine/eventlog.py` already
  supports for faster replay-from-checkpoint) exist but are an `07` decision, not this document's.
- **Confusion risk:** an operator or Feature Spec author could assume "estimated ephemeris" means
  the exported element set itself carries injected numerical error (a "fuzzy" TLE). Decision 4
  settles this is *not* the MVP design — export is an exact propagation of the last real observation
  plus a separately reported uncertainty/confidence field, not a synthetically-degraded element set.
  If a future increment wants the latter, it is new scope, not implied by this document.

## 9. Open Questions

- **Should a future increment inject synthetic estimation error into the propagated element set
  itself** (rather than only reporting `uncertainty_km`/`confidence` alongside an exact propagation),
  to more realistically model an analyst's real degrading-TLE experience? Neither `R105` nor any
  other research input takes a position on this modeling-fidelity tradeoff. Decision 4 below picks
  the simpler MVP (no injected error) as the not-further-blocking default, but flags this as a
  genuine future-work question, not a settled "never."
- **Sampling-rate/performance ceiling for a large `[t1, t2]` span** (Risks) is left to
  `07-implementation-planning` to size against the existing `~24 satellites`/`ADR-0019` sizing
  guideline — this document does not set a numeric ceiling because no source document supplies one.

## 10. Decision Log

1. **`Track.state_estimate` already satisfies "does not reflect an unobserved manoeuvre until
   re-observation."** Verified by direct reading of `orders.py:745`, `ssn.py:386`, and
   `session/scene.py`'s `_geo(t.state_estimate, now)` render path: the snapshot is written only at
   observation time and forward-propagated independently of `Asset.orbit`'s own live truth. `BL-0068`'s
   framing ("track state is a copy of truth") does not hold for the position/state dimension of
   custody as currently implemented — only for the *history* dimension (Decision 2). No engine change
   follows from this half of the backlog item.
2. **No new "estimated element-set history" data structure is introduced.** A query for a cell's
   past belief state at time T < now is answered by replaying the deterministic `EventLog` to the
   eventlog position nearest T (`engine/simulation.py::replay`, the same mechanism
   `session/aar.py::state_at`/`snapshot_at` already use for the AAR scrubber, `FR-7310`) and reading
   that cell's `Track.state_estimate` as reconstructed at that point, then propagating it to exactly
   T. This is the minimal-surgery answer consistent with this project's own established pattern of
   reusing existing precedent rather than inventing a new tier/structure (the same reasoning
   `ADR-0034`/`ADR-0035` applied to directed energy this same increment) — the event log's replay
   guarantee already *is* the history; storing a second, parallel history would duplicate it and
   risk the two diverging.
3. **The cell-observed export (`FR-7420`) is a new Session-Layer function, not an engine change.** It
   drives `replay()` across a requested time span (a generalization of `aar.py`'s single-point
   `state_at`, not a different mechanism), reads only the requesting cell's own `Track` at each
   sampled instant (enforcing `ADR-0004`'s fog-of-war-at-the-boundary the same way every other
   cell-scoped read does), and feeds the result through a serializer shared with `FR-7410`'s truth
   export (parameterized by state source, not duplicated).
4. **MVP export reports uncertainty as metadata, not injected element-set error.** The exported
   state at each sampled time is the *exact* forward-propagation of the last real observation's
   snapshot (no synthetic noise added to the element values themselves); `uncertainty_km`/
   `confidence` at that same time (already computed by `Track.current_uncertainty_km`/
   `current_confidence`) are reported alongside it as separate fields. Rejected alternative:
   injecting deterministic pseudo-random estimation error into the propagated elements themselves —
   not chosen for v1 because no source document specifies a numerical model for how much error to
   inject or how it should scale, and inventing one here would be exactly the kind of
   `02-research-*`-owned domain claim this skill must not originate. Left as Open Question 1 for a
   future increment, not decided against permanently.
5. **A RIC reference object's frame comes from ground truth if it's the requesting cell's own
   Asset, or from that same cell's own `Track.state_estimate` if it's merely tracked.** A cell always
   knows its own asset's true state exactly (custody/fog-of-war has never applied to a cell's
   knowledge of its own assets — only to its knowledge of *other* objects, per `R105` §3's "custody is
   per-cell" framing, which is about objects a cell must earn knowledge of, not its own fleet).
   Applying the cell's own estimate to a reference object it doesn't own keeps the export internally
   consistent (never silently mixing one truth-frame axis with one belief-frame axis in the same RIC
   transform).

## Consequences

- `04-requirements-engineering` may now close `BL-0068`'s remaining requirements-level gap (if any —
  this document resolves the domain-model question in full; a follow-up `04` pass should confirm no
  new numbered FR is needed beyond `FR-7420`, which already exists, or add a small explicit leaf if
  the review judges one warranted) and, more importantly, **`FR-7420`'s block is now lifted** — its
  Acceptance Criteria can be finalized against Decision 2/3's mechanism.
- `06-feature-specification` may now draft the Feature Spec covering `FR-7410`+`FR-7420` (ephemeris
  export), citing this document's System Architecture/Decision Log directly, and should also touch
  FS-103 (Custody Management) to note the confirmed "already independent estimate" finding
  (Decision 1) so a future reader of FS-103 doesn't re-raise it as an open defect.
- No `engine/custody.py` or `engine/simulation.py` code changes are required by this document itself
  — `07-implementation-planning`'s eventual package is purely Session-Layer (a new export function)
  plus a shared serializer with `FR-7410`.
- Backlog `BL-0068` should be flipped from `SCHEDULED` (entry stage 03) to reflect this closure —
  routed to `04`/`06` next, per the pipeline journal.

## Related

[R105](../research/encyclopedia/R105-custody-theory.md); [ADR-0002](adr/ADR-0002-deterministic-core.md);
[ADR-0004](adr/ADR-0004-fog-of-war-at-boundary.md); [ADR-0013](adr/ADR-0013-custody-weapons-quality-gate.md);
`docs/requirements/01-functional-requirements.md` `FR-1510`, `FR-7410`, `FR-7420`;
`docs/reviews/requirements-update-must-tier-batch.md` (Finding 4, the block this document lifts);
`docs/pipeline/backlog.md` `BL-0068`, `BL-0069`.
