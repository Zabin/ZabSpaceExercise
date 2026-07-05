"""Vignette loading and world-building from data files."""

from __future__ import annotations

import pytest
import yaml

from spacesim.content.vignette import Vignette, build_world, list_vignettes, load_vignette


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_ORBIT = {
    "epoch": 1893456000000000,
    "semi_major_axis_m": 6_778_000.0,
    "eccentricity": 0.0,
    "inclination_deg": 51.6,
    "raan_deg": 0.0,
    "arg_perigee_deg": 0.0,
    "true_anomaly_deg": 0.0,
}


def _make_vignette(blue_forces: list[dict]) -> Vignette:
    raw = {
        "id": "test-caps",
        "title": "Cap test",
        "start_epoch_utc": "2030-01-01T00:00:00Z",
        "blue_forces": blue_forces,
        "red_forces": [],
        "neutral_forces": [],
        "sensors": [],
    }
    return Vignette.model_validate(raw)


def _sat(i: int, group: str | None = None) -> dict:
    d = {"id": f"SAT-{i}", "kind": "satellite", "orbit": dict(_ORBIT, true_anomaly_deg=float(i * 10))}
    if group:
        d["group"] = group
    return d


def test_vignette_1_loads_and_builds_a_world():
    assert any(v["id"] == "leo-isr-denial" for v in list_vignettes())
    vig = load_vignette("leo-isr-denial")
    assert vig.title == "LEO ISR Denial"

    world, ctx = build_world(vig)
    # Forces instantiated with correct ownership.
    assert world.assets["ISR-EO-1"].owner == "blue"
    assert world.assets["JAM-NORTH"].owner == "red"
    assert world.assets["ISR-EO-1"].orbit.epoch == ctx.start_epoch  # epoch defaulted to start
    assert world.sensors["BLUE-RADAR"].owner == "blue"
    # Parameter dials resolve into ROE + deadline. IP-1172: ctx.roe is now cell-keyed; this
    # legacy-only vignette (no explicit roe: block) mirrors the same value to both cells.
    assert ctx.roe["blue"]["kinetic_authorized"] is False
    assert ctx.roe["red"]["kinetic_authorized"] is False
    assert ctx.landing_deadline == ctx.start_epoch + 10800 * 1_000_000


def test_parameter_override_flows_into_roe():
    vig = load_vignette("leo-isr-denial")
    _, ctx = build_world(vig, overrides={"red_kinetic_authorized": True})
    assert ctx.roe["blue"]["kinetic_authorized"] is True
    assert ctx.roe["red"]["kinetic_authorized"] is True


def test_explicit_per_cell_roe_gates_independently_and_is_backward_compatible():
    """IP-1172 (FR-3420, NFR-2010) — explicit roe: block vs. legacy-only fallback."""
    vig = load_vignette("leo-isr-denial")

    # No explicit roe: block on the base vignette — legacy fallback applies.
    assert vig.roe is None

    # An explicit, divergent per-cell block overrides the legacy parameters entirely.
    raw = vig.model_dump()
    raw["roe"] = {"blue": {"kinetic_authorized": True, "cyber_authorized": False},
                  "red": {"kinetic_authorized": False, "cyber_authorized": True}}
    vig2 = Vignette.model_validate(raw)
    _, ctx = build_world(vig2)
    assert ctx.roe["blue"] == {"kinetic_authorized": True, "cyber_authorized": False}
    assert ctx.roe["red"] == {"kinetic_authorized": False, "cyber_authorized": True}


def test_partial_per_cell_roe_block_defaults_missing_subkey_to_false():
    """IP-1172 (FR-3420) — a roe: block that only sets one sub-key for one cell defaults the
    rest to False (fail safe), never raises and never silently authorizes."""
    vig = load_vignette("leo-isr-denial")
    raw = vig.model_dump()
    raw["roe"] = {"blue": {"kinetic_authorized": True}}  # no cyber_authorized key; no "red" key at all
    vig2 = Vignette.model_validate(raw)
    _, ctx = build_world(vig2)
    assert ctx.roe["blue"] == {"kinetic_authorized": True, "cyber_authorized": False}
    assert ctx.roe["red"] == {"kinetic_authorized": False, "cyber_authorized": False}


# ---------------------------------------------------------------------------
# Satellite cap enforcement (build-spec/01-context-and-scope.md §3.1)
# ---------------------------------------------------------------------------

def test_total_satellite_cap_enforced():
    """25 orbital assets must raise ValueError."""
    vig = _make_vignette([_sat(i) for i in range(25)])
    with pytest.raises(ValueError, match="≤24 satellite cap"):
        build_world(vig)


def test_total_satellite_cap_at_limit_passes():
    """Exactly 24 orbital assets must not raise."""
    vig = _make_vignette([_sat(i) for i in range(24)])
    build_world(vig)   # no exception


def test_per_constellation_cap_enforced():
    """4 satellites in the same group must raise ValueError."""
    sats = [_sat(i, group="ALPHA") for i in range(4)]
    vig = _make_vignette(sats)
    with pytest.raises(ValueError, match="constellation.*cap"):
        build_world(vig)


def test_per_constellation_cap_at_limit_passes():
    """3 satellites in the same group must not raise."""
    sats = [_sat(i, group="ALPHA") for i in range(3)]
    vig = _make_vignette(sats)
    build_world(vig)   # no exception


def test_ungrouped_satellites_not_counted_per_constellation():
    """5 ungrouped orbital assets are fine — no group means not constellation-capped."""
    vig = _make_vignette([_sat(i) for i in range(5)])
    build_world(vig)   # no exception
