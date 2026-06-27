# R310 — Effects-Based Operations

> **Document ID:** R310
> **Version:** 1.1
> **Status:** ✅ Done
> **Dependencies:** [R309](R309-center-of-gravity-analysis.md)
> **Referenced By:** [R306](R306-operational-assessment.md)
> **Produces:** the cascading-effects vocabulary [R306](R306-operational-assessment.md) (Operational Assessment)'s MOE concept depends on
> **Feature Mapping:** vignette authoring, FS-201 (Competency Assessment, forward-looking)
> **Related Topics:** [R309](R309-center-of-gravity-analysis.md) (Center of Gravity Analysis), [R306](R306-operational-assessment.md) (Operational Assessment), the five-D's
> taxonomy ([`research/03-counterspace-taxonomy.md`](../03-counterspace-taxonomy.md), MSTR-002 §2 invariant 3)
> **Last Reviewed:** 2026-06-27
> **Primary Sources Consulted:** 1

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

The simulator's five-D's effect taxonomy (deceive/disrupt/deny/degrade/destroy) already implies an
effects-based way of thinking — choosing an effect category is choosing *what operational effect* is
sought, not just which weapon/tool is used. This topic gives the implementer the formal EBO
vocabulary so that mapping (tool → direct effect → cascading operational effect) is made explicit
rather than collapsed into "the effect category is the effect," and gives the implementer the
real-world cautionary history behind that vocabulary.

## 2. Scope

Covers: the effects-based planning logic (effect-backward vs. tool-forward), the direct/indirect/
systemic effect hierarchy, and the documented historical critique of EBO's predictive over-claims.
Does **not** cover: identifying *which* asset/capability is the target of an effect (that is
[R309](R309-center-of-gravity-analysis.md), Center of Gravity Analysis) or measuring whether an
effect was actually achieved (that is [R306](R306-operational-assessment.md), Operational
Assessment).

## 3. Concepts

**Effects-based operations: plan from the desired effect backward to the action, not from the
available tool forward.** EBO doctrine, as it rose to prominence in post-Cold War joint planning,
emphasizes starting from "what operational outcome do we want to cause" and selecting the action
that best produces it, rather than starting from "what capabilities do we have" and using whichever
is available — directly relevant to vignette design: a well-designed objective should specify the
*effect* sought (deny Red's SDA picture of asset X) and let the operator choose among capabilities
(jam, cyber, deception) that could produce it, rather than prescribing a specific tool.

**Direct, indirect (cascading), and systemic effects.** A direct effect is the immediate, intended
consequence of an action (a jam denies a specific sensor pass); an indirect/cascading effect is a
downstream consequence the direct effect causes (denying that sensor pass delays Red's custody
build-up, which delays a Red engagement decision, [R208](R208-ooda-loops.md)); a systemic effect is the aggregate
consequence across the whole operational system (Red's overall SDA confidence degrades across
multiple denied passes). The engine currently models direct effects explicitly (the effect resolver)
and indirect/systemic effects only implicitly, through their downstream mechanical consequences
([R306](R306-operational-assessment.md)'s MOE/MOP distinction is the assessment-side version of this same gap).

**The EBO critique: cascading effects are hard to predict and can be over-claimed.** General James
N. Mattis, then commander of US Joint Forces Command, formally directed in his memorandum
["USJFCOM Commander's Guidance for Effects-based Operations"](https://press.armywarcollege.edu/parameters/vol38/iss3/10/)
(2008-08-14) that USJFCOM would no longer use, sponsor, or export the terms and concepts related to
EBO in training, doctrine development, and Joint Professional Military Education support, arguing
that EBO's premise — that planners could reliably predict second- and third-order effects in complex
adversarial systems — had proven unsound in practice. This is a directly relevant, dated, documented
caution for vignette design and for any future assessment feature: don't claim a vignette's
objective "proves" a specific cascading effect occurred just because the direct effect (the
objective flip) succeeded; [R306](R306-operational-assessment.md)'s MOP/MOE distinction is the
concrete safeguard against this over-claim.

### Sources

- *Gen. James N. Mattis, "USJFCOM Commander's Guidance for Effects-based Operations"* (memorandum,
  2008-08-14; reprinted in *Parameters*, US Army War College Press, vol. 38, no. 3) — [live](https://press.armywarcollege.edu/parameters/vol38/iss3/10/)
  · [snapshot](https://web.archive.org/web/2026/https://press.armywarcollege.edu/parameters/vol38/iss3/10/)
  · accessed 2026-06-27.

## 4. Operational Context

EBO rose to prominence in post-Cold War joint doctrine as an organizing framework for linking
tactical actions to strategic outcomes, then was substantially critiqued and formally discontinued as
USJFCOM-sponsored terminology by the 2008-08-14 Mattis memo for overpromising predictability of
cascading effects in complex systems — both the appeal and the critique are directly relevant: this
simulator can usefully frame vignette objectives around desired effects, while explicitly avoiding
the predictive over-claim the real doctrine eventually walked back.

## 5. Implementation Guidance

- **A vignette objective should be authored from the desired effect, with the tool left to the
  operator's choice where doctrinally reasonable** — an objective phrased as "deny Red SDA on asset
  X for window Y" (effect-based) gives the operator a meaningful tradecraft choice; one phrased as
  "use jam.py on asset X" (tool-prescriptive) removes that choice and is usually a design smell unless
  the vignette is deliberately teaching a specific tool's mechanics (e.g. an onboarding vignette).
- **Don't let any future assessment feature claim a flipped objective demonstrates a cascading/
  systemic effect beyond what was directly measured** — per the 2008 EBO critique, report only the
  direct, measured effect ([R306](R306-operational-assessment.md)'s MOP/MOE framing) and explicitly
  flag any inferred cascading claim as inferred, not measured.
- **If a future feature models genuine cascading consequences (e.g. Red's subsequent custody
  picture degrading after a sustained jam campaign), implement it as an explicit, documented state
  effect in the engine** (a real mechanical link), not as a narrative assumption layered onto the
  AAR — an unimplemented "implied" cascading effect that's only described in prose risks exactly the
  over-claim this topic warns about.

## 6. Feature Mapping

Vignette authoring is the direct consumer; FS-201 (Competency Assessment) inherits the MOP/MOE
caution for any future effectiveness-scoring dimension.

## 7. Related Topics

[R309](R309-center-of-gravity-analysis.md) (Center of Gravity Analysis, the targeting input to EBO), [R306](R306-operational-assessment.md) (Operational Assessment, the
measurement-side application of the MOP/MOE distinction this topic motivates), the five-D's taxonomy
([`research/03-counterspace-taxonomy.md`](../03-counterspace-taxonomy.md)).
