"""Baseline power trajectory must be stable — audit Jun 2026 §TT&C FIX 1/2.

The complaint that drove this test: "in the first vignette satellite power goes low
without clear reasoning." Root cause was a content-calibration bug — the YAML drain
rate (0.0003 SoC/s) drove a ~63%-depth-of-discharge sawtooth every orbit (1.00 → 0.37),
3-4x deeper than any real LEO bus, with a razor-thin per-orbit margin that tipped into a
death spiral under any extra load.

These tests pin the corrected behaviour:
  - With NO Red action, the ISR satellite's battery never falls into the yellow band
    (< 0.30 SoC) across several orbits of baseline eclipse cycling.
  - The penumbra-aware tick blends charge/drain by lit fraction (no binary cliff).
"""
from __future__ import annotations

from spacesim.content.vignette import load_vignette
from spacesim.engine.bus import BusState, advance_bus
from spacesim.engine.simtime import minutes
from spacesim.session.manager import SessionManager


def test_baseline_soc_stays_healthy_over_several_orbits():
    """No attacks, no commands — just advance ~3 LEO orbits and watch the ISR battery.

    A ~600 km LEO orbit is ~97 min; 300 min covers ~3 orbits including ~3 eclipse
    seasons. With the corrected rates the SoC must stay green (>= 0.30) the whole time.
    """
    mgr = SessionManager(load_vignette("leo-isr-denial"), seed=1)
    mgr.start()
    sat = mgr.world.assets["ISR-EO-1"]
    assert sat.bus_state is not None

    lowest = sat.bus_state.power.battery_soc
    # Step in 5-min increments so the bus_tick scheduler (300 s period) fires each step.
    for step_min in range(5, 305, 5):
        mgr.advance_to(mgr.world.now + minutes(5))
        soc = sat.bus_state.power.battery_soc
        lowest = min(lowest, soc)

    assert lowest >= 0.30, (
        f"baseline SoC dipped to {lowest:.3f} with no Red action — the power model is "
        f"draining too aggressively (audit §TT&C FIX 1)"
    )


def test_penumbra_tick_blends_charge_and_drain():
    """A half-lit tick (lit fraction 0.5) nets charge-minus-drain, not a binary switch."""
    bus = BusState(last_update=0)
    bus.power.battery_soc = 0.5
    bus.power.charge_rate_per_s = 0.0001
    bus.power.drain_rate_per_s = 0.0001
    # Fully lit over 600 s: +0.06; fully dark: -0.06; half-lit nets ~0.
    advance_bus(bus, None, minutes(10), sunlit=0.5)
    assert abs(bus.power.battery_soc - 0.5) < 1e-9
    # in_eclipse flag is driven by the lit fraction threshold (0.5 → not in eclipse).
    assert bus.power.in_eclipse is False


def test_full_umbra_still_drains_and_full_sun_still_charges():
    bus = BusState(last_update=0)
    bus.power.battery_soc = 0.5
    bus.power.drain_rate_per_s = 0.0001
    advance_bus(bus, None, minutes(10), sunlit=0.0)
    assert bus.power.battery_soc < 0.5 and bus.power.in_eclipse is True

    bus2 = BusState(last_update=0)
    bus2.power.battery_soc = 0.5
    bus2.power.charge_rate_per_s = 0.0001
    advance_bus(bus2, None, minutes(10), sunlit=1.0)
    assert bus2.power.battery_soc > 0.5 and bus2.power.in_eclipse is False


def test_eclipse_flag_exposed_in_soh_snapshot():
    """The fleet rail / drill-down must be able to SHOW the operator why SoC is falling."""
    from spacesim.engine.bus import soh_snapshot
    bus = BusState(last_update=0)
    advance_bus(bus, None, minutes(5), sunlit=0.0)
    snap = soh_snapshot(bus)
    assert "in_eclipse" in snap and snap["in_eclipse"] is True
