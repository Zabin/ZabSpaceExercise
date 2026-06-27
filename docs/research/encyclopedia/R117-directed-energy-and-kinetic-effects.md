# R117 — Directed Energy and Kinetic Effects

> **Document ID:** R117
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R105](R105-custody-theory.md)
> **Referenced By:** FS-105
> **Produces:** implementation constraints for [`engine/engage.py`](../../../spacesim/engine/engage.py), `WEAPON_ENGAGEMENT` access channel
> **Feature Mapping:** FS-105 (Spacecraft Operations)
> **Related Topics:** [R105](R105-custody-theory.md) (Custody Theory — the weapons-quality gate this category requires), [R101](R101-orbital-mechanics-for-operations.md)
> (Orbital Mechanics — regime as a reachability gate), MSTR-002 (kinetic effects are the one
> irreversible category)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 1

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Kinetic engagement is the simulator's one genuinely irreversible effect category — `reversible=False`,
`kinetic=True`, with debris consequences — and is gated by the heaviest precondition stack in the
engine: ROE authorization, ammo, weapons-quality custody, and regime reachability. This topic gives
the implementer the `engage.py` model so a new kinetic-adjacent feature respects that stack.

## 2. Scope

Covers: the engagement precondition stack (ROE/ammo/weapons-quality/reachability), the
declared-not-simulated Pₖ and debris-risk models, and the closing-geometry preview pattern. Does
**not** cover: the weapons-quality custody threshold itself ([R105](R105-custody-theory.md)), or the regime-reachability
geometry it reuses ([R101](R101-orbital-mechanics-for-operations.md)).

## 3. Concepts

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

### Sources

- *U.S. Space Command, Russian direct-ascent anti-satellite missile test creates significant,
  long-lasting space debris* (2021-11-15 event) — [live](https://www.spacecom.mil/Newsroom/News/Article-Display/Article/2842957/russian-direct-ascent-anti-satellite-missile-test-creates-significant-long-last/)
  · [snapshot](https://web.archive.org/web/2026/https://www.spacecom.mil/Newsroom/News/Article-Display/Article/2842957/russian-direct-ascent-anti-satellite-missile-test-creates-significant-long-last/)
  · accessed 2026-06-27.

**Reachability is gated by regime, before Pₖ math ever runs.** `AccessProvider._weapon_predicate`
enforces `interceptor_max_alt_m` (default 2,000 km — LEO-only reach by default) and
`interceptor_mask_deg` — a ground-based interceptor sized for LEO genuinely cannot reach a GEO
target regardless of ammo/custody/ROE; this is [R101](R101-orbital-mechanics-for-operations.md)'s regime-as-reachability-gate principle applied
concretely to this effect category.

## 4. Operational Context

Real kinetic counterspace engagement is bounded by exactly these same gates in the real world:
authorization (ROE), a sufficiently confident and characterized track (you do not engage on a bare
detection), interceptor reach (a direct-ascent system sized for one regime cannot reach another),
and — once fired — an irreversible, debris-generating outcome with consequences for the entire
operating environment, not just the target. This is precisely why the engine treats kinetic effects
as the one category with `reversible=False`.

## 5. Implementation Guidance

- **A new kinetic or directed-energy effect must derive its success/kill probability from a
  declared, auditable database** (like the four-class `INTERCEPTORS` table), never an
  operator-typed number — this mirrors the same audit-driven fix applied to jam ([R115](R115-electronic-warfare-in-space-operations.md)) and engage.
- **Never relax the weapons-quality gate for a new engagement-like feature** — if a feature needs a
  lower-confidence-bar engagement type, it must say so explicitly as a new, distinctly-named
  confidence tier ([R105](R105-custody-theory.md) §4), not silently read raw detection confidence.
- **Preserve the regime-reachability check (`interceptor_max_alt_m`/`interceptor_mask_deg`) for any
  new interceptor class** — don't bypass `AccessProvider._weapon_predicate` with a parallel
  reachability rule.
- **Mark any new irreversible/debris-generating effect with the matching `reversible=False`,
  `kinetic=True` (or analogous) flags** so downstream consequence-confirm UI (the kinetic
  consequence-confirm dialog) and assessment (DOM-002) treat it with the same gravity.

## 6. Feature Mapping

FS-105 (Spacecraft Operations) is the direct consumer — any new engagement-class feature must
preserve the existing consequence-confirm UX pattern for irreversible actions.

## 7. Related Topics

[R105](R105-custody-theory.md) (the weapons-quality gate this category's defining precondition), [R101](R101-orbital-mechanics-for-operations.md) (regime as a
reachability gate), MSTR-002 (the five-D taxonomy and its one irreversible exception).
