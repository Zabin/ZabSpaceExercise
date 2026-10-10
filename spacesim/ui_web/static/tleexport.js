"use strict";
// IP-1211 (FR-7440) — quick TLE export: a copyable current-epoch two-line element set for one
// satellite. A pure consumer of GET /api/sessions/{sid}/tle/{cell}?object_id=: fog-of-war is
// applied server-side (a cell exports only from its own Track; White reads ground truth via the
// god-view path). Candidates for a cell are its tracked objects only (Design Decision 5 — own-asset
// export is not yet in scope); White sees every on-orbit asset. Fetched on open / selection change
// only (a TLE is a snapshot to copy, not a live view); selection is not persisted.
(function () {
  const el = (id) => document.getElementById(id);
  const escH = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  function candidates() {
    const ids = new Set();
    if (CELL === "white") {
      const assets = (typeof ASSETS !== "undefined") ? ASSETS : {};
      for (const [id, a] of Object.entries(assets)) {
        const k = a.kind || "";
        if (!k.startsWith("ground") && k !== "space_based" && !a.network) ids.add(id);
      }
    } else if (typeof SCENE !== "undefined" && SCENE) {
      (SCENE.tracks || []).forEach((t) => ids.add(t.object));
    }
    return [...ids].sort();
  }

  function fillPicker() {
    const sel = el("tle-object");
    const cur = sel.value;
    const ids = candidates();
    sel.innerHTML = ids.map((i) => `<option value="${escH(i)}">${escH(i)}</option>`).join("");
    if (cur && ids.includes(cur)) sel.value = cur;
    return ids.length;
  }

  function show(text, meta) {
    el("tle-text").value = text;
    el("tle-meta").innerHTML = meta;
    el("tle-copied").textContent = "";
  }

  async function load() {
    if (typeof SID === "undefined" || !SID) { show("", "(load a vignette first)"); return; }
    if (CELL === "observer") { show("", "(TLE export is not available to the Observer seat)"); return; }
    if (!fillPicker()) {
      show("", CELL === "white" ? "(no on-orbit satellite in this session)"
                                : "(your cell holds no track to export — task a sensor first)");
      return;
    }
    const q = new URLSearchParams({ object_id: el("tle-object").value });
    try {
      const r = await fetch(`/api/sessions/${SID}/tle/${CELL}?${q}`);
      const d = await r.json().catch(() => ({}));
      if (!r.ok) { show("", `<span class='red'>${escH(d.detail || r.statusText)}</span>`); return; }
      show(`${d.line1}\n${d.line2}`,
        `${escH(d.object_id)} · epoch ${escH(d.epoch_iso)} · from ${d.source === "truth" ? "ground truth" : "your track (belief)"}` +
        ` · fit residual ${Number(d.fit_error_m).toFixed(1)} m<br>${escH(d.note)}`);
    } catch (e) { show("", `<span class='red'>${escH(e.message)}</span>`); }
  }

  async function copy() {
    const ta = el("tle-text");
    if (!ta.value) return;
    let ok = false;
    try {
      if (navigator.clipboard && window.isSecureContext) { await navigator.clipboard.writeText(ta.value); ok = true; }
    } catch (e) { ok = false; }
    if (!ok) {  // plain-HTTP LAN fallback: select the text and use the legacy copy command
      ta.focus(); ta.select();
      try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    }
    el("tle-copied").textContent = ok ? "copied" : "select the text and press Ctrl/⌘+C";
  }

  function open() { const p = el("tle-panel"); if (!p) return; p.classList.add("open"); load(); }
  function close() { const p = el("tle-panel"); if (p) p.classList.remove("open"); }

  addEventListener("DOMContentLoaded", () => {
    const b = el("tle-open");
    if (b) b.addEventListener("click", () => (el("tle-panel").classList.contains("open") ? close() : open()));
    const c = el("tle-close"); if (c) c.addEventListener("click", close);
    const s = el("tle-object"); if (s) s.addEventListener("change", load);
    const k = el("tle-copy"); if (k) k.addEventListener("click", copy);
  });
})();
