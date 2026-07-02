# FS-109 — Multiplayer / LAN Session Transport

> **Document ID:** FS-109
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [DOM-003](../domains/DOM-003-white-cell-framework.md) §6, [ADR-0014](../architecture/adr/ADR-0014-lazy-clock-rlock-multiplayer.md), [ADR-0015](../architecture/adr/ADR-0015-lan-trust-model.md), [ADR-0026](../architecture/adr/ADR-0026-rlock-lan-scaling-ceiling.md)
> **Referenced By:** [FS-106](FS-106-white-cell-dashboard.md) (the White-only clock-control trigger surface this mechanism serves), [docs/feature-planning/03-feature-catalog.md](../feature-planning/03-feature-catalog.md) `FEAT-6300`/`FEAT-6400`
> **Produces:** the consistent-clock, consistent-lock substrate every cell-facing Feature (Blue/Red/Observer/White) reads through
> **Feature Mapping:** FS-109 (this document)
> **Related Topics:** [FS-106](FS-106-white-cell-dashboard.md) (White Cell's clock-authority trigger, upstream of this mechanism's propagation), `CLAUDE.md` "Multiplayer workflow" and "LAN trust model (load-bearing)"

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `feature-specification` skill's 20-field template. It is a **new**
Feature Specification, split out of `FS-106-white-cell-dashboard.md` v1.0 per
`docs/feature-planning/05-feature-review.md` Finding F-03 — the prior v1.0 draft bundled this
mechanism (its own dedicated ADRs: ADR-0014, ADR-0015, ADR-0026) inside the White Cell facilitator
UI document despite serving every connected cell (Blue, Red, Observer, White alike), not only the
facilitator.*

## Feature ID

FS-109

## Title

Multiplayer / LAN Session Transport

## Purpose

Guarantee that a session's simulated clock advances exactly once per real-time interval and that
concurrent mutations from multiple connected clients never corrupt shared session state —
regardless of whether the deployment is single-browser hot-seat or multi-tab/multi-machine LAN
cooperative play — per `docs/feature-planning/03-feature-catalog.md` `FEAT-6300`/`FEAT-6400`'s own
Purpose fields.

## Scope

In scope: the server-authoritative lazy-catch-up clock mechanism (advances state exactly once
regardless of connected client count); per-session mutation locking (serializes concurrent
state-changing requests); serving both single-browser hot-seat play and multi-tab/multi-machine LAN
play from one underlying Session object. Out of scope: *who* is authorized to issue a clock-control
request in the first place (White Cell only — [FS-106](FS-106-white-cell-dashboard.md)'s FR-4310);
the hot-seat hand-off screen-blank behavior between role changes on one browser (a distinct,
currently unspecified Feature — `FEAT-6600` in the Feature Catalog); and session
discovery/join-by-URL-hash as a *facilitator-facing* administrative workflow (that framing remains
[FS-106](FS-106-white-cell-dashboard.md)/DOM-003 §6's, per this document's Open Questions — this
document specifies the underlying mechanism session discovery relies on: one Session object shared
across clients, FR-6410).

**Note on a discrepancy found while researching this spec:** `docs/requirements/03-requirements-
traceability-matrix.md`'s master matrix row for `FR-6510` labels it "Multi-monitor pop-out windows,"
but `docs/requirements/01-functional-requirements.md`'s own numbered baseline defines FR-6510 as
"Observer read-only view with no command ability" (under category FR-6500) — a different
capability entirely. Multi-monitor pop-out windows, a real, shipped `CLAUDE.md`-documented P8
capability (`ui_web/static/app.js`), appears to have **no numbered FR leaf at all** in the current
`01-functional-requirements.md`. This document does not resolve that inconsistency or invent a
citation for pop-out windows — it is recorded here as an Open Question for whoever owns the
requirements baseline and RTM.

## Requirements Implemented

FR-6310 (server-authoritative lazy clock shared across connections), FR-6320 (per-session mutation
locking), FR-6410 (one Session object shared across hot-seat and LAN modes), NFR-1400 (LAN
multiplayer concurrency ceiling is a documented, untested estimate) — per
`docs/feature-planning/03-feature-catalog.md` `FEAT-6300`/`FEAT-6400`'s `Included Requirements`.

## User Workflows

- Two or more browser clients (any mix of White/Blue/Red/Observer seats) connect to the same
  session identifier; each observes an identical simulated clock value for reads issued within the
  same catch-up cycle, with no per-client clock drift.
- Two operators (potentially on different cells) submit orders against the same session
  concurrently; both requests are applied sequentially, in receipt order, with no lost update.
- A facilitator starts a session hot-seat (single browser, sequential role changes) or opens the
  same session URL from multiple LAN machines; the resulting `WorldState` is identical regardless
  of which mode is used, given the same sequence of operator actions.

## System Behaviour

- **The clock advances exactly once per real-time interval regardless of connected client count**
  (FR-6310): a server-authoritative lazy-catch-up mechanism, not a per-client clock. Every read
  request from any connected client triggers a catch-up against the session's wall-clock anchor and
  rate before returning.
- **All state-mutating operations against a session are serialized** (FR-6320): a per-session lock
  ensures no two concurrent mutating requests interleave partially; each is applied to completion
  before the next begins.
- **One Session object serves both hot-seat and LAN-cooperative modes** (FR-6410): the same action
  sequence produces identical `WorldState` in either mode; there is no separate "LAN session" data
  structure or code path.
- **The ~16-participant LAN concurrency ceiling is a documented estimate, not a load-tested
  guarantee** (NFR-1400, ADR-0026): the per-session `RLock` serialization design targets roughly 16
  simultaneous participants; no automated load test enforces or validates this figure in v1.

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `session/manager.py` (`SessionManager`) | Owns the `(_wall_anchor, _sim_anchor, _rate, _clock_running)` lazy-clock fields; `set_clock`/`catch_up`/`clock_state`; re-anchors on start/rewind/undo/advance so the wall clock cannot snap the sim backward. |
| `session/inprocess.py` (`InProcessSession`) | Wraps every mutating call in the `_locked(sid)` context manager (per-session `RLock`); every read pass-through calls `catch_up(sid)` first; owns `list_sessions`/`set_clock`/`clock_state` for session discovery. |
| `ui_web/server.py` | Exposes `/api/sessions/{sid}/clock` and `/api/sessions` over the above, consumed by both the White Cell dashboard (FS-106) trigger surface and every connected client's read polling. |

## Interfaces Used

INT-0001 (Browser ↔ Operator Console, HTTP transport) — every connected client's poll/action loop
runs over this interface and is subject to the catch-up/locking behavior specified here. INT-0006
(Operator Console → Session Layer, the `SessionAPI` seam) — clock-control and mutating requests
route through this seam before reaching the mechanism specified here.

## Data Model Changes

None beyond the existing `Session` object's own lazy-clock fields
(`_wall_anchor`/`_sim_anchor`/`_rate`/`_clock_running`), already part of the Domain Model per
`docs/architecture/04-domain-model.md`'s Session entity. No new entity is introduced by this
Feature.

## State Changes

- Clock-running state transitions (running/paused, rate changes) re-anchor
  `(_wall_anchor, _sim_anchor)` so a subsequent catch-up computes correctly from the new anchor
  point.
- A rewind/undo/branch operation (invoked via FS-106's trigger surface, executed by FS-107's
  mechanism) re-anchors the clock so the wall clock cannot snap the sim backward past the new
  point — the anchor update itself is this Feature's State Change; the rewind/undo/branch logic is
  not.
- The per-session lock's acquisition/release is a transient state per mutating request; it does not
  persist across requests.

## Error Handling

- A concurrent mutating request arriving while the per-session lock is held waits for release
  rather than being rejected or silently dropped (FR-6320) — no error surfaces to the caller solely
  due to lock contention under the documented ~16-participant ceiling (NFR-1400).
- No documented behavior exists in the requirements baseline for what happens beyond the
  ~16-participant ceiling (see Open Questions) — ADR-0026 accepts this as an unaddressed v1 limit,
  not a specified failure mode.

## Performance Considerations

- **NFR-1400** (documented, untested ~16-participant concurrency ceiling) is this Feature's
  central performance constraint — the per-session `RLock` design is optimized for that scale, not
  validated beyond it.
- **NFR-1100** (responsive UI at high time-multipliers) depends partly on this Feature's catch-up
  mechanism not stalling under concurrent load, though NFR-1100 itself is owned by `FEAT-8100`
  (Browser-Based Operator Console Presentation) in the Feature Catalog, not this Feature.

## Security Considerations

- This mechanism is one of the two components (alongside fog-of-war filtering, a different,
  not-yet-specified Feature) that implement the LAN trust model (ADR-0015): session discovery
  (`/api/sessions`) and join-by-hash are deliberately unauthenticated — any participant who can
  reach the LAN and knows or is given a session identifier can join as any cell. This is an
  accepted v1 trust boundary, not a defect of this Feature's design (ADR-0015's own Consequences
  section is the recorded rationale).
- Per-cell token hardening (CNFR-04/CR-02 in the requirements baseline) is a tracked future-work
  item, not part of this Feature's scope.

## Acceptance Criteria

- Two simulated clients polling the same session concurrently observe an identical simulated clock
  value for reads issued within the same catch-up cycle.
- Two concurrent order-submission requests against the same session are applied sequentially with
  no lost update.
- The same sequence of operator actions issued first via a single hot-seat browser and then via
  multiple LAN-connected browsers produces an identical resulting `WorldState`.

## Verification Plan

Test (automated) for all three Acceptance Criteria above, consistent with FR-6310/FR-6320/FR-6410's
own stated Verification Method ("Test") in `docs/requirements/01-functional-requirements.md`.
NFR-1400's own Metric/verification-method field states no automated load test exists or is required
for v1 — Inspection of ADR-0026's Consequences section is the recorded verification for that NFR
specifically.

## Dependencies

`FEAT-1100` (Deterministic, Sub-Stepped Simulation Clock) in the Feature Catalog — this Feature's
lazy-clock mechanism re-anchors around, but does not replace, the core deterministic clock. No
other `FS-xxx` document is a prerequisite.

## Risks

- The ~16-participant concurrency ceiling (NFR-1400/ADR-0026) is untested; a larger cohort session
  is the most likely real-world scenario to expose it.
- Splitting this mechanism out of FS-106 (v1.0) creates a cross-document seam with
  [FS-106](FS-106-white-cell-dashboard.md): a future change to who may trigger a clock-control
  request must be coordinated between both documents.
- `IMP-106A-white-cell-dashboard.md`/`IP-1060` were written against FS-106's prior, broader scope
  and now over-cite relative to both FS-106 v2.0 and this new document — reconciling the
  Implementation Package layer is a follow-on task, not performed here.

## Open Questions

- **Multi-monitor pop-out windows have no numbered FR leaf** in the current
  `docs/requirements/01-functional-requirements.md` baseline, despite the RTM's own FR-6510 row
  citing "Multi-monitor pop-out windows" (a mismatch with that same ID's actual definition in the
  FR document — see Scope). This document does not specify pop-out-window behavior as a result;
  whoever owns the requirements baseline/RTM should resolve which is correct and, if pop-out
  windows genuinely has no FR, add one.
- **Domain ownership:** `docs/domains/DOM-003-white-cell-framework.md` §6 frames "multiplayer
  session discovery" as White-Cell-domain territory (a facilitation concern). This document
  specifies the underlying mechanism as serving all cells equally, not a White-Cell-specific
  concern — both framings are individually defensible (DOM-003 for *why the requirement exists*,
  this document for *what the mechanism does*), but no document reconciles them explicitly. Flagged
  for the domain owner, not resolved here.
- Whether session-discovery's *facilitator-facing panel* (as opposed to the underlying one-Session-
  object mechanism specified here) belongs in this document or remains in FS-106 is unresolved —
  see FS-106's own matching Open Question.

## Related ADRs

ADR-0014 (lazy clock + RLock multiplayer) —
`docs/architecture/adr/ADR-0014-lazy-clock-rlock-multiplayer.md`; ADR-0015 (LAN trust model) —
`docs/architecture/adr/ADR-0015-lan-trust-model.md`; ADR-0026 (RLock LAN scaling ceiling) —
`docs/architecture/adr/ADR-0026-rlock-lan-scaling-ceiling.md`.

## Related Interfaces

INT-0001, INT-0006 — per `docs/design/05-interface-control-document.md` (both are also this
document's Interfaces Used; no additional related-but-unused interface applies).
