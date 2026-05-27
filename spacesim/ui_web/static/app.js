"use strict";
// Thin client over the SessionAPI. Renders only the fog-filtered view/scene for the active cell;
// the browser never touches the engine. Owns the command menu and the 2D belief map + controls.

let SID = null, CELL = "white", SCENE = null;
let ASSETS = {};           // id -> {kind, owner} for the current view (assets + sensors)
let DEFAULT_STATION = "GS-NORTH";
const mapCam = { lon: 0, lat: 0, zoom: 1, tracks: true, grid: true, map: true };
let DRILL = { asset: null, param: null };
let FLEET_FILTER = "all";
let NEXT = {};   // asset id -> next-contact sim-time (µs) for the fleet-rail countdown
let ALARMS = []; // latest alarm feed (shared by the fleet badge + the alarm list)

// Format a next-contact countdown; color amber < 5 min, red < 1 min (P1 — imminent windows draw the eye).
function countdown(now, t) {
  if (t == null) return { txt: "—", cls: "muted" };
  const s = Math.max(0, Math.round((t - now) / 1e6));
  if (s === 0) return { txt: "live", cls: "green" };
  const txt = `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
  return { txt, cls: s < 60 ? "red" : s < 300 ? "yellow" : "" };
}

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
  // Bus/payload verbs (action "command") — plan to the next command window like any uplink.
  "eps.shed_load": () => ({ via: DEFAULT_STATION }),
  "eps.restore_load": () => ({ via: DEFAULT_STATION }),
  "eps.set_charge_mode": () => ({ via: DEFAULT_STATION, mode: "fast" }),
  "adcs.set_mode": () => ({ via: DEFAULT_STATION, mode: "nominal" }),
  "cdh.dump_storage": () => ({ via: DEFAULT_STATION }),
  "satcom.mitigate_interference": () => ({ via: DEFAULT_STATION }),
  "satcom.shift_users": () => ({ via: DEFAULT_STATION }),
  "isr.collect_now": () => ({ via: DEFAULT_STATION }),
  "isr.schedule_collection": () => ({ via: DEFAULT_STATION }),
};

// Plain-language tooltips for the engine's own validator reason strings (OPERATOR-UI-DESIGN.md §12.2).
// Keys mirror OrderSystem._validate verbatim so UI and engine never drift.
const REASON_TIPS = {
  no_window: "No access window in the planning horizon — wait for the next pass.",
  no_command_station: "No command path — set a ground station ('via') or a stored-program time.",
  no_downlink_station: "No downlink station — set a ground station ('via').",
  roe_kinetic_not_authorized: "ROE does not authorize kinetic effects.",
  roe_cyber_not_authorized: "ROE does not authorize cyber effects.",
  no_weapons_quality_track: "No weapons-quality track — task a sensor to characterize the target first.",
  no_ammo: "No munitions remaining on this effector.",
  insufficient_delta_v: "Insufficient delta-v for this maneuver.",
  not_owner: "This asset belongs to another cell.",
  no_such_asset: "Unknown asset.",
  no_such_sensor: "Unknown sensor.",
  sensor_contended: "Sensor is busy — it can service this only at a later window.",
  unknown_action: "Action not supported for this asset.",
  unknown_command: "Command verb not supported.",
  no_payload_for_verb: "This asset's payload can't run that command.",
  payload_unavailable: "Payload unavailable — bus is safed or power-red (clear that first).",
};

async function loadVignettes() {
  const list = await api.get("/api/vignettes");
  $("vignette").innerHTML = list.map((v) => `<option value="${v.id}">${v.title}</option>`).join("");
}
async function loadSession() {
  SID = (await api.post("/api/sessions", { vignette_id: $("vignette").value, seed: +$("seed").value })).session;
  $("session").textContent = "session " + SID; $("start").disabled = false;
  const injects = await api.get(`/api/sessions/${SID}/injects`).catch(() => []);
  $("inject-sel").innerHTML = injects.map((i) => `<option value="${i.id}">${i.label}</option>`).join("") || "<option>(none)</option>";
  await refresh();
}
const start = async () => { await api.post(`/api/sessions/${SID}/start`); await refresh(); };
const step = async (dt) => { await api.post(`/api/sessions/${SID}/step`, { dt_sim_s: dt }); await refresh(); };
const rewind = async () => { await api.post(`/api/sessions/${SID}/rewind`, { t: 0 }); await refresh(); };
async function fireInject() {
  const id = $("inject-sel").value; if (!id || id === "(none)") return;
  await api.post(`/api/sessions/${SID}/inject`, { inject: id }); await refresh();
}

async function renderQueue() {
  const orders = await api.get(`/api/sessions/${SID}/orders/${CELL}`).catch(() => []);
  $("queue").innerHTML = orders.length ? orders.map((o) => {
    const w = o.window ? iso(o.window[0]).slice(11, 19) : "—";
    const cancel = o.status === "queued" ? `<button class="icon" data-oid="${o.id}">✕</button>` : "";
    return `<div class="qrow ${o.status}"><span>${o.actor} ${o.action} ${o.target || ""}</span>` +
           `<span class="muted">${o.status} · ${o.delivery_path || ""} · ${w}</span>${cancel}</div>`;
  }).join("") : "<div class='muted'>(empty)</div>";
  document.querySelectorAll("#queue [data-oid]").forEach((b) => b.onclick = async () => {
    await api.post(`/api/sessions/${SID}/cancel`, { cell: CELL, order_id: b.dataset.oid }); refresh();
  });
}

async function drawRibbon(actor) {
  const c = $("ribbon"), x = c.getContext("2d");
  x.fillStyle = "#0a0f15"; x.fillRect(0, 0, c.width, c.height);
  const wa = await api.get(`/api/sessions/${SID}/windows/${CELL}/${actor}`).catch(() => null);
  if (!wa || !wa.windows.length) { x.fillStyle = "#7a8aa0"; x.font = "11px monospace"; x.fillText("no passes / not a satellite", 8, 26); return; }
  const span = wa.horizon_s * 1e6, now = wa.now;
  const lane = { command_uplink: 6, telemetry_downlink: 24 };
  const col = { command_uplink: "#6fcf6f", telemetry_downlink: "#5a96e6" };
  x.strokeStyle = "#1b2531"; for (let f = 0; f <= 6; f++) { const px = f / 6 * c.width; x.beginPath(); x.moveTo(px, 0); x.lineTo(px, c.height); x.stroke(); }
  wa.windows.forEach((w) => {
    const x0 = (w.start - now) / span * c.width, x1 = (w.end - now) / span * c.width;
    x.fillStyle = col[w.channel] || "#888"; x.fillRect(x0, lane[w.channel] || 14, Math.max(2, x1 - x0), 12);
  });
  x.fillStyle = "#9fb0c0"; x.font = "10px monospace"; x.fillText("uplink", 2, 16); x.fillText("downlink", 2, 34);
}

function setCell(c) {
  CELL = c;
  document.querySelectorAll(".cell").forEach((b) => b.classList.toggle("active", b.dataset.cell === c));
  refresh();
}

// Build the order body from the compose form, or null if params JSON is invalid / no actor.
function composeBody() {
  let params; try { params = JSON.parse($("o-params").value || "{}"); } catch { return null; }
  const actor = $("o-actor").value; if (!actor) return null;
  const cell = CELL === "white" ? (ASSETS[actor]?.owner || "blue") : CELL;
  let action = $("o-action").value;
  // A dotted verb (eps.shed_load, satcom.*) is a bus/payload command carried by the "command" action.
  if (action.includes(".")) { params = { ...params, verb: action }; action = "command"; }
  return { cell, actor, action, target: $("o-target")?.value || null, params };
}

// Verbs offered for an asset: kind-based core actions + bus verbs for satellites + payload verbs by type.
function actionsFor(a) {
  const acts = (ACTIONS_BY_KIND[a.kind] || ["observe"]).slice();
  if (a.kind === "satellite") {
    acts.push("eps.shed_load", "eps.restore_load", "eps.set_charge_mode", "adcs.set_mode", "cdh.dump_storage");
    if (a.payload === "satcom") acts.push("satcom.mitigate_interference", "satcom.shift_users");
    if (a.payload === "isr_eo" || a.payload === "isr_sar") acts.push("isr.collect_now", "isr.schedule_collection");
  }
  return acts;
}

// Plan-first "why can't I?" preview (P4 / §12): dry-run the composed order on every edit and
// pre-disable Issue with the validator's reason — without mutating session state.
async function previewOrder() {
  const btn = $("issue"), out = $("o-preview");
  if (!SID || !out) return;
  const body = composeBody();
  if (!body) { btn.disabled = true; btn.title = "Fix params JSON"; out.className = "preview bad"; out.textContent = "✗ invalid params JSON"; return; }
  let ack; try { ack = await api.post(`/api/sessions/${SID}/order/validate`, body); } catch { return; }
  if (ack.ok) {
    btn.disabled = false; btn.title = "";
    out.className = "preview ok";
    out.textContent = `✓ will queue · ${ack.delivery_path || "—"} · window ${ack.earliest_window ? iso(ack.earliest_window[0]) : "n/a"}`;
  } else {
    const tip = REASON_TIPS[ack.reason] || ack.reason;
    btn.disabled = true; btn.title = tip;
    out.className = "preview bad";
    out.textContent = `✗ ${tip}`;
  }
}

// Verbs that are irreversible / escalatory get a deliberate consequence confirm (§12.3, P5).
const CONSEQUENCE = {
  engage: "Kinetic, debris-generating strike. Political cost: HIGH. Debris may threaten your own LEO assets.",
};

async function issueOrder() {
  const body = composeBody();
  if (!body) { $("order-result").textContent = "Invalid params JSON"; return; }
  const consequence = CONSEQUENCE[body.action];
  if (consequence && !window.confirm(`${consequence}\n\nProceed with ${body.action} on ${body.target || "target"}?`)) {
    $("order-result").textContent = "cancelled (consequence not confirmed)"; return;
  }
  const ack = await api.post(`/api/sessions/${SID}/order`, body);
  $("order-result").textContent = ack.ok
    ? `${ack.status} · ${ack.delivery_path || "—"} · window ${ack.earliest_window ? iso(ack.earliest_window[0]) : "n/a"}`
    : `REJECTED: ${ack.reason}`;
  await refresh();
}

function onActorChange() {
  const id = $("o-actor").value, a = ASSETS[id] || {};
  $("actor-info").textContent = a.kind ? `${a.kind} · ${a.owner}${a.payload ? " · " + a.payload : ""}` : "";
  $("o-action").innerHTML = actionsFor(a).map((x) => `<option>${x}</option>`).join("");
  onActionChange();
  if (SID && id) drawRibbon(id);
}
function onActionChange() {
  const tmpl = PARAM_TEMPLATE[$("o-action").value]; if (tmpl) $("o-params").value = JSON.stringify(tmpl());
  previewOrder();
}

let REFRESH_SEQ = 0;
async function refresh() {
  if (!SID) return;
  // Supersede guard: a later refresh (e.g. after a cell switch) makes any in-flight earlier one
  // abort before it writes, so a slow godview fetch can't clobber the new cell's fog-filtered view.
  const my = ++REFRESH_SEQ;
  const stale = () => my !== REFRESH_SEQ;
  let assets, tracks, effects, messages, objectives, now;
  if (CELL === "white") {
    const g = await api.get(`/api/sessions/${SID}/godview`);
    now = g.now;
    assets = Object.values(g.assets); tracks = g.tracks;
    effects = (g.active_effects || []).map((e) => ({ target: e.target, symptom: e.outcome, attributed: true }));
    messages = g.messages || []; objectives = await api.get(`/api/sessions/${SID}/objectives`);
    Object.values(g.sensors || {}).forEach((s) => assets.push(s));
  } else {
    const v = await api.get(`/api/sessions/${SID}/view/${CELL}`);
    now = v.now;
    assets = v.own_assets.concat(v.own_sensors); tracks = v.known_tracks;
    effects = v.visible_effects; messages = v.messages; objectives = v.objectives;
  }
  if (stale()) return;
  $("now").textContent = iso(now);
  ASSETS = {}; assets.forEach((a) => ASSETS[a.id] = { kind: a.kind, owner: a.owner, payload: a.payload_state ? a.payload_state.type : null });
  const station = assets.find((a) => a.kind === "ground_station"); if (station) DEFAULT_STATION = station.id;

  // Fleet rail: next-contact countdown + power gauge + alarm badge (§4.1), with a filter bar (§4).
  NEXT = (await api.get(`/api/sessions/${SID}/next_contacts/${CELL}`).catch(() => ({ next: {} }))).next || {};
  ALARMS = await api.get(`/api/sessions/${SID}/alarms/${CELL}`).catch(() => []);
  if (stale()) return;
  const alarmCount = {}; ALARMS.forEach((a) => { if (a.asset && a.asset !== "—") alarmCount[a.asset] = (alarmCount[a.asset] || 0) + 1; });
  renderFleet(assets, alarmCount, now);
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
  const scene = await api.get(`/api/sessions/${SID}/scene/${CELL === "white" ? "blue" : CELL}`);
  if (stale()) return;
  SCENE = scene;
  window.Globe && Globe.render(SCENE);
  if (DRILL.asset) openDrill(DRILL.asset);
  ["g-focus", "m-focus"].forEach((id) => {
    const sel = $(id); if (!sel) return; const cur = sel.value;
    const ids = SCENE.assets.map((a) => a.id).concat(SCENE.tracks.map((t) => t.object));
    sel.innerHTML = `<option value="">—</option>` + ids.map((i) => `<option>${i}</option>`).join("");
    if (ids.includes(cur)) sel.value = cur;
  });
  drawMap();
  renderQueue();
  renderAlarms();
  refreshAAR();
}

function rollup(bus) {
  if (!bus) return "";
  if (bus.mode === "safe_mode") return "red";
  const rank = { green: 0, yellow: 1, red: 2 };
  const subs = [bus.power, bus.attitude, bus.thermal, bus.propulsion, bus.cdh, bus.comms];
  return subs.reduce((w, s) => (s && rank[s.status] > rank[w] ? s.status : w), "green");
}

function fleetPasses(a, soh, bus, alarms) {     // does asset pass the active fleet filter?
  if (FLEET_FILTER === "bus-red") return soh === "red";
  if (FLEET_FILTER === "safed") return bus === "safe_mode";
  if (FLEET_FILTER === "attack") return alarms > 0;
  return true;
}

function renderFleet(assets, alarmCount, now) {
  const rows = assets.map((a) => {
    const bus = a.bus_state ? a.bus_state.mode : "—", bc = bus === "safe_mode" ? "red" : "";
    const soh = rollup(a.bus_state), n = alarmCount[a.id] || 0;
    if (!fleetPasses(a, soh, bus, n)) return "";
    const cd = countdown(now, NEXT[a.id]);
    const soc = a.bus_state ? Math.round(a.bus_state.power.battery_soc * 100) + "%" : "—";
    const badge = n ? `<span class="badge">⚠${n}</span>` : "";
    return `<tr data-asset="${a.id}" style="cursor:pointer"><td class="${soh}">●</td><td>${a.id}</td><td>${a.kind}</td>`
      + `<td class="${cd.cls}">${cd.txt}</td><td>${soc}</td><td class="${bc}">${bus}</td><td>${badge}</td></tr>`;
  }).join("");
  $("assets").querySelector("tbody").innerHTML = rows || `<tr><td colspan="7" class="muted">no assets match filter</td></tr>`;
}

function renderAlarms() {
  // Reuses the feed fetched in refresh(); clicking an alarm deep-links to the asset's drill-down (§4.3).
  $("alarms").innerHTML = ALARMS.length
    ? ALARMS.map((a, i) => `<li class="red alarm-line" data-asset="${a.asset}" data-i="${i}" style="cursor:pointer">${a.asset}: ${a.text}</li>`).join("")
    : "<li class='muted'>(no alarms)</li>";
  document.querySelectorAll("#alarms .alarm-line").forEach((li) => li.onclick = () => {
    const aid = li.dataset.asset; if (aid && aid !== "—") openDrill(aid);
  });
}

async function saveSession() {
  const state = await api.get(`/api/sessions/${SID}/save`);
  const blob = new Blob([JSON.stringify(state)], { type: "application/json" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob); a.download = `${state.vignette_id}-save.json`; a.click();
}
async function loadSaveFile(file) {
  const state = JSON.parse(await file.text());
  SID = (await api.post("/api/sessions/load_save", state)).session;
  $("session").textContent = "session " + SID; $("start").disabled = false;
  const injects = await api.get(`/api/sessions/${SID}/injects`).catch(() => []);
  $("inject-sel").innerHTML = injects.map((i) => `<option value="${i.id}">${i.label}</option>`).join("") || "<option>(none)</option>";
  await refresh();
}

async function refreshAAR() {
  const snap = await api.get(`/api/sessions/${SID}/aar/at`).catch(() => null);
  if (!snap) return;
  const sl = $("aar-slider"); sl.max = snap.n_events; if (+sl.value > snap.n_events) sl.value = snap.n_events;
  aarAt(sl.value);
}
async function aarAt(seq) {
  const snap = await api.get(`/api/sessions/${SID}/aar/at?seq=${seq}`).catch(() => null);
  if (!snap) return;
  $("aar-label").textContent = `event ${snap.seq} / ${snap.n_events} · ${iso(snap.now)} · debris ${snap.debris}`;
  $("aar-obj").textContent = JSON.stringify(snap.objectives, null, 2);
  $("aar-assets").textContent = snap.assets.map((a) => `${a.id}: ${a.health}${a.bus_mode ? " / " + a.bus_mode : ""}`).join("\n");
}

// ---- 2D belief map with pan / zoom / center / layers ----
function drawMap() {
  if (!SCENE) return;
  const c = $("map"), x = c.getContext("2d");
  x.fillStyle = "#070b10"; x.fillRect(0, 0, c.width, c.height);
  const PX = (lon) => c.width / 2 + (lon - mapCam.lon) * (c.width / 360) * mapCam.zoom;
  const PY = (lat) => c.height / 2 - (lat - mapCam.lat) * (c.height / 180) * mapCam.zoom;
  if (mapCam.map && window.WorldMap && WorldMap.ready()) {
    WorldMap.draw(x, (lon, lat) => ({ x: PX(lon), y: PY(lat), front: true }), { maxJump: c.width * 0.5 });
  }
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
  const mm = $("m-map"); if (mm) mm.onchange = (e) => { mapCam.map = e.target.checked; drawMap(); };
  $("m-focus").onchange = (e) => {
    const a = SCENE && (SCENE.assets.find((z) => z.id === e.target.value) || SCENE.tracks.find((z) => z.object === e.target.value));
    if (a) { mapCam.lon = a.lon_deg; mapCam.lat = a.lat_deg; mapCam.zoom = Math.max(mapCam.zoom, 2.5); drawMap(); }
  };
}

// ---- subsystem drill-down (telemetry graphs + log; diagnose, don't get told) ----
let DRILL_DB = {};
async function openDrill(assetId) {
  DRILL.asset = assetId;
  let tele;
  try { tele = await api.get(`/api/sessions/${SID}/telemetry/${CELL}/${assetId}`); }
  catch { $("drill-title").textContent = `${assetId} — no telemetry (fog / not your asset)`; $("drill-params").innerHTML = ""; return; }
  DRILL_DB = {};
  Object.values(tele.subsystems).forEach((arr) => arr.forEach((p) => (DRILL_DB[p.id] = p)));
  $("drill-title").textContent = `${assetId} — bus ${tele.bus_mode || "—"}`;
  $("drill-params").innerHTML = Object.entries(tele.subsystems).map(([sub, params]) =>
    `<div class="sub"><b>${sub}</b> ` + params.map((p) =>
      `<span class="pchip ${p.status}" data-param="${p.id}">${p.label} ${p.value ?? "LOS"}</span>`).join(" ") + "</div>").join("");
  $("drill-log").textContent = (tele.log || []).join("\n") || "(all nominal)";
  document.querySelectorAll("#drill-params .pchip").forEach((c) => c.onclick = () => drawParam(c.dataset.param));
  drawParam(DRILL.param && DRILL_DB[DRILL.param] ? DRILL.param : "rx_power_dbm");
}
async function drawParam(param) {
  if (!DRILL_DB[param]) param = Object.keys(DRILL_DB)[0];
  DRILL.param = param;
  const base = `/api/sessions/${SID}/telemetry/${CELL}/${DRILL.asset}/${param}`;
  const series = await api.get(`${base}?n=120`);
  // Compare-to-nominal (§5.3): overlay the clean baseline so an attack signature reads as deviation.
  const ghost = $("drill-nominal")?.checked
    ? await api.get(`${base}?n=120&nominal=1`).catch(() => null)
    : null;
  window.Graph && Graph.draw($("drill-graph"), series, DRILL_DB[param], ghost);
}

window.addEventListener("DOMContentLoaded", () => {
  window.WorldMap && WorldMap.load().then(() => drawMap());
  window.Globe && Globe.init("globe");
  initMapControls();
  $("assets").addEventListener("click", (e) => { const tr = e.target.closest("tr[data-asset]"); if (tr) openDrill(tr.dataset.asset); });
  $("load").onclick = loadSession; $("start").onclick = start; $("rewind").onclick = rewind;
  $("fire-inject").onclick = fireInject; $("issue").onclick = issueOrder;
  $("save").onclick = () => SID && saveSession();
  $("loadbtn").onclick = () => $("loadfile").click();
  $("loadfile").onchange = (e) => e.target.files[0] && loadSaveFile(e.target.files[0]);
  $("aar-slider").oninput = (e) => aarAt(e.target.value);
  $("o-actor").onchange = onActorChange; $("o-action").onchange = onActionChange;
  $("o-target").oninput = previewOrder; $("o-params").oninput = previewOrder;
  $("drill-nominal").onchange = () => DRILL.param && drawParam(DRILL.param);
  document.querySelectorAll("[data-step]").forEach((b) => b.onclick = () => step(+b.dataset.step));
  document.querySelectorAll(".cell").forEach((b) => b.onclick = () => setCell(b.dataset.cell));
  document.querySelectorAll("#fleet-filter .chip").forEach((b) => b.onclick = () => {
    FLEET_FILTER = b.dataset.filter;
    document.querySelectorAll("#fleet-filter .chip").forEach((c) => c.classList.toggle("active", c === b));
    if (SID) refresh();
  });
  document.addEventListener("keydown", onShortcut);
  setCell("white"); loadVignettes();
});

// Keyboard shortcuts (§12.4): j/k step the selected actor, c focuses compose, g graphs it. Ignored in fields.
function onShortcut(e) {
  if (/^(INPUT|SELECT|TEXTAREA)$/.test(document.activeElement.tagName)) return;
  const sel = $("o-actor"), opts = [...sel.options];
  if (e.key === "j" || e.key === "k") {
    if (!opts.length) return;
    let i = opts.findIndex((o) => o.value === sel.value);
    i = (i + (e.key === "j" ? 1 : opts.length - 1)) % opts.length;
    sel.value = opts[i].value; onActorChange();
  } else if (e.key === "c") { sel.focus(); }
  else if (e.key === "g" && sel.value) { openDrill(sel.value); }
}
