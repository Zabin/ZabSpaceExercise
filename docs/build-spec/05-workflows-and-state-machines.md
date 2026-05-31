[← Build Spec index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 13. Operator workflow walkthroughs

These narrate the **actual click-path** for each major role so the GUI (M5) is built around real
tasks, not abstract menus. Each references the requirements it satisfies.

### 13.1 White Cell — set up and start an exercise
1. Launch app → **New Exercise** → choose **Build new** or **Load vignette JSON**. (FR-S1)
2. If building: pick a base template or blank; set title, mission text, **start epoch**, **seed**,
   and **classification** (UNCLASSIFIED//EXERCISE or //TRAINING). (FR-W5)
3. Add assets: choose templates (e.g., `ISR_EO`, `SATCOM_GEO`), then set each asset's starting
   orbit by **importing a TLE from Space-Track** (if online) or **pasting/entering one manually**,
   or entering Keplerian elements. Assign ground sites and sensors. (FR-S2)
4. Define `roles_needed` (the builder suggests roles from the assets present): e.g., *Blue ISR
   Bus Op*, *Blue ISR Payload Op*, *Blue SDA Op*, *Red EW Op*, *Red Orbital Op*. (FR-W2, OR-2)
5. Set tunable parameters incl. the **safe-mode dials**; set injects. **Validate** → fix any
   precise errors (bad TLE, unsatisfied role). **Save JSON.** (FR-S3, NFR-6)
6. **Assign seats:** a checkbox matrix maps each human seat → roles → assets, and marks each role
   **bus / payload / both**. (FR-W2, OR-1/2)
7. **Start** → wall clock begins at the chosen multiplier. (FR-W3, OR-4)

### 13.2 White Cell — run the exercise
- Watch the **god-view**: ground truth, both cells' belief, SOH of all assets, the timeline,
  and a live event log. (FR-W6)
- **Manage the hot seat:** announce who's up; the active operator blanks the screen; White Cell
  confirms the next role; keyboard passes; new operator un-blanks into their role view. (OR-3)
- **Control time:** raise/lower the multiplier to skip dead time between passes; **pause** for a
  timeout or teaching point; **rewind** to re-run a decision. (FR-W3, OR-4)
- **Inject** scripted or manual events; **re-tune** live parameters (e.g., raise Red EW intensity
  or change a safe-mode dial). (FR-W4/W7)
- Adjudicate manually (v1 has no auto-scoring); narrate consequences.

### 13.3 Blue/Red — bus operator
1. Sit, un-blank into the assigned **bus** role; see only assigned assets. (OR-1)
2. Read the **fleet SOH rollup** (red/yellow/green); drill into a satellite → subsystem →
   parameter. Note the **telemetry timestamp** — is this fresh (in contact) or stale? (FR-B1/B3)
3. See **"next contact in 00:06:12 via STATION-A"**; open the **pass-timeline ribbon**. (FR-P1)
4. **Plan a pass:** queue bus commands (e.g., desaturate wheels, manage battery before eclipse,
   slew to attitude) into the next uplink window; the queue shows scheduled times; edit/cancel
   freely until uplink. (FR-P1/P3)
5. If a satellite has entered **safe mode**: confirm at next contact via the stored-telemetry
   dump, **diagnose**, and queue the multi-step **recovery procedure**; watch for **re-safe** if
   a root cause persists. (FR-B5, §12 of safe-mode doc)
6. Hand off (blank screen) when White Cell calls the next role. (OR-3)

### 13.4 Blue/Red — payload operator (per type)
- **SATCOM:** monitor transponder power/temperature and **interference level**; if a carrier
  degrades (a jam, experienced as interference — not a label), re-plan frequency/beam or shift
  customers. (FR-B4, taxonomy)
- **ISR:** build a **collection schedule** against target passes; watch **storage fill** and the
  **downlink backlog**; queue downlinks at ground/relay passes; read **image-quality** (a dazzle
  or weather shows as degraded product). (FR-B4) — exercises the collect-vs-downlink split.
- **SIGINT/SDA:** **task sensors** (search/track/characterize) within geometry and **single-task
  contention**; watch custody/uncertainty change on report; cue radar→optical. (FR-P2)
- **Space-control:** select target (needs a **weapons-quality track**), effect level on the five
  D's, and timing inside an engagement/proximity window; read **uncertain effect assessment**.
  (FR-E6/E7)

### 13.5 Red — a representative offensive sequence (Vignette 1)
1. Red EW Op pre-plans a **downlink jam** active over the landing area for the landing window.
2. Red Orbital Op tasks SDA to **maintain custody** of the Blue ISR sats (know when they image).
3. Red (cyber) attempts a **safe-mode inducement** on one Blue ISR sat (susceptibility per dial);
   if it succeeds, that sat's payload drops — Red has bought time without debris. (FR-B5)
4. Red weighs whether to escalate to kinetic (default **off**); doing so would spawn debris and a
   political-consequence inject. (FR-E6)

---

## 14. Key state machines

Explicit states the engine implements; the UI reflects them. (Detailed fields in
`04-data-model.md`.)

### 14.1 PlannedActivity (command or collection)
```
DRAFT ─▶ PLANNED ─▶ ACTIVE ─▶ EXECUTED            (commands)
                          └─▶ REPORTED            (collection)
   any ─▶ CANCELLED (operator)     ACTIVE ─▶ FAILED{reason}
```
Transitions gated by re-validation at execute time (ownership/window/resources/ROE/track). (FR-P4)

### 14.2 Bus mode / safe mode
```
NOMINAL ─(fault|power|attitude|thermal|cyber|ew|bus_stress, susceptibility check)─▶ SAFE_MODE
SAFE_MODE: payload OFF; bus autonomy points to sun, awaits ground
SAFE_MODE ─(recovery chain across passes; per-step success)─▶ NOMINAL
SAFE_MODE ─(root cause persists)─▶ SAFE_MODE  (re-safe)
```
Defender-visible substates: `defender_confirmed`, `defender_diagnosis`. (FR-B5)

### 14.3 Custody / Track confidence
```
UNKNOWN ─(detection)─▶ TRACKED(low conf) ─(characterize)─▶ CHARACTERIZED
TRACKED ─(no obs, time)─▶ confidence decays ─▶ may fall below gate ─▶ custody lost
any ─(observation window)─▶ confidence reset/raised, uncertainty shrinks
```
Weapons-quality gate = `confidence ≥ threshold AND characterized`. (FR-E7)

### 14.4 Exercise session
```
SETUP ─▶ ASSIGNED(roles) ─▶ RUNNING ⇄ PAUSED ─▶ ENDED(log written)
RUNNING ─(rewind)─▶ replays to earlier sim_time, continues  (deterministic)
```
(FR-W3, FR-L2)

---
