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


@dataclass
class VignetteContext:
    """Runtime values derived from a vignette + chosen parameter values."""

    start_epoch: int
    param_values: dict
    roe: dict
    landing_deadline: int
    ops_fidelity: str = "realistic"
    fog_of_war: str = "realistic_sda"


def list_vignettes() -> list[dict]:
    out = []
    for path in sorted(VIGNETTE_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text())["vignette"]
        out.append({"id": data["id"], "title": data.get("title", data["id"]), "path": str(path)})
    return out


def load_vignette(path_or_id: str) -> Vignette:
    path = Path(path_or_id)
    if not path.exists():
        candidate = VIGNETTE_DIR / f"{path_or_id}.yaml"
        if candidate.exists():
            path = candidate
        else:  # resolve by the vignette's declared id (filenames are numbered, ids are not)
            path = None
            for p in sorted(VIGNETTE_DIR.glob("*.yaml")):
                if yaml.safe_load(p.read_text())["vignette"]["id"] == path_or_id:
                    path = p
                    break
            if path is None:
                raise FileNotFoundError(f"no vignette with id or path {path_or_id!r}")
    data = yaml.safe_load(path.read_text())
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
    )
    return world, ctx


def evaluate_objectives(world, ctx: VignetteContext) -> dict:
    """Objective status for Vignette 1: Blue must deliver imagery before the landing window."""
    delivered = bool(world.mission.get("imagery_delivered", False))
    at = world.mission.get("imagery_delivered_at")
    in_time = delivered and at is not None and at <= ctx.landing_deadline
    window_passed = world.now >= ctx.landing_deadline
    return {
        "blue": {"deliver_isr": in_time},
        "red": {"deny_isr": (not in_time) and window_passed},
    }
