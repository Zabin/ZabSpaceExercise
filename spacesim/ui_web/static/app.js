"use strict";
// Thin client: every action goes through the SessionAPI endpoints; the browser never
// touches the engine and only ever renders the fog-filtered CellView for the active cell.

let SID = null;
let CELL = "white";

const $ = (id) => document.getElementById(id);
const api = {
  async get(path) { const r = await fetch(path); if (!r.ok) throw new Error(await r.text()); return r.json(); },
  async post(path, body) {
    const r = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body || {}) });
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  },
};

function isoFromMicros(micros) {
  if (micros == null) return "—";
  const d = new Date(micros / 1000);
  return d.toISOString().replace(".000Z", "Z");
}

async function loadVignettes() {
  const list = await api.get("/api/vignettes");
  $("vignette").innerHTML = list.map((v) => `<option value="${v.id}">${v.title}</option>`).join("");
}

async function loadSession() {
  const res = await api.post("/api/sessions", { vignette_id: $("vignette").value, seed: Number($("seed").value) });
  SID = res.session;
  $("session").textContent = `session: ${SID}`;
  $("start").disabled = false;
  await refresh();
}

async function start() { await api.post(`/api/sessions/${SID}/start`); await refresh(); }
async function step(dt) { await api.post(`/api/sessions/${SID}/step`, { dt_sim_s: dt }); await refresh(); }

async function rewind() {
  // Rewind to the session's start epoch (the godview's initial 'now' isn't exposed, so use the
  // earliest event or just step the clock back via the view's start — here: reload not needed).
  const god = await api.get(`/api/sessions/${SID}/godview`).catch(() => null);
  // Simplest: rewind to a very early time; the engine clamps to kept events.
  await api.post(`/api/sessions/${SID}/rewind`, { t: 0 });
  await refresh();
}

async function fireInject() {
  const id = prompt("Inject id (e.g. commercial_imagery_leak):", "commercial_imagery_leak");
  if (!id) return;
  await api.post(`/api/sessions/${SID}/inject`, { inject: id });
  await refresh();
}

async function issueOrder() {
  let params = {};
  try { params = JSON.parse($("o-params").value || "{}"); }
  catch (e) { $("order-result").textContent = "Invalid params JSON"; return; }
  const body = { cell: CELL, actor: $("o-actor").value, action: $("o-action").value,
    target: $("o-target").value || null, params };
  const ack = await api.post(`/api/sessions/${SID}/order`, body);
  $("order-result").textContent = ack.ok
    ? `${ack.status} via ${ack.delivery_path || "—"}; window ${ack.earliest_window ? isoFromMicros(ack.earliest_window[0]) : "n/a"}`
    : `REJECTED: ${ack.reason}`;
  await refresh();
}

function setCell(cell) {
  CELL = cell;
  document.querySelectorAll(".cell").forEach((b) => b.classList.toggle("active", b.dataset.cell === cell));
  refresh();
}

function statusClass(s) { return ["green", "yellow", "red"].includes(s) ? s : ""; }

async function refresh() {
  if (!SID) return;
  if (CELL === "white") {
    const god = await api.get(`/api/sessions/${SID}/godview`);
    $("now").textContent = isoFromMicros(god.now);
    renderAssets(Object.values(god.assets));
    renderTracks(god.tracks);
    $("effects").innerHTML = (god.active_effects || []).map((e) => `<li>${e.target}: ${e.outcome}</li>`).join("");
    $("messages").innerHTML = (god.messages || []).map((m) => `<li>${m.text}</li>`).join("");
  } else {
    const view = await api.get(`/api/sessions/${SID}/view/${CELL}`);
    $("now").textContent = isoFromMicros(view.now);
    renderAssets(view.own_assets);
    renderTracks(view.known_tracks);
    $("effects").innerHTML = view.visible_effects.map(
      (e) => `<li>${e.target}: ${e.symptom} ${e.attributed ? "(attributed)" : "(source unknown)"}</li>`).join("");
    $("messages").innerHTML = view.messages.map((m) => `<li>${m.text}</li>`).join("");
  }
  $("objectives").textContent = JSON.stringify(await api.get(`/api/sessions/${SID}/objectives`), null, 2);
  await drawMap();
}

async function drawMap() {
  const cell = CELL === "white" ? "blue" : CELL; // god-view borrows Blue's belief frame for the map
  const scene = await api.get(`/api/sessions/${SID}/scene/${cell}`);
  const c = $("map"), ctx = c.getContext("2d");
  ctx.fillStyle = "#0b0f14"; ctx.fillRect(0, 0, c.width, c.height);
  ctx.strokeStyle = "#1c2531";
  for (let lon = -180; lon <= 180; lon += 30) { const x = (lon + 180) / 360 * c.width; ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, c.height); ctx.stroke(); }
  for (let lat = -90; lat <= 90; lat += 30) { const y = (90 - lat) / 180 * c.height; ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(c.width, y); ctx.stroke(); }
  const px = (lon) => (lon + 180) / 360 * c.width;
  const py = (lat) => (90 - lat) / 180 * c.height;
  // Own assets (known): triangles for on-orbit, squares for ground.
  ctx.fillStyle = "#6fcf6f";
  scene.assets.forEach((a) => {
    const x = px(a.lon_deg), y = py(a.lat_deg);
    ctx.beginPath();
    if (a.on_orbit) { ctx.moveTo(x, y - 5); ctx.lineTo(x - 5, y + 4); ctx.lineTo(x + 5, y + 4); ctx.closePath(); ctx.fill(); }
    else { ctx.fillRect(x - 4, y - 4, 8, 8); }
    ctx.fillStyle = "#9fb0c0"; ctx.font = "11px monospace"; ctx.fillText(a.id, x + 7, y + 3); ctx.fillStyle = "#6fcf6f";
  });
  // Tracks (belief): circle whose radius encodes the growing uncertainty volume.
  scene.tracks.forEach((t) => {
    const x = px(t.lon_deg), y = py(t.lat_deg);
    const r = Math.max(4, Math.min(40, t.uncertainty_km / 20));
    ctx.strokeStyle = t.characterized ? "#e0c24a" : "#e06a6a";
    ctx.globalAlpha = 0.5; ctx.beginPath(); ctx.arc(x, y, r, 0, 2 * Math.PI); ctx.stroke(); ctx.globalAlpha = 1;
    ctx.fillStyle = ctx.strokeStyle; ctx.beginPath(); ctx.arc(x, y, 2, 0, 2 * Math.PI); ctx.fill();
    ctx.fillStyle = "#9fb0c0"; ctx.fillText(`${t.object} ±${t.uncertainty_km}km`, x + 6, y - 6);
  });
}

function renderAssets(assets) {
  $("assets").querySelector("tbody").innerHTML = assets.map((a) => {
    const busMode = a.bus_state ? a.bus_state.mode : "—";
    const cls = busMode === "safe_mode" ? "red" : "";
    return `<tr><td>${a.id}</td><td>${a.kind}</td><td>${a.health}</td><td class="${cls}">${busMode}</td></tr>`;
  }).join("");
}

function renderTracks(tracks) {
  $("tracks").querySelector("tbody").innerHTML = tracks.map(
    (t) => `<tr><td>${t.object}</td><td>${t.confidence.toFixed(2)}</td><td>${t.characterized}</td><td>${t.classification}</td></tr>`
  ).join("");
}

window.addEventListener("DOMContentLoaded", () => {
  $("load").addEventListener("click", loadSession);
  $("start").addEventListener("click", start);
  $("rewind").addEventListener("click", rewind);
  $("fire-inject").addEventListener("click", fireInject);
  $("issue").addEventListener("click", issueOrder);
  document.querySelectorAll("[data-step]").forEach((b) => b.addEventListener("click", () => step(Number(b.dataset.step))));
  document.querySelectorAll(".cell").forEach((b) => b.addEventListener("click", () => setCell(b.dataset.cell)));
  setCell("white");
  loadVignettes();
});
