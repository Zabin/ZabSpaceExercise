# FS-106 — White Cell Dashboard

> **Document ID:** FS-106
> **Version:** 2.4
> **Status:** ✅ Ready for implementation planning (v2.4: `FR-4320` and the corrected `FR-4310`
> enforcement; v2.3 additions `FR-4450`/`FR-4620`). Everything up to v2.2 is ✅ Done, except that
> `FR-4310`'s enforcement was found not built (see v2.4).
> **Changelog (v2.4, 2026-10-23, pipeline run #218):** Adds `FR-4320` (White Cell lifecycle and
> facilitation controls refused for any other seat, owner decision `BL-0307`) and corrects the
> enforcement point for `FR-4310`: earlier versions placed the role check in `SessionManager`, which
> never sees the caller's seat; it belongs at the server boundary where the Observer refusal
> (`IP-1130`) already sits. Requirements review R1 found `FR-4310` recorded verified (VR-1060) but
> not enforced. Updated Requirements Implemented, System Behaviour, Subsystem Responsibilities,
> Error Handling, Security Considerations, Acceptance Criteria, Verification Plan and Open
> Questions.
> **Changelog (v2.1, 2026-09-26):** Added `FR-4420` (condition-triggered injects, evaluated
> deterministically) and `FR-4430` (four new inject effect types: anomaly, sensor outage, forced
> custody loss, scripted manoeuvre) to `Requirements Implemented`, closing backlog `BL-0070`
> (external validation report, 26 Sep 2026, item B4). Updated User Workflows, System Behaviour,
> Data Model Changes, Error Handling, Acceptance Criteria, Verification Plan, and Open Questions
> accordingly; no other field's substance changed.
> **Changelog (v2.2, 2026-10-15):** Ratified the inject failure-mode behaviour that `IP-1062`
> (Design Decisions 1–3, ✅ `VERIFIED`) and `IP-1063` (Design Decisions 2–3, ✅ `VERIFIED`) had
> settled at package level, closing backlog `BL-0191`: Error Handling now enumerates the inject
> failure modes, and the three v2.1 inject Open Questions are closed by reference to those
> decisions. Acceptance Criteria and Verification Plan gained matching v2.2 entries. Package status
> tags in `Produces` were refreshed (`BL-0193`). No other field's substance changed.
> **Changelog (v2.3, 2026-10-18):** Added `FR-4450` (White Cell edits or cancels a scheduled,
> not-yet-fired inject; `FEAT-4400`) and `FR-4620` (a side-by-side controller view of ground truth
> with both cells' belief; `FEAT-4600`) to `Requirements Implemented`. This closes the spec stage
> of backlog `BL-0079` (external validation report, 26 Sep 2026, item B13). Both leaves were
> already folded into this document's Features by `05-feature-decomposition` (run #83). Updated
> Scope, User Workflows, System Behaviour, Subsystem Responsibilities, Data Model Changes, State
> Changes, Error Handling, Security Considerations, Acceptance Criteria, Verification Plan and
> Risks. No v2.2 field's substance changed.
> **Dependencies:** [DOM-003](../domains/DOM-003-white-cell-framework.md), [DOM-001](../domains/DOM-001-training-framework.md), [R106](../research/encyclopedia/R106-mission-operations.md), [R301](../research/encyclopedia/R301-campaign-design.md), [R307](../research/encyclopedia/R307-wargaming-theory.md), [R308](../research/encyclopedia/R308-red-teaming-methodology.md)
> **Referenced By:** [DOM-001](../domains/DOM-001-training-framework.md), [DOM-003](../domains/DOM-003-white-cell-framework.md), [R106](../research/encyclopedia/R106-mission-operations.md), [R301](../research/encyclopedia/R301-campaign-design.md), [R307](../research/encyclopedia/R307-wargaming-theory.md), [R308](../research/encyclopedia/R308-red-teaming-methodology.md), [IMP-106A](../implementations/IMP-106A-white-cell-dashboard.md) · [IP-1064](../implementation/packages/IP-1064-condition-inject-follow-ups.md) (✅ VERIFIED 2026-10-17, VR-1064 v2.0), [IP-1065](../implementation/packages/IP-1065-console-and-session-small-fixes.md) (✅ VERIFIED 2026-10-17, VR-1065), [IP-1066](../implementation/packages/IP-1066-pending-inject-edit-cancel.md) (✅ VERIFIED 2026-10-18, [VR-1066](../implementation/verification/VR-1066-pending-inject-edit-cancel.md)), [IP-1067](../implementation/packages/IP-1067-side-by-side-controller-view.md) (✅ VERIFIED 2026-10-18, [VR-1067](../implementation/verification/VR-1067-side-by-side-controller-view.md))
> **Produces:** the facilitation surface [FS-108](FS-108-inject-authoring.md) (candidate) would extend; remediation package [IP-1061](../implementation/packages/IP-1061-inject-and-sizing-defect-remediation.md) (`FR-4410` defects, 2026-09-26); [IP-1062](../implementation/packages/IP-1062-condition-triggered-injects-and-new-effects.md) (`FR-4420`/`FR-4430`, ✅ `VERIFIED`, [VR-1062](../implementation/verification/VR-1062-condition-triggered-injects-and-new-effects.md)); remediation package [IP-1063](../implementation/packages/IP-1063-inject-effect-fire-time-validation.md) (`FR-4430`/`FR-4410` inject fire-time validation, `BL-0129`/`BL-0188`, ✅ `VERIFIED`, [VR-1063](../implementation/verification/VR-1063-inject-effect-fire-time-validation.md))
> **Feature Mapping:** FS-106 (this document)
> **Related Topics:** [FS-107](FS-107-after-action-review.md) (White-only AAR controls), [FS-109](FS-109-multiplayer-session-transport.md)
> (the underlying session/clock transport this dashboard's admin panel triggers), [FS-110](FS-110-save-and-resume.md)
> (the underlying save/resume mechanism this dashboard's admin panel triggers), [FS-111](FS-111-ai-red-doctrine-automation.md)
> (the underlying doctrine-preset generation mechanism this dashboard's preset selector controls),
> [DOM-002](../domains/DOM-002-assessment-framework.md) §6 (facilitator-rubric assessment mode, hosted here)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template. **Version 2.0
narrows this document's scope** per `docs/feature-planning/05-feature-review.md` Finding F-03: the
prior v1.0 draft bundled the White Cell facilitator UI together with three architecturally distinct
capabilities (multiplayer/LAN session transport, save/resume, and AI-Red doctrine automation), each
of which now has its own dedicated Feature Specification (FS-109, FS-110, FS-111 respectively).
This version retains the existing Document ID, status, and MSTR-006 §5 metadata per that section's
rules for a re-scoping revision (not a fresh document).*

## Feature ID

FS-106

## Title

White Cell Dashboard

## Purpose

The White Cell Dashboard is the facilitator's console: unrestricted god-view across both cells,
inject authoring/scheduling, clock/pacing control authority, and manual adjudication. Per
[DOM-003](../domains/DOM-003-white-cell-framework.md) §1, it must trace back to White Cell's role
as instructional designer ([MSTR-003](../master/MSTR-003-educational-philosophy.md) §7), not a
neutral referee — every capability in this spec exists to let a facilitator *shape* the learning
experience in real time, not merely observe it.

## Scope

In scope: god-view rendering (both cells' belief + ground truth simultaneously) and view-as-cell;
*(v2.3)* the side-by-side controller view (`FR-4620`) and editing or cancelling a pending inject
(`FR-4450`);
the inject build/schedule panel; clock pause/resume and the rewind/undo/branch **trigger surface**
(the White-only authority to invoke these, not the replay/scrub instrument itself); manual
adjudication (the absence of automated scoring, plus live safe-mode-dial/parameter adjustment
mid-exercise); and the facilitator-facing Red-doctrine-preset **selector/hand-tuning control**
(choosing and adjusting a preset — not the automated activity-generation mechanism the preset
drives).

Out of scope, each now owned by its own Feature Specification: the AAR replay/scrub instrument
itself ([FS-107](FS-107-after-action-review.md)); a richer inject-authoring UX
([FS-108](FS-108-inject-authoring.md), a separate, currently-candidate spec); the
server-authoritative lazy clock, per-session mutation locking, and hot-seat/LAN session-sharing
mechanism this dashboard's clock controls and session-admin panel sit on top of
([FS-109](FS-109-multiplayer-session-transport.md)); the deterministic save/resume mechanism and
content/session ownership split this dashboard's save-file controls invoke
([FS-110](FS-110-save-and-resume.md)); and the doctrine-preset-driven Red activity-generation
mechanism itself, as opposed to the facilitator's control over which preset is selected
([FS-111](FS-111-ai-red-doctrine-automation.md)).

**Also explicitly out of scope, and not covered by any existing Feature Specification:** vignette
selection/parameter tuning and seat-to-role assignment at session setup (FR-4110, FR-4210) —
`docs/feature-planning/03-feature-catalog.md`'s FEAT-4100/FEAT-4200. Reading this document's actual
workflows shows they were never in scope here either, despite superficially reading as "White Cell
setup." This is flagged as a genuine documentation gap for a future Feature Specification, not
silently absorbed into this rewrite.

## Requirements Implemented

FR-4310 (exclusive White Cell clock control), FR-4410 (immediate/scheduled inject application),
FR-4610 (White Cell god-view with per-cell view-as), FR-4710 (no automated scoring), FR-4720
(live adjustment of safe-mode dials/exercise parameters) — per `docs/feature-planning/03-feature-
catalog.md` FEAT-4300/FEAT-4400/FEAT-4600/FEAT-4700's `Included Requirements`. This is the first
version of this document to cite explicit FR IDs; the RTM's own "None identified" traceability gap
for FS-106 (`docs/feature-planning/05-feature-review.md` Finding F-06) is closed for these four FRs
by this revision — a corresponding update to `docs/requirements/03-requirements-traceability-
matrix.md`'s Impl. Package column is a separate, follow-on documentation task, not performed here
(this skill does not edit the requirements baseline).

**Added v2.1:** `FR-4420` (condition-triggered injects, evaluated deterministically on scheduled
engine ticks) and `FR-4430` (four new inject effect types: spacecraft anomaly with a
controller-set true cause, sensor outage for any sensor, forced custody loss/degrade, scripted
manoeuvre) — both children of `FR-4400`, the same parent `FR-4410` sits under, so both are the
same "inject authoring and firing" capability this document already owns, extended rather than a
new capability requiring a new Feature.

**Added v2.3:**

- `FR-4450` (edit or cancel a scheduled, not-yet-fired inject) is under `FR-4400`, in `FEAT-4400`.
- `FR-4620` (side-by-side controller view: ground truth beside each cell's belief) is under
  `FR-4600`, in `FEAT-4600`.

Both are Could-tier leaves the Feature Catalog already assigns to this document's Features
(run #83). `FEAT-4400`'s `FR-4440` is specified by FS-123, not here.

**Added v2.4:** `FR-4320` (refuse White Cell lifecycle and facilitation controls from any other
seat), in `FEAT-4300` beside `FR-4310` (run #212 sweep).

## User Workflows

- The White Cell facilitator opens the god-view, observing both cells' belief states and ground
  truth simultaneously without granting either cell additional ground-truth access.
- The facilitator selects an inject template from the existing `inject_library.yaml` five-template
  set, edits its parameters as JSON, and schedules it for Now / +seconds / absolute-UTC delivery.
- The facilitator pauses or resumes the exercise clock, or triggers rewind/undo/branch — the
  underlying mechanics of these are [FS-109](FS-109-multiplayer-session-transport.md) (clock) and
  [FS-107](FS-107-after-action-review.md) (rewind/undo/branch replay); this dashboard is the
  White-only trigger surface for both.
- The facilitator views which Red-doctrine preset is active and switches or hand-tunes it
  mid-exercise for pacing reasons; the preset's actual activity-generation behavior is
  [FS-111](FS-111-ai-red-doctrine-automation.md).
- The facilitator observes mission-set/campaign sequencing (which vignette in a sequence is
  active) — grounded in [R301](../research/encyclopedia/R301-campaign-design.md) §5, not itself
  traced to a numbered FR (see Open Questions).
- The facilitator observes the assess beat across both cells simultaneously
  ([R106](../research/encyclopedia/R106-mission-operations.md) §5) — a perspective
  [FS-105](FS-105-spacecraft-operations.md)'s per-cell console does not provide, and likewise not
  itself traced to a numbered FR (see Open Questions).
- *(Added v2.1)* The facilitator authors a condition-triggered inject — a range threshold between
  two named assets, a named cell's custody-confidence threshold on a track, or an objective
  reaching a declared state — instead of an immediate/time-scheduled trigger, using the same
  authoring surface `FR-4410` already provides (`FR-4420`).
- *(Added v2.1)* The facilitator selects one of the four new inject effect types (spacecraft
  anomaly with a controller-set true cause, sensor outage on any named sensor, forced custody
  loss/degrade against a named cell's track, or a scripted manoeuvre of any named asset) and
  configures its type-appropriate payload, using the same panel `FR-4410`'s existing effects
  already populate (`FR-4430`).

- *(Added v2.3)* The facilitator opens the **pending-inject queue**. It lists every inject that
  has not yet fired, each with its trigger kind, its fire time (for a time-scheduled inject), and
  its effects. The queue covers:
  - the vignette's time-triggered injects still in the future;
  - its condition-triggered injects not yet fired;
  - injects White Cell itself scheduled for a future time.

  The facilitator either **cancels** one, after which it never fires, or **edits** it, replacing
  its effect list and, for a time-scheduled inject, its fire time (`FR-4450`).
- *(Added v2.3)* The facilitator opens the **side-by-side controller view**. It shows ground truth,
  Blue's picture and Red's picture together, so each cell's belief can be compared with truth and
  with the other cell's at a glance (`FR-4620`).

## System Behaviour

- **Must expose unrestricted god-view without granting Red/Blue any new ground-truth access.** Per
  [DOM-003](../domains/DOM-003-white-cell-framework.md) §3, any new god-view-only capability is
  acceptable; any capability that would let Red/Blue access ground truth through this dashboard is
  a fog-of-war violation regardless of framing.
- **Inject authoring must work against the existing `inject_library.yaml` mechanism, not duplicate
  it.** Per [DOM-003](../domains/DOM-003-white-cell-framework.md) §4, the dashboard exposes the
  five reusable templates with editable-JSON + Now/+seconds/absolute-UTC scheduler (FR-4410); the
  inject *execution* path is engine-side and out of scope to re-implement.
- **Clock/pacing control authority (FR-4310) must remain exclusively White Cell's**, applying
  identically to every connected client — no per-tab pacing negotiation (ADR-0016). The mechanism
  that propagates a pause/resume/rate-change to every connected client is
  [FS-109](FS-109-multiplayer-session-transport.md)'s responsibility, not this Feature's.
- *(v2.4)* **Only a request that names the White Cell seat may use a White Cell control**
  (`FR-4310`, `FR-4320`). The controls are: clock control (start of the clock is the session start,
  pause/resume/rate, step, advance, rewind, undo — `FR-4310`); and session start, setting an
  exercise parameter, firing an inject, editing the force (TLE add, bulk import, ground-asset add),
  assigning seats to roles, designating the Observer's view, and loading a save into a new session
  (`FR-4320`). A request naming `blue`, `red` or `observer` is refused with a reason before it
  reaches the session, and the session is unchanged; the same request naming `white` proceeds
  exactly as today.
  - **A request that names no seat is refused too.** `FR-4310`'s Postcondition is that no
    request not issued by White Cell changes the clock; a request with no seat is not issued by
    White Cell. This matches how the server already enforces its existing White-only actions
    (GDS-09 §4: seat declaration, inject cancel and edit, the controller view, live ROE change —
    each refuses any caller not naming `white`), so every White-only action follows one rule. The browser client always
    names its seat on a mutating request (it defaults to `white`), so no operator flow changes.
  - Seat assignment and Observer designation already refuse a non-White caller inside the session
    layer (`IP-1151`, `IP-1130`); they keep that check and gain nothing new except a test.
- **God-view/view-as (FR-4610) must never grant write access to the viewed cell's state.** A
  view-as-Red request returns exactly the data INT-0004 would return to a Red-seated operator, no
  more.
- **No automated scoring exists anywhere in the outbound interface set (FR-4710).** Live parameter
  adjustment (FR-4720, e.g. safe-mode dials) takes effect on the next evaluation with no session
  restart.
- **Red-doctrine-preset visibility and control is a facilitator-tooling requirement** (DOM-003 §7):
  the facilitator needs visibility into which preset drives Red and the ability to switch or
  hand-tune it mid-exercise — an unconvincing or passive Red undermines training per
  [R308](../research/encyclopedia/R308-red-teaming-methodology.md). The preset's own behavior once
  selected is [FS-111](FS-111-ai-red-doctrine-automation.md)'s System Behaviour, not this
  document's.
- *(Added v2.1)* **A condition-triggered inject's condition is evaluated only on scheduled engine
  ticks against the deterministic `WorldState`, never against wall-clock time.** Per `FR-4420`'s
  own Rationale, evaluating it anywhere else would reintroduce nondeterminism into a system whose
  `(initial_state, ordered eventlog, seed) → byte-identical state` invariant is load-bearing
  (`ADR-0002`, `ADR-0006`) — the same replay guarantee `FS-107`'s AAR scrubber and `ADS-1500`'s
  custody-export design (this same increment) both depend on.
- *(Added v2.1)* **A forced custody-loss effect changes only the targeted cell's own `Track`/
  `TrackCatalog` entry, never another cell's** (`FR-4430`'s own Postcondition) — the same
  fog-of-war-at-the-boundary invariant (`ADR-0004`) every other cell-scoped mutation in this
  system already respects; this Feature does not introduce a parallel enforcement path.
- *(Added v2.1)* **An anomaly inject's controller-set true cause is recorded in the event log
  exactly as the facilitator set it, never re-derived** — the panel is presenting a White-Cell
  narrative decision, not computing a diagnosis.
- *(Added v2.3)* **Pending-inject queue (`FR-4450`).**
  - **Identity.** Every pending inject has a stable handle: a vignette inject keeps its own id,
    and an inject White Cell scheduled through the console gets an id when it is scheduled. The
    queue is read-only: listing it changes nothing.
  - **Cancel.** A cancel removes the inject from the queue, and the inject subsequently never
    fires. A cancelled condition-triggered inject is never evaluated again.
  - **Edit.** An edit replaces the inject's effect list and, for a time-scheduled inject, its fire
    time. The inject later fires carrying the edited values, never the original ones (`FR-4450`
    Postcondition). An edited fire time earlier than now is clamped to now, the same rule a newly
    scheduled White inject follows.
  - **Validation.** An edited effect list passes the same whole-inject check a newly fired inject
    does (v2.2 Error Handling): it is accepted whole or refused whole.
  - **Determinism.** A cancel or edit is a White Cell action recorded in the event log at the
    simulated instant it is made (`ADR-0002`). Replay therefore reproduces it, and a rewind to an
    earlier instant discards it with the rest of the later history. After such a rewind the inject
    is pending again with its original parameters.
  - **Already fired.** An inject that has already fired can no longer be edited or cancelled.
- *(Added v2.3)* **Side-by-side controller view (`FR-4620`).**
  - **Content.** White Cell sees ground truth plus Blue's and Red's own views together. Each
    cell's panel is exactly what `FR-4610`'s view-as returns for that cell, with no additional
    ground truth and no filtering of its own. The fog-of-war filter remains the single
    `SessionAPI`/`CellController` path (`ADR-0004`).
  - **One instant.** All three panels describe **one and the same simulated instant**, so a
    difference between panels is a difference in belief, never a clock skew between reads.
  - **Read-only.** The view grants White Cell no write access to either cell's state through this
    display path (`FR-4620` Postcondition).
- **Authority-tier statement** (DOM-003 §8): this spec now touches three of DOM-003's four
  authority tiers — visibility (god-view), inject, and clock-trigger — plus manual adjudication.
  Session administration (§6 of DOM-003) is no longer this document's own System Behaviour; it is
  [FS-109](FS-109-multiplayer-session-transport.md)/[FS-110](FS-110-save-and-resume.md)'s (see Open
  Questions for the resulting DOM-003 framing tension).

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `session/manager.py` (`SessionManager`) | Applies clock-control requests (pause/resume/rewind/undo/branch trigger); delegates the multi-client clock propagation to FS-109. *(v2.4: it does not see the caller's seat, so it is not where `FR-4310` is enforced — see the next row.)* |
| `ui_web/server.py` (the HTTP boundary) | *(v2.4)* Refuses every White Cell control listed under System Behaviour unless the request names the `white` seat (`FR-4310`, `FR-4320`), at the point where the Observer refusal (`IP-1130`) already sits, before the request reaches `SessionAPI`. |
| `session/manager.py` (`InProcessSession.inject_library()`) | Loads/exposes the five reusable inject templates and applies scheduled/immediate injects (FR-4410). |
| `session/api.py` (`SessionAPI`) | Serves god-view and view-as-cell requests (FR-4610), reusing the fog-of-war filter FS-106 does not itself implement (that filter's own Feature is `FEAT-6200` in the Feature Catalog, specified by a different, not-yet-authored FS). |
| `session/redai.py` | Exposes the currently-selected doctrine preset for display and accepts a facilitator's preset-switch/hand-tune request (DOM-003 §7); the preset's own generation behavior is FS-111's subsystem responsibility, not this row's. |
| `ui_web/server.py` / `ui_web/static/` | Renders the dashboard panels (god-view, inject panel, clock controls, adjudication/parameter controls) over the above. *(v2.3)* Also renders the pending-inject queue with its edit and cancel controls, and the side-by-side controller view. |
| `session/manager.py` (`SessionManager`) *(v2.3)* | Owns the pending-inject queue: listing it, cancelling and editing an entry with the White-only and already-fired checks, recording each cancel or edit in the event log, and reusing the v2.2 whole-inject check for edited effects (`FR-4450`). |
| `session/api.py` / `session/inprocess.py` *(v2.3)* | Serves the side-by-side controller view as ground truth plus both cells' `CellView`s for one simulated instant, reusing `get_godview`/`get_view` unchanged (`FR-4620`). |

## Interfaces Used

INT-0002 (White Cell Facilitator ↔ Operator Console, exercise control) — per
`docs/design/05-interface-control-document.md`. INT-0003 (in-app scenario builder) is **removed**
from this revision's Interfaces Used: on inspection, this document's actual Scope (god-view,
injects, clock, adjudication) does not touch the in-app vignette builder that INT-0003 describes;
that interface belongs to `FEAT-5100` (In-App Iterative Vignette Builder), a different, currently
unspecified Feature. Carrying it here was inherited from the prior v1.0 draft without a workflow
that used it — corrected here rather than propagated.

## Data Model Changes

Not addressed in any prior version of this document — no existing content to carry forward. The
dashboard consumes existing session state without a Domain Model change. Flagged as an Open
Question below, unchanged from v1.0.

*(Added v2.1)* `FR-4420`/`FR-4430` likewise require no new Domain Model entity: a
condition-triggered inject is a new *trigger shape* on the existing `Inject` concept (alongside
immediate/scheduled), and the four new effect types are new entries in the existing inject-effect
vocabulary, both extending structures the domain model already has (`GDS-04` §1.12 Inject),
consistent with `ADR-0007` (content as data).

*(Added v2.3)* `FR-4450` adds no new Domain Model entity. A pending inject is the existing
`Inject` concept (`GDS-04` §1.12) in its scheduled state. Its handle, and the record of a
cancellation or edit, are session/event-log state, not a new entity. `FR-4620` reads existing
state only.

## State Changes

- Inject scheduling commits an inject to the session's inject queue; the inject executes at the
  scheduled sim time via `WorldState` direct mutation (INT-0016, per the ICD).
- *(Added v2.3)* A cancel moves a pending inject to *cancelled*, and it never fires. An edit
  replaces a pending inject's effects and fire time and leaves it pending. Both happen only before
  the inject fires, and both are recorded in the event log (`FR-4450`).
- Red doctrine preset changes take effect immediately for AI-Red (ADR-0021) — the effect itself is
  FS-111's State Changes, not this document's.
- Clock-control and save/resume state transitions themselves are FS-109's and FS-110's State
  Changes respectively; this document only originates the White-Cell-authorized *request* for them.

## Error Handling

- Clock-control requests from a non-White-Cell role are rejected with the clock state unchanged
  (FR-4310) — the propagation mechanism that keeps all clients consistent is FS-109's concern.
- *(v2.4)* A White Cell control requested by any seat other than `white`, or by no seat, is refused
  with a "forbidden" outcome and a reason naming the control and that only White Cell may use it;
  nothing in the session changes (`FR-4320`). An unknown session is still reported as unknown
  first, as today.
- *(v2.2 — ratified from `IP-1063` Design Decision 2, grounded in `FR-4430`'s Precondition
  "the targeted Asset/Sensor/Track exists in the current `WorldState`" and `FR-4410`)*
  **White-Cell-originated inject, fired now or scheduled: checked whole, rejected atomically.**
  Every effect in the inject is checked before anything is scheduled, logged or applied.
  - The structural check covers all twelve effect types: a known type, its required fields, and
    well-formed values.
  - The `FR-4430` target-precondition check covers the four `FR-4430` types, against the world at
    fire/schedule time. An `anomaly` target must be an asset that has a bus; a `sensor_outage`
    target must be a sensor; a `forced_custody_loss` needs the named cell to hold a track on the
    target; a `scripted_manoeuvre` target must have an orbit, and its parameters must be accepted
    by the manoeuvre computation.
  - If any effect fails, the whole inject is refused. **None** of its effects apply, no clock moves,
    and White Cell sees a rejection naming each failing effect by position, type and reason.
  - The eight pre-`FR-4430` types keep their earlier missing-target posture; they are checked
    structurally only.
- *(v2.2 — ratified from `IP-1063` Design Decision 3)* **Inject that reaches the deterministic
  handler without passing the White-Cell check** (vignette-scheduled, condition-triggered, or
  scheduled earlier and fired later). An effect that fails the structural check is skipped whole,
  and White Cell alone receives one message naming the effect type and the reason. The remaining
  effects still apply, and the run never halts on a bad effect. The skip decision is a pure
  function of the world and the effect, so live and replay match exactly (`NFR-1500`).
- *(v2.2 — ratified from `IP-1062` Design Decision 2, retained by `IP-1063` Design Decision 3)* **A
  well-formed effect whose target is missing or unsuitable when it fires in the handler** is a
  silent no-op. It has no state change and no message.
- *(v2.2 — ratified from `IP-1062` Design Decision 2)* **A condition-triggered inject whose
  condition names a deleted/expired asset, track or cell** evaluates false and never fires. It is
  not an error at authoring or at run time.
- *(v2.2 — ratified from `IP-1062` Design Decision 3, under `ADR-0005`)* **A scripted-manoeuvre
  inject against an asset with insufficient Δv** is applied anyway. It neither checks nor deducts
  `AssetResources.delta_v_ms`, because injects are the documented bypass of plan-first commanding.

- *(Added v2.3)* **Edit or cancel requests (`FR-4450`):**
  - A request naming no pending inject, or one that has already fired, is refused with the reason
    and changes nothing.
  - A request from any seat other than White Cell, including the Observer seat (`FR-6510`/
    `IP-1130`), is refused and changes nothing.
  - An edit whose new effect list fails the whole-inject check is refused whole (as v2.2). The
    inject stays pending with its previous parameters.
- *(Added v2.3)* **Side-by-side view requests (`FR-4620`):** a request from a non-White seat is
  refused. The view is a ground-truth display at the same no-cell trust level as the god-view.

## Performance Considerations

- **Single point of time control.** All clock-control *requests* originate only from this
  dashboard for the White Cell role (ADR-0016); the requirement that they apply identically and
  simultaneously across all connected clients is FS-109's Performance Consideration, not
  duplicated here.
- **Human factors.** Per [DOM-003](../domains/DOM-003-white-cell-framework.md) §3, the god-view's
  role is instructional — the facilitator is shaping learning, not merely observing — and the
  dashboard's design must reflect this purpose.

## Security Considerations

- The dashboard must not expose any capability that grants Red/Blue ground-truth access — this is
  the single most critical invariant for this feature (DOM-003 §3).
- The LAN trust model (ADR-0015) applies: the dashboard's god-view is one of the no-cell
  ground-truth endpoints. The trust model's multi-client/session-sharing implications are FS-109's
  Security Considerations, not restated here.

- *(Added v2.3)* The side-by-side controller view and the inject edit/cancel controls are
  White-only, at the same client-side-trust level as every other White surface (`CLAUDE.md` LAN
  trust model). Neither exposes ground truth to a Red or Blue seat.
- *(v2.4)* The White-only refusal (`FR-4310`, `FR-4320`) is a structural check at the same trust
  level as the Observer refusal: the seat is asserted by the client, so a participant who lies about
  their seat still passes it (ADR-0015). It closes accidental use from a Blue or Red seat in
  hot-seat and LAN play; it is not authentication, and nothing here claims it is.

## Acceptance Criteria

- God-view renders both cells' belief states and ground truth simultaneously without modifying
  either cell's fog-of-war-filtered view.
- Inject authoring works against the existing `inject_library.yaml` five-template set with
  editable-JSON + Now/+seconds/absolute-UTC scheduling; no duplicate inject-execution path exists.
- Clock pause/resume/rewind/undo/branch **trigger** requests are accepted only from the White Cell
  role; a Blue- or Red-role request is rejected with no clock-state change.
- *(v2.4)* For each control listed under System Behaviour — clock rate/pause, step, advance,
  rewind, undo, session start, parameter set, inject fire, TLE add, bulk import, ground-asset add,
  seat assignment, Observer designation, save load — a request naming `blue`, `red` or
  `observer`, and one naming no seat, is refused and leaves the session unchanged (sim time,
  started flag, parameters, assets, event-log length, seat assignments, session count); the same
  request naming `white` succeeds.
- No outbound interface returns a computed score/win-loss field; a live safe-mode-dial adjustment
  takes effect on the next evaluation with no session restart.
- Red doctrine preset is viewable and switchable/hand-tunable mid-exercise from this dashboard.
- Mission-set/campaign sequence visibility and the cross-cell assess beat are visible from this
  dashboard (research-grounded, not FR-traced — see Open Questions).
- *(Added v2.1)* A condition-triggered inject fires at the identical simulated tick on both an
  original run and a replay of the same `(initial_state, ordered eventlog, seed)`.
- *(Added v2.1)* Each of the four new inject effect types (anomaly, sensor outage, forced custody
  loss, scripted manoeuvre), once fired, produces the expected change on its targeted
  Asset/Sensor/Track/`BusState`, and a forced custody-loss effect never changes a non-targeted
  cell's own `Track`.
- *(Added v2.2)* A White-Cell inject containing at least one effect that fails the structural or
  `FR-4430` target-precondition check is refused as a whole. No effect in it is applied, including
  valid effects listed before the bad one. The refusal names each failing effect.
- *(Added v2.2)* An inject that reaches the handler with a structurally invalid effect never halts
  the run. That effect is skipped with exactly one White-only message, the other effects apply,
  and a replay of the session reproduces the live world byte-identically.
- *(Added v2.2)* Every shipped vignette inject and every inject-library template passes the check.

- *(Added v2.3)* **Cancel (`FR-4450`).** A pending time-scheduled inject cancelled before its
  fire time is gone from the pending queue, and after the clock passes its fire time it has not
  fired: no effect applied and no inject record. The same holds for a pending condition-triggered
  inject whose condition later becomes true.
- *(Added v2.3)* **Edit (`FR-4450`).** A pending inject edited to change one effect parameter (for
  example a message's text) fires carrying the edited value, not the original one. An edited fire
  time is the time it fires at.
- *(Added v2.3)* **Refusals (`FR-4450`).** Editing or cancelling an already-fired inject, an
  unknown handle, or a request from a non-White seat is refused with nothing changed. An edit with
  an invalid effect is refused whole.
- *(Added v2.3)* **Replay and rewind (`FR-4450`).** A session containing a cancel and an edit
  replays byte-identically. A rewind to before the cancel leaves the inject pending again.
- *(Added v2.3)* **Side-by-side view (`FR-4620`).** The view returns ground truth plus Blue's and
  Red's views for a single simulated instant. Each cell's panel equals that cell's `FR-4610`
  view-as result at that instant, and the truth panel equals the god-view at that instant.

## Verification Plan

Test (automated) for clock-authority role rejection (FR-4310) — *(v2.4)* and for every `FR-4320`
control, one test per control and refused seat, each asserting both the refusal and the unchanged
session state, tagged `@pytest.mark.verifies("FR-4310")` or `("FR-4320")` (a package claim
without such a test is how R1 happened) — and the no-automated-scoring
inspection sweep (FR-4710); Demonstration for inject-scheduling UX, doctrine-preset switching, and
live parameter adjustment (FR-4720), consistent with those requirements' own stated Verification
Methods in `docs/requirements/01-functional-requirements.md`.

*(Added v2.1)* Test (automated) for `FR-4420` (a condition-triggered inject fires at the same
simulated tick under replay) and `FR-4430` (each new effect type's targeted-state assertion,
including the negative assertion that a forced custody-loss effect never touches a non-targeted
cell's own `Track`) — consistent with both requirements' own stated Verification Method (Test).

*(Added v2.2)* Test (automated) for the ratified inject failure modes: atomic rejection at the
White-Cell boundary (direct call and over HTTP), skip-never-halt with a White-only message in the
handler, replay parity on the skip path, and shipped-content cleanliness. These are already
exercised by `IP-1063`'s tests and were independently re-derived in `VR-1063`.

*(Added v2.3)* Test (automated) for `FR-4450` (cancel, edit, refusal, replay and rewind, each
directly and over HTTP) and for `FR-4620` (the single-instant three-view read, compared field by
field with the god-view and each cell's view-as). This is consistent with both requirements'
stated Verification Method (Test). The browser rendering of both panels is Demonstration, like the
rest of this dashboard's UI.

## Dependencies

[FS-109](FS-109-multiplayer-session-transport.md) (clock-control requests this dashboard issues are
propagated by FS-109's mechanism), [FS-110](FS-110-save-and-resume.md) (session-admin save/resume
requests this dashboard's panel would trigger — see Open Questions on whether that panel remains
part of this document or FS-110's own UI surface), [FS-111](FS-111-ai-red-doctrine-automation.md)
(the preset this dashboard lets a facilitator select/tune). [DOM-003](../domains/DOM-003-white-cell-framework.md),
[DOM-001](../domains/DOM-001-training-framework.md), [R106](../research/encyclopedia/R106-mission-operations.md),
[R301](../research/encyclopedia/R301-campaign-design.md), [R307](../research/encyclopedia/R307-wargaming-theory.md),
[R308](../research/encyclopedia/R308-red-teaming-methodology.md) (unchanged from v1.0).
[FS-107](FS-107-after-action-review.md) (the AAR instrument this dashboard's controls invoke) and
[FS-108](FS-108-inject-authoring.md) (candidate) remain downstream/adjacent, not upstream
dependencies.

## Risks

- **This split (v2.0) introduces a cross-document seam that did not exist in v1.0.** A future
  change to clock-control authority (e.g. a new role gaining partial pacing control) now requires
  coordinated updates to this document *and* FS-109; the two must be kept in sync explicitly, not
  assumed consistent.
- Composing multiple inject templates into a pre-scripted sequence ahead of a session is named in
  DOM-003 §9 as not currently possible — treating it as in scope would be a silent scope addition
  requiring FS-108 or a new ID (unchanged from v1.0).
- Granting any capability to Red/Blue through this dashboard that provides indirect ground-truth
  access would compromise the fog-of-war boundary regardless of framing (unchanged from v1.0).
- **`IMP-106A-white-cell-dashboard.md` (and its successor `IP-1060`) were written against this
  document's prior, broader v1.0 scope.** Both now over-cite this document relative to its narrowed
  v2.0 scope (they also cover material now specified by FS-109/FS-110/FS-111). Reconciling the
  Implementation Package layer against this split is a follow-on task, out of scope for this
  Feature Specification revision.

- *(Added v2.3)* **Rewind interplay (`FR-4450`).** A facilitator may expect a cancel to survive a
  rewind. This spec deliberately follows the event-log semantics (`ADR-0002`): a rewind discards a
  later cancel or edit, exactly as it discards every other later action. The operator-facing manual
  must say so.
- *(Added v2.3)* **Scope of an edit.** `FR-4450` says "parameters". This revision reads that as the
  effect list plus, for a time-scheduled inject, the fire time. Changing a condition-triggered
  inject's *condition* is not covered: it is neither requested by `BL-0079` nor needed by
  `FR-4450`'s acceptance criterion. A request for it would come through `00-intake`.

## Open Questions

- *(v2.4)* **Other White surfaces not in `FR-4320`'s list.** The Vignette Creator's draft-session
  edits, the AI-Red step trigger, save (`GET`), save-as-vignette and save-as-scenario are White
  surfaces in the client but not named by `FR-4320`, so v2.4 does not require their refusal. Matters
  because a Blue seat could still trigger them by accident. **Resolution path:** `04` decides at
  its next pass whether to widen `FR-4320`; until then, leaving them as they are is consistent with
  the baseline.

- **DOM-003 §6 framing tension (new in v2.0):** DOM-003 explicitly claims "session administration
  (save/resume, multiplayer session discovery)" as White-Cell-domain territory, reasoned as a
  facilitation concern rather than an infrastructure one. This Feature Specification split
  (FS-109/FS-110 now specifying the underlying mechanisms) does not contradict that domain framing
  — DOM-003 can and does still ground multiple Feature Specifications — but it does mean DOM-003's
  own §6 text and Feature Mapping frontmatter should be read as covering FS-109/FS-110 as siblings
  of FS-106, not as implying those mechanisms belong inside this single document. DOM-003's
  frontmatter has been updated accordingly (see that document).
- Whether the save/resume and session-discovery *panel UI* (as opposed to the underlying
  mechanism, now FS-109/FS-110) belongs in this document or should move entirely to FS-109/FS-110 is
  unresolved — this revision keeps the panel-triggering workflow bullets here provisionally under
  "session administration" framing per DOM-003 §6, pending a UI-ownership decision.
- Mission-set/campaign-sequence visibility and the cross-cell assess-beat view are grounded in
  R301/R106 but trace to no numbered FR in `docs/requirements/01-functional-requirements.md` —
  unchanged from v1.0, not resolved by this revision.
- The source document does not assign a formal per-subsystem Subsystem Responsibilities table
  beyond what this revision now states; whether further decomposition is warranted is open.
- The source document does not address Data Model Changes; whether the dashboard requires any new
  Domain Model entities is unresolved (unchanged from v1.0).
- `IMP-106A`/`IP-1060` reconciliation against this narrowed scope (see Risks) is an open follow-on
  task.
- *(Added v2.1, carried from the Requirements Review, `BL-0091`)* **Scripted-manoeuvre inject
  entry-mode ambiguity.** `FR-4430` does not state whether a scripted-manoeuvre inject must resolve
  through `engine/maneuver.py`'s existing six entry modes (eci/lvlh/finite_burn/target_coe/
  hohmann/plane_change) or may set a resulting state directly — a design-level choice this Feature
  Specification cannot make on its own authority; it needs either an explicit `04-requirements-
  engineering` amendment naming the mode, or a deliberate `07-implementation-planning` decision
  citing this document. Whichever it names, the Postcondition/Acceptance-Criteria text above should
  be updated to state it explicitly once resolved. **Closed v2.2:** resolved by `IP-1062` Design
  Decision 1 (always through the six entry modes via the existing manoeuvre computation, never a
  direct state set; ✅ `VERIFIED`, `VR-1062`). Ratified in Error Handling above.
- *(Added v2.1)* **Condition-triggered inject targeting a deleted/expired asset, track, or cell**
  — `FR-4420` does not state whether such a condition simply never fires (evaluates false forever),
  is treated as an error at authoring time, or something else. **Closed v2.2:** the condition
  evaluates false and never fires (`IP-1062` Design Decision 2, retained by `IP-1063`). Ratified in
  Error Handling above.
- *(Added v2.1)* **Scripted-manoeuvre inject against an asset with insufficient Δv** — `FR-4430`
  does not state whether the manoeuvre is clamped, rejected, or applied anyway (bypassing the
  normal `AssetResources.delta_v_ms` gate `FR-1310` enforces for operator-issued manoeuvre orders).
  Given injects are the documented, accepted bypass of plan-first commanding (`ADR-0005`), a
  facilitator-authored manoeuvre plausibly *should* bypass this gate too — but that is an inference,
  not a stated decision, and is flagged here rather than assumed. **Closed v2.2:** bypassed, neither
  checked nor deducted (`IP-1062` Design Decision 3, under `ADR-0005`). Ratified in Error Handling
  above. Facilitator-facing consequence: a scripted manoeuvre is outside the normal Δv budget.

- *(Added v2.3)* None open for `FR-4450`/`FR-4620`; the two scoping reads are stated under Risks.

## Related ADRs

ADR-0016 (single point of time control) —
`docs/architecture/adr/ADR-0016-single-point-of-time-control.md`. ADR-0027 (scenario-authoring
boundary) is **removed** from this revision's Related ADRs — it grounded the now-removed INT-0003
citation (see Interfaces Used) and does not bear on this document's narrowed scope. **Added v2.1:**
ADR-0002 (deterministic core) and ADR-0006 (sub-stepped clock) — `FR-4420`'s condition-trigger
determinism requirement; ADR-0004 (fog-of-war at the boundary) — `FR-4430`'s forced-custody-loss
per-cell scoping; ADR-0005 (plan-first commanding) — both new leaves exercise the same documented
inject bypass this document's existing FR-4410 scope already relies on. **v2.3:** ADR-0002
(`FR-4450` cancels and edits are event-log actions) and ADR-0004 (`FR-4620` reuses the single
fog-of-war filter path) bear on the new leaves; no new ADR is needed.

## Related Interfaces

INT-0002 (White Cell Facilitator ↔ Operator Console, exercise control) — per
`docs/design/05-interface-control-document.md`. INT-0003 is related context (consumed by a
different, unspecified Feature — FEAT-5100 in the Feature Catalog) but is not directly used by this
document — see Interfaces Used.
