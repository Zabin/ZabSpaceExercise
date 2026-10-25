"""IP-1160 (FS-116; FR-3510) — a drift guard that runs without a browser: the console's client-side
verb tags (``VERB_ROLE`` in ``app.js``) must agree with the server's authoritative scope table
(``ROLE_SCOPE_BY_VERB``), and the operator-seat plumbing must exist in the shipped client."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from spacesim.session.manager import ROLE_SCOPE_BY_VERB

pytestmark = pytest.mark.verifies("FR-3510")

STATIC = Path(__file__).resolve().parents[1] / "ui_web" / "static"


def _app_js() -> str:
    return (STATIC / "app.js").read_text(encoding="utf-8")


def _verb_role(src: str) -> dict[str, str]:
    block = re.search(r"const VERB_ROLE = \{(.*?)\n\};", src, re.S)
    assert block, "VERB_ROLE block not found in app.js"
    return dict(re.findall(r'"?([\w.]+)"?\s*:\s*"(\w+)"', block.group(1)))


def test_19_every_dotted_client_verb_tag_equals_the_server_scope():
    tags = _verb_role(_app_js())
    dotted = {v: t for v, t in tags.items() if "." in v}
    assert dotted, "no dotted verbs parsed"
    for verb, tag in dotted.items():
        assert verb in ROLE_SCOPE_BY_VERB, f"{verb} is tagged in app.js but unknown to the server"
        assert ("payload" if tag == "sda" else tag) == ROLE_SCOPE_BY_VERB[verb], verb
    # the four the manual filter previously mis-tagged or omitted
    assert dotted["pnt.set_integrity"] == "payload" and dotted["def.escort_posture"] == "bus"
    assert dotted["def.disperse"] == "bus" and dotted["def.set_deception_mode"] == "payload"
    assert dotted["def.harden"] == "payload"                       # already right; must stay


def test_20_the_client_carries_the_operator_seat_through_compose_reasons_and_markup():
    src = _app_js()
    compose = re.search(r"function composeBody\(\) \{(.*?)\n\}\n", src, re.S)
    assert compose and "seat" in compose.group(1)
    tips = re.search(r"const REASON_TIPS = \{(.*?)\n\};", src, re.S).group(1)
    assert "role_scope_not_assigned" in tips and "role_scope_out_of_scope" in tips
    assert 'id="o-seat"' in (STATIC / "index.html").read_text(encoding="utf-8")
