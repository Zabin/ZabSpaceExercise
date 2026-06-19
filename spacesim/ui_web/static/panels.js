"use strict";
// Panel manager — each info panel is movable (drag its header), scalable (resize handle when
// floating), closeable (✕ in the header), and openable (View ▾ → Panels). Layout persists in
// localStorage so a console arrangement survives reloads. Panels are docked in the normal grid
// flow by default; dragging one floats it out of flow (position: fixed) so the rest reflow —
// which is how an operator stops the Mission brief (or any panel) from shoving everything else
// around when it opens.
(function () {
  const LS_KEY = "panel-layout-v1";

  // Registry of manageable panels. `handle` overrides the default drag-handle (the panel's <h2>).
  const PANELS = [
    { id: "brief-panel",     label: "Mission brief" },
    { id: "cell-time-panel", label: "Cell & Time" },
    { id: "fleet-panel",     label: "Fleet SOH rollup" },
    { id: "tasking-panel",   label: "Tasking (sensor)" },
    { id: "order-panel",     label: "Satellite command" },
    { id: "globe-panel",     label: "3D globe", handle: ".viewer-head" },
    { id: "map-panel",       label: "2D belief map", handle: ".viewer-head" },
    { id: "activity-panel",  label: "Activity timeline" },
    { id: "aar-panel",       label: "After-action review" },
    { id: "drill-panel",     label: "Subsystem drill-down" },
  ];

  let state = loadState();
  function loadState() { try { return JSON.parse(localStorage.getItem(LS_KEY)) || {}; } catch { return {}; } }
  function saveState() { try { localStorage.setItem(LS_KEY, JSON.stringify(state)); } catch { /* quota */ } }
  function st(id) { return (state[id] = state[id] || { hidden: false, float: null }); }

  const def = (id) => PANELS.find((p) => p.id === id);

  // Apply a panel's persisted state (visibility + float geometry) to the DOM.
  function apply(id) {
    const el = document.getElementById(id);
    if (!el) return;
    const s = st(id);
    el.hidden = !!s.hidden;
    const fl = s.float;
    if (fl) {
      el.classList.add("panel-floating");
      el.style.position = "fixed";
      el.style.left = fl.left + "px";
      el.style.top = fl.top + "px";
      el.style.width = fl.width + "px";
      if (fl.height) el.style.height = fl.height + "px";
      el.style.zIndex = "60";
      el.style.margin = "0";
    } else {
      el.classList.remove("panel-floating");
      ["position", "left", "top", "width", "height", "zIndex", "margin"].forEach((k) => (el.style[k] = ""));
    }
  }

  function headerOf(el, d) {
    return (d.handle ? el.querySelector(d.handle) : el.querySelector(":scope > h2")) || el.querySelector("h2");
  }

  // Inject the grip + dock + close controls into a panel's header.
  function injectControls(el, d) {
    if (el.querySelector(":scope > .panel-tools, .panel-tools")) return;
    const header = headerOf(el, d);
    if (!header) return;
    const tools = document.createElement("span");
    tools.className = "panel-tools";
    tools.innerHTML =
      `<button class="panel-grip" title="Drag to move this panel">⠿</button>` +
      `<button class="panel-dock" title="Re-dock to the default layout">▣</button>` +
      `<button class="panel-close" title="Close this panel (re-open from View ▾ → Panels)">✕</button>`;
    header.appendChild(tools);

    tools.querySelector(".panel-close").addEventListener("click", (e) => {
      e.stopPropagation();
      st(el.id).hidden = true; apply(el.id); saveState(); syncMenu();
    });
    tools.querySelector(".panel-dock").addEventListener("click", (e) => {
      e.stopPropagation();
      st(el.id).float = null; apply(el.id); saveState();
    });
    // Drag: pointerdown on the grip, or anywhere on the header that isn't an interactive control.
    const grip = tools.querySelector(".panel-grip");
    grip.addEventListener("pointerdown", (e) => startDrag(e, el));
    header.addEventListener("pointerdown", (e) => {
      if (e.target.closest("button, input, select, textarea, a, label, .ctrl")) return;
      startDrag(e, el);
    });
    header.classList.add("panel-handle");
  }

  let drag = null;
  function startDrag(e, el) {
    e.preventDefault();
    const r = el.getBoundingClientRect();
    // Float the panel at its current on-screen position so it doesn't jump on grab.
    const s = st(el.id);
    s.float = s.float || { left: r.left, top: r.top, width: r.width, height: 0 };
    s.float.left = r.left; s.float.top = r.top; s.float.width = r.width;
    apply(el.id);
    drag = { el, dx: e.clientX - r.left, dy: e.clientY - r.top };
    window.addEventListener("pointermove", onDrag);
    window.addEventListener("pointerup", endDrag, { once: true });
  }
  function onDrag(e) {
    if (!drag) return;
    const s = st(drag.el.id).float;
    const maxL = window.innerWidth - 80, maxT = window.innerHeight - 40;
    s.left = Math.max(0, Math.min(maxL, e.clientX - drag.dx));
    s.top = Math.max(0, Math.min(maxT, e.clientY - drag.dy));
    drag.el.style.left = s.left + "px";
    drag.el.style.top = s.top + "px";
  }
  function endDrag() {
    window.removeEventListener("pointermove", onDrag);
    if (drag) { saveState(); drag = null; }
  }

  // Capture user resizes of floating panels (the native CSS resize handle) into persisted state.
  function watchResize(el) {
    if (!window.ResizeObserver) return;
    const ro = new ResizeObserver(() => {
      const s = st(el.id);
      if (!s.float || !el.classList.contains("panel-floating")) return;
      s.float.width = Math.round(el.getBoundingClientRect().width);
      s.float.height = Math.round(el.getBoundingClientRect().height);
      clearTimeout(el._panelSaveT);
      el._panelSaveT = setTimeout(saveState, 250);
    });
    ro.observe(el);
  }

  // Build the View ▾ → Panels section: a show/hide checkbox per panel + Reset layout.
  function buildMenu() {
    const menu = document.getElementById("view-menu");
    if (!menu || menu.querySelector("#panels-section")) return;
    const sec = document.createElement("div");
    sec.className = "menu-section";
    sec.id = "panels-section";
    sec.innerHTML = `<div class="menu-head">Panels</div>` +
      PANELS.map((p) =>
        `<label class="menu-item"><input type="checkbox" data-panel="${p.id}"> ${p.label}</label>`).join("") +
      `<button class="menu-item" id="panels-reset" title="Restore every panel to the default docked layout">↺ Reset layout</button>`;
    menu.appendChild(sec);
    sec.querySelectorAll("input[data-panel]").forEach((cb) => {
      cb.addEventListener("change", () => {
        st(cb.dataset.panel).hidden = !cb.checked;
        apply(cb.dataset.panel); saveState();
      });
    });
    sec.querySelector("#panels-reset").addEventListener("click", () => {
      PANELS.forEach((p) => { state[p.id] = { hidden: false, float: null }; apply(p.id); });
      saveState(); syncMenu();
    });
  }

  function syncMenu() {
    document.querySelectorAll("#panels-section input[data-panel]").forEach((cb) => {
      cb.checked = !st(cb.dataset.panel).hidden;
    });
  }

  function init() {
    PANELS.forEach((d) => {
      const el = document.getElementById(d.id);
      if (!el) return;
      el.classList.add("panel-managed");
      injectControls(el, d);
      watchResize(el);
      apply(d.id);
    });
    buildMenu();
    syncMenu();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
