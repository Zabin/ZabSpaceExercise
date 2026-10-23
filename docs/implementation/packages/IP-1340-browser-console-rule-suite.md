# IP-1340 — Browser Suite for the Load-Bearing Console Rules (NFR-2840)

> **Package ID:** IP-1340
> **Version:** 1.0
> **Status:** 🟢 READY — authored 2026-10-23 by `07-implementation-planning`, pipeline run #222.
> No package dependencies.
> **Authorization (MSTR-006 §3):** **not yet given.** The owner decided to add the suite
> (`BL-0304`); the build go-ahead is separate.
> **Dependencies:** [FS-134](../../features/FS-134-browser-console-rule-suite.md) v1.0 (the spec).
> **Referenced By:** [00-master-build-plan.md](../00-master-build-plan.md), [packages/INDEX.md](INDEX.md),
> [`backlog.md`](../../pipeline/backlog.md) `BL-0304`
> **Produces:** a headless-browser test module, in the default suite under a `browser` marker,
> checking FS-134's rules (a)–(c); Playwright as a test dependency.
> **Feature Reference:** [FS-134](../../features/FS-134-browser-console-rule-suite.md) (`FEAT-12200`)
> **Related Topics:** [IP-1330](IP-1330-test-origin-marker-and-checks.md) (registers `verifies`;
> independent); `tools/record_walkthrough.py` (the existing Playwright driver)

[↑ Master Build Plan](../00-master-build-plan.md) · [Packages index](INDEX.md) · [Docs index](../../INDEX.md)

*Forward-design package; test and test-tooling only.*

---

## Package ID

IP-1340.

## Objective

**As built at `1e52643`**, no test drives the browser (GDS-08 "Verification status").
`tools/record_walkthrough.py` drives Playwright against a running server and asserts nothing; it
launches Chromium with an explicit executable (`/opt/pw-browsers/chromium-1194/chrome-linux/chrome`,
line 80). **Measured 2026-10-23:** Playwright 1.64.1 (current on the package index) expects its own
Chromium build 1248 and fails to launch by default here; launched with the installed build's
executable it works (Chromium 141). After this package, `python3 -m pytest` runs a small browser
suite that checks FS-134's three rules, skipping loudly only where Playwright or a Chromium build is
missing.

## Design Decisions

1. **Browser executable.** Use Playwright's own browser when present; otherwise the first installed
   Chromium under `PLAYWRIGHT_BROWSERS_PATH` (the cloud image's `/opt/pw-browsers`), the same
   approach as `tools/record_walkthrough.py`; skip with a reason naming what is missing when neither
   exists. Never download a browser from a test (FS-134 Risks).
2. **Server fixture.** A module-scoped fixture starts `spacesim.ui_web.server:app` with uvicorn on
   a free loopback port in a background thread, waits until it answers, and stops it at teardown
   (FS-134 Decision 2).
3. **Canvas observation** (FS-134 Open Question 1, decided here): an init script, added to the page
   before the console's scripts run, wraps the 2D canvas drawing calls that render text
   (`fillText`/`strokeText`) and records each label drawn. Rule (a) then checks both the page's text
   and the recorded labels. No client code changes. (`globe.js` and `app.js` draw their labels with
   `fillText`; the init script covers both.)
4. **Driving the console.** Choose the seat with the header seat buttons (`index.html` line 22–25,
   `data-cell`), compose orders through the command menu (`#o-action`, `#o-target`,
   `#o-target-manual`, `#issue`, `#o-preview`), and handle `window.confirm` through Playwright's
   dialog event (accept or dismiss). Session setup (create, start, task a sensor) goes through the
   HTTP API from the test, naming `cell=white`, so only the rule under test is driven in the page.
5. **Stable selectors.** If an element the tests need has no stable selector, adding an `id` or
   `data-` attribute to `index.html`/`app.js` is in scope; nothing else in the client changes.

## Requirements Covered

NFR-2840 (with `NFR-3010` and `NFR-3020` named in the rule (a)/(b) markers as the rules being
verified in the browser — both are FEAT-8100's leaves, verified here, not owned).

## Architecture Components

Test suite and test configuration; the C12 browser client is exercised, not changed (except
Decision 5).

## Interfaces

INT-0002, driven by the real browser client.

## Files to Create/Modify

- **Create** `spacesim/tests/test_browser_console_rules.py` — the fixture (Decisions 1–2), the init
  script (Decision 3), and the tests below.
- **Modify** `pyproject.toml` — add `playwright>=1.44` to the `dev` extra (minimum version only,
  `BL-0299`); register the `browser` marker (with `verifies` if IP-1330 has not already).
- **Modify** `.claude/hooks/session-start.sh` — add `playwright` to the install list (no browser
  download; the image ships Chromium).
- **Modify** `CLAUDE.md` "Build/test commands" — how to run or deselect the browser tests
  (`-m browser`, `-m "not browser"`) and that they skip where no browser is installed.
- **Modify** (only if Decision 5 applies) `spacesim/ui_web/static/index.html` / `app.js`.
- *Not modified:* `docs/architecture/08-ui-architecture.md` belongs to `03`; its "Verification
  status" paragraph is updated by `03` after this package is verified.

## Implementation Tasks

1. Baseline suite run.
2. Build the fixture and init script; confirm a trivial page load test runs headless here.
3. Write each rule test; for each, break the rule in a scratch copy of the client once and confirm
   the test fails (FS-134 criterion 6) — record the output for `09`; do not commit the breakage.
4. Dependency, marker, hook and `CLAUDE.md` updates.
5. Full suite (browser tests running, not skipped), both gates.

## Tests to Add

In `spacesim/tests/test_browser_console_rules.py`, all marked `browser`:

| Test | Verifies | Asserts |
|---|---|---|
| Blue view: no page text, list entry, target option or drawn label names a Red object Blue has not detected; a tracked Red object is drawn with its confidence encoding | `NFR-2840`, `NFR-3010` | as stated (rule a) |
| Red view: same for an undetected Blue object | `NFR-2840`, `NFR-3010` | as stated |
| White view shows the undetected object (non-vacuity) | `NFR-2840` | object present |
| Refused order: Issue disabled, dry-run reason shown before any issue; valid order enables Issue | `NFR-2840`, `NFR-3020` | as stated (rule b) |
| Malformed parameters disable Issue with a reason; a click while disabled sends nothing | `NFR-2840`, `NFR-3020` | order count unchanged |
| `engage` and `cyber` show a consequence confirmation; dismissing sends nothing and shows "cancelled"; accepting sends | `NFR-2840` | as stated (rule c) |
| `observe` issues with no confirmation | `NFR-2840` | no dialog |
| Without a browser the module skips with a reason (simulate by pointing the executable lookup at nothing) | `NFR-2840` | skip reason names the missing tool |

## Documentation Updates

`CLAUDE.md` (commands); RTM `NFR-2840` (and the browser half of `NFR-3010`/`NFR-3020`) Test cells.
GDS-08's verification-status paragraph is `03`'s follow-on once `09` passes.

## Definition of Done

1. The browser tests run headless in this environment and pass.
2. Each rule's test was seen failing against a deliberately broken scratch client (recorded).
3. Without Playwright or Chromium, the module skips with a named reason; the rest of the suite runs.
4. Playwright declared as a minimum-version test dependency and installed by the session hook.
5. Every test tagged; full suite and both gates green.

## Verification Checklist

- [ ] The full suite output shows the browser tests **ran** (not skipped) in the verification
      environment.
- [ ] `09` repeats the deliberate-break demonstration for at least one rule.
- [ ] No client file changed except stable-selector additions (diff check).
- [ ] The server fixture binds loopback only and stops at teardown (read it).
- [ ] `pyproject.toml`, the hook and `CLAUDE.md` updated; both gates green by name.

## Dependencies

None. (IP-1330 is independent: if it lands first its strict-marker mode requires this package to
register `browser`, which it does.)

## Risks

- **Browser/Playwright version drift** (measured above): Decision 1's fallback; a future image
  change is caught by the skip-with-reason, which `09` treats as not verified.
- **Brittle selectors and timing:** waits on page state, never fixed sleeps; stable selectors.
- **Slow default run:** a handful of tests on one server; the marker allows local deselection.

## Rollback Considerations

Revert the commit; removing a test-only dependency and module changes no runtime behavior.
