# R115 — Electronic Warfare in Space Operations

> **Document ID:** R115
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R110](R110-communications.md)
> **Referenced By:** [R117](R117-directed-energy-and-kinetic-effects.md), FS-105
> **Produces:** implementation constraints for [`engine/jam.py`](../../../spacesim/engine/jam.py), `JAM_FOOTPRINT` access channel
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R110](R110-communications.md) (Communications — the thing EW denies), MSTR-002 (the five-D effect
> taxonomy: EW is `deny`/`disrupt`/`degrade`, never `destroy`), [R116](R116-cyber-operations-against-space-systems.md) (Cyber Operations — the doctrinal
> contrast of window-gated vs. not)

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Electronic warfare is the simulator's most "physics-forward" effect category — jam success and
footprint are derived from power/modulation/bandwidth inputs rather than an operator-typed
probability — and this topic gives the implementer the `jam.py` model behind it so a new EW feature
computes consistently with the existing one.

## 2. Concepts

**Modulation choice trades effectiveness against detectability and attribution.** The
`MODULATIONS` database (`barrage`/`spot`/`sweep`/`deceptive`) each carry `effectiveness`,
`radius_factor`, `attribution_bias`, `detectability`, and `power_factor` — `deceptive` is the most
effective (1.30×) and least detectable (0.20) but is `overt`-attributed once discovered (it
requires intercepting the victim's own signal first), while `barrage` is blunt, easily detected
(0.90), but only `ambiguous`-attributed. There is no free "best" choice — every modulation is a
distinct point on an effectiveness/detectability/attribution tradeoff surface.

**Success probability is fully derived from physical inputs, not operator-typed.** Per the Jun 2026
Commands audit (§C2), `OrderSystem._exec_payload`'s jam branch computes a `base_prob` from a
power-scaled curve (`0.6 + 0.3·√(power_w/100)`, capped at 0.98) then applies `jam.effective_success_prob`
to adjust for modulation and the bandwidth-coverage ratio (`bandwidth_hz` vs. `victim_bandwidth_hz`)
— the operator chooses power/modulation/bandwidth, not a success number directly. A legacy
operator-supplied `success_prob` is parsed for save-file back-compat only and otherwise ignored.

**Jamming is gated by the `jam_footprint` access channel, exactly like other ground-based effects.**
`AccessProvider._weapon_predicate`-style gating via `_ground_sat_predicate` with `jam_mask_deg`
means a jammer must have geometric access (elevation above mask) to the victim, just like a command
uplink — EW is window-gated, the explicit doctrinal contrast with cyber ([R116](R116-cyber-operations-against-space-systems.md)).

**Defensive postures reduce the *experienced* effect, not the underlying probability database.**
`def.frequency_hop` and `satcom.mitigate_interference`/`shift_users` act on the defender's side
(`freq_hopping`, `interference_mitigation`) and are applied by the effect resolver as modifiers —
the attacker's computed `adj_prob` represents the attack's raw potency; the resolver, not the jam
math, is where defender posture knocks it down.

## 3. Operational Context

Real electronic warfare against satellite links is exactly this kind of engineering tradeoff:
power, modulation sophistication, and bandwidth coverage against a link's actual occupied spectrum
determine denial effectiveness, while modulation choice independently determines how detectable and
attributable the jamming is — sophisticated deceptive jamming buys effectiveness and stealth at the
cost of needing prior signal intercept and certain attribution once caught.

## 4. Implementation Guidance

- **A new jamming feature must derive success from physical inputs through `jam.effective_success_prob`**,
  never accept an operator-typed probability — this was an explicit, audited fix (Jun 2026 §C2);
  reintroducing operator-set probabilities is a regression of that fix.
- **A new modulation type must be added to the `MODULATIONS` database** with all five parameters
  (`effectiveness`, `radius_factor`, `attribution_bias`, `detectability`, `power_factor`) — don't
  special-case a new modulation in the resolver instead.
- **EW effects remain window-gated through `JAM_FOOTPRINT`** — do not give a new EW capability a
  cyber-style "resolves anywhere, anytime" path; that exception is reserved for cyber ([R116](R116-cyber-operations-against-space-systems.md)) by
  explicit doctrine.
- **Defensive mitigation should modify the resolver's outcome, not the jam-math module** — keep
  `jam.py` a pure, defender-agnostic computation of the attack's raw potency.

## 5. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer — any EW-adjacent UI should expose the
modulation tradeoff (effectiveness vs. detectability vs. attribution) explicitly, not collapse it to
a single "jam" button.

## 6. Related Topics

[R110](R110-communications.md) (Communications — what EW denies, and the defensive postures that mitigate it), [R116](R116-cyber-operations-against-space-systems.md) (Cyber
Operations — the doctrinal not-window-gated exception), MSTR-002 (the five-D taxonomy EW operates
within).
