"use strict";
// Minimal seeded-telemetry line graph on a 2D canvas: plots a series with soft/hard limit lines,
// the trace colored by the current point's status. No dependencies.
window.Graph = (function () {
  const COL = { green: "#6fcf6f", yellow: "#e0c24a", red: "#e06a6a", los: "#7a8aa0" };
  function draw(canvas, series, spec) {
    const x = canvas.getContext("2d"), W = canvas.width, H = canvas.height;
    x.fillStyle = "#0a0f15"; x.fillRect(0, 0, W, H);
    const pts = (series.points || []).filter((p) => p.value !== null);
    if (!pts.length) { x.fillStyle = "#7a8aa0"; x.font = "12px monospace"; x.fillText("loss of signal", 12, H / 2); return; }
    const vals = pts.map((p) => p.value).concat([spec.soft, spec.hard]);
    let lo = Math.min(...vals), hi = Math.max(...vals); if (hi === lo) hi = lo + 1;
    const pad = (hi - lo) * 0.1; lo -= pad; hi += pad;
    const px = (i) => 36 + i / (pts.length - 1 || 1) * (W - 48);
    const py = (v) => H - 18 - (v - lo) / (hi - lo) * (H - 30);
    // limit lines
    x.setLineDash([4, 3]);
    for (const [lim, c] of [[spec.soft, "#e0c24a"], [spec.hard, "#e06a6a"]]) {
      x.strokeStyle = c; x.beginPath(); x.moveTo(36, py(lim)); x.lineTo(W - 12, py(lim)); x.stroke();
    }
    x.setLineDash([]);
    // trace
    x.strokeStyle = COL[pts[pts.length - 1].status] || "#9fb0c0"; x.lineWidth = 1.5; x.beginPath();
    pts.forEach((p, i) => (i ? x.lineTo(px(i), py(p.value)) : x.moveTo(px(i), py(p.value))));
    x.stroke();
    x.fillStyle = "#9fb0c0"; x.font = "11px monospace";
    x.fillText(`${spec.label} (${spec.unit})`, 36, 12);
    x.fillText(hi.toPrecision(3), 2, 14); x.fillText(lo.toPrecision(3), 2, H - 6);
  }
  return { draw };
})();
