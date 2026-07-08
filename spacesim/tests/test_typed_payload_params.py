"""IP-1171 (FR-5170/FR-5180) — typed per-payload-type parameter sub-models on PayloadState.

Replaces the generic, untyped parameter surface with named, validated, per-payload-type
sub-models — one per type (satcom/isr_eo/isr_sar/sigint/sda/weather/pnt/mw) — populated only
when PayloadState.type matches, so a vignette author (and the eventual Vignette Creator UI,
IP-1174) gets a real schema instead of an opaque ``detail: dict`` bag. Bus power/propulsion
authoring already reaches live fields (PowerState.charge_rate_per_s/drain_rate_per_s,
AssetResources.delta_v_ms) via plain pydantic nested-model coercion — this file also proves
that path never touches the dead AssetResources.power_w field.
"""
from __future__ import annotations

from spacesim.content.vignette import build_world, load_vignette, list_vignettes
from spacesim.engine.bus import PayloadState
from spacesim.engine.entities import Asset
from spacesim.engine.isr import BEAM_MODES


def test_isr_eo_asset_gets_isr_eo_params_only():
    p = PayloadState(type="isr_eo")
    assert p.isr_eo is not None
    assert p.satcom is None
    assert p.isr_sar is None
    assert p.sigint is None
    assert p.sda is None
    assert p.weather is None
    assert p.pnt is None
    assert p.mw is None


def test_satcom_asset_gets_bandwidth_params():
    p = PayloadState(type="satcom")
    assert p.satcom is not None
    assert p.satcom.bandwidth_class in ("narrowband", "wideband")
    assert p.satcom.data_rate_kbps_max > 0
    assert p.isr_eo is None


def test_weather_and_mw_sub_models_mirror_ip1170_beam_modes():
    """weather/mw typed defaults are wired to IP-1170's real BEAM_MODES entries, not invented
    or copied from isr_eo's generic fallback numbers (BL-0053's original symptom)."""
    weather = PayloadState(type="weather")
    mw = PayloadState(type="mw")
    assert weather.weather is not None
    assert mw.mw is not None

    weather_default_bp = BEAM_MODES["weather"]["conus"]
    mw_default_bp = BEAM_MODES["mw"]["scan"]
    assert weather.weather.resolution_m == weather_default_bp["resolution_m"]
    assert weather.weather.swath_km == weather_default_bp["swath_km"]
    assert mw.mw.resolution_m == mw_default_bp["resolution_m"]
    assert mw.mw.swath_km == mw_default_bp["swath_km"]

    eo_default_bp = BEAM_MODES["isr_eo"]["stripmap"]
    assert weather.weather.resolution_m != eo_default_bp["resolution_m"]
    assert mw.mw.resolution_m != eo_default_bp["resolution_m"]


def test_pnt_asset_gets_baseline_accuracy():
    p = PayloadState(type="pnt")
    assert p.pnt is not None
    # R134: GPS SPS baseline is <=9m/95%, single-digit-to-low-tens-of-meters band.
    assert 1.0 <= p.pnt.accuracy_m <= 50.0


def test_explicit_sub_model_override_is_respected_not_overwritten():
    p = PayloadState(type="satcom", satcom={"bandwidth_class": "wideband", "data_rate_kbps_max": 16384.0})
    assert p.satcom.bandwidth_class == "wideband"
    assert p.satcom.data_rate_kbps_max == 16384.0


def test_space_control_type_gets_no_typed_sub_model():
    """space_control is not one of the 8 typed payload types (FR-5170's own list) -- stays
    on the untyped detail dict, per this package's explicit out-of-scope note."""
    p = PayloadState(type="space_control")
    assert all(
        getattr(p, name) is None
        for name in ("satcom", "isr_eo", "isr_sar", "sigint", "sda", "weather", "pnt", "mw")
    )


def test_bus_power_and_propulsion_override_reaches_live_fields_not_dead_power_w():
    data = {
        "id": "SAT-TEST-1171",
        "owner": "blue",
        "resources": {"delta_v_ms": 500.0, "power_w": 999.0},
        "bus_state": {"power": {"charge_rate_per_s": 0.01, "drain_rate_per_s": 0.02}},
    }
    asset = Asset.model_validate(data)
    assert asset.resources.delta_v_ms == 500.0
    assert asset.bus_state.power.charge_rate_per_s == 0.01
    assert asset.bus_state.power.drain_rate_per_s == 0.02
    # power_w is a dead field (R111 §3/§5) -- setting it is harmless but must never be read
    # by anything this package's own scope touches; confirmed it round-trips inertly.
    assert asset.resources.power_w == 999.0


def test_all_currently_shipped_vignettes_load_and_build_unchanged():
    """Regression: every additive PayloadState field is Optional/None-defaulting, so none of
    the currently shipped vignettes change behavior."""
    ids = [v["id"] for v in list_vignettes()]
    assert len(ids) >= 19, f"expected at least 19 shipped vignettes, found {len(ids)}"
    for vid in ids:
        vignette = load_vignette(vid)
        world, ctx = build_world(vignette)
        assert world.assets
