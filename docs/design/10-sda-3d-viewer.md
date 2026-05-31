# SDA-Derived 3D Viewer

The tool includes a **3D viewer**, but with a critical doctrinal constraint the user
specified: it is **not a live feed of reality.** It renders **the cell's own Space Domain
Awareness belief state** — what that cell's sensors and shared feeds have actually observed,
characterized, and propagated. Showing perfect ground truth would be unrealistic and would
destroy the training value. This document specifies the viewer and, crucially, *what it is
allowed to draw.*

## 1. The core rule: render from custody, not from truth

There are two world states in the engine (see `04-data-model.md`):

- **Ground truth** — the real position/identity/payload of every object. Held by the engine
  and visible only to White Cell.
- **Per-cell SDA belief** — each cell's `TrackCatalog`: the objects it has detected, with
  estimated state, uncertainty, characterization, and time-since-last-observation.

> **The 3D viewer for Red or Blue draws ONLY that cell's SDA belief.** An object the cell has
> never observed does not appear. An object observed hours ago appears as a faded, propagated
> ghost with a growing uncertainty volume. This "render-from-custody" layer is shared with the
> 2D map (see `09-gui-principles.md` §3) and implemented once.

White Cell has a viewer mode that *can* show ground truth (and toggle to see exactly what Red
or Blue sees) for adjudication and after-action review.

## 2. What the viewer shows

A 3D globe with Earth, the relevant orbital regimes, and the cell's tracked catalog:

- **Earth** with day/night terminator (drives optical-sensor and dazzle constraints) and
  configurable basemap (coastlines sufficient; imagery optional).
- **Own assets** — always shown at known state (the cell commands them, so it knows where they
  are), with orbit paths, current position, sensor/jammer footprints, and fuel/health badges.
- **Tracked objects** — friendly/hostile/unknown/neutral per the cell's catalog, each rendered
  with its **confidence encoding**:
  - high-confidence current track: solid marker, thin orbit path;
  - aging track: translucent marker inside a **covariance/uncertainty ellipsoid** that grows
    with time-since-observation;
  - propagated-only (no recent obs): dashed ghost orbit and a large uncertainty volume;
  - detected-but-uncharacterized: a hollow "?" marker (we know *something* is there).
- **Ground sites** — own ground stations and SDA sensors, with their instantaneous coverage
  (radar fences/optical fields of regard) projected so the operator sees *where they can
  currently see*.
- **Access geometry overlays (toggle):** line-of-sight cones from ground stations to own
  sats (command windows), sensor-to-target observation geometry, RPO closest-approach
  predictions, and debris-field volumes.
- **Predicted tracks:** future propagated path of any selected object, with the uncertainty
  fanning out the further ahead you look.

## 3. What the viewer must NOT show
- ❌ Objects the cell has not detected.
- ❌ True positions of objects the cell only has stale tracks for (show the *estimate* and its
  uncertainty instead).
- ❌ Characterization (payload/intent) the cell hasn't earned through collection.
- ❌ The other cell's plans, queued orders, or asset health.

If the operator wants better fidelity on an object, the answer is **task a sensor** (next doc),
wait for the collection, and watch the uncertainty volume shrink — a core gameplay loop, made
visible in 3D.

## 4. Time integration
The viewer is bound to the sim clock. As time advances (real-time or White-Cell-compressed):
- own assets and tracks move along their orbits;
- uncertainty volumes **grow** between observations and **snap smaller** when a tasked sensor
  reports;
- footprints sweep; terminator moves; predicted RPO approaches update.

When White Cell rewinds/fast-forwards/undoes, the viewer re-renders from the belief state at
that sim-time (deterministic replay makes this exact).

## 5. Interaction
- Orbit/pan/zoom the globe; click an object to select it (populates the decision panel in 2D).
- Toggle layers: tracks by affiliation, footprints, LOS cones, uncertainty volumes, debris,
  predicted paths.
- "Frame" a regime (LEO/MEO/GEO) with sensible camera presets — operators shouldn't fight the
  camera.
- Scrub a *preview* of a selected object's predicted track without changing sim time.
- Right-click an unknown/aged track → **"Task sensor on this object"** shortcut into the
  tasking flow.

## 6. Fidelity now vs. later
- **v1 (moderate):** render positions from the same Kepler+J2 propagation the engine uses;
  uncertainty volumes can be a simple growth model (radius ∝ time-since-obs × along-track rate)
  rather than a true covariance. Good enough to teach the concept and look right.
- **Later (high):** real covariance ellipsoids from an estimator/UKF, SGP4 paths, sensor-
  specific measurement noise, and proper observation-update shrinking of the covariance. The
  viewer reads the same `Track` objects; only their `uncertainty` field gets richer.

## 7. Tech notes
- **Web stack:** a self-contained orthographic canvas globe (`spacesim/ui_web/static/globe.js`)
  consumes the engine's track/position stream — no external 3D library, no network deps. Coastlines
  and borders come from a committed offline `world.json`. The same `drawWorld` helper is shared
  with the 2D map (`world.js`).
- **Desktop stack:** a `pyqtgraph`/OpenGL or `vispy`-based globe would mirror the web canvas globe.
  More work than the web path — another point in favor of the web UI for v1.
- The viewer is a **pure consumer** of engine state: it never computes truth, only draws the
  belief stream the session sends it (already filtered by the per-cell fog-of-war layer in
  `07-api-and-networking.md`). This keeps the "no cheating" guarantee structural, not
  cosmetic.

## 8. Why this matters for training
Rendering belief-not-truth turns the 3D view from eye-candy into the **SDA picture an operator
actually fights from**: incomplete, aging, and improved only by deliberately tasking scarce
sensors. Watching an uncertainty volume bloom over a hostile track you stopped watching — and
realizing you've lost custody right before a decision window — is the lesson.
