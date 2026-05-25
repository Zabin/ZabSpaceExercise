"use strict";
// Thin client over the SessionAPI. Renders only the fog-filtered view/scene for the active cell;
// the browser never touches the engine. Owns the command menu and the 2D belief map + controls.

let SID = null, CELL = "white", SCENE = null;
let ASSETS = {};           // id -> {kind, owner} for the current view (assets + sensors)
let DEFAULT_STATION = "GS-NORTH";
const mapCam = { lon: 0, lat: 0, zoom: 1, tracks: true, grid: true };

const $ = (id) => document.getElementById(id);
const api = {
  async get(p) { const r = await fetch(p); if (!r.ok) throw new Error(await r.text()); return r.json(); },
  async post(p, b) { const r = await fetch(p, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(b || {}) }); if (!r.ok) throw new Error(await r.text()); return r.json(); },
};
const iso = (m) => m == null ? "—" : new Date(m / 1000).toISOString().replace(".000Z", "Z");

// Legal actions per asset kind (from 05-cell-interfaces.md) + a starting parameter template.
const ACTIONS_BY_KIND = {
  satellite: ["downlink", "maneuver"], jammer: ["jam"], interceptor: ["engage"],
  cyber_unit: ["cyber"], directed_energy: ["jam"],
  ground_radar: ["observe"], ground_optical: ["observe"], space_based: ["observe"],
};
const PARAM_TEMPLATE = {
  downlink: () => ({ via: DEFAULT_STATION }),
  maneuver: () => ({ dv: [0, 5, 0], via: DEFAULT_STATION }),
  jam: () => ({ success_prob: 1.0, outcome: "deny" }),
  engage: () => ({}),
  cyber: () => ({ access_vector: "ground_modem", outcome: "safe_mode", success_prob: 1.0 }),
  observe: () => ({ intent: "characterize" }),
};

async function loadVignettes() {
  const list = await api.get("/api/vignettes");
  $("vignette").innerHTML = list.map((v) => `<option value="${v.id}">${v.title}</option>`).join("");
}
async function loadSession() {
  SID = (await api.post("/api/sessions", { vignette_id: $("vignette").value, seed: +$("seed").value })).session;
  $("session").textContent = "session " + SID; $("start").disabled = false; await refresh();
}
const start = async () => { await api.post(`/api/sessions/${SID}/start`); await refresh(); };
const step = async (dt) => { await api.post(`/api/sessions/${SID}/step`, { dt_sim_s: dt }); await refresh(); };
const rewind = async () => { await api.post(`/api/sessions/${SID}/rewind`, { t: 0 }); await refresh(); };
async function fireInject() {
  const id = prompt("Inject id:", "commercial_imagery_leak"); if (!id) return;
  await api.post(`/api/sessions/${SID}/inject`, { inject: id }); await refresh();
}

function setCell(c) {
  CELL = c;
  document.querySelectorAll(".cell").forEach((b) => b.classList.toggle("active", b.dataset.cell === c));
  refresh();
}

async function issueOrder() {
  let params; try { params = JSON.parse($("o-params").value || "{}"); } catch { $("order-result").textContent = "Invalid params JSON"; return; }
  const actor = $("o-actor").value;
  const cell = CELL === "white" ? (ASSETS[actor]?.owner || "blue") : CELL;
  const ack = await api.post(`/api/sessions/${SID}/order`, { cell, actor, action: $("o-action").value, target: $("o-target")?.value || null, params });
  $("order-result").textContent = ack.ok
    ? `${ack.status} · ${ack.delivery_path || "—"} · window ${ack.earliest_window ? iso(ack.earliest_window[0]) : "n/a"}`
    : `REJECTED: ${ack.reason}`;
  await refresh();
}

function onActorChange() {
  const a = ASSETS[$("o-actor").value] || {};
  $("actor-info").textContent = a.kind ? `${a.kind} · ${a.owner}` : "";
  const acts = ACTIONS_BY_KIND[a.kind] || ["observe"];
  $("o-action").innerHTML = acts.map((x) => `<option>${x}</option>`).join("");
  onActionChange();
}
function onActionChange() {
  const tmpl = PARAM_TEMPLATE[$("o-action").value]; if (tmpl) $("o-params").value = JSON.stringify(tmpl());
}

async function refresh() {
  if (!SID) return;
  let assets, tracks, effects, messages, objectives;
  if (CELL === "white") {
    const g = await api.get(`/api/sessions/${SID}/godview`);
    $("now").textContent = iso(g.now);
    assets = Object.values(g.assets); tracks = g.tracks;
    effects = (g.active_effects || []).map((e) => ({ target: e.target, symptom: e.outcome, attributed: true }));
    messages = g.messages || []; objectives = await api.get(`/api/sessions/${SID}/objectives`);
    Object.values(g.sensors || {}).forEach((s) => assets.push(s));
  } else {
    const v = await api.get(`/api/sessions/${SID}/view/${CELL}`);
    $("now").textContent = iso(v.now);
    assets = v.own_assets.concat(v.own_sensors); tracks = v.known_tracks;
    effects = v.visible_effects; messages = v.messages; objectives = v.objectives;
  }
  ASSETS = {}; assets.forEach((a) => ASSETS[a.id] = { kind: a.kind, owner: a.owner });
  const station = assets.find((a) => a.kind === "ground_station"); if (station) DEFAULT_STATION = station.id;

  $("assets").querySelector("tbody").innerHTML = assets.map((a) => {
    const bus = a.bus_state ? a.bus_state.mode : "—"; const bc = bus === "safe_mode" ? "red" : "";
    return `<tr><td>${a.id}</td><td>${a.kind}</td><td>${a.health || "—"}</td><td class="${bc}">${bus}</td></tr>`;
  }).join("");
  $("tracks").querySelector("tbody").innerHTML = tracks.map((t) =>
    `<tr><td>${t.object}</td><td>${(+t.confidence).toFixed(2)}</td><td>${t.characterized}</td><td>${t.classification}</td></tr>`).join("");
  $("effects").innerHTML = effects.map((e) => `<li>${e.target}: ${e.symptom} ${e.attributed ? "(attributed)" : "(source unknown)"}</li>`).join("");
  $("messages").innerHTML = messages.map((m) => `<li>${m.text}</li>`).join("");
  $("objectives").textContent = JSON.stringify(objectives, null, 2);

  // Command menu: populate actor list (own assets + sensors that can act).
  const actorIds = assets.filter((a) => ACTIONS_BY_KIND[a.kind]).map((a) => a.id);
  const prev = $("o-actor").value;
  $("o-actor").innerHTML = actorIds.map((i) => `<option>${i}</option>`).join("");
  if (actorIds.includes(prev)) $("o-actor").value = prev;
  onActorChange();

  // Viewers.
  SCENE = await api.get(`/api/sessions/${SID}/scene/${CELL === "white" ? "blue" : CELL}`);
  window.Globe && Globe.render(SCENE);
  ["g-focus", "m-focus"].forEach((id) => {
    const sel = $(id); if (!sel) return; const cur = sel.value;
    const ids = SCENE.assets.map((a) => a.id).concat(SCENE.tracks.map((t) => t.object));
    sel.innerHTML = `<option value="">—</option>` + ids.map((i) => `<option>${i}</option>`).join("");
    if (ids.includes(cur)) sel.value = cur;
  });
  drawMap();
}

// ---- 2D belief map with pan / zoom / center / layers ----
function drawMap() {
  if (!SCENE) return;
  const c = $("map"), x = c.getContext("2d");
  x.fillStyle = "#070b10"; x.fillRect(0, 0, c.width, c.height);
  const PX = (lon) => c.width / 2 + (lon - mapCam.lon) * (c.width / 360) * mapCam.zoom;
  const PY = (lat) => c.height / 2 - (lat - mapCam.lat) * (c.height / 180) * mapCam.zoom;
  if (mapCam.grid) {
    x.strokeStyle = "#1b2531";
    for (let lon = -180; lon <= 180; lon += 30) { x.beginPath(); x.moveTo(PX(lon), 0); x.lineTo(PX(lon), c.height); x.stroke(); }
    for (let lat = -90; lat <= 90; lat += 30) { x.beginPath(); x.moveTo(0, PY(lat)); x.lineTo(c.width, PY(lat)); x.stroke(); }
  }
  x.fillStyle = "#6fcf6f";
  SCENE.assets.forEach((a) => {
    const px = PX(a.lon_deg), py = PY(a.lat_deg);
    if (a.on_orbit) { x.beginPath(); x.moveTo(px, py - 5); x.lineTo(px - 5, py + 4); x.lineTo(px + 5, py + 4); x.closePath(); x.fill(); }
    else x.fillRect(px - 4, py - 4, 8, 8);
    x.fillStyle = "#9fb0c0"; x.font = "11px monospace"; x.fillText(a.id, px + 7, py + 3); x.fillStyle = "#6fcf6f";
  });
  if (mapCam.tracks) SCENE.tracks.forEach((t) => {
    const px = PX(t.lon_deg), py = PY(t.lat_deg), r = Math.max(4, Math.min(40, t.uncertainty_km / 18));
    x.strokeStyle = t.characterized ? "#e0c24a" : "#e06a6a";
    x.beginPath(); x.arc(px, py, r, 0, 2 * Math.PI); x.stroke();
    x.fillStyle = x.strokeStyle; x.beginPath(); x.arc(px, py, 2, 0, 2 * Math.PI); x.fill();
    x.fillStyle = "#9fb0c0"; x.fillText(`${t.object} ±${t.uncertainty_km}km`, px + 6, py - 6);
  });
}

function initMapControls() {
  const c = $("map"); if (!c) return; let drag = null;
  c.addEventListener("mousedown", (e) => drag = { x: e.clientX, y: e.clientY });
  window.addEventListener("mouseup", () => drag = null);
  window.addEventListener("mousemove", (e) => {
    if (!drag) return;
    mapCam.lon -= (e.clientX - drag.x) / (c.width / 360) / mapCam.zoom;
    mapCam.lat += (e.clientY - drag.y) / (c.height / 180) / mapCam.zoom;
    drag = { x: e.clientX, y: e.clientY }; drawMap();
  });
  c.addEventListener("wheel", (e) => { e.preventDefault(); mapCam.zoom = Math.max(0.5, Math.min(8, mapCam.zoom * (e.deltaY < 0 ? 1.1 : 0.9))); drawMap(); });
  $("m-zoom-in").onclick = () => { mapCam.zoom = Math.min(8, mapCam.zoom * 1.2); drawMap(); };
  $("m-zoom-out").onclick = () => { mapCam.zoom = Math.max(0.5, mapCam.zoom / 1.2); drawMap(); };
  $("m-reset").onclick = () => { Object.assign(mapCam, { lon: 0, lat: 0, zoom: 1 }); drawMap(); };
  $("m-tracks").onchange = (e) => { mapCam.tracks = e.target.checked; drawMap(); };
  $("m-grid").onchange = (e) => { mapCam.grid = e.target.checked; drawMap(); };
  $("m-focus").onchange = (e) => {
    const a = SCENE && (SCENE.assets.find((z) => z.id === e.target.value) || SCENE.tracks.find((z) => z.object === e.target.value));
    if (a) { mapCam.lon = a.lon_deg; mapCam.lat = a.lat_deg; mapCam.zoom = Math.max(mapCam.zoom, 2.5); drawMap(); }
  };
}

window.addEventListener("DOMContentLoaded", () => {
  window.Globe && Globe.init("globe");
  initMapControls();
  $("load").onclick = loadSession; $("start").onclick = start; $("rewind").onclick = rewind;
  $("fire-inject").onclick = fireInject; $("issue").onclick = issueOrder;
  $("o-actor").onchange = onActorChange; $("o-action").onchange = onActionChange;
  document.querySelectorAll("[data-step]").forEach((b) => b.onclick = () => step(+b.dataset.step));
  document.querySelectorAll(".cell").forEach((b) => b.onclick = () => setCell(b.dataset.cell));
  setCell("white"); loadVignettes();
});
