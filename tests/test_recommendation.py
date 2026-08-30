"""Recommendation coverage (pipeline) — every fault scenario yields a usable action.

Regression for "the recommendation only fired on takt_slip": each injected fault must now
produce a driver-appropriate recommendation, and a clean shift must stay silent.
"""

from engine.pipeline import analyze


def test_takt_slip_recommends_labor_move():
    r = analyze("takt_slip_s14")["recommendation"]
    assert r is not None
    assert "operator" in r["action"].lower()
    assert r["metric"] == "units recovered"
    assert r["recovered"]["mean"] > 0


def test_defect_scenario_recommends_containment():
    r = analyze("torque_drift_s8")["recommendation"]
    assert r is not None
    assert any(w in r["action"].lower() for w in ("quarantine", "recalibrate", "contain"))
    assert r["recovered"] is not None            # vehicles still containable


def test_surge_recommends_pacing_not_labor():
    r = analyze("surge_3x")["recommendation"]
    assert r is not None
    assert "surge" in r["driver"].lower()
    assert "labor" not in r["action"].lower() or "can't" in r["action"].lower()


def test_baseline_is_balanced():
    assert analyze("baseline")["recommendation"] is None
