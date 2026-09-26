# R117 — Directed Energy and Kinetic Effects

> **Document ID:** R117
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R105](R105-custody-theory.md)
> **Referenced By:** FS-105
> **Produces:** implementation constraints for [`engine/engage.py`](../../../spacesim/engine/engage.py), `WEAPON_ENGAGEMENT` access channel, and (new in v1.1) a directed-energy (DE) order/resolution path (`FR-1410`'s `directed_energy` category, currently declared but unreachable from any order — backlog `BL-0066`/`BL-0086`)
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R105](R105-custody-theory.md) (Custody Theory — the weapons-quality gate this category requires), [R101](R101-orbital-mechanics-for-operations.md)
> (Orbital Mechanics — regime as a reachability gate), [R115](R115-electronic-warfare-in-space-operations.md) (Electronic Warfare — DE dazzle shares EW's reversible-deny
> shape, though the mechanism and gating differ), MSTR-002 (kinetic effects are the one
> irreversible category — v1.1 narrows this: see §3.2)
> **Last Reviewed:** 2026-09-26
> **Primary Sources Consulted:** 8 (1 for the v1.0 kinetic content; 7 new for v1.1's directed-energy
> content, WebSearch multi-source corroboration only — see `BL-0087`)

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

*v1.1 changelog (2026-09-26): closes `BL-0086` — the v1.0 file's title named directed energy but
its content was entirely about kinetic engagement. §3.2/§4.2/§5's DE bullets, the Dependencies/
Related Topics/Feature Mapping updates, and this changelog note are new; the v1.0 kinetic content
(§3.1/§4.1 below) is unchanged in substance, only renumbered from a single undivided §3/§4.*

## 1. Purpose

This topic covers the simulator's two most consequence-heavy effect categories: **kinetic
engagement** (`reversible=False`, `kinetic=True`, debris-generating — the one category the engine
has always resolved) and **directed energy** (declared as a category and asset kind since the
engine's five-D model was built, but — until this revision's implementation guidance is acted on —
never actually produced by any order; see `BL-0066`). Both are gated more heavily than the other
three D's categories; this topic gives the implementer the models for each so a new
engagement-adjacent feature respects the right precondition stack.

## 2. Scope

Covers: the kinetic engagement precondition stack (ROE/ammo/weapons-quality/reachability) and its
declared-not-simulated Pₖ/debris-risk models (§3.1); directed-energy weapon mechanisms (laser
dazzle vs. blinding/damage, high-power microwave), their reversibility split, an irradiance-based
effectiveness model, and range/reachability considerations for ground- vs. space-based platforms
(§3.2). Does **not** cover: the weapons-quality custody threshold itself ([R105](R105-custody-theory.md)), the
regime-reachability geometry both categories reuse ([R101](R101-orbital-mechanics-for-operations.md)), or electronic warfare's link-denial
model ([R115](R115-electronic-warfare-in-space-operations.md) — DE dazzle is a distinct physical mechanism from RF jamming despite the
superficial "denies a sensor" similarity).

## 3. Concepts

### 3.1 Kinetic engagement (`engine/engage.py`)

**Engagement requires the full precondition stack, not just an access window.** `_validate` for
`order.action == "engage"` checks, in order: ROE (`roe.get("kinetic_authorized")`), ammo
(`actor.resources.ammo >= 1`), and a **weapons-quality** track (`track.is_weapons_quality(...)`) —
the single highest bar in the engine, per [R105](R105-custody-theory.md)'s threshold-not-synonym distinction. A track that
merely exists (any confidence) does not pass.

**Pₖ is derived from interceptor class, target altitude, and salvo size — not operator-typed.**
Per the Jun 2026 Commands audit (§M2), `engage.kill_probability_from_class` sources its model from
four interceptor classes drawn from open-source DA-ASAT test records; the operator picks a class and
salvo size, and target altitude is derived from the world (the target's periapsis), never typed —
preventing an operator from gaming Pₖ by misreporting target altitude.

**Closing geometry is computed read-only for operator preview before commitment.**
`engage.closing_geometry` (range, range-rate, closing speed, time-to-closest-approach, predicted
miss distance) is a pure function used to show the operator what's about to happen — the same
"see before you commit" pattern as `dry_run()` ([R103](R103-satellite-command-and-control.md)), but specific to the geometric consequences of
a one-way irreversible action.

**Debris risk is a declared property of the effect, not a derived physics simulation.**
`EffectInstance(debris_risk="high", ...)` is set directly on the kinetic effect template — the
debris-cone *consequence* is a documented, declared severity tag for downstream consumers (AAR,
assessment), not a simulated fragmentation/propagation model. The real-world precedent for this
severity tag is stark: Russia's 15 Nov 2021 direct-ascent ASAT test against Kosmos 1408 (~480 km
altitude) generated over 1,500 pieces of trackable debris plus hundreds of thousands of smaller
untracked fragments, forcing ISS crew to shelter as the debris cloud passed
([U.S. Space Command, *Russian direct-ascent anti-satellite missile test creates significant,
long-lasting space debris*](https://www.spacecom.mil/Newsroom/News/Article-Display/Article/2842957/russian-direct-ascent-anti-satellite-missile-test-creates-significant-long-last/)
([Wayback](https://web.archive.org/web/2026/https://www.spacecom.mil/Newsroom/News/Article-Display/Article/2842957/russian-direct-ascent-anti-satellite-missile-test-creates-significant-long-last/))) —
exactly the kind of environment-wide, undoable consequence `debris_risk="high"` exists to flag for
downstream consumers, even though the engine itself does not simulate the fragmentation.

**Reachability is gated by regime, before Pₖ math ever runs.** `AccessProvider._weapon_predicate`
enforces `interceptor_max_alt_m` (default 2,000 km — LEO-only reach by default) and
`interceptor_mask_deg` — a ground-based interceptor sized for LEO genuinely cannot reach a GEO
target regardless of ammo/custody/ROE; this is [R101](R101-orbital-mechanics-for-operations.md)'s regime-as-reachability-gate principle applied
concretely to this effect category.

#### Sources (§3.1)

- *U.S. Space Command, Russian direct-ascent anti-satellite missile test creates significant,
  long-lasting space debris* (2021-11-15 event) — [live](https://www.spacecom.mil/Newsroom/News/Article-Display/Article/2842957/russian-direct-ascent-anti-satellite-missile-test-creates-significant-long-last/)
  · [snapshot](https://web.archive.org/web/2026/https://www.spacecom.mil/Newsroom/News/Article-Display/Article/2842957/russian-direct-ascent-anti-satellite-missile-test-creates-significant-long-last/)
  · accessed 2026-06-27.

### 3.2 Directed energy (new in v1.1 — closes `BL-0086`)

**Two physically distinct DE mechanisms exist, with different reversibility profiles.**
High-energy laser weapons act thermo-mechanically, primarily on external/optical surfaces; when
directed at a satellite's optical sensors this splits into **dazzling** (temporary loss of sight —
does not affect the satellite's underlying function once the laser passes) and **blinding**
(permanent damage to the optics) [(CSIS Aerospace Security, *Counterspace Weapons 101*)](https://aerospace.csis.org/aerospace101/counterspace-weapons-101/)
([Wayback](https://web.archive.org/web/2026/https://aerospace.csis.org/aerospace101/counterspace-weapons-101/))
, corroborated by [(MITRE SPARTA, *High-Powered Laser*, technique EX-0018.02)](https://sparta.aerospace.org/technique/EX-0018/02/)
([Wayback](https://web.archive.org/web/2026/https://sparta.aerospace.org/technique/EX-0018/02/))
, both accessed 2026-09-26. High-power microwave (HPM) weapons instead couple destructive RF
energy directly into electronics via "front-door" (the target's own antennas) or "back-door"
(seams/gaps in shielding) paths, inducing damaging voltage/current surges — a fundamentally
different, internal-electronics mechanism from a laser's external thermal effect. Critically, HPM
attacks **may be reversible or irreversible, and the attacker may not fully control which** —
unlike a laser dazzle, whose reversibility the attacker can calibrate via dwell time and power
[(CSIS Aerospace Security, *Counterspace Weapons 101*, HPM section)](https://aerospace.csis.org/aerospace101/counterspace-weapons-101/)
, accessed 2026-09-26. The real-world precedent for dazzle's reversibility: reports surfaced in 2006
that U.S. imaging satellites were illuminated by ground-based lasers over Chinese territory without
loss of the satellites' collection capability — dazzling, not blinding
[(CSIS, *Space Threat Assessment*; corroborated by Secure World Foundation's *2026 Global
Counterspace Capabilities Report*, which names China's Bohu facility as an operational
ground-based laser-ranging/dazzling/blinding site)](https://www.swfound.org/publications-and-reports/2026-global-counterspace-capabilities-report)
, accessed 2026-09-26.

**DE effectiveness is a function of irradiance at the target, itself a function of power, range,
aperture, and beam quality — a real, citable physical model, not an invented one.** Spot size at
range scales as (wavelength × range) / aperture, so a larger aperture and better beam quality
concentrate more power onto a smaller spot at a given range, raising irradiance; irradiance is what
determines whether a dazzle or a damage threshold is crossed
[(energo.house, *Directed Energy Weapons: Power Requirements Explained*, citing beam-quality/
aperture/range scaling)](https://energo.house/en/energy-technologies/directed-energy-weapons-power-requirements-and-the-science-of-turning-light-into-force.html)
, corroborated by a DTIC technical report on high-energy-laser atmospheric propagation
[(DTIC ADA607774, *High Energy Laser Propagation in Various Atmospheric Conditions*)](https://apps.dtic.mil/sti/tr/pdf/ADA607774.pdf)
, both accessed 2026-09-26. This is the "declared, auditable" model §5 (Implementation Guidance)
calls for: a DE effect's success probability should scale with range (falling off, not a flat
per-class number the way `engage.py`'s discrete interceptor classes are), unlike kinetic
engagement's discrete Pₖ-by-class table — because DE is continuous-physics-driven, not a discrete
munition type.

**Ground-based DE range is atmosphere-limited; space-based DE is not.** For a ground-based laser,
atmospheric attenuation, turbulence, and thermal blooming all degrade effective range and are
weather-dependent — reported attenuation in dense fog/battlefield smoke can exceed 30 dB/km, and a
100 kW-class high-energy laser's effective engagement range against a moving target was reported as
"greater than five kilometers" in clear weather but under three kilometers in hazy/turbulent/rainy
conditions [(DTIC ADA607774)](https://apps.dtic.mil/sti/tr/pdf/ADA607774.pdf), accessed 2026-09-26.
A space-based DE platform (or a ground-based one engaging above the atmosphere) has no such
attenuation term — its effective range is governed by the irradiance/aperture/range relationship
above alone. This means a ground-based DE weapon's effective range genuinely varies with
conditions this simulator does not model (weather) — the practical implication for this engine
(§5) is that ground-based DE reachability should be treated the same way `AccessProvider`'s
existing line-of-sight/mask-angle geometry already gates other ground-to-orbit channels, without
inventing a new weather layer.

#### Sources (§3.2)

- CSIS Aerospace Security, *Counterspace Weapons 101* — [live](https://aerospace.csis.org/aerospace101/counterspace-weapons-101/)
  · [snapshot](https://web.archive.org/web/2026/https://aerospace.csis.org/aerospace101/counterspace-weapons-101/)
  · accessed 2026-09-26.
- MITRE SPARTA, *High-Powered Laser*, technique EX-0018.02 — [live](https://sparta.aerospace.org/technique/EX-0018/02/)
  · [snapshot](https://web.archive.org/web/2026/https://sparta.aerospace.org/technique/EX-0018/02/)
  · accessed 2026-09-26.
- Secure World Foundation, *2026 Global Counterspace Capabilities Report* — [live](https://www.swfound.org/publications-and-reports/2026-global-counterspace-capabilities-report)
  · [snapshot](https://web.archive.org/web/2026/https://www.swfound.org/publications-and-reports/2026-global-counterspace-capabilities-report)
  · accessed 2026-09-26.
- energo.house, *Directed Energy Weapons: Power Requirements Explained* — [live](https://energo.house/en/energy-technologies/directed-energy-weapons-power-requirements-and-the-science-of-turning-light-into-force.html)
  · [snapshot](https://web.archive.org/web/2026/https://energo.house/en/energy-technologies/directed-energy-weapons-power-requirements-and-the-science-of-turning-light-into-force.html)
  · accessed 2026-09-26.
- DTIC, *High Energy Laser Propagation in Various Atmospheric Conditions* (ADA607774) — [live](https://apps.dtic.mil/sti/tr/pdf/ADA607774.pdf)
  · [snapshot](https://web.archive.org/web/2026/https://apps.dtic.mil/sti/tr/pdf/ADA607774.pdf)
  · accessed 2026-09-26.

> **Verification caveat (per `BL-0087`):** this session's `WebFetch` tool was blocked by the
> environment's egress policy for every one of the above domains (confirmed via the proxy status
> endpoint — the same class of restriction `BL-0028` recorded for the R600 authoring pass). Every
> claim above rests on ≥2 independent `WebSearch` results cross-checked against each other, per
> that same precedent, rather than the corpus's normal fetch-and-confirm adversarial verification
> pass (`10-sources-and-methodology.md` §5.3). Not blocking this topic's use — multi-source
> corroboration is solid grounding — but a future session with unrestricted `WebFetch` should run
> the standard verification pass (fetch each URL, confirm the claim, spot-check Wayback
> availability) before this section is relied on with the same confidence as the rest of R100.

## 4. Operational Context

### 4.1 Kinetic

Real kinetic counterspace engagement is bounded by exactly these same gates in the real world:
authorization (ROE), a sufficiently confident and characterized track (you do not engage on a bare
detection), interceptor reach (a direct-ascent system sized for one regime cannot reach another),
and — once fired — an irreversible, debris-generating outcome with consequences for the entire
operating environment, not just the target. This is precisely why the engine treats kinetic effects
as the one category with `reversible=False` — as of v1.0 of this topic.

### 4.2 Directed energy

Real DE counterspace use already exercises exactly the escalation-control logic MSTR-002/CLAUDE.md
build the simulator's own "most effects are reversible" framing around: a state can dazzle a
satellite (reversible, deniable, calibratable) as a lower rung on an escalation ladder before ever
resorting to a kinetic strike (irreversible, overt, debris-generating) — the strategic value of DE
specifically *is* that reversibility, letting an actor signal capability and intent without
crossing the irreversibility threshold kinetic engagement always crosses. At least three states
(the US, Russia, China) have developed, tested, or deployed DE counterspace capabilities, and
several more (France, Germany) are pursuing non-destructive, debris-free on-board laser
capabilities for the same reason — non-destructiveness is the explicit design goal, not an
incidental property [(Secure World Foundation, *2026 Global Counterspace Capabilities Report*)](https://www.swfound.org/publications-and-reports/2026-global-counterspace-capabilities-report)
, accessed 2026-09-26. HPM breaks this clean story: because its reversibility is not
attacker-controllable, doctrine treats it as a more escalatory class of "non-kinetic" effect than
laser dazzle, closer in risk profile to a kinetic action than to reversible EW — a real doctrinal
tension this topic surfaces rather than resolves (see §5 and Open Questions in `FS-105` v1.1).

## 5. Implementation Guidance

- **A new kinetic effect must derive its success/kill probability from a declared, auditable
  database** (like the four-class `INTERCEPTORS` table), never an operator-typed number — this
  mirrors the same audit-driven fix applied to jam ([R115](R115-electronic-warfare-in-space-operations.md)) and engage.
- **A new directed-energy effect's success probability should derive from the irradiance/range/
  aperture relationship in §3.2, not a discrete per-class table** — DE is continuous-physics-driven
  (spot size ∝ wavelength × range / aperture; effectiveness falls with range), unlike kinetic's
  discrete interceptor classes. A DE implementation package should propose a specific formula
  (e.g. an inverse-range-squared or inverse-spot-area falloff, parameterized by a declared
  `power_w`/`aperture_m`/`beam_quality` per DE asset template) grounded in this section, not invent
  one from scratch nor leave it operator-typed.
- **A DE effect must carry the dazzle/blind reversibility split, not one flag for all DE.** Per
  §3.2: a low-irradiance/short-dwell effect should resolve as reversible (`deny`/`disrupt`,
  `reversible=True`) and a threshold-crossing high-irradiance/sustained-dwell effect as irreversible
  (`degrade`/`destroy`, `reversible=False`) — the crossing point is a design parameter this
  guidance names but does not fix a number for (no open-source irradiance-threshold figure was
  found; see Open Questions in `FS-105` v1.1). HPM's attacker-uncontrollable reversibility (§3.2)
  means an HPM-class DE effect should default to the irreversible branch unless a future revision
  characterizes a graduated HPM severity model.
- **Never relax the weapons-quality gate for a new engagement-like feature** — if a feature needs a
  lower-confidence-bar engagement type, it must say so explicitly as a new, distinctly-named
  confidence tier ([R105](R105-custody-theory.md) §4), not silently read raw detection confidence. A reversible DE
  dazzle plausibly warrants exactly such a new, lower, distinctly-named tier (it is not a one-way
  irreversible action the way kinetic and DE-damage are) — this is named as an open design question
  for `06-feature-specification`/`03-architecture-design-synthesis` to resolve, not decided here.
- **Preserve the regime-reachability check (`interceptor_max_alt_m`/`interceptor_mask_deg`) for any
  new interceptor class**, and reuse the same line-of-sight/mask-angle reachability model for a new
  ground-based DE reachability rule rather than inventing a parallel one (§3.2) — don't bypass
  `AccessProvider._weapon_predicate` (or its ground-DE analog) with a duplicate reachability check.
- **Mark any new irreversible/debris-generating effect with the matching `reversible=False`,
  `kinetic=True` (or analogous) flags** so downstream consequence-confirm UI (the kinetic
  consequence-confirm dialog) and assessment (DOM-002) treat it with the same gravity. A DE-damage
  effect is not `kinetic=True` (no debris) but should still gate through the same consequence-
  confirm pattern given its irreversibility.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer for both kinetic and (as of v1.1's guidance)
directed-energy engagement-class features — any new engagement-class feature must preserve the
existing consequence-confirm UX pattern for irreversible actions.

## 7. Related Topics

[R105](R105-custody-theory.md) (the weapons-quality gate this category's defining precondition), [R101](R101-orbital-mechanics-for-operations.md) (regime as a
reachability gate), [R115](R115-electronic-warfare-in-space-operations.md) (Electronic Warfare — DE dazzle's reversible-deny shape parallels EW's,
though the physical mechanism and gating differ), MSTR-002 (the five-D taxonomy; v1.1 narrows its
"kinetic is the one irreversible category" framing — DE-damage and uncontrolled-severity HPM are
also potentially irreversible, an open tension this topic surfaces rather than resolves).
