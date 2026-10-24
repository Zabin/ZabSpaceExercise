"""IP-1330 (FS-133; NFR-2820, NFR-3840, NFR-2830, NFR-2850) — the test-origin ledger reader, the
origin checks and the traceability-matrix Test-column generator, as plain functions.

Reads the four baseline ledgers (never writes them, except ``regenerate_matrix``'s caller writing
the matrix) and works on records the suite's ``conftest.py`` collects once. Kept apart from any
``test_`` module so the checks can be exercised on synthetic inputs and reused by later
documentation-integrity checks (FS-135).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FR_LEDGER = REPO / "docs" / "requirements" / "01-functional-requirements.md"
NFR_LEDGER = REPO / "docs" / "requirements" / "02-non-functional-requirements.md"
FS_LEDGER = REPO / "docs" / "features" / "feature-index.md"
IP_LEDGER = REPO / "docs" / "implementation" / "packages" / "INDEX.md"
MATRIX = REPO / "docs" / "requirements" / "03-requirements-traceability-matrix.md"
ALLOWLIST = Path(__file__).resolve().parent / "test_origin_allowlist.txt"
TESTS_DIR = Path(__file__).resolve().parent

# One shared FR identifier pattern (four- or five-digit leaves, e.g. FR-5310, FR-10110) so the
# well-formed check, the ledger reader and the matrix generator cannot drift apart (IP-1335).
FR_ID = r"FR-\d{4,5}"
WELL_FORMED = re.compile(rf"^(?:{FR_ID}|NFR-\d{{4}}|FS-\d{{3,4}}|IP-\d{{4}})$")
CANDIDATE = re.compile(r"^(?:CR|CNFR)-\d+$")
UNASSIGNED = "UNASSIGNED"


class LedgerError(RuntimeError):
    """A baseline ledger yielded no IDs (renamed, moved or reformatted) — fail loudly (FS-133)."""


@dataclass(frozen=True)
class OriginRecord:
    """One collected test: where it lives and the IDs its ``verifies`` markers declare."""
    nodeid: str          # e.g. spacesim/tests/test_x.py::test_a[param]
    module: str          # e.g. test_x.py
    func: str            # e.g. test_a  (no parametrization suffix)
    ids: tuple[str, ...]


# -- baseline ----------------------------------------------------------------------------------
def _before_candidates(text: str) -> str:
    return text.split("## Candidate Requirements", 1)[0]


def _need(ids: set[str], ledger: Path, what: str) -> set[str]:
    if not ids:
        raise LedgerError(f"baseline ledger {ledger.name if not ledger.is_relative_to(REPO) else ledger.relative_to(REPO)} yielded no {what} IDs")
    return ids


def load_baseline() -> dict[str, set[str]]:
    fr = _need(set(re.findall(rf"^#### ({FR_ID})\b", _before_candidates(FR_LEDGER.read_text("utf-8")), re.M)),
               FR_LEDGER, "FR")
    nfr = _need(set(re.findall(r"^- \*\*(NFR-\d{4})\b", _before_candidates(NFR_LEDGER.read_text("utf-8")), re.M)),
                NFR_LEDGER, "NFR")
    fs = _need(set(re.findall(r"^\| \[(FS-\d{3,4})\]", FS_LEDGER.read_text("utf-8"), re.M)), FS_LEDGER, "FS")
    ip = _need(set(re.findall(r"^\| \[(IP-\d{4})\]", IP_LEDGER.read_text("utf-8"), re.M)), IP_LEDGER, "IP")
    return {"FR": fr, "NFR": nfr, "FS": fs, "IP": ip}


def resolve_problem(req_id: str, baseline: dict[str, set[str]]) -> str | None:
    """Why ``req_id`` is not a live baseline item, or ``None`` when it is. (Retirement is not yet
    defined — BL-0317 — so this tests existence and non-candidate status only.)"""
    if CANDIDATE.match(req_id):
        return "a Candidate Requirement is not a baseline item"
    if not WELL_FORMED.match(req_id):
        return "malformed ID (expected FR-nnnn or FR-nnnnn, NFR-nnnn, FS-nnn or IP-nnnn)"
    kind = req_id.split("-", 1)[0]
    if req_id not in baseline[kind]:
        return "not in the baseline ledger (unknown, or retired — retirement is not yet marked, BL-0317)"
    return None


# -- allow-list --------------------------------------------------------------------------------
def read_allowlist(path: Path = ALLOWLIST) -> set[str]:
    return {ln.strip() for ln in path.read_text("utf-8").splitlines() if ln.strip() and not ln.startswith("#")}


# -- the checks (pure: records in, problems out) -----------------------------------------------
def origin_problems(records: list[OriginRecord], baseline: dict[str, set[str]], allowlist: set[str],
                    existing_modules: set[str]) -> list[str]:
    """Every failure of FS-133's mechanical checks, as readable lines."""
    problems: list[str] = []
    by_module: dict[str, list[OriginRecord]] = {}
    for r in records:
        by_module.setdefault(r.module, []).append(r)
    for r in records:
        if not r.ids and r.module not in allowlist:
            problems.append(f"untagged test (no `verifies` origin): {r.nodeid}")
        for i in r.ids:
            why = resolve_problem(i, baseline)
            if why:
                problems.append(f"{r.nodeid}: origin {i!r} — {why}")
    for mod in sorted(allowlist):
        if mod not in existing_modules:
            problems.append(f"allow-list names {mod}, which does not exist")
        elif mod in by_module and all(r.ids for r in by_module[mod]):
            problems.append(f"allow-list is stale: {mod} is fully tagged — remove it (the list only shrinks)")
    return problems


# -- origin report -----------------------------------------------------------------------------
def tests_by_requirement(records: list[OriginRecord]) -> dict[str, list[str]]:
    out: dict[str, set[str]] = {}
    for r in records:
        for i in r.ids:
            out.setdefault(i, set()).add(f"{r.nodeid.split('::', 1)[0]}::{r.func}")
    return {k: sorted(v) for k, v in out.items()}


def report_lines(records: list[OriginRecord], baseline: dict[str, set[str]],
                 only: set[str] | None = None) -> list[str]:
    """The read-only listing: tests by declared ID, then baseline requirements no test names."""
    by_req = tests_by_requirement(records)
    ids = sorted(i for i in by_req if only is None or i in only)
    lines = ["== tests by declared origin =="]
    for i in ids:
        lines.append(f"{i}: " + ", ".join(by_req[i]))
    scope = sorted(i for kind in ("FR", "NFR") for i in baseline[kind] if only is None or i in only)
    lines.append("== requirements no test names ==")
    lines.extend(i for i in scope if i not in by_req)
    untagged = sorted(r.nodeid for r in records if not r.ids)
    lines.append(f"== untagged tests: {len(untagged)} ==")
    return lines


# -- generated RTM Test column (NFR-2850) ------------------------------------------------------
def _split_row(line: str) -> list[str]:
    """Split a markdown table row on ``|`` outside backtick spans; the leading/trailing empty
    pieces are kept so ``'|'.join`` reproduces the line byte-for-byte."""
    parts, cur, in_code = [], [], False
    for ch in line:
        if ch == "`":
            in_code = not in_code
        if ch == "|" and not in_code:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return parts


def cell_for(req_id: str, by_req: dict[str, list[str]]) -> str:
    tests = by_req.get(req_id)
    return " " + (", ".join(f"`{t}`" for t in tests) if tests else UNASSIGNED) + " "


def regenerate_matrix(text: str, records: list[OriginRecord], baseline: dict[str, set[str]]
                      ) -> tuple[str, list[str]]:
    """Rewrite only the ``Test`` cell of every baseline-requirement row, in every matrix table that
    has a ``Test`` column. Everything else (other columns, candidate rows, prose) stays
    byte-identical. Returns the new text and the rows it could not place (an ID that looks like a
    requirement but is not a baseline leaf)."""
    by_req = tests_by_requirement(records)
    leaves = baseline["FR"] | baseline["NFR"]
    out, problems = [], []
    test_col: int | None = None
    for line in text.split("\n"):
        if not line.startswith("|"):
            test_col = None
            out.append(line)
            continue
        cells = _split_row(line)
        names = [c.strip() for c in cells]
        if "Test" in names and test_col is None and not re.match(r"^\s*\|[-| :]+\|\s*$", line):
            test_col = names.index("Test")      # a header row
            out.append(line)
            continue
        if test_col is None or re.match(r"^\s*\|[-| :]+\|\s*$", line):
            out.append(line)
            continue
        m = re.match(rf"^((?:{FR_ID}|NFR-\d{{4}}))\b", names[1] if len(names) > 1 else "")
        if m and test_col < len(cells) - 1:
            if m.group(1) in leaves:
                cells[test_col] = cell_for(m.group(1), by_req)
            else:
                problems.append(f"matrix row {m.group(1)} is not a baseline leaf")
        out.append("|".join(cells))
    return "\n".join(out), problems


def matrix_diff_rows(committed: str, generated: str) -> list[str]:
    """Names of the matrix rows whose Test cell differs between two texts."""
    rows = []
    for a, b in zip(committed.split("\n"), generated.split("\n")):
        if a != b:
            cells = [c.strip() for c in _split_row(a)]
            rows.append(cells[1] if len(cells) > 1 else a[:40])
    if len(committed.split("\n")) != len(generated.split("\n")):
        rows.append("(line count differs)")
    return rows
