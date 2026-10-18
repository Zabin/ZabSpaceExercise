# VR-1131 — Verification Report: Verification-Coverage Follow-Ups, Test-Only (FR-6510, FR-4210, FR-3310, NFR-3400)

> **Document ID:** VR-1131
> **Version:** 1.0
> **Status:** ✅ Final
> **Dependencies:** [IP-1131](../packages/IP-1131-verification-coverage-follow-ups.md);
> [FS-113](../../features/FS-113-observer-read-only-access.md), [FS-115](../../features/FS-115-session-setup.md),
> [FS-102](../../features/FS-102-command-scheduling.md) v1.1; `NFR-3400` (amended 2026-10-17)
> **Referenced By:** [INDEX.md](INDEX.md), [00-master-build-plan.md](../00-master-build-plan.md),
> [packages/INDEX.md](../packages/INDEX.md), [`backlog.md`](../../pipeline/backlog.md)
> `BL-0023`/`BL-0024`/`BL-0259`/`BL-0260`, `BL-0279`
> **Produces:** the `COMPLETE → VERIFIED` transition of `IP-1131`
> **Related Topics:** [`spacesim/tests/test_training_sources.py`](../../../spacesim/tests/test_training_sources.py),
> [`spacesim/tests/test_observer.py`](../../../spacesim/tests/test_observer.py),
> [`spacesim/tests/test_session_setup.py`](../../../spacesim/tests/test_session_setup.py),
> [`spacesim/tests/test_ssn.py`](../../../spacesim/tests/test_ssn.py)

[↑ Verification index](INDEX.md) · [Master Build Plan](../00-master-build-plan.md) · [Packages index](../packages/INDEX.md)

## Package

- **ID / Title:** IP-1131 — Verification-Coverage Follow-Ups (test-only): Observer rejection on
  `/roles/assign` and `/observer/view`, SSN-kind rewind parity, and a training `Sources:`-anchor test.
- **Version verified:** 1.0
- **Tree state verified:** commit `c562112` (branch `claude/chart-prompt-file-90hm9u`, local
  tracking branch `verify-batch`). Implementing commit: `6c0a4e7` (2026-10-17, pipeline run #171).
  The four test files are unchanged since `6c0a4e7`.
- **Independence:** first verification pass. Fresh session with no involvement in `6c0a4e7`.

## Result

**VERIFIED, with one Low hardening note (`BL-0279`, not a defect against the package).** A
test-only package whose tests "all passed on arrival" can be vacuous. This one is not. Every new
test was **mutation-checked**: the behaviour it guards was broken in a throwaway copy of the tree,
and the test was confirmed to fail, so none of them passes regardless of the code.

**The self-test claim, the flagged central point, was checked directly by breaking things.** The
real `test_training_sources.py` was run against a throwaway copy of `spacesim/` +
`docs/training/` + `tools/` + `spacesim.config.yaml`:

| # | Mutation in the throwaway copy | `test_training_sources.py` | Reported problem |
|---|---|---|---|
| M0 | none (baseline) | pass | — |
| — | (first copy accidentally omitted the repo-root `spacesim.config.yaml`) | **fail** | `01-install-and-run.md: path not found: spacesim.config.yaml`. An unplanned extra demonstration: a missing root-level file is caught |
| M1 | a footer symbol renamed (`13-blue` `ORDER_PARAM_RULES` → `…RULEZ`) | **fail** | `13-blue-cell-manual.md: spacesim/engine/orders.py: symbol not found: ORDER_PARAM_RULEZ` |
| M2 | a footer path moved (`13-blue` `spacesim/engine/custody.py` → `custodyy.py`) | **fail** | `path not found: spacesim/engine/custodyy.py` |
| M3 | a **code-side** rename, every occurrence (`orders.py` `ORDER_PARAM_RULES` → `OBS_RULE_TABLE`), footers untouched | **fail** | both footers that cite it (`09`, `13-blue`) reported. This is the A12 scenario the test exists for |
| M5 | a footer-cited module deleted (`session/scene.py`) | **fail** | both citing footers (`12`, `13-blue`) reported |
| M6 | a symbol on a footer **continuation** line broken (`12-white` `score_belief_truth_divergence`) | **fail** | `spacesim/session/assessment.py: symbol not found: score_belief_truth_divergenze`, so multi-line footers are parsed |
| M7 | the checker gutted (`check_footer` → `return []`) | **fail** — `test_checker_fails_on_a_broken_footer` | `assert []`. **The self-test catches a vacuously permissive checker**, which is the point of having it |
| M8 | the footer parser gutted (`_footers` → `return []`) | **fail** | `assert 0 > 50` (the footer-count guard) |
| M4 | code-side rename that **keeps the old name as a prefix** (`ORDER_PARAM_RULES` → `ORDER_PARAM_RULES_V2`) | pass | not caught: the symbol check is a substring match |
| M9 | one module's footers reformatted (`> **Sources:**` → `> Sources:` throughout `13-blue`) | pass | not caught: that module's footers silently drop out, and the guard only checks that the corpus-wide count stays above 50 |

So the checker has real teeth for every rename, move and deletion of the kind A12 is about (M1–M3,
M5, M6), and the self-test proves it catches a gutted checker (M7). M4 and M9 are limits of the
design the package itself specifies. Design Decision 3 says "assert its last dotted part
**occurs** in that file" (substring by design), and Risks says "the parser must stay tolerant".
They are recorded as a Low hardening note (`BL-0279`), not as a failed check. A coverage
measurement on the real corpus supports how cheap that hardening would be. The parser finds **67
footers**, checks **174 paths** and **278 symbols**, and every one of the 278 also matches as a
whole word (`\b…\b`), so a word-boundary check would cost nothing today. 82 of 576 backticked
footer tokens are not checked. They are routes (`GET /api/…`), sibling `.md` links, requirement
IDs, and six brace-expansion paths (`engine/{maneuver,isr,jam}.py`, `engine/{jam,engage}.py`),
which the regex does not match. The docstring mentions only routes and globs, so these brace paths
go unchecked silently (part of `BL-0279`). Two footers have no code path by design (`15` is an
index; `16` cites a `*.yaml` glob).

## Mutation checks of the other three items

| Item | Mutation (throwaway copy) | Result |
|---|---|---|
| `BL-0023`, `BL-0024` — Observer refused on `/observer/view`, `/roles/assign` (HTTP) and direct `assign_role` | `inprocess.py`: both White-only gates widened to `if cell not in ("white", "observer")` | **all 3 new tests fail**. They really send `cell="observer"` to the named route or method (read: the routes pass the body `cell` to the gated `InProcessSession` methods). Each also asserts no state change (designation stays `godview`; staffing report unchanged), not only `ok: False` |
| `BL-0259` — FR-3310 rewind parity | (a) `_rebind` no longer clears `ssn.requests`; (b) `_rebind` no longer clears `osys.orders` | **fails in both cases**, on the SSN side and on the command side respectively. The test also checks that the pre-rewind state is not vacuous (the track is delivered and the downlink `executed` before the rewind), and that `replay()` equals the live world afterwards |

**Observation on `BL-0259`, not a finding.** The package's Design Decision 2 expected the
rewound SSN request to be "pending again". As built, a rewind to before execution **drops** both
a queued command and an SSN request: lists empty, no pending execute events, and re-advancing
executes neither (`_rebind`, consistent with `CLAUDE.md`'s "queued events were dropped by the
rewind"). The implementer probed this first (journal run #171) and wrote the test to `FR-3310`'s
actual Acceptance Criterion: "returns to its pre-execution state **exactly as a command-kind
activity would**". That is parity, and parity holds. The test enforces the requirement, not the
planner's parenthetical guess. The as-built behaviour was disclosed in the journal and in `BL-0259` ("parity holds as built
(both kinds vanish on a rewind to before execution and neither re-executes)"), though not
labelled as a departure from Design Decision 2's wording. Noted here for
`07-implementation-planning`'s awareness; no action needed.

## Definition of Done audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| All tests pass; the self-test proves the anchor checker fails on a broken footer. | All 5 new tests (6 functions) pass. The self-test was checked by mutation M7, and the checker's teeth on real footers by M1–M3/M5/M6 (above). | ✅ Pass |
| No production file changed (`git show --stat` lists tests and ledgers only). | `git show 6c0a4e7 --stat`: `ROADMAP.md`, MBP, `packages/INDEX.md`, RTM, and four files under `spacesim/tests/`. No production file. | ✅ Pass |
| Full suite and both gates green; RTM and ledgers updated; follow-ups filed. | Test run below. RTM `FR-6510`/`FR-4210`/`FR-3310`/`NFR-3400` rows cite the new tests by name ✓. MBP/INDEX/ROADMAP read `COMPLETE` ✓. Follow-ups filed: `BL-0273` (`15` §15.3/§15.4 wording) and `BL-0274` (A12 status, `01-vision`), as the package's Documentation Updates require ✓. The FS-102/113/115 `Referenced By` entries still read "planned"; this report corrects them. | ✅ Pass |

## Verification Checklist audit

| Item | Evidence | Pass/Fail |
|---|---|---|
| Confirm each test exercises the named route/method with the named cell. | Read the tests and the routes, and mutation-checked them (above). `POST /api/sessions/{sid}/observer/view` and `POST /api/sessions/{sid}/roles/assign` are sent body `cell: "observer"`. `InProcessSession.assign_role(…, "observer", …)` is called directly. `submit_ssn_request` + a `downlink` order are run through `rewind_to`. | ✅ Pass |
| Break a footer symbol in a scratch copy and confirm `test_training_sources.py` fails. | M1 (footer symbol) and M6 (continuation-line symbol) both fail, naming the exact footer and symbol. M2, M3, M5, M7 and M8 go further. | ✅ Pass |
| Full suite and both gates by name. | See Test run. | ✅ Pass |

## Requirements audit

| Requirement | Tested by (new) | RTM cell | Pass/Fail |
|---|---|---|---|
| `FR-6510` (Observer cannot mutate) | `test_observer.py::test_observer_cannot_set_the_observer_view`, `::test_observer_cannot_assign_roles_over_http`, `test_session_setup.py::test_observer_cannot_assign_roles` | Cites the tests and `IP-1131` ✓ → `VERIFIED` | ✅ Pass |
| `FR-4210` (White-only role assignment) | `test_session_setup.py::test_observer_cannot_assign_roles`, the HTTP roles test | ✓ → `VERIFIED` | ✅ Pass |
| `FR-3310` (rewind parity, collection vs command) | `test_ssn.py::test_ssn_request_and_command_behave_identically_under_rewind` | ✓ → `VERIFIED` | ✅ Pass |
| `NFR-3400` (training sources gated automatically) | `test_training_sources.py` (2 functions) | ✓ → `VERIFIED` | ✅ Pass (Low hardening note, `BL-0279`) |

## Test run

```
python3 -m pytest -p no:warnings -p no:cacheprovider               # full suite (tree c562112)
python3 -m pytest spacesim/tests/test_determinism.py spacesim/tests/test_import_guard.py \
    spacesim/tests/test_training_sources.py spacesim/tests/test_observer.py \
    spacesim/tests/test_session_setup.py spacesim/tests/test_ssn.py
# mutation driver: throwaway copies of the tree, one mutation each, real test file run per copy
```

- **Full suite:** **1022 passed, 3 skipped** (1025 collected).
- **Permanent gates plus this package's four modules, run by name:** **78 passed** (the gates are
  the 14 in `test_determinism.py` + `test_import_guard.py`).
- **Mutations:** 12 run (M0–M9 on the anchor checker, 3 on the other items). Every mutation of
  behaviour the package claims to gate made a test fail; the two that passed (M4, M9) are the
  design limits described above.

## Scope audit

`git show 6c0a4e7 --stat`: exactly the declared Files to Create (`test_training_sources.py`) and
Files to Modify (`test_observer.py`, `test_session_setup.py`, `test_ssn.py`, new functions only),
plus ledgers. No production file. No excursion.

## Findings

| # | Description | Severity | Owner |
|---|---|---|---|
| 1 | `test_training_sources.py` hardening, within the package's own design but worth closing given A12's purpose. (a) The symbol check is a substring match, so a code rename that keeps the old name as a prefix or substring (`X` → `X_V2`) passes (M4). A word-boundary match costs nothing today, since all 278 symbols already match as whole words. (b) The footer-count guard is corpus-wide, so one module's footers silently dropping out after a format drift passes (M9). (c) Brace-expansion paths (`engine/{a,b}.py`, six occurrences) are silently unchecked, and the docstring names only routes and globs. | Low | `BL-0279` → `07-implementation-planning` (a small test-only remediation; or ride the next package that touches the training gate) |

## Traceability actions taken by this report

- MBP row, `packages/INDEX.md` row, `ROADMAP.md` row: `COMPLETE → VERIFIED`; MBP Package Status line.
- RTM `FR-6510`/`FR-4210`/`FR-3310`/`NFR-3400` cells: `IP-1131 (COMPLETE …, awaiting 09)` → `VERIFIED … VR-1131`.
- FS-102/FS-113/FS-115 `Referenced By` entries for `IP-1131`: "planned" → `VERIFIED` (`VR-1131`).
- Backlog: `BL-0023`, `BL-0024`, `BL-0259` and `BL-0260` → `DONE`. New `BL-0279`. `BL-0270` updated:
  `IP-1131` verified, and the batch is down to `IP-1064`'s re-verification. `BL-0273` (manual impact of this
  package) is left `SCHEDULED`; its claim that `test_training_sources.py` gates every footer is
  confirmed, subject to `BL-0279`'s caveats.
