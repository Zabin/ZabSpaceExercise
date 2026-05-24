"""Bus SOH model: limits/alarms, battery in eclipse, payload gating, storage, ops_fidelity."""

from __future__ import annotations

from spacesim.engine.bus import (
    BusState,
    PayloadState,
    advance_bus,
    bus_view,
    can_collect,
    downlink_storage,
    enter_safe_mode,
    overall_status,
    payload_available,
    status_high,
    status_low,
)
from spacesim.engine.simtime import minutes


def test_limit_coloring():
    assert status_low(0.8, 0.3, 0.15) == "green"
    assert status_low(0.25, 0.3, 0.15) == "yellow"
    assert status_low(0.1, 0.3, 0.15) == "red"
    assert status_high(0.5, 0.85, 0.98) == "green"
    assert status_high(0.9, 0.85, 0.98) == "yellow"
    assert status_high(0.99, 0.85, 0.98) == "red"


def test_battery_drains_in_eclipse_and_trips_yellow_then_red():
    bus = BusState(last_update=0)
    bus.power.battery_soc = 0.5
    bus.power.drain_rate_per_s = 0.5 / 600  # would empty in 10 min
    seen = []
    for k in range(1, 11):
        advance_bus(bus, None, minutes(k), sunlit=False)
        seen.append(bus.power.status)
    assert bus.power.in_eclipse
    assert bus.power.battery_soc < 0.5
    assert "yellow" in seen and "red" in seen  # crossed both alarm thresholds


def test_sunlit_recharges_battery():
    bus = BusState(last_update=0)
    bus.power.battery_soc = 0.2
    bus.power.charge_rate_per_s = 0.5 / 600
    advance_bus(bus, None, minutes(5), sunlit=True)
    assert bus.power.battery_soc > 0.2
    assert not bus.power.in_eclipse


def test_payload_gated_by_safe_mode_and_power():
    bus = BusState()
    assert payload_available(bus)
    bus.power.battery_soc = 0.1  # red
    advance_bus(bus, None, 0, sunlit=True)
    assert not payload_available(bus)
    bus2 = BusState()
    enter_safe_mode(bus2, now=1000, cause="cyber")
    assert not payload_available(bus2)
    assert bus2.mode == "safe_mode"


def test_isr_storage_fills_blocks_collection_until_downlink():
    bus = BusState(last_update=0)
    payload = PayloadState(type="isr_eo", collecting=True, collect_rate_per_s=1.0 / 600)
    for k in range(1, 13):  # >10 min of collection fills storage
        advance_bus(bus, payload, minutes(k), sunlit=True)
    assert bus.cdh.storage_frac >= 1.0
    assert not can_collect(bus)        # storage full → no more collection
    downlink_storage(bus, 1.0)
    assert bus.cdh.storage_frac == 0.0
    assert can_collect(bus)            # downlink frees storage


def test_ops_fidelity_collapses_or_expands_the_bus_view():
    bus = BusState()
    bus.power.battery_soc = 0.1  # red
    advance_bus(bus, None, 0, sunlit=True)
    tactical = bus_view(bus, "tactical")
    assert set(tactical.keys()) == {"health"} and tactical["health"] == "red"
    realistic = bus_view(bus, "realistic")
    assert "power" in realistic and "detail" not in realistic
    full = bus_view(bus, "full_ttc")
    assert "detail" in full and full["detail"]["battery_soc"] == 0.1
    assert overall_status(bus) == "red"
