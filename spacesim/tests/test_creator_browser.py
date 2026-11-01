"""IP-1086 (VR-1086 F2/O2) — the Vignette Creator console shows a server refusal to the author.

Real Chromium against the real server (same fixtures as ``test_browser_console_rules.py``): White
opens the Creator, and (a) a save of a draft the load gate would refuse shows the 400 reason in the
result line; (b) a stale-epoch TLE pasted into the TLE form shows the refusal reason; (c) a ground
asset with an unusable id shows the refusal reason. Skips with a named reason where Playwright or
Chromium is missing.
"""
from __future__ import annotations

import json

import pytest

from test_browser_console_rules import browser_path, content, pw_browser, server  # noqa: F401 — fixtures
from tle_helpers import in_epoch_tle

pytestmark = [pytest.mark.browser, pytest.mark.verifies("FR-5110")]

STALE1 = "1 25544U 98067A   24001.50000000  .00016717  00000-0  10270-3 0  9994"
STALE2 = "2 25544  51.6416 247.4627 0006703 130.5360 325.0288 16.20000000999993"


@pytest.fixture()
def creator(server, pw_browser):                                   # noqa: F811
    import httpx
    http = httpx.Client(base_url=server, timeout=30)
    sid = http.post("/api/sessions", json={"vignette_id": "leo-isr-denial", "seed": 1}).json()["session"]
    ctx = pw_browser.new_context(viewport={"width": 1500, "height": 1000})
    page = ctx.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto(f"{server}/#{sid}")
    page.wait_for_function("document.querySelectorAll('#fleet-panel tbody tr').length > 0")
    page.click('button.cell[data-cell="white"]')                 # the Creator is a White-only menu
    page.wait_for_function("document.body.dataset.cell === 'white'")
    page.click("#creator-btn")
    page.wait_for_selector("#creator-menu", state="visible")
    page.click("#creator-new")
    page.wait_for_function("document.getElementById('creator-save-result').textContent.includes('draft')")
    yield page, errors
    ctx.close()
    http.close()


def _result(page, needle):
    page.wait_for_function(f"document.getElementById('creator-save-result').textContent.includes({json.dumps(needle)})")
    return page.inner_text("#creator-save-result")


@pytest.mark.verifies("FR-5110", "FR-5120")
def test_refused_save_of_an_incomplete_draft_shows_the_reason(creator):
    page, errors = creator
    page.fill("#creator-json", json.dumps({"assets": [{"id": "NOORBIT", "owner": "blue", "kind": "satellite"}]}))
    page.click("#creator-json-save")
    page.wait_for_function("document.getElementById('creator-json-result').textContent.includes('saved')")
    page.fill("#creator-save-id", "br-ip1086-refused")
    page.click("#creator-save")
    text = _result(page, "must declare an orbit")
    assert text.startswith("error:") and "NOORBIT" in text and "br-ip1086-refused" in text
    assert not errors


@pytest.mark.verifies("FR-5110", "FR-5311")
def test_stale_tle_paste_shows_the_refusal_reason_and_adds_nothing(creator):
    page, errors = creator
    page.fill("#creator-tle-id", "STALE-1")
    page.fill("#creator-tle-l1", STALE1)
    page.fill("#creator-tle-l2", STALE2)
    page.click("#creator-tle-add")
    text = _result(page, "refused:")
    assert "STALE-1" in text and "TLE does not parse/propagate" in text
    assert "STALE-1" not in page.inner_text("#creator-asset-list")
    # a TLE valid at the exercise start is accepted and reported as such
    l1, l2 = in_epoch_tle()
    page.fill("#creator-tle-id", "GOOD-1")
    page.fill("#creator-tle-l1", l1)
    page.fill("#creator-tle-l2", l2)
    page.click("#creator-tle-add")
    assert _result(page, "TLE added")
    page.wait_for_function("document.getElementById('creator-asset-list').textContent.includes('GOOD-1')")
    assert not errors


@pytest.mark.verifies("FR-5140", "FR-5310")
def test_ground_asset_with_a_bad_id_shows_the_refusal_reason(creator):
    page, errors = creator
    page.fill("#creator-gnd-id", ".hid")
    page.fill("#creator-gnd-lat", "10")
    page.fill("#creator-gnd-lon", "20")
    page.click("#creator-gnd-add")
    text = _result(page, "refused:")
    assert ".hid" in text and "is not valid" in text
    assert not errors
