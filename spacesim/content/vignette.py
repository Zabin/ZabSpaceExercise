"""Vignette schema + loader (``00-vignette-framework.md``, ``04-data-model.md`` §6).

Vignettes are **data files** (YAML), not code. This module defines the loadable schema, builds a
ready-to-run ``WorldState`` from a vignette (instantiating assets/sensors and resolving the White
Cell parameter dials into ROE + objective deadlines), and evaluates objective status. Content
format decision: YAML (human-authorable; matches the architecture/tech-stack/roadmap docs).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field

from spacesim.engine import simtime
from spacesim.engine.entities import Asset, Sensor

CONTENT_DIR = Path(__file__).resolve().parent
VIGNETTE_DIR = CONTENT_DIR / "vignettes"


class Parameter(BaseModel):
    id: str
    label: str = ""
    type: str = "enum"
    options: list[Any] = Field(default_factory=list)
    min: Optional[float] = None
    max: Optional[float] = None
    default: Any = None
    affects: str = ""


class Inject(BaseModel):
    id: str
    label: str = ""
    trigger: dict = Field(default_factory=dict)
    effects: list[dict] = Field(default_factory=list)
    repeatable: bool = False


class Vignette(BaseModel):
    id: str
    title: str
    classification: str = "UNCLASSIFIED-TRAINING"
    learning_objectives: list[str] = Field(default_factory=list)
    doctrinal_basis: list[str] = Field(default_factory=list)
    red_doctrine_profile: str = "generic"
    estimated_duration_min: int = 60
    start_epoch_utc: str = "2030-01-01T00:00:00Z"
    geography: dict = Field(default_factory=dict)
    orbital_environment: dict = Field(default_factory=dict)
    blue_forces: list[dict] = Field(default_factory=list)
    red_forces: list[dict] = Field(default_factory=list)
    neutral_forces: list[dict] = Field(default_factory=list)
    sensors: list[dict] = Field(default_factory=list)
    objectives: dict = Field(default_factory=dict)
    escalation_thresholds: dict = Field(default_factory=dict)
    parameters: list[Parameter] = Field(default_factory=list)
    injects: list[Inject] = Field(default_factory=list)
    # Optional guided-walkthrough script: {"blue": [step,...], "red": [step,...]} where each step is
    # {n, title, when, action, actor, target, params, expect}. Drives the manual + its screenshots.
    tutorial: dict = Field(default_factory=dict)
    # FW §11.D.17 — White-Cell coaching notes: facilitator pop-ups keyed to time/event seq.
    # Each note: {at_sim_t: int microseconds | null, cell: "blue"|"red"|"white",
    #             title: str, body: str}.  Surfaced in the Coaching panel; ignored by the engine.
    coaching: list[dict] = Field(default_factory=list)
    # Per-cell mission brief shown above Objectives when the session starts.  Fog-of-war is
    # honored at authoring time — `blue` may not reveal hidden Red dispositions, and `red` may
    # not reveal Blue's deadline.  Each block: {situation, mission, friendly_forces,
    # threat_picture, deadline_note, roe_note, success_criteria, tool_tips} — any of which may
    # be omitted.  When absent, the UI auto-generates a fallback from title + theater +
    # objectives + learning_objectives.
    intro_brief: dict = Field(default_factory=dict)


@dataclass
class VignetteContext:
    """Runtime values derived from a vignette + chosen parameter values."""

    start_epoch: int
    param_values: dict
    roe: dict
    landing_deadline: int
    ops_fidelity: str = "realistic"
    fog_of_war: str = "realistic_sda"
    objectives: dict = field(default_factory=dict)
    red_doctrine_profile: str = "generic"
    ssn_networks: dict = field(default_factory=dict)   # cell -> SSNNetwork (only populated if vignette opts in)


def list_vignettes() -> list[dict]:
    out = []
    for path in sorted(VIGNETTE_DIR.glob("*.yaml")):
        # Audit Jun 2026 §B/E - tolerate one malformed file rather than 500ing
        # the whole listing endpoint.
        try:
            raw = yaml.safe_load(path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict) or "vignette" not in raw:
                continue
            data = raw["vignette"]
            if not isinstance(data, dict) or "id" not in data:
                continue
            out.append({"id": data["id"], "title": data.get("title", data["id"]), "path": str(path)})
        except (yaml.YAMLError, OSError):
            continue
    return out


def load_vignette(path_or_id: str) -> Vignette:
    """Load a vignette by its declared id.

    Audit Jun 2026 §D4 hardening: only basenames are accepted; any input
    containing path separators, parent-directory traversal, an absolute-path
    marker, or non-`[A-Za-z0-9_.-]` characters is rejected without touching the
    filesystem. The resolved path is then re-checked to live inside
    ``VIGNETTE_DIR`` (defence in depth against symlink/normalisation tricks).
    """
    if not isinstance(path_or_id, str) or not path_or_id:
        raise ValueError("vignette id must be a non-empty string")
    if "/" in path_or_id or "\\" in path_or_id or ".." in path_or_id:
        raise ValueError(f"vignette id contains path separators or traversal: {path_or_id!r}")
    if path_or_id.startswith(("~", ".")):
        raise ValueError(f"vignette id may not start with '~' or '.': {path_or_id!r}")
    # Lock the charset — same as web-layer TleRequest.id / OrderRequest.actor.
    import re as _re
    if not _re.fullmatch(r"[A-Za-z0-9_.\-]{1,128}", path_or_id):
        raise ValueError(f"vignette id has disallowed characters: {path_or_id!r}")

    candidate = (VIGNETTE_DIR / f"{path_or_id}.yaml").resolve()
    vignette_root = VIGNETTE_DIR.resolve()
    if vignette_root not in candidate.parents:
        raise ValueError(f"vignette path escapes VIGNETTE_DIR: {candidate}")
    if candidate.exists():
        path = candidate
    else:  # resolve by the vignette's declared id (filenames are numbered, ids are not)
        path = None
        for p in sorted(VIGNETTE_DIR.glob("*.yaml")):
            data_inner = yaml.safe_load(p.read_text(encoding="utf-8"))
            if not isinstance(data_inner, dict) or "vignette" not in data_inner:
                continue
            if data_inner["vignette"].get("id") == path_or_id:
                path = p
                break
        if path is None:
            raise FileNotFoundError(f"no vignette with id {path_or_id!r}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "vignette" not in data:
        raise ValueError(f"malformed vignette file (missing 'vignette' key): {path.name}")
    return Vignette.model_validate(data["vignette"])


def resolve_params(vignette: Vignette, overrides: Optional[dict] = None) -> dict:
    values = {p.id: p.default for p in vignette.parameters}
    if overrides:
        values.update({k: v for k, v in overrides.items() if k in values})
    return values


def build_world(vignette: Vignette, overrides: Optional[dict] = None):
    """Instantiate a WorldState + VignetteContext from the vignette and parameter choices."""
    from spacesim.engine.world import WorldState  # local import: engine layer

    start = simtime.from_iso(vignette.start_epoch_utc)
    params = resolve_params(vignette, overrides)
    world = WorldState(now=start)

    for owner, force in (("blue", vignette.blue_forces), ("red", vignette.red_forces), ("neutral", vignette.neutral_forces)):
        for spec in force:
            data = {**spec, "owner": owner}
            if data.get("orbit") is not None and data["orbit"].get("epoch") is None:
                data["orbit"]["epoch"] = start
            asset = Asset.model_validate(data)
            world.assets[asset.id] = asset

    for spec in vignette.sensors:
        sensor = Sensor.model_validate(spec)
        world.sensors[sensor.id] = sensor

    # Enforce v1 satellite caps (build-spec/01-context-and-scope.md §3.1)
    orbital = [a for a in world.assets.values() if a.orbit is not None]
    if len(orbital) > 24:
        raise ValueError(
            f"vignette '{vignette.id}': {len(orbital)} orbital assets exceed the ≤24 satellite cap"
        )
    from collections import Counter
    group_counts = Counter(a.group for a in orbital if a.group)
    over = {g: n for g, n in group_counts.items() if n > 3}
    if over:
        detail = ", ".join(f"{g}={n}" for g, n in over.items())
        raise ValueError(
            f"vignette '{vignette.id}': constellation(s) exceed the ≤3 satellite cap: {detail}"
        )

    # SSN per-cell networks (opt-in via vignette params; off by default) — `docs/SSN-DESIGN.md`.
    ssn_networks: dict = {}
    from spacesim.engine.ssn import instantiate_network as _ssn_instantiate
    for cell, key in (("blue", "ssn_blue_dispersion"), ("red", "ssn_red_dispersion")):
        net = _ssn_instantiate(world, cell, str(params.get(key, "off")))
        if net is not None:
            ssn_networks[cell] = net

    roe = {
        "kinetic_authorized": bool(params.get("red_kinetic_authorized", False)),
        "cyber_authorized": bool(params.get("cyber_authorized", params.get("red_cyber_authorized", False))),
    }
    landing_offset_s = float(params.get("landing_window_start_s", 1800))
    ctx = VignetteContext(
        start_epoch=start,
        param_values=params,
        roe=roe,
        landing_deadline=start + int(landing_offset_s * 1_000_000),
        ops_fidelity=str(params.get("ops_fidelity", "realistic")),
        fog_of_war=str(params.get("fog_of_war", "realistic_sda")),
        objectives=vignette.objectives,
        red_doctrine_profile=str(params.get("red_doctrine_profile", vignette.red_doctrine_profile)),
        ssn_networks=ssn_networks,
    )
    return world, ctx


def evaluate_objectives(world, ctx: VignetteContext) -> dict:
    """Data-driven objective status: each objective declares a ``metric`` evaluated here."""
    out: dict = {}
    for side in ("blue", "red"):
        out[side] = {}
        for obj in ctx_objectives(world, ctx, side):
            out[side][obj["id"]] = _evaluate_metric(world, ctx, obj.get("metric", {}))
    return out


def ctx_objectives(world, ctx: VignetteContext, side: str) -> list[dict]:
    return ctx.objectives.get(side, [])


def _deadline(ctx: VignetteContext, metric: dict) -> int:
    if "by_s" in metric:
        return ctx.start_epoch + int(float(metric["by_s"]) * 1_000_000)
    return ctx.landing_deadline


def _range_km(world, a_id: str, b_id: str) -> Optional[float]:
    import numpy as np
    from spacesim.engine.propagator import ModeratePropagator
    a, b = world.assets.get(a_id), world.assets.get(b_id)
    if a is None or b is None or a.orbit is None or b.orbit is None:
        return None
    prop = ModeratePropagator()
    ra, _ = prop.rv(a.orbit, world.now)
    rb, _ = prop.rv(b.orbit, world.now)
    return float(np.linalg.norm(ra - rb)) / 1000.0


def _evaluate_metric(world, ctx: VignetteContext, m: dict) -> bool:
    from spacesim.engine.effects import is_link_denied
    kind = m.get("kind")
    now = world.now
    deadline = _deadline(ctx, m)

    if kind == "deliver_before":
        flag = m.get("flag", "imagery_delivered")
        at = world.mission.get(f"{flag}_at")
        return bool(world.mission.get(flag)) and at is not None and at <= deadline
    if kind == "deny_delivery":
        flag = m.get("flag", "imagery_delivered")
        at = world.mission.get(f"{flag}_at")
        delivered_in_time = bool(world.mission.get(flag)) and at is not None and at <= deadline
        return (not delivered_in_time) and now >= deadline
    if kind == "custody":
        tr = world.track_for(m["side"], m["object"])
        return tr is not None and tr.current_confidence(now) >= float(m.get("min_conf", 0.5))
    if kind == "deny_custody":
        tr = world.track_for(m["side"], m["object"])
        ok = tr is not None and tr.current_confidence(now) >= float(m.get("min_conf", 0.5))
        return (not ok) and now >= deadline
    if kind == "characterized":
        tr = world.track_for(m["side"], m["object"])
        return tr is not None and tr.characterized
    if kind == "asset_destroyed":
        a = world.assets.get(m["target"])
        return a is not None and a.health == "destroyed"
    if kind == "asset_survived":
        a = world.assets.get(m["target"])
        return a is not None and a.health != "destroyed" and now >= deadline
    if kind == "asset_safed":
        a = world.assets.get(m["target"])
        return a is not None and a.bus_state is not None and a.bus_state.safe_mode.active
    if kind == "asset_operational":
        a = world.assets.get(m["target"])
        safed = a is not None and a.bus_state is not None and a.bus_state.safe_mode.active
        return a is not None and a.health != "destroyed" and not safed and now >= deadline
    if kind == "no_debris":
        return len(world.debris) == 0 and now >= deadline
    if kind == "debris_present":
        return len(world.debris) > 0
    if kind == "link_denied":
        return is_link_denied(world, m["target"], now)
    if kind == "proximity":
        r = _range_km(world, m["a"], m["b"])
        return r is not None and r <= float(m.get("max_km", 50.0))
    if kind == "evade":
        r = _range_km(world, m["a"], m["b"])
        return r is not None and r >= float(m.get("min_km", 50.0)) and now >= deadline
    return False
