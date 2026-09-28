"use strict";
// IP-1174 (FS-117 §FR-5120-FR-5160) — the Vignette Creator's White-Cell-facing UI surfaces: a
// synchronized JSON view, a ground-truth 2D/3D preview (reusing app.js's/globe.js's existing
// rendering code), TLE/lat-long asset entry with a curated-site picker, an asset menu
// (edit/reassign/delete), and a seat-count-declaration + seat/role-assignment matrix. A dedicated
// module, following the existing globe.js/graph.js pattern of separate front-end files alongside
// app.js, since app.js already handles a live exercise session — this module is a thin client
// over its own *draft* session (created via POST /api/sessions/draft, IP-1173) and never touches
// the live SID/CELL globals app.js owns.

window.Creator = (function () {
  const $ = (id) => document.getElementById(id);
  let sid = null;   // this Creator panel's own draft session id — independent of app.js's SID

  function ensureDraft() {
    return sid !== null;
  }

  async function newDraft() {
    const title = $("creator-title").value.trim() || "Untitled Draft";
    const r = await api.post("/api/sessions/draft", { title });
    sid = r.session;
    $("creator-save-result").textContent = `draft ${sid} created`;
    await refreshAssetList();
    await refreshSeatMatrix();
  }

  async function saveVignette() {
    if (!ensureDraft()) { $("creator-save-result").textContent = "create a draft first"; return; }
    const vid = $("creator-save-id").value.trim();
    if (!vid) { $("creator-save-result").textContent = "vignette id required"; return; }
    try {
      const r = await api.post(`/api/sessions/${sid}/save_vignette`, {
        vignette_id: vid, title: $("creator-title").value.trim() || vid,
      });
      $("creator-save-result").textContent = `saved: ${r.path}`;
    } catch (e) {
      $("creator-save-result").textContent = `error: ${e.message}`;
    }
  }

  // -- FR-5140: TLE-paste and lat/long asset entry -----------------------------------------------

  async function addTle() {
    if (!ensureDraft()) return;
    await api.post(`/api/sessions/${sid}/force/tle`, {
      id: $("creator-tle-id").value.trim(),
      line1: $("creator-tle-l1").value.trim(),
      line2: $("creator-tle-l2").value.trim(),
      owner: $("creator-tle-owner").value,
      kind: $("creator-tle-kind").value.trim() || "satellite",
    });
    await refreshAssetList();
  }

  async function loadGroundSites() {
    const sites = await api.get("/api/ground_sites");
    const sel = $("creator-gnd-site");
    sel.innerHTML = `<option value="">(free entry)</option>` +
      sites.map((s) => `<option value="${s.code}" data-lat="${s.lat_deg}" data-lon="${s.lon_deg}">${s.code} — ${s.site}</option>`).join("");
    sel.onchange = () => {
      const opt = sel.selectedOptions[0];
      if (opt && opt.dataset.lat) { $("creator-gnd-lat").value = opt.dataset.lat; $("creator-gnd-lon").value = opt.dataset.lon; }
    };
  }

  async function addGroundAsset() {
    if (!ensureDraft()) return;
    await api.post(`/api/sessions/${sid}/force/ground`, {
      id: $("creator-gnd-id").value.trim(),
      lat_deg: parseFloat($("creator-gnd-lat").value),
      lon_deg: parseFloat($("creator-gnd-lon").value),
      owner: $("creator-gnd-owner").value,
      kind: $("creator-gnd-kind").value.trim() || "ground_station",
    });
    await refreshAssetList();
  }

  // -- FR-5150: asset menu (edit, reassign, delete) -----------------------------------------------

  async function refreshAssetList() {
    if (!ensureDraft()) return;
    const state = await api.get(`/api/sessions/${sid}/creator/state`);
    const el = $("creator-asset-list");
    if (!state.assets.length) { el.textContent = "(no assets yet)"; return; }
    el.innerHTML = state.assets.map((a) => `
      <div class="menu-item-row" data-asset="${a.id}" style="border-bottom:1px solid var(--border,#333);padding:2px 0">
        <b>${a.id}</b> (${a.kind})
        <select class="c-owner" style="width:5em">
          ${["blue", "red", "neutral"].map((o) => `<option value="${o}" ${o === a.owner ? "selected" : ""}>${o}</option>`).join("")}
        </select>
        <button class="c-reassign">Set cell</button>
        <button class="c-delete">✕ Delete</button>
      </div>`).join("");
    el.querySelectorAll("[data-asset]").forEach((row) => {
      const id = row.dataset.asset;
      row.querySelector(".c-reassign").onclick = async () => {
        await api.patch(`/api/sessions/${sid}/creator/asset/${id}`, { patch: { owner: row.querySelector(".c-owner").value } });
        await refreshAssetList();
      };
      row.querySelector(".c-delete").onclick = async () => {
        await api.del(`/api/sessions/${sid}/creator/asset/${id}`);
        await refreshAssetList();
      };
    });
  }

  // -- FR-5120: synchronized JSON view ------------------------------------------------------------

  async function jsonLoad() {
    if (!ensureDraft()) return;
    const state = await api.get(`/api/sessions/${sid}/creator/state`);
    $("creator-json").value = JSON.stringify(state, null, 2);
    $("creator-json-result").textContent = "loaded";
  }

  async function jsonSave() {
    if (!ensureDraft()) return;
    try {
      const parsed = JSON.parse($("creator-json").value);
      const r = await api.put(`/api/sessions/${sid}/creator/state`, { assets: parsed.assets || [] });
      $("creator-json-result").textContent = r.ok ? "saved" : `rejected: ${r.reason}`;
      await refreshAssetList();
    } catch (e) {
      $("creator-json-result").textContent = `invalid JSON: ${e.message}`;
    }
  }

  // -- FR-5160: seat-count declaration + seat/role-assignment matrix -------------------------------

  async function declareSeats() {
    if (!ensureDraft()) return;
    const cell = $("creator-seat-cell").value;
    const count = parseInt($("creator-seat-count").value, 10) || 1;
    await api.post(`/api/sessions/${sid}/creator/seats`, { cell, count });
    await refreshSeatMatrix();
  }

  async function refreshSeatMatrix() {
    if (!ensureDraft()) return;
    const [seats, state] = await Promise.all([
      api.get(`/api/sessions/${sid}/creator/seats`),
      api.get(`/api/sessions/${sid}/creator/state`),
    ]);
    const allSeats = Object.values(seats).flat();
    const el = $("creator-matrix");
    if (!allSeats.length || !state.assets.length) { el.textContent = "(declare seats and add assets first)"; return; }
    el.innerHTML = `<table style="font-size:11px"><thead><tr><th>Seat</th><th>Asset</th><th>Role</th><th></th></tr></thead><tbody>` +
      allSeats.map((seat) => {
        const cell = seat.split("-")[0];
        return `<tr data-seat="${seat}" data-cell="${cell}">
          <td>${seat}</td>
          <td><select class="m-asset">${state.assets.map((a) => `<option value="${a.id}">${a.id}</option>`).join("")}</select></td>
          <td><select class="m-role"><option value="both">both</option><option value="bus">bus</option><option value="payload">payload</option></select></td>
          <td><button class="m-assign">Assign</button></td>
        </tr>`;
      }).join("") + `</tbody></table>`;
    el.querySelectorAll("tr[data-seat]").forEach((row) => {
      row.querySelector(".m-assign").onclick = async () => {
        // BL-0123 remediation: `RoleAssignmentRequest.cell` is the *caller's* own seat (must be
        // "white") — `role_assignments` itself carries no per-cell partitioning at all, so this
        // must never be `row.dataset.cell` (the assigned seat's own cell prefix, e.g. "blue"),
        // which would make assigning a non-White seat's role fail the White-Cell-only check.
        // The Vignette Creator is a White-Cell-only tool (see module banner above), so the caller
        // is always White here.
        await api.post(`/api/sessions/${sid}/roles/assign`, {
          cell: "white", seat: row.dataset.seat,
          asset_or_constellation: row.querySelector(".m-asset").value,
          role: row.querySelector(".m-role").value,
        });
      };
    });
  }

  // -- FR-5130: ground-truth 2D/3D preview (reuses the existing map/globe renderers) ---------------

  async function refreshPreview() {
    if (!ensureDraft()) return;
    const scene = await api.get(`/api/sessions/${sid}/creator/scene`);
    window.SCENE = scene;       // same global the live session's poll loop sets — same consumers
    if (typeof drawMap === "function") drawMap();
    window.Globe && Globe.render(scene);
  }

  function init() {
    if (!$("creator-btn")) return;   // menu absent (e.g. a pop-out layout) — nothing to wire
    $("creator-new").onclick = newDraft;
    $("creator-save").onclick = saveVignette;
    $("creator-tle-add").onclick = addTle;
    $("creator-gnd-add").onclick = addGroundAsset;
    $("creator-refresh").onclick = refreshAssetList;
    $("creator-json-load").onclick = jsonLoad;
    $("creator-json-save").onclick = jsonSave;
    $("creator-seat-declare").onclick = declareSeats;
    $("creator-preview").onclick = refreshPreview;
    loadGroundSites();
  }

  return { init };
})();
