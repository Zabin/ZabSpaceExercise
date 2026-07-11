"""IP-1171 (FR-5170/FR-5180) — typed per-payload-type parameter sub-schemas + bus power/
propulsion authoring confirmation.

Each of the 8 payload types gets a named, validated, R109/R110/R129/R134-grounded sub-model on
``PayloadState``, auto-populated only for the field matching ``PayloadState.type`` — never a
generic key-value bag, never a mismatched sub-model populated by accident.
"""
from __future__ import annotations

from spacesim.engine.bus import (
    IsrEoParams,
    IsrSarParams,
    MwParams,
    PayloadState,
    PntParams,
    SatcomParams,
    SdaParams,
    SigintParams,
    WeatherParams,
)
from spacesim.engine.entities import Asset, AssetResources
from spacesim.engine.isr import BEAM_MODES

_ALL_PARAM_FIELDS = ("satcom", "isr_eo", "isr_sar", "sigint", "sda", "weather", "mw", "pnt")


def _other_fields_are_none(payload: PayloadState, populated: str) -> bool:
    return all(getattr(payload, f) is None for f in _ALL_PARAM_FIELDS if f != populated)


def test_isr_eo_payload_populates_only_isr_eo_params_with_named_fields():
    payload = PayloadState(type="isr_eo")
    assert isinstance(payload.isr_eo, IsrEoParams)
    assert payload.isr_eo.resolution_m > 0
    assert payload.isr_eo.swath_km > 0
    assert _other_fields_are_none(payload, "isr_eo")


def test_satcom_payload_populates_only_satcom_params_with_bandwidth_fields():
    payload = PayloadState(type="satcom")
    assert isinstance(payload.satcom, SatcomParams)
    assert payload.satcom.data_rate_kbps_max > 0
    assert payload.satcom.bandwidth_class in ("narrowband", "wideband_ku", "wideband_ka_hts")
    assert _other_fields_are_none(payload, "satcom")


def test_isr_sar_payload_populates_only_isr_sar_params():
    payload = PayloadState(type="isr_sar")
    assert isinstance(payload.isr_sar, IsrSarParams)
    assert _other_fields_are_none(payload, "isr_sar")


def test_sigint_payload_populates_only_sigint_params():
    payload = PayloadState(type="sigint")
    assert isinstance(payload.sigint, SigintParams)
    assert payload.sigint.band in ("UHF", "L", "S", "X", "Ku", "Ka", "W")
    assert payload.sigint.mode in ("scan", "track", "geolocate")
    assert _other_fields_are_none(payload, "sigint")


def test_sda_payload_populates_only_sda_params():
    payload = PayloadState(type="sda")
    assert isinstance(payload.sda, SdaParams)
    assert _other_fields_are_none(payload, "sda")


def test_pnt_payload_populates_only_pnt_params_with_sps_baseline_accuracy():
    payload = PayloadState(type="pnt")
    assert isinstance(payload.pnt, PntParams)
    # R134 — GPS SPS baseline: single-digit-to-low-tens-of-meters, not sub-meter.
    assert 1.0 <= payload.pnt.baseline_accuracy_m <= 20.0
    assert _other_fields_are_none(payload, "pnt")


def test_weather_and_mw_payloads_populate_typed_params_grounded_in_now_verified_beam_modes():
    """IP-1170 (BL-0053) has reached VERIFIED — weather/mw are no longer 'plausible but inert';
    their typed sub-models mirror the real, R109-grounded BEAM_MODES default-mode entries."""
    weather = PayloadState(type="weather")
    assert isinstance(weather.weather, WeatherParams)
    assert _other_fields_are_none(weather, "weather")
    conus = BEAM_MODES["weather"]["conus"]
    assert weather.weather.swath_km == conus["swath_km"]
    assert weather.weather.resolution_m == conus["resolution_m"]
    assert weather.weather.duty_cycle == conus["duty_cycle"]

    mw = PayloadState(type="mw")
    assert isinstance(mw.mw, MwParams)
    assert _other_fields_are_none(mw, "mw")
    scan = BEAM_MODES["mw"]["scan"]
    assert mw.mw.swath_km == scan["swath_km"]
    assert mw.mw.resolution_m == scan["resolution_m"]
    assert mw.mw.duty_cycle == scan["duty_cycle"]


def test_isr_eo_isr_sar_sda_authored_defaults_mirror_their_own_beam_modes_default_mode():
    """The three lowest-risk types (already grounded via BEAM_MODES before this package)
    mirror their own default-mode entry exactly — an authored baseline, not a copy of a
    different type's numbers."""
    eo = PayloadState(type="isr_eo").isr_eo
    eo_default = BEAM_MODES["isr_eo"]["stripmap"]
    assert eo.swath_km == eo_default["swath_km"]
    assert eo.resolution_m == eo_default["resolution_m"]

    sar = PayloadState(type="isr_sar").isr_sar
    sar_default = BEAM_MODES["isr_sar"]["stripmap"]
    assert sar.swath_km == sar_default["swath_km"]
    assert sar.resolution_m == sar_default["resolution_m"]

    sda = PayloadState(type="sda").sda
    sda_default = BEAM_MODES["sda"]["nominal"]
    assert sda.swath_km == sda_default["swath_km"]
    assert sda.resolution_m == sda_default["resolution_m"]


def test_unrecognized_payload_type_populates_no_typed_sub_model():
    payload = PayloadState(type="space_control")
    assert all(getattr(payload, f) is None for f in _ALL_PARAM_FIELDS)


def test_explicit_vignette_authored_values_are_not_overwritten_by_auto_population():
    payload = PayloadState(type="satcom", satcom=SatcomParams(bandwidth_class="wideband_ka_hts",
                                                                data_rate_kbps_max=16384))
    assert payload.satcom.bandwidth_class == "wideband_ka_hts"
    assert payload.satcom.data_rate_kbps_max == 16384


def test_bus_power_and_propulsion_overrides_reach_live_fields_not_power_w():
    """FR-5180 — confirms (not adds) that Asset.model_validate() already routes per-asset
    vignette overrides to PowerState.charge_rate_per_s/drain_rate_per_s and
    AssetResources.delta_v_ms, never AssetResources.power_w."""
    data = {
        "id": "IP1171-BUS-TEST", "owner": "blue", "kind": "satellite",
        "resources": {"delta_v_ms": 350.0, "power_w": 999.0},
        "bus_state": {"power": {"charge_rate_per_s": 0.0021, "drain_rate_per_s": 0.0009}},
    }
    asset = Asset.model_validate(data)
    assert asset.resources.delta_v_ms == 350.0
    assert asset.bus_state.power.charge_rate_per_s == 0.0021
    assert asset.bus_state.power.drain_rate_per_s == 0.0009
    # power_w is accepted (the field still exists) but is never read by advance_bus — the
    # dead-field finding this package's own Risks/ADS-5100B §3.1 discloses, not a defect here.
    assert asset.resources.power_w == 999.0


def test_all_19_vignettes_load_and_build_unchanged_with_new_optional_fields():
    from spacesim.content.vignette import build_world, list_vignettes, load_vignette
    vignettes = list_vignettes()
    assert len(vignettes) == 19
    for v in vignettes:
        vig = load_vignette(v["id"])
        world, ctx = build_world(vig)
        assert len(world.assets) > 0
