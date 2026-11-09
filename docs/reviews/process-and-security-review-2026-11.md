# Process and Security Review — pipeline, development, documentation, malicious code

> **Requested by:** the owner, 2026-11-09, as the input to a whole-repository refactor.
> **Reviewed commit:** `ae7a5f1` (`main`); product code is identical to Release 1.0 (`82436ba`).
> **Companion:** [whole-release integration review](integration-review-release-1.0-whole-release.md) (product behaviour; ten findings).
> **Nature:** read-only. Nothing was fixed. This is not a pipeline stage report; it reviews the pipeline itself.
> **Headline:**
> - **Malicious code: none found.** No backdoor, hidden network call, obfuscated payload, unsafe loader, secret, hidden-character trick or planted instruction in the tracked tree.
> - **Vulnerabilities: 1 Medium, 4 Low.** The Medium is stored script injection in the console.
> - **Process: 3 High, 6 Medium, 3 Low.** The largest: no automated checks run on any pull request, and the project's records restate the same fact in up to 14 files.

## 1. What was examined, and how

| Area | Method |
|---|---|
| Malicious code | Pattern sweep of all 169 Python files, 9 JavaScript files, the shell hook, `.claude/` and `.github/` for dynamic execution, process spawning, unsafe deserialization, network use, encoded blobs. Every hit was read. |
| Secrets | Regex scan for cloud, GitHub, API-key and private-key formats over the tree and over the history of every ref. |
| Hidden text | Scan for zero-width, bidirectional-override and tag characters; scan of skills and docs for planted-instruction phrasing. |
| Binaries | `file` on all 60 images and video; the one SVG checked for script. |
| Dependencies | The 33 pins in `requirements.lock` checked by name and with `pip-audit`. |
| Web surface | `server.py`, `inprocess.py`, `manager.py` read in full (previous review); HTML sinks in the console read; a dozen live requests for injection, cross-origin, host, size and path-traversal behaviour. |
| Process | Measurements of the tree, the skills, the records and the Git history; the pipeline's own rules read against what the records show happened. |

**Limits.** The sweep is pattern-led: it reads every hit, not every line. History was scanned for secrets only. The 123 remote branches were not reviewed beyond that scan. No fuzzing, no load test.

## 2. Malicious code — clean

- **Dynamic execution:** no `eval`, `exec`, `compile`, `pickle`, `marshal`, `ctypes`, `__import__` or `shell=True` anywhere in product code or tools.
- **Process spawning:** two uses, both fixed argument lists with no user input: `spacesim/version.py` runs `git rev-parse --short HEAD`; the `run-spacesim` driver starts `uvicorn`. Tests spawn `pytest` on themselves.
- **Network:** product code makes no outbound connection. The console loads only its own nine scripts and one stylesheet; no CDN, no external URL anywhere in code.
- **Loaders:** every YAML read is `yaml.safe_load`.
- **Secrets:** none in the tree; none in any ref's history.
- **Hidden characters and planted instructions:** none in code, skills or documents.
- **Binaries:** 57 PNG, 1 GIF, 1 WebM, 1 SVG; all are what their extensions say; the SVG has no script.
- **Dependencies:** all 33 names are the genuine packages (`annotated-doc` and `opentelemetry-api` are pulled in by `fastapi`; `pyee` and `greenlet` by `playwright`). `pip-audit`: no known vulnerabilities.
- **Hooks and automation:** one session-start hook (installs Python packages, cloud sessions only); no Git hooks; no workflows.
- **Path traversal:** static files, vignette source and vignette load all refuse `..` (404 or 400).
- **Cross-site request forgery:** a cross-origin preflight is refused (405) and a `text/plain` JSON body is refused (422).

## 3. Vulnerabilities

| # | Finding | Evidence | Severity | Owner |
|---|---|---|---|---|
| **S-1** | **Stored script injection in the console.** Several places build HTML from server data without escaping. | `app.js` conjunction list (`<b>${c.a}</b>`), coaching notes (`n.title`, `n.body`), the first inject drop-down (`i.id`, `i.label`). Live: an inject with `a: "<img src=x onerror=alert(1)>"` was accepted and served to Blue's conjunction feed. Messages and tracks are escaped correctly, so the escaping helper exists and is simply not used everywhere. Two routes in: any request naming the White seat, and a vignette file from someone else (coaching notes, inject labels). | Medium | `07` (remediation package; escape at every sink, validate inject `a`/`b` as ids) |
| **S-2** | **No `Host` check.** A request with `Host: evil.example` is served. A web page the facilitator visits could use DNS rebinding to reach a loopback-bound server. | live, 200 | Low | `07` (trusted-host list from the config file) |
| **S-3** | **No size limits.** `creator/seats` with a count of 3,000,000 returned a 43 MB reply and stored the list; request bodies are unbounded (a 20 MB body was accepted). | live | Low | `07` (with the caps package, `BL-0407`) |
| **S-4** | **The lock has no hashes, and the session hook ignores it.** `requirements.lock` pins versions but not file hashes. The session-start hook installs unpinned packages and skips any already present, so a cloud session tests on whatever is installed: this session had `pydantic` 2.13.5 and `numpy` 2.5.3 against the locked 2.14.2 and 2.5.4. | hook, `pip` | Low | `08` (dependency package in M0: hashed lock; hook installs from the lock) |
| **S-5** | **Seven requests return HTTP 500, and the vignette list exposes absolute server paths.** | integration review L-1; plan row P-13 | Low | already routed |

Also security-relevant, from the companion review: order-preview routes return ground truth to a cell (M-1). The absence of authentication is the documented trusted-LAN model, not a finding.

## 4. Pipeline process

| # | Finding | Evidence | Severity |
|---|---|---|---|
| **P-1** | **Nothing checks a pull request automatically.** There is no workflow; both open PRs report zero checks. "Suite green before every commit" depends on each session remembering. | `.github/` holds only the PR template | High |
| **P-2** | **One fact is written in many places.** A single package (`IP-1160`) is named in 14 files, 147 times in the Master Build Plan alone. Its status is restated in the package header, the build plan, the package index, `ROADMAP.md`, two traceability matrices, the journal and the backlog. Every review so far has found ledger drift; the documentation-integrity suite exists to catch it after the fact. | counts at `ae7a5f1` | High |
| **P-3** | **The records are not readable.** Journal rows run to 5,800 characters in one table cell; backlog cells to 14,300. The two live files are 254 KB; the archives 772 KB. A reader cannot find what is open without a script. | `docs/pipeline/` | High |
| **P-4** | **The independent release review found five Medium defects that 94 package verifications and seven integration reviews did not.** Each verification checks a package against its own specification; behaviour that falls between packages has no owner and no test. | companion review | Medium |
| **P-5** | **Throughput cost.** 268 manager runs delivered 94 packages (about 2.9 runs each), under one-step-per-run and fresh-session verification. | journal | Medium |
| **P-6** | **The skills carry their own history.** 21 skills, 4,441 lines; `08-code-implementation` is 577 lines and `05-feature-decomposition` 546. Dated owner decisions and past incidents are written into the rules. | `.claude/skills/` | Medium |
| **P-7** | **Pull requests wait.** The branching rule is squash-merge to `main`, but nothing merges: #91 has been open six days. The session cannot merge without the owner's instruction. | PR state | Low |
| **P-8** | **123 remote branches.** Deletion and tag pushes are refused from cloud sessions (HTTP 403). | `git branch -r` | Low |

## 5. Development process

| # | Finding | Evidence | Severity |
|---|---|---|---|
| **D-1** | **No linter, formatter or type checker is configured.** `pyproject.toml` configures only `pytest`. | `pyproject.toml` | Medium |
| **D-2** | **A few files carry most of the logic.** `app.js` 3,233 lines; `manager.py` 1,917; `orders.py` 1,285; `server.py` 1,271; `inprocess.py` 1,138. Comments record package history (`IP-xxxx`, `BL-xxxx`) on most functions, so the code reads as a change log. | line counts | Medium |
| **D-3** | **The development environment is not the release environment.** See S-4. `requires-python` says 3.11; only 3.13 was validated (already decision D14). | hook, lock | Medium |
| **D-4** | **5.4 MB of generated media is committed** (a 4.1 MB video, a 1.3 MB GIF, 57 screenshots produced by `tools/render_manual.py`). | `docs/manual/` | Low |

**Worth keeping as they are:** the determinism gate; the import guard; the fog-of-war matrix tests; test-origin tagging with a generated matrix column; the documentation-integrity checks; the per-release lock, archive ref and manifest; verification by a session that did not write the code. The suite is fast: 2,244 tests in about five minutes on four cores, which makes P-1 cheap to fix.

## 6. Documentation process

| # | Finding | Evidence | Severity |
|---|---|---|---|
| **C-1** | **Documentation outweighs the product six to one.** 125,700 lines of documentation in 621 files against about 21,000 lines of production code. Implementation records alone are 35,100 lines. | tree counts | Medium |
| **C-2** | **`CLAUDE.md` is 67 KB and is loaded into every session.** 443 of its 687 lines are a code map that narrates package history (135 package references; one line is 1,446 characters). The durable guidance is under 150 lines. | `CLAUDE.md` | Medium |
| **C-3** | **Superseded material is still in the tree and still linked.** `docs/build-spec/` (9 files, last changed June), `docs/design/` (16), `docs/domains/` (10), `docs/implementations/` (11, beside `docs/implementation/`), three June audit files, `FUTURE-WORK.md`, `DOCUMENTATION-PLAN.md`. There are two requirements traceability matrices. `CLAUDE.md` still gives build-spec paths for the phase plan. | tree | Medium |
| **C-4** | **`memory.md` is five months stale** (last changed 2026-06-28; reports 469 tests) while `CLAUDE.md` still directs readers to it. | `memory.md` | Low |
| **C-5** | **The functional-requirements file is 309 KB in one file**, opening with a 30-line amendment history before any requirement. | `docs/requirements/01` | Low |

The retirement sweep (decision D10, plan item D-08) already covers part of C-3.

## 7. What this means for the refactor

Proposed order. Each step is a separate, reviewable change.

1. **Safety net first.** Add a CI workflow: full suite, determinism gate, documentation integrity, `pip-audit`. Record the baseline (suite counts, a world-state hash per vignette from the replay check) so every later step can prove it changed no behaviour.
2. **Records.** One source of truth per fact. Package status lives in the package header only; the build plan, index and roadmap tables are generated from it, as the matrix Test column already is. Journal and backlog become short structured entries (one item per file, or a data file with a generated view). History stays in the `archive/release-1.0` ref, not the working tree.
3. **`CLAUDE.md` and memory.** `CLAUDE.md` cut to the durable guidance (invariants, commands, trust model, where to look). The code map becomes module-level documentation next to the code. `memory.md` retired.
4. **Documentation.** The retirement sweep; one traceability matrix; one implementation folder; requirements split by family; generated media out of Git.
5. **Pipeline skills.** Shared rules stated once in the README; each skill reduced to its own procedure; dated history removed. Add a seam check to verification (P-4): tests generated from the live route table for fog and for refusals, as the non-finite guard already has.
6. **Code.** Behaviour-preserving restructuring behind the determinism and replay-equality gates: split `app.js`, `manager.py` and `server.py` by responsibility; move history out of comments; add `ruff` and a type check. The fourteen product and security defects from the two reviews are fixed as their own packages, not inside the restructuring, so a behaviour change is never hidden in a move.

**Decisions this needs from the owner.**

| # | Question | Recommendation |
|---|---|---|
| 1 | Is the restructuring behaviour-preserving, with defect fixes as separate packages? | Yes |
| 2 | Does it run through the pipeline? | Code through packages and independent verification. Records, documents and skills as owner-authorized maintenance changes, since the pipeline cannot review itself. |
| 3 | May superseded records and documents leave the working tree, given `archive/release-1.0` holds them? | Yes |
| 4 | May a GitHub Actions workflow be added? | Yes |
| 5 | Who merges? The refactor is many small PRs; they stall if each waits days. | Owner grants merge-on-green for this track, or reviews in batches |
