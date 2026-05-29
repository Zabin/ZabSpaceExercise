"""Red doctrine profiles — selectable AI-Red behavior presets (``00-BUILD-SPECIFICATION.md`` §10 M6).

A light behavior layer that issues doctrine-flavored orders for Red assets through the same
OrderSystem a human Red cell would use (so it is fully constrained by windows, ROE, and custody):

  * ``russia_ew_first``   — lead with electromagnetic attack: jam Blue links.
  * ``china_integrated``  — integrated: cyber the link/ground segment where a vector exists, else jam.
  * ``generic``           — cautious: task Red sensors to build custody, no offensive action.

This is a *preset*, not an optimizer — enough to give Blue something doctrinally recognisable to
react to. It reads the chosen profile from the vignette/parameters (``ctx.red_doctrine_profile``).
"""

from __future__ import annotations

from spacesim.engine.orders import Order


class RedDoctrine:
    def __init__(self, manager) -> None:
        self.mgr = manager
        self.profile = manager.ctx.red_doctrine_profile

    def _blue_satellites(self) -> list[str]:
        w = self.mgr.world
        return [i for i, a in w.assets.items() if a.owner == "blue" and a.orbit is not None]

    def _red_assets(self, kind: str) -> list[str]:
        w = self.mgr.world
        return [i for i, a in w.assets.items() if a.owner == "red" and a.kind == kind]

    def step(self) -> list:
        """Issue one round of doctrine-appropriate Red orders; returns the OrderAcks."""
        acks = []
        targets = self._blue_satellites()
        if not targets:
            return acks
        tgt = targets[0]

        if self.profile in ("russia_ew_first", "china_integrated"):
            for jammer in self._red_assets("jammer"):
                acks.append(self.mgr.issue_order("red", Order(
                    cell="red", actor=jammer, action="jam", target=tgt,
                    params={"success_prob": 1.0, "outcome": "deny"})))

        if self.profile == "china_integrated":
            for cyber in self._red_assets("cyber_unit"):
                victim = self._first_vulnerable(targets)
                if victim is not None:
                    vid, vector = victim
                    acks.append(self.mgr.issue_order("red", Order(
                        cell="red", actor=cyber, action="cyber", target=vid,
                        params={"access_vector": vector, "outcome": "safe_mode",
                                "success_prob": 1.0, "sm_susceptibility": 1.0})))

        if self.profile == "generic":
            for sensor in [i for i, s in self.mgr.world.sensors.items() if s.owner == "red"]:
                acks.append(self.mgr.issue_order("red", Order(
                    cell="red", actor=sensor, action="observe", target=tgt, params={"intent": "track"})))

        return acks

    def _first_vulnerable(self, targets: list[str]):
        for tid in targets:
            asset = self.mgr.world.assets.get(tid)
            for v in (asset.cyber_vulnerabilities if asset else []):
                if not v.get("patched"):
                    return tid, v.get("vector")
        return None
