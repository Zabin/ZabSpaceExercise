"""IP-1350 (FS-135; NFR-3800, NFR-3820, NFR-3830) — documentation-integrity checks that run with
the full suite: relative links resolve, each INDEX.md lists its folder's documents, and the
status ledgers agree. Check 2 (NFR-3810, retired documents; IP-1092) reads the `Retired documents` section of every
INDEX.md.

Each check is a pure function of a repository root, so the synthetic-tree tests seed one defect in
a temporary tree. The real tree runs against a committed shrink-only allow-list (one text file per
check beside this module, one defect per line, each naming its owning stage): a defect not listed
fails; a listed defect that no longer occurs fails too, so the lists can only shrink.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from urllib.parse import unquote

import pytest

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".pytest_cache"}
# FS-135 Decision 1 — frozen history, never checked.
FROZEN_PREFIXES = (
    "docs/implementation/verification/", "docs/reviews/", "docs/architecture/adr/",
    "docs/pipeline/backlog-archive.md", "docs/pipeline/pipeline-journal-archive.md",
)
JOURNAL = "docs/pipeline/pipeline-journal.md"


# -- the live set ------------------------------------------------------------------------------
def _rel(root: Path, p: Path) -> str:
    return p.relative_to(root).as_posix()


def live_md_files(root: Path) -> list[Path]:
    out = []
    for p in sorted(root.rglob("*.md")):
        if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
            continue
        if _rel(root, p).startswith(FROZEN_PREFIXES):
            continue
        out.append(p)
    return out


def live_text(root: Path, p: Path) -> str:
    text = p.read_text(encoding="utf-8", errors="replace")
    if _rel(root, p) == JOURNAL:                 # the Position block is live; the run log is frozen
        text = text.split("## Run log", 1)[0]
    return text


FENCE = re.compile(r"^\s*(```|~~~)")
CODE_SPAN = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")


def _prose_lines(text: str):
    """(line number, line) for non-fenced lines, inline code spans blanked."""
    in_fence = False
    for n, line in enumerate(text.split("\n"), 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            yield n, CODE_SPAN.sub("", line)


# -- check 1: links resolve (NFR-3800) ---------------------------------------------------------
def broken_links(root: Path) -> list[tuple[str, int, str]]:
    out = []
    for f in live_md_files(root):
        for n, line in _prose_lines(live_text(root, f)):
            for m in LINK.finditer(line):
                target = m.group(1)
                if target.startswith("#") or re.match(r"^[A-Za-z][A-Za-z0-9+.\-]*:", target):
                    continue
                if target.startswith("/"):
                    out.append((_rel(root, f), n, target))     # absolute path: a defect, not resolved
                    continue
                path = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if path and not (f.parent / path).exists():
                    out.append((_rel(root, f), n, target))
    return out


def link_keys(root: Path) -> set[str]:
    return {f"{rel} -> {t}" for rel, _, t in broken_links(root)}


# -- check 2: retired documents are deleted, declared, and named by no live document (NFR-3810) -
RETIRED_HEADING = re.compile(r"^##\s+Retired documents\s*$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TABLE_SEP = re.compile(r"^\|[\s:|\-]+\|\s*$")


def _section_bounds(lines: list[str]) -> list[tuple[int, int]]:
    """(first, last) 1-based line numbers of every `## Retired documents` section, heading included,
    ending before the next heading of level 1 or 2."""
    out = []
    for i, line in enumerate(lines):
        if RETIRED_HEADING.match(line):
            end = len(lines)
            for j in range(i + 1, len(lines)):
                if re.match(r"^#{1,2}\s", lines[j]):
                    end = j
                    break
            out.append((i + 1, end))
    return out


def _unquote_cell(cell: str) -> str:
    return cell.replace("`", "").strip()


def retired_declarations(root: Path):
    """-> (rows, problems, exempt). rows: dicts {index, line, path, id, date, successor}; problems:
    (mode, index, detail) for an unreadable section ('unreadable'); exempt: {index: {line numbers}} —
    the declaring sections, the only lines the reference scan skips."""
    rows, problems, exempt = [], [], {}
    for f in live_md_files(root):
        if f.name != "INDEX.md":
            continue
        rel = _rel(root, f)
        lines = live_text(root, f).split("\n")
        for first, last in _section_bounds(lines):
            exempt.setdefault(rel, set()).update(range(first, last + 1))
            body = [(n, lines[n - 1]) for n in range(first + 1, last + 1) if lines[n - 1].strip()]
            table = [(n, ln) for n, ln in body if ln.lstrip().startswith("|")]
            if not table:
                if body and all(ln.strip().rstrip(".").lower() == "none" for _, ln in body):
                    continue                                  # `none` body: zero rows
                problems.append(("unreadable", rel, f"line {first}: no table under the heading"))
                continue
            if len(table) < 2 or not TABLE_SEP.match(table[1][1].strip()) or len(_cells(table[0][1])) != 4:
                problems.append(("unreadable", rel, f"line {first}: need a 4-column header row and separator"))
                continue
            for n, ln in table[2:]:
                c = _cells(ln)
                if len(c) != 4:
                    problems.append(("unreadable", rel, f"line {n}: row has {len(c)} columns, not 4"))
                    continue
                rows.append({"index": rel, "line": n, "path": _unquote_cell(c[0]), "id": _unquote_cell(c[1]),
                             "date": _unquote_cell(c[2]), "successor": _unquote_cell(c[3])})
    return rows, problems, exempt


def _date_ok(s: str) -> bool:
    if not ISO_DATE.match(s):
        return False
    try:
        date.fromisoformat(s)
    except ValueError:
        return False
    return True


def _entry_regex(entry: str, is_id: bool) -> re.Pattern:
    if is_id:
        return re.compile(r"(?<![\w-])" + re.escape(entry) + r"(?![\w-])")
    base = entry.rstrip("/")
    return re.compile(r"(?<![\w.\-])" + re.escape(base) + r"(?!\w|-|\.\w)")


def retired_findings(root: Path) -> set[tuple[str, str, str]]:
    """(mode, where, detail): 'a' declared path still present; 'b' live reference outside the
    declaring section; 'c' incomplete row; 'unreadable' section table. Unlike check 1, fenced code and
    code spans are scanned — a command naming a retired path is still a live mention."""
    rows, problems, exempt = retired_declarations(root)
    out = set(problems)
    entries = []                                            # (regex, text, declaring index)
    for r in rows:
        where, tag = r["index"], f"line {r['line']}"
        if not r["path"]:
            out.add(("c", where, f"{tag}: no former path"))
            continue
        if not _date_ok(r["date"]):
            out.add(("c", where, f"{tag}: {r['path']}: missing or non-ISO retirement date"))
        succ = r["successor"]
        if not succ:
            out.add(("c", where, f"{tag}: {r['path']}: no successor (write `none` if there is none)"))
        elif succ.lower() != "none" and not ((root / succ).exists() or ((root / where).parent / succ).exists()):
            out.add(("c", where, f"{tag}: {r['path']}: successor {succ} does not exist"))
        if (root / r["path"].rstrip("/")).exists():
            out.add(("a", where, f"{tag}: {r['path']} is declared retired but still present"))
        entries.append((_entry_regex(r["path"], False), r["path"], where))
        if r["id"]:
            entries.append((_entry_regex(r["id"], True), r["id"], where))
    if not entries:
        return out
    for f in live_md_files(root):
        rel = _rel(root, f)
        skip = exempt.get(rel, set())
        for n, line in enumerate(live_text(root, f).split("\n"), 1):
            if n in skip:
                continue
            for rx, text, decl in entries:
                for m in rx.finditer(line):
                    if "/" not in text.rstrip("/") and m.start() and line[m.start() - 1] == "/" \
                            and not line[:m.start()].endswith(("../", "./")):
                        continue                              # root name under another folder: a different path
                    out.add(("b", f"{rel}:{n}", f"{text} (declared in {decl})"))
                    break
    return out


def retired_keys(root: Path) -> set[str]:
    """Allow-list keys: failure mode (b) only — (a), (c) and an unreadable table are never allow-listable."""
    keys = set()
    for mode, where, detail in retired_findings(root):
        if mode == "b":
            keys.add(f"{where.rsplit(':', 1)[0]} -> {detail.split(' (declared in ')[0]}")
    return keys


# -- check 3: indexes agree with their folders (NFR-3820) --------------------------------------
BACKTICKED = re.compile(r"`([^`\n]+)`")


def _listed_by(root: Path, index: Path, seen: set[Path] | None = None) -> set[Path]:
    """Resolved paths an index lists — by link or by a backticked path — following linked
    sub-indexes. A backticked path counts when it resolves from the index's folder, from its parent
    folder, or from the repository root; a bare name only from the index's own folder."""
    seen = seen if seen is not None else set()
    seen.add(index.resolve())
    text = live_text(root, index)
    listed: set[Path] = set()
    for n, line in _prose_lines(text):
        for m in LINK.finditer(line):
            t = m.group(1)
            if t.startswith("#") or re.match(r"^[A-Za-z][A-Za-z0-9+.\-]*:", t):
                continue
            listed.add((index.parent / unquote(t.split("#", 1)[0])).resolve())
    for m in BACKTICKED.finditer(text):
        t = m.group(1).strip()
        if t.startswith("/") or " " in t:
            continue
        listed.add((index.parent / t).resolve())
        if "/" in t:
            listed.add((index.parent.parent / t).resolve())
            listed.add((root / t).resolve())
    for sub in list(listed):
        if sub.suffix == ".md" and "index" in sub.name.lower() and sub.exists() and sub not in seen:
            # A sub-index speaks only for documents at or below its own folder.
            listed |= {p for p in _listed_by(root, sub, seen) if sub.parent.resolve() in p.parents}
    return listed


def unlisted_documents(root: Path) -> list[tuple[str, str]]:
    out = []
    for index in live_md_files(root):
        if index.name != "INDEX.md":
            continue
        listed = _listed_by(root, index)
        for doc in sorted(index.parent.glob("*.md")):
            if doc.name != "INDEX.md" and doc.resolve() not in listed:
                out.append((_rel(root, index), doc.name))
    return out


def index_keys(root: Path) -> set[str]:
    return {f"{i} -> {d}" for i, d in unlisted_documents(root)}


# -- check 4: ledgers agree (NFR-3830) ---------------------------------------------------------
PKG_VOCAB = re.compile(r"^(NOT STARTED|READY|IN PROGRESS|BLOCKED|COMPLETE|VERIFIED)\b")


class LedgerEmpty(RuntimeError):
    pass


def _cells(line: str) -> list[str]:
    parts, cur, in_code = [], [], False
    for ch in line:
        if ch == "`":
            in_code = not in_code
        if ch == "|" and not in_code:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur).strip())
    return parts[1:-1] if len(parts) > 2 else parts


def _word(cell: str) -> str:
    return re.sub(r"^[^A-Za-z]+", "", cell).strip("*_ ")


def package_statuses(text: str, name: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in text.split("\n"):
        m = re.match(r"^\| \[(IP-\d{4})\]", line)
        if not m or m.group(1) in out:
            continue
        for c in _cells(line)[1:]:
            v = PKG_VOCAB.match(_word(c))
            if v:
                out[m.group(1)] = v.group(1)
                break
    if not out:
        raise LedgerEmpty(f"{name} yielded no package rows")
    return out


def gds_statuses(text: str, name: str) -> dict[str, str]:
    out = {}
    for line in text.split("\n"):
        m = re.match(r"^\| (GDS-\d{2}) \|", line)
        if m:
            status = _cells(line)[-1]
            out[m.group(1)] = "authored" if re.search(r"Authored", status) and "Planned" not in status else "planned"
    if not out:
        raise LedgerEmpty(f"{name} yielded no GDS rows")
    return out


def _fs_word(s: str) -> str:
    s = _word(s)
    return "done" if s.startswith("Done") else "ready" if s.startswith("Ready") else "candidate"


def fs_statuses(root: Path) -> tuple[dict[str, str], dict[str, str]]:
    index = (root / "docs/features/feature-index.md").read_text(encoding="utf-8")
    idx, hdr = {}, {}
    for line in index.split("\n"):
        m = re.match(r"^\| \[(FS-\d{3,4})\]\(([^)]+)\)", line)
        if not m:
            continue
        cells = _cells(line)
        idx[m.group(1)] = _fs_word(cells[3])
        spec = root / "docs/features" / m.group(2)
        if spec.exists():
            sm = re.search(r"^> \*\*Status:\*\*\s*(.+)$", spec.read_text(encoding="utf-8"), re.M)
            if sm:
                hdr[m.group(1)] = _fs_word(sm.group(1))
    if not idx:
        raise LedgerEmpty("docs/features/feature-index.md yielded no FS rows")
    return idx, hdr


def _compare(pair: str, a: dict[str, str], b: dict[str, str], an: str, bn: str) -> set[str]:
    out = set()
    for item in sorted(set(a) | set(b)):
        if item not in a:
            out.add(f"{pair}: {item} missing from {an}")
        elif item not in b:
            out.add(f"{pair}: {item} missing from {bn}")
        elif a[item] != b[item]:
            out.add(f"{pair}: {item} is {a[item]} in {an} but {b[item]} in {bn}")
    return out


def ledger_disagreements(root: Path) -> set[str]:
    mbp = (root / "docs/implementation/00-master-build-plan.md").read_text(encoding="utf-8")
    pidx = (root / "docs/implementation/packages/INDEX.md").read_text(encoding="utf-8")
    out = _compare("packages", package_statuses(mbp, "Master Build Plan"),
                   package_statuses(pidx, "packages/INDEX.md"), "Master Build Plan", "packages/INDEX.md")
    arch = (root / "docs/architecture/INDEX.md").read_text(encoding="utf-8")
    road = (root / "ROADMAP.md").read_text(encoding="utf-8")
    out |= _compare("gds", gds_statuses(arch, "architecture/INDEX.md"), gds_statuses(road, "ROADMAP.md"),
                    "architecture/INDEX.md", "ROADMAP.md")
    idx, hdr = fs_statuses(root)
    out |= _compare("fs", idx, hdr, "feature-index.md", "the spec header")
    return out


# -- allow-lists -------------------------------------------------------------------------------
def read_allow(name: str) -> set[str]:
    p = HERE / name
    return {ln.split(" | ", 1)[0].strip() for ln in p.read_text("utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")}


def _gate(found: set[str], allow: set[str], what: str) -> None:
    new = sorted(found - allow)
    stale = sorted(allow - found)
    assert not new, f"new {what} defect(s) — fix them or (never) allow-list them:\n  " + "\n  ".join(new)
    assert not stale, (f"allow-listed {what} defect(s) no longer occur — remove them from the list "
                       f"(it only shrinks):\n  " + "\n  ".join(stale))


# -- real tree ---------------------------------------------------------------------------------
@pytest.mark.verifies("NFR-3800")
def test_real_tree_has_no_unlisted_broken_relative_link():
    _gate(link_keys(REPO), read_allow("doc_integrity_allow_links.txt"), "broken-link")


@pytest.mark.verifies("NFR-3820")
def test_real_tree_every_index_lists_its_folders_documents():
    _gate(index_keys(REPO), read_allow("doc_integrity_allow_indexes.txt"), "unlisted-document")


@pytest.mark.verifies("NFR-3830")
def test_real_tree_status_ledgers_agree():
    _gate(ledger_disagreements(REPO), read_allow("doc_integrity_allow_ledgers.txt"), "ledger")


# -- synthetic trees ---------------------------------------------------------------------------
def _w(root: Path, rel: str, text: str) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


@pytest.mark.verifies("NFR-3800")
def test_synthetic_broken_link_reported_with_file_line_target_and_exemptions(tmp_path):
    _w(tmp_path, "docs/a.md", "ok [x](b.md)\nbad [y](missing.md#frag)\n```\n[z](in-fence.md)\n```\n"
                              "`[c](in-span.md)` [abs](/docs/b.md) [web](https://e.com) [anchor](#top)\n")
    _w(tmp_path, "docs/b.md", "x\n")
    _w(tmp_path, "docs/reviews/frozen.md", "[bad](nowhere.md)\n")
    _w(tmp_path, "docs/pipeline/pipeline-journal.md", "[ok](../a.md)\n## Run log\n[bad](old-gone.md)\n")
    found = broken_links(tmp_path)
    assert ("docs/a.md", 2, "missing.md#frag") in found
    assert ("docs/a.md", 6, "/docs/b.md") in found
    assert {r for r, _, _ in found} == {"docs/a.md"}      # fence, span, frozen, run log ignored
    assert len(found) == 2


@pytest.mark.verifies("NFR-3820")
def test_synthetic_unlisted_document_reported_with_index_and_document(tmp_path):
    _w(tmp_path, "docs/INDEX.md", "[a](a.md) and `docs/c.md` and [sub](sub/INDEX.md)\n")
    for n in ("a", "b", "c"):
        _w(tmp_path, f"docs/{n}.md", "x\n")
    _w(tmp_path, "docs/sub/INDEX.md", "[s1](s1.md)\n")
    _w(tmp_path, "docs/sub/s1.md", "x\n")
    _w(tmp_path, "docs/sub/s2.md", "x\n")
    assert unlisted_documents(tmp_path) == [("docs/INDEX.md", "b.md"), ("docs/sub/INDEX.md", "s2.md")]


@pytest.mark.verifies("NFR-3820")
def test_synthetic_sub_index_listing_counts(tmp_path):
    _w(tmp_path, "docs/INDEX.md", "[enc](enc/INDEX.md)\n")
    _w(tmp_path, "docs/enc/INDEX.md", "[r](R1-index.md)\n")
    _w(tmp_path, "docs/enc/R1-index.md", "[t](R101.md)\n")
    _w(tmp_path, "docs/enc/R101.md", "x\n")
    assert unlisted_documents(tmp_path) == []


@pytest.mark.verifies("NFR-3830")
def test_synthetic_ledger_disagreements_name_item_and_both_statuses():
    a = {"IP-1": "READY", "IP-2": "VERIFIED", "IP-3": "BLOCKED"}
    b = {"IP-1": "COMPLETE", "IP-2": "VERIFIED", "IP-4": "READY"}
    out = _compare("packages", a, b, "MBP", "INDEX")
    assert out == {"packages: IP-1 is READY in MBP but COMPLETE in INDEX",
                   "packages: IP-3 missing from INDEX", "packages: IP-4 missing from MBP"}
    assert package_statuses("| [IP-1009](x.md) | t | 🔵 COMPLETE |\n", "x") == {"IP-1009": "COMPLETE"}
    assert gds_statuses("| GDS-00 | V | `p` | ✅ Authored — merge gate closed |\n| GDS-01 | C | `p` | ⛔ Planned |\n",
                        "x") == {"GDS-00": "authored", "GDS-01": "planned"}
    assert _fs_word("✅ Ready for implementation planning (x)") == "ready" and _fs_word("✅ Done") == "done"


@pytest.mark.verifies("NFR-3830")
def test_synthetic_ledger_with_no_rows_fails_loudly():
    with pytest.raises(LedgerEmpty) as exc:
        package_statuses("# nothing\n", "Master Build Plan")
    assert "Master Build Plan" in str(exc.value)
    with pytest.raises(LedgerEmpty):
        gds_statuses("", "ROADMAP.md")


@pytest.mark.verifies("NFR-3800", "NFR-3820", "NFR-3830")
def test_allow_list_gate_is_shrink_only():
    _gate({"a"}, {"a"}, "x")
    with pytest.raises(AssertionError, match="new x"):
        _gate({"a", "b"}, {"a"}, "x")
    with pytest.raises(AssertionError, match="no longer occur"):
        _gate({"a"}, {"a", "b"}, "x")


# -- check 2: retired documents (NFR-3810, IP-1092) — synthetic trees written before the code ----
def _idx(*rows: str, body: str | None = None) -> str:
    head = "| Former path | Former ID | Retired | Successor |\n|---|---|---|---|\n"
    sect = body if body is not None else head + "".join(r + "\n" for r in rows)
    return "# Idx\n\n## Retired documents\n\n" + sect + "\n## Other\n\nbody\n"


def _modes(root: Path) -> set[str]:
    return {m for m, _, _ in retired_findings(root)}


@pytest.mark.verifies("NFR-3810")
def test_retired_no_section_passes_and_none_body_is_zero_rows(tmp_path):
    _w(tmp_path, "docs/INDEX.md", "# Idx\n\n[a](a.md)\n")
    _w(tmp_path, "docs/a.md", "x\n")
    assert retired_findings(tmp_path) == set()
    _w(tmp_path, "docs/INDEX.md", _idx(body="none\n") + "[a](a.md)\n")
    assert retired_findings(tmp_path) == set()
    assert retired_declarations(tmp_path)[0] == []


@pytest.mark.verifies("NFR-3810")
def test_retired_mode_a_declared_path_still_present(tmp_path):
    _w(tmp_path, "docs/INDEX.md", _idx("| `docs/old.md` | DOC-1 | 2026-10-01 | none |"))
    assert retired_findings(tmp_path) == set()
    _w(tmp_path, "docs/old.md", "x\n")
    found = retired_findings(tmp_path)
    assert [(m, w) for m, w, _ in found] == [("a", "docs/INDEX.md")]
    assert "docs/old.md" in next(iter(found))[2]


@pytest.mark.verifies("NFR-3810")
def test_retired_mode_b_live_reference_in_every_form_reported_with_file_line_entry_index(tmp_path):
    _w(tmp_path, "docs/INDEX.md", _idx("| `docs/old.md` | DOC-1 | 2026-10-01 | none |") + "mention DOC-1 here\n")
    _w(tmp_path, "docs/l.md", "[x](old.md)\n")
    _w(tmp_path, "docs/t.md", "see `docs/old.md`\nplain docs/old.md.\n```\ncat docs/old.md\n```\n")
    _w(tmp_path, "docs/sib/INDEX.md", "sibling docs/old.md\n")
    f = {(w, d) for m, w, d in retired_findings(tmp_path) if m == "b"}
    assert ("docs/t.md:1", "docs/old.md (declared in docs/INDEX.md)") in f
    assert ("docs/t.md:2", "docs/old.md (declared in docs/INDEX.md)") in f
    assert ("docs/t.md:4", "docs/old.md (declared in docs/INDEX.md)") in f       # fenced code is scanned
    assert ("docs/sib/INDEX.md:1", "docs/old.md (declared in docs/INDEX.md)") in f
    assert any(w.startswith("docs/INDEX.md:") and d.startswith("DOC-1") for w, d in f)  # rest of declaring index
    assert not any(w.startswith("docs/l.md") for w, _ in f)   # bare relative link is check 1's business


@pytest.mark.verifies("NFR-3810")
def test_retired_declaring_section_and_frozen_history_exempt(tmp_path):
    _w(tmp_path, "docs/INDEX.md", _idx("| `docs/old.md` | DOC-1 | 2026-10-01 | `docs/new.md` |"))
    _w(tmp_path, "docs/new.md", "x\n")
    _w(tmp_path, "docs/reviews/r.md", "docs/old.md DOC-1\n")
    _w(tmp_path, "docs/pipeline/pipeline-journal.md", "pos\n## Run log\ndocs/old.md\n")
    assert retired_findings(tmp_path) == set()


@pytest.mark.verifies("NFR-3810")
def test_retired_id_is_a_whole_token_and_path_a_whole_boundary(tmp_path):
    _w(tmp_path, "docs/INDEX.md", _idx("| `docs/a.md` | FR-1210 | 2026-10-01 | none |"))
    _w(tmp_path, "docs/x.md", "FR-12100 and XFR-1210 and docs/a.md.bak and docs/a.mdx and xdocs/a.md\n")
    assert retired_findings(tmp_path) == set()
    _w(tmp_path, "docs/y.md", "FR-1210, ok\n")
    assert {m for m, _, _ in retired_findings(tmp_path)} == {"b"}


@pytest.mark.verifies("NFR-3810")
def test_retired_folder_row_covers_everything_beneath(tmp_path):
    _w(tmp_path, "docs/INDEX.md", _idx("| `docs/oldf/` |  | 2026-10-01 | none |"))
    _w(tmp_path, "docs/x.md", "see docs/oldf/deep/file.md and docs/oldfolder/z.md\n")
    f = retired_findings(tmp_path)
    assert [(m, w) for m, w, _ in f] == [("b", "docs/x.md:1")]
    (tmp_path / "docs/oldf").mkdir()
    assert "a" in _modes(tmp_path)


@pytest.mark.verifies("NFR-3810")
def test_retired_mode_c_incomplete_rows_each_reported(tmp_path):
    rows = ["| `docs/p1.md` |  |  | none |",                          # no date
            "| `docs/p2.md` |  | 20-10-2026 | none |",              # bad date
            "| `docs/p3.md` |  | 2026-10-01 |  |",                  # no successor
            "|  | X-1 | 2026-10-01 | none |",                       # no path
            "| `docs/p5.md` |  | 2026-10-01 | `docs/missing.md` |"]  # successor absent
    _w(tmp_path, "docs/INDEX.md", _idx(*rows))
    found = retired_findings(tmp_path)
    assert [m for m, _, _ in found] == ["c"] * 5
    assert len({d for _, _, d in found}) == 5
    _w(tmp_path, "docs/INDEX.md", _idx("| `docs/p3.md` |  | 2026-10-01 | none |"))
    assert retired_findings(tmp_path) == set()


@pytest.mark.verifies("NFR-3810")
def test_retired_unreadable_table_fails_naming_the_index(tmp_path):
    _w(tmp_path, "docs/sub/INDEX.md", _idx(body="some prose, no table\n"))
    _w(tmp_path, "docs/INDEX.md", _idx(body="| a | b |\n|---|---|\n| x | y |\n"))
    found = retired_findings(tmp_path)
    assert {(m, w) for m, w, _ in found} == {("unreadable", "docs/sub/INDEX.md"), ("unreadable", "docs/INDEX.md")}


@pytest.mark.verifies("NFR-3810")
def test_retired_root_path_declared_in_docs_index_is_enforced(tmp_path):
    _w(tmp_path, "docs/INDEX.md", _idx("| `ROADMAP.md` |  | 2026-10-01 | none |"))
    _w(tmp_path, "docs/x.md", "see ../ROADMAP.md and docs/ROADMAP.md\n")
    assert [(m, w) for m, w, _ in retired_findings(tmp_path)] == [("b", "docs/x.md:1")]
    _w(tmp_path, "ROADMAP.md", "x\n")
    assert "a" in _modes(tmp_path)


@pytest.mark.verifies("NFR-3810")
def test_retired_allow_list_gates_mode_b_only_and_is_shrink_only(tmp_path):
    _w(tmp_path, "docs/INDEX.md", _idx("| `docs/old.md` | DOC-1 | 2026-10-01 | none |"))
    _w(tmp_path, "docs/x.md", "docs/old.md\n")
    keys = retired_keys(tmp_path)
    assert keys == {"docs/x.md -> docs/old.md"}
    _gate(keys, set(keys), "retired")
    with pytest.raises(AssertionError, match="no longer occur"):
        _gate(set(), set(keys), "retired")
    _w(tmp_path, "docs/old.md", "x\n")                       # mode (a) is not a key: never allow-listable
    assert retired_keys(tmp_path) == keys
    assert "a" in _modes(tmp_path)


@pytest.mark.verifies("NFR-3810")
def test_real_tree_retired_documents_check_is_clean_with_empty_allow_list():
    assert read_allow("doc_integrity_allow_retired.txt") == set()
    hard = [f for f in retired_findings(REPO) if f[0] != "b"]
    assert not hard, f"retired-documents defect(s) (never allow-listable): {hard}"
    _gate(retired_keys(REPO), read_allow("doc_integrity_allow_retired.txt"), "retired")
