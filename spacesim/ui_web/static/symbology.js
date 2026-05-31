"use strict";
// FUTURE-WORK §4 — APP-6-adapted space symbology pack.
// Mission-type-specific marker shapes shared by the 2D map (app.js) and the 3D globe (globe.js).
// Not formally APP-6 compliant — this is a v1 visual convention that joint trainees recognise.
//
// Conventions (filled with cell-accent for own; outlined in track-color for tracks):
//   ISR (eo/sar):  triangle pointing up      ("imaging")
//   SATCOM:        square                    ("comms")
//   PNT:           diamond                   ("navigation")
//   SIGINT:        inverted triangle         ("signals")
//   SDA payload:   plus/cross                ("surveillance")
//   weather:       circle                    ("environmental")
//   ground_station: filled square (larger)   ("ground")
//   jammer:        star (5-point)            ("effector EW")
//   interceptor:   filled diamond + line     ("kinetic effector")
//   default sat:   triangle (legacy)
window.Symbology = (function () {
  function draw(ctx, x, y, asset, opts) {
    opts = opts || {};
    const r = opts.r || 5;
    const kind = (asset && asset.kind) || "satellite";
    const payload = (asset && asset.payload) || "";
    // Ground entities first.
    if (kind === "ground_station") { ctx.fillRect(x - r, y - r, 2 * r, 2 * r); return; }
    if (kind === "jammer") { star(ctx, x, y, r); return; }
    if (kind === "interceptor") { diamond(ctx, x, y, r); ctx.fillRect(x - 1, y - r * 1.8, 2, r * 1.4); return; }
    if (kind === "terrestrial_force") { ctx.fillRect(x - r, y - r * 0.6, 2 * r, r * 1.2); return; }
    // Orbital — branch on payload type.
    if (payload === "satcom") { ctx.fillRect(x - r, y - r, 2 * r, 2 * r); return; }
    if (payload === "pnt")    { diamond(ctx, x, y, r); return; }
    if (payload === "sigint") { invTriangle(ctx, x, y, r); return; }
    if (payload === "weather"){ ctx.beginPath(); ctx.arc(x, y, r, 0, 2 * Math.PI); ctx.fill(); return; }
    if (payload === "sda")    { plus(ctx, x, y, r); return; }
    // Default: triangle (ISR or generic orbital).
    triangle(ctx, x, y, r);
  }
  function triangle(c, x, y, r) {
    c.beginPath(); c.moveTo(x, y - r); c.lineTo(x - r, y + r * 0.8);
    c.lineTo(x + r, y + r * 0.8); c.closePath(); c.fill();
  }
  function invTriangle(c, x, y, r) {
    c.beginPath(); c.moveTo(x, y + r); c.lineTo(x - r, y - r * 0.8);
    c.lineTo(x + r, y - r * 0.8); c.closePath(); c.fill();
  }
  function diamond(c, x, y, r) {
    c.beginPath(); c.moveTo(x, y - r); c.lineTo(x + r, y);
    c.lineTo(x, y + r); c.lineTo(x - r, y); c.closePath(); c.fill();
  }
  function plus(c, x, y, r) {
    c.fillRect(x - r, y - 1, 2 * r, 2);
    c.fillRect(x - 1, y - r, 2, 2 * r);
  }
  function star(c, x, y, r) {
    c.beginPath();
    for (let i = 0; i < 10; i++) {
      const ang = (i * Math.PI / 5) - Math.PI / 2;
      const rr = i % 2 ? r * 0.5 : r;
      const px = x + rr * Math.cos(ang), py = y + rr * Math.sin(ang);
      i ? c.lineTo(px, py) : c.moveTo(px, py);
    }
    c.closePath(); c.fill();
  }
  return { draw };
})();
