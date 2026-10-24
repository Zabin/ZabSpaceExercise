"""IP-1330 (FS-133) — every test declares a resolvable origin, the origin report works, and the
traceability matrix's Test column equals the generated one.

Criteria on synthetic inputs run through ``baseline_ids``'s pure functions; the "real suite" checks
read the records ``conftest.py`` collected in this run.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import baseline_ids as bi

pytestmark = pytest.mark.verifies("NFR-2820")

BASELINE = {"FR": {"FR-1110", "FR-1120"}, "NFR": {"NFR-1500"}, "FS": {"FS-101"}, "IP": {"IP-1330"}}


def R(module, func, *ids):
    return bi.OriginRecord(nodeid=f"spacesim/tests/{module}::{func}", module=module, func=func, ids=tuple(ids))


@pytest.fixture(scope="session")
def records(request):
    return request.config._verifies_records


def _modules_on_disk():
    return {p.name for p in bi.TESTS_DIR.glob("test_*.py")}


def _whole_suite(records):
    return {r.module for r in records} >= _modules_on_disk()


# -- real suite ---------------------------------------------------------------------------------
def test_every_collected_test_outside_the_allowlist_declares_an_origin(records):
    problems = [p for p in bi.origin_problems(records, bi.load_baseline(), bi.read_allowlist(),
                                              _modules_on_disk()) if p.startswith("untagged")]
    assert not problems, "\n".join(problems)


@pytest.mark.verifies("NFR-2820")
def test_allowlist_only_shrinks(records):
    problems = [p for p in bi.origin_problems(records, bi.load_baseline(), bi.read_allowlist(),
                                              _modules_on_disk()) if p.startswith("allow-list")]
    assert not problems, "\n".join(problems)


@pytest.mark.verifies("NFR-3840")
def test_every_declared_id_in_the_real_suite_resolves(records):
    problems = [p for p in bi.origin_problems(records, bi.load_baseline(), bi.read_allowlist(),
                                              _modules_on_disk()) if "origin '" in p]
    assert not problems, "\n".join(problems) + "\n(retirement is not yet marked — BL-0317)"


# -- synthetic: NFR-2820 -------------------------------------------------------------------------
def test_untagged_synthetic_test_outside_the_allowlist_is_reported_by_name():
    recs = [R("test_a.py", "test_tagged", "FR-1110"), R("test_a.py", "test_bare")]
    out = bi.origin_problems(recs, BASELINE, set(), {"test_a.py"})
    assert len(out) == 1 and "test_a.py::test_bare" in out[0]


def test_untagged_test_in_an_allowlisted_module_is_tolerated_but_a_fully_tagged_one_is_stale():
    assert bi.origin_problems([R("test_a.py", "t")], BASELINE, {"test_a.py"}, {"test_a.py"}) == []
    stale = bi.origin_problems([R("test_a.py", "t", "FR-1110")], BASELINE, {"test_a.py"}, {"test_a.py"})
    assert len(stale) == 1 and "stale" in stale[0]
    missing = bi.origin_problems([], BASELINE, {"gone.py"}, {"test_a.py"})
    assert len(missing) == 1 and "gone.py" in missing[0]


# -- synthetic: NFR-3840 -------------------------------------------------------------------------
@pytest.mark.verifies("NFR-3840")
@pytest.mark.parametrize("bad", ["FR-9999", "FR-12", "CR-01", "CNFR-02", "REQ-1"])
def test_unknown_malformed_and_candidate_ids_are_reported_with_test_and_id(bad):
    out = bi.origin_problems([R("test_a.py", "test_x", bad)], BASELINE, set(), {"test_a.py"})
    assert len(out) == 1 and "test_a.py::test_x" in out[0] and bad in out[0]


@pytest.mark.verifies("NFR-3840")
@pytest.mark.parametrize("good", ["FR-1110", "NFR-1500", "FS-101", "IP-1330"])
def test_real_shaped_ids_resolve(good):
    assert bi.origin_problems([R("test_a.py", "t", good)], BASELINE, set(), {"test_a.py"}) == []


@pytest.mark.verifies("NFR-3840")
def test_the_live_baseline_resolves_one_of_each_kind():
    base = bi.load_baseline()
    for kind in ("FR", "NFR", "FS", "IP"):
        assert base[kind], kind
        assert bi.resolve_problem(sorted(base[kind])[0], base) is None


@pytest.mark.verifies("NFR-3840")
def test_a_ledger_yielding_no_ids_fails_loudly(tmp_path, monkeypatch):
    empty = tmp_path / "01-functional-requirements.md"
    empty.write_text("# nothing here\n", encoding="utf-8")
    monkeypatch.setattr(bi, "FR_LEDGER", empty)
    with pytest.raises(bi.LedgerError) as exc:
        bi.load_baseline()
    assert "functional-requirements" in str(exc.value) or "FR" in str(exc.value)


# -- NFR-2830: the report ------------------------------------------------------------------------
@pytest.mark.verifies("NFR-2830")
def test_report_lists_tests_for_an_id_and_requirements_no_test_names_and_writes_nothing():
    recs = [R("test_a.py", "test_one", "FR-1110"), R("test_a.py", "test_two", "FR-1110", "NFR-1500"),
            R("test_a.py", "test_bare")]
    before = bi.MATRIX.read_text("utf-8")
    lines = bi.report_lines(recs, BASELINE)
    assert any(l.startswith("FR-1110:") and "test_one" in l and "test_two" in l for l in lines)
    assert "FR-1120" in lines[lines.index("== requirements no test names ==") + 1:]
    assert bi.report_lines(recs, BASELINE, only={"NFR-1500"})[1].startswith("NFR-1500:")
    assert bi.MATRIX.read_text("utf-8") == before


@pytest.mark.verifies("NFR-2830")
def test_the_report_command_names_the_determinism_gate_under_nfr_1500():
    root = Path(bi.REPO)
    done = subprocess.run([sys.executable, "-m", "pytest", "--origin-report", "--origin-ids=NFR-1500",
                           "-p", "no:cacheprovider"], cwd=root, capture_output=True, text=True)
    assert done.returncode in (0, 5), done.stdout + done.stderr
    assert "NFR-1500:" in done.stdout and "test_determinism.py" in done.stdout


# -- NFR-2820: strict markers --------------------------------------------------------------------
def test_a_misspelt_marker_fails_collection_under_strict_markers(tmp_path):
    t = tmp_path / "test_typo.py"
    t.write_text("import pytest\n\n@pytest.mark.verfies('FR-1110')\ndef test_x():\n    pass\n", encoding="utf-8")
    done = subprocess.run([sys.executable, "-m", "pytest", "-c", str(bi.REPO / "pyproject.toml"),
                           f"--rootdir={tmp_path}", "-p", "no:cacheprovider", str(t)],
                          capture_output=True, text=True)
    assert done.returncode != 0
    assert "verfies" in done.stdout + done.stderr


# -- NFR-2850: the generated Test column ---------------------------------------------------------
MATRIX_SNIPPET = """\
# Matrix

| Req ID | Title | Test | Impl. Package |
|---|---|---|---|
| FR-1110 | Clock | UNASSIGNED | `engine/clock.py` |
| FR-1120 | Determinism | `hand-edited.py` | UNASSIGNED |
| CR-01 | A candidate | `keep-me.py` | UNASSIGNED |

prose line with | pipes | that must stay
"""


@pytest.mark.verifies("NFR-2850")
def test_regeneration_changes_only_test_cells_and_is_idempotent():
    recs = [R("test_a.py", "test_one", "FR-1110"), R("test_a.py", "test_two", "FR-1110", "FS-101")]
    new, problems = bi.regenerate_matrix(MATRIX_SNIPPET, recs, BASELINE)
    assert problems == []
    old_l, new_l = MATRIX_SNIPPET.split("\n"), new.split("\n")
    changed = [i for i, (a, b) in enumerate(zip(old_l, new_l)) if a != b]
    assert len(changed) == 2                      # FR-1110 gains tests, FR-1120's hand edit goes
    assert "`spacesim/tests/test_a.py::test_one`" in new_l[changed[0]]
    assert "| UNASSIGNED |" in new_l[changed[1]] and "hand-edited" not in new
    assert "`engine/clock.py`" in new_l[changed[0]] and "`keep-me.py`" in new   # other columns/candidates intact
    assert "prose line with | pipes | that must stay" in new
    assert bi.regenerate_matrix(new, recs, BASELINE)[0] == new


@pytest.mark.verifies("NFR-2850")
def test_a_hand_edited_cell_is_reported_by_row_and_an_unknown_row_id_is_reported():
    gen, _ = bi.regenerate_matrix(MATRIX_SNIPPET, [], BASELINE)
    assert bi.matrix_diff_rows(MATRIX_SNIPPET, gen) == ["FR-1120"]
    bad = MATRIX_SNIPPET.replace("| CR-01 |", "| FR-7777 |")
    _, problems = bi.regenerate_matrix(bad, [], BASELINE)
    assert problems == ["matrix row FR-7777 is not a baseline leaf"]


@pytest.mark.verifies("NFR-2850")
def test_the_committed_matrix_test_column_equals_the_generated_one(records):
    if not _whole_suite(records):
        pytest.skip("partial collection: the generated column needs the whole suite's origins")
    committed = bi.MATRIX.read_text("utf-8")
    generated, problems = bi.regenerate_matrix(committed, records, bi.load_baseline())
    assert not problems, "\n".join(problems)
    diff = bi.matrix_diff_rows(committed, generated)
    assert not diff, ("traceability matrix Test column is stale for: " + ", ".join(diff)
                      + " — regenerate with `python3 -m pytest --origin-report=rtm`")
