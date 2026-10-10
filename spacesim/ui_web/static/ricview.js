"use strict";
// IP-1300 (FR-8210/FR-8220) — live RIC-frame relative-motion view + CATS phase-angle readout.
// A pure consumer of GET /api/sessions/{sid}/ric_view/{cell}: fog-of-war is applied server-side
// (own assets + own Tracks only; White reads ground truth via the god-view path). The
// origin/chase/target selection is per-viewer, per-request UI state and is deliberately NOT
// persisted (IP-1300 Design Decision 3 / BL-0156). The CATS angle is shown as a raw, unbanded
// number (Design Decision 4 / BL-0154) — no colour/usable-band classification is implied.
(function () {
  const POLL_MS = 1500;      // same cadence as the main view poll
  let timer = null;

  const el = (id) => document.getElementById(id);
  const escH = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  // Candidate objects this seat can pick: on-orbit assets in the current view + the cell's own
  // tracked objects. The server is the authority — a stale/out-of-custody pick comes back 404.
  function candidates() {
    const ids = new Set();
    const assets = (typeof ASSETS !== "undefined") ? ASSETS : {};
    for (const [id, a] of Object.entries(assets)) {
      const k = a.kind || "";
      if (!k.startsWith("ground") && k !== "space_based" && !a.network) ids.add(id);
    }
    if (typeof SCENE !== "undefined" && SCENE && CELL !== "white") {
      (SCENE.tracks || []).forEach((t) => ids.add(t.object));
    }
    return [...ids].sort();
  }

  function fillSelect(sel, ids, allowNone) {
    const cur = sel.value;
    sel.innerHTML = (allowNone ? `<option value="">(none)</option>` : "") +
      ids.map((i) => `<option value="${escH(i)}">${escH(i)}</option>`).join("");
    if (cur && (ids.includes(cur) || (allowNone && cur === ""))) sel.value = cur;
  }

  function refreshPickers() {
    const ids = candidates();
    fillSelect(el("ric-origin"), ids, false);
    fillSelect(el("ric-chase"), ids, true);
    fillSelect(el("ric-target"), ids, true);
  }

  function plot(objects) {
    // In-track (horizontal, km) vs radial (vertical, km); origin at centre. Auto-scaled.
    const W = 340, H = 220, pad = 18;
    const maxAbs = Math.max(1, ...objects.map((o) => Math.max(Math.abs(o.ric_r[1]), Math.abs(o.ric_r[0])) / 1000));
    const sx = (W / 2 - pad) / maxAbs, sy = (H / 2 - pad) / maxAbs;
    const cx = W / 2, cy = H / 2;
    const pts = objects.map((o) => {
      const x = cx + (o.ric_r[1] / 1000) * sx, y = cy - (o.ric_r[0] / 1000) * sy;
      const cls = o.source === "track" ? "ric-pt-track" : "ric-pt-asset";
      return `<circle class="${cls}" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="4"></circle>` +
             `<text class="ric-lbl" x="${(x + 6).toFixed(1)}" y="${(y - 4).toFixed(1)}">${escH(o.id)}</text>`;
    }).join("");
    return `<svg viewBox="0 0 ${W} ${H}" class="ric-svg" role="img" aria-label="RIC relative positions">
      <line class="ric-axis" x1="${pad}" y1="${cy}" x2="${W - pad}" y2="${cy}"></line>
      <line class="ric-axis" x1="${cx}" y1="${pad}" x2="${cx}" y2="${H - pad}"></line>
      <text class="ric-lbl" x="${W - pad - 60}" y="${cy - 4}">+I (in-track)</text>
      <text class="ric-lbl" x="${cx + 4}" y="${pad + 8}">+R (radial)</text>
      <text class="ric-lbl muted" x="${pad}" y="${H - 4}">scale ±${maxAbs.toFixed(1)} km</text>
      <circle class="ric-origin" cx="${cx}" cy="${cy}" r="5"></circle>${pts}</svg>`;
  }

  async function poll() {
    const out = el("ric-out"); if (!out) return;
    if (typeof SID === "undefined" || !SID) { out.innerHTML = "<div class='muted'>(load a vignette first)</div>"; return; }
    if (CELL === "observer") { out.innerHTML = "<div class='muted'>(the RIC view is not available to the Observer seat)</div>"; return; }
    refreshPickers();
    const origin = el("ric-origin").value;
    if (!origin) { out.innerHTML = "<div class='muted'>(no on-orbit object visible to this seat)</div>"; return; }
    const q = new URLSearchParams({ origin });
    const chase = el("ric-chase").value, target = el("ric-target").value;
    if (chase) q.set("chase", chase);
    if (target) q.set("target", target);
    let v;
    try {
      const r = await fetch(`/api/sessions/${SID}/ric_view/${CELL}?${q}`);
      if (!r.ok) { const d = await r.json().catch(() => ({})); out.innerHTML = `<div class='red'>${escH(d.detail || r.statusText)}</div>`; return; }
      v = await r.json();
    } catch (e) { out.innerHTML = `<div class='red'>${escH(e.message)}</div>`; return; }
    const rows = v.objects.map((o) => `<tr><td>${escH(o.id)}${o.source === "track" ? " <span class='muted'>(track)</span>" : ""}</td>` +
      `<td>${(o.ric_r[0] / 1000).toFixed(2)}</td><td>${(o.ric_r[1] / 1000).toFixed(2)}</td><td>${(o.ric_r[2] / 1000).toFixed(2)}</td>` +
      `<td>${(o.range_m / 1000).toFixed(2)}</td></tr>`).join("");
    const cats = v.cats
      ? `<div class="ric-cats">CATS phase angle (${escH(v.cats.chase)} → ${escH(v.cats.target)}): <b>${v.cats.phase_angle_deg.toFixed(1)}°</b>
         <span class="muted">— 0° front-lit · 90° side-lit · 180° backlit</span></div>`
      : `<div class="muted ric-cats">Select both a chase and a target for the CATS phase angle.</div>`;
    out.innerHTML = plot(v.objects) + cats +
      `<table class="ric-table"><thead><tr><th>Object</th><th>R km</th><th>I km</th><th>C km</th><th>Range km</th></tr></thead>
       <tbody>${rows || "<tr><td colspan='5' class='muted'>(no other objects visible)</td></tr>"}</tbody></table>`;
  }

  function open() {
    const p = el("ric-panel"); if (!p) return;
    p.classList.add("open");
    poll();
    if (!timer) timer = setInterval(poll, POLL_MS);
  }
  function close() {
    const p = el("ric-panel"); if (p) p.classList.remove("open");
    if (timer) { clearInterval(timer); timer = null; }
  }

  addEventListener("DOMContentLoaded", () => {
    const b = el("ric-open");
    if (b) b.addEventListener("click", () => (el("ric-panel").classList.contains("open") ? close() : open()));
    const c = el("ric-close"); if (c) c.addEventListener("click", close);
    ["ric-origin", "ric-chase", "ric-target"].forEach((id) => { const s = el(id); if (s) s.addEventListener("change", poll); });
  });
})();
