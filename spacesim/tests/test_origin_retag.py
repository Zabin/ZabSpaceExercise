"""IP-1334 / IP-1079 (FS-133) — guard for the test-origin retag.

Pins each retagged test's declared origin set (``(module, function) -> expected IDs``) so the
retag cannot drift back, and re-checks that no test lost its last ID or declares an unresolvable
one. It reads the records ``conftest.py`` collected in this run (only the *selected* items, so a
``-m`` filter or a partial path run leaves out what it deselected). Per pinned row: module file gone
from disk -> fail ("module removed or renamed"); file present but not collected in this run -> not
applicable (passes vacuously, never skips); collected -> the function must exist with exactly the
pinned tag set. The suite growing is not this guard's business (IP-1079: no collected-count bounds).
The browser module's rows are checked by a ``browser``-marked test, so ``-m browser`` checks them
and ``-m "not browser"`` checks the rest; the unfiltered run checks all. No check skips.
"""

from __future__ import annotations

import pytest

import baseline_ids as bi

pytestmark = pytest.mark.verifies("NFR-2820")

# Modules whose tests carry the ``browser`` marker (their rows are checked under ``-m browser``).
BROWSER_MODULES = {"test_browser_console_rules.py"}

EXPECTED = [
    ('test_aar.py', 'test_state_at_time_reconstructs_world_at_arbitrary_time', ('FR-7310', 'NFR-2410')),
    ('test_aar.py', 'test_worlds_at_times_matches_state_at_time', ('FR-7310', 'NFR-2410')),
    ('test_browser_console_rules.py', 'test_a_player_seat_loading_a_vignette_sees_the_refusal', ('FR-4320', 'NFR-2840')),
    ('test_bus_commands.py', 'test_adcs_desaturate_restores_pointing', ('FS-105',)),
    ('test_bus_commands.py', 'test_adcs_point_payload_slews_attitude', ('FS-105',)),
    ('test_bus_commands.py', 'test_batch3_verbs_mutate_observably', ('FS-105',)),
    ('test_bus_commands.py', 'test_batch6_verbs_registered', ('FS-105',)),
    ('test_bus_commands.py', 'test_cdh_load_stored_program_rejected_when_disabled', ('FS-105',)),
    ('test_bus_commands.py', 'test_cdh_load_stored_program_succeeds_when_enabled', ('FS-105',)),
    ('test_bus_commands.py', 'test_cdh_reset_subsystem_exits_fault_state', ('FS-105',)),
    ('test_bus_commands.py', 'test_def_disperse_sets_flags', ('FS-105',)),
    ('test_bus_commands.py', 'test_def_escort_posture_logs_consequence', ('FS-105',)),
    ('test_bus_commands.py', 'test_def_maneuver_evade_can_issue_gate', ('FR-1310',)),
    ('test_bus_commands.py', 'test_def_maneuver_evade_consumes_dv_and_sets_flag', ('FR-1310',)),
    ('test_bus_commands.py', 'test_def_maneuver_evade_rejected_when_dv_insufficient', ('FR-1310',)),
    ('test_bus_commands.py', 'test_def_set_deception_mode_in_verb_set', ('FS-105',)),
    ('test_bus_commands.py', 'test_def_set_deception_mode_requires_payload', ('FS-105',)),
    ('test_bus_commands.py', 'test_def_set_deception_mode_toggles_payload_flag', ('FS-105',)),
    ('test_bus_commands.py', 'test_dump_storage_refreshes_ground_view', ('FR-2310',)),
    ('test_bus_commands.py', 'test_eps_select_bus_changes_charge_mode', ('FS-105',)),
    ('test_bus_commands.py', 'test_frequency_hop_shrinks_jam_signature_in_telemetry', ('FR-2330', 'FR-2410')),
    ('test_bus_commands.py', 'test_lost_asset_command_fails_gracefully', ('FS-105',)),
    ('test_bus_commands.py', 'test_mitigate_interference_shrinks_jam_signature', ('FR-2330', 'FR-2410')),
    ('test_bus_commands.py', 'test_new_verbs_are_in_command_verbs_set', ('FS-105',)),
    ('test_bus_commands.py', 'test_prop_collision_avoid_consumes_dv_and_clears_warning', ('FR-1310',)),
    ('test_bus_commands.py', 'test_prop_collision_avoid_requires_pending_warning', ('FS-105',)),
    ('test_bus_commands.py', 'test_prop_station_keep_consumes_delta_v', ('FR-1310',)),
    ('test_bus_commands.py', 'test_prop_station_keep_in_verb_set', ('FS-105',)),
    ('test_bus_commands.py', 'test_prop_station_keep_insufficient_delta_v', ('FR-1310',)),
    ('test_bus_commands.py', 'test_restore_load_undoes_shed', ('FS-105',)),
    ('test_bus_commands.py', 'test_set_charge_mode_scales_charging', ('FS-105',)),
    ('test_bus_commands.py', 'test_set_mode_changes_attitude', ('FS-105',)),
    ('test_bus_commands.py', 'test_shed_load_slows_battery_drain', ('FS-105',)),
    ('test_cell_activity.py', 'test_scheduled_inject_appears_as_inject_row', ('FS-101',)),
    ('test_cell_activity.py', 'test_scheduled_inject_skipped_when_past_window', ('FS-101',)),
    ('test_config.py', 'test_content_defaults_when_no_file', ('NFR-2700',)),
    ('test_config.py', 'test_content_env_var_overrides_default_path', ('NFR-2700',)),
    ('test_config.py', 'test_content_partial_override_keeps_other_defaults', ('NFR-2700',)),
    ('test_config.py', 'test_content_yaml_overrides', ('NFR-2700',)),
    ('test_console_small_fixes.py', 'test_fire_inject_reports_a_rejection', ('NFR-1600',)),
    ('test_content.py', 'test_vignette_1_loads_and_builds_a_world', ('FR-5310',)),
    ('test_controller_view.py', 'test_read_only', ('FR-4620', 'NFR-2410')),
    ('test_defensive_audit_2026.py', 'test_executed_observe_releases_sensor_booking', ('FR-3210',)),
    ('test_defensive_audit_2026.py', 'test_inject_library_is_cached_for_real', ('FR-4460',)),
    ('test_defensive_audit_2026.py', 'test_period_s_invalid_a', ('NFR-1600',)),
    ('test_defensive_modifiers.py', 'test_harden_still_reduces_safe_mode_susceptibility', ('FR-1420',)),
    ('test_determinism.py', 'test_cannot_advance_backwards', ('FR-1110', 'FR-1120', 'NFR-1500')),
    ('test_determinism.py', 'test_save_round_trip_reproduces_state', ('FR-1120', 'FR-7210', 'NFR-1500')),
    ('test_ephemeris.py', 'test_ephemeris_exports_unchanged_after_migration', ('FR-7410', 'FR-7420')),
    ('test_ephemeris.py', 'test_live_ric_view_is_read_only_and_deterministic', ('FR-8210', 'NFR-2410')),
    ('test_ephemeris.py', 'test_quick_tle_is_read_only', ('FR-7440', 'NFR-2410')),
    ('test_future_work.py', 'test_aar_csv_export_has_three_sections', ('FS-107',)),
    ('test_future_work.py', 'test_aar_csv_export_round_trips_objectives', ('FS-107',)),
    ('test_future_work.py', 'test_aar_json_export_endpoint_serves_csv_and_json', ('FS-107',)),
    ('test_future_work.py', 'test_spoof_drives_integrity_flag_telemetry_signature', ('FR-1410', 'FR-2330')),
    ('test_future_work.py', 'test_vignette_source_endpoint_404s_unknown_id', ('FS-115',)),
    ('test_future_work.py', 'test_vignette_source_endpoint_returns_yaml', ('FS-115',)),
    ('test_future_work_batch11.py', 'test_drag_acceleration_opposes_velocity', ('FR-1230',)),
    ('test_future_work_batch11.py', 'test_drag_decay_negative_for_leo', ('FR-1230',)),
    ('test_future_work_batch11.py', 'test_eclipse_fraction_full_sunlight_on_sun_side', ('FR-1210',)),
    ('test_future_work_batch11.py', 'test_eclipse_fraction_in_range', ('FR-1210',)),
    ('test_future_work_batch11.py', 'test_eclipse_fraction_zero_in_full_umbra', ('FR-1210',)),
    ('test_inject_library.py', 'test_inject_library_loads_nonempty', ('FR-4460',)),
    ('test_inject_library.py', 'test_library_effects_use_supported_types', ('FR-4460',)),
    ('test_inject_library.py', 'test_library_entries_have_required_fields', ('FR-4460',)),
    ('test_inject_library.py', 'test_library_entry_roundtrip_through_fire_inject', ('FR-4410', 'FR-4460')),
    ('test_inject_library.py', 'test_library_is_cached', ('FR-4460',)),
    ('test_inject_library.py', 'test_spawn_debris_effect_creates_debris_field', ('FR-1430', 'FR-4410')),
    ('test_observe_order_remediation.py', 'test_null_params_mean_absent', ('NFR-1600',)),
    ('test_observe_order_remediation.py', 'test_well_formed_orders_unchanged', ('NFR-1600',)),
    ('test_orbit.py', 'test_mean_to_true_extraction_did_not_change_elements_to_rv', ('FR-1210',)),
    ('test_orbit.py', 'test_mean_to_true_round_trips_with_true_to_mean', ('FR-1210',)),
    ('test_order_param_hardening.py', 'test_cyber_params_refused', ('NFR-1600',)),
    ('test_order_param_hardening.py', 'test_engage_params_refused', ('NFR-1600',)),
    ('test_order_param_hardening.py', 'test_failed_cyber_plan_leaves_no_state', ('NFR-1600',)),
    ('test_order_param_hardening.py', 'test_jam_params_refused', ('NFR-1600',)),
    ('test_order_param_hardening.py', 'test_maneuver_dv_refused_and_state_untouched', ('NFR-1600',)),
    ('test_order_param_hardening.py', 'test_null_params_mean_absent', ('NFR-1600',)),
    ('test_order_param_hardening.py', 'test_numeric_strings_still_accepted_with_identical_payloads', ('NFR-1600',)),
    ('test_order_param_hardening.py', 'test_observe_param_check_unchanged', ('NFR-1600',)),
    ('test_order_param_hardening.py', 'test_routing_params_refused', ('NFR-1600',)),
    ('test_orders.py', 'test_custody_confidence_at_decision_captured_for_targeted_actions', ('FR-10110',)),
    ('test_orders.py', 'test_custody_confidence_at_decision_none_without_target_or_track', ('FR-10110',)),
    ('test_orders.py', 'test_custody_confidence_at_decision_replays_byte_identically', ('FR-1120',)),
    ('test_orders.py', 'test_dry_run_never_captures_custody_confidence', ('FS-201', 'NFR-2410')),
    ('test_pending_inject_queue.py', 'test_http_non_white_is_403', ('FR-4320', 'FR-4450')),
    ('test_planning.py', 'test_sensor_contention_serializes_tasks_onto_later_windows', ('FR-3210',)),
    ('test_power_calibration.py', 'test_eclipse_flag_exposed_in_soh_snapshot', ('FR-2110', 'NFR-3050')),
    ('test_save_load_robustness.py', 'test_absent_and_string_classification_load', ('FR-7230', 'NFR-1600')),
    ('test_save_load_robustness.py', 'test_bad_save_is_400_naming_the_problem_and_leaves_no_trace', ('FR-7230', 'NFR-1600')),
    ('test_save_load_robustness.py', 'test_content_equals_the_saved_force_after_pre_start_edits', ('FR-7220',)),
    ('test_save_load_robustness.py', 'test_final_time_boundaries_load', ('FR-4330', 'FR-7230', 'NFR-1600')),
    ('test_save_load_robustness.py', 'test_final_time_ceiling_is_one_year_and_exceeds_shipped_horizons', ('FR-4330', 'FR-7230', 'NFR-1600')),
    ('test_save_load_robustness.py', 'test_junk_order_row_is_400_naming_orders_and_index', ('FR-7230', 'NFR-1600')),
    ('test_save_load_robustness.py', 'test_junk_ssn_row_is_400_naming_ssn_requests', ('FR-7230', 'NFR-1600')),
    ('test_save_load_robustness.py', 'test_legacy_missing_vignette_wording_is_pinned', ('FR-7230', 'NFR-1600')),
    ('test_save_load_robustness.py', 'test_non_mapping_overrides_is_400_naming_overrides', ('FR-7230', 'NFR-1600')),
    ('test_save_load_robustness.py', 'test_non_string_classification_is_400', ('FR-7230', 'NFR-1600')),
    ('test_save_load_robustness.py', 'test_out_of_range_final_time_is_400_naming_final_time', ('FR-7230', 'NFR-1600')),
    ('test_save_load_robustness.py', 'test_pending_row_with_bad_kind_or_payload_is_400', ('FR-7230', 'NFR-1600')),
    ('test_save_load_robustness.py', 'test_pending_row_with_bad_t_is_400', ('FR-7230', 'NFR-1600')),
    ('test_save_load_robustness.py', 'test_refused_loads_do_not_consume_a_session_id', ('NFR-1600',)),
    ('test_save_load_robustness.py', 'test_resume_unchanged_and_content_alone_builds_same_force', ('FR-7210', 'FR-7220')),
    ('test_save_load_robustness.py', 'test_server_backstop_alone_turns_missing_vignette_into_400', ('FR-7230', 'NFR-1600')),
    ('test_save_load_robustness.py', 'test_untouched_session_content_is_the_authored_vignette', ('FR-7220',)),
    ('test_save_load_robustness.py', 'test_valid_order_and_ssn_rows_still_load', ('FR-7230', 'NFR-1600')),
    ('test_save_load_robustness.py', 'test_valid_pending_rows_still_load', ('FR-7230', 'NFR-1600')),
    ('test_save_load_robustness.py', 'test_valid_saves_still_load_with_same_warnings', ('FR-7210', 'FR-7230')),
    ('test_save_load_robustness.py', 'test_validate_save_reraises_missing_vignette_as_value_error', ('FR-7230', 'NFR-1600')),
    ('test_save_load_robustness.py', 'test_whole_refused_set_leaves_registry_unchanged_and_valid_saves_unchanged', ('FR-7230', 'NFR-1600')),
    ('test_self_contained_save.py', 'test_content_portion_extracts_and_loads_as_a_fresh_vignette', ('FR-7220',)),
    ('test_self_contained_save.py', 'test_content_portion_world_matches_baseline_without_force_edits', ('FR-7220',)),
    ('test_self_contained_save.py', 'test_force_added_assets_survive', ('FR-7210',)),
    ('test_self_contained_save.py', 'test_immediate_round_trip_every_shipped_vignette', ('FR-7210',)),
    ('test_self_contained_save.py', 'test_invalid_baseline_refused_and_no_session', ('FR-7230', 'NFR-1800')),
    ('test_self_contained_save.py', 'test_invalid_content_portion_refused_with_problems_and_no_session', ('FR-7230', 'NFR-1800')),
    ('test_self_contained_save.py', 'test_legacy_save_resumes_by_id_with_warning', ('FR-7210',)),
    ('test_self_contained_save.py', 'test_resume_after_vignette_file_deleted_or_renamed', ('FR-7230',)),
    ('test_self_contained_save.py', 'test_resume_after_vignette_file_is_edited', ('FR-7230',)),
    ('test_self_contained_save.py', 'test_resume_in_a_fresh_inprocess_session', ('NFR-1800',)),
    ('test_self_contained_save.py', 'test_save_keeps_every_pre_existing_key', ('FR-7210',)),
    ('test_self_contained_save.py', 'test_simulator_version_mismatch_resumes_with_warning_naming_both', ('FR-7230',)),
    ('test_session_setup.py', 'test_observer_cannot_assign_roles', ('FR-4210', 'FR-4320')),
    ('test_session_setup.py', 'test_only_white_cell_can_assign_roles', ('FR-4210', 'FR-4320')),
    ('test_space_weather_index.py', 'test_drag_and_anomaly_multipliers', ('FR-1230', 'FR-4440')),
    ('test_space_weather_index.py', 'test_series_without_bcs_or_anomaly_block_changes_no_orbit', ('FR-1230',)),
    ('test_ssn.py', 'test_harden_reduces_safe_mode_probability', ('FR-1420',)),
    ('test_telemetry.py', 'test_cyber_signature_ramps_fsw_errors_under_safe_mode', ('FR-2330',)),
    ('test_telemetry.py', 'test_directed_energy_signature_drops_snr_and_heats_optics', ('FR-2330',)),
    ('test_telemetry.py', 'test_ew_jam_signature_raises_rx_power_and_recovers', ('FR-2330',)),
    ('test_telemetry.py', 'test_nominal_series_is_deterministic_and_read_only', ('FR-2330', 'NFR-2410')),
    ('test_telemetry.py', 'test_nominal_series_strips_attack_signature_for_compare_overlay', ('FR-2330',)),
    ('test_telemetry.py', 'test_power_sag_and_kinetic_loss_of_signal', ('FR-2330',)),
    ('test_telemetry.py', 'test_sampler_returns_physical_values_only_no_cause_label', ('FR-2330',)),
    ('test_telemetry.py', 'test_sampling_is_deterministic_and_repeatable', ('FR-2330',)),
    ('test_telemetry.py', 'test_series_cleared_episode_stays_in_history', ('FR-2330',)),
    ('test_telemetry.py', 'test_series_cyber_cpu_load_pre_onset_matches_replay', ('FR-2330',)),
    ('test_telemetry.py', 'test_series_destroyed_asset_not_los_before_kill', ('FR-2330',)),
    ('test_telemetry.py', 'test_series_pre_onset_matches_replay', ('FR-2330',)),
    ('test_telemetry.py', 'test_telemetry_export_is_read_only_and_deterministic', ('FR-2320', 'NFR-2410')),
    ('test_undo_clock_floor.py', 'test_engine_undo_on_empty_log_keeps_initial_time', ('FR-4330', 'NFR-1600')),
    ('test_undo_clock_floor.py', 'test_undo_still_403_for_non_white', ('FR-4330', 'NFR-1600')),
    ('test_validate_order.py', 'test_dry_run_is_side_effect_free', ('NFR-2410', 'NFR-3020')),
    ('test_vignette_creator_session.py', 'test_draft_session_evicted_by_existing_max_live_sessions_cap', ('FR-5110', 'NFR-3710')),
    ('test_vignette_creator_ui.py', 'test_asset_edit_reflected_in_json_view_and_scene', ('FR-5120', 'FR-5150')),
    ('test_vignette_creator_ui.py', 'test_seat_declaration_rejects_non_white_caller', ('FR-4320', 'FR-5160')),
    ('test_vignette_load_validation.py', 'test_http_traversal_id_is_400', ('FR-5310', 'NFR-3700')),
    ('test_web.py', 'test_ephemeris_cell_observed_route_fog_of_war_enforced', ('FR-7420',)),
    ('test_web.py', 'test_maneuver_ledger_route_and_csv_export_are_fog_scoped', ('FR-1320', 'FR-6210')),
    ('test_web.py', 'test_scene_returns_assets', ('FR-8110',)),
    ('test_web.py', 'test_session_discovery_lists_sessions', ('FR-6410',)),
    ('test_web.py', 'test_telemetry_series_count', ('FR-2310',)),
    ('test_white_control_correctness.py', 'test_a_rewind_leaves_the_running_state_and_reanchors', ('FR-4310',)),
    ('test_white_control_correctness.py', 'test_body_seat_is_not_authority', ('FR-4320',)),
    ('test_white_control_correctness.py', 'test_clock_state_exposes_start_epoch', ('FR-4310',)),
    ('test_white_control_correctness.py', 'test_layering_value_error_then_ack', ('NFR-1600',)),
    ('test_white_control_correctness.py', 'test_non_white_is_403_and_non_integer_is_422', ('FR-4310',)),
    ('test_white_control_correctness.py', 'test_rewind_before_start_and_after_now_is_refused', ('FR-4330', 'NFR-1600')),
    ('test_white_control_correctness.py', 'test_rewind_to_start_leaves_a_start_sized_save', ('FR-4330', 'NFR-1600')),
    ('test_white_control_correctness.py', 'test_rewind_to_zero_is_refused_with_the_span_and_changes_nothing', ('FR-4330', 'NFR-1600')),
    ('test_white_control_correctness.py', 'test_seat_routes_refuse_by_query_seat', ('FR-4320',)),
    ('test_white_control_correctness.py', 'test_session_layer_still_refuses_a_non_white_cell', ('FR-4320',)),
    ('test_white_control_correctness.py', 'test_the_span_edges_are_allowed', ('FR-4330',)),
    ('test_white_control_correctness.py', 'test_white_succeeds_with_effect_visible', ('FR-4320',)),
    ('test_white_only_controls.py', 'test_clock_controls_accepted_for_white', ('FR-4310',)),
    ('test_white_only_controls.py', 'test_clock_controls_refused_for_non_white', ('FR-4310',)),
    ('test_white_only_controls.py', 'test_config_controls_accepted_for_white', ('FR-4320',)),
    ('test_white_only_controls.py', 'test_config_controls_refused_for_non_white', ('FR-4320',)),
    ('test_white_only_controls.py', 'test_load_save_refused_for_non_white_accepted_for_white', ('FR-4320',)),
    ('test_white_only_controls.py', 'test_seat_assignment_and_observer_designation_refused_for_player_seats', ('FR-4320',)),
    ('test_white_only_controls.py', 'test_unknown_session_is_404_before_the_seat_check', ('FR-4310', 'FR-4320')),
]

def _ids_by_test(records):
    out: dict[tuple[str, str], set[str]] = {}
    for rec in records:
        out.setdefault((rec.module, rec.func), set()).update(rec.ids)
    return out


def check_rows(records, expected, files_on_disk, collected_modules=None):
    """Pure core of the guard: ``(problems, not_applicable)`` for the pinned ``expected`` rows.

    ``files_on_disk`` is the set of ``test_*.py`` names present; ``collected_modules`` defaults to
    the modules appearing in ``records`` (the records hold selected items only).
    """
    got = _ids_by_test(records)
    collected = {r.module for r in records} if collected_modules is None else set(collected_modules)
    problems, not_applicable = [], []
    for module, func, tags in expected:
        if module not in files_on_disk:
            problems.append(f"{module}::{func}: module removed or renamed")
        elif module not in collected:
            not_applicable.append((module, func))
        elif (module, func) not in got:
            problems.append(f"{module}::{func} no longer exists (renamed or removed?)")
        elif got[(module, func)] != set(tags):
            problems.append(f"{module}::{func} declares {sorted(got[(module, func)])}, "
                            f"expected {sorted(tags)}")
    return problems, not_applicable


@pytest.fixture(scope="session")
def records(request):
    return request.config._verifies_records


def _disk():
    return {p.name for p in bi.TESTS_DIR.glob("test_*.py")}


def _assert_row_in_place(records, row):
    problems, _not_applicable = check_rows(records, [row], _disk())   # not applicable: outside this run
    assert not problems, "\n".join(problems)


@pytest.mark.parametrize("module,func,expected", [r for r in EXPECTED if r[0] not in BROWSER_MODULES],
                         ids=[f"{m}::{f}" for m, f, _ in EXPECTED if m not in BROWSER_MODULES])
def test_each_listed_retag_is_in_place(records, module, func, expected):
    _assert_row_in_place(records, (module, func, expected))


@pytest.mark.browser
@pytest.mark.parametrize("module,func,expected", [r for r in EXPECTED if r[0] in BROWSER_MODULES],
                         ids=[f"{m}::{f}" for m, f, _ in EXPECTED if m in BROWSER_MODULES])
def test_each_listed_browser_retag_is_in_place(records, module, func, expected):
    _assert_row_in_place(records, (module, func, expected))


def test_no_retagged_test_lost_its_last_id_or_declares_an_unresolvable_one(records):
    got = _ids_by_test(records)
    baseline = bi.load_baseline()
    problems = []
    for module, func, _ in EXPECTED:
        ids = got.get((module, func))
        if ids is None:
            continue
        if not ids:
            problems.append(f"{module}::{func} declares no origin")
        problems += [f"{module}::{func}: {i} — {bi.resolve_problem(i, baseline)}"
                     for i in sorted(ids) if bi.resolve_problem(i, baseline)]
    assert not problems, "\n".join(problems)


# -- IP-1079: tests of the guard's own logic (written first; they fail until check_rows exists) ----
import ast
import subprocess
import sys
from pathlib import Path

_THIS = Path(__file__).resolve()
_DISK = {p.name for p in bi.TESTS_DIR.glob("test_*.py")}


def _consistent_records():
    """Synthetic records in which every pinned row is present with exactly its pinned tag set."""
    recs = [bi.OriginRecord(nodeid=f"spacesim/tests/{m}::{f}", module=m, func=f, ids=tuple(t))
            for m, f, t in EXPECTED]
    # every module also holds an unpinned test, as in a real run (a module is "collected" if any item is)
    recs += [bi.OriginRecord(f"spacesim/tests/{m}::test_unpinned", m, "test_unpinned", ("FS-133",))
             for m in sorted({m for m, _, _ in EXPECTED})]
    return recs


@pytest.mark.verifies("FS-133")
def test_a_consistent_record_set_has_no_problems_and_every_row_applicable():
    problems, n_a = check_rows(_consistent_records(), EXPECTED, _DISK)
    assert problems == [] and n_a == []


@pytest.mark.verifies("FS-133")
@pytest.mark.parametrize("victim", [EXPECTED[0], EXPECTED[2], EXPECTED[40], EXPECTED[-1]],
                         ids=lambda r: f"{r[0]}::{r[1]}")
def test_mutation_a_deleted_pinned_test_fails(victim):
    recs = [r for r in _consistent_records() if (r.module, r.func) != victim[:2]]
    problems, _ = check_rows(recs, EXPECTED, _DISK)
    assert len(problems) == 1
    assert f"{victim[0]}::{victim[1]}" in problems[0] and "no longer exists" in problems[0]


@pytest.mark.verifies("FS-133")
@pytest.mark.parametrize("mutate", [lambda ids: ids + ("FR-9999",), lambda ids: ids[1:], lambda ids: ()],
                         ids=["add-a-tag", "drop-a-tag", "empty-set"])
def test_mutation_a_retagged_pinned_test_fails(mutate):
    victim = next(r for r in EXPECTED if len(r[2]) >= 2)
    recs = [bi.OriginRecord(r.nodeid, r.module, r.func, mutate(r.ids)) if (r.module, r.func) == victim[:2] else r
            for r in _consistent_records()]
    problems, _ = check_rows(recs, EXPECTED, _DISK)
    assert len(problems) == 1
    assert f"{victim[0]}::{victim[1]}" in problems[0]
    assert str(sorted(victim[2])) in problems[0] and "expected" in problems[0] and "declares" in problems[0]


@pytest.mark.verifies("FS-133")
def test_mutation_a_removed_module_fails_but_a_deselected_module_does_not():
    module = EXPECTED[0][0]
    rows = [r for r in EXPECTED if r[0] == module]
    recs = [r for r in _consistent_records() if r.module != module]
    problems, n_a = check_rows(recs, EXPECTED, _DISK - {module})
    assert len(problems) == len(rows) and all("module removed or renamed" in p for p in problems)
    problems, n_a = check_rows(recs, EXPECTED, _DISK | {module})   # file present, just not collected
    assert problems == [] and sorted(n_a) == sorted(r[:2] for r in rows)


@pytest.mark.verifies("IP-1079")
def test_growth_in_unpinned_tests_does_not_fail_the_guard():
    recs = _consistent_records()
    recs += [bi.OriginRecord(f"spacesim/tests/test_new.py::test_n{i}", "test_new.py", f"test_n{i}", ("FS-133",))
             for i in range(500)]
    problems, n_a = check_rows(recs, EXPECTED, _DISK | {"test_new.py"})
    assert problems == [] and n_a == []


@pytest.mark.verifies("IP-1079")
def test_the_count_bounds_and_their_test_are_gone():
    src = _THIS.read_text("utf-8")
    for dead in ("COLLECTED" + "_BEFORE", "COLLECTED" + "_UPPER", "def test_collected" + "_count"):
        assert dead not in src


@pytest.mark.verifies("IP-1079")
def test_browser_rows_are_exactly_the_browser_marked_modules():
    for module in {m for m, _, _ in EXPECTED}:
        marked = "pytest.mark.browser" in (bi.TESTS_DIR / module).read_text("utf-8")
        assert (module in BROWSER_MODULES) == marked, module


@pytest.mark.verifies("IP-1079")
def test_no_check_in_the_guard_calls_skip_or_is_skipif_marked():
    tree = ast.parse(_THIS.read_text("utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = ast.unparse(node.func)
            assert f not in ("pytest.skip", "pytest.importorskip", "pytest.xfail"), ast.unparse(node)
            assert f != "pytest.mark.skip" and f != "pytest.mark.skipif", ast.unparse(node)


def _run_guard(tmp_path, *marker_args):
    xml = tmp_path / ("j%d.xml" % len(marker_args))
    cmd = [sys.executable, "-m", "pytest", str(_THIS), "-q", "-p", "no:cacheprovider", "--junitxml", str(xml),
           "-k", "not test_no_double_skip_across_the_three_ways", *marker_args]
    proc = subprocess.run(cmd, cwd=bi.TESTS_DIR.parent.parent, capture_output=True, text=True, timeout=300)
    import xml.etree.ElementTree as ET
    suite = ET.parse(xml).getroot().iter("testcase")
    cases = list(suite)
    skipped = [c.get("name") for c in cases if c.find("skipped") is not None]
    return proc.returncode, len(cases), skipped, proc.stdout[-400:]


@pytest.mark.verifies("IP-1079")
def test_no_double_skip_across_the_three_ways_the_suite_is_run(tmp_path):
    rc_all, n_all, sk_all, out = _run_guard(tmp_path)
    rc_b, n_b, sk_b, out_b = _run_guard(tmp_path, "-m", "browser")
    rc_nb, n_nb, sk_nb, out_nb = _run_guard(tmp_path, "-m", "not browser")
    assert (rc_all, rc_b, rc_nb) == (0, 0, 0), (out, out_b, out_nb)
    assert sk_all == [] and sk_b == [] and sk_nb == []
    assert n_b >= 1 and n_nb >= 1 and n_all >= n_b and n_all >= n_nb   # each filtered run actually runs guard checks
