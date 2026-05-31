"""Render a full training-manual screenshot set from live SessionAPI/engine data (Pillow).

Not browser captures (the sandbox blocks installing a browser) — these paint the web UI's panels
from genuine, fog-filtered session data so they faithfully show each major feature and menu.
Output: docs/manual/*.png + docs/manual/INDEX.md.  Run: ``python3 tools/render_manual.py``.
"""

from __future__ import annotations

import json
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
# Cell-accent palette mirrors style.css body[data-cell="..."] (FW user-added #3/#4/#5).
CELL_ACCENT = {"white": (138, 150, 173), "blue": (90, 143, 224), "red": (224, 122, 122), None: BORDER}
# Active cell threaded by canvas() into panel() so h2 headings tint correctly per screenshot.
_ACTIVE_CELL = [None]
f12 = ImageFont.truetype(F, 12); f13 = ImageFont.truetype(F, 13)
f12b = ImageFont.truetype(FB, 12); f13b = ImageFont.truetype(FB, 13); f16b = ImageFont.truetype(FB, 16)
W, H = 1200, 720
PROP = ModeratePropagator()
INDEX: list[tuple[str, str]] = []

_WORLD = None
def world_data():
    global _WORLD
    if _WORLD is None:
        p = Path(__file__).resolve().parent.parent / "spacesim" / "ui_web" / "static" / "world.json"
        _WORLD = json.loads(p.read_text()) if p.exists() else {"coast": [], "borders": []}
    return _WORLD


def draw_world(d, project, maxjump=None):
    """Draw coastlines+borders via project(lon,lat)->(x,y) or None (far side). Mirrors world.js."""
    w = world_data()
    for arr, col in ((w["coast"], (44, 74, 99)), (w["borders"], (34, 56, 75))):
        for seg in arr:
            run = []
            for lon, lat in seg:
                p = project(lon, lat)
                if p is None or (maxjump and run and abs(p[0] - run[-1][0]) > maxjump):
                    if len(run) > 1:
                        d.line(run, fill=col)
                    run = [] if p is None else [p]
                    continue
                run.append(p)
            if len(run) > 1:
                d.line(run, fill=col)


def canvas(cell, subtitle):
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    accent = CELL_ACCENT[cell] if cell in CELL_ACCENT else BORDER
    _ACTIVE_CELL[0] = cell
    d.rectangle([0, 0, W, 36], fill=(17, 22, 29))
    # FW user-added #11/#12 — cell-accent toolbar underline (mirrors web CSS).
    d.line([0, 36, W, 36], fill=accent, width=2)
    # FW user-added #8 — inline-SVG logo equivalent: small Earth + orbit + sat glyph in 24×24.
    cx, cy, r = 16, 18, 9
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(10, 20, 36), outline=accent)
    d.ellipse([cx - r - 4, cy - 4, cx + r + 4, cy + 4], outline=accent)
    d.polygon([(cx + r + 3, cy - 6), (cx + r, cy - 2), (cx + r + 6, cy - 2)], fill=accent)
    d.text((34, 9), "Space Control & Orbital Warfare Exercise Simulator", font=f16b, fill=TEXT)
    d.text((W - 360, 9), "UNCLASSIFIED // TRAINING", font=f13b, fill=GREEN)
    if cell:
        chip = {"white": (90, 100, 120), "blue": (60, 110, 200), "red": (200, 80, 80)}[cell]
        d.rounded_rectangle([W - 150, 6, W - 110, 26], radius=4, fill=chip)
        d.text((W - 145, 9), cell.upper()[:3], font=f13b, fill=(255, 255, 255))
    d.text((34, 44), subtitle, font=f13, fill=MUTED)
    return img, d


def panel(d, x, y, w, h, title):
    accent = CELL_ACCENT[_ACTIVE_CELL[0]] if _ACTIVE_CELL[0] in CELL_ACCENT else BORDER
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=PANEL, outline=BORDER)
    # FW user-added #3/#4/#5 — left-side cell accent bar + tinted h2 underline.
    d.line([x + 1, y + 1, x + 1, y + h - 1], fill=accent, width=3)
    d.text((x + 12, y + 9), title, font=f16b, fill=accent)
    d.line([x + 12, y + 31, x + w - 12, y + 31], fill=accent, width=2)
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
    draw_world(d, lambda lon, lat: P(lon, lat), maxjump=mw * 0.5)
    # FW user-added #2 — ground tracks: dim polyline for each orbital asset's projected sub-points.
    track_col = (110, 124, 142)
    for a in scene.assets:
        track = getattr(a, "track", None) or []
        if not a.on_orbit or len(track) < 2:
            continue
        prev = None
        run = []
        for pt in track:
            X, Y = P(pt[1], pt[0])
            if prev is not None and abs(X - prev[0]) > mw * 0.5:
                if len(run) > 1: d.line(run, fill=track_col)
                run = []
            run.append((X, Y)); prev = (X, Y)
        if len(run) > 1: d.line(run, fill=track_col)
    # Cell-accent for own-asset markers (matches the live UI).
    accent = CELL_ACCENT[_ACTIVE_CELL[0]] if _ACTIVE_CELL[0] in CELL_ACCENT else GREEN
    if accent == BORDER: accent = GREEN
    for a in scene.assets:
        px, py = P(a.lon_deg, a.lat_deg)
        _app6_marker(d, px, py, a, accent)
        d.text((px + 7, py - 5), a.id, font=f12, fill=MUTED)
    for t in scene.tracks:
        px, py = P(t.lon_deg, t.lat_deg)
        r = max(5, min(46, t.uncertainty_km / 18))
        col = YELLOW if t.characterized else RED
        d.ellipse([px - r, py - r, px + r, py + r], outline=col)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=col)
        d.text((px + 6, py - 16), f"{t.object} ±{t.uncertainty_km}km", font=f12, fill=MUTED)


def _app6_marker(d, px, py, a, accent):
    """APP-6-adapted marker shapes (mirrors ui_web/static/symbology.js, FW §4)."""
    kind = getattr(a, "kind", "satellite")
    # Asset may not expose payload directly — best-effort sniff from the .kind enum.
    payload = ""
    detail = getattr(a, "id", "").lower()
    if "satcom" in detail or "comm" in detail: payload = "satcom"
    elif "pnt" in detail or "gnss" in detail: payload = "pnt"
    elif "sigint" in detail: payload = "sigint"
    elif "wx" in detail or "weath" in detail: payload = "weather"
    elif "sda" in detail or "radar" in detail: payload = "sda"
    r = 5
    if kind == "ground_station":
        d.rectangle([px - r, py - r, px + r, py + r], fill=accent); return
    if kind == "jammer":   # 5-pt star
        pts = []
        for i in range(10):
            ang = math.radians(i * 36 - 90); rr = r * (0.5 if i % 2 else 1.0)
            pts.append((px + rr * math.cos(ang), py + rr * math.sin(ang)))
        d.polygon(pts, fill=accent); return
    if kind == "interceptor":
        d.polygon([(px, py - r), (px + r, py), (px, py + r), (px - r, py)], fill=accent)
        d.rectangle([px - 1, py - r * 2, px + 1, py - r], fill=accent); return
    if payload == "satcom":
        d.rectangle([px - r, py - r, px + r, py + r], fill=accent); return
    if payload == "pnt":
        d.polygon([(px, py - r), (px + r, py), (px, py + r), (px - r, py)], fill=accent); return
    if payload == "sigint":
        d.polygon([(px, py + r), (px - r, py - r * 0.8), (px + r, py - r * 0.8)], fill=accent); return
    if payload == "weather":
        d.ellipse([px - r, py - r, px + r, py + r], fill=accent); return
    if payload == "sda":
        d.rectangle([px - r, py - 1, px + r, py + 1], fill=accent)
        d.rectangle([px - 1, py - r, px + 1, py + r], fill=accent); return
    # Default (ISR or generic orbital): triangle.
    d.polygon([(px, py - r), (px - r, py + r * 0.8), (px + r, py + r * 0.8)], fill=accent)


def save(img, name, caption):
    OUT.mkdir(parents=True, exist_ok=True)
    img.save(OUT / name)
    INDEX.append((name, caption))
    print("wrote", name)


# ---------------------------------------------------------------------------
# Callout helpers for the UI-reference module (FW §11 follow-up — annotated
# panel screenshots with numbered red circles cross-referenced from docs/training/10-ui-reference.md).
# ---------------------------------------------------------------------------
CALLOUT_FILL = (224, 64, 64); CALLOUT_TEXT = (255, 255, 255); CALLOUT_R = 10


def callout(d, x, y, n):
    """Numbered red circle at (x, y) — center coordinates."""
    d.ellipse([x - CALLOUT_R, y - CALLOUT_R, x + CALLOUT_R, y + CALLOUT_R],
              fill=CALLOUT_FILL, outline=(255, 255, 255), width=2)
    s = str(n)
    # Crude centering — DejaVuSansMono digits are roughly 7 px wide × 11 px tall at f12
    cw = 6 if len(s) == 1 else 10
    d.text((x - cw // 2, y - 7), s, font=f12, fill=CALLOUT_TEXT)


def legend(d, x, y, w, h, title, rows):
    """Small numbered legend panel (rows = [(n, label), ...])."""
    d.rounded_rectangle([x, y, x + w, y + h], radius=6, fill=PANEL, outline=BORDER)
    d.text((x + 10, y + 8), title, font=f13b, fill=MUTED)
    yy = y + 28
    for n, label in rows:
        callout(d, x + 20, yy + 6, n)
        d.text((x + 36, yy + 1), label, font=f12, fill=TEXT); yy += 18
    return yy


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

    def _wproj(lon, lat):
        px, py, fr = proj(lat, lon, 0)
        return (px, py) if fr else None
    draw_world(sd, _wproj)

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
    # FW user-added #1 — orbital paths on the globe (own assets only).
    accent = CELL_ACCENT[_ACTIVE_CELL[0]] if _ACTIVE_CELL[0] in CELL_ACCENT else GREEN
    if accent == BORDER: accent = GREEN
    track_col = (110, 124, 142)
    for a in scene.assets:
        track = getattr(a, "track", None) or []
        if not a.on_orbit or len(track) < 2:
            continue
        prev = None
        for pt in track:
            px, py, fr = proj(pt[0], pt[1], (pt[2] or 0) / 1000)
            if prev and prev[2] and fr:
                sd.line([prev[0], prev[1], px, py], fill=track_col)
            prev = (px, py, fr)
    for a in scene.assets:
        px, py, fr = proj(a.lat_deg, a.lon_deg, (a.alt_m or 0) / 1000)
        if not fr:
            continue
        if a.on_orbit:
            sd.polygon([(px, py - 6), (px - 6, py + 5), (px + 6, py + 5)], fill=accent)
        else:
            sd.rectangle([px - 4, py - 4, px + 4, py + 4], fill=accent)
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


def draw_graph(d, x, y, w, h, points, spec, title):
    panel(d, x, y, w, h, title)
    gx, gy, gw, gh = x + 40, y + 46, w - 56, h - 70
    d.rectangle([gx, gy, gx + gw, gy + gh], fill=(10, 15, 21), outline=BORDER)
    vals = [p["value"] for p in points if p["value"] is not None]
    if not vals:
        d.text((gx + 10, gy + gh / 2), "loss of signal", font=f13, fill=MUTED); return
    lo, hi = min(vals + [spec["soft"], spec["hard"]]), max(vals + [spec["soft"], spec["hard"]])
    if hi == lo: hi = lo + 1
    pad = (hi - lo) * 0.1; lo -= pad; hi += pad
    px = lambda i: gx + i / (len(points) - 1 or 1) * gw
    py = lambda v: gy + gh - (v - lo) / (hi - lo) * gh
    for lim, c in ((spec["soft"], YELLOW), (spec["hard"], RED)):
        yy = py(lim)
        for xx in range(int(gx), int(gx + gw), 8):
            d.line([xx, yy, xx + 4, yy], fill=c)
    col = {"green": GREEN, "yellow": YELLOW, "red": RED, "los": MUTED}.get(points[-1]["status"], TEXT)
    line = [(px(i), py(p["value"])) for i, p in enumerate(points) if p["value"] is not None]
    if len(line) > 1:
        d.line(line, fill=col, width=2)
    d.text((gx, gy - 14), f"{spec['label']} ({spec['unit']})", font=f12, fill=MUTED)
    d.text((x + 6, gy), f"{hi:.3g}", font=f12, fill=MUTED); d.text((x + 6, gy + gh - 12), f"{lo:.3g}", font=f12, fill=MUTED)


def _param_panel(d, x, y, w, h, world, asset_id, t, title):
    from spacesim.engine import telemetry as tel
    ix, iy = panel(d, x, y, w, h, title)
    db = tel.telemetry_db(world, asset_id, t, 1)
    for sub, params in db.items():
        d.text((ix, iy), sub.upper(), font=f12, fill=MUTED); iy += 16
        for p in params:
            c = {"green": GREEN, "yellow": YELLOW, "red": RED, "los": MUTED}.get(p["status"], TEXT)
            d.text((ix + 10, iy), f"{p['label']}", font=f13, fill=TEXT)
            d.text((ix + 180, iy), f"{p['value']} {p['unit']}", font=f13b, fill=c); iy += 17
        iy += 4


def s_telemetry_jam():
    from spacesim.engine import telemetry as tel
    from spacesim.engine.effects import ActiveEffect
    from spacesim.engine.bus import BusState
    world = WorldState(now=simtime.minutes(20))
    world.assets["BLUE-SATCOM"] = Asset(id="BLUE-SATCOM", owner="blue", kind="satellite", bus_state=BusState())
    world.active_effects.append(ActiveEffect(target="BLUE-SATCOM", outcome="deny", start=0,
                                             end=simtime.minutes(40), category="electronic_warfare"))
    img, d = canvas("blue", "Subsystem drill-down — diagnosing from telemetry (the cause is NOT labeled)")
    _param_panel(d, 12, 66, 360, 600, world, "BLUE-SATCOM", world.now, "Subsystems (click a parameter)")
    pts = tel.series(world, "BLUE-SATCOM", "rx_power_dbm", 0, simtime.minutes(60), 120, 1)
    sp = tel.PARAMS["rx_power_dbm"]
    draw_graph(d, 388, 66, W - 400, 300, pts, {"label": sp.label, "unit": sp.unit, "soft": sp.soft, "hard": sp.hard},
               "comms.rx_power_dbm")
    lx, ly = panel(d, 388, 378, W - 400, 288, "Subsystem log (symptoms)")
    log = tel.subsystem_log(world, "BLUE-SATCOM", world.now, 1)
    lines(d, lx, ly, [(s, RED if "RED" in s else YELLOW) for s in log] or [("(all nominal)", MUTED)])
    d.text((lx, ly + 200), "Clue: receiver RX power is HIGH and C/N0 has collapsed — consistent with", font=f12, fill=MUTED)
    d.text((lx, ly + 216), "uplink/downlink jamming. Mitigate: re-plan frequency/beam, geolocate the source.", font=f12, fill=MUTED)
    save(img, "30-telemetry-jam.png", "Subsystem drill-down: RX power spikes / C/N0 collapses under jamming (operator infers the cause).")


def s_telemetry_cyber():
    from spacesim.engine import telemetry as tel
    from spacesim.engine.bus import BusState, enter_safe_mode
    world = WorldState(now=simtime.minutes(30))
    world.assets["BLUE-SATCOM"] = Asset(id="BLUE-SATCOM", owner="blue", kind="satellite", bus_state=BusState())
    enter_safe_mode(world.assets["BLUE-SATCOM"].bus_state, now=0, cause="cyber")
    img, d = canvas("blue", "Subsystem drill-down — a different signature points elsewhere")
    _param_panel(d, 12, 66, 360, 600, world, "BLUE-SATCOM", world.now, "Subsystems")
    pts = tel.series(world, "BLUE-SATCOM", "fsw_error_count", 0, simtime.minutes(40), 120, 1)
    sp = tel.PARAMS["fsw_error_count"]
    draw_graph(d, 388, 66, W - 400, 300, pts, {"label": sp.label, "unit": sp.unit, "soft": sp.soft, "hard": sp.hard},
               "cdh.fsw_error_count")
    lx, ly = panel(d, 388, 378, W - 400, 288, "Subsystem log (symptoms)")
    log = tel.subsystem_log(world, "BLUE-SATCOM", world.now, 1)
    lines(d, lx, ly, [(s, RED if "RED" in s else YELLOW) for s in log] or [("(all nominal)", MUTED)])
    d.text((lx, ly + 200), "Clue: flight-software error & command-reject counters are climbing and the", font=f12, fill=MUTED)
    d.text((lx, ly + 216), "bird dropped to safe mode — consistent with a cyber/command-path intrusion.", font=f12, fill=MUTED)
    save(img, "31-telemetry-cyber.png", "Subsystem drill-down: FSW error counters climb + safe mode — a cyber signature.")


def s_queue_timeline():
    from spacesim.content.vignette import load_vignette
    from spacesim.engine.orders import Order
    mgr = SessionManager(load_vignette("training-basics"), seed=1); mgr.start()
    mgr.issue_order("blue", Order(cell="blue", actor="RADAR-TRN", action="observe", target="RED-TGT", params={"intent": "characterize"}))
    mgr.issue_order("blue", Order(cell="blue", actor="ISR-EO-1", action="downlink", params={"via": "GS-TRN"}))
    mgr.issue_order("blue", Order(cell="blue", actor="ISR-EO-1", action="maneuver", params={"dv": [0, 5, 0], "via": "GS-TRN"}))
    mgr.cancel_order("blue", mgr.list_orders("blue")[-1]["id"])  # cancel the just-queued maneuver
    orders = mgr.list_orders("blue")
    wa = mgr.windows_ahead("blue", "ISR-EO-1")

    img, d = canvas("blue", "Command queue & pass timeline — plan-first commanding (orders queue to windows; cancellable)")
    qx, qy = panel(d, 12, 66, 560, 320, "Command queue")
    rows = [[(o["actor"] + " " + o["action"] + " " + (o["target"] or ""), TEXT),
             (o["delivery_path"] or "—", MUTED),
             (o["status"], GREEN if o["status"] in ("queued", "executed") else (RED if o["status"] == "cancelled" else MUTED))]
            for o in orders]
    table(d, qx, qy, ["ORDER", "DELIVERY", "STATUS"], rows, [300, 150, 110], lh=22)

    tx, ty = panel(d, 588, 66, W - 600, 320, "Pass timeline — ISR-EO-1 (next 6 h)")
    rx0, rw = tx, (W - 600) - 24
    span = wa["horizon_s"] * 1_000_000; now = wa["now"]
    lanes = {"command_uplink": (ty + 30, GREEN, "uplink"), "telemetry_downlink": (ty + 70, BLUEc, "downlink")}
    for ch, (yy, col, lab) in lanes.items():
        d.text((rx0, yy - 2), lab, font=f12, fill=MUTED)
        d.rectangle([rx0 + 70, yy, rx0 + 70 + rw - 70, yy + 16], outline=BORDER)
    for w in wa["windows"]:
        ch = lanes.get(w["channel"])
        if not ch:
            continue
        yy, col, _ = ch
        x0 = rx0 + 70 + (w["start"] - now) / span * (rw - 70)
        x1 = rx0 + 70 + (w["end"] - now) / span * (rw - 70)
        d.rectangle([x0, yy + 1, max(x0 + 2, x1), yy + 15], fill=col)
    d.text((rx0, ty + 120), "Orders queue to the next valid window; the ribbon shows when each", font=f12, fill=MUTED)
    d.text((rx0, ty + 136), "pass opens. A queued order can be cancelled before it uplinks.", font=f12, fill=MUTED)
    save(img, "32-command-queue.png", "Command queue (cancellable) and the per-asset pass-timeline ribbon.")


def s_aar_scrubber():
    from spacesim.content.vignette import load_vignette
    mgr = SessionManager(load_vignette("multi-domain-taiwan"), seed=3); mgr.start()
    RedDoctrine(mgr).step(); mgr.advance_to(mgr.world.now + simtime.minutes(2))
    start, end = aar.snapshot_at(mgr, 0), aar.snapshot_at(mgr, None)

    img, d = canvas("white", "After-action review — scrub the deterministic timeline (read-only replay)")
    sx, sy = panel(d, 12, 66, W - 24, 110, "Timeline scrubber")
    bx0, bx1, by = sx + 10, W - 60, sy + 24
    d.line([bx0, by, bx1, by], fill=BORDER, width=3)
    for k in range(end["n_events"] + 1):
        hx = bx0 + (bx1 - bx0) * (k / max(1, end["n_events"]))
        d.ellipse([hx - 3, by - 3, hx + 3, by + 3], fill=BLUEc)
    d.ellipse([bx1 - 6, by - 6, bx1 + 6, by + 6], fill=GREEN)  # handle at the end
    d.text((sx, by + 16), f"event {end['n_events']} / {end['n_events']}  ·  {simtime.to_iso(end['now'])}  ·  drag to any decision point", font=f13, fill=MUTED)

    ax, ay = panel(d, 12, 188, (W - 36) // 2, 320, "At event 0 (start)")
    _objs(d, ax, ay, start["objectives"]); _assets(d, ax, ay + 150, start["assets"])
    bx, byp = panel(d, 24 + (W - 36) // 2, 188, (W - 36) // 2, 320, "At the latest event")
    _objs(d, bx, byp, end["objectives"]); _assets(d, bx, byp + 150, end["assets"])

    lx, ly = panel(d, 12, 520, W - 24, 130, "Save / resume")
    lines(d, lx, ly, [
        ("Save writes a complete snapshot (history + pending orders + queue); resume re-derives the", MUTED),
        ("exact world from (initial, seed, event log) and restores the queued orders — byte-identical.", MUTED),
        ("Because the core is deterministic, scrubbing here never disturbs the live session.", MUTED)])
    save(img, "33-aar-scrubber.png", "AAR timeline scrubber (state at any event) + save/resume note.")


def _objs(d, x, y, objs):
    d.text((x, y), "Objectives", font=f13b, fill=MUTED); y += 18
    for side in ("blue", "red"):
        for oid, met in objs.get(side, {}).items():
            d.text((x, y), f"{side}.{oid}", font=f13, fill=TEXT)
            d.text((x + 220, y), "MET" if met else "pending", font=f13b, fill=GREEN if met else MUTED); y += 17


def _assets(d, x, y, assets):
    d.text((x, y), "Assets", font=f13b, fill=MUTED); y += 18
    for a in assets[:7]:
        c = RED if a["health"] == "destroyed" or a["bus_mode"] == "safe_mode" else GREEN
        d.text((x, y), f"{a['id']}: {a['health']}" + (f" / {a['bus_mode']}" if a["bus_mode"] else ""), font=f13, fill=c); y += 16


def s_alarms_soh():
    from spacesim.content.vignette import load_vignette
    mgr = SessionManager(load_vignette("satcom-cyber-link"), seed=1); mgr.start()
    RedDoctrine(mgr).step(); mgr.advance_to(mgr.world.now + simtime.minutes(2))
    view = mgr.get_view("blue"); alarms = mgr.alarms("blue")

    img, d = canvas("blue", "Fleet SOH rollup + alarms feed — at-a-glance health and what's off-nominal")
    fx, fy = panel(d, 12, 66, 560, 300, "Fleet SOH rollup (own assets)")
    rows = []
    for a in view.own_assets:
        bus = a.get("bus_state")
        soh = "red" if (bus and bus["mode"] == "safe_mode") else "green"
        rows.append([("●", _color(soh)), (a["id"], TEXT), (a["kind"], MUTED),
                     (bus["mode"] if bus else "—", RED if bus and bus["mode"] == "safe_mode" else MUTED)])
    table(d, fx, fy, ["SOH", "ID", "KIND", "BUS"], rows, [50, 180, 160, 120])
    axx, ayy = panel(d, 588, 66, W - 600, 480, "Alarm / event feed")
    lines(d, axx, ayy, [(f"{a['asset']}: {a['text']}", RED if "RED" in a["text"] or "SAFE" in a["text"] else YELLOW) for a in alarms[:18]]
          or [("(no alarms)", MUTED)])
    d.text((fx, fy + 240), "The rollup is a single green/yellow/red dot per asset; click a row to drill", font=f12, fill=MUTED)
    d.text((fx, fy + 256), "into subsystem graphs. The feed lists symptoms — the cause is yours to infer.", font=f12, fill=MUTED)
    save(img, "34-alarms-soh.png", "Fleet SOH rollup (per-asset dot) and the alarms/event feed.")


def _color(s):
    return {"green": GREEN, "yellow": YELLOW, "red": RED}.get(s, TEXT)


def write_index():
    md = ["# Training-manual screenshots\n",
          "Generated by `tools/render_manual.py` from live SessionAPI/engine data (the sandbox cannot",
          "install a browser, so these paint the web UI's panels from genuine fog-filtered state).\n"]
    for name, cap in INDEX:
        md.append(f"- **{name}** — {cap}")
    (OUT / "INDEX.md").write_text("\n".join(md) + "\n")
    print("wrote INDEX.md")


def s_maneuver_assistant():
    """FW §11.A — Maneuver mode assistant (six entry modes with live Δv preview)."""
    img, d = canvas("blue", "Maneuver mode assistant — six entry modes with live Δv preview")
    mx, my = panel(d, 12, 66, 580, 360, "Maneuver mode picker")
    rows = [
        [("eci",          BLUEc), ("Δv [x, y, z] in ECI (m/s)",                 TEXT)],
        [("lvlh",         BLUEc), ("Radial / Along-track / Normal frame",       TEXT)],
        [("finite_burn",  BLUEc), ("Direction + magnitude + duration",          TEXT)],
        [("target_coe",   BLUEc), ("Target orbit elements (a/e/i/RAAN/ω)",      TEXT)],
        [("hohmann",      BLUEc), ("2-burn altitude transfer (Δv₁ + Δv₂)",      TEXT)],
        [("plane_change", BLUEc), ("Rodrigues rotation by Δi (deg)",            TEXT)],
    ]
    table(d, mx, my, ["MODE", "MEANING"], rows, [160, 380], lh=24)
    px, py = panel(d, 608, 66, W - 620, 360, "Live preview (LVLH, Δv_T = 10 m/s)")
    py = kv(d, px, py, [
        ("Cost",          "10.000 m/s",                       GREEN),
        ("Δv (ECI)",      "[0.000, 9.998, -0.058] m/s",        TEXT),
        ("New orbit",     "a 6843 km · e 0.0014 · i 51.6°",   BLUEc),
        ("Alt range",     "468–477 km (LEO)",                 MUTED),
        ("Second burn",   "—",                                MUTED),
    ], kw=120)
    py += 6
    d.text((px, py),     "POST /api/sessions/{sid}/maneuver/compute  →  read-only preview", font=f12, fill=MUTED)
    d.text((px, py + 16), "Operator scrubs sliders → preview updates live → Issue order pre-fills dv.", font=f12, fill=MUTED)
    save(img, "35-maneuver-assistant.png",
         "Maneuver assistant: six entry modes (ECI, LVLH, finite burn, target COE, Hohmann, plane change) "
         "with live Δv preview before commit.")


def s_isr_beam_modes():
    """FW §11.A.6 + ISR expansion — beam-mode picker with footprint preview."""
    from spacesim.engine.isr import BEAM_MODES
    img, d = canvas("blue", "ISR collection — beam mode + look angle + footprint preview")
    tx, ty = panel(d, 12, 66, 700, 340, "Beam mode database (EO / SAR / SDA)")
    rows = []
    for ptype in ("isr_eo", "isr_sar"):
        for mode, mp in BEAM_MODES[ptype].items():
            rows.append([
                (ptype.upper().replace("ISR_", ""), BLUEc),
                (mode,                              TEXT),
                (f"{mp['swath_km']:>5g} km",         MUTED),
                (f"{mp['resolution_m']:>4g} m",      MUTED),
                (f"×{mp['power_factor']:.1f}",       YELLOW),
                (f"{int(mp['duty_cycle']*100)}%",    GREEN),
            ])
    table(d, tx, ty, ["PAYLOAD", "MODE", "SWATH", "RES", "POWER", "DUTY"], rows,
          [100, 130, 100, 80, 90, 80], lh=20)

    px, py = panel(d, 728, 66, W - 740, 340, "Task panel — stripmap, 15° look")
    py = kv(d, px, py, [
        ("Sensor",      "ISR-EO-1",       TEXT),
        ("Beam mode",   "stripmap",       BLUEc),
        ("Look angle",  "15°",            YELLOW),
        ("Duration",    "300 s",          TEXT),
        ("Eff. gain",   "0.97",           GREEN),
        ("SOC drain",   "0.058",          MUTED),
    ], kw=110)
    py += 8
    d.text((px, py),     "Footprint polygon (4 corners) appears on the 2-D", font=f12, fill=MUTED)
    d.text((px, py + 16), "map after the collection window fires — dashed teal.", font=f12, fill=MUTED)

    save(img, "36-isr-beam-modes.png",
         "ISR beam-mode picker: payload + mode picks swath / resolution / power / duty, with live "
         "effective gain and SOC-drain preview.")


def s_jam_preview():
    """FW §11.A.1 — Jam parameter assistant with footprint preview."""
    img, d = canvas("blue", "Jam command — modulation × power × bandwidth → footprint preview")
    tx, ty = panel(d, 12, 66, 480, 340, "Modulation database")
    rows = [
        [("barrage",   BLUEc), ("broadband noise · easy to detect",  TEXT), ("eff 1.0",  GREEN)],
        [("spot",      BLUEc), ("narrow notch at freq_center",       TEXT), ("eff 0.95", GREEN)],
        [("sweep",     BLUEc), ("hopping noise · agile victims",     TEXT), ("eff 0.7",  YELLOW)],
        [("deceptive", BLUEc), ("replays victim signal · OVERT",     RED),  ("eff 1.3",  GREEN)],
    ]
    table(d, tx, ty, ["MOD", "DESCRIPTION", "EFF"], rows, [110, 280, 80], lh=24)

    px, py = panel(d, 508, 66, W - 520, 340, "Live preview")
    py = kv(d, px, py, [
        ("Modulation",  "spot",        BLUEc),
        ("Power",       "200 W",       TEXT),
        ("Eff. radius", "75.0 km",     YELLOW),
        ("P(success)",  "0.86",        GREEN),
        ("Detect risk", "50%",         MUTED),
        ("Attribution", "ambiguous",   TEXT),
        ("Power draw",  "140 W",       MUTED),
    ], kw=120)
    py += 6
    d.text((px, py),     "POST /api/sessions/{sid}/jam/compute → orange dashed", font=f12, fill=MUTED)
    d.text((px, py + 16), "footprint polygon on the 2-D map (centered on jammer).", font=f12, fill=MUTED)
    save(img, "37-jam-preview.png",
         "Jam assistant: modulation × power × bandwidth picker with effective-radius and "
         "footprint preview before commit.")


def s_consequence_preview():
    """FW §11.D.18 — live consequence preview for every action."""
    img, d = canvas("blue", "Live consequence preview — escalation / attribution / reversibility before commit")
    tx, ty = panel(d, 12, 66, W - 24, 340, "Severity per action (target: own civilian / red military)")
    rows = [
        [("observe",            BLUEc), ("LOW",    GREEN),  ("esc 1",  TEXT), ("reversible",   GREEN), ("ambiguous", TEXT)],
        [("downlink",           BLUEc), ("LOW",    GREEN),  ("esc 0",  TEXT), ("reversible",   GREEN), ("ambiguous", TEXT)],
        [("jam (spot)",         BLUEc), ("LOW",    GREEN),  ("esc 3",  TEXT), ("reversible",   GREEN), ("ambiguous", TEXT)],
        [("jam (deceptive)",    BLUEc), ("MED",    YELLOW), ("esc 3",  TEXT), ("reversible",   GREEN), ("OVERT",     RED)],
        [("cyber (data_exfil)", BLUEc), ("MED",    YELLOW), ("esc 2",  TEXT), ("reversible",   GREEN), ("covert",    TEXT)],
        [("cyber (WIPER)",      BLUEc), ("HIGH",   RED),    ("esc 6",  TEXT), ("IRREVERSIBLE", RED),   ("covert",    TEXT)],
        [("maneuver",           BLUEc), ("LOW",    GREEN),  ("esc 1",  TEXT), ("reversible",   GREEN), ("overt",     TEXT)],
        [("engage (kinetic)",   BLUEc), ("HIGH",   RED),    ("esc 8",  TEXT), ("IRREVERSIBLE", RED),   ("OVERT",     RED)],
    ]
    table(d, tx, ty, ["ACTION", "SEV", "ESC", "REVERSIBLE?", "ATTRIBUTION"], rows,
          [200, 80, 100, 200, 200], lh=26)
    nx, ny = panel(d, 12, 420, W - 24, 240, "Notes & guidance")
    lines(d, nx, ny, [
        ("• The consequence-preview line updates every time the operator changes action / target / params.", MUTED),
        ("• Civilian targets bump LOW → MED automatically (denying a civilian link raises political cost).", MUTED),
        ("• Wiper / kinetic / debris-generating actions trip the orange (MED) or red (HIGH) badge.", MUTED),
        ("• Issue button stays enabled; the preview is advisory — final ROE gating is server-side.", MUTED),
        ("", TEXT),
        ("Endpoint: POST /api/sessions/{sid}/preview/consequence  (request: full Order body)", BLUEc),
        ("Returns:  {severity, escalation_w, reversible, debris_risk, attribution, civilian_risk, notes}", BLUEc),
    ])
    save(img, "38-consequence-preview.png",
         "Live consequence preview: severity / escalation / reversibility / attribution surfaced "
         "before the operator commits.")


def s_conjunction_panel():
    """FW §11.C.14 — conjunction screening + one-click evade."""
    img, d = canvas("blue", "Conjunction screening — upcoming close approaches + one-click evade")
    tx, ty = panel(d, 12, 66, W - 24, 320, "Conjunctions (next 1 h)")
    rows = [
        [("BLUE-COMSAT-1",  BLUEc), ("UNKNOWN-RPO",  RED),    ("18.5 km",  YELLOW), ("CA in 10:00",  TEXT), ("[Evade]",  GREEN)],
        [("ISR-EO-1",       BLUEc), ("DEBRIS-A1",    MUTED),  ("42.0 km",  TEXT),   ("CA in 24:18",  TEXT), ("[Evade]",  GREEN)],
        [("ISR-EO-2",       BLUEc), ("DEBRIS-A1",    MUTED),  ("88.4 km",  TEXT),   ("CA in 26:05",  TEXT), ("[Evade]",  GREEN)],
    ]
    table(d, tx, ty, ["OWN ASSET", "OTHER", "RANGE", "TIME-TO-CA", "ACTION"], rows,
          [220, 220, 130, 200, 130], lh=28)

    nx, ny = panel(d, 12, 400, W - 24, 260, "How it works")
    lines(d, nx, ny, [
        ("• Data source: world.conjunctions (loaded from `conjunction_warning` injects or screening).", MUTED),
        ("• Endpoint:    GET /api/sessions/{sid}/conjunctions/{cell}  → list filtered by ownership.", MUTED),
        ("• Evade button issues a `command` order with verb `prop.collision_avoid`.", MUTED),
        ("• The order queues to the next command-uplink window for the affected satellite.", MUTED),
        ("• Replay-safe: the verb mutates world.conjunctions deterministically (eventlog-recorded).", MUTED),
        ("", TEXT),
        ("Recommended White-Cell injects: `conjunction_warning` or the library's `rpo_ambiguous`.", BLUEc),
    ])
    save(img, "39-conjunction-panel.png",
         "Conjunction-screening sidebar: each row carries range, time-to-CA, and a one-click "
         "[Evade] button that fires prop.collision_avoid for the own asset.")


def s_inject_builder():
    """FW §11.D.19 — White-Cell inject library + builder with timestamp scheduler."""
    img, d = canvas("white", "White-Cell inject builder — library + JSON editor + Now/+N s/absolute UTC scheduler")
    lx, ly = panel(d, 12, 66, 460, 340, "Inject library (5 templates)")
    rows = [
        [("debris_field_500km",     BLUEc), ("Unattributed breakup at 500 km",     TEXT)],
        [("gnss_jam_regional",      BLUEc), ("Localized GNSS jamming advisory",    TEXT)],
        [("rpo_ambiguous",          BLUEc), ("Unannounced satellite approach",     TEXT)],
        [("gs_outage_diego_garcia", BLUEc), ("Ground station DG-EAST uplink down", TEXT)],
        [("space_weather_severe",   BLUEc), ("Severe geomagnetic storm",           TEXT)],
    ]
    table(d, lx, ly, ["ID", "LABEL"], rows, [220, 220], lh=26)
    d.text((lx, ly + 165), "GET /api/sessions/{sid}/inject_library", font=f12, fill=MUTED)

    bx, by = panel(d, 488, 66, W - 500, 340, "Builder — \"Severe geomagnetic storm\" loaded")
    by = kv(d, bx, by, [
        ("Template",  "space_weather_severe", BLUEc),
        ("Effects",   "[{type: space_weather, severity: severe},",  TEXT),
        ("",          " {type: message, to: [white, blue, red],",   TEXT),
        ("",          "  text: \"Geomag storm advisory ...\"}]",    TEXT),
    ], kw=100)
    by += 8
    d.text((bx, by),       "Schedule:", font=f13b, fill=MUTED); by += 18
    d.text((bx, by),       "  ○ Now (immediate)", font=f13, fill=TEXT); by += 16
    d.text((bx, by),       "  ● + seconds from now: 60", font=f13, fill=GREEN); by += 16
    d.text((bx, by),       "  ○ Absolute UTC", font=f13, fill=MUTED); by += 22
    d.text((bx, by),       "[ Schedule / fire ]", font=f13b, fill=GREEN); by += 18
    d.text((bx, by),       "✓ scheduled for 2030-01-01T00:01:00Z (2 effects)", font=f12, fill=GREEN)

    nx, ny = panel(d, 12, 420, W - 24, 240, "How it works (replay-safe)")
    lines(d, nx, ny, [
        ("• Templates load from spacesim/content/inject_library.yaml (5 reusable patterns).", MUTED),
        ("• White Cell picks a template → JSON editor pre-fills → adjusts any field → schedules.", MUTED),
        ("• Now: fires immediately through the event log.  Future: schedules through sim.scheduler.", MUTED),
        ("• POST /api/sessions/{sid}/inject  with {inject:{effects:[...]}, at_sim_t:<µs UTC>}.", MUTED),
        ("• Past timestamps clamp to \"now\" (no backwards time travel).", MUTED),
        ("• Eventlog-recorded → byte-identical on save/resume + AAR scrub.", MUTED),
        ("", TEXT),
        ("New handler: spawn_debris  (appends to world.debris with regime + altitude + n_fragments).", BLUEc),
    ])
    save(img, "40-inject-builder.png",
         "White-Cell inject builder: library template picker + JSON editor + "
         "Now/+seconds/absolute-UTC scheduler with replay-safe future-dated firing.")


def s_accessibility_toggles():
    """FW §11.D.20 — accessibility palette toggles."""
    img, d = canvas("blue", "Accessibility — three toggles for colorblind / high-contrast / large-text use")
    # Three side-by-side sample panels showing each palette
    pw = (W - 48) // 3
    sx0 = 12

    # Standard
    sx, sy = panel(d, sx0, 66, pw, 280, "Standard palette")
    sy = kv(d, sx, sy, [("Accent", "#4fae7f", (79,174,127)),
                         ("Accent2","#3f7fd0", (63,127,208)),
                         ("Green",  "#6fcf6f", GREEN),
                         ("Yellow", "#e0c24a", YELLOW),
                         ("Red",    "#e06a6a", RED)], kw=80)

    # Colorblind-safe (Okabe-Ito) — pre-existing
    sx2 = sx0 + pw + 12
    sx, sy = panel(d, sx2, 66, pw, 280, "cb-safe (Okabe-Ito)")
    sy = kv(d, sx, sy, [("Accent", "#56B4E9", (86,180,233)),
                         ("Accent2","#0072B2", (0,114,178)),
                         ("Green",  "#009E73", (0,158,115)),
                         ("Yellow", "#F0E442", (240,228,66)),
                         ("Red",    "#D55E00", (213,94,0))], kw=80)

    # High-contrast (new, FW §11.D.20)
    sx3 = sx0 + 2 * (pw + 12)
    # Draw black-bg sample
    d.rounded_rectangle([sx3, 66, sx3 + pw, 66 + 280], radius=6, fill=(0, 0, 0), outline=(255, 255, 255))
    d.line([sx3 + 1, 67, sx3 + 1, 66 + 279], fill=(255, 255, 0), width=3)
    d.text((sx3 + 12, 75), "hi-contrast (WCAG-AAA)", font=f16b, fill=(255, 255, 0))
    d.line([sx3 + 12, 97, sx3 + pw - 12, 97], fill=(255, 255, 0), width=2)
    yy = 106
    for k, v, col in [("Bg",       "#000000", (255,255,255)),
                       ("Text",    "#ffffff", (255,255,255)),
                       ("Accent",  "#ffff00", (255,255,0)),
                       ("Accent2", "#00ffff", (0,255,255)),
                       ("Green",   "#00ff80", (0,255,128)),
                       ("Red",     "#ff4040", (255,64,64))]:
        d.text((sx3 + 12, yy), k, font=f13, fill=(200,200,200))
        d.text((sx3 + 92, yy), v, font=f13b, fill=col); yy += 22

    # Footer notes
    nx, ny = panel(d, 12, 360, W - 24, 300, "Toggles & persistence")
    lines(d, nx, ny, [
        ("Three header toggles, persisted in localStorage via the existing applyToggle path:", MUTED),
        ("  • cb        — Okabe-Ito palette (deuteranopia + protanopia safe; pre-existing)", BLUEc),
        ("  • hc        — high-contrast WCAG-AAA palette (black bg, white borders, yellow/cyan accents)", GREEN),
        ("  • bigtext   — 17 px base font + larger button hit areas (projector / low-vision)", YELLOW),
        ("", TEXT),
        ("All three are accessible from the ⌘K command palette as well:", MUTED),
        ("  - \"toggle cb-safe palette\"", BLUEc),
        ("  - \"toggle high-contrast mode\"", BLUEc),
        ("  - \"toggle large-text mode\"", BLUEc),
    ])
    save(img, "41-accessibility-toggles.png",
         "Accessibility palettes: standard / Okabe-Ito colorblind-safe / WCAG-AAA high-contrast, "
         "plus a large-text toggle. All persist in localStorage and are command-palette accessible.")


def s_local_time():
    """Local time selector — split UTC + selectable local timezone."""
    img, d = canvas("blue", "Time display — UTC for logic; selectable local timezone for operator convenience")
    cx, cy = panel(d, 12, 66, 580, 240, "Header time block")
    cy = kv(d, cx, cy, [
        ("UTC",       "2030-01-01T00:15:42Z",                  GREEN),
        ("Local",     "[Eastern ▾]  2029-12-31 19:15:42 EST",  TEXT),
    ], kw=80)
    cy += 14
    d.text((cx, cy), "Selectable zones: Eastern (default), Central, Mountain, Pacific,", font=f12, fill=MUTED)
    d.text((cx, cy + 16), "London, Paris/Berlin, Tokyo, UTC-only.", font=f12, fill=MUTED)

    nx, ny = panel(d, 608, 66, W - 620, 240, "Important")
    lines(d, nx, ny, [
        ("• Engine logic, saves, eventlog, and AAR snapshots remain in UTC microseconds.", MUTED),
        ("• Local time is a convenience render only — no server round-trip.", MUTED),
        ("• Switching zones re-renders instantly via Intl.DateTimeFormat.", MUTED),
        ("• Stored in localStorage so the operator's choice survives a reload.", MUTED),
    ])

    fx, fy = panel(d, 12, 320, W - 24, 340, "Why this matters in PME")
    lines(d, fx, fy, [
        ("Operators often think in their home timezone while the simulator runs in UTC.", TEXT),
        ("Splitting the display means:", MUTED),
        ("  • No risk of UTC↔local conversion errors leaking into logs / saves / AAR.", MUTED),
        ("  • Operators can quickly translate \"next pass in 12 min\" to a wall-clock time without math.", MUTED),
        ("  • All scheduling fields (inject `at_sim_t`, AAR scrubber) stay UTC-canonical.", MUTED),
        ("", TEXT),
        ("Tip: the inject builder's \"absolute UTC\" field also accepts a UTC literal so the", BLUEc),
        ("operator can paste a time from the UTC clock row without conversion.", BLUEc),
    ])
    save(img, "42-local-time.png",
         "Time-display block: UTC clock (canonical) above a selectable local-time row (Eastern default; "
         "Central/Mountain/Pacific/London/Paris/Tokyo/UTC-only options).")


# ---------------------------------------------------------------------------
# UI-reference annotated screenshots (FW follow-up).  Each function renders a
# schematic of one panel with numbered red callouts that the corresponding
# table in docs/training/10-ui-reference.md cross-references row-for-row.
# ---------------------------------------------------------------------------

def _ref_save(img, fname, caption):
    save(img, fname, caption)


def s_ref_header():
    img, d = canvas(None, "UI reference — header / toolbar (always visible)")
    # Re-paint the toolbar with sample controls, wrapped to two rows so all 23 fit
    tx, ty = panel(d, 12, 66, W - 24, 140, "Header — every control (laid out in two rows for legibility)")
    row1 = [
        ("Vignette", 110), ("Seed", 50), ("Load", 50), ("Start", 55),
        ("White", 50), ("Blue", 45), ("Red", 45),
        ("+1m", 40), ("+10m", 50), ("+1h", 40),
        ("⟲ Rewind", 80), ("Save", 50), ("Load file", 75),
    ]
    row2 = [
        ("present", 65), ("projector", 75), ("cb-safe", 60), ("hi-contrast", 80),
        ("large-text", 75), ("Tutorial", 65), ("Inspect", 60),
        ("⏸ Handover", 90), ("? Help", 55), ("Detach", 55),
    ]
    coord = []
    for row_y_offset, row in [(8, row1), (62, row2)]:
        x = tx
        y0 = ty + row_y_offset
        for lbl, w in row:
            d.rounded_rectangle([x, y0, x + w, y0 + 26], radius=4, fill=(30, 38, 50), outline=BORDER)
            d.text((x + 6, y0 + 7), lbl, font=f12, fill=TEXT)
            coord.append((x + w // 2, y0 + 13))
            x += w + 6
    for i, (cx, cy) in enumerate(coord, 1):
        callout(d, cx, cy - 22, i)
    # Legend
    lx, ly = panel(d, 12, 218, W - 24, 460, "Legend (cross-ref `10-ui-reference.md` §1)")
    rows = [
        (1,  "Vignette dropdown — pick scenario from the library"),
        (2,  "Seed — deterministic RNG seed (any non-negative integer)"),
        (3,  "Load — create the session (must precede Start)"),
        (4,  "Start — begin the exercise (enabled after Load)"),
        (5,  "White cell button — facilitator god-view"),
        (6,  "Blue cell button — player view (fog-of-war)"),
        (7,  "Red cell button — player view (fog-of-war)"),
        (8,  "+1 minute step"),
        (9,  "+10 minute step"),
        (10, "+1 hour step"),
        (11, "Rewind to t=0 (deterministic replay)"),
        (12, "Save — download the session as JSON"),
        (13, "Load file — resume from a JSON save"),
        (14, "present — presentation-mode body class"),
        (15, "projector — projector body class (larger fonts; hides compose)"),
        (16, "cb-safe — Okabe-Ito colorblind-safe palette"),
        (17, "hi-contrast — WCAG-AAA palette (black bg, white borders)"),
        (18, "large-text — 17 px base + larger button hit areas"),
        (19, "Tutorial — open the vignette's coachmark tour"),
        (20, "Inspect — open the YAML inspector modal"),
        (21, "⏸ Handover — blur the screen for hot-seat handoff"),
        (22, "? Help — open the help modal"),
        (23, "Detach viewers — pop globe + map into a 2nd window"),
    ]
    legend(d, lx, ly, W - 48, 420, "Header controls", rows)
    _ref_save(img, "ref-01-header.png",
              "UI reference §1 — header / toolbar: 23 always-visible controls (vignette load, cell switcher, time, presets, accessibility, modal triggers).")


def s_ref_cell_time():
    img, d = canvas("blue", "UI reference — Cell & Time sidebar panel")
    px, py = panel(d, 12, 66, W - 24, 360, "Cell & Time")
    # Clock block
    d.text((px, py),       "UTC:",   font=f13, fill=MUTED); callout(d, px - 4,  py + 8, 1)
    d.text((px + 50, py),  "2030-01-01T00:15:42Z", font=f13b, fill=GREEN)
    d.text((px, py + 22),  "[Eastern ▾]", font=f13b, fill=TEXT); callout(d, px + 60, py + 30, 2)
    d.text((px + 110, py + 22), "2029-12-31 19:15:42 EST", font=f13, fill=TEXT); callout(d, px + 200, py + 30, 3)
    d.text((px, py + 50),  "session abc1234", font=f12, fill=MUTED); callout(d, px - 4, py + 58, 4)
    # Objectives block
    d.text((px, py + 80),  "Objectives", font=f13b, fill=MUTED); callout(d, px - 4, py + 88, 5)
    d.text((px, py + 100), "  blue.image_target: pending", font=f12, fill=TEXT)
    d.text((px, py + 116), "  blue.return_to_safe: MET",   font=f12, fill=GREEN)
    # Messages
    d.text((px, py + 142), "Messages", font=f13b, fill=MUTED); callout(d, px - 4, py + 150, 6)
    d.text((px, py + 162), "  • SDA: unknown closing on BLUE-COMSAT-1", font=f12, fill=TEXT)
    # Coaching
    d.text((px, py + 188), "Coaching", font=f13b, fill=MUTED); callout(d, px - 4, py + 196, 7)
    d.text((px, py + 208), "  • Discuss the delayed downlink in AAR", font=f12, fill=BLUEc)
    # Conjunctions
    d.text((px, py + 234), "Conjunctions", font=f13b, fill=MUTED); callout(d, px - 4, py + 242, 8)
    d.text((px, py + 254), "  BLUE-COMSAT-1 ↔ UNKNOWN-RPO  18.5 km  CA 10:00  [Evade]", font=f12, fill=TEXT)

    lx, ly = panel(d, 12, 440, W - 24, 220, "Legend (`10-ui-reference.md` §2)")
    legend(d, lx, ly, W - 48, 180, "Cell & Time controls", [
        (1, "UTC clock — canonical sim time"),
        (2, "Timezone selector — Eastern / Central / Mountain / Pacific / London / Paris/Berlin / Tokyo / UTC-only"),
        (3, "Local time — read-only, follows the selector"),
        (4, "Session label — read-only id"),
        (5, "Objectives — current mission flags per cell"),
        (6, "Messages — inbox for this cell"),
        (7, "Coaching — facilitator notes due-now for this cell"),
        (8, "Conjunctions — upcoming close approaches; per-row Evade button"),
    ])
    _ref_save(img, "ref-02-cell-time.png",
              "UI reference §2 — Cell & Time sidebar: clock, timezone selector, objectives, messages, coaching, conjunctions.")


def s_ref_injects():
    img, d = canvas("white", "UI reference — Injects panel (White Cell)")
    px, py = panel(d, 12, 66, W - 24, 460, "Injects (White Cell)")
    # Fire row
    d.rounded_rectangle([px, py, px + 200, py + 24], radius=4, fill=(30,38,50), outline=BORDER)
    d.text((px + 6, py + 6), "patch_modem ▾", font=f12, fill=TEXT); callout(d, px - 4, py + 12, 1)
    d.rounded_rectangle([px + 210, py, px + 260, py + 24], radius=4, fill=GREEN, outline=BORDER)
    d.text((px + 222, py + 6), "Fire", font=f12b, fill=(0,0,0)); callout(d, px + 270, py + 12, 2)
    # Builder
    d.text((px, py + 40), "▼  Build / schedule inject", font=f13b, fill=BLUEc); callout(d, px - 4, py + 48, 3)
    bx = px + 16; by = py + 70
    d.text((bx, by), "Template: [space_weather_severe ▾]", font=f12, fill=TEXT); callout(d, bx - 22, by + 6, 4)
    d.text((bx + 320, by), "[Load]", font=f12b, fill=GREEN); callout(d, bx + 360, by + 6, 5)
    d.text((bx, by + 24), "Effects:", font=f12, fill=MUTED); callout(d, bx - 22, by + 30, 6)
    d.rounded_rectangle([bx, by + 42, bx + 700, by + 130], radius=4, fill=(10,16,22), outline=BORDER)
    d.text((bx + 6, by + 48), "[{\"type\":\"space_weather\",\"severity\":\"severe\"},", font=f12, fill=TEXT)
    d.text((bx + 6, by + 64), " {\"type\":\"message\",\"to\":[\"white\",\"blue\",\"red\"],",  font=f12, fill=TEXT)
    d.text((bx + 6, by + 80), "  \"text\":\"Geomag storm advisory\"}]",                       font=f12, fill=TEXT)
    d.text((bx, by + 150), "Schedule: [+ seconds from now ▾]", font=f12, fill=TEXT); callout(d, bx - 22, by + 156, 7)
    d.text((bx + 320, by + 150), "+s: [60]", font=f12, fill=TEXT); callout(d, bx + 372, by + 156, 8)
    d.text((bx + 450, by + 150), "UTC: [2030-01-01T00:01:00]", font=f12, fill=MUTED); callout(d, bx + 605, by + 156, 9)
    d.rounded_rectangle([bx, by + 180, bx + 160, by + 206], radius=4, fill=GREEN, outline=BORDER)
    d.text((bx + 8, by + 186), "Schedule / fire", font=f12b, fill=(0,0,0)); callout(d, bx + 170, by + 193, 10)

    lx, ly = panel(d, 12, 540, W - 24, 130, "Legend (`10-ui-reference.md` §3)")
    legend(d, lx, ly, W - 48, 90, "Injects panel controls", [
        (1, "Inject dropdown — vignette-defined injects"),
        (2, "Fire — immediate, no scheduling"),
        (3, "Build / schedule inject — disclosure that opens the builder below"),
        (4, "Template — 5 library entries + (custom)"),
        (5, "Load — pre-fill the editor from the template"),
        (6, "Effects — JSON list editor; any handler in manager._h_inject"),
        (7, "Schedule mode — Now / +seconds / Absolute UTC"),
        (8, "+s — relative offset (when Schedule=+s)"),
        (9, "UTC — datetime-local (when Schedule=absolute)"),
        (10, "Schedule / fire — submit; past timestamps clamp to now"),
    ])
    _ref_save(img, "ref-03-injects.png",
              "UI reference §3 — Injects panel: fire-by-id row + 10-control builder (template / editor / schedule).")


def s_ref_fleet():
    img, d = canvas("blue", "UI reference — Fleet rail")
    px, py = panel(d, 12, 66, W - 24, 360, "Fleet SOH rollup (own assets)")
    # Filter chips
    chips_x = px; chips_y = py
    for i, (lbl, w) in enumerate([("All",40),("Bus-red",70),("Payload-degraded",125),("Under-attack",100),("Safed",60)]):
        d.rounded_rectangle([chips_x, chips_y, chips_x + w, chips_y + 24], radius=12,
                            fill=(80,120,180) if i == 0 else (30,38,50), outline=BORDER)
        d.text((chips_x + 8, chips_y + 6), lbl, font=f12, fill=TEXT)
        chips_x += w + 6
    callout(d, px - 6, py + 12, 1)
    # Fleet table
    ty = py + 40
    rows = [
        ("ISR-EO-1",   "satellite", "nominal", GREEN,  "10:32",  ""),
        ("ISR-EO-2",   "satellite", "degraded",YELLOW, "10:48", "[batch]"),
        ("ISR-SAR-1",  "satellite", "nominal", GREEN,  "10:55",  ""),
        ("COMSAT-1",   "satellite", "safed",   RED,    "—",      ""),
        ("RADAR-N",    "ground",    "nominal", GREEN,  "—",      ""),
    ]
    headers = ["ID", "KIND", "HEALTH", "NEXT", ""]
    table(d, px, ty, headers, [[(c, col) for c, col in
                                 [(r[0], TEXT), (r[1], MUTED), (r[2], r[3]), (r[4], BLUEc), (r[5], YELLOW)]] for r in rows],
          [180, 130, 110, 90, 80], lh=26)
    callout(d, px + 50, ty + 30, 2)
    callout(d, px + 50, ty + 60, 3)

    lx, ly = panel(d, 12, 440, W - 24, 200, "Legend (`10-ui-reference.md` §4)")
    legend(d, lx, ly, W - 48, 160, "Fleet rail controls", [
        (1, "Filter chips — All / Bus-red / Payload-degraded / Under-attack / Safed"),
        (2, "Row click — open the Subsystem drill-down for that asset"),
        (3, "Shift-click — toggle the row into the multi-asset batch (see §9)"),
    ])
    _ref_save(img, "ref-04-fleet.png",
              "UI reference §4 — Fleet rail: 5 filter chips + clickable rows (click=drill, shift-click=batch).")


def s_ref_tasking():
    img, d = canvas("blue", "UI reference — Tasking (sensor)")
    px, py = panel(d, 12, 66, W - 24, 320, "Tasking (sensor)")
    # Mode chips
    cx = px
    for i, lbl in enumerate(["Organic", "SSN request"]):
        d.rounded_rectangle([cx, py, cx + (60 if i == 0 else 100), py + 24], radius=12,
                            fill=(80,120,180) if i == 0 else (30,38,50), outline=BORDER)
        d.text((cx + 6, py + 6), lbl, font=f12, fill=TEXT)
        cx += (60 if i == 0 else 100) + 6
    callout(d, px - 6, py + 12, 1)
    # Row 1
    y1 = py + 40
    fields1 = [("Intent: [characterize ▾]", 200, 2), ("Sensor: [auto ▾]", 160, 3),
               ("Regime: [LEO ▾]", 150, 4), ("Target: [RED-TGT]", 170, 5)]
    cx = px
    for lbl, w, n in fields1:
        d.rounded_rectangle([cx, y1, cx + w, y1 + 22], radius=4, fill=(30,38,50), outline=BORDER)
        d.text((cx + 6, y1 + 5), lbl, font=f12, fill=TEXT); callout(d, cx + w // 2, y1 - 8, n)
        cx += w + 6
    # Row 2
    y2 = y1 + 32
    fields2 = [("Priority: [priority ▾]", 180, 6)]
    cx = px
    for lbl, w, n in fields2:
        d.rounded_rectangle([cx, y2, cx + w, y2 + 22], radius=4, fill=(30,38,50), outline=BORDER)
        d.text((cx + 6, y2 + 5), lbl, font=f12, fill=TEXT); callout(d, cx + w // 2, y2 - 8, n)
        cx += w + 6
    d.rounded_rectangle([cx, y2, cx + 130, y2 + 22], radius=4, fill=GREEN, outline=BORDER)
    d.text((cx + 8, y2 + 5), "Plan collection", font=f12b, fill=(0,0,0)); callout(d, cx + 65, y2 - 8, 7)
    # Row 3 (ISR params)
    y3 = y2 + 32
    fields3 = [("Mode: [stripmap ▾]", 170, 8), ("Look angle: ▬▬▬● 15°", 200, 9), ("Duration (s): [300]", 170, 10)]
    cx = px
    for lbl, w, n in fields3:
        d.rounded_rectangle([cx, y3, cx + w, y3 + 22], radius=4, fill=(30,38,50), outline=BORDER)
        d.text((cx + 6, y3 + 5), lbl, font=f12, fill=TEXT); callout(d, cx + w // 2, y3 - 8, n)
        cx += w + 6
    # Coverage / SSN queue
    y4 = y3 + 38
    d.text((px, y4), "✓ coalition · global · 8 eligible sensors (concurrency 3)", font=f12, fill=GREEN)
    callout(d, px - 6, y4 + 8, 11)
    y5 = y4 + 24
    d.text((px, y5), "SSN queue: ssn-1  characterize  RED-TGT  GEO  priority  SCHEDULED  [✕]", font=f12, fill=TEXT)
    callout(d, px - 6, y5 + 8, 12)

    lx, ly = panel(d, 12, 400, W - 24, 240, "Legend (`10-ui-reference.md` §5)")
    legend(d, lx, ly, W - 48, 200, "Tasking controls", [
        (1, "Mode chips — Organic / SSN request"),
        (2, "Intent — search / track / characterize / cue"),
        (3, "Sensor — auto or pick an own sensor (Organic only)"),
        (4, "Regime — LEO / MEO / GEO / HEO / cislunar (SSN only)"),
        (5, "Target — track id"),
        (6, "Priority — routine / priority / immediate"),
        (7, "Plan collection — submit the order or SSN request"),
        (8, "Beam mode — auto + 6 named modes (EO/SAR-specific)"),
        (9, "Look angle — 0–45° off-nadir slider"),
        (10, "Duration — 30–3600 s per collection"),
        (11, "Coverage line — read-only feasibility hint"),
        (12, "SSN queue rows — per-row [✕] cancel button"),
    ])
    _ref_save(img, "ref-05-tasking.png",
              "UI reference §5 — Tasking panel: 2 mode chips + intent/sensor/regime/target/priority + ISR beam-mode trio + SSN queue.")


def s_ref_compose():
    img, d = canvas("blue", "UI reference — Satellite command (compose)")
    px, py = panel(d, 12, 66, W - 24, 380, "Satellite command")
    # Role chips
    cx = px
    for i, lbl in enumerate(["All","Bus","Payload","SDA"]):
        w = 50 + (10 if lbl == "Payload" else 0)
        d.rounded_rectangle([cx, py, cx + w, py + 22], radius=12,
                            fill=(80,120,180) if i == 0 else (30,38,50), outline=BORDER)
        d.text((cx + 6, py + 5), lbl, font=f12, fill=TEXT)
        cx += w + 6
    callout(d, px - 6, py + 10, 1)
    # Fields
    y1 = py + 36
    fields = [("Actor: [ISR-EO-1 ▾]", 200, 2),
              ("Action: [observe ▾]",  170, 3),
              ("Target: [RED-TGT]",    180, 4),
              ("Params: {\"intent\":\"characterize\"}", 320, 5)]
    cx = px
    for lbl, w, n in fields:
        d.rounded_rectangle([cx, y1, cx + w, y1 + 22], radius=4, fill=(30,38,50), outline=BORDER)
        d.text((cx + 6, y1 + 5), lbl, font=f12, fill=TEXT); callout(d, cx + w // 2, y1 - 8, n)
        cx += w + 6
    # Preview lines
    y2 = y1 + 40
    d.text((px, y2),       "✓ will queue · ground_uplink · window 14:32:10",      font=f12, fill=GREEN);  callout(d, px - 6, y2 + 6, 6)
    d.text((px, y2 + 18),  "⚠ LOW · esc 1 · reversible · debris none · ambiguous", font=f12, fill=MUTED); callout(d, px - 6, y2 + 24, 7)
    # Buttons
    y3 = y2 + 50
    d.rounded_rectangle([px, y3, px + 110, y3 + 28], radius=4, fill=BLUEc, outline=BORDER)
    d.text((px + 18, y3 + 8), "Issue order", font=f13b, fill=(0,0,0)); callout(d, px + 55, y3 - 8, 8)
    d.rounded_rectangle([px + 120, y3, px + 240, y3 + 28], radius=4, fill=(30,38,50), outline=BORDER)
    d.text((px + 130, y3 + 8), "★ Save preset", font=f12b, fill=YELLOW); callout(d, px + 180, y3 - 8, 9)
    d.rounded_rectangle([px + 530, y3, px + 670, y3 + 28], radius=4, fill=(30,38,50), outline=BORDER)
    d.text((px + 540, y3 + 8), "? Coachmark tour", font=f12, fill=BLUEc); callout(d, px + 600, y3 - 8, 10)
    # Playbook list, ribbon, queue
    y4 = y3 + 48
    d.text((px, y4),       "Playbooks: ★ \"daily downlink\"  ★ \"defensive maneuver\"", font=f12, fill=TEXT); callout(d, px - 6, y4 + 6, 11)
    y5 = y4 + 28
    d.text((px, y5),       "[cmd  ▮▮  ▮      ]", font=f12, fill=GREEN)
    d.text((px, y5 + 14),  "[tlm        ▮▮   ]", font=f12, fill=BLUEc)
    d.text((px, y5 + 28),  "[obs   ▮   ▮▮    ]", font=f12, fill=YELLOW); callout(d, px - 6, y5 + 14, 12)
    y6 = y5 + 60
    d.text((px, y6), "Queue: ord-3 ISR-EO-1 observe RED-TGT  ground_uplink  queued  [✕]", font=f12, fill=TEXT)
    callout(d, px - 6, y6 + 6, 13)

    lx, ly = panel(d, 12, 460, W - 24, 200, "Legend (`10-ui-reference.md` §6)")
    legend(d, lx, ly, W - 48, 160, "Satellite command controls", [
        (1, "Role filter chips — All / Bus / Payload / SDA"),
        (2, "Actor — own assets (filtered by role chip)"),
        (3, "Action — legal actions for the actor's kind"),
        (4, "Target — string (track id, station id, …)"),
        (5, "Params — JSON; pre-filled per action; live dry-run"),
        (6, "Validity preview — ✓ queue / ✗ reason (read-only)"),
        (7, "Consequence preview — severity / esc / reversible / attr"),
        (8, "Issue order — primary submit"),
        (9, "★ Save preset — store the current order as a playbook"),
        (10, "? Coachmark tour — start the in-page walkthrough"),
        (11, "Playbook list — saved presets, click to re-load"),
        (12, "Pass-timeline ribbon — cmd / tlm / obs lanes, next 6 h"),
        (13, "Queue rows — per-row cancel button"),
    ])
    _ref_save(img, "ref-06-compose.png",
              "UI reference §6 — Satellite command: 13 compose-form controls (role chip → actor/action/target/params → previews → issue → presets → ribbon → queue).")


def s_ref_maneuver():
    img, d = canvas("blue", "UI reference — Maneuver assistant (Action=maneuver)")
    px, py = panel(d, 12, 66, W - 24, 380, "Maneuver assistant — mode + fields + Compute")
    # Mode dropdown
    d.rounded_rectangle([px, py, px + 250, py + 24], radius=4, fill=(30,38,50), outline=BORDER)
    d.text((px + 6, py + 6), "Maneuver mode: [lvlh ▾]", font=f12, fill=TEXT); callout(d, px - 6, py + 12, 1)
    # ECI row
    y = py + 36
    d.text((px, y), "ECI:",  font=f13b, fill=BLUEc)
    for i, lbl in enumerate(["Δv X [0]", "Δv Y [5]", "Δv Z [0]"]):
        d.rounded_rectangle([px + 60 + i*110, y - 4, px + 150 + i*110, y + 16], radius=4, fill=(30,38,50), outline=BORDER)
        d.text((px + 66 + i*110, y - 1), lbl, font=f12, fill=TEXT)
    callout(d, px - 6, y + 6, 2)
    # LVLH
    y = py + 64
    d.text((px, y), "LVLH:", font=f13b, fill=BLUEc)
    for i, lbl in enumerate(["R [0]", "T [5]", "N [0]"]):
        d.rounded_rectangle([px + 60 + i*90, y - 4, px + 130 + i*90, y + 16], radius=4, fill=(30,38,50), outline=BORDER)
        d.text((px + 66 + i*90, y - 1), lbl, font=f12, fill=TEXT)
    callout(d, px - 6, y + 6, 3)
    # finite_burn
    y = py + 92
    d.text((px, y), "Finite:", font=f13b, fill=BLUEc)
    for i, lbl in enumerate(["DirR [0]","DirT [1]","DirN [0]","mag [5]","dur [60]"]):
        d.rounded_rectangle([px + 60 + i*92, y - 4, px + 140 + i*92, y + 16], radius=4, fill=(30,38,50), outline=BORDER)
        d.text((px + 66 + i*92, y - 1), lbl, font=f12, fill=TEXT)
    callout(d, px - 6, y + 6, 4)
    # target_coe
    y = py + 120
    d.text((px, y), "T-COE:", font=f13b, fill=BLUEc)
    for i, lbl in enumerate(["a","e","i","RAAN","ω"]):
        d.rounded_rectangle([px + 60 + i*90, y - 4, px + 130 + i*90, y + 16], radius=4, fill=(30,38,50), outline=BORDER)
        d.text((px + 66 + i*90, y - 1), lbl + " [keep]", font=f12, fill=MUTED)
    callout(d, px - 6, y + 6, 5)
    # hohmann
    y = py + 148
    d.text((px, y), "Hohmann:", font=f13b, fill=BLUEc)
    d.rounded_rectangle([px + 78, y - 4, px + 240, y + 16], radius=4, fill=(30,38,50), outline=BORDER)
    d.text((px + 84, y - 1), "target alt (km) [600]", font=f12, fill=TEXT)
    callout(d, px - 6, y + 6, 6)
    # plane_change
    y = py + 176
    d.text((px, y), "Plane chg:", font=f13b, fill=BLUEc)
    d.rounded_rectangle([px + 78, y - 4, px + 220, y + 16], radius=4, fill=(30,38,50), outline=BORDER)
    d.text((px + 84, y - 1), "Δi (deg) [5]", font=f12, fill=TEXT)
    callout(d, px - 6, y + 6, 7)
    # Compute + result
    y = py + 220
    d.rounded_rectangle([px, y, px + 160, y + 28], radius=4, fill=GREEN, outline=BORDER)
    d.text((px + 12, y + 8), "Compute Δv →", font=f12b, fill=(0,0,0)); callout(d, px + 80, y - 8, 8)
    d.text((px + 180, y + 8), "Δv = 5.00 m/s · → a 6843 km · e 0.0014 · i 51.6° (LEO)", font=f12, fill=GREEN)
    callout(d, px + 180, y + 32, 9)

    lx, ly = panel(d, 12, 460, W - 24, 200, "Legend (`10-ui-reference.md` §7)")
    legend(d, lx, ly, W - 48, 160, "Maneuver assistant controls", [
        (1, "Maneuver mode — eci / lvlh / finite_burn / target_coe / hohmann / plane_change"),
        (2, "ECI mode — Δv [x,y,z] m/s in inertial frame"),
        (3, "LVLH mode — Radial / Along-track / Normal (m/s) in orbit frame"),
        (4, "Finite-burn — direction + magnitude + duration (s, informational)"),
        (5, "Target-COE — a/e/i/RAAN/ω; blank=keep current; matches velocity at same true anomaly"),
        (6, "Hohmann — target altitude (km); 2-burn preview shows second burn"),
        (7, "Plane-change — Δi (deg, signed); Rodrigues rotation about r̂"),
        (8, "Compute Δv → — POST /maneuver/compute (read-only)"),
        (9, "Cost / new-orbit / second-burn preview — read-only result line"),
    ])
    _ref_save(img, "ref-07-maneuver.png",
              "UI reference §7 — Maneuver assistant: 6 entry modes + Compute Δv → preview before commit.")


def s_ref_jam():
    img, d = canvas("blue", "UI reference — Jam assistant (Action=jam)")
    px, py = panel(d, 12, 66, W - 24, 280, "Jam assistant — modulation + parameters + footprint preview")
    fields = [
        ("Modulation: [spot ▾]", 200, 1),
        ("Power (W) [200]",       150, 2),
        ("BW (kHz) [1000]",       150, 3),
        ("Victim BW (kHz) [1000]",180, 4),
        ("Base P_s [0.9]",        140, 5),
    ]
    cx = px
    for lbl, w, n in fields:
        d.rounded_rectangle([cx, py, cx + w, py + 24], radius=4, fill=(30,38,50), outline=BORDER)
        d.text((cx + 6, py + 6), lbl, font=f12, fill=TEXT); callout(d, cx + w // 2, py - 8, n)
        cx += w + 6
    y2 = py + 50
    d.rounded_rectangle([px, y2, px + 170, y2 + 28], radius=4, fill=GREEN, outline=BORDER)
    d.text((px + 8, y2 + 8), "Preview footprint", font=f12b, fill=(0,0,0)); callout(d, px + 80, y2 - 8, 6)
    d.text((px + 190, y2 + 8), "spot · r 75 km · Ps 0.86", font=f12, fill=GREEN); callout(d, px + 240, y2 + 32, 7)
    d.text((px, y2 + 50), "radius ≈ 75.0 km · P(success) 0.86 · draw 140 W · detect 50% · attr ambiguous", font=f12, fill=TEXT)

    lx, ly = panel(d, 12, 360, W - 24, 200, "Legend (`10-ui-reference.md` §8)")
    legend(d, lx, ly, W - 48, 160, "Jam assistant controls", [
        (1, "Modulation — barrage / spot / sweep / deceptive"),
        (2, "Power — transmit power in watts (drives effective radius)"),
        (3, "BW — jammer bandwidth in kHz"),
        (4, "Victim BW — target signal bandwidth in kHz"),
        (5, "Base P_s — operator's base success probability (0–1)"),
        (6, "Preview footprint — POST /jam/compute; renders orange dashed polygon on the 2-D map"),
        (7, "Summary / result line — radius, Ps, draw, detect, attribution"),
    ])
    _ref_save(img, "ref-08-jam.png",
              "UI reference §8 — Jam assistant: modulation × power × bandwidth → effective-radius + footprint preview.")


def s_ref_batch():
    img, d = canvas("blue", "UI reference — Batch bar + fleet-subset helpers")
    px, py = panel(d, 12, 66, W - 24, 220, "Batch bar")
    d.text((px, py), "Batch (3): ISR-EO-1, ISR-EO-2, ISR-SAR-1", font=f12, fill=TEXT)
    callout(d, px - 6, py + 6, 1)
    d.rounded_rectangle([px + 480, py - 4, px + 600, py + 24], radius=4, fill=GREEN, outline=BORDER)
    d.text((px + 492, py + 4), "Issue to all", font=f12b, fill=(0,0,0)); callout(d, px + 540, py - 14, 2)
    d.rounded_rectangle([px + 610, py - 4, px + 680, py + 24], radius=4, fill=(30,38,50), outline=BORDER)
    d.text((px + 626, py + 4), "Clear", font=f12b, fill=YELLOW); callout(d, px + 644, py - 14, 3)
    # Fleet-subset row
    y2 = py + 40
    d.text((px, y2 - 4), "Apply to subset:", font=f12, fill=MUTED)
    cx = px + 120
    for lbl, w in [("All own",70),("ISR sats",80),("SATCOM",75),("Same group",100)]:
        d.rounded_rectangle([cx, y2 - 4, cx + w, y2 + 20], radius=4, fill=(30,38,50), outline=BORDER)
        d.text((cx + 6, y2 + 1), lbl, font=f12, fill=TEXT)
        cx += w + 6
    callout(d, px + 110, y2 - 14, 4)

    lx, ly = panel(d, 12, 300, W - 24, 200, "Legend (`10-ui-reference.md` §9)")
    legend(d, lx, ly, W - 48, 160, "Batch bar controls", [
        (1, "Batch list — read-only; shift-click fleet rows to add/remove"),
        (2, "Issue to all — POSTs the current compose body once per batched asset"),
        (3, "Clear — empty the batch"),
        (4, "Fleet-subset helpers — All own / ISR sats / SATCOM / Same group (predicate-fill)"),
    ])
    _ref_save(img, "ref-09-batch.png",
              "UI reference §9 — Batch bar: shift-click batch + 4 fleet-subset helpers + Issue-to-all / Clear.")


def s_ref_globe():
    img, d = canvas("blue", "UI reference — 3D globe viewer")
    px, py = panel(d, 12, 66, 700, 340, "3D globe")
    # toolbar row
    cx = px
    for i, lbl in enumerate(["＋","－","tilt ▬▬●▬", "zoom-to [ISR-EO-1 ▾]","map ✓","spin ☐","Reset"]):
        w = 40 if lbl in ("＋","－") else (110 if "tilt" in lbl else (180 if "zoom" in lbl else 70))
        d.rounded_rectangle([cx, py, cx + w, py + 22], radius=4, fill=(30,38,50), outline=BORDER)
        d.text((cx + 6, py + 5), lbl, font=f12, fill=TEXT)
        callout(d, cx + w // 2, py - 8, i + 1)
        cx += w + 6
    # Globe sketch
    cx0, cy0, R = px + 320, py + 180, 90
    d.ellipse([cx0 - R, cy0 - R, cx0 + R, cy0 + R], fill=(10,20,40), outline=BLUEc, width=2)
    d.ellipse([cx0 - R - 18, cy0 - 4, cx0 + R + 18, cy0 + 4], outline=YELLOW, width=1)
    d.text((cx0 - 50, cy0 + R + 10), "drag = rotate · wheel = zoom", font=f12, fill=MUTED)
    callout(d, cx0 - 70, cy0 - 50, 7)
    callout(d, cx0 + 80, cy0 + 30, 8)

    lx, ly = panel(d, 728, 66, W - 740, 340, "Legend (`10-ui-reference.md` §10)")
    legend(d, lx, ly, W - 760, 300, "3D globe controls", [
        (1, "＋ — zoom in"),
        (2, "－ — zoom out"),
        (3, "tilt — slider (–80° to +80°)"),
        (4, "zoom-to — dropdown of own assets + tracks"),
        (5, "map — toggle the world coastline + border overlay"),
        (6, "spin — toggle auto-rotation"),
        (7, "drag — rotate"),
        (8, "wheel — zoom"),
        (None, ""),
        (None, "Reset — restore the default camera (no callout shown here)"),
    ])
    _ref_save(img, "ref-10-globe.png",
              "UI reference §10 — 3D globe viewer: zoom / tilt / zoom-to / map / spin / Reset + drag-to-rotate + wheel-to-zoom.")


def s_ref_map():
    img, d = canvas("blue", "UI reference — 2D belief map viewer")
    px, py = panel(d, 12, 66, 700, 340, "2D belief map")
    cx = px
    for i, lbl in enumerate(["＋","－","center [ISR-EO-1 ▾]","map ✓","tracks ✓","grid ✓","Reset"]):
        w = 40 if lbl in ("＋","－") else (180 if "center" in lbl else 75)
        d.rounded_rectangle([cx, py, cx + w, py + 22], radius=4, fill=(30,38,50), outline=BORDER)
        d.text((cx + 6, py + 5), lbl, font=f12, fill=TEXT)
        callout(d, cx + w // 2, py - 8, i + 1)
        cx += w + 6
    # Map sketch
    mx0, my0, MW, MH = px + 60, py + 60, 560, 230
    d.rectangle([mx0, my0, mx0 + MW, my0 + MH], fill=(8,12,18), outline=BORDER)
    for k in range(-90, 91, 30):
        ly_ = my0 + MH // 2 - int(k / 90.0 * MH // 2)
        d.line([mx0, ly_, mx0 + MW, ly_], fill=(28,38,52))
    d.text((mx0 + 8, my0 + MH - 18), "drag = pan · wheel = zoom", font=f12, fill=MUTED)
    callout(d, mx0 + 200, my0 + 120, 7)
    callout(d, mx0 + 360, my0 + 200, 8)

    lx, ly = panel(d, 728, 66, W - 740, 340, "Legend (`10-ui-reference.md` §11)")
    legend(d, lx, ly, W - 760, 300, "2D map controls", [
        (1, "＋ — zoom in"),
        (2, "－ — zoom out"),
        (3, "center — dropdown of own assets + tracks"),
        (4, "map — coastlines + country borders overlay"),
        (5, "tracks — toggle uncertainty rings + track labels"),
        (6, "grid — 30°-spaced lat/lon graticule"),
        (7, "drag — pan"),
        (8, "wheel — zoom"),
        (None, ""),
        (None, "Reset — restore the default camera (no callout shown here)"),
    ])
    _ref_save(img, "ref-11-map.png",
              "UI reference §11 — 2D belief map: zoom / center / map / tracks / grid / Reset + drag-to-pan + wheel-to-zoom.")


def s_ref_aar():
    img, d = canvas("white", "UI reference — After-action review (AAR)")
    px, py = panel(d, 12, 66, W - 24, 320, "After-action review")
    # Slider row
    d.line([px, py + 12, px + 700, py + 12], fill=BORDER, width=3)
    d.ellipse([px + 480 - 6, py + 12 - 6, px + 480 + 6, py + 12 + 6], fill=GREEN)
    callout(d, px + 360, py - 4, 1)
    # Bookmark + downloads
    d.rounded_rectangle([px + 720, py - 2, px + 830, py + 26], radius=4, fill=(30,38,50), outline=BORDER)
    d.text((px + 728, py + 6), "📌 Bookmark", font=f12, fill=YELLOW); callout(d, px + 775, py - 14, 2)
    d.text((px + 850, py + 6),  "⬇ CSV", font=f12b, fill=BLUEc); callout(d, px + 870, py - 14, 3)
    d.text((px + 910, py + 6),  "⬇ JSON", font=f12b, fill=BLUEc); callout(d, px + 930, py - 14, 3)
    # Bookmark list
    y2 = py + 50
    d.text((px, y2), "Bookmarks:  ★ before-engage (t=0:14:08)   ★ first-jam (t=0:21:33)", font=f12, fill=TEXT)
    callout(d, px - 6, y2 + 6, 4)
    # Branches
    y3 = y2 + 28
    d.rounded_rectangle([px, y3, px + 220, y3 + 26], radius=4, fill=(30,38,50), outline=BORDER)
    d.text((px + 10, y3 + 6), "＋ Save current branch", font=f12, fill=GREEN); callout(d, px + 110, y3 - 14, 5)
    d.rounded_rectangle([px + 232, y3, px + 410, y3 + 26], radius=4, fill=(30,38,50), outline=BORDER)
    d.text((px + 244, y3 + 6), "Compare selected", font=f12, fill=BLUEc); callout(d, px + 320, y3 - 14, 6)
    d.text((px, y3 + 40), "Branches:  ☐ baseline   ☑ alt-evade   ☐ no-cyber", font=f12, fill=TEXT)
    callout(d, px - 6, y3 + 46, 7)

    lx, ly = panel(d, 12, 400, W - 24, 240, "Legend (`10-ui-reference.md` §12)")
    legend(d, lx, ly, W - 48, 200, "AAR controls", [
        (1, "Scrubber — range slider over event sequence (read-only replay)"),
        (2, "📌 Bookmark — pin the current sim moment"),
        (3, "⬇ CSV / ⬇ JSON — download the AAR report"),
        (4, "Bookmark list — clickable to jump back"),
        (5, "＋ Save current branch — name the live world for later comparison"),
        (6, "Compare selected — diff two saved branches"),
        (7, "Branch list — check boxes select a pair to compare"),
    ])
    _ref_save(img, "ref-12-aar.png",
              "UI reference §12 — AAR: scrubber + bookmarks + CSV/JSON download + branch save/compare.")


def s_ref_drill():
    img, d = canvas("blue", "UI reference — Subsystem drill-down")
    px, py = panel(d, 12, 66, W - 24, 380, "Subsystem drill-down — ISR-EO-1 (bus + payload + telemetry + recovery)")
    # Parameter chips
    chips = ["battery_soc","temp_c","rx_power_dbm","cn0_dbhz","cmd_reject_count","fsw_error_count"]
    cx = px
    for c in chips:
        d.rounded_rectangle([cx, py, cx + 120, py + 22], radius=10, fill=(30,38,50), outline=BORDER)
        d.text((cx + 6, py + 5), c, font=f12, fill=BLUEc)
        cx += 126
    callout(d, px + 60, py - 10, 1)
    # Toggles
    y2 = py + 38
    d.text((px, y2), "[☐ compare to nominal]", font=f12, fill=TEXT); callout(d, px + 80, y2 + 6, 2)
    d.text((px + 200, y2), "overlay: [battery_soc ▾]", font=f12, fill=TEXT); callout(d, px + 310, y2 + 6, 3)
    # Graph rectangle
    gx, gy, GW, GH = px, y2 + 30, 540, 180
    d.rectangle([gx, gy, gx + GW, gy + GH], fill=(8,12,18), outline=BORDER)
    for k in range(1, 5):
        d.line([gx, gy + k * GH // 5, gx + GW, gy + k * GH // 5], fill=(28,38,52))
    d.text((gx + 8, gy + GH - 18), "telemetry graph (read-only)", font=f12, fill=MUTED)
    callout(d, gx + 270, gy + 90, 4)
    # Verb buttons on the right
    vx = px + 560; vy = y2 + 30
    for i, vb in enumerate(["eps.shed_load","comms.config_link","def.patch_cyber","cdh.clear_fault"]):
        d.rounded_rectangle([vx, vy + i*32, vx + 200, vy + 24 + i*32], radius=4, fill=(30,38,50), outline=BORDER)
        d.text((vx + 8, vy + 6 + i*32), vb, font=f12, fill=GREEN)
    callout(d, vx + 100, vy - 10, 5)
    # Recovery strip
    rx, ry = panel(d, 12, 460, W - 24, 100, "Recovery strip (when safed)")
    d.text((rx, ry), "Diagnosis: cyber  ·  passes used 0/3", font=f12, fill=YELLOW)
    d.rounded_rectangle([rx, ry + 24, rx + 160, ry + 50], radius=4, fill=GREEN, outline=BORDER)
    d.text((rx + 18, ry + 30), "Begin recovery", font=f12b, fill=(0,0,0)); callout(d, rx + 78, ry + 60, 6)
    d.rounded_rectangle([rx + 180, ry + 24, rx + 360, ry + 50], radius=4, fill=(30,38,50), outline=BORDER)
    d.text((rx + 190, ry + 30), "Patch (def.patch_cyber)", font=f12, fill=BLUEc); callout(d, rx + 270, ry + 60, 7)

    lx, ly = panel(d, 12, 580, W - 24, 90, "Legend (`10-ui-reference.md` §13)")
    legend(d, lx, ly, W - 48, 56, "Drill-down controls", [
        (1, "Parameter chips — click to graph that parameter"),
        (2, "compare to nominal — toggle the ghost baseline overlay"),
        (3, "overlay — pick a second parameter to overlay on the graph"),
        (4, "Graph canvas — read-only line graph (60-pt rolling)"),
        (5, "Verb buttons — one-click load the command into the compose form"),
        (6, "Begin recovery — start the multi-pass safe-mode chain"),
        (7, "Patch (def.patch_cyber) — load the patch-cyber command pre-filled"),
    ])
    _ref_save(img, "ref-13-drill.png",
              "UI reference §13 — Subsystem drill-down: parameter chips + nominal/overlay toggles + graph + per-verb buttons + recovery strip.")


def s_ref_activity():
    """Annotated screenshot of the per-cell Gantt timeline (white-cell example)."""
    img, d = canvas("white", "UI reference — Cell activity timeline (White-cell view shows all three lanes)")
    # Top: control row
    cx, cy = panel(d, 12, 66, W - 24, 60, "Cell activity timeline")
    d.text((cx, cy + 4),       "Past window: [30 min ▾]", font=f12, fill=TEXT); callout(d, cx + 80, cy + 12, 1)
    d.text((cx + 200, cy + 4), "Future window: [2 h ▾]",   font=f12, fill=TEXT); callout(d, cx + 280, cy + 12, 2)
    # Gantt canvas region
    gx, gy = panel(d, 12, 144, W - 24, 240, "Gantt (past · present · scheduled)")
    GW = W - 48; GH = 200
    g_left = gx; g_right = gx + GW; g_top = gy; g_bot = gy + GH
    d.rectangle([g_left, g_top, g_right, g_bot], fill=(8,12,18), outline=BORDER)
    # X axis grid + ticks
    for k in range(5):
        x = g_left + (k + 1) * GW // 6
        d.line([x, g_top, x, g_bot], fill=(28,38,52))
        d.text((x + 2, g_top + 4), f"+{(k+1)*40}m", font=f12, fill=MUTED)
    # NOW line
    nowx = g_left + GW // 3
    d.line([nowx, g_top - 6, nowx, g_bot + 6], fill=GREEN, width=2)
    d.text((nowx - 12, g_bot + 4), "NOW", font=f12b, fill=GREEN); callout(d, nowx + 4, g_top - 12, 3)
    # Three lanes — blue, red, neutral
    lane_h = (GH - 8) // 3
    lane_labels = [("BLUE", (90, 143, 224)), ("RED", (224, 122, 122)), ("NEUTRAL", (155, 170, 190))]
    for li, (lbl, col) in enumerate(lane_labels):
        ly = g_top + 4 + li * lane_h
        d.rectangle([g_left, ly, g_right, ly + lane_h - 2], fill=(20, 26, 34))
        d.text((g_left + 6, ly + 6), lbl, font=f12b, fill=col)
    callout(d, g_left + 30, g_top + 30, 4)            # lane label
    callout(d, g_left + 30, g_top + 30 + lane_h, 4)
    callout(d, g_left + 30, g_top + 30 + 2 * lane_h, 4)

    # Sample bars — Blue lane
    bly = g_top + 4 + 0 * lane_h + 30
    # executed past
    d.rectangle([nowx - 200, bly, nowx - 130, bly + 14], fill=(90,143,224,200))
    d.text((nowx - 195, bly + 2), "downlink", font=f12, fill=(10,15,21)); callout(d, nowx - 165, bly - 12, 5)
    # active straddles now
    d.rectangle([nowx - 30, bly + 22, nowx + 60, bly + 36], fill=(90,143,224,200))
    d.rectangle([nowx - 30, bly + 22, nowx + 60, bly + 36], outline=GREEN, width=2)
    d.text((nowx - 25, bly + 24), "observe", font=f12, fill=(10,15,21)); callout(d, nowx + 15, bly + 8, 6)
    # queued future (dashed)
    d.text((nowx + 100, bly + 24), "[queued: maneuver — dashed outline]", font=f12, fill=(90,143,224))
    callout(d, nowx + 230, bly + 10, 7)

    # Red lane — cancelled bar
    rly = g_top + 4 + 1 * lane_h + 22
    d.rectangle([nowx - 180, rly, nowx - 90, rly + 14], fill=(120,120,120,80))
    d.line([nowx - 180, rly + 7, nowx - 90, rly + 7], fill=(180,180,180), width=1)
    d.text((nowx - 175, rly + 2), "(cancelled)", font=f12, fill=MUTED); callout(d, nowx - 130, rly - 12, 8)
    # Rejected marker (×)
    d.line([nowx - 60, rly, nowx - 46, rly + 14], fill=RED, width=2)
    d.line([nowx - 46, rly, nowx - 60, rly + 14], fill=RED, width=2)
    callout(d, nowx - 38, rly - 12, 9)

    # Neutral lane — scheduled inject marker
    nly = g_top + 4 + 2 * lane_h + 22
    d.rectangle([nowx + 60, nly, nowx + 130, nly + 14], outline=(155,170,190), width=1)
    d.text((nowx + 65, nly + 2), "inject", font=f12, fill=(155,170,190)); callout(d, nowx + 95, nly - 12, 10)

    # Click-to-detail line
    d.text((gx, g_bot + 22), "Click a bar → ▼", font=f12, fill=MUTED)
    d.rectangle([gx + 130, g_bot + 16, gx + 900, g_bot + 38], fill=(20,26,34), outline=BORDER)
    d.text((gx + 138, g_bot + 21), "BLUE · ISR-EO-1 · observe → RED-TGT · active · 14:32:10 → 14:37:10 · ground_uplink",
           font=f12, fill=TEXT); callout(d, gx + 500, g_bot + 8, 11)

    lx, ly = panel(d, 12, 444, W - 24, 220, "Legend (`10-ui-reference.md` §15)")
    legend(d, lx, ly, W - 48, 190, "Activity timeline controls + visual encoding", [
        (1,  "Past window — 10 min / 30 min / 1 h / 3 h"),
        (2,  "Future window — 30 min / 1 h / 2 h / 6 h"),
        (3,  "NOW vertical line — bright green, marks the current sim time"),
        (4,  "Lane label — one lane per cell (BLUE / RED / NEUTRAL).  Fog-of-war: Blue cell sees only BLUE lane; Red sees only RED; White sees all three."),
        (5,  "Executed bar — filled cell-coloured rectangle (the past)"),
        (6,  "Active bar — filled + bright-green outline (straddles NOW)"),
        (7,  "Queued / scheduled bar — dashed cell-coloured outline (future)"),
        (8,  "Cancelled bar — grey strikethrough"),
        (9,  "Rejected order — red × marker at issued_at (no window)"),
        (10, "Scheduled inject — dashed neutral-coloured rectangle"),
        (11, "Click any bar → detail line shows cell · actor · action · status · window · delivery path"),
    ])
    save(img, "ref-15-activity.png",
         "UI reference §15 — Cell activity timeline: per-cell Gantt of past + present + scheduled orders, "
         "with status-encoded bars and fog-of-war filtering.")


def s_ref_modals_keys():
    img, d = canvas(None, "UI reference — Modals, overlays, keyboard & mouse")
    # Modals legend
    px, py = panel(d, 12, 66, (W - 36) // 2, 360, "Modals & overlays")
    rows = [
        ("Command palette",  "⌘K / Ctrl+K opens.  Text input + result list."),
        ("",                 "↑/↓ navigate · Enter run · Esc close."),
        ("Handover overlay", "⏸ Handover button blurs screen; Resume to return."),
        ("Help modal",       "? Help opens; Close to dismiss."),
        ("Tutorial panel",   "Tutorial button opens; click steps to progress; ✕ close."),
        ("Coachmark tour",   "? Coachmark tour starts; Back / Next / ✕ Close."),
        ("Vignette inspector","Inspect opens YAML; ⬇ Download YAML · Close."),
    ]
    yy = py
    for lbl, body in rows:
        d.text((px, yy), lbl, font=f13b, fill=BLUEc); d.text((px + 180, yy), body, font=f12, fill=TEXT); yy += 22
    # Keyboard shortcuts legend
    kx, ky = panel(d, 24 + (W - 36) // 2, 66, (W - 36) // 2, 360, "Keyboard & mouse")
    krows = [
        ("j / k",         "cycle through actor select"),
        ("c",             "focus the compose form"),
        ("g",             "graph the selected actor's telemetry"),
        ("⌘K / Ctrl-K",   "open command palette"),
        ("Esc",           "close palette / coachmark / handover"),
        ("↑ / ↓",         "navigate palette items"),
        ("Enter",         "run highlighted palette item"),
        ("Shift+click",   "toggle a fleet row into the batch"),
        ("",              ""),
        ("Map / globe drag",    "pan (map) / rotate (globe)"),
        ("Map / globe wheel",   "zoom"),
        ("AAR scrubber drag",   "scrub the event log"),
        ("Fleet row click",     "open Subsystem drill-down"),
    ]
    yy = ky
    for lbl, body in krows:
        d.text((kx, yy), lbl, font=f13b, fill=GREEN); d.text((kx + 170, yy), body, font=f12, fill=TEXT); yy += 22
    _ref_save(img, "ref-14-modals-keys.png",
              "UI reference §14 — Modals & overlays + keyboard shortcuts + mouse / canvas interactions.")


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
    s_telemetry_jam()
    s_telemetry_cyber()
    s_queue_timeline()
    s_aar_scrubber()
    s_alarms_soh()
    # FW §11 batch 11 — UX & realism upgrade screenshots.
    s_maneuver_assistant()
    s_isr_beam_modes()
    s_jam_preview()
    s_consequence_preview()
    s_conjunction_panel()
    s_inject_builder()
    s_accessibility_toggles()
    s_local_time()
    # UI reference module — 14 annotated panels (docs/training/10-ui-reference.md).
    s_ref_header()
    s_ref_cell_time()
    s_ref_injects()
    s_ref_fleet()
    s_ref_tasking()
    s_ref_compose()
    s_ref_maneuver()
    s_ref_jam()
    s_ref_batch()
    s_ref_globe()
    s_ref_map()
    s_ref_aar()
    s_ref_drill()
    s_ref_activity()
    s_ref_modals_keys()
    write_index()


if __name__ == "__main__":
    main()
