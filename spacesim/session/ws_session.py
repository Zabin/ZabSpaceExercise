"""WebSocket transport stub for the P8 multiplayer seam (FUTURE-WORK §1 / build-spec/04 §10 M8).

Matches ``InProcessSession``'s interface exactly. To activate LAN multiplayer, replace the
``InProcessSession`` singleton in ``server.py`` with a ``WebSocketSession`` that routes each
method call through a WebSocket or HTTP-RPC channel to the authoritative server process.

Drop-in contract:
  - Method signatures are identical to ``InProcessSession``; replace the import in ``server.py``.
  - ``InProcessSession`` bodies stay as-is; only the call mechanism changes (local → network).
  - Session-id format can change (e.g. UUIDs); the server assigns and returns them.
  - All fog-of-war enforcement stays server-side (``CellController`` / ``SessionAPI``).
  - The ``get_eventlog(since_seq)`` method is the natural push-delta anchor; a WebSocket push
    channel replaces polling by streaming events as they are scheduled.

See FUTURE-WORK §1 for the full multiplayer roadmap and the three pre-requisites
(WebSocket transport, serializable Order, push-delta channel).
"""

from __future__ import annotations

from typing import Optional

from spacesim.engine.orders import Order
from spacesim.session.api import Ack, CellView, OrderAck


class WebSocketSession:
    """Stub: raises NotImplementedError on every call.  Implement the bodies for LAN multiplayer."""

    def __init__(self, server_url: str) -> None:
        self._url = server_url
        raise NotImplementedError("WebSocketSession is a seam stub — implement the network transport")

    # -- lifecycle -------------------------------------------------------------
    def list_vignettes(self) -> list[dict]:
        raise NotImplementedError

    def load_vignette(self, vignette_id: str, overrides: Optional[dict] = None, seed: int = 0) -> str:
        raise NotImplementedError

    def set_parameter(self, session: str, param_id: str, value) -> Ack:
        raise NotImplementedError

    def start(self, session: str) -> Ack:
        raise NotImplementedError

    # -- time control ----------------------------------------------------------
    def step(self, session: str, dt_sim_s: float) -> Ack:
        raise NotImplementedError

    def advance_to(self, session: str, t: int) -> Ack:
        raise NotImplementedError

    def rewind_to(self, session: str, t: int) -> Ack:
        raise NotImplementedError

    def undo_last(self, session: str, n: int = 1) -> Ack:
        raise NotImplementedError

    # -- injects & orders ------------------------------------------------------
    def add_tle(self, session: str, asset_id: str, line1: str, line2: str,
                owner: str = "blue", kind: str = "satellite") -> Ack:
        raise NotImplementedError

    def red_doctrine_step(self, session: str) -> list[OrderAck]:
        raise NotImplementedError

    def fire_inject(self, session: str, inject) -> Ack:
        raise NotImplementedError

    def issue_order(self, session: str, cell: str, order: Order) -> OrderAck:
        raise NotImplementedError

    def validate_order(self, session: str, cell: str, order: Order) -> OrderAck:
        raise NotImplementedError

    def list_orders(self, session: str, cell: str) -> list:
        raise NotImplementedError

    def cancel_order(self, session: str, cell: str, order_id: str) -> Ack:
        raise NotImplementedError

    def windows_ahead(self, session: str, cell: str, asset: str):
        raise NotImplementedError

    def next_contacts(self, session: str, cell: str) -> dict:
        raise NotImplementedError

    def recovery_status(self, session: str, cell: str, asset: str):
        raise NotImplementedError

    def begin_recovery(self, session: str, cell: str, asset: str, via: str) -> dict:
        raise NotImplementedError

    # -- SSN -------------------------------------------------------------------
    def submit_ssn_request(self, session: str, cell: str, intent: str, target: str,
                           regime: str, priority: str = "priority"):
        raise NotImplementedError

    def list_ssn_requests(self, session: str, cell: str) -> list:
        raise NotImplementedError

    def cancel_ssn_request(self, session: str, cell: str, rid: str) -> bool:
        raise NotImplementedError

    def ssn_coverage(self, session: str, cell: str, regime: str) -> dict:
        raise NotImplementedError

    def list_injects(self, session: str) -> list:
        raise NotImplementedError

    # -- reads -----------------------------------------------------------------
    def get_view(self, session: str, cell: str) -> CellView:
        raise NotImplementedError

    def get_scene(self, session: str, cell: str):
        raise NotImplementedError

    def get_telemetry(self, session: str, cell: str, asset: str):
        raise NotImplementedError

    def get_series(self, session: str, cell: str, asset: str, param: str, t0=None, t1=None,
                   n: int = 120, nominal: bool = False):
        raise NotImplementedError

    def get_godview(self, session: str):
        raise NotImplementedError

    def get_eventlog(self, session: str, since_seq: int = 0) -> list:
        raise NotImplementedError

    def objectives(self, session: str) -> dict:
        raise NotImplementedError

    # -- after-action review ---------------------------------------------------
    def aar_report(self, session: str):
        raise NotImplementedError

    def aar_objectives_at(self, session: str, seq=None) -> dict:
        raise NotImplementedError

    def aar_snapshot_at(self, session: str, seq=None) -> dict:
        raise NotImplementedError

    def alarms(self, session: str, cell: str) -> list:
        raise NotImplementedError

    # -- save / resume ---------------------------------------------------------
    def save(self, session: str) -> dict:
        raise NotImplementedError

    def load_save(self, state: dict) -> str:
        raise NotImplementedError
