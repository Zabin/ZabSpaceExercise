"""IP-1350 (FS-135; NFR-3800, NFR-3820, NFR-3830) — documentation-integrity checks that run with
the full suite: relative links resolve, each INDEX.md lists its folder's documents, and the
status ledgers agree. Check 2 (NFR-3810, retired documents) waits on BL-0319.

Each check is a pure function of a repository root, so the synthetic-tree tests seed one defect in
a temporary tree. The real tree runs against a committed shrink-only allow-list (one text file per
check beside this module, one defect per line, each naming its owning stage): a defect not listed
fails; a listed defect that no longer occurs fails too, so the lists can only shrink.
"""

from __future__ import annotations

import re
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
