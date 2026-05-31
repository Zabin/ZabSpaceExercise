"use strict";
// A self-contained 3D globe viewer — orthographic azimuthal projection of a rotating sphere drawn
// on a 2D canvas (no external libraries, works offline). Renders the per-cell belief scene from
// /scene: own assets on/above the globe (hidden when behind the limb) and tracks as uncertainty
// rings. Controls: drag to rotate, tilt slider, zoom (wheel + buttons), zoom-to an asset, spin,
// reset. The full WebGL/textured globe can layer on later without changing the /scene contract.

window.Globe = (function () {
  const RE = 6371; // km, display only
  let cv, ctx, scene = null, showMap = true;
  let cam = { lon0: 0, pitch: 20, zoom: 1, auto: false };

  function project(lat, lon, altKm) {
    const la = lat * Math.PI / 180, lo = (lon - cam.lon0) * Math.PI / 180;
    const la0 = cam.pitch * Math.PI / 180;
    const cosc = Math.sin(la0) * Math.sin(la) + Math.cos(la0) * Math.cos(la) * Math.cos(lo);
    const x = Math.cos(la) * Math.sin(lo);
    const y = Math.cos(la0) * Math.sin(la) - Math.sin(la0) * Math.cos(la) * Math.cos(lo);
    const r = (cv.width / 2 - 18) * cam.zoom;
    const rad = r * (1 + (altKm || 0) / RE);
    return { x: cv.width / 2 + rad * x, y: cv.height / 2 - rad * y, front: cosc >= 0, R: r };
  }

  function draw() {
    if (!ctx) return;
    ctx.fillStyle = "#070b10"; ctx.fillRect(0, 0, cv.width, cv.height);
    const R = (cv.width / 2 - 18) * cam.zoom, cx = cv.width / 2, cy = cv.height / 2;
    // Ocean disk.
    ctx.beginPath(); ctx.arc(cx, cy, R, 0, 2 * Math.PI); ctx.fillStyle = "#0e2438"; ctx.fill();
    ctx.strokeStyle = "#2a3646"; ctx.stroke();
    // Day/night: soft highlight centered on the subsolar point if it's on the near side.
    if (scene) {
      const s = project(scene.sun_lat_deg, scene.sun_lon_deg, 0);
      if (s.front) {
        const g = ctx.createRadialGradient(s.x, s.y, 4, s.x, s.y, R * 1.3);
        g.addColorStop(0, "rgba(120,150,170,.35)"); g.addColorStop(1, "rgba(120,150,170,0)");
        ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, R, 0, 2 * Math.PI); ctx.clip();
        ctx.fillStyle = g; ctx.fillRect(0, 0, cv.width, cv.height); ctx.restore();
      }
    }
    // Country map (coastlines + borders), clipped to the near side via the front flag.
    if (window.WorldMap && WorldMap.ready() && showMap) {
      ctx.save(); ctx.beginPath(); ctx.arc(cx, cy, R, 0, 2 * Math.PI); ctx.clip();
      WorldMap.draw(ctx, (lon, lat) => { const p = project(lat, lon, 0); return { x: p.x, y: p.y, front: p.front }; }, {});
      ctx.restore();
    }
    // Graticule (near-side segments only).
    ctx.strokeStyle = "rgba(60,90,120,.5)"; ctx.lineWidth = 1;
    for (let lon = -180; lon < 180; lon += 30) seg((t) => [t, lon], -90, 90);
    for (let lat = -60; lat <= 60; lat += 30) seg((t) => [lat, t], -180, 180);
    if (!scene) return;
    // User-added FW #1 — orbital paths: dim polyline projected at the asset's altitude.
    ctx.strokeStyle = "rgba(159,176,192,0.4)"; ctx.lineWidth = 1;
    scene.assets.forEach((a) => {
      if (!a.on_orbit || !a.track || a.track.length < 2) return;
      ctx.beginPath();
      let prev = null;
      a.track.forEach((p) => {
        const proj = project(p[0], p[1], (p[2] || 0) / 1000);
        if (prev && prev.front && proj.front) ctx.lineTo(proj.x, proj.y);
        else ctx.moveTo(proj.x, proj.y);
        prev = proj;
      });
      ctx.stroke();
    });
    // Own assets — color matches the active cell accent (§10.A.1); APP-6 shapes via Symbology (§4).
    const accent = window.cellAccent ? window.cellAccent() : "#6fcf6f";
    scene.assets.forEach((a) => {
      const p = project(a.lat_deg, a.lon_deg, (a.alt_m || 0) / 1000);
      if (!p.front) return;
      ctx.fillStyle = accent;
      if (window.Symbology) Symbology.draw(ctx, p.x, p.y, a, { r: 5 });
      else { if (a.on_orbit) { ctx.beginPath(); ctx.moveTo(p.x, p.y - 5); ctx.lineTo(p.x - 5, p.y + 4); ctx.lineTo(p.x + 5, p.y + 4); ctx.closePath(); ctx.fill(); } else ctx.fillRect(p.x - 4, p.y - 4, 8, 8); }
      ctx.fillStyle = "#9fb0c0"; ctx.font = "11px monospace"; ctx.fillText(a.id, p.x + 7, p.y + 3);
    });
    // Tracks (belief) with uncertainty ring.
    scene.tracks.forEach((t) => {
      const p = project(t.lat_deg, t.lon_deg, (t.alt_m || 0) / 1000);
      if (!p.front) return;
      const rr = Math.max(5, Math.min(40, t.uncertainty_km / 18));
      ctx.strokeStyle = t.characterized ? "#e0c24a" : "#e06a6a";
      ctx.beginPath(); ctx.arc(p.x, p.y, rr, 0, 2 * Math.PI); ctx.stroke();
      ctx.fillStyle = ctx.strokeStyle; ctx.beginPath(); ctx.arc(p.x, p.y, 2, 0, 2 * Math.PI); ctx.fill();
      ctx.fillStyle = "#9fb0c0"; ctx.fillText(`${t.object} ±${t.uncertainty_km}km`, p.x + 6, p.y - 6);
    });
  }

  function seg(fn, a, b) {
    let prev = null;
    for (let t = a; t <= b; t += 6) {
      const [lat, lon] = fn(t); const p = project(lat, lon, 0);
      if (prev && prev.front && p.front) { ctx.beginPath(); ctx.moveTo(prev.x, prev.y); ctx.lineTo(p.x, p.y); ctx.stroke(); }
      prev = p;
    }
  }

  function init(id) {
    cv = document.getElementById(id); if (!cv) return; ctx = cv.getContext("2d");
    let drag = null;
    cv.addEventListener("mousedown", (e) => { drag = { x: e.clientX, y: e.clientY }; });
    window.addEventListener("mouseup", () => { drag = null; });
    window.addEventListener("mousemove", (e) => {
      if (!drag) return;
      cam.lon0 = (cam.lon0 - (e.clientX - drag.x) * 0.5);
      cam.pitch = Math.max(-80, Math.min(80, cam.pitch + (e.clientY - drag.y) * 0.3));
      const tilt = document.getElementById("g-tilt"); if (tilt) tilt.value = Math.round(cam.pitch);
      drag = { x: e.clientX, y: e.clientY }; draw();
    });
    cv.addEventListener("wheel", (e) => { e.preventDefault(); cam.zoom = clampZoom(cam.zoom * (e.deltaY < 0 ? 1.1 : 0.9)); draw(); });
    on("g-zoom-in", () => { cam.zoom = clampZoom(cam.zoom * 1.2); draw(); });
    on("g-zoom-out", () => { cam.zoom = clampZoom(cam.zoom / 1.2); draw(); });
    on("g-reset", () => { cam = { lon0: 0, pitch: 20, zoom: 1, auto: false }; const a = document.getElementById("g-auto"); if (a) a.checked = false; draw(); });
    const tilt = document.getElementById("g-tilt"); if (tilt) tilt.addEventListener("input", () => { cam.pitch = +tilt.value; draw(); });
    const auto = document.getElementById("g-auto"); if (auto) auto.addEventListener("change", () => { cam.auto = auto.checked; });
    const focus = document.getElementById("g-focus"); if (focus) focus.addEventListener("change", () => focusOn(focus.value));
    const mapcb = document.getElementById("g-map"); if (mapcb) mapcb.addEventListener("change", () => { showMap = mapcb.checked; draw(); });
    setInterval(() => { if (cam.auto) { cam.lon0 -= 1.2; draw(); } }, 60);
    if (window.WorldMap) WorldMap.load().then(draw);
  }

  function focusOn(id) {
    if (!scene) return;
    const a = scene.assets.find((x) => x.id === id) || scene.tracks.find((x) => x.object === id);
    if (!a) return;
    cam.lon0 = a.lon_deg; cam.pitch = a.lat_deg; cam.zoom = clampZoom(2.2); draw();
  }

  const clampZoom = (z) => Math.max(0.6, Math.min(6, z));
  const on = (id, fn) => { const el = document.getElementById(id); if (el) el.addEventListener("click", fn); };

  function render(s) { scene = s; draw(); }
  return { init, render, focusOn };
})();
