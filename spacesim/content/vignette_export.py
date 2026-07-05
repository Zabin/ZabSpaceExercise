"""IP-1173 (FR-5110) — reverse serialization: WorldState + VignetteContext -> Vignette YAML.

The mirror image of ``vignette.py``'s ``load_vignette()``/``build_world()``: walks a draft
session's live state and emits a complete, loadable vignette file. Kept in a separate module
since it is a genuinely new, opposite-direction responsibility — not a variant of
``session/manager.py``'s ``save_state()``/``from_state()``, which serialize session/game state
(eventlog, pending orders), not authorable vignette content.
"""
from __future__ import annotations

import re

import yaml

from spacesim.content.vignette import VIGNETTE_DIR, Vignette, VignetteContext
from spacesim.engine import simtime
from spacesim.engine.world import WorldState

# Same charset discipline as ui_web/server.py's _validate_id / content/vignette.py's
# load_vignette() — this is now a write path to VIGNETTE_DIR, at least as sensitive as the
# existing read path.
_ID_RE = re.compile(r"^[A-Za-z0-9_.\-]{1,128}$")


def export_vignette(
    world: WorldState, ctx: VignetteContext, vignette_id: str, title: str,
    classification: str = "UNCLASSIFIED-TRAINING",
) -> Vignette:
    """Build a ``Vignette`` model from a draft session's current state. Does not write to disk
    — see ``save_vignette`` for that."""
    if not _ID_RE.match(vignette_id):
        raise ValueError(f"vignette id must match {_ID_RE.pattern}: {vignette_id!r}")

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
        start_epoch_utc=simtime.to_iso(ctx.start_epoch),
        blue_forces=blue_forces,
        red_forces=red_forces,
        neutral_forces=neutral_forces,
        sensors=sensors,
        roe=dict(ctx.roe),
        objectives=dict(ctx.objectives),
    )


def save_vignette(
    world: WorldState, ctx: VignetteContext, vignette_id: str, title: str,
    classification: str = "UNCLASSIFIED-TRAINING",
) -> str:
    """Build a ``Vignette`` from the current draft state and write it to ``VIGNETTE_DIR`` as
    ``{vignette_id}.yaml`` — the only code path that writes an authored vignette file for the
    Creator (``FR-5110``'s own Postcondition: no partial file exists before this explicit
    action). Returns the written file's path.

    Known limitation (not this package's scope to resolve — see IP-1173's Risks/Outstanding
    Issues): this overwrites an existing file of the same id without confirmation, the same way
    a hand-edited YAML file would. A "confirm overwrite" UX belongs to IP-1174's Creator UI.
    """
    vignette = export_vignette(world, ctx, vignette_id, title, classification=classification)
    candidate = (VIGNETTE_DIR / f"{vignette_id}.yaml").resolve()
    vignette_root = VIGNETTE_DIR.resolve()
    if vignette_root not in candidate.parents:
        raise ValueError(f"vignette id escapes VIGNETTE_DIR: {vignette_id!r}")
    candidate.write_text(
        yaml.safe_dump({"vignette": vignette.model_dump(exclude_none=True)}, sort_keys=False),
        encoding="utf-8",
    )
    return str(candidate)
