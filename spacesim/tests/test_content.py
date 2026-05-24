"""Vignette loading and world-building from data files."""

from __future__ import annotations

from spacesim.content.vignette import build_world, list_vignettes, load_vignette


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
    # Parameter dials resolve into ROE + deadline.
    assert ctx.roe["kinetic_authorized"] is False
    assert ctx.landing_deadline == ctx.start_epoch + 10800 * 1_000_000


def test_parameter_override_flows_into_roe():
    vig = load_vignette("leo-isr-denial")
    _, ctx = build_world(vig, overrides={"red_kinetic_authorized": True})
    assert ctx.roe["kinetic_authorized"] is True
