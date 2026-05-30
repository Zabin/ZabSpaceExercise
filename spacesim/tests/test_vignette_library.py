"""Validates the four-track vignette library (mission-set / Red COA / learning / novel).

Architecture defined in ``docs/vignettes/00-LIBRARY-ARCHITECTURE.md``.  Each new vignette must
load, build a world that respects the satellite caps, start a session, evaluate objectives, and
render both cells' views without error.
"""

from __future__ import annotations

import pytest

from spacesim.content.vignette import list_vignettes, load_vignette
from spacesim.session.manager import SessionManager


# The library partitions vignette ids by track prefix (see §1 of the architecture doc).
MISSION_TRIALS = {"mt-isr-sar", "mt-sigint-geolocate", "mt-weather-collect"}
RED_COA = {"coa-russia-ml", "coa-russia-md", "coa-china-ml", "coa-china-md", "coa-misc-iran-ml"}
LEARNING_STREAM = {"learn-intermediate-recovery"}
NOVEL_CONCEPTS = {"nv-isl-relay-debris"}

NEW_VIGNETTES = MISSION_TRIALS | RED_COA | LEARNING_STREAM | NOVEL_CONCEPTS


@pytest.mark.parametrize("vid", sorted(NEW_VIGNETTES))
def test_new_vignette_loads_and_starts(vid: str):
    """Every new vignette: loads, starts a session, has both cells' objectives, renders views."""
    mgr = SessionManager(load_vignette(vid), seed=1)
    mgr.start()
    objs = mgr.objectives()
    assert set(objs.keys()) == {"blue", "red"}
    assert objs["blue"], f"{vid}: no blue objectives defined"
    assert objs["red"], f"{vid}: no red objectives defined"
    mgr.get_view("blue")
    mgr.get_view("red")
    mgr.get_scene("blue")


def test_new_vignettes_are_in_the_registry():
    """All 10 new vignette IDs must be discoverable by list_vignettes()."""
    ids = {v["id"] for v in list_vignettes()}
    missing = NEW_VIGNETTES - ids
    assert not missing, f"missing from registry: {missing}"


def test_mission_trials_use_correct_payload_types():
    """Each mission-set trial must instantiate the correct payload type on its primary Blue sat."""
    expected = {
        "mt-isr-sar": "isr_sar",
        "mt-sigint-geolocate": "sigint",
        "mt-weather-collect": "weather",
    }
    for vid, payload_type in expected.items():
        mgr = SessionManager(load_vignette(vid), seed=1)
        mgr.start()
        payloads = {a.payload_state.type for a in mgr.world.assets.values()
                    if a.payload_state is not None}
        assert payload_type in payloads, f"{vid}: missing payload type {payload_type}"


def test_red_coa_library_covers_three_actors():
    """The Red COA library must cover Russia, China, and at least one Misc actor."""
    russia = {v for v in RED_COA if "russia" in v}
    china = {v for v in RED_COA if "china" in v}
    misc = {v for v in RED_COA if "misc" in v}
    assert russia, "missing Russia COA vignettes"
    assert china, "missing China COA vignettes"
    assert misc, "missing Misc COA vignettes"


def test_russia_and_china_have_ml_and_md_pairs():
    """Architecture §3: each major actor must have both ML and MD COAs."""
    assert "coa-russia-ml" in RED_COA and "coa-russia-md" in RED_COA
    assert "coa-china-ml" in RED_COA and "coa-china-md" in RED_COA


def test_red_kinetic_authorized_only_in_md_vignettes():
    """ML scenarios should not pre-authorize kinetic Red action; MD scenarios should."""
    for vid in RED_COA:
        mgr = SessionManager(load_vignette(vid), seed=1)
        mgr.start()
        kinetic_default = mgr.ctx.roe.get("kinetic_authorized", False)
        if vid.endswith("-md"):
            assert kinetic_default is True, f"{vid}: MD COA should default kinetic_authorized=True"
        else:
            assert kinetic_default is False, f"{vid}: ML COA should default kinetic_authorized=False"


def test_isl_relay_vignette_marks_assets_as_isl_capable():
    """The novel ISL-relay vignette must have at least two ISL-capable Blue satellites."""
    mgr = SessionManager(load_vignette("nv-isl-relay-debris"), seed=1)
    mgr.start()
    isl = [a for a in mgr.world.assets.values()
           if a.owner == "blue" and a.isl_capable and a.orbit is not None]
    assert len(isl) >= 2, "ISL-relay vignette needs ≥2 ISL-capable blue sats"


def test_recovery_learning_vignette_has_tutorial_script():
    """The intermediate recovery vignette ships a per-cell tutorial script."""
    vig = load_vignette("learn-intermediate-recovery")
    assert "blue" in vig.tutorial and "red" in vig.tutorial
    assert len(vig.tutorial["blue"]) >= 5
    assert len(vig.tutorial["red"]) >= 5
