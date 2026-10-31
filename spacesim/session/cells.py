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
        effect_windows = []
        for ae in world.active_effects:
            if own_owner.get(ae.target) == cell:
                visible_effects.append({
                    "target": ae.target,
                    "symptom": ae.outcome,
                    # Source is withheld unless the effect is overtly attributable.
                    "attributed": ae.attribution == "overt",
                })
                # Time spans for pass-correlation shading on the telemetry graph (§9.1) — own assets only.
                effect_windows.append({
                    "target": ae.target, "category": getattr(ae, "category", ""),
                    "start": ae.start, "end": ae.end,
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
            effect_windows=effect_windows,
            messages=messages,
            objectives=objectives or {},
        )

    @staticmethod
    def activity_rows(tagged: list[dict], cell: str, now: int) -> list[dict]:
        """IP-1088 (FR-6210/FR-6220) — the single fail-closed filter for the per-cell activity feed.

        ``tagged`` is ground-truth rows from ``InProcessSession.cell_activity``, each
        ``{"row": <feed row>, "owner": <owning cell>, "effect": <None | {template, category,
        outcome, overt}>}``. White keeps every row. Blue/Red are an allow-list by kind: their own
        orders; effects on assets they own that have started, relabelled to what their ``CellView``
        already grants (category + symptom, ``(attributed)`` only when overt - never the template).
        Any other kind (injects, and anything added later) is dropped for a player cell.
        """
        if cell == "white":
            return [t["row"] for t in tagged]
        out: list[dict] = []
        for t in tagged:
            row = t["row"]
            kind = row.get("kind")
            if kind == "order":
                if t.get("owner") == cell:
                    out.append(row)
            elif kind == "effect":
                eff = t.get("effect") or {}
                if t.get("owner") != cell or row["start"] > now:
                    continue
                cat = eff.get("category") or "effect"
                label = f"{cat} \u2192 {row['target']} ({eff.get('outcome')})"
                if eff.get("overt"):
                    label += " (attributed)"
                out.append({**row, "action": cat, "label": label})
        return out
