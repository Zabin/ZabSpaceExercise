# FS-134 — Automated Browser Verification of Load-Bearing Console Rules

> **Document ID:** FS-134
> **Version:** 1.0 (2026-10-23, pipeline run #215)
> **Status:** ✅ Done (built by `IP-1340`, `VERIFIED` 2026-10-24, `VR-1340`)
> **Approved input:** the Feature Catalog entry `FEAT-12200` (Epic `EP-12000`) in
> [`docs/feature-planning/03-feature-catalog.md`](../feature-planning/03-feature-catalog.md),
> following the FS-130–FS-133 convention. Owner decision it elaborates: `BL-0304` ("Add a small
> browser suite"), answering [GDS-08](../architecture/08-ui-architecture.md) OQ1.
> **Referenced By:** [feature index](feature-index.md); `FEAT-12200`; [IP-1340](../implementation/packages/IP-1340-browser-console-rule-suite.md) (✅ VERIFIED 2026-10-24, [VR-1340](../implementation/verification/VR-1340-browser-console-rule-suite.md))
> **Related Topics:** [GDS-08](../architecture/08-ui-architecture.md) "Verification status";
> [FS-133](FS-133-test-origin-traceability.md) (every test here carries the origin marker);
> `tools/record_walkthrough.py` (the existing headless-browser driver)

[↑ Feature index](feature-index.md) · [Docs index](../INDEX.md)

*This document follows the `06-feature-specification` skill's 20-field template. It specifies a
test suite, not product behavior: the console rules it checks belong to FEAT-8100 and FEAT-6200
and are already built; this Feature makes the browser half of them verified.*

## Feature ID

FS-134

## Title

Automated Browser Verification of Load-Bearing Console Rules

## Purpose

Verify in a real browser what the backend tests cannot: what the console actually shows — per
`FEAT-12200`'s Purpose. GDS-08 records the browser client as **unverified end to end**: every
backend path a screen uses is tested, but nothing asserts what the browser renders. The training
value of fog-of-war and plan-first depends on what the trainee sees.

## Scope

In scope: the three rules `NFR-2840` names — (a) a Blue or Red seat never displays ground truth for
objects outside its custody, (b) a command the server would refuse is shown disabled with its
reason before it is issued, (c) kinetic and cyber orders require an explicit consequence
confirmation before they are sent — plus the browser tooling, how the suite starts the server, and
how and where it runs.

Out of scope: a general UI regression suite (any rule beyond the three); the console rules
themselves (`NFR-3010`, `NFR-3020`, FEAT-8100; `FR-6210`, FEAT-6200 — this spec verifies them and
changes none); visual or pixel comparison; accessibility checks; the manual's screenshot and
walkthrough tools (`tools/render_manual.py`, `tools/record_walkthrough.py`), which stay
documentation tools that assert nothing.

## Requirements Implemented

NFR-2840 (load-bearing UI rules verified by automated browser tests) — per `FEAT-12200`'s
`Included Requirements`.

## Design Decisions

Requirements review R7 asks this specification to name the tooling and the run mode.

1. **Tooling: Playwright for Python, driving headless Chromium.** It is the driver the project
   already uses (`tools/record_walkthrough.py`), so no new technology enters the stack; it is
   installable from the package index, and a Chromium build is already present in the project's
   cloud sessions. It joins the test dependency group (`pyproject.toml`'s `dev` extra) and the
   cloud session-start hook's install list, as a minimum version per `BL-0299`.
2. **Server: started by the test, in process.** Each run starts the FastAPI app on a free local
   port in a background thread for the duration of the browser tests, and stops it afterwards; it
   never relies on an already-running server and never binds beyond the loopback interface.
3. **Run mode: in the default suite, marked, and skipped loudly only where no browser exists.** The
   browser tests run with `python3 -m pytest` like every other test. They carry a registered
   `browser` marker so they can be selected or deselected (`-m browser`, `-m "not browser"`). Where
   Playwright or a Chromium build is not installed they are **skipped with a reason that says so**,
   never silently passed. A skip is not a pass for verification: `09` and `11` must run them in an
   environment where they execute (the cloud environment does), and record that they ran.
4. **Observation, not pixels.** The globe and 2D map are canvas-drawn, so "not displayed" cannot be
   read from the page's text alone. The suite observes what the client draws (the labels and
   objects it passes to its drawing calls, and every text node and list or menu entry on the page),
   not screenshot pixels. How the drawing calls are observed is `07`'s choice (Open Question 1).

## User Workflows

1. **A developer or `08` implementer** changes console code and runs the full suite; the browser
   tests start a server, open the console as each seat, and pass or fail with the rule and seat
   named.
2. **`09` verifying a console-touching package** runs the full suite in an environment with a
   browser and records that the browser tests ran (not skipped).
3. **`11` at release** cites the browser tests' result as the evidence that the three rules hold in
   the shipped client.
4. **A contributor without a browser installed** runs the suite; the browser tests are skipped with
   a message naming what to install, and the rest of the suite runs normally.

## System Behaviour

**Rule (a) — no ground truth in a player seat** (`NFR-2840` (a), `NFR-3010`, `FR-6210`):

- The test loads a vignette and creates a situation in which Red owns at least one object Blue has
  never detected and at least one object Blue does hold a track on (by tasking a sensor or by a
  vignette's initial tracks), then opens the console as Blue.
- Pass: no page text, list entry, target menu option, tooltip, map label or globe label names the
  undetected object or its true position; the tracked object appears, carrying its confidence
  encoding (current, aging, propagated-only or uncharacterized — `NFR-3010`).
- Edge cases checked: the same for Red's view of an undetected Blue object; the target dropdown,
  which lists known targets only; the same session opened as White shows the undetected
  object (proving the test's object exists and the check is not vacuous).

**Rule (b) — disabled with its reason before issue** (`NFR-2840` (b), `NFR-3020`):

- The test opens the command menu as a cell seat and composes an order the server refuses (for
  example, an action with no access window, or a target out of custody).
- Pass: the Issue button is disabled, and the reason the server's dry-run returns (in its operator
  wording) is shown on screen before any issue attempt; composing a valid order re-enables Issue.
- Edge cases checked: a malformed parameter entry also disables Issue with a stated reason; an
  attempt to issue while disabled sends no order (the session's order list is unchanged).

**Rule (c) — consequence confirmation** (`NFR-2840` (c)):

- The test composes a valid kinetic (`engage`) order and, separately, a valid `cyber` order, and
  clicks Issue.
- Pass: a confirmation naming the consequence appears before anything is sent; declining it sends
  nothing (the session's order list is unchanged) and the console says the order was cancelled;
  accepting it sends the order.
- Edge case checked: a non-escalatory order (for example `observe`) issues without a confirmation,
  so the check is specific to the two escalatory actions.

**Every failure names its rule, seat and the offending element**, so a failing run says what broke
without a screenshot.

## Subsystem Responsibilities

| Subsystem | Responsibility |
|---|---|
| C12 Browser client / C4 Operator Console (`spacesim/ui_web/static/`) | The system under test. Unchanged by this Feature, except where a stable selector for an element the tests must find is missing; adding one (an `id` or `data-` attribute) is permitted and changes no behavior. |
| `spacesim/ui_web/server.py` (the FastAPI app) | Served in process by the test (Design Decision 2); unchanged. |
| `spacesim/tests/` | Hosts the browser tests and the server fixture; each test carries `@pytest.mark.verifies("NFR-2840", …)` naming the rule's leaf too (`NFR-3010`, `NFR-3020`). |
| `pyproject.toml`, `.claude/hooks/session-start.sh` | Declare Playwright as a test dependency (minimum version) and the `browser` marker; install it in cloud sessions. |

## Interfaces Used

INT-0002 (the HTTP surface the console uses), exercised through the browser exactly as an operator
would; no interface is added or changed.

## Data Model Changes

None.

## State Changes

None outside the test run: each test creates its own session on its own in-process server and
discards it.

## Error Handling

- Playwright or Chromium missing → the browser tests are skipped with a reason naming what is
  missing; the rest of the suite runs.
- The server fails to start or the console fails to load → the test fails (not skips), naming the
  step, since a console that does not load is itself a failure.
- An element the test needs is not found → the test fails naming the element, rather than passing
  vacuously.

## Performance Considerations

No NFR sets a test-time budget. The suite should stay "small" (`BL-0304`): one server per run, a
handful of tests, no fixed sleeps (wait on the page's own state). If the browser tests noticeably
slow the default run, the `browser` marker lets a contributor deselect them locally; verification
still runs them.

## Security Considerations

The test server binds to loopback only and lives for the test run. The tests exercise the LAN trust
model as built (client-asserted seat, `ADR-0015`): they check what an honest client shows a seat,
not whether a dishonest client can impersonate one, which the trust model accepts.

## Acceptance Criteria

1. With Playwright and Chromium installed, `python3 -m pytest` runs the browser tests (they are not
   skipped) and they pass on the current console.
2. Rule (a): opened as Blue, no rendered text, list, menu option or drawn label names a Red object
   Blue has not detected; a Red object Blue tracks is drawn with its confidence encoding; opened as
   White, the undetected object is shown.
3. Rule (a) holds for Red's view of an undetected Blue object.
4. Rule (b): a refused order leaves Issue disabled with the dry-run's reason visible before any
   issue attempt; a valid order enables Issue.
5. Rule (c): issuing `engage`, and separately `cyber`, shows a consequence confirmation first;
   declining sends no order; `observe` issues with no confirmation.
6. Each rule's test fails when its rule is deliberately broken in a scratch copy of the client — a
   ground-truth object added to the player scene, the Issue button left enabled on a refusal, the
   confirmation removed — demonstrated once at verification, not left in the suite.
7. Without Playwright installed, the browser tests are reported as skipped with a reason naming the
   missing tool, and the rest of the suite still runs.
8. Every browser test carries `@pytest.mark.verifies(...)` naming `NFR-2840` and its rule's leaf.

## Verification Plan

Criteria 1–5, 7, 8: Test. Criterion 6: Demonstration at `09` (the verifier breaks each rule in a
scratch copy and records the failing output in the Verification Report). `09` records whether the
browser tests ran or were skipped; a skipped run cannot verify this Feature.

## Dependencies

FEAT-8100 (the console and its rules `NFR-3010`/`NFR-3020`) and FEAT-6200 (the fog-of-war filtering
the player views render) per the catalog — both built. FS-133's marker is used if registered;
this suite does not wait for FS-133's backfill.

## Risks

- **Brittleness.** Browser tests break on harmless markup changes. Mitigation: target stable
  selectors (Subsystem Responsibilities) and the page's own state, never layout or timing.
- **Silent skipping.** A suite that skips everywhere verifies nothing. Mitigation: Design Decision
  3 and the Verification Plan make a skip visible and insufficient for `09`.
- **Browser version drift.** The Playwright package expects a matching Chromium build; the cloud
  image ships one at a fixed path. If they diverge, the tests must be pointed at the installed
  executable rather than downloading a browser (the cloud environment forbids the download).
- **Canvas observation** may need small test hooks in the client (Open Question 1).

## Open Questions

1. **How to observe canvas drawing.** The globe and map draw on `<canvas>`, so rule (a)'s "not
   drawn" needs the drawn labels/objects. Options: wrap the canvas drawing calls from the test
   before the page's scripts run (no client change), or have the client expose the list of objects
   it last drew (a small, test-only read hook). Matters because the second changes client code.
   **Resolution path:** `07` chooses; prefer the first, which changes nothing in the client.
2. **ADR for a new test dependency.** ADR-0020 lists the stack (pytest among it) but not test-only
   tools. Matters only if the project wants every dependency recorded in an ADR. **Resolution
   path:** `03` decides at its next maintenance pass (rides `BL-0311`); the default is that a
   test-only tool already used by the project's own tools needs no ADR.
3. **The intentional-friction rule (`BL-0312`, review R6).** DOM-007 §3, as absorbed in GDS-06
   NFR-9, asks every console design to say which friction is intentional. This spec touches the
   console's two deliberate frictions — the consequence confirmation (rule c) and the disabled
   Issue button (rule b) — and records them as intentional here: both slow the operator on purpose,
   to make an escalatory or invalid action a decision (`NFR-3020`; GDS-08 §6, "Consequence confirm"). Whether the
   feature-specification template should require that statement in every console spec is an owner
   decision. **Resolution path:** the owner, on `BL-0312` (its revisit trigger fired with this run).

## Related ADRs

ADR-0004 (fog-of-war at the session boundary), ADR-0008 (the browser client), ADR-0015 (LAN trust
model), ADR-0020 (tech stack).

## Related Interfaces

INT-0006 (the SessionAPI seam the server calls; not driven directly by the tests).
