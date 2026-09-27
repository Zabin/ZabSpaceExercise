> **Document ID:** FS-118
> **Version:** 1.0
> **Status:** ✅ Ready for implementation planning
> **Note on this repository's chain:** no `05-feature-decomposition` Feature Catalog exists here
> (per this skill's own Gotchas); this document's approved input is the just-baselined
> requirements themselves — `docs/requirements/01-functional-requirements.md` `FR-5410`/`FR-5420`,
> `docs/requirements/02-non-functional-requirements.md` `NFR-3700` — plus the real baseline code
> those requirements cite (`spacesim/content/vignette.py`, `spacesim/content/vignette_export.py`,
> `spacesim/config.py`).
> **Dependencies:** [FS-117](FS-117-vignette-creator.md) (`FR-5110`/`IP-1173` — the draft-save
> capability `FR-5420` is explicitly distinct from, not a variant of), `FR-5310` (load-time vignette
> validation, unchanged by this Feature)
> **Referenced By:** [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0082` (external
> validation report, 26 Sep 2026, item B16), [docs/requirements/01-functional-requirements.md](../requirements/01-functional-requirements.md)
> `FR-5410`/`FR-5420`, [docs/requirements/02-non-functional-requirements.md](../requirements/02-non-functional-requirements.md)
> `NFR-3700`, [IP-1180](../implementation/packages/IP-1180-external-vignette-directories.md)
> (Implementation Package, `NOT STARTED`, not yet authorized)
> **Produces:** an external-vignette-directory load path and a safe, user-directory-scoped
> save-as-scenario write target, satisfying `FR-5410`/`FR-5420`/`NFR-3700` in full
> **Feature Mapping:** FS-118 (this document)
> **Related Topics:** [FS-110](FS-110-save-and-resume.md) (`ADR-0022` save-file ownership split —
> a structurally similar "where does a write actually land" precedent), [ADS-1500](../architecture/ADS-1500-per-cell-custody-estimated-state-and-export.md)
> (unrelated capability, same increment — cited only because both were authored in the same
> Must-tier intake batch, per `docs/pipeline/pipeline-journal.md` run #61-#62)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template.*

# FS-118 — External Vignette Directories & Safe Scenario Save Target

## Purpose

Let a user keep authored/derived vignette scenarios outside the source tree — in one or more
directories they configure — while loading them alongside the built-in library, and let any
save-producing capability (this Feature's own future save-as-scenario work, `BL-0071`/`FR-5510`;
today's Vignette Creator draft save, `FS-117`) write only into a directory the user configured for
that purpose, never into the built-in `VIGNETTE_DIR`. `FR-5410`'s own Rationale states the need
directly: the baseline hard-codes a single load directory and a save path that writes into the
built-in library itself, which is unsuitable once a user wants scenarios that persist independent
of the installed source tree.

## Scope

**In scope:** (1) loading vignettes from zero or more externally-configured directories, listed
as a group distinct from the built-in library, per `FR-5410`; (2) restricting `save_vignette` (and
any future save-as-scenario capability built on the same write path) to a configured user
directory, per `FR-5420`; (3) generalizing the existing `load_vignette` path-traversal guard to
every content root this Feature introduces, per `NFR-3700`.

**Out of scope (named, not silently absorbed):** the save-as-scenario capability's own *content*
(what a saved scenario carries — tracks, resources, health, space-weather, version stamp) is
`BL-0071`/`FR-5510`'s scope, a separate Feature Specification; this document only specifies *where*
any such save lands and generalizes the traversal guard it must obey. The Vignette Creator's
existing draft-save mechanism (`FS-117`, `IP-1173`) is unchanged by this Feature — it is named here
only to state explicitly that this Feature's user-directory write target and that mechanism's
existing behavior are two different things (see Open Question 1).

## Requirements Implemented

- `FR-5410` — Load vignettes from configured external directories.
- `FR-5420` — `save_vignette` writes only to a configured user directory, with no path traversal.
- `NFR-3700` — Path-traversal safety generalized to external content roots.

## User Workflows

1. **White Cell configures an external vignette directory.** White Cell (or whoever administers
   the deployment) adds one or more directory paths to `spacesim.config.yaml` (or the equivalent
   environment-variable override, per `spacesim/config.py`'s existing `SPACESIM_CONFIG` convention)
   under a new configuration key for external vignette sources, and a separate key for the
   configured user-save directory.
2. **White Cell opens the vignette-selection interface.** The interface (the existing
   vignette-selection surface `FR-4110` already provides) presents two groups: the built-in
   library (unchanged) and, for each configured external directory, its own labeled group of
   vignettes found there.
3. **White Cell selects an external vignette and starts a session.** Loading proceeds exactly as
   for a built-in vignette (`FR-5310`'s existing load-time validation applies unchanged, regardless
   of which directory the file came from).
4. **A save-producing capability writes a vignette file.** Whether the write is today's `FS-117`
   draft save or a future `FR-5510` save-as-scenario action, the write target is resolved against
   the configured user-save directory, never `VIGNETTE_DIR`; an identifier containing a traversal
   token is rejected before any filesystem access, exactly as `load_vignette`'s existing guard
   already does for the load path.
5. **A vignette id collides between the built-in library and a configured external directory.**
   The system resolves this deterministically and discloses which one was selected (`FR-5410`'s own
   Postcondition) — the interface does not silently prefer one over the other without saying so.

## System Behaviour

- **Normal path — load.** The vignette catalog (whatever code path today enumerates `VIGNETTE_DIR`,
  per `spacesim/content/vignette.py`) is extended to also enumerate each configured external
  directory, tagging each resulting entry with its origin (built-in vs. named external directory).
  No configured external directory: catalog behavior is unchanged from baseline (`FR-5410`'s own
  Acceptance Criteria).
- **Edge case — external directory unreadable or absent.** Not addressed by `FR-5410`'s own
  Preconditions beyond "if any, exists and is readable" — see Open Question 2.
- **Normal path — save.** `save_vignette` (or an equivalent future save path) resolves its target
  directory to the configured user-save directory rather than `VIGNETTE_DIR`, and applies the same
  identifier-charset/traversal check `load_vignette` already applies (`spacesim/content/vignette.py`
  lines 140-153), generalized to run against the user-save directory's own resolved root instead of
  (or in addition to) `VIGNETTE_DIR`'s.
- **Edge case — traversal identifier submitted to the save path.** Rejected before any filesystem
  call, identically to how `load_vignette` already rejects one on the load path (`FR-5420`'s own
  Acceptance Criteria; `NFR-3700`'s verification method).
- **Edge case — no user-save directory configured.** Not addressed by `FR-5410`/`FR-5420`'s own
  text — see Open Question 3.

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| `content/` (`spacesim/content/vignette.py`) | Owns the vignette catalog enumeration; extended to read from configured external directories in addition to `VIGNETTE_DIR`, tagging each entry's origin. Owns the existing traversal guard (`load_vignette` lines 140-153) this Feature generalizes. |
| `content/` (`spacesim/content/vignette_export.py`) | Owns `save_vignette`'s write target; changed to resolve against the configured user-save directory instead of `VIGNETTE_DIR`. |
| `spacesim/config.py` | Owns the `spacesim.config.yaml`/`SPACESIM_CONFIG` configuration surface this Feature's new external-directories list and user-save-directory value are read from, extending the existing `ServerConfig`-style pattern (a new config section, not a new file format). |
| Operator Console (`ui_web/`) | Presents the two-group (built-in / external) vignette-selection list; no fog-of-war concern (White-Cell-only surface, consistent with every other scenario-authoring surface, `ADR-0004`). |

## Interfaces Used

- `INT-0011` (Session Layer → Content & Data, vignette/template load) — the existing interface this
  Feature's load-path extension operates through; no new interface introduced. **Note:** the
  Requirements Review already flagged (`docs/reviews/requirements-update-must-tier-batch.md`, not a
  finding against this specific ICD entry) that some sibling Must-tier items stretch `INT-0011`'s
  documented shape; this Feature's own use (multiple directories, same load semantics) is a closer
  fit and does not itself require an ICD edit.
- `INT-0012` (Session Layer → Content & Data / Filesystem, save round trip) — the existing interface
  `FR-5420`'s user-directory-scoped write operates through.

## Data Model Changes

None to the Domain Model (`GDS-04`) itself. This Feature is a configuration-surface and
filesystem-path change, not a new entity — the vignette catalog gains an "origin" tag per entry
(built-in vs. named external directory), which is presentation/bookkeeping metadata, not a new
domain concept.

## State Changes

None to session/persistent engine state. The only new "state" this Feature introduces is the
configuration file's own new section (external directories list; user-save directory), read once at
startup per the existing `spacesim/config.py` pattern — not a runtime-mutable session state.

## Error Handling

- A configured external directory that does not exist or is not readable: behavior not specified by
  the baselined requirements (Open Question 2) — this document does not invent one.
- A vignette id collision between the built-in library and an external directory: resolved
  deterministically and disclosed (`FR-5410`'s Postcondition) — the specific resolution rule (e.g.
  built-in wins, external wins, first-configured-directory wins) is not stated in the requirement
  and is Open Question 4.
- A save request with a traversal-token identifier: rejected before any filesystem access, with a
  specific reason distinguishable from a generic failure (mirroring `FR-5310`'s existing "invalid
  scenario data fails loudly" posture for the load path).
- No user-save directory configured: not specified (Open Question 3).

## Performance Considerations

None named by `FR-5410`/`FR-5420`/`NFR-3700` — enumerating a small number of additional directories
at catalog-build time is not a performance-sensitive path relative to the existing single-directory
enumeration it extends.

## Security Considerations

- `NFR-3700` is this Feature's core security requirement: the existing `load_vignette` traversal
  guard (reject a path separator, `..`, an absolute-path marker, or a disallowed character, without
  touching the filesystem, then re-verify the resolved path lives inside the intended root) must
  apply identically to every external directory and to the user-save directory — no content root
  this Feature adds may be reachable by an identifier the existing guard would already reject
  against `VIGNETTE_DIR`.
- `NFR-2200` (secure development practice, "input validation on all loaded files") already commits
  to this posture for the single existing content root; this Feature is `NFR-2200`'s posture applied
  to the newly-plural set of roots, not a new security posture.
- `ADR-0018` (offline-first runtime): loading from a local, user-configured directory introduces no
  network dependency — consistent with the existing invariant.

## Acceptance Criteria

1. Given a configured external directory containing a valid vignette file, that vignette appears in
   the selection interface labeled as external, distinct from the built-in-library group; given no
   configured external directory, behavior is unchanged from baseline. *(`FR-5410`)*
2. Given a vignette identifier containing `../` or an absolute path submitted to the save path, the
   request is rejected before any filesystem access occurs; given a valid identifier, the file is
   written to the configured user-save directory, never `VIGNETTE_DIR`. *(`FR-5420`, `NFR-3700`)*
3. A traversal identifier already rejected by the existing `load_vignette` guard against
   `VIGNETTE_DIR` is also rejected, with no filesystem access, against every configured external
   directory and the configured user-save directory. *(`NFR-3700`)*

## Verification Plan

- Criterion 1 — Test: a fixture external directory with a valid vignette file; assert it appears
  labeled correctly in the catalog; assert an empty configuration reproduces baseline behavior
  byte-for-byte.
- Criterion 2 — Test: parametrized over traversal-token identifiers (path separator, `..`, absolute
  path, disallowed character) submitted to the save path; assert rejection with no filesystem
  mutation, then assert a valid identifier lands in the configured user-save directory.
- Criterion 3 — Test: the same traversal-token parametrization run against each of (a) `VIGNETTE_DIR`
  (existing behavior, regression-only), (b) a configured external directory, (c) the configured
  user-save directory — asserting identical rejection behavior across all three.

## Dependencies

- `FS-117` (Vignette Creator) — not a build dependency (this Feature does not require `FS-117`'s
  code to exist), but a *scope* dependency: `FS-117`'s existing `save_vignette`/draft-save behavior
  is the thing `FR-5420` changes the write target of, so an Implementation Package for this Feature
  must coordinate with wherever `FS-117`'s `IP-1173`/`IP-1174` left that write path.
- `FR-5310` (load-time vignette validation) — unchanged, but every vignette this Feature loads
  (built-in or external) still passes through it.

## Risks

- **Ambiguity risk (Open Questions 2-4 below).** Three genuine gaps in the baselined requirements'
  own text mean an Implementation Package cannot fully commit to edge-case behavior without a
  requirements-level or design-level answer first.
- **Coordination risk with `FS-117`.** `FR-5420` changes `save_vignette`'s write target, a function
  `IP-1173`/`IP-1174` (both `FS-117`'s) already implement and (for `IP-1173`) have `VERIFIED`. An
  Implementation Package for this Feature must treat that existing, verified code as something to
  *modify* (the write-target resolution), not something to reimplement — a naive from-scratch
  reimplementation risks silently dropping behavior `IP-1173`'s own tests already lock in.

## Open Questions

1. **Is the Vignette Creator's existing draft save (`FS-117`, `IP-1173`'s `save_vignette`) the same
   code path `FR-5420` changes, or a distinct save mechanism this Feature must also apply its
   user-directory restriction to separately?** `FR-5420`'s own Description names `save_vignette`
   explicitly (the same function `IP-1173` implemented), suggesting it is the same code path — but
   neither `FR-5420` nor `FS-117` states this as a settled fact, only as parallel citations. This
   matters because an Implementation Package needs to know whether it is modifying one function's
   write-target resolution or reconciling two. Resolving this needs a direct read of `IP-1173`'s
   as-shipped code at implementation-planning time — not something this specification-level
   document can settle from the requirements text alone.
2. **What is the observable behavior when a configured external directory does not exist or is not
   readable at catalog-build time?** `FR-5410`'s Precondition states "if any, exists and is
   readable" but its own System Behaviour/Acceptance Criteria do not say what happens when that
   precondition is violated (silently skip the bad directory? fail the whole catalog build? surface
   a warning to White Cell?). Needs a `04-requirements-engineering` amendment or an explicit
   `07-implementation-planning` design decision — this document does not invent one.
3. **What is the observable behavior of a save request when no user-save directory is configured
   at all?** Neither `FR-5410` nor `FR-5420` states whether this is an error (reject the save
   entirely), a fallback (e.g. reject with a specific "configure a user-save directory first"
   message), or something else. Same resolution path as Open Question 2.
4. **What is the deterministic tie-break rule when a vignette id collides between the built-in
   library and a configured external directory (or between two external directories)?** `FR-5410`'s
   Postcondition requires the collision be "resolved deterministically and disclosed," but does not
   state the rule itself (built-in wins? first-configured-directory wins? reject the collision
   outright and require unique ids?). This is squarely a design decision an Implementation Package
   needs a concrete answer to before it can write a single, unambiguous resolution function.

## Related ADRs

`ADR-0007` (content as data, not code — this Feature's directories still hold plain YAML vignette
files, no new content format); `ADR-0018` (offline-first runtime); `ADR-0022` (save-file ownership
split — the precedent for treating "where a save lands" as its own architecturally-meaningful
question, though `ADR-0022` itself concerns session-save/content ownership, a different split from
this Feature's built-in-vs-external-vs-user-directory question).

## Related Interfaces

`INT-0013` (Content & Data → Space-Track.org, TLE import) — unrelated to this Feature's own scope,
listed only because it is the interface `FR-5220` (a sibling Must-tier Feature, bulk TLE/OMM import)
uses and the Requirements Review already flagged as ICD-stretched; no relationship to this Feature's
own load/save paths.
