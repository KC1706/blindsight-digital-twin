"""Forecast tests (M3)."""

from engine.forecast import forecast, p_binding_by_station
from engine.ground_truth_sim import GroundTruthSim
from engine.observe import extract_observation
from engine.scenarios import load_scenario
from engine.virtual_sensor import estimate_cycle_times


def _est(name):
    res = GroundTruthSim(scenario=load_scenario(name)).run()
    return estimate_cycle_times(extract_observation(res)), res.line


def test_forecast_identifies_s14_constraint():
    est, line = _est("takt_slip_s14")
    fc = forecast(est, line, horizon_s=7200, M=500)
    assert fc.constraint_station_id == 14
    assert fc.p_binding > 0.4
    # bands are ordered and non-negative
    assert fc.units_lost.lo <= fc.units_lost.mean <= fc.units_lost.hi
    assert fc.eta_s.lo <= fc.eta_s.hi


def test_p_binding_sums_to_one():
    est, line = _est("baseline")
    pb = p_binding_by_station(est, line, M=500)
    assert abs(sum(pb.values()) - 1.0) < 1e-6


def test_slip_loses_more_than_baseline():
    base, line = _est("baseline")
    slip, _ = _est("takt_slip_s14")
    lost_base = forecast(base, line, 7200, 500).units_lost.mean
    lost_slip = forecast(slip, line, 7200, 500).units_lost.mean
    assert lost_slip > lost_base
