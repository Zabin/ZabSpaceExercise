[↑ Docs index](../INDEX.md) · [Pipeline journal](../pipeline/pipeline-journal.md) ·
[Training index](../training/INDEX.md) · [Traceability matrix](../training/15-manual-traceability.md)

# Training Review — Run #114 Scope (Inject Fire-Time Validation, Target "or id" Orientation, White Manual Split)

> **Document ID:** REV-TRN-005
> **Skill:** `09-training-manual-review`
> **Scope:** the sections one `08-training-manual-authoring` run (pipeline run #114) touched, in
> two commits:
> - **`f500c8a`** (closing `BL-0192`/`BL-0194`/`BL-0195`): `10-ui-reference.md` §10.3 (row 2,
>   new row 11, the four `FR-4430` effect types and their keys, the "checked before anything
>   fires" list, the timed/conditional skip rules); the `WCM-5` "refused whole" bullet and its
>   `> Sources:` footer; `11-vignette-playbooks.md` "How to read a step"; `03-first-exercise.md`
>   Step 4; the `04-guided-vignette.md` set-up callout; `15-manual-traceability.md` §15.1 Injects
>   row and §15.2 `WCM-5` row.
> - **`dc5073e`** (closing `BL-0179`): the White manual split — `WCM-12`–`WCM-16` moved to the new
>   `12a-white-cell-analysis-and-exports.md`; the pointer section left in `12`; `training/INDEX.md`;
>   the §15 header and §15.2 White note; ROADMAP `TR-12a`.
>
> Each touched section was read whole, not just the changed lines.
> **Commit reviewed:** `a7695ea` (branch `claude/chart-prompt-file-90hm9u` tip at review time; no
> commit after `dc5073e` touches `docs/training/`).
> **Independence:** this session authored neither commit, nor any commit on this branch before
> this review. It is a fresh session, distinct from the one that ran pipeline runs #113–#119.
> **Upstream:** `08-training-manual-authoring` (run #114) · **Downstream:**
> `10-integration-review`, `11-release-readiness`

## Headline

Run #114's prose is **accurate against shipped behaviour in every load-bearing claim**. It was
checked in code and driven live on a fixture different from the author's: `geo-rpo-shadowing`
seed 23 for the injects, and `leo-isr-denial` seed 1 / `training-basics` seed 1 for the target
claims. The split moved every line verbatim. Traceability is consistent in both directions, with
0 orphans. The playbook suite passed 16/16, and `test_training.py` passed 4/4.
**No Critical or High findings.** There are 3 Low findings:

- F1: one sentence in §10.3 overstates what goes unchecked.
- F2: the §10.3 pointer to example payloads covers none of the four new effect types.
- F3: two broken intra-file anchors in `01`. These are pre-existing and outside the scope of run
  #114's edits.

## Dimensions exercised

### 1. Accuracy — prose claims vs. shipped behaviour

**Code reads** (at `a7695ea`):

- `session/manager.py`: `INJECT_EFFECT_TYPES`, `_INJECT_REQUIRED_KEYS`, `_MANEUVER_MODES`,
  `_inject_effect_problem`, `validate_inject_effects`, `fire_inject`, `_apply_inject_effects` and
  `_skip_inject_effect`.
- `ui_web/server.py`: the `/inject` route, which turns a failed `Ack` into a 400 with `detail`.
- `ui_web/static/app.js`: `api.post` (throws `Error(await r.text())` on a non-2xx response),
  `fireInject`, `fireBuiltInject`, `buildTargetGroups`, `targetOptionsHtml` and
  `populateTargetPicker`.
- `index.html`: the `o-target-manual` and `task-target-manual` "or id" inputs.

**Live drive** (in-process `TestClient` on `geo-rpo-shadowing` seed 23; the author used
`multi-domain-taiwan` seed 5). Two vignette timed injects were added to the loaded `Vignette`
before `start()`, in the content-as-data shape:

| Claim (location) | Exercised | Observed | Verdict |
|---|---|---|---|
| A bus-less `anomaly` is rejected whole, and a valid effect ahead of it is not applied (§10.3, `WCM-5`) | builder POST: `message` + `anomaly` on `RED-INSP` | 400 `inject rejected: #1 anomaly: anomaly target 'RED-INSP' has no bus …`; the message never appeared | ✓ |
| One entry per bad effect; `#i` counts from 0 (row 11) | `[bogus, message-without-text, sensor_outage on BLUE-HVA]` | 400 `#0 bogus: unknown effect type …; #2 sensor_outage: … is not a sensor`; a bare `message` is valid, since it has no required keys | ✓ |
| `forced_custody_loss` needs a held track; `scripted_manoeuvre` needs a valid mode and an orbit (§10.3 list) | three single-effect POSTs | 400 `red holds no track on 'NOPE'`; 400 `mode 'warp' is not one of [...]`; 400 `'BLUE-OPT' does not exist or has no orbit` (a ground sensor) | ✓ |
| Fire-by-name runs the same check (§10.3) | `{"inject": "t2"}` (a vignette inject: bus-less `anomaly`) | 400, same reason text | ✓ |
| Timed vignette inject: a malformed effect is skipped, the others apply, and White alone is told (§10.3, `WCM-5`) | `t1` at +60 s: `anomaly` with `subsystem: power` + a Blue `message` | messages: `[white] inject effect skipped (anomaly): anomaly subsystem must be 'bus' or 'telemetry', got 'power'` and `[blue] TIMED-OK` | ✓ |
| A well-formed effect whose target is unsuitable when it fires is skipped with no message (§10.3) | `t2` at +120 s: bus-less `anomaly`; and a builder `anomaly` on `BLUE-HVA` scheduled +600 s, whose `bus_state` was then removed before it fired | no message in either case | ✓ |
| Builder injects scheduled for later are "**not** checked at the console" (§10.3) | builder bus-less `anomaly` with `at_sim_t` = now + 600 s | **400 at scheduling time**. The console does check it; only the re-check when it fires is absent | **F1** |
| The Fire button shows nothing on a 400 (row 2, `WCM-5`) | code read: `fireInject` has no `catch` and no result element, and `app.js` has no global `unhandledrejection` handler | the rejection goes only to the browser console | ✓ (bug already filed as `BL-0196`) |
| Row 11 result-line text | code read: `"✗ server error: " + err.message`, where `err.message` is the response body | renders as `✗ server error: {"detail":"inject rejected: #i …"}`. Row 11 ("followed by the server's … text") and `WCM-5` (`✗ server error: … inject rejected: …`) are both accurate; the JSON envelope sits inside the ellipsis | ✓ (observation, no finding) |
| `03` Step 4: Red holds no track on `ISR-EO-1`, so the dropdown reads *no known targets yet* | `leo-isr-denial` seed 1 Red view, at start and after +30 min then rewind to 0 | `known_tracks` = [], and no non-Red targetable asset in view → the empty-state option `no known targets yet — type an id below, …` | ✓ |
| `04` callout: `RED-TGT` (Blue Step 2) and `ISR-EO-1` (Red Step 2) are not listed | `training-basics` seed 1, Blue and Red views at start | both `known_tracks` = [] | ✓ |
| `11`: the dropdown lists known objects; the "or id" box takes them otherwise | code read (`buildTargetGroups`, `index.html:392`) | matches; the §10.6 row 4 anchor resolves | ✓ |

**Split verbatim check (`dc5073e`).** All 135 lines removed from `12-white-cell-manual.md` occur
verbatim in `12a-white-cell-analysis-and-exports.md` (`grep -vxFf` over removed lines vs. 12a →
empty). The only additions to `12` are the six-line pointer section. `12a` carries a nav header,
an orientation paragraph and the five sections, with IDs unchanged.

### 2. Traceability integrity

A scripted check over all of `docs/training/*.md` at `a7695ea`:

- **Links:** every relative link resolves to an existing file, and every anchor into a `.md`
  resolves, except two pre-existing intra-file anchors in `01` (**F3**, not in scope). All links
  added by run #114 (to §10.3, §10.6, `12a`, `12`, `15`) resolve.
- **Section IDs:** 43 `WCM`/`BLU`/`RED` section IDs are defined across `12`/`12a`/`13`/`14`,
  with no duplicates. Every ID is cited in `15`, and every ID `15` cites is defined. **0 orphans.**
- **Footers:** every literal `spacesim/…` path in a `> Sources:` footer exists (0 missing). The
  three function names `WCM-5`'s footer adds (`fire_inject`, `validate_inject_effects`,
  `_skip_inject_effect`) and the two `app.js` names (`fireBuiltInject`, `fireInject`) all exist.
- **Footer ⇄ matrix:** the `WCM-5` footer matches the §15.2 `WCM-5` row and the §15.1 Injects
  row exactly.
- **Split bookkeeping:** `15` names `12a` in its header and in the §15.2 White note; `INDEX.md`
  has a `12a` row and the role pointer; ROADMAP `TR-12a` is present. No inbound link anywhere in
  the repo targets a moved `WCM-12`–`16` anchor in `12-white-cell-manual.md`, so none broke. The
  IP-package prose mentions of `WCM-14`/`15`/`16` cite IDs, not file anchors.

### 3. Coverage

- Fire-time inject validation is White-only (only White fires injects). It is covered in the
  shared reference (§10.3) and in the White role section (`WCM-5`). No Blue/Red section is owed,
  and the skip message is White-only by design (`to: ["white"]`).
- Untracked-target guidance now reaches every onboarding entry point a new operator meets first
  (`03` Step 4, the `04` set-up callout, `11`), plus §10.5/§10.6. REV-TRN-004 already found the
  role manuals' coverage clean.
- **Gap (F2):** §10.3 sends the reader to `07-white-cell-facilitation.md` "for example payloads",
  but `07` has a single example (`space_weather` + `message`) and none for any of the four `FR-4430` types, so a facilitator has the key names
  and no worked example. The optional `forced_custody_loss` key `degrade_to`, which the validator
  checks, is not mentioned anywhere in the corpus.
- Recently shipped packages: `IP-1212` (VERIFIED) is outside run #114's scope; its manual impact
  is already tracked as `BL-0202`.

### 4. Pedagogy

- **Audience fit (MSTR-003 / NFR-3600):** the new text is procedural ("type its id in the **or
  id** box"; "re-check the inject in the builder"). It quotes the exact on-screen strings an
  operator will see, which suits recognition-based troubleshooting. "HTTP 400" appears in
  facilitator-facing text, next to the plain-language consequence ("applies none of its
  effects"); this is acceptable for the White audience.
- **Module size (NFR-3500, ~300 lines):** the split brought `12` from 334 to 205 lines, with
  `12a` at 148. `10-ui-reference.md` is at 469 lines, already tracked as `BL-0198`; run #114 added
  31 lines to it.
- **Grounding:** the split's rationale cites NFR-3500 directly. No sequencing or scaffolding
  decision in scope needs R600 grounding beyond that.

## Findings

| Finding | Artifact(s) | Description | Severity | Recommended owner |
|---|---|---|---|---|
| F1 | `10-ui-reference.md` §10.3 ("Two cases are **not** checked at the console", second bullet) | Builder injects scheduled for later **are** checked at the console, when you click Schedule / fire. Live: a bus-less `anomaly` at +600 s returned 400 immediately. What is missing is a re-check when the inject fires. The bullet's own trailing clause ("whose targets may have changed since you scheduled them") hints at that, but the lead-in says the opposite. Consequence for the next sentence: a *malformed* effect can never reach fire time by this route, so for builder injects only the silent target-miss skip applies. Suggested wording: "checked when you schedule them, but not re-checked when they fire". | Low | `08-training-manual-authoring` |
| F2 | `10-ui-reference.md` §10.3 ("See `07-white-cell-facilitation.md` for example payloads"); `07-white-cell-facilitation.md` | `07` has a single example payload (`space_weather` + `message`, lines 55–56), so it gives no example for any of the four new types `anomaly` / `sensor_outage` / `forced_custody_loss` / `scripted_manoeuvre`, nor for most of the earlier eight. The optional `forced_custody_loss.degrade_to` key is undocumented. Either add worked examples (e.g. one `scripted_manoeuvre` with a real `params` shape) or narrow the pointer. | Low | `08-training-manual-authoring` |
| F3 | `01-install-and-run.md:155-156` (pre-existing, outside run #114's edits) | Two intra-file anchors do not resolve: `[§9](#9-http-api-reference)` (the HTTP API reference is `08-http-api-reference.md`) and `[§4](#4-your-first-exercise)` (§4 and its "Headless walkthrough" are in `03-first-exercise.md`). These are left over from the earlier monolith-to-modules split. | Low | `08-training-manual-authoring` |

## Verification runs (at `a7695ea`)

- `python3 -m pytest spacesim/tests/test_vignette_tutorials.py -q` → **16 passed**.
- `python3 -m pytest spacesim/tests/test_training.py -q` → **4 passed**.
- Live-drive and link/orphan scripts: session scratchpad only; nothing written to the tree.

## Pipeline position

Stage 09 peer (training review). The only files this review wrote are this report and its
ROADMAP review-theme entry. All three findings route to `08-training-manual-authoring`. They are
Low, so they can ride the next pass on the same files: `BL-0202` is already `SCHEDULED` for
`08-training-manual-authoring` and touches the White manual corpus.
