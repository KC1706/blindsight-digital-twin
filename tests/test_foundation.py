"""Foundation sanity tests (M0)."""

from engine.ground_truth_sim import GroundTruthSim
from engine.line import build_default_line
from engine.scenarios import available, load_scenario
from engine.schemas import Scenario


def _short(name: str) -> Scenario:
    sc = load_scenario(name)
    sc.duration_s = 3000  # long enough for the 40-station line to fill and exit units
    return sc


def test_line_shape():
    line = build_default_line()
    assert len(line.stations) == 40
    assert 8 in line.dark_stations() and 14 in line.dark_stations()
    assert all(0 <= c < len(line.stations) for c in line.checkpoints())
    instrumented = sum(s.instrumented for s in line.stations)
    assert 0.5 < instrumented / len(line.stations) < 0.8  # ~65% coverage


def test_all_scenarios_load():
    names = available()
    for n in ("baseline", "takt_slip_s14", "torque_drift_s8", "surge_3x"):
        assert n in names
        assert load_scenario(n).name == n


def test_sim_runs_and_produces_observables():
    res = GroundTruthSim(scenario=_short("baseline")).run()
    assert res.throughput > 0
    assert len(res.scans) > 0
    assert len(res.vehicles) > res.throughput  # some WIP still on the line
    # every station has a state log summing to the run duration
    for log in res.state_log.values():
        assert sum(log.values()) == int(res.scenario.duration_s)


def test_drift_creates_defects_and_traceable_scans():
    res = GroundTruthSim(scenario=load_scenario("torque_drift_s8")).run()
    defective = [v for v in res.vehicles if 8 in v.defects]
    assert defective, "torque drift at S8 should damage some vehicles"
    # scans exist at checkpoint 8, enabling a later defect trace
    assert any(cp == 8 for _, cp, _ in res.scans)


def test_takt_slip_makes_s14_the_constraint():
    res = GroundTruthSim(scenario=load_scenario("takt_slip_s14")).run()
    assert res.ground_truth_bottleneck() == 14
