# ADR-0038 — Event application is failure-atomic: a handler that raises leaves no trace in live state

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0038
- **Title:** When an event handler raises during a live advance, the engine restores the pre-event
  state, logs a no-op failure record in the event's place, and keeps advancing
- **Status:** Accepted

## Context

`CLAUDE.md` invariant 1 (ADR-0002): `(initial_state, ordered eventlog, seed) → byte-identical
state`. Live state must therefore always equal what replaying the event log produces.

As built (`engine/simulation.py::Simulation.advance_to`, verified at `e1e721c`), each due event is
popped, its handler is applied to the live `WorldState` with the live RNG, and only then is the
event appended to the event log. If the handler raises:

1. the event is already popped from the scheduler, never appended, and lost;
2. any mutation the handler made to `WorldState` before raising stays in live state, and any RNG
   draw it made has advanced the live RNG — but neither is reproduced by a replay, because the
   event is not in the log;
3. the triggering `advance_to` call raises, and the next one proceeds as though nothing happened.

Point 2 is a live/replay divergence against invariant 1. A rewind, undo, save/resume or AAR
replay then reconstructs a different world from the one the operators saw. This was reproduced
for `IP-1052` with a wrong-length manoeuvre `dv` (no mutation before the raise in that case, so the
divergence was latent rather than visible). `IP-1052` and `IP-1310` closed two content routes into
the gap; the general ordering was routed here (`BL-0227`).

`NFR-1600` also applies: "the running engine shall never crash on a legal operator action".

## Decision

Event application in a live advance is **failure-atomic**:

1. If a handler raises, the engine **restores live `WorldState` and RNG to exactly the state the
   event log reproduces** before that event. The mechanism is the existing deterministic rebuild
   (initial state + seed + logged entries), run only on this failure path. Pending scheduled events
   other than the failed one are **kept**; a failure is not a rewind.
2. In the failed event's place, the engine **appends a failure record** to the event log: a
   distinct event kind whose handler is a no-op, carrying the original event's kind, actor, sim
   time, payload and the exception's class and message. Replaying the record changes nothing, so
   live state and replayed state agree, and the AAR and event log show that something failed and
   what.
3. The advance **continues** to its target, firing later due events normally. The failed event is
   not retried.

Handlers keep their existing obligation to validate before mutating and to record domain failures
as ordinary outcomes (for example `_h_effect`'s failed-effect records). This decision is the safety
net for a handler that does not, not a replacement for it.

## Alternatives Considered

- **Append before apply** — rejected. A raising event in the log makes every later replay raise at
  the same point, so rewind, resume and AAR break permanently for the session.
- **Copy the world and RNG state before every event** — rejected. It costs a full deep copy on the
  hot path of every event at every time multiplier, to protect a path that should be rare. The
  rebuild-on-failure route costs nothing until a failure occurs.
- **Keep raising and let the session layer decide** — rejected. It leaves the divergence in place;
  the session layer has no way to undo a partial mutation.
- **Skip the record and drop the event silently** — rejected. State would stay consistent, but a
  facilitator would have no trace that a scheduled action never happened.

## Rationale

The decision makes invariant 1 hold on the failure path without touching the success path. It
reuses the rebuild primitive that rewind and undo already rely on, so it adds no second
reconstruction mechanism. The failure record keeps the event log a complete account of the
session (`FR-7110`, `NFR-2600`). Continuing the advance honours `NFR-1600`.

## Consequences

- `07-implementation-planning`: a remediation package for `engine/simulation.py` (and the no-op
  record's handler registration in `engine/handlers.py`), test-first. Tests should cover: a handler
  that mutates then raises leaves live state equal to replay; RNG state equals replay; later events
  in the same advance still fire; other pending events survive; the failure record appears in the
  log and replays as a no-op; the determinism gate stays green.
- `04-requirements-engineering`: no new leaf is needed. `FR-1120` (determinism) and `NFR-1600`
  already require the behaviour; the package cites them.
- Surfacing a failure record to White Cell beyond the event log and AAR (an alarm, for example)
  is not part of this decision.

## Related

`CLAUDE.md` invariant 1; ADR-0002; `FR-1120`, `FR-7110`, `NFR-1600`, `NFR-2600`
(`docs/requirements/`); GDS-03 §2.1 and §4 "Determinism"; `docs/pipeline/backlog.md` `BL-0227`;
`IP-1052`, `IP-1310`.
