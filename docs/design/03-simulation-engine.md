# Simulation Engine — Time, Orbits, Access Windows, Event Loop

This is the heart of the system and the contract Claude Code should implement most carefully.
It must be **deterministic**, **UI-agnostic**, and **fidelity-swappable**. Cross-reference the
physics rationale in `../research/04-orbital-mechanics-primer.md`.

## 1. The simulation clock and event loop

The engine advances **simulated UTC** in discrete ticks. White Cell sets the multiplier; Red/
Blue cannot.

```
loop while running:
    dt_sim = tick_real_seconds * time_multiplier      # how much sim-time this tick covers
    target = clock.now + dt_sim
    # advance in safe sub-steps so no scheduled event is skipped
    for each scheduled event with t <= target (in time order):
        clock.now = event.t
        apply(event)            # maneuver completes, window opens, inject fires, order executes
        eventlog.append(event)
    clock.now = target
    update_derived_state()      # custody decay, fuel, eclipse, recompute upcoming windows
    snapshot_if_due()
```

- **Sub-stepping** guarantees that a 600× multiplier never "jumps over" a 6-minute LEO pass.
  Compute the next event time and never advance past it in one step.
- The loop is driven by the SessionManager; at 1× it ticks on a real timer, at high multipliers
  it runs as fast as it can up to the target (fast-forward is just a large multiplier).

## 2. Interfaces (the fidelity seams)

These three interfaces are the entire "moderate-now, high-fidelity-later" story. Implement the
moderate versions in v1; never let callers depend on the implementation.

### `Propagator`
```python
class Propagator(Protocol):
    def state_at(self, orbit: OrbitState, t: SimTime) -> ECIState: ...
    def apply_impulse(self, orbit: OrbitState, dv: Vec3, t: SimTime) -> OrbitState: ...
    def ground_track(self, orbit: OrbitState, t0: SimTime, t1: SimTime) -> list[GeoPoint]: ...
```
- **Moderate impl:** Keplerian + J2 nodal precession; or Skyfield/SGP4 for TLE-backed assets.
- **High-fidelity impl (later):** full SGP4/SDP4 or numerical propagator with drag/SRP/third-body.

### `AccessProvider`
```python
class AccessProvider(Protocol):
    def windows(self, actor: AssetId, target: TargetId, channel: Channel,
                t0: SimTime, horizon: SimTime) -> list[AccessWindow]: ...
```
- Computes the gating windows for every action. **Channels:** `command_uplink`,
  `telemetry_downlink`, `sensor_observation`, `jam_footprint`, `weapon_engagement`,
  `rpo_proximity`.
- **Moderate impl:** elevation-mask passes (ground↔sat), horizon + lighting (sensors),
  footprint LOS (jammers), reachability + geometry (interceptors), range threshold after
  phasing (RPO).
- **High-fidelity impl (later):** real link budgets (EIRP/G-T/path loss), atmospheric effects on
  DE, precise Lambert intercept windows.

### `EffectResolver`
```python
class EffectResolver(Protocol):
    def resolve(self, effect: EffectInstance, world: WorldState,
                rng: SeededRng) -> EffectOutcome: ...
```
- Maps an attempted effect to one of the **5 D's** (deceive/disrupt/deny/degrade/destroy),
  using effect template attributes, target defenses, geometry quality, and the seeded RNG.
- Emits side effects: debris spawn (kinetic), custody/attribution changes, fuel/ammo
  consumption, political-consequence triggers.

## 3. Access-window computation (moderate fidelity, v1)

For each `(actor, target, channel)` over a look-ahead horizon:

1. **Ground ↔ satellite (uplink/downlink):** propagate satellite to ECEF; for each owner ground
   station compute elevation; a window = interval where `elevation ≥ mask` (default 5–10°).
   `quality` ∝ peak elevation.
2. **Sensor observation:** as above, plus for **optical** require target sunlit and sensor in
   darkness (shadow model); radar ignores lighting.
3. **Jam footprint:** uplink jam → jammer must lie within the satellite's receive footprint and
   have LOS; downlink jam → jammer near the victim user with LOS. Window = LOS interval.
4. **Weapon engagement (DA-ASAT):** target altitude/inclination within interceptor reach AND
   target within engagement geometry of the launch site → short engagement window with flight
   time modeled on the timeline.
5. **RPO proximity:** after a phasing maneuver, predict when range to target drops below the
   proximity threshold → proximity window (also visible to the defender's SDA).

**Caching:** recompute windows for an asset only when its orbit changes (maneuver) or when the
horizon advances past the last computed window. This keeps high multipliers cheap.

## 4. Orders, queuing, and execution

Players issue **orders**, not instantaneous actions. An order is validated, then **queued for
the next valid access window**:

```python
@dataclass
class Order:
    actor: AssetId
    action: ActionType           # downlink, image, maneuver(dv), jam(target), rpo_close(target),
                                 # engage(target), escort(asset), cyber(vector), set_posture(...)
    params: dict
    issued_at: SimTime
    earliest_window: AccessWindow | None   # filled by AccessProvider; None ⇒ executes when ready
    status: Literal["queued","executing","done","failed","cancelled"]
```

- On issue: `CellController` checks ownership + ROE/permission, then asks `AccessProvider` for
  the next window for the relevant channel and sets `earliest_window`.
- The Scheduler fires the order when `clock.now` reaches the window; `EffectResolver` resolves it.
- **Cyber orders are the exception:** they are *not* gated by an orbital window — they resolve
  against `{access_vector, success_probability, persistence, patchable}` at issue time (subject
  to the defender's cyber posture). This is why cyber feels fast and flexible.
- Maneuvers consume **delta-v** from the asset's budget; engagement consumes ammo; jammers/DE
  consume power while active.

## 5. Derived-state updates each tick
- **Custody decay:** every tracked object's track confidence decays with time since last
  observation; an observation window resets it. (See `custody.py` / vignette 7.)
- **Fuel / power / ammo** bookkeeping.
- **Eclipse** state for power and optical constraints.
- **Debris fields:** advance coarse hazard regions; per-asset-per-orbit conjunction risk roll.
- **Inject conditions:** evaluate condition-triggered injects.

## 6. Determinism rules (enforce with tests)
- All randomness flows through **one seeded RNG** carried in/with state. No `random()` calls
  anywhere else.
- No wall-clock reads in the engine; only `clock.now`.
- Resolution is a **pure function** of `(WorldState, EffectInstance, rng_state)`.
- Property test: replaying the same EventLog from the same snapshot with the same seed yields a
  byte-identical WorldState. This test *is* the rewind/undo guarantee.

## 7. Save / replay format
A save = `{ initial_state, seed, snapshots[], eventlog[] }`. This supports load, exact rewind,
undo, branching ("what-if"), and full **after-action replay** — critical for the PME use case.
