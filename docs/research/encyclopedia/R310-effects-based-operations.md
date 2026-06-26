# R310 — Effects-Based Operations

> **Document ID:** R310
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** R309
> **Referenced By:** R306
> **Produces:** the cascading-effects vocabulary R306 (Operational Assessment)'s MOE concept depends on
> **Feature Mapping:** vignette authoring, FS-201 (Competency Assessment, forward-looking)
> **Related Topics:** R309 (Center of Gravity Analysis), R306 (Operational Assessment), the five-D's
> taxonomy (`research/03-counterspace-taxonomy.md`, MSTR-002 §2 invariant 3)

[↑ Tier R300 index](R300-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

The simulator's five-D's effect taxonomy (deceive/disrupt/deny/degrade/destroy) already implies an
effects-based way of thinking — choosing an effect category is choosing *what operational effect* is
sought, not just which weapon/tool is used. This topic gives the implementer the formal EBO
vocabulary so that mapping (tool → direct effect → cascading operational effect) is made explicit
rather than collapsed into "the effect category is the effect."

## 2. Concepts

**Effects-based operations: plan from the desired effect backward to the action, not from the
available tool forward.** EBO doctrine emphasizes starting from "what operational outcome do we want
to cause" and selecting the action that best produces it, rather than starting from "what
capabilities do we have" and using whichever is available — directly relevant to vignette design:
a well-designed objective should specify the *effect* sought (deny Red's SDA picture of asset X) and
let the operator choose among capabilities (jam, cyber, deception) that could produce it, rather than
prescribing a specific tool.

**Direct, indirect (cascading), and systemic effects.** A direct effect is the immediate, intended
consequence of an action (a jam denies a specific sensor pass); an indirect/cascading effect is a
downstream consequence the direct effect causes (denying that sensor pass delays Red's custody
build-up, which delays a Red engagement decision, R208); a systemic effect is the aggregate
consequence across the whole operational system (Red's overall SDA confidence degrades across
multiple denied passes). The engine currently models direct effects explicitly (the effect resolver)
and indirect/systemic effects only implicitly, through their downstream mechanical consequences
(R306's MOE/MOP distinction is the assessment-side version of this same gap).

**The EBO critique: cascading effects are hard to predict and can be over-claimed.** EBO doctrine has
been substantially critiqued in real military practice for overestimating planners' ability to
predict second- and third-order effects in complex adversarial systems — a caution directly relevant
to vignette design and to any future assessment feature: don't claim a vignette's objective "proves"
a specific cascading effect occurred just because the direct effect (the objective flip) succeeded;
R306's MOP/MOE distinction is the concrete safeguard against this over-claim.

## 3. Operational Context

EBO rose to prominence in post-Cold War joint doctrine as an organizing framework for linking
tactical actions to strategic outcomes, was then substantially critiqued (notably by USJFCOM in the
2000s) for overpromising predictability of cascading effects in complex systems — both the appeal and
the critique are directly relevant: this simulator can usefully frame vignette objectives around
desired effects, while explicitly avoiding the predictive over-claim the real doctrine eventually
walked back.

## 4. Implementation Guidance

- **A vignette objective should be authored from the desired effect, with the tool left to the
  operator's choice where doctrinally reasonable** — an objective phrased as "deny Red SDA on asset
  X for window Y" (effect-based) gives the operator a meaningful tradecraft choice; one phrased as
  "use jam.py on asset X" (tool-prescriptive) removes that choice and is usually a design smell unless
  the vignette is deliberately teaching a specific tool's mechanics (e.g. an onboarding vignette).
- **Don't let any future assessment feature claim a flipped objective demonstrates a cascading/
  systemic effect beyond what was directly measured** — per the EBO critique, report only the direct,
  measured effect (R306's MOP/MOE framing) and explicitly flag any inferred cascading claim as
  inferred, not measured.
- **If a future feature models genuine cascading consequences (e.g. Red's subsequent custody
  picture degrading after a sustained jam campaign), implement it as an explicit, documented state
  effect in the engine** (a real mechanical link), not as a narrative assumption layered onto the
  AAR — an unimplemented "implied" cascading effect that's only described in prose risks exactly the
  over-claim this topic warns about.

## 5. Feature Mapping

Vignette authoring is the direct consumer; FS-201 (Competency Assessment) inherits the MOP/MOE
caution for any future effectiveness-scoring dimension.

## 6. Related Topics

R309 (Center of Gravity Analysis, the targeting input to EBO), R306 (Operational Assessment, the
measurement-side application of the MOP/MOE distinction this topic motivates), the five-D's taxonomy
(`research/03-counterspace-taxonomy.md`).
