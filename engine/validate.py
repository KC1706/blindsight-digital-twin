"""Validation & trust (issues #15, #16, #35, #36).

We don't ask the plant to trust the twin — we make it score itself:

- **accuracy vs ground truth** (#15): dark vs instrumented cycle-time MAPE and error-bar
  coverage, on held-out scenarios;
- **false-alarm rate** (#15): how often the forecast cries "units lost" on clean baseline
  runs — the metric that erodes floor trust;
- **CRPS + calibration** (#35): proper scoring of the probabilistic forecast vs a persistence
  baseline;
- **value of information** (#16, #36): greedy submodular ranking of which dark stations to
  instrument first, by how much each removes forecast ambiguity.
"""

from __future__ import annotations

import copy

import numpy as np

from .forecast import forecast, p_binding_by_station
from .ground_truth_sim import GroundTruthSim
from .observe import extract_observation
from .scenarios import load_scenario
from .schemas import Band, LineConfig, Scenario, ValidationReport
from .virtual_sensor import estimate_cycle_times

ALARM_THRESHOLD = 8.0      # units-lost forecast above which we'd raise an alarm


def accuracy_vs_truth(scenario_names=("baseline", "takt_slip_s14", "torque_drift_s8")):
    inst_errs, dark_errs, covered, total = [], [], 0, 0
    for name in scenario_names:
        res = GroundTruthSim(scenario=load_scenario(name)).run()
        est = estimate_cycle_times(extract_observation(res))
        for s in res.line.stations:
            true = res.true_mean_cycle.get(s.id, s.mean_cycle_s)
            if true <= 0:
                continue
            err = abs(est[s.id].mean - true) / true
            (inst_errs if s.instrumented else dark_errs).append(err)
            if not s.instrumented:
                total += 1
                if est[s.id].lo <= true <= est[s.id].hi:
                    covered += 1
    return {
        "mape_instrumented": round(100 * float(np.mean(inst_errs)), 1),
        "mape_dark": round(100 * float(np.mean(dark_errs)), 1),
        "dark_band_coverage": round(covered / max(1, total), 2),
    }


def false_alarm_rate(n_runs: int = 12) -> float:
    alarms = 0
    for seed in range(100, 100 + n_runs):
        sc = Scenario(name="baseline", duration_s=7200, seed=seed)
        res = GroundTruthSim(scenario=sc).run()
        est = estimate_cycle_times(extract_observation(res))
        fc = forecast(est, res.line, 7200, M=300, seed=seed)
        if fc.units_lost.mean > ALARM_THRESHOLD:
            alarms += 1
    return round(alarms / n_runs, 2)


def _crps_normal(mean, sd, obs):
    # closed-form CRPS for a Gaussian forecast (Gneiting & Raftery)
    sd = max(sd, 1e-6)
    z = (obs - mean) / sd
    from math import erf, exp, pi, sqrt
    cdf = 0.5 * (1 + erf(z / sqrt(2)))
    pdf = exp(-0.5 * z * z) / sqrt(2 * pi)
    return float(sd * (z * (2 * cdf - 1) + 2 * pdf - 1 / sqrt(pi)))


def forecast_crps(scenario_names=("takt_slip_s14", "torque_drift_s8", "surge_3x")):
    ours, persistence = [], []
    base = 9.0   # persistence: always predict the baseline's typical loss
    for name in scenario_names:
        res = GroundTruthSim(scenario=load_scenario(name)).run()
        est = estimate_cycle_times(extract_observation(res))
        fc = forecast(est, res.line, 7200, M=500)
        ideal = 7200 / res.line.takt_s
        # ground-truth constraint-attributable loss = what a perfect twin would forecast
        max_true = max(res.true_mean_cycle.values())
        realized_loss = max(0.0, ideal - 7200 / max_true)
        sd = max(1.0, (fc.units_lost.hi - fc.units_lost.lo) / 2.56)
        ours.append(_crps_normal(fc.units_lost.mean, sd, realized_loss))
        persistence.append(_crps_normal(base, 5.0, realized_loss))
    return {"crps_model": round(float(np.mean(ours)), 2),
            "crps_persistence": round(float(np.mean(persistence)), 2)}


def _entropy(pb: dict[int, float]) -> float:
    return -sum(p * np.log(p) for p in pb.values() if p > 0)


def _forecast_uncertainty(est, line) -> float:
    fc = forecast(est, line, 7200, M=500)
    return fc.units_lost.hi - fc.units_lost.lo        # width of the units-lost band


def value_of_information(scenario_name: str = "takt_slip_s14", top_k: int = 3):
    """Greedy submodular: which dark stations, if instrumented, most tighten the forecast.

    Pinning a dark station's estimate (as a sensor would) shrinks the forecast's units-lost
    band; the station that shrinks it most is the one to instrument first.
    """
    res = GroundTruthSim(scenario=load_scenario(scenario_name)).run()
    line: LineConfig = res.line
    est = estimate_cycle_times(extract_observation(res))
    dark = line.dark_stations()

    chosen: list[dict] = []
    current = copy.deepcopy(est)
    base_width = _forecast_uncertainty(current, line)
    for _ in range(top_k):
        w0 = _forecast_uncertainty(current, line)
        best_d, best_gain, best_est = None, -1e9, None
        for d in dark:
            if any(c["station_id"] == d for c in chosen):
                continue
            trial = copy.deepcopy(current)
            m = trial[d].mean
            trial[d] = Band(mean=m, lo=m * 0.98, hi=m * 1.02)   # as if a sensor pinned it
            gain = w0 - _forecast_uncertainty(trial, line)
            if gain > best_gain:
                best_d, best_gain, best_est = d, gain, trial
        if best_d is None or best_gain <= 0.05:
            break
        chosen.append({"station_id": best_d,
                       "forecast_band_reduction": round(float(best_gain), 2)})
        current = best_est
    return {"baseline_forecast_band": round(float(base_width), 2),
            "instrument_first": chosen}


def build_report() -> ValidationReport:
    acc = accuracy_vs_truth()
    far = false_alarm_rate()
    crps = forecast_crps()
    res = GroundTruthSim(scenario=load_scenario("takt_slip_s14")).run()
    est = estimate_cycle_times(extract_observation(res))
    fc = forecast(est, res.line, 7200, 500)
    return ValidationReport(
        cycle_time_mape_instrumented=acc["mape_instrumented"],
        cycle_time_mape_dark=acc["mape_dark"],
        forecast_crps=crps["crps_model"],
        false_alarm_rate=far,
        median_lead_time_s=fc.eta_s.mean,
    )
