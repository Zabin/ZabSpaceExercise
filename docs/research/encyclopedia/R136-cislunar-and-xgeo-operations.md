# R136 — Cislunar and xGEO Operations

> **Document ID:** R136
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R101](R101-orbital-mechanics-for-operations.md), [R102](R102-space-domain-awareness.md)
> **Referenced By:** [R504](R504-future-space-warfare-concepts.md)
> **Produces:** research grounding for any future cislunar/xGEO regime extension of
> [`engine/propagator.py`](../../../spacesim/engine/propagator.py)'s `Propagator` seam and
> [`engine/geometry.py`](../../../spacesim/engine/geometry.py)'s Earth-centric frames (deferred
> item; no engine implementation exists yet)
> **Feature Mapping:** none yet — research-first per this topic's own scope (§2)
> **Related Topics:** [R101](R101-orbital-mechanics-for-operations.md) (Orbital Mechanics for
> Operations — the Earth-centric two-body+J2 model this topic explains what breaks beyond),
> [R102](R102-space-domain-awareness.md) (Space Domain Awareness — the detect/track/characterize/
> attribute chain this topic identifies new failure modes for at cislunar range), [R118](R118-space-surveillance-networks.md)
> (Space Surveillance Networks — the ground-based sensor-dispersion model whose GEO-range assumptions
> this topic's range/geometry finding challenges)
> **Last Reviewed:** 2026-07-01
> **Primary Sources Consulted:** 2

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Identified as **GAP-04** in the Independent Strategic Review Board report
([`docs/reviews/strategic-review-2026-07.md`](../../reviews/strategic-review-2026-07.md) Part 3):
[R101](R101-orbital-mechanics-for-operations.md) grounds the simulator's Earth-centric two-body+J2
Kepler model plus sgp4 TLE propagation, and [R102](R102-space-domain-awareness.md) grounds the
detect-track-characterize-attribute SDA chain — both explicitly scoped to Earth-orbit regimes
(LEO/MEO/GEO). Neither addresses what changes beyond GEO: the Moon's gravity stops being a
perturbation correction and becomes a first-order force, and the SDA problem changes character (not
just gets harder) because the ground-based sensor geometry both R101 and R102 implicitly assume no
longer holds at lunar distance. This topic supplies that missing grounding, consistent with
MSTR-007 §2's purpose, so a future cislunar/xGEO extension of the `Propagator`/`AccessProvider` seam
(explicitly designed for exactly this kind of fidelity substitution, per ADR-0009) starts from real
operational precedent. Per this topic's own scope, **it does not design that extension** — it is
research-first grounding for a not-yet-authorized regime.

## 2. Scope

Covers: why Earth-centric two-body/J2 dynamics stop being a valid approximation beyond GEO (the
circular restricted three-body problem and near-rectilinear halo orbits as the operationally-relevant
alternative), and why ground-based SDA sensor geometry designed for GEO-range custody does not
extend cleanly to lunar distance. Does **not** cover: the Earth-orbit two-body+J2/TLE propagation
model itself ([R101](R101-orbital-mechanics-for-operations.md), unchanged and still the correct
model for every regime the simulator currently implements), the general SDA detect/track chain
([R102](R102-space-domain-awareness.md), which this topic identifies a new failure mode for but does
not restate), or any specific cislunar mission's engineering detail beyond what is needed to
establish the regime-level operational facts.

## 3. Concepts

**Cislunar space situational awareness has moved from an academic curiosity to a funded program of
record, driven by a genuinely new regime, not an extension of GEO-range SDA.** The Air Force Research
Laboratory's Oracle program (formerly named the Cislunar Highway Patrol System, CHPS) exists
specifically because SDA in the region between Earth and the Moon "poses AFRL's 'biggest' challenge"
— the program's own stated purpose is to demonstrate space situational awareness, object detection,
and tracking near the Moon, motivated by the resurgence of civil, commercial, and international
lunar-exploration activity that needs custody-quality tracking this simulator's Earth-orbit SSN model
was never designed for ([Breaking Defense, "Oracle's vision: Understanding cislunar satellite images
poses AFRL's 'biggest' challenge," 2022-11](https://breakingdefense.com/2022/11/oracles-vision-understanding-cislunar-satellite-images-poses-afrls-biggest-challenge/)
([Wayback](https://web.archive.org/web/2026/https://breakingdefense.com/2022/11/oracles-vision-understanding-cislunar-satellite-images-poses-afrls-biggest-challenge/))).
Oracle's two-satellite Family of Systems (Oracle-Mobility and Oracle-Prime) is explicitly designed to
overcome a geometry problem unique to this regime: solar-exclusion and lunar-exclusion zones limit
what a purely Earth-based or traditional-orbit sensor can see near the Moon at all, requiring
sensor placement *in* cislunar space rather than looking at it from Earth or Earth orbit
([New Space Economy, "AFRL Oracle Program for Cislunar Space Situational Awareness (SSA)"](https://newspaceeconomy.ca/2026/02/04/afrl-oracle-program-for-cislunar-space-situational-awareness-ssa/)
([Wayback](https://web.archive.org/web/2026/https://newspaceeconomy.ca/2026/02/04/afrl-oracle-program-for-cislunar-space-situational-awareness-ssa/))).

**The dynamics underlying cislunar operations are qualitatively different from Earth-orbit
Kepler+J2, not merely a higher-order perturbation correction.** In Earth orbit, lunar/solar gravity
is a third-body *perturbation* on an otherwise-dominant two-body Earth-satellite system — exactly
the small correction [R101](R101-orbital-mechanics-for-operations.md) and `engine/perturbations.py`
already treat it as. In cislunar space, Earth and Moon gravity are of comparable order, and the
governing framework becomes the Circular Restricted Three-Body Problem (CR3BP), not a perturbed
two-body system. The mission-relevant trajectory family this produces — the Near-Rectilinear Halo
Orbit (NRHO), a member of the L1/L2 halo-orbit family with favorable long-term stability properties,
an eccentric shape with a low perilune and high apolune pass — is the orbit class NASA's planned
Gateway lunar station and the already-flown CAPSTONE demonstration both use, and it has no analog
reachable by [R101](R101-orbital-mechanics-for-operations.md)'s Kepler-element parameterization at
all ([Purdue University / AAS 18-406, "Earth-Moon Near Rectilinear Halo and Butterfly..."](https://engineering.purdue.edu/people/kathleen.howell.1/Publications/Conferences/2018_AAS_WhiDavBurMcCPowMcGHow.pdf)
([Wayback](https://web.archive.org/web/2026/https://engineering.purdue.edu/people/kathleen.howell.1/Publications/Conferences/2018_AAS_WhiDavBurMcCPowMcGHow.pdf))).
CAPSTONE (Cislunar Autonomous Positioning System Technology Operations and Navigation Experiment),
launched 2022-06-28 via Rocket Lab, was NASA's own flight demonstration of NRHO operations and
autonomous cislunar navigation, managed by Advanced Space, whose CR3BP operational experience is now
cited by AFRL's own follow-on cislunar SDA work as direct operational precedent
([Air & Space Forces Magazine, "Lunar Activities Advance as Cubesat Enters Orbit, AFRL Awards
'Oracle' Contract"](https://www.airandspaceforces.com/lunar-activities-advance-as-cubesat-enters-orbit-afrl-awards-oracle-contract/)
([Wayback](https://web.archive.org/web/2026/https://www.airandspaceforces.com/lunar-activities-advance-as-cubesat-enters-orbit-afrl-awards-oracle-contract/)))).

**This is a structurally different regime for the simulator's `Propagator` seam, exactly the kind of
substitution ADR-0009 designed the seam to accommodate — but no cislunar implementation exists behind
it.** `engine/propagator.py`'s `ModeratePropagator` computes state via `elements_to_rv` (Kepler+J2,
`engine/orbit.py`) for fictional assets or sgp4 for TLE-backed real satellites — both fundamentally
two-body-with-corrections formulations; `engine/geometry.py`'s frames are Earth-centered (ECI/ECEF
via GMST) with no lunar-frame or barycentric-frame concept at all. A CR3BP-based cislunar
`Propagator` implementation would need a different state representation entirely (typically
normalized Earth-Moon rotating-frame coordinates, not osculating Kepler elements), which is a clean
match for the `Propagator` Protocol's own stated purpose ("a numerical / high-fidelity propagator can
be dropped in later without touching gameplay code," per `engine/propagator.py`'s module docstring)
but represents a larger fidelity jump than any other seam substitution this simulator has scoped so
far — Kepler+J2-to-sgp4 stays within the two-body-family, while Kepler-to-CR3BP does not.

**The GEO-range SDA sensor-geometry assumption breaks down well before reaching cislunar distance,
which is the sharper near-term-relevant finding for this simulator's existing GEO-adjacent
scenarios.** [R118](R118-space-surveillance-networks.md)'s SSN dispersion presets model ground-based
optical/radar sensors whose usable range and geometric-triangulation baseline are calibrated to
LEO-through-GEO distances (~36,000 km at GEO); lunar distance (~384,400 km average) is roughly an
order of magnitude farther, at which range angles-only ground-based optical tracking (the dominant
real-world GEO-belt SDA technique) loses the triangulation baseline/parallax precision that makes
custody-quality tracking possible from Earth alone — precisely the "biggest challenge" AFRL's own
Oracle program cites as its reason to place sensors in cislunar space rather than extend Earth-based
SSN range (§3, first finding). A future xGEO extension does not need the full CR3BP propagator
substitution to be operationally relevant — a superGEO/xGEO custody-degradation model (ground-SSN
custody confidence decaying faster with range beyond GEO) is a smaller, earlier-feasible step that
this simulator's existing GEO-adjacent vignettes could plausibly use before a full cislunar dynamics
model is ever built.

### Sources

- *Breaking Defense, "Oracle's vision: Understanding cislunar satellite images poses AFRL's
  'biggest' challenge"* (2022-11) — [live](https://breakingdefense.com/2022/11/oracles-vision-understanding-cislunar-satellite-images-poses-afrls-biggest-challenge/)
  · [snapshot](https://web.archive.org/web/2026/https://breakingdefense.com/2022/11/oracles-vision-understanding-cislunar-satellite-images-poses-afrls-biggest-challenge/)
  · accessed 2026-07-01.
- *New Space Economy, "AFRL Oracle Program for Cislunar Space Situational Awareness (SSA)"* — [live](https://newspaceeconomy.ca/2026/02/04/afrl-oracle-program-for-cislunar-space-situational-awareness-ssa/)
  · [snapshot](https://web.archive.org/web/2026/https://newspaceeconomy.ca/2026/02/04/afrl-oracle-program-for-cislunar-space-situational-awareness-ssa/)
  · accessed 2026-07-01.
- *Purdue University / AAS 18-406, "Earth-Moon Near Rectilinear Halo and Butterfly Orbits..."* — [live](https://engineering.purdue.edu/people/kathleen.howell.1/Publications/Conferences/2018_AAS_WhiDavBurMcCPowMcGHow.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://engineering.purdue.edu/people/kathleen.howell.1/Publications/Conferences/2018_AAS_WhiDavBurMcCPowMcGHow.pdf)
  · accessed 2026-07-01.
- *Air & Space Forces Magazine, "Lunar Activities Advance as Cubesat Enters Orbit, AFRL Awards
  'Oracle' Contract"* — [live](https://www.airandspaceforces.com/lunar-activities-advance-as-cubesat-enters-orbit-afrl-awards-oracle-contract/)
  · [snapshot](https://web.archive.org/web/2026/https://www.airandspaceforces.com/lunar-activities-advance-as-cubesat-enters-orbit-afrl-awards-oracle-contract/)
  · accessed 2026-07-01.

## 4. Operational Context

A real cislunar SDA operator's job differs from a GEO-belt SDA operator's job in a way that matters
for training realism, not just physics fidelity: the GEO-belt operator reasons about custody as a
continuous confidence-decay problem over an established, well-triangulated sensor network
([R105](R105-custody-theory.md)), while the cislunar operator faces a genuinely sparser, geometry-
constrained sensor picture where solar/lunar exclusion zones create real periods where no ground- or
Earth-orbit-based sensor can see a given cislunar region at all — an availability gap qualitatively
different from the confidence-decay-over-time model this simulator's `Track` custody already
implements for Earth-orbit regimes. A White Cell wanting a cislunar-flavored vignette without waiting
for a full CR3BP propagator could still teach the *SDA* half of this lesson (custody gaps driven by
sensor-geometry exclusion zones) well before the *dynamics* half (NRHO station-keeping, three-body
transfers) is implemented.

## 5. Implementation Guidance

- **Do not attempt to approximate cislunar dynamics inside the existing Kepler+J2 `OrbitState`
  representation.** Per §3's third finding, CR3BP requires a structurally different state
  representation (rotating-frame coordinates, not osculating elements); a future cislunar
  `Propagator` implementation should be a genuinely new `Propagator` Protocol implementation (as
  ADR-0009's seam design already anticipates for exactly this kind of fidelity jump), not an
  extension of `ModeratePropagator`'s existing Kepler/sgp4 branch logic.
- **Sequence a superGEO/xGEO custody-degradation extension before a full cislunar dynamics model, if
  either is authorized.** Per §3's fourth finding, the SDA-range problem (ground-based custody
  degrading beyond GEO range) is both more immediately relevant to the simulator's existing GEO-belt
  scenarios and a smaller implementation lift than the full CR3BP dynamics substitution — a future
  roadmap should not treat "cislunar" as one monolithic feature when its SDA half and dynamics half
  have very different implementation costs and immediate relevance.
- **`engine/geometry.py`'s ECI/ECEF Earth-centered frames should not be silently reused for a future
  cislunar feature.** Per §3's third finding, a genuinely new frame (Earth-Moon rotating/barycentric)
  is required; extending the existing GMST-based ECI↔ECEF conversion to "just add the Moon" would
  produce physically wrong results, not merely lower-fidelity ones.
- **This topic does not authorize starting a cislunar/xGEO Implementation Package.** Per §2, this
  remains a deferred, not-yet-scoped item; this topic's role is to ensure that when either the SDA-
  range extension or the full dynamics extension is scoped, it starts from the real AFRL Oracle/
  CAPSTONE precedent and the CR3BP-vs-two-body structural distinction rather than an assumption-free
  "just extend GEO" design.

## 6. Feature Mapping

None yet, by design (§2) — this is research-first grounding for a not-yet-authorized regime
extension. When a cislunar/xGEO feature is scoped (SDA-range extension or full CR3BP dynamics), its
FS-xxx should cite this topic directly rather than re-deriving the regime-boundary argument.

## 7. Related Topics

[R101](R101-orbital-mechanics-for-operations.md) (Orbital Mechanics for Operations — the Earth-centric
two-body+J2/TLE model this topic explains the structural limit of), [R102](R102-space-domain-awareness.md)
(Space Domain Awareness — the detect/track/characterize/attribute chain this topic identifies a new
range/geometry failure mode for), [R105](R105-custody-theory.md) (Custody Theory — the confidence-decay
model this topic's operational-context section contrasts with cislunar's geometry-driven availability
gaps), [R118](R118-space-surveillance-networks.md) (Space Surveillance Networks — the ground-based
sensor-dispersion model whose GEO-range calibration this topic's SDA finding challenges beyond GEO),
ADR-0009 (the moderate-fidelity propagation decision and its explicit `Propagator`-seam design for
future fidelity substitution).
