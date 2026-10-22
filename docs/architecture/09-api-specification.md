# GDS-09 — API Specification

> **Document ID:** GDS-09
> **Version:** 1.0
> **Status:** ✅ Authored — merge gate closed (see "Merge gate" below)
> **Dependencies:** GDS-08
> **Referenced By:** GDS-10
> **Produces:** GDS-10
> **Feature Mapping:** N/A — program-level
> **Related Topics:** [`design/07-api-and-networking.md`](../design/07-api-and-networking.md) (merge
> source — superseded by this document), [`design/05-interface-control-document.md`](../design/05-interface-control-document.md)
> (the interface inventory, `INT-0001`…`INT-0016`; companion to this document — see below),
> [GDS-08](08-ui-architecture.md) (the screens that call this API),
> [GDS-07](07-data-model.md) (the payload shapes), [GDS-06](06-non-functional-requirements.md)
> (NFR-5 trust boundary, NFR-15 limits), ADR-0001, ADR-0003, ADR-0004, ADR-0014, ADR-0015,
> ADR-0016, ADR-0026.

[↑ Architecture index](INDEX.md) · [Docs index](../INDEX.md)

## Purpose

The contracts at SpaceSim's service boundaries: the `SessionAPI` seam between the presentation
layer and everything below it, and the HTTP API that carries that seam to browsers on a LAN. It
states who may call what, what comes back, how state reaches clients, and what the trust model
does and does not protect. It describes the shipped API (`spacesim/session/api.py`,
`spacesim/session/inprocess.py`, `spacesim/ui_web/server.py`); the exact signature of a call is the
code, and this document is the contract that code must keep.

## Relationship to the Interface Control Document

| Document | Grain | Role |
|---|---|---|
| `design/07-api-and-networking.md` | Sketch | **Superseded.** A pre-implementation design; its contract is restated here as built. |
| **GDS-09 (this document)** | Contract | **Authoritative** for the two programmatic interfaces — `SessionAPI` (`INT-0006`) and HTTP (`INT-0001`–`INT-0005`) — and for authorization, delivery, errors and limits across them. |
| `design/05-interface-control-document.md` | Inventory | **Authoritative for the interface inventory**: every interface between components (`INT-0001`…`INT-0016`), with participants and data. Owned by `03`. It closes its own §7 issue 1 ("no baselined wire-level contract") by citing this document. It moves under `docs/architecture/` in the single cleanup sweep with the rest of `docs/design/` (see "Merge gate"). |

---

## 1. Boundary rules

- **The presentation layer depends on `SessionAPI`, never on the engine** (ADR-0003). The engine
  imports no UI or transport code (invariant 2, enforced by the import-guard test).
- **Everything crossing the seam is a serializable message** — `pydantic` models to JSON — even in
  process, so a transport changes how messages travel, never what they are.
- **The session layer is authoritative.** Clients send intents (issue an order, fire an inject,
  set the clock); they never mutate state directly, and every accepted intent becomes a logged
  event (GDS-06 NFR-12).
- **Fog of war is applied once, server-side,** at `SessionAPI`/`CellController` (ADR-0004). No
  client receives another cell's hidden state from a cell-scoped call.
- **Reads have no side effects** (GDS-06 NFR-13): any read may be called at any time and rate.

## 2. The `SessionAPI` seam (`INT-0006`)

`session/api.py::SessionAPI` is the protocol; `session/inprocess.py::InProcessSession` is its only
implementation, used by both hot-seat and LAN play. Method groups, as built:

| Group | Methods | Caller |
|---|---|---|
| Lifecycle | `list_vignettes`, `load_vignette`, `set_parameter`, `start`, `create_draft_session`, `save_vignette`, `list_sessions` | White Cell |
| Time | `set_clock` (running, rate), `clock_state`, `step`, `advance_to`, `rewind_to`, `undo_last`, `catch_up` | White Cell (clock reads: any) |
| Injects | `fire_inject`, `pending_injects`, `cancel_inject`, `edit_inject` | White Cell |
| Authorization | `issue_roe_change`, `decide_gated_order`, `assign_role`, `staffing_report`, `set_observer_view` | White Cell, or a gate's required role |
| Orders | `issue_order`, `validate_order` (dry run), `cancel_order` | Red, Blue (White when driving a side) |
| Reads | `get_view` (fog-filtered `CellView`), `get_godview` (truth), `get_eventlog(since_seq)`, `objectives`, scene, telemetry, windows, alarms, recovery, exports | Per cell; truth reads unfiltered |
| Persistence | `save` (returns the save envelope), `load_save` (state → new session ID) | White Cell |

**Message types** (`session/api.py`):

- **`Ack`** — `ok`, `reason`. Every mutating call returns one; a refusal is `ok = false` with a
  human-readable reason, not an exception.
- **`OrderAck`** — `ok`, `id`, `reason`, `status`, `earliest_window`, `delivery_path`. Lets the UI
  say "queued for 06:14:00Z via STATION-BRAVO" or show the refusal reason.
- **`CellView`** — `cell`, `now`, `own_assets`, `own_sensors`, `known_tracks` (belief about others),
  `visible_effects` (symptoms on own assets, attribution-limited), `effect_windows`, `messages`,
  `objectives`. The only picture a player cell receives.

**Concurrency.** Each session has a re-entrant lock: every mutation runs inside it, and every read
first calls `catch_up` (the lazy clock, ADR-0014), so the sim clock advances exactly once however
many clients read. The lock is designed for roughly 16 LAN participants, an untested estimate
(ADR-0026).

## 3. The HTTP API (`INT-0001`–`INT-0005`)

FastAPI, JSON over HTTP, 91 API routes; the console page is served at `/`.

**Conventions**

- Session-scoped routes live under `/api/sessions/{sid}/…`; `sid` is `sess-N`. Unknown `sid` → 404.
- Cell-scoped reads put the cell in the path (`/view/{cell}`, `/scene/{cell}`,
  `/telemetry/{cell}/{asset}`) and return that cell's filtered picture.
- Every mutating call carries the caller's seat as a `cell` value (body or query), and the server
  refuses any mutation from the Observer seat before it reaches the session layer (IP-1130).
- Times on the wire are integer microseconds (GDS-07 §1) unless a field is named as ISO-8601.

**Status codes**

| Code | Meaning |
|---|---|
| 200 | Success, **including a refused order**: `OrderAck` with `ok = false` and a reason is a normal result, not an error. |
| 400 | Invalid input: an invalid vignette (`invalid_vignette`, with every problem listed), a malformed or precondition-failing inject, an out-of-range export span or sample count, an oversized save. |
| 403 | The seat may not do this: the Observer on any mutation; a non-White seat on a server-enforced White-only route (§4). |
| 404 | Not found: unknown session or vignette, or an object outside the caller's custody (RIC view, TLE export). |

**Route families** (paths relative to `/api/sessions/{sid}` unless absolute):

| Family | Routes |
|---|---|
| Discovery and lifecycle | `GET /api/sessions`, `POST /api/sessions` (load), `POST /api/sessions/draft`, `POST /api/sessions/load_save`, `GET /api/vignettes`, `GET /api/vignettes/{vid}/source`, `GET /api/vignettes/{vid}/tutorial`, `GET /api/ground_sites`, `POST /start`, `POST /param`, `GET /save`, `POST /save_vignette` |
| Time | `GET /clock`, `POST /clock`, `POST /step`, `POST /advance`, `POST /rewind`, `POST /undo`, `POST /red_step` |
| Cell picture | `GET /view/{cell}`, `GET /scene/{cell}`, `GET /brief/{cell}`, `GET /windows/{cell}/{asset}`, `GET /next_contacts/{cell}`, `GET /alarms/{cell}`, `GET /activity/{cell}`, `GET /conjunctions/{cell}`, `GET /coaching/{cell}`, `GET /ric_view/{cell}` |
| Telemetry | `GET /telemetry/{cell}/{asset}`, `GET /telemetry/{cell}/{asset}/{param}` (`&nominal=1` for the clean baseline), `GET /telemetry/{cell}/{asset}/export.csv` |
| Orders | `POST /order/validate`, `POST /order`, `POST /cancel`, `GET /orders/{cell}`, `POST /preview/consequence`, `POST /maneuver/compute`, `/jam/compute`, `/engage/compute`, `/cyber/compute`, `/sigint/compute` |
| Safe mode | `GET /recovery/{cell}/{asset}`, `POST /recovery/{cell}/{asset}` |
| Tasking (SSN) | `POST /ssn/{cell}/request`, `GET /ssn/{cell}/requests`, `POST /ssn/{cell}/cancel`, `GET /ssn/{cell}/coverage` |
| Facilitation | `POST /inject`, `GET /injects`, `GET /injects/pending`, `POST /injects/{handle}/cancel`, `POST /injects/{handle}/edit`, `GET /inject_library`, `POST /roe/change`, `POST /gate/decide`, `POST /roles/assign`, `GET /roles/staffing`, `GET /controller_view`, `POST /observer/view`, `GET /observer/view`, `GET /observer/designation` |
| Force edits | `POST /force/tle`, `POST /force/bulk_import`, `POST /force/ground` |
| Ground truth | `GET /godview`, `GET /eventlog`, `GET /objectives`, `GET /assessment`, `GET /ephemeris/truth` |
| Exports | `GET /ephemeris/{cell}`, `GET /tle/{cell}`, `GET /maneuver_ledger/{cell}/{asset}` (+ `/export.csv`), `GET /aar/export.csv`, `GET /aar/export.json` |
| AAR | `GET /aar`, `GET /aar/at`, `GET /aar/objectives`, `POST /aar/playback/start`, `/advance`, `/speed`, `/viewpoint`, `GET /aar/playback/state` |
| Vignette Creator | `GET`/`PUT /creator/state`, `GET /creator/scene`, `GET`/`POST /creator/seats`, `PATCH`/`DELETE /creator/asset/{asset_id}` |

The screen-to-route binding (which panel calls what, how often) is GDS-08 §4–§7's concern; this
table is the contract surface.

## 4. Authorization (as built)

Cell selection is **client-side trust** (ADR-0015, GDS-06 NFR-5): there is no authentication, and
the server believes the seat a request names. Within that, the server enforces three rules:

1. **Fog on every cell-scoped read.** A request for `/view/blue` gets Blue's filtered picture and
   nothing more, whoever sent it.
2. **The Observer seat never mutates.** Every mutating route refuses `cell = observer` (403).
3. **Server-enforced White-only actions** — refused (403, or `ok = false`) for any other seat:
   declaring seats (`/creator/seats`), cancelling or editing a pending inject, the controller view,
   changing ROE (`issue_roe_change`), and deciding a gated order (only the gate's `required_role`).

**Everything else White Cell does is White-only by UI convention only.** Start, parameters, the
clock (pause, resume, rate), step, advance, rewind, undo, firing an inject, force edits, seat
assignment, Observer designation and loading a save are offered only on White Cell's screens, but
the server accepts them from any non-Observer seat. ADR-0016 says time control is "reachable only
through the White Cell's session-layer calls", and the API does not yet enforce that (OQ1).

**Ground-truth reads have no cell binding** by design: `/godview`, `/eventlog`, `/save`, `/aar*`,
`/objectives`, `/assessment`, `/ephemeris/truth`, the Observer view and White Cell's facilitation
reads (the full named set is `FR-6220`).

### The LAN trust model (carried over from `CLAUDE.md` and ADR-0015)

Deploy only on a trusted LAN with cooperative participants. A hostile participant can read another
cell's picture by naming that cell in a URL, read ground truth from the unbound endpoints, and — per
the gap above — drive White Cell's unenforced controls. This is accepted for v1's PME context, where
everyone in the room is on the same team learning together; per-cell tokens are deferred hardening
(`CNFR-04`). The Observer rejection and the five White-only checks are real structural rules, but
at the same trust level: a participant who lies about their seat bypasses them.

## 5. State delivery

- **Polling.** Clients poll (about every 1.5 s); the server's lazy clock catches up on each read.
  The client interpolates its displayed clock between polls and shows a "no updates" warning after
  4 s without a successful poll.
- **One clock for everyone.** The sim clock advances exactly once regardless of how many tabs or
  machines poll, and only the clock routes change its rate or running state.
- **Joining.** Loading a session sets the URL to `…/#sess-N`; any browser that opens it joins that
  session (`GET /api/sessions` lists them). Pop-out windows join the same way with a layout token
  (GDS-08 §4).
- **No push.** `design/07` planned WebSocket push of view deltas keyed off event-log sequence
  numbers. It was not built; `get_eventlog(since_seq)` exists and would be the delta contract if
  push is ever added.

## 6. Hot-seat and LAN use the same contract

The same `InProcessSession` serves one machine (hot-seat, seat switching) and many (LAN): only the
number of browsers changes, not the contract, the fog rules or the clock. This is the "contract
equivalence" `design/07` required: nothing in `engine/` changed for multiplayer.

## 7. Error and validation contract

- Mutations return `Ack`/`OrderAck`; refusals carry a reason the UI shows verbatim (mapped to plain
  language for tooltips). No window, insufficient delta-v or rounds, ROE-blocked, no weapons-quality
  track, contended sensor and unknown command are normal refusals, not exceptions.
- **Order refusal reasons** (the validator's vocabulary, `engine/orders.py` and
  `engine/buscommands.py`): geometry and delivery — `no_window`, `no_command_station`,
  `no_downlink_station`; authority — `roe_kinetic_not_authorized`, `roe_cyber_not_authorized`,
  `not_owner`; custody — `no_weapons_quality_track`, `requires_cue`, `no_target`; resources —
  `insufficient_delta_v`, `insufficient_ammo`, `no_ammo`; spacecraft — `no_bus`, `no_payload`,
  `no_payload_for_verb`, `payload_unavailable`, `cannot_collect`, `no_cyber_vector`,
  `no_interference_detected`, `no_conjunction`; references — `no_such_asset`, `no_such_sensor`,
  `sensor_contended`, `unknown_action`, `unknown_command`. An order held by a gating rule is not
  refused: it returns status `pending_approval`.
- Input validation failures that are not order refusals are HTTP 400 with the reason (§3).

## 8. Limits

Capped before any work starts (GDS-06 NFR-15): 32 live sessions per process (oldest evicted); 100,000
event-log entries in a loaded save; 10,000 samples per time-span export.

---

## Departures from the legacy `design/07-api-and-networking.md`

- **Clock.** `play`/`pause`/`set_multiplier` became one `set_clock(running, rate)` on a
  server-authoritative lazy clock.
- **Branches.** `list_branches`/`switch_branch` were not built (GDS-08 departures).
- **Persistence.** `save(path)`/`load_save(path)` became "return the envelope to the client" and
  "load an envelope into a new session": the server writes no save file.
- **Force edits.** `edit_force` became `/force/tle`, `/force/bulk_import` and `/force/ground`.
- **Push.** WebSocket push was not built (§5).
- **Authentication and per-role authorization** (`design/07` §5 step 3) were deliberately not added;
  the trust model above replaces them for v1, and only five White-only checks exist (§4).

## Open Questions

- **OQ1 — White-only controls are not enforced server-side.** Start, parameters, clock, step,
  advance, rewind, undo, inject firing, force edits, seat assignment, Observer designation and
  loading a save accept any non-Observer seat. Under the trust model this is consistent (a liar
  bypasses any seat check), but it contradicts ADR-0016's wording and `design/07`'s authorization
  table, and the same cheap structural check already guards the five White-only actions. Should
  the remaining White Cell controls be refused for non-White seats (closing an accidental-misuse
  path in hot-seat and LAN play), or should ADR-0016 be revised to say "by UI convention"? Owner
  decision.
- **OQ2 — No API versioning.** Routes carry no version, and a client and server from different
  builds have no way to detect a mismatch. Acceptable while the client is served by the same server
  that hosts the API; a question only if a separate client ever appears.
- **OQ3 — ICD re-issue.** The ICD asks to be re-issued once GDS-07 and GDS-09 exist, to replace its
  "not specified" fields with citations of them (its own merge gate). That, plus its move under
  `docs/architecture/`, is `03`'s follow-up work (`BL-0294`).

## Merge gate (closed)

- [x] **Absorbed `design/07-api-and-networking.md`**, each required element explicitly:
  - **The `SessionAPI` boundary** (§1 boundary rule, §2 protocol) → §1–§2, restated as built.
  - **In-process / LAN contract equivalence** (§5 migration) → §6; the migration happened as
    planned, with the web transport instead of a separate server.
  - **The documented LAN trust model** (`CLAUDE.md` "LAN trust model") → §4, carried over in full
    and extended with what the server does and does not enforce.
  - State delivery (§3) → §5; authority and fog (§4) → §1 and §4; error contract (§6) → §7.
  Every difference is listed under "Departures".
- [x] **Reconciled with the shipped API.** The route table was taken from `ui_web/server.py` (91
  routes); the authorization rules were read from its guards, which is how OQ1 surfaced.
- [x] **ICD placement decided.** The ICD stays the authoritative interface inventory, as this
  document's companion, rather than being merged into it: an inventory of sixteen component
  interfaces and a contract for two programmatic ones are different jobs. **The file move under
  `docs/architecture/` is deferred to the single cleanup sweep** that retires `docs/design/` and
  build-spec (`BL-0292`), because 45 files link to its current path and moving it twice would mean
  two reference sweeps. Its re-issue against GDS-07/09 is `BL-0294`'s remaining work.
- [x] **DOM content (`BL-0293`).** No DOM section has API content.
- [x] **Decision recorded:** **this document is the authoritative API specification**, and
  `design/07-api-and-networking.md` is superseded in full. It is not edited here; it retires with
  the rest of `docs/design/` (apart from the ICD) once GDS-10 closes.

## Next

`GDS-10` (Requirements Traceability Matrix) may now begin. OQ1 needs an owner decision; OQ3 is `03`
follow-up work.
