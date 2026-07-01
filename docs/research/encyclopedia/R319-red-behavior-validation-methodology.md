# R319 — Red Behavior Validation Methodology

> **Document ID:** R319
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [R308](R308-red-teaming-methodology.md)
> **Referenced By:** —
> **Produces:** doctrinal grounding for DOM-005 (Validation Framework, ⛔ Planned) to consume when it
> defines concrete validation criteria for `redai.py` doctrine presets and any future AI-Red
> **Feature Mapping:** none yet — supplies grounding for DOM-005 and the ADR-0024 fog-of-war-parity
> future-work item; not itself a feature
> **Related Topics:** [R308](R308-red-teaming-methodology.md) (Red Teaming Methodology — the
> qualitative doctrinal-plausibility principle this topic supplies a validation *method* for),
> [R307](R307-wargaming-theory.md) (Wargaming Theory — what an exercise outcome can validly
> demonstrate, the broader context this topic's narrower Red-fidelity question sits inside),
> DOM-005 (Validation Framework, currently ⛔ Planned — the intended consumer), ADR-0024 (AI-Red
> epistemic-parity gap, tracked but unresolved)
> **Last Reviewed:** 2026-07-01
> **Primary Sources Consulted:** 0 (Tier C professional-military-journal source; see §3 note)

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Identified as **GAP-08** in the Independent Strategic Review Board report
([`docs/reviews/strategic-review-2026-07.md`](../../reviews/strategic-review-2026-07.md) Part 3
and Part 4.5's "negative training" red-team finding): [R308](R308-red-teaming-methodology.md)
already supplies the *principle* — Red must be doctrinally plausible, neither passive nor
omniscient, and structurally independent of pressure to "go easy" — but names no concrete method
for *checking* whether a given `redai.py` doctrine preset, or a future AI-Red, actually satisfies
that principle rather than merely appearing to. This is precisely the negative-training risk the
strategic review flags: an exercise run against an unvalidated Red teaches trainees confidently,
and the confidence is unearned if Red's behavior does not, in fact, resemble any real adversary's.
This topic supplies the doctrinal grounding a future validation method would draw on; it does not
itself define DOM-005's validation criteria, which remains that document's job once authorized.

## 2. Scope

Covers: what "behavioral fidelity" means as a checkable property of an adversary model, the
distinction between validating against real-world adversary action patterns versus validating
against "does this produce a fun/winnable exercise," and why these two validation targets can
diverge and even conflict. Does **not** cover: the qualitative doctrinal-plausibility principle
itself ([R308](R308-red-teaming-methodology.md), assumed here as already established), the broader
question of what a wargame's outcome can validly demonstrate about the real world
([R307](R307-wargaming-theory.md)), or DOM-005's eventual concrete validation criteria and
instrument design (out of scope for a research-tier topic; DOM-005 is a domain-framework document,
not something this skill authors).

## 3. Concepts

**Behavioral fidelity is checkable by comparing a modeled adversary's action sequence against
real, historical adversary behavior — not just by expert impression.** A structured approach
compares an adversary model's chosen actions, scenario by scenario, against documented historical
adversary decisions in analogous situations, using sequence-level comparison rather than only
end-state outcome comparison — the same distinction custody theory draws between confidence in a
single detection and confidence built from a track's history
([R105](R105-custody-theory.md)'s analog). Applied to `redai.py`, this means a doctrine preset's
validation should ask "does this preset's *sequence* of chosen actions resemble how the doctrine it
claims to represent has actually behaved historically," not only "did this preset produce a
balanced exercise."

**"Getting Red right" is treated as a named, recurring failure mode in professional wargaming
practice, not a solved problem.** The naval-professional literature has specifically named the
failure of red-cell fidelity as a recurring wargaming defect — Red played by inexperienced or
under-resourced personnel, or tuned (deliberately or not) to produce a predetermined Blue outcome,
degrades a wargame's findings regardless of how sophisticated the rest of the exercise design is
([US Naval Institute, *Proceedings*, "War Gaming Must Get Red Right," January 2017](https://www.usni.org/magazines/proceedings/2017/january/war-gaming-must-get-red-right)).
*Single source (Tier C, professional-journal) — full-page verification via WebFetch was not
completed in this session (network access to the URL was not available); the citation rests on
the article's title, venue, and publication date as retrieved via search index, corroborated by the
independent-but-consistent framing already documented in [R308](R308-red-teaming-methodology.md)'s
Zenko (2015) and UK MOD Handbook (2021) sources on the same underlying failure mode. Flagged per the
methodology's §3 single-source rule pending a future session's full verification pass.* This is a
Tier-C corroborating source for a claim [R308](R308-red-teaming-methodology.md)'s Tier-A/B sources
already substantively establish — it is cited here specifically because it is the professional
wargaming-practice literature's own naming of "getting Red right" as a recurring, checkable failure
category, which is what motivates treating validation as a distinct methodological step from the
principle itself.

**Fidelity validation and "produces a winnable/fun exercise" are different, sometimes conflicting,
validation targets.** [R308](R308-red-teaming-methodology.md) §5 already states that a preset must
be evaluated against doctrinal plausibility, "not against 'does it let Blue win the intended way'"
— this topic sharpens that into a validation-methodology consequence: a preset tuned to pass a
playability check (does the exercise resolve in a reasonable time, does Blue have a viable path)
can still fail a fidelity check (does this resemble real adversary behavior), and the two checks
require different evidence. A playability check can be run by playing the vignette; a fidelity
check requires external comparison against real-world adversary behavior patterns, which is exactly
what DOM-005's "did we build the right model" framing (vs. verification's "did we build the model
right") already distinguishes at the assessment-instrument level — the same distinction applies to
Red as an adversary model, not only to Blue-facing assessment rubrics.

**Epistemic parity is a fidelity precondition, not a separate concern.** A Red model reading ground
truth instead of a fog-of-war-filtered view (the tracked gap in ADR-0024 — confirmed empirically:
`RedDoctrine._blue_satellites()`, `_red_assets()`, and `_first_vulnerable()` currently read
`self.mgr.world` directly rather than a `CellView`) cannot be behaviorally validated against real
adversary doctrine in the first place, because a real adversary never has that information either —
any fidelity comparison run against the current implementation would be comparing an
information-privileged decision-maker to a historical record of information-constrained ones,
an apples-to-oranges comparison regardless of how sophisticated the comparison method is. This is
why ADR-0024's fog-of-war-parity item is not merely a realism nice-to-have but a **precondition**
for any future validation methodology DOM-005 might define.

### Sources

- *US Naval Institute, Proceedings, "War Gaming Must Get Red Right"* (January 2017) — [live](https://www.usni.org/magazines/proceedings/2017/january/war-gaming-must-get-red-right)
  · [snapshot](https://web.archive.org/web/2026/https://www.usni.org/magazines/proceedings/2017/january/war-gaming-must-get-red-right)
  · accessed 2026-07-01. *Single source, Tier C — see inline flag above.*

## 4. Operational Context

Professional wargaming institutions that rely on exercise findings for real decisions (RAND, the
naval wargaming tradition, allied defense colleges) treat red-cell quality as a named risk to the
validity of the entire exercise's conclusions, not a secondary staffing detail — because a finding
generated against an unrealistic adversary is not merely less useful, it can be actively misleading,
producing false confidence in a friendly posture that would not actually hold against a real
opponent. This is the precise mechanism behind the strategic review's "negative training" concern:
a PME trainee who defeats a Red model that does not resemble any real adversary's behavior may
leave the exercise with confidence that has not been earned.

## 5. Implementation Guidance

- **A future DOM-005 (Validation Framework) should treat Red-behavior fidelity as its own named
  validation target, distinct from assessment-instrument validity** (DOM-005's current scope, per
  its own §2, is framed around fidelity claims and assessment-instrument validity generally; Red
  fidelity is a specific, high-priority instance of the first category this topic's grounding
  should feed directly into when DOM-005 is authored).
- **Any concrete fidelity check should compare `redai.py` preset action sequences against
  documented historical adversary behavior patterns** (already available in this corpus:
  `research/02-doctrine-non-western.md`'s PRC/Russia-class doctrine corpus), not only against
  whether an exercise "felt" balanced when played.
- **Do not treat a playability/balance check as a substitute for a fidelity check** — per §3, they
  are different validation targets that can diverge; a preset design process that only iterates
  against playability risks converging on a Red that is fun to play against but doctrinally
  unrepresentative, which is the negative-training failure mode this topic exists to name.
- **Any future AI-Red epistemic-parity fix (ADR-0024, `FUTURE-WORK.md` §1) should be sequenced
  before, or explicitly scoped alongside, any fidelity-validation effort** — per §3's precondition
  argument, validating a ground-truth-reading Red's fidelity against real (information-constrained)
  adversary behavior is not a meaningful comparison regardless of method sophistication.

## 6. Feature Mapping

None yet — this topic grounds DOM-005 (currently ⛔ Planned) and the ADR-0024 future-work item; it
does not itself authorize either.

## 7. Related Topics

[R308](R308-red-teaming-methodology.md) (Red Teaming Methodology — the qualitative principle this
topic supplies a validation method for), [R307](R307-wargaming-theory.md) (Wargaming Theory — the
broader validity context), DOM-005 (Validation Framework, the intended consumer), ADR-0024 (the
epistemic-parity precondition this topic identifies).
