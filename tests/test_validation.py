"""M5 validation tests — the trust metrics must hold."""

from engine.validate import (
    accuracy_vs_truth,
    false_alarm_rate,
    forecast_crps,
    value_of_information,
)


def test_accuracy_within_bounds():
    acc = accuracy_vs_truth()
    assert acc["mape_instrumented"] < 5
    assert acc["mape_dark"] < 12
    assert acc["dark_band_coverage"] >= 0.75      # well-calibrated bands


def test_low_false_alarm_rate():
    assert false_alarm_rate(n_runs=8) <= 0.25


def test_forecast_beats_persistence():
    c = forecast_crps()
    assert c["crps_model"] < c["crps_persistence"]


def test_voi_recommends_the_constraint_first():
    voi = value_of_information("takt_slip_s14")
    first = voi["instrument_first"]
    assert first and first[0]["station_id"] == 14
