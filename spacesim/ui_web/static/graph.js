"use strict";
// Minimal seeded-telemetry line graph on a 2D canvas: plots a series with soft/hard limit lines,
// the trace colored by the current point's status. No dependencies.
window.Graph = (function () {
  const COL = { green: "#6fcf6f", yellow: "#e0c24a", red: "#e06a6a", los: "#7a8aa0" };
  // Time-axis line graph with optional faint dashed `ghost` (nominal), an optional second `overlay`
  // series (normalized to the same plot for shape comparison), and optional `windows` time spans
  // shaded behind everything to correlate the trace with hostile-effect intervals (§9.1).
  function draw(canvas, series, spec, ghost, opts) {
    opts = opts || {};
    const overlay = opts.overlay, windows = opts.windows || [];
    const x = canvas.getContext("2d"), W = canvas.width, H = canvas.height;
    x.fillStyle = "#0a0f15"; x.fillRect(0, 0, W, H);
    const pts = (series.points || []).filter((p) => p.value !== null);
    const gpts = ((ghost && ghost.points) || []).filter((p) => p.value !== null);
    const opts2 = ((overlay && overlay.points) || []).filter((p) => p.value !== null);
    if (!pts.length) { x.fillStyle = "#7a8aa0"; x.font = "12px monospace"; x.fillText("loss of signal", 12, H / 2); return; }
    const vals = pts.map((p) => p.value).concat(gpts.map((p) => p.value)).concat([spec.soft, spec.hard]);
    let lo = Math.min(...vals), hi = Math.max(...vals); if (hi === lo) hi = lo + 1;
    const pad = (hi - lo) * 0.1; lo -= pad; hi += pad;
    // Time-axis bounds drawn from the live series (graphs the same window the operator asked for).
    const t0 = pts[0].t, t1 = pts[pts.length - 1].t || (t0 + 1);
    const px = (t) => 36 + (t - t0) / (t1 - t0) * (W - 48);
    const py = (v) => H - 18 - (v - lo) / (hi - lo) * (H - 30);
    // Pass-correlation shading: each effect window that overlaps the visible range gets a faint band.
    for (const w of windows) {
      const a = Math.max(t0, w.start), z = Math.min(t1, w.end || t1);
      if (z <= a) continue;
      x.fillStyle = w.attributed ? "rgba(224,106,106,0.10)" : "rgba(224,194,74,0.10)";
      x.fillRect(px(a), 12, Math.max(2, px(z) - px(a)), H - 30);
    }
    // limit lines
    x.setLineDash([4, 3]);
    for (const [lim, c] of [[spec.soft, "#e0c24a"], [spec.hard, "#e06a6a"]]) {
      x.strokeStyle = c; x.beginPath(); x.moveTo(36, py(lim)); x.lineTo(W - 12, py(lim)); x.stroke();
    }
    // nominal ghost (faint, dashed) — drawn under the live trace
    if (gpts.length) {
      x.setLineDash([3, 3]); x.strokeStyle = "rgba(159,176,192,0.55)"; x.lineWidth = 1; x.beginPath();
      gpts.forEach((p, i) => (i ? x.lineTo(px(p.t), py(p.value)) : x.moveTo(px(p.t), py(p.value))));
      x.stroke();
    }
    // overlay trace (second parameter) — normalized so shape/correlation is visible across scales.
    let overlayLo = null, overlayHi = null;
    if (opts2.length) {
      const ov = opts2.map((p) => p.value);
      overlayLo = Math.min(...ov); overlayHi = Math.max(...ov);
      const span = (overlayHi - overlayLo) || 1;
      const opy = (v) => H - 18 - (v - overlayLo) / span * (H - 30);
      x.setLineDash([1, 3]); x.strokeStyle = "#9bd3ff"; x.lineWidth = 1; x.beginPath();
      opts2.forEach((p, i) => (i ? x.lineTo(px(p.t), opy(p.value)) : x.moveTo(px(p.t), opy(p.value))));
      x.stroke();
    }
    x.setLineDash([]);
    // live trace
    x.strokeStyle = COL[pts[pts.length - 1].status] || "#9fb0c0"; x.lineWidth = 1.5; x.beginPath();
    pts.forEach((p, i) => (i ? x.lineTo(px(p.t), py(p.value)) : x.moveTo(px(p.t), py(p.value))));
    x.stroke();
    x.fillStyle = "#9fb0c0"; x.font = "11px monospace";
    x.fillText(`${spec.label} (${spec.unit})`, 36, 12);
    let legendX = W - 110;
    if (opts2.length) { x.fillStyle = "#9bd3ff"; x.fillText(`···${overlay.param}`, legendX, 12); legendX -= 110; }
    if (gpts.length) { x.fillStyle = "rgba(159,176,192,0.7)"; x.fillText("- - nominal", legendX, 12); }
    x.fillStyle = "#9fb0c0";
    x.fillText(hi.toPrecision(3), 2, 14); x.fillText(lo.toPrecision(3), 2, H - 6);
    // FUTURE-WORK §8 — surface the OVERLAY's true y-scale on the right edge so the operator
    // doesn't have to guess what the normalized second trace means in absolute terms.
    if (opts2.length && overlayHi !== null) {
      x.fillStyle = "#9bd3ff";
      x.textAlign = "right";
      x.fillText(overlayHi.toPrecision(3), W - 2, 14);
      x.fillText(overlayLo.toPrecision(3), W - 2, H - 6);
      x.textAlign = "left";
    }
  }
  // Tiny inline sparkline for a subsystem-card parameter row (§5.1). No axis labels.
  // The sparkline and the large drill-down graph must be visually CONNECTED — they draw the
  // same read-time-seeded series over the same window. To make that obvious, the sparkline
  // shares the large graph's policies: (1) the y-range folds in the soft/hard limit lines
  // (so a trace that reads flat in the big graph also reads flat here, instead of being
  // auto-stretched to fill the box), and (2) the x-axis is time-based, not sample-ordinal
  // (audit Jun 2026 §graphs).
  function spark(canvas, series, spec) {
    const x = canvas.getContext("2d"), W = canvas.width, H = canvas.height;
    x.clearRect(0, 0, W, H);
    const pts = (series.points || []).filter((p) => p.value !== null);
    if (pts.length < 2) return;
    const lims = spec ? [spec.soft, spec.hard].filter((v) => v != null) : [];
    const ys = pts.map((p) => p.value).concat(lims);
    let lo = Math.min(...ys), hi = Math.max(...ys); if (hi === lo) hi = lo + 1;
    const t0 = pts[0].t, t1 = pts[pts.length - 1].t || (t0 + 1);
    const py = (v) => H - 2 - (v - lo) / (hi - lo) * (H - 4);
    const px = (t) => 1 + (t1 > t0 ? (t - t0) / (t1 - t0) : 0) * (W - 2);
    // Faint soft-limit line so the sparkline carries the same context as the large graph.
    if (spec && spec.soft != null) {
      x.strokeStyle = "rgba(224,194,74,0.35)"; x.lineWidth = 1; x.setLineDash([2, 2]);
      x.beginPath(); x.moveTo(0, py(spec.soft)); x.lineTo(W, py(spec.soft)); x.stroke();
      x.setLineDash([]);
    }
    x.strokeStyle = COL[pts[pts.length - 1].status] || "#9fb0c0"; x.lineWidth = 1;
    x.beginPath();
    pts.forEach((p, i) => (i ? x.lineTo(px(p.t), py(p.value)) : x.moveTo(px(p.t), py(p.value))));
    x.stroke();
  }
  return { draw, spark };
})();
