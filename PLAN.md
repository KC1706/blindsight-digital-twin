# Blindsight — Technical Plan

**Track 4 · DigitalTwin.ai · Round 2 · Team DarkShield**

This document is the engineering plan for the working prototype. It is the source the
GitHub Milestones/Issues taskboard is derived from. Scope for Round 2 is a **proof-of-concept
on simulated data** that makes the core predictive mechanism visible and runnable.

---

## 1. Design goals

1. **Demonstrate the core mechanism, not photoreal geometry.** We model how *work flows*,
   not 3D CAD. The detail follows the decision.
2. **Honest observability split.** A ground-truth simulator produces "reality"; the twin only
   ever consumes the *observable* subset (instrumented stations + scan timestamps). The gap
   between them is the whole point — and lets us score our own accuracy.
3. **Every number has error bars.** No estimate or forecast is shown without a confidence band.
4. **Validated before trusted.** Predictions are backtested against replayed outcomes so we can
   report false-alarm rate, lead time, and calibration — the thing that erodes floor trust.

## 2. Core mechanism (what the prototype must show)

### 2.1 Ground truth vs. observation
- A discrete-event simulator (SimPy or a compact custom DES) runs a mixed-model line and emits
  a full event log. This is "reality" — the prototype must *not* read it directly.
- An observability mask keeps only: (a) state transitions at **instrumented** stations
  (working / blocked / starved / idle), and (b) **scan-checkpoint timestamps** per vehicle
  (VIN). Manual ("dark") stations emit nothing.

### 2.2 Virtual sensing — blocked/starved inference
- For a dark station between two instrumented neighbours, rising **blocking** upstream +
  rising **starvation** downstream localizes it as the constraint. Produces a real-time
  "who is the bottleneck right now" signal without a sensor on the station.

### 2.3 Virtual sensing — travel-time tomography
- Vehicle *i* travels segment between checkpoints `c_k → c_{k+1}`; its measured travel time
  `T_i ≈ Σ_j A_ij · x_j + wait`, where `x_j` is the effective cycle time of station `j` and
  `A` is the station-in-segment incidence matrix.
- Accumulate many vehicles → over-determined linear system. Solve by **regularized least
  squares** (ridge / non-negativity), separating cycle time from queue wait using flow state.
- Residual variance per station → **confidence / error bars**. Sensor-poor segments get wider
  bands — surfaced honestly.

### 2.4 Forecast — Monte Carlo forward simulation
- Seed a fast forward-sim with current WIP positions + per-station cycle-time *distributions*
  (from 2.3). Run **N≈500** replications for a **2-hour** horizon.
- Aggregate: P(station is the binding constraint), expected units lost, ETA-to-constraint,
  with percentile bands.

### 2.5 Prescription — counterfactual action ranking
- Candidate levers: move an operator Sᵢ→Sⱼ, add/rebalance buffer, adjust takt.
- Re-simulate each counterfactual → rank by **expected units recovered** net of cost.
- Output as `driver → controllable lever → action → expected impact → confidence`.

### 2.6 Defect propagation trace
- On an SPC signal at a station (e.g. torque drift beyond control limits), use scan timestamps
  to enumerate the **exact VINs** processed inside the drift window and their current positions
  → a containment list before the fault reaches end-of-line audit.

### 2.7 Trust — validation & value of information
- **Backtest harness**: replay historical windows, compare forecasts to realized outcomes.
  Metrics: Brier score / calibration curve, lead time, false-alarm rate, units-saved capture.
- **Value of information**: rank dark stations by expected reduction in forecast error if
  instrumented → "instrument these 3 first."

## 3. Simulated data

- **Line**: ~40 stations across Body → Paint → General Assembly, mixed-model, with buffers
  between zones. Each station has a *true* cycle-time distribution, a station type
  (robot/manual), and a sensor-coverage flag (~60–70% instrumented, rest dark).
- **Scenarios** (in `scenarios/`):
  - `torque_drift_s8` — a tool drifts 4% out of spec at Station 8 (defect-trace demo).
  - `takt_slip_s14` — Station 14 runs ~9s over takt (bottleneck forecast + operator move).
  - `surge_3x` — 3× normal arrival volume (behaviour under surge).
  - `baseline` — nominal shift for calibration.

## 4. Architecture

```
engine/
  line.py             # topology, station config, buffers, scenario loader
  ground_truth_sim.py # DES → "reality" + full event log
  observe.py          # apply sensor-coverage mask → observable stream only
  virtual_sensor.py   # blocked/starved inference + tomography solver (+error bars)
  forecast.py         # Monte Carlo forward simulation
  prescribe.py        # counterfactual lever search + ranking
  defect_trace.py     # VIN containment from scan timestamps
  validate.py         # backtest metrics + value-of-information ranking
api/
  main.py             # FastAPI: REST snapshots + websocket live stream
  schemas.py          # pydantic models
web/
  index.html app.js styles.css   # 3 stakeholder views wired to the API
```

**Tech**: Python 3.14, numpy, (SimPy optional), FastAPI + uvicorn, pydantic; vanilla-JS
dashboard (no build step) with an SVG/canvas line map.

## 5. Build phases → taskboard milestones

| Milestone | Goal | Key output |
|---|---|---|
| **M0 Foundations** | repo, plan, deps, line config schema | this repo, `requirements.txt`, `line.py` |
| **M1 Ground truth + observability** | DES reality + scan log; sensor mask; scenarios | `ground_truth_sim.py`, `observe.py`, `scenarios/` |
| **M2 Virtual sensing** | blocked/starved + tomography with error bars | `virtual_sensor.py` + accuracy-vs-truth test |
| **M3 Forecast** | Monte Carlo 500×/2h; constraint prob + units lost | `forecast.py` |
| **M4 Prescription + defect trace** | counterfactual ranking; VIN containment | `prescribe.py`, `defect_trace.py` |
| **M5 Validation & trust** | backtest metrics; instrument-3-first | `validate.py`, `docs/VALIDATION.md` |
| **M6 API** | REST + websocket live stream | `api/main.py` |
| **M7 Dashboard** | floor / plant-manager / leadership views | `web/` |
| **M8 Demo & proposal** | scripted scenarios, business case, pitch align | `docs/BUSINESS_PROPOSAL.md`, demo script |

Each milestone is tracked as a GitHub Milestone; individual tasks are Issues linked to it.

## 6. How the prototype maps to the Round 2 rubric

| Round 2 solutioning area | Where addressed |
|---|---|
| Modelling: what to represent vs infer | §2.1–2.3 — cycle time / flow modelled; dark stations inferred |
| Predictive: anomaly / SPC / ML, and validation | §2.2, §2.6, §2.7 |
| Handling data gaps (partial/no instrumentation) | §2.2–2.3 virtual sensing + error bars |
| UX: 3 distinct stakeholder views from one model | §4 `web/`, M7 |
| Integration around legacy PLCs / OT constraints | consumes existing scan + state feeds only; no line changes |
| Scalability & ROI | §2.7 VoI, M8 business case |
| Predictive claims validated / false alarms erode trust | §2.7 backtest, calibration, false-alarm rate |

## 7. Success metrics / acceptance criteria

The prototype must hit measurable bars (reported in `docs/VALIDATION.md`), not just "it runs":

| Capability | Target (illustrative, PoC) |
|---|---|
| Dark-station cycle-time estimate | MAPE ≤ ~15% vs ground truth; error-bar coverage ≈ nominal (80% band contains truth ~80%) |
| Bottleneck call | precision/recall ≥ ~0.8 on injected events; median lead time ≥ ~60 min |
| False-alarm rate | reported and tuned below a stated threshold (the trust metric) |
| Forecast calibration | reliability diagram near-diagonal; CRPS beats a persistence baseline |
| Recommendation | expected units-recovered with a confidence it beats "do nothing" |
| Runtime | 500-replication / 2-h forecast in a few seconds on a laptop |

Every headline number is reported **split by instrumented vs dark stations** — the honest test.

## 8. Deep-tech methods

The differentiating techniques are specified in [`docs/METHODS.md`](docs/METHODS.md):
active-period bottleneck detection, a **Bayesian hierarchical tomographic inverse problem** for
dark-station service times, an **online particle/Kalman filter** for live state, SPC + causal
attribution for multi-causal root cause, **uncertainty-propagating Monte-Carlo forecasting**,
**simulation-optimization (OCBA/KN)** for prescription, distributional backtesting (CRPS,
calibration), and **submodular value-of-information** sensor placement.

## 9. Two-person work split (parallel tracks)

Plenty of runway → build for depth, run two tracks in parallel with a thin API contract as the
seam (agree `api/schemas.py` early so both sides mock against it).

- **Track A — "Engine & Science" (Dev 1):** M1 ground-truth sim + observability, M2 virtual
  sensing (tomography + filter), M3 forecast, M4 prescription + defect trace, M5 validation.
  Owns `engine/`, `docs/METHODS.md`, `docs/VALIDATION.md`.
- **Track B — "Product & Story" (Dev 2):** M0 scaffolding, M6 API, M7 dashboard (3 views),
  M8 demo + business proposal. Owns `api/`, `web/`, `docs/BUSINESS_PROPOSAL.md`,
  `docs/DEMO_SCRIPT.md`.
- **Shared seam:** `api/schemas.py` (data contract) agreed in M0 so Track B builds the UI
  against fixtures while Track A implements the real engine behind the same shapes.

## 10. Dependencies & critical path

```
M0 ─► M1 ─► M2 ─► M3 ─► M4 ─┐
                 └► M5 ◄─────┤   (M5 validates M2/M3/M4)
M0 ─► (schemas) ─► M6 ─► M7  │
                            └► M8 (needs a runnable M3+M7)
```

Critical path to a demo: **M0 → M1 → M2 → M3 → M6 → M7 → M8**. M4/M5 deepen the story and are
p1 (not p0) — they make the pitch *win*, not merely *run*. Track B's M6/M7 proceed against
fixtures as soon as schemas exist, so the UI is never blocked on the science.

## 11. Out of scope for the PoC

Real PLC/OT integration, real plant data, production hardening, auth, 3D visualization.
Stated explicitly per the brief ("working proof-of-concept on illustrative or sample data").
