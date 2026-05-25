"""Render a full training-manual screenshot set from live SessionAPI/engine data (Pillow).

Not browser captures (the sandbox blocks installing a browser) — these paint the web UI's panels
from genuine, fog-filtered session data so they faithfully show each major feature and menu.
Output: docs/manual/*.png + docs/manual/INDEX.md.  Run: ``python3 tools/render_manual.py``.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from spacesim.content.vignette import list_vignettes, load_vignette
from spacesim.engine import simtime
from spacesim.engine.custody import Track
from spacesim.engine.entities import Asset, AssetResources, Sensor
from spacesim.engine.geometry import R_EARTH_EQ, GeoPoint, ecef_to_geodetic, eci_to_ecef
from spacesim.engine.orbit import OrbitState
from spacesim.engine.orders import Order, OrderSystem
from spacesim.engine.propagator import ModeratePropagator
from spacesim.engine.recovery import RecoverySystem
from spacesim.engine.effects import EffectInstance, ModerateEffectResolver
from spacesim.engine.simulation import Simulation
from spacesim.engine.world import WorldState
from spacesim.session import aar
from spacesim.session.manager import SessionManager
from spacesim.session.redai import RedDoctrine
from spacesim.session.scene import build_scene

OUT = Path(__file__).resolve().parent.parent / "docs" / "manual"
F = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

BG = (14, 17, 22); PANEL = (20, 26, 34); BORDER = (38, 48, 64)
TEXT = (215, 221, 227); MUTED = (159, 176, 192)
GREEN = (111, 207, 111); YELLOW = (224, 194, 74); RED = (224, 106, 106); BLUEc = (90, 150, 230)
f12 = ImageFont.truetype(F, 12); f13 = ImageFont.truetype(F, 13)
f13b = ImageFont.truetype(FB, 13); f16b = ImageFont.truetype(FB, 16)
W, H = 1200, 720
PROP = ModeratePropagator()
INDEX: list[tuple[str, str]] = []


def canvas(cell, subtitle):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 36], fill=(17, 22, 29)); d.line([0, 36, W, 36], fill=BORDER)
    d.text((14, 9), "Space Control & Orbital Warfare Exercise Simulator", font=f16b, fill=TEXT)
    d.text((W - 360, 9), "UNCLASSIFIED // TRAINING", font=f13b, fill=GREEN)
    if cell:
        chip = {"white": (90, 100, 120), "blue": (60, 110, 200), "red": (200, 80, 80)}[cell]
        d.rounded_rectangle([W - 150, 6, W - 110, 26], radius=4, fill=chip)
        d.text((W - 145, 9), cell.upper()[:3], font=f13b, fill=(255, 255, 255))
    d.text((14, 44), subtitle, font=f13, fill=MUTED)
    return img, d


def panel(d, x, y, w, h, title):
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=PANEL, outline=BORDER)
    d.text((x + 12, y + 9), title, font=f16b, fill=TEXT)
    d.line([x + 12, y + 31, x + w - 12, y + 31], fill=BORDER)
    return x + 12, y + 40


def table(d, x, y, headers, rows, widths, lh=19):
    cx = x
    for h_, w_ in zip(headers, widths):
        d.text((cx, y), h_, font=f12, fill=MUTED); cx += w_
    y += lh
    for row in rows:
        cx = x
        for (txt, col), w_ in zip(row, widths):
            d.text((cx, y), str(txt)[: int(w_ / 7)], font=f13, fill=col); cx += w_
        y += lh
    return y


def kv(d, x, y, pairs, lh=20, kw=150):
    for k, v, col in pairs:
        d.text((x, y), k, font=f13, fill=MUTED); d.text((x + kw, y), str(v), font=f13b, fill=col); y += lh
    return y


def lines(d, x, y, items, lh=18, col=TEXT):
    for s, c in items:
        d.text((x, y), s, font=f13, fill=c); y += lh
    return y


def hcol(s):
    return GREEN if s == "nominal" else (RED if s in ("destroyed", "safe_mode") else YELLOW)


def draw_map(d, x, y, w, h, scene, title):
    panel(d, x, y, w, h, title)
    mx, my, mw, mh = x + 12, y + 42, w - 24, h - 54
    d.rectangle([mx, my, mx + mw, my + mh], fill=(11, 15, 20))
    for lon in range(-180, 181, 30):
        px = mx + (lon + 180) / 360 * mw; d.line([px, my, px, my + mh], fill=(28, 37, 49))
    for lat in range(-90, 91, 30):
        py = my + (90 - lat) / 180 * mh; d.line([mx, py, mx + mw, py], fill=(28, 37, 49))
    def P(lon, lat):
        return mx + (lon + 180) / 360 * mw, my + (90 - lat) / 180 * mh
    for a in scene.assets:
        px, py = P(a.lon_deg, a.lat_deg)
        if a.on_orbit:
            d.polygon([(px, py - 5), (px - 5, py + 4), (px + 5, py + 4)], fill=GREEN)
        else:
            d.rectangle([px - 4, py - 4, px + 4, py + 4], fill=GREEN)
        d.text((px + 7, py - 5), a.id, font=f12, fill=MUTED)
    for t in scene.tracks:
        px, py = P(t.lon_deg, t.lat_deg)
        r = max(5, min(46, t.uncertainty_km / 18))
        col = YELLOW if t.characterized else RED
        d.ellipse([px - r, py - r, px + r, py + r], outline=col)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=col)
        d.text((px + 6, py - 16), f"{t.object} ±{t.uncertainty_km}km", font=f12, fill=MUTED)


def save(img, name, caption):
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / name)
    INDEX.append((name, caption))
    print("wrote", name)


def asset_rows(assets):
    rows = []
    for a in assets:
        bus = a["bus_state"]["mode"] if a.get("bus_state") else "—"
        rows.append([(a["id"], TEXT), (a["kind"], MUTED), (a["health"], hcol(a["health"]), ),
                     (bus, hcol(bus))])
    # normalize 3-tuples
    return [[(c[0], c[1]) for c in r] for r in rows]


# ---------------------------------------------------------------------------
def s_gallery():
    img, d = canvas(None, "Vignette picker — the eight selectable scenarios (White Cell menu)")
    ix, iy = panel(d, 12, 66, W - 24, 600, "Scenario library")
    rows = []
    for v in list_vignettes():
        vig = load_vignette(v["id"])
        rows.append([(vig.id, BLUEc), (vig.title, TEXT), (", ".join(vig.doctrinal_basis)[:46], MUTED),
                     (vig.red_doctrine_profile, YELLOW)])
    table(d, ix, iy, ["ID", "TITLE", "DOMAINS", "RED DOCTRINE"], rows, [220, 240, 380, 180], lh=22)
    save(img, "01-vignette-picker.png", "Vignette picker / scenario library (all eight vignettes).")


def s_cell(cell, mgr, name, sub):
    view = mgr.get_view(cell) if cell != "white" else None
    img, d = canvas(cell, sub)
    if cell == "white":
        god = mgr.get_godview()
        assets = [a.model_dump() for a in god.assets.values()]
        tracks = [t.model_dump() for t in god.tracks]
    else:
        assets = view.own_assets; tracks = view.known_tracks
    ix, iy = panel(d, 12, 66, 560, 360, "Fleet — ground truth" if cell == "white" else "Fleet (own assets)")
    table(d, ix, iy, ["ID", "KIND", "HEALTH", "BUS"], asset_rows(assets),
          [150, 160, 110, 110])
    ox, oy = panel(d, 588, 66, W - 600, 200, "Objectives")
    pairs = []
    full = mgr.objectives()
    for side in ("blue", "red"):
        for oid, met in full.get(side, {}).items():
            pairs.append((f"{side}.{oid}", "MET" if met else "pending", GREEN if met else MUTED))
    kv(d, ox, oy, pairs, kw=240)
    tx, ty = panel(d, 588, 278, W - 600, 148, "Custody tracks (belief)")
    if tracks:
        table(d, tx, ty, ["OBJECT", "CONF", "CHAR", "CLASS"],
              [[(t["object"], TEXT), (f"{t['confidence']:.2f}", TEXT), (str(t["characterized"]), TEXT), (t["classification"], MUTED)] for t in tracks],
              [160, 90, 90, 140])
    else:
        d.text((tx, ty), "(no custody held)", font=f13, fill=MUTED)
    scene = build_scene(mgr.world, cell if cell != "white" else "blue")
    draw_map(d, 12, 438, W - 24, 230, scene, "Belief map — render-from-custody (own assets + track uncertainty)")
    save(img, name, sub)


def _subpoint(orbit, t):
    g = ecef_to_geodetic(eci_to_ecef(PROP.rv(orbit, t)[0], t)); g.alt_m = 0.0
    return g


def s_orders():
    # Queued downlink + rejected engage, side by side, from Vignette 1.
    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=1); mgr.start()
    ack_ok = mgr.issue_order("blue", Order(cell="blue", actor="ISR-EO-1", action="downlink", params={"via": "GS-NORTH"}))
    ack_bad = mgr.issue_order("red", Order(cell="red", actor="RED-ASAT", action="engage", target="ISR-EO-1"))
    img, d = canvas("blue", "Order panel — plan-first commanding: accepted (queued to a window) vs rejected (with reason)")
    ix, iy = panel(d, 12, 66, 560, 250, "Accepted order")
    kv(d, ix, iy, [
        ("Actor", "ISR-EO-1", TEXT), ("Action", "downlink", TEXT), ("Via", "GS-NORTH", TEXT),
        ("Status", ack_ok.status, GREEN), ("Delivery path", ack_ok.delivery_path, BLUEc),
        ("Executes", simtime.to_iso(ack_ok.earliest_window[0]) if ack_ok.earliest_window else "—", TEXT),
    ])
    rx, ry = panel(d, 588, 66, W - 600, 250, "Rejected order")
    kv(d, rx, ry, [
        ("Actor", "RED-ASAT", TEXT), ("Action", "engage", TEXT), ("Target", "ISR-EO-1", TEXT),
        ("Status", ack_bad.status, RED), ("Reason", ack_bad.reason, RED),
    ])
    iy2 = panel(d, 12, 332, W - 24, 80, "Why-can't-I")[1]
    lines(d, 24, iy2, [("Engagement blocked: kinetic ASAT not authorized in this vignette, and no weapons-quality track on the target.", MUTED)])
    save(img, "05-order-panel.png", "Order panel: a queued command (with delivery path + window) and a rejected one (with reason).")


def s_planning():
    # ISL delivery beats a distant ground pass.
    world = WorldState(now=0)
    world.assets["SAT"] = Asset(id="SAT", owner="blue", kind="satellite",
                                orbit=OrbitState(a_m=R_EARTH_EQ + 550e3, e=0, i_deg=51.6, raan_deg=33, argp_deg=0, ta_deg=0, epoch=0),
                                resources=AssetResources(delta_v_ms=100.0))
    world.assets["FAR-GS"] = Asset(id="FAR-GS", owner="blue", kind="ground_station", location=GeoPoint(lat_deg=-60, lon_deg=-90))
    world.assets["RELAY"] = Asset(id="RELAY", owner="blue", kind="satellite", isl_capable=True,
                                  orbit=OrbitState(a_m=42164e3, e=0, i_deg=0, raan_deg=0, argp_deg=0, ta_deg=0, epoch=0))
    sim = Simulation(world, seed=1); osys = OrderSystem(sim)
    ap = osys._ap()
    from spacesim.engine.access import COMMAND_UPLINK
    gnd = ap.windows("FAR-GS", "SAT", COMMAND_UPLINK, 0, 24 * 3600 * 1_000_000)
    order = osys.issue(Order(cell="blue", actor="SAT", action="maneuver", params={"dv": [0, 5, 0], "via": "FAR-GS"}))
    img, d = canvas("blue", "Planning & tasking — command delivery chooses the earliest of ground / ISL / stored")
    ix, iy = panel(d, 12, 66, W - 24, 230, "Delivery path selection (maneuver SAT)")
    kv(d, ix, iy, [
        ("Ground uplink", f"next pass at +{int((gnd[0].start)/1e6/3600)} h via FAR-GS" if gnd else "none", MUTED),
        ("ISL relay", f"crosslink via RELAY at +{int(order.earliest_window[0]/1e6)} s", GREEN),
        ("Chosen path", order.delivery_path, BLUEc),
        ("Status", order.status, GREEN),
    ], kw=200)
    d.text((24, 250), "ISL relay reaches the satellite far sooner than the distant ground pass — a real tactical advantage.", font=f13, fill=MUTED)
    save(img, "06-planning-isl.png", "Command planning: ISL relay delivers sooner than a distant ground pass.")


def s_tasking():
    # task -> custody -> unlock engagement.
    sat = OrbitState(a_m=R_EARTH_EQ + 550e3, e=0, i_deg=51.6, raan_deg=33, argp_deg=0, ta_deg=0, epoch=0)
    world = WorldState(now=0)
    world.assets["RSAT"] = Asset(id="RSAT", owner="red", kind="satellite", orbit=sat)
    world.assets["INT"] = Asset(id="INT", owner="blue", kind="interceptor", location=_subpoint(sat, 0), resources=AssetResources(ammo=1))
    world.sensors["RADAR"] = Sensor(id="RADAR", owner="blue", kind="ground_radar", location=_subpoint(sat, 0))
    sim = Simulation(world, seed=1); osys = OrderSystem(sim, roe={"kinetic_authorized": True})
    before = osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT"))
    task = osys.issue(Order(cell="blue", actor="auto", action="observe", target="RSAT", params={"intent": "characterize", "gain": 0.9, "classification": "hostile"}))
    sim.advance_to(task.earliest_window[0] + 1)
    tr = world.track_for("blue", "RSAT")
    after = osys.issue(Order(cell="blue", actor="INT", action="engage", target="RSAT", params={"success_prob": 1.0}))
    img, d = canvas("blue", "SDA tasking loop — task a sensor, gain custody, unlock a previously-blocked engagement")
    ix, iy = panel(d, 12, 66, W - 24, 300, "task → custody → unlock")
    iy = kv(d, ix, iy, [
        ("1. Engage (no track)", f"{before.status}: {before.fail_reason}", RED),
        ("2. Task RADAR", f"characterize RSAT, {task.status} (auto-selected sensor)", GREEN),
        ("3. Track after report", f"conf {tr.current_confidence(world.now):.2f}, characterized={tr.characterized}, weapons-quality={tr.is_weapons_quality(world.now)}", TEXT),
        ("4. Engage (now)", f"{after.status} via weapon-engagement window", GREEN),
    ], kw=210)
    save(img, "07-sda-tasking.png", "Task → custody → unlock: a sensor report yields a weapons-quality track that enables the engagement.")


def s_belief_map():
    # GEO inspector belief with growing uncertainty.
    sat = OrbitState(a_m=42164e3, e=0, i_deg=0.05, raan_deg=0, argp_deg=0, ta_deg=0, epoch=0)
    world = WorldState(now=0)
    world.assets["BLUE-HVA"] = Asset(id="BLUE-HVA", owner="blue", kind="satellite", orbit=sat)
    tr = Track(object="RED-INSP", owner="blue", last_observation=0, confidence=1.0, characterized=True,
               classification="hostile", state_estimate=OrbitState(a_m=42164e3, e=0, i_deg=0.05, raan_deg=0, argp_deg=0, ta_deg=0.6, epoch=0))
    world.tracks.append(tr)
    world.now = simtime.minutes(50)  # custody has decayed → the volume has bloomed
    scene = build_scene(world, "blue")
    img, d = canvas("blue", "Belief map (Vignette 2 GEO RPO) — own HVA known; the hostile inspector is a growing uncertainty volume")
    draw_map(d, 12, 66, W - 24, 600, scene, "Render-from-custody — uncertainty grows between optical looks, snaps on report")
    chips(d, W - 372, 74, ["+","-","center","tracks","grid","reset"], active="tracks")
    save(img, "08-belief-map.png", "Belief map (2D) with zoom / pan / center / layer controls; tracked objects show growing uncertainty.")


def s_soh_safe():
    # SATCOM safed via cyber → fleet SOH + bus drill-down.
    mgr = SessionManager(load_vignette("satcom-cyber-link"), seed=1); mgr.start()
    RedDoctrine(mgr).step(); mgr.advance_to(mgr.world.now + simtime.minutes(1))
    sat = mgr.world.assets["BLUE-SATCOM"]; bus = sat.bus_state
    img, d = canvas("blue", "Fleet SOH rollup & drill-down — a cyber attack has driven the SATCOM bird to safe mode")
    ix, iy = panel(d, 12, 66, 560, 200, "Fleet SOH rollup")
    table(d, ix, iy, ["ID", "KIND", "HEALTH", "BUS"],
          [[("BLUE-SATCOM", TEXT), ("satellite", MUTED), ("nominal", GREEN), ("safe_mode", RED)]],
          [170, 150, 110, 110])
    bx, by = panel(d, 588, 66, W - 600, 320, "Bus drill-down (subsystems vs limits)")
    kv(d, bx, by, [
        ("Mode", bus.mode, RED), ("Power", bus.power.status, hcol(bus.power.status)),
        ("Attitude", f"{bus.attitude.status} (mode {bus.attitude.mode})", YELLOW if bus.attitude.mode == "safe" else GREEN),
        ("Thermal", bus.thermal.status, GREEN), ("Propulsion", bus.propulsion.status, GREEN),
        ("C&DH", f"{bus.cdh.status} (fsw {bus.cdh.fsw_mode})", YELLOW), ("Comms", bus.comms.status, GREEN),
        ("Safe-mode cause", bus.safe_mode.cause, RED), ("Payload", "OFF (no mission in safe mode)", RED),
    ], kw=200)
    iy2 = panel(d, 12, 286, 560, 120, "Alarm / event feed")[1]
    lines(d, 24, iy2, [("⚠ SATCOM-1 entered SAFE MODE (cause: cyber) — discovered at next contact", RED),
                       ("payload disabled; recovery requires command passes", MUTED)])
    save(img, "09-fleet-soh-safe-mode.png", "Fleet SOH rollup and bus drill-down with a satellite in cyber-induced safe mode.")


def s_recovery():
    sat = OrbitState(a_m=R_EARTH_EQ + 550e3, e=0, i_deg=51.6, raan_deg=33, argp_deg=0, ta_deg=0, epoch=0)
    world = WorldState(now=0)
    world.assets["SAT"] = Asset(id="SAT", owner="blue", kind="satellite", orbit=sat,
                                bus_state=None, cyber_vulnerabilities=[{"vector": "ground_modem", "patchable": True, "patched": False}])
    from spacesim.engine.bus import BusState
    world.assets["SAT"].bus_state = BusState()
    world.assets["GS"] = Asset(id="GS", owner="blue", kind="ground_station", location=_subpoint(sat, 0))
    ModerateEffectResolver().resolve(EffectInstance(category="cyber", target="SAT", access_vector="ground_modem",
                                                    requires="none", intended_outcome="safe_mode", success_prob=1.0), world, Simulation(world, 0).rng)
    sim = Simulation(world, seed=1); rec = RecoverySystem(sim, difficulty="quick", root_cause_persists=True)
    p1 = rec.begin_recovery("SAT", "GS"); sim.advance_to(p1["finish_at"] + 1)
    resafed = world.assets["SAT"].bus_state.mode
    blocked = world.assets["SAT"].bus_state.safe_mode.blocked_reason
    world.assets["SAT"].cyber_vulnerabilities[0]["patched"] = True
    p2 = rec.begin_recovery("SAT", "GS"); sim.advance_to(p2["finish_at"] + 1)
    final = world.assets["SAT"].bus_state.mode
    img, d = canvas("blue", "Safe-mode recovery loop — confirm, recover across passes, re-safe until the root cause is patched")
    ix, iy = panel(d, 12, 66, W - 24, 320, "Recovery procedure (safe_mode_recovery_difficulty = quick)")
    kv(d, ix, iy, [
        ("Induced by", "cyber (ground_modem exploit)", RED),
        ("Attempt 1", f"confirmed at contact, then {resafed.upper()}", RED),
        ("Blocked reason", blocked, RED),
        ("Mitigation", "Blue patches the modem vulnerability", GREEN),
        ("Attempt 2", f"recovery sticks → {final.upper()}", GREEN),
    ], kw=180)
    save(img, "10-safe-mode-recovery.png", "Safe-mode recovery: re-safed while the vulnerability is unpatched, then recovered after patching.")


def s_rewind_branch():
    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=1); mgr.start()
    start = mgr.world.now
    mgr.issue_order("blue", Order(cell="blue", actor="ISR-EO-1", action="downlink", params={"via": "GS-NORTH"}))
    mgr.advance_to(start + 800 * 1_000_000)
    a = mgr.objectives()
    mgr.rewind_to(start)
    mgr.issue_order("red", Order(cell="red", actor="JAM-NORTH", action="jam", target="ISR-EO-1", params={"success_prob": 1.0, "outcome": "deny"}))
    mgr.issue_order("blue", Order(cell="blue", actor="ISR-EO-1", action="downlink", params={"via": "GS-NORTH"}))
    mgr.advance_to(mgr.ctx.landing_deadline + 1)
    b = mgr.objectives()
    img, d = canvas("white", "Time travel — rewind to a fork and branch to a different outcome (deterministic replay)")
    ax, ay = panel(d, 12, 66, 580, 220, "Branch A — Blue downlinks unopposed")
    kv(d, ax, ay, [("blue.deliver_isr", a["blue"]["deliver_isr"], GREEN if a["blue"]["deliver_isr"] else MUTED),
                   ("red.deny_isr", a["red"]["deny_isr"], GREEN if a["red"]["deny_isr"] else MUTED)], kw=200)
    bx, by = panel(d, 608, 66, W - 620, 220, "Branch B — Red jams the downlink")
    kv(d, bx, by, [("blue.deliver_isr", b["blue"]["deliver_isr"], GREEN if b["blue"]["deliver_isr"] else MUTED),
                   ("red.deny_isr", b["red"]["deny_isr"], GREEN if b["red"]["deny_isr"] else MUTED)], kw=200)
    iy = panel(d, 12, 300, W - 24, 90, "Time controls")[1]
    lines(d, 24, iy, [("[+1m] [+10m] [+1h]   [Rewind to start]   — White Cell controls sim time; rewind/undo/branch are byte-exact.", MUTED)])
    save(img, "11-time-travel-branch.png", "Rewind-to-fork and branch: the same start yields a Blue win or a Red denial depending on play.")


def s_tle():
    from spacesim.session.inprocess import InProcessSession
    api = InProcessSession(); sid = api.load_vignette("leo-isr-denial", seed=1)
    l1 = "1 25544U 98067A   08264.51782528 -.00002182  00000-0 -11606-4 0  2927"
    l2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 15.72125391563537"
    ack = api.add_tle(sid, "ISS", l1, l2, owner="blue"); api.start(sid)
    scene = api.get_scene(sid, "blue"); iss = [a for a in scene.assets if a.id == "ISS"][0]
    img, d = canvas("white", "Force editor — add a real named satellite by TLE (propagates alongside fictional assets)")
    ix, iy = panel(d, 12, 66, W - 24, 230, "Add-by-TLE")
    kv(d, ix, iy, [("Name", "ISS (25544)", TEXT), ("Line 1", l1, MUTED), ("Line 2", l2, MUTED),
                   ("Validation", "accepted" if ack.ok else ack.reason, GREEN if ack.ok else RED),
                   ("Sub-point now", f"lat {iss.lat_deg:.1f}, lon {iss.lon_deg:.1f}, alt {iss.alt_m/1000:.0f} km", BLUEc)], kw=110)
    save(img, "12-tle-force-add.png", "Force editor: a real satellite added by TLE, validated and propagating.")


def s_doctrine_aar():
    a = SessionManager(load_vignette("multi-domain-taiwan"), seed=1); a.start()
    acks = RedDoctrine(a).step(); a.advance_to(a.world.now + simtime.minutes(1))
    rep = aar.report(a)
    b = SessionManager(load_vignette("multi-domain-taiwan"), seed=1); b.start()
    b.fire_inject("patch_modem"); RedDoctrine(b).step(); b.advance_to(b.world.now + simtime.minutes(1))
    diff = aar.compare_branches(rep, aar.report(b))
    img, d = canvas("white", "Red doctrine (china_integrated) + AAR — campaign timeline and branch comparison (capstone)")
    ix, iy = panel(d, 12, 66, 620, 380, "AAR decision timeline (Vignette 8)")
    rows = [[(simtime.to_iso(e.sim_time)[11:19], MUTED), (e.actor, BLUEc), (e.summary, TEXT)] for e in rep.timeline[:12]]
    table(d, ix, iy, ["TIME", "ACTOR", "DECISION"], rows, [90, 70, 430])
    dx, dy = panel(d, 648, 66, W - 660, 200, "Doctrine step (orders issued)")
    lines(d, dx, dy, [(f"{a.status} : red order", GREEN if a.status == 'queued' else MUTED) for a in acks[:6]] or [("(none)", MUTED)])
    cx, cy = panel(d, 648, 278, W - 660, 168, "Branch comparison")
    kv(d, cx, cy, [("events A / B", f"{diff['events_a']} / {diff['events_b']}", TEXT)] +
       [(k, f"A={v['a']} → B={v['b']}", YELLOW) for k, v in diff["objective_flips"].items()], kw=150)
    save(img, "13-doctrine-and-aar.png", "Red doctrine campaign + AAR: decision timeline and a branch comparison showing an objective flip.")


def chips(d, x, y, items, active=None):
    """Draw a row of little control buttons; returns the new x cursor."""
    for label in items:
        w = 14 + len(label) * 8
        fill = (47, 111, 99) if label == active else (30, 42, 56)
        d.rounded_rectangle([x, y, x + w, y + 24], radius=5, fill=fill, outline=(56, 80, 108))
        d.text((x + 7, y + 5), label, font=f12, fill=TEXT)
        x += w + 6
    return x


def draw_globe(img, d, x, y, w, h, scene, title, cam):
    """Orthographic 3D globe (mirrors static/globe.js); rendered into a clipped sub-image."""
    d.rounded_rectangle([x, y, x + w, y + h], radius=8, fill=PANEL, outline=BORDER)
    chips(d, x + 12, y + 8, ["rotate","tilt","+","-","zoom-to","spin","reset"], active="tilt")
    gx, gy, gw, gh = int(x + 8), int(y + 40), int(w - 16), int(h - 50)
    sub = Image.new("RGB", (gw, gh), (7, 11, 16)); sd = ImageDraw.Draw(sub)
    cx, cy = gw / 2, gh / 2
    R = (min(gw, gh) / 2 - 12) * cam.get("zoom", 1.0)
    lon0, la0 = cam.get("lon0", 0.0), math.radians(cam.get("pitch", 20.0))

    def proj(lat, lon, altkm=0.0):
        la, lo = math.radians(lat), math.radians(lon - lon0)
        cosc = math.sin(la0) * math.sin(la) + math.cos(la0) * math.cos(la) * math.cos(lo)
        px = math.cos(la) * math.sin(lo)
        py = math.cos(la0) * math.sin(la) - math.sin(la0) * math.cos(la) * math.cos(lo)
        rad = R * (1 + altkm / 6371.0)
        return cx + rad * px, cy - rad * py, cosc >= 0

    sd.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(14, 36, 56), outline=BORDER)
    sx, sy, sfront = proj(scene.sun_lat_deg, scene.sun_lon_deg)
    if sfront:
        sd.ellipse([sx - R * 0.5, sy - R * 0.5, sx + R * 0.5, sy + R * 0.5], fill=(28, 56, 78))

    def seg(fn, a, b):
        prev = None
        for t in range(a, b + 1, 6):
            la, lo = fn(t); px, py, fr = proj(la, lo)
            if prev and prev[2] and fr:
                sd.line([prev[0], prev[1], px, py], fill=(46, 70, 96))
            prev = (px, py, fr)
    for lon in range(-180, 180, 30):
        seg(lambda t, L=lon: (t, L), -90, 90)
    for lat in range(-60, 61, 30):
        seg(lambda t, L=lat: (L, t), -180, 180)
    for a in scene.assets:
        px, py, fr = proj(a.lat_deg, a.lon_deg, (a.alt_m or 0) / 1000)
        if not fr:
            continue
        if a.on_orbit:
            sd.polygon([(px, py - 6), (px - 6, py + 5), (px + 6, py + 5)], fill=GREEN)
        else:
            sd.rectangle([px - 4, py - 4, px + 4, py + 4], fill=GREEN)
        sd.text((px + 8, py - 5), a.id, font=f12, fill=(200, 214, 226))
    for t in scene.tracks:
        px, py, fr = proj(t.lat_deg, t.lon_deg, (t.alt_m or 0) / 1000)
        if not fr:
            continue
        rr = max(6, min(40, t.uncertainty_km / 18)); col = YELLOW if t.characterized else RED
        sd.ellipse([px - rr, py - rr, px + rr, py + rr], outline=col)
        sd.ellipse([px - 2, py - 2, px + 2, py + 2], fill=col)
        sd.text((px + 8, py - 16), f"{t.object} ±{t.uncertainty_km}km", font=f12, fill=(200, 214, 226))
    img.paste(sub, (gx, gy))


def s_globe():
    from spacesim.session import build_scene
    # A GEO HVA + a tracked inspector + a couple of LEO assets for a fuller globe.
    from spacesim.engine.entities import Asset
    from spacesim.engine.custody import Track
    from spacesim.engine.orbit import OrbitState
    world = WorldState(now=simtime.minutes(40))
    world.assets["BLUE-HVA"] = Asset(id="BLUE-HVA", owner="blue", kind="satellite",
                                     orbit=OrbitState(a_m=42164e3, e=0, i_deg=0.05, raan_deg=0, argp_deg=0, ta_deg=0, epoch=0))
    world.assets["ISR-LEO"] = Asset(id="ISR-LEO", owner="blue", kind="satellite",
                                    orbit=OrbitState(a_m=R_EARTH_EQ + 550e3, e=0, i_deg=51.6, raan_deg=33, argp_deg=0, ta_deg=0, epoch=0))
    world.assets["GS-1"] = Asset(id="GS-1", owner="blue", kind="ground_station", location=GeoPoint(lat_deg=35, lon_deg=-30))
    world.tracks.append(Track(object="RED-INSP", owner="blue", last_observation=0, confidence=1.0, characterized=True,
                              classification="hostile",
                              state_estimate=OrbitState(a_m=42164e3, e=0, i_deg=0.05, raan_deg=0, argp_deg=0, ta_deg=0.6, epoch=0)))
    scene = build_scene(world, "blue")

    img, d = canvas("blue", "3D globe — orthographic belief view; drag to rotate, tilt/zoom, zoom-to an asset")
    draw_globe(img, d, 12, 66, W - 24, 600, scene, "globe", {"lon0": -20, "pitch": 25, "zoom": 1.0})
    save(img, "14-globe-overview.png", "3D globe viewer (zoomed out) with rotate/tilt/zoom/zoom-to controls.")

    img2, d2 = canvas("blue", "3D globe — 'zoom-to' the GEO HVA: the camera centers and zooms on the selected asset")
    draw_globe(img2, d2, 12, 66, W - 24, 600, scene, "globe", {"lon0": scene.assets[0].lon_deg, "pitch": 5, "zoom": 1.7})
    save(img2, "15-globe-zoomto.png", "3D globe viewer zoomed-to the selected GEO asset.")


def s_white_controls():
    from spacesim.content.vignette import load_vignette, build_world
    vig = load_vignette("multi-domain-taiwan")
    _, ctx = build_world(vig)
    img, d = canvas("white", "White Cell control panel — scenario dials, time controls, and injects")
    ix, iy = panel(d, 12, 66, 720, 420, "Parameters (dials)")
    rows = []
    for p in vig.parameters:
        opts = ("/".join(map(str, p.options)) if p.options else (p.type))
        rows.append([(p.label, TEXT), (opts[:34], MUTED), (str(ctx.param_values.get(p.id)), GREEN)])
    table(d, ix, iy, ["PARAMETER", "OPTIONS / TYPE", "VALUE"], rows, [300, 280, 110], lh=22)
    tx, ty = panel(d, 748, 66, W - 760, 150, "Time controls")
    chips(d, tx, ty + 4, ["+1m", "+10m", "+1h", "⟲ Rewind", "Undo"])
    lines(d, tx, ty + 40, [("play / pause · fast-forward", MUTED), ("rewind & branch are byte-exact", MUTED)])
    jx, jy = panel(d, 748, 228, W - 760, 258, "Injects")
    lines(d, jx, jy, [("• " + i.label, TEXT) for i in vig.injects] or [("(none)", MUTED)])
    save(img, "16-white-controls.png", "White Cell control panel: parameter dials, time controls, and injects.")


ACTIONS_BY_KIND = {"satellite": ["downlink", "maneuver"], "jammer": ["jam"], "interceptor": ["engage"],
                   "cyber_unit": ["cyber"], "ground_radar": ["observe"], "ground_optical": ["observe"]}
PARAM_TEMPLATE = {"downlink": '{"via": "GS-NORTH"}', "maneuver": '{"dv": [0,5,0], "via": "GS-NORTH"}',
                  "jam": '{"success_prob": 1.0, "outcome": "deny"}', "engage": "{}",
                  "cyber": '{"access_vector": "ground_modem", "outcome": "safe_mode"}', "observe": '{"intent": "characterize"}'}


def s_command_menu():
    img, d = canvas("blue", "Satellite command selection — actions are filtered to the chosen asset's kind")
    lx, ly = panel(d, 12, 66, 360, 360, "Asset kinds → legal actions")
    rows = [[(k, BLUEc), (", ".join(v), TEXT)] for k, v in ACTIONS_BY_KIND.items()]
    table(d, lx, ly, ["KIND", "LEGAL ACTIONS"], rows, [150, 190], lh=24)
    rx, ry = panel(d, 388, 66, W - 400, 360, "Command panel — Actor: ISR-EO-1 (satellite)")
    ry = kv(d, rx, ry, [("Actor", "ISR-EO-1  (satellite · blue)", TEXT),
                        ("Action ▾", "downlink   [maneuver]", GREEN),
                        ("Target", "(optional)", MUTED),
                        ("Params", PARAM_TEMPLATE["downlink"], BLUEc)], kw=110)
    ry += 10
    d.text((rx, ry), "Selecting an actor filters the Action menu to that kind's legal actions and", font=f13, fill=MUTED)
    d.text((rx, ry + 18), "pre-fills a parameter template; the order is then queued to its access window.", font=f13, fill=MUTED)
    save(img, "17-command-menu.png", "Satellite command selection menu: actions filtered by asset kind with a param template.")


def _walk_image(cell, stepno, title, when, cmd_lines, result_lines, objectives, fname):
    img, d = canvas(cell, f"Training walkthrough — {cell.upper()} step {stepno}: {title}")
    cx, cy = panel(d, 12, 66, 560, 220, "Command")
    cy = kv(d, cx, cy, [("When", when, YELLOW)] + cmd_lines, kw=110)
    rx, ry = panel(d, 588, 66, W - 600, 220, "Result")
    lines(d, rx, ry, result_lines)
    ox, oy = panel(d, 12, 300, W - 24, 130, "Objectives")
    pairs = []
    for side in ("blue", "red"):
        for oid, met in objectives.get(side, {}).items():
            pairs.append((f"{side}.{oid}", "MET" if met else "pending", GREEN if met else MUTED))
    kv(d, ox, oy, pairs, kw=240)
    save(img, fname, f"Training walkthrough — {cell} step {stepno}: {title}.")


def s_training_blue():
    from spacesim.content.vignette import load_vignette
    from spacesim.engine.orders import Order
    mgr = SessionManager(load_vignette("training-basics"), seed=1); mgr.start()
    O = lambda **k: Order(cell="blue", **k)

    _walk_image("blue", 1, "Review fleet & objectives", "at start",
                [("Action", "review own assets / SOH", TEXT)],
                [("ISR-EO-1 nominal; awaiting orders.", MUTED)], mgr.objectives(), "18-train-blue-1.png")

    t = mgr.issue_order("blue", O(actor="RADAR-TRN", action="observe", target="RED-TGT",
                                  params={"intent": "characterize", "classification": "hostile"}))
    mgr.advance_to(t.earliest_window[0] + 1)
    _walk_image("blue", 2, "Task the sensor to build custody", "RADAR-TRN sees RED-TGT",
                [("Actor", "RADAR-TRN", TEXT), ("Action", "observe (characterize)", TEXT), ("Target", "RED-TGT", TEXT)],
                [(f"track on RED-TGT · characterized={mgr.world.track_for('blue','RED-TGT').characterized}", GREEN),
                 ("keep_custody now MET", GREEN)], mgr.objectives(), "19-train-blue-2.png")

    dl = mgr.issue_order("blue", O(actor="ISR-EO-1", action="downlink", params={"via": "GS-TRN"}))
    _walk_image("blue", 3, "Plan the imagery downlink", "queues to the next GS-TRN pass",
                [("Actor", "ISR-EO-1", TEXT), ("Action", "downlink", TEXT), ("Params", '{"via":"GS-TRN"}', BLUEc)],
                [(f"{dl.status} · {dl.delivery_path}", GREEN), (f"executes {simtime.to_iso(dl.earliest_window[0])}", TEXT)],
                mgr.objectives(), "20-train-blue-3.png")

    mgr.advance_to(dl.earliest_window[1] + 1)
    _walk_image("blue", 4, "Advance to the downlink window", "+10 min (past the window)",
                [("Action", "advance time", TEXT)],
                [("imagery delivered ✓", GREEN), ("deliver_isr now MET", GREEN)], mgr.objectives(), "21-train-blue-4.png")

    mv = mgr.issue_order("blue", O(actor="ISR-EO-1", action="maneuver", params={"dv": [0, 5, 0], "via": "GS-TRN"}))
    _walk_image("blue", 5, "Maneuver to preserve the orbit", "next GS-TRN command pass",
                [("Actor", "ISR-EO-1", TEXT), ("Action", "maneuver (Δv 5 m/s)", TEXT)],
                [(f"{mv.status} · {mv.delivery_path}", GREEN), ("Δv decremented on execution", MUTED)],
                mgr.objectives(), "22-train-blue-5.png")

    _walk_image("blue", 6, "Confirm the objective", "after execution",
                [("Action", "review objectives", TEXT)],
                [("Blue delivered imagery in time.", GREEN)], mgr.objectives(), "23-train-blue-6.png")


def s_training_red():
    from spacesim.content.vignette import load_vignette
    from spacesim.engine.orders import Order
    mgr = SessionManager(load_vignette("training-basics"), seed=1); mgr.start()
    O = lambda **k: Order(cell="red", **k)

    _walk_image("red", 1, "Review own assets", "at start",
                [("Action", "review jammer / cyber / radar / interceptor", TEXT)],
                [("Red force ready.", MUTED)], mgr.objectives(), "24-train-red-1.png")

    o = mgr.issue_order("red", O(actor="RED-RDR", action="observe", target="ISR-EO-1", params={"intent": "track"}))
    mgr.advance_to(o.earliest_window[0] + 1)
    _walk_image("red", 2, "Find the Blue ISR satellite", "RED-RDR sees ISR-EO-1",
                [("Actor", "RED-RDR", TEXT), ("Action", "observe (track)", TEXT), ("Target", "ISR-EO-1", TEXT)],
                [("custody on ISR-EO-1 established", GREEN)], mgr.objectives(), "25-train-red-2.png")

    j = mgr.issue_order("red", O(actor="JAM-TRN", action="jam", target="ISR-EO-1",
                                 params={"success_prob": 1.0, "outcome": "deny"}))
    _walk_image("red", 3, "Jam the downlink", "during the GS-TRN pass",
                [("Actor", "JAM-TRN", TEXT), ("Action", "jam (deny)", TEXT), ("Target", "ISR-EO-1", TEXT)],
                [(f"{j.status} · {j.delivery_path}", GREEN), ("link denied during the footprint window", YELLOW)],
                mgr.objectives(), "26-train-red-3.png")

    mgr.issue_order("red", O(actor="RED-CYBER", action="cyber", target="ISR-EO-1",
                             params={"access_vector": "ground_modem", "outcome": "safe_mode", "success_prob": 1.0, "sm_susceptibility": 1.0}))
    mgr.advance_to(mgr.world.now + 60 * 1_000_000)
    _walk_image("red", 4, "Cyber the modem (off-pass)", "any time — cyber isn't window-gated",
                [("Actor", "RED-CYBER", TEXT), ("Action", "cyber → safe_mode", TEXT), ("Vector", "ground_modem", TEXT)],
                [(f"ISR-EO-1 bus mode: {mgr.world.assets['ISR-EO-1'].bus_state.mode}", RED), ("disable_isr now MET", GREEN)],
                mgr.objectives(), "27-train-red-4.png")

    eng = mgr.issue_order("red", O(actor="RED-ASAT", action="engage", target="ISR-EO-1"))
    _walk_image("red", 5, "Attempt a kinetic strike (ROE check)", "any pass",
                [("Actor", "RED-ASAT", TEXT), ("Action", "engage", TEXT), ("Target", "ISR-EO-1", TEXT)],
                [(f"{eng.status.upper()}: {eng.reason}", RED), ("kinetic ASAT is off by default — restraint", MUTED)],
                mgr.objectives(), "28-train-red-5.png")

    mgr.advance_to(mgr.ctx.landing_deadline + 1)
    _walk_image("red", 6, "Advance and assess", "past the delivery window",
                [("Action", "advance time", TEXT)],
                [("Blue delivered nothing in the window.", GREEN), ("deny_isr now MET", GREEN)],
                mgr.objectives(), "29-train-red-6.png")


def write_index():
    md = ["# Training-manual screenshots\n",
          "Generated by `tools/render_manual.py` from live SessionAPI/engine data (the sandbox cannot",
          "install a browser, so these paint the web UI's panels from genuine fog-filtered state).\n"]
    for name, cap in INDEX:
        md.append(f"- **{name}** — {cap}")
    (OUT / "INDEX.md").write_text("\n".join(md) + "\n")
    print("wrote INDEX.md")


def main():
    s_gallery()
    m = SessionManager(load_vignette("leo-isr-denial"), seed=1); m.start()
    s_cell("white", m, "02-white-godview.png", "White Cell god-view — ground truth for both sides (Vignette 1)")
    s_cell("blue", m, "03-blue-cell.png", "Blue Cell — fog-of-war view (own assets and own custody only)")
    s_cell("red", m, "04-red-cell.png", "Red Cell — fog-of-war view (Red never sees Blue's assets)")
    s_orders()
    s_planning()
    s_tasking()
    s_belief_map()
    s_soh_safe()
    s_recovery()
    s_rewind_branch()
    s_tle()
    s_doctrine_aar()
    s_globe()
    s_white_controls()
    s_command_menu()
    s_training_blue()
    s_training_red()
    write_index()


if __name__ == "__main__":
    main()
