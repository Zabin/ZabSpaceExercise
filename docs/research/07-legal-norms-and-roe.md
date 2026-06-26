---
last_reviewed: 2026-06-12
primary_sources_consulted: 28
status: stable
---

# Legal, Normative & Rules-of-Engagement Frame

[← Research index](INDEX.md) · [↑ Docs index](../INDEX.md) · methodology: [`10-sources-and-methodology.md`](10-sources-and-methodology.md)

The simulator's effect resolver does not enforce international space law — it *prices*
it. Every order a cell issues is permitted (subject to the engine's window-gating and
physics-feasibility checks), and the legal-and-normative substrate appears as a *cost*
in the political-consequence side effect on every irreversible kinetic outcome and as
the ROE-flag defaults on every vignette's parameters block. This file is the spine for
that substrate: the three foundational treaties that form the peacetime floor (§1),
the LOAC layer that applies in armed conflict (§2), the most-recent and most
operationally load-bearing norm — the 2022 destructive-DA-ASAT moratorium and the
follow-on UNGA Resolution 77/41 (§3), the norms-still-under-negotiation track (§4),
and the engine encoding pattern that turns all four layers into vignette parameters
and political-cost scoring (§5).

This file is the canonical reference for every `roe_kinetic_authorized` /
`roe_cyber_authorized` flag in the vignette library, every `intro_brief.roe_note`
text shown to operators at session start, and the calibration of every
`political_consequence` severity in the engine's effect resolver.

---

## 1. The treaty floor (OST 1967, Registration 1976, Liability 1972)

Three United Nations treaties form the legal substrate every modern space-law
analysis stands on, and the substrate the simulator's ROE defaults rest on:
the **Outer Space Treaty (OST, 1967)**, the **Convention on International
Liability for Damage Caused by Space Objects (Liability Convention, 1972)**,
and the **Convention on Registration of Objects Launched into Outer Space
(Registration Convention, 1976)**. The OST is the constitution; the Liability
and Registration Conventions operationalise the two articles of the OST that
most directly bind state behaviour around damage (Art. VII) and identification
of space objects (Art. VIII). All three were negotiated under the auspices of
the UN Committee on the Peaceful Uses of Outer Space (COPUOS) and are
maintained by the UN Office for Outer Space Affairs (UNOOSA). The simulator's
`roe_kinetic_authorized` / `roe_cyber_authorized` flags and the
`political_consequence` side effect in [`engine/effects.py`](../../spacesim/engine/effects.py)
encode the *cost* of crossing these instruments rather than any of them as a
hard veto — by design, a Red Cell can choose to violate the floor, but pays
for it in the scoring.

### Outer Space Treaty (1967)

*Treaty on Principles Governing the Activities of States in the Exploration
and Use of Outer Space, Including the Moon and Other Celestial Bodies*, opened
for signature 27 January 1967 and entered into force **10 October 1967**, with
**118 States Parties** as of October 2025 ([UNOOSA treaty page](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/outerspacetreaty.html);
[Arms Control Association *Outer Space Treaty at a Glance*](https://www.armscontrol.org/factsheets/outer-space-treaty-glance)).
It is the most widely-ratified space-law instrument and the only one whose
near-universal adherence makes its core obligations plausibly *customary*
international law binding even non-parties. The OST emerged from a deliberate
two-step UNGA process: **Resolution 1721 (XVI), 20 December 1961** —
"International Co-Operation in the Peaceful Uses of Outer Space" — laid down
the proto-principles (international law applies in space; no national
appropriation), and **Resolution 1962 (XVIII), 13 December 1963** — the
"Declaration of Legal Principles" — fixed the substantive frame that the 1967
treaty then codified ([UNOOSA Resolution 1721 (XVI)](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/resolutions/res_16_1721.html)).

Four articles bear directly on the simulator's effect resolver and ROE gates:

- **Article IV** — no nuclear weapons or other weapons of mass destruction
  may be placed in orbit, installed on celestial bodies, or stationed in outer
  space "in any other manner," and the Moon and other celestial bodies are to
  be used "exclusively for peaceful purposes"
  ([UNOOSA Outer Space Treaty](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/outerspacetreaty.html)).
  This is the article that makes the v1-excluded orbital nuclear ASAT a treaty
  violation, not merely a balancing problem (see
  [`03-counterspace-taxonomy.md`](03-counterspace-taxonomy.md) §8 out-of-scope)
  and the article the engine-context audit cites directly
  ([`docs/AUDIT-2026-06-COMMANDS.md`](../AUDIT-2026-06-COMMANDS.md) §M2).
- **Article VI** — States bear *international responsibility* for "national
  activities in outer space … whether such activities are carried on by
  governmental agencies or by non-governmental entities," with continuing
  authorisation-and-supervision duties
  ([UNOOSA Outer Space Treaty](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/outerspacetreaty.html)).
  A commercial operator's bird is the launching State's legal problem — which
  is why the simulator treats a Red attack on a Western commercial SATCOM
  asset (Vignette 2 / 6) as a state-on-state act for political-cost scoring.
- **Article VII** — the launching State is *internationally liable* for
  damage caused by its space object to another State Party "or to its natural
  or juridical persons" on Earth, in air space, or in outer space
  ([UNOOSA Outer Space Treaty](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/outerspacetreaty.html)).
  The Liability Convention (below) is Article VII's operational machinery.
- **Article IX** — States shall conduct activities "with due regard to the
  corresponding interests" of other States and shall undertake consultations
  where an activity may cause "potentially harmful interference"
  ([UNOOSA Outer Space Treaty](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/outerspacetreaty.html)).
  The norms case against persistent close-approach RPO and sustained EW often
  rests here even when the act is below an armed-conflict threshold.

### Liability Convention (1972)

*Convention on International Liability for Damage Caused by Space Objects*,
opened for signature 29 March 1972 and entered into force **1 September 1972**
([UNOOSA treaty page](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/liability-convention.html)).
It elaborates OST Article VII into a two-regime liability scheme: **absolute**
liability for damage caused by a space object on the surface of the Earth or
to aircraft in flight (Article II), and **fault** liability for damage caused
elsewhere — i.e., in space, to another space object (Article III). Claims are
state-to-state only; an injured private party must have its government
present the claim ([UNOOSA treaty page](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/liability-convention.html)).
The Cosmos-1408 debris cloud (2021-11-15) and the historical FY-1C cloud
(2007-01-11) sit squarely in the Article III "fault" regime — every ISS dodge
or commercial-bird conjunction caused by tracked fragments from those events
is a potential fault-liability claim and one of the doctrinal reasons the
2022 destructive-DA-ASAT moratorium (§3 below) emerged.

### Registration Convention (1976)

*Convention on Registration of Objects Launched into Outer Space*, opened for
signature 14 January 1975 and entered into force **15 September 1976**, with
**78 States Parties** as of January 2026 ([UNOOSA treaty page](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/registration-convention.html)).
States Parties maintain a national registry and furnish the UN Secretary-General
with the launching State, an appropriate designator or registration number,
date and territory or location of launch, basic orbital parameters (nodal
period, inclination, apogee, perigee), and general function of the space
object ([UNOOSA treaty page](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/registration-convention.html)).
The Convention expanded the earlier voluntary UN Register established by
Resolution 1721B (XVI) of December 1961. Its operational consequence for the
simulator is the *public-record* assumption: every catalogued space object has
an attributable launching State, which is what makes the engine's
`attribution=overt` default for kinetic acts (and the SDA cross-cueing in
[`engine/ssn.py`](../../spacesim/engine/ssn.py)) doctrinally realistic — there
is no "ghost satellite" in the floor regime.

---

The three treaties together set the *peacetime* substrate the simulator's ROE
defaults stand on. The engine in [`session/manager.py`](../../spacesim/session/manager.py)
loads each vignette's `roe_kinetic_authorized` and `roe_cyber_authorized`
flags from `vignette.parameters` — most vignettes default both to *false*,
which is the doctrinally-correct reading of the floor: a kinetic ASAT engages
Article IX "due regard," potentially Article VII liability, and (since 2022)
the destructive-DA-ASAT moratorium covered in §3; a cyber action implicates
Article VI state responsibility for non-governmental effects. When a cell
issues an order that the engine resolves as `destroy` with `kinetic=True`,
[`engine/effects.py`](../../spacesim/engine/effects.py) emits a
`political_consequence` side effect whose severity is sourced to this floor
— the act is *permitted* (the engine does not veto), but the political-cost
score reflects the treaty-and-norms penalty the actor incurred. Forward-link:
the 2022 moratorium (§3 below) is the most recent layer atop this floor and
is the live political-cost signal in vignettes 5 and 8.

Used by: [`session/manager.py`](../../spacesim/session/manager.py) (the
`roe_kinetic_authorized` / `roe_cyber_authorized` flags loaded from vignette
parameters); [`engine/effects.py:political_consequence`](../../spacesim/engine/effects.py)
(the escalation-cost side effect on irreversible kinetic outcomes);
[`content/vignettes/*.yaml:parameters`](../../spacesim/content/vignettes/)
(per-vignette ROE default values, with most floors set to false).

### Sources

- *UNOOSA, "Treaty on Principles Governing the Activities of States in the
  Exploration and Use of Outer Space, Including the Moon and Other Celestial
  Bodies"* (the Outer Space Treaty, 1967) — [live](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/outerspacetreaty.html)
  · [snapshot](https://web.archive.org/web/2026*/https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/outerspacetreaty.html)
  · accessed 2026-06-12.
- *UNOOSA, "Convention on International Liability for Damage Caused by Space
  Objects"* (Liability Convention, 1972) — [live](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/liability-convention.html)
  · [snapshot](https://web.archive.org/web/2026*/https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/liability-convention.html)
  · accessed 2026-06-12.
- *UNOOSA, "Convention on Registration of Objects Launched into Outer Space"*
  (Registration Convention, 1976) — [live](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/registration-convention.html)
  · [snapshot](https://web.archive.org/web/2026*/https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/registration-convention.html)
  · accessed 2026-06-12.
- *UNOOSA, "General Assembly Resolution 1721 (XVI)"* (20 December 1961,
  International Co-Operation in the Peaceful Uses of Outer Space) —
  [live](https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/resolutions/res_16_1721.html)
  · [snapshot](https://web.archive.org/web/2026*/https://www.unoosa.org/oosa/en/ourwork/spacelaw/treaties/resolutions/res_16_1721.html)
  · accessed 2026-06-12.
- *Arms Control Association, "The Outer Space Treaty at a Glance"* —
  [live](https://www.armscontrol.org/factsheets/outer-space-treaty-glance)
  · [snapshot](https://web.archive.org/web/2026*/https://www.armscontrol.org/factsheets/outer-space-treaty-glance)
  · accessed 2026-06-12.

---

## 2. The law of armed conflict (LOAC) applied to space

§1's three treaties (OST 1967, Liability 1972, Registration 1976) describe the
*peacetime* substrate — they are **jus ad bellum** in flavour: when and how a
State may use force at all, and what obligations it carries while operating in
the space environment. Once an armed conflict has crossed the use-of-force
threshold and the parties are inside an armed-conflict regime, a different and
much older body of law takes over: the **law of armed conflict (LOAC)**, also
called **international humanitarian law (IHL)** or **jus in bello**. LOAC
governs *how* the fight is conducted — what may be targeted, what care must be
taken, what suffering is forbidden — and it applies to a counterspace effect
delivered in armed conflict the same way it applies to any other military
operation
([ICRC, "What is international humanitarian law?"](https://www.icrc.org/en/document/what-international-humanitarian-law)).
The simulator's `roe_kinetic_authorized` / `roe_cyber_authorized` flags model the
peacetime floor; the IHL principles in this section model the *additional*
constraints that bite once the vignette is set in armed conflict, and they shape
the `escalation_weight` field on every [`EffectInstance`](../../spacesim/engine/effects.py).

### The four IHL principles in counterspace targeting

IHL is built on four cardinal principles, codified in the 1949 Geneva
Conventions and their 1977 Additional Protocols and treated as customary
international law binding on every State regardless of ratification
([ICRC Customary IHL database](https://ihl-databases.icrc.org/en/customary-ihl)):

- **Distinction.** Parties must at all times distinguish between combatants /
  military objectives and civilians / civilian objects; only the former may be
  attacked (AP I Art. 48; CIHL Rules 1, 7).
- **Proportionality.** An attack on a military objective is unlawful if the
  incidental civilian harm is excessive in relation to the concrete and direct
  military advantage anticipated (AP I Art. 51(5)(b); CIHL Rule 14).
- **Precautions in attack.** A party planning an attack must take all feasible
  precautions to verify the target, choose means and methods to minimize
  collateral harm, and cancel or suspend if proportionality fails (AP I Art.
  57; CIHL Rules 15-21).
- **Military necessity.** Force may be used only to the extent required to
  achieve a legitimate military aim; gratuitous destruction is forbidden (Hague
  IV / Lieber Code lineage; CIHL Rule 50 on protected property).

Each principle bites distinctively in space. *Distinction* drives the dual-use
problem below — a satellite that simultaneously carries military and civilian
traffic is, in IHL terms, ambiguously categorized. *Proportionality* governs
the kinetic-vs-reversible choice: a destructive DA-ASAT strike whose debris
cloud knocks out civilian SATCOM and weather services for years rarely passes
a proportionality test against a single tactical target, which is the
doctrinal lever behind the engine's high `escalation_weight` on destructive
outcomes (see [`03-counterspace-taxonomy.md`](../../03-counterspace-taxonomy.md) §1).
*Precautions* drive the SDA / track-quality gate the engine encodes in
[`engine/custody.py`](../../spacesim/engine/custody.py) — a weapons-quality
track is the IHL evidentiary floor for "verify the target." *Military
necessity* frames the reversible-first ladder: if `disrupt` achieves the
military aim, `destroy` is doctrinally hard to justify.

### The three manual projects — Tallinn, Woomera, MILAMOS

The principles above are settled, but their *application* to novel domains is
not — which is why the international-law community has, over the past decade,
produced three parallel **non-binding expert manuals** that work out what IHL
means in cyberspace and outer space:

- **Tallinn Manual 2.0 on the International Law Applicable to Cyber Operations**
  (Cambridge University Press, **February 2017**) — produced under the
  auspices of the NATO Cooperative Cyber Defence Centre of Excellence (CCDCOE)
  by an international group of experts. Tallinn 2.0 extends the 2013 first
  edition (which covered cyber operations *during* armed conflict) to
  peacetime cyber operations and applies general international law and IHL to
  the full cyber-conflict spectrum
  ([CCDCOE Tallinn Manual page](https://ccdcoe.org/research/tallinn-manual/);
  [Cambridge University Press](https://www.cambridge.org/core/books/tallinn-manual-20-on-the-international-law-applicable-to-cyber-operations/E4FFD83EA790D7C4C3C28FC9CA2FB6C9)).
- **Woomera Manual on the International Law of Military Space Operations**
  — a draft expert manual led from the University of Adelaide in partnership
  with the University of Exeter, the University of Nebraska, and UNSW
  Canberra; launched in **2018** and still in draft as of mid-2026
  ([Woomera Manual project page](https://law.adelaide.edu.au/woomera)).
  Covers both peacetime and armed-conflict regimes for military space
  operations.
- **MILAMOS Manual on International Law Applicable to Military Uses of Outer
  Space** — the McGill / University of Adelaide companion project (Centre for
  Research in Air and Space Law), launched **2016** and producing a rules-based
  restatement of the peacetime and armed-conflict law applicable to military
  uses of outer space
  ([McGill MILAMOS project page](https://www.mcgill.ca/milamos/)).

The community settled on *three* manuals rather than one because each project
takes a different lane: Tallinn 2.0 is cyber-first (and bleeds into space only
where cyber means are used against space systems — the Viasat case below);
Woomera frames itself as the *military-space* operator's manual, with a
practitioner-facing orientation; MILAMOS frames itself as the *international
lawyer's* restatement, with a heavier emphasis on the peacetime regime and
non-conflict thresholds. None of the three is binding; all three are
*persuasive* — they cite each other, and States increasingly cite them in
official position papers.

### The dual-use targeting problem

The hardest LOAC question in counterspace is **dual-use targeting**: what to do
when a space system carries both military and civilian traffic on the same
hardware. The canonical hard case is **Viasat KA-SAT, 24 February 2022** —
the GRU-attributed AcidRain wiper attack pushed ~tens of thousands of consumer
modems offline at the opening hour of Russia's full-scale invasion of Ukraine,
denying tactical SATCOM to Ukrainian command posts *and* knocking ~5,800
Enercon wind turbines in Germany off remote telemetry, plus thousands of
European civilian subscribers ([CCDCOE Cyber Law Toolkit, Viasat KA-SAT attack
(2022)](https://cyberlaw.ccdcoe.org/wiki/Viasat_KA-SAT_attack_(2022))). The
attack illustrates every IHL pressure-point at once: distinction (a single
modem network served military and civilian users intermixed), proportionality
(spillover into Germany), precautions (did the attacker verify the civilian
footprint?), and necessity (was a *wiper* required, or would a temporary deny
have sufficed?). GNSS is the other canonical case: the GPS, GLONASS, BeiDou,
and Galileo constellations are core military systems whose signals also
underwrite global civilian aviation, banking timing, and emergency services,
making any kinetic or persistent denial attack a distinction-and-proportionality
problem before it is a tactical one.

### How the engine encodes it

The engine's reading of LOAC-in-space is the one the manual projects converge
on: *contested in detail, settled in principle*. The OST floor cited in §1
plus the four IHL principles apply; what is unsettled is the application —
where the kinetic threshold sits for a non-debris-generating co-orbital
nudge, whether a GNSS spoof against military users counts as an "attack" for
IHL Article 49 purposes, whether reversible cyber effects ever cross the
distinction line. The engine sidesteps the unsettled application by encoding
*cost* rather than *veto*: every [`EffectInstance`](../../spacesim/engine/effects.py)
carries an `escalation_weight` field whose magnitude tracks the proportionality
calculus — irreversible kinetic with debris persistence carries the highest
weight, reversible EW the lowest, with cyber's weight scaled by the modeled
civilian-spillover footprint of the access vector (the `ground_modem` vector
inherits Viasat's spillover lesson). The resolver emits a `political_consequence`
side effect whose severity is read from this weight, so a cell that crosses
the proportionality line pays in the AAR scoring even when the floor regime
(§1) and the moratorium (§3 below) would each individually permit the act.

Used by: [`engine/effects.py:EffectInstance.escalation_weight`](../../spacesim/engine/effects.py)
(the proportionality-calibrated cost field on every resolved effect);
[`engine/effects.py:political_consequence`](../../spacesim/engine/effects.py)
(the side-effect emitter that reads `escalation_weight` and writes scoring cost);
[`content/vignettes/*.yaml:intro_brief.roe_note`](../../spacesim/content/vignettes/)
(per-vignette ROE notes in the mission brief that name the IHL principles in
operator-readable form).

### Sources

- *ICRC, "What is international humanitarian law?"* — [live](https://www.icrc.org/en/document/what-international-humanitarian-law)
  · [snapshot](https://web.archive.org/web/2026*/https://www.icrc.org/en/document/what-international-humanitarian-law)
  · accessed 2026-06-12.
- *ICRC Customary IHL database* (the canonical 161-rule restatement of
  customary IHL, including distinction, proportionality, precautions, and
  necessity) — [live](https://ihl-databases.icrc.org/en/customary-ihl)
  · [snapshot](https://web.archive.org/web/2026*/https://ihl-databases.icrc.org/en/customary-ihl)
  · accessed 2026-06-12.
- *CCDCOE, Tallinn Manual project page* (Tallinn Manual 2.0, February 2017) —
  [live](https://ccdcoe.org/research/tallinn-manual/)
  · [snapshot](https://web.archive.org/web/2026*/https://ccdcoe.org/research/tallinn-manual/)
  · accessed 2026-06-12.
- *Cambridge University Press, Tallinn Manual 2.0 on the International Law
  Applicable to Cyber Operations* (Schmitt ed., 2017) — [live](https://www.cambridge.org/core/books/tallinn-manual-20-on-the-international-law-applicable-to-cyber-operations/E4FFD83EA790D7C4C3C28FC9CA2FB6C9)
  · [snapshot](https://web.archive.org/web/2026*/https://www.cambridge.org/core/books/tallinn-manual-20-on-the-international-law-applicable-to-cyber-operations/E4FFD83EA790D7C4C3C28FC9CA2FB6C9)
  · accessed 2026-06-12.
- *Woomera Manual on the International Law of Military Space Operations*,
  University of Adelaide project page (launched 2018, draft ongoing) —
  [live](https://law.adelaide.edu.au/woomera)
  · [snapshot](https://web.archive.org/web/2026*/https://law.adelaide.edu.au/woomera)
  · accessed 2026-06-12.
- *MILAMOS Manual on International Law Applicable to Military Uses of Outer
  Space*, McGill Centre for Research in Air and Space Law project page
  (launched 2016) — [live](https://www.mcgill.ca/milamos/)
  · [snapshot](https://web.archive.org/web/2026*/https://www.mcgill.ca/milamos/)
  · accessed 2026-06-12.
- *CCDCOE Cyber Law Toolkit, "Viasat KA-SAT attack (2022)"* — [live](https://cyberlaw.ccdcoe.org/wiki/Viasat_KA-SAT_attack_(2022))
  · [snapshot](https://web.archive.org/web/2026*/https://cyberlaw.ccdcoe.org/wiki/Viasat_KA-SAT_attack_(2022))
  · accessed 2026-06-12.

---

## 3. The 2022 destructive-DA-ASAT test moratorium

Stacked atop the §1 treaty floor sits the most-recent — and the most operationally
load-bearing — layer the simulator encodes: the **US-led April 2022 unilateral
moratorium on destructive direct-ascent ASAT testing** and its **December 2022 UNGA
endorsement** as Resolution 77/41. Unlike the OST / Liability / Registration triad, the
moratorium is *political*, not legal — no signature, no ratification, no
dispute-resolution machinery. It is a norm, asserted unilaterally and then validated by
a 155-state UNGA vote, that any *destructive, debris-generating* direct-ascent
intercept of a satellite is internationally costly. That cost is exactly what the
engine's [`political_consequence`](../../spacesim/engine/effects.py) side effect on
`kinetic=True` + `Outcome=destroy` resolves into a score penalty — see the closing
paragraph and §3 of [`03-counterspace-taxonomy.md`](03-counterspace-taxonomy.md) for
the cross-reference.

### The US declaration (Vandenberg SFB, 18 April 2022)

Speaking at Vandenberg Space Force Base on **18 April 2022**, US Vice President
Kamala Harris announced that the United States "commits not to conduct destructive,
direct-ascent anti-satellite (DA-ASAT) missile testing, and … seeks to establish this
as a new international norm for responsible behavior in space"
([US State Department, *U.S. National Statement on the International Norm Against
Destructive Direct-Ascent Anti-Satellite Missile Testing*, 18 April 2022](https://www.state.gov/u-s-national-statement-on-the-international-norm-against-destructive-direct-ascent-anti-satellite-missile-testing/);
[White House, *Fact Sheet: Vice President Harris Advances National Security Norms in
Space*, 18 April 2022](https://www.whitehouse.gov/briefing-room/statements-releases/2022/04/18/fact-sheet-vice-president-harris-advances-national-security-norms-in-space/)).
Two scope choices are doctrinally load-bearing for the engine. **First**, the
declaration covers *destructive* DA-ASAT only — non-destructive tests (a fly-by, a
miss-distance demonstration) and the entire **co-orbital / RPO**, **EW**, **directed-
energy**, and **cyber** counterspace families sit outside its frame. The engine
mirrors this scope: only `Category="direct_ascent"` + `Outcome="destroy"` with
`kinetic=True` triggers the high-severity political-cost path; the other four
categories carry their own (lower) escalation weights. **Second**, the Vandenberg
language is *unilateral* — the US bound itself first and invited others to follow,
rather than negotiating a treaty text. That matters for vignette design (Vignette 5
turns the moratorium on with `roe_kinetic_authorized: false` but leaves the option
open for Red to violate it; the cost falls in scoring, not in a hard engine veto).

### UNGA Resolution 77/41 (7 December 2022)

The UN General Assembly adopted Resolution 77/41 — "Destructive direct-ascent
anti-satellite missile testing" — on **7 December 2022** by a vote of **155 in favour,
9 against, 9 abstaining**, after First-Committee passage on 31 October 2022
([UN press release, *First Committee Approves Nine Drafts*, 31 October 2022](https://press.un.org/en/2022/gadis3703.doc.htm)).
The nine States voting **against** were **Belarus, Bolivia, Central African Republic,
China, Cuba, Iran, Nicaragua, the Russian Federation, and Syria**; **India** abstained
along with eight other states (the SWF tracker reconciles the recorded First-Committee
vs. plenary roll-calls in detail)
([SWF, *Direct-Ascent Anti-Satellite Missile Tests: State Positions on the Moratorium,
UNGA Resolution, and Lessons for the Future*, October 2023](https://www.swfound.org/publications-and-reports/direct-ascent-anti--satellite-missile-tests-state-positions-on-the-moratorium-unga-resolution-and-lessons-for-the-future)).
The Resolution is a **recommendation**, not a binding instrument, and Russia in
particular has rejected the moratorium framing as one-sided — but the 155-vote majority
is the closest thing the open-source record has to a global consensus that
debris-generating kinetic ASAT is no longer politically free, and is the load-bearing
empirical fact the engine's high `political_consequence` severity for `destroy`-class
kinetic effects rests on.

### The SWF state-positions tracker

SWF's October 2023 *Direct-Ascent Anti-Satellite Missile Tests* report is the
canonical open-source ledger of which states have adopted the unilateral moratorium
pledge beyond merely voting yes on 77/41. As of the report's October 2023 cut-off,
**37 states** had publicly committed to a national-level destructive-DA-ASAT testing
moratorium — Canada, New Zealand, Japan, Germany, the UK, the Republic of Korea,
Australia, France, and most of NATO and the broader G7, with Costa Rica and Norway
the most-recent additions noted at publication
([SWF, *State Positions on the Moratorium*, October 2023](https://www.swfound.org/publications-and-reports/direct-ascent-anti--satellite-missile-tests-state-positions-on-the-moratorium-unga-resolution-and-lessons-for-the-future)).
Notably, **none of the four states with publicly-demonstrated DA-ASAT capability
beyond the United States — China, Russia, India, and (by single 2008 test) the US
itself — has joined except the US**; the moratorium's signatory base is composed of
states that *do not have* a destructive DA-ASAT capability to give up. The 2023 report
also catalogues an **industry statement** (signed by 27 commercial space operators in
April 2023) in parallel support
([SWF, *Release of Industry Statement in Support of International Commitments to Not
Conduct Destructive ASAT Tests*, April 2023](https://swfound.org/events/2023/release-of-industry-statement-in-support-of-international-commitments-to-not-conduct-destructive-asat-tests)).

### The proximate trigger: Cosmos-1408 (15 November 2021)

The Vandenberg announcement came **five months after** the Russian PL-19 Nudol
intercept of the defunct **Cosmos-1408 SIGINT satellite on 15 November 2021** at
~480 km altitude, which left **>1,500 tracked debris fragments** in a regime
persistent for **years to decades** and forced multiple ISS evasive manoeuvres in the
24 months that followed
([SWF, *SWF Statement on Russian ASAT Test*, 15 November 2021](https://swfound.org/news/all-news/2021/11/swf-statement-on-russian-asat-test)).
The chronology is doctrinally explicit in both the White House fact sheet and the SWF
moratorium report: Cosmos-1408 was the proximate trigger. See
[`03-counterspace-taxonomy.md` §3](03-counterspace-taxonomy.md) for the per-test
record (FY-1C 2007, Burnt Frost 2008, Mission Shakti 2019, Cosmos-1408 2021) the
moratorium is reacting to, and the engine's `abm_heavy` interceptor class to which
Cosmos-1408 maps in [`engine/engage.py:INTERCEPTORS`](../../spacesim/engine/engage.py).

### How the engine encodes the moratorium

The moratorium is a **norm, not a law** — there is no Article-IV-style hard veto, and
the engine deliberately mirrors that. A Red Cell with `roe_kinetic_authorized: true`
in vignette parameters *can* order a destructive kinetic ASAT and the engine will
resolve it; what changes is the scoring. [`engine/effects.py:political_consequence`](../../spacesim/engine/effects.py)
emits its highest-severity escalation cost for `kinetic=True` + `Outcome="destroy"` +
`debris_risk in {medium, high}` — calibrated to the 155-9-9 UNGA vote and the SWF
joiner ledger above. Two secondary engine encodings follow: the moratorium makes
**attribution unambiguous** (the booster plume, the catalog churn, and the
political response are all overt), so [`engine/effects.py:EffectInstance.attribution`](../../spacesim/engine/effects.py)
defaults to `"overt"` for destructive kinetic effects; and Vignette 5 (the DA-ASAT
crisis) turns the moratorium ON via `roe_kinetic_authorized: false` so the Red Cell
trainee must consciously *choose* to absorb the political cost to satisfy the
mission objective. The engine in this sense is a **norms-as-cost** machine: the floor
of §1 + the norm-layer of §3 are both *prices in the COA score*, never hard
prohibitions, which is what makes the simulator a useful PME tool for reasoning about
when violating a norm is worth the cost.

Used by: [`engine/effects.py:political_consequence`](../../spacesim/engine/effects.py)
(the escalation-cost severity on irreversible kinetic outcomes);
[`engine/effects.py:EffectInstance.attribution`](../../spacesim/engine/effects.py)
(`"overt"` default for destructive kinetic effects — the moratorium makes attribution
unambiguous); [`content/vignettes/05-da-asat-crisis.yaml`](../../spacesim/content/vignettes/)
(Vignette 5, the scenario where the moratorium-norm trade-off is the core teaching
point).

### Sources

- *US State Department, "U.S. National Statement on the International Norm Against
  Destructive Direct-Ascent Anti-Satellite Missile Testing"* (18 April 2022) —
  [live](https://www.state.gov/u-s-national-statement-on-the-international-norm-against-destructive-direct-ascent-anti-satellite-missile-testing/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.state.gov/u-s-national-statement-on-the-international-norm-against-destructive-direct-ascent-anti-satellite-missile-testing/)
  · accessed 2026-06-12.
- *White House, "Fact Sheet: Vice President Harris Advances National Security Norms
  in Space"* (18 April 2022) — [live](https://www.whitehouse.gov/briefing-room/statements-releases/2022/04/18/fact-sheet-vice-president-harris-advances-national-security-norms-in-space/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.whitehouse.gov/briefing-room/statements-releases/2022/04/18/fact-sheet-vice-president-harris-advances-national-security-norms-in-space/)
  · accessed 2026-06-12.
- *UN press release, "First Committee Approves Nine Drafts, Including Texts on
  Outer-Space Security, Anti-Satellite Missile Testing, Nuclear-Weapon-Free Zones"*
  (GA/DIS/3703, 31 October 2022) — [live](https://press.un.org/en/2022/gadis3703.doc.htm)
  · [snapshot](https://web.archive.org/web/2024*/https://press.un.org/en/2022/gadis3703.doc.htm)
  · accessed 2026-06-12.
- *Secure World Foundation, "Direct-Ascent Anti-Satellite Missile Tests: State
  Positions on the Moratorium, UNGA Resolution, and Lessons for the Future"*
  (October 2023) — [live](https://www.swfound.org/publications-and-reports/direct-ascent-anti--satellite-missile-tests-state-positions-on-the-moratorium-unga-resolution-and-lessons-for-the-future)
  · [snapshot](https://web.archive.org/web/2024*/https://www.swfound.org/publications-and-reports/direct-ascent-anti--satellite-missile-tests-state-positions-on-the-moratorium-unga-resolution-and-lessons-for-the-future)
  · accessed 2026-06-12.
- *Secure World Foundation, "Release of Industry Statement in Support of International
  Commitments to Not Conduct Destructive ASAT Tests"* (April 2023) —
  [live](https://swfound.org/events/2023/release-of-industry-statement-in-support-of-international-commitments-to-not-conduct-destructive-asat-tests)
  · [snapshot](https://web.archive.org/web/2024*/https://swfound.org/events/2023/release-of-industry-statement-in-support-of-international-commitments-to-not-conduct-destructive-asat-tests)
  · accessed 2026-06-12.
- *Secure World Foundation, "SWF Statement on Russian ASAT Test"* (15 November 2021)
  — [live](https://swfound.org/news/all-news/2021/11/swf-statement-on-russian-asat-test)
  · [snapshot](https://web.archive.org/web/2024*/https://swfound.org/news/all-news/2021/11/swf-statement-on-russian-asat-test)
  · accessed 2026-06-12.

---

## 4. Norms and CBMs under negotiation

The §3 destructive-DA-ASAT moratorium is the rare case of a norm that crossed from
draft text into an adopted UNGA endorsement — most of the rest of the
counterspace-norms agenda sits one step further upstream, still inside the
negotiating chambers at Geneva and New York. Between §3's adopted norm and a future
treaty regime is a **contested negotiation layer** the simulator does not encode as
engine rules (none of the proposals below has yet produced binding law), but which
the White Cell can fold into vignettes as `message` injects or `intro_brief.roe_note`
text when a scenario hinges on a state's diplomatic positioning. The layer matters
because it sets the *vocabulary* — "responsible behaviours," "TCBMs," "no first
placement," "legally binding instrument" — that real-world cells and political
advisors actually use in a crisis, and a PME tool that strips it out forfeits a chunk
of training value.

### UNGA Resolution 75/36 (December 2020) → the OEWG (2022-2023)

The current "responsible behaviours" track opened on **7 December 2020** when the
UNGA adopted **Resolution 75/36** — "Reducing space threats through norms, rules and
principles of responsible behaviours" — on a UK-led initiative that deliberately
inverted the prior treaty-first PAROS framing: rather than negotiate a binding ban
on weapons, the resolution asked States to *describe* the behaviours they consider
threatening and to identify norms that would make space operations safer
([UNODA Outer Space (Emerging Challenges)](https://disarmament.unoda.org/en/our-work/emerging-challenges/outer-space);
[UN Digital Library, A/RES/75/36](https://digitallibrary.un.org/record/3895440?ln=en)).
The follow-on Resolution **76/231** of December 2021 then convened the
**Open-Ended Working Group on Reducing Space Threats through Norms, Rules and
Principles of Responsible Behaviours (OEWG)**, which met for **four sessions in
2022-2023** in Geneva with over 70 participating States and dozens of civil-society
observers
([SWF, *OEWG on Reducing Space Threats — 2023 Fact Sheet*](https://www.swfound.org/publications-and-reports/oewg-reducing-space-threats-2023-fact-sheet);
[UNIDIR, *OEWG on Reducing Space Threats: Recap Report*](https://unidir.org/publication/oewg-on-reducing-space-threats-recap-report/)).
Standing agenda items included destructive ASAT testing, uncoordinated rendezvous and
proximity operations (RPO), and the application of international humanitarian law in
space — the topics the simulator already encodes as `political_consequence` cost
inputs in §2 and §3.

### The OEWG's failed consensus and the analytical takeaway

The OEWG's **fourth and final session concluded 1 September 2023** without consensus
on a substantive report; in an unprecedented procedural outcome the group could not
adopt even a basic procedural description of the meetings, and the Chair instead
issued a personal summary as a working paper
([Project Ploughshares, *OEWG on Reducing Space Threats — Final Recap*, September
2023](https://ploughshares.ca/the-open-ended-working-group-on-reducing-space-threats-final-recap/)).
The proximate blockers were Russia and a small group of like-minded States who
objected to the "responsible behaviours" framing on the grounds that it diverted
attention from the underlying treaty-first PPWT proposal (below); the structural
fault-line was the **norms-first vs. treaty-first contestation** that has shaped the
PAROS agenda for two decades, with the US / UK / Western bloc preferring incremental
behavioural norms (which constrain Russian and Chinese terrestrial counterspace
capabilities) and the Russia / China bloc preferring a binding placement-of-weapons
treaty (which constrains US space-based missile defence) — neither side willing to
trade its preferred order of operations
([Open Canada, *Star-crossed States: No result from the UN Working Group on
Reducing Space Threats*, 2023](https://opencanada.org/star-crossed-states-no-result-from-the-un-working-group-on-reducing-space-threats/);
[UN press release GA/DIS/3730, *Consensus Scuttled in First Committee … Creating
Parallel Processes*, 2023](https://press.un.org/en/2023/gadis3730.doc.htm)).

### The GGE on PAROS and the parallel CD / PPWT track

The treaty-first track ran in parallel through two other fora. The **Group of
Governmental Experts on Further Practical Measures for the Prevention of an Arms
Race in Outer Space (GGE-PAROS)** convened in **two two-week sessions in Geneva in
2018 and 2019** under UNGA Resolution 72/250, with a 25-State membership mandated to
"consider and make recommendations on substantial elements of an international
legally binding instrument" on PAROS — but the GGE, like the later OEWG, was
**unable to reach consensus on a substantive report**
([UNODA, *GGE on Further Practical Measures for PAROS (2019)*](https://meetings.unoda.org/gge-paros/group-governmental-experts-further-practical-measures-prevention-arms-race-outer-space)).
At the Conference on Disarmament (CD) in Geneva, Russia and China have since **2008**
tabled the **Draft Treaty on the Prevention of the Placement of Weapons in Outer
Space and of the Threat or Use of Force against Outer Space Objects (PPWT)**, with an
updated text introduced on **10 June 2014**
([Reaching Critical Will, *Russia and China table new draft treaty …*, 2014](https://www.reachingcriticalwill.org/disarmament-fora/cd/2014/cd-reports/8908-russia-and-china-table-new-draft-treaty-to-prevent-weapons-in-space);
[*The Space Review*, *The 2014 PPWT: a new draft but with the same and different
problems*, 2015](https://www.thespacereview.com/article/2575/1)).
Western analysts read the PPWT as **structurally one-sided**: it would prohibit the
placement of weapons in space (where the US has the largest stake) while leaving
ground-based ASATs (the SC-19, the PL-19 Nudol, the A-235) entirely outside its scope
and providing no verification machinery — the criticism most often cited as the
reason the CD has never reached a programme of work on the text. The current
**follow-on OEWG on Prevention of an Arms Race in Outer Space (2024-2025)**,
authorised by **UNGA Resolution 78/238 (22 December 2023)**, is the latest attempt
to bridge the two tracks: its mandate covers "further practical measures … on PAROS,
including the prevention of the placement of weapons in outer space," explicitly
combining the behavioural-norms and legally-binding-instrument vocabularies
([Diplo, *Six resolutions related to outer space adopted at UNGA 78*, January 2024](https://www.diplomacy.edu/updates/six-resolutions-related-to-outer-space-adopted-at-unga-78/);
[SWF, *Multilateral Space Security Initiatives*](https://www.swfound.org/publications-and-reports/multilateral-space-security-initiatives)).

### Engine implication

None of the four instruments above — Resolution 75/36, the OEWG outcome, the
GGE-PAROS recommendations, the PPWT — has yet produced binding law, and the
simulator therefore does not encode any of them as engine rules: there is no
`ppwt_compliance` flag, no `oewg_norm_violation` cost term. They enter the simulator
*as text*: the White Cell can introduce any of them mid-vignette as an
`inject_library.yaml` `message` effect (e.g. "Russian MFA cites PPWT Article II in
demarche over Blue's RPO approach"), or a vignette author can name them in a per-cell
`intro_brief.roe_note` to frame the diplomatic backdrop the cell is operating
against. See §5 below for the ROE design pattern that translates this layer into
vignette parameters — most often by toggling `roe_kinetic_authorized` or
`roe_cyber_authorized` to reflect the cell's interpretation of its own State's
position in the ongoing negotiation.

Used by: [`content/vignettes/*.yaml:intro_brief.roe_note`](../../spacesim/content/vignettes/)
(per-vignette ROE-note text where negotiated norms can be referenced as the
diplomatic backdrop);
[`content/inject_library.yaml`](../../spacesim/content/inject_library.yaml)
(white-cell inject templates that can introduce a CBM or PPWT-style demarche as a
mid-vignette `message` effect).

### Sources

- *UNODA, "Outer Space" (Emerging Challenges page)* — [live](https://disarmament.unoda.org/en/our-work/emerging-challenges/outer-space)
  · [snapshot](https://web.archive.org/web/2026*/https://disarmament.unoda.org/en/our-work/emerging-challenges/outer-space)
  · accessed 2026-06-12.
- *UN Digital Library, "Reducing space threats through norms, rules and principles
  of responsible behaviours"* (A/RES/75/36, 7 December 2020) —
  [live](https://digitallibrary.un.org/record/3895440?ln=en)
  · [snapshot](https://web.archive.org/web/2026*/https://digitallibrary.un.org/record/3895440?ln=en)
  · accessed 2026-06-12.
- *Secure World Foundation, "OEWG on Reducing Space Threats — 2023 Fact Sheet"*
  (October 2023) — [live](https://www.swfound.org/publications-and-reports/oewg-reducing-space-threats-2023-fact-sheet)
  · [snapshot](https://web.archive.org/web/2024*/https://www.swfound.org/publications-and-reports/oewg-reducing-space-threats-2023-fact-sheet)
  · accessed 2026-06-12.
- *UNIDIR, "OEWG on Reducing Space Threats: Recap Report"* (2023) —
  [live](https://unidir.org/publication/oewg-on-reducing-space-threats-recap-report/)
  · [snapshot](https://web.archive.org/web/2024*/https://unidir.org/publication/oewg-on-reducing-space-threats-recap-report/)
  · accessed 2026-06-12.
- *Project Ploughshares, "The Open-Ended Working Group on Reducing Space Threats —
  Final Recap"* (September 2023) — [live](https://ploughshares.ca/the-open-ended-working-group-on-reducing-space-threats-final-recap/)
  · [snapshot](https://web.archive.org/web/2024*/https://ploughshares.ca/the-open-ended-working-group-on-reducing-space-threats-final-recap/)
  · accessed 2026-06-12.
- *Open Canada, "Star-crossed States: No result from the UN Working Group on
  Reducing Space Threats"* (2023) — [live](https://opencanada.org/star-crossed-states-no-result-from-the-un-working-group-on-reducing-space-threats/)
  · [snapshot](https://web.archive.org/web/2024*/https://opencanada.org/star-crossed-states-no-result-from-the-un-working-group-on-reducing-space-threats/)
  · accessed 2026-06-12.
- *UN press release, "Consensus Scuttled in First Committee over Two Competing Draft
  Resolutions on Space Security, Creating Parallel Processes, Polarization"*
  (GA/DIS/3730, 2023) — [live](https://press.un.org/en/2023/gadis3730.doc.htm)
  · [snapshot](https://web.archive.org/web/2024*/https://press.un.org/en/2023/gadis3730.doc.htm)
  · accessed 2026-06-12.
- *UNODA, "Group of Governmental Experts on Further Practical Measures for the
  Prevention of an Arms Race in Outer Space (2019)"* —
  [live](https://meetings.unoda.org/gge-paros/group-governmental-experts-further-practical-measures-prevention-arms-race-outer-space)
  · [snapshot](https://web.archive.org/web/2024*/https://meetings.unoda.org/gge-paros/group-governmental-experts-further-practical-measures-prevention-arms-race-outer-space)
  · accessed 2026-06-12.
- *Reaching Critical Will, "Russia and China table new draft treaty to prevent
  weapons in space"* (2014) — [live](https://www.reachingcriticalwill.org/disarmament-fora/cd/2014/cd-reports/8908-russia-and-china-table-new-draft-treaty-to-prevent-weapons-in-space)
  · [snapshot](https://web.archive.org/web/2024*/https://www.reachingcriticalwill.org/disarmament-fora/cd/2014/cd-reports/8908-russia-and-china-table-new-draft-treaty-to-prevent-weapons-in-space)
  · accessed 2026-06-12.
- *The Space Review, "The 2014 PPWT: a new draft but with the same and different
  problems"* (Listner & Rajagopalan, 2015) —
  [live](https://www.thespacereview.com/article/2575/1)
  · [snapshot](https://web.archive.org/web/2024*/https://www.thespacereview.com/article/2575/1)
  · accessed 2026-06-12.
- *Diplo, "Six resolutions related to outer space adopted at UNGA 78"* (January 2024,
  covering A/RES/78/238 on the follow-on OEWG on PAROS) —
  [live](https://www.diplomacy.edu/updates/six-resolutions-related-to-outer-space-adopted-at-unga-78/)
  · [snapshot](https://web.archive.org/web/2024*/https://www.diplomacy.edu/updates/six-resolutions-related-to-outer-space-adopted-at-unga-78/)
  · accessed 2026-06-12.
- *Secure World Foundation, "Multilateral Space Security Initiatives"* (ongoing
  tracker covering OEWG-PAROS 2024-2025) —
  [live](https://www.swfound.org/publications-and-reports/multilateral-space-security-initiatives)
  · [snapshot](https://web.archive.org/web/2024*/https://www.swfound.org/publications-and-reports/multilateral-space-security-initiatives)
  · accessed 2026-06-12.

---

## 5. ROE design pattern (how the sim maps law to play)

The prior four subsections described **what the legal landscape is** — the §1 treaty
floor, the §2 LOAC overlay, the §3 destructive-DA-ASAT moratorium, the §4
responsible-behaviours / CBM layer. This subsection describes **what the engine does
with it**. A unifying design pattern emerges: **norms-as-cost, not norms-as-veto**. The
engine almost never refuses an order on legal grounds; it resolves the order and
charges the political price through a side-effect channel that the AAR reads back as
scoring. The lone hard-veto is the OST Art. IV ban on orbital weapons of mass
destruction, encoded as a *scenario-set out-of-bounds* (no orbital-WMD asset templates
exist) rather than as a runtime check. Everything else is priced, not blocked. This
mirrors the doctrinal preference USSF *Spacepower* (Capstone Publication, **June 2020**)
articulates for **reversible effects first** — "non-kinetic, reversible means" are the
doctrinal default because they preserve the contested orbital regime that the same
force must keep operating in
([USSF *Spacepower* Capstone Publication, June 2020](https://media.defense.gov/2020/Jun/17/2002317391/-1/-1/0/SPACE_CAPSTONE_PUBLICATION_10_JUN_2020.PDF)).

### The two ROE flags

[`content/vignette.py:build_world`](../../spacesim/content/vignette.py) (lines 205-208)
reads `red_kinetic_authorized` and `cyber_authorized` out of the vignette `parameters:`
block and writes them onto `VignetteContext.roe`.
[`session/manager.py`](../../spacesim/session/manager.py) line 40 then constructs
`OrderSystem(self.sim, roe=dict(self.ctx.roe))`, copying the dict so White Cell can flip
a flag at runtime without mutating the vignette source. Of the 19 shipped vignettes,
**all default `red_kinetic_authorized: false`** except Vignette 5 (the DA-ASAT crisis)
and the four "MD" Red-COA presets (`coa-china-md`, `coa-russia-md`, …); `cyber_authorized`
defaults true in the cyber-themed vignettes (6, 8, the COA presets) and false elsewhere.
Kinetic OFF + cyber selectively ON is the engine's encoding of the §1 treaty floor + §3
moratorium baseline.

### The validate-step gates

[`OrderSystem.validate()`](../../spacesim/engine/orders.py) (lines 343-354) is the
gatekeeper. An `engage` order with `kinetic_authorized=false` returns
`(False, "roe_kinetic_not_authorized")`; a `cyber` order with `cyber_authorized=false`
returns `(False, "roe_cyber_not_authorized")`. Both reasons surface in the UI's order
panel as pre-disabled buttons with human-readable strings in
[`ui_web/static/app.js`](../../spacesim/ui_web/static/app.js) ("ROE does not authorize
kinetic / cyber effects."), and the dry-run pre-check returns the same reason without
scheduling — so the trainee sees *why* a button is disabled before issuing.

### `political_consequence` as the unified cost signal

The substantive cost channel is [`engine/effects.py:ModerateEffectResolver.resolve`](../../spacesim/engine/effects.py)
emitting a `political_consequence` side effect into `EffectOutcome.side_effects`. Two
emission paths exist: a **high-severity path** (lines 137-138) when an irreversible
kinetic effect succeeds with `debris_risk != "none"` — severity is `"high"` if
`EffectInstance.escalation_weight >= 7` or `debris_risk == "high"`, `"medium"` otherwise
— and a **medium-severity collateral path** (lines 159-162) when a reversible
link-denial outcome (`deny`, `disrupt`, `spoof`) lands on a `civilian=True` target,
modelling the §2 distinction / proportionality lesson the Viasat KA-SAT case crystallises
([CCDCOE *Tallinn Manual 2.0*, February 2017](https://ccdcoe.org/research/tallinn-manual/)).
The `escalation_weight` field is itself the §2 / §3 calibration knob: destructive
kinetic templates carry the highest weights (moratorium calibration), reversible EW the
lowest, cyber scaled by access-vector spillover.

### Per-vignette `intro_brief.roe_note`

Every vignette's [`intro_brief`](../../spacesim/content/vignettes/) block carries a
per-cell `roe_note:` string surfacing the relevant treaty / norm framing in
operator-readable form. Vignette 1's note tells Blue "Red kinetic ASAT is DISABLED by
default … Blue has no kinetic option this vignette"; Vignette 5's red note warns
"Kinetic is AUTHORIZED here … Weapons-quality track is REQUIRED"; Vignette 6's notes the
cyber-ON default with "No window required, no kinetic involved." The notes render into
the Mission-brief panel via `/api/sessions/{sid}/brief/{cell}` alongside live ROE chips
and objective deadlines, so the trainee sees the law-to-engine mapping the moment a
vignette loads. The framing matches the West-leaning "responsible behaviours in space"
posture the UK FCDO codifies
([UK Government, *National Space Strategy in Action*, February 2023](https://www.gov.uk/government/publications/national-space-strategy-in-action)).

### The PME trade-off

This pattern lets the trainee **choose** to violate a norm and **discover** the cost in
the AAR — the PME teaching point. A hard-veto pattern (refuse every kinetic order whose
debris cone touches a populated regime) would just block the order and prevent the
lesson. The Vignette 5 cycle — Red authorised kinetic, Red strikes, Red wins, debris
field forms, `un_condemnation` inject fires, *both cells* lose the regime — only runs
because the engine resolved the strike rather than blocking it. The cost was paid in
`political_consequence` severity plus debris persistence, not in a refusal at
`validate()`.

Used by: [`session/manager.py`](../../spacesim/session/manager.py) (line 40, ROE flag
loading); [`engine/orders.py:OrderSystem.validate`](../../spacesim/engine/orders.py)
(lines 343-354, the validate-step ROE gates);
[`engine/effects.py:political_consequence`](../../spacesim/engine/effects.py) (the
unified cost signal, both kinetic and civilian-collateral paths);
[`content/vignettes/*.yaml:intro_brief.roe_note`](../../spacesim/content/vignettes/)
(per-vignette ROE-note text rendered by `/api/sessions/{sid}/brief/{cell}`).

### Sources

- *USSF Spacepower, Space Capstone Publication* (June 2020 — the doctrinal preference
  for reversible / non-kinetic means in space) — [live](https://media.defense.gov/2020/Jun/17/2002317391/-1/-1/0/SPACE_CAPSTONE_PUBLICATION_10_JUN_2020.PDF)
  · [snapshot](https://web.archive.org/web/2026*/https://media.defense.gov/2020/Jun/17/2002317391/-1/-1/0/SPACE_CAPSTONE_PUBLICATION_10_JUN_2020.PDF)
  · accessed 2026-06-12.
- *CCDCOE, Tallinn Manual 2.0 project page* (the canonical non-binding restatement of
  cyber-LOAC application; same source §2 cites) — [live](https://ccdcoe.org/research/tallinn-manual/)
  · [snapshot](https://web.archive.org/web/2026*/https://ccdcoe.org/research/tallinn-manual/)
  · accessed 2026-06-12.
- *UK Government, "National Space Strategy in Action"* (February 2023 — the UK FCDO /
  MoD articulation of responsible-behaviours framing for military space) —
  [live](https://www.gov.uk/government/publications/national-space-strategy-in-action)
  · [snapshot](https://web.archive.org/web/2026*/https://www.gov.uk/government/publications/national-space-strategy-in-action)
  · accessed 2026-06-12.

---

## 6. Cross-references

- **Engine modules sourced by this file.** [`session/manager.py`](../../spacesim/session/manager.py) (§1, §3, §5 — the `roe_kinetic_authorized` / `roe_cyber_authorized` flag loading from vignette parameters); [`engine/orders.py`](../../spacesim/engine/orders.py) (§5 — the validate-step ROE gates that reject orders violating active ROE flags); [`engine/effects.py`](../../spacesim/engine/effects.py) (§1, §2, §3, §5 — the `political_consequence` side effect calibrated to the treaty floor + the §3 moratorium; the `EffectInstance.escalation_weight` field calibrated to the §2 IHL proportionality principle; the `EffectInstance.attribution="overt"` default for destructive kinetic effects per §3); [`engine/engage.py:INTERCEPTORS`](../../spacesim/engine/engage.py) (§3 — `abm_heavy` calibrated to the Cosmos-1408 proximate-trigger record); [`engine/ssn.py`](../../spacesim/engine/ssn.py) (§1 — the public-record assumption the Registration Convention establishes).
- **Vignette / content surfaces.** [`content/vignettes/*.yaml:parameters`](../../spacesim/content/vignettes/) (every vignette's ROE-flag defaults per §1 and §5); [`content/vignettes/*.yaml:intro_brief.roe_note`](../../spacesim/content/vignettes/) (per-vignette ROE-note text surfacing the relevant treaty / LOAC / moratorium framing — §2 IHL principles and §4 CBM context land here); [`content/inject_library.yaml`](../../spacesim/content/inject_library.yaml) (white-cell `message` injects can introduce a §4 CBM mid-vignette); [`content/vignettes/05-da-asat-crisis.yaml`](../../spacesim/content/vignettes/) (Vignette 5 — the canonical "destructive DA-ASAT trade-off" scenario built around §3).
- **Sibling primer files.** [`01-doctrine-western.md`](01-doctrine-western.md) (reversible-effects-first doctrinal preference that §5 encodes); [`03-counterspace-taxonomy.md`](03-counterspace-taxonomy.md) (the per-category effects this file's political-cost calibration scores; §3 of that file specifically catalogs the four DA-ASAT tests §3 here reacts to); [`04-orbital-mechanics-primer.md`](04-orbital-mechanics-primer.md) (the access-window gates this file's ROE flags add on top of); [`07a-incident-record.md`](07a-incident-record.md) (Tier 4 deferred — the per-incident catalog that anchors §3's moratorium chronology).
- **Audit predecessor.** [`docs/AUDIT-2026-06-COMMANDS.md`](../AUDIT-2026-06-COMMANDS.md) §M2 (the commands-layer audit that crystallized the `INTERCEPTORS` database around the four DA-ASAT test records §3 cites and the Cosmos-1408 trigger §3 names).
- **Research encyclopedia.** [`encyclopedia/R303-deterrence-theory.md`](encyclopedia/R303-deterrence-theory.md) and [`encyclopedia/R304-escalation-dynamics.md`](encyclopedia/R304-escalation-dynamics.md) for the strategic-theory counterparts to this file's treaty/ROE/political-cost calibration; [`encyclopedia/R213-signaling-theory.md`](encyclopedia/R213-signaling-theory.md) (already cites this file in the reverse direction) for the CBM/signaling treatment of §4.

*Last reviewed: 2026-06-12. Pending review: every 12 months from `last_reviewed`.*
