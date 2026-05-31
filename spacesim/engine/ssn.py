"""Mock Space Surveillance Network — per-cell, request-tasked observation enterprise.

Implements the design in ``docs/SSN-DESIGN.md``. Each cell owns one ``SSNNetwork`` of
``network: True`` sensors instantiated at vignette load from a **dispersion preset**
(``sparse``/``regional``/``global``/``proliferated``). Operators submit **requests** (intent +
target + regime + priority); the network resolves them at submission via the existing
``AccessProvider`` — pick the earliest viable window inside the priority's SLA, add a processing
delay, schedule two deterministic events (``ssn_collect`` then ``ssn_deliver``) on the engine
timeline. Replay reproduces both events byte-identically; cancel-before-collect is replay-safe
via the scheduler's tag-cancel (the events never log).

Affiliations (per `SSN-DESIGN.md` §3): Blue → coalition (broader spread, higher processing delay,
−1 concurrency); Red → national (preset as-is). Networks are fog-scoped — requests, queue, and
products belong only to the requester; White sees both.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from spacesim.engine.access import AccessProvider, SENSOR_OBSERVATION
from spacesim.engine.custody import Track, observe
from spacesim.engine.entities import GeoPoint, Sensor
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import scene_from_world
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.world import WorldState

# ----------------------------- Dispersion presets ---------------------------

_DISPERSION = ("sparse", "regional", "global", "proliferated")

# Per-preset concurrency cap (national flavour). Coalition subtracts 1 (floor 1).
_CONCURRENCY = {"sparse": 1, "regional": 2, "global": 3, "proliferated": 5}

# Hybrid SLA: max-wait per priority (seconds); processing/dissemination delay per priority.
MAX_WAIT_S       = {"immediate": 900, "priority": 3600, "routine": 21600}
PROCESSING_DELAY_S = {"immediate": 120, "priority": 600, "routine": 1800}
# FUTURE-WORK §7 — per-priority "cost" (collection-budget units). Forces White-Cell triage
# when the budget is finite; defaults are tuned so a 100-unit budget covers ~5 immediate /
# ~15 priority / ~50 routine requests over a session.
PRIORITY_COST    = {"immediate": 20, "priority": 7, "routine": 2}
COALITION_DELAY_MULTIPLIER = 1.5         # coalition queues a partner-shared product (§7.1)

# Sensor type → regimes the SSN deems eligible (`SSN-DESIGN.md` §5 matrix). Ground radar is
# intentionally NOT eligible for GEO (forces sparse radar-only nets to fail GEO requests cleanly).
_REGIME_FOR_KIND = {
    "ground_radar":   {"LEO", "MEO"},
    "ground_optical": {"LEO", "MEO", "GEO"},
    "space_based":    {"LEO", "MEO", "GEO", "HEO", "cislunar"},
}


def _radar_sites(preset: str) -> list[tuple[float, float]]:
    """Deterministic (lat, lon) layouts per preset — site count and spread per §4."""
    if preset == "sparse":
        return [(34.0, -120.6), (30.5, -86.5), (51.5, -1.0)]
    if preset == "regional":
        return [(34.0, -120.6), (30.5, -86.5), (51.5, -1.0), (35.7, 139.7)]
    if preset == "global":
        return [(34.0, -120.6), (30.5, -86.5), (51.5, -1.0), (35.7, 139.7), (-31.9, 115.9)]
    return [(34.0, -120.6), (30.5, -86.5), (51.5, -1.0), (35.7, 139.7),
            (-31.9, 115.9), (-33.9, 18.4), (28.6, 77.2), (64.1, -21.9)]


def _optical_sites(preset: str) -> list[tuple[float, float]]:
    if preset in ("sparse",):
        return []
    if preset == "regional":
        return [(20.7, -156.3), (32.7, -16.9)]
    if preset == "global":
        return [(20.7, -156.3), (32.7, -16.9), (-23.3, 16.5), (-43.5, 172.6)]
    return [(20.7, -156.3), (32.7, -16.9), (-23.3, 16.5), (-43.5, 172.6),
            (40.5, 23.0), (37.2, -3.0)]


def _space_count(preset: str) -> int:
    return {"sparse": 0, "regional": 0, "global": 1, "proliferated": 3}[preset]


# --------------------------- Data models -----------------------------------

@dataclass
class SSNNetwork:
    cell: str                                 # blue | red
    affiliation: str                          # coalition | national
    dispersion: str                           # sparse | regional | global | proliferated
    sensors: list[str] = field(default_factory=list)
    concurrency: int = 1


@dataclass
class SSNRequest:
    id: str
    cell: str                                 # requester (fog scope)
    intent: str                               # search | track | characterize
    target: str
    regime: str                               # LEO | MEO | GEO | HEO | cislunar
    priority: str                             # routine | priority | immediate
    submitted_at: int = 0
    assigned_sensor: Optional[str] = None
    collect_at: Optional[int] = None
    product_at: Optional[int] = None
    state: str = "DRAFT"                      # DRAFT | SCHEDULED | COLLECTED | DELIVERED | CANCELLED | FAILED
    fail_reason: Optional[str] = None
    # FUTURE-WORK §7 — route through a non-organic network (e.g. "commercial"). When empty,
    # uses the cell's own network (legacy default). When set, looks up self.networks[network].
    network: str = ""


@dataclass
class SSNAck:
    ok: bool
    id: str = ""
    reason: str = ""
    state: str = "DRAFT"
    assigned_sensor: Optional[str] = None
    collect_at: Optional[int] = None
    product_at: Optional[int] = None


# --------------------------- Network instantiation -------------------------

def _network_prefix(cell: str) -> str:
    return f"{cell.upper()}-SSN"


def instantiate_network(world: WorldState, cell: str, dispersion: str,
                        affiliation: str = "",
                        sensor_owner: Optional[str] = None) -> Optional[SSNNetwork]:
    """Generate the network's sensors into ``world.sensors`` and return its ``SSNNetwork``.

    ``dispersion=='off'`` returns ``None``. Affiliations default per the design: Blue → coalition,
    Red → national. ``sensor_owner`` lets the commercial network use ``neutral`` sensors while
    keeping the network keyed by ``cell="commercial"`` (FUTURE-WORK §7).
    """
    if dispersion in (None, "off", ""):
        return None
    if dispersion not in _DISPERSION:
        return None
    aff = affiliation or ("coalition" if cell == "blue" else "national")
    prefix = _network_prefix(cell)
    own = sensor_owner if sensor_owner is not None else cell
    sensor_ids: list[str] = []

    for i, (lat, lon) in enumerate(_radar_sites(dispersion), start=1):
        sid = f"{prefix}-RDR-{i}"
        world.sensors[sid] = Sensor(id=sid, owner=own, kind="ground_radar",
                                    location=GeoPoint(lat_deg=lat, lon_deg=lon, alt_m=0.0),
                                    network=True)
        sensor_ids.append(sid)
    for i, (lat, lon) in enumerate(_optical_sites(dispersion), start=1):
        sid = f"{prefix}-OPT-{i}"
        world.sensors[sid] = Sensor(id=sid, owner=own, kind="ground_optical",
                                    location=GeoPoint(lat_deg=lat, lon_deg=lon, alt_m=0.0),
                                    needs_lighting=True, network=True)
        sensor_ids.append(sid)
    # Space-based observers in GEO belt at fixed slot longitudes; cislunar slot above (HEO apogee).
    for i in range(_space_count(dispersion)):
        sid = f"{prefix}-SBO-{i + 1}"
        # Deterministic GEO equatorial slot, longitude spread across the belt.
        raan_deg = 30.0 + 120.0 * i
        is_cislunar = (i == 2)               # third observer is the high-apogee/cislunar one
        a_m = 384_400_000.0 if is_cislunar else 42_164_000.0
        e = 0.7 if is_cislunar else 0.0
        i_deg = 28.0 if is_cislunar else 0.0
        orbit = OrbitState(a_m=a_m, e=e, i_deg=i_deg, raan_deg=raan_deg,
                           argp_deg=0.0, ta_deg=0.0, epoch=world.now)
        world.sensors[sid] = Sensor(id=sid, owner=own, kind="space_based", orbit=orbit, network=True)
        sensor_ids.append(sid)

    concurrency = max(1, _CONCURRENCY[dispersion] - (1 if aff == "coalition" else 0))
    return SSNNetwork(cell=cell, affiliation=aff, dispersion=dispersion,
                      sensors=sensor_ids, concurrency=concurrency)


# --------------------------- The system ------------------------------------

class SSNSystem:
    """Per-cell SSN — submission resolution + deterministic ``ssn_collect``/``ssn_deliver`` events."""

    def __init__(self, sim, networks: dict[str, SSNNetwork], access_config=None,
                 budgets: Optional[dict[str, int]] = None) -> None:
        self.sim = sim
        self.networks = networks                                  # cell -> SSNNetwork
        self.requests: dict[str, SSNRequest] = {}
        self._counter = 0
        self.prop = ModeratePropagator()
        self.access_config = access_config
        self._bookings: dict[str, list[tuple[int, int]]] = {}     # sensor_id -> [(start, end)]
        self._inflight: dict[str, int] = {c: 0 for c in networks}
        # FUTURE-WORK §7 — collection-budget triage. None = unlimited (current default).
        # Otherwise: per-cell remaining budget units, decremented by PRIORITY_COST on submit.
        self.budgets: Optional[dict[str, int]] = dict(budgets) if budgets is not None else None
        sim.register_handler("ssn_collect", self._h_collect)
        sim.register_handler("ssn_deliver", self._h_deliver)

    # --- helpers -----------------------------------------------------------

    @property
    def world(self) -> WorldState:
        return self.sim.world

    def _ap(self) -> AccessProvider:
        return AccessProvider(scene_from_world(self.world), propagator=self.prop, config=self.access_config)

    def _eligible(self, network: SSNNetwork, regime: str) -> list[str]:
        out = []
        for sid in network.sensors:
            s = self.world.sensors.get(sid)
            if s is not None and regime in _REGIME_FOR_KIND.get(s.kind, set()):
                out.append(sid)
        return out

    def _contended(self, sid: str, start: int, end: int) -> bool:
        return any(not (end <= b0 or start >= b1) for (b0, b1) in self._bookings.get(sid, []))

    # --- public API --------------------------------------------------------

    def submit_request(self, cell: str, req: SSNRequest) -> SSNAck:
        """Hybrid resolution + deterministic scheduling. Read-only on failure paths."""
        # FUTURE-WORK §7 — third-party / commercial network routing. If req.network is set
        # (e.g. "commercial"), use that network's sensors instead of the cell's organic SSN.
        # Falls back to the cell's own network when unset (legacy behaviour).
        net_key = req.network or cell
        net = self.networks.get(net_key)
        if net is None:
            return SSNAck(ok=False, reason="no_network")
        if req.regime not in {"LEO", "MEO", "GEO", "HEO", "cislunar"}:
            return SSNAck(ok=False, reason="bad_regime")
        if req.priority not in MAX_WAIT_S:
            return SSNAck(ok=False, reason="bad_priority")
        if req.target not in self.world.assets:
            return SSNAck(ok=False, reason="no_such_target")
        # FUTURE-WORK §7 — collection-budget triage. Commercial requests cost 2× as much.
        if self.budgets is not None:
            cost = PRIORITY_COST[req.priority] * (2 if req.network == "commercial" else 1)
            remaining = self.budgets.get(cell, 0)
            if cost > remaining:
                return SSNAck(ok=False, reason="budget_exhausted")
            self.budgets[cell] = remaining - cost

        req.submitted_at = self.sim.clock.now
        eligible = self._eligible(net, req.regime)
        if not eligible:
            req.state, req.fail_reason = "FAILED", "no_coverage_regime"
            self._counter += 1
            req.id = f"ssn-{self._counter}"
            self.requests[req.id] = req
            return SSNAck(ok=False, id=req.id, reason="no_coverage_regime", state="FAILED")

        # Earliest viable window across eligible sensors within the SLA horizon (hybrid rule §7.2).
        ap = self._ap()
        now = self.sim.clock.now
        horizon = now + MAX_WAIT_S[req.priority] * 1_000_000
        best: Optional[tuple[str, int, int, float]] = None
        for sid in eligible:
            for w in ap.windows(sid, req.target, SENSOR_OBSERVATION, now, horizon):
                if self._contended(sid, w.start, w.end):
                    continue
                if best is None or w.start < best[1]:
                    best = (sid, w.start, w.end, float(w.quality))
                break
        if best is None:
            req.state, req.fail_reason = "FAILED", "no_coverage_within_sla"
            self._counter += 1
            req.id = f"ssn-{self._counter}"
            self.requests[req.id] = req
            return SSNAck(ok=False, id=req.id, reason="no_coverage_within_sla", state="FAILED")

        sid, start, end, quality = best
        delay_s = PROCESSING_DELAY_S[req.priority]
        if net.affiliation == "coalition":
            delay_s = int(delay_s * COALITION_DELAY_MULTIPLIER)
        if self._inflight.get(cell, 0) >= net.concurrency:
            delay_s += PROCESSING_DELAY_S[req.priority]    # saturation surcharge (§9)

        self._counter += 1
        req.id = f"ssn-{self._counter}"
        req.assigned_sensor = sid
        req.collect_at = start
        req.product_at = start + delay_s * 1_000_000
        req.state = "SCHEDULED"
        self.requests[req.id] = req
        self._bookings.setdefault(sid, []).append((start, end))
        self._inflight[cell] = self._inflight.get(cell, 0) + 1

        # Two deterministic events tagged with the request id (cancel-before-collect skips both).
        # Window quality rides on the payload so a poor (grazing) pass yields a weaker product (§8).
        self.sim.schedule(start, "ssn_collect",
                          {"req": req.id, "target": req.target, "intent": req.intent, "quality": quality},
                          actor=cell, tag=req.id)
        self.sim.schedule(req.product_at, "ssn_deliver",
                          {"req": req.id, "cell": cell, "target": req.target, "intent": req.intent},
                          actor=cell, tag=req.id)

        return SSNAck(ok=True, id=req.id, state="SCHEDULED",
                      assigned_sensor=sid, collect_at=start, product_at=req.product_at)

    def cancel_request(self, cell: str, rid: str) -> bool:
        r = self.requests.get(rid)
        if r is None or (cell != "white" and r.cell != cell):
            return False
        if r.state != "SCHEDULED":
            return False
        self.sim.cancel(rid)
        r.state = "CANCELLED"
        self._inflight[r.cell] = max(0, self._inflight.get(r.cell, 0) - 1)
        return True

    def list_requests(self, cell: str) -> list[dict]:
        out = []
        for r in self.requests.values():
            if cell != "white" and r.cell != cell:
                continue
            out.append({"id": r.id, "cell": r.cell, "intent": r.intent, "target": r.target,
                        "regime": r.regime, "priority": r.priority, "state": r.state,
                        "assigned_sensor": r.assigned_sensor, "collect_at": r.collect_at,
                        "product_at": r.product_at, "submitted_at": r.submitted_at,
                        "reason": r.fail_reason})
        return out

    def coverage(self, cell: str, regime: str) -> dict:
        """Phenomenology check ± earliest viable window (across the network) for the regime."""
        net = self.networks.get(cell)
        if net is None:
            return {"covered": False, "sensors": [], "next_window": None}
        # Phenomenology: which member sensors are *kind-eligible* for the regime.
        eligible_kinds = [sid for sid in net.sensors
                          if regime in _REGIME_FOR_KIND.get(self.world.sensors[sid].kind, set())]
        return {"covered": bool(eligible_kinds), "sensors": eligible_kinds,
                "concurrency": net.concurrency, "affiliation": net.affiliation,
                "dispersion": net.dispersion}

    # --- handlers ----------------------------------------------------------
    # Handlers are pure on ``(world, payload)`` so replay re-runs them on a fresh world byte-
    # identically. Per-request bookkeeping in ``self.requests`` is for the UI / list/cancel; it
    # has no effect on the WorldState that replay reproduces (and is cleared on rewind via _rebind).

    def _h_collect(self, world: WorldState, payload: dict, rng) -> None:
        """Stage the measurement on ``world.ssn_staged`` (replay-safe). Skip if target is lost."""
        rid = payload["req"]
        target = payload["target"]
        obj = world.assets.get(target)
        if obj is None or getattr(obj, "health", "nominal") == "destroyed":
            req = self.requests.get(rid)
            if req is not None:
                req.state, req.fail_reason = "FAILED", "target_lost"
                self._inflight[req.cell] = max(0, self._inflight.get(req.cell, 0) - 1)
            return
        world.ssn_staged[rid] = {
            "orbit": obj.orbit.model_dump() if obj.orbit is not None else None,
            "quality": float(payload.get("quality", 1.0)),
        }
        req = self.requests.get(rid)
        if req is not None:
            req.state = "COLLECTED"

    def _h_deliver(self, world: WorldState, payload: dict, rng) -> None:
        """Apply the staged measurement to the requesting cell's Track (fog-scoped)."""
        rid = payload["req"]
        cell = payload["cell"]
        target = payload["target"]
        intent = payload["intent"]
        staged = world.ssn_staged.pop(rid, None)
        if staged is None:
            req = self.requests.get(rid)
            if req is not None:
                req.state, req.fail_reason = "FAILED", "target_lost"
            return
        track = world.track_for(cell, target)
        if track is None:
            track = Track(object=target, owner=cell, last_observation=world.now, confidence=0.0)
            world.tracks.append(track)
        # Characterize products land high-confidence (the SSN delivers a finished assessment, not a
        # series of cuts); track/search add modest gain so custody still wants follow-on requests.
        # Window quality scales the gain (§8 — a grazing pass yields a weaker product).
        base = 0.95 if intent == "characterize" else 0.5
        wq = float(staged.get("quality", 1.0))
        gain = base * (0.5 + 0.5 * wq)
        confidence = min(1.0, track.current_confidence(world.now) + gain)
        observe(track, world.now, quality=confidence,
                characterizes=(intent == "characterize"), classification=None)
        if staged.get("orbit") is not None:
            track.state_estimate = OrbitState.model_validate(staged["orbit"])
        world.messages.append({"to": [cell], "t": world.now,
                               "text": f"SSN product delivered: {target} ({intent})"})
        req = self.requests.get(rid)
        if req is not None:
            req.state = "DELIVERED"
            self._inflight[cell] = max(0, self._inflight.get(cell, 0) - 1)
