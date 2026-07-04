# IP-1120 — Classification Banner

> **Package ID:** IP-1120
> **Version:** 1.1 (2026-07-03 — implemented by `08-code-implementation`; see Status below.
> **Note:** the Status blockquote below still read `BLOCKED` as of the start of this implementation
> run, even though `IP-1150` had already reached `VERIFIED` on 2026-07-03 during an earlier run
> [run #3] — the Master Build Plan and `packages/INDEX.md` were correctly updated to `READY` at
> that time, but this package's own header text was not refreshed to match. `08-code-implementation`
> treated the Master Build Plan (the authoritative sequencing ledger) as controlling, proceeded on
> that basis, and corrects this document's own stale text as routine status bookkeeping in this
> same pass — not a design change.)
> **Status:** ✅ VERIFIED *(2026-07-04, [`VR-1120`](../verification/VR-1120-classification-banner.md)
> — every Definition of Done/Verification Checklist item confirmed against the live tree; full
> suite green (566 passed/3 skipped), both permanent gates green; RTM `FR-4510`/`NFR-3100`
> `Impl. Package` cells updated. Both documented Implementation Tasks deviations confirmed
> accurate, harmless, in-scope. One Low finding: the DoD text names a non-existent `aar.export_json`
> function (actual path is a FastAPI route dumping the same model) — informational only. Was 🔵
> COMPLETE *(implemented 2026-07-03 — one resolved `classification` value now flows
> from `Vignette.classification` (or a White-Cell override supplied at session setup) through
> `session/manager.py` to the UI-facing session-create/discovery responses, `aar.export_csv`, and
> `save_state`, replacing the prior hard-coded banner literal. Full suite green (519 passed/3
> skipped, up from 507/3 — 12 new tests), both permanent gates (`test_determinism.py`,
> `test_import_guard.py`) green. Entered `COMPLETE`, not `VERIFIED` — only `09-package-verification`
> may write `VERIFIED`.)* Was 🟡 READY *(authorized 2026-07-03, unblocked the same day once
> [IP-1150](IP-1150-vignette-selection.md) reached `VERIFIED` — MSTR-006 §3 authorization obtained
> 2026-07-03, project owner, recorded in `docs/pipeline/pipeline-journal.md` run #2).*)*)*
> **Dependencies:** FS-112, [IP-1150](IP-1150-vignette-selection.md) (vignette-selection/session-
> setup workflow this Feature's banner-value setting is part of, per FS-112's own Dependencies field)
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md)
> **Produces:** the banner string rendered on every screen and embedded in every export
> **Feature Reference:** [FS-112 — Classification Banner](../../features/FS-112-classification-banner.md)
> **Supersedes:** none — new package, first Implementation Package written against FS-112
> **Related Topics:** [`spacesim/content/vignette.py`](../../../spacesim/content/vignette.py),
> [`spacesim/ui_web/static/index.html`](../../../spacesim/ui_web/static/index.html),
> [`spacesim/session/aar.py`](../../../spacesim/session/aar.py),
> [`spacesim/session/manager.py`](../../../spacesim/session/manager.py)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*This package was authored after `07-implementation-planning`'s required build-status verification
pass (`docs/implementation/01-technical-work-breakdown.md` Tranche 1) found FS-112 **partially**
built — the vast majority of a full close-out is genuine gap-closing work, not documentation of
already-shipped behavior, so this package enters the forward-design status track
(`BLOCKED`/`READY`), not `VERIFIED`.*

## Package ID

IP-1120

## Title

Classification Banner — wire the rendered/exported banner to the vignette's classification value

## Objective

Make the classification banner FR-4510/NFR-3100 actually describe — replace the current
hard-coded, disconnected banner string with one that (a) is set from `Vignette.classification` at
scenario build time, (b) is selectable/overridable by White Cell in the session-setup UI, and (c)
is embedded in every AAR export and save file, not merely rendered on screen.

**Situation: partially built.** `Vignette.classification` (`content/vignette.py:47`) already exists
as a schema field with a documented default (`"UNCLASSIFIED-TRAINING"`), and every screen already
renders *a* banner string (`ui_web/static/index.html:96`) — but the two are not connected, there is
no White-Cell-facing control to set the value, and no export path embeds it. This package closes
that gap; it does not introduce the field or the on-screen banner slot, both of which already exist.

## Feature Reference

[FS-112 — Classification Banner](../../features/FS-112-classification-banner.md)

## Requirements Covered

| Req ID | Title (abridged) | How this package covers it |
|---|---|---|
| FR-4510 | Classification banner set and displayed | Adds a White-Cell-facing control to set/override `Vignette.classification` at session setup (alongside the existing parameter-override mechanism `IP-1150` already ships), and threads the resulting value from the loaded session through to every screen render, replacing the current hard-coded literal. |
| NFR-3100 | Classification banner on every screen and export | Extends the already-universal on-screen rendering (unchanged coverage — every screen already shows the header banner) to also cover `session/aar.py`'s `export_csv` and `session/manager.py`'s `save_state`, neither of which currently embeds any banner value. |

## Architecture Components

- **C5 Content & Data** — `content/vignette.py`'s `Vignette.classification` field (already exists,
  unmodified by this package).
- **C4 Operator Console** — `ui_web/static/` banner render slot (`index.html:96`) and a new
  session-setup control for selecting/overriding the value.
- **C2 Session / Application Layer** — `session/manager.py` (carries the active session's resolved
  classification value for the UI/export paths to read), `session/aar.py` (`export_csv`, and any
  markdown/JSON export path it grows).

## Interfaces

**INT-0002** (White Cell Facilitator ↔ Operator Console, exercise control) — the session-setup
path where the value is set/overridden. **INT-0001** (Browser ↔ Operator Console) — every screen
render across every cell's browser client, unchanged surface, now reading a real value instead of a
literal.

## Files to Create

None — every touch point already exists; this is a wiring/completion package.

## Files to Modify

- `spacesim/ui_web/static/index.html` — replace the hard-coded `<span class="banner">UNCLASSIFIED
  // TRAINING</span>` (`:96`) with a placeholder the client JS populates from the active session's
  resolved classification value.
- `spacesim/ui_web/static/app.js` — on session load/refresh, read the classification value the
  server returns and set the banner span's text; add a session-setup control (in the same panel
  `IP-1150`'s vignette-selection/parameter-override UI lives in) to override it before `Start`.
- `spacesim/ui_web/server.py` — surface the active session's resolved `classification` value on
  whatever response the client already polls for session state (e.g. alongside the existing
  `/api/sessions` load response), and accept an optional override on session creation.
- `spacesim/session/manager.py` — resolve and carry the session's active classification value
  (vignette default, or the White-Cell override if supplied at setup) so both the UI-facing read
  path and the export paths below read the same single source of truth.
- `spacesim/session/aar.py` — `export_csv` (`:120`) gains a `META` row carrying the active banner
  value; any future markdown/JSON AAR export this module grows must do the same (NFR-3100 is a
  no-exception, every-export rule).
- `spacesim/session/manager.py` — `save_state` (`:430`) gains a `classification` key in its
  returned dict; `from_state` (`:449`) is unaffected (the value is re-derived from the reloaded
  vignette/override, not itself replayed — see Data Model Changes below).

## Implementation Tasks

1. Add a `classification` (or override) field to whatever request model `ui_web/server.py`'s
   session-creation endpoint accepts, defaulting to the loaded vignette's own
   `Vignette.classification` when not supplied.
2. Resolve the session's active classification value once, at session construction, in
   `session/manager.py` — store it alongside `self.ctx` so every downstream reader (UI poll,
   `aar.export_csv`, `save_state`) reads the same resolved value, never re-deriving it
   independently (avoids the two-sources-of-truth failure mode this package is closing).
3. Surface the resolved value on the session-state response `ui_web/static/app.js` already polls;
   have the client set the banner span's text from it instead of the current literal.
4. Add a minimal session-setup control (dropdown or text field, White-Cell-only per FR-4510's own
   "White Cell selects... at scenario build time" workflow) for overriding the classification value
   before `Start`, in the same UI region `IP-1150`'s vignette/parameter-override controls live in.
5. Embed the resolved value in `aar.export_csv`'s `META` section and in `save_state`'s returned
   dict.
6. Confirm no export path in `session/aar.py` or `session/manager.py` is missed — NFR-3100 is
   explicitly a no-omission rule, not a best-effort one.

**Implementation notes (2026-07-03, added by `08-code-implementation`, two deliberate deviations
from this section's literal text above — both within `session/manager.py`, an already-in-scope
file, not a scope expansion):**

- **Task 3's "session-state response `app.js` already polls"** turned out to be ambiguous once
  actually implemented: `app.js`'s periodic `refresh()` loop uses `/godview` (White) or
  `/view/{cell}` (Blue/Red/Observer) — both fog-filtered, frequently-repolled structures not
  natural homes for a value FS-112 itself states is "fixed for its lifetime." A joining/pop-out tab
  (`joinSessionFromHash()`) never calls either of those on join — it reads `GET /api/sessions`
  (`list_sessions()`). Continuously re-polling a value that never changes would also have been
  wasted work. The shipped design instead surfaces `classification` on the one-time
  `POST /api/sessions` response (for the creating tab) **and** on `list_sessions()` (for a joining
  tab) — both already read `SessionManager.classification`, the same single resolved value, so this
  is a different *transport* choice than the sketch above, not a different *source of truth*.
- **Task 6 / "Files to Modify"'s claim that `from_state` is "unaffected"** was not followed: without
  restoring the saved `classification` key on resume, a saved-then-reloaded session would silently
  revert to the vignette's default banner, contradicting FS-112's own "fixed for its lifetime"
  System Behaviour and partly defeating the point of `save_state` embedding the value at all. This
  package's own Rollback Considerations already anticipated `from_state` tolerating the key's
  *absence* (old saves) — the shipped `from_state` does that (via `.get(...)`) while also restoring
  it when present, which strictly implements DoD item "the call sites all read one resolved
  value... never re-deriving it independently" more completely than the literal task text asked for.

## Tests to Add

- `spacesim/tests/test_content.py` or a new `test_classification_banner.py` — a test asserting a
  session loaded with a non-default classification override resolves to that value (not the
  vignette's default), mirroring the existing `test_parameter_override_flows_into_roe` pattern
  (`test_content.py:62`).
- A test asserting `aar.export_csv(rep)` output contains the session's active classification value
  in its `META` section for a session built with a non-default override.
- A test asserting `SessionManager.save_state()`'s returned dict contains the session's active
  classification value.
- No client-side (JS) test is proposed — consistent with this project's existing pattern of no
  automated coverage for `ui_web/static/` (browser GUI is unverified headless per `CLAUDE.md`);
  this remains a manual/inspection check per FR-4510's own stated Verification Method ("Test" for
  the data-layer pieces above, "Inspection" per NFR-3100 for the on-screen render itself, matching
  the sweep pattern FR-4510's Verification Plan already describes).

## Documentation Updates

- `ROADMAP.md` Implementation Packages theme — add this package's row.
- `CLAUDE.md`'s Code Map — no entry needed (no new module; existing entries for
  `content/vignette.py`, `session/aar.py`, `ui_web/static/` already cover the touched files).
- `docs/features/FS-112-classification-banner.md`'s `Referenced By` metadata — add this package
  (cross-link only, per this skill's Step 4; the FS's content is unmodified).

## Definition of Done

*(Implemented 2026-07-03 by `08-code-implementation` — every item below is now satisfied against
the shipped code and tests; `09-package-verification` independently re-confirms this before the
package may advance to `VERIFIED`.)*

- [x] **Explicit user authorization obtained** for this package's Implementation Tasks (MSTR-006
  §3, 2026-07-03, project owner, recorded in `docs/pipeline/pipeline-journal.md` run #2).
  [IP-1150](IP-1150-vignette-selection.md) reached `VERIFIED` 2026-07-03 (run #3, `VR-1150`),
  clearing the dependency gate this item used to note as still open.
- [x] A session's on-screen banner reflects `Vignette.classification` (or a White-Cell override),
  not a hard-coded literal, on every screen — set once from the server's resolved value (the
  create response for the creating tab, `list_sessions()` for a joining/pop-out tab), matching
  FR-4510's "fixed for its lifetime" semantics; no continuous re-polling needed since the value
  never changes mid-session (see Implementation Tasks note below on this design choice).
- [x] A White-Cell-facing control exists to set/override the classification value at session setup
  (a text input in the same Session ▾ menu `IP-1150`'s vignette/seed controls live in).
- [x] `aar.export_csv` embeds the session's active classification value (a new `AARReport.classification`
  field, populated by `aar.report()`); `aar.export_json` (which dumps the same `AARReport`) picks it
  up automatically, with no omission.
- [x] `save_state`'s returned dict carries the active classification value; `from_state` restores it
  on resume (an addition beyond the package's literal "from_state is unaffected" text — see
  Implementation Tasks note below).
- [x] The call sites (session-create response, `list_sessions()`, `export_csv`, `save_state`) all
  read the one value `SessionManager.classification` resolves once at construction, never
  re-deriving it independently.

## Verification Checklist

- [ ] New/updated tests in `test_content.py` (or `test_classification_banner.py`) pass.
- [ ] `python3 -m pytest spacesim/tests/test_determinism.py` remains green (this package touches no
  engine state and must not begin to).
- [ ] `python3 -m pytest spacesim/tests/test_import_guard.py` remains green (no new engine import
  is introduced by this package's `session/`/`ui_web/` changes).
- [ ] Manual inspection: every screen in the running UI shows the resolved banner value, not the
  literal `UNCLASSIFIED // TRAINING` string, when a session is built with a non-default override.
- [ ] Manual inspection: a downloaded AAR CSV export and a downloaded save file both contain the
  session's active classification value.

## Dependencies

- **Upstream:** [IP-1150](IP-1150-vignette-selection.md) (the session-setup/vignette-load
  mechanism this package's setup control extends) — `VERIFIED` 2026-07-03 (`VR-1150`, run #3); this
  package's dependency gate cleared that same day.
- **Downstream:** None in this pass.
- **Build-sequencing:** Sequenced after `IP-1150` reached `VERIFIED`, as planned; not on this plan's
  critical path (see `00-master-build-plan.md`).

## Risks

- **Authorization risk (resolved 2026-07-03):** MSTR-006 §3's explicit, separate user go-ahead is
  now on record in the pipeline journal, and `IP-1150` reached `VERIFIED` the same day — both
  former gates are cleared; this package is now implemented (`COMPLETE`).
- **Two-sources-of-truth risk (mitigated by design, not merely avoided):** `SessionManager.classification`
  is resolved exactly once, at construction, and every reader (session-create response,
  `list_sessions()`, `aar.export_csv`, `save_state`) reads that one attribute — including
  `set_parameter()`'s pre-start manager-reconstruction path, which explicitly re-passes the current
  `classification` forward (a case this Risk's original wording didn't call out by name, but which
  the same failure mode applies to).
- **RTM title-mismatch, routed upstream, not fixed here:** `docs/requirements/03-requirements-
  traceability-matrix.md` row for `FR-4510` currently lists its Title column as "Observer view" —
  a copy/paste defect (the correct title, "Classification banner set and displayed," is what
  `docs/requirements/01-functional-requirements.md:824` — the RTM's own source of truth — states).
  This does not block authoring this package (the FR's content, not the RTM's title-column
  restatement, is authoritative), but is flagged here for whoever next touches the RTM
  (`04-requirements-engineering`'s territory, not this skill's to fix) — left untouched by
  `08-code-implementation` for the same reason (Test/Impl. Package cells only, per its own scope
  discipline).
- **`NFR-3100`'s own RTM row was separately malformed (missing its `Impl. Package` column
  entirely), discovered while updating it — corrected as part of filling in this package's own
  citation** (the same row, not a different one), not a broader RTM sweep.

## Rollback Considerations

Rollback surface is small and additive: the new setup control, the server-side override field, and
the three read/embed call sites. Reverting drops back to the current (defective but harmless)
hard-coded-banner behavior — no data migration, no save-file schema break (the `classification` key
`save_state` gains is additive; `from_state` does not require it to be present, so old save files
remain loadable).
