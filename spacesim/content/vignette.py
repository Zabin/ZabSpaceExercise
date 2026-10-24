"""Vignette schema + loader (``00-vignette-framework.md``, ``04-data-model.md`` §6).

Vignettes are **data files** (YAML), not code. This module defines the loadable schema, builds a
ready-to-run ``WorldState`` from a vignette (instantiating assets/sensors and resolving the White
Cell parameter dials into ROE + objective deadlines), and evaluates objective status. Content
format decision: YAML (human-authorable; matches the architecture/tech-stack/roadmap docs).
"""

from __future__ import annotations

import logging
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal, Optional, Sequence

import yaml
from pydantic import BaseModel, Field

from spacesim.engine import simtime
from spacesim.engine.entities import Asset, Sensor

CONTENT_DIR = Path(__file__).resolve().parent
VIGNETTE_DIR = CONTENT_DIR / "vignettes"

_logger = logging.getLogger(__name__)

# Same charset discipline as ui_web/server.py's _validate_id / OrderRequest.actor.
_ID_RE = re.compile(r"[A-Za-z0-9_.\-]{1,128}")


def _validate_id(path_or_id: str) -> None:
    """IP-1180 (NFR-3700) — shared id-validation, extracted from ``load_vignette()``'s existing
    body with no behavior change, so the save path (``vignette_export.py``) applies the exact
    same guard rather than maintaining a second copy."""
    if not isinstance(path_or_id, str) or not path_or_id:
        raise ValueError("vignette id must be a non-empty string")
    if "/" in path_or_id or "\\" in path_or_id or ".." in path_or_id:
        raise ValueError(f"vignette id contains path separators or traversal: {path_or_id!r}")
    if path_or_id.startswith(("~", ".")):
        raise ValueError(f"vignette id may not start with '~' or '.': {path_or_id!r}")
    if not _ID_RE.fullmatch(path_or_id):
        raise ValueError(f"vignette id has disallowed characters: {path_or_id!r}")


def _resolve_within_root(root: Path, filename: str) -> Path:
    """IP-1180 (NFR-3700) — the resolved-path-inside-root re-check, generalized from
    ``load_vignette()``'s existing body to take any content root, not only ``VIGNETTE_DIR``."""
    candidate = (root / filename).resolve()
    root_resolved = root.resolve()
    if root_resolved not in candidate.parents:
        raise ValueError(f"path escapes root {root}: {candidate}")
    return candidate


class VignetteValidationError(ValueError):
    """IP-1310 (FR-5310, NFR-1600) — a vignette refused at load, naming every failing element.

    ``problems`` is a list of ``{"where": "<section>[<entry>].<field>", "reason": "<text>"}``.
    Subclasses ``ValueError`` so existing ``ValueError`` callers keep working.
    """

    def __init__(self, vignette_id: str, problems: list[dict]):
        self.vignette_id = vignette_id
        self.problems = list(problems)
        super().__init__(self.message)

    @property
    def message(self) -> str:
        n = len(self.problems)
        if not n:
            return f"vignette {self.vignette_id!r} is invalid"
        first = self.problems[0]
        more = f" (and {n - 1} more problem{'s' if n > 2 else ''})" if n > 1 else ""
        return f"vignette {self.vignette_id!r} is invalid: {first['where']}: {first['reason']}{more}"


def _configured_external_dirs() -> list[Path]:
    from spacesim.config import load_content_config
    return [Path(d) for d in load_content_config().external_vignette_dirs]


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


class RoleRequirement(BaseModel):
    """IP-1151 (FR-4210) — a seat/role staffing requirement a vignette may declare. Absent/empty
    (every vignette shipped before this package) means no mandatory staffing requirement at all —
    additive and backward-compatible by construction."""
    asset_or_constellation: str
    role: Literal["bus", "payload", "both"] = "both"
    mandatory: bool = True


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
    # IP-1151 (FR-4210) — declared seat/role staffing requirements, consumed by
    # session/manager.py's Role Assignment registry + staffing gate. Empty/absent for every
    # vignette shipped before this package (no mandatory staffing requirement).
    roles_needed: list[RoleRequirement] = Field(default_factory=list)
    # IP-1172 (FR-3420, NFR-2010) — optional per-cell ROE: {"blue": {kinetic_authorized,
    # cyber_authorized}, "red": {...}}. Absent for every vignette shipped before this package;
    # build_world() falls back to the legacy flat red_kinetic_authorized/cyber_authorized
    # parameters, replicated identically to both cells, when this field is absent.
    roe: Optional[dict] = None
    # IP-1270 (FR-3430) — optional effect-authorization gating rules, each
    # {action_type?: str, reversibility_category?: str, required_role: str}. A rule with both
    # axes absent matches every order (not a useful declaration, but not rejected either). Absent
    # for every vignette shipped before this package (additive, NFR-2010) — zero behavior change.
    effect_gating_rules: list[dict] = Field(default_factory=list)
    # IP-1290 (FR-1450) — optional per-effect-class detectability/attribution-difficulty overrides,
    # each {action_type?: str, reversibility_category?: str, confidence: float}, keyed by the same
    # shared enumeration as effect_gating_rules above (IP-1270 Design Decision 1). Absent for every
    # vignette shipped before this package (additive, NFR-2010) — zero behavior change.
    effect_detectability_config: list[dict] = Field(default_factory=list)
    # IP-1200 (FR-5510) — save-as-scenario's carried-forward mid-exercise state. All three
    # absent/empty for every vignette shipped before this package (additive, NFR-2010).
    initial_tracks: list[dict] = Field(default_factory=list)   # each entry a Track.model_dump()
    simulator_version: Optional[str] = None
    initial_space_weather: Optional[dict] = None   # the same plain dict shape as world.space_weather
    # IP-1230 (FR-1230/FR-4440, ADR-0039) — both optional and absent for every vignette shipped
    # before this package (zero behavior change). `space_weather_series`: entries
    # {at_sim_s >= 0, f107?, kp?}, converted by build_world into world.space_weather["index_series"]
    # (absolute sim time). `environmental_anomalies`: {base_rate_per_day >= 0, assets: [ids],
    # subsystem: bus|telemetry (default bus), cause (default "space_weather")}.
    space_weather_series: list[dict] = Field(default_factory=list)
    environmental_anomalies: Optional[dict] = None


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
    # IP-1270 (FR-3430) — passed through unmodified from vignette.effect_gating_rules.
    gating_rules: list[dict] = field(default_factory=list)
    # IP-1290 (FR-1450) — passed through unmodified from vignette.effect_detectability_config.
    detectability_config: list[dict] = field(default_factory=list)


def list_vignettes(external_dirs: Optional[Sequence[Path]] = None) -> list[dict]:
    """Enumerate the built-in library plus any configured external directories (IP-1180,
    FR-5410). Each entry carries ``origin``: ``"built-in"`` for ``VIGNETTE_DIR``, or the external
    directory's own basename. A same-id collision resolves to whichever root was scanned first
    (built-in, then external directories in configured order) — the loser is skipped and a
    ``WARNING`` discloses the shadow (Design Decision 4)."""
    out: list[dict] = []
    seen_ids: set[str] = set()
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
            out.append({"id": data["id"], "title": data.get("title", data["id"]),
                        "path": str(path), "origin": "built-in"})
            seen_ids.add(data["id"])
        except (yaml.YAMLError, OSError):
            continue

    dirs = list(external_dirs) if external_dirs is not None else _configured_external_dirs()
    for ext_dir in dirs:
        ext_dir = Path(ext_dir)
        if not ext_dir.is_dir():
            # Design Decision 2 — an unreadable/nonexistent configured directory is skipped,
            # logged, and the catalog build continues with the remaining roots.
            _logger.warning("external vignette directory unreadable or missing, skipped: %s", ext_dir)
            continue
        origin = ext_dir.name
        for path in sorted(ext_dir.glob("*.yaml")):
            try:
                raw = yaml.safe_load(path.read_text(encoding="utf-8"))
                if not isinstance(raw, dict) or "vignette" not in raw:
                    continue
                data = raw["vignette"]
                if not isinstance(data, dict) or "id" not in data:
                    continue
                vid = data["id"]
                if vid in seen_ids:
                    _logger.warning(
                        "vignette id %r in external directory %s shadowed by an earlier entry, skipped",
                        vid, ext_dir,
                    )
                    continue
                out.append({"id": vid, "title": data.get("title", vid),
                            "path": str(path), "origin": origin})
                seen_ids.add(vid)
            except (yaml.YAMLError, OSError):
                continue
    return out


def _declared_vignette_id(path: Path) -> Optional[str]:
    """IP-1311 (FR-5310, NFR-1600): the ``vignette.id`` a file declares, or ``None`` when the file
    is unreadable, not valid YAML, not a mapping, or has no mapping ``vignette`` block with an id.
    Shared by both id-resolution scans so one bad neighbour never blocks a lookup."""
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (yaml.YAMLError, OSError, UnicodeDecodeError):
        return None
    if not isinstance(raw, dict):
        return None
    block = raw.get("vignette")
    if not isinstance(block, dict):
        return None
    return block.get("id")


def load_vignette(path_or_id: str, external_dirs: Optional[Sequence[Path]] = None) -> Vignette:
    """Load a vignette by its declared id.

    Audit Jun 2026 §D4 hardening: only basenames are accepted; any input
    containing path separators, parent-directory traversal, an absolute-path
    marker, or non-`[A-Za-z0-9_.-]` characters is rejected without touching the
    filesystem. The resolved path is then re-checked to live inside
    ``VIGNETTE_DIR`` (defence in depth against symlink/normalisation tricks).

    IP-1180 (FR-5410): after exhausting the built-in search (unchanged, still checked first —
    Design Decision 4's built-in-wins rule), falls through to each configured external directory
    in turn, applying the same guard against every root.
    """
    _validate_id(path_or_id)

    candidate = _resolve_within_root(VIGNETTE_DIR, f"{path_or_id}.yaml")
    if candidate.exists():
        path = candidate
    else:  # resolve by the vignette's declared id (filenames are numbered, ids are not)
        path = None
        for p in sorted(VIGNETTE_DIR.glob("*.yaml")):
            if _declared_vignette_id(p) == path_or_id:
                path = p
                break
        if path is None:
            dirs = list(external_dirs) if external_dirs is not None else _configured_external_dirs()
            for ext_dir in dirs:
                ext_dir = Path(ext_dir)
                if not ext_dir.is_dir():
                    continue
                ext_candidate = _resolve_within_root(ext_dir, f"{path_or_id}.yaml")
                if ext_candidate.exists():
                    path = ext_candidate
                    break
                for p in sorted(ext_dir.glob("*.yaml")):
                    if _declared_vignette_id(p) == path_or_id:
                        path = p
                        break
                if path is not None:
                    break
        if path is None:
            raise FileNotFoundError(f"no vignette with id {path_or_id!r}")
    # IP-1310 (FR-5310, NFR-1600) — every content failure from here on is one
    # VignetteValidationError naming each failing element, never a bare parser/pydantic error.
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise VignetteValidationError(path_or_id, [{"where": path.name, "reason": f"not valid YAML: {exc}"}]) from exc
    if not isinstance(data, dict) or "vignette" not in data:
        raise VignetteValidationError(path_or_id, [{"where": path.name,
                                                    "reason": "malformed vignette file (missing 'vignette' key)"}])
    from pydantic import ValidationError
    try:
        vignette = Vignette.model_validate(data["vignette"])
    except ValidationError as exc:
        raise VignetteValidationError(path_or_id, _pydantic_problems("vignette", exc)) from exc
    problems = validate_vignette(vignette)
    if problems:
        raise VignetteValidationError(path_or_id, problems)
    return vignette


def resolve_params(vignette: Vignette, overrides: Optional[dict] = None) -> dict:
    values = {p.id: p.default for p in vignette.parameters}
    if overrides:
        values.update({k: v for k, v in overrides.items() if k in values})
    return values


def _force_sections(vignette: Vignette):
    return (("blue", vignette.blue_forces), ("red", vignette.red_forces),
            ("neutral", vignette.neutral_forces))


def _asset_data(spec: dict, owner: str, start: int) -> dict:
    """The force-entry normalisation ``build_world`` applies (owner injected, orbit epoch defaulted
    to the vignette start). Shared with ``validate_vignette`` (IP-1310) so the two cannot drift."""
    data = {**spec, "owner": owner}
    if data.get("orbit") is not None and data["orbit"].get("epoch") is None:
        data["orbit"]["epoch"] = start
    return data


def _loc_text(loc) -> str:
    return ".".join(str(part) for part in loc) if loc else "(entry)"


def _pydantic_problems(where: str, exc) -> list[dict]:
    from pydantic import ValidationError
    if isinstance(exc, ValidationError):
        return [{"where": f"{where}.{_loc_text(err.get('loc'))}" if err.get("loc") else where,
                 "reason": str(err.get("msg", "invalid"))} for err in exc.errors()]
    return [{"where": where, "reason": str(exc)}]


def _environmental_anomaly_problems(block, asset_ids, bused) -> list[dict]:
    """IP-1230 (ADR-0039 decision 8) — problems in an optional ``environmental_anomalies`` block."""
    if block is None:
        return []
    where = "environmental_anomalies"
    if not isinstance(block, dict):
        return [{"where": where, "reason": "must be a mapping"}]
    out: list[dict] = []
    rate = block.get("base_rate_per_day")
    if (not isinstance(rate, (int, float)) or isinstance(rate, bool) or not math.isfinite(rate)
            or rate < 0):
        out.append({"where": f"{where}.base_rate_per_day",
                    "reason": f"must be a finite number >= 0, got {rate!r}"})
    assets = block.get("assets")
    if not isinstance(assets, list) or not assets:
        out.append({"where": f"{where}.assets", "reason": "must be a non-empty list of asset ids"})
    else:
        for aid in assets:
            if aid not in asset_ids:
                out.append({"where": f"{where}.assets", "reason": f"{aid!r} is not a declared asset"})
            elif aid not in bused:
                out.append({"where": f"{where}.assets",
                            "reason": f"{aid!r} has no bus (bus_state), so an anomaly cannot land on it"})
    if block.get("subsystem", "bus") not in ("bus", "telemetry"):
        out.append({"where": f"{where}.subsystem",
                    "reason": f"must be 'bus' or 'telemetry', got {block.get('subsystem')!r}"})
    if not isinstance(block.get("cause", "space_weather"), str):
        out.append({"where": f"{where}.cause", "reason": "must be a string"})
    return out


def validate_vignette(vignette: Vignette) -> list[dict]:
    """IP-1310 (FS-131; FR-5310–FR-5314, NFR-1600) — every load-time problem in ``vignette``.

    Pure: reads no clock, draws no RNG, schedules nothing, and mutates nothing it did not create
    (every entry is deep-copied before normalisation). Returns ``[]`` for a valid vignette;
    otherwise one ``{"where", "reason"}`` dict per failing element, all problems collected.
    """
    import copy

    from spacesim.engine.custody import Track
    from spacesim.engine.propagator import ModeratePropagator

    problems: list[dict] = []
    try:
        start = simtime.from_iso(vignette.start_epoch_utc)
    except Exception as exc:  # noqa: BLE001 — any parse failure is a content problem
        problems.append({"where": "start_epoch_utc", "reason": str(exc)})
        start = None

    # Force entries: the build_world normalisation + Asset model (FR-5310, FR-5312, FR-5311).
    asset_sections: dict[str, list[str]] = {}
    bused: set[str] = set()   # IP-1230 — assets with a bus (environmental-anomaly eligibility)
    groups: set[str] = set()
    prop = ModeratePropagator()
    for owner, force in _force_sections(vignette):
        section = f"{owner}_forces"
        for index, spec in enumerate(force):
            ref = spec.get("id", index) if isinstance(spec, dict) else index
            where = f"{section}[{ref}]"
            if not isinstance(spec, dict):
                problems.append({"where": where, "reason": "entry is not a mapping"})
                continue
            try:
                asset = Asset.model_validate(_asset_data(copy.deepcopy(spec), owner, start or 0))
            except Exception as exc:  # noqa: BLE001
                problems.extend(_pydantic_problems(where, exc))
                continue
            asset_sections.setdefault(asset.id, []).append(section)
            if asset.bus_state is not None:
                bused.add(asset.id)
            if asset.group:
                groups.add(asset.group)
            # FR-5312 — a satellite needs an orbit; every other kind except a cyber unit (whose
            # effects are window-independent, ADR-0012) needs a location.
            if asset.kind == "satellite" and asset.orbit is None:
                problems.append({"where": f"{where}.orbit", "reason": "a satellite must declare an orbit"})
            elif asset.kind not in ("satellite", "cyber_unit") and asset.location is None:
                problems.append({"where": f"{where}.location",
                                 "reason": f"a {asset.kind} must declare a location"})
            # FR-5311 — a TLE orbit must initialise and propagate at the vignette start epoch.
            if asset.orbit is not None and asset.orbit.source == "tle" and start is not None:
                try:
                    prop.rv(asset.orbit, start)
                except Exception as exc:  # noqa: BLE001
                    problems.append({"where": f"{where}.orbit",
                                     "reason": f"TLE does not parse/propagate: {exc}"})

    # FR-5313 — asset ids unique across the three force lists.
    for asset_id, sections in asset_sections.items():
        if len(sections) > 1:
            problems.append({"where": f"{'/'.join(sections)}[{asset_id}]",
                             "reason": f"asset id {asset_id!r} is declared {len(sections)} times"})

    # Sensors: the Sensor model and its validators (FR-5310), then unique ids (FR-5313).
    sensor_ids: dict[str, int] = {}
    for index, spec in enumerate(vignette.sensors):
        ref = spec.get("id", index) if isinstance(spec, dict) else index
        where = f"sensors[{ref}]"
        try:
            sensor = Sensor.model_validate(copy.deepcopy(spec))
        except Exception as exc:  # noqa: BLE001
            problems.extend(_pydantic_problems(where, exc))
            continue
        sensor_ids[sensor.id] = sensor_ids.get(sensor.id, 0) + 1
    for sensor_id, count in sensor_ids.items():
        if count > 1:
            problems.append({"where": f"sensors[{sensor_id}]",
                             "reason": f"sensor id {sensor_id!r} is declared {count} times"})

    # FR-5314 — each roles_needed entry names a declared asset or constellation group.
    for index, req in enumerate(vignette.roles_needed):
        if req.asset_or_constellation not in asset_sections and req.asset_or_constellation not in groups:
            problems.append({"where": f"roles_needed[{index}].asset_or_constellation",
                             "reason": f"{req.asset_or_constellation!r} is not a declared asset or group"})

    for index, spec in enumerate(vignette.initial_tracks):
        try:
            Track.model_validate(copy.deepcopy(spec))
        except Exception as exc:  # noqa: BLE001
            problems.extend(_pydantic_problems(f"initial_tracks[{index}]", exc))

    # IP-1230 (ADR-0039 decision 6) — a declared index series must be physical; the same shared
    # validator the White inject boundary uses (engine/perturbations.py::index_series_problems).
    from spacesim.engine.perturbations import index_series_problems
    for reason in index_series_problems(list(vignette.space_weather_series), "at_sim_s"):
        problems.append({"where": "space_weather_series", "reason": reason})
    if isinstance(vignette.initial_space_weather, dict) and "index_series" in vignette.initial_space_weather:
        for reason in index_series_problems(vignette.initial_space_weather["index_series"], "t"):
            problems.append({"where": "initial_space_weather.index_series", "reason": reason})
    problems.extend(_environmental_anomaly_problems(vignette.environmental_anomalies, asset_sections, bused))

    # Catch-all: whatever else build_world enforces is enforced at load too.
    if not problems:
        try:
            build_world(vignette.model_copy(deep=True))
        except Exception as exc:  # noqa: BLE001
            problems.append({"where": "build", "reason": f"{type(exc).__name__}: {exc}"})
    return problems


def build_world(vignette: Vignette, overrides: Optional[dict] = None):
    """Instantiate a WorldState + VignetteContext from the vignette and parameter choices."""
    from spacesim.engine.world import WorldState  # local import: engine layer

    start = simtime.from_iso(vignette.start_epoch_utc)
    params = resolve_params(vignette, overrides)
    world = WorldState(now=start)

    for owner, force in _force_sections(vignette):
        for spec in force:
            asset = Asset.model_validate(_asset_data(spec, owner, start))
            world.assets[asset.id] = asset

    for spec in vignette.sensors:
        sensor = Sensor.model_validate(spec)
        world.sensors[sensor.id] = sensor

    # Satellite/constellation sizing (~24 total, ≤3 per constellation) is a soft guideline for
    # typical White-Cell hardware, not an engine-enforced cap (ADR-0019, NFR-1300) — IP-1061
    # (BL-0065) removed the hard ValueError this used to raise. The clock-lag watchdog
    # (`SessionManager._record_catch_up_lag`) is the intended backstop for oversized vignettes.

    # SSN per-cell networks (opt-in via vignette params; off by default) — `docs/SSN-DESIGN.md`.
    ssn_networks: dict = {}
    from spacesim.engine.ssn import instantiate_network as _ssn_instantiate
    for cell, key in (("blue", "ssn_blue_dispersion"), ("red", "ssn_red_dispersion")):
        net = _ssn_instantiate(world, cell, str(params.get(key, "off")))
        if net is not None:
            ssn_networks[cell] = net

    # IP-1172 (FR-3420, NFR-2010) — always produce a fully cell-keyed roe dict. An explicit
    # vignette.roe block is used directly (missing cell/sub-key defaults to False — fail safe,
    # never silently authorized); otherwise the legacy flat parameters are replicated
    # identically to both cells, so all 19 pre-IP-1172 vignettes are unaffected.
    if vignette.roe:
        roe = {
            cell: {
                "kinetic_authorized": bool(vignette.roe.get(cell, {}).get("kinetic_authorized", False)),
                "cyber_authorized": bool(vignette.roe.get(cell, {}).get("cyber_authorized", False)),
            }
            for cell in ("blue", "red")
        }
    else:
        legacy = {
            "kinetic_authorized": bool(params.get("red_kinetic_authorized", False)),
            "cyber_authorized": bool(params.get("cyber_authorized", params.get("red_cyber_authorized", False))),
        }
        roe = {"blue": dict(legacy), "red": dict(legacy)}
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
        gating_rules=list(vignette.effect_gating_rules),
        detectability_config=list(vignette.effect_detectability_config),
    )
    # IP-1200 (FR-5510) — save-as-scenario's carried-forward state, consumed only when present
    # (absent/empty for every pre-IP-1200 vignette, per NFR-2010).
    if vignette.initial_tracks:
        from spacesim.engine.custody import Track
        world.tracks = [Track.model_validate(t) for t in vignette.initial_tracks]
    if vignette.initial_space_weather:
        world.space_weather = dict(vignette.initial_space_weather)
    # IP-1230 (ADR-0039 decision 1) — a declared index series, stored in absolute sim time and
    # merged into (never replacing) world.space_weather, so `severity` is kept.
    if vignette.space_weather_series:
        entries = [{"t": start + int(float(e["at_sim_s"]) * 1_000_000),
                    **{k: float(e[k]) for k in ("f107", "kp") if k in e}}
                   for e in vignette.space_weather_series]
        merged = sorted(list(world.space_weather.get("index_series", [])) + entries, key=lambda e: e["t"])
        world.space_weather = {**world.space_weather, "index_series": merged}
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


def _measure_metric(world, ctx: VignetteContext, m: dict):
    """IP-1064 (BL-0131, FR-4420 Outputs) — the measured quantity `_evaluate_metric` compares, for
    the condition-inject record: range in km for ``proximity``/``evade``, the track's current
    confidence for ``custody``/``deny_custody`` (0.0 with no track). Any other metric has no
    measured quantity, so its boolean result is the value. Read-only; never changes a decision."""
    kind = m.get("kind")
    if kind in ("proximity", "evade"):
        return _range_km(world, m["a"], m["b"])
    if kind in ("custody", "deny_custody"):
        tr = world.track_for(m["side"], m["object"])
        return float(tr.current_confidence(world.now)) if tr is not None else 0.0
    return _evaluate_metric(world, ctx, m)
