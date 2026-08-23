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
let REALTIME_GEN = 0;     // generation counter; bumped on stop so in-flight ticks abandon themselves
let REALTIME_ON = false;  // whether the real-time clock loop should keep ticking
// Local 1Hz clock interpolation between server polls (every ~1.5s) so the displayed UTC ticks
// each second instead of jumping every poll. Set on each successful refresh; the ticker reads
// them and extrapolates: display = LAST_REFRESH_SERVER_NOW + (Date.now() - LAST_REFRESH_WALL_MS).
let LAST_REFRESH_WALL_MS = 0;
let LAST_REFRESH_SERVER_NOW = null;
let SERVER_CLOCK_RUNNING_CACHED = false;
let CLOCK_TICKER = null;
const NET_STALE_MS = 4000;  // after 4s with no successful poll, show the "no updates" warning

// Format a next-contact countdown; color amber < 5 min, red < 1 min (P1 — imminent windows draw the eye).
function countdown(now, t) {
  if (t == null) return { txt: "—", cls: "muted" };
  const s = Math.max(0, Math.round((t - now) / 1e6));
  if (s === 0) return { txt: "live", cls: "green" };
  const txt = `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
  return { txt, cls: s < 60 ? "red" : s < 300 ? "yellow" : "" };
}

const $ = (id) => document.getElementById(id);
// Minimal HTML-escape for text interpolated into innerHTML (tutorial steps, etc.).
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const api = {
  async get(p) { const r = await fetch(p); if (!r.ok) throw new Error(await r.text()); return r.json(); },
  // IP-1130 — every POST carries the caller's own current seat as a query param, so every mutating
  // route's server-side Observer guard can see who's asking even for routes whose body has no
  // "cell" field of its own (start/step/clock/etc.). Centralized here rather than touching every
  // individual call site; routes that already read `cell` from the JSON body simply ignore it.
  async post(p, b) {
    const url = p + (p.includes("?") ? "&" : "?") + "cell=" + encodeURIComponent(CELL);
    const r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(b || {}) });
    if (!r.ok) throw new Error(await r.text());
    return r.json();
  },
};
// Drop sub-second precision so the displayed clock never shows .xxx ms — sim time advances
// per-event but the readouts here are operator-grade, not millisecond-precise.
const iso = (m) => m == null ? "—" : new Date(m / 1000).toISOString().replace(/\.\d{3}Z$/, "Z");
// Convert sim microseconds to a local time string in the currently selected timezone.
function localTimeStr(micros) {
  if (micros == null) return "—";
  const tzEl = document.getElementById("tz-select");
  const tz = tzEl ? tzEl.value : "America/New_York";
  if (tz === "UTC") return "";   // "UTC only" — nothing extra to show
  try {
    return new Date(micros / 1000).toLocaleString("en-US", {
      timeZone: tz, hour12: false,
      year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", second: "2-digit",
    }) + " " + new Intl.DateTimeFormat("en-US", { timeZone: tz, timeZoneName: "short" })
        .formatToParts(new Date(micros / 1000)).find((p) => p.type === "timeZoneName")?.value;
  } catch { return ""; }
}

// Legal actions per asset kind (from 05-cell-interfaces.md) + a starting parameter template.
const ACTIONS_BY_KIND = {
  satellite: ["downlink", "maneuver"], jammer: ["jam"], interceptor: ["engage"],
  cyber_unit: ["cyber"], directed_energy: ["jam"],
  ground_radar: ["observe"], ground_optical: ["observe"], space_based: ["observe"],
};
// Actions that carry an order-level Target — orders.py only reads order.target for these four
// (jam/engage/cyber effects resolve against it; observe/sensor-tasking windows against it).
// maneuver/downlink/command (dotted bus+payload verbs) act on the actor itself and never read
// order.target, so the Target field is disabled/blanked for every other action (see
// populateTargetPicker()).
const TARGET_REQUIRED_ACTIONS = new Set(["jam", "engage", "cyber", "observe"]);
const PARAM_TEMPLATE = {
  downlink: () => ({ via: DEFAULT_STATION }),
  maneuver: () => ({ dv: [0, 5, 0], via: DEFAULT_STATION }),
  // Audit 2026-06 Commands §C2 — jam/engage/cyber no longer accept success_prob;
  // Pₛ derives from physical params + defender state. The form template seeds the
  // physical inputs the operator IS allowed to choose.
  jam: () => ({ modulation: "barrage", power_w: 200.0 }),
  engage: () => ({ interceptor_class: "mrbm_kkv", salvo_n: 1 }),
  cyber: () => ({ vector: "ground_modem", payload: "seize_c2" }),
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
  "sigint.task_collection": () => ({ via: DEFAULT_STATION, band: "X", intercept_mode: "geolocate", dwell_s: 600 }),
  "wx.schedule_collection": () => ({ via: DEFAULT_STATION }),
  // Stage B verbs
  "cdh.reset_subsystem": () => ({ via: DEFAULT_STATION }),
  "adcs.desaturate": () => ({ via: DEFAULT_STATION }),
  "isr.set_mode": () => ({ via: DEFAULT_STATION, mode: "wide" }),
  "def.maneuver_evade": () => ({ via: DEFAULT_STATION, dv_cost: 5.0 }),
  // Realism-research-recommended verbs (Phase D §15):
  "pnt.flex_power": () => ({ via: DEFAULT_STATION, on: true, signal: "M-code" }),
  "pnt.set_health_flag": () => ({ via: DEFAULT_STATION, healthy: false }),
  "mw.add_stare_area": () => ({ via: DEFAULT_STATION, center: [0.0, 0.0], revisit_s: 30 }),
  "satcom.geolocate_interference": () => ({ via: DEFAULT_STATION, dwell_s: 600 }),
  "wx.request_sector": () => ({ via: DEFAULT_STATION, center: [0.0, 0.0], cadence_s: 60 }),
  // Final catalog-verb fill
  "satcom.set_frequency_plan": () => ({ via: DEFAULT_STATION, plan: "default" }),
  "satcom.reconfigure_beam": () => ({ via: DEFAULT_STATION, spot: "default" }),
  "sda.task_characterize": () => ({ via: DEFAULT_STATION, target: "TGT-1" }),
  "sda.task_search": () => ({ via: DEFAULT_STATION }),
  "sda.task_track": () => ({ via: DEFAULT_STATION, target: "TGT-1" }),
};

// Verb roles for the §1.2 role selector — drives the Bus/Payload/SDA/All filter on the command menu.
const VERB_ROLE = {
  downlink: "bus", maneuver: "bus", observe: "sda",
  "eps.shed_load": "bus", "eps.restore_load": "bus", "eps.set_charge_mode": "bus",
  "adcs.set_mode": "bus", "adcs.desaturate": "bus",
  "cdh.dump_storage": "bus", "cdh.clear_fault": "bus", "cdh.reset_subsystem": "bus",
  "tcs.set_mode": "bus", "tcs.set_heater": "bus",
  "comms.enable_isl": "bus", "comms.config_link": "bus",
  "satcom.mitigate_interference": "payload", "satcom.shift_users": "payload",
  "satcom.geolocate_interference": "payload", "satcom.reconfigure_beam": "payload",
  "isr.collect_now": "payload", "isr.schedule_collection": "payload", "isr.set_mode": "payload",
  "sigint.task_collection": "payload", "wx.schedule_collection": "payload",
  "wx.request_sector": "payload", "mw.add_stare_area": "payload",
  "pnt.flex_power": "payload", "pnt.set_health_flag": "payload",
  "def.patch_cyber": "bus", "def.frequency_hop": "bus",
  "def.harden": "payload", "def.set_threat_warning": "bus", "def.maneuver_evade": "bus",
  "satcom.set_frequency_plan": "payload",
  "sda.task_search": "sda", "sda.task_track": "sda", "sda.task_characterize": "sda",
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
  const sel = $("vignette");
  try {
    const list = await api.get("/api/vignettes");
    if (!list || !list.length) {
      sel.innerHTML = '<option value="" disabled selected>(no vignettes found — check server)</option>';
      return;
    }
    sel.innerHTML = list.map((v) => `<option value="${esc(v.id)}">${esc(v.title)}</option>`).join("");
  } catch (e) {
    sel.innerHTML = '<option value="" disabled selected>(failed to load — is the server running?)</option>';
    console.error("loadVignettes failed:", e);
  }
}
// Update the small toolbar session summary chip ("vignette · sess-N · ▶" etc.).
function updateSessionSummary(vignetteLabel, started) {
  const el = $("session-summary"); if (!el) return;
  if (!SID) { el.hidden = true; el.textContent = ""; return; }
  el.hidden = false;
  const tag = started ? "▶ running" : "loaded";
  el.textContent = `${vignetteLabel || ""} · ${SID} · ${tag}`.replace(/^ · /, "");
}

// IP-1120 — the banner is set once at Load and fixed for the session's lifetime (FR-4510); no
// polling needed. Both the creating tab (loadSession) and a joining tab (joinSessionFromHash)
// read it from the server (never re-derive it), per NFR-3100's single-source-of-truth guarantee.
function setBanner(text) {
  const el = $("banner");
  if (el && text) el.textContent = text;
}

async function loadSession() {
  stopRealtimeClock();
  const vselect = $("vignette");
  const vlabel = vselect && vselect.selectedOptions[0] ? vselect.selectedOptions[0].textContent : vselect.value;
  const classOverride = ($("classification-override") || {}).value || "";
  const resp = await api.post("/api/sessions", {
    vignette_id: vselect.value, seed: +$("seed").value,
    classification: classOverride.trim() || undefined,
  });
  SID = resp.session;
  setBanner(resp.classification);
  location.hash = SID;   // multiplayer: shareable URL — Blue/Red tabs open this to join
  $("session").textContent = "session " + SID; $("start").disabled = false;
  updateSessionSummary(vlabel, false);
  const injects = await api.get(`/api/sessions/${SID}/injects`).catch(() => []);
  $("inject-sel").innerHTML = injects.map((i) => `<option value="${i.id}">${i.label}</option>`).join("") || "<option>(none)</option>";
  await loadInjectLibrary();
  await refresh();
}

// Multiplayer: try to join the session named in location.hash. Returns true if it joined.
async function joinSessionFromHash() {
  const hashSid = (location.hash || "").replace(/^#/, "");
  if (!hashSid) return false;
  try {
    const sessions = await api.get("/api/sessions");
    const found = sessions.find((s) => s.sid === hashSid);
    if (!found) return false;
    SID = hashSid;
    $("session").textContent = "session " + SID;
    $("start").disabled = !!found.started;
    updateSessionSummary(found.title || found.vignette_id, found.started);
    setBanner(found.classification);   // IP-1120 — same resolved value the creating tab set
    const injects = await api.get(`/api/sessions/${SID}/injects`).catch(() => []);
    $("inject-sel").innerHTML = injects.map((i) => `<option value="${esc(i.id)}">${esc(i.label)}</option>`).join("") || "<option>(none)</option>";
    await loadInjectLibrary();
    return true;
  } catch (e) { console.warn("join-by-hash failed:", e); return false; }
}

// Multiplayer: server owns the real-time clock. The client just polls refresh() at ~1.5s so it
// observes the server's advanced clock + other tabs' actions. No more /step from the client.
function startRealtimeClock() {
  if (REALTIME_ON) return;
  REALTIME_ON = true;
  const myGen = REALTIME_GEN;
  const tick = async () => {
    if (!REALTIME_ON || myGen !== REALTIME_GEN || !SID) return;
    try {
      if (REALTIME_ON && myGen === REALTIME_GEN) await refresh();
    } catch { /* swallow — next tick will re-sync; the staleness watcher will surface persistent failures */ }
    if (REALTIME_ON && myGen === REALTIME_GEN) setTimeout(tick, 1500);
  };
  setTimeout(tick, 1000);
  startClockTicker();
}
function stopRealtimeClock() {
  REALTIME_ON = false;
  REALTIME_GEN++;   // any in-flight callback's myGen no longer matches; it abandons its refresh
  stopClockTicker();
}

// 1Hz local interpolation of the displayed clock. The poll loop hits the server at ~1.5s; this
// ticker advances the readout each second from the last server-anchored sim-now + wall elapsed.
// It also raises the "no updates from server" warning if a refresh hasn't landed for NET_STALE_MS.
function startClockTicker() {
  if (CLOCK_TICKER) return;
  CLOCK_TICKER = setInterval(updateClockDisplay, 1000);
}
function stopClockTicker() {
  if (CLOCK_TICKER) { clearInterval(CLOCK_TICKER); CLOCK_TICKER = null; }
  const warn = $("net-stale"); if (warn) warn.hidden = true;
}
function updateClockDisplay() {
  if (LAST_REFRESH_SERVER_NOW == null) return;
  const elapsedMs = Date.now() - LAST_REFRESH_WALL_MS;
  // Server is paused → display the last anchored sim time; otherwise extrapolate.
  const displayMicros = SERVER_CLOCK_RUNNING_CACHED
    ? LAST_REFRESH_SERVER_NOW + elapsedMs * 1000
    : LAST_REFRESH_SERVER_NOW;
  const txt = iso(displayMicros);
  const n1 = $("now"); if (n1) n1.textContent = txt;
  const n2 = $("now-header"); if (n2) n2.textContent = txt;
  const nl = $("now-local"); if (nl) nl.textContent = localTimeStr(displayMicros);
  // Staleness warning: persistent poll failures (network down, server stopped) leave the
  // operator looking at a frozen clock — surface it so they know the readout is no longer live.
  const warn = $("net-stale");
  if (warn) {
    if (elapsedMs > NET_STALE_MS) {
      warn.hidden = false;
      warn.textContent = `⚠ no updates from server (${Math.floor(elapsedMs / 1000)}s)`;
    } else {
      warn.hidden = true;
    }
  }
}
const start = async () => {
  // IP-1151 — Start is hard-blocked server-side while a mandatory role assignment is unmet; the
  // Ack comes back HTTP 200 with ok:false (a rejected request, not a server error), so it must be
  // checked explicitly rather than treated as success by default.
  const ack = await api.post(`/api/sessions/${SID}/start`);
  if (!ack.ok) { alert(ack.reason || "Start refused"); return; }
  startRealtimeClock();                                     // begin client poll loop
  await refresh();
};
// Manual time-jump (White +1m/+10m/+1h): server re-anchors after advance_to.
const step = async (dt) => { await api.post(`/api/sessions/${SID}/step`, { dt_sim_s: dt }); await refresh(); };
const rewind = async () => {
  stopRealtimeClock();
  await api.post(`/api/sessions/${SID}/rewind`, { t: 0 });
  startRealtimeClock();   // server re-anchors on rewind; resume poll loop
  await refresh();
};
// White-only Start/Pause toggle that drives the server clock.
async function setServerClock(running) {
  if (!SID) return;
  await api.post(`/api/sessions/${SID}/clock`, { running });
  await refresh();
}
async function fireInject() {
  const id = $("inject-sel").value; if (!id || id === "(none)") return;
  await api.post(`/api/sessions/${SID}/inject`, { inject: id }); await refresh();
}

// ---- FW §11.D.19 — Inject library + builder (White Cell) -----------------
let INJECT_LIBRARY = [];

async function loadInjectLibrary() {
  if (!SID) return;
  try { INJECT_LIBRARY = await api.get(`/api/sessions/${SID}/inject_library`); }
  catch { INJECT_LIBRARY = []; }
  const sel = $("inject-lib"); if (!sel) return;
  sel.innerHTML = '<option value="">(custom)</option>' +
    INJECT_LIBRARY.map((i, idx) => `<option value="${idx}">${i.label || i.id}</option>`).join("");
}

function loadInjectTemplate() {
  const sel = $("inject-lib"); if (!sel) return;
  const idx = sel.value;
  const ta = $("inject-effects"); if (!ta) return;
  if (idx === "") { ta.value = '[\n  {"type": "message", "to": ["blue"], "text": "…"}\n]'; return; }
  const item = INJECT_LIBRARY[+idx]; if (!item) return;
  ta.value = JSON.stringify(item.effects || [], null, 2);
  $("inject-build-result").textContent = `Loaded "${item.label}" — edit JSON, set schedule, then fire.`;
}

function injectScheduleAt() {
  const mode = $("inject-when").value;
  if (mode === "now") return null;
  if (mode === "rel") {
    const dt_s = parseFloat($("inject-rel-s").value || "0");
    if (!isFinite(dt_s) || dt_s < 0) return null;
    return (NOW || 0) + Math.round(dt_s * 1_000_000);
  }
  if (mode === "abs") {
    const v = $("inject-abs-utc").value;
    if (!v) return null;
    // datetime-local is in local timezone — treat as UTC literal so the operator's intent is exact
    const ms = Date.parse(v + "Z");
    if (isNaN(ms)) return null;
    return ms * 1000;
  }
  return null;
}

async function fireBuiltInject() {
  const out = $("inject-build-result");
  if (!SID) { out.textContent = "No active session."; return; }
  const raw = $("inject-effects").value.trim();
  let effects;
  try { effects = JSON.parse(raw); }
  catch (err) { out.style.color = "var(--red)"; out.textContent = "✗ effects JSON invalid: " + err.message; return; }
  if (!Array.isArray(effects)) { out.style.color = "var(--red)"; out.textContent = "✗ effects must be a JSON list"; return; }
  const at = injectScheduleAt();
  const body = { inject: { effects }, at_sim_t: at };
  try {
    await api.post(`/api/sessions/${SID}/inject`, body);
    out.style.color = "var(--accent)";
    out.textContent = at ? `✓ scheduled for ${iso(at)} (${effects.length} effect${effects.length === 1 ? "" : "s"})`
                          : `✓ fired immediately (${effects.length} effect${effects.length === 1 ? "" : "s"})`;
    await refresh();
  } catch (err) {
    out.style.color = "var(--red)";
    out.textContent = "✗ server error: " + (err.message || err);
  }
}

function onInjectWhenChange() {
  const mode = $("inject-when").value;
  $("inject-rel-wrap").style.display = mode === "rel" ? "" : "none";
  $("inject-abs-wrap").style.display = mode === "abs" ? "" : "none";
}

async function renderQueue() {
  const QUEUE_TTL_US = 5 * 60 * 1_000_000;   // drop completed/cancelled after 5 min sim time
  const orders = await api.get(`/api/sessions/${SID}/orders/${CELL}`).catch(() => []);
  const visible = orders.filter((o) => {
    if (o.status !== "executed" && o.status !== "cancelled") return true;
    const t = o.window ? o.window[1] : (o.issued_at || 0);
    return NOW > 0 && (NOW - t) < QUEUE_TTL_US;
  });
  $("queue").innerHTML = visible.length ? visible.map((o) => {
    const w = o.window ? iso(o.window[0]).slice(11, 19) : "—";
    const cancel = o.status === "queued" ? `<button class="icon" data-oid="${o.id}">✕</button>` : "";
    return `<div class="qrow ${o.status}"><span>${esc(o.actor)} ${esc(o.action)} ${esc(o.target || "")}</span>` +
           `<span class="muted">${o.status} · ${o.delivery_path || ""} · ${w}</span>${cancel}</div>`;
  }).join("") : "<div class='muted'>(empty)</div>";
  document.querySelectorAll("#queue [data-oid]").forEach((b) => b.onclick = async () => {
    await api.post(`/api/sessions/${SID}/cancel`, { cell: CELL, order_id: b.dataset.oid }); refresh();
  });
}

async function drawRibbon(actor) {
  const c = $("ribbon"), x = c.getContext("2d");
  const wa = await api.get(`/api/sessions/${SID}/windows/${CELL}/${actor}`).catch(() => null);
  x.fillStyle = "#0a0f15"; x.fillRect(0, 0, c.width, c.height);
  if (!wa || !wa.windows.length) { x.fillStyle = "#7a8aa0"; x.font = "11px monospace"; x.fillText("no passes / not a satellite", 8, 26); return; }
  const span = wa.horizon_s * 1e6, now = wa.now;
  // FW §11.C.16 — Gantt ribbon: three lanes (command / telemetry / sensor_observation),
  // shaded blocks per window, vertical "now" line, hourly tick labels.
  const lane = { command_uplink: 6, telemetry_downlink: 18, sensor_observation: 30 };
  const col  = { command_uplink: "#6fcf6f", telemetry_downlink: "#5a96e6", sensor_observation: "#e6c95a" };
  x.strokeStyle = "#1b2531";
  const hours = Math.max(1, Math.round(wa.horizon_s / 3600));
  for (let f = 0; f <= hours; f++) { const px = f / hours * c.width; x.beginPath(); x.moveTo(px, 0); x.lineTo(px, c.height); x.stroke(); }
  wa.windows.forEach((w) => {
    const x0 = (w.start - now) / span * c.width, x1 = (w.end - now) / span * c.width;
    x.fillStyle = col[w.channel] || "#888";
    x.fillRect(x0, lane[w.channel] || 14, Math.max(2, x1 - x0), 10);
  });
  // Lane labels
  x.fillStyle = "#9fb0c0"; x.font = "10px monospace";
  x.fillText("cmd", 2, 15); x.fillText("tlm", 2, 27); x.fillText("obs", 2, 39);
}

function setCell(c) {
  CELL = c;
  document.body.setAttribute("data-cell", c);    // drives --cell-accent across panels/borders/rows
  document.querySelectorAll(".cell").forEach((b) => b.classList.toggle("active", b.dataset.cell === c));
  document.querySelectorAll(".white-only").forEach((el) => { el.style.display = c === "white" ? "" : "none"; });
  // IP-1130 — Observer has no command ability whatsoever (FR-6510). This is a UX convenience only;
  // the server-side guard on every mutating route is the actual enforcement (server.py's
  // _reject_observer, exercised even for a request that bypasses this UI entirely).
  const isObserver = c === "observer";
  if ($("issue")) $("issue").disabled = isObserver;
  document.querySelectorAll("#order-panel input, #order-panel select, #order-panel button")
    .forEach((el) => { el.disabled = isObserver; });
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
  // The dropdown covers everything the cell already has a track/belief on; the manual field
  // is the escape hatch for an id the cell knows from the scenario but hasn't tracked yet —
  // most importantly, tasking a sensor at all (the "observe" action IS how custody gets built,
  // so its target can never come pre-populated from a track the operator doesn't have yet).
  const target = $("o-target-manual")?.value || $("o-target")?.value || null;
  return { cell, actor, action, target, params };
}

// Verbs offered for an asset: kind-based core actions + bus verbs for satellites + payload verbs by type.
function actionsFor(a) {
  const acts = (ACTIONS_BY_KIND[a.kind] || ["observe"]).slice();
  if (a.kind === "satellite") {
    acts.push("eps.shed_load", "eps.restore_load", "eps.set_charge_mode",
              "adcs.set_mode", "adcs.desaturate",
              "cdh.dump_storage", "cdh.clear_fault", "cdh.reset_subsystem",
              "tcs.set_mode", "tcs.set_heater",
              "comms.enable_isl", "comms.config_link",
              "def.frequency_hop", "def.harden", "def.set_threat_warning", "def.maneuver_evade");
    if (a.payload === "satcom") acts.push("satcom.mitigate_interference", "satcom.shift_users",
                                          "satcom.set_frequency_plan", "satcom.reconfigure_beam",
                                          "satcom.geolocate_interference");
    if (a.payload === "sda") acts.push("sda.task_search", "sda.task_track", "sda.task_characterize");
    if (a.payload === "isr_eo" || a.payload === "isr_sar") acts.push("isr.collect_now", "isr.schedule_collection", "isr.set_mode");
    if (a.payload === "sigint") acts.push("sigint.task_collection");
    if (a.payload === "weather") acts.push("wx.schedule_collection", "wx.request_sector");
    if (a.payload === "mw") acts.push("mw.add_stare_area");
    if (a.payload === "pnt") acts.push("pnt.flex_power", "pnt.set_health_flag");
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
  // FW §11.D.18 — live consequence preview alongside the validity preview.
  renderConsequencePreview(body);
}

async function renderConsequencePreview(body) {
  const el = $("consequence-preview"); if (!el) return;
  if (!body || !body.action) { el.textContent = ""; return; }
  let res; try {
    res = await api.post(`/api/sessions/${SID}/preview/consequence`, body);
  } catch { el.textContent = ""; return; }
  const sev = res.severity || "low";
  const sevColor = { high: "var(--red)", medium: "var(--yellow)", low: "var(--muted)" }[sev];
  el.style.color = sevColor;
  const notesStr = (res.notes && res.notes.length) ? " · " + res.notes.join(" · ") : "";
  el.textContent = `⚠ ${sev.toUpperCase()} · esc ${res.escalation_w} · ${res.reversible ? "reversible" : "irreversible"} · debris ${res.debris_risk} · attr ${res.attribution}${notesStr}`;
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
  const target = $("task-target-manual")?.value || $("task-target").value
              || $("o-target-manual")?.value || $("o-target").value;
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
  // Build ISR collection params
  const beamMode = $("task-beam-mode") && $("task-beam-mode").value;
  const lookAngle = $("task-look-angle") ? parseFloat($("task-look-angle").value) : 0;
  const duration = $("task-duration") ? parseFloat($("task-duration").value) : 300;
  const params = {
    intent: $("task-intent").value,
    priority: $("task-priority").value,
    ...(beamMode ? { beam_mode: beamMode } : {}),
    look_angle_deg: lookAngle,
    duration_s: duration,
  };
  const body = { cell, actor: $("task-sensor").value, action: "observe", target, params };
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
  if ($("task-isr-params")) $("task-isr-params").style.display = (m === "ssn") ? "none" : "";
  $("task-coverage").textContent = "";
  if (m === "ssn" && SID) { ssnCoverage(); renderSsnQueue(CELL === "white" ? "blue" : CELL); }
}

// ISR beam mode info table: swath, resolution, power, duty cycle for quick reference
const ISR_BEAM_INFO = {
  wide_area:   { swath: "100/500 km", res: "10/25 m",  power: "low",  duty: "30/10%" },
  stripmap:    { swath: "30/25 km",   res: "3/3 m",    power: "med",  duty: "40/15%" },
  spotlight:   { swath: "5/4 km",     res: "0.5/0.3 m",power: "high", duty: "50/8%"  },
  scan:        { swath: "400 km",     res: "30 m",      power: "low",  duty: "25%"    },
  fine:        { swath: "10 km",      res: "1 m",       power: "high", duty: "12%"    },
  polarimetric:{ swath: "30 km",      res: "5 m",       power: "high", duty: "20%"    },
};

function updateIsrInfo() {
  const el = $("task-isr-info"); if (!el) return;
  const mode = $("task-beam-mode") && $("task-beam-mode").value;
  const look = $("task-look-angle") && parseFloat($("task-look-angle").value);
  if ($("task-look-val")) $("task-look-val").textContent = look + "°";
  const info = mode && ISR_BEAM_INFO[mode];
  if (!info) { el.textContent = ""; return; }
  const penalty = look > 0 ? ` · ${Math.round(Math.cos(look * Math.PI / 180) * 100)}% gain at ${look}° look` : "";
  el.textContent = `swath ${info.swath} · res ${info.res} · power ${info.power} · duty ${info.duty}${penalty}`;
}

// Multi-screen pop-outs (Part E of LAN-multiplayer plan). A pop-out is just another tab that
// joins the same session (URL hash carries SID, ?cell=... carries the cell, ?layout=... carries
// the panel list). The opened window loads the full app, polls like any other client, and the
// layout-cull at boot hides every panel not requested. No postMessage / IPC needed — the server
// is the single source of truth.
//
// Maps each layout token to the IDs of panels to KEEP visible. Multiple tokens can be combined
// with "+" (e.g. layout=globe+map shows both viewers side-by-side).
// globe-panel and map-panel are children of viewers-panel, so the outer wrapper must be kept
// whenever either viewer is requested; individual inner panels are also culled separately.
const LAYOUT_PANELS = {
  full:        ["*"],
  globe:       ["viewers-panel", "globe-panel", "cell-time-panel"],
  map:         ["viewers-panel", "map-panel",   "cell-time-panel"],
  "globe+map": ["viewers-panel", "globe-panel", "map-panel", "cell-time-panel"],
  fleet:       ["fleet-panel", "drill-panel", "cell-time-panel"],
  order:       ["order-panel", "activity-panel", "cell-time-panel"],
  aar:         ["aar-panel", "assessment-panel", "cell-time-panel"],
};

function popOut(layoutToken) {
  if (!SID) return;
  const url = `/?layout=${encodeURIComponent(layoutToken)}&cell=${CELL}#${SID}`;
  window.open(url, `popout-${layoutToken}-${Date.now()}`, "width=900,height=700");
}

function applyLayoutCull() {
  const params = new URLSearchParams(location.search);
  const layout = params.get("layout") || "full";
  if (layout === "full") return;
  const keep = new Set();
  layout.split("+").forEach((tok) => (LAYOUT_PANELS[tok] || []).forEach((id) => keep.add(id)));
  if (keep.size === 0) return;
  // Hide top-level direct children of main that aren't in the keep set. The mission brief
  // panel lives outside <main> (full page width, above every other panel) but is still a
  // top-level layout element subject to the same pop-out culling, so it's included explicitly.
  document.querySelectorAll("main > [id], #brief-panel").forEach((el) => {
    if (!keep.has(el.id)) el.hidden = true;
  });
  // Hide individual viewer sub-panels (globe-panel / map-panel inside viewers-panel).
  document.querySelectorAll("#viewers-panel > [id]").forEach((el) => {
    if (!keep.has(el.id)) el.hidden = true;
  });
  document.body.classList.add("popout");
  document.body.dataset.layout = layout;
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

// -- Declarative shape-class form templates (Audit 2026-06 Commands §M4 Phase C step 2) -------
// Each entry is a list of fields. Field shape:
//   { key, type: "enum"|"bool"|"number"|"text"|"latlon", label, default, options?, min?, max?, step?, help? }
// `via` is auto-prepended as a station picker when the action goes through a window. Verbs not
// listed here fall back to the JSON escape hatch (#o-params), so coverage is additive.
const VERB_FORM_SCHEMA = {
  // -- Bus verbs ------------------------------------------------------------
  "eps.set_charge_mode": [
    { key: "mode", type: "enum", label: "Charge mode",
      options: ["nominal", "fast", "trickle"], default: "fast" },
  ],
  "eps.select_bus": [
    { key: "bus", type: "enum", label: "Power bus",
      options: ["primary", "secondary"], default: "primary" },
  ],
  "adcs.set_mode": [
    { key: "mode", type: "enum", label: "Attitude mode",
      options: ["nominal", "slew", "safe"], default: "nominal" },
  ],
  "tcs.set_mode": [
    { key: "mode", type: "enum", label: "Thermal mode",
      options: ["nominal", "operational", "survival"], default: "operational" },
  ],
  "tcs.set_heater": [
    { key: "on", type: "bool", label: "Heater on", default: true },
  ],
  "comms.enable_isl": [
    { key: "on", type: "bool", label: "ISL on", default: true },
  ],
  "comms.config_link": [
    { key: "data_rate_kbps", type: "number", label: "Data rate (kbps)",
      default: 2048, min: 64, max: 16384, step: 64 },
  ],
  "adcs.point_payload": [
    { key: "target", type: "text", label: "Slew target id", default: "" },
  ],
  "def.frequency_hop": [
    { key: "on", type: "bool", label: "Hopping on", default: true,
      help: "Audit §C1: reduces incoming jam Pₛ at the resolver to 40% residual." },
  ],
  "def.harden": [
    { key: "on", type: "bool", label: "Harden payload", default: true,
      help: "Engages on top of design-time hardening for the safe-mode roll." },
  ],
  "def.set_threat_warning": [
    { key: "on", type: "bool", label: "Threat warning on", default: true },
  ],
  "def.maneuver_evade": [
    { key: "dv_cost", type: "number", label: "Δv cost (m/s)",
      default: 5.0, min: 1.0, max: 50.0, step: 0.5,
      help: "Audit §C1: evasion_active halves kinetic Pₖ for fly-out window." },
  ],
  "def.patch_cyber": [
    { key: "vector", type: "enum", label: "Vector to patch",
      options: ["", "rf", "ground_modem", "ground_segment", "insider", "supply_chain"],
      default: "ground_modem",
      help: "Empty patches every vulnerability; named vector closes that single access path." },
  ],
  "def.escort_posture": [
    { key: "target", type: "text", label: "Escort target id", default: "" },
  ],
  // -- Payload verbs --------------------------------------------------------
  "isr.set_mode": [
    { key: "mode", type: "enum", label: "ISR mode",
      options: ["nominal", "wide", "narrow", "standby"], default: "wide" },
  ],
  "isr.prioritize_downlink": [
    { key: "priority", type: "enum", label: "Priority",
      options: ["routine", "high", "urgent"], default: "high" },
  ],
  "sigint.task_collection": [
    { key: "band", type: "enum", label: "Band",
      options: ["UHF", "L", "S", "X", "Ku", "Ka", "W"], default: "X" },
    { key: "intercept_mode", type: "enum", label: "Intercept mode",
      options: ["scan", "track", "geolocate"], default: "geolocate" },
    { key: "dwell_s", type: "number", label: "Dwell (s)",
      default: 600, min: 1, max: 7200, step: 30 },
  ],
  "sda.task_track": [
    { key: "target", type: "text", label: "Track target id", default: "" },
  ],
  "sda.task_characterize": [
    { key: "target", type: "text", label: "Characterize target id", default: "" },
  ],
  "satcom.set_frequency_plan": [
    { key: "plan", type: "text", label: "Plan id", default: "default",
      help: "Optional beam_pattern/polarization/eirp_dbm in advanced JSON." },
  ],
  "satcom.reconfigure_beam": [
    { key: "spot", type: "text", label: "Beam spot id", default: "default" },
  ],
  // -- Realism §15 additions (Phase D) ---------------------------------------
  "pnt.flex_power": [
    { key: "on", type: "bool", label: "Flex power on", default: true },
    { key: "signal", type: "enum", label: "Signal",
      options: ["M-code", "PY"], default: "M-code",
      help: "IS-GPS-200E flex power — raise mil signal power in jammed regions." },
  ],
  "pnt.set_health_flag": [
    { key: "healthy", type: "bool", label: "SV healthy", default: false,
      help: "Setting unhealthy auto-broadcasts a NANU consequence event." },
    { key: "sv_id", type: "text", label: "SV id (optional)", default: "" },
  ],
  "mw.add_stare_area": [
    { key: "center", type: "latlon", label: "AOI center", default: [0.0, 0.0] },
    { key: "revisit_s", type: "enum", label: "Revisit",
      options: ["10", "30", "60"], default: "30",
      help: "SBIRS step-stare cadence (seconds between AOI revisits)." },
  ],
  "satcom.geolocate_interference": [
    { key: "dwell_s", type: "number", label: "Dwell (s)",
      default: 600, min: 60, max: 3600, step: 60,
      help: "MAJE-style geoloc; CEP scales as 50 km / (dwell / 600 s)." },
  ],
  "wx.request_sector": [
    { key: "center", type: "latlon", label: "Sector center", default: [0.0, 0.0] },
    { key: "cadence_s", type: "enum", label: "Cadence",
      options: ["30", "60"], default: "60",
      help: "GOES-R MDS request cadence (30 s mesoscale or 60 s default)." },
  ],
};

function _esc(s) { return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "\"": "&quot;" }[c])); }

function renderVerbForm(action) {
  const wrap = $("verb-form"); if (!wrap) return;
  const schema = VERB_FORM_SCHEMA[action];
  if (!schema) { wrap.style.display = "none"; wrap.innerHTML = ""; return; }
  // Build inputs. via is auto-prepended unless the verb is cyber/jam/engage (their own panels).
  const html = [];
  html.push(`<label>via <input id="vf-via" type="text" value="${_esc(DEFAULT_STATION)}" style="width:8em"></label>`);
  for (const f of schema) {
    const id = `vf-${f.key}`;
    if (f.type === "enum") {
      const opts = f.options.map((o) => `<option value="${_esc(o)}"${o === f.default ? " selected" : ""}>${_esc(o)}</option>`).join("");
      html.push(`<label>${_esc(f.label)} <select id="${id}">${opts}</select></label>`);
    } else if (f.type === "bool") {
      html.push(`<label><input id="${id}" type="checkbox"${f.default ? " checked" : ""}> ${_esc(f.label)}</label>`);
    } else if (f.type === "number") {
      const min = f.min != null ? ` min="${f.min}"` : "";
      const max = f.max != null ? ` max="${f.max}"` : "";
      const step = f.step != null ? ` step="${f.step}"` : "";
      html.push(`<label>${_esc(f.label)} <input id="${id}" type="number" value="${f.default}"${min}${max}${step}></label>`);
    } else if (f.type === "text") {
      html.push(`<label>${_esc(f.label)} <input id="${id}" type="text" value="${_esc(f.default)}" style="width:10em"></label>`);
    } else if (f.type === "latlon") {
      const [lat, lon] = f.default;
      html.push(`<label>${_esc(f.label)} lat <input id="${id}-lat" type="number" step="0.5" value="${lat}" style="width:5em"></label>`);
      html.push(`<label>lon <input id="${id}-lon" type="number" step="0.5" value="${lon}" style="width:5em"></label>`);
    }
    if (f.help) html.push(`<span class="muted" style="font-size:11px;flex-basis:100%">${_esc(f.help)}</span>`);
  }
  wrap.innerHTML = html.join("");
  wrap.style.display = "";
  // Wire each input to update #o-params and trigger preview on change.
  wrap.querySelectorAll("input,select").forEach((el) => {
    el.addEventListener("change", () => updateOParamsFromVerbForm(action));
    el.addEventListener("input", () => updateOParamsFromVerbForm(action));
  });
  updateOParamsFromVerbForm(action);
}

function updateOParamsFromVerbForm(action) {
  const schema = VERB_FORM_SCHEMA[action]; if (!schema) return;
  const params = { via: $("vf-via")?.value || DEFAULT_STATION };
  for (const f of schema) {
    const id = `vf-${f.key}`;
    if (f.type === "enum") {
      const v = $(id)?.value; if (v) params[f.key] = (f.options.every((o) => /^\d+$/.test(o))) ? parseInt(v, 10) : v;
    } else if (f.type === "bool") {
      params[f.key] = !!$(id)?.checked;
    } else if (f.type === "number") {
      const v = parseFloat($(id)?.value); if (!Number.isNaN(v)) params[f.key] = v;
    } else if (f.type === "text") {
      const v = $(id)?.value; if (v) params[f.key] = v;
    } else if (f.type === "latlon") {
      params[f.key] = [parseFloat($(`${id}-lat`)?.value || "0"), parseFloat($(`${id}-lon`)?.value || "0")];
    }
  }
  if ($("o-params")) $("o-params").value = JSON.stringify(params);
  previewOrder();
}

function onActorChange() {
  const id = $("o-actor").value, a = ASSETS[id] || {};
  $("actor-info").textContent = a.kind ? `${a.kind} · ${a.owner}${a.payload ? " · " + a.payload : ""}` : "";
  const prevAction = $("o-action").value;
  $("o-action").innerHTML = actionsFor(a).map((x) => `<option>${x}</option>`).join("");
  if (prevAction && [...$("o-action").options].some((o) => o.value === prevAction))
    $("o-action").value = prevAction;
  onActionChange(prevAction !== $("o-action").value);  // also repopulates target (owner + gating)
  if (SID && id) drawRibbon(id);
}
function onActionChange(resetParams = true) {
  const action = $("o-action").value;
  const tmpl = PARAM_TEMPLATE[action]; if (resetParams && tmpl) $("o-params").value = JSON.stringify(tmpl());
  // Audit 2026-06 Commands §M4 Phase C step 2 — declarative shape-class form.
  // Verbs in VERB_FORM_SCHEMA show typed inputs; others fall through to JSON.
  if (resetParams) renderVerbForm(action);
  // Show/hide the maneuver mode assistant.
  const isMnvr = action === "maneuver";
  $("mnvr-panel") && ($("mnvr-panel").style.display = isMnvr ? "" : "none");
  if (isMnvr) mnvrModeChange();
  // Show/hide the jam parameter assistant.
  const isJam = action === "jam";
  $("jam-panel") && ($("jam-panel").style.display = isJam ? "" : "none");
  if (isJam) jamSummaryUpdate();
  // Audit 2026-06 Commands §M4 — engage and cyber assistant panels (Phase C step 1).
  const isEng = action === "engage";
  $("engage-panel") && ($("engage-panel").style.display = isEng ? "" : "none");
  if (isEng) engageSummaryUpdate();
  const isCyber = action === "cyber";
  $("cyber-panel") && ($("cyber-panel").style.display = isCyber ? "" : "none");
  if (isCyber) cyberSummaryUpdate();
  // Clear any prior jam preview footprint
  if (!isJam && window.JAM_PREVIEW) { JAM_PREVIEW = null; if (typeof drawMap === "function") drawMap(); }
  populateTargetPicker();   // (re)gate the Target field for the new action; owner unchanged
  previewOrder();
}

// -- Maneuver mode assistant --------------------------------------------------

const MNVR_FIELD_IDS = {
  eci: ["mnvr-eci"],
  lvlh: ["mnvr-lvlh"],
  finite_burn: ["mnvr-finite-burn"],
  target_coe: ["mnvr-target-coe"],
  hohmann: ["mnvr-hohmann"],
  plane_change: ["mnvr-plane-change"],
};

function mnvrModeChange() {
  const mode = $("mnvr-mode")?.value || "eci";
  Object.values(MNVR_FIELD_IDS).flat().forEach((id) => {
    const el = $(id); if (el) el.style.display = "none";
  });
  (MNVR_FIELD_IDS[mode] || []).forEach((id) => {
    const el = $(id); if (el) el.style.display = "";
  });
  $("mnvr-result") && ($("mnvr-result").innerHTML = "");
  $("mnvr-cost") && ($("mnvr-cost").textContent = "");
}

function mnvrGatherParams() {
  const mode = $("mnvr-mode")?.value || "eci";
  const via = (() => { try { return JSON.parse($("o-params").value || "{}").via || "GS-NORTH"; } catch { return "GS-NORTH"; } })();
  if (mode === "eci") {
    return { mode, via,
      dv: [numVal("mnvr-eci-x"), numVal("mnvr-eci-y"), numVal("mnvr-eci-z")] };
  }
  if (mode === "lvlh") {
    return { mode, via,
      dv_r: numVal("mnvr-lvlh-r"), dv_t: numVal("mnvr-lvlh-t"), dv_n: numVal("mnvr-lvlh-n") };
  }
  if (mode === "finite_burn") {
    return { mode, via,
      direction_r: numVal("mnvr-fb-r"), direction_t: numVal("mnvr-fb-t"), direction_n: numVal("mnvr-fb-n"),
      magnitude_ms: numVal("mnvr-fb-mag"), duration_s: numVal("mnvr-fb-dur") };
  }
  if (mode === "target_coe") {
    const p = { mode, via };
    const aEl = $("mnvr-coe-a"); if (aEl?.value !== "") p.a_km = numVal("mnvr-coe-a");
    const eEl = $("mnvr-coe-e"); if (eEl?.value !== "") p.e = numVal("mnvr-coe-e");
    const iEl = $("mnvr-coe-i"); if (iEl?.value !== "") p.i_deg = numVal("mnvr-coe-i");
    const rEl = $("mnvr-coe-raan"); if (rEl?.value !== "") p.raan_deg = numVal("mnvr-coe-raan");
    const wEl = $("mnvr-coe-argp"); if (wEl?.value !== "") p.argp_deg = numVal("mnvr-coe-argp");
    return p;
  }
  if (mode === "hohmann") {
    return { mode, via, target_alt_km: numVal("mnvr-hoh-alt") };
  }
  if (mode === "plane_change") {
    return { mode, via, delta_i_deg: numVal("mnvr-pc-di") };
  }
  return { mode, via };
}

function numVal(id) {
  const el = $(id); return el ? parseFloat(el.value) || 0 : 0;
}

async function computeManeuver() {
  if (!SID) { $("mnvr-result").textContent = "No active session."; return; }
  const actor = $("o-actor").value;
  if (!actor) { $("mnvr-result").textContent = "Select an asset first."; return; }
  const cell = CELL === "white" ? (ASSETS[actor]?.owner || "blue") : CELL;
  const mp = mnvrGatherParams();
  const body = { cell, actor, mode: mp.mode, params: mp };
  let res;
  try { res = await api.post(`/api/sessions/${SID}/maneuver/compute`, body); }
  catch { $("mnvr-result").textContent = "Server error"; return; }

  if (res.error) {
    $("mnvr-result").innerHTML = `<span style="color:var(--red)">${res.error}</span>`;
    $("mnvr-cost").textContent = "";
    return;
  }

  // Show cost
  $("mnvr-cost").textContent = `Δv = ${res.cost.toFixed(2)} m/s`;

  // Build preview text
  const o = res.new_orbit || {};
  const orbitStr = o.a_km
    ? `→ a=${o.a_km} km  e=${o.e}  i=${o.i_deg}°  ` +
      `alt ${o.alt_periapsis_km}–${o.alt_apoapsis_km} km  (${o.regime || "?"})`
    : "";
  let html = `<span class="ok">dv = [${res.dv.map((x) => x.toFixed(3)).join(", ")}] m/s\n${orbitStr}</span>`;
  if (res.second_burn) {
    const sb = res.second_burn;
    html += `\n<span class="second">2nd burn: ${sb.note}</span>`;
  }
  if (res.duration_s) {
    html += `\n<span>burn duration: ${res.duration_s} s (informational)</span>`;
  }
  $("mnvr-result").innerHTML = html;

  // Load the computed dv into o-params so the order system will use it
  const via = mp.via || "GS-NORTH";
  $("o-params").value = JSON.stringify({ dv: res.dv, via });
  previewOrder();
}

// -- Jam parameter assistant --------------------------------------------------

// Cached preview footprint drawn on the 2-D map until the user changes action/actor.
let JAM_PREVIEW = null;

function jamGatherParams() {
  // Audit 2026-06 Commands §C2 — Pₛ derives from modulation × power × bandwidth coverage
  // (defender state cuts it further at the resolver). The operator no longer types a
  // base success probability; the assistant panel surfaces the computed Pₛ as read-only.
  return {
    modulation: $("jam-mod")?.value || "barrage",
    power_w: parseFloat($("jam-power")?.value || "100"),
    bandwidth_hz: parseFloat($("jam-bw")?.value || "1000") * 1000,
    victim_bandwidth_hz: parseFloat($("jam-vbw")?.value || "1000") * 1000,
  };
}

function jamSummaryUpdate() {
  const mp = jamGatherParams();
  const el = $("jam-summary");
  if (el) el.textContent = `${mp.modulation} · ${mp.power_w}W · BW ${(mp.bandwidth_hz / 1000)|0}/${(mp.victim_bandwidth_hz / 1000)|0} kHz`;
}

async function computeJam() {
  if (!SID) { $("jam-result").textContent = "No active session."; return; }
  const actor = $("o-actor").value;
  if (!actor) { $("jam-result").textContent = "Select a jammer first."; return; }
  const cell = CELL === "white" ? (ASSETS[actor]?.owner || "blue") : CELL;
  const mp = jamGatherParams();
  let res;
  try { res = await api.post(`/api/sessions/${SID}/jam/compute`, { cell, actor, params: mp }); }
  catch { $("jam-result").textContent = "Server error"; return; }

  if (res.error) {
    $("jam-result").innerHTML = `<span style="color:var(--red)">${res.error}</span>`;
    JAM_PREVIEW = null;
    if (typeof drawMap === "function") drawMap();
    return;
  }

  const html = `<span class="ok">radius ≈ ${res.effective_radius_km} km · P<sub>s</sub> = ${res.success_prob}\n` +
               `draw ${res.power_draw_w} W · detect ${(res.detectability*100)|0}% · attr ${res.attribution_default}</span>`;
  $("jam-result").innerHTML = html;
  $("jam-summary").textContent = `${res.modulation} · r${res.effective_radius_km}km · Ps${res.success_prob}`;

  // Cache for the map overlay
  JAM_PREVIEW = {
    polygon: res.footprint_polygon,
    center: res.center,
    radius_km: res.effective_radius_km,
    modulation: res.modulation,
  };
  if (typeof drawMap === "function") drawMap();

  // Pre-fill the order params so the issued jam uses these settings
  const cur = (() => { try { return JSON.parse($("o-params").value || "{}"); } catch { return {}; } })();
  $("o-params").value = JSON.stringify({ ...cur, ...mp });
  previewOrder();
}

// -- Engage parameter assistant (Audit 2026-06 Commands §M2) ------------------

function engageGatherParams() {
  return {
    interceptor_class: $("engage-class")?.value || "mrbm_kkv",
    salvo_n: parseInt($("engage-salvo")?.value || "1", 10),
  };
}

function engageSummaryUpdate() {
  const mp = engageGatherParams();
  const el = $("engage-summary");
  if (el) el.textContent = `${mp.interceptor_class} · salvo ${mp.salvo_n}`;
  // Pre-fill the order params so the engage form picks up the assistant's choice.
  const cur = (() => { try { return JSON.parse($("o-params").value || "{}"); } catch { return {}; } })();
  $("o-params").value = JSON.stringify({ ...cur, ...mp });
  previewOrder();
}

async function computeEngage() {
  if (!SID) { $("engage-result").textContent = "No active session."; return; }
  const actor = $("o-actor").value;
  const target = $("o-target-manual")?.value || $("o-target").value;
  if (!actor || !target) { $("engage-result").textContent = "Select actor + target."; return; }
  const cell = CELL === "white" ? (ASSETS[actor]?.owner || "red") : CELL;
  const mp = engageGatherParams();
  let res;
  try {
    res = await api.post(`/api/sessions/${SID}/engage/compute`,
                         { cell, actor, target, params: mp });
  } catch { $("engage-result").textContent = "Server error"; return; }
  if (res.error) {
    $("engage-result").innerHTML = `<span style="color:var(--red)">${esc(res.error)}</span>`;
    return;
  }
  const pk = res.pk_estimate ?? res.success_prob ?? "—";
  const reach = res.in_reach === false ? " · OUT OF REACH" : "";
  $("engage-result").innerHTML =
    `<span class="ok">P<sub>k</sub> ≈ ${pk}${reach} · target alt ${res.target_alt_km ?? "—"} km</span>`;
}

// -- Cyber parameter assistant (Audit 2026-06 Commands §C2) -------------------

function cyberGatherParams() {
  return {
    vector: $("cyber-vector")?.value || "ground_modem",
    payload: $("cyber-payload")?.value || "seize_c2",
    dwell_s: parseFloat($("cyber-dwell")?.value || "0"),
  };
}

function cyberSummaryUpdate() {
  const mp = cyberGatherParams();
  const el = $("cyber-summary");
  if (el) el.textContent = `${mp.vector} · ${mp.payload} · dwell ${mp.dwell_s}s`;
  const cur = (() => { try { return JSON.parse($("o-params").value || "{}"); } catch { return {}; } })();
  $("o-params").value = JSON.stringify({ ...cur, ...mp });
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
  // IP-1130 — Observer has no fog-of-war view of its own; it reads whatever White Cell designated
  // (godview or a named cell), fetched via the exact same /godview or /view/{cell} calls every
  // other seat already makes below — no third, merged parsing path.
  let effectiveCell = CELL;
  if (CELL === "observer") {
    const d = await api.get(`/api/sessions/${SID}/observer/designation`).catch(() => ({ designation: "godview" }));
    effectiveCell = d.designation;
  }
  if (effectiveCell === "godview" || effectiveCell === "white") {
    const g = await api.get(`/api/sessions/${SID}/godview`);
    now = g.now;
    assets = Object.values(g.assets); tracks = g.tracks;
    effects = (g.active_effects || []).map((e) => ({ target: e.target, symptom: e.outcome, attributed: true }));
    ewin = (g.active_effects || []).map((e) => ({ target: e.target, category: e.category || "", start: e.start, end: e.end, attributed: true }));
    messages = g.messages || []; objectives = await api.get(`/api/sessions/${SID}/objectives`);
    Object.values(g.sensors || {}).forEach((s) => assets.push(s));
  } else {
    const v = await api.get(`/api/sessions/${SID}/view/${effectiveCell}`);
    now = v.now;
    assets = v.own_assets.concat(v.own_sensors); tracks = v.known_tracks;
    effects = v.visible_effects; ewin = v.effect_windows || [];
    messages = v.messages; objectives = v.objectives;
  }
  if (stale()) return;
  NOW = now;
  // Anchor the 1Hz interpolated ticker on this fresh sample; updateClockDisplay() paints the
  // readouts each second (and re-paints immediately here via the call below) — no need to set
  // textContent twice with identical strings.
  LAST_REFRESH_SERVER_NOW = now;
  LAST_REFRESH_WALL_MS = Date.now();
  // Multiplayer: cache the server clock state for the interpolated ticker AND keep the white-only
  // Pause/Resume button in sync. Cheap GET every refresh() — the server returns {running, rate,
  // now} from cached anchor fields.
  if (SID) {
    api.get(`/api/sessions/${SID}/clock`).then((s) => {
      SERVER_CLOCK_RUNNING_CACHED = !!s.running;
      const clockBtn = $("clock-toggle");
      if (clockBtn) clockBtn.textContent = s.running ? "⏸ Pause" : "▶ Resume";
    }).catch(() => {});
  }
  updateClockDisplay();
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
  const tbody = $("tracks").querySelector("tbody");
  tbody.innerHTML = tracks.map((t) => {
    const s = t.state_estimate;
    const kep = s && s.source === "kepler" && s.a_m != null;
    // Period: T = 2π√(a³/μ), μ_earth = 3.986e14 m³/s²
    const period_min = kep ? (2 * Math.PI * Math.sqrt(Math.pow(s.a_m, 3) / 3.986e14) / 60) : null;
    const coeHint = kep ? `<span class="coe-toggle-hint">▸</span>` : "—";
    const obsTime = t.last_observation ? iso(t.last_observation).replace("T", " ").replace(/\.\d+Z/, "Z") : "—";
    const coeBlock = kep ? `
      <tr class="track-coe-row">
        <td colspan="5">
          <div class="track-coe">
            <span class="track-coe-label">Observed</span><span>${obsTime}</span>
            <span class="track-coe-label">a</span><span>${(s.a_m / 1000).toFixed(1)} km</span>
            <span class="track-coe-label">e</span><span>${(+s.e).toFixed(4)}</span>
            <span class="track-coe-label">i</span><span>${(+s.i_deg).toFixed(2)}°</span>
            <span class="track-coe-label">Ω</span><span>${(+s.raan_deg).toFixed(2)}°</span>
            <span class="track-coe-label">ω</span><span>${(+s.argp_deg).toFixed(2)}°</span>
            <span class="track-coe-label">ν</span><span>${(+s.ta_deg).toFixed(2)}°</span>
            <span class="track-coe-label">T</span><span>${period_min.toFixed(1)} min</span>
            <span class="track-coe-label">Regime</span><span>${s.regime || "—"}</span>
          </div>
        </td>
      </tr>` : "";
    return `<tr class="track-main${kep ? " track-expandable" : ""}" title="${kep ? "Click to show orbital elements at observation time" : ""}">
      <td>${esc(t.object)}</td><td>${(+t.confidence).toFixed(2)}</td><td>${t.characterized}</td><td>${esc(t.classification)}</td><td>${coeHint}</td>
    </tr>${coeBlock}`;
  }).join("");
  // Toggle COE sub-rows on click.
  tbody.querySelectorAll("tr.track-expandable").forEach((row) => {
    row.addEventListener("click", () => {
      const next = row.nextElementSibling;
      if (next && next.classList.contains("track-coe-row")) {
        const open = next.style.display !== "none" && next.style.display !== "";
        next.style.display = open ? "none" : "";
        row.querySelector(".coe-toggle-hint").textContent = open ? "▸" : "▾";
      }
    });
  });
  // Collapse all COE rows on first render so the table stays compact.
  tbody.querySelectorAll("tr.track-coe-row").forEach((r) => { r.style.display = "none"; });
  // Target autocomplete: own assets + every known-track object id (with classification hint).
  // This is what Red/Blue can legally target — the fog-of-war boundary already filtered the
  // input data, so we just surface the ids the cell can see. Free-text entry still works for
  // White's god-view picks or for typing an id that hasn't been characterised yet.
  populateTargetOptions(assets, tracks);
  // FUTURE-WORK §4 Δv-economy panel: assets with non-zero Δv reserves shown with years-of-life
  // estimate at ~15 m/s/yr (typical LEO station-keeping budget). Helps the operator weigh
  // maneuver decisions against lifetime cost.
  const dv = $("deltav"); if (dv) {
    const rows = assets.filter((a) => a.resources && a.resources.delta_v_ms > 0).map((a) => {
      const dvms = +a.resources.delta_v_ms;
      const years = (dvms / 15).toFixed(1);
      const soc = a.bus_state ? Math.round(a.bus_state.power.battery_soc * 100) + "%" : "—";
      const aid = esc(a.id);
      const tip = `<span data-asset-ref="${aid}">${aid}</span>`;
      const lifeClass = dvms < 15 ? "red" : (dvms < 45 ? "yellow" : "green");
      return `<tr><td>${tip}</td><td>${dvms.toFixed(1)}</td><td>${soc}</td><td class="${lifeClass}">${years}</td></tr>`;
    });
    dv.querySelector("tbody").innerHTML = rows.length ? rows.join("")
      : "<tr><td colspan=4 class='muted'>(no maneuver-capable assets)</td></tr>";
  }
  $("effects").innerHTML = effects.map((e) => `<li>${esc(e.target)}: ${esc(e.symptom)} ${e.attributed ? "(attributed)" : "(source unknown)"}</li>`).join("");
  $("messages").innerHTML = messages.map((m) => `<li>${esc(m.text)}</li>`).join("");
  renderObjectives(objectives);
  renderBrief();

  // Command menu: populate actor list (own assets + sensors that can act; network sensors excluded).
  const actorIds = assets.filter((a) => ACTIONS_BY_KIND[a.kind] && !a.network).map((a) => a.id);
  const prev = $("o-actor").value;
  const prevList = [...$("o-actor").options].map((o) => o.value).join(",");
  const newList = actorIds.join(",");
  if (prevList !== newList) {
    $("o-actor").innerHTML = actorIds.map((i) => `<option>${i}</option>`).join("");
    if (actorIds.includes(prev)) $("o-actor").value = prev;
    onActorChange();
  }
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
  if (DRILL.asset) {
    const lt = ASSETS[DRILL.asset]?.last_tel || 0;
    if (lt !== DRILL_LAST_TEL) openDrill(DRILL.asset);  // new telemetry arrived — full rebuild
    else updateDrillTitle();                             // pass-gated: just age the stale badge
    renderOrbitalElements(DRILL.asset);                  // COEs refresh every poll (post-maneuver visible within ~1.5s)
  }
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
  renderConjunctions();   // FW §11.C.14
  renderCoaching();       // FW §11.D.17
  renderActivity();       // per-cell Gantt timeline
  if (TASK_MODE === "ssn") { ssnCoverage(); renderSsnQueue(CELL === "white" ? "blue" : CELL); }
}

// ---------------------------------------------------------------------------
// Cell activity Gantt timeline (past / present / scheduled).
// Fog-of-war is server-side: White sees all three cells, Blue/Red see only own.
// ---------------------------------------------------------------------------
let ACTIVITY = null;

async function renderActivity() {
  const c = $("activity-canvas"); if (!c || !SID) return;
  const past = parseInt($("activity-past")?.value || "1800", 10);
  const future = parseInt($("activity-future")?.value || "7200", 10);
  let data;
  try {
    data = await api.get(`/api/sessions/${SID}/activity/${CELL}?past_window_s=${past}&future_window_s=${future}`);
  } catch { return; }
  ACTIVITY = data;
  drawActivityGantt();
}

// Cell colour map (matches the cell-accent palette in style.css).
const ACTIVITY_CELL_COLOR = {
  blue:    { fill: "rgba(90,143,224,0.85)",  ring: "#5a8fe0" },
  red:     { fill: "rgba(224,122,122,0.85)", ring: "#e07a7a" },
  neutral: { fill: "rgba(155,170,190,0.80)", ring: "#9faabd" },
};
const ACTIVITY_HITBOX = [];   // populated by drawActivityGantt for click-to-detail

function drawActivityGantt() {
  const c = $("activity-canvas"); if (!c || !ACTIVITY) return;
  const ctx = c.getContext("2d");
  const W = c.width, H = c.height;
  ctx.fillStyle = "#070b10"; ctx.fillRect(0, 0, W, H);
  ACTIVITY_HITBOX.length = 0;

  const { now, t_start, t_end, cells } = ACTIVITY;
  const activities = ACTIVITY.activities.filter((a) => a.status !== "cancelled");
  const span = Math.max(1, t_end - t_start);
  const LEFT = 60, RIGHT = 12, TOP = 22, BOT = 18;
  const X = (t) => LEFT + (t - t_start) / span * (W - LEFT - RIGHT);
  // Hourly tick marks
  ctx.strokeStyle = "#1b2531"; ctx.lineWidth = 1;
  const oneHour = 3600 * 1_000_000;
  const firstTick = Math.ceil(t_start / oneHour) * oneHour;
  ctx.font = "10px monospace"; ctx.fillStyle = "#7a8aa0";
  for (let t = firstTick; t <= t_end; t += oneHour) {
    const x = X(t);
    ctx.beginPath(); ctx.moveTo(x, TOP - 4); ctx.lineTo(x, H - BOT + 4); ctx.stroke();
    ctx.fillText(iso(t).slice(11, 16), x + 2, TOP - 8);
  }
  // "Now" vertical line — bright green
  const nowX = X(now);
  ctx.strokeStyle = "#6fcf6f"; ctx.lineWidth = 2;
  ctx.beginPath(); ctx.moveTo(nowX, TOP - 6); ctx.lineTo(nowX, H - BOT + 6); ctx.stroke();
  ctx.fillStyle = "#6fcf6f"; ctx.font = "10px monospace";
  ctx.fillText("NOW", nowX - 12, H - 4);

  // Lane layout: one lane per cell.  Stack bars inside each lane vertically.
  const laneCount = cells.length;
  const laneH = (H - TOP - BOT) / Math.max(1, laneCount);
  cells.forEach((cell, ci) => {
    const yLane = TOP + ci * laneH;
    // Lane background + label
    ctx.fillStyle = "rgba(255,255,255,0.02)";
    ctx.fillRect(LEFT, yLane, W - LEFT - RIGHT, laneH - 2);
    ctx.fillStyle = ACTIVITY_CELL_COLOR[cell]?.ring || "#9faabd";
    ctx.font = "12px monospace";
    ctx.fillText(cell.toUpperCase(), 8, yLane + 14);
    // Group bars by actor inside the lane → sub-rows
    const cellRows = activities.filter((a) => a.cell === cell);
    const actors = [...new Set(cellRows.map((a) => a.actor))];
    actors.forEach((actor, ai) => {
      const subY = yLane + 18 + ai * 18;
      if (subY + 14 > yLane + laneH - 2) return;   // ran out of room
      ctx.fillStyle = "#9faabd"; ctx.font = "10px monospace";
      ctx.fillText(actor.slice(0, 12), 8, subY + 10);
      cellRows.filter((a) => a.actor === actor).forEach((a) => {
        const x0 = Math.max(LEFT, X(a.start));
        const x1 = Math.min(W - RIGHT, X(a.end));
        const w = Math.max(2, x1 - x0);
        drawActivityBar(ctx, x0, subY + 2, w, 12, a, cell);
        ACTIVITY_HITBOX.push({ x: x0, y: subY + 2, w, h: 12, a });
      });
    });
  });
}

function drawActivityBar(ctx, x, y, w, h, a, cell) {
  const col = ACTIVITY_CELL_COLOR[cell] || ACTIVITY_CELL_COLOR.neutral;
  switch (a.status) {
    case "executed":
      ctx.fillStyle = col.fill; ctx.fillRect(x, y, w, h); break;
    case "active":
      ctx.fillStyle = col.fill; ctx.fillRect(x, y, w, h);
      ctx.strokeStyle = "#6fcf6f"; ctx.lineWidth = 2; ctx.strokeRect(x, y, w, h); break;
    case "queued":
    case "scheduled":
      ctx.strokeStyle = col.ring; ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 3]); ctx.strokeRect(x, y, w, h); ctx.setLineDash([]); break;
    case "cancelled":
      ctx.fillStyle = "rgba(120,120,120,0.30)"; ctx.fillRect(x, y, w, h);
      ctx.strokeStyle = "rgba(180,180,180,0.6)"; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(x, y + h / 2); ctx.lineTo(x + w, y + h / 2); ctx.stroke(); break;
    case "rejected":
      ctx.strokeStyle = "#e06a6a"; ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(x, y); ctx.lineTo(x + w, y + h);
      ctx.moveTo(x + w, y); ctx.lineTo(x, y + h);
      ctx.stroke(); break;
    default:
      ctx.fillStyle = col.fill; ctx.fillRect(x, y, w, h);
  }
  // Label: dark text on filled bars (executed/active/default); bright on outlined future bars.
  if (w > 40) {
    const unfilled = a.status === "queued" || a.status === "scheduled";
    ctx.fillStyle = unfilled ? "#d6e8ff" : "#0a0f15";
    ctx.font = "10px monospace";
    ctx.fillText(a.action.slice(0, Math.floor(w / 7)), x + 4, y + 9);
  }
}

// Click-to-detail: print the matched bar's metadata into #activity-detail.
addEventListener("DOMContentLoaded", () => {
  const c = $("activity-canvas"); if (!c) return;
  c.addEventListener("click", (e) => {
    const rect = c.getBoundingClientRect();
    const scaleX = c.width / rect.width;
    const x = (e.clientX - rect.left) * scaleX;
    const y = (e.clientY - rect.top) * (c.height / rect.height);
    const hit = ACTIVITY_HITBOX.find((b) => x >= b.x && x <= b.x + b.w && y >= b.y && y <= b.y + b.h);
    const el = $("activity-detail"); if (!el) return;
    if (!hit) { el.textContent = "—"; return; }
    const a = hit.a;
    el.textContent = `${a.cell.toUpperCase()} · ${a.actor} · ${a.action}` +
      (a.target ? ` → ${a.target}` : "") +
      ` · ${a.status} · ${iso(a.start)} → ${iso(a.end)}` +
      (a.delivery_path ? ` · ${a.delivery_path}` : "");
  });
  $("activity-past") && $("activity-past").addEventListener("change", renderActivity);
  $("activity-future") && $("activity-future").addEventListener("change", renderActivity);
});

// FW §11.C.14 — conjunction screening panel.  Each entry shows the two objects,
// range/time-to-CA, and an "Evade" button that fires the prop.collision_avoid verb.
// Pretty-print an objective id: "deliver_isr" → "Deliver ISR", "keep_custody" → "Keep custody".
// Treats short trailing tokens (≤4 chars) as acronyms (ISR, EW, SDA, GS) and uppercases them.
function prettyObjectiveId(id) {
  const parts = String(id || "").split("_").filter(Boolean);
  if (!parts.length) return "(unnamed)";
  return parts
    .map((p, i) => (p.length <= 4 && i > 0 ? p.toUpperCase() : p[0].toUpperCase() + p.slice(1)))
    .join(" ");
}

// Render the per-side objectives status as a colored list rather than raw JSON. Two shapes:
//   White (/objectives endpoint): nested {blue: {id: bool}, red: {id: bool}}
//   Blue/Red (CellView.objectives): flat per-cell {id: bool} — fog-filtered by the server.
// Met rows are green-accented; unmet rows are dim+red.
function renderObjectives(objectives) {
  const el = $("objectives");
  if (!el) return;
  const row = (id, met) => {
    const cls = met ? "met" : "unmet";
    const mark = met ? "✓" : "✗";
    return `<div class="obj-row ${cls}"><span class="obj-mark">${mark}</span><span class="obj-id">${prettyObjectiveId(id)}</span></div>`;
  };
  const entries = Object.entries(objectives || {});
  if (entries.length === 0) { el.innerHTML = "<div class='obj-empty'>(no objectives)</div>"; return; }
  // Heuristic: if every value is a plain object (not bool), this is the nested {side: {...}} shape.
  const nested = entries.every(([, v]) => v && typeof v === "object" && !Array.isArray(v));
  const parts = [];
  if (nested) {
    for (const [side, sideObj] of entries) {
      parts.push(`<div class="obj-side">${side}</div>`);
      const sideEntries = Object.entries(sideObj || {});
      if (!sideEntries.length) parts.push("<div class='obj-empty'>(no objectives)</div>");
      else for (const [id, met] of sideEntries) parts.push(row(id, met));
    }
  } else {
    for (const [id, met] of entries) parts.push(row(id, met));
  }
  el.innerHTML = parts.join("");
}

async function renderConjunctions() {
  const el = $("conjunction-list"); if (!el) return;
  const cell = CELL === "white" ? "white" : CELL;
  let list = [];
  try { list = await api.get(`/api/sessions/${SID}/conjunctions/${cell}`); } catch { list = []; }
  if (!list.length) { el.className = "muted"; el.textContent = "(no conjunction warnings)"; return; }
  el.className = "";
  el.innerHTML = list.map((c, i) => {
    const tca = c.t_close ? new Date(c.t_close / 1000).toISOString().slice(11, 19) : "?";
    const own = (ASSETS[c.a] || ASSETS[c.b]);
    const evadeBtn = own
      ? `<button class="vbtn" data-evade="${ASSETS[c.a] ? c.a : c.b}">Evade</button>`
      : "";
    return `<div class="qrow"><span><b>${c.a}</b> ↔ <b>${c.b}</b></span>
      <span>${c.range_km != null ? c.range_km.toFixed(1) + " km" : "?"}</span>
      <span>CA ${tca}</span>${evadeBtn}</div>`;
  }).join("");
  el.querySelectorAll(".vbtn[data-evade]").forEach((b) => b.onclick = async () => {
    const actor = b.dataset.evade;
    const o = { cell: ASSETS[actor]?.owner || cell, actor,
                action: "command", target: null,
                params: { verb: "prop.collision_avoid" } };
    try {
      const ack = await api.post(`/api/sessions/${SID}/order`, o);
      b.textContent = ack.ok ? "Queued" : "REJECT";
    } catch { b.textContent = "ERR"; }
    setTimeout(refresh, 600);
  });
}

// FW §11.D.17 — coaching notes panel.
async function renderCoaching() {
  const el = $("coaching-list"); if (!el) return;
  const cell = CELL === "white" ? "white" : CELL;
  let notes = [];
  try { notes = await api.get(`/api/sessions/${SID}/coaching/${cell}`); } catch { notes = []; }
  if (!notes.length) { el.className = "muted"; el.textContent = "(no notes)"; return; }
  el.className = "";
  el.innerHTML = notes.map((n) =>
    `<div class="qrow"><span><b>${n.title || "(note)"}</b><br><span class="muted">${n.body || ""}</span></span></div>`
  ).join("");
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

// Latest target data cached so the actor-aware target dropdowns can rebuild when the
// operator changes actor/action without another network round-trip.
let TARGET_ASSETS = [];
let TARGET_TRACKS = [];

function populateTargetOptions(assets, tracks) {
  TARGET_ASSETS = assets || [];
  TARGET_TRACKS = tracks || [];
  populateTargetPicker();
}

// Group every target the current fog-of-war view exposes, excluding `excludeOwner`'s own side.
// Fog-of-war correct: Blue/Red see their known_tracks (the only enemy objects they've
// identified) plus any non-own asset their view exposes; White (god view) sees every asset,
// filtered by whichever owner is passed in. Ground stations / sensors are never offered as
// offensive targets — only the four physically-targetable kinds below.
const TARGETABLE_KINDS = new Set(["satellite", "space_based", "interceptor", "directed_energy"]);
function buildTargetGroups(excludeOwner) {
  const seen = new Set();
  const byOwner = {};   // owner -> [{id, label}]
  const add = (id, owner, label) => {
    if (!id || seen.has(id)) return;
    seen.add(id);
    const grp = owner || "unknown";
    (byOwner[grp] = byOwner[grp] || []).push({ id, label });
  };
  // Known enemy tracks (these are objects the cell has custody/belief on — always valid targets).
  (TARGET_TRACKS || []).forEach((t) => {
    if (!t.object) return;
    const cls = t.classification || "unknown";
    const ch = t.characterized ? "char" : "uncertain";
    add(t.object, t.owner || "track", `${t.object} — ${cls} · ${ch}`);
  });
  // Assets the view exposes that are not the excluded side and are physically targetable.
  (TARGET_ASSETS || []).forEach((a) => {
    if (!a.id || !TARGETABLE_KINDS.has(a.kind)) return;
    if (excludeOwner && a.owner === excludeOwner) return;   // not your own side
    add(a.id, a.owner, `${a.id} — ${a.owner || "?"} · ${a.kind}`);
  });
  return { byOwner, seen };
}

function targetOptionsHtml(byOwner, emptyLabel) {
  const groups = Object.keys(byOwner).sort();
  let html = `<option value="">${esc(emptyLabel)}</option>`;
  if (!groups.length) {
    // Nothing tracked yet — this is expected at the start of a scenario (before any sensor has
    // been tasked) or whenever the operator hasn't built custody on the intended target. The
    // "or id" field beside this dropdown is exactly for that case: an operator can still task a
    // sensor (or jam/cyber) against an id they know from the mission brief but haven't tracked.
    html += `<option value="" disabled>no known targets yet — type an id below, or task a sensor to build custody</option>`;
  } else if (groups.length === 1) {
    html += byOwner[groups[0]].map((o) => `<option value="${esc(o.id)}">${esc(o.label)}</option>`).join("");
  } else {
    html += groups.map((g) =>
      `<optgroup label="${esc(g)} targets">` +
      byOwner[g].map((o) => `<option value="${esc(o.id)}">${esc(o.label)}</option>`).join("") +
      `</optgroup>`).join("");
  }
  return html;
}

// Populate the "known targets on the other side" <select>s: the compose form's Target field
// (Satellite command) and the Tasking rail's Target field. Both draw on the same fog-of-war
// filtered lists — Red and Blue otherwise have no way to see what the other cell has. Each
// select is paired with a manual "or id" text input (…-manual) for targets not yet tracked —
// most importantly, the "observe" action IS how custody gets built in the first place, so its
// target can never come pre-populated from a track the operator doesn't have yet.
function populateTargetPicker() {
  const orderSel = $("o-target"), orderManual = $("o-target-manual");
  if (orderSel) {
    const actor = $("o-actor") ? $("o-actor").value : "";
    const actorOwner = (ASSETS[actor] && ASSETS[actor].owner) || (CELL !== "white" ? CELL : null);
    const prev = orderSel.value;
    const { byOwner, seen } = buildTargetGroups(actorOwner);
    orderSel.innerHTML = targetOptionsHtml(byOwner, "(pick a known target…)");
    if (prev && seen.has(prev)) orderSel.value = prev;
    // Only jam/engage/cyber/observe carry an order-level target (TARGET_REQUIRED_ACTIONS) —
    // blank + disable both fields for every other action so neither looks required.
    const action = $("o-action") ? $("o-action").value : "";
    const needsTarget = TARGET_REQUIRED_ACTIONS.has(action);
    orderSel.disabled = !needsTarget;
    if (orderManual) orderManual.disabled = !needsTarget;
    if (!needsTarget) {
      orderSel.value = "";
      if (orderManual) orderManual.value = "";
    }
  }

  const taskSel = $("task-target");
  if (taskSel) {
    // Tasking always plans sensor collection against the other side, on behalf of the acting
    // cell (White tasks as Blue — see planTask()'s own `cell` resolution).
    const taskOwner = CELL === "white" ? "blue" : CELL;
    const prev = taskSel.value;
    const { byOwner, seen } = buildTargetGroups(taskOwner);
    taskSel.innerHTML = targetOptionsHtml(byOwner, "(pick a target…)");
    if (prev && seen.has(prev)) taskSel.value = prev;
  }
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
  stopRealtimeClock();
  SID = (await api.post("/api/sessions/load_save", state)).session;
  location.hash = SID;   // multiplayer: resumed session is also shareable
  $("session").textContent = "session " + SID; $("start").disabled = false;
  updateSessionSummary(state.vignette_id || "resumed", state.started);
  const injects = await api.get(`/api/sessions/${SID}/injects`).catch(() => []);
  $("inject-sel").innerHTML = injects.map((i) => `<option value="${esc(i.id)}">${esc(i.label)}</option>`).join("") || "<option>(none)</option>";
  await loadInjectLibrary();
  // Resumed sessions intentionally load with the server clock PAUSED so they don't fast-forward
  // the wall-time gap since the save. White clicks Start (or the Resume button) to re-arm.
  if (state.started) startRealtimeClock();
  await refresh();
  refreshAssessment();  // IP-2010 — populate once on load; the panel's own button refreshes it later
  refreshStaffingReport();  // IP-1151 — populate once on load; assignment actions refresh it after
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

// IP-1151 — seat-to-role staffing report (unmet mandatory roles_needed entries). Refreshed on
// session load and after each assignment, not polled continuously — it only changes in response
// to a White-Cell assignment action, not to the passage of sim time.
async function refreshStaffingReport() {
  if (!SID) return;
  const report = await api.get(`/api/sessions/${SID}/roles/staffing`).catch(() => null);
  if (!report) return;
  $("staffing-report").textContent = report.length
    ? report.map((r) => `unmet: ${r.asset_or_constellation} / ${r.role}`).join("\n")
    : "fully staffed (or this vignette declares no roles_needed)";
}

// IP-2010 — competency assessment rubric (custody quality / window discipline / belief-truth
// divergence). Manual refresh, not polled every tick like the rest of refresh(): each dimension
// replays the eventlog per decision, so it's a debrief-time report, not a live gauge.
async function refreshAssessment() {
  if (!SID) return;
  const rep = await api.get(`/api/sessions/${SID}/assessment`).catch(() => null);
  if (!rep) return;
  const fmt = (side) => Object.entries(rep[side] || {})
    .filter(([k]) => k !== "disclosure")
    .map(([k, v]) => `${k}: ${v}`).join("\n") || "—";
  $("assessment-blue").textContent = fmt("blue");
  $("assessment-red").textContent = fmt("red");
  $("assessment-disclosure").textContent = (rep.blue && rep.blue.disclosure) || (rep.red && rep.red.disclosure) || "";
}

// ---- 2D belief map with pan / zoom / center / layers ----
function drawMap() {
  if (!SCENE) return;
  const c = $("map"), x = c.getContext("2d");
  // Brighter ocean fill so coastlines + grid have something to register against on dark monitors.
  x.fillStyle = "#0e2740"; x.fillRect(0, 0, c.width, c.height);
  const PX = (lon) => c.width / 2 + (lon - mapCam.lon) * (c.width / 360) * mapCam.zoom;
  const PY = (lat) => c.height / 2 - (lat - mapCam.lat) * (c.height / 180) * mapCam.zoom;
  if (mapCam.map && window.WorldMap && WorldMap.ready()) {
    WorldMap.draw(x, (lon, lat) => ({ x: PX(lon), y: PY(lat), front: true }), { maxJump: c.width * 0.5, coastWidth: 1.3 });
  }
  if (mapCam.grid) {
    x.strokeStyle = "rgba(140,180,215,0.45)"; x.lineWidth = 1;
    for (let lon = -180; lon <= 180; lon += 30) { x.beginPath(); x.moveTo(PX(lon), 0); x.lineTo(PX(lon), c.height); x.stroke(); }
    for (let lat = -90; lat <= 90; lat += 30) { x.beginPath(); x.moveTo(0, PY(lat)); x.lineTo(c.width, PY(lat)); x.stroke(); }
  }
  // §10.C.10 — terminator overlay (computed from sun_lat/lon already in SceneView).
  if (SCENE.sun_lat_deg != null && window.drawTerminator) {
    window.drawTerminator(x, c, PX, PY, SCENE.sun_lat_deg, SCENE.sun_lon_deg);
  }
  // §10.A.1 — own-asset marker color tracks the active cell's accent.
  // §4 APP-6 symbology — payload-specific shapes via Symbology.draw().
  // User-added FW #2 — ground tracks: dim polyline of the sub-satellite path for the next orbit.
  const accent = window.cellAccent ? cellAccent() : "#6fcf6f";
  if (mapCam.tracks !== false) {
    x.strokeStyle = "rgba(210,225,245,0.65)"; x.lineWidth = 1.2;
    SCENE.assets.forEach((a) => {
      if (!a.on_orbit || !a.track || a.track.length < 2) return;
      x.beginPath();
      let lastX = null;
      a.track.forEach((p, i) => {
        const X = PX(p[1]), Y = PY(p[0]);
        // Break the polyline when the sub-point wraps across the antimeridian.
        if (lastX !== null && Math.abs(X - lastX) > c.width * 0.5) { x.stroke(); x.beginPath(); x.moveTo(X, Y); }
        else if (i === 0) x.moveTo(X, Y);
        else x.lineTo(X, Y);
        lastX = X;
      });
      x.stroke();
    });
  }
  x.fillStyle = accent;
  SCENE.assets.forEach((a) => {
    const px = PX(a.lon_deg), py = PY(a.lat_deg);
    if (window.Symbology) Symbology.draw(x, px, py, a, { r: 5 });
    else { if (a.on_orbit) { x.beginPath(); x.moveTo(px, py - 5); x.lineTo(px - 5, py + 4); x.lineTo(px + 5, py + 4); x.closePath(); x.fill(); } else x.fillRect(px - 4, py - 4, 8, 8); }
    x.fillStyle = "#e6edf7"; x.font = "11px monospace"; x.fillText(a.id, px + 7, py + 3); x.fillStyle = accent;
  });
  if (mapCam.tracks) SCENE.tracks.forEach((t) => {
    const px = PX(t.lon_deg), py = PY(t.lat_deg), r = Math.max(4, Math.min(40, t.uncertainty_km / 18));
    x.strokeStyle = t.characterized ? "#ffd35a" : "#ff8585";
    x.lineWidth = 1.5;
    x.beginPath(); x.arc(px, py, r, 0, 2 * Math.PI); x.stroke();
    x.fillStyle = x.strokeStyle; x.beginPath(); x.arc(px, py, 2.5, 0, 2 * Math.PI); x.fill();
    x.fillStyle = "#e6edf7"; x.fillText(`${t.object} ±${t.uncertainty_km}km`, px + 6, py - 6);
  });
  // Jam preview footprint (read-only overlay, cleared when action != jam)
  if (window.JAM_PREVIEW && JAM_PREVIEW.polygon && JAM_PREVIEW.polygon.length > 2) {
    x.save();
    x.strokeStyle = "rgba(255,120,80,0.85)";
    x.fillStyle   = "rgba(255,120,80,0.10)";
    x.lineWidth = 1.5;
    x.setLineDash([6, 4]);
    x.beginPath();
    JAM_PREVIEW.polygon.forEach((c, i) => {
      const px_ = PX(c[1]), py_ = PY(c[0]);
      if (i === 0) x.moveTo(px_, py_); else x.lineTo(px_, py_);
    });
    x.closePath(); x.fill(); x.stroke();
    x.setLineDash([]);
    if (JAM_PREVIEW.center) {
      const cx = PX(JAM_PREVIEW.center.lon_deg);
      const cy = PY(JAM_PREVIEW.center.lat_deg);
      x.fillStyle = "rgba(255,120,80,0.95)";
      x.beginPath(); x.arc(cx, cy, 3, 0, 2*Math.PI); x.fill();
      x.font = "10px monospace";
      x.fillText(`jam ${JAM_PREVIEW.modulation} r${JAM_PREVIEW.radius_km}km`, cx + 5, cy - 4);
    }
    x.restore();
  }
  // ISR collection footprints — translucent filled polygon + label with beam mode
  if (mapCam.tracks !== false && SCENE.footprints && SCENE.footprints.length) {
    SCENE.footprints.forEach((fp) => {
      if (!fp.corners || fp.corners.length < 3) return;
      x.save();
      x.strokeStyle = "rgba(100,220,255,0.70)";
      x.fillStyle   = "rgba(100,220,255,0.08)";
      x.lineWidth = 1.5;
      x.setLineDash([4, 3]);
      x.beginPath();
      fp.corners.forEach((c, i) => {
        const px_ = PX(c[1]), py_ = PY(c[0]);
        if (i === 0) x.moveTo(px_, py_); else x.lineTo(px_, py_);
      });
      x.closePath();
      x.fill();
      x.stroke();
      x.setLineDash([]);
      // Label at the centroid
      const cLat = fp.corners.reduce((s, c) => s + c[0], 0) / fp.corners.length;
      const cLon = fp.corners.reduce((s, c) => s + c[1], 0) / fp.corners.length;
      x.fillStyle = "rgba(100,220,255,0.8)";
      x.font = "10px monospace";
      x.fillText(`${fp.target} [${fp.beam_mode}]`, PX(cLon) + 2, PY(cLat) - 3);
      x.restore();
    });
  }
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
let DRILL_LAST_TEL = 0;  // last_tel timestamp at the time of the last full drill render

function _renderDrillTitle(assetId, lt, busMode) {
  const ageS = lt > 0 ? Math.max(0, Math.round((NOW - lt) / 1e6)) : null;
  const staleTag = (ageS != null && ageS > 60)
    ? ` · <span class="muted">stale since ${iso(lt)} (${Math.floor(ageS / 60)}m)</span>`
    : (ageS != null ? ` · <span class="muted">as-of ${iso(lt)}</span>` : "");
  $("drill-title").innerHTML = `${assetId} — bus ${busMode}${staleTag}`;
}

function updateDrillTitle() {
  if (!DRILL.asset) return;
  const lt = ASSETS[DRILL.asset]?.last_tel || 0;
  const titleEl = $("drill-title");
  _renderDrillTitle(DRILL.asset, lt, titleEl.dataset.busMode || "—");
}

// Classical orbital elements for the selected asset, sourced from the scene
// (no extra fetch). Called on drill open AND on every poll refresh so the
// block reflects post-maneuver elements within ~1.5s of execution.
function renderOrbitalElements(assetId) {
  const host = $("drill-orbit");
  if (!host) return;
  const ra = SCENE && SCENE.assets && SCENE.assets.find((a) => a.id === assetId);
  if (!ra || !ra.on_orbit || ra.a_km == null) { host.innerHTML = ""; return; }
  const fmt = (v, d) => (v == null ? "—" : Number(v).toFixed(d));
  host.innerHTML =
    `<h3>Orbital elements</h3>` +
    `<div class="coes">` +
      `<span><b>a</b> ${fmt(ra.a_km, 1)} km</span>` +
      `<span><b>period</b> ${fmt(ra.period_min, 1)} min</span>` +
      `<span><b>e</b> ${fmt(ra.e, 4)}</span>` +
      `<span><b>i</b> ${fmt(ra.i_deg, 2)}°</span>` +
      `<span><b>Ω</b> ${fmt(ra.raan_deg, 2)}°</span>` +
      `<span><b>ω</b> ${fmt(ra.argp_deg, 2)}°</span>` +
      `<span><b>ν</b> ${fmt(ra.ta_deg, 2)}°</span>` +
      `<span><b>alt</b> ${fmt(ra.alt_m / 1000, 1)} km</span>` +
      (ra.regime ? `<span class="muted">${ra.regime}</span>` : "") +
    `</div>`;
}

async function openDrill(assetId) {
  DRILL.asset = assetId;
  let tele;
  try { tele = await api.get(`/api/sessions/${SID}/telemetry/${CELL}/${assetId}`); }
  catch { $("drill-title").textContent = `${assetId} — no telemetry (fog / not your asset)`; $("drill-params").innerHTML = ""; renderOrbitalElements(assetId); return; }
  DRILL_DB = {};
  Object.values(tele.subsystems).forEach((arr) => arr.forEach((p) => (DRILL_DB[p.id] = p)));
  const lt = ASSETS[assetId]?.last_tel || 0;
  DRILL_LAST_TEL = lt;
  const titleEl = $("drill-title");
  titleEl.dataset.busMode = tele.bus_mode || "—";
  _renderDrillTitle(assetId, lt, tele.bus_mode || "—");
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
  // Tiny inline sparklines (§5.1) — one series per param chip; ignore failures silently.
  // Same n (120) and same default window as the large drill-down graph so the two are the
  // same curve at the same resolution — only the size differs (audit Jun 2026 §graphs).
  document.querySelectorAll("#drill-params .spark").forEach(async (cv) => {
    try {
      const s = await api.get(`/api/sessions/${SID}/telemetry/${CELL}/${assetId}/${cv.dataset.param}?n=120`);
      window.Graph && Graph.spark(cv, s, DRILL_DB[cv.dataset.param]);
    } catch { /* offline param — silent */ }
  });
  $("drill-log").textContent = (tele.log || []).join("\n") || "(all nominal)";
  document.querySelectorAll("#drill-params .pchip").forEach((c) => c.onclick = () => drawParam(c.dataset.param));
  document.querySelectorAll("#drill-params .vbtn").forEach((b) => b.onclick = () => loadVerb(b.dataset.actor, b.dataset.verb));
  renderRecovery(assetId, tele.bus_mode);
  renderOrbitalElements(assetId);
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
  "comms.enable_isl": "comms", "comms.config_link": "comms", "def.frequency_hop": "comms",
  "satcom.mitigate_interference": "payload", "satcom.shift_users": "payload",
  "satcom.set_frequency_plan": "payload", "satcom.reconfigure_beam": "payload",
  "satcom.geolocate_interference": "payload",
  "isr.collect_now": "payload", "isr.schedule_collection": "payload", "isr.set_mode": "payload",
  "sigint.task_collection": "payload", "wx.schedule_collection": "payload",
  "wx.request_sector": "payload", "mw.add_stare_area": "payload", "def.harden": "payload",
  "pnt.flex_power": "payload", "pnt.set_health_flag": "payload",
  "sda.task_search": "payload", "sda.task_track": "payload", "sda.task_characterize": "payload",
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
  // Multiplayer: Pause/Resume drives the server-authoritative clock for ALL connected tabs.
  const clockBtn = $("clock-toggle");
  if (clockBtn) clockBtn.onclick = async () => {
    if (!SID) return;
    const st = await api.get(`/api/sessions/${SID}/clock`);
    await setServerClock(!st.running);
  };
  $("fire-inject").onclick = fireInject; $("issue").onclick = issueOrder;
  // FW §11.D.19 — inject builder
  if ($("inject-lib-load")) $("inject-lib-load").onclick = loadInjectTemplate;
  if ($("inject-lib")) $("inject-lib").onchange = loadInjectTemplate;
  if ($("inject-when")) $("inject-when").onchange = onInjectWhenChange;
  if ($("inject-build-fire")) $("inject-build-fire").onclick = fireBuiltInject;
  $("save").onclick = () => SID && saveSession();
  $("loadbtn").onclick = () => $("loadfile").click();
  $("loadfile").onchange = (e) => e.target.files[0] && loadSaveFile(e.target.files[0]);
  $("aar-slider").oninput = (e) => aarAt(e.target.value);
  if ($("assessment-refresh")) $("assessment-refresh").onclick = refreshAssessment;
  // IP-1130 — White Cell designates the read-only Observer seat's view.
  if ($("observer-designation")) $("observer-designation").onchange = (e) => {
    if (SID) api.post(`/api/sessions/${SID}/observer/view`, { cell: "white", designation: e.target.value });
  };
  // IP-1151 — White Cell binds a seat to {asset_or_constellation, role} against the vignette's
  // declared roles_needed; Start is refused server-side while any mandatory entry is unmet.
  if ($("role-assign")) $("role-assign").onclick = async () => {
    if (!SID) return;
    const seat = $("role-seat").value.trim(), asset = $("role-asset").value.trim();
    if (!seat || !asset) return;
    await api.post(`/api/sessions/${SID}/roles/assign`, {
      cell: "white", seat, asset_or_constellation: asset, role: $("role-kind").value,
    });
    refreshStaffingReport();
  };
  $("o-actor").onchange = onActorChange; $("o-action").onchange = onActionChange;
  $("o-target").onchange = previewOrder; $("o-params").oninput = previewOrder;
  $("o-target-manual").oninput = previewOrder;
  $("drill-nominal").onchange = () => DRILL.param && drawParam(DRILL.param);
  $("drill-overlay").onchange = () => DRILL.param && drawParam(DRILL.param);
  $("present").onchange = (e) => document.body.classList.toggle("present", e.target.checked);
  // Pop-out submenu: each button opens a new window joined to the same session at the layout token.
  document.querySelectorAll(".popout-btn").forEach((b) => b.onclick = () => popOut(b.dataset.layout));
  $("task-plan").onclick = planTask;
  document.querySelectorAll("#task-mode .chip").forEach((b) => b.onclick = () => setTaskMode(b.dataset.tmode));
  $("task-regime").onchange = ssnCoverage;
  if ($("task-beam-mode")) $("task-beam-mode").onchange = updateIsrInfo;
  if ($("task-look-angle")) $("task-look-angle").oninput = updateIsrInfo;
  const tzSel = document.getElementById("tz-select");
  if (tzSel) tzSel.onchange = () => {
    const localEl = document.getElementById("now-local");
    if (localEl) localEl.textContent = localTimeStr(NOW);
  };
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
  // Toolbar dropdown menus (View + Settings). Each pair shares the same open/close pattern;
  // opening one closes the others, plus outside-click + Escape close any open menu.
  const menus = [
    { btn: $("session-btn"),  menu: $("session-menu") },
    { btn: $("view-btn"),     menu: $("view-menu") },
    { btn: $("settings-btn"), menu: $("settings-menu") },
  ].filter((m) => m.btn && m.menu);
  for (const m of menus) {
    m.btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const open = m.menu.hidden;
      menus.forEach((o) => { o.menu.hidden = true; });
      m.menu.hidden = !open;
    });
  }
  document.addEventListener("click", (e) => {
    menus.forEach((m) => {
      if (!m.menu.hidden && !m.menu.contains(e.target) && e.target !== m.btn) m.menu.hidden = true;
    });
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") menus.forEach((m) => { m.menu.hidden = true; });
  });
  // Multiplayer init: if URL hash names a live session, join it (Blue default for joiners);
  // otherwise stay on white-cell load screen. Pop-out windows carry ?layout=… and ?cell=… and
  // are culled to the requested panels before any rendering.
  applyLayoutCull();
  (async () => {
    const joined = await joinSessionFromHash();
    if (joined) {
      const cellQ = new URLSearchParams(location.search).get("cell");
      setCell(cellQ === "white" || cellQ === "blue" || cellQ === "red" ? cellQ : "blue");
      await refresh();
      startRealtimeClock();
    } else {
      setCell("white");
      await loadVignettes();
    }
  })();
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
        // Prefer the dropdown if the saved target is still a known option; otherwise it's an
        // id the operator typed manually at save time (or has since lost custody on) — put it
        // back in the manual field rather than silently dropping it.
        const sel = $("o-target");
        if (sel && [...sel.options].some((o) => o.value === p.target)) {
          sel.value = p.target || "";
          if ($("o-target-manual")) $("o-target-manual").value = "";
        } else {
          if (sel) sel.value = "";
          if ($("o-target-manual")) $("o-target-manual").value = p.target || "";
        }
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
  const pts = [];
  for (let lon = -180; lon <= 180; lon += 2) {
    const arg = (lon - sunLon) * Math.PI / 180;
    const latT = Math.atan(-Math.cos(arg) / tlat) * 180 / Math.PI;
    pts.push([PX(lon), PY(latT)]);
  }
  const firstX = pts[0][0], lastX = pts[pts.length - 1][0];
  const nightTop = sunLat < 0;   // if sun is south, the north pole is in night
  const polY = nightTop ? 0 : c.height;
  ctx.save();
  // Filled night side — darker so it reads as a distinct hemisphere on dim monitors.
  ctx.fillStyle = "rgba(0,0,12,0.55)";
  ctx.beginPath();
  pts.forEach(([px, py], i) => i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py));
  ctx.lineTo(lastX, polY); ctx.lineTo(firstX, polY); ctx.closePath();
  ctx.fill();
  // Bright terminator curve itself — high-contrast delimiter the eye can lock on.
  ctx.strokeStyle = "rgba(255,220,140,0.85)"; ctx.lineWidth = 1.5;
  ctx.beginPath();
  pts.forEach(([px, py], i) => i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py));
  ctx.stroke();
  ctx.restore();
};

// Persisted toggles + initial render of playbooks/bookmarks.
addEventListener("DOMContentLoaded", () => {
  applyToggle("projector", "projector");
  applyToggle("cb", "cb");
  applyToggle("hc", "hi-contrast");
  applyToggle("bigtext", "large-text");
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
// Re-render playbooks/bookmarks/branches whenever the vignette selection changes.
addEventListener("DOMContentLoaded", () => {
  const v = $("vignette"); if (v) v.addEventListener("change", () => { renderPlaybooks(); renderBookmarks(); renderBranches(); });
  renderBranches();
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
    items.push({ label: "toggle high-contrast mode", tag: "view", run: () => { const hc = $("hc"); hc.checked = !hc.checked; hc.dispatchEvent(new Event("change")); }});
    items.push({ label: "toggle large-text mode", tag: "view", run: () => { const bt = $("bigtext"); bt.checked = !bt.checked; bt.dispatchEvent(new Event("change")); }});
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
    // FW §11.D.19 — library entries surface as palette commands too.
    INJECT_LIBRARY.forEach((lib, idx) => {
      items.push({
        label: `inject lib: ${lib.label || lib.id}`,
        tag: "inject",
        run: () => {
          const det = $("inject-builder"); if (det) det.open = true;
          $("inject-lib").value = String(idx);
          loadInjectTemplate();
        },
      });
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

  // FW §11.C.13 — fleet-subset batch helpers.  Each populates BATCH with assets
  // matching a predicate, then renders so the user can confirm and Issue-to-all.
  const own = () => Object.entries(ASSETS).filter(([id, a]) =>
    a.owner === (CELL === "white" ? "blue" : CELL));
  function selectSubset(pred) {
    BATCH.clear();
    own().forEach(([id, a]) => { if (pred(id, a)) BATCH.add(id); });
    batchRender();
  }
  const fa = $("fleet-apply-all");
  if (fa) fa.onclick = () => selectSubset(() => true);
  const fi = $("fleet-apply-isr");
  if (fi) fi.onclick = () => selectSubset((id, a) => (a.payload || "").startsWith("isr"));
  const fc = $("fleet-apply-comsat");
  if (fc) fc.onclick = () => selectSubset((id, a) => a.payload === "satcom");
  const fg = $("fleet-apply-group");
  if (fg) fg.onclick = () => {
    const actor = $("o-actor").value;
    const grp = actor && ASSETS[actor] && ASSETS[actor].group;
    if (!grp) { $("order-result").textContent = "Select an asset with a group first."; return; }
    selectSubset((id, a) => a.group === grp);
  };
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
  // Scroll target into view first so getBoundingClientRect returns on-screen coords.
  el.scrollIntoView({ behavior: "instant", block: "nearest", inline: "nearest" });
  const r = el.getBoundingClientRect();
  const hole = $("coachmark-hole");
  hole.style.left = (r.left - 4) + "px"; hole.style.top = (r.top - 4) + "px";
  hole.style.width = (r.width + 8) + "px"; hole.style.height = (r.height + 8) + "px";
  const tip = $("coachmark-tip");
  // Place tip below target when room allows, above otherwise.
  const spaceBelow = window.innerHeight - r.bottom;
  const tipTop = spaceBelow >= 180 ? r.bottom + 12 : Math.max(8, r.top - 180);
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
  // Click on backdrop (outside the tip box) closes the tour.
  $("coachmark-wrap").addEventListener("click", (e) => { if (!$("coachmark-tip").contains(e.target)) coachClose(); });
  // Escape closes the tour.
  document.addEventListener("keydown", (e) => { if (e.key === "Escape" && $("coachmark-wrap").classList.contains("on")) { e.stopPropagation(); coachClose(); } });
});

// FUTURE-WORK §9 — Replay branches. Save the current AAR report as a named branch (localStorage,
// scoped by vignette), then compare two branches client-side using the same diff shape that
// session/aar.py compare_branches() returns (events_a/b + objective flips).
function brKey() { const v = $("vignette")?.value; return "branches:" + (v || "default"); }
function brList() { try { return JSON.parse(localStorage.getItem(brKey()) || "[]"); } catch { return []; } }
function brSave(items) { localStorage.setItem(brKey(), JSON.stringify(items)); renderBranches(); }
function renderBranches() {
  const div = $("branch-list"); if (!div) return;
  const items = brList();
  if (!items.length) { div.className = "bookmark-list muted"; div.textContent = "(no branches)"; return; }
  div.className = "bookmark-list";
  div.innerHTML = items.map((b, i) =>
    `<span class="bookmark-chip" data-i="${i}"><input type="checkbox" data-i="${i}" />${b.name} <span class="muted">${b.report.n_events} events</span><span class="x" data-del="${i}">✕</span></span>`).join("");
  div.querySelectorAll(".x").forEach((x) => x.addEventListener("click", (e) => {
    e.stopPropagation();
    const items = brList(); items.splice(+e.target.dataset.del, 1); brSave(items);
  }));
}
function compareBranches() {
  const checked = [...document.querySelectorAll("#branch-list input[type=checkbox]:checked")].map((c) => +c.dataset.i);
  const items = brList();
  if (checked.length !== 2) { $("branch-diff").textContent = "(select exactly 2 branches)"; return; }
  const a = items[checked[0]].report, b = items[checked[1]].report;
  const flips = {};
  for (const side of ["blue", "red"]) {
    const ao = (a.final_objectives || {})[side] || {}, bo = (b.final_objectives || {})[side] || {};
    for (const oid of new Set([...Object.keys(ao), ...Object.keys(bo)])) {
      if (ao[oid] !== bo[oid]) flips[`${side}.${oid}`] = { a: ao[oid], b: bo[oid] };
    }
  }
  $("branch-diff").textContent = JSON.stringify({
    events_a: a.n_events, events_b: b.n_events, objective_flips: flips
  }, null, 2);
}
addEventListener("DOMContentLoaded", () => {
  const bs = $("branch-save"); if (bs) bs.addEventListener("click", async () => {
    if (!SID) return;
    const report = await api.get(`/api/sessions/${SID}/aar`).catch(() => null);
    if (!report) return;
    const name = prompt("Branch name:", `branch-${brList().length + 1}`); if (!name) return;
    const items = brList(); items.push({ name, report }); brSave(items);
  });
  const bc = $("branch-compare"); if (bc) bc.addEventListener("click", compareBranches);
});

// §10.E.18 — Per-vignette tutorial panel. Reads the vignette's per-cell `tutorial` script and
// renders it as an ordered list scoped to the active cell (the script lives in the YAML).
async function tutorialOpen() {
  const panel = $("tutorial-panel"); if (!panel) return;
  if (!SID) { panel.classList.add("open"); $("tutorial-steps").innerHTML = "<li>(load a vignette first)</li>"; return; }
  // Structured per-cell tutorial from the API (parsed server-side by pydantic — no fragile
  // YAML scraping, so blue/red steps stay separate). White sees Blue's script.
  const vid = $("vignette") ? $("vignette").value : "";
  const cellKey = CELL === "white" ? "blue" : CELL;
  $("tutorial-title").textContent = `Tutorial — ${cellKey} cell`;
  try {
    const tut = await api.get(`/api/vignettes/${vid}/tutorial`);
    const steps = (tut[cellKey] || []).map((s) => {
      const cmd = s.actor
        ? `${s.action} · ${s.actor}${s.target ? " → " + s.target : ""}` +
          (s.params ? " " + JSON.stringify(s.params) : "")
        : s.action;
      const when = s.when ? `<span class="muted"> — ${esc(s.when)}</span>` : "";
      const expect = s.expect ? `<br><span class="muted">↳ ${esc(s.expect)}</span>` : "";
      return `<li><b>${esc(s.title || "(untitled)")}</b>${when}<br><code>${esc(cmd)}</code>${expect}</li>`;
    });
    $("tutorial-steps").innerHTML = steps.length ? steps.join("") : "<li>(no tutorial defined for this cell)</li>";
  } catch { $("tutorial-steps").innerHTML = "<li>(no tutorial available for this vignette)</li>"; }
  panel.classList.add("open");
}
function tutorialClose() { const p = $("tutorial-panel"); if (p) p.classList.remove("open"); }
addEventListener("DOMContentLoaded", () => {
  const tb = $("tutorial"); if (tb) tb.addEventListener("click", () => {
    const p = $("tutorial-panel"); if (!p) return;
    p.classList.contains("open") ? tutorialClose() : tutorialOpen();
  });
  const tc = $("tutorial-close"); if (tc) tc.addEventListener("click", tutorialClose);
});

// ---------------------------------------------------------------------------
// Mission brief panel — first thing a new operator should read.  Pulls the
// per-cell brief from /api/sessions/{sid}/brief/{cell} which combines static
// vignette intro_brief.{cell} text with live ROE + objective deadlines.
// Auto-opens on first session load (localStorage flag); collapsible thereafter.
// ---------------------------------------------------------------------------
let LAST_BRIEF_SID = null;       // suppress re-fetching every poll
async function renderBrief() {
  const body = $("brief-body");
  const titleEl = $("brief-vignette-title");
  if (!body) return;
  if (!SID) {
    body.innerHTML = "<div class='muted'>(load a vignette to see the mission brief)</div>";
    if (titleEl) titleEl.textContent = "";
    return;
  }
  // Re-fetch on every refresh so deadline countdowns + ROE stay live.
  let brief;
  try { brief = await api.get(`/api/sessions/${SID}/brief/${CELL}`); }
  catch { body.innerHTML = "<div class='muted'>(brief unavailable)</div>"; return; }

  const fmtRemaining = (s) => {
    if (s == null || s < 0) return "expired";
    const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), ss = s % 60;
    return h > 0 ? `${h}h ${String(m).padStart(2, "0")}m` : `${m}m ${String(ss).padStart(2, "0")}s`;
  };

  // White sees both cells; Blue/Red see their own.
  const renderCell = (b) => {
    const t = b.text || {};
    const block = (label, text) => text ? `<dt>${label}</dt><dd>${esc(text)}</dd>` : "";
    const lo = (b.learning_objectives || []).map((x) => `<li>${esc(x)}</li>`).join("");
    const objs = (b.objectives || []).map((o) => {
      const stale = o.remaining_s <= 0;
      const cls = stale ? "obj-expired" : "obj-live";
      return `<li class="${cls}"><b>${esc(o.id)}</b> — ${esc(o.desc || "(no description)")}` +
             ` <span class="muted">T-${fmtRemaining(o.remaining_s)}</span></li>`;
    }).join("");
    const roe = b.roe || {};
    const roeChips = [
      `<span class="roe-chip ${roe.kinetic_authorized ? "on" : "off"}">kinetic ${roe.kinetic_authorized ? "ON" : "OFF"}</span>`,
      `<span class="roe-chip ${roe.cyber_authorized ? "on" : "off"}">cyber ${roe.cyber_authorized ? "ON" : "OFF"}</span>`,
    ].join(" ");
    const doctrine = b.red_doctrine_profile && b.cell === "red"
      ? `<div class="brief-doctrine"><b>Red doctrine:</b> ${esc(b.red_doctrine_profile)}</div>`
      : "";
    return `
      <div class="brief-cell brief-cell-${b.cell}">
        <div class="brief-meta">
          <span><b>Theater:</b> ${esc(b.theater || "—")}</span>
          <span><b>Start:</b> ${esc((b.start_epoch_utc || "").replace("T", " ").replace("Z", " UTC"))}</span>
          <span><b>Duration:</b> ~${b.estimated_duration_min || "?"} min</span>
          <span><b>ROE:</b> ${roeChips}</span>
        </div>
        ${doctrine}
        <dl class="brief-text">
          ${block("Situation", t.situation)}
          ${block("Mission", t.mission)}
          ${block("Friendly forces", t.friendly_forces)}
          ${block("Threat picture", t.threat_picture)}
          ${block("Deadline", t.deadline_note)}
          ${block("Rules of engagement", t.roe_note)}
          ${block("Success criteria", t.success_criteria)}
          ${block("Tool tips", t.tool_tips)}
        </dl>
        <div class="brief-objectives"><b>Objectives</b><ul>${objs || "<li class='muted'>(none)</li>"}</ul></div>
        ${lo ? `<div class="brief-learn"><b>Learning objectives</b><ul>${lo}</ul></div>` : ""}
      </div>`;
  };

  if (CELL === "white" && brief.blue && brief.red) {
    body.innerHTML = `<div class="brief-grid">${renderCell(brief.blue)}${renderCell(brief.red)}</div>`;
    if (titleEl) titleEl.textContent = "(white sees both cells)";
  } else {
    body.innerHTML = renderCell(brief);
    if (titleEl) titleEl.textContent = brief.title ? `— ${brief.title}` : "";
  }

  // Auto-open the brief on the first encounter of this session, then remember the user's choice.
  if (SID !== LAST_BRIEF_SID) {
    LAST_BRIEF_SID = SID;
    const dismissedKey = `brief-dismissed-${SID}`;
    if (!localStorage.getItem(dismissedKey)) {
      $("brief-panel").classList.remove("collapsed");
      $("brief-toggle").textContent = "▾";
    }
  }
}
function toggleBrief() {
  const panel = $("brief-panel");
  if (!panel) return;
  const collapsed = panel.classList.toggle("collapsed");
  $("brief-toggle").textContent = collapsed ? "▸" : "▾";
  if (SID) localStorage.setItem(`brief-dismissed-${SID}`, collapsed ? "1" : "");
}
addEventListener("DOMContentLoaded", () => {
  const bt = $("brief-toggle"); if (bt) bt.addEventListener("click", toggleBrief);
  const bo = $("brief-open"); if (bo) bo.addEventListener("click", () => {
    const p = $("brief-panel"); if (!p) return;
    p.classList.remove("collapsed");
    $("brief-toggle").textContent = "▾";
    p.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

// §10.D.17 — Vignette inspector. Pulls the raw YAML and shows it in a modal; "Download YAML"
// streams it as a file so trainers can fork a scenario by hand.
async function inspectorOpen() {
  const wrap = $("inspector-wrap"); if (!wrap) return;
  const vid = $("vignette") ? $("vignette").value : "";
  $("inspector-id").textContent = vid || "(no vignette selected)";
  try {
    const yaml = await fetch(`/api/vignettes/${vid}/source`).then((r) => r.text());
    $("inspector-yaml").textContent = yaml;
    $("inspector-download").onclick = () => {
      const blob = new Blob([yaml], { type: "text/yaml" });
      const a = document.createElement("a"); a.href = URL.createObjectURL(blob);
      a.download = `${vid}.yaml`; a.click(); URL.revokeObjectURL(a.href);
    };
  } catch { $("inspector-yaml").textContent = "(failed to load vignette source)"; }
  wrap.classList.add("open");
}
addEventListener("DOMContentLoaded", () => {
  const ib = $("inspect-vignette"); if (ib) ib.addEventListener("click", inspectorOpen);
  const ic = $("inspector-close"); if (ic) ic.addEventListener("click", () => $("inspector-wrap").classList.remove("open"));
  const iw = $("inspector-wrap"); if (iw) iw.addEventListener("click", (e) => { if (e.target === iw) iw.classList.remove("open"); });
});

// ===================================================================
// User-added future work (FUTURE-WORK.md §"User added Future work")
// ===================================================================

// #6 — Hand-off screen blank between operators. Click ⏸ Handover, the screen blurs and a big
// headline appears until the next operator clicks Resume.
addEventListener("DOMContentLoaded", () => {
  const btn = $("handover-btn"), wrap = $("handover"), resume = $("handover-resume");
  if (!btn || !wrap) return;
  let pendingCell = null;
  btn.addEventListener("click", () => {
    pendingCell = CELL === "blue" ? "red" : CELL === "red" ? "blue" : "white";
    $("handover-title").textContent = `HANDING OFF → ${pendingCell.toUpperCase()}`;
    $("handover-who").textContent = `Pass the keyboard to the ${pendingCell.toUpperCase()} operator and click Resume.`;
    wrap.classList.add("open");
  });
  if (resume) resume.addEventListener("click", () => {
    wrap.classList.remove("open");
    if (pendingCell) { setCell(pendingCell); pendingCell = null; }
  });
});

// #9 — Tooltips for ALL buttons that don't already have a title=. Reads the button's text and
// derives a 1-line description from the existing ACRONYMS dict or a short fallback.
const BUTTON_HINTS = {
  "Load": "Load the selected vignette as a new session",
  "Start": "Start the loaded session (sim clock begins ticking)",
  "+1m": "Advance simulation time by 1 minute",
  "+10m": "Advance simulation time by 10 minutes",
  "+1h": "Advance simulation time by 1 hour",
  "⟲ Rewind": "Rewind to t=0 and replay the eventlog",
  "Save": "Download the current session state as JSON",
  "Issue order": "Submit the composed order (validates first — see preview)",
  "★ Save preset": "Save the current compose form as a named playbook (FW §10.B.7)",
  "Plan collection": "Submit a sensor-tasking (or SSN) request for the selected target",
  "Fire": "Fire the selected inject (White-Cell only)",
  "Compare selected": "Diff two saved AAR branches (FW §9 replay branching)",
  "＋ Save current branch": "Snapshot the live AAR as a named branch in localStorage",
  "📌 Bookmark": "Pin the current sim time as a bookmark (jump back later)",
  "⏸ Handover": "Blank/blur the screen for hot-seat handoff",
  "? Help": "Open the help panel",
};
addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("button").forEach((b) => {
    if (b.title) return;
    const label = (b.textContent || "").trim();
    if (BUTTON_HINTS[label]) b.title = BUTTON_HINTS[label];
  });
});

// #10 — Help panel toggle.
addEventListener("DOMContentLoaded", () => {
  const open = $("help-btn"), wrap = $("help-wrap"), close = $("help-close");
  if (open) open.addEventListener("click", () => wrap.classList.add("open"));
  if (close) close.addEventListener("click", () => wrap.classList.remove("open"));
  if (wrap) wrap.addEventListener("click", (e) => { if (e.target === wrap) wrap.classList.remove("open"); });
});

// Maneuver mode assistant listeners.
addEventListener("DOMContentLoaded", () => {
  const modeSelect = $("mnvr-mode");
  if (modeSelect) modeSelect.addEventListener("change", mnvrModeChange);
  const computeBtn = $("mnvr-compute");
  if (computeBtn) computeBtn.addEventListener("click", computeManeuver);
  // Re-compute on field change so the preview stays live.
  ["mnvr-eci-x","mnvr-eci-y","mnvr-eci-z",
   "mnvr-lvlh-r","mnvr-lvlh-t","mnvr-lvlh-n",
   "mnvr-fb-r","mnvr-fb-t","mnvr-fb-n","mnvr-fb-mag","mnvr-fb-dur",
   "mnvr-coe-a","mnvr-coe-e","mnvr-coe-i","mnvr-coe-raan","mnvr-coe-argp",
   "mnvr-hoh-alt","mnvr-pc-di",
  ].forEach((id) => {
    const el = $(id);
    if (el) el.addEventListener("change", computeManeuver);
  });
});

// Jam / engage / cyber parameter assistant listeners (Audit 2026-06 Commands §M4).
addEventListener("DOMContentLoaded", () => {
  const jamBtn = $("jam-compute");
  if (jamBtn) jamBtn.addEventListener("click", computeJam);
  ["jam-mod", "jam-power", "jam-bw", "jam-vbw"].forEach((id) => {
    const el = $(id);
    if (el) el.addEventListener("change", jamSummaryUpdate);
  });
  const engBtn = $("engage-compute");
  if (engBtn) engBtn.addEventListener("click", computeEngage);
  ["engage-class", "engage-salvo"].forEach((id) => {
    const el = $(id);
    if (el) el.addEventListener("change", engageSummaryUpdate);
  });
  ["cyber-vector", "cyber-payload", "cyber-dwell"].forEach((id) => {
    const el = $(id);
    if (el) el.addEventListener("change", cyberSummaryUpdate);
  });
});
