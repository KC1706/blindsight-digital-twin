# Blindsight — a digital twin that sees the stations it can't measure

**Team DarkShield · Accenture Innovation Challenge 2026 · Round 2 · Track 4 (DigitalTwin.ai)**

> The stations that most need watching are the ones nothing can see.
> Blindsight reads the sensors already on the line — differently — to estimate the dark
> stations, forecast the line two hours ahead, and tell the plant what to do next.

---

## The problem (Round 2, Track 4)

Real assembly lines are a patchwork of legacy and modern equipment. Sensor coverage is
**uneven** — robot cells are richly instrumented, manual stations often have nothing but a
checklist. And manual stations, where humans vary, are usually *where the bottleneck is*.
Existing MES/PLC dashboards are rear-view mirrors: they tell you the line stopped **after** it
stopped. Retrofitting sensors means scarce maintenance windows and capex.

## The idea: "the line is the sensor"

Blindsight never assumes it can see every station. It infers the invisible ones from the
physics of flow, then closes the loop:

1. **Virtual sensing** — blocked/starved propagation localizes a dark bottleneck from its
   instrumented neighbours; travel-time tomography over existing scan checkpoints estimates
   every station's cycle time, dark or not — each with an error bar.
2. **Probabilistic forecast** — a 2-hour Monte-Carlo forward run gives P(binding constraint),
   ETA, and expected units lost, with percentile bands.
3. **Prescriptive action** — counterfactual re-simulation ranks levers (move an operator,
   rebalance a buffer) by expected units recovered.
4. **Defect trace** — an SPC signal + scan timestamps names the exact VINs in a drift window
   and where each one is right now — before end-of-line audit.
5. **Trust & value-of-information** — every estimate is backtested; the twin ranks which dark
   stations to instrument first.

**Retrofit-free and read-only** — no PLC writes, no new hardware to prove the mechanism.

## What's in this prototype

A working proof-of-concept on a simulated mixed-model line (**40 stations**, Body → Paint →
General Assembly, **10 dark/manual stations with no sensor = 25%**, scan checkpoints at zone
boundaries). The digital twin consumes **only the observable subset** (instrumented states +
scan timestamps) via an enforced boundary — it never reads ground truth.

Two additional core-mechanism capabilities shipped this round:

- **Variant-aware design matrix** — recovers per-variant work content on a mixed-model line
  (a sunroof fitted on one trim) and localizes it to the exact dark station, no sensor needed.
- **Online particle filter** — a live, recursive posterior over line state that tracks a
  regime change (operator swap, tool drift) within minutes, not after the shift.

## Validation — the twin scoring itself (`docs/VALIDATION.md`)

| Metric | Result |
|---|---|
| Cycle-time MAPE — dark stations (no sensor) | **3.3%** (instrumented: 1.9%) |
| Error-bar coverage (80% band) | **100%** |
| False-alarm rate (12 clean shifts) | **0%** |
| Forecast CRPS vs persistence baseline | **0.48 vs 5.05 (~10× better)** |
| Bottleneck localization (`takt_slip_s14`) | dark **S14**, with no sensor on it |

All reproducible: `./.venv/bin/python -m engine.validate`.

## Three views, one model

| Stakeholder | View | Needs |
|---|---|---|
| Floor supervisor | Real-time line map | live blocked/starved state, live constraint, the next action |
| Plant manager | 2-hour forecast | constraint timeline, per-station bands, per-variant work content |
| Leadership | ROI / business case | units & $ saved, "instrument these 3 first" |

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# tests (the twin scoring itself)
pytest -q                      # 31 tests

# the dashboard + API (then open http://127.0.0.1:8000/)
./.venv/bin/uvicorn api.main:app --port 8000
```

Demo scenarios (dropdown in the dashboard): `baseline`, `takt_slip_s14` (dark bottleneck),
`torque_drift_s8` (defect trace), `surge_3x` (volume surge). Demo runsheet:
`docs/DEMO_SCRIPT.md`. Pitch deck: `deck/index.html` (offline).

## Repository layout

```
engine/      # the core mechanism (pure Python, tested)
  virtual_sensor.py   line.py   ground_truth_sim.py   observe.py
  forecast.py   prescribe.py   defect_trace.py   root_cause.py
  online_filter.py    validate.py   pipeline.py   schemas.py
api/         # FastAPI service (REST + websocket live stream)
web/         # browser dashboard — the 3 stakeholder views
deck/        # pitch presentation (offline reveal.js) + speaker notes + Q&A
scenarios/   # named demo scenarios (JSON)
tests/       # engine unit + validation tests
docs/        # business proposal, methods, validation, ROI, roadmap, risks
PLAN.md      # technical plan & build phases
```

## Round 2 deliverables

- **Detailed Business Proposal** → `docs/BUSINESS_PROPOSAL.md`
- **Working Prototype** → `engine/` + `api/` + `web/`
- **Pitch Presentation** → `deck/`

## Status

🟢 **Working prototype — mechanism proven end-to-end, validated, CI green.**
