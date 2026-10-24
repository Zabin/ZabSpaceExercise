"""IP-1340 (FS-134; NFR-2840) — a headless-browser suite for the console's load-bearing rules:
(a) fog of war — nothing a cell has not detected is drawn or listed (NFR-3010);
(b) plan-first — a refused order disables Issue with its reason before any issue (NFR-3020);
(c) irreversible effects (`engage`, `cyber`) need a consequence confirmation.

The module starts the real server (loopback, free port, background thread), drives the shipped
client in Chromium, and skips with a named reason where Playwright or a Chromium build is missing.
It never downloads a browser. Session setup goes through the HTTP API naming ``cell=white``, so only
the rule under test is driven in the page. Waits are on page state, never fixed sleeps.
"""

from __future__ import annotations

import glob
import json
import os
import re
import socket
import threading
import time
from pathlib import Path

import pytest
import yaml

pytestmark = [pytest.mark.browser, pytest.mark.verifies("NFR-2840")]

W = {"cell": "white"}
BROWSER_ROOT_DEFAULT = "/opt/pw-browsers"

# Wrap the 2D canvas text calls before any console script runs and record every label drawn.
INIT_SCRIPT = """
window.__inflight = 0;      // dry-run (order/validate) requests in flight; `settle()` waits on it
const __fetch = window.fetch;   // (harmless now that the client discards superseded responses, IP-1073)
window.fetch = function (u, o) {
  const watch = String(u).includes('/order/validate');
  if (watch) window.__inflight++;
  return __fetch.call(this, u, o).finally(() => { if (watch) window.__inflight--; });
};
window.__labels = [];
for (const k of ['fillText', 'strokeText']) {
  const o = CanvasRenderingContext2D.prototype[k];
  CanvasRenderingContext2D.prototype[k] = function (t, ...a) {
    try { window.__labels.push(String(t)); } catch (e) {}
    return o.call(this, t, ...a);
  };
}
"""


# -- browser discovery (Design Decision 1) ------------------------------------------------------
def resolve_browser(browsers_path: str | None, use_playwright_default: bool = True) -> tuple[str | None, str]:
    """(executable, reason). Playwright's own Chromium when present, else the newest Chromium build
    under ``browsers_path``; ``(None, reason)`` names what is missing. Never downloads."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return None, "Playwright is not installed (pip install playwright)"
    if use_playwright_default:
        with sync_playwright() as pw:
            own = pw.chromium.executable_path
        if own and Path(own).exists():
            return own, ""
    root = browsers_path or BROWSER_ROOT_DEFAULT
    builds = sorted(glob.glob(os.path.join(root, "chromium-*", "chrome-linux*", "chrome")), reverse=True)
    if builds:
        return builds[0], ""
    return None, f"no Chromium build found under {root} (and Playwright's own Chromium is not installed)"


@pytest.mark.verifies("NFR-2840")
def test_without_a_browser_the_lookup_skips_with_a_reason_naming_the_missing_tool(tmp_path):
    exe, reason = resolve_browser(str(tmp_path), use_playwright_default=False)
    if exe is None and "Playwright is not installed" in reason:
        assert "Playwright" in reason
        return
    assert exe is None and "Chromium" in reason and str(tmp_path) in reason


# -- server + content fixtures ------------------------------------------------------------------
@pytest.fixture(scope="module")
def browser_path():
    exe, reason = resolve_browser(os.environ.get("PLAYWRIGHT_BROWSERS_PATH"))
    if exe is None:
        pytest.skip(reason)
    return exe


def _track(obj, owner, orbit, start, characterized, confidence):
    return {"object": obj, "owner": owner, "last_observation": start, "confidence": confidence,
            "characterized": characterized, "classification": "hostile",
            "state_estimate": {**orbit, "epoch": start}}


@pytest.fixture(scope="module")
def content(tmp_path_factory):
    """Two scenario variants in a temporary external content dir (IP-1180 `content:`): one where
    Blue already tracks RED-OBJ, one where Red already holds a weapons-quality track of ISR-EO-1."""
    from spacesim.content.vignette import VIGNETTE_DIR
    from spacesim.engine import simtime

    ext = tmp_path_factory.mktemp("ext")

    def variant(src, new_id, tracks):
        raw = yaml.safe_load((VIGNETTE_DIR / src).read_text(encoding="utf-8"))
        v = raw["vignette"]
        v["id"] = new_id
        start = simtime.from_iso(v["start_epoch_utc"])
        v["initial_tracks"] = tracks(v, start)
        (ext / f"{new_id}.yaml").write_text(yaml.safe_dump(raw), encoding="utf-8")

    def orbit_of(v, side, oid):
        return next(a["orbit"] for a in v[f"{side}_forces"] if a["id"] == oid)

    variant("07-sda-custody-hunt.yaml", "br-blue-tracks-red",
            lambda v, s: [_track("RED-OBJ", "blue", orbit_of(v, "red", "RED-OBJ"), s, False, 0.9)])
    variant("01-leo-isr-denial.yaml", "br-red-tracks-blue",
            lambda v, s: [_track("ISR-EO-1", "red", orbit_of(v, "blue", "ISR-EO-1"), s, True, 1.0)])
    cfg = ext / "cfg.yaml"
    cfg.write_text(yaml.safe_dump({"content": {"external_vignette_dirs": [str(ext)]}}), encoding="utf-8")
    mp = pytest.MonkeyPatch()
    mp.setenv("SPACESIM_CONFIG", str(cfg))
    yield ext
    mp.undo()


@pytest.fixture(scope="module")
def server(content):
    import httpx
    import uvicorn
    from spacesim.ui_web.server import create_app

    s = socket.socket()
    s.bind(("127.0.0.1", 0))      # loopback only
    port = s.getsockname()[1]
    s.close()
    srv = uvicorn.Server(uvicorn.Config(create_app(), host="127.0.0.1", port=port, log_level="warning"))
    t = threading.Thread(target=srv.run, daemon=True)
    t.start()
    base = f"http://127.0.0.1:{port}"
    for _ in range(200):
        try:
            httpx.get(base + "/api/sessions", timeout=1)
            break
        except Exception:
            time.sleep(0.05)
    else:
        raise RuntimeError("test server did not start")
    yield base
    srv.should_exit = True
    t.join(timeout=10)


@pytest.fixture(scope="module")
def pw_browser(browser_path):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True, executable_path=browser_path)
        yield b
        b.close()


class Console:
    def __init__(self, base, browser, vignette, viewport=None):
        import httpx
        self.base, self.http = base, httpx.Client(base_url=base, timeout=30)
        self.sid = self.http.post("/api/sessions", json={"vignette_id": vignette, "seed": 1}).json()["session"]
        assert self.http.post(f"/api/sessions/{self.sid}/start", params=W).status_code == 200
        assert self.http.post(f"/api/sessions/{self.sid}/clock", params=W, json={"running": False}).status_code == 200
        self.ctx = browser.new_context(viewport=viewport or {"width": 1500, "height": 1000})
        self.errors: list[str] = []          # uncaught page errors (an unhandled rejection is one)
        self.ctx.add_init_script(INIT_SCRIPT)
        self.page = self.ctx.new_page()
        self.page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.dialogs: list[str] = []
        self.accept = False
        self.page.on("dialog", self._on_dialog)
        self.page.goto(f"{base}/#{self.sid}")
        self.page.wait_for_function("document.querySelectorAll('#fleet-panel tbody tr').length > 0")

    def _on_dialog(self, d):
        self.dialogs.append(d.message)
        d.accept() if self.accept else d.dismiss()

    def close(self):
        self.ctx.close()
        self.http.close()

    def seat(self, cell):
        """Switch seat and wait until the console has re-rendered for it: the scene the client
        fetches for that seat has arrived and been drawn, and the map is redrawn from it."""
        p = self.page
        scene = "blue" if cell == "white" else cell        # White views through the Blue scene
        with p.expect_response(lambda r: r.url.split("?")[0].endswith(f"/scene/{scene}")):
            p.click(f'button.cell[data-cell="{cell}"]')
        p.wait_for_function(f"document.body.dataset.cell === '{cell}' && SCENE && SCENE.cell === '{scene}'")
        p.evaluate("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")
        p.evaluate("window.__labels = []; drawMap();")       # the client's own redraw of its current state
        p.wait_for_function("window.__labels.length > 0")
        p.wait_for_function("document.querySelectorAll('#o-actor option').length > 0")

    def surfaces(self) -> str:
        """Everything a cell can read about objects: fleet rows, every option in the order and
        tasking panels, and every label the canvases drew."""
        p = self.page
        fleet = p.inner_text("#fleet-panel")
        options = p.eval_on_selector_all("#order-panel option, #tasking-panel option",
                                         "els => els.map(e => e.value + ' ' + e.textContent)")
        return "\n".join([fleet, *options, *p.evaluate("window.__labels")])

    def truth_ids(self, owner):
        god = self.http.get(f"/api/sessions/{self.sid}/godview").json()
        assets = god["assets"].values() if isinstance(god["assets"], dict) else god["assets"]
        return {a["id"] for a in assets if a["owner"] == owner}

    def tracked(self, cell):
        return {t["object"] for t in self.http.get(f"/api/sessions/{self.sid}/scene/{cell}").json()["tracks"]}

    def orders(self, cell):
        return len(self.http.get(f"/api/sessions/{self.sid}/orders/{cell}").json())

    def settle(self):
        self.page.wait_for_function("window.__inflight === 0")

    def compose(self, actor, action, target=None, params=None):
        p = self.page
        p.select_option("#o-actor", actor)
        self.settle()
        p.select_option("#o-action", action)
        self.settle()
        if target is not None:
            p.fill("#o-target-manual", target)
            self.settle()
        if params is not None:
            p.evaluate("document.getElementById('json-params-wrap').open = true")
            p.fill("#o-params", params)
            self.settle()


@pytest.fixture()
def console(server, pw_browser):
    made = []

    def open_(vignette, viewport=None):
        c = Console(server, pw_browser, vignette, viewport)
        made.append(c)
        return c

    yield open_
    for c in made:
        c.close()


def mentions(text, oid):
    return re.search(rf"(?<![A-Za-z0-9_-]){re.escape(oid)}(?![A-Za-z0-9_-])", text) is not None


# -- rule (a): fog of war -----------------------------------------------------------------------
@pytest.mark.verifies("NFR-2840", "NFR-3010")
def test_blue_view_names_no_red_object_blue_has_not_detected(console):
    c = console("sda-custody-hunt")
    c.seat("blue")
    hidden = c.truth_ids("red") - c.tracked("blue")
    assert hidden, "non-vacuity: the scenario must hold a Red object Blue has not detected"
    text = c.surfaces()
    assert [h for h in sorted(hidden) if mentions(text, h)] == []


@pytest.mark.verifies("NFR-2840", "NFR-3010")
def test_red_view_names_no_blue_object_red_has_not_detected(console):
    c = console("leo-isr-denial")
    c.seat("red")
    hidden = c.truth_ids("blue") - c.tracked("red")
    assert hidden
    text = c.surfaces()
    assert [h for h in sorted(hidden) if mentions(text, h)] == []


@pytest.mark.verifies("NFR-2840", "NFR-3010")
def test_a_tracked_object_is_drawn_with_its_confidence_encoding(console):
    c = console("br-blue-tracks-red")
    c.seat("blue")
    assert c.tracked("blue") == {"RED-OBJ"}
    c.page.wait_for_function("window.__labels.some(l => /RED-OBJ ±[0-9.]+km/.test(l))")   # position uncertainty
    row = c.page.locator("#tracks tbody tr", has_text="RED-OBJ").first       # the custody table row
    assert re.search(r"0\.\d\d", row.inner_text())


@pytest.mark.verifies("NFR-2840")
def test_white_view_shows_the_objects_the_cells_cannot_see(console):
    c = console("leo-isr-denial")
    c.seat("white")
    c.page.wait_for_function("[...document.querySelectorAll('#o-target option')].some(o => o.value === 'RED-ASAT')")
    text = c.surfaces()
    assert mentions(text, "RED-ASAT") and mentions(text, "ISR-EO-1")


# -- rule (b): plan-first -----------------------------------------------------------------------
@pytest.mark.verifies("NFR-2840", "NFR-3020")
def test_a_refused_order_disables_issue_with_its_reason_before_any_issue(console):
    c = console("leo-isr-denial")
    c.seat("blue")
    c.compose("ISR-EO-1", "downlink", params='{"via":"GS-NORTH"}')
    c.page.wait_for_function("document.getElementById('o-preview').textContent.includes('will queue')")
    assert c.page.is_enabled("#issue")
    c.compose("ISR-EO-1", "downlink", params='{"via":"NO-SUCH-STATION"}')
    c.page.wait_for_function("document.getElementById('issue').disabled")
    reason = c.page.inner_text("#o-preview")
    assert reason.strip() and "will queue" not in reason
    assert c.orders("blue") == 0                      # nothing was issued to learn this


@pytest.mark.verifies("NFR-2840", "NFR-3020")
def test_malformed_parameters_disable_issue_and_a_click_while_disabled_sends_nothing(console):
    c = console("leo-isr-denial")
    c.seat("blue")
    c.compose("ISR-EO-1", "downlink", params="{not json")
    c.page.wait_for_function("document.getElementById('issue').disabled")
    assert c.page.inner_text("#o-preview").strip()
    c.page.click("#issue", force=True)
    c.page.wait_for_timeout(300)       # let a (wrongly) sent request land; there is no event to await
    assert c.orders("blue") == 0 and c.dialogs == []


# -- rule (c): consequence confirmation ----------------------------------------------------------
def _confirm_flow(c, cell, actor, action, target, flag=None):
    if flag:
        ack = c.http.post(f"/api/sessions/{c.sid}/roe/change",
                          json={"cell": "white", "target_cell": cell, "flag": flag, "value": True}).json()
        assert ack["ok"], ack
    c.seat(cell)
    c.compose(actor, action, target=target)
    c.page.wait_for_function("!document.getElementById('issue').disabled")
    before = c.orders(cell)
    c.accept = False
    c.page.click("#issue")
    c.page.wait_for_function("document.getElementById('order-result').textContent.includes('cancelled')")
    assert len(c.dialogs) == 1 and c.orders(cell) == before          # dismissed: nothing sent
    c.accept = True
    c.page.click("#issue")
    c.page.wait_for_function("!document.getElementById('order-result').textContent.includes('cancelled')"
                             " && document.getElementById('order-result').textContent.length > 0")
    assert len(c.dialogs) == 2 and c.orders(cell) == before + 1        # accepted: sent


@pytest.mark.verifies("NFR-2840")
def test_engage_asks_for_a_consequence_confirmation(console):
    c = console("br-red-tracks-blue")
    _confirm_flow(c, "red", "RED-ASAT", "engage", "ISR-EO-1", flag="kinetic_authorized")
    assert "debris" in c.dialogs[0].lower()


@pytest.mark.verifies("NFR-2840")
def test_cyber_asks_for_a_consequence_confirmation(console):
    c = console("satcom-cyber-link")
    _confirm_flow(c, "red", "RED-CYBER", "cyber", "BLUE-SATCOM", flag="cyber_authorized")
    assert "cyber" in c.dialogs[0].lower()


@pytest.mark.verifies("NFR-2840")
def test_observe_issues_with_no_confirmation(console):
    c = console("sda-custody-hunt")
    c.seat("blue")
    c.compose("BLUE-RADAR-1", "observe", target="RED-OBJ")
    c.page.wait_for_function("!document.getElementById('issue').disabled")
    before = c.orders("blue")
    c.page.click("#issue")
    c.page.wait_for_function("document.getElementById('order-result').textContent.length > 0")
    assert c.dialogs == [] and c.orders("blue") == before + 1


# -- IP-1073: the console follows the server's refusals ------------------------------------------
STATUS = "#control-status"


def _palette_labels(c, text):
    p = c.page
    p.keyboard.press("Control+k")
    p.fill("#palette-input", text)
    labels = p.eval_on_selector_all("#palette-list li", "els => els.map(e => e.firstChild.textContent)")
    p.keyboard.press("Escape")
    return labels


@pytest.mark.verifies("FR-4310")
def test_a_non_white_seat_is_not_offered_time_control_in_the_palette(console):
    c = console("leo-isr-denial")
    c.seat("blue")
    assert _palette_labels(c, "advance") == [] and _palette_labels(c, "rewind") == []
    c.seat("white")
    assert len(_palette_labels(c, "advance")) == 3 and len(_palette_labels(c, "rewind")) == 1


@pytest.mark.verifies("FR-4310")
def test_a_non_white_bookmark_click_sends_nothing_and_says_why(console):
    c = console("leo-isr-denial")
    c.seat("blue")
    c.page.evaluate("bmSave([{name: 'mark', t: SCENE.now}])")
    sent = []
    c.page.on("request", lambda r: sent.append(r.url) if "/rewind" in r.url else None)
    # the bookmark list lives in the White-only AAR panel, hidden from this seat: dispatch the click
    c.page.dispatch_event(".bookmark-chip", "click")
    c.page.wait_for_function(f"document.querySelector('{STATUS}').textContent.includes('White')")
    assert sent == [] and c.errors == []


@pytest.mark.verifies("NFR-1600")
def test_a_refused_time_control_is_reported_not_thrown(console):
    c = console("leo-isr-denial")
    c.seat("white")
    c.page.route("**/advance*", lambda r: r.fulfill(
        status=403, content_type="application/json", body=json.dumps({"detail": "clock is locked by test"})))
    c.page.keyboard.press("Control+k")
    c.page.fill("#palette-input", "advance +1 min")
    c.page.keyboard.press("Enter")
    c.page.wait_for_function(f"document.querySelector('{STATUS}').textContent.includes('clock is locked by test')")
    assert c.errors == []


def _choose_file(c, name, text):
    c.page.set_input_files("#loadfile", files=[{"name": name, "mimeType": "application/json",
                                                "buffer": text.encode("utf-8")}])


def _ensure_polling(c):
    c.page.evaluate("startRealtimeClock()")      # idempotent; the join path already armed it
    assert c.page.evaluate("REALTIME_ON") is True


@pytest.mark.verifies("NFR-1600")
@pytest.mark.parametrize("seat", ["white", "blue"])
def test_a_refused_load_shows_its_reason_and_leaves_the_session_running(console, seat):
    c = console("leo-isr-denial")
    c.seat(seat)
    _ensure_polling(c)
    _choose_file(c, "bad.json", '{"save_format": 1}')
    c.page.wait_for_function("document.getElementById('session').textContent.includes('Load failed')")
    assert c.page.evaluate("REALTIME_ON") is True and c.page.evaluate("SID") == c.sid
    assert c.errors == []


@pytest.mark.verifies("NFR-1600")
def test_an_unparseable_save_file_is_reported(console):
    c = console("leo-isr-denial")
    c.seat("white")
    _ensure_polling(c)
    _choose_file(c, "junk.json", "not json")
    c.page.wait_for_function("document.getElementById('session').textContent.includes('Load failed')")
    assert c.page.evaluate("REALTIME_ON") is True and c.page.evaluate("SID") == c.sid
    assert c.errors == []


@pytest.mark.verifies("FR-7230")
def test_a_legacy_saves_resume_warning_is_shown(console):
    c = console("leo-isr-denial")
    c.seat("white")
    save = c.http.get(f"/api/sessions/{c.sid}/save", params=W).json()
    for k in ("save_format", "content", "baseline"):
        save.pop(k, None)
    _choose_file(c, "legacy.json", json.dumps(save))
    c.page.wait_for_function(f"SID !== '{c.sid}'")
    assert any("legacy save" in d for d in c.dialogs), c.dialogs


@pytest.mark.verifies("FR-4310")
def test_a_player_seat_loading_a_vignette_sees_the_refusal(console):
    c = console("leo-isr-denial")
    c.seat("blue")
    c.page.evaluate("loadSession()")
    c.page.wait_for_function("document.getElementById('session').textContent.includes('Load failed')")
    assert "white" in c.page.inner_text("#session").lower() and c.errors == []


def _hold_first_validate(c):
    held = []
    def handler(route):
        if not held:
            held.append(route)          # the first response is held until the test releases it
        else:
            route.continue_()
    c.page.route("**/order/validate*", handler)
    return held


GOOD = '{"via":"GS-NORTH"}'
BAD = '{"via":"NO-SUCH-STATION"}'


@pytest.mark.verifies("NFR-3020")
@pytest.mark.parametrize("first,last,accepted", [(BAD, GOOD, True), (GOOD, BAD, False)])
def test_the_dry_run_preview_follows_the_last_edit(console, first, last, accepted):
    c = console("leo-isr-denial")
    c.seat("blue")
    c.compose("ISR-EO-1", "downlink", params=last if accepted is False else first)   # settled start
    p = c.page
    held = _hold_first_validate(c)
    p.fill("#o-params", first)                  # request A: held
    p.wait_for_function("window.__inflight >= 1")
    while not held:
        p.wait_for_timeout(20)
    p.fill("#o-params", last)                   # request B: the last edit, answered at once
    p.wait_for_function("window.__inflight === 1")
    want = "will queue" if accepted else "✗"
    p.wait_for_function(f"document.getElementById('o-preview').textContent.includes('{want}')")
    held[0].continue_()                         # the stale response lands last
    p.wait_for_function("window.__inflight === 0")
    p.evaluate("new Promise(r => setTimeout(r, 50))")        # let the client process the response
    text = p.inner_text("#o-preview")
    assert ("will queue" in text) is accepted and p.is_enabled("#issue") is accepted


@pytest.mark.verifies("NFR-3030")
def test_a_menu_reaches_its_last_entry_at_low_height(console):
    c = console("leo-isr-denial", viewport={"width": 1500, "height": 700})
    p = c.page
    p.click("#view-btn")
    m = p.evaluate("""() => { const e = document.getElementById('view-menu'), r = e.getBoundingClientRect();
                              return {bottom: r.bottom, sh: e.scrollHeight, ch: e.clientHeight}; }""")
    assert m["bottom"] <= 700 and m["sh"] > m["ch"]
    last = p.locator("#view-menu .menu-item").last
    last.scroll_into_view_if_needed()
    box = last.bounding_box()
    assert 0 <= box["y"] and box["y"] + box["height"] <= 700
    p.evaluate("window.__hit = false; document.getElementById('view-menu').addEventListener('click', () => { window.__hit = true; }); 0")
    last.click()                                # Playwright hit-tests the point: it fails if anything covers the entry
    p.wait_for_function("window.__hit === true")
    assert (last.get_attribute("id") or last.inner_text()).strip()    # the last entry (e.g. Reset layout)
