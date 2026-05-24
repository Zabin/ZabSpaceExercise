"""CellController — applies fog-of-war to produce a per-cell view (``05-cell-interfaces.md``).

A cell sees its **own** assets/sensors in full, but other-side objects **only** through its own
SDA tracks (custody), and effects on its assets as **symptoms** whose source is hidden unless the
effect is overtly attributable. White Cell uses ``get_godview`` (ground truth) instead. Enforcing
this here — not in the UI — is what stops a future untrusted client from cheating.
"""

from __future__ import annotations

from spacesim.session.api import CellView


class CellController:
    @staticmethod
    def view(world, cell: str, objectives: dict | None = None) -> CellView:
        own_owner = {a.id: a.owner for a in world.assets.values()}

        own_assets = [a.model_dump() for a in world.assets.values() if a.owner == cell]
        own_sensors = [s.model_dump() for s in world.sensors.values() if s.owner == cell]
        known_tracks = [t.model_dump() for t in world.tracks if t.owner == cell]

        visible_effects = []
        for ae in world.active_effects:
            if own_owner.get(ae.target) == cell:
                visible_effects.append({
                    "target": ae.target,
                    "symptom": ae.outcome,
                    # Source is withheld unless the effect is overtly attributable.
                    "attributed": ae.attribution == "overt",
                })

        messages = [m for m in world.messages if cell in m.get("to", [])]

        return CellView(
            cell=cell,
            now=world.now,
            own_assets=own_assets,
            own_sensors=own_sensors,
            known_tracks=known_tracks,
            visible_effects=visible_effects,
            messages=messages,
            objectives=objectives or {},
        )
