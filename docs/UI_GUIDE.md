# Dashboard UI Guide

Open the dashboard (`make serve` → http://127.0.0.1:8000). A **guided tour starts
automatically the first time**; click **❓ Guide** (top-right) to replay it anytime. This
document is the written companion to that live tour.

## Global controls (top bar)

| Component | What it is | How it works |
|---|---|---|
| **Scenario dropdown** | The situation being analysed | Switches between `baseline` (normal), `takt_slip_s14` (a manual station slips over takt), `torque_drift_s8` (a tool drifts, making defects), `surge_3x` (3× arrivals). Everything recomputes. |
| **❓ Guide** | Replays the interactive tour | Spotlights each component with a plain-English explanation. |
| **Tabs** | The three stakeholder views | Same model, three audiences: Floor / Plant / Leadership. |

## 🏭 Floor supervisor — "what's happening right now"

| Component | What it tells you | How it works under the hood |
|---|---|---|
| **Headline banner** | The one thing to know: which station is the constraint, whether it has a sensor, cars at risk | Fuses the bottleneck localizer + forecast into one sentence. |
| **Live line map (SVG)** | All 40 stations; colour = state; white ring = dark (no sensor); ▼ = bottleneck; purple dots = cars | Green working / amber blocked (piling up) / red starved (running dry). Dots animate over a websocket replaying real vehicle positions. |
| **Legend + clock** | Colour key + live shift time, cars built, cars on line | Streamed live from the server. |
| **Live constraint (recursive filter)** | The current constraint segment — named down to the dark station — plus a per-segment live-load strip, updating as the shift plays | A Rao-Blackwellized particle filter fuses scans into a live per-segment posterior **every tick** and snaps to a regime change (operator swap, tool drift) within minutes. Constraint found via the blocked→starved boundary, so it isn't fooled by blocking propagating upstream. Precomputed & cached (`/api/live_state`), so no stateful filter runs inside the socket loop. |
| **Recommended action** | The suggested fix, cars recovered, confidence, Accept/Override | Found by re-simulating "what-if" operator moves; every click is written to the audit log. |
| **Defect containment** | Cars affected by a drift and how many are still catchable | Uses scan timestamps to list the exact VINs processed during the drift window. |

## 📈 Plant manager — "what happens over the next 2 hours"

| Component | What it tells you | How it works |
|---|---|---|
| **Binding constraint** | Which station will choke the line + P(binding) | Share of 500 Monte-Carlo simulations where this station is the bottleneck. |
| **Units lost** | Cars lost over 2h, as a range | 80% band from the simulations — never a fake-exact number. |
| **ETA** | Time until losses begin | From the rate mismatch between the constraint and takt. |
| **Per-station cycle-time table** | Every station's estimated speed with error bars; dark rows highlighted; P(constraint) per station | Bar = estimate, shaded band = uncertainty. Dark stations are reconstructed from flow + scans with no sensor. |
| **Mixed-model work content (per-variant)** | Per-variant service time at each station, and where a variant adds extra work (e.g. a sunroof on one trim) — validated vs ground truth | Variant-aware travel-time tomography recovers per-variant cycle times and localizes a variant-specific operation to the exact dark station, no sensor needed (`/api/variants`). |

## 💼 Leadership — "is it worth it, and what do we buy"

| Component | What it tells you | How it works |
|---|---|---|
| **Throughput** | Cars built this shift | From the simulation. |
| **Recoverable units** | Cars the recommended action saves | From the prescription step. |
| **Margin recovered / yr** | Dollar impact | Recoverable units × margin/unit × shifts × days (assumptions shown). |
| **Instrument first (VoI)** | Which dark station to add a sensor to first | Greedy ranking by how much a sensor there shrinks forecast uncertainty. |
| **Trust panel** | The twin scoring itself: dark-station accuracy, false-alarm rate, forecast CRPS | Measured on held-out scenarios vs the ground-truth simulator. |

## Suggested first run

1. Select **`takt_slip_s14`** → watch the map: Station 14 (white ring = dark) turns into the ▼ bottleneck with **no sensor on it**.
2. Watch the **Live constraint** panel: as the shift plays, the recursive filter shifts the constraint onto S14's segment within minutes of the slip — reacting live, not in hindsight.
3. Read the **recommendation**, click **Accept**, see the audit log.
4. Switch to **`torque_drift_s8`** → open **Defect containment** to see the exact affected cars.
5. Open **Plant manager** → see S14's estimate sit above its neighbours, with error bars.
6. Open **Leadership** → the ROI and the "instrument S14 first" line.
