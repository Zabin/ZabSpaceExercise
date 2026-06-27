# R104 — Collection Management

> **Document ID:** R104
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R102](R102-space-domain-awareness.md), [R109](R109-sensor-operations.md)
> **Referenced By:** [R118](R118-space-surveillance-networks.md), [R119](R119-space-situational-data-fusion.md), FS-104
> **Produces:** implementation constraints for [`engine/orders.py`](../../../spacesim/engine/orders.py) (`_plan_collection`, `_sensor_bookings`)
> **Feature Mapping:** FS-104 (SDA Tasking)
> **Related Topics:** [R102](R102-space-domain-awareness.md) (SDA), [R109](R109-sensor-operations.md) (Sensor Operations), [R118](R118-space-surveillance-networks.md) (Space Surveillance Networks)

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Collection management is what turns "we have sensors" into "we have custody of the right things at
the right time" — it is a continuous resource-allocation problem, not a one-time setup, and this
topic gives the implementation model behind `OrderSystem._plan_collection`/`_contended` so a new
sensor or tasking feature respects existing contention rather than quietly bypassing it.

## 2. Concepts

**Tasking is contended, not infinite.** `OrderSystem._sensor_bookings` records one task at a time
per sensor as `(start, end)` intervals; `_contended()` rejects an order whose proposed window
overlaps an existing booking on the same sensor. A sensor cannot be tasked against two targets at
once — this is the structural reason collection planning is a real scheduling problem.

**"Auto" tasking vs. named-sensor tasking.** An order with `actor="auto"` lets `_candidate_sensors`
search every sensor the cell owns for the earliest uncontended window; a named sensor restricts the
search to that one asset. A new feature that adds tasking should preserve both modes — operators
need the explicit-control path as much as the convenience path.

**Two distinct contention/SLA systems exist side by side.** Organic sensor tasking (this topic) is
windowed and first-come-first-served via `_sensor_bookings`; the SSN ([R118](R118-space-surveillance-networks.md)) is a separate
priority/SLA-queued system (`immediate`/`priority`/`routine` with `MAX_WAIT_S`/`PROCESSING_DELAY_S`)
for off-board collection requests. They are not the same resource pool — don't conflate "the sensor
is free" with "an SSN slot is free."

**Auto-cueing bridges organic detection to SSN tasking.** `OrderSystem.auto_cue_ssn`, when set,
automatically files an SSN `characterize` request when an organic observation produces a track with
confidence in `(0.3, 0.85)` that isn't yet characterized — modeling the real-world practice of
escalating a marginal detection to a higher-capability asset rather than re-tasking the same sensor
indefinitely.

## 3. Operational Context

Real collection management is the unglamorous daily work of SDA operations: competing requests for
scarce, finite sensor time, prioritized against mission value, with explicit SLAs for how long a
request can wait before it's considered failed. The simulator's `_contended` check and the SSN's
priority-cost budget ([R118](R118-space-surveillance-networks.md)) exist to make operators feel that scarcity as a planning constraint,
not an artificial difficulty dial.

## 4. Implementation Guidance

- **A new sensor modality must register its bookings in `_sensor_bookings`** (or the SSN-equivalent
  request queue) — a parallel ad hoc availability tracker would let two orders silently double-book
  the same sensor.
- **`cancel()` must release the booking it created**, exactly mirroring `_release_bookings_on_execute`
  — a tasking feature that doesn't release on cancel leaks capacity that can never be reclaimed for
  the rest of the session.
- **Don't let a new feature "jump the queue."** If a feature needs priority tasking, model it as a
  new SSN-style priority tier ([R118](R118-space-surveillance-networks.md)) with its own published SLA, not as a side channel that bypasses
  `_contended`.
- **Auto-cueing logic (escalation from organic to SSN) should stay confidence-band-gated**, not
  triggered on every observation — an unconditional auto-cue would flood the SSN request queue and
  defeat its own scarcity model.

## 5. Feature Mapping

FS-104 (SDA Tasking) is the direct consumer. [R118](R118-space-surveillance-networks.md) (SSN) is the parallel off-board collection system;
[R119](R119-space-situational-data-fusion.md) (Data Fusion) consumes the combined output of both.

## 6. Related Topics

[R102](R102-space-domain-awareness.md) (SDA — the chain stage this tasking advances), [R109](R109-sensor-operations.md) (Sensor Operations — the modalities being
tasked), [R118](R118-space-surveillance-networks.md) (SSN — the off-board collection counterpart with its own SLA model).
