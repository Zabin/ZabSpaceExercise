"use strict";
// Thin client over the SessionAPI. Renders only the fog-filtered view/scene for the active cell;
// the browser never touches the engine. Owns the command menu and the 2D belief map + controls.

let SID = null, CELL = "white", SCENE = null;
let ASSETS = {};           // id -> {kind, owner} for the current view (assets + sensors)
let DEFAULT_STATION = "GS-NORTH";
const mapCam = { lon: 0, lat: 0, zoom: 1, tracks: true, grid: true, map: true };
let DRILL = { asset: null, param: null };
let FLEET_FILTER = "all";
let NEXT = {};            // asset id -> next-contact sim-time (µs) for the fleet-rail countdown
let ALARMS = [];          // latest alarm feed (shared by the fleet badge + the alarm list)
let EFFECT_WINDOWS = [];  // active-effect time spans on own assets (graph shading, §9.1)
let NOW = 0;              // current sim time captured each refresh (for stale-banner + shading)

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
  "def.patch_cyber": () => ({ via: DEFAULT_STATION, vector: "ground_modem" }),
  "cdh.clear_fault": () => ({ via: DEFAULT_STATION }),
  "tcs.set_mode": () => ({ via: DEFAULT_STATION, mode: "operational" }),
  "tcs.set_heater": () => ({ via: DEFAULT_STATION, on: true }),
  "comms.enable_isl": () => ({ via: DEFAULT_STATION, on: true }),
  "comms.config_link": () => ({ via: DEFAULT_STATION, data_rate_kbps: 2048 }),
  "def.frequency_hop": () => ({ via: DEFAULT_STATION, on: true }),
  "def.harden": () => ({ via: DEFAULT_STATION, on: true }),
  "def.set_threat_warning": () => ({ via: DEFAULT_STATION, on: true }),
  "sigint.task_collection": () => ({ via: DEFAULT_STATION }),
  "wx.schedule_collection": () => ({ via: DEFAULT_STATION }),
  // Stage B verbs
  "cdh.reset_subsystem": () => ({ via: DEFAULT_STATION }),
  "adcs.desaturate": () => ({ via: DEFAULT_STATION }),
  "comms.point_antenna": () => ({ via: DEFAULT_STATION, mode: "earth" }),
  "isr.set_mode": () => ({ via: DEFAULT_STATION, mode: "wide" }),
  "pnt.set_integrity": () => ({ via: DEFAULT_STATION, mode: "standard" }),
  "def.maneuver_evade": () => ({ via: DEFAULT_STATION, dv_cost: 5.0 }),
};

// Verb roles for the §1.2 role selector — drives the Bus/Payload/SDA/All filter on the command menu.
const VERB_ROLE = {
  downlink: "bus", maneuver: "bus", observe: "sda",
  "eps.shed_load": "bus", "eps.restore_load": "bus", "eps.set_charge_mode": "bus",
  "adcs.set_mode": "bus", "adcs.desaturate": "bus",
  "cdh.dump_storage": "bus", "cdh.clear_fault": "bus", "cdh.reset_subsystem": "bus",
  "tcs.set_mode": "bus", "tcs.set_heater": "bus",
  "comms.enable_isl": "bus", "comms.config_link": "bus", "comms.point_antenna": "bus",
  "satcom.mitigate_interference": "payload", "satcom.shift_users": "payload",
  "isr.collect_now": "payload", "isr.schedule_collection": "payload", "isr.set_mode": "payload",
  "sigint.task_collection": "payload", "wx.schedule_collection": "payload",
  "pnt.set_integrity": "payload",
  "def.patch_cyber": "bus", "def.frequency_hop": "bus",
  "def.harden": "payload", "def.set_threat_warning": "bus", "def.maneuver_evade": "bus",
};
let ROLE_FILTER = "all";

// Plain-language tooltips for the engine's own validator reason strings (00-BUILD-SPECIFICATION.md §16.9).
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
  document.body.setAttribute("data-cell", c);    // drives --cell-accent across panels/borders/rows
  document.querySelectorAll(".cell").forEach((b) => b.classList.toggle("active", b.dataset.cell === c));
  if (window.redrawAll) redrawAll();            // re-tint own-asset markers immediately
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
    acts.push("eps.shed_load", "eps.restore_load", "eps.set_charge_mode",
              "adcs.set_mode", "adcs.desaturate",
              "cdh.dump_storage", "cdh.clear_fault", "cdh.reset_subsystem",
              "tcs.set_mode", "tcs.set_heater",
              "comms.enable_isl", "comms.config_link", "comms.point_antenna",
              "def.frequency_hop", "def.harden", "def.set_threat_warning", "def.maneuver_evade");
    if (a.payload === "satcom") acts.push("satcom.mitigate_interference", "satcom.shift_users");
    if (a.payload === "isr_eo" || a.payload === "isr_sar") acts.push("isr.collect_now", "isr.schedule_collection", "isr.set_mode");
    if (a.payload === "sigint") acts.push("sigint.task_collection");
    if (a.payload === "weather") acts.push("wx.schedule_collection");
    if (a.payload === "pnt") acts.push("pnt.set_integrity");
    if ((a.cyber_vulns || []).length) acts.push("def.patch_cyber");      // defender's root-cause fix
  }
  // Role filter (§1.2): All shows everything; Bus/Payload/SDA narrow by VERB_ROLE.
  if (ROLE_FILTER !== "all") return acts.filter((v) => (VERB_ROLE[v] || "bus") === ROLE_FILTER);
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
  cyber: "Cyber effect. Covert but escalatory; ROE-gated; persistence and re-safe risk if root cause persists.",
};

// Dedicated tasking rail (§7.4, P-UI-6): Organic posts /order with action=observe; SSN posts
// /ssn/{cell}/request and shows the cell's SSN request queue + a coverage preview line.
let TASK_MODE = "organic";

async function planTask() {
  const target = $("task-target").value || $("o-target").value;
  if (!SID || !target) { $("task-result").textContent = "Pick a target (track id)."; return; }
  const cell = CELL === "white" ? "blue" : CELL;
  if (TASK_MODE === "ssn") {
    const body = { intent: $("task-intent").value, target, regime: $("task-regime").value,
                   priority: $("task-priority").value };
    const ack = await api.post(`/api/sessions/${SID}/ssn/${cell}/request`, body);
    $("task-result").textContent = ack.ok
      ? `${ack.state} · ${ack.assigned_sensor} · collect ${iso(ack.collect_at)} → product ${iso(ack.product_at)}`
      : `FAILED: ${ack.reason}`;
    await renderSsnQueue(cell);
    return;
  }
  const body = { cell, actor: $("task-sensor").value, action: "observe", target,
                 params: { intent: $("task-intent").value, priority: $("task-priority").value } };
  const ack = await api.post(`/api/sessions/${SID}/order`, body);
  $("task-result").textContent = ack.ok
    ? `${ack.status} · ${ack.delivery_path || "—"} · window ${ack.earliest_window ? iso(ack.earliest_window[0]) : "n/a"}`
    : `REJECTED: ${ack.reason}`;
  await refresh();
}

async function ssnCoverage() {
  if (!SID || TASK_MODE !== "ssn") { $("task-coverage").textContent = ""; return; }
  const cell = CELL === "white" ? "blue" : CELL;
  const regime = $("task-regime").value;
  try {
    const c = await api.get(`/api/sessions/${SID}/ssn/${cell}/coverage?regime=${regime}`);
    if (!c.sensors || !c.sensors.length) {
      $("task-coverage").className = "preview bad";
      $("task-coverage").textContent = `✗ ${cell.toUpperCase()}-SSN has no eligible sensor for ${regime} (no network or wrong phenomenology).`;
    } else {
      $("task-coverage").className = "preview ok";
      $("task-coverage").textContent = `✓ ${c.affiliation || ""} · ${c.dispersion || ""} · ${c.sensors.length} eligible sensor(s) for ${regime} (concurrency ${c.concurrency || "?"}).`;
    }
  } catch { $("task-coverage").textContent = ""; }
}

async function renderSsnQueue(cell) {
  if (!SID) return;
  const list = await api.get(`/api/sessions/${SID}/ssn/${cell}/requests`).catch(() => []);
  if (!list.length) { $("ssn-queue").innerHTML = "<span class='muted'>(empty)</span>"; return; }
  $("ssn-queue").innerHTML = list.map((r) => {
    const cancel = r.state === "SCHEDULED"
      ? `<button class="vbtn" data-rid="${r.id}">✕</button>` : "";
    const win = r.collect_at ? `collect ${iso(r.collect_at)} → product ${iso(r.product_at)}` : (r.reason || "");
    return `<div class="qrow ${r.state.toLowerCase()}"><span>${r.id} ${r.intent} ${r.target} ${r.regime} ${r.priority}</span><span>${r.state}</span><span>${win}</span>${cancel}</div>`;
  }).join("");
  document.querySelectorAll("#ssn-queue .vbtn").forEach((b) => b.onclick = async () => {
    await api.post(`/api/sessions/${SID}/ssn/${cell}/cancel`, { request_id: b.dataset.rid });
    renderSsnQueue(cell);
  });
}

function setTaskMode(m) {
  TASK_MODE = m;
  document.querySelectorAll("#task-mode .chip").forEach((c) => c.classList.toggle("active", c.dataset.tmode === m));
  $("task-sensor-wrap").style.display = (m === "ssn") ? "none" : "";
  $("task-regime-wrap").style.display = (m === "ssn") ? "" : "none";
  $("task-coverage").textContent = "";
  if (m === "ssn" && SID) { ssnCoverage(); renderSsnQueue(CELL === "white" ? "blue" : CELL); }
}

// Multi-display reflow (§3.3 / P-UI-8): pop the 3D globe + 2D map into a second window for
// projector / dual-screen setups. The detached window reads its initial scene via postMessage and
// re-fetches on a slow tick so it stays in sync — no engine change, no shared state.
function detachViewers() {
  const w = window.open("", "viewers", "width=1100,height=720");
  if (!w) return;
  w.document.title = "spacesim viewers";
  w.document.body.style.cssText = "margin:0;background:#0a0f15;color:#9fb0c0;font-family:monospace";
  w.document.body.innerHTML = `<canvas id="d-globe" width="560" height="400" style="background:#0a0f15"></canvas>
    <canvas id="d-map" width="560" height="400" style="background:#0a0f15"></canvas>
    <div id="d-status" style="position:absolute;top:8px;right:12px;font-size:11px;opacity:.6">detached · syncing…</div>`;
  const tick = async () => {
    if (w.closed) return;
    try {
      const sc = await api.get(`/api/sessions/${SID}/scene/${CELL === "white" ? "blue" : CELL}`);
      // Draw a minimal 2D belief layer using the primary's WorldMap projection.
      const ctx = w.document.getElementById("d-map").getContext("2d");
      ctx.fillStyle = "#0a0f15"; ctx.fillRect(0, 0, 560, 400);
      ctx.fillStyle = "#9fb0c0"; ctx.font = "10px monospace";
      sc.assets.forEach((a) => {
        const x = (a.lon_deg + 180) / 360 * 560, y = (90 - a.lat_deg) / 180 * 400;
        ctx.fillStyle = a.owner === "blue" ? "#5a8fe0" : a.owner === "red" ? "#e06a6a" : "#9fb0c0";
        ctx.fillRect(x - 2, y - 2, 4, 4);
        ctx.fillStyle = "#9fb0c0"; ctx.fillText(a.id, x + 4, y + 3);
      });
      w.document.getElementById("d-status").textContent = `detached · ${iso(sc.now)} · ${sc.assets.length} assets`;
    } catch { /* primary may have unloaded */ }
    setTimeout(tick, 2000);
  };
  tick();
}

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
  let assets, tracks, effects, messages, objectives, now, ewin;
  if (CELL === "white") {
    const g = await api.get(`/api/sessions/${SID}/godview`);
    now = g.now;
    assets = Object.values(g.assets); tracks = g.tracks;
    effects = (g.active_effects || []).map((e) => ({ target: e.target, symptom: e.outcome, attributed: true }));
    ewin = (g.active_effects || []).map((e) => ({ target: e.target, category: e.category || "", start: e.start, end: e.end, attributed: true }));
    messages = g.messages || []; objectives = await api.get(`/api/sessions/${SID}/objectives`);
    Object.values(g.sensors || {}).forEach((s) => assets.push(s));
  } else {
    const v = await api.get(`/api/sessions/${SID}/view/${CELL}`);
    now = v.now;
    assets = v.own_assets.concat(v.own_sensors); tracks = v.known_tracks;
    effects = v.visible_effects; ewin = v.effect_windows || [];
    messages = v.messages; objectives = v.objectives;
  }
  if (stale()) return;
  NOW = now;
  $("now").textContent = iso(now);
  EFFECT_WINDOWS = ewin;
  ASSETS = {}; assets.forEach((a) => ASSETS[a.id] = {
    kind: a.kind, owner: a.owner,
    payload: a.payload_state ? a.payload_state.type : null,
    payload_health: a.payload_state ? a.payload_state.health : null,
    last_tel: a.bus_state ? a.bus_state.last_telemetry_time : null,
    cyber_vulns: a.cyber_vulnerabilities || [],
    network: !!a.network,    // SSN sensors are request-only (filtered from organic pickers)
  });
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

  // Command menu: populate actor list (own assets + sensors that can act; network sensors excluded).
  const actorIds = assets.filter((a) => ACTIONS_BY_KIND[a.kind] && !a.network).map((a) => a.id);
  const prev = $("o-actor").value;
  $("o-actor").innerHTML = actorIds.map((i) => `<option>${i}</option>`).join("");
  if (actorIds.includes(prev)) $("o-actor").value = prev;
  onActorChange();
  // Tasking rail sensor picker (P-UI-6): own organic sensors + auto (network sensors are SSN-only).
  const tsel = $("task-sensor");
  if (tsel) {
    const cur = tsel.value;
    const sids = assets.filter((a) => !a.network && ((a.kind && a.kind.startsWith("ground_")) || a.kind === "space_based")).map((a) => a.id);
    tsel.innerHTML = `<option value="auto">auto</option>` + sids.map((i) => `<option>${i}</option>`).join("");
    if (cur && (cur === "auto" || sids.includes(cur))) tsel.value = cur;
  }

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
  if (TASK_MODE === "ssn") { ssnCoverage(); renderSsnQueue(CELL === "white" ? "blue" : CELL); }
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
  if (FLEET_FILTER === "payload") return a.payload_state && a.payload_state.health && a.payload_state.health !== "green";
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
    const sel = DRILL.asset === a.id ? " selected" : "";   // cell-accent highlight for the drilled row
    return `<tr data-asset="${a.id}" class="${sel.trim()}" style="cursor:pointer"><td class="${soh}">●</td><td>${a.id}</td><td>${a.kind}</td>`
      + `<td class="${cd.cls}">${cd.txt}</td><td>${soc}</td><td class="${bc}">${bus}</td><td>${badge}</td></tr>`;
  }).join("");
  $("assets").querySelector("tbody").innerHTML = rows || `<tr><td colspan="7" class="muted">no assets match filter</td></tr>`;
  if (window.batchRender) batchRender();    // re-apply .batched class after the rows re-render
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
  if (window.refreshAarLinks) refreshAarLinks();      // §10.E.20 — keep CSV/JSON download href live
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
  // §10.C.10 — terminator overlay (computed from sun_lat/lon already in SceneView).
  if (SCENE.sun_lat_deg != null && window.drawTerminator) {
    window.drawTerminator(x, c, PX, PY, SCENE.sun_lat_deg, SCENE.sun_lon_deg);
  }
  // §10.A.1 — own-asset marker color tracks the active cell's accent.
  const accent = window.cellAccent ? cellAccent() : "#6fcf6f";
  x.fillStyle = accent;
  SCENE.assets.forEach((a) => {
    const px = PX(a.lon_deg), py = PY(a.lat_deg);
    if (a.on_orbit) { x.beginPath(); x.moveTo(px, py - 5); x.lineTo(px - 5, py + 4); x.lineTo(px + 5, py + 4); x.closePath(); x.fill(); }
    else x.fillRect(px - 4, py - 4, 8, 8);
    x.fillStyle = "#9fb0c0"; x.font = "11px monospace"; x.fillText(a.id, px + 7, py + 3); x.fillStyle = accent;
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
  // Pass-gated telemetry semantics (§5.4): show "as-of HH:MM:SS" / stale-since when out of contact.
  const lt = ASSETS[assetId]?.last_tel || 0;
  const ageS = lt > 0 ? Math.max(0, Math.round((NOW - lt) / 1e6)) : null;
  const staleTag = (ageS != null && ageS > 60)
    ? ` · <span class="muted">stale since ${iso(lt)} (${Math.floor(ageS / 60)}m)</span>`
    : (ageS != null ? ` · <span class="muted">as-of ${iso(lt)}</span>` : "");
  $("drill-title").innerHTML = `${assetId} — bus ${tele.bus_mode || "—"}${staleTag}`;
  // Populate the overlay-param selector for this asset's params (Compare-to-nominal toggled separately).
  const overlaySel = $("drill-overlay");
  if (overlaySel) {
    const prev = overlaySel.value;
    const opts = ['<option value="">(no overlay)</option>'].concat(
      Object.values(tele.subsystems).flat().map((p) => `<option value="${p.id}">${p.label}</option>`));
    overlaySel.innerHTML = opts.join("");
    if (prev) overlaySel.value = prev;
  }
  // Each subsystem card carries its parameter chips (→ graph) and its command verbs (→ compose).
  const a = ASSETS[assetId] || {};
  $("drill-params").innerHTML = Object.entries(tele.subsystems).map(([sub, params]) => {
    const chips = params.map((p) =>
      `<span class="pchip ${p.status}" data-param="${p.id}" data-acronym="${(p.label || "").split(" ")[0]}">${p.label} ${p.value ?? "LOS"}` +
      ` <canvas class="spark" data-param="${p.id}" width="48" height="12"></canvas></span>`).join(" ");
    const verbs = verbsForSubsystem(a, sub).map((v) =>
      `<button class="vbtn" data-verb="${v}" data-actor="${assetId}">${v}</button>`).join(" ");
    return `<div class="sub"><b data-acronym="${sub.toUpperCase()}">${sub}</b> ${chips}${verbs ? `<div class="vbtns">${verbs}</div>` : ""}</div>`;
  }).join("");
  // §10.A.4 — diff-pulse: if a value changed since the last drill render, flash that pchip.
  document.querySelectorAll("#drill-params .pchip").forEach((chip) => {
    const pid = chip.dataset.param;
    const par = Object.values(tele.subsystems).flat().find((p) => p.id === pid);
    if (par) window.maybePulse && maybePulse(chip, assetId + ":" + pid, par.value);
  });
  // Tiny inline sparklines (§5.1) — one short series per param chip; ignore failures silently.
  document.querySelectorAll("#drill-params .spark").forEach(async (cv) => {
    try {
      const s = await api.get(`/api/sessions/${SID}/telemetry/${CELL}/${assetId}/${cv.dataset.param}?n=30`);
      window.Graph && Graph.spark(cv, s, DRILL_DB[cv.dataset.param]);
    } catch { /* offline param — silent */ }
  });
  $("drill-log").textContent = (tele.log || []).join("\n") || "(all nominal)";
  document.querySelectorAll("#drill-params .pchip").forEach((c) => c.onclick = () => drawParam(c.dataset.param));
  document.querySelectorAll("#drill-params .vbtn").forEach((b) => b.onclick = () => loadVerb(b.dataset.actor, b.dataset.verb));
  renderRecovery(assetId, tele.bus_mode);
  drawParam(DRILL.param && DRILL_DB[DRILL.param] ? DRILL.param : "rx_power_dbm");
}

// Safe-mode recovery strip (§5.5): the guided multi-pass chain + a "begin recovery" action.
async function renderRecovery(assetId, busMode) {
  const strip = $("recovery-strip");
  if (busMode !== "safe_mode") { strip.innerHTML = ""; return; }
  const st = await api.get(`/api/sessions/${SID}/recovery/${CELL}/${assetId}`).catch(() => null);
  if (!st) { strip.innerHTML = ""; return; }
  const done = st.confirmed;   // confirmation is the first pass; later steps complete on finish
  const steps = st.steps.map((s, i) =>
    `<span class="rstep ${done && i === 0 ? "ok" : ""}">${i + 1}.${s}</span>`).join(" → ");
  // Any unpatched cyber vulnerability on this safed asset → surface a one-click deep-link to
  // def.patch_cyber pre-filled with the vector, so the operator can clear the root cause and make
  // recovery stick. The op may patch pre-emptively (before diagnosis) or after the re-safe.
  const cyberVuln = (ASSETS[assetId]?.cyber_vulns || []).find((v) => !v.patched) || null;
  const patchLink = cyberVuln
    ? ` <button class="vbtn" id="rec-patch" data-vector="${cyberVuln.vector}">Patch (def.patch_cyber)</button>`
    : "";
  const blocked = st.blocked_reason
    ? `<div class="red">⚠ ${st.blocked_reason} — remove the root cause (patch the vector / kill the jammer), then recover again.</div>`
    : "";
  strip.innerHTML = `<div class="recovery">
    <b class="red">SAFE MODE</b> · diagnosis: ${st.diagnosis} · passes ${st.passes_used}/${st.passes_needed}
    <button class="vbtn" id="rec-begin" data-asset="${assetId}">Begin recovery</button>${patchLink}
    <div class="rsteps">${steps}</div>${blocked}</div>`;
  $("rec-begin").onclick = async () => {
    const r = await api.post(`/api/sessions/${SID}/recovery/${CELL}/${assetId}`, { via: DEFAULT_STATION });
    $("rec-begin").textContent = r.ok ? `recovery scheduled (${r.passes_used} pass${r.passes_used > 1 ? "es" : ""})` : `cannot start: ${r.reason}`;
  };
  const patchBtn = $("rec-patch");
  if (patchBtn) patchBtn.onclick = () => {
    loadVerb(assetId, "def.patch_cyber");
    try {
      const p = JSON.parse($("o-params").value);
      p.vector = patchBtn.dataset.vector;
      $("o-params").value = JSON.stringify(p);
      previewOrder();
    } catch { /* template already correct */ }
  };
}

// Which command verbs belong on which telemetry-subsystem card (§5.1 cards carry their own buttons).
const VERB_SUBSYSTEM = {
  "eps.shed_load": "power", "eps.restore_load": "power", "eps.set_charge_mode": "power",
  "adcs.set_mode": "attitude", "adcs.desaturate": "attitude",
  "tcs.set_mode": "thermal", "tcs.set_heater": "thermal",
  "cdh.dump_storage": "cdh", "cdh.clear_fault": "cdh", "cdh.reset_subsystem": "cdh", "def.patch_cyber": "cdh",
  "comms.enable_isl": "comms", "comms.config_link": "comms", "comms.point_antenna": "comms", "def.frequency_hop": "comms",
  "satcom.mitigate_interference": "payload", "satcom.shift_users": "payload",
  "isr.collect_now": "payload", "isr.schedule_collection": "payload", "isr.set_mode": "payload",
  "sigint.task_collection": "payload", "wx.schedule_collection": "payload", "def.harden": "payload",
  "pnt.set_integrity": "payload",
  "def.maneuver_evade": "propulsion",
};
function verbsForSubsystem(a, sub) {
  return actionsFor(a).filter((v) => v.includes(".") && VERB_SUBSYSTEM[v] === sub);
}

// Load a subsystem-card verb into the compose form and preview it (operator reviews, then Issues).
function loadVerb(actor, verb) {
  $("o-actor").value = actor; onActorChange();   // repopulates actions for this asset
  $("o-action").value = verb; onActionChange();   // sets param template + runs dry-run preview
  $("o-action").scrollIntoView({ block: "center" });
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
  // Two-param overlay (§5.3): plot a second parameter alongside, normalized for shape comparison.
  const overlayParam = $("drill-overlay")?.value;
  const overlay = overlayParam && overlayParam !== param
    ? await api.get(`/api/sessions/${SID}/telemetry/${CELL}/${DRILL.asset}/${overlayParam}?n=120`).catch(() => null)
    : null;
  // Pass-correlation shading (§9.1): the hostile-effect time spans on this asset within the window.
  const windows = EFFECT_WINDOWS.filter((w) => w.target === DRILL.asset);
  window.Graph && Graph.draw($("drill-graph"), series, DRILL_DB[param], ghost, { overlay, windows });
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
  $("drill-overlay").onchange = () => DRILL.param && drawParam(DRILL.param);
  $("present").onchange = (e) => document.body.classList.toggle("present", e.target.checked);
  $("detach").onclick = detachViewers;
  $("task-plan").onclick = planTask;
  document.querySelectorAll("#task-mode .chip").forEach((b) => b.onclick = () => setTaskMode(b.dataset.tmode));
  $("task-regime").onchange = ssnCoverage;
  document.querySelectorAll("[data-step]").forEach((b) => b.onclick = () => step(+b.dataset.step));
  document.querySelectorAll(".cell").forEach((b) => b.onclick = () => setCell(b.dataset.cell));
  document.querySelectorAll("#fleet-filter .chip").forEach((b) => b.onclick = () => {
    FLEET_FILTER = b.dataset.filter;
    document.querySelectorAll("#fleet-filter .chip").forEach((c) => c.classList.toggle("active", c === b));
    if (SID) refresh();
  });
  document.querySelectorAll("#role-filter .chip").forEach((b) => b.onclick = () => {
    ROLE_FILTER = b.dataset.role;
    document.querySelectorAll("#role-filter .chip").forEach((c) => c.classList.toggle("active", c === b));
    onActorChange();    // re-derive the action list under the new role filter
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

// ===================================================================
// FUTURE-WORK §10 implementations (frontend)
// ===================================================================

// §10.A.1 — Read the active cell's accent from CSS, exposed to globe.js / map drawing.
window.cellAccent = function () {
  const v = getComputedStyle(document.body).getPropertyValue("--cell-accent").trim();
  return v || "#6fcf6f";
};

// Lightweight redraw used by toggles that don't change session state.
window.redrawAll = function () {
  if (SCENE) {
    if (window.Globe) Globe.render(SCENE);
    if (typeof drawMap === "function") drawMap();
  }
};

// §10.A.2, §10.A.3 — Color-blind + projector toggles, persisted in localStorage.
function applyToggle(id, cls) {
  const cb = $(id); if (!cb) return;
  const stored = localStorage.getItem("toggle:" + id) === "1";
  cb.checked = stored;
  document.body.classList.toggle(cls, stored);
  cb.addEventListener("change", () => {
    document.body.classList.toggle(cls, cb.checked);
    localStorage.setItem("toggle:" + id, cb.checked ? "1" : "0");
    if (window.redrawAll) redrawAll();
  });
}

// §10.A.4 — Diff-highlight: track previous numeric values per asset+param, pulse on change.
const PREV_VALUES = {};
window.maybePulse = function (cell, key, value) {
  const prev = PREV_VALUES[key];
  PREV_VALUES[key] = value;
  if (prev !== undefined && prev !== value && cell) {
    cell.classList.remove("diff-pulse"); void cell.offsetWidth;   // restart the animation
    cell.classList.add("diff-pulse");
  }
};

// §10.A.5, §10.E.19 — Tooltip on hover for [data-asset-ref] and [data-acronym]. One shared element.
const ACRONYMS = {
  SOH: "State of Health — the health rollup across all bus/payload subsystems.",
  RPO: "Rendezvous & Proximity Operations — co-orbital approach to inspect or threaten.",
  ISL: "Inter-Satellite Link — crosslink between two satellites; bypasses ground passes.",
  AAR: "After-Action Review — deterministic replay/scrub of a finished exercise.",
  SSN: "Space Surveillance Network — the SDA enterprise that fulfills request-based custody.",
  SDA: "Space Domain Awareness — knowing what is on orbit, where, and what it's doing.",
  EW:  "Electronic Warfare — jamming / spoofing of RF links (reversible).",
  ROE: "Rules of Engagement — what the cell is authorized to do (kinetic / cyber).",
  TT: "Tracking, Telemetry & Commanding — the ground/sat command/control link.",
  TTC: "TT&C — Tracking, Telemetry & Commanding.",
  PNT: "Positioning, Navigation, Timing — GPS-class service.",
  ISR: "Intelligence, Surveillance & Reconnaissance — imaging / SIGINT collection.",
  GEO: "Geostationary orbit (~35,786 km altitude).",
  LEO: "Low Earth Orbit (~200–2,000 km altitude).",
  MEO: "Medium Earth Orbit (~2,000–35,786 km altitude).",
  HVA: "High-Value Asset — the satellite Red wants to neutralize.",
  PME: "Professional Military Education — the audience for this simulator.",
  UEWR: "Upgraded Early Warning Radar (e.g. Cape Cod SFS, Fylingdales).",
  ECCM: "Electronic Counter-Countermeasures — defenses against jamming (e.g. frequency hopping).",
  "Δv": "Delta-v — change in orbital velocity; the maneuver budget that gates asset lifetime.",
  FSW: "Flight Software — the on-orbit computer software that controls the satellite.",
  CDH: "Command & Data Handling — the on-board computer subsystem.",
  EPS: "Electrical Power Subsystem — solar arrays + battery.",
  ADCS: "Attitude Determination & Control Subsystem — pointing.",
  TCS: "Thermal Control Subsystem — heaters / radiators.",
};
let _tipEl = null;
function tipEl() { return _tipEl || ($("tooltip"));}
function hideTip() { const t = tipEl(); if (t) t.style.display = "none"; }
function showTip(html, ev) {
  const t = tipEl(); if (!t) return;
  t.innerHTML = html; t.style.display = "block";
  const x = ev.clientX + 14, y = ev.clientY + 14;
  t.style.left = x + "px"; t.style.top = y + "px";
}
document.addEventListener("mouseover", (e) => {
  const acr = e.target.closest("[data-acronym]");
  if (acr) {
    const k = acr.dataset.acronym;
    const def = ACRONYMS[k] || ACRONYMS[k.toUpperCase()];
    if (def) showTip(`<b>${k}</b> — ${def}`, e);
    return;
  }
  const ref = e.target.closest("[data-asset-ref]");
  if (ref) {
    const id = ref.dataset.assetRef;
    const a = (SCENE && SCENE.assets.find((x) => x.id === id)) || null;
    if (a) {
      const soh = a.bus_state ? a.bus_state.mode : "—";
      const soc = a.bus_state ? Math.round(a.bus_state.power.battery_soc * 100) + "%" : "—";
      showTip(`<b>${a.id}</b><br>kind: ${a.kind}<br>bus: ${soh} · SoC: ${soc}`, e);
    }
  }
});
document.addEventListener("mousemove", (e) => {
  const t = tipEl(); if (!t || t.style.display === "none") return;
  t.style.left = (e.clientX + 14) + "px"; t.style.top = (e.clientY + 14) + "px";
});
document.addEventListener("mouseout", (e) => {
  if (e.target.closest && (e.target.closest("[data-acronym]") || e.target.closest("[data-asset-ref]"))) hideTip();
});

// §10.B.7 — Order presets / playbooks. Saved in localStorage scoped to vignette id.
function pbKey() { const v = $("vignette")?.value; return "playbooks:" + (v || "default"); }
function pbList() { try { return JSON.parse(localStorage.getItem(pbKey()) || "[]"); } catch { return []; } }
function pbSave(items) { localStorage.setItem(pbKey(), JSON.stringify(items)); renderPlaybooks(); }
function renderPlaybooks() {
  const div = $("playbook-list"); if (!div) return;
  const items = pbList();
  if (!items.length) { div.className = "playbook-list muted"; div.textContent = "(no presets saved)"; return; }
  div.className = "playbook-list";
  div.innerHTML = items.map((p, i) =>
    `<span class="playbook-chip" data-i="${i}">${p.name}<span class="x" data-del="${i}">✕</span></span>`).join("");
  div.querySelectorAll(".playbook-chip").forEach((c) => {
    c.addEventListener("click", (e) => {
      if (e.target.classList.contains("x")) {
        const items = pbList(); items.splice(+e.target.dataset.del, 1); pbSave(items);
      } else {
        const p = pbList()[+c.dataset.i];
        $("o-actor").value = p.actor; onActorChange();
        $("o-action").value = p.action; onActionChange();
        $("o-target").value = p.target || "";
        $("o-params").value = p.params;
        previewOrder();
      }
    });
  });
}

// §10.B.9 — Scene-moment bookmarks. Saved in localStorage scoped to vignette id.
function bmKey() { const v = $("vignette")?.value; return "bookmarks:" + (v || "default"); }
function bmList() { try { return JSON.parse(localStorage.getItem(bmKey()) || "[]"); } catch { return []; } }
function bmSave(items) { localStorage.setItem(bmKey(), JSON.stringify(items)); renderBookmarks(); }
function renderBookmarks() {
  const div = $("bookmark-list"); if (!div) return;
  const items = bmList();
  if (!items.length) { div.className = "bookmark-list muted"; div.textContent = "(no bookmarks)"; return; }
  div.className = "bookmark-list";
  div.innerHTML = items.map((b, i) => {
    const dt = new Date(b.t / 1000).toISOString().substring(11, 19);
    return `<span class="bookmark-chip" data-i="${i}">${b.name} <span class="muted">${dt}</span><span class="x" data-del="${i}">✕</span></span>`;
  }).join("");
  div.querySelectorAll(".bookmark-chip").forEach((c) => {
    c.addEventListener("click", async (e) => {
      if (e.target.classList.contains("x")) {
        const items = bmList(); items.splice(+e.target.dataset.del, 1); bmSave(items);
      } else {
        const b = bmList()[+c.dataset.i];
        if (!SID) return;
        await api.post(`/api/sessions/${SID}/rewind`, { t: b.t });
        refresh();
      }
    });
  });
}

// §10.C.10 — Day/night terminator overlay on the 2D map. Shades the night side using sun_lat/lon.
window.drawTerminator = function (ctx, c, PX, PY, sunLat, sunLon) {
  // For each longitude, the terminator latitude is:  lat_t = atan(-cos(lon - sunLon) / tan(sunLat))
  // (vanishes when sin(sunLat) = 0; treat the equator case specially).
  if (sunLat == null || sunLon == null) return;
  const slat = sunLat * Math.PI / 180, tlat = Math.tan(slat || 1e-9);
  ctx.save();
  ctx.fillStyle = "rgba(0,0,0,0.30)";
  ctx.beginPath();
  let firstX = null, lastX = null;
  for (let lon = -180; lon <= 180; lon += 2) {
    const arg = (lon - sunLon) * Math.PI / 180;
    const latT = Math.atan(-Math.cos(arg) / tlat) * 180 / Math.PI;
    const x = PX(lon), y = PY(latT);
    if (lon === -180) { ctx.moveTo(x, y); firstX = x; }
    else ctx.lineTo(x, y);
    lastX = x;
  }
  // Close the polygon along whichever pole the night side wraps to.
  const nightTop = sunLat < 0;   // if sun is south, the north pole is in night
  const polY = nightTop ? 0 : c.height;
  ctx.lineTo(lastX, polY); ctx.lineTo(firstX, polY); ctx.closePath();
  ctx.fill();
  ctx.restore();
};

// Persisted toggles + initial render of playbooks/bookmarks.
addEventListener("DOMContentLoaded", () => {
  applyToggle("projector", "projector");
  applyToggle("cb", "cb");
  const sp = $("save-playbook");
  if (sp) sp.addEventListener("click", () => {
    const body = composeBody(); if (!body) return;
    const name = prompt("Name this preset:", `${body.action} ${body.actor}`);
    if (!name) return;
    const items = pbList();
    items.push({ name, actor: body.actor, action: body.action, target: body.target || "", params: $("o-params").value });
    pbSave(items);
  });
  const bma = $("bookmark-add");
  if (bma) bma.addEventListener("click", () => {
    if (!SCENE) return;
    const t = SCENE.now;
    const name = prompt("Bookmark name:", "decision");
    if (!name) return;
    const items = bmList(); items.push({ name, t }); bmSave(items);
  });
  renderPlaybooks(); renderBookmarks();
});

// Wire AAR export links to the current session.
function refreshAarLinks() {
  const csv = $("aar-csv"), js = $("aar-json");
  if (csv && SID) csv.href = `/api/sessions/${SID}/aar/export.csv`;
  if (js && SID) js.href = `/api/sessions/${SID}/aar/export.json`;
}
// Re-render playbooks/bookmarks whenever the vignette selection changes.
addEventListener("DOMContentLoaded", () => {
  const v = $("vignette"); if (v) v.addEventListener("change", () => { renderPlaybooks(); renderBookmarks(); });
});

// §10.B.6 — Command palette (Cmd-K / Ctrl-K). Fuzzy menu over assets, time-advances, cells, injects.
const PALETTE = {
  // Each entry: {label, tag, run: fn}
  items: () => {
    const items = [];
    items.push({ label: "switch to Blue cell",  tag: "cell",  run: () => setCell("blue") });
    items.push({ label: "switch to Red cell",   tag: "cell",  run: () => setCell("red") });
    items.push({ label: "switch to White cell", tag: "cell",  run: () => setCell("white") });
    items.push({ label: "advance +1 min",       tag: "time",  run: () => stepBy(60) });
    items.push({ label: "advance +10 min",      tag: "time",  run: () => stepBy(600) });
    items.push({ label: "advance +1 hour",      tag: "time",  run: () => stepBy(3600) });
    items.push({ label: "rewind to start",      tag: "time",  run: () => rewindTo(0) });
    items.push({ label: "export AAR (CSV)",     tag: "aar",   run: () => SID && (location.href = `/api/sessions/${SID}/aar/export.csv`) });
    items.push({ label: "export AAR (JSON)",    tag: "aar",   run: () => SID && (location.href = `/api/sessions/${SID}/aar/export.json`) });
    items.push({ label: "toggle projector mode", tag: "view", run: () => { const cb = $("projector"); cb.checked = !cb.checked; cb.dispatchEvent(new Event("change")); }});
    items.push({ label: "toggle cb-safe palette", tag: "view", run: () => { const cb = $("cb"); cb.checked = !cb.checked; cb.dispatchEvent(new Event("change")); }});
    // Assets from the cell's view.
    if (SCENE) {
      SCENE.assets.forEach((a) => {
        items.push({
          label: `select asset ${a.id}`, tag: "asset",
          run: () => { $("o-actor").value = a.id; onActorChange(); openDrill(a.id); }
        });
        items.push({
          label: `focus globe on ${a.id}`, tag: "globe",
          run: () => window.Globe && Globe.focusOn(a.id),
        });
      });
    }
    // Active injects from the white-cell dropdown.
    const isel = $("inject-sel");
    if (isel) [...isel.options].forEach((o) => {
      if (o.value) items.push({ label: `fire inject ${o.value}`, tag: "inject", run: () => { isel.value = o.value; $("fire-inject").click(); } });
    });
    return items;
  },
  filter: "", cursor: 0,
};

function paletteOpen() { $("palette-wrap").classList.add("open"); $("palette-input").value = ""; PALETTE.filter = ""; PALETTE.cursor = 0; paletteRender(); $("palette-input").focus(); }
function paletteClose() { $("palette-wrap").classList.remove("open"); }
function paletteMatches() {
  const q = PALETTE.filter.toLowerCase().split(/\s+/).filter(Boolean);
  return PALETTE.items().filter((it) => q.every((t) => (it.label + " " + it.tag).toLowerCase().includes(t))).slice(0, 24);
}
function paletteRender() {
  const ms = paletteMatches();
  if (PALETTE.cursor >= ms.length) PALETTE.cursor = Math.max(0, ms.length - 1);
  $("palette-list").innerHTML = ms.map((it, i) =>
    `<li data-i="${i}" class="${i === PALETTE.cursor ? "active" : ""}">${it.label}<span class="tag">${it.tag}</span></li>`).join("");
  document.querySelectorAll("#palette-list li").forEach((li) => {
    li.addEventListener("click", () => { paletteRun(+li.dataset.i); });
  });
}
function paletteRun(i) {
  const ms = paletteMatches(); if (!ms[i]) return;
  paletteClose(); ms[i].run();
}
addEventListener("keydown", (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
    e.preventDefault();
    $("palette-wrap").classList.contains("open") ? paletteClose() : paletteOpen();
    return;
  }
  if (!$("palette-wrap").classList.contains("open")) return;
  if (e.key === "Escape") paletteClose();
  else if (e.key === "ArrowDown") { e.preventDefault(); PALETTE.cursor++; paletteRender(); }
  else if (e.key === "ArrowUp")   { e.preventDefault(); PALETTE.cursor--; paletteRender(); }
  else if (e.key === "Enter")     { e.preventDefault(); paletteRun(PALETTE.cursor); }
});
addEventListener("DOMContentLoaded", () => {
  const pin = $("palette-input"); if (pin) pin.addEventListener("input", () => { PALETTE.filter = pin.value; PALETTE.cursor = 0; paletteRender(); });
  const wrap = $("palette-wrap"); if (wrap) wrap.addEventListener("click", (e) => { if (e.target === wrap) paletteClose(); });
});

// Helpers used by the palette (extracted from the existing toolbar handlers).
async function stepBy(s) { if (!SID) return; await api.post(`/api/sessions/${SID}/advance`, { t: (SCENE ? SCENE.now : 0) + s * 1_000_000 }); refresh(); }
async function rewindTo(t) { if (!SID) return; await api.post(`/api/sessions/${SID}/rewind`, { t }); refresh(); }

// §10.B.8 — Multi-asset batch selection. Shift-click a fleet row to toggle; "Issue to all" runs
// the current compose against each batched asset (substituting actor).
const BATCH = new Set();
function batchRender() {
  const bar = $("batch-bar"); if (!bar) return;
  bar.classList.toggle("empty", BATCH.size === 0);
  $("batch-count").textContent = BATCH.size;
  $("batch-list").textContent = [...BATCH].join(", ");
  document.querySelectorAll("#assets tbody tr[data-asset]").forEach((tr) => {
    tr.classList.toggle("batched", BATCH.has(tr.dataset.asset));
  });
}
addEventListener("DOMContentLoaded", () => {
  const a = $("assets");
  if (a) a.addEventListener("click", (e) => {
    const tr = e.target.closest("tr[data-asset]");
    if (!tr || !e.shiftKey) return;
    if (BATCH.has(tr.dataset.asset)) BATCH.delete(tr.dataset.asset);
    else BATCH.add(tr.dataset.asset);
    e.preventDefault(); e.stopPropagation();
    batchRender();
  });
  const bi = $("batch-issue");
  if (bi) bi.addEventListener("click", async () => {
    const body = composeBody(); if (!body || BATCH.size === 0) return;
    const results = [];
    for (const id of BATCH) {
      const b = { ...body, actor: id };
      try { results.push({ id, ack: await api.post(`/api/sessions/${SID}/order`, b) }); }
      catch (err) { results.push({ id, ack: { ok: false, reason: String(err) } }); }
    }
    $("order-result").textContent = results.map((r) => `${r.id}: ${r.ack.ok ? "OK " + r.ack.status : "✗ " + (r.ack.reason || "")}`).join("\n");
    refresh();
  });
  const bc = $("batch-clear");
  if (bc) bc.addEventListener("click", () => { BATCH.clear(); batchRender(); });
});

// §10.E.18 — Coachmark tour. A small scripted overlay that walks the trainee through the UI.
const COACH_STEPS = [
  { sel: "#cells", title: "Pick your cell", body: "Switch between White (facilitator), Blue, and Red. The whole UI re-tints to your cell's color so you always know whose console you're driving." },
  { sel: "#assets", title: "Fleet rail", body: "Your assets and their state-of-health (SOH) in one glance. Click a row to drill down; <b>shift-click</b> to add it to the multi-asset batch." },
  { sel: "#order-panel", title: "Compose a command", body: "Pick an actor, an action, and parameters. The plan-time preview tells you whether the order would be accepted and why." },
  { sel: "#save-playbook", title: "Save it as a playbook", body: "Reusable orders (★ Save preset) are stored per vignette and recallable with one click." },
  { sel: "#aar-panel", title: "After-action review", body: "Scrub the deterministic timeline, jump to a bookmarked moment, and download the AAR as CSV/JSON for downstream analysis." },
  { sel: "#drill-panel", title: "Telemetry drill-down", body: "Symptoms not verdicts: each chip is a physical signal. Diagnose the cause yourself from the patterns." },
  { sel: ".banner", title: "You're done", body: "Press <b>Ctrl/Cmd-K</b> any time to open the command palette. Good luck, operator." },
];
let COACH_I = 0;
function coachOpen() { $("coachmark-wrap").classList.add("on"); COACH_I = 0; coachShow(); }
function coachClose() { $("coachmark-wrap").classList.remove("on"); }
function coachShow() {
  const step = COACH_STEPS[COACH_I]; if (!step) { coachClose(); return; }
  const el = document.querySelector(step.sel); if (!el) { COACH_I++; return coachShow(); }
  const r = el.getBoundingClientRect();
  const hole = $("coachmark-hole");
  hole.style.left = (r.left - 4) + "px"; hole.style.top = (r.top - 4) + "px";
  hole.style.width = (r.width + 8) + "px"; hole.style.height = (r.height + 8) + "px";
  const tip = $("coachmark-tip");
  const tipTop = Math.min(window.innerHeight - 200, r.bottom + 12);
  const tipLeft = Math.min(window.innerWidth - 360, Math.max(8, r.left));
  tip.style.left = tipLeft + "px"; tip.style.top = tipTop + "px";
  $("coachmark-title").textContent = step.title;
  $("coachmark-body").innerHTML = step.body;
  $("coachmark-step").textContent = `${COACH_I + 1} / ${COACH_STEPS.length}`;
  $("coachmark-back").disabled = COACH_I === 0;
  $("coachmark-next").textContent = COACH_I === COACH_STEPS.length - 1 ? "Done" : "Next →";
}
addEventListener("DOMContentLoaded", () => {
  const cs = $("coach-start"); if (cs) cs.addEventListener("click", coachOpen);
  $("coachmark-next").addEventListener("click", () => { if (++COACH_I >= COACH_STEPS.length) coachClose(); else coachShow(); });
  $("coachmark-back").addEventListener("click", () => { if (--COACH_I < 0) COACH_I = 0; coachShow(); });
  $("coachmark-close").addEventListener("click", coachClose);
});
