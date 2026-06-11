# Orbital Mechanics Primer — The Sim's Physics of Access

This file defines the **physics that constrains Red and Blue actions**. The user's core
requirement: cells can only interact with space systems within *realistic limitations —
access times based on orbit pass times and ground stations.* This file specifies the
"moderate fidelity" model and names the seams where a high-fidelity model swaps in.

The single most important design rule:

> **You cannot command, observe, or attack a satellite whenever you feel like it. You can
> only act when geometry permits — when the satellite is in view of the right ground
> station, sensor, jammer, or interceptor. Everything else is *waiting for the pass.***

---

## 1. Orbital regimes (sets which actions are even possible)

| Regime | Altitude | Period | Pass behavior | Typical missions | Reachable by |
|---|---|---|---|---|---|
| **LEO** | ~300–2,000 km | ~90 min | Short passes (~5–12 min), many per day, ground track shifts each orbit | ISR, some SATCOM, weather | everything |
| **MEO** | ~2,000–35,786 km (GNSS cluster ~19,100–23,222 km) | ~6–14 h | Long passes, slow geometry | GNSS/PNT | EW/cyber mostly; kinetic hard |
| **GEO** | ~35,786 km | 23 h 56 m (sidereal) | **Effectively fixed** over a longitude; always in view of its region | SATCOM, missile warning, some ISR | EW/cyber/RPO/DE; kinetic very hard |
| **HEO** | elliptical | ~12 h | Long dwell near apogee over high latitudes | Missile warning, polar comms | EW/cyber/RPO |
| **Cislunar** | beyond GEO | days+ | Specialized | SDA, future | (future/high-fidelity) |

**Why this matters in play:** the regime of the target determines the menu. A LEO ISR sat
is vulnerable to nearly everything but only *reachable* for a few minutes per pass. A GEO
SATCOM sat is almost impossible to kill kinetically but sits still for EW/cyber/RPO. The sim
teaches this by *construction*, not by lecture.

---

## 2. The access window — the central game mechanic

An **access window** is a time interval during which a specific *actor asset* can interact
with a specific *target* via a specific *channel*. The engine continuously computes these and
gates every action against them.

```yaml
access_window:
  actor_asset:   # ground_station | sensor | jammer | interceptor | satellite
  target:        # satellite | ground_site
  channel:       # command_uplink | telemetry_downlink | sensor_observation |
                 # jam_footprint | weapon_engagement | rpo_proximity
  start_utc:
  end_utc:
  quality:       # 0..1 — peak elevation / link margin proxy
  geometry_note: # max elevation, range, sun angle (for optical), etc.
```

### Window types the engine must compute

1. **Ground-station ↔ satellite (command/telemetry).** A satellite can only be *commanded*
   or *downloaded* when it rises above the minimum elevation mask of one of the owner's
   ground stations. **A Red/Blue order to a satellite queues until the next station pass.**
   This is the most important realism constraint in the whole sim.
2. **Sensor ↔ target (SDA observation).** Radar/optical sensors can only track a target when
   it is above the horizon (and for optical: target sunlit, sensor in darkness). Custody
   decays between observations.
3. **Jammer footprint ↔ target/user (EW).** Uplink jam needs the jammer inside the
   satellite's receive footprint; downlink jam needs it near the victim user; both need LOS.
4. **Interceptor ↔ target (kinetic engagement).** DA-ASAT: target within reachable
   altitude/inclination and correct geometry over the launch site. Co-orbital: a computed
   *closing window* after a phasing maneuver.
5. **RPO proximity ↔ target.** Distance-to-target falls below a threshold after maneuvering;
   creates inspection/escort/strike opportunities and is observable by the defender.

> **Design seam:** all windows come from one interface, `AccessProvider.windows(actor,
> target, channel, horizon)`. v1 implements it with simplified propagation; high fidelity
> swaps the implementation only.

---

## 3. Moderate-fidelity propagation model (v1)

The goal is *believable* pass times and geometry, not mission-planning accuracy.

- **Orbit representation:** classical Keplerian elements per satellite
  `{a, e, i, RAAN, argP, true_anomaly, epoch}` for fictional / generic assets. For
  TLE-sourced assets, sgp4 is used directly via the `Propagator` seam
  (`spacesim/engine/propagator.py`); the elements are not back-converted to
  Keplerian, so SGP4 perturbation effects are preserved for real-satellite scenarios.
- **Propagation:** two-body Keplerian propagation plus **J2 nodal precession** (so RAAN
  drifts and Sun-synchronous orbits behave, which matters for ISR pass timing). This is the
  cheap model that still produces correct *pass cadence and ground-track drift* — the things
  players feel.
- **Ground tracks & visibility:** propagate to ECI, rotate to ECEF using GMST (sidereal
  time), convert to lat/lon/alt; compute elevation/azimuth from each ground site; a pass is
  the interval where elevation ≥ mask (default 5–10°).
- **Maneuver / delta-v:** model orbit changes as **impulsive burns** that edit the Keplerian
  elements (Hohmann-style transfers for regime changes, phasing burns for RPO). Track a
  **fuel/delta-v budget** per maneuverable asset; when it's gone, the asset can't maneuver.
- **RPO closing:** approximate phasing time from the difference in orbital period and the
  required phase angle; surface a "time to close" estimate to the operator.
- **Lighting:** simple cylindrical Earth-shadow model for eclipse (power) and a Sun-position
  model for optical observation/dazzle constraints.

### Implemented in v1 and deliberately deferred to high fidelity (behind the interface)

The propagator seam in `engine/propagator.py` admits two implementations:
**(a) Keplerian + J2** for fictional assets (the rest of this section), and
**(b) sgp4** for any TLE-sourced asset, which gives standard SGP4 perturbation
behaviour out of the box. Beyond that, deferred for v1:

- General full-perturbation numerical propagators (Cowell / Encke).
- True RF link budgets (EIRP, G/T, path loss, rain fade) instead of the `quality` proxy.
- Continuous-thrust (electric) maneuvers; precise Lambert-solver intercepts.
- Atmospheric drag decay, solar radiation pressure, third-body lunar/solar.
- Conjunction/collision and detailed debris propagation (v1 uses a coarse debris-field model).

---

## 4. Time and the timeline

- The sim runs on **simulated UTC**. Real-time by default (1× wall clock).
- White Cell can set the **time multiplier** (e.g., 1×, 10×, 60×, 600×) so a multi-day GEO
  RPO closes within a session, and can **pause, fast-forward, rewind, and undo** (see White
  Cell controls doc). Red/Blue cannot change time.
- Because windows are deterministic functions of orbital state + time, **rewind is exact**:
  re-propagating from a saved state reproduces identical windows. This is why the engine must
  be deterministic given `(initial_state, action_log, seed)`.

---

## 5. What the operator sees (turning physics into UX)

For each of their assets, Red/Blue see:
- **"Next contact in 00:07:12 via STATION-BRAVO (6 min window, max el 41°)"** — a live
  countdown to the next actionable window.
- A **pass timeline ribbon** per asset showing upcoming windows colored by channel.
- A **command queue**: orders accepted now but *executed at the next valid window*, with the
  scheduled execution time shown.
- For SDA: a **custody confidence** meter per tracked object that decays between observations.

> **Teaching effect:** players internalize that space ops are a game of *scheduling against
> orbital geometry* — pre-positioning tasking, racing the adversary to the next pass, and
> accepting that some actions simply cannot happen for hours.

## Sources / basis
- Standard astrodynamics (Vallado, *Fundamentals of Astrodynamics and Applications*) for the
  Keplerian + J2 + GMST visibility approach used at moderate fidelity.
- USSF *Space Warfighting* (2025) for the doctrinal framing of maneuver, lines of
  communication, and segment access.
- SWF *Global Counterspace Capabilities* (2025/2026) for regime-dependent reachability of
  each counter type.
