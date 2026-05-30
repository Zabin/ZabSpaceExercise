"""Safe-mode recovery procedure chain (``12-safe-mode-loop.md`` §5, §6.3).

Recovery is a multi-pass procedure, not a button: detect/confirm at the first contact, then a
sequence of command-uplink passes to clear faults, re-point, re-enable the payload, and verify.
The number of passes is the §6.3 model — ``base × recovery_difficulty`` — and **if the inducing
cause persists** (e.g. the cyber vulnerability is unpatched), the satellite is **re-safed**: the
defender must remove the root cause (patch the vuln) before recovery sticks. Steps run as
scheduled events at real command-uplink windows, so the whole chain is deterministic and replays.
"""

from __future__ import annotations

from typing import Optional

from spacesim.engine.access import AccessConfig, AccessProvider, COMMAND_UPLINK
from spacesim.engine.bus import exit_safe_mode, refresh_ground_view
from spacesim.engine.orders import scene_from_world
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.world import WorldState

PASSES_FOR_DIFFICULTY = {"quick": 1, "realistic": 2, "punishing": 3}


class RecoverySystem:
    def __init__(
        self,
        sim,
        difficulty: str = "realistic",
        root_cause_persists: bool = True,
        access_config: Optional[AccessConfig] = None,
    ) -> None:
        self.sim = sim
        self.prop = ModeratePropagator()
        self.difficulty = difficulty
        self.root_cause_persists = root_cause_persists
        self.access_config = access_config
        sim.register_handler("recovery_confirm", self._h_confirm)
        sim.register_handler("recovery_finish", self._h_finish)

    @property
    def world(self) -> WorldState:
        return self.sim.world

    def passes_needed(self) -> int:
        return PASSES_FOR_DIFFICULTY.get(self.difficulty, 2)

    def begin_recovery(self, sat_id: str, via_station: str) -> dict:
        """Schedule confirmation + a multi-pass recovery chain over command-uplink windows."""
        ap = AccessProvider(scene_from_world(self.world), propagator=self.prop, config=self.access_config)
        now = self.sim.clock.now
        wins = ap.windows(via_station, sat_id, COMMAND_UPLINK, now, now + 24 * 3600 * 1_000_000)
        if not wins:
            return {"ok": False, "reason": "no_pass"}
        n = self.passes_needed()
        passes_used = min(n, len(wins))
        self.sim.schedule(wins[0].start, "recovery_confirm", {"sat": sat_id})
        finish = wins[passes_used - 1]
        self.sim.schedule(finish.start, "recovery_finish",
                          {"sat": sat_id, "passes_used": passes_used,
                           "root_cause_persists": self.root_cause_persists})
        return {"ok": True, "passes_used": passes_used, "finish_at": finish.start}

    def _h_confirm(self, world: WorldState, payload: dict, rng) -> None:
        sat = world.assets.get(payload["sat"])
        if sat is None or sat.bus_state is None or not sat.bus_state.safe_mode.active:
            return
        sm = sat.bus_state.safe_mode
        sm.defender_confirmed = True
        sm.defender_diagnosis = "suspected_attack" if sm.cause in ("cyber", "ew") else (sm.cause or "fault")
        refresh_ground_view(sat.bus_state, world.now)  # stored telemetry dump confirms it
        # FUTURE-WORK §5: step deep-links — first contact completes establish_contact + dump_telemetry.
        if "establish_contact" not in sm.steps_done:
            sm.steps_done.append("establish_contact")
        if "dump_telemetry" not in sm.steps_done:
            sm.steps_done.append("dump_telemetry")
        sm.current_step = "diagnose"

    def _h_finish(self, world: WorldState, payload: dict, rng) -> None:
        sat = world.assets.get(payload["sat"])
        if sat is None or sat.bus_state is None or not sat.bus_state.safe_mode.active:
            return
        sm = sat.bus_state.safe_mode
        sm.passes_used += int(payload["passes_used"])
        if payload.get("root_cause_persists") and self._root_cause_unresolved(sat):
            sm.blocked_reason = f"root cause persists ({sm.cause})"  # re-safed: stays in safe mode
            sm.current_step = "blocked"
            world.effect_log.append({"t": world.now, "template": "recovery", "target": sat.id,
                                     "achieved": "re_safed", "success": False})
            return
        passes = sm.passes_used
        steps = list(sm.steps_done)
        # Recovery complete: all standard steps applied.
        for s in ("patch", "re_enable"):
            if s not in steps:
                steps.append(s)
        exit_safe_mode(sat.bus_state)
        sat.bus_state.safe_mode.passes_used = passes  # preserve for inspection
        sat.bus_state.safe_mode.steps_done = steps
        sat.bus_state.safe_mode.current_step = "done"
        world.effect_log.append({"t": world.now, "template": "recovery", "target": sat.id,
                                 "achieved": "recovered", "success": True})

    def _root_cause_unresolved(self, sat) -> bool:
        if sat.bus_state.safe_mode.cause == "cyber":
            return any(not v.get("patched") for v in sat.cyber_vulnerabilities)
        return False
