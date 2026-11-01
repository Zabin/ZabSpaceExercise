"""FastAPI server over the in-process SessionAPI.

Run: ``python3 -m spacesim.ui_web`` — reads host/port/reload from
``spacesim.config.yaml`` at the repo root (defaults to 127.0.0.1:8000).
The bare ``uvicorn spacesim.ui_web.server:app`` CLI also works but ignores
the YAML; pass ``--host``/``--port`` directly to override.
Everything the UI does goes through these endpoints; the browser never touches the engine.
"""

from __future__ import annotations

import json
import math
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Literal, Optional

import re

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator

from spacesim.engine.orders import Order
from spacesim.session import ephemeris
from spacesim.session.api import Ack, CellView, OrderAck
from spacesim.session.inprocess import (PLAYBACK_REFUSED, InProcessSession, PlaybackSeatRefused,
                                        playback_seat_decision)
from spacesim.session.aar import PlaybackSession
from spacesim.session.scene import SceneView

STATIC_DIR = Path(__file__).resolve().parent / "static"

# Audit Jun 2026 §D2 — server-side validation for client-supplied identifiers
# that flow into rendered DOM, eventlog payloads, and the YAML loader.
_ID_RE = re.compile(r"^[A-Za-z0-9_.\-]{1,64}$")


def _validate_id(value: str, *, field: str) -> str:
    if not isinstance(value, str) or not _ID_RE.match(value):
        raise ValueError(f"{field} must match {_ID_RE.pattern}")
    return value


_SEAT_RE = re.compile(r"^[A-Za-z0-9_. -]{0,64}$")


def _validate_seat(value: Optional[str], *, field: str) -> Optional[str]:
    """IP-1160 — operator-seat names: letters, digits, ``-``, ``_``, ``.`` and space; at most 64."""
    if value is not None and not _SEAT_RE.match(value):
        raise ValueError(f"{field} must match {_SEAT_RE.pattern}")
    return value


def _first_nonfinite(value: Any, path: str = "body") -> Optional[str]:
    """IP-1082 (NFR-1600, FR-4330) — the path of the first ``NaN``/``Infinity``/``-Infinity`` number
    anywhere in a decoded JSON value (nested lists/objects included), else None. Starlette's JSON
    parser accepts those literals, so a pydantic ``float``/``int`` field would otherwise admit them."""
    if isinstance(value, float):
        return None if math.isfinite(value) else path
    if isinstance(value, dict):
        for k, v in value.items():
            hit = _first_nonfinite(v, f"{path}.{k}")
            if hit:
                return hit
    elif isinstance(value, list):
        for i, v in enumerate(value):
            hit = _first_nonfinite(v, f"{path}[{i}]")
            if hit:
                return hit
    return None


# Fields that must be JSON numbers: pydantic would coerce ``true`` to 1.0 / 1 (IP-1082, review F4).
_NUMBER_ONLY = {
    "/clock": ("rate",), "/step": ("dt_sim_s",), "/advance": ("t",), "/rewind": ("t",), "/undo": ("n",),
    "/aar/playback/start": ("speed",), "/aar/playback/advance": ("dt_s",), "/aar/playback/speed": ("speed",),
    "/inject": ("at_sim_t",), "/edit": ("at_sim_t",),      # IP-1084 — a boolean would coerce to 1
}


def _body_problem(decoded: Any, path: str) -> Optional[str]:
    """The first refusal reason for a decoded JSON body, or None: a non-finite number anywhere, or a
    boolean where one of the route's numeric fields is expected."""
    hit = _first_nonfinite(decoded)
    if hit:
        return f"{hit}: a non-finite number (NaN or Infinity) is not allowed"
    if isinstance(decoded, dict):
        for suffix, fields in _NUMBER_ONLY.items():
            if path.endswith(suffix):
                for f in fields:
                    if isinstance(decoded.get(f), bool):
                        return f"body.{f}: must be a number, not a boolean"
    return None


async def _body_refusal(request: Request) -> Optional[str]:
    """The reason to refuse this request's JSON body, or None. A body that is not JSON is left to
    the route's own validation."""
    raw = await request.body()
    if not raw:
        return None
    try:
        decoded = json.loads(raw)
    except ValueError:
        return None
    return _body_problem(decoded, request.url.path)


async def _refuse_nonfinite(request: Request) -> None:
    """The one place the non-finite policy lives: a 400 naming the field, before any state changes."""
    why = await _body_refusal(request)
    if why:
        raise HTTPException(status_code=400, detail=why)


# -- request bodies ------------------------------------------------------------
class LoadRequest(BaseModel):
    vignette_id: str
    overrides: dict = {}
    seed: int = 0
    classification: Optional[str] = None  # IP-1120 — White-Cell override; None = vignette default


class DraftRequest(BaseModel):
    title: str = "Untitled Draft"


class SaveVignetteRequest(BaseModel):
    vignette_id: str
    title: str
    classification: Optional[str] = None
    # IP-1200 (FR-5510) — save-as-scenario, additive; default preserves IP-1173's existing
    # draft-save behavior for every existing caller.
    as_scenario: bool = False

    @field_validator("vignette_id")
    @classmethod
    def _vid_charset(cls, v: str) -> str:
        return _validate_id(v, field="SaveVignetteRequest.vignette_id")


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
    at_sim_t: Optional[int] = None   # FW §11.D.19: optional future-dated scheduling (µs UTC)


class InjectEditRequest(BaseModel):
    """IP-1066 (FR-4450) — new effects and/or a new fire time (µs UTC) for a pending inject."""
    effects: Optional[list] = None
    at_sim_t: Optional[int] = None


class TleRequest(BaseModel):
    id: str
    line1: str
    line2: str
    owner: str = "blue"
    kind: str = "satellite"

    @field_validator("id")
    @classmethod
    def _id_charset(cls, v: str) -> str:
        return _validate_id(v, field="TleRequest.id")


class BulkImportRequest(BaseModel):
    """IP-1190 (FR-5220) — multi-object TLE / CCSDS OMM (KVN) bulk import, alongside (not
    replacing) ``TleRequest``'s single-object path. ``assignments`` maps each object's parsed
    ``raw_id`` to {"asset_id": ..., "owner": ..., "kind": ...}."""
    format: Literal["tle", "omm"]
    content: str
    assignments: dict[str, dict] = {}


class OrderRequest(BaseModel):
    cell: str
    actor: str
    action: str
    target: Optional[str] = None
    params: dict = {}
    # IP-1160 (FR-3520) — the OPERATOR seat (key of the Role Assignment registry), not the console
    # seat ``cell``. Optional: omitting it skips the role-scope gate (client-asserted, LAN trust).
    seat: Optional[str] = None

    @field_validator("seat")
    @classmethod
    def _seat_charset(cls, v: Optional[str]) -> Optional[str]:
        return _validate_seat(v, field="OrderRequest.seat")

    @field_validator("actor")
    @classmethod
    def _actor_charset(cls, v: str) -> str:
        # Allow "auto" as the sentinel for sensor-auto-select.
        if v == "auto":
            return v
        return _validate_id(v, field="OrderRequest.actor")

    @field_validator("target")
    @classmethod
    def _target_charset(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return v
        return _validate_id(v, field="OrderRequest.target")


class CancelRequest(BaseModel):
    cell: str
    order_id: str


class GateDecisionRequest(BaseModel):
    """IP-1270 (FR-3430) — cell is the caller's own seat (must match the gate's required_role)."""
    cell: str
    order_id: str
    approve: bool


class RoeChangeRequest(BaseModel):
    """IP-1270 (FR-3440) — cell is the caller's own seat (must be "white"); target_cell is the
    cell the ROE flag applies to."""
    cell: str
    target_cell: str
    flag: str
    value: bool


class PlaybackStartRequest(BaseModel):
    """IP-1280 (FR-7330) — viewpoint is "truth" or a cell that participated in the recorded
    exercise."""
    viewpoint: str = "truth"
    speed: float = 1.0


class PlaybackAdvanceRequest(BaseModel):
    dt_s: float


class PlaybackViewpointRequest(BaseModel):
    viewpoint: str


class PlaybackSpeedRequest(BaseModel):
    speed: float


class ManeuverComputeRequest(BaseModel):
    cell: str
    actor: str
    mode: str          # eci | lvlh | finite_burn | target_coe | hohmann | plane_change
    params: dict = {}


class JamComputeRequest(BaseModel):
    cell: str
    actor: str
    params: dict = {}    # modulation, power_w, bandwidth_hz, victim_bandwidth_hz, success_prob


class EngageComputeRequest(BaseModel):
    cell: str
    actor: str
    target: str
    params: dict = {}   # success_prob, salvo_n, interceptor_dv_ms


class CyberComputeRequest(BaseModel):
    cell: str
    actor: str
    target: str
    params: dict = {}   # vector, payload, dwell_s, persistence_h


class SigintComputeRequest(BaseModel):
    cell: str
    actor: str
    params: dict = {}   # band, intercept_mode, dwell_s, n_collectors


class RecoveryRequest(BaseModel):
    via: str


class SSNRequestBody(BaseModel):
    intent: str
    target: str
    regime: str
    priority: str = "priority"


class ClockRequest(BaseModel):
    """Server-authoritative real-time clock control (multiplayer)."""
    running: bool
    rate: float = 1.0


class ObserverViewRequest(BaseModel):
    """IP-1130 — cell is the caller's own seat (must be "white"); designation is "godview" or a
    cell name (the view the Observer seat will be served)."""
    cell: str
    designation: str


class RoleAssignmentRequest(BaseModel):
    """IP-1151 — cell is the caller's own seat (must be "white"); binds seat to
    {asset_or_constellation, role} against the vignette's declared roles_needed."""
    cell: str
    seat: str
    asset_or_constellation: str
    role: str = "both"

    @field_validator("seat")
    @classmethod
    def _seat_charset(cls, v: str) -> str:
        return _validate_seat(v, field="RoleAssignmentRequest.seat")


class SSNCancelBody(BaseModel):
    request_id: str


class GroundAssetRequest(BaseModel):
    """IP-1174 (FR-5140) — lat/long asset entry, the ground-based sibling of ``TleRequest``.
    BL-0125 remediation: ``owner`` shares ``Asset``'s own vocabulary (blue/red/neutral) instead of
    an unconstrained ``str``, so a malformed owner rejects at the request-schema level (422)
    rather than reaching ``Asset(...)`` unvalidated."""
    id: str
    lat_deg: float
    lon_deg: float
    owner: Literal["blue", "red", "neutral"] = "blue"
    kind: str = "ground_station"

    @field_validator("id")
    @classmethod
    def _id_charset(cls, v: str) -> str:
        return _validate_id(v, field="GroundAssetRequest.id")

    @field_validator("lat_deg")
    @classmethod
    def _lat_range(cls, v: float) -> float:
        """BL-0124 remediation — reject an out-of-range latitude (e.g. 999) at the request
        schema level instead of silently storing it."""
        if not -90.0 <= v <= 90.0:
            raise ValueError(f"lat_deg must be in [-90, 90], got {v}")
        return v

    @field_validator("lon_deg")
    @classmethod
    def _lon_range(cls, v: float) -> float:
        if not -180.0 <= v <= 180.0:
            raise ValueError(f"lon_deg must be in [-180, 180], got {v}")
        return v


class CreatorStateRequest(BaseModel):
    """IP-1174 (FR-5120) — the JSON view's write: a full replacement asset list."""
    assets: list[dict]


class CreatorAssetPatchRequest(BaseModel):
    """IP-1174 (FR-5150) — the asset menu's edit operation; any subset of Asset's own fields."""
    patch: dict


class SeatDeclarationRequest(BaseModel):
    """IP-1174 (FR-5160) — seat-count declaration, one cell at a time. ``cell`` here is the
    *target* cell the seats are declared for (white/blue/red) — the caller's own identity is
    carried separately, as the query-param ``cell`` every other mutating route already uses
    (see ``declare_seats`` below; this remediation closes BL-0123)."""
    cell: str
    count: int


@contextmanager
def _vignette_load_errors(vid: str):
    """IP-1310 (FS-131 OQ4) — map a refused vignette load to a client error, never a 500:
    invalid content → 400 ``invalid_vignette`` with every problem; unknown id → 404; an id the
    path guard refuses → 400."""
    from spacesim.content.vignette import VignetteValidationError
    try:
        yield
    except VignetteValidationError as exc:
        raise HTTPException(status_code=400, detail={
            "error": "invalid_vignette", "vignette": exc.vignette_id,
            "message": exc.message, "problems": exc.problems,
        }) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"vignette {vid!r} not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def create_app(api: Optional[InProcessSession] = None) -> FastAPI:
    api = api or InProcessSession()
    app = FastAPI(title="Space Control & Orbital Warfare Exercise Simulator")

    def _require(sid: str) -> None:
        if sid not in api._sessions:
            raise HTTPException(status_code=404, detail=f"unknown session {sid}")

    def _reject_observer(cell: Optional[str]) -> None:
        """IP-1130 — structural rejection at the server boundary, independent of what the UI
        offers: any request whose caller identifies itself as the Observer seat is refused before
        it reaches SessionManager, whether or not that request came through the UI at all (FS-113
        Security Considerations). Matches this repository's documented client-side-trust LAN model
        (CLAUDE.md) — the caller asserts its own seat, the same way every cell/order carries its
        own ``cell`` today; this adds no new authentication, only a new rejection rule."""
        if cell == "observer":
            raise HTTPException(status_code=403, detail="the Observer seat is read-only")

    def _require_white(cell: Optional[str]) -> None:
        """IP-1068 (FR-4310/FR-4320) — White Cell controls are refused unless the request names
        the ``white`` seat (Blue, Red, Observer, or no seat at all). Same client-asserted-seat trust
        level as ``_reject_observer`` — a structural rejection, not authentication."""
        if cell != "white":
            raise HTTPException(status_code=403,
                                detail="White Cell control: refused unless the request names the white seat")

    async def _finite_json_guard(request: Request, sid: Optional[str] = None,
                                 cell: Optional[str] = None) -> None:
        """IP-1082 — dependency on every White control route (pinned by a route-table test): the
        session (404) and the seat rule (403, FR-4310) answer first, then a non-finite number
        anywhere in the JSON body is a 400 with a reason (never a 500 or a poisoned clock)."""
        if sid is not None:
            _require(sid)
        _require_white(cell)
        await _refuse_nonfinite(request)

    async def _finite_json_guard_open(request: Request, sid: Optional[str] = None) -> None:
        """IP-1082 (F1) — the same non-finite check for every other mutating route (orders, compute
        previews, SSN, recovery, gate/ROE, session creation): not White-only, so the route keeps its
        own seat rule; 404 for an unknown session first, then a 400 naming the non-finite field."""
        if sid is not None:
            _require(sid)
        await _refuse_nonfinite(request)

    async def _inject_finite_guard(request: Request, sid: str, cell: Optional[str] = None) -> None:
        """IP-1082 (F1) — pending-inject cancel/edit: White-only with this family's own 403 wording
        (``only White Cell may ...``), kept; then the shared check."""
        _require(sid)
        if cell != "white":
            verb = "cancel" if request.url.path.endswith("/cancel") else "edit"
            raise HTTPException(status_code=403, detail=f"only White Cell may {verb} an inject")
        await _refuse_nonfinite(request)

    async def _playback_finite_guard(request: Request, sid: str, cell: Optional[str] = None) -> None:
        """IP-1082 (FR-7330) — the same check for the AAR playback value routes, plus the speed range
        ``|speed| <= PlaybackSession.MAX_SPEED``. Those routes are not White-only, so the seat rule is
        IP-1077's own: a seat it refuses still gets its 403 first."""
        _require(sid)
        why = await _body_refusal(request)
        if why is None:
            raw = await request.body()
            body = json.loads(raw) if raw else None
            sp = body.get("speed") if isinstance(body, dict) else None
            if isinstance(sp, (int, float)) and abs(sp) > PlaybackSession.MAX_SPEED:
                why = (f"body.speed: {sp!r} is outside the playback speed range "
                       f"[-{PlaybackSession.MAX_SPEED:g}, {PlaybackSession.MAX_SPEED:g}]")
        if why:
            action = request.url.path.rsplit("/", 1)[-1]
            raw = await request.body()
            try:
                body = json.loads(raw)
            except ValueError:
                body = None
            requested = body.get("viewpoint") if isinstance(body, dict) else None
            seat = playback_seat_decision(cell, action, requested, api._playback_current(sid))
            if seat:
                raise HTTPException(status_code=403, detail=seat)
            raise HTTPException(status_code=400, detail=why)

    def _refuse_player_seat_on_create(cell: Optional[str]) -> None:
        """IP-1072 (FR-4320 as extended) — creating a session or a Vignette Creator draft is refused
        when the request *names* a player seat (blue/red/observer). Unlike ``_require_white`` an
        absent seat is allowed: creation precedes seat selection in the hot-seat flow and in the
        documented curl recipes/tools, and the requirement speaks of a request that names a
        non-White seat. The asymmetry is deliberate. Same client-asserted-seat trust level."""
        if cell in ("blue", "red", "observer"):
            raise HTTPException(status_code=403,
                                detail="White Cell control: sessions are created by the white seat, not "
                                       f"the {cell} seat")

    @app.post("/api/sessions/{sid}/observer/view", dependencies=[Depends(_finite_json_guard)])
    def set_observer_view(sid: str, req: ObserverViewRequest, cell: Optional[str] = None) -> Ack:
        """IP-1074 (FR-4320) — White-Cell-only by the *query* seat (403 otherwise). The body ``cell``
        is accepted for compatibility but is not authority: White is passed to the session layer,
        whose own check stays as defence in depth."""
        _require(sid); _require_white(cell)
        return api.set_observer_view(sid, "white", req.designation)

    @app.get("/api/sessions/{sid}/observer/view")
    def observer_view(sid: str) -> dict:
        _require(sid)
        return api.get_observer_view(sid).model_dump()

    @app.get("/api/sessions/{sid}/observer/designation")
    def observer_designation(sid: str) -> dict:
        """So the client can fetch /godview or /view/{cell} directly (the exact same call every
        other seat already makes) instead of parsing a merged response shape."""
        _require(sid)
        return {"designation": api.observer_designation(sid)}

    @app.post("/api/sessions/{sid}/roles/assign", dependencies=[Depends(_finite_json_guard)])
    def assign_role(sid: str, req: RoleAssignmentRequest, cell: Optional[str] = None) -> Ack:
        """IP-1151/IP-1074 (FR-4320) — White-Cell-only by the *query* seat (403 for Blue, Red,
        Observer or no seat). The body ``cell`` is accepted for compatibility but is not authority;
        the session layer's own White check stays as defence in depth."""
        _require(sid); _require_white(cell)
        return api.assign_role(sid, "white", req.seat, req.asset_or_constellation, req.role)

    @app.get("/api/sessions/{sid}/roles/staffing")
    def staffing_report(sid: str) -> list[dict]:
        _require(sid)
        return api.staffing_report(sid)

    @app.get("/api/sessions/{sid}/roles/scope")
    def role_scope(sid: str, seat: Optional[str] = None, cell: Optional[str] = None) -> dict:
        """IP-1160 (FR-3510) — without ``seat``: ONLY the static verb->scope table (no assets, no
        assignments; nothing session-specific, so safe for any caller). With ``seat`` the caller
        must name its console seat (``cell``: white/blue/red; the Observer has none -> 403) and gets
        that operator seat's scope fog-scoped to the cell: Blue/Red see only their own cell's
        role-gated assets and an unbound answer for anything else; White sees every asset."""
        _require(sid)
        if not seat:
            return {"verbs": api.role_scope(sid, None)["verbs"]}
        try:
            _validate_seat(seat, field="seat")
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        if cell not in ("white", "blue", "red"):
            raise HTTPException(status_code=403, detail="a seat-specific scope read must name the white, blue or red console seat")
        return api.role_scope(sid, seat, cell)

    @app.get("/api/vignettes")
    def list_vignettes() -> list[dict]:
        return api.list_vignettes()

    @app.get("/api/vignettes/{vid}/source", response_class=PlainTextResponse)
    def vignette_source(vid: str) -> str:
        """Return the raw YAML of a vignette (FUTURE-WORK §10.D.17 vignette inspector)."""
        for v in api.list_vignettes():
            if v["id"] == vid:
                return Path(v["path"]).read_text(encoding="utf-8")
        raise HTTPException(status_code=404, detail=f"vignette {vid!r} not found")

    @app.get("/api/vignettes/{vid}/tutorial")
    def vignette_tutorial(vid: str) -> dict:
        """Structured per-cell player tutorial for the in-UI Tutorial panel — parsed by pydantic,
        not regex-scraped from YAML, so blue/red steps never bleed into each other."""
        from spacesim.content.vignette import load_vignette
        with _vignette_load_errors(vid):
            return load_vignette(vid).tutorial or {}

    @app.get("/api/sessions/{sid}/brief/{cell}")
    def session_brief(sid: str, cell: str) -> dict:
        """Per-cell mission brief: situation, mission, friendly forces, threat picture, deadline,
        ROE, success criteria, tool tips.  Pulls vignette.intro_brief.{cell} + runtime objective
        deadlines + computed ROE.  White sees both cells."""
        return api.session_brief(sid, cell)

    @app.post("/api/sessions", dependencies=[Depends(_finite_json_guard_open)])
    def load(req: LoadRequest, cell: Optional[str] = None) -> dict:
        _refuse_player_seat_on_create(cell)
        with _vignette_load_errors(req.vignette_id):
            sid = api.load_vignette(req.vignette_id, overrides=req.overrides or None, seed=req.seed,
                                    classification=req.classification)
        return {"session": sid, "classification": api.classification(sid)}

    @app.post("/api/sessions/draft", dependencies=[Depends(_finite_json_guard_open)])
    def create_draft(req: DraftRequest, cell: Optional[str] = None) -> dict:
        """IP-1173 (FR-5110) — open a Vignette Creator draft session: an unstarted SessionManager
        backed by a near-empty Vignette, registered/evicted the same way a normal session is."""
        _refuse_player_seat_on_create(cell)
        sid = api.create_draft_session(title=req.title)
        return {"session": sid}

    @app.post("/api/sessions/{sid}/save_vignette", dependencies=[Depends(_finite_json_guard)])
    def save_vignette(sid: str, req: SaveVignetteRequest, cell: Optional[str] = None) -> dict:
        """IP-1173 (FR-5110) — the only route that writes an authored vignette file. Works for
        any session (draft or normal); no partial file is ever written by any other path."""
        _require(sid); _require_white(cell)
        try:
            path = api.save_vignette(sid, req.vignette_id, req.title,
                                     classification=req.classification or "UNCLASSIFIED-TRAINING",
                                     as_scenario=req.as_scenario)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        return {"vignette_id": req.vignette_id, "path": path}

    @app.get("/api/sessions")
    def list_sessions() -> list[dict]:
        """Multiplayer discovery: list every live session so other tabs/machines can join one."""
        return api.list_sessions()

    @app.post("/api/sessions/{sid}/clock", dependencies=[Depends(_finite_json_guard)])
    def set_clock(sid: str, req: ClockRequest, cell: Optional[str] = None) -> dict:
        """Arm/disarm the server-authoritative real-time clock (multiplayer)."""
        _require(sid); _require_white(cell)
        r = api.set_clock(sid, req.running, req.rate)
        if isinstance(r, Ack):          # IP-1082 — a refused rate is a 400 with the reason, nothing changed
            raise HTTPException(status_code=400, detail=r.reason)
        return r

    @app.get("/api/sessions/{sid}/clock")
    def get_clock(sid: str) -> dict:
        _require(sid)
        return api.clock_state(sid)

    @app.post("/api/sessions/{sid}/param", dependencies=[Depends(_finite_json_guard)])
    def set_parameter(sid: str, req: ParamRequest, cell: Optional[str] = None) -> Ack:
        _require(sid); _require_white(cell)
        return api.set_parameter(sid, req.param_id, req.value)

    @app.post("/api/sessions/{sid}/start", dependencies=[Depends(_finite_json_guard)])
    def start(sid: str, cell: Optional[str] = None) -> Ack:
        _require(sid); _require_white(cell)
        return api.start(sid)

    @app.post("/api/sessions/{sid}/step", dependencies=[Depends(_finite_json_guard)])
    def step(sid: str, req: StepRequest, cell: Optional[str] = None) -> Ack:
        """IP-1076 (FR-4330, NFR-1600) — ``dt_sim_s`` must be finite and >= 0 and the result must not
        pass ``start_epoch`` + 366 days; anything else is a 400 with a reason, nothing changed."""
        _require(sid); _require_white(cell)
        ack = api.step(sid, req.dt_sim_s)
        if not ack.ok:
            raise HTTPException(status_code=400, detail=ack.reason)
        return ack

    @app.post("/api/sessions/{sid}/advance", dependencies=[Depends(_finite_json_guard)])
    def advance(sid: str, req: TimeRequest, cell: Optional[str] = None) -> Ack:
        """IP-1076 (FR-4330, NFR-1600) — ``t`` must lie in ``[now, start_epoch + 366 days]``; anything
        else is a 400 naming the span, nothing changed."""
        _require(sid); _require_white(cell)
        ack = api.advance_to(sid, req.t)
        if not ack.ok:
            raise HTTPException(status_code=400, detail=ack.reason)
        return ack

    @app.post("/api/sessions/{sid}/rewind", dependencies=[Depends(_finite_json_guard)])
    def rewind(sid: str, req: TimeRequest, cell: Optional[str] = None) -> Ack:
        """IP-1074 (FR-4310, NFR-1600) — ``t`` must lie in ``[start_epoch, now]`` (``GET /clock``
        carries ``start_epoch``); anything else is a 400 naming the span, nothing changed."""
        _require(sid); _require_white(cell)
        ack = api.rewind_to(sid, req.t)
        if not ack.ok:
            raise HTTPException(status_code=400, detail=ack.reason)
        return ack

    @app.post("/api/sessions/{sid}/undo", dependencies=[Depends(_finite_json_guard)])
    def undo(sid: str, req: UndoRequest, cell: Optional[str] = None) -> Ack:
        _require(sid); _require_white(cell)
        ack = api.undo_last(sid, req.n)
        if not ack.ok:
            raise HTTPException(status_code=400, detail=ack.reason)
        return ack

    @app.post("/api/sessions/{sid}/inject", dependencies=[Depends(_finite_json_guard)])
    def inject(sid: str, req: InjectRequest, cell: Optional[str] = None) -> Ack:
        """Fire or schedule an inject. IP-1063 (BL-0188/BL-0129): a malformed inject, or one whose
        FR-4430 target precondition fails (e.g. an `anomaly` on an asset with no bus), is a 400
        naming the reason, with nothing applied — the console's `api.post` only surfaces non-2xx."""
        _require(sid); _require_white(cell)
        ack = api.fire_inject(sid, req.inject, at_sim_t=req.at_sim_t)
        if not ack.ok:
            raise HTTPException(status_code=400, detail=ack.reason)
        return ack

    @app.get("/api/sessions/{sid}/inject_library")
    def inject_library_list(sid: str) -> list:
        """FW §11.D.19 — return the reusable inject templates with their effects payload."""
        _require(sid)
        return api.inject_library()

    @app.post("/api/sessions/{sid}/force/tle", dependencies=[Depends(_finite_json_guard)])
    def add_tle(sid: str, req: TleRequest, cell: Optional[str] = None) -> Ack:
        _require(sid); _require_white(cell)
        return api.add_tle(sid, req.id, req.line1, req.line2, owner=req.owner, kind=req.kind)

    @app.post("/api/sessions/{sid}/force/bulk_import", dependencies=[Depends(_finite_json_guard)])
    def bulk_import(sid: str, req: BulkImportRequest, cell: Optional[str] = None) -> list[dict]:
        """IP-1190 (FR-5220) — multi-object TLE/CCSDS OMM (KVN) import, additive alongside
        `force/tle` above. A file recognized as neither format (Design Decision 1) surfaces as
        a 400, not a per-object report."""
        _require(sid); _require_white(cell)
        try:
            return api.bulk_import(sid, req.format, req.content, req.assignments)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    # -- Vignette Creator UI surfaces (IP-1174) --------------------------------
    @app.post("/api/sessions/{sid}/force/ground", dependencies=[Depends(_finite_json_guard)])
    def add_ground_asset(sid: str, req: GroundAssetRequest, cell: Optional[str] = None) -> Ack:
        """FR-5140 — lat/long asset entry, the ground-based sibling of ``force/tle`` above."""
        _require(sid); _require_white(cell)
        return api.add_ground_asset(sid, req.id, req.lat_deg, req.lon_deg,
                                    owner=req.owner, kind=req.kind)

    @app.get("/api/ground_sites")
    def ground_sites() -> list[dict]:
        """FR-5140 — the curated site list offered before free-entry coordinates."""
        from spacesim.content.ground_sites import load_ground_sites
        return load_ground_sites()

    @app.get("/api/sessions/{sid}/creator/state")
    def creator_state(sid: str) -> dict:
        """FR-5120 — the JSON view's read: every asset, exactly as the form UI would also see it."""
        _require(sid)
        return api.creator_state(sid)

    @app.put("/api/sessions/{sid}/creator/state", dependencies=[Depends(_finite_json_guard)])
    def creator_set_state(sid: str, req: CreatorStateRequest, cell: Optional[str] = None) -> Ack:
        """FR-5120 — the JSON view's write: replace the whole asset list atomically."""
        _require(sid); _require_white(cell)
        return api.creator_set_state(sid, req.assets)

    @app.patch("/api/sessions/{sid}/creator/asset/{asset_id}", dependencies=[Depends(_finite_json_guard)])
    def creator_edit_asset(sid: str, asset_id: str, req: CreatorAssetPatchRequest,
                           cell: Optional[str] = None) -> Ack:
        """FR-5150 — the asset menu's edit/reassign operation (owner reassignment is just a
        patch of the ``owner`` field, so no separate reassign route is needed)."""
        _require(sid); _require_white(cell)
        return api.creator_edit_asset(sid, asset_id, req.patch)

    @app.delete("/api/sessions/{sid}/creator/asset/{asset_id}", dependencies=[Depends(_finite_json_guard)])
    def creator_delete_asset(sid: str, asset_id: str, cell: Optional[str] = None) -> Ack:
        """FR-5150 — the asset menu's delete operation."""
        _require(sid); _require_white(cell)
        return api.creator_delete_asset(sid, asset_id)

    @app.get("/api/sessions/{sid}/creator/scene")
    def creator_scene(sid: str) -> dict:
        """FR-5130 — the 2D/3D initial-state preview, ground-truth (no CellController filtering)."""
        _require(sid)
        return api.creator_scene(sid)

    @app.post("/api/sessions/{sid}/creator/seats", dependencies=[Depends(_finite_json_guard)])
    def declare_seats(sid: str, req: SeatDeclarationRequest, cell: Optional[str] = None) -> dict:
        """FR-5160 — seat-count declaration; White-Cell-only. BL-0123 remediation: unlike
        ``roles/assign`` (which is not cell-partitioned at all — ``cell`` there is purely caller
        identity), ``declare_seats`` genuinely needs a distinct *target* cell (white/blue/red),
        carried in ``req.cell``. The caller's own identity is the query-param ``cell``, the same
        convention every other mutating route in this file already uses (``creator_set_state``,
        ``creator_edit_asset``, etc.) — only a White-Cell caller may declare seats for *any*
        target cell, including White's own."""
        _require(sid)
        _require_white(cell)
        return api.declare_seats(sid, req.cell, req.count)

    @app.get("/api/sessions/{sid}/creator/seats")
    def seats_declared(sid: str) -> dict:
        _require(sid)
        return api.seats_declared(sid)

    @app.post("/api/sessions/{sid}/red_step", dependencies=[Depends(_finite_json_guard)])
    def red_step(sid: str, cell: Optional[str] = None) -> list[OrderAck]:
        _require(sid); _require_white(cell)
        return api.red_doctrine_step(sid)

    @app.post("/api/sessions/{sid}/order", dependencies=[Depends(_finite_json_guard_open)])
    def issue_order(sid: str, req: OrderRequest) -> OrderAck:
        _require(sid); _reject_observer(req.cell)
        order = Order(cell=req.cell, actor=req.actor, action=req.action, target=req.target, params=req.params)
        return api.issue_order(sid, req.cell, order, seat=req.seat)

    @app.post("/api/sessions/{sid}/order/validate", dependencies=[Depends(_finite_json_guard_open)])
    def validate_order(sid: str, req: OrderRequest) -> OrderAck:
        """Dry-run an order: accepted (window/path) or rejected (reason), mutating no session state."""
        _require(sid); _reject_observer(req.cell)
        order = Order(cell=req.cell, actor=req.actor, action=req.action, target=req.target, params=req.params)
        return api.validate_order(sid, req.cell, order, seat=req.seat)

    @app.get("/api/sessions/{sid}/orders/{cell}")
    def list_orders(sid: str, cell: str) -> list:
        _require(sid)
        return api.list_orders(sid, cell)

    @app.post("/api/sessions/{sid}/maneuver/compute", dependencies=[Depends(_finite_json_guard_open)])
    def maneuver_compute(sid: str, req: ManeuverComputeRequest) -> dict:
        """Compute an ECI impulse from a higher-level maneuver description (read-only)."""
        _require(sid); _reject_observer(req.cell)
        return api.compute_maneuver(sid, req.cell, req.actor, req.mode, req.params)

    @app.post("/api/sessions/{sid}/jam/compute", dependencies=[Depends(_finite_json_guard_open)])
    def jam_compute(sid: str, req: JamComputeRequest) -> dict:
        """Preview a jam order's effective radius, success probability, and footprint."""
        _require(sid); _reject_observer(req.cell)
        return api.compute_jam(sid, req.cell, req.actor, req.params)

    @app.post("/api/sessions/{sid}/engage/compute", dependencies=[Depends(_finite_json_guard_open)])
    def engage_compute(sid: str, req: EngageComputeRequest) -> dict:
        """Preview an engage order: closing geometry, Pₖ, debris cone (read-only)."""
        _require(sid); _reject_observer(req.cell)
        return api.compute_engage(sid, req.cell, req.actor, req.target, req.params)

    @app.post("/api/sessions/{sid}/cyber/compute", dependencies=[Depends(_finite_json_guard_open)])
    def cyber_compute(sid: str, req: CyberComputeRequest) -> dict:
        """Preview a cyber order: success/detect prob, attribution, payload effect."""
        _require(sid); _reject_observer(req.cell)
        return api.compute_cyber(sid, req.cell, req.actor, req.target, req.params)

    @app.post("/api/sessions/{sid}/sigint/compute", dependencies=[Depends(_finite_json_guard_open)])
    def sigint_compute(sid: str, req: SigintComputeRequest) -> dict:
        """Preview a SIGINT collection: geolocation accuracy + power draw."""
        _require(sid); _reject_observer(req.cell)
        return api.compute_sigint(sid, req.cell, req.actor, req.params)

    @app.post("/api/sessions/{sid}/preview/consequence", dependencies=[Depends(_finite_json_guard_open)])
    def preview_consequence(sid: str, req: OrderRequest) -> dict:
        """FW §11.D.18 — political-cost / escalation preview before order commit."""
        _require(sid); _reject_observer(req.cell)
        return api.preview_consequence(sid, req.cell, req.action, req.target or "", req.params or {})

    @app.get("/api/sessions/{sid}/activity/{cell}")
    def cell_activity(sid: str, cell: str,
                       past_window_s: int = 1800,
                       future_window_s: int = 7200) -> dict:
        """Cell activity Gantt feed: past + present + scheduled rows for the cell.

        White sees all cells (blue / red / neutral); Blue and Red see only their own
        orders and the started effects on their own assets (category + symptom); a scheduled
        inject is White-only. ``observer`` follows the Observer designation; any other cell is
        refused with 400 (IP-1088, FR-6210).
        """
        _require(sid)
        try:
            return api.cell_activity(sid, cell, past_window_s, future_window_s)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    @app.get("/api/sessions/{sid}/coaching/{cell}")
    def coaching(sid: str, cell: str) -> list[dict]:
        """FW §11.D.17 — White-Cell coaching notes visible to this cell at world.now."""
        _require(sid)
        return api.coaching_notes(sid, cell)

    @app.get("/api/sessions/{sid}/conjunctions/{cell}")
    def conjunctions(sid: str, cell: str) -> list[dict]:
        """FW §11.C.14 — upcoming close-approach warnings.  Filtered to assets the cell owns."""
        _require(sid)
        # Audit Jun 2026 §D10 — hold the session lock through the iteration so a
        # concurrent mutation can't raise ``dict changed size during iteration``.
        with api._locked_read(sid) as mgr:
            out = []
            for c in list(mgr.world.conjunctions):
                a_owner = (mgr.world.assets.get(c.get("a", "")) or
                           type("X", (), {"owner": None})).owner
                b_owner = (mgr.world.assets.get(c.get("b", "")) or
                           type("X", (), {"owner": None})).owner
                if cell in ("white",) or cell in (a_owner, b_owner):
                    out.append({**c, "now": mgr.world.now})
            return out

    @app.post("/api/sessions/{sid}/cancel", dependencies=[Depends(_finite_json_guard_open)])
    def cancel_order(sid: str, req: CancelRequest) -> Ack:
        _require(sid); _reject_observer(req.cell)
        return api.cancel_order(sid, req.cell, req.order_id)

    @app.post("/api/sessions/{sid}/gate/decide", dependencies=[Depends(_finite_json_guard_open)])
    def decide_gated_order(sid: str, req: GateDecisionRequest) -> Ack:
        """IP-1270 (FR-3430) — approve/deny a pending-approval order; role-gated inside
        SessionManager/OrderSystem against the matched rule's own required_role."""
        _require(sid); _reject_observer(req.cell)
        return api.decide_gated_order(sid, req.cell, req.order_id, req.approve)

    @app.post("/api/sessions/{sid}/roe/change", dependencies=[Depends(_finite_json_guard_open)])
    def issue_roe_change(sid: str, req: RoeChangeRequest) -> Ack:
        """IP-1270 (FR-3440) — a live, logged mid-session ROE-flag change; White-Cell-only
        (checked inside SessionManager/OrderSystem)."""
        _require(sid); _reject_observer(req.cell)
        return api.issue_roe_change(sid, req.cell, req.target_cell, req.flag, req.value)

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

    @app.post("/api/sessions/{sid}/recovery/{cell}/{asset}", dependencies=[Depends(_finite_json_guard_open)])
    def begin_recovery(sid: str, cell: str, asset: str, req: RecoveryRequest) -> dict:
        """Schedule the multi-pass safe-mode recovery chain over command-uplink windows."""
        _require(sid); _reject_observer(cell)
        return api.begin_recovery(sid, cell, asset, req.via)

    # ---- SSN (mock Space Surveillance Network) -------------------------------
    @app.post("/api/sessions/{sid}/ssn/{cell}/request", dependencies=[Depends(_finite_json_guard_open)])
    def ssn_submit(sid: str, cell: str, body: SSNRequestBody) -> dict:
        """Submit an SSN collection request — accepted (scheduled) or FAILED with reason."""
        _require(sid); _reject_observer(cell)
        ack = api.submit_ssn_request(sid, cell, body.intent, body.target, body.regime, body.priority)
        return {"ok": ack.ok, "id": ack.id, "reason": ack.reason, "state": ack.state,
                "assigned_sensor": ack.assigned_sensor,
                "collect_at": ack.collect_at, "product_at": ack.product_at}

    @app.get("/api/sessions/{sid}/ssn/{cell}/requests")
    def ssn_list(sid: str, cell: str) -> list:
        _require(sid)
        return api.list_ssn_requests(sid, cell)

    @app.post("/api/sessions/{sid}/ssn/{cell}/cancel", dependencies=[Depends(_finite_json_guard_open)])
    def ssn_cancel(sid: str, cell: str, body: SSNCancelBody) -> Ack:
        _require(sid); _reject_observer(cell)
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

    # IP-1066 (FR-4450) — the pending-inject queue. Listing is a no-cell White read like
    # /injects; cancel/edit are White-only (403 otherwise, Observer included), at the same
    # client-side-trust level as every other White route (CLAUDE.md LAN trust model).
    @app.get("/api/sessions/{sid}/injects/pending")
    def injects_pending(sid: str) -> list:
        _require(sid)
        return api.pending_injects(sid)

    @app.post("/api/sessions/{sid}/injects/{handle}/cancel", dependencies=[Depends(_inject_finite_guard)])
    def inject_cancel(sid: str, handle: str, cell: Optional[str] = None) -> Ack:
        _require(sid)
        if cell != "white":
            raise HTTPException(status_code=403, detail="only White Cell may cancel an inject")
        ack = api.cancel_inject(sid, handle)
        if not ack.ok:
            raise HTTPException(status_code=400, detail=ack.reason)
        return ack

    @app.post("/api/sessions/{sid}/injects/{handle}/edit", dependencies=[Depends(_inject_finite_guard)])
    def inject_edit(sid: str, handle: str, req: InjectEditRequest, cell: Optional[str] = None) -> Ack:
        _require(sid)
        if cell != "white":
            raise HTTPException(status_code=403, detail="only White Cell may edit an inject")
        ack = api.edit_inject(sid, handle, effects=req.effects, at_sim_t=req.at_sim_t)
        if not ack.ok:
            raise HTTPException(status_code=400, detail=ack.reason)
        return ack

    @app.get("/api/sessions/{sid}/view/{cell}")
    def get_view(sid: str, cell: str) -> CellView:
        _require(sid)
        return api.get_view(sid, cell)  # fog applied server-side

    @app.get("/api/sessions/{sid}/scene/{cell}")
    def get_scene(sid: str, cell: str) -> SceneView:
        _require(sid)
        return api.get_scene(sid, cell)  # render-from-custody belief geometry

    @app.get("/api/sessions/{sid}/ric_view/{cell}")
    def get_ric_view(sid: str, cell: str, origin: str, chase: Optional[str] = None,
                     target: Optional[str] = None) -> dict:
        """IP-1300 (FR-8210/FR-8220) — live RIC-frame relative-motion view about ``origin``,
        plus an unbanded CATS phase-angle readout when both ``chase`` and ``target`` are given.
        Fog applied server-side (own assets + own Tracks only); ``white`` reads ground truth via
        the god-view path. An out-of-custody selection is a 404, like ``/telemetry``."""
        _require(sid)
        try:
            return api.get_ric_view(sid, cell, origin, chase=chase, target=target)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @app.get("/api/sessions/{sid}/tle/{cell}")
    def get_tle(sid: str, cell: str, object_id: str) -> dict:
        """IP-1211 (FR-7440) — quick, copyable current-epoch TLE for one satellite. Fog applied
        server-side: a cell exports its own satellites from their actual orbit (IP-1212, FR-7440
        as amended) and any other satellite only from its own Track; ``white`` reads ground truth
        via the god-view path. Any rejection (another side's satellite with no track, no estimate,
        unknown id, no orbit, unrepresentable orbit) is a 404 with the reason, like ``/ric_view``."""
        _require(sid)
        try:
            return api.get_tle(sid, cell, object_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc))

    @app.get("/api/sessions/{sid}/telemetry/{cell}/{asset}")
    def telemetry(sid: str, cell: str, asset: str) -> dict:
        _require(sid)
        r = api.get_telemetry(sid, cell, asset)
        if r is None:
            raise HTTPException(status_code=404, detail="no telemetry for this asset (fog/ownership)")
        return r

    # IP-1260 (FR-2320) — declared BEFORE the /{param} series route so "export.csv" is never
    # captured as a parameter id.
    @app.get("/api/sessions/{sid}/telemetry/{cell}/{asset}/export.csv", response_class=PlainTextResponse)
    def telemetry_export_csv(sid: str, cell: str, asset: str, t1: Optional[str] = None,
                             t2: Optional[str] = None,
                             interval_s: Optional[float] = Query(None, gt=0)) -> str:
        """IP-1260 (FR-2320) — the cell's own telemetry for one asset over a sim-time span, as CSV
        (one row per sampled instant x parameter). Fog-scoped identically to
        `/telemetry/{cell}/{asset}` (own assets only, White sees any; 404 otherwise). Omitted
        bounds default to the recorded range; a partially out-of-range span is clamped, a wholly
        out-of-range one is a 400 (same rule as `/ephemeris`). IP-1262: a request whose sampling
        would exceed `ephemeris.MAX_EXPORT_SAMPLES` instants is also a 400 naming the ceiling.
        IP-1089 (FR-7450): `t1`/`t2` are an ISO-8601 UTC timestamp (`...Z` or `+00:00`) or integer
        microseconds; anything else is a 400 naming the bound and the reason."""
        _require(sid)
        try:
            rows = api.telemetry_export(sid, cell, asset, t1=t1, t2=t2, interval_s=interval_s)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        if rows is None:
            raise HTTPException(status_code=404, detail="no telemetry for this asset (fog/ownership)")
        import csv, io
        cols = ["t", "utc", "asset", "subsystem", "param", "value", "unit", "status"]
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(cols)
        for row in rows:
            w.writerow(["" if row[k] is None else row[k] for k in cols])
        return buf.getvalue()

    @app.get("/api/sessions/{sid}/telemetry/{cell}/{asset}/{param}")
    def telemetry_series(sid: str, cell: str, asset: str, param: str,
                         t0: Optional[int] = None, t1: Optional[int] = None,
                         # Audit Jun 2026 §D6 — bound n to prevent CPU/memory DoS.
                         n: int = Query(120, ge=2, le=2000),
                         nominal: bool = False) -> dict:
        _require(sid)
        r = api.get_series(sid, cell, asset, param, t0=t0, t1=t1, n=n, nominal=nominal)
        if r is None:
            raise HTTPException(status_code=404, detail="no such telemetry series")
        return r

    @app.get("/api/sessions/{sid}/maneuver_ledger/{cell}/{asset}")
    def maneuver_ledger(sid: str, cell: str, asset: str) -> list[dict]:
        """IP-1250 (FR-1320) — per-asset manoeuvre ledger; fog-scoped identically to
        `/telemetry/{cell}/{asset}` (own assets only, White sees any)."""
        _require(sid)
        r = api.maneuver_ledger(sid, cell, asset)
        if r is None:
            raise HTTPException(status_code=404, detail="no maneuver ledger for this asset (fog/ownership)")
        return r

    @app.get("/api/sessions/{sid}/maneuver_ledger/{cell}/{asset}/export.csv", response_class=PlainTextResponse)
    def maneuver_ledger_export_csv(sid: str, cell: str, asset: str) -> str:
        """IP-1250 (FR-1320) — the same ledger rows, serialized as CSV."""
        _require(sid)
        rows = api.maneuver_ledger(sid, cell, asset)
        if rows is None:
            raise HTTPException(status_code=404, detail="no maneuver ledger for this asset (fog/ownership)")
        import csv, io
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["t", "cost", "purpose_tag", "remaining_delta_v_ms"])
        for row in rows:
            w.writerow([row["t"], row["cost"], row["purpose_tag"], row["remaining_delta_v_ms"]])
        return buf.getvalue()

    @app.get("/api/sessions/{sid}/godview")
    def get_godview(sid: str) -> dict:
        _require(sid)
        return api.get_godview(sid).model_dump()

    @app.get("/api/sessions/{sid}/controller_view")
    def controller_view(sid: str, cell: Optional[str] = None) -> dict:
        """IP-1067 (FR-4620) — White-only side-by-side view: truth + both cells' own views, one
        simulated instant (403 for any other seat; client-side-trust model, CLAUDE.md)."""
        _require(sid)
        if cell != "white":
            raise HTTPException(status_code=403, detail="only White Cell may open the controller view")
        return api.controller_view(sid)

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

    def _playback_ack(ack: Ack) -> Ack:
        """IP-1077 — an Ack refused by the playback seat rule is a 403, not a 200 ``ok: false``."""
        if not ack.ok and (ack.reason or "").startswith(PLAYBACK_REFUSED):
            raise HTTPException(status_code=403, detail=ack.reason)
        return ack

    @app.post("/api/sessions/{sid}/aar/playback/start", dependencies=[Depends(_playback_finite_guard)])
    def playback_start(sid: str, req: PlaybackStartRequest, cell: Optional[str] = None) -> Ack:
        """IP-1280 (FR-7330) — start (or replace) this session's variable-speed AAR playback,
        from ground truth or a named cell's fog-of-war-respecting viewpoint; rejected at the
        request boundary if the cell did not participate in the recorded exercise.
        IP-1077 (FR-7340) — seat rule via the ``cell`` query seat: White any viewpoint, a player
        only its own cell, Observer/no seat refused (403, before any other check)."""
        _require(sid)
        return _playback_ack(api.playback_start(sid, req.viewpoint, req.speed, seat=cell))

    @app.post("/api/sessions/{sid}/aar/playback/advance", dependencies=[Depends(_playback_finite_guard)])
    def playback_advance(sid: str, req: PlaybackAdvanceRequest, cell: Optional[str] = None) -> dict:
        """IP-1077 — White, or a player while the viewpoint is its own cell; else 403."""
        _require(sid)
        try:
            r = api.playback_advance(sid, req.dt_s, seat=cell)
        except PlaybackSeatRefused as exc:
            raise HTTPException(status_code=403, detail=str(exc))
        except ValueError as exc:          # IP-1082 (F2) — an advance that overflows is a 400, never a 500
            raise HTTPException(status_code=400, detail=str(exc))
        if r is None:
            raise HTTPException(status_code=404, detail="no playback session — call .../playback/start first")
        return r

    @app.get("/api/sessions/{sid}/aar/playback/state")
    def playback_state(sid: str, cell: Optional[str] = None) -> dict:
        """IP-1077 — White or Observer, or a player while the viewpoint is its own cell; else 403."""
        _require(sid)
        try:
            r = api.playback_state(sid, seat=cell)
        except PlaybackSeatRefused as exc:
            raise HTTPException(status_code=403, detail=str(exc))
        if r is None:
            raise HTTPException(status_code=404, detail="no playback session — call .../playback/start first")
        return r

    @app.post("/api/sessions/{sid}/aar/playback/viewpoint", dependencies=[Depends(_playback_finite_guard)])
    def playback_set_viewpoint(sid: str, req: PlaybackViewpointRequest, cell: Optional[str] = None) -> Ack:
        """Design Decision 1 — a viewpoint switch continues from the same simulated moment.
        IP-1077 — White any viewpoint, a player only its own cell; else 403."""
        _require(sid)
        return _playback_ack(api.playback_set_viewpoint(sid, req.viewpoint, seat=cell))

    @app.post("/api/sessions/{sid}/aar/playback/speed", dependencies=[Depends(_playback_finite_guard)])
    def playback_set_speed(sid: str, req: PlaybackSpeedRequest, cell: Optional[str] = None) -> Ack:
        """IP-1077 — White, or a player while the viewpoint is its own cell; else 403."""
        _require(sid)
        return _playback_ack(api.playback_set_speed(sid, req.speed, seat=cell))

    @app.get("/api/sessions/{sid}/assessment")
    def assessment_report(sid: str) -> dict:
        """Competency assessment rubric report (IP-2010, FS-201) — per-cell/per-exercise, both
        cells side-by-side, never a composite score. A ground-truth, no-cell-binding endpoint like
        /aar and /objectives (CLAUDE.md's LAN trust model note applies identically here)."""
        _require(sid)
        return api.assessment_report(sid)

    @app.get("/api/sessions/{sid}/alarms/{cell}")
    def alarms(sid: str, cell: str) -> list:
        _require(sid)
        return api.alarms(sid, cell)

    @app.get("/api/sessions/{sid}/ephemeris/truth", response_class=PlainTextResponse)
    def ephemeris_truth(sid: str, object_id: str, reference_id: str, t1: str, t2: str,
                         interval_s: Optional[float] = None, format: str = "csv") -> str:
        """IP-1210 (FR-7410) — ground-truth ephemeris export over a time span, ECI + RIC. A
        no-cell, White-Cell-only endpoint (`FR-6220`), like `/godview`/`/eventlog`/`/aar*`.
        IP-1262: a non-finite or non-positive `interval_s`, or sampling over
        `ephemeris.MAX_EXPORT_SAMPLES` instants, is a 400. IP-1089 (FR-7450): `t1`/`t2` are an
        ISO-8601 UTC timestamp or integer microseconds; a bad bound is a 400 naming it."""
        _require(sid)
        try:
            rows = api.truth_ephemeris(sid, object_id, reference_id, t1, t2, interval_s=interval_s)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        if format == "oem":
            return ephemeris.write_oem(rows, object_id)
        if format == "ric":
            # FR-7430 — the companion RIC-specific export, alongside "oem" (ECI-only, CCSDS-
            # conformant) and the default "csv" (which already carries both ECI and RIC).
            return ephemeris.write_ric_csv(rows)
        return ephemeris.write_csv(rows)

    @app.get("/api/sessions/{sid}/ephemeris/{cell}", response_class=PlainTextResponse)
    def ephemeris_cell_observed(sid: str, cell: str, object_id: str, reference_id: str,
                                t1: str, t2: str, interval_s: Optional[float] = None,
                                format: str = "csv") -> str:
        """IP-1210 (FR-7420) — `cell`'s own believed ephemeris over a time span, ECI + RIC. Same
        fog-of-war trust level as every other cell-scoped read (`/view/{cell}`, `/scene/{cell}`).
        IP-1262: a non-finite or non-positive `interval_s`, or sampling over
        `ephemeris.MAX_EXPORT_SAMPLES` instants, is a 400. IP-1089 (FR-7450): `t1`/`t2` are an
        ISO-8601 UTC timestamp or integer microseconds; a bad bound is a 400 naming it."""
        _require(sid)
        try:
            rows = api.cell_observed_ephemeris(sid, cell, object_id, reference_id, t1, t2,
                                               interval_s=interval_s)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        if format == "oem":
            return ephemeris.write_oem(rows, object_id)
        if format == "ric":
            return ephemeris.write_ric_csv(rows)
        return ephemeris.write_csv(rows)

    @app.get("/api/sessions/{sid}/save")
    def save(sid: str) -> dict:
        _require(sid)
        return api.save(sid)

    @app.post("/api/sessions/load_save", dependencies=[Depends(_finite_json_guard)])
    def load_save(state: dict, cell: Optional[str] = None) -> dict:
        _require_white(cell)
        try:
            sid, warnings = api.load_save_with_warnings(state)
        except (ValueError, FileNotFoundError) as exc:   # IP-1102 — never a 500 for an unusable save
            raise HTTPException(status_code=400, detail=str(exc))
        return {"session": sid, "warnings": warnings}

    if STATIC_DIR.exists():
        app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")

    app.state.api = api
    return app


app = create_app()
