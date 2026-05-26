"""In-process implementation of the SessionAPI (v1: one machine, one player).

Holds a registry of live SessionManagers keyed by session id. This is the exact boundary a
network transport will later wrap — the method bodies stay; only the call mechanism changes.
"""

from __future__ import annotations

from typing import Optional

from spacesim.content.vignette import list_vignettes, load_vignette
from spacesim.engine.orders import Order
from spacesim.session.api import Ack, CellView, OrderAck
from spacesim.session import aar
from spacesim.session.manager import SessionManager
from spacesim.session.redai import RedDoctrine


class InProcessSession:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionManager] = {}
        self._counter = 0

    # -- lifecycle -------------------------------------------------------------
    def list_vignettes(self) -> list[dict]:
        return list_vignettes()

    def load_vignette(self, vignette_id: str, overrides: Optional[dict] = None, seed: int = 0) -> str:
        vignette = load_vignette(vignette_id)
        self._counter += 1
        sid = f"sess-{self._counter}"
        self._sessions[sid] = SessionManager(vignette, overrides=overrides, seed=seed)
        return sid

    def set_parameter(self, session: str, param_id: str, value) -> Ack:
        mgr = self._sessions[session]
        if mgr.started:
            return Ack(ok=False, reason="cannot change parameters after start")
        overrides = dict(mgr.ctx.param_values)
        overrides[param_id] = value
        self._sessions[session] = SessionManager(mgr.vignette, overrides=overrides, seed=mgr.sim._seed)
        return Ack()

    def start(self, session: str) -> Ack:
        self._sessions[session].start()
        return Ack()

    # -- time control ----------------------------------------------------------
    def step(self, session: str, dt_sim_s: float) -> Ack:
        self._sessions[session].step(dt_sim_s)
        return Ack()

    def advance_to(self, session: str, t: int) -> Ack:
        self._sessions[session].advance_to(t)
        return Ack()

    def rewind_to(self, session: str, t: int) -> Ack:
        self._sessions[session].rewind_to(t)
        return Ack()

    def undo_last(self, session: str, n: int = 1) -> Ack:
        self._sessions[session].undo_last(n)
        return Ack()

    # -- injects & orders ------------------------------------------------------
    def add_tle(self, session: str, asset_id: str, line1: str, line2: str,
                owner: str = "blue", kind: str = "satellite") -> Ack:
        ok, reason = self._sessions[session].add_tle(asset_id, line1, line2, owner=owner, kind=kind)
        return Ack(ok=ok, reason=reason)

    def red_doctrine_step(self, session: str) -> list[OrderAck]:
        return RedDoctrine(self._sessions[session]).step()

    def fire_inject(self, session: str, inject) -> Ack:
        self._sessions[session].fire_inject(inject)
        return Ack()

    def issue_order(self, session: str, cell: str, order: Order) -> OrderAck:
        return self._sessions[session].issue_order(cell, order)

    # -- reads -----------------------------------------------------------------
    def get_view(self, session: str, cell: str) -> CellView:
        return self._sessions[session].get_view(cell)

    def get_scene(self, session: str, cell: str):
        return self._sessions[session].get_scene(cell)

    def get_telemetry(self, session: str, cell: str, asset: str):
        return self._sessions[session].get_telemetry(cell, asset)

    def get_series(self, session: str, cell: str, asset: str, param: str, t0=None, t1=None, n: int = 120):
        return self._sessions[session].get_series(cell, asset, param, t0=t0, t1=t1, n=n)

    def get_godview(self, session: str):
        return self._sessions[session].get_godview()

    def get_eventlog(self, session: str, since_seq: int = 0) -> list:
        return self._sessions[session].get_eventlog(since_seq)

    def objectives(self, session: str) -> dict:
        return self._sessions[session].objectives()

    # -- after-action review ---------------------------------------------------
    def aar_report(self, session: str):
        return aar.report(self._sessions[session])

    def aar_objectives_at(self, session: str, seq=None) -> dict:
        return aar.objectives_at(self._sessions[session], seq)
