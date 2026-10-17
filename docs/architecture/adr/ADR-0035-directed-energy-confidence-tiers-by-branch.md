# ADR-0035 — Directed-energy custody requirement follows its reversibility branch

[↑ ADR index](INDEX.md)

- **Decision ID:** ADR-0035
- **Title:** DE-dazzle requires no custody precondition (like `jam`); DE-damage requires the
  weapons-quality gate (like `engage`) — no new confidence tier is introduced
- **Status:** Accepted

## Context

`FS-105` v1.1's Open Question `BL-0089` asked two related questions: (1) does a directed-energy
(DE) order need a new, lower-than-weapons-quality custody confidence tier, and (2) does a
DE-damage effect resolving `reversible=False` create a second irreversible category alongside
kinetic, in tension with the "kinetic effects are the one irreversible category" framing `R117`
v1.0 attributed to `MSTR-002`.

**On (2): that attribution does not hold up.** Direct read of `docs/master/MSTR-002-architecture-
principles.md` confirms it makes no statement about reversibility or kinetic effects at all — the
"most effects are reversible... not kinetic" framing is `CLAUDE.md`'s own summary prose, not an
`MSTR-002` principle, and `CLAUDE.md` already says "most," not "all" or "the one" — it does not
foreclose a second, narrower irreversible sub-case. There is no formal principle to amend. `R117`
v1.1's own citation of "MSTR-002" for this claim (carried forward from v1.0) is corrected by this
ADR to cite `CLAUDE.md` instead, where the claim actually lives.

**On (1): `R105` §5 (Implementation Guidance) already anticipates exactly this question** — "any
new effect category that requires custody as a precondition must specify which confidence tier it
requires (mere detection vs. weapons-quality vs. something in between) explicitly in its own spec."
Two tiers already exist as *shipped, working precedent*, not as a menu to choose a new one from:
`order.action == "jam"` has **no** custody/track precondition at all in `OrderSystem._validate`
(only a valid access window); `order.action == "engage"` requires the full weapons-quality gate
(`track.is_weapons_quality(...)`, `R105` §3). `R117` v1.1 §3.2/§4.2 characterizes DE-dazzle as
structurally the same kind of effect as jam (reversible, deny/disrupt, a denial of sensor/link
function) and DE-damage as structurally the same kind of effect as kinetic engagement
(irreversible, degrade/destroy, consequence-confirm-gated).

## Decision

DE's custody precondition follows its reversibility branch, reusing the two existing tiers rather
than introducing a third:

- A **DE-dazzle** order (resolves `reversible=True`) requires **no custody precondition** —
  identical to `jam`'s existing `_validate` behavior. An accessible target (via `weapon_engagement`,
  `ADR-0034`) may be dazzled regardless of track confidence, matching dazzle's role as a reversible,
  low-consequence denial effect.
- A **DE-damage** order (resolves `reversible=False`) requires the **same weapons-quality gate** as
  kinetic engagement (`track.is_weapons_quality(...)`) — identical treatment for identical
  consequence-severity (irreversible, consequence-confirm-gated).
- **No new confidence tier is introduced.** `R105`'s "something in between" option is explicitly
  not exercised: DE does not need a novel construct, only the correct existing tier per branch.
- `CLAUDE.md`'s "most effects are reversible... not kinetic" framing needs no amendment (see
  Context); `R117`'s citation of this claim is corrected to `CLAUDE.md`, not `MSTR-002`.

## Alternatives Considered

- **A single, uniform DE custody rule (e.g. always weapons-quality)** — rejected. This would
  over-gate DE-dazzle, treating a reversible denial effect as gravely as an irreversible strike,
  contrary to `R117` v1.1's own reversibility-based escalation-control framing (§4.2: DE's
  strategic value *is* letting an actor act below the irreversibility threshold).
  Under-gating DE-damage (e.g. no track requirement) was not seriously considered — it is the one
  branch structurally identical to kinetic, and kinetic's weapons-quality bar is the "single
  highest bar in the engine" (`R117` §3.1) for a specific, still-applicable reason (an irreversible,
  debris/damage-generating action should not fire on a bare detection).
- **A genuinely new, distinctly-named intermediate tier** (per `R105` §5's third option) —
  rejected as unnecessary. Both DE branches already have a structurally matching existing
  precedent (jam's none-required tier; engage's weapons-quality tier); inventing a third tier
  would add complexity `R105` itself only calls for "if" no existing tier fits.

## Rationale

Reusing existing, shipped precedent per branch is the minimal-surgery answer consistent with
`R105`'s own decision rule, and correctly encodes DE's real-world escalation-control value (a
reversible dazzle carries less weight than a kinetic strike, and should not be gated as heavily).

## Consequences

- The DE Implementation Package's `_validate` addition for the `directed_energy`-producing order
  mirrors `jam`'s custody-free path for the dazzle branch and `engage`'s weapons-quality check for
  the damage branch — no `custody.py`/`Track` change is required for either branch.
- `R117`'s "Related Topics" and Risks citations of "MSTR-002" for the reversibility-count framing
  should be corrected to `CLAUDE.md` the next time `R117` is touched (a small citation-accuracy
  finding, not a blocking one — filed to the backlog alongside this ADR).
- `FS-105` v1.1's `BL-0089` Open Question is closed by this decision.

## Related

`R105` (Custody Theory, §5 Implementation Guidance — the confidence-tier decision rule this ADR
exercises); `R117` v1.1 §3.2/§4.2 (`docs/research/encyclopedia/R117-directed-energy-and-kinetic-effects.md`);
`FS-105` v1.1 (`docs/features/FS-105-spacecraft-operations.md`, Open Questions/Risks); `ADR-0034`
(the companion decision on DE's access channel); `CLAUDE.md` (the actual source of the "most
effects are reversible... not kinetic" framing); backlog `BL-0066`, `BL-0089`.
