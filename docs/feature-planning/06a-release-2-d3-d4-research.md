# Release 2.0 Decisions D3 and D4 — Research Memo

[↑ Feature planning index](INDEX.md) · Research: [R138](../research/encyclopedia/R138-satellite-service-availability-and-link-denial-measurement.md) ·
[R139](../research/encyclopedia/R139-passive-rf-emitter-characterization-and-geolocation.md)

> **What this is.** The `02-research-ow-orbital-mechanics` grounding the owner asked for (2026-11-01) for
> two owner decisions in the Release 2.0 plan (`06-release-2-plan.md` §6 D3/D4, on branch
> `claude/release-2-plan`, not yet on `main`). The owner wants both decided on the physical reality the
> simulator models, not on code convenience. **Not** a requirement, spec or package; nothing here is
> authorized work. Code was read at `origin/main` `be41705` and was not changed.
>
> **Source caveat.** Direct page fetch was blocked in the authoring environment. Citations in R138/R139
> were checked against search-index abstracts and are queued for the `10-sources-and-methodology.md`
> §5.3 verification pass. The two load-bearing findings below (the D3 MOE/MOP gap, and the D4 geometry
> and receiver-direction findings) rest on the engine's own code and the vignette's own orbit elements,
> not on external numbers.

## D3 — Availability objective

**Recommendation: option (a), promoted to Must, with four precise refinements.**

**Physical rationale.** Every standard and contract that defines service availability measures it at
the **user end**, as a **fraction of time over an interval**: the GPS SPS PS PDOP and position-service
availability percentages, Starlink's 99.9% SLA counted from terminal-to-network pings, ITU-T
unavailable-seconds. Asset availability (A_o = uptime/(uptime+downtime)) is a different quantity. A
satellite can be fully healthy while users in a jammed area have no service, which is exactly the
Baltic GNSS pattern of 2024–25 and `coa-russia-ml`'s own brief. In doctrine terms, the shipped
objectives score a measure of performance (the bird is healthy) under a measure-of-effectiveness label
("service available"). Option (b), health and not-denied at the deadline instant, is still a one-instant
reading: it scores a 59-minute jam that lifts at T+59 as MET. Option (c) keeps the wrong lesson.
(R138 §3–§4.)

**What the metric computes (R138 §5).** New objective kind (working name `service_availability`); keep
`asset_operational` unchanged as the survival MOP.

- Instant `t` is unavailable if the asset is destroyed, or in safe mode, or
  `is_link_denied(world, target, t, link)`, or (PNT only) `is_link_spoofed(world, target, t)`.
- `availability = 1 − |unavailable ∩ [from_s, by_s]| / (by_s − from_s)`; **MET iff `now ≥ by_s` and
  `availability ≥ min_fraction`**; the running fraction is shown as in-progress before the deadline.
  Optionally report the longest outage and gate on `max_outage_s`.
- Computed by **exact interval arithmetic**: `world.active_effects` is never pruned, and safe-mode and
  destroyed intervals come from replay. Not by coarse sampling, which would alias short jams
  (invariant 5).
- `link` defaults to the **service** link (`downlink` plus unscoped). The engine's `uplink` is the TT&C
  command path, so jamming it does not by itself cut user service.

**Acceptable moderate-fidelity simplifications.** Asset-scoped denial stands for "the theater's users
are denied", because each vignette has one theater; a user-area `GroundSite` is the later growth path.
No DOP or constellation geometry for PNT. No separate link-budget computation, because the jam model's
`ActiveEffect` outcome already decides margin exhaustion. No debounce by default. **Known gap to flag,
not fix:** the engine has no user/transponder uplink separate from TT&C, so global-effect uplink jamming
of a bent pipe is approximated with `link: any`.

**Implied requirement and acceptance tests** (for `04-requirements-engineering`, then `06`/`07`):

1. Jam of the service link across the whole window → availability 0.0, NOT MET. The same run under
   `asset_operational` reads MET (this is the B-18 regression).
2. No effects → 1.0, MET.
3. Jam covering exactly 20% of the window → availability 0.80 (exact). MET at `min_fraction: 0.75`,
   NOT MET at 0.9.
4. Coherence: at every sampled instant, Red `link_denied` true ⇒ Blue instantaneous-available false (the
   two use the same predicate and `link`).
5. Safe mode for N seconds and destruction at t_d are each counted as outage, for N seconds and for
   `[t_d, by_s]` respectively.
6. A command-uplink-only jam does not reduce downlink-service availability. With `link: any` it does.
7. A PNT spoof interval counts as unavailable; the same interval on a SATCOM asset does not.
8. Determinism: identical replay gives an identical fraction, and rewind then re-advance recomputes it
   exactly.
9. Never MET before `by_s`.

**Impact on plan tiers.** F-03 + B-18 move **Should → Must** (as the plan recommends). Scope is larger
than "two objectives". **11 objectives in 8 vignettes** (`03-gnss-ew-campaign`, `06-satcom-cyber-link`,
`08-multi-domain-taiwan`, `coa-china-md`, `coa-china-ml`, `coa-misc-iran-ml`, `coa-russia-md`,
`coa-russia-ml`) need re-pointing, plus their briefs' "NOTE: measures health" caveats, their playbook
entries and `test_vignette_tutorials.py` expectations. Estimate: 1 code package (M) + 1–2
`08-vignette-development` runs + a manual-impact pass. The survival objectives in five other vignettes
stay as they are.

## D4 — SIGINT characterization path

**Recommendation: a corrected option (a), "(a′)". Neither (a) as worded nor (b) is physically
achievable.**

**Findings that change the options (R139 §3.4, §5):**

- `passive_rf_fix()` models **ground receivers against an orbiting emitter**. Against `RED-EMITTER`
  (a ground station, received by satellites) it always returns `None`: `_is_emitting` reads a
  `bus_state` the ground asset does not have, and `SENSOR_OBSERVATION` accepts only satellite targets.
  Wiring it in unchanged (option (a) as worded) cannot reach the objective.
- **The vignette's constellation geometry makes common view impossible.** At ≈800 km altitude, a
  satellite sees a ground point within ≈22.7° (5° mask) to 27.3° (0° mask) of Earth central angle.
  SIGINT-1/2/3 are 120° apart in one plane, beyond the ≈45–55° that common view allows, so no two of
  them ever hear the emitter at the same time. TDOA/FDOA need simultaneous reception, so even a correct
  mechanic could not characterize the emitter. Real systems cluster their collectors: PARCAE triplets,
  HawkEye 360 clusters ≈300 km apart.
- Option (b) is physically wrong. `sigint.task_collection` executes when the command is **delivered**
  over TT&C, not when the emitter is in the collector's footprint. Producing a Track there characterizes
  an emitter the satellite cannot see, and it bypasses window gating (invariant 4).
- The `emitter_silent` (EMCON) inject is message-only. No ground emitter has an emission state.

**(a′) in one line:** characterize through the `observe` order (`intent="characterize"`) issued by
SIGINT payload assets, using a **generalized** `passive_rf_fix()` (space receivers against a ground
emitter, via the existing ground↔satellite visibility predicate) and `geolocation_error_km()` for the
fix error.

**What "characterized" must mean (R139 §3.1).** The emitter was emitting during the collection, AND
≥3 SIGINT receivers had simultaneous view (FR-1650's 2D count), AND
`geolocation_error_km(band, mode, dwell_s, n_receivers) ≤ max_error_km` (authored on the objective).
An intercept that fails on geometry or error raises detection confidence but leaves
`characterized=False`. The error is recorded on the Track for display. `sigint.task_collection` stays
the configurator whose `band`/`intercept_mode`/`dwell_s` the observe order reads.

**Implied requirements and acceptance tests:**

- FR-1650 delta (`04`): passive-RF fix also covers space-based receivers against a ground emitter. A new
  leaf for an emitter's emission state, and an EMCON inject effect that sets it.
- Tests: (1) clustered 3-sat geometry, emitter on, `geolocate` mode → characterized. (2) Same geometry,
  emitter silent (EMCON inject) → not characterized and `dry_run` names the reason. (3) 2 receivers in
  view → not characterized (FR-1650 count). (4) Error above `max_error_km` (short dwell, `scan` mode) →
  detected but not characterized. (5) The shipped 120°-phased geometry → no simultaneous view at any t
  (a geometry regression test that pins the finding). (6) The bus verb alone never sets `characterized`.
  (7) Determinism under replay and rewind.
- Vignette (`08-vignette-development`): cluster the three satellites a few degrees apart (≈250–500 km),
  change the learning objective from "multi-pass" to "simultaneous look angles", make Red's
  `deny_characterization` the complement of Blue's predicate instead of `deny_custody`, and fix
  `preserve_constellation` (its description says all 3 satellites but its metric targets only SIGINT-1).

**Impact on plan tiers.** F-04/B-19/B-20 stay **Should**. Size moves from M toward **M+**: 1–2 code
packages (passive-RF generalization plus emission state and EMCON effect; the observe-path wiring), one
requirements delta, and one vignette run. It is still inside R2.0's "finish half-wired seams" theme.
Single-satellite multi-pass Doppler geolocation (the Cospas-Sarsat technique, which needs two passes to
resolve the A/B ambiguity) is real and matches the vignette's original wording. It goes in **Could** as
a follow-on that reuses the same `characterized` predicate.

## Next step

Route both to `00-pipeline-manager` with the Release 2.0 intake (§7 of the plan): the D3 metric to `04`
(new objective-kind requirement) and then `06`; the D4 FR-1650 delta to `04`; the content fixes to
`08-vignette-development`. The owner still makes the D3/D4 decision. This memo is the evidence for it.
