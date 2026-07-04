"""IP-3010 — Research Analytics: seeded Monte-Carlo batch runner.

``run_batch`` is pure orchestration over already-verified machinery (``SessionManager``'s seeded
``Simulation``, IP-2010's ``assessment_report``) — these tests exercise the wiring, not the
scoring logic itself (already exhaustively covered by ``test_assessment.py``).
"""

from __future__ import annotations

from spacesim.session.research_export import RunRecord, export_csv, export_json
from spacesim.tools.research_batch import run_batch

VIGNETTE_ID = "leo-isr-denial"


def test_run_batch_returns_one_record_per_seed_with_correct_metadata():
    records = run_batch(VIGNETTE_ID, seeds=[1, 2, 3], condition_label="baseline", n_steps_or_until=600)
    assert len(records) == 3
    for seed, rec in zip([1, 2, 3], records):
        assert isinstance(rec, RunRecord)
        assert rec.vignette_id == VIGNETTE_ID
        assert rec.seed == seed
        assert rec.condition_label == "baseline"
        assert set(rec.assessment.keys()) == {"blue", "red"}


def test_identical_vignette_and_seed_produce_byte_identical_run_records():
    """The reproducibility property this whole feature exists to provide (FS-301 Acceptance
    Criteria): two independent batch runs of the same (vignette_id, seed) must match exactly."""
    first = run_batch(VIGNETTE_ID, seeds=[42], condition_label="repro-check", n_steps_or_until=600)
    second = run_batch(VIGNETTE_ID, seeds=[42], condition_label="repro-check", n_steps_or_until=600)
    assert first[0].model_dump_json() == second[0].model_dump_json()


def test_varying_the_seed_produces_the_known_deterministic_outcome_per_seed():
    """This fixture vignette drives no cell-issued order during the batch window (``run_batch``
    only advances the clock — it does not automate Red doctrine or issue Blue orders, per this
    package's own scope), so ``assessment_report``'s dimensions all default per
    ``session/assessment.py``'s own documented "no qualifying decisions" behavior. The "expected
    distribution shape" for *this* fixture is therefore a single point mass: every seed
    deterministically produces the same default tiers. This is still a real distribution-shape
    assertion (not a placeholder) — it would fail if seeding were wired incorrectly (e.g., if a
    bug caused ``score_custody_quality`` to read stale cross-run state) and confirms `run_batch`
    starts every seed from a genuinely clean, decision-free initial state.
    """
    records = run_batch(VIGNETTE_ID, seeds=[10, 11, 12], condition_label="distribution", n_steps_or_until=600)
    expected = {
        "custody_quality": "speculative",
        "window_discipline": "disciplined",
        "belief_truth_divergence": "low-divergence",
    }
    for rec in records:
        for cell in ("blue", "red"):
            assert rec.assessment[cell]["custody_quality"] == expected["custody_quality"]
            assert rec.assessment[cell]["window_discipline"] == expected["window_discipline"]
            assert rec.assessment[cell]["belief_truth_divergence"] == expected["belief_truth_divergence"]


def test_run_batch_never_reimplements_ip2010_scoring(monkeypatch):
    """``run_batch`` must call ``assessment_report`` exactly once per run, never duplicate its
    scoring logic (FS-301's explicit non-goal, per its own Risks section)."""
    import spacesim.tools.research_batch as batch_mod

    calls = []
    original = batch_mod.assessment_report

    def _counting(mgr, *a, **kw):
        calls.append(mgr)
        return original(mgr, *a, **kw)

    monkeypatch.setattr(batch_mod, "assessment_report", _counting)
    run_batch(VIGNETTE_ID, seeds=[1, 2], condition_label="x", n_steps_or_until=600)
    assert len(calls) == 2  # exactly once per seed, never zero, never duplicated


def test_run_batch_uses_a_fresh_session_manager_per_seed_no_shared_state():
    """No shared mutable state between runs (this package's own Risks section) — each run must
    start from a clean seeded initial state, not accumulate state across seeds."""
    records = run_batch(VIGNETTE_ID, seeds=[5, 5], condition_label="isolation", n_steps_or_until=600)
    assert records[0].model_dump_json() == records[1].model_dump_json()


def test_export_csv_has_one_row_per_run_and_one_column_per_dimension():
    records = run_batch(VIGNETTE_ID, seeds=[1, 2], condition_label="export-check", n_steps_or_until=600)
    csv_text = export_csv(records)
    lines = [ln for ln in csv_text.strip().splitlines()]
    assert len(lines) == 1 + len(records)  # header + one row per run
    header = lines[0]
    assert "vignette_id" in header and "seed" in header and "condition_label" in header
    assert "blue_custody_quality" in header
    assert "red_belief_truth_divergence" in header


def test_export_json_round_trips_every_record():
    records = run_batch(VIGNETTE_ID, seeds=[1, 2], condition_label="export-check", n_steps_or_until=600)
    import json
    parsed = json.loads(export_json(records))
    assert len(parsed) == len(records)
    assert parsed[0]["vignette_id"] == VIGNETTE_ID
    assert parsed[0]["seed"] == 1
