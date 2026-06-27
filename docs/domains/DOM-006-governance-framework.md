# DOM-006 — Governance Framework

> **Document ID:** DOM-006
> **Version:** 1.0
> **Status:** 🚧 In progress
> **Dependencies:** MSTR-001, MSTR-006
> **Referenced By:** DOM-003, DOM-009, all FS-*, all IMP-*
> **Produces:** the change-control rules for simulator content (vignettes, ROE, effect templates) and feature scope
> **Feature Mapping:** N/A — process framework, not a feature surface itself
> **Related Topics:** MSTR-006 (documentation governance — the sibling document this elaborates for *simulator* content), DOM-003, DOM-009

[↑ Docs index](../INDEX.md)

## 1. Purpose

MSTR-006 governs the *documentation corpus's* lifecycle. DOM-006 governs the **simulator's content
and feature-scope lifecycle** — how a new vignette, ROE rule, effect template, or feature proposal
moves from idea to authorized, shippable change. The two are siblings: MSTR-006 for docs-about-docs,
DOM-006 for docs-about-the-product.

## 2. Scope

In scope: authorization gates for new vignette content, ROE/doctrine changes, and feature-scope
decisions; the relationship between `FUTURE-WORK.md` (deferred items) and active Feature
Specifications. Out of scope: documentation-corpus versioning (MSTR-006), engineering code review
practice (a repository/CI concern, not a documentation-domain one).

## 3. Content change classes

| Class | Example | Authorization needed |
|---|---|---|
| **Additive, low-risk** | A new inject template, a new vignette within an existing progression slot (DOM-001 §4) | Author discretion; record in `ROADMAP.md`/vignette INDEX |
| **Additive, scope-expanding** | A new effect category, a new access channel, a new sensor modality | Feature Specification required (Phase 4 process) before any Implementation Package |
| **Modifying existing balance** | Recalibrating power-drain constants (the Jun 2026 audit precedent), ROE defaults | Documented audit/rationale (see `AUDIT-2026-06*.md` as the precedent format) + regression test |
| **Large, multi-tier undertaking** | The research-corpus 10× expansion (`FUTURE-WORK.md` §12), a new top-level domain | 🅿️ explicit user authorization per MSTR-006 §3, tier by tier |

## 4. The `FUTURE-WORK.md` ↔ Feature Specification relationship

`FUTURE-WORK.md` is the single-source v1.1+ TODO — it is where a deferred item *starts its life*,
often as a one-paragraph gap statement (e.g., the dead `power_w` field, the decoupled propellant
gauge, noted in `AUDIT-2026-06-UI-TTC.md` §2). DOM-006's rule: **a `FUTURE-WORK.md` item graduates
into a Feature Specification once it is judged worth doing** (an author or facilitator decision,
not automatic), at which point the FS supersedes the TODO bullet as the authoritative description
and the bullet should be marked resolved-by-reference (`→ see FS-xxx`) rather than duplicated.
Items that stay as bare TODO bullets indefinitely are *known, accepted gaps*, not silently forgotten
ones — this is why `FUTURE-WORK.md` exists as a single source rather than scattered code comments.

## 5. Audit reports as a governance artifact

The three `AUDIT-2026-06*.md` reports are the existing precedent for how DOM-006 expects a
significant retrospective review to be documented: point-in-time, dated, scoped to specific
complaints/findings, with explicit "fixed" vs. "documented, lower priority, follow-up" sections.
Future audits (e.g., a Phase-6/7/8 consistency/dependency/traceability review of this very
documentation expansion) should follow this same shape rather than inventing a new report format
each time.

## 6. Decision rights

| Decision | Who decides |
|---|---|
| Whether a `FUTURE-WORK.md` item graduates to a Feature Specification | Any contributor, by writing the FS — no separate approval gate for *specifying* |
| Whether a 🅿️-tier or large undertaking is authorized to *start* | The user/program owner (MSTR-006 §3) |
| Whether a vignette content change is balanced/correct doctrine | White Cell subject-matter judgment (DOM-003, DOM-009) |
| Whether an architecture/invariant (MSTR-002) may be relaxed for a feature | Not a unilateral author decision — requires explicit escalation per MSTR-006 §6 |

## 7. What this framework expects from Feature Specifications and Implementation Packages

Every FS should note, if applicable, which `FUTURE-WORK.md` item(s) it graduates from (or state "new,
not previously tracked"). Every IMP should state which content-change class (§3) its work falls
into and, for "modifying existing balance" or larger classes, point to the audit/rationale artifact
justifying the change.

## 8. Related topics

MSTR-006 (the documentation-corpus governance this framework parallels for simulator content),
DOM-003 (White Cell's authority over in-session content decisions, a narrower real-time cousin of
this framework's content-change governance), DOM-009 (doctrine development, which feeds the
"modifying existing balance" and doctrinal-additive classes in §3).
