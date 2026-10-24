"""IP-1335 (FS-133; NFR-2820, NFR-2850) — five-digit ``FR-`` identifiers can be declared as a test
origin, the baseline reader and RTM generator see them, and the assessment/research tests carry
their leaves (``FR-10110`` / ``FR-10210``).
"""

from __future__ import annotations

import ast
import re

import pytest

import baseline_ids as bi

pytestmark = pytest.mark.verifies("NFR-2820", "NFR-2850")

@pytest.fixture(scope="module")
def baseline():
    return bi.load_baseline()


def R(module, func, *ids):
    return bi.OriginRecord(nodeid=f"spacesim/tests/{module}::{func}", module=module, func=func, ids=tuple(ids))


def test_five_digit_ids_are_well_formed_and_resolve(baseline):
    for i in ("FR-10110", "FR-10210", "FR-11420"):
        assert bi.resolve_problem(i, baseline) is None, i


@pytest.mark.parametrize("bad", ["FR-123456", "FR-12", "FR-1011", "NFR-10110"])
def test_malformed_or_unknown_ids_still_rejected(baseline, bad):
    assert bi.resolve_problem(bad, baseline) is not None


def test_baseline_reads_five_digit_headings(baseline):
    fr = baseline["FR"]
    assert {"FR-10110", "FR-10210"} <= fr
    headings = set(re.findall(r"^#### (FR-11\d{3})\b", bi.FR_LEDGER.read_text("utf-8"), re.M))
    assert len(headings) == 7 and headings <= fr
    assert "FR-1110" in fr and "FR-5310" in fr


def test_matrix_generation_places_a_five_digit_row(baseline):
    text = bi.MATRIX.read_text("utf-8")
    recs = [R("test_assessment.py", "test_a", "FR-10110")]
    new, problems = bi.regenerate_matrix(text, recs, baseline)
    assert not problems
    row = next(ln for ln in new.split("\n") if ln.startswith("| FR-10110"))
    assert "`spacesim/tests/test_assessment.py::test_a`" in row


def _declared(path, ids_expected_for):
    tree = ast.parse(path.read_text("utf-8"))
    out = {}
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
            ids = []
            for d in node.decorator_list:
                if (isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute) and d.func.attr == "verifies"):
                    ids += [a.value for a in d.args if isinstance(a, ast.Constant)]
            out[node.name] = ids
    return out


@pytest.mark.parametrize("module,leaf,old,count", [
    ("test_assessment.py", "FR-10110", "FS-201", 13),
    ("test_research_batch.py", "FR-10210", "FS-301", 7),
])
def test_retags_in_place_and_count_unchanged(module, leaf, old, count):
    declared = _declared(bi.TESTS_DIR / module, None)
    assert len(declared) == count
    for name, ids in declared.items():
        assert leaf in ids and old not in ids, name
