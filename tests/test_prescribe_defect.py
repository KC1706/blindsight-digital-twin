"""M4 tests: prescription, SPC change-point, defect trace."""

import numpy as np

from engine.defect_trace import trace_defects
from engine.ground_truth_sim import GroundTruthSim
from engine.observe import extract_observation
from engine.prescribe import recommend
from engine.root_cause import cusum_change_point
from engine.scenarios import load_scenario
from engine.virtual_sensor import estimate_cycle_times


def test_recommendation_recovers_units_for_slip():
    res = GroundTruthSim(scenario=load_scenario("takt_slip_s14")).run()
    est = estimate_cycle_times(extract_observation(res))
    rec = recommend(est, res.line, 7200)
    assert rec is not None
    assert "Station 14" in rec.action
    assert rec.expected_units_recovered.mean > 0
    assert 0 <= rec.confidence <= 1


def test_cusum_detects_step():
    signal = [50] * 20 + [66] * 20        # clean step
    onset, _ = cusum_change_point(signal)
    assert onset is not None and 15 <= onset <= 25


def test_defect_trace_high_recall():
    res = GroundTruthSim(scenario=load_scenario("torque_drift_s8")).run()
    obs = extract_observation(res)
    tr = trace_defects(obs, station_id=8, onset_s=2400, end_s=res.duration_s)
    true_def = {v.vin for v in res.vehicles if 8 in v.defects}
    found = set(tr.affected_vins)
    recall = len(found & true_def) / max(1, len(true_def))
    assert recall > 0.9, f"defect-trace recall too low: {recall:.2f}"
    # every flagged VIN has an estimated current position
    assert all(v in tr.current_positions for v in tr.affected_vins)
