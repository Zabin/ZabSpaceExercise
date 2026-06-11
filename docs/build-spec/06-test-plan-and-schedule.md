[← Build Spec index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 15. Test plan

Testing is part of the deliverable, not an afterthought (NFR-7). Strategy by layer:

### 15.1 Engine unit tests (headless, fast, deterministic)
- **Propagation/windows (M2):** pass times for known TLEs vs. Skyfield reference within
  tolerance; J2 nodal drift present; eclipse intervals sane; all six channels produce windows.
- **Effects (M3):** each category→outcome; reversibility restores state; kinetic spawns a
  debris object and trips the political-consequence side effect; cyber resolves with no window.
- **Custody (M3):** decay curve; reset on observation; gate blocks under-tracked engagement.
- **Bus/payload (M3.5):** battery drains in eclipse and trips limits; storage fills and blocks
  collection; payload disabled when bus unhealthy; safe-mode inducement honors the susceptibility
  formula and dial.
- **Scheduler (M4.5):** ground-uplink vs. ISL path selection; stored-program trigger;
  re-validation failure paths; recovery chain incl. re-safe-on-persistence and the difficulty dial.

### 15.2 Determinism property test (NFR-3, from M1)
Generate randomized legal action sequences; assert that re-running from the same seed reproduces
identical per-tick **state hashes**; assert that **rewind→replay** matches the original forward
run up to the rewind point. Run in the local CI-style check on every change.

### 15.3 Fog-of-war / role tests (M4)
Assert the **API itself** (not just the UI) withholds: Red cannot read Blue hidden parameters,
unobserved objects, or another role's private state; a bus role cannot issue payload commands and
vice-versa; an operator cannot act on unassigned assets. (OR-1/2, FR-E7)

### 15.4 Scenario validation tests (M6)
Malformed TLE, missing `roles_needed` asset, unknown template, out-of-range parameter → precise
load-time errors (NFR-6). All 8 shipped vignettes load and validate.

### 15.5 GUI/workflow acceptance (M5, manual + scripted where possible)
Drive the **demo DoD** (§10.1) end-to-end; verify every disabled control explains itself; verify
the screen-blank hides sensitive content; verify the classification banner on screens and the
written log.

### 15.6 Performance test (NFR-2/4)
~24-satellite scenario at 600× on the reference laptop profile: UI stays responsive; window
computation does not block the event loop; memory stable over a 2-hour run.

---

## 16. Phased schedule & effort

Sequencing follows §10 above; this is the milestone-level view with relative effort
(S/M/L) and dependencies. (No calendar dates — single maintainer, user-driven pace.)

| Phase / Milestone | Effort | Depends on | Key output |
|---|---|---|---|
| M0 Skeleton | S | — | repo, loaders, test harness |
| M1 Deterministic core | M | M0 | clock, world, log, hashing, **determinism test** |
| M2 Orbits & windows | L | M1 | Propagator + AccessProvider (moderate) |
| M3 Effects & SDA | L | M2 | EffectResolver, custody, cyber exception |
| M3.5 Bus & payload + safe-mode induce | M | M3 | SOH, payload gating, pass-gated telemetry |
| M4 Session & Vignette 1 (headless) | M | M3.5 | SessionManager, fog CellView, roles |
| M4.5 Planning, tasking & recovery | M | M4 | unified scheduler, ISL, sensor tasking, recovery |
| M5 GUI (incl. 2D ECI+RIC, builder, hot-seat) | L | M4.5 | the playable app; **demo DoD** |
| M6 Content (7 vignettes + builder polish; expanded to 19 in library expansion) | M | M5 | full 19-vignette library |
| M7 Logging persistence & AAR | S | M5 | written log; AAR replay (scrub, branch-compare) |
| M8 LAN multiplayer + multi-monitor pop-outs | M | M7 | server-authoritative lazy clock + RLock + `/api/sessions` discovery + join-by-hash + `?layout=` pop-outs |
| **v1.1** 3D belief-state globe enhancements; constellation aggregation; per-cell auth tokens | L | M8 | see [`../FUTURE-WORK.md`](../FUTURE-WORK.md) |

**Critical path:** M1→M2→M3→M3.5→M4→M4.5→M5→M7→M8 (all complete as of June 2026).
The 2D views and scenario builder were the long poles in M5.

---

## 17. Open items to confirm with White Cell before/after first demo

These are deliberately left open; sensible defaults are in place (§3.3) and can be changed in
data or a short follow-up without architectural impact:
1. Exact **NATO/APP-6-style symbol mapping** for each asset/track type (a lookup table — easy to
   adjust). 
2. Whether observers should default to **god-view** or a **named cell view**.
3. Default **time multiplier** per vignette (currently a parameter; confirm sensible defaults per
   scenario — GEO RPO wants high, LEO ISR wants modest).
4. Whether the **screen-blank** should also require a White Cell click to un-blank (extra
   discipline) or trust the verbal handoff (current default: verbal).
5. The precise **soft/hard limit values** in each asset template's `telemetry_db` (start from the
   research defaults; tune for teaching).

---
