# FS-112 — Classification Banner

> **Document ID:** FS-112
> **Version:** 1.0
> **Status:** ✅ Done
> **Dependencies:** [DOM-003](../domains/DOM-003-white-cell-framework.md), [FS-115](FS-115-session-setup.md)
> **Referenced By:** [docs/feature-planning/03-feature-catalog.md](../feature-planning/03-feature-catalog.md) `FEAT-4500`, [docs/feature-planning/05-feature-review.md](../feature-planning/05-feature-review.md) Finding F-02, [IP-1120](../implementation/packages/IP-1120-classification-banner.md)
> **Produces:** the banner string rendered on every screen and embedded in every export
> **Feature Mapping:** FS-112 (this document)
> **Related Topics:** [FS-106](FS-106-white-cell-dashboard.md) (the White Cell dashboard this banner renders alongside), [FS-107](FS-107-after-action-review.md) (AAR exports this banner must be embedded in)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template. It is a **new**
Feature Specification closing Finding F-02 in `docs/feature-planning/05-feature-review.md`: this
capability had a real, Must-priority baselined FR (FR-4510) but zero presence in any of the 11
pre-existing `FS-xxx` documents.*

## Feature ID

FS-112

## Title

Classification Banner

## Purpose

Make explicit, on every screen and in every exported file, that all session content is unclassified
training material — per `docs/feature-planning/03-feature-catalog.md` `FEAT-4500`'s own Purpose
field.

## Scope

In scope: setting a classification banner value (`UNCLASSIFIED//EXERCISE` or
`UNCLASSIFIED//TRAINING`) at scenario build time, and rendering/embedding that value on every UI
screen and in every exported file with no omission. Out of scope: the vignette-build workflow this
setting is part of ([FS-115](FS-115-session-setup.md), which this Feature depends on); the content
of AAR exports themselves beyond banner embedding ([FS-107](FS-107-after-action-review.md)).

## Requirements Implemented

FR-4510 (classification banner set and displayed), NFR-3100 (classification banner on every screen
and export) — per `docs/feature-planning/03-feature-catalog.md` `FEAT-4500`'s `Included
Requirements`.

## User Workflows

- White Cell selects a classification banner value while building/loading a vignette.
- Every screen a White Cell, Blue, Red, or Observer participant views during the session renders
  the active banner value.
- Every export the session produces (AAR export, save file) embeds the same banner value.

## System Behaviour

- **The banner value is set once, at scenario build time** (FR-4510) — there is no mechanism in
  the requirements baseline for changing it mid-session; a session's banner is fixed for its
  lifetime.
- **Every screen render includes the active banner** (FR-4510, NFR-3100) — this is a universal,
  no-exception display rule: no screen (White, Blue, Red, or Observer view) omits it.
- **Every exported file embeds the active banner** (FR-4510, NFR-3100) — this includes AAR exports
  and save files; an export produced during a session with banner X set displays/embeds banner X.
- **Default content carries no real classification marking** (NFR-3100's own Rationale) — the
  default banner values are themselves unclassified/fictional strings, consistent with the
  project's unclassified-by-design posture (GDS-00 §4).

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `content/vignette.py` (Content & Data) | Carries the classification banner value as a vignette-level field, set at scenario build time. |
| `ui_web/static/` (banner component) | Renders the active banner on every screen. |
| `session/aar.py` (export paths) | Embeds the active banner in every AAR export. |

## Interfaces Used

INT-0002 (White Cell Facilitator ↔ Operator Console, exercise control) — the scenario-build path
where the banner value is set. INT-0001 (Browser ↔ Operator Console) — every screen render across
every cell's browser client displays the banner over this interface.

## Data Model Changes

A classification-banner field on the Vignette/Session entity (per `docs/architecture/04-domain-
model.md`'s Vignette/Session model) — the requirements baseline does not name a specific field
structure beyond "a selected classification banner value," so this document does not assert one
(see Open Questions).

## State Changes

None beyond the one-time banner-value assignment at scenario build; the value does not transition
during a session's lifetime per the requirements baseline (see System Behaviour).

## Error Handling

The requirements baseline does not specify behavior for a vignette with no classification banner
value set (e.g., whether a default is silently applied or the load is rejected) — flagged as an
Open Question.

## Performance Considerations

None beyond NFR-3100's universal-rendering requirement — a single string rendered on every screen
carries no meaningful performance cost per the requirements baseline.

## Security Considerations

This Feature exists specifically *as* a safety-of-use control (per its own Purpose) rather than
introducing a new trust boundary: it is a labeling mechanism, not an access-control mechanism, and
does not itself gate any capability.

## Acceptance Criteria

- Given a session with banner X set, every screen render produced during that session
  displays banner X, with no screen omitting it.
- Given a session with banner X set, every AAR export and save file produced during that session
  embeds banner X.

## Verification Plan

Inspection — a static sweep across every UI screen-render path and every export path (AAR, save)
confirming none omits the active banner, consistent with FR-4510's own stated Verification Method
("the acceptance criteria... a review of every outbound interface" pattern shared with FR-4710 in
the same requirements category).

## Dependencies

[FS-115](FS-115-session-setup.md) (Session Setup: Vignette Selection & Seat Assignment) — the
scenario-build workflow this Feature's banner-value setting is part of, per `FEAT-4500`'s own
`Dependencies: FEAT-5100` in the Feature Catalog (FEAT-5100, In-App Iterative Vignette Builder, is
the mechanism; the White-Cell-facing setup workflow it's exercised through is FS-115).

## Risks

- **This Feature's build status is unconfirmed.** Unlike FS-109/FS-110/FS-111 (split from an
  existing, narratively-detailed FS-106), this Feature had no prior narrative description anywhere
  in the FS corpus to draw on — this specification is written directly from the requirements
  baseline and Feature Catalog entry, with no existing implementation description to verify
  against. Confirming it is actually built (per the RTM's own `UNASSIGNED` Impl. Package citation)
  is a prerequisite to trusting this document's Acceptance Criteria are already met, not just
  specified.

## Open Questions

- **Build status is unverified.** The RTM's Impl. Package column for FR-4510 is `UNASSIGNED`, and
  no prior FS document described this capability's implementation. Whoever owns the codebase should
  confirm against `ui_web/static/` and `session/aar.py` export paths before treating this as
  closed — if unbuilt, this specification is ready to hand to an Implementation Package; if built,
  the RTM citation gap should be closed separately.
- The exact Data Model field/structure for the classification-banner value is not specified by any
  approved architecture document — this specification does not invent one (see Data Model Changes).
- Behavior for a vignette with no classification banner value set is not specified in the
  requirements baseline.

## Related ADRs

None directly — the requirements baseline does not cite an ADR for this capability (consistent with
FR-4510's own "Related ADRs: (none directly)" field).

## Related Interfaces

INT-0002, INT-0001 — per `docs/design/05-interface-control-document.md` (both are also this
document's Interfaces Used).
