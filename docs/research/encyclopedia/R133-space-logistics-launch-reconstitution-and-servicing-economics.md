# R133 — Space Logistics: Launch, Reconstitution, and Servicing Economics

> **Document ID:** R133
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R112](R112-propulsion-and-maneuver-planning.md)
> **Referenced By:** —
> **Produces:** research grounding for any future reconstitution/resupply Implementation Package
> (deferred item; the nearest existing analog is `SessionManager`'s TLE force-add path, `docs/build-spec/04-nfr-milestones-and-risks.md` §10 P6)
> **Feature Mapping:** none yet — research-first per this topic's own scope (§2)
> **Related Topics:** [R112](R112-propulsion-and-maneuver-planning.md) (Propulsion and Maneuver
> Planning — the Δv-economy model this topic extends to the "how do you get more Δv/mass on orbit
> at all" question), [R108](R108-constellation-operations.md) (Constellation Operations — fleet-level
> loss and the sizing guideline reconstitution would restore), [R132](R132-proliferated-constellation-c2-and-mesh-operations.md)
> (Proliferated-Constellation C2 — the scale regime where attrition tolerance and reconstitution
> cadence matter most), `docs/FUTURE-WORK.md` §12.4.6 (the `09-emerging-tech.md` primer stub that
> already names on-orbit refueling as future citation-backbone content)
> **Last Reviewed:** 2026-07-01
> **Primary Sources Consulted:** 3

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Identified as **GAP-05** in the Independent Strategic Review Board report
([`docs/reviews/strategic-review-2026-07.md`](../../reviews/strategic-review-2026-07.md) Part 3):
[R112](R112-propulsion-and-maneuver-planning.md) grounds Δv as a finite, trackable *in-mission*
resource (`AssetResources.delta_v_ms`, non-renewable once a session starts), but the simulator has
no concept at all of what happens *between* sessions or *after* an asset is destroyed or exhausted —
whether a lost or depleted satellite can be replaced, on what timeline, and at what relative cost
compared to servicing it in place. This topic supplies that missing half: the real-world facts about
launch cadence/responsiveness, on-orbit servicing/refueling, and reconstitution timelines, so that
if/when a reconstitution or resupply feature is authorized it is designed against real operational
tempo rather than an assumption-free invention. Per this topic's own scope, **it does not design
that feature** — it is research-first grounding, consistent with MSTR-007 §2.

## 2. Scope

Covers: how fast a real replacement satellite can reach orbit (responsive-launch programs, not
routine multi-year procurement cycles); what on-orbit servicing (refueling, life-extension,
inspection) actually costs and delivers today; and what "reconstitution" means as a doctrinal
concept distinct from ordinary attrition replacement. Does **not** cover: the Δv-economy mechanics
of maneuvering an already-on-orbit asset ([R112](R112-propulsion-and-maneuver-planning.md), unchanged
and still the correct model for in-session propulsion), fleet-level C2 at proliferated scale
([R132](R132-proliferated-constellation-c2-and-mesh-operations.md), a related but distinct
scale-of-command question), or the design of any future reconstitution/resupply feature (explicitly
out of scope — tracked only as a deferred item).

## 3. Concepts

**Responsive launch has moved from doctrine to demonstrated capability, on a timeline the current
simulator has no analog for.** The US Space Force's Tactically Responsive Space (TacRS) program —
online since 2021 — flew its first live demonstration, Victus Nox, in September 2023: Firefly
Aerospace and Millennium Space Systems received a "launch" order and had **24 hours** to update the
trajectory, encapsulate the payload, move it to the pad, and stand ready to launch at the first
available window, ultimately lifting off just **27 hours** after the call-up
([Firefly Aerospace, "Firefly Aerospace Successfully Launches U.S. Space Force VICTUS NOX Responsive
Space Mission with 24-Hour Notice," 2023-09-14](https://fireflyspace.com/news/firefly-aerospace-successfully-launches-victus-nox-with-24-hour-notice/)
([Wayback](https://web.archive.org/web/2026/https://fireflyspace.com/news/firefly-aerospace-successfully-launches-victus-nox-with-24-hour-notice/))
· [Space.com, "New record! Firefly Aerospace launches Space Force mission 27 hours after receiving
order," 2023-09-15](https://www.space.com/firefly-aerospace-rapid-launch-space-force-success)
([Wayback](https://web.archive.org/web/2026/https://www.space.com/firefly-aerospace-rapid-launch-space-force-success))).
Before that call-up window even opened, the space vehicle itself had already been transported ~165
miles from Millennium's El Segundo facility to Vandenberg Space Force Base, tested, fueled, and
mated to its Alpha payload adapter in just under 58 hours of a 60-hour window
([SpaceNews, "Firefly launches Space Force 'Victus Nox' mission," 2023-09-14](https://spacenews.com/firefly-launches-space-force-victus-nox-mission/)
([Wayback](https://web.archive.org/web/2026/https://spacenews.com/firefly-launches-space-force-victus-nox-mission/))).
The post-launch objective was to bring the space vehicle to operational readiness in under 48 hours.
This is the real precedent for "how fast can a replacement asset physically reach orbit" — days, not
the years a routine acquisition cycle implies — but it required a dedicated, pre-funded rapid-call-up
program, not a generic "launch a satellite" capability every operator has on demand.

**Reconstitution is a distinct doctrinal concept from ordinary attrition replacement.** DARPA and
the Space Force frame tactical reconstitution as restoring lost or degraded constellation capability
on tactical timelines — hours to weeks — specifically *in response to* combat losses (ASAT
engagement, debris collision) or surge demand, not as part of a peacetime replenishment schedule
([Air & Space Forces Magazine, "DARPA Seeks Tech to Reconstitute Space Force Satellites During
Conflict," 2026](https://www.airandspaceforces.com/darpa-reconstitute-space-force-satellites-conflict/)
([Wayback](https://web.archive.org/web/2026/https://www.airandspaceforces.com/darpa-reconstitute-space-force-satellites-conflict/))).
The Joint Air Power Competence Centre frames the same concept as a deliberate deterrent: cheap,
reconstitutable proliferated small-satellite architectures reduce the payoff of an adversary's
kinetic ASAT strike because the constellation can be refreshed faster than the adversary can afford
to keep destroying it, which is precisely the strategic logic the strategic review's GAP-10 finding
(closed by [R132](R132-proliferated-constellation-c2-and-mesh-operations.md)) already identifies as
the scale-appropriate context for reconstitution to matter
([JAPCC, "Leveraging Responsive Space and Rapid Reconstitution"](https://www.japcc.org/essays/leveraging-responsive-space-and-rapid-reconstitution/)
([Wayback](https://web.archive.org/web/2026/https://www.japcc.org/essays/leveraging-responsive-space-and-rapid-reconstitution/))).
*Single source (Tier C, cross-corroborated).* Both sources converge independently on the
hours-to-weeks reconstitution timescale and the loss-triggered (not routine) framing, but neither is
a Tier-A program-office document at the level of specificity R132's SDA factsheets reached.

**On-orbit servicing is commercially real today, but at GEO-class cost and single-digit-asset scale
— not a routine field-repair analog.** Northrop Grumman's Mission Extension Vehicle (MEV) program
demonstrated the first commercial satellite life-extension docking: MEV-1 launched October 2019 and
docked to the depleted Intelsat IS-901 on **2020-02-25**, providing five additional years of service
life by taking over the client satellite's propulsion and attitude control rather than transferring
propellant; MEV-2 launched **2020-08-15** and docked to Intelsat IS-1002 on **2021-04-12**
([eoPortal, "MEV-1 & 2 (Mission Extension Vehicle-1 and -2)"](https://www.eoportal.org/satellite-missions/mev-1)
([Wayback](https://web.archive.org/web/2026/https://www.eoportal.org/satellite-missions/mev-1))).
The lease-based commercial model prices this service at roughly a quarter to a half of the
$300-500M cost of building and launching a new GEO comsat — expensive relative to the constellation
sizes ($ per satellite) this simulator's ≤24-satellite guideline implies, and not yet a refueling
capability at all (MEV extends life via docked propulsion, not propellant transfer; true refueling
of satellites never designed for it remains a distinct, less-mature capability track)
([Breaking Defense, "SpaceLogistics sees potential defense market for orbital life-extension
spacecraft," 2022-03](https://breakingdefense.com/2022/03/spacelogistics-sees-potential-defense-market-for-orbital-life-extension-spacecraft/)
([Wayback](https://web.archive.org/web/2026/https://breakingdefense.com/2022/03/spacelogistics-sees-potential-defense-market-for-orbital-life-extension-spacecraft/))).
*Single source (Tier C).* The cost-ratio figure rests on Breaking Defense's reporting alone in this
research pass; it is directionally consistent with the public $300-500M GEO comsat cost range cited
independently across trade press, but the specific quarter-to-half servicing-cost ratio has not been
independently corroborated by a Tier-A/B source in this pass.

**Launch cost has fallen enough to change what "reconstitution" can afford, but the figures are
contested and move fast.** Reusable-booster launch pricing is widely reported in the $2,700-3,000/kg
range for a Falcon 9 dedicated flight against a $69.75M list price, with commercial rideshare slots
(SpaceX Transporter) available near $5,500-6,000/kg for smallsat-class payloads — both figures are an
order of magnitude below the pre-reuse era ([Orbital Radar, "How Much Does It Cost to Launch a
Rocket? Live Cost-Per-Kg Calculator"](https://orbitalradar.com/space-economy/launch-cost-trends)
([Wayback](https://web.archive.org/web/2026/https://orbitalradar.com/space-economy/launch-cost-trends))).
*Single source (Tier C/D, general commercial-press figure).* This is a fast-moving, frequently-revised
commercial pricing figure rather than a fixed engineering constant; it is cited here only to establish
the order-of-magnitude fact (launch is now cheap enough that "just launch a replacement" is a
economically live option for LEO-class assets in a way it was not a decade ago), not as a precise
number an implementer should hard-code.

### Sources

- *Firefly Aerospace, "Firefly Aerospace Successfully Launches U.S. Space Force VICTUS NOX Responsive
  Space Mission with 24-Hour Notice"* (2023-09-14) — [live](https://fireflyspace.com/news/firefly-aerospace-successfully-launches-victus-nox-with-24-hour-notice/)
  · [snapshot](https://web.archive.org/web/2026/https://fireflyspace.com/news/firefly-aerospace-successfully-launches-victus-nox-with-24-hour-notice/)
  · accessed 2026-07-01.
- *Space.com, "New record! Firefly Aerospace launches Space Force mission 27 hours after receiving
  order"* (2023-09-15) — [live](https://www.space.com/firefly-aerospace-rapid-launch-space-force-success)
  · [snapshot](https://web.archive.org/web/2026/https://www.space.com/firefly-aerospace-rapid-launch-space-force-success)
  · accessed 2026-07-01.
- *SpaceNews, "Firefly launches Space Force 'Victus Nox' mission"* (2023-09-14) — [live](https://spacenews.com/firefly-launches-space-force-victus-nox-mission/)
  · [snapshot](https://web.archive.org/web/2026/https://spacenews.com/firefly-launches-space-force-victus-nox-mission/)
  · accessed 2026-07-01.
- *Air & Space Forces Magazine, "DARPA Seeks Tech to Reconstitute Space Force Satellites During
  Conflict"* — [live](https://www.airandspaceforces.com/darpa-reconstitute-space-force-satellites-conflict/)
  · [snapshot](https://web.archive.org/web/2026/https://www.airandspaceforces.com/darpa-reconstitute-space-force-satellites-conflict/)
  · accessed 2026-07-01.
- *Joint Air Power Competence Centre, "Leveraging Responsive Space and Rapid Reconstitution"* — [live](https://www.japcc.org/essays/leveraging-responsive-space-and-rapid-reconstitution/)
  · [snapshot](https://web.archive.org/web/2026/https://www.japcc.org/essays/leveraging-responsive-space-and-rapid-reconstitution/)
  · accessed 2026-07-01.
- *eoPortal, "MEV-1 & 2 (Mission Extension Vehicle-1 and -2)"* — [live](https://www.eoportal.org/satellite-missions/mev-1)
  · [snapshot](https://web.archive.org/web/2026/https://www.eoportal.org/satellite-missions/mev-1)
  · accessed 2026-07-01.
- *Breaking Defense, "SpaceLogistics sees potential defense market for orbital life-extension
  spacecraft"* (2022-03) — [live](https://breakingdefense.com/2022/03/spacelogistics-sees-potential-defense-market-for-orbital-life-extension-spacecraft/)
  · [snapshot](https://web.archive.org/web/2026/https://breakingdefense.com/2022/03/spacelogistics-sees-potential-defense-market-for-orbital-life-extension-spacecraft/)
  · accessed 2026-07-01.
- *Orbital Radar, "How Much Does It Cost to Launch a Rocket? Live 2026 Cost-Per-Kg Calculator"* — [live](https://orbitalradar.com/space-economy/launch-cost-trends)
  · [snapshot](https://web.archive.org/web/2026/https://orbitalradar.com/space-economy/launch-cost-trends)
  · accessed 2026-07-01.

## 4. Operational Context

A White Cell running a multi-session or extended campaign-style exercise (the capstone Vignette 8 /
AAR-replay format the simulator already supports, per `CLAUDE.md`'s P7 note) may want to model a
Blue or Red satellite being destroyed and ask "what happens next" beyond the current session
boundary. Real operators distinguish sharply between three tempos that a naive "just spawn a new
satellite" model would collapse into one: **routine replenishment** (years, ordinary procurement,
not modeled here), **tactical reconstitution** (hours to weeks, purpose-built rapid-call-up programs
like TacRS, requires the replacement to already exist or be buildable on that timeline), and
**in-place servicing** (docking to an existing degraded-but-not-destroyed asset, which only helps a
satellite that still exists and is reachable — not a replacement for a destroyed one). Conflating
these three would teach a false lesson: that satellite loss is cheaply and quickly reversible in
general, when in reality only the narrow TacRS-style path is currently fast, and only for assets a
sponsor pre-funded for exactly this contingency.

## 5. Implementation Guidance

- **Do not model "reconstitution" as instant or free.** Any future feature representing asset
  replacement after combat loss should gate it behind an explicit multi-session or multi-day sim-time
  delay reflecting the TacRS 24-72-hour call-up-to-launch precedent at the fastest end — and this
  fastest end should be the *exception*, reserved for a scenario explicitly modeling a
  pre-positioned rapid-response asset, not the default for an arbitrary destroyed satellite.
- **Keep reconstitution and in-place servicing as two distinct mechanics, not one.** Per §3/§4, MEV-
  style servicing only applies to an asset that still exists (`health != "destroyed"`) and is
  reachable for RPO; it should extend `AssetResources`/`BusState` fields on the *existing* `Asset`
  object (e.g., restoring depleted `delta_v_ms` via a docked-servicer event), while reconstitution
  necessarily creates a *new* `Asset` — closer in engine terms to the existing TLE force-add path
  (`SessionManager`, per `CLAUDE.md`'s P6 vignette-library note) than to any maneuver/effect handler.
- **Price servicing and reconstitution asymmetrically with launch/reconstitution scale, not as a flat
  Δv refill.** Per §3's MEV cost-ratio finding, in-place servicing is a relatively expensive,
  single-asset, GEO-class operation in the real world; a future feature should not make it cheaper or
  faster than reconstituting via new launch by default, since the real-world economics do not
  support that ordering for most orbit regimes.
- **This topic does not authorize starting a reconstitution/servicing Implementation Package.**
  Per §2, that remains a deferred, not-yet-scoped item; this topic's role is to ensure that when it
  is scoped, tempo and cost assumptions start from the TacRS/MEV precedent rather than an
  assumption-free "instant respawn."

## 6. Feature Mapping

None yet, by design (§2) — this is research-first grounding for a not-yet-authorized feature. When
reconstitution/servicing mechanics are scoped, the FS-xxx should cite this topic directly.

## 7. Related Topics

[R112](R112-propulsion-and-maneuver-planning.md) (Propulsion and Maneuver Planning — the in-mission
Δv-economy model this topic extends to the between-mission resupply question), [R108](R108-constellation-operations.md)
(Constellation Operations — the sizing guideline reconstitution would restore after loss),
[R132](R132-proliferated-constellation-c2-and-mesh-operations.md) (Proliferated-Constellation C2 —
the scale at which reconstitution's deterrent logic, per §3, actually applies), `docs/FUTURE-WORK.md`
§12.4.6 (the deferred `09-emerging-tech.md` primer stub already naming on-orbit refueling as future
content).
