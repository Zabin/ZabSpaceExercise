"""IP-1330 (FS-133) — test-origin recorder and report option.

Records, once and during the collection pytest already does, each collected test's declared
``verifies`` origin IDs (``config._verifies_records``) for ``test_test_origins.py``. Also registers
``--origin-report[=list|rtm]`` (+ ``--origin-ids``): a command that prints the origin report, or
(``rtm``) rewrites only the Test cells of the traceability matrix, and runs no tests.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import baseline_ids as bi  # noqa: E402


def pytest_addoption(parser):
    g = parser.getgroup("origins", "test-origin traceability (FS-133)")
    g.addoption("--origin-report", nargs="?", const="list", default=None, choices=("list", "rtm"),
                help="print the test-origin report ('list', default) or regenerate the traceability "
                     "matrix's Test column ('rtm'); runs no tests")
    g.addoption("--origin-ids", default=None,
                help="comma-separated requirement IDs to limit the 'list' report to (a release's scope)")


def _ids_of(item) -> tuple[str, ...]:
    ids: list[str] = []
    for mark in item.iter_markers("verifies"):
        ids.extend(a for a in mark.args if isinstance(a, str))
    return tuple(dict.fromkeys(ids))


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config, items):
    records = []
    for it in items:
        path, _, rest = it.nodeid.partition("::")
        func = rest.split("[", 1)[0].split("::")[-1]
        records.append(bi.OriginRecord(nodeid=it.nodeid, module=Path(path).name, func=func, ids=_ids_of(it)))
    config._verifies_records = records
    mode = config.getoption("--origin-report")
    if not mode:
        return
    tr = config.pluginmanager.get_plugin("terminalreporter")
    write = tr.write_line if tr else print
    baseline = bi.load_baseline()
    if mode == "list":
        only = config.getoption("--origin-ids")
        for ln in bi.report_lines(records, baseline, set(only.split(",")) if only else None):
            write(ln)
    else:
        old = bi.MATRIX.read_text("utf-8")
        new, problems = bi.regenerate_matrix(old, records, baseline)
        for p in problems:
            write(p)
        if new != old:
            bi.MATRIX.write_text(new, encoding="utf-8")
        write(f"traceability matrix Test column regenerated ({'changed' if new != old else 'unchanged'})")
    items[:] = []   # report mode runs no tests
