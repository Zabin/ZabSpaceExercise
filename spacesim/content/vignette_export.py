"""IP-1173 (FR-5110) — reverse serialization: WorldState + VignetteContext -> Vignette YAML.

The mirror image of ``vignette.py``'s ``load_vignette()``/``build_world()``: walks a draft
session's live state and emits a complete, loadable vignette file. Kept in a separate module
since it is a genuinely new, opposite-direction responsibility — not a variant of
``session/manager.py``'s ``save_state()``/``from_state()``, which serialize session/game state
(eventlog, pending orders), not authorable vignette content.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from typing import Optional

from spacesim.config import load_content_config
from spacesim.content.vignette import Vignette, VignetteContext, _resolve_within_root, _validate_id
from spacesim.engine import simtime
from spacesim.engine.world import WorldState
from spacesim.version import simulator_version


def export_vignette(
    world: WorldState, ctx: VignetteContext, vignette_id: str, title: str,
    classification: str = "UNCLASSIFIED-TRAINING", start_epoch: Optional[int] = None,
) -> Vignette:
    """Build a ``Vignette`` model from a draft session's current state. Does not write to disk
    — see ``save_vignette`` for that.

    IP-1200 (FR-5510): ``start_epoch``, when given, becomes the resulting vignette's declared
    start (a save-as-scenario call passes the save moment); omitted, this reproduces IP-1173's
    exact prior behavior (``ctx.start_epoch``, the *original* vignette's start)."""
    _validate_id(vignette_id)

    blue_forces: list[dict] = []
    red_forces: list[dict] = []
    neutral_forces: list[dict] = []
    buckets = {"blue": blue_forces, "red": red_forces, "neutral": neutral_forces}
    for asset in world.assets.values():
        buckets[asset.owner].append(asset.model_dump(exclude={"owner"}))

    sensors = [sensor.model_dump() for sensor in world.sensors.values()]

    return Vignette(
        id=vignette_id,
        title=title,
        classification=classification,
        start_epoch_utc=simtime.to_iso(start_epoch if start_epoch is not None else ctx.start_epoch),
        blue_forces=blue_forces,
        red_forces=red_forces,
        neutral_forces=neutral_forces,
        sensors=sensors,
        roe=dict(ctx.roe),
        objectives=dict(ctx.objectives),
        initial_tracks=[t.model_dump() for t in world.tracks],
        simulator_version=simulator_version(),
        initial_space_weather=dict(world.space_weather) if world.space_weather else None,
    )


def save_vignette(
    world: WorldState, ctx: VignetteContext, vignette_id: str, title: str,
    classification: str = "UNCLASSIFIED-TRAINING", start_epoch: Optional[int] = None,
) -> str:
    """Build a ``Vignette`` from the current draft state and write it to the configured
    ``user_save_dir`` (IP-1180, FR-5420) as ``{vignette_id}.yaml`` — the only code path that
    writes an authored vignette file for the Creator (``FR-5110``'s own Postcondition: no partial
    file exists before this explicit action). Returns the written file's path.

    Raises ``ValueError`` if no ``user_save_dir`` is configured (Design Decision 3) — a save
    request never silently falls back to ``VIGNETTE_DIR``, which would defeat FR-5420's purpose.

    Known limitation (not this package's scope to resolve — see IP-1173's Risks/Outstanding
    Issues): this overwrites an existing file of the same id without confirmation, the same way
    a hand-edited YAML file would. A "confirm overwrite" UX belongs to IP-1174's Creator UI.
    """
    vignette = export_vignette(world, ctx, vignette_id, title, classification=classification,
                                start_epoch=start_epoch)
    user_save_dir = load_content_config().user_save_dir
    if not user_save_dir:
        raise ValueError(
            "no user-save directory configured — set content.user_save_dir in spacesim.config.yaml"
        )
    candidate = _resolve_within_root(Path(user_save_dir), f"{vignette_id}.yaml")
    candidate.write_text(
        yaml.safe_dump({"vignette": vignette.model_dump(exclude_none=True)}, sort_keys=False),
        encoding="utf-8",
    )
    return str(candidate)
