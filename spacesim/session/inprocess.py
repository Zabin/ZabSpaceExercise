"""In-process implementation of the SessionAPI (v1: one machine, one player).

Holds a registry of live SessionManagers keyed by session id. This is the exact boundary a
network transport will later wrap — the method bodies stay; only the call mechanism changes.
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

from spacesim.content.vignette import list_vignettes, load_vignette
from spacesim.engine.orders import Order
from spacesim.session.api import Ack, CellView, OrderAck
from spacesim.session import aar
from spacesim.session.manager import SessionManager
from spacesim.session.redai import RedDoctrine


class InProcessSession:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionManager] = {}
        self._counter = 0

    # -- multiplayer plumbing --------------------------------------------------
    # Every mutation is wrapped with the session's RLock; every read first calls
    # catch_up() so the lazy server-authoritative clock advances under the lock.
    # See docs/build-spec/04 §M8 (LAN multiplayer seam).
    @contextmanager
    def _locked(self, session: str) -> Iterator[SessionManager]:
        mgr = self._sessions[session]
        with mgr._lock:
            yield mgr

    def catch_up(self, session: str) -> None:
        """Server-authoritative clock tick: advance sim to wall-now under the session lock."""
        self._sessions[session].catch_up()

    def set_clock(self, session: str, running: bool, rate: float = 1.0) -> dict:
        with self._locked(session) as mgr:
            mgr.set_clock(running, rate=rate)
            return mgr.clock_state()

    def clock_state(self, session: str) -> dict:
        with self._locked(session) as mgr:
            mgr._catch_up_locked()
            return mgr.clock_state()

    def list_sessions(self) -> list[dict]:
        out = []
        for sid, mgr in self._sessions.items():
            out.append({
                "sid": sid,
                "vignette_id": mgr.vignette.id,
                "title": mgr.vignette.title,
                "started": mgr.started,
                "now": mgr.sim.clock.now,
                "running": mgr._clock_running,
            })
        return out

    # -- lifecycle -------------------------------------------------------------
    def list_vignettes(self) -> list[dict]:
        return list_vignettes()

    def load_vignette(self, vignette_id: str, overrides: Optional[dict] = None, seed: int = 0) -> str:
        vignette = load_vignette(vignette_id)
        self._counter += 1
        sid = f"sess-{self._counter}"
        self._sessions[sid] = SessionManager(vignette, overrides=overrides, seed=seed)
        return sid

    def set_parameter(self, session: str, param_id: str, value) -> Ack:
        # Pre-start parameter swap replaces the manager. Hold the OLD manager's lock while
        # constructing + swapping; the new manager has its own fresh lock.
        with self._locked(session) as mgr:
            if mgr.started:
                return Ack(ok=False, reason="cannot change parameters after start")
            overrides = dict(mgr.ctx.param_values)
            overrides[param_id] = value
            self._sessions[session] = SessionManager(mgr.vignette, overrides=overrides, seed=mgr.sim._seed)
        return Ack()

    def start(self, session: str) -> Ack:
        with self._locked(session) as mgr:
            mgr.start()
        return Ack()

    # -- time control ----------------------------------------------------------
    def step(self, session: str, dt_sim_s: float) -> Ack:
        with self._locked(session) as mgr:
            mgr.step(dt_sim_s)
        return Ack()

    def advance_to(self, session: str, t: int) -> Ack:
        with self._locked(session) as mgr:
            mgr.advance_to(t)
        return Ack()

    def rewind_to(self, session: str, t: int) -> Ack:
        with self._locked(session) as mgr:
            mgr.rewind_to(t)
        return Ack()

    def undo_last(self, session: str, n: int = 1) -> Ack:
        with self._locked(session) as mgr:
            mgr.undo_last(n)
        return Ack()

    # -- injects & orders ------------------------------------------------------
    def add_tle(self, session: str, asset_id: str, line1: str, line2: str,
                owner: str = "blue", kind: str = "satellite") -> Ack:
        with self._locked(session) as mgr:
            ok, reason = mgr.add_tle(asset_id, line1, line2, owner=owner, kind=kind)
        return Ack(ok=ok, reason=reason)

    def red_doctrine_step(self, session: str) -> list[OrderAck]:
        with self._locked(session) as mgr:
            return RedDoctrine(mgr).step()

    def fire_inject(self, session: str, inject, at_sim_t: Optional[int] = None) -> Ack:
        with self._locked(session) as mgr:
            mgr.fire_inject(inject, at_sim_t=at_sim_t)
        return Ack()

    def inject_library(self) -> list[dict]:
        """FW §11.D.19 — return the reusable inject templates from content/inject_library.yaml.

        Returns the same shape as ``list_injects()`` plus the full ``effects`` payload so the
        UI's white-cell inject builder can prefill its form.  Cached after first load.
        """
        if getattr(self, "_inject_library_cache", None) is None:
            import yaml
            path = Path(__file__).resolve().parent.parent / "content" / "inject_library.yaml"
            if not path.exists():
                self._inject_library_cache = []
            else:
                try:
                    doc = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
                    self._inject_library_cache = [
                        {"id": i.get("id"), "label": i.get("label", i.get("id", "")),
                         "trigger": (i.get("trigger") or {}).get("type", "manual"),
                         "effects": i.get("effects") or []}
                        for i in (doc.get("injects") or [])
                    ]
                except Exception:
                    self._inject_library_cache = []
        return list(self._inject_library_cache)

    def issue_order(self, session: str, cell: str, order: Order) -> OrderAck:
        with self._locked(session) as mgr:
            return mgr.issue_order(cell, order)

    def validate_order(self, session: str, cell: str, order: Order) -> OrderAck:
        # dry-run is read-only but still touches order-system state; lock anyway for safety.
        with self._locked(session) as mgr:
            mgr._catch_up_locked()
            return mgr.validate_order(cell, order)

    def list_orders(self, session: str, cell: str) -> list:
        self.catch_up(session)
        return self._sessions[session].list_orders(cell)

    def cancel_order(self, session: str, cell: str, order_id: str) -> Ack:
        with self._locked(session) as mgr:
            ok = mgr.cancel_order(cell, order_id)
        return Ack(ok=ok, reason="" if ok else "order not found / not cancellable")

    def windows_ahead(self, session: str, cell: str, asset: str):
        self.catch_up(session)
        return self._sessions[session].windows_ahead(cell, asset)

    def next_contacts(self, session: str, cell: str) -> dict:
        self.catch_up(session)
        return self._sessions[session].next_contacts(cell)

    def recovery_status(self, session: str, cell: str, asset: str):
        self.catch_up(session)
        return self._sessions[session].recovery_status(cell, asset)

    def begin_recovery(self, session: str, cell: str, asset: str, via: str) -> dict:
        with self._locked(session) as mgr:
            return mgr.begin_recovery(cell, asset, via)

    # SSN
    def submit_ssn_request(self, session: str, cell: str, intent: str, target: str,
                           regime: str, priority: str = "priority"):
        with self._locked(session) as mgr:
            return mgr.submit_ssn_request(cell, intent, target, regime, priority)

    def list_ssn_requests(self, session: str, cell: str) -> list:
        self.catch_up(session)
        return self._sessions[session].list_ssn_requests(cell)

    def cancel_ssn_request(self, session: str, cell: str, rid: str) -> bool:
        with self._locked(session) as mgr:
            return mgr.cancel_ssn_request(cell, rid)

    def ssn_coverage(self, session: str, cell: str, regime: str) -> dict:
        self.catch_up(session)
        return self._sessions[session].ssn_coverage(cell, regime)

    def list_injects(self, session: str) -> list:
        return self._sessions[session].list_injects()

    # -- reads -----------------------------------------------------------------
    def get_view(self, session: str, cell: str) -> CellView:
        self.catch_up(session)
        return self._sessions[session].get_view(cell)

    def get_scene(self, session: str, cell: str):
        self.catch_up(session)
        return self._sessions[session].get_scene(cell)

    def get_telemetry(self, session: str, cell: str, asset: str):
        self.catch_up(session)
        return self._sessions[session].get_telemetry(cell, asset)

    def get_series(self, session: str, cell: str, asset: str, param: str, t0=None, t1=None,
                   n: int = 120, nominal: bool = False):
        self.catch_up(session)
        return self._sessions[session].get_series(cell, asset, param, t0=t0, t1=t1, n=n, nominal=nominal)

    def get_godview(self, session: str):
        self.catch_up(session)
        return self._sessions[session].get_godview()

    def get_eventlog(self, session: str, since_seq: int = 0) -> list:
        self.catch_up(session)
        return self._sessions[session].get_eventlog(since_seq)

    def objectives(self, session: str) -> dict:
        self.catch_up(session)
        return self._sessions[session].objectives()

    def session_brief(self, session: str, cell: str) -> dict:
        """Per-cell mission brief + ROE + deadline status, surfaced in the UI's brief panel.

        Combines static vignette `intro_brief.{cell}` text with live runtime state (current
        sim time, computed deadline, ROE booleans).  White sees both cells' briefs.
        """
        self.catch_up(session)
        mgr = self._sessions[session]
        v = mgr.vignette
        ctx = mgr.ctx
        now = mgr.world.now

        def _cell_brief(c: str) -> dict:
            text = v.intro_brief.get(c, {}) if isinstance(v.intro_brief, dict) else {}
            # Per-objective deadline: use metric.by_s if set, else ctx.landing_deadline.
            objs_out = []
            for obj in v.objectives.get(c, []):
                metric = obj.get("metric", {}) or {}
                deadline_us = ctx.start_epoch + int(float(metric["by_s"]) * 1_000_000) \
                    if "by_s" in metric else ctx.landing_deadline
                objs_out.append({
                    "id": obj.get("id"),
                    "desc": obj.get("desc", ""),
                    "metric_kind": metric.get("kind", ""),
                    "deadline": int(deadline_us),
                    "remaining_s": max(0, (int(deadline_us) - now) // 1_000_000),
                })
            return {
                "cell": c,
                "title": v.title,
                "theater": (v.geography or {}).get("theater", ""),
                "start_epoch_utc": v.start_epoch_utc,
                "estimated_duration_min": v.estimated_duration_min,
                "red_doctrine_profile": ctx.red_doctrine_profile,
                "learning_objectives": list(v.learning_objectives),
                "text": text,             # situation/mission/etc — from the YAML intro_brief.{cell}
                "objectives": objs_out,   # enriched with desc + deadline
                "roe": dict(ctx.roe),     # {kinetic_authorized, cyber_authorized}
                "now": now,
            }

        if cell == "white":
            return {"now": now, "blue": _cell_brief("blue"), "red": _cell_brief("red")}
        return _cell_brief(cell)

    # -- maneuver mode computation (read-only) ---------------------------------
    def compute_maneuver(self, session: str, cell: str, actor: str,
                         mode: str, params: dict) -> dict:
        self.catch_up(session)
        mgr = self._sessions[session]
        asset = mgr.world.assets.get(actor)
        if asset is None:
            return {"error": f"asset {actor!r} not found"}
        if asset.orbit is None:
            return {"error": f"asset {actor!r} has no orbit (ground asset?)"}
        from spacesim.engine.maneuver import compute_maneuver as _cm
        try:
            return _cm(asset.orbit, mode, params, mgr.world.now, mgr.osys.prop)
        except (ValueError, Exception) as exc:
            return {"error": str(exc)}

    def cell_activity(self, session: str, cell: str,
                       past_window_s: int = 1800,
                       future_window_s: int = 7200) -> dict:
        """Cell activity Gantt feed: past + present + scheduled activity for one cell.

        Cell scope (fog-of-war):
          - cell == "white": activity from all three cells (blue + red + neutral) in
            separate lanes plus scheduled injects.
          - cell == "blue" / "red": only that cell's own orders + own active effects.

        Source data (engine-deterministic, read-only):
          - osys.orders.values()        — issued orders (past, queued, cancelled, rejected)
          - sim.scheduler.pending()     — future scheduled events (injects, deliveries)
          - world.active_effects        — currently-active effects (start/end)

        Returns:
            {
              now: int,                         # current sim time (µs UTC)
              t_start: int, t_end: int,         # display window
              cells: ["blue","red","neutral"],  # lanes present (single-cell views drop the others)
              activities: [
                { kind, cell, actor, action, target?, start, end, status, label }
              ]
            }
        kind: "order" | "inject" | "effect"
        status: "executed" | "queued" | "cancelled" | "rejected" | "active" | "scheduled"
        """
        self.catch_up(session)   # multiplayer: surface the live now in the Gantt
        mgr = self._sessions[session]
        now = mgr.world.now
        t_start = now - past_window_s * 1_000_000
        t_end = now + future_window_s * 1_000_000

        def _own_asset(actor_id: str, target_cell: str) -> bool:
            a = mgr.world.assets.get(actor_id) or mgr.world.sensors.get(actor_id)
            return a is not None and getattr(a, "owner", None) == target_cell

        activities: list[dict] = []

        # 1) Orders (past, queued, cancelled, rejected).
        from spacesim.engine.orders import BAR_DURATION_S
        for o in mgr.osys.orders.values():
            if cell != "white" and o.cell != cell:
                continue
            label = f"{o.actor} {o.action}" + (f" → {o.target}" if o.target else "")
            if o.earliest_window is not None:
                win_start, win_end = o.earliest_window
                # Clamp bar to a realistic action duration so the Gantt reflects how
                # long the actual uplink/collection/dump takes, not the whole pass.
                if o.action == "observe":
                    dur_us = int(float(o.params.get("duration_s", 300)) * 1_000_000)
                else:
                    dur_s = BAR_DURATION_S.get(o.action)
                    dur_us = dur_s * 1_000_000 if dur_s is not None else None
                if dur_us is not None:
                    bar_end = min(win_end, win_start + dur_us)
                else:
                    bar_end = win_end
                start, end = win_start, bar_end
            else:
                # Cyber / rejected orders: no window. Show as a marker around issued_at.
                start = o.issued_at or now
                end = start + 60_000_000   # 60 s nominal marker width
            # Skip bars completely outside the display window
            if end < t_start or start > t_end:
                continue
            status = o.status
            if status == "queued" and start <= now <= end:
                status = "active"   # the bar straddles now → currently executing
            activities.append({
                "kind": "order",
                "cell": o.cell,
                "actor": o.actor,
                "action": o.action,
                "target": o.target,
                "start": int(start),
                "end": int(end),
                "status": status,
                "label": label,
                "delivery_path": o.delivery_path,
            })

        # 2) Scheduled non-order events (injects).  Skip bus ticks and per-order execute_*
        #    events (already represented by their order above).
        order_tags = {o.id for o in mgr.osys.orders.values()}
        for ev in mgr.sim.scheduler.pending():
            if ev.kind != "inject":
                continue
            if ev.tag and ev.tag in order_tags:
                continue
            if ev.t < t_start or ev.t > t_end:
                continue
            ev_cell = ev.actor if ev.actor in ("blue", "red", "white", "neutral") else "white"
            if cell != "white" and ev_cell not in (cell, "white"):
                continue
            n_eff = len((ev.payload or {}).get("effects", []) or [])
            activities.append({
                "kind": "inject",
                "cell": ev_cell,
                "actor": "white-cell",
                "action": "inject",
                "target": None,
                "start": int(ev.t),
                "end": int(ev.t + 60_000_000),
                "status": "scheduled",
                "label": f"inject ({n_eff} effects)",
                "delivery_path": None,
            })

        # 3) Active effects — currently in progress on own assets (cell scope).
        for eff in mgr.world.active_effects:
            target_asset = mgr.world.assets.get(eff.target)
            target_owner = getattr(target_asset, "owner", None)
            if cell != "white" and target_owner != cell:
                continue
            if eff.end < t_start or eff.start > t_end:
                continue
            activities.append({
                "kind": "effect",
                "cell": target_owner or "neutral",
                "actor": eff.target,
                "action": eff.category or eff.template or "effect",
                "target": eff.target,
                "start": int(eff.start),
                "end": int(eff.end),
                "status": "active" if eff.start <= now <= eff.end else "scheduled",
                "label": f"{eff.template or eff.category} → {eff.target} ({eff.outcome})",
                "delivery_path": None,
            })

        # Sort by start time so the renderer can stack bars deterministically.
        activities.sort(key=lambda a: (a["cell"], a["start"], a["actor"]))

        cells = ["blue", "red", "neutral"] if cell == "white" else [cell]
        return {"now": now, "t_start": t_start, "t_end": t_end,
                "cells": cells, "activities": activities}

    def preview_consequence(self, session: str, cell: str, action: str, target: str,
                              params: dict) -> dict:
        """Estimate the political-cost / escalation risk of an action *before* commit.

        Returns:
            severity        — "low" | "medium" | "high"
            escalation_w    — numeric escalation weight (0..10)
            reversible      — whether the effect can be rolled back
            debris_risk     — "none" | "low" | "high"
            attribution     — default attribution disposition (overt/ambiguous/covert)
            civilian_risk   — boolean (denying a civilian link raises cost)
            notes           — list of short human strings for the UI to display
        """
        self.catch_up(session)
        mgr = self._sessions[session]
        params = params or {}
        # Defaults
        escalation = int(params.get("escalation_weight", {
            "jam": 3, "engage": 8, "observe": 1, "downlink": 0, "cyber": 4,
            "command": 1, "maneuver": 1,
        }.get(action, 1)))
        reversible = action not in ("engage",)
        debris_risk = "high" if action == "engage" else "none"
        attribution = {
            "engage": "overt", "jam": "ambiguous", "cyber": "covert",
            "observe": "ambiguous", "downlink": "ambiguous",
            "command": "covert", "maneuver": "overt",
        }.get(action, "ambiguous")
        notes: list[str] = []
        # Civilian risk
        target_asset = mgr.world.assets.get(target or "")
        civilian = bool(target_asset and getattr(target_asset, "civilian", False))
        if civilian:
            notes.append("Target is a civilian asset — denial raises political cost.")
        # Cyber-specific overrides
        if action == "cyber":
            from spacesim.engine.cyber import payload_params, vector_params
            vp, _ = vector_params(params.get("vector"))
            pp, _ = payload_params(params.get("payload"))
            escalation = int(params.get("escalation_weight", pp["escalation_weight"]))
            reversible = pp["reversible"]
            attribution = vp["attribution_bias"]
            if pp["intended_outcome"] == "destroy":
                notes.append("Wiper payload is irreversible — destruction of state.")
        # Jam-specific overrides
        if action == "jam":
            from spacesim.engine.jam import modulation_params
            mp, _ = modulation_params(params.get("modulation"))
            attribution = mp["attribution_bias"]
            if attribution == "overt":
                notes.append("Deceptive jam is highly attributable.")
        if escalation >= 7 or debris_risk == "high":
            severity = "high"
        elif escalation >= 4:
            severity = "medium"
        else:
            severity = "low"
        if civilian and severity == "low":
            severity = "medium"
        return {
            "action": action, "target": target,
            "severity": severity,
            "escalation_w": escalation,
            "reversible": reversible,
            "debris_risk": debris_risk,
            "attribution": attribution,
            "civilian_risk": civilian,
            "notes": notes,
        }

    def coaching_notes(self, session: str, cell: str) -> list[dict]:
        """Return the coaching notes from the loaded vignette that are due-now and visible to cell.

        A note is visible when its target cell matches the requesting cell (or is "white" /
        unspecified, in which case all cells see it) AND its at_sim_t is null OR is ≤ world.now.
        """
        self.catch_up(session)
        mgr = self._sessions[session]
        v = getattr(mgr, "vignette", None)
        if v is None:
            return []
        notes = list(getattr(v, "coaching", []) or [])
        now = mgr.world.now
        out: list[dict] = []
        for n in notes:
            target_cell = n.get("cell") or "white"
            if target_cell not in ("white", cell):
                continue
            at = n.get("at_sim_t")
            if at is not None and int(at) > now:
                continue
            out.append(n)
        return out

    def compute_engage(self, session: str, cell: str, actor: str, target: str,
                        params: dict) -> dict:
        """Preview a kinetic engage order: closing geometry + Pₖ + debris cone (read-only)."""
        self.catch_up(session)
        from spacesim.engine.engage import (
            closing_geometry, debris_cone_estimate, kill_probability,
        )
        import numpy as np
        mgr = self._sessions[session]
        a = mgr.world.assets.get(actor)
        b = mgr.world.assets.get(target)
        if a is None or b is None:
            return {"error": "actor or target not found"}
        if a.orbit is None or b.orbit is None:
            return {"error": "engage preview requires both actor and target in orbit"}
        ra, va = mgr.osys.prop.rv(a.orbit, mgr.world.now)
        rb, vb = mgr.osys.prop.rv(b.orbit, mgr.world.now)
        geom = closing_geometry(np.asarray(ra), np.asarray(va),
                                 np.asarray(rb), np.asarray(vb))
        base_pk = float(params.get("success_prob", 0.9))
        salvo_n = int(params.get("salvo_n", 1))
        interceptor_dv = float(params.get("interceptor_dv_ms", 200.0))
        pk = kill_probability(base_pk, miss_km=geom["miss_km"],
                              interceptor_dv_ms=interceptor_dv, salvo_n=salvo_n)
        debris = debris_cone_estimate(geom["miss_km"], geom["closing_speed_kms"])
        return {
            "actor": actor, "target": target,
            **geom,
            "salvo_n": salvo_n,
            "interceptor_dv_ms": interceptor_dv,
            "kill_probability": pk,
            "debris": debris,
        }

    def compute_cyber(self, session: str, cell: str, actor: str, target: str,
                       params: dict) -> dict:
        """Preview a cyber order: success prob × detect prob × attribution + payload effect."""
        self.catch_up(session)
        from spacesim.engine.cyber import (
            attribution_score, effective_success, payload_params, vector_params,
        )
        mgr = self._sessions[session]
        b = mgr.world.assets.get(target)
        target_posture = b.cyber_posture if b else "medium"
        vector = params.get("vector")
        payload_name = params.get("payload")
        dwell_s = float(params.get("dwell_s", 0.0))
        persistence_h = float(params.get("persistence_h", 1.0))
        vp, vname = vector_params(vector)
        pp, pname = payload_params(payload_name)
        succ = effective_success(vector, target_posture, dwell_s)
        attr = attribution_score(vector, dwell_s, persistence_h)
        return {
            "vector": vname, "payload": pname,
            "target_posture": target_posture,
            "success_prob": round(succ, 3),
            "detect_prob": attr["detect_prob"],
            "attribution_default": attr["attribution_bias"],
            "reversible": pp["reversible"],
            "escalation_weight": pp["escalation_weight"],
            "intended_outcome": pp["intended_outcome"],
            "patchable": vp["patchable"],
            "min_persistence_h": vp["min_persistence_h"],
        }

    def compute_sigint(self, session: str, cell: str, actor: str, params: dict) -> dict:
        """Preview a SIGINT collection: expected geolocation accuracy + power draw."""
        self.catch_up(session)
        from spacesim.engine.sigint import (
            band_params, geolocation_error_km, mode_params, soc_drain,
        )
        mgr = self._sessions[session]
        a = mgr.world.assets.get(actor)
        if a is None:
            return {"error": f"asset {actor!r} not found"}
        band = params.get("band", "L")
        mode = params.get("intercept_mode", "track")
        dwell_s = float(params.get("dwell_s", mode_params(mode)[0]["dwell_s_default"]))
        n_collectors = int(params.get("n_collectors", 1))
        bp, bname = band_params(band)
        mp, mname = mode_params(mode)
        err = geolocation_error_km(band, mode, dwell_s, n_collectors)
        drain = soc_drain(mode, dwell_s)
        return {
            "band": bname, "intercept_mode": mname,
            "dwell_s": dwell_s,
            "n_collectors": n_collectors,
            "geolocation_error_km": err,
            "soc_drain": round(drain, 4),
            "freq_ghz": bp["freq_ghz"],
            "atmos_loss_db": bp["atmos_loss_db"],
            "power_factor": mp["power_factor"],
        }

    def compute_jam(self, session: str, cell: str, actor: str, params: dict) -> dict:
        """Preview a jam order's effective radius, success probability, and footprint.

        Read-only: no state mutation.  Returns:
            {modulation, power_w, effective_radius_km, footprint_polygon,
             success_prob, detectability, power_draw_w, attribution_default}
        """
        self.catch_up(session)
        from spacesim.engine.jam import (
            effective_radius_km, effective_success_prob, jam_footprint_polygon,
            modulation_params, power_draw_w,
        )
        from spacesim.engine.geometry import eci_to_ecef, ecef_to_geodetic

        mgr = self._sessions[session]
        asset = mgr.world.assets.get(actor)
        if asset is None:
            return {"error": f"asset {actor!r} not found"}
        modulation = params.get("modulation", "barrage")
        power_w = float(params.get("power_w", 100.0))
        bandwidth_hz = float(params.get("bandwidth_hz", 1e6))
        victim_bw_hz = float(params.get("victim_bandwidth_hz", 1e6))
        base_prob = float(params.get("success_prob", 0.9))

        mp, resolved = modulation_params(modulation)
        radius_km = effective_radius_km(power_w, modulation)
        adj_prob = effective_success_prob(base_prob, modulation, bandwidth_hz, victim_bw_hz)

        # Footprint at the jammer's ground position (if it has one) or its sub-satellite point.
        if asset.location is not None:
            lat, lon = asset.location.lat_deg, asset.location.lon_deg
        elif asset.orbit is not None:
            r, _ = mgr.osys.prop.rv(asset.orbit, mgr.world.now)
            g = ecef_to_geodetic(eci_to_ecef(r, mgr.world.now))
            lat, lon = g.lat_deg, g.lon_deg
        else:
            lat, lon = 0.0, 0.0
        footprint = jam_footprint_polygon(lat, lon, radius_km)

        return {
            "modulation": resolved,
            "power_w": round(power_w, 1),
            "effective_radius_km": round(radius_km, 2),
            "footprint_polygon": footprint,
            "success_prob": round(adj_prob, 3),
            "detectability": mp["detectability"],
            "power_draw_w": round(power_draw_w(power_w, modulation), 1),
            "attribution_default": mp["attribution_bias"],
            "center": {"lat_deg": round(lat, 4), "lon_deg": round(lon, 4)},
        }

    # -- after-action review ---------------------------------------------------
    def aar_report(self, session: str):
        self.catch_up(session)
        return aar.report(self._sessions[session])

    def aar_objectives_at(self, session: str, seq=None) -> dict:
        return aar.objectives_at(self._sessions[session], seq)

    def aar_snapshot_at(self, session: str, seq=None) -> dict:
        return aar.snapshot_at(self._sessions[session], seq)

    def alarms(self, session: str, cell: str) -> list:
        self.catch_up(session)
        return self._sessions[session].alarms(cell)

    # -- save / resume ---------------------------------------------------------
    def save(self, session: str) -> dict:
        # Snapshot under lock so an in-flight mutation can't tear the state.
        with self._locked(session) as mgr:
            mgr._catch_up_locked()
            return mgr.save_state()

    def load_save(self, state: dict) -> str:
        self._counter += 1
        sid = f"sess-{self._counter}"
        self._sessions[sid] = SessionManager.from_state(state)
        return sid
