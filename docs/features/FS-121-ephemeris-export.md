> **Document ID:** FS-121
> **Version:** 2.3 (2026-10-31 — adds `FR-7450` (ISO-8601 UTC span bounds on the three time-span exports, owner decision to build before release, `BL-0181`); the span-bound parser is owned here and shared with `FS-126`. All `FR-7410`–`FR-7440` content unchanged.) Prior: 2.2 (2026-10-17 — `FR-7410`/`FR-7420` restated upstream as one asset per export
> (`BL-0137`); User Workflows 1–2 follow (`BL-0262`). Nothing else changed.) Prior: 2.1 (2026-10-15 — `FR-7440` amended upstream (`BL-0159`): a cell's **own** satellites
> are now in scope; the fields that amendment affects are updated and Open Question 5 is closed.
> Nothing else changed.) Prior: 2.0 (2026-10-10 — extended to cover all of `FEAT-7400`: adds `FR-7440` (quick TLE
> export, `BL-0109`) and records `FR-7430` (companion RIC file, already built/`VERIFIED` under
> `IP-1210`, closing the RTM's "FS-121 (amendment pending)" note). The `FR-7410`/`FR-7420` content
> of v1.0 is unchanged in substance.)
> **Status:** 🟢 Ready for new work — `FR-7410`–`FR-7440` built (`IP-1210`, `IP-1211`, `IP-1212`, `IP-1261`, `IP-1262` all `VERIFIED`); `FR-7450` (v2.3) is specified and unbuilt, awaiting an Implementation Package.
> *(Status line updated 2026-10-17, pipeline run #163, `BL-0200`: it described the spec's readiness for planning, which lagged the built Feature. Open Questions recorded below are historical unless marked otherwise; the cited package's Design Decisions record how each was settled where the build needed it.)*
> **Note on this repository's chain:** v1.0's approved input was `FR-7410`/`FR-7420` directly ("no
> Feature Catalog exists here"). As of v2.0 the approved input **is** a real Feature Catalog entry —
> `FEAT-7400` in [`docs/feature-planning/03-feature-catalog.md`](../feature-planning/03-feature-catalog.md)
> (run #83, 2026-10-03), whose `Included Requirements` are `FR-7410`-`FR-7440`. This document is
> extended in place (not a new FS) because one Feature maps to one Feature Specification and FS-121
> already owns three of `FEAT-7400`'s four leaves. `Purpose`/`Scope`/`Dependencies`/`Affected
> Subsystems`/`Related ADRs` for the `FR-7440` additions are carried forward from that entry.
> **Dependencies:** [FS-103](FS-103-custody-management.md) v1.1 (`Track.state_estimate`'s confirmed
> independence from truth, and the replay-based history mechanism `FR-7420` reuses), [FS-107](FS-107-after-action-review.md)
> (`FR-7310`/`session/aar.py::state_at` — the replay mechanism both `FR-7410`'s and `FR-7420`'s
> time-span sampling are built on), `FR-6220` (no-cell ground-truth endpoints, the binding `FR-7410`
> must use), `FR-6210` (fog-of-war, the binding `FR-7440`'s cell-scoped path must use)
> **Referenced By:** [docs/pipeline/backlog.md](../pipeline/backlog.md) `BL-0069` (external
> validation report, 26 Sep 2026, item B3), `BL-0109` (quick TLE export request), `BL-0110` (the
> TLE-generation design question), [IP-1210](../implementation/packages/IP-1210-ephemeris-export.md)
> (Implementation Package for `FR-7410`-`FR-7430`, ✅ `VERIFIED` 2026-09-28),
> [IP-1211](../implementation/packages/IP-1211-quick-tle-export.md) (Implementation Package for `FR-7440`, ✅ `VERIFIED`, [VR-1211](../implementation/verification/VR-1211-quick-tle-export.md)),
> [IP-1261](../implementation/packages/IP-1261-telemetry-series-history-remediation.md) (remediation package — migrates `FR-7410`/`FR-7420`'s time-span sampling onto a shared single-pass replay helper, output unchanged; ✅ `VERIFIED`, [VR-1261](../implementation/verification/VR-1261-telemetry-series-history-remediation.md)),
> [IP-1212](../implementation/packages/IP-1212-own-satellite-tle-export.md) (remediation package for the amended `FR-7440` — own satellites exportable, `BL-0201`; 🟢 `READY`, authored 2026-10-15),
> [IP-1262](../implementation/packages/IP-1262-export-sampling-bounds.md) (remediation package — explicit-`interval_s` floor + sample-count ceiling, closing Open Question 2's explicit-interval half, `BL-0176`; ✅ `VERIFIED`, [VR-1262](../implementation/verification/VR-1262-export-sampling-bounds.md)),
> [`docs/feature-planning/03-feature-catalog.md`](../feature-planning/03-feature-catalog.md) `FEAT-7400`
> **Produces:** truth and cell-observed ephemeris export in ECI/RIC, CSV/CCSDS OEM + companion RIC
> file, satisfying `FR-7410`/`FR-7420`/`FR-7430`; and a quick, copyable current-epoch TLE for any
> satellite visible to the requesting cell, satisfying `FR-7440`
> **Feature Mapping:** FS-121 (this document) ⇄ `FEAT-7400`
> **Related Topics:** [ADS-1500](../architecture/ADS-1500-per-cell-custody-estimated-state-and-export.md),
> [FS-103](FS-103-custody-management.md) v1.1, [FS-107](FS-107-after-action-review.md),
> [R101](../research/encyclopedia/R101-orbital-mechanics-for-operations.md) (TLE field layout,
> checksum, SGP4 lineage — grounds `FR-7440`'s output format), [ADR-0009](../architecture/adr/ADR-0009-moderate-orbital-fidelity.md)
> (moderate fidelity — bounds the accuracy `FR-7440`'s exported TLE need carry)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template.*

# FS-121 — State-Vector/Ephemeris & TLE Export

*(v1.0 title: "Ephemeris Export (Truth and Cell-Observed, ECI/RIC, CSV/CCSDS OEM)"; retitled in v2.0 to
match `FEAT-7400`'s catalog Title.)*

## Purpose

Let White Cell export ground-truth state vectors, and let a cell export its own believed
(custody-estimated) state vectors, for a time span, in ECI and RIC frames, as CSV and CCSDS OEM
files — a capability the baseline entirely lacks (god-view returns only current-instant truth as
JSON; AAR export covers the event log, not state vectors). `FR-7410`/`FR-7420`'s own Rationale
states this directly. **Added v2.0 (`FR-7440`):** separately, let any cell — and White Cell — take a
*current* two-line element set for any satellite it can currently see out of the simulator by
simple copy/paste, for tools that consume TLEs directly ("can just be an easy place to cut and
paste, or a cut-and-paste button next to it" — `BL-0109`, the project owner's own minimal-UI bar).
`FEAT-7400`'s own `Purpose`/`User Value`.

## Scope

**In scope:** (1) a no-cell, White-Cell-only truth ephemeris export over a requested time span, in
ECI and RIC-relative-to-a-chosen-object, as CSV and CCSDS OEM (`FR-7410`); (2) a cell-scoped,
fog-of-war-respecting export of that same cell's own believed state vectors over the same kind of
time span/frame/format set (`FR-7420`); (3) the companion RIC-only export file paired with the
OEM output (`FR-7430`, as built — recorded here in v2.0, no new behavior); (4) **(v2.0)** a quick,
single-satellite, current-epoch TLE export, presented as a copyable text field and/or a
copy-to-clipboard action — no file-download flow — for any satellite the requesting cell owns or
holds a `Track` on (cell-scoped, fog-of-war-filtered, `FR-6210`; own satellites added v2.1), or any
on-orbit satellite for White Cell via the no-cell exception (`FR-6220`) (`FR-7440`).

**(v2.3) Also in scope — `FR-7450`:** the form of the span `t1`/`t2` bounds on exactly three
exports — per-asset telemetry CSV (`FR-2320`, spec `FS-126`), truth ephemeris (`FR-7410`) and
cell-observed ephemeris (`FR-7420`), each with its RIC companion (`FR-7430`). **Not changed:** the
telemetry graph window (`t0`/`t1` on the series read), the live RIC view, the AAR/ledger exports,
the quick TLE export (no span), the exported values, `interval_s`, the sample-count ceiling
(`NFR-3710`) and the clamp/reject rule for out-of-range spans.

**Out of scope:** TLE *import* (`FR-5210`/`FR-5220`, a different Feature); a time-span or bulk
multi-object TLE export (`FR-7440` names one target satellite per request); any change to the
`Propagator` seam's propagation behavior (`ADR-0009`) — `FR-7440` serializes a state the existing
propagators already produce, it does not change how anything is propagated; the fog-of-war filter
itself (`FEAT-6200`, a dependency, per `FEAT-7400`'s `Excluded Requirements`); the underlying estimated-state-history mechanism itself, already designed by
`ADS-1500` (reused here, not re-specified); any change to `FS-103`'s custody model or `FS-107`'s AAR
replay mechanism, both of which this Feature consumes unchanged.

## Requirements Implemented

**(v2.3)** `FR-7450` (ISO-8601 UTC bounds on time-span exports) is added. It spans three exports
(telemetry CSV, truth ephemeris, cell-observed ephemeris, each with its `FR-7430` RIC companion),
so it is specified once, here, because two of the three exports and the shared span rule
(`_clamp_or_reject`/`sample_times`) already live in this Feature; `FS-126` (telemetry CSV) points
here. `FEAT-7400`'s catalog `Included Requirements` do not list `FR-7450` — see Open Question 9.

`FR-7410` (truth ephemeris export), `FR-7420` (cell-observed ephemeris export), `FR-7430`
(companion RIC-specific export file — v2.0, as built), `FR-7440` (quick TLE export for a
cell-visible satellite — v2.0). These are exactly `FEAT-7400`'s `Included Requirements`; none
added, none dropped.

## User Workflows

1. **Truth export (White Cell).** White Cell specifies a time span, one asset (several assets are exported
   by repeated requests, per `FR-7410`), a reference
   object (for RIC), and a format (CSV or CCSDS OEM); the system returns ground-truth state vectors
   for that span in both ECI and RIC-relative-to-the-reference-object form, via one of the existing
   no-cell endpoints (`FR-6220`).
2. **Cell-observed export (a Blue or Red cell operator).** The requesting cell specifies a time span,
   one tracked-object identifier (one per export, per `FR-7420`), a reference object, and a format; the system returns that
   cell's own believed state vectors (never ground truth, never another cell's belief) for the span,
   via a cell-scoped endpoint.
3. **Companion RIC file (`FR-7430`, as built).** Either requester above selects the RIC-only format
   alongside an OEM export; the system returns the same RIC columns the CSV export already carries,
   as a dedicated file.
4. **Quick TLE export — Blue or Red cell operator (`FR-7440`).** (a) The operator, viewing a
   satellite their cell currently holds a `Track` on **or one of their own satellites** (v2.1;
   placement in the console is Open Question 7), invokes "TLE" for it. (b) The console shows a two-line text block in a copyable field, with a
   copy-to-clipboard action beside it. (c) The operator copies it and pastes it into an external
   tool (STK, GMAT, a TLE-consuming script). Edge: the operator requests another side's satellite
   the cell holds no `Track` on (e.g. a stale selection, or a hand-crafted request) — the request is
   rejected with a reason; no TLE is shown.
5. **Quick TLE export — White Cell (`FR-7440`, `FR-6220` exception).** White Cell invokes the same
   action on any on-orbit satellite and receives a TLE derived from ground truth. Edge: the named
   object does not exist, or has no orbit — rejected with a reason.

## System Behaviour

**(v2.3, `FR-7450`) Span-bound parsing.** Each of `t1` and `t2` on the three exports is read by one
shared bound parser at the session boundary (the three routes do not each keep their own;
whether it sits in `SessionAPI` or the route layer is a `07` decision, Open Question 10). It runs
before the existing out-of-range check and before any replay, so a refused bound costs no replay.
- *Integer microseconds:* a bound of decimal digits only, optionally one leading `-`, is read as
  integer microseconds exactly as today. It is never read as a date.
- *ISO-8601 UTC:* extended form `YYYY-MM-DDThh:mm:ss`, optional fraction of 1-6 digits, then `Z` or
  `+00:00`. The result is the integer microseconds (Unix epoch, UTC) that `simtime.to_iso` renders,
  so an ISO bound and its microsecond equivalent give identical exports.
- *Refused:* no zone designator (naive), non-zero offset, more than six fractional digits (no
  rounding), date alone, basic format, week/ordinal date, leap second (`:60`), out-of-range field,
  lower-case `z`/`t`, anything else. The parser is stricter than `simtime.from_iso`, which assumes UTC
  for a naive string, and does not reuse its leniency.
- *Mixed pair:* one ISO bound and one integer is accepted.
- *Omitted bound:* the telemetry export's existing defaults for an omitted `t1`/`t2` are unchanged.
- The form never changes the exported values, `interval_s`, the span ceiling or the clamping of a
  partly out-of-range span (`FR-7450` Postconditions). The parsed values feed the same `sample_times`
  and `_clamp_or_reject` path as today.

- **Truth export** samples ground truth (`Asset.orbit`, propagated via the existing `Propagator`
  seam) at each requested time in the span, transforms to ECI directly and to RIC relative to the
  chosen reference object's own truth state, and serializes to the requested format. Reachable only
  through the existing no-cell endpoints (`/godview`, `/eventlog`, `/save`, `/aar*`, `/objectives`
  per `FR-6220`) — never a new cell-scoped route (`ADR-0004`, `ADR-0015`).
- **Cell-observed export** samples, at each requested time T in the span, the requesting cell's own
  belief state via the mechanism `ADS-1500` designs: replay the deterministic `EventLog` to the
  position nearest T (`engine/simulation.py::replay`, the same call `session/aar.py::state_at`
  already makes), read that cell's reconstructed `Track.state_estimate`, and forward-propagate it to
  exactly T. A time T at which the cell holds no `Track` on the object produces no point for that T
  (an empty result, not a fabricated one) — `FR-7420`'s own Postcondition.
- **RIC reference-object rule (cell-observed export only):** if the reference object is the
  requesting cell's own owned Asset, its ground-truth orbit is used directly (a cell always knows
  its own asset's true state exactly); if the reference object is itself only tracked, the same
  cell's own `Track.state_estimate` for it (at the same T) is used, never ground truth
  (`ADS-1500` Decision 5).
- **`FR-7420` is blocked on nothing architecturally** (`ADS-1500` resolved `BL-0068`'s domain-model
  question in full) but its detailed workflow depends on `FS-103` v1.1's confirmed design being read
  by whoever writes its Implementation Package — flagged in Open Questions only insofar as this
  document's own Acceptance Criteria for `FR-7420` cannot be exercised until that reading happens
  (a sequencing note, not an unresolved design question).
- **Companion RIC file (`FR-7430`, as built)** serializes the *same* RIC values the CSV path
  computes (a second serialization, not a second RIC computation) — `FR-7430`'s own Postcondition.
- **Quick TLE export (`FR-7440`) — state source.** The exported TLE is derived from exactly one
  state source, chosen by requester, mirroring the existing fog-of-war rule every cell-scoped read
  follows (`FR-6210`, `ADR-0004`):
  - *Cell-scoped request from cell C for satellite X:* C's own `Track` on X, specifically its
    `Track.state_estimate` (the same source `FR-7420`'s cell-observed path reads — `FEAT-7400`'s
    `Technical Value`: same fog posture, no new convention). Never X's ground-truth orbit, never
    another cell's track. Because `state_estimate` is captured at the last observation and then
    propagated forward by the existing `Propagator` seam (`FS-103` v1.1), a target that has
    manoeuvred since C last observed it exports C's *stale belief*, not its new truth — this is the
    correct, intended fog-of-war outcome, not a defect.
  - *(v2.1) Cell-scoped request from cell C for its **own** satellite Z:* Z's actual orbit
    (`Asset.orbit`). A cell always knows its own asset's true state exactly, and custody applies
    only to other objects (`ADS-1500` Decision 5, the same rule this Feature's RIC reference-object
    rule already applies; amended `FR-7440`). No `Track` is required or consulted. If C also holds a
    `Track` on its own satellite, the own-asset rule still applies; ownership decides, not whether a
    track exists.
  - *White Cell (no-cell path, `FR-6220`):* X's ground-truth orbit.
- **"Current epoch."** The TLE's epoch is the session's current simulated time (`world.now`), read
  from the sim clock — never the wall clock (`ADR-0002`). The exported TLE should, when propagated
  by a standard SGP4 implementation to its own epoch, reproduce the believed state at that instant
  to within an accuracy bound that `07-implementation-planning` must state and test (Open
  Question 4 — the bound depends on `BL-0110`'s chosen generation method).
- **Well-formedness.** The output is two 69-character lines in the standard NORAD TLE layout with a
  valid mod-10 checksum on each line (`R101`'s TLE-format section; CelesTrak format reference). A
  well-formed TLE is one the project's own existing TLE import path (`FR-5210`, `sgp4`'s parser)
  accepts — giving a self-consistent round-trip check.
- **Source-orbit kinds `FR-7440` must handle.** The selected state source can be either of the two
  orbit kinds the engine propagates (`ADR-0009`): a TLE-sourced orbit (SGP4 mean elements already
  stored, with their own original epoch) or a Kepler+J2 orbit (fictional assets, *and* any
  TLE-sourced object after a manoeuvre, since an impulse re-expresses the orbit as osculating
  Kepler elements). The latter is the `BL-0110` gap: no existing engine function converts an
  osculating/Kepler+J2 state into SGP4 mean elements. How `FR-7440` produces a current-epoch TLE
  for each kind is Open Question 4 — `FR-7440`'s own Notes assign this choice to `06`/`07`, and
  this spec deliberately records the constraints and options rather than picking one.
- **Rejection (edge cases).** A cell-scoped request is rejected — no TLE is returned, a specific
  reason is given — when: the named satellite is another side's and the cell holds no `Track` on
  it; the `Track` exists but carries no `state_estimate` (custody without a state); the object does
  not exist; or (v2.1) it is the cell's own asset but has no orbit (e.g. a ground station).
  `FR-7440`'s Postcondition (amended): no cell-scoped request returns a TLE for a satellite the
  cell neither owns nor holds a `Track` on, and no cell-scoped TLE of a non-owned satellite is
  derived from ground truth. A White-Cell request is rejected when the object does not exist or
  has no orbit.
- **Read-only.** Producing a TLE mutates no session or world state, consumes no RNG draw, and
  writes no event-log entry — like every other export in this Feature and like `scene.py`.

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| Session Layer (new export function, sibling to `session/aar.py`) | Drives replay across the requested time span (a generalization of `aar.py::state_at`'s single-point replay) for both truth and cell-observed variants; reads the appropriate state source per variant. |
| `engine/simulation.py` (`replay`) | Reconstructs `WorldState` at each sampled time — unchanged, reused as-is. |
| `engine/propagator.py` (`Propagator`) | Forward-propagates the sampled state (truth `Asset.orbit` or a cell's `Track.state_estimate`) to exactly the requested time — unchanged, reused as-is. |
| A new shared ephemeris serializer (ECI/RIC transform, CSV/CCSDS OEM writers) | Parameterized by state source (truth vs. cell-observed); shared between `FR-7410` and `FR-7420` rather than duplicated, per `ADS-1500`'s System Architecture. |
| `ui_web/server.py` | Exposes the truth export through an existing no-cell route and the cell-observed export through a new cell-scoped route, both per `ADR-0004`/`FR-6220`'s existing binding rules. |
| **(v2.0, `FR-7440`)** C2 Session/Application Layer (`SessionManager`/`InProcessSession`/`CellController`, `session/ephemeris.py`'s export family) | Resolves the requester's permitted state source (for a cell: its own `Track.state_estimate` for another side's satellite, or — v2.1 — the actual orbit of a satellite it owns; ground truth for White Cell), applies the rejection rules, and invokes the TLE serialization — the fog-of-war decision lives here, at the boundary (`ADR-0004`), never in the UI. |
| **(v2.0, `FR-7440`)** C1 Simulation Engine (`engine/orbit.py`/`engine/propagator.py`) | Supplies the state to serialize via the existing `Propagator` seam (unchanged), and hosts whatever pure, deterministic orbit-to-TLE conversion `07` chooses for `BL-0110` (Open Question 4). No change to propagation behavior. |
| **(v2.0, `FR-7440`)** C4 Operator Console (`ui_web/static/`) | Presents the returned TLE as a copyable text field with a copy-to-clipboard action; renders the rejection reason on failure. Holds no filtering logic. |
| **(v2.0, `FR-7440`)** C3 Mock SSN | No new responsibility — named in `FEAT-7400`'s `Affected Subsystems` because SSN deliveries are one of the existing writers of `Track.state_estimate` (`engine/ssn.py`), i.e. a source of the belief state `FR-7440` exports; unchanged. |

## Interfaces Used

`INT-0014` (AAR/Replay → Simulation Engine, EventLog/WorldState) — the interface both exports drive,
per `ADS-1500`'s System Architecture, generalized from a single-point read to a time-span read.
Flagged (Requirements Review Finding 6, `docs/reviews/requirements-update-must-tier-batch.md`,
backlog `BL-0093`) as a documented-shape stretch: `INT-0014` describes single-point replay reads,
not a time-span/multi-format export. Not resolved here — routed to whoever next touches the ICD.
`INT-0007` (`CellController` → Custody/TrackCatalog) for the cell-observed variant's fog-of-war
binding — and, in v2.0, for `FR-7440`'s cell-scoped read of the requesting cell's own `Track`.
**(v2.0, `FR-7440`)** `INT-0006` (Operator Console → Session Layer, the `SessionAPI` single seam) —
the console requests the TLE through the existing seam, as every other cell-scoped read does. The
concrete route path/parameter shape is not committed to by any ICD entry or ADR — Open Question 6.

## Data Model Changes

None. Both exports read existing entities (`Asset.orbit`, `Track.state_estimate`) through the
existing replay mechanism; no new Domain Model entity, per `ADS-1500` Decision 2/3.
**(v2.0, `FR-7440`)** None. The TLE is a derived, transient output computed on request from the
existing `OrbitState` (`Asset.orbit` / `Track.state_estimate`); nothing is stored back. The existing
`OrbitState.tle_line1`/`tle_line2` fields are read (for TLE-sourced orbits) but never written by
this Feature.

## State Changes

None — both exports are read-only, exactly like `FR-7310`'s AAR replay/scrub (no live session state
is mutated by producing an export). **(v2.0)** The same holds for `FR-7440`: no world/session state,
RNG state, or event-log entry is created; the clipboard copy is a purely client-side action.

## Error Handling

- **(v2.3, `FR-7450`)** A bound that cannot be read is refused with a 400 that names the bound
  (`t1` or `t2`) and the reason (for example "no zone designator", "non-zero UTC offset", "more than
  six fractional digits", "date without time", "not a timestamp or integer"), and nothing is
  exported. A refusal is distinct from the out-of-range and sample-ceiling errors. The error code and
  exact wording are a `07` decision (Open Question 10).
- A requested time span outside the session's own recorded event-log range: not addressed by
  `FR-7410`/`FR-7420`'s own text — see Open Questions.
- A cell-observed export request for an object the requesting cell never held a `Track` on at any
  point in the span: produces an empty result for that object across the whole span (an extension
  of the same-T empty-point behavior above), not an error.
- A malformed/out-of-range reference-object identifier: rejected with a specific reason, consistent
  with the existing "invalid input fails loudly" posture (`FR-5310`'s analogous rule for vignette
  loading).
- **(v2.0, `FR-7440`; narrowed v2.1)** Cell requests a TLE for another side's satellite it holds no
  `Track` on → rejected with a specific reason (`FR-7440` Acceptance Criteria/Postcondition); no
  TLE, partial or otherwise. A cell's own satellite is never rejected for lacking a `Track`.
- **(v2.0, `FR-7440`)** Cell holds a `Track` with no `state_estimate` → rejected with a specific
  reason (there is no believed orbit to serialize — never fall back to ground truth).
- **(v2.0, `FR-7440`)** Unknown object id, or an object with no orbit (White Cell or cell) →
  rejected with a specific reason.
- **(v2.0, `FR-7440`)** The believed orbit cannot be represented in a standard TLE (e.g. a
  hyperbolic/escape or otherwise SGP4-invalid state, or one whose values overflow the fixed-width
  TLE fields) → rejected with a specific reason, never a silently malformed TLE. Whether any orbit
  regime the engine supports (e.g. `CISLUNAR`) needs an explicit rule is part of Open Question 4.

## Performance Considerations

**(v2.3, `FR-7450`)** Parsing is constant-time string work done before any replay; the ceiling
`NFR-3710` and the replay cost are unchanged. A refused bound triggers no replay.

- **Replay cost scales with sample count × eventlog length** (`ADS-1500` Constraints/Risks) — a
  naive per-sample full replay from `initial_state` could be slow for a fine-grained sample rate
  over a long time span. `ADS-1500` explicitly leaves the mitigation (coarser default sampling,
  reuse of `Snapshot` checkpoints) to `07-implementation-planning`, not this document.
- **(v2.0, `FR-7440`)** A single-satellite, current-instant request: no replay, one state
  evaluation (plus whatever bounded, fixed-iteration work `07`'s `BL-0110` choice needs). It must
  stay interactive at the same cadence as other on-demand console reads (`NFR-1100`), and any
  engine-side conversion must be a pure, UI-agnostic function (`NFR-1900`). Determinism
  (`ADR-0002`): the conversion must be deterministic and read no wall clock — the TLE epoch comes
  from sim time.

## Security Considerations

**(v2.3, `FR-7450`)** The parser adds no new route and no new trust surface: the three routes keep
their existing bindings (`/ephemeris/truth` no-cell and White-only; the cell-observed and telemetry
routes cell-scoped under `FR-6210`). A bound is data, never evaluated; the strict grammar rejects
everything outside it.

- Truth export must remain reachable only through the existing no-cell endpoints (`FR-6220`,
  `ADR-0015`'s documented LAN trust boundary) — never a new cell-scoped route, per `FR-7410`'s own
  Postcondition.
- Cell-observed export must enforce the same fog-of-war-at-the-boundary rule (`ADR-0004`) every
  other cell-scoped read already does — reads only the requesting cell's own `Track`, never another
  cell's, never ground truth.
- **(v2.0, `FR-7440`)** Same posture: for another side's satellite the cell-scoped TLE path reads only
  the requesting cell's own `Track`, filtered at the `SessionAPI`/`CellController` boundary
  (`ADR-0004`, `FR-6210`). **(v2.1)** For the cell's own satellite it reads that satellite's actual
  orbit; this exposes nothing the cell does not already see (`FR-6210` exposes a cell's own assets
  at truth), and the ownership check must sit at the same boundary, never in the UI; White
  Cell's ground-truth variant rides the existing no-cell exception (`FR-6220`, `ADR-0015`) rather
  than becoming a new, separately-named unfiltered surface. The exported TLE of a manoeuvred target
  must reflect the cell's belief, so it must not leak the post-manoeuvre truth. No new trust
  boundary: the cell selector remains client-side trust per `ADR-0015`, exactly as for `/scene/{cell}`.
- **(v2.0)** If the console's copy-to-clipboard uses the browser Clipboard API, it needs a secure
  context in most browsers; on a plain-HTTP LAN deployment the copyable text field is the
  guaranteed fallback (the project owner's own bar accepts either).

## Console Friction

**(v2.3, `FR-7450`)** Not applicable: no console surface. The three exports are URL-only today
(manual sections `WCM-15`, `WCM-16`, `BLU-13`, `BLU-14`, `RED-12`, `RED-13`) and `FR-7450` changes only what the query
string accepts. The deliberate strictness (naive timestamps refused rather than assumed UTC) is
friction at the API, justified by a local-time slip otherwise yielding a silently wrong span; the
refusal message names the bound and reason so it is self-correcting. The `FR-7440` TLE console
surface is unchanged.

## Manual Impact

**(v2.3)** On build, `08-training-manual-authoring` updates `docs/training/08-http-api-reference.md`
(the sentence at line ~108 that bounds are "integer microseconds of sim UTC" becomes: ISO-8601 UTC
or integer microseconds, with the accepted form, refused forms and one worked example) and the
export sections named by `docs/training/15-manual-traceability.md` §15.1 for the two export rows
(ephemeris time-span; telemetry CSV): `WCM-15`, `WCM-16`, `BLU-13`, `BLU-14`, `RED-12`, `RED-13`, so an
operator is shown a timestamp rather than microseconds. Documents as-built behavior only; nothing
is written before the build lands.

## Acceptance Criteria

1. Given a time span and a reference object, the truth export's CSV and CCSDS OEM files both contain
   state vectors matching the engine's own truth at each sampled time, correctly transformed into
   RIC relative to the chosen reference object; the export is reachable only via an existing no-cell
   endpoint. *(`FR-7410`)*
2. Given the estimated-state-history mechanism (`ADS-1500`, already resolved), a cell-observed export
   request from cell C for object X returns C's own estimated state at each sampled time, matching
   `CellController`'s existing fog-of-war filtering rule — no ground truth, no other cell's belief
   state. *(`FR-7420`)*
3. *(`FR-7430`, as built)* The companion RIC file's values equal the corresponding CSV export's RIC
   columns exactly, for both the truth and cell-observed variants.
4. *(`FR-7440`)* Given cell C holding a `Track` (with a `state_estimate`) on satellite X, a C-scoped
   TLE request for X returns exactly two lines, each 69 characters, in standard TLE layout, each with
   a correct mod-10 checksum, and the pair is accepted by the project's own TLE import parser
   (`sgp4`'s `twoline2rv`).
5. *(`FR-7440`)* The returned TLE's epoch equals the session's current sim time (to the TLE epoch
   field's own resolution), not the original TLE's epoch and not wall-clock time.
6. *(`FR-7440`)* Propagating the returned TLE with SGP4 to its own epoch reproduces C's believed
   position for X at that instant within the accuracy bound `07-implementation-planning` states
   (Open Question 4) — tested for at least one TLE-sourced and one Kepler+J2-sourced target.
7. *(`FR-7440`)* Given C holds no `Track` on another side's satellite Y (or the `Track` has no `state_estimate`),
   the C-scoped request for Y is rejected with a reason and returns no TLE.
8. *(`FR-7440`, fog-of-war)* If X has manoeuvred after C's last observation, C's exported TLE
   reproduces C's pre-manoeuvre belief, not X's post-manoeuvre ground truth; White Cell's export
   for X reproduces the ground truth.
9. *(`FR-7440`)* Producing a TLE leaves the session's world state, RNG state, and event log
   unchanged (the determinism property test stays green).
10. *(`FR-7440`, UI)* The console presents the TLE in a copyable text field with an adjacent
    copy-to-clipboard action — no file download is required.
11. *(`FR-7440`, v2.1 — own satellite)* Given cell C owning satellite Z and holding no `Track` on it,
    a C-scoped TLE request for Z returns a well-formed TLE (as in criterion 4) whose SGP4
    propagation to its own epoch reproduces Z's actual position within the same bound as criterion
    6. The same request made by the other cell, which holds no `Track` on Z, is still rejected
    (criterion 7).
12. *(`FR-7450`)* For each of the three exports and its RIC companion, a span given as ISO-8601 UTC
    bounds (including a fractional second and a `+00:00` designator) returns exactly the rows
    returned for the same span given as integer microseconds.
13. *(`FR-7450`)* A span given as integer microseconds, and a mixed pair (one ISO bound, one
    integer), are accepted unchanged.
14. *(`FR-7450`)* A naive timestamp, a non-zero offset, seven fractional digits, a date alone, a
    basic-format string and a non-time string are each refused with an error naming the bound
    (`t1` or `t2`) and the reason, and nothing is exported; no replay runs for a refused bound.
15. *(`FR-7450`)* The telemetry graph window, the live RIC view and the AAR/ledger exports behave as
    before (a bound that is not an integer is not newly accepted there).

## Verification Plan

Test (automated) for both criteria, per `FR-7410`/`FR-7420`'s own stated Verification Method.
Criterion 2's test suite should include the negative assertion (a cell-observed export never
contains ground truth or another cell's belief), mirroring the existing fog-of-war test pattern
(`spacesim/tests/test_scene.py`).
**(v2.0)** Criterion 3: Test (already shipped — `test_ephemeris.py`, `test_web.py`). Criteria 4-9:
Test (automated, per `FR-7440`'s Verification Method), at both the session layer and the HTTP
route; criteria 7 and 8 are the negative fog-of-war assertions, mirroring `test_scene.py`'s
pattern. Criterion 10: Inspection/Demonstration (the console is unverified headless per this
project's established UI-verification posture — `CLAUDE.md` status line), backed by a route-level
Test that the payload carries the two TLE lines.
**(v2.1)** Criterion 11: Test (automated) at the session layer and the HTTP route, including the
cross-cell negative (the other cell's request for Z is still rejected).
**(v2.3)** Criteria 12-15: Test (automated, `FR-7450`'s Verification Method), tagged
`@pytest.mark.verifies("FR-7450")`: a table-driven parser unit test for the accepted and refused
grammar (every refused form in the System Behaviour list), then a route-level parity test per export
(ISO vs microseconds, row-for-row equal), the mixed pair, the refusal naming the bound, and a
spy asserting no replay on a refused bound. Criterion 15: Test that the series route's `t0`/`t1`
still take integers only.

## Dependencies

`FR-6220` (no-cell endpoints), `FS-107`/`FR-7310` (the replay mechanism both variants reuse), `FS-103`
v1.1 (the confirmed custody-independence finding and the replay-based history design).
`FEAT-7400`'s catalog Dependencies: `FEAT-7100`, `FEAT-6200`. **(v2.0, `FR-7440`)** `FR-6210`
(fog-of-war filter, `FEAT-6200`), `FR-1210` (the `Propagator` seam that yields the state to
serialize), `FR-1510` (custody/`Track`) — `FR-7440`'s own Dependencies, all already built and
`VERIFIED`. `FR-7440` does **not** depend on `FR-7410`-`FR-7430` being built (it reuses their fog
posture, not their code path); no other `FS-xxx` must exist first.

## Risks

- **Interface-model stretch (see Interfaces Used)** — `INT-0014`'s documented shape may need an
  architecture-owner edit before an Implementation Package can cite it cleanly for a time-span
  export, though neither `FR-7410` nor `FR-7420` is itself blocked by this (per `BL-0093`'s own
  "not blocking" framing).
- **Performance risk (see Performance Considerations)** — sizing the sampling-rate/time-span ceiling
  is deferred to implementation planning, with no numeric target from any source document.
- **Shared-serializer coupling risk.** Building one serializer shared between `FR-7410` and
  `FR-7420` (per `ADS-1500`'s System Architecture) means a serialization defect affects both exports
  at once — an acceptable, deliberate coupling (avoiding duplication), but worth naming so an
  Implementation Package tests both variants against any serializer change.
- **(v2.0) TLE-generation accuracy risk (`BL-0110`).** An SGP4 TLE encodes *mean* elements; the
  engine's Kepler+J2 path carries *osculating* elements. Serializing osculating elements straight
  into TLE fields produces a TLE that is well-formed but propagates (under SGP4) to a position
  offset from the believed state by the J2 short-period terms — order kilometres in LEO. Whether
  that is acceptable, and how it is bounded/documented, is Open Question 4. Mis-stating the
  accuracy would mislead an analyst using the TLE externally.
- **(v2.0) Scope-fit risk on option (c).** `BL-0110`'s option (c) — export only TLE-sourced
  objects — would leave every Kepler-fictional satellite (the majority of shipped vignettes'
  assets) un-exportable, in tension with `FR-7440`'s Description "**any** satellite currently
  visible to the requesting cell" and `BL-0109`'s own wording. Choosing (c) would narrow the
  approved requirement and therefore needs the project owner (or a `04` amendment), not a `07`
  decision alone.
- **(v2.0) Catalog-identity risk.** TLE line 1 carries a satellite catalog number and
  international designator; fictional objects have neither (Open Question 8). An invented number
  that collides with a real catalog object could confuse an external tool.

## Open Questions

1. **Behavior for a requested time span outside the session's own recorded event-log range** — not
   addressed by either requirement's text. Needs a `04-requirements-engineering` amendment or an
   explicit `07` decision (clamp to the recorded range? reject outright?).
2. **Sampling-rate/performance ceiling** — carried from `ADS-1500`'s own Open Question 2, restated
   here since it directly bounds this Feature's practical usability for a long time span.
3. *(Sequencing note, not a design ambiguity)* Whoever writes the Implementation Package for
   `FR-7420` should read `FS-103` v1.1's confirmed System Behaviour note (`Track.state_estimate`'s
   independence from truth) directly before starting, since it is the load-bearing fact this
   Feature's entire cell-observed variant depends on.

*(Open Questions 1-3 were resolved by `IP-1210`'s Design Decisions 1-2 and are retained here
unchanged as historical record. Questions 4-8 below are new in v2.0, all for `FR-7440`.)*

4. **How is a current-epoch TLE generated from the believed orbit? (`BL-0110`)** `FR-7440`'s Notes
   explicitly assign this choice to `06`/`07`; this spec records the constraints and leaves the
   choice to `07-implementation-planning`. Options (from `BL-0110`): (a) a real mean-element fit —
   e.g. an iterative correction of SGP4 mean elements until SGP4's own state at the epoch matches
   the believed state; (b) re-epoch a TLE-sourced object's original elements to the current time
   (and, for Kepler+J2 objects, a direct osculating-to-TLE-field mapping) with a documented,
   bounded-error approximation; (c) export TLE-sourced objects only (see Risks — needs the owner,
   not `07` alone). Constraints any choice must satisfy: covers both orbit kinds the engine
   propagates (TLE-sourced *and* Kepler+J2, including post-manoeuvre objects) unless the owner
   approves (c); deterministic and wall-clock-free (`ADR-0002`); a pure engine-side function with
   no change to the `Propagator` seam's behavior (`ADR-0009`, `NFR-1900`) — so it needs no new
   architecture interface and does not route to `03`; states a numeric accuracy bound (Acceptance
   Criterion 6) and tests it; rejects unrepresentable orbits (Error Handling). `ADR-0009`'s
   "moderate fidelity is sufficient for the training objectives" bounds how rigorous the fit need
   be. **Why it matters:** it determines whether the exported TLE is trustworthy in external tools.
   **Resolution path:** a `07-implementation-planning` Design Decision (or, if `07` judges option
   (c) the only feasible one, the project owner).
5. **Is a cell's *own* satellite exportable?** `FR-7440` defines "visible" as "the cell holds a
   `Track` on it" and its Postcondition forbids returning a TLE for any satellite without one — but
   a cell normally holds no `Track` on its own assets, while it does know their true orbits exactly
   (`ADS-1500` Decision 5; `FS-130`/`IP-1300`'s visible-object rule treats own assets as visible).
   Read literally, own assets are not exportable. **Why it matters:** exporting one's own
   satellite's TLE is a natural operator need. **Resolution path:** a `04-requirements-engineering`
   amendment to `FR-7440` (broaden "visible" to include own assets); until then `07` should follow
   the literal requirement. **Closed v2.1:** `FR-7440` was amended on 2026-10-15 (`BL-0159`;
   [report](../reviews/requirements-update-parked-questions-batch.md)), and own satellites are now in
   scope (System Behaviour, Error Handling, Acceptance Criterion 11). The shipped `IP-1211` follows
   the pre-amendment reading (its Design Decision 5), so a remediation package is owed (`BL-0201`).
6. **Route path and request shape.** No ICD interface or ADR commits to a URL/parameter convention
   beyond the general cell-scoped `GET /api/sessions/{sid}/<resource>/{cell}` pattern and the
   White-Cell no-cell pattern. A `07-implementation-planning` decision (same as `FS-130`'s
   `BL-0155`).
7. **Where in the console the TLE action lives** (track list, belief-map selection, fleet rail, a
   panel) — not stated by any requirement beyond "copyable field or copy button". A
   `07-implementation-planning` decision.
8. **Catalog number / international designator / name for objects without a real one.** TLE line 1
   requires a 5-character catalog number and an international designator; a TLE-sourced object can
   carry its originals forward, a fictional one has none. Options include a fixed placeholder or a
   deterministic derived number; must not silently imply a real object's identity. A
   `07-implementation-planning` decision.
9. **(v2.3) `FR-7450` is in no Feature Catalog entry.** `FEAT-7400` lists `FR-7410`-`FR-7440`; the
   telemetry export's `FEAT` lists `FR-2320`. This spec carries `FR-7450` as the owning home by
   judgement; the catalog should record where it belongs. Owner: `05-feature-decomposition`
   (catalog entry), not this spec.
10. **(v2.3) Where the shared bound parser lives, and the error code and wording.** `FR-7450`'s Notes
    leave both to `06`/`07`. This spec requires one parser shared by all three routes, run before
    replay; its module placement and the exact 400 body are `07-implementation-planning` decisions.

## Related ADRs

`ADR-0002` (deterministic core — the replay guarantee both exports depend on), `ADR-0004`
(fog-of-war at the boundary), `ADR-0015` (LAN trust model — the no-cell endpoint binding `FR-7410`
must respect). **(v2.0)** `ADR-0013` (custody / `Track` — `FEAT-7400`'s catalog Related ADRs;
`FR-7440` reads the `Track` this ADR governs), `ADR-0009` (moderate orbital fidelity — bounds
`FR-7440`'s TLE accuracy expectation and the two orbit kinds it must handle). **(v2.3, `FR-7450`)** `ADR-0004`, `ADR-0015` (unchanged bindings), per `FR-7450`'s Related ADRs.

## Related Interfaces

`INT-0007` (Custody/TrackCatalog), `INT-0014` (AAR/Replay — see Interfaces Used). **(v2.0)**
`FR-5210`/`FR-5220`'s TLE import path (`content/bulk_import.py`, `SessionManager.add_tle`) — not
used by `FR-7440`, but its parser is the round-trip well-formedness check named in Acceptance
Criterion 4.
