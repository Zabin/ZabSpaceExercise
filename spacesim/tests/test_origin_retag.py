"""IP-1334 (FS-133) — guard for the test-origin retag.

Pins each retagged test's declared origin set (``(module, function) -> expected IDs``) so the
retag cannot drift back, re-checks that no test lost its last ID or declares an unresolvable one,
and that the retag added or removed no test. Reads the records ``conftest.py`` collected in this
run; a row whose module was not collected (a partial run) is skipped, not failed.
"""

from __future__ import annotations

import pytest

import baseline_ids as bi

pytestmark = pytest.mark.verifies("NFR-2820")

# Collected items before the retag (2026-10-24: 1,371 once the IP-1311..IP-1073 stack is merged),
# excluding this module's own items. The
# upper bound leaves room for tests later packages add; tag edits alone must not move the count.
COLLECTED_BEFORE = 1371
COLLECTED_UPPER = 1500

EXPECTED = [
    ('test_aar.py', 'test_state_at_time_reconstructs_world_at_arbitrary_time', ('FR-7310', 'NFR-2410')),
    ('test_aar.py', 'test_worlds_at_times_matches_state_at_time', ('FR-7310', 'NFR-2410')),
    ('test_assessment.py', 'test_assessment_report_presents_dimensions_side_by_side_never_a_composite', ('FR-4710', 'FS-201')),
    ('test_assessment.py', 'test_scoring_functions_never_mutate_world_state', ('FS-201', 'NFR-2410')),
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
    ('test_orders.py', 'test_custody_confidence_at_decision_captured_for_targeted_actions', ('FS-201',)),
    ('test_orders.py', 'test_custody_confidence_at_decision_none_without_target_or_track', ('FS-201',)),
    ('test_orders.py', 'test_custody_confidence_at_decision_replays_byte_identically', ('FR-1120',)),
    ('test_orders.py', 'test_dry_run_never_captures_custody_confidence', ('FS-201', 'NFR-2410')),
    ('test_pending_inject_queue.py', 'test_http_non_white_is_403', ('FR-4320', 'FR-4450')),
    ('test_planning.py', 'test_sensor_contention_serializes_tasks_onto_later_windows', ('FR-3210',)),
    ('test_power_calibration.py', 'test_eclipse_flag_exposed_in_soh_snapshot', ('FR-2110', 'NFR-3050')),
    ('test_save_load_robustness.py', 'test_bad_save_is_400_naming_the_problem_and_leaves_no_trace', ('FR-7230', 'NFR-1600')),
    ('test_save_load_robustness.py', 'test_content_equals_the_saved_force_after_pre_start_edits', ('FR-7220',)),
    ('test_save_load_robustness.py', 'test_refused_loads_do_not_consume_a_session_id', ('NFR-1600',)),
    ('test_save_load_robustness.py', 'test_resume_unchanged_and_content_alone_builds_same_force', ('FR-7210', 'FR-7220')),
    ('test_save_load_robustness.py', 'test_untouched_session_content_is_the_authored_vignette', ('FR-7220',)),
    ('test_save_load_robustness.py', 'test_valid_saves_still_load_with_same_warnings', ('FR-7210', 'FR-7230')),
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
    ('test_white_only_controls.py', 'test_clock_controls_accepted_for_white', ('FR-4310',)),
    ('test_white_only_controls.py', 'test_clock_controls_refused_for_non_white', ('FR-4310',)),
    ('test_white_only_controls.py', 'test_config_controls_accepted_for_white', ('FR-4320',)),
    ('test_white_only_controls.py', 'test_config_controls_refused_for_non_white', ('FR-4320',)),
    ('test_white_only_controls.py', 'test_load_save_refused_for_non_white_accepted_for_white', ('FR-4320',)),
    ('test_white_only_controls.py', 'test_seat_assignment_and_observer_designation_refused_for_player_seats', ('FR-4320',)),
    ('test_white_only_controls.py', 'test_unknown_session_is_404_before_the_seat_check', ('FR-4310', 'FR-4320')),
]


@pytest.fixture(scope="session")
def records(request):
    return request.config._verifies_records


def _ids_by_test(records):
    out: dict[tuple[str, str], set[str]] = {}
    for rec in records:
        out.setdefault((rec.module, rec.func), set()).update(rec.ids)
    return out


def _whole_suite(records):
    return {r.module for r in records} >= {p.name for p in bi.TESTS_DIR.glob("test_*.py")}


@pytest.mark.parametrize("module,func,expected", EXPECTED, ids=[f"{m}::{f}" for m, f, _ in EXPECTED])
def test_each_listed_retag_is_in_place(records, module, func, expected):
    got = _ids_by_test(records)
    if not any(m == module for m, _ in got):
        pytest.skip(f"{module} not collected in this run")
    assert (module, func) in got, f"{module}::{func} no longer exists (renamed or removed?)"
    assert got[(module, func)] == set(expected), (
        f"{module}::{func} declares {sorted(got[(module, func)])}, expected {sorted(expected)}")


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


def test_collected_count_unchanged_by_the_retag(records):
    if not _whole_suite(records):
        pytest.skip("partial run: the count is only meaningful over the whole suite")
    n = sum(1 for r in records if r.module != "test_origin_retag.py")
    assert COLLECTED_BEFORE <= n <= COLLECTED_UPPER, n
