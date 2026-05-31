# API & Networking — Client Contract and the Multiplayer Seam

This document defines the **Session API**: the single boundary between the UI and the engine. In
v1 it is called **in-process** (one machine, one player). The same contract becomes the network
protocol when LAN multiplayer is added — so getting this boundary clean now is what makes the
future cheap.

## 1. The boundary rule
- The **UI depends on the Session API**, never on the engine directly.
- The **engine never imports UI or transport code.**
- Everything crossing the boundary is a **serializable message** (pydantic models → JSON), even
  in v1 where it's an in-process call. This means switching to a network transport changes the
  *transport*, not the *messages*.

## 2. Session API (abstract)

```python
class SessionAPI(Protocol):
    # --- lifecycle (White Cell) ---
    def list_vignettes(self) -> list[VignetteSummary]: ...
    def load_vignette(self, vignette_id: str) -> SessionId: ...
    def set_parameter(self, session: SessionId, param_id: str, value) -> Ack: ...
    def edit_force(self, session: SessionId, edit: ForceEdit) -> Ack: ...      # incl. add-TLE
    def start(self, session: SessionId) -> Ack: ...

    # --- time control (White Cell) ---
    def play(self, session: SessionId) -> Ack: ...
    def pause(self, session: SessionId) -> Ack: ...
    def set_multiplier(self, session: SessionId, mult: float) -> Ack: ...
    def step(self, session: SessionId, dt_sim_s: int) -> Ack: ...
    def rewind_to(self, session: SessionId, t: SimTime) -> Ack: ...
    def undo_last(self, session: SessionId, n: int = 1) -> Ack: ...
    def list_branches(self, session: SessionId) -> list[BranchInfo]: ...
    def switch_branch(self, session: SessionId, branch: BranchId) -> Ack: ...

    # --- injects (White Cell) ---
    def fire_inject(self, session: SessionId, inject: Inject) -> Ack: ...

    # --- player actions (Red / Blue, also White when driving a side) ---
    def issue_order(self, session: SessionId, cell: Cell, order: Order) -> OrderAck: ...
    def cancel_order(self, session: SessionId, cell: Cell, order_id: str) -> Ack: ...

    # --- reads (all cells; server applies fog-of-war per cell) ---
    def get_view(self, session: SessionId, cell: Cell) -> CellView: ...        # fog-filtered
    def get_godview(self, session: SessionId) -> WorldState: ...               # White only
    def get_eventlog(self, session: SessionId, since_seq: int = 0) -> list[EventLogEntry]: ...

    # --- persistence ---
    def save(self, session: SessionId, path: str) -> Ack: ...
    def load_save(self, path: str) -> SessionId: ...
```

`OrderAck` carries acceptance/rejection + reason + the scheduled execution window, so the UI can
show "queued for 06:14:00Z via STATION-BRAVO" or the rejection reason.

## 3. State delivery: pull + push
- **v1 (in-process):** the UI calls `get_view(cell)` after each interaction and on a timer; cheap
  because it's a function call.
- **Future (network):** the server **pushes** view deltas to each client over WebSocket whenever
  state changes, keyed off `EventLog` sequence numbers, so clients stay live without polling.
  `get_eventlog(since_seq)` already expresses the delta contract — implement reads that way from
  day one and push becomes trivial.

## 4. Authority & fog-of-war live at the boundary
- The **SessionManager is authoritative** in both v1 and multiplayer. Clients/UI send *intents*
  (`issue_order`, `fire_inject`); they never mutate state directly.
- **Fog-of-war is applied server-side** in `get_view`/push, never client-side. A Red client must
  be *incapable* of receiving Blue's hidden state — enforce it at the API, so an untrusted future
  network client cannot cheat. (In v1 this also cleanly powers the single-player cell-switcher.)

## 5. The multiplayer migration (documented, not built)
When LAN multiplayer is wanted:
1. Wrap `SessionAPI` in a transport server (FastAPI/WebSocket if the web UI was chosen — then
   it's already there; or a small asyncio/gRPC server for the desktop UI).
2. Run the engine in the **server** process; Red/Blue/White become thin clients that call the
   same API methods over the wire and render the `CellView` they're sent.
3. Add authentication/role assignment (which connection is Red vs. Blue vs. White) and per-role
   authorization on the White-only methods.
4. Nothing in `engine/` changes. The determinism, fog filtering, and queuing already assume an
   authoritative server.

| Method group | v1 caller | Multiplayer caller | Authorization |
|---|---|---|---|
| lifecycle/time/inject | local White UI | White client | White only |
| issue/cancel order | local UI (any cell) | Red/Blue/White clients | own cell only |
| get_view | local UI | each client | own cell; White any |
| get_godview | local White UI | White client | White only |

## 6. Error & validation contract
- All mutating calls return an `Ack{ok, reason}` or `OrderAck`; rejections always include a
  human-readable `reason` (surfaced in the UI).
- TLE import errors, insufficient-fuel, ROE-blocked, and no-window-available are all normal
  rejection paths, not exceptions — the UI treats them as feedback.
- Reads are side-effect-free and safe to call at any time/multiplier.
