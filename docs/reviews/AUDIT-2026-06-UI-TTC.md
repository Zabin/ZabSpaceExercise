# AUDIT 2026-06 (UI + TT&C) — Panel layout, power-model logic, telemetry graphs, target picker

**Date:** 2026-06-12 · **Branch:** `claude/planning-docs-review-rmZwP` ·
**Scope:** four operator-facing concerns raised after the commands audit —
(1) panel layout control, (2) TT&C/power data logic, (3) telemetry thumbnail-vs-large
graph consistency, (4) a valid-target dropdown for the command form.

---

## 1. Movable / scalable / closeable / openable panels

**Complaint:** "The layout of the new mission details shuffles the flow of everything else."
The Mission brief panel auto-opens as the first grid item in column 1; when it is tall it
forces row 1's height and pushes the rest of the console down.

**Fix:** new `spacesim/ui_web/static/panels.js` panel manager + CSS in `style.css`.
Ten panels are registered (`brief`, `cell-time`, `fleet`, `tasking`, `order`, `globe`, `map`,
`activity`, `aar`, `drill`). Each gets a header control cluster:

- **Movable** — drag the header (or the ⠿ grip) to float the panel (`position: fixed`); it
  leaves the grid flow so the remaining panels reflow, which is how an operator stops the brief
  (or any panel) from shoving the layout around.
- **Scalable** — a floated panel carries the native CSS `resize: both` handle; the size is
  persisted.
- **Closeable** — the ✕ button hides the panel.
- **Openable** — View ▾ → **Panels** lists every panel with a show/hide checkbox, plus a
  **↺ Reset layout** that re-docks everything.
- **Re-dock** — the ▣ button returns a floated panel to the grid.

State (hidden + float geometry) persists per panel in `localStorage["panel-layout-v1"]`. The
brief panel's existing collapse (▾) toggle is unchanged and independent of close/float.

Verified in a real browser (Playwright): 10 control bars injected, the Panels menu section
built, brief floats on drag, Cell & Time closes via ✕.

## 2. TT&C / power-model logic ("power goes low without clear reasoning")

A full attribute-by-attribute audit of `BusState`/`PayloadState` SOH lives in the agent report;
the headline findings and fixes:

**Root cause (BUG, fixed):** the vignette YAML drain rate (`0.0003` SoC/s) drove a
**1.00 → 0.37 sawtooth every ~97-minute orbit** (~63% depth-of-discharge — 3-4× deeper than a
real LEO bus), purely from baseline eclipse with **zero Red action**. The per-orbit margin was
razor-thin (net 0% at eclipse fraction 0.40), so any added load tipped the battery into a
death spiral. It was *not* a microsecond/seconds unit bug — `advance_bus` integrates seconds
correctly.

Fixes:
- **Recalibrated** charge/drain across all 10 vignettes (`charge 0.0002→0.00012`,
  `drain 0.0003/0.0002→0.0001`). Baseline SoC now cycles a gentle **0.79–1.00** (~21% DoD) over
  multiple orbits with no attack.
- **Penumbra-aware tick:** `advance_bus(sunlit)` now takes a *lit fraction* in [0,1] (bool still
  accepted) and blends `charge·lit − drain·(1−lit)`; `busmodel._sunlit` returns
  `eclipse_fraction()` instead of the binary `is_sunlit()`. The promised smooth terminator ramp
  (FW §11.B.10) is finally wired in, so the discharge curve no longer steps off a cliff.
- **Surfaced the cause:** `soh_snapshot` now exposes `in_eclipse` so the UI can show the
  operator *why* SoC is falling (the drop is expected physics, just never surfaced before).
- Regression test `test_power_calibration.py` pins baseline SoC ≥ 0.30 over several orbits.

**Other SOH findings (documented, lower priority — follow-up):**
- `entities.AssetResources.power_w` (1500 W in vignette 1) is a **dead field** — never read; the
  power model uses the abstract `charge_rate_per_s` instead. Either wire it (derive rates from
  array W + battery Wh) or remove it.
- `propulsion.propellant_frac` (the telemetry gauge) is **decoupled** from
  `resources.delta_v_ms` (what maneuvers actually spend) — burning Δv never moves the propellant
  gauge. Pick one source of truth.
- `ThermalState.temp_c`/`heater_watts`/`radiator_capacity_w` are declared (FW §11.B.11) but
  never integrated by `advance_bus` — `temp_c` is static at 20 °C. Either model it or mark it
  not-yet-live.
- Telemetry `ParamSpec` thresholds **do** match the bus model constants (no fix needed).

## 3. Telemetry thumbnail vs large graph

**Complaint:** thumbnails "do not appear connected to the large graphs."

**Finding (NOT a data bug):** both the sparkline and the drill-down graph fetch the *same*
read-time-seeded series from the *same* endpoint, *same* window (`now-3600s → now`), *same*
seed and sim time. The disconnect was presentation:
- the large graph folds the soft/hard limit lines into its y-range (a nominal trace reads flat),
  while the sparkline auto-scaled to its own min/max (read jagged);
- the sparkline used `n=30` vs the large graph's `n=120`, and indexed x by sample ordinal not
  time.

**Fix (`graph.js` `spark()` + `app.js`):** the sparkline now shares the large graph's y-policy
(folds in the soft/hard limits + draws a faint soft-limit line) and uses a time-based x-axis;
the thumbnail fetch is `n=120` to match. The two are now the same curve at the same scale,
differing only in size.

## 4. Valid-target dropdown

**Complaint:** "provide a drop down menu of valid targets in the other cell."

**Fix (`index.html` + `app.js`):** added `#o-target-pick` next to the free-text id field.
Fog-of-war correct:
- **Blue/Red** are offered their `known_tracks` — the only enemy objects they've identified
  (you must build custody before you can target).
- **White** (god view) is offered every asset *not* owned by the selected actor's side, grouped
  by owner — so a White operator driving a Blue asset is offered Red targets.
- Ground stations / sensors are never offered as offensive targets; the picker rebuilds on actor
  change (valid targets depend on the actor's side). The free-text id input is retained for
  own-asset commands and manual entry.

---

**Test status:** 473 passed, 3 skipped (was 469; +4 from `test_power_calibration.py`). UI
changes (panels, graph, target picker) are HTML/CSS/JS only and were verified live in a real
headless browser, not by pytest.
