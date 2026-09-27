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


# -- IP-1180 (FR-5410, NFR-3700) — external vignette directories -----------------------------

def _write_vignette_file(directory, vignette_id: str, title: str = "External") -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / f"{vignette_id}.yaml").write_text(
        yaml.safe_dump({"vignette": {
            "id": vignette_id, "title": title,
            "start_epoch_utc": "2030-01-01T00:00:00Z",
            "blue_forces": [], "red_forces": [], "neutral_forces": [], "sensors": [],
        }}),
        encoding="utf-8",
    )


def test_list_vignettes_empty_external_dirs_reproduces_baseline(tmp_path):
    baseline = list_vignettes()
    same = list_vignettes(external_dirs=[])
    assert [v["id"] for v in baseline] == [v["id"] for v in same]
    assert all(v["origin"] == "built-in" for v in same)


def test_list_vignettes_enumerates_external_directory_with_origin_tag(tmp_path):
    ext = tmp_path / "my-external-vignettes"
    _write_vignette_file(ext, "ext-vig-1", "An External Vignette")
    entries = {v["id"]: v for v in list_vignettes(external_dirs=[ext])}
    assert "ext-vig-1" in entries
    assert entries["ext-vig-1"]["origin"] == "my-external-vignettes"


def test_list_vignettes_skips_unreadable_or_missing_external_directory(tmp_path):
    missing = tmp_path / "does-not-exist"
    entries = list_vignettes(external_dirs=[missing])
    # The catalog build still succeeds and still contains every built-in entry.
    assert any(v["id"] == "leo-isr-denial" for v in entries)


def test_list_vignettes_id_collision_resolves_built_in_first(tmp_path):
    ext = tmp_path / "colliding-dir"
    _write_vignette_file(ext, "leo-isr-denial", "A Shadow Attempt")
    entries = [v for v in list_vignettes(external_dirs=[ext]) if v["id"] == "leo-isr-denial"]
    assert len(entries) == 1
    assert entries[0]["origin"] == "built-in"
    assert entries[0]["title"] != "A Shadow Attempt"


def test_load_vignette_finds_object_that_exists_only_in_external_directory(tmp_path):
    ext = tmp_path / "only-here"
    _write_vignette_file(ext, "only-in-external", "Only External")
    vig = load_vignette("only-in-external", external_dirs=[ext])
    assert vig.title == "Only External"
    with pytest.raises(FileNotFoundError):
        load_vignette("only-in-external")  # not visible without the external dir


@pytest.mark.parametrize("bad_id", [
    "../../etc/passwd",
    "/etc/passwd",
    "..\\..\\windows\\system32\\config",
    "~root/.ssh/id_rsa",
    ".env",
    "foo/bar",
    "id with space",
])
def test_load_vignette_rejects_traversal_against_external_directory_too(tmp_path, bad_id):
    """FS-118 Acceptance Criterion 3 — the traversal guard rejects identically whether checked
    against VIGNETTE_DIR (existing coverage, test_defensive_audit_2026.py) or an external
    directory, with no filesystem access on rejection."""
    ext = tmp_path / "some-external-dir"
    ext.mkdir()
    with pytest.raises((ValueError, FileNotFoundError)):
        load_vignette(bad_id, external_dirs=[ext])


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
# Satellite sizing is a soft guideline, not an engine cap (ADR-0019, NFR-1300).
# IP-1061 removed the hard ValueError raises this section used to pin.
# ---------------------------------------------------------------------------

def test_vignette_above_24_satellites_loads():
    """25 orbital assets must load without error — no engine-enforced cap (ADR-0019)."""
    vig = _make_vignette([_sat(i) for i in range(25)])
    build_world(vig)   # no exception


def test_total_satellite_cap_at_limit_passes():
    """Exactly 24 orbital assets must not raise."""
    vig = _make_vignette([_sat(i) for i in range(24)])
    build_world(vig)   # no exception


def test_constellation_above_3_loads():
    """4 satellites in the same group must load without error — no engine-enforced cap (ADR-0019)."""
    sats = [_sat(i, group="ALPHA") for i in range(4)]
    vig = _make_vignette(sats)
    build_world(vig)   # no exception


def test_per_constellation_cap_at_limit_passes():
    """3 satellites in the same group must not raise."""
    sats = [_sat(i, group="ALPHA") for i in range(3)]
    vig = _make_vignette(sats)
    build_world(vig)   # no exception


def test_ungrouped_satellites_not_counted_per_constellation():
    """5 ungrouped orbital assets are fine — no group means not constellation-capped."""
    vig = _make_vignette([_sat(i) for i in range(5)])
    build_world(vig)   # no exception
