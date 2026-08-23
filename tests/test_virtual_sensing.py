"""Virtual sensing accuracy tests (M2) — the twin scoring itself vs ground truth."""

import numpy as np

from engine.ground_truth_sim import GroundTruthSim
from engine.observe import extract_observation
from engine.scenarios import load_scenario
from engine.virtual_sensor import blocked_starved_bottleneck, estimate_cycle_times


def _run(name):
    res = GroundTruthSim(scenario=load_scenario(name)).run()
    return res, extract_observation(res)


def test_bottleneck_localized_to_dark_s14():
    for name in ("baseline", "takt_slip_s14"):
        res, obs = _run(name)
        bn, conf = blocked_starved_bottleneck(obs)
        assert bn == 14, f"{name}: expected S14, got S{bn}"
        assert conf > 0.3


def test_dark_station_estimates_track_truth():
    res, obs = _run("baseline")
    est = estimate_cycle_times(obs)
    dark = res.line.dark_stations()
    mape = np.mean([abs(est[j].mean - res.true_mean_cycle[j]) / res.true_mean_cycle[j]
                    for j in dark]) * 100
    assert mape < 25, f"dark-station MAPE too high: {mape:.0f}%"
    # the bottleneck estimate must bracket the truth within its error bars
    b = est[14]
    assert b.lo <= res.true_mean_cycle[14] <= b.hi


def test_error_bars_present_everywhere():
    res, obs = _run("takt_slip_s14")
    est = estimate_cycle_times(obs)
    assert set(est) == {s.id for s in res.line.stations}
    for b in est.values():
        assert b.lo <= b.mean <= b.hi        # never a bare number
