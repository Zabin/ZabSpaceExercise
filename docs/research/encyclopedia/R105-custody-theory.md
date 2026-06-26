# R105 — Custody Theory

> **Document ID:** R105
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** R102
> **Referenced By:** R104, R109, R115, R116, R117, R119, DOM-002, FS-103
> **Produces:** implementation constraints for `engine/custody.py`
> **Feature Mapping:** FS-103 (Custody Management)
> **Related Topics:** R102 (SDA), MSTR-004 Glossary (custody, weapons-quality track), DOM-002 §4 (custody quality as an assessment dimension)

[↑ Tier R100 index](R100-index.md) · [Encyclopedia index](INDEX.md)

## 1. Purpose

Custody is arguably the single most pedagogically load-bearing concept in the simulator
(MSTR-003 §4) — it is *the* mechanism by which fog-of-war becomes a felt, earned thing rather than
an abstract rule. This topic gives the precise model so new features that touch custody (a new
sensor, a new weapon-class effect, a new assessment metric) implement it consistently.

## 2. Concepts

**Custody is not binary.** `Track` models custody as a *confidence* value that decays over time
since last refresh, on-demand (computed when read, not on a background ticking process) — this
on-demand decay design is itself an implementation choice worth preserving: it means custody
confidence is always correct-as-of-now without requiring a per-tick update pass over every track in
every session.

**Weapons-quality track is a threshold, not a synonym for custody.** A track exists (has some
confidence) the moment any detection occurs; a *weapons-quality* track is one whose confidence has
crossed a specific, higher threshold required to authorize a weapon-class effect. Treating "has a
track" and "weapons-quality" as interchangeable is the single most common implementation error this
topic exists to prevent — many real-world custody-related incidents (and many vignette objectives)
turn exactly on this distinction.

**Custody must be actively maintained.** Confidence decays without refresh; a single detection does
not grant permanent custody. This is the structural reason a cell must keep tasking sensors against
an object of interest rather than "set and forget" — it is what makes collection management (R104)
a real, continuous resource-allocation problem instead of a one-time setup cost.

**Custody is per-cell.** Red and Blue maintain entirely independent `TrackCatalog`s on the same
underlying ground-truth objects — one cell's custody of an object says nothing about the other
cell's. This independence is what the `CellController` fog-of-war boundary (MSTR-002 §2 invariant
3) actually enforces at the data-structure level.

## 3. Operational Context

Real SSA/SDA practice treats "do we have actionable custody" as a constantly re-evaluated
operational question, not a one-time classification — an analyst routinely has to judge whether a
track is current enough, and confident enough, to support a given decision (engagement,
maneuver-avoidance, simple monitoring). Different decisions require different confidence
thresholds — the weapons-quality gate is the simulator's explicit encoding of "engagement requires
the highest bar."

## 4. Implementation Guidance

- **Never let a feature derive "is this engageable" from anything other than the live
  weapons-quality gate computed at decision time.** Caching an engageability boolean (rather than
  recomputing confidence on demand) reintroduces exactly the staleness bug the on-demand decay
  design exists to prevent.
- **A new sensor modality or SSN source (R109, R118) should feed into the existing `Track`
  structure**, contributing to confidence/refresh, rather than creating a parallel "this cell knows
  about X" channel.
- **Any new effect category that requires custody as a precondition must specify which confidence
  tier it requires** (mere detection vs. weapons-quality vs. something in between) explicitly in its
  Feature Specification — don't leave this as an implicit assumption.
- **Assessment features (DOM-002) measuring "custody quality" should distinguish "engaged a
  weapons-quality track" from "engaged after only a bare detection"** — this is precisely the
  speculative-vs-disciplined distinction DOM-002 §4 calls for.

## 5. Feature Mapping

FS-103 (Custody Management) is the direct owner. R104 (Collection Management), R115-R117 (effect
categories with custody preconditions), and DOM-002 (assessment) are all downstream consumers of
this model.

## 6. Related Topics

R102 (SDA — the broader chain custody's *track* stage sits inside), R119 (Data Fusion — combining
multiple sources to raise one custody confidence value), MSTR-004 (Glossary — canonical one-line
definitions of "custody" and "weapons-quality track").
