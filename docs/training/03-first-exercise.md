[← Training index](INDEX.md) · [↑ Docs index](../INDEX.md)

## 4. Your first exercise

We'll run **Vignette 1 — LEO ISR Denial**. Blue operates an imaging satellite and must deliver
imagery before a landing window; Red wants to deny it without escalating to a kinetic strike.

### Step 1 — Load and start
1. In the picker, choose **LEO ISR Denial**, leave **Seed = 1**, click **Load**, then **Start**.
2. Click **White** to confirm the order of battle: Blue's `ISR-EO-1` and ground stations; Red's
   surface group, a downlink jammer (`JAM-NORTH`), and an (off-by-default) interceptor.

### Step 2 — Become Blue and plan a downlink
1. Click **Blue**. The objectives read `blue.deliver_isr: pending`.
2. In the **Order panel**, set **Actor** = `ISR-EO-1`, **Action** = `downlink`,
   **Params** = `{"via": "GS-NORTH"}`, then click **Issue**.
3. The result shows the order **queued**, its **delivery path** (ground uplink), and **when** it
   will execute — you do not act instantly; the command waits for the next station pass.

![Order panel](../manual/05-order-panel.png)

### Step 3 — Advance time to the window
Click **+10m** a few times. When the clock passes the downlink window, the order executes and
`blue.deliver_isr` flips to **MET** — Blue delivered the imagery in time. **Blue wins.**

### Step 4 — Rewind and try the other branch
Because the engine is deterministic, White Cell can **rewind** and explore "what if".

1. Click **Rewind to start**. Delivery is undone; the clock is back at the start.
2. Click **Red**, then issue: **Actor** = `JAM-NORTH`, **Action** = `jam`,
   **Target** = `ISR-EO-1`, **Params** = `{"success_prob": 1.0, "outcome": "deny"}` → **Issue**.
3. Click **Blue** and issue the same downlink as before.
4. Advance time. This time the downlink is **blocked** — Red jammed it. Blue sees a *symptom* on
   `ISR-EO-1` (`deny — source unknown`) but cannot immediately attribute it. **Red wins.**

![Time travel and branching](../manual/11-time-travel-branch.png)

That contrast — same start, opposite outcomes depending on play — is the core teaching mechanic.

### Headless walkthrough (no browser)
The same exercise in Python:

```python
from spacesim.session.inprocess import InProcessSession
from spacesim.engine.orders import Order

api = InProcessSession()
sid = api.load_vignette("leo-isr-denial", seed=1)
api.start(sid)

ack = api.issue_order(sid, "blue",
        Order(cell="blue", actor="ISR-EO-1", action="downlink", params={"via": "GS-NORTH"}))
print(ack.status, ack.delivery_path, ack.earliest_window)

start = api.get_godview(sid).now
api.advance_to(sid, start + 800_000_000)          # advance ~13 min past the window
print(api.objectives(sid))                         # blue.deliver_isr -> True
```

---
