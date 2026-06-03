"use strict";
// Shared country-map drawer. Loads the committed low-res coastline+border polylines once and draws
// them through whatever projection a viewer supplies, so it rides the 2D pan/zoom and the 3D
// rotate/tilt/zoom automatically. project(lon,lat) -> {x, y, front}; front=false hides far-side
// (globe) segments. opts.maxJump breaks dateline wrap-around on the flat 2D map.
window.WorldMap = (function () {
  let data = null, loading = null;
  async function load() {
    if (data) return data;
    if (!loading) loading = fetch("/world.json").then((r) => r.json()).then((d) => (data = d));
    return loading;
  }
  function _set(ctx, segs, project, style, maxJump, width) {
    ctx.strokeStyle = style; ctx.lineWidth = width || 1;
    for (const seg of segs) {
      let started = false, lx = 0, ly = 0;
      ctx.beginPath();
      for (const pt of seg) {
        const p = project(pt[0], pt[1]);
        if (p.front === false) { started = false; continue; }
        if (started && maxJump && Math.abs(p.x - lx) > maxJump) started = false;
        if (!started) { ctx.moveTo(p.x, p.y); started = true; } else ctx.lineTo(p.x, p.y);
        lx = p.x; ly = p.y;
      }
      ctx.stroke();
    }
  }
  function draw(ctx, project, opts) {
    if (!data) return;
    const o = opts || {};
    _set(ctx, data.coast, project, o.coast || "#7aa8d0", o.maxJump, o.coastWidth || 1.2);
    if (o.borders !== false) _set(ctx, data.borders, project, o.border || "#5077a0", o.maxJump, o.borderWidth || 1);
  }
  return { load, draw, ready: () => !!data };
})();
