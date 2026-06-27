# FS-108 — Inject Authoring *(candidate)*

> **Document ID:** FS-108
> **Version:** 0.1 (candidate scope — not authorized)
> **Status:** 🅿️ Scoped, not authorized
> **Dependencies:** [DOM-003](../domains/DOM-003-white-cell-framework.md) §4, §9
> **Referenced By:** [DOM-003](../domains/DOM-003-white-cell-framework.md)
> **Produces:** nothing yet — no Implementation Package may begin against this ID without explicit
> user go-ahead (see [`MSTR-006`](../master/MSTR-006-governance-principles.md) §3)
> **Feature Mapping:** FS-108 (this document)
> **Related Topics:** [FS-106](FS-106-white-cell-dashboard.md) (the dashboard this feature would extend)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

## Why this is a stub, not a full spec

Per [DOM-003](../domains/DOM-003-white-cell-framework.md) §1's frontmatter, FS-108 is explicitly marked **"(candidate)"** everywhere it
appears in the existing corpus — the owning domain document describes the *gap* this feature would
close but stops short of committing it as scoped work. Per [`MSTR-006`](../master/MSTR-006-governance-principles.md) §3, promoting this
to a full ✅ Feature Specification (or beginning any Implementation Package against it) requires
explicit user authorization, which has not been given. This document records the candidate scope
as it exists in the corpus today, so the gap is documented without being prematurely committed.

## Candidate scope (per DOM-003 §4 and §9)

The White Cell Dashboard ([FS-106](FS-106-white-cell-dashboard.md)) already exposes the existing inject mechanism — five
reusable templates in `inject_library.yaml`, an editable-JSON form, and a Now/+seconds/absolute-UTC
scheduler. [DOM-003](../domains/DOM-003-white-cell-framework.md) §4 names a feature that makes inject *authoring* easier (not the
underlying execution mechanism, which is already engine-side and complete) as squarely its own
territory:

- Templated parameter forms (vs. raw editable JSON) for the existing five templates.
- A preview-before-schedule step.
- A library browser with search, as the template library grows.
- (§9, open work) Composing multiple inject templates into a pre-scripted sequence ahead of a
  session — today inject scheduling is ad hoc, one at a time, live.

## Explicit non-goal

This candidate would not duplicate or replace the inject *execution* mechanism — that engine-side
capability (`InProcessSession.inject_library()`) already exists and works; FS-108's hypothetical
scope is authoring ergonomics only.

## Next step if authorized

If the user authorizes this feature, it should be promoted to a full Feature Specification (status
✅, version 1.0) following the same structure as [FS-101](FS-101-mission-planning.md)-[FS-107](FS-107-after-action-review.md), grounded in [DOM-003](../domains/DOM-003-white-cell-framework.md) §4/§9,
before any Implementation Package work begins.
