# IP-1150 — Session Setup: Vignette Selection & Parameter Tuning

> **Package ID:** IP-1150
> **Version:** 1.0
> **Status:** 🔵 COMPLETE *(implementation exists, tested, in production use; entered `COMPLETE`,
> not `VERIFIED`, per this skill's rule that an as-built package may be born `VERIFIED` only after
> an actual `09-package-verification` pass — this authoring pass confirmed the cited code and test
> exist, but is not that independent pass.)*
> **Dependencies:** FS-115 (FR-4110 slice)
> **Referenced By:** [IP-1120](IP-1120-classification-banner.md), [IP-1151](IP-1151-seat-role-assignment.md) (both `BLOCKED` on this package reaching `VERIFIED`), [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** the loaded, parameter-resolved Session every other package in this plan's session
> layer builds on
> **Feature Reference:** [FS-115 — Session Setup: Vignette Selection & Seat Assignment](../../features/FS-115-session-setup.md) (FR-4110 portion)
> **Supersedes:** none — new package, first Implementation Package written against FS-115
> **Related Topics:** [`spacesim/session/manager.py`](../../../spacesim/session/manager.py),
> [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py),
> [`spacesim/tests/test_content.py`](../../../spacesim/tests/test_content.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*FS-115 covers two Feature Catalog entries (`FEAT-4100` vignette selection, `FEAT-4200` seat
assignment). This package covers only the `FEAT-4100`/FR-4110 half, which `07-implementation-
planning`'s build-status verification pass
(`docs/implementation/01-technical-work-breakdown.md` Tranche 1) found already built and tested.
The `FEAT-4200`/FR-4210 half (seat-to-role assignment against `roles_needed`) is not built at all
and is covered separately by [IP-1151](IP-1151-seat-role-assignment.md) — see that package and the
TWBS for the split rationale.*

## Package ID

IP-1150

## Title

Session Setup: Vignette Selection & Parameter Tuning (FS-115, FR-4110 slice)

## Objective

Document the existing vignette-selection-with-tunable-parameters mechanism against FR-4110's
Acceptance Criteria: a White Cell facilitator can select a vignette and optionally override its
declared parameters, and every parameter left unmodified takes its documented default.

**Situation: already implemented, tested, in production use.**

## Feature Reference

[FS-115 — Session Setup: Vignette Selection & Seat Assignment](../../features/FS-115-session-setup.md) (FR-4110 portion only — see IP-1151 for FR-4210)

## Requirements Covered

| Req ID | Title (abridged) | How this package covers it |
|---|---|---|
| FR-4110 | Vignette selection with tunable, defaulted parameters | `content/vignette.py`'s `list_vignettes()` (`:94`) and `load_vignette()` (`:112`) supply the selectable catalog; `Vignette.parameters` (`content/vignette.py:61`, a `list[Parameter]`) declares each tunable dial with its own `default` (`:32`); `SessionManager.__init__` (`session/manager.py:35`) accepts an `overrides: Optional[dict]` and resolves it via `build_world(vignette, overrides)` into `self.ctx.param_values`, from which every unmodified parameter is read at its declared default. `spacesim/tests/test_content.py:62` (`test_parameter_override_flows_into_roe`) confirms an override actually changes resolved behavior (ROE), and by construction (the same resolution path) an *absent* override leaves the declared default in effect. The web layer accepts overrides on session creation (`ui_web/server.py:201` `POST /api/sessions`, exercised by `spacesim/tests/test_web.py:186` with `{"overrides": {"ssn_blue_dispersion": "regional"}}`). |

## Architecture Components

- **C5 Content & Data** — `content/vignette.py`'s `Vignette`/`Parameter` schema and
  `list_vignettes()`/`load_vignette()` loaders.
- **C2 Session / Application Layer** — `session/manager.py`'s `SessionManager.__init__` and the
  parameter-resolution path into `VignetteContext.param_values`.
- **C4 Operator Console** / **C6 White Cell** — `ui_web/server.py`'s `POST /api/sessions` endpoint
  and the vignette-selection panel in `ui_web/static/app.js` (`app.js:162`, `GET /api/vignettes`).

## Interfaces

**INT-0002** (White Cell Facilitator ↔ Operator Console, exercise control) — the sole interface
FS-115 names for both vignette selection and seat assignment; this slice covers the
vignette-selection half of that surface.

## Files to Create

None — capability already implemented.

## Files to Modify

None — this package documents shipped code.

### Reference files

- `spacesim/content/vignette.py:25-33` (`Parameter` model, `default` field), `:44-77` (`Vignette`
  model), `:94-109` (`list_vignettes`), `:112-` (`load_vignette`).
- `spacesim/session/manager.py:35-` (`SessionManager.__init__`, `overrides` parameter,
  `build_world(vignette, overrides)` call).
- `spacesim/ui_web/server.py:172-173` (`GET /api/vignettes`), `:201` (`POST /api/sessions`).
- `spacesim/tests/test_content.py:62` (`test_parameter_override_flows_into_roe`).
- `spacesim/tests/test_web.py:186` (session creation with `overrides` in the request body).

## Implementation Tasks

All **already complete**:

1. ✅ Implement a `Vignette.parameters` schema (`Parameter` model with a `default` field) so every
   tunable dial has a documented default value.
2. ✅ Implement `SessionManager.__init__`'s `overrides` parameter, resolved into
   `VignetteContext.param_values` such that an unmodified parameter takes its declared default.
3. ✅ Expose vignette listing/loading and override submission over `ui_web/server.py`'s
   `/api/vignettes` and `/api/sessions` endpoints.
4. ✅ Cover override-flows-through-to-behavior with an automated test
   (`test_parameter_override_flows_into_roe`).

## Tests to Add

None — covered by the existing `test_parameter_override_flows_into_roe`
(`spacesim/tests/test_content.py:62`) and `test_web.py`'s session-creation-with-overrides coverage
(`:186`). *(Optional, not required for this package's Definition of Done: a dedicated test
asserting that a vignette loaded with **zero** overrides resolves every parameter to its declared
default — the current test coverage exercises the override path, not the explicit
no-override-means-default path FR-4110's Acceptance Criteria states verbatim. Flagged for
`09-package-verification` to assess as a coverage gap, not authored here since it is not required
to document already-shipped behavior.)*

## Documentation Updates

- `ROADMAP.md` Implementation Packages theme — add this package's row.
- `docs/features/FS-115-session-setup.md`'s `Referenced By` metadata — add this package
  (cross-link only; note the metadata should point to both `IP-1150` and `IP-1151`, mirroring how
  `FS-105`'s metadata points to both `IP-1050` and `IP-1051`).

## Definition of Done

- [x] A vignette can be selected and loaded with optional parameter overrides.
- [x] Every parameter left unmodified resolves to its documented default value.
- [x] Automated test coverage exists for the override-changes-behavior path.

## Verification Checklist

- [x] `content/vignette.py:25-33,44-77,94-109,112-`, `session/manager.py:35-`,
  `ui_web/server.py:172-173,201` read and confirmed against the current tree.
- [x] `spacesim/tests/test_content.py:62` present and (per this authoring pass's reading) exercises
  the Acceptance Criteria's override behavior.
- [ ] `09-package-verification` should re-run `python3 -m pytest spacesim/tests/test_content.py
  spacesim/tests/test_web.py` and confirm green, and assess the optional no-override-default
  coverage gap noted in Tests to Add.

## Dependencies

- **Upstream:** None beyond the engine's own content-loading path (already shipped, out of this
  pass's package scope).
- **Downstream:** [IP-1120](IP-1120-classification-banner.md) (extends this package's session-setup
  UI region with a classification-override control) and [IP-1151](IP-1151-seat-role-assignment.md)
  (the seat-assignment slice of the same Feature, sequenced after vignette selection per FR-4210's
  own Preconditions: "A Vignette is loaded (FR-4110)") both stay formally `BLOCKED` until this
  package reaches `VERIFIED`.
- **Build-sequencing:** Should be the first of this tranche's five packages to clear
  `09-package-verification`, since two others are blocked on it.

## Risks

- **This package's own build-status verification was performed by this authoring pass, not by an
  independent `09-package-verification` run** — per this skill's status-vocabulary rule, that keeps
  it at `COMPLETE`, not `VERIFIED`, even though the evidence is strong (a passing, on-point
  automated test plus direct code reading). Downstream packages' formal `BLOCKED` state is a direct
  consequence of this, not a sign of a functional problem.
- **No test currently exercises the explicit "zero overrides → all defaults" path** — see Tests to
  Add. This is a coverage gap, not a known behavioral defect (the resolution mechanism is uniform
  regardless of whether an override is present), but should not be silently assumed equivalent to
  having a test for it.

## Rollback Considerations

Not applicable in the ordinary sense — this package proposes no code change. If future work reveals
a defect in the resolution path, rollback would mean reverting to the vignette's declared defaults
being used unconditionally (i.e. the override mechanism itself), which is bounded to
`session/manager.py`'s `overrides` parameter and its call sites in `ui_web/server.py`.
