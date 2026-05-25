"""FastAPI server over the in-process SessionAPI.

Run: ``uvicorn spacesim.ui_web.server:app --reload`` then open http://127.0.0.1:8000/.
Everything the UI does goes through these endpoints; the browser never touches the engine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from spacesim.engine.orders import Order
from spacesim.session.api import Ack, CellView, OrderAck
from spacesim.session.inprocess import InProcessSession

STATIC_DIR = Path(__file__).resolve().parent / "static"


# -- request bodies ------------------------------------------------------------
class LoadRequest(BaseModel):
    vignette_id: str
    overrides: dict = {}
    seed: int = 0


class ParamRequest(BaseModel):
    param_id: str
    value: Any


class StepRequest(BaseModel):
    dt_sim_s: float


class TimeRequest(BaseModel):
    t: int


class UndoRequest(BaseModel):
    n: int = 1


class InjectRequest(BaseModel):
    inject: Any  # inject id (str) or {effects:[...]}


class OrderRequest(BaseModel):
    cell: str
    actor: str
    action: str
    target: Optional[str] = None
    params: dict = {}


def create_app(api: Optional[InProcessSession] = None) -> FastAPI:
    api = api or InProcessSession()
    app = FastAPI(title="Space Control & Orbital Warfare Exercise Simulator")

    def _require(sid: str) -> None:
        if sid not in api._sessions:
            raise HTTPException(status_code=404, detail=f"unknown session {sid}")

    @app.get("/api/vignettes")
    def list_vignettes() -> list[dict]:
        return api.list_vignettes()

    @app.post("/api/sessions")
    def load(req: LoadRequest) -> dict:
        sid = api.load_vignette(req.vignette_id, overrides=req.overrides or None, seed=req.seed)
        return {"session": sid}

    @app.post("/api/sessions/{sid}/param")
    def set_parameter(sid: str, req: ParamRequest) -> Ack:
        _require(sid)
        return api.set_parameter(sid, req.param_id, req.value)

    @app.post("/api/sessions/{sid}/start")
    def start(sid: str) -> Ack:
        _require(sid)
        return api.start(sid)

    @app.post("/api/sessions/{sid}/step")
    def step(sid: str, req: StepRequest) -> Ack:
        _require(sid)
        return api.step(sid, req.dt_sim_s)

    @app.post("/api/sessions/{sid}/advance")
    def advance(sid: str, req: TimeRequest) -> Ack:
        _require(sid)
        return api.advance_to(sid, req.t)

    @app.post("/api/sessions/{sid}/rewind")
    def rewind(sid: str, req: TimeRequest) -> Ack:
        _require(sid)
        return api.rewind_to(sid, req.t)

    @app.post("/api/sessions/{sid}/undo")
    def undo(sid: str, req: UndoRequest) -> Ack:
        _require(sid)
        return api.undo_last(sid, req.n)

    @app.post("/api/sessions/{sid}/inject")
    def inject(sid: str, req: InjectRequest) -> Ack:
        _require(sid)
        return api.fire_inject(sid, req.inject)

    @app.post("/api/sessions/{sid}/order")
    def issue_order(sid: str, req: OrderRequest) -> OrderAck:
        _require(sid)
        order = Order(cell=req.cell, actor=req.actor, action=req.action, target=req.target, params=req.params)
        return api.issue_order(sid, req.cell, order)

    @app.get("/api/sessions/{sid}/view/{cell}")
    def get_view(sid: str, cell: str) -> CellView:
        _require(sid)
        return api.get_view(sid, cell)  # fog applied server-side

    @app.get("/api/sessions/{sid}/godview")
    def get_godview(sid: str) -> dict:
        _require(sid)
        return api.get_godview(sid).model_dump()

    @app.get("/api/sessions/{sid}/eventlog")
    def get_eventlog(sid: str, since_seq: int = 0) -> list:
        _require(sid)
        return [e.model_dump() for e in api.get_eventlog(sid, since_seq)]

    @app.get("/api/sessions/{sid}/objectives")
    def objectives(sid: str) -> dict:
        _require(sid)
        return api.objectives(sid)

    if STATIC_DIR.exists():
        app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

    app.state.api = api
    return app


app = create_app()
