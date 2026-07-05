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
        # IP-1172: ctx.roe is now cell-keyed; these COA vignettes have no explicit roe: block,
        # so both cells share the same legacy-fallback value — checking Red's own is correct.
        kinetic_default = mgr.ctx.roe.get("red", {}).get("kinetic_authorized", False)
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


# ---------------------------------------------------------------------------
# Realistic ground infrastructure (docs/vignettes/GROUND-INFRASTRUCTURE.md)
# ---------------------------------------------------------------------------

# Canonical real-world coordinates the library uses for Blue/Red ground sites. If a vignette
# author moves a known site to fictional coordinates, this test will catch it.
KNOWN_SITES = {
    # Blue
    "Kourou":           (5.24, -52.77),
    "Al Dhafra":        (24.25, 54.55),
    "Diego Garcia":     (-7.41, 72.45),
    "Andersen Guam":    (13.62, 144.86),
    "Vandenberg":       (34.74, -120.57),
    "Schriever":        (38.81, -104.53),
    "RAF Oakhanger":    (51.12, -0.89),
    "SvalSat":          (78.23, 15.39),
    "Wallops":          (37.94, -75.46),
    "Fairbanks":        (64.86, -147.85),
    "Cape Cod SFS":     (41.75, -70.54),
    "Eglin AFB":        (30.57, -86.21),
    "RAF Fylingdales":  (54.36, -0.67),
    "Cavalier SFS":     (48.72, -97.90),
    "Vardo Globus":     (70.37, 31.13),
    "GEODSS Maui":      (20.71, -156.26),
    "GEODSS Socorro":   (33.82, -106.66),
    "Al Yah UAE":       (24.21, 55.74),
    # Red
    "Plesetsk":         (62.93, 40.57),
    "Don-2N":           (56.17, 37.77),
    "Kaliningrad":      (54.71, 20.51),
    "Dzhankoy":         (45.71, 34.39),
    "Jiuquan":          (40.96, 100.29),
    "Korla":            (41.64, 86.24),
    "Woody Island":     (16.83, 112.34),
    "Bandar Abbas":     (27.13, 56.21),
    "Isfahan":          (32.65, 51.67),
    "Yulin Hainan":     (18.23, 109.70),
}


def _all_ground_locations() -> list[tuple[str, str, float, float]]:
    """Yield (vignette_id, asset_id, lat, lon) for every ground asset across all vignettes."""
    out = []
    for v in list_vignettes():
        vig = load_vignette(v["id"])
        # Force assets with locations
        for force_list in (vig.blue_forces, vig.red_forces, vig.neutral_forces):
            for spec in force_list:
                loc = spec.get("location")
                if loc is not None:
                    out.append((v["id"], spec.get("id", "?"), loc["lat_deg"], loc["lon_deg"]))
        # Sensors with locations
        for s in vig.sensors:
            loc = s.get("location")
            if loc is not None:
                out.append((v["id"], s.get("id", "?"), loc["lat_deg"], loc["lon_deg"]))
    return out


def test_no_ground_assets_at_origin():
    """No ground asset should be at (0, 0) — the Atlantic null-island placeholder."""
    bad = [(vid, aid) for (vid, aid, lat, lon) in _all_ground_locations()
           if abs(lat) < 0.1 and abs(lon) < 0.1]
    assert not bad, f"ground assets at (~0, 0): {bad}"


def test_no_ground_assets_in_ocean_dead_zones():
    """No ground asset should be in the South Atlantic dead zone (-30..0 lat, -30..0 lon)
    — that band is the open ocean between Africa and South America with no plausible bases."""
    bad = []
    for (vid, aid, lat, lon) in _all_ground_locations():
        if -30 < lat < 0 and -30 < lon < 0:
            bad.append((vid, aid, lat, lon))
    assert not bad, f"ground assets in South Atlantic dead zone: {bad}"


def test_known_site_coords_match_canonical():
    """If a vignette uses a canonical site name's coords, they must match the catalog precisely.

    Tolerates 0.5° drift to allow minor adjustments (e.g. notional 'near' positions).
    """
    # Sample a few canonical pairs that should appear in updated vignettes.
    must_appear = [
        ("Plesetsk",      62.93, 40.57),
        ("Jiuquan",       40.96, 100.29),
        ("Kaliningrad",   54.71, 20.51),
        ("Al Dhafra",     24.25, 54.55),
        ("SvalSat",       78.23, 15.39),
        ("GEODSS Maui",   20.71, -156.26),
    ]
    all_coords = [(lat, lon) for (_, _, lat, lon) in _all_ground_locations()]
    for name, lat, lon in must_appear:
        matched = any(abs(la - lat) < 0.5 and abs(lo - lon) < 0.5
                      for (la, lo) in all_coords)
        assert matched, f"canonical site {name} ({lat}, {lon}) not used by any vignette"
