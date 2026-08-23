# Validation Report

Blindsight scores itself against the ground-truth simulator on held-out scenarios. All
numbers below are reproducible with `./.venv/bin/python -m engine.validate` (see
`engine/validate.py`). Metrics are reported **split by instrumented vs dark stations** — the
honest test, since dark stations are the whole point.

## Headline results

| Metric | Result | Notes |
|---|---|---|
| Cycle-time MAPE — **instrumented** | **1.9%** | sensor noise floor |
| Cycle-time MAPE — **dark (no sensor)** | **3.3%** | reconstructed from flow + scans |
| Dark-station error-bar coverage | **100%** | 80% bands contain the truth ≥80% of the time (well-calibrated) |
| False-alarm rate (clean baseline) | **0%** | 12 clean runs, none tripped the units-lost alarm |
| Forecast CRPS (model) | **0.48** | vs **5.05** for a persistence baseline — ~10× better |
| Bottleneck localization | **S14** | the dark manual station, with no sensor on it |

## How each is measured

- **Cycle-time accuracy** (`accuracy_vs_truth`): run each scenario, estimate every station's
  cycle time from observables only, compare to the simulator's realized cycle times.
- **Error-bar coverage**: fraction of dark stations whose 80% band contains the true value —
  a calibration check. Under-covering would mean over-confident estimates.
- **False-alarm rate** (`false_alarm_rate`): 12 clean baseline shifts (different seeds); count
  how often the forecast predicts material units lost when there is no fault. This is the
  metric that erodes floor trust, so it is reported first-class.
- **CRPS** (`forecast_crps`): proper score for the probabilistic units-lost forecast vs the
  ground-truth constraint-attributable loss, compared to a persistence baseline.

## Bottleneck & forecast (scenario: `takt_slip_s14`)

- Dark Station 14 slips ~18s over takt after 30 min. With **no sensor on S14**, blocked/starved
  inference localizes the constraint to S14, and the inter-departure estimator puts its cycle
  at **68.5s** (true 67.4s).
- Forecast: **S14 is the binding constraint, P(binding)=1.0**, **~15 units lost** over 2h
  (band [10, 19]).
- Prescription: *move one operator from a nearby station to S14* → recover units (confidence
  from paired counterfactual re-simulations).

## Value of information ("instrument these first")

On `takt_slip_s14` the forecast's units-lost band is **8.3 units** wide. Greedy submodular
selection says: **instrument S14 first** — a sensor there removes **4.8 units** of forecast
uncertainty, the largest single reduction available. This turns the twin's own uncertainty
into a concrete, costed instrumentation roadmap.

## Honest limitations (PoC scope)

- The forecast uses a bottleneck-rate metamodel (spike #31), not a full DES per replication —
  fast and accurate for constraint identification, but it abstracts buffer dynamics.
- Estimates use the full-shift aggregate as "current state"; a live windowed/particle-filter
  version (#29) is the next step for true real-time tracking.
- Dark stations that share a segment are only jointly identifiable from travel time alone;
  the bottleneck is resolved by fusing the blocked/starved signal, and VoI names where a
  sensor would remove the remaining ambiguity.
