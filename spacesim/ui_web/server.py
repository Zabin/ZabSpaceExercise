"""FastAPI server over the in-process SessionAPI.

Run: ``uvicorn spacesim.ui_web.server:app --reload`` then open http://127.0.0.1:8000/.
Everything the UI does goes through these endpoints; the browser never touches the engine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from spacesim.engine.orders import Order
from spacesim.session.api import Ack, CellView, OrderAck
from spacesim.session.inprocess import InProcessSession
from spacesim.session.scene import SceneView

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


class TleRequest(BaseModel):
    id: str
    line1: str
    line2: str
    owner: str = "blue"
    kind: str = "satellite"


class OrderRequest(BaseModel):
    cell: str
    actor: str
    action: str
    target: Optional[str] = None
    params: dict = {}


class CancelRequest(BaseModel):
    cell: str
    order_id: str


class RecoveryRequest(BaseModel):
    via: str


class SSNRequestBody(BaseModel):
    intent: str
    target: str
    regime: str
    priority: str = "priority"


class SSNCancelBody(BaseModel):
    request_id: str


def create_app(api: Optional[InProcessSession] = None) -> FastAPI:
    api = api or InProcessSession()
    app = FastAPI(title="Space Control & Orbital Warfare Exercise Simulator")

    def _require(sid: str) -> None:
        if sid not in api._sessions:
            raise HTTPException(status_code=404, detail=f"unknown session {sid}")

    @app.get("/api/vignettes")
    def list_vignettes() -> list[dict]:
        return api.list_vignettes()

    @app.get("/api/vignettes/{vid}/source", response_class=PlainTextResponse)
    def vignette_source(vid: str) -> str:
        """Return the raw YAML of a vignette (FUTURE-WORK §10.D.17 vignette inspector)."""
        for v in api.list_vignettes():
            if v["id"] == vid:
                return Path(v["path"]).read_text()
        raise HTTPException(status_code=404, detail=f"vignette {vid!r} not found")

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

    @app.post("/api/sessions/{sid}/force/tle")
    def add_tle(sid: str, req: TleRequest) -> Ack:
        _require(sid)
        return api.add_tle(sid, req.id, req.line1, req.line2, owner=req.owner, kind=req.kind)

    @app.post("/api/sessions/{sid}/red_step")
    def red_step(sid: str) -> list[OrderAck]:
        _require(sid)
        return api.red_doctrine_step(sid)

    @app.post("/api/sessions/{sid}/order")
    def issue_order(sid: str, req: OrderRequest) -> OrderAck:
        _require(sid)
        order = Order(cell=req.cell, actor=req.actor, action=req.action, target=req.target, params=req.params)
        return api.issue_order(sid, req.cell, order)

    @app.post("/api/sessions/{sid}/order/validate")
    def validate_order(sid: str, req: OrderRequest) -> OrderAck:
        """Dry-run an order: accepted (window/path) or rejected (reason), mutating no session state."""
        _require(sid)
        order = Order(cell=req.cell, actor=req.actor, action=req.action, target=req.target, params=req.params)
        return api.validate_order(sid, req.cell, order)

    @app.get("/api/sessions/{sid}/orders/{cell}")
    def list_orders(sid: str, cell: str) -> list:
        _require(sid)
        return api.list_orders(sid, cell)

    @app.post("/api/sessions/{sid}/cancel")
    def cancel_order(sid: str, req: CancelRequest) -> Ack:
        _require(sid)
        return api.cancel_order(sid, req.cell, req.order_id)

    @app.get("/api/sessions/{sid}/windows/{cell}/{asset}")
    def windows_ahead(sid: str, cell: str, asset: str) -> dict:
        _require(sid)
        r = api.windows_ahead(sid, cell, asset)
        if r is None:
            raise HTTPException(status_code=404, detail="no windows for this asset (fog/ownership)")
        return r

    @app.get("/api/sessions/{sid}/next_contacts/{cell}")
    def next_contacts(sid: str, cell: str) -> dict:
        """Fleet-rail countdown: next command/telemetry contact time per own satellite."""
        _require(sid)
        return api.next_contacts(sid, cell)

    @app.get("/api/sessions/{sid}/recovery/{cell}/{asset}")
    def recovery_status(sid: str, cell: str, asset: str) -> dict:
        _require(sid)
        r = api.recovery_status(sid, cell, asset)
        if r is None:
            raise HTTPException(status_code=404, detail="no recovery state (fog/ownership/no bus)")
        return r

    @app.post("/api/sessions/{sid}/recovery/{cell}/{asset}")
    def begin_recovery(sid: str, cell: str, asset: str, req: RecoveryRequest) -> dict:
        """Schedule the multi-pass safe-mode recovery chain over command-uplink windows."""
        _require(sid)
        return api.begin_recovery(sid, cell, asset, req.via)

    # ---- SSN (mock Space Surveillance Network) -------------------------------
    @app.post("/api/sessions/{sid}/ssn/{cell}/request")
    def ssn_submit(sid: str, cell: str, body: SSNRequestBody) -> dict:
        """Submit an SSN collection request — accepted (scheduled) or FAILED with reason."""
        _require(sid)
        ack = api.submit_ssn_request(sid, cell, body.intent, body.target, body.regime, body.priority)
        return {"ok": ack.ok, "id": ack.id, "reason": ack.reason, "state": ack.state,
                "assigned_sensor": ack.assigned_sensor,
                "collect_at": ack.collect_at, "product_at": ack.product_at}

    @app.get("/api/sessions/{sid}/ssn/{cell}/requests")
    def ssn_list(sid: str, cell: str) -> list:
        _require(sid)
        return api.list_ssn_requests(sid, cell)

    @app.post("/api/sessions/{sid}/ssn/{cell}/cancel")
    def ssn_cancel(sid: str, cell: str, body: SSNCancelBody) -> Ack:
        _require(sid)
        ok = api.cancel_ssn_request(sid, cell, body.request_id)
        return Ack(ok=ok)

    @app.get("/api/sessions/{sid}/ssn/{cell}/coverage")
    def ssn_coverage(sid: str, cell: str, regime: str) -> dict:
        _require(sid)
        return api.ssn_coverage(sid, cell, regime)

    @app.get("/api/sessions/{sid}/injects")
    def injects_list(sid: str) -> list:
        _require(sid)
        return api.list_injects(sid)

    @app.get("/api/sessions/{sid}/view/{cell}")
    def get_view(sid: str, cell: str) -> CellView:
        _require(sid)
        return api.get_view(sid, cell)  # fog applied server-side

    @app.get("/api/sessions/{sid}/scene/{cell}")
    def get_scene(sid: str, cell: str) -> SceneView:
        _require(sid)
        return api.get_scene(sid, cell)  # render-from-custody belief geometry

    @app.get("/api/sessions/{sid}/telemetry/{cell}/{asset}")
    def telemetry(sid: str, cell: str, asset: str) -> dict:
        _require(sid)
        r = api.get_telemetry(sid, cell, asset)
        if r is None:
            raise HTTPException(status_code=404, detail="no telemetry for this asset (fog/ownership)")
        return r

    @app.get("/api/sessions/{sid}/telemetry/{cell}/{asset}/{param}")
    def telemetry_series(sid: str, cell: str, asset: str, param: str,
                         t0: Optional[int] = None, t1: Optional[int] = None, n: int = 120,
                         nominal: bool = False) -> dict:
        _require(sid)
        r = api.get_series(sid, cell, asset, param, t0=t0, t1=t1, n=n, nominal=nominal)
        if r is None:
            raise HTTPException(status_code=404, detail="no such telemetry series")
        return r

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

    @app.get("/api/sessions/{sid}/aar")
    def aar_report(sid: str):
        _require(sid)
        return api.aar_report(sid)

    @app.get("/api/sessions/{sid}/aar/objectives")
    def aar_objectives_at(sid: str, seq: Optional[int] = None) -> dict:
        _require(sid)
        return api.aar_objectives_at(sid, seq)

    @app.get("/api/sessions/{sid}/aar/at")
    def aar_snapshot_at(sid: str, seq: Optional[int] = None) -> dict:
        _require(sid)
        return api.aar_snapshot_at(sid, seq)

    @app.get("/api/sessions/{sid}/aar/export.csv", response_class=PlainTextResponse)
    def aar_export_csv(sid: str) -> str:
        """Download the AAR as CSV for downstream PME analysis (FUTURE-WORK §10.E.20)."""
        from spacesim.session.aar import export_csv
        _require(sid)
        return export_csv(api.aar_report(sid))

    @app.get("/api/sessions/{sid}/aar/export.json")
    def aar_export_json(sid: str) -> dict:
        """Download the AAR as JSON (FUTURE-WORK §10.E.20). Mirrors /aar but pinned filename."""
        _require(sid)
        return api.aar_report(sid).model_dump()

    @app.get("/api/sessions/{sid}/alarms/{cell}")
    def alarms(sid: str, cell: str) -> list:
        _require(sid)
        return api.alarms(sid, cell)

    @app.get("/api/sessions/{sid}/save")
    def save(sid: str) -> dict:
        _require(sid)
        return api.save(sid)

    @app.post("/api/sessions/load_save")
    def load_save(state: dict) -> dict:
        return {"session": api.load_save(state)}

    if STATIC_DIR.exists():
        app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

    app.state.api = api
    return app


app = create_app()
